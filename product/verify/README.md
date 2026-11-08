# Parinama Verify (`pkv`): version 0.0.1

An **independent checker** for code changes, whether an AI or a person made them. The full product plan is in [P001](../../docs/product/P001-first-workflow-public-evidence.md). Words are explained in the [Glossary](../../docs/GLOSSARY.md).

## What works today

| Part | What it does | Status |
|---|---|---|
| **Change reader** (`gitdiff.py`) | Asks git which files were added, changed, deleted or renamed, including unsaved edits and brand-new files. | ✅ Built and self-checked |
| **Fingerprint** (`gitdiff.py`) | Produces one short code (the **tree hash**) that identifies the exact state of all the code. Change one character and the code changes. | ✅ Built and self-checked |
| **Code map** (`imports.py`) | Reads every Python file *without running it* and records which files use which. This is called an **import graph**. | ✅ Built and self-checked |
| **Test finder** (`affected.py`) | Starting from the changed files, follows the map *backwards* to every test that could break, and writes down the reason for each one. | ✅ Built and self-checked |
| Test runner + "is the result out of date?" | Actually runs the chosen tests and records proof. | ⏳ Next (week 1, day 3) |
| Cheating detector | Spots deleted or weakened tests, new "skip" markers, and similar tricks. | ⏳ Week 1, day 4 |
| Receipt (report) | Prints VERIFIED / UNVERIFIED / SUSPICIOUS. | ⏳ Week 1, day 5 |

## Try it

From inside any Python project that uses git, run:

```bash
PYTHONPATH=/Volumes/projects/hope/parinamakramam/product/verify python3 -m pkv affected
```

Example output (from our own self-checks):

```
Changed files (1):
  modified  app/utils.py

Tests to run: 1 of 5
  tests/test_utils.py
      why: tests/test_utils.py uses app/utils.py, which was modified

To run them yourself:
  python -m pytest tests/test_utils.py
```

**Options:**
- `--base main` compares with the `main` branch, the way a GitHub pull request would.
- `--json` produces output for other programs to read.
- `pkv fingerprint` prints the fingerprint of the code as it is now.

## Its safety rules

1. **It never runs your code** while building the map. It only *reads* it.
2. **When unsure, it runs more tests, not fewer.** If a project settings file or an unrecognised data file changes, it says "every test must run" and explains why. Running too many tests wastes a minute; running too few can hide a bug.
3. **It tells you what it can't see.** Files that load code by name at run time, and files with syntax errors, are listed as warnings.
4. **It uses no AI and sends nothing anywhere.** It needs only Python's built-in parts (decision D-014).

## Self-checks

```bash
cd /Volumes/projects/hope/parinamakramam/product/verify
PYTHONPATH=. uv run --no-project --python 3.14 --with pytest python -m pytest -q tests
```

**27 self-checks, all passing** (8 November 2026). Each one builds a tiny throw-away project, makes a change, and checks that the right tests are picked for the right reason.

**One check came from a real mistake.** Running the tool on our own project showed that changing a sub-project's settings file wrongly demanded every test in the whole project. That was fixed, and a check was added so the mistake can't come back.

## Known limits

- **It follows imports only.** If code reads a file by name (`open("data.json")`), the link isn't visible. A changed data file therefore triggers "run everything".
- **It finds test files by name only** (`test_*.py` or `*_test.py`), which is pytest's default. Custom naming settings aren't read yet.
- **It hasn't been tried on large real-world projects yet.** That's planned for week 1, day 5.
