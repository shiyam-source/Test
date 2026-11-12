"""Build the carousel (HTML, rendered to PNG/PDF by render.js) and the post copy
from out/summary.json. Simulated data puts a watermark on every slide and a
banner on the post text.

    python -m halflife.render --summary out/summary.json --out out
    node render.js out/carousel.html out
"""
from __future__ import annotations

import argparse
import json
import os
import re

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OR, CHALK, GREY, PEACH = "#EE6216", "#F6F4F1", "#8C8882", "#FFAF85"
ENG = {"chatgpt": "ChatGPT", "perplexity": "Perplexity", "ai_mode": "Google AI Mode", "gemini": "Gemini", "claude": "Claude"}


def days(km):
    if km.get("half_life_days") is not None:
        return f"{km['half_life_days']:.0f}"
    return f">{(len(km['curve']) - 1) * 7}"


def cap(t):
    return t[:1].upper() + t[1:]


def pct(x):
    return "n/a" if x is None else f"{x * 100:.0f}%"


def curve_svg(s, W=860, H=560):
    X0, Y0, PW, PH = 70, 20, W - 110, H - 80
    kinds = [("brand", "Brand mentioned", OR, 3.2), ("domain", "Same domain cited", PEACH, 2.2), ("url", "Same URL cited", CHALK, 2.2)]
    maxw = max(len(s["overall"][k]["curve"]) for k, *_ in kinds) - 1
    sx = lambda t: X0 + t / maxw * PW
    sy = lambda v: Y0 + (1 - v) * PH
    g = ""
    for v in (0, .25, .5, .75, 1):
        g += f'<line x1="{X0}" x2="{X0 + PW}" y1="{sy(v):.1f}" y2="{sy(v):.1f}" stroke="#2A2A2A"/>'
        g += f'<text x="{X0 - 12}" y="{sy(v) + 5:.1f}" text-anchor="end" class="ax">{int(v * 100)}%</text>'
    for t in range(0, maxw + 1, 2 if maxw > 8 else 1):
        g += f'<text x="{sx(t):.1f}" y="{Y0 + PH + 26}" text-anchor="middle" class="ax">{t * 7}d</text>'
    g += f'<line x1="{X0}" x2="{X0 + PW}" y1="{sy(.5):.1f}" y2="{sy(.5):.1f}" stroke="{GREY}" stroke-dasharray="5 5"/>'
    g += f'<text x="{X0 + PW}" y="{sy(.5) - 8:.1f}" text-anchor="end" class="ax">half-life line</text>'
    labels, used = "", []
    for k, name, col, w in kinds:
        c = s["overall"][k]["curve"]
        pts = []
        for i, (t, v) in enumerate(c):  # step function
            if i:
                pts.append(f"{sx(t):.1f},{sy(c[i - 1][1]):.1f}")
            pts.append(f"{sx(t):.1f},{sy(v):.1f}")
        g += f'<polyline points="{" ".join(pts)}" fill="none" stroke="{col}" stroke-width="{w}"/>'
        med = s["overall"][k]["median_weeks"]
        if med is not None:
            g += f'<circle cx="{sx(med):.1f}" cy="{sy(.5):.1f}" r="6" fill="{col}" stroke="#111" stroke-width="2"/>'
        lt, lv = c[-1]
        ly = sy(lv) + 5
        while any(abs(ly - u) < 22 for u in used):
            ly -= 22
        used.append(ly)
        labels += f'<text x="{sx(lt) + 12:.1f}" y="{ly:.1f}" class="sl" fill="{col}">{name}</text>'
    return f'<svg width="{W + 150}" height="{H}" style="overflow:visible">{g}{labels}</svg>'


def bars(rows, mx, w=520, hi=None, unit="d"):
    out = ""
    for name, a, b in rows:
        out += f'<div class="eb"><div class="en">{name}</div><div class="ebars">'
        for val, col, lab in ((a, CHALK, "URL"), (b, OR, "brand")):
            ww = 0 if val is None else max(val / mx * w, 3)
            txt = "n/a" if val is None else f"{val:.0f}{unit}"
            out += f'<div class="ebr"><i style="width:{ww:.0f}px;background:{col}"></i><em>{txt}</em><small>{lab}</small></div>'
        out += "</div></div>"
    return out


def build(s: dict) -> tuple[str, str]:
    o = s["overall"]
    url_hl, dom_hl, br_hl = days(o["url"]), days(o["domain"]), days(o["brand"])
    ratio = s.get("brand_vs_url_ratio")
    ratio_txt = f"{ratio}×" if ratio else "n/a"
    sim = s.get("simulated")
    engines = [ENG.get(e, e) for e in s["engines"]]
    src = sorted(((k, v["half_life_days"]) for k, v in s["url_by_source"].items() if v["half_life_days"]), key=lambda x: -x[1])
    long_src, short_src = (src[0], src[-1]) if src else (("n/a", 0), ("n/a", 0))
    eng_rows = [(ENG.get(e, e), s["url_by_engine"][e]["half_life_days"], s["brand_by_engine"][e]["half_life_days"]) for e in s["engines"]]
    eng_max = max([v for _, a, b in eng_rows for v in (a, b) if v] + [1])
    src_rows = "".join(
        f'<div class="sr"><span>{cap(k)}</span><i style="width:{v / src[0][1] * 460:.0f}px;background:{OR if k == long_src[0] else (PEACH if k == short_src[0] else CHALK)}"></i><em>{v:.0f} days</em></div>'
        for k, v in src)
    surv_tbl = "".join(
        f'<tr><td>{lab}</td><td>{pct(o["url"][key])}</td><td>{pct(o["domain"][key])}</td><td class="o">{pct(o["brand"][key])}</td></tr>'
        for lab, key in (("after 1 week", "s1"), ("after 2 weeks", "s2"), ("after 4 weeks", "s4"), ("after 8 weeks", "s8")))
    churn = s["weekly_churn"]
    wm = '<div class="wm">SIMULATED DATA · LAYOUT PREVIEW · NOT A FINDING</div>' if sim else ""
    logo = re.sub(r'width="100%" height="100%" ', "", open(os.path.join(HERE, "assets/slate-logo.svg")).read(), count=1)
    N = 7

    def slide(i, kick, title, body, so=""):
        sw = '<span class="sw">swipe <b>→</b></span>' if i < N else '<span class="sw">end</span>'
        return f'''<section class="slide">{wm}<div class="prog"><i style="width:{i / N * 100:.1f}%"></i></div>
<div class="hdr"><div class="logo">{logo}</div><div class="pg">CITATION LAB · HALF-LIFE · {i:02d} / {N:02d}</div></div>
<div class="kick">{kick}</div><h2>{title}</h2><div class="body">{body}</div>
{f'<div class="so"><b>→</b> {so}</div>' if so else ''}
<div class="ftr"><span>SlateIndex · {s["collected"]:,} AI answers · {s["runs"]} weekly runs · {s["first_run"]} to {s["last_run"]}</span>{sw}</div></section>'''

    slides = [
        f'''<section class="slide cover">{wm}<div class="prog"><i style="width:{100 / N:.1f}%"></i></div>
<div class="hdr"><div class="logo">{logo}</div><div class="pg">CITATION LAB · HALF-LIFE · 01 / {N:02d}</div></div>
<div class="kick" style="margin-top:150px">SLATE CITATION LAB · THE HALF-LIFE OF AN AI CITATION</div>
<div class="cbig">Half of this week's AI citations are gone in <span>{url_hl} days</span>.</div>
<div class="cbig m">Brand mentions last <span>{ratio_txt}</span> longer.</div>
<div class="chips">{"".join(f"<span>{e}</span>" for e in engines)}</div>
<div class="clist"><div><b>{s["collected"]:,}</b> AI answers · <b>{s["runs"]}</b> weekly runs · <b>{s["prompts"]:,}</b> fixed prompts · <b>{s["categories"]}</b> categories</div>
<div>Survival analysis on every cited URL, domain and named brand</div></div>
<div class="cby"><span><b>Shiyam Sunder</b> · CEO, Slate</span><span class="sw">swipe <b>→</b></span></div></section>''',
        slide(2, "METHOD", "How we measured decay.", f'''<div class="steps">
<div class="st"><b>01</b><div><h4>Same prompts, every week</h4><p>{s["prompts"]:,} fixed buyer prompts across {s["categories"]} categories, run every Monday on {", ".join(engines)}. Answers collected from the consumer apps through data providers, not the APIs.</p></div></div>
<div class="st"><b>02</b><div><h4>Track every item's spell</h4><p>A spell is an unbroken run of weeks in which the same URL, domain or brand appears in the answer to the same prompt on the same engine.</p></div></div>
<div class="st"><b>03</b><div><h4>Strict rules for "gone"</h4><p>Gone = absent for 2 straight collected runs (one-week flickers don't count). A missing response is skipped, never counted as absent. Only spells that start after week 1 are used.</p></div></div>
<div class="st"><b>04</b><div><h4>Kaplan-Meier survival</h4><p>Half-life = median survival. Spells still alive at the last run are censored, not dropped. URL vs brand compared with a log-rank test.</p></div></div></div>''',
              f'{o["url"]["n_spells"]:,} URL spells and {o["brand"]["n_spells"]:,} brand spells analysed.'),
        slide(3, "FINDING 01 · THE DECAY CURVE", f'Citations fade in <span class="o">days</span>.<br>Brand mentions hold for weeks.',
              f'<div class="sh">SHARE OF SPELLS STILL ALIVE · BY DAYS SINCE FIRST APPEARANCE</div>{curve_svg(s)}'
              f'<div class="stats3"><div><b>{url_hl}d</b><span>half-life of a cited URL</span></div><div><b>{dom_hl}d</b><span>half-life of a cited domain</span></div><div><b class="o">{br_hl}d</b><span>half-life of a brand mention</span></div></div>',
              f'Same answers, same prompts. What the engine says about you outlives the page it cited.'),
        slide(4, "FINDING 02 · WEEKLY CHURN", f'<span class="o">{pct(churn.get("url"))}</span> of cited URLs are replaced<br>every single week.',
              f'''<div class="churn"><div><b>{pct(churn.get("url"))}</b><span>of URLs cited one week are gone the next</span></div><div><b>{pct(churn.get("domain"))}</b><span>of domains</span></div><div><b class="o">{pct(churn.get("brand"))}</b><span>of brands</span></div></div>
<div class="sh" style="margin-top:44px">STILL PRESENT AFTER…</div><table class="tb"><tr><th></th><th>URL</th><th>domain</th><th>brand</th></tr>{surv_tbl}</table>''',
              'A single weekly snapshot of "cited pages" is mostly noise. A brand-level trend is mostly signal.'),
        slide(5, "FINDING 03 · BY ENGINE", 'Every engine churns citations.<br>None of them churn the shortlist.',
              f'<div class="sh">HALF-LIFE IN DAYS · URL VS BRAND</div>{bars(eng_rows, eng_max)}',
              'The gap between citation churn and brand stability shows up on every engine.'),
        slide(6, "FINDING 04 · BY SOURCE TYPE", f'{cap(long_src[0])} citations last longest.<br><span class="o">{cap(short_src[0])} churns fastest.</span>',
              f'<div class="sh">URL CITATION HALF-LIFE BY SOURCE TYPE</div>{src_rows}'
              f'<div class="note" style="margin-top:20px">Source type from the cited domain: vendor sites (tracked brands\' own domains), review sites, community / UGC (Reddit, YouTube, LinkedIn, Quora…), and everything else.</div>',
              f'If you want citations that stick, {long_src[0]} pages hold on {long_src[1] / short_src[1]:.1f}× longer than {short_src[0]} ones.' if short_src[1] else ''),
        slide(7, "LIMITS · WHAT IT MEANS", 'Measure the shortlist, not the snapshot.',
              f'''<div class="g2"><div><div class="sh">WHAT TO DO WITH THIS</div>
<p class="li">Report citations on a rolling 4-week window, never a single week.</p>
<p class="li">Make brand mention rate the headline KPI; citations are the evidence underneath it.</p>
<p class="li">Read a lost citation as normal turnover unless it stays gone for 2+ weeks.</p></div>
<div><div class="sh">LIMITS</div>
<p class="li">{s["runs"]} weekly runs: spells longer than ~{s["runs"] - 1} weeks are censored, so the longest half-lives are lower bounds.</p>
<p class="li">One answer per prompt per engine per week: answer-to-answer variance and true decay can't be fully separated.</p>
<p class="li">Sensitivity: with no flicker tolerance, half-lives drop to {s["sensitivity_tol0"]["url"] * 7:.0f}d (URL) and {s["sensitivity_tol0"]["brand"] * 7:.0f}d (brand). The gap holds.</p></div></div>
<div class="credit">Data: SlateIndex, CC BY 4.0. Analysis by Slate research.</div>''', ''),
    ]
    css = open(os.path.join(HERE, "halflife/carousel.css")).read()
    html = f'<!doctype html><html><head><meta charset="utf-8"><style>{css}</style></head><body>{"".join(slides)}</body></html>'

    banner = "[SIMULATED DATA. LAYOUT PREVIEW ONLY. DO NOT POST THESE NUMBERS.]\n\n" if sim else ""
    post = f"""{banner}Half of this week's AI citations are gone in {url_hl} days.

Brand mentions last {ratio_txt} longer.

We tracked {s["prompts"]:,} fixed buyer prompts on {", ".join(engines)}, every week for {s["runs"]} weeks. Same prompts, same categories, answers collected from the consumer apps. Then we ran survival analysis on every cited URL, every cited domain and every brand named.

What decays:
→ A cited URL has a half-life of {url_hl} days.
→ A cited domain: {dom_hl} days.
→ A named brand: {br_hl} days.

Every week, {pct(churn.get("url"))} of cited URLs are replaced. Only {pct(churn.get("brand"))} of brands are.

After 4 weeks, {pct(o["url"]["s4"])} of URL citations are still there. {pct(o["brand"]["s4"])} of brand mentions are.

By source: {long_src[0]} citations last longest ({long_src[1]:.0f} days). {short_src[0]} churns fastest ({short_src[1]:.0f} days).

What I take from it:
A weekly "pages cited" report is mostly noise. Run it on a rolling 4-week window, and make brand mention rate the headline number. Citations are the evidence underneath it, and the evidence rotates. The verdict mostly doesn't.

Method, for the people who'll ask:
→ Kaplan-Meier survival. Half-life = median survival.
→ "Gone" = absent for 2 straight weekly runs, so one-week flickers don't count.
→ Missing responses are skipped, never counted as absent.
→ Only spells starting after week 1 are used. Spells still alive at the end are censored.
→ With zero flicker tolerance, half-lives drop to {s["sensitivity_tol0"]["url"] * 7:.0f} days (URL) and {s["sensitivity_tol0"]["brand"] * 7:.0f} days (brand). The gap holds.

Limits: {s["runs"]} weekly runs, so the longest half-lives are lower bounds. One answer per prompt per engine per week.

Data: SlateIndex (CC BY 4.0).

What's your citation-reporting window today? One week, or longer?"""
    return html, post


def main(argv=None):
    ap = argparse.ArgumentParser(); ap.add_argument("--summary", default="out/summary.json"); ap.add_argument("--out", default="out")
    a = ap.parse_args(argv)
    s = json.load(open(a.summary))
    html, post = build(s)
    open(f"{a.out}/carousel.html", "w").write(html)
    open(f"{a.out}/post.txt", "w").write(post)
    print(f"carousel -> {a.out}/carousel.html\npost     -> {a.out}/post.txt ({len(post)} chars)" + ("\n(SIMULATED - preview only)" if s.get("simulated") else ""))


if __name__ == "__main__":
    main()
