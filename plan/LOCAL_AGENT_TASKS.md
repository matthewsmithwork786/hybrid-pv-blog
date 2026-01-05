# Local Agent Execution Guide

This guide provides step-by-step instructions for local agents to run and test the analysis scripts. Each task includes troubleshooting guidance.

---

## Environment Setup (MUST DO FIRST)

### Step 1: Activate Python Environment

```bash
# Windows (PowerShell)
C:\Users\matts\miniforge3\Scripts\activate.bat
mamba activate hybridpv

# Verify Python
python --version  # Should be 3.11+
```

### Step 2: Install Required Packages

```bash
# Core packages (should already be installed)
pip install pandas numpy plotly folium

# For PyPSA optimization
pip install pypsa

# For NEMOSIS data loading
pip install nemosis

# For financial calculations
pip install numpy-financial
```

### Step 3: Verify Installation

```python
# Quick test
python -c "import pandas, numpy, plotly; print('Core packages OK')"
python -c "import pypsa; print('PyPSA OK')"
python -c "import nemosis; print('NEMOSIS OK')"
```

---

## Task 1: Run Section 1 Script

**Script:** `scripts/section1/s1_solar_price_curtailment.py`

**Purpose:** Generate solar price correlation and curtailment analysis chart

### Steps

```bash
cd "C:\Users\matts\Documents\Aus research\Hybrid PV BESS vs standalone\Code\Git\Hybrid_PV_Blog"
python scripts/section1/s1_solar_price_curtailment.py
```

### Expected Output

- Console: Data loading messages, summary statistics
- File: `data/outputs/section1/solar_price_curtailment.html`

### Troubleshooting

| Issue | Solution |
|-------|----------|
| `ModuleNotFoundError: No module named 'polars'` | `pip install polars` |
| `FileNotFoundError: NEMOSIS cache` | Script uses synthetic data automatically |
| Empty chart | Check console for error messages |

### Success Criteria

- [ ] Script runs without errors
- [ ] HTML file created in output directory
- [ ] Chart shows price-solar correlation when opened in browser

---

## Task 2: Run Section 3 Scripts

### Task 2a: BESS Capacity Growth

**Script:** `scripts/section3/s3_bess_capacity_growth.py`

```bash
python scripts/section3/s3_bess_capacity_growth.py
```

**Expected Output:** `data/outputs/section3/bess_capacity_growth.html`

### Task 2b: BESS Map

**Script:** `scripts/section3/s3_bess_map_colocation.py`

```bash
python scripts/section3/s3_bess_map_colocation.py
```

**Expected Output:** `data/outputs/section3/bess_map_colocation.html`

### Troubleshooting Section 3

| Issue | Solution |
|-------|----------|
| `requests.exceptions.ConnectionError` | OpenElectricity API may be down; script has fallback data |
| Map not rendering | Check internet connection; Folium needs CDN access |

---

## Task 3: Run Section 4 Scripts

### Task 3a: Revenue Skew Analysis

**Script:** `scripts/section4/s4_revenue_skew.py`

```bash
python scripts/section4/s4_revenue_skew.py
```

**Expected Output:** `data/outputs/section4/revenue_skew.html`

**Key Finding:** Chart should show 50% of revenue concentrated in ~10% of hours

### Task 3b: MLF Map

**Script:** `scripts/section4/s4_mlf_map_nsw.py`

```bash
python scripts/section4/s4_mlf_map_nsw.py
```

**Expected Output:** `data/outputs/section4/mlf_map_nsw.html`

### Task 3c: MLF Impact Analysis

**Script:** `scripts/section4/s4_mlf_impact_revenue.py`

```bash
python scripts/section4/s4_mlf_impact_revenue.py
```

**Expected Output:** `data/outputs/section4/mlf_impact_revenue.html`

### Troubleshooting Section 4

| Issue | Solution |
|-------|----------|
| `ValueError: no numeric data` | Check data loading; use synthetic fallback |
| Folium import error | `pip install folium` |

---

## Task 4: Run Section 5 PyPSA Model

**This is the most complex task. Take it step by step.**

### Step 4.1: Test Individual Modules

```bash
# Test scenarios module
python scripts/section5/pypsa_model/scenarios.py

# Test timeseries module
python scripts/section5/pypsa_model/timeseries.py

# Test financials module
python scripts/section5/pypsa_model/financials.py
```

Each should print test output without errors.

### Step 4.2: Run Full Scenario Comparison

```bash
python scripts/section5/pypsa_model/run_scenarios.py
```

### Expected Output

- Console: Scenario comparison summary with IRR, NPV, payback for each scenario
- Files:
  - `data/outputs/section5/scenario_comparison.json`
  - `data/outputs/section5/scenario_comparison.html`

### Troubleshooting PyPSA

| Issue | Solution |
|-------|----------|
| `ModuleNotFoundError: pypsa` | `pip install pypsa` |
| `No solver available` | `conda install -c conda-forge glpk` |
| `Memory error` | Edit script to use `freq="4H"` instead of hourly |
| PyPSA optimization fails | Script falls back to revenue estimates |

### Key Results to Verify

- Standalone BESS IRR should be highest (best MLF)
- DC-coupled IRR should be lowest (no grid charging)
- AC-coupled IRR should be middle (balance of constraints)

---

## Task 5: Run Decision Tree Script

**Script:** `scripts/section5/s5_decision_tree.py`

```bash
python scripts/section5/s5_decision_tree.py
```

**Expected Output:** `data/outputs/section5/decision_tree.html`

---

## Task 6: Render Quarto Book

After all charts are generated:

```bash
quarto render
```

**Expected Output:** `docs/index.html` and all section pages

### Troubleshooting Quarto

| Issue | Solution |
|-------|----------|
| `quarto not found` | Ensure Quarto is installed and in PATH |
| Python execution errors | These are expected; we use iframe embedding |
| Missing charts | Check iframe paths in .qmd files |

---

## Task 7: Verify Full Blog

1. Open `docs/index.html` in browser
2. Navigate through all sections
3. Verify each chart loads and is interactive

### Checklist

- [ ] Index page loads
- [ ] Section 1 chart visible and interactive
- [ ] Section 3 charts (2) visible
- [ ] Section 4 charts (3) visible
- [ ] Section 5 charts (2) visible
- [ ] Navigation works between sections
- [ ] Styling looks correct (purple/yellow theme)

---

## Quick Reference: All Scripts

| Section | Script | Output |
|---------|--------|--------|
| 1 | `s1_solar_price_curtailment.py` | `solar_price_curtailment.html` |
| 3 | `s3_bess_capacity_growth.py` | `bess_capacity_growth.html` |
| 3 | `s3_bess_map_colocation.py` | `bess_map_colocation.html` |
| 4 | `s4_revenue_skew.py` | `revenue_skew.html` |
| 4 | `s4_mlf_map_nsw.py` | `mlf_map_nsw.html` |
| 4 | `s4_mlf_impact_revenue.py` | `mlf_impact_revenue.html` |
| 5 | `s5_decision_tree.py` | `decision_tree.html` |
| 5 | `pypsa_model/run_scenarios.py` | `scenario_comparison.html` |

---

## Escalation

If you encounter issues not covered here:

1. **Check the error message carefully** - Python errors usually indicate the problem
2. **Check imports** - Missing package? Install it
3. **Check paths** - Wrong directory? Use absolute paths
4. **Check data** - Scripts fall back to synthetic data if real data unavailable
5. **Read CLAUDE.md** - Contains project-specific guidance

---

## Success Summary

When complete, you should have:

- [ ] 8 HTML chart files in `data/outputs/` subdirectories
- [ ] 1 JSON results file for PyPSA scenarios
- [ ] Quarto book rendered in `docs/`
- [ ] All charts interactive when viewed in browser
