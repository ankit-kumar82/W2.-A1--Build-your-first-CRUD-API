"""
In-memory dataset management for the Task API.
"""
from typing import List, Dict, Any, Optional

# Initial task dataset required by assignment
INITIAL_TASKS: List[Dict[str, Any]] = [
    {"id": 1, "title": "Learn FastAPI", "done": False},
    {"id": 2, "title": "Complete Assignment", "done": False},
    {"id": 3, "title": "Push to GitHub", "done": True},
]

# Primary in-memory store
tasks_db: List[Dict[str, Any]] = [task.copy() for task in INITIAL_TASKS]
_next_id: int = 4


def get_all_tasks() -> List[Dict[str, Any]]:
    """Retrieve all tasks from in-memory storage."""
    return tasks_db


def get_task_by_id(task_id: int) -> Optional[Dict[str, Any]]:
    """Retrieve a single task by ID."""
    for task in tasks_db:
        if task["id"] == task_id:
            return task
    return None


def create_task(title: str) -> Dict[str, Any]:
    """Create a new task with assigned ID and default done status."""
    global _next_id
    new_task = {
        "id": _next_id,
        "title": title,
        "done": False,
    }
    tasks_db.append(new_task)
    _next_id += 1
    return new_task


def update_task(task_id: int, title: Optional[str] = None, done: Optional[bool] = None) -> Optional[Dict[str, Any]]:
    """Update an existing task in-memory."""
    task = get_task_by_id(task_id)
    if task is None:
        return None

    if title is not None:
        task["title"] = title
    if done is not None:
        task["done"] = done

    return task


def delete_task(task_id: int) -> bool:
    """Delete a task by ID."""
    global tasks_db
    initial_len = len(tasks_db)
    tasks_db = [task for task in tasks_db if task["id"] != task_id]
    return len(tasks_db) < initial_len


def reset_tasks_db() -> List[Dict[str, Any]]:
    """Reset the task database to the initial seed state."""
    global tasks_db, _next_id
    tasks_db = [task.copy() for task in INITIAL_TASKS]
    _next_id = 4
    return tasks_db
