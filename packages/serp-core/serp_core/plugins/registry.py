"""
Module registry for tracking loaded modules
"""

from typing import Dict, List, Optional

from serp_core.plugins.types import ModuleConfig, ModuleInfo


class ModuleRegistry:
    """
    Central registry for all loaded modules.

    Tracks module metadata, configuration, and loaded state.
    """

    def __init__(self) -> None:
        self._modules: Dict[str, ModuleInfo] = {}
        self._configs: Dict[str, ModuleConfig] = {}
        self._loaded: Dict[str, bool] = {}

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


# Global module registry instance
_module_registry = ModuleRegistry()


def get_module_registry() -> ModuleRegistry:
    """Get the global module registry"""
    return _module_registry
