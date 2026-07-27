"""
Auth guard middleware / dependency module for FastAPI.
Extracts and verifies JWT Bearer tokens with Supabase Auth.
"""
from typing import Any, Dict, Optional
from fastapi import Depends, HTTPException, Request, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from app.supabase_client import supabase

security_scheme = HTTPBearer(auto_error=False)


def extract_token_from_request(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security_scheme),
) -> str:
    """Extract raw bearer token string from request header."""
    if not credentials or not credentials.credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Access token required",
        )
    return credentials.credentials


async def get_current_user(
    token: str = Depends(extract_token_from_request),
) -> Dict[str, Any]:
    """
    Verifies access token with Supabase Auth API.
    Returns authenticated user payload if valid, otherwise raises 401 Unauthorized.
    """
    try:
        response = supabase.auth.get_user(token)
        if not response or not getattr(response, "user", None):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid or expired token",
            )
        user_obj = response.user
        # Convert user instance to dict representation
        user_dict = {
            "id": getattr(user_obj, "id", None),
            "email": getattr(user_obj, "email", None),
            "created_at": getattr(user_obj, "created_at", None),
            "role": getattr(user_obj, "role", "authenticated"),
            "user_metadata": getattr(user_obj, "user_metadata", {}) or {},
            "app_metadata": getattr(user_obj, "app_metadata", {}) or {},
        }
        return user_dict
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
        ) from exc


async def require_admin(
    current_user: Dict[str, Any] = Depends(get_current_user),
) -> Dict[str, Any]:
    """
    Authorization dependency ensuring the current user has admin privileges.
    Returns 403 Forbidden if the user is not an admin.
    """
    role = current_user.get("role")
    user_meta = current_user.get("user_metadata", {})
    app_meta = current_user.get("app_metadata", {})
    is_admin = (
        role == "admin"
        or user_meta.get("role") == "admin"
        or app_meta.get("role") == "admin"
        or (current_user.get("email") and "admin" in current_user.get("email", ""))
    )
    if not is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Forbidden: Admin access required",
        )
    return current_user
