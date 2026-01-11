"""
CLI commands for serp-shell
"""

import click
import uvicorn


@click.group()
def main():
    """SimpleERP command-line interface"""
    pass


@main.command()
@click.option("--host", default="0.0.0.0", help="Host to bind to")
@click.option("--port", default=8000, help="Port to bind to")
def run(host: str, port: int):
    """Run the SERP application in production mode"""
    click.echo("Starting SimpleERP server...")
    uvicorn.run(
        "serp_shell.api.app:create_app",
        host=host,
        port=port,
        factory=True,
    )


@main.command()
@click.option("--host", default="0.0.0.0", help="Host to bind to")
@click.option("--port", default=8000, help="Port to bind to")
def dev(host: str, port: int):
    """Run the SERP application in development mode with auto-reload"""
    click.echo("Starting SimpleERP development server...")
    uvicorn.run(
        "serp_shell.api.app:create_app",
        host=host,
        port=port,
        reload=True,
        factory=True,
    )


@main.command()
def version():
    """Show the version"""
    from serp_shell import __version__

    click.echo(f"SimpleERP Shell version {__version__}")


@main.command()
@click.option(
    "--backend",
    type=click.Choice(["memory", "redis", "kafka"]),
    default="memory",
    help="Event bus backend to use"
)
@click.option(
    "--group",
    default="serp-workers",
    help="Consumer group name"
)
@click.option(
    "--redis-url",
    default="redis://localhost:6379",
    help="Redis URL (if using redis backend)"
)
@click.option(
    "--kafka-servers",
    default="localhost:9094",
    help="Kafka bootstrap servers (if using kafka backend)"
)
@click.option(
    "--log-level",
    type=click.Choice(["DEBUG", "INFO", "WARNING", "ERROR"]),
    default="INFO",
    help="Logging level"
)
def worker(
    backend: str,
    group: str,
    redis_url: str,
    kafka_servers: str,
    log_level: str
):
    """Start the event worker process
    
    The event worker consumes events from the configured
    event bus and dispatches them to registered handlers.
    
    Examples:
    
        # Start with in-memory bus (development)
        serp worker
        
        # Start with Redis
        serp worker --backend redis --redis-url redis://localhost:6379
        
        # Start with Kafka
        serp worker --backend kafka --kafka-servers localhost:9094
    """
    click.echo("Starting SERP Event Worker...")
    click.echo(f"  Backend: {backend}")
    click.echo(f"  Consumer Group: {group}")
    
    from serp_shell.worker import run_worker
    from serp_shell.worker.config import WorkerSettings
    
    settings = WorkerSettings(
        event_bus_backend=backend,
        consumer_group=group,
        redis_url=redis_url,
        kafka_bootstrap_servers=kafka_servers,
        log_level=log_level,
    )
    
    run_worker(settings)


if __name__ == "__main__":
    main()

