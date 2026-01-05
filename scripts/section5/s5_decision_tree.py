"""
Decision Tree Visualization for Standalone vs. Co-located BESS
Creates an interactive decision flowchart using Plotly
"""

import sys
from pathlib import Path
import plotly.graph_objects as go

# Add parent directory to path to import utils
sys.path.append(str(Path(__file__).parent.parent))
from utils.style_config import TEMPLATE, COLORS
from utils.data_paths import OUTPUTS_DIR, ensure_output_dirs


def create_decision_tree():
    """
    Create an interactive decision tree visualization for the
    standalone vs. co-located BESS decision framework.
    """

    # Define node positions (x, y)
    # Tree flows top to bottom
    nodes = {
        # Level 0: Start
        'start': {'x': 0.5, 'y': 1.0, 'text': 'BESS Investment<br>Decision', 'type': 'start'},

        # Level 1: Scenario Type
        'scenario': {'x': 0.5, 'y': 0.85, 'text': 'Investment<br>Scenario?', 'type': 'decision'},

        # Level 2: Branches
        'greenfield': {'x': 0.25, 'y': 0.70, 'text': 'Greenfield<br>(New Build)', 'type': 'branch'},
        'retrofit': {'x': 0.75, 'y': 0.70, 'text': 'Retrofit<br>(Existing Solar)', 'type': 'branch'},

        # Level 3: Greenfield questions
        'mlf_check': {'x': 0.15, 'y': 0.55, 'text': 'Solar Site<br>MLF > 0.92?', 'type': 'decision'},
        'cis_need': {'x': 0.35, 'y': 0.55, 'text': 'CIS Eligibility<br>Critical?', 'type': 'decision'},

        # Level 3: Retrofit questions
        'ppa_expiry': {'x': 0.65, 'y': 0.55, 'text': 'PPA Expiring<br>Soon?', 'type': 'decision'},
        'merchant_ok': {'x': 0.85, 'y': 0.55, 'text': 'Merchant<br>Acceptable?', 'type': 'decision'},

        # Level 4: Further decisions
        'green_premium': {'x': 0.25, 'y': 0.40, 'text': 'Green Premium<br>Available?', 'type': 'decision'},
        'contract_value': {'x': 0.75, 'y': 0.40, 'text': 'Can Re-contract<br>with Battery?', 'type': 'decision'},

        # Level 5: Outcomes
        'standalone_1': {'x': 0.05, 'y': 0.20, 'text': 'STANDALONE<br>Recommended', 'type': 'standalone'},
        'standalone_2': {'x': 0.20, 'y': 0.20, 'text': 'STANDALONE<br>Likely Better', 'type': 'standalone'},
        'colocated_1': {'x': 0.35, 'y': 0.20, 'text': 'CO-LOCATED<br>Recommended', 'type': 'colocated'},
        'colocated_2': {'x': 0.50, 'y': 0.20, 'text': 'CO-LOCATED<br>For CIS', 'type': 'colocated'},
        'colocated_3': {'x': 0.65, 'y': 0.20, 'text': 'CO-LOCATED<br>Protect Asset', 'type': 'colocated'},
        'standalone_3': {'x': 0.80, 'y': 0.20, 'text': 'STANDALONE<br>Consider Both', 'type': 'standalone'},
        'evaluate': {'x': 0.95, 'y': 0.20, 'text': 'DETAILED<br>Analysis Needed', 'type': 'evaluate'},
    }

    # Define edges (from, to, label)
    edges = [
        ('start', 'scenario', ''),
        ('scenario', 'greenfield', 'New'),
        ('scenario', 'retrofit', 'Existing'),
        ('greenfield', 'mlf_check', ''),
        ('greenfield', 'cis_need', ''),
        ('retrofit', 'ppa_expiry', ''),
        ('retrofit', 'merchant_ok', ''),
        ('mlf_check', 'standalone_1', 'No'),
        ('mlf_check', 'green_premium', 'Yes'),
        ('cis_need', 'colocated_2', 'Yes'),
        ('cis_need', 'standalone_2', 'No'),
        ('green_premium', 'colocated_1', 'Yes'),
        ('green_premium', 'standalone_2', 'No'),
        ('ppa_expiry', 'colocated_3', 'Yes'),
        ('ppa_expiry', 'contract_value', 'No'),
        ('merchant_ok', 'standalone_3', 'Yes'),
        ('merchant_ok', 'colocated_3', 'No'),
        ('contract_value', 'colocated_3', 'Yes'),
        ('contract_value', 'evaluate', 'No'),
    ]

    # Create figure
    fig = go.Figure()

    # Color mapping
    node_colors = {
        'start': COLORS['accent'],
        'decision': '#E3F2FD',  # Light blue
        'branch': '#FFF3E0',    # Light orange
        'standalone': COLORS['battery'],
        'colocated': COLORS['battery_colocated'],
        'evaluate': '#FFD700',  # Yellow
    }

    border_colors = {
        'start': COLORS['accent'],
        'decision': '#1976D2',
        'branch': '#E65100',
        'standalone': COLORS['battery'],
        'colocated': COLORS['battery_colocated'],
        'evaluate': '#C7A600',
    }

    text_colors = {
        'start': 'white',
        'decision': '#1976D2',
        'branch': '#E65100',
        'standalone': 'white',
        'colocated': 'white',
        'evaluate': '#2C3E50',
    }

    # Draw edges first (so they appear behind nodes)
    for from_node, to_node, label in edges:
        from_pos = nodes[from_node]
        to_pos = nodes[to_node]

        # Draw line
        fig.add_trace(go.Scatter(
            x=[from_pos['x'], to_pos['x']],
            y=[from_pos['y'], to_pos['y']],
            mode='lines',
            line=dict(color='#BDBDBD', width=2),
            hoverinfo='skip',
            showlegend=False
        ))

        # Add label if exists
        if label:
            mid_x = (from_pos['x'] + to_pos['x']) / 2
            mid_y = (from_pos['y'] + to_pos['y']) / 2
            fig.add_annotation(
                x=mid_x,
                y=mid_y,
                text=f"<b>{label}</b>",
                showarrow=False,
                font=dict(size=10, color='#666'),
                bgcolor='white',
                borderpad=2
            )

    # Draw nodes
    for node_id, node in nodes.items():
        node_type = node['type']

        # Add node as a scatter point with custom marker
        fig.add_trace(go.Scatter(
            x=[node['x']],
            y=[node['y']],
            mode='markers+text',
            marker=dict(
                size=60 if node_type in ['standalone', 'colocated', 'evaluate'] else 50,
                color=node_colors[node_type],
                line=dict(color=border_colors[node_type], width=3),
                symbol='square' if node_type == 'decision' else 'circle'
            ),
            text=node['text'],
            textposition='middle center',
            textfont=dict(
                size=9,
                color=text_colors[node_type],
                family='Lato, sans-serif'
            ),
            hoverinfo='text',
            hovertext=get_hover_text(node_id, node),
            showlegend=False
        ))

    # Update layout
    fig.update_layout(
        template=TEMPLATE,
        title={
            'text': '<b>BESS Deployment Decision Framework</b><br>' +
                   '<sup>Navigate the key decision points for standalone vs. co-located</sup>',
            'x': 0.5,
            'xanchor': 'center',
            'font': dict(size=18)
        },
        xaxis=dict(
            showgrid=False,
            zeroline=False,
            showticklabels=False,
            range=[-0.1, 1.1]
        ),
        yaxis=dict(
            showgrid=False,
            zeroline=False,
            showticklabels=False,
            range=[0.1, 1.1],
            scaleanchor='x',
            scaleratio=0.6
        ),
        height=700,
        width=1000,
        margin=dict(l=20, r=20, t=80, b=20),
        plot_bgcolor='white',
        paper_bgcolor='white',
        hovermode='closest'
    )

    # Add legend manually
    legend_items = [
        ('Standalone Recommended', COLORS['battery']),
        ('Co-located Recommended', COLORS['battery_colocated']),
        ('Decision Point', '#1976D2'),
        ('Further Analysis', '#C7A600'),
    ]

    for i, (label, color) in enumerate(legend_items):
        fig.add_trace(go.Scatter(
            x=[None],
            y=[None],
            mode='markers',
            marker=dict(size=12, color=color),
            name=label,
            showlegend=True
        ))

    fig.update_layout(
        legend=dict(
            orientation='h',
            yanchor='bottom',
            y=-0.05,
            xanchor='center',
            x=0.5,
            font=dict(size=11)
        )
    )

    return fig


def get_hover_text(node_id, node):
    """Generate detailed hover text for each node"""

    hover_texts = {
        'start': 'Start here: Evaluate your BESS investment opportunity',
        'scenario': 'First question: Are you building new or adding to existing solar?',
        'greenfield': 'New development: You have flexibility in location and design',
        'retrofit': 'Existing solar: You have location constraints but potential synergies',
        'mlf_check': 'Key factor: Does the solar site have acceptable MLF (>0.92)?<br>Poor MLF significantly reduces battery revenue.',
        'cis_need': 'Financing question: Is CIS eligibility critical for your project?<br>Co-location is explicitly eligible for CIS.',
        'ppa_expiry': 'Urgency check: Is your solar PPA expiring soon?<br>Battery can help re-contract the asset.',
        'merchant_ok': 'Risk tolerance: Can you accept merchant exposure on the solar asset?',
        'green_premium': 'Revenue check: Can you capture a green premium for solar-charged storage?',
        'contract_value': 'Re-contracting: Can you secure a new PPA if you add battery storage?',
        'standalone_1': 'STANDALONE: Poor solar MLF makes co-location uneconomic.<br>Build battery at optimal location.',
        'standalone_2': 'STANDALONE: Location value likely exceeds co-location synergies.<br>Validate with detailed modeling.',
        'colocated_1': 'CO-LOCATED: Green premium plus synergies justify location penalty.<br>Structure for ESG offtakers.',
        'colocated_2': 'CO-LOCATED: CIS eligibility provides financing advantage.<br>Accept some location penalty for contract security.',
        'colocated_3': 'CO-LOCATED: Battery protects solar asset value.<br>Lower battery IRR acceptable if combined returns meet hurdle.',
        'standalone_3': 'STANDALONE: Merchant tolerance opens optimal location options.<br>Consider both if solar MLF is acceptable.',
        'evaluate': 'DETAILED ANALYSIS NEEDED: Run dispatch modeling to compare scenarios.<br>Decision depends on specific project economics.',
    }

    return hover_texts.get(node_id, node['text'])


def create_simple_decision_flowchart():
    """
    Create a simpler, cleaner decision flowchart using annotations
    """

    fig = go.Figure()

    # Define the flowchart structure
    # Using a grid layout with clear levels

    # Colors
    start_color = COLORS['accent']
    decision_color = '#E3F2FD'
    standalone_color = COLORS['battery']
    colocated_color = COLORS['battery_colocated']

    # Create boxes using shapes
    shapes = []
    annotations = []

    # Level 0: Start
    shapes.append(dict(
        type='rect',
        x0=0.35, x1=0.65, y0=0.92, y1=1.0,
        fillcolor=start_color,
        line=dict(color=start_color, width=2)
    ))
    annotations.append(dict(
        x=0.5, y=0.96,
        text='<b>BESS Investment Decision</b>',
        font=dict(color='white', size=14),
        showarrow=False
    ))

    # Level 1: First Decision
    shapes.append(dict(
        type='rect',
        x0=0.30, x1=0.70, y0=0.78, y1=0.88,
        fillcolor=decision_color,
        line=dict(color='#1976D2', width=2)
    ))
    annotations.append(dict(
        x=0.5, y=0.83,
        text='<b>Is this a new build or retrofit?</b>',
        font=dict(color='#1976D2', size=12),
        showarrow=False
    ))

    # Arrow from start to decision
    annotations.append(dict(
        x=0.5, y=0.91, ax=0.5, ay=0.88,
        arrowhead=2, arrowsize=1, arrowwidth=2, arrowcolor='#999',
        showarrow=True
    ))

    # Level 2: Two branches
    # Greenfield branch
    shapes.append(dict(
        type='rect',
        x0=0.05, x1=0.35, y0=0.62, y1=0.72,
        fillcolor='#FFF3E0',
        line=dict(color='#E65100', width=2)
    ))
    annotations.append(dict(
        x=0.20, y=0.67,
        text='<b>GREENFIELD</b><br>New Development',
        font=dict(color='#E65100', size=11),
        showarrow=False
    ))
    annotations.append(dict(
        x=0.30, y=0.83, ax=0.20, ay=0.72,
        text='New', font=dict(size=10),
        arrowhead=2, arrowsize=1, arrowwidth=2, arrowcolor='#999',
        showarrow=True
    ))

    # Retrofit branch
    shapes.append(dict(
        type='rect',
        x0=0.65, x1=0.95, y0=0.62, y1=0.72,
        fillcolor='#FFF3E0',
        line=dict(color='#E65100', width=2)
    ))
    annotations.append(dict(
        x=0.80, y=0.67,
        text='<b>RETROFIT</b><br>Existing Solar',
        font=dict(color='#E65100', size=11),
        showarrow=False
    ))
    annotations.append(dict(
        x=0.70, y=0.83, ax=0.80, ay=0.72,
        text='Existing', font=dict(size=10),
        arrowhead=2, arrowsize=1, arrowwidth=2, arrowcolor='#999',
        showarrow=True
    ))

    # Level 3: Key questions
    # Greenfield: MLF check
    shapes.append(dict(
        type='rect',
        x0=0.02, x1=0.38, y0=0.45, y1=0.55,
        fillcolor=decision_color,
        line=dict(color='#1976D2', width=2)
    ))
    annotations.append(dict(
        x=0.20, y=0.50,
        text='Is solar site MLF > 0.92?<br>Is CIS eligibility critical?',
        font=dict(color='#1976D2', size=10),
        showarrow=False
    ))
    annotations.append(dict(
        x=0.20, y=0.62, ax=0.20, ay=0.55,
        arrowhead=2, arrowsize=1, arrowwidth=2, arrowcolor='#999',
        showarrow=True
    ))

    # Retrofit: PPA check
    shapes.append(dict(
        type='rect',
        x0=0.62, x1=0.98, y0=0.45, y1=0.55,
        fillcolor=decision_color,
        line=dict(color='#1976D2', width=2)
    ))
    annotations.append(dict(
        x=0.80, y=0.50,
        text='Is PPA expiring soon?<br>Can you re-contract with battery?',
        font=dict(color='#1976D2', size=10),
        showarrow=False
    ))
    annotations.append(dict(
        x=0.80, y=0.62, ax=0.80, ay=0.55,
        arrowhead=2, arrowsize=1, arrowwidth=2, arrowcolor='#999',
        showarrow=True
    ))

    # Level 4: Outcomes - Greenfield
    # Standalone outcome
    shapes.append(dict(
        type='rect',
        x0=0.02, x1=0.18, y0=0.25, y1=0.38,
        fillcolor=standalone_color,
        line=dict(color=standalone_color, width=2)
    ))
    annotations.append(dict(
        x=0.10, y=0.315,
        text='<b>STANDALONE</b><br>Poor MLF or<br>no CIS need',
        font=dict(color='white', size=9),
        showarrow=False
    ))
    annotations.append(dict(
        x=0.10, y=0.45, ax=0.10, ay=0.38,
        text='No', font=dict(size=9),
        arrowhead=2, arrowsize=1, arrowwidth=2, arrowcolor='#999',
        showarrow=True
    ))

    # Co-located outcome
    shapes.append(dict(
        type='rect',
        x0=0.22, x1=0.38, y0=0.25, y1=0.38,
        fillcolor=colocated_color,
        line=dict(color=colocated_color, width=2)
    ))
    annotations.append(dict(
        x=0.30, y=0.315,
        text='<b>CO-LOCATED</b><br>Good MLF +<br>CIS/premium',
        font=dict(color='white', size=9),
        showarrow=False
    ))
    annotations.append(dict(
        x=0.30, y=0.45, ax=0.30, ay=0.38,
        text='Yes', font=dict(size=9),
        arrowhead=2, arrowsize=1, arrowwidth=2, arrowcolor='#999',
        showarrow=True
    ))

    # Level 4: Outcomes - Retrofit
    # Co-located (protect asset)
    shapes.append(dict(
        type='rect',
        x0=0.62, x1=0.78, y0=0.25, y1=0.38,
        fillcolor=colocated_color,
        line=dict(color=colocated_color, width=2)
    ))
    annotations.append(dict(
        x=0.70, y=0.315,
        text='<b>CO-LOCATED</b><br>Protect solar<br>asset value',
        font=dict(color='white', size=9),
        showarrow=False
    ))
    annotations.append(dict(
        x=0.70, y=0.45, ax=0.70, ay=0.38,
        text='Yes', font=dict(size=9),
        arrowhead=2, arrowsize=1, arrowwidth=2, arrowcolor='#999',
        showarrow=True
    ))

    # Evaluate further
    shapes.append(dict(
        type='rect',
        x0=0.82, x1=0.98, y0=0.25, y1=0.38,
        fillcolor='#FFF9C4',
        line=dict(color='#F9A825', width=2)
    ))
    annotations.append(dict(
        x=0.90, y=0.315,
        text='<b>EVALUATE</b><br>Model both<br>scenarios',
        font=dict(color='#F57F17', size=9),
        showarrow=False
    ))
    annotations.append(dict(
        x=0.90, y=0.45, ax=0.90, ay=0.38,
        text='No', font=dict(size=9),
        arrowhead=2, arrowsize=1, arrowwidth=2, arrowcolor='#999',
        showarrow=True
    ))

    # Key insight box
    shapes.append(dict(
        type='rect',
        x0=0.25, x1=0.75, y0=0.05, y1=0.18,
        fillcolor='#E8F5E9',
        line=dict(color='#4CAF50', width=2)
    ))
    annotations.append(dict(
        x=0.50, y=0.115,
        text='<b>Key Insight:</b> For greenfield, standalone typically wins unless specific<br>co-location benefits apply. For retrofit, co-location typically protects asset value.',
        font=dict(color='#2E7D32', size=10),
        showarrow=False
    ))

    # Update layout
    fig.update_layout(
        shapes=shapes,
        annotations=annotations,
        template=TEMPLATE,
        title={
            'text': '<b>Standalone vs. Co-located BESS Decision Framework</b>',
            'x': 0.5,
            'xanchor': 'center',
            'font': dict(size=16, family='Lato, sans-serif')
        },
        xaxis=dict(
            showgrid=False,
            zeroline=False,
            showticklabels=False,
            range=[0, 1]
        ),
        yaxis=dict(
            showgrid=False,
            zeroline=False,
            showticklabels=False,
            range=[0, 1.05]
        ),
        height=600,
        width=900,
        margin=dict(l=20, r=20, t=60, b=20),
        plot_bgcolor='white',
        paper_bgcolor='white'
    )

    return fig


def main():
    """Generate and save the decision tree visualization"""

    print("Creating decision tree visualization...")

    # Create the simpler flowchart (cleaner for the report)
    fig = create_simple_decision_flowchart()

    # Save outputs
    ensure_output_dirs()
    output_dir = OUTPUTS_DIR / "section5"
    output_dir.mkdir(parents=True, exist_ok=True)

    # Save as HTML
    html_path = output_dir / "decision_tree.html"
    fig.write_html(str(html_path), include_plotlyjs="cdn")
    print(f"HTML saved to: {html_path}")

    # Save as JSON
    json_path = output_dir / "decision_tree.json"
    fig.write_json(str(json_path))
    print(f"JSON saved to: {json_path}")

    # Also create the more complex interactive version
    fig_complex = create_decision_tree()
    complex_html = output_dir / "decision_tree_interactive.html"
    fig_complex.write_html(str(complex_html), include_plotlyjs="cdn")
    print(f"Interactive version saved to: {complex_html}")

    print("\nDecision tree visualizations created successfully!")

    return fig


if __name__ == "__main__":
    main()
