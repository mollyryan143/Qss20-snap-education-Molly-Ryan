"""
01_clean_data.py
QSS 20 Final Project — Molly Ryan

PURPOSE:
    Load the raw NLSCYA (1979–2018) CSV, identify and extract key variables,
    recode missing values, construct welfare exposure indicators, and save
    a cleaned subset for downstream analysis.

INPUT:
    data/raw/nlscya_all_1979-2018.csv   (raw NLSCYA data, not tracked in git)

OUTPUT:
    data/processed/nlscya_qss20_cleaned_subset.csv

VARIABLES CONSTRUCTED:
    - any_snap / any_tanf_afdc     : ever received SNAP or TANF (binary)
    - snap_wave_count               : number of waves with SNAP receipt
    - exposure_group                : Neither / SNAP only / TANF only / Both
    - hs_or_more_from_degree        : HS diploma or higher (binary)
    - bachelors_or_more_from_degree : bachelor's degree or higher (binary)
    - mother_educ_latest            : most recent mother education measure
    - father_in_hh_any              : father ever in household (binary)
    - race / sex / female           : recoded from numeric codes
"""

import pandas as pd
import numpy as np
from pathlib import Path

# ── Paths ─────────────────────────────────────────────────────────────────────

RAW_PATH     = Path("data/raw/nlscya_all_1979-2018.csv")
OUT_PATH     = Path("data/processed/nlscya_qss20_cleaned_subset.csv")
OUT_PATH.parent.mkdir(parents=True, exist_ok=True)

# ── Missing value codes (NLS standard) ───────────────────────────────────────

NEG_CODES = [-1, -2, -3, -4, -5, -7, -8, -9]

# ── Column mappings (raw variable ID → readable name) ────────────────────────

ID_COL      = "C0000100"   # child ID
MOTHER_ID   = "C0000200"   # mother ID
SEX_COL     = "C0000300"
BMONTH_COL  = "C0000400"
BYEAR_COL   = "C0000500"
BORDER_COL  = "C0000600"
RACE_COL    = "C0000700"
MAGEBIR_COL = "C0000800"

HIGHEST_GRADE_COL   = "C0001000"
HIGHEST_DEGREE_COL  = "C0001100"

SNAP_COLS = {
    1994: "C1266300", 1996: "C1571700", 1998: "C1990500",
    2000: "C2510000", 2002: "C2603100", 2004: "C2864400",
    2006: "C3359900", 2008: "C3871200", 2010: "C5109800",
    2012: "C5692700", 2014: "C5850900", 2016: "C6219900",
    2018: "C6561700",
}

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

# ── Load raw data ─────────────────────────────────────────────────────────────

print("Loading raw data...")
all_needed = (
    {ID_COL, MOTHER_ID, SEX_COL, BMONTH_COL, BYEAR_COL, BORDER_COL,
     RACE_COL, MAGEBIR_COL, HIGHEST_GRADE_COL, HIGHEST_DEGREE_COL}
    | set(SNAP_COLS.values())
    | set(TANF_COLS.values())
    | set(MOTHER_EDUC_COLS.values())
    | set(FATHER_HH_COLS.values())
)

raw = pd.read_csv(RAW_PATH, usecols=lambda c: c in all_needed, low_memory=False)
print(f"  Loaded {raw.shape[0]:,} rows, {raw.shape[1]} columns")

# ── Recode negatives as NaN ───────────────────────────────────────────────────

for col in raw.select_dtypes("number").columns:
    raw[col] = raw[col].replace(NEG_CODES, np.nan)

# ── Rename core columns ───────────────────────────────────────────────────────

df = pd.DataFrame()
df["child_id"]          = raw[ID_COL]
df["mother_id"]         = raw[MOTHER_ID]
df["sex_code"]          = raw[SEX_COL]
df["birth_month"]       = raw[BMONTH_COL]
df["birth_year"]        = raw[BYEAR_COL]
df["birth_order"]       = raw[BORDER_COL]
df["race_code"]         = raw[RACE_COL]
df["mother_age_at_birth"]= raw[MAGEBIR_COL]
df["highest_grade_category"] = raw[HIGHEST_GRADE_COL]
df["highest_degree_code"]    = raw[HIGHEST_DEGREE_COL]

# ── Race and sex labels ───────────────────────────────────────────────────────

df["race"] = df["race_code"].map({1: "Hispanic", 2: "Black", 3: "Non-Black, Non-Hispanic"})
df["sex"]  = df["sex_code"].map({1: "Male", 2: "Female"})
df["female"] = (df["sex"] == "Female").astype(float)

# ── SNAP and TANF wave variables ──────────────────────────────────────────────

for year, col in SNAP_COLS.items():
    if col in raw.columns:
        df[f"snap_{year}"] = (raw[col] == 1).astype(float).where(raw[col].notna(), np.nan)

for year, col in TANF_COLS.items():
    if col in raw.columns:
        df[f"tanf_afdc_{year}"] = (raw[col] == 1).astype(float).where(raw[col].notna(), np.nan)

# ── Aggregate welfare exposure ────────────────────────────────────────────────

snap_wave_cols = [f"snap_{y}" for y in SNAP_COLS if f"snap_{y}" in df.columns]
tanf_wave_cols = [f"tanf_afdc_{y}" for y in TANF_COLS if f"tanf_afdc_{y}" in df.columns]

df["valid_snap_waves"]     = df[snap_wave_cols].notna().sum(axis=1)
df["valid_tanf_afdc_waves"]= df[tanf_wave_cols].notna().sum(axis=1)
df["snap_wave_count"]      = df[snap_wave_cols].sum(axis=1, skipna=True)
df["tanf_afdc_wave_count"] = df[tanf_wave_cols].sum(axis=1, skipna=True)
df["any_snap"]      = (df["snap_wave_count"] > 0).astype(float).where(df["valid_snap_waves"] > 0, np.nan)
df["any_tanf_afdc"] = (df["tanf_afdc_wave_count"] > 0).astype(float).where(df["valid_tanf_afdc_waves"] > 0, np.nan)

conditions = [
    (df["any_snap"]==0) & (df["any_tanf_afdc"]==0),
    (df["any_snap"]==1) & (df["any_tanf_afdc"]==0),
    (df["any_snap"]==0) & (df["any_tanf_afdc"]==1),
    (df["any_snap"]==1) & (df["any_tanf_afdc"]==1),
]
df["exposure_group"] = np.select(conditions, ["Neither","SNAP only","TANF only","Both"], default=np.nan)

# ── Education outcomes ────────────────────────────────────────────────────────

grade = df["highest_grade_category"]
df["hs_or_more_from_grade"]        = (grade >= 12).astype(float).where(grade.notna(), np.nan)
df["associate_or_more_from_grade"] = (grade >= 14).astype(float).where(grade.notna(), np.nan)
df["bachelors_or_more_from_grade"] = (grade >= 16).astype(float).where(grade.notna(), np.nan)

deg = df["highest_degree_code"]
df["hs_or_more_from_degree"]        = (deg >= 1).astype(float).where(deg.notna(), np.nan)
df["associate_or_more_from_degree"] = (deg >= 3).astype(float).where(deg.notna(), np.nan)
df["bachelors_or_more_from_degree"] = (deg >= 4).astype(float).where(deg.notna(), np.nan)

# ── Mother education (latest available) ──────────────────────────────────────

for year, col in MOTHER_EDUC_COLS.items():
    if col in raw.columns:
        df[f"mother_educ_{year}"] = raw[col]

educ_cols_ordered = [f"mother_educ_{y}" for y in sorted(MOTHER_EDUC_COLS.keys(), reverse=True)
                     if f"mother_educ_{y}" in df.columns]
df["mother_educ_latest"]       = df[educ_cols_ordered].bfill(axis=1).iloc[:, 0]
df["mother_educ_baseline_1979"]= df.get("mother_educ_1979", np.nan)

# ── Father in household ───────────────────────────────────────────────────────

for year, col in FATHER_HH_COLS.items():
    if col in raw.columns:
        df[f"father_in_hh_{year}"] = (raw[col] == 1).astype(float).where(raw[col].notna(), np.nan)

fhh_cols = [f"father_in_hh_{y}" for y in FATHER_HH_COLS if f"father_in_hh_{y}" in df.columns]
df["valid_father_hh_waves"]  = df[fhh_cols].notna().sum(axis=1)
df["father_in_hh_wave_count"]= df[fhh_cols].sum(axis=1, skipna=True)
df["father_in_hh_any"]       = (df["father_in_hh_wave_count"] > 0).astype(float).where(
                                    df["valid_father_hh_waves"] > 0, np.nan)

# ── Save ──────────────────────────────────────────────────────────────────────

df.to_csv(OUT_PATH, index=False)
print(f"\nSaved: {OUT_PATH}")
print(f"  Shape: {df.shape[0]:,} rows × {df.shape[1]} columns")
print(f"\nKey variable coverage:")
for col in ["any_snap","any_tanf_afdc","highest_grade_category","mother_educ_latest","father_in_hh_any"]:
    n = df[col].notna().sum()
    print(f"  {col}: {n:,} ({n/len(df)*100:.1f}%)")

print("\n01_clean_data.py complete.")
