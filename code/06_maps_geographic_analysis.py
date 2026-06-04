"""
06_maps_geographic_analysis.py
QSS 20 Final Project — Molly Ryan

RESEARCH QUESTION:
    Do predictors of educational attainment differ by childhood SNAP receipt?

PURPOSE:
    Produce US choropleth maps showing how SNAP receipt rates and the
    education gap between SNAP and non-SNAP children vary geographically
    across the four U.S. Census regions.

    Because the NLSCYA public data does not include state identifiers,
    all states within a region share the same color — the map shows
    regional variation, not state-level variation.

    Method:
    - Download a U.S. Census TIGER shapefile (low-resolution, ~1MB)
    - Dissolve state boundaries into four Census regions using geopandas
    - Merge NLSCYA region statistics onto the region polygons
    - Plot choropleth maps with region outlines only (no state lines)

INPUT:
    data/processed/nlscya_qss20_cleaned_subset_geo.csv  (from script 02)

OUTPUT:
    output/map_snap_rate_by_region.png
    output/map_avg_grade_by_region.png
    output/map_snap_avg_grade.png
    output/map_nonsnap_avg_grade.png
    output/map_grade_gap_snap_vs_nonsnap.png
"""

import pandas as pd
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import geopandas as gpd
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from utils import load_clean, make_analysis_frame, save_fig, NEG_CODES, OUTCOME

# ── Paths ─────────────────────────────────────────────────────────────────────

IN_PATH    = Path("data/processed/nlscya_qss20_cleaned_subset_geo.csv")
OUTPUT_DIR = Path("output")
OUTPUT_DIR.mkdir(exist_ok=True)

# ── State to Census region mapping ────────────────────────────────────────────

STATE_TO_REGION = {
    "Connecticut":"Northeast","Maine":"Northeast","Massachusetts":"Northeast",
    "New Hampshire":"Northeast","New Jersey":"Northeast","New York":"Northeast",
    "Pennsylvania":"Northeast","Rhode Island":"Northeast","Vermont":"Northeast",
    "Illinois":"Midwest","Indiana":"Midwest","Iowa":"Midwest","Kansas":"Midwest",
    "Michigan":"Midwest","Minnesota":"Midwest","Missouri":"Midwest",
    "Nebraska":"Midwest","North Dakota":"Midwest","Ohio":"Midwest",
    "South Dakota":"Midwest","Wisconsin":"Midwest",
    "Alabama":"South","Arkansas":"South","Delaware":"South","Florida":"South",
    "Georgia":"South","Kentucky":"South","Louisiana":"South","Maryland":"South",
    "Mississippi":"South","North Carolina":"South","Oklahoma":"South",
    "South Carolina":"South","Tennessee":"South","Texas":"South",
    "Virginia":"South","West Virginia":"South","District of Columbia":"South",
    "Alaska":"West","Arizona":"West","California":"West","Colorado":"West",
    "Hawaii":"West","Idaho":"West","Montana":"West","Nevada":"West",
    "New Mexico":"West","Oregon":"West","Utah":"West","Washington":"West",
    "Wyoming":"West",
}

# ── Load NLSCYA data ──────────────────────────────────────────────────────────

df  = load_clean(IN_PATH)
reg = make_analysis_frame(df)
reg[OUTCOME] = reg[OUTCOME].replace(NEG_CODES, np.nan)

# ── Compute region statistics ─────────────────────────────────────────────────

overall = (
    reg.dropna(subset=["region", OUTCOME])
    .groupby("region")
    .agg(n=(OUTCOME, "count"), avg_grade=(OUTCOME, "mean"), snap_rate=("snap_ever", "mean"))
    .reset_index()
)

by_snap = (
    reg.dropna(subset=["region", "snap_ever", OUTCOME])
    .groupby(["region", "snap_ever"])[OUTCOME]
    .mean().unstack("snap_ever")
    .rename(columns={0.0: "nonsnap_grade", 1.0: "snap_grade"})
    .reset_index()
)
by_snap["grade_gap"] = by_snap["nonsnap_grade"] - by_snap["snap_grade"]

region_stats = overall.merge(by_snap, on="region", how="left").round(3)
print("\nRegion statistics:")
print(region_stats.to_string(index=False))

# ── Build region GeoDataFrame ─────────────────────────────────────────────────

print("\nDownloading U.S. Census TIGER shapefile...")
states_gdf = gpd.read_file(
    "https://www2.census.gov/geo/tiger/GENZ2018/shp/cb_2018_us_state_20m.zip"
)

# Contiguous US only
contiguous = states_gdf[~states_gdf["NAME"].isin([
    "Alaska", "Hawaii", "Puerto Rico",
    "United States Virgin Islands", "Guam",
    "Commonwealth of the Northern Mariana Islands", "American Samoa"
])].copy()

contiguous["region"] = contiguous["NAME"].map(STATE_TO_REGION)
contiguous = contiguous.dropna(subset=["region"])

regions_gdf = contiguous.dissolve(by="region").reset_index()
regions_gdf = regions_gdf.merge(region_stats, on="region", how="left")

# ── Map helper ────────────────────────────────────────────────────────────────

def save_region_map(gdf, value_col, title, colorbar_label, filename,
                    cmap, vmin, vmax, note=""):
    fig, ax = plt.subplots(figsize=(11, 6.5))

    gdf.plot(
        column=value_col, ax=ax, cmap=cmap,
        vmin=vmin, vmax=vmax, edgecolor="white", linewidth=2.0,
        legend=True,
        legend_kwds=dict(label=colorbar_label, orientation="vertical",
                         shrink=0.6, pad=0.02, fraction=0.03),
    )

    # Label each region
    for _, row in gdf.iterrows():
        centroid = row.geometry.centroid
        val = row[value_col]
        if pd.isna(val):
            continue
        ax.annotate(
            f"{row['region']}\n{val:.2f}",
            xy=(centroid.x, centroid.y),
            ha="center", va="center", fontsize=9, fontweight="bold",
            color="white",
        )

    ax.set_axis_off()
    ax.set_title(title, fontsize=13, fontweight="bold", pad=12)
    if note:
        fig.text(0.5, 0.02, note, ha="center", fontsize=8, color="#555")

    plt.tight_layout()
    save_fig(fig, OUTPUT_DIR / filename, tight=False)


# ── Produce maps ──────────────────────────────────────────────────────────────

save_region_map(regions_gdf, "snap_rate",
    "SNAP Receipt Rate by Census Region",
    "SNAP rate (0-1)", "map_snap_rate_by_region.png",
    "YlOrRd", 0.15, 0.50,
    note="NLSCYA children, 1994-2018. Contiguous US only.")

save_region_map(regions_gdf, "avg_grade",
    "Average Highest Grade Completed by Census Region",
    "Avg grade (12=HS, 16=BA)", "map_avg_grade_by_region.png",
    "Blues", 11, 14,
    note="All NLSCYA children.")

save_region_map(regions_gdf, "snap_grade",
    "Average Highest Grade — SNAP Children",
    "Avg grade (12=HS, 16=BA)", "map_snap_avg_grade.png",
    "Oranges", 10, 13,
    note="Children with any SNAP receipt.")

save_region_map(regions_gdf, "nonsnap_grade",
    "Average Highest Grade — Non-SNAP Children",
    "Avg grade (12=HS, 16=BA)", "map_nonsnap_avg_grade.png",
    "Blues", 11, 14,
    note="Children with no SNAP receipt.")

save_region_map(regions_gdf, "grade_gap",
    "Education Gap: Non-SNAP vs. SNAP Children by Census Region",
    "Grade gap (non-SNAP minus SNAP)", "map_grade_gap_snap_vs_nonsnap.png",
    "YlOrRd", 0, 2.5,
    note="Larger value = wider education gap between SNAP and non-SNAP children in that region.")

print("\n06_maps_geographic_analysis.py complete.")
print("All outputs saved to output/")
