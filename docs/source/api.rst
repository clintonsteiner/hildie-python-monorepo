API Reference
=============

This section will contain the API documentation for Hildie packages.

.. note::
   API documentation will be auto-generated once the packages are installed.
   For now, see the source code in the ``packages/`` directory.

check-unittest-super
--------------------

``src/hildie/check_unittest_super.py``

.. code-block:: text

   check_file(filepath: str) -> list[str]
       Parse filepath and return a list of error strings for any setUp/tearDown
       methods where super() is not the last statement.

   fix_file(filepath: str) -> tuple[list[str], bool]
       Fix violations in filepath in place.
       Returns (unfixable_errors, was_modified).

   is_unittest_subclass(node: ast.ClassDef) -> bool
       Return True if the class inherits from unittest.TestCase.

   is_super_call(stmt, method_name, class_node) -> bool
       Return True if stmt is an accepted super() call for method_name.

archive-git-forks
-----------------

Tools for archiving Git fork repositories.

my-library
----------

Core library functions and utilities.

my-cli
------

Command-line interface tools.

my-app
------

Application utilities and helpers.
