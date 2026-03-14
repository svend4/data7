"""
Integration Tests for Authentication API

Tests the complete authentication flow including registration, login,
token refresh, and authorization.
"""

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession


# ============================================================================
# Authentication Flow Tests
# ============================================================================

class TestAuthenticationFlow:
    """Test complete authentication workflows."""

    @pytest.mark.asyncio
    async def test_complete_auth_flow(self, async_client: AsyncClient):
        """
        Test complete authentication flow:
        1. Register
        2. Login
        3. Access protected endpoint
        4. Refresh token
        5. Logout
        """
        # 1. Register new user
        register_data = {
            "username": "testuser",
            "email": "test@example.com",
            "password": "SecurePass123",
            "full_name": "Test User"
        }

        register_response = await async_client.post(
            "/api/auth/register",
            json=register_data
        )

        assert register_response.status_code == 201
        user_data = register_response.json()
        assert user_data["username"] == "testuser"
        assert user_data["email"] == "test@example.com"
        assert "id" in user_data
        assert "hashed_password" not in user_data  # Password should not be returned

        # 2. Login
        login_data = {
            "username": "testuser",
            "password": "SecurePass123"
        }

        login_response = await async_client.post(
            "/api/auth/login",
            json=login_data
        )

        assert login_response.status_code == 200
        tokens = login_response.json()
        assert "access_token" in tokens
        assert "refresh_token" in tokens
        assert tokens["token_type"] == "bearer"

        access_token = tokens["access_token"]
        refresh_token = tokens["refresh_token"]

        # 3. Access protected endpoint with access token
        headers = {"Authorization": f"Bearer {access_token}"}

        me_response = await async_client.get("/api/auth/me", headers=headers)

        assert me_response.status_code == 200
        me_data = me_response.json()
        assert me_data["username"] == "testuser"
        assert me_data["email"] == "test@example.com"
        assert "permissions" in me_data
        assert "roles" in me_data

        # 4. Refresh token
        refresh_response = await async_client.post(
            "/api/auth/refresh",
            json={"refresh_token": refresh_token}
        )

        assert refresh_response.status_code == 200
        new_tokens = refresh_response.json()
        assert "access_token" in new_tokens
        assert "refresh_token" in new_tokens
        assert new_tokens["access_token"] != access_token  # New token

        # 5. Logout
        logout_response = await async_client.post(
            "/api/auth/logout",
            headers=headers,
            json={"refresh_token": refresh_token}
        )

        assert logout_response.status_code == 204

        # 6. Verify old token is now invalid (blacklisted)
        verify_response = await async_client.post(
            "/api/auth/verify",
            headers=headers
        )

        # Token should be blacklisted
        assert verify_response.status_code in [401, 403]

    @pytest.mark.asyncio
    async def test_duplicate_username_rejected(self, async_client: AsyncClient):
        """Test that duplicate usernames are rejected."""
        user_data = {
            "username": "duplicate_test",
            "email": "user1@example.com",
            "password": "SecurePass123"
        }

        # First registration should succeed
        response1 = await async_client.post("/api/auth/register", json=user_data)
        assert response1.status_code == 201

        # Second registration with same username should fail
        user_data["email"] = "user2@example.com"  # Different email
        response2 = await async_client.post("/api/auth/register", json=user_data)
        assert response2.status_code == 400
        assert "already exists" in response2.json()["detail"].lower()

    @pytest.mark.asyncio
    async def test_login_with_wrong_password(self, async_client: AsyncClient):
        """Test login fails with wrong password."""
        # Register user
        register_data = {
            "username": "wrongpass_test",
            "email": "wrongpass@example.com",
            "password": "CorrectPassword123"
        }

        await async_client.post("/api/auth/register", json=register_data)

        # Try to login with wrong password
        login_data = {
            "username": "wrongpass_test",
            "password": "WrongPassword123"
        }

        response = await async_client.post("/api/auth/login", json=login_data)

        assert response.status_code == 401
        assert "incorrect" in response.json()["detail"].lower()

    @pytest.mark.asyncio
    async def test_login_with_nonexistent_user(self, async_client: AsyncClient):
        """Test login fails with non-existent username."""
        login_data = {
            "username": "nonexistent_user",
            "password": "SomePassword123"
        }

        response = await async_client.post("/api/auth/login", json=login_data)

        assert response.status_code == 401


# ============================================================================
# Token Management Tests
# ============================================================================

class TestTokenManagement:
    """Test JWT token operations."""

    @pytest.mark.asyncio
    async def test_access_protected_without_token(self, async_client: AsyncClient):
        """Test accessing protected endpoint without token fails."""
        response = await async_client.get("/api/auth/me")

        assert response.status_code in [401, 403]

    @pytest.mark.asyncio
    async def test_access_protected_with_invalid_token(self, async_client: AsyncClient):
        """Test accessing protected endpoint with invalid token fails."""
        headers = {"Authorization": "Bearer invalid_token_here"}

        response = await async_client.get("/api/auth/me", headers=headers)

        assert response.status_code in [401, 403]

    @pytest.mark.asyncio
    async def test_refresh_with_invalid_token(self, async_client: AsyncClient):
        """Test token refresh with invalid refresh token fails."""
        response = await async_client.post(
            "/api/auth/refresh",
            json={"refresh_token": "invalid_refresh_token"}
        )

        assert response.status_code == 401

    @pytest.mark.asyncio
    async def test_verify_valid_token(self, async_client: AsyncClient):
        """Test token verification with valid token."""
        # Register and login
        await async_client.post("/api/auth/register", json={
            "username": "verifytest",
            "email": "verify@example.com",
            "password": "Password123"
        })

        login_response = await async_client.post("/api/auth/login", json={
            "username": "verifytest",
            "password": "Password123"
        })

        tokens = login_response.json()
        headers = {"Authorization": f"Bearer {tokens['access_token']}"}

        # Verify token
        response = await async_client.post("/api/auth/verify", headers=headers)

        assert response.status_code == 200
        data = response.json()
        assert data["valid"] is True
        assert data["username"] == "verifytest"


# ============================================================================
# Authorization Tests (RBAC)
# ============================================================================

class TestAuthorization:
    """Test role-based access control."""

    @pytest.mark.asyncio
    async def test_user_has_default_viewer_role(self, async_client: AsyncClient):
        """Test newly registered user has default viewer role."""
        # Register and login
        await async_client.post("/api/auth/register", json={
            "username": "defaultrole",
            "email": "defaultrole@example.com",
            "password": "Password123"
        })

        login_response = await async_client.post("/api/auth/login", json={
            "username": "defaultrole",
            "password": "Password123"
        })

        tokens = login_response.json()
        headers = {"Authorization": f"Bearer {tokens['access_token']}"}

        # Get user info
        me_response = await async_client.get("/api/auth/me", headers=headers)
        user_data = me_response.json()

        # Should have viewer role by default
        assert "viewer" in user_data["roles"]
        assert "agents:read" in user_data["permissions"]
        assert "tasks:read" in user_data["permissions"]

    @pytest.mark.asyncio
    async def test_viewer_cannot_create_agents(self, async_client: AsyncClient):
        """Test viewer role cannot create agents (no agents:create permission)."""
        # This is a placeholder - actual implementation depends on
        # RBAC middleware being applied to agent creation endpoint
        # For now, we just verify the user doesn't have the permission

        await async_client.post("/api/auth/register", json={
            "username": "viewertest",
            "email": "viewer@example.com",
            "password": "Password123"
        })

        login_response = await async_client.post("/api/auth/login", json={
            "username": "viewertest",
            "password": "Password123"
        })

        tokens = login_response.json()
        headers = {"Authorization": f"Bearer {tokens['access_token']}"}

        me_response = await async_client.get("/api/auth/me", headers=headers)
        user_data = me_response.json()

        # Viewer should NOT have agents:create permission
        assert "agents:create" not in user_data["permissions"]


# ============================================================================
# Password Validation Tests
# ============================================================================

class TestPasswordValidation:
    """Test password validation rules."""

    @pytest.mark.asyncio
    async def test_short_password_rejected(self, async_client: AsyncClient):
        """Test password shorter than 8 characters is rejected."""
        register_data = {
            "username": "shortpass",
            "email": "short@example.com",
            "password": "Short1"  # Only 6 characters
        }

        response = await async_client.post("/api/auth/register", json=register_data)

        # Should fail validation (422 Unprocessable Entity)
        assert response.status_code == 422

    @pytest.mark.asyncio
    async def test_weak_password_rejected(self, async_client: AsyncClient):
        """Test weak password (all lowercase) is rejected."""
        register_data = {
            "username": "weakpass",
            "email": "weak@example.com",
            "password": "weakpassword"  # No uppercase or numbers
        }

        response = await async_client.post("/api/auth/register", json=register_data)

        # Should fail validation
        assert response.status_code == 422


# ============================================================================
# Email Validation Tests
# ============================================================================

class TestEmailValidation:
    """Test email validation."""

    @pytest.mark.asyncio
    async def test_invalid_email_rejected(self, async_client: AsyncClient):
        """Test invalid email format is rejected."""
        register_data = {
            "username": "invalidemail",
            "email": "not-an-email",  # Invalid format
            "password": "SecurePass123"
        }

        response = await async_client.post("/api/auth/register", json=register_data)

        # Should fail validation
        assert response.status_code == 422


# ============================================================================
# Health Check Tests
# ============================================================================

class TestAuthHealth:
    """Test authentication service health."""

    @pytest.mark.asyncio
    async def test_auth_health_endpoint(self, async_client: AsyncClient):
        """Test authentication health check endpoint."""
        response = await async_client.get("/api/auth/health")

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert data["service"] == "authentication"
        assert "features" in data
