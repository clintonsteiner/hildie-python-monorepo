# Version Management

This document describes how versions are managed in the Hildie monorepo.

## Single Source of Truth

Version information is stored in **three places only**:

1. **`src/hildie/_version.py`** - Python source of truth (all packages import from here)
2. **`BUILD.bazel`** - Bazel build configuration (for wheel generation)
3. **`docs/source/conf.py`** - Documentation configuration

All package `__init__.py` files import `__version__` from `src/hildie/_version.py`, eliminating duplication.

## Manual Version Updates

To update the version manually:

```bash
python3 tools/update_version.py <version>
```

Example:
```bash
python3 tools/update_version.py 0.2.22
```

The script will:
- Validate the version format (semantic versioning: X.Y.Z)
- Update all three version locations
- Report which files were changed

## Automated Release Process

When you push a new git tag (e.g., `v0.2.22`), the GitHub Actions workflow automatically:

1. Extracts the version from the tag (strips the `v` prefix)
2. Runs `tools/update_version.py` to update all version files
3. Builds the wheel with the correct version
4. Publishes to PyPI
5. Creates a GitHub release

### Creating a New Release

```bash
# Create and push a new tag
git tag v0.2.22
git push origin v0.2.22
```

The workflow takes care of the rest!

## Version File Structure

```
src/hildie/
├── _version.py              # Single source of truth ✓
├── __init__.py              # Imports from _version.py
├── hildie_app/
│   └── __init__.py         # Imports from _version.py
├── hildie_cli/
│   └── __init__.py         # Imports from _version.py
└── ...
```

## Benefits

- **No duplication**: Version defined in only one Python file
- **Automatic sync**: Release workflow updates all files
- **Single script**: Easy to maintain and extend
- **Type-safe imports**: All packages import from the same source
