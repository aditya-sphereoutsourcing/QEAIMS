import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import time
from utils.data_generator import get_fault_simulation_data
from utils.network_graph import create_system_graph, simulate_fault, create_network_visualization

st.set_page_config(
    page_title="QEAIMS - System Recovery",
    page_icon="🔄",
    layout="wide"
)

st.title("System Recovery Visualization")
st.markdown("Visualize how the QEAIMS system autonomously recovers from faults through a multi-stage self-healing process")

# Get fault simulation data
fault_data = get_fault_simulation_data()

# Create columns for controls and visualization
col1, col2 = st.columns([1, 3])

with col1:
    st.subheader("Recovery Controls")
    
    # Fault scenario selection
    fault_type = st.selectbox(
        "Select Fault Scenario:",
        [
            "power_outage",
            "water_main_break",
            "cyber_attack",
            "sewage_overflow",
            "grid_instability"
        ],
        format_func=lambda x: x.replace('_', ' ').title()
    )
    
    # Add simulation duration slider
    recovery_time = st.slider(
        "Recovery Duration (minutes):",
        min_value=5,
        max_value=60,
        value=15,
        step=5
    )
    
    # Start recovery simulation button
    start_recovery = st.button("Start Recovery Simulation")
    
    # Display recovery stages
    st.subheader("Recovery Stages")
    stages = [
        "1. Fault Detection",
        "2. Impact Assessment",
        "3. Resource Allocation",
        "4. Isolation of Affected Areas",
        "5. Deployment of Recovery Mechanisms",
        "6. Restoration of Services",
        "7. Verification and Optimization"
    ]
    
    # Create placeholder for active stage
    active_stage = st.empty()
    
    # Progress container
    progress_container = st.container()
    
# Main visualization area
with col2:
    st.subheader("System Recovery Progress")
    
    # Network visualization placeholder
    network_viz = st.empty()
    
    # Create columns for system metrics
    electricity_col, water_col, sewage_col, banking_col = st.columns(4)
    
    with electricity_col:
        electricity_metric = st.empty()
    
    with water_col:
        water_metric = st.empty()
        
    with sewage_col:
        sewage_metric = st.empty()
        
    with banking_col:
        banking_metric = st.empty()
    
    # Recovery timeline chart
    timeline_chart = st.empty()
    
    # Recovery details
    recovery_details = st.expander("Recovery Process Details")
    with recovery_details:
        details_container = st.container()

# When the recovery simulation is started
if start_recovery:
    # Get the fault scenario
    scenario = fault_data['scenarios'][fault_type]
    fault_info = simulate_fault(fault_type)
    normal_data = fault_data['normal']
    fault_state_data = scenario['data']
    
    # Set up progress tracking
    recovery_steps = len(stages)
    step_duration = recovery_time * 60 / recovery_steps  # step duration in seconds
    
    # Simulate recovery process
    with st.spinner(f"Simulating recovery from {scenario['description']}..."):
        # Calculate transition steps for each metric
        transition_steps = 20  # number of steps for transition animation
        
        # Helper function to calculate transition values
        def calculate_transition(start, end, steps):
            return np.linspace(start, end, steps)
        
        # Transition values for each system's health score
        electricity_health_transition = calculate_transition(
            fault_state_data['electricity']['health_score'],
            normal_data['electricity']['health_score'],
            transition_steps
        )
        
        water_health_transition = calculate_transition(
            fault_state_data['water']['health_score'],
            normal_data['water']['health_score'],
            transition_steps
        )
        
        sewage_health_transition = calculate_transition(
            fault_state_data['sewage']['health_score'],
            normal_data['sewage']['health_score'],
            transition_steps
        )
        
        banking_health_transition = calculate_transition(
            fault_state_data['banking']['health_score'],
            normal_data['banking']['health_score'],
            transition_steps
        )
        
        # Timeline data for visualization
        timeline_data = {
            'Stage': [],
            'Start': [],
            'End': [],
            'Status': []
        }
        
        # Process each recovery stage
        for i, stage in enumerate(stages):
            # Calculate elapsed and remaining time
            elapsed = i * step_duration
            remaining = recovery_time * 60 - elapsed
            
            # Update active stage display
            active_stage.markdown(f"**Current Stage:** {stage}")
            
            # Update progress container
            with progress_container:
                # Display progress bar
                st.progress((i + 1) / recovery_steps)
                
                # Display time remaining
                minutes_remaining = int(remaining // 60)
                seconds_remaining = int(remaining % 60)
                st.write(f"Time remaining: {minutes_remaining} minutes, {seconds_remaining} seconds")
            
            # Update timeline data
            timeline_data['Stage'].append(stage)
            timeline_data['Start'].append(elapsed / 60)  # convert to minutes
            timeline_data['End'].append((elapsed + step_duration) / 60)  # convert to minutes
            timeline_data['Status'].append('Completed' if i < 1 else 'In Progress' if i == 1 else 'Pending')
            
            # Create timeline chart
            timeline_df = pd.DataFrame(timeline_data)
            fig = px.timeline(
                timeline_df, 
                x_start="Start", 
                x_end="End", 
                y="Stage",
                color="Status",
                color_discrete_map={
                    'Completed': '#00FF00',
                    'In Progress': '#FFAA00',
                    'Pending': '#AAAAAA'
                },
                title="Recovery Process Timeline"
            )
            fig.update_yaxes(autorange="reversed")
            timeline_chart.plotly_chart(fig, use_container_width=True)
            
            # Animate system metrics recovery based on the stage
            transition_per_stage = int(transition_steps / recovery_steps)
            start_idx = i * transition_per_stage
            end_idx = min((i + 1) * transition_per_stage, transition_steps - 1)
            
            for j in range(start_idx, end_idx + 1):
                # Update metrics with transition values
                electricity_metric.metric(
                    "Electricity Health",
                    f"{electricity_health_transition[j]:.1f}%",
                    f"{electricity_health_transition[j] - fault_state_data['electricity']['health_score']:.1f}%"
                )
                
                water_metric.metric(
                    "Water Health",
                    f"{water_health_transition[j]:.1f}%",
                    f"{water_health_transition[j] - fault_state_data['water']['health_score']:.1f}%"
                )
                
                sewage_metric.metric(
                    "Sewage Health",
                    f"{sewage_health_transition[j]:.1f}%",
                    f"{sewage_health_transition[j] - fault_state_data['sewage']['health_score']:.1f}%"
                )
                
                banking_metric.metric(
                    "Banking Health",
                    f"{banking_health_transition[j]:.1f}%",
                    f"{banking_health_transition[j] - fault_state_data['banking']['health_score']:.1f}%"
                )
                
                # Update network visualization
                # Create a copy of the fault graph and gradually update node colors and status
                recovery_progress = j / (transition_steps - 1)
                
                # For demo, just show the original fault visualization
                if i == 0:
                    # Initial fault state
                    network_fig = create_network_visualization(
                        fault_info['graph'], 
                        f"Network State: {fault_info['description']} (Detection Phase)"
                    )
                    network_viz.plotly_chart(network_fig, use_container_width=True)
                elif i < recovery_steps - 1:
                    # Intermediate recovery state - would be better with actual gradual recovery logic
                    network_fig = create_network_visualization(
                        fault_info['graph'], 
                        f"Network State: {fault_info['description']} (Recovery Phase {i+1}/{recovery_steps-1})"
                    )
                    network_viz.plotly_chart(network_fig, use_container_width=True)
                else:
                    # Final recovered state
                    G_normal = create_system_graph()
                    network_fig = create_network_visualization(
                        G_normal, 
                        "Network State: Fully Recovered"
                    )
                    network_viz.plotly_chart(network_fig, use_container_width=True)
                
                # Add recovery details
                with details_container:
                    recovery_actions = {
                        0: "Monitoring systems have detected anomalies in the network.",
                        1: "Analyzing the scope and severity of the fault.",
                        2: "Allocating necessary resources for recovery operations.",
                        3: "Isolating affected components to prevent cascading failures.",
                        4: "Deploying automated and manual recovery mechanisms.",
                        5: "Gradually restoring services in order of priority.",
                        6: "Verifying system integrity and optimizing performance."
                    }
                    
                    st.write(f"**Stage {i+1}:** {stages[i]}")
                    st.write(recovery_actions.get(i, ""))
                    
                    if i > 0:
                        st.write("Completed actions:")
                        for k in range(i):
                            st.write(f"✓ {stages[k]}")
                
                # Pause to create animation effect
                time.sleep(step_duration / (end_idx - start_idx + 1))
            
            # Add brief pause between stages
            time.sleep(0.5)
    
    # Display completion message
    st.success(f"Recovery simulation complete! System restored after {recovery_time} minutes.")
    
    # Show final state
    electricity_metric.metric(
        "Electricity Health",
        f"{normal_data['electricity']['health_score']:.1f}%",
        f"{normal_data['electricity']['health_score'] - fault_state_data['electricity']['health_score']:.1f}%"
    )
    
    water_metric.metric(
        "Water Health",
        f"{normal_data['water']['health_score']:.1f}%",
        f"{normal_data['water']['health_score'] - fault_state_data['water']['health_score']:.1f}%"
    )
    
    sewage_metric.metric(
        "Sewage Health",
        f"{normal_data['sewage']['health_score']:.1f}%",
        f"{normal_data['sewage']['health_score'] - fault_state_data['sewage']['health_score']:.1f}%"
    )
    
    banking_metric.metric(
        "Banking Health",
        f"{normal_data['banking']['health_score']:.1f}%",
        f"{normal_data['banking']['health_score'] - fault_state_data['banking']['health_score']:.1f}%"
    )
    
    # Update timeline to show all stages completed
    timeline_data = {
        'Stage': stages,
        'Start': [i * step_duration / 60 for i in range(len(stages))],
        'End': [(i + 1) * step_duration / 60 for i in range(len(stages))],
        'Status': ['Completed'] * len(stages)
    }
    
    timeline_df = pd.DataFrame(timeline_data)
    fig = px.timeline(
        timeline_df, 
        x_start="Start", 
        x_end="End", 
        y="Stage",
        color="Status",
        color_discrete_map={
            'Completed': '#00FF00',
            'In Progress': '#FFAA00',
            'Pending': '#AAAAAA'
        },
        title="Recovery Process Timeline"
    )
    fig.update_yaxes(autorange="reversed")
    timeline_chart.plotly_chart(fig, use_container_width=True)
else:
    # Display instructions when not running a simulation
    network_viz.info("Select a fault scenario and click 'Start Recovery Simulation' to begin.")
    
    # Display empty metrics placeholders
    electricity_metric.metric("Electricity Health", "N/A", "0%")
    water_metric.metric("Water Health", "N/A", "0%")
    sewage_metric.metric("Sewage Health", "N/A", "0%")
    banking_metric.metric("Banking Health", "N/A", "0%")