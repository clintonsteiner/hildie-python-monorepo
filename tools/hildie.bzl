"""Hildie-specific Bazel macros."""

load("@rules_python//python:defs.bzl", "py_binary")

def hildie_cli(name, module):
    """Creates a CLI binary from a hildie module.

    Args:
        name: Binary name (e.g., "hildie-cli")
        module: Module path (e.g., "hildie_cli")
    """
    py_binary(
        name = name,
        srcs = ["src/hildie/{}/main.py".format(module)],
        main = "src/hildie/{}/main.py".format(module),
        deps = ["//:hildie"],
    )

def all_package_tests(name, packages):
    """Creates a test_suite that includes all package tests.

    Args:
        name: Name of the test suite
        packages: List of package names (e.g., ["my-app", "my-cli"])
    """
    native.test_suite(
        name = name,
        tests = ["//packages/{}:tests".format(pkg) for pkg in packages],
    )
