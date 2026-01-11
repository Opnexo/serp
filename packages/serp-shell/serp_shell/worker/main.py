"""
Event worker main entry point.

This module provides the main worker process that:
1. Creates an event bus based on configuration
2. Discovers and registers event handlers from all modules
3. Starts the event consumer loop
"""

import asyncio
import logging
import signal
import socket
from typing import Optional

from serp_core.events import IEventBus
from serp_core.events.adapters import InMemoryEventBus, RedisEventBus, KafkaEventBus

from .config import WorkerSettings, get_worker_settings
from .discovery import register_all_handlers

logger = logging.getLogger(__name__)


def create_event_bus(settings: WorkerSettings) -> IEventBus:
    """
    Create an event bus instance based on configuration.
    
    Args:
        settings: Worker settings with backend configuration
        
    Returns:
        Configured IEventBus implementation
    """
    consumer_name = settings.consumer_name or f"{socket.gethostname()}-{id(settings)}"
    
    if settings.event_bus_backend == "memory":
        logger.info("Using InMemoryEventBus (for development/testing)")
        return InMemoryEventBus()
    
    elif settings.event_bus_backend == "redis":
        logger.info(f"Using RedisEventBus: {settings.redis_url}")
        try:
            from redis.asyncio import Redis
        except ImportError:
            raise ImportError(
                "redis package required for Redis backend. "
                "Install with: pip install redis[hiredis]"
            )
        
        redis_client = Redis.from_url(settings.redis_url)
        return RedisEventBus(
            redis_client=redis_client,
            consumer_group=settings.consumer_group,
            consumer_name=consumer_name,
            max_retry=settings.max_retry,
        )
    
    elif settings.event_bus_backend == "kafka":
        logger.info(f"Using KafkaEventBus: {settings.kafka_bootstrap_servers}")
        return KafkaEventBus(
            bootstrap_servers=settings.kafka_bootstrap_servers,
            consumer_group=settings.consumer_group,
            client_id=consumer_name,
        )
    
    else:
        raise ValueError(f"Unknown event bus backend: {settings.event_bus_backend}")


async def run_worker_async(settings: Optional[WorkerSettings] = None) -> None:
    """
    Run the event worker asynchronously.
    
    Args:
        settings: Optional settings (uses defaults if not provided)
    """
    settings = settings or get_worker_settings()
    
    # Configure logging
    logging.basicConfig(
        level=getattr(logging, settings.log_level.upper()),
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    
    logger.info("=" * 60)
    logger.info("SERP Event Worker Starting")
    logger.info(f"Backend: {settings.event_bus_backend}")
    logger.info(f"Consumer Group: {settings.consumer_group}")
    logger.info("=" * 60)
    
    # Create event bus
    event_bus = create_event_bus(settings)
    
    # Discover and register handlers
    handler_count = register_all_handlers(event_bus)
    
    if handler_count == 0:
        logger.warning("No event handlers discovered! Worker will idle.")
    
    # Setup graceful shutdown
    shutdown_event = asyncio.Event()
    
    def signal_handler():
        logger.info("Shutdown signal received...")
        shutdown_event.set()
    
    # Register signal handlers (Unix only, gracefully handle Windows)
    try:
        loop = asyncio.get_running_loop()
        for sig in (signal.SIGTERM, signal.SIGINT):
            loop.add_signal_handler(sig, signal_handler)
    except NotImplementedError:
        # Windows doesn't support add_signal_handler
        pass
    
    # Start the event bus consumer
    try:
        # Start consumer in background
        consumer_task = asyncio.create_task(event_bus.start())
        
        # Wait for shutdown signal
        await shutdown_event.wait()
        
        # Stop the consumer
        await event_bus.stop()
        consumer_task.cancel()
        
    except asyncio.CancelledError:
        logger.info("Worker cancelled")
    except Exception as e:
        logger.error(f"Worker error: {e}")
        raise
    finally:
        logger.info("SERP Event Worker stopped")


def run_worker(settings: Optional[WorkerSettings] = None) -> None:
    """
    Run the event worker (blocking).
    
    This is the main entry point for the CLI command.
    
    Args:
        settings: Optional settings (uses defaults if not provided)
    """
    try:
        asyncio.run(run_worker_async(settings))
    except KeyboardInterrupt:
        print("\nWorker stopped by user")
