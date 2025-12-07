"""
Application startup and module loading
"""

import logging

from fastapi import FastAPI
from serp_core.plugins import (
    ModuleLoader,
    discover_modules,
    get_module_registry,
)

from serp_shell.startup.config import get_settings

logger = logging.getLogger(__name__)


async def bootstrap_application(app: FastAPI) -> None:
    """
    Bootstrap the application:
    1. Discover installed modules
    2. Load module configurations
    3. Initialize modules
    4. Register API routes
    5. Setup UI integration

    Args:
        app: FastAPI application instance
    """
    logger.info("Starting application bootstrap...")

    settings = get_settings()
    registry = get_module_registry()

    # 1. Discover modules
    logger.info("Discovering installed modules...")
    discovered_modules = discover_modules()
    logger.info(f"Found {len(discovered_modules)} modules")

    # 2. Register modules
    for name, module_info in discovered_modules.items():
        # Check if module is enabled in config
        if name in settings.enabled_modules or settings.enable_all_modules:
            logger.info(f"Registering module: {name}")
            registry.register(module_info)
        else:
            logger.info(f"Skipping disabled module: {name}")

    # 3. Load modules
    logger.info("Loading module entry points...")
    loader = ModuleLoader(registry)
    all_entry_points = loader.load_all()

    # 4. Register API routes from modules
    for module_name, entry_points in all_entry_points.items():
        if "api" in entry_points:
            try:
                logger.info(f"Loading API routes for {module_name}...")
                load_api_routes = entry_points["api"]
                router = load_api_routes()

                # Register router with module prefix
                module_prefix = module_name.replace("serp-", "")
                app.include_router(
                    router, prefix=f"/api/{module_prefix}", tags=[module_name]
                )

                logger.info(f"Registered routes for {module_name}")
            except Exception as e:
                logger.error(f"Error loading routes for {module_name}: {e}")

    logger.info("Application bootstrap complete")
    logger.info(f"Loaded {len(registry.loaded_modules())} modules")
