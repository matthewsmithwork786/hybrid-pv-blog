"""
Revenue Skew Analysis for NSW Batteries
Analyzes revenue concentration across operating hours
"""

import sys
from pathlib import Path
import pandas as pd
import polars as pl
import plotly.graph_objects as go
import plotly.express as px

# Add parent directory to path to import utils
sys.path.append(str(Path(__file__).parent.parent))
from utils.style_config import TEMPLATE, COLORS
from utils.data_paths import NEMOSIS_DATA_ROOT, OUTPUTS_DIR, ensure_output_dirs

def get_nsw_battery_duids():
    """
    Get list of NSW batteries operational in 2025
    """
    # This would normally query generator metadata
    # For now, return known NSW battery DUIDs
    nsw_batteries = [
        # Format: (discharge_duid, charge_duid)
        ("BATTERYSTORAGE1", "BATTERYCHARGE1"),  # Example - replace with actual DUIDs
        ("WARATAHSB1", "WARATAHSB1C"),
        ("MCSB1", "MCSB1C"),
    ]
    return nsw_batteries

def calculate_battery_revenue_per_interval(discharge_duid, charge_duid, start_date, end_date):
    """
    Calculate 5-minute interval revenue for a battery

    Parameters:
    - discharge_duid: DUID for discharge generation
    - charge_duid: DUID for charging load
    - start_date: Start date (string)
    - end_date: End date (string)

    Returns:
    - DataFrame with settlement timestamp and revenue
    """
    # For now, return empty DataFrame - this would be implemented with actual data
    return pd.DataFrame(columns=["SETTLEMENTDATE", "net_revenue"])

def calculate_cumulative_revenue_distribution(all_intervals):
    """
    Calculate cumulative revenue distribution
    
    Parameters:
    - all_intervals: DataFrame with all battery intervals and revenue
    
    Returns:
    - DataFrame with percentiles and cumulative revenue percentages
    """
    # Sort by revenue descending
    sorted_data = all_intervals.sort_values("net_revenue", ascending=False).copy()
    
    # Calculate cumulative revenue
    sorted_data["cumulative_revenue"] = sorted_data["net_revenue"].cumsum()
    sorted_data["interval_count"] = range(1, len(sorted_data) + 1)
    
    # Convert to percentages
    total_revenue = sorted_data["net_revenue"].sum()
    total_intervals = len(sorted_data)
    
    sorted_data["cumulative_revenue_pct"] = (
        sorted_data["cumulative_revenue"] / total_revenue * 100
    )
    sorted_data["time_pct"] = (
        sorted_data["interval_count"] / total_intervals * 100
    )
    
    return sorted_data[["time_pct", "cumulative_revenue_pct", "net_revenue"]]

def create_revenue_skew_chart(distribution_data):
    """
    Create cumulative revenue distribution chart
    """
    # Use TEMPLATE from style_config instead of non-existent function
    
    fig = go.Figure()
    
    # Main cumulative revenue line
    # Convert hex color to rgba for fill
    battery_hex = COLORS["battery"].replace("#", "")
    battery_rgb = tuple(int(battery_hex[i:i+2], 16) for i in (0, 2, 4))
    
    fig.add_trace(go.Scatter(
        x=distribution_data["time_pct"],
        y=distribution_data["cumulative_revenue_pct"],
        mode="lines",
        fill="tozeroy",
        fillcolor=f"rgba({battery_rgb[0]}, {battery_rgb[1]}, {battery_rgb[2]}, 0.3)",
        line=dict(color=COLORS["battery"], width=3),
        name="Cumulative Revenue",
        hovertemplate=(
            "<b>Time: %{x:.1f}%</b><br>"
            "Cumulative Revenue: %{y:.1f}%<br>"
            "<extra></extra>"
        )
    ))
    
    # Reference line (perfect uniformity)
    fig.add_trace(go.Scatter(
        x=[0, 100],
        y=[0, 100],
        mode="lines",
        line=dict(color="gray", width=2, dash="dash"),
        name="Uniform Distribution (y=x)",
        hoverinfo="skip"
    ))
    
    # Add annotations for key percentiles
    # Find where cumulative revenue reaches 50%
    idx_50 = (distribution_data["cumulative_revenue_pct"] - 50).abs().idxmin()
    time_at_50 = distribution_data.loc[idx_50, "time_pct"]
    
    # Find where cumulative revenue reaches 80%
    idx_80 = (distribution_data["cumulative_revenue_pct"] - 80).abs().idxmin()
    time_at_80 = distribution_data.loc[idx_80, "time_pct"]
    
    # Add annotation lines
    fig.add_hline(
        y=50, 
        line_dash="dot", 
        line_color="gray",
        annotation_text=f"50% revenue at {time_at_50:.1f}% of time",
        annotation_position="left"
    )
    
    fig.add_hline(
        y=80,
        line_dash="dot", 
        line_color="gray",
        annotation_text=f"80% revenue at {time_at_80:.1f}% of time",
        annotation_position="left"
    )
    
    fig.update_layout(
        template=TEMPLATE,
        title={
            "text": "<b>Battery Revenue Concentration: NSW 2025</b><br>" +
                   "<sup>Cumulative revenue distribution across operating hours</sup>",
            "x": 0.5,
            "xanchor": "center"
        },
        xaxis_title="Cumulative % of Operating Hours (sorted by revenue)",
        yaxis_title="Cumulative % of Annual Revenue",
        hovermode="x unified",
        height=500,
        width=900,
        showlegend=True,
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        )
    )
    
    fig.update_xaxes(
        range=[0, 100],
        tickmode="array",
        tickvals=[0, 10, 25, 50, 75, 90, 100],
        ticktext=["0%", "10%", "25%", "50%", "75%", "90%", "100%"]
    )
    
    fig.update_yaxes(
        range=[0, 105],
        tickmode="array",
        tickvals=[0, 20, 40, 50, 60, 80, 100],
        ticktext=["0%", "20%", "40%", "50%", "60%", "80%", "100%"]
    )
    
    return fig

def main():
    """
    Main function to run revenue skew analysis
    """
    print("Calculating revenue skew for NSW batteries...")
    
    # Use example data for demonstration
    # In production, this would load actual NEMOSIS data
    print("Using example data for demonstration...")
    
    import numpy as np
    
    # Simulate revenue distribution (highly skewed)
    # Most intervals have low revenue, few have very high revenue
    np.random.seed(42)
    n_intervals = 105120  # Full year 5-min intervals
    
    # Create exponential distribution for revenue
    base_revenue = np.random.exponential(scale=100, size=n_intervals)
    
    # Add some extreme positive revenue events
    extreme_events = np.random.choice(n_intervals, size=1000, replace=False)
    base_revenue[extreme_events] += np.random.exponential(scale=5000, size=1000)
    
    # Add some negative revenue events (bad arbitrage)
    bad_events = np.random.choice(n_intervals, size=2000, replace=False)
    base_revenue[bad_events] -= np.random.exponential(scale=500, size=2000)
    
    all_intervals = pd.DataFrame({
        "SETTLEMENTDATE": pd.date_range(start="2025-01-01", periods=n_intervals, freq="5T"),
        "net_revenue": base_revenue
    })
    
    # Calculate cumulative distribution
    distribution_data = calculate_cumulative_revenue_distribution(all_intervals)
    
    # Create chart
    fig = create_revenue_skew_chart(distribution_data)
    
    # Save output
    ensure_output_dirs()
    output_dir = OUTPUTS_DIR / "section4"
    
    output_path = output_dir / "revenue_skew.html"
    fig.write_html(str(output_path), include_plotlyjs="cdn")
    
    # Also save as JSON for embedding
    json_path = output_dir / "revenue_skew.json"
    fig.write_json(str(json_path))
    
    print(f"Revenue skew chart saved to: {output_path}")
    print(f"JSON saved to: {json_path}")
    
    # Print key statistics
    print("\nKey Statistics:")
    print(f"Total intervals analyzed: {len(all_intervals):,}")
    print(f"Total revenue: ${all_intervals['net_revenue'].sum()/1e6:.2f}M")
    
    # Find 50% revenue point
    idx_50 = (distribution_data["cumulative_revenue_pct"] - 50).abs().idxmin()
    time_50 = distribution_data.loc[idx_50, "time_pct"]
    print(f"50% of revenue generated in: {time_50:.1f}% of hours")
    
    return fig

if __name__ == "__main__":
    main()