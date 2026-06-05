"""
table1_descriptive.py
QSS 20 Final Project — Molly Ryan

PURPOSE:
    Generate Table 1 — descriptive statistics by SNAP status.
    For each variable: mean and SD for each group, difference,
    t-test p-value, and significance stars.
    Outputs both a CSV and a LaTeX table for Overleaf.

INPUT:
    data/processed/nlscya_qss20_cleaned_subset_full.csv

OUTPUT:
    output/table1_descriptive.csv
    output/table1_descriptive.tex
"""

import pandas as pd
import numpy as np
from scipy import stats
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from utils import load_clean, make_analysis_frame

# ── Paths ─────────────────────────────────────────────────────────────────────

IN_PATH    = Path("data/processed/nlscya_qss20_cleaned_subset_full.csv")
OUTPUT_DIR = Path("output")
OUTPUT_DIR.mkdir(exist_ok=True)

# ── Load data ─────────────────────────────────────────────────────────────────

df  = load_clean(IN_PATH)
reg = make_analysis_frame(df)

snap    = reg[reg["snap_ever"] == 1]
nonsnap = reg[reg["snap_ever"] == 0]

# ── Variables to include in Table 1 ──────────────────────────────────────────

# (variable_name, display_label, decimal_places)
VARIABLES = [
    ("highest_grade",  "Highest grade completed",      2),
    ("mother_educ",    "Mother's education (grades)",   2),
    ("mother_age",     "Mother's age at birth",         2),
    ("birth_order",    "Birth order",                   2),
    ("birth_year",     "Birth year",                    1),
    ("female",         "Female (%)",                    1),
    ("black",          "Black (%)",                     1),
    ("hispanic",       "Hispanic (%)",                  1),
    ("father_in_hh",   "Father in household (%)",       1),
    ("ppvt_avg",       "Avg PPVT verbal score",         1),
    ("math_avg",       "Avg math score",                1),
]

# ── Helper: significance stars ────────────────────────────────────────────────

def stars(p):
    if p < 0.001: return "***"
    if p < 0.01:  return "**"
    if p < 0.05:  return "*"
    return ""

# ── Build table ───────────────────────────────────────────────────────────────

rows = []
for var, label, dp in VARIABLES:
    if var not in reg.columns:
        continue

    s  = snap[var].dropna()
    ns = nonsnap[var].dropna()

    if len(s) < 2 or len(ns) < 2:
        continue

    mean_s  = s.mean()
    mean_ns = ns.mean()
    sd_s    = s.std()
    sd_ns   = ns.std()
    diff    = mean_s - mean_ns

    # Two-sided t-test (assumes unequal variance — Welch's t-test)
    t_stat, p_val = stats.ttest_ind(s, ns, equal_var=False)

    # For percentage variables multiply by 100
    is_pct = var in ["female", "black", "hispanic", "father_in_hh"]
    if is_pct:
        mean_s  *= 100
        mean_ns *= 100
        sd_s    *= 100
        sd_ns   *= 100
        diff    *= 100

    fmt = f".{dp}f"
    rows.append({
        "Variable":          label,
        "Non-SNAP mean":     f"{mean_ns:{fmt}}",
        "Non-SNAP SD":       f"({sd_ns:{fmt}})",
        "SNAP mean":         f"{mean_s:{fmt}}",
        "SNAP SD":           f"({sd_s:{fmt}})",
        "Difference":        f"{diff:+.{dp}f}",
        "p-value":           f"{p_val:.3f}",
        "Sig":               stars(p_val),
        "N (Non-SNAP)":      len(ns),
        "N (SNAP)":          len(s),
    })

table = pd.DataFrame(rows)

print("\nTable 1: Descriptive Statistics by SNAP Status")
print(table.to_string(index=False))

table.to_csv(OUTPUT_DIR / "table1_descriptive.csv", index=False)
print(f"\nSaved: {OUTPUT_DIR / 'table1_descriptive.csv'}")

# ── LaTeX output ──────────────────────────────────────────────────────────────

latex_rows = []
for _, row in table.iterrows():
    latex_rows.append(
        f"    {row['Variable']} & "
        f"{row['Non-SNAP mean']} {row['Non-SNAP SD']} & "
        f"{row['SNAP mean']} {row['SNAP SD']} & "
        f"{row['Difference']} & "
        f"{row['p-value']}{row['Sig']} \\\\"
    )

n_ns = int(nonsnap["snap_ever"].notna().sum())
n_s  = int(snap["snap_ever"].notna().sum())

latex = f"""\\begin{{table}}[htbp]
\\centering
\\caption{{Descriptive Statistics by Childhood SNAP Receipt}}
\\label{{tab:descriptive}}
\\small
\\begin{{tabular}}{{lcccc}}
\\hline\\hline
 & Non-SNAP & SNAP & Difference & p-value \\\\
 & (n={n_ns:,}) & (n={n_s:,}) & & \\\\
 & Mean (SD) & Mean (SD) & & \\\\
\\hline
{chr(10).join(latex_rows)}
\\hline\\hline
\\end{{tabular}}
\\begin{{tablenotes}}
\\small
\\item Notes: Means and standard deviations reported. Percentage variables (Female, Black, Hispanic,
Father in household) are displayed as percentages. Differences are SNAP minus non-SNAP.
p-values from two-sided Welch's t-tests assuming unequal variances.
*** p$<$0.001, ** p$<$0.01, * p$<$0.05.
\\end{{tablenotes}}
\\end{{table}}"""

tex_path = OUTPUT_DIR / "table1_descriptive.tex"
tex_path.write_text(latex)
print(f"Saved: {tex_path}")
print("\nPaste the contents of output/table1_descriptive.tex directly into Overleaf.")
