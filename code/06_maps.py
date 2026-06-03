"""
QSS 20 — US Choropleth Maps by Census Region (no state lines, region outlines only)

Uses geopandas to dissolve US states into 4 Census regions,
then plots with matplotlib so we get clean region outlines only.

Maps produced:
  map_snap_rate_by_region.png
  map_avg_grade_by_region.png
  map_snap_avg_grade.png
  map_nonsnap_avg_grade.png
  map_grade_gap_snap_vs_nonsnap.png  ← key finding map
"""

import pandas as pd
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import geopandas as gpd
from pathlib import Path

output_dir = Path("../output")
output_dir.mkdir(exist_ok=True)

# ── 1. Load NLSCYA data ───────────────────────────────────────────────────────

geo_path = Path("../data/processed/nlscya_qss20_cleaned_subset_geo.csv")
df = pd.read_csv(geo_path, low_memory=False)

neg_codes = [-1,-2,-3,-4,-5,-7,-8,-9]
df["snap_ever"]     = pd.to_numeric(df["any_snap"], errors="coerce")
df["highest_grade"] = pd.to_numeric(df["highest_grade_category"], errors="coerce").replace(neg_codes, np.nan)

# ── 2. Compute region statistics ──────────────────────────────────────────────

overall = (
    df.dropna(subset=["region","highest_grade"])
    .groupby("region")
    .agg(n=("highest_grade","count"),
         avg_grade=("highest_grade","mean"),
         snap_rate=("snap_ever","mean"))
    .reset_index()
)

by_snap = (
    df.dropna(subset=["region","snap_ever","highest_grade"])
    .groupby(["region","snap_ever"])["highest_grade"]
    .mean()
    .unstack("snap_ever")
    .rename(columns={0.0:"nonsnap_grade", 1.0:"snap_grade"})
    .reset_index()
)
by_snap["grade_gap"] = by_snap["nonsnap_grade"] - by_snap["snap_grade"]

region_stats = overall.merge(by_snap, on="region", how="left").round(3)
print("Region statistics:")
print(region_stats)

# ── 3. Build region GeoDataFrame ──────────────────────────────────────────────

STATE_TO_REGION = {
    "Connecticut":"Northeast","Maine":"Northeast","Massachusetts":"Northeast",
    "New Hampshire":"Northeast","New Jersey":"Northeast","New York":"Northeast",
    "Pennsylvania":"Northeast","Rhode Island":"Northeast","Vermont":"Northeast",
    "Illinois":"Midwest","Indiana":"Midwest","Iowa":"Midwest","Kansas":"Midwest",
    "Michigan":"Midwest","Minnesota":"Midwest","Missouri":"Midwest","Nebraska":"Midwest",
    "North Dakota":"Midwest","Ohio":"Midwest","South Dakota":"Midwest","Wisconsin":"Midwest",
    "Alabama":"South","Arkansas":"South","Delaware":"South","Florida":"South",
    "Georgia":"South","Kentucky":"South","Louisiana":"South","Maryland":"South",
    "Mississippi":"South","North Carolina":"South","Oklahoma":"South",
    "South Carolina":"South","Tennessee":"South","Texas":"South","Virginia":"South",
    "West Virginia":"South","District of Columbia":"South",
    "Alaska":"West","Arizona":"West","California":"West","Colorado":"West",
    "Hawaii":"West","Idaho":"West","Montana":"West","Nevada":"West",
    "New Mexico":"West","Oregon":"West","Utah":"West","Washington":"West",
    "Wyoming":"West",
}

# Download US states shapefile from Census (low resolution, fast)
print("\nDownloading US states shapefile...")
states_gdf = gpd.read_file(
    "https://www2.census.gov/geo/tiger/GENZ2018/shp/cb_2018_us_state_20m.zip"
)

# Keep contiguous US only (drop AK, HI, PR, territories)
contiguous = states_gdf[~states_gdf["NAME"].isin(["Alaska","Hawaii","Puerto Rico",
    "United States Virgin Islands","Guam","Commonwealth of the Northern Mariana Islands",
    "American Samoa"])]

contiguous = contiguous.copy()
contiguous["region"] = contiguous["NAME"].map(STATE_TO_REGION)
contiguous = contiguous.dropna(subset=["region"])

# Dissolve states into regions
regions_gdf = contiguous.dissolve(by="region").reset_index()
regions_gdf = regions_gdf.merge(region_stats, on="region", how="left")

print("Regions GeoDataFrame:")
print(regions_gdf[["region","avg_grade","snap_rate","grade_gap"]])

# ── 4. Map helper ─────────────────────────────────────────────────────────────

def save_region_map(gdf, value_col, title, colorbar_label, filename,
                    cmap, vmin, vmax, annotation=None):

    fig, ax = plt.subplots(1, 1, figsize=(11, 6.5))

    gdf.plot(
        column        = value_col,
        ax            = ax,
        cmap          = cmap,
        vmin          = vmin,
        vmax          = vmax,
        edgecolor     = "white",
        linewidth     = 2.0,
        legend        = True,
        legend_kwds   = dict(
            label     = colorbar_label,
            orientation = "vertical",
            shrink    = 0.6,
            pad       = 0.02,
            fraction  = 0.03,
        ),
    )

    # Label each region with name + value
    for _, row in gdf.iterrows():
        centroid = row.geometry.centroid
        val = row[value_col]
        if pd.isna(val):
            continue
        ax.annotate(
            f"{row['region']}\n{val:.2f}",
            xy         = (centroid.x, centroid.y),
            ha         = "center",
            va         = "center",
            fontsize   = 9,
            fontweight = "bold",
            color      = "white",
            bbox       = dict(boxstyle="round,pad=0.2", fc="none", ec="none"),
        )

    ax.set_axis_off()
    ax.set_title(title, fontsize=14, fontweight="bold", pad=15)

    if annotation:
        fig.text(0.5, 0.02, annotation, ha="center", fontsize=8, color="#555")

    plt.tight_layout()
    out = output_dir / filename
    plt.savefig(out, dpi=150, bbox_inches="tight", facecolor="white")
    plt.close()
    print(f"Saved: {out}")


# ── 5. Draw the maps ──────────────────────────────────────────────────────────

save_region_map(
    regions_gdf,
    value_col      = "snap_rate",
    title          = "SNAP Receipt Rate by Census Region",
    colorbar_label = "SNAP rate (0–1)",
    filename       = "map_snap_rate_by_region.png",
    cmap           = "Reds",
    vmin=0.15, vmax=0.50,
    annotation     = "NLSCYA children, 1994–2018. Contiguous US only.",
)

save_region_map(
    regions_gdf,
    value_col      = "avg_grade",
    title          = "Average Highest Grade Completed by Census Region",
    colorbar_label = "Avg grade  (12=HS, 16=BA)",
    filename       = "map_avg_grade_by_region.png",
    cmap           = "Blues",
    vmin=11, vmax=14,
    annotation     = "All NLSCYA children.",
)

save_region_map(
    regions_gdf,
    value_col      = "snap_grade",
    title          = "Average Highest Grade — SNAP Children",
    colorbar_label = "Avg grade  (12=HS, 16=BA)",
    filename       = "map_snap_avg_grade.png",
    cmap           = "Oranges",
    vmin=10, vmax=13,
    annotation     = "Children with any SNAP/Food Stamp receipt.",
)

save_region_map(
    regions_gdf,
    value_col      = "nonsnap_grade",
    title          = "Average Highest Grade — Non-SNAP Children",
    colorbar_label = "Avg grade  (12=HS, 16=BA)",
    filename       = "map_nonsnap_avg_grade.png",
    cmap           = "Blues",
    vmin=11, vmax=14,
    annotation     = "Children with no SNAP/Food Stamp receipt.",
)

save_region_map(
    regions_gdf,
    value_col      = "grade_gap",
    title          = "Education Gap: Non-SNAP vs. SNAP Children\nby Census Region",
    colorbar_label = "Grade gap (non-SNAP minus SNAP)",
    filename       = "map_grade_gap_snap_vs_nonsnap.png",
    cmap           = "YlOrRd",
    vmin=0, vmax=2.5,
    annotation     = "Larger value = bigger education gap between non-SNAP and SNAP children.",
)

print("\nAll maps saved to:", output_dir)
