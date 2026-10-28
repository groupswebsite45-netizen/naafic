from fastapi import FastAPI
from app.core.config import settings
from app.core.database import Base, engine
from app.api.v1.api import api_v1_router
from app.middleware.cors import setup_cors
from app.middleware.error_handler import setup_exception_handlers
from app.utils.logger import logger


def create_application() -> FastAPI:
    """Initialize FastAPI application with routes and middleware."""
    app = FastAPI(
        title=settings.APP_NAME,
        version="1.0.0-foundation",
        description="RESTful API Backend for Education Management System",
        docs_url="/docs" if settings.DEBUG else None,
        redoc_url="/redoc" if settings.DEBUG else None,
    )

    # Setup CORS middleware
    setup_cors(app)

    # Setup uniform error handlers
    setup_exception_handlers(app)

    # Include Versioned API Routers
    app.include_router(api_v1_router)

    @app.get("/health", tags=["Health"])
    def root_health():
        return {
            "status": "healthy",
            "app": settings.APP_NAME,
            "version": "1.0.0-foundation",
            "environment": settings.APP_ENV
        }

    return app


app = create_application()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG
    )
