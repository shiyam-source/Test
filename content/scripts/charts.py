import json, os, math
import numpy as np
import matplotlib
matplotlib.use("svg")
import matplotlib.pyplot as plt
from matplotlib import font_manager

BASE = os.path.join(os.path.dirname(__file__), "..")
R = json.load(open(os.path.join(BASE, "data", "results.json")))
OUT = os.path.join(BASE, "build", "charts"); os.makedirs(OUT, exist_ok=True)

for f in font_manager.findSystemFonts():
    if "Inter" in f: font_manager.fontManager.addfont(f)
INK, INK2, MUTED, GRID = "#0b0b0b", "#52514e", "#8a8984", "#e6e5e1"
SLATE, PROF, AQUA, YEL, GRAY = "#2a78d6", "#eb6834", "#1baf7a", "#eda100", "#b9b8b2"
plt.rcParams.update({"font.family": "Inter", "svg.fonttype": "none", "font.size": 9.5, "text.color": INK,
    "axes.labelcolor": INK2, "xtick.color": INK2, "ytick.color": INK2, "axes.edgecolor": GRID,
    "axes.spines.top": False, "axes.spines.right": False, "axes.spines.left": False,
    "axes.grid": True, "grid.color": GRID, "grid.linewidth": 0.6, "axes.axisbelow": True,
    "xtick.major.size": 0, "ytick.major.size": 0, "figure.facecolor": "white", "axes.facecolor": "white"})

def save(fig, name):
    fig.savefig(os.path.join(OUT, name + ".svg"), bbox_inches="tight", pad_inches=0.08); plt.close(fig)

def pct(ax, axis="y"):
    fmt = matplotlib.ticker.FuncFormatter(lambda v, _: f"{v*100:.0f}%")
    (ax.yaxis if axis == "y" else ax.xaxis).set_major_formatter(fmt)

def wilson(p, n, z=1.959964):
    d = 1 + z*z/n; c = (p + z*z/(2*n))/d; h = z*math.sqrt(p*(1-p)/n + z*z/(4*n*n))/d
    return c-h, c+h

# C1 interval band vs runs
ns = np.unique(np.round(np.logspace(np.log10(5), 3, 200)).astype(int))
lo = [wilson(0.3, n)[0] for n in ns]; hi = [wilson(0.3, n)[1] for n in ns]
fig, ax = plt.subplots(figsize=(6.6, 3.3))
ax.fill_between(ns, lo, hi, color=SLATE, alpha=0.16, lw=0)
ax.plot(ns, lo, color=SLATE, lw=1.6); ax.plot(ns, hi, color=SLATE, lw=1.6)
ax.axhline(0.3, color=INK2, lw=1, ls=(0, (3, 3)))
ax.set_xscale("log"); ax.set_xlim(5, 1000); ax.set_ylim(0, 0.72); pct(ax)
ax.set_xticks([7, 30, 60, 100, 250, 1000]); ax.set_xticklabels(["7", "30", "60", "100", "250", "1,000"])
for n, lab in ((7, "7-day trial\n9%–65%"), (30, "Daily for a month\n17%–48%"), (100, "100 runs\n22%–40%"), (1000, "1,000 runs\n27%–33%")):
    a, b = wilson(0.3, n); ax.plot([n, n], [a, b], color=INK, lw=2, solid_capstyle="round")
    ax.annotate(lab, (n, b), xytext=(0, 6), textcoords="offset points", ha="center" if n not in (1000,) else "right", fontsize=8.2, color=INK)
ax.text(5.4, 0.315, "True rate: 30%", fontsize=8, color=INK2)
ax.set_xlabel("AI answers sampled for one prompt on one engine (log scale)"); ax.set_ylabel("95% range of the reported rate")
save(fig, "c1_interval_band")

# C2 phantom moves
ph = R["phantom"]
fig, ax = plt.subplots(figsize=(6.6, 2.4))
labels = ["7 runs", "30 runs\n(daily)", "60 runs", "100 runs", "250 runs"]
vals = [p["phantom_10pt"] for p in ph]; v20 = [p["phantom_20pt"] for p in ph]
x = np.arange(len(vals))
ax.bar(x - 0.19, vals, 0.36, color=SLATE, label="Swing of 10+ points", zorder=2)
ax.bar(x + 0.19, v20, 0.36, color=PROF, label="Swing of 20+ points", zorder=2)
for i, (a, b) in enumerate(zip(vals, v20)):
    ax.text(i - 0.19, a + 0.015, f"{a*100:.0f}%", ha="center", fontsize=8.2, color=INK)
    ax.text(i + 0.19, b + 0.015, f"{b*100:.0f}%" if b >= 0.005 else "<1%", ha="center", fontsize=8.2, color=INK)
ax.set_xticks(x); ax.set_xticklabels(labels); ax.set_ylim(0, 0.85); pct(ax); ax.grid(axis="x", visible=False)
ax.set_ylabel("Share of prompt-months"); ax.legend(frameon=False, loc="upper right", fontsize=8.5)
save(fig, "c2_phantom_moves")

# C3 leaderboard
lb = R["leaderboard"]
fig, ax = plt.subplots(figsize=(6.6, 2.9))
xs = [l["runs"] for l in lb]
ax.plot(xs, [l["leader_correct"] for l in lb], color=SLATE, lw=2, marker="o", ms=6, mec="white", mew=1.5)
ax.plot(xs, [l["true_leader_ranked_3rd_or_worse"] for l in lb], color=PROF, lw=2, marker="o", ms=6, mec="white", mew=1.5)
ax.set_xscale("log"); ax.set_xticks(xs); ax.set_xticklabels([f"{x:,}" for x in xs]); ax.set_ylim(0, 1); pct(ax)
ax.annotate("True leader shown at #1", (250, lb[-2]["leader_correct"]), xytext=(-8, 6), textcoords="offset points", ha="right", fontsize=8.4, color=INK)
ax.annotate("True leader shown at #3 or lower", (7, lb[0]["true_leader_ranked_3rd_or_worse"]), xytext=(4, 8), textcoords="offset points", fontsize=8.4, color=INK)
for l in lb:
    if l["runs"] == 30:
        ax.annotate(f"{l['leader_correct']*100:.0f}%", (30, l["leader_correct"]), xytext=(0, 8), textcoords="offset points", ha="center", fontsize=8.2)
        ax.annotate(f"{l['true_leader_ranked_3rd_or_worse']*100:.0f}%", (30, l["true_leader_ranked_3rd_or_worse"]), xytext=(0, -14), textcoords="offset points", ha="center", fontsize=8.2)
ax.set_xlabel("AI answers per brand per month (log scale)"); ax.set_ylabel("Share of simulated months")
save(fig, "c3_leaderboard")

# C4 clusters
cl = R["clusters"]
fig, ax = plt.subplots(figsize=(6.6, 2.7))
labs = [f"{c['prompts_in_cluster']} prompt{'s' if c['prompts_in_cluster']>1 else ''}\n{c['answers_per_month']:,} answers" for c in cl]
v = [c["approx_mdc"] for c in cl]
ax.bar(range(len(v)), v, 0.55, color=SLATE, zorder=2)
for i, a in enumerate(v): ax.text(i, a + 0.005, f"{a*100:.0f} pts", ha="center", fontsize=8.5)
ax.set_xticks(range(len(v))); ax.set_xticklabels(labs); ax.grid(axis="x", visible=False)
ax.yaxis.set_major_formatter(matplotlib.ticker.FuncFormatter(lambda x, _: f"{x*100:.0f} pts")); ax.set_ylim(0, 0.22)
ax.set_ylabel("Smallest reliable change")
save(fig, "c4_clusters")

# C5 one prompt vs brand topline, constant truth
rng = np.random.default_rng(7)
true = rng.beta(3, 7, size=(100, 3)); true[0, :] = 0.30
obs = rng.binomial(30, np.repeat(true[None], 12, 0)) / 30
months = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
one = obs[:, 0, 0]; brand = obs.mean(axis=(1, 2))
fig, ax = plt.subplots(figsize=(6.6, 2.45))
ax.axhline(0.30, color=INK2, lw=1, ls=(0, (3, 3)))
ax.plot(range(12), one, color=PROF, lw=2, marker="o", ms=6, mec="white", mew=1.5)
ax.plot(range(12), brand, color=SLATE, lw=2)
ax.set_xticks(range(12)); ax.set_xticklabels(months); ax.set_ylim(0, 0.62); pct(ax); ax.grid(axis="x", visible=False)
i_max = int(np.argmax(one)); i_min = int(np.argmin(one))
ax.annotate(f"{one[i_max]*100:.0f}%", (i_max, one[i_max]), xytext=(0, 7), textcoords="offset points", ha="center", fontsize=8.2)
ax.annotate(f"{one[i_min]*100:.0f}%", (i_min, one[i_min]), xytext=(0, -13), textcoords="offset points", ha="center", fontsize=8.2)
ax.text(11.25, one[-1] - 0.04, "One prompt,\none engine", fontsize=8.2, va="center", color=INK)
ax.text(11.25, brand[-1] + 0.06, "Brand-wide\naverage", fontsize=8.2, va="center", color=INK)
ax.text(0, 0.56, "Dashed line = true rate (30%), constant all year", fontsize=8, color=INK2)
ax.set_xlim(-0.4, 12.6); ax.set_ylabel("Reported appearance rate")
save(fig, "c5_one_prompt")
json.dump({"one_prompt": [round(float(x), 3) for x in one], "brand": [round(float(x), 4) for x in brand]}, open(os.path.join(BASE, "data", "c5_series.json"), "w"))

# Q1 cost per answer
vend = [v for v in R["vendors"] if v["per_answer"] and v["vendor"] != "Otterly Lite"]
vend.append(dict(vendor="Slate Growth (net of credits)", per_answer=round(124/10000, 4)))
vend = sorted(vend, key=lambda v: v["per_answer"])
def color(n): return SLATE if n.startswith("Slate") else (PROF if n.startswith("Profound") else GRAY)
fig, ax = plt.subplots(figsize=(6.6, 3.5))
y = np.arange(len(vend))
ax.barh(y, [v["per_answer"] for v in vend], 0.6, color=[color(v["vendor"]) for v in vend], zorder=2)
for i, v in enumerate(vend): ax.text(v["per_answer"] + 0.0012, i, f"${v['per_answer']:.3f}", va="center", fontsize=8.3)
ax.set_yticks(y); ax.set_yticklabels([v["vendor"] for v in vend]); ax.grid(axis="y", visible=False)
ax.xaxis.set_major_formatter(matplotlib.ticker.FuncFormatter(lambda x, _: f"${x:.2f}")); ax.set_xlim(0, 0.095)
ax.set_xlabel("List price per sampled AI answer (USD)")
save(fig, "q1_per_answer")

# Q2 cost per prompt
vp = sorted([v for v in R["vendors"] if v["per_prompt"]], key=lambda v: v["per_prompt"])
fig, ax = plt.subplots(figsize=(6.6, 3.1))
y = np.arange(len(vp))
ax.barh(y, [v["per_prompt"] for v in vp], 0.6, color=[color(v["vendor"]) for v in vp], zorder=2)
for i, v in enumerate(vp): ax.text(v["per_prompt"] + 0.05, i, f"${v['per_prompt']:.2f}", va="center", fontsize=8.3)
ax.set_yticks(y); ax.set_yticklabels([v["vendor"] for v in vp]); ax.grid(axis="y", visible=False)
ax.xaxis.set_major_formatter(matplotlib.ticker.FuncFormatter(lambda x, _: f"${x:.0f}")); ax.set_xlim(0, 4.7)
ax.set_xlabel("List price per tracked prompt per month (USD)")
save(fig, "q2_per_prompt")

# Q3 time to a decision-grade reading (±5 pts, 323 answers)
need = R["n_for_halfwidth"]["5pt"]
designs = [("1 prompt, 1 engine,\nonce a day", need / 30), ("1 prompt, 3 engines\npooled, once a day", need / 90),
           ("1 prompt, 4 engines,\n3 runs a day", need / 360), ("10-prompt topic,\n3 engines, once a day", need / 900)]
fig, ax = plt.subplots(figsize=(6.6, 2.3))
cols = [PROF, GRAY, SLATE, SLATE]
ax.bar(range(4), [d[1] for d in designs], 0.55, color=cols, zorder=2)
for i, d in enumerate(designs):
    lab = f"{d[1]:.1f} months" if d[1] >= 1 else f"{d[1]*30:.0f} days"
    ax.text(i, d[1] + 0.2, lab, ha="center", fontsize=8.5)
ax.set_xticks(range(4)); ax.set_xticklabels([d[0] for d in designs]); ax.grid(axis="x", visible=False)
ax.set_ylabel("Time to a ±5-point reading"); ax.set_ylim(0, 12.5)
ax.yaxis.set_major_formatter(matplotlib.ticker.FuncFormatter(lambda x, _: f"{x:.0f} mo"))
save(fig, "q3_time_to_confidence")

# Q4 agency
ag = R["agency"]; c = [a["clients"] for a in ag]
fig, ax = plt.subplots(figsize=(6.6, 3.2))
ax.plot(c, [a["profound"] for a in ag], color=PROF, lw=2)
ax.plot(c, [a["otterly_standard"] for a in ag], color=AQUA, lw=2)
ax.plot(c, [a["peec_starter"] for a in ag], color=YEL, lw=2)
ax.plot(c, [a["slate_agency_reported"] for a in ag], color=SLATE, lw=2, ls=(0, (5, 3)))
ax.text(30.4, ag[-1]["profound"], "Profound agency\n$99 + $399/client", va="center", fontsize=8.2)
ax.text(30.4, ag[-1]["otterly_standard"], "Otterly Standard\n$189/client", va="center", fontsize=8.2)
ax.text(30.4, ag[-1]["peec_starter"] + 450, "Peec Starter\n$95/client", va="center", fontsize=8.2)
ax.text(30.4, 1150, "Slate Agency, reported\n$2,000 flat (allowances\nunverified)", va="center", fontsize=8.2)
ax.scatter([10], [4089], s=40, color=PROF, edgecolor="white", lw=1.5, zorder=3)
ax.annotate("10 clients: $4,089/mo", (10, 4089), xytext=(-8, 10), textcoords="offset points", ha="right", fontsize=8.3)
ax.set_xlim(1, 30); ax.set_ylim(0, 12500); ax.set_xlabel("Client workspaces"); ax.set_ylabel("Monthly tracking cost")
ax.yaxis.set_major_formatter(matplotlib.ticker.FuncFormatter(lambda x, _: f"${x/1000:.0f}k" if x else "$0"))
save(fig, "q4_agency")
print("charts:", sorted(os.listdir(OUT)))
