"""
SERP Document Management Module

Document and file management system.
"""

from serp_core.plugins.types import ModuleInfo

from serp_dm.config import DMSettings

__version__ = "0.1.0"

MODULE_INFO = ModuleInfo(
    name="dm",
    version=__version__,
    display_name="Document Management",
    description="Document and file management system with folders and metadata",
    author="SERP Team",
    dependencies=["serp-core>=1.0.0", "serp-resources>=0.1.0"],
    entry_points={
        "api": "serp_dm.interfaces.api.routes:load_api_routes",
        "ui": "serp_dm.ui:load_ui_config",
    },
)

__all__ = [
    "DMSettings",
    "MODULE_INFO",
]
