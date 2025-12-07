"""
UI View generator
"""

from pathlib import Path

from serp_cli.generators.base import BaseGenerator
from serp_cli.utils.naming import to_pascal_case, to_snake_case


class ViewGenerator(BaseGenerator):
    """Generator for UI views"""

    def generate(
        self,
        name: str,
        module: str,
        route: str = None,
        permission: str = None,
        **kwargs,
    ) -> Path:
        """
        Generate a UI view component.

        Args:
            name: View name (e.g., "CustomerList")
            module: Module name
            route: Route path (e.g., "/customers")
            permission: Required permission

        Returns:
            Path to the generated view file
        """
        route = route or f"/{to_snake_case(name).replace('_', '-')}"

        context = {
            "view_name": to_pascal_case(name),
            "view_name_snake": to_snake_case(name),
            "module": module,
            "route": route,
            "permission": permission,
            "has_permission": permission is not None,
        }

        content = self.render_template("view.tsx.j2", context)

        module_path = self.get_module_path(module)
        output_path = module_path / "UI" / "views" / f"{to_pascal_case(name)}.tsx"

        return self.write_file(output_path, content)
