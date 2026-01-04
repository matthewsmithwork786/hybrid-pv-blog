"""
Section 3 Analysis: Co-location Configuration Diagram

Generates electrical schematic diagram showing three battery co-location options:
1. Non-hybrid: Separate grid connections
2. AC-coupled: Shared grid connection, separate DUIDs
3. DC-coupled: Single DUID, behind-the-meter

Uses graphviz to create professional electrical diagram.

Output: data/outputs/section3/colocation_diagram.svg
"""

import sys
from pathlib import Path

# Add utils to path
sys.path.append(str(Path(__file__).parent.parent / "utils"))

from data_paths import get_output_path

# Check if graphviz is available
try:
    from graphviz import Digraph
    GRAPHVIZ_AVAILABLE = True
except ImportError:
    GRAPHVIZ_AVAILABLE = False
    print("\n✗ graphviz not installed. Installing...")

if not GRAPHVIZ_AVAILABLE:
    import subprocess
    subprocess.run([sys.executable, "-m", "pip", "install", "graphviz"], check=True)
    from graphviz import Digraph

print("=" * 80)
print("Section 3: Co-location Configuration Diagram")
print("=" * 80)

# ============================================================================
# Create Non-Hybrid Configuration
# ============================================================================

print("\nCreating Non-Hybrid configuration diagram...")

non_hybrid = Digraph(name='non_hybrid', format='svg')
non_hybrid.attr(rankdir='LR', splines='ortho', nodesep='0.5', ranksep='1.0')
non_hybrid.attr('node', shape='box', style='rounded,filled', fillcolor='#FFFACD', fontname='Lato')
non_hybrid.attr('edge', fontname='Lato', fontsize='10')

# Add components
non_hybrid.node('PV', 'Solar PV\nArray', fillcolor='#FFD700')
non_hybrid.node('PV_INV', 'PV Inverter', fillcolor='#E8E8E8')
non_hybrid.node('GRID1', 'Grid Connection 1\n(PV DUID)', shape='doublecircle', fillcolor='#90EE90')

non_hybrid.node('BESS', 'Battery\nStorage', fillcolor='#DDA0DD')
non_hybrid.node('BESS_INV', 'Battery Inverter', fillcolor='#E8E8E8')
non_hybrid.node('GRID2', 'Grid Connection 2\n(Battery DUID)', shape='doublecircle', fillcolor='#90EE90')

# Add connections
non_hybrid.edge('PV', 'PV_INV', label='DC')
non_hybrid.edge('PV_INV', 'GRID1', label='AC')
non_hybrid.edge('BESS', 'BESS_INV', label='DC')
non_hybrid.edge('BESS_INV', 'GRID2', label='AC')

# Add label
non_hybrid.attr(label='Non-Hybrid\n\n• Separate grid connections\n• Dual MLFs\n• Independent dispatch\n• Two approval processes',
               labelloc='b', fontsize='12', fontname='Lato')

# ============================================================================
# Create AC-Coupled Configuration
# ============================================================================

print("Creating AC-Coupled configuration diagram...")

ac_coupled = Digraph(name='ac_coupled', format='svg')
ac_coupled.attr(rankdir='LR', splines='ortho', nodesep='0.5', ranksep='1.0')
ac_coupled.attr('node', shape='box', style='rounded,filled', fillcolor='#FFFACD', fontname='Lato')
ac_coupled.attr('edge', fontname='Lato', fontsize='10')

# Add components
ac_coupled.node('PV', 'Solar PV\nArray', fillcolor='#FFD700')
ac_coupled.node('PV_INV', 'PV Inverter', fillcolor='#E8E8E8')

ac_coupled.node('AC_BUS', 'AC Bus', shape='box', style='filled', fillcolor='#FFA500')

ac_coupled.node('BESS', 'Battery\nStorage', fillcolor='#DDA0DD')
ac_coupled.node('BESS_INV', 'Battery Inverter', fillcolor='#E8E8E8')

ac_coupled.node('GRID', 'Shared Grid\nConnection', shape='doublecircle', fillcolor='#90EE90')

# Add connections
ac_coupled.edge('PV', 'PV_INV', label='DC')
ac_coupled.edge('PV_INV', 'AC_BUS', label='AC')
ac_coupled.edge('BESS', 'BESS_INV', label='DC')
ac_coupled.edge('BESS_INV', 'AC_BUS', label='AC')
ac_coupled.edge('AC_BUS', 'GRID', label='AC')

# Add label
ac_coupled.attr(label='AC-Coupled\n\n• Shared connection\n• Separate PV & Battery DUIDs\n• Independent DC systems\n• Can charge from grid',
               labelloc='b', fontsize='12', fontname='Lato')

# ============================================================================
# Create DC-Coupled Configuration
# ============================================================================

print("Creating DC-Coupled configuration diagram...")

dc_coupled = Digraph(name='dc_coupled', format='svg')
dc_coupled.attr(rankdir='LR', splines='ortho', nodesep='0.5', ranksep='1.0')
dc_coupled.attr('node', shape='box', style='rounded,filled', fillcolor='#FFFACD', fontname='Lato')
dc_coupled.attr('edge', fontname='Lato', fontsize='10')

# Add components
dc_coupled.node('PV', 'Solar PV\nArray', fillcolor='#FFD700')

dc_coupled.node('DC_BUS', 'DC Bus', shape='box', style='filled', fillcolor='#FFA500')

dc_coupled.node('BESS', 'Battery\nStorage', fillcolor='#DDA0DD')

dc_coupled.node('SHARED_INV', 'Shared Inverter', fillcolor='#E8E8E8')

dc_coupled.node('GRID', 'Grid Connection\n(Single DUID)', shape='doublecircle', fillcolor='#90EE90')

# Add connections
dc_coupled.edge('PV', 'DC_BUS', label='DC')
dc_coupled.edge('BESS', 'DC_BUS', label='DC')
dc_coupled.edge('DC_BUS', 'SHARED_INV', label='DC')
dc_coupled.edge('SHARED_INV', 'GRID', label='AC')

# Add label
dc_coupled.attr(label='DC-Coupled\n\n• Single DUID\n• Behind-the-meter\n• Highest efficiency\n• Limited grid charging',
               labelloc='b', fontsize='12', fontname='Lato')

# ============================================================================
# Combine into Single Diagram
# ============================================================================

print("\nCombining diagrams...")

# Create master diagram with three subgraphs
master = Digraph(name='colocation_options', format='svg', engine='dot')
master.attr(rankdir='TB', splines='ortho', nodesep='0.8', ranksep='1.5')
master.attr('graph', fontname='Lato', fontsize='14')

# Title
master.attr(
    label='Battery Co-location Configuration Options\n\nThree approaches to integrating battery storage with solar PV',
    labelloc='t',
    fontsize='18',
    fontname='Lato'
)

# Add subgraphs
with master.subgraph(name='cluster_0') as c:
    c.attr(label='Non-Hybrid Configuration', fontsize='14', style='rounded', color='gray')
    c.node('NH_PV', 'Solar PV\nArray', fillcolor='#FFD700', style='rounded,filled', fontname='Lato')
    c.node('NH_PV_INV', 'PV Inverter', fillcolor='#E8E8E8', style='rounded,filled', fontname='Lato')
    c.node('NH_GRID1', 'Grid\nConnection 1', shape='circle', fillcolor='#90EE90', style='filled', fontname='Lato')
    c.node('NH_BESS', 'Battery\nStorage', fillcolor='#DDA0DD', style='rounded,filled', fontname='Lato')
    c.node('NH_BESS_INV', 'Battery\nInverter', fillcolor='#E8E8E8', style='rounded,filled', fontname='Lato')
    c.node('NH_GRID2', 'Grid\nConnection 2', shape='circle', fillcolor='#90EE90', style='filled', fontname='Lato')
    c.edge('NH_PV', 'NH_PV_INV', label='DC')
    c.edge('NH_PV_INV', 'NH_GRID1', label='AC')
    c.edge('NH_BESS', 'NH_BESS_INV', label='DC')
    c.edge('NH_BESS_INV', 'NH_GRID2', label='AC')
    c.node('NH_LABEL', '• Max flexibility\n• Dual MLFs\n• Independent dispatch\n• Two approvals',
           shape='plaintext', fontname='Lato', fontsize='11')

with master.subgraph(name='cluster_1') as c:
    c.attr(label='AC-Coupled Configuration', fontsize='14', style='rounded', color='gray')
    c.node('AC_PV', 'Solar PV\nArray', fillcolor='#FFD700', style='rounded,filled', fontname='Lato')
    c.node('AC_PV_INV', 'PV Inverter', fillcolor='#E8E8E8', style='rounded,filled', fontname='Lato')
    c.node('AC_BUS', 'AC Bus', fillcolor='#FFA500', style='filled', fontname='Lato')
    c.node('AC_BESS', 'Battery\nStorage', fillcolor='#DDA0DD', style='rounded,filled', fontname='Lato')
    c.node('AC_BESS_INV', 'Battery\nInverter', fillcolor='#E8E8E8', style='rounded,filled', fontname='Lato')
    c.node('AC_GRID', 'Shared Grid\nConnection', shape='circle', fillcolor='#90EE90', style='filled', fontname='Lato')
    c.edge('AC_PV', 'AC_PV_INV', label='DC')
    c.edge('AC_PV_INV', 'AC_BUS', label='AC')
    c.edge('AC_BESS', 'AC_BESS_INV', label='DC')
    c.edge('AC_BESS_INV', 'AC_BUS', label='AC')
    c.edge('AC_BUS', 'AC_GRID', label='AC')
    c.node('AC_LABEL', '• Shared connection\n• Separate DUIDs\n• Independent DC\n• Can charge from grid',
           shape='plaintext', fontname='Lato', fontsize='11')

with master.subgraph(name='cluster_2') as c:
    c.attr(label='DC-Coupled Configuration', fontsize='14', style='rounded', color='gray')
    c.node('DC_PV', 'Solar PV\nArray', fillcolor='#FFD700', style='rounded,filled', fontname='Lato')
    c.node('DC_BUS', 'DC Bus', fillcolor='#FFA500', style='filled', fontname='Lato')
    c.node('DC_BESS', 'Battery\nStorage', fillcolor='#DDA0DD', style='rounded,filled', fontname='Lato')
    c.node('DC_INV', 'Shared\nInverter', fillcolor='#E8E8E8', style='rounded,filled', fontname='Lato')
    c.node('DC_GRID', 'Grid\nConnection', shape='circle', fillcolor='#90EE90', style='filled', fontname='Lato')
    c.edge('DC_PV', 'DC_BUS', label='DC')
    c.edge('DC_BESS', 'DC_BUS', label='DC')
    c.edge('DC_BUS', 'DC_INV', label='DC')
    c.edge('DC_INV', 'DC_GRID', label='AC')
    c.node('DC_LABEL', '• Single DUID\n• Behind-the-meter\n• Highest efficiency\n• Limited grid charging',
           shape='plaintext', fontname='Lato', fontsize='11')

# Save diagram
output_file = get_output_path("section3", "colocation_diagram")
master.render(str(output_file), cleanup=True)

print(f"\n✓ Diagram saved to: {output_file}.svg")

# Also save individual diagrams
output_nh = get_output_path("section3", "colocation_non_hybrid")
non_hybrid.render(str(output_nh), cleanup=True)
print(f"✓ Non-hybrid diagram: {output_nh}.svg")

output_ac = get_output_path("section3", "colocation_ac_coupled")
ac_coupled.render(str(output_ac), cleanup=True)
print(f"✓ AC-coupled diagram: {output_ac}.svg")

output_dc = get_output_path("section3", "colocation_dc_coupled")
dc_coupled.render(str(output_dc), cleanup=True)
print(f"✓ DC-coupled diagram: {output_dc}.svg")

# ============================================================================
# Summary
# ============================================================================

print("\n" + "=" * 80)
print("SUMMARY")
print("=" * 80)

print("\nDiagrams created:")
print("  1. Non-hybrid: Separate grid connections, dual MLFs, max flexibility")
print("  2. AC-coupled: Shared connection, separate DUIDs, can charge from grid")
print("  3. DC-coupled: Single DUID, behind-the-meter, highest efficiency")

print("\nKey Trade-offs:")
print("  Non-hybrid → AC-coupled:")
print("    Gain: Shared connection capex savings ($50-100/kW)")
print("    Lose: Dual MLF flexibility")
print("\n  AC-coupled → DC-coupled:")
print("    Gain: Conversion efficiency, single DUID simplicity")
print("    Lose: Grid charging capability, dispatch independence")

print("\n" + "=" * 80)
print("Analysis complete!")
print("=" * 80)
