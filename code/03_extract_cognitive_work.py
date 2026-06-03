"""
QSS 20 — Extract cognitive ability and child work variables from raw NLSCYA data
and merge into the cleaned geo subset.

Cognitive variables:
  PPVT (Peabody Picture Vocabulary Test) — language/verbal ability
  MATH — math achievement score
  Both available across waves 1986–2014. We take the average across all waves
  where the child was tested, giving a stable ability measure.

Child work variables (2002–2012):
  CS-WORKFORPAY  — did the child work for pay (binary)
  CS-EARNPERWK   — earnings per week
  CS-WORKFREQ    — how often they worked
  We summarize as: ever_worked (binary) and avg_earnings_per_week

Output: nlscya_qss20_cleaned_subset_full.csv
"""

import pandas as pd
import numpy as np
from pathlib import Path

output_dir  = Path("../output")
output_dir.mkdir(exist_ok=True)

raw_path     = Path("../data/raw/nlscya_all_1979-2018.csv")
cleaned_path = Path("../data/processed/nlscya_qss20_cleaned_subset_geo.csv")

# ── 1. Define variable IDs ────────────────────────────────────────────────────

ID_COL = "C0000100"

# PPVT raw scores by wave
PPVT_COLS = {
    1986: "C0580900", 1988: "C0800400", 1990: "C0999600", 1992: "C1199600",
    1994: "C1508600", 1996: "C1565500", 1998: "C1800900", 2000: "C2504400",
    2002: "C2532900", 2004: "C2803700", 2006: "C3112200", 2008: "C3615900",
    2010: "C3994500", 2012: "C5538500", 2014: "C5814300",
}

# Math raw scores by wave
MATH_COLS = {
    1986: "C0579900", 1988: "C0799400", 1990: "C0998600", 1992: "C1198600",
    1994: "C1507600", 1996: "C1564500", 1998: "C1799900", 2000: "C2503500",
    2002: "C2532000", 2004: "C2802800", 2006: "C3111300", 2008: "C3615000",
    2010: "C3993600", 2012: "C5537600", 2014: "C5813400",
}

# Child work variables by wave
WORK_FOR_PAY_COLS = {
    2002: "C2573900", 2004: "C2845500", 2006: "C3352300",
    2008: "C3856000", 2010: "C5104400", 2012: "C5681700",
}

EARN_PER_WK_COLS = {
    2002: "C2574300", 2004: "C2845900", 2006: "C3352700",
    2008: "C3856400", 2010: "C5104800", 2012: "C5682100",
}

WORK_FREQ_COLS = {
    2002: "C2574100", 2004: "C2845700", 2006: "C3352500",
    2008: "C3856200", 2010: "C5104600", 2012: "C5681900",
}

# ── 2. Find which columns exist in the CSV ────────────────────────────────────

print("Reading column names from raw file...")
raw_header = pd.read_csv(raw_path, nrows=0).columns.tolist()
raw_clean  = [c.strip('"') for c in raw_header]
raw_set    = set(raw_clean)

def find_cols(col_dict):
    found = {}
    for year, col in col_dict.items():
        if col in raw_set:
            found[year] = col
        else:
            print(f"  Missing: {col} ({year})")
    return found

print("\nPPVT columns:")
ppvt_found  = find_cols(PPVT_COLS)
print(f"  Found {len(ppvt_found)} waves")

print("\nMath columns:")
math_found  = find_cols(MATH_COLS)
print(f"  Found {len(math_found)} waves")

print("\nWork-for-pay columns:")
work_found  = find_cols(WORK_FOR_PAY_COLS)
earn_found  = find_cols(EARN_PER_WK_COLS)
freq_found  = find_cols(WORK_FREQ_COLS)
print(f"  Found {len(work_found)} waves")

# ── 3. Load only needed columns ───────────────────────────────────────────────

all_needed = (
    {ID_COL}
    | set(ppvt_found.values())
    | set(math_found.values())
    | set(work_found.values())
    | set(earn_found.values())
    | set(freq_found.values())
)

print(f"\nLoading {len(all_needed)} columns from raw file...")
raw = pd.read_csv(
    raw_path,
    usecols=lambda c: c.strip('"') in all_needed,
    low_memory=False,
)
raw.columns = [c.strip('"') for c in raw.columns]
print("Raw subset shape:", raw.shape)

# ── 4. Clean negative missing codes ──────────────────────────────────────────

NEG = [-1, -2, -3, -4, -5, -7, -8, -9]
for col in raw.columns:
    if col != ID_COL:
        raw[col] = pd.to_numeric(raw[col], errors="coerce").replace(NEG, np.nan)

# ── 5. Cognitive scores — average across waves ────────────────────────────────

# Average PPVT score across all waves where tested
ppvt_cols_list = list(ppvt_found.values())
math_cols_list = list(math_found.values())

raw["ppvt_avg"] = raw[ppvt_cols_list].mean(axis=1, skipna=True)
raw["math_avg"] = raw[math_cols_list].mean(axis=1, skipna=True)

# Also take the EARLIEST available score (childhood baseline)
def earliest_valid(row, cols_by_year):
    for year in sorted(cols_by_year.keys()):
        col = cols_by_year[year]
        if col in row.index and pd.notna(row[col]) and row[col] > 0:
            return row[col]
    return np.nan

raw["ppvt_earliest"] = raw.apply(lambda r: earliest_valid(r, ppvt_found), axis=1)
raw["math_earliest"] = raw.apply(lambda r: earliest_valid(r, math_found),  axis=1)

print("\nCognitive score summary:")
print(raw[["ppvt_avg","math_avg","ppvt_earliest","math_earliest"]].describe().round(2))

# ── 6. Work variables — summarize across waves ────────────────────────────────

work_cols_list = list(work_found.values())
earn_cols_list = list(earn_found.values())
freq_cols_list = list(freq_found.values())

# Ever worked for pay across any wave
raw["ever_worked"] = (
    raw[work_cols_list]
    .apply(lambda col: col.map({1: 1, 0: 0}))
    .max(axis=1)
)

# Average weekly earnings across waves where they worked
raw["avg_earn_per_wk"] = raw[earn_cols_list].mean(axis=1, skipna=True)

# Average work frequency (1=regularly, 2=sometimes, 3=rarely — lower = more)
raw["avg_work_freq"] = raw[freq_cols_list].mean(axis=1, skipna=True)

print("\nWork variable summary:")
print(raw[["ever_worked","avg_earn_per_wk","avg_work_freq"]].describe().round(2))

print("\nEver worked distribution:")
print(raw["ever_worked"].value_counts(dropna=False))

# ── 7. Build merge frame ──────────────────────────────────────────────────────

new_vars = raw[[
    ID_COL,
    "ppvt_avg", "math_avg",
    "ppvt_earliest", "math_earliest",
    "ever_worked", "avg_earn_per_wk", "avg_work_freq",
]].rename(columns={ID_COL: "child_id"})

# ── 8. Merge into cleaned geo file ───────────────────────────────────────────

cleaned = pd.read_csv(cleaned_path, low_memory=False)
print(f"\nCleaned data before merge: {cleaned.shape}")

full = cleaned.merge(new_vars, on="child_id", how="left")
print(f"Merged data shape:         {full.shape}")

# Coverage check
for col in ["ppvt_avg","math_avg","ppvt_earliest","math_earliest","ever_worked","avg_earn_per_wk"]:
    n = full[col].notna().sum()
    pct = n / len(full) * 100
    print(f"  {col}: {n} non-missing ({pct:.1f}%)")

# ── 9. Save ───────────────────────────────────────────────────────────────────

out_path = Path("../data/processed/nlscya_qss20_cleaned_subset_full.csv")
full.to_csv(out_path, index=False)
print(f"\nSaved full dataset: {out_path}")
print(f"Columns: {full.shape[1]}  |  Rows: {full.shape[0]}")
print("\nNew variables added:")
for col in ["ppvt_avg","math_avg","ppvt_earliest","math_earliest",
            "ever_worked","avg_earn_per_wk","avg_work_freq"]:
    print(f"  {col}")
print("\nDone.")
