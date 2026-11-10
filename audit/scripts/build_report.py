"""Build the audit report HTML from the collected data."""
import json, sys, base64, io, collections, statistics as st
from PIL import Image

S = sys.argv[1]
OUTFILE = sys.argv[2]
lh = json.load(open(f"{S}/lh_summary.json"))
resp = json.load(open(f"{S}/responsive.json"))
for _r in resp:  # tracking pixels blocked by the audit sandbox are not real broken images
    if _r.get("broken"):
        _r["broken"] = [u for u in _r["broken"] if "track.gif" not in u and "slatehq" not in u]

PAGES = [
    ("home", "/", "Homepage"),
    ("saas-seo-agency", "/saas-seo-agency", "Service page"),
    ("industries_fintech-seo-agency", "/industries/fintech-seo-agency", "Industry page"),
    ("about", "/about", "About"),
    ("blog", "/blog", "Blog index"),
    ("blog_aeo-vs-seo", "/blog/aeo-vs-seo", "Blog post"),
    ("customers_locus", "/customers/locus", "Case study"),
    ("research_saas-ppc-2026-report", "/research/saas-ppc-2026-report", "Research report"),
    ("tools_acv-calculator", "/tools/acv-calculator", "Calculator tool"),
    ("coach", "/coach", "Coach (webinar) index"),
]


def g(slug, form, site):
    return lh[f"{slug}|{form}|{site}"]


def esc(s):
    return (str(s).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;"))


# ---------- metric table ----------
def cell(prd, stg, kind):
    """kind: 'score' (higher better), 'ms'/'s'/'cls'/'kb' (lower better)."""
    if kind == "score":
        d = stg - prd
        better = d > 2
        worse = d < -2
        txt_p, txt_s = f"{prd:.0f}", f"{stg:.0f}"
        delta = f"{d:+.0f}"
    else:
        d = stg - prd
        thr = {"s": 0.15, "ms": 30, "cls": 0.01, "kb": 50}[kind]
        better = d < -thr
        worse = d > thr
        if kind == "s":
            txt_p, txt_s, delta = f"{prd:.2f}s", f"{stg:.2f}s", f"{d:+.2f}s"
        elif kind == "ms":
            txt_p, txt_s, delta = f"{prd:.0f}", f"{stg:.0f}", f"{d:+.0f}"
        elif kind == "cls":
            txt_p, txt_s, delta = f"{prd:.3f}", f"{stg:.3f}", f"{d:+.3f}"
        else:
            txt_p, txt_s, delta = f"{prd/1024:.1f}", f"{stg/1024:.1f}", f"{d/1024:+.1f}"
    cls = "good" if better else "bad" if worse else "flat"
    return f'<td class="num">{txt_p}</td><td class="num"><span class="pill {cls}">{txt_s}</span></td>'


def perf_table(form):
    rows = []
    for slug, path, label in PAGES:
        p, s = g(slug, form, "prd"), g(slug, form, "stg")
        rows.append(
            f'<tr><th scope="row"><span class="tpl">{label}</span><code>{path}</code></th>'
            + cell(p["perf"], s["perf"], "score")
            + cell(p["lcp"] / 1000, s["lcp"] / 1000, "s")
            + cell(p["tbt"], s["tbt"], "ms")
            + cell(p["cls"], s["cls"], "cls")
            + cell(p["fcp"] / 1000, s["fcp"] / 1000, "s")
            + cell(p["kb"], s["kb"], "kb")
            + "</tr>")
    head = ('<thead><tr><th rowspan="2">Page</th><th colspan="2">Perf score</th><th colspan="2">LCP</th>'
            '<th colspan="2">TBT (ms)</th><th colspan="2">CLS</th><th colspan="2">FCP</th><th colspan="2">Weight (MB)</th></tr>'
            '<tr class="sub">' + '<th>Live</th><th>Staging</th>' * 6 + '</tr></thead>')
    return f'<div class="tablewrap"><table class="perf">{head}<tbody>{"".join(rows)}</tbody></table></div>'


def tally(form, key, higher_better):
    w = l = t = 0
    thr = {"perf": 2, "lcp": 150, "tbt": 30, "cls": 0.01, "kb": 50}[key]
    for slug, _, _ in PAGES:
        p, s = g(slug, form, "prd")[key], g(slug, form, "stg")[key]
        d = (s - p) if higher_better else (p - s)
        if d > thr: w += 1
        elif d < -thr: l += 1
        else: t += 1
    return w, l, t


T = {f"{form}_{k}": tally(form, k, k == "perf") for form in ("mobile", "desktop") for k in ("perf", "lcp", "tbt", "cls", "kb")}

# ---------- LCP dumbbell chart (mobile) ----------
def lcp_chart():
    W, rowh, left, right, top = 760, 34, 190, 30, 34
    H = top + rowh * len(PAGES) + 30
    maxv = 13
    x = lambda v: left + (W - left - right) * v / maxv
    out = [f'<svg viewBox="0 0 {W} {H}" role="img" aria-label="Mobile LCP per page, live versus staging" class="chart">']
    # thresholds
    for v, lab, anchor, dx in ((2.5, "Good ≤ 2.5s", "end", -5), (4.0, "Poor > 4s", "start", 5)):
        out.append(f'<line x1="{x(v):.1f}" x2="{x(v):.1f}" y1="{top-14}" y2="{H-26}" class="thr"/>'
                   f'<text x="{x(v)+dx:.1f}" y="{top-18}" text-anchor="{anchor}" class="thrlab">{lab}</text>')
    for v in range(0, maxv + 1, 2):
        out.append(f'<line x1="{x(v):.1f}" x2="{x(v):.1f}" y1="{top-6}" y2="{H-26}" class="grid"/>'
                   f'<text x="{x(v):.1f}" y="{H-10}" class="axis" text-anchor="middle">{v}s</text>')
    for i, (slug, path, label) in enumerate(PAGES):
        y = top + rowh * i + rowh / 2
        p, s = g(slug, "mobile", "prd")["lcp"] / 1000, g(slug, "mobile", "stg")["lcp"] / 1000
        cls = "good" if s < p - 0.15 else "bad" if s > p + 0.15 else "flat"
        out.append(f'<text x="{left-12}" y="{y+4:.1f}" text-anchor="end" class="rowlab">{label}</text>')
        out.append(f'<line x1="{x(min(p,s)):.1f}" x2="{x(max(p,s)):.1f}" y1="{y:.1f}" y2="{y:.1f}" class="bar {cls}"/>')
        out.append(f'<circle cx="{x(p):.1f}" cy="{y:.1f}" r="6" class="dot prd"><title>Live {p:.2f}s</title></circle>')
        out.append(f'<circle cx="{x(s):.1f}" cy="{y:.1f}" r="6" class="dot stg {cls}"><title>Staging {s:.2f}s</title></circle>')
        lx = x(max(p, s)) + 10
        out.append(f'<text x="{lx:.1f}" y="{y+4:.1f}" class="vlab">{p:.1f} → {s:.1f}s</text>')
    out.append("</svg>")
    return "".join(out)


# ---------- responsive ----------
VPN = {"m360": "360 phone", "m390": "390 phone", "t768": "768 tablet", "d1024": "1024 laptop", "d1440": "1440 desktop"}
R = collections.defaultdict(dict)
for r in resp:
    R[(r["path"], r["vp"])][r["site"]] = r


def resp_table():
    rows = []
    for slug, path, label in PAGES:
        tds = []
        for vp in VPN:
            d = R.get((path, vp), {})
            p, s, df = d.get("prd", {}), d.get("stg", {}), d.get("diff", {})
            if "error" in s or not s:
                tds.append('<td><span class="pill bad">error</span></td>'); continue
            issues = []
            if s.get("hOverflow"): issues.append(f"overflow {s['sw']}px")
            if s.get("broken"): issues.append(f"{len(s['broken'])} broken img")
            hp, hs = p.get("height", 0), s.get("height", 0)
            hd = (hs - hp) / hp * 100 if hp else 0
            fd = df.get("foldDiffPct")
            regress = [i for i in issues if not (p.get("hOverflow") and i.startswith("overflow"))]
            status = "bad" if regress else ("warn" if abs(hd) > 5 or (fd or 0) > 8 else "good")
            txt = ", ".join(issues) if issues else "OK"
            sub = f"fold diff {fd:.1f}% · height {hd:+.0f}%" if fd is not None else f"height {hd:+.0f}%"
            tds.append(f'<td><span class="pill {status}">{esc(txt)}</span><small>{sub}</small></td>')
        rows.append(f'<tr><th scope="row"><span class="tpl">{label}</span><code>{path}</code></th>{"".join(tds)}</tr>')
    head = "<thead><tr><th>Page</th>" + "".join(f"<th>{v}</th>" for v in VPN.values()) + "</tr></thead>"
    return f'<div class="tablewrap"><table class="resp">{head}<tbody>{"".join(rows)}</tbody></table></div>'


def resp_stats():
    stg = [r for r in resp if r["site"] == "stg" and "error" not in r]
    prd = [r for r in resp if r["site"] == "prd" and "error" not in r]
    f = lambda rows, k: sum(1 for r in rows if r.get(k))
    diffs = [r["foldDiffPct"] for r in resp if r["site"] == "diff"]
    return dict(
        combos=len(stg), stg_overflow=f(stg, "hOverflow"), prd_overflow=f(prd, "hOverflow"),
        stg_broken=sum(len(r.get("broken", [])) for r in stg), prd_broken=sum(len(r.get("broken", [])) for r in prd),
        stg_small=round(st.mean(r.get("smallTargets", 0) for r in stg), 1), prd_small=round(st.mean(r.get("smallTargets", 0) for r in prd), 1),
        stg_tiny=round(st.mean(r.get("tinyText", 0) for r in stg), 1), prd_tiny=round(st.mean(r.get("tinyText", 0) for r in prd), 1),
        median_diff=round(st.median(diffs), 2) if diffs else None, max_diff=max(diffs) if diffs else None,
        stg_err=sum(1 for r in stg if r.get("jsErrors")), prd_err=sum(1 for r in prd if r.get("jsErrors")),
        overflow_list=sorted({(r["path"], r["vp"], r["sw"], tuple(r.get("offenders", [])[:3])) for r in stg if r.get("hOverflow")}),
        prd_overflow_list=sorted({(r["path"], r["vp"]) for r in prd if r.get("hOverflow")}),
        js_errs=sorted({(r["path"], e) for r in stg for e in r.get("jsErrors", [])})[:8],
        prd_js_errs=sorted({(r["path"], e) for r in prd for e in r.get("jsErrors", [])})[:8],
    )


RS = resp_stats()


def thumb(path, w=340, crop_h=None):
    im = Image.open(path).convert("RGB")
    if crop_h:
        im = im.crop((0, 0, im.width, min(im.height, crop_h)))
    r = w / im.width
    im = im.resize((w, int(im.height * r)), Image.LANCZOS)
    b = io.BytesIO(); im.save(b, "JPEG", quality=70, optimize=True)
    return "data:image/jpeg;base64," + base64.b64encode(b.getvalue()).decode()


def shots():
    out = []
    for slug, path, label in PAGES[:6]:
        a = f"{S}/resp/{slug}__m390__prd.png"; b = f"{S}/resp/{slug}__m390__stg.png"
        try:
            out.append(f'<figure class="shot"><figcaption>{label} · 390px</figcaption><div class="pair">'
                       f'<div><img src="{thumb(a, 220)}" alt="Live {label} on a 390px phone" loading="lazy"><span>Live</span></div>'
                       f'<div><img src="{thumb(b, 220)}" alt="Staging {label} on a 390px phone" loading="lazy"><span>Staging</span></div>'
                       f'</div></figure>')
        except FileNotFoundError:
            pass
    return "".join(out)


data = dict(T=T, RS=RS)
json.dump(data, open(f"{S}/report_data.json", "w"), indent=1, default=str)

tpl = open(f"{S}/scripts/report_template.html").read()
html = (tpl.replace("{{PERF_MOBILE}}", perf_table("mobile"))
        .replace("{{PERF_DESKTOP}}", perf_table("desktop"))
        .replace("{{LCP_CHART}}", lcp_chart())
        .replace("{{RESP_TABLE}}", resp_table())
        .replace("{{SHOTS}}", shots()))
for k, v in T.items():
    html = html.replace("{{%s_W}}" % k, str(v[0])).replace("{{%s_L}}" % k, str(v[1])).replace("{{%s_T}}" % k, str(v[2]))
for k, v in RS.items():
    html = html.replace("{{RS_%s}}" % k, esc(v) if not isinstance(v, list) else esc(v))
open(OUTFILE, "w").write(html)
print("written", OUTFILE, len(html) // 1024, "KB")
print(json.dumps(T)); print(json.dumps({k: v for k, v in RS.items()}, default=str)[:3000])
