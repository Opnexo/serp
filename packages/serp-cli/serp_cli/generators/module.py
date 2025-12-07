"""
Module generator
"""

from datetime import datetime
from pathlib import Path

from serp_cli.generators.base import BaseGenerator


class ModuleGenerator(BaseGenerator):
    """Generator for complete SERP modules"""

    def generate(
        self, name: str, description: str = "", author: str = "", **kwargs
    ) -> Path:
        """
        Generate a complete module structure.

        Args:
            name: Module name (e.g., "serp-inventory")
            description: Module description
            author: Author name

        Returns:
            Path to the generated module directory
        """
        # Ensure serp- prefix
        if not name.startswith("serp-"):
            name = f"serp-{name}"

        module_slug = name.replace("-", "_")
        module_display_name = name.replace("serp-", "").replace("-", " ").title()

        context = {
            "module_name": name,
            "module_slug": module_slug,
            "module_display_name": module_display_name,
            "description": description or f"SERP {module_display_name} module",
            "author": author or "Your Name",
            "year": datetime.now().year,
        }

        # Create module directory
        output_dir = Path.cwd() / name
        output_dir.mkdir(exist_ok=True)

        # Generate pyproject.toml
        pyproject_content = self.render_template("module/pyproject.toml.j2", context)
        self.write_file(output_dir / "pyproject.toml", pyproject_content)

        # Generate README.md
        readme_content = self.render_template("module/README.md.j2", context)
        self.write_file(output_dir / "README.md", readme_content)

        # Generate __init__.py
        init_content = self.render_template("module/__init__.py.j2", context)
        self.write_file(output_dir / module_slug / "__init__.py", init_content)

        # Create DDD directory structure
        directories = [
            f"{module_slug}/Domain/Entities",
            f"{module_slug}/Domain/ValueObjects",
            f"{module_slug}/Domain/Repositories",
            f"{module_slug}/Domain/Services",
            f"{module_slug}/Application/Services",
            f"{module_slug}/Application/DTOs",
            f"{module_slug}/Infrastructure/Repositories",
            f"{module_slug}/Infrastructure/Persistence",
            f"{module_slug}/Interfaces/API",
            f"{module_slug}/Interfaces/Permissions",
            f"{module_slug}/UI/views",
            f"{module_slug}/UI/components",
            "tests/test_domain",
            "tests/test_application",
            "tests/test_api",
        ]

        for directory in directories:
            dir_path = output_dir / directory
            dir_path.mkdir(parents=True, exist_ok=True)
            # Create __init__.py files
            if not directory.startswith("tests"):
                (dir_path / "__init__.py").write_text(
                    '"""\nPackage initialization\n"""\n'
                )

        # Create .gitignore
        gitignore_content = """__pycache__/
*.py[cod]
*$py.class
*.so
.Python
build/
dist/
*.egg-info/
.env
.venv
venv/
"""
        self.write_file(output_dir / ".gitignore", gitignore_content)

        return output_dir
