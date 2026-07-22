"""
In-memory domain models for the Task API.
"""
from typing import Dict, Any


class TaskModel:
    """Domain model representing a Task in memory."""

    def __init__(self, task_id: int, title: str, done: bool = False) -> None:
        self.id = task_id
        self.title = title
        self.done = done

    def to_dict(self) -> Dict[str, Any]:
        """Convert model instance to a dictionary representation."""
        return {
            "id": self.id,
            "title": self.title,
            "done": self.done,
        }
