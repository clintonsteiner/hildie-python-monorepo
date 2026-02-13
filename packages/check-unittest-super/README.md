# check-unittest-super

A pre-commit hook that enforces `super()` calls are the **last** statement in
`setUp`, `tearDown`, `setUpClass`, and `tearDownClass` for classes that inherit
from `unittest.TestCase`.

## Why?

Calling `super().setUp()` first means the base class runs before your test
state is set up, which can cause subtle ordering bugs. The correct pattern is:

```python
def setUp(self):
    self.db = create_test_db()   # your setup first
    super().setUp()              # base class last
```

## Usage in other repos

Add to `.pre-commit-config.yaml` using the repo's tag:

```yaml
- repo: https://github.com/clintonsteiner/python-monorepo
  rev: v1.2.3  # replace with the latest tag
  hooks:
    - id: unittest-super-last
```

No extra dependencies required — the hook uses only the Python standard library.

## Options

| Flag        | Description                                                  |
|-------------|--------------------------------------------------------------|
| `--fix`     | Auto-correct violations in place (moves or adds super() call)|
| `--profile` | Print per-file timing to stderr after the run                |

### --fix behaviour

- If `super()` exists but is not last → it is moved to the end of the method.
- If `super()` is missing entirely → `super().method_name()` is appended.
- Exits with code `1` if any file was modified (pre-commit re-runs the hook).
- Exits with code `0` if no changes were needed.

Enable in `.pre-commit-config.yaml`:

```yaml
- repo: https://github.com/clintonsteiner/python-monorepo
  rev: v1.2.3
  hooks:
    - id: unittest-super-last
      args: [--fix]
```

### --profile behaviour

Prints millisecond timing per file to stderr, plus a total:

```
1.23ms  tests/test_foo.py
0.87ms  tests/test_bar.py
--- 2.10ms total (2 files)
```

## Accepted super() forms

All three forms are recognised as valid:

```python
super().setUp()                  # zero-arg (Python 3)
super(MyTest, self).setUp()      # two-arg explicit
unittest.TestCase.setUp(self)    # direct base-class call
```

## Running manually

```bash
python src/hildie/check_unittest_super.py path/to/test_file.py
python src/hildie/check_unittest_super.py --fix path/to/test_file.py
```

Or via the installed console script:

```bash
check-unittest-super path/to/test_file.py
check-unittest-super --fix path/to/test_file.py
```

## Development

```bash
bazel test //packages/check-unittest-super:tests
```
