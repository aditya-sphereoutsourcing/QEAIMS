import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from utils.data_generator import get_detailed_data
from utils.anomaly_detection import analyze_system_health

st.set_page_config(
    page_title="QEAIMS - Water System",
    page_icon="💧",
    layout="wide"
)

st.title("Water System Monitoring")
st.markdown("Real-time monitoring and analysis of the integrated water distribution system")

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

# Get detailed water data
water_data = get_detailed_data('water', hours=hours)

# Create system health metrics at the top
col1, col2, col3, col4 = st.columns(4)

# Get latest values
latest_flow = water_data['flow_kl_h'].iloc[-1]
latest_pressure = water_data['pressure_bar'].iloc[-1]
latest_turbidity = water_data['turbidity_ntu'].iloc[-1]
latest_ph = water_data['ph_level'].iloc[-1]

# Calculate changes
flow_change = latest_flow - water_data['flow_kl_h'].iloc[-2]
pressure_change = latest_pressure - water_data['pressure_bar'].iloc[-2]
turbidity_change = latest_turbidity - water_data['turbidity_ntu'].iloc[-2]
ph_change = latest_ph - water_data['ph_level'].iloc[-2]

with col1:
    st.metric(
        label="Water Flow",
        value=f"{latest_flow:.1f} kL/h",
        delta=f"{flow_change:.1f} kL/h"
    )

with col2:
    st.metric(
        label="Pressure",
        value=f"{latest_pressure:.1f} bar",
        delta=f"{pressure_change:.1f} bar"
    )

with col3:
    st.metric(
        label="Turbidity",
        value=f"{latest_turbidity:.2f} NTU",
        delta=f"{turbidity_change:.2f} NTU"
    )

with col4:
    st.metric(
        label="pH Level",
        value=f"{latest_ph:.1f}",
        delta=f"{ph_change:.1f}"
    )

# System health analysis
st.subheader("System Health Analysis")

# Run the health analysis
health_analysis = analyze_system_health(water_data, 'water')

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
tab1, tab2, tab3 = st.tabs(["Flow Monitoring", "Water Quality Metrics", "Anomaly Detection"])

with tab1:
    st.subheader("Water Flow Over Time")
    
    fig = px.line(
        water_data, 
        x='timestamp', 
        y='flow_kl_h',
        title='Water Flow (kL/h)',
        labels={'timestamp': 'Time', 'flow_kl_h': 'Flow (kL/h)'}
    )
    
    # Add a different color for anomalies
    anomaly_data = water_data[water_data['anomaly']]
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
    water_data['hour'] = water_data['timestamp'].dt.hour
    
    # Group by hour and calculate statistics
    hourly_flow = water_data.groupby('hour')['flow_kl_h'].agg(['mean', 'min', 'max']).reset_index()
    
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
        fillcolor='rgba(0,128,0,0.2)',
        line=dict(width=0),
        name='Min/Max Range'
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    # Pressure monitoring
    st.subheader("Pressure Monitoring")
    
    fig = px.line(
        water_data,
        x='timestamp',
        y='pressure_bar',
        title='Water Pressure (bar)',
        labels={'timestamp': 'Time', 'pressure_bar': 'Pressure (bar)'}
    )
    
    # Add acceptable range
    fig.add_shape(
        type="rect",
        x0=water_data['timestamp'].min(),
        x1=water_data['timestamp'].max(),
        y0=4.5,
        y1=5.5,
        fillcolor="rgba(0,255,0,0.1)",
        layer="below",
        line=dict(width=0),
        name="Acceptable Range"
    )
    
    st.plotly_chart(fig, use_container_width=True)

with tab2:
    st.subheader("Water Quality Metrics")
    
    # Create columns for pH and turbidity
    col1, col2 = st.columns(2)
    
    with col1:
        # pH level trend
        fig = px.line(
            water_data,
            x='timestamp',
            y='ph_level',
            title='pH Level Trend',
            labels={'timestamp': 'Time', 'ph_level': 'pH Level'}
        )
        
        # Add acceptable range
        fig.add_shape(
            type="rect",
            x0=water_data['timestamp'].min(),
            x1=water_data['timestamp'].max(),
            y0=6.5,
            y1=8.5,
            fillcolor="rgba(0,255,0,0.1)",
            layer="below",
            line=dict(width=0),
            name="Acceptable Range"
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        # Turbidity trend
        fig = px.line(
            water_data,
            x='timestamp',
            y='turbidity_ntu',
            title='Turbidity Trend',
            labels={'timestamp': 'Time', 'turbidity_ntu': 'Turbidity (NTU)'}
        )
        
        # Add threshold line
        fig.add_shape(
            type="line",
            x0=water_data['timestamp'].min(),
            x1=water_data['timestamp'].max(),
            y0=1.0,
            y1=1.0,
            line=dict(
                color="red",
                width=2,
                dash="dash",
            ),
            name="Maximum Acceptable"
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    # Chlorine levels
    st.subheader("Chlorine Levels")
    
    fig = px.line(
        water_data,
        x='timestamp',
        y='chlorine_ppm',
        title='Chlorine Levels (ppm)',
        labels={'timestamp': 'Time', 'chlorine_ppm': 'Chlorine (ppm)'}
    )
    
    # Add acceptable range
    fig.add_shape(
        type="rect",
        x0=water_data['timestamp'].min(),
        x1=water_data['timestamp'].max(),
        y0=0.8,
        y1=1.6,
        fillcolor="rgba(0,255,0,0.1)",
        layer="below",
        line=dict(width=0),
        name="Acceptable Range"
    )
    
    st.plotly_chart(fig, use_container_width=True)

with tab3:
    st.subheader("Anomaly Detection")
    
    # Create a combined view of metrics with anomalies highlighted
    anomaly_data = water_data[water_data['anomaly']]
    
    # Flow with anomalies highlighted
    fig = px.scatter(
        water_data,
        x='timestamp',
        y='flow_kl_h',
        color='anomaly',
        title='Flow Anomalies',
        labels={'timestamp': 'Time', 'flow_kl_h': 'Flow (kL/h)', 'anomaly': 'Anomaly'},
        color_discrete_map={False: 'blue', True: 'red'}
    )
    
    # Add line connecting non-anomalous points
    normal_data = water_data[~water_data['anomaly']]
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
    
    # Display anomaly statistics
    if not anomaly_data.empty:
        st.subheader("Anomaly Statistics")
        
        anomaly_count = len(anomaly_data)
        total_count = len(water_data)
        anomaly_percent = (anomaly_count / total_count) * 100
        
        st.write(f"- **Total anomalies detected:** {anomaly_count}")
        st.write(f"- **Percentage of data points:** {anomaly_percent:.2f}%")
        
        # If there are anomalies, show a table of them
        st.subheader("Anomaly Details")
        
        # Format the anomaly data for display
        display_columns = ['timestamp', 'flow_kl_h', 'pressure_bar', 'turbidity_ntu', 'ph_level']
        formatted_anomalies = anomaly_data[display_columns].copy()
        formatted_anomalies['timestamp'] = formatted_anomalies['timestamp'].dt.strftime('%Y-%m-%d %H:%M:%S')
        
        st.dataframe(formatted_anomalies, use_container_width=True)
    else:
        st.info("No anomalies detected in the selected time period.")
