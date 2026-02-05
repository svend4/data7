"""
JWT Authentication System

Implements secure JWT-based authentication with access and refresh tokens.
Supports user registration, login, token refresh, and logout.
"""

from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from jose import JWTError, jwt
from passlib.context import CryptContext
from pydantic import BaseModel, EmailStr, Field
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from uuid import UUID, uuid4
import secrets


# ============================================================================
# Configuration
# ============================================================================

SECRET_KEY = "your-secret-key-change-in-production-use-env-var"  # TODO: Use environment variable
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 15
REFRESH_TOKEN_EXPIRE_DAYS = 7

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


# ============================================================================
# Pydantic Models
# ============================================================================

class UserBase(BaseModel):
    """Base user model."""
    username: str = Field(..., min_length=3, max_length=50)
    email: EmailStr
    full_name: Optional[str] = None


class UserCreate(UserBase):
    """User creation model."""
    password: str = Field(..., min_length=8, max_length=100)


class UserLogin(BaseModel):
    """User login model."""
    username: str
    password: str


class UserInDB(UserBase):
    """User model in database."""
    id: UUID
    hashed_password: str
    is_active: bool = True
    is_superuser: bool = False
    roles: list[str] = []
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class UserResponse(UserBase):
    """User response model (without password)."""
    id: UUID
    is_active: bool
    is_superuser: bool
    roles: list[str]
    created_at: datetime


class Token(BaseModel):
    """Token response model."""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class TokenData(BaseModel):
    """Token payload data."""
    sub: str  # user_id
    username: str
    email: str
    roles: list[str]
    permissions: list[str]
    exp: int
    iat: int
    jti: str  # Token unique ID


class RefreshTokenRequest(BaseModel):
    """Refresh token request."""
    refresh_token: str


# ============================================================================
# Password Utilities
# ============================================================================

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verify a plain password against a hashed password.

    Args:
        plain_password: Plain text password
        hashed_password: Hashed password from database

    Returns:
        True if password matches, False otherwise
    """
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """
    Hash a password.

    Args:
        password: Plain text password

    Returns:
        Hashed password
    """
    return pwd_context.hash(password)


# ============================================================================
# Token Utilities
# ============================================================================

def create_access_token(data: Dict[str, Any], expires_delta: Optional[timedelta] = None) -> str:
    """
    Create a JWT access token.

    Args:
        data: Token payload data
        expires_delta: Token expiration time

    Returns:
        Encoded JWT token
    """
    to_encode = data.copy()

    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)

    to_encode.update({
        "exp": expire,
        "iat": datetime.utcnow(),
        "jti": str(uuid4())
    })

    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def create_refresh_token(user_id: str) -> str:
    """
    Create a JWT refresh token.

    Args:
        user_id: User ID

    Returns:
        Encoded JWT refresh token
    """
    expire = datetime.utcnow() + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)

    to_encode = {
        "sub": user_id,
        "type": "refresh",
        "exp": expire,
        "iat": datetime.utcnow(),
        "jti": str(uuid4())
    }

    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def decode_token(token: str) -> TokenData:
    """
    Decode and validate a JWT token.

    Args:
        token: JWT token

    Returns:
        Token data

    Raises:
        JWTError: If token is invalid or expired
    """
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])

        # Extract token data
        token_data = TokenData(
            sub=payload.get("sub"),
            username=payload.get("username"),
            email=payload.get("email"),
            roles=payload.get("roles", []),
            permissions=payload.get("permissions", []),
            exp=payload.get("exp"),
            iat=payload.get("iat"),
            jti=payload.get("jti")
        )

        return token_data

    except JWTError as e:
        raise JWTError(f"Could not validate credentials: {str(e)}")


def is_token_expired(token_data: TokenData) -> bool:
    """
    Check if a token is expired.

    Args:
        token_data: Token data

    Returns:
        True if expired, False otherwise
    """
    if not token_data.exp:
        return True

    expiration = datetime.fromtimestamp(token_data.exp)
    return datetime.utcnow() > expiration


# ============================================================================
# Role & Permission Mapping
# ============================================================================

ROLE_PERMISSIONS = {
    "viewer": [
        "agents:read",
        "tasks:read",
        "analytics:read",
        "alerts:read",
        "graphs:read"
    ],
    "operator": [
        "agents:read",
        "agents:update",
        "tasks:read",
        "tasks:write",
        "tasks:execute",
        "analytics:read",
        "alerts:read",
        "alerts:acknowledge",
        "graphs:read",
        "graphs:analyze"
    ],
    "admin": [
        "agents:*",
        "tasks:*",
        "analytics:*",
        "alerts:*",
        "graphs:*",
        "users:read",
        "users:update"
    ],
    "superadmin": ["*"]
}


def get_permissions_for_roles(roles: list[str]) -> list[str]:
    """
    Get all permissions for given roles.

    Args:
        roles: List of role names

    Returns:
        List of permission strings
    """
    permissions = set()

    for role in roles:
        role_perms = ROLE_PERMISSIONS.get(role, [])
        permissions.update(role_perms)

    return list(permissions)


def has_permission(user_permissions: list[str], required_permission: str) -> bool:
    """
    Check if user has required permission.

    Args:
        user_permissions: User's permissions
        required_permission: Required permission (e.g., "agents:write")

    Returns:
        True if user has permission, False otherwise
    """
    # Check for wildcard permission
    if "*" in user_permissions:
        return True

    # Check for exact match
    if required_permission in user_permissions:
        return True

    # Check for resource wildcard (e.g., "agents:*" matches "agents:write")
    resource, action = required_permission.split(":", 1)
    wildcard = f"{resource}:*"

    if wildcard in user_permissions:
        return True

    return False


# ============================================================================
# User Management (Placeholder - needs database models)
# ============================================================================

class UserManager:
    """
    User management class.

    Handles user CRUD operations, authentication, and authorization.
    """

    @staticmethod
    async def create_user(db: AsyncSession, user_data: UserCreate) -> UserInDB:
        """
        Create a new user.

        Args:
            db: Database session
            user_data: User creation data

        Returns:
            Created user
        """
        # TODO: Implement with actual User model
        hashed_password = get_password_hash(user_data.password)

        # Placeholder - replace with actual database operation
        user = UserInDB(
            id=uuid4(),
            username=user_data.username,
            email=user_data.email,
            full_name=user_data.full_name,
            hashed_password=hashed_password,
            is_active=True,
            is_superuser=False,
            roles=["viewer"],  # Default role
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )

        return user

    @staticmethod
    async def authenticate_user(db: AsyncSession, username: str, password: str) -> Optional[UserInDB]:
        """
        Authenticate a user.

        Args:
            db: Database session
            username: Username
            password: Password

        Returns:
            User if authentication successful, None otherwise
        """
        # TODO: Implement with actual database query
        # Placeholder - replace with actual database operation

        # This is a mock user for demonstration
        mock_user = UserInDB(
            id=uuid4(),
            username="admin",
            email="admin@example.com",
            full_name="Admin User",
            hashed_password=get_password_hash("admin123"),
            is_active=True,
            is_superuser=True,
            roles=["admin"],
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )

        # Verify credentials
        if username != mock_user.username:
            return None

        if not verify_password(password, mock_user.hashed_password):
            return None

        return mock_user

    @staticmethod
    async def get_user_by_id(db: AsyncSession, user_id: UUID) -> Optional[UserInDB]:
        """
        Get user by ID.

        Args:
            db: Database session
            user_id: User ID

        Returns:
            User if found, None otherwise
        """
        # TODO: Implement with actual database query
        return None

    @staticmethod
    async def get_user_by_username(db: AsyncSession, username: str) -> Optional[UserInDB]:
        """
        Get user by username.

        Args:
            db: Database session
            username: Username

        Returns:
            User if found, None otherwise
        """
        # TODO: Implement with actual database query
        return None


# ============================================================================
# Token Blacklist (Redis-based, placeholder)
# ============================================================================

class TokenBlacklist:
    """
    Token blacklist for logout functionality.

    Uses Redis to store blacklisted tokens.
    """

    # TODO: Implement with Redis
    _blacklisted_tokens: set = set()

    @classmethod
    async def add_token(cls, jti: str, exp: int):
        """
        Add token to blacklist.

        Args:
            jti: Token unique ID
            exp: Token expiration timestamp
        """
        cls._blacklisted_tokens.add(jti)
        # TODO: Store in Redis with TTL based on exp

    @classmethod
    async def is_blacklisted(cls, jti: str) -> bool:
        """
        Check if token is blacklisted.

        Args:
            jti: Token unique ID

        Returns:
            True if blacklisted, False otherwise
        """
        return jti in cls._blacklisted_tokens
        # TODO: Check Redis


# ============================================================================
# Authentication Functions
# ============================================================================

async def register_user(db: AsyncSession, user_data: UserCreate) -> UserResponse:
    """
    Register a new user.

    Args:
        db: Database session
        user_data: User registration data

    Returns:
        Created user (without password)
    """
    # Check if username exists
    existing_user = await UserManager.get_user_by_username(db, user_data.username)
    if existing_user:
        raise ValueError("Username already exists")

    # Create user
    user = await UserManager.create_user(db, user_data)

    return UserResponse(
        id=user.id,
        username=user.username,
        email=user.email,
        full_name=user.full_name,
        is_active=user.is_active,
        is_superuser=user.is_superuser,
        roles=user.roles,
        created_at=user.created_at
    )


async def login_user(db: AsyncSession, login_data: UserLogin) -> Token:
    """
    Login user and return tokens.

    Args:
        db: Database session
        login_data: Login credentials

    Returns:
        Access and refresh tokens
    """
    # Authenticate user
    user = await UserManager.authenticate_user(db, login_data.username, login_data.password)

    if not user:
        raise ValueError("Incorrect username or password")

    if not user.is_active:
        raise ValueError("User account is inactive")

    # Get permissions
    permissions = get_permissions_for_roles(user.roles)

    # Create tokens
    access_token_data = {
        "sub": str(user.id),
        "username": user.username,
        "email": user.email,
        "roles": user.roles,
        "permissions": permissions
    }

    access_token = create_access_token(access_token_data)
    refresh_token = create_refresh_token(str(user.id))

    return Token(
        access_token=access_token,
        refresh_token=refresh_token,
        token_type="bearer"
    )


async def refresh_access_token(db: AsyncSession, refresh_token: str) -> Token:
    """
    Refresh access token using refresh token.

    Args:
        db: Database session
        refresh_token: Refresh token

    Returns:
        New access and refresh tokens
    """
    try:
        # Decode refresh token
        payload = jwt.decode(refresh_token, SECRET_KEY, algorithms=[ALGORITHM])

        # Verify token type
        if payload.get("type") != "refresh":
            raise ValueError("Invalid token type")

        # Check if blacklisted
        jti = payload.get("jti")
        if await TokenBlacklist.is_blacklisted(jti):
            raise ValueError("Token has been revoked")

        # Get user
        user_id = UUID(payload.get("sub"))
        user = await UserManager.get_user_by_id(db, user_id)

        if not user or not user.is_active:
            raise ValueError("User not found or inactive")

        # Get permissions
        permissions = get_permissions_for_roles(user.roles)

        # Create new tokens
        access_token_data = {
            "sub": str(user.id),
            "username": user.username,
            "email": user.email,
            "roles": user.roles,
            "permissions": permissions
        }

        new_access_token = create_access_token(access_token_data)
        new_refresh_token = create_refresh_token(str(user.id))

        # Blacklist old refresh token
        await TokenBlacklist.add_token(jti, payload.get("exp"))

        return Token(
            access_token=new_access_token,
            refresh_token=new_refresh_token,
            token_type="bearer"
        )

    except JWTError:
        raise ValueError("Invalid refresh token")


async def logout_user(access_token: str, refresh_token: str):
    """
    Logout user by blacklisting tokens.

    Args:
        access_token: Access token
        refresh_token: Refresh token
    """
    try:
        # Decode and blacklist access token
        access_payload = jwt.decode(access_token, SECRET_KEY, algorithms=[ALGORITHM])
        await TokenBlacklist.add_token(
            access_payload.get("jti"),
            access_payload.get("exp")
        )

        # Decode and blacklist refresh token
        refresh_payload = jwt.decode(refresh_token, SECRET_KEY, algorithms=[ALGORITHM])
        await TokenBlacklist.add_token(
            refresh_payload.get("jti"),
            refresh_payload.get("exp")
        )

    except JWTError:
        pass  # Ignore errors during logout
