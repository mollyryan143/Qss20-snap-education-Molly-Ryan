"""
QSS 20 — Full regression: highest grade completed
Outcome: highest_grade
Variables: demographics, family, geography, cognitive scores, work frequency

Two analyses:
  1. Correlation ranking — which variables have the strongest raw correlation
     with highest grade, separately for SNAP and non-SNAP groups
  2. OLS regression — all variables together, split by SNAP status
     so we can compare how each factor relates to grades in each group
"""

import pandas as pd
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import statsmodels.formula.api as smf
from pathlib import Path

output_dir = Path("../output")
output_dir.mkdir(exist_ok=True)

# ── 1. Load data ──────────────────────────────────────────────────────────────

path = Path("../data/processed/nlscya_qss20_cleaned_subset_full.csv")
df = pd.read_csv(path, low_memory=False)
print("Loaded:", df.shape)

neg_codes = [-1,-2,-3,-4,-5,-7,-8,-9]
for col in df.select_dtypes("number").columns:
    df[col] = df[col].replace(neg_codes, np.nan)

# Outcome
df["highest_grade"] = pd.to_numeric(df["highest_grade_category"], errors="coerce")

# Demographics
df["snap_ever"]    = pd.to_numeric(df["any_snap"],            errors="coerce")
df["female"]       = pd.to_numeric(df["female"],              errors="coerce")
df["black"]        = (df["race"] == "Black").astype(float)
df["hispanic"]     = (df["race"] == "Hispanic").astype(float)
df["birth_year"]   = pd.to_numeric(df["birth_year"],          errors="coerce")
df["birth_order"]  = pd.to_numeric(df["birth_order"],         errors="coerce")

# Family
df["mother_educ"]  = pd.to_numeric(df["mother_educ_latest"],  errors="coerce")
df["mother_age"]   = pd.to_numeric(df["mother_age_at_birth"], errors="coerce")
df["father_in_hh"] = pd.to_numeric(df["father_in_hh_any"],   errors="coerce")

# Geography
df["urban"] = (df["urban_rural"] == "Urban").astype(float).where(df["urban_rural"].notna(), np.nan)
df["south"] = (df["region"] == "South").astype(float).where(df["region"].notna(), np.nan)
df["west"]  = (df["region"] == "West").astype(float).where(df["region"].notna(), np.nan)
df["midwest"]= (df["region"] == "Midwest").astype(float).where(df["region"].notna(), np.nan)

# Cognitive + work
df["ppvt_avg"]      = pd.to_numeric(df["ppvt_avg"],      errors="coerce")
df["math_avg"]      = pd.to_numeric(df["math_avg"],      errors="coerce")
df["avg_work_freq"] = pd.to_numeric(df["avg_work_freq"], errors="coerce")

# ── 2. Define all variables with readable labels ──────────────────────────────

ALL_VARS = {
    # Cognitive
    "ppvt_avg":      "Avg verbal score (PPVT)",
    "math_avg":      "Avg math score",
    # Demographics
    "female":        "Female",
    "black":         "Black",
    "hispanic":      "Hispanic",
    "birth_year":    "Birth year",
    "birth_order":   "Birth order",
    # Family
    "mother_educ":   "Mother's education",
    "mother_age":    "Mother's age at birth",
    "father_in_hh":  "Father in household",
    # Geography
    "urban":         "Urban residence",
    "south":         "South region",
    "west":          "West region",
    "midwest":       "Midwest region",
    # Work
    "avg_work_freq": "Work frequency (lower=more)",
}

CONTROLS = list(ALL_VARS.keys())
OUTCOME  = "highest_grade"

print(f"\nSample sizes:")
print(f"  Total with outcome: {df[OUTCOME].notna().sum()}")
print(f"  SNAP group:         {((df['snap_ever']==1) & df[OUTCOME].notna()).sum()}")
print(f"  Non-SNAP group:     {((df['snap_ever']==0) & df[OUTCOME].notna()).sum()}")

# ── 3. Correlation table ──────────────────────────────────────────────────────
# Raw Pearson correlation of each variable with highest_grade,
# split by SNAP vs non-SNAP

snap    = df[df["snap_ever"] == 1]
nonsnap = df[df["snap_ever"] == 0]

corr_rows = []
for var, label in ALL_VARS.items():
    r_all    = df[[var, OUTCOME]].dropna()[var].corr(df[[var, OUTCOME]].dropna()[OUTCOME])
    r_snap   = snap[[var, OUTCOME]].dropna()[var].corr(snap[[var, OUTCOME]].dropna()[OUTCOME])
    r_nonsnap= nonsnap[[var, OUTCOME]].dropna()[var].corr(nonsnap[[var, OUTCOME]].dropna()[OUTCOME])
    n_snap   = snap[[var, OUTCOME]].dropna().shape[0]
    n_nonsnap= nonsnap[[var, OUTCOME]].dropna().shape[0]
    corr_rows.append({
        "variable":       var,
        "label":          label,
        "r_all":          round(r_all, 3),
        "r_snap":         round(r_snap, 3),
        "r_nonsnap":      round(r_nonsnap, 3),
        "diff":           round(r_snap - r_nonsnap, 3),
        "n_snap":         n_snap,
        "n_nonsnap":      n_nonsnap,
    })

corr_df = pd.DataFrame(corr_rows).sort_values("r_all", ascending=False)
print("\n── Correlations with highest grade completed ──")
print(corr_df[["label","r_all","r_snap","r_nonsnap","diff"]].to_string(index=False))
corr_df.to_csv(output_dir / "correlation_ranking.csv", index=False)

# ── 4. Plot: correlation ranking ──────────────────────────────────────────────

fig, ax = plt.subplots(figsize=(10, 7))

corr_plot = corr_df.sort_values("r_all")
y = np.arange(len(corr_plot))
w = 0.28

bars_all    = ax.barh(y,          corr_plot["r_all"],    w, label="All children",  color="#555555", alpha=0.85)
bars_nonsnap= ax.barh(y + w,      corr_plot["r_nonsnap"],w, label="Non-SNAP",      color="#2196F3", alpha=0.85)
bars_snap   = ax.barh(y + w*2,    corr_plot["r_snap"],   w, label="SNAP",          color="#F44336", alpha=0.85)

ax.set_yticks(y + w)
ax.set_yticklabels(corr_plot["label"].values, fontsize=9)
ax.axvline(0, color="black", linewidth=0.8, linestyle="--", alpha=0.5)
ax.set_xlabel("Pearson correlation with highest grade completed", fontsize=10)
ax.set_title(
    "Correlation Between Each Variable and Highest Grade Completed\nSNAP vs. Non-SNAP Children",
    fontsize=12, fontweight="bold"
)
ax.legend(fontsize=9, loc="lower right")
ax.grid(axis="x", linestyle=":", alpha=0.4)
plt.subplots_adjust(top=0.90, left=0.28)
plt.savefig(output_dir / "correlation_ranking.png", dpi=150, bbox_inches="tight")
plt.close()
print(f"\nSaved: {output_dir / 'correlation_ranking.png'}")

# ── 5. OLS regressions ────────────────────────────────────────────────────────
# Run separately for SNAP and non-SNAP, using all variables with enough coverage

def run_ols(data, label):
    needed = [OUTCOME] + CONTROLS
    clean  = data.dropna(subset=[OUTCOME]).copy()

    # Drop vars with <100 non-missing in this subsample
    use_vars = []
    for v in CONTROLS:
        n = clean[v].notna().sum()
        if n >= 100:
            use_vars.append(v)
        else:
            print(f"  [{label}] Dropping {v} — only {n} non-missing")

    formula = f"{OUTCOME} ~ " + " + ".join(use_vars)
    clean2  = clean.dropna(subset=use_vars)
    fit     = smf.ols(formula, data=clean2).fit(cov_type="HC3")
    ci      = fit.conf_int()

    rows = []
    for v in use_vars:
        if v not in fit.params.index:
            continue
        rows.append({
            "variable": v,
            "label":    ALL_VARS[v],
            "coef":     fit.params[v],
            "ci_low":   ci.loc[v, 0],
            "ci_high":  ci.loc[v, 1],
            "p_value":  fit.pvalues[v],
            "group":    label,
            "n":        int(fit.nobs),
            "r2":       round(fit.rsquared, 3),
        })

    print(f"\n  {label}: n={int(fit.nobs)}, R²={fit.rsquared:.3f}")
    return pd.DataFrame(rows), fit

print("\n── OLS regressions ──")
nonsnap_df, nonsnap_fit = run_ols(nonsnap, "Non-SNAP")
snap_df,    snap_fit    = run_ols(snap,    "SNAP")

reg_results = pd.concat([nonsnap_df, snap_df], ignore_index=True)
reg_results.to_csv(output_dir / "full_regression_results.csv", index=False)

# Print ranked by absolute coefficient (all children pooled for ranking)
print("\n── Non-SNAP coefficients ranked by size ──")
print(nonsnap_df.sort_values("coef", ascending=False)[
    ["label","coef","ci_low","ci_high","p_value"]].round(3).to_string(index=False))

print("\n── SNAP coefficients ranked by size ──")
print(snap_df.sort_values("coef", ascending=False)[
    ["label","coef","ci_low","ci_high","p_value"]].round(3).to_string(index=False))

# ── 6. Plot: OLS coefficient comparison ──────────────────────────────────────

# Only plot variables present in both groups
shared_vars = set(nonsnap_df["variable"]) & set(snap_df["variable"])
ns = nonsnap_df[nonsnap_df["variable"].isin(shared_vars)].set_index("variable")
s  = snap_df[snap_df["variable"].isin(shared_vars)].set_index("variable")

# Sort by non-SNAP coefficient
order = ns["coef"].sort_values().index.tolist()
labels_ordered = [ALL_VARS[v] for v in order]
y = np.arange(len(order))

fig2, ax2 = plt.subplots(figsize=(10, 7))

for grp_df, color, label, offset in [
    (ns, "#2196F3", "Non-SNAP", -0.15),
    (s,  "#F44336", "SNAP",      0.15),
]:
    coefs     = [grp_df.loc[v, "coef"]   if v in grp_df.index else np.nan for v in order]
    errs_low  = [grp_df.loc[v, "coef"] - grp_df.loc[v, "ci_low"]  if v in grp_df.index else np.nan for v in order]
    errs_high = [grp_df.loc[v, "ci_high"] - grp_df.loc[v, "coef"] if v in grp_df.index else np.nan for v in order]
    sig       = [grp_df.loc[v, "p_value"] < 0.05 if v in grp_df.index else False for v in order]

    ax2.errorbar(
        coefs, y + offset,
        xerr=[errs_low, errs_high],
        fmt="o", color=color, label=label,
        capsize=4, markersize=6, linewidth=1.4,
        markeredgecolor="white", markeredgewidth=0.5,
    )

    # Mark significant results with a star
    for i, (c, is_sig) in enumerate(zip(coefs, sig)):
        if is_sig and not np.isnan(c):
            ax2.text(c, y[i] + offset + 0.22, "★", ha="center",
                     fontsize=7, color=color, alpha=0.9)

ax2.axvline(0, color="black", linewidth=0.9, linestyle="--", alpha=0.5)
ax2.set_yticks(y)
ax2.set_yticklabels(labels_ordered, fontsize=9)
ax2.set_xlabel("OLS coefficient — effect on highest grade completed\n★ = significant at p < 0.05  |  Robust standard errors",
               fontsize=9)
ax2.set_title(
    "What Predicts Highest Grade Completed?\nSNAP vs. Non-SNAP Children — Full Model",
    fontsize=12, fontweight="bold"
)
ax2.legend(fontsize=10, framealpha=0.9)
ax2.grid(axis="x", linestyle=":", alpha=0.35)

# Add R² annotations
n_ns = int(nonsnap_df["n"].iloc[0])
n_s  = int(snap_df["n"].iloc[0])
r2_ns = nonsnap_df["r2"].iloc[0]
r2_s  = snap_df["r2"].iloc[0]
ax2.text(0.98, 0.02,
    f"Non-SNAP: n={n_ns:,}, R²={r2_ns:.3f}\nSNAP: n={n_s:,}, R²={r2_s:.3f}",
    transform=ax2.transAxes, ha="right", va="bottom",
    fontsize=8, color="#333",
    bbox=dict(boxstyle="round,pad=0.3", fc="white", ec="#ccc", alpha=0.8)
)

plt.subplots_adjust(top=0.90, left=0.28)
plt.savefig(output_dir / "full_regression_coef_plot.png", dpi=150, bbox_inches="tight")
plt.close()
print(f"\nSaved: {output_dir / 'full_regression_coef_plot.png'}")

# ── 7. Summary table: top correlations ───────────────────────────────────────

print("\n── Top 5 strongest correlations with highest grade ──")
print("  Overall:")
top5 = corr_df.reindex(corr_df["r_all"].abs().sort_values(ascending=False).index).head(5)
for _, row in top5.iterrows():
    print(f"    {row['label']:<35} r = {row['r_all']:+.3f}")

print("  Within SNAP group:")
top5s = corr_df.reindex(corr_df["r_snap"].abs().sort_values(ascending=False).index).head(5)
for _, row in top5s.iterrows():
    print(f"    {row['label']:<35} r = {row['r_snap']:+.3f}")

print("  Within non-SNAP group:")
top5n = corr_df.reindex(corr_df["r_nonsnap"].abs().sort_values(ascending=False).index).head(5)
for _, row in top5n.iterrows():
    print(f"    {row['label']:<35} r = {row['r_nonsnap']:+.3f}")

print(f"\nDone. Outputs saved to: {output_dir}")
