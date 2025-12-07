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


if __name__ == "__main__":
    main()
