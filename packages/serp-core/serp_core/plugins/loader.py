"""
Module loader for initializing modules
"""

import importlib
from typing import Any, Dict, List, Optional

from serp_core.plugins.registry import ModuleRegistry, get_module_registry
from serp_core.plugins.types import ModuleInfo


class ModuleLoader:
    """
    Loader for initializing SERP modules.

    Handles:
    - Loading module entry points
    - Dependency resolution
    - Initialization ordering
    """

    def __init__(self, registry: Optional[ModuleRegistry] = None):
        self.registry = registry or get_module_registry()

    def load_module(self, module_info: ModuleInfo) -> Dict[str, Any]:
        """
        Load a single module's entry points.

        Args:
            module_info: Module metadata

        Returns:
            Dictionary of loaded entry points

        Example:
            loader = ModuleLoader()
            entry_points = loader.load_module(module_info)

            # Get API routes
            api_loader = entry_points.get("api")
            if api_loader:
                routes = api_loader()
        """
        loaded_entry_points = {}

        for key, entry_point_str in module_info.entry_points.items():
            try:
                # Parse entry point string: "module.path:attribute"
                module_path, attr_name = entry_point_str.split(":")
                module = importlib.import_module(module_path)
                entry_point = getattr(module, attr_name)
                loaded_entry_points[key] = entry_point

            except Exception as e:
                print(f"Error loading entry point '{key}' from {module_info.name}: {e}")
                continue

        # Mark module as loaded
        self.registry.mark_loaded(module_info.name)

        return loaded_entry_points

    def load_all(self) -> Dict[str, Dict[str, Any]]:
        """
        Load all enabled modules.

        Returns:
            Dictionary mapping module name to loaded entry points
        """
        all_entry_points = {}

        # Get enabled modules in dependency order
        modules = self._sort_by_dependencies(self.registry.enabled_modules())

        for module_info in modules:
            try:
                entry_points = self.load_module(module_info)
                all_entry_points[module_info.name] = entry_points
            except Exception as e:
                print(f"Error loading module {module_info.name}: {e}")
                continue

        return all_entry_points

    def _sort_by_dependencies(self, modules: List[ModuleInfo]) -> List[ModuleInfo]:
        """
        Sort modules by dependencies (topological sort).

        Args:
            modules: List of modules to sort

        Returns:
            Sorted list where dependencies come before dependents
        """
        # Simple implementation - in production, use proper topological sort
        # For now, just ensure serp-core is first
        sorted_modules = []
        core_modules = []
        other_modules = []

        for module in modules:
            if module.name == "serp-core":
                core_modules.append(module)
            else:
                other_modules.append(module)

        sorted_modules.extend(core_modules)
        sorted_modules.extend(other_modules)

        return sorted_modules
