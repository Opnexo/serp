"""
Repository generator
"""

from pathlib import Path
from typing import List

from serp_cli.generators.base import BaseGenerator
from serp_cli.utils.naming import to_pascal_case, to_snake_case


class RepositoryGenerator(BaseGenerator):
    """Generator for repositories"""

    def generate(
        self,
        name: str,
        entity: str,
        module: str,
        custom_methods: List[str] = None,
        **kwargs,
    ) -> Path:
        """
        Generate a repository.

        Args:
            name: Repository name (e.g., "CustomerRepository")
            entity: Entity name (e.g., "Customer")
            module: Module name
            custom_methods: List of custom method names

        Returns:
            Path to the generated repository file
        """
        custom_methods = custom_methods or []

        # Ensure name ends with "Repository"
        if not name.endswith("Repository"):
            name = f"{name}Repository"

        context = {
            "repository_name": to_pascal_case(name),
            "entity_name": to_pascal_case(entity),
            "entity_name_snake": to_snake_case(entity),
            "module": module,
            "custom_methods": custom_methods,
        }

        content = self.render_template("repository.py.j2", context)

        module_path = self.get_module_path(module)
        output_path = (
            module_path / "Domain" / "Repositories" / f"{to_snake_case(name)}.py"
        )

        return self.write_file(output_path, content)
