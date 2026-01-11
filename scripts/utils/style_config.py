"""
Style configuration for Beyond the Solar Curve report.
Economist Style - Clean, authoritative design with red/blue palette.
"""

import plotly.io as pio
import plotly.graph_objects as go

# Color palette - Economist Style
COLORS = {
    'pv': '#F4B400',           # Golden yellow (solar PV)
    'wind': '#0F9D58',         # Green (wind)
    'battery': '#7B1FA2',      # Purple (battery standalone)
    'battery_colocated': '#E65100',  # Deep orange (battery co-located)
    'accent': '#006BA2',       # Economist Blue (accent color)
    'primary': '#E3120B',      # Economist Red (primary)
    'text': '#1D1D1D',         # Dark grey (text)
    'background': '#FFFFFF',   # White (background)
    'grid': '#DBDBDB',         # Light grey (gridlines)
    'negative': '#E3120B',     # Red (negative values)
    'positive': '#0F9D58',     # Green (positive values)
}

# Libre Franklin font configuration
FONT_CONFIG = dict(
    family="Libre Franklin, -apple-system, sans-serif",
    size=14,
    color=COLORS['text']
)

FONT_TITLE = dict(
    family="Libre Franklin, -apple-system, sans-serif",
    size=18,
    color=COLORS['text']
)

FONT_AXIS = dict(
    family="Libre Franklin, -apple-system, sans-serif",
    size=12,
    color=COLORS['text']
)

# Default Plotly template - Economist Style
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
            linecolor=COLORS['text'],
            tickfont=FONT_AXIS,
            title=dict(font=FONT_AXIS)
        ),
        yaxis=dict(
            showgrid=True,
            gridcolor=COLORS['grid'],
            gridwidth=1,
            zeroline=True,
            zerolinecolor=COLORS['text'],
            zerolinewidth=1,
            showline=True,
            linewidth=1,
            linecolor=COLORS['text'],
            tickfont=FONT_AXIS,
            title=dict(font=FONT_AXIS)
        ),
        hovermode='x unified',
        hoverlabel=dict(
            bgcolor='white',
            font_size=12,
            font_family='Libre Franklin, sans-serif',
            bordercolor=COLORS['grid']
        ),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1,
            font=FONT_CONFIG,
            bgcolor='rgba(255, 255, 255, 0.95)',
            bordercolor=COLORS['grid'],
            borderwidth=1
        ),
        margin=dict(l=60, r=40, t=80, b=60),
        colorway=[
            COLORS['primary'],    # Economist Red
            COLORS['accent'],     # Economist Blue
            COLORS['pv'],         # Golden yellow
            COLORS['battery'],    # Purple
            COLORS['positive'],   # Green
            COLORS['battery_colocated'],  # Deep orange
        ]
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
    [0.0, '#E3120B'],    # Red (low MLF <0.85)
    [0.25, '#FF9800'],   # Orange (0.85-0.90)
    [0.5, '#F4B400'],    # Yellow (0.90-0.95)
    [0.75, '#66BB6A'],   # Light green (0.95-1.00)
    [1.0, '#0F9D58']     # Dark green (>1.00)
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
        return '#E3120B'  # Red
    elif mlf_value < 0.90:
        return '#FF9800'  # Orange
    elif mlf_value < 0.95:
        return '#F4B400'  # Yellow
    elif mlf_value < 1.00:
        return '#66BB6A'  # Light green
    else:
        return '#0F9D58'  # Dark green
