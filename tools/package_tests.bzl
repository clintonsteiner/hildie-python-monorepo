"""Macro for creating standard package test targets."""

load("//tools:pytest.bzl", "pytest_tests")

def package_tests(deps = None, **kwargs):
    """Creates standard test target for a package.

    Args:
        deps: Additional dependencies beyond the default hildie library
        **kwargs: Additional arguments passed to pytest_tests
    """
    default_deps = ["//:hildie"]

    if deps:
        all_deps = default_deps + deps
    else:
        all_deps = default_deps

    pytest_tests(
        name = "tests",
        srcs = native.glob(["tests/**/test_*.py"]),
        deps = all_deps,
        **kwargs
    )
