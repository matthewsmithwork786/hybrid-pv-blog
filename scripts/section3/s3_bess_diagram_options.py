"""
Section 3: BESS Co-location Diagram Options

Recreates the Modo BESS co-location diagram using multiple Python packages.
Generates four different versions for comparison:
1. Matplotlib with custom icons
2. Graphviz with improved styling
3. Schemdraw electrical schematic style
4. Pure SVG/HTML for web embedding

Output: data/outputs/section3/bess_diagram_*.{svg,png,html}
"""

import sys
from pathlib import Path

# Add utils to path
sys.path.append(str(Path(__file__).parent.parent / "utils"))
from data_paths import get_output_path, ensure_output_dirs

# Ensure output directories exist
ensure_output_dirs()

print("=" * 80)
print("BESS Co-location Diagram Generator")
print("Creating multiple diagram options...")
print("=" * 80)

# Colors matching the original diagram
COLORS = {
    'ac_line': '#1a1a1a',        # Black for AC connections
    'dc_line': '#e91e63',        # Pink/magenta for DC connections
    'border': '#3f51b5',         # Blue dashed border
    'inverter': '#ffeb3b',       # Yellow for inverters
    'background': '#ffffff',      # White background
    'text': '#333333',           # Dark text
}

# ==============================================================================
# OPTION 1: Matplotlib with Custom Drawing
# ==============================================================================
def create_matplotlib_diagram():
    """Create diagram using Matplotlib with custom shapes and annotations."""
    print("\n" + "-" * 40)
    print("Option 1: Matplotlib Diagram")
    print("-" * 40)

    try:
        import matplotlib.pyplot as plt
        import matplotlib.patches as mpatches
        from matplotlib.patches import FancyBboxPatch, Rectangle, Circle, ConnectionPatch
        from matplotlib.lines import Line2D
        import matplotlib.image as mpimg
        import numpy as np
    except ImportError as e:
        print(f"✗ Missing dependency: {e}")
        return None

    fig, axes = plt.subplots(1, 3, figsize=(15, 8))
    fig.suptitle('Indicative diagrams of co-located battery and renewable generation',
                 fontsize=14, fontweight='bold', y=0.98)

    for ax in axes:
        ax.set_xlim(0, 100)
        ax.set_ylim(0, 100)
        ax.set_aspect('equal')
        ax.axis('off')

    def draw_grid_icon(ax, x, y, scale=1):
        """Draw transmission tower icon."""
        # Tower structure
        tower_color = '#333333'
        # Main vertical pole
        ax.plot([x, x], [y-8*scale, y+8*scale], color=tower_color, lw=2)
        # Cross arms
        ax.plot([x-6*scale, x+6*scale], [y+4*scale, y+4*scale], color=tower_color, lw=2)
        ax.plot([x-4*scale, x+4*scale], [y-2*scale, y-2*scale], color=tower_color, lw=2)
        # Wires
        ax.plot([x-6*scale, x-10*scale], [y+4*scale, y+4*scale], color=tower_color, lw=1.5)
        ax.plot([x+6*scale, x+10*scale], [y+4*scale, y+4*scale], color=tower_color, lw=1.5)

    def draw_inverter(ax, x, y, width=12, height=8, label=""):
        """Draw inverter box."""
        rect = FancyBboxPatch((x-width/2, y-height/2), width, height,
                              boxstyle="round,pad=0.02,rounding_size=1",
                              facecolor=COLORS['inverter'], edgecolor='#333333', lw=1.5)
        ax.add_patch(rect)
        if label:
            ax.text(x, y, label, ha='center', va='center', fontsize=8, fontweight='bold')

    def draw_solar_panel(ax, x, y, scale=1):
        """Draw solar panel icon."""
        panel_color = '#333333'
        # Main panel rectangle
        rect = Rectangle((x-6*scale, y-4*scale), 12*scale, 8*scale,
                         facecolor='white', edgecolor=panel_color, lw=1.5)
        ax.add_patch(rect)
        # Grid lines
        for i in range(1, 3):
            ax.plot([x-6*scale+i*4*scale, x-6*scale+i*4*scale],
                   [y-4*scale, y+4*scale], color=panel_color, lw=0.5)
        for i in range(1, 2):
            ax.plot([x-6*scale, x+6*scale],
                   [y-4*scale+i*4*scale, y-4*scale+i*4*scale], color=panel_color, lw=0.5)
        # Stand
        ax.plot([x, x], [y-4*scale, y-8*scale], color=panel_color, lw=1.5)
        ax.plot([x-3*scale, x+3*scale], [y-8*scale, y-8*scale], color=panel_color, lw=1.5)

    def draw_battery(ax, x, y, scale=1):
        """Draw battery icon."""
        batt_color = '#333333'
        # Main battery body
        rect = Rectangle((x-5*scale, y-6*scale), 10*scale, 12*scale,
                         facecolor='white', edgecolor=batt_color, lw=1.5)
        ax.add_patch(rect)
        # Battery terminal
        rect2 = Rectangle((x-2*scale, y+6*scale), 4*scale, 2*scale,
                          facecolor='white', edgecolor=batt_color, lw=1.5)
        ax.add_patch(rect2)
        # Battery level indicators
        for i in range(3):
            rect3 = Rectangle((x-3.5*scale, y-4*scale+i*3.5*scale), 7*scale, 2.5*scale,
                              facecolor='#e0e0e0', edgecolor='none')
            ax.add_patch(rect3)

    def draw_dashed_border(ax, x1, y1, x2, y2, label=""):
        """Draw dashed border around configuration."""
        rect = FancyBboxPatch((x1, y1), x2-x1, y2-y1,
                              boxstyle="round,pad=0.02,rounding_size=2",
                              facecolor='none', edgecolor=COLORS['border'],
                              linestyle='--', lw=2)
        ax.add_patch(rect)
        if label:
            ax.text((x1+x2)/2, y2+3, label, ha='center', va='bottom',
                   fontsize=11, fontweight='bold')

    # -------------------------------------------------------------------------
    # Configuration 1: Non-hybrid
    # -------------------------------------------------------------------------
    ax1 = axes[0]
    ax1.set_title('Non-hybrid', fontsize=12, fontweight='bold', pad=10)

    # Grid connection
    draw_grid_icon(ax1, 50, 85)

    # Connection point
    ax1.plot(50, 72, 'ko', markersize=8)
    ax1.plot([50, 50], [77, 72], color=COLORS['ac_line'], lw=2)

    # Split to two paths
    ax1.plot([50, 30], [72, 72], color=COLORS['ac_line'], lw=2)
    ax1.plot([50, 70], [72, 72], color=COLORS['ac_line'], lw=2)
    ax1.plot([30, 30], [72, 55], color=COLORS['ac_line'], lw=2)
    ax1.plot([70, 70], [72, 55], color=COLORS['ac_line'], lw=2)

    # Inverters
    draw_inverter(ax1, 30, 48)
    draw_inverter(ax1, 70, 48)

    # DC connections (pink)
    ax1.plot([30, 30], [40, 25], color=COLORS['dc_line'], lw=2)
    ax1.plot([70, 70], [40, 25], color=COLORS['dc_line'], lw=2)

    # Solar panel and battery
    draw_solar_panel(ax1, 30, 15)
    draw_battery(ax1, 70, 15)

    # DUID labels
    ax1.text(30, 2, 'DUID 1', ha='center', fontsize=9, fontweight='bold')
    ax1.text(70, 2, 'DUID 2', ha='center', fontsize=9, fontweight='bold')

    # Dashed borders
    draw_dashed_border(ax1, 12, 5, 48, 68)
    draw_dashed_border(ax1, 52, 5, 88, 68)

    # Row labels
    ax1.text(3, 85, 'Grid connection', fontsize=8, va='center')
    ax1.text(3, 48, 'Inverter', fontsize=8, va='center')
    ax1.text(3, 15, 'Solar/battery', fontsize=8, va='center')

    # -------------------------------------------------------------------------
    # Configuration 2: AC-coupled hybrid
    # -------------------------------------------------------------------------
    ax2 = axes[1]
    ax2.set_title('AC-coupled hybrid', fontsize=12, fontweight='bold', pad=10)

    # Grid connection
    draw_grid_icon(ax2, 50, 85)

    # Connection point
    ax2.plot(50, 72, 'ko', markersize=8)
    ax2.plot([50, 50], [77, 72], color=COLORS['ac_line'], lw=2)

    # Single path down then split
    ax2.plot([50, 50], [72, 60], color=COLORS['ac_line'], lw=2)
    ax2.plot([50, 30], [60, 60], color=COLORS['ac_line'], lw=2)
    ax2.plot([50, 70], [60, 60], color=COLORS['ac_line'], lw=2)
    ax2.plot([30, 30], [60, 55], color=COLORS['ac_line'], lw=2)
    ax2.plot([70, 70], [60, 55], color=COLORS['ac_line'], lw=2)

    # Inverters
    draw_inverter(ax2, 30, 48)
    draw_inverter(ax2, 70, 48)

    # DC connections (pink)
    ax2.plot([30, 30], [40, 25], color=COLORS['dc_line'], lw=2)
    ax2.plot([70, 70], [40, 25], color=COLORS['dc_line'], lw=2)

    # Solar panel and battery
    draw_solar_panel(ax2, 30, 15)
    draw_battery(ax2, 70, 15)

    # DUID labels
    ax2.text(30, 2, 'DUID 1', ha='center', fontsize=9, fontweight='bold')
    ax2.text(70, 2, 'DUID 2', ha='center', fontsize=9, fontweight='bold')

    # Single dashed border
    draw_dashed_border(ax2, 12, 5, 88, 68)

    # -------------------------------------------------------------------------
    # Configuration 3: DC-coupled hybrid
    # -------------------------------------------------------------------------
    ax3 = axes[2]
    ax3.set_title('DC-coupled hybrid', fontsize=12, fontweight='bold', pad=10)

    # Grid connection
    draw_grid_icon(ax3, 50, 85)

    # Connection point
    ax3.plot(50, 72, 'ko', markersize=8)
    ax3.plot([50, 50], [77, 72], color=COLORS['ac_line'], lw=2)

    # Single AC path to inverter
    ax3.plot([50, 50], [72, 55], color=COLORS['ac_line'], lw=2)

    # Single inverter
    draw_inverter(ax3, 50, 48)

    # DC connections (pink) - split after inverter
    ax3.plot([50, 50], [40, 35], color=COLORS['dc_line'], lw=2)
    ax3.plot([50, 30], [35, 35], color=COLORS['dc_line'], lw=2)
    ax3.plot([50, 70], [35, 35], color=COLORS['dc_line'], lw=2)
    ax3.plot([30, 30], [35, 25], color=COLORS['dc_line'], lw=2)
    ax3.plot([70, 70], [35, 25], color=COLORS['dc_line'], lw=2)

    # Solar panel and battery
    draw_solar_panel(ax3, 30, 15)
    draw_battery(ax3, 70, 15)

    # Single DUID label
    ax3.text(50, 2, 'Single DUID', ha='center', fontsize=9, fontweight='bold')

    # Single dashed border
    draw_dashed_border(ax3, 12, 5, 88, 68)

    plt.tight_layout()

    # Save outputs
    output_path = get_output_path("section3", "bess_diagram_matplotlib")
    fig.savefig(f"{output_path}.png", dpi=150, bbox_inches='tight',
                facecolor='white', edgecolor='none')
    fig.savefig(f"{output_path}.svg", bbox_inches='tight',
                facecolor='white', edgecolor='none')

    print(f"✓ Saved: {output_path}.png")
    print(f"✓ Saved: {output_path}.svg")

    plt.close()
    return output_path


# ==============================================================================
# OPTION 2: Improved Graphviz Diagram
# ==============================================================================
def create_graphviz_diagram():
    """Create diagram using Graphviz with custom HTML-like nodes."""
    print("\n" + "-" * 40)
    print("Option 2: Graphviz Diagram")
    print("-" * 40)

    try:
        from graphviz import Digraph
    except ImportError:
        print("✗ graphviz not installed")
        return None

    # Create main diagram
    dot = Digraph(name='bess_colocation', format='svg', engine='neato')
    dot.attr(bgcolor='white', pad='0.5', fontname='Arial')
    dot.attr('node', fontname='Arial', fontsize='10')
    dot.attr('edge', fontname='Arial')

    # Title
    dot.attr(label='Indicative diagrams of co-located battery and renewable generation',
             labelloc='t', fontsize='14', fontweight='bold')

    # Define positions for neato layout
    configs = [
        ('non_hybrid', 0, 'Non-hybrid'),
        ('ac_coupled', 4, 'AC-coupled hybrid'),
        ('dc_coupled', 8, 'DC-coupled hybrid')
    ]

    for prefix, x_offset, title in configs:
        # Grid connection (top)
        dot.node(f'{prefix}_grid', '⚡\nGrid',
                shape='none', pos=f'{x_offset},4!')

        # Inverters
        if prefix == 'dc_coupled':
            # Single inverter for DC-coupled
            dot.node(f'{prefix}_inv', '▭\nInverter',
                    shape='box', style='filled', fillcolor='#ffeb3b',
                    pos=f'{x_offset},2!')
        else:
            # Two inverters for non-hybrid and AC-coupled
            dot.node(f'{prefix}_inv1', '▭',
                    shape='box', style='filled', fillcolor='#ffeb3b',
                    pos=f'{x_offset-0.8},2!')
            dot.node(f'{prefix}_inv2', '▭',
                    shape='box', style='filled', fillcolor='#ffeb3b',
                    pos=f'{x_offset+0.8},2!')

        # Solar and Battery
        dot.node(f'{prefix}_solar', '☀️\nSolar',
                shape='none', pos=f'{x_offset-0.8},0!')
        dot.node(f'{prefix}_batt', '🔋\nBattery',
                shape='none', pos=f'{x_offset+0.8},0!')

        # Title label
        dot.node(f'{prefix}_title', title,
                shape='none', fontsize='11', fontweight='bold',
                pos=f'{x_offset},5!')

        # DUID labels
        if prefix == 'dc_coupled':
            dot.node(f'{prefix}_duid', 'Single DUID',
                    shape='none', fontsize='9', pos=f'{x_offset},-1!')
        else:
            dot.node(f'{prefix}_duid1', 'DUID 1',
                    shape='none', fontsize='9', pos=f'{x_offset-0.8},-1!')
            dot.node(f'{prefix}_duid2', 'DUID 2',
                    shape='none', fontsize='9', pos=f'{x_offset+0.8},-1!')

    # Add edges (connections)
    # Non-hybrid
    dot.edge('non_hybrid_grid', 'non_hybrid_inv1', color='black', penwidth='2')
    dot.edge('non_hybrid_grid', 'non_hybrid_inv2', color='black', penwidth='2')
    dot.edge('non_hybrid_inv1', 'non_hybrid_solar', color='#e91e63', penwidth='2')
    dot.edge('non_hybrid_inv2', 'non_hybrid_batt', color='#e91e63', penwidth='2')

    # AC-coupled
    dot.edge('ac_coupled_grid', 'ac_coupled_inv1', color='black', penwidth='2')
    dot.edge('ac_coupled_grid', 'ac_coupled_inv2', color='black', penwidth='2')
    dot.edge('ac_coupled_inv1', 'ac_coupled_solar', color='#e91e63', penwidth='2')
    dot.edge('ac_coupled_inv2', 'ac_coupled_batt', color='#e91e63', penwidth='2')

    # DC-coupled
    dot.edge('dc_coupled_grid', 'dc_coupled_inv', color='black', penwidth='2')
    dot.edge('dc_coupled_inv', 'dc_coupled_solar', color='#e91e63', penwidth='2')
    dot.edge('dc_coupled_inv', 'dc_coupled_batt', color='#e91e63', penwidth='2')

    output_path = get_output_path("section3", "bess_diagram_graphviz")
    dot.render(str(output_path), cleanup=True)

    print(f"✓ Saved: {output_path}.svg")
    return output_path


# ==============================================================================
# OPTION 3: Schemdraw Electrical Diagram
# ==============================================================================
def create_schemdraw_diagram():
    """Create diagram using Schemdraw for electrical schematic style."""
    print("\n" + "-" * 40)
    print("Option 3: Schemdraw Diagram")
    print("-" * 40)

    try:
        import schemdraw
        import schemdraw.elements as elm
        from schemdraw import Drawing
    except ImportError:
        print("✗ schemdraw not installed. Install with: pip install schemdraw")
        return None

    import matplotlib.pyplot as plt

    # Create figure with three separate schemdraw drawings
    fig, axes = plt.subplots(1, 3, figsize=(16, 8))
    fig.suptitle('Indicative diagrams of co-located battery and renewable generation',
                 fontsize=14, fontweight='bold')

    # -------------------------------------------------------------------------
    # Non-hybrid configuration
    # -------------------------------------------------------------------------
    with schemdraw.Drawing(canvas=axes[0], show=False) as d:
        d.config(unit=2, fontsize=10)

        # Title
        d += elm.Label().at((3, 8)).label('Non-hybrid')

        # Grid connection
        d += elm.Line().at((3, 7)).down().length(0.5).color('black')
        d += elm.Dot()

        # Split to two branches
        d += elm.Line().left().length(1.5).color('black')
        d += elm.Line().right().at((3, 6.5)).length(1.5).color('black')

        # Left branch - PV
        d += elm.Line().at((1.5, 6.5)).down().length(1).color('black')
        d += elm.RBox(w=1.5, h=0.8).anchor('N').label('INV').fill('#ffeb3b')
        d += elm.Line().down().length(1).color('#e91e63')
        d += elm.RBox(w=1.2, h=0.8).anchor('N').label('PV')
        d += elm.Label().at((1.5, 2.5)).label('DUID 1')

        # Right branch - Battery
        d += elm.Line().at((4.5, 6.5)).down().length(1).color('black')
        d += elm.RBox(w=1.5, h=0.8).anchor('N').label('INV').fill('#ffeb3b')
        d += elm.Line().down().length(1).color('#e91e63')
        d += elm.Battery().anchor('N').label('BESS')
        d += elm.Label().at((4.5, 2.5)).label('DUID 2')

    # -------------------------------------------------------------------------
    # AC-coupled configuration
    # -------------------------------------------------------------------------
    with schemdraw.Drawing(canvas=axes[1], show=False) as d:
        d.config(unit=2, fontsize=10)

        # Title
        d += elm.Label().at((3, 8)).label('AC-coupled hybrid')

        # Grid connection
        d += elm.Line().at((3, 7)).down().length(1).color('black')
        d += elm.Dot()

        # Split to two branches (AC bus)
        d += elm.Line().left().length(1.5).color('black')
        d += elm.Line().right().at((3, 6)).length(1.5).color('black')

        # Left branch - PV
        d += elm.Line().at((1.5, 6)).down().length(0.5).color('black')
        d += elm.RBox(w=1.5, h=0.8).anchor('N').label('INV').fill('#ffeb3b')
        d += elm.Line().down().length(1).color('#e91e63')
        d += elm.RBox(w=1.2, h=0.8).anchor('N').label('PV')
        d += elm.Label().at((1.5, 2.5)).label('DUID 1')

        # Right branch - Battery
        d += elm.Line().at((4.5, 6)).down().length(0.5).color('black')
        d += elm.RBox(w=1.5, h=0.8).anchor('N').label('INV').fill('#ffeb3b')
        d += elm.Line().down().length(1).color('#e91e63')
        d += elm.Battery().anchor('N').label('BESS')
        d += elm.Label().at((4.5, 2.5)).label('DUID 2')

    # -------------------------------------------------------------------------
    # DC-coupled configuration
    # -------------------------------------------------------------------------
    with schemdraw.Drawing(canvas=axes[2], show=False) as d:
        d.config(unit=2, fontsize=10)

        # Title
        d += elm.Label().at((3, 8)).label('DC-coupled hybrid')

        # Grid connection
        d += elm.Line().at((3, 7)).down().length(1.5).color('black')

        # Single inverter
        d += elm.RBox(w=1.5, h=0.8).anchor('N').label('INV').fill('#ffeb3b')
        d += elm.Line().down().length(0.5).color('#e91e63')
        d += elm.Dot()

        # Split to PV and Battery (DC side)
        d += elm.Line().left().length(1.5).color('#e91e63')
        d += elm.Line().right().at((3, 4.5)).length(1.5).color('#e91e63')

        # PV
        d += elm.Line().at((1.5, 4.5)).down().length(1).color('#e91e63')
        d += elm.RBox(w=1.2, h=0.8).anchor('N').label('PV')

        # Battery
        d += elm.Line().at((4.5, 4.5)).down().length(1).color('#e91e63')
        d += elm.Battery().anchor('N').label('BESS')

        # Single DUID label
        d += elm.Label().at((3, 2.5)).label('Single DUID')

    plt.tight_layout()

    output_path = get_output_path("section3", "bess_diagram_schemdraw")
    fig.savefig(f"{output_path}.png", dpi=150, bbox_inches='tight',
                facecolor='white', edgecolor='none')
    fig.savefig(f"{output_path}.svg", bbox_inches='tight',
                facecolor='white', edgecolor='none')

    print(f"✓ Saved: {output_path}.png")
    print(f"✓ Saved: {output_path}.svg")

    plt.close()
    return output_path


# ==============================================================================
# OPTION 4: Pure SVG/HTML Diagram
# ==============================================================================
def create_svg_diagram():
    """Create diagram using pure SVG for maximum control and web embedding."""
    print("\n" + "-" * 40)
    print("Option 4: SVG/HTML Diagram")
    print("-" * 40)

    svg_content = '''<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 900 450" width="900" height="450">
  <style>
    .title { font: bold 16px Arial, sans-serif; fill: #333; }
    .subtitle { font: bold 13px Arial, sans-serif; fill: #333; }
    .label { font: 11px Arial, sans-serif; fill: #333; }
    .duid-label { font: bold 10px Arial, sans-serif; fill: #333; }
    .row-label { font: 10px Arial, sans-serif; fill: #666; }
    .ac-line { stroke: #1a1a1a; stroke-width: 2; fill: none; }
    .dc-line { stroke: #e91e63; stroke-width: 2; fill: none; }
    .border { stroke: #3f51b5; stroke-width: 2; stroke-dasharray: 8,4; fill: none; rx: 8; }
    .inverter { fill: #ffeb3b; stroke: #333; stroke-width: 1.5; }
    .component { fill: white; stroke: #333; stroke-width: 1.5; }
  </style>

  <!-- Title -->
  <text x="450" y="30" text-anchor="middle" class="title">Indicative diagrams of co-located battery and renewable generation</text>

  <!-- Row Labels -->
  <text x="30" y="90" class="row-label">Grid connection</text>
  <text x="30" y="200" class="row-label">Inverter</text>
  <text x="30" y="320" class="row-label">Solar/battery</text>

  <!-- ========== NON-HYBRID ========== -->
  <g id="non-hybrid" transform="translate(150, 50)">
    <text x="75" y="0" text-anchor="middle" class="subtitle">Non-hybrid</text>

    <!-- Grid Icon (Transmission Tower) -->
    <g transform="translate(75, 35)">
      <line x1="0" y1="-15" x2="0" y2="15" stroke="#333" stroke-width="2"/>
      <line x1="-12" y1="-8" x2="12" y2="-8" stroke="#333" stroke-width="2"/>
      <line x1="-8" y1="2" x2="8" y2="2" stroke="#333" stroke-width="2"/>
      <line x1="-12" y1="-8" x2="-18" y2="-8" stroke="#333" stroke-width="1.5"/>
      <line x1="12" y1="-8" x2="18" y2="-8" stroke="#333" stroke-width="1.5"/>
    </g>

    <!-- Connection point -->
    <circle cx="75" cy="70" r="4" fill="#333"/>
    <line x1="75" y1="50" x2="75" y2="70" class="ac-line"/>

    <!-- Split to two paths -->
    <line x1="75" y1="70" x2="30" y2="70" class="ac-line"/>
    <line x1="75" y1="70" x2="120" y2="70" class="ac-line"/>
    <line x1="30" y1="70" x2="30" y2="130" class="ac-line"/>
    <line x1="120" y1="70" x2="120" y2="130" class="ac-line"/>

    <!-- Inverters -->
    <rect x="10" y="130" width="40" height="30" rx="3" class="inverter"/>
    <rect x="100" y="130" width="40" height="30" rx="3" class="inverter"/>

    <!-- DC connections -->
    <line x1="30" y1="160" x2="30" y2="220" class="dc-line"/>
    <line x1="120" y1="160" x2="120" y2="220" class="dc-line"/>

    <!-- Solar Panel -->
    <g transform="translate(30, 250)">
      <rect x="-20" y="-20" width="40" height="30" class="component"/>
      <line x1="-20" y1="-5" x2="20" y2="-5" stroke="#333" stroke-width="0.5"/>
      <line x1="-7" y1="-20" x2="-7" y2="10" stroke="#333" stroke-width="0.5"/>
      <line x1="7" y1="-20" x2="7" y2="10" stroke="#333" stroke-width="0.5"/>
      <line x1="0" y1="10" x2="0" y2="25" stroke="#333" stroke-width="1.5"/>
      <line x1="-10" y1="25" x2="10" y2="25" stroke="#333" stroke-width="1.5"/>
    </g>

    <!-- Battery -->
    <g transform="translate(120, 250)">
      <rect x="-15" y="-25" width="30" height="45" class="component"/>
      <rect x="-6" y="-30" width="12" height="5" class="component"/>
      <rect x="-11" y="-18" width="22" height="10" fill="#e0e0e0"/>
      <rect x="-11" y="-5" width="22" height="10" fill="#e0e0e0"/>
      <rect x="-11" y="8" width="22" height="10" fill="#e0e0e0"/>
    </g>

    <!-- Dashed borders -->
    <rect x="-5" y="85" width="70" height="220" class="border"/>
    <rect x="85" y="85" width="70" height="220" class="border"/>

    <!-- DUID labels -->
    <text x="30" y="340" text-anchor="middle" class="duid-label">DUID 1</text>
    <text x="120" y="340" text-anchor="middle" class="duid-label">DUID 2</text>
  </g>

  <!-- ========== AC-COUPLED HYBRID ========== -->
  <g id="ac-coupled" transform="translate(400, 50)">
    <text x="75" y="0" text-anchor="middle" class="subtitle">AC-coupled hybrid</text>

    <!-- Grid Icon -->
    <g transform="translate(75, 35)">
      <line x1="0" y1="-15" x2="0" y2="15" stroke="#333" stroke-width="2"/>
      <line x1="-12" y1="-8" x2="12" y2="-8" stroke="#333" stroke-width="2"/>
      <line x1="-8" y1="2" x2="8" y2="2" stroke="#333" stroke-width="2"/>
      <line x1="-12" y1="-8" x2="-18" y2="-8" stroke="#333" stroke-width="1.5"/>
      <line x1="12" y1="-8" x2="18" y2="-8" stroke="#333" stroke-width="1.5"/>
    </g>

    <!-- Connection point -->
    <circle cx="75" cy="70" r="4" fill="#333"/>
    <line x1="75" y1="50" x2="75" y2="70" class="ac-line"/>

    <!-- Single path then split at AC bus -->
    <line x1="75" y1="70" x2="75" y2="100" class="ac-line"/>
    <line x1="30" y1="100" x2="120" y2="100" class="ac-line"/>
    <line x1="30" y1="100" x2="30" y2="130" class="ac-line"/>
    <line x1="120" y1="100" x2="120" y2="130" class="ac-line"/>

    <!-- Inverters -->
    <rect x="10" y="130" width="40" height="30" rx="3" class="inverter"/>
    <rect x="100" y="130" width="40" height="30" rx="3" class="inverter"/>

    <!-- DC connections -->
    <line x1="30" y1="160" x2="30" y2="220" class="dc-line"/>
    <line x1="120" y1="160" x2="120" y2="220" class="dc-line"/>

    <!-- Solar Panel -->
    <g transform="translate(30, 250)">
      <rect x="-20" y="-20" width="40" height="30" class="component"/>
      <line x1="-20" y1="-5" x2="20" y2="-5" stroke="#333" stroke-width="0.5"/>
      <line x1="-7" y1="-20" x2="-7" y2="10" stroke="#333" stroke-width="0.5"/>
      <line x1="7" y1="-20" x2="7" y2="10" stroke="#333" stroke-width="0.5"/>
      <line x1="0" y1="10" x2="0" y2="25" stroke="#333" stroke-width="1.5"/>
      <line x1="-10" y1="25" x2="10" y2="25" stroke="#333" stroke-width="1.5"/>
    </g>

    <!-- Battery -->
    <g transform="translate(120, 250)">
      <rect x="-15" y="-25" width="30" height="45" class="component"/>
      <rect x="-6" y="-30" width="12" height="5" class="component"/>
      <rect x="-11" y="-18" width="22" height="10" fill="#e0e0e0"/>
      <rect x="-11" y="-5" width="22" height="10" fill="#e0e0e0"/>
      <rect x="-11" y="8" width="22" height="10" fill="#e0e0e0"/>
    </g>

    <!-- Single dashed border -->
    <rect x="-5" y="85" width="160" height="220" class="border"/>

    <!-- DUID labels -->
    <text x="30" y="340" text-anchor="middle" class="duid-label">DUID 1</text>
    <text x="120" y="340" text-anchor="middle" class="duid-label">DUID 2</text>
  </g>

  <!-- ========== DC-COUPLED HYBRID ========== -->
  <g id="dc-coupled" transform="translate(650, 50)">
    <text x="75" y="0" text-anchor="middle" class="subtitle">DC-coupled hybrid</text>

    <!-- Grid Icon -->
    <g transform="translate(75, 35)">
      <line x1="0" y1="-15" x2="0" y2="15" stroke="#333" stroke-width="2"/>
      <line x1="-12" y1="-8" x2="12" y2="-8" stroke="#333" stroke-width="2"/>
      <line x1="-8" y1="2" x2="8" y2="2" stroke="#333" stroke-width="2"/>
      <line x1="-12" y1="-8" x2="-18" y2="-8" stroke="#333" stroke-width="1.5"/>
      <line x1="12" y1="-8" x2="18" y2="-8" stroke="#333" stroke-width="1.5"/>
    </g>

    <!-- Connection point -->
    <circle cx="75" cy="70" r="4" fill="#333"/>
    <line x1="75" y1="50" x2="75" y2="70" class="ac-line"/>

    <!-- Single AC path to inverter -->
    <line x1="75" y1="70" x2="75" y2="130" class="ac-line"/>

    <!-- Single Inverter -->
    <rect x="55" y="130" width="40" height="30" rx="3" class="inverter"/>

    <!-- DC connection splits after inverter -->
    <line x1="75" y1="160" x2="75" y2="190" class="dc-line"/>
    <line x1="30" y1="190" x2="120" y2="190" class="dc-line"/>
    <line x1="30" y1="190" x2="30" y2="220" class="dc-line"/>
    <line x1="120" y1="190" x2="120" y2="220" class="dc-line"/>

    <!-- Solar Panel -->
    <g transform="translate(30, 250)">
      <rect x="-20" y="-20" width="40" height="30" class="component"/>
      <line x1="-20" y1="-5" x2="20" y2="-5" stroke="#333" stroke-width="0.5"/>
      <line x1="-7" y1="-20" x2="-7" y2="10" stroke="#333" stroke-width="0.5"/>
      <line x1="7" y1="-20" x2="7" y2="10" stroke="#333" stroke-width="0.5"/>
      <line x1="0" y1="10" x2="0" y2="25" stroke="#333" stroke-width="1.5"/>
      <line x1="-10" y1="25" x2="10" y2="25" stroke="#333" stroke-width="1.5"/>
    </g>

    <!-- Battery -->
    <g transform="translate(120, 250)">
      <rect x="-15" y="-25" width="30" height="45" class="component"/>
      <rect x="-6" y="-30" width="12" height="5" class="component"/>
      <rect x="-11" y="-18" width="22" height="10" fill="#e0e0e0"/>
      <rect x="-11" y="-5" width="22" height="10" fill="#e0e0e0"/>
      <rect x="-11" y="8" width="22" height="10" fill="#e0e0e0"/>
    </g>

    <!-- Single dashed border -->
    <rect x="-5" y="85" width="160" height="220" class="border"/>

    <!-- Single DUID label -->
    <text x="75" y="340" text-anchor="middle" class="duid-label">Single DUID</text>
  </g>

  <!-- Legend -->
  <g transform="translate(750, 400)">
    <line x1="0" y1="0" x2="30" y2="0" stroke="#1a1a1a" stroke-width="2"/>
    <text x="35" y="4" class="label">AC</text>
    <line x1="60" y1="0" x2="90" y2="0" stroke="#e91e63" stroke-width="2"/>
    <text x="95" y="4" class="label">DC</text>
  </g>
</svg>'''

    output_path = get_output_path("section3", "bess_diagram_svg")

    # Save SVG
    with open(f"{output_path}.svg", 'w') as f:
        f.write(svg_content)

    # Create HTML wrapper for easy embedding
    html_content = f'''<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>BESS Co-location Configurations</title>
    <style>
        body {{
            font-family: Arial, sans-serif;
            margin: 20px;
            background: #f5f5f5;
        }}
        .diagram-container {{
            background: white;
            padding: 20px;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            max-width: 950px;
            margin: 0 auto;
        }}
        svg {{
            width: 100%;
            height: auto;
        }}
    </style>
</head>
<body>
    <div class="diagram-container">
        {svg_content}
    </div>
</body>
</html>'''

    with open(f"{output_path}.html", 'w') as f:
        f.write(html_content)

    print(f"✓ Saved: {output_path}.svg")
    print(f"✓ Saved: {output_path}.html")

    return output_path


# ==============================================================================
# OPTION 5: High-Quality Matplotlib with Professional Icons
# ==============================================================================
def create_matplotlib_professional():
    """Create a more professional Matplotlib diagram with better icons."""
    print("\n" + "-" * 40)
    print("Option 5: Professional Matplotlib Diagram")
    print("-" * 40)

    try:
        import matplotlib.pyplot as plt
        import matplotlib.patches as mpatches
        from matplotlib.patches import FancyBboxPatch, Rectangle, Circle, Polygon, PathPatch
        from matplotlib.path import Path
        import numpy as np
    except ImportError as e:
        print(f"✗ Missing dependency: {e}")
        return None

    fig, axes = plt.subplots(1, 3, figsize=(16, 9))
    fig.patch.set_facecolor('white')
    fig.suptitle('Indicative diagrams of co-located battery and renewable generation',
                 fontsize=15, fontweight='bold', y=0.96)

    for ax in axes:
        ax.set_xlim(0, 100)
        ax.set_ylim(0, 100)
        ax.set_aspect('equal')
        ax.axis('off')
        ax.set_facecolor('white')

    def draw_transmission_tower(ax, x, y, scale=1.0):
        """Draw a more realistic transmission tower icon."""
        color = '#333333'
        lw = 1.5

        # Main structure - lattice tower shape
        # Left leg
        ax.plot([x-4*scale, x-2*scale], [y-10*scale, y+6*scale], color=color, lw=lw)
        # Right leg
        ax.plot([x+4*scale, x+2*scale], [y-10*scale, y+6*scale], color=color, lw=lw)
        # Top
        ax.plot([x-2*scale, x+2*scale], [y+6*scale, y+6*scale], color=color, lw=lw)
        # Cross braces
        ax.plot([x-3*scale, x+3*scale], [y-2*scale, y-2*scale], color=color, lw=lw*0.7)
        ax.plot([x-2.5*scale, x+2.5*scale], [y+2*scale, y+2*scale], color=color, lw=lw*0.7)

        # Cross arms
        ax.plot([x-8*scale, x+8*scale], [y+4*scale, y+4*scale], color=color, lw=lw*1.2)
        ax.plot([x-6*scale, x+6*scale], [y+0*scale, y+0*scale], color=color, lw=lw)

        # Wires hanging from cross arms
        ax.plot([x-8*scale, x-10*scale], [y+4*scale, y+3*scale], color=color, lw=lw*0.8)
        ax.plot([x+8*scale, x+10*scale], [y+4*scale, y+3*scale], color=color, lw=lw*0.8)
        ax.plot([x-6*scale, x-8*scale], [y+0*scale, y-1*scale], color=color, lw=lw*0.8)
        ax.plot([x+6*scale, x+8*scale], [y+0*scale, y-1*scale], color=color, lw=lw*0.8)

    def draw_inverter_box(ax, x, y, width=14, height=10):
        """Draw inverter as a rounded rectangle."""
        rect = FancyBboxPatch((x-width/2, y-height/2), width, height,
                              boxstyle="round,pad=0.02,rounding_size=2",
                              facecolor='#ffeb3b', edgecolor='#333333', lw=1.5)
        ax.add_patch(rect)

    def draw_solar_panel_icon(ax, x, y, scale=1.0):
        """Draw a tilted solar panel icon."""
        color = '#333333'
        lw = 1.5

        # Panel (tilted rectangle)
        panel_pts = [
            (x-8*scale, y-2*scale),
            (x+8*scale, y-2*scale),
            (x+8*scale, y+6*scale),
            (x-8*scale, y+6*scale),
        ]
        panel = Polygon(panel_pts, closed=True, facecolor='white', edgecolor=color, lw=lw)
        ax.add_patch(panel)

        # Grid lines
        for i in range(1, 3):
            ax.plot([x-8*scale + i*5.3*scale, x-8*scale + i*5.3*scale],
                   [y-2*scale, y+6*scale], color=color, lw=0.5)
        ax.plot([x-8*scale, x+8*scale], [y+2*scale, y+2*scale], color=color, lw=0.5)

        # Stand
        ax.plot([x, x], [y-2*scale, y-8*scale], color=color, lw=lw)
        ax.plot([x-5*scale, x+5*scale], [y-8*scale, y-8*scale], color=color, lw=lw)

    def draw_battery_icon(ax, x, y, scale=1.0):
        """Draw a battery icon."""
        color = '#333333'
        lw = 1.5

        # Main body
        rect = Rectangle((x-6*scale, y-8*scale), 12*scale, 16*scale,
                         facecolor='white', edgecolor=color, lw=lw)
        ax.add_patch(rect)

        # Terminal
        rect2 = Rectangle((x-3*scale, y+8*scale), 6*scale, 3*scale,
                          facecolor='white', edgecolor=color, lw=lw)
        ax.add_patch(rect2)

        # Charge level bars
        for i, alpha in enumerate([0.8, 0.6, 0.4]):
            bar = Rectangle((x-4*scale, y-6*scale + i*4.5*scale), 8*scale, 3.5*scale,
                            facecolor=(0.6, 0.6, 0.6, alpha), edgecolor='none')
            ax.add_patch(bar)

    def draw_dashed_box(ax, x1, y1, x2, y2):
        """Draw dashed border."""
        rect = FancyBboxPatch((x1, y1), x2-x1, y2-y1,
                              boxstyle="round,pad=0.02,rounding_size=3",
                              facecolor='none', edgecolor='#3f51b5',
                              linestyle='--', lw=2)
        ax.add_patch(rect)

    # =========================================================================
    # NON-HYBRID
    # =========================================================================
    ax1 = axes[0]
    ax1.set_title('Non-hybrid', fontsize=13, fontweight='bold', pad=15)

    # Grid tower
    draw_transmission_tower(ax1, 50, 85)

    # Connection point and AC lines
    ax1.plot(50, 70, 'ko', markersize=6)
    ax1.plot([50, 50], [75, 70], color=COLORS['ac_line'], lw=2)
    ax1.plot([50, 28], [70, 70], color=COLORS['ac_line'], lw=2)
    ax1.plot([50, 72], [70, 70], color=COLORS['ac_line'], lw=2)
    ax1.plot([28, 28], [70, 52], color=COLORS['ac_line'], lw=2)
    ax1.plot([72, 72], [70, 52], color=COLORS['ac_line'], lw=2)

    # Inverters
    draw_inverter_box(ax1, 28, 45)
    draw_inverter_box(ax1, 72, 45)

    # DC lines (pink)
    ax1.plot([28, 28], [38, 25], color=COLORS['dc_line'], lw=2)
    ax1.plot([72, 72], [38, 25], color=COLORS['dc_line'], lw=2)

    # Solar and battery
    draw_solar_panel_icon(ax1, 28, 15)
    draw_battery_icon(ax1, 72, 14)

    # Dashed boxes
    draw_dashed_box(ax1, 10, 3, 46, 65)
    draw_dashed_box(ax1, 54, 3, 90, 65)

    # Labels
    ax1.text(28, -2, 'DUID 1', ha='center', fontsize=10, fontweight='bold')
    ax1.text(72, -2, 'DUID 2', ha='center', fontsize=10, fontweight='bold')

    # Row labels
    ax1.text(2, 85, 'Grid connection', fontsize=9, va='center', color='#666')
    ax1.text(2, 45, 'Inverter', fontsize=9, va='center', color='#666')
    ax1.text(2, 15, 'Solar/battery', fontsize=9, va='center', color='#666')

    # =========================================================================
    # AC-COUPLED HYBRID
    # =========================================================================
    ax2 = axes[1]
    ax2.set_title('AC-coupled hybrid', fontsize=13, fontweight='bold', pad=15)

    # Grid tower
    draw_transmission_tower(ax2, 50, 85)

    # Connection and AC bus
    ax2.plot(50, 70, 'ko', markersize=6)
    ax2.plot([50, 50], [75, 70], color=COLORS['ac_line'], lw=2)
    ax2.plot([50, 50], [70, 60], color=COLORS['ac_line'], lw=2)
    ax2.plot([28, 72], [60, 60], color=COLORS['ac_line'], lw=2)
    ax2.plot([28, 28], [60, 52], color=COLORS['ac_line'], lw=2)
    ax2.plot([72, 72], [60, 52], color=COLORS['ac_line'], lw=2)

    # Inverters
    draw_inverter_box(ax2, 28, 45)
    draw_inverter_box(ax2, 72, 45)

    # DC lines
    ax2.plot([28, 28], [38, 25], color=COLORS['dc_line'], lw=2)
    ax2.plot([72, 72], [38, 25], color=COLORS['dc_line'], lw=2)

    # Solar and battery
    draw_solar_panel_icon(ax2, 28, 15)
    draw_battery_icon(ax2, 72, 14)

    # Single dashed box
    draw_dashed_box(ax2, 10, 3, 90, 65)

    # Labels
    ax2.text(28, -2, 'DUID 1', ha='center', fontsize=10, fontweight='bold')
    ax2.text(72, -2, 'DUID 2', ha='center', fontsize=10, fontweight='bold')

    # =========================================================================
    # DC-COUPLED HYBRID
    # =========================================================================
    ax3 = axes[2]
    ax3.set_title('DC-coupled hybrid', fontsize=13, fontweight='bold', pad=15)

    # Grid tower
    draw_transmission_tower(ax3, 50, 85)

    # Connection to single inverter
    ax3.plot(50, 70, 'ko', markersize=6)
    ax3.plot([50, 50], [75, 70], color=COLORS['ac_line'], lw=2)
    ax3.plot([50, 50], [70, 52], color=COLORS['ac_line'], lw=2)

    # Single inverter
    draw_inverter_box(ax3, 50, 45)

    # DC bus and splits
    ax3.plot([50, 50], [38, 32], color=COLORS['dc_line'], lw=2)
    ax3.plot([28, 72], [32, 32], color=COLORS['dc_line'], lw=2)
    ax3.plot([28, 28], [32, 25], color=COLORS['dc_line'], lw=2)
    ax3.plot([72, 72], [32, 25], color=COLORS['dc_line'], lw=2)

    # Solar and battery
    draw_solar_panel_icon(ax3, 28, 15)
    draw_battery_icon(ax3, 72, 14)

    # Single dashed box
    draw_dashed_box(ax3, 10, 3, 90, 65)

    # Single DUID label
    ax3.text(50, -2, 'Single DUID', ha='center', fontsize=10, fontweight='bold')

    # =========================================================================
    # Legend
    # =========================================================================
    legend_elements = [
        plt.Line2D([0], [0], color=COLORS['ac_line'], lw=2, label='AC'),
        plt.Line2D([0], [0], color=COLORS['dc_line'], lw=2, label='DC'),
    ]
    fig.legend(handles=legend_elements, loc='lower right',
               bbox_to_anchor=(0.95, 0.02), ncol=2, fontsize=10)

    plt.tight_layout(rect=[0, 0.03, 1, 0.95])

    output_path = get_output_path("section3", "bess_diagram_professional")
    fig.savefig(f"{output_path}.png", dpi=200, bbox_inches='tight',
                facecolor='white', edgecolor='none')
    fig.savefig(f"{output_path}.svg", bbox_inches='tight',
                facecolor='white', edgecolor='none')

    print(f"✓ Saved: {output_path}.png")
    print(f"✓ Saved: {output_path}.svg")

    plt.close()
    return output_path


# ==============================================================================
# MAIN EXECUTION
# ==============================================================================
if __name__ == "__main__":
    results = {}

    # Run all diagram generators
    print("\nGenerating all diagram options...\n")

    # Option 1: Basic Matplotlib
    try:
        results['matplotlib'] = create_matplotlib_diagram()
    except Exception as e:
        print(f"✗ Matplotlib diagram failed: {e}")
        results['matplotlib'] = None

    # Option 2: Graphviz
    try:
        results['graphviz'] = create_graphviz_diagram()
    except Exception as e:
        print(f"✗ Graphviz diagram failed: {e}")
        results['graphviz'] = None

    # Option 3: Schemdraw
    try:
        results['schemdraw'] = create_schemdraw_diagram()
    except Exception as e:
        print(f"✗ Schemdraw diagram failed: {e}")
        results['schemdraw'] = None

    # Option 4: SVG
    try:
        results['svg'] = create_svg_diagram()
    except Exception as e:
        print(f"✗ SVG diagram failed: {e}")
        results['svg'] = None

    # Option 5: Professional Matplotlib
    try:
        results['professional'] = create_matplotlib_professional()
    except Exception as e:
        print(f"✗ Professional Matplotlib diagram failed: {e}")
        results['professional'] = None

    # Summary
    print("\n" + "=" * 80)
    print("SUMMARY")
    print("=" * 80)

    print("\nGenerated diagrams:")
    for name, path in results.items():
        if path:
            print(f"  ✓ {name.capitalize()}: {path}")
        else:
            print(f"  ✗ {name.capitalize()}: Failed")

    print("\nRecommendations:")
    print("  • Option 4 (SVG): Best for web embedding, most faithful to original")
    print("  • Option 5 (Professional): Best for print/presentations")
    print("  • Option 1 (Matplotlib): Good balance of quality and customization")
    print("  • Option 2 (Graphviz): Best for automated layouts")
    print("  • Option 3 (Schemdraw): Best for electrical engineering context")

    print("\n" + "=" * 80)
