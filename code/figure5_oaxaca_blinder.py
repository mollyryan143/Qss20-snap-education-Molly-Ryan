"""
figure5_oaxaca_blinder.py
QSS 20 Final Project — Molly Ryan

PURPOSE:
    Oaxaca-Blinder decomposition of the grade completion gap between
    non-SNAP and SNAP children.

    The gap in average highest grade completed between groups has two parts:

    1. ENDOWMENTS (explained)
       How much of the gap is because SNAP and non-SNAP children have
       different characteristics? (e.g. SNAP kids have less educated mothers,
       more siblings, younger mothers)

    2. COEFFICIENTS (unexplained)
       How much of the gap remains because those same characteristics
       have DIFFERENT effects for the two groups?
       This is the core finding of this paper.

    3. INTERACTION
       The overlap between the two effects.

    Interpretation example:
       If the total gap = 1.47 grades and endowments explain 0.90 grades,
       then about 61% of the gap is due to group differences in
       characteristics, and 39% remains unexplained by characteristics alone.

INPUT:
    data/processed/nlscya_qss20_cleaned_subset_full.csv

OUTPUT:
    output/figure5_oaxaca_blinder.png
    output/figure5_oaxaca_blinder.csv
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
from utils import load_clean, make_analysis_frame, save_fig, BASE_CONTROLS, OUTCOME, CONTROL_LABELS

# ── Paths ─────────────────────────────────────────────────────────────────────

IN_PATH    = Path("data/processed/nlscya_qss20_cleaned_subset_full.csv")
OUTPUT_DIR = Path("output")
OUTPUT_DIR.mkdir(exist_ok=True)

# ── Load and prepare ──────────────────────────────────────────────────────────

df  = load_clean(IN_PATH)
reg = make_analysis_frame(df)
reg[OUTCOME] = reg[OUTCOME].replace([-1,-2,-3,-4,-5,-7,-8,-9], np.nan)

needed = [OUTCOME, "snap_ever"] + BASE_CONTROLS
clean  = reg.dropna(subset=needed).copy()

snap    = clean[clean["snap_ever"] == 1]
nonsnap = clean[clean["snap_ever"] == 0]

print(f"Non-SNAP n={len(nonsnap):,}  mean grade={nonsnap[OUTCOME].mean():.3f}")
print(f"SNAP     n={len(snap):,}  mean grade={snap[OUTCOME].mean():.3f}")
print(f"Raw gap (non-SNAP minus SNAP): {nonsnap[OUTCOME].mean() - snap[OUTCOME].mean():.3f}")

# ── Oaxaca-Blinder decomposition (threefold) ──────────────────────────────────
#
# We implement this manually using OLS — standard approach in social science.
#
# Reference group: non-SNAP (group A)
# Comparison group: SNAP (group B)
#
# Threefold decomposition:
#   Gap = Endowments + Coefficients + Interaction
#
#   Endowments  = (X_A - X_B) * B_B
#   Coefficients= X_B * (B_A - B_B)
#   Interaction = (X_A - X_B) * (B_A - B_B)
#
# where X = mean characteristics, B = regression coefficients

formula = OUTCOME + " ~ " + " + ".join(BASE_CONTROLS)

fit_ns = smf.ols(formula, data=nonsnap).fit()
fit_s  = smf.ols(formula, data=snap).fit()

# Mean characteristics for each group (including intercept)
controls_with_intercept = ["Intercept"] + BASE_CONTROLS

X_ns = pd.Series({"Intercept": 1.0, **{c: nonsnap[c].mean() for c in BASE_CONTROLS}})
X_s  = pd.Series({"Intercept": 1.0, **{c: snap[c].mean()    for c in BASE_CONTROLS}})

B_ns = fit_ns.params
B_s  = fit_s.params

# Align
X_ns = X_ns.reindex(B_ns.index).fillna(0)
X_s  = X_s.reindex(B_ns.index).fillna(0)

# Threefold decomposition by variable
endowments   = (X_ns - X_s) * B_s
coefficients = X_s * (B_ns - B_s)
interaction  = (X_ns - X_s) * (B_ns - B_s)

total_endow = endowments.sum()
total_coef  = coefficients.sum()
total_inter = interaction.sum()
total_gap   = nonsnap[OUTCOME].mean() - snap[OUTCOME].mean()

print(f"\n=== Oaxaca-Blinder Threefold Decomposition ===")
print(f"Total gap (non-SNAP minus SNAP): {total_gap:.3f} grades")
print(f"  Endowments (explained):        {total_endow:.3f} ({total_endow/total_gap*100:.1f}%)")
print(f"  Coefficients (unexplained):    {total_coef:.3f}  ({total_coef/total_gap*100:.1f}%)")
print(f"  Interaction:                   {total_inter:.3f}  ({total_inter/total_gap*100:.1f}%)")

# Per-variable breakdown
print(f"\n=== Per-variable endowment contributions ===")
endo_df = pd.DataFrame({
    "variable":    endowments.index,
    "label":       [CONTROL_LABELS.get(v, v) for v in endowments.index],
    "endowment":   endowments.values,
    "coefficient": coefficients.values,
    "interaction": interaction.values,
}).set_index("variable")

endo_df["endow_pct"] = endo_df["endowment"] / total_gap * 100
print(endo_df[["label","endowment","endow_pct","coefficient"]].round(3).to_string())

# Save
endo_df.reset_index().to_csv(OUTPUT_DIR / "figure5_oaxaca_blinder.csv", index=False)

# ── Plot 1: Overall decomposition bar ────────────────────────────────────────

fig, axes = plt.subplots(1, 2, figsize=(13, 6))

# Left panel: stacked bar showing decomposition
components = [
    "Endowments\n(explained by\ncharacteristics)",
    "Coefficients\n(unexplained —\ndifferent returns)",
    "Interaction\n(overlap of\nboth effects)"
]
values     = [total_endow, total_coef, total_inter]
colors     = ["#0f766e", "#b45309", "#94a3b8"]
pcts       = [v/total_gap*100 for v in values]

bars = axes[0].bar(components, values, color=colors, width=0.5, edgecolor="white", linewidth=1.5)
axes[0].axhline(0, color="black", linewidth=0.8, linestyle="--", alpha=0.5)

for bar, val, pct in zip(bars, values, pcts):
    axes[0].text(
        bar.get_x() + bar.get_width()/2,
        val + 0.02 if val >= 0 else val - 0.08,
        f"{val:+.2f}\n({pct:.1f}%)",
        ha="center", va="bottom" if val >= 0 else "top",
        fontsize=9, fontweight="bold"
    )

axes[0].set_ylabel("Grades", fontsize=10)
axes[0].set_title(
    f"Total gap = {total_gap:.2f} grades\n"
    "How much is explained by characteristics\nvs. different returns to those characteristics?",
    fontsize=10, fontweight="bold"
)
axes[0].set_ylim(-0.3, max(values) + 0.4)
axes[0].grid(axis="y", linestyle=":", alpha=0.35)

# Right panel: per-variable endowment contributions (drop intercept)
endo_plot = endo_df.drop("Intercept").sort_values("endowment")
y = np.arange(len(endo_plot))
bar_colors = ["#0f766e" if v >= 0 else "#b45309" for v in endo_plot["endowment"]]

axes[1].barh(y, endo_plot["endowment"], color=bar_colors, alpha=0.85, height=0.6)
axes[1].axvline(0, color="black", linewidth=0.8, linestyle="--", alpha=0.5)

for i, (_, row) in enumerate(endo_plot.iterrows()):
    axes[1].text(
        row["endowment"] + 0.01 if row["endowment"] >= 0 else row["endowment"] - 0.01,
        i,
        f"{row['endowment']:+.3f}",
        va="center",
        ha="left" if row["endowment"] >= 0 else "right",
        fontsize=8, color="#333"
    )

axes[1].set_yticks(y)
axes[1].set_yticklabels(endo_plot["label"].values, fontsize=9)
axes[1].set_xlabel("Contribution to grade gap\n(positive = SNAP kids disadvantaged by this characteristic)", fontsize=9)
axes[1].set_title(
    "Which characteristics explain\nthe most of the grade gap?",
    fontsize=10, fontweight="bold"
)
axes[1].grid(axis="x", linestyle=":", alpha=0.35)

from matplotlib.patches import Patch
legend_els = [
    Patch(facecolor="#0f766e", label="Explains gap (SNAP more disadvantaged)"),
    Patch(facecolor="#b45309", label="Reduces gap (SNAP less disadvantaged)"),
]
axes[1].legend(handles=legend_els, fontsize=8, loc="lower right")

fig.suptitle(
    "Oaxaca-Blinder Decomposition of the Grade Completion Gap\n"
    "Non-SNAP vs. SNAP Children",
    fontsize=12, fontweight="bold"
)

note = (
    "Notes: Endowments = share of gap explained by SNAP and non-SNAP children having different "
    "characteristics (e.g. mother's education, family structure).\n"
    "Coefficients = share explained by those same characteristics having different effects for "
    "each group — the core finding of this paper.\n"
    "Interaction = technical overlap between the two effects; typically reported but not "
    "substantively interpreted."
)
fig.text(0.5, -0.04, note, ha="center", fontsize=7.5, color="#475569",
         wrap=True, style="italic",
         bbox=dict(boxstyle="square,pad=0.4", fc="#f8fafc", ec="#e2e8f0"))

plt.subplots_adjust(top=0.85, wspace=0.35, bottom=0.18)
save_fig(fig, OUTPUT_DIR / "figure5_oaxaca_blinder.png", tight=False)
print(f"\nSaved: {OUTPUT_DIR / 'figure5_oaxaca_blinder.png'}")
print("figure5_oaxaca_blinder.py complete.")
