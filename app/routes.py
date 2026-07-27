"""
API routes for task management CRUD operations, analytics, and reset endpoints.
"""
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status

from app import schemas, data, utils
from app.rate_limiter import login_limiter
from app.supabase_client import supabase

router = APIRouter()


# -----------------------------------------------------------------------------
# Stage 1: Auth Signup & Login Routes
# -----------------------------------------------------------------------------

@router.post(
    "/auth/signup",
    status_code=status.HTTP_201_CREATED,
    responses={
        400: {"model": schemas.ErrorResponse, "description": "Bad Request"}
    },
    summary="Sign Up User",
    description="Registers a new user account with email and password via Supabase Auth.",
)
def signup(payload: schemas.UserSignUpRequest):
    """Create a new user account using Supabase Auth."""
    if not payload.email or not payload.password:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Missing email or password",
        )
    try:
        res = supabase.auth.sign_up({"email": payload.email, "password": payload.password})
        if getattr(res, "user", None) is None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Signup failed",
            )
        user_data = res.user
        return {
            "message": "User registered successfully",
            "user": {
                "id": getattr(user_data, "id", None),
                "email": getattr(user_data, "email", None),
                "created_at": getattr(user_data, "created_at", None),
            },
        }
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc


@router.post(
    "/auth/login",
    response_model=schemas.TokenResponse,
    status_code=status.HTTP_200_OK,
    responses={
        400: {"model": schemas.ErrorResponse, "description": "Bad Request"},
        401: {"model": schemas.ErrorResponse, "description": "Invalid login credentials"},
        429: {"model": schemas.ErrorResponse, "description": "Too many login attempts"},
    },
    summary="Log In User",
    description="Authenticates credentials with Supabase Auth and returns JWT access and refresh tokens.",
)
def login(payload: schemas.UserLoginRequest):
    """Authenticate user credentials and return JWT tokens."""
    if not payload.email or not payload.password:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Missing email or password",
        )
    
    # Enforce login rate limiting
    login_limiter.check_rate_limit(payload.email)
    
    try:
        res = supabase.auth.sign_in_with_password({"email": payload.email, "password": payload.password})
        session = getattr(res, "session", None)
        if not res or not session or not getattr(session, "access_token", None):
            login_limiter.record_failure(payload.email)
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid login credentials",
            )
        
        login_limiter.record_success(payload.email)
        user_obj = getattr(res, "user", None)
        user_dict = {
            "id": getattr(user_obj, "id", None) if user_obj else None,
            "email": getattr(user_obj, "email", None) if user_obj else None,
            "created_at": getattr(user_obj, "created_at", None) if user_obj else None,
        }
        return {
            "access_token": session.access_token,
            "refresh_token": getattr(session, "refresh_token", None),
            "token_type": "bearer",
            "user": user_dict,
        }
    except HTTPException:
        raise
    except Exception as exc:
        login_limiter.record_failure(payload.email)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid login credentials",
        ) from exc


@router.get(
    "/",
    response_model=schemas.APIMetadata,
    status_code=status.HTTP_200_OK,
    summary="Get API Metadata",
    description="Returns metadata about the API including name, version, and endpoints.",
)
def get_root():
    """Root endpoint returning API details."""
    return {
        "name": "Task API",
        "version": "1.0",
        "endpoints": ["/tasks"],
    }


@router.get(
    "/health",
    response_model=schemas.HealthCheck,
    status_code=status.HTTP_200_OK,
    summary="Health Check",
    description="Checks the health status of the application.",
)
def get_health():
    """Health check endpoint."""
    return {"status": "ok"}


@router.get(
    "/stats",
    response_model=schemas.TaskStats,
    status_code=status.HTTP_200_OK,
    summary="Get Task Statistics",
    description="Returns statistical overview of tasks including total, done, and open counts.",
)
def get_stats():
    """Bonus endpoint returning task statistics from database."""
    tasks = data.get_all_tasks()
    return utils.calculate_task_stats(tasks)


@router.post(
    "/reset",
    response_model=List[schemas.Task],
    status_code=status.HTTP_200_OK,
    summary="Reset Tasks",
    description="Restores the initial state of tasks in PostgreSQL database.",
)
def reset_tasks():
    """Bonus endpoint to restore initial tasks in database."""
    return data.reset_tasks_db()


@router.get(
    "/tasks",
    response_model=List[schemas.Task],
    status_code=status.HTTP_200_OK,
    summary="Get All Tasks",
    description="Returns a list of all tasks. Supports optional status filtering and title search.",
)
def get_tasks(
    done: Optional[bool] = Query(default=None, description="Filter by completion status"),
    search: Optional[str] = Query(default=None, description="Search tasks by title keyword"),
):
    """Retrieve tasks with optional filter and search parameters from PostgreSQL database."""
    return data.get_all_tasks(done=done, search=search)


@router.get(
    "/tasks/{id}",
    response_model=schemas.Task,
    status_code=status.HTTP_200_OK,
    responses={
        404: {"model": schemas.ErrorResponse, "description": "Task not found"}
    },
    summary="Get Task by ID",
    description="Retrieve details of a single task by its unique identifier.",
)
def get_task(id: int):
    """Retrieve one task by ID from PostgreSQL database."""
    task = data.get_task_by_id(id)
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found",
        )
    return task


@router.post(
    "/tasks",
    response_model=schemas.Task,
    status_code=status.HTTP_201_CREATED,
    responses={
        400: {"model": schemas.ErrorResponse, "description": "Title missing or empty"}
    },
    summary="Create Task",
    description="Creates a new task with auto-assigned ID and done set to false in PostgreSQL database.",
)
def create_task(payload: schemas.TaskCreate):
    """Create a new task in PostgreSQL database."""
    return data.create_task(title=payload.title)


@router.put(
    "/tasks/{id}",
    response_model=schemas.Task,
    status_code=status.HTTP_200_OK,
    responses={
        400: {"model": schemas.ErrorResponse, "description": "Invalid body or missing fields"},
        404: {"model": schemas.ErrorResponse, "description": "Task not found"},
    },
    summary="Update Task",
    description="Update title and/or done status of an existing task in PostgreSQL database.",
)
def update_task(id: int, payload: schemas.TaskUpdate):
    """Update an existing task in PostgreSQL database."""
    if payload.title is None and payload.done is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="At least one field (title or done) must be provided to update",
        )

    updated_task = data.update_task(
        task_id=id,
        title=payload.title,
        done=payload.done,
    )

    if not updated_task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found",
        )

    return updated_task


@router.delete(
    "/tasks/{id}",
    status_code=status.HTTP_204_NO_CONTENT,
    responses={
        404: {"model": schemas.ErrorResponse, "description": "Task not found"}
    },
    summary="Delete Task",
    description="Deletes a task from PostgreSQL database by its unique identifier.",
)
def delete_task(id: int):
    """Delete a task by ID from PostgreSQL database."""
    deleted = data.delete_task(id)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found",
        )
    return None
