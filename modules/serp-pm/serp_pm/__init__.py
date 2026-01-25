"""
SERP Project Management Core Module

Foundational project management providing base entities for methodology extensions.
"""

from serp_core.plugins.types import ModuleInfo

from serp_pm.config import PMSettings

__version__ = "0.1.0"

MODULE_INFO = ModuleInfo(
    name="pm",
    version=__version__,
    display_name="Project Management",
    description="Core project management module - foundation for methodology extensions",
    author="SERP Team",
    dependencies=["serp-core>=1.0.0", "serp-resources>=0.1.0"],
)

__all__ = [
    "PMSettings",
    "MODULE_INFO",
]
