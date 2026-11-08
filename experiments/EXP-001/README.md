# EXP-001 results folder: how to read the files

The computer generated the files in this folder automatically when the experiment ran, so they use short technical labels. This page translates them. The full story is in the [research report](../../docs/research/R001-primitive-evolution-prior-art-and-thesis.md), and every word is in the [Glossary](../../docs/GLOSSARY.md).

## What's in here

| File or folder | What it is |
|---|---|
| `results/summary.md` | The main score table for the real experiment (exam papers 0–9, 5 rounds of learning). |
| `results/summary.json` | The same numbers in a computer-readable form, plus fingerprints of the exact code used. |
| `results/raw/` | 200 files, one per run (exam paper × puzzle type × student). They record every detail: which shortcuts were invented, which were rejected, and the score each round. |
| `results_compute_matched_B150000/` | Student A, who never learns, given **5 times more tries**, to compare fairly with the learners' total effort. |
| `results_compute_matched_B450000/` | Student A given **15 times more tries**, to compare fairly with Student E. |
| `hypothesis_tests.txt` | The verdict on each prediction we wrote down in advance. |
| `analysis.py` | The small program that produced `hypothesis_tests.txt` from the raw results. |

## Translating the labels

| Label in the files | Meaning |
|---|---|
| `D-struct` | **Patterned puzzles** (with hidden repeating tricks) |
| `D-flat` | **Random puzzles** (no hidden tricks) |
| `C0_fixed` | Student A: never learns |
| `C1_compose` | Student B: learns only what to try first |
| `C2_grow` | Student C: saves shortcuts, chosen by how much they shorten old solutions |
| `C2r_random` | Student C-random: saves random shortcuts |
| `C3_evolve` | Student D: your full idea |
| `C3_noHO` / `C3_noPrune` / `C3_noGate` | Student D without action slots / without removing unused shortcuts / without the undo rule |
| `C4_search` | Student E: tests each shortcut before keeping it |
| `O_oracle` | The cheat student, secretly given the right building blocks |
| `test solve` | Score: puzzles solved out of 100. A puzzle counts only if the recipe also works on the hidden check examples. |
| `95% CI` | The range the true score very likely lies in. Narrow ranges mean we're more certain. |
| `Δ vs C0` | How many points better (+) or worse (−) than Student A |
| `pp` | "Points out of 100" |
| `W/T/L` | On how many of the 10 exam papers the student **W**on, **T**ied or **L**ost against the comparison student |
| `by level` | Score split by puzzle difficulty. L2 is easier, L4 is hardest. |
| `compute (values)` | How much effort was used, counted as distinct results tried |
| `PASS` / `FAIL` | Whether the prediction met the success rule we set in advance: at least 5 points better, and clearly not luck |
| `CI>0` / `CI<0` / `CI spans 0` | For extra observations: clearly better, clearly worse, or can't tell from luck |
| `gate rejections: 47` | The undo rule stopped 47 changes that would have made practice scores worse |
| `deprecation events: 0` | "Remove unused shortcuts" never happened, so that feature is untested |
