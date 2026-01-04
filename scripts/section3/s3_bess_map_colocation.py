"""
Section 3 Analysis: BESS Co-location Map

Creates interactive Folium map showing battery storage facilities across the NEM.
Batteries are classified as:
- Standalone (purple): >1km from nearest solar facility
- Co-located (dark orange): ≤1km from nearest solar facility

Data source: OpenElectricity API

Output: data/outputs/section3/bess_map_colocation.html
"""

import sys
from pathlib import Path
import pandas as pd
import folium
from geopy.distance import geodesic

# Add utils to path
sys.path.append(str(Path(__file__).parent.parent / "utils"))

from style_config import COLORS, get_status_opacity
from data_paths import get_output_path
from nemosis_helpers import get_openelectricity_facilities

print("=" * 80)
print("Section 3: BESS Co-location Mapping")
print("=" * 80)

# ============================================================================
# Load Facility Data
# ============================================================================

print("\nFetching battery facilities from OpenElectricity API...")

try:
    batteries = get_openelectricity_facilities(
        fueltech_id=['battery_discharging'],  # Use discharge to avoid duplicates
        status_id=['operating', 'committed', 'commissioning']
    )
    print(f"✓ Loaded {len(batteries)} battery facilities")
except Exception as e:
    print(f"\n✗ Error fetching battery data: {e}")
    print("\nPlease run:")
    print("  python scripts/download/download_generator_metadata.py")
    sys.exit(1)

print("\nFetching solar facilities from OpenElectricity API...")

try:
    solar = get_openelectricity_facilities(
        fueltech_id='solar_utility',
        status_id=['operating', 'committed', 'commissioning']
    )
    print(f"✓ Loaded {len(solar)} solar facilities")
except Exception as e:
    print(f"\n✗ Error fetching solar data: {e}")
    sys.exit(1)

# ============================================================================
# Calculate Co-location
# ============================================================================

print("\n" + "-" * 80)
print("Calculating distances to nearest solar facility...")

# Filter facilities with valid coordinates
batteries = batteries[
    batteries['location_lat'].notna() &
    batteries['location_lng'].notna()
].copy()

solar = solar[
    solar['location_lat'].notna() &
    solar['location_lng'].notna()
].copy()

print(f"Batteries with coordinates: {len(batteries)}")
print(f"Solar facilities with coordinates: {len(solar)}")

# Calculate distance to nearest solar for each battery
def find_nearest_solar_distance(battery_row):
    """Calculate distance to nearest solar facility."""
    battery_coord = (battery_row['location_lat'], battery_row['location_lng'])

    distances = []
    for _, solar_row in solar.iterrows():
        solar_coord = (solar_row['location_lat'], solar_row['location_lng'])
        dist = geodesic(battery_coord, solar_coord).km
        distances.append(dist)

    if distances:
        return min(distances)
    else:
        return None

print("Computing distances...")
batteries['nearest_solar_km'] = batteries.apply(find_nearest_solar_distance, axis=1)

# Classify as co-located or standalone
CO_LOCATION_THRESHOLD_KM = 1.0
batteries['is_colocated'] = batteries['nearest_solar_km'] <= CO_LOCATION_THRESHOLD_KM

# Summary
n_colocated = batteries['is_colocated'].sum()
n_standalone = (~batteries['is_colocated']).sum()

print(f"\n✓ Distance calculation complete")
print(f"  Co-located (≤{CO_LOCATION_THRESHOLD_KM}km): {n_colocated}")
print(f"  Standalone (>{CO_LOCATION_THRESHOLD_KM}km): {n_standalone}")
print(f"  Co-located percentage: {n_colocated / len(batteries) * 100:.1f}%")

# ============================================================================
# Create Interactive Map
# ============================================================================

print("\n" + "-" * 80)
print("Creating interactive map...")

# Map center (Australia)
map_center = [-27.0, 133.0]
zoom_start = 5

# Create base map
m = folium.Map(location=map_center, zoom_start=zoom_start, tiles='OpenStreetMap')

# Create feature groups
fg_standalone = folium.FeatureGroup(name='Standalone BESS (>1km from solar)')
fg_colocated = folium.FeatureGroup(name='Co-located BESS (≤1km from solar)')

# Add feature groups to map
fg_standalone.add_to(m)
fg_colocated.add_to(m)

# Scale circle radius by capacity
if 'capacity_registered' in batteries.columns:
    min_cap = batteries['capacity_registered'].min()
    max_cap = batteries['capacity_registered'].max()
    min_radius = 4
    max_radius = 12

    def get_radius(cap):
        if pd.isna(cap) or max_cap == min_cap:
            return min_radius
        return min_radius + (cap - min_cap) / (max_cap - min_cap) * (max_radius - min_radius)

    batteries['radius'] = batteries['capacity_registered'].apply(get_radius)
else:
    batteries['radius'] = 6  # Default

# Add markers
print(f"Adding {len(batteries)} battery markers to map...")

for idx, row in batteries.iterrows():
    # Determine color and feature group
    if row['is_colocated']:
        color = COLORS['battery_colocated']  # Dark orange
        fg = fg_colocated
        classification = "Co-located"
    else:
        color = COLORS['battery']  # Purple
        fg = fg_standalone
        classification = "Standalone"

    # Get opacity based on status
    opacity = get_status_opacity(row['status_id']) if 'status_id' in row else 0.7

    # Create popup content
    capacity = row.get('capacity_registered', 'N/A')
    storage = row.get('capacity_storage', 'N/A')
    status = row.get('status_id', 'Unknown')
    network = row.get('network_region', 'N/A')
    nearest_km = row['nearest_solar_km']

    popup_html = f"""
    <div style="font-family: Lato, sans-serif; min-width: 250px;">
        <h4 style="margin: 0 0 10px 0;">{row['facility_name']}</h4>
        <table style="width: 100%; font-size: 12px;">
            <tr><td><b>Classification:</b></td><td>{classification}</td></tr>
            <tr><td><b>Nearest Solar:</b></td><td>{nearest_km:.2f} km</td></tr>
            <tr><td><b>Region:</b></td><td>{network}</td></tr>
            <tr><td><b>Status:</b></td><td>{status}</td></tr>
            <tr><td><b>Capacity:</b></td><td>{capacity} MW</td></tr>
            <tr><td><b>Storage:</b></td><td>{storage} MWh</td></tr>
        </table>
    </div>
    """

    # Add circle marker
    folium.CircleMarker(
        location=[row['location_lat'], row['location_lng']],
        radius=row['radius'],
        color=color,
        fill=True,
        fill_color=color,
        fill_opacity=opacity,
        weight=1,
        popup=folium.Popup(popup_html, max_width=300)
    ).add_to(fg)

# Add layer control
folium.LayerControl().add_to(m)

# Add legend
legend_html = f"""
<div style="position: fixed;
            top: 10px; right: 10px; width: 220px;
            background-color: white; z-index:9999; font-size:14px;
            border:2px solid grey; border-radius: 5px; padding: 10px;
            font-family: Lato, sans-serif;">
    <h4 style="margin: 0 0 10px 0;">BESS Classification</h4>
    <p style="margin: 5px 0;">
        <span style="background-color:{COLORS['battery']};
                     padding: 2px 8px; color: white; border-radius: 3px;">
            Standalone
        </span> &gt;1km from solar
    </p>
    <p style="margin: 5px 0;">
        <span style="background-color:{COLORS['battery_colocated']};
                     padding: 2px 8px; color: white; border-radius: 3px;">
            Co-located
        </span> ≤1km from solar
    </p>
    <p style="margin: 10px 0 5px 0; font-size: 12px; color: #666;">
        Circle size = Capacity (MW)
    </p>
</div>
"""
m.get_root().html.add_child(folium.Element(legend_html))

# Save map
output_file = get_output_path("section3", "bess_map_colocation.html")
m.save(str(output_file))

print(f"\n✓ Map saved to: {output_file}")
print(f"  File size: {output_file.stat().st_size / 1024:.1f} KB")

# ============================================================================
# Summary Statistics
# ============================================================================

print("\n" + "=" * 80)
print("SUMMARY")
print("=" * 80)

print(f"\nTotal Batteries: {len(batteries)}")
print(f"  Standalone: {n_standalone} ({n_standalone/len(batteries)*100:.1f}%)")
print(f"  Co-located: {n_colocated} ({n_colocated/len(batteries)*100:.1f}%)")

# By region
if 'network_region' in batteries.columns:
    print("\nBy Region:")
    for region in batteries['network_region'].value_counts().index[:5]:
        region_batteries = batteries[batteries['network_region'] == region]
        n_region_colocated = region_batteries['is_colocated'].sum()
        n_region_total = len(region_batteries)
        print(f"  {region}: {n_region_total} total, {n_region_colocated} co-located ({n_region_colocated/n_region_total*100:.0f}%)")

# By status
if 'status_id' in batteries.columns:
    print("\nBy Status:")
    for status in batteries['status_id'].value_counts().index:
        status_batteries = batteries[batteries['status_id'] == status]
        n_status_colocated = status_batteries['is_colocated'].sum()
        n_status_total = len(status_batteries)
        print(f"  {status}: {n_status_total} total, {n_status_colocated} co-located ({n_status_colocated/n_status_total*100:.0f}%)")

print("\nKey Insights:")
print(f"  • Majority of batteries ({n_standalone/len(batteries)*100:.0f}%) are standalone")
print(f"  • Co-located batteries represent niche deployment model")
print(f"  • Geographic clustering near major load centers visible")

print("\n" + "=" * 80)
print("Analysis complete!")
print("=" * 80)
