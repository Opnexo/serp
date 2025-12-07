"""
UI component registry
"""

from dataclasses import dataclass, field
from typing import Any, Dict, List


@dataclass
class UIComponent:
    """
    Represents a UI component provided by a module.

    Example:
        customer_list = UIComponent(
            id="customers.list",
            module="serp-crm",
            type="view",
            path="/customers",
            component_path="@serp/crm/views/CustomerList"
        )
    """

    id: str
    module: str
    type: str  # "view", "widget", "modal", etc.
    path: str
    component_path: str
    metadata: Dict[str, Any] = field(default_factory=dict)


class UIRegistry:
    """
    Registry for UI components provided by modules.

    Modules register their views, widgets, and other UI components.
    """

    def __init__(self) -> None:
        self._components: Dict[str, UIComponent] = {}

    def register(self, component: UIComponent) -> None:
        """Register a UI component"""
        self._components[component.id] = component

    def get(self, component_id: str) -> UIComponent | None:
        """Get a component by ID"""
        return self._components.get(component_id)

    def all(self) -> List[UIComponent]:
        """Get all registered components"""
        return list(self._components.values())

    def by_module(self, module_name: str) -> List[UIComponent]:
        """Get all components for a module"""
        return [c for c in self._components.values() if c.module == module_name]

    def by_type(self, component_type: str) -> List[UIComponent]:
        """Get all components of a type"""
        return [c for c in self._components.values() if c.type == component_type]


# Global UI registry
_ui_registry = UIRegistry()


def get_ui_registry() -> UIRegistry:
    """Get the global UI registry"""
    return _ui_registry
