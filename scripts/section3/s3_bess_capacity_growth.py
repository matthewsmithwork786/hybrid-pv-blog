"""
Section 3 Analysis: BESS Capacity Growth

Generates stacked bar chart showing battery energy storage capacity (MWh)
installed across the NEM from 2018-2028, grouped by status.

Data source: NEM Generation Information Oct 2025.xlsx

Output: data/outputs/section3/bess_capacity_growth.html
"""

import sys
from pathlib import Path
import pandas as pd
import plotly.graph_objects as go

# Add utils to path
sys.path.append(str(Path(__file__).parent.parent / "utils"))

from style_config import COLORS, FONT_CONFIG, STATUS_COLORS
from data_paths import get_output_path, CONTEXT_NEM_GEN_INFO

print("=" * 80)
print("Section 3: BESS Capacity Growth Analysis")
print("=" * 80)

# ============================================================================
# Load and Process Data
# ============================================================================

print(f"\nLoading data from: {CONTEXT_NEM_GEN_INFO}")

try:
    # Load Excel file
    df = pd.read_excel(CONTEXT_NEM_GEN_INFO, sheet_name='ExistingGeneration&NewDevs')
    print(f"✓ Loaded {len(df)} total generator records")
except FileNotFoundError:
    print(f"\n✗ Error: File not found")
    print(f"  Expected: {CONTEXT_NEM_GEN_INFO}")
    print("\nPlease ensure the context file exists at this location.")
    sys.exit(1)

# Filter for batteries
print("\nFiltering for battery storage facilities...")

# Check column names (may vary in Excel file)
fuel_col = None
for col in df.columns:
    if 'fuel' in col.lower() and ('source' in col.lower() or 'tech' in col.lower()):
        fuel_col = col
        break

if fuel_col is None:
    print("Available columns:")
    for col in df.columns:
        print(f"  - {col}")
    raise ValueError("Could not find fuel source column")

print(f"Using column: {fuel_col}")

# Filter for battery
batteries = df[df[fuel_col].str.contains('Battery', case=False, na=False)].copy()
print(f"✓ Found {len(batteries)} battery facilities")

# ============================================================================
# Extract Year and Status
# ============================================================================

print("\nProcessing years and status...")

# Try to find commissioned date column
date_cols = [col for col in batteries.columns if 'date' in col.lower() or 'year' in col.lower()]
print(f"Available date columns: {date_cols}")

# Extract year from commissioned date or expected first year
if 'Commissioned Date' in batteries.columns:
    batteries['Year'] = pd.to_datetime(batteries['Commissioned Date'], errors='coerce').dt.year
elif 'Commission Date' in batteries.columns:
    batteries['Year'] = pd.to_datetime(batteries['Commission Date'], errors='coerce').dt.year
else:
    batteries['Year'] = None

# Fill missing years with expected first year
if 'Expected First Year' in batteries.columns:
    batteries['Year'] = batteries['Year'].fillna(batteries['Expected First Year'])
elif 'Expected Year' in batteries.columns:
    batteries['Year'] = batteries['Year'].fillna(batteries['Expected Year'])

# Remove rows without year
batteries = batteries[batteries['Year'].notna()].copy()
batteries['Year'] = batteries['Year'].astype(int)

print(f"Year range: {batteries['Year'].min()} - {batteries['Year'].max()}")

# Find status column
status_col = None
for col in batteries.columns:
    if 'status' in col.lower():
        status_col = col
        break

if status_col:
    print(f"Status column: {status_col}")
    print(f"Unique statuses: {batteries[status_col].unique()}")
else:
    print("Warning: No status column found, creating default status")
    batteries['Status'] = 'In Service'
    status_col = 'Status'

# Find capacity storage column
capacity_col = None
for col in batteries.columns:
    if 'storage' in col.lower() and 'mwh' in col.lower():
        capacity_col = col
        break

if capacity_col is None:
    print("\nSearching for capacity storage column...")
    for col in batteries.columns:
        if 'capacity' in col.lower():
            print(f"  Checking: {col}")
            if batteries[col].dtype in ['float64', 'int64']:
                # Check if values are reasonable for MWh
                max_val = batteries[col].max()
                if max_val > 10 and max_val < 100000:
                    capacity_col = col
                    print(f"  → Using {col} (max: {max_val})")
                    break

if capacity_col is None:
    raise ValueError("Could not find capacity storage (MWh) column")

print(f"\nCapacity column: {capacity_col}")

# ============================================================================
# Aggregate by Year and Status
# ============================================================================

print("\nAggregating capacity by year and status...")

# Group and sum
grouped = (
    batteries
    .groupby(['Year', status_col])[capacity_col]
    .sum()
    .reset_index()
    .rename(columns={capacity_col: 'Capacity_MWh'})
)

print(f"✓ Aggregated to {len(grouped)} year-status combinations")

# Filter to 2018-2028
grouped = grouped[(grouped['Year'] >= 2018) & (grouped['Year'] <= 2028)]

print("\nCapacity by year and status:")
for year in sorted(grouped['Year'].unique()):
    year_data = grouped[grouped['Year'] == year]
    total = year_data['Capacity_MWh'].sum()
    print(f"\n  {year}: {total:,.0f} MWh")
    for _, row in year_data.iterrows():
        print(f"    - {row[status_col]}: {row['Capacity_MWh']:,.0f} MWh")

# ============================================================================
# Create Visualization
# ============================================================================

print("\n" + "-" * 80)
print("Creating stacked bar chart...")

# Get unique statuses and sort by priority
status_priority = {
    'In Service': 0,
    'Operating': 0,
    'In Commissioning': 1,
    'Commissioning': 1,
    'Committed': 2,
    'Committed*': 3,
    'Anticipated': 4
}

statuses = sorted(
    grouped[status_col].unique(),
    key=lambda x: status_priority.get(x, 99)
)

print(f"Status order: {statuses}")

# Create figure
fig = go.Figure()

# Add trace for each status
for status in statuses:
    status_data = grouped[grouped[status_col] == status]

    # Get color
    color = STATUS_COLORS.get(status.lower(), COLORS['accent'])

    fig.add_trace(go.Bar(
        x=status_data['Year'],
        y=status_data['Capacity_MWh'],
        name=status,
        marker_color=color,
        hovertemplate="<b>%{x}</b><br>" +
                      f"{status}: %{{y:,.0f}} MWh<br>" +
                      "<extra></extra>"
    ))

# Update layout
fig.update_layout(
    title=dict(
        text="Battery Energy Storage Capacity in the NEM<br>" +
             "<sub>Installed and projected capacity (MWh) by status, 2018-2028</sub>",
        font=dict(size=20, family="Lato")
    ),
    xaxis=dict(
        title="Year",
        tickmode='linear',
        tick0=2018,
        dtick=1
    ),
    yaxis=dict(
        title="Capacity (MWh)",
        tickformat=',.0f'
    ),
    barmode='stack',
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

# Save outputs
output_file = get_output_path("section3", "bess_capacity_growth.html")
fig.write_html(str(output_file))
print(f"\n✓ Visualization saved to: {output_file}")

json_file = get_output_path("section3", "bess_capacity_growth.json")
fig.write_json(str(json_file))
print(f"✓ JSON data saved to: {json_file}")

# ============================================================================
# Summary Statistics
# ============================================================================

print("\n" + "=" * 80)
print("SUMMARY")
print("=" * 80)

total_2019 = grouped[grouped['Year'] == 2019]['Capacity_MWh'].sum()
total_2025 = grouped[grouped['Year'] == 2025]['Capacity_MWh'].sum()
total_2028 = grouped[grouped['Year'] == 2028]['Capacity_MWh'].sum()

print(f"\nTotal Battery Capacity:")
print(f"  2019: {total_2019:,.0f} MWh")
print(f"  2025: {total_2025:,.0f} MWh")
print(f"  2028 (projected): {total_2028:,.0f} MWh")

if total_2019 > 0:
    growth_2025 = (total_2025 / total_2019)
    print(f"\nGrowth:")
    print(f"  2019-2025: {growth_2025:.1f}x")

print("\nKey Insights:")
print(f"  • Rapid BESS deployment from {total_2019:,.0f} MWh (2019) to {total_2025:,.0f} MWh (2025)")
print(f"  • Significant pipeline: {total_2028:,.0f} MWh projected by 2028")
print(f"  • Battery storage is now a critical NEM asset class")

print("\n" + "=" * 80)
print("Analysis complete!")
print("=" * 80)
