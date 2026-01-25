"""API package __init__.py"""

from serp_dm.interfaces.api.routes import load_api_routes, router

__all__ = ["load_api_routes", "router"]
