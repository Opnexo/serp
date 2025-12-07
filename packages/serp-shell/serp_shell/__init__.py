"""
serp-shell: FastAPI application shell for SimpleERP
"""

__version__ = "1.0.0"

from serp_shell.api.app import create_app

__all__ = ["__version__", "create_app"]
