# QSS 20 Final Project

## Project Overview

This project explores the relationship between SNAP/Food Stamp and AFDC/TANF receipt and educational outcomes using data from the NLSY79 Children and Young Adults survey.

The main question is:

> How does welfare program participation relate to high school completion and college attainment?

---

## Repository Structure

### `code/`

Contains the main notebooks used for the project:

- `01_pull_data.ipynb`  - Loads and inspects the dataset

- `02_clean_construct.ipynb`  -  Cleans variables and creates welfare exposure groups

- `03_analyze_visualize.ipynb`  -  Produces summary statistics and visualizations

---

### `output/`

Contains generated figures and tables from the analysis:

- education distribution plots
- high school completion comparisons
- summary tables

---

## Data

The original NLSY79-CYA dataset is too large for GitHub, so this repository includes smaller cleaned/subset files used for analysis:

- `data/nlscya_subset.csv`
- `data/nlscya_cleaned.csv`

Original data source:

- NLSY79 Children and Young Adults  
  https://www.nlsinfo.org/content/cohorts/nlsy79-children

---

## Current Progress

So far, the project:

- loaded and cleaned the data
- created SNAP/TANF exposure groups
- compared educational outcomes across groups
- generated initial figures and tables

---

## Requirements

Python packages used:

```bash
pip install pandas numpy matplotlib
