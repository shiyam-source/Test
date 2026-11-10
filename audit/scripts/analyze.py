import json, sys, collections, statistics as st
S = sys.argv[1]
d = json.load(open(f"{S}/crawl.json"))
C = collections.Counter
norm = lambda s: (s or "").strip()

print("URLs:", len(d))
print("prod status:", C(x["prod"].get("status") for x in d))
print("stg status:", C(x["stg"].get("status") for x in d))
for x in d:
    if x["stg"].get("status") != 200 or x["prod"].get("status") != 200:
        print("  STATUS DIFF", x["path"], x["prod"].get("status"), x["prod"].get("location"), "|", x["stg"].get("status"), x["stg"].get("location"))

ok = [x for x in d if x["stg"].get("status") == 200 and x["prod"].get("status") == 200]
fields = ["title", "desc", "canonical", "og_title", "og_image", "robots"]
diffs = collections.defaultdict(list)
for x in ok:
    p, s = x["prod"], x["stg"]
    for f in ["title", "desc", "og_title"]:
        if norm(p.get(f)) != norm(s.get(f)):
            diffs[f].append((x["path"], p.get(f), s.get(f)))
    pc, sc = norm(p.get("canonical")).rstrip("/"), norm(s.get("canonical")).rstrip("/")
    if pc != sc:
        diffs["canonical"].append((x["path"], p.get("canonical"), s.get("canonical")))
    if p.get("h1") != s.get("h1"):
        diffs["h1"].append((x["path"], p.get("h1"), s.get("h1")))
    if p.get("schema") != s.get("schema"):
        diffs["schema"].append((x["path"], p.get("schema"), s.get("schema")))
    if norm(p.get("robots")) != norm(s.get("robots")):
        diffs["robots"].append((x["path"], p.get("robots"), s.get("robots")))
    pw, sw = p.get("words", 0), s.get("words", 0)
    if pw and abs(pw - sw) / pw > 0.10:
        diffs["words>10%"].append((x["path"], pw, sw))
    if p.get("hreflang") != s.get("hreflang"):
        diffs["hreflang"].append((x["path"], p.get("hreflang"), s.get("hreflang")))
    if bool(p.get("og_image")) != bool(s.get("og_image")):
        diffs["og_image_presence"].append((x["path"], p.get("og_image"), s.get("og_image")))
    pl = {l.split("|")[1] for l in p.get("int_links", [])}
    sl = {l.split("|")[1] for l in s.get("int_links", [])}
    miss = pl - sl
    if miss:
        diffs["int_links_missing_on_stg"].append((x["path"], sorted(miss)[:8], len(miss)))

for k, v in diffs.items():
    print(f"\n### {k}: {len(v)} pages differ")
    for row in v[:12]:
        print("   ", row)

# Hosts staging links to
hosts = C()
for x in ok:
    for l in x["stg"].get("int_links", []):
        hosts[l.split("|")[0]] += 1
print("\nstg internal link hosts:", hosts)
hosts = C()
for x in ok:
    for l in x["prod"].get("int_links", []):
        hosts[l.split("|")[0]] += 1
print("prod internal link hosts:", hosts)

def agg(side):
    rows = [x[side] for x in ok]
    tot = lambda k: sum(r.get(k, 0) for r in rows)
    return dict(
        pages=len(rows),
        median_ttfb=st.median(r["ttfb_ms"] for r in rows),
        p90_ttfb=sorted(r["ttfb_ms"] for r in rows)[int(len(rows) * .9)],
        median_html_kb=round(st.median(r["bytes"] for r in rows) / 1024),
        imgs=tot("img_count"), no_alt=tot("img_no_alt"), empty_alt=tot("img_empty_alt"),
        lazy=tot("img_lazy"), no_dims=tot("img_no_dims"), srcset=tot("img_srcset"),
        no_h1=sum(1 for r in rows if not r.get("h1")), multi_h1=sum(1 for r in rows if len(r.get("h1") or []) > 1),
        no_desc=sum(1 for r in rows if not r.get("desc")), no_canon=sum(1 for r in rows if not r.get("canonical")),
        no_schema=sum(1 for r in rows if not r.get("schema")),
        median_scripts=st.median(r.get("scripts", 0) for r in rows),
        cache=C(r.get("cache") for r in rows).most_common(3),
        xrobots=C(r.get("x_robots") for r in rows).most_common(3),
        ctype=C(r.get("ctype") for r in rows).most_common(2),
        robots_meta=C(r.get("robots") for r in rows).most_common(3),
    )
print("\nPROD agg:", json.dumps(agg("prod"), indent=1, default=str))
print("STG agg:", json.dumps(agg("stg"), indent=1, default=str))
json.dump({k: v for k, v in diffs.items()}, open(f"{S}/diffs.json", "w"), default=str)
