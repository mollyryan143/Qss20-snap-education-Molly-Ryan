# SNAP/TANF Receipt and Educational Attainment
## QSS 20 Final Project — Molly Ryan, Spring 2026

---

## Research Question

Does childhood SNAP (Food Stamp) receipt predict lower educational attainment, and do the factors that typically protect educational outcomes — mother's education, father's presence, cognitive ability — operate differently for children in SNAP households versus those who never received SNAP?

---

## Data Source

**NLSY79 Children and Young Adults (NLSCYA), 1979–2018**
- Unit of analysis: child respondents linked to NLSY79 mothers
- N = 11,545 children across biennial survey waves (1994–2018)
- Downloaded from the NLS Investigator: https://www.nlsinfo.org/investigator/pages/search
- Raw data file (~2.8 GB) is stored locally and **not tracked in this repository**
- Cleaned processed subsets are included in `data/processed/`

---

## Repository Structure

```
├── code/
│   ├── 01_clean_data.py                   # Load raw NLSCYA, recode variables, save cleaned subset
│   ├── 02_extract_geography.py            # Extract Census region + urban/rural from raw data
│   ├── 03_extract_cognitive_work.py       # Extract PPVT, math scores, child work variables
│   ├── 04_regression_analysis.py          # Split-sample OLS + interaction models (SNAP vs non-SNAP)
│   ├── 05_full_regression_correlations.py # Full model with all variables, correlation ranking
│   └── 06_maps.py                         # US choropleth maps by Census region
│
├── data/
│   ├── raw/                               # Raw NLSCYA files (NOT tracked in git — too large)
│   └── processed/
│       ├── nlscya_qss20_cleaned_subset.csv      # Core cleaned variables (script 01 output)
│       ├── nlscya_qss20_cleaned_subset_geo.csv  # + geography (script 02 output)
│       └── nlscya_qss20_cleaned_subset_full.csv # + cognitive + work (script 03 output)
│
└── output/
    ├── correlation_ranking.png            # Pearson r with highest grade — all variables
    ├── split_sample_coef_plot.png         # OLS coefficients: SNAP vs non-SNAP side by side
    ├── interaction_coef_plot.png          # Interaction model: which slopes differ by SNAP status
    ├── full_regression_coef_plot.png      # Full model with cognitive + work variables
    ├── map_snap_rate_by_region.png        # SNAP receipt rate by Census region
    ├── map_grade_gap_snap_vs_nonsnap.png  # Education gap between groups by region
    ├── correlation_ranking.csv            # Tidy correlation table
    ├── split_sample_results.csv           # Split-sample OLS coefficients
    ├── full_regression_results.csv        # Full model OLS coefficients
    └── snap_nonsnap_means_table.csv       # Descriptive means by SNAP status
```

---

## How to Run

Scripts must be run in order from the project root directory:

```bash
python code/01_clean_data.py
python code/02_extract_geography.py
python code/03_extract_cognitive_work.py
python code/04_regression_analysis.py
python code/05_full_regression_correlations.py
python code/06_maps.py
```

**Requirements:** Python 3.9+

```bash
pip install pandas numpy matplotlib statsmodels geopandas plotly kaleido
