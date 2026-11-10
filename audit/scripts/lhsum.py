import json, glob, sys, os, statistics as st, collections
S = sys.argv[1]
rows = collections.defaultdict(list)
for f in glob.glob(f"{S}/lhr/*.json"):
    slug, site, form, i = os.path.basename(f)[:-5].split("__")
    try:
        j = json.load(open(f))
    except Exception:
        continue
    if j.get("runtimeError"):
        print("RTERR", f, j["runtimeError"]); continue
    a = j["audits"]; c = j["categories"]
    num = lambda k: a[k].get("numericValue")
    items = a["network-requests"]["details"]["items"]
    tw = sum(x.get("transferSize", 0) for x in items)
    byt = collections.Counter()
    for x in items:
        byt[x.get("resourceType")] += x.get("transferSize", 0)
    rows[(slug, form, site)].append(dict(
        perf=c["performance"]["score"] * 100, a11y=c["accessibility"]["score"] * 100,
        bp=c["best-practices"]["score"] * 100, seo=c["seo"]["score"] * 100,
        fcp=num("first-contentful-paint"), lcp=num("largest-contentful-paint"), tbt=num("total-blocking-time"),
        cls=num("cumulative-layout-shift"), si=num("speed-index"), ttfb=num("server-response-time"),
        kb=tw / 1024, reqs=len(items), js=byt["Script"] / 1024, img=byt["Image"] / 1024, css=byt["Stylesheet"] / 1024,
        font=byt["Font"] / 1024, dom=a["dom-size"].get("numericValue"),
        lcp_el=(a.get("largest-contentful-paint-element", {}).get("details", {}).get("items", [{}])[0].get("items", [{}])[0].get("node", {}).get("snippet", "") if a.get("largest-contentful-paint-element", {}).get("details") else ""),
        bootup=num("bootup-time"), mainthread=num("mainthread-work-breakdown"),
        unused_js=(a.get("unused-javascript", {}).get("details", {}) or {}).get("overallSavingsBytes", 0) / 1024,
        unused_css=(a.get("unused-css-rules", {}).get("details", {}) or {}).get("overallSavingsBytes", 0) / 1024,
        fails=[k for k, v in a.items() if v.get("score") is not None and v.get("score") < 0.9 and v.get("scoreDisplayMode") in ("binary", "numeric", "metricSavings")],
    ))
summary = {}
for k, v in sorted(rows.items()):
    med = {m: st.median(r[m] for r in v) for m in v[0] if isinstance(v[0][m], (int, float))}
    med["n"] = len(v)
    med["lcp_el"] = v[0]["lcp_el"][:160]
    med["fails"] = sorted(set.intersection(*[set(r["fails"]) for r in v]))
    summary["|".join(k)] = med
json.dump(summary, open(f"{S}/lh_summary.json", "w"), indent=1)
hdr = "page form site n perf a11y bp seo FCP LCP TBT CLS SI TTFB KB reqs JS IMG DOM"
print(hdr)
for k, m in summary.items():
    print(k.replace("|", " "), m["n"], *[int(m[x]) for x in ["perf", "a11y", "bp", "seo"]],
          *[f"{m[x]/1000:.2f}s" for x in ["fcp", "lcp"]], f"{m['tbt']:.0f}ms", f"{m['cls']:.3f}", f"{m['si']/1000:.2f}s", f"{m['ttfb']:.0f}",
          *[int(m[x]) for x in ["kb", "reqs", "js", "img", "dom"]])
