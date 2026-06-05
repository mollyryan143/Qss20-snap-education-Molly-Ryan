"""
figure3_geography_dotplot.py
QSS 20 Final Project — Molly Ryan

PURPOSE:
    Produce a dot plot showing average highest grade completed by
    Census region x urban/rural x SNAP status.

    Each row = one region/urban-rural combination (8 groups)
    Two dots per row = SNAP (amber) vs non-SNAP (teal)
    Shows whether the urban/rural divide matters differently
    across regions for SNAP vs non-SNAP children.

INPUT:
    data/processed/nlscya_qss20_cleaned_subset_geo.csv

OUTPUT:
    output/figure3_region_urban_dotplot.png
"""

import pandas as pd
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.lines as mlines
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

# Keep only Urban and Rural (drop Unknown)
reg = reg[reg["urban_rural"].isin(["Urban", "Rural"])]

# Drop missing
reg = reg.dropna(subset=[OUTCOME, "snap_ever", "region", "urban_rural"])

print(f"Analysis sample: {len(reg):,} children")
print("\nGroup sizes:")
print(reg.groupby(["region", "urban_rural", "snap_ever"])[OUTCOME].count().to_string())

# ── Compute group means and CIs ───────────────────────────────────────────────

def mean_ci(series):
    """Return mean and 95% CI half-width."""
    n    = len(series)
    mean = series.mean()
    se   = series.std() / np.sqrt(n)
    return mean, 1.96 * se, n

rows = []
for region in ["Northeast", "Midwest", "South", "West"]:
    for urban in ["Urban", "Rural"]:
        for snap_val, snap_label in [(0, "Non-SNAP"), (1, "SNAP")]:
            sub = reg[
                (reg["region"] == region) &
                (reg["urban_rural"] == urban) &
                (reg["snap_ever"] == snap_val)
            ][OUTCOME]
            if len(sub) < 10:
                continue
            mean, ci, n = mean_ci(sub)
            rows.append({
                "region":     region,
                "urban_rural":urban,
                "group":      snap_label,
                "label":      f"{region} — {urban}",
                "mean":       mean,
                "ci":         ci,
                "n":          n,
            })

plot_df = pd.DataFrame(rows)
print("\nGroup means:")
print(plot_df[["label","group","mean","ci","n"]].round(3).to_string(index=False))

# ── Order rows: by region, then Urban before Rural ───────────────────────────

region_order = ["Northeast", "Midwest", "West", "South"]
urban_order  = ["Urban", "Rural"]

plot_df["region_rank"] = plot_df["region"].map({r: i for i, r in enumerate(region_order)})
plot_df["urban_rank"]  = plot_df["urban_rural"].map({u: i for i, u in enumerate(urban_order)})
plot_df = plot_df.sort_values(["region_rank", "urban_rank"], ascending=[False, False])

labels = plot_df["label"].unique()
# Keep order from sorted df
seen = set()
ordered_labels = []
for l in plot_df["label"]:
    if l not in seen:
        ordered_labels.append(l)
        seen.add(l)

y_map = {label: i for i, label in enumerate(ordered_labels)}

# ── Plot ──────────────────────────────────────────────────────────────────────

COLORS  = {"Non-SNAP": "#0f766e", "SNAP": "#b45309"}
OFFSETS = {"Non-SNAP": -0.18,     "SNAP":  0.18}
MARKERS = {"Non-SNAP": "o",       "SNAP":  "s"}

fig, ax = plt.subplots(figsize=(9, 7))

for group in ["Non-SNAP", "SNAP"]:
    sub = plot_df[plot_df["group"] == group]
    y_pos = [y_map[l] + OFFSETS[group] for l in sub["label"]]

    ax.errorbar(
        sub["mean"], y_pos,
        xerr=sub["ci"],
        fmt=MARKERS[group],
        color=COLORS[group],
        label=group,
        capsize=4,
        markersize=7,
        linewidth=1.4,
        markeredgecolor="white",
        markeredgewidth=0.5,
    )

    # Annotate n
    for _, row in sub.iterrows():
        y = y_map[row["label"]] + OFFSETS[group]
        ax.text(
            row["mean"] + row["ci"] + 0.05, y,
            f'n={row["n"]}',
            va="center", ha="left",
            fontsize=7, color=COLORS[group], alpha=0.8
        )

# Region dividers
region_boundaries = []
prev_region = None
for label in ordered_labels:
    region = label.split(" — ")[0]
    if prev_region and region != prev_region:
        idx = ordered_labels.index(label)
        region_boundaries.append(idx - 0.5)
    prev_region = region

for b in region_boundaries:
    ax.axhline(b, color="#cbd5e1", linewidth=1, linestyle="--")

# Reference line at overall mean
overall_mean = reg[OUTCOME].mean()
ax.axvline(overall_mean, color="#94a3b8", linewidth=1,
           linestyle=":", label=f"Overall mean ({overall_mean:.2f})")

ax.set_yticks(range(len(ordered_labels)))
ax.set_yticklabels(ordered_labels, fontsize=10)
ax.set_xlabel("Mean highest grade completed (95% CI)", fontsize=10)
ax.set_title(
    "Average Grade Completion by Region, Urban/Rural, and SNAP Status\n"
    "Do geographic context and SNAP receipt interact?",
    fontsize=11, fontweight="bold"
)
ax.legend(fontsize=9, loc="lower right")
ax.grid(axis="x", linestyle=":", alpha=0.35)

# Add grade reference labels at top
for grade, label in [(12, "HS"), (14, "AA"), (16, "BA")]:
    if ax.get_xlim()[0] < grade < ax.get_xlim()[1]:
        ax.axvline(grade, color="#e2e8f0", linewidth=0.8, linestyle="-", zorder=0)
        ax.text(grade, len(ordered_labels) - 0.3, label,
                ha="center", fontsize=7, color="#94a3b8")

plt.subplots_adjust(left=0.22, right=0.92, top=0.88)
save_fig(fig, OUTPUT_DIR / "figure3_region_urban_dotplot.png", tight=False)

print(f"\nSaved: {OUTPUT_DIR / 'figure3_region_urban_dotplot.png'}")
print("\nfigure3_geography_dotplot.py complete.")
