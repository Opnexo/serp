"""
Module configuration loader.

Loads module configuration from YAML files and provides
a production-ready way to discover enabled modules without
requiring pyproject.toml dependencies.
"""

import importlib
import os
from pathlib import Path
from typing import Any, Callable

import yaml
from pydantic import BaseModel


class ModuleUIConfig(BaseModel):
    """UI-specific configuration for a module."""

    bundle_path: str = ""
    hmr_port: int | None = None


class ModuleConfig(BaseModel):
    """Configuration for a single module."""

    id: str
    package: str
    enabled: bool = True
    ui: ModuleUIConfig = ModuleUIConfig()


class ModulesConfig(BaseModel):
    """Root configuration containing all modules."""

    modules: list[ModuleConfig] = []


def find_config_file() -> Path | None:
    """
    Find the modules.yaml config file.

    Searches in order:
    1. SERP_MODULES_CONFIG environment variable
    2. ./config/modules.yaml (relative to cwd)
    3. /etc/serp/modules.yaml (system-wide)
    4. ~/.serp/modules.yaml (user-specific)
    """
    # 1. Environment variable
    if env_path := os.environ.get("SERP_MODULES_CONFIG"):
        path = Path(env_path)
        if path.exists():
            return path

    # 2. Relative to current working directory
    cwd_config = Path.cwd() / "config" / "modules.yaml"
    if cwd_config.exists():
        return cwd_config

    # 3. Also check parent directories (for when running from packages/serp-shell)
    for parent in Path.cwd().parents:
        parent_config = parent / "config" / "modules.yaml"
        if parent_config.exists():
            return parent_config

    # 4. System-wide config
    system_config = Path("/etc/serp/modules.yaml")
    if system_config.exists():
        return system_config

    # 5. User-specific config
    user_config = Path.home() / ".serp" / "modules.yaml"
    if user_config.exists():
        return user_config

    return None


def load_modules_config() -> ModulesConfig:
    """
    Load the modules configuration from YAML file.

    Returns:
        ModulesConfig with all configured modules
    """
    config_path = find_config_file()

    if config_path is None:
        print("Warning: No modules.yaml config file found. No modules will be loaded.")
        return ModulesConfig(modules=[])

    print(f"Loading modules config from: {config_path}")

    try:
        with open(config_path) as f:
            data = yaml.safe_load(f) or {}

        return ModulesConfig(**data)
    except Exception as e:
        print(f"Error loading modules config: {e}")
        return ModulesConfig(modules=[])


def get_enabled_modules() -> list[ModuleConfig]:
    """
    Get list of enabled modules from configuration.

    Returns:
        List of enabled ModuleConfig objects
    """
    config = load_modules_config()
    return [m for m in config.modules if m.enabled]


def load_module_ui_config(module: ModuleConfig) -> dict[str, Any] | None:
    """
    Load the UI configuration for a specific module.

    Dynamically imports the module's ui package and calls load_ui_config().

    Args:
        module: The module configuration

    Returns:
        UI config dict or None if loading fails
    """
    try:
        # Import the module's ui subpackage
        ui_module = importlib.import_module(f"{module.package}.ui")

        # Call load_ui_config if it exists
        if hasattr(ui_module, "load_ui_config"):
            config = ui_module.load_ui_config()

            # Ensure the config has the module ID
            if isinstance(config, dict):
                config.setdefault("moduleId", module.id)

                # Merge in the config-file UI settings
                if module.ui.hmr_port:
                    config.setdefault("hmr", {})
                    config["hmr"]["port"] = module.ui.hmr_port

                return config

    except ImportError as e:
        print(f"Warning: Could not import module '{module.package}': {e}")
        print(f"  Make sure '{module.package}' is installed: pip install {module.id}")
    except Exception as e:
        print(f"Error loading UI config for '{module.id}': {e}")

    return None


def load_all_module_ui_configs() -> dict[str, dict[str, Any]]:
    """
    Load UI configurations for all enabled modules.

    Returns:
        Dictionary mapping module ID to UI config
    """
    configs: dict[str, dict[str, Any]] = {}

    for module in get_enabled_modules():
        config = load_module_ui_config(module)
        if config:
            configs[module.id] = config
            print(f"  ✓ Loaded UI config for module: {module.id}")
        else:
            print(f"  ✗ Failed to load UI config for module: {module.id}")

    return configs
