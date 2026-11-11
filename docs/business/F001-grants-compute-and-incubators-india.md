# F001: Grants, free computing and incubators for a solo founder in India

**Date:** 11 November 2026 · **Version:** 1 · **Brief deliverable:** 18

**How this was checked:** each row was read on the programme's own page on 11 November 2026, unless the row says otherwise. Rules, amounts and dates change often, so re-read the official page before applying. Each statement carries a label, as in P001:
- ✅ **Read on the official page today.**
- 📰 **From a secondary source**, such as a news site or a grant listing. The official page couldn't be read or didn't say.
- 🔮 **My judgement.**

---

## 1. The short version

### In plain words

1. **Almost all Indian government money needs a registered company first.** The key is "DPIIT recognition", the government's official stamp that you are a startup. It is only for a Private Limited Company, an LLP or a registered partnership; a person alone can't get it ✅. Registering a company costs real money. Among other things there is a digital signature, state stamp duty, usually an accountant's fee, and yearly filings (amounts not checked here). It also creates legal duties. So that is a separate decision, and it is yours.
2. **One well-known government grant is ruled out entirely.** NIDHI-PRAYAS, which pays individuals up to ₹10 lakh to build a prototype, excludes pure software projects 📰.
3. **There is real money for a person working alone, with no company.** It comes mostly from foundations abroad that fund open research. Emergent Ventures India and the Transformative AI Fund accept individuals at any time ✅. NLnet's CodeSupply call closes on **3 January 2027** ✅, but it has a rule against AI-made work that probably excludes us (section 4).
4. **Free computing is available today, at no cost and with no company:** Kaggle and Google Colab notebooks, and Google's TPU Research Cloud for research (by application) ✅.
5. **Cloud companies' startup credits** (Amazon, Microsoft, Google, NVIDIA) mostly want a company, a website, a paid account or proof of traction. They are for later, except perhaps Amazon's smallest tier.

**My recommendation 🔮:** don't register a company yet. First, apply as an individual to Emergent Ventures India and the Transformative AI Fund. I can draft both applications; only you can send them. Use the free notebooks for any computing beyond the MacBook. Revisit registering a company when pkv has its first real users. Incorporation would then unlock DPIIT, the Seed Fund through an incubator, and the cloud credits.

### In engineering terms

The funding landscape splits on **legal form**:

- **Individuals.** Non-dilutive grants from private funders are open to them: Emergent Ventures (Mercatus Center), EA Funds' Transformative AI Fund, NLnet's EU-funded open calls. So are compute grants such as TPU Research Cloud.
- **DPIIT-recognised entities.** Almost all Government of India instruments need one: SISFS (Startup India Seed Fund Scheme) through incubators; MeitY's TIDE 2.0, GENESIS and SAMRIDH through partner organisations; the IndiaAI compute subsidy for startups; and the Section 80-IAC tax holiday. Recognition requires a Private Limited, an LLP or a registered partnership (80-IAC: Private Limited or LLP only).
- **Hyperscaler credits.** These are tiered by funding stage, and usually gated by incorporation, a website, or a paid account with a payment method.

---

## 2. Open now, with no company (₹0)

| Programme | What you get | Who can apply | Fits us? | Deadline | Strings attached | Source |
|---|---|---|---|---|---|---|
| **Emergent Ventures India** (Mercatus Center) | An equity-free grant or fellowship; the size isn't published | Individuals, 13 or older, no upper age limit 📰. Choose India in the application's "My project will affect" menu 📰 | 🔮 **Good.** It funds unusual individuals with "zero to one" projects; the October 2026 cohort included an AI research grant to a student 📰 | **Rolling**; the 20th India cohort was announced in October 2026 📰 | None stated; equity-free 📰 | [EV India, 20th cohort](https://marginalrevolution.com/marginalrevolution/2026/10/emergent-ventures-india-20th-cohort.html) (the programme's own announcement blog) |
| **Transformative AI Fund** (EA Funds; successor of the closed Long-Term Future Fund) | Typically $10k–$150k, rarely over $300k ✅ | Individuals, new organisations, and existing ones starting new projects ✅. Countries not stated | 🔮 **Medium.** Its focus is reducing catastrophic risk from advanced AI. pkv's measurements of AI coding agents skipping, weakening or editing tests are a case of *overseeing AI agents*. That pitch is honest only if we frame it as oversight research, not as a product | **Rolling**: "always open to applications" ✅ | Usually a public grant report 🔮 | [funds.effectivealtruism.org/funds/transformative-ai](https://funds.effectivealtruism.org/funds/transformative-ai) |
| **NLnet: CodeSupply fund** (EU Horizon Europe) | €5,000–€50,000 for a first grant; €400,000 call budget ✅ | "Independent researchers, developers, and organisations" ✅. Non-EU applicants must explain the project's "European dimension" ✅ | 🔮 **Weak, and probably blocked.** The theme is software supply-chain metadata. pkv's receipts could be pitched as verifiable metadata about how a change was checked, but the rule "proposals and projects should be made by humans, not AI" ✅ very likely excludes a project built with an AI assistant, as ours is | **3 January 2027, 12:00 CET** ✅ | Results must be open source ✅ | [nlnet.nl/codesupply](https://nlnet.nl/codesupply/), [nlnet.nl/propose](https://nlnet.nl/propose/) |
| **GitHub Sponsors** | Monthly support from people or companies. **No fee** on sponsorships from personal accounts; up to 6% from organisations ✅ | Anyone who contributes to open source and lives in a supported region; **India is supported** ✅ | 🔮 **Fine to set up; little money** until pkv has users | Any time | GitHub Sponsors terms ✅ | [GitHub Docs: About GitHub Sponsors](https://docs.github.com/en/sponsors/getting-started-with-github-sponsors/about-github-sponsors) |
| **TPU Research Cloud** (Google) | Cloud TPUs (Google's AI chips) **at no charge**, for limited periods ✅. Other cloud services, such as storage, are billed 📰 | "Researchers"; the page lists no country, academic or company rule ✅ | 🔮 **Useful later**, for the guidance experiment's neural guesser, if the MacBook isn't enough. Works with JAX, PyTorch, TensorFlow and Julia ✅ | By "express interest" form ✅ | Share the research publicly (we do anyway); give Google feedback; follow Google's AI principles ✅ | [sites.research.google/trc/about](https://sites.research.google/trc/about/) |
| **Kaggle and Google Colab notebooks** | Free GPU time in the browser. Kaggle is commonly reported at about 30 GPU-hours a week; your own quota shows in your account settings 📰 | Anyone with an account | 🔮 **Yes**, for small training runs | — | Session time limits 📰 | [Kaggle](https://www.kaggle.com/), [Colab](https://colab.research.google.com/) |

**Not now:**
- **GitHub Secure Open Source Fund.** $10,000 a project, rolling ✅. It requires "demonstrated community traction and adoption", which pkv doesn't have yet, and **selected applicants have a virtual interview** ✅. [Page](https://github.com/open-source/github-secure-open-source-fund).
- **Coefficient Giving** (formerly Open Philanthropy), technical AI safety request for proposals. Reported as rolling 📰, but its page refused our reader (HTTP 403), so the eligibility of individuals is unverified.

## 3. Needs a registered company first

| Programme | What you get | Key conditions | Status today | Source |
|---|---|---|---|---|
| **DPIIT startup recognition** | The gateway to the schemes below; the 80-IAC tax holiday (3 years out of the first 10) ✅ | Private Limited, LLP, partnership or cooperative ✅. A One Person Company is reported to qualify 📰. Up to 10 years old (20 for deep tech); turnover under ₹200 crore ✅ | **No fee** for recognition ✅; registering the company itself costs money | [startupindia.gov.in recognition page](https://www.startupindia.gov.in/content/sih/en/startupgov/startup_recognition_page.html) |
| **Startup India Seed Fund Scheme** | Up to ₹20 lakh grant and ₹50 lakh debt, through a selected incubator 📰 | DPIIT recognition, applied for through an incubator 📰 | **Unclear.** The official page didn't load for our reader, and secondary sources disagree on whether the scheme was extended beyond 15 May 2026 📰 | [seedfund.startupindia.gov.in](https://seedfund.startupindia.gov.in/) |
| **MeitY TIDE 2.0, GENESIS, SAMRIDH** | Grants through incubators (TIDE 2.0, up to about ₹7 lakh at some centres 📰); SAMRIDH is an accelerator with matching investment for revenue-stage startups 📰 | Through partner incubators and accelerators | No open call confirmed 📰 | listings via [startupgrantsindia.com](https://www.startupgrantsindia.com/providers/ministry-of-electronics-and-information-technology) |
| **IndiaAI Compute Portal** | Subsidised GPUs: about 38,000 listed; prices reported from about ₹65 per GPU-hour; a subsidy of up to 40% after approval 📰 | Categories include researchers, students, startups and MSMEs. Researchers are reportedly fast-tracked with an h-index of 5 or 150 citations, which we don't have 📰. Sign-in with DigiLocker, e-Pramaan or Jan Parichay 📰 | Operating 📰. Reports say researchers received under 1% of the subsidy so far 📰 | [compute.indiaai.gov.in](https://compute.indiaai.gov.in/), [ThePrint analysis](https://theprint.in/tech/indiaai-mission-9-model-builders-get-rs-1058-cr-of-govts-compute-subsidy-researchers-only-rs-10-cr/3076401/) |
| **AWS Activate Founders** | $1,000 in credits, up to $5,000 for some ✅ | Pre-Series B, founded in the last 10 years, an AWS account on a **paid plan** (needs a payment card) ✅ | Open ✅ | [aws.amazon.com/startups/credits](https://aws.amazon.com/startups/credits) |
| **Microsoft for Startups** | Credits after approval; up to $5,000 through "business verification", and up to $150,000 over time with Azure usage ✅ | "Early-stage startups building software products" ✅; the page doesn't state a company rule | Open ✅ | [microsoft.com/startups](https://www.microsoft.com/en-us/startups) |
| **NVIDIA Inception** | Free membership; partner cloud credits, GPU discounts, free courses ✅ | Must be incorporated, employ at least one developer, have a working website, and be under 10 years old ✅ | Open ✅ | [nvidia.com/en-in/startups](https://www.nvidia.com/en-in/startups/) |
| **Google for Startups Accelerator: India** | Equity-free; mentoring; cloud credits, subject to review ✅ | AI-first startups, ideally Seed to Series A, with traction ✅ | **Closed** (deadline was 19 April 2026); a form to register interest in future programmes ✅ | [startup.google.com](https://startup.google.com/programs/accelerator/india/) |

**Ruled out:**
- **NIDHI-PRAYAS** (DST). Up to ₹10 lakh for individual innovators to build a first prototype, but "pure software, e-commerce, service, and app-based projects cannot be supported" 📰 (wording repeated by several PRAYAS centres).

## 4. Fit with the founder's rules

| Rule | Where it bites |
|---|---|
| **No interviews (D-002)** | The rule is about interviewing users and customers. Some funders interview *applicants*: the GitHub Secure Open Source Fund does ✅, and others may ask for a call. Whether a funder's call is acceptable is **your decision**; I haven't assumed either way. |
| **Honesty about AI help** | This project is built with an AI assistant. Every application must say so plainly. NLnet asks for work "made by humans, not AI" ✅, so applying there would mean either disclosing and probably being refused, or hiding it. Hiding it is not acceptable, so the CodeSupply call is likely a no. Its generative-AI policy page didn't load for us, so read it before deciding. |
| **₹0** | Everything in section 2 costs nothing. Section 3 starts with the cost of registering a company. |
| **Sending things in your name** | I can draft applications. You read and submit them, and only you can accept a programme's terms. |

## 5. Suggested order 🔮

1. **Now (no cost, no company):** draft the **Emergent Ventures India** application. It is about one solo founder, ₹0, open research, and a product with public, honest benchmarks.
2. **Next:** draft a **Transformative AI Fund** application, framed as research on detecting AI coding agents that weaken or skip tests. Its evidence would be BENCH-001 to 003 and REAL-001, with the known misses stated.
3. **When the guidance experiment needs more than the MacBook:** use Kaggle or Colab first, then the TPU Research Cloud form.
4. **When pkv has real users:** a GitHub Sponsors profile (an account setting, your step); then decide whether to register a company (OPC or Private Limited). That unlocks DPIIT, the Seed Fund through an incubator, cloud credits and NVIDIA Inception.
5. **Re-read this table every three months.** Deadlines and rules change; NLnet's current call, for example, runs for two months.

## 6. What this document can't tell you

- **Whether we'll win anything.** pkv has no users yet, and most funders weigh traction or track record. The research results are honest but modest.
- **Exact company registration costs and duties.** These vary by state and change; ask an accountant before deciding.
- **The official wording** for SISFS, the IndiaAI portal and Coefficient Giving. Those pages couldn't be read today; the rows say so.
