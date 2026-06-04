"""
02_extract_geography.py
QSS 20 Final Project — Molly Ryan

RESEARCH QUESTION:
    Do predictors of educational attainment differ by childhood SNAP receipt?

PURPOSE:
    Extract Census region and urban/rural status from the raw NLSCYA data
    across 13 survey waves (1994–2018). Each child is assigned their most
    commonly observed value across waves (modal assignment), which handles
    children whose family moved during the survey period.

    Geographic variables are used in two ways in this study:
      1. As control variables in the full regression model (script 05)
      2. As the basis for choropleth maps showing regional variation (script 06)

    NOTE: The NLSCYA public data does not include state-level identifiers.
    Geography is therefore limited to four U.S. Census regions.

INPUT:
    data/raw/nlscya_all_1979-2018.csv
    data/processed/nlscya_qss20_cleaned_subset.csv  (from script 01)

OUTPUT:
    data/processed/nlscya_qss20_cleaned_subset_geo.csv

REGION CODES (NLS standard):
    1 = Northeast  |  2 = Midwest  |  3 = South  |  4 = West

URBAN/RURAL CODES (NLS standard):
    0 = Rural  |  1 = Urban  |  2 = Unknown
"""

import pandas as pd
import numpy as np
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from utils import NEG_CODES, load_clean

# ── Paths ─────────────────────────────────────────────────────────────────────

RAW_PATH     = Path("data/raw/nlscya_all_1979-2018.csv")
IN_PATH      = Path("data/processed/nlscya_qss20_cleaned_subset.csv")
OUT_PATH     = Path("data/processed/nlscya_qss20_cleaned_subset_geo.csv")

ID_COL = "C0000100"

# ── Geographic variable IDs by wave (from NLS codebook) ──────────────────────

REGION_COLS = {
    1994: "Y0383801", 1996: "Y0678700", 1998: "Y0975500",
    2000: "Y1193000", 2002: "Y1435200", 2004: "Y1673400",
    2006: "Y1949200", 2008: "Y2267800", 2010: "Y2616700",
    2012: "Y2967200", 2014: "Y3332700", 2016: "Y3676500",
    2018: "Y4282500",
}

URBAN_COLS = {
    1994: "Y0384012", 1996: "Y0679808", 1998: "Y0975708",
    2000: "Y1204600", 2002: "Y1447600", 2004: "Y1676300",
    2006: "Y1972300", 2008: "Y2267900", 2010: "Y2616800",
    2012: "Y2967300", 2014: "Y3332800", 2016: "Y3676600",
    2018: "Y4282600",
}

REGION_LABELS = {1: "Northeast", 2: "Midwest", 3: "South", 4: "West"}
URBAN_LABELS  = {0: "Rural", 1: "Urban", 2: "Unknown"}

# ── Helper: find column name in raw file (handles quoted headers) ─────────────

def find_col(target, available):
    target = target.strip('"')
    for c in available:
        if c.strip('"') == target:
            return c
    return None


def most_common_valid(row, cols):
    """Return the modal non-missing value across a set of columns for one row."""
    vals = [int(row[c]) for c in cols
            if c in row.index and pd.notna(row[c]) and row[c] not in NEG_CODES]
    if not vals:
        return np.nan
    return max(set(vals), key=vals.count)


# ── Identify which columns exist in the raw file ──────────────────────────────

print("Scanning raw file column names...")
raw_cols       = pd.read_csv(RAW_PATH, nrows=0).columns.tolist()
raw_cols_clean = [c.strip('"') for c in raw_cols]

region_found = {}
urban_found  = {}
keep         = [ID_COL]

for year, col in REGION_COLS.items():
    match = find_col(col, raw_cols_clean)
    if match:
        region_found[year] = match
        keep.append(match)

for year, col in URBAN_COLS.items():
    match = find_col(col, raw_cols_clean)
    if match:
        urban_found[year] = match
        keep.append(match)

print(f"  Region waves found:     {sorted(region_found.keys())}")
print(f"  Urban/rural waves found:{sorted(urban_found.keys())}")

# ── Load only needed columns from raw ────────────────────────────────────────

raw = pd.read_csv(RAW_PATH, usecols=lambda c: c.strip('"') in keep, low_memory=False)
raw.columns = [c.strip('"') for c in raw.columns]
print(f"  Raw subset: {raw.shape[0]:,} rows × {raw.shape[1]} columns")

# ── Assign modal region and urban/rural per child ─────────────────────────────

print("\nAssigning modal region and urban/rural per child...")
region_cols_list = list(region_found.values())
urban_cols_list  = list(urban_found.values())

raw["region_modal"]      = raw.apply(lambda r: most_common_valid(r, region_cols_list), axis=1)
raw["urban_rural_modal"] = raw.apply(lambda r: most_common_valid(r, urban_cols_list),  axis=1)

raw["region"]     = raw["region_modal"].map(REGION_LABELS)
raw["urban_rural"]= raw["urban_rural_modal"].map(URBAN_LABELS)

geo = raw[[ID_COL, "region", "urban_rural"]].rename(columns={ID_COL: "child_id"})

print("\nRegion distribution:")
print(geo["region"].value_counts(dropna=False).to_string())
print("\nUrban/rural distribution:")
print(geo["urban_rural"].value_counts(dropna=False).to_string())

# ── Merge into cleaned subset ─────────────────────────────────────────────────

cleaned = load_clean(IN_PATH)
merged  = cleaned.merge(geo, on="child_id", how="left")

print(f"\nMerge complete: {merged.shape[0]:,} rows × {merged.shape[1]} columns")
print(f"  Region non-missing:     {merged['region'].notna().sum():,}")
print(f"  Urban/rural non-missing:{merged['urban_rural'].notna().sum():,}")

merged.to_csv(OUT_PATH, index=False)
print(f"\nSaved: {OUT_PATH}")
print("Next step: run 03_extract_cognitive_work.py")
