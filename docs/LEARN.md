# Learn everything in this project, from zero

This is a course that teaches every idea used in Parinamakramam, in order, starting from nothing. Each lesson has six parts:

1. **🖼 Picture.** An everyday comparison.
2. **📖 The real word.** The term professionals use, so you can read papers and talk to anyone.
3. **🎯 Precisely.** The correct meaning. Simple doesn't mean wrong: every picture here is accurate, and where a picture stops working, the lesson says so.
4. **📍 In our project.** Where you can see it in our files.
5. **🛠 Try it.** Something to type or open. Commands go in the **Terminal** app, the program where you type instructions to the computer.
6. **✅ Check yourself.** A question to test yourself. Click to see the answer.

Go in order: each lesson builds on the previous ones. One lesson a day takes 33 days, but you can go faster. Words are also listed in the [Glossary](GLOSSARY.md).

---

# Part A: How code works

## Lesson 1. What a program is

🖼 **Picture.** A recipe: exact steps, followed in order, by someone who does *exactly* what is written and nothing else.

📖 **The real words.**
- **Program**, **code**, **source code**.
- **Programming language**: the language a recipe is written in. Ours is **Python**.
- **Running** or **executing** a program.

🎯 **Precisely.** A program is text that a computer can follow step by step. Python reads your text and carries out each instruction. That makes Python an **interpreter**: a program that runs other programs. Computers have no common sense: if the recipe says "add salt" twice, they add it twice.

📍 **In our project.** Every file ending in `.py` is a Python program. For example, `research/pevo/run_exp001.py` runs the whole experiment.

🛠 **Try it.** Type this into Terminal:

```bash
python3 -c "print(2 + 3)"
```

You told Python to run a one-line program, and it printed `5`.

✅ **Check yourself.** Why do programs need to be so exact?
<details><summary>Answer</summary>Because the computer does exactly what's written, with no guessing. Ambiguity that a human would resolve sensibly becomes a mistake (a <b>bug</b>) in a program.</details>

## Lesson 2. Files, folders and paths

🖼 **Picture.** A postal address: country → city → street → house.

📖 **The real words.** **File**, **folder** (also called a **directory**), **path**.
- An **absolute path** starts from the very top of the computer.
- A **relative path** starts from "where I am now".

🎯 **Precisely.** `/Volumes/projects/hope/parinamakramam/README.md` is an absolute path. Seen from inside the `parinamakramam` folder, the same file is simply `README.md` (a relative path). The `/` separates the levels.

📍 **In our project.** Our tool prints relative paths like `tests/test_utils.py`.

🛠 **Try it.** These commands move into the project and list what's there. `cd` means "change directory"; `ls` means "list".

```bash
cd /Volumes/projects/hope/parinamakramam && ls
```

✅ **Check yourself.** Is `docs/GLOSSARY.md` absolute or relative?
<details><summary>Answer</summary>Relative. It doesn't start with <code>/</code>, so it only makes sense from the <code>parinamakramam</code> folder.</details>

## Lesson 3. Functions: inputs and outputs

🖼 **Picture.** A juicer: oranges go in, juice comes out. You don't need to know how it works inside to use it.

📖 **The real words.**
- **Function**: a named mini-program.
- **Input** (also called an **argument** or **parameter**): what goes in.
- **Output** (also called the **return value**): what comes out.

🎯 **Precisely.** `def double(x): return x * 2` defines a function named `double`. Then `double(4)` gives `8`.

Functions can also take *other functions* as input. These are called **higher-order functions**. For example, `map(double, [1, 2, 3])` applies `double` to every item and gives `[2, 4, 6]`. Remember this idea: it's the "action slot" at the heart of our research.

📍 **In our project.** The 26 building blocks in `research/pevo/pevo/dsl.py` are functions: `sort`, `reverse`, `map`, `filter`…

🛠 **Try it.** This defines `double` and uses it with `map`:

```bash
python3 -c "
def double(x): return x * 2
print(list(map(double, [1, 2, 3])))"
```

✅ **Check yourself.** In "sort, then do ___ to every number", what kind of thing fills the blank?
<details><summary>Answer</summary>A function, such as "double" or "add 1". The blank takes an action, not a number. That's what makes it higher-order.</details>

## Lesson 4. Tests: code that checks code

🖼 **Picture.** A tasting spoon. After cooking, you taste to check the dish is right before serving it.

📖 **The real words.**
- **Test**, **assertion** (in code: **assert**).
- **Test suite**: all the tests together.
- **pytest**: the tool that finds and runs Python tests.
- A test **passes** or **fails**.

🎯 **Precisely.** `assert double(4) == 8` means: "if this isn't true, stop and report a failure". pytest looks for files named `test_*.py`, runs every function inside named `test_…`, and reports which passed and which failed.

**Important limit:** passing tests prove only what they check. A test that checks nothing (`assert True`) always passes. That's exactly the kind of trick our product catches.

📍 **In our project.**
- `research/pevo/tests/test_pevo.py` holds 11 tests.
- `product/verify/tests/test_pkv.py` holds 27 tests.

🛠 **Try it.** This runs the 11 research tests. You'll see `11 passed`.

```bash
cd /Volumes/projects/hope/parinamakramam/research/pevo && uv run --no-project --python 3.14 --with pytest python -m pytest -q tests
```

✅ **Check yourself.** An AI changes your code, then deletes the one test that was failing. Do "all tests pass"?
<details><summary>Answer</summary>Yes, and that's the problem. The claim is true but meaningless, because the check that would have caught the bug is gone. This is called <b>test tampering</b>.</details>

---

# Part B: Working like a professional

## Lesson 5. git: the project's time machine

🖼 **Picture.** Saving a game. Each save point lets you return to exactly that moment, and a list shows every save point and what changed between them.

📖 **The real words.**
- **git**: the tool.
- **Repository** (**repo**): a project tracked by git.
- **Commit**: a save point, or snapshot.
- **Commit message**: a note on what changed and why.
- **Diff**: the exact differences between two versions.
- **Hash**: the fingerprint that names each snapshot.

🎯 **Precisely.** A commit stores the whole project's state, plus who made it, when, and a message. Each commit is named by a **hash**: a long code calculated from its contents (for example `fe5edc4…`). If anything differs, the hash differs. That's why a hash can prove *exactly* which code an experiment used.

📍 **In our project.** Our first snapshot is `fe5edc4`. It holds the original technical versions of every document.

🛠 **Try it.** The first command shows the list of snapshots. The second shows what has changed since the last one.

```bash
cd /Volumes/projects/hope/parinamakramam && git log --oneline
```

```bash
cd /Volumes/projects/hope/parinamakramam && git status
```

✅ **Check yourself.** Why does the experiment registry name a commit hash?
<details><summary>Answer</summary>So anyone can get back the exact code that produced the results and re-run it. Without that, "our results" could silently drift as the code changes. This idea is called <b>reproducibility</b>.</details>

## Lesson 6. Branches and the merge base

🖼 **Picture.** Photocopy a document and edit the copy while someone else edits the original. Later you combine the two. To see *your* edits only, you compare your copy with the version as it was when you made the photocopy, not with the original as it is today.

📖 **The real words.**
- **Branch**: a line of work.
- **main**: the main branch.
- **Merge**: combining two branches.
- **Merge base**: the point where your branch split off.

🎯 **Precisely.** `pkv affected --base main` compares your files with the merge base of `main` and your work. That way, other people's later changes on `main` don't get mixed up with yours. GitHub pull requests show changes the same way. One of our self-checks (`test_base_branch_compares_from_where_work_branched_off`) proves this works.

✅ **Check yourself.** If you compared with today's `main` instead, what would go wrong?
<details><summary>Answer</summary>Changes other people made to <code>main</code> after you branched off would look like your changes, so the tool would run tests you didn't affect.</details>

## Lesson 7. GitHub, issues, pull requests and CI

🖼 **Picture.**
- GitHub is a shared library building for projects.
- **Issues** are its public complaints book.
- **Pull requests** are formal proposals: "please accept my changes".
- **CI** is a robot assistant who automatically re-checks every proposal.

📖 **The real words.**
- **GitHub**, **issue**, **pull request (PR)**, **code review**.
- **CI**, which stands for **continuous integration**.
- **GitHub Actions**: GitHub's CI robot.

🎯 **Precisely.** CI is a service that runs a project's tests automatically on every change. Our product will eventually run inside CI, because there the AI that wrote the code can't interfere with the checking. That gives a real **separation of duties**: whoever does the work isn't the one who checks it.

📍 **In our project.** The evidence in [P001](product/P001-first-workflow-public-evidence.md) comes from public GitHub issues.

✅ **Check yourself.** Why is running checks inside CI more trustworthy than letting the AI report its own results?
<details><summary>Answer</summary>The AI can't edit or fake the results there. It's the same reason an exam is marked by someone other than the student.</details>

---

# Part C: The research

## Lesson 8. Program search: finding a recipe from examples

🖼 **Picture.** Someone shows you `[3,1,2] → [1,2,3]` and `[5,4] → [4,5]` and asks: what's the rule? You try simple guesses first ("reverse?" no; "sort?" yes!).

📖 **The real words.**
- **Program synthesis**: writing programs automatically.
- **Programming by example**: synthesis from input/output examples.
- **Search** and **enumeration**: trying candidate programs systematically.
- **Bottom-up search**: building big programs out of small ones.
- **Search budget**: how many tries are allowed.

🎯 **Precisely.** Our search tries programs in order of **cost**, which is roughly their size, cheapest first.

It also skips duplicates. If `reverse(reverse(x))` produces exactly the same outputs as `x` on every example, it's a duplicate and is dropped. This trick is called **observational equivalence**, and it saves a huge amount of work.

The budget counts **distinct results tried**. That's fair across computers of different speeds.

📍 **In our project.** `research/pevo/pevo/enumerate.py`.

✅ **Check yourself.** Why must a correct recipe also work on 4 *hidden* examples?
<details><summary>Answer</summary>A recipe can fit the visible examples by coincidence without being the real rule. Hidden examples catch that. This is called checking <b>generalisation</b> on <b>held-out</b> data, and it prevents <b>overfitting</b>.</details>

## Lesson 9. Building blocks, types and languages

🖼 **Picture.** LEGO bricks, and the studs that decide which bricks can join.

📖 **The real words.**
- **Primitive**: a basic building block.
- **DSL (domain-specific language)**: a small set of primitives built for one kind of task.
- **Type**: what kind of value something is (list, number, function).
- **Type system**: the rules for which types fit together.
- **Grammar**: the rules for which combinations are allowed.

🎯 **Precisely.** `sort` takes a list and gives a list (written `List → List`). `sum` takes a list and gives a number (`List → Int`). So `sum(sort(x))` is allowed but `sort(sum(x))` is not, because `sort` can't take a number. Types shrink the search enormously, since nonsense combinations are never tried.

📍 **In our project.** `research/pevo/pevo/dsl.py`, with its 26 primitives and 4 types.

✅ **Check yourself.** Is `map(double, sort(x))` allowed?
<details><summary>Answer</summary>Yes. <code>sort(x)</code> gives a list, and <code>map</code> takes a function (<code>double</code>) and a list, and gives a list.</details>

## Lesson 10. Shortcuts: abstraction and library learning

🖼 **Picture.** The masala-base jar. A combination you keep making, saved ready to use.

📖 **The real words.**
- **Abstraction**: a reusable piece with blanks.
- **Hole** (or **parameter**): a blank.
- **Library learning**: automatically discovering abstractions.
- **Higher-order hole**: a blank that takes a function. These are our "action slots".

🎯 **Precisely.** From the solution `map(double, sort(x))`, you can make the abstraction `f(□) = map(□, sort(x))`, where the blank takes any number-to-number function. Adding it means `map(add1, sort(x))` becomes a single cheap step. That lowers its cost, so search finds it within the budget.

**The catch:** every added abstraction also adds options at every step of the search, so useless ones slow it down. This tension is called the **branching-factor trade-off**.

📍 **In our project.** `research/pevo/pevo/abstraction.py`.

✅ **Check yourself.** Why can adding a shortcut make search *worse*?
<details><summary>Answer</summary>The search now has more options to try at every step, so useless shortcuts waste the budget. Our random-shortcut student (C-random) showed exactly this.</details>

## Lesson 11. How to choose shortcuts: looking back vs looking forward

🖼 **Picture.** Two students make revision notes.
- Student 1 summarises the chapters they've already mastered. That's neat, but useless for the exam.
- Student 2 makes notes for the chapter they keep failing.

📖 **The real words.**
- **Compression**, or **MDL (minimum description length)**: prefer whatever describes your past solutions most briefly. This is **retrospective** (looking back).
- **Prospective** selection (looking forward): prefer whatever helps future or unsolved problems.
- **Utility**: how useful something is.

🎯 **Precisely.** Our compression score is `uses × (size − 1) − size`, which means "how many symbols this shortcut saves across old solutions".

Our experiment showed it picks shortcuts for problems already solved. A May 2026 paper found that humans choose prospectively instead. Our next experiment, EXP-002, tries prospective selection: building shortcuts from *near-miss* attempts on unsolved puzzles.

✅ **Check yourself.** Which of the two students is our Student C, and which does EXP-002 try to build?
<details><summary>Answer</summary>Student C is Student 1, who looks back. EXP-002 tries to build Student 2, who looks forward.</details>

## Lesson 12. Designing a fair experiment

🖼 **Picture.** Testing a new fertiliser. You need a plant with no fertiliser to compare against, and the same sun and water for every plant. You also decide in advance how much taller counts as "it works".

📖 **The real words.**
- **Baseline**: the plain comparison. Ours is Student A.
- **Treatment** or **condition**: the version being tested.
- **Control**: a comparison designed to rule out other explanations.
  - A **positive control** *should* show an effect. Ours is the cheat student. If it doesn't, the test is broken.
  - A **negative control** *should not* show an effect. Ours is the random puzzles.
- **Ablation**: switching off one part to see what it contributes. Ours are the "D without…" students.
- **Pre-registration**: writing predictions and success rules before running.
- **Training / test split**: the material you learn from vs the material you're examined on.
- **Calibration set**: material reserved for tuning. Ours is paper 100.
- **Seed**: a number that fixes the random choices, so a run can be repeated exactly.

🎯 **Precisely.** We built every one of these in. The most important is that **the 10 exam papers were never looked at while building**. Otherwise you can unknowingly tune your method to the exam, and your results won't hold up anywhere else. That failure is called **overfitting to the test set**.

📍 **In our project.** [EXPERIMENT_REGISTRY.md](../governance/EXPERIMENT_REGISTRY.md), and decisions D-005 to D-007 in [DECISION_LOG.md](../governance/DECISION_LOG.md).

✅ **Check yourself.** If the cheat student had scored the same as Student A, what would we have concluded?
<details><summary>Answer</summary>That the exam can't detect the benefit of good building blocks, so none of the other comparisons would mean anything. We'd fix the exam first. The positive control passed, so the exam works.</details>

## Lesson 13. Is it real or luck? Basic statistics

🖼 **Picture.** You flip a coin 10 times and get 6 heads. Is the coin unfair? Probably not: 6 out of 10 happens by luck all the time. Our scores have the same problem: each exam paper is a bit easier or harder by chance.

📖 **The real words.**
- **Mean**: the average.
- **Variance** or **noise**: how much results wobble by chance.
- **Paired comparison**: compare two students *on the same paper*, which cancels out paper difficulty.
- **Bootstrap**: a resampling method for estimating uncertainty.
- **Confidence interval (CI)**: a range of plausible values for the true difference.
- **Effect size**: how big the difference is.
- **Threshold**: the minimum effect we decided in advance would count.
- **Percentage points (pp)**: a difference between two percentages. 58% to 61% is +3 pp.

🎯 **Precisely.**
1. For each of the 10 papers, take the difference (Student D's score − Student C's score). That gives 10 numbers.
2. **The bootstrap:** randomly pick 10 of those numbers *with replacement* (so the same paper can be picked twice), and average them. Repeat thousands of times.
3. The middle 95% of all those averages is the **95% confidence interval**.

How to read the interval:
- If it's entirely above 0, the improvement is very unlikely to be luck.
- If it includes 0, we can't rule out luck.
- The precise statement is this: if we repeated the whole experiment many times, intervals built this way would contain the true difference about 95% of the time.

We also required **at least +5 points**, because a real but tiny effect isn't worth building a company on.

📍 **In our project.** In the [technical appendix](research/R001-technical-appendix.md), D vs C was **+1.2 points, interval −2.8 to +4.8**. The interval includes 0, so that's a fail. E vs C was **+4.0, interval +1.0 to +6.8**. That's real, but below 5, so it officially failed.

✅ **Check yourself.** Student E's interval was +1.0 to +6.8. Is the effect real? Did it pass?
<details><summary>Answer</summary>It's probably real, because the whole interval is above 0. But it did not pass, because the average (+4.0) is below the +5 threshold we set in advance. Being honest means not moving that line afterwards.</details>

## Lesson 14. Reading our results like a scientist

🎯 **The three findings, stated correctly:**
1. **Benchmark validity.** The positive control beat the baseline by +18.5 pp, interval [+15.2, +21.8], on 10 of 10 papers. So the exam can detect good building blocks.
2. **Negative result on the core hypothesis.** The full idea did not beat ordinary library learning, and the interval includes 0. "Not supported" is different from "proven false": our *methods of discovery* failed. The idea might still work with better discovery.
3. **The exchange rate.** The right library was worth as much as 15× more search budget (76.5% vs 76.3%). This becomes our yardstick: "a library is worth N× search".

**What we must *not* say:** "evolving building blocks doesn't work", or "it works in real AI". Both claims go beyond what was tested. Generalising beyond your evidence is called **over-claiming**, and it's the most common mistake in AI research.

📍 **In our project.** [R001](research/R001-primitive-evolution-prior-art-and-thesis.md), sections 6.4 and 6.5.

---

# Part D: The product

## Lesson 15. The import graph and static analysis

🖼 **Picture.** A city map of one-way roads. File A has a road to file B if A uses B.

📖 **The real words.**
- **Import**: one file using another.
- **Dependency**: B is a dependency of A if A uses B.
- **Graph**: dots joined by lines. The dots are **nodes**; the lines are **edges**.
- **Import graph**: the graph of which files import which.
- **Static analysis**: reading code without running it.
- **Abstract syntax tree (AST)**: the structured form Python turns code into before running it.
- **Dynamic import**: code that decides at run time what to load, which static analysis can't see.

🎯 **Precisely.** Our tool turns each file into an AST using Python's built-in `ast` module, finds every `import` statement, and works out which project file each import refers to. It never runs the user's code, which is a safety property.

It handles:
- packages (folders containing `__init__.py`);
- relative imports (`from ..models import User`);
- the "src layout" (code kept inside a `src/` folder).

📍 **In our project.** `product/verify/pkv/imports.py`.

✅ **Check yourself.** Why is "never runs the user's code" important for a checker?
<details><summary>Answer</summary>The code being checked might be broken, or even malicious. Reading it is safe; running it during analysis isn't. The checker must not be harmed by, or fooled by, what it checks.</details>

## Lesson 16. Finding affected tests: breadth-first search

🖼 **Picture.** Drop dye into the river at the changed file and see which test files it reaches, flowing *backwards* along the roads.

📖 **The real words.**
- **Reverse dependencies**: everything that depends on a file.
- **Breadth-first search (BFS)**: visit all direct neighbours first, then their neighbours, and so on.
- **Transitive dependency**: an indirect one, as in "A uses B, which uses C".
- **Test impact analysis** (or **affected-test selection**): working out which tests a change could break.
- **Conservative**: when unsure, choose the safe option.

🎯 **Precisely.** We start from each changed file and do a BFS over reverse dependencies, remembering how we reached each file. That's how the tool can explain itself: *"test_api.py uses app/api.py, which uses app/models.py, which was modified."*

Special cases:
- Shared test settings (`conftest.py`) affect every test in their folder and below.
- A project settings file affects every test in its folder.
- A change it can't trace means "run every test".

📍 **In our project.** `product/verify/pkv/affected.py`.

🛠 **Try it.** Run the tool on our own project:

```bash
cd /Volumes/projects/hope/parinamakramam && PYTHONPATH=product/verify python3 -m pkv affected
```

✅ **Check yourself.** Why does an unknown data file trigger "run everything" instead of "run nothing"?
<details><summary>Answer</summary>Running too many tests costs a little time. Running too few can let a real bug through, and the tool would then wrongly say "verified". For a checker, a false "all clear" is the worst possible failure.</details>

## Lesson 17. Fingerprints and stale results

🖼 **Picture.** A photo of a receipt is only proof of the purchase on that receipt. If the shopping bag changed afterwards, the photo proves nothing about the new bag.

📖 **The real words.**
- **Hash function**: turns any content into a short fingerprint.
- **Tree hash**: git's fingerprint of a whole folder's contents.
- **Stale**: out of date.
- **Provenance**: a record of where a result came from.

🎯 **Precisely.** The tool records the tree hash before and after running tests. If the hash now differs from the one at test time, the result is stale. So *"tests passed"* becomes a checkable claim: *"tests passed on code with fingerprint X, and the code is still X."* Our fingerprint includes unsaved edits and new files, but never disturbs the user's own staging area (proven by a self-check).

🛠 **Try it.** This prints the current fingerprint. Edit any file, run it again, and the code changes.

```bash
cd /Volumes/projects/hope/parinamakramam && PYTHONPATH=product/verify python3 -m pkv fingerprint
```

✅ **Check yourself.** An AI runs the tests, then edits one more line, then says "tests pass". What does pkv say?
<details><summary>Answer</summary>That the result is stale. The fingerprint changed after the tests ran, so they no longer prove anything about the current code. (This part is coming in the next version.)</details>

## Lesson 18. Tampering and why independence matters

🎯 **Precisely.** The common ways tests get gamed:
- deleting tests;
- removing assertions;
- adding `skip` or `xfail` (which means "expected to fail");
- tautologies like `assert True`;
- editing the expected answers at the same time as the code.

None of these are bugs in the *code*; they're bugs in the *evidence*. That's why the checker must be **independent**: separate from the AI that wrote the code, using no AI judgement, producing only recorded facts.

The general principle is that a **generator** (whatever does the work) must never be its own **evaluator** (whatever judges the work). Our research follows the same rule: the learner can never change the exam marker.

---

# Part E: The AI landscape

## Lesson 19. Neural networks and large language models

🎯 **Precisely.**
- A **neural network** is a mathematical function with millions or billions of adjustable numbers, called **parameters** or **weights**.
- **Training** adjusts the weights so the outputs get better at a task.
- A **large language model (LLM)**, like the one writing this, is a neural network trained to predict the next piece of text (a **token**).
- An **AI agent** is an LLM that can also take actions, like editing files and running commands, in a loop.
- **Inference** means running a trained model. It costs money in computing power every time.

That's why a product that needs no inference (like ours) costs almost nothing per user.

## Lesson 20. Evolution as a search method

🖼 **Picture.** A plant breeder: make many variants, keep the best, cross them, repeat.

📖 **The real words.**
- **Evolutionary algorithm**; **population**.
- **Fitness**: a score of how good something is.
- **Mutation**: a random change. **Crossover**: mixing two parents.
- **Quality-diversity**: keeping many *different* good solutions, not just the single best.
- **Model merging**: combining the weights of trained models.

🎯 **Precisely.** Sakana AI uses evolutionary search to find good ways to merge existing models. Quality-diversity methods (like their CycleQD) keep a varied population, because today's second-best might be tomorrow's best parent.

The Darwin Gödel Machine applies evolution to an agent's own code, and keeps only versions that score better on real tests. This is called **empirical validation**.

✅ **Check yourself.** What's the difference between Sakana's model merging and our research question?
<details><summary>Answer</summary>Merging recombines existing parts, like shuffling genes. We ask how to invent new building blocks and new joining rules, like inventing new genes and new ways of combining them.</details>

---

# Part F: The business

## Lesson 21. Open source and licences

🎯 **Precisely.**
- **Open source** means the code is public and others may use it, under the terms of a **licence**. Common licences:
  - **MIT** and **Apache-2.0** are *permissive*: anyone may use the code, even commercially. Apache-2.0 also includes protection around patents.
  - **GPL** is *copyleft*: anyone who distributes changed versions must share them under the same terms.
- **Choosing our licence is your decision** (it's listed as an open question in PROJECT_STATE).
- Licences also matter for research data. **Never train on code whose licence doesn't allow it**, and never on private customer code without permission. That's one of our founding rules.

## Lesson 22. How a free tool becomes a business

🎯 **Precisely.**
- **Freemium**: the core tool is free; teams pay for extras like history, dashboards and enforcement.
- **Unit economics**: the cost and revenue per user. Ours are excellent, because there's no inference cost.
- **Platform risk**: a bigger company you depend on, or compete next to, might build your feature. Ours is that AI tool makers add their own verification.
- **Moat**: whatever makes you hard to copy. Ours would be neutrality (we work with every AI tool), trust, and being the best at this one narrow job.
- **Signals without interviews**: downloads, installs, retention (people keep using it), and payment.

## Lesson 23. Why we keep a decision log, a registry and a state file

🎯 **Precisely.** These are the habits of a disciplined lab and company:
- The **decision log** stops us forgetting *why* we chose something, so we don't undo good decisions by accident.
- The **registry** stops us moving goalposts after seeing results.
- The **state file** lets anyone, including a new Claude session, pick up exactly where we left off.

Together they make the company **auditable**: every claim can be traced back to its evidence.

---

# Part G: How careful engineers check their own work

## Lesson 24. Processes, exit codes and environment variables

🖼 **Picture.**
- A **process** is a worker the computer hires to follow one program.
- When the worker finishes, they hand back a slip with one number: the **exit code**.
- Every worker also carries a backpack of notes from whoever hired them: the **environment variables**.

📖 **The real words.**
- **Process**; **subprocess** (a process started by another process).
- **Exit code**, also called **return code** or **exit status**.
- **Environment variable**: a named setting such as `PATH` or `HOME`.
- **Timeout**: a time limit.

🎯 **Precisely.**
- By convention, exit code 0 means success and anything else means some kind of failure. pytest uses 0 for "all passed", 1 for "some failed", 2 for "interrupted", and 5 for "no tests found".
- Environment variables often hold **secrets**, like `GH_TOKEN`, the key to a GitHub account. Any program you start can read them unless you remove them first.
- pkv starts pytest as a subprocess with a **minimal environment**: only `PATH`, `HOME` and similar. So a test, or something malicious hidden in a test, can't read your tokens.
- If the tests run past the timeout, pkv stops the whole **process group**: the tests plus anything they started.

📍 **In our project.** `product/verify/pkv/runner.py`. The self-check `test_runner_hides_secrets_unless_asked` proves the secret is hidden.

🛠 **Try it.** The first line runs `true`, which always succeeds, then prints its exit code. The second does the same with `false`, which always fails.

```bash
true; echo $?
```

```bash
false; echo $?
```

✅ **Check yourself.** Why does pkv give back exit code 4 for SUSPICIOUS, not 0?
<details><summary>Answer</summary>Robots like GitHub Actions only read the exit code. Anything other than 0 makes them stop and refuse the change, which is exactly what should happen when tests were weakened.</details>

## Lesson 25. Verdicts and the cost of a wrong "all clear"

🎯 **Precisely.** A checker can make two kinds of mistake:
- A **false alarm** (a *false positive*): it says "problem" when there isn't one. That's annoying; you lose a few minutes.
- A **missed problem** (a *false negative*): it says "all clear" when there's a problem. That's dangerous, because broken code ships with a stamp of approval.

pkv is deliberately built to prefer false alarms. Unsure means run more tests, and weaker evidence means UNVERIFIED rather than VERIFIED.

That's also why **"changed code that no test checks"** gives UNVERIFIED. "All tests pass" is true, but says *nothing* about that code. The evidence doesn't cover the claim.

✅ **Check yourself.** Every test passed, but the change deleted one test. Which verdict is right, and why?
<details><summary>Answer</summary>SUSPICIOUS. The passing result can't be trusted, because the deleted test might be exactly the one that would have failed. Weakened evidence outranks passing tests.</details>

## Lesson 26. Testing the tests: regression tests, dogfooding and mutation testing

🖼 **Picture.**
- A **regression test** is like a smoke alarm installed in the exact spot where a fire once started.
- **Dogfooding** is a chef eating their own cooking every day.
- **Mutation testing** is deliberately leaving the stove on to check the smoke alarm really beeps.

📖 **The real words.**
- **Regression**: something that used to work breaks again.
- **Regression test**: a test added *because* a bug was found, so that bug can never quietly return.
- **Dogfooding**: using your own product yourself.
- **Mutation testing**: deliberately introducing a bug (a *mutant*) and checking a test fails. If no test fails, the mutant "survived", and your tests have a blind spot.

🎯 **Precisely.** Using pkv on our own project found 5 real mistakes within minutes, and each now has a regression test. Then we broke three safeguards on purpose. Two were caught. The third survived, revealing a missing test, which we added. Now all three are caught.

This is the same honesty principle as our research. A check you've never seen fail could be checking nothing at all, like the `assert True` our product hunts for.

📍 **In our project.** The "found by running pkv on our own project" sections in `product/verify/tests/test_check.py`.

✅ **Check yourself.** You deliberately break the code and every test still passes. What have you learned?
<details><summary>Answer</summary>Your tests have a blind spot: nothing checks that behaviour. Add a test that fails on the broken version and passes on the correct one.</details>

## Lesson 27. Monorepos and settings files

🎯 **Precisely.**
- A **monorepo** is one repository holding several projects. Ours holds two: `research/pevo` and `product/verify`.
- Each project can have its own **settings file** for pytest (`pytest.ini`, or a `[tool.pytest…]` section in `pyproject.toml`).
- One pytest run uses exactly one settings file, chosen from the folders above the tests it's given.
- So pkv **groups tests by sub-project** and runs each group separately, with the overall result being the most serious one.
- The setting `pythonpath = .` tells pytest where a project's own code lives, so the tests can find it from any folder.

📍 **In our project.** `research/pevo/pytest.ini`, `product/verify/pyproject.toml`, and `group_by_project` in `runner.py`.

---

# Part H: Working at a professional standard

## Lesson 28. Benchmarks, held-out sets and the forking-paths trap

🖼 **Picture.** A driving instructor who only ever tests you on the same route. You could memorise that route without learning to drive. A fair examiner keeps a **second route you've never seen**.

📖 **The real words.**
- **Benchmark**: a fixed set of test situations.
- **Held-out set**: situations deliberately kept apart from the ones used for improving.
- **Overfitting**: becoming good at the test rather than at the skill.
- **Garden of forking paths**: if you try many small variations and keep the one that looks best, you'll find "improvements" that are really just luck.
- **Freezing a design**: committing to settings *before* the real test.

🎯 **Precisely.**
- pkv's rules were improved using only BENCH-001's misses. BENCH-002 was written and saved *before* those improvements.
- The held-out score doubled (5 → 10 of 13), which is evidence the rules generalise.
- In EXP-002, the design allowed small adjustments after one calibration paper. We **didn't use them**: differences of ±2 points on one paper are smaller than the noise between papers, so choosing by them would be choosing by luck.

📍 **In our project.** `product/verify/benchmark/`; decision D-023; [EXPERIMENT_REGISTRY.md](../governance/EXPERIMENT_REGISTRY.md).

✅ **Check yourself.** After seeing BENCH-002's results, can we now improve pkv using BENCH-002 and still call its score "held out"?
<details><summary>Answer</summary>No. Once you've looked at it and changed the tool because of it, it's no longer held out. The next improvement needs a fresh set (BENCH-003) written before the change.</details>

## Lesson 29. Reproducing results before touching frozen code

🖼 **Picture.** Re-baking a prize-winning cake after reorganising the kitchen. If it doesn't taste *exactly* the same, the reorganisation changed something.

📖 **The real words.**
- **Reproducibility**: getting the same results again.
- **Refactoring**: changing how code is written without changing what it does.
- **Behaviour-preserving change**: one that provably changes nothing observable.

🎯 **Precisely.** Twice today we changed shared research code: first a tidy-up, then letting the search return its bank. Each time we re-ran all 200 EXP-001 runs and compared every result file with the published ones. They were identical apart from timing fields. Only then was the change accepted. Without this, an "harmless" edit could silently change published science.

## Lesson 30. Linters, type checkers and continuous integration

🖼 **Picture.**
- A **linter** is a proof-reader for code.
- A **type checker** checks that every part receives the kind of thing it expects, like a plug fitting its socket.
- **CI** is a robot that runs every check on every upload.

📖 **The real words.**
- **Linter**: ours is `ruff`.
- **Static type checking**: ours is `mypy --strict`.
- **CI pipeline**: GitHub Actions, with several **jobs**.
- **Regression gate**: CI fails if quality drops.
- **Flaky**: a result that changes between runs.

🎯 **Precisely.** These tools found real problems today:
- The linter found a research self-check that **claimed more than it tested**.
- The type checker found a **crash** on `pytestmark: list`.
- Running the practice set twice exposed **non-determinism**, and its cause: the "racy git" fingerprint bug.
- CI caught an over-long line from a scripted edit.

`scripts/check-all.sh` runs the same checks locally before uploading.

## Lesson 31. GitHub Actions and script injection

🖼 **Picture.** A form whose "name" box gets pasted directly into an instruction for a robot. If someone writes "Bob; also delete everything" as their name, the robot obeys.

📖 **The real words.**
- **GitHub Action**: a reusable workflow step.
- **Composite action**: one made of shell steps.
- **Script injection**: untrusted text pasted into a command so that it *becomes* part of the command.

🎯 **Precisely.**
- Our action passes every input (branch names, settings) through **environment variables** and quotes them, never pasting `${{ … }}` text into the command itself. GitHub's security guidance recommends exactly this.
- A rehearsal also caught a subtle bug: a failed run could display an **old receipt** left on the machine. The action now deletes old receipts first.

## Lesson 32. Versions and changelogs

📖 **The real words.**
- **Semantic Versioning** (MAJOR.MINOR.PATCH): PATCH for bug fixes, MINOR for new features, MAJOR for changes that break existing use.
- **Changelog**: a dated list of what changed in each version.

🎯 **Precisely.** pkv went 0.0.1 → 0.0.2 (two bug fixes) → 0.1.0 (new detection rules). Before 1.0, anything may change. [CHANGELOG.md](../CHANGELOG.md) records each step, including how every bug was found and tested.

## Lesson 33. Negative results and stop rules

🎯 **Precisely.**
- EXP-002's idea, learning building blocks from near misses, **failed** its pre-registered test (−2.3 points against C3). My own guess had been a small gain.
- A professional records this as clearly as a success, explains the likely reason (programs with close *outputs* don't share the right *structure*), and follows the **stop rule** written in advance: at most one more variant, then move on.
- Stop rules protect a one-person company's most limited resource, which is time.

✅ **Check yourself.** Why write the stop rule *before* seeing the result?
<details><summary>Answer</summary>After a disappointing result it's tempting to keep trying "just one more tweak" forever. A rule written in advance, when you had no stake in the outcome, decides fairly when to stop.</details>

---

**When you finish:** reread [R001](research/R001-primitive-evolution-prior-art-and-thesis.md) and [P001](product/P001-first-workflow-public-evidence.md). You'll understand every line. Then try explaining EXP-001's result in your own words. If you can explain it simply *and* correctly, you've truly learned it.
