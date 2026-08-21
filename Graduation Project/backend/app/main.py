import sys
from pathlib import Path
from contextlib import asynccontextmanager
from typing import Dict

# Ensure the backend directory is in sys.path when running this file directly
backend_dir = str(Path(__file__).resolve().parent.parent)
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.api.routes import prediction
from app.services.inference import inference_service
from app.utils.logging_config import logger


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifespan context manager to handle application startup and shutdown events.
    Loads ML model pipeline on startup once and cleans up resources on shutdown.
    """
    # Startup: Load ML model pipeline
    logger.info(f"Starting {settings.PROJECT_NAME} v{settings.VERSION}...")
    logger.info(f"Loading ML model from: {settings.MODEL_PATH}")

    is_loaded = inference_service.load_model()
    app.state.model = inference_service.model

    if is_loaded:
        logger.info("ML model pipeline ready for inference.")
    else:
        logger.warning("Operating in fallback estimation mode.")

    yield

    # Shutdown: Clean up resources
    logger.info(f"Shutting down {settings.PROJECT_NAME}...")
    app.state.model = None


# Initialize FastAPI application
app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    lifespan=lifespan,
)

# CORS middleware configuration allowing frontend origin (http://localhost:5173)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount API routers (both at /api/v1 prefix and root level)
app.include_router(prediction.router, prefix=settings.API_V1_STR)
app.include_router(prediction.router)


@app.get("/health", tags=["Health"])
def health_check() -> Dict[str, str]:
    """Root health check endpoint returning standard status ok."""
    return {"status": "ok"}


@app.get("/", tags=["Root"])
def root():
    """Root endpoint providing API information and documentation links."""
    return {
        "message": f"Welcome to {settings.PROJECT_NAME}",
        "docs": "/docs",
        "redoc": "/redoc",
        "api_v1": settings.API_V1_STR,
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)



