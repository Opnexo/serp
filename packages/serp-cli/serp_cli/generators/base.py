"""
Base generator class
"""

from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any, Dict

import inflect
from jinja2 import ChoiceLoader, Environment, FileSystemLoader, PackageLoader

from serp_cli.utils.naming import to_pascal_case, to_snake_case


class BaseGenerator(ABC):
    """
    Base class for all code generators.

    Provides template rendering and file writing utilities.
    """

    def __init__(self):
        # Setup Jinja2 environment with multiple loaders
        self.inflect_engine = inflect.engine()

        # Try to load custom templates from ~/.serp/templates, fall back to package templates
        loaders = []

        # User templates
        user_templates = Path.home() / ".serp" / "templates"
        if user_templates.exists():
            loaders.append(FileSystemLoader(str(user_templates)))

        # Package templates
        loaders.append(PackageLoader("serp_cli", "templates"))

        self.env = Environment(
            loader=ChoiceLoader(loaders),
            trim_blocks=True,
            lstrip_blocks=True,
        )

        # Add custom filters
        self.env.filters["snake_case"] = to_snake_case
        self.env.filters["pascal_case"] = to_pascal_case
        self.env.filters["plural"] = self.inflect_engine.plural
        self.env.filters["singular"] = self.inflect_engine.singular_noun

    @abstractmethod
    def generate(self, **kwargs) -> Path:
        """
        Generate code based on provided parameters.

        Returns:
            Path to the generated file
        """
        raise NotImplementedError

    def render_template(self, template_name: str, context: Dict[str, Any]) -> str:
        """
        Render a Jinja2 template with the given context.

        Args:
            template_name: Name of the template file
            context: Dictionary of template variables

        Returns:
            Rendered template string
        """
        template = self.env.get_template(template_name)
        return template.render(**context)

    def write_file(self, path: Path, content: str) -> Path:
        """
        Write content to a file, creating directories if needed.

        Args:
            path: Path to write to
            content: Content to write

        Returns:
            Path to the written file
        """
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content)
        return path

    def get_module_path(self, module: str) -> Path:
        """
        Get the path to a module directory.

        Args:
            module: Module name (e.g., "serp-crm")

        Returns:
            Path to the module directory
        """
        module_name = module.replace("-", "_")

        # Try to find the module in common locations
        search_paths = [
            Path.cwd() / module_name,
            Path.cwd() / "modules" / module / module_name,
            Path.cwd() / ".." / module / module_name,
        ]

        for path in search_paths:
            if path.exists():
                return path

        # Default to current directory
        return Path.cwd() / module_name
