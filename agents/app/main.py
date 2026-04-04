from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import uvicorn

from app.config import settings
from app.utils.logger import setup_logging, logger
from app.api.v1.router import api_router


# Setup logging
setup_logging()


def create_application() -> FastAPI:
    """Application factory"""
    
    application = FastAPI(
        title=settings.api_title,
        version=settings.api_version,
        description="Production-ready multi-agent backend for incident response compliance analysis",
        docs_url="/docs" if settings.environment == "development" else None,
        redoc_url="/redoc" if settings.environment == "development" else None,
    )
    
    # CORS middleware
    application.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins_list,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    # Include routers
    application.include_router(api_router, prefix="/api/v1")
    
    # Root health endpoint
    @application.get("/health")
    async def health_check():
        """Root health check endpoint"""
        return {
            "status": "healthy",
            "service": "playbook-pulse-agents",
            "version": settings.api_version,
            "environment": settings.environment
        }
    
    # Global exception handler
    @application.exception_handler(Exception)
    async def global_exception_handler(request, exc):
        logger.error(f"Unhandled exception: {exc}", exc_info=True)
        return JSONResponse(
            status_code=500,
            content={
                "error": "Internal server error",
                "message": str(exc) if settings.environment == "development" else "An error occurred"
            }
        )
    
    # Startup event
    @application.on_event("startup")
    async def startup_event():
        logger.info(f"Starting PlaybookPulse Agents API v{settings.api_version}")
        logger.info(f"Environment: {settings.environment}")
        logger.info(f"Anthropic API configured: {bool(settings.anthropic_api_key)}")
    
    # Shutdown event
    @application.on_event("shutdown")
    async def shutdown_event():
        logger.info("Shutting down PlaybookPulse Agents API")
    
    return application


# Create app instance
app = create_application()


def main():
    """Entry point for running the application"""
    uvicorn.run(
        "app.main:app",
        host=settings.api_host,
        port=settings.api_port,
        reload=settings.environment == "development",
        log_level=settings.log_level.lower(),
    )


if __name__ == "__main__":
    main()
