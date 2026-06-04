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
│   ├── 01_clean_data.py                      # Load raw NLSCYA, recode variables, build cleaned subset
│   ├── 02_extract_geography.py               # Extract Census region + urban/rural (13 waves)
│   ├── 03_extract_cognitive_work.py          # Extract PPVT, math scores, child work variables
│   ├── 04_regression_snap_vs_nonsnap.py      # Core analysis: split-sample OLS + interaction model
│   ├── 05_full_regression_all_predictors.py  # Full model with cognitive + geographic predictors
│   └── 06_maps_geographic_analysis.py        # US choropleth maps by Census region
│
├── data/
│   ├── raw/                                  # Raw NLSCYA files (NOT in git — too large)
│   └── processed/
│       ├── nlscya_qss20_cleaned_subset.csv       # Core cleaned variables (script 01 output)
│       ├── nlscya_qss20_cleaned_subset_geo.csv   # + Census region + urban/rural (script 02 output)
│       └── nlscya_qss20_cleaned_subset_full.csv  # + cognitive scores + work (script 03 output)
│
└── output/
    ├── split_sample_coef_plot.png            # Core finding: OLS coefficients by group
    ├── interaction_coef_plot.png             # Interaction model: where slopes differ significantly
    ├── correlation_ranking.png               # All predictors ranked by correlation with grades
    ├── full_regression_coef_plot.png         # Full model with cognitive + geographic variables
    ├── map_snap_rate_by_region.png           # SNAP receipt rate by Census region
    ├── map_avg_grade_by_region.png           # Average grade by region (all children)
    ├── map_snap_avg_grade.png                # Average grade — SNAP children
    ├── map_nonsnap_avg_grade.png             # Average grade — non-SNAP children
    ├── map_grade_gap_snap_vs_nonsnap.png     # Education gap between groups by region
    ├── split_sample_results.csv             # Split-sample OLS coefficients (tidy)
    ├── interaction_results.csv              # Interaction model coefficients (tidy)
    ├── full_regression_results.csv          # Full model coefficients (tidy)
    ├── correlation_ranking.csv              # Pearson correlations by group
    └── snap_nonsnap_means_table.csv         # Descriptive means: SNAP vs. non-SNAP
```

---

## How the Research Evolved

This project's analytical pipeline reflects a deliberate progression from simple to complex:

| Script | Stage | What it adds |
|--------|-------|--------------|
| `01_clean_data.py` | Data cleaning | Core outcome (highest grade), SNAP grouping variable, family background |
| `02_extract_geography.py` | Data enrichment | Census region and urban/rural — enables geographic analysis |
| `03_extract_cognitive_work.py` | Data enrichment | Cognitive test scores (PPVT, math) and child work variables |
| `04_regression_snap_vs_nonsnap.py` | Core analysis | Split-sample OLS and interaction model — directly tests the research question |
| `05_full_regression_all_predictors.py` | Extended analysis | Adds cognitive + geographic predictors; ranks all variables by correlation |
| `06_maps_geographic_analysis.py` | Visualization | Regional variation in SNAP rates and the education gap |

---

## Methods

1. **Data cleaning** — Recoded NLS negative missing codes (−1 through −9) as NaN. Constructed binary welfare indicators, education outcome variables, and family structure measures.

2. **Geographic extraction** — Identified Census region and urban/rural variable IDs across 13 waves using the NLS codebook. Assigned each child their modal (most common) value across waves.

3. **Cognitive extraction** — Averaged PPVT verbal and math achievement scores across up to 15 waves (1986–2014). Also extracted each child's earliest available score as a childhood baseline.

4. **Split-sample OLS** — Divided sample into SNAP (n≈2,754) and non-SNAP (n≈5,529) groups. Ran the same OLS specification on each group with HC3 robust standard errors. Compared coefficients side by side.

5. **Interaction model** — Ran one OLS model with `snap_ever × each control` interaction terms to formally test where slopes differ significantly between groups.

6. **Correlation ranking** — Computed Pearson correlations between each predictor and highest grade, separately by SNAP status, to identify which variables show the largest group differences.

7. **Geographic maps** — Downloaded U.S. Census TIGER shapefile, dissolved states into Census regions using geopandas, and plotted choropleth maps with region outlines only.

---

## Key Findings

1. **Mother's education** is the strongest predictor overall (r = +0.317), but weaker for SNAP children (r = +0.278) than non-SNAP children (r = +0.326).

2. **Math scores** are nearly as predictive as mother's education (r = +0.303) and are actually stronger within the SNAP group (β = +0.10) than non-SNAP (β = +0.06).

3. **Being female** predicts higher grade completion in both groups, with a larger gap for SNAP children (+0.94 grades) than non-SNAP (+0.83 grades).

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
| `highest_grade_category` | Outcome | Highest grade completed (0–20); 12=HS, 16=BA |
| `any_snap` | Key predictor | Ever received SNAP across observed waves (binary) |
| `mother_educ_latest` | Control | Mother's highest grade (most recent wave) |
| `father_in_hh_any` | Control | Father ever in household (binary) |
| `ppvt_avg` | Control | Average PPVT verbal score across all tested waves |
| `math_avg` | Control | Average math score across all tested waves |
| `female` / `race` | Control | Sex (binary) and race/ethnicity |
| `region` / `urban_rural` | Geographic | Census region and urban/rural (modal across waves) |
