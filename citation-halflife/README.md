# Citation half-life: a Slate Citation Lab study

**Question:** once an AI engine cites a page, or names a brand, for a given buyer prompt, how long does it keep doing so?

**Hook:** "Half of this week's AI citations are gone in __ days. Brand mentions last __× longer."

**Why it matters:** nobody publishes decay curves for AI citations. If citations churn in days while brand mentions hold for weeks, two things follow. Weekly citation reports are mostly noise. And "named, not cited" is the KPI that actually holds still, which puts a number on a claim from the first Citation Lab series.

## Data

SlateIndex weekly runs (see [slateindex.ai/methodology](https://slateindex.ai/methodology)):
- **Prompts:** about 30 fixed buyer prompts per category × 33 categories ≈ 990 prompts, split across informational, commercial, transactional and navigational intents.
- **Engines:** ChatGPT, Perplexity and Google AI Mode. Answers are collected **from the consumer apps through data providers, not the APIs**.
- **Schedule:** every Monday at 09:30 IST. Every run is kept, and the data is published under CC BY 4.0.
- **What's recorded:** for every response, the brands named (in order) and the sources cited.

The export format is in [DATA_REQUEST.md](DATA_REQUEST.md).

## Method

| Step | Definition |
|---|---|
| Unit | A **spell**: an unbroken run of weekly runs in which the same item appears in the answer to the same prompt on the same engine. Items are tracked at three levels: exact URL, domain, brand. |
| End of a spell | The item is absent for **2 consecutive collected runs**, so one-week flickers don't count as deaths. Sensitivity check: tolerance 0, where any absence ends the spell. |
| Missing data | A scheduled response that wasn't collected is **skipped**. It neither extends nor ends a spell. |
| Left truncation | Spells already present in the first run have an unknown start and are excluded. Only spells that start later ("incident spells") are used. |
| Right censoring | Spells still alive at the last run are censored, not dropped. |
| Estimator | Kaplan–Meier survival curves. **Half-life = median survival time**, reported in days (weeks × 7). |
| Comparison | URL vs brand survival with a log-rank test. Stratified by engine, intent, URL source type (vendor site, review site, community/UGC, media/other), and brand starting position (top 3 vs lower). |
| Churn | Week-over-week: of the items present in run *t*, the share absent in run *t+1*, for the same prompt and engine. |

### Known limits (stated on the last slide and in the post)
- **The number of runs caps what we can see.** With about 13 runs, spells longer than about 12 weeks are censored, so the brand half-life may come out as a lower bound ("more than X days").
- **One answer per prompt, per engine, per week.** Answer-to-answer variance can't be fully separated from true decay. That's why the flicker tolerance exists, and why both tolerances are reported.
- **The prompt set is B2B software only.** Results describe that space, not consumer queries.

## Layout

```
halflife/spells.py     presence series -> spells (flicker tolerance, missing weeks, truncation)
halflife/survival.py   Kaplan-Meier, median survival, log-rank test
halflife/analyze.py    export -> out/summary.json, out/curves.csv
halflife/render.py     summary -> out/carousel.html + out/post.txt (watermarked if simulated)
halflife/carousel.css  Slate design system
halflife/simulate.py   synthetic export for building and testing (writes data/SIMULATED)
render.js              carousel.html -> out/slides/*.png + out/carousel.pdf
tests/test_halflife.py spell rules, KM on a textbook case, KM recovering known hazards, log-rank power
preview/               the carousel rendered on SIMULATED data (layout only, not findings)
```

## Run

```bash
python3 tests/test_halflife.py                       # statistics tests
python3 -m halflife.simulate                         # only for a dry run
python3 -m halflife.analyze --data data --out out
python3 -m halflife.render --summary out/summary.json --out out
node render.js out/carousel.html out                 # PNGs at 2x + PDF for LinkedIn
```

## Status
- [x] Study design, analysis, statistical tests
- [x] Carousel (6 slides: decay curve as the hook, then churn, source type, engine, method, limits) and post copy generated from the results
- [x] Dry run on simulated data, watermarked
- [ ] SlateIndex export (see DATA_REQUEST.md)
- [ ] Real run, a sanity review of the numbers, then publish
