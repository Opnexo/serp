"""
UI module loader for serp-common.

This module provides the UI configuration that is loaded by the shell.
"""

from pathlib import Path


def load_ui_config():
    """
    Load UI configuration for the common module.

    Returns the path to the UI bundle and module configuration.
    """
    ui_dir = Path(__file__).parent

    return {
        "module_id": "common",
        "module_name": "Common",
        "version": "0.1.0",
        "bundle_path": ui_dir / "dist" / "common-module.iife.js",
        "icon": "Building",
        "description": "Shared entities and resources",
        "ribbon": {
            "tab_id": "common",
            "tab_label": "Common",
            "tab_icon": "Building",
            "tab_order": 5,
            "groups": [
                {
                    "group_id": "common-resources",
                    "group_label": "Resources",
                    "group_order": 1,
                    "buttons": [
                        {
                            "button_id": "common-addresses-list",
                            "label": "Addresses",
                            "icon": "MapPin",
                            "permission": "common:addresses:list",
                            "action": {"type": "navigate", "route": "/common/addresses"},
                            "button_order": 1,
                            "tooltip": "Manage addresses",
                        },
                    ],
                },
            ],
        },
        "routes": [
            {
                "route_id": "common-addresses",
                "path": "/common/addresses",
                "permission": "common:addresses:list",
                "component": "AddressesListView",
            },
            {
                "route_id": "common-address-detail",
                "path": "/common/addresses/:id",
                "permission": "common:addresses:read",
                "component": "AddressDetailView",
            },
            {
                "route_id": "common-address-new",
                "path": "/common/addresses/new",
                "permission": "common:addresses:create",
                "component": "AddressEditView",
            },
            {
                "route_id": "common-address-edit",
                "path": "/common/addresses/:id/edit",
                "permission": "common:addresses:update",
                "component": "AddressEditView",
            },
        ],
    }
