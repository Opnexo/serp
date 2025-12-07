"""
FastAPI application factory
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from serp_shell.api.middleware import setup_middleware
from serp_shell.api.routes import auth, health, module_bundles, ui_config
from serp_shell.startup.bootstrap import bootstrap_application
from serp_shell.startup.config import get_settings


def create_app() -> FastAPI:
    """
    Create and configure the FastAPI application.

    Returns:
        Configured FastAPI application instance
    """
    settings = get_settings()

    app = FastAPI(
        title=settings.app_title,
        description="SimpleERP API",
        version="1.0.0",
        docs_url="/docs",
        redoc_url="/redoc",
        openapi_url="/openapi.json",
    )

    # Setup CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Setup custom middleware
    setup_middleware(app)

    # Register core routes
    app.include_router(health.router, tags=["Health"])
    app.include_router(auth.router, prefix="/api/auth", tags=["Authentication"])
    app.include_router(ui_config.router, prefix="/api", tags=["UI Configuration"])
    app.include_router(module_bundles.router, prefix="/api", tags=["Module Bundles"])

    # Bootstrap modules on startup
    @app.on_event("startup")
    async def startup_event():
        """Bootstrap the application and load modules"""
        await bootstrap_application(app)

    # Global exception handler
    @app.exception_handler(Exception)
    async def global_exception_handler(request, exc):
        return JSONResponse(
            status_code=500,
            content={"detail": "Internal server error", "error": str(exc)},
        )

    return app
