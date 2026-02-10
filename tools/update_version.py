#!/usr/bin/env python3
"""Update version across all files in the monorepo."""

import re
import sys
from pathlib import Path

try:
    from packaging.version import InvalidVersion, Version
except ImportError:
    print("Error: packaging library not found", file=sys.stderr)
    print("Install it with: pip install packaging", file=sys.stderr)
    sys.exit(1)


def update_version(version: str) -> None:
    """Update version in all relevant files.

    Args:
        version: The version string (e.g., "0.2.21")
    """
    if not version:
        print("Error: Version is required", file=sys.stderr)
        sys.exit(1)

    # Validate version format using packaging.version
    try:
        parsed_version = Version(version)
        # Normalize the version string
        version = str(parsed_version)
    except InvalidVersion:
        print(f"Error: Invalid version format: {version}", file=sys.stderr)
        print("Expected format: PEP 440 compliant version (e.g., 0.2.21)", file=sys.stderr)
        sys.exit(1)

    root = Path(__file__).parent.parent
    files_to_update = [
        # Single source of truth for Python version
        (
            root / "src/hildie/_version.py",
            lambda content: re.sub(
                r'__version__ = "[0-9.]+"', f'__version__ = "{version}"', content
            ),
        ),
        # BUILD.bazel for Bazel builds
        (
            root / "BUILD.bazel",
            lambda content: re.sub(r'version = "[0-9.]+"', f'version = "{version}"', content),
        ),
        # Docs configuration
        (
            root / "docs/source/conf.py",
            lambda content: re.sub(r'release = "[0-9.]+"', f'release = "{version}"', content),
        ),
    ]

    updated_count = 0
    for file_path, updater in files_to_update:
        if not file_path.exists():
            print(f"Warning: File not found: {file_path}", file=sys.stderr)
            continue

        try:
            content = file_path.read_text()
            new_content = updater(content)

            if content != new_content:
                file_path.write_text(new_content)
                print(f"✓ Updated {file_path.relative_to(root)}")
                updated_count += 1
            else:
                print(f"- No change needed in {file_path.relative_to(root)}")
        except Exception as e:
            print(f"Error updating {file_path}: {e}", file=sys.stderr)
            sys.exit(1)

    print(f"\nSuccessfully updated {updated_count} files to version {version}")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: update_version.py <version>", file=sys.stderr)
        print("Example: update_version.py 0.2.21", file=sys.stderr)
        sys.exit(1)

    update_version(sys.argv[1])
