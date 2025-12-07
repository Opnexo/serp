"""
serp-core: Core foundation for SimpleERP platform

This package provides the foundational building blocks for SERP modules:
- Domain-Driven Design patterns
- Plugin system and module discovery
- Authentication and authorization framework
- UI integration types
"""

__version__ = "1.0.0"

from serp_core.plugins import ModuleInfo

# Module information for serp-core itself
MODULE_INFO = ModuleInfo(
    name="serp-core",
    version=__version__,
    display_name="SERP Core",
    description="Core foundation for SimpleERP platform",
    author="SimpleERP Team",
    dependencies=[],
    entry_points={},
)

__all__ = ["__version__", "MODULE_INFO"]
