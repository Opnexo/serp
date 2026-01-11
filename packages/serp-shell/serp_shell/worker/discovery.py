"""
Event handler discovery via Python entry points.

Modules register their event handlers using the `serp.event_handlers` entry point:

    [project.entry-points."serp.event_handlers"]
    my_module = "my_module.Application.EventHandlers:load_event_handlers"

The load_event_handlers function receives an IEventBus and registers handlers.
"""

import importlib.metadata
import logging
from typing import Callable, Dict, List

from serp_core.events import IEventBus

logger = logging.getLogger(__name__)

ENTRY_POINT_GROUP = "serp.event_handlers"


def discover_event_handlers() -> Dict[str, Callable[[IEventBus], None]]:
    """
    Discover all event handler registration functions from installed packages.
    
    Returns:
        Dict mapping module name to load_event_handlers function
    
    Example entry point definition in pyproject.toml:
        [project.entry-points."serp.event_handlers"]
        payments = "serp_payments.Application.EventHandlers:load_event_handlers"
    """
    handlers: Dict[str, Callable[[IEventBus], None]] = {}
    
    try:
        entry_points = importlib.metadata.entry_points(group=ENTRY_POINT_GROUP)
    except TypeError:
        # Python 3.9 compatibility
        all_eps = importlib.metadata.entry_points()
        entry_points = all_eps.get(ENTRY_POINT_GROUP, [])
    
    for ep in entry_points:
        module_name = ep.name
        try:
            load_fn = ep.load()
            handlers[module_name] = load_fn
            logger.info(f"Discovered event handlers: {module_name}")
        except Exception as e:
            logger.warning(f"Failed to load event handlers for {module_name}: {e}")
    
    return handlers


def register_all_handlers(event_bus: IEventBus) -> int:
    """
    Discover and register all event handlers with the event bus.
    
    Args:
        event_bus: The event bus to register handlers with
        
    Returns:
        Number of modules that registered handlers
    """
    handlers = discover_event_handlers()
    registered_count = 0
    
    for module_name, load_fn in handlers.items():
        try:
            logger.info(f"Registering handlers for: {module_name}")
            load_fn(event_bus)
            registered_count += 1
        except Exception as e:
            logger.error(f"Error registering handlers for {module_name}: {e}")
    
    logger.info(f"Registered handlers from {registered_count} modules")
    return registered_count
