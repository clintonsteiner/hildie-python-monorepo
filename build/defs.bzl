"""Shared build definitions for the Hildie monorepo."""

load("@rules_python//python:defs.bzl", "py_library", "py_test")

def hildie_py_library(name, **kwargs):
    """Creates a Python library with standard Hildie settings."""
    py_library(
        name = name,
        **kwargs
    )

def hildie_py_test(name, srcs, deps = [], data = [], **kwargs):
    """Creates a pytest-based test target.

    Args:
        name: Name of the test target
        srcs: Test source files
        deps: Dependencies for the tests
        data: Additional data files
        **kwargs: Additional arguments passed to py_test
    """
    # Create a test for each test file
    for src in srcs:
        test_name = src.replace("/", "_").replace(".py", "")
        py_test(
            name = test_name,
            srcs = [src],
            main = src,
            deps = deps + ["@pip//pytest"],
            data = data,
            **kwargs
        )

    # Create a test suite that includes all tests
    native.test_suite(
        name = name,
        tests = [":" + src.replace("/", "_").replace(".py", "") for src in srcs],
    )
