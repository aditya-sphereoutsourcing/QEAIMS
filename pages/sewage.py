import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from utils.data_generator import get_detailed_data
from utils.anomaly_detection import analyze_system_health

st.set_page_config(
    page_title="QEAIMS - Sewage System",
    page_icon="🧪",
    layout="wide"
)

st.title("Sewage System Monitoring")
st.markdown("Real-time monitoring and analysis of the integrated sewage treatment system")

# Sidebar for timerange selection
st.sidebar.header("Time Range")
time_range = st.sidebar.selectbox(
    "Select time period:",
    ["Last 24 Hours", "Last 7 Days", "Last 30 Days"]
)

# Convert selection to hours
if time_range == "Last 24 Hours":
    hours = 24
elif time_range == "Last 7 Days":
    hours = 24 * 7
else:
    hours = 24 * 30

# Get detailed sewage data
sewage_data = get_detailed_data('sewage', hours=hours)

# Create system health metrics at the top
col1, col2, col3, col4 = st.columns(4)

# Get latest values
latest_flow = sewage_data['flow_kl_h'].iloc[-1]
latest_treatment = sewage_data['treatment_efficiency'].iloc[-1]
latest_contaminant = sewage_data['contaminant_level'].iloc[-1]
latest_oxygen = sewage_data['dissolved_oxygen'].iloc[-1]

# Calculate changes
flow_change = latest_flow - sewage_data['flow_kl_h'].iloc[-2]
treatment_change = latest_treatment - sewage_data['treatment_efficiency'].iloc[-2]
contaminant_change = latest_contaminant - sewage_data['contaminant_level'].iloc[-2]
oxygen_change = latest_oxygen - sewage_data['dissolved_oxygen'].iloc[-2]

with col1:
    st.metric(
        label="Sewage Flow",
        value=f"{latest_flow:.1f} kL/h",
        delta=f"{flow_change:.1f} kL/h"
    )

with col2:
    st.metric(
        label="Treatment Efficiency",
        value=f"{latest_treatment:.1f}%",
        delta=f"{treatment_change:.1f}%"
    )

with col3:
    st.metric(
        label="Contaminant Level",
        value=f"{latest_contaminant:.2f} ppm",
        delta=f"{contaminant_change:.2f} ppm",
        delta_color="inverse"  # Lower is better for contaminants
    )

with col4:
    st.metric(
        label="Dissolved Oxygen",
        value=f"{latest_oxygen:.1f} mg/L",
        delta=f"{oxygen_change:.1f} mg/L"
    )

# System health analysis
st.subheader("System Health Analysis")

# Run the health analysis
health_analysis = analyze_system_health(sewage_data, 'sewage')

# Create columns for health score and status
col1, col2 = st.columns(2)

with col1:
    # Health score gauge chart
    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=health_analysis['health_score'],
        title={'text': "Health Score"},
        domain={'x': [0, 1], 'y': [0, 1]},
        gauge={
            'axis': {'range': [0, 100]},
            'bar': {'color': "darkblue"},
            'steps': [
                {'range': [0, 50], 'color': "red"},
                {'range': [50, 75], 'color': "orange"},
                {'range': [75, 90], 'color': "yellow"},
                {'range': [90, 100], 'color': "green"}
            ]
        }
    ))
    st.plotly_chart(fig)

with col2:
    st.subheader("Status: " + health_analysis['status'])
    st.write("**Issues:**")
    for issue in health_analysis['issues']:
        st.write(f"- {issue}")
    
    st.write("**Recommendations:**")
    for recommendation in health_analysis['recommendations']:
        st.write(f"- {recommendation}")

# Create tabs for different visualizations
tab1, tab2, tab3 = st.tabs(["Flow Monitoring", "Treatment Metrics", "Anomaly Detection"])

with tab1:
    st.subheader("Sewage Flow Over Time")
    
    fig = px.line(
        sewage_data, 
        x='timestamp', 
        y='flow_kl_h',
        title='Sewage Flow (kL/h)',
        labels={'timestamp': 'Time', 'flow_kl_h': 'Flow (kL/h)'}
    )
    
    # Add a different color for anomalies
    anomaly_data = sewage_data[sewage_data['anomaly']]
    if not anomaly_data.empty:
        fig.add_scatter(
            x=anomaly_data['timestamp'],
            y=anomaly_data['flow_kl_h'],
            mode='markers',
            marker=dict(color='red', size=8),
            name='Anomaly'
        )
    
    st.plotly_chart(fig, use_container_width=True)
    
    # Add daily/hourly patterns
    st.subheader("Flow Patterns")
    
    # Add hour of day to the data
    sewage_data['hour'] = sewage_data['timestamp'].dt.hour
    
    # Group by hour and calculate statistics
    hourly_flow = sewage_data.groupby('hour')['flow_kl_h'].agg(['mean', 'min', 'max']).reset_index()
    
    fig = px.line(
        hourly_flow,
        x='hour',
        y='mean',
        title='Average Flow by Hour of Day',
        labels={'hour': 'Hour of Day', 'mean': 'Average Flow (kL/h)'}
    )
    
    # Add range for min/max
    fig.add_scatter(
        x=hourly_flow['hour'],
        y=hourly_flow['min'],
        mode='lines',
        line=dict(width=0),
        showlegend=False
    )
    
    fig.add_scatter(
        x=hourly_flow['hour'],
        y=hourly_flow['max'],
        mode='lines',
        fill='tonexty',
        fillcolor='rgba(128,0,0,0.2)',
        line=dict(width=0),
        name='Min/Max Range'
    )
    
    st.plotly_chart(fig, use_container_width=True)

with tab2:
    st.subheader("Treatment Efficiency Metrics")
    
    # Create columns for treatment efficiency and contaminant level
    col1, col2 = st.columns(2)
    
    with col1:
        # Treatment efficiency trend
        fig = px.line(
            sewage_data,
            x='timestamp',
            y='treatment_efficiency',
            title='Treatment Efficiency Trend',
            labels={'timestamp': 'Time', 'treatment_efficiency': 'Efficiency (%)'}
        )
        
        # Add threshold line
        fig.add_shape(
            type="line",
            x0=sewage_data['timestamp'].min(),
            x1=sewage_data['timestamp'].max(),
            y0=85,
            y1=85,
            line=dict(
                color="red",
                width=2,
                dash="dash",
            ),
            name="Minimum Acceptable"
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        # Contaminant level trend
        fig = px.line(
            sewage_data,
            x='timestamp',
            y='contaminant_level',
            title='Contaminant Level Trend',
            labels={'timestamp': 'Time', 'contaminant_level': 'Contaminant Level (ppm)'}
        )
        
        # Add threshold line
        fig.add_shape(
            type="line",
            x0=sewage_data['timestamp'].min(),
            x1=sewage_data['timestamp'].max(),
            y0=10,
            y1=10,
            line=dict(
                color="red",
                width=2,
                dash="dash",
            ),
            name="Maximum Acceptable"
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    # Dissolved oxygen and methane levels
    st.subheader("Dissolved Oxygen and Methane Levels")
    
    # Create columns for DO and methane
    col1, col2 = st.columns(2)
    
    with col1:
        # Dissolved oxygen trend
        fig = px.line(
            sewage_data,
            x='timestamp',
            y='dissolved_oxygen',
            title='Dissolved Oxygen Levels',
            labels={'timestamp': 'Time', 'dissolved_oxygen': 'Dissolved Oxygen (mg/L)'}
        )
        
        # Add threshold line
        fig.add_shape(
            type="line",
            x0=sewage_data['timestamp'].min(),
            x1=sewage_data['timestamp'].max(),
            y0=5,
            y1=5,
            line=dict(
                color="red",
                width=2,
                dash="dash",
            ),
            name="Minimum Acceptable"
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        # Methane level trend
        fig = px.line(
            sewage_data,
            x='timestamp',
            y='methane_level',
            title='Methane Levels',
            labels={'timestamp': 'Time', 'methane_level': 'Methane (%)'}
        )
        
        # Add threshold line
        fig.add_shape(
            type="line",
            x0=sewage_data['timestamp'].min(),
            x1=sewage_data['timestamp'].max(),
            y0=5,
            y1=5,
            line=dict(
                color="red",
                width=2,
                dash="dash",
            ),
            name="Maximum Acceptable"
        )
        
        st.plotly_chart(fig, use_container_width=True)

with tab3:
    st.subheader("Anomaly Detection")
    
    # Create a combined view of metrics with anomalies highlighted
    anomaly_data = sewage_data[sewage_data['anomaly']]
    
    # Flow with anomalies highlighted
    fig = px.scatter(
        sewage_data,
        x='timestamp',
        y='flow_kl_h',
        color='anomaly',
        title='Flow Anomalies',
        labels={'timestamp': 'Time', 'flow_kl_h': 'Flow (kL/h)', 'anomaly': 'Anomaly'},
        color_discrete_map={False: 'blue', True: 'red'}
    )
    
    # Add line connecting non-anomalous points
    normal_data = sewage_data[~sewage_data['anomaly']]
    fig.add_trace(
        go.Scatter(
            x=normal_data['timestamp'],
            y=normal_data['flow_kl_h'],
            mode='lines',
            line=dict(color='blue'),
            showlegend=False
        )
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    # Treatment efficiency with anomalies
    fig = px.scatter(
        sewage_data,
        x='timestamp',
        y='treatment_efficiency',
        color='anomaly',
        title='Treatment Efficiency Anomalies',
        labels={'timestamp': 'Time', 'treatment_efficiency': 'Efficiency (%)', 'anomaly': 'Anomaly'},
        color_discrete_map={False: 'green', True: 'red'}
    )
    
    # Add line connecting non-anomalous points
    fig.add_trace(
        go.Scatter(
            x=normal_data['timestamp'],
            y=normal_data['treatment_efficiency'],
            mode='lines',
            line=dict(color='green'),
            showlegend=False
        )
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    # Display anomaly statistics
    if not anomaly_data.empty:
        st.subheader("Anomaly Statistics")
        
        anomaly_count = len(anomaly_data)
        total_count = len(sewage_data)
        anomaly_percent = (anomaly_count / total_count) * 100
        
        st.write(f"- **Total anomalies detected:** {anomaly_count}")
        st.write(f"- **Percentage of data points:** {anomaly_percent:.2f}%")
        
        # If there are anomalies, show a table of them
        st.subheader("Anomaly Details")
        
        # Format the anomaly data for display
        display_columns = ['timestamp', 'flow_kl_h', 'treatment_efficiency', 'contaminant_level', 'dissolved_oxygen']
        formatted_anomalies = anomaly_data[display_columns].copy()
        formatted_anomalies['timestamp'] = formatted_anomalies['timestamp'].dt.strftime('%Y-%m-%d %H:%M:%S')
        
        st.dataframe(formatted_anomalies, use_container_width=True)
    else:
        st.info("No anomalies detected in the selected time period.")
