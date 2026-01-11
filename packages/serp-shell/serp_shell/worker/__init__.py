"""
SERP Event Worker

This module provides the event consumer process that:
- Discovers event handlers from installed modules via entry points
- Subscribes to relevant event streams
- Dispatches events to handlers
"""

from .main import run_worker
from .discovery import discover_event_handlers
from .config import WorkerSettings, get_worker_settings

__all__ = [
    "run_worker",
    "discover_event_handlers",
    "WorkerSettings",
    "get_worker_settings",
]
