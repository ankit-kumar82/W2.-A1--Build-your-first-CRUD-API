"""
PostgreSQL and SQLite database configuration, engine setup, and initial dataset seeding.
"""
import os
import socket
import time
from typing import Generator
from dotenv import load_dotenv
from sqlmodel import SQLModel, create_engine, Session, select

# Load environment variables from .env file
load_dotenv()


def get_db_url() -> str:
    """Retrieve active database URL with fallback for local host execution outside Docker."""
    url = os.getenv(
        "DATABASE_URL",
        "postgresql://postgres:postgres@db:5432/tasks_db"
    )

    # Check if host 'db' is resolvable (Docker Compose network)
    if "@db:" in url or "//db:" in url:
        try:
            socket.gethostbyname("db")
        except socket.gaierror:
            # Fallback to local SQLite database when running outside Docker container
            BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            DATABASE_PATH = os.path.join(BASE_DIR, "tasks.db")
            return f"sqlite:///{DATABASE_PATH}"

    return url


DATABASE_URL = get_db_url()


def create_db_engine(url: str):
    """Create SQLModel database engine based on URL scheme."""
    if url.startswith("sqlite"):
        return create_engine(url, echo=False, connect_args={"check_same_thread": False})
    return create_engine(url, echo=False, pool_pre_ping=True)


engine = create_db_engine(DATABASE_URL)


def get_session() -> Generator[Session, None, None]:
    """Yield a database session for request handling."""
    with Session(engine) as session:
        yield session


def init_db(max_retries: int = 10, delay: int = 2) -> None:
    """Initialize database tables and seed initial sample tasks if empty with retries."""
    # Import models to ensure they are registered with SQLModel.metadata
    from app.models import Task  # noqa: F401

    for attempt in range(max_retries):
        try:
            SQLModel.metadata.create_all(engine)
            seed_initial_data()
            break
        except Exception as e:
            if attempt < max_retries - 1:
                time.sleep(delay)
            else:
                raise e


def seed_initial_data() -> None:
    """Insert three initial sample tasks if the tasks table is empty."""
    from app.models import Task

    with Session(engine) as session:
        statement = select(Task)
        existing_task = session.exec(statement).first()
        if existing_task is None:
            sample_tasks = [
                Task(title="Learn FastAPI", done=False),
                Task(title="Complete Assignment", done=False),
                Task(title="Push to GitHub", done=True),
            ]
            session.add_all(sample_tasks)
            session.commit()



