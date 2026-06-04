"""
05_full_regression_all_predictors.py
QSS 20 Final Project — Molly Ryan

RESEARCH QUESTION:
    Do predictors of educational attainment differ by childhood SNAP receipt?

PURPOSE:
    Extend the regression analysis from script 04 by adding cognitive ability
    scores (PPVT, math), work frequency, and geographic controls. This script
    also ranks all predictors by their raw Pearson correlation with highest
    grade, separately for SNAP and non-SNAP children, to identify which
    variables show the largest differences between groups.

    This represents the most complete model in the study pipeline.

INPUT:
    data/processed/nlscya_qss20_cleaned_subset_full.csv  (from script 03)

OUTPUT:
    output/correlation_ranking.png
    output/full_regression_coef_plot.png
    output/correlation_ranking.csv
    output/full_regression_results.csv
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
from utils import (load_clean, make_analysis_frame, save_fig,
                   CONTROL_LABELS, FULL_CONTROLS, OUTCOME)

# ── Paths ─────────────────────────────────────────────────────────────────────

IN_PATH    = Path("data/processed/nlscya_qss20_cleaned_subset_full.csv")
OUTPUT_DIR = Path("output")
OUTPUT_DIR.mkdir(exist_ok=True)

# ── Load and prepare ──────────────────────────────────────────────────────────

df  = load_clean(IN_PATH)
reg = make_analysis_frame(df)

snap    = reg[reg["snap_ever"] == 1]
nonsnap = reg[reg["snap_ever"] == 0]

# ── Correlation ranking ───────────────────────────────────────────────────────

corr_rows = []
for var in FULL_CONTROLS:
    if var not in reg.columns:
        continue
    r_all     = reg[[var, OUTCOME]].dropna()[var].corr(reg[[var, OUTCOME]].dropna()[OUTCOME])
    r_snap    = snap[[var, OUTCOME]].dropna()[var].corr(snap[[var, OUTCOME]].dropna()[OUTCOME])
    r_nonsnap = nonsnap[[var, OUTCOME]].dropna()[var].corr(nonsnap[[var, OUTCOME]].dropna()[OUTCOME])
    corr_rows.append({
        "variable": var,
        "label":    CONTROL_LABELS.get(var, var),
        "r_all":    round(r_all,     3),
        "r_snap":   round(r_snap,    3),
        "r_nonsnap":round(r_nonsnap, 3),
        "diff":     round(r_snap - r_nonsnap, 3),
    })

corr_df = pd.DataFrame(corr_rows).sort_values("r_all", ascending=False)
print("\nCorrelation with highest grade:")
print(corr_df[["label","r_all","r_snap","r_nonsnap","diff"]].to_string(index=False))
corr_df.to_csv(OUTPUT_DIR / "correlation_ranking.csv", index=False)

print("\nTop 5 overall:")
for _, row in corr_df.head(5).iterrows():
    print(f"  {row['label']:<35} r = {row['r_all']:+.3f}")

# ── Correlation plot ──────────────────────────────────────────────────────────

corr_plot = corr_df.sort_values("r_all")
y = np.arange(len(corr_plot))
w = 0.26

fig, ax = plt.subplots(figsize=(10, 7))
ax.barh(y,        corr_plot["r_all"],    w, label="All children",  color="#475569", alpha=0.85)
ax.barh(y + w,    corr_plot["r_nonsnap"],w, label="Non-SNAP",      color="#0f766e", alpha=0.85)
ax.barh(y + w*2,  corr_plot["r_snap"],   w, label="SNAP",          color="#b45309", alpha=0.85)

ax.set_yticks(y + w)
ax.set_yticklabels(corr_plot["label"].values, fontsize=9)
ax.axvline(0, color="black", linewidth=0.8, linestyle="--", alpha=0.5)
ax.set_xlabel("Pearson r with highest grade completed", fontsize=10)
ax.set_title(
    "Which Predictors Correlate Most Strongly with Grade Completion?\nBy SNAP Receipt Status",
    fontsize=11, fontweight="bold"
)
ax.legend(fontsize=9)
ax.grid(axis="x", linestyle=":", alpha=0.35)
plt.subplots_adjust(top=0.88, left=0.27)
save_fig(fig, OUTPUT_DIR / "correlation_ranking.png", tight=False)

# ── Full OLS model ────────────────────────────────────────────────────────────

def run_ols(data, group_label):
    needed   = [OUTCOME] + FULL_CONTROLS
    clean    = data.dropna(subset=[OUTCOME]).copy()
    use_vars = [v for v in FULL_CONTROLS if v in clean.columns and clean[v].notna().sum() >= 100]
    formula  = f"{OUTCOME} ~ " + " + ".join(use_vars)
    fit      = smf.ols(formula, data=clean.dropna(subset=use_vars)).fit(cov_type="HC3")
    ci       = fit.conf_int()

    rows = []
    for v in use_vars:
        if v not in fit.params.index:
            continue
        rows.append({
            "variable": v,
            "label":    CONTROL_LABELS.get(v, v),
            "coef":     fit.params[v],
            "ci_low":   ci.loc[v, 0],
            "ci_high":  ci.loc[v, 1],
            "p_value":  fit.pvalues[v],
            "group":    group_label,
            "n":        int(fit.nobs),
            "r2":       round(fit.rsquared, 3),
        })
    print(f"\n{group_label}: n={int(fit.nobs):,}  R²={fit.rsquared:.3f}")
    return pd.DataFrame(rows)

nonsnap_df = run_ols(nonsnap, "Non-SNAP")
snap_df    = run_ols(snap,    "SNAP")

reg_results = pd.concat([nonsnap_df, snap_df], ignore_index=True)
reg_results.to_csv(OUTPUT_DIR / "full_regression_results.csv", index=False)
print(f"\nSaved: {OUTPUT_DIR / 'full_regression_results.csv'}")

# ── Full model coefficient plot ───────────────────────────────────────────────

shared = set(nonsnap_df["variable"]) & set(snap_df["variable"])
ns = nonsnap_df[nonsnap_df["variable"].isin(shared)].set_index("variable")
s  = snap_df[snap_df["variable"].isin(shared)].set_index("variable")
order = ns["coef"].sort_values().index.tolist()
labels_ordered = [CONTROL_LABELS.get(v, v) for v in order]
y = np.arange(len(order))

fig2, ax2 = plt.subplots(figsize=(10, 7))

for grp_df, color, label, offset in [
    (ns, "#0f766e", "Non-SNAP", -0.15),
    (s,  "#b45309", "SNAP",      0.15),
]:
    coefs     = [grp_df.loc[v, "coef"]   if v in grp_df.index else np.nan for v in order]
    errs_low  = [grp_df.loc[v, "coef"] - grp_df.loc[v, "ci_low"]  if v in grp_df.index else np.nan for v in order]
    errs_high = [grp_df.loc[v, "ci_high"] - grp_df.loc[v, "coef"] if v in grp_df.index else np.nan for v in order]
    sig       = [grp_df.loc[v, "p_value"] < 0.05 if v in grp_df.index else False for v in order]

    ax2.errorbar(coefs, y + offset,
        xerr=[errs_low, errs_high],
        fmt="o", color=color, label=label,
        capsize=4, markersize=6, linewidth=1.4)

    for i, (c, is_sig) in enumerate(zip(coefs, sig)):
        if is_sig and not np.isnan(c):
            ax2.text(c, y[i] + offset + 0.22, "✦",
                     ha="center", fontsize=7, color=color, alpha=0.9)

ax2.axvline(0, color="black", linewidth=0.9, linestyle="--", alpha=0.5)
ax2.set_yticks(y)
ax2.set_yticklabels(labels_ordered, fontsize=9)
ax2.set_xlabel("OLS coefficient — effect on highest grade\n✦ = significant at p<0.05  |  HC3 robust SEs", fontsize=9)
ax2.set_title(
    "Full Model: All Predictors of Grade Completion\nSNAP vs. Non-SNAP Children",
    fontsize=11, fontweight="bold"
)
ax2.legend(fontsize=10)
ax2.grid(axis="x", linestyle=":", alpha=0.35)

n_ns = int(nonsnap_df["n"].iloc[0])
n_s  = int(snap_df["n"].iloc[0])
r2_ns = nonsnap_df["r2"].iloc[0]
r2_s  = snap_df["r2"].iloc[0]
ax2.text(0.98, 0.02,
    f"Non-SNAP: n={n_ns:,}, R²={r2_ns}\nSNAP: n={n_s:,}, R²={r2_s}",
    transform=ax2.transAxes, ha="right", va="bottom", fontsize=8,
    bbox=dict(boxstyle="square,pad=0.3", fc="white", ec="#ccc"))

plt.subplots_adjust(left=0.27, top=0.88)
save_fig(fig2, OUTPUT_DIR / "full_regression_coef_plot.png", tight=False)

print("\n05_full_regression_all_predictors.py complete.")
print("Next step: run 06_maps_geographic_analysis.py")
