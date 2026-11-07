# -*- coding: utf-8 -*-
import csv
import json
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter

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

with open(RESULTS / "branch_bound_stats.json", encoding="utf-8") as f:
    S = json.load(f)

with open(RESULTS / "branch_bound_benchmark.csv", newline="", encoding="utf-8") as f:
    exact_rows = list(csv.DictReader(f))


def kfmt(x, pos=None):
    if x >= 1_000_000:
        return f"{x/1_000_000:.1f}M"
    if x >= 1_000:
        return f"{x/1_000:.0f}k"
    return f"{x:.0f}"


def style(ax):
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.tick_params(colors="#333333", labelsize=9)
    ax.set_axisbelow(True)


def bar_labels(ax, bars, labels, fontsize=8, color="#333333"):
    for b, lab in zip(bars, labels):
        ax.annotate(lab, (b.get_x() + b.get_width() / 2, b.get_height()),
                    xytext=(0, 3), textcoords="offset points",
                    ha="center", va="bottom", fontsize=fontsize, color=color)


# --------------------------------------------------------------- exact compare
by_k = S["exact_by_k"]
ks = [str(k) for k in range(5, 12)]
rows = [by_k[k] for k in ks]
bb_opt = [r["optimal"] for r in rows]
bt_opt = [r["backtrack_optimal"] for r in rows]
cases = [r["cases"] for r in rows]
bb_nodes = [r["total_nodes"] for r in rows]
bt_nodes = [r["backtrack_total_nodes"] for r in rows]
bb_time = [r["total_time"] for r in rows]
bt_time = [r["backtrack_total_time"] for r in rows]

fig, axes = plt.subplots(1, 3, figsize=(11.2, 4.0))
x = range(len(ks))
w = 0.36
ax = axes[0]
b1 = ax.bar([i - w/2 for i in x], bb_opt, width=w, color=BLUE, edgecolor="white", label="分支限界法")
b2 = ax.bar([i + w/2 for i in x], bt_opt, width=w, color=ORANGE, edgecolor="white", label="回溯法")
for i, c in enumerate(cases):
    ax.annotate(f"n={c}", (i, c), xytext=(0, 4), textcoords="offset points",
                ha="center", fontsize=7.0, color="#555555")
ax.set_xticks(list(x)); ax.set_xticklabels(ks)
ax.set_ylim(0, max(cases) * 1.18)
ax.set_xlabel("飞机数 K"); ax.set_ylabel("完成搜索的案例数")
ax.set_title("(a) 证明最优的案例数", fontsize=10.8, pad=8)
ax.legend(fontsize=7.8, frameon=False, loc="upper right")
style(ax)

ax = axes[1]
b1 = ax.bar([i - w/2 for i in x], bb_nodes, width=w, color=BLUE, edgecolor="white", label="分支限界法")
b2 = ax.bar([i + w/2 for i in x], bt_nodes, width=w, color=ORANGE, edgecolor="white", label="回溯法")
ax.set_yscale("log")
ax.set_ylim(1e3, 4e8)
ax.yaxis.set_major_formatter(FuncFormatter(kfmt))
ax.set_xticks(list(x)); ax.set_xticklabels(ks)
ax.set_xlabel("飞机数 K"); ax.set_ylabel("总搜索结点数（对数轴）")
ax.set_title("(b) 总搜索结点数", fontsize=10.8, pad=8)
style(ax)

ax = axes[2]
b1 = ax.bar([i - w/2 for i in x], bb_time, width=w, color=BLUE, edgecolor="white", label="分支限界法")
b2 = ax.bar([i + w/2 for i in x], bt_time, width=w, color=ORANGE, edgecolor="white", label="回溯法")
ax.set_yscale("log")
ax.set_ylim(0.5, 1e4)
ax.yaxis.set_major_formatter(FuncFormatter(kfmt))
ax.set_xticks(list(x)); ax.set_xticklabels(ks)
ax.set_xlabel("飞机数 K"); ax.set_ylabel("总耗时 / ms（对数轴）")
ax.set_title("(c) 总求解耗时", fontsize=10.8, pad=8)
style(ax)
fig.text(0.5, -0.035, "精确组 2000 例，时间上限 2000 ms、结点上限 500 万；柱高为组内案例之和。",
         ha="center", fontsize=8.3, color="#555555")
fig.tight_layout(w_pad=2.0)
fig.savefig(FIG / "exact_compare.png", facecolor="white")
plt.close(fig)

# ------------------------------------------------------- per-case search scatter
bt_nodes_case = [int(r["Backtracking_Nodes"]) for r in exact_rows]
bb_nodes_case = [int(r["BranchBound_Nodes"]) for r in exact_rows]
bt_time_case = [float(r["Backtracking_TimeMs"]) for r in exact_rows]
bb_time_case = [float(r["BranchBound_TimeMs"]) for r in exact_rows]
status = [r["BranchBound_Status"] for r in exact_rows]
positive = [(a, b, s) for a, b, s in zip(bt_nodes_case, bb_nodes_case, status) if a > 0 and b > 0]
reduction = [(a - b) / a * 100.0 for a, b in zip(bt_nodes_case, bb_nodes_case) if a > 0]

fig, axes = plt.subplots(1, 2, figsize=(10.2, 4.1))
ax = axes[0]
colors = [BLUE if s == "optimal" else ORANGE for _, _, s in positive]
ax.scatter([a for a, _, _ in positive], [b for _, b, _ in positive],
           s=10, alpha=0.55, c=colors, linewidths=0)
lo, hi = 50, 2e7
ax.plot([lo, hi], [lo, hi], color=GRAY, linewidth=0.9, linestyle="--", label="y = x")
ax.set_xscale("log"); ax.set_yscale("log")
ax.set_xlim(lo, hi); ax.set_ylim(lo, hi)
ax.set_xlabel("回溯法结点数（对数轴）")
ax.set_ylabel("分支限界法结点数（对数轴）")
ax.set_title("(a) 逐案例搜索规模（有搜索结点）", fontsize=10.5, pad=8)
ax.legend(fontsize=8, frameon=False, loc="upper left")
style(ax)

ax = axes[1]
bins = [0, 20, 40, 60, 80, 90, 100]
counts = [0] * (len(bins) - 1)
for r in reduction:
    for i in range(len(bins) - 1):
        if bins[i] <= r < bins[i + 1] or (i == len(bins) - 2 and r == 100):
            counts[i] += 1
            break
labels = ["0-20", "20-40", "40-60", "60-80", "80-90", "90-100"]
bars = ax.bar(labels, counts, color=GREEN, edgecolor="white", linewidth=0.8)
bar_labels(ax, bars, [str(c) for c in counts], fontsize=7.8)
ax.set_xlabel("结点数减少比例 / %")
ax.set_ylabel("案例数")
ax.set_title("(b) 结点数减少比例分布", fontsize=10.8, pad=8)
ax.tick_params(axis="x", labelsize=7.8)
ax.set_ylim(0, max(counts) * 1.18)
style(ax)
fig.text(0.5, -0.035, "精确组 2000 例；244 例由根结点下界直接证明最优（无搜索结点），余下 1756 例参与统计。",
         ha="center", fontsize=8.0, color="#555555")
fig.tight_layout(w_pad=2.0)
fig.savefig(FIG / "exact_search_scatter.png", facecolor="white")
plt.close(fig)

# -------------------------------------------------------------- scalability
groups = ["K13-15", "K16-80", "K81-499"]
grows = [S["scalability_groups"][g] for g in groups]
cases = [r["cases"] for r in grows]
bb_opt = [r["optimal"] for r in grows]
bt_opt = [r["backtrack_optimal"] for r in grows]
bb_time = [r["total_time"] for r in grows]
bt_time = [r["backtrack_total_time"] for r in grows]
bb_nodes = [r["total_nodes"] for r in grows]
bt_nodes = [r["backtrack_total_nodes"] for r in grows]

fig, axes = plt.subplots(1, 3, figsize=(11.0, 4.0))
x = range(len(groups)); w = 0.35
ax = axes[0]
b1 = ax.bar([i - w/2 for i in x], bb_opt, width=w, color=BLUE, edgecolor="white", label="分支限界法")
b2 = ax.bar([i + w/2 for i in x], bt_opt, width=w, color=ORANGE, edgecolor="white", label="回溯法")
for i, c in enumerate(cases):
    ax.annotate(f"n={c}", (i, c), xytext=(0, 4), textcoords="offset points",
                ha="center", fontsize=7.2, color="#555555")
ax.set_xticks(list(x)); ax.set_xticklabels(groups)
ax.set_ylim(0, max(cases) * 1.18)
ax.set_ylabel("完成搜索的案例数")
ax.set_title("(a) 证明最优的案例数", fontsize=10.8, pad=8)
ax.legend(fontsize=7.6, frameon=False, loc="upper right")
style(ax)

ax = axes[1]
b1 = ax.bar([i - w/2 for i in x], bb_time, width=w, color=BLUE, edgecolor="white")
b2 = ax.bar([i + w/2 for i in x], bt_time, width=w, color=ORANGE, edgecolor="white")
bar_labels(ax, b1, [f"{v/1000:.1f}s" for v in bb_time], fontsize=7.2)
bar_labels(ax, b2, [f"{v/1000:.1f}s" for v in bt_time], fontsize=7.2)
ax.set_xticks(list(x)); ax.set_xticklabels(groups)
ax.set_ylim(0, max(max(bb_time), max(bt_time)) * 1.18)
ax.set_ylabel("总耗时 / ms")
ax.set_title("(b) 总求解耗时", fontsize=10.8, pad=8)
style(ax)

ax = axes[2]
b1 = ax.bar([i - w/2 for i in x], [v/1e6 for v in bb_nodes], width=w, color=BLUE, edgecolor="white")
b2 = ax.bar([i + w/2 for i in x], [v/1e6 for v in bt_nodes], width=w, color=ORANGE, edgecolor="white")
bar_labels(ax, b1, [f"{v/1e6:.1f}M" for v in bb_nodes], fontsize=7.0)
bar_labels(ax, b2, [f"{v/1e6:.1f}M" for v in bt_nodes], fontsize=7.0)
ax.set_xticks(list(x)); ax.set_xticklabels(groups)
ax.set_ylim(0, max(max(bb_nodes), max(bt_nodes)) / 1e6 * 1.18)
ax.set_ylabel("总搜索结点数 / 百万")
ax.set_title("(c) 总搜索结点数", fontsize=10.8, pad=8)
style(ax)
fig.text(0.5, -0.035, "可扩展性组 100 例；时间上限 2000 ms、结点上限 500 万。",
         ha="center", fontsize=8.3, color="#555555")
fig.tight_layout(w_pad=2.0)
fig.savefig(FIG / "scalability_compare.png", facecolor="white")
plt.close(fig)

# ------------------------------------------------------------------- stress
names = ["小（K≤15）", "中（K16-80）", "大（K>80）"]
srows = [S["stress_by_scale"][k] for k in ["small", "medium", "large"]]
scases = [r["cases"] for r in srows]
sbb_opt = [r["optimal"] for r in srows]
sbt_opt = [r["backtrack_optimal"] for r in srows]
sbb_time = [r["total_time"] for r in srows]
sbt_time = [r["backtrack_total_time"] for r in srows]
s_gap = [-r["gap_vs_backtrack"] for r in srows]
s_improved = [r["improved"] for r in srows]

fig, axes = plt.subplots(1, 3, figsize=(11.0, 4.0))
x = range(len(names)); w = 0.35
ax = axes[0]
b1 = ax.bar([i - w/2 for i in x], sbb_opt, width=w, color=BLUE, edgecolor="white", label="分支限界法")
b2 = ax.bar([i + w/2 for i in x], sbt_opt, width=w, color=ORANGE, edgecolor="white", label="回溯法")
for i, c in enumerate(scases):
    ax.annotate(f"n={c}", (i, c), xytext=(0, 4), textcoords="offset points",
                ha="center", fontsize=7.0, color="#555555")
ax.set_xticks(list(x)); ax.set_xticklabels(names)
ax.set_ylim(0, max(scases) * 1.18)
ax.set_ylabel("完成搜索的案例数")
ax.set_title("(a) 证明最优的案例数", fontsize=10.8, pad=8)
ax.legend(fontsize=7.4, frameon=False, loc="upper right")
style(ax)

ax = axes[1]
bars = ax.bar(names, s_gap, color=GREEN, edgecolor="white", width=0.58)
bar_labels(ax, bars, [f"{v:.4f}%" for v in s_gap], fontsize=7.6)
ax.set_ylabel("总目标值下降 / %")
ax.set_title("(b) 相对回溯法的目标值改进", fontsize=10.8, pad=8)
ax.set_ylim(0, max(s_gap) * 1.32 if max(s_gap) > 0 else 0.02)
style(ax)

ax = axes[2]
b1 = ax.bar([i - w/2 for i in x], sbb_time, width=w, color=BLUE, edgecolor="white")
b2 = ax.bar([i + w/2 for i in x], sbt_time, width=w, color=ORANGE, edgecolor="white")
bar_labels(ax, b1, [f"{v/1000:.1f}s" for v in sbb_time], fontsize=7.0)
bar_labels(ax, b2, [f"{v/1000:.1f}s" for v in sbt_time], fontsize=7.0)
ax.set_xticks(list(x)); ax.set_xticklabels(names)
ax.set_ylim(0, max(max(sbb_time), max(sbt_time)) * 1.18)
ax.set_ylabel("总耗时 / ms")
ax.set_title("(c) 总求解耗时", fontsize=10.8, pad=8)
style(ax)
fig.text(0.5, -0.035, "全量 10000 例，时间上限 200 ms、结点上限 20 万；分支限界法改进案例数分别为 "
         + "/".join(str(v) for v in s_improved) + "。",
         ha="center", fontsize=8.0, color="#555555")
fig.tight_layout(w_pad=2.0)
fig.savefig(FIG / "stress_compare.png", facecolor="white")
plt.close(fig)

print("written:")
for p in ["exact_compare.png", "exact_search_scatter.png", "scalability_compare.png", "stress_compare.png"]:
    fp = FIG / p
    print(fp, fp.stat().st_size)
