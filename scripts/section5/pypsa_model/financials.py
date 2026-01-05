"""
Financial Calculations
======================

CAPEX, OPEX, revenue, and IRR calculations for scenario comparison.

LOCAL AGENT NOTES:
------------------
- IRR uses numpy_financial if available, fallback to scipy
- Revenue comes from dispatch optimization results
- CAPEX/OPEX based on industry benchmarks
"""

import numpy as np
import pandas as pd
from typing import Dict, Any, Optional, Tuple
from dataclasses import dataclass

# Try numpy_financial, fall back to scipy
try:
    from numpy_financial import irr, npv
    NPF_AVAILABLE = True
except ImportError:
    try:
        from scipy.optimize import brentq

        def irr(cashflows):
            """Simple IRR calculation using scipy."""
            def npv_func(rate):
                return sum(cf / (1 + rate) ** i for i, cf in enumerate(cashflows))

            try:
                return brentq(npv_func, -0.99, 10.0)
            except ValueError:
                return np.nan

        def npv(rate, cashflows):
            """Simple NPV calculation."""
            return sum(cf / (1 + rate) ** i for i, cf in enumerate(cashflows))

        NPF_AVAILABLE = True
    except ImportError:
        NPF_AVAILABLE = False


@dataclass
class FinancialParams:
    """Financial modeling parameters."""

    # Project timeline
    project_life_years: int = 15
    construction_months: int = 18

    # Financing
    debt_ratio: float = 0.70  # 70% debt
    interest_rate: float = 0.065  # 6.5%
    debt_term_years: int = 15

    # Operating costs (% of CAPEX annually)
    opex_battery_pct: float = 0.015  # 1.5% of battery CAPEX
    opex_solar_pct: float = 0.010  # 1.0% of solar CAPEX
    insurance_pct: float = 0.005  # 0.5% of total CAPEX

    # Degradation
    battery_degradation_annual: float = 0.02  # 2% per year
    solar_degradation_annual: float = 0.005  # 0.5% per year

    # Other
    inflation: float = 0.025  # 2.5%
    discount_rate: float = 0.08  # 8% for NPV
    tax_rate: float = 0.30  # 30% corporate tax


def calculate_annual_opex(
    scenario,
    params: Optional[FinancialParams] = None,
    year: int = 1,
) -> float:
    """
    Calculate annual operating expenses.

    Parameters:
    -----------
    scenario : Scenario
        Project scenario configuration
    params : FinancialParams
        Financial parameters
    year : int
        Year of operation (for inflation adjustment)

    Returns:
    --------
    float
        Annual OPEX in $
    """
    if params is None:
        params = FinancialParams()

    # Base OPEX
    battery_capex = scenario.battery_mw * 1000 * scenario.capex_battery
    battery_opex = battery_capex * params.opex_battery_pct

    if scenario.solar_mw:
        solar_capex = scenario.solar_mw * 1000 * scenario.capex_solar
        solar_opex = solar_capex * params.opex_solar_pct
    else:
        solar_opex = 0

    insurance = scenario.total_capex * params.insurance_pct

    # Inflation adjustment
    inflation_factor = (1 + params.inflation) ** (year - 1)

    total_opex = (battery_opex + solar_opex + insurance) * inflation_factor

    return total_opex


def calculate_degraded_capacity(
    initial_capacity: float,
    year: int,
    degradation_rate: float,
) -> float:
    """Calculate capacity after degradation."""
    return initial_capacity * (1 - degradation_rate) ** (year - 1)


def calculate_annual_revenue(
    dispatch_results: pd.DataFrame,
    scenario,
    year: int = 1,
    params: Optional[FinancialParams] = None,
) -> Dict[str, float]:
    """
    Calculate annual revenue from dispatch results.

    Parameters:
    -----------
    dispatch_results : pd.DataFrame
        Results from PyPSA optimization with columns:
        - price: wholesale price $/MWh
        - discharge: battery discharge MWh
        - solar_gen: solar generation MWh (if applicable)
        - fcas_revenue: FCAS revenue $ (if calculated)

    scenario : Scenario
        Project configuration

    year : int
        Year of operation (for degradation)

    Returns:
    --------
    dict
        Revenue breakdown by source
    """
    if params is None:
        params = FinancialParams()

    # Degradation factor for battery
    batt_degradation = (1 - params.battery_degradation_annual) ** (year - 1)

    revenues = {}

    # Arbitrage revenue: discharge * price * MLF * degradation
    if "discharge" in dispatch_results.columns:
        arbitrage = (
            dispatch_results["discharge"]
            * dispatch_results["price"]
            * scenario.mlf
            * batt_degradation
        ).sum()
        revenues["arbitrage"] = arbitrage

    # Charging cost (negative revenue)
    if "charge" in dispatch_results.columns:
        charge_cost = (
            dispatch_results["charge"]
            * dispatch_results["price"]
            * scenario.mlf
        ).sum()
        revenues["charge_cost"] = -charge_cost

    # Solar revenue (if applicable)
    if scenario.solar_mw and "solar_gen" in dispatch_results.columns:
        solar_degradation = (1 - params.solar_degradation_annual) ** (year - 1)
        solar_rev = (
            dispatch_results["solar_gen"]
            * dispatch_results["price"]
            * scenario.mlf
            * solar_degradation
        ).sum()
        revenues["solar"] = solar_rev

    # FCAS revenue (simplified - actual would come from co-optimization)
    if scenario.fcas_enabled:
        # Rough estimate: 10% of arbitrage revenue
        fcas_estimate = revenues.get("arbitrage", 0) * 0.10
        revenues["fcas"] = fcas_estimate

    # PPA revenue (if applicable)
    if scenario.ppa_enabled and scenario.ppa_price and scenario.ppa_load_mw:
        # Annual PPA revenue for contracted volume
        ppa_hours = 8760 * 0.3  # Assume 30% capacity factor for PPA delivery
        ppa_revenue = scenario.ppa_load_mw * ppa_hours * scenario.ppa_price
        revenues["ppa"] = ppa_revenue

    revenues["total"] = sum(revenues.values())

    return revenues


def calculate_project_cashflows(
    scenario,
    annual_revenues: list,
    params: Optional[FinancialParams] = None,
) -> pd.DataFrame:
    """
    Calculate project cash flows over life.

    Parameters:
    -----------
    scenario : Scenario
        Project configuration
    annual_revenues : list
        Revenue for each year of operation
    params : FinancialParams
        Financial parameters

    Returns:
    --------
    pd.DataFrame
        Year-by-year cash flows
    """
    if params is None:
        params = FinancialParams()

    years = range(params.project_life_years + 1)
    cashflows = []

    for year in years:
        if year == 0:
            # Year 0: Construction capital outflow
            cf = {
                "year": 0,
                "capex": -scenario.total_capex,
                "revenue": 0,
                "opex": 0,
                "ebitda": 0,
                "net_cashflow": -scenario.total_capex,
            }
        else:
            # Operating years
            revenue = annual_revenues[year - 1] if year <= len(annual_revenues) else annual_revenues[-1]
            opex = calculate_annual_opex(scenario, params, year)
            ebitda = revenue - opex

            cf = {
                "year": year,
                "capex": 0,
                "revenue": revenue,
                "opex": -opex,
                "ebitda": ebitda,
                "net_cashflow": ebitda,
            }

        cashflows.append(cf)

    return pd.DataFrame(cashflows)


def calculate_irr(
    cashflows: pd.DataFrame,
) -> float:
    """
    Calculate unlevered project IRR.

    Parameters:
    -----------
    cashflows : pd.DataFrame
        Must contain 'net_cashflow' column

    Returns:
    --------
    float
        IRR as decimal (0.10 = 10%)
    """
    if not NPF_AVAILABLE:
        print("Warning: numpy_financial not available, returning NaN")
        return np.nan

    cf_values = cashflows["net_cashflow"].values
    return irr(cf_values)


def calculate_npv(
    cashflows: pd.DataFrame,
    discount_rate: float = 0.08,
) -> float:
    """
    Calculate net present value.

    Parameters:
    -----------
    cashflows : pd.DataFrame
        Must contain 'net_cashflow' column
    discount_rate : float
        Discount rate (default 8%)

    Returns:
    --------
    float
        NPV in $
    """
    if not NPF_AVAILABLE:
        print("Warning: numpy_financial not available, returning NaN")
        return np.nan

    cf_values = cashflows["net_cashflow"].values
    return npv(discount_rate, cf_values)


def calculate_payback_period(
    cashflows: pd.DataFrame,
) -> float:
    """
    Calculate simple payback period.

    Returns:
    --------
    float
        Years to payback (can be fractional)
    """
    cumulative = cashflows["net_cashflow"].cumsum()

    # Find first year where cumulative becomes positive
    positive_years = cumulative[cumulative > 0]

    if len(positive_years) == 0:
        return np.inf  # Never pays back

    payback_year = positive_years.index[0]

    # Interpolate for fractional year
    if payback_year > 0:
        prev_cumulative = cumulative.iloc[payback_year - 1]
        year_cashflow = cashflows["net_cashflow"].iloc[payback_year]
        fraction = -prev_cumulative / year_cashflow
        return payback_year - 1 + fraction

    return payback_year


def calculate_lcoe(
    scenario,
    annual_generation_mwh: float,
    params: Optional[FinancialParams] = None,
) -> float:
    """
    Calculate levelized cost of energy/storage.

    Parameters:
    -----------
    scenario : Scenario
        Project configuration
    annual_generation_mwh : float
        Annual energy throughput
    params : FinancialParams
        Financial parameters

    Returns:
    --------
    float
        LCOE in $/MWh
    """
    if params is None:
        params = FinancialParams()

    # Total lifecycle costs
    total_opex = sum(
        calculate_annual_opex(scenario, params, year)
        for year in range(1, params.project_life_years + 1)
    )
    total_cost = scenario.total_capex + total_opex

    # Total lifecycle generation (with degradation)
    total_gen = sum(
        annual_generation_mwh * (1 - params.battery_degradation_annual) ** (year - 1)
        for year in range(1, params.project_life_years + 1)
    )

    if total_gen == 0:
        return np.inf

    return total_cost / total_gen


def scenario_financial_summary(
    scenario,
    annual_revenues: list,
    params: Optional[FinancialParams] = None,
) -> Dict[str, Any]:
    """
    Generate complete financial summary for a scenario.

    Parameters:
    -----------
    scenario : Scenario
        Project configuration
    annual_revenues : list
        Annual revenue estimates
    params : FinancialParams
        Financial parameters

    Returns:
    --------
    dict
        Complete financial metrics
    """
    if params is None:
        params = FinancialParams()

    cashflows = calculate_project_cashflows(scenario, annual_revenues, params)

    return {
        "scenario_name": scenario.name,
        "total_capex_m": scenario.total_capex / 1e6,
        "year_1_revenue_m": annual_revenues[0] / 1e6 if annual_revenues else 0,
        "year_1_opex_m": calculate_annual_opex(scenario, params, 1) / 1e6,
        "project_irr": calculate_irr(cashflows),
        "project_npv_m": calculate_npv(cashflows, params.discount_rate) / 1e6,
        "payback_years": calculate_payback_period(cashflows),
        "mlf": scenario.mlf,
        "grid_charging": scenario.grid_charging,
        "fcas_enabled": scenario.fcas_enabled,
    }


if __name__ == "__main__":
    # Quick test
    from scenarios import create_all_scenarios

    scenarios = create_all_scenarios()

    print("Financial Summary Test")
    print("=" * 60)

    for key, scenario in scenarios.items():
        # Assume $10M annual revenue for testing
        annual_revenues = [10_000_000] * 15

        summary = scenario_financial_summary(scenario, annual_revenues)

        print(f"\n{summary['scenario_name']}")
        print("-" * 40)
        print(f"  CAPEX: ${summary['total_capex_m']:.1f}M")
        print(f"  Year 1 Revenue: ${summary['year_1_revenue_m']:.1f}M")
        print(f"  Year 1 OPEX: ${summary['year_1_opex_m']:.1f}M")
        print(f"  Project IRR: {summary['project_irr']*100:.1f}%")
        print(f"  Project NPV: ${summary['project_npv_m']:.1f}M")
        print(f"  Payback: {summary['payback_years']:.1f} years")
