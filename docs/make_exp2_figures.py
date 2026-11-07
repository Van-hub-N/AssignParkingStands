import json
import os
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter, LogLocator

ROOT = Path(__file__).resolve().parents[1]
RESULTS = ROOT / "results"
FIG = ROOT / "docs" / "figures"
FIG.mkdir(parents=True, exist_ok=True)

plt.rcParams.update({
    "font.family": "Noto Sans CJK SC",
    "font.size": 10,
    "axes.unicode_minus": False,
    "axes.edgecolor": "#777777",
    "axes.linewidth": 0.8,
    "axes.grid": True,
    "grid.color": "#D9D9D9",
    "grid.linewidth": 0.6,
    "grid.alpha": 0.8,
    "figure.dpi": 200,
    "savefig.dpi": 200,
    "savefig.bbox": "tight",
})

BLUE = "#4472C4"
ORANGE = "#ED7D31"
GREEN = "#70AD47"
GRAY = "#A5A5A5"
RED = "#C00000"
LIGHT_BLUE = "#DDEBF7"
LIGHT_ORANGE = "#FCE4D6"

with open(RESULTS / "backtracking_stats.json", encoding="utf-8") as f:
    stats = json.load(f)


def kfmt(x, pos=None):
    if x >= 1_000_000:
        return f"{x/1_000_000:.1f}M"
    if x >= 1_000:
        return f"{x/1_000:.0f}k"
    return f"{x:.0f}"


def bar_labels(ax, bars, labels, color="black", fontsize=8, dy=0.02):
    for b, lab in zip(bars, labels):
        ax.annotate(lab, (b.get_x() + b.get_width()/2, b.get_height()),
                    xytext=(0, 3), textcoords="offset points",
                    ha="center", va="bottom", fontsize=fontsize, color=color)


def style(ax):
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.tick_params(colors="#333333", labelsize=9)
    ax.set_axisbelow(True)


# ---------------------------------------------------------------- exact growth
by_k = stats["exact_by_k"]
ks = [str(k) for k in range(5, 12)]
rows = [by_k[k] for k in ks]
nodes = [r["mean_nodes"] for r in rows]
times = [r["mean_time"] for r in rows]
max_nodes = [r["max_nodes"] for r in rows]
limit_counts = [r["node_limit"] + r["time_limit"] for r in rows]

fig, axes = plt.subplots(1, 2, figsize=(10.2, 4.1))
ax = axes[0]
bars = ax.bar(ks, nodes, color=[BLUE if c == 0 else ORANGE for c in limit_counts],
              edgecolor="white", linewidth=0.8, width=0.66)
ax.set_yscale("log")
ax.set_ylim(50, 2.5e7)
ax.yaxis.set_major_formatter(FuncFormatter(kfmt))
ax.set_xlabel("飞机数 K")
ax.set_ylabel("平均搜索结点数（对数轴）")
ax.set_title("(a) 平均结点数随 K 增长", fontsize=11, pad=8)
ax.grid(axis="y", which="major", color="#D9D9D9", linewidth=0.6)
ax.grid(axis="y", which="minor", visible=False)
for b, v, lim in zip(bars, nodes, limit_counts):
    lab = kfmt(v)
    if lim:
        lab = f"{lab}\n({lim}例触顶)"
    ax.annotate(lab, (b.get_x()+b.get_width()/2, b.get_height()),
                xytext=(0, 4), textcoords="offset points", ha="center", va="bottom",
                fontsize=7.8, color=RED if lim else "#333333")
style(ax)

ax = axes[1]
bars = ax.bar(ks, times, color=[BLUE if c == 0 else ORANGE for c in limit_counts],
              edgecolor="white", linewidth=0.8, width=0.66)
ax.set_yscale("log")
ax.set_ylim(0.002, 200)
ax.set_xlabel("飞机数 K")
ax.set_ylabel("平均单案例耗时 / ms（对数轴）")
ax.set_title("(b) 平均耗时随 K 增长", fontsize=11, pad=8)
ax.grid(axis="y", which="major", color="#D9D9D9", linewidth=0.6)
ax.grid(axis="y", which="minor", visible=False)
for b, v, lim in zip(bars, times, limit_counts):
    lab = f"{v:.3f}" if v < 1 else f"{v:.1f}"
    if lim:
        lab = f"{lab}\n({lim}例触顶)"
    ax.annotate(lab, (b.get_x()+b.get_width()/2, b.get_height()),
                xytext=(0, 4), textcoords="offset points", ha="center", va="bottom",
                fontsize=7.8, color=RED if lim else "#333333")
style(ax)
fig.text(0.5, -0.035, "K≤10 时全部案例完成搜索；K=11 时 14/100 例达到 1000 万结点上限。",
         ha="center", fontsize=8.6, color="#555555")
fig.tight_layout(w_pad=2.0)
fig.savefig(FIG / "exact_growth.png", facecolor="white")
plt.close(fig)

# ----------------------------------------------------------- exact improvement
improved_rate = [r["improved"] / r["cases"] * 100 for r in rows]
gap_improve = [-r["gap"] for r in rows]
max_gap = [r["max_gap"] for r in rows]

fig, axes = plt.subplots(1, 3, figsize=(10.6, 3.9))
for ax, vals, title, color, fmt in [
    (axes[0], improved_rate, "(a) 改进案例占比", GREEN, "{:.1f}%"),
    (axes[1], gap_improve, "(b) 总目标值下降", BLUE, "{:.2f}%"),
    (axes[2], max_gap, "(c) 单案例最大改进", ORANGE, "{:.1f}%"),
]:
    bars = ax.bar(ks, vals, color=color, edgecolor="white", linewidth=0.8, width=0.66, alpha=0.92)
    ax.set_xlabel("飞机数 K")
    ax.set_ylabel("%")
    ax.set_title(title, fontsize=10.8, pad=8)
    ax.set_ylim(0, max(vals) * 1.22 if max(vals) > 0 else 1)
    bar_labels(ax, bars, [fmt.format(v) for v in vals], fontsize=7.6)
    style(ax)
axes[1].set_ylim(0, max(gap_improve) * 1.22)
axes[0].set_ylim(0, max(improved_rate) * 1.25)
axes[2].set_ylim(0, max(max_gap) * 1.18)
fig.text(0.5, -0.04, "每一组 K 的案例数：K=5/6 各 400，K=7 300，K=8 100，K=9 500，K=10 200，K=11 100；K=11 含 14 个结点受限案例。",
         ha="center", fontsize=8.2, color="#555555")
fig.tight_layout(w_pad=1.8)
fig.savefig(FIG / "exact_improvement.png", facecolor="white")
plt.close(fig)

# -------------------------------------------------------------- scalability
groups = ["K13-15", "K16-80", "K81-499"]
grows = [stats["scalability_groups"][g] for g in groups]
cases = [r["cases"] for r in grows]
opt = [r["optimal"] for r in grows]
lim = [r["node_limit"] + r["time_limit"] for r in grows]
gap = [-r["gap"] for r in grows]
mtime = [r["mean_time"] for r in grows]

fig, axes = plt.subplots(1, 3, figsize=(10.8, 4.0))
ax = axes[0]
b1 = ax.bar(groups, opt, color=BLUE, edgecolor="white", linewidth=0.8, width=0.58, label="完成搜索")
b2 = ax.bar(groups, lim, bottom=opt, color=ORANGE, edgecolor="white", linewidth=0.8, width=0.58, label="结点受限")
for i, (o, l, c) in enumerate(zip(opt, lim, cases)):
    if o:
        ax.annotate(f"{o} 最优", (i, o/2), ha="center", va="center", color="white", fontsize=8.5, fontweight="bold")
    if l:
        ax.annotate(f"{l} 受限", (i, o + l/2), ha="center", va="center", color="white", fontsize=8.5, fontweight="bold")
    ax.annotate(f"{o}/{c}", (i, c), xytext=(0, 4), textcoords="offset points", ha="center", fontsize=8)
ax.set_ylim(0, max(cases) * 1.18)
ax.set_ylabel("案例数")
ax.set_title("(a) 搜索完成情况", fontsize=10.8, pad=8)
ax.legend(fontsize=7.8, frameon=False, loc="upper right")
style(ax)

ax = axes[1]
bars = ax.bar(groups, gap, color=GREEN, edgecolor="white", linewidth=0.8, width=0.58)
ax.set_ylabel("总目标值下降 / %")
ax.set_title("(b) 相对贪心的目标值改进", fontsize=10.8, pad=8)
ax.set_ylim(0, max(gap) * 1.25)
bar_labels(ax, bars, [f"-{v:.2f}%" for v in gap], fontsize=8)
style(ax)

ax = axes[2]
bars = ax.bar(groups, mtime, color=GRAY, edgecolor="white", linewidth=0.8, width=0.58)
ax.set_ylabel("平均单案例耗时 / ms")
ax.set_title("(c) 平均耗时", fontsize=10.8, pad=8)
ax.set_ylim(0, max(mtime) * 1.22)
bar_labels(ax, bars, [f"{v:.1f}" for v in mtime], fontsize=8)
style(ax)
fig.text(0.5, -0.04, "每组参数：时间上限 1000 ms、结点上限 500 万；实际均由结点上限触发，未触发时间上限。",
         ha="center", fontsize=8.2, color="#555555")
fig.tight_layout(w_pad=1.8)
fig.savefig(FIG / "scalability_status.png", facecolor="white")
plt.close(fig)

# ------------------------------------------------------------------- stress
names = ["小", "中", "大"]
srows = [stats["stress_by_scale"][k] for k in ["small", "medium", "large"]]
scases = [r["cases"] for r in srows]
sopt = [r["optimal"] for r in srows]
slim = [r["node_limit"] + r["time_limit"] for r in srows]
srate = [r["improved"] / r["cases"] * 100 for r in srows]
sgap = [-r["gap"] for r in srows]
stime = [r["mean_time"] for r in srows]

fig, axes = plt.subplots(1, 3, figsize=(10.8, 4.0))
ax = axes[0]
ax.bar(names, sopt, color=BLUE, edgecolor="white", linewidth=0.8, width=0.55, label="完成搜索")
ax.bar(names, slim, bottom=sopt, color=ORANGE, edgecolor="white", linewidth=0.8, width=0.55, label="结点受限")
for i, (o, l, c) in enumerate(zip(sopt, slim, scases)):
    if o:
        ax.annotate(f"{o}", (i, o/2), ha="center", va="center", color="white", fontsize=8, fontweight="bold")
    ax.annotate(f"{l}", (i, o + l/2), ha="center", va="center", color="white", fontsize=8, fontweight="bold")
    ax.annotate(f"{c}", (i, c), xytext=(0, 4), textcoords="offset points", ha="center", fontsize=8)
ax.set_ylim(0, max(scases) * 1.18)
ax.set_ylabel("案例数")
ax.set_title("(a) 搜索完成情况", fontsize=10.8, pad=8)
ax.legend(fontsize=7.6, frameon=False, loc="upper right")
style(ax)

ax = axes[1]
x = range(len(names))
w = 0.34
b1 = ax.bar([i - w/2 for i in x], srate, width=w, color=GREEN, edgecolor="white", label="改进案例占比")
b2 = ax.bar([i + w/2 for i in x], sgap, width=w, color=BLUE, edgecolor="white", label="总目标值下降")
ax.set_xticks(list(x))
ax.set_xticklabels(names)
ax.set_ylabel("%")
ax.set_ylim(0, max(max(srate), max(sgap)) * 1.25)
for b, v in list(zip(b1, srate)) + list(zip(b2, sgap)):
    ax.annotate(f"{v:.2f}%", (b.get_x()+b.get_width()/2, b.get_height()),
                xytext=(0, 3), textcoords="offset points", ha="center", fontsize=7.4)
ax.set_title("(b) 改进覆盖与总体收益", fontsize=10.8, pad=8)
ax.legend(fontsize=7.4, frameon=False, loc="upper left")
style(ax)

ax = axes[2]
bars = ax.bar(names, stime, color=GRAY, edgecolor="white", linewidth=0.8, width=0.55)
ax.set_ylabel("平均单案例耗时 / ms")
ax.set_title("(c) 平均耗时", fontsize=10.8, pad=8)
ax.set_ylim(0, max(stime) * 1.22)
bar_labels(ax, bars, [f"{v:.1f}" for v in stime], fontsize=8)
style(ax)
fig.text(0.5, -0.04, "10000 个案例全部返回可行解，0 个非法解、0 个不可行解；时间上限 200 ms、结点上限 20 万，均由结点上限触发。",
         ha="center", fontsize=8.2, color="#555555")
fig.tight_layout(w_pad=1.8)
fig.savefig(FIG / "stress_by_scale.png", facecolor="white")
plt.close(fig)

print("written:")
for p in ["flow_backtracking.png", "exact_growth.png", "exact_improvement.png", "scalability_status.png", "stress_by_scale.png"]:
    fp = FIG / p
    print(fp, fp.stat().st_size)