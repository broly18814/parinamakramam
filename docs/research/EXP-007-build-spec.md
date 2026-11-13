# EXP-007 build specification (committed before any EXP-007 code runs on data)

**Status:** 14 November 2026. It fills gaps the [EXP-007 design](EXP-007-design.md) leaves open, before any code exists and before any calibration data is seen. Each choice is the simplest one consistent with the design and with EXP-006. **None is tuned:** the only tuned settings remain the design's own (the model, λ, the split, and *k* if sampling is too slow).

## In plain words

The design says *what* is compared. Building it showed three things it doesn't say exactly:
1. **How the model sees the code, and how its guesses are compared with the hidden piece.** EXP-005 compares code in a "normalised" form, with variable names numbered and strings replaced. A language model reads real code much better, so it's shown the real code, and each guess is normalised the same way before comparing.
2. **One of the seven cells doesn't exist yet.** Learned blocks with the sharper guesser (`L1`·G2) needs a two-level grammar that knows the blocks. EXP-006 never built one.
3. **The model-guided grammar (G3) is described in one sentence.** It's defined exactly below.

## S1. What the model is shown (the prompt)

- **The text:** the future function's **original source**, read from the pinned commit with `git show`, with the hidden piece's exact span replaced by the identifier `__HOLE__`.
  - **The span:** the normalised node keeps the original `lineno`, `col_offset`, `end_lineno` and `end_col_offset`, because `normalise` uses `copy.deepcopy`.
  - **A hidden statement** becomes the line `__HOLE__` at the same indentation.
- **The instruction**, fixed, one line: "Write only the Python code that replaces `__HOLE__`: a single expression, or a single statement if `__HOLE__` stands alone on its line. No explanation."
- **Under `L1` and `L2`,** the prompt also lists the 50 blocks as readable code with `HOLE` placeholders (EXP-005's `example` form).
  - **Under `L2`,** each block has its name and description (S4).
  - **Under `L1`,** the blocks are unnamed. They're numbered in learned order.
- **Chat template:** the model's own. **Reasoning ("thinking") is off**, if the model supports turning it off: 64 new tokens leave no room for it.

## S2. Turning a guess into a comparable piece

1. **Clean the text:** strip a surrounding code fence; keep the first logical line for an expression, or the first statement for a statement.
2. **Put it back:** replace `__HOLE__` in the prompt's function text with the guess, dedent, and `ast.parse` it.
3. **Normalise the completed function** exactly as EXP-005 does (`normalise`), so local names get numbered consistently, including names the guess introduces.
4. **Find the piece:** the node of the hole's kind (expression or statement) whose start position equals the hole's. Its `shape()` is the guess's piece.
5. **A guess that fails at any step is dropped,** and counted as "unparseable" in the results.

## S3. The model-guided grammar (G3), per task

- **The samples' counts:** for each usable guess, count the base rules (`template`) of its piece, in the same **two-level contexts** as G2, starting from the task's own context. Under `L1`/`L2`, each piece is first rewritten with the blocks (`rewrite_plan`), so block rules are counted too.
- **The probability:** for a context `c2` where the samples count `n_s(c2) > 0`:

  `P(r | c2) = λ · n_s(r, c2) / n_s(c2) + (1 − λ) · P_base(r | c2)`

  Where the samples never reach a context, `P = P_base`.
- **`P_base`:**
  - under `L0`, G2;
  - under `L1`/`L2`, G2 with blocks (S5).
- **Rules the past never had:** a base rule that appears only in samples (a new name, say) gets probability only from the samples' part. That's why G3 can make more tasks buildable. Their completion bounds come from the same fixed-point computation.
- **No usable guesses:** the task's G3 grammar is `P_base`, and that's reported.
- **The search is unchanged:** EXP-006's A\*, effort measure and budget B = 5,000.

## S4. Names and descriptions for `L2`, deterministic

**The name** is built from the block's root node and the first named thing inside it, in `ast.walk` order:
- a call: the callee's attribute or name (`append`, `isinstance`);
- otherwise, the root type in snake case (`compare`, `if_stmt`);
- followed by `_` and the number of holes.

Names that repeat get `_2`, `_3` and so on, in learned order.

**The description** has one sentence per pattern, from a fixed table keyed on the root type, filled from the block's parts. For example: "calls `<receiver>.append` with 1 argument"; "checks `isinstance(<x>, <T>)`"; "an `if` whose test compares with `None`".

**No model is used for names.** That keeps `L2` reproducible, as the design requires.

## S5. A two-level grammar with blocks (needed for `L1`·G2 and `L1`/`L2`·G3)

It's G2's definition applied to the rewritten past, as G1 with blocks is G1's definition applied to the rewritten past:
- **The data:** each past function is rewritten with the blocks (`rewrite_plan`).
- **What's counted:** in each two-level context, a block use counts once, at its root, and the nodes it covers count nothing.
- **Hole contexts:** a hole's one-level context is the one EXP-006 already gives it (`hole_ctxs`). Its two-level context is that, preceded by its parent's own context *inside the block*. If the hole is a direct child of the block's root, that's the root's context.
- **The back-off:** to the one-level grammar with the same blocks, exactly as G2 backs off to G1.

## S6. The "model alone" controls

- **Any-of-k:** solved if any usable guess's piece equals the target's shape.
- **Top-1:** solved if the guess with the **highest average log-probability per generated token** matches. Ties go to the earlier sample. Log-probabilities are recorded while sampling; nothing extra is computed.

## S7. Sampling, reproducibly

- **Settings:** MLX-LM; temperature 0.8, top-p 0.95, 64 new tokens; *k* = 16.
- **The seed:** a fixed seed per (task, library) pair, derived from the task's index.
- **The record:** every raw guess text, its token count and its log-probability are saved, so the whole analysis can be re-run without the model.

## S8. Self-checks (written alongside the code)

- **S2 round-trip:** the true piece's own source, put back by S2, reproduces the target's shape exactly, on all calibration tasks.
- **S3 reduces to the base grammar:** with λ = 0, or with no samples, G3 equals the base grammar on every task (same effort).
- **S5 reduces to G2:** with no blocks, the two-level grammar with blocks equals G2.
- **S4 is deterministic:** the same library always gets the same names.
- **Replay:** a saved sampling run reproduces every published number without the model.
