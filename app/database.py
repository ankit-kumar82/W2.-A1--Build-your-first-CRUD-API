"""
SQLite database configuration, engine setup, and initial dataset seeding.
"""
import os
from typing import Generator
from sqlmodel import SQLModel, create_engine, Session, select

# Absolute path to tasks.db in the project root directory
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATABASE_PATH = os.path.join(BASE_DIR, "tasks.db")
DATABASE_URL = f"sqlite:///{DATABASE_PATH}"

# Create SQLite database engine with multi-thread check disabled for FastAPI
engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False},
)


def get_session() -> Generator[Session, None, None]:
    """Yield a database session for request handling."""
    with Session(engine) as session:
        yield session


def init_db() -> None:
    """Initialize database tables and seed initial sample tasks if empty."""
    # Import models to ensure they are registered with SQLModel.metadata
    from app.models import Task  # noqa: F401

    SQLModel.metadata.create_all(engine)
    seed_initial_data()


def seed_initial_data() -> None:
    """Insert three initial sample tasks if the tasks table is empty."""
    from app.models import Task

    with Session(engine) as session:
        statement = select(Task)
        existing_tasks = session.exec(statement).first()
        if existing_tasks is None:
            sample_tasks = [
                Task(id=1, title="Learn FastAPI", done=False),
                Task(id=2, title="Complete Assignment", done=False),
                Task(id=3, title="Push to GitHub", done=True),
            ]
            session.add_all(sample_tasks)
            session.commit()
