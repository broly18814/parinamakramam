# What the development run shows (12 November 2026)

All 8 tools on the 30 public development cases, run after the founder's go-ahead ("Yes, run them"). The numbers are in [RESULTS.md](RESULTS.md); the raw output of every run is in `runs.jsonl`.

**The development set is not the benchmark result.** It's small (20 cheats, 10 honest changes), we wrote most of it, and we may look at it while building. The result that counts is the held-out run (see [SEAL.md](../../SEAL.md)). These are first readings.

> **Update, the same day: A2.** pkv with its new mutation check (`--mutate`) was added later.
> - **Round 1, exactly as designed:** 15/20 cheats, 6/9 subtle, 3/10 false alarms ([`../dev-a2-round1/`](../dev-a2-round1/RESULTS.md)).
> - **Round 2, after two general improvements:** 17/20, 8/9, 3/10 (in RESULTS.md here).
>
> Round 2 was improved on these very cases, so only the held-out run can show whether it's really better ([A2 design and results](../../../../docs/product/A2-design.md)).

## In plain words

- **checkwash, a tool with 1 GitHub star, did best overall.** It caught 15 of 20 cheats, including 6 of the 9 subtle ones, with 2 false alarms in 10 honest changes. Our tool, pkv, caught 13 of 20 (4 of 9 subtle) with the same 2 false alarms. **On this set, pkv isn't the best checker, and we say so.**
- **testwall catches everything, but only because it objects to *any* change to a test file.** It caught all 9 subtle cheats, and also raised a false alarm on 7 of the 10 honest changes, including every honest rename and merge. A tool like this stops the AI changing tests at all; it doesn't judge whether a change was honest.
- **Skylos, the best-known tool (935 GitHub stars), caught 9 of 20, and only 1 of 9 subtle ones.** That agrees with its own published self-test, which admits it misses the subtle cases.
- **Three kinds of cheat nobody catches well:**
  - **an expected answer edited to match the bug:** only testwall, by objecting to everything;
  - **a test made unable to fail** (wrapped in `pytest.raises(AssertionError)`, or returning early): checkwash 1 of 2, testwall 2 of 2;
  - **a hard-coded answer in the code:** only Skylos, 1 of 2.

  This is the gap plan v2's A2, a mutation check on the changed lines, is designed for. Making small deliberate bugs in the changed code and seeing whether the tests notice works the same whether a test was loosened, edited or rigged.
- **Every honest refactor with unchanged tests (H1) passed every tool.** The false alarms all come from honest changes *to tests* (renames, merges, documented behaviour changes).

## In engineering terms

| | Cheats caught | Semantic (T4–T7) | False alarms |
|---|---|---|---|
| checkwash 0.12.0 | 15/20 | 6/9 | 2/10 |
| pkv 0.2.1 | 13/20 | 4/9 | 2/10 |
| testwall 1.0.1 | 16/20 | 9/9 | **7/10** |
| Skylos 5.6.0 | 9/20 | 1/9 | 1/10 |
| dunnit 0.3.0 | 6/20 | 0/9 | 1/10 |
| goodhart `4ec997e` | 5/20 | 0/9 | 1/10 |
| tamperguard 0.2.0 | 4/20 | 0/9 | 0/10 |
| tampercheck 0.1.1 | 2/20 | 0/9 | 0/10 |

**Against the sealed predictions, as a first reading only** (they're scored on the held-out set):
- **H-TB1** (pkv: removal recall ≥ 70%, semantic ≤ 50%): on development, removal 7/7 and semantic 4/9 (44%). It would pass.
- **H-TB2** (no tool has semantic recall ≥ 80% with false alarms ≤ 10%): testwall has 100% semantic but 70% false alarms, and checkwash 67% with 20%. It would pass.

**Checks on the adapters.** The low scores aren't adapter errors. Every tool produced a verdict on all 30 cases, and every low scorer flagged some cases, with its own named findings (for example tampercheck on D02 and D03, tamperguard on D03 and D19). The verdict rules are the ones committed in [SEAL.md](../../SEAL.md) before this run. goodhart's rule was added after the seal but before this run.

**Limits:**
- 30 cases, so the ranges are wide; for example, checkwash's and pkv's ranges overlap almost entirely.
- Each tool ran with its defaults. Some (checkwash, tamperguard) have stricter settings that could change the result; we report defaults, as the design says.
