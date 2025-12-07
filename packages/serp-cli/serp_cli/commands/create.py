"""
Create commands for generating code
"""

import click
from rich.console import Console
from rich.prompt import Confirm, Prompt

from serp_cli.generators import (
    EntityGenerator,
    ModuleGenerator,
    RepositoryGenerator,
    ServiceGenerator,
    ViewGenerator,
)

console = Console()


@click.group()
def create():
    """Create new SERP components (entities, services, modules, etc.)"""
    pass


@create.command()
@click.argument("name", required=False)
@click.option("--module", "-m", help="Module name (e.g., serp-crm)")
@click.option("--field", "-f", multiple=True, help="Field definition (name:type)")
@click.option("--value-object", "-vo", multiple=True, help="Value object to create")
def entity(name, module, field, value_object):
    """Create a new domain entity"""

    # Interactive mode if name not provided
    if not name:
        name = Prompt.ask("Entity name")

    if not module:
        module = Prompt.ask("Module name", default="serp-custom")

    # Parse fields
    fields = []
    if field:
        for f in field:
            if ":" in f:
                field_name, field_type = f.split(":", 1)
                fields.append({"name": field_name, "type": field_type})

    # Interactive field addition
    if not fields and Confirm.ask("Add fields interactively?", default=True):
        while True:
            field_name = Prompt.ask("Field name (empty to finish)", default="")
            if not field_name:
                break
            field_type = Prompt.ask("Field type", default="str")
            fields.append({"name": field_name, "type": field_type})

    console.print(f"\n[bold green]Creating entity:[/bold green] {name}")
    console.print(f"[dim]Module: {module}[/dim]")
    console.print(f"[dim]Fields: {len(fields)}[/dim]")

    generator = EntityGenerator()
    output_path = generator.generate(
        name=name, module=module, fields=fields, value_objects=list(value_object)
    )

    console.print(f"\n✓ Entity created at: [cyan]{output_path}[/cyan]")


@create.command()
@click.argument("name", required=False)
@click.option("--entity", "-e", help="Entity name")
@click.option("--module", "-m", help="Module name")
@click.option("--method", multiple=True, help="Custom repository methods")
def repository(name, entity, module, method):
    """Create a new repository"""

    if not name:
        name = Prompt.ask("Repository name")

    if not entity:
        entity = Prompt.ask("Entity name")

    if not module:
        module = Prompt.ask("Module name", default="serp-custom")

    console.print(f"\n[bold green]Creating repository:[/bold green] {name}")
    console.print(f"[dim]Entity: {entity}[/dim]")
    console.print(f"[dim]Module: {module}[/dim]")

    generator = RepositoryGenerator()
    output_path = generator.generate(
        name=name, entity=entity, module=module, custom_methods=list(method)
    )

    console.print(f"\n✓ Repository created at: [cyan]{output_path}[/cyan]")


@create.command()
@click.argument("name", required=False)
@click.option(
    "--type",
    "-t",
    type=click.Choice(["domain", "application"]),
    default="application",
    help="Service type",
)
@click.option("--module", "-m", help="Module name")
def service(name, type, module):
    """Create a new service"""

    if not name:
        name = Prompt.ask("Service name")

    if not module:
        module = Prompt.ask("Module name", default="serp-custom")

    console.print(f"\n[bold green]Creating {type} service:[/bold green] {name}")
    console.print(f"[dim]Module: {module}[/dim]")

    generator = ServiceGenerator()
    output_path = generator.generate(name=name, service_type=type, module=module)

    console.print(f"\n✓ Service created at: [cyan]{output_path}[/cyan]")


@create.command()
@click.argument("name", required=False)
@click.option("--module", "-m", help="Module name")
@click.option("--route", "-r", help="Route path (e.g., /customers)")
@click.option("--permission", "-p", help="Required permission")
def view(name, module, route, permission):
    """Create a new UI view"""

    if not name:
        name = Prompt.ask("View name")

    if not module:
        module = Prompt.ask("Module name", default="serp-custom")

    if not route:
        route = Prompt.ask("Route path", default=f"/{name.lower()}")

    console.print(f"\n[bold green]Creating view:[/bold green] {name}")
    console.print(f"[dim]Module: {module}[/dim]")
    console.print(f"[dim]Route: {route}[/dim]")

    generator = ViewGenerator()
    output_path = generator.generate(
        name=name, module=module, route=route, permission=permission
    )

    console.print(f"\n✓ View created at: [cyan]{output_path}[/cyan]")


@create.command()
@click.argument("name", required=False)
@click.option("--description", "-d", help="Module description")
@click.option("--author", "-a", help="Author name")
def module(name, description, author):
    """Create a new SERP module"""

    if not name:
        name = Prompt.ask("Module name (e.g., inventory)")

    # Ensure serp- prefix
    if not name.startswith("serp-"):
        name = f"serp-{name}"

    if not description:
        description = Prompt.ask("Description", default=f"SERP {name} module")

    if not author:
        author = Prompt.ask("Author name", default="Your Name")

    console.print(f"\n[bold green]Creating module:[/bold green] {name}")
    console.print(f"[dim]Description: {description}[/dim]")

    generator = ModuleGenerator()
    output_path = generator.generate(name=name, description=description, author=author)

    console.print(f"\n✓ Module created at: [cyan]{output_path}[/cyan]")
    console.print("\n[bold]Next steps:[/bold]")
    console.print(f"  cd {output_path}")
    console.print("  uv sync")
    console.print("  serp-cli create entity YourEntity --module " + name)
