#!/usr/bin/env python3
"""
Template setup script for Python monorepo.
Helps customize the template for a new project.
"""

import os
import re
import shutil
from pathlib import Path


def get_input(prompt: str, default: str = "") -> str:
    """Get user input with optional default."""
    if default:
        display_prompt = f"{prompt} [{default}]: "
    else:
        display_prompt = f"{prompt}: "

    value = input(display_prompt).strip()
    return value if value else default


def replace_in_file(file_path: Path, replacements: dict[str, str]) -> None:
    """Replace text in a file."""
    try:
        content = file_path.read_text()
        for old, new in replacements.items():
            content = content.replace(old, new)
        file_path.write_text(content)
    except UnicodeDecodeError:
        # Skip binary files
        pass


def rename_directory(old_path: Path, new_path: Path) -> None:
    """Rename a directory."""
    if old_path.exists():
        if new_path.exists():
            shutil.rmtree(new_path)
        old_path.rename(new_path)


def setup_template() -> None:
    """Main setup function."""
    print("\n" + "=" * 60)
    print("Python Monorepo Template Setup")
    print("=" * 60 + "\n")

    # Get user inputs
    print("Project Configuration:")
    project_name = get_input("Project name", "my-project")
    author_name = get_input("Author name", "Developer")
    author_email = get_input("Author email", "dev@example.com")

    print("\nPackage Names (leave blank to use defaults):")
    library_name = get_input("Library package name", "my-library")
    app_name = get_input("App package name", "my-app")
    cli_name = get_input("CLI package name", "my-cli")

    # Convert names to valid Python module names
    library_module = library_name.replace("-", "_")
    app_module = app_name.replace("-", "_")
    cli_module = cli_name.replace("-", "_")

    # Build replacements dictionary
    replacements = {
        "my-library": library_name,
        "my_library": library_module,
        "my-app": app_name,
        "my_app": app_module,
        "my-cli": cli_name,
        "my_cli": cli_module,
        "python-monorepo": project_name,
        "Developer": author_name,
        "dev@example.com": author_email,
        "A Python monorepo using uv workspaces": f"{project_name} - Python monorepo with uv",
    }

    root_dir = Path(".")

    print("\nApplying changes...\n")

    # Replace in all text files
    for file_path in root_dir.rglob("*"):
        if file_path.is_file() and not should_skip_file(file_path):
            try:
                replace_in_file(file_path, replacements)
                print(f"✓ {file_path.relative_to(root_dir)}")
            except Exception as e:
                print(f"✗ {file_path.relative_to(root_dir)}: {e}")

    # Rename package directories
    packages_dir = root_dir / "packages"

    if library_name != "my-library" and (packages_dir / "my-library").exists():
        print(f"\nRenaming my-library → {library_name}")
        rename_directory(packages_dir / "my-library", packages_dir / library_name)

    if app_name != "my-app" and (packages_dir / "my-app").exists():
        print(f"Renaming my-app → {app_name}")
        rename_directory(packages_dir / "my-app", packages_dir / app_name)

    if cli_name != "my-cli" and (packages_dir / "my-cli").exists():
        print(f"Renaming my-cli → {cli_name}")
        rename_directory(packages_dir / "my-cli", packages_dir / cli_name)

    # Rename source directories
    for package_dir in packages_dir.iterdir():
        if package_dir.is_dir():
            src_dir = package_dir / "src"
            if src_dir.exists():
                for old_name, new_name in [
                    ("my_library", library_module),
                    ("my_app", app_module),
                    ("my_cli", cli_module),
                ]:
                    old_module = src_dir / old_name
                    new_module = src_dir / new_name
                    if old_module.exists() and old_name != new_name:
                        print(f"Renaming {old_module.name} → {new_module.name}")
                        rename_directory(old_module, new_module)

    # Cleanup template files
    print("\nCleaning up template files...")
    template_files = ["TEMPLATE.md", "setup_template.py"]
    for filename in template_files:
        file_path = root_dir / filename
        if file_path.exists():
            file_path.unlink()
            print(f"✓ Removed {filename}")

    print("\n" + "=" * 60)
    print("Template setup complete!")
    print("=" * 60)
    print("\nNext steps:")
    print("1. Review and update README.md with your project description")
    print("2. Update package descriptions in each pyproject.toml")
    print("3. Update the LICENSE file if using a different license")
    print("4. Run: uv sync")
    print("5. Start developing!\n")


def should_skip_file(file_path: Path) -> bool:
    """Check if a file should be skipped during replacement."""
    skip_patterns = {
        ".git",
        "__pycache__",
        ".pytest_cache",
        ".ruff_cache",
        ".uv",
        "*.pyc",
        ".lock",
        "node_modules",
        ".venv",
    }

    # Check against patterns
    for pattern in skip_patterns:
        if pattern in file_path.parts:
            return True

    # Skip binary and large files
    if file_path.suffix in {".png", ".jpg", ".jpeg", ".gif", ".pdf", ".bin", ".so"}:
        return True

    return False


if __name__ == "__main__":
    try:
        setup_template()
    except KeyboardInterrupt:
        print("\n\nSetup cancelled.")
    except Exception as e:
        print(f"\nError: {e}")
        exit(1)
