---
title: "Your AI visibility dashboard is mostly noise. Here's the math."
slug: ai-visibility-coin-flip-report
meta_description: "We modelled how many AI answers a visibility number needs before it means anything. Daily tracking shows a 10-point swing in 37% of prompt-months, even when nothing changed."
primary_keyword: AI visibility tracking accuracy
secondary_keywords: [Profound alternative, AI search visibility, share of voice in ChatGPT, AEO measurement, prompt tracking]
asset: "The Coin-Flip Report (PDF, 9 pages)"
author: Slate Research
date: 2026-11
---

# Your AI visibility dashboard is mostly noise. Here's the math.

Here's a scene that plays out in a lot of marketing reviews right now. The AI visibility slide comes up. "Best CRM for startups" fell from 41% to 22% in ChatGPT this month. Someone asks what happened. Somebody else says a competitor published a big comparison page. A ticket gets opened to refresh the pillar post.

Probably nothing happened.

We modelled what AI visibility trackers can actually detect, given how they sample. If a prompt's true appearance rate is a steady 30% and you sample it once a day, a month of data can report anything from 17% to 48%. A drop from 41% to 22% is well within what happens when nothing changes at all.

The full study is **The Coin-Flip Report** ([download the PDF](#)). This post walks through what we found, why it matters most for anyone tracking at the prompt level (which is how most teams use tools like Profound), and how to measure without fooling yourself.

## AI answers are random. The industry agrees on that much.

Nobody serious argues that AI answers are stable. In January 2026, SparkToro and Gumshoe had 600 volunteers run the same 12 brand-recommendation prompts 2,961 times across ChatGPT, Claude and Google's AI surfaces. There was less than a 1-in-100 chance of getting the same set of brands twice, and less than a 1-in-1,000 chance of the same brands in the same order. Rand Fishkin's summary, widely quoted: any tool that gives a "ranking position in AI" is "full of baloney."

Kevin Indig has made the same point more gently: "Everyone is trying to measure AI visibility, but the thing they're measuring isn't stable."

The category's response has been to stop talking about rank and start talking about **appearance rate**: the share of answers that mention you. That's the right move. But an appearance rate is an estimate from a sample, and your plan sets the sample size through three numbers: how many prompts, how many engines, and how often each one runs.

That's what nobody has priced out. So we did.

## What we did

We treated each AI answer as a yes/no draw (did your brand appear or not), then:

- computed exact 95% confidence intervals for common sample sizes
- worked out the smallest month-over-month change each design can reliably detect
- simulated 200 tracking programs of 100 prompts × 3 engines × 12 months in which **no true rate ever changes**, and counted the "movement" the dashboards showed anyway
- simulated 20,000 months of a five-brand competitive race to see how often the real leader comes out on top

We didn't collect AI answers for this, and that's deliberate. Real answers also shift with model updates, personalization, location and API-versus-app collection. Leaving all of that out gives the trackers the best case. Real dashboards are noisier than anything in this study.

## Finding 1: a single prompt-month is a wide range, not a number

Daily runs give you about 30 answers per prompt per engine per month. Here's what that buys, if your true rate is 30%:

| Answers sampled | What the dashboard can show (95% range) |
|---|---|
| 7 (a one-week trial) | 9% – 65% |
| 30 (daily for a month) | 17% – 48% |
| 100 | 22% – 40% |
| 1,000 | 27% – 33% |

Put differently, a month-over-month swing of up to about **23 points** on a single prompt is ordinary noise at daily sampling. To *reliably* catch a real change (80% power) you need a move of about 35 points.

## Finding 2: noise looks exactly like a campaign result

In one simulated run, a prompt with a fixed 30% true rate came out at **47% in June and 13% in October**. Nothing changed. Show those two months on a slide and you'd celebrate one and panic about the other.

Across all 200 simulated programs:

- **37%** of prompt-months showed a swing of 10+ points with no real change
- **8.5%** showed a swing of 20+ points
- at 100 runs a month, the 10-point false alarms fall to 11%; at 250 runs, to about 1%

If your team reviews 300 prompt-engine pairs a month, that's roughly **110 double-digit moves that mean nothing**. A content calendar built from "prompts we lost this month" is mostly a calendar of random draws.

## Finding 3: share-of-voice leaderboards are close to coin flips

Competitive tables are where this gets expensive, because they drive positioning decisions. We simulated five brands with fixed true rates of 34%, 31%, 30%, 28% and 25%. That's a realistic, contested category.

With 30 answers per brand per month:

- the real leader showed up at **#1 only 37% of the time**
- it showed up at **#3 or lower 39% of the time**
- all five brands came out in the right order **3% of the time**

Even at 1,000 answers per brand, the full order was right less than half the time. The honest output for a race like that is "statistically tied", and almost no dashboard will tell you so.

## Finding 4: your topline is fine

Brand-wide numbers behave well. Averaged across 100 prompts and 3 engines (9,000 answers a month), the simulated brand's topline moved by at most about 1.2 points from month to month.

So the problem isn't AI visibility tracking as a whole. The problem is reading individual prompts as if they were trends, and that's exactly the view prompt-level dashboards are built around.

## What this means for Profound users (and everyone else)

On reported figures, Profound's agency workspace and its former Growth plan both ran 100 prompts across 3 engines once a day. Its current trial is reported at 50 prompts, 3 engines, for 7 days. Here's what those designs can detect:

| Design | Per-prompt 95% range at 30% | Smallest reliable change (one engine) | Engines pooled |
|---|---|---|---|
| 7-day trial (50 × 3 × 7) | 9% – 65% | 66 pts | 42 pts |
| Daily, 100 prompts × 3 engines | 17% – 48% | 35 pts | 20 pts |
| Same budget, 40 priority prompts × 4 engines × 60 runs | 20% – 42% | 25 pts | 12 pts |

Profound isn't doing anything wrong here. Its front-end data collection is a real strength, and reviewers praise it for good reason. The limit is arithmetic, and it applies to every vendor with a fixed cadence, Slate included. If we spread Slate's 10,000-answer Growth pool evenly across 100 prompts and 4 engines, single-prompt readings are no better.

The difference is in what you're allowed to do with the budget. With a fixed daily cadence, every prompt gets the same 30 draws whether it matters or not. With unlimited prompts and an answer pool, you can put depth on the 40 prompts you're actively fixing and run the rest lightly. With the same budget, that roughly halves the change you can detect.

And a 7-day trial can't tell you whether your visibility moved. It can tell you whether the workflow fits your team, which engines matter and whether the reports make sense. Judge a trial on that.

## Finding 5: pool prompts into topics and most of the problem goes away

Teams act on topics ("CRM for startups") more than on single strings. Pooling related prompts gives you a big sample without a bigger plan. We simulated it with prompts that have *different* true rates, so the pooling isn't flattering itself.

At daily sampling across three engines, the smallest reliable monthly change is:

- 1 prompt: 19 points
- 5-prompt topic: 8 points
- 10-prompt topic: **6 points**
- 25-prompt topic: 4 points

That's the most useful single change most teams can make, and it doesn't cost anything extra.

## A measurement standard we think every vendor should meet

We're proposing seven rules for anyone reporting AI visibility. Slate should be held to them like everyone else.

1. **Every rate ships with its range and sample size.** "31% (24–39%, n = 120)", never a bare "31%".
2. **No rank positions.** Report appearance rate and share of answers. Call close races ties.
3. **Topics are the unit of trend.** Use single prompts for diagnosis, not monthly progress reports.
4. **Put sampling depth where the work is.** Prompts you're fixing get more runs; background prompts get fewer.
5. **Call your shot before the data arrives.** Log the fix, the prompts it should move and by how much, then read the result once the planned sample is in.
6. **Disclose collection mode.** API or app, logged in or out, location and model version. Surfer found API answers had no sources about 25% of the time, while app-scraped answers always did.
7. **Publish the method.** If a vendor won't say how a number is sampled, treat the number as unverified.

## Ten questions to bring to your next demo

1. How many answers per prompt, per engine, per month does my plan actually collect?
2. Can I change runs per prompt, or is the cadence fixed?
3. Do you show a confidence range or sample size next to each rate?
4. API or consumer app? Logged in or out? From which location?
5. How do you handle model updates? Are they marked on trend charts?
6. What's the smallest change your reports treat as real, and why?
7. Can I group prompts into topics and trend the topic?
8. Where does your prompt-volume data come from, and has anyone outside the company validated it?
9. Can I export every raw answer with a timestamp?
10. Which engines are included, and what does each extra one cost?

Ask Slate these too. Any vendor worth signing with should be able to answer all ten in writing.

## The bottom line

An AI visibility number without a sample size is an anecdote. The fix is neither a bigger dashboard nor a more expensive contract. Buy the sampling depth your decisions need, put it on the prompts you're working on, read results by topic, and spend the rest of your effort changing what the models read: third-party listicles, review sites, directories, and the pages AI engines actually cite.

That last part is where Slate puts most of its energy. It watches the answers, and it also does the fixing.

**[Download The Coin-Flip Report (PDF)](#)**, with full method, every table and the ten-question vendor checklist.

---

*Disclosure: Slate sells an AI visibility and execution platform. Every limit described here applies to Slate's tracking as well. Plan figures for other vendors are third-party reported as of November 2026.*

<!--
EDITOR NOTES (remove before publishing)
- Verify Profound trial (50 prompts x 3 engines x 7 days) and agency workspace (100 x 3 x daily) on tryprofound.com/pricing.
- Verify SparkToro figures and the Fishkin "baloney" quote on SparkToro's original post (currently from secondary coverage).
- Verify the Indig quote on the Substack note.
- "Slate unlimited prompts + 10,000-answer pool" and the ability to set runs per prompt: confirm in product before publishing the "focus allocation" claim.
- Replace the (#) links with the hosted PDF URL.
-->
