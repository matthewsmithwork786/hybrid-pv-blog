"""
PyPSA Model for BESS Deployment Analysis
=========================================

This package provides dispatch optimization for comparing standalone vs. co-located
battery storage configurations in the Australian NEM.

Modules:
--------
- network: PyPSA network setup and component definitions
- scenarios: Scenario configuration (standalone, AC-coupled, DC-coupled)
- timeseries: Price and solar capacity factor loading
- financials: CAPEX, OPEX, and IRR calculations
- run_scenarios: Main execution script

LOCAL AGENT INSTRUCTIONS:
-------------------------
1. Ensure PyPSA is installed: pip install pypsa highspy
2. Run scenarios: python scripts/section5/pypsa_model/run_scenarios.py
3. Outputs saved to: data/outputs/section5/

TROUBLESHOOTING:
- If HiGHS solver fails: pip install highspy
- If memory errors: Reduce time resolution (see run_scenarios.py)
- If price data missing: Script uses synthetic data fallback
"""

from pathlib import Path

# Package version
__version__ = "1.0.0"

# Module root
MODULE_ROOT = Path(__file__).parent

# Default parameters
DEFAULT_PARAMS = {
    "battery_mw": 100,
    "battery_hours": 4,
    "solar_mw": 200,
    "region": "NSW1",
    "year": 2025,
    "ppa_price": 70,  # $/MWh
    "ppa_load_mw": 50,
}
