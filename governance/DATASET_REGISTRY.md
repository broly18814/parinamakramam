# Dataset registry: what we may train on, and why

**Plan v2, Track C, step C2** (brief §16). Every dataset the project trains or evaluates on is listed here **before** it's used. Each entry gives its licence, what we owe in return, and the exact version. A dataset not on this page may not be used.

**Status:** second draft, 12 November 2026, widened at the founder's request ("don't only pick FineWeb-Edu, IndicCorp v2, Sangraha and The Stack v1; pick others too"). Nothing is downloaded yet.
- **Where the licences come from:** each dataset's Hugging Face record (`cardData.license`, the gating flag and the current commit, read through the public API on 12 November 2026), or its README where the record has no licence field. Earlier licence reading is in R002 ([training notes](../docs/research/R002-fresh-plan/notes/small_model_training_mac.md), [Indic notes](../docs/research/R002-fresh-plan/notes/indic_languages_coding.md)).
- **The "commit" column** is the dataset's version on 12 November 2026. The exact commit and SHA-256 fingerprints are fixed in a manifest when files are downloaded.

## In plain words

**Two things make training data good.**
1. **Quality:** clean, informative, deduplicated text. Most sources below are already *quality-filtered*: a classifier kept only pages that read like teaching material, or only the best-scoring documents.
2. **Lawfulness:** a licence that allows a business to use the trained model. Using text we're not allowed to use can make the model itself unusable.

**How much we actually need is small.** By the C1 measurements, the largest run this Mac can do in a few days, 125M parameters, sees about 2.5 billion tokens. Our datasets total trillions. So the job is to *choose the best few billion tokens*, not to collect more. Every source is downloaded only as a sample.

Each dataset gets one of three marks:
- **Use:** licence allows commercial use; we owe at most credit.
- **Use with conditions:** allowed, but with a condition we must meet, written next to it (share-alike, another company's model wrote it, or per-file licences).
- **Excluded:** not used, even for research, so it can never contaminate a model we later sell.

## 1. English: general text

| Dataset | Why it's good | Licence | Mark | Commit |
|---|---|---|---|---|
| **FineWeb-Edu** (`HuggingFaceFW/fineweb-edu`) | Web pages a classifier scored as educational; the strongest small-model result in R002 | ODC-By | Use | `87f09149ef47` |
| **DCLM-Baseline** (`mlfoundations/dclm-baseline-1.0`) | Web text selected by a trained quality filter; a strong recipe at small scale | CC-BY-4.0 | Use | `a3b142c183ae` |
| **FineWeb** (`HuggingFaceFW/fineweb`) | The large deduplicated web set FineWeb-Edu came from; for broader coverage | ODC-By | Use | `9bb295ddab0e` |
| **FinePDFs** (`HuggingFaceFW/finepdfs`) | Text from PDFs (reports, papers, manuals): longer, denser documents than web pages | ODC-By | Use | `220bac3acbf0` |
| **Dolma / OLMo mix** (`allenai/dolma`, `allenai/olmo-mix-1124`, `allenai/dolmino-mix-1124`) | AI2's fully documented open training mixes, including a high-quality "mid-training" mix | ODC-By (per-source terms apply) | Use with conditions: read each subset's source terms before using that subset | `7f48140530a0`, `99ee6aaace88`, `a319f19eef1e` |
| **Common Corpus** (`PleIAs/common_corpus`) | Only public-domain or openly licensed text, each document tagged with its licence; books, newspapers, government, science, code | per document (public domain, CC0, CC-BY, MIT, …) | Use with conditions: keep only documents whose own `license` tag allows commercial use | `307910e4c5d0` |
| **Common Pile / Comma training set** (`common-pile/comma_v0.1_training_dataset`) | "Public domain and openly licensed text" (its own words), 8 TB raw: Gutenberg, pre-1929 books, USPTO, PubMed, Stack Exchange, arXiv | per source; no single field on the record | Use with conditions: per-source licences to be read from its paper; its `stackv2_*` parts fall under the Stack v2 exclusion below | `5afc546db324` |
| **Wikipedia** (`wikimedia/wikipedia`, English) | Clean encyclopaedic text | CC-BY-SA-3.0 and GFDL | Use with conditions: share-alike. Whether a trained model counts as an adaptation is legally unsettled; credit Wikipedia, and never ship Wikipedia text verbatim | `b04c8d1ceb2f` |
| **C4** (`allenai/c4`) | Older cleaned web text; a standard baseline | ODC-By | Use (baseline only) | `1588ec454efa` |

## 2. Maths and science (reasoning-dense text)

| Dataset | Why it's good | Licence | Mark | Commit |
|---|---|---|---|---|
| **FineMath** (`HuggingFaceTB/finemath`) | Maths pages selected by a quality classifier | ODC-By | Use | `e92b25a61673` |
| **OpenWebMath** (`open-web-math/open-web-math`) | Maths web pages with formulas kept | ODC-By, plus Common Crawl's terms (its own README) | Use | `fde8ef8de230` |
| **peS2o** (`allenai/peS2o`) | Open-access scientific papers | ODC-By | Use | `636a503e44a3` |
| **Proof-Pile-2** (`EleutherAI/proof-pile-2`) | Maths papers, formal proofs, maths code | "We do not alter the license of any of the underlying data": per source | Use with conditions: only the parts whose own licence is read and allows it | `901a9273a770` |

## 3. Code

| Dataset | Why it's good | Licence | Mark | Commit |
|---|---|---|---|---|
| **The Stack v1 dedup** (`bigcode/the-stack-dedup`, Python first) | Permissively licensed GitHub code, deduplicated; StarCoder's base | per file, BigCode Terms of Use | Use with conditions: keep each file's licence and repo for attribution; honour opt-outs; restrict to MIT, BSD, Apache-2.0, ISC, Unlicense and CC0. **Terms must be accepted on Hugging Face: a founder step** | `17cad72c886a` |
| **StarCoderData** (`bigcode/starcoderdata`) | The Stack v1 plus GitHub issues, Jupyter notebooks and commits, cleaned | as The Stack v1 | Use with conditions: as above; issues and commits are user-written text with weaker provenance, so they're used only after a check | `9fc30b578ced` |
| **OpenCoder file corpus** (`OpenCoder-LLM/opc-fineweb-code-corpus`) | Code-related web pages recalled from FineWeb | MIT | Use | `9e8e48e666c2` |
| **OpenCoder annealing corpus** (`OpenCoder-LLM/opc-annealing-corpus`) | High-quality code and synthetic code-textbook data used in OpenCoder's final training stage | ODC-By | Use with conditions: which model wrote the synthetic part, and that model's terms, are read first | `078e4bc1d397` |
| **GitHub-code-clean** (`codeparrot/github-code-clean`) | A big multi-language code set with a per-file licence column | Apache-2.0 packaging; per-file licences include GPL | Use with conditions: **drop GPL, AGPL and LGPL rows**; keep permissive only | `c48d40f9e70f` |

## 4. Code *changes*: the data closest to the product

These teach how code is *changed*, and how changes are checked. That's exactly what pkv and the brief's Stage 2–3 are about.

| Dataset | Why it's good | Licence | Mark | Commit |
|---|---|---|---|---|
| **CommitPackFT** (`bigcode/commitpackft`) | About 700,000 filtered commits: a commit message and the code before and after; high quality, many languages | MIT (dataset); code from permissively licensed repos | Use | `fc56fe33c030` |
| **CommitPack** (`bigcode/commitpack`) | The full 4 TB of permissively licensed commits CommitPackFT came from | MIT | Use (samples only) | `5eee2c845bf8` |
| **SWE-Gym** (`SWE-Gym/SWE-Gym`) | Real GitHub issues with executable environments and tests, made for training agents | MIT | Use | `bb94ed9e39bb` |
| **SWE-rebench** (`nebius/SWE-rebench`) | A continually refreshed set of real issue-fixing tasks with tests | CC-BY-4.0 | Use | `89cdfbab4ab1` |
| **SWE-bench** (`princeton-nlp/SWE-bench`) | The standard real-repository benchmark | MIT (its GitHub licence); the patches keep their repos' licences | **Evaluation only**, never trained on | `e48e2bd1e9fe` |

## 5. Instructions and reasoning (for later fine-tuning, not pre-training)

| Dataset | Why it's good | Licence | Mark | Commit |
|---|---|---|---|---|
| **OpenCodeReasoning** (`nvidia/OpenCodeReasoning`) | Step-by-step solutions to programming problems | CC-BY-4.0 | Use with conditions: written by another model; its terms are read first | `20a1ca19c0d0` |
| **OpenCodeInstruct** (`nvidia/OpenCodeInstruct`) | Millions of coding instructions with tests | CC-BY-4.0 | Use with conditions: as above | `8f3ba5bafe4d` |
| **OpenCoder SFT** (`OpenCoder-LLM/opc-sft-stage2`) | Curated coding instructions | MIT | Use with conditions: as above | `7d28f40d579e` |
| **Self-OSS-Instruct** (`bigcode/self-oss-instruct-sc2-exec-filter-50k`) | Instructions written by StarCoder2, kept only if the code ran | ODC-By | Use with conditions: StarCoder2's OpenRAIL-M use restrictions are read first | `356bb069eee8` |
| **Tülu 3 SFT mix** (`allenai/tulu-3-sft-mixture`) | AI2's open general instruction mix | ODC-By (subsets carry their own terms) | Use with conditions: per subset | `b14afda60f1b` |
| **IndicAlign** (`ai4bharat/indic-align`) | Instructions in 15 Indian languages, Telugu and Hindi included | CC-BY-4.0 | Use | `032b6a9070e7` |
| **Samvaad Hindi** (`sarvamai/samvaad-hi-v1`) | Hindi conversations | Apache-2.0 | Use with conditions: which model wrote it is read first | `6439910cc994` |

## 6. Telugu and Hindi text

| Dataset | Why it's good | Licence | Mark | Commit |
|---|---|---|---|---|
| **IndicCorp v2** (`ai4bharat/IndicCorpV2`) | AI4Bharat's large cleaned Indic news and web corpus | CC0 by its README's blanket statement; **no licence field on the record** | Use (README statement recorded) | `2d7285e6ce14` |
| **Sangraha** (`ai4bharat/sangraha`, *verified* split) | Indic pre-training data checked by humans | CC-BY-4.0 | Use; the *synthetic* split only after its generation terms are read | `8b813c3f62d3` |
| **FineWeb-2** (`HuggingFaceFW/fineweb-2`: `tel_Telu`, `hin_Deva`, and the romanised `tel_Latn`, `hin_Latn`) | FineWeb's cleaning, applied per language. The romanised parts cover Tenglish and Hinglish, which matter for IND-1 | ODC-By | Use | `af9c13333eb9` |
| **HPLT 2.0 cleaned** (`HPLT/HPLT2.0_cleaned`: `tel_Telu`, `hin_Deva`) | A large European cleaned web crawl, with separate Telugu and Hindi parts | CC0 packaging; users must comply with copyright and data-protection law (its terms) | Use with conditions: as its terms say | `d1324a5283f7` |
| **MADLAD-400** (`allenai/MADLAD-400`) | Google's audited 400-language web set; Telugu and Hindi are among its languages | ODC-By | Use | `9d886a76bd8f` |
| **Wikipedia** (Telugu `te`, Hindi `hi`) | Clean encyclopaedic text | CC-BY-SA-3.0 and GFDL | Use with conditions: as English Wikipedia above | `b04c8d1ceb2f` |
| **BPCC**, except its "existing mined corpora" part (`ai4bharat/BPCC`) | English↔Indic sentence pairs, partly translated by humans | CC0 for most parts, with a split licence (R002) | Use with conditions: only the parts R002 lists as CC0 or CC-BY; **gated, terms accepted by the founder** | `5bde309374f2` |
| **Aksharantar** (`ai4bharat/Aksharantar`) | Word-level transliteration between Indic scripts and Latin letters | CC-BY (manual parts), CC0 (mined parts) | Use | `e418c1fc928d` |
| **CulturaX** (`uonlp/CulturaX`) | Cleaned mC4 and OSCAR text, 167 languages | gated; **licence not readable without accepting terms** | Not yet: unverified | `6a8734bc69fe` |

## 7. Evaluation only (never trained on)

| Dataset | Used for | Licence | Commit |
|---|---|---|---|
| **indic-swe-bench** | IND-1 | Apache-2.0 (per R002) | pinned on download |
| **SWE-bench** | real-repository tasks | MIT | `e48e2bd1e9fe` |
| **HumanEval** (`openai/openai_humaneval`) | small code models | MIT | `7dce6050a7d6` |
| **MBPP** (`google-research-datasets/mbpp`) | small code models | CC-BY-4.0 | `4bb6404fdc6c` |
| **APPS** (`codeparrot/apps`) | harder programming problems | MIT | `21e74ddf8de1` |
| **MILU** (`ai4bharat/MILU`) | Indic knowledge, Telugu and Hindi | CC-BY-4.0, gated (auto) | `846d7016558b` |
| **FLORES+** (`openlanguagedata/flores_plus`) | translation and bits-per-byte across languages on parallel text (EXP-M1) | CC-BY-SA-4.0, gated (auto) | `1147e2dc59f3` |

## Excluded

| Dataset | Why |
|---|---|
| **Samanantar** | CC-BY-NC-4.0: no commercial use. |
| **BPCC's "existing mined corpora" part** | It repackages Samanantar under CC0, which conflicts with Samanantar's own non-commercial licence. |
| **The Stack v2**, **Stack-Edu**, **Python-Edu**, and the `stackv2_*` parts of the Comma set | Bulk access needs a Software Heritage/INRIA agreement. Their training principles expect an openly licensed model with its files published by identifier, which doesn't fit a model we might keep closed. Reconsidered if we decide to release a model openly. |
| **IndicSentenceSummarization** | CC-BY-NC-4.0: no commercial use. |
| **Swecha "Chandamama Kathalu"** | CC-BY-NC-SA-4.0: no commercial use. |
| **Cosmopedia**, **TinyStories** | Written by other companies' models, under terms that may restrict training competing models; TinyStories is also share-alike (CDLA-Sharing). Research-only at most, so not used. |
| **NVIDIA Nemotron-CC v2**, **Nemotron pretraining code**, **Nemotron-CC-Math**, **Nemotron Indic** | Gated under NVIDIA's own agreements (`other`); not read in full. |

## How quality is ensured (beyond the source's own filtering)

1. **Deduplicate across sources:** near-duplicate removal over the combined mix, because FineWeb, FineWeb-Edu and DCLM overlap.
2. **Decontaminate:** remove any document overlapping an evaluation set in section 7, before training.
3. **Language check:** Telugu and Hindi documents are re-checked with a language identifier, and the script share is reported.
4. **Mixture chosen by measurement, not taste:** EXP-M1's calibration compares candidate mixes on small models (DataDecide-style ranking at 10M–50M), and picks by bits per byte on held-out text from each language.

## Rules

1. **Before the first download**, re-read the licence on the dataset's own page and note the date. If it differs from this page, stop and log a decision.
2. **Pin the exact version:** the Hugging Face commit, plus a SHA-256 of every downloaded file, in a manifest committed beside the experiment.
3. **Keep provenance:** for code, keep each file's repo and licence, so an attribution file can be generated.
4. **Evaluation sets never enter training data** (quality rule 2).
5. **"Use with conditions" means the condition is met first.** Each condition is recorded as met (with the date) in the manifest before the data is used in a published result.
6. **Gated datasets** (The Stack v1, StarCoderData, BPCC, MILU, FLORES+) need their terms accepted on Hugging Face. **That's the founder's step**: accepting terms is an agreement.
