"""
Plugin type definitions
"""

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional


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
