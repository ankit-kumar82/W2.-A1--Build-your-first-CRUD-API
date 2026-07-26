# FlyRank Backend Internship Week 3 Assignment - FastAPI CRUD API with SQLite & SQLModel

A clean, robust, and fully documented RESTful CRUD API built with Python 3.10+, FastAPI, and SQLite using **SQLModel**. Converted from in-memory storage to persistent SQLite database storage while keeping the API endpoints, payloads, response schemas, and status codes exactly identical to Week 2.

---

## Features

- **FastAPI Framework**: High-performance, modern REST API.
- **SQLite Database Persistence**: Database stored locally in `tasks.db`.
- **SQLModel ORM**: Combines SQLAlchemy power with Pydantic type safety for database operations.
- **Automatic Schema Initialization & Seeding**: Table creation and 3 sample tasks seeded automatically on app startup if empty.
- **Pydantic Request Validation**: Strict payload validation with custom HTTP 400 error formatting for missing/empty titles.
- **Full CRUD Operations**:
  - `GET /tasks` - List all tasks from SQLite database with status filtering (`?done=true`) and case-insensitive search (`?search=query`).
  - `GET /tasks/{id}` - Fetch single task by ID or return `404 Task not found`.
  - `POST /tasks` - Insert new task in database (auto-assigned primary key ID, `done=false`, title validation).
  - `PUT /tasks/{id}` - Update title and/or completion status in database.
  - `DELETE /tasks/{id}` - Delete task from database (returns `204 No Content`).
- **Bonus Operations**:
  - `GET /stats` - Summary of total, completed, and open tasks from database.
  - `POST /reset` - Clear database table and re-seed the 3 initial sample tasks.
- **Interactive OpenAPI Docs**: Complete Swagger UI documentation available at `/docs`.

---

## Project Structure

```text
todo-api/
│
├── app/
│   ├── __init__.py    # Application package initialization
│   ├── database.py    # SQLite engine, session manager & init_db seeding [NEW]
│   ├── main.py        # FastAPI app, lifespan handler & exception handling
│   ├── models.py      # SQLModel table definition for tasks
│   ├── schemas.py     # Pydantic schemas for request validation & response serialization
│   ├── routes.py      # API endpoint handlers
│   ├── data.py        # SQLite database CRUD operations using SQLModel
│   └── utils.py       # Task filtering, search, and statistics calculation helpers
│
├── tasks.db           # SQLite database file (created automatically) [NEW]
├── requirements.txt   # Project dependencies (FastAPI, Uvicorn, Pydantic, SQLModel)
├── README.md          # Complete project documentation
├── .gitignore         # Git ignore rules
└── LICENSE            # License file (MIT)
```

---

## SQLite Database Specification

- **Database File**: `tasks.db` (located at project root)
- **Table Name**: `tasks`
- **Columns**:
  - `id` (INTEGER, Primary Key, Auto-increment)
  - `title` (TEXT, Not Null)
  - `done` (BOOLEAN, Not Null, Default `False`)
- **Initial Seed Dataset**:
  1. `{"id": 1, "title": "Learn FastAPI", "done": false}`
  2. `{"id": 2, "title": "Complete Assignment", "done": false}`
  3. `{"id": 3, "title": "Push to GitHub", "done": true}`

---

## Explanation of Modified & Created Files

| File Path | Action | Rationale / Explanation |
| :--- | :--- | :--- |
| [`requirements.txt`](file:///c:/Users/ankit/OneDrive/Desktop/Build%20your%20first%20CRUD%20API/todo-api/requirements.txt) | Modified | Added `sqlmodel>=0.0.14` dependency for database ORM operations. |
| [`app/database.py`](file:///c:/Users/ankit/OneDrive/Desktop/Build%20your%20first%20CRUD%20API/todo-api/app/database.py) | **Created** | Sets up the SQLite database engine pointing to `tasks.db`, configures session management (`get_session`), and implements `init_db()` to automatically create tables and seed 3 initial sample tasks if the `tasks` table is empty. |
| [`app/models.py`](file:///c:/Users/ankit/OneDrive/Desktop/Build%20your%20first%20CRUD%20API/todo-api/app/models.py) | Modified | Converted in-memory `TaskModel` class into a `SQLModel` table class (`Task`) mapping directly to the `tasks` table in SQLite. |
| [`app/schemas.py`](file:///c:/Users/ankit/OneDrive/Desktop/Build%20your%20first%20CRUD%20API/todo-api/app/schemas.py) | Modified | Added `model_config = ConfigDict(from_attributes=True)` to the `Task` Pydantic schema so SQLModel database instances can be serialized seamlessly into API JSON responses. |
| [`app/data.py`](file:///c:/Users/ankit/OneDrive/Desktop/Build%20your%20first%20CRUD%20API/todo-api/app/data.py) | Modified | Replaced all in-memory list operations (`tasks_db`) with SQLModel `Session(engine)` database queries (`select`, `insert`, `update`, `delete`, `reset`). |
| [`app/utils.py`](file:///c:/Users/ankit/OneDrive/Desktop/Build%20your%20first%20CRUD%20API/todo-api/app/utils.py) | Modified | Updated task filtering and analytics calculation utilities to support attribute access (`.done`, `.title`) on SQLModel task instances. |
| [`app/routes.py`](file:///c:/Users/ankit/OneDrive/Desktop/Build%20your%20first%20CRUD%20API/todo-api/app/routes.py) | Modified | Connected all endpoint routes to the updated database data access functions in `app/data.py`. |
| [`app/main.py`](file:///c:/Users/ankit/OneDrive/Desktop/Build%20your%20first%20CRUD%20API/todo-api/app/main.py) | Modified | Integrated FastAPI `lifespan` context manager to trigger `init_db()` automatically when the server starts up. |

---

## Complete Code for Updated Files

### 1. `requirements.txt`
```text
fastapi>=0.100.0
uvicorn>=0.23.0
pydantic>=2.0.0
sqlmodel>=0.0.14
```

### 2. `app/database.py`
```python
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
    from app.models import Task  # Register models with SQLModel.metadata

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
```

### 3. `app/models.py`
```python
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
```

### 4. `app/schemas.py`
```python
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
```

### 5. `app/data.py`
```python
"""
SQLite database CRUD operations for the Task API using SQLModel.
"""
from typing import List, Dict, Any, Optional
from sqlmodel import Session, select, delete

from app.database import engine
from app.models import Task

INITIAL_TASKS: List[Dict[str, Any]] = [
    {"id": 1, "title": "Learn FastAPI", "done": False},
    {"id": 2, "title": "Complete Assignment", "done": False},
    {"id": 3, "title": "Push to GitHub", "done": True},
]


def get_all_tasks(done: Optional[bool] = None, search: Optional[str] = None) -> List[Task]:
    """Retrieve tasks from SQLite database with optional status filter and search query."""
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
```

### 6. `app/utils.py`
```python
"""
Utility functions for filtering, searching, and analytics.
"""
from typing import List, Dict, Any, Optional, Union
from app.models import Task


def filter_and_search_tasks(
    tasks: List[Union[Task, Dict[str, Any]]],
    done: Optional[bool] = None,
    search: Optional[str] = None,
) -> List[Union[Task, Dict[str, Any]]]:
    """Filter tasks by completion status and/or search term matching the title."""
    results = tasks

    if done is not None:
        results = [
            t for t in results
            if (t.done if isinstance(t, Task) else t["done"]) == done
        ]

    if search is not None and search.strip():
        query = search.strip().lower()
        results = [
            t for t in results
            if query in (t.title if isinstance(t, Task) else t["title"]).lower()
        ]

    return results


def calculate_task_stats(tasks: List[Union[Task, Dict[str, Any]]]) -> Dict[str, int]:
    """Calculate totals for total, done, and open tasks."""
    total = len(tasks)
    done_count = sum(
        1 for t in tasks
        if (t.done if isinstance(t, Task) else t["done"])
    )
    open_count = total - done_count

    return {
        "total": total,
        "done": done_count,
        "open": open_count,
    }
```

### 7. `app/routes.py`
```python
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
```

### 8. `app/main.py`
```python
"""
Main FastAPI application entry point with lifespan database initialization.
"""
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.database import init_db
from app.routes import router


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan event handler to initialize database tables and seed sample data on startup."""
    init_db()
    yield


app = FastAPI(
    title="FlyRank Task API",
    description="FastAPI SQLite CRUD API with SQLModel for FlyRank Backend Internship Assignment.",
    version="2.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)


@app.exception_handler(StarletteHTTPException)
async def custom_http_exception_handler(request: Request, exc: StarletteHTTPException):
    """Custom exception handler to format HTTP error responses as required."""
    return JSONResponse(
        status_code=exc.status_code,
        content={"error": exc.detail},
    )


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Custom validation handler to return 400 status with error details for request errors."""
    errors = exc.errors()
    msg = "Invalid body or missing fields"
    if errors:
        first_err = errors[0]
        if "msg" in first_err:
            msg = first_err["msg"]

    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content={"error": msg},
    )


app.include_router(router)
```

---

## Installation & Setup

1. **Navigate to project directory:**
   ```bash
   cd todo-api
   ```

2. **Create virtual environment:**
   ```bash
   python -m venv venv
   ```

3. **Activate virtual environment:**
   - **Windows (PowerShell):**
     ```powershell
     .\venv\Scripts\Activate.ps1
     ```
   - **Windows (CMD):**
     ```cmd
     .\venv\Scripts\activate.bat
     ```
   - **macOS / Linux:**
     ```bash
     source venv/bin/activate
     ```

4. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

---

## Run Command

Start the server locally using Uvicorn:

```bash
uvicorn app.main:app --reload
```

The application server starts at: `http://127.0.0.1:8000`

On server startup, `tasks.db` will be created automatically in the project root if it does not exist, and 3 initial sample tasks will be seeded into the `tasks` table.

---

## Steps to Test using Swagger UI (`/docs`)

1. Open your browser and navigate to **[http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)**.
2. **`GET /tasks`**:
   - Expand `GET /tasks` -> click **Try it out** -> click **Execute**.
   - Verify status `200 OK` and response body containing the 3 initial sample tasks (`id`: 1, 2, 3).
3. **`GET /tasks?done=true`**:
   - Set parameter `done` = `true` -> click **Execute**.
   - Verify only completed tasks (`done: true`) are returned.
4. **`GET /tasks?search=fastapi`**:
   - Set parameter `search` = `fastapi` -> click **Execute**.
   - Verify task matching "Learn FastAPI" is returned.
5. **`GET /tasks/{id}`**:
   - Set `id` = `1` -> click **Execute** -> returns `200 OK` with task details.
   - Set `id` = `999` -> click **Execute** -> returns `404 Not Found` with `{"error": "Task not found"}`.
6. **`POST /tasks`**:
   - Expand `POST /tasks` -> click **Try it out**.
   - Request body: `{"title": "Build SQLite persistence"}`.
   - Click **Execute** -> returns `201 Created` with new ID (`4`).
   - Test invalid request: payload `{"title": "   "}` -> returns `400 Bad Request` with `{"error": "Value error, Title cannot be missing or empty"}`.
7. **`PUT /tasks/{id}`**:
   - Set `id` = `4`, Request body: `{"title": "Build SQLite persistence layer", "done": true}`.
   - Click **Execute** -> returns `200 OK` with updated fields.
8. **`DELETE /tasks/{id}`**:
   - Set `id` = `4` -> click **Execute** -> returns `204 No Content`.
   - Call `GET /tasks/4` again -> returns `404 Not Found`.
9. **`GET /stats`**:
   - Click **Execute** -> returns `200 OK` with statistical totals (`total`, `done`, `open`).
10. **`POST /reset`**:
    - Click **Execute** -> resets SQLite table and returns the 3 initial seed tasks.

---

## API Endpoint Reference Table

| Method | Endpoint | Status Code | Description |
| :--- | :--- | :--- | :--- |
| `GET` | `/` | `200 OK` | API details and metadata |
| `GET` | `/health` | `200 OK` | Server health status check |
| `GET` | `/stats` | `200 OK` | Summary totals from SQLite database |
| `POST` | `/reset` | `200 OK` | Reset SQLite tasks table to initial seed dataset |
| `GET` | `/tasks` | `200 OK` | Get all tasks (supports `done` & `search` query params) |
| `GET` | `/tasks/{id}` | `200 OK` / `404` | Get task by ID |
| `POST` | `/tasks` | `201 Created` / `400` | Create new task in SQLite database |
| `PUT` | `/tasks/{id}` | `200 OK` / `400` / `404` | Update task title and/or done status |
| `DELETE` | `/tasks/{id}` | `204 No Content` / `404` | Delete task by ID |

---

You can add this section to your **README.md**.

## Interactive API Documentation

### Swagger UI

Swagger UI provides an interactive interface to explore and test all API endpoints directly from your browser.

**Local:**

```text
http://127.0.0.1:8000/docs
```

**Live Deployment:**

```text
https://w2-a1-build-your-first-crud-api-2.onrender.com/docs
```

Features:

* Interactive API testing
* Request and response examples
* Automatic schema documentation
* Execute API requests without Postman

---

### ReDoc

ReDoc provides clean, readable API documentation generated from the OpenAPI specification.

**Local:**

```text
http://127.0.0.1:8000/redoc
```

**Live Deployment:**

```text
https://w2-a1-build-your-first-crud-api-2.onrender.com/redoc
```

Features:

* Professional API documentation
* Endpoint descriptions
* Request and response models
* Parameter details
* Error response documentation

---

## Live API

**Base URL**

```text
https://w2-a1-build-your-first-crud-api-2.onrender.com
```

### Available Endpoints

| Method | Endpoint      | Description        |
| ------ | ------------- | ------------------ |
| GET    | `/`           | API metadata       |
| GET    | `/tasks`      | Get all tasks      |
| GET    | `/tasks/{id}` | Get task by ID     |
| POST   | `/tasks`      | Create a new task  |
| PUT    | `/tasks/{id}` | Update a task      |
| DELETE | `/tasks/{id}` | Delete a task      |
| GET    | `/stats`      | Task statistics    |
| POST   | `/reset`      | Reset sample tasks |


## API Documentation

| Resource | Link |
|----------|------|
| Live API | https://w2-a1-build-your-first-crud-api-2.onrender.com |
| Swagger UI | https://w2-a1-build-your-first-crud-api-2.onrender.com/docs |
| ReDoc | https://w2-a1-build-your-first-crud-api-2.onrender.com/redoc |
---

## Git Commit History Strategy (Assignment Stages)

To maintain an exact stage-by-stage git commit history for grading:

```bash
# Stage 0: Basic server setup
git init
git add .gitignore LICENSE requirements.txt app/__init__.py app/main.py
git commit -m "Stage 0: hello server"

# Stage 1: Metadata and Health endpoints
git add app/schemas.py app/routes.py
git commit -m "Stage 1: root and health endpoints"

# Stage 2: Read endpoints and 404 handling
git commit -am "Stage 2: read endpoints with 404"

# Stage 3: Task creation and Pydantic validation
git commit -am "Stage 3: create with validation"

# Stage 4: Full CRUD capabilities (PUT and DELETE)
git commit -am "Stage 4: full CRUD"

# Stage 5: OpenAPI / Swagger UI documentation
git commit -am "Stage 5: Swagger UI"

# Stage 6: Publish & documentation
git add README.md
git commit -m "Stage 6: publish and docs"

# Week 3 Assignment Stage: SQLite Database Integration
git add app/database.py app/models.py app/schemas.py app/data.py app/utils.py app/routes.py app/main.py requirements.txt README.md
git commit -m "Stage 7: Convert in-memory store to SQLite with SQLModel persistence"
```
