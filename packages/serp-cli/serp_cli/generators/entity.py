"""
Entity generator
"""

from pathlib import Path
from typing import Dict, List

from serp_cli.generators.base import BaseGenerator
from serp_cli.utils.naming import to_pascal_case, to_snake_case


class EntityGenerator(BaseGenerator):
    """Generator for domain entities"""

    def generate(
        self,
        name: str,
        module: str,
        fields: List[Dict[str, str]] = None,
        value_objects: List[str] = None,
        **kwargs,
    ) -> Path:
        """
        Generate a domain entity.

        Args:
            name: Entity name (e.g., "Customer")
            module: Module name (e.g., "serp-crm")
            fields: List of field definitions [{"name": "email", "type": "str"}]
            value_objects: List of value object names to create

        Returns:
            Path to the generated entity file
        """
        fields = fields or []
        value_objects = value_objects or []

        # Prepare context
        context = {
            "entity_name": to_pascal_case(name),
            "entity_name_snake": to_snake_case(name),
            "module": module,
            "fields": fields,
            "value_objects": value_objects,
            "has_fields": len(fields) > 0,
        }

        # Render template
        content = self.render_template("entity.py.j2", context)

        # Determine output path
        module_path = self.get_module_path(module)
        output_path = module_path / "Domain" / "Entities" / f"{to_snake_case(name)}.py"

        # Write file
        return self.write_file(output_path, content)
