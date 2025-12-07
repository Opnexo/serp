"""
Custom middleware for the application
"""

import logging
import time

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from serp_core.exceptions import (
    ApplicationError,
    AuthenticationError,
    DomainError,
)

logger = logging.getLogger(__name__)


def setup_middleware(app: FastAPI) -> None:
    """Setup all middleware for the application"""

    @app.middleware("http")
    async def log_requests(request: Request, call_next):
        """Log all HTTP requests"""
        start_time = time.time()

        response = await call_next(request)

        process_time = time.time() - start_time
        logger.info(
            f"{request.method} {request.url.path} "
            f"completed in {process_time:.3f}s with status {response.status_code}"
        )

        return response

    @app.middleware("http")
    async def handle_exceptions(request: Request, call_next):
        """Handle domain and application exceptions"""
        try:
            return await call_next(request)
        except AuthenticationError as e:
            return JSONResponse(
                status_code=401, content={"detail": str(e), "type": "auth_error"}
            )
        except DomainError as e:
            return JSONResponse(
                status_code=400, content={"detail": str(e), "type": "domain_error"}
            )
        except ApplicationError as e:
            return JSONResponse(
                status_code=400,
                content={"detail": str(e), "type": "application_error"},
            )
        except Exception:
            logger.exception("Unhandled exception")
            return JSONResponse(
                status_code=500,
                content={"detail": "Internal server error", "type": "server_error"},
            )
