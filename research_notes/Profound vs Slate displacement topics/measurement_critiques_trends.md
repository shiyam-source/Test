# Measurement critiques of AI search visibility tracking (Profound and its category), and trends to late 2026

> Research method note (read first): this session's network policy blocked WebFetch to most target domains (searchengineland.com, searchenginejournal.com, surferseo.com, windsor.ai, seonotebook.notion.site all failed DNS resolution). All findings below come from WebSearch result extracts, not full-page reads. Quoted text is the wording the search tool returned from the cited page. Treat it as "near-verbatim, verify before publishing", especially anything attributed to a named person. Where a quote came through a secondary blog and not the person's own channel, I say so.

## 1. Measurement validity: run-to-run variance, API vs. front-end, logged-out vs. personalized, sample sizes, synthetic vs. real prompts

### Takeaway
The strongest public evidence (SparkToro/Gumshoe, Jan 2026) shows that a single AI answer is close to a random draw. Brand lists repeat less than 1% of the time, so any "rank position in AI" is noise. The API answers many trackers rely on differ structurally from what users see in the app, and logged-out tracking ignores the memory and personalization that OpenAI extended to all tiers in June 2026. The only defensible metric is an aggregated appearance rate over many runs, reported with confidence intervals. Most vendors do not publish intervals.

### Cited Findings
**Run-to-run variance (SparkToro / Gumshoe study, published around 28 Jan 2026)**
- Design: 600 volunteers ran 12 brand-recommendation prompts through ChatGPT, Claude and Google AI surfaces 2,961 times in Nov–Dec 2025, with 60–100 runs per prompt per engine. — [Search Engine Land coverage](https://searchengineland.com/ai-recommendation-lists-rarely-repeat-study-468076); [Search Engine Journal coverage](https://www.searchenginejournal.com/ai-recommendations-change-with-nearly-every-query-sparktoro/566242); design details as summarized in [ThriveStack research note](https://www.thrivestack.ai/research/ai-visibility-tracking-non-determinism) and [Chosenly](https://chosenly.com/blog/llms-are-inconsistent-are-ai-search-tools-even-useful/)
- Finding: the chance of getting the same set of brands on a repeat run was under 1 in 100, and the same brands in the same order under 1 in 1,000. Claude was only slightly more consistent. — [SEL](https://searchengineland.com/ai-recommendation-lists-rarely-repeat-study-468076); [SEJ](https://www.searchenginejournal.com/ai-recommendations-change-with-nearly-every-query-sparktoro/566242)
- Rand Fishkin's line, as quoted by several secondary posts: "any tool that gives a 'ranking position in AI' is full of baloney." — quoted in [Dubado Solutions](https://dubadosolutions.com/rand-fishkin-proved-ai-recommendations-are-inconsistent-heres-why-and-how-to-fix-it/) and [Juris Digital](https://jurisdigital.com/news/stop-paying-for-ai-visibility-tracking-heres-what-actually-matters/) (secondary; verify against SparkToro original)
- Fishkin's recommendation, as reported: track visibility (appearance rate) at scale, not rank. He also urged marketers to stop paying for AI tracking products that lack stats-backed, publicly reviewable research. — [SEJ](https://www.searchenginejournal.com/ai-recommendations-change-with-nearly-every-query-sparktoro/566242); [Communicate Online](https://communicateonline.me/news/ai-brand-recommendations-vary-marketers-warned-on-tracking-tools/)
- Conflict of interest, disclosed in the study: it was co-run with Gumshoe.ai (Patrick O'Donnell), which sells AI tracking. Fishkin said his starting hypothesis was that AI tracking would prove pointless. The study is not peer-reviewed, and he called for larger follow-ups. — [SEJ](https://www.searchenginejournal.com/ai-recommendations-change-with-nearly-every-query-sparktoro/566242)
- Sample-size statistics: a commentator calculated that a 1% mention rate observed over 100 runs has a 95% confidence interval of roughly 0.2% to 5.5%. — cited in [ThriveStack](https://www.thrivestack.ai/research/ai-visibility-tracking-non-determinism) / [Verbatim Digital](https://verbatimdigital.com/articles/our-take-on-rand-fishkin-s-ai-visibility-research) (search extract; exact attribution unclear)
- Vendor rebuttal (from a competitor tracker): critics "acknowledge that aggregated visibility percentage ... can be stable and meaningful". — [LLM Pulse, "AI Rank Tracking Myths"](https://llmpulse.ai/blog/ai-rank-tracking-myths/)

**API vs. scraped front-end**
- Surfer SEO compared 1,000 prompt executions on ChatGPT and Perplexity. API answers contained no sources about 25% of the time, while scraped UI answers always had sources (16 on average vs. 7). The API detected no brand about 8% of the time. API answers were shorter (332 vs. 433 words). Surfer's data scientist said that using API monitoring as a proxy for AI visibility is wrong. — [Surfer SEO](https://surferseo.com/blog/llm-scraped-ai-answers-vs-api-results)
- A secondary blog reports only 24% brand overlap between API and scraped results. I could not confirm this figure in Surfer's own write-up. — [The Stacc](https://thestacc.com/blog/llm-scraped-vs-api-results/)
- Windsor.ai test on ChatGPT and Claude (page updated 16 Sep 2026): answers naming no tool at all were 7% via API and 57% in the app. One tool (Pipedream) appeared in 59% of API answers and 0% of app answers. Two API calls a few hours apart on the same day differed by 1.7 positions on average. — [Windsor.ai](https://windsor.ai/ai-visibility-tracking-accuracy/) (Windsor is a vendor)
- Vendor framing on both sides: [Conductor](https://conductor.com/academy/scraping-vs-api) and [seoClarity](https://www.seoclarity.net/blog/scraping-vs.-api) argue that UI scraping shows what users actually see, while APIs are cleaner and reproducible but simplified. Conductor also raises compliance and reliability concerns about scraping. Other overviews: [Superlines](https://www.superlines.io/articles/api-vs-ui-data-ai-visibility-tools/), [Metehan.ai, "How AI visibility tools collect data" (2 Jul 2026)](https://metehan.ai/articles/how-ai-visibility-tools-collect-data)

**Logged-out vs. personalized / memory**
- OpenAI's June 4, 2026 memory update reportedly keeps stored context current across conversations and doubled memory capacity for US Plus/Pro users. — [Reconn AI changelog](https://reconn-ai.com/llm-changelog.php)
- Tom's Guide describes ChatGPT's new memory ("Dreaming") as building a profile of the user on its own, and reports that OpenAI admits users can't see all of it. — [Tom's Guide](https://www.tomsguide.com/ai/chatgpts-new-memory-builds-a-profile-of-you-on-its-own-and-openai-admits-you-cant-see-all-of-it)
- Personalization from past chats and email was extended to Free and Go tiers on June 9, 2026. — [Digital Applied](https://www.digitalapplied.com/blog/chatgpt-personalization-free-tier-june-2026-confidentiality-guide). Per-chat memory controls appeared in an Aug 2026 Android beta (single source). — [Cryptonomist](https://en.cryptonomist.ch/2026/08/20/chatgpt-personalization-update-memory/)
- Vendors now concede that a visibility number is only valid for one fixed configuration (logged-out, browsing on, chosen region, named model). — [Rankry, "Which ChatGPT are you actually tracking?"](https://rankry.ai/blog/chatgpt-visibility-tracker/); [Cicero Studio](https://cicero.studio/en/blog/chatgpt-persistent-memory-personalization-ai-visibility-2026/)
- iPullRank notes that the major tools "miss out on the bulk of" AI Overviews "because they track based on logged-out states." — [iPullRank, How AI Mode Works](https://ipullrank.com/how-ai-mode-works)
- Mike King, on Google AI Mode patents (May 2025): results "are no longer deterministic in this environment. They are highly probabilistic." — [Mike King on X](https://x.com/iPullRank/status/1927495770015723733)

**Synthetic vs. real prompts / polling analogy**
- Kevin Indig (H1 2026): "Everyone is trying to measure AI visibility, but the thing they're measuring isn't stable. So, we need a different approach." He argues prompt tracking should work more like polling and focus groups than SEO rank tracking, and lists engine, personalization, reasoning level, model updates and stochastic variability as variables to control. — [Growth Memo, AI Halftime Report H1 2026](https://www.growth-memo.com/p/ai-halftime-report-h1-2026); [Indig Substack note](https://substack.com/@kevinindig/note/c-302753921)
- Indig frames the core error as treating AI visibility like a rank tracker. — [Growth Memo, "Make your prompt tracking more accurate"](https://www.growth-memo.com/p/how-to-make-prompt-tracking-much)
- Academic: a July 2026 arXiv critical survey of GEO (2023–2026) reports that generic heuristics transfer poorly and that competition erodes individual gains. It also notes "commercial audits further reveal low source overlap, substantial run-to-run variability, and persistent fidelity gaps", and proposes a reproducible protocol built on repeated measurement plus paraphrases. — [arXiv 2607.14035](https://arxiv.org/html/2607.14035v1)
- A cross-platform measurement paper finds the same prompt style can widen citations on one engine and fail on another. The data "discourages a single universal optimization recipe." — [arXiv 2604.25707](https://arxiv.org/html/2604.25707v2)
- A position paper argues that offline GEO setups miss deployment dynamics such as cross-platform distribution and whether a brand keeps being cited over time. — [arXiv 2606.12439](https://arxiv.org/html/2606.12439v1)

### Inferences
- The defensible unit of measurement is a distribution, not a position. Thought-leadership angle for Slate: "Your AI rank is a coin flip; your consideration-set share is real." Reporting a single prompt's result as a KPI is statistically invalid when brand lists repeat under 1% of the time.
- A sample-size angle: at 60–100 runs per prompt, low appearance rates have very wide intervals. A dashboard that tracks a few hundred prompts once per day can't reliably detect a week-over-week change below several percentage points. This supports the argument that a dashboard can't tell you whether your fix worked unless the system that made the fix also designs the measurement, for example with pre/post windows, holdouts and more runs on the prompts that changed.
- The "which ChatGPT?" problem gets worse with memory. Logged-out tracking measures a population of zero real users, since most buyers are logged in with memory on. A provocative frame for Slate is that visibility trackers measure an imaginary amnesiac user. Personalization shifts the goal from winning a prompt to being in the model's prior and the user's evidence trail (reviews, comparisons, communities).
- The API-vs-UI split is a credible "know what you're buying" topic, because tools differ on this and buyers rarely ask.

### Gaps
- I could not read SparkToro's original post (blocked), so the exact Fishkin quotes and the 1-in-100 / 1-in-1,000 figures are as reported by SEL/SEJ and secondary blogs.
- I found no independent, peer-reviewed replication of the SparkToro or Surfer results.
- The magnitude of variance in Indig's large personalization study was not visible in the search extracts.
- I found no study quantifying how much memory or personalization changes brand recommendations for logged-in users compared with logged-out ones.

## 2. Does Profound disclose its methodology? Critiques of Prompt Volumes, Conversation Explorer and citation studies

### Takeaway
Profound describes Prompt Volumes as built on "hundreds of millions of anonymized real conversations" (panel/clickstream-style data). I found no published sample size, panel composition, weighting or validation. Practitioner spot-checks show Profound volumes far above Ahrefs and GSC demand for the same term, and Profound's own Head of Data reportedly advises sanity-checking against GSC. Profound's own research says 40–60% of cited domains change month to month, which undercuts point-in-time case studies.

### Cited Findings
- Profound launched new Prompt Volumes features on Sep 18, 2025, and describes the data as built on hundreds of millions of anonymized real conversations. — [Profound changelog](https://product.tryprofound.com/en/changelog/new-prompt-volumes-features-available-now)
- LinkedIn practitioner spot-check: for "ai email agents", Profound showed 9,800 monthly prompts, Ahrefs showed 40 searches and Google Search Console showed 45 impressions. The author blames panel extrapolation ("if the panel sees 1% ... the data scales it by 100x"), reports that Profound's own Head of Data recommends sanity-checking prompt volume against GSC, and in another example puts Profound at about 25 times GSC impressions. Single anecdote. — [Raf Rivera, LinkedIn](https://ph.linkedin.com/in/rafrivera)
- The SEO Notebook newsletter compared Profound prompt volume with Ahrefs keyword data, found a gap it calls "absolutely massive", and warns that chasing inflated prompt volumes wastes time. — [SEO Notebook, "The Problem with Prompt Volume"](https://seonotebook.notion.site/The-Problem-with-Prompt-Volume-2bd8c368519180d69a34f962f3c03563)
- Conceptual critique: prompt data mixes information-seeking with content generation. "when users have texts written, this increases the prompt volume without any real search interest". The authors conclude prompt search volume is not currently a reliable control variable. — [Jaeckert & O'Daniel](https://www.jaeckert-odaniel.com/en/prompt-search-volume-real-data-or-all-guessed/)
- A third-party review (Trakkr, a competitor) rates Profound's data-accuracy claims "partially verified". It says Profound's pages describe Prompt Volumes latency in inconsistent ways and that start dates and regional coverage vary. — [Trakkr review: data accuracy](https://trakkr.ai/reviews/profound-review/data-accuracy)
- Competitor Scrunch (Jan 21, 2026) lists general panel-data pitfalls: panel composition bias, unit-of-exposure problems and over-reading small slices. It advises reconciling panel numbers with first-party sources like GSC. — [Scrunch, "Panel data, explained"](https://scrunch.com/blog/2026-01-panel-data-explained)
- Benchmark for good disclosure: Epoch AI's ChatGPT-usage methodology states its panel (a 5,000-person opt-in YouGov panel), denominators and metrics. — [Epoch AI methodology](https://epoch.ai/data/chatgpt-usage-documentation/methodology)
- Profound's own research (as cited in critical coverage): 40–60% of the domains cited by major AI platforms change month to month. — reported in [The Ad Spend](https://theadspend.com/blog/ai-search-scam-2026) and related coverage of [Digiday, May 2026](https://digiday.com/marketing/marketers-question-expensive-ai-visibility-tools-as-inconsistent-results-fuel-skepticism/) (secondary)
- Profound markets a GSC integration to "pair traditional search performance with AI Search performance". It does not address the overestimation claims. — [Profound GSC integration page](https://www.tryprofound.com/integrations/google-search-console)

### Inferences
- Topic angle: "Prompt volume is the new 'keyword difficulty': a vendor-invented number with no audit trail." Slate can contrast black-box demand estimates with first-party signals it can act on: GSC queries, sales-call questions, support tickets, and logs of AI referrals and agent hits.
- Privacy angle: clickstream panels of "anonymized real conversations" invite questions about consent and provenance (browser-extension panels and similar). I found no reporting on where Profound's panel comes from, so this should be posed as a question buyers should ask, not as a claim.
- Judo point: if 40–60% of cited domains churn monthly, a dashboard snapshot goes stale within weeks. Visibility is a maintenance problem that needs continuous execution (refreshing listicles, directory entries and third-party mentions), not a quarterly report.

### Gaps
- I did not find Profound's published methodology, panel size, panel sourcing (for example browser extensions or data brokers), weighting or validation. Absence of evidence in search is not proof that none exists.
- I found no specific critiques of Conversation Explorer beyond the Prompt Volumes critiques, and no critiques of specific Profound citation studies (such as Reddit/Wikipedia citation-share reports).
- The 40–60% churn figure is reported secondhand. Locate Profound's original "volatility" research before quoting it.

## 3. The monitoring-vs-action gap: does visibility data change outcomes, and what actually moves AI visibility?

### Takeaway
Buyers increasingly report that dashboards neither agree with each other nor tie to revenue. Agencies say three tools give three answers, VML is testing 17 platforms at once, and Digiday reports CMOs struggling to link AI visibility to sales. The evidence on levers points to off-site, third-party work: brand mentions, who you are listed alongside in third-party listicles, and the freshness of those associations, plus classic SEO rankings. Owned-site gimmicks like llms.txt show no measurable effect.

### Cited Findings
**Buyer skepticism / ROI**
- Digiday (Kimeko McCoy, May 1, 2026) reports that marketers question expensive AI visibility tools as inconsistent results fuel skepticism. Paul Dyer, CEO of AI agency /prompt, says that running three tools on identical prompts produces three different answers. VML is testing 17 AI visibility platforms at once, and some agencies are building internal trackers to cut costs. — [Digiday](https://digiday.com/marketing/marketers-question-expensive-ai-visibility-tools-as-inconsistent-results-fuel-skepticism/) (details via search extracts and secondary coverage: [Mission Media](https://missionmedia.asia/ai-visibility-tools-unreliable/), [KD Hungerford on X](https://x.com/KDHungerford/status/2067851128515997883))
- Digiday: "CMOs are struggling to link AI visibility with sales". AI visibility isn't clicked and tracked in a way that allows direct sales attribution. — [Digiday](https://digiday.com/marketing/cmos-are-struggling-to-link-ai-visibility-with-sales/)
- Reported price ranges: US$1,500–30,000/month for platforms (per Mission Media). Profound's entry plan is reportedly US$499/month. — [Mission Media](https://missionmedia.asia/ai-visibility-tools-unreliable/). Context: Profound raised a $96M Series C at a $1B valuation. — [The Ad Spend](https://theadspend.com/blog/ai-search-scam-2026)
- Kevin Indig, analyzing four brands, could not establish a reliable link between AI visibility and later branded search or direct traffic. He suggests combining self-reported attribution with leading indicators. — [Growth Memo, "Does AI drive more direct traffic?"](https://www.growth-memo.com/p/does-ai-drive-more-direct-traffic)
- Commentary titled "Share of Model Is Not a Metric Yet". — [The World of Search](https://www.theworldofsearch.com/share-of-model-is-not-a-metric-yet-what-marketing-leaders-should-actually-measure-in-ai-search)

**What moves visibility (evidence)**
- Ahrefs (May 26, 2025, 75K brands): the factors most correlated with brand presence in Google AI Overviews are branded web mentions (0.664), branded anchors (0.527) and branded search volume (0.392), against backlinks at 0.218. "The top 3 correlations are all off-site factors." Brands in the top quartile for mentions averaged 169 AIO mentions against 14 for the next quartile. Ahrefs warns that correlation ≠ causation. — [Ahrefs](https://ahrefs.com/blog/ai-overview-brand-correlation/)
- Search Engine Land (Sep 14, 2026, two GEO experiments across two brands and two verticals): better-written listicles on general sites produced little visibility. An owned listicle is "more of a foundation than a primary growth engine." Performance changed when recognized companies or experts were added to or removed from listicles, so co-mention companions matter. SERP visibility still appeared to influence LLM visibility, especially in ChatGPT. Caveat: AI Mode wasn't tracked in experiment 1. — [Search Engine Land](https://searchengineland.com/geo-experiments-challenge-conventional-ai-visibility-advice-488342). Secondary write-ups report "source decay", meaning visibility from a placement fades. — [DEV Community summary](https://dev.to/alifar/third-party-listicles-drove-early-ai-visibility-in-two-geo-experiments-2ha0)
- Mike King / iPullRank: citation selection happens at the passage level, so a single paragraph from a lower-ranking page can beat a comprehensive guide (query fan-out coverage). His free Qforia tool simulates fan-out. — [iPullRank query fan-out webinar](https://ipullrank.com/resources/webinars/query-fan-out-webinar); [NoGood fan-out guide](https://nogood.io/blog/query-fan-out-guide/)

**Myths**
- llms.txt: SE Ranking's study of about 300K domains found 10.13% had the file and found no effect on LLM citation frequency. Removing the variable improved the model's predictions. — [SE Ranking](https://seranking.com/blog/llms-txt/). Server logs show about 84 llms.txt requests across 62,100+ AI bot visits (about 0.1%) (Otterly data, via [Tobira](https://blog.tobira.ai/does-llms-txt-actually-work/)). Google's Gary Illyes reportedly said in July 2025 that Google doesn't support llms.txt, and John Mueller compared it to the meta keywords tag. — [guptadeepak.com](https://guptadeepak.com/llms-txt-meta-keywords-2026/); [TDM Insights](https://tdminsights.com/insights/llms-txt-has-adoption-but-no-evidence-behind-it/)
- Lily Ray on llms.txt: "I think for now it's a bit overhyped." She also says scaling content with generative AI doesn't work. — [Peec AI webinar recap](https://peec.ai/blog/what-should-marketing-teams-focus-on-for-ai-search-in-2026-insights-from-lily-ray-ethan-smith-and-peec-ai)
- Lily Ray (Mar 2026) calls it misleading to claim GEO credit for AI visibility "that was almost certainly driven by organic rankings the site already had." — [Lily Ray Substack, "Your GEO Strategy Might Be Destroying Your SEO"](https://lilyraynyc.substack.com/p/your-geo-strategy-might-be-destroying)
- Academic: AgentGEO (arXiv, Mar 2026) diagnoses specific citation failures and repairs them. It reports over 40% relative citation-rate improvement while modifying only 5% of content (vs. 25% for baselines), and notes that generic optimization can harm long-tail content. — [arXiv 2603.09296](https://arxiv.org/abs/2603.09296)

### Inferences
- The evidence says the levers are mostly off-site and relational: who mentions you, who you're listed next to, and how recently. Those are exactly the tasks a dashboard can't do, such as listicle outreach and corrections, directory and review profile upkeep, and third-party mentions. This is the core of Slate's "coworker that executes" pitch. Topic: "AI visibility is a PR and partnerships problem wearing an SEO costume."
- "Source decay" plus 40–60% monthly churn means visibility gains need continuous maintenance. Topic: "AI visibility has a half-life", with an operating cadence argument for autonomous execution.
- AgentGEO's finding (targeted diagnosis plus minimal edits beats generic rewrites) supports a "surgical fixes, not content volume" positioning.
- Contrarian topic: "Stop buying GEO for wins your SEO already earned" (from Lily Ray's critique). This argues for measuring incrementality, which needs controlled actions that a do-it system can log.

### Gaps
- I found no controlled study showing that teams using a monitoring dashboard alone improve AI visibility less than teams that also execute. The "dashboards don't change outcomes" claim is inferred from attribution complaints and lever evidence, not measured directly.
- I found no evidence-based studies on Reddit, review-site or directory impact in this pass (other researchers may cover them). Schema's effect on LLM citation was not covered.

## 4. Emerging shifts to late 2026 that weaken prompt-rank tracking

### Takeaway
By Nov 2026, four shifts erode "rank in a prompt" as a KPI. ChatGPT ads arrived (testing from Feb 9, 2026; international expansion Aug 2026). Default-on memory and personalization reached all tiers in June 2026. Agentic commerce runs on structured feeds and protocols (ACP from OpenAI/Stripe, UCP from Google/Shopify, announced Jan 11, 2026), so agents can transact without visiting a page. AI crawlers still return very few referrals relative to the pages they crawl. All four point from "what did the answer say" toward "is my data, offer and evidence agent-readable and correct everywhere".

### Cited Findings
- ChatGPT ads: OpenAI began testing ads on Feb 9, 2026 for logged-in adult Free and Go users, as sponsored cards below the answer. Product-feed ads entered beta in June 2026, and the UK, Mexico, Brazil, Japan and South Korea were added in Aug 2026. — [Visby](https://visby.ai/blogs/chatgpt-ads-are-here-what-it-means-for-ai-visibility-and-geo); [SEMoptimize](https://semoptimize.com/blog/chatgpt-ads-for-advertisers-2026/); [AmICited](https://www.amicited.com/blog/chatgpt-ads-global-expansion-brand-visibility/) (agency/vendor blogs; verify against OpenAI docs)
- OpenAI states that ads don't shape the generated answer and sit in a separate sponsored box. — [SPM Communications](https://spmcommunications.com/blog/geo-and-chatgpt-ads-what-they-mean-for-visibility). An SE Ranking study (Aug 2026, secondhand) found advertisers uncited in about 96% of tested responses. — [SEMoptimize](https://semoptimize.com/blog/chatgpt-ads-for-advertisers-2026/)
- Agentic commerce: Google and Shopify announced the Universal Commerce Protocol on Jan 11, 2026 at NRF, with 20+ endorsers. ACP (OpenAI and Stripe) requires a structured product feed, a checkout API and a payment integration. — [FashionNetwork](https://uk.fashionnetwork.com/news/Google-rolls-out-its-universal-standard-for-ai-powered-commerce,1797225.html); [Weaverse](https://weaverse.io/blogs/agentic-commerce-acp-ucp-2026); [Thomas Wiegold](https://thomas-wiegold.com/blog/agentic-commerce-ucp/). Sources conflict on maturity: one reports OpenAI moved Instant Checkout to an app-based model or backed away after about five months, and UCP was described as early access in March 2026. — [Thomas Wiegold](https://thomas-wiegold.com/blog/agentic-commerce-ucp/); [Presta](https://wearepresta.com/the-universal-commerce-protocol-rollout-in-2026-what-every-e-commerce-brand-needs-to-know/)
- Commentators argue that agents call commerce APIs and feeds directly and favor structured data (APIs, feeds, schema) over rendered pages. — [Bluestone PIM](https://www.bluestonepim.com/blog/how-to-prepare-for-agentic-commerce); [Productsup tracker](https://www.productsup.com/agentic-commerce-tracker)
- Crawl-to-referral ratios: Cloudflare's July 2025 analysis put them at roughly Google 14:1, OpenAI 1,700:1 and Anthropic 73,000:1. 2026 figures vary widely by window: for July 2026, one tally has Anthropic at 1,917:1 and OpenAI at 251:1, while a Q1 2026 report has Anthropic at 20,583:1. Google stays near 5:1. — [PPC Land](https://ppc.land/crawl-to-referral-ratio/); [eCorpIT](https://ecorpit.com/ai-crawler-crawl-to-referral-ratio-2026-geo-decision/); [TinyFish](https://current.tinyfish.ai/issue/27/echoes/article/14060/20583-pages-per-referral-what-the-crawl-to) (secondary; check Cloudflare Radar directly)
- Cloudflare split its crawler controls (search vs. agent vs. training) in Sep 2026, per a secondary write-up. — [DEV Community](https://dev.to/mr_manushukla/september-15-2026-cloudflares-crawler-split-and-how-to-configure-search-agent-and-training-3ek0)
- OpenAI's Atlas announcement advised using agent mode logged out to limit access to sensitive data. The search tool reported that the page now notes Atlas has been deprecated. — [OpenAI](https://openai.com/index/introducing-chatgpt-atlas/) (deprecation status unverified)
- Users behave differently in AI Overviews than in AI Mode. — [Growth Memo](https://www.growth-memo.com/p/users-behave-differently-in-ai-overviews)

### Inferences
- Once ads sit next to organic answers, an "AI share of voice" number that blends sponsored and organic, or ignores sponsored units, misleads. Ads also make "is my organic presence correct and persuasive" more valuable, since organic citations are not for sale.
- In agentic commerce the "answer" may never render. The buyer is an agent reading feeds, pricing, inventory and reviews. Topic for Slate: "Your next buyer doesn't read your answer. It reads your feed." That pushes the job from monitoring prompts to keeping structured data, directory listings and third-party facts accurate, which is execution work.
- Agent and crawler traffic is now measurable in server logs and at the CDN, while prompts are not. A first-party "agent analytics" story (which bots fetched what, then what referred) is more defensible than synthetic prompt panels.

### Gaps
- I found no reliable data on what share of B2B purchase research is now done by agents, or on how analytics tools attribute agent sessions.
- I found no primary OpenAI documentation in this pass for ads mechanics or Atlas deprecation. Dates come from secondary blogs and should be checked.
- I found no study on how Google AI Mode personalization (Gemini memory or Workspace context) affects brand recommendations.

## 5. Vendor lock-in and data ownership

### Takeaway
Third-party reviews say Profound puts all-time history, CSV/JSON export, API and MCP access behind its unpriced Enterprise tier, and that trial accounts keep no prompt history. I found no public Profound terms on who owns prompt histories.

### Cited Findings
- Reviews state that Profound's trial keeps no prompt history, exports or API access. All-time history, CSV/JSON exports, API and MCP access and SSO are on Enterprise, which has no published price. — [Trakkr: Profound integrations, API, MCP and export](https://trakkr.ai/reviews/profound-review/integrations) (competitor); [Geoptie review](https://geoptie.com/blog/profound-review)
- Profound's API docs reportedly say access is "available on request", and its MCP announcement reportedly limits MCP to Enterprise customers. — [Promptwatch vs Profound](https://promptwatch.com/promptwatch-vs-profound) (competitor)
- G2 themes: cost is the most frequent complaint. One reviewer says the "cost per prompt is higher than average", and the interface is called "data-heavy" and "overwhelming for new users". Overall ratings are high (about 4.5–4.6, counts vary by source). — [G2](https://www.g2.com/products/profound/reviews?page=10); [Scalenut review](https://www.scalenut.com/blogs/profound-ai-reviews); [Mentionova](https://mentionova.com/blog/profound-reviews-reddit)
- General principle: exporting raw data may not preserve the prompts, configuration and decision history needed to reproduce a system elsewhere. — [dotkonnekt, data portability in AI contracts](https://dotkonnekt.com/blogs/enterprise-ai/securing-data-portability-in-ai-contracts-to-prevent-lock-in)
- Note: Slate itself publishes a Profound pricing page. — [slatehq.com/blog/profound-aeo-pricing](https://slatehq.com/blog/profound-aeo-pricing)

### Inferences
- Topic angle: "Your prompt history is your market research. Who owns it?" Because runs are noisy, longitudinal history is the only thing that makes the data meaningful. Gating history and export behind Enterprise means the asset that gains value over time is the one hardest to take with you.
- A stronger Slate frame is that the durable asset isn't the prompt log but the changes made in the world: corrected listicles, updated directories, published content. Those persist whatever vendor you use.

### Gaps
- I found no public Profound ToS or DPA language on prompt-history ownership, retention or post-termination export. Ask sales or legal directly.
- The export and API claims come from competitor-authored reviews and need confirming against Profound docs.

## 6. Practitioner voices (skeptical and bullish)

### Takeaway
The skeptics include Fishkin (rank is "baloney", demand public stats), Indig (unstable measurement, polling not rank-tracking, no proven traffic link), Lily Ray (GEO is often repackaged SEO, hype, false credit-taking) and the Digiday agency quotes ("three tools, three answers"). The mild bulls (Fishkin, vendor rebuttals) accept aggregated appearance rate over many runs. Almost nobody defends position tracking.

### Cited Findings
- Rand Fishkin (SparkToro, Jan 2026): "any tool that gives a 'ranking position in AI' is full of baloney" (secondary quote). He also urged buyers to stop paying for tools without stats-backed, publicly reviewable research. — [Dubado](https://dubadosolutions.com/rand-fishkin-proved-ai-recommendations-are-inconsistent-heres-why-and-how-to-fix-it/); [SEJ](https://www.searchenginejournal.com/ai-recommendations-change-with-nearly-every-query-sparktoro/566242)
- Fishkin podcast, "Your homepage is not your homepage anymore". — [No Hacks podcast ep. 219](https://nohacksshow.buzzsprout.com/1677508/episodes/18787517-219-your-homepage-is-not-your-homepage-anymore-with-rand-fishkin) (content not extracted)
- Kevin Indig (2026): "Everyone is trying to measure AI visibility, but the thing they're measuring isn't stable. So, we need a different approach." — [Substack note](https://substack.com/@kevinindig/note/c-302753921). Kalicube Summit 2026 session: personalization exists, especially for local, but variance is high. — [Kalicube Summit](https://kalicubesummit.com/2026/sessions/kevin-indig-grounded-gate-session/)
- Mike King (iPullRank): AI Mode results "are no longer deterministic ... highly probabilistic". — [X](https://x.com/iPullRank/status/1927495770015723733). He frames AI search as a branding channel. — [iPullRank](https://ipullrank.com/ai-search-is-a-branding-channel)
- Lily Ray: llms.txt "a bit overhyped" — [Peec AI](https://peec.ai/blog/what-should-marketing-teams-focus-on-for-ai-search-in-2026-insights-from-lily-ray-ethan-smith-and-peec-ai). Calls opportunistic GEO services "a grift" and much of GEO repackaged SEO (via secondary summary) — [Kafkai](https://kafkai.ai/articles/ai-seo/ai-visibility-spam-is-wrong/) and [PPC Land](https://ppc.land/lily-ray-what-the-seo-industry-is-getting-dangerously-wrong-about-ai-search/). The same secondary source says she highlights that LLM responses are "non-deterministic and highly personalized", a limitation tools don't mention. — [Kafkai](https://kafkai.ai/articles/ai-seo/ai-visibility-spam-is-wrong/). She warns GEO experiments risk Google removals. — [SEL interview](https://searchengineland.com/lily-ray-search-engine-land-20-for-20-interview-486614)
- Paul Dyer (CEO, /prompt), via Digiday: run three tools on identical prompts and you get three different answers (paraphrase via extract). — [Digiday](https://digiday.com/marketing/marketers-question-expensive-ai-visibility-tools-as-inconsistent-results-fuel-skepticism/)
- A polemical critique: "The AI Search Grift, One Year Later: They Sold Each Other the Territory". — [The Ad Spend](https://theadspend.com/blog/ai-search-scam-2026)
- Defense of tracking from a vendor: aggregated visibility percentage can be stable and meaningful. — [LLM Pulse](https://llmpulse.ai/blog/ai-rank-tracking-myths/)

### Inferences
- The expert consensus has shifted from "track your AI rank" to "sample the distribution like a pollster, then do the off-site work". Slate can position itself in the second half of that sentence and frame Profound-style tools as polling firms selling exit polls to candidates who still need to campaign.
- Candidate contrarian topics backed by this evidence:
  1. "AI rank is a coin flip": a statistics primer on confidence intervals for appearance rates.
  2. "The amnesiac user problem": logged-out tracking in a memory-on world.
  3. "API answers aren't answers": what your tracker actually queries.
  4. "Prompt volume is the new keyword difficulty": black-box demand estimates.
  5. "AI visibility has a half-life": source decay and 40–60% monthly citation churn, so maintenance beats measurement.
  6. "Your companions are your ranking factor": co-mention and listicle-neighbor effects (SEL Sep 2026).
  7. "Your next buyer reads your feed, not your answer": ACP, UCP and agentic commerce.
  8. "Stop paying GEO for SEO's wins": an incrementality argument (Lily Ray).
  9. "Own the fix, not the log": data ownership in a world of noisy measurement.

### Gaps
- I found no verbatim 2025–2026 statements from Aleyda Solis or Britney Muller on AI visibility tools (not reached in this pass).
- I did not search Reddit r/SEO threads directly.
- Lily Ray's sharpest quotes ("grift") are secondhand. Verify them against her Substack or X before publishing.
