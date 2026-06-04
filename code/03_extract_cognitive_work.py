"""
03_extract_cognitive_work.py
QSS 20 Final Project — Molly Ryan

RESEARCH QUESTION:
    Do predictors of educational attainment differ by childhood SNAP receipt?

PURPOSE:
    Extract cognitive ability scores and child work variables from the raw
    NLSCYA data across multiple survey waves. These variables extend the
    analysis beyond basic demographics and family structure to test whether
    cognitive ability and early work experience predict grade completion
    differently for SNAP vs. non-SNAP children.

COGNITIVE VARIABLES:
    ppvt_avg        : Average PPVT verbal score across all tested waves (1986-2014)
    math_avg        : Average math achievement score across all tested waves
    ppvt_earliest   : First recorded PPVT score (childhood baseline)
    math_earliest   : First recorded math score (childhood baseline)
    Coverage: ~80-82% of sample

WORK VARIABLES (2002-2012):
    ever_worked     : Child ever worked for pay (binary)
    avg_earn_per_wk : Average weekly earnings
    avg_work_freq   : Average work frequency (lower = more frequent)
    Coverage: ~28% (only asked of older children in later waves)

INPUT:
    data/raw/nlscya_all_1979-2018.csv
    data/processed/nlscya_qss20_cleaned_subset_geo.csv  (from script 02)

OUTPUT:
    data/processed/nlscya_qss20_cleaned_subset_full.csv
"""

import pandas as pd
import numpy as np
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from utils import NEG_CODES, load_clean, print_coverage

# ── Paths ─────────────────────────────────────────────────────────────────────

RAW_PATH = Path("data/raw/nlscya_all_1979-2018.csv")
IN_PATH  = Path("data/processed/nlscya_qss20_cleaned_subset_geo.csv")
OUT_PATH = Path("data/processed/nlscya_qss20_cleaned_subset_full.csv")

ID_COL = "C0000100"

# ── Variable IDs by wave (from NLS codebook) ──────────────────────────────────

PPVT_COLS = {
    1986: "C0580900", 1988: "C0800400", 1990: "C0999600", 1992: "C1199600",
    1994: "C1508600", 1996: "C1565500", 1998: "C1800900", 2000: "C2504400",
    2002: "C2532900", 2004: "C2803700", 2006: "C3112200", 2008: "C3615900",
    2010: "C3994500", 2012: "C5538500", 2014: "C5814300",
}

MATH_COLS = {
    1986: "C0579900", 1988: "C0799400", 1990: "C0998600", 1992: "C1198600",
    1994: "C1507600", 1996: "C1564500", 1998: "C1799900", 2000: "C2503500",
    2002: "C2532000", 2004: "C2802800", 2006: "C3111300", 2008: "C3615000",
    2010: "C3993600", 2012: "C5537600", 2014: "C5813400",
}

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

# ── Helpers ───────────────────────────────────────────────────────────────────

def find_available_cols(col_dict, raw_set):
    """Return subset of col_dict whose values exist in raw_set."""
    return {yr: col for yr, col in col_dict.items() if col in raw_set}


def earliest_valid(row, cols_by_year):
    """Return the first non-missing, positive score across waves."""
    for year in sorted(cols_by_year.keys()):
        col = cols_by_year[year]
        if col in row.index and pd.notna(row[col]) and row[col] > 0:
            return row[col]
    return np.nan


# ── Identify available columns in raw file ────────────────────────────────────

print("Scanning raw file column names...")
raw_header = pd.read_csv(RAW_PATH, nrows=0).columns.tolist()
raw_set    = set(c.strip('"') for c in raw_header)

ppvt_found = find_available_cols(PPVT_COLS, raw_set)
math_found = find_available_cols(MATH_COLS, raw_set)
work_found = find_available_cols(WORK_FOR_PAY_COLS, raw_set)
earn_found = find_available_cols(EARN_PER_WK_COLS, raw_set)
freq_found = find_available_cols(WORK_FREQ_COLS, raw_set)

print(f"  PPVT waves:    {len(ppvt_found)}  {sorted(ppvt_found.keys())}")
print(f"  Math waves:    {len(math_found)}  {sorted(math_found.keys())}")
print(f"  Work waves:    {len(work_found)}  {sorted(work_found.keys())}")

# ── Load only needed columns ──────────────────────────────────────────────────

all_needed = (
    {ID_COL}
    | set(ppvt_found.values())
    | set(math_found.values())
    | set(work_found.values())
    | set(earn_found.values())
    | set(freq_found.values())
)

raw = pd.read_csv(RAW_PATH, usecols=lambda c: c.strip('"') in all_needed, low_memory=False)
raw.columns = [c.strip('"') for c in raw.columns]

for col in raw.columns:
    if col != ID_COL:
        raw[col] = pd.to_numeric(raw[col], errors="coerce").replace(NEG_CODES, np.nan)

print(f"  Loaded {raw.shape[0]:,} rows for extraction")

# ── Cognitive scores ──────────────────────────────────────────────────────────

raw["ppvt_avg"]      = raw[list(ppvt_found.values())].mean(axis=1, skipna=True)
raw["math_avg"]      = raw[list(math_found.values())].mean(axis=1, skipna=True)
raw["ppvt_earliest"] = raw.apply(lambda r: earliest_valid(r, ppvt_found), axis=1)
raw["math_earliest"] = raw.apply(lambda r: earliest_valid(r, math_found),  axis=1)

# ── Work variables ────────────────────────────────────────────────────────────

raw["ever_worked"]     = raw[list(work_found.values())].apply(
    lambda col: col.map({1: 1, 0: 0})).max(axis=1)
raw["avg_earn_per_wk"] = raw[list(earn_found.values())].mean(axis=1, skipna=True)
raw["avg_work_freq"]   = raw[list(freq_found.values())].mean(axis=1, skipna=True)

# ── Merge into geo file ───────────────────────────────────────────────────────

new_vars = raw[[ID_COL,
    "ppvt_avg", "math_avg", "ppvt_earliest", "math_earliest",
    "ever_worked", "avg_earn_per_wk", "avg_work_freq",
]].rename(columns={ID_COL: "child_id"})

cleaned = load_clean(IN_PATH)
full    = cleaned.merge(new_vars, on="child_id", how="left")

print(f"\nFinal dataset: {full.shape[0]:,} rows x {full.shape[1]} columns")
print_coverage(full, [
    "ppvt_avg", "math_avg", "ppvt_earliest", "math_earliest",
    "ever_worked", "avg_earn_per_wk", "avg_work_freq",
])

full.to_csv(OUT_PATH, index=False)
print(f"\nSaved: {OUT_PATH}")
print("Next step: run 04_regression_snap_vs_nonsnap.py")
