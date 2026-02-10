"""Pytest test generation macros."""

load("@rules_python//python:defs.bzl", "py_test")

def pytest_test(name, srcs, deps = [], args = [], **kwargs):
    """Creates a py_test that runs with pytest.

    Args:
        name: Test target name
        srcs: Test source files
        deps: Dependencies
        args: Additional pytest arguments
        **kwargs: Additional py_test arguments
    """
    py_test(
        name = name,
        srcs = srcs,
        main = srcs[0] if len(srcs) == 1 else None,
        deps = deps + ["@pip//pytest"],
        args = ["-v"] + args + ["$(location {})".format(src) for src in srcs],
        **kwargs
    )

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
