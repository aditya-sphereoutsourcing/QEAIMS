import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from utils.data_generator import get_latest_data, get_historical_data, get_detailed_data
from utils.anomaly_detection import detect_anomalies, analyze_system_health

st.set_page_config(
    page_title="QEAIMS - AI Recommendations",
    page_icon="🤖",
    layout="wide"
)

st.title("AI Recommendation Engine")
st.markdown("Intelligent analysis of system anomalies with actionable recommendations for resolving detected issues")

# Get data for analysis
latest_data = get_latest_data()
historical_data = get_historical_data(hours=24)

# Create main layout
col1, col2 = st.columns([1, 2])

with col1:
    st.subheader("System Analysis")
    
    # System selection
    system = st.selectbox(
        "Select System to Analyze:",
        ["electricity", "water", "sewage", "banking"],
        format_func=lambda x: x.capitalize()
    )
    
    # Time range selection
    time_range = st.selectbox(
        "Analysis Time Range:",
        [6, 12, 24, 48],
        index=2,
        format_func=lambda x: f"Last {x} hours"
    )
    
    # Analysis depth
    analysis_depth = st.slider(
        "Analysis Depth:",
        min_value=1,
        max_value=5,
        value=3,
        help="Higher values provide more detailed analysis but may take longer"
    )
    
    # Run analysis button
    run_analysis = st.button("Run AI Analysis")
    
    # Display system health metrics
    st.subheader("Current Status")
    
    # Get system health from latest data
    if system == "electricity":
        health_score = latest_data["electricity"]["health_score"]
        # Determine anomaly based on health score threshold
        is_anomaly = health_score < 75
    elif system == "water":
        health_score = latest_data["water"]["health_score"]
        is_anomaly = health_score < 75
    elif system == "sewage":
        health_score = latest_data["sewage"]["health_score"]
        is_anomaly = health_score < 75
    elif system == "banking":
        health_score = latest_data["banking"]["health_score"]
        is_anomaly = health_score < 75
    
    # Display health score with appropriate color
    if health_score >= 90:
        st.success(f"{system.capitalize()} System Health: {health_score:.1f}%")
    elif health_score >= 70:
        st.warning(f"{system.capitalize()} System Health: {health_score:.1f}%")
    else:
        st.error(f"{system.capitalize()} System Health: {health_score:.1f}%")
    
    # Display anomaly status
    if is_anomaly:
        st.error("⚠️ Anomaly Detected")
    else:
        st.success("✅ Normal Operation")

# Main content area
with col2:
    if run_analysis:
        # Display analysis in progress spinner
        with st.spinner(f"Running AI analysis on {system} system..."):
            # Get detailed data for the selected system
            detailed_data = get_detailed_data(system, hours=time_range)
            
            # Run anomaly detection
            if system == "electricity":
                anomaly_columns = ["load_mw", "voltage", "frequency", "power_factor"]
            elif system == "water":
                anomaly_columns = ["flow_kl_h", "pressure_bar", "turbidity_ntu", "ph_level"]
            elif system == "sewage":
                anomaly_columns = ["flow_kl_h", "treatment_efficiency", "contaminant_level", "dissolved_oxygen"]
            elif system == "banking":
                anomaly_columns = ["transactions_per_second", "response_time_ms", "success_rate", "error_rate"]
            
            # Detect anomalies
            anomalies = detect_anomalies(detailed_data, columns=anomaly_columns)
            
            # Analyze system health
            health_analysis = analyze_system_health(detailed_data, system)
            
            # Display analysis results
            st.subheader("AI Analysis Results")
            
            # Display health assessment
            status_color = "green" if health_analysis["status"] == "Healthy" else "orange" if health_analysis["status"] == "Warning" else "red"
            st.markdown(f"### System Status: <span style='color:{status_color}'>{health_analysis['status']}</span>", unsafe_allow_html=True)
            
            # Display confidence score
            confidence = 85 + np.random.randint(-5, 6)  # Simulated confidence score
            st.progress(confidence / 100)
            st.caption(f"Analysis Confidence: {confidence}%")
            
            # Display recommendations
            st.subheader("AI Recommendations")
            
            # Generate recommendations based on system and health status
            recommendations = []
            
            if system == "electricity":
                if health_analysis["status"] == "Critical":
                    recommendations = [
                        "Implement immediate load shedding to stabilize the grid",
                        "Activate backup generation capacity",
                        "Isolate unstable transmission lines",
                        "Prepare for rolling blackouts in non-critical areas"
                    ]
                elif health_analysis["status"] == "Warning":
                    recommendations = [
                        "Reduce load on substations showing instability",
                        "Balance phase distribution across the network",
                        "Monitor frequency fluctuations on transmission lines",
                        "Prepare backup generation systems for standby"
                    ]
                else:
                    recommendations = [
                        "Continue normal operations",
                        "Schedule preventative maintenance during off-peak hours",
                        "Optimize load distribution for efficiency",
                        "Review contingency plans for potential weather events"
                    ]
            
            elif system == "water":
                if health_analysis["status"] == "Critical":
                    recommendations = [
                        "Activate emergency water treatment protocols",
                        "Issue boil water advisory for affected areas",
                        "Redirect flow from secondary reservoirs",
                        "Isolate contaminated sections of the distribution network"
                    ]
                elif health_analysis["status"] == "Warning":
                    recommendations = [
                        "Increase chlorination levels at treatment plants",
                        "Monitor pressure fluctuations in the main distribution lines",
                        "Prepare for potential conservation measures",
                        "Check pump station performance and efficiency"
                    ]
                else:
                    recommendations = [
                        "Maintain current operations",
                        "Conduct regular water quality sampling",
                        "Schedule hydrant flushing in lower usage areas",
                        "Optimize reservoir levels for upcoming demand patterns"
                    ]
            
            elif system == "sewage":
                if health_analysis["status"] == "Critical":
                    recommendations = [
                        "Activate emergency overflow containment systems",
                        "Redirect flow to backup treatment facilities",
                        "Deploy mobile pumping units to affected areas",
                        "Issue public health advisory for potentially affected waterways"
                    ]
                elif health_analysis["status"] == "Warning":
                    recommendations = [
                        "Increase treatment capacity at primary facilities",
                        "Monitor influent composition for industrial contaminants",
                        "Prepare for potential high-flow events",
                        "Check lift station performance across the network"
                    ]
                else:
                    recommendations = [
                        "Maintain current operations",
                        "Schedule routine maintenance of lift stations",
                        "Optimize chemical usage in treatment processes",
                        "Review capacity plans for upcoming seasonal changes"
                    ]
            
            elif system == "banking":
                if health_analysis["status"] == "Critical":
                    recommendations = [
                        "Activate disaster recovery protocols",
                        "Fail over to backup data centers",
                        "Implement transaction rate limiting to maintain core services",
                        "Deploy security countermeasures against potential cyber threats"
                    ]
                elif health_analysis["status"] == "Warning":
                    recommendations = [
                        "Scale up processing capacity in affected subsystems",
                        "Investigate transaction latency patterns",
                        "Prepare backup systems for potential failover",
                        "Review security logs for anomalous activity patterns"
                    ]
                else:
                    recommendations = [
                        "Maintain current operations",
                        "Schedule routine system maintenance during off-peak hours",
                        "Optimize database query performance",
                        "Review disaster recovery procedures with IT teams"
                    ]
            
            # Display recommendations with priority levels
            priorities = ["Critical", "High", "Medium", "Low"][:len(recommendations)]
            
            for i, (rec, pri) in enumerate(zip(recommendations, priorities)):
                priority_color = "red" if pri == "Critical" else "orange" if pri == "High" else "blue" if pri == "Medium" else "green"
                st.markdown(f"**Priority {i+1} ({pri}):** <span style='color:{priority_color}'>{rec}</span>", unsafe_allow_html=True)
            
            # Show anomaly details
            st.subheader("Anomaly Details")
            
            # Count anomalies
            anomaly_count = anomalies.sum()
            
            if anomaly_count > 0:
                # Extract anomalous data points
                anomalous_data = detailed_data[anomalies].copy()
                
                # Display anomaly count
                st.warning(f"Detected {anomaly_count} anomalous data points out of {len(detailed_data)}")
                
                # Show example anomalies
                st.dataframe(anomalous_data.head(5))
                
                # Generate time series plot with anomalies highlighted
                primary_metric = anomaly_columns[0]  # Use the first metric as primary for visualization
                
                fig = go.Figure()
                
                # Add normal data points
                fig.add_trace(go.Scatter(
                    x=detailed_data.loc[~anomalies, "timestamp"],
                    y=detailed_data.loc[~anomalies, primary_metric],
                    mode="lines",
                    name="Normal Data",
                    line=dict(color="blue")
                ))
                
                # Add anomalous points
                fig.add_trace(go.Scatter(
                    x=detailed_data.loc[anomalies, "timestamp"],
                    y=detailed_data.loc[anomalies, primary_metric],
                    mode="markers",
                    name="Anomalies",
                    marker=dict(color="red", size=10)
                ))
                
                # Update layout
                fig.update_layout(
                    title=f"{primary_metric.replace('_', ' ').title()} with Detected Anomalies",
                    xaxis_title="Time",
                    yaxis_title=primary_metric.replace('_', ' ').title(),
                    legend_title="Data Points"
                )
                
                st.plotly_chart(fig, use_container_width=True)
                
                # Show contributing factors
                st.subheader("Contributing Factors")
                
                # Determine which features are most associated with anomalies
                feature_importance = {}
                
                for col in anomaly_columns:
                    # Calculate the difference between anomalous and normal values
                    normal_mean = detailed_data.loc[~anomalies, col].mean()
                    anomaly_mean = detailed_data.loc[anomalies, col].mean()
                    
                    # Calculate the percentage difference
                    pct_diff = abs((anomaly_mean - normal_mean) / normal_mean * 100)
                    
                    feature_importance[col] = pct_diff
                
                # Create a dataframe for the feature importance
                importance_df = pd.DataFrame({
                    "Feature": list(feature_importance.keys()),
                    "Importance": list(feature_importance.values())
                })
                
                # Sort by importance
                importance_df = importance_df.sort_values("Importance", ascending=False)
                
                # Create bar chart
                fig = px.bar(
                    importance_df,
                    x="Feature",
                    y="Importance",
                    title="Feature Contribution to Anomalies",
                    labels={"Feature": "System Parameter", "Importance": "Contribution (%)"},
                    color="Importance",
                    color_continuous_scale="Reds"
                )
                
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.success("No anomalies detected in the selected time period")
            
            # Predictive insights section
            st.subheader("Predictive Insights")
            
            # Simulate predictive analytics
            prediction_hours = 6
            confidence_high = 90 - np.random.randint(0, 10)
            confidence_med = 75 - np.random.randint(0, 15)
            
            # Generate forecast messages based on system status
            if health_analysis["status"] == "Critical":
                forecast = f"System conditions predicted to worsen in the next {prediction_hours} hours without intervention."
                proba = np.random.randint(75, 96)
                st.error(f"⚠️ {forecast} (Confidence: {proba}%)")
            elif health_analysis["status"] == "Warning":
                forecast = f"Conditions may stabilize within {prediction_hours} hours if recommended actions are taken."
                proba = np.random.randint(60, 86)
                st.warning(f"⚠️ {forecast} (Confidence: {proba}%)")
            else:
                forecast = f"System predicted to maintain normal operations for the next {prediction_hours} hours."
                proba = np.random.randint(85, 99)
                st.info(f"ℹ️ {forecast} (Confidence: {proba}%)")
            
            # Display completion message
            st.success("AI analysis complete!")
    else:
        # Display instructions
        st.info("Select a system and time range, then click 'Run AI Analysis' to generate intelligent recommendations.")
        
        # Display example insights
        st.subheader("AI Analysis Capabilities")
        
        capabilities = [
            "Anomaly Detection: Identify unusual patterns in system behavior",
            "Root Cause Analysis: Determine the underlying causes of detected anomalies",
            "Predictive Insights: Forecast potential issues before they occur",
            "Prioritized Recommendations: Receive actionable steps based on severity and impact",
            "Cross-System Impact Assessment: Understand how issues in one utility affect others"
        ]
        
        for cap in capabilities:
            st.markdown(f"- {cap}")
            
        # Example visualization
        st.subheader("Sample Analysis Output")
        
        # Create sample time series data
        dates = pd.date_range(start="2025-03-01", periods=48, freq="H")
        values = [100 + 10 * np.sin(i/5) + np.random.normal(0, 2) for i in range(48)]
        
        # Introduce some artificial anomalies
        anomaly_indices = [10, 25, 35]
        for idx in anomaly_indices:
            values[idx] = values[idx] + 25 if np.random.random() > 0.5 else values[idx] - 25
        
        # Create sample dataframe
        sample_df = pd.DataFrame({"timestamp": dates, "value": values})
        
        # Create sample anomaly mask
        anomaly_mask = [i in anomaly_indices for i in range(48)]
        
        # Plot sample time series with anomalies
        fig = go.Figure()
        
        # Add normal data points
        fig.add_trace(go.Scatter(
            x=sample_df.loc[~pd.Series(anomaly_mask), "timestamp"],
            y=sample_df.loc[~pd.Series(anomaly_mask), "value"],
            mode="lines",
            name="Normal Data",
            line=dict(color="blue")
        ))
        
        # Add anomalous points
        fig.add_trace(go.Scatter(
            x=sample_df.loc[pd.Series(anomaly_mask), "timestamp"],
            y=sample_df.loc[pd.Series(anomaly_mask), "value"],
            mode="markers",
            name="Detected Anomalies",
            marker=dict(color="red", size=10)
        ))
        
        # Update layout
        fig.update_layout(
            title="Example: Anomaly Detection in System Metrics",
            xaxis_title="Time",
            yaxis_title="Metric Value",
            legend_title="Data Points"
        )
        
        st.plotly_chart(fig, use_container_width=True)