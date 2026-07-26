# FlyRank Backend Internship Assignment A3 - Task CRUD API with PostgreSQL & Docker Compose

A clean, robust, and production-ready RESTful CRUD API built with Python 3.11+, FastAPI, SQLModel, and PostgreSQL running inside Docker. Upgraded from SQLite to containerized PostgreSQL persistence using Docker Compose while maintaining full backward compatibility with all API endpoints, schemas, status codes, and request/response payloads.

---

## Repository
- **GitHub Repository**: [https://github.com/ankit-kumar82/flyrank-backend-A3-task-api-postgres-docker](https://github.com/ankit-kumar82/flyrank-backend-A3-task-api-postgres-docker)

---

## Features

- **FastAPI Framework**: High-performance RESTful API with automated Pydantic request validation.
- **PostgreSQL Database**: Persistent PostgreSQL relational database running inside a Docker container.
- **SQLModel ORM**: Combines SQLAlchemy power with Pydantic type safety for database operations.
- **Environment Configuration**: Dynamic database connection string management via `.env` file (`python-dotenv`).
- **Containerized Architecture**: Dockerized FastAPI service paired with PostgreSQL via `compose.yaml`.
- **Data Persistence**: Named Docker volume (`postgres_data`) preserving database state across container restarts.
- **Automatic Schema Initialization & Seeding**: Table creation and 3 sample tasks seeded automatically on app startup if empty.
- **Full CRUD Operations**:
  - `GET /tasks` - List all tasks from PostgreSQL database with status filtering (`?done=true`) and case-insensitive search (`?search=query`).
  - `GET /tasks/{id}` - Fetch single task by ID or return `404 Task not found`.
  - `POST /tasks` - Insert new task in database (auto-incrementing primary key ID, `done=false`, title validation).
  - `PUT /tasks/{id}` - Update title and/or completion status in database.
  - `DELETE /tasks/{id}` - Delete task from database (returns `204 No Content`).
- **Bonus Operations**:
  - `GET /stats` - Summary of total, completed, and open tasks from database.
  - `POST /reset` - Clear database table and re-seed the 3 initial sample tasks.
- **Interactive Documentation**:
  - **Swagger UI**: [http://localhost:8000/docs](http://localhost:8000/docs)
  - **ReDoc UI**: [http://localhost:8000/redoc](http://localhost:8000/redoc)

---

## Project Structure

```text
todo-api/
│
├── app/
│   ├── __init__.py    # Application package initialization
│   ├── database.py    # PostgreSQL connection engine, dotenv & init_db retries
│   ├── main.py        # FastAPI app entry point, lifespan handler & exception handling
│   ├── models.py      # SQLModel table definition for tasks
│   ├── schemas.py     # Pydantic schemas for request validation & response serialization
│   ├── routes.py      # API endpoint handlers
│   ├── data.py        # PostgreSQL database CRUD operations using SQLModel
│   └── utils.py       # Task filtering, search, and statistics helpers
│
├── Dockerfile         # Multi-stage Docker build file for FastAPI application
├── compose.yaml       # Docker Compose configuration for API and PostgreSQL services
├── .env               # Active environment variables file
├── .env.example       # Template environment variables file
├── requirements.txt   # Project dependencies (FastAPI, Uvicorn, Pydantic, SQLModel, psycopg2-binary, python-dotenv)
├── README.md          # Complete project documentation
├── .gitignore         # Git ignore rules
└── LICENSE            # License file (MIT)
```

---

## Environment Variables Configuration

Environment variables are loaded dynamically using `python-dotenv`. A template `.env.example` file is provided in the repository.

```env
DATABASE_URL=postgresql://postgres:postgres@db:5432/tasks_db
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres
POSTGRES_DB=tasks_db
```

- `DATABASE_URL`: Connection string used by SQLModel engine (`db` refers to the PostgreSQL container service name in Docker Compose).
- `POSTGRES_USER`: Database superuser username.
- `POSTGRES_PASSWORD`: Database superuser password.
- `POSTGRES_DB`: Default database created on PostgreSQL startup.

---

## How to Build and Run with Docker Compose

Running the API and PostgreSQL database together requires only a single command:

1. **Clone/Navigate to the repository directory:**
   ```bash
   cd todo-api
   ```

2. **Start containers using Docker Compose:**
   ```bash
   docker compose up --build
   ```

   This command will:
   - Build the FastAPI container image using `Dockerfile`.
   - Pull the official `postgres:15-alpine` image.
   - Start the PostgreSQL service (`db`) with persistent volume mounting.
   - Wait for PostgreSQL healthcheck to pass.
   - Start the FastAPI service (`api`) on `http://localhost:8000`.
   - Run `init_db()` on startup to create the `tasks` table and seed 3 sample tasks automatically.

3. **Stop containers:**
   ```bash
   docker compose down
   ```

4. **Stop containers and clear database volume (Reset DB):**
   ```bash
   docker compose down -v
   ```

---

## API Endpoint Reference Table

| Method | Endpoint | Status Code | Description |
| :--- | :--- | :--- | :--- |
| `GET` | `/` | `200 OK` | API details and metadata |
| `GET` | `/health` | `200 OK` | Server health status check |
| `GET` | `/stats` | `200 OK` | Task summary totals from PostgreSQL |
| `POST` | `/reset` | `200 OK` | Reset tasks table to 3 initial seed tasks |
| `GET` | `/tasks` | `200 OK` | Get all tasks (supports `done` & `search` query params) |
| `GET` | `/tasks/{id}` | `200 OK` / `404` | Get task by ID |
| `POST` | `/tasks` | `201 Created` / `400` | Create new task in PostgreSQL database |
| `PUT` | `/tasks/{id}` | `200 OK` / `400` / `404` | Update task title and/or done status |
| `DELETE` | `/tasks/{id}` | `204 No Content` / `404` | Delete task by ID |

---

## Interactive Documentation URLs

- **Swagger UI**: [http://localhost:8000/docs](http://localhost:8000/docs)
- **ReDoc UI**: [http://localhost:8000/redoc](http://localhost:8000/redoc)

---

## Commands to Test the API

You can test all endpoints using `curl` commands:

1. **API Metadata (`GET /`)**:
   ```bash
   curl -X GET http://localhost:8000/
   ```

2. **Health Check (`GET /health`)**:
   ```bash
   curl -X GET http://localhost:8000/health
   ```

3. **Get All Tasks (`GET /tasks`)**:
   ```bash
   curl -X GET http://localhost:8000/tasks
   ```

4. **Filter Tasks by Completion (`GET /tasks?done=true`)**:
   ```bash
   curl -X GET "http://localhost:8000/tasks?done=true"
   ```

5. **Search Tasks by Keyword (`GET /tasks?search=FastAPI`)**:
   ```bash
   curl -X GET "http://localhost:8000/tasks?search=FastAPI"
   ```

6. **Get Task by ID (`GET /tasks/1`)**:
   ```bash
   curl -X GET http://localhost:8000/tasks/1
   ```

7. **Create Task (`POST /tasks`)**:
   ```bash
   curl -X POST http://localhost:8000/tasks \
     -H "Content-Type: application/json" \
     -d '{"title": "Deploy PostgreSQL with Docker Compose"}'
   ```

8. **Update Task (`PUT /tasks/1`)**:
   ```bash
   curl -X PUT http://localhost:8000/tasks/1 \
     -H "Content-Type: application/json" \
     -d '{"done": true}'
   ```

9. **Delete Task (`DELETE /tasks/1`)**:
   ```bash
   curl -X DELETE http://localhost:8000/tasks/1
   ```

10. **Get Task Statistics (`GET /stats`)**:
    ```bash
    curl -X GET http://localhost:8000/stats
    ```

11. **Reset Database (`POST /reset`)**:
    ```bash
    curl -X POST http://localhost:8000/reset
    ```

---

## File Modification Summary

| File Path | Action | Rationale / Explanation |
| :--- | :--- | :--- |
| [`requirements.txt`](file:///c:/Users/ankit/OneDrive/Desktop/Build%20your%20first%20CRUD%20API/todo-api/requirements.txt) | Modified | Added `psycopg2-binary` (PostgreSQL driver) and `python-dotenv` (environment variables). |
| [`.env.example`](file:///c:/Users/ankit/OneDrive/Desktop/Build%20your%20first%20CRUD%20API/todo-api/.env.example) | **Created** | Template environment variables file containing default PostgreSQL configuration parameters. |
| [`.env`](file:///c:/Users/ankit/OneDrive/Desktop/Build%20your%20first%20CRUD%20API/todo-api/.env) | **Created** | Active environment configuration for database connection. |
| [`app/database.py`](file:///c:/Users/ankit/OneDrive/Desktop/Build%20your%20first%20CRUD%20API/todo-api/app/database.py) | Modified | Replaced SQLite setup with PostgreSQL engine driven by `DATABASE_URL` via `python-dotenv`. Added retries to `init_db()`. |
| [`app/models.py`](file:///c:/Users/ankit/OneDrive/Desktop/Build%20your%20first%20CRUD%20API/todo-api/app/models.py) | Modified | Updated docstrings for PostgreSQL SQLModel database tables. |
| [`app/data.py`](file:///c:/Users/ankit/OneDrive/Desktop/Build%20your%20first%20CRUD%20API/todo-api/app/data.py) | Modified | Updated docstrings and auto-increment seeding logic for PostgreSQL. |
| [`app/routes.py`](file:///c:/Users/ankit/OneDrive/Desktop/Build%20your%20first%20CRUD%20API/todo-api/app/routes.py) | Modified | Updated docstrings to reference PostgreSQL database. |
| [`app/main.py`](file:///c:/Users/ankit/OneDrive/Desktop/Build%20your%20first%20CRUD%20API/todo-api/app/main.py) | Modified | Updated OpenAPI documentation metadata. |
| [`Dockerfile`](file:///c:/Users/ankit/OneDrive/Desktop/Build%20your%20first%20CRUD%20API/todo-api/Dockerfile) | **Created** | Container build file for FastAPI application using `python:3.11-slim`. |
| [`compose.yaml`](file:///c:/Users/ankit/OneDrive/Desktop/Build%20your%20first%20CRUD%20API/todo-api/compose.yaml) | **Created** | Docker Compose orchestration file defining `api` and `db` services with volume persistence. |
| [`README.md`](file:///c:/Users/ankit/OneDrive/Desktop/Build%20your%20first%20CRUD%20API/todo-api/README.md) | Modified | Comprehensive updated project documentation. |

---

## Git Commit History Strategy

```bash
# Stage 8: Upgrade Task CRUD API to PostgreSQL with Docker and Docker Compose
git add .env.example compose.yaml Dockerfile requirements.txt app/database.py app/models.py app/data.py app/routes.py app/main.py README.md
git commit -m "Stage 8: Upgrade Task CRUD API to PostgreSQL with Docker and Docker Compose"
```
