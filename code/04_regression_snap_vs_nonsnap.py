"""
04_regression_snap_vs_nonsnap.py
QSS 20 Final Project — Molly Ryan

RESEARCH QUESTION:
    Do predictors of educational attainment differ by childhood SNAP receipt?

PURPOSE:
    This is the core analysis script. It tests the research question directly
    using two complementary regression approaches:

    1. SPLIT-SAMPLE OLS
       Run the same regression model separately on SNAP children (n~2,754)
       and non-SNAP children (n~5,529). Comparing coefficients side by side
       reveals whether predictors like mother's education or father's presence
       operate differently across groups.

    2. INTERACTION MODEL
       Run one OLS regression that includes snap_ever x each control variable
       as interaction terms. The interaction coefficient formally tests whether
       a given predictor's slope is statistically significantly different
       for SNAP vs. non-SNAP children.

    OUTCOME: highest_grade (continuous, 0-20)
        12 = HS diploma  |  14 = Associate's  |  16 = Bachelor's

    NOTE: TANF is excluded from this analysis. The TANF group is too small
    for reliable split-sample comparison and is not part of this study's
    research question.

INPUT:
    data/processed/nlscya_qss20_cleaned_subset_geo.csv  (from script 02)

OUTPUT:
    output/split_sample_coef_plot.png
    output/interaction_coef_plot.png
    output/split_sample_results.csv
    output/interaction_results.csv
    output/snap_nonsnap_means_table.csv
"""

import pandas as pd
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Patch
import statsmodels.formula.api as smf
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from utils import (load_clean, make_analysis_frame, save_fig,
                   CONTROL_LABELS, BASE_CONTROLS, OUTCOME)

# ── Paths ─────────────────────────────────────────────────────────────────────

IN_PATH    = Path("data/processed/nlscya_qss20_cleaned_subset_geo.csv")
OUTPUT_DIR = Path("output")
OUTPUT_DIR.mkdir(exist_ok=True)

# ── Load and prepare data ─────────────────────────────────────────────────────

df  = load_clean(IN_PATH)
reg = make_analysis_frame(df)

snap    = reg[reg["snap_ever"] == 1].copy()
nonsnap = reg[reg["snap_ever"] == 0].copy()

print(f"\nSample sizes:")
print(f"  SNAP:     {len(snap):,}")
print(f"  Non-SNAP: {len(nonsnap):,}")
print(f"\nMean highest grade:")
print(f"  SNAP:     {snap[OUTCOME].mean():.2f}")
print(f"  Non-SNAP: {nonsnap[OUTCOME].mean():.2f}")
print(f"  Gap:      {nonsnap[OUTCOME].mean() - snap[OUTCOME].mean():.2f} grades")

# ── Descriptive means table ───────────────────────────────────────────────────

snap_means    = snap[BASE_CONTROLS + [OUTCOME]].mean()
nonsnap_means = nonsnap[BASE_CONTROLS + [OUTCOME]].mean()

means_table = pd.DataFrame({
    "Non-SNAP mean": nonsnap_means,
    "SNAP mean":     snap_means,
    "Difference":    snap_means - nonsnap_means,
}).rename(index={**CONTROL_LABELS, OUTCOME: "Highest grade completed"})

print("\nDescriptive means by SNAP status:")
print(means_table.round(3).to_string())
means_table.round(3).to_csv(OUTPUT_DIR / "snap_nonsnap_means_table.csv")

# ── Split-sample OLS ──────────────────────────────────────────────────────────

formula = f"{OUTCOME} ~ " + " + ".join(BASE_CONTROLS)
needed  = [OUTCOME] + BASE_CONTROLS + ["snap_ever"]
clean   = reg.dropna(subset=needed).copy()

split_rows = []
for snap_val, group_label in [(0, "Non-SNAP"), (1, "SNAP")]:
    sub = clean[clean["snap_ever"] == snap_val]
    fit = smf.ols(formula, data=sub).fit(cov_type="HC3")
    ci  = fit.conf_int()
    print(f"\n{group_label}: n={int(fit.nobs):,}  R²={fit.rsquared:.3f}")
    for term in BASE_CONTROLS:
        split_rows.append({
            "group":   group_label,
            "term":    term,
            "label":   CONTROL_LABELS.get(term, term),
            "coef":    fit.params.get(term, np.nan),
            "ci_low":  ci.loc[term, 0] if term in ci.index else np.nan,
            "ci_high": ci.loc[term, 1] if term in ci.index else np.nan,
            "p_value": fit.pvalues.get(term, np.nan),
            "n":       int(fit.nobs),
            "r2":      round(fit.rsquared, 3),
        })

split_df = pd.DataFrame(split_rows)
split_df.to_csv(OUTPUT_DIR / "split_sample_results.csv", index=False)
print(f"\nSaved: {OUTPUT_DIR / 'split_sample_results.csv'}")

# ── Plot: split-sample coefficients ──────────────────────────────────────────

labels  = [CONTROL_LABELS[c] for c in BASE_CONTROLS]
y_pos   = np.arange(len(labels))
colors  = {"Non-SNAP": "#0f766e", "SNAP": "#b45309"}
offsets = {"Non-SNAP": -0.18, "SNAP": 0.18}

fig, ax = plt.subplots(figsize=(9, 6))

for group in ["Non-SNAP", "SNAP"]:
    sub = split_df[split_df["group"] == group].set_index("label")
    coefs     = [sub.loc[l, "coef"]    for l in labels]
    errs_low  = [sub.loc[l, "coef"] - sub.loc[l, "ci_low"]  for l in labels]
    errs_high = [sub.loc[l, "ci_high"] - sub.loc[l, "coef"] for l in labels]
    ax.errorbar(
        coefs, y_pos + offsets[group],
        xerr=[errs_low, errs_high],
        fmt="o", color=colors[group], label=group,
        capsize=4, markersize=6, linewidth=1.4,
    )

ax.axvline(0, color="black", linewidth=0.9, linestyle="--", alpha=0.5)
ax.set_yticks(y_pos)
ax.set_yticklabels(labels, fontsize=10)
ax.set_xlabel("OLS coefficient — effect on highest grade completed\n(HC3 robust standard errors)", fontsize=9)
ax.set_title(
    "Do Predictors of Grade Completion Differ by SNAP Receipt?\nSplit-Sample OLS Coefficients",
    fontsize=11, fontweight="bold"
)
ax.legend(fontsize=10)
ax.grid(axis="x", linestyle=":", alpha=0.4)

n_ns = int(split_df[split_df["group"]=="Non-SNAP"]["n"].iloc[0])
n_s  = int(split_df[split_df["group"]=="SNAP"]["n"].iloc[0])
r2_ns = split_df[split_df["group"]=="Non-SNAP"]["r2"].iloc[0]
r2_s  = split_df[split_df["group"]=="SNAP"]["r2"].iloc[0]
ax.text(0.98, 0.02,
    f"Non-SNAP: n={n_ns:,}, R²={r2_ns}\nSNAP: n={n_s:,}, R²={r2_s}",
    transform=ax.transAxes, ha="right", va="bottom", fontsize=8,
    bbox=dict(boxstyle="square,pad=0.3", fc="white", ec="#ccc"))

plt.subplots_adjust(left=0.27, top=0.88)
save_fig(fig, OUTPUT_DIR / "split_sample_coef_plot.png", tight=False)

# ── Interaction model ─────────────────────────────────────────────────────────

int_formula = (
    f"{OUTCOME} ~ snap_ever + " + " + ".join(BASE_CONTROLS) +
    " + " + " + ".join([f"snap_ever:{c}" for c in BASE_CONTROLS])
)

int_fit = smf.ols(int_formula, data=clean).fit(cov_type="HC3")
int_ci  = int_fit.conf_int()

int_rows = []
for c in BASE_CONTROLS:
    term = f"snap_ever:{c}"
    if term not in int_fit.params.index:
        term = f"{c}:snap_ever"
    if term not in int_fit.params.index:
        continue
    int_rows.append({
        "control": c,
        "label":   CONTROL_LABELS.get(c, c),
        "coef":    int_fit.params[term],
        "ci_low":  int_ci.loc[term, 0],
        "ci_high": int_ci.loc[term, 1],
        "p_value": int_fit.pvalues[term],
    })

int_df = pd.DataFrame(int_rows).sort_values("coef")
int_df["significant"] = int_df["p_value"] < 0.05

print("\nInteraction model (snap_ever x control):")
print(int_df[["label","coef","ci_low","ci_high","p_value","significant"]].round(3).to_string(index=False))
int_df.to_csv(OUTPUT_DIR / "interaction_results.csv", index=False)

# ── Plot: interaction coefficients ────────────────────────────────────────────

fig2, ax2 = plt.subplots(figsize=(8, 6))
bar_colors = ["#b45309" if p < 0.05 else "#94a3b8" for p in int_df["p_value"]]
y2 = np.arange(len(int_df))

ax2.barh(y2, int_df["coef"], color=bar_colors, alpha=0.85, height=0.55)
ax2.errorbar(
    int_df["coef"], y2,
    xerr=[int_df["coef"] - int_df["ci_low"], int_df["ci_high"] - int_df["coef"]],
    fmt="none", color="black", capsize=4, linewidth=1.2,
)
ax2.axvline(0, color="black", linewidth=0.9, linestyle="--", alpha=0.5)
ax2.set_yticks(y2)
ax2.set_yticklabels(int_df["label"].values, fontsize=10)
ax2.set_xlabel("Interaction coefficient: SNAP x predictor\nEffect on highest grade completed", fontsize=9)
ax2.set_title(
    "Where Do Slopes Differ Significantly Between Groups?\nInteraction Model (snap_ever x control)",
    fontsize=11, fontweight="bold"
)
ax2.legend(handles=[
    Patch(facecolor="#b45309", label="Significant (p < 0.05)"),
    Patch(facecolor="#94a3b8", label="Not significant"),
], fontsize=9)
ax2.grid(axis="x", linestyle=":", alpha=0.35)
plt.subplots_adjust(left=0.27, top=0.88)
save_fig(fig2, OUTPUT_DIR / "interaction_coef_plot.png", tight=False)

print("\n04_regression_snap_vs_nonsnap.py complete.")
print("Next step: run 05_full_regression_all_predictors.py")
