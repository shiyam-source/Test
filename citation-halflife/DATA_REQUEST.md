# Data request: SlateIndex run history for the citation half-life study

**For:** whoever owns the SlateIndex database (the collection and publishing pipeline).
**Why:** the public site shows trends for the last 9 runs only and doesn't list cited URLs per run. The study needs the raw per-response records for **every weekly run since launch**.

## What to export: 4 CSV files, UTF-8, with headers

### 1. `responses.csv`: one row per *scheduled* response

| column | type | example | notes |
|---|---|---|---|
| `response_id` | string | `r_8812031` | unique |
| `run_date` | date | `2026-11-09` | the Monday the run started (IST) |
| `engine` | string | `chatgpt` / `perplexity` / `ai_mode` | |
| `category` | string | `product-analytics` | |
| `prompt_id` | string | `p_4471` | **stable across runs**; the same prompt must keep the same id |
| `intent` | string | `commercial` | informational / commercial / transactional / navigational |
| `collected` | 0/1 | `1` | 0 = scheduled but not collected (missing). **Include missing rows**: the analysis needs them to tell "absent" from "not collected" |

### 2. `citations.csv`: one row per cited source in a collected response

| column | type | example |
|---|---|---|
| `response_id` | string | `r_8812031` |
| `url` | string | `https://www.g2.com/categories/product-analytics` |

Raw URLs as returned are fine. The analysis normalises them (host lowercased, `www.` and trailing slash stripped; query strings are already ignored). If the provider returns the citation's position or index, add a `position` column. It's optional.

### 3. `mentions.csv`: one row per tracked brand named in a collected response

| column | type | example |
|---|---|---|
| `response_id` | string | `r_8812031` |
| `brand` | string | `amplitude` |
| `position` | int | `1` |

Use the same deterministic mention extraction the index already uses.

### 4. `brands.csv`: the brand roster

| column | type | example |
|---|---|---|
| `brand` | string | `amplitude` |
| `domain` | string | `amplitude.com` |

This is used to classify citations as "vendor site" vs review, community or media.

## Scope and checks

- **All runs since launch.** Weekly runs started around mid-August 2026, so roughly 12–14 runs by now.
- **Keep prompt ids stable.** If a prompt's wording changed, either give it a new id or flag it. A reworded prompt silently changes what gets cited.
- **Flag runs with known problems:** the 2 Nov citation-authority restatement doesn't affect this study, but provider outages or partial runs do. A `notes.csv` with `run_date,engine,note` is enough.
- **Rough size:** about 990 prompts × 3 engines × ~13 runs ≈ 39k responses, ~400k citation rows and ~200k mention rows. It's a few tens of MB of CSV.

## What happens next

Drop the four files into `citation-halflife/data/` (and delete the `SIMULATED` marker file), then run:

```bash
python3 -m halflife.analyze --data data --out out
python3 -m halflife.render --summary out/summary.json --out out
node render.js out/carousel.html out
```

Every number on the carousel and in the post copy updates from the real data, and the "SIMULATED" watermark disappears.
