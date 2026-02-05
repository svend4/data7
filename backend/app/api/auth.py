"""
Authentication API Routes

JWT-based authentication endpoints for user registration, login, and token management.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.jwt import (
    UserCreate,
    UserLogin,
    UserResponse,
    Token,
    RefreshTokenRequest,
    TokenData,
    register_user,
    login_user,
    refresh_access_token,
    logout_user,
    decode_token,
    TokenBlacklist
)
from app.auth.rbac import get_current_user
from app.infrastructure import get_db


router = APIRouter(tags=["Authentication"])
security = HTTPBearer()


# ============================================================================
# Public Endpoints (No Authentication Required)
# ============================================================================

@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register(
    user_data: UserCreate,
    db: AsyncSession = Depends(get_db)
):
    """
    Register a new user.

    Creates a new user account with the provided credentials.

    Args:
        user_data: User registration data (username, email, password, etc.)
        db: Database session

    Returns:
        Created user information (without password)

    Raises:
        HTTPException 400: If username or email already exists
        HTTPException 422: If validation fails
    """
    try:
        user = await register_user(db, user_data)
        return user

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Registration failed: {str(e)}"
        )


@router.post("/login", response_model=Token)
async def login(
    credentials: UserLogin,
    db: AsyncSession = Depends(get_db)
):
    """
    Login with username and password.

    Authenticates user and returns access and refresh tokens.

    Args:
        credentials: Login credentials (username, password)
        db: Database session

    Returns:
        Access token and refresh token

    Raises:
        HTTPException 401: If credentials are invalid
        HTTPException 403: If user account is inactive
    """
    try:
        tokens = await login_user(db, credentials)
        return tokens

    except ValueError as e:
        error_message = str(e)

        if "inactive" in error_message.lower():
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=error_message
            )

        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=error_message,
            headers={"WWW-Authenticate": "Bearer"}
        )

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Login failed: {str(e)}"
        )


@router.post("/refresh", response_model=Token)
async def refresh(
    request: RefreshTokenRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    Refresh access token using refresh token.

    Generates new access and refresh tokens. Old refresh token is invalidated.

    Args:
        request: Refresh token
        db: Database session

    Returns:
        New access token and refresh token

    Raises:
        HTTPException 401: If refresh token is invalid or expired
    """
    try:
        tokens = await refresh_access_token(db, request.refresh_token)
        return tokens

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e),
            headers={"WWW-Authenticate": "Bearer"}
        )

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Token refresh failed: {str(e)}"
        )


# ============================================================================
# Protected Endpoints (Authentication Required)
# ============================================================================

@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
async def logout(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    refresh_token: RefreshTokenRequest = None
):
    """
    Logout user.

    Invalidates access and refresh tokens by adding them to blacklist.

    Args:
        credentials: Bearer token from Authorization header
        refresh_token: Optional refresh token to invalidate

    Returns:
        No content (204)

    Raises:
        HTTPException 401: If token is invalid
    """
    try:
        access_token = credentials.credentials

        # If refresh token provided, invalidate both
        if refresh_token:
            await logout_user(access_token, refresh_token.refresh_token)
        else:
            # Invalidate only access token
            token_data = decode_token(access_token)
            await TokenBlacklist.add_token(token_data.jti, token_data.exp)

        return None

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Logout failed: {str(e)}",
            headers={"WWW-Authenticate": "Bearer"}
        )


@router.get("/me", response_model=dict)
async def get_current_user_info(
    current_user: TokenData = Depends(get_current_user)
):
    """
    Get current authenticated user information.

    Returns information about the currently authenticated user from JWT token.

    Args:
        current_user: Current user from JWT token

    Returns:
        User information including roles and permissions

    Requires:
        Valid JWT token in Authorization header
    """
    return {
        "user_id": current_user.sub,
        "username": current_user.username,
        "email": current_user.email,
        "roles": current_user.roles,
        "permissions": current_user.permissions,
        "issued_at": current_user.iat,
        "expires_at": current_user.exp
    }


@router.post("/verify", response_model=dict)
async def verify_token(
    current_user: TokenData = Depends(get_current_user)
):
    """
    Verify JWT token validity.

    Checks if the provided token is valid and not expired.

    Args:
        current_user: Current user from JWT token

    Returns:
        Token validity status

    Raises:
        HTTPException 401: If token is invalid or expired
    """
    return {
        "valid": True,
        "user_id": current_user.sub,
        "username": current_user.username,
        "roles": current_user.roles
    }


# ============================================================================
# Health Check
# ============================================================================

@router.get("/health")
async def auth_health():
    """
    Authentication service health check.

    Returns:
        Health status of authentication service
    """
    return {
        "status": "healthy",
        "service": "authentication",
        "features": {
            "registration": "enabled",
            "login": "enabled",
            "refresh": "enabled",
            "logout": "enabled",
            "rbac": "enabled"
        }
    }
