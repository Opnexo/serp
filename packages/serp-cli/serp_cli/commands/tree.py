"""
Tree command for showing module structure
"""

from pathlib import Path

import click
from rich.console import Console
from rich.tree import Tree

console = Console()


@click.command()
@click.argument("path", type=click.Path(exists=True), default=".")
@click.option("--depth", "-d", type=int, default=3, help="Maximum depth to show")
def tree(path, depth):
    """Show module directory structure"""

    module_path = Path(path).resolve()

    tree_view = Tree(f"[bold cyan]{module_path.name}[/bold cyan]", guide_style="dim")

    def add_directory(parent_tree, directory, current_depth=0):
        """Recursively add directory contents to tree"""
        if current_depth >= depth:
            return

        try:
            items = sorted(directory.iterdir(), key=lambda x: (not x.is_dir(), x.name))
        except PermissionError:
            return

        for item in items:
            # Skip common ignore patterns
            if item.name.startswith(".") or item.name in [
                "__pycache__",
                "node_modules",
                ".venv",
                "venv",
            ]:
                continue

            if item.is_dir():
                branch = parent_tree.add(f"[bold blue]{item.name}[/bold blue]/")
                add_directory(branch, item, current_depth + 1)
            else:
                # Color-code files by type
                if item.suffix == ".py":
                    parent_tree.add(f"[green]{item.name}[/green]")
                elif item.suffix in [".md", ".txt", ".rst"]:
                    parent_tree.add(f"[yellow]{item.name}[/yellow]")
                elif item.suffix in [".toml", ".yaml", ".yml", ".json"]:
                    parent_tree.add(f"[magenta]{item.name}[/magenta]")
                else:
                    parent_tree.add(f"[dim]{item.name}[/dim]")

    add_directory(tree_view, module_path)

    console.print()
    console.print(tree_view)
    console.print()
