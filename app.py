import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from utils.data_generator import get_latest_data, get_historical_data
from utils.anomaly_detection import get_anomaly_status

# Set page configuration
st.set_page_config(
    page_title="QEAIMS Dashboard",
    page_icon="🔌",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Dashboard title
st.title("QEAIMS - Quantum Encrypted AI Managed System")
st.markdown("""
This dashboard demonstrates the vision of an integrated utilities monitoring system with 
quantum encryption, AI-driven monitoring, and self-healing capabilities for critical infrastructure.
""")

# Sidebar
st.sidebar.title("Navigation")
st.sidebar.markdown("Use the sidebar to navigate between different sections of the dashboard.")

# Get latest data for overview
latest_data = get_latest_data()

# Create metrics row
col1, col2, col3, col4 = st.columns(4)

with col1:
    electricity_anomaly = get_anomaly_status('electricity', latest_data)
    electricity_color = "🟢" if electricity_anomaly == "Normal" else "🔴"
    st.metric(
        label=f"{electricity_color} Electricity System",
        value=f"{latest_data['electricity']['load']:.1f} MW",
        delta=f"{latest_data['electricity']['load_change']:.1f} MW"
    )
    
with col2:
    water_anomaly = get_anomaly_status('water', latest_data)
    water_color = "🟢" if water_anomaly == "Normal" else "🔴"
    st.metric(
        label=f"{water_color} Water System",
        value=f"{latest_data['water']['flow']:.1f} kL/h",
        delta=f"{latest_data['water']['flow_change']:.1f} kL/h"
    )
    
with col3:
    sewage_anomaly = get_anomaly_status('sewage', latest_data)
    sewage_color = "🟢" if sewage_anomaly == "Normal" else "🔴"
    st.metric(
        label=f"{sewage_color} Sewage System",
        value=f"{latest_data['sewage']['flow']:.1f} kL/h",
        delta=f"{latest_data['sewage']['flow_change']:.1f} kL/h"
    )
    
with col4:
    banking_anomaly = get_anomaly_status('banking', latest_data)
    banking_color = "🟢" if banking_anomaly == "Normal" else "🔴"
    st.metric(
        label=f"{banking_color} Banking System",
        value=f"{latest_data['banking']['transactions']:.0f} tps",
        delta=f"{latest_data['banking']['transaction_change']:.0f} tps"
    )

# System health overview
st.subheader("System Health Overview")

# Get historical data for charts
historical_data = get_historical_data(hours=24)

# Create a consolidated health score chart
health_scores = pd.DataFrame({
    'timestamp': historical_data['timestamp'],
    'Electricity Health': historical_data['electricity']['health_score'],
    'Water Health': historical_data['water']['health_score'],
    'Sewage Health': historical_data['sewage']['health_score'],
    'Banking Health': historical_data['banking']['health_score']
})

health_scores_melted = pd.melt(
    health_scores, 
    id_vars=['timestamp'], 
    value_vars=['Electricity Health', 'Water Health', 'Sewage Health', 'Banking Health'],
    var_name='System',
    value_name='Health Score'
)

fig = px.line(
    health_scores_melted,
    x='timestamp',
    y='Health Score',
    color='System',
    title='Integrated System Health Scores (Last 24 Hours)',
    labels={'timestamp': 'Time', 'Health Score': 'Health Score (%)'},
    range_y=[0, 100]
)

fig.update_layout(
    legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
    hovermode="x unified"
)

st.plotly_chart(fig, use_container_width=True)

# Anomaly detection overview
st.subheader("Anomaly Detection Overview")

# Create columns for anomaly charts
col1, col2 = st.columns(2)

with col1:
    # Electricity anomaly detection
    electricity_anomalies = pd.DataFrame({
        'timestamp': historical_data['timestamp'],
        'load': historical_data['electricity']['load'],
        'anomaly': historical_data['electricity']['anomaly']
    })
    
    fig_elec = px.scatter(
        electricity_anomalies,
        x='timestamp',
        y='load',
        color='anomaly',
        title='Electricity Load Anomalies',
        labels={'timestamp': 'Time', 'load': 'Load (MW)', 'anomaly': 'Anomaly Status'},
        color_discrete_map={'False': 'blue', 'True': 'red'}
    )
    
    # Add a line connecting non-anomalous points
    normal_data = electricity_anomalies[electricity_anomalies['anomaly'] == False]
    fig_elec.add_trace(
        go.Scatter(
            x=normal_data['timestamp'],
            y=normal_data['load'],
            mode='lines',
            line=dict(color='blue'),
            showlegend=False
        )
    )
    
    st.plotly_chart(fig_elec, use_container_width=True)

with col2:
    # Water anomaly detection
    water_anomalies = pd.DataFrame({
        'timestamp': historical_data['timestamp'],
        'flow': historical_data['water']['flow'],
        'anomaly': historical_data['water']['anomaly']
    })
    
    fig_water = px.scatter(
        water_anomalies,
        x='timestamp',
        y='flow',
        color='anomaly',
        title='Water Flow Anomalies',
        labels={'timestamp': 'Time', 'flow': 'Flow (kL/h)', 'anomaly': 'Anomaly Status'},
        color_discrete_map={'False': 'green', 'True': 'red'}
    )
    
    # Add a line connecting non-anomalous points
    normal_data = water_anomalies[water_anomalies['anomaly'] == False]
    fig_water.add_trace(
        go.Scatter(
            x=normal_data['timestamp'],
            y=normal_data['flow'],
            mode='lines',
            line=dict(color='green'),
            showlegend=False
        )
    )
    
    st.plotly_chart(fig_water, use_container_width=True)

# System status summary
st.subheader("System Status Summary")

# Create a status table
status_data = {
    'System': ['Electricity', 'Water', 'Sewage', 'Banking'],
    'Status': [
        get_anomaly_status('electricity', latest_data),
        get_anomaly_status('water', latest_data),
        get_anomaly_status('sewage', latest_data),
        get_anomaly_status('banking', latest_data)
    ],
    'Quantum Encryption': ['Active', 'Active', 'Active', 'Active'],
    'Self-Healing': [
        'Monitoring' if get_anomaly_status('electricity', latest_data) == 'Normal' else 'Active',
        'Monitoring' if get_anomaly_status('water', latest_data) == 'Normal' else 'Active',
        'Monitoring' if get_anomaly_status('sewage', latest_data) == 'Normal' else 'Active',
        'Monitoring' if get_anomaly_status('banking', latest_data) == 'Normal' else 'Active'
    ],
    'Last Update': ['Just now', 'Just now', 'Just now', 'Just now']
}

status_df = pd.DataFrame(status_data)
st.table(status_df)

# Information about the QEAIMS project
st.subheader("About QEAIMS")
st.markdown("""
The QEAIMS project envisions a groundbreaking unified network that connects critical public utilities 
(electricity, water, sewage) and financial services under one intelligent system. Leveraging quantum 
encryption, artificial intelligence, and distributed ledger technology, the system continuously monitors 
for anomalies, autonomously isolates faults, and initiates repair and recovery procedures.

**Key Features:**
- Real-time monitoring of integrated utility systems
- AI-driven anomaly detection
- Quantum-encrypted communication for maximum security
- Self-healing capabilities for automatic fault isolation and repair
- Transparent and auditable operations through distributed ledger technology
""")

# Footer
st.markdown("---")
st.markdown("© 2023 QEAIMS Project | Quantum Encrypted AI Managed System")
