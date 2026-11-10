"""Parity crawl: fetch every production sitemap URL on both hosts and extract SEO fields."""
import json, re, sys, time, concurrent.futures as cf
from urllib.parse import urlparse, urljoin
import requests
from bs4 import BeautifulSoup

S = sys.argv[1]  # scratchpad dir
UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0 Safari/537.36 TDAuditBot"
PROD = "https://www.tripledart.com"
STG = "https://staging.tripledart.com"

xml = open(f"{S}/raw/www.tripledart.com_sitemap.xml").read()
paths = sorted({urlparse(u).path.rstrip("/") or "/" for u in re.findall(r"<loc>(.*?)</loc>", xml)})

sess = requests.Session()
sess.headers["User-Agent"] = UA


def extract(base, path):
    url = base + path
    rec = {"url": url}
    for attempt in range(3):
        try:
            t = time.time()
            r = sess.get(url, allow_redirects=False, timeout=30)
            rec["ttfb_ms"] = int(r.elapsed.total_seconds() * 1000)
            break
        except Exception as e:
            rec["error"] = str(e)
            time.sleep(2)
    else:
        return rec
    rec["status"] = r.status_code
    rec["location"] = r.headers.get("location")
    rec["x_robots"] = r.headers.get("x-robots-tag")
    rec["cf_cache"] = r.headers.get("cf-cache-status")
    rec["cache"] = r.headers.get("cache-control")
    rec["ctype"] = r.headers.get("content-type")
    rec["bytes"] = len(r.content)
    if r.status_code != 200 or "html" not in (rec["ctype"] or ""):
        return rec
    html = r.content.decode("utf-8", "replace")
    soup = BeautifulSoup(html, "lxml")
    g = lambda sel, attr="content": (soup.select_one(sel) or {}).get(attr) if soup.select_one(sel) else None
    rec["title"] = soup.title.get_text(strip=True) if soup.title else None
    rec["desc"] = g('meta[name="description"]')
    rec["robots"] = g('meta[name="robots"]')
    rec["canonical"] = g('link[rel="canonical"]', "href")
    rec["og_title"] = g('meta[property="og:title"]')
    rec["og_image"] = g('meta[property="og:image"]')
    rec["og_url"] = g('meta[property="og:url"]')
    rec["hreflang"] = [l.get("hreflang") for l in soup.select('link[rel="alternate"][hreflang]')]
    rec["h1"] = [h.get_text(" ", strip=True) for h in soup.find_all("h1")]
    rec["h2_count"] = len(soup.find_all("h2"))
    schema = []
    for s in soup.select('script[type="application/ld+json"]'):
        try:
            d = json.loads(s.string or "")
            items = d.get("@graph", [d]) if isinstance(d, dict) else d
            for it in items if isinstance(items, list) else [items]:
                t = it.get("@type") if isinstance(it, dict) else None
                schema += t if isinstance(t, list) else [t]
        except Exception as e:
            schema.append("INVALID_JSON")
            rec.setdefault("schema_err", []).append(str(e)[:120])
    rec["schema"] = sorted(str(x) for x in schema)
    imgs = soup.find_all("img")
    rec["img_count"] = len(imgs)
    rec["img_no_alt"] = sum(1 for i in imgs if i.get("alt") is None)
    rec["img_empty_alt"] = sum(1 for i in imgs if i.get("alt") == "")
    rec["img_lazy"] = sum(1 for i in imgs if i.get("loading") == "lazy")
    rec["img_no_dims"] = sum(1 for i in imgs if not (i.get("width") and i.get("height")))
    rec["img_srcset"] = sum(1 for i in imgs if i.get("srcset"))
    links = set()
    for a in soup.find_all("a", href=True):
        h = a["href"].strip()
        if h.startswith(("mailto:", "tel:", "#", "javascript:")):
            continue
        u = urlparse(urljoin(base + path, h))
        if u.netloc in ("www.tripledart.com", "staging.tripledart.com", "tripledart.com", "new.tripledart.com"):
            links.add(f"{u.netloc}|{u.path.rstrip('/') or '/'}")
    rec["int_links"] = sorted(links)
    for s in soup(["script", "style", "noscript"]):
        s.decompose()
    rec["words"] = len(soup.get_text(" ", strip=True).split())
    rec["scripts"] = len(BeautifulSoup(html, "lxml").find_all("script"))
    return rec


def both(path):
    return {"path": path, "prod": extract(PROD, path), "stg": extract(STG, path)}


out = []
with cf.ThreadPoolExecutor(8) as ex:
    for i, res in enumerate(ex.map(both, paths)):
        out.append(res)
        if i % 50 == 0:
            print(i, res["path"], res["prod"].get("status"), res["stg"].get("status"), flush=True)
json.dump(out, open(f"{S}/crawl.json", "w"))
print("done", len(out))
