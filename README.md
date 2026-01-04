# Beyond the Solar Curve

**A Capital Allocation Framework for Co-located vs. Standalone BESS in the NEM**

## Overview

This report provides a comprehensive analysis framework for renewable energy developers and infrastructure investors to evaluate whether battery energy storage systems (BESS) should be co-located with solar PV plants in the Australian National Electricity Market (NEM).

## Project Structure

```
Hybrid_PV_Blog/
├── sections/              # Quarto report chapters
├── scripts/               # Python analysis scripts
│   ├── download/          # Data download scripts
│   ├── section1-5/        # Section-specific analyses
│   └── utils/             # Shared utilities
├── data/outputs/          # Generated charts and tables
├── assets/                # Static assets (CSS, images)
├── skills/                # Claude Code skill documentation
└── docs/                  # GitHub Pages output (auto-generated)
```

## Setup

### Prerequisites

- Python 3.11+
- Mamba or Conda
- Quarto 1.3+
- Git

### Environment Setup

```bash
# Create mamba environment
mamba create -n hybridpv python=3.11
mamba activate hybridpv

# Install dependencies
pip install -r requirements.txt

# Install Quarto separately (system package)
# Download from: https://quarto.org/docs/get-started/
```

### Data Prerequisites

This project uses cached NEMOSIS data. Run the download scripts first:

```bash
cd scripts/download
python download_dispatchprice.py
python download_dispatch_scada.py
python download_dispatchload.py
python download_generator_metadata.py
```

Data will be cached to: `C:\Users\matts\Documents\Aus research\Nemosis_data`

## Usage

### Generate All Analyses

Run individual analysis scripts to generate charts and tables:

```bash
cd scripts/section1
python s1_solar_price_curtailment.py

cd ../section3
python s3_bess_capacity_growth.py
python s3_bess_map_colocation.py
# ... etc
```

### Render Report

```bash
# Preview locally
quarto preview

# Render to HTML
quarto render

# Output will be in docs/ folder
```

### Deploy to GitHub Pages

```bash
# Initialize git and push to GitHub
git init
git add .
git commit -m "Initial commit"
git remote add origin <your-repo-url>
git push -u origin main

# Configure GitHub Pages
# Settings -> Pages -> Source: /docs folder
```

## Report Sections

1. **The Investment Problem** - Solar price collapse and curtailment analysis
2. **The BESS Integration Thesis** - Conceptual framework for co-location decisions
3. **The Trade-Off Analysis** - BESS growth trends, co-location mapping, revenue analysis
4. **The Technical Constraints** - MLF impacts, revenue concentration analysis
5. **The Strategic Framework** - Decision tree for investment evaluation

## Style Guide

**Colors:**
- Solar PV: `#FFD700` (yellow)
- Wind: `#2E7D32` (green)
- Battery: `#7B1FA2` (purple)
- Battery Co-located: `#FF6F00` (dark orange)
- Accent: `#00ACC1` (teal)

**Typography:**
- Font: Lato (sans-serif)
- Consistent Plotly theming via `scripts/utils/style_config.py`

## Data Sources

- **NEMOSIS:** Historical NEM market data (AEMO)
- **OpenElectricity API:** Current generator metadata
- **PyPSA:** Energy system modeling
- **NEM Generation Information:** AEMO generator registry

## Key Features

- Interactive Plotly visualizations
- Folium maps for geospatial analysis
- Reproducible analysis (all Python scripts included)
- Quarto-based static site generation
- GitHub Pages deployment

## Development

### Code Organization

Each analysis is a standalone Python script that:
1. Loads cached NEMOSIS data
2. Processes data using shared utilities
3. Generates interactive visualization
4. Saves output to `data/outputs/`

Scripts can be run independently or executed via Quarto during rendering.

### Utilities

- `style_config.py`: Plotly theming and color palette
- `nemosis_helpers.py`: NEMOSIS data loading and processing
- `data_paths.py`: Centralized path management

### Skills

Claude Code skills are provided in `skills/` for NEMOSIS and PyPSA:
- `NEMOSIS_skill.md`: NEM data access patterns
- `PyPSA_skill.md`: Power system modeling

## Contributing

This is a research project for infrastructure investment analysis. For questions or collaboration inquiries, please open an issue.

## License

All code is provided for research and educational purposes.

## Acknowledgments

- **NEMOSIS:** UNSW CEEM for NEM data access library
- **OpenElectricity:** Dylan McConnell for generator metadata API
- **PyPSA:** PyPSA developers for power system modeling framework
- **AEMO:** Australian Energy Market Operator for NEM data
