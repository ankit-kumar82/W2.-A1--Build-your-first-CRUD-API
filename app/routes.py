"""
API routes for task management CRUD operations, analytics, and reset endpoints.
"""
from typing import List, Optional
from fastapi import APIRouter, HTTPException, Query, status

from app import schemas, data, utils

router = APIRouter()


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
    description="Restores the initial state of tasks in SQLite database.",
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
    """Retrieve tasks with optional filter and search parameters from SQLite database."""
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
    """Retrieve one task by ID from SQLite database."""
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
    description="Creates a new task with auto-assigned ID and done set to false in SQLite database.",
)
def create_task(payload: schemas.TaskCreate):
    """Create a new task in SQLite database."""
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
    description="Update title and/or done status of an existing task in SQLite database.",
)
def update_task(id: int, payload: schemas.TaskUpdate):
    """Update an existing task in SQLite database."""
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
    description="Deletes a task from SQLite database by its unique identifier.",
)
def delete_task(id: int):
    """Delete a task by ID from SQLite database."""
    deleted = data.delete_task(id)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found",
        )
    return None
