# A6 launch: notes for the founder (facts, not a post)

**Plan v2, Track A, step A6.** Prepared on 13 November 2026, for pkv 0.3.0.

**These are notes, not a draft.** Hacker News's guidelines say: "Please don't put generated text in HN posts", and for comments: "Don't post generated text or AI-edited text." So everything below is facts, numbers, links and likely questions. **The words of the post, and of every reply, have to be yours.** Nothing here is meant to be pasted.

## 1. The rules (read on 13 November 2026)

**Hacker News, Show HN** ([showhn.html](https://news.ycombinator.com/showhn.html), [guidelines](https://news.ycombinator.com/newsguidelines.html)):
- **Qualifies:** "something you've made that other people can play with". pkv qualifies: `pip install`, no sign-up.
- **The title starts with "Show HN".** No uppercase or exclamation marks for effect, and don't editorialize.
- **You must have** "worked on [it] personally" and be "around to discuss" it. Plan to be available for several hours after posting.
- **Version announcements** ("Foo 1.3.1 is out") "generally aren't substantive enough". This would be pkv's first Show HN, so present the project, not "0.3 is out".
- **Don't ask anyone to upvote or comment** ("Don't solicit upvotes, comments, or submissions"), and **don't automate posting.**
- **No generated text in the post** and **no generated or AI-edited text in comments** (above).

**Reddit: not verified.**
- My tools couldn't open Reddit (it's blocked for them), so I couldn't read r/Python's rules.
- From public posts, r/Python project posts usually use the "Showcase" flair, with sections like "What My Project Does", "Target Audience" and "Comparison". **That's an observed habit, not a rule I've read.**
- **Read each subreddit's sidebar rules yourself before posting** (r/Python, and any other you choose). Many forbid AI-written posts and limit self-promotion.

## 2. What you're showing, as facts

- **What it is:** pkv (Parinama Verify), an **independent checker for code changes made by AI coding agents**, or by anyone.
- **What it does:**
  1. works out which pytest tests a change can affect;
  2. **runs them itself**, in a clean copy of exactly the changed code;
  3. looks for **signs the tests were weakened** (deleted, skipped, emptied, loosened);
  4. writes a **sealed receipt** that anyone can re-run with `pkv fresh --rerun`.
- **The problem it targets:** an AI agent saying "done, all tests pass" when it weakened a test, ran stale code, or didn't run the relevant tests at all.
- **New in 0.3:**
  - the Claude Code hook (`pkv hook install`), which keeps Claude working when the change isn't verified;
  - `pkv map`, a map of a project with the code no test reaches;
  - receipts you can re-run.
- **Basics:** Python 3.10+, pytest; **no dependencies** (standard library only); **no AI inside; no network calls**; Apache-2.0.
- **Made by one person in India, with no funding.** Mention it only if you want to.

## 3. The numbers, each with where it comes from

Every study's predictions were committed **before** it ran, and the failures are published too.

| Claim | Number | Source | Say with it |
|---|---|---|---|
| Clean copy doesn't change results | same verdict on **120 / 120** real commits; 0 of 49,869 test outcomes differed | [REAL-004](../A3-design.md) | four well-kept libraries; fresh checkouts had no leftovers to catch, so this shows the *cost* (none), not the benefit |
| Receipts reproduce | **112 / 112** re-runs reproduced | REAL-004 | same four libraries |
| The map is right | contained **1,358 / 1,358** files Python really loaded; 89.6% of its links real | [REAL-005](../A5-design.md) | six projects, two never seen before; pure-Python libraries only |
| Against other tools | pkv (default) caught **24 / 41** hidden cheats with **3 / 20** false alarms; it caught every deleted test, added skip and removed assertion (14 / 14) | [TAMPER-BENCH held-out](../../../benchmarks/tamper-bench/results/heldout/NOTES.md) | **testwall caught 32 / 41 and checkwash 28 / 41** (with 15 and 7 false alarms). Skylos had fewer false alarms (2). We wrote the benchmark, though 39% of its cases come from outside sources |
| Real-commit false alarms | 4 / 120 unseen commits (pkv 0.1.2) | [REAL-001](../REAL-001-design.md) | all from renamed or moved tests |
| The hook in Claude Code | tested in live sessions; the live test found 2 defects, both fixed before release | [A4](../A4-design.md) | one Claude Code version (2.1.217), one model (Haiku) |

## 4. What not to claim

- **That pkv catches the most cheats.** By default it doesn't (testwall and checkwash catch more). With `--mutate` it caught 34 / 41, but its false alarms rose beyond our own pre-set limit, so we decided not to present it as an advantage (D-051).
- **That the receipt is signed.** The seal shows edits but isn't a signature: anyone who recomputes it gets past it. `--rerun` is the check that needs no trust.
- **That the map is always right.** No misses in 1,358 links on six libraries; heavy dynamic loading or plugins weren't tested.
- **That it works beyond Python and pytest.** It doesn't yet.
- **Any user numbers.** There are none yet (baseline below).

## 5. Likely questions, with the facts for your answers

- **"Why not just run the whole test suite?"**
  - You can: `--in-place` or CI does that.
  - pkv's point is the *receipt*: which tests, on exactly which code, and whether the tests themselves were weakened. A full suite passing says nothing about a test the agent deleted.
- **"How is this different from mutation testing (mutmut, cosmic-ray)?"**
  - pkv's default doesn't mutate anything.
  - `--mutate` is *differential*: it mutates only the old version of the changed lines, and compares the old tests with the new ones, so it reports checks that were *removed*. It's optional because of its false alarms.
- **"Does it use AI?"** No. Every sentence in a receipt comes from recorded data.
- **"Can't the agent just edit the receipt?"** It'll show as TAMPERED, unless the seal is recomputed. Then `pkv fresh --rerun` repeats the run and shows NOT REPRODUCED. A self-check tests exactly this case.
- **"Can't the agent just disable the hook?"**
  - With the default install, the hook lives in the project's shared settings file, `.claude/settings.json`. An agent that edits it changes a file in the commit, which a reviewer sees.
  - With `--scope local` or `--scope user`, that edit wouldn't show in the commit.
  - pkv doesn't sandbox anything, and says so.
- **"You wrote the benchmark you're scored on."** True:
  - the cases were sealed before any tool ran;
  - 39% come from rivals' own published examples and research;
  - we published results where rivals beat us.
- **"What happens when the tests are slow?"** It runs only the affected tests, with a time limit (`--timeout`). A hook check happens only when the code has changed since the last one.
- **"Telemetry?"** None. pkv makes no network calls.

## 6. Commands people can try (these you can paste: they're commands, not prose)

```bash
python -m pip install parinama-verify==0.3.0
```

```bash
pkv check
```

```bash
pkv fresh .pkv/receipt.json --rerun
```

```bash
pkv map
```

```bash
pkv hook install
```

Links:
- **PyPI:** https://pypi.org/project/parinama-verify/
- **Code:** https://github.com/broly18814/parinamakramam
- **GitHub Action:** https://github.com/broly18814/parinama-verify-action

## 7. Practical steps

1. **Before posting:**
   - list the action's `v0.3.0` on the Marketplace (PROJECT_STATE);
   - read the subreddits' rules;
   - check that the README's first screen says what pkv is in one look.
2. **Post once per place.** Don't cross-post the same day everywhere, and don't ask anyone to vote.
3. **Be there** to answer, in your own words. Criticism is data:
   - a reported false alarm or missed cheat becomes a GitHub issue (there are templates for both);
   - a fix is judged on a fresh set, never on the reported case alone.
4. **Afterwards:** take an adoption reading (`scripts/adoption.sh`) the same day, then weekly for 12 weeks. The plan's success bar (PLAN-v2, section 3) is **3 or more public repositories outside ours using the Action or the hook.**

## 8. The baseline before the launch (13 November 2026)

From `scripts/adoption.sh`, plus a public code search:
- **PyPI downloads:** 2 today, 111 this week, 111 this month. Many are robots and our own release checks.
- **GitHub:** 0 stars and 0 forks; 47 page views (21 unique visitors) in 14 days.
- **Wheel downloads from GitHub releases:** 4.
- **The Action's repository:** 0 stars; 11 views (3 unique).
- **Public repositories using the Action or `product/verify`, other than ours: 0.**
