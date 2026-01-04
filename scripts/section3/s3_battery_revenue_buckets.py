"""
Section 3 Analysis: Battery Revenue by Price Bucket

Generates column chart showing percentage of battery revenue by price bucket.
Demonstrates how battery revenue concentrates in negative pricing and high-price events.

Filters: NSW batteries operational full year 2025
Revenue: Net revenue = (discharge revenue) - (charging cost)

Output: data/outputs/section3/battery_revenue_buckets.html
"""

import sys
from pathlib import Path
import polars as pl
import pandas as pd
import plotly.graph_objects as go

# Add utils to path
sys.path.append(str(Path(__file__).parent.parent / "utils"))

from style_config import COLORS, FONT_CONFIG
from data_paths import get_output_path
from nemosis_helpers import (
    load_cached_dispatch_scada,
    load_cached_dispatchprice,
    get_openelectricity_facilities
)

print("=" * 80)
print("Section 3: Battery Revenue by Price Bucket Analysis")
print("=" * 80)

# Analysis period
ANALYSIS_YEAR = 2025
START_DATE = f"{ANALYSIS_YEAR}-01-01"
END_DATE = f"{ANALYSIS_YEAR}-12-31"

print(f"\nAnalyzing battery revenue for {ANALYSIS_YEAR}")
print(f"Region: NSW1")

# ============================================================================
# PART 1: Identify NSW Batteries Operational Full Year
# ============================================================================

print("\n" + "-" * 80)
print("Identifying NSW batteries operational full year 2025...")

try:
    # Get battery facilities from OpenElectricity
    batteries_discharge = get_openelectricity_facilities(
        fueltech_id='battery_discharging',
        region='NSW1',
        status_id='operating'
    )

    batteries_charge = get_openelectricity_facilities(
        fueltech_id='battery_charging',
        region='NSW1',
        status_id='operating'
    )

    print(f"✓ Found {len(batteries_discharge)} discharging DUIDs")
    print(f"✓ Found {len(batteries_charge)} charging DUIDs")

except Exception as e:
    print(f"\n✗ Error fetching battery metadata: {e}")
    print("\nPlease run:")
    print("  python scripts/download/download_generator_metadata.py")
    sys.exit(1)

# Filter for batteries operational full year 2025
# Use first_seen and last_seen to identify batteries operational throughout 2025
batteries_discharge['first_seen'] = pd.to_datetime(batteries_discharge.get('first_seen', None), errors='coerce')
batteries_discharge['last_seen'] = pd.to_datetime(batteries_discharge.get('last_seen', None), errors='coerce')

operational_full_year = batteries_discharge[
    (batteries_discharge['first_seen'] <= pd.Timestamp(START_DATE)) &
    ((batteries_discharge['last_seen'].isna()) | (batteries_discharge['last_seen'] >= pd.Timestamp(END_DATE)))
].copy()

print(f"\n✓ Identified {len(operational_full_year)} batteries operational full year {ANALYSIS_YEAR}")

if len(operational_full_year) == 0:
    print("\n✗ No batteries found operational for full year 2025")
    print("Using all operating batteries instead...")
    operational_full_year = batteries_discharge.copy()

# Get discharge and charging DUIDs
discharge_duids = operational_full_year['duid'].dropna().unique().tolist()

# Match charging DUIDs (typically same station code with different suffix)
# Extract station codes from discharge DUIDs
def get_station_code(duid):
    """Extract station code from DUID (typically first part before number)"""
    # Most battery DUIDs follow pattern: STATIONNAME1, STATIONNAME2
    # Charging is often STATIONNAMEC1, STATIONNAMEC2
    # We'll use facility_code to match
    return duid

# Create mapping via facility_code
discharge_with_code = operational_full_year[['duid', 'facility_code']].dropna()
charge_with_code = batteries_charge[['duid', 'facility_code']].dropna()

# Match charging DUIDs to discharge DUIDs via facility_code
matched_charge = charge_with_code[
    charge_with_code['facility_code'].isin(discharge_with_code['facility_code'])
]
charging_duids = matched_charge['duid'].unique().tolist()

print(f"  Discharge DUIDs: {len(discharge_duids)}")
print(f"  Charging DUIDs: {len(charging_duids)}")

if len(discharge_duids) == 0:
    print("\n✗ No discharge DUIDs found. Cannot proceed with analysis.")
    sys.exit(1)

# ============================================================================
# PART 2: Load SCADA and Price Data
# ============================================================================

print("\n" + "-" * 80)
print("Loading SCADA data...")

# Load discharge SCADA
try:
    print(f"Loading discharge SCADA for {len(discharge_duids)} DUIDs...")
    scada_discharge = load_cached_dispatch_scada(START_DATE, END_DATE, duids=discharge_duids)
    print(f"✓ Loaded {len(scada_discharge):,} discharge records")
except FileNotFoundError as e:
    print(f"\n✗ Error: {e}")
    print("\nPlease run:")
    print("  python scripts/download/download_dispatch_scada.py")
    sys.exit(1)

# Load charging SCADA
if len(charging_duids) > 0:
    try:
        print(f"Loading charging SCADA for {len(charging_duids)} DUIDs...")
        scada_charge = load_cached_dispatch_scada(START_DATE, END_DATE, duids=charging_duids)
        print(f"✓ Loaded {len(scada_charge):,} charging records")
    except FileNotFoundError as e:
        print(f"\n✗ Warning: Could not load charging SCADA: {e}")
        scada_charge = pl.DataFrame()
else:
    print("No charging DUIDs found, using discharge data only")
    scada_charge = pl.DataFrame()

# Load price data
print("\nLoading price data...")
try:
    prices = load_cached_dispatchprice(START_DATE, END_DATE, region='NSW1')
    print(f"✓ Loaded {len(prices):,} price records")
except FileNotFoundError as e:
    print(f"\n✗ Error: {e}")
    print("\nPlease run:")
    print("  python scripts/download/download_dispatchprice.py")
    sys.exit(1)

# ============================================================================
# PART 3: Calculate Revenue by Price Bucket
# ============================================================================

print("\n" + "-" * 80)
print("Calculating revenue...")

# Join discharge SCADA to prices
print("Joining discharge SCADA to prices...")
scada_discharge = scada_discharge.join(
    prices.select(['SETTLEMENTDATE', 'REGIONID', 'RRP']),
    on='SETTLEMENTDATE',
    how='left'
)

# Calculate discharge revenue (positive)
# Energy = Power (MW) × (5/60) hours
# Revenue = Energy × Price
scada_discharge = scada_discharge.with_columns([
    (pl.col('SCADAVALUE') * (5/60) * pl.col('RRP')).alias('revenue_discharge')
])

print(f"✓ Calculated discharge revenue")

# Join charging SCADA to prices and calculate charging cost (negative revenue)
if len(scada_charge) > 0:
    print("Joining charging SCADA to prices...")
    scada_charge = scada_charge.join(
        prices.select(['SETTLEMENTDATE', 'REGIONID', 'RRP']),
        on='SETTLEMENTDATE',
        how='left'
    )

    # Charging cost is negative revenue (paying to charge)
    scada_charge = scada_charge.with_columns([
        (-1 * pl.col('SCADAVALUE') * (5/60) * pl.col('RRP')).alias('revenue_charge')
    ])

    print(f"✓ Calculated charging cost")

# Combine discharge and charging revenue
print("Combining discharge and charging revenue...")

# Aggregate discharge revenue by interval
discharge_by_interval = scada_discharge.group_by('SETTLEMENTDATE').agg([
    pl.sum('revenue_discharge').alias('revenue')
])

# Aggregate charging revenue by interval
if len(scada_charge) > 0:
    charge_by_interval = scada_charge.group_by('SETTLEMENTDATE').agg([
        pl.sum('revenue_charge').alias('revenue')
    ])

    # Combine (sum revenues at each interval)
    combined_revenue = discharge_by_interval.join(
        charge_by_interval,
        on='SETTLEMENTDATE',
        how='outer',
        suffix='_charge'
    ).with_columns([
        (pl.col('revenue').fill_null(0) + pl.col('revenue_charge').fill_null(0)).alias('net_revenue')
    ])
else:
    combined_revenue = discharge_by_interval.with_columns([
        pl.col('revenue').alias('net_revenue')
    ])

# Join prices to get RRP for each interval
combined_revenue = combined_revenue.join(
    prices.select(['SETTLEMENTDATE', 'RRP']),
    on='SETTLEMENTDATE',
    how='left'
)

print(f"✓ Combined revenue calculated for {len(combined_revenue):,} intervals")

# ============================================================================
# PART 4: Assign Price Buckets
# ============================================================================

print("\n" + "-" * 80)
print("Assigning price buckets...")

# Define price buckets
PRICE_BUCKETS = [
    ('<-$1000', float('-inf'), -1000),
    ('-$1000 to -$500', -1000, -500),
    ('-$500 to -$100', -500, -100),
    ('-$100 to $0', -100, 0),
    ('$0 to $300', 0, 300),
    ('$300 to $1000', 300, 1000),
    ('$1000 to $2000', 1000, 2000),
    ('>$2000', 2000, float('inf'))
]

# Assign bucket to each interval
def assign_bucket(price):
    for bucket_name, low, high in PRICE_BUCKETS:
        if low <= price < high:
            return bucket_name
    return 'Unknown'

# Create bucket column
combined_revenue = combined_revenue.with_columns([
    pl.col('RRP').map_elements(assign_bucket, return_dtype=pl.Utf8).alias('price_bucket')
])

# Aggregate revenue by bucket
bucket_revenue = (
    combined_revenue
    .group_by('price_bucket')
    .agg([
        pl.sum('net_revenue').alias('total_revenue')
    ])
    .sort('total_revenue', descending=True)
)

# Calculate percentage of total revenue
total_revenue = bucket_revenue['total_revenue'].sum()
bucket_revenue = bucket_revenue.with_columns([
    (pl.col('total_revenue') / total_revenue * 100).alias('pct_revenue')
])

print(f"✓ Revenue aggregated by price bucket")
print(f"\nTotal annual battery revenue: ${total_revenue:,.0f}")

# Reorder buckets in logical price order
bucket_order = [b[0] for b in PRICE_BUCKETS]
bucket_revenue = bucket_revenue.with_columns([
    pl.col('price_bucket').cast(pl.Categorical).cat.set_ordering('physical')
])

# Convert to pandas for ordered categorical
bucket_revenue_pd = bucket_revenue.to_pandas()
bucket_revenue_pd['price_bucket'] = pd.Categorical(
    bucket_revenue_pd['price_bucket'],
    categories=bucket_order,
    ordered=True
)
bucket_revenue_pd = bucket_revenue_pd.sort_values('price_bucket')

print("\nRevenue by price bucket:")
for _, row in bucket_revenue_pd.iterrows():
    print(f"  {row['price_bucket']:20s}: {row['pct_revenue']:6.1f}% (${row['total_revenue']:>12,.0f})")

# ============================================================================
# PART 5: Create Visualization
# ============================================================================

print("\n" + "-" * 80)
print("Creating visualization...")

# Create figure
fig = go.Figure()

# Add bar chart
fig.add_trace(go.Bar(
    x=bucket_revenue_pd['price_bucket'],
    y=bucket_revenue_pd['pct_revenue'],
    marker_color=COLORS['battery'],
    hovertemplate="<b>%{x}</b><br>" +
                  "Revenue: %{y:.1f}%<br>" +
                  "Absolute: $%{customdata:,.0f}<br>" +
                  "<extra></extra>",
    customdata=bucket_revenue_pd['total_revenue']
))

# Update layout
fig.update_layout(
    title=dict(
        text=f"Battery Revenue Concentration by Price Bucket ({ANALYSIS_YEAR})<br>" +
             "<sub>NSW batteries show significant revenue from negative pricing and high-price events</sub>",
        font=dict(size=20, family="Lato")
    ),
    xaxis=dict(
        title="Price Bucket ($/MWh)",
        tickangle=-45
    ),
    yaxis=dict(
        title="Percentage of Total Revenue (%)",
        tickformat='.1f'
    ),
    showlegend=False,
    font=FONT_CONFIG,
    plot_bgcolor='white',
    paper_bgcolor='white',
    hovermode='x'
)

# Save outputs
output_file = get_output_path("section3", "battery_revenue_buckets.html")
fig.write_html(str(output_file))
print(f"\n✓ Visualization saved to: {output_file}")

json_file = get_output_path("section3", "battery_revenue_buckets.json")
fig.write_json(str(json_file))
print(f"✓ JSON data saved to: {json_file}")

# ============================================================================
# Summary Statistics
# ============================================================================

print("\n" + "=" * 80)
print("SUMMARY")
print("=" * 80)

print(f"\nBatteries Analyzed: {len(discharge_duids)}")
print(f"Analysis Period: {ANALYSIS_YEAR}")
print(f"Total Revenue: ${total_revenue:,.0f}")

# Calculate revenue from negative prices
negative_revenue = bucket_revenue_pd[
    bucket_revenue_pd['price_bucket'].isin(['<-$1000', '-$1000 to -$500', '-$500 to -$100', '-$100 to $0'])
]['total_revenue'].sum()
negative_pct = negative_revenue / total_revenue * 100

print(f"\nRevenue from negative prices: ${negative_revenue:,.0f} ({negative_pct:.1f}%)")

# Calculate revenue from high prices (>$1000)
high_revenue = bucket_revenue_pd[
    bucket_revenue_pd['price_bucket'].isin(['$1000 to $2000', '>$2000'])
]['total_revenue'].sum()
high_pct = high_revenue / total_revenue * 100

print(f"Revenue from high prices (>$1000): ${high_revenue:,.0f} ({high_pct:.1f}%)")

print("\nKey Insights:")
print(f"  • Battery revenue highly concentrated in extreme price events")
print(f"  • {negative_pct:.0f}% of revenue from negative pricing (paid to charge)")
print(f"  • {high_pct:.0f}% of revenue from high-price events (>$1000/MWh)")
print(f"  • Revenue concentration demonstrates arbitrage value of storage")

print("\n" + "=" * 80)
print("Analysis complete!")
print("=" * 80)
