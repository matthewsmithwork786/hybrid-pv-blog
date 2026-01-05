"""
Section 1 Analysis: Solar Price Collapse and Curtailment

Generates dual-axis chart showing:
- Primary axis: Average annual wholesale price during solar hours (10:00-16:00 NSW)
- Secondary axis: Annual solar curtailment percentage

Period: 2018-2025

Output: data/outputs/section1/solar_price_curtailment.html
"""

import sys
from pathlib import Path
import polars as pl
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# Add utils to path
sys.path.append(str(Path(__file__).parent.parent / "utils"))

from style_config import COLORS, get_color, format_currency, format_percentage, FONT_CONFIG
from data_paths import get_output_path, NEMOSIS_DATA_ROOT
from nemosis_helpers import (
    load_cached_dispatchprice,
    load_cached_dispatchload,
    get_solar_duids,
    calculate_curtailment,
    filter_solar_hours
)

print("=" * 80)
print("Section 1: Solar Price Collapse and Curtailment Analysis")
print("=" * 80)

# Date range - 2024 data available from August onwards
START_DATE = "2024-08-01"
END_DATE = "2024-12-31"

print(f"\nAnalyzing data from {START_DATE} to {END_DATE}")
print(f"Region: NSW1")
print(f"Solar hours: 10:00-16:00")

# ============================================================================
# PART 1: Solar Hour Prices
# ============================================================================

print("\n" + "-" * 80)
print("Loading price data...")

try:
    prices = load_cached_dispatchprice(START_DATE, END_DATE, region='NSW1')
    print(f"[OK] Loaded {len(prices):,} price records")
except FileNotFoundError as e:
    print(f"\n[ERROR] {e}")
    print("\nPlease run data download scripts first:")
    print("  python scripts/download/download_dispatchprice.py")
    sys.exit(1)

# Filter for solar hours (10:00-16:00)
print("Filtering for solar hours (10:00-16:00)...")
solar_prices = filter_solar_hours(prices, start_hour=10, end_hour=16)
print(f"[OK] Filtered to {len(solar_prices):,} solar hour records")

# Calculate annual average price
print("Calculating annual average prices...")
solar_prices = solar_prices.with_columns(
    pl.col("SETTLEMENTDATE").dt.year().alias("year")
)

annual_prices = (
    solar_prices
    .group_by("year")
    .agg(pl.mean("RRP").alias("avg_price"))
    .sort("year")
)

print("\nAnnual average solar hour prices (10:00-16:00 NSW):")
for row in annual_prices.iter_rows(named=True):
    print(f"  {row['year']}: ${row['avg_price']:.2f}/MWh")

# ============================================================================
# PART 2: Solar Curtailment
# ============================================================================

print("\n" + "-" * 80)
print("Loading curtailment data...")

# Get solar DUIDs
print("Fetching solar generator DUIDs from OpenElectricity API...")
try:
    solar_duids = get_solar_duids(region='NSW1')
    print(f"[OK] Found {len(solar_duids)} solar generators in NSW")
except Exception as e:
    print(f"\n[ERROR] Error fetching solar DUIDs: {e}")
    print("\nPlease run:")
    print("  python scripts/download/download_generator_metadata.py")
    sys.exit(1)

# Load dispatch load data
print(f"Loading DISPATCHLOAD for {len(solar_duids)} solar generators...")
try:
    dispatch = load_cached_dispatchload(START_DATE, END_DATE, duids=solar_duids)
    print(f"[OK] Loaded {len(dispatch):,} dispatch records")
except FileNotFoundError as e:
    print(f"\n[ERROR] {e}")
    print("\nPlease run:")
    print("  python scripts/download/download_dispatchload.py")
    sys.exit(1)

# Calculate curtailment
print("Calculating curtailment...")
dispatch = calculate_curtailment(dispatch)

# Add year column
dispatch = dispatch.with_columns(
    pl.col("SETTLEMENTDATE").dt.year().alias("year")
)

# Annual curtailment aggregation
annual_curtailment = (
    dispatch
    .group_by("year")
    .agg([
        pl.sum("curtailment_MW").alias("total_curtailment_mwh"),
        pl.sum("AVAILABILITY").alias("total_availability_mwh")
    ])
    .with_columns(
        (pl.col("total_curtailment_mwh") / pl.col("total_availability_mwh") * 100)
        .alias("curtailment_pct")
    )
    .sort("year")
)

print("\nAnnual solar curtailment (NSW):")
for row in annual_curtailment.iter_rows(named=True):
    print(f"  {int(row['year'])}: {row['curtailment_pct']:.2f}%")

# ============================================================================
# PART 3: Visualization
# ============================================================================

print("\n" + "-" * 80)
print("Creating visualization...")

# Create figure with secondary y-axis
fig = make_subplots(specs=[[{"secondary_y": True}]])

# Add price bars (primary axis)
fig.add_trace(
    go.Bar(
        x=annual_prices["year"].to_list(),
        y=annual_prices["avg_price"].to_list(),
        name="Solar Hour Price",
        marker_color=COLORS['pv'],
        hovertemplate="<b>%{x}</b><br>" +
                      "Price: $%{y:.2f}/MWh<br>" +
                      "<extra></extra>"
    ),
    secondary_y=False
)

# Add curtailment line (secondary axis)
fig.add_trace(
    go.Scatter(
        x=annual_curtailment["year"].to_list(),
        y=annual_curtailment["curtailment_pct"].to_list(),
        name="Curtailment",
        mode='lines+markers',
        line=dict(color=COLORS['negative'], width=3),
        marker=dict(size=8),
        hovertemplate="<b>%{x}</b><br>" +
                      "Curtailment: %{y:.2f}%<br>" +
                      "<extra></extra>"
    ),
    secondary_y=True
)

# Update layout
fig.update_layout(
    title=dict(
        text="The Collapse of Solar Economics in NSW<br>" +
             "<sub>Solar hour prices (10:00-16:00) and curtailment trends, 2018-2025</sub>",
        font=dict(size=20, family="Lato")
    ),
    xaxis=dict(
        title="Year",
        tickmode='linear',
        tick0=2018,
        dtick=1
    ),
    yaxis=dict(
        title="Average Price ($/MWh)",
        range=[0, max(annual_prices["avg_price"].to_list()) * 1.2]
    ),
    yaxis2=dict(
        title="Curtailment (%)",
        range=[0, max(annual_curtailment["curtailment_pct"].to_list()) * 1.5]
    ),
    hovermode='x unified',
    showlegend=True,
    legend=dict(
        orientation="h",
        yanchor="bottom",
        y=1.02,
        xanchor="right",
        x=1
    ),
    font=FONT_CONFIG,
    plot_bgcolor='white',
    paper_bgcolor='white'
)

# Save output
output_file = get_output_path("section1", "solar_price_curtailment.html")
fig.write_html(str(output_file))

print(f"\n[OK] Visualization saved to: {output_file}")
print(f"  File size: {output_file.stat().st_size / 1024:.1f} KB")

# Also save as JSON for Quarto embedding
json_file = get_output_path("section1", "solar_price_curtailment.json")
fig.write_json(str(json_file))
print(f"[OK] JSON data saved to: {json_file}")

# ============================================================================
# Summary Statistics
# ============================================================================

print("\n" + "=" * 80)
print("SUMMARY")
print("=" * 80)

# Price decline
price_2018 = annual_prices.filter(pl.col("year") == 2018)["avg_price"][0]
price_2025 = annual_prices.filter(pl.col("year") == 2025)["avg_price"][0]
price_decline_pct = (price_2018 - price_2025) / price_2018 * 100

print(f"\nSolar Hour Price Decline:")
print(f"  2018: ${price_2018:.2f}/MWh")
print(f"  2025: ${price_2025:.2f}/MWh")
print(f"  Decline: {price_decline_pct:.1f}%")

# Curtailment increase
curt_2018 = annual_curtailment.filter(pl.col("year") == 2018)["curtailment_pct"][0]
curt_2025 = annual_curtailment.filter(pl.col("year") == 2025)["curtailment_pct"][0]

print(f"\nCurtailment Increase:")
print(f"  2018: {curt_2018:.2f}%")
print(f"  2025: {curt_2025:.2f}%")
print(f"  Increase: {curt_2025 - curt_2018:.2f} percentage points")

print("\nKey Insights:")
print(f"  • Solar hour prices collapsed {price_decline_pct:.0f}% in 7 years")
print(f"  • Curtailment increased {curt_2025/curt_2018:.1f}x from 2018 to 2025")
print(f"  • 2025 solar is curtailed {curt_2025:.1f}% of the time in NSW")

print("\n" + "=" * 80)
print("Analysis complete!")
print("=" * 80)
