"""
QSS 20 — SNAP vs. Non-SNAP: How control variables relate to highest grade completed

Single outcome: highest_grade (continuous, 0–20 scale)
  Grade 12 = HS diploma
  Grade 14 = Associate's
  Grade 16 = Bachelor's
  Grade 18+ = Graduate degree

Two analyses:
  1. Split-sample OLS: same model run separately on SNAP and non-SNAP kids
  2. Interaction model: one regression with snap_ever × each control term
"""

import pandas as pd
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Patch
import statsmodels.formula.api as smf
from pathlib import Path

output_dir = Path("../output")
output_dir.mkdir(exist_ok=True)

# ── 0. Load data ──────────────────────────────────────────────────────────────

csv_path = Path("../data/processed/nlscya_qss20_cleaned_subset_geo.csv")
if not csv_path.exists():
    csv_path = Path("../data/processed/nlscya_qss20_cleaned_subset.csv")

df = pd.read_csv(csv_path, low_memory=False)
print("Loaded:", df.shape)

# ── 1. Build analysis frame ───────────────────────────────────────────────────

reg = df.copy()

neg_codes = [-1, -2, -3, -4, -5, -7, -8, -9]
for col in reg.select_dtypes("number").columns:
    reg[col] = reg[col].replace(neg_codes, np.nan)

# Single outcome
reg["highest_grade"] = pd.to_numeric(reg["highest_grade_category"], errors="coerce")

# Predictors
reg["snap_ever"]   = pd.to_numeric(reg["any_snap"],            errors="coerce")
reg["female"]      = pd.to_numeric(reg["female"],              errors="coerce")
reg["mother_educ"] = pd.to_numeric(reg["mother_educ_latest"],  errors="coerce")
reg["birth_order"] = pd.to_numeric(reg["birth_order"],         errors="coerce")
reg["birth_year"]  = pd.to_numeric(reg["birth_year"],          errors="coerce")
reg["mother_age"]  = pd.to_numeric(reg["mother_age_at_birth"], errors="coerce")
reg["father_in_hh"]= pd.to_numeric(reg["father_in_hh_any"],   errors="coerce")
reg["black"]       = (reg["race"] == "Black").astype(float)
reg["hispanic"]    = (reg["race"] == "Hispanic").astype(float)

print("\nSNAP group sizes:")
print(reg["snap_ever"].value_counts(dropna=False))
print(f"\nHighest grade — mean: {reg['highest_grade'].mean():.2f}, "
      f"range: {reg['highest_grade'].min():.0f}–{reg['highest_grade'].max():.0f}")

CONTROLS = [
    "female", "black", "hispanic",
    "birth_year", "birth_order",
    "mother_age", "mother_educ", "father_in_hh",
]

CONTROL_LABELS = {
    "female":       "Female",
    "black":        "Black",
    "hispanic":     "Hispanic",
    "birth_year":   "Birth year",
    "birth_order":  "Birth order",
    "mother_age":   "Mother's age at birth",
    "mother_educ":  "Mother's education (grades)",
    "father_in_hh": "Father in household (ever)",
}

OUTCOME      = "highest_grade"
OUTCOME_LABEL= "Highest grade completed\n(12=HS, 14=Associate's, 16=Bachelor's)"

# ── 2. Descriptive table ──────────────────────────────────────────────────────

snap_means    = reg[reg["snap_ever"] == 1][CONTROLS + [OUTCOME]].mean()
nonsnap_means = reg[reg["snap_ever"] == 0][CONTROLS + [OUTCOME]].mean()

means_table = pd.DataFrame({
    "Non-SNAP mean": nonsnap_means,
    "SNAP mean":     snap_means,
    "Difference":    snap_means - nonsnap_means,
}).rename(index={**CONTROL_LABELS, OUTCOME: "Highest grade completed"})

print("\n── Descriptive means: SNAP vs. Non-SNAP ──")
print(means_table.round(3).to_string())
means_table.round(3).to_csv(output_dir / "snap_nonsnap_means_table.csv")
print(f"Saved: {output_dir / 'snap_nonsnap_means_table.csv'}")

# ── 3. Split-sample OLS ───────────────────────────────────────────────────────

formula = f"{OUTCOME} ~ " + " + ".join(CONTROLS)
needed  = [OUTCOME] + CONTROLS + ["snap_ever"]
clean   = reg.dropna(subset=needed).copy()

split_rows = []
for snap_val, group_label in [(0, "Non-SNAP"), (1, "SNAP")]:
    sub = clean[clean["snap_ever"] == snap_val]
    fit = smf.ols(formula, data=sub).fit(cov_type="HC3")
    ci  = fit.conf_int()
    print(f"\n{group_label} (n={int(fit.nobs)}): R²={fit.rsquared:.3f}")
    for term in CONTROLS:
        split_rows.append({
            "group":   group_label,
            "term":    term,
            "label":   CONTROL_LABELS[term],
            "coef":    fit.params.get(term, np.nan),
            "ci_low":  ci.loc[term, 0] if term in ci.index else np.nan,
            "ci_high": ci.loc[term, 1] if term in ci.index else np.nan,
            "n":       int(fit.nobs),
        })

split_df = pd.DataFrame(split_rows)
print("\n── Split-sample results ──")
print(split_df[["group","label","coef","ci_low","ci_high"]].round(3).to_string(index=False))
split_df.to_csv(output_dir / "split_sample_results.csv", index=False)

# ── 4. Plot: split-sample coefficient comparison ──────────────────────────────

labels  = [CONTROL_LABELS[c] for c in CONTROLS]
y_pos   = np.arange(len(labels))
colors  = {"Non-SNAP": "#2196F3", "SNAP": "#F44336"}
offsets = {"Non-SNAP": -0.18, "SNAP": 0.18}

fig, ax = plt.subplots(figsize=(9, 6))

for group in ["Non-SNAP", "SNAP"]:
    sub = split_df[split_df["group"] == group].set_index("label")
    coefs     = [sub.loc[l, "coef"]    for l in labels]
    errs_low  = [sub.loc[l, "coef"] - sub.loc[l, "ci_low"]  for l in labels]
    errs_high = [sub.loc[l, "ci_high"] - sub.loc[l, "coef"] for l in labels]
    ax.errorbar(
        coefs,
        y_pos + offsets[group],
        xerr=[errs_low, errs_high],
        fmt="o", color=colors[group], label=group,
        capsize=4, markersize=6, linewidth=1.4,
    )

ax.axvline(0, color="black", linewidth=0.9, linestyle="--", alpha=0.6)
ax.set_yticks(y_pos)
ax.set_yticklabels(labels, fontsize=10)
ax.set_xlabel("OLS coefficient — effect on highest grade completed\n(robust standard errors)", fontsize=9)
ax.legend(fontsize=10, framealpha=0.9)

# Add reference lines for meaningful grade thresholds
for grade, label_text in [(12, "HS"), (16, "BA")]:
    pass  # Grade thresholds are on y-axis, not x — skip

ax.set_title(
    "How Background Factors Relate to Education:\nSNAP vs. Non-SNAP Children",
    fontsize=12, fontweight="bold"
)
ax.grid(axis="x", linestyle=":", alpha=0.4)
plt.subplots_adjust(top=0.88, left=0.25)
plt.savefig(output_dir / "split_sample_coef_plot.png", dpi=150, bbox_inches="tight")
plt.close()
print(f"\nSaved: {output_dir / 'split_sample_coef_plot.png'}")

# ── 5. Interaction model ──────────────────────────────────────────────────────

main_terms        = " + ".join(CONTROLS)
interaction_terms = " + ".join([f"snap_ever:{c}" for c in CONTROLS])
int_formula = f"{OUTCOME} ~ snap_ever + {main_terms} + {interaction_terms}"

int_fit = smf.ols(int_formula, data=clean).fit(cov_type="HC3")
int_ci  = int_fit.conf_int()

int_rows = []
for c in CONTROLS:
    term = f"snap_ever:{c}"
    if term not in int_fit.params.index:
        term = f"{c}:snap_ever"
    if term not in int_fit.params.index:
        continue
    int_rows.append({
        "label":   CONTROL_LABELS[c],
        "coef":    int_fit.params[term],
        "ci_low":  int_ci.loc[term, 0],
        "ci_high": int_ci.loc[term, 1],
        "p_value": int_fit.pvalues[term],
    })

int_df = pd.DataFrame(int_rows).sort_values("coef")
int_df["significant"] = int_df["p_value"] < 0.05
print("\n── Interaction results (snap_ever × control) ──")
print(int_df[["label","coef","ci_low","ci_high","p_value","significant"]].round(3).to_string(index=False))
int_df.to_csv(output_dir / "interaction_results.csv", index=False)

# ── 6. Plot: interaction coefficients ─────────────────────────────────────────

fig2, ax2 = plt.subplots(figsize=(8, 6))

bar_colors = ["#D32F2F" if p < 0.05 else "#90A4AE" for p in int_df["p_value"]]
y2 = np.arange(len(int_df))

ax2.barh(y2, int_df["coef"], color=bar_colors, alpha=0.85, height=0.55)
ax2.errorbar(
    int_df["coef"], y2,
    xerr=[int_df["coef"] - int_df["ci_low"], int_df["ci_high"] - int_df["coef"]],
    fmt="none", color="black", capsize=4, linewidth=1.2,
)
ax2.axvline(0, color="black", linewidth=0.9, linestyle="--", alpha=0.6)
ax2.set_yticks(y2)
ax2.set_yticklabels(int_df["label"].values, fontsize=10)
ax2.set_xlabel("Interaction coefficient (SNAP × control)\nEffect on highest grade completed", fontsize=9)
ax2.grid(axis="x", linestyle=":", alpha=0.4)

legend_els = [
    Patch(facecolor="#D32F2F", label="Significant (p < 0.05)"),
    Patch(facecolor="#90A4AE", label="Not significant"),
]
ax2.legend(handles=legend_els, fontsize=10, framealpha=0.9)
ax2.set_title(
    "Does SNAP Status Change How Background Factors\nRelate to Education?",
    fontsize=12, fontweight="bold"
)
plt.subplots_adjust(top=0.88, left=0.25)
plt.savefig(output_dir / "interaction_coef_plot.png", dpi=150, bbox_inches="tight")
plt.close()
print(f"Saved: {output_dir / 'interaction_coef_plot.png'}")

print("\nDone. All outputs saved to:", output_dir)
