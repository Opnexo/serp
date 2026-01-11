"""
Application startup and module loading
"""

import logging

from fastapi import FastAPI
from serp_core.plugins import (
    ModuleLoader,
    create_simple_health_check,
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

    # 5. Register health checks from modules
    logger.info("Registering module health checks...")
    for module_name, entry_points in all_entry_points.items():
        module_info = registry.get(module_name)
        if not module_info:
            continue

        if "health" in entry_points:
            # Module provides its own health check
            try:
                health_check = entry_points["health"]
                registry.register_health_check(module_name, health_check)
                logger.info(f"Registered custom health check for {module_name}")
            except Exception as e:
                logger.error(f"Error registering health check for {module_name}: {e}")
        else:
            # Create a simple default health check for modules without one
            default_health = create_simple_health_check(
                module_id=module_name,
                module_name=module_info.display_name,
                version=module_info.version,
            )
            registry.register_health_check(module_name, default_health)
            logger.info(f"Registered default health check for {module_name}")

    logger.info("Application bootstrap complete")
    logger.info(f"Loaded {len(registry.loaded_modules())} modules")
    logger.info(f"Registered {len([m for m in registry.loaded_modules() if registry.has_health_check(m.name)])} health checks")
