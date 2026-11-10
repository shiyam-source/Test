# Slate Citation Lab: LinkedIn posts (series of 3)

Audience: technical SEOs, AI search researchers, web developers.
Data source: Slate's Multi-LLM Citation Study (Akilan), 1,000 B2B SaaS queries, captured 3 Aug 2026.
Image for each post: `part-1.png`, `part-2.png`, `part-3.png` (4:5, 2160×2700).
Suggested cadence: one a week, same weekday. Each post teases the next.

---

## Part 1: Cross-engine citation overlap

**Image:** part-1.png

29.

That's how many citations ChatGPT, Perplexity and Claude agreed on, across 1,000 identical prompts.

Out of 31,128.

Slate Citation Lab, part 1 of 3.

The setup: 1,000 B2B SaaS queries across 40 categories, split evenly into BOFU, MOFU and TOFU. Each one went through ChatGPT, Perplexity, Claude and Gemini with web search on. We pulled every URL each engine surfaced, normalised them (host lowercased, www and trailing slash stripped, 20 tracking params like utm_* and gclid dropped), and joined everything per query against Google's top 10 and the AI Overview citations for the same queries.

What came out:

1. Engines almost never cite the same page.
Mean per-query URL overlap:
→ Perplexity vs Claude: 13.6%
→ ChatGPT vs Perplexity: 0.9%
→ ChatGPT vs Claude: 0.5%
Even at domain level, the best pair tops out at 18.1%.

2. 88.7% of query–URL citations came from one engine only.
11.2% from two. 0.09% from all three. That's the 29.
When all three do converge, 62.1% of those pages already rank in Google's top 10.

3. They agree on vendors, though.
We matched 154 B2B SaaS brand names in the answer text. Pairwise vendor overlap runs 35.2% to 42.0%, for every pair.
Gemini, which showed almost no links in our capture, sits in the same band.
On the 509 queries where all four named a vendor, they named 7.5 between them and agreed on 2.1.

4. Most of what gets cited isn't in Google at all.
The three link-surfacing engines cited 19,906 unique URLs. 14,757 of them (74.1%) appear in neither the top 10 nor the AI Overview.

My read:
The engines share a picture of each category, and they reach it through almost completely separate evidence. So the vendor consensus isn't coming from the citations. It's upstream: training data, plus whatever each retrieval stack happens to pull.

Two practical consequences:
→ An "AI citation rate" averaged across engines blends four unrelated numbers. Report each engine on its own.
→ "Named in the answer" is the metric that holds still. "Cited" is four separate games.

Method notes, before you ask:
→ API with web search, not the consumer apps: gpt-5.4-mini, sonar-pro, claude-sonnet-4.6, gemini-2.5-flash. Malte Landwehr's 52k-chat UI vs API test shows the two retrieve differently, so read every level here as API-side. We haven't rerun this in the UIs yet.
→ One run per query, captured 3 Aug 2026. Run-to-run variance isn't separated from engine differences. Gaps this wide are unlikely to be noise. The decimals won't last.
→ Gemini returns grounding metadata outside the answer text, and our capture didn't keep it. Gemini is scored on brand mentions only.
→ 61 of Claude's 1,000 responses were truncated at around 8,100 characters, so Claude's citation counts are a floor.

Akilan on our team ran this.

Part 2 next: each engine's citation fingerprint. Including the two engines that cited Reddit zero times in 1,000 queries.

If you run your own panels: does URL overlap look this low in the consumer UIs, or do the apps converge more?

---

## Part 2: Citation fingerprints

**Image:** part-2.png

Claude cited Reddit 0 times across 1,000 queries.
ChatGPT: also 0.
Perplexity: 1,051.

Slate Citation Lab, part 2 of 3. Same 1,000 B2B SaaS prompts, same capture, now scored on what each surface actually links to.

1. Link volume differs by an order of magnitude.
Links per answer:
→ Perplexity 19.08 (linked on all 1,000 queries)
→ Claude 12.49
→ Google AI Overview 9.42
→ ChatGPT 3.10 (linked on 628)
→ Gemini 0.07 (16 answers had a URL, see caveat)

2. ChatGPT isn't citing on informational queries. It's linking products.
It showed a link on 90.7% of BOFU queries, 89.5% of MOFU, and 8.1% of TOFU.
33.4% of the URLs it did show sit on a pricing or plans path. For Perplexity that's 2.0%, Claude 2.6%, AI Overview 1.5%.
Result: only 1.0% of Google's top-10 pages ever appear in a ChatGPT answer.

3. The Reddit split isn't an availability problem.
546 Reddit, Quora and Stack Overflow pages ranked in Google's top 10 for these queries.
→ Perplexity quoted 74.2% of them
→ AI Overview 37.0%
→ Claude 0.0%
Same pages, ranking and on-topic. Reddit is Perplexity's single most-cited domain (5.5% of its links, on 617 queries).
Community and social content as a share of citations: Perplexity 10.7%, AI Overview 10.4%, Claude 0.6%, ChatGPT 0.1%.

4. The same page format gets opposite treatment.
Pricing pages that rank: Perplexity cites 77.1% of them (its highest format). AI Overview cites 38.1% (its lowest).
Definition pages are the only format in the top two for Perplexity, Claude and AI Overview.

My read:
"Get on Reddit for AI visibility" is engine-specific advice. It works for Perplexity, partly for AI Overviews, and does nothing for ChatGPT or Claude, at least through the API.
And on ChatGPT, your pricing page is the citable asset for commercial queries. Your blog barely shows up.

Caveats:
→ API, not UI. Malte Landwehr measured up to 20 fan-outs per prompt in the ChatGPT UI against 7 in the API, so UI link behaviour is probably richer than this.
→ Gemini's grounding metadata isn't in the captured answer text, so 0.07 describes what a reader sees in that text, not what the model retrieved.
→ One run per query, 3 Aug 2026.

Part 3 next: we tested 19 page attributes on 6,881 ranking pages to see what gets a page cited. Almost none of it matters.

Question for anyone who has dug into this: is Claude's zero Reddit a retrieval-provider effect or a deliberate filter? Has anyone seen it cite reddit.com in the consumer app?

---

## Part 3: The null result

**Image:** part-3.png

Word count. H3s. Schema. Lists. Content depth.

We tested 19 page attributes on 6,881 ranking pages to see which ones get a page cited by AI.

For Perplexity and Google AI Overviews, none of them clears a negligible effect size.

Only rank does.

Slate Citation Lab, part 3 of 3.

The setup: for every top-10 page across the 1,000 queries (11,002-page scrape, 6,881 clean), compare cited vs not cited, per engine. Mann-Whitney with Cliff's δ for continuous attributes, chi-square with φ for binary ones. Anything under 0.11 is negligible.

1. Perplexity is a rank-following machine.
Organic position: δ 0.307, the largest effect in the whole study.
Every page attribute: under 0.10.
Citation rate falls from 86.9% at position 1 to 46.0% at position 9.

2. AI Overviews: same story, weaker.
Position: 0.131. Nothing else above 0.09.
55.1% cited at position 1, 34.1% at position 9.

3. Claude is the exception.
→ word count 0.186
→ content depth score 0.173
→ H3 count 0.152
→ has lists 0.151
→ schema count 0.149
All of these beat Claude's own position effect (0.149). None leaves the weak band. But the direction is consistent: Claude leans toward longer, deeper, more structured pages.

4. Put everything in one model and it barely moves.
Standardised logistic regression, position plus all 19 attributes:
→ Perplexity: McFadden R² 0.063, of which position alone gives 0.050
→ Claude: 0.057, position alone 0.011
→ AI Overview: 0.032, position alone 0.009
The full model beats the base rate by 0.6 to 4.1 points.

My read:
Among pages that already rank, there is no content checklist that gets you cited by Perplexity or AI Overviews. Rank is the one lever that transfers across every engine, and even that is weak: position 1 still goes uncited 13% of the time in Perplexity and 65% of the time in Claude.
If Claude matters to you, depth and structure are the only content signals with any weight.
Most "optimise your page for AI citation" advice is selling a lever this data can't find.

The caveat that matters most: page attributes only exist for pages in Google's top 10 or AI Overview. That's about a quarter of the cited pool. The other 74.1% of cited URLs sit outside Google entirely, and this analysis can't see them.

That's the next study: what the 74% actually is.
Follow if you want it when it lands.

Which attribute did you expect to show up here that didn't?

---

## Posting notes

- Put the methodology link (or "full study coming") in the first comment, not the body.
- Tag Malte Landwehr where his test is mentioned. Credit, and his audience is exactly this one.
- Tag Akilan on every post.
- Part 3 promises a follow-up study on the 74%. Only keep that line if the team will actually run it.
