"""
Validate command for checking module structure
"""

from pathlib import Path

import click
from rich.console import Console
from rich.panel import Panel

console = Console()


@click.command()
@click.argument("path", type=click.Path(exists=True), default=".")
def validate(path):
    """Validate SERP module structure"""

    module_path = Path(path)
    console.print(f"\n[bold]Validating module at:[/bold] {module_path}\n")

    errors = []
    warnings = []

    # Check pyproject.toml
    pyproject = module_path / "pyproject.toml"
    if not pyproject.exists():
        errors.append("Missing pyproject.toml")
    else:
        console.print("✓ Found pyproject.toml")

    # Check module directory
    module_dirs = list(module_path.glob("serp_*"))
    if not module_dirs:
        errors.append("No module directory found (serp_*)")
    else:
        module_dir = module_dirs[0]
        console.print(f"✓ Found module directory: {module_dir.name}")

        # Check __init__.py
        init_file = module_dir / "__init__.py"
        if not init_file.exists():
            errors.append(f"Missing {module_dir.name}/__init__.py")
        else:
            console.print("✓ Found __init__.py")

            # Check for MODULE_INFO
            content = init_file.read_text()
            if "MODULE_INFO" not in content:
                warnings.append("MODULE_INFO not found in __init__.py")
            else:
                console.print("✓ MODULE_INFO defined")

        # Check DDD structure
        expected_dirs = ["Domain", "Application", "Infrastructure", "Interfaces"]
        for dir_name in expected_dirs:
            dir_path = module_dir / dir_name
            if dir_path.exists():
                console.print(f"✓ Found {dir_name}/ directory")
            else:
                warnings.append(f"Missing recommended directory: {dir_name}/")

    # Check tests
    tests_dir = module_path / "tests"
    if not tests_dir.exists():
        warnings.append("No tests/ directory found")
    else:
        console.print("✓ Found tests/ directory")

    # Summary
    console.print()
    if errors:
        console.print(
            Panel(
                "\n".join(f"✗ {e}" for e in errors),
                title="[bold red]Errors[/bold red]",
                border_style="red",
            )
        )

    if warnings:
        console.print(
            Panel(
                "\n".join(f"⚠ {w}" for w in warnings),
                title="[bold yellow]Warnings[/bold yellow]",
                border_style="yellow",
            )
        )

    if not errors and not warnings:
        console.print(
            Panel(
                "[bold green]✓ Module structure is valid![/bold green]",
                border_style="green",
            )
        )

    console.print()
