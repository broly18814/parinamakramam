# Project map: proj

13 Python files: 7 code, 5 test, 1 shared test settings (conftest.py). Read without running anything.

## Parts of the project

| Part | Code files | Test files | Uses parts | Code reached by tests |
|---|---|---|---|---|
| `app` | 6 | 0 | - | 6 of 6 |
| `tests` | 1 | 5 | `app` | 1 of 1 |

## Most-used code (top 7)

A change here affects the most of the project.

| File | Used directly by | Reached by test files |
|---|---|---|
| `app/__init__.py` | 9 | 4 of 5 |
| `app/models.py` | 3 | 3 of 5 |
| `app/sub/__init__.py` | 2 | 1 of 5 |
| `app/api.py` | 1 | 1 of 5 |
| `app/sub/deep.py` | 1 | 1 of 5 |
| `app/utils.py` | 1 | 1 of 5 |
| `tests/helpers.py` | 1 | 1 of 5 |

## Code no test reaches (0)

Every code file is reached by at least one test file.

---
A link means one file imports another, found by reading the code. `pkv map --module FILE` shows one file in detail; `--json` gives the whole map.
