"""
Health check utilities for SERP modules.

Provides helper functions and a base class for implementing
module health checks.
"""

import time
from abc import ABC, abstractmethod
from typing import Any, Callable, Coroutine, List, Optional

from serp_core.plugins.types import (
    ComponentHealth,
    HealthStatus,
    ModuleHealthReport,
)


class HealthCheckBuilder:
    """
    Builder for creating ModuleHealthReport with component checks.

    Example:
        async def health_check() -> ModuleHealthReport:
            builder = HealthCheckBuilder("serp-crm", "CRM Module", "1.0.0")

            # Add database check
            await builder.add_async_check(
                "database",
                check_database_connection
            )

            # Add cache check
            await builder.add_async_check(
                "redis",
                check_redis_connection
            )

            return builder.build()
    """

    def __init__(self, module_id: str, module_name: str, version: str = "1.0.0"):
        self.module_id = module_id
        self.module_name = module_name
        self.version = version
        self.components: List[ComponentHealth] = []
        self._overall_status = HealthStatus.HEALTHY

    def add_component(self, component: ComponentHealth) -> "HealthCheckBuilder":
        """Add a pre-built component health check."""
        self.components.append(component)
        self._update_overall_status(component.status)
        return self

    async def add_async_check(
        self,
        name: str,
        check_func: Callable[[], Coroutine[Any, Any, bool]],
        critical: bool = True,
    ) -> "HealthCheckBuilder":
        """
        Add an async health check function.

        Args:
            name: Component name (e.g., "database", "cache")
            check_func: Async function that returns True if healthy
            critical: If True, failure sets overall status to UNHEALTHY;
                      if False, sets to DEGRADED
        """
        start_time = time.perf_counter()
        try:
            is_healthy = await check_func()
            response_time = (time.perf_counter() - start_time) * 1000

            if is_healthy:
                status = HealthStatus.HEALTHY
                message = None
            else:
                status = HealthStatus.UNHEALTHY if critical else HealthStatus.DEGRADED
                message = f"{name} check returned unhealthy"

        except Exception as e:
            response_time = (time.perf_counter() - start_time) * 1000
            status = HealthStatus.UNHEALTHY if critical else HealthStatus.DEGRADED
            message = str(e)

        component = ComponentHealth(
            name=name,
            status=status,
            message=message,
            response_time_ms=round(response_time, 2),
        )
        self.components.append(component)
        self._update_overall_status(status)
        return self

    def add_sync_check(
        self,
        name: str,
        check_func: Callable[[], bool],
        critical: bool = True,
    ) -> "HealthCheckBuilder":
        """
        Add a synchronous health check function.

        Args:
            name: Component name
            check_func: Sync function that returns True if healthy
            critical: If True, failure sets overall status to UNHEALTHY
        """
        start_time = time.perf_counter()
        try:
            is_healthy = check_func()
            response_time = (time.perf_counter() - start_time) * 1000

            if is_healthy:
                status = HealthStatus.HEALTHY
                message = None
            else:
                status = HealthStatus.UNHEALTHY if critical else HealthStatus.DEGRADED
                message = f"{name} check returned unhealthy"

        except Exception as e:
            response_time = (time.perf_counter() - start_time) * 1000
            status = HealthStatus.UNHEALTHY if critical else HealthStatus.DEGRADED
            message = str(e)

        component = ComponentHealth(
            name=name,
            status=status,
            message=message,
            response_time_ms=round(response_time, 2),
        )
        self.components.append(component)
        self._update_overall_status(status)
        return self

    def _update_overall_status(self, component_status: HealthStatus) -> None:
        """Update overall status based on component status."""
        if component_status == HealthStatus.UNHEALTHY:
            self._overall_status = HealthStatus.UNHEALTHY
        elif (
            component_status == HealthStatus.DEGRADED
            and self._overall_status == HealthStatus.HEALTHY
        ):
            self._overall_status = HealthStatus.DEGRADED

    def build(self, message: Optional[str] = None) -> ModuleHealthReport:
        """Build the final health report."""
        return ModuleHealthReport(
            module_id=self.module_id,
            module_name=self.module_name,
            status=self._overall_status,
            version=self.version,
            components=self.components,
            message=message,
        )


def create_simple_health_check(
    module_id: str,
    module_name: str,
    version: str = "1.0.0",
) -> Callable[[], Coroutine[Any, Any, ModuleHealthReport]]:
    """
    Create a simple health check function for modules without external dependencies.

    Example:
        # In your module's health.py
        health_check = create_simple_health_check(
            "serp-users",
            "User Management",
            "1.0.0"
        )

        # Register via entry point
        [project.entry-points."serp.modules.health"]
        users = "serp_users:health_check"
    """

    async def health_check() -> ModuleHealthReport:
        return ModuleHealthReport(
            module_id=module_id,
            module_name=module_name,
            status=HealthStatus.HEALTHY,
            version=version,
            components=[
                ComponentHealth(
                    name="module",
                    status=HealthStatus.HEALTHY,
                    message="Module is loaded and running",
                )
            ],
        )

    return health_check
