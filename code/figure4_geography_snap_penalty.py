"""
figure4_geography_snap_penalty.py
QSS 20 Final Project — Molly Ryan

PURPOSE:
    Estimate the SNAP education penalty (OLS coefficient on snap_ever)
    separately for each region x urban/rural subgroup.

    This answers: where geographically is the SNAP education gap largest?

    Each subgroup regression controls for:
        female, black, hispanic, birth_year, birth_order,
        mother_age, mother_educ, father_in_hh

    The SNAP coefficient in each model estimates how many fewer grades
    SNAP children complete compared to non-SNAP children in that
    specific geographic context, holding controls constant.

INPUT:
    data/processed/nlscya_qss20_cleaned_subset_geo.csv

OUTPUT:
    output/figure4_geography_snap_penalty.png
    output/figure4_geography_snap_penalty.csv
"""

import pandas as pd
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import statsmodels.formula.api as smf
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from utils import load_clean, make_analysis_frame, save_fig, BASE_CONTROLS, OUTCOME

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

print(f"Analysis sample: {len(reg):,} children")

# ── Run OLS for each region x urban subgroup ──────────────────────────────────

formula = f"{OUTCOME} ~ snap_ever + " + " + ".join(BASE_CONTROLS)

rows = []
for region in ["Northeast", "Midwest", "West", "South"]:
    for urban in ["Urban", "Rural"]:
        sub = reg[
            (reg["region"] == region) &
            (reg["urban_rural"] == urban)
        ].dropna(subset=[OUTCOME, "snap_ever"] + BASE_CONTROLS)

        if len(sub) < 30:
            print(f"Skipping {region} {urban} — only {len(sub)} rows")
            continue

        fit  = smf.ols(formula, data=sub).fit(cov_type="HC3")
        ci   = fit.conf_int()
        coef = fit.params.get("snap_ever", np.nan)
        p    = fit.pvalues.get("snap_ever", np.nan)

        rows.append({
            "region":      region,
            "urban_rural": urban,
            "label":       f"{region} — {urban}",
            "coef":        coef,
            "ci_low":      ci.loc["snap_ever", 0] if "snap_ever" in ci.index else np.nan,
            "ci_high":     ci.loc["snap_ever", 1] if "snap_ever" in ci.index else np.nan,
            "p_value":     p,
            "n":           int(fit.nobs),
            "r2":          round(fit.rsquared, 3),
        })

        stars = "***" if p < 0.001 else "**" if p < 0.01 else "*" if p < 0.05 else ""
        print(f"{region:<12} {urban:<6}  n={int(fit.nobs):>4}  "
              f"SNAP coef={coef:>+.3f}  "
              f"CI=[{ci.loc['snap_ever',0]:>+.3f}, {ci.loc['snap_ever',1]:>+.3f}]  "
              f"p={p:.4f}{stars}")

plot_df = pd.DataFrame(rows)
plot_df.to_csv(OUTPUT_DIR / "figure4_geography_snap_penalty.csv", index=False)
print(f"\nSaved: {OUTPUT_DIR / 'figure4_geography_snap_penalty.csv'}")

# ── Order labels ──────────────────────────────────────────────────────────────

region_order = ["Northeast", "Midwest", "West", "South"]
urban_order  = ["Urban", "Rural"]

plot_df["region_rank"] = plot_df["region"].map({r: i for i, r in enumerate(region_order)})
plot_df["urban_rank"]  = plot_df["urban_rural"].map({u: i for i, u in enumerate(urban_order)})
plot_df = plot_df.sort_values(["region_rank", "urban_rank"], ascending=[False, False])

ordered_labels = plot_df["label"].tolist()
y_map = {label: i for i, label in enumerate(ordered_labels)}

# ── Plot ──────────────────────────────────────────────────────────────────────

fig, ax = plt.subplots(figsize=(9, 6))

for _, row in plot_df.iterrows():
    y     = y_map[row["label"]]
    color = "#b45309" if row["p_value"] < 0.05 else "#94a3b8"

    ax.errorbar(
        row["coef"], y,
        xerr=[[row["coef"] - row["ci_low"]], [row["ci_high"] - row["coef"]]],
        fmt="o", color=color,
        capsize=5, markersize=8, linewidth=1.6,
        markeredgecolor="white", markeredgewidth=0.6,
    )

    # Stars
    stars = "***" if row["p_value"] < 0.001 else "**" if row["p_value"] < 0.01 \
            else "*" if row["p_value"] < 0.05 else ""
    if stars:
        ax.text(row["ci_high"] + 0.05, y, stars,
                va="center", ha="left", fontsize=9,
                color="#b45309", fontweight="bold")

    # n label
    ax.text(row["ci_low"] - 0.05, y, f"n={row['n']}",
            va="center", ha="right", fontsize=7, color="#64748b")

# Reference line at zero
ax.axvline(0, color="black", linewidth=1, linestyle="--", alpha=0.6)

# Region dividers
prev_region = None
for label in ordered_labels:
    region = label.split(" — ")[0]
    if prev_region and region != prev_region:
        idx = ordered_labels.index(label)
        ax.axhline(idx - 0.5, color="#cbd5e1", linewidth=1, linestyle="-")
    prev_region = region

# Region labels
prev_region = None
region_start = 0
for i, label in enumerate(ordered_labels):
    region = label.split(" — ")[0]
    if region != prev_region:
        if prev_region is not None:
            mid = (region_start + i - 1) / 2
            ax.text(ax.get_xlim()[0] if ax.get_xlim()[0] < 0 else -2.2,
                    mid, prev_region,
                    va="center", ha="right", fontsize=8,
                    color="#475569", style="italic", fontweight="bold")
        region_start = i
        prev_region  = region
# Last region
mid = (region_start + len(ordered_labels) - 1) / 2

from matplotlib.patches import Patch
legend_els = [
    Patch(facecolor="#b45309", label="Significant (p < 0.05)"),
    Patch(facecolor="#94a3b8", label="Not significant"),
]
ax.legend(handles=legend_els, fontsize=9, loc="lower right")

ax.set_yticks(range(len(ordered_labels)))
ax.set_yticklabels(
    [l.split(" — ")[1] for l in ordered_labels], fontsize=10
)
ax.set_xlabel(
    "SNAP coefficient — estimated grade gap (SNAP minus non-SNAP)\n"
    "controlling for family background and demographics | HC3 robust SEs",
    fontsize=9
)
ax.set_title(
    "Where Is the SNAP Education Penalty Largest?\n"
    "OLS Coefficient on SNAP Receipt by Region and Urban/Rural Status",
    fontsize=11, fontweight="bold"
)
ax.grid(axis="x", linestyle=":", alpha=0.35)

plt.subplots_adjust(left=0.15, right=0.90, top=0.88, bottom=0.15)
save_fig(fig, OUTPUT_DIR / "figure4_geography_snap_penalty.png", tight=False)
print(f"Saved: {OUTPUT_DIR / 'figure4_geography_snap_penalty.png'}")
print("\nfigure4_geography_snap_penalty.py complete.")
