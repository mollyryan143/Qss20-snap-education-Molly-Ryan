"""
figure3_geography_dotplot.py
QSS 20 Final Project — Molly Ryan

PURPOSE:
    Produce a dot plot showing average highest grade completed by
    Census region x urban/rural x SNAP status, compared to the
    overall sample mean.

    Each row = one region/urban-rural combination (8 groups)
    Two dots per row = SNAP (amber) vs non-SNAP (teal)
    Vertical reference line = overall sample mean
    Shows how each group compares to the overall average

INPUT:
    data/processed/nlscya_qss20_cleaned_subset_geo.csv

OUTPUT:
    output/figure3_region_urban_dotplot.png
"""

import pandas as pd
import numpy as np
from scipy import stats
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from utils import load_clean, make_analysis_frame, save_fig, OUTCOME

# ── Paths ─────────────────────────────────────────────────────────────────────

IN_PATH    = Path("data/processed/nlscya_qss20_cleaned_subset_geo.csv")
OUTPUT_DIR = Path("output")
OUTPUT_DIR.mkdir(exist_ok=True)

# ── Load and prepare ──────────────────────────────────────────────────────────

df  = load_clean(IN_PATH)
reg = make_analysis_frame(df)
reg[OUTCOME] = reg[OUTCOME].replace([-1,-2,-3,-4,-5,-7,-8,-9], np.nan)
reg = reg[reg["urban_rural"].isin(["Urban", "Rural"])]
reg = reg.dropna(subset=[OUTCOME, "snap_ever", "region", "urban_rural"])

overall_mean = reg[OUTCOME].mean()
print(f"Overall mean highest grade: {overall_mean:.3f}")
print(f"Analysis sample: {len(reg):,} children")

# ── Compute group means and CIs ───────────────────────────────────────────────

def mean_ci(series):
    n    = len(series)
    mean = series.mean()
    se   = series.std() / np.sqrt(n)
    ci   = 1.96 * se
    t, p = stats.ttest_1samp(series, overall_mean)
    return mean, ci, n, p

rows = []
for region in ["Northeast", "Midwest", "West", "South"]:
    for urban in ["Urban", "Rural"]:
        for snap_val, snap_label in [(0, "Non-SNAP"), (1, "SNAP")]:
            sub = reg[
                (reg["region"] == region) &
                (reg["urban_rural"] == urban) &
                (reg["snap_ever"] == snap_val)
            ][OUTCOME].dropna()
            if len(sub) < 10:
                continue
            mean, ci, n, p = mean_ci(sub)
            rows.append({
                "region":      region,
                "urban_rural": urban,
                "group":       snap_label,
                "label":       f"{region} — {urban}",
                "mean":        mean,
                "ci":          ci,
                "n":           n,
                "p":           p,
                "sig":         p < 0.05,
                "diff":        mean - overall_mean,
            })

plot_df = pd.DataFrame(rows)

# ── Build ordered label list ──────────────────────────────────────────────────

region_order = ["Northeast", "Midwest", "West", "South"]
urban_order  = ["Urban", "Rural"]

plot_df["region_rank"] = plot_df["region"].map({r: i for i, r in enumerate(region_order)})
plot_df["urban_rank"]  = plot_df["urban_rural"].map({u: i for i, u in enumerate(urban_order)})
plot_df = plot_df.sort_values(["region_rank", "urban_rank"], ascending=[False, False])

seen, ordered_labels = set(), []
for l in plot_df["label"]:
    if l not in seen:
        ordered_labels.append(l)
        seen.add(l)

y_map = {label: i for i, label in enumerate(ordered_labels)}

# ── Plot ──────────────────────────────────────────────────────────────────────

COLORS  = {"Non-SNAP": "#0f766e", "SNAP": "#b45309"}
OFFSETS = {"Non-SNAP": -0.18,     "SNAP":  0.18}
MARKERS = {"Non-SNAP": "o",       "SNAP":  "s"}

fig, ax = plt.subplots(figsize=(10, 7))

for group in ["Non-SNAP", "SNAP"]:
    sub = plot_df[plot_df["group"] == group]
    y_pos = [y_map[l] + OFFSETS[group] for l in sub["label"]]

    ax.errorbar(
        sub["mean"], y_pos,
        xerr=sub["ci"],
        fmt=MARKERS[group],
        color=COLORS[group],
        label=group,
        capsize=4, markersize=7, linewidth=1.4,
        markeredgecolor="white", markeredgewidth=0.5,
    )

    # Significance stars vs overall mean
    for _, row in sub.iterrows():
        y = y_map[row["label"]] + OFFSETS[group]
        star = "***" if row["p"] < 0.001 else "**" if row["p"] < 0.01 else "*" if row["p"] < 0.05 else ""
        if star:
            ax.text(
                row["mean"] + row["ci"] + 0.08, y,
                star, va="center", ha="left",
                fontsize=8, color=COLORS[group], fontweight="bold"
            )

# Overall mean reference line
ax.axvline(overall_mean, color="#64748b", linewidth=1.5,
           linestyle="--", label=f"Overall mean ({overall_mean:.2f})", zorder=1)

# Region dividers
prev_region = None
for label in ordered_labels:
    region = label.split(" — ")[0]
    if prev_region and region != prev_region:
        idx = ordered_labels.index(label)
        ax.axhline(idx - 0.5, color="#cbd5e1", linewidth=1, linestyle="-")
    prev_region = region

# Region labels on right side
prev_region = None
region_start = 0
for i, label in enumerate(ordered_labels):
    region = label.split(" — ")[0]
    if region != prev_region:
        if prev_region:
            mid = (region_start + i - 1) / 2
            ax.text(ax.get_xlim()[1] if ax.get_xlim()[1] > 0 else 8.5,
                   mid, prev_region,
                   va="center", ha="left", fontsize=8,
                   color="#64748b", style="italic")
        region_start = i
        prev_region = region

# Grade reference lines
for grade, grade_label in [(4, ""), (6, ""), (12, "HS"), (16, "BA")]:
    ax.axvline(grade, color="#f1f5f9", linewidth=0.8, linestyle="-", zorder=0)
    if grade_label:
        ax.text(grade, len(ordered_labels) - 0.2, grade_label,
                ha="center", fontsize=7, color="#94a3b8")

ax.set_yticks(range(len(ordered_labels)))
ax.set_yticklabels([l.split(" — ")[1] for l in ordered_labels], fontsize=10)
ax.set_xlabel("Mean highest grade completed (95% CI)\n* p<0.05 vs. overall sample mean", fontsize=9)
ax.set_title(
    "Average Grade Completion by Region, Urban/Rural, and SNAP Status\n"
    "Compared to overall sample mean (dashed line)",
    fontsize=11, fontweight="bold"
)
ax.legend(fontsize=9, loc="lower right")
ax.grid(axis="x", linestyle=":", alpha=0.3)

plt.subplots_adjust(left=0.12, right=0.88, top=0.88, bottom=0.1)
save_fig(fig, OUTPUT_DIR / "figure3_region_urban_dotplot.png", tight=False)
print(f"Saved: {OUTPUT_DIR / 'figure3_region_urban_dotplot.png'}")
