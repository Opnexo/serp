"""
Plugin system for module discovery and loading
"""

from serp_core.plugins.discovery import discover_modules
from serp_core.plugins.loader import ModuleLoader
from serp_core.plugins.registry import ModuleRegistry, get_module_registry
from serp_core.plugins.types import ModuleConfig, ModuleInfo

__all__ = [
    "ModuleInfo",
    "ModuleConfig",
    "discover_modules",
    "ModuleRegistry",
    "get_module_registry",
    "ModuleLoader",
]
