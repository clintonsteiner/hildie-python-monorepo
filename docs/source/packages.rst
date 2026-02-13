Packages
========

The Hildie monorepo contains several packages, each serving a specific purpose.

check-unittest-super
--------------------

Pre-commit hook that enforces ``super()`` is the **last** call in
``setUp``, ``tearDown``, ``setUpClass``, and ``tearDownClass`` for
``unittest.TestCase`` subclasses.

**Purpose:** Prevent subtle ordering bugs caused by running base-class setup
before test-specific state is initialised.

**Location:** ``packages/check-unittest-super``

**Source:** ``src/hildie/check_unittest_super.py``

Use in other repos by referencing this repo's tag:

.. code-block:: yaml

   - repo: https://github.com/clintonsteiner/hildies-python-monorepo
     rev: v0.22.23
     hooks:
       - id: unittest-super-last

Optional flags:

- ``--fix`` — auto-correct violations in place (moves or inserts the ``super()`` call)
- ``--profile`` — print per-file millisecond timing to stderr

archive-git-forks
-----------------

Tools for archiving and managing Git fork repositories.

**Purpose:** Helps manage and archive Git forks when you need to preserve copies of
forked repositories.

**Location:** ``packages/archive-git-forks``

my-app
------

Application utilities and helpers.

**Purpose:** Common utilities for building Python applications.

**Location:** ``packages/my-app``

my-cli
------

Command-line interface tools and utilities.

**Purpose:** Tools for building CLI applications with Python.

**Location:** ``packages/my-cli``

my-library
----------

Core library functions and utilities.

**Purpose:** General-purpose utilities and helper functions used across the monorepo.

**Location:** ``packages/my-library``

Package Structure
-----------------

Each package follows a consistent structure:

.. code-block:: text

   packages/<package-name>/
   ├── BUILD.bazel          # Bazel build configuration
   ├── pyproject.toml       # Package metadata
   ├── src/                 # Source code
   │   └── <package>/
   │       └── __init__.py
   └── tests/               # Tests
       └── test_*.py

Building Packages
-----------------

Using Bazel:

.. code-block:: bash

   # Build all packages
   bazel build //...

   # Build a specific package
   bazel build //packages/my-library:my-library

   # Run tests
   bazel test //...

Using standard Python tools:

.. code-block:: bash

   # From a package directory
   cd packages/my-library
   uv pip install -e .
