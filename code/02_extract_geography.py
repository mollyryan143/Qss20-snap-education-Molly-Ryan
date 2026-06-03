"""
QSS 20 — Extract region and urban/rural variables from raw NLSCYA data
and merge into the cleaned subset CSV.

Region codes (NLS standard):
  1 = Northeast
  2 = North Central / Midwest
  3 = South
  4 = West

Urban/Rural codes (NLS standard):
  0 = Rural
  1 = Urban
  2 = Unknown / other
"""

import pandas as pd
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from pathlib import Path

output_dir = Path("../output")
output_dir.mkdir(exist_ok=True)

raw_path     = Path("../data/raw/nlscya_all_1979-2018.csv")
cleaned_path = Path("../data/processed/nlscya_qss20_cleaned_subset.csv")

# ── 1. Load raw data (only the columns we need) ───────────────────────────────

# Child ID column
ID_COL = "C0000100"

# Region variable IDs by wave (from codebook)
REGION_COLS = {
    1994: "Y0383801",
    1996: "Y0678700",
    1998: "Y0975500",
    2000: "Y1193000",
    2002: "Y1435200",
    2004: "Y1673400",
    2006: "Y1949200",
    2008: "Y2267800",
    2010: "Y2616700",
    2012: "Y2967200",
    2014: "Y3332700",
    2016: "Y3676500",
    2018: "Y4282500",
}

# Urban/rural variable IDs by wave
URBAN_COLS = {
    1994: "Y0384012",
    1996: "Y0679808",
    1998: "Y0975708",
    2000: "Y1204600",
    2002: "Y1447600",
    2004: "Y1676300",
    2006: "Y1972300",
    2008: "Y2267900",
    2010: "Y2616800",
    2012: "Y2967300",
    2014: "Y3332800",
    2016: "Y3676600",
    2018: "Y4282600",
}

# Only keep columns that actually exist in the file
print("Reading column names from raw file...")
raw_cols = pd.read_csv(raw_path, nrows=0).columns.tolist()
raw_cols_clean = [c.strip('"') for c in raw_cols]

def find_col(target, available):
    target = target.strip('"')
    for c in available:
        if c.strip('"') == target:
            return c
    return None

keep = [ID_COL]
region_found, urban_found = {}, {}

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

# Strip quotes from actual header for reading
keep_quoted = [f'"{c}"' if f'"{c}"' in raw_cols else c for c in keep]

print(f"Region waves found: {sorted(region_found.keys())}")
print(f"Urban/rural waves found: {sorted(urban_found.keys())}")

print("\nLoading raw data columns...")
raw = pd.read_csv(raw_path, usecols=lambda c: c.strip('"') in keep, low_memory=False)
raw.columns = [c.strip('"') for c in raw.columns]
print("Raw subset shape:", raw.shape)

# ── 2. Take the most common non-missing value across waves ────────────────────
#
# We want one region and one urban/rural value per child.
# Strategy: use the most frequently observed non-missing value across all waves.
# This handles cases where a child moves between waves.

neg_codes = [-1, -2, -3, -4, -5, -7, -8, -9]

def most_common_valid(row, cols):
    vals = []
    for c in cols:
        if c in row.index:
            v = row[c]
            if pd.notna(v) and v not in neg_codes:
                vals.append(int(v))
    if not vals:
        return np.nan
    return max(set(vals), key=vals.count)

region_cols_list = list(region_found.values())
urban_cols_list  = list(urban_found.values())

print("\nComputing modal region and urban/rural per child...")
raw["region_modal"]     = raw.apply(lambda r: most_common_valid(r, region_cols_list), axis=1)
raw["urban_rural_modal"]= raw.apply(lambda r: most_common_valid(r, urban_cols_list),  axis=1)

# ── 3. Recode to readable labels ─────────────────────────────────────────────

REGION_LABELS = {1: "Northeast", 2: "Midwest", 3: "South", 4: "West"}
URBAN_LABELS  = {0: "Rural", 1: "Urban", 2: "Unknown"}

raw["region"]     = raw["region_modal"].map(REGION_LABELS)
raw["urban_rural"]= raw["urban_rural_modal"].map(URBAN_LABELS)

geo = raw[[ID_COL, "region", "urban_rural"]].rename(columns={ID_COL: "child_id"})

print("\nRegion distribution:")
print(geo["region"].value_counts(dropna=False))
print("\nUrban/rural distribution:")
print(geo["urban_rural"].value_counts(dropna=False))

# ── 4. Merge into cleaned subset ──────────────────────────────────────────────

cleaned = pd.read_csv(cleaned_path, low_memory=False)
print(f"\nCleaned data shape before merge: {cleaned.shape}")

merged = cleaned.merge(geo, on="child_id", how="left")
print(f"Merged data shape:               {merged.shape}")
print(f"Region non-missing: {merged['region'].notna().sum()}")
print(f"Urban/rural non-missing: {merged['urban_rural'].notna().sum()}")

# Save updated cleaned file
out_path = Path("../data/processed/nlscya_qss20_cleaned_subset_geo.csv")
merged.to_csv(out_path, index=False)
print(f"\nSaved: {out_path}")

# ── 5. Quick descriptive plots ────────────────────────────────────────────────

merged["snap_ever"]         = pd.to_numeric(merged["any_snap"], errors="coerce")
merged["highest_grade"]     = pd.to_numeric(merged["highest_grade_category"], errors="coerce")
merged["bachelors_or_more"] = pd.to_numeric(merged["bachelors_or_more_from_degree"], errors="coerce")

neg = [-1,-2,-3,-4,-5,-7,-8,-9]
for col in ["highest_grade","bachelors_or_more"]:
    merged[col] = merged[col].replace(neg, np.nan)

# Plot 1: SNAP rate by region
fig, axes = plt.subplots(1, 2, figsize=(12, 5))

snap_by_region = (
    merged.dropna(subset=["region","snap_ever"])
    .groupby("region")["snap_ever"]
    .agg(["mean","count"])
    .sort_values("mean")
)
axes[0].barh(snap_by_region.index, snap_by_region["mean"] * 100, color="#F44336")
axes[0].set_xlabel("% ever on SNAP")
axes[0].set_title("SNAP Receipt Rate by Region", fontweight="bold")
for i, (idx, row) in enumerate(snap_by_region.iterrows()):
    axes[0].text(row["mean"]*100 + 0.3, i, f'n={int(row["count"])}', va="center", fontsize=8)

snap_by_urban = (
    merged[merged["urban_rural"] != "Unknown"]
    .dropna(subset=["urban_rural","snap_ever"])
    .groupby("urban_rural")["snap_ever"]
    .agg(["mean","count"])
    .sort_values("mean")
)
axes[1].barh(snap_by_urban.index, snap_by_urban["mean"] * 100, color="#2196F3")
axes[1].set_xlabel("% ever on SNAP")
axes[1].set_title("SNAP Receipt Rate by Urban/Rural", fontweight="bold")
for i, (idx, row) in enumerate(snap_by_urban.iterrows()):
    axes[1].text(row["mean"]*100 + 0.3, i, f'n={int(row["count"])}', va="center", fontsize=8)

fig.suptitle("Geographic Variation in SNAP Receipt", fontsize=13, fontweight="bold")
plt.subplots_adjust(top=0.88)
plt.savefig(output_dir / "geo_snap_rates.png", dpi=150, bbox_inches="tight")
plt.close()
print(f"Saved: {output_dir / 'geo_snap_rates.png'}")

# Plot 2: Mean highest grade by region x SNAP status
fig2, axes2 = plt.subplots(1, 2, figsize=(12, 5))

for ax, geo_var, title in zip(
    axes2,
    ["region", "urban_rural"],
    ["Region", "Urban/Rural"]
):
    sub = merged[merged.get("urban_rural", pd.Series()) != "Unknown"] if geo_var == "urban_rural" else merged
    grp = (
        sub.dropna(subset=[geo_var, "snap_ever", "highest_grade"])
        .groupby([geo_var, "snap_ever"])["highest_grade"]
        .mean()
        .unstack("snap_ever")
        .rename(columns={0.0: "Non-SNAP", 1.0: "SNAP"})
    )
    x = np.arange(len(grp))
    w = 0.35
    ax.bar(x - w/2, grp.get("Non-SNAP", 0), w, label="Non-SNAP", color="#2196F3")
    ax.bar(x + w/2, grp.get("SNAP", 0),     w, label="SNAP",     color="#F44336")
    ax.set_xticks(x)
    ax.set_xticklabels(grp.index, rotation=20, ha="right")
    ax.set_ylabel("Mean highest grade completed")
    ax.set_title(f"Education by {title} and SNAP Status", fontweight="bold")
    ax.legend()
    ax.set_ylim(0, 16)

fig2.suptitle("Education Outcomes by Geography and SNAP Status", fontsize=13, fontweight="bold")
plt.subplots_adjust(top=0.88)
plt.savefig(output_dir / "geo_education_by_snap.png", dpi=150, bbox_inches="tight")
plt.close()
print(f"Saved: {output_dir / 'geo_education_by_snap.png'}")

print("\nDone. New cleaned file with geography saved to:")
print(f"  {out_path}")
