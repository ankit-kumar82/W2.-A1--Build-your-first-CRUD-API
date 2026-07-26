"""
SQLite database CRUD operations for the Task API using SQLModel.
"""
from typing import List, Dict, Any, Optional
from sqlmodel import Session, select, delete

from app.database import engine
from app.models import Task

# Initial sample dataset required by assignment
INITIAL_TASKS: List[Dict[str, Any]] = [
    {"id": 1, "title": "Learn FastAPI", "done": False},
    {"id": 2, "title": "Complete Assignment", "done": False},
    {"id": 3, "title": "Push to GitHub", "done": True},
]


def get_all_tasks(done: Optional[bool] = None, search: Optional[str] = None) -> List[Task]:
    """
    Retrieve tasks from SQLite database with optional status filter and search query.
    """
    with Session(engine) as session:
        statement = select(Task)

        if done is not None:
            statement = statement.where(Task.done == done)

        if search is not None and search.strip():
            query = f"%{search.strip()}%"
            statement = statement.where(Task.title.ilike(query))

        statement = statement.order_by(Task.id)
        results = session.exec(statement).all()
        return list(results)


def get_task_by_id(task_id: int) -> Optional[Task]:
    """Retrieve a single task by ID from SQLite database."""
    with Session(engine) as session:
        return session.get(Task, task_id)


def create_task(title: str) -> Task:
    """Create a new task in SQLite database with default done status set to False."""
    with Session(engine) as session:
        new_task = Task(title=title, done=False)
        session.add(new_task)
        session.commit()
        session.refresh(new_task)
        return new_task


def update_task(task_id: int, title: Optional[str] = None, done: Optional[bool] = None) -> Optional[Task]:
    """Update an existing task in SQLite database."""
    with Session(engine) as session:
        task = session.get(Task, task_id)
        if task is None:
            return None

        if title is not None:
            task.title = title
        if done is not None:
            task.done = done

        session.add(task)
        session.commit()
        session.refresh(task)
        return task


def delete_task(task_id: int) -> bool:
    """Delete a task by ID from SQLite database."""
    with Session(engine) as session:
        task = session.get(Task, task_id)
        if task is None:
            return False

        session.delete(task)
        session.commit()
        return True


def reset_tasks_db() -> List[Task]:
    """Reset the SQLite tasks table to the initial seed state."""
    with Session(engine) as session:
        session.exec(delete(Task))
        session.commit()

        sample_tasks = [
            Task(id=1, title="Learn FastAPI", done=False),
            Task(id=2, title="Complete Assignment", done=False),
            Task(id=3, title="Push to GitHub", done=True),
        ]
        session.add_all(sample_tasks)
        session.commit()

        for t in sample_tasks:
            session.refresh(t)

        return sample_tasks
