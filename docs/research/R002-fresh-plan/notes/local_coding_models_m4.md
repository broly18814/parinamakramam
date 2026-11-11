# Running open-weight coding models locally on a MacBook Pro M4 (48 GB unified memory), as of 12 November 2026

Scope note: research done 12 Nov 2026 with about 18 search/fetch calls. Most speed numbers come from community benchmark pages (oMLX), not from controlled studies. Most quality numbers are **vendor-reported** SWE-bench Verified scores. Older or estimated figures are flagged inline.

**Chip identification matters.** A 48 GB MacBook Pro M4 is never the base M4. 48 GB is offered only with the **M4 Pro (273 GB/s memory bandwidth)** or with the **16-core-CPU / 40-core-GPU M4 Max (546 GB/s)**. The 14-core M4 Max has 410 GB/s and ships with 36 GB. Source: [MacRumors M4 vs M4 Pro vs M4 Max guide](https://www.macrumors.com/guide/m4-vs-m4-pro-vs-m4-max), [9to5Mac on M4 Max](https://9to5mac.com/2024/10/30/m4-max-chip-has-16-core-cpu-40-core-gpu-and-35-increase-in-memory-bandwidth/), [Apple MacBook Pro specs](https://apple.com/uk/macbook-pro/specs). The founder should run "About This Mac" to confirm which chip they have. Generation speed on the M4 Max is roughly 2x the M4 Pro for the same model, because decode speed scales with bandwidth. All measured numbers below are labelled with the exact chip.

## 1. Which current open-weight coding/agentic models fit in 48 GB at usable quantisation?

### Takeaway
The 2026 sweet spot for a 48 GB Mac is the **Qwen 3.6 family (April 2026, Apache-2.0)**:
- **Qwen3.6-35B-A3B** is a mixture-of-experts model (only about 3B parameters active per token, so it is fast). It is about 20 GB at 4-bit and about 37 GB at 8-bit.
- **Qwen3.6-27B** is dense (all parameters active, so higher quality but slower). It is about 17 GB at 4-bit and about 22–30 GB at Q6–Q8.

Other models that fit are Qwen3-Coder-30B-A3B (2025), Devstral Small 2 (24B), gpt-oss-20b and GLM-4.7-Flash (30B-A3B). Qwen3-Coder-Next (80B-A3B) is borderline or too large for 48 GB. Frontier open-weight models (DeepSeek V4, Kimi K2.6, GLM-5, MiniMax M3) do not fit.

### Cited Findings
- **Qwen3.6-35B-A3B**: 35B total, 3B active MoE, Apache-2.0, 262,144-token native context (extensible to about 1M with YaRN), released April 2026 — [Hugging Face model card](https://huggingface.co/Qwen/Qwen3.6-35B-A3B)
- **Qwen3.6-27B**: 27B dense, Apache-2.0, 262,144-token native context, April 2026 — [Hugging Face model card](https://huggingface.co/Qwen/Qwen3.6-27B)
- Approximate file sizes, per a third-party guide:
  - Qwen3.6-35B-A3B: about 20 GB at Q4_K_M / MLX 4-bit, about 37 GB at Q8, about 70 GB at bf16.
  - Qwen3.6-27B: about 16.8 GB at Q4_K_M, about 22–30 GB at Q6–Q8.
  - Gemma 4 26B-A4B: about 15 GB at Q4.
  - Qwen2.5-Coder-32B: about 20 GB at Q4.
  - Llama 3.3 70B: about 40 GB at Q4.
  - DeepSeek V4-Flash (284B MoE): 110 GB or more even at 2-bit.
  - Source: [InsiderLLM, "Best Local LLMs for Mac in 2026" (updated 23 Jul 2026)](https://insiderllm.com/guides/best-local-llms-mac-2026/)
- Measured fit on a 48 GB Mac (an M5 Pro, not an M4): Qwen3.6-35B-A3B at MXFP8 in Ollama used **37 GB of 48 GB**. The author ruled out DeepSeek V4 Flash and Kimi K2.6 as too large — [Igor Kulman, 6 May 2026](https://blog.kulman.sk/running-local-llm-coding-server/)
- Measured peak memory on an M4 Pro 48 GB with oMLX (an MLX-based server):
  - Qwen3-Coder-30B-A3B 4-bit: 17.1 GB at 4k context — [oMLX benchmark fh0qhmnx](https://omlx.ai/benchmarks/fh0qhmnx)
  - Qwen3.6-35B-A3B-OptiQ 4-bit: 21.7 GB at 1k context, rising to 28.2 GB at 64k context — [oMLX benchmark z9qjy26p](https://omlx.ai/benchmarks/z9qjy26p)
  - Qwen3.6-27B 4-bit: 17.3 GB at 4k context — [oMLX benchmark b1j1yyks](https://omlx.ai/benchmarks/b1j1yyks)
- **Qwen3-Coder-Next** (released about 3 Feb 2026): 80B total / 3B active, Apache-2.0, 256K context, non-thinking only (it never produces `<think>` reasoning blocks). It officially supports MLX-LM, Ollama, LM Studio and llama.cpp. The model card suggests cutting context to about 32K if the server hits out-of-memory errors — [Hugging Face model card](https://huggingface.co/Qwen/Qwen3-Coder-Next)
- An aggregated guide summary says Qwen3-Coder-Next needs about 48.4 GB for weights alone and recommends 64 GB as the minimum tier. This came from a search-result summary of several 2026 "best local coding model" guides and the exact page was not verified — [aicomputerguide](https://aicomputerguide.com/guides/best-local-coding-models-2026/), [Kilo blog](https://blog.kilo.ai/p/the-best-local-coding-models-for)
- **Devstral Small 2** (24B): Apache-2.0. **Devstral 2** (123B) is too large for 48 GB and uses a "modified MIT" licence — [Mistral, Devstral 2 announcement](https://mistral.ai/news/devstral-2-vibe-cli/)
- **GLM-4.7-Flash**: 30B-A3B MoE, MIT licence — [NYU Shanghai RITS summary](https://rits.shanghai.nyu.edu/ai/glm-4-7-flash-z-ais-efficient-30b-moe-model-for-coding-and-agents/)
- **gpt-oss-20b**: Apache-2.0 (licence as recorded by [BenchLM](https://benchlm.ai/benchmarks/swe-bench-verified)). It runs in MXFP4 (a native 4-bit format) under oMLX on M4 Pro machines with 24 GB and 48 GB — [search summary of oMLX pages](https://omlx.ai/benchmarks/ywfs6s6x)
- Ollama's own `ollama launch` docs and guides recommend glm-4.7-flash, qwen3-coder and gpt-oss:20b as local coding models — [Ollama blog: launch](https://registry.ollama.ai/blog/launch)

### Inferences
- On 48 GB, the practical choices are:
  - (a) Qwen3.6-35B-A3B at 4-bit or 8-bit, for speed;
  - (b) Qwen3.6-27B at 4-bit to 8-bit, for best quality per GB;
  - (c) Devstral Small 2, gpt-oss-20b or GLM-4.7-Flash as alternatives.
- Arithmetic check: 80B parameters × about 4.5 bits per weight ≈ 45 GB. So Qwen3-Coder-Next at 4-bit leaves almost nothing for macOS, the KV cache (the memory that holds the conversation context) or an IDE. It is not a realistic daily driver on 48 GB, and a 3-bit quant would cost quality.
- macOS reserves part of unified memory for itself, and by default the GPU can use only a fraction of it (commonly cited around 70–75%). This implies about 32–36 GB usable for model plus KV cache. **This figure is not from a source found in this research; treat it as unverified.**

### Gaps
- No primary sources were fetched for Seed-Coder, Granite code, Codestral, DeepSeek-Coder-V2-Lite or Qwen2.5-Coder 2026 status. By late 2026 these appear to be superseded by the Qwen 3.5/3.6 and GLM-4.7 generation. Their only mentions came via guide tables, for example Qwen2.5-Coder-32B at about 20 GB Q4 in InsiderLLM.
- No "GLM-4.x Air" 2026 data was gathered. GLM-4.5-Air (about 106B total) would not fit 48 GB at 4-bit by arithmetic.
- The exact usable GPU memory limit on macOS 26 was not sourced.

## 2. Measured generation and prompt-processing speeds on M4-class machines

### Takeaway
On an **M4 Pro 48 GB (273 GB/s)** with MLX (via oMLX), measured speeds are:
- MoE models with about 3B active parameters (Qwen3-Coder-30B-A3B, Qwen3.6-35B-A3B, gpt-oss-20b): about **60–85 tokens/s generation** and about **600–900 tokens/s prompt processing** at short context.
- Dense **Qwen3.6-27B**: only about **15 tokens/s generation** and about **125 tokens/s prompt processing**.

Speed drops at long context. Qwen3.6-35B-A3B falls to about 45 tokens/s generation at 32k and 34 tokens/s at 64k. Time-to-first-token on a 32k prompt is about 56 seconds. That delay is the real bottleneck for agentic coding, because agents send very large prompts.

### Cited Findings (all measured unless marked as an estimate)
| Model / quant | Chip, memory | Runtime | Context | Prompt processing (tok/s) | Generation (tok/s) | Date | Source |
|---|---|---|---|---|---|---|---|
| Qwen3-Coder-30B-A3B-Instruct 4-bit | M4 Pro 20-core GPU, 48 GB | oMLX v0.4.1, macOS 26.5 | 1k / 4k | 750 / 768 | 72.6 / 61.1 (TTFT 5.3 s at 4k) | 2026-06-05 | [oMLX fh0qhmnx](https://omlx.ai/benchmarks/fh0qhmnx) |
| same, batched 2× / 4× | same | same | 1k | – | 103 / 123 aggregate | 2026-06-05 | [oMLX fh0qhmnx](https://omlx.ai/benchmarks/fh0qhmnx) |
| Qwen3.6-35B-A3B-OptiQ 4-bit | M4 Pro 16-core GPU, 48 GB | oMLX v0.4.1 | 1k / 4k / 8k / 16k / 32k / 64k | 638 / 743 / 726 / 674 / 582 / 452 | 61.6 / 58.4 / 55.6 / 50.5 / 44.6 / 33.8 (TTFT 56 s at 32k) | 2026-06-04 | [oMLX z9qjy26p](https://omlx.ai/benchmarks/z9qjy26p) |
| Qwen3.6-35B-A3B (various quants) | M4 Pro 16- and 20-core GPU, 48 GB | oMLX v0.3.7–v0.3.8 | 1k–4k | 568–899 | 37.6–86.2 | 2026 | search summary of oMLX pages, e.g. [cooa5fyn](https://omlx.ai/benchmarks/cooa5fyn) (individual pages not all fetched) |
| Qwen3.6-27B 4-bit (dense) | M4 Pro 20-core GPU, 48 GB | oMLX v0.3.6, macOS 26.3 | 1k / 4k | 124.6 / 125.7 | 15.6 / 15.0 | 2026-04-25 | [oMLX b1j1yyks](https://omlx.ai/benchmarks/b1j1yyks) |
| Qwen3.6-27B 4-bit | M4 Pro 16-core GPU, 64 GB | oMLX | 1k / 8k | – | about 15 | 2026 | [oMLX iwgft0pe](https://omlx.ai/benchmarks/iwgft0pe) (search summary) |
| Qwen3.6-27B 4-bit | M4 Max 32-core GPU, 36 GB (410 GB/s) | oMLX | 4k | – | about 20.5 | 2026 | [oMLX g6fizp89](https://omlx.ai/benchmarks/g6fizp89) (search summary) |
| Qwen3.6-27B MTP 4-bit | M4 Max, 128 GB | oMLX | 1k | – | about 28.6 | 2026 | [oMLX 2mo1fii4](https://omlx.ai/benchmarks/2mo1fii4) (search summary) |
| Qwen3.6-27B 4-bit | M4 Max, 128 GB | MLX | – | – | about 22 high-power / about 11 low-power mode | 2026-05-10 | [blog post](https://myblog-6mw.pages.dev/posts/local-llm-m4-max-benchmark-2026-05-10/) (search summary) |
| gpt-oss-20b MXFP4 | M4 Pro 20-core GPU, 48 GB | oMLX | 1k | – | 65.5 | 2026 | search summary of [oMLX pages](https://omlx.ai/benchmarks/ywfs6s6x) |
| gpt-oss-20b MXFP4 | M4 Pro 16-core GPU, 24 GB | oMLX | 4k | – | 49.6 | 2026 | same |
| Qwen3-Coder-30B-A3B 8-bit | M4 Max | MLX | – | – | 29–41 | – | [JacobPEvans/mlx-benchmarks dataset](https://huggingface.co/datasets/JacobPEvans/mlx-benchmarks/viewer/default/train) (search summary) |
| Qwen3.6-35B-A3B Q4 | M4 Max | MLX-LM / Ollama / LM Studio | – | – | 45–55 / 40–50 / 40–55 | 2026 | [InsiderLLM](https://insiderllm.com/guides/best-local-llms-mac-2026/) ("approximate community reports", **not measured by the author**) |
| GLM-4.7-Flash, custom Metal Marlin quant | M4 Max | non-MLX custom runtime | 2k | 42 | 5.4 | – | [HF Kearm/GLM-4.7-Flash-Trellis-MM](https://huggingface.co/Kearm/GLM-4.7-Flash-Trellis-MM) (search summary; atypical runtime, **not representative of MLX**) |

- **Estimates, not measurements:**
  - willitrunai projects Qwen3.6-27B Q4_K_M at about 17 tokens/s on M4 Pro 48 GB and about 27 tokens/s on M4 Max 128 GB — [willitrunai](https://willitrunai.com/can-run/qwen-3.6-27b-on-m4-max-128gb)
  - It also estimates gpt-oss-20b at about 40 tokens/s (Q4_K_M) on M4 Pro and about 66 tokens/s on M4 Max — [willitrunai](https://willitrunai.com/es/can-run/gpt-oss-20b-on-m4-max-48gb)
- Bandwidth reference figures: M4 Pro 273 GB/s; M4 Max 410–546 GB/s; M5 Max 460–614 GB/s; M3 Ultra 819 GB/s — [InsiderLLM](https://insiderllm.com/guides/best-local-llms-mac-2026/); M4 figures corroborated by [MacRumors](https://www.macrumors.com/guide/m4-vs-m4-pro-vs-m4-max)
- On an M5 Pro 48 GB, the `mlx_lm.server` (v0.31.3) crashed with a Metal out-of-memory error after a few exchanges, with both Qwen3.6-27B and 35B-A3B. The cause was a KV cache that grew without limit. The author switched to Ollama. After Ollama unloads an idle model (default 5 minutes), reloading takes about 2 minutes — [Igor Kulman, May 2026](https://blog.kulman.sk/running-local-llm-coding-server/)

### Inferences
- On an M4 Pro, the MoE models at about 3B active parameters (Qwen3.6-35B-A3B, Qwen3-Coder-30B-A3B, gpt-oss-20b, GLM-4.7-Flash) are the only ones that feel interactive. Dense 27B at about 15 tokens/s is usable for chat but slow for agent loops that generate thousands of tokens.
- On an M4 Max 48 GB (546 GB/s), expect about 1.5–2x higher generation speed. Measured M4 Max 48 GB data was not found; the M4 Max figures above come from 36 GB and 128 GB machines.
- The bigger issue for agents is **prompt processing**. Coding agents send 10k–40k-token system prompts plus file contents, so at about 600 tokens/s each fresh 30k-token prompt costs about 50 seconds before the first token. Prompt caching (reusing the already-processed part of a prompt between turns, which oMLX and LM Studio support) is therefore essential.

### Gaps
- No exact-hardware llama.cpp `llama-bench` results were found for M4 Pro 48 GB (the llama.cpp Apple Silicon discussion thread was not fetched).
- No measured Devstral Small 2 speeds on M4 were found. By arithmetic (24B dense at 4-bit is about 13–14 GB), expect roughly 15–20 tokens/s on M4 Pro, similar to Qwen3.6-27B. **This is unverified.**
- No measured numbers exist specifically for a 48 GB M4 Max.
- oMLX pages are user-submitted and not independently verified. Quant variants and versions differ between runs.

## 3. Licences and commercial-use terms

### Takeaway
Most of the models that fit 48 GB are permissively licensed: Qwen 3.5/3.6 and Qwen3-Coder are Apache-2.0, Devstral Small 2 is Apache-2.0, gpt-oss is Apache-2.0, and GLM-4.7-Flash is MIT. A solo company can build on and resell products using them. The exceptions are the larger, non-fitting models. Devstral 2 (123B) uses a "modified MIT" licence that reportedly bars companies with over US$20M monthly revenue. Kimi uses a modified MIT licence, and MiniMax uses a community licence.

### Cited Findings
- Qwen3.6-35B-A3B and Qwen3.6-27B: Apache-2.0 — [HF](https://huggingface.co/Qwen/Qwen3.6-35B-A3B), [HF](https://huggingface.co/Qwen/Qwen3.6-27B)
- Qwen3-Coder-Next: Apache-2.0 — [HF](https://huggingface.co/Qwen/Qwen3-Coder-Next)
- Devstral Small 2: Apache-2.0. Devstral 2 (123B): modified MIT — [Mistral](https://mistral.ai/news/devstral-2-vibe-cli/)
- The Devstral 2 modified MIT licence reportedly says companies above US$20M monthly revenue are "not authorized to exercise any rights under this license". The official announcement page does not state the cap, so check the LICENSE file — [Implicator.ai](https://www.implicator.ai/mistrals-open-source-trick-build-a-great-model-gate-it-behind-revenue-caps-call-it-freedom/)
- GLM-4.7-Flash: MIT — [NYU Shanghai RITS](https://rits.shanghai.nyu.edu/ai/glm-4-7-flash-z-ais-efficient-30b-moe-model-for-coding-and-agents/)
- Licences recorded on BenchLM: gpt-oss-20b and gpt-oss-120b Apache-2.0; DeepSeek V4 Pro and Flash MIT; GLM-5 MIT; Kimi K2.5 and K2.6 "Modified MIT"; MiniMax M3 "MiniMax Community License"; Qwen3.6-Plus and Qwen3.7 proprietary (not open weight) — [BenchLM SWE-bench Verified page, updated 11 Nov 2026](https://benchlm.ai/benchmarks/swe-bench-verified)

### Inferences
- For a ₹0 solo company, Apache-2.0 Qwen 3.6 models are the cleanest base. They allow commercial use, modification and redistribution with notice, and include a patent grant (a standard Apache-2.0 feature).
- Alibaba now keeps its newest flagship models closed: Qwen3.6-Plus and Qwen3.7 are proprietary per BenchLM. Future open releases from them are not guaranteed.

### Gaps
- The full licence texts were not read directly. Acceptable-use clauses (for example in the gpt-oss usage policy) were not checked.

## 4. Quality on SWE-bench Verified and similar benchmarks, and the gap to frontier models

### Takeaway
On developer-reported scores, the best model that fits 48 GB is **Qwen3.6-27B at 77.2% SWE-bench Verified** (SWE-bench Pro 53.5%, Terminal-Bench 2.0 59.3%). That is close to Claude Opus 4.5's 80.9% (late 2025). Current frontier hosted models are listed at **85–96%** on aggregators (Claude Opus 5 at 96%), so the gap is about 15–20 points. SWE-bench Verified itself is now considered saturated and contaminated, which makes those numbers less meaningful.

### Cited Findings
- **Qwen3.6-27B**: SWE-bench Verified 77.2, SWE-bench Pro 53.5, Terminal-Bench 2.0 59.3. On the same card, Claude 4.5 Opus scores 80.9 / 57.1 / 59.3 and Qwen3.5-397B-A17B scores 76.2 / 50.9 / 52.5 (vendor-reported) — [HF model card](https://huggingface.co/Qwen/Qwen3.6-27B)
- **Qwen3.6-35B-A3B**: SWE-bench Verified 73.4, SWE-bench Pro 49.5, Terminal-Bench 2.0 51.5, SWE-bench Multilingual 67.2. On the same card, Gemma4-31B scores 52.0 and Gemma4-26B-A4B scores 17.4 on SWE-bench Verified — [HF model card](https://huggingface.co/Qwen/Qwen3.6-35B-A3B)
- **Qwen3-Coder-Next**: SWE-bench Verified 70.6, SWE-bench Pro 44.3, Terminal-Bench 2.0 36.2 — [HF model card](https://huggingface.co/Qwen/Qwen3-Coder-Next)
- **Devstral Small 2**: SWE-bench Verified 68.0%. Devstral 2 (123B) scores 72.2% (vendor-reported, with an agent scaffold) — [Mistral](https://mistral.ai/news/devstral-2-vibe-cli/)
- **GLM-4.7-Flash**: SWE-bench Verified 59.2% (Z.ai-reported). Z.ai's own table lists Qwen3-30B-A3B at 22.0% and gpt-oss-20b at 34.0% — [NYU Shanghai RITS](https://rits.shanghai.nyu.edu/ai/glm-4-7-flash-z-ais-efficient-30b-moe-model-for-coding-and-agents/)
  - **Conflict:** BenchLM lists **gpt-oss-20b at 60.7%** and gpt-oss-120b at 62.4%, which appear to be OpenAI's own high-reasoning figures — [BenchLM](https://benchlm.ai/benchmarks/swe-bench-verified). The two sources clearly use different harnesses or reasoning settings.
- On a Q4 quantised build, one guide reports 73.4 for Qwen3.6-27B (vs 77.2 at full precision). The source is unclear and this may conflate it with the 35B-A3B figure — search summary of [aicomputerguide](https://aicomputerguide.com/guides/best-local-coding-models-2026/). **Treat as unverified.**
- **BenchLM leaderboard (updated 11 Nov 2026), top entries:**
  - Claude Opus 5: 96%
  - Claude Mythos 5: 95.5%
  - Claude Fable 5: 95%
  - Fireworks Ember-1: 92.2%
  - Claude Opus 4.8: 88.6%
  - Claude Opus 4.7: 87.6%
  - Claude Sonnet 5: 85.2%
  - GPT-5.3 Codex: 85%
  - Source: [BenchLM](https://benchlm.ai/benchmarks/swe-bench-verified)
- **Best open-weight models on BenchLM** (none fit 48 GB):
  - DeepSeek V4 Pro: 80.6%
  - MiniMax M3: 80.5%
  - Kimi K2.6: 80.2%
  - DeepSeek V4 Flash: 79%
  - GLM-5: 77.8%
  - Source: [BenchLM](https://benchlm.ai/benchmarks/swe-bench-verified)
- BenchLM moved SWE-bench Verified to "display-only" because "its tests are contaminated and saturated". It does not label each score as vendor-reported or independently run — [BenchLM](https://benchlm.ai/benchmarks/swe-bench-verified)
- One aggregator says the official swebench.com leaderboard has no Verified entry dated after 2026-02-26, so newer scores are vendor or aggregator figures. Gemini 3.1 Pro was listed at 80.6% in a March 2026 snapshot — search summary of [llm-stats](https://llm-stats.com/benchmarks/swe-bench) / [BenchLM](https://benchlm.ai/benchmarks/swe-bench-verified)

### Inferences
- A local Qwen3.6-27B is roughly at "late-2025 frontier" level on SWE-bench Verified, assuming vendor numbers hold after quantisation. It is about 1 year and 15–20 points behind November 2026 frontier models.
- On harder or newer benchmarks (SWE-bench Pro around 50% vs frontier 57%+ for Opus 4.5 alone), the gap is likely larger. Real-world local agent performance will also be lower than these numbers suggest, because:
  - the reported numbers use full-precision weights and long contexts;
  - local setups use 4-bit quants and contexts capped at 16k–64k;
  - local prompt processing is slow.
- **Messaging risk:** "near-frontier quality locally" is only defensible for the 27B dense model, and that model is slow (about 15 tokens/s) on an M4 Pro.

### Gaps
- No independent (non-vendor) SWE-bench run of quantised Qwen 3.6 models on Apple hardware was found.
- The official swebench.com leaderboard was not fetched directly. The frontier scores in the mid-90s come only from an aggregator and should be checked before quoting.
- The Aider Polyglot leaderboard was not consulted.

## 5. Tooling for local agentic coding, and known failure modes of small local models

### Takeaway
The tooling is mature:
- Ollama's `ollama launch` (v0.15, Jan 2026) starts Claude Code, OpenCode, Codex or Droid against local models in one command. Ollama has spoken Anthropic's Messages API since v0.14.
- LM Studio, mlx-lm, oMLX and llama.cpp all expose OpenAI-compatible servers that Cline, Continue, Kilo and OpenCode can use.

The dominant failure modes are:
- **silent context truncation**, because Ollama's default context window is small (2k–4k historically, 32k in recent builds);
- tool-call format drift in smaller models;
- tool-calling degradation at around 30k tokens;
- KV-cache memory blow-ups in the mlx-lm server.

### Cited Findings
- `ollama launch` was added in v0.15 (January 2026) and supports Claude Code, OpenCode, Codex and Droid. Ollama added Anthropic Messages API support in v0.14, so Claude Code needs no proxy. The recommended local models are glm-4.7-flash, qwen3-coder and gpt-oss:20b, with at least 64k context suggested — [Ollama blog](https://registry.ollama.ai/blog/launch), [AlternativeTo news](https://alternativeto.net/news/2026/1/ollama-debuts-ollama-launch-to-run-coding-tools-with-local-or-cloud-models)
- Qwen3-Coder-Next lists integration with "Claude Code, Qwen Code, Qoder, Kilo, Trae, Cline". Tool calling goes through an OpenAI-compatible API using the `qwen3_coder` tool-call parser — [HF](https://huggingface.co/Qwen/Qwen3-Coder-Next)
- Qwen3.6 claims strong tool calling. It recommends the vLLM/SGLang `--tool-call-parser qwen3_coder` flag and Qwen-Agent with MCP (Model Context Protocol, a standard for connecting models to tools) — [HF](https://huggingface.co/Qwen/Qwen3.6-35B-A3B)
- Working 48 GB Mac setup: Ollama serving Qwen3.6-35B-A3B MXFP8, accessed from OpenCode via the `@ai-sdk/openai-compatible` provider, `num_ctx` set to 16384, `OLLAMA_KEEP_ALIVE=24h`.
  - Failures seen: the mlx-lm server crashed with a Metal out-of-memory error because the KV cache grew without limit. A generic Ollama Q4_K_M 27B gave weak code, which the author attributed to the quant and a presence penalty of 1.5.
  - Source: [Igor Kulman, May 2026](https://blog.kulman.sk/running-local-llm-coding-server/)
- When input exceeds Ollama's context window, it silently drops the oldest tokens with no error. Agent harnesses send large tool JSON schemas, so truncation can remove the tool definitions entirely: the model then behaves as if it has no tools. The fix is to set `OLLAMA_CONTEXT_LENGTH` or `num_ctx` and check with `ollama ps` — [Aident.ai](https://aident.ai/blog/fix-claude-code-ollama-context-truncation), [Kaxo OpenClaw guide](https://kaxo-website.pages.dev/insights/openclaw-ollama-local-llm-guide), [Sebastian Zehner, Ollama/OpenCode](https://sebastianzehner.netlify.app/posts/ollama-context-window-optimization-opencode/)
- 7B–14B models drop the tool-call format after the first tool result, or write the tool call as plain text instead of executing it — [n8n community](https://community.n8n.io/t/tool-calling-chain-with-local-ollama-models-7b-14b-2nd-tool-never-executed/280320)
- Local models claim to have done an action when they did not — [OpenClawDC](https://openclawdc.com/blog/local-model-says-it-did-it-but-didnt/)
- llama.cpp issue: tool calls break down (for example repeated calls to the same tool) at roughly 30k tokens of context — [llama.cpp issue #20164](https://github.com/ggml-org/llama.cpp/issues/20164) (via search summary)
- Some failures are attributed to chat-template mismatches rather than model size — [Towards AI, "10 silent defaults"](https://pub.towardsai.net/10-silent-defaults-that-make-your-local-llm-look-dumber-than-it-is-96a65f41b96c) (search summary)

### Inferences
- A differentiated product could add value exactly where these failure modes sit:
  - auto-sizing context to available memory;
  - KV-cache limits and prompt caching;
  - template and tool-parser validation;
  - tool-call repair and retries;
  - compact tool schemas that fit in 16k–32k.
- Generic "run a model locally" is already commoditised by Ollama, LM Studio and `ollama launch`.

### Gaps
- No Cline-, Continue- or Aider-specific failure reports were gathered.
- No quantitative tool-calling reliability benchmarks (for example BFCL or tau-bench) were found for quantised local models.

## 6. Is "private, local-first" a documented need, and who already offers it?

### Takeaway
There is real but mostly vendor-documented demand. Tabnine sells SaaS, VPC, on-premise and fully air-gapped deployments, priced at about $39 per user per month in 2026. It was named a Gartner Magic Quadrant "Visionary" (2025, and reportedly again in May 2026 for Enterprise AI Coding Agents). GitHub Copilot and Gemini Code Assist reportedly lack air-gapped options. No hard market-size or survey data on demand was found. Free local stacks (Ollama plus OpenCode, Claude Code or Cline) already serve individual developers, which compresses the space for a paid solo-founder product.

### Cited Findings
- Tabnine offers SaaS, VPC, on-premise and fully air-gapped deployment ("no external network connections at all"). A 2026 pricing check lists $39 per user per month (annual) — [Codegen Tabnine review](https://codegen.com/ai-tools/tabnine/), [dev.to Tabnine review 2026](https://dev.to/jovan_chan_9500711396d4e6/tabnine-review-2026-is-privacy-first-ai-coding-worth-39-a-month-1ebf)
- Tabnine was named a Visionary in the 2025 Gartner Magic Quadrant — [Generation-NT press release](https://www.generation-nt.com/communiques-presse/tabnine-named-visionary-in-the-2025-gartner-magic-quadrant-for-2062614). A later page reports a Visionary placement in the May 2026 Gartner MQ for Enterprise AI Coding Agents — [RubinLake tech radar](https://rubinlake.com/fr/technology-radar/developer-ai-and-delivery/tabnine-enterprise)
- A Tricentis acquisition of Tabnine (30 July 2026) was reported by one source but **not corroborated** — search summary.
- Copilot reportedly cannot offer on-premise or air-gapped deployment. Gemini Code Assist runs only on Google Cloud — [dev.to Copilot vs Tabnine 2026](https://dev.to/rahulxsingh/github-copilot-vs-tabnine-the-complete-comparison-2026-49d8), [Augment: Tabnine vs Gemini Code Assist](https://www.augmentcode.com/tools/tabnine-vs-gemini-code-assist), [Tech-Insider](https://tech-insider.org/au/?p=525) (affiliate-style sources)
- An overview of enterprise AI code assistants for air-gapped environments exists — [IntuitionLabs](https://intuitionlabs.ai/articles/enterprise-ai-code-assistants-air-gapped-environments) (not fetched in full). Its point that "air-gapped doesn't mean compliant" is cited in search summaries.
- NVIDIA publishes a playbook for connecting CLI coding agents to local models — [NVIDIA build playbook](https://build.nvidia.com/playbooks/cli-coding-agent)

### Inferences
- The need is documented mainly through vendor positioning: Tabnine's whole enterprise pitch, and the air-gapped offerings from large vendors. Defence, finance, healthcare and government buyers are the usual targets, but **no buyer survey data was found to confirm this**.
- **Feasibility:** technically yes. A 48 GB M4 Pro runs Qwen3.6-35B-A3B at about 45–60 tokens/s with 32k context, and Qwen3.6-27B (77% SWE-bench Verified, vendor-reported) at about 15 tokens/s.
- **Differentiation:** weak as a generic "local coding assistant". Ollama, LM Studio, OpenCode, Cline, Continue, Kilo and Claude Code via `ollama launch` cover this for free, and Tabnine covers enterprise air-gapped deployment.
- Possible openings:
  - (a) reliability engineering for local agent loops (context management, tool-call repair, verified evals on Apple Silicon);
  - (b) a niche vertical with compliance packaging;
  - (c) honest, reproducible benchmarks of quantised models on Macs, which are currently scattered across community pages.
- Selling enterprise air-gapped deployment as a solo founder with no interviews (per project constraints) would be very hard, because enterprise procurement needs security reviews and support.

### Gaps
- No independent surveys or market-size data were found on demand for code-never-leaves-the-machine assistants. Stack Overflow and JetBrains developer surveys, and Gartner data, were not retrieved.
- Other privacy-focused competitors were not researched: Tabby (self-hosted), Refact.ai, Continue's enterprise offering, Sourcegraph self-hosted, JetBrains local models and Cursor privacy mode.
