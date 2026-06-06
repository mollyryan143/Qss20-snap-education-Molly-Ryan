# Final Paper Outline — 10 pages

**Working title:** *SNAP and AFDC/TANF Receipt and Long-Term Educational Outcomes: A Descriptive Analysis Using the NLSY79 Children and Young Adults Survey*

**Author:** Molly Ryan
**Course:** QSS 20, Spring 2026
**Project type:** Descriptive comparison (per rubric)
**Template:** Cook County bail paper (Fink, Jin, Punaini, Tolat — `felonysentencing_example_descriptivecomparison.pdf`)

---

## Page budget

| Section | Pages | Rubric points |
|---|---|---|
| Abstract | 0.3 | — |
| 1. Introduction | 1.0 | 5 (shared) |
| 2. Related Work | 1.5 | 5 (shared) |
| 3. Data | 1.5 | 10 |
| 4. Methods | 2.0 | 20 |
| 5. Results | 2.7 | 10 + 10 |
| 6. Discussion / Limitations / Conclusion | 1.0 | 2 |
| Works Cited | (does not count toward 10) | — |

---

## Abstract (0.3 page)

**What to write:** 4–6 sentences describing the question, data, method, headline finding.

**Template you can fill in:**
> This paper examines the descriptive association between SNAP/Food Stamp receipt, AFDC/TANF receipt, and long-term educational attainment among children of NLSY79 mothers. Using the public-use NLSY79 Children and Young Adults file (N = 11,545 children of NLSY79 women, covering 1979–2018), I construct four exposure groups (Neither, SNAP only, TANF only, Both) based on welfare receipt 1994–2006 and compare HS/GED completion rates and the distribution of educational attainment across groups. I find a monotonic gradient: respondents with no welfare exposure have a 92% HS/GED completion rate, falling to 85% in the SNAP-only group and 82% in the Both group. The differences are descriptive and confounded by household income, parental education, and other factors not adjusted for in this analysis.

**Source material:** Milestone 1 abstract-style framing, Milestone 2 headline numbers.

---

## 1. Introduction (1.0 page)

**Goal:** Motivate why welfare policy matters, narrow to SNAP and TANF specifically, and state the research question.

**Suggested paragraph structure:**

1. **Opening hook on welfare policy's stakes** — Pull from your Me Search opening. SNAP losing $187B in funding over the next decade [cite DeSilver 2025]; food-stamp reliance jumped during COVID and remains elevated [Pew analysis figure from Me Search]; cuts could create financial hardship for children and families [cite Kosec & Mo 2026].
2. **Why SNAP and TANF together** — These are the two largest U.S. cash and in-kind welfare programs for families with children. They operate via different mechanisms (food security vs. cash assistance) which the literature suggests may have different effects on child wellbeing. SNAP reduces food insecurity and improves birth outcomes [cite Gundersen]; AFDC/TANF affects work incentives and household stability [cite Hanson & Andrew 2009; Aizer et al. 2022].
3. **Why education as the outcome** — Education attainment is one of the clearest indicators of long-run economic mobility. If welfare programs improve children's prospects, education is where we should see it [cite Pilkauskas 2023; Heflin et al. 2022].
4. **The gap and the research question** — Most published literature studies one program at a time. This paper compares four groups directly — Neither, SNAP only, TANF only, Both — to ask: *Are educational outcomes systematically different across these four welfare-exposure groups among children of NLSY79 mothers?* I do not estimate a causal effect; I describe associations.
5. **Roadmap sentence** — "Section 2 reviews the related literature. Section 3 describes the data. Section 4 explains how I constructed the exposure groups and outcome measures. Section 5 presents the descriptive comparison. Section 6 discusses limitations and directions for future work."

**Source material:**
- Me Search ¶1 (your personal motivation, the SNAP-cut figure)
- Lit Review §3 ¶1 (literature framing)
- Milestone 1 §2 (research question wording)

---

## 2. Related Work (1.5 pages)

**Goal:** Show you've read the field; place your project within it; identify the gap you fill.

**Suggested structure (use the Lit Review you already wrote):**

1. **Welfare programs as anti-poverty infrastructure** (~5 sentences)
   - Banerjee et al. 2024 — social protection covers ~2.5 billion globally
   - Esser et al. 2009 — cross-national variation in welfare design

2. **U.S.-specific evidence on SNAP and child outcomes** (~6 sentences)
   - Gundersen — SNAP, WIC, NSLP, SBP are the four largest U.S. food programs (~$100B combined budget); SNAP alone reaches 47M+ people
   - Pilkauskas 2023 — food security and early childhood stability link to better educational outcomes
   - Heflin et al. 2022 — childhood SNAP and TANF participation tracked longitudinally via administrative data

3. **AFDC/TANF and work incentives** (~5 sentences)
   - Hanson & Andrew 2009 — state-level variation in TANF earnings deductions; California is unusually generous (50% earnings deduction, $225 fixed monthly deduction)
   - Aizer et al. 2022 — central debate is benefits-for-children vs. work-disincentives-for-adults
   - Han — state variation in labor incentives and work requirements

4. **Comparing SNAP and TANF together** (~3 sentences) — the gap
   - "Most prior work studies SNAP or TANF in isolation. The four-group comparison (Neither / SNAP only / TANF only / Both) is uncommon in the literature, though it is the natural way to compare the two programs' associations with the same outcome in the same sample."

5. **Self-critique pulled forward from the felony example** (~3 sentences)
   - Following Fink et al. (2021), I am careful to frame findings descriptively. Associations between welfare receipt and education can reflect program effects, selection into program participation, or third-factor confounders (parental education, income, neighborhood). Disentangling these requires controls and ideally exogenous variation, which is beyond this paper's scope.

**Source material:** Lit Review §1 (source list) and §3 (synthesis). You already have 8–11 sources written up. **Reuse the citation list verbatim** — it satisfies the "at least half peer-reviewed" criterion you flagged in the Lit Review.

---

## 3. Data (1.5 pages)

**Goal:** Hit every rubric data sub-element: (1) source, (2) time window, (3) original unit of analysis, (4) unit of analysis used, (5) limitations, (6) missingness.

**Suggested structure:**

### 3.1 Source

> Data come from the **National Longitudinal Survey of Youth 1979 — Children and Young Adults** (NLSY79-CYA), a public-use longitudinal survey administered by the U.S. Bureau of Labor Statistics through the Center for Human Resource Research at Ohio State University. The full extract used here covers waves from 1979 to 2018 and was downloaded from the NLS Investigator portal (https://www.nlsinfo.org/investigator). NLSY79-CYA follows the **biological children of the women in the original NLSY79 cohort** from birth into adulthood, capturing cognitive assessments, schooling, family structure, and (once respondents turn 15+) the Young Adult Survey on their own welfare receipt, education, and labor-force outcomes.

### 3.2 Time window

> The raw extract spans 1979–2018. For SNAP/Food Stamp exposure I use the seven biennial waves from 1994 to 2006. For AFDC/TANF exposure I use the three waves the relevant question was asked: 1994, 1996, and 1998 (AFDC was replaced by TANF in 1997 under PRWORA, and the welfare-receipt question wording on the NLSY79-CYA changed after 1998).

### 3.3 Unit of analysis

- **Original:** child × wave (long format); after appending the Young Adult Survey, also young-adult-respondent × wave.
- **In this paper:** one row per **child** of an NLSY79 mother (cross-sectional). Welfare exposure and education are summarized across all waves to a single row per child.

### 3.4 Table 1: data summary (modeled on Table 1 of the bail example)

```
+---------------------+-----------+-----------+-------------------+------------------------+
| Data source         | N rows    | Years     | Unit of analysis  | Key variables          |
+---------------------+-----------+-----------+-------------------+------------------------+
| nlscya_all_         | 11,545    | 1979–2018 | Child of NLSY79   | AFDC_1994, AFDC_1996,  |
| 1979-2018.csv       | children  |           | mother (cross-    | AFDC_1998, FOODSTAMPS_ |
| (full extract)      | (82,318   |           | sectional after   | 1994 through _2016,    |
|                     | vars)     |           | constructing      | HSDIPLOMA_EVER,        |
|                     |           |           | exposure summary) | GED_EVER, PROFDEGREE_  |
|                     |           |           |                   | EVER, CRACE, CSEX,     |
|                     |           |           |                   | CPUBID, MPUBID         |
+---------------------+-----------+-----------+-------------------+------------------------+
| nlscya_subset.csv   | 11,545    | same      | same              | 22-variable subset     |
| (used in analysis)  | children, |           |                   | tracked in the GitHub  |
|                     | 22 vars   |           |                   | repository             |
+---------------------+-----------+-----------+-------------------+------------------------+
```

### 3.5 Limitations of the data source

Four bullets (mirroring the Milestone 2 README):

- **Respondent-level reporting.** The AFDC and food-stamp variables in NLSY79-CYA ask the young-adult respondent about *their own and their spouse/partner's* welfare receipt, not their mother's receipt during their childhood. The interpretation is therefore "young adults who themselves received welfare as they entered adulthood" rather than "children of welfare-receiving mothers." Future work would link the mother's NLSY79 main-file welfare history to extend the analysis.
- **Window mismatch between programs.** SNAP receipt is captured 1994–2006 (and through 2016); AFDC/TANF is captured 1994–1998 only. The two indicators therefore reflect partly different exposure windows.
- **Sample restriction by age.** Of 11,545 NLS-CYA children, only ~2,275 have non-missing values for both the SNAP and TANF exposure indicators. Most missingness is structural: the child was younger than 15 in the relevant waves and so not eligible for the Young Adult Survey.
- **No information on benefit dollar amounts or duration.** The exposure indicators are binary (ever received yes/no) rather than measuring intensity, duration, or generosity of benefits.

### 3.6 Missingness in key fields

Make a small table or paragraph noting:
- AFDC_1998: 9,406 of 11,545 (81%) are missing (-7 = not asked in this round)
- FOODSTAMPS_2006: 7,017 of 11,545 (61%) are missing
- HSDIPLOMA_EVER: 2,921 of 11,545 (25%) are missing
- Effective analysis sample after restricting to both exposure and education non-missing: **2,275 children**

**Source material:** Milestone 2 README §"Known limitations"; the variable-mapping notebook output.

---

## 4. Methods (2.0 pages — the heaviest section)

**Goal:** Hit every methods sub-element: (1) cleaning steps, (2) merges, (3) variable definitions, (4) since this is descriptive not predictive, no train-test split needed but state the test logic, (5) link to code lines.

**Suggested structure:**

### 4.1 Variable extraction from the raw NLS file

> The raw NLS Investigator extract (`nlscya_all_1979-2018.csv`, 2.8 GB, 82,318 variables × 11,545 children) is too large to load into memory directly. I extracted 22 target columns via a streaming Python CSV reader, mapping the cryptic NLS column codes (e.g., `Y0314700`) to human-readable names (`AFDC_1994`) using the variable-name mapping parsed from the auto-generated R loader script that ships with the NLS extract. See `code/01_pull_data.ipynb` for the extraction and `output/nlscya_variable_mapping.csv` for the full 82,318-row code→name mapping.

### 4.2 Recoding NLS missing codes

> NLSY79-CYA uses negative integers as missing-data flags: -1 (refused), -2 (don't know), -3 (invalid skip), -4 (valid skip), -5 (non-interview), -7 (missing/not asked in this round). I recode all six to `NaN` for every analytic variable. Identifier columns (`CPUBID`, `MPUBID`) are left untouched. See `code/02_clean_construct.ipynb` lines [X]–[Y].

### 4.3 Constructing welfare-exposure indicators (Unit 4: user-defined functions)

Two binary indicators, then a four-level group variable:

- `snap_ever = 1` if `max(FOODSTAMPS_1994, FOODSTAMPS_1996, ..., FOODSTAMPS_2006) == 1`; `0` if all observed values are 0; `NaN` if all are missing.
- `tanf_ever = 1` if `max(AFDC_1994, AFDC_1996, AFDC_1998) == 1`; `0` if all observed values are 0; `NaN` if all are missing.
- `program_group` (categorical) via a user-defined function `assign_group(row)` that maps the (`snap_ever`, `tanf_ever`) pair to one of `Neither`, `SNAP only`, `TANF only`, `Both SNAP and TANF`; returns `NaN` if either input is missing.

**Include the function code as a snippet** — the rubric explicitly allows "code snippet in the paper appendix or link to the relevant script or notebook and note the line numbers."

```python
def assign_group(row):
    s, t = row['snap_ever'], row['tanf_ever']
    if pd.isna(s) or pd.isna(t):
        return np.nan
    if s == 1 and t == 1: return 'Both SNAP and TANF'
    if s == 1 and t == 0: return 'SNAP only'
    if s == 0 and t == 1: return 'TANF only'
    return 'Neither'
```

### 4.4 Constructing the education outcome (3-level ordinal)

NLSY79-CYA provides three cross-round (XRND) education-attainment summary indicators per respondent: `HSDIPLOMA_EVER`, `GED_EVER`, `PROFDEGREE_EVER`. I collapse these into one ordinal `edu_level`:

- 0 = No HS diploma and no GED
- 1 = HS diploma or GED, no professional/college degree
- 2 = Has a professional/college degree

A respondent is dropped from the education analysis if both `HSDIPLOMA_EVER` and `GED_EVER` are missing (typically because the child was too young to have completed schooling by the most recent wave).

### 4.5 Analytic sample

> The final analytic sample is the **intersection** of children with non-missing `program_group` and non-missing `edu_level`: **N = 2,275 children**.

### 4.6 Descriptive comparison design

> I report (i) the cross-tab of `program_group` × `edu_label` normalized to row percentages (Figure 1), and (ii) the share of each program-exposure group that holds an HS diploma or GED, with 95% binomial confidence intervals (Figure 2; Table 1). Because the four groups have very different sample sizes — and `TANF only` in particular has only N = 7 — the figures show the underlying sample size in each bar and the confidence intervals make uncertainty explicit.

### 4.7 What I do **not** do (transparency about scope)

> This is a descriptive comparison, not a causal estimate. I do not regression-adjust for parental education, household income, family structure, or race/ethnicity; I do not match on observables; I do not exploit any source of exogenous variation (e.g., state-level TANF rule changes following 1996 PRWORA). These extensions are the natural next step for Milestone 3 / final-paper expansion.

**Optional:** Include a small flowchart showing: raw 2.8GB CSV → 22-column subset → recoded → exposure groups + outcome → analytic sample of 2,275 → Figures 1–2. The rubric says "consider using a flowchart" for sequential methods.

**Source material:**
- Milestone 2 code (lines from `02_clean_construct.ipynb`, `03_analyze_visualize.ipynb`) — paste them
- Milestone 2 README, "Key variables" section

---

## 5. Results (2.7 pages — split evenly across 5.1 and 5.2)

**Goal:** Hit "summarize key patterns + at least one descriptive figure/table with informative caption."

### 5.1 Sample description (Table 1, ~0.4 page)

| Group | N | % of analytic sample | % Female (CSEX=2) | % Black (CRACE=2) |
|---|---|---|---|---|
| Neither | 1,567 | 68.9% | (compute) | (compute) |
| SNAP only | 574 | 25.2% | (compute) | (compute) |
| TANF only | 7 | 0.3% | (compute) | (compute) |
| Both SNAP and TANF | 127 | 5.6% | (compute) | (compute) |
| **Total** | **2,275** | 100% | (compute) | (compute) |

Caption: "Table 1. Composition of the analytic sample by SNAP/TANF exposure group. Each row reports the number of children of NLSY79 mothers assigned to a group based on whether they ever reported AFDC or food-stamp receipt in the relevant waves (1994–1998 for AFDC, 1994–2006 for food stamps). The TANF-only cell is sparsely populated (N=7) and should be interpreted with caution."

**This table costs you ~30 minutes** — just add the gender/race breakdowns to the existing `summary` table in `03_analyze_visualize.ipynb`.

### 5.2 Headline finding: HS completion gradient (Figure 2 + writeup, ~1.2 pages)

**Insert `output/fig2_hs_completion_by_group.png` here.** Caption:

> Figure 2. Share of NLSY79-CYA respondents with a high-school diploma or GED, by SNAP/TANF exposure group. Error bars are 95% binomial confidence intervals. The "TANF only" cell (N=7) has an uninformatively wide confidence interval and should not drive interpretation. Among the three well-powered groups, there is a monotonic gradient: 92.1% completion in Neither, 85.4% in SNAP only, and 81.9% in Both.

**Writeup paragraphs to expand:**

1. Quote the four rates and CIs from Table 1 (the 92.1 / 85.4 / 85.7 / 81.9 figures from Milestone 2).
2. State the magnitude: respondents in the "Both" group are about 10 percentage points less likely to hold an HS/GED than respondents in the "Neither" group.
3. Caveat the TANF-only cell explicitly: with N=7, the 95% CI is ±26 percentage points, so even if the point estimate is informative, it cannot be statistically distinguished from any of the other groups.
4. State what the gradient does and does **not** support: it is consistent with a story in which welfare-receiving families have systematically different educational trajectories than non-receiving families; it does **not** establish that welfare receipt *causes* lower educational attainment. Pull the felony-paper framing: "these differences could be attributed to … background differences … for which we are unable to account."

### 5.3 Education distribution by group (Figure 1 + writeup, ~1.0 page)

**Insert `output/fig1_education_distribution.png` here.** Caption:

> Figure 1. Percent distribution of educational attainment within each SNAP/TANF exposure group. Bars sum to 100% within each group. "Professional degree" is a thin slice (1–3%) across all groups because of the NLSY79-CYA age structure — many respondents in the analytic sample had not had time to complete a college degree by the most recent wave at which they were observed. Differences between groups are concentrated in the No HS / GED versus HS or GED categories.

**Writeup paragraphs to expand:**

1. Walk through the stacked bars: the share with No HS / GED rises from ~8% (Neither) to ~14% (SNAP only) to ~18% (Both).
2. Note that the gradient on the HS-or-better margin is consistent across both program groups but the *Both* group is meaningfully worse than the *SNAP-only* group, suggesting receipt of both programs (not just one) is the marker of difference.
3. Briefly engage with the literature: this is consistent with Pilkauskas (2023) and Heflin et al. (2022), who find that long-term welfare participation predicts lower educational attainment, while also being consistent with Aizer et al. (2022)'s emphasis on confounding by household resources.

### 5.4 (Optional) Subgroup robustness check

If you have time: rerun Figures 1–2 separately for `CSEX == 1` vs `CSEX == 2` (or by race), and report whether the gradient looks similar. This is exactly the kind of supplementary analysis the felony paper did with their offense subsets. Even a one-paragraph "the pattern is qualitatively similar across boys and girls" earns points.

---

## 6. Discussion (1.0 page)

**Goal:** Synopsis + limitations + future directions. The rubric only weights this section at 2 points, so be efficient.

**Suggested four paragraphs:**

1. **Recap headline.** "Across 2,275 children of NLSY79 mothers, I find a 10-percentage-point gradient in HS/GED completion between respondents who never reported AFDC or food-stamp receipt and respondents who reported both. The gradient is monotonic across well-powered groups…"

2. **What this is and isn't.** Repeat the descriptive-not-causal point. Specifically name three confounders: parental education, household income, family structure. Note that selection-into-program-participation likely accounts for some-unknown share of the observed gradient.

3. **Data limitations specific to this study.** AFDC question only asked 1994–1998 (so the TANF-only group is structurally underpowered). Respondent-level reporting (not maternal). Only 2,275 of 11,545 children have usable data on both exposure and education.

4. **Future directions.** (i) Link the mother's NLSY79 main-file welfare history. (ii) Add controls and run logistic regression of `has_hs` on `program_group` + controls — the natural Unit-11 / supervised-ML extension. (iii) Exploit the 1996 PRWORA welfare reform as a source of state-level variation in TANF rules (a la Hanson & Andrew 2009) to move from descriptive to quasi-experimental.

---

## Works Cited

Pull the citation list directly from your Lit Review (you already have ≥8 peer-reviewed sources). Add:
- The bail-decision example (Fink et al. 2021) only if you cite it in the related-work self-critique
- DeSilver 2025 and Kosec & Mo 2026 from your Me Search

---

## What you can copy-paste from existing assignments

| Existing assignment | Section it feeds | Quantity to reuse |
|---|---|---|
| Me Search §1 (welfare matters) | Intro ¶1 | Most of it, lightly edited |
| Me Search Figure 1 (food stamp use) | Optional intro figure | Drop in directly |
| Lit Review §1 (source list) | Works Cited | Full list |
| Lit Review §3 (synthesis) | Related Work §2 | Most of it, restructured |
| Milestone 1 (welfare version) §2 | Intro ¶4 (research question) | Question wording verbatim |
| Milestone 1 §3 | Data §3.1, §3.2 | Most of it, updated for NLSY-CYA specifics |
| Milestone 1 §6 (anticipated challenges) | Discussion §3 (limitations) | Most of it, updated |
| Milestone 2 README "Known limitations" | Data §3.5 | Word-for-word |
| Milestone 2 README "Key variables" | Methods §4.3, §4.4 | Word-for-word |
| Milestone 2 README "Headline result" table | Results Table 1 | Drop in directly |
| `code/02_clean_construct.ipynb` `assign_group` function | Methods §4.3 | Drop in directly |
| `output/fig1_education_distribution.png` | Results §5.3 | Drop in directly |
| `output/fig2_hs_completion_by_group.png` | Results §5.2 | Drop in directly |

You're roughly **40% done with the writing already** if you reuse aggressively.

---

## Suggested writing order (if working backward from a deadline)

1. **Data section first** — it's mostly a paste-up from Milestone 2 README and Milestone 1.
2. **Methods next** — paste your `assign_group` function and the variable definitions; write the surrounding prose.
3. **Results** — drop in the two figures + Table 1; write the captions and 2–3 paragraphs of interpretation per figure.
4. **Related Work** — restructure your Lit Review.
5. **Introduction** — pull from Me Search ¶1, add a roadmap sentence at the end.
6. **Abstract** — write last, after everything else is settled.
7. **Discussion** — write last, after Results.

Estimated total writing time if you reuse everything available: **6–8 focused hours**.
