"""
utils.py
QSS 20 Final Project — Molly Ryan

Shared helper functions used across analysis scripts.
Import with: from utils import load_clean, recode_negatives, make_analysis_frame
"""

import pandas as pd
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from pathlib import Path

# ── NLS missing value codes ───────────────────────────────────────────────────

NEG_CODES = [-1, -2, -3, -4, -5, -7, -8, -9]

# ── Readable control variable labels (used in all plots and tables) ───────────

CONTROL_LABELS = {
    "female":       "Female",
    "black":        "Black",
    "hispanic":     "Hispanic",
    "birth_year":   "Birth year",
    "birth_order":  "Birth order",
    "mother_age":   "Mother's age at birth",
    "mother_educ":  "Mother's education (grades)",
    "father_in_hh": "Father in household (ever)",
    "urban":        "Urban residence",
    "northeast":    "Northeast region",
    "south":        "South region",
    "west":         "West region",
    "midwest":      "Midwest region",
    "ppvt_avg":     "Avg verbal score (PPVT)",
    "math_avg":     "Avg math score",
    "avg_work_freq":"Work frequency (lower=more)",
}

# ── Core controls used in split-sample regressions ───────────────────────────

BASE_CONTROLS = [
    "female", "black", "hispanic",
    "birth_year", "birth_order",
    "mother_age", "mother_educ", "father_in_hh",
]

FULL_CONTROLS = BASE_CONTROLS + [
    "urban", "northeast", "south", "west", "midwest",
    "ppvt_avg", "math_avg", "avg_work_freq",
]

OUTCOME = "highest_grade"


def recode_negatives(df):
    """Replace NLS negative missing codes with NaN in all numeric columns."""
    for col in df.select_dtypes("number").columns:
        df[col] = df[col].replace(NEG_CODES, np.nan)
    return df


def load_clean(path):
    """Load a processed CSV and recode negative missing values."""
    df = pd.read_csv(path, low_memory=False)
    df = recode_negatives(df)
    print(f"Loaded: {path.name}  {df.shape[0]:,} rows × {df.shape[1]} columns")
    return df


def make_analysis_frame(df):
    """
    Build the standard analysis frame used in all regression scripts.
    Creates readable column names from raw cleaned variables.
    Focuses on SNAP vs. non-SNAP comparison (TANF excluded due to small n).
    """
    reg = df.copy()

    # Outcome
    reg["highest_grade"] = pd.to_numeric(reg["highest_grade_category"], errors="coerce")

    # Key grouping variable
    reg["snap_ever"]    = pd.to_numeric(reg["any_snap"],            errors="coerce")

    # Demographics
    reg["female"]       = pd.to_numeric(reg["female"],              errors="coerce")
    reg["black"]        = (reg["race"] == "Black").astype(float)
    reg["hispanic"]     = (reg["race"] == "Hispanic").astype(float)
    reg["birth_year"]   = pd.to_numeric(reg["birth_year"],          errors="coerce")
    reg["birth_order"]  = pd.to_numeric(reg["birth_order"],         errors="coerce")

    # Family background
    reg["mother_educ"]  = pd.to_numeric(reg["mother_educ_latest"],  errors="coerce")
    reg["mother_age"]   = pd.to_numeric(reg["mother_age_at_birth"], errors="coerce")
    reg["father_in_hh"] = pd.to_numeric(reg["father_in_hh_any"],   errors="coerce")

    # Geography (added in script 02)
    if "urban_rural" in reg.columns:
        reg["urban"] = (reg["urban_rural"] == "Urban").astype(float).where(
            reg["urban_rural"].notna(), np.nan)
    if "region" in reg.columns:
        reg["northeast"] = (reg["region"] == "Northeast").astype(float).where(reg["region"].notna(), np.nan)
        reg["south"]     = (reg["region"] == "South").astype(float).where(reg["region"].notna(), np.nan)
        reg["west"]      = (reg["region"] == "West").astype(float).where(reg["region"].notna(), np.nan)
        reg["midwest"]   = (reg["region"] == "Midwest").astype(float).where(reg["region"].notna(), np.nan)

    # Cognitive scores (added in script 03)
    for col in ["ppvt_avg", "math_avg", "avg_work_freq"]:
        if col in reg.columns:
            reg[col] = pd.to_numeric(reg[col], errors="coerce")

    return reg


def print_coverage(df, cols):
    """Print non-missing count and percentage for a list of columns."""
    print("\nVariable coverage:")
    for col in cols:
        if col in df.columns:
            n = df[col].notna().sum()
            print(f"  {col:<30} {n:>6,}  ({n/len(df)*100:.1f}%)")


def save_fig(fig, path, tight=True):
    """Save a matplotlib figure and close it."""
    if tight:
        plt.tight_layout()
    fig.savefig(path, dpi=150, bbox_inches="tight")
    plt.close(fig)
    print(f"Saved: {path}")
