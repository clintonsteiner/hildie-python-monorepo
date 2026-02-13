#!/usr/bin/env python3
"""Pre-commit hook: super setUp/tearDown calls must be the last statements in
those methods for classes that inherit from unittest.TestCase.

Checked methods: setUp, tearDown, setUpClass, tearDownClass.

Accepted super call forms:
  super().method()                  - Python 3 zero-arg super
  super(ClassName, self).method()   - explicit two-arg super
  BaseClass.method(self)            - direct base class call

Flags:
  --fix      Auto-correct violations in place.
  --profile  Print per-file timing to stderr.

Performance notes:
  Files that do not contain the text "TestCase" are skipped before AST parsing
  (fast pre-screen).  On a typical repo this eliminates >80 % of parse work
  because most Python files are not test files.
"""

import ast
import sys
import time
from pathlib import Path

CHECKED_METHODS = {"setUp", "tearDown", "setUpClass", "tearDownClass"}


def is_unittest_subclass(node: ast.ClassDef) -> bool:
    for base in node.bases:
        if isinstance(base, ast.Attribute):
            if (
                isinstance(base.value, ast.Name)
                and base.value.id == "unittest"
                and base.attr == "TestCase"
            ):
                return True
        elif isinstance(base, ast.Name) and base.id == "TestCase":
            return True
    return False


def _names_equal(a: ast.expr, b: ast.expr) -> bool:
    """Return True if two name/attribute AST nodes refer to the same identifier."""
    if isinstance(a, ast.Name) and isinstance(b, ast.Name):
        return a.id == b.id
    if isinstance(a, ast.Attribute) and isinstance(b, ast.Attribute):
        return a.attr == b.attr and _names_equal(a.value, b.value)
    return False


def is_super_call(stmt: ast.stmt, method_name: str, class_node: ast.ClassDef) -> bool:
    """Return True if stmt is an accepted super call for method_name.

    Accepted forms:
      super().method_name()
      super(Class, self/cls).method_name()
      BaseClass.method_name(self/cls)
    """
    if not isinstance(stmt, ast.Expr):
        return False
    call = stmt.value
    if not isinstance(call, ast.Call):
        return False
    if not isinstance(call.func, ast.Attribute):
        return False
    if call.func.attr != method_name:
        return False

    receiver = call.func.value

    # super() or super(ClassName, self/cls)
    if (
        isinstance(receiver, ast.Call)
        and isinstance(receiver.func, ast.Name)
        and receiver.func.id == "super"
    ):
        return True

    # Explicit base class: BaseClass.method(self) where BaseClass is a declared base
    for base in class_node.bases:
        if _names_equal(receiver, base):
            return True

    return False


def _effective_stmts(method: ast.FunctionDef) -> list[ast.stmt]:
    """Return method body statements, excluding pass and a leading docstring."""
    stmts = [s for s in method.body if not isinstance(s, ast.Pass)]
    if stmts and isinstance(stmts[0], ast.Expr) and isinstance(stmts[0].value, ast.Constant):
        stmts = stmts[1:]
    return stmts


def check_file(filepath: str) -> list[str]:
    source = Path(filepath).read_text(encoding="utf-8")

    # Fast pre-screen: if "TestCase" doesn't appear anywhere in the source
    # there can be no unittest.TestCase subclasses, so skip AST parsing entirely.
    if "TestCase" not in source:
        return []

    try:
        tree = ast.parse(source, filename=filepath)
    except SyntaxError as exc:
        return [f"{filepath}: SyntaxError: {exc}"]

    errors = []
    for node in ast.walk(tree):
        if not isinstance(node, ast.ClassDef):
            continue
        if not is_unittest_subclass(node):
            continue

        for item in node.body:
            if not isinstance(item, ast.FunctionDef):
                continue
            if item.name not in CHECKED_METHODS:
                continue

            stmts = _effective_stmts(item)
            if not stmts:
                continue

            last = stmts[-1]
            if not is_super_call(last, item.name, node):
                errors.append(
                    f"{filepath}:{last.lineno}: "
                    f"{node.name}.{item.name}() must end with super().{item.name}()"
                )

    return errors


def fix_file(filepath: str) -> tuple[list[str], bool]:
    """Fix violations in filepath in place.

    Returns (unfixable_errors, was_modified).
    Moves misplaced super() calls to the end; adds missing ones.
    """
    path = Path(filepath)
    source = path.read_text(encoding="utf-8")

    # Fast pre-screen: no TestCase means nothing to fix.
    if "TestCase" not in source:
        return [], False

    try:
        tree = ast.parse(source, filename=filepath)
    except SyntaxError as exc:
        return [f"{filepath}: SyntaxError: {exc}"], False

    # Collect (method, class, super_stmt_or_None, cached_stmts) for each violation.
    # We cache stmts here to avoid recomputing them in the fix loop.
    fixes: list[tuple[ast.FunctionDef, ast.ClassDef, ast.stmt | None, list[ast.stmt]]] = []

    for node in ast.walk(tree):
        if not isinstance(node, ast.ClassDef):
            continue
        if not is_unittest_subclass(node):
            continue
        for item in node.body:
            if not isinstance(item, ast.FunctionDef):
                continue
            if item.name not in CHECKED_METHODS:
                continue
            stmts = _effective_stmts(item)
            if not stmts:
                continue
            last = stmts[-1]
            if is_super_call(last, item.name, node):
                continue
            super_stmt = next((s for s in stmts if is_super_call(s, item.name, node)), None)
            fixes.append((item, node, super_stmt, stmts))

    if not fixes:
        return [], False

    lines = source.splitlines(keepends=True)

    # Sort bottom-to-top so earlier line numbers stay valid as we edit.
    fixes.sort(key=lambda t: t[0].lineno, reverse=True)

    for method, _cls, super_stmt, stmts in fixes:
        last = stmts[-1]
        indent = " " * last.col_offset

        if super_stmt is not None:
            # Remove the misplaced super() call and re-insert after last stmt.
            s_start = super_stmt.lineno - 1  # 0-indexed
            s_end = super_stmt.end_lineno  # exclusive (end_lineno is inclusive 1-indexed)
            super_lines = lines[s_start:s_end]
            del lines[s_start:s_end]
            # last.end_lineno was relative to the original file; adjust for deletion.
            offset = s_end - s_start
            last_line_idx = last.end_lineno - 1 - offset
            # Ensure the line we're appending after ends with a newline.
            if not lines[last_line_idx].endswith("\n"):
                lines[last_line_idx] += "\n"
            lines[last_line_idx + 1 : last_line_idx + 1] = super_lines
        else:
            # Insert a new super() call after the last statement.
            insert_idx = last.end_lineno  # 0-indexed position after last line
            # Ensure the preceding line ends with a newline.
            if not lines[insert_idx - 1].endswith("\n"):
                lines[insert_idx - 1] += "\n"
            new_call = f"{indent}super().{method.name}()\n"
            lines.insert(insert_idx, new_call)

    path.write_text("".join(lines), encoding="utf-8")
    return [], True


def main() -> int:
    import argparse

    parser = argparse.ArgumentParser(
        description="Check that super() is the last call in unittest setUp/tearDown."
    )
    parser.add_argument("files", nargs="*", help="Python files to check")
    parser.add_argument("--fix", action="store_true", help="Auto-correct violations in place")
    parser.add_argument("--profile", action="store_true", help="Print per-file timing to stderr")
    args = parser.parse_args()

    all_errors: list[str] = []
    any_modified = False
    timings: dict[str, float] = {}

    for filepath in args.files:
        t0 = time.perf_counter()
        if args.fix:
            errors, modified = fix_file(filepath)
            any_modified = any_modified or modified
        else:
            errors = check_file(filepath)
        timings[filepath] = time.perf_counter() - t0
        all_errors.extend(errors)

    if args.profile and timings:
        for fp, elapsed in timings.items():
            print(f"{elapsed * 1000:.2f}ms  {fp}", file=sys.stderr)
        total = sum(timings.values())
        print(f"--- {total * 1000:.2f}ms total ({len(timings)} files)", file=sys.stderr)

    for err in all_errors:
        print(err, file=sys.stderr)

    if args.fix:
        return 1 if any_modified else 0
    return 1 if all_errors else 0


if __name__ == "__main__":
    sys.exit(main())
