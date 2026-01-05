"""
Run Scenario Comparison
=======================

Main script to run all scenarios and generate comparison outputs.

LOCAL AGENT NOTES:
------------------
1. Activate hybridpv environment first
2. PyPSA must be installed: pip install pypsa
3. Run from project root: python scripts/section5/pypsa_model/run_scenarios.py
4. Outputs go to data/outputs/section5/

TROUBLESHOOTING:
- If PyPSA import fails: pip install pypsa
- If solver fails: install glpk (conda install -c conda-forge glpk)
- If NEMOSIS fails: uses synthetic data automatically
- Memory issues: reduce to 4-hourly snapshots (freq="4H")
"""

import sys
from pathlib import Path
import json
import pandas as pd
import numpy as np

# Add parent directories to path
sys.path.append(str(Path(__file__).parent.parent.parent))

from scenarios import create_all_scenarios, scenarios_comparison_table
from network import create_network_for_scenario
from timeseries import load_all_timeseries
from financials import (
    FinancialParams,
    calculate_annual_opex,
    scenario_financial_summary,
)

# Try importing plotting utilities
try:
    from utils.style_config import TEMPLATE, COLORS
    from utils.data_paths import OUTPUTS_DIR, ensure_output_dirs
    UTILS_AVAILABLE = True
except ImportError:
    UTILS_AVAILABLE = False
    OUTPUTS_DIR = Path(__file__).parent.parent.parent.parent / "data" / "outputs" / "section5"

# Check if PyPSA is available
try:
    import pypsa
    PYPSA_AVAILABLE = True
except ImportError:
    PYPSA_AVAILABLE = False
    print("Warning: PyPSA not installed. Install with: pip install pypsa")

# Check if Plotly is available
try:
    import plotly.graph_objects as go
    from plotly.subplots import make_subplots
    PLOTLY_AVAILABLE = True
except ImportError:
    PLOTLY_AVAILABLE = False


def run_dispatch_optimization(
    network,
    solver_name: str = "glpk",
) -> pd.DataFrame:
    """
    Run PyPSA dispatch optimization.

    Parameters:
    -----------
    network : pypsa.Network
        Configured PyPSA network
    solver_name : str
        Solver to use (glpk, gurobi, cplex)

    Returns:
    --------
    pd.DataFrame
        Dispatch results by timestamp
    """
    if not PYPSA_AVAILABLE:
        print("PyPSA not available - returning empty results")
        return pd.DataFrame()

    try:
        # Run linear optimal power flow
        status = network.optimize(solver_name=solver_name)

        if status[0] != "ok":
            print(f"Optimization failed: {status}")
            return pd.DataFrame()

        # Extract results
        results = pd.DataFrame(index=network.snapshots)

        # Generator dispatch
        for gen in network.generators.index:
            results[f"gen_{gen}"] = network.generators_t.p[gen]

        # Storage dispatch
        for store in network.storage_units.index:
            results[f"store_p_{store}"] = network.storage_units_t.p[store]
            results[f"store_soc_{store}"] = network.storage_units_t.state_of_charge[store]

        # Prices (from marginal cost at bus)
        if hasattr(network, "buses_t") and "marginal_price" in network.buses_t:
            results["price"] = network.buses_t.marginal_price.iloc[:, 0]

        return results

    except Exception as e:
        print(f"Optimization error: {e}")
        return pd.DataFrame()


def estimate_annual_revenue(
    dispatch_results: pd.DataFrame,
    prices: pd.Series,
    scenario,
) -> float:
    """
    Estimate annual revenue from dispatch results.

    Simplified calculation - actual would be more complex.
    """
    if dispatch_results.empty:
        # Fallback estimate based on typical revenue
        # Assumes ~$100/kW-yr for standalone, less for constrained
        base_revenue = scenario.battery_mw * 1000 * 100  # $100/kW

        if not scenario.grid_charging:
            base_revenue *= 0.7  # 30% reduction for DC-coupled

        base_revenue *= scenario.mlf / 0.98  # MLF adjustment

        return base_revenue

    # Calculate from dispatch
    revenue = 0

    # Battery discharge revenue
    store_cols = [c for c in dispatch_results.columns if c.startswith("store_p_")]
    for col in store_cols:
        discharge = dispatch_results[col].clip(lower=0)  # Positive = discharge
        revenue += (discharge * prices * scenario.mlf).sum()

        charge = (-dispatch_results[col]).clip(lower=0)  # Negative = charge
        revenue -= (charge * prices * scenario.mlf).sum()

    # Solar revenue
    solar_cols = [c for c in dispatch_results.columns if "solar" in col.lower()]
    for col in solar_cols:
        revenue += (dispatch_results[col] * prices * scenario.mlf).sum()

    return revenue


def create_comparison_chart(
    results: dict,
    output_path: Path,
) -> None:
    """
    Create comparison visualization.

    Parameters:
    -----------
    results : dict
        Scenario results with financial metrics
    output_path : Path
        Where to save the HTML chart
    """
    if not PLOTLY_AVAILABLE:
        print("Plotly not available - skipping chart generation")
        return

    # Prepare data
    scenarios_list = list(results.keys())
    irrs = [results[s]["project_irr"] * 100 for s in scenarios_list]
    capex = [results[s]["total_capex_m"] for s in scenarios_list]
    revenues = [results[s]["year_1_revenue_m"] for s in scenarios_list]

    # Color mapping
    if UTILS_AVAILABLE:
        colors = [
            COLORS["battery"],  # Standalone
            COLORS["battery_coloc"],  # AC-coupled
            COLORS["accent"],  # DC-coupled
        ]
    else:
        colors = ["#7B1FA2", "#FF6F00", "#00ACC1"]

    # Create subplots
    fig = make_subplots(
        rows=1, cols=3,
        subplot_titles=["Project IRR (%)", "Total CAPEX ($M)", "Year 1 Revenue ($M)"],
        horizontal_spacing=0.1,
    )

    # IRR bars
    fig.add_trace(
        go.Bar(
            x=scenarios_list,
            y=irrs,
            marker_color=colors,
            name="IRR",
            text=[f"{v:.1f}%" for v in irrs],
            textposition="outside",
        ),
        row=1, col=1,
    )

    # CAPEX bars
    fig.add_trace(
        go.Bar(
            x=scenarios_list,
            y=capex,
            marker_color=colors,
            name="CAPEX",
            text=[f"${v:.0f}M" for v in capex],
            textposition="outside",
        ),
        row=1, col=2,
    )

    # Revenue bars
    fig.add_trace(
        go.Bar(
            x=scenarios_list,
            y=revenues,
            marker_color=colors,
            name="Revenue",
            text=[f"${v:.1f}M" for v in revenues],
            textposition="outside",
        ),
        row=1, col=3,
    )

    # Update layout
    fig.update_layout(
        title=dict(
            text="Scenario Comparison: Standalone vs Co-located BESS",
            font=dict(size=18),
        ),
        showlegend=False,
        height=450,
        template=TEMPLATE if UTILS_AVAILABLE else "plotly_white",
        margin=dict(t=80, b=60),
    )

    # Update y-axes
    fig.update_yaxes(title_text="IRR (%)", row=1, col=1)
    fig.update_yaxes(title_text="CAPEX ($M)", row=1, col=2)
    fig.update_yaxes(title_text="Revenue ($M)", row=1, col=3)

    # Save
    fig.write_html(output_path, include_plotlyjs="cdn")
    print(f"Chart saved to: {output_path}")


def run_all_scenarios(
    battery_mw: float = 100.0,
    battery_hours: float = 4.0,
    solar_mw: float = 200.0,
    region: str = "NSW1",
    year: int = 2025,
    use_synthetic: bool = True,
) -> dict:
    """
    Run all scenarios and return comparison.

    Parameters:
    -----------
    battery_mw : float
        Battery power capacity
    battery_hours : float
        Battery duration
    solar_mw : float
        Solar capacity for co-located scenarios
    region : str
        NEM region
    year : int
        Analysis year
    use_synthetic : bool
        Use synthetic data (True) or try NEMOSIS (False)

    Returns:
    --------
    dict
        Results for each scenario
    """
    print("=" * 60)
    print("Running Scenario Comparison")
    print("=" * 60)

    # Create scenarios
    scenarios = create_all_scenarios(
        battery_mw=battery_mw,
        battery_hours=battery_hours,
        solar_mw=solar_mw,
        region=region,
    )

    print(f"\nScenarios created:")
    for key, scenario in scenarios.items():
        print(f"  - {scenario.name}: {scenario.battery_mw}MW/{scenario.battery_mwh}MWh")

    # Load time series data
    print("\nLoading time series data...")
    cache_path = None if use_synthetic else "path/to/nemosis/cache"
    snapshots, prices, solar_cf = load_all_timeseries(year, region, cache_path)

    # Run each scenario
    results = {}
    financial_params = FinancialParams()

    for key, scenario in scenarios.items():
        print(f"\n--- Running {scenario.name} ---")

        if PYPSA_AVAILABLE:
            # Create and configure network
            network = create_network_for_scenario(
                scenario=scenario,
                snapshots=snapshots,
                prices=prices,
                solar_cf=solar_cf,
            )

            # Run optimization
            dispatch_results = run_dispatch_optimization(network)
        else:
            dispatch_results = pd.DataFrame()

        # Estimate revenue
        annual_revenue = estimate_annual_revenue(dispatch_results, prices, scenario)
        print(f"  Estimated annual revenue: ${annual_revenue/1e6:.1f}M")

        # Generate annual revenue stream (with degradation)
        annual_revenues = [
            annual_revenue * (1 - financial_params.battery_degradation_annual) ** (y - 1)
            for y in range(1, financial_params.project_life_years + 1)
        ]

        # Calculate financial metrics
        summary = scenario_financial_summary(scenario, annual_revenues, financial_params)
        results[key] = summary

        print(f"  Project IRR: {summary['project_irr']*100:.1f}%")
        print(f"  Project NPV: ${summary['project_npv_m']:.1f}M")

    return results


def main():
    """Main entry point."""
    print("\n" + "=" * 60)
    print("PyPSA BESS Scenario Comparison")
    print("=" * 60)

    if not PYPSA_AVAILABLE:
        print("\nWARNING: PyPSA not installed!")
        print("Install with: pip install pypsa")
        print("Continuing with revenue estimates only...\n")

    # Ensure output directory exists
    output_dir = Path(OUTPUTS_DIR) if UTILS_AVAILABLE else Path(__file__).parent.parent.parent.parent / "data" / "outputs" / "section5"
    output_dir.mkdir(parents=True, exist_ok=True)

    # Run scenarios
    results = run_all_scenarios(
        battery_mw=100.0,
        battery_hours=4.0,
        solar_mw=200.0,
        region="NSW1",
        year=2025,
        use_synthetic=True,
    )

    # Print summary
    print("\n" + "=" * 60)
    print("SCENARIO COMPARISON SUMMARY")
    print("=" * 60)

    for key, summary in results.items():
        print(f"\n{summary['scenario_name'].upper()}")
        print("-" * 40)
        print(f"  Total CAPEX:       ${summary['total_capex_m']:.1f}M")
        print(f"  Year 1 Revenue:    ${summary['year_1_revenue_m']:.1f}M")
        print(f"  Year 1 OPEX:       ${summary['year_1_opex_m']:.2f}M")
        print(f"  Project IRR:       {summary['project_irr']*100:.1f}%")
        print(f"  Project NPV:       ${summary['project_npv_m']:.1f}M")
        print(f"  Payback Period:    {summary['payback_years']:.1f} years")
        print(f"  MLF:               {summary['mlf']:.2f}")
        print(f"  Grid Charging:     {'Yes' if summary['grid_charging'] else 'No'}")

    # Save results as JSON
    json_path = output_dir / "scenario_comparison.json"
    with open(json_path, "w") as f:
        json.dump(results, f, indent=2, default=str)
    print(f"\nResults saved to: {json_path}")

    # Create comparison chart
    chart_path = output_dir / "scenario_comparison.html"
    create_comparison_chart(results, chart_path)

    print("\n" + "=" * 60)
    print("Analysis complete!")
    print("=" * 60)

    return results


if __name__ == "__main__":
    main()
