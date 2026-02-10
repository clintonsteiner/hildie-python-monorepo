<h1 align="center">Hildie</h1>

<p align="center">
  <em>A Python monorepo built with Bazel, named after the best dog.</em>
</p>

<p align="center">
  <a href="https://pypi.org/project/hildie/"><img src="https://img.shields.io/pypi/v/hildie?color=blue" alt="PyPI"></a>
  <a href="https://pypi.org/project/hildie/"><img src="https://img.shields.io/badge/python-3.11%2B-blue" alt="Python 3.11+"></a>
  <a href="https://github.com/clintonsteiner/python-monorepo/actions"><img src="https://github.com/clintonsteiner/python-monorepo/actions/workflows/bazel.yml/badge.svg" alt="Build"></a>
  <a href="https://github.com/clintonsteiner/python-monorepo/blob/master/LICENSE"><img src="https://img.shields.io/badge/license-MIT-green" alt="License"></a>
</p>

---

## About

**Hildie** is a collection of Python utilities and tools, packaged as a single installable module. This project demonstrates a modern Python monorepo structure using [Bazel](https://bazel.build/) for builds, testing, and publishing.

Why "Hildie"? Because all the good package names were taken, so this project is named after Hildie — the adorable pup you see above, peacefully napping with her favorite stuffed horse.

## Installation

```bash
pip install hildie
```

## Features

- **Modular Design**: Multiple sub-packages under a single namespace
- **Bazel Build System**: Fast, reproducible builds with caching
- **Automated Publishing**: Tag a release and it's automatically published to PyPI
- **Fully Tested**: Comprehensive test coverage across all packages

## Packages

| Package | Description |
|---------|-------------|
| `hildie.hildie_library` | Core utility functions for math operations |
| `hildie.hildie_app` | Application components for data processing |
| `hildie.hildie_cli` | Command-line interface tools |
| `hildie.hildie_archive_git_forks` | Utility for archiving GitHub forks |

## Quick Start

### Basic Usage

```python
from hildie.hildie_library import add, multiply

# Simple math operations
result = add(2, 3)      # Returns: 5
product = multiply(4, 5) # Returns: 20
```

### Using the App

```python
from hildie.hildie_app import App

app = App()
result = app.process_numbers([1, 2, 3, 4, 5])
print(result)  # {'sum': 15, 'product': 120}
```

### CLI Tools

```bash
# After installing hildie
python -m hildie.hildie_cli --help
```

### GitHub Fork Archiver

```python
from hildie.hildie_archive_git_forks.archiver import GitHubForkArchiver

archiver = GitHubForkArchiver(token="your-github-token")
archiver.archive_forks("username")
```

## API Reference

### hildie.hildie_library

| Function | Description |
|----------|-------------|
| `add(a, b)` | Add two numbers together |
| `multiply(a, b)` | Multiply two numbers |

### hildie.hildie_app

| Class | Description |
|-------|-------------|
| `App` | Main application class for processing data |

### hildie.hildie_archive_git_forks

| Class | Description |
|-------|-------------|
| `GitHubForkArchiver` | Archive GitHub forks to local storage |

## Development

### Prerequisites

- [Bazelisk](https://github.com/bazelbuild/bazelisk) (recommended) or Bazel 7+
- Python 3.11+

### Building

```bash
# Build all targets
bazel build //...

# Build the wheel
bazel build //:wheel
```

### Testing

```bash
# Run all tests
bazel test //...
```

### Running CLIs

```bash
bazel run //:hildie-cli
bazel run //:hildie-archive-git-forks
```

## Project Structure

```
hildie/
├── src/hildie/                    # Source code
│   ├── __init__.py
│   ├── hildie_library/            # Core library
│   ├── hildie_app/                # Application
│   ├── hildie_cli/                # CLI tools
│   └── hildie_archive_git_forks/  # Fork archiver
├── packages/                      # Test suites
│   ├── my-library/tests/
│   ├── my-app/tests/
│   ├── my-cli/tests/
│   └── archive-git-forks/tests/
├── tools/                         # Build macros
├── BUILD.bazel                    # Root build file
├── MODULE.bazel                   # Bazel dependencies
└── pyproject.toml                 # Project metadata
```

## Publishing

Releases are automated via GitHub Actions. To publish a new version:

```bash
git tag v0.2.0
git push origin v0.2.0
```

The workflow will:
1. Run all tests
2. Build the wheel with the tagged version
3. Publish to PyPI
4. Create a GitHub release

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Run tests (`bazel test //...`)
4. Commit your changes
5. Push to the branch
6. Open a Pull Request

## Maintainer

**Clinton Steiner** — [clintonsteiner@gmail.com](mailto:clintonsteiner@gmail.com)

- GitHub: [@clintonsteiner](https://github.com/clintonsteiner)

## License

This project is licensed under the MIT License — see the [LICENSE](LICENSE) file for details.

---

<p align="center">
  <em>Made by Clinton, inspired by Hildie</em>
</p>
<p align="center">
  <img src="https://raw.githubusercontent.com/clintonsteiner/python-monorepo/refs/heads/master/hildie.png" alt="Hildie the Dog" width="400"/>
</p>
