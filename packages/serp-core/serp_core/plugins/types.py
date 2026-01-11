"""
Plugin type definitions
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Callable, Coroutine, Dict, List, Optional, Union


class HealthStatus(str, Enum):
    """Health status levels for modules and components."""

    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"


@dataclass
class ComponentHealth:
    """Health status of an individual component within a module."""

    name: str
    status: HealthStatus
    message: Optional[str] = None
    response_time_ms: Optional[float] = None


@dataclass
class ModuleHealthReport:
    """
    Complete health report for a module.

    Example:
        report = ModuleHealthReport(
            module_id="serp-crm",
            module_name="CRM Module",
            status=HealthStatus.HEALTHY,
            components=[
                ComponentHealth(name="database", status=HealthStatus.HEALTHY),
                ComponentHealth(name="cache", status=HealthStatus.HEALTHY),
            ]
        )
    """

    module_id: str
    module_name: str
    status: HealthStatus
    version: str = "1.0.0"
    components: List[ComponentHealth] = field(default_factory=list)
    message: Optional[str] = None
    checked_at: datetime = field(default_factory=datetime.utcnow)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            "module_id": self.module_id,
            "module_name": self.module_name,
            "status": self.status.value,
            "version": self.version,
            "components": [
                {
                    "name": c.name,
                    "status": c.status.value,
                    "message": c.message,
                    "response_time_ms": c.response_time_ms,
                }
                for c in self.components
            ],
            "message": self.message,
            "checked_at": self.checked_at.isoformat(),
        }


# Type alias for health check functions
HealthCheckFunc = Callable[[], Coroutine[Any, Any, ModuleHealthReport]]


@dataclass
class ModuleInfo:
    """
    Module metadata exported by each SERP module.

    Every module must export a MODULE_INFO instance in its __init__.py:

    Example:
        # In serp_users/__init__.py
        from serp_core.plugins import ModuleInfo

        MODULE_INFO = ModuleInfo(
            name="serp-users",
            version="1.0.0",
            display_name="User Management",
            description="User authentication and management",
            author="SimpleERP Team",
            dependencies=["serp-core>=1.0.0"],
            entry_points={
                "api": "serp_users.Interfaces.API:load_api_routes",
                "ui": "serp_users.UI:registry",
                "permissions": "serp_users.Interfaces.Permissions:permissions",
            }
        )
    """

    name: str
    version: str
    display_name: str
    description: str = ""
    author: str = ""
    dependencies: List[str] = field(default_factory=list)
    entry_points: Dict[str, str] = field(default_factory=dict)
    config_schema: Optional[Dict[str, Any]] = None
    enabled: bool = True


@dataclass
class ModuleConfig:
    """
    Runtime configuration for a module.

    Example:
        module_config = ModuleConfig(
            name="serp-users",
            enabled=True,
            settings={
                "password_min_length": 8,
                "session_timeout": 3600,
                "allow_registration": True
            }
        )
    """

    name: str
    enabled: bool = True
    settings: Dict[str, Any] = field(default_factory=dict)
