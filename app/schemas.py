"""
Pydantic schemas for request validation and response serialization.
"""
from typing import List, Optional
from pydantic import BaseModel, ConfigDict, Field, field_validator


class APIMetadata(BaseModel):
    """Schema for root endpoint response."""
    name: str = Field(default="Task API", description="Name of the API")
    version: str = Field(default="1.0", description="API version")
    endpoints: List[str] = Field(default=["/tasks"], description="Available base endpoints")


class HealthCheck(BaseModel):
    """Schema for health endpoint response."""
    status: str = Field(default="ok", description="Status of the application")


class TaskBase(BaseModel):
    """Base schema for task attributes."""
    title: str = Field(..., description="Title of the task")

    @field_validator("title")
    @classmethod
    def validate_title_not_empty(cls, value: str) -> str:
        """Validate that title is present and non-empty."""
        if not value or not value.strip():
            raise ValueError("Title cannot be missing or empty")
        return value.strip()


class TaskCreate(TaskBase):
    """Schema for creating a new task."""
    pass


class TaskUpdate(BaseModel):
    """Schema for updating an existing task."""
    title: Optional[str] = Field(default=None, description="Updated title of the task")
    done: Optional[bool] = Field(default=None, description="Updated completion status")

    @field_validator("title")
    @classmethod
    def validate_title_if_provided(cls, value: Optional[str]) -> Optional[str]:
        """Validate title if provided in update payload."""
        if value is not None and not value.strip():
            raise ValueError("Title cannot be empty")
        return value.strip() if value is not None else None


class Task(TaskBase):
    """Schema representing a complete Task object."""
    id: int = Field(..., description="Unique identifier for the task")
    done: bool = Field(default=False, description="Completion status of the task")

    model_config = ConfigDict(from_attributes=True)


class TaskStats(BaseModel):
    """Schema for task statistics."""
    total: int = Field(..., description="Total number of tasks")
    done: int = Field(..., description="Number of completed tasks")
    open: int = Field(..., description="Number of open (uncompleted) tasks")


class ErrorResponse(BaseModel):
    """Schema for error responses."""
    error: str = Field(..., description="Error message description")


class UserSignUpRequest(BaseModel):
    """Schema for user registration request."""
    email: str = Field(..., description="User email address")
    password: str = Field(..., description="User password")

    @field_validator("email", "password")
    @classmethod
    def validate_not_empty(cls, value: str) -> str:
        if not value or not value.strip():
            raise ValueError("Email and password cannot be empty")
        return value.strip()


class UserLoginRequest(BaseModel):
    """Schema for user login request."""
    email: str = Field(..., description="User email address")
    password: str = Field(..., description="User password")

    @field_validator("email", "password")
    @classmethod
    def validate_not_empty(cls, value: str) -> str:
        if not value or not value.strip():
            raise ValueError("Email and password cannot be empty")
        return value.strip()


class RefreshTokenRequest(BaseModel):
    """Schema for refreshing access token."""
    refresh_token: str = Field(..., description="Refresh token string")

    @field_validator("refresh_token")
    @classmethod
    def validate_not_empty(cls, value: str) -> str:
        if not value or not value.strip():
            raise ValueError("Refresh token cannot be empty")
        return value.strip()


class TokenResponse(BaseModel):
    """Schema for token authentication response."""
    access_token: str = Field(..., description="JWT Access Token")
    refresh_token: Optional[str] = Field(default=None, description="Refresh Token")
    token_type: str = Field(default="bearer", description="Token type")
    user: Optional[dict] = Field(default=None, description="Authenticated user info")


class UserProfileResponse(BaseModel):
    """Schema for protected user profile response."""
    id: str = Field(..., description="User unique identifier")
    email: str = Field(..., description="User email address")
    created_at: Optional[str] = Field(default=None, description="Account creation timestamp")
    role: Optional[str] = Field(default="authenticated", description="User role")
