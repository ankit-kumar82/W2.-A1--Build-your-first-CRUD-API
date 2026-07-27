"""
Comprehensive test suite for Supabase Auth API, JWT verification middleware, protected routes,
role authorization (403 Forbidden), login rate limiting (429), and token refresh flow.
"""
from unittest.mock import MagicMock, patch
import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.rate_limiter import login_limiter

client = TestClient(app)


# -----------------------------------------------------------------------------
# 1. Public Endpoint Tests
# -----------------------------------------------------------------------------

def test_public_info_endpoint():
    """Verify GET /public/info returns 200 OK without authorization."""
    response = client.get("/public/info")
    assert response.status_code == 200
    assert response.json() == {"message": "Welcome stranger! This info is public."}


# -----------------------------------------------------------------------------
# 2. Signup Endpoint Validation Tests
# -----------------------------------------------------------------------------

def test_signup_missing_fields():
    """Verify POST /auth/signup returns 400 Bad Request when email or password is empty."""
    response = client.post("/auth/signup", json={"email": "", "password": ""})
    assert response.status_code == 400
    assert "error" in response.json()

    response_missing_pass = client.post("/auth/signup", json={"email": "test@example.com", "password": "   "})
    assert response_missing_pass.status_code == 400


@patch("app.routes.supabase.auth.sign_up")
def test_signup_success(mock_sign_up):
    """Verify POST /auth/signup returns 201 Created on successful registration."""
    mock_user = MagicMock()
    mock_user.id = "user-uuid-123"
    mock_user.email = "newuser@example.com"
    mock_user.created_at = "2026-07-27T00:00:00Z"

    mock_response = MagicMock()
    mock_response.user = mock_user
    mock_sign_up.return_value = mock_response

    response = client.post(
        "/auth/signup",
        json={"email": "newuser@example.com", "password": "securepassword123"},
    )
    assert response.status_code == 201
    data = response.json()
    assert data["message"] == "User registered successfully"
    assert data["user"]["email"] == "newuser@example.com"
    assert data["user"]["id"] == "user-uuid-123"


# -----------------------------------------------------------------------------
# 3. Login Endpoint & Rate Limiting Tests
# -----------------------------------------------------------------------------

def test_login_missing_fields():
    """Verify POST /auth/login returns 400 Bad Request for missing credentials."""
    response = client.post("/auth/login", json={"email": "", "password": "password"})
    assert response.status_code == 400


@patch("app.routes.supabase.auth.sign_in_with_password")
def test_login_invalid_credentials(mock_sign_in):
    """Verify POST /auth/login returns 401 Unauthorized for invalid credentials."""
    mock_sign_in.side_effect = Exception("Invalid login credentials")

    response = client.post(
        "/auth/login",
        json={"email": "invaliduser@example.com", "password": "wrongpassword"},
    )
    assert response.status_code == 401
    assert response.json()["error"] == "Invalid login credentials"


@patch("app.routes.supabase.auth.sign_in_with_password")
def test_login_success(mock_sign_in):
    """Verify POST /auth/login returns 200 OK with access and refresh tokens."""
    mock_session = MagicMock()
    mock_session.access_token = "valid-jwt-access-token"
    mock_session.refresh_token = "valid-refresh-token"

    mock_user = MagicMock()
    mock_user.id = "user-uuid-123"
    mock_user.email = "test@example.com"
    mock_user.created_at = "2026-07-27T00:00:00Z"

    mock_response = MagicMock()
    mock_response.session = mock_session
    mock_response.user = mock_user
    mock_sign_in.return_value = mock_response

    response = client.post(
        "/auth/login",
        json={"email": "test@example.com", "password": "password123"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["access_token"] == "valid-jwt-access-token"
    assert data["refresh_token"] == "valid-refresh-token"
    assert data["token_type"] == "bearer"
    assert data["user"]["email"] == "test@example.com"


@patch("app.routes.supabase.auth.sign_in_with_password")
def test_login_rate_limiting(mock_sign_in):
    """Verify login endpoint returns 429 Too Many Requests after consecutive failures."""
    mock_sign_in.side_effect = Exception("Invalid login credentials")
    test_email = "bruteforce@example.com"
    login_limiter.record_success(test_email)  # Reset state

    # Trigger failed attempts up to limit
    for _ in range(login_limiter.max_attempts):
        res = client.post(
            "/auth/login",
            json={"email": test_email, "password": "badpassword"},
        )
        assert res.status_code in (401, 429)

    # Next attempt should be blocked by rate limiter with status 429
    blocked_res = client.post(
        "/auth/login",
        json={"email": test_email, "password": "badpassword"},
    )
    assert blocked_res.status_code == 429
    assert "Too many failed login attempts" in blocked_res.json()["error"]
    login_limiter.record_success(test_email)  # Clean up


# -----------------------------------------------------------------------------
# 4. Protected Route & Token Verification Tests
# -----------------------------------------------------------------------------

def test_protected_profile_no_token():
    """Verify GET /protected/profile returns 401 when no Authorization header is sent."""
    response = client.get("/protected/profile")
    assert response.status_code == 401
    assert response.json()["error"] == "Access token required"


@patch("app.auth.supabase.auth.get_user")
def test_protected_profile_invalid_token(mock_get_user):
    """Verify GET /protected/profile returns 401 when token is tampered with or expired."""
    mock_get_user.side_effect = Exception("Invalid token")

    response = client.get(
        "/protected/profile",
        headers={"Authorization": "Bearer tampered-invalid-jwt-token"},
    )
    assert response.status_code == 401
    assert response.json()["error"] == "Invalid or expired token"


@patch("app.auth.supabase.auth.get_user")
def test_protected_profile_success(mock_get_user):
    """Verify GET /protected/profile returns 200 OK and user metadata for valid token."""
    mock_user = MagicMock()
    mock_user.id = "user-uuid-456"
    mock_user.email = "verified@example.com"
    mock_user.created_at = "2026-07-27T10:00:00Z"
    mock_user.role = "authenticated"
    mock_user.user_metadata = {}
    mock_user.app_metadata = {}

    mock_response = MagicMock()
    mock_response.user = mock_user
    mock_get_user.return_value = mock_response

    response = client.get(
        "/protected/profile",
        headers={"Authorization": "Bearer valid-jwt-token"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == "user-uuid-456"
    assert data["email"] == "verified@example.com"


@patch("app.auth.supabase.auth.get_user")
def test_protected_dashboard_success(mock_get_user):
    """Verify GET /protected/dashboard reuses middleware guard successfully."""
    mock_user = MagicMock()
    mock_user.id = "user-uuid-789"
    mock_user.email = "dashboard@example.com"
    mock_user.role = "authenticated"
    mock_user.user_metadata = {}
    mock_user.app_metadata = {}

    mock_response = MagicMock()
    mock_response.user = mock_user
    mock_get_user.return_value = mock_response

    response = client.get(
        "/protected/dashboard",
        headers={"Authorization": "Bearer valid-jwt-token"},
    )
    assert response.status_code == 200
    assert "Welcome to your private dashboard" in response.json()["message"]


# -----------------------------------------------------------------------------
# 5. Role Authorization (403 Forbidden) Tests
# -----------------------------------------------------------------------------

@patch("app.auth.supabase.auth.get_user")
def test_admin_route_forbidden_for_regular_user(mock_get_user):
    """Verify GET /protected/admin returns 403 Forbidden for non-admin user."""
    mock_user = MagicMock()
    mock_user.id = "regular-user-123"
    mock_user.email = "regularuser@example.com"
    mock_user.role = "authenticated"
    mock_user.user_metadata = {"role": "user"}
    mock_user.app_metadata = {}

    mock_response = MagicMock()
    mock_response.user = mock_user
    mock_get_user.return_value = mock_response

    response = client.get(
        "/protected/admin",
        headers={"Authorization": "Bearer regular-user-token"},
    )
    assert response.status_code == 403
    assert "Forbidden: Admin access required" in response.json()["error"]


@patch("app.auth.supabase.auth.get_user")
def test_admin_route_success_for_admin_user(mock_get_user):
    """Verify GET /protected/admin returns 200 OK for admin user."""
    mock_user = MagicMock()
    mock_user.id = "admin-user-999"
    mock_user.email = "admin@example.com"
    mock_user.role = "admin"
    mock_user.user_metadata = {"role": "admin"}
    mock_user.app_metadata = {}

    mock_response = MagicMock()
    mock_response.user = mock_user
    mock_get_user.return_value = mock_response

    response = client.get(
        "/protected/admin",
        headers={"Authorization": "Bearer admin-user-token"},
    )
    assert response.status_code == 200
    assert "Welcome Admin!" in response.json()["message"]


# -----------------------------------------------------------------------------
# 6. Logout & Token Refresh Tests
# -----------------------------------------------------------------------------

@patch("app.auth.supabase.auth.get_user")
@patch("app.routes.supabase.auth.sign_out")
def test_logout_endpoint(mock_sign_out, mock_get_user):
    """Verify POST /auth/logout returns 204 No Content for authenticated user."""
    mock_user = MagicMock()
    mock_user.id = "user-logout-1"
    mock_user.email = "logout@example.com"
    mock_user.user_metadata = {}
    mock_user.app_metadata = {}

    mock_response = MagicMock()
    mock_response.user = mock_user
    mock_get_user.return_value = mock_response

    response = client.post(
        "/auth/logout",
        headers={"Authorization": "Bearer valid-jwt-token"},
    )
    assert response.status_code == 204


@patch("app.routes.supabase.auth.refresh_session")
def test_refresh_token_success(mock_refresh):
    """Verify POST /auth/refresh returns 200 OK with new access token."""
    mock_session = MagicMock()
    mock_session.access_token = "new-fresh-access-token"
    mock_session.refresh_token = "new-fresh-refresh-token"

    mock_user = MagicMock()
    mock_user.id = "user-uuid-123"
    mock_user.email = "refreshed@example.com"

    mock_response = MagicMock()
    mock_response.session = mock_session
    mock_response.user = mock_user
    mock_refresh.return_value = mock_response

    response = client.post(
        "/auth/refresh",
        json={"refresh_token": "valid-old-refresh-token"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["access_token"] == "new-fresh-access-token"
    assert data["refresh_token"] == "new-fresh-refresh-token"
