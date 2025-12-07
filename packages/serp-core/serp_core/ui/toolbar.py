"""
Toolbar configuration types
"""

from dataclasses import dataclass, field
from typing import List, Optional


@dataclass
class ToolbarItem:
    """
    Represents an item in the toolbar (ribbon).

    Example:
        new_customer = ToolbarItem(
            id="customers.new",
            label="New Customer",
            icon="user-plus",
            action="/customers/new",
            permission="customers.create",
            shortcut="Ctrl+N"
        )
    """

    id: str
    label: str
    icon: str
    action: str  # Route or callback
    permission: Optional[str] = None
    shortcut: Optional[str] = None
    order: int = 0


@dataclass
class ToolbarGroup:
    """
    Represents a group of toolbar items.

    Example:
        customer_group = ToolbarGroup(
            id="customers",
            label="Customers",
            items=[
                ToolbarItem(...),
                ToolbarItem(...),
            ]
        )
    """

    id: str
    label: str
    items: List[ToolbarItem] = field(default_factory=list)
    order: int = 0
