import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from utils.data_generator import get_latest_data, get_fault_simulation_data
from utils.network_graph import simulate_fault

st.set_page_config(
    page_title="QEAIMS - Geographic View",
    page_icon="🗺️",
    layout="wide"
)

st.title("Geographic Infrastructure Visualization")
st.markdown("Interactive map-based view of the integrated utility infrastructure and affected areas during fault scenarios")

# Define map layout parameters
map_center = {"lat": 40.7128, "lon": -74.0060}  # NYC coordinates as an example
default_zoom = 11

# Define infrastructure locations (for demo purposes)
infrastructure = {
    "electricity": [
        {"name": "Main Power Plant", "lat": 40.7433, "lon": -73.9485, "type": "generation", "capacity": 1200},
        {"name": "Substation Alpha", "lat": 40.7180, "lon": -74.0011, "type": "distribution", "capacity": 450},
        {"name": "Substation Beta", "lat": 40.6892, "lon": -73.9783, "type": "distribution", "capacity": 350},
        {"name": "Solar Array", "lat": 40.7500, "lon": -73.9700, "type": "generation", "capacity": 200}
    ],
    "water": [
        {"name": "Main Reservoir", "lat": 40.7822, "lon": -73.9700, "type": "storage", "capacity": 2000},
        {"name": "Treatment Plant Alpha", "lat": 40.7600, "lon": -73.9900, "type": "treatment", "capacity": 900},
        {"name": "Pumping Station 1", "lat": 40.7300, "lon": -74.0150, "type": "distribution", "capacity": 500},
        {"name": "Pumping Station 2", "lat": 40.6950, "lon": -73.9900, "type": "distribution", "capacity": 450}
    ],
    "sewage": [
        {"name": "Main Treatment Plant", "lat": 40.7100, "lon": -74.0200, "type": "treatment", "capacity": 1200},
        {"name": "Pumping Station A", "lat": 40.7400, "lon": -74.0000, "type": "collection", "capacity": 600},
        {"name": "Pumping Station B", "lat": 40.6800, "lon": -73.9800, "type": "collection", "capacity": 550},
        {"name": "Overflow Facility", "lat": 40.7000, "lon": -73.9600, "type": "emergency", "capacity": 300}
    ],
    "banking": [
        {"name": "Main Data Center", "lat": 40.7500, "lon": -74.0050, "type": "processing", "capacity": 5000},
        {"name": "Backup Data Center", "lat": 40.7200, "lon": -74.0200, "type": "backup", "capacity": 4000},
        {"name": "Network Hub Alpha", "lat": 40.7350, "lon": -73.9900, "type": "network", "capacity": 3000},
        {"name": "Network Hub Beta", "lat": 40.6950, "lon": -73.9950, "type": "network", "capacity": 2500}
    ]
}

# Create dataframe for all infrastructure
all_infrastructure = []
for system, locations in infrastructure.items():
    for location in locations:
        location_data = location.copy()
        location_data["system"] = system
        all_infrastructure.append(location_data)

infrastructure_df = pd.DataFrame(all_infrastructure)

# Create sidebar controls
st.sidebar.header("Map Controls")

# System selection
systems_to_show = st.sidebar.multiselect(
    "Systems to display:",
    ["electricity", "water", "sewage", "banking"],
    default=["electricity", "water", "sewage", "banking"],
    format_func=lambda x: x.capitalize()
)

# Fault simulation
st.sidebar.subheader("Fault Simulation")
show_fault = st.sidebar.checkbox("Show Fault Impact", value=False)

if show_fault:
    fault_type = st.sidebar.selectbox(
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
    
    # Get fault simulation data
    fault_data = get_fault_simulation_data()
    fault_info = simulate_fault(fault_type)
    
    # Mark affected areas based on fault type
    if fault_type in fault_data["scenarios"]:
        st.sidebar.markdown(f"**Description:** {fault_data['scenarios'][fault_type]['description']}")
        st.sidebar.markdown(f"**Severity:** {fault_info['severity']}")
        st.sidebar.markdown(f"**Affected Systems:** {', '.join([s.capitalize() for s in fault_info['systems']])}")
        
# Filter infrastructure based on selection
filtered_infrastructure = infrastructure_df[infrastructure_df["system"].isin(systems_to_show)]

# Create the map
st.subheader("Infrastructure Map")

# Create dataframe for connections between infrastructure
connections = []
for system in systems_to_show:
    system_locations = [loc for loc in infrastructure[system]]
    for i in range(len(system_locations) - 1):
        for j in range(i + 1, len(system_locations)):
            # Only create connections within the same system
            connection = {
                "from_lat": system_locations[i]["lat"],
                "from_lon": system_locations[i]["lon"],
                "to_lat": system_locations[j]["lat"],
                "to_lon": system_locations[j]["lon"],
                "system": system
            }
            connections.append(connection)

connections_df = pd.DataFrame(connections)

# Create the base map
fig = go.Figure()

# Add infrastructure points
for system in systems_to_show:
    system_data = filtered_infrastructure[filtered_infrastructure["system"] == system]
    
    # Define color scheme for each system
    color_map = {
        "electricity": "yellow",
        "water": "blue",
        "sewage": "green",
        "banking": "purple"
    }
    
    # Get the base color for the system
    base_color = color_map.get(system, "gray")
    
    # Check if we're showing a fault and if this system is affected
    point_color = base_color
    if show_fault and system in fault_info["systems"]:
        hover_template = (
            "<b>%{customdata[0]}</b><br>" +
            "Type: %{customdata[1]}<br>" +
            "Capacity: %{customdata[2]}<br>" +
            "System: %{customdata[3]}<br>" +
            "<b>Status: Affected by Fault</b>"
        )
    else:
        hover_template = (
            "<b>%{customdata[0]}</b><br>" +
            "Type: %{customdata[1]}<br>" +
            "Capacity: %{customdata[2]}<br>" +
            "System: %{customdata[3]}<br>" +
            "Status: Normal"
        )
    
    # Add the scatter points for this system
    fig.add_trace(go.Scattermapbox(
        lat=system_data["lat"],
        lon=system_data["lon"],
        mode="markers",
        marker=dict(
            size=10, 
            color=base_color if not show_fault else 
                  "red" if system in fault_info["systems"] else base_color
        ),
        name=system.capitalize(),
        customdata=np.stack((
            system_data["name"], 
            system_data["type"], 
            system_data["capacity"],
            system_data["system"]
        ), axis=-1),
        hovertemplate=hover_template
    ))
    
    # Add connections between infrastructure of the same system
    system_connections = connections_df[connections_df["system"] == system]
    for idx, connection in system_connections.iterrows():
        fig.add_trace(go.Scattermapbox(
            lat=[connection["from_lat"], connection["to_lat"]],
            lon=[connection["from_lon"], connection["to_lon"]],
            mode="lines",
            line=dict(
                width=2, 
                color="red" if show_fault and system in fault_info["systems"] else base_color
            ),
            opacity=0.7,
            showlegend=False
        ))

# If showing a fault, add affected area circles
if show_fault:
    # Determine epicenter of the fault based on fault type
    if fault_type == "power_outage":
        epicenter = {"lat": infrastructure["electricity"][0]["lat"], "lon": infrastructure["electricity"][0]["lon"]}
        radius = 0.03  # Approx size of affected area
    elif fault_type == "water_main_break":
        epicenter = {"lat": infrastructure["water"][2]["lat"], "lon": infrastructure["water"][2]["lon"]}
        radius = 0.015
    elif fault_type == "cyber_attack":
        epicenter = {"lat": infrastructure["banking"][0]["lat"], "lon": infrastructure["banking"][0]["lon"]}
        radius = 0.01
    elif fault_type == "sewage_overflow":
        epicenter = {"lat": infrastructure["sewage"][0]["lat"], "lon": infrastructure["sewage"][0]["lon"]}
        radius = 0.02
    else:  # grid_instability
        epicenter = {"lat": infrastructure["electricity"][1]["lat"], "lon": infrastructure["electricity"][1]["lon"]}
        radius = 0.025
    
    # Create a circle to represent the affected area
    circle_points = []
    steps = 36  # Number of points to create the circle
    for i in range(steps + 1):
        angle = (i / steps) * 2 * np.pi
        lat = epicenter["lat"] + radius * np.cos(angle)
        lon = epicenter["lon"] + radius * np.sin(angle)
        circle_points.append((lat, lon))
    
    circle_lats, circle_lons = zip(*circle_points)
    
    fig.add_trace(go.Scattermapbox(
        lat=list(circle_lats),
        lon=list(circle_lons),
        mode="lines",
        line=dict(width=2, color="red"),
        fill="toself",
        fillcolor="rgba(255, 0, 0, 0.3)",
        name=f"Affected Area: {fault_type.replace('_', ' ').title()}",
        hoverinfo="name"
    ))

# Configure map layout
fig.update_layout(
    mapbox=dict(
        style="open-street-map",
        center=map_center,
        zoom=default_zoom
    ),
    margin={"r": 0, "t": 0, "l": 0, "b": 0},
    legend=dict(
        yanchor="top",
        y=0.99,
        xanchor="left",
        x=0.01,
        bgcolor="rgba(255, 255, 255, 0.8)"
    ),
    height=600
)

# Display the map
st.plotly_chart(fig, use_container_width=True)

# Additional information panels
col1, col2 = st.columns(2)

with col1:
    st.subheader("Infrastructure Statistics")
    
    # Get latest data
    latest_data = get_latest_data()
    
    # Display statistics for each system
    for system in systems_to_show:
        with st.expander(f"{system.capitalize()} Infrastructure"):
            # Create a summary dataframe
            system_summary = filtered_infrastructure[filtered_infrastructure["system"] == system]
            
            # Add health status from latest data
            if system == "electricity":
                health = latest_data["electricity"]["health_score"]
            elif system == "water":
                health = latest_data["water"]["health_score"]
            elif system == "sewage":
                health = latest_data["sewage"]["health_score"]
            elif system == "banking":
                health = latest_data["banking"]["health_score"]
            else:
                health = 90  # Default
            
            st.metric(
                f"{system.capitalize()} System Health", 
                f"{health:.1f}%",
                delta="-15%" if show_fault and system in fault_info["systems"] else "0%"
            )
            
            # Show infrastructure details
            st.dataframe(
                system_summary[["name", "type", "capacity"]].rename(
                    columns={"name": "Name", "type": "Type", "capacity": "Capacity"}
                )
            )

with col2:
    st.subheader("Critical Areas")
    
    if show_fault:
        st.error(f"**ALERT:** {fault_data['scenarios'][fault_type]['description']}")
        
        # Create a dataframe of affected locations
        affected_systems = fault_info["systems"]
        affected_locations = filtered_infrastructure[filtered_infrastructure["system"].isin(affected_systems)]
        
        st.markdown("### Affected Infrastructure")
        st.dataframe(
            affected_locations[["name", "system", "type"]].rename(
                columns={"name": "Name", "system": "System", "type": "Type"}
            ).assign(Status="Affected")
        )
        
        st.markdown("### Recovery Recommendations")
        recommendations = {
            "power_outage": [
                "Activate backup generators at critical water and sewage facilities",
                "Implement load shedding to preserve essential services",
                "Prioritize restoration of power to healthcare and emergency services",
                "Deploy mobile power units to key banking data centers"
            ],
            "water_main_break": [
                "Isolate the affected water main segment",
                "Reroute water flow through alternate pipelines",
                "Reduce pressure in the system to minimize leakage",
                "Issue water conservation advisory for affected areas"
            ],
            "cyber_attack": [
                "Activate air-gapped backup systems",
                "Implement emergency security protocols",
                "Isolate affected network segments",
                "Deploy manual transaction processing procedures"
            ],
            "sewage_overflow": [
                "Engage emergency pumping stations",
                "Divert flow to secondary treatment facilities",
                "Deploy containment systems at overflow points",
                "Issue public health advisory for affected waterways"
            ],
            "grid_instability": [
                "Engage stabilization systems on key transmission lines",
                "Reduce load on affected substations",
                "Implement islanding protocols for critical infrastructure",
                "Activate microgrids for essential services"
            ]
        }
        
        for i, rec in enumerate(recommendations.get(fault_type, [])):
            st.markdown(f"{i+1}. {rec}")
    else:
        st.info("Enable 'Show Fault Impact' in the sidebar to visualize critical areas during a fault scenario.")
        
        # Display normal state information
        st.markdown("### Infrastructure Overview")
        
        # Count infrastructure by system
        system_counts = filtered_infrastructure.groupby("system").size().reset_index(name="count")
        
        # Display as a bar chart
        fig = px.bar(
            system_counts, 
            x="system", 
            y="count", 
            color="system",
            labels={"system": "System", "count": "Number of Facilities"},
            title="Infrastructure Distribution by System"
        )
        st.plotly_chart(fig, use_container_width=True)