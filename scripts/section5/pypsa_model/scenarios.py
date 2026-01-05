"""
Scenario Definitions
====================

Defines the three deployment scenarios for comparison:
1. Standalone BESS
2. AC-coupled (co-located with separate DUID)
3. DC-coupled (co-located behind-the-meter)

LOCAL AGENT NOTES:
------------------
- Each scenario has different constraints and revenue streams
- MLF values are critical - standalone gets better MLF
- DC-coupled cannot charge from grid
"""

from dataclasses import dataclass, field
from typing import Dict, Any, Optional
import pandas as pd


@dataclass
class Scenario:
    """Base scenario configuration."""

    name: str
    description: str

    # Battery parameters
    battery_mw: float = 100.0
    battery_hours: float = 4.0

    # Solar parameters (None for standalone)
    solar_mw: Optional[float] = None

    # Location parameters
    region: str = "NSW1"
    mlf: float = 0.95

    # Charging constraints
    grid_charging: bool = True  # Can charge from grid?
    max_grid_charge_rate: float = 1.0  # Fraction of battery MW

    # Revenue parameters
    fcas_enabled: bool = True
    arbitrage_enabled: bool = True
    ppa_enabled: bool = False
    ppa_price: Optional[float] = None  # $/MWh
    ppa_load_mw: Optional[float] = None

    # Cost parameters ($/kW)
    capex_battery: float = 800.0
    capex_solar: float = 1000.0
    capex_connection: float = 200.0  # Grid connection

    # Additional cost adjustments
    connection_synergy: float = 0.0  # Cost reduction for shared connection

    @property
    def battery_mwh(self) -> float:
        """Total battery energy capacity."""
        return self.battery_mw * self.battery_hours

    @property
    def total_capex(self) -> float:
        """Total project capital cost in $."""
        battery_cost = self.battery_mw * 1000 * self.capex_battery
        connection_cost = self.battery_mw * 1000 * (self.capex_connection - self.connection_synergy)

        if self.solar_mw:
            solar_cost = self.solar_mw * 1000 * self.capex_solar
        else:
            solar_cost = 0

        return battery_cost + solar_cost + connection_cost

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "name": self.name,
            "description": self.description,
            "battery_mw": self.battery_mw,
            "battery_hours": self.battery_hours,
            "battery_mwh": self.battery_mwh,
            "solar_mw": self.solar_mw,
            "region": self.region,
            "mlf": self.mlf,
            "grid_charging": self.grid_charging,
            "fcas_enabled": self.fcas_enabled,
            "ppa_enabled": self.ppa_enabled,
            "total_capex": self.total_capex,
        }


def create_standalone_scenario(
    battery_mw: float = 100.0,
    battery_hours: float = 4.0,
    region: str = "NSW1",
) -> Scenario:
    """
    Create standalone BESS scenario.

    Key characteristics:
    - Optimal location (high MLF ~0.98)
    - Full grid charging flexibility
    - Full FCAS participation
    - Higher connection costs (no sharing)
    """
    return Scenario(
        name="Standalone BESS",
        description="Grid-scale battery at optimal location",
        battery_mw=battery_mw,
        battery_hours=battery_hours,
        solar_mw=None,
        region=region,
        mlf=0.98,  # Optimal location
        grid_charging=True,
        max_grid_charge_rate=1.0,
        fcas_enabled=True,
        arbitrage_enabled=True,
        ppa_enabled=False,
        capex_battery=800.0,
        capex_connection=200.0,
        connection_synergy=0.0,
    )


def create_ac_coupled_scenario(
    battery_mw: float = 100.0,
    battery_hours: float = 4.0,
    solar_mw: float = 200.0,
    region: str = "NSW1",
    ppa_price: Optional[float] = None,
    ppa_load_mw: Optional[float] = None,
) -> Scenario:
    """
    Create AC-coupled co-located scenario.

    Key characteristics:
    - Location constrained by solar site (lower MLF ~0.90)
    - Grid charging allowed (separate DUID)
    - Shared connection infrastructure ($75/kW saving)
    - Can participate in FCAS
    - Eligible for CIS and green PPAs
    """
    scenario = Scenario(
        name="AC-Coupled",
        description="Co-located with solar, separate DUID",
        battery_mw=battery_mw,
        battery_hours=battery_hours,
        solar_mw=solar_mw,
        region=region,
        mlf=0.90,  # Constrained by solar site
        grid_charging=True,
        max_grid_charge_rate=1.0,
        fcas_enabled=True,
        arbitrage_enabled=True,
        capex_battery=800.0,
        capex_solar=1000.0,
        capex_connection=200.0,
        connection_synergy=75.0,  # Shared infrastructure
    )

    if ppa_price is not None:
        scenario.ppa_enabled = True
        scenario.ppa_price = ppa_price
        scenario.ppa_load_mw = ppa_load_mw or battery_mw * 0.5

    return scenario


def create_dc_coupled_scenario(
    battery_mw: float = 100.0,
    battery_hours: float = 4.0,
    solar_mw: float = 200.0,
    region: str = "NSW1",
    ppa_price: Optional[float] = None,
    ppa_load_mw: Optional[float] = None,
) -> Scenario:
    """
    Create DC-coupled co-located scenario.

    Key characteristics:
    - Location constrained by solar site (lower MLF ~0.88)
    - NO grid charging (behind-the-meter)
    - Maximum infrastructure sharing ($100/kW saving)
    - Limited FCAS participation
    - "Green battery" - only solar-charged
    - Strong CIS and ESG positioning
    """
    scenario = Scenario(
        name="DC-Coupled",
        description="Co-located behind-the-meter, single DUID",
        battery_mw=battery_mw,
        battery_hours=battery_hours,
        solar_mw=solar_mw,
        region=region,
        mlf=0.88,  # Same poor location as AC but slightly worse due to losses
        grid_charging=False,  # Cannot charge from grid
        max_grid_charge_rate=0.0,
        fcas_enabled=False,  # Limited FCAS capability
        arbitrage_enabled=True,
        capex_battery=800.0,
        capex_solar=1000.0,
        capex_connection=200.0,
        connection_synergy=100.0,  # Maximum sharing benefit
    )

    if ppa_price is not None:
        scenario.ppa_enabled = True
        scenario.ppa_price = ppa_price
        scenario.ppa_load_mw = ppa_load_mw or battery_mw * 0.5

    return scenario


def create_all_scenarios(
    battery_mw: float = 100.0,
    battery_hours: float = 4.0,
    solar_mw: float = 200.0,
    region: str = "NSW1",
) -> Dict[str, Scenario]:
    """
    Create all three scenarios for comparison.

    Returns dictionary mapping scenario names to Scenario objects.
    """
    return {
        "standalone": create_standalone_scenario(
            battery_mw=battery_mw,
            battery_hours=battery_hours,
            region=region,
        ),
        "ac_coupled": create_ac_coupled_scenario(
            battery_mw=battery_mw,
            battery_hours=battery_hours,
            solar_mw=solar_mw,
            region=region,
        ),
        "dc_coupled": create_dc_coupled_scenario(
            battery_mw=battery_mw,
            battery_hours=battery_hours,
            solar_mw=solar_mw,
            region=region,
        ),
    }


def scenarios_comparison_table(scenarios: Dict[str, Scenario]) -> pd.DataFrame:
    """
    Create comparison DataFrame for all scenarios.

    Useful for displaying side-by-side comparison in reports.
    """
    data = []
    for key, scenario in scenarios.items():
        row = scenario.to_dict()
        row["key"] = key
        data.append(row)

    df = pd.DataFrame(data)
    df = df.set_index("key")

    return df


if __name__ == "__main__":
    # Quick test of scenario creation
    scenarios = create_all_scenarios()

    print("Scenario Comparison:")
    print("=" * 60)

    for key, scenario in scenarios.items():
        print(f"\n{scenario.name}")
        print("-" * 40)
        print(f"  Battery: {scenario.battery_mw} MW / {scenario.battery_mwh} MWh")
        print(f"  Solar: {scenario.solar_mw} MW" if scenario.solar_mw else "  Solar: None")
        print(f"  MLF: {scenario.mlf}")
        print(f"  Grid charging: {scenario.grid_charging}")
        print(f"  FCAS enabled: {scenario.fcas_enabled}")
        print(f"  Total CAPEX: ${scenario.total_capex/1e6:.1f}M")
