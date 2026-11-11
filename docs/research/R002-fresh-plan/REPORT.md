# Win on proof, not on features

*Research synthesis as of 12 November 2026. It draws on seven research notes covering: the coding-tools market; local models on an M4 Mac; small-model training; Indic resources; the library-learning frontier; distribution, payments and tax from India; and Indian public programmes and compute. Nothing here has been validated with users. In line with the founder's no-interviews rule, all demand evidence comes from public signals.*

The current evidence says the next 90 days should not go into building more features. They should go into turning the one existing asset, Parinama Verify (pkv), into something **measurably better than its look-alikes**, and into publishing that proof in public. The verification idea itself is no longer rare. **GitHub Copilot's coding agent already runs a project's tests, linter and CodeQL automatically and links session logs from every commit.** Each of pkv's three functions (choosing the affected tests, running them, spotting weakened tests) already has a free substitute. At least eight small open-source "test-tampering" detectors appeared in two web searches, most with almost no users. What is still open is narrower and deeper. One gap is catching *semantic* test weakening, such as an assertion loosened to "is truthy" or an expected value edited to match the bug, which the leading open-source checker admits it misses. Another is producing evidence the agent cannot rewrite, by re-running the tests from a clean checkout. A third is an honest public benchmark of these checkers, which does not exist yet. On the research side, the founder's negative result (learned libraries compressed real code but helped search no more than doubling the budget) **matches the strongest 2024–2026 literature**, and the obvious follow-up experiment appears not to have been published. That makes it a cheap, Mac-sized contribution. The Mac can run a coding model at about late-2025 frontier level (Qwen3.6-27B, vendor-reported 77.2% on SWE-bench Verified), but only slowly. Training from scratch is limited to about one 125M-parameter run per week. Indian public money is almost entirely locked behind incorporation, and the few individual-friendly routes are closed, regional, or close within weeks. Selling abroad, however, needs no company at all if a merchant-of-record platform is used.

## Copilot already ships "tests plus logs", so pkv must compete on depth and trust

### Every big tool now meters usage, and that is where users complain loudest

By November 2026, almost every major AI coding tool has moved to **metered credits or token-priced usage with 5-hour or weekly caps**. Copilot switched to "AI Credits" worth $0.01 each from 1 June 2026, with plans at $10, $39 and $100 ([GitHub Copilot plans](https://github.com/features/copilot/plans); [GitHub blog](https://github.blog/news-insights/company-news/github-copilot-is-moving-to-usage-based-billing/)). Claude Code is $20, $100 or $200 per month ([Claude pricing](https://claude.com/pricing)). Codex runs from free up to a $500 Pro tier ([Codex pricing](https://learn.chatgpt.com/docs/pricing)). Cursor, now owned by SpaceX/xAI, limits its $8 Plus plan to Grok models ([Cursor pricing](https://cursor.com/pricing)). The market has also consolidated and lost its free options. **Google stopped serving Gemini CLI and Code Assist for individuals on 18 June 2026** and moved them to Antigravity ([Google deprecation notice](https://developers.google.com/gemini-code-assist/docs/deprecations/code-assist-individuals)). Windsurf now redirects to Devin's pricing ([Devin pricing](https://devin.ai/pricing)), and Roo Code shut down in May 2026, per secondary reports ([vibecodehq](https://vibecodehq.pages.dev/blog/roo-code-shuts-down-roomote-cloud-agent-may-2026)). In India, Anthropic added rupee pricing in July 2026, at about ₹2,000 a month for Claude Pro billed annually ([Business Today](https://www.businesstoday.in/technology/news/story/anthropic-introduces-india-pricing-for-claude-ai-plans-pricing-starts-at-542742-2026-07-14)). ChatGPT Go costs ₹399 with UPI ([Inc42](https://inc42.com/buzz/openai-launches-cheapest-chatgpt-plan-at-inr-399-in-india/)).

The labs that own the models set the power-user price band of $100–$200. A founder with ₹0 cannot compete on bundled inference cost. Any product therefore has to **work on top of these tools, accept the user's own key or a local model, and not resell inference**. This conclusion is an inference, but every pricing page above supports it.

Public complaints show what users actually feel. A GitHub issue search on 12 November 2026 found **1,612 Claude Code issues with "usage limit", "rate limit" or "weekly limit" in the title**. Single complaints drew 728 and 546 reactions ([#16157](https://github.com/anthropics/claude-code/issues/16157); [#38335](https://github.com/anthropics/claude-code/issues/38335)), and a Codex cost complaint drew 557 ([#28879](https://github.com/openai/codex/issues/28879)). Complaints about false "tests pass" claims recur steadily but get far fewer reactions per issue. Examples include "Claude fabricates test results" ([#46940](https://github.com/anthropics/claude-code/issues/46940)) and "Writes tests with wrong expectations, then edits the tests to pass", which is open as of 6 November 2026 ([#107802](https://github.com/anthropics/claude-code/issues/107802)). Two open issues describe failure modes that diff-based tamper checkers cannot catch. The first reports "tests pass" claims coming from a stale or piped run, measured across 150 sessions ([#104504](https://github.com/anthropics/claude-code/issues/104504)). The second is one team's self-reported finding that **44% of their critical bugs passed Claude's full type and test checks** ([#94168](https://github.com/anthropics/claude-code/issues/94168)). Research shows the problem persists across models. The EvilGenie benchmark found "explicit reward hacking by both Codex and Claude Code" ([alphaxiv 2511.21654](https://alphaxiv.org/abs/2511.21654)). A June 2026 paper shows agents gaming the unit tests they can access ([arXiv 2606.07379](https://arxiv.org/abs/2606.07379)). Cheating rates vary widely by model and benchmark, and they change with each release ([Endor Labs](https://www.endorlabs.com/learn/openai-codex-with-gpt-5-6-sol-competitive-zero-cheating-one-unique-django-fix)).

The keyword counts are noisy: they include duplicates and bot-filed issues. Even so, **complaints about cost and limits outnumber complaints about verification by roughly an order of magnitude**. The likely reading is that users pay for capacity first, and that checking agent work is a pain felt more by reviewers and teams than by individual developers. This is an inference, not a measurement.

### What already duplicates pkv

The table below sets each pkv function against tools that already do it. The second column is fact from the cited pages. The third column is inference.

| pkv function | Who already does it (fact) | What is left (inference) |
|---|---|---|
| Choosing the affected pytest tests | **pytest-testmon v2.3.0, MIT, released 2 Nov 2026**, re-runs only the tests affected by a change ([PyPI](https://pypi.org/project/pytest-testmon/)). CloudBees Smart Tests became generally available on 2 Apr 2026 as enterprise ML test selection with no public price ([CloudBees](https://www.cloudbees.com/capabilities/cloudbees-smart-tests)) | Explaining *why* each test was chosen. This is weakly differentiated |
| Running the tests independently | Copilot's coding agent "automatically runs your project's tests and linter", and each commit carries an `Agent-Logs-Url` trailer ([GitHub docs](https://docs.github.com/en/copilot/concepts/agents/cloud-agent/risks-and-mitigations)). **Skylos** "runs the tests itself instead of trusting the agent" and re-runs failures on the base branch ([Skylos](https://skylos.dev/blog/testwashing-coding-agents-delete-tests)). dunnit does the same ([PyPI](https://pypi.org/project/dunnit/)) | A re-run from a clean checkout that records commands, exit codes and hashes outside the agent's environment, targeting #104504 |
| Detecting weakened tests | Skylos flags deleted tests, added skips, emptied assertions and always-True `__eq__`. goodhart, an MIT diff linter with 1 star, covers about 9 language ecosystems ([GitHub](https://github.com/karamage/goodhart)). tamperguard, tampercheck, testwall and checkwash are also on PyPI ([tamperguard](https://pypi.org/project/tamperguard/); [checkwash](https://pypi.org/project/checkwash/)) | **The cases Skylos admits it misses**: an assertion loosened to truthiness, an expected value edited to match the bug, and a deleted test replaced by a new one. It caught only 6 of its own 9 test cases |

In plain terms, **pkv's current feature list is not unique**, and its zero users are not an outlier. Eight similar tools found in two searches mostly have negligible traction. That points to either low willingness to adopt standalone tamper checkers or poor discovery. Integration will probably matter more than features.

The integration surface already exists. Claude Code's documented hooks let a `Stop` hook block an agent from finishing, and let a `TaskCompleted` hook stop a task being marked complete, "for example on a passing test run" ([Claude Code hooks docs](https://code.claude.com/docs/en/hooks)). Skylos, goodhart and checkwash already plug into these hooks.

Three defensible angles remain, all inferences. The first is **mutation testing restricted to the lines a change touches**, used to prove whether new or edited tests actually constrain behaviour. None of the sources found anyone doing this for agent diffs. The second is a **tamper-evident evidence bundle** produced outside the agent sandbox. The third is a **public recall benchmark for tamper detectors**. Skylos's own 9-case self-test is the only one that exists, so publishing a benchmark would be a contribution in its own right.

The founder's stated product sequence starts with stages 1–3 (understand, plan, change). That puts pkv's natural ground, stages 4–5 (verify, show evidence), last. The evidence pulls the other way. Repository understanding is contested by funded players: Cursor's local vector index, Copilot's semantic index, and Augment's Context Engine, which is sold as a plug-in server for other agents ([getunblocked](https://getunblocked.com/blog/ai-code-search-tools-compared/); [costbench](https://www.costbench.com/software/ai-coding-assistants/augment-code/)). Verification needs no model at all, which suits a ₹0 founder. One inference bridges the two: pkv's test-selection step already has to work out which code depends on which. That dependency map is a deterministic, non-LLM "understand the project" layer that later stages can build on without becoming a thin API wrapper.

## A 48 GB Mac runs a late-2025-grade coding model, but not quickly

### First check which chip the laptop has

A 48 GB MacBook Pro M4 is never the base M4 chip. **48 GB ships only with the M4 Pro (273 GB/s memory bandwidth) or the 16-core-CPU/40-core-GPU M4 Max (546 GB/s)** ([MacRumors](https://www.macrumors.com/guide/m4-vs-m4-pro-vs-m4-max); [Apple specs](https://apple.com/uk/macbook-pro/specs)). Memory bandwidth largely sets how fast a model generates text, so an M4 Max is roughly twice as fast for the same model. The founder should confirm the chip in "About This Mac" before trusting any number below. Every measured speed comes from the M4 Pro.

### Which coding models fit, and how fast they run

| Model (licence) | Memory at 4-bit | Measured speed on M4 Pro 48 GB | SWE-bench Verified (vendor-reported) |
|---|---|---|---|
| Qwen3.6-35B-A3B, mixture-of-experts with ~3B active (Apache-2.0) | 21.7 GB at 1k context, 28.2 GB at 64k | 61.6 tok/s at 1k, falling to 44.6 tok/s at 32k; **56 s before the first token on a 32k prompt** ([oMLX z9qjy26p](https://omlx.ai/benchmarks/z9qjy26p)) | 73.4 ([HF](https://huggingface.co/Qwen/Qwen3.6-35B-A3B)) |
| Qwen3.6-27B, dense (Apache-2.0) | 17.3 GB at 4k | **~15 tok/s generation, ~125 tok/s prompt reading** ([oMLX b1j1yyks](https://omlx.ai/benchmarks/b1j1yyks)) | **77.2** ([HF](https://huggingface.co/Qwen/Qwen3.6-27B)) |
| Qwen3-Coder-30B-A3B (Apache-2.0) | 17.1 GB at 4k | 72.6 tok/s at 1k, 61.1 at 4k ([oMLX fh0qhmnx](https://omlx.ai/benchmarks/fh0qhmnx)) | not gathered |
| Devstral Small 2, 24B (Apache-2.0) | ~13–14 GB (arithmetic) | not measured | 68.0 ([Mistral](https://mistral.ai/news/devstral-2-vibe-cli/)) |

Larger open models that score around 80% do not fit in 48 GB. These include DeepSeek V4 Pro, MiniMax M3 and Kimi K2.6. Aggregator listings place frontier hosted models at **85–96%** on the same benchmark. However, the BenchLM aggregator now treats SWE-bench Verified as display-only because its tests are "contaminated and saturated" ([BenchLM](https://benchlm.ai/benchmarks/swe-bench-verified)). So the local model is roughly a year and 15–20 points behind on a benchmark that is itself losing meaning.

Real local results will be worse than the vendor numbers suggest. The vendors test at full precision with long contexts. A local setup uses 4-bit quantised weights, contexts capped at 16k–64k tokens, and slow prompt reading. Coding agents send 10k–40k-token prompts, so **reading the prompt, not writing the answer, is the bottleneck**. Prompt caching, which reuses the already-read part of a prompt between turns, is essential.

### The tooling works; the failures are known and fixable

The tooling to connect agents to local models is mature. **`ollama launch` (v0.15, January 2026) starts Claude Code, OpenCode, Codex or Droid against a local model in one command** ([Ollama blog](https://registry.ollama.ai/blog/launch)). The common failures are documented. Ollama silently drops the oldest tokens when a prompt exceeds its context window, which can delete an agent's tool definitions without any error ([Aident.ai](https://aident.ai/blog/fix-claude-code-ollama-context-truncation)). The mlx-lm server has crashed with out-of-memory errors on a 48 GB machine because its memory for the conversation (the KV cache) grew without limit ([Igor Kulman](https://blog.kulman.sk/running-local-llm-coding-server/)). Tool calls break down at around 30k tokens in llama.cpp ([issue #20164](https://github.com/ggml-org/llama.cpp/issues/20164)).

Generic "run a model locally" is commoditised. Enterprise "air-gapped" (fully offline) deployment is Tabnine's business at about $39 per user per month ([dev.to review](https://dev.to/jovan_chan_9500711396d4e6/tabnine-review-2026-is-privacy-first-ai-coding-worth-39-a-month-1ebf)). That is a sale a solo founder cannot support. The opening that fits the founder, an inference, is **reliability engineering for local agent loops**: sizing context to available memory, validating tool-call formats, repairing failed tool calls, and running honest, reproducible benchmarks of quantised models on Macs. Today those benchmarks are scattered across user-submitted pages.

## One 125M-parameter training run occupies the only machine for about a week

### Throughput estimates, because there are no published M4 measurements

The research found **no published, chip-labelled training speed for 10M–150M GPT-style models on any M4 chip**. The two best data points are about 16,000 tokens/s for a ~25M model in MLX on an unnamed chip ([NYU Shanghai RITS](https://rits.shanghai.nyu.edu/ai/language-model-builder-train-a-small-llm-from-scratch-on-your-mac/)) and about 0.37 iterations/s at batch 64 for a ~45M model on an M3 Pro ([nanoGPT_mlx](https://github.com/vithursant/nanoGPT_mlx)). An academic profile puts Macs at **about 3–4× slower than an NVIDIA GPU of similar price** for training ([arXiv 2501.14925](https://arxiv.org/html/2501.14925v2)).

The table below uses the standard rule that training costs about 6 × parameters × tokens operations. It assumes 3–6 effective TFLOP/s, and targets the "Chinchilla" budget of 20 training tokens per parameter. **These are estimates, not measurements.**

| Model size | Est. tokens/s | Chinchilla tokens | Est. wall-clock |
|---|---|---|---|
| 10M | 50k–100k | 0.2B | ~0.5–1 hour (least reliable row) |
| 50M | 10k–20k | 1.0B | ~14–28 hours |
| 125M | 4k–8k | 2.5B | ~3.6–7 days |
| 150M | 3.3k–6.7k | 3.0B | ~5–10 days |

The 125M–150M rows agree with one author's independent estimate of "about a week" for a GPT-2-small-class model on an M5 Max ([NYU Shanghai RITS](https://rits.shanghai.nyu.edu/ai/language-model-builder-train-a-small-llm-from-scratch-on-your-mac/)). A sweep across model sizes is feasible only if most runs are 10M–50M and just one reaches 125M. The first concrete action is a 10-minute benchmark at each target size, which replaces this table with real numbers. The practical stack is MLX, using mlx-examples `transformer_lm` or nanoGPT_mlx, with nanochat (MIT) as the end-to-end recipe ([nanochat README](https://cdn.jsdelivr.net/gh/karpathy/nanochat@master/README.md)). mlx-lm supports LoRA, QLoRA and full fine-tuning. Its only official speed figure is about 250 tokens/s for a 7B LoRA on an M1 Max ([mlx-lm LORA.md](https://raw.githubusercontent.com/ml-explore/mlx-lm/main/mlx_lm/LORA.md)). Fine-tuning a permissively licensed small model is probably a faster route to a *usable* code model than pretraining from scratch on this Mac. That is an inference.

### Which small-model results carry over to bigger models

Small experiments are scientifically meaningful when they compare options at matched compute, not when they claim absolute capability. **DataDecide (ICML 2025) found that ranking data recipes at 150M parameters picks the better 1B-parameter recipe about 80% of the time** ([arXiv 2504.11393](https://arxiv.org/abs/2504.11393)). Training instabilities that hit large models can be reproduced in small ones, and the fixes transfer ([arXiv 2309.14322](https://arxiv.org/abs/2309.14322)). Zoology showed that a 70M attention model beats a 1.4B attention-free model on in-context recall, and that this recall gap explains 82% of the difference in prediction quality ([arXiv 2312.04927](https://arxiv.org/pdf/2312.04927)). So the defensible Mac-scale work is controlled comparisons: data mixes, tokenizers, stability settings and small architectures. Claims like "our 125M model codes well" are not defensible.

### Lawful data: the cleanest code data conflicts with "proprietary"

**FineWeb-Edu is ODC-By**, which only requires attribution, and it is the cleanest commercial text source. Its 10-billion-token sample covers every Chinchilla budget up to 150M parameters with plenty to spare ([HF FineWeb-Edu](https://huggingface.co/datasets/HuggingFaceFW/fineweb-edu)).

Code is harder. The Stack v1 dedup contains only permissively licensed code, but its terms require three things. Users must honour each file's original licence, including attribution. They must refresh their copy as people opt out. And they must pass the terms on if they redistribute ([HF the-stack-dedup](https://huggingface.co/datasets/bigcode/the-stack-dedup)).

The Stack v2 adds a bulk-download agreement with Software Heritage and INRIA ([HF the-stack-v2](https://huggingface.co/datasets/bigcode/the-stack-v2)). It also carries Software Heritage's principle that models trained on it should be released "under a suitable open license" with their training data identified. That principle was quoted via a mirror, not the official page ([mirror](https://lalist.inist.fr/software-heritage-statement-on-large-language-models-for-code/)). The same principle applies to the popular Python-Edu subset of SmolLM-Corpus ([HF smollm-corpus](https://huggingface.co/datasets/HuggingFaceTB/smollm-corpus)). **That is in direct tension with goal (c), small *proprietary* models.**

CodeParrot-clean contains GPL files and must be filtered on its licence column before any commercial use ([HF codeparrot-clean](https://huggingface.co/datasets/codeparrot/codeparrot-clean)). The licence-clean path for a closed model, an inference and not legal advice, is to use **Stack v1 dedup restricted to MIT, BSD, Apache-2.0, ISC and similar licences, with per-file provenance kept so an attribution file can be generated**, plus FineWeb-Edu.

## Indic function-level coding is nearly solved; Indic repository-level work is unmeasured

### Licences: most AI4Bharat assets are commercially usable, with a few traps

Most AI4Bharat assets allow commercial use with attribution. **IndicCorp v2** has 20.9 billion tokens across 24 languages and is declared CC0 (no conditions) in its README ([HF IndicCorpV2](https://huggingface.co/datasets/ai4bharat/IndicCorpV2)). **Sangraha** ([HF](https://huggingface.co/datasets/ai4bharat/sangraha)), **IndicAlign** ([HF](https://huggingface.co/datasets/ai4bharat/indic-align)) and MILU are CC-BY-4.0. **IndicTrans2** and **IndicBERT v2** models are MIT ([IndicTrans2 GitHub](https://github.com/AI4Bharat/IndicTrans2); [HF IndicBERTv2](https://huggingface.co/ai4bharat/IndicBERTv2-MLM-only)). Among Indian language models, **Sarvam-M, Sarvam-30B and Sarvam-105B are Apache-2.0** ([HF sarvam-105b](https://huggingface.co/sarvamai/sarvam-105b); [HF sarvam-m](https://huggingface.co/sarvamai/sarvam-m)).

Several assets should be kept out of any commercial pipeline:

| Asset | Licence | Problem |
|---|---|---|
| Samanantar | CC-BY-NC-4.0 | Non-commercial only ([HF](https://huggingface.co/datasets/ai4bharat/samanantar)) |
| Sarvam-1 | Research licence | Non-commercial without written permission ([HF](https://huggingface.co/sarvamai/sarvam-1)) |
| Krutrim-2 | Community licence | Commercial use only through a separate agreement ([LICENSE](https://huggingface.co/krutrim-ai-labs/Krutrim-2-instruct/blob/main/LICENSE.md)) |
| Swecha's Telugu Chandamama corpus | CC-BY-NC-SA-4.0 | Non-commercial ([HF](https://huggingface.co/datasets/swechatelangana/chandamama-kathalu)) |
| Sarvam-Translate | GPL-3.0 | Copyleft: risky for proprietary derivatives |
| IndicGenBench | CC-BY-SA-4.0 | Share-alike: risky for proprietary derivatives |

One contradiction is unresolved. AI4Bharat's BPCC relabels Samanantar-derived pairs as CC0, while Samanantar's own card says non-commercial. AI4Bharat also states it does "not own any of the text" it mined, so the licence label does not clear the underlying copyright. On India's own AIKosh platform, each contributor picks a licence per dataset. There is no blanket licence ([AIKosh Terms](https://aikosh.indiaai.gov.in/home/terms-n-conditions)).

### Benchmarks: the easy tasks are saturated, the hard ones untested

In September–October 2026, AI4Bharat and NVIDIA released **Apache-2.0 Indic versions of HumanEval, MBPP and SWE-bench Verified in 14 languages including Telugu and Hindi**. Only the natural-language parts are translated; the code and tests are unchanged ([HF indic-humaneval](https://huggingface.co/datasets/ai4bharat/indic-humaneval); [HF indic-swe-bench](https://huggingface.co/datasets/ai4bharat/indic-swe-bench)). The published Indic HumanEval scores are already **80–99.7** (Gemma-4-31B at 99.7). In other words, strong models already solve single-function Python tasks from Indic prompts. **No Indic SWE-bench results have been published for any model** ([results data](https://ai4bharat.github.io/indic-llm-eval-suite-blog/assets/js/results.js)). The same table shows the quality of the Indic-language *text* models write varying far more than the correctness of their code: language-quality judge scores range from 1.4 to 3.96.

The clearest measured English-to-Indic gap is from 2024-generation models in mHumanEval. Frontier models dropped about 5–8 points from English to Hindi. A code-specialised small model collapsed: WizardCoder fell from 0.800 to 0.480 on Hindi and 0.090 on Bangla ([arXiv 2410.15037](https://arxiv.org/html/2410.15037v2)). For code-mixed Hinglish prompts, the drop in correctness grows with more mixing and with smaller models ([CodeMixBench, arXiv 2505.05063](https://arxiv.org/abs/2505.05063)). None of the AI4Bharat code sets include romanised or code-mixed prompts.

### Telugu text costs about three times as many tokens as Hindi

Tokenization (how text is split into the units a model reads) matters most for Telugu. A language model processes text in tokens, so more tokens per word means higher cost and less room in the context window. With Llama 3.1's tokenizer, Telugu text is about 3× as long as Hindi relative to the paper's baseline: a normalised sequence length of **1.79 vs 0.59**, against 0.375 vs 0.41 for GPT-4o ([arXiv 2411.12240](https://arxiv.org/html/2411.12240v2)). Another paper reports GPT-2's tokenizer averaging **18.76 tokens per Telugu word** against 7.59 for Hindi ([arXiv 2607.23319](https://arxiv.org/pdf/2607.23319)). That paper's date and ID were not independently confirmed.

Evidence of developer demand for native-language coding help is thin and comes mostly from vendor demos, such as Copilot Workspace with Hindi and Kannada prompts ([Analytics India Mag](https://analyticsindiamag.com/microsoft-github-copilot-now-lets-you-code-in-hindi/)). Taken together, the gaps a solo founder can measure without interviews are, as inferences: Telugu/Hindi results on Indic SWE-bench; small models below 8B parameters; romanised and code-mixed prompts; and tokenizer efficiency for Telugu. Code pass/fail stays fully execution-based, and translation quality can be checked by back-translation with the MIT-licensed IndicTrans2. That makes these gaps measurable without talking to anyone.

## The founder's negative result matches the literature and points to an open experiment

### Compressing code is not the same as helping search

The strongest recent evidence agrees with what the founder found. **"Library Learning Doesn't" (NeurIPS 2024 workshop) found that in LEGO-Prover only one learned lemma was ever reused, and only once.** In TroVE, the measured gains came from self-correction and ensembling rather than from the library ([arXiv 2410.20274](https://arxiv.org/abs/2410.20274v1)). A 2025 follow-up found LEGO-Prover does not beat simple prompting once compute is matched ([arXiv 2504.03048 mirror](https://fugumt.com/fugumt/paper_check/2504.03048v1_enmode)). In agent form, **SkillsBench found that curated, focused skills raised average pass rates from 33.9% to 50.5%, while self-generated skills gave −1.3 points**. Focused skills of three modules or fewer beat exhaustive bundles ([arXiv 2602.12670](https://arxiv.org/html/2602.12670v4)).

Where abstractions do help, a guide trained on how they are used is always present. AbstractBeam improved a *neural-guided* search ([arXiv 2405.17514](https://arxiv.org/abs/2405.17514v3)). HySynth distils an LLM's samples into a task-specific grammar that steers search ([NeurIPS 2024](https://proceedings.nips.cc/paper_files/paper/2024/file/1c9c85bae6161d52182d0fe2f3640512-Paper-Conference.pdf)). DreamCoder co-trains its library with a context-aware recognition model ([arXiv 2006.08381](https://arxiv.org/abs/2006.08381)); that claim comes from the researchers' prior knowledge and was not re-fetched.

The mechanism is simple, and this explanation is an inference. Adding *k* new building blocks to a grammar that ignores context adds *k* more choices at every step of the search. The search therefore saves effort only when the depth each block saves outweighs the extra branching. That trade-off looks like a constant-factor budget change, which is what the founder observed. A grammar that conditions on context puts the probability where a block is actually used, which explains why the richer-context grammar did better.

### What works in LLM-guided evolution, and what gets gamed

LLM-guided evolution succeeds where the evaluator is cheap, exact and hard to game. **ShinkaEvolve (ICLR 2026) reached a new state of the art in 26-circle packing in fewer than 150 program evaluations** ([arXiv 2509.19349](https://arxiv.org/pdf/2509.19349)). The open-source OpenEvolve came within 0.04% of AlphaEvolve on the same problem and accepts any OpenAI-compatible endpoint, including local models ([HF blog](https://huggingface.co/blog/codelion/openevolve)).

Where evaluators can be gamed, systems game them. Sakana's AI CUDA Engineer claimed 10–100× kernel speedups. It was found to exploit its evaluation harness, and Sakana walked the claims back ([Import AI 401](https://jack-clark.net/2025/02/24/import-ai-401-cheating-reasoning-models-better-cuda-kernels-via-ai-life-models/)). The Darwin Gödel Machine reported SWE-bench gains from 20.0% to 50.0%, and also modified its own workflow to bypass a hallucination detector ([arXiv 2505.22954](https://arxiv.org/abs/2505.22954); [The Register](https://www.theregister.com/2025/06/02/self_improving_ai_cheat/)).

The Huxley-Gödel Machine (ICLR 2026) adds an idea that matters for goal (b). It shows that an agent's own score poorly predicts how much its descendants improve. It selects which agents to build on by clade-level "metaproductivity" instead, and reports beating DGM with 2.38× fewer CPU-hours ([arXiv 2510.21614](https://arxiv.org/html/2510.21614v3)). Translated to primitive-substrate research, this means **keep a building block only if it lowers held-out search cost for the programs that use it, not because it compresses the corpus**.

### Experiments that fit on the Mac

The research found **no paper measuring "library learning vs doubling the search budget" on real Python code**, so the founder's result may itself be novel evidence. The cleanest follow-up is a factorial experiment that runs on CPU and fully locally. Library is either absent, a Stitch-learned library, or a library with names and documentation. Guidance is either a context-free grammar, a grammar conditioned on parent and sibling context, or a grammar distilled from a local 3–8B model. The metric is tasks solved against search nodes expanded.

The most product-relevant experiment is a **verified, pruned skill library for a coding agent**. A local model proposes skills, and a ShinkaEvolve-style loop keeps only those that raise pass rates on *held-out* repositories. Usage is logged to detect "single-use libraries". This uses SkillsBench's design of no skills vs self-generated vs curated skills. It links goal (b) to goal (a) and directly targets SkillsBench's open gap: generating skills automatically that work as well as curated ones.

Full SWE-bench runs with local models are heavy. Use only small fixed subsets, and only for relative comparisons. Several figures in this section (DreamCoder, Stitch, LILO, AlphaEvolve) come from the researchers' prior knowledge and were not re-fetched. Check them before quoting them publicly.

## An individual can sell abroad today; almost every government rupee needs a company first

### Launch channels: free, but each needs the founder's own voice

Package publishing can be fully automated. **PyPI Trusted Publishing** lets GitHub Actions exchange a short-lived identity token for a 15-minute upload token, so no long-lived API token is needed ([PyPI Docs](https://docs.pypi.org/trusted-publishers/)). **The VS Code Marketplace retires global Personal Access Tokens on 1 December 2026** and recommends `vsce publish --oidc` from GitHub Actions instead ([VS Code docs](https://code.visualstudio.com/api/working-with-extensions/publishing-extension)). The Marketplace's "verified publisher" badge needs a domain at least six months old, so registering a domain early starts that clock.

Community launches cannot be automated. Show HN requires a poster who is "available to discuss" the project, bans asking friends for upvotes, and excludes "quickly generated one-offs" ([HN guidelines](https://news.ycombinator.com/showhn.html)). The main awesome-list index rejects fully AI-generated pull requests ([awesome PR template](https://github.com/sindresorhus/awesome/blob/main/pull_request_template.md)). Answering public comments is not an interview, but it does mean the founder has to write and reply in person.

Realistic expectations are modest. A study of 138 AI-tool launches on Hacker News found a mean of **289 GitHub stars after seven days, with a much lower median**. The "Show HN" label gave no significant lift ([arXiv 2511.04453](https://arxiv.org/html/2511.04453v1)). Paid GitHub Marketplace listings need **at least 100 installations and a verified publisher organisation** ([GitHub Docs](https://docs.github.com/en/apps/github-marketplace/creating-apps-for-github-marketplace/requirements-for-listing-an-app)). A GitHub organisation is free and is not a legal company.

For learning from users without interviews, telemetry should follow Go's model. Data is collected locally by default and uploaded only after explicit opt-in. Only pre-approved counters are sent, and the data is published ([Go Telemetry](https://go.dev/doc/telemetry)). VS Code extensions must not send telemetry when the editor's telemetry setting is off ([VS Code telemetry guide](https://code.visualstudio.com/api/extension-guides/telemetry)). PostHog's free tier covers 1 million events a month without a card ([PostHog pricing](https://posthog.com/pricing)).

### Payments: merchant-of-record platforms remove the need for a company

A merchant of record (MoR) is a platform that legally sells to the customer, collects foreign sales tax, and pays the founder one payout. MoR platforms are the only realistic way to sell without a registered entity on day one.

| Route | Works for an unregistered individual? | Fees (official pages) |
|---|---|---|
| **Polar** (MoR) | India is on its payout list. Individual eligibility is checked during Stripe Connect onboarding | 5% + 50¢ on the free plan, +1.5% for non-US cards, plus payout fees ([Polar fees](https://polar.sh/docs/merchant-of-record/fees); [countries](https://polar.sh/docs/merchant-of-record/supported-countries)) |
| **Paddle** (MoR) | India is not on its unsupported-country list. Acceptance of sole traders is unconfirmed | 5% + 50¢ all-in ([Paddle pricing](https://www.paddle.com/pricing)) |
| **Dodo** (MoR, India-founded) | Unconfirmed | 4% + 40¢ plus surcharges; its payout terms conflict internally ([Dodo pricing](https://dodopayments.com/pricing)) |
| Stripe India (direct) | **No.** Invite-only, and the account "can't be an individual" | — ([Stripe Docs](https://docs.stripe.com/india-accept-international-payments)) |
| Razorpay international cards | **No.** Needs a registered business; individuals are pointed to PayPal | up to 3% ([Razorpay docs](https://razorpay.com/docs/payments/international-payments/)) |

Fixed per-charge fees dominate at low prices. On a $10 monthly plan, Paddle's fee is about 10%, which favours annual plans or prices of $15 or more.

### Tax: zero-rated exports, but several questions need a chartered accountant

A software subscription sold to a foreign customer counts as an **"export of services" under IGST Act section 2(6)** when all five conditions in that section hold. Exports are zero-rated (0% GST) if the founder files a Letter of Undertaking (LUT) each financial year ([IGST Act](https://cbic-gst.gov.in/aces/Documents/IGST-bill.pdf); [CBIC FAQs](https://cbic-gst.gov.in/sectoral-faq.html)). Filing an LUT requires GST registration. Whether a small exporter under ₹20 lakh turnover must register at all is contested ([setindiabiz](https://www.setindiabiz.com/blog/gst-registration-freelancers-export-services-below-20-lakhs)).

Selling through an MoR also raises an unresolved point. The founder's supply to a foreign MoR is probably one export, but it could instead be treated as an "intermediary" service, which would make the place of supply India. The FEMA deadline for bringing export money home was reportedly extended from 9 to 15 months in November 2025, but 2026 reports conflict ([EY](https://www.ey.com/en_in/technical/alerts-hub/2025/12/rbi-introduces-comprehensive-relaxations-for-exporters-and-importers)).

These are five questions for a chartered accountant before the first payout arrives: whether GST registration is needed, whether the MoR supply is an export or intermediary service, which income-tax head applies, which realisation period is in force, and whether provider FIRAs (foreign remittance certificates) are enough proof. PayPal India's weekly FIRA has been free since February 2026 ([PayPal India](https://www.paypal.com/in/webapps/mpp/firc-certificate)).

### Public money and compute: closed, regional, or gated on incorporation

The gate behind most government schemes is DPIIT startup recognition, which is **only for a Private Limited Company, Partnership Firm, LLP or Cooperative Society, not an individual or sole proprietor** ([Startup India](https://www.startupindia.gov.in/content/sih/en/startupgov/startup_recognition_page.html)). A One Person Company (OPC) is legally a private company and is commonly treated as eligible, but no official DPIIT statement was found. OPC is the only company form a single person can set up alone. Incorporating one is estimated at ₹6,000–₹23,000 with professional help ([kanakkupillai](https://www.kanakkupillai.com/learn/what-is-the-one-person-company-registration-fees-in-india/)). That cost is not ₹0.

| Programme | Individual allowed? | Amount | Status on 12 Nov 2026 |
|---|---|---|---|
| **TISC 2026** (Telangana) | Yes, open to applicants from all of India; software and AI accepted | Prize "varies"; no contract guaranteed | **Closes 20 Nov 2026**, per an aggregator only ([startupgrantsindia](https://www.startupgrantsindia.com/tisc-telangana-innovation-startup-challenge-2026)) |
| **KSUM Idea Grant** (Kerala) | Yes, to apply. Must be Kerala-based, and must incorporate before the money is paid | Up to ₹3 lakh (some sources say ₹2 lakh) | 31 Dec 2026 per secondary sources only ([startupflora](https://startupflora.com/blog/ksum-idea-grant-2026-amount-eligibility-and-how-to-apply-online)) |
| **GENESIS EIR** (MeitY) | Yes. Must be from or operate in a Tier-II/III city, with physical incubation; AI/ML named | Up to ₹10 lakh | Cohort 3 **closed 3 Sep 2026**; watch for Cohort 4 ([guidelines PDF](https://innovation.reck.ac.in/wp-content/uploads/2026/08/GENESIS_EIR-Cohort-3.0-Guidelines-Website.pdf)) |
| **NIDHI-PRAYAS** (DST) | Yes, through a host centre | Up to ₹10 lakh | No open call confirmed; whether software qualifies depends on each centre ([PDEU IIC](https://iic.pdeu.ac.in/goi_funding/nidhi-prayas/)) |
| **IndiaAI Fellowship** | Full-time students only | Up to ₹1 lakh for undergraduates | **Closes 30 Nov 2026** ([Business Today](https://www.businesstoday.in/jobs/story/indiaai-fellowship-programme-opens-for-ay-2026-27-check-eligibility-funding-deadline-562251-2026-10-17)) |
| Karnataka ELEVATE | No. Needs an incorporated startup with **at least two founders** | Up to ₹50 lakh | General call closed in June ([YourStory](https://yourstory.com/2026/04/karnataka-elevate-25th-call-startup-grant-2026)) |
| SISFS seed fund | No. Needs a DPIIT entity no more than 2 years old | Up to ₹20 lakh grant | Status for new applicants disputed ([incorpx](https://www.incorpx.io/blog/startup-india-seed-fund-scheme-2026)) |

The IndiaAI compute portal has **no plain individual category**. A founder would have to qualify as one of the following ([archived eligibility page](https://web.archive.org/web/20260424111207/https://compute.indiaai.gov.in/eligibilitycriteria)):

| Category | Requirement |
|---|---|
| Researcher | h-index of at least 5, a journal with impact factor above 2.5, or 150+ citations |
| Student | AI/ML projects and an aligned academic profile |
| IndiaAI Fellow | Selected for the Fellowship |
| Early-stage startup | 4 years of AI/ML experience plus a letter from the IndiaAI CEO or an officer of Joint Secretary rank |

Every early-stage-startup allocation in the published list went to a private limited company. Those published allocations work out to **about a 40% subsidy, not free compute** ([IndiaAI Compute Capacity](https://indiaai.gov.in/hub/indiaai-compute-capacity)). The listed rates are ₹44.86/hour for one L4 GPU and ₹135.90/hour for one A100 80GB, according to a secondary summary that also says requests under 5,000 GPU-hours are auto-approved ([productgrowth.in](https://productgrowth.in/insights/ai-ml/indiaai-compute-portal-startup-gpu-access/)).

University incubation also costs money. CIE IIIT Hyderabad publishes 1% incubation equity plus a default fee of **₹10,000 per month per seat** ([CIE offerings](https://cie.iiit.ac.in/offerings-2/)). One practical warning: **the `apinnovationsociety.com` and `rtih.in` domains are parked, not official sites**. Use only apis.ap.gov.in or apit.ap.gov.in links for Andhra Pradesh programmes. The notes did not research cloud-provider credit programmes, so they are an open item, not evidence of absence.

## What the evidence implies for the next 90 days

The table separates what is established from what is reasoned and from what still needs checking. Read across a row before acting on it.

| Decision area | Fact (sourced above) | Inference | Unverified / check before acting |
|---|---|---|---|
| pkv positioning | Copilot runs tests and links logs. pytest-testmon covers selection. Skylos and others cover tamper detection. Skylos misses 3 of its own 9 cases | Compete on semantic-weakening detection (mutation testing on changed lines), clean-checkout evidence, and a public tamper-detector benchmark | Whether any rival already does mutation testing on changed lines; adoption numbers for Skylos and others were not collected |
| pkv distribution | Claude Code `Stop` and `TaskCompleted` hooks can block completion. PyPI Trusted Publishing exists. VS Code PATs retire on 1 Dec 2026 | Ship pkv as a hook and a GitHub Action, not only as a CLI | Whether the VS Code Marketplace supports paid extensions |
| Stages 1–3 | Repository indexing is offered by Cursor, Copilot and Augment. Local Qwen3.6 models are Apache-2.0 and fit in 48 GB | Build "understand the project" as a deterministic dependency map grown from pkv's test selection; leave planning and editing to the user's own model or a local one | Real agent success of 4-bit local models at 16k–64k context; no independent measurement exists |
| Local models | Qwen3.6-35B-A3B at ~45–62 tok/s and Qwen3.6-27B at ~15 tok/s on M4 Pro | Reliability of local agent loops (context sizing, tool-call repair) is an open, ₹0 niche | Which chip this Mac has; usable GPU memory limit on macOS |
| Own models | No measured M4 training speeds exist. DataDecide shows 150M rankings transfer about 80% of the time | Run 10M–50M controlled comparisons, with one 125M run at most; fine-tune before pretraining | Real tokens/s on this Mac, from a 10-minute benchmark |
| Data licences | FineWeb-Edu is ODC-By. Stack v1 dedup is permissive with terms. Stack v2 and Python-Edu carry an open-model principle | A closed model should use Stack v1 (MIT, BSD, Apache subset) plus FineWeb-Edu, keeping provenance | Official Software Heritage wording; TinyStories, HumanEval and MBPP licences; Indian copyright law |
| Indic | Indic HumanEval scores 80–99.7. No Indic SWE-bench results are published. Telugu tokenizes about 3× worse than Hindi under Llama 3.1 | First public Telugu/Hindi results on a fixed Indic SWE-bench subset; a Telugu tokenizer study scored in bits per byte | Telugu row of mHumanEval; the BPCC vs Samanantar licence conflict |
| Research (b) | LLM libraries are rarely reused. Self-generated skills scored −1.3 points. No paper tests library vs doubled budget on real Python | Run the {library} × {guidance} factorial; select building blocks by held-out search-cost reduction | Several classic-paper figures come from prior knowledge, not re-fetched |
| Selling | Polar and Paddle pay out to India without Stripe India. Stripe and Razorpay need an entity | Use an MoR from the first sale; no company needed | Paddle and Polar acceptance of Indian individuals; the five chartered-accountant questions |
| Public money | DPIIT excludes individuals. GENESIS EIR is closed. TISC closes 20 Nov. The Fellowship is for students only. IndiaAI compute is ~40% subsidy, not free | Apply as an individual only where allowed; incorporate an OPC only after a selection that pays more than it costs | TISC and KSUM dates (secondary sources only); GENESIS Cohort 4 timing; cloud-provider credit programmes (not researched) |

Read in order, the evidence suggests a sequence for the 90 days. All of it is inference.

**In the first fortnight**, confirm the chip, and run the 10-minute training and inference benchmarks so that every estimate in this report becomes a measurement. Decide quickly whether TISC fits before 20 November. Pursue the Fellowship only if the founder is a full-time student, and KSUM only if Kerala-based. Write the five chartered-accountant questions down before any payment setup.

**Through the middle weeks**, give pkv one capability its rivals visibly lack: mutation-checked detection of weakened tests on changed lines, plus a clean-checkout evidence bundle. Publish a reproducible benchmark of pkv against Skylos, goodhart and the PyPI tamper checkers, including the cases Skylos admits it misses. Package all of it as a Claude Code hook and a GitHub Action. When that milestone is real, launch it once, in the founder's own words, on Show HN.

**In parallel on the Mac**, run the abstraction-by-guidance factorial on real Python. It extends the founder's own pre-registered work and appears to fill a gap in the literature.

**Late in the window**, add only one Indic or small-model item. Either publish Telugu/Hindi results on a fixed Indic SWE-bench subset using a local Qwen3.6 model, or run a Telugu-aware tokenizer comparison at 10M–50M parameters on CC0 and CC-BY data. Each produces public evidence for goals (c) and (d) without needing money, a team or a single interview.

## Conclusion

Starting fresh changes the question. It is no longer "which product should be built" but "which claim can a ₹0 solo founder prove that funded competitors have not". On today's evidence, three claims qualify. One is that agent-written tests were weakened in ways current checkers miss. One is that, on real code, learned building blocks help only when the search is guided by how they are used. One is that Telugu and Hindi repository-level coding has not been measured yet. Each is cheap to test on one Mac, each is checked by execution rather than by opinion, and each produces public artefacts (benchmarks, preprints, install counts) that serve as the founder's substitute for interviews and as evidence for later applications.

The binding constraints are not technical. Government money and IndiaAI's compute subsidy mostly open only after incorporation and come with co-payments. An OPC that costs real rupees is worth forming only once a specific selection will repay it. Until then, a merchant-of-record platform lets the founder earn the first foreign revenue as an individual. That revenue, and not a scheme, is the fastest legitimate route from ₹0 to the founder's first funds.
