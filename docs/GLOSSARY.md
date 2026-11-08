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
| **Bootstrap / confidence range** | A way of checking whether a result could be luck: reshuffle the results thousands of times and see how much the answer wobbles. If the whole range of likely values is above zero, it's very unlikely to be luck. |
| **Budget** | How many tries the computer gets. Every student gets the same budget, so nobody wins by trying harder. |
| **Calibration / practice paper** | The one set of puzzles (number 100) we used to build and fix the system. The real exam papers were kept unseen. |
| **CI (Continuous Integration)** | A service that automatically runs a project's checks every time someone changes the code, for example GitHub Actions. *(In the technical appendix, "CI" means confidence interval instead, which is the confidence range above.)* |
| **CLI (command-line tool)** | A program you run by typing a command in the Terminal instead of clicking buttons. |
| **Commit / snapshot** | A saved copy of the whole project at one moment, made with git. You can always go back to it. |
| **Compression / shortening** | Judging a shortcut by how much shorter it makes your *old* solutions. That's the usual method, and our experiment found it picks the wrong shortcuts. |
| **Condition** | One "student" in our experiment, meaning one version of the computer with certain features switched on or off. |
| **Data slot** | A blank in a shortcut that takes a thing, such as a list or a number. Compare *action slot*. |
| **Deprecation / pruning** | Throwing away shortcuts that aren't useful any more. |
| **Diff** | The list of exactly what changed in the code: which files, which lines added and which removed. |
| **DSL (domain-specific language)** | The small, fixed set of basic actions the computer starts with. Ours has 26. |
| **Enumeration / search** | Trying possible recipes one by one, simplest first. |
| **Evaluator / exam marker** | The part that marks the results. It's fixed, and the learner can never change it, so it can't cheat. |
| **Exploratory result** | Something we noticed but didn't predict in advance. It's a lead to follow up, not proof. |
| **git** | A free program that saves snapshots of a project so you can see every change and go back to any earlier version. |
| **GitHub** | A website where programmers store code and publicly report problems with software. |
| **Hypothesis** | A prediction written down *before* the experiment, so we can't move the goalposts afterwards. |
| **Import / import graph** | In Python, one file "imports" another to use its code. The import graph is the map of which files use which. We use it to work out which checks a change could affect. |
| **Library** | The computer's growing collection of saved shortcuts. |
| **MDL (minimum description length)** | The technical name for *compression / shortening*. |
| **Module** | One Python code file, or a folder of them. |
| **Negative control** | A test where the method *should not* help, like our random puzzles. If it helps there too, something is fishy. |
| **Open source** | Code anyone may read, use and improve for free. |
| **Oracle / cheat student** | A student secretly given the right answers' building blocks. It shows the best possible score, which tells us whether our exam can detect improvement at all. |
| **pkv / Parinama Verify** | Our first product: an independent checker for code changes made by AI. |
| **Points / pp (percentage points)** | Our scores are "puzzles solved out of 100". "+3 points" means 3 more puzzles out of 100. |
| **Positive control** | A test where the method *should* help, like the cheat student. If it doesn't, the exam is broken. |
| **Pre-registration** | Writing down predictions and success rules before running an experiment. |
| **Primitive** | A basic building block, one of the starting actions. |
| **Program / recipe** | A list of instructions a computer follows. |
| **pytest** | The most common tool for running automatic checks in Python projects. |
| **Python** | A popular programming language. Our code is written in it. |
| **Repository (repo)** | A project folder tracked by git, usually stored on GitHub. |
| **Search prior / habits** | Which building blocks the computer tries first. |
| **Seed / exam paper** | A number that generates one particular set of puzzles. The same number always produces the same puzzles, so results can be repeated exactly. |
| **Stale result** | A test result from *before* the code last changed. It no longer proves anything about the current code. |
| **Substrate** | The whole "material" the computer builds with: its blocks, fitting rules, building rules and habits. |
| **Tampering** | Changing the checks so that broken code passes, for example deleting a check or making it always pass. |
| **Test (automatic check)** | A small program that checks other code works, for example "adding 2 and 3 should give 5". |
| **Tree hash** | A short fingerprint of the exact state of all the code. If even one character changes, the fingerprint changes. |
| **Type** | What kind of thing something is: a list, a number, an action. Types decide what can snap together. |
| **Validation gate / undo rule** | After each change, check the practice score; if it got worse, undo the change. |
