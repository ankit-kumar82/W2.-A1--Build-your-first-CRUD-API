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
