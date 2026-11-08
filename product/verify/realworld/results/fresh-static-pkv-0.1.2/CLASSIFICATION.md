# REAL-002, step 2: pkv 0.1.2's findings on the fresh commits, classified

These 120 fresh commits are positions 61–90 of the REAL-001 projects. They were analysed read-only by pkv **0.1.2** (`run_real.py static --set fresh`), and nothing from the projects was installed or run. The labels below were written and committed **before** pkv 0.2.0 was run on these commits, as [D4-design.md](../../../../docs/product/D4-design.md), section 4, requires.

| Project | Commits | With a suspicious finding | Errors |
|---|---|---|---|
| click | 30 | 0 | 0 |
| more-itertools | 30 | 0 | 0 |
| boltons | 30 | 0 | 0 |
| tomli | 30 | 2 | 0 |

| Commit | Finding | Label | Why |
|---|---|---|---|
| tomli #64 `9e56735f22` | test-file-deleted: `tests/test_flags.py` | **S-intended** | The file tested only `Flags.set_for_relative_key`, and the same commit removed that method. The module still exists, which is why pkv says "the code it tested is still there", but the tested code is gone. It isn't a move. |
| tomli #65 `486c156d96` | fewer-checks: `test_load` 3 → 1 | **S-intended** | The commit removes text-file support ("Remove text file object support"), and the checks for that mode went with it. It isn't a move. |

**Consequences for the registered predictions:**
- **Q1 (safety):** two S-intended findings exist, and 0.2.0 must keep both suspicious.
- **Q2:** there are no move false alarms (D4) among these commits, so Q2 can't be tested on this set. That's reported as such, not as a pass.
