"""
01_clean_data.py
QSS 20 Final Project — Molly Ryan

RESEARCH QUESTION:
    Do predictors of educational attainment differ by childhood SNAP receipt?

PURPOSE:
    Load the raw NLSCYA (1979–2018) CSV, extract key variables, recode
    NLS missing values, and construct the primary analysis variables.
    This is the first step in the pipeline — all downstream scripts
    depend on the output of this file.

    TANF/AFDC is retained in the cleaned file for documentation purposes
    but is excluded from all analysis. TANF had too few participants
    for reliable comparison and is not part of this study's research question.

INPUT:
    data/raw/nlscya_all_1979-2018.csv
    (Raw NLSCYA data — not tracked in git due to file size ~2.8 GB.
     Download from: https://www.nlsinfo.org/investigator/pages/search)

OUTPUT:
    data/processed/nlscya_qss20_cleaned_subset.csv

KEY VARIABLES CONSTRUCTED:
    Outcome
        highest_grade_category  : highest grade completed (numeric, 0–20)

    Primary grouping variable
        any_snap                : child ever in SNAP household (binary)
        snap_wave_count         : number of waves with SNAP receipt

    Family background
        mother_educ_latest      : mother's education, most recent wave
        father_in_hh_any        : father ever present in household (binary)

    Demographics
        race / female           : recoded from numeric NLS codes

    Note: TANF variables are constructed but NOT used in analysis.
"""

import pandas as pd
import numpy as np
import sys
from pathlib import Path

# Allow imports from code/ directory
sys.path.insert(0, str(Path(__file__).parent))
from utils import NEG_CODES, print_coverage

# ── Paths ─────────────────────────────────────────────────────────────────────

RAW_PATH = Path("data/raw/nlscya_all_1979-2018.csv")
OUT_PATH = Path("data/processed/nlscya_qss20_cleaned_subset.csv")
OUT_PATH.parent.mkdir(parents=True, exist_ok=True)

if not RAW_PATH.exists():
    raise FileNotFoundError(
        f"Raw data not found at {RAW_PATH}.\n"
        "Download from https://www.nlsinfo.org/investigator/pages/search"
    )

# ── Raw variable IDs (from NLS codebook) ─────────────────────────────────────

ID_COL      = "C0000100"
MOTHER_ID   = "C0000200"
SEX_COL     = "C0000300"
BMONTH_COL  = "C0000400"
BYEAR_COL   = "C0000500"
BORDER_COL  = "C0000600"
RACE_COL    = "C0000700"
MAGEBIR_COL = "C0000800"

HIGHEST_GRADE_COL  = "C0001000"
HIGHEST_DEGREE_COL = "C0001100"

# SNAP receipt per wave (primary grouping variable)
SNAP_COLS = {
    1994: "C1266300", 1996: "C1571700", 1998: "C1990500",
    2000: "C2510000", 2002: "C2603100", 2004: "C2864400",
    2006: "C3359900", 2008: "C3871200", 2010: "C5109800",
    2012: "C5692700", 2014: "C5850900", 2016: "C6219900",
    2018: "C6561700",
}

# TANF — retained for documentation only, excluded from analysis
# (n too small for reliable split-sample comparison)
TANF_COLS = {
    1994: "C1270300", 1996: "C1574100", 1998: "C1992900",
    2000: "C2512400", 2002: "C2605500", 2004: "C2866800",
    2006: "C3362300", 2008: "C3873600", 2010: "C5112200",
    2012: "C5695100", 2014: "C5853300", 2016: "C6222300",
    2018: "C6564100",
}

MOTHER_EDUC_COLS = {
    1979: "R0214800", 1994: "C1267100", 2006: "C3374100",
    2008: "C3884700", 2012: "C5706800",
}

FATHER_HH_COLS = {
    1994: "C1265000", 1996: "C1570400", 1998: "C1989200",
    2000: "C2508700", 2002: "C2601800", 2004: "C2863100",
    2006: "C3358600",
}

# ── Load raw data (only needed columns) ──────────────────────────────────────

print("Loading raw data...")
all_needed = (
    {ID_COL, MOTHER_ID, SEX_COL, BMONTH_COL, BYEAR_COL,
     BORDER_COL, RACE_COL, MAGEBIR_COL, HIGHEST_GRADE_COL, HIGHEST_DEGREE_COL}
    | set(SNAP_COLS.values())
    | set(TANF_COLS.values())
    | set(MOTHER_EDUC_COLS.values())
    | set(FATHER_HH_COLS.values())
)

raw = pd.read_csv(RAW_PATH, usecols=lambda c: c in all_needed, low_memory=False)
print(f"  Loaded {raw.shape[0]:,} rows, {raw.shape[1]} columns")

# Replace NLS negative missing codes with NaN
for col in raw.select_dtypes("number").columns:
    raw[col] = raw[col].replace(NEG_CODES, np.nan)

# ── Build cleaned dataframe ───────────────────────────────────────────────────

df = pd.DataFrame()

# Core identifiers and demographics
df["child_id"]           = raw[ID_COL]
df["mother_id"]          = raw[MOTHER_ID]
df["sex_code"]           = raw[SEX_COL]
df["birth_month"]        = raw[BMONTH_COL]
df["birth_year"]         = raw[BYEAR_COL]
df["birth_order"]        = raw[BORDER_COL]
df["race_code"]          = raw[RACE_COL]
df["mother_age_at_birth"]= raw[MAGEBIR_COL]

# Education outcome (primary dependent variable)
df["highest_grade_category"] = raw[HIGHEST_GRADE_COL]
df["highest_degree_code"]    = raw[HIGHEST_DEGREE_COL]

# Readable race and sex labels
df["race"]   = df["race_code"].map({1: "Hispanic", 2: "Black", 3: "Non-Black, Non-Hispanic"})
df["sex"]    = df["sex_code"].map({1: "Male", 2: "Female"})
df["female"] = (df["sex"] == "Female").astype(float)

# ── SNAP receipt per wave ─────────────────────────────────────────────────────

for year, col in SNAP_COLS.items():
    if col in raw.columns:
        df[f"snap_{year}"] = (raw[col] == 1).astype(float).where(raw[col].notna(), np.nan)

snap_wave_cols = [f"snap_{y}" for y in SNAP_COLS if f"snap_{y}" in df.columns]
df["valid_snap_waves"] = df[snap_wave_cols].notna().sum(axis=1)
df["snap_wave_count"]  = df[snap_wave_cols].sum(axis=1, skipna=True)
df["any_snap"]         = (df["snap_wave_count"] > 0).astype(float).where(
                             df["valid_snap_waves"] > 0, np.nan)

print(f"\nSNAP group sizes:")
print(df["any_snap"].value_counts(dropna=False).to_string())

# ── TANF receipt (constructed but excluded from analysis) ─────────────────────

for year, col in TANF_COLS.items():
    if col in raw.columns:
        df[f"tanf_{year}"] = (raw[col] == 1).astype(float).where(raw[col].notna(), np.nan)

tanf_wave_cols = [f"tanf_{y}" for y in TANF_COLS if f"tanf_{y}" in df.columns]
df["tanf_wave_count"] = df[tanf_wave_cols].sum(axis=1, skipna=True)
df["any_tanf"]        = (df["tanf_wave_count"] > 0).astype(float).where(
                             df[[f"tanf_{y}" for y in TANF_COLS if f"tanf_{y}" in df.columns]].notna().sum(axis=1) > 0,
                             np.nan)

print(f"\nTANF group sizes (excluded from analysis — small n):")
print(df["any_tanf"].value_counts(dropna=False).to_string())

# ── Education outcome variables ───────────────────────────────────────────────

# Grade-based thresholds (used for reference, main outcome is continuous)
grade = df["highest_grade_category"]
df["hs_or_more"]        = (grade >= 12).astype(float).where(grade.notna(), np.nan)
df["associates_or_more"]= (grade >= 14).astype(float).where(grade.notna(), np.nan)
df["bachelors_or_more"] = (grade >= 16).astype(float).where(grade.notna(), np.nan)

# ── Mother's education (latest available wave) ────────────────────────────────

for year, col in MOTHER_EDUC_COLS.items():
    if col in raw.columns:
        df[f"mother_educ_{year}"] = raw[col]

educ_cols_ordered = [f"mother_educ_{y}"
                     for y in sorted(MOTHER_EDUC_COLS.keys(), reverse=True)
                     if f"mother_educ_{y}" in df.columns]
df["mother_educ_latest"] = df[educ_cols_ordered].bfill(axis=1).iloc[:, 0]

# ── Father in household (any wave) ───────────────────────────────────────────

for year, col in FATHER_HH_COLS.items():
    if col in raw.columns:
        df[f"father_in_hh_{year}"] = (raw[col] == 1).astype(float).where(raw[col].notna(), np.nan)

fhh_cols = [f"father_in_hh_{y}" for y in FATHER_HH_COLS if f"father_in_hh_{y}" in df.columns]
df["father_in_hh_wave_count"] = df[fhh_cols].sum(axis=1, skipna=True)
df["father_in_hh_any"]        = (df["father_in_hh_wave_count"] > 0).astype(float).where(
                                     df[fhh_cols].notna().sum(axis=1) > 0, np.nan)

# ── Save ──────────────────────────────────────────────────────────────────────

df.to_csv(OUT_PATH, index=False)
print(f"\nSaved: {OUT_PATH}")
print(f"Shape: {df.shape[0]:,} rows × {df.shape[1]} columns")

print_coverage(df, [
    "any_snap", "any_tanf",
    "highest_grade_category",
    "mother_educ_latest",
    "father_in_hh_any",
])

print("\n01_clean_data.py complete.")
print("Next step: run 02_extract_geography.py")
