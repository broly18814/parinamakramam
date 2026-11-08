# REAL-001 held-out set: every alarm, classified by hand

pkv **0.1.2**, run once on 9 November 2026, after the fixes from the study set were frozen. Results are in the four `.json` files in this folder. The rubric and its application are the same as for the [study set](../study/CLASSIFICATION.md).

## Summary

| Project | Commits | VERIFIED | FAILED | UNVERIFIED | SUSPICIOUS | Tool error |
|---|---|---|---|---|---|---|
| click | 30 | 2 | 23 | 0 | 5 | 0 |
| more-itertools | 30 | 30 | 0 | 0 | 0 | 0 |
| boltons | 30 | 28 | 0 | 1 | 1 | 0 |
| tomli | 30 | 21 | 2 | 1 | 6 | 0 |
| **All** | **120** | **81** | **25** | **2** | **12** | **0** |

## SUSPICIOUS: 12 commits

| Commit | Finding | Label | Why |
|---|---|---|---|
| click #33 | fewer-checks 3 → 1 | **S-intended** | The behaviour changed from raising an error to a warning. `pytest.warns(UserWarning, match=...)` now checks the type and message, and the exit-code check went. |
| click #40 | test-removed: `test_fish_multiline_help_complete` | **S-true** | A fix to fish completion removed the multi-line help test with no replacement, while the code stays. Worth a reviewer's look. |
| click #41 | check-weakened: 2 → 1 exact checks | **S-true** | `assert pager is created[0]` was replaced by `assert not stream.closed`. That's accurate, and worth a look. |
| click #42 | skip-added: `test_echo_via_pager` | **S-intended** | A `skipif`, with a stated reason, for a test that's flaky on macOS with Python 3.13+. |
| click #47 | test-removed: `test_faulthandler_enable` | **S-intended** | The commit reverts the behaviour that test covered ("revert default fileno exposure"). |
| boltons #35 | test-removed: `test_FunctionBuilder_KWONLY_MARKER` | **S-intended** | `_KWONLY_MARKER`, the thing it tested, was removed from the code in the same commit. |
| tomli #40 | test-file-deleted: `profiler/test_for_profiler.py` | **S-intended** | A profiling harness, removed while the profiler tooling was reorganised. |
| tomli #51 | test-removed: `TestMiscellaneous::test_own_pyproject` | **S-true** | A check that the package version matches `pyproject.toml` was dropped while making the tests work for other module names. It's accurate, and worth a look. |
| tomli #47 | test-removed ×2, test-file-deleted | **S-false (D4)** | `test_toml_compliance.py` was renamed to `test_data.py`, its class renamed, and `test_extras.py` merged into it. |
| tomli #53 | test-removed ×4 | **S-false (D4)** | pytest-style test functions were rewritten as `unittest` classes with the same tests. |
| tomli #55 | test-removed ×6 | **S-false (D4)** | `test_misc.py` was migrated to `unittest`. The same 6 tests are now methods of `TestMiscellaneous`. |
| tomli #56 | test-removed ×4 | **S-false (D4)** | The same migration, for `test_error.py`. |

**Totals:**
- **4 of 120 commits** have a false alarm, all from the known, unfixed defect D4 (tests renamed or moved).
- No false alarm came from D1, D2, D3 or D5.
- The 8 accurate findings are 3 S-true and 5 S-intended.

## UNVERIFIED: 2 commits

| Commit | Reason | Label |
|---|---|---|
| boltons #52 | `docs/conf.py` changed; no test uses it | **U-accurate** |
| tomli #34 | `profiler/profiler_script.py` changed; no test uses it | **U-accurate** |

## FAILED: 25 commits, all caused by our environment

| Commits | What failed | Label | Why |
|---|---|---|---|
| click #34–39, 43–46, 48–60 (23 commits), and the 5 SUSPICIOUS click commits | `tests/test_basic.py` fails to load | **F-env** | Today's pytest rejects a non-list iterable passed to `parametrize`, and click's settings turn warnings into errors. click fixed this in commit #32. pkv's FAILED verdict was correct: the tests really couldn't load. |
| tomli #59, #60 | `tests/test_extras.py` and `tests/test_toml_compliance.py` fail to load | **F-env** | This older code needed the `python-dateutil` test package, which the next commit (#57) removed. Our environment installs only pytest (rule E3). |

## The false all-clear check: 1 disagreement

pkv said VERIFIED after running only some test files on 31 commits, and the full suite was then run on each. It disagreed **once**: tomli #58 (`c00fbc1f82`).

- **By the rule as written, this counts as a false all-clear**, and R3 is scored as failed.
- **What actually happened:**
  - The commit only adds tests to `tests/test_misc.py`. pkv selected and ran that file, and all 6 of its tests passed.
  - The full suite was interrupted because two *other* test files couldn't load, for the environment reason above (python-dateutil).
  - Those files failed in exactly the same way at the parent (#59) and the grandparent (#60), so the change didn't cause it.
  - No test that this change could affect failed.

  So it isn't a selection miss. But pkv's receipt said nothing about the rest of the suite being broken. A cheap whole-suite load check would have spotted it (open problem OI-11).

## Did the fixes generalise?

The same held-out receipts were also scored with **pkv 0.1.1's rules**. Nothing from the projects was run: the stored run was reused, limited to the tests both versions selected. The script is in the appendix.

| | pkv 0.1.1 | pkv 0.1.2 |
|---|---|---|
| Commits with a false alarm | **12** | **4** |
| Accurate findings | 8 | 8 (the same ones) |

The 8 commits that differ are all fixed false alarms:
- boltons #39, 40, 43, 48, 49, 52, 54: the `test_url` fixture (D2);
- click #31: the stress tests the project leaves out (D1).

No new false alarm appeared, and no accurate finding was lost.

**How much each fix was really exercised:**
- D2 was exercised 7 times.
- D1 only once, because click's tests couldn't load in 28 of its 30 held-out commits.
- D3 (`x == x`) never came up.

So the held-out set strongly supports the D2 fix, only weakly supports D1, and says nothing about D3.

## Appendix: the comparison script

Run from the repository root with a checkout of pkv 0.1.1 (snapshot `03c97b7`):
`python3 compare.py <pkv-0.1.1>/product/verify product/verify/realworld/results <work>/receipts/heldout <work>/src`

```python
"""Recompute REAL-001 held-out verdicts with pkv 0.1.1's rules, from saved receipts (nothing is executed)."""
import json, subprocess, sys
from collections import Counter
old_pkv, results, receipts, src = sys.argv[1:5]
sys.path.insert(0, old_pkv)
from dataclasses import fields
from pkv import __version__
from pkv.affected import select_tests
from pkv.gitdiff import changed_files
from pkv.report import decide
from pkv.runner import RunRecord
from pkv.tamper import find_not_run, find_tampering
assert __version__ == "0.1.1", __version__
names = {f.name for f in fields(RunRecord)}
tally = Counter(); per = {}
for p in ["click", "more-itertools", "boltons", "tomli"]:
    repo = f"{src}/{p}"
    for r in json.load(open(f"{results}/heldout/{p}.json")):
        subprocess.run(["git", "-C", repo, "checkout", "-q", "--detach", "-f", r["commit"]], check=True)
        subprocess.run(["git", "-C", repo, "clean", "-q", "-f", "-d"], check=True)
        rc = json.load(open(f"{receipts}/{p}-{r['commit'][:12]}.json"))
        changes = changed_files(repo, r["parent"])
        sel = select_tests(repo, changes)
        run = RunRecord(**{k: v for k, v in rc["run"].items() if k in names}) if rc["run"] else None
        findings = find_tampering(repo, changes, r["parent"])
        if run and run.outcome in ("passed", "failed"):
            both = [t for t in sel.tests if t in rc["selection"]["tests"]]  # tests the stored run really covered
            findings += find_not_run(repo, both, run.executed)
        v, _ = decide(sel, run, findings, ran_requested=True)
        tally[(p, v)] += 1
        if v != r["verdict"]:
            per[f"{p} #{r['position']}"] = (v, r["verdict"], sorted({f.kind for f in findings if f.severity == "suspicious"}))
    subprocess.run(["git", "-C", repo, "checkout", "-q", "--detach", "-f", {"click":"8abb77a8432e03ed14a95f972b44f905279415a7","more-itertools":"f42daddf205f335fea6e200dad46049f33e71221","boltons":"d31d821d56c8f7756af9c30a864077f2e5855321","tomli":"43a86ade8b795c6ef9b4ec53372a607cd1ed426f"}[p]], check=True)
for k, v in sorted(per.items()):
    print(f"{k}: 0.1.1 says {v[0]}, 0.1.2 said {v[1]}  {v[2]}")
print({f"{p}:{v}": n for (p, v), n in sorted(tally.items())})
```
