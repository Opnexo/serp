"""
API interface for serp-common module.
"""


def load_api_routes():
    """Load API routes for common module."""
    from serp_common.interfaces.api.routes import router

    return router
