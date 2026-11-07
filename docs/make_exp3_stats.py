# -*- coding: utf-8 -*-
"""Summarize branch-and-bound benchmark CSV files into results/branch_bound_stats.json."""
import csv
import json
import statistics
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RESULTS = ROOT / "results"


def f(row, key):
    return float(row[key])


def i(row, key):
    return int(row[key])


def summarize(rows):
    if not rows:
        return {}
    greedy = [i(r, "Greedy_Cost") for r in rows]
    backtrack = [i(r, "Backtracking_Cost") for r in rows]
    branch = [i(r, "BranchBound_Cost") for r in rows]
    bt_time = [f(r, "Backtracking_TimeMs") for r in rows]
    bb_time = [f(r, "BranchBound_TimeMs") for r in rows]
    bt_nodes = [i(r, "Backtracking_Nodes") for r in rows]
    bb_nodes = [i(r, "BranchBound_Nodes") for r in rows]
    gap_bt_signed = [(b - a) / a * 100.0 for a, b in zip(backtrack, branch)]
    gap_greedy = [(b - a) / a * 100.0 for a, b in zip(greedy, branch)]
    improve_bt = [-g for g in gap_bt_signed]
    improved_gaps = [g for g in improve_bt if g > 0]
    total_greedy = sum(greedy)
    total_bt = sum(backtrack)
    total_bb = sum(branch)

    out = {
        "cases": len(rows),
        "optimal": sum(1 for r in rows if r["BranchBound_Status"] == "optimal"),
        "node_limit": sum(1 for r in rows if r["BranchBound_Status"] == "node_limit"),
        "time_limit": sum(1 for r in rows if r["BranchBound_Status"] == "time_limit"),
        "infeasible": sum(1 for r in rows if r["BranchBound_Status"] == "infeasible"),
        "invalid": sum(1 for r in rows if r["BranchBound_Status"] not in ("optimal", "node_limit", "time_limit")),
        "improved": sum(1 for g in improve_bt if g > 1e-12),
        "equal": sum(1 for g in improve_bt if abs(g) <= 1e-12),
        "worse": sum(1 for g in improve_bt if g < -1e-12),
        "improved_vs_greedy": sum(1 for g in gap_greedy if g < -1e-12),
        "equal_vs_greedy": sum(1 for g in gap_greedy if abs(g) <= 1e-12),
        "worse_vs_greedy": sum(1 for g in gap_greedy if g > 1e-12),
        "total_greedy": total_greedy,
        "total_backtrack": total_bt,
        "total_branch": total_bb,
        "gap_vs_greedy": (total_bb - total_greedy) / total_greedy * 100.0,
        "gap_vs_backtrack": (total_bb - total_bt) / total_bt * 100.0,
        "total_time": sum(bb_time),
        "mean_time": statistics.mean(bb_time),
        "max_time": max(bb_time),
        "total_nodes": sum(bb_nodes),
        "mean_nodes": statistics.mean(bb_nodes),
        "max_nodes": max(bb_nodes),
        "backtrack_optimal": sum(1 for r in rows if r["Backtracking_Status"] == "optimal"),
        "backtrack_node_limit": sum(1 for r in rows if r["Backtracking_Status"] == "node_limit"),
        "backtrack_time_limit": sum(1 for r in rows if r["Backtracking_Status"] == "time_limit"),
        "backtrack_total_time": sum(bt_time),
        "backtrack_mean_time": statistics.mean(bt_time),
        "backtrack_max_time": max(bt_time),
        "backtrack_total_nodes": sum(bt_nodes),
        "backtrack_mean_nodes": statistics.mean(bt_nodes),
        "backtrack_max_nodes": max(bt_nodes),
        "complete_both": sum(1 for r in rows if r["BranchBound_Complete"] == "1" and r["Backtracking_Complete"] == "1"),
        "complete_value_mismatch": sum(1 for r in rows if r["BranchBound_Complete"] == "1" and r["Backtracking_Complete"] == "1" and i(r, "BranchBound_Cost") != i(r, "Backtracking_Cost")),
        "mean_gap_vs_backtrack": statistics.mean(gap_bt_signed),
        "median_gap_vs_backtrack": statistics.median(gap_bt_signed),
        "min_gap_vs_backtrack": min(gap_bt_signed),
        "max_gap_vs_backtrack": max(gap_bt_signed),
        "max_improvement_vs_backtrack": max(improve_bt),
        "improved_mean_gap": statistics.mean(improved_gaps) if improved_gaps else 0.0,
        "improved_median_gap": statistics.median(improved_gaps) if improved_gaps else 0.0,
        "improved_min_gap": min(improved_gaps) if improved_gaps else 0.0,
    }
    out["node_reduction_percent"] = (
        (out["backtrack_total_nodes"] - out["total_nodes"]) / out["backtrack_total_nodes"] * 100.0
        if out["backtrack_total_nodes"] else 0.0
    )
    out["time_change_percent"] = (
        (out["total_time"] - out["backtrack_total_time"]) / out["backtrack_total_time"] * 100.0
        if out["backtrack_total_time"] else 0.0
    )
    return out


def read(name):
    with (RESULTS / name).open(newline="", encoding="utf-8") as fh:
        return list(csv.DictReader(fh))


exact_rows = read("branch_bound_benchmark.csv")
scal_rows = read("branch_bound_scalability.csv")
stress_rows = read("branch_bound_stress_all.csv")

exact = summarize(exact_rows)
scalability = summarize(scal_rows)
stress = summarize(stress_rows)

exact_by_k = {}
for k in range(5, 12):
    exact_by_k[str(k)] = summarize([r for r in exact_rows if int(r["K"]) == k])

scalability_groups = {
    "K13-15": summarize([r for r in scal_rows if 13 <= int(r["K"]) <= 15]),
    "K16-80": summarize([r for r in scal_rows if 16 <= int(r["K"]) <= 80]),
    "K81-499": summarize([r for r in scal_rows if int(r["K"]) > 80]),
}
stress_by_scale = {
    "small": summarize([r for r in stress_rows if r["Scale"] == "small"]),
    "medium": summarize([r for r in stress_rows if r["Scale"] == "medium"]),
    "large": summarize([r for r in stress_rows if r["Scale"] == "large"]),
}


def top_improved(rows, limit=15):
    items = []
    for r in rows:
        bt = i(r, "Backtracking_Cost")
        bb = i(r, "BranchBound_Cost")
        if bb < bt:
            items.append({
                "case": i(r, "CaseId"),
                "K": i(r, "K"),
                "N": i(r, "N"),
                "M": i(r, "M"),
                "greedy": i(r, "Greedy_Cost"),
                "backtrack": bt,
                "branch": bb,
                "gap": (bt - bb) / bt * 100.0,
                "backtrack_nodes": i(r, "Backtracking_Nodes"),
                "branch_nodes": i(r, "BranchBound_Nodes"),
                "backtrack_time": f(r, "Backtracking_TimeMs"),
                "branch_time": f(r, "BranchBound_TimeMs"),
            })
    items.sort(key=lambda x: (-x["gap"], x["case"]))
    return items[:limit]


def top_slowest(rows, limit=10):
    items = [{
        "case": i(r, "CaseId"), "K": i(r, "K"), "N": i(r, "N"), "M": i(r, "M"),
        "time": f(r, "BranchBound_TimeMs"), "nodes": i(r, "BranchBound_Nodes"),
        "status": r["BranchBound_Status"],
    } for r in rows]
    items.sort(key=lambda x: -x["time"])
    return items[:limit]


data = {
    "generated_from": [
        "results/branch_bound_benchmark.csv",
        "results/branch_bound_scalability.csv",
        "results/branch_bound_stress_all.csv",
    ],
    "exact": exact,
    "exact_by_k": exact_by_k,
    "scalability": scalability,
    "scalability_groups": scalability_groups,
    "stress": stress,
    "stress_by_scale": stress_by_scale,
    "top_improved": top_improved(stress_rows),
    "top_improved_exact": top_improved(exact_rows),
    "slowest_exact": top_slowest(exact_rows),
    "slowest_stress": top_slowest(stress_rows),
    "status_changed": [
        {
            "case": i(r, "CaseId"), "K": i(r, "K"),
            "backtrack": i(r, "Backtracking_Cost"), "branch": i(r, "BranchBound_Cost"),
            "backtrack_status": r["Backtracking_Status"], "branch_status": r["BranchBound_Status"],
        }
        for r in exact_rows if r["Backtracking_Status"] != r["BranchBound_Status"]
    ],
}

with (RESULTS / "branch_bound_stats.json").open("w", encoding="utf-8") as fh:
    json.dump(data, fh, ensure_ascii=False, indent=1)

print("wrote", RESULTS / "branch_bound_stats.json")
for name, d in (("exact", exact), ("scalability", scalability), ("stress", stress)):
    print(name, "cases", d["cases"], "optimal", d["optimal"], "node_limit", d["node_limit"],
          "cost", d["total_branch"], "bt", d["total_backtrack"],
          "gap_bt %.6f" % d["gap_vs_backtrack"], "time %.2f" % d["total_time"],
          "bt_time %.2f" % d["backtrack_total_time"], "nodes", d["total_nodes"],
          "bt_nodes", d["backtrack_total_nodes"])
print("exact mismatches", exact["complete_value_mismatch"], "status_changed", len(data["status_changed"]))
