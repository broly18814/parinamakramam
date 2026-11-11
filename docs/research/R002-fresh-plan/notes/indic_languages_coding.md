# Indic-language (Telugu/Hindi) resources and benchmarks for AI-assisted software engineering (as of 12 Nov 2026)

Method note: licence values below were read on 12 Nov 2026 from the Hugging Face (HF) model and dataset metadata through the public HF API (`cardData.license`), from README/LICENSE files, and from official GitHub READMEs. "Gated: auto" means you must accept terms on HF before downloading. "Gated: manual" means the owner approves each request. Being downloadable does NOT mean commercial use is allowed. Every row says which.

## 1. Which AI4Bharat and other Indic datasets and models can lawfully be used, especially commercially?

### Takeaway
Most AI4Bharat assets are commercially usable: CC0, CC-BY-4.0 or MIT, with attribution. The main exceptions are Samanantar (CC-BY-NC-4.0, non-commercial), Airavata (Llama 2 Community Licence) and IndicGenBench (CC-BY-SA-4.0, share-alike). Among Indian LLMs, the Sarvam-M, Sarvam-30B and Sarvam-105B weights are Apache-2.0, so they can be used commercially. Sarvam-1 is research/non-commercial only. Krutrim-2 needs a separate commercial agreement. Sarvam-Translate is GPL-3.0. BharatGPT-3B-Indic is "other" and manually gated, and I could not verify its terms.

### Cited Findings

**AI4Bharat (official cards/repos)**
- **IndicTrans2** model checkpoints: MIT. It covers all 22 scheduled Indian languages (25 language-script variants plus English). The latest update listed is 18 Jan 2025 (RoPE long-context variants up to 2048 tokens). The paper is TMLR 2023. — [IndicTrans2 GitHub](https://github.com/AI4Bharat/IndicTrans2); HF metadata for `ai4bharat/indictrans2-en-indic-1B` says `license: mit`, gated: auto, last modified 8 Oct 2026 — [HF](https://huggingface.co/ai4bharat/indictrans2-en-indic-1B)
- **BPCC** (Bharat Parallel Corpus Collection) has a split licence. Existing mined corpora (NLLB & Samanantar), existing seed corpora (NLLB-Seed, ILCI, MASSIVE), newly added mined corpora (Samanantar++ & Comparable) and back-translation data (BPCC-BT) are **CC0**. Newly added seed corpora (BPCC-H-Wiki, BPCC-H-Daily) and the IN22 test sets (IN22-Gen, IN22-Conv) are **CC-BY-4.0**. The repo also states: "We do not own any of the text from which this data has been extracted." — [IndicTrans2 GitHub](https://github.com/AI4Bharat/IndicTrans2). The HF dataset card has no licence field in its metadata and is gated: auto — [HF ai4bharat/BPCC](https://huggingface.co/datasets/ai4bharat/BPCC)
- **Samanantar**: **CC-BY-NC-4.0, so commercial use is not allowed.** It covers English plus 11 Indic languages, Telugu and Hindi included. — [HF ai4bharat/samanantar](https://huggingface.co/datasets/ai4bharat/samanantar). Note: BPCC repackages "Existing Mined Corpora (NLLB & Samanantar)" under CC0, which conflicts with Samanantar's own CC-BY-NC-4.0 card. Treat this as unresolved; see Gaps.
- **IndicCorp v2**: the HF README says: "All the datasets created as part of this work will be released under a CC-0 license and all models & code will be release under an MIT license". There is no licence field in the HF metadata. Size: 20.9B tokens across 24 languages. — [HF ai4bharat/IndicCorpV2](https://huggingface.co/datasets/ai4bharat/IndicCorpV2); [IndicBERT GitHub](https://github.com/AI4Bharat/IndicBERT)
- **IndicBERT v2** models (e.g. `IndicBERTv2-MLM-only`, `IndicBERTv2-MLM-Sam-TLM`): **MIT**. They cover 23 Indic languages plus English. — [HF](https://huggingface.co/ai4bharat/IndicBERTv2-MLM-only); [IndicBERT GitHub](https://github.com/AI4Bharat/IndicBERT)
- **IndicXTREME**: nine NLU tasks, 20 languages, 105 evaluation sets. Its licence falls under the same blanket "datasets … CC-0" statement, but there is no aggregate HF card (the `ai4bharat/IndicXTREME` API lookup failed). Component sets differ: `ai4bharat/IndicQA` is CC-BY-4.0, and `ai4bharat/IndicXParaphrase` has no licence in its metadata. — [HF IndicCorpV2 README](https://huggingface.co/datasets/ai4bharat/IndicCorpV2); [HF IndicQA](https://huggingface.co/datasets/ai4bharat/IndicQA); [HF IndicXParaphrase](https://huggingface.co/datasets/ai4bharat/IndicXParaphrase)
- **Aksharantar** (transliteration): metadata says `license: cc`. The README breaks it down as "Manually collected data: Released under CC-BY license. Mined dataset (from Samanantar and IndicCorp): Released under CC0 license. Existing sources: Released under CC0 license." It covers 21 languages, Telugu and Hindi included. Last modified Aug 2023. — [HF ai4bharat/Aksharantar](https://huggingface.co/datasets/ai4bharat/Aksharantar)
- **IndicVoices** (speech): **CC-BY-4.0**, gated: auto, last modified 15 Jun 2026. — [HF ai4bharat/IndicVoices](https://huggingface.co/datasets/ai4bharat/IndicVoices)
- **Airavata** (Hindi instruction model): **Llama 2 Community Licence** (`license: llama2`), gated: auto, English and Hindi. — [HF ai4bharat/Airavata](https://huggingface.co/ai4bharat/Airavata). Its training data, `indic-instruct-data-v0.1`, has no licence field in its metadata. — [HF](https://huggingface.co/datasets/ai4bharat/indic-instruct-data-v0.1)
- **Sangraha** (pretraining corpus, verified/unverified/synthetic splits): **CC-BY-4.0**. It covers 17 languages, Telugu and Hindi included. — [HF ai4bharat/sangraha](https://huggingface.co/datasets/ai4bharat/sangraha). The README points to the technical report for licence details. — [arXiv 2401.15006](https://arxiv.org/abs/2401.15006)
- **IndicAlign** (instruction data): **CC-BY-4.0**, 15 languages. — [HF ai4bharat/indic-align](https://huggingface.co/datasets/ai4bharat/indic-align)
- **MILU** (Indic knowledge MCQ): **CC-BY-4.0**, gated: auto. It covers 11 languages including Telugu and Hindi. Last modified 8 Sep 2026, and MILU-1.5 is part of the October 2026 suite. — [HF ai4bharat/MILU](https://huggingface.co/datasets/ai4bharat/MILU); [Indic-LLM-Eval-Suite blog](https://ai4bharat.github.io/indic-llm-eval-suite-blog/)
- **IndicGenBench** (Google, not AI4Bharat): the HF config `IndicGenBench_flores_in` is **CC-BY-SA-4.0**, which is share-alike. It covers 29 languages. The GitHub repo licence is reported as "Other" (NOASSERTION). — [HF google/IndicGenBench_flores_in](https://huggingface.co/datasets/google/IndicGenBench_flores_in); [GitHub API](https://api.github.com/repos/google-research-datasets/indic-gen-bench)
- **Pralekha** (document alignment): CC-BY-4.0. — [HF](https://huggingface.co/datasets/ai4bharat/Pralekha)
- **New (Sep–Oct 2026) AI4Bharat code benchmarks**: `indic-humaneval`, `indic-mbpp` and `indic-swe-bench` are all **Apache-2.0**, non-gated, created 22 Sep 2026, and cover 14 languages including Telugu and Hindi. Details are under Q2. — [HF indic-humaneval](https://huggingface.co/datasets/ai4bharat/indic-humaneval); [HF indic-mbpp](https://huggingface.co/datasets/ai4bharat/indic-mbpp); [HF indic-swe-bench](https://huggingface.co/datasets/ai4bharat/indic-swe-bench)

**Other Indian models**
- **Sarvam-M**: **Apache-2.0**. Base model is `mistralai/Mistral-Small-3.1-24B-Base-2503`. It covers English plus 10 Indic languages. — [HF sarvamai/sarvam-m](https://huggingface.co/sarvamai/sarvam-m)
- **Sarvam-30B / Sarvam-105B**: **Apache-2.0**. They cover 22 Indian languages plus English. Sarvam-105B is a MoE model with 10.3B active parameters. — [HF sarvam-105b](https://huggingface.co/sarvamai/sarvam-105b); [HF sarvam-30b](https://huggingface.co/sarvamai/sarvam-30b); [Sarvam blog](https://www.sarvam.ai/blogs/sarvam-30b-105b)
- **Sarvam-1** (2B): the README says "Sarvam non-commercial license". LICENSE.md is the "Sarvam AI Research License", and §3.2 says use is "only … for non-commercial and Research Purposes, unless you have obtained explicit written permission". **Commercial use is not allowed** without written permission. — [HF sarvamai/sarvam-1](https://huggingface.co/sarvamai/sarvam-1)
- **Sarvam-Translate**: **GPL-3.0** (copyleft). — [HF sarvamai/sarvam-translate](https://huggingface.co/sarvamai/sarvam-translate)
- **Krutrim-2-instruct**: "Krutrim Community License Agreement v1.0". It defines "Commercial Use" as use where "more than 1 million monthly active users of the Licensee use the Software". The same licence also says "Commercial Use is permitted only through a separate commercial license agreement with Krutrim" and "Commercial Distribution: Prohibited unless authorized … This includes … integration into proprietary products". **Treat it as not commercially usable without a deal.** — [HF Krutrim-2-instruct LICENSE](https://huggingface.co/krutrim-ai-labs/Krutrim-2-instruct/blob/main/LICENSE.md)
- **BharatGPT-3B-Indic (CoRover)**: metadata `license: other`, gated: manual (owner approval). I could not read the README. **Licence terms not verified.** — [HF CoRover/BharatGPT-3B-Indic](https://huggingface.co/CoRover/BharatGPT-3B-Indic)
- **Google Gemma Indic variants**: an HF API search of Google's own models found no official Gemma model with "Indic" or "Hindi" in its name. The "Indic Gemma" models are community fine-tunes by Telugu-LLM-Labs (Navarasa 2.0, 2B/7B, plus Telugu-gemma). Their HF metadata has no licence field. — [HF Telugu-LLM-Labs](https://huggingface.co/Telugu-LLM-Labs). Gemma-family base models use the Gemma licence (e.g. `license: gemma` on [google/gemma-2-2b-jpn-it](https://huggingface.co/google/gemma-2-2b-jpn-it)).
- **NVIDIA Nemotron Indic pretraining data** (companion to the AI4Bharat suite, about 2.8T tokens across 22 languages): `Nemotron-Pretraining-Indic-CC-v1` is under "nvidia-data-agreement-for-model-training" and gated: manual. `Nemotron-Pretraining-Indic-Specialized-v1` is "other". The technical report is CC-BY-4.0. — [HF NVIDIA Indic CC](https://huggingface.co/datasets/nvidia/Nemotron-Pretraining-Indic-CC-v1); [Indic-LLM-Eval-Suite blog](https://ai4bharat.github.io/indic-llm-eval-suite-blog/)

**Telugu-specific (Swecha, IIIT Hyderabad)**
- **Swecha "Chandamama Kathalu"** (volunteer OCR of Chandamama stories, Telugu): HF `swechatelangana/chandamama-kathalu` is **CC-BY-NC-SA-4.0, so commercial use is not allowed**. — [HF](https://huggingface.co/datasets/swechatelangana/chandamama-kathalu). Press reports say Swecha "open-sourced everything" and was considering a distinct licence. Swecha and Ozonetel built a 7B Telugu SLM, and IIIT Hyderabad partnered with Swecha on a Telugu LLM. — [Analytics India Mag](https://analyticsindiamag.com/ai-trends/an-open-source-movement-led-to-indias-first-telugu-slm)
- **Telugu classification datasets** by HF user `mounikaiiith` (Telugu_Sentiment, Telugu_Emotion, Telugu-Hatespeech, Telugu-Sarcasm, Telugu_Clickbait): all **CC-BY-4.0**. — [HF mounikaiiith/Telugu_Sentiment](https://huggingface.co/datasets/mounikaiiith/Telugu_Sentiment)
- **Telugu-LLM-Labs** `telugu_alpaca_yahma_cleaned_filtered_romanized`: CC-BY-4.0. — [HF](https://huggingface.co/datasets/Telugu-LLM-Labs/telugu_alpaca_yahma_cleaned_filtered_romanized). Several `SuryaKrishna02/aya-telugu-*` sets (news, poems, recipes) are Apache-2.0. — [HF aya-telugu-news-articles](https://huggingface.co/datasets/SuryaKrishna02/aya-telugu-news-articles). `community-datasets/telugu_news` and `telugu_books` are licence "unknown". — [HF telugu_news](https://huggingface.co/datasets/community-datasets/telugu_news)

**IndiaAI / AIKosh**
- AIKosh has no blanket licence. Each contributor picks a licence from a dropdown, and users must also follow "Supplemental Terms" and AIKosh policies. — [AIKosh Terms](https://aikosh.indiaai.gov.in/home/terms-n-conditions). Artefacts can be open, registered or restricted access. — [IndiaAI EoI page](https://indiaai.gov.in/article/now-open-expression-of-interest-eoi-to-contribute-datasets-and-ai-artefacts-to-aikosh)
- In 2025 the press reported that AIKosh datasets "will not … be available for monetisation". This is press reporting, not the terms text. — [Business Standard via Magzter](https://www.magzter.com/en/stories/newspaper/Business-Standard/DATASETS-ON-AIKOSH-WILL-NOT-BE-AVAILABLE-FOR-MONETISATION)

### Inferences
- A licence-clean commercial base exists. For data: IndicCorp v2 (CC0), BPCC except Samanantar-derived parts (CC0/CC-BY-4.0), Sangraha, IndicAlign and MILU (CC-BY-4.0, attribution needed). For models: IndicTrans2 and IndicBERT v2 (MIT) and Sarvam-M/30B/105B (Apache-2.0). These are enough to fine-tune or distil a small Indic-capable proprietary model.
- Avoid Samanantar, Sarvam-1, Krutrim-2 and Swecha Chandamama in any commercial training pipeline. Treat GPL-3.0 (Sarvam-Translate) and CC-BY-SA-4.0 (IndicGenBench) as risky for proprietary derivatives. Evaluation-only use of CC-BY-SA test sets is lower risk, but that is not legal advice.
- The CC0 relabelling of Samanantar-derived text inside BPCC, and AI4Bharat's own statement that it "does not own" the underlying text, mean upstream copyright in the crawled sources is not cleared by the licence label. This is a residual risk for any web-mined corpus.

### Gaps
- Bhashini datasets/models licence terms: not researched or verified in this pass.
- Exact AIKosh per-dataset licences for Telugu/Hindi text corpora: not verified. The dataset pages need login/browsing.
- BharatGPT-3B-Indic terms are behind manual gating, so not verified.
- Licence of Telugu-LLM-Labs Navarasa models: not stated in metadata (it probably inherits Gemma terms, which is an inference).
- Samanantar CC-BY-NC vs BPCC "CC0" for the same mined pairs: the contradiction is unresolved. Ask AI4Bharat before relying on it.
- IIIT Hyderabad's official Telugu LLM/corpus release (projected for Aug 2025): I could not confirm whether it shipped or under what licence.
- I did not confirm that `mounikaiiith` is IIIT Hyderabad-affiliated. The handle suggests it, but that is an inference.

## 2. Has coding with Telugu/Hindi instructions been benchmarked? What gap vs English?

### Takeaway
Yes, and as of October 2026 it is much better covered than a year earlier. In Sept–Oct 2026, AI4Bharat and NVIDIA released Apache-2.0 Indic versions of HumanEval, MBPP and SWE-bench Verified in 14 languages, Telugu and Hindi included. Published scores for 10 open models on Indic HumanEval and MBPP are high (about 80–99.7), so function-level coding from Indic prompts is close to saturated for strong models. No Indic SWE-bench results have been published yet, and no per-language English-vs-Telugu deltas were found in public form.

### Cited Findings
- **AI4Bharat Indic-LLM-Eval-Suite (Oct 2026, with NVIDIA)** includes code benchmarks HumanEval, MBPP and SWE-bench. Translation used an LLM pipeline. Items with a judge score of 98 or more pass straight through, and lower-scoring items are corrected and re-judged. Per the pipeline description, human reviewers check 100% of failures and spot-check 20% of passes. The blog does not name the translator LLM. — [Indic-LLM-Eval-Suite blog](https://ai4bharat.github.io/indic-llm-eval-suite-blog/)
- `indic-humaneval`: 164 problems. Only the `prompt` field is translated, into 14 languages (as, bn, gu, hi, kn, ml, mr, ne, or, pa, sa, ta, te, ur), with "a portion of the translations reviewed and corrected by human annotators". `indic-mbpp`: 500 test-split problems, `text` field translated. `indic-swe-bench`: SWE-bench Verified's 500 instances, with only `problem_statement` translated; code, patches and tests are unchanged. All three are Apache-2.0. — [HF indic-humaneval](https://huggingface.co/datasets/ai4bharat/indic-humaneval); [HF indic-mbpp](https://huggingface.co/datasets/ai4bharat/indic-mbpp); [HF indic-swe-bench](https://huggingface.co/datasets/ai4bharat/indic-swe-bench)
- **Published Indic code scores** (metric labelled "strict", zero-shot, post-trained models), from the blog's results data:
  - Indic HumanEval: Nemotron-3.5-Super-120B 97.87; Nemotron-3-Super-120B 94.92; sarvam-105b-1026 97.21; Gemma-4-31B-it 99.7; Gnani-evon-v3.3-30B 80.34; Muse-Glimmer-30B (Meta) 96.49; Nemotron-3.5-Lightning-30B 85.67; Qwen3-30B 79.83; Sarvam-30b 93.34; Gemma-4-26B-A4B-it 99.19.
  - Indic MBPP: 88.43 / 85.15 / 85.12 / 85.88 / 79.85 / 80.88 / 81.9 / 79.25 / 79.25 / 85.32, in the same model order.
  - There is no SWE-bench row in the published table.
  - Source: [blog results.js](https://ai4bharat.github.io/indic-llm-eval-suite-blog/assets/js/results.js); [blog](https://ai4bharat.github.io/indic-llm-eval-suite-blog/)
- The same table shows that **Indic-language output quality** varies far more than code correctness. Indic Arena-Hard "Language quality" judge scores range from 1.4 (Nemotron-3-Super-120B) to 3.96 (Gemma-4-31B). Indic AlpacaEval "Language quality" ranges from 1.61 to 4.92. — [blog results.js](https://ai4bharat.github.io/indic-llm-eval-suite-blog/assets/js/results.js)
- AI4Bharat's qualitative statement on the English gap: "strong English performance doesn't necessarily translate to equally strong performance in Indian languages". It notes models that solve reasoning problems in English but struggle with the same task in Bengali, Kannada or Odia. — [blog](https://ai4bharat.github.io/indic-llm-eval-suite-blog/)
- **mHumanEval** (NAACL 2025) has prompts in 204 natural languages. Expert human translations cover 15 languages, **including Hindi and Telugu** (and Bangla). It evaluated GPT-4o, Claude-3.5, GPT-3.5, DeepSeek-Coder-V2, WizardCoder and Aya. Average Python pass@1 across 204 languages: GPT-4o 0.738, Claude-3.5 0.739, GPT-3.5 0.360, DeepSeek-Coder 0.229, WizardCoder 0.098, Aya 0.445. Performance generally falls for lower-resource languages. GPT-3.5 and DeepSeek drop sharply, while GPT-4o and Claude-3.5 stay consistent. — [arXiv 2410.15037](https://arxiv.org/html/2410.15037v2). The repo is Apache-2.0. — [GitHub mHumanEval](https://github.com/mraihan-gmu/mHumanEval-Benchmark)
- **mHumanEval per-language Python pass@1** (appendix tables 22–24; model order Claude-3.5 / GPT-4o / GPT-3.5 / DeepSeek-Coder-V2 / WizardCoder / Aya). This is the clearest measured English-vs-Indic gap found:
  - English (eng_Latn): 0.938 / 0.910 / 0.770 / 0.902 / 0.800 / 0.650
  - Hindi (hin_Deva): 0.854 / 0.859 / 0.600 / 0.872 / 0.480 / 0.572
  - Bangla (ben_Beng): 0.797 / 0.792 / 0.541 / 0.565 / 0.090 / 0.523
  - That is a drop of about 5–8 points for frontier models (2024 generation) going English → Hindi, and about 12–14 points English → Bangla. The drop for code-specialised small models is much larger: WizardCoder falls from 0.800 to 0.480 (Hindi) and 0.090 (Bangla), and DeepSeek-Coder from 0.902 to 0.565 (Bangla).
  - Telugu's row was not in the retrieved part of the appendix.
  - Source: [arXiv 2410.15037 appendix](https://arxiv.org/html/2410.15037v2)
- **HumanEval-XL** (80 problems × 12 programming languages × 23 natural languages = 22,080 problems). The visible part of its language list (21 of 23) has no Hindi or Telugu. — [arXiv 2402.16694](https://arxiv.org/abs/2402.16694); [GitHub FloatAI/HumanEval-XL](https://github.com/FloatAI/HumanEval-XL)
- **IndicEval-XL** (Deutsche Telekom, Feb 2025) is HumanEval-XL's English prompts translated into 6 Indic languages. Models: Gemini 1.5, Gemini 2.0 and a small LLaMA 7B. Hindi did well and Sanskrit poorly. It uses BERTScore/CodeBERTScore, **not execution-based pass@k**. — [arXiv 2502.19067](https://arxiv.org/html/2502.19067v1). The GitHub repo has no licence detected by the GitHub API. — [GitHub telekom/IndicEval-XL](https://github.com/telekom/IndicEval-XL)
- **CodeMixBench** (May 2025) is built on BigCodeBench, with 1,140 tasks. It includes Hinglish at code-mixing levels 0.6 and 0.9, and tests 1B–15B open models. Code-mixed prompts consistently reduce pass@1 compared with English. The drop grows with more mixing and is larger for smaller models. — [arXiv 2505.05063](https://arxiv.org/abs/2505.05063)
- **HinglishEval** (poster): English pass@1 is generally higher than Hinglish, "though the difference is not very pronounced". — [HinglishEval PDF](https://sahakintan.github.io/myportfolio/assets/pdf/HinglishEval.pdf) (secondary/poster, not peer-reviewed as far as I could tell)
- **Sarvam-105B English coding** (model card): LiveCodeBench v6 71.7 and SWE-bench Verified (SWE-Agent harness) 45.0. Comparators: GLM-4.5-Air 57.6, GPT-OSS-120B 50.6, Qwen3-Next-80B-A3B-Thinking 60.9. So the best Indian open model trails peers on English agentic SWE. — [HF sarvam-105b](https://huggingface.co/sarvamai/sarvam-105b)

### Inferences
- For simple, single-function Python tasks, the Indic-prompt penalty for 30B+ modern open models looks small. Indic HumanEval reaches 97–99.7 for Gemma-4 and Nemotron-3.5-Super, which is near typical English HumanEval ceilings. A product pitched as "better code from Telugu prompts" on HumanEval-style tasks would have little headroom.
- The measurable openings are probably elsewhere:
  - **(a)** Repository-level/agentic tasks with Telugu/Hindi issue text. Indic SWE-bench exists, but no results are published.
  - **(b)** Small models (≤8B), where CodeMixBench shows larger drops.
  - **(c)** Romanised/code-mixed ("Tenglish"/Hinglish) prompts, which the AI4Bharat code sets do not cover (they are native script only).
  - **(d)** The quality of Telugu/Hindi explanations, comments and docs. Judge-scored "language quality" spreads widely even when code is correct.
- The "strict" metric is not defined on the blog, and it is unclear whether scores are averaged over the 14 languages. Do not compare it directly with English pass@1 until the technical report ("coming soon") is out.

### Gaps
- No public per-language English vs Hindi vs Telugu pass@1 deltas found for current frontier models (GPT-5-class, Claude 4-class, Gemini 3-class). The only per-language deltas found are mHumanEval's 2024-generation models (English/Hindi/Bangla above). The Telugu row was not retrieved.
- No published Indic SWE-bench scores for any model.
- HumanEval-XL's language list: the last 2 of its 23 natural languages were not captured, so it is not fully confirmed that Hindi and Telugu are absent (they are absent from the 21 visible). MCEval: not verified this pass. My understanding is that it is multilingual in programming languages, not natural languages, but that is unconfirmed.
- IndicEval-XL's full list of 6 languages and whether Telugu is included: not confirmed.
- The AI4Bharat Indic code sets are labelled Apache-2.0, but upstream licences (HumanEval, MBPP, SWE-bench Verified) and the translator LLM's terms are not stated on the cards. Verify before redistributing derivatives.

## 3. Community sentiment, native-speaker evaluation without interviews, and tokenizer inflation

### Takeaway
Public evidence of developer demand for native-language coding help is thin and mostly vendor-driven (Microsoft/GitHub, Amazon demos). Non-interview evaluation is feasible by combining several checks:
- execution-based tests, since code and tests are language-neutral;
- AI4Bharat's partly human-reviewed sets, plus mHumanEval's expert Hindi/Telugu translations;
- back-translation and LLM-judge filters;
- volunteer review by open contribution, which AI4Bharat itself invites.

Telugu suffers much worse token inflation than Hindi in older and Llama-family tokenizers, though GPT-4o-era tokenizers narrowed the gap.

### Cited Findings
**Community / market signals (biased evidence)**
- At Microsoft Build 2024, Satya Nadella said developers can program in their native language, including Hindi. GitHub Copilot Workspace was demoed with Hindi and Kannada prompts. — [Analytics India Mag](https://analyticsindiamag.com/microsoft-github-copilot-now-lets-you-code-in-hindi/); [AIM Kannada](https://analyticsindiamag.com/ai-news-updates/microsoft-shows-how-to-code-in-kannada/)
- Amazon Q Developer added Hindi interaction and documentation. — [Analytics India Mag](https://analyticsindiamag.com/ai-news-updates/amazon-q-developer-now-lets-you-code-in-hindi)
- An r/developersIndia thread (May 2024), "LLMs in Indic languages and how to [develop]", exists via a mirror. I did not read its content. — [mirror link](https://lr.sudovanilla.org/r/developersIndia/comments/1cqd3bd/discussion_llms_in_indic_languages_and_how_to)
- An academic study, "Explain in Plain Language Questions with Indic Languages: Drawbacks, Affordances, and Opportunities", is a relevant lead on Indic-language code comprehension in CS education. I found it but did not read it. — [arXiv 2409.20297](https://arxiv.org/html/2409.20297v1)
- IIT Bombay's CodeVaani is a multilingual speech-driven code-understanding assistant inside Bodhitree LMS. This was reported in search-result summaries and not verified at the primary source.

**Evaluation without interviews**
- AI4Bharat's pipeline (LLM judge threshold of 98 or more, 100% human review of failures, 20% spot-check of passes) is a reusable template. The suite explicitly invites community benchmark contributions by email and GitHub. — [blog](https://ai4bharat.github.io/indic-llm-eval-suite-blog/); [GitHub indic-llm-eval-suite](https://github.com/AI4Bharat/indic-llm-eval-suite)
- `indic-swe-bench` translates only the issue text, leaving code, patches and tests unchanged. Correctness therefore stays fully execution-based and language-neutral, and no human grader is needed for pass/fail. — [HF indic-swe-bench](https://huggingface.co/datasets/ai4bharat/indic-swe-bench)
- mHumanEval provides expert (human) translations for Hindi and Telugu, usable as a human-quality reference set. — [arXiv 2410.15037](https://arxiv.org/html/2410.15037v2)
- IndicTrans2 (MIT) can do back-translation round-trip checks: Telugu → English → compare with the original English prompt. Its IN22 test sets are CC-BY-4.0. — [IndicTrans2 GitHub](https://github.com/AI4Bharat/IndicTrans2)
- Swecha's Chandamama corpus was produced by volunteer OCR plus volunteer proofreading. This is precedent that open, volunteer Telugu contribution works at scale (one report says 40,000 stories). — [Analytics India Mag](https://analyticsindiamag.com/ai-trends/an-open-source-movement-led-to-indias-first-telugu-slm)

**Tokenizer inflation**
- Normalized Sequence Length (lower is better, relative to an unnamed baseline tokenizer), Hindi / Telugu:
  - GPT-4o 0.4091 / 0.375; GPT-4 1.0 / 1.75; Llama 3.1 (405B) 0.5909 / 1.7916; SUTRA 0.4545 / 0.2916.
  - Sarvam OpenHathi 0.4545 / 2.6666; Airavata 0.4545 / 2.6666; Indic Gemma 0.5455 / 0.625.
  - Phi-3.5-MoE 1.0454 / 2.625; Aya-23-35B 1.0454 / 1.7083; Project Indus 0.3182 / 2.8333.
  - Source: [arXiv 2411.12240 Table 2](https://arxiv.org/html/2411.12240v2)
- Fertility (tokens per word) with the GPT-2 tokenizer: Hindi 7.59 and Telugu 18.76, against 1.04 and 1.87 for the BHARATI morphology-aware tokenizer. Dravidian (agglutinative) languages tokenize worse than Indo-Aryan ones. — [arXiv 2607.23319](https://arxiv.org/pdf/2607.23319) (date/ID not independently confirmed)
- Sarvam-1's model card claims fertility of 1.4–2.1 across its supported languages, "2-4x more efficient than existing multilingual models". This is a vendor claim. — [HF sarvamai/sarvam-1](https://huggingface.co/sarvamai/sarvam-1)
- IndicSuperTokenizer (Nov 2025) reports a 39.5% average fertility improvement over LLaMA4 and 18% over Sutra across 22 languages. — [arXiv 2511.03237](https://arxiv.org/abs/2511.03237v1)

### Inferences
- With Llama-3.1-family tokenizers, Telugu text costs about 3x Hindi (1.79 vs 0.59 NSL). That inflates API cost and eats context window for Telugu prompts. Llama/Qwen-derived small proprietary models would hit this. An Indic-efficient tokenizer (Sarvam, SUTRA, GPT-4o-class) or vocabulary extension matters more for Telugu than for Hindi.
- A no-interview evaluation plan is realistic: run `indic-humaneval`/`indic-mbpp`/`indic-swe-bench` (Telugu, Hindi) against English originals by execution, and add a romanised/code-mixed variant generated with IndicTrans2/Aksharantar (commercially usable licences). Then check translation fidelity by back-translation and by sampling against mHumanEval's expert translations. Finally, invite volunteer native-speaker review through a public GitHub repo, following AI4Bharat and Swecha precedent.

### Gaps
- No direct reading of r/developersIndia or other Indian developer forums on native-language coding assistance. Searches returned news, vendor demos and course listings, not substantive threads. Community demand remains unevidenced.
- No Telugu/Hindi token-inflation figures found for Claude, Gemini, Qwen3 or Gemma-4 tokenizers.
- The NSL paper does not name its baseline tokenizer, which limits absolute interpretation.
