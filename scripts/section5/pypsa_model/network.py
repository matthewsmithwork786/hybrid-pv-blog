"""
PyPSA Network Setup
===================

Creates the base network structure for BESS dispatch optimization.

Components:
- Bus: Single NSW bus representing grid connection point
- Generator: Solar PV (for co-located scenarios)
- StorageUnit: Battery energy storage
- Load: PPA obligation or merchant sell opportunity
- Generator (Shortfall): Penalty generator for unmet PPA

LOCAL AGENT NOTES:
------------------
- Network uses hourly resolution for annual simulation
- HiGHS solver is recommended (free, fast)
- Adjust max_hours for battery duration scenarios
"""

import pypsa
import pandas as pd
import numpy as np
from typing import Optional


def create_base_network(
    snapshots: pd.DatetimeIndex,
    battery_mw: float = 100,
    battery_hours: float = 4,
    solar_mw: Optional[float] = None,
    mlf: float = 0.95,
    region: str = "NSW1"
) -> pypsa.Network:
    """
    Create base PyPSA network for BESS analysis.

    Parameters:
    -----------
    snapshots : pd.DatetimeIndex
        Time periods for optimization
    battery_mw : float
        Battery power capacity (MW)
    battery_hours : float
        Battery duration (hours) - determines MWh capacity
    solar_mw : float, optional
        Solar PV capacity (MW) - if None, standalone battery
    mlf : float
        Marginal Loss Factor at connection point
    region : str
        NEM region identifier

    Returns:
    --------
    pypsa.Network
        Configured network ready for scenario-specific additions
    """
    # Initialize network
    network = pypsa.Network()
    network.set_snapshots(snapshots)

    # Store metadata
    network.region = region
    network.mlf = mlf

    # Add bus (connection point)
    network.add("Bus", "grid", carrier="electricity")

    # Add carriers for visualization
    network.add("Carrier", "electricity")
    network.add("Carrier", "solar", color="#FFD700")
    network.add("Carrier", "battery", color="#7B1FA2")

    # Add battery storage
    battery_mwh = battery_mw * battery_hours
    network.add(
        "StorageUnit",
        "battery",
        bus="grid",
        p_nom=battery_mw,
        max_hours=battery_hours,
        efficiency_store=0.92,  # Round-trip ~85%
        efficiency_dispatch=0.92,
        standing_loss=0.0001,  # 0.01% per hour self-discharge
        carrier="battery",
        marginal_cost=0.5,  # Degradation cost $/MWh cycling
        cyclic_state_of_charge=True,  # End year at starting SOC
    )

    # Add solar PV if co-located
    if solar_mw is not None and solar_mw > 0:
        network.add(
            "Generator",
            "solar_pv",
            bus="grid",
            p_nom=solar_mw,
            carrier="solar",
            marginal_cost=0,  # Zero marginal cost
            # p_max_pu will be set by timeseries
        )

    return network


def add_merchant_components(
    network: pypsa.Network,
    enable_grid_charging: bool = True
) -> pypsa.Network:
    """
    Add merchant market interaction components.

    Allows battery to buy/sell at market prices.

    Parameters:
    -----------
    network : pypsa.Network
        Base network
    enable_grid_charging : bool
        If True, battery can charge from grid (standalone mode)
        If False, battery can only charge from solar (DC-coupled)

    Returns:
    --------
    pypsa.Network
        Network with merchant components added
    """
    # Merchant sell (export to grid at market price)
    # This is modeled as a load with negative value (revenue)
    network.add(
        "Load",
        "merchant_sell",
        bus="grid",
        p_set=0,  # Variable - will be optimized
    )

    if enable_grid_charging:
        # Merchant buy (import from grid at market price)
        # This allows grid charging during low/negative prices
        network.add(
            "Generator",
            "grid_import",
            bus="grid",
            p_nom_extendable=True,
            p_nom_max=network.storage_units.p_nom["battery"],  # Limited to battery capacity
            carrier="electricity",
            marginal_cost=0,  # Will be set to market price
        )

    return network


def add_ppa_components(
    network: pypsa.Network,
    ppa_mw: float = 50,
    ppa_price: float = 70,
    shortfall_penalty: float = 150
) -> pypsa.Network:
    """
    Add PPA (Power Purchase Agreement) components.

    Models a fixed-volume delivery obligation with penalty for shortfall.

    Parameters:
    -----------
    network : pypsa.Network
        Base network
    ppa_mw : float
        Contracted delivery capacity (MW)
    ppa_price : float
        PPA price ($/MWh) - used for revenue calculation
    shortfall_penalty : float
        Penalty for unmet delivery ($/MWh)

    Returns:
    --------
    pypsa.Network
        Network with PPA components added
    """
    # PPA load (contracted delivery obligation)
    network.add(
        "Load",
        "ppa_delivery",
        bus="grid",
        p_set=ppa_mw,  # Fixed delivery requirement
    )

    # Shortfall generator (meets PPA when solar+battery insufficient)
    network.add(
        "Generator",
        "shortfall",
        bus="grid",
        p_nom_extendable=True,
        carrier="electricity",
        marginal_cost=shortfall_penalty,  # High cost discourages use
    )

    # Store PPA parameters for later revenue calculation
    network.ppa_price = ppa_price
    network.ppa_mw = ppa_mw

    return network


def configure_for_scenario(
    network: pypsa.Network,
    scenario: str,
    price_series: pd.Series,
    solar_cf_series: Optional[pd.Series] = None
) -> pypsa.Network:
    """
    Configure network for specific scenario.

    Parameters:
    -----------
    network : pypsa.Network
        Base network with components
    scenario : str
        One of: "standalone", "ac_coupled", "dc_coupled"
    price_series : pd.Series
        Wholesale prices ($/MWh) indexed by snapshots
    solar_cf_series : pd.Series, optional
        Solar capacity factors (0-1) indexed by snapshots

    Returns:
    --------
    pypsa.Network
        Configured network ready for optimization
    """
    # Ensure price series aligns with snapshots
    price_series = price_series.reindex(network.snapshots).fillna(50)

    # Set solar capacity factors if applicable
    if solar_cf_series is not None and "solar_pv" in network.generators.index:
        solar_cf = solar_cf_series.reindex(network.snapshots).fillna(0)
        network.generators_t.p_max_pu["solar_pv"] = solar_cf

    # Configure based on scenario
    if scenario == "standalone":
        # Full grid charging capability
        if "grid_import" in network.generators.index:
            # Cost to charge = market price (negative prices = get paid)
            network.generators_t.marginal_cost["grid_import"] = price_series

    elif scenario == "ac_coupled":
        # Grid charging available but at market price
        if "grid_import" in network.generators.index:
            network.generators_t.marginal_cost["grid_import"] = price_series

    elif scenario == "dc_coupled":
        # No grid charging - remove grid import if present
        if "grid_import" in network.generators.index:
            network.remove("Generator", "grid_import")

    else:
        raise ValueError(f"Unknown scenario: {scenario}")

    return network


def solve_network(
    network: pypsa.Network,
    solver_name: str = "highs"
) -> pypsa.Network:
    """
    Solve the network optimization.

    Parameters:
    -----------
    network : pypsa.Network
        Configured network
    solver_name : str
        Solver to use (highs recommended)

    Returns:
    --------
    pypsa.Network
        Solved network with results
    """
    print(f"  Solving with {solver_name}...")

    status = network.optimize(
        solver_name=solver_name,
        solver_options={"threads": 4}
    )

    if status[0] != "ok":
        print(f"  Warning: Solver status = {status}")

    return network


def extract_results(network: pypsa.Network, mlf: float = 1.0) -> dict:
    """
    Extract key results from solved network.

    Parameters:
    -----------
    network : pypsa.Network
        Solved network
    mlf : float
        MLF for revenue adjustment

    Returns:
    --------
    dict
        Results including dispatch, revenue, cycles, etc.
    """
    results = {}

    # Battery dispatch
    battery_p = network.storage_units_t.p["battery"]
    results["battery_discharge_mwh"] = battery_p.clip(lower=0).sum()
    results["battery_charge_mwh"] = (-battery_p.clip(upper=0)).sum()

    # Cycles per year
    battery_capacity_mwh = (
        network.storage_units.p_nom["battery"] *
        network.storage_units.max_hours["battery"]
    )
    results["cycles_per_year"] = results["battery_discharge_mwh"] / battery_capacity_mwh

    # Solar generation if present
    if "solar_pv" in network.generators.index:
        results["solar_generation_mwh"] = network.generators_t.p["solar_pv"].sum()
    else:
        results["solar_generation_mwh"] = 0

    # Grid import if available
    if "grid_import" in network.generators.index:
        results["grid_import_mwh"] = network.generators_t.p["grid_import"].sum()
    else:
        results["grid_import_mwh"] = 0

    # Shortfall if PPA present
    if "shortfall" in network.generators.index:
        results["shortfall_mwh"] = network.generators_t.p["shortfall"].sum()
    else:
        results["shortfall_mwh"] = 0

    # Revenue calculation (simplified)
    # In reality, need to track discharge at specific prices
    results["mlf"] = mlf

    return results
