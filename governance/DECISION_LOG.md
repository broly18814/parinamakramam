# Decision log: our diary of important choices

**What this is:** every important choice, why we made it, and what would make us change our mind.

**The rules:**
- **Append only.** We never change the *meaning* of a past decision. If we change our mind, we add a new decision that replaces the old one.
- On 8 November 2026 the *wording* of D-001 to D-011 was rewritten in plain language. Their meaning is unchanged. The original technical wording is saved in git snapshot `a200f19`.

Words are explained in the [Glossary](../docs/GLOSSARY.md).

| No. | Date | What we decided | Why | We'd reconsider if… |
|---|---|---|---|---|
| D-001 | 8 Nov 2026 | The company is called **Parinamakramam** (పరిణామక్రమం, "the course of evolution"). | The founder's choice. | The name turns out to be trademarked, or the website name isn't available. |
| D-002 | 8 Nov 2026 | **No interviews, ever.** We judge demand only from public evidence and from what people do on their own: downloads, installs, payments. | The founder's rule. Not negotiable. | Never. |
| D-003 | 8 Nov 2026 | We changed the research question from "inventing new building blocks is *necessary*" to "with limited time, inventing new building blocks helps **only when** the problems contain hidden repeating patterns". | The 26 letters can already write every book, so new blocks are never strictly necessary. What they change is *effort*, and effort can be measured. | — |
| D-004 | 8 Nov 2026 | The first experiment uses a small puzzle world of list-of-numbers puzzles. It's written in plain Python and needs no graphics card. | It's free, runs on the MacBook in minutes, and is well studied (DreamCoder and AbstractBeam used similar puzzles). | Results stop telling us anything new. Then move to real software (EXP-005). |
| D-005 | 8 Nov 2026 | "Time" is measured as **the number of distinct results the computer tries**, identical for everyone. | It's fair, and it doesn't depend on how fast the computer is. It stops "trying harder" from looking like "learning better". | — |
| D-006 | 8 Nov 2026 | Exam paper 100 is for practice and fixing. Papers 0–9 are the real exam, and **must not be looked at** until the design is frozen. | It stops us from accidentally tuning the system to the exam. | — |
| D-007 | 8 Nov 2026 | After the practice run, we added (a) the **cheat student**, who is given the right blocks, and (b) **Student E**, who keeps a shortcut only if it measurably solves more practice puzzles. Then we froze the design. | The practice run showed the learners picking tiny useless shortcuts. Without a cheat student we couldn't tell whether the *exam* was broken or the *learners* were. | — |
| D-008 | 8 Nov 2026 | EXP-001's core prediction **is not supported**, and we record it as a failure. Next we work on **discovery** (EXP-002), not on the exam. | The cheat student's +18.5 points shows the exam works, but our learners recovered almost none of that. | EXP-002 fails too. Then rethink the puzzle world or how the question is framed. |
| D-009 | 8 Nov 2026 | First product: an **independent checker for AI-written code changes**, for Python, pytest and GitHub. Not a general AI coding assistant. | It had the strongest public evidence compared with its competition, costs nothing per user, and produces useful research data. | A big company releases an equivalent checker that works with every AI tool, or few people adopt ours after the first version. |
| D-010 | 8 Nov 2026 | No company registration, payment systems or paid tools yet. | There's nothing to sell yet, so no cost is justified. | The first paid offer is ready (around day 60–70). |
| D-011 | 8 Nov 2026 | All documents use plain language. | The founder asked. | — |
| D-012 | 8 Nov 2026 | **D-011 is strengthened:** every document is now fully plain-language, with a [Glossary](../docs/GLOSSARY.md). The exact maths for specialists lives in a separate [technical appendix](../docs/research/R001-technical-appendix.md). | The founder said the earlier documents still weren't plain enough. Other researchers still need the precise version to check our work, so it's kept, but out of the way. | — |
| D-013 | 8 Nov 2026 | The project is now saved with **git**, a free snapshot tool. The first snapshot is `a200f19`. Experiments will name the snapshot they used. | We can go back to any earlier version, and anyone can re-run an experiment on the exact same code. This fixes open problem OI-1. | — |
| D-014 | 8 Nov 2026 | The checker tool (`pkv`) uses **only Python's built-in parts**: no outside packages, and no AI calls. | Nothing to pay for, nothing extra to install, and less that can break or be tampered with. | We need a feature that's impractical without an outside package. |
