"""
Service generator
"""

from pathlib import Path

from serp_cli.generators.base import BaseGenerator
from serp_cli.utils.naming import to_pascal_case, to_snake_case


class ServiceGenerator(BaseGenerator):
    """Generator for domain and application services"""

    def generate(self, name: str, service_type: str, module: str, **kwargs) -> Path:
        """
        Generate a service.

        Args:
            name: Service name (e.g., "CustomerService")
            service_type: "domain" or "application"
            module: Module name

        Returns:
            Path to the generated service file
        """
        # Ensure name ends with "Service"
        if not name.endswith("Service"):
            name = f"{name}Service"

        context = {
            "service_name": to_pascal_case(name),
            "service_name_snake": to_snake_case(name),
            "service_type": service_type,
            "module": module,
            "is_domain": service_type == "domain",
            "is_application": service_type == "application",
        }

        content = self.render_template("service.py.j2", context)

        module_path = self.get_module_path(module)

        if service_type == "domain":
            output_path = (
                module_path / "Domain" / "Services" / f"{to_snake_case(name)}.py"
            )
        else:
            output_path = (
                module_path / "Application" / "Services" / f"{to_snake_case(name)}.py"
            )

        return self.write_file(output_path, content)
