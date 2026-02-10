# Quick Start Guide

## Installation

```bash
cd /Users/cs/python-monorepo
uv sync
```

## Common Commands

### Linting & Formatting

```bash
# Check code style
uv run ruff check .

# Auto-fix formatting
uv run ruff format .

# Check formatting without changing files
uv run ruff format --check .
```

### Testing

```bash
# Run all tests
uv run pytest

# Run tests with coverage
uv run pytest --cov=packages

# Run tests for a specific package
uv run pytest packages/my-library

# Run a specific test file
uv run pytest packages/my-library/tests/test_example.py

# Run tests with verbose output
uv run pytest -v
```

### Working with the CLI

```bash
# Add two numbers
uv run my-cli add-numbers 10 5

# Multiply two numbers
uv run my-cli multiply-numbers 4 7

# Sum multiple numbers
uv run my-cli sum-all 1 2 3 4 5

# Multiply multiple numbers
uv run my-cli multiply-all 2 3 4
```

### Managing Dependencies

```bash
# Add a dependency to a package
uv add -p packages/my-library requests

# Add a dev dependency
uv add -p packages/my-library --group dev pytest-mock

# Update lockfile
uv lock --upgrade

# Sync with latest lockfile
uv sync
```

### Workspace Information

```bash
# See workspace structure
uv workspace list

# See all packages
cd /Users/cs/python-monorepo && ls -la packages/
```

## Adding a New Package

1. Create directory structure:
   ```bash
   mkdir -p packages/my-new-package/{src/my_new_package,tests}
   ```

2. Create `packages/my-new-package/pyproject.toml`:
   ```toml
   [build-system]
   requires = ["hatchling"]
   build-backend = "hatchling.build"

   [project]
   name = "my-new-package"
   version = "0.1.0"
   description = "Your description"
   requires-python = ">=3.11"
   ```

3. Add to root `pyproject.toml`:
   ```toml
   [tool.uv]
   workspace = [
       { path = "packages/my-library" },
       { path = "packages/my-app" },
       { path = "packages/my-cli" },
       { path = "packages/my-new-package" },  # New
   ]
   ```

4. Run `uv sync` to update

## Publishing a Package

### Tag Format for Publishing

```bash
# Publish all packages
git tag v0.2.0
git push origin v0.2.0

# Publish specific package
git tag my-library-v0.2.0
git push origin my-library-v0.2.0
```

The `publish.yml` workflow will automatically build and publish to PyPI.

## Project Structure Quick Reference

```
python-monorepo/
├── packages/
│   ├── my-library/      # Reusable library (no deps)
│   ├── my-app/          # App depending on my-library
│   └── my-cli/          # CLI depending on my-library + click
├── pyproject.toml       # Workspace config
├── ruff.toml            # Linting config
└── .github/workflows/   # CI/CD workflows
```

## Troubleshooting

**"Module not found" errors:**
```bash
uv sync
```

**Dependency conflicts:**
```bash
uv lock --upgrade
```

**Need to rebuild environment:**
```bash
rm -rf .uv
uv sync
```

## Key Files

- `pyproject.toml` - Workspace definition and shared dev dependencies
- `ruff.toml` - Shared linting and formatting rules
- `.github/workflows/lint.yml` - Automated linting on push/PR
- `README.md` - Full documentation
