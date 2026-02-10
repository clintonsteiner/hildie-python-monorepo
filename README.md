# Hildie

A Python monorepo built with Bazel.

## Installation

```bash
pip install hildie
```

## Usage

```python
from hildie.hildie_library import add, multiply
from hildie.hildie_app import App
from hildie.hildie_cli.main import cli
from hildie.hildie_archive_git_forks.archiver import GitHubForkArchiver
```

## Development

### Prerequisites

- [Bazelisk](https://github.com/bazelbuild/bazelisk) (recommended) or Bazel 7+
- Python 3.12+

### Build

```bash
bazel build //...
```

### Test

```bash
bazel test //...
```

### Build wheel

```bash
bazel build //:wheel
```

### Run CLIs

```bash
bazel run //:hildie-cli
bazel run //:hildie-archive-git-forks
```

## Project Structure

```
├── src/hildie/                    # All source code
│   ├── hildie_library/            # Core library
│   ├── hildie_app/                # Application
│   ├── hildie_cli/                # CLI tool
│   └── hildie_archive_git_forks/  # Git fork archiver
├── packages/                      # Test directories
│   ├── my-library/tests/
│   ├── my-app/tests/
│   ├── my-cli/tests/
│   └── archive-git-forks/tests/
├── tools/                         # Build macros
├── BUILD.bazel                    # Root build file
└── MODULE.bazel                   # Bazel module definition
```

## Publishing

Push a version tag to publish to PyPI:

```bash
git tag v0.2.0
git push origin v0.2.0
```

The version is automatically extracted from the tag.

## Documentation

Full documentation is available in the `docs/` directory. To build and view:

```bash
# Install documentation dependencies
uv pip install -e ".[docs]"

# Build the docs
cd docs
make html

# Open in browser
open build/html/index.html
```

The documentation includes the story behind the name "Hildie" - since all the good package names were taken, this project is named after Hildie, the best dog!

## License

MIT
