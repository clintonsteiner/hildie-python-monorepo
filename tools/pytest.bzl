"""Pytest test macros for Hildie monorepo."""

load("@rules_python//python:defs.bzl", "py_test")

def pytest_tests(name, srcs, deps = [], **kwargs):
    """Creates individual py_test targets for each test file and a test_suite.

    Args:
        name: Base name for the test suite
        srcs: List of test source files (use glob)
        deps: Dependencies for all tests
        **kwargs: Additional arguments passed to each py_test
    """
    test_targets = []

    for src in srcs:
        # Extract test name from filename: tests/test_foo.py -> test_foo
        test_name = src.replace("tests/", "").replace(".py", "").replace("/", "_")
        test_targets.append(":" + test_name)

        py_test(
            name = test_name,
            srcs = [src],
            main = src,
            deps = deps + ["@pip//pytest"],
            args = ["-v"],
            **kwargs
        )

    native.test_suite(
        name = name,
        tests = test_targets,
    )

def package_tests(deps = None, **kwargs):
    """Standard test target for a package. Auto-discovers tests/**/test_*.py files.

    Args:
        deps: Additional dependencies beyond //:hildie
        **kwargs: Additional arguments passed to pytest_tests
    """
    all_deps = ["//:hildie"] + (deps if deps else [])

    pytest_tests(
        name = "tests",
        srcs = native.glob(["tests/**/test_*.py"]),
        deps = all_deps,
        **kwargs
    )
