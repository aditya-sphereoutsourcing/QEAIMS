import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from utils.data_generator import get_detailed_data
from utils.anomaly_detection import analyze_system_health

st.set_page_config(
    page_title="QEAIMS - Electricity System",
    page_icon="⚡",
    layout="wide"
)

st.title("Electricity System Monitoring")
st.markdown("Real-time monitoring and analysis of the integrated electricity grid")

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

# Get detailed electricity data
electricity_data = get_detailed_data('electricity', hours=hours)

# Create system health metrics at the top
col1, col2, col3, col4 = st.columns(4)

# Get latest values
latest_load = electricity_data['load_mw'].iloc[-1]
latest_voltage = electricity_data['voltage'].iloc[-1]
latest_frequency = electricity_data['frequency'].iloc[-1]
latest_power_factor = electricity_data['power_factor'].iloc[-1]

# Calculate changes
load_change = latest_load - electricity_data['load_mw'].iloc[-2]
voltage_change = latest_voltage - electricity_data['voltage'].iloc[-2]
frequency_change = latest_frequency - electricity_data['frequency'].iloc[-2]
power_factor_change = latest_power_factor - electricity_data['power_factor'].iloc[-2]

with col1:
    st.metric(
        label="Power Load",
        value=f"{latest_load:.1f} MW",
        delta=f"{load_change:.1f} MW"
    )

with col2:
    st.metric(
        label="Voltage",
        value=f"{latest_voltage:.1f} V",
        delta=f"{voltage_change:.1f} V"
    )

with col3:
    st.metric(
        label="Frequency",
        value=f"{latest_frequency:.2f} Hz",
        delta=f"{frequency_change:.2f} Hz"
    )

with col4:
    st.metric(
        label="Power Factor",
        value=f"{latest_power_factor:.2f}",
        delta=f"{power_factor_change:.2f}"
    )

# System health analysis
st.subheader("System Health Analysis")

# Run the health analysis
health_analysis = analyze_system_health(electricity_data, 'electricity')

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
tab1, tab2, tab3 = st.tabs(["Load Monitoring", "Grid Stability Metrics", "Anomaly Detection"])

with tab1:
    st.subheader("Power Load Over Time")
    
    fig = px.line(
        electricity_data, 
        x='timestamp', 
        y='load_mw',
        title='Power Load (MW)',
        labels={'timestamp': 'Time', 'load_mw': 'Load (MW)'}
    )
    
    # Add a different color for anomalies
    anomaly_data = electricity_data[electricity_data['anomaly']]
    if not anomaly_data.empty:
        fig.add_scatter(
            x=anomaly_data['timestamp'],
            y=anomaly_data['load_mw'],
            mode='markers',
            marker=dict(color='red', size=8),
            name='Anomaly'
        )
    
    st.plotly_chart(fig, use_container_width=True)
    
    # Add daily/hourly patterns
    st.subheader("Load Patterns")
    
    # Add hour of day to the data
    electricity_data['hour'] = electricity_data['timestamp'].dt.hour
    
    # Group by hour and calculate statistics
    hourly_load = electricity_data.groupby('hour')['load_mw'].agg(['mean', 'min', 'max']).reset_index()
    
    fig = px.line(
        hourly_load,
        x='hour',
        y='mean',
        title='Average Load by Hour of Day',
        labels={'hour': 'Hour of Day', 'mean': 'Average Load (MW)'}
    )
    
    # Add range for min/max
    fig.add_scatter(
        x=hourly_load['hour'],
        y=hourly_load['min'],
        mode='lines',
        line=dict(width=0),
        showlegend=False
    )
    
    fig.add_scatter(
        x=hourly_load['hour'],
        y=hourly_load['max'],
        mode='lines',
        fill='tonexty',
        fillcolor='rgba(0,100,80,0.2)',
        line=dict(width=0),
        name='Min/Max Range'
    )
    
    st.plotly_chart(fig, use_container_width=True)

with tab2:
    st.subheader("Grid Stability Metrics")
    
    # Create columns for voltage and frequency
    col1, col2 = st.columns(2)
    
    with col1:
        # Voltage trend
        fig = px.line(
            electricity_data,
            x='timestamp',
            y='voltage',
            title='Voltage Trend',
            labels={'timestamp': 'Time', 'voltage': 'Voltage (V)'}
        )
        
        # Add acceptable range
        fig.add_shape(
            type="rect",
            x0=electricity_data['timestamp'].min(),
            x1=electricity_data['timestamp'].max(),
            y0=220,
            y1=240,
            fillcolor="rgba(0,255,0,0.1)",
            layer="below",
            line=dict(width=0),
            name="Acceptable Range"
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        # Frequency trend
        fig = px.line(
            electricity_data,
            x='timestamp',
            y='frequency',
            title='Frequency Trend',
            labels={'timestamp': 'Time', 'frequency': 'Frequency (Hz)'}
        )
        
        # Add acceptable range
        fig.add_shape(
            type="rect",
            x0=electricity_data['timestamp'].min(),
            x1=electricity_data['timestamp'].max(),
            y0=49.5,
            y1=50.5,
            fillcolor="rgba(0,255,0,0.1)",
            layer="below",
            line=dict(width=0),
            name="Acceptable Range"
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    # Power factor trend
    fig = px.line(
        electricity_data,
        x='timestamp',
        y='power_factor',
        title='Power Factor Trend',
        labels={'timestamp': 'Time', 'power_factor': 'Power Factor'}
    )
    
    # Add threshold line
    fig.add_shape(
        type="line",
        x0=electricity_data['timestamp'].min(),
        x1=electricity_data['timestamp'].max(),
        y0=0.9,
        y1=0.9,
        line=dict(
            color="red",
            width=2,
            dash="dash",
        ),
        name="Minimum Acceptable"
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    # Grid stability index
    fig = px.line(
        electricity_data,
        x='timestamp',
        y='grid_stability',
        title='Grid Stability Index',
        labels={'timestamp': 'Time', 'grid_stability': 'Stability Index (%)'}
    )
    
    st.plotly_chart(fig, use_container_width=True)

with tab3:
    st.subheader("Anomaly Detection")
    
    # Create a combined view of metrics with anomalies highlighted
    anomaly_data = electricity_data[electricity_data['anomaly']]
    
    # Load with anomalies highlighted
    fig = px.scatter(
        electricity_data,
        x='timestamp',
        y='load_mw',
        color='anomaly',
        title='Load Anomalies',
        labels={'timestamp': 'Time', 'load_mw': 'Load (MW)', 'anomaly': 'Anomaly'},
        color_discrete_map={False: 'blue', True: 'red'}
    )
    
    # Add line connecting non-anomalous points
    normal_data = electricity_data[~electricity_data['anomaly']]
    fig.add_trace(
        go.Scatter(
            x=normal_data['timestamp'],
            y=normal_data['load_mw'],
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
        total_count = len(electricity_data)
        anomaly_percent = (anomaly_count / total_count) * 100
        
        st.write(f"- **Total anomalies detected:** {anomaly_count}")
        st.write(f"- **Percentage of data points:** {anomaly_percent:.2f}%")
        
        # If there are anomalies, show a table of them
        st.subheader("Anomaly Details")
        
        # Format the anomaly data for display
        display_columns = ['timestamp', 'load_mw', 'voltage', 'frequency', 'power_factor']
        formatted_anomalies = anomaly_data[display_columns].copy()
        formatted_anomalies['timestamp'] = formatted_anomalies['timestamp'].dt.strftime('%Y-%m-%d %H:%M:%S')
        
        st.dataframe(formatted_anomalies, use_container_width=True)
    else:
        st.info("No anomalies detected in the selected time period.")
