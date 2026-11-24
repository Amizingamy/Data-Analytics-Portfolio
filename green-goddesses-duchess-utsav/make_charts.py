"""Draws the case-study charts from the CSV files in data/. Run: python make_charts.py"""
import csv, pathlib
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

HERE = pathlib.Path(__file__).parent
RED, BLUE, GREY, INK = "#D9281C", "#2D5DB0", "#B8B0A9", "#2A1618"
plt.rcParams.update({"font.family": "DejaVu Sans", "axes.edgecolor": INK, "text.color": INK,
                     "axes.labelcolor": INK, "xtick.color": INK, "ytick.color": INK})

def rows(name):
    with open(HERE / "data" / name, newline="") as f:
        return list(csv.DictReader(f))

def clean(ax):
    for s in ("top", "right", "left"):
        ax.spines[s].set_visible(False)
    ax.set_yticks([])

def save(fig, name):
    fig.savefig(HERE / "charts" / name, dpi=200, bbox_inches="tight", facecolor="white")
    plt.close(fig)

# 1. before / after
ba = {r["metric"]: r for r in rows("before_after.csv")}
fig, axes = plt.subplots(1, 3, figsize=(10, 4.2))
spec = [("views", "Views", "about 1,700", "521,057", "300x"),
        ("interactions", "Interactions", "35", "4,387", "125x"),
        ("net_follower_change", "Net follower change", "+3", "+284", None)]
for ax, (k, title, lab0, lab1, mult) in zip(axes, spec):
    a, b = float(ba[k]["previous_two_months"]), float(ba[k]["campaign_27aug_25sep"])
    ax.bar([0, 1], [a, b], color=[GREY, RED], width=.62)
    ax.set_ylim(0, b * 1.22)
    ax.text(0, a + b * .02, lab0, ha="center", va="bottom", fontsize=10)
    ax.text(1, b + b * .02, lab1, ha="center", va="bottom", fontsize=11, fontweight="bold")
    ax.set_xticks([0, 1]); ax.set_xticklabels(["Previous\ntwo months", "27 Aug to\n25 Sep"], fontsize=9)
    ax.set_title(title + (f"  ({mult})" if mult else ""), fontsize=11, loc="left", fontweight="bold")
    clean(ax)
fig.suptitle("Green Goddesses Instagram: before vs during the Duchess Utsav campaign", fontsize=12, x=.01, ha="left")
fig.tight_layout(); save(fig, "before_after.png")

# 2. paid vs organic
po = rows("paid_vs_organic.csv")
fig, ax = plt.subplots(figsize=(10, 3.2))
labels = {"views": "Views", "new_follows": "New follows"}
for i, r in enumerate(reversed(po)):
    p, o = float(r["paid_pct"]), float(r["organic_pct"])
    ax.barh(i, p, color=RED, height=.55); ax.barh(i, o, left=p, color=BLUE, height=.55)
    ax.text(p / 2, i, f"Promoted  {p:.0f}%", ha="center", va="center", color="white", fontsize=11, fontweight="bold")
    ax.text(p + o / 2, i, f"Organic  {o:.0f}%", ha="center", va="center", color="white", fontsize=10, fontweight="bold")
ax.set_yticks(range(len(po))); ax.set_yticklabels([labels[r["measure"]] for r in reversed(po)], fontsize=11)
ax.set_xlim(0, 100); ax.set_xticks([]); ax.spines[["top", "right", "bottom"]].set_visible(False)
ax.set_title("3 promoted posts drove most views and new follows", fontsize=12, loc="left", fontweight="bold")
fig.tight_layout(); save(fig, "paid_vs_organic.png")

# 3. formats
fm = rows("formats.csv")
fig, (a1, a2) = plt.subplots(1, 2, figsize=(10, 3.9), gridspec_kw={"width_ratios": [1.2, 1]})
vals = [float(r["interactions"]) for r in fm]
bars = a1.bar([r["format"] for r in fm], vals, color=[RED, GREY, GREY], width=.6)
for b, v in zip(bars, vals):
    a1.text(b.get_x() + b.get_width() / 2, v + 25, f"{v:,.0f}", ha="center", fontsize=11, fontweight="bold")
a1.set_ylim(0, 2100); a1.set_title("Interactions by format", fontsize=11, loc="left", fontweight="bold"); clean(a1)
labs = ["Shares", "Saves"]; rv = [float(fm[0]["shares"]), float(fm[0]["saves"])]; pv = [float(fm[1]["shares"]), float(fm[1]["saves"])]
x = [0, 1]
for xi, r, p in zip(x, rv, pv):
    a2.bar(xi - .19, r, .34, color=RED); a2.bar(xi + .19, p, .34, color=GREY)
    a2.text(xi - .19, r + 4, f"{r:.0f}", ha="center", fontsize=10, fontweight="bold"); a2.text(xi + .19, p + 4, f"{p:.0f}", ha="center", fontsize=10)
a2.set_xticks(x); a2.set_xticklabels(labs, fontsize=10); a2.set_ylim(0, 290)
a2.set_title("Reels (red) vs posts (grey)", fontsize=11, loc="left", fontweight="bold"); clean(a2)
fig.tight_layout(); save(fig, "interactions_by_format.png")

# 4. views by post
tp = rows("top_posts.csv")
fig, ax = plt.subplots(figsize=(10, 3.4))
names = {"promoted": RED, "organic": BLUE}
for i, r in enumerate(reversed(tp)):
    v = float(r["views"]); ax.barh(i, v, color=names[r["type"]], height=.55)
    ax.text(v + 3000, i, f"{v:,.0f}  ({r['type']})", va="center", fontsize=10)
ax.set_yticks(range(len(tp))); ax.set_yticklabels([r["post"] for r in reversed(tp)], fontsize=10)
ax.set_xlim(0, 400000); ax.set_xticks([]); ax.spines[["top", "right", "bottom"]].set_visible(False)
ax.set_title("Views on the standout posts", fontsize=12, loc="left", fontweight="bold")
fig.tight_layout(); save(fig, "views_by_post.png")
print("charts done")
