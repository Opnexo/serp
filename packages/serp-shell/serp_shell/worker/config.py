"""
Worker configuration settings.
"""

from functools import lru_cache
from typing import Literal, Optional

from pydantic import Field
from serp_core.config import Settings


class WorkerSettings(Settings):
    """
    Settings for the event worker process.
    
    Configuration via environment variables (SERP_WORKER_*).
    """
    
    # Event bus backend
    event_bus_backend: Literal["memory", "redis", "kafka"] = Field(
        default="memory",
        env="SERP_WORKER_BACKEND",
        description="Event bus backend to use"
    )
    
    # Consumer group settings
    consumer_group: str = Field(
        default="serp-workers",
        env="SERP_WORKER_GROUP",
        description="Consumer group name for load balancing"
    )
    consumer_name: Optional[str] = Field(
        default=None,
        env="SERP_WORKER_NAME",
        description="Unique consumer name (auto-generated if not set)"
    )
    
    # Redis settings
    redis_url: str = Field(
        default="redis://localhost:6379",
        env="SERP_REDIS_URL",
        description="Redis connection URL"
    )
    
    # Kafka settings
    kafka_bootstrap_servers: str = Field(
        default="localhost:9094",
        env="SERP_KAFKA_SERVERS",
        description="Kafka broker addresses"
    )
    
    # Worker behavior
    max_retry: int = Field(
        default=3,
        env="SERP_WORKER_MAX_RETRY",
        description="Maximum retry attempts for failed handlers"
    )
    
    # Logging
    log_level: str = Field(
        default="INFO",
        env="SERP_WORKER_LOG_LEVEL"
    )
    
    class Config:
        env_file = ".env"
        env_prefix = "SERP_"


@lru_cache()
def get_worker_settings() -> WorkerSettings:
    """Get cached worker settings instance."""
    return WorkerSettings()
