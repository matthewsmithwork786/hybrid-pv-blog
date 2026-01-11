"""
Style configuration for Beyond the Solar Curve report.
Pudding.cool Style - Bold, modern, playful design.
"""

import plotly.io as pio
import plotly.graph_objects as go

# Color palette - Pudding Style
COLORS = {
    'pv': '#FFE066',           # Bright yellow (solar PV)
    'wind': '#00D4AA',         # Teal (wind)
    'battery': '#6C63FF',      # Purple (battery standalone)
    'battery_colocated': '#FF6B9D',  # Hot pink (battery co-located)
    'accent': '#00D4AA',       # Teal (accent color)
    'primary': '#6C63FF',      # Vibrant purple (primary)
    'secondary': '#FF6B9D',    # Hot pink
    'text': '#1A1A2E',         # Dark blue-grey (text)
    'background': '#FAFAFE',   # Cool off-white (background)
    'grid': '#E0E0EC',         # Light purple-grey (gridlines)
    'negative': '#FF5C5C',     # Coral red (negative values)
    'positive': '#00D4AA',     # Teal (positive values)
}

# Space Grotesk / DM Sans font configuration
FONT_CONFIG = dict(
    family="DM Sans, -apple-system, sans-serif",
    size=14,
    color=COLORS['text']
)

FONT_TITLE = dict(
    family="Space Grotesk, sans-serif",
    size=20,
    color=COLORS['text']
)

FONT_AXIS = dict(
    family="DM Sans, -apple-system, sans-serif",
    size=12,
    color=COLORS['text']
)

# Default Plotly template - Pudding Style
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
            linewidth=2,
            linecolor=COLORS['primary'],
            tickfont=FONT_AXIS,
            title=dict(font=FONT_AXIS)
        ),
        yaxis=dict(
            showgrid=True,
            gridcolor=COLORS['grid'],
            gridwidth=1,
            zeroline=True,
            zerolinecolor=COLORS['primary'],
            zerolinewidth=2,
            showline=True,
            linewidth=2,
            linecolor=COLORS['primary'],
            tickfont=FONT_AXIS,
            title=dict(font=FONT_AXIS)
        ),
        hovermode='x unified',
        hoverlabel=dict(
            bgcolor=COLORS['primary'],
            font_size=13,
            font_family='DM Sans, sans-serif',
            font_color='white',
            bordercolor=COLORS['secondary']
        ),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1,
            font=FONT_CONFIG,
            bgcolor='rgba(250, 250, 254, 0.95)',
            bordercolor=COLORS['grid'],
            borderwidth=1
        ),
        margin=dict(l=60, r=40, t=80, b=60),
        colorway=[
            COLORS['primary'],    # Purple
            COLORS['secondary'],  # Hot pink
            COLORS['accent'],     # Teal
            COLORS['pv'],         # Yellow
            COLORS['negative'],   # Coral
            '#FFB547',            # Orange
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
    'committed': COLORS['primary'],
    'commissioning': COLORS['secondary'],
    'in commissioning': COLORS['secondary'],
    'anticipated': '#7A7A8C'  # Muted grey
}


# MLF color scale (for maps) - Pudding palette
MLF_COLORSCALE = [
    [0.0, '#FF5C5C'],    # Coral (low MLF <0.85)
    [0.25, '#FF6B9D'],   # Pink (0.85-0.90)
    [0.5, '#FFE066'],    # Yellow (0.90-0.95)
    [0.75, '#33E0BD'],   # Light teal (0.95-1.00)
    [1.0, '#00D4AA']     # Teal (>1.00)
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
        return '#FF5C5C'  # Coral
    elif mlf_value < 0.90:
        return '#FF6B9D'  # Pink
    elif mlf_value < 0.95:
        return '#FFE066'  # Yellow
    elif mlf_value < 1.00:
        return '#33E0BD'  # Light teal
    else:
        return '#00D4AA'  # Teal
