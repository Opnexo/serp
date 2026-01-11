"""
Plugin system for module discovery and loading
"""

from serp_core.plugins.discovery import discover_health_checks, discover_modules
from serp_core.plugins.health import HealthCheckBuilder, create_simple_health_check
from serp_core.plugins.loader import ModuleLoader
from serp_core.plugins.registry import ModuleRegistry, get_module_registry
from serp_core.plugins.types import (
    ComponentHealth,
    HealthCheckFunc,
    HealthStatus,
    ModuleConfig,
    ModuleHealthReport,
    ModuleInfo,
)

__all__ = [
    # Module types
    "ModuleInfo",
    "ModuleConfig",
    # Health check types
    "HealthStatus",
    "ComponentHealth",
    "ModuleHealthReport",
    "HealthCheckFunc",
    # Health check utilities
    "HealthCheckBuilder",
    "create_simple_health_check",
    # Discovery and loading
    "discover_modules",
    "discover_health_checks",
    "ModuleRegistry",
    "get_module_registry",
    "ModuleLoader",
]
