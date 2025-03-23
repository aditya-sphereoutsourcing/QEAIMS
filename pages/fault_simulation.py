import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import time
from utils.data_generator import get_fault_simulation_data
from utils.network_graph import create_system_graph, simulate_fault, create_network_visualization

st.set_page_config(
    page_title="QEAIMS - Fault Simulation",
    page_icon="⚠️",
    layout="wide"
)

st.title("Fault Simulation and Self-Healing")
st.markdown("Simulate various fault scenarios to visualize how the QEAIMS system detects, isolates, and self-heals critical infrastructure issues")

# Get fault simulation data
fault_data = get_fault_simulation_data()

# Create columns for simulation controls
col1, col2 = st.columns([1, 3])

with col1:
    st.subheader("Simulation Controls")
    
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
    sim_duration = st.slider(
        "Simulation Duration (minutes):",
        min_value=5,
        max_value=60,
        value=15,
        step=5
    )
    
    # Self-healing toggle
    enable_healing = st.checkbox("Enable Self-Healing", value=True)
    
    # Simulation button
    if st.button("Run Simulation", type="primary"):
        st.session_state.simulation_running = True
        st.session_state.simulation_start_time = time.time()
        st.session_state.simulation_end_time = time.time() + (sim_duration * 60)
        st.session_state.fault_type = fault_type
        st.session_state.enable_healing = enable_healing
        st.rerun()

with col2:
    # Display fault description
    if 'simulation_running' not in st.session_state:
        st.info("Select a fault scenario and click 'Run Simulation' to begin.")
        # Display empty simulation container
        st.empty()
    else:
        # Get simulation fault info
        fault_info = simulate_fault(st.session_state.fault_type)
        
        # Display a notification
        st.warning(f"Active Simulation: {fault_info['description']}")
        
        # Create progress indicator
        current_time = time.time()
        total_duration = st.session_state.simulation_end_time - st.session_state.simulation_start_time
        elapsed_time = current_time - st.session_state.simulation_start_time
        
        if current_time < st.session_state.simulation_end_time:
            progress = elapsed_time / total_duration
            remaining = st.session_state.simulation_end_time - current_time
            
            st.progress(progress)
            st.write(f"Simulation in progress: {int(remaining/60)} minutes, {int(remaining%60)} seconds remaining")
            
            # Add simulation reset button
            if st.button("Stop Simulation"):
                st.session_state.pop('simulation_running')
                st.rerun()
        else:
            # Simulation complete
            st.success("Simulation Complete")
            st.progress(1.0)
            
            # Add simulation reset button
            if st.button("Reset Simulation"):
                st.session_state.pop('simulation_running')
                st.rerun()

# Main simulation display
if 'simulation_running' in st.session_state:
    fault_info = simulate_fault(st.session_state.fault_type)
    
    # Create tabs for different views
    tab1, tab2, tab3 = st.tabs(["Network Impact", "System Metrics", "Recovery Process"])
    
    with tab1:
        st.subheader("Network Impact Visualization")
        
        # Display the network graph with affected nodes
        network_fig = create_network_visualization(fault_info['graph'], f"Network Impact: {fault_info['description']}")
        st.plotly_chart(network_fig, use_container_width=True)
        
        # Display affected systems table
        st.subheader("Affected Systems")
        
        # Create status summary table
        status_data = {
            'System': ['Electricity Grid', 'Water System', 'Sewage System', 'Banking Network'],
            'Status': [
                fault_info['anomaly_status']['electricity'],
                fault_info['anomaly_status']['water'],
                fault_info['anomaly_status']['sewage'],
                fault_info['anomaly_status']['banking']
            ],
            'Impact Level': [
                'High' if 'electricity' in fault_info['systems'] else 'Low',
                'High' if 'water' in fault_info['systems'] else 'Low',
                'High' if 'sewage' in fault_info['systems'] else 'Low',
                'High' if 'banking' in fault_info['systems'] else 'Low'
            ],
            'Autonomous Response': [
                'Fault Isolation Active' if 'electricity' in fault_info['systems'] else 'Monitoring',
                'Fault Isolation Active' if 'water' in fault_info['systems'] else 'Monitoring',
                'Fault Isolation Active' if 'sewage' in fault_info['systems'] else 'Monitoring',
                'Fault Isolation Active' if 'banking' in fault_info['systems'] else 'Monitoring'
            ]
        }
        
        # Create dataframe
        status_df = pd.DataFrame(status_data)
        
        # Display as table
        st.table(status_df)
    
    with tab2:
        st.subheader("System Metrics During Fault")
        
        # Create columns for normal vs. fault state metrics
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("Normal State")
            
            # Get normal data
            normal_data = fault_data['normal']
            
            # Create metrics for normal state
            metrics_data = {
                'Metric': [],
                'Electricity': [],
                'Water': [],
                'Sewage': [],
                'Banking': []
            }
            
            # Add electricity metrics
            metrics_data['Metric'].extend(['Load (MW)', 'Voltage (V)', 'Frequency (Hz)', 'Health Score (%)'])
            metrics_data['Electricity'].extend([
                f"{normal_data['electricity']['load']:.1f}",
                f"{normal_data['electricity']['voltage']:.1f}",
                f"{normal_data['electricity']['frequency']:.2f}",
                f"{normal_data['electricity']['health_score']:.1f}"
            ])
            
            # Add water metrics
            metrics_data['Water'].extend([
                f"{normal_data['water']['flow']:.1f}",
                f"{normal_data['water']['pressure']:.1f}",
                f"{normal_data['water']['quality']:.1f}",
                f"{normal_data['water']['health_score']:.1f}"
            ])
            
            # Add sewage metrics
            metrics_data['Sewage'].extend([
                f"{normal_data['sewage']['flow']:.1f}",
                f"{normal_data['sewage']['treatment_efficiency']:.1f}",
                f"{normal_data['sewage']['contaminant_level']:.1f}",
                f"{normal_data['sewage']['health_score']:.1f}"
            ])
            
            # Add banking metrics
            metrics_data['Banking'].extend([
                f"{normal_data['banking']['transactions']:.0f}",
                f"{normal_data['banking']['response_time']:.2f}",
                f"{normal_data['banking']['success_rate']:.1f}",
                f"{normal_data['banking']['health_score']:.1f}"
            ])
            
            # Create and display dataframe
            normal_df = pd.DataFrame(metrics_data)
            st.dataframe(normal_df, use_container_width=True)
        
        with col2:
            st.subheader("Fault State")
            
            # Get fault scenario
            scenario = fault_data['scenarios'][st.session_state.fault_type]
            fault_data_metrics = scenario['data']
            
            # Create metrics for fault state
            metrics_data = {
                'Metric': [],
                'Electricity': [],
                'Water': [],
                'Sewage': [],
                'Banking': []
            }
            
            # Add electricity metrics
            metrics_data['Metric'].extend(['Load (MW)', 'Voltage (V)', 'Frequency (Hz)', 'Health Score (%)'])
            metrics_data['Electricity'].extend([
                f"{fault_data_metrics['electricity']['load']:.1f}",
                f"{fault_data_metrics['electricity']['voltage']:.1f}",
                f"{fault_data_metrics['electricity']['frequency']:.2f}",
                f"{fault_data_metrics['electricity']['health_score']:.1f}"
            ])
            
            # Add water metrics
            metrics_data['Water'].extend([
                f"{fault_data_metrics['water']['flow']:.1f}",
                f"{fault_data_metrics['water']['pressure']:.1f}",
                f"{fault_data_metrics['water']['quality']:.1f}",
                f"{fault_data_metrics['water']['health_score']:.1f}"
            ])
            
            # Add sewage metrics
            metrics_data['Sewage'].extend([
                f"{fault_data_metrics['sewage']['flow']:.1f}",
                f"{fault_data_metrics['sewage']['treatment_efficiency']:.1f}",
                f"{fault_data_metrics['sewage']['contaminant_level']:.1f}",
                f"{fault_data_metrics['sewage']['health_score']:.1f}"
            ])
            
            # Add banking metrics
            metrics_data['Banking'].extend([
                f"{fault_data_metrics['banking']['transactions']:.0f}",
                f"{fault_data_metrics['banking']['response_time']:.2f}",
                f"{fault_data_metrics['banking']['success_rate']:.1f}",
                f"{fault_data_metrics['banking']['health_score']:.1f}"
            ])
            
            # Create and display dataframe
            fault_df = pd.DataFrame(metrics_data)
            st.dataframe(fault_df, use_container_width=True)
        
        # Add charts comparing normal vs fault metrics for affected systems
        st.subheader("Metric Comparison: Normal vs. Fault State")
        
        # Create bar charts comparing the main metrics for each affected system
        affected_systems = fault_info['systems']
        
        if 'electricity' in affected_systems:
            # Electricity comparison
            electricity_data = {
                'State': ['Normal', 'Fault'],
                'Load (MW)': [normal_data['electricity']['load'], fault_data_metrics['electricity']['load']],
                'Health Score (%)': [normal_data['electricity']['health_score'], fault_data_metrics['electricity']['health_score']]
            }
            
            elec_df = pd.DataFrame(electricity_data)
            elec_df_melted = pd.melt(elec_df, id_vars=['State'], var_name='Metric', value_name='Value')
            
            fig = px.bar(
                elec_df_melted,
                x='Metric',
                y='Value',
                color='State',
                barmode='group',
                title='Electricity System Metrics',
                color_discrete_map={'Normal': 'green', 'Fault': 'red'}
            )
            
            st.plotly_chart(fig, use_container_width=True)
        
        if 'water' in affected_systems:
            # Water comparison
            water_data = {
                'State': ['Normal', 'Fault'],
                'Flow (kL/h)': [normal_data['water']['flow'], fault_data_metrics['water']['flow']],
                'Health Score (%)': [normal_data['water']['health_score'], fault_data_metrics['water']['health_score']]
            }
            
            water_df = pd.DataFrame(water_data)
            water_df_melted = pd.melt(water_df, id_vars=['State'], var_name='Metric', value_name='Value')
            
            fig = px.bar(
                water_df_melted,
                x='Metric',
                y='Value',
                color='State',
                barmode='group',
                title='Water System Metrics',
                color_discrete_map={'Normal': 'green', 'Fault': 'red'}
            )
            
            st.plotly_chart(fig, use_container_width=True)
    
    with tab3:
        st.subheader("Automatic Recovery Process")
        
        # Create a recovery timeline
        current_time = time.time()
        total_duration = st.session_state.simulation_end_time - st.session_state.simulation_start_time
        elapsed_time = current_time - st.session_state.simulation_start_time
        progress_percent = min(1.0, elapsed_time / total_duration)
        
        # Recovery phases
        phases = [
            "Fault Detection",
            "Fault Isolation",
            "System Stabilization",
            "Resource Reallocation",
            "Repair Procedures",
            "System Reintegration",
            "Normal Operation Restored"
        ]
        
        # Define phase thresholds (percentage of total simulation)
        phase_thresholds = [0.05, 0.15, 0.3, 0.5, 0.7, 0.9, 1.0]
        
        # Find current phase
        current_phase = 0
        for i, threshold in enumerate(phase_thresholds):
            if progress_percent <= threshold:
                current_phase = i
                break
        
        # Create phase color list (completed phases are green, current is blue, future are gray)
        phase_colors = []
        for i in range(len(phases)):
            if i < current_phase:
                phase_colors.append("green")
            elif i == current_phase:
                phase_colors.append("blue")
            else:
                phase_colors.append("gray")
        
        # Display recovery phases as a timeline
        st.subheader("Recovery Timeline")
        
        # Create a dataframe for the timeline
        timeline_data = []
        for i, phase in enumerate(phases):
            completed = i < current_phase
            active = i == current_phase
            
            # Calculate phase start and end percentage
            start_percent = 0 if i == 0 else phase_thresholds[i-1]
            end_percent = phase_thresholds[i]
            
            # Calculate phase duration in minutes
            phase_duration = (end_percent - start_percent) * (total_duration / 60)
            
            timeline_data.append({
                'Phase': phase,
                'Status': 'Completed' if completed else ('In Progress' if active else 'Pending'),
                'Duration': f"{phase_duration:.1f} minutes",
                'Progress': '100%' if completed else (f"{min(100, (progress_percent - start_percent) / (end_percent - start_percent) * 100):.0f}%" if active else '0%')
            })
        
        # Create and display dataframe
        timeline_df = pd.DataFrame(timeline_data)
        st.table(timeline_df)
        
        # Show current recovery actions
        st.subheader("Current Recovery Actions")
        
        # Phase-specific actions
        if current_phase == 0:
            st.write("🔍 **Fault Detection Phase**")
            st.write("- Anomaly detection systems have identified potential issues")
            st.write("- AI monitoring system confirming fault parameters")
            st.write("- Quantum-secured alert being distributed to all connected systems")
            st.write("- Preparing isolation boundaries based on fault characteristics")
        
        elif current_phase == 1:
            st.write("🛡️ **Fault Isolation Phase**")
            st.write("- Isolating affected nodes to prevent cascading failures")
            st.write("- Implementing backup protocols for critical services")
            st.write("- Establishing secure communication channels around isolation zone")
            st.write("- Activating redundant systems to maintain essential services")
        
        elif current_phase == 2:
            st.write("⚖️ **System Stabilization Phase**")
            st.write("- Balancing resource allocation across remaining active nodes")
            st.write("- Fine-tuning operational parameters to accommodate fault conditions")
            st.write("- Implementing emergency load shedding procedures where necessary")
            st.write("- Establishing new baseline for system performance during recovery")
        
        elif current_phase == 3:
            st.write("🔄 **Resource Reallocation Phase**")
            st.write("- Redistributing available resources to maintain critical operations")
            st.write("- Prioritizing essential services based on public safety requirements")
            st.write("- Activating mutual aid agreements with neighboring systems")
            st.write("- Implementing optimized operational algorithms for fault conditions")
        
        elif current_phase == 4:
            st.write("🔧 **Repair Procedures Phase**")
            st.write("- Dispatching repair resources to affected components")
            st.write("- Executing automated repair sequences where available")
            st.write("- Testing repaired components in isolated environment")
            st.write("- Preparing for system reintegration once repairs are verified")
        
        elif current_phase == 5:
            st.write("🔌 **System Reintegration Phase**")
            st.write("- Gradually reintegrating repaired components into the network")
            st.write("- Monitoring system response to reintegrated components")
            st.write("- Re-establishing normal communication and control channels")
            st.write("- Conducting real-time security verification of reintegrated components")
        
        elif current_phase == 6:
            st.write("✅ **Normal Operation Restored**")
            st.write("- All systems operating within normal parameters")
            st.write("- Enhanced monitoring active for 72 hours following incident")
            st.write("- Incident data recorded in blockchain ledger for transparency")
            st.write("- AI system updating fault response protocols based on incident analysis")
        
        # Add self-healing visualization
        if st.session_state.enable_healing:
            st.subheader("Self-Healing Visualization")
            
            # Create a gauge showing recovery progress
            fig = go.Figure(go.Indicator(
                mode="gauge+number+delta",
                value=progress_percent * 100,
                domain={'x': [0, 1], 'y': [0, 1]},
                title={'text': "Recovery Progress"},
                delta={'reference': 0, 'increasing': {'color': "green"}},
                gauge={
                    'axis': {'range': [0, 100]},
                    'bar': {'color': "green"},
                    'steps': [
                        {'range': [0, 50], 'color': "lightgray"},
                        {'range': [50, 80], 'color': "gray"},
                        {'range': [80, 100], 'color': "lightgreen"}
                    ],
                    'threshold': {
                        'line': {'color': "red", 'width': 4},
                        'thickness': 0.75,
                        'value': 90
                    }
                }
            ))
            
            st.plotly_chart(fig, use_container_width=True)
            
            # Add estimated time to recovery
            remaining_time = max(0, st.session_state.simulation_end_time - current_time)
            st.info(f"Estimated time to full recovery: {int(remaining_time/60)} minutes, {int(remaining_time%60)} seconds")
        else:
            st.warning("Self-healing capabilities are disabled. Manual intervention required for recovery.")
            st.button("Enable Self-Healing", on_click=lambda: st.session_state.update(enable_healing=True))
        
        # Add incident report
        st.subheader("Preliminary Incident Report")
        
        scenario = fault_data['scenarios'][st.session_state.fault_type]
        
        incident_data = {
            'Parameter': [
                'Incident Type',
                'Severity',
                'Affected Systems',
                'Detection Method',
                'Response Type',
                'Estimated Recovery Time',
                'Incident ID'
            ],
            'Value': [
                scenario['description'],
                scenario.get('severity', 'Medium'),
                ', '.join([s.capitalize() for s in scenario.get('systems', [])]),
                'AI Anomaly Detection',
                'Automated Self-Healing' if st.session_state.enable_healing else 'Manual Intervention Required',
                scenario.get('recovery_time', 'Unknown'),
                f"INC-{int(time.time())}"
            ]
        }
        
        # Create and display incident report
        incident_df = pd.DataFrame(incident_data)
        st.table(incident_df)

# Display information about the fault simulation page when no simulation is running
if 'simulation_running' not in st.session_state:
    st.subheader("About Fault Simulation")
    
    st.markdown("""
    The QEAIMS Fault Simulation module demonstrates the system's ability to detect, isolate, and recover from various fault scenarios across the integrated utility network. This capability is central to the QEAIMS vision of a resilient, self-healing infrastructure.
    
    ### Available Fault Scenarios:
    
    - **Power Outage**: Simulates a major electricity grid failure affecting multiple dependent systems
    - **Water Main Break**: Simulates a critical water distribution system failure
    - **Cyber Attack**: Simulates a coordinated attack on banking networks and systems
    - **Sewage Overflow**: Simulates a sewage system overflow after excessive rainfall
    - **Grid Instability**: Simulates electrical grid fluctuations causing cascading issues
    
    ### Key QEAIMS Self-Healing Capabilities:
    
    1. **Anomaly Detection**: Continuous AI monitoring detects deviations from normal operating parameters
    2. **Fault Isolation**: Automatically isolates affected components to prevent cascading failures
    3. **Resource Reallocation**: Dynamically adjusts resource distribution to maintain critical services
    4. **Repair Coordination**: Initiates and coordinates repair procedures based on fault characteristics
    5. **System Reintegration**: Safely brings repaired components back online with continuous monitoring
    
    ### Simulation Controls:
    
    - Select a fault scenario from the dropdown menu
    - Adjust the simulation duration as needed
    - Toggle the self-healing capability to compare automated vs. manual recovery
    - Click "Run Simulation" to begin the demonstration
    
    The simulation will provide a visual representation of the fault's impact on the network, track system metrics during the fault, and demonstrate the autonomous recovery process enabled by QEAIMS.
    """)
