"""
Main FastAPI application entry point.
"""
from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.routes import router

app = FastAPI(
    title="FlyRank Task API",
    description="FastAPI In-Memory CRUD API for FlyRank Backend Internship Assignment.",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
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
    # Check if error is due to missing or empty title
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
