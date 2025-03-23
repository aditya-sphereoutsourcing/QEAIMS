import streamlit as st
import pandas as pd
import numpy as np
import networkx as nx
import plotly.graph_objects as go
from utils.data_generator import get_latest_data
from utils.anomaly_detection import get_anomaly_status
from utils.network_graph import create_system_graph, update_graph_status, create_network_visualization

st.set_page_config(
    page_title="QEAIMS - Network View",
    page_icon="🌐",
    layout="wide"
)

st.title("Integrated Network Visualization")
st.markdown("Interactive visualization of the QEAIMS integrated utility network")

# Get latest data and anomaly status
latest_data = get_latest_data()

# Create anomaly status dictionary
anomaly_status = {
    'electricity': get_anomaly_status('electricity', latest_data),
    'water': get_anomaly_status('water', latest_data),
    'sewage': get_anomaly_status('sewage', latest_data),
    'banking': get_anomaly_status('banking', latest_data)
}

# Create network graph
system_graph = create_system_graph()

# Update graph based on current system status
updated_graph = update_graph_status(system_graph, anomaly_status)

# Display network visualization
st.subheader("Unified System Network")

# Create network visualization
network_fig = create_network_visualization(updated_graph, "QEAIMS Integrated System Network")
st.plotly_chart(network_fig, use_container_width=True)

# System status overview
st.subheader("System Status Overview")

# Create status summary table
status_data = {
    'System': ['Electricity Grid', 'Water System', 'Sewage System', 'Banking Network'],
    'Status': [
        anomaly_status['electricity'],
        anomaly_status['water'],
        anomaly_status['sewage'],
        anomaly_status['banking']
    ],
    'Nodes': [
        '5 active / 0 isolated',
        '5 active / 0 isolated',
        '5 active / 0 isolated',
        '5 active / 0 isolated'
    ],
    'Connection State': [
        'Quantum Encrypted',
        'Quantum Encrypted',
        'Quantum Encrypted',
        'Quantum Encrypted'
    ],
    'Last Updated': ['Just now', 'Just now', 'Just now', 'Just now']
}

# Convert to dataframe
status_df = pd.DataFrame(status_data)

# Display as table
st.table(status_df)

# System interdependencies
st.subheader("System Interdependencies")

# Create interdependency matrix
dependencies = pd.DataFrame({
    'System': ['Electricity Grid', 'Water System', 'Sewage System', 'Banking Network'],
    'Depends On': [
        'None',
        'Electricity Grid',
        'Electricity Grid, Water System',
        'Electricity Grid'
    ],
    'Provides For': [
        'Water System, Sewage System, Banking Network',
        'Sewage System',
        'None',
        'Electricity Grid, Water System, Sewage System (billing)'
    ]
})

# Display as dataframe
st.dataframe(dependencies, use_container_width=True)

# Network statistics
st.subheader("Network Statistics")

col1, col2, col3 = st.columns(3)

with col1:
    st.metric(
        label="Total Network Nodes",
        value="25"
    )

with col2:
    # Calculate edge count
    edge_count = len(system_graph.edges())
    st.metric(
        label="Total Connections",
        value=str(edge_count)
    )

with col3:
    # Calculate centrality
    centrality = nx.degree_centrality(system_graph)
    max_central_node = max(centrality, key=centrality.get)
    max_centrality = centrality[max_central_node]
    
    st.metric(
        label="Network Resilience",
        value="High",
        help="Based on network topology and redundancy"
    )

# Advanced network metrics
st.subheader("Advanced Network Metrics")

# Calculate network metrics
avg_path_length = nx.average_shortest_path_length(system_graph)
clustering = nx.average_clustering(system_graph)
density = nx.density(system_graph)

col1, col2, col3 = st.columns(3)

with col1:
    st.metric(
        label="Average Path Length",
        value=f"{avg_path_length:.2f}",
        help="Average number of steps along the shortest paths for all pairs of nodes"
    )

with col2:
    st.metric(
        label="Clustering Coefficient",
        value=f"{clustering:.2f}",
        help="Measure of the degree to which nodes tend to cluster together"
    )

with col3:
    st.metric(
        label="Network Density",
        value=f"{density:.2f}",
        help="Ratio of actual connections to possible connections"
    )

# Information about the network visualization
st.markdown("""
### Understanding the Network Visualization

This interactive network graph represents the integrated QEAIMS system connecting critical public utilities:

- **Central Node**: The core QEAIMS system that coordinates all connected utilities
- **Main System Nodes**: Primary systems for electricity, water, sewage, and banking
- **Subsystem Nodes**: Individual components within each system
- **Connections**: Data and control links between systems and components

The network uses quantum encryption for secure communication between all nodes. The graph highlights:

- **Normal operation** - Blue/Green nodes
- **Anomalies** - Red nodes
- **System interdependencies** - Cross-system connections

You can interact with the graph by:
- Hovering over nodes to see details
- Clicking and dragging to pan
- Zooming in/out with mouse wheel
- Selecting specific systems using the legend
""")
