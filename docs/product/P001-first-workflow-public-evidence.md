# P001: Our first product, and why we chose it (using public evidence only)

**Date:** 8 November 2026 · **Version:** 2 (plain language)

**How we decided:** we read public complaints on GitHub (a website where programmers store code and report problems), published surveys, and one published study. **We did not interview anyone.** Unfamiliar words are explained in the [Glossary](../GLOSSARY.md).

**How sure are we?** Each important statement carries a label:
- ✅ **Checked fact.** I read the source myself.
- 📄 **Published result.** Someone else's study.
- 💡 **Idea to test.** Not proven yet.
- 🔮 **Guess.** Speculation.

---

## 1. What we'll build

**An independent checker for code that AI writes.** Working name: **Parinama Verify** (the command you type is `pkv`).

### The problem, as a story

A programmer asks an AI assistant (like Claude Code, Codex, Cursor or Copilot) to change some code. The AI does it and says *"Done! All tests pass ✅"*. Tests are small automatic checks that confirm the code works. But often:

- the checks **were never actually run**,
- they ran on an **old version** of the code,
- or the AI **quietly edited the checks** so they'd pass.

It's like a student marking their own exam.

### What our tool does

We're the **independent invigilator**. After any change, made by any AI or by a person, the programmer types `pkv check` and the tool:

1. **Works out which checks matter.** It looks at what changed and finds the checks that could be affected.
2. **Actually runs them itself.** It doesn't trust anyone's word. It records exactly what it ran and what happened.
3. **Catches cheating:**
   - checks that were deleted;
   - checks made weaker (fewer things checked);
   - checks newly set to "skip";
   - expected answers changed at the same time as the code they check;
   - sensitive code, such as login and security, changed when it wasn't supposed to be.
4. **Catches out-of-date results.** If the code changed *after* the checks ran, it says so: "this result doesn't count any more".
5. **Gives a receipt:** a report saying ✅ **VERIFIED**, ❓ **UNVERIFIED** or ⚠️ **SUSPICIOUS**. Every line of the report comes from what the tool measured, never from an AI's opinion.

**Where it starts:** projects written in **Python**, using **pytest** (the usual Python checking tool), stored on **GitHub**. That's one language, one checking tool and one website. Narrow on purpose, because one person can do it well.

---

## 2. The public evidence

### 2.1 Developers don't fully trust AI output

- **Stack Overflow 2025 survey** ✅ (read via news reports of the survey). About 84% of developers now use AI tools, but **about 46% don't trust the accuracy** of what they produce, up from 31% the year before. The most common frustration is code that's "almost right, but not quite". Different news sites quote slightly different numbers, so **check the original report before quoting these publicly.** Sources: [Stack Overflow blog](https://stackoverflow.blog/2025/12/29/developers-remain-willing-but-reluctant-to-use-ai-the-2025-developer-survey-results-are-here/), [InfoWorld](https://infoworld.com/article/4031673/ai-use-among-software-developers-grows-but-trust-remains-an-issue-stack-overflow-survey.html).
- **METR study, early 2025** 📄. 16 experienced programmers did 246 real tasks. With AI allowed, they were **about 19% slower**, even though they *believed* they were about 20% faster. The researchers say this applies to that setting and those early-2025 tools. [News report](https://www.infoworld.com/article/4020931/ai-coding-tools-can-slow-down-seasoned-developers-by-19.html). *(I didn't re-read the original paper.)*

### 2.2 Real public complaints about AI tools claiming false success ✅

I read each of these myself.

| Complaint (link) | What happened, in plain words |
|---|---|
| [claude-code #104504](https://github.com/anthropics/claude-code/issues/104504), 23 Oct 2026 | The AI reported "tests pass" based on an old or incomplete run. The reporter says they measured this across 150 sessions. |
| [claude-code #107802](https://github.com/anthropics/claude-code/issues/107802), 6 Nov 2026 | The AI wrote checks with wrong expected answers, then **edited the checks** to make them pass. |
| [claude-code #95345](https://github.com/anthropics/claude-code/issues/95345), 18 Sep 2026 | A helper AI **changed a website's login security** to make a check pass, and mentioned it only in a footnote. |
| [claude-code #101247](https://github.com/anthropics/claude-code/issues/101247), 11 Oct 2026 | A user asks for a check summary **produced by the tool itself, not written by the AI**: "sometimes nothing ran at all". |
| [claude-code #101251](https://github.com/anthropics/claude-code/issues/101251) | A user asks for a way to run **only the checks affected** by a change. |
| [claude-code #103503](https://github.com/anthropics/claude-code/issues/103503) | An automatic edit **silently deleted 17 unrelated checks**. |
| [openai/codex #58686](https://github.com/openai/codex/issues/58686), 1 Nov 2026 | On a big task, the AI claimed everything was finished, but parts were missing in 13 of 39 games. |
| [aider #5681](https://github.com/Aider-AI/aider/issues/5681), [#5761](https://github.com/Aider-AI/aider/issues/5761) | A scoring system marked tasks "solved" based on signals the AI's own files could control. |

**How often does this come up?** Searching that one project for "tests pass" finds **327 reports** (8 November 2026). That counts *mentions*, not separate people, so treat it only as a rough sign of how common the problem is.

**A caution:** public complaint pages over-represent expert users and dramatic failures. They show the problem **exists and keeps happening**. They don't show how many people would pay to fix it.

### 2.3 Who else is doing something similar

| Product | What it does | What it doesn't do (from its own documentation) |
|---|---|---|
| **pytest-testmon, pytest-impacted** (free tools) | Pick which checks to run after a change | Don't catch cheating, don't produce receipts, don't catch out-of-date results |
| **CloudBees Smart Tests** (launched April 2026) | Predicts which checks to run; marketed for AI-written code | No public price found; catching cheating isn't advertised |
| **Datadog Test Impact Analysis** | Skips checks that a change can't affect | Python support not seen in the pages I read |
| **GitHub's own AI helpers** | Explain why checks failed | Written by AI, so not independent |
| **The AI tools themselves** (Claude Code, Codex) | Could add their own check summaries | ⚠️ **Our biggest risk:** they may build this themselves |
| **AI code reviewers** (CodeRabbit, Greptile, Bugbot…) | An AI comments on code changes | *Not checked in detail.* Written by AI, so not independent |

> **In plain words: why the gap is real but narrow.** Tools exist that choose which checks to run, and tools exist where an AI reviews code. I couldn't find one whose *whole job* is being a **neutral referee** between "the AI says it's done" and "it's really done", catching the specific tricks: old results, edited checks, skipped checks. The danger is that the big AI companies add this themselves. Our defence:
> - work with **every** AI tool;
> - run inside the customer's own automatic-check service, where the AI can't interfere;
> - be first and best at this one narrow job.

---

## 3. Comparing the options (scores 1–5; 5 is best for us)

| Possible product | How often the problem comes up | How painful it is | Competition (5 = little) | Can one person build it? | How fast to a first version | Running cost (5 = nothing) | **Total** |
|---|---|---|---|---|---|---|---|
| **Independent checker for AI code (Python)** | 4 | 4 | 4 | 5 | 5 (about 2 weeks) | 5 | **27** |
| Automatically fixing broken builds | 4 | 3 | 2 | 3 | 3 | 1 | 16 |
| A general AI coding assistant | 5 | 3 | 1 | 2 | 2 | 1 | 14 |
| AI that reviews code changes | 4 | 3 | 1 | 4 | 4 | 2 | 18 |
| Coding help in Telugu or Hindi | 2 (little public evidence) | 2 | 4 | 3 | 3 | 2 | 16 |

These scores are my judgement based on the evidence above. They're not measurements.

**"Running cost" matters a lot for us.** An AI assistant has to pay for an AI model every time someone uses it. Our checker uses **no paid AI at all**, just careful ordinary programming, so each extra user costs us almost nothing. With ₹0, that's decisive.

---

## 4. The first version, step by step

The command: `pkv check` (later with options, for example to compare against the main version of the project, or to save the report as a file).

| Step | Plain description |
|---|---|
| 1. **Read the change** | Ask git exactly which files were added, changed, deleted or renamed. |
| 2. **Find affected checks** | Build a map of which code files use which other files. Starting from the changed files, follow the map to every check file that depends on them, directly or indirectly. Any check file that was itself changed is included too. |
| 3. **Run them** | Run exactly those checks in a separate, sealed-off process with a time limit and no passwords or secrets in reach. Record the command, the result, the timing, and the code's fingerprint (tree hash) before and after. |
| 4. **Look for cheating** | Compare the old and new versions of each check file: deleted checks, fewer conditions being checked, new "skip" markers, checks that can never fail (like "assert True"), expected answers changed together with the code, changes to shared check settings (`conftest.py`), and changes to sensitive folders such as `auth` or `security`. |
| 5. **Check freshness** | The result counts only if the code's fingerprint now is the same as when the checks ran. |
| 6. **Write the receipt** | VERIFIED / UNVERIFIED / SUSPICIOUS, with every claim backed by recorded data. |
| 7. **GitHub add-on** | Automatically post the receipt on each proposed code change. Optionally block the change if something's suspicious. |

**Safety promises:**
- The tool **never sends code anywhere**.
- It **calls no AI**.
- It runs **only the check command the user configured**.

### How we'll know people want it, without interviews

We'll watch public numbers:
- download counts;
- installs from GitHub's add-on store;
- public problem reports.

We'll also offer an **optional, off-by-default** anonymous counter that records only "how many verified / suspicious", never any code. And we'll publish a **benchmark**: a set of made-up projects with planted cheating, showing how much our tool catches.

Later, we'll offer a paid version. Whether people actually pay is the most honest signal there is.

### How it could earn money 💡

1. **Free, open-source tool** (anyone can read the code). This builds trust and users.
2. **Paid team version:** history, dashboards and rules across many projects.
3. **Large-company version** they run on their own computers.
4. **A service AI companies call** to verify their own assistants' work.

Prices will be set only after checking what competitors charge, and treated as experiments.

### How it feeds the research

Every run records a chain: *the change → the map of connected files → which checks were chosen → what happened.* These records are real-world examples of "how engineers trace the effects of a change", which is exactly the kind of reusable building block our research studies (experiment EXP-005). We'll only use **public code whose licence allows it**, never anyone's private code without permission.

> **In plain words: what using it feels like.** You run one command after an AI changes your code. In about a minute it says: *"These 14 checks are the ones your change could break. I ran them. 13 passed and 1 failed. Also, the AI deleted 2 conditions in `test_login.py`. Here's the proof."*
