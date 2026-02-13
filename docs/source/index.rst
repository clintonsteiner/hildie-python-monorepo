Welcome to Hildie's Documentation!
===================================

.. image:: _static/hildie.png
   :width: 300px
   :align: center
   :alt: Hildie the dog

Hildie is a Python monorepo containing a collection of utilities and tools.

.. image:: https://img.shields.io/pypi/v/hildie.svg
   :alt: PyPI Version
.. image:: https://img.shields.io/pypi/v/hildie
   :alt: Python Versions
.. image:: https://img.shields.io/github/actions/workflow/status/clintonsteiner/hildies-python-monorepo/bazel.yml?branch=master&label=passing&color=brightgreen
   :alt: Build Status
.. image:: https://img.shields.io/github/license/clintonsteiner/hildies-python-monorepo
   :alt: License

.. note::
   **Why "Hildie"?** All the good package names were taken, so this project is named
   after Hildie, the best dog. See :doc:`about` for the full story!

.. toctree::
   :maxdepth: 2
   :caption: Contents:

   about
   installation
   packages
   api

Quick Start
-----------

Install the package:

.. code-block:: bash

   pip install hildie

Or using uv:

.. code-block:: bash

   uv pip install hildie

Packages
--------

This monorepo contains several packages:

* **check-unittest-super** - Pre-commit hook enforcing super() call ordering in unittest
* **archive-git-forks** - Tools for archiving Git fork repositories
* **my-app** - Application utilities
* **my-cli** - Command-line interface tools
* **my-library** - Core library utilities

See the :doc:`packages` page for detailed information about each package.

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
