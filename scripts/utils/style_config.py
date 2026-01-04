"""
Style configuration for Beyond the Solar Curve report.
Provides consistent Plotly themes, color palettes, and formatting.
"""

import plotly.io as pio
import plotly.graph_objects as go

# Color palette
COLORS = {
    'pv': '#FFD700',           # Yellow (solar PV)
    'wind': '#2E7D32',         # Green (wind)
    'battery': '#7B1FA2',      # Purple (battery standalone)
    'battery_colocated': '#FF6F00',  # Dark orange (battery co-located)
    'accent': '#00ACC1',       # Teal (accent color)
    'text': '#2C3E50',         # Dark blue-grey (text)
    'background': '#FFFFFF',   # White (background)
    'grid': '#E5E5E5',         # Light grey (gridlines)
    'negative': '#D32F2F',     # Red (negative values, curtailment)
    'positive': '#388E3C',     # Dark green (positive values)
}

# Lato font configuration
FONT_CONFIG = dict(
    family="Lato, sans-serif",
    size=14,
    color=COLORS['text']
)

FONT_TITLE = dict(
    family="Lato, sans-serif",
    size=20,
    color=COLORS['text']
)

FONT_AXIS = dict(
    family="Lato, sans-serif",
    size=12,
    color=COLORS['text']
)

# Default Plotly template for NEM report
TEMPLATE = go.layout.Template(
    layout=go.Layout(
        font=FONT_CONFIG,
        title_font=FONT_TITLE,
        plot_bgcolor=COLORS['background'],
        paper_bgcolor=COLORS['background'],
        xaxis=dict(
            showgrid=False,
            zeroline=True,
            zerolinecolor=COLORS['grid'],
            zerolinewidth=1,
            showline=True,
            linewidth=1,
            linecolor=COLORS['grid'],
            tickfont=FONT_AXIS,
            titlefont=FONT_AXIS
        ),
        yaxis=dict(
            showgrid=True,
            gridcolor=COLORS['grid'],
            gridwidth=1,
            zeroline=True,
            zerolinecolor=COLORS['grid'],
            zerolinewidth=1,
            showline=True,
            linewidth=1,
            linecolor=COLORS['grid'],
            tickfont=FONT_AXIS,
            titlefont=FONT_AXIS
        ),
        hovermode='x unified',
        hoverlabel=dict(
            bgcolor='white',
            font_size=12,
            font_family='Lato, sans-serif'
        ),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1,
            font=FONT_CONFIG,
            bgcolor='rgba(255, 255, 255, 0.8)',
            bordercolor=COLORS['grid'],
            borderwidth=1
        ),
        margin=dict(l=60, r=40, t=80, b=60)
    )
)

# Register template
pio.templates["nem_report"] = TEMPLATE
pio.templates.default = "nem_report"


def get_color(tech):
    """
    Get color for a given technology type.

    Parameters:
    -----------
    tech : str
        Technology type ('pv', 'wind', 'battery', 'battery_colocated', 'accent')

    Returns:
    --------
    str : Hex color code
    """
    return COLORS.get(tech.lower(), COLORS['accent'])


def get_status_opacity(status):
    """
    Get opacity value based on facility status.

    Parameters:
    -----------
    status : str
        Status type ('operating', 'committed', 'commissioning', 'anticipated')

    Returns:
    --------
    float : Opacity value (0-1)
    """
    status_map = {
        'operating': 0.9,
        'in service': 0.9,
        'committed': 0.7,
        'commissioning': 0.6,
        'in commissioning': 0.6,
        'anticipated': 0.4
    }
    return status_map.get(status.lower(), 0.5)


def format_currency(value, decimals=0):
    """
    Format value as currency (AUD).

    Parameters:
    -----------
    value : float
        Value to format
    decimals : int
        Number of decimal places (default 0)

    Returns:
    --------
    str : Formatted currency string
    """
    if decimals == 0:
        return f"${value:,.0f}"
    else:
        return f"${value:,.{decimals}f}"


def format_percentage(value, decimals=1):
    """
    Format value as percentage.

    Parameters:
    -----------
    value : float
        Value to format (0-100)
    decimals : int
        Number of decimal places (default 1)

    Returns:
    --------
    str : Formatted percentage string
    """
    return f"{value:.{decimals}f}%"


def format_energy(value, decimals=0):
    """
    Format value as energy (MWh).

    Parameters:
    -----------
    value : float
        Value in MWh
    decimals : int
        Number of decimal places (default 0)

    Returns:
    --------
    str : Formatted energy string
    """
    if value >= 1000:
        return f"{value/1000:,.{decimals}f} GWh"
    else:
        return f"{value:,.{decimals}f} MWh"


def create_hover_template(metrics):
    """
    Create standardized hover template for Plotly charts.

    Parameters:
    -----------
    metrics : dict
        Dictionary of metric names and formats
        Example: {'Year': '%{x}', 'Price': '$%{y:.2f}/MWh'}

    Returns:
    --------
    str : Hover template string
    """
    lines = ["<b>%{fullData.name}</b><br>"]
    lines.extend([f"{name}: {fmt}" for name, fmt in metrics.items()])
    lines.append("<extra></extra>")  # Remove secondary box
    return "<br>".join(lines)


# Status color mapping for generator maps
STATUS_COLORS = {
    'operating': COLORS['positive'],
    'in service': COLORS['positive'],
    'committed': COLORS['accent'],
    'commissioning': '#FFA726',  # Orange
    'in commissioning': '#FFA726',
    'anticipated': '#9E9E9E'  # Grey
}


# MLF color scale (for maps)
MLF_COLORSCALE = [
    [0.0, '#D32F2F'],    # Red (low MLF <0.85)
    [0.25, '#FF9800'],   # Orange (0.85-0.90)
    [0.5, '#FFD700'],    # Yellow (0.90-0.95)
    [0.75, '#66BB6A'],   # Light green (0.95-1.00)
    [1.0, '#2E7D32']     # Dark green (>1.00)
]


def get_mlf_color(mlf_value):
    """
    Get color for MLF value based on scale.

    Parameters:
    -----------
    mlf_value : float
        MLF value (typically 0.80-1.05)

    Returns:
    --------
    str : Hex color code
    """
    if mlf_value < 0.85:
        return '#D32F2F'  # Red
    elif mlf_value < 0.90:
        return '#FF9800'  # Orange
    elif mlf_value < 0.95:
        return '#FFD700'  # Yellow
    elif mlf_value < 1.00:
        return '#66BB6A'  # Light green
    else:
        return '#2E7D32'  # Dark green
