# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a Quarto-based research report analyzing battery energy storage system (BESS) investment decisions in Australia's National Electricity Market (NEM). The core question: **Does co-locating battery storage with solar PV create value, or does it destroy returns compared to standalone BESS deployment?**

## Critical Development Context

### Python Environment
- **Environment:** `hybridpv` (mamba/conda environment at `C:\Users\matts\miniforge3\envs\hybridpv`)
- **Python Version:** 3.11+
- **Always use this environment** when running analysis scripts: `C:\Users\matts\miniforge3\envs\hybridpv\python.exe`

### Quarto Execution Issue
**IMPORTANT:** Python code execution is **DISABLED** in Quarto due to Jupyter setup issues with the system Python 3.14.2. Instead, use **HTML iframe embedding** for charts:
- Generate charts independently using Python scripts
- Embed pre-rendered HTML/JSON files in sections using: `<iframe src="../data/outputs/sectionX/chart.html"></iframe>`
- Quarto config: `execute.enabled: false`

### Data Path Architecture
- **NEMOSIS Data:** Cached at `C:\Users\matts\Documents\Aus research\Nemosis_data` (external to project)
- **Project Outputs:** `data/outputs/section1/`, `section3/`, `section4/`, `section5/`
- **Path Management:** Use `scripts/utils/data_paths.py` for centralized path constants

## Build and Development Commands

### Environment Setup
```bash
# Activate the correct Python environment
mamba activate hybridpv

# Install dependencies (if needed)
pip install -r requirements.txt
```

### Running Analysis Scripts
```bash
# Generate individual charts
cd "C:\Users\matts\Documents\Aus research\Hybrid PV BESS vs standalone\Code\Git\Hybrid_PV_Blog"

# Section 1: Investment Problem
C:\Users\matts\miniforge3\envs\hybridpv\python.exe scripts/section1/s1_solar_price_curtailment.py

# Section 3: Trade-off Analysis
C:\Users\matts\miniforge3\envs\hybridpv\python.exe scripts/section3/s3_bess_capacity_growth.py
C:\Users\matts\miniforge3\envs\hybridpv\python.exe scripts/section3/s3_bess_map_colocation.py

# Section 4: Technical Constraints (tested and working)
C:\Users\matts\miniforge3\envs\hybridpv\python.exe scripts/section4/s4_revenue_skew.py
C:\Users\matts\miniforge3\envs\hybridpv\python.exe scripts/section4/s4_mlf_map_nsw.py
```

### Rendering the Report
```bash
# Render Quarto book to static HTML
quarto render

# Preview locally (if server issues occur, use render + manual browser)
quarto preview

# Output location: docs/index.html
# View in browser: explorer docs/index.html
```

### Testing Chart Integration
```bash
# After generating charts, test blog rendering
quarto render
# Check that iframe references work correctly in browser
# Verify chart interactivity in sections/04_technical_constraints.html
```

## Architecture and Code Organization

### Analysis Script Pattern
Each analysis script follows this structure:
1. **Import utilities** from `scripts/utils/` (using `sys.path.append(str(Path(__file__).parent.parent))`)
2. **Load/process data** using NEMOSIS cached data or generate example data
3. **Create visualization** using Plotly (charts) or Folium (maps)
4. **Save outputs** to `data/outputs/sectionX/` as both HTML and JSON
5. **Return figure object** for potential further use

### Key Utility Modules
- **`style_config.py`**: Plotly template `TEMPLATE`, color palette `COLORS`, Lato font theming
- **`data_paths.py`**: Centralized paths (`OUTPUTS_DIR`, `NEMOSIS_DATA_ROOT`, section outputs)
- **`nemosis_helpers.py`**: NEMOSIS data loading functions (currently simplified)

### Import Pattern for Scripts
```python
# Standard import pattern for section scripts
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))
from utils.style_config import TEMPLATE, COLORS
from utils.data_paths import OUTPUTS_DIR, ensure_output_dirs
```

### Quarto Section Structure
- **Markdown content** with analysis narrative
- **HTML iframe embeds** for pre-generated charts: `<iframe src="../data/outputs/sectionX/chart.html" width="100%" height="500"></iframe>`
- **Styled placeholders** for missing charts using color-coded divs
- **No Python code execution** (disabled due to Jupyter issues)

### Chart Integration Strategy
1. **Generate chart files** independently using Python scripts
2. **Embed in sections** using HTML iframes with relative paths
3. **Use placeholders** for charts not yet generated
4. **Test in browser** after `quarto render` to verify interactivity

## Working Scripts Status

### ✅ Tested and Working
- `scripts/section4/s4_revenue_skew.py` - Generates revenue concentration analysis
- `scripts/section4/s4_mlf_map_nsw.py` - Generates interactive MLF choropleth map

### ⚠️ Known Issues
- `scripts/section4/s4_mlf_impact_revenue.py` - Runtime errors (simplified version created)
- Most section1 and section3 scripts - Not yet tested with actual data
- NEMOSIS data loading - Uses example data due to missing cached data

### 🎯 Current Chart Outputs
- `data/outputs/section4/revenue_skew.html` - Revenue concentration (50% in 5.7% of hours)
- `data/outputs/section4/mlf_map_nsw.html` - Interactive NSW generator MLF map

## Key Technical Decisions

### Why HTML Iframe Embedding?
- Quarto Python execution fails due to system Python 3.14.2 Jupyter issues
- Pre-rendered charts ensure interactivity works in browser
- Allows independent testing of analysis scripts
- Avoids complex Jupyter setup debugging

### Color Scheme
- **Solar PV:** `#FFD700` (yellow)  
- **Battery:** `#7B1FA2` (purple)
- **Battery Co-located:** `#FF6F00` (dark orange)
- **Accent:** `#00ACC1` (teal)
- **Consistent** across all charts via `style_config.py`

### Data Management
- **NEMOSIS data** is external (not in git repo): `C:\Users\matts\Documents\Aus research\Nemosis_data`
- **Chart outputs** are gitignored for repo size
- **Working charts** are embedded directly in blog sections
- **Example data** used when real data unavailable

## Development Workflow

1. **Create analysis script** in appropriate `scripts/sectionX/` folder
2. **Test script independently** using hybridpv environment
3. **Generate chart outputs** to `data/outputs/sectionX/`
4. **Embed in Quarto section** using HTML iframe
5. **Render blog** with `quarto render`
6. **Test in browser** to verify chart interactivity
7. **Commit working scripts** with tested status

## Important Notes

- **Always use hybridpv environment** for Python script execution
- **Test scripts before embedding** - broken scripts break chart rendering
- **Check iframe paths** - relative paths must be correct for Quarto output structure
- **Preserve working scripts** - we have limited tested functionality
- **Blog is currently viewable** at `docs/index.html` with embedded interactive charts