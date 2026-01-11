"""
Style configuration for Beyond the Solar Curve report.
Financial Times Style - Sophisticated dark navy with salmon accents.
"""

import plotly.io as pio
import plotly.graph_objects as go

# Color palette - FT Navy Style
COLORS = {
    'pv': '#E5A882',           # Warm salmon (solar PV)
    'wind': '#4A7C59',         # Muted green (wind)
    'battery': '#5C4B8A',      # Muted purple (battery standalone)
    'battery_colocated': '#C9A66B',  # Gold (battery co-located)
    'accent': '#1B3A57',       # Navy blue (accent color)
    'primary': '#0D1B2A',      # Dark navy (primary)
    'warm': '#C9A66B',         # Gold accent
    'text': '#33302E',         # Dark brown-grey (text)
    'background': '#FFF9F5',   # Warm off-white (background)
    'grid': '#E5D9CD',         # Warm grey (gridlines)
    'negative': '#A63D40',     # Muted red (negative values)
    'positive': '#4A7C59',     # Muted green (positive values)
}

# Playfair Display / Source Sans 3 font configuration
FONT_CONFIG = dict(
    family="Source Sans 3, Georgia, serif",
    size=14,
    color=COLORS['text']
)

FONT_TITLE = dict(
    family="Playfair Display, Georgia, serif",
    size=18,
    color=COLORS['primary']
)

FONT_AXIS = dict(
    family="Source Sans 3, Georgia, serif",
    size=12,
    color=COLORS['text']
)

# Default Plotly template - FT Navy Style
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
            zerolinewidth=1,
            showline=True,
            linewidth=1,
            linecolor=COLORS['primary'],
            tickfont=FONT_AXIS,
            title=dict(font=FONT_AXIS)
        ),
        hovermode='x unified',
        hoverlabel=dict(
            bgcolor=COLORS['primary'],
            font_size=12,
            font_family='Source Sans 3, sans-serif',
            font_color='#FFE4D1',
            bordercolor=COLORS['warm']
        ),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1,
            font=FONT_CONFIG,
            bgcolor='rgba(255, 249, 245, 0.95)',
            bordercolor=COLORS['grid'],
            borderwidth=1
        ),
        margin=dict(l=60, r=40, t=80, b=60),
        colorway=[
            COLORS['primary'],    # Dark navy
            COLORS['warm'],       # Gold
            COLORS['pv'],         # Salmon
            COLORS['battery'],    # Purple
            COLORS['positive'],   # Green
            COLORS['battery_colocated'],  # Gold
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
    'commissioning': COLORS['warm'],
    'in commissioning': COLORS['warm'],
    'anticipated': '#8A8683'  # Muted grey
}


# MLF color scale (for maps) - FT palette
MLF_COLORSCALE = [
    [0.0, '#A63D40'],    # Muted red (low MLF <0.85)
    [0.25, '#C9A66B'],   # Gold (0.85-0.90)
    [0.5, '#E5A882'],    # Salmon (0.90-0.95)
    [0.75, '#6B9B7A'],   # Light green (0.95-1.00)
    [1.0, '#4A7C59']     # Muted green (>1.00)
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
        return '#A63D40'  # Red
    elif mlf_value < 0.90:
        return '#C9A66B'  # Gold
    elif mlf_value < 0.95:
        return '#E5A882'  # Salmon
    elif mlf_value < 1.00:
        return '#6B9B7A'  # Light green
    else:
        return '#4A7C59'  # Green
