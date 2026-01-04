# PyPSA Skill - Power System Analysis

## Overview

PyPSA (Python for Power System Analysis) is an open-source toolbox for simulating and optimizing modern power and energy systems. This skill covers patterns used in the Australian NEM modeling context.

## Key Concepts

### Network Components

PyPSA models power systems as networks with these core components:

| Component | Description | Key Parameters |
|-----------|-------------|----------------|
| **Bus** | Network node (connection point) | carrier (electricity, hydrogen, etc.) |
| **Generator** | Power generation unit | p_nom (capacity MW), p_max_pu (availability profile), marginal_cost |
| **Load** | Power demand | p_set (demand profile MWh/h) |
| **StorageUnit** | Battery/pumped hydro | p_nom (power MW), max_hours (duration), efficiency_store/dispatch |
| **Link** | Transmission/conversion | bus0, bus1, efficiency, p_nom |
| **Carrier** | Energy type definition | co2_emissions, color for visualization |

### Optimization Framework

PyPSA uses **linear programming** to minimize total system cost:

```
minimize: Σ(generation_cost + storage_cost + curtailment_penalty + ...)
subject to: energy balance, capacity limits, storage dynamics, custom constraints
```

**Solver:** HiGHS (open-source, fast, included with PyPSA)

## Basic Network Setup

### Create Network and Add Components

```python
import pypsa
import pandas as pd

# Initialize network
network = pypsa.Network()

# Add bus (connection point)
network.add("Bus", "NSW", carrier="electricity")

# Add solar PV generator with capacity factor profile
network.add("Generator", "PV_NSW",
    bus="NSW",
    p_nom=200,  # 200 MW capacity
    carrier="solar",
    p_max_pu=pv_profile,  # Hourly capacity factors (0-1)
    marginal_cost=0  # Zero marginal cost
)

# Add battery storage
network.add("StorageUnit", "Battery_NSW",
    bus="NSW",
    p_nom=100,  # 100 MW power capacity
    max_hours=4,  # 400 MWh energy capacity (4-hour duration)
    efficiency_store=0.95,  # 95% charging efficiency
    efficiency_dispatch=0.95,  # 95% discharging efficiency
    standing_loss=0.01,  # 1% hourly self-discharge
    marginal_cost=0.5  # Cycling degradation cost $/MWh
)

# Add fixed load
network.add("Load", "PPA_Load",
    bus="NSW",
    p_set=100  # Constant 100 MW demand
)

# Set time snapshots (hourly for full year)
network.set_snapshots(pd.date_range('2024-01-01', '2024-12-31 23:00', freq='H'))
```

### Running Optimization

```python
# Solve linear optimal power flow
network.optimize(solver_name='highs')

# Access results
generators_dispatch = network.generators_t.p  # Generator output (MW) by timestep
storage_dispatch = network.storage_units_t.p  # Storage power (MW), negative = charging
storage_soc = network.storage_units_t.state_of_charge  # Storage energy (MWh)
prices = network.buses_t.marginal_price  # Shadow prices ($/MWh)
```

## Custom Constraints

### Annual Capacity Factor Constraint

Limit shortfall generation to achieve minimum annual CUF:

```python
def constrain_annual_cuf(network, target_cuf=0.80):
    """
    Constrain annual capacity utilization factor.

    If target_cuf = 0.80, allow 20% shortfall from PPA load.
    """
    ppa_load_annual = network.loads_t.p_set["PPA_Load"].sum()
    max_shortfall = ppa_load_annual * (1 - target_cuf)

    # Add constraint: Shortfall_generator_annual <= max_shortfall
    network.model.add_constraints(
        network.generators_t.p["Shortfall_Generator"].sum() <= max_shortfall,
        name="AnnualCUF"
    )
```

### Merchant Buy Limit

Limit grid purchases as percentage of total generation:

```python
def constrain_merchant_buy(network, buy_limit_pct=0.20):
    """
    Limit merchant purchases to % of renewable generation.
    """
    re_gen_annual = (
        network.generators_t.p["PV_Gen"].sum() +
        network.storage_units_t.p["Battery"].clip(lower=0).sum()  # Discharge only
    )
    max_buy = re_gen_annual * buy_limit_pct

    network.model.add_constraints(
        network.loads_t.p["MerchantBuy_Load"].sum() <= max_buy,
        name="MerchantBuyLimit"
    )
```

## Common Modeling Patterns

### Merchant Arbitrage Model

```python
# Battery charges from grid at market price, discharges for revenue

# Add merchant sell generator (revenue from exports)
network.add("Generator", "MerchantSell",
    bus="NSW",
    p_nom_extendable=True,  # Unlimited capacity
    marginal_cost=0  # Revenue = market price (shadow price)
)

# Add merchant buy load (cost of imports)
network.add("Load", "MerchantBuy",
    bus="NSW",
    p_set=0  # Not fixed, will be optimized
)

# The optimizer will charge battery when prices are low, discharge when high
```

### PPA with Penalty Structure

```python
# Model a PPA with fixed delivery and penalty for shortfall

# Add PPA load (contracted demand)
network.add("Load", "PPA",
    bus="NSW",
    p_set=100  # 100 MW constant
)

# Add shortfall generator (meets PPA when RE insufficient)
network.add("Generator", "Shortfall",
    bus="NSW",
    p_nom_extendable=True,
    marginal_cost=150  # High penalty cost ($/MWh)
)

# Optimizer minimizes shortfall due to high cost
# Constraint can limit total annual shortfall (see Annual CUF above)
```

### Timeseries Profiles

```python
# Load hourly solar and price data
pv_profile = pd.read_feather('solar_cuf_2024.feather')  # Values 0-1
price_profile = pd.read_feather('nsw_prices_2024.feather')  # $/MWh

# Apply to generators
network.generators_t.p_max_pu["PV_NSW"] = pv_profile.values

# Market price affects optimization via marginal_cost on merchant generators
# High prices -> optimizer prefers to generate/discharge
# Low prices -> optimizer prefers to charge batteries
```

## Output Analysis

### Summary Statistics

```python
# Total generation by type
gen_by_tech = network.generators_t.p.sum()

# Battery cycles (annual)
battery_discharge_mwh = network.storage_units_t.p["Battery"].clip(lower=0).sum()
battery_capacity_mwh = network.storage_units.max_hours["Battery"] * network.storage_units.p_nom["Battery"]
cycles_per_year = battery_discharge_mwh / battery_capacity_mwh / 365

# Capacity factor
pv_cuf = network.generators_t.p["PV_NSW"].sum() / (network.generators.p_nom["PV_NSW"] * len(network.snapshots))

# Revenue (from shadow prices)
revenue = (network.generators_t.p["MerchantSell"] * network.buses_t.marginal_price["NSW"]).sum()
```

### Hourly Dispatch Visualization

```python
import plotly.graph_objects as go

# Create dispatch chart
fig = go.Figure()

# PV generation
fig.add_trace(go.Scatter(
    x=network.snapshots,
    y=network.generators_t.p["PV_NSW"],
    name="Solar PV",
    fill='tozeroy',
    line=dict(color='#FFD700')
))

# Battery (positive = discharge, negative = charge)
fig.add_trace(go.Scatter(
    x=network.snapshots,
    y=network.storage_units_t.p["Battery"],
    name="Battery",
    line=dict(color='#7B1FA2')
))

# Storage SOC on secondary axis
fig.add_trace(go.Scatter(
    x=network.snapshots,
    y=network.storage_units_t.state_of_charge["Battery"],
    name="Battery SOC",
    yaxis='y2',
    line=dict(color='#00ACC1', dash='dash')
))

fig.update_layout(
    yaxis=dict(title="Power (MW)"),
    yaxis2=dict(title="SOC (MWh)", overlaying='y', side='right')
)
fig.show()
```

## Configuration Patterns (Excel-based)

The reference PyPSA implementation uses Excel workbooks for scenario configuration:

### Excel Structure

| Sheet | Purpose |
|-------|---------|
| **control** | Model parameters (PPA tariff, penalty multiplier, annual CUF target) |
| **generators** | Generator definitions (ONSW, PV, merchant, penalties) |
| **storage** | Storage unit definitions (batteries, pumped hydro) |
| **load** | Load profiles |
| **buses** | Network nodes |
| **carriers** | Technology definitions |
| **scenarios** | Scenario selection and parameters |

### Loading from Excel

```python
import pandas as pd

# Load all sheets
xlsx_file = pd.ExcelFile('pypsa_config.xlsm')

# Load and filter by scenario
control = pd.read_excel(xlsx_file, 'control')
control = control[control['Scenario'] == 1]

# Extract parameters
ppa_tariff = control['ppa_tariff'].iloc[0]
annual_cuf = control['annual_cuf'].iloc[0]

# Load component definitions
generators = pd.read_excel(xlsx_file, 'generators')
generators = generators[generators['Scenario'] == 1]

# Add to network
for _, row in generators.iterrows():
    network.add("Generator", row['name'],
        bus=row['bus'],
        p_nom=row['p_nom'],
        carrier=row['carrier'],
        marginal_cost=row['marginal_cost']
    )
```

## Sensitivity Analysis

### Parametric Sweep

```python
from joblib import Parallel, delayed

def run_scenario(pv_mw, battery_mw, battery_hours):
    """Run single scenario and return results."""
    network = create_network(pv_mw, battery_mw, battery_hours)
    network.optimize(solver_name='highs')
    return extract_results(network)

# Grid search across capacity ranges
pv_range = range(80, 241, 20)  # 80-240 MW in 20 MW steps
battery_mw_range = range(0, 71, 10)  # 0-70 MW
battery_hours_range = [2, 4, 6]  # Duration options

# Run in parallel
results = Parallel(n_jobs=-1)(
    delayed(run_scenario)(pv, batt_mw, batt_hr)
    for pv in pv_range
    for batt_mw in battery_mw_range
    for batt_hr in battery_hours_range
)

# Convert to DataFrame for analysis
results_df = pd.DataFrame(results)
```

## Performance Tips

1. **Use HiGHS solver** - faster than Gurobi for most cases, free
2. **Reduce time resolution** - hourly instead of 5-min for exploratory runs
3. **Limit extendable capacities** - set reasonable `p_nom_max` to avoid unbounded solutions
4. **Remove leap days** from timeseries for consistency
5. **Parallel execution** - use joblib for multi-scenario analysis

## File Locations (Project-Specific)

Reference implementation: `C:\Users\matts\Documents\Aus research\Gen modelling\PyPSA`

Key files:
- `PyPSA_functions.py` - Helper functions (create_network, constrain_annual_CUF, output_stats)
- `PyPSA_config.py` - Parametric sensitivity runner
- `PyPSA_inputs_Aus.xlsm` - Excel configuration template
- `Chosen plant CUFs_18-24_60min.feather` - Solar/wind capacity factors
- `NSW QLD price data_2018-24_60min.feather` - Historical market prices

## References

- **PyPSA Documentation:** https://pypsa.readthedocs.io/
- **PyPSA GitHub:** https://github.com/PyPSA/PyPSA
- **HiGHS Solver:** https://highs.dev/
- **Examples:** https://pypsa.readthedocs.io/en/latest/examples-basic.html
