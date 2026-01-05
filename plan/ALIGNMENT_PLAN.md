# Project Alignment Plan: Beyond the Solar Curve

## Executive Summary

This document compares the **original project request** with the **current implementation state**, identifies key divergences and roadblocks, and provides detailed sub-plans to bring the project back on track. Each sub-plan is designed to be executed independently by agents with refreshed context.

---

## Part 1: Gap Analysis

### 1.1 Original Request vs Current State

| Requirement | Original Request | Current State | Gap Severity |
|-------------|------------------|---------------|--------------|
| **Technology Platform** | Shiny (interactive web app) | Quarto (static book) | **MAJOR** |
| **Python Execution** | Live code execution in browser | Disabled (iframe embedding) | **MAJOR** |
| **Code Visibility** | Readers can see analysis code | Code hidden, only outputs shown | **MODERATE** |
| **Section 1** | Solar price collapse + curtailment chart | Placeholder div (no real chart) | **HIGH** |
| **Section 2** | BESS Integration Thesis | **MISSING ENTIRELY** | **CRITICAL** |
| **Section 3** | 4 charts (capacity, map, diagram, revenue buckets) | Placeholder divs (no real charts) | **HIGH** |
| **Section 4** | 3 charts (revenue skew, MLF impact, MLF map) | 2 working charts, 1 missing | **MODERATE** |
| **Section 5** | Strategic Framework + PyPSA modeling | **MISSING ENTIRELY** | **CRITICAL** |
| **Decision Tree** | Interactive dtreeviz diagram | Not implemented | **HIGH** |
| **Data Source** | Real NEMOSIS data | Mostly simulated/example data | **HIGH** |
| **PyPSA Modeling** | Sizing optimization, financial model | Not implemented | **CRITICAL** |

### 1.2 Key Roadblocks Identified

1. **Jupyter/Python 3.14 Incompatibility**: System Python 3.14.2 causes Quarto Python execution to fail. Workaround: iframe embedding of pre-rendered charts.

2. **NEMOSIS Data Access**: Scripts reference Windows paths (`C:\Users\matts\...`) that don't exist in current environment. No actual cached data available.

3. **Technology Mismatch**: Original request specified Shiny for interactivity, but Quarto was implemented instead. Quarto is static-first and doesn't provide the same level of interactivity.

4. **Missing Context Files**: Reference notebooks (`.ipynb` files) and Excel files from original request are not in repository.

5. **PyPSA Integration**: No PyPSA modeling code has been written despite being core to Section 5.

---

## Part 2: Strategic Decisions Required

Before proceeding, the following decisions need resolution:

### Decision 1: Technology Platform
**Options:**
- **A) Stay with Quarto**: Accept static output, focus on pre-rendered charts. Simpler but less interactive.
- **B) Migrate to Shiny**: Follow original request. More work but provides true interactivity.
- **C) Hybrid (Quarto + Observable/Shiny widgets)**: Quarto with embedded interactive components.

**Recommendation**: Option A (Quarto) for MVP, with clear documentation that interactivity is via Plotly hover/zoom only. Shiny migration as future enhancement.

### Decision 2: Data Strategy
**Options:**
- **A) Synthetic Data**: Generate realistic synthetic data that matches expected patterns.
- **B) Public Data Sources**: Use OpenElectricity API and publicly available AEMO data.
- **C) Wait for Real Data**: Block until NEMOSIS cached data is available.

**Recommendation**: Option B (Public Data) where available, Option A (Synthetic) for gaps.

### Decision 3: Python Environment
**Options:**
- **A) Fix Quarto Execution**: Debug Jupyter kernel configuration.
- **B) Continue Iframe Approach**: Pre-render all charts externally.
- **C) Switch to R/Observable**: Use native Quarto execution with different languages.

**Recommendation**: Option B (Iframe Approach) is already working. Focus on content, not tooling.

---

## Part 3: Detailed Sub-Plans

Each sub-plan is self-contained and can be executed by an agent with a fresh context window. Sub-plans are ordered by dependency (earlier plans should complete first where noted).

---

### SUB-PLAN 1: UI/Design System Overhaul

**Priority**: HIGH
**Estimated Complexity**: MEDIUM
**Dependencies**: None

#### Objective
Create a professional, consistent design system that elevates the visual quality of the report beyond basic Quarto theming.

#### Current Problems
1. Basic Cosmo theme with minimal customization
2. Placeholder charts use inconsistent styling (styled divs)
3. No reusable component patterns for analysis sections
4. Missing visual hierarchy for key findings/callouts
5. Tables lack professional styling
6. No consistent chart embedding pattern

#### Tasks

**Task 1.1: Enhanced CSS Framework**
- Location: `assets/styles/custom.css`
- Add custom callout box styles matching the color palette:
  - `.analysis-box` - Container for chart sections (solar yellow border for PV, purple for battery)
  - `.key-finding` - Highlighted insight boxes
  - `.data-note` - Small notes about data sources
  - `.chart-placeholder` - Styled placeholder for missing charts
- Add responsive iframe container styles
- Add print-friendly styles
- Add dark mode support (optional)

**Task 1.2: Chart Embedding Component**
Create a standardized pattern for embedding charts:
```html
<div class="chart-container" data-status="complete|pending|error">
  <div class="chart-header">
    <h4 class="chart-title">Chart Title</h4>
    <span class="chart-status-badge">Status</span>
  </div>
  <iframe src="path/to/chart.html" class="chart-iframe"></iframe>
  <div class="chart-footer">
    <span class="chart-source">Data: AEMO via NEMOSIS</span>
    <a href="path/to/script.py" class="chart-code-link">View Analysis Code</a>
  </div>
</div>
```

**Task 1.3: Quarto Configuration Enhancement**
- Update `_quarto.yml` to use custom partials
- Add proper page metadata
- Configure proper code linking
- Add custom SCSS variables integration

**Task 1.4: Navigation and TOC Improvements**
- Add section progress indicators
- Create chapter summary boxes at section starts
- Add "Key Takeaways" component styling

#### Deliverables
1. Enhanced `custom.css` with complete design system
2. Updated `_quarto.yml` with improved configuration
3. Reusable HTML include files for chart containers
4. Style guide documentation (in `/plan/STYLE_GUIDE.md`)

#### Success Criteria
- All sections use consistent visual styling
- Charts have clear status indicators (complete/pending)
- Code links are visible and functional
- Report looks professional when rendered

---

### SUB-PLAN 2: Section 1 - Solar Price Collapse Analysis

**Priority**: HIGH
**Estimated Complexity**: MEDIUM
**Dependencies**: Sub-Plan 1 (design system)

#### Objective
Complete the Section 1 analysis with a real or realistic synthetic dual-axis chart showing solar hour price collapse and curtailment growth (2018-2025).

#### Current State
- Content narrative is complete and well-written
- Chart placeholder exists but no actual chart
- Script `scripts/section1/s1_solar_price_curtailment.py` exists but may not work

#### Data Requirements
1. **NSW wholesale prices (2018-2025)**: Filter for hours 10:00-16:00, calculate annual averages
2. **Solar curtailment data**: AEMO curtailment estimates or proxy calculation

#### Tasks

**Task 2.1: Data Acquisition**
- Option A: Use OpenElectricity API for price data
- Option B: Generate synthetic data matching documented trends:
  - 2018: ~$85/MWh solar-hour average, <1% curtailment
  - 2025: ~$35/MWh solar-hour average, ~5% curtailment

**Task 2.2: Update Analysis Script**
- Location: `scripts/section1/s1_solar_price_curtailment.py`
- Implement data loading (real or synthetic)
- Create dual-axis Plotly chart:
  - Left axis: Average price ($/MWh), bar chart, yellow color
  - Right axis: Curtailment (%), line chart, red color
- Use style_config.py for consistent theming
- Save to `data/outputs/section1/solar_price_curtailment.html`

**Task 2.3: Update Section Content**
- Location: `sections/01_investment_problem.qmd`
- Replace placeholder div with proper chart container
- Add iframe embedding with correct path
- Add chart source attribution
- Link to analysis script

#### Deliverables
1. Working `s1_solar_price_curtailment.py` script
2. Generated `data/outputs/section1/solar_price_curtailment.html`
3. Updated `sections/01_investment_problem.qmd` with embedded chart

#### Success Criteria
- Chart renders correctly in browser
- Dual axes display with correct scales
- Hover information shows year, price, and curtailment
- Chart tells the story of solar price collapse

---

### SUB-PLAN 3: Section 3 - Battery Deployment Charts

**Priority**: HIGH
**Estimated Complexity**: HIGH
**Dependencies**: Sub-Plan 1 (design system)

#### Objective
Complete Section 3's four analysis charts: BESS capacity growth, co-location map, revenue buckets, and co-location diagram.

#### Current State
- Content narrative is comprehensive
- All four chart positions have placeholders
- Scripts exist in `scripts/section3/` but are incomplete

#### Chart 3.1: BESS Capacity Growth (Column Chart)

**Data Requirements:**
- BESS MWh by year (2018-2028)
- Stacked by status: operating, committed, anticipated
- Source: NEM Generation Information spreadsheet (not in repo)

**Tasks:**
- Create synthetic data based on documented trends (500 MWh 2019 → 10,000+ MWh 2026-2027)
- Update `scripts/section3/s3_bess_capacity_growth.py`
- Generate stacked bar chart with purple palette variations
- Save to `data/outputs/section3/bess_capacity_growth.html`

#### Chart 3.2: Battery Co-location Map

**Data Requirements:**
- Battery locations (lat/long) across NEM
- Classification: standalone vs co-located (within 1km of solar)
- Source: OpenElectricity API + geospatial analysis

**Tasks:**
- Update `scripts/section3/s3_bess_map_colocation.py`
- Fetch battery and solar locations from OpenElectricity API
- Calculate distances to determine co-location status
- Create Folium/Plotly map with purple (standalone) and orange (co-located) markers
- Save to `data/outputs/section3/bess_map_colocation.html`

#### Chart 3.3: Revenue by Price Bucket

**Data Requirements:**
- NSW battery dispatch and revenue by price range
- Price buckets: <-$1000, -$1000 to -$500, ..., >$2000
- Source: NEMOSIS dispatch data (or synthetic)

**Tasks:**
- Update `scripts/section3/s3_battery_revenue_buckets.py`
- Generate realistic synthetic revenue distribution
- Create horizontal bar chart showing revenue percentage per bucket
- Highlight negative pricing and extreme event revenue
- Save to `data/outputs/section3/battery_revenue_buckets.html`

#### Chart 3.4: Co-location Configuration Diagram

**Data Requirements:**
- Technical schematic of AC-coupled, DC-coupled, non-hybrid configurations
- Source: Re-create from Modo Energy diagram reference

**Tasks:**
- Update `scripts/section3/s3_colocation_diagram.py`
- Use graphviz or schemdraw to create technical diagram
- Show electrical connections, DUIDs, grid connection points
- Save as both HTML and PNG for flexibility
- Save to `data/outputs/section3/colocation_diagram.html`

#### Deliverables
1. Four working scripts in `scripts/section3/`
2. Four chart files in `data/outputs/section3/`
3. Updated `sections/03_tradeoff_analysis.qmd` with embedded charts

#### Success Criteria
- All four charts render and are interactive (where applicable)
- Map shows clear standalone vs co-located distinction
- Revenue bucket chart demonstrates negative pricing opportunity
- Diagram clearly explains three configuration options

---

### SUB-PLAN 4: Section 4 - Technical Constraints (Complete)

**Priority**: MEDIUM
**Estimated Complexity**: LOW
**Dependencies**: Sub-Plan 1 (design system)

#### Objective
Complete Section 4 by adding the missing MLF impact analysis chart.

#### Current State
- Two charts working: `revenue_skew.html`, `mlf_map_nsw.html`
- One chart missing: MLF impact on battery revenue (like Modo BESS revenue chart)
- Script `s4_mlf_impact_revenue.py` exists but has runtime errors

#### Tasks

**Task 4.1: Fix MLF Impact Script**
- Location: `scripts/section4/s4_mlf_impact_revenue.py`
- Debug and fix runtime errors
- Generate synthetic data showing:
  - X-axis: Batteries ranked by MLF
  - Y-axis: Annual revenue impact (% reduction from optimal)
- Create bar chart with red gradient for low-MLF batteries
- Save to `data/outputs/section4/mlf_impact_revenue.html`

**Task 4.2: Update Section Content**
- Location: `sections/04_technical_constraints.qmd`
- Add embedding for MLF impact chart
- Remove duplicate MLF map code block (lines 96-103 have Python code that won't execute)
- Ensure all three charts are properly embedded

#### Deliverables
1. Fixed `s4_mlf_impact_revenue.py` script
2. Generated `data/outputs/section4/mlf_impact_revenue.html`
3. Updated `sections/04_technical_constraints.qmd`

#### Success Criteria
- All three Section 4 charts render correctly
- No Python code blocks in QMD file (all charts via iframe)
- MLF impact clearly demonstrates the "hidden tax" narrative

---

### SUB-PLAN 5: Create Section 2 - BESS Integration Thesis

**Priority**: HIGH
**Estimated Complexity**: MEDIUM
**Dependencies**: Sub-Plan 1 (design system)

#### Objective
Create the missing Section 2 that bridges the problem statement (Section 1) with the trade-off analysis (Section 3).

#### Original Request Content
From the original draft:
- 2.1 Restoring Value: Battery storage as solution for PV assets
- 2.2 The Investor Dilemma: Standalone vs co-located as distinct asset classes
- Key question: Does PV add value to BESS or drag down returns?

#### Tasks

**Task 5.1: Create Section File**
- Create `sections/02_bess_integration.qmd`
- Write narrative content covering:
  - Battery storage as solution to solar intermittency
  - Shift generation to high-value evening peaks
  - Protect against curtailment (behind-the-meter)
  - Two distinct asset class models
  - The core investor question

**Task 5.2: Update Quarto Configuration**
- Update `_quarto.yml` to include Section 2 in book chapters
- Ensure correct ordering: 01, 02, 03, 04

**Task 5.3: Add Transition Content**
- End Section 1 with clear transition to Section 2
- Begin Section 3 with reference back to Section 2

#### Deliverables
1. New file `sections/02_bess_integration.qmd`
2. Updated `_quarto.yml`
3. Minor edits to Sections 1 and 3 for flow

#### Success Criteria
- Section 2 provides clear logical bridge
- Report flow is: Problem → Solution thesis → Trade-off analysis
- No charts required (narrative section)

---

### SUB-PLAN 6: Create Section 5 - Strategic Framework (Core)

**Priority**: CRITICAL
**Estimated Complexity**: HIGH
**Dependencies**: Sub-Plans 1-4 (builds on previous analysis)

#### Objective
Create Section 5 with the strategic decision framework and prepare for PyPSA integration.

#### Original Request Content
Five-step framework:
1. Determine Hurdle Rate & Benchmark
2. Quantify Efficiencies (capex/opex savings)
3. Determine Contracting Options
4. Location Viability (MLF, curtailment assessment)
5. Modeling & Validation (PyPSA dispatch + financial model)

#### Tasks

**Task 6.1: Create Section File**
- Create `sections/05_strategic_framework.qmd`
- Write narrative content for Steps 1-4
- Create placeholder for Step 5 (PyPSA modeling)

**Task 6.2: Create Decision Tree Visualization**
- Create `scripts/section5/s5_decision_tree.py`
- Use dtreeviz or graphviz to create decision flowchart
- Key decision nodes:
  - New build vs retrofit?
  - Target hurdle rate achieved?
  - Capex synergies > MLF penalty?
  - Green premium available?
  - CIS eligibility?
- Save to `data/outputs/section5/decision_tree.html`

**Task 6.3: Create Sensitivity Parameters Table**
- Design interactive parameter table showing:
  - Capex assumptions (PV $/W, BESS $/kWh)
  - Revenue assumptions (electricity price, FCAS, capacity payments)
  - MLF scenarios
  - Return hurdles

**Task 6.4: Update Quarto Configuration**
- Update `_quarto.yml` to include Section 5

#### Deliverables
1. New file `sections/05_strategic_framework.qmd`
2. Decision tree script and HTML output
3. Parameter table (static or interactive)
4. Updated `_quarto.yml`

#### Success Criteria
- Framework is actionable (readers can apply to their projects)
- Decision tree clearly guides standalone vs co-located choice
- PyPSA placeholder ready for Sub-Plan 7

---

### SUB-PLAN 7: PyPSA Dispatch Modeling

**Priority**: CRITICAL
**Estimated Complexity**: VERY HIGH
**Dependencies**: Sub-Plan 6 (framework established)

#### Objective
Implement PyPSA-based dispatch optimization comparing standalone BESS vs co-located configurations.

#### Scope
This is the most complex sub-plan and should be broken into phases:

**Phase 7A: Model Setup**
- Create `scripts/section5/pypsa_model/` directory structure
- Implement base network with NSW bus
- Add generator components (PV, merchant grid)
- Add storage unit (BESS)
- Add load components (PPA, merchant sell)

**Phase 7B: Scenario Definition**
- Define configuration scenarios:
  - Standalone BESS (any location, grid charging)
  - AC-coupled hybrid (shared connection, independent dispatch)
  - DC-coupled hybrid (behind-the-meter, solar charging only)
- Parameterize: PV size, BESS power, BESS duration

**Phase 7C: Optimization**
- Run annual dispatch optimization for each scenario
- Apply MLF adjustments per scenario
- Calculate annual revenue and costs

**Phase 7D: Financial Model**
- Calculate capex (with/without synergies)
- Calculate opex
- Compute levered IRR for each scenario
- Sensitivity analysis on key parameters

**Phase 7E: Results Visualization**
- Create comparison charts:
  - Dispatch profile comparison (sample week)
  - Annual revenue by source
  - IRR comparison across scenarios
  - Sensitivity tornado chart
- Save to `data/outputs/section5/`

#### Tasks

**Task 7.1: Create Model Infrastructure**
- Create `scripts/section5/pypsa_model/__init__.py`
- Create `scripts/section5/pypsa_model/network.py` (network setup)
- Create `scripts/section5/pypsa_model/scenarios.py` (scenario definitions)
- Create `scripts/section5/pypsa_model/constraints.py` (custom constraints)

**Task 7.2: Load Time Series Data**
- Source solar capacity factors (synthetic or from OpenElectricity)
- Source price data (synthetic matching 2025 patterns)
- Create `scripts/section5/pypsa_model/timeseries.py`

**Task 7.3: Implement Scenarios**
- Standalone BESS scenario
- AC-coupled hybrid scenario
- DC-coupled hybrid scenario
- Create `scripts/section5/pypsa_model/run_scenarios.py`

**Task 7.4: Financial Calculations**
- Create `scripts/section5/pypsa_model/financials.py`
- Implement CAPEX calculation (with synergy discounts)
- Implement OPEX calculation
- Implement IRR calculation

**Task 7.5: Results Visualization**
- Create `scripts/section5/s5_pypsa_results.py`
- Generate comparison charts
- Save outputs to `data/outputs/section5/`

**Task 7.6: Integrate into Section 5**
- Update `sections/05_strategic_framework.qmd`
- Embed PyPSA result charts
- Add interpretation narrative

#### Deliverables
1. Complete PyPSA model in `scripts/section5/pypsa_model/`
2. Time series data files
3. Scenario comparison charts in `data/outputs/section5/`
4. Updated Section 5 with embedded results

#### Success Criteria
- Model runs without errors
- Results demonstrate trade-offs quantitatively
- IRR comparison provides clear investment guidance
- Sensitivity analysis shows critical parameters

---

### SUB-PLAN 8: Data Infrastructure & Portability

**Priority**: MEDIUM
**Estimated Complexity**: MEDIUM
**Dependencies**: None (can run in parallel)

#### Objective
Establish robust data infrastructure that works across environments and allows reproducibility.

#### Current Problems
1. Windows-specific paths hardcoded
2. No data download/generation scripts
3. Unclear which data is real vs synthetic
4. No data versioning or documentation

#### Tasks

**Task 8.1: Update Path Configuration**
- Update `scripts/utils/data_paths.py` to use environment-aware paths
- Support both Windows and Linux/Mac paths
- Use environment variables for data roots

**Task 8.2: Create Data Generation Scripts**
- Create `scripts/data_generation/` directory
- `generate_synthetic_prices.py` - NSW prices 2018-2025
- `generate_synthetic_solar.py` - Solar capacity factors
- `generate_synthetic_batteries.py` - Battery metadata and locations

**Task 8.3: Create Data Fetching Scripts**
- Update `scripts/download/` scripts for OpenElectricity API
- Add caching layer for API responses
- Document rate limits and usage

**Task 8.4: Data Documentation**
- Create `data/README.md` documenting:
  - Data sources (real vs synthetic)
  - Data schema/formats
  - Generation/download instructions
  - Data versioning approach

#### Deliverables
1. Updated `data_paths.py` with cross-platform support
2. Data generation scripts in `scripts/data_generation/`
3. Updated download scripts in `scripts/download/`
4. `data/README.md` documentation

#### Success Criteria
- Project runs on any platform without path errors
- Data can be regenerated from scratch
- Clear documentation of data provenance

---

### SUB-PLAN 9: Report Finalization & Quality Assurance

**Priority**: LOW (final phase)
**Estimated Complexity**: MEDIUM
**Dependencies**: All previous sub-plans

#### Objective
Final polish, quality assurance, and documentation.

#### Tasks

**Task 9.1: Content Review**
- Proofread all section narratives
- Ensure consistent terminology
- Verify all statistics match chart data
- Check cross-references between sections

**Task 9.2: Chart Quality Check**
- Verify all charts render correctly
- Check hover interactions work
- Ensure consistent styling across charts
- Verify chart titles and labels are accurate

**Task 9.3: Update Index Page**
- Update `index.qmd` with accurate status
- Add proper key findings
- Create executive summary

**Task 9.4: README Updates**
- Update `README.md` with:
  - Project description
  - Setup instructions
  - Running the report
  - Contributing guidelines

**Task 9.5: Final Render and Test**
- Run `quarto render`
- Test all pages in browser
- Check mobile responsiveness
- Verify print styling

#### Deliverables
1. Polished content across all sections
2. Working, styled charts
3. Updated `index.qmd` and `README.md`
4. Final rendered report in `docs/`

#### Success Criteria
- Report renders without errors
- All charts interactive and correctly styled
- Content is professional and accurate
- Documentation complete for future maintainers

---

## Part 4: Execution Order

### Phase 1: Foundation (Parallel)
- **Sub-Plan 1**: UI/Design System Overhaul
- **Sub-Plan 8**: Data Infrastructure & Portability

### Phase 2: Missing Content
- **Sub-Plan 5**: Create Section 2 (BESS Integration Thesis)
- **Sub-Plan 2**: Section 1 Chart Completion
- **Sub-Plan 3**: Section 3 Charts (4 charts)
- **Sub-Plan 4**: Section 4 Completion

### Phase 3: Core Analysis
- **Sub-Plan 6**: Section 5 Framework (narrative + decision tree)
- **Sub-Plan 7**: PyPSA Modeling (complex, may need multiple sessions)

### Phase 4: Finalization
- **Sub-Plan 9**: Report Finalization & QA

---

## Part 5: Agent Instructions

When executing any sub-plan, agents should:

1. **Read CLAUDE.md first** - Contains critical context about the project
2. **Check current file state** - Files may have changed since this plan was written
3. **Use style_config.py** - All charts must use the defined color palette and template
4. **Save outputs correctly** - Charts to `data/outputs/sectionX/`, scripts to `scripts/sectionX/`
5. **Test before completing** - Render Quarto and verify chart embedding
6. **Document changes** - Update CLAUDE.md if significant changes are made
7. **Commit incrementally** - Commit working state after each major task

### Environment Notes
- Python environment: `hybridpv` (mamba/conda)
- Quarto execution: DISABLED (use iframe embedding)
- Data paths: See `scripts/utils/data_paths.py`
- Chart library: Plotly (HTML output with CDN)
- Map library: Folium (HTML output)

---

## Appendix A: File Structure Reference

```
hybrid-pv-blog/
├── _quarto.yml           # Quarto configuration
├── index.qmd             # Landing page
├── CLAUDE.md             # Agent instructions
├── requirements.txt      # Python dependencies
│
├── sections/
│   ├── 01_investment_problem.qmd
│   ├── 02_bess_integration.qmd      # TO CREATE
│   ├── 03_tradeoff_analysis.qmd
│   ├── 04_technical_constraints.qmd
│   └── 05_strategic_framework.qmd   # TO CREATE
│
├── scripts/
│   ├── utils/
│   │   ├── style_config.py
│   │   ├── data_paths.py
│   │   └── nemosis_helpers.py
│   ├── section1/
│   │   └── s1_solar_price_curtailment.py
│   ├── section3/
│   │   ├── s3_bess_capacity_growth.py
│   │   ├── s3_bess_map_colocation.py
│   │   ├── s3_battery_revenue_buckets.py
│   │   └── s3_colocation_diagram.py
│   ├── section4/
│   │   ├── s4_revenue_skew.py         # WORKING
│   │   ├── s4_mlf_map_nsw.py          # WORKING
│   │   └── s4_mlf_impact_revenue.py   # NEEDS FIX
│   ├── section5/                       # TO CREATE
│   │   ├── s5_decision_tree.py
│   │   ├── s5_pypsa_results.py
│   │   └── pypsa_model/
│   └── download/
│
├── data/
│   ├── outputs/
│   │   ├── section1/
│   │   ├── section3/
│   │   ├── section4/
│   │   │   ├── revenue_skew.html      # EXISTS
│   │   │   └── mlf_map_nsw.html       # EXISTS
│   │   └── section5/
│   └── README.md                       # TO CREATE
│
├── assets/
│   └── styles/
│       └── custom.css
│
├── skills/
│   ├── NEMOSIS_skill.md
│   └── PyPSA_skill.md
│
├── plan/
│   ├── original_draft.md
│   └── ALIGNMENT_PLAN.md              # THIS FILE
│
└── docs/                              # Rendered output
```

---

## Appendix B: Color Palette Quick Reference

| Purpose | Color | Hex Code |
|---------|-------|----------|
| Solar PV | Yellow | `#FFD700` |
| Wind | Green | `#2E7D32` |
| Battery (Standalone) | Purple | `#7B1FA2` |
| Battery (Co-located) | Dark Orange | `#FF6F00` |
| Accent/Links | Teal | `#00ACC1` |
| Text | Dark Blue-Grey | `#2C3E50` |
| Negative/Curtailment | Red | `#D32F2F` |
| Positive | Dark Green | `#388E3C` |

---

*Plan created: 2026-01-05*
*Last updated: 2026-01-05*
