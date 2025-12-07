"""
List command for viewing modules and components
"""

import click
from rich.console import Console
from rich.table import Table
from serp_core.plugins import discover_modules

console = Console()


@click.command()
@click.option("--verbose", "-v", is_flag=True, help="Show detailed information")
def list_modules(verbose):
    """List all installed SERP modules"""

    console.print("\n[bold]Discovering SERP modules...[/bold]\n")

    modules = discover_modules()

    if not modules:
        console.print("[yellow]No SERP modules found.[/yellow]")
        console.print("\nInstall modules with: [cyan]uv add serp-users serp-crm[/cyan]")
        return

    table = Table(title="Installed SERP Modules")
    table.add_column("Name", style="cyan", no_wrap=True)
    table.add_column("Version", style="green")
    table.add_column("Display Name", style="white")

    if verbose:
        table.add_column("Author", style="dim")
        table.add_column("Description", style="dim")

    for name, info in sorted(modules.items()):
        row = [name, info.version, info.display_name]
        if verbose:
            row.extend([info.author, info.description])
        table.add_row(*row)

    console.print(table)
    console.print(f"\n[dim]Total modules: {len(modules)}[/dim]\n")
