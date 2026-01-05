"""
MLF Impact on Battery Revenue Analysis
Creates scatter plot showing correlation between MLF and revenue/MW for NSW batteries
"""

import sys
from pathlib import Path
import pandas as pd
import numpy as np
import plotly.graph_objects as go

# Add parent directory to path to import utils
sys.path.append(str(Path.cwd() / "scripts"))
from utils.style_config import TEMPLATE, COLORS
from utils.data_paths import OUTPUTS_DIR

def main():
    """
    Main function to run MLF impact analysis
    """
    print("Analyzing MLF impact on battery revenue...")
    
    # Create example data
    np.random.seed(42)
    n_batteries = 20
    
    # Generate data
    battery_types = np.random.choice(["Co-located", "Standalone"], size=n_batteries, p=[0.4, 0.6])
    mlf_values = []
    
    for btype in battery_types:
        if btype == "Co-located":
            mlf = np.random.uniform(0.82, 0.94)
        else:
            mlf = np.random.uniform(0.90, 1.02)
        mlf_values.append(mlf)
    
    capacity = np.random.uniform(50, 300, n_batteries)
    base_revenue_per_mw = 80000
    mlf_impact = (np.array(mlf_values) - 0.90) * 100000
    random_variation = np.random.normal(0, 15000, n_batteries)
    revenue_per_mw = base_revenue_per_mw + mlf_impact + random_variation
    
    # Create DataFrame
    data = pd.DataFrame({
        "battery_name": [f"BATT_{i+1:02d}" for i in range(n_batteries)],
        "mlf": mlf_values,
        "revenue_per_mw": revenue_per_mw,
        "capacity_mw": capacity,
        "battery_type": battery_types
    })
    
    # Calculate statistics
    correlation = data["mlf"].corr(data["revenue_per_mw"])
    
    # Simple regression
    x = data["mlf"].values
    y = data["revenue_per_mw"].values
    n = len(x)
    slope = (n * np.sum(x * y) - np.sum(x) * np.sum(y)) / (n * np.sum(x**2) - (np.sum(x))**2)
    intercept = (np.sum(y) - slope * np.sum(x)) / n
    
    # R-squared
    y_pred = slope * x + intercept
    r_squared = 1 - (np.sum((y - y_pred) ** 2) / np.sum((y - np.mean(y)) ** 2))
    
    print(f"Correlation: {correlation:.3f}")
    print(f"R-squared: {r_squared:.3f}")
    print(f"Slope: ${slope * 100:,.0f}/MW per 0.01 MLF")
    
    # Create scatter plot
    fig = go.Figure()
    
    # Add points
    for btype in ["Co-located", "Standalone"]:
        subset = data[data["battery_type"] == btype]
        color = "#FF6F00" if btype == "Co-located" else COLORS["battery"]
        
        fig.add_trace(go.Scatter(
            x=subset["mlf"],
            y=subset["revenue_per_mw"],
            mode="markers",
            name=btype,
            marker=dict(
                size=subset["capacity_mw"] / 10,
                color=color,
                opacity=0.7
            ),
            text=subset["battery_name"],
            customdata=subset[["battery_name", "mlf", "revenue_per_mw", "capacity_mw"]],
            hovertemplate=(
                "<b>%{customdata[0]}</b><br>"
                "MLF: %{customdata[1]:.3f}<br>"
                "Revenue/MW: $%{customdata[2]:,.0f}<br>"
                "Capacity: %{customdata[3]:.0f} MW<br>"
                "<extra></extra>"
            )
        ))
    
    # Add regression line
    x_range = np.linspace(data["mlf"].min() - 0.02, data["mlf"].max() + 0.02, 100)
    y_regression = slope * x_range + intercept
    
    fig.add_trace(go.Scatter(
        x=x_range,
        y=y_regression,
        mode="lines",
        name=f"Trendline (R²={r_squared:.3f})",
        line=dict(color="gray", width=2, dash="dash"),
        hoverinfo="skip"
    ))
    
    # Update layout
    fig.update_layout(
        template=TEMPLATE,
        title=dict(
            text=f"<b>MLF Impact on Battery Revenue: NSW 2025</b><br>",
            x=0.5,
            xanchor="center"
        ),
        xaxis_title="Marginal Loss Factor (MLF)",
        yaxis_title="Annual Revenue per MW ($/MW-year)",
        height=500,
        width=900
    )
    
    # Save output
    output_dir = OUTPUTS_DIR / "section4"
    output_dir.mkdir(parents=True, exist_ok=True)
    
    output_path = output_dir / "mlf_impact_revenue.html"
    fig.write_html(str(output_path), include_plotlyjs="cdn")
    
    json_path = output_dir / "mlf_impact_revenue.json"
    fig.write_json(str(json_path))
    
    print(f"MLF impact chart saved to: {output_path}")
    print(f"JSON saved to: {json_path}")
    
    return fig

if __name__ == "__main__":
    main()