"""
Main CLI entry point
"""

import click
from rich.console import Console

from serp_cli.commands import create, list_cmd, tree, validate

console = Console()


@click.group()
@click.version_option()
def main():
    """
    SimpleERP CLI - Developer tools for building SERP modules

    Create entities, services, repositories, and more with simple commands.
    """
    pass


# Register command groups
main.add_command(create.create)
main.add_command(list_cmd.list_modules)
main.add_command(validate.validate)
main.add_command(tree.tree)


if __name__ == "__main__":
    main()
