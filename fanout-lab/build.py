"""Fan-out modifier ranks per model -> fanout.html. Render with: node render.js [dpr]"""
import pathlib
ROOT = pathlib.Path(__file__).parent
F = "../citation-halflife/assets/fonts/"

MODELS = ["ChatGPT", "Claude Haiku 4.5", "Claude Sonnet 5", "Claude Opus 5"]
# ranked lists from the study: (modifier, share of fan-out queries %). Then modifiers outside the top 100.
RANKS = [
    ([("year", 24.6), ("site", 20.4), ("official", 13.6), ("best", 10.1), ("review", 5.0), ("comparison", 0.8)], ["top"]),
    ([("year", 22.6), ("best", 18.2), ("comparison", 5.5), ("top", 2.3), ("review", 1.4)], ["site", "official"]),
    ([("year", 35.7), ("best", 23.7), ("comparison", 9.8), ("top", 4.6), ("review", 3.8)], ["site", "official"]),
    ([("year", 57.4), ("comparison", 3.8), ("best", 3.3)], ["site", "official", "review", "top"]),
]
LABEL = {"year": "Year mention", "site": "site:", "official": "“official”", "best": "“best”",
         "review": "“review”", "comparison": "“comparison”", "top": "“top”"}
# stroke, bar tint, value colour, line width
STYLE = {"year": ("#EE6216", "#FCD9C4", "#C94A0A", 3.2),
         "best": ("#141414", "#E4E2DF", "#141414", 2.2),
         "comparison": ("#6E6E78", "#E9E9EC", "#55555E", 2.2),
         "review": ("#A6A6AE", "#EFEFF1", "#6E6E78", 1.8),
         "top": ("#A6A6AE", "#EFEFF1", "#6E6E78", 1.8),
         "site": ("#E0704A", "#FBE3D9", "#B8502C", 0),
         "official": ("#E0704A", "#FBE3D9", "#B8502C", 0)}

W, PW, PH, PITCH, TOP = 968, 206, 56, 74, 60
GAP = (W - 4 * PW) / 3
cx = lambda i: i * (PW + GAP)
cy = lambda r: TOP + r * PITCH
FULL = 60.0  # bar scale: 60% share = full pill

svg, lines, pos = [], [], [{} for _ in MODELS]
for i, m in enumerate(MODELS):
    svg.append(f'<text x="{cx(i)+2}" y="22" class="mh">{m}</text>')
    present, absent = RANKS[i]
    for r, (k, v) in enumerate(present):
        x, y = cx(i), cy(r); st, tint, vc, _ = STYLE[k]; pos[i][k] = y + PH / 2
        bw = max(0, v / FULL * (PW - 3))
        svg.append(f'<clipPath id="c{i}{r}"><rect x="{x}" y="{y}" width="{PW}" height="{PH}" rx="9"/></clipPath>'
                   f'<rect x="{x}" y="{y}" width="{PW}" height="{PH}" rx="9" fill="#fff"/>'
                   f'<rect x="{x}" y="{y}" width="{bw:.1f}" height="{PH}" fill="{tint}" clip-path="url(#c{i}{r})"/>'
                   f'<rect x="{x}" y="{y}" width="{PW}" height="{PH}" rx="9" fill="none" stroke="{st}" stroke-width="{2 if k=="year" else 1.4}"/>'
                   f'<text x="{x+12}" y="{y+34}" class="rk">{r+1}</text>'
                   f'<text x="{x+28}" y="{y+34.5}" class="lb{" yr" if k=="year" else ""}">{LABEL[k]}</text>'
                   f'<text x="{x+PW-12}" y="{y+34.5}" class="pc" text-anchor="end" fill="{vc}">{v:.1f}%</text>')
    for j, k in enumerate(absent):
        x, y = cx(i), cy(len(present) + j)
        svg.append(f'<rect x="{x+.5}" y="{y+.5}" width="{PW-1}" height="{PH-1}" rx="9" fill="#FAFAF9" stroke="#C9C9CE" stroke-dasharray="4 4"/>'
                   f'<text x="{x+16}" y="{y+34}" class="na">{LABEL[k]}</text>'
                   f'<text x="{x+PW-12}" y="{y+34}" class="nat" text-anchor="end">not in top 100</text>')
for i in range(3):
    for k, y1 in pos[i].items():
        if k in pos[i + 1] and STYLE[k][3]:
            y2 = pos[i + 1][k]; x1, x2 = cx(i) + PW, cx(i + 1); mx = (x1 + x2) / 2
            lines.append(f'<path d="M{x1},{y1} C{mx},{y1} {mx},{y2} {x2},{y2}" fill="none" stroke="{STYLE[k][0]}" stroke-width="{STYLE[k][3]}"/>')
H = cy(7) + 4
chart = f'<svg width="{W}" height="{H}" viewBox="0 0 {W} {H}">{"".join(lines)}{"".join(svg)}</svg>'

html = f"""<!doctype html><html><head><meta charset="utf-8"><style>
@font-face{{font-family:IT;font-weight:400;src:url({F}inter-tight-latin-400-normal.woff2)}}
@font-face{{font-family:IT;font-weight:500;src:url({F}inter-tight-latin-500-normal.woff2)}}
@font-face{{font-family:IT;font-weight:600;src:url({F}inter-tight-latin-600-normal.woff2)}}
@font-face{{font-family:JB;font-weight:400;src:url({F}jetbrains-mono-latin-400-normal.woff2)}}
@font-face{{font-family:JB;font-weight:500;src:url({F}jetbrains-mono-latin-500-normal.woff2)}}
*{{box-sizing:border-box;margin:0;padding:0}}
body{{background:#fff;color:#141414;font-family:IT,sans-serif}}
.slide{{position:relative;width:1080px;height:1350px;padding:60px 56px;background:#fff;overflow:hidden}}
.top{{display:flex;justify-content:space-between;font-family:JB,monospace;font-size:13px;letter-spacing:1.6px;color:#8A8A92}}
.top b{{color:#EE6216;font-weight:500}}
h1{{font-size:64px;font-weight:600;letter-spacing:-2px;line-height:1.05;margin-top:46px;max-width:930px}}
h1 em{{font-style:normal;color:#EE6216}}
.sub{{font-size:24px;line-height:1.4;color:#55555E;margin-top:20px;max-width:900px}}
.stats code,.sub code{{font-family:JB,monospace;font-size:21px;color:#141414;background:#F3F2F0;padding:1px 6px;border-radius:4px}}
.chart{{margin-top:46px}}
svg .mh{{font-family:JB,monospace;font-size:15px;font-weight:500;fill:#141414;letter-spacing:.3px}}
svg .rk{{font-family:JB,monospace;font-size:13px;fill:#9A9AA2}}
svg .lb{{font-family:IT;font-size:17.5px;font-weight:600;fill:#141414}}
svg .lb.yr{{fill:#141414}}
svg .pc{{font-family:JB,monospace;font-size:15px;letter-spacing:-.3px;font-weight:500}}
svg .na{{font-family:IT;font-size:16px;font-weight:500;fill:#A6A6AE}}
svg .nat{{font-family:JB,monospace;font-size:11.5px;fill:#AEAEB5}}
.key{{font-family:JB,monospace;font-size:12.5px;color:#8A8A92;margin-top:16px;display:flex;gap:28px}}
.key i{{display:inline-block;width:26px;height:11px;border-radius:2px;background:#FCD9C4;border:1px solid #EE6216;vertical-align:-1px;margin-right:8px}}
.key s{{display:inline-block;width:26px;height:11px;border-radius:2px;border:1px dashed #C9C9CE;vertical-align:-1px;margin-right:8px;text-decoration:none}}
.stats{{display:grid;grid-template-columns:repeat(3,1fr);margin-top:44px;border-top:1.5px solid #141414}}
.stats code{{font-size:16px !important}}
.stats div{{padding:22px 24px 0 0}}
.stats div+div{{padding-left:24px;border-left:1px solid #E4E2DF}}
.stats b{{display:block;font-family:JB,monospace;font-size:40px;font-weight:500;letter-spacing:-1px;color:#141414}}
.stats b.o{{color:#EE6216}}
.stats span{{display:block;font-size:19px;line-height:1.4;color:#55555E;margin-top:10px}}
.ftr{{position:absolute;left:56px;right:56px;bottom:46px;display:flex;justify-content:space-between;font-family:JB,monospace;font-size:12px;color:#8A8A92}}
</style></head><body><section class="slide">
<div class="top"><span><b>SLATE LABS</b> / QUERY FAN-OUT</span><span>4 MODELS · TOP MODIFIERS, RANKED</span></div>
<h1>Claude Opus 5 puts a year in <em>57%</em> of its searches.</h1>
<p class="sub">What each model adds when it rewrites a prompt into search queries. ChatGPT reaches for <code>site:</code> and “official”. No Claude model does.</p>
<div class="chart">{chart}
<div class="key"><span><i></i>fill = share of fan-out queries containing the modifier</span><span><s></s>not in the model’s top 100</span></div></div>
<div class="stats">
<div><b class="o">22.6 → 57.4%</b><span>queries with a year, Haiku 4.5 → Opus 5. It grows with model size.</span></div>
<div><b>20.4%</b><span>of ChatGPT queries use <code>site:</code> to target one domain. Not in any Claude model’s top 100.</span></div>
<div><b>23.7 → 3.3%</b><span>“best”, Sonnet 5 → Opus 5. Opus drops the buyer phrasing.</span></div>
</div>
<div class="ftr"><span>Slate Labs fan-out query study</span><span>slatehq.com</span></div>
</section></body></html>"""
(ROOT / "fanout.html").write_text(html)
print("wrote fanout.html")
