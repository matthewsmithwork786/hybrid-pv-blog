"""
MLF Choropleth Map for NSW Generators
Creates interactive Folium map showing MLF values across NSW
"""

import sys
from pathlib import Path
import pandas as pd
import numpy as np
import folium
from folium import plugins
import json

# Add parent directory to path to import utils
sys.path.append(str(Path.cwd().parent.parent / "scripts"))
from utils.style_config import COLORS
from utils.data_paths import OUTPUTS_PATH

def get_nsw_generator_mlf_data():
    """
    Get MLF data for all NSW generators
    
    Returns:
    - DataFrame with generator locations and MLF values
    """
    # In production, this would query:
    # 1. Generator metadata (OpenElectricity API)
    # 2. MLF tables (AEMO registration data)
    
    # For demonstration, create realistic example data
    np.random.seed(42)
    
    # NSW geographic bounds (approximate)
    lat_range = (-37.5, -28.0)  # Southern to northern NSW
    lon_range = (141.0, 153.5)  # Western to eastern NSW
    
    # Create generator data with realistic geographic distribution
    # High MLF near coast/cities, low MLF in west/rural areas
    
    n_generators = 150
    
    # Define regions with different MLF characteristics
    regions = [
        {
            "name": "Sydney Metropolitan",
            "lat_range": (-34.0, -33.5),
            "lon_range": (150.8, 151.5),
            "mlf_range": (0.98, 1.05),
            "fueltech_mix": ["gas", "battery", "solar", "wind"],
            "n": 25
        },
        {
            "name": "Newcastle/Lake Macquarie",
            "lat_range": (-33.2, -32.8),
            "lon_range": (151.4, 151.8),
            "mlf_range": (0.96, 1.02),
            "fueltech_mix": ["gas", "coal", "battery", "solar"],
            "n": 20
        },
        {
            "name": "Central Coast",
            "lat_range": (-33.5, -33.2),
            "lon_range": (151.2, 151.5),
            "mlf_range": (0.95, 1.01),
            "fueltech_mix": ["gas", "battery", "solar"],
            "n": 15
        },
        {
            "name": "Wollongong/Illawarra",
            "lat_range": (-34.5, -34.2),
            "lon_range": (150.8, 151.0),
            "mlf_range": (0.94, 1.00),
            "fueltech_mix": ["coal", "gas", "battery", "solar"],
            "n": 15
        },
        {
            "name": "New England Tablelands",
            "lat_range": (-31.5, -29.5),
            "lon_range": (151.0, 152.0),
            "mlf_range": (0.90, 0.97),
            "fueltech_mix": ["wind", "solar", "battery"],
            "n": 20
        },
        {
            "name": "Riverina",
            "lat_range": (-35.5, -34.0),
            "lon_range": (146.0, 147.5),
            "mlf_range": (0.85, 0.94),
            "fueltech_mix": ["solar", "battery", "gas"],
            "n": 20
        },
        {
            "name": "Far West",
            "lat_range": (-32.0, -29.0),
            "lon_range": (142.0, 145.0),
            "mlf_range": (0.80, 0.90),
            "fueltech_mix": ["solar", "battery"],
            "n": 15
        },
        {
            "name": "Mid-North Coast",
            "lat_range": (-32.0, -30.5),
            "lon_range": (152.0, 153.0),
            "mlf_range": (0.92, 0.99),
            "fueltech_mix": ["solar", "wind", "battery"],
            "n": 10
        },
        {
            "name": "South Coast",
            "lat_range": (-37.0, -35.5),
            "lon_range": (149.5, 150.5),
            "mlf_range": (0.91, 0.98),
            "fueltech_mix": ["wind", "solar", "battery"],
            "n": 10
        }
    ]
    
    generators = []
    
    for region in regions:
        for i in range(region["n"]):
            # Random location within region
            lat = np.random.uniform(region["lat_range"][0], region["lat_range"][1])
            lon = np.random.uniform(region["lon_range"][0], region["lon_range"][1])
            
            # MLF based on region
            mlf = np.random.uniform(region["mlf_range"][0], region["mlf_range"][1])
            
            # Fueltech
            fueltech = np.random.choice(region["fueltech_mix"])
            
            # Capacity varies by technology
            if fueltech == "coal":
                capacity = np.random.uniform(500, 2000)
            elif fueltech == "gas":
                capacity = np.random.uniform(50, 500)
            elif fueltech == "battery":
                capacity = np.random.uniform(50, 300)
            elif fueltech == "solar":
                capacity = np.random.uniform(50, 400)
            elif fueltech == "wind":
                capacity = np.random.uniform(50, 500)
            else:
                capacity = np.random.uniform(50, 300)
            
            generators.append({
                "name": f"{fueltech.upper()}_{region['name'].replace(' ', '_')}_{len(generators)+1}",
                "lat": lat,
                "lon": lon,
                "mlf": mlf,
                "fueltech": fueltech,
                "capacity_mw": capacity,
                "region": region["name"]
            })
    
    return pd.DataFrame(generators)

def get_mlf_color(mlf):
    """
    Get color for MLF value (red=low, yellow=medium, green=high)
    """
    if mlf < 0.85:
        return "#d32f2f"  # Dark red (very poor)
    elif mlf < 0.90:
        return "#f57c00"  # Orange (poor)
    elif mlf < 0.95:
        return "#fbc02d"  # Yellow (medium)
    elif mlf < 1.0:
        return "#8bc34a"  # Light green (good)
    else:
        return "#2e7d32"  # Dark green (excellent)

def get_fueltech_icon(fueltech):
    """
    Get icon/color for fuel technology
    """
    icons = {
        "coal": "⚫",
        "gas": "🔵", 
        "solar": "🟡",
        "wind": "🌬️",
        "battery": "🔋"
    }
    return icons.get(fueltech, "⚪")

def create_mlf_map(generators):
    """
    Create interactive Folium map with MLF choropleth
    """
    # Create base map centered on NSW
    m = folium.Map(
        location=[-32.0, 147.5],
        zoom_start=7,
        tiles="OpenStreetMap"
    )
    
    # Add layer groups for different fuel types
    fueltechs = generators["fueltech"].unique()
    layer_groups = {}
    
    for fueltech in sorted(fueltechs):
        layer_groups[fueltech] = folium.FeatureGroup(name=f"{fueltech.capitalize()} Plants")
        m.add_child(layer_groups[fueltech])
    
    # Add generators to map
    for idx, gen in generators.iterrows():
        # Get color based on MLF
        color = get_mlf_color(gen["mlf"])
        
        # Marker size based on capacity
        radius = max(5, min(20, gen["capacity_mw"] / 50))
        
        # Create popup
        popup_html = f"""
        <div style="font-family: Arial, sans-serif;">
            <h4>{gen["name"]}</h4>
            <b>Technology:</b> {gen["fueltech"].capitalize()}<br>
            <b>Capacity:</b> {gen["capacity_mw"]:.0f} MW<br>
            <b>MLF:</b> {gen["mlf"]:.3f}<br>
            <b>Region:</b> {gen["region"]}<br>
            <b>Location:</b> ({gen["lat"]:.2f}, {gen["lon"]:.2f})
        </div>
        """
        
        # Create tooltip
        tooltip = f"""
        <b>{gen["name"]}</b><br>
        {gen["fueltech"].capitalize()} | {gen["capacity_mw"]:.0f} MW<br>
        MLF: {gen["mlf"]:.3f}
        """
        
        # Add circle marker
        marker = folium.CircleMarker(
            location=[gen["lat"], gen["lon"]],
            radius=radius,
            popup=folium.Popup(popup_html, max_width=300),
            tooltip=tooltip,
            color=color,
            fill=True,
            fillColor=color,
            fillOpacity=0.7,
            weight=2
        )
        
        # Add to appropriate layer
        layer_groups[gen["fueltech"]].add_child(marker)
    
    # Add layer control
    folium.LayerControl(position="topright").add_to(m)
    
    # Add MLF legend
    legend_html = """
    <div style="
        position: fixed;
        bottom: 50px;
        left: 50px;
        width: 250px;
        height: 180px;
        background-color: white;
        border: 2px solid grey;
        z-index: 9999;
        font-size: 14px;
        padding: 10px;
        border-radius: 5px;
    ">
    <p style="margin: 0 0 10px 0; font-weight: bold;">Marginal Loss Factor (MLF)</p>
    <p style="margin: 5px 0;"><i class="fa fa-circle" style="color: #d32f2f;"></i> &lt; 0.85 (Very Poor)</p>
    <p style="margin: 5px 0;"><i class="fa fa-circle" style="color: #f57c00;"></i> 0.85 - 0.90 (Poor)</p>
    <p style="margin: 5px 0;"><i class="fa fa-circle" style="color: #fbc02d;"></i> 0.90 - 0.95 (Medium)</p>
    <p style="margin: 5px 0;"><i class="fa fa-circle" style="color: #8bc34a;"></i> 0.95 - 1.00 (Good)</p>
    <p style="margin: 5px 0;"><i class="fa fa-circle" style="color: #2e7d32;"></i> &gt; 1.00 (Excellent)</p>
    </div>
    """
    m.get_root().html.add_child(folium.Element(legend_html))
    
    # Add fueltech legend
    fueltech_legend_html = """
    <div style="
        position: fixed;
        bottom: 50px;
        left: 320px;
        width: 200px;
        height: 180px;
        background-color: white;
        border: 2px solid grey;
        z-index: 9999;
        font-size: 14px;
        padding: 10px;
        border-radius: 5px;
    ">
    <p style="margin: 0 0 10px 0; font-weight: bold;">Technology Type</p>
    <p style="margin: 5px 0;">🔋 Battery</p>
    <p style="margin: 5px 0;">🟡 Solar</p>
    <p style="margin: 5px 0;">🌬️ Wind</p>
    <p style="margin: 5px 0;">🔵 Gas</p>
    <p style="margin: 5px 0;">⚫ Coal</p>
    <p style="margin: 10px 0 0 0; font-size: 11px; font-style: italic;">
    Toggle layers in top-right
    </p>
    </div>
    """
    m.get_root().html.add_child(folium.Element(fueltech_legend_html))
    
    # Add title
    title_html = """
    <h3 align="center" style="
        position: fixed;
        top: 10px;
        left: 50%;
        transform: translateX(-50%);
        z-index: 9999;
        background-color: white;
        padding: 10px 20px;
        border-radius: 5px;
        border: 2px solid grey;
        margin: 0;
    ">NSW Generator MLF Distribution</h3>
    """
    m.get_root().html.add_child(folium.Element(title_html))
    
    # Add mini map
    minimap = plugins.MiniMap()
    m.add_child(minimap)
    
    # Add fullscreen button
    plugins.Fullscreen().add_to(m)
    
    return m

def print_mlf_statistics(generators):
    """
    Print summary statistics for MLF distribution
    """
    print("\n" + "="*60)
    print("NSW GENERATOR MLF STATISTICS")
    print("="*60)
    
    # Overall statistics
    print(f"\nOverall MLF Statistics:")
    print(f"  Mean: {generators['mlf'].mean():.3f}")
    print(f"  Median: {generators['mlf'].median():.3f}")
    print(f"  Std Dev: {generators['mlf'].std():.3f}")
    print(f"  Range: {generators['mlf'].min():.3f} - {generators['mlf'].max():.3f}")
    
    # By fueltech
    print(f"\nMLF by Technology:")
    for fueltech in sorted(generators["fueltech"].unique()):
        subset = generators[generators["fueltech"] == fueltech]
        print(f"  {fueltech.capitalize():10s}: {subset['mlf'].mean():.3f} (avg)")
    
    # By region
    print(f"\nMLF by Region:")
    for region in sorted(generators["region"].unique()):
        subset = generators[generators["region"] == region]
        print(f"  {region:25s}: {subset['mlf'].mean():.3f} (avg)")
    
    # Battery-specific analysis
    batteries = generators[generators["fueltech"] == "battery"]
    if len(batteries) > 0:
        print(f"\nBattery-Specific Analysis:")
        print(f"  Count: {len(batteries)}")
        print(f"  Mean MLF: {batteries['mlf'].mean():.3f}")
        print(f"  Range: {batteries['mlf'].min():.3f} - {batteries['mlf'].max():.3f}")
        
        # Count by MLF category
        high_mlf = len(batteries[batteries["mlf"] >= 0.95])
        low_mlf = len(batteries[batteries["mlf"] < 0.90])
        print(f"  High MLF (≥0.95): {high_mlf} ({high_mlf/len(batteries)*100:.0f}%)")
        print(f"  Low MLF (<0.90): {low_mlf} ({low_mlf/len(batteries)*100:.0f}%)")
    
    # Solar-specific analysis (for co-location context)
    solar = generators[generators["fueltech"] == "solar"]
    if len(solar) > 0:
        print(f"\nSolar-Specific Analysis (Co-location Context):")
        print(f"  Count: {len(solar)}")
        print(f"  Mean MLF: {solar['mlf'].mean():.3f}")
        print(f"  Range: {solar['mlf'].min():.3f} - {solar['mlf'].max():.3f}")
    
    print("\n" + "="*60)

def main():
    """
    Main function to create MLF map
    """
    print("Generating MLF choropleth map for NSW generators...")
    
    # Get generator data
    generators = get_nsw_generator_mlf_data()
    
    # Print statistics
    print_mlf_statistics(generators)
    
    # Create map
    mlf_map = create_mlf_map(generators)
    
    # Save output
    output_dir = OUTPUTS_PATH / "section4"
    output_dir.mkdir(parents=True, exist_ok=True)
    
    output_path = output_dir / "mlf_map_nsw.html"
    mlf_map.save(str(output_path))
    
    print(f"\nMLF map saved to: {output_path}")
    print("Map includes:")
    print("  - 150+ generators across NSW")
    print("  - Color-coded by MLF value")
    print("  - Layer groups by technology type")
    print("  - Interactive markers with popup details")
    print("  - Mini-map and fullscreen controls")
    
    return mlf_map

if __name__ == "__main__":
    main()