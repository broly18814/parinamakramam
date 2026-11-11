# Training small language models (10M–150M parameters) on an M4 MacBook Pro (48 GB), plus lawful code/text datasets (as of 12 November 2026)

Scope note: research done with web search and fetch on 12 Nov 2026. Measured Apple-Silicon *training* throughput numbers for small GPT-style models are scarce in public sources. Most published Mac numbers are for *inference*, which does not transfer to training. Every throughput figure below names the chip. Anything not measured is labelled **ESTIMATE**.

Hardware ambiguity to resolve first: Apple sells a 48 GB MacBook Pro with either an M4 Pro or an M4 Max chip. The two have very different GPU core counts. Run `system_profiler SPDisplaysDataType` and note the GPU core count before trusting any estimate. (This comes from my general knowledge of Apple's configurations and was not re-verified in this session.)

## Q1. What training throughput has been measured on M-series chips, and how long would Chinchilla budgets take?

### Takeaway
There are very few published, chip-labelled tokens/sec figures for from-scratch GPT training on Apple Silicon. The two best data points are about 16,000 tokens/sec for a ~25M model (MLX, chip not stated) and about 0.37 iterations/sec at batch 64 for a ~45M model (MLX, M3 Pro). Extrapolating with the standard 6·N·D FLOP rule, a 10M model reaches its Chinchilla budget (20 tokens per parameter) in about an hour. A 50M model takes about a day. A 125M–150M GPT-2-small-class model takes roughly 4–10 days of continuous training on one M4-class laptop. One independent source estimates "about a week" for GPT-2-small class on an M5 Max, which agrees.

### Cited Findings
- **~25.1M-parameter Transformer, MLX, about 16,000 tokens/sec.** Setup: 10K-vocabulary BPE tokenizer, 547M-token corpus, 16,270 steps shown in the loss curve. The article does not name the chip for this demo run. It is the "Language Model Builder" macOS app, released 21 July 2026 (v1.1.0 on 22 July 2026). — [NYU Shanghai RITS: Language Model Builder](https://rits.shanghai.nyu.edu/ai/language-model-builder-train-a-small-llm-from-scratch-on-your-mac/)
- The same article estimates that a GPT-2-small-class model (about 100–150M parameters) would take **about a week on a MacBook Pro M5 Max**. Its default settings produce coherent text "in as little as a day." This is the author's estimate, not a measurement. — [NYU Shanghai RITS](https://rits.shanghai.nyu.edu/ai/language-model-builder-train-a-small-llm-from-scratch-on-your-mac/)
- **nanoGPT_mlx, MacBook M3 Pro, ~45M-parameter GPT-2: "~0.37 iterations/second" at batch_size=64** (local_batch_size=4 × gradient_accumulation=16). The README does not state the context length (block_size), memory, or layer dimensions. The repo also supports 124M GPT-2 on OpenWebText but gives no timing for it. — [vithursant/nanoGPT_mlx](https://github.com/vithursant/nanoGPT_mlx)
- The ml-explore/mlx-examples `transformer_lm` README only gives `python main.py --gpu` on PTB by default. It publishes no speed, model size, or perplexity numbers. — [mlx-examples transformer_lm README](https://raw.githubusercontent.com/ml-explore/mlx-examples/main/transformer_lm/README.md)
- pranavjad/mlx-gpt2: a character-level model on ~1M characters of Shakespeare trains in "around 10 minutes on a macbook". The chip is not stated. — [pranavjad/mlx-gpt2](https://github.com/pranavjad/mlx-gpt2)
- A GPT-style TinyStories trainer (MLX or PyTorch MPS) estimates **4–8 hours on M4 Max for 50,000+ steps**. It gives no tokens/sec. — [zubair-khan-ai/train_llm_mlx](https://github.com/zubair-khan-ai/train_llm_mlx)
- Academic profiling (Feng, Xu, Wang, Lin; arXiv 2501.14925, Jan 2025):
  - Hardware tested: M2 Pro, M2 Max and M2 Ultra against RTX A6000, RTX 4090 and 2080 Ti.
  - Workloads: GPT-2 large, GPT-2 XL and Whisper.
  - Framework: MLX vs PyTorch MPS vs CUDA.
  - Headline: expected speed on a Mac is "about 3x-4x lower than an NVIDIA GPU of similar price".
  - FP16 gives MLX only about 20–30% speedup on matrix-matrix products, and MPS gains almost nothing. On vector-Jacobian products, CUDA gets about 5–6× from FP16 while MLX and MPS get about 2×.
  - Apple's kernel launch overhead is much higher than CUDA's.
  - The gap is attributed to page faults, power, and kernel-launch time.
  - On GPT-2-large pretraining, the RTX A6000 "slightly underperforms" the M2 Ultra with MLX.

  — [arXiv 2501.14925 (HTML v2)](https://arxiv.org/html/2501.14925v2)
- nanochat on Mac:
  - `runs/runcpu.sh` "dramatically shrinks the LLM" so that training takes "a few ten minutes". The README warns, "You will not get strong results in this way."
  - MPS defaults to float32. bfloat16 works on recent macOS with about 25% less memory at similar speed (override with `NANOCHAT_DTYPE`).
  - Throughput is logged as `train/tok_per_sec` and `train/mfu`.
  - The README gives no Mac numbers.

  — [karpathy/nanochat README](https://cdn.jsdelivr.net/gh/karpathy/nanochat@master/README.md)
- For contrast with a GPU cluster:
  - nanochat's speedrun is "a 4e19 FLOPs capability model" (GPT-2 grade by DCLM CORE score, about depth 26) on an 8×H100 node. It takes about 1.5–2 hours and costs about $48 at roughly $3/GPU/hr, or about $15 on spot instances. — [nanochat README](https://cdn.jsdelivr.net/gh/karpathy/nanochat@master/README.md)
  - modded-nanogpt advertises "NanoGPT (124M) in 90 seconds" on 8×H100. — [KellerJordan/modded-nanogpt](https://github.com/KellerJordan/modded-nanogpt?tab=readme-ov-file)
  - Original nanoGPT recommends "at least an 8X A100 40GB node" to reproduce GPT-2 124M. — [karpathy/nanoGPT](https://github.com/karpathy/nanogpt)
- Hugging Face notes that only a single MPS device can be used, because the gloo and nccl distributed backends do not work with MPS. — [HF Accelerate MPS guide](https://huggingface.co/docs/accelerate/main/en/usage_guides/mps)
- A PyTorch forum user reports that an M5 Mac trains a custom CNN much slower than an Nvidia RTX 4050. Another user saw nearly identical CPU and MPS times. Both are anecdotes showing that MPS is not automatically fast. — [PyTorch forum (M5 vs 4050)](https://discuss.pytorch.org/t/super-slow-training-in-m5-mac-compared-to-4050-nvidia-gpu-why/224311); [PyTorch forum (CPU≈MPS)](https://discuss.pytorch.org/t/essentially-identical-training-time-on-cpu-mps-unconvinced-im-using-mps-at-all/193441)

### Inferences
- **Implied compute from the measured points (ESTIMATE):**
  - The 25.1M model at 16k tok/s implies about 6 × 25.1e6 × 16,000 ≈ **2.4 TFLOP/s effective**, ignoring attention FLOPs. The chip is unknown.
  - For nanoGPT_mlx on M3 Pro (64 sequences × 0.37 it/s): if block_size = 1024, that is ≈24k tok/s, or ≈6.5 TFLOP/s for 45M. If block_size = 256, it is ≈6k tok/s, or ≈1.6 TFLOP/s.
  - The block size is not stated, so treat this as a range of about 1.5–6 effective TFLOP/s on an M3 Pro.
- **Throughput and Chinchilla time on an M4 MacBook Pro (ESTIMATE).** Assumption: 3–6 effective TFLOP/s sustained in MLX with bf16/fp32 mixed. Use the low end for an M4 Pro and the high end for an M4 Max. Method: tokens/sec ≈ F / (6N), and the Chinchilla budget is D = 20N.

  | Model | Tokens/sec (est.) | Tokens/day (est.) | Chinchilla D = 20N | Wall-clock to Chinchilla (est.) |
  |---|---|---|---|---|
  | 10M | 50k–100k | 4.3B–8.6B | 0.2B | ~0.5–1.1 h |
  | 50M | 10k–20k | 0.86B–1.7B | 1.0B | ~14–28 h |
  | 125M | 4k–8k | 0.35B–0.69B | 2.5B | ~3.6–7.2 days |
  | 150M | 3.3k–6.7k | 0.29B–0.58B | 3.0B | ~5–10 days |

  - The 125M–150M rows agree with the independent "about a week on M5 Max" estimate above.
  - Small models have proportionally more attention, embedding and overhead cost, and Apple kernel-launch overhead is high (per arXiv 2501.14925). So the 10M row is the least reliable: real throughput may be well below 50k tok/s unless batch × sequence length is large.
- Practical implication: **one 125M Chinchilla run uses about a week of the only machine.** A scaling-law sweep across 5–8 sizes is feasible only if most runs are 10M–50M and the largest is 125M. Over-training far past 20 tokens/param (as SmolLM does) is out of reach at 125M+.
- Thermals matter: a laptop running for days at full GPU load may throttle. Measure tokens/sec at hour 1 and at hour 24. This is an inference, not measured.
- Do a 10-minute benchmark first: time 50 steps at each target size with `mx.eval` synchronisation, and record `tok/s` and peak memory (`mx.metal.get_peak_memory()`). Then replace these estimates with real numbers.

### Gaps
- I found no public, chip-labelled tokens/sec measurement for 10M, 50M, 125M or 150M GPT training on any M4 chip (Pro or Max) in MLX, llm.c or PyTorch MPS. The llm.c Metal/MPS port status was not verified.
- The nanoGPT_mlx block size is unknown, so its tokens/sec cannot be computed exactly.
- arXiv 2501.14925's per-pass time tables (Table 4) were not readable in the fetched HTML.
- I did not verify a direct MLX vs PyTorch MPS training-speed comparison at 10M–150M scale on M4.

## Q2. What reproducible recipes and repositories exist?

### Takeaway
On a Mac, the practical stack is MLX: mlx-examples `transformer_lm` for a minimal LM, nanoGPT_mlx for a nanoGPT-shaped config system, and mlx-lm for LoRA/QLoRA/DoRA/full fine-tuning. nanochat (MIT) is the best end-to-end recipe (tokenizer → pretrain → SFT → eval → chat). Its speed figures are for 8×H100, and on a Mac only a shrunken CPU/MPS mode runs. TinyStories is the canonical "meaningful in under 10M parameters" dataset. The SmolLM-Corpus is the canonical small-model pretraining mix.

### Cited Findings
- **mlx-examples/transformer_lm**: a decoder-only Transformer LM that depends only on MLX. It runs with `python main.py --gpu` on PTB by default, and `--dataset` selects others. — [README](https://raw.githubusercontent.com/ml-explore/mlx-examples/main/transformer_lm/README.md)
- **nanoGPT_mlx**: a port of nanoGPT to MLX with Shakespeare and OpenWebText 124M configs. — [vithursant/nanoGPT_mlx](https://github.com/vithursant/nanoGPT_mlx)
- **nanochat (Karpathy, MIT licence)**:
  - Full pipeline with a speedrun on 8×H100 (GPT-2 grade, about $48) and `runs/runcpu.sh` for CPU/MPS.
  - The leaderboard changed the pretraining data to NVIDIA ClimbMix in March 2026.
  - The SmolTalk task is used for chat fine-tuning.

  — [nanochat README](https://cdn.jsdelivr.net/gh/karpathy/nanochat@master/README.md)
- A community walkthrough of nanochat from zero (discussion #677) reports a depth-4 model trained for 1000 iterations in about 45 min. Whether it ran on CPU or MPS was unclear. — [nanochat discussion #677](https://github.com/karpathy/nanochat/discussions/677)
- **modded-nanogpt**: a GPT-2 124M speedrun ("NanoGPT (124M) in 90 seconds" on 8×H100). It is a source of architecture and optimiser tricks (e.g., Muon) to try at small scale. — [KellerJordan/modded-nanogpt](https://github.com/KellerJordan/modded-nanogpt?tab=readme-ov-file)
- **mlx-lm LoRA / QLoRA / DoRA / full fine-tuning**: `--fine-tune-type lora|dora|full`. QLoRA is used automatically when `--model` points to a quantized model (made with convert `-q`). — [mlx-lm LORA.md](https://raw.githubusercontent.com/ml-explore/mlx-lm/main/mlx_lm/LORA.md)
- **TinyStories** (Eldan & Li, arXiv 2305.07759): models "below 10 million total parameters", including single-block transformers, produce fluent, consistent multi-paragraph stories with near-perfect grammar. The paper proposes GPT-4 grading of grammar, creativity and consistency. The paper page states no dataset licence. — [arXiv 2305.07759](https://arxiv.org/abs/2305.07759)
- **SmolLM-Corpus**: Cosmopedia v2 (39.1M rows, synthetic, generated by Mixtral-8x7B-Instruct), FineWeb-Edu dedup (190M rows, "220 billion tokens"), and Python-Edu (7.68M rows). Python-Edu contents must be pulled from Software Heritage S3, which takes about 6 h on a 16-core AWS instance. The dataset-level tag is ODC-By. — [HuggingFaceTB/smollm-corpus](https://huggingface.co/datasets/HuggingFaceTB/smollm-corpus)
- **Language Model Builder** (macOS, MLX, July 2026): a GUI app to train small LMs, including on "TinyStories 2" (2.2 GB synthetic stories). — [NYU Shanghai RITS](https://rits.shanghai.nyu.edu/ai/language-model-builder-train-a-small-llm-from-scratch-on-your-mac/)

### Inferences
- Recommended path: prototype in mlx-examples `transformer_lm` or nanoGPT_mlx, then port the nanochat *evaluation* (CORE score) and tokenizer-training pieces. That gives results comparable to a known public baseline even though the training is far smaller.
- FineWeb-Edu `sample-10BT` covers the full Chinchilla budget for every size up to 150M (3B tokens), with plenty to spare.

### Gaps
- I did not verify an official SmolLM *training-recipe* repo (huggingface/smollm) in this session.
- I did not confirm whether an llm.c Metal backend exists or is maintained.
- The TinyStories dataset licence on the Hugging Face card was not fetched. Check the card for "cdla-sharing-1.0" or similar before commercial use.

## Q3. Code and text datasets: terms, commercial usability, and attribution/opt-out obligations

### Takeaway
None of the BigCode code datasets is "public domain, do anything". They are permissively licensed code (or code with no detected licence), redistributed under BigCode Terms of Use. Those terms require you to:
- honour each file's original licence, including attribution;
- keep your copy updated to the latest version with opt-outs removed;
- pass the terms on if you redistribute.

The Stack v2 and Python-Edu also come with Software Heritage's LLM principles, which ask that resulting models be released under an open licence with the training data identified by SWHID. That is a real constraint on a *closed* commercial model. FineWeb-Edu is ODC-By (attribution) and is the cleanest commercially usable text. CodeParrot-clean includes GPL files and should be filtered on its `license` column for commercial use.

### Cited Findings
- **The Stack v2** (bigcode/the-stack-v2):
  - Terms of use: "Downloading the dataset in bulk requires a an agreement with SoftwareHeritage and INRIA". Users must follow Software Heritage's principles for LLM training and "must abide by the terms of the original licenses, including attribution clauses when relevant". Provenance is provided per file.
  - The dataset "is regularly updated to enact validated data removal requests", and users agree to update to the most recent usable version.
  - Your email and username are shared with the maintainers.
  - The HF repo holds only SWHIDs (blob IDs). File contents sit in the Software Heritage S3 bucket and need your own AWS credentials.
  - Each file has `license_type` = `permissive` or `no_license`. "Permissive" means Blue Oak Council-approved or ScanCode "Permissive"/"Public Domain".
  - Sizes: full 67.5 TB, dedup 32.1 TB, train-full about 900B tokens.
  - Opt-out: the "Am I In The Stack?" Space, the opt-out-v2 GitHub repo, or contact@bigcode-project.org.

  — [HF: bigcode/the-stack-v2](https://huggingface.co/datasets/bigcode/the-stack-v2)
- **Software Heritage statement on LLMs for code (19 Oct 2023)**:
  - Resulting models "must be made available under a suitable open license, along with the documentation and tooling".
  - Training data must be "fully and precisely identified", e.g., by publishing SWHIDs.
  - Opt-out mechanisms should exist where possible.

  This wording was quoted via an aggregator or mailing list and may differ slightly from the official page. BigCode adopted these principles for StarCoder2 (Feb 2024). Some critics in a GNU Guix thread call the opt-out principle "a figleaf". — [Software Heritage statement (mirror)](https://lalist.inist.fr/software-heritage-statement-on-large-language-models-for-code/); [Roland Tanglao copy](https://rolandtanglao.com/2023/10/19/p0859-swh-statement-on-llm-for-code); [Guix-devel critique](https://mail.gnu.org/archive/html/guix-devel/2024-03/msg00184.html)
- **The Stack v1 dedup** (bigcode/the-stack-dedup):
  - Permissive licences only. v1.0 had 18 licences; v1.1 dropped copyleft MPL/EPL/LGPL and listed 193 permissive licences across 358 languages.
  - A file is included if *at least one* repo containing it has a permissive licence.
  - Licence detection used GHArchive and go-license-detector, and the card hedges "to the best of our knowledge".
  - Sizes: about 3 TB (v1.1), about 2.7 TB after v1.2's stronger near-dedup.
  - Same obligations as v2: original-licence attribution, update to the latest usable version, pass the terms on when hosting. Opt-out via "Am I In The Stack?" and opt-out-v2.
  - The card's opt-out cut-off dates are internally inconsistent (v1.2 cites 09.02.2022, which predates v1.1).

  — [HF: bigcode/the-stack-dedup](https://huggingface.co/datasets/bigcode/the-stack-dedup)
- **StarCoderData** (bigcode/starcoderdata):
  - Contents: 86 languages plus 54 GB of GitHub issues, 13 GB of Jupyter notebooks and 32 GB of commits. "783GB of code", "approximately 250 Billion tokens"; the file listing shows 311 GB, a discrepancy the card does not explain.
  - Decontaminated, near-deduplicated, and PII-redacted.
  - The licence field reads "other", governed by The Stack Terms of Use: original licences and attribution apply, keep the latest version, and pass the terms on if re-hosting.
  - Gated: requires login and acceptance.

  — [HF: bigcode/starcoderdata](https://huggingface.co/datasets/bigcode/starcoderdata)
- **FineWeb-Edu**:
  - Licence ODC-By.
  - Subsets: `sample-10BT` (9.67M rows), `sample-100BT` (97.3M rows), `sample-350BT` (339M rows), and default (1.53B rows).

  — [HF: HuggingFaceFW/fineweb-edu](https://huggingface.co/datasets/HuggingFaceFW/fineweb-edu)
- **SmolLM-Corpus**: tagged ODC-By overall. For Python-Edu, "Please refer to the-stack-v2 for the data license". Cosmopedia v2 was generated by Mixtral-8x7B-Instruct, and the card states no terms for those outputs. — [HF: HuggingFaceTB/smollm-corpus](https://huggingface.co/datasets/HuggingFaceTB/smollm-corpus)
- **CodeParrot-clean**:
  - Python files from GitHub: about 5.36M files, about 50 GB (listing 12.8 GB).
  - A per-file `license` column has 15 values, including **gpl-2.0 and gpl-3.0** alongside apache-2.0 and bsd-3-clause.
  - Exact-match dedup only. No dataset-level licence or terms.

  — [HF: codeparrot/codeparrot-clean](https://huggingface.co/datasets/codeparrot/codeparrot-clean)

### Inferences
- **Commercial-use ranking (inference, not legal advice):**
  1. **FineWeb-Edu (ODC-By)** — the most straightforward. Attribute the dataset. Underlying web pages keep their own copyright and Common Crawl terms; I did not verify the latter in this session.
  2. **The Stack v1 dedup, permissive** — usable commercially in BigCode's intended sense (StarCoder-family models were trained on it). You must:
     - keep provenance so you can honour attribution clauses (e.g., MIT/BSD/Apache NOTICE files) if the model reproduces code;
     - re-download or refresh to the latest version as opt-outs land;
     - not redistribute without passing the terms on.
  3. **StarCoderData** — same as v1, plus issues and commits. Issues and commits are user-generated text with weaker licence provenance than files.
  4. **The Stack v2 / Python-Edu** — bulk access needs a Software Heritage/INRIA agreement plus AWS egress. A ₹0 founder can still pull small subsets via HF + S3, but S3 transfer costs and the agreement are real friction. SWH's principles expect an **openly licensed model and published SWHIDs**, so they fit an open-weights release and not a closed commercial model. The `no_license` portion of v2 is the riskiest part. For commercial training, filter to `license_type == "permissive"`.
  5. **CodeParrot-clean** — for commercial use, filter to permissive values of `license` and drop GPL/AGPL/LGPL. Unfiltered, it is best kept for research.
- Safest permissive-only code subset: Stack v1 dedup (already permissive-only) or Stack v2 filtered to `permissive`, further restricted to MIT/BSD/Apache-2.0/ISC/Unlicense/CC0. Keep the per-file repo name and licence so you can generate an attribution file. Run near-dedup and HumanEval/MBPP decontamination yourself if you build a new mix (StarCoderData is already decontaminated).
- Evaluation sets: HumanEval and MBPP are commonly used. Their licences were not verified in this session, so check them before shipping benchmark results commercially.

### Gaps
- I did not fetch the official softwareheritage.org statement page or the BigCode governance/opt-out page directly. The SWH principle wording comes from mirrors.
- FineWeb-Edu token counts per sample, the Common Crawl ToU, and the card's PII caveats were not in the fetched excerpt.
- TinyStories, Cosmopedia (Mixtral output terms), HumanEval and MBPP licences were not verified.
- I found no data on Indic-language code or text dataset licences (e.g., AI4Bharat IndicCorp, Sangraha) in this session.
- This is not legal advice. Indian-law treatment of training on copyrighted code (Copyright Act 1957 fair dealing) was not researched.

## Q4. Which small-model experiments are scientifically meaningful, and do small-scale results transfer?

### Takeaway
There is solid peer-reviewed evidence that carefully designed 10M–150M experiments predict larger-scale outcomes for **data-selection decisions**, **training-stability / learning-rate phenomena**, and **architecture recall gaps**. DataDecide (ICML 2025) shows 150M-scale rankings pick the better 1B-scale data recipe about 80% of the time. Wortsman et al. reproduce large-model instabilities in small models. Zoology shows a 70M attention model beats a 1.4B gated-convolution model on associative recall, and that recall explains 82% of the perplexity gap. Meaningful Mac-scale projects are therefore controlled, equal-compute *comparisons* with public baselines. Absolute capability claims (HumanEval pass@1 at 125M) will be small and should be framed as relative.

### Cited Findings
- **DataDecide** (Magnusson et al., arXiv 2504.11393, ICML 2025):
  - Setup: controlled pretraining over 25 corpora, 14 model configurations, sizes up to 1B parameters.
  - Ranking data recipes at a **single small size of 150M predicts the better 1B model about 80% of the time**.
  - None of 8 scaling-law baselines beat the compute-decision frontier of single-scale prediction.
  - Continuous likelihood metrics make MMLU, ARC and HellaSwag >80% predictable at 1B using about 0.01% of target compute. SocialIQA is hard to predict.
  - Limitation: a single 100:1 token/param ratio.
  - All models, data and evals are released on HF.

  — [arXiv 2504.11393](https://arxiv.org/abs/2504.11393); [ICML 2025 poster](https://icml.cc/virtual/2025/poster/44022); [PMLR](https://proceedings.mlr.press/v267/magnusson25a.html)
- **Small-scale proxies for large-scale Transformer training instabilities** (Wortsman, Liu, Xiao, Everett et al., arXiv 2309.14322):
  - Attention-logit growth and output-logit divergence appear in small models at high learning rates.
  - Mitigations that work at scale work similarly at small scale.
  - Warm-up, weight decay and μParam together give small models similar loss across a wide LR range.
  - Instabilities can be predicted from how activation and gradient norms scale.

  — [arXiv 2309.14322](https://arxiv.org/abs/2309.14322)
- **Zoology** (Arora et al., arXiv 2312.04927, ICLR 2024):
  - Gated-convolution (attention-free) architectures underperform attention by up to 2.1 perplexity points on the Pile.
  - 82% of the gap is explained by in-context associative recall.
  - A 70M attention model beats a 1.4B gated-convolution model on associative recall.
  - It introduces the synthetic MQAR task for cheap architecture diagnosis.

  — [arXiv 2312.04927](https://arxiv.org/pdf/2312.04927); [Hazy Research blog](https://hazyresearch.stanford.edu/blog/2023-12-11-zoology1-analysis)
- **TinyStories**: under 10M parameters, models can show coherent generation when the data distribution is narrow and simple. This makes it a valid testbed for studying *emergence* and interpretability at tiny scale. — [arXiv 2305.07759](https://arxiv.org/abs/2305.07759)
- **The Mac-vs-GPU gap is about 3–4×** at similar price (arXiv 2501.14925). Experiments should therefore be sized so that a full sweep fits in days, not weeks. — [arXiv 2501.14925](https://arxiv.org/html/2501.14925v2)

### Inferences
- **Meaningful experiments sized for this Mac (inference from the above plus the Q1 estimates):**
  1. **Data-recipe ranking at 10M–150M following the DataDecide protocol.** For example, a permissive-only code mix vs a code+FineWeb-Edu mix, or Python-Edu-filtered vs unfiltered. Report rankings and likelihood-based proxy metrics, and compare against DataDecide's released checkpoints. This has the strongest published evidence of transfer.
  2. **Equal-FLOP architecture comparisons** (Transformer vs Mamba/RWKV vs hybrid) at 10M–50M. Include MQAR (Zoology) alongside perplexity, because the recall gap is the documented failure mode. MLX implementations of Mamba/RWKV were not verified and may need writing.
  3. **LR / stability sweeps (Wortsman-style)** at 10M–50M: LR sensitivity curves with and without qk-norm, z-loss, μP. These are cheap and known to transfer qualitatively.
  4. **Scaling-law slice:** 5–6 sizes from 5M to 125M at 20 tokens/param. ESTIMATE: total compute is dominated by the 125M run, about 4–7 days. Fit the loss vs compute exponent and compare to published Chinchilla/Kaplan slopes. The Chinchilla/Kaplan papers were not fetched this session.
  5. **Tokenizer studies (including Indic scripts):** train BPE/Unigram tokenizers at different vocabulary sizes on mixed Indic + English + code text. Measure fertility (tokens per word) and bits-per-byte, *not* per-token perplexity, at fixed 10M–50M model size. Bits-per-byte makes models with different tokenizers comparable. This is a standard methodological point; no specific Indic tokenizer paper was verified in this session.
  6. **Code completion at 50M–150M:** evaluate with execution-based pass@k on HumanEval/MBPP-style tests. Expect low absolute numbers (inference; no source verified for 125M HumanEval figures). A cleaner signal may come from a narrow domain (e.g., a DSL) with its own unit tests.
  7. **Learned search guidance for program synthesis:** a 10M–50M policy/value model guiding enumerative or beam search on a DSL. Small models are the natural regime here, because the search does the heavy lifting.
- **Toy vs meaningful:** an experiment is meaningful when it (a) compares conditions at matched compute, (b) uses several seeds or confidence intervals, (c) includes a baseline from a published paper or released checkpoint, and (d) states which result is expected to transfer (rankings and LR behaviour) and which is not (absolute capability).

### Gaps
- I did not fetch the papers on Mamba (2312.00752), RWKV, Chinchilla (2203.15556), Kaplan scaling laws, μTransfer, or the "emergent abilities mirage" paper in this session. Cite them only after verification.
- I found no verified source on Indic tokenizer studies (fertility or fairness across scripts).
- I found no verified HumanEval/MBPP pass@1 figures for models in the 10M–150M range.
- I found no counter-evidence paper showing small-scale results *failing* to transfer, beyond DataDecide's roughly 20% error rate and its note that SocialIQA is unpredictable.

## Q5. Fine-tuning existing small open models with LoRA/QLoRA via mlx-lm: memory and speed

### Takeaway
mlx-lm supports LoRA, QLoRA (automatic when the base model is quantized), DoRA and full fine-tuning. The only official speed figure is about 250 tokens/sec for Mistral-7B LoRA on an M1 Max (32 GB). Memory is controlled with batch size, `--num-layers`, gradient checkpointing and shorter sequences. Inference: a 48 GB M4 machine can comfortably LoRA or QLoRA models up to about 7–8B, and can full-fine-tune sub-1B models such as SmolLM2-135M/360M.

### Cited Findings
- mlx-lm LoRA on an **M1 Max 32 GB**, Mistral-7B on the wikisql example, "runs at about 250 tokens-per-second". — [mlx-lm LORA.md](https://raw.githubusercontent.com/ml-explore/mlx-lm/main/mlx_lm/LORA.md)
- Memory controls:
  - `--batch-size` (default 4; drop to 2 or 1);
  - `--grad-accumulation-steps`;
  - `--num-layers` (default 16; 8 or 4 cuts backprop memory);
  - `--grad-checkpoint`;
  - splitting long examples.

  On a 32 GB machine, Mistral-7B with `--batch-size 1 --num-layers 4` "should run reasonably fast". QLoRA runs when `--model` is a quantized model (convert with `-q`). `--fine-tune-type` accepts `lora`, `dora` or `full`. — [mlx-lm LORA.md](https://raw.githubusercontent.com/ml-explore/mlx-lm/main/mlx_lm/LORA.md)
- arXiv 2501.14925 found LoRA fine-tuning of GPT-2 large feasible on M2-series Macs. Full fine-tuning of GPT-2 XL used ZeRO-Offload on CUDA for comparison. — [arXiv 2501.14925](https://arxiv.org/html/2501.14925v2)

### Inferences
- **ESTIMATE.** Base memory footprints: weights for 7B bf16 ≈ 14 GB, 7B 4-bit ≈ 4 GB, 1.7B bf16 ≈ 3.4 GB. Full fine-tune with AdamW needs roughly 16 bytes per parameter: 135M ≈ 2 GB, 360M ≈ 6 GB, 1.7B ≈ 27 GB plus activations, which is tight on 48 GB.
- On 48 GB, 7–8B LoRA in bf16 and 7–14B QLoRA in 4-bit should fit with batch 1–4 and gradient checkpointing. Speed on M4 Max should be at least the M1 Max's 250 tok/s for 7B. Measure this; it is not verified.
- For Parinamakramam, fine-tuning a permissively licensed small model (e.g., SmolLM2 or Qwen2.5-Coder-0.5B/1.5B) on a lawful code subset is probably a faster route to a usable code model than pretraining from scratch on the Mac. Check each model's licence first; I did not verify them in this session.

### Gaps
- I found no official mlx-lm peak-memory tables, and no M4-specific LoRA throughput numbers.
- SmolLM2 and Qwen2.5-Coder licences and sizes were not fetched in this session.
