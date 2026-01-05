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
| **Content (Sections 1-5)** | Needs Polish | Narrative exists but reads too AI-like, needs more depth |
| **Chart Scripts** | Complete | Scripts exist for all required charts |
| **Chart Outputs (HTML)** | Not Generated | Scripts need to be run locally with real NEMOSIS data |
| **Quarto Rendering** | Functional | Using iframe embedding pattern |

**Primary Gaps:**
1. **Content quality** - Section narratives need editing to sound more natural and add substantive detail
2. **Chart generation** - Scripts must be run locally to generate HTML outputs using real NEM data

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

**Chart Requirements:**
1. **Decision Tree:** Interactive flowchart for standalone vs co-located decision

**Note:** PyPSA model infrastructure exists in `scripts/section5/pypsa_model/` but is **out of scope** for the current phase. Focus on the decision tree and narrative content first.

---

## Priority Task List

### Priority 1: Improve Content Quality (Can be done remotely)

The section narratives currently read too AI-like and lack depth. Content editing needed:
- Make writing more natural and less formulaic
- Add substantive detail and industry insight
- Improve flow between sections
- Ensure professional but accessible tone

**Sections needing attention:**
- All five sections could benefit from polish
- Add more specific examples and real-world context
- Strengthen the analytical narrative

### Priority 2: Generate Chart Outputs (Requires local environment)

Scripts must be run locally with real NEMOSIS data:

```bash
# Section 1
python scripts/section1/s1_solar_price_curtailment.py

# Section 3
python scripts/section3/s3_bess_capacity_growth.py
python scripts/section3/s3_bess_map_colocation.py
python scripts/section3/s3_battery_revenue_buckets.py

# Section 4
python scripts/section4/s4_revenue_skew.py
python scripts/section4/s4_mlf_map_nsw.py
python scripts/section4/s4_mlf_impact_revenue.py

# Section 5
python scripts/section5/s5_decision_tree.py
```

### Priority 3: Debug Script Issues (If needed)

If scripts fail:
1. **Import errors:** Install missing packages (`pip install <package>`)
2. **Path errors:** Update `data_paths.py` for current environment
3. **Data errors:** Ensure NEMOSIS data cache is properly configured

### Priority 4: Render Quarto Book

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

### Data Sources

All analysis uses **real NEM data** - no synthetic data:

1. **NEMOSIS:** Historical NEM dispatch and pricing data
   - Cached locally at `C:\Users\matts\Documents\Aus research\Nemosis_data`
   - See `skills/NEMOSIS_skill.md` for usage patterns

2. **OpenElectricity API:** Generator metadata, locations
   - Public API for facility information

3. **AEMO Excel Files:** Generation information spreadsheets
   - `NEM Generation Information Oct 2025.xlsx` for capacity data

### Path Configuration

Paths configured in `scripts/utils/data_paths.py`:
- Windows paths are set for the development environment
- Cross-platform detection handles Linux/Mac if needed

---

## Known Issues and Workarounds

### Issue 1: Quarto Python Execution Disabled

**Cause:** Jupyter kernel compatibility issues with system Python 3.14
**Workaround:** Pre-render all charts as HTML, embed via iframe
**Status:** This is the intended approach - not a bug

### Issue 2: NEMOSIS Data External to Repo

**Cause:** Large data cache (GB+) is stored outside the git repository
**Location:** `C:\Users\matts\Documents\Aus research\Nemosis_data`
**Action:** Ensure this path is accessible when running scripts locally

---

## Success Criteria

### Content Quality

- [ ] Section narratives read naturally (not AI-like)
- [ ] Sufficient depth and industry insight
- [ ] Professional but accessible tone
- [ ] Clear logical flow between sections

### Technical Completeness

- [ ] All section content renders in Quarto
- [ ] Charts generated for each section using real NEM data
- [ ] Charts are interactive (hover, zoom, pan)
- [ ] Decision tree provides actionable framework
- [ ] Report provides clear investment guidance

---

## Agent Instructions

### For Cloud/Remote Agents (no Python execution)

Focus on **content improvement**:
1. Edit QMD section files to improve narrative quality
2. Make writing less AI-like, more natural and substantive
3. Add industry context and specific examples
4. Review and fix any documentation issues

### For Local Agents (with Python environment)

Focus on **chart generation**:
1. **Read CLAUDE.md first** - Critical development context
2. **Activate environment:** `mamba activate hybridpv`
3. **Run scripts** to generate chart outputs
4. **Use real data** - NEMOSIS cache must be accessible
5. **Test in browser** - Verify charts are interactive

### Testing a Script Locally

```bash
# Navigate to project root
cd /path/to/hybrid-pv-blog

# Activate environment
mamba activate hybridpv

# Run script
python scripts/sectionX/script_name.py

# Check output
ls data/outputs/sectionX/

# View in browser
start data/outputs/sectionX/chart.html  # Windows
```

### If a Script Fails

1. Check error message carefully
2. Verify NEMOSIS data path is correct
3. Install missing packages (`pip install <package>`)
4. Check `data_paths.py` configuration

---

## Archived Plans

Previous planning documents have been moved to `/plan/archived/`. These contain historical context but should not be used for current implementation decisions:

- `ALIGNMENT_PLAN_ARCHIVED.md` - Gap analysis from earlier project state
- `LOCAL_AGENT_TASKS_ARCHIVED.md` - Outdated execution guide
- `original_draft_ARCHIVED.md` - Original project requirements
- `STYLE_GUIDE_ARCHIVED.md` - Design system (core colors still valid)

---

*Plan maintained by project contributors. Update this document when significant changes occur.*
