"""
SQLModel database models for the Task API.
"""
from typing import Optional, Dict, Any
from sqlmodel import SQLModel, Field


class Task(SQLModel, table=True):
    """
    SQLModel representation of the 'tasks' table in SQLite.
    """
    __tablename__ = "tasks"

    id: Optional[int] = Field(default=None, primary_key=True)
    title: str = Field(nullable=False)
    done: bool = Field(default=False, nullable=False)

    def to_dict(self) -> Dict[str, Any]:
        """Convert model instance to dictionary representation."""
        return {
            "id": self.id,
            "title": self.title,
            "done": self.done,
        }
