import logging

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.api.routes import documents, health
from app.config.settings import get_settings
from app.utils.errors import AppError

settings = get_settings()

logging.basicConfig(level=settings.log_level)
logger = logging.getLogger("document_summary_assistant")

app = FastAPI(
    title="Document Summary Assistant API",
    version="0.1.0",
    description="Upload a PDF or image, extract its text (with OCR fallback), "
    "and generate an AI-powered summary, key points, main ideas, and "
    "improvement suggestions.",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_allow_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.exception_handler(AppError)
async def app_error_handler(request: Request, exc: AppError) -> JSONResponse:
    return JSONResponse(
        status_code=exc.status_code,
        content={"error": exc.error, "message": exc.message},
    )


@app.exception_handler(RequestValidationError)
async def request_validation_error_handler(
    request: Request, exc: RequestValidationError
) -> JSONResponse:
    # FastAPI's own default shape for a malformed request body is
    # {"detail": [...]}, with no top-level "message" - every other error
    # in this app is {"error", "message"}, and the frontend only knows how
    # to read that shape. Without this handler, a malformed request (e.g.
    # a stray null slipping into a list field) silently degrades to the
    # frontend's generic "Something went wrong" fallback instead of a
    # message that actually explains anything.
    logger.warning(
        "Request validation failed for %s %s: %s", request.method, request.url, exc.errors()
    )
    return JSONResponse(
        status_code=422,
        content={
            "error": "validation_error",
            "message": "The request was missing required information or had an invalid format.",
        },
    )


@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    logger.exception("Unhandled exception while processing %s %s", request.method, request.url)
    return JSONResponse(
        status_code=500,
        content={
            "error": "internal_error",
            "message": "Something went wrong on our end. Please try again.",
        },
    )


app.include_router(health.router, prefix="/api")
app.include_router(documents.router, prefix="/api")
