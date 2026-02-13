Installation
============

From PyPI
---------

Install Hildie using pip:

.. code-block:: bash

   pip install hildie

Or using uv (recommended):

.. code-block:: bash

   uv pip install hildie

From Source
-----------

Clone the repository:

.. code-block:: bash

   git clone https://github.com/clintonsteiner/hildies-python-monorepo.git
   cd hildies-python-monorepo

Install in development mode:

.. code-block:: bash

   uv pip install -e .

Requirements
------------

- Python 3.11 or higher
- pip or uv for package management

Development Requirements
------------------------

For development, you'll need additional tools:

.. code-block:: bash

   # Install development dependencies
   uv pip install -e ".[dev]"

   # Or using pip
   pip install -e ".[dev]"

Development tools used in this project:

- **Bazel** - Build system
- **pytest** - Testing framework
- **ruff** - Linting and formatting
- **pre-commit** - Git hooks for code quality

Verifying Installation
----------------------

After installation, verify that Hildie is installed correctly:

.. code-block:: python

   import hildie
   print(hildie.__version__)
