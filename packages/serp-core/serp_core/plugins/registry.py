"""
Module registry for tracking loaded modules
"""

from typing import Any, Callable, Coroutine, Dict, List, Optional

from serp_core.plugins.types import (
    HealthCheckFunc,
    HealthStatus,
    ModuleConfig,
    ModuleHealthReport,
    ModuleInfo,
)


class ModuleRegistry:
    """
    Central registry for all loaded modules.

    Tracks module metadata, configuration, loaded state, and health checks.
    """

    def __init__(self) -> None:
        self._modules: Dict[str, ModuleInfo] = {}
        self._configs: Dict[str, ModuleConfig] = {}
        self._loaded: Dict[str, bool] = {}
        self._health_checks: Dict[str, HealthCheckFunc] = {}

    def register(
        self, module_info: ModuleInfo, config: Optional[ModuleConfig] = None
    ) -> None:
        """
        Register a module.

        Args:
            module_info: Module metadata
            config: Optional runtime configuration
        """
        self._modules[module_info.name] = module_info
        self._loaded[module_info.name] = False

        if config:
            self._configs[module_info.name] = config
        else:
            # Create default config
            self._configs[module_info.name] = ModuleConfig(
                name=module_info.name, enabled=module_info.enabled
            )

    def get(self, name: str) -> Optional[ModuleInfo]:
        """Get module info by name"""
        return self._modules.get(name)

    def get_config(self, name: str) -> Optional[ModuleConfig]:
        """Get module configuration by name"""
        return self._configs.get(name)

    def is_loaded(self, name: str) -> bool:
        """Check if a module is loaded"""
        return self._loaded.get(name, False)

    def mark_loaded(self, name: str) -> None:
        """Mark a module as loaded"""
        if name in self._modules:
            self._loaded[name] = True

    def all(self) -> List[ModuleInfo]:
        """Get all registered modules"""
        return list(self._modules.values())

    def enabled_modules(self) -> List[ModuleInfo]:
        """Get all enabled modules"""
        return [
            info for name, info in self._modules.items() if self._configs[name].enabled
        ]

    def loaded_modules(self) -> List[ModuleInfo]:
        """Get all loaded modules"""
        return [info for name, info in self._modules.items() if self._loaded.get(name)]

    def exists(self, name: str) -> bool:
        """Check if a module is registered"""
        return name in self._modules

    def clear(self) -> None:
        """Clear all registered modules"""
        self._modules.clear()
        self._configs.clear()
        self._loaded.clear()
        self._health_checks.clear()

    # Health check methods
    def register_health_check(
        self, module_name: str, health_check: HealthCheckFunc
    ) -> None:
        """
        Register a health check function for a module.

        Args:
            module_name: Name of the module
            health_check: Async function that returns ModuleHealthReport
        """
        self._health_checks[module_name] = health_check

    def get_health_check(self, module_name: str) -> Optional[HealthCheckFunc]:
        """Get the health check function for a module."""
        return self._health_checks.get(module_name)

    def has_health_check(self, module_name: str) -> bool:
        """Check if a module has a registered health check."""
        return module_name in self._health_checks

    async def check_module_health(self, module_name: str) -> Optional[ModuleHealthReport]:
        """
        Run health check for a specific module.

        Returns:
            ModuleHealthReport if health check exists, None otherwise
        """
        health_check = self._health_checks.get(module_name)
        if health_check:
            return await health_check()
        return None

    async def check_all_health(self) -> Dict[str, ModuleHealthReport]:
        """
        Run health checks for all loaded modules.

        Returns:
            Dict mapping module names to their health reports
        """
        results: Dict[str, ModuleHealthReport] = {}
        for module_name in self._health_checks:
            if self._loaded.get(module_name, False):
                try:
                    report = await self._health_checks[module_name]()
                    results[module_name] = report
                except Exception as e:
                    # Create an error report if health check fails
                    module_info = self._modules.get(module_name)
                    results[module_name] = ModuleHealthReport(
                        module_id=module_name,
                        module_name=module_info.display_name if module_info else module_name,
                        status=HealthStatus.UNHEALTHY,
                        version=module_info.version if module_info else "unknown",
                        message=f"Health check failed: {str(e)}",
                    )
        return results

    def get_overall_status(self, reports: Dict[str, ModuleHealthReport]) -> HealthStatus:
        """
        Determine overall system health from individual module reports.

        Returns UNHEALTHY if any module is unhealthy,
        DEGRADED if any module is degraded,
        HEALTHY otherwise.
        """
        if not reports:
            return HealthStatus.HEALTHY

        statuses = [r.status for r in reports.values()]

        if HealthStatus.UNHEALTHY in statuses:
            return HealthStatus.UNHEALTHY
        if HealthStatus.DEGRADED in statuses:
            return HealthStatus.DEGRADED
        return HealthStatus.HEALTHY


# Global module registry instance
_module_registry = ModuleRegistry()


def get_module_registry() -> ModuleRegistry:
    """Get the global module registry"""
    return _module_registry
