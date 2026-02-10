# Python Monorepo with uv Workspaces

A modern Python monorepo template using [uv](https://github.com/astral-sh/uv) for workspace management and dependency resolution. This template supports libraries, applications, and CLI tools with shared tooling and configuration.

> **Using this as a template?** See [TEMPLATE.md](TEMPLATE.md) for setup instructions and the automated setup script.

## Features

- **Unified Workspace Management**: Single `uv` workspace for all packages
- **Shared Tooling**: Centralized linting (ruff), testing (pytest), and CI/CD configuration
- **Independent Publishing**: Each package can be published separately to PyPI
- **Cross-Package Dependencies**: Packages can depend on each other using workspace sources
- **Efficient CI/CD**: GitHub Actions workflows for linting, testing, and publishing
- **Modern Python Packaging**: PEP 621 (pyproject.toml) and PEP 735 (dependency-groups)

## Project Structure

```
python-monorepo/
├── .github/workflows/          # GitHub Actions workflows
│   ├── lint.yml               # Linting workflow
│   ├── test.yml               # Testing workflow
│   └── publish.yml            # Publishing workflow
├── packages/                   # Workspace members
│   ├── my-library/            # Reusable library
│   │   ├── src/my_library/    # Package source code
│   │   ├── tests/             # Package tests
│   │   └── pyproject.toml     # Package configuration
│   ├── my-app/                # Application using the library
│   │   ├── src/my_app/
│   │   ├── tests/
│   │   └── pyproject.toml
│   └── my-cli/                # CLI tool using the library
│       ├── src/my_cli/
│       ├── tests/
│       └── pyproject.toml
├── pyproject.toml             # Root workspace configuration
├── ruff.toml                  # Shared linting configuration
├── .gitignore                 # Git ignore rules
└── README.md                  # This file
```

## Getting Started

### Prerequisites

- Python 3.11 or later
- [uv](https://github.com/astral-sh/uv) (install with `curl -LsSf https://astral.sh/uv/install.sh | sh`)

### Installation

1. Clone the repository:
   ```bash
   git clone <repository-url>
   cd python-monorepo
   ```

2. Sync dependencies:
   ```bash
   uv sync
   ```

   This installs all workspace members and development dependencies in an isolated environment.

## Development

### Running Commands

All commands should be run from the workspace root using `uv run`:

```bash
# Run linting
uv run ruff check .
uv run ruff format .

# Run tests
uv run pytest

# Run tests with coverage
uv run pytest --cov=packages
```

### Working with Specific Packages

To work with a specific package:

```bash
# Install only a specific package
uv sync --package my-library

# Run tests for a specific package
uv run pytest packages/my-library/tests
```

### Adding Dependencies

To add a dependency to a package:

```bash
# Add a regular dependency
uv add -p packages/my-library requests

# Add a development dependency
uv add -p packages/my-library --group dev pytest-mock
```

To add a workspace package as a dependency:

Edit the `dependencies` field in the package's `pyproject.toml`:

```toml
[project]
dependencies = [
    "my-library>=0.1.0",
]
```

The dependency will be resolved from the workspace source automatically.

### Creating a New Package

1. Create the package directory structure:
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
   description = "Description here"
   requires-python = ">=3.11"
   # ... other metadata
   ```

3. Add the package to the root `pyproject.toml`:
   ```toml
   [tool.uv]
   workspace = [
       { path = "packages/my-library" },
       { path = "packages/my-app" },
       { path = "packages/my-cli" },
       { path = "packages/my-new-package" },  # New package
   ]
   ```

4. Run `uv sync` to update the workspace

## Linting and Formatting

Configuration is centralized in `ruff.toml`. All packages use the same linting rules.

```bash
# Check code style
uv run ruff check .

# Format code
uv run ruff format .

# Check formatting without changes
uv run ruff format --check .
```

## Testing

All tests use pytest. Configuration is in the root `pyproject.toml`.

```bash
# Run all tests
uv run pytest

# Run tests for a specific package
uv run pytest packages/my-library

# Run tests with coverage
uv run pytest --cov=packages

# Run a specific test file
uv run pytest packages/my-library/tests/test_example.py
```

## CI/CD

The monorepo includes GitHub Actions workflows:

- **lint.yml**: Runs `ruff check` and `ruff format --check` on every push and PR
- **test.yml**: Runs pytest on Python 3.11, 3.12, and 3.13
- **publish.yml**: Publishes packages to PyPI on version tags

### Publishing a Package

Tag a release with one of these formats:

```bash
# Publish all packages
git tag v0.1.0
git push origin v0.1.0

# Publish a specific package
git tag my-library-v0.1.0
git push origin my-library-v0.1.0
```

The publishing workflow will:
1. Build the package
2. Publish to PyPI using trusted publishing (no secrets required)

## Package Contents

### my-library

A reusable library with basic math functions:

- `add(a, b)`: Add two numbers
- `multiply(a, b)`: Multiply two numbers

### my-app

An application that uses my-library to process lists of numbers:

- `process_numbers(numbers)`: Calculate sum and product of a list

### my-cli

A CLI tool for mathematical operations:

- `my-cli add-numbers A B`: Add two numbers
- `my-cli multiply-numbers A B`: Multiply two numbers
- `my-cli sum-all NUMS...`: Sum multiple numbers
- `my-cli multiply-all NUMS...`: Multiply multiple numbers

## Best Practices

1. **Use workspace dependencies**: When possible, depend on other workspace packages rather than external packages
2. **Consistent versioning**: Keep related packages at similar versions
3. **Shared configuration**: Use the root configuration for common settings
4. **Test coverage**: Write tests for all packages, aim for >80% coverage
5. **Type hints**: Use Python type hints for better IDE support and documentation
6. **Meaningful commits**: Write descriptive commit messages that explain the "why"

## Troubleshooting

### "Module not found" errors

Make sure you've run `uv sync` to install the workspace:

```bash
uv sync
```

### Dependency conflicts

Check the `uv.lock` file is up to date:

```bash
uv lock --upgrade
```

### Tests not discovering

Ensure tests are in the `tests/` directory following the naming convention `test_*.py`.

## Contributing

1. Create a feature branch: `git checkout -b feature/my-feature`
2. Make your changes and add tests
3. Run linting and tests: `uv run ruff check . && uv run pytest`
4. Commit with descriptive messages
5. Push and create a pull request

## License

MIT - See LICENSE file for details

## Resources

- [uv documentation](https://docs.astral.sh/uv/)
- [PEP 735 - Dependency Groups](https://peps.python.org/pep-0735/)
- [PEP 621 - pyproject.toml](https://peps.python.org/pep-0621/)
- [pytest documentation](https://docs.pytest.org/)
- [ruff documentation](https://docs.astral.sh/ruff/)
