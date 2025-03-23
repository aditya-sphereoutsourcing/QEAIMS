import networkx as nx
import pandas as pd
import numpy as np
import plotly.graph_objects as go

def create_system_graph():
    """
    Create a network graph representing the integrated QEAIMS system.
    
    Returns:
        nx.Graph: NetworkX graph object representing the system
    """
    # Create an empty graph
    G = nx.Graph()
    
    # Add nodes for each major system component
    # Central nodes
    G.add_node("QEAIMS Central", type="central", size=25, color="#1f77b4")
    
    # Add main system nodes
    G.add_node("Electricity Grid", type="electricity", size=20, color="#ff7f0e")
    G.add_node("Water System", type="water", size=20, color="#2ca02c")
    G.add_node("Sewage System", type="sewage", size=20, color="#d62728")
    G.add_node("Banking Network", type="banking", size=20, color="#9467bd")
    
    # Add sub-system nodes for Electricity
    G.add_node("Power Plant 1", type="electricity", size=15, color="#ff7f0e")
    G.add_node("Power Plant 2", type="electricity", size=15, color="#ff7f0e")
    G.add_node("Substation 1", type="electricity", size=15, color="#ff7f0e")
    G.add_node("Substation 2", type="electricity", size=15, color="#ff7f0e")
    G.add_node("Electricity Control", type="electricity", size=15, color="#ff7f0e")
    
    # Add sub-system nodes for Water
    G.add_node("Water Treatment 1", type="water", size=15, color="#2ca02c")
    G.add_node("Water Treatment 2", type="water", size=15, color="#2ca02c")
    G.add_node("Reservoir 1", type="water", size=15, color="#2ca02c")
    G.add_node("Reservoir 2", type="water", size=15, color="#2ca02c")
    G.add_node("Water Control", type="water", size=15, color="#2ca02c")
    
    # Add sub-system nodes for Sewage
    G.add_node("Sewage Treatment 1", type="sewage", size=15, color="#d62728")
    G.add_node("Sewage Treatment 2", type="sewage", size=15, color="#d62728")
    G.add_node("Sewage Pumping 1", type="sewage", size=15, color="#d62728")
    G.add_node("Sewage Pumping 2", type="sewage", size=15, color="#d62728")
    G.add_node("Sewage Control", type="sewage", size=15, color="#d62728")
    
    # Add sub-system nodes for Banking
    G.add_node("Data Center 1", type="banking", size=15, color="#9467bd")
    G.add_node("Data Center 2", type="banking", size=15, color="#9467bd")
    G.add_node("Transaction Processing", type="banking", size=15, color="#9467bd")
    G.add_node("Fraud Detection", type="banking", size=15, color="#9467bd")
    G.add_node("Banking Control", type="banking", size=15, color="#9467bd")
    
    # Add edges from QEAIMS central to main systems
    G.add_edge("QEAIMS Central", "Electricity Grid", weight=5)
    G.add_edge("QEAIMS Central", "Water System", weight=5)
    G.add_edge("QEAIMS Central", "Sewage System", weight=5)
    G.add_edge("QEAIMS Central", "Banking Network", weight=5)
    
    # Add edges for Electricity subsystems
    G.add_edge("Electricity Grid", "Power Plant 1", weight=3)
    G.add_edge("Electricity Grid", "Power Plant 2", weight=3)
    G.add_edge("Electricity Grid", "Substation 1", weight=3)
    G.add_edge("Electricity Grid", "Substation 2", weight=3)
    G.add_edge("Electricity Grid", "Electricity Control", weight=3)
    
    # Add edges for Water subsystems
    G.add_edge("Water System", "Water Treatment 1", weight=3)
    G.add_edge("Water System", "Water Treatment 2", weight=3)
    G.add_edge("Water System", "Reservoir 1", weight=3)
    G.add_edge("Water System", "Reservoir 2", weight=3)
    G.add_edge("Water System", "Water Control", weight=3)
    
    # Add edges for Sewage subsystems
    G.add_edge("Sewage System", "Sewage Treatment 1", weight=3)
    G.add_edge("Sewage System", "Sewage Treatment 2", weight=3)
    G.add_edge("Sewage System", "Sewage Pumping 1", weight=3)
    G.add_edge("Sewage System", "Sewage Pumping 2", weight=3)
    G.add_edge("Sewage System", "Sewage Control", weight=3)
    
    # Add edges for Banking subsystems
    G.add_edge("Banking Network", "Data Center 1", weight=3)
    G.add_edge("Banking Network", "Data Center 2", weight=3)
    G.add_edge("Banking Network", "Transaction Processing", weight=3)
    G.add_edge("Banking Network", "Fraud Detection", weight=3)
    G.add_edge("Banking Network", "Banking Control", weight=3)
    
    # Add cross-system connections to show interdependency
    G.add_edge("Power Plant 1", "Water Treatment 1", weight=1)  # Power plant needs water
    G.add_edge("Water Treatment 1", "Electricity Control", weight=1)  # Water treatment needs electricity
    G.add_edge("Sewage Treatment 1", "Electricity Control", weight=1)  # Sewage treatment needs electricity
    G.add_edge("Data Center 1", "Electricity Control", weight=1)  # Data centers need electricity
    G.add_edge("Transaction Processing", "Data Center 1", weight=1)  # Transactions run in data centers
    
    return G

def update_graph_status(G, anomaly_data):
    """
    Update the status of nodes in the graph based on anomaly data.
    
    Args:
        G (nx.Graph): NetworkX graph object representing the system
        anomaly_data (dict): Dictionary with anomaly status for each system
        
    Returns:
        nx.Graph: Updated graph with status information
    """
    # Create a copy of the graph to avoid modifying the original
    G_updated = G.copy()
    
    # Update status for electricity nodes
    electricity_status = anomaly_data.get('electricity', 'Normal')
    for node in G_updated.nodes:
        if G_updated.nodes[node]['type'] == 'electricity':
            if electricity_status == "Anomaly Detected":
                G_updated.nodes[node]['color'] = "#ff0000"  # Red for anomaly
                G_updated.nodes[node]['status'] = "Anomaly"
            else:
                G_updated.nodes[node]['status'] = "Normal"
    
    # Update status for water nodes
    water_status = anomaly_data.get('water', 'Normal')
    for node in G_updated.nodes:
        if G_updated.nodes[node]['type'] == 'water':
            if water_status == "Anomaly Detected":
                G_updated.nodes[node]['color'] = "#ff0000"  # Red for anomaly
                G_updated.nodes[node]['status'] = "Anomaly"
            else:
                G_updated.nodes[node]['status'] = "Normal"
    
    # Update status for sewage nodes
    sewage_status = anomaly_data.get('sewage', 'Normal')
    for node in G_updated.nodes:
        if G_updated.nodes[node]['type'] == 'sewage':
            if sewage_status == "Anomaly Detected":
                G_updated.nodes[node]['color'] = "#ff0000"  # Red for anomaly
                G_updated.nodes[node]['status'] = "Anomaly"
            else:
                G_updated.nodes[node]['status'] = "Normal"
    
    # Update status for banking nodes
    banking_status = anomaly_data.get('banking', 'Normal')
    for node in G_updated.nodes:
        if G_updated.nodes[node]['type'] == 'banking':
            if banking_status == "Anomaly Detected":
                G_updated.nodes[node]['color'] = "#ff0000"  # Red for anomaly
                G_updated.nodes[node]['status'] = "Anomaly"
            else:
                G_updated.nodes[node]['status'] = "Normal"
    
    return G_updated

def create_network_visualization(G, title="QEAIMS Integrated System Network"):
    """
    Create a Plotly visualization of the network graph.
    
    Args:
        G (nx.Graph): NetworkX graph object
        title (str): Title for the visualization
        
    Returns:
        go.Figure: Plotly figure object
    """
    # Calculate layout using networkx
    pos = nx.spring_layout(G, seed=42, k=0.15)
    
    # Create node traces for each node type
    node_traces = {}
    node_types = set(nx.get_node_attributes(G, 'type').values())
    
    for node_type in node_types:
        node_traces[node_type] = go.Scatter(
            x=[],
            y=[],
            text=[],
            mode='markers',
            name=node_type.capitalize(),
            marker=dict(
                showscale=False,
                size=[],
                line=dict(width=2, color='#ffffff')
            ),
            hoverinfo='text'
        )
    
    # Add nodes to traces
    for node in G.nodes():
        x, y = pos[node]
        node_type = G.nodes[node]['type']
        size = G.nodes[node]['size']
        color = G.nodes[node]['color']
        status = G.nodes[node].get('status', 'Normal')
        
        node_traces[node_type].x = node_traces[node_type].x + (x,)
        node_traces[node_type].y = node_traces[node_type].y + (y,)
        node_traces[node_type].marker.size = node_traces[node_type].marker.size + (size,)
        
        node_info = f'Node: {node}<br>Type: {node_type}<br>Status: {status}'
        node_traces[node_type].text = node_traces[node_type].text + (node_info,)
        
        # If the node has a specific color, add it to the marker.color list
        if 'color' not in node_traces[node_type].marker:
            node_traces[node_type].marker.color = []
        node_traces[node_type].marker.color = node_traces[node_type].marker.color + (color,)
    
    # Create edge traces
    edge_trace = go.Scatter(
        x=[],
        y=[],
        line=dict(width=1, color='#888'),
        hoverinfo='none',
        mode='lines'
    )
    
    # Add edges to trace
    for edge in G.edges():
        x0, y0 = pos[edge[0]]
        x1, y1 = pos[edge[1]]
        edge_trace.x += (x0, x1, None)
        edge_trace.y += (y0, y1, None)
    
    # Create figure
    fig = go.Figure(
        data=[edge_trace] + list(node_traces.values()),
        layout=go.Layout(
            title=title,
            titlefont=dict(size=16),
            showlegend=True,
            hovermode='closest',
            margin=dict(b=20, l=5, r=5, t=40),
            xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
            yaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
            legend=dict(
                x=0,
                y=1,
                font=dict(size=10)
            )
        )
    )
    
    return fig

def simulate_fault(fault_type):
    """
    Simulate a fault in the system and return affected components.
    
    Args:
        fault_type (str): Type of fault to simulate
        
    Returns:
        dict: Information about the fault and affected components
    """
    # Create base graph
    G = create_system_graph()
    
    # Define fault scenarios and affected nodes
    fault_scenarios = {
        'power_outage': {
            'description': 'Power Outage in Eastern Grid',
            'affected_nodes': ['Power Plant 1', 'Substation 1', 'Electricity Control'],
            'secondary_nodes': ['Water Treatment 1', 'Data Center 1'],
            'severity': 'High',
            'systems': ['electricity', 'water', 'banking']
        },
        'water_main_break': {
            'description': 'Major Water Main Break',
            'affected_nodes': ['Water Treatment 1', 'Reservoir 1', 'Water Control'],
            'secondary_nodes': [],
            'severity': 'Medium',
            'systems': ['water']
        },
        'cyber_attack': {
            'description': 'Cyber Attack on Banking Network',
            'affected_nodes': ['Banking Network', 'Data Center 1', 'Transaction Processing', 'Fraud Detection'],
            'secondary_nodes': [],
            'severity': 'Critical',
            'systems': ['banking']
        },
        'sewage_overflow': {
            'description': 'Sewage System Overflow',
            'affected_nodes': ['Sewage Treatment 1', 'Sewage Pumping 1', 'Sewage Control'],
            'secondary_nodes': ['Water Treatment 1'],
            'severity': 'Medium',
            'systems': ['sewage', 'water']
        },
        'grid_instability': {
            'description': 'Electrical Grid Instability',
            'affected_nodes': ['Electricity Grid', 'Substation 1', 'Substation 2'],
            'secondary_nodes': ['Data Center 1', 'Water Treatment 1', 'Sewage Treatment 1'],
            'severity': 'High',
            'systems': ['electricity', 'water', 'sewage', 'banking']
        }
    }
    
    # Get scenario info
    scenario = fault_scenarios.get(fault_type, fault_scenarios['power_outage'])
    
    # Mark affected nodes in graph
    G_fault = G.copy()
    
    # Update primary affected nodes
    for node in scenario['affected_nodes']:
        if node in G_fault.nodes():
            G_fault.nodes[node]['color'] = "#ff0000"  # Red for primary affected
            G_fault.nodes[node]['status'] = "Fault"
            G_fault.nodes[node]['size'] += 5  # Make them larger
    
    # Update secondary affected nodes
    for node in scenario['secondary_nodes']:
        if node in G_fault.nodes():
            G_fault.nodes[node]['color'] = "#ffa500"  # Orange for secondary affected
            G_fault.nodes[node]['status'] = "At Risk"
    
    # Create anomaly status dict for systems
    anomaly_status = {
        'electricity': 'Normal',
        'water': 'Normal',
        'sewage': 'Normal',
        'banking': 'Normal'
    }
    
    # Update anomaly status for affected systems
    for system in scenario['systems']:
        anomaly_status[system] = "Anomaly Detected"
    
    # Add fault information to return
    fault_info = {
        'description': scenario['description'],
        'affected_nodes': scenario['affected_nodes'],
        'secondary_nodes': scenario['secondary_nodes'],
        'severity': scenario['severity'],
        'systems': scenario['systems'],
        'graph': G_fault,
        'anomaly_status': anomaly_status
    }
    
    return fault_info
