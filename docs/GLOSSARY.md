# Glossary: every technical word, in plain language

If a word in any Parinamakramam document confuses you, look it up here. The words are in alphabetical order.

| Word | What it means |
|---|---|
| **Abstraction** | A saved shortcut, often with blanks to fill in. "Sort, then do ___ to every number" is an abstraction. |
| **Action slot** (higher-order hole) | A blank in a shortcut that takes *another action*, for example "do **[double it]** to every number". Compare *data slot*. |
| **Affected tests** | The automatic checks that could break because of a particular code change. If you change the login code, the login checks are affected; the checks for printing invoices probably aren't. |
| **Agent / AI coding assistant** | An AI program that writes or edits code for you, for example Claude Code, Codex, Cursor or Copilot. |
| **Archive** | A logbook of every shortcut ever invented, including the ones that were thrown away. |
| **Baseline** | The plain, simple version you compare against. In our experiment it's Student A, who never learns. |
| **Benchmark** | A standard exam used to compare methods fairly. |
| **Benchmark (practice set)** | A fixed set of test situations used to measure a tool. pkv's are BENCH-001 and BENCH-002. |
| **Best-first search / A\* search** | Trying the most promising option first instead of going in a fixed order. A\* ("A-star") is the standard version: it scores each unfinished attempt by its cost so far plus the *least* it could still cost to finish, and always continues the attempt with the lowest total. If that estimate never overestimates, the first finished answer is guaranteed to be the best one. EXP-006 uses it to produce guesses in order from most to least likely. |
| **Bit (of surprise)** | A unit for how unlikely something is. Each extra bit means half as likely, and about twice as many guesses before a best-first search reaches it. |
| **Bootstrap / confidence range** | A way of checking whether a result could be luck: reshuffle the results thousands of times and see how much the answer wobbles. If the whole range of likely values is above zero, it's very unlikely to be luck. |
| **Budget** | How many tries the computer gets. Every student gets the same budget, so nobody wins by trying harder. |
| **Calibration / practice paper** | The one set of puzzles (number 100) we used to build and fix the system. The real exam papers were kept unseen. |
| **Canonical form** | One standard way of writing something that can be written several ways. pkv treats `assert a == b` and `self.assertEqual(a, b)` as the same check because they share one canonical form. |
| **Changelog** | A dated list of what changed in each version. Ours is CHANGELOG.md. |
| **CI (Continuous Integration)** | A service that automatically runs a project's checks every time someone changes the code, for example GitHub Actions. *(In the technical appendix, "CI" means confidence interval instead, which is the confidence range above.)* |
| **CLI (command-line tool)** | A program you run by typing a command in the Terminal instead of clicking buttons. |
| **Cluster bootstrap** | The bootstrap done on whole groups. In EXP-006 several hidden pieces come from the same function and aren't independent, so we reshuffle whole functions, not single pieces. |
| **Commit / snapshot** | A saved copy of the whole project at one moment, made with git. You can always go back to it. |
| **Composite action / GitHub Action** | A reusable step for GitHub's robot. pkv is available as one (product/verify/action.yml). |
| **Compression / shortening** | Judging a shortcut by how much shorter it makes your *old* solutions. That's the usual method, and our experiment found it picks the wrong shortcuts. |
| **Condition** | One "student" in our experiment, meaning one version of the computer with certain features switched on or off. |
| **Context (in a grammar)** | What the computer looks at when it guesses the next piece. In EXP-006 the context is *where* the piece goes, for example "the thing being called in a function call". A wider context looks one level further up as well. |
| **Data slot** | A blank in a shortcut that takes a thing, such as a list or a number. Compare *action slot*. |
| **Deprecation / pruning** | Throwing away shortcuts that aren't useful any more. |
| **Diff** | The list of exactly what changed in the code: which files, which lines added and which removed. |
| **Dogfooding** | Using your own product on yourself. Running pkv on our own project found 5 real mistakes. |
| **DPIIT recognition** | The Indian government's official certificate that a company is a "startup". It is free, but only a registered company, LLP or partnership can get it, not a person alone. Most government startup money (the Seed Fund, MeitY schemes, the startup tax holiday) needs it. See F001. |
| **DSL (domain-specific language)** | The small, fixed set of basic actions the computer starts with. Ours has 26. |
| **Enumeration / search** | Trying possible recipes one by one, simplest first. |
| **Environment variable** | A named setting every program receives from whoever started it, for example `PATH`. These often hold secrets, so pkv hides them from tests. |
| **Equity-free grant (non-dilutive funding)** | Money you don't pay back and that doesn't buy part of your company. Compare an investor, who takes a share (equity) in exchange. |
| **Evaluator / exam marker** | The part that marks the results. It's fixed, and the learner can never change it, so it can't cheat. |
| **Exact match** | Counting a guess as right only if it's identical to the real answer. Strict, but nobody has to judge it. |
| **Exit code** | The number a program hands back when it finishes. 0 means success. Robots like GitHub Actions read it to decide whether to accept a change. |
| **Exploratory result** | Something we noticed but didn't predict in advance. It's a lead to follow up, not proof. |
| **False alarm / missed problem** | The two ways a checker can be wrong. A false alarm says 'problem' when there isn't one. A missed problem says 'all clear' when there is one, and that's far worse. |
| **Fixture** | A pytest helper that prepares something for tests (data, a temporary folder). It isn't a test itself, even if its name starts with `test`. |
| **Flaky (non-deterministic)** | A result that changes from run to run with nothing changed. A flaky score is meaningless. |
| **Forking paths** | Trying many small variations and keeping the one that looks best; it produces 'improvements' that are really luck. |
| **Freeze (a design)** | Committing to every setting before the real test, so it can't be tuned to the answers. |
| **git** | A free program that saves snapshots of a project so you can see every change and go back to any earlier version. |
| **GitHub** | A website where programmers store code and publicly report problems with software. |
| **Held-out set** | Test situations kept apart from the ones used for improving, to check that improvements generalise. |
| **Hypothesis** | A prediction written down *before* the experiment, so we can't move the goalposts afterwards. |
| **Import / import graph** | In Python, one file "imports" another to use its code. The import graph is the map of which files use which. We use it to work out which checks a change could affect. |
| **Incubator** | An organisation, often at a university, that supports young startups with mentoring, space and sometimes money. In India many government grants reach startups only through an incubator. |
| **JUnit XML** | A standard file format test tools use to write down each test's result. pkv reads it for exact counts. |
| **Licence** | The legal terms for using someone's work. Ours is the Apache License 2.0: anyone may use, change and share pkv, even commercially, if they keep our licence and notice files. |
| **Library** | The computer's growing collection of saved shortcuts. |
| **Linter** | A program that proof-reads code for likely bugs and inconsistent style. Ours is ruff. |
| **Marketplace (GitHub)** | GitHub's store of ready-made tools, including Actions. Listing is free; it's the main way strangers find an Action. It needs the Action's own repository with `action.yml` at the top. |
| **MDL (minimum description length)** | The technical name for *compression / shortening*. |
| **Module** | One Python code file, or a folder of them. |
| **Monorepo** | One repository holding several projects. Ours holds the research and the product. |
| **Mutation testing** | Deliberately breaking code to check the tests notice. A break that no test catches reveals a blind spot. |
| **Near miss** | For an unsolved puzzle, the attempt whose answers came closest. EXP-002 tried learning from these, and it didn't help. |
| **NOTICE file** | A short file naming the project and who owns it. The Apache licence requires anyone who shares the work to keep it. |
| **Negative control** | A test where the method *should not* help, like our random puzzles. If it helps there too, something is fishy. |
| **Open source** | Code anyone may read, use and improve for free. |
| **Oracle / cheat student** | A student secretly given the right answers' building blocks. It shows the best possible score, which tells us whether our exam can detect improvement at all. |
| **pkv / Parinama Verify** | Our first product: an independent checker for code changes made by AI. |
| **Points / pp (percentage points)** | Our scores are "puzzles solved out of 100". "+3 points" means 3 more puzzles out of 100. |
| **Positive control** | A test where the method *should* help, like the cheat student. If it doesn't, the exam is broken. |
| **Pre-registration** | Writing down predictions and success rules before running an experiment. |
| **Primitive** | A basic building block, one of the starting actions. |
| **Probabilistic grammar (PCFG)** | A grammar is a set of rules for building valid code, such as "a call is a function followed by arguments". A *probabilistic* grammar also says how likely each rule is, learned by counting in real code. Multiplying the likelihoods of the rules used gives the likelihood of a whole piece of code. PCFG stands for probabilistic context-free grammar. |
| **Process / subprocess** | A running program. A subprocess is one started by another program; pkv runs pytest as a subprocess. |
| **Program / recipe** | A list of instructions a computer follows. |
| **pytest** | The most common tool for running automatic checks in Python projects. |
| **Python** | A popular programming language. Our code is written in it. |
| **Racy git** | A git timing trap: a file edited to the same size within the same second can look unchanged. It caused a pkv bug that is now fixed. |
| **Receipt (evidence)** | pkv's record of a check: what changed, which tests ran, the results, the fingerprint, and the verdict. Saved as JSON and Markdown. |
| **Regression gate** | A CI check that fails if quality drops, e.g. if any practice-set verdict changes. |
| **Regression test** | A test added because a bug was found, so that bug can never quietly come back. |
| **Release (tag)** | A permanent name for one exact snapshot (for example `pkv-v0.2.0`), published with ready-made files, so people install exactly what was tested. |
| **Replay study** | Checking real changes that real people made, one at a time, as if each were new. REAL-001 is ours. |
| **Repository (repo)** | A project folder tracked by git, usually stored on GitHub. |
| **Reproducibility** | Getting exactly the same results again from the same code and data. |
| **Script injection** | Untrusted text pasted into a command so it becomes part of the command. Prevented by passing inputs as environment variables. |
| **Search prior / habits** | Which building blocks the computer tries first. |
| **Secret scanning / push protection** | GitHub features that look for passwords and keys in code. Push protection goes further and refuses an upload that contains one. |
| **Seed / exam paper** | A number that generates one particular set of puzzles. The same number always produces the same puzzles, so results can be repeated exactly. |
| **Semantic Versioning** | Version numbers MAJOR.MINOR.PATCH: PATCH for fixes, MINOR for features, MAJOR for breaking changes. |
| **SPDX identifier** | A standard short name for a licence, such as `Apache-2.0`, written at the top of a file so tools know its licence. |
| **Stale result** | A test result from *before* the code last changed. It no longer proves anything about the current code. |
| **Stop rule** | A rule, written in advance, for when to abandon a line of work. |
| **Substrate** | The whole "material" the computer builds with: its blocks, fitting rules, building rules and habits. |
| **Tampering** | Changing the checks so that broken code passes, for example deleting a check or making it always pass. |
| **Temporal split** | Learning from the past and testing on the future, so the test can't leak into the learning. EXP-005 used each project's history this way. |
| **Test (automatic check)** | A small program that checks other code works, for example "adding 2 and 3 should give 5". |
| **Timeout** | A time limit. Tests that run longer are stopped. |
| **Tree hash** | A short fingerprint of the exact state of all the code. If even one character changes, the fingerprint changes. |
| **Tree-substitution grammar (TSG)** | A grammar whose rules can be whole ready-made chunks with gaps, not only single steps. Adding EXP-005's building blocks to a probabilistic grammar makes it one. |
| **Type** | What kind of thing something is: a list, a number, an action. Types decide what can snap together. |
| **Type checker** | A program that checks every part of the code receives the kind of value it expects. Ours is mypy. |
| **Untested change** | Changed code that no test reaches. 'All tests pass' says nothing about it. |
| **Validation gate / undo rule** | After each change, check the practice score; if it got worse, undo the change. |
| **Verdict** | pkv's one-word conclusion: VERIFIED, FAILED, UNVERIFIED or SUSPICIOUS. |
| **Wheel (`.whl`)** | The ready-built file of a Python package, the one `pip install` downloads. It's a zip file, so it can be checked by its fingerprint and unpacked without pip. |
