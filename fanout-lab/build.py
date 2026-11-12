"""Build fanout-lab/fanout.html from the data below. Render: node render.js"""
import pathlib
ROOT = pathlib.Path(__file__).parent
logo = (ROOT.parent / "citation-halflife/assets/slate-logo.svg").read_text().replace('width="100%" height="100%"', '')

MODELS = ["ChatGPT", "Claude Haiku 4.5", "Claude Sonnet 5", "Claude Opus 5"]
# share of fan-out queries containing the modifier; None = not in that model's top 100
DATA = [
    ("Year mention", [24.6, 22.6, 35.7, 57.4]),
    ("“best”",       [10.1, 18.2, 23.7, 3.3]),
    ("“comparison”", [0.8, 5.5, 9.8, 3.8]),
    ("“review”",     [5.0, 1.4, 3.8, None]),
    ("“top”",        [None, 2.3, 4.6, None]),
    ("site:",        [20.4, None, None, None]),
    ("“official”",   [13.6, None, None, None]),
]
MAX, BARW = 57.4, 104

def cell(label, mi, v):
    if v is None:
        return '<div class="c na"><span>not in top 100</span></div>'
    tone = "or" if label == "Year mention" else ("pe" if mi == 0 and label in ("site:", "“official”") else "gr")
    w = max(3, round(v / MAX * BARW))
    return f'<div class="c {tone}"><i style="width:{w}px"></i><em>{v:.1f}%</em></div>'

rows = "".join(
    f'<div class="r{" hl" if lab == "Year mention" else ""}"><div class="lab">{lab}</div>' + "".join(cell(lab, i, v) for i, v in enumerate(vals)) + "</div>"
    for lab, vals in DATA)
head = '<div class="r h"><div class="lab"></div>' + "".join(f'<div class="c">{m.replace("Claude ", "Claude<br>")}</div>' for m in MODELS) + "</div>"

html = f"""<!doctype html><html><head><meta charset="utf-8"><style>
@font-face{{font-family:IT;font-weight:400;src:url(../citation-halflife/assets/fonts/inter-tight-latin-400-normal.woff2)}}
@font-face{{font-family:IT;font-weight:500;src:url(../citation-halflife/assets/fonts/inter-tight-latin-500-normal.woff2)}}
@font-face{{font-family:IT;font-weight:600;src:url(../citation-halflife/assets/fonts/inter-tight-latin-600-normal.woff2)}}
@font-face{{font-family:JB;font-weight:400;src:url(../citation-halflife/assets/fonts/jetbrains-mono-latin-400-normal.woff2)}}
@font-face{{font-family:JB;font-weight:500;src:url(../citation-halflife/assets/fonts/jetbrains-mono-latin-500-normal.woff2)}}
:root{{--bg:#111;--ink:#F6F4F1;--ink2:#B9B5AF;--mute:#8C8882;--grid:#2A2A2A;--or:#EE6216;--pe:#FFAF85}}
*{{box-sizing:border-box;margin:0;padding:0}}
body{{background:var(--bg);color:var(--ink);font-family:IT,sans-serif}}
.slide{{position:relative;width:1080px;height:1350px;padding:56px 64px;overflow:hidden}}
.hdr{{display:flex;justify-content:space-between;align-items:center}}
.hdr svg{{height:26px;width:auto;color:var(--ink)}}
.mono{{font-family:JB,monospace;font-size:13px;letter-spacing:2px;color:var(--mute)}}
.kick{{font-family:JB,monospace;font-size:14px;letter-spacing:2.5px;color:var(--or);margin-top:56px}}
h1{{font-size:64px;font-weight:600;letter-spacing:-2.2px;line-height:1.04;margin-top:16px}}
h1 b{{color:var(--or);font-weight:600}}
.sub{{font-size:26px;line-height:1.35;color:var(--ink2);margin-top:22px;max-width:900px}}
.tk code,.sub code{{font-family:JB,monospace;font-size:23px;color:var(--pe)}}
.grid{{margin-top:44px}}
.r{{display:grid;grid-template-columns:200px repeat(4,1fr);align-items:center;height:66px;border-top:1px solid var(--grid)}}
.r.h{{height:62px;border-top:none;align-items:end;padding-bottom:12px}}
.r.h .c{{font-family:JB,monospace;font-size:13px;letter-spacing:.5px;color:var(--ink2);line-height:1.35}}
.r.hl{{background:rgba(238,98,22,.08);border-top:1px solid rgba(238,98,22,.45);border-bottom:1px solid rgba(238,98,22,.45)}}
.lab{{font-size:22px;color:var(--ink2);padding-left:14px}}
.r.hl .lab{{color:var(--ink);font-weight:600}}
.c{{display:flex;align-items:center;gap:10px}}
.c i{{display:block;height:24px;border-radius:0 4px 4px 0}}
.c em{{font-style:normal;font-family:JB,monospace;font-size:19px}}
.c.or i{{background:var(--or)}} .c.or em{{color:var(--or);font-weight:500}}
.c.pe i{{background:var(--pe)}} .c.pe em{{color:var(--pe)}}
.c.gr i{{background:#5C5C64}} .c.gr em{{color:var(--ink2)}}
.c.na span{{font-family:JB,monospace;font-size:12px;color:#5f5c58;border:1px dashed #3d3d3d;border-radius:6px;padding:7px 10px}}
.tk{{margin-top:40px;display:grid;gap:18px}}
.tk div{{display:grid;grid-template-columns:44px 1fr;font-size:22px;line-height:1.38;color:var(--ink2)}}
.tk b{{font-family:JB,monospace;font-weight:500;color:var(--or);font-size:18px;padding-top:3px}}
.tk strong{{color:var(--ink);font-weight:600}}
.ftr{{position:absolute;left:64px;right:64px;bottom:44px;display:flex;justify-content:space-between;gap:30px;font-family:JB,monospace;font-size:11.5px;line-height:1.5;color:var(--mute);border-top:1px solid var(--grid);padding-top:16px}}
</style></head><body><section class="slide">
<div class="hdr">{logo}<span class="mono">SLATE LABS · FAN-OUT STUDY</span></div>
<div class="kick">WHAT AI MODELS ACTUALLY TYPE INTO SEARCH</div>
<h1>Claude Opus 5 puts a year in <b>57%</b> of its searches.</h1>
<p class="sub">ChatGPT reaches for <code>site:</code> and “official” instead. Neither makes the top 100 for any Claude model.</p>
<div class="grid">{head}{rows}</div>
<div class="tk">
<div><b>01</b><span><strong>Year is the #1 modifier in all four models.</strong> Haiku 23% → Sonnet 36% → Opus 57%. In seven weeks, those searches say 2027.</span></div>
<div><b>02</b><span><strong>ChatGPT goes to the source.</strong> 1 in 5 of its searches uses <code>site:</code> to target one domain. Your own site has to answer that query.</span></div>
<div><b>03</b><span><strong>“best” drops from 24% (Sonnet 5) to 3% (Opus 5).</strong> Listicle-shaped pages match some models’ searches, not others.</span></div>
</div>
<div class="ftr"><span>Share of fan-out queries containing each modifier.<br>Dashed = outside that model’s top 100 modifiers.</span><span style="text-align:right">Source: Slate Labs<br>slatehq.com</span></div>
</section></body></html>"""
(ROOT / "fanout.html").write_text(html)
print("wrote fanout.html")
