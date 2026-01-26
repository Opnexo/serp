"""
UI Configuration routes for dynamic module loading
"""

import traceback
from typing import Any, Dict

from fastapi import APIRouter
from serp_core.plugins.discovery import load_all_ui_configs_from_yaml

router = APIRouter()


@router.get("/ui-config")
async def get_ui_config() -> Dict[str, Any]:
    """
    Get aggregated UI configurations from all installed modules.

    This endpoint discovers and loads UI configurations from all SERP modules
    that have registered a 'serp.modules.ui' entry point.

    Returns:
        Dict containing UI configurations for all modules, keyed by module name.
        Each module config includes:
        - moduleId: Module identifier
        - moduleName: Display name
        - ribbon: Toolbar/ribbon configuration with tabs, groups, and buttons
        - routes: Route definitions with permissions
        - permissions: List of all module permissions

    Example response:
        {
            "crm": {
                "moduleId": "crm",
                "moduleName": "CRM",
                "ribbon": {...},
                "routes": [...],
                "permissions": [...]
            }
        }
    """
    try:
        print("=" * 80)
        print("UI CONFIG ENDPOINT CALLED")
        print("=" * 80)

        print("Loading UI configs...")
        ui_configs = load_all_ui_configs_from_yaml()

        print(f"Loaded {len(ui_configs)} module configs:")
        for module_name, config in ui_configs.items():
            print(f"  - {module_name}: {type(config)}")

        print("=" * 80)

        # TODO: Filter by user permissions when auth is implemented
        # For now, return all configs

        return ui_configs

    except Exception as e:
        # Log the full error with traceback
        print("=" * 80)
        print("ERROR IN UI CONFIG ENDPOINT!")
        print("=" * 80)
        print(f"Error type: {type(e).__name__}")
        print(f"Error message: {e}")
        print("Traceback:")
        traceback.print_exc()
        print("=" * 80)

        # Return error info instead of crashing
        return {
            "error": str(e),
            "error_type": type(e).__name__,
            "traceback": traceback.format_exc(),
        }


@router.get("/ui-config/{module_name}")
async def get_module_ui_config(module_name: str) -> Dict[str, Any]:
    """
    Get UI configuration for a specific module.

    Args:
        module_name: The name of the module (e.g., 'crm', 'invoicing')

    Returns:
        UI configuration dict for the specified module, or 404 if not found
    """
    try:
        ui_configs = load_all_ui_configs_from_yaml()

        if module_name in ui_configs:
            return ui_configs[module_name]
        else:
            return {"error": f"Module '{module_name}' not found or has no UI config"}

    except Exception as e:
        print(f"Error loading UI config for {module_name}: {e}")
        return {"error": str(e)}
