# Educational Attainment & Welfare in the United States
## QSS 20 Final Project — Molly Ryan, Dartmouth College, Spring 2026

### 🌐 [View the live project website →](https://molly-ryan-portfolio.netlify.app/)

---

## Research Question

**Do Predictors of Educational Attainment Differ by Childhood SNAP Receipt?**

Using longitudinal NLSY79 data, this study examines how a range of individual, family, and geographic factors relate to educational attainment — and whether those relationships differ by childhood SNAP receipt.

> This study identifies associations, not causes. SNAP receipt and educational outcomes are both shaped by underlying poverty and family circumstances. Findings describe patterns in the data and should not be interpreted as evidence that SNAP itself causes any particular outcome.

---

## Data

**NLSY79 Children and Young Adults (NLSCYA), 1979–2018**
- Unit of analysis: child respondents linked to NLSY79 mothers
- N = 11,545 children across biennial survey waves (1994–2018)
- Source: Bureau of Labor Statistics — https://www.nlsinfo.org/investigator/pages/search
- Raw data (~2.8 GB) is stored locally and **not tracked in this repository**
- Processed subsets are included in `data/processed/`

**Note on TANF:** TANF/AFDC is retained in the cleaning script for documentation but is **excluded from all analysis**. The TANF group is too small for reliable split-sample comparison. This study focuses exclusively on SNAP vs. non-SNAP.

---

## Repository Structure

```
├── code/
│   ├── utils.py                              # Shared helper functions and constants
│   ├── 01_clean_data.py                      # Input: raw NLSCYA CSV | Does: recodes missing values, constructs SNAP indicator, education outcome, family variables | Output: nlscya_qss20_cleaned_subset.csv
│   ├── 02_extract_geography.py               # Input: nlscya_qss20_cleaned_subset.csv | Does: extracts Census region + urban/rural across 13 waves, assigns modal value per child | Output: nlscya_qss20_cleaned_subset_geo.csv
│   ├── 03_extract_cognitive_work.py          # Input: nlscya_qss20_cleaned_subset_geo.csv | Does: averages PPVT and math scores across up to 15 waves, extracts child work variables | Output: nlscya_qss20_cleaned_subset_full.csv
│   ├── 04_regression_snap_vs_nonsnap.py      # Input: nlscya_qss20_cleaned_subset.csv | Does: split-sample OLS with HC3 SEs, interaction model, correlation ranking | Output: split_sample_results.csv, interaction_results.csv, correlation_ranking.csv, split_sample_coef_plot.png, interaction_coef_plot.png, correlation_ranking.png
│   ├── 05_full_regression_all_predictors.py  # Input: nlscya_qss20_cleaned_subset_full.csv | Does: full OLS model with cognitive + geographic predictors by SNAP group | Output: full_regression_results.csv, full_regression_coef_plot.png
│   └── 06_maps_geographic_analysis.py        # Input: nlscya_qss20_cleaned_subset_geo.csv + Census TIGER shapefile | Does: dissolves states to Census regions, merges sample stats, plots choropleth maps | Output: map_snap_rate_by_region.png, map_grade_gap_snap_vs_nonsnap.png, map_snap_avg_grade.png, map_nonsnap_avg_grade.png
│
├── data/
│   ├── raw/                                  # Raw NLSCYA files (NOT in git — too large; download from nlsinfo.org)
│   └── processed/
│       ├── nlscya_qss20_cleaned_subset.csv       # Core cleaned variables (01 output)
│       ├── nlscya_qss20_cleaned_subset_geo.csv   # + Census region + urban/rural (02 output)
│       └── nlscya_qss20_cleaned_subset_full.csv  # + cognitive scores + work variables (03 output)
│
└── output/
    ├── split_sample_coef_plot.png            # Core finding: OLS coefficients by SNAP group
    ├── interaction_coef_plot.png             # Interaction model: where slopes differ significantly
    ├── correlation_ranking.png               # Predictors ranked by correlation with outcome
    ├── full_regression_coef_plot.png         # Full model with cognitive + geographic controls
    ├── map_snap_rate_by_region.png           # SNAP receipt rate by Census region
    ├── map_avg_grade_by_region.png           # Average attainment score by region (all children)
    ├── map_snap_avg_grade.png                # Average attainment score — SNAP children
    ├── map_nonsnap_avg_grade.png             # Average attainment score — non-SNAP children
    ├── map_grade_gap_snap_vs_nonsnap.png     # Attainment gap between groups by region
    ├── split_sample_results.csv             # Split-sample OLS coefficients (tidy)
    ├── interaction_results.csv              # Interaction model coefficients (tidy)
    ├── full_regression_results.csv          # Full model coefficients (tidy)
    ├── correlation_ranking.csv              # Pearson correlations by group
    └── snap_nonsnap_means_table.csv         # Descriptive means: SNAP vs. non-SNAP
```

---

## Script Details

| Script | Input | What it does | Output |
|--------|-------|--------------|--------|
| `utils.py` | — | Shared constants and helper functions used across all scripts | — |
| `01_clean_data.py` | Raw NLSCYA CSV (82,318 cols) | Recodes NLS missing codes (−1 to −9) as NaN; constructs SNAP indicator, educational attainment outcome, and family background variables | `nlscya_qss20_cleaned_subset.csv` |
| `02_extract_geography.py` | `cleaned_subset.csv` | Identifies Census region and urban/rural variable IDs across 13 waves; assigns each child their modal value | `cleaned_subset_geo.csv` |
| `03_extract_cognitive_work.py` | `cleaned_subset_geo.csv` | Averages PPVT verbal and math scores across up to 15 tested waves; extracts child work-for-pay variables | `cleaned_subset_full.csv` |
| `04_regression_snap_vs_nonsnap.py` | `cleaned_subset.csv` | Runs split-sample OLS (HC3 SEs) and pooled interaction model; computes Pearson correlations by group | Coefficient CSVs + plots |
| `05_full_regression_all_predictors.py` | `cleaned_subset_full.csv` | Full OLS model with cognitive and geographic controls by SNAP group | Full regression CSV + plot |
| `06_maps_geographic_analysis.py` | `cleaned_subset_geo.csv` + TIGER shapefile | Downloads Census shapefile, dissolves to regions, merges sample stats, plots choropleth maps | Map PNGs |

---

## Key Findings

1. **Mother's education** is the strongest predictor overall (r = +0.317), but weaker for SNAP children (r = +0.278) than non-SNAP children (r = +0.326).

2. **Math scores** are nearly as predictive as mother's education (r = +0.303) and are actually stronger within the SNAP group (β = +0.10) than non-SNAP (β = +0.06).

3. **Being female** predicts higher attainment in both groups, with a larger gap for SNAP children (+0.94 scale points) than non-SNAP (+0.83 scale points).

4. **Father in household** has a significant positive effect for non-SNAP children (β = +0.66, p<0.001) but a smaller, non-significant effect for SNAP children (β = +0.42, p=0.09).

5. **Race (Black)** shows opposite correlations across groups: negative for non-SNAP (r = −0.107) but slightly positive within SNAP (r = +0.059).

---

## How to Run

Run scripts in order from the project root directory:

```bash
python code/01_clean_data.py
python code/02_extract_geography.py
python code/03_extract_cognitive_work.py
python code/04_regression_snap_vs_nonsnap.py
python code/05_full_regression_all_predictors.py
python code/06_maps_geographic_analysis.py
```

**Requirements:**
```bash
pip install pandas numpy matplotlib statsmodels geopandas
```

---

## Key Variables

| Variable | Type | Description |
|---|---|---|
| `highest_grade_category` | Outcome | Educational attainment on an ordered categorical scale; higher values = greater attainment |
| `any_snap` | Key predictor | Ever received SNAP across observed waves (binary) |
| `mother_educ_latest` | Control | Mother's highest grade completed (most recent wave) |
| `father_in_hh_any` | Control | Father ever in household (binary) |
| `ppvt_avg` | Control | Average PPVT verbal score across all tested waves |
| `math_avg` | Control | Average math achievement score across all tested waves |
| `female` / `race` | Control | Sex (binary) and race/ethnicity (Black, Hispanic, Non-Black Non-Hispanic) |
| `region` / `urban_rural` | Geographic | Census region and urban/rural classification (modal value across waves) |

---

## AI Transcripts

This project used AI coding assistants as part of the analytical workflow. Full session transcripts are available in this repository:
- [QSS20Chat1.pdf](QSS20Chat1.pdf) — Claude session: data cleaning, regression pipeline, geographic visualization
- [QSS20Chat2.pdf](QSS20Chat2.pdf) — Claude session: paper writing, LaTeX formatting, Overleaf compilation
- [ChatGPT session](https://chatgpt.com/share/6a204afa-f6f4-83ea-91c0-ffea88a83dae) — GPT-5.5 Thinking: supplementary analysis review
