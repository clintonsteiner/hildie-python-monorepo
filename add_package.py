#!/usr/bin/env python3
"""Utility to easily add a new package to the Python monorepo."""

import argparse
import sys
from pathlib import Path
from textwrap import dedent


def create_package(package_name: str, description: str | None = None) -> None:
    """Create a new package in the monorepo.

    Args:
        package_name: The name of the package (e.g., 'my-new-package')
        description: Optional description for the package
    """
    # Normalize package name
    package_dir_name = package_name.replace("-", "_")

    # Create package directory structure
    root = Path(__file__).parent
    package_path = root / "packages" / package_name
    src_path = package_path / "src" / package_dir_name
    tests_path = package_path / "tests"

    # Create directories
    src_path.mkdir(parents=True, exist_ok=True)
    tests_path.mkdir(parents=True, exist_ok=True)

    print(f"📦 Creating package: {package_name}")

    # Create pyproject.toml
    pyproject_content = dedent(f'''\
        [build-system]
        requires = ["hatchling"]
        build-backend = "hatchling.build"

        [project]
        name = "{package_name}"
        version = "0.1.0"
        description = "{description or 'A package in the monorepo'}"
        readme = "README.md"
        requires-python = ">=3.11"
        authors = [{{name = "Developer", email = "dev@example.com"}}]
        license = {{text = "MIT"}}
        keywords = ["example"]

        [project.urls]
        Homepage = "https://github.com/example/python-monorepo"
        Repository = "https://github.com/example/python-monorepo"

        [tool.hatch.build.targets.wheel]
        packages = ["src/{package_dir_name}"]

        [dependency-groups]
        dev = [
            "pytest>=7.4.0",
            "pytest-cov>=4.1.0",
        ]
        ''')

    (package_path / "pyproject.toml").write_text(pyproject_content)
    print(f"  ✓ Created pyproject.toml")

    # Create __init__.py
    (src_path / "__init__.py").write_text('"""Package initialization."""\n\n__version__ = "0.1.0"\n')
    print(f"  ✓ Created {package_dir_name}/__init__.py")

    # Create test file
    test_file = tests_path / "test_example.py"
    test_content = dedent(f'''\
        """Example tests for {package_name}."""


        def test_example():
            """Example test."""
            assert True
        ''')
    test_file.write_text(test_content)
    print(f"  ✓ Created test_example.py")

    # Create README
    readme_content = dedent(f'''\
        # {package_name}

        {description or 'A package in the monorepo'}

        ## Installation

        ```bash
        uv pip install -e .
        ```

        ## Development

        ```bash
        uv sync
        pytest
        ```
        ''')
    (package_path / "README.md").write_text(readme_content)
    print(f"  ✓ Created README.md")

    # Update root pyproject.toml
    root_pyproject = root / "pyproject.toml"
    content = root_pyproject.read_text()

    # Check if workspace entry already exists
    if f'{{ path = "packages/{package_name}" }}' not in content:
        # Find the workspace section and add the new package
        lines = content.split('\n')
        for i, line in enumerate(lines):
            if 'workspace = [' in line:
                # Find the closing bracket
                for j in range(i + 1, len(lines)):
                    if lines[j].strip() == ']':
                        # Insert new package entry before closing bracket
                        lines.insert(j, f'    {{ path = "packages/{package_name}" }},')
                        break
                break

        root_pyproject.write_text('\n'.join(lines))
        print(f"  ✓ Updated root pyproject.toml")

    print(f"\n✅ Package '{package_name}' created successfully!\n")
    print(f"Location: {package_path}")
    print(f"Next steps:")
    print(f"  1. Run: uv sync")
    print(f"  2. Edit {package_path}/README.md")
    print(f"  3. Add your code to src/{package_dir_name}/")
    print(f"  4. Add tests to tests/")


def main():
    parser = argparse.ArgumentParser(
        description="Add a new package to the Python monorepo",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=dedent("""\
            Examples:
              python add_package.py my-new-package
              python add_package.py my-new-package -d "My package description"
            """),
    )
    parser.add_argument("package_name", help="Name of the new package (e.g., 'my-new-package')")
    parser.add_argument(
        "-d", "--description",
        help="Description of the package",
        default=None,
    )

    args = parser.parse_args()

    try:
        create_package(args.package_name, args.description)
    except Exception as e:
        print(f"❌ Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
