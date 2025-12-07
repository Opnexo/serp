"""
Module discovery via Python entry points
"""

import importlib
import importlib.metadata
from typing import Any, Callable, Dict, List

from serp_core.plugins.types import ModuleInfo


def discover_modules() -> Dict[str, ModuleInfo]:
    """
    Discover all installed SERP modules via entry points.

    Looks for modules that define the 'serp.modules' entry point group.

    Returns:
        Dictionary mapping module name to ModuleInfo

    Example entry point in pyproject.toml:
        [project.entry-points."serp.modules"]
        serp-users = "serp_users:MODULE_INFO"
        serp-crm = "serp_crm:MODULE_INFO"
    """
    modules = {}

    try:
        # Get all entry points in the 'serp.modules' group
        entry_points = importlib.metadata.entry_points()

        # Handle both old and new API
        if hasattr(entry_points, "select"):
            # Python 3.10+
            serp_modules = entry_points.select(group="serp.modules")
        else:
            # Python 3.9
            serp_modules = entry_points.get("serp.modules", [])

        for entry_point in serp_modules:
            try:
                # Load the MODULE_INFO object
                module_info = entry_point.load()

                if isinstance(module_info, ModuleInfo):
                    modules[module_info.name] = module_info
                else:
                    print(
                        f"Warning: {entry_point.name} does not export valid MODULE_INFO"
                    )

            except Exception as e:
                print(f"Error loading module {entry_point.name}: {e}")
                continue

    except Exception as e:
        print(f"Error discovering modules: {e}")

    return modules


def discover_modules_by_import() -> Dict[str, ModuleInfo]:
    """
    Alternative discovery method: directly import known modules.

    This is useful during development when entry points aren't set up yet.

    Returns:
        Dictionary mapping module name to ModuleInfo
    """
    module_packages = [
        "serp_users",
        "serp_crm",
        "serp_invoicing",
        # Add more as needed
    ]

    modules = {}

    for package_name in module_packages:
        try:
            module = importlib.import_module(package_name)
            if hasattr(module, "MODULE_INFO"):
                module_info = module.MODULE_INFO
                if isinstance(module_info, ModuleInfo):
                    modules[module_info.name] = module_info
        except ImportError:
            # Module not installed, skip it
            continue
        except Exception as e:
            print(f"Error loading {package_name}: {e}")
            continue

    return modules


def get_module_dependencies(module_info: ModuleInfo) -> List[str]:
    """
    Extract module dependencies from ModuleInfo.

    Returns:
        List of module names this module depends on
    """
    dependencies = []

    for dep in module_info.dependencies:
        # Parse dependency string (e.g., "serp-users>=1.0.0")
        dep_name = dep.split(">=")[0].split("==")[0].split(">")[0].split("<")[0]
        dep_name = dep_name.strip()
        dependencies.append(dep_name)

    return dependencies


def discover_ui_configs() -> Dict[str, Callable[[], Dict[str, Any]]]:
    """
    Discover all installed SERP module UI configurations via entry points.

    Looks for modules that define the 'serp.modules.ui' entry point group.
    Each entry point should reference a function that returns a UI config dict.

    Returns:
        Dictionary mapping module name to UI config loader function

    Example entry point in pyproject.toml:
        [project.entry-points."serp.modules.ui"]
        crm = "serp_crm.ui:load_ui_config"
    """
    ui_configs = {}

    try:
        # Get all entry points in the 'serp.modules.ui' group
        entry_points = importlib.metadata.entry_points()

        # Handle both old and new API
        if hasattr(entry_points, "select"):
            # Python 3.10+
            serp_ui_modules = entry_points.select(group="serp.modules.ui")
        else:
            # Python 3.9
            serp_ui_modules = entry_points.get("serp.modules.ui", [])

        for entry_point in serp_ui_modules:
            try:
                # Load the load_ui_config function
                load_ui_config = entry_point.load()

                if callable(load_ui_config):
                    ui_configs[entry_point.name] = load_ui_config
                else:
                    print(
                        f"Warning: {entry_point.name} UI config loader is not callable"
                    )

            except Exception as e:
                print(f"Error loading UI config for module {entry_point.name}: {e}")
                continue

    except Exception as e:
        print(f"Error discovering UI configs: {e}")

    return ui_configs


def load_all_ui_configs() -> Dict[str, Dict[str, Any]]:
    """
    Load all UI configurations from discovered modules.

    Returns:
        Dictionary mapping module name to UI config dict
    """
    ui_config_loaders = discover_ui_configs()
    loaded_configs = {}

    for module_name, loader_func in ui_config_loaders.items():
        try:
            config = loader_func()
            if isinstance(config, dict):
                loaded_configs[module_name] = config
            else:
                print(
                    f"Warning: UI config from {module_name} is not a dict: {type(config)}"
                )
        except Exception as e:
            print(f"Error calling UI config loader for {module_name}: {e}")
            continue

    return loaded_configs
