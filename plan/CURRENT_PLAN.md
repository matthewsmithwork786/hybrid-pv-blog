# Project Plan: Beyond the Solar Curve

**Last Updated:** 2026-01-05
**Status:** Active Development

> **For AI Agents:** This is the authoritative project plan. Also read `/CLAUDE.md` for technical development context.

---

## Executive Summary

This project is a Quarto-based research report analyzing battery energy storage system (BESS) investment decisions in Australia's National Electricity Market (NEM). The core question: **Does co-locating battery storage with solar PV create value, or does it destroy returns compared to standalone BESS deployment?**

### Current State Overview

| Component | Status | Notes |
|-----------|--------|-------|
| **Content (Sections 1-5)** | Complete | All five narrative sections written |
| **Chart Scripts** | Mostly Complete | 16 Python scripts exist |
| **Chart Outputs (HTML)** | Minimal | Only 1 HTML chart generated |
| **PyPSA Model** | Infrastructure Ready | Code exists, needs testing/outputs |
| **Quarto Rendering** | Functional | Using iframe embedding pattern |

**Primary Gap:** Scripts exist but chart outputs have not been generated. The report structure is complete but visualizations need to be rendered.

---

## Project Structure

```
hybrid-pv-blog/
├── _quarto.yml              # Quarto book configuration
├── index.qmd                # Landing page with key findings
├── CLAUDE.md                # Development instructions (READ THIS)
├── requirements.txt         # Python dependencies
│
├── sections/                # Report content (ALL COMPLETE)
│   ├── 01_investment_problem.qmd
│   ├── 02_bess_integration.qmd
│   ├── 03_tradeoff_analysis.qmd
│   ├── 04_technical_constraints.qmd
│   └── 05_strategic_framework.qmd
│
├── scripts/                 # Analysis scripts
│   ├── utils/               # Shared utilities
│   │   ├── style_config.py  # Plotly template, colors
│   │   ├── data_paths.py    # Path constants
│   │   └── nemosis_helpers.py
│   ├── section1/            # 1 script
│   ├── section3/            # 4 scripts
│   ├── section4/            # 3 scripts
│   ├── section5/            # Decision tree + PyPSA model
│   └── download/            # NEMOSIS data download scripts
│
├── data/
│   └── outputs/             # Generated chart HTML/JSON
│       ├── section1/        # Empty - needs generation
│       ├── section3/        # Has BESS diagrams only
│       ├── section4/        # Empty - needs generation
│       └── section5/        # Empty - needs generation
│
├── assets/
│   └── styles/
│       └── custom.css       # Custom Quarto styling
│
├── skills/                  # Reference documentation
│   ├── NEMOSIS_skill.md
│   └── PyPSA_skill.md
│
├── plan/                    # Project planning
│   ├── CURRENT_PLAN.md      # THIS FILE
│   └── archived/            # Old plans (skip these)
│
└── docs/                    # Rendered Quarto output
```

---

## Implementation Status by Section

### Section 1: The Investment Problem

**Content:** Complete - Covers solar price collapse and curtailment crisis

| Script | Output | Status |
|--------|--------|--------|
| `s1_solar_price_curtailment.py` | `solar_price_curtailment.html` | Script exists, output not generated |

**Chart Requirements:**
- Dual-axis column chart: Solar-hour prices (2018-2025) + curtailment percentage
- Data: NSW wholesale prices 10:00-16:00, annual averages
- Colors: Yellow bars (price), red line (curtailment)

---

### Section 2: The BESS Integration Thesis

**Content:** Complete - Narrative section explaining how BESS restores value

**No charts required** - This is a conceptual bridge section.

---

### Section 3: Trade-Off Analysis

**Content:** Complete - Compares standalone vs co-located deployment

| Script | Output | Status |
|--------|--------|--------|
| `s3_bess_capacity_growth.py` | `bess_capacity_growth.html` | Script exists, output not generated |
| `s3_bess_map_colocation.py` | `bess_map_colocation.html` | Script exists, output not generated |
| `s3_battery_revenue_buckets.py` | `battery_revenue_buckets.html` | Script exists, output not generated |
| `s3_colocation_diagram.py` | `bess_diagram_*.svg/html` | **COMPLETE** - Multiple diagram formats exist |
| `s3_bess_diagram_options.py` | (alternative diagram script) | Backup option |

**Chart Requirements:**
1. **Capacity Growth:** Stacked column chart of NEM BESS MWh by year (2018-2028)
2. **Co-location Map:** Interactive Folium map showing standalone (purple) vs co-located (orange) batteries
3. **Revenue Buckets:** Horizontal bar chart of battery revenue by price bucket
4. **Configuration Diagram:** Technical schematic of AC-coupled, DC-coupled, non-hybrid (DONE)

---

### Section 4: Technical Constraints

**Content:** Complete - Covers revenue concentration, MLFs, grid constraints

| Script | Output | Status |
|--------|--------|--------|
| `s4_revenue_skew.py` | `revenue_skew.html` | Script exists, output not generated |
| `s4_mlf_map_nsw.py` | `mlf_map_nsw.html` | Script exists, output not generated |
| `s4_mlf_impact_revenue.py` | `mlf_impact_revenue.html` | Script exists, may have issues |

**Chart Requirements:**
1. **Revenue Skew:** Cumulative distribution showing 50% of revenue in ~10% of hours
2. **MLF Map:** Choropleth map of NSW generator MLFs
3. **MLF Impact:** Bar chart showing revenue impact by MLF band

---

### Section 5: Strategic Framework

**Content:** Complete - Five-step decision framework with detailed guidance

| Script | Output | Status |
|--------|--------|--------|
| `s5_decision_tree.py` | `decision_tree.html` | Script exists, output not generated |
| `pypsa_model/run_scenarios.py` | `scenario_comparison.html` | Full PyPSA model infrastructure exists |

**PyPSA Model Components:**
- `pypsa_model/__init__.py` - Package init
- `pypsa_model/network.py` - Network setup
- `pypsa_model/scenarios.py` - Scenario definitions (standalone, AC-coupled, DC-coupled)
- `pypsa_model/timeseries.py` - Time series data loading
- `pypsa_model/financials.py` - IRR, NPV calculations
- `pypsa_model/run_scenarios.py` - Main execution script

**Chart Requirements:**
1. **Decision Tree:** Interactive flowchart for standalone vs co-located decision
2. **Scenario Comparison:** Bar chart comparing IRR across scenarios
3. **Dispatch Profile:** Sample week showing charging/discharging patterns (optional)

---

## Priority Task List

### Priority 1: Generate Core Chart Outputs

These scripts should be run to generate the HTML chart outputs:

```bash
# Section 4 (documented as previously working)
python scripts/section4/s4_revenue_skew.py
python scripts/section4/s4_mlf_map_nsw.py

# Section 1
python scripts/section1/s1_solar_price_curtailment.py

# Section 3
python scripts/section3/s3_bess_capacity_growth.py
python scripts/section3/s3_bess_map_colocation.py
python scripts/section3/s3_battery_revenue_buckets.py
```

### Priority 2: Test and Fix Any Broken Scripts

If scripts fail, check:
1. **Import errors:** Install missing packages (`pip install <package>`)
2. **Path errors:** Update `data_paths.py` for current environment
3. **Data errors:** Scripts should fall back to synthetic data if real data unavailable

### Priority 3: Run PyPSA Model

```bash
# Test individual modules first
python scripts/section5/pypsa_model/scenarios.py
python scripts/section5/pypsa_model/timeseries.py
python scripts/section5/pypsa_model/financials.py

# Run full scenario comparison
python scripts/section5/pypsa_model/run_scenarios.py
```

### Priority 4: Generate Decision Tree

```bash
python scripts/section5/s5_decision_tree.py
```

### Priority 5: Render Quarto Book

```bash
quarto render
# Output: docs/index.html
```

---

## Technical Context

### Python Environment

- **Environment Name:** `hybridpv` (mamba/conda)
- **Python Version:** 3.11+
- **Key Packages:** pandas, numpy, plotly, folium, pypsa, nemosis

### Quarto Configuration

- **Python execution:** DISABLED (`execute.enabled: false`)
- **Chart integration:** HTML iframe embedding
- **Output directory:** `docs/`

### Chart Embedding Pattern

Charts are embedded in QMD files using iframes:

```html
<iframe src="../data/outputs/section4/revenue_skew.html"
        width="100%"
        height="500"
        style="border: none;">
</iframe>
```

### Color Palette (from style_config.py)

| Purpose | Hex Code |
|---------|----------|
| Solar PV | `#FFD700` |
| Wind | `#2E7D32` |
| Battery (Standalone) | `#7B1FA2` |
| Battery (Co-located) | `#FF6F00` |
| Accent/Links | `#00ACC1` |
| Negative/Curtailment | `#D32F2F` |

---

## Data Strategy

### Current Approach

Scripts use **synthetic/example data** when real NEMOSIS data is unavailable. This allows development without the external data cache.

### Data Sources

1. **NEMOSIS:** Historical NEM dispatch and pricing (requires external cache)
2. **OpenElectricity API:** Generator metadata, locations
3. **Synthetic:** Generated data matching expected patterns

### Path Configuration

Update `scripts/utils/data_paths.py` for your environment:

```python
# Key path constants
OUTPUTS_DIR = Path(__file__).parent.parent.parent / "data" / "outputs"
NEMOSIS_DATA_ROOT = Path(os.environ.get("NEMOSIS_DATA_PATH", "/path/to/nemosis"))
```

---

## Known Issues and Workarounds

### Issue 1: Quarto Python Execution Disabled

**Cause:** Jupyter kernel compatibility issues with system Python
**Workaround:** Pre-render all charts as HTML, embed via iframe

### Issue 2: Windows Paths in Scripts

**Cause:** Original development on Windows, some paths hardcoded
**Workaround:** Scripts should use `data_paths.py` constants; update as needed

### Issue 3: NEMOSIS Data Not Available

**Cause:** Large data cache is external to repository
**Workaround:** Scripts fall back to synthetic data generation

### Issue 4: MLF Impact Script Errors

**Status:** Reported in previous plans, may need debugging
**Action:** Test script, fix if errors occur, or simplify to synthetic data

---

## Success Criteria

### Minimum Viable Product

- [ ] All section content renders in Quarto
- [ ] At least one chart per section (4 charts minimum)
- [ ] Charts are interactive (hover, zoom)
- [ ] Decision tree provides actionable framework

### Full Implementation

- [ ] All 10+ planned charts generated
- [ ] PyPSA scenarios run successfully
- [ ] IRR comparison across scenarios displayed
- [ ] Report provides quantitative investment guidance

---

## Agent Instructions

When working on this project:

1. **Read CLAUDE.md first** - Critical development context
2. **Check script status** - Many scripts exist but outputs don't
3. **Use style_config.py** - Maintain consistent styling
4. **Test incrementally** - Run one script, check output, then proceed
5. **Use synthetic data** - Don't block on missing real data
6. **Commit frequently** - Preserve working state

### Testing a Script

```bash
# Navigate to project root
cd /path/to/hybrid-pv-blog

# Run script
python scripts/sectionX/script_name.py

# Check output
ls data/outputs/sectionX/

# View in browser
# Open the generated HTML file
```

### If a Script Fails

1. Read the error message carefully
2. Check for missing imports (`pip install <package>`)
3. Check for path issues (update `data_paths.py`)
4. Check for data issues (ensure fallback to synthetic data exists)
5. Simplify the script if needed to generate basic output

---

## Archived Plans

Previous planning documents have been moved to `/plan/archived/`. These contain historical context but should not be used for current implementation decisions:

- `ALIGNMENT_PLAN_ARCHIVED.md` - Gap analysis from earlier project state
- `LOCAL_AGENT_TASKS_ARCHIVED.md` - Outdated execution guide
- `original_draft_ARCHIVED.md` - Original project requirements
- `STYLE_GUIDE_ARCHIVED.md` - Design system (core colors still valid)

---

*Plan maintained by project contributors. Update this document when significant changes occur.*
