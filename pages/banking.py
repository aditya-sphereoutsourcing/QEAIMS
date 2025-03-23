import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from utils.data_generator import get_detailed_data
from utils.anomaly_detection import analyze_system_health

st.set_page_config(
    page_title="QEAIMS - Banking System",
    page_icon="🏦",
    layout="wide"
)

st.title("Banking System Monitoring")
st.markdown("Real-time monitoring and analysis of the integrated banking transaction system")

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

# Get detailed banking data
banking_data = get_detailed_data('banking', hours=hours)

# Create system health metrics at the top
col1, col2, col3, col4 = st.columns(4)

# Get latest values
latest_tps = banking_data['transactions_per_second'].iloc[-1]
latest_response = banking_data['response_time_ms'].iloc[-1]
latest_success = banking_data['success_rate'].iloc[-1]
latest_error = banking_data['error_rate'].iloc[-1]

# Calculate changes
tps_change = latest_tps - banking_data['transactions_per_second'].iloc[-2]
response_change = latest_response - banking_data['response_time_ms'].iloc[-2]
success_change = latest_success - banking_data['success_rate'].iloc[-2]
error_change = latest_error - banking_data['error_rate'].iloc[-2]

with col1:
    st.metric(
        label="Transactions Per Second",
        value=f"{latest_tps:.0f} tps",
        delta=f"{tps_change:.0f} tps"
    )

with col2:
    st.metric(
        label="Response Time",
        value=f"{latest_response:.1f} ms",
        delta=f"{response_change:.1f} ms",
        delta_color="inverse"  # Lower is better for response time
    )

with col3:
    st.metric(
        label="Success Rate",
        value=f"{latest_success:.2f}%",
        delta=f"{success_change:.2f}%"
    )

with col4:
    st.metric(
        label="Error Rate",
        value=f"{latest_error:.2f}%",
        delta=f"{error_change:.2f}%",
        delta_color="inverse"  # Lower is better for error rate
    )

# System health analysis
st.subheader("System Health Analysis")

# Run the health analysis
health_analysis = analyze_system_health(banking_data, 'banking')

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
tab1, tab2, tab3 = st.tabs(["Transaction Monitoring", "Performance Metrics", "Anomaly Detection"])

with tab1:
    st.subheader("Transactions Per Second Over Time")
    
    fig = px.line(
        banking_data, 
        x='timestamp', 
        y='transactions_per_second',
        title='Transaction Volume (TPS)',
        labels={'timestamp': 'Time', 'transactions_per_second': 'Transactions Per Second'}
    )
    
    # Add a different color for anomalies
    anomaly_data = banking_data[banking_data['anomaly']]
    if not anomaly_data.empty:
        fig.add_scatter(
            x=anomaly_data['timestamp'],
            y=anomaly_data['transactions_per_second'],
            mode='markers',
            marker=dict(color='red', size=8),
            name='Anomaly'
        )
    
    st.plotly_chart(fig, use_container_width=True)
    
    # Add daily/hourly patterns
    st.subheader("Transaction Patterns")
    
    # Add hour of day to the data
    banking_data['hour'] = banking_data['timestamp'].dt.hour
    
    # Group by hour and calculate statistics
    hourly_tps = banking_data.groupby('hour')['transactions_per_second'].agg(['mean', 'min', 'max']).reset_index()
    
    fig = px.line(
        hourly_tps,
        x='hour',
        y='mean',
        title='Average Transactions by Hour of Day',
        labels={'hour': 'Hour of Day', 'mean': 'Average TPS'}
    )
    
    # Add range for min/max
    fig.add_scatter(
        x=hourly_tps['hour'],
        y=hourly_tps['min'],
        mode='lines',
        line=dict(width=0),
        showlegend=False
    )
    
    fig.add_scatter(
        x=hourly_tps['hour'],
        y=hourly_tps['max'],
        mode='lines',
        fill='tonexty',
        fillcolor='rgba(128,0,128,0.2)',
        line=dict(width=0),
        name='Min/Max Range'
    )
    
    st.plotly_chart(fig, use_container_width=True)

with tab2:
    st.subheader("System Performance Metrics")
    
    # Create columns for response time and success rate
    col1, col2 = st.columns(2)
    
    with col1:
        # Response time trend
        fig = px.line(
            banking_data,
            x='timestamp',
            y='response_time_ms',
            title='Response Time Trend',
            labels={'timestamp': 'Time', 'response_time_ms': 'Response Time (ms)'}
        )
        
        # Add threshold line
        fig.add_shape(
            type="line",
            x0=banking_data['timestamp'].min(),
            x1=banking_data['timestamp'].max(),
            y0=300,
            y1=300,
            line=dict(
                color="red",
                width=2,
                dash="dash",
            ),
            name="Maximum Acceptable"
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        # Success rate trend
        fig = px.line(
            banking_data,
            x='timestamp',
            y='success_rate',
            title='Transaction Success Rate',
            labels={'timestamp': 'Time', 'success_rate': 'Success Rate (%)'}
        )
        
        # Add threshold line
        fig.add_shape(
            type="line",
            x0=banking_data['timestamp'].min(),
            x1=banking_data['timestamp'].max(),
            y0=99,
            y1=99,
            line=dict(
                color="red",
                width=2,
                dash="dash",
            ),
            name="Minimum Acceptable"
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    # Error rate and security index
    st.subheader("Error Rate and Security Index")
    
    # Create columns for error rate and security index
    col1, col2 = st.columns(2)
    
    with col1:
        # Error rate trend
        fig = px.line(
            banking_data,
            x='timestamp',
            y='error_rate',
            title='Transaction Error Rate',
            labels={'timestamp': 'Time', 'error_rate': 'Error Rate (%)'}
        )
        
        # Add threshold line
        fig.add_shape(
            type="line",
            x0=banking_data['timestamp'].min(),
            x1=banking_data['timestamp'].max(),
            y0=1,
            y1=1,
            line=dict(
                color="red",
                width=2,
                dash="dash",
            ),
            name="Maximum Acceptable"
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        # Security index trend
        fig = px.line(
            banking_data,
            x='timestamp',
            y='security_index',
            title='Security Index',
            labels={'timestamp': 'Time', 'security_index': 'Security Index (%)'}
        )
        
        # Add threshold line
        fig.add_shape(
            type="line",
            x0=banking_data['timestamp'].min(),
            x1=banking_data['timestamp'].max(),
            y0=95,
            y1=95,
            line=dict(
                color="red",
                width=2,
                dash="dash",
            ),
            name="Minimum Acceptable"
        )
        
        st.plotly_chart(fig, use_container_width=True)

with tab3:
    st.subheader("Anomaly Detection")
    
    # Create a combined view of metrics with anomalies highlighted
    anomaly_data = banking_data[banking_data['anomaly']]
    
    # Transactions with anomalies highlighted
    fig = px.scatter(
        banking_data,
        x='timestamp',
        y='transactions_per_second',
        color='anomaly',
        title='Transaction Anomalies',
        labels={'timestamp': 'Time', 'transactions_per_second': 'Transactions Per Second', 'anomaly': 'Anomaly'},
        color_discrete_map={False: 'blue', True: 'red'}
    )
    
    # Add line connecting non-anomalous points
    normal_data = banking_data[~banking_data['anomaly']]
    fig.add_trace(
        go.Scatter(
            x=normal_data['timestamp'],
            y=normal_data['transactions_per_second'],
            mode='lines',
            line=dict(color='blue'),
            showlegend=False
        )
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    # Response time with anomalies
    fig = px.scatter(
        banking_data,
        x='timestamp',
        y='response_time_ms',
        color='anomaly',
        title='Response Time Anomalies',
        labels={'timestamp': 'Time', 'response_time_ms': 'Response Time (ms)', 'anomaly': 'Anomaly'},
        color_discrete_map={False: 'green', True: 'red'}
    )
    
    # Add line connecting non-anomalous points
    fig.add_trace(
        go.Scatter(
            x=normal_data['timestamp'],
            y=normal_data['response_time_ms'],
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
        total_count = len(banking_data)
        anomaly_percent = (anomaly_count / total_count) * 100
        
        st.write(f"- **Total anomalies detected:** {anomaly_count}")
        st.write(f"- **Percentage of data points:** {anomaly_percent:.2f}%")
        
        # If there are anomalies, show a table of them
        st.subheader("Anomaly Details")
        
        # Format the anomaly data for display
        display_columns = ['timestamp', 'transactions_per_second', 'response_time_ms', 'success_rate', 'error_rate']
        formatted_anomalies = anomaly_data[display_columns].copy()
        formatted_anomalies['timestamp'] = formatted_anomalies['timestamp'].dt.strftime('%Y-%m-%d %H:%M:%S')
        
        st.dataframe(formatted_anomalies, use_container_width=True)
    else:
        st.info("No anomalies detected in the selected time period.")
