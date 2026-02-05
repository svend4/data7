"""
Role-Based Access Control (RBAC) Middleware

Implements permission checking and role-based authorization.
Provides decorators for route protection and permission enforcement.
"""

from typing import List, Optional, Callable
from functools import wraps
from fastapi import HTTPException, status, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from app.auth.jwt import decode_token, has_permission, is_token_expired, TokenBlacklist


# ============================================================================
# Security Scheme
# ============================================================================

security = HTTPBearer()


# ============================================================================
# Permission Checker
# ============================================================================

class PermissionChecker:
    """
    Permission checker dependency.

    Usage:
        @router.get("/agents", dependencies=[Depends(PermissionChecker(["agents:read"]))])
        async def list_agents():
            ...
    """

    def __init__(self, required_permissions: List[str]):
        """
        Initialize permission checker.

        Args:
            required_permissions: List of required permissions
        """
        self.required_permissions = required_permissions

    async def __call__(
        self,
        credentials: HTTPAuthorizationCredentials = Depends(security)
    ):
        """
        Check if user has required permissions.

        Args:
            credentials: HTTP authorization credentials

        Raises:
            HTTPException: If user doesn't have required permissions
        """
        token = credentials.credentials

        try:
            # Decode token
            token_data = decode_token(token)

            # Check if token is expired
            if is_token_expired(token_data):
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Token has expired",
                    headers={"WWW-Authenticate": "Bearer"}
                )

            # Check if token is blacklisted
            if await TokenBlacklist.is_blacklisted(token_data.jti):
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Token has been revoked",
                    headers={"WWW-Authenticate": "Bearer"}
                )

            # Check permissions
            user_permissions = token_data.permissions

            for required_permission in self.required_permissions:
                if not has_permission(user_permissions, required_permission):
                    raise HTTPException(
                        status_code=status.HTTP_403_FORBIDDEN,
                        detail=f"Missing required permission: {required_permission}"
                    )

            return token_data

        except HTTPException:
            raise

        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate credentials",
                headers={"WWW-Authenticate": "Bearer"}
            )


# ============================================================================
# Role Checker
# ============================================================================

class RoleChecker:
    """
    Role checker dependency.

    Usage:
        @router.delete("/agents/{id}", dependencies=[Depends(RoleChecker(["admin"]))])
        async def delete_agent(id: str):
            ...
    """

    def __init__(self, required_roles: List[str]):
        """
        Initialize role checker.

        Args:
            required_roles: List of required roles (any one is sufficient)
        """
        self.required_roles = required_roles

    async def __call__(
        self,
        credentials: HTTPAuthorizationCredentials = Depends(security)
    ):
        """
        Check if user has one of required roles.

        Args:
            credentials: HTTP authorization credentials

        Raises:
            HTTPException: If user doesn't have required role
        """
        token = credentials.credentials

        try:
            # Decode token
            token_data = decode_token(token)

            # Check if token is expired
            if is_token_expired(token_data):
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Token has expired",
                    headers={"WWW-Authenticate": "Bearer"}
                )

            # Check if token is blacklisted
            if await TokenBlacklist.is_blacklisted(token_data.jti):
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Token has been revoked",
                    headers={"WWW-Authenticate": "Bearer"}
                )

            # Check roles
            user_roles = token_data.roles

            if not any(role in user_roles for role in self.required_roles):
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=f"Requires one of roles: {', '.join(self.required_roles)}"
                )

            return token_data

        except HTTPException:
            raise

        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate credentials",
                headers={"WWW-Authenticate": "Bearer"}
            )


# ============================================================================
# Get Current User
# ============================================================================

async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    """
    Get current authenticated user from token.

    Args:
        credentials: HTTP authorization credentials

    Returns:
        Token data

    Raises:
        HTTPException: If authentication fails
    """
    token = credentials.credentials

    try:
        # Decode token
        token_data = decode_token(token)

        # Check if token is expired
        if is_token_expired(token_data):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token has expired",
                headers={"WWW-Authenticate": "Bearer"}
            )

        # Check if token is blacklisted
        if await TokenBlacklist.is_blacklisted(token_data.jti):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token has been revoked",
                headers={"WWW-Authenticate": "Bearer"}
            )

        return token_data

    except HTTPException:
        raise

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"}
        )


# ============================================================================
# Optional Authentication
# ============================================================================

async def get_current_user_optional(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security)
):
    """
    Get current user (optional - returns None if not authenticated).

    Useful for endpoints that work both authenticated and unauthenticated.

    Args:
        credentials: Optional HTTP authorization credentials

    Returns:
        Token data or None
    """
    if not credentials:
        return None

    try:
        return await get_current_user(credentials)
    except HTTPException:
        return None


# ============================================================================
# Function Decorators
# ============================================================================

def require_permission(*permissions: str):
    """
    Decorator to require specific permissions.

    Usage:
        @require_permission("agents:write", "agents:delete")
        async def delete_agent(agent_id: str, current_user: TokenData):
            ...
    """
    def decorator(func: Callable):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Get current user from kwargs
            current_user = kwargs.get("current_user")

            if not current_user:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Authentication required"
                )

            # Check permissions
            user_permissions = current_user.permissions

            for permission in permissions:
                if not has_permission(user_permissions, permission):
                    raise HTTPException(
                        status_code=status.HTTP_403_FORBIDDEN,
                        detail=f"Missing required permission: {permission}"
                    )

            return await func(*args, **kwargs)

        return wrapper
    return decorator


def require_role(*roles: str):
    """
    Decorator to require specific roles.

    Usage:
        @require_role("admin", "superadmin")
        async def admin_operation(current_user: TokenData):
            ...
    """
    def decorator(func: Callable):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Get current user from kwargs
            current_user = kwargs.get("current_user")

            if not current_user:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Authentication required"
                )

            # Check roles
            user_roles = current_user.roles

            if not any(role in user_roles for role in roles):
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=f"Requires one of roles: {', '.join(roles)}"
                )

            return await func(*args, **kwargs)

        return wrapper
    return decorator


# ============================================================================
# Permission Helper Functions
# ============================================================================

def check_resource_owner(user_id: str, resource_user_id: str) -> bool:
    """
    Check if user is the owner of a resource.

    Args:
        user_id: Current user ID
        resource_user_id: Resource owner ID

    Returns:
        True if user is owner, False otherwise
    """
    return user_id == resource_user_id


def check_permission_or_owner(
    current_user,
    required_permission: str,
    resource_user_id: Optional[str] = None
) -> bool:
    """
    Check if user has permission OR is the resource owner.

    Args:
        current_user: Current user token data
        required_permission: Required permission
        resource_user_id: Optional resource owner ID

    Returns:
        True if user has permission or is owner, False otherwise
    """
    # Check permission
    if has_permission(current_user.permissions, required_permission):
        return True

    # Check ownership
    if resource_user_id and check_resource_owner(current_user.sub, resource_user_id):
        return True

    return False


# ============================================================================
# Permission Groups
# ============================================================================

PERMISSION_GROUPS = {
    "agents_read": ["agents:read"],
    "agents_write": ["agents:read", "agents:write"],
    "agents_full": ["agents:read", "agents:write", "agents:delete"],

    "tasks_read": ["tasks:read"],
    "tasks_write": ["tasks:read", "tasks:write"],
    "tasks_execute": ["tasks:read", "tasks:write", "tasks:execute"],
    "tasks_full": ["tasks:read", "tasks:write", "tasks:execute", "tasks:delete"],

    "analytics_read": ["analytics:read"],
    "analytics_full": ["analytics:read", "analytics:write"],

    "alerts_read": ["alerts:read"],
    "alerts_manage": ["alerts:read", "alerts:acknowledge", "alerts:resolve"],
    "alerts_configure": ["alerts:read", "alerts:acknowledge", "alerts:resolve", "alerts:configure"],

    "graphs_read": ["graphs:read"],
    "graphs_analyze": ["graphs:read", "graphs:analyze"],
    "graphs_optimize": ["graphs:read", "graphs:analyze", "graphs:optimize"],
    "graphs_full": ["graphs:read", "graphs:analyze", "graphs:optimize", "graphs:delete"],

    "admin": ["*"]
}


def get_permission_group(group_name: str) -> List[str]:
    """
    Get permissions for a permission group.

    Args:
        group_name: Group name

    Returns:
        List of permissions
    """
    return PERMISSION_GROUPS.get(group_name, [])
