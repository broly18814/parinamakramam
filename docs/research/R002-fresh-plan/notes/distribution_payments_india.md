# Distribution channels and payment and legal rails for a solo Indian developer-tool founder selling globally (as of 12 Nov 2026)

Source labels used throughout: **[OFFICIAL]** means the provider's or government's own page. **[BLOG]** means a third party, often a competitor with a commercial interest (Skydo, Xflow, Winvesta, Dodo's own blog about rivals, and so on). **[ACADEMIC]** means a preprint. **[CA]** marks a point a chartered accountant must confirm before the founder acts on it.

---

## 1. Launch and distribution channels for a free open-source developer tool

### Takeaway
The channels are free to use, but nearly all of them need the founder's own account and their own human-written post. Show HN, Reddit, Product Hunt and awesome-list pull requests all forbid or penalise vote-soliciting, and some forbid AI-generated or automated content. Package publishing (VS Code Marketplace, Open VSX, PyPI) can and should be automated from CI. The best quantitative evidence (one preprint) puts a typical Hacker News launch at roughly 100 to 300 GitHub stars in the first week. The median is far lower, and the "Show HN" label itself gave no measurable lift.

### Cited Findings

**Hacker News (Show HN)**
- [OFFICIAL] What qualifies: "something you've made that other people can play with". It should be non-trivial, built by the poster, and the poster should be available to discuss it. It should be easy to try "without signups or emails". — [HN Show HN guidelines](https://news.ycombinator.com/showhn.html)
- [OFFICIAL] Not allowed as Show HN: blog posts, sign-up pages, newsletters, lists, landing pages, fundraisers, routine version updates, and "quickly generated one-offs". The guidelines note "anybody can do that now". — [HN Show HN guidelines](https://news.ycombinator.com/showhn.html)
- [OFFICIAL] Asking friends to upvote or comment is "not ok". Every Show HN goes to the /shownew page, and only moves to /show after clearing a small points threshold. Posters are advised to "explain how and why." — [HN Show HN guidelines](https://news.ycombinator.com/showhn.html)
- [ACADEMIC] A study of 138 HN-to-GitHub launches of AI/LLM tools (2024 to 2025) measured the average stars gained after HN exposure: 121 at 24 hours, 189 at 48 hours and 289 at 7 days. The median is "much lower" than the mean, so a few viral posts skew it. — [arXiv 2511.04453](https://arxiv.org/html/2511.04453v1)
- [ACADEMIC] Same study: Show HN posts gained 119 *fewer* stars at 48 hours than other posts (β = -119.2, p = 0.39), which is not significant. The authors attribute this to selection bias, since Show HN posts are often early solo projects. HN score was the strongest predictor of stars. Posting at 12:00 to 17:00 UTC was associated with about 200 more stars (unadjusted), and weekend versus weekday made no difference (p = 0.81). The design is observational and the sample is small and limited to AI tools. — [arXiv 2511.04453](https://arxiv.org/html/2511.04453v1)
- [OFFICIAL, company blog] PostHog's own HN launch write-up: they aimed for 500 stars and passed 800 five days later. Doing well on HN got them onto the GitHub Trending main page, which brought more users. — [PostHog, "After the HN launch"](https://posthog.com/blog/after-the-hn-launch)
- [BLOG] A counter-example: a solo developer's open-source desktop agent had 21 stars one month after launch, with most of the growth in week one. — [dev.to, "One month of launching a solo open-source desktop agent"](https://dev.to/openpilot/one-month-of-launching-a-solo-open-source-desktop-agent-the-real-numbers-1g9a)
- [BLOG, unverified] A repository built on 188k Show HN posts claims the median Show HN scores 2 points and that 50 points is the top 6%. I could not verify this. — [karix-ai/launch-skills](https://github.com/karix-ai/launch-skills)

**VS Code Marketplace and Open VSX**
- [OFFICIAL] VS Code Marketplace publishing setup:
  - You need a publisher ID, which "cannot be changed once created", plus a Microsoft account and the `vsce` CLI.
  - **Global Personal Access Tokens are retired on 1 December 2026.** Microsoft recommends federated identity instead: GitHub Actions Trusted Publishing (`vsce publish --oidc`) or Azure Pipelines. Trusted Publishing isn't supported on other CI providers.
  - Restrictions: no user-provided SVGs, the icon must be a PNG of at least 128×128, and README images must use HTTPS.

  — [VS Code: Publishing Extensions](https://code.visualstudio.com/api/working-with-extensions/publishing-extension)
- [OFFICIAL] The "verified publisher" badge needs a domain registered for at least 6 months, extensions on the Marketplace for at least 6 months, and a DNS TXT record. Review takes up to 5 business days. — [VS Code: Publishing Extensions](https://code.visualstudio.com/api/working-with-extensions/publishing-extension)
- [OFFICIAL] Open VSX setup, in order:
  1. Create an Eclipse account using the same GitHub account you use on open-vsx.org.
  2. Accept the Publisher Agreement.
  3. Create an access token.
  4. Create the namespace (`npx ovsx create-namespace`). Creating it does **not** make you the verified owner; you must claim ownership separately.
  5. Publish with `npx ovsx publish`. The HaaLeo/publish-vscode-extension GitHub Action can automate this.

  — [Open VSX wiki: Publishing Extensions](https://github.com/eclipse/openvsx/wiki/Publishing-Extensions)

**PyPI**
- [OFFICIAL] PyPI Trusted Publishing uses OIDC. A CI provider such as GitHub Actions swaps a short-lived identity token for a project-scoped upload token that expires after 15 minutes. This "eliminates the need to use manually generated API tokens." The only manual step is configuring the trusted publisher on PyPI once. — [PyPI Docs: Trusted Publishers](https://docs.pypi.org/trusted-publishers/)

**GitHub Marketplace**
- [OFFICIAL] Anyone can list a free app. Only apps owned by an **organization** can sell, and paid plans need publisher verification plus a "financial onboarding process". — [GitHub Docs: About GitHub Marketplace for apps](https://docs.github.com/en/apps/github-marketplace/github-marketplace-overview/about-github-marketplace-for-apps)
- [OFFICIAL] A paid listing needs at least 100 installations for a GitHub App (200 users for an OAuth app). The owner must be a verified-publisher organization, and the app must support both monthly and annual billing and handle purchase, upgrade, downgrade, cancellation and free-trial events. — [GitHub Docs: Requirements for listing an app](https://docs.github.com/en/apps/github-marketplace/creating-apps-for-github-marketplace/requirements-for-listing-an-app)

**Reddit**
- [BLOG/mirror] r/Python reduced its showcase flairs to a single "Showcase" flair in 2024, banned Medium.com links, and runs a recurring Showcase thread. These come from mirrored moderator posts, not the live sidebar. — [r/Python community updates (mirror)](https://redlib.hbubli.cc/r/Python/comments/1ak0ysc/rpython_community_updates/kpcdr63/?context=3); [r/Python Showcase thread, Jun 2026 (mirror)](https://redlib.groet-infra.nl/r/Python/comments/1tws1w7/showcase_thread/)
- [BLOG/mirror] r/devops runs a weekly self-promotion thread posted by AutoModerator. — [r/devops mirror](https://r.datuan.dev/r/devops)
- [BLOG/mirror] r/programming revised its rules in May 2024 to cut "low quality blogspam". A third-party 2026 guide says self-promotion is allowed on Saturdays only, which I could not verify. — [r/programming "State of the subreddit", May 2024 (mirror)](https://redlib.hbubli.cc/r/programming/comments/1chs4ib/the_state_of_the_subreddit_may_2024); [teract.ai guide](https://www.teract.ai/resources/reddit-marketing-developer-tools-2026)
- reddit.com itself could not be fetched, so the site-wide self-promotion policy could not be quoted (see Gaps).

**Product Hunt**
- [BLOG, self-reported] Developer-tool results from founders' own write-ups:
  - Kilo Code: 681 points, 278 comments, #1 Product of the Day.
  - Jolt AI: 473 points, #3 of the Day.
  - Bucket DX: 297 points.
  - dyrector.io (open source): about 260 upvotes, 6th place.
  - A small open-source project went from 0 to 168 GitHub stars around its launch.

  — [Kilo Code](https://www.producthunt.com/p/kilocode/how-kilo-code-didn-t-launch-on-product-hunt); [Jolt AI](https://www.producthunt.com/p/jolt-ai/how-jolt-ai-launched); [Bucket DX](https://www.producthunt.com/p/bucket/bucket-dx-24-hours-on-product-hunt); [dyrector.io](https://dev.to/dyrectorio/product-hunt-is-for-the-cool-kids-10l4); [dev.to zero-budget launch](https://dev.to/rahil_pirani_c48446facc8c/i-launched-an-open-source-tool-on-product-hunt-with-no-budget-no-team-and-no-audience-heres-57c3)
- [BLOG] A failure case: "4 weeks, 1 SaaS, 3 upvotes". — [dev.to honest Product Hunt postmortem](https://dev.to/ykiki/4-weeks-1-saas-3-upvotes-an-honest-product-hunt-postmortem-53h6)

**Awesome lists**
- [OFFICIAL, sindresorhus/awesome] These rules cover adding a whole *list* to the meta "awesome" index. Individual topic lists set their own rules.
  - The list must be at least 30 days old.
  - "Fully AI-generated pull requests are not accepted", and the list must not be AI-generated.
  - Contributors must review at least 4 other open pull requests first.
  - Lists must hold only maintained, documented items.

  — [awesome PR template](https://github.com/sindresorhus/awesome/blob/main/pull_request_template.md)

### Inferences
- **What needs the founder's own account and hand-written post (cannot ethically be automated):**
  - Show HN: the founder must be "available to discuss", and vote rings are banned.
  - Reddit showcase and self-promo threads.
  - Product Hunt.
  - Awesome-list pull requests: AI-generated PRs are banned and 4 human reviews are required first.
  - dev.to articles.

  An AI agent can draft text, but the founder must edit it, post it and answer comments personally. Automated cross-posting to these communities risks bans.
- **What can be automated in CI:**
  - VS Code Marketplace publishing via GitHub OIDC Trusted Publishing. This becomes effectively mandatory after the 1 Dec 2026 PAT retirement.
  - Open VSX publishing via token and a GitHub Action.
  - PyPI releases (see Gaps for official confirmation).
  - GitHub Releases and changelogs.
- **Install counts as signals:** Marketplace installs and GitHub stars are public, self-service validation signals that need no interviews. HN score predicts stars, and stars predict Trending, which compounds. GitHub Marketplace *paid* selling needs 100 installs and an organization, so it is a later-stage option, not day 1.
- **Reasonable launch expectation:** One well-received HN post is worth a few hundred stars, while a median post gets close to nothing. Plan several "launch-worthy" milestones (major overhauls qualify for Show HN; routine releases do not) instead of one big launch.
- **Verified publisher timing:** Register the product domain early. The 6-month domain-age clock for the VS Code verified badge starts at registration.

### Gaps
- The Reddit site-wide self-promotion policy and the live sidebar rules for r/Python, r/programming and r/devops could not be fetched (reddit.com blocked). Only mirrors and third-party summaries were found, so the founder should read each sidebar before posting.
- No official Product Hunt rules page was fetched, so its policy on asking for upvotes and on automated or AI posting is unconfirmed.
- I found no official sources on dev.to posting rules or on how Marketplace and PyPI search ranking works. PyPI Trusted Publishing is now confirmed (see above), but the PyPI page names only GitHub Actions as an example provider and gives no full list.
- The GitHub Marketplace revenue share and payout terms (in the Developer Agreement) were not retrieved.
- I found no dataset on what share of Marketplace installs or stars convert to paying users for developer tools.
- I did not confirm whether the VS Code Marketplace supports paid extensions. My understanding is that it does not, so monetisation must happen outside the Marketplace, but this is unverified.

---

## 2. Payment providers: who lets an Indian individual or new entity sell subscriptions abroad

### Takeaway
For an Indian solo founder in Nov 2026, merchant-of-record (MoR) platforms are the only realistic path that needs no entity on day 1. Paddle, Polar, Dodo, Gumroad and Lemon Squeezy all become the legal seller and pay out to India, at about 4 to 10% plus payout fees. Direct processors are harder:
- **Stripe India** is invite-only and excludes individuals; it needs a sole proprietorship, LLP or company.
- **Razorpay** card acceptance from abroad needs a registered business; individuals are pushed to PayPal.
- **PayPal India** accepts individuals but costs about 4.4% plus a fixed fee plus an FX spread.

### Cited Findings

**Stripe India (direct processor, not MoR)**
- [OFFICIAL] "Stripe is available by invite only in India… businesses from India can't sign up for a new Stripe account through our website, and must request an invite." It supports "a select number of businesses, with a focus on international expansion." — [Stripe Docs: Accept international payments from India](https://docs.stripe.com/india-accept-international-payments)
- [OFFICIAL] Export charges require:
  - A registered Indian business (sole proprietorship, LLP or company). The account "can't be an individual."
  - An Importer Exporter Code (IEC), which is optional for services unless the merchant accepts AMEX or claims Foreign Trade Policy benefits.
  - Opting in to exports during onboarding.
  - One RBI transaction purpose code per account (for example P0802 software consultancy, P0807 off-site software exports, P0806 subscriptions).
  - The customer's name, billing address and a service description on every charge.

  Payouts are in INR. Stripe Billing subscriptions are supported for international customers. Standard Chartered emails a payment advice on each export payout day. 3DS applies to international cards. — [Stripe Docs](https://docs.stripe.com/india-accept-international-payments)
- [BLOG] Stripe went invite-only in India in May 2024. Third-party estimates of all-in cost are about 5 to 6.3% on international payments; these are unverified figures from competitors. — [Skydo](https://skydo.com/blog/stripe-india-charges-review-alternatives); [Winvesta](https://www.winvesta.in/blog/businesses/stripe-alternatives-for-india-best-payment-platforms-for-freelancers-and-businesses)

**Stripe Managed Payments (Stripe's MoR, built from Lemon Squeezy)**
- [OFFICIAL] Lemon Squeezy's update of 28 Jan 2026 says Managed Payments supports "merchants in 35+ countries" with expansion "later this year". Access is by waitlist, and sellers outside supported countries are pointed to Stripe Atlas. — [Lemon Squeezy 2026 update](https://www.lemonsqueezy.com/blog/2026-update)
- [BLOG] Paddle reported that the beta did not support India. A current official eligibility list was not retrieved. — [Paddle webinar page](https://www.paddle.com/resources/stripe-managed-payments)

**Lemon Squeezy (MoR, now "Link, LLC")**
- [OFFICIAL] Fees: 5% + $0.50, plus 1.5% for international payments, 1.5% for PayPal and 0.5% for subscriptions. Payout fees for non-US merchants are 1% per bank payout or 3% per PayPal payout (capped at $30). — [Lemon Squeezy fees](https://docs.lemonsqueezy.com/help/getting-started/fees)
- [OFFICIAL] India bank payouts are only possible "if their accounts are pre-approved by Stripe". Otherwise Indian merchants must use PayPal payouts. — [Lemon Squeezy supported countries](https://docs.lemonsqueezy.com/help/getting-started/supported-countries)
- [OFFICIAL] The 2026 post admits "slower support responses and less frequent product updates" while the team focuses on migrating sellers to Stripe Managed Payments. — [Lemon Squeezy 2026 update](https://www.lemonsqueezy.com/blog/2026-update)

**Paddle (MoR)**
- [OFFICIAL] Paddle works "with software businesses anywhere in the world" except a list of unsupported countries, and India is not on that list. — [Paddle supported countries](https://www.paddle.com/help/start/intro-to-paddle/which-countries-are-supported-by-paddle)
- [OFFICIAL] Pricing is 5% + 50¢ per checkout transaction. That includes MoR tax collection and filing, fraud protection, chargeback handling and buyer support, with "no hidden fees". — [Paddle pricing](https://www.paddle.com/pricing)
- [OFFICIAL, ProfitWell-hosted copy] Payouts go by wire or Payoneer, on a monthly schedule with a minimum threshold. Some countries incur a $15 SWIFT fee. — [Paddle: When and how do I get paid](https://www.paddle.com/help/manage/get-paid/when-and-how-do-i-get-paid)
- [BLOG] Indian payouts likely fall under the SWIFT fee, with a conversion margin of up to 1.5%. — [Winvesta](https://www.winvesta.in/blog/businesses/paddle-payouts-india-fees-timing-bank-options)

**Polar.sh (MoR, open-source oriented)**
- [OFFICIAL] India is in the payout country list. Payouts go through Stripe Connect Express. The FAQ says Stripe's India invite-only status does not block payouts, because customer payments go to Polar (US) and Connect Express only handles transfers. Individuals can sell if Connect Express supports the "individual" business type in the founder's region, which must be checked in onboarding for India. — [Polar supported countries](https://polar.sh/docs/merchant-of-record/supported-countries)
- [OFFICIAL] Fees:

  | Plan | Monthly fee | Per-transaction fee |
  |---|---|---|
  | Starter | free | 5% + 50¢ |
  | Pro | $20 | 3.8% + 40¢ |
  | Growth | $100 | 3.6% + 35¢ |
  | Scale | $400 | 3.4% + 30¢ |

  On top of that: +1.5% for non-US cards. Stripe's payout fees apply: $2 per month with active payouts, 0.25% + $0.25 per payout, and 1% cross-border FX for non-EU countries. Disputes cost $15. — [Polar fees](https://polar.sh/docs/merchant-of-record/fees)

**Dodo Payments (MoR, India-founded)**
- [OFFICIAL] Fees:
  - Base: 4% + $0.40.
  - Surcharges: +1.5% for international, +0.5% for subscriptions, +3% for PayPal.
  - Domestic India cards and UPI: 4% + 15¢.
  - Refunds $1, disputes $30.
  - No setup or monthly fees.
  - Payouts: listed as "Free" in the table, but the FAQ says $5 if the payout is under $1,000. USD SWIFT payouts for non-US businesses cost $25. These conflict internally.

  — [Dodo pricing](https://dodopayments.com/pricing)
- [BLOG, Dodo's own and others] As MoR, Dodo is the legal seller and sends a consolidated payout to the Indian bank account. There are conflicting reports on whether an INR wallet or INR settlement still exists. — [Dodo blog](https://dodopayments.com/blogs/get-paid-usd-developer-india); [Whop review](https://whop.com/blog/dodo-payments-review/); [Dodo INR page](https://dodopayments.com/currency/inr)

**Gumroad (MoR)**
- [OFFICIAL] Fees are 10% + $0.50 per transaction, or 30% on sales through the Discover marketplace. "Gumroad is your merchant of record", with worldwide sales tax collection and remittance since 1 Jan 2025. Payout is by direct deposit or PayPal, "varies by country". India is not specifically listed. — [Gumroad pricing](https://gumroad.com/pricing)

**Razorpay (Indian processor, holds a PA-CB licence)**
- [OFFICIAL] International cards need "an eligible registered business with a valid website". Individuals and freelancers "must integrate PayPal to accept international payments" (International Bank Transfer is also listed for individuals). Onboarding accepts individuals, sole proprietorships, partnerships, private and public limited companies, LLPs and NGOs. KYC needs: PAN (personal or business), GSTIN if registered, Udyam certificate for MSMEs, address proof, authorised signatory details, and video KYC with Aadhaar and PAN. Subscriptions are listed as supported for international payments. — [Razorpay international payments docs](https://razorpay.com/docs/payments/international-payments/)
- [OFFICIAL] Fees:
  - International cards: up to 3%.
  - International bank transfers (MoneySaver / virtual multi-currency accounts): 1% plus GST, 0% FX markup.
  - Subscriptions on cards: 0.9% plus platform fees.
  - 18% GST on Razorpay's fees.
  - No setup or annual fees.

  — [Razorpay pricing](https://razorpay.com/pricing/)

**PayPal India**
- [OFFICIAL] A purpose code (an RBI code, for example P0802) must be set before withdrawing to an Indian bank. Changing it from goods to services needs proof (service agreement, invoice, SOFTEX or website). — [PayPal India: purpose code](https://www.paypal.com/in/cshelp/article/what-is-the-purpose-code-help978)
- [OFFICIAL] "Starting Feb 2026, you will be able to download an automatically generated FIRA every week" at no cost, under Reports → Tax → FIRA. An older PayPal page describes a monthly FIRA. — [PayPal India FIRC page](https://www.paypal.com/in/webapps/mpp/firc-certificate); [PayPal monthly digital FIRA](https://www.paypal.com/in/brc/article/paypal-monthly-digital-firc)
- [BLOG] Fees are a 4.4% commercial fee + $0.30 (USD) plus a currency conversion spread of about 3 to 4%, for an all-in cost of about 5 to 9%. 18% GST applies on the fees. The official fee page returned HTTP 403. — [Skydo](https://www.skydo.com/compare/paypal-pricing); [Xflow](https://www.xflowpay.com/blog/paypal-transaction-fees)

**Cashfree**
- [BLOG, competitor] Cashfree reportedly holds a PA-CB licence, issues a free e-FIRA per transaction within 24 hours, is aimed at invoices under $10,000, and does not automate eBRC. No official fee or individual-eligibility page was retrieved. — [Skydo: Cashfree vs Razorpay](https://www.skydo.com/compare/cashfree-vs-razorpay); [Skydo: PA-CB guide](https://www.skydo.com/blog/top-6-international-payment-aggregators-in-india-2026-guide)

**RBI cross-border aggregator (PA-CB) cap**
- [BLOG and law-firm notes] RBI's 2025 Payment Aggregator Master Directions cap PA-CB transactions at ₹25 lakh per transaction or per unit; sources differ on which. Some sources also cite a USD 10,000 export cap. These limits are irrelevant at developer-subscription prices. — [Cyril Amarchand Mangaldas client alert](https://www.cyrilshroff.com/wp-content/uploads/2025/10/Client-Alert-RBI-Introduces-Consolidated-Framework-for-Payment-Aggregators-3.pdf); [Winvesta](https://www.winvesta.in/blog/businesses/rbis-25-lakh-cap-on-cross-border-payments-what-to-know)

### Inferences
- **No entity needed (individual PAN plus bank account), in order of fit:**
  1. **Polar**: built for open source, India payouts confirmed. Individual eligibility still has to be checked during Stripe Connect onboarding.
  2. **Paddle**: 5% + 50¢ all-in MoR. Individual or sole-trader acceptance is unconfirmed.
  3. **Dodo**: India-focused, but its payout fee terms conflict internally.
  4. **Gumroad**: a 10% fee, which makes it expensive.
  5. **Lemon Squeezy**: in maintenance mode, and India bank payouts need Stripe pre-approval, so likely PayPal payouts at 3%.
  6. **PayPal**: direct, not MoR. The founder carries the tax burden.
- **Needs a registered entity:** Stripe India (sole proprietorship, LLP or company, *plus* an invite) and Razorpay international card acceptance (a "registered business"). A **sole proprietorship** is not a separate legal entity, but in practice it is set up with GST registration, Udyam registration and a current account. It is the cheapest way to qualify and is *not* incorporation. **[CA]**
- **Incorporation is not justified at the start.** Every MoR option works without a company. GitHub Marketplace paid listings need a GitHub *organization*, which is a free GitHub construct, not a legal company.
- **Effective cost on a $10 per month subscription:**
  - Polar Starter: about 5% + 1.5% + 50¢, so about $1.15 per charge before payout fees, or 11.5%.
  - Paddle: 5% + 50¢, so $1.00, or 10%.

  Fixed per-charge fees dominate at low prices, so annual plans or prices of $15 or more reduce the percentage drag.

### Gaps
- Paddle's and Dodo's KYC requirements for an Indian individual or sole proprietor could not be retrieved from official pages.
- Polar's acceptance of individuals specifically in India needs onboarding confirmation.
- I did not retrieve Stripe Managed Payments' current country list, so whether India was added in 2026 is unknown.
- The official PayPal India fee schedule was blocked (HTTP 403), so its fees come only from competitor blogs.
- Official Cashfree pricing and onboarding pages were not retrieved.
- Gumroad's India payout method could not be confirmed.

---

## 3. Tax and compliance: GST export of services, LUT, thresholds, OIDAR, FEMA/FIRA, and what an MoR removes

### Takeaway
Selling a software subscription from India to a foreign customer is an "export of services" if the five conditions in IGST Act section 2(6) are met. That makes it zero-rated: 0% GST if the founder files an LUT (Form GST RFD-11) each financial year once GST-registered. OIDAR is mainly a regime for *foreign* suppliers selling into India, so an Indian exporter of digital services is generally zero-rated, not taxed as OIDAR. Whether GST registration is needed below ₹20 lakh turnover is contested and is the most important question for a CA. Selling through an MoR changes the picture: the MoR is the seller to end customers, and the founder's supply is arguably one export to the MoR. **[CA]**

### Cited Findings
- [OFFICIAL] IGST Act section 2(6) defines export of services. All five conditions must hold:
  1. The supplier is in India.
  2. The recipient is outside India.
  3. The place of supply is outside India.
  4. Payment is received in convertible foreign exchange (or in INR where RBI permits).
  5. Supplier and recipient are not merely establishments of one distinct person.

  Section 16 makes exports "zero-rated supply". The exporter can either supply under a bond or LUT without paying IGST and claim a refund of unused input tax credit, or pay IGST and claim a refund. — [IGST Act 2017 (CBIC)](https://cbic-gst.gov.in/aces/Documents/IGST-bill.pdf); [CBIC Sectoral FAQs](https://cbic-gst.gov.in/sectoral-faq.html)
- [OFFICIAL] CBIC's LUT/Bond master circular gives the LUT procedure. Payments from NRE accounts (in rupees) do not meet the foreign-exchange condition, per the CBIC FAQs. — [CBIC Circular 8/8/2017-GST](https://cbic-gst.gov.in/pdf/Final_Master_circular_LUT_Bond_04102017.pdf); [CBIC Sectoral FAQs](https://cbic-gst.gov.in/sectoral-faq.html)
- [BLOG] The LUT is filed in Form GST RFD-11 under section 16(3) of the IGST Act and rule 96A of the CGST Rules. It must be renewed every financial year, so a fresh one is needed for FY 2026-27. — [legalsuvidha](https://legalsuvidha.com/blog/form-rfd-11-filing-of-letter-of-undertakinglut-in-gst); [incorpx](https://www.incorpx.io/guide/how-to-apply-for-gst-lut-export-services)
- [BLOG/forums, conflicting] **Registration threshold:**
  - The rule: CGST Act section 24 makes registration compulsory for inter-State taxable supplies, and an export of services counts as inter-State.
  - The exception: Notification 10/2017-Integrated Tax (13 Oct 2017) exempts suppliers of inter-State *services* with all-India aggregate turnover up to ₹20 lakh (₹10 lakh in Manipur, Mizoram, Nagaland and Tripura).
  - The conflict: sources disagree on whether small service exporters can rely on this exemption and how export receipts are counted.

  **[CA]** — [setindiabiz](https://www.setindiabiz.com/blog/gst-registration-freelancers-export-services-below-20-lakhs); [taxmanagementindia forum](https://www.taxmanagementindia.com/web/View_discussions_detail.asp?ID=113055); [kanakkupillai](https://www.kanakkupillai.com/learn/new-gst-registration-threshold-limit-for-services/)
- [BLOG] OIDAR is defined in IGST Act section 2(17). It mainly governs *foreign* suppliers selling to non-taxable online recipients in India, who must register (Form GST REG-10). Since 1 Oct 2023 the scope is broader (any unregistered person in India). An Indian supplier serving a recipient outside India is an "export of service", not OIDAR. Sources conflict on whether the "essentially automated" wording has been formally notified as removed. — [treelife](https://treelife.in/legal/oidar-registration-in-india/); [taxguru](https://taxguru.in/?p=879579); [cleartax](https://cleartax.in/s/place-of-supply-for-oidar); [CBIC OIDAR flier (2017)](https://cbic-gst.gov.in/hindi/pdf/e-version-gst-fliers/OIDAR_online%20version_online%20version_20_July_2017.pdf)
- [OFFICIAL, RBI] RBI has published draft, and reportedly final, "Directions on Export and Import of Goods and Services" that supersede the older Master Direction. The final document URL redirected and could not be read. — [RBI draft directions](https://website.rbi.org.in/documents/d/rbi/draftdirectionsonexportandimportofgoodsandservices-1-)
- [BLOG/law firm, conflicting] **Realisation period:** export proceeds must be realised and repatriated within a set period, which was reportedly extended from 9 to 15 months by a 13 Nov 2025 FEMA amendment (FEMA 23(R)/(7)/2025-RB). There are conflicting 2026 reports of a temporary 9-month window (5 June to 30 Sept 2026) and of 18 months for INR-invoiced exports. — [EY alert](https://www.ey.com/en_in/technical/alerts-hub/2025/12/rbi-introduces-comprehensive-relaxations-for-exporters-and-importers); [Taxmann](https://www.taxmann.com/post/blog/rbi-extends-the-time-period-for-realisation-of-full-export-from-9-to-15-months); [Xflow](https://www.xflowpay.com/blog/realisation-and-repatriation-of-export-proceeds)
- [OFFICIAL, provider] FIRA/FIRC is evidence of foreign inward remittance:
  - PayPal India issues a free weekly digital FIRA (from Feb 2026).
  - Stripe India's partner bank (Standard Chartered) emails a payment advice on each export payout.
  - Cashfree reportedly issues a per-transaction e-FIRA (blog source).

  — [PayPal FIRC](https://www.paypal.com/in/webapps/mpp/firc-certificate); [Stripe Docs](https://docs.stripe.com/india-accept-international-payments); [Skydo on Cashfree](https://www.skydo.com/compare/cashfree-vs-razorpay)
- [OFFICIAL, MoR] What an MoR takes on:
  - Paddle "collect[s] the correct rate of tax, track[s] the filing deadlines" and submits returns, and handles fraud and chargebacks. — [Paddle pricing](https://www.paddle.com/pricing)
  - Gumroad handles worldwide sales tax collection and remittance. — [Gumroad pricing](https://gumroad.com/pricing)
  - Stripe Managed Payments handles indirect tax compliance in 80+ countries; outside those, the merchant remains responsible. — [Stripe Managed Payments docs](https://docs.stripe.com/managed-payments)
  - Under an MoR, the Indian developer "is not the seller in the eyes of the law", and the MoR remits one payout. — [Dodo blog](https://dodopayments.com/blogs/get-paid-usd-developer-india); [Karbon](https://www.karboncard.com/blog/dodo-payment)

### Inferences
- **What an MoR removes:**
  - Foreign VAT, GST and US sales-tax registration and filing in dozens of countries.
  - Customer invoices and tax receipts.
  - Chargebacks and fraud handling.
  - Per-customer export documentation (name and address per charge, as Stripe India requires).
- **What the founder still keeps:**
  1. Indian income tax on the payouts (as an individual, business or professional income, possibly under presumptive taxation). **[CA]**
  2. The Indian GST position on the founder's supply to the MoR. That supply likely qualifies as an export of services to a foreign company, zero-rated with an LUT if registered. Whether registration is required at all below ₹20 lakh is unresolved. **[CA]**
  3. Evidence of realisation: FIRA or bank advice for each MoR payout, kept for GST refund and FEMA purposes.
  4. Choosing the right purpose code at the receiving bank (for example P0802 or P0807 for software).
- **Without an MoR** (Stripe India, Razorpay or PayPal direct), the founder also owns foreign indirect-tax exposure (EU VAT and others on digital services to consumers). For a solo founder, that is a strong argument for an MoR from day 1.
- **Actions that need GST registration and/or a business identity:**
  - Filing an LUT (needs a GSTIN).
  - Stripe India (sole proprietorship or higher).
  - Razorpay international cards (registered business).
  - An IEC is only needed for AMEX on Stripe. An IEC is PAN-based and an individual can obtain one.

  **[CA]**
- **Things a CA must confirm before the first rupee arrives:**
  - (a) Whether GST registration is mandatory for MoR payouts under ₹20 lakh.
  - (b) Whether the founder's supply to an MoR is an "export of services" or an intermediary service. Intermediary services are a known trap where the place of supply becomes India.
  - (c) The income-tax head and presumptive-scheme eligibility.
  - (d) The realisation period currently in force under FEMA 2026.
  - (e) Whether PayPal or other provider FIRAs suffice as realisation proof.

### Gaps
- The final 2025/2026 RBI export-import directions could not be retrieved (the URL redirected), so the exact realisation period in force on 12 Nov 2026 is not confirmed from an official page.
- I found no official CBIC clarification on whether an Indian developer supplying through a foreign MoR is an intermediary or a principal supplier.
- The text of Notification 10/2017-IT and any later amendment affecting exporters' threshold exemption was not fetched.
- Income-tax treatment (presumptive scheme under sections 44AD or 44ADA, or their successors under the Income-tax Act 2025) was not researched.
- An official LUT filing walkthrough on gst.gov.in was not fetched; the RFD-11 details come from blogs.

---

## 4. Privacy-respecting, consent-based analytics for a CLI tool or extension

### Takeaway
Go's toolchain telemetry is the strongest public model of consent-first CLI telemetry:
- Collection is **local by default**, and uploads happen only after an explicit opt-in.
- Only pre-approved aggregate counters are uploaded, with no user content.
- The data is published publicly, and changes go through a public proposal process.

For storage, PostHog's free tier (1M events per month, no card) easily covers an opt-in CLI. Plausible is cookieless and banner-free, but it is website analytics (for the docs site), not CLI telemetry.

### Cited Findings
- [OFFICIAL] Go telemetry runs in three modes: `local` (the default: collected locally, "never uploaded"), `on` (uploaded, subject to sampling) and `off` (nothing collected). Uploads are weekly and restricted to counters in a public upload config, approved via a proposal process. Stack counters "don't include any information about user inputs". The gopls language server prompts users to opt in. Uploaded data is publicly charted at telemetry.go.dev, and sampling reduces volume once enough users opt in. About 16,000 opted-in participants give statistically significant measurements. — [Go Telemetry docs](https://go.dev/doc/telemetry)
- [OFFICIAL] PostHog's free tier: the first 1M analytics events per month are free, along with 5K session replays. Allowances reset monthly with no rollover, and no card is needed for the free tier. — [PostHog pricing](https://posthog.com/pricing)
- [OFFICIAL] Plausible: "We do not use cookies or any other persistent identifiers", "no consent banner is required", and it claims GDPR, CCPA and PECR compliance. It offers a 30-day free trial with no card, and the code is open source and self-hostable. — [Plausible: privacy-focused analytics](https://plausible.io/privacy-focused-web-analytics)
- [OFFICIAL] VS Code's rules for extension telemetry:
  - Extensions must respect `vscode.env.isTelemetryEnabled` and `onDidChangeTelemetryEnabled`. "If `isTelemetryEnabled` reports false, even if your setting is enabled, telemetry must not be sent."
  - A custom setting should be tagged `telemetry` and `usesOnlineServices`.
  - Collect as little as possible, collect no personally identifiable information, and add no collection that lacks consent.
  - Shipping a `telemetry.json` disclosure file (viewable via the CLI `--telemetry` flag) is recommended.
  - The first-party `@vscode/extension-telemetry` module reports to Azure Application Insights.

  — [VS Code: Telemetry extension authors guide](https://code.visualstudio.com/api/extension-guides/telemetry)
- [OBSERVED] consoledonottrack.com, the domain usually cited for the `DO_NOT_TRACK=1` CLI convention, now serves unrelated content (pet-care articles). It can no longer be cited as the source for that convention. — [consoledonottrack.com (fetched 12 Nov 2026)](https://consoledonottrack.com/)
- [OFFICIAL, platform signal] VS Code Marketplace install counts and GitHub stars and forks are public. They serve as zero-telemetry adoption signals (see section 1). — [VS Code publishing docs](https://code.visualstudio.com/api/working-with-extensions/publishing-extension); [arXiv 2511.04453](https://arxiv.org/html/2511.04453v1)

### Inferences
- **Recommended pattern for the founder's CLI or extension, following Go's model:**
  - Default to off, or local-only.
  - On first run, show a one-time prompt describing exactly which counters would be sent, with a documented command such as `tool telemetry on|off|status`.
  - Honour a global opt-out environment variable as well, such as the community `DO_NOT_TRACK=1` convention (see Gaps).
  - Send only aggregate event names (command used, version, OS, coarse error class). Never send paths, arguments or code.
  - Publish the event schema in the repository and, ideally, publish aggregate dashboards.
- **VS Code extensions:** also respect the editor's own telemetry setting. See Gaps; the API was not fetched.
- **Zero-telemetry validation signals** fit the "no interviews" rule:
  - Marketplace installs, PyPI download statistics and GitHub stars, forks, issues and discussions.
  - MoR checkout conversion, trial-to-paid and churn data from the payment dashboard.
  - Plausible or PostHog on the documentation site for funnel data, with no cookies.
- **Cost:** PostHog's free 1M events per month and Plausible Community Edition self-hosting keep the cost at ₹0. Plausible Cloud is paid after the trial; its price was not retrieved.

### Gaps
- `DO_NOT_TRACK` has no authoritative source: it is an informal community convention, not a standard, and its original site has lapsed. Which CLIs honour it was not researched. The founder can still honour it as a courtesy, alongside the tool's own opt-out.
- PostHog's per-event price beyond the free tier, and its EU-hosting option, were not confirmed from the live page.
- Plausible Cloud pricing and the Community Edition licence (believed to be AGPL) were not confirmed.
- Whether opt-in telemetry from Indian users brings DPDP Act 2023 obligations was not researched. **[CA / lawyer]**
