import json, os, re, subprocess, random
BASE = os.path.join(os.path.dirname(__file__), "..")
B = os.path.join(BASE, "build"); R = json.load(open(os.path.join(BASE, "data", "results.json")))

def dots():
    rnd = random.Random(42); out = ['<svg class="dots" viewBox="0 0 240 240" xmlns="http://www.w3.org/2000/svg">']
    for i in range(12):
        for j in range(12):
            x, y = 10 + i * 20, 10 + j * 20
            if rnd.random() < 0.3: out.append(f'<circle cx="{x}" cy="{y}" r="6.5" fill="#3987e5"/>')
            else: out.append(f'<circle cx="{x}" cy="{y}" r="6" fill="none" stroke="#3a5f91" stroke-width="1.2"/>')
    return "".join(out) + "</svg>"

def pct(x): return f"{x*100:.0f}%"
def rows(kind):
    h = []
    if kind == "leaderboard":
        for l in R["leaderboard"]:
            hl = ' class="hl"' if l["runs"] == 30 else ""
            h.append(f'<tr{hl}><td>{l["runs"]:,}</td><td class="r">{pct(l["leader_correct"])}</td><td class="r">{pct(l["true_leader_ranked_3rd_or_worse"])}</td><td class="r">{l["order_correct"]*100:.1f}%</td></tr>')
    elif kind == "plans":
        for p in R["plans"]:
            hl = ' class="hl"' if "focus" in p["plan"] else ""
            name = p["plan"].replace(" (removed Sep 2026)", " (removed)").replace(" / agency workspace", " / agency").replace(" allocation", "").replace("Growth, ", "Growth: ")
            h.append(f'<tr{hl}><td>{name}†</td><td class="r">{p["prompts"]}</td><td class="r">{p["engines"]}</td><td class="r">{p["runs"]}</td><td class="r">{p["answers"]:,}</td><td class="r">{pct(p["lo"])}–{pct(p["hi"])}</td><td class="r">{p["mdc"]*100:.0f} pts</td><td class="r">{p["mdc_pooled_engines"]*100:.0f} pts</td></tr>')
    elif kind == "decision":
        for d in R["decision_grade"]:
            m10 = f'{d["months_to_10pt_fixed_daily"]}' if d["months_to_10pt_fixed_daily"] else "—"
            m5 = f'{d["months_to_5pt_fixed_daily"]}' if d["months_to_5pt_fixed_daily"] else "—"
            h.append(f'<tr><td>{d["vendor"]}</td><td class="r">${d["per_answer"]:.3f}</td><td class="r">${d["cost_10pt"]:.2f}</td><td class="r">${d["cost_5pt"]:.2f}</td><td class="r">{m10}</td><td class="r">{m5}</td></tr>')
    elif kind == "vendors":
        for v in R["vendors"]:
            h.append(f'<tr><td>{v["vendor"]}</td><td class="r">${v["price"]:,}</td><td class="r">{v["prompts"] or "—"}</td><td class="r">{f"{v[chr(97)+chr(110)+chr(115)+chr(119)+chr(101)+chr(114)+chr(115)]:,}" if v["answers"] else "—"}</td><td>{v["note"]}</td></tr>')
    return "\n".join(h)

for name in ("coin-flip-report", "quota-tax-report"):
    s = open(os.path.join(B, name + ".html")).read()
    s = s.replace("{{dots}}", dots())
    s = re.sub(r"\{\{chart:(\w+)\}\}", lambda m: re.sub(r"<\?xml.*?\?>|<!DOCTYPE.*?>", "", open(os.path.join(B, "charts", m.group(1) + ".svg")).read(), flags=re.S), s)
    s = re.sub(r"\{\{rows:(\w+)\}\}", lambda m: rows(m.group(1)), s)
    open(os.path.join(B, name + ".rendered.html"), "w").write(s)
print("rendered")
