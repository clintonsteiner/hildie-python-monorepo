"""Tests for hildie.check_unittest_super pre-commit hook."""

import ast
import io
import sys
import tempfile
import textwrap
import time
import unittest
from pathlib import Path
from unittest.mock import patch

from hildie.check_unittest_super import check_file, fix_file, is_super_call, is_unittest_subclass

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _parse_class(source: str) -> ast.ClassDef:
    for node in ast.walk(ast.parse(textwrap.dedent(source))):
        if isinstance(node, ast.ClassDef):
            return node
    raise ValueError("No ClassDef found in source")


def _parse_stmt(source: str) -> ast.stmt:
    return ast.parse(textwrap.dedent(source)).body[0]


def _dummy_class(bases: str = "unittest.TestCase") -> ast.ClassDef:
    return _parse_class(f"class Foo({bases}): pass")


# ---------------------------------------------------------------------------
# is_unittest_subclass
# ---------------------------------------------------------------------------


class TestIsUnittestSubclass(unittest.TestCase):
    def test_unittest_testcase_attribute(self):
        assert is_unittest_subclass(_parse_class("class Foo(unittest.TestCase): pass"))

    def test_testcase_direct_import(self):
        assert is_unittest_subclass(_parse_class("class Foo(TestCase): pass"))

    def test_no_bases(self):
        assert not is_unittest_subclass(_parse_class("class Foo: pass"))

    def test_object_base(self):
        assert not is_unittest_subclass(_parse_class("class Foo(object): pass"))

    def test_unrelated_attribute_base(self):
        assert not is_unittest_subclass(_parse_class("class Foo(other.Base): pass"))

    def test_unrelated_name_base(self):
        assert not is_unittest_subclass(_parse_class("class Foo(SomethingElse): pass"))

    def test_multiple_bases_one_matches(self):
        assert is_unittest_subclass(_parse_class("class Foo(Mixin, unittest.TestCase): pass"))


# ---------------------------------------------------------------------------
# is_super_call
# ---------------------------------------------------------------------------


class TestIsSuperCall(unittest.TestCase):
    """Tests for the three accepted super call forms."""

    # -- zero-arg super() --

    def test_zero_arg_super_setUp(self):
        cls = _dummy_class()
        assert is_super_call(_parse_stmt("super().setUp()"), "setUp", cls)

    def test_zero_arg_super_tearDown(self):
        cls = _dummy_class()
        assert is_super_call(_parse_stmt("super().tearDown()"), "tearDown", cls)

    def test_zero_arg_super_setUpClass(self):
        cls = _dummy_class()
        assert is_super_call(_parse_stmt("super().setUpClass()"), "setUpClass", cls)

    def test_zero_arg_super_tearDownClass(self):
        cls = _dummy_class()
        assert is_super_call(_parse_stmt("super().tearDownClass()"), "tearDownClass", cls)

    # -- two-arg super(Class, self) --

    def test_two_arg_super_setUp(self):
        cls = _dummy_class()
        assert is_super_call(_parse_stmt("super(MyTest, self).setUp()"), "setUp", cls)

    def test_two_arg_super_tearDown(self):
        cls = _dummy_class()
        assert is_super_call(_parse_stmt("super(MyTest, self).tearDown()"), "tearDown", cls)

    def test_two_arg_super_setUpClass(self):
        cls = _dummy_class()
        assert is_super_call(_parse_stmt("super(MyTest, cls).setUpClass()"), "setUpClass", cls)

    # -- explicit base class call --

    def test_explicit_base_name(self):
        cls = _parse_class("class Foo(TestCase): pass")
        assert is_super_call(_parse_stmt("TestCase.setUp(self)"), "setUp", cls)

    def test_explicit_base_attribute(self):
        cls = _parse_class("class Foo(unittest.TestCase): pass")
        assert is_super_call(_parse_stmt("unittest.TestCase.setUp(self)"), "setUp", cls)

    def test_explicit_base_teardown(self):
        cls = _parse_class("class Foo(TestCase): pass")
        assert is_super_call(_parse_stmt("TestCase.tearDown(self)"), "tearDown", cls)

    def test_explicit_base_setUpClass(self):
        cls = _parse_class("class Foo(TestCase): pass")
        assert is_super_call(_parse_stmt("TestCase.setUpClass()"), "setUpClass", cls)

    # -- rejections --

    def test_wrong_method_name(self):
        cls = _dummy_class()
        assert not is_super_call(_parse_stmt("super().setUp()"), "tearDown", cls)

    def test_self_call_not_super(self):
        cls = _dummy_class()
        assert not is_super_call(_parse_stmt("self.setUp()"), "setUp", cls)

    def test_plain_function_call(self):
        cls = _dummy_class()
        assert not is_super_call(_parse_stmt("foo()"), "setUp", cls)

    def test_assignment_not_super(self):
        cls = _dummy_class()
        assert not is_super_call(_parse_stmt("x = 1"), "setUp", cls)

    def test_unrelated_base_explicit_call(self):
        cls = _parse_class("class Foo(TestCase): pass")
        assert not is_super_call(_parse_stmt("OtherBase.setUp(self)"), "setUp", cls)


# ---------------------------------------------------------------------------
# check_file
# ---------------------------------------------------------------------------


class TestCheckFile(unittest.TestCase):
    def setUp(self):
        self._tmpdir = tempfile.TemporaryDirectory()
        self._path = Path(self._tmpdir.name) / "sample.py"
        super().setUp()

    def tearDown(self):
        self._tmpdir.cleanup()
        super().tearDown()

    def _check(self, source: str) -> list[str]:
        self._path.write_text(textwrap.dedent(source))
        return check_file(str(self._path))

    # -- valid: no errors expected --

    def test_setup_zero_arg_super_last(self):
        assert (
            self._check("""
            import unittest
            class MyTest(unittest.TestCase):
                def setUp(self):
                    self.x = 1
                    super().setUp()
        """)
            == []
        )

    def test_teardown_zero_arg_super_last(self):
        assert (
            self._check("""
            import unittest
            class MyTest(unittest.TestCase):
                def tearDown(self):
                    self.x = None
                    super().tearDown()
        """)
            == []
        )

    def test_setup_two_arg_super_last(self):
        assert (
            self._check("""
            import unittest
            class MyTest(unittest.TestCase):
                def setUp(self):
                    self.x = 1
                    super(MyTest, self).setUp()
        """)
            == []
        )

    def test_setup_explicit_base_name_last(self):
        assert (
            self._check("""
            from unittest import TestCase
            class MyTest(TestCase):
                def setUp(self):
                    self.x = 1
                    TestCase.setUp(self)
        """)
            == []
        )

    def test_setup_explicit_base_attribute_last(self):
        assert (
            self._check("""
            import unittest
            class MyTest(unittest.TestCase):
                def setUp(self):
                    self.x = 1
                    unittest.TestCase.setUp(self)
        """)
            == []
        )

    def test_both_setup_and_teardown_valid(self):
        assert (
            self._check("""
            import unittest
            class MyTest(unittest.TestCase):
                def setUp(self):
                    self.x = 1
                    super().setUp()
                def tearDown(self):
                    self.x = None
                    super().tearDown()
        """)
            == []
        )

    def test_setup_with_leading_docstring(self):
        assert (
            self._check("""
            import unittest
            class MyTest(unittest.TestCase):
                def setUp(self):
                    \"\"\"Set up fixtures.\"\"\"
                    self.x = 1
                    super().setUp()
        """)
            == []
        )

    def test_setup_only_super_call(self):
        assert (
            self._check("""
            import unittest
            class MyTest(unittest.TestCase):
                def setUp(self):
                    super().setUp()
        """)
            == []
        )

    def test_setup_only_pass(self):
        assert (
            self._check("""
            import unittest
            class MyTest(unittest.TestCase):
                def setUp(self):
                    pass
        """)
            == []
        )

    def test_no_setup_or_teardown(self):
        assert (
            self._check("""
            import unittest
            class MyTest(unittest.TestCase):
                def test_something(self):
                    assert True
        """)
            == []
        )

    def test_non_unittest_class_ignored(self):
        assert (
            self._check("""
            class NotATest:
                def setUp(self):
                    self.x = 1
        """)
            == []
        )

    def test_setUpClass_super_last(self):
        assert (
            self._check("""
            import unittest
            class MyTest(unittest.TestCase):
                @classmethod
                def setUpClass(cls):
                    cls.db = object()
                    super().setUpClass()
        """)
            == []
        )

    def test_tearDownClass_super_last(self):
        assert (
            self._check("""
            import unittest
            class MyTest(unittest.TestCase):
                @classmethod
                def tearDownClass(cls):
                    cls.db = None
                    super().tearDownClass()
        """)
            == []
        )

    def test_testcase_direct_import(self):
        assert (
            self._check("""
            from unittest import TestCase
            class MyTest(TestCase):
                def setUp(self):
                    self.x = 1
                    super().setUp()
        """)
            == []
        )

    def test_multiple_valid_classes(self):
        assert (
            self._check("""
            import unittest
            class FirstTest(unittest.TestCase):
                def setUp(self):
                    super().setUp()
            class SecondTest(unittest.TestCase):
                def tearDown(self):
                    super().tearDown()
        """)
            == []
        )

    # -- invalid: errors expected --

    def test_setup_super_not_last(self):
        errors = self._check("""
            import unittest
            class MyTest(unittest.TestCase):
                def setUp(self):
                    super().setUp()
                    self.x = 1
        """)
        assert len(errors) == 1
        assert "MyTest.setUp()" in errors[0]

    def test_teardown_super_not_last(self):
        errors = self._check("""
            import unittest
            class MyTest(unittest.TestCase):
                def tearDown(self):
                    super().tearDown()
                    self.x = None
        """)
        assert len(errors) == 1
        assert "MyTest.tearDown()" in errors[0]

    def test_setup_missing_super(self):
        errors = self._check("""
            import unittest
            class MyTest(unittest.TestCase):
                def setUp(self):
                    self.x = 1
        """)
        assert len(errors) == 1
        assert "MyTest.setUp()" in errors[0]

    def test_teardown_missing_super(self):
        errors = self._check("""
            import unittest
            class MyTest(unittest.TestCase):
                def tearDown(self):
                    self.x = None
        """)
        assert len(errors) == 1
        assert "MyTest.tearDown()" in errors[0]

    def test_setUpClass_super_not_last(self):
        errors = self._check("""
            import unittest
            class MyTest(unittest.TestCase):
                @classmethod
                def setUpClass(cls):
                    super().setUpClass()
                    cls.db = object()
        """)
        assert len(errors) == 1
        assert "MyTest.setUpClass()" in errors[0]

    def test_tearDownClass_missing_super(self):
        errors = self._check("""
            import unittest
            class MyTest(unittest.TestCase):
                @classmethod
                def tearDownClass(cls):
                    cls.db = None
        """)
        assert len(errors) == 1
        assert "MyTest.tearDownClass()" in errors[0]

    def test_multiple_methods_both_invalid(self):
        errors = self._check("""
            import unittest
            class MyTest(unittest.TestCase):
                def setUp(self):
                    super().setUp()
                    self.x = 1
                def tearDown(self):
                    self.x = None
        """)
        assert len(errors) == 2

    def test_multiple_classes_one_invalid(self):
        errors = self._check("""
            import unittest
            class GoodTest(unittest.TestCase):
                def setUp(self):
                    super().setUp()
            class BadTest(unittest.TestCase):
                def setUp(self):
                    self.x = 1
        """)
        assert len(errors) == 1
        assert "BadTest.setUp()" in errors[0]

    def test_syntax_error_returns_error(self):
        errors = self._check("def (broken syntax")
        assert len(errors) == 1
        assert "SyntaxError" in errors[0]

    def test_error_message_contains_filepath_and_lineno(self):
        errors = self._check("""
            import unittest
            class MyTest(unittest.TestCase):
                def setUp(self):
                    self.x = 1
        """)
        assert len(errors) == 1
        assert str(self._path) in errors[0]
        # line number should be present as "path:N:"
        assert errors[0].count(":") >= 2

    # -- pre-screen performance: files without TestCase must not be parsed --

    def test_non_testcase_file_returns_no_errors(self):
        assert (
            self._check("""
            import os
            def helper():
                return 42
        """)
            == []
        )

    def test_prescreen_skips_parsing_large_non_test_file(self):
        """A large file with no TestCase should be handled in well under 10 ms."""
        source = "import os\n" + "x = 1\n" * 2000
        self._path.write_text(source)
        t0 = time.perf_counter()
        errors = check_file(str(self._path))
        elapsed_ms = (time.perf_counter() - t0) * 1000
        assert errors == []
        assert elapsed_ms < 10, f"pre-screen took {elapsed_ms:.1f}ms (expected < 10ms)"

    def test_testcase_in_comment_still_parses(self):
        """A file where 'TestCase' only appears in a comment should still be parsed
        (false positive for the pre-screen), but produce no errors."""
        assert (
            self._check("""
            # This module relates to TestCase patterns
            def helper():
                return 42
        """)
            == []
        )


# ---------------------------------------------------------------------------
# fix_file
# ---------------------------------------------------------------------------


class TestFixFile(unittest.TestCase):
    def setUp(self):
        self._tmpdir = tempfile.TemporaryDirectory()
        self._path = Path(self._tmpdir.name) / "sample.py"
        super().setUp()

    def tearDown(self):
        self._tmpdir.cleanup()
        super().tearDown()

    def _fix(self, source: str) -> tuple[list[str], bool, str]:
        self._path.write_text(textwrap.dedent(source))
        errors, modified = fix_file(str(self._path))
        return errors, modified, self._path.read_text()

    # -- basic move / insert --

    def test_misplaced_super_moved_to_last(self):
        errors, modified, _ = self._fix("""
            import unittest
            class MyTest(unittest.TestCase):
                def setUp(self):
                    super().setUp()
                    self.x = 1
        """)
        assert errors == []
        assert modified is True
        assert check_file(str(self._path)) == []

    def test_misplaced_super_in_middle_of_many_stmts(self):
        """super() in position 2 of 5 statements should move to position 5."""
        errors, modified, result = self._fix("""
            import unittest
            class MyTest(unittest.TestCase):
                def setUp(self):
                    self.a = 1
                    super().setUp()
                    self.b = 2
                    self.c = 3
                    self.d = 4
        """)
        assert errors == []
        assert modified is True
        assert check_file(str(self._path)) == []
        lines = result.splitlines()
        # super() must be the last non-empty line in the method
        method_lines = [line for line in lines if line.strip()]
        assert method_lines[-1].strip() == "super().setUp()"

    def test_two_arg_super_misplaced(self):
        errors, modified, _ = self._fix("""
            import unittest
            class MyTest(unittest.TestCase):
                def setUp(self):
                    super(MyTest, self).setUp()
                    self.x = 1
        """)
        assert errors == []
        assert modified is True
        assert check_file(str(self._path)) == []

    def test_missing_super_setUp_added(self):
        errors, modified, result = self._fix("""
            import unittest
            class MyTest(unittest.TestCase):
                def setUp(self):
                    self.x = 1
        """)
        assert errors == []
        assert modified is True
        assert check_file(str(self._path)) == []
        assert "super().setUp()" in result

    def test_missing_super_tearDown_added(self):
        errors, modified, result = self._fix("""
            import unittest
            class MyTest(unittest.TestCase):
                def tearDown(self):
                    self.x = None
        """)
        assert errors == []
        assert modified is True
        assert "super().tearDown()" in result

    def test_missing_super_setUpClass_added(self):
        errors, modified, result = self._fix("""
            import unittest
            class MyTest(unittest.TestCase):
                @classmethod
                def setUpClass(cls):
                    cls.db = object()
        """)
        assert errors == []
        assert modified is True
        assert "super().setUpClass()" in result
        assert check_file(str(self._path)) == []

    def test_missing_super_tearDownClass_added(self):
        errors, modified, result = self._fix("""
            import unittest
            class MyTest(unittest.TestCase):
                @classmethod
                def tearDownClass(cls):
                    cls.db = None
        """)
        assert errors == []
        assert modified is True
        assert "super().tearDownClass()" in result
        assert check_file(str(self._path)) == []

    def test_setUpClass_misplaced_moved(self):
        errors, modified, _ = self._fix("""
            import unittest
            class MyTest(unittest.TestCase):
                @classmethod
                def setUpClass(cls):
                    super().setUpClass()
                    cls.db = object()
        """)
        assert errors == []
        assert modified is True
        assert check_file(str(self._path)) == []

    def test_tearDownClass_misplaced_moved(self):
        errors, modified, _ = self._fix("""
            import unittest
            class MyTest(unittest.TestCase):
                @classmethod
                def tearDownClass(cls):
                    super().tearDownClass()
                    cls.db = None
        """)
        assert errors == []
        assert modified is True
        assert check_file(str(self._path)) == []

    # -- multiple violations --

    def test_multiple_methods_both_fixed(self):
        errors, modified, _ = self._fix("""
            import unittest
            class MyTest(unittest.TestCase):
                def setUp(self):
                    super().setUp()
                    self.x = 1
                def tearDown(self):
                    self.x = None
        """)
        assert errors == []
        assert modified is True
        assert check_file(str(self._path)) == []

    def test_multiple_classes_multiple_violations(self):
        errors, modified, _ = self._fix("""
            import unittest
            class FirstTest(unittest.TestCase):
                def setUp(self):
                    self.a = 1
            class SecondTest(unittest.TestCase):
                def tearDown(self):
                    self.b = 2
        """)
        assert errors == []
        assert modified is True
        assert check_file(str(self._path)) == []

    # -- idempotency --

    def test_fix_is_idempotent(self):
        source = textwrap.dedent("""
            import unittest
            class MyTest(unittest.TestCase):
                def setUp(self):
                    super().setUp()
                    self.x = 1
        """)
        self._path.write_text(source)
        _, modified1 = fix_file(str(self._path))
        _, modified2 = fix_file(str(self._path))
        assert modified1 is True
        assert modified2 is False
        assert check_file(str(self._path)) == []

    # -- no-op cases --

    def test_already_valid_not_modified(self):
        errors, modified, _ = self._fix("""
            import unittest
            class MyTest(unittest.TestCase):
                def setUp(self):
                    self.x = 1
                    super().setUp()
        """)
        assert errors == []
        assert modified is False

    def test_non_unittest_class_not_fixed(self):
        source = textwrap.dedent("""
            class NotATest:
                def setUp(self):
                    self.x = 1
        """)
        errors, modified, result = self._fix(source)
        assert errors == []
        assert modified is False
        assert result == source

    def test_method_only_pass_not_modified(self):
        source = textwrap.dedent("""
            import unittest
            class MyTest(unittest.TestCase):
                def setUp(self):
                    pass
        """)
        errors, modified, result = self._fix(source)
        assert errors == []
        assert modified is False

    def test_no_testcase_file_not_modified(self):
        source = "import os\nx = 1\n"
        errors, modified, result = self._fix(source)
        assert errors == []
        assert modified is False
        assert result == source

    def test_syntax_error_not_modified(self):
        errors, modified, _ = self._fix("def (broken syntax")
        assert len(errors) == 1
        assert "SyntaxError" in errors[0]
        assert modified is False

    # -- content preservation --

    def test_fix_preserves_other_methods(self):
        errors, modified, result = self._fix("""
            import unittest
            class MyTest(unittest.TestCase):
                def setUp(self):
                    super().setUp()
                    self.x = 1
                def test_something(self):
                    assert self.x == 1
                def helper(self):
                    return 42
        """)
        assert errors == []
        assert modified is True
        assert "test_something" in result
        assert "helper" in result
        assert check_file(str(self._path)) == []

    def test_leading_docstring_preserved(self):
        errors, modified, result = self._fix("""
            import unittest
            class MyTest(unittest.TestCase):
                def setUp(self):
                    \"\"\"Set up the test.\"\"\"
                    super().setUp()
                    self.x = 1
        """)
        assert errors == []
        assert modified is True
        assert '"""Set up the test."""' in result
        assert check_file(str(self._path)) == []

    def test_fix_preserves_indentation(self):
        """Inserted super() call must match method body indentation."""
        errors, modified, result = self._fix("""
            import unittest
            class MyTest(unittest.TestCase):
                def setUp(self):
                    self.x = 1
        """)
        assert modified is True
        lines = result.splitlines()
        super_line = next(line for line in lines if "super()" in line)
        assert super_line.startswith("        ")  # 8 spaces

    def test_no_trailing_newline_handled(self):
        """Files without a trailing newline must not corrupt the output."""
        source = (
            "import unittest\n"
            "class MyTest(unittest.TestCase):\n"
            "    def setUp(self):\n"
            "        self.x = 1"  # no trailing newline
        )
        self._path.write_text(source)
        errors, modified = fix_file(str(self._path))
        assert errors == []
        assert modified is True
        result = self._path.read_text()
        # The file must be parseable and valid after the fix.
        assert check_file(str(self._path)) == []
        # super() must be on its own line
        lines = result.splitlines()
        assert any("super().setUp()" in line for line in lines)

    def test_pre_screen_skips_non_testcase_file(self):
        """fix_file must not modify a file that has no TestCase."""
        source = "import os\nx = 1\n" * 500
        self._path.write_text(source)
        t0 = time.perf_counter()
        errors, modified = fix_file(str(self._path))
        elapsed_ms = (time.perf_counter() - t0) * 1000
        assert not modified
        assert elapsed_ms < 10, f"pre-screen took {elapsed_ms:.1f}ms"


# ---------------------------------------------------------------------------
# main
# ---------------------------------------------------------------------------


class TestMain(unittest.TestCase):
    def setUp(self):
        self._tmpdir = tempfile.TemporaryDirectory()
        super().setUp()

    def tearDown(self):
        self._tmpdir.cleanup()
        super().tearDown()

    def _write(self, name: str, source: str) -> str:
        path = Path(self._tmpdir.name) / name
        path.write_text(textwrap.dedent(source))
        return str(path)

    def test_clean_files_returns_zero(self):
        path = self._write(
            "clean.py",
            """
            import unittest
            class MyTest(unittest.TestCase):
                def setUp(self):
                    super().setUp()
        """,
        )
        with patch.object(sys, "argv", ["check-unittest-super", path]):
            from hildie.check_unittest_super import main

            assert main() == 0

    def test_invalid_file_returns_one(self):
        path = self._write(
            "bad.py",
            """
            import unittest
            class MyTest(unittest.TestCase):
                def setUp(self):
                    self.x = 1
        """,
        )
        with patch.object(sys, "argv", ["check-unittest-super", path]):
            from hildie.check_unittest_super import main

            assert main() == 1

    def test_no_args_returns_zero(self):
        with patch.object(sys, "argv", ["check-unittest-super"]):
            from hildie.check_unittest_super import main

            assert main() == 0

    def test_fix_flag_returns_one_when_file_modified(self):
        path = self._write(
            "bad.py",
            """
            import unittest
            class MyTest(unittest.TestCase):
                def setUp(self):
                    self.x = 1
        """,
        )
        with patch.object(sys, "argv", ["check-unittest-super", "--fix", path]):
            from hildie.check_unittest_super import main

            assert main() == 1

    def test_fix_flag_returns_zero_when_nothing_to_fix(self):
        path = self._write(
            "clean.py",
            """
            import unittest
            class MyTest(unittest.TestCase):
                def setUp(self):
                    self.x = 1
                    super().setUp()
        """,
        )
        with patch.object(sys, "argv", ["check-unittest-super", "--fix", path]):
            from hildie.check_unittest_super import main

            assert main() == 0

    def test_fix_flag_corrects_file(self):
        path = self._write(
            "bad.py",
            """
            import unittest
            class MyTest(unittest.TestCase):
                def setUp(self):
                    self.x = 1
        """,
        )
        with patch.object(sys, "argv", ["check-unittest-super", "--fix", path]):
            from hildie.check_unittest_super import main

            main()
        assert check_file(path) == []

    def test_profile_flag_outputs_timing(self):
        path = self._write(
            "clean.py",
            """
            import unittest
            class MyTest(unittest.TestCase):
                def setUp(self):
                    super().setUp()
        """,
        )
        with patch.object(sys, "argv", ["check-unittest-super", "--profile", path]):
            from hildie.check_unittest_super import main

            buf = io.StringIO()
            with patch("sys.stderr", buf):
                main()
        output = buf.getvalue()
        assert "ms" in output
        assert "total" in output

    def test_fix_and_profile_combined(self):
        path = self._write(
            "bad.py",
            """
            import unittest
            class MyTest(unittest.TestCase):
                def setUp(self):
                    self.x = 1
        """,
        )
        with patch.object(sys, "argv", ["check-unittest-super", "--fix", "--profile", path]):
            from hildie.check_unittest_super import main

            buf = io.StringIO()
            with patch("sys.stderr", buf):
                result = main()
        assert result == 1  # file was modified
        assert "ms" in buf.getvalue()
        assert check_file(path) == []
