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
    description="FastAPI PostgreSQL CRUD API with SQLModel and Docker for FlyRank Backend Internship Assignment.",
    version="3.0.0",
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
