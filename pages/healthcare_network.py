import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import datetime
from utils.data_generator import get_latest_data, get_historical_data

st.set_page_config(
    page_title="QEAIMS - Healthcare Network",
    page_icon="🏥",
    layout="wide"
)

st.title("Healthcare Network Monitoring")
st.markdown("Track hospital operations, patient visitation, and road network performance for emergency services")

# Generate simulated healthcare data
def generate_healthcare_data(days=7, hospitals=5):
    """Generate simulated healthcare data for demonstration."""
    today = datetime.datetime.now().date()
    dates = [(today - datetime.timedelta(days=i)) for i in range(days)]
    dates.reverse()  # Put in chronological order

    hospital_names = [
        "General Hospital",
        "Memorial Medical Center",
        "University Hospital",
        "Children's Hospital",
        "Community Medical Center"
    ][:hospitals]

    data = []
    for date in dates:
        for hospital in hospital_names:
            # Generate consistent but variable data
            seed_val = int(f"{date.year}{date.month:02d}{date.day:02d}{hospital_names.index(hospital)}")
            np.random.seed(seed_val)
            
            # Base metrics with daily variation
            patient_visits = np.random.randint(100, 300)
            emergency_visits = np.random.randint(30, 80)
            avg_wait_time = np.random.randint(15, 90)
            power_usage = np.random.randint(80, 120)
            water_usage = np.random.randint(70, 130)
            occupancy_rate = np.random.randint(60, 95)
            ambulance_trips = np.random.randint(10, 35)
            
            # Weekend adjustment (fewer scheduled visits, similar emergency visits)
            if date.weekday() >= 5:  # Weekend
                patient_visits = int(patient_visits * 0.7)
            
            # Add to dataset
            data.append({
                "date": date,
                "hospital": hospital,
                "patient_visits": patient_visits,
                "emergency_visits": emergency_visits,
                "avg_wait_time": avg_wait_time,
                "power_usage": power_usage,
                "water_usage": water_usage,
                "occupancy_rate": occupancy_rate,
                "ambulance_trips": ambulance_trips,
                "day_of_week": date.strftime("%A")
            })
    
    return pd.DataFrame(data)

# Generate road network data
def generate_road_network_data(days=7, routes=8):
    """Generate simulated road network data for emergency routes."""
    today = datetime.datetime.now().date()
    dates = [(today - datetime.timedelta(days=i)) for i in range(days)]
    dates.reverse()  # Put in chronological order

    route_names = [
        "Route 1: Hospital to Downtown",
        "Route 2: Hospital to North District",
        "Route 3: Hospital to East District",
        "Route 4: Hospital to South District",
        "Route 5: Hospital to West District",
        "Route 6: Hospital to Industrial Zone",
        "Route 7: Hospital to Suburbs",
        "Route 8: Hospital to Airport"
    ][:routes]

    data = []
    for date in dates:
        for route in route_names:
            # Generate consistent but variable data
            seed_val = int(f"{date.year}{date.month:02d}{date.day:02d}{route_names.index(route)}")
            np.random.seed(seed_val)
            
            # Time (minutes) and traffic metrics
            travel_time = np.random.randint(10, 45)
            traffic_density = np.random.randint(20, 95)
            emergency_response_time = np.random.randint(5, 25)
            incidents = np.random.randint(0, 5)
            road_condition = np.random.randint(70, 100)
            
            # Rush hour adjustment
            if date.weekday() < 5:  # Weekday
                # Add rush hour pattern for weekdays
                travel_time = int(travel_time * 1.3)
                traffic_density = int(min(traffic_density * 1.4, 100))
            
            # Weather effect (random for demonstration)
            weather_impact = np.random.choice([0, 0, 0, 1, 2])  # 0=normal, 1=rain, 2=severe
            if weather_impact == 1:  # Rain
                travel_time = int(travel_time * 1.2)
                road_condition -= np.random.randint(5, 15)
            elif weather_impact == 2:  # Severe weather
                travel_time = int(travel_time * 1.5)
                road_condition -= np.random.randint(15, 30)
                incidents += np.random.randint(1, 3)
            
            # Add to dataset
            data.append({
                "date": date,
                "route": route,
                "travel_time": travel_time,
                "traffic_density": traffic_density,
                "emergency_response_time": emergency_response_time,
                "incidents": incidents,
                "road_condition": road_condition,
                "weather_impact": ["Normal", "Rain", "Severe"][weather_impact],
                "day_of_week": date.strftime("%A")
            })
    
    return pd.DataFrame(data)

# Generate data
healthcare_df = generate_healthcare_data(days=14)
road_network_df = generate_road_network_data(days=14)

# Main layout
tab1, tab2, tab3 = st.tabs(["Hospital Operations", "Patient Visitation", "Emergency Response Network"])

with tab1:
    st.header("Hospital Operations Dashboard")
    
    # Filters
    col1, col2 = st.columns([1, 3])
    
    with col1:
        # Date range selector
        start_date = st.date_input(
            "Start Date",
            healthcare_df["date"].min(),
            min_value=healthcare_df["date"].min(),
            max_value=healthcare_df["date"].max()
        )
        
        end_date = st.date_input(
            "End Date",
            healthcare_df["date"].max(),
            min_value=healthcare_df["date"].min(),
            max_value=healthcare_df["date"].max()
        )
        
        # Hospital selector
        selected_hospitals = st.multiselect(
            "Select Hospitals",
            options=healthcare_df["hospital"].unique(),
            default=healthcare_df["hospital"].unique()[:3]  # Default select first 3
        )
        
        # Utility status
        st.subheader("Utility Status")
        
        # Get latest data from main QEAIMS
        latest_data = get_latest_data()
        
        # Display utility metrics
        power_status = "✅ Normal" if latest_data["electricity"]["health_score"] >= 90 else "⚠️ Warning" if latest_data["electricity"]["health_score"] >= 70 else "🔴 Critical"
        water_status = "✅ Normal" if latest_data["water"]["health_score"] >= 90 else "⚠️ Warning" if latest_data["water"]["health_score"] >= 70 else "🔴 Critical"
        
        st.metric("Power Supply", power_status)
        st.metric("Water Supply", water_status)
        
        # Backup system status
        backup_power = np.random.randint(92, 101)
        st.metric("Backup Power Capacity", f"{backup_power}%")
        
        st.markdown("---")
        st.caption("Data updates every 15 minutes")
    
    with col2:
        # Filter data based on selections
        filtered_data = healthcare_df[
            (healthcare_df["date"] >= start_date) &
            (healthcare_df["date"] <= end_date) &
            (healthcare_df["hospital"].isin(selected_hospitals))
        ]
        
        # Hospital occupancy chart
        st.subheader("Hospital Occupancy Rates")
        occupancy_pivot = filtered_data.pivot(index="date", columns="hospital", values="occupancy_rate")
        
        fig_occupancy = px.line(
            occupancy_pivot, 
            labels={"value": "Occupancy Rate (%)", "date": "Date"},
            title="Daily Hospital Occupancy Rates"
        )
        fig_occupancy.update_layout(legend_title="Hospital")
        st.plotly_chart(fig_occupancy, use_container_width=True)
        
        # Utility usage charts
        col_a, col_b = st.columns(2)
        
        with col_a:
            # Power usage chart
            power_pivot = filtered_data.pivot(index="date", columns="hospital", values="power_usage")
            fig_power = px.line(
                power_pivot,
                labels={"value": "Power Usage (kW)", "date": "Date"},
                title="Daily Power Consumption"
            )
            fig_power.update_layout(legend_title="Hospital")
            st.plotly_chart(fig_power, use_container_width=True)
        
        with col_b:
            # Water usage chart
            water_pivot = filtered_data.pivot(index="date", columns="hospital", values="water_usage")
            fig_water = px.line(
                water_pivot,
                labels={"value": "Water Usage (kL)", "date": "Date"},
                title="Daily Water Consumption"
            )
            fig_water.update_layout(legend_title="Hospital")
            st.plotly_chart(fig_water, use_container_width=True)
        
        # Hospital stats comparison
        st.subheader("Hospital Performance Metrics")
        
        # Get the most recent date's data for each hospital
        latest_date = filtered_data["date"].max()
        latest_stats = filtered_data[filtered_data["date"] == latest_date]
        
        metrics_table = latest_stats[["hospital", "occupancy_rate", "avg_wait_time", "power_usage", "water_usage"]]
        metrics_table.columns = ["Hospital", "Occupancy Rate (%)", "Avg Wait Time (min)", "Power Usage (kW)", "Water Usage (kL)"]
        
        st.dataframe(metrics_table, use_container_width=True)
        
        # Show critical metrics
        critical_occupancy = latest_stats[latest_stats["occupancy_rate"] > 90]
        if not critical_occupancy.empty:
            st.warning(f"⚠️ {len(critical_occupancy)} hospitals have occupancy rates above 90%")
            
        long_wait = latest_stats[latest_stats["avg_wait_time"] > 60]
        if not long_wait.empty:
            st.warning(f"⚠️ {len(long_wait)} hospitals have average wait times above 60 minutes")

with tab2:
    st.header("Patient Visitation Analysis")
    
    # Filters
    col1, col2 = st.columns([1, 3])
    
    with col1:
        # Date range selector (use the same as before for consistency)
        visit_start_date = st.date_input(
            "Start Date",
            healthcare_df["date"].min(),
            min_value=healthcare_df["date"].min(),
            max_value=healthcare_df["date"].max(),
            key="visit_start_date"
        )
        
        visit_end_date = st.date_input(
            "End Date",
            healthcare_df["date"].max(),
            min_value=healthcare_df["date"].min(),
            max_value=healthcare_df["date"].max(),
            key="visit_end_date"
        )
        
        # Hospital selector
        visit_hospitals = st.multiselect(
            "Select Hospitals",
            options=healthcare_df["hospital"].unique(),
            default=healthcare_df["hospital"].unique(),  # Default select all
            key="visit_hospitals"
        )
        
        # Aggregation options
        agg_option = st.radio(
            "View By",
            options=["Day", "Hospital", "Day of Week"]
        )
        
        # Visit type filter
        visit_type = st.radio(
            "Visit Type",
            options=["All Visits", "Regular Visits", "Emergency Visits"]
        )
    
    with col2:
        # Filter data based on selections
        visit_data = healthcare_df[
            (healthcare_df["date"] >= visit_start_date) &
            (healthcare_df["date"] <= visit_end_date) &
            (healthcare_df["hospital"].isin(visit_hospitals))
        ]
        
        # Process based on visit type selection
        if visit_type == "Regular Visits":
            visit_metric = "patient_visits"
            visit_title = "Regular Patient Visits"
        elif visit_type == "Emergency Visits":
            visit_metric = "emergency_visits"
            visit_title = "Emergency Department Visits"
        else:
            # Create combined metric
            visit_data["total_visits"] = visit_data["patient_visits"] + visit_data["emergency_visits"]
            visit_metric = "total_visits"
            visit_title = "Total Patient Visits"
        
        # Create visualizations based on aggregation choice
        if agg_option == "Day":
            # Daily visits across all selected hospitals
            daily_visits = visit_data.groupby("date")[visit_metric].sum().reset_index()
            
            fig = px.line(
                daily_visits,
                x="date",
                y=visit_metric,
                title=f"Daily {visit_title}",
                labels={visit_metric: "Number of Visits", "date": "Date"}
            )
            st.plotly_chart(fig, use_container_width=True)
            
            # Show 7-day trend
            if len(daily_visits) >= 7:
                last_7_days = daily_visits.tail(7)
                pct_change = ((last_7_days[visit_metric].iloc[-1] - last_7_days[visit_metric].iloc[0]) / 
                            last_7_days[visit_metric].iloc[0] * 100)
                
                trend_icon = "📈" if pct_change > 0 else "📉"
                st.metric(
                    "7-Day Trend", 
                    f"{trend_icon} {abs(pct_change):.1f}% {'increase' if pct_change > 0 else 'decrease'}"
                )
        
        elif agg_option == "Hospital":
            # Visits by hospital
            hospital_visits = visit_data.groupby("hospital")[visit_metric].sum().reset_index()
            
            fig = px.bar(
                hospital_visits,
                x="hospital",
                y=visit_metric,
                title=f"{visit_title} by Hospital",
                labels={visit_metric: "Number of Visits", "hospital": "Hospital"},
                color="hospital"
            )
            st.plotly_chart(fig, use_container_width=True)
            
            # Hospital with most visits
            top_hospital = hospital_visits.loc[hospital_visits[visit_metric].idxmax()]
            st.metric(
                "Highest Volume Hospital", 
                top_hospital["hospital"],
                f"{top_hospital[visit_metric]} visits"
            )
        
        else:  # Day of Week
            # Visits by day of week
            weekday_visits = visit_data.groupby("day_of_week")[visit_metric].mean().reset_index()
            
            # Sort by days of week
            days_order = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
            weekday_visits["day_of_week"] = pd.Categorical(
                weekday_visits["day_of_week"], 
                categories=days_order, 
                ordered=True
            )
            weekday_visits = weekday_visits.sort_values("day_of_week")
            
            fig = px.bar(
                weekday_visits,
                x="day_of_week",
                y=visit_metric,
                title=f"Average {visit_title} by Day of Week",
                labels={visit_metric: "Average Visits", "day_of_week": "Day of Week"},
                color="day_of_week"
            )
            st.plotly_chart(fig, use_container_width=True)
            
            # Busiest day of week
            busiest_day = weekday_visits.loc[weekday_visits[visit_metric].idxmax()]
            st.metric(
                "Busiest Day of Week", 
                busiest_day["day_of_week"],
                f"{busiest_day[visit_metric]:.1f} avg visits"
            )
        
        # Additional Metrics
        st.subheader("Patient Metrics")
        
        col_a, col_b, col_c = st.columns(3)
        
        with col_a:
            total_patients = visit_data[visit_metric].sum()
            st.metric("Total Patients", f"{total_patients:,}")
        
        with col_b:
            avg_daily = visit_data.groupby("date")[visit_metric].sum().mean()
            st.metric("Average Daily Visits", f"{avg_daily:.1f}")
        
        with col_c:
            emergency_ratio = (visit_data["emergency_visits"].sum() / 
                              (visit_data["patient_visits"].sum() + visit_data["emergency_visits"].sum()) * 100)
            st.metric("Emergency Visit Ratio", f"{emergency_ratio:.1f}%")
        
        # Wait Time Analysis
        st.subheader("Wait Time Analysis")
        
        # Average wait time by hospital
        wait_time_data = visit_data.groupby("hospital")["avg_wait_time"].mean().reset_index()
        wait_time_data = wait_time_data.sort_values("avg_wait_time", ascending=False)
        
        fig = px.bar(
            wait_time_data,
            x="hospital",
            y="avg_wait_time",
            title="Average Wait Time by Hospital",
            labels={"avg_wait_time": "Average Wait Time (min)", "hospital": "Hospital"},
            color="avg_wait_time",
            color_continuous_scale="RdYlGn_r"  # Red for high wait times (reversed green-yellow-red)
        )
        st.plotly_chart(fig, use_container_width=True)

with tab3:
    st.header("Emergency Response Network")
    
    # Filters
    col1, col2 = st.columns([1, 3])
    
    with col1:
        # Date range selector
        road_start_date = st.date_input(
            "Start Date",
            road_network_df["date"].min(),
            min_value=road_network_df["date"].min(),
            max_value=road_network_df["date"].max(),
            key="road_start_date"
        )
        
        road_end_date = st.date_input(
            "End Date",
            road_network_df["date"].max(),
            min_value=road_network_df["date"].min(),
            max_value=road_network_df["date"].max(),
            key="road_end_date"
        )
        
        # Route selector
        selected_routes = st.multiselect(
            "Select Routes",
            options=road_network_df["route"].unique(),
            default=road_network_df["route"].unique()  # Default select all
        )
        
        # Emergency response simulator
        st.subheader("Response Time Simulator")
        
        selected_route = st.selectbox(
            "Select Emergency Route",
            options=road_network_df["route"].unique()
        )
        
        # Time of day selector for simulation
        time_of_day = st.select_slider(
            "Time of Day",
            options=["Early Morning (2-5am)", "Morning (6-9am)", "Midday (10am-2pm)", 
                    "Afternoon (3-6pm)", "Evening (7-10pm)", "Night (11pm-1am)"]
        )
        
        # Weather condition for simulation
        weather = st.select_slider(
            "Weather Conditions",
            options=["Clear", "Light Rain", "Heavy Rain", "Snow", "Severe Storm"]
        )
        
        # Run simulation button
        simulate_button = st.button("Run Response Simulation")
        
        if simulate_button:
            # Basic simulation logic
            base_time = np.random.randint(8, 15)  # Base minutes
            
            # Time of day factor
            tod_factors = {
                "Early Morning (2-5am)": 0.8,
                "Morning (6-9am)": 1.5,
                "Midday (10am-2pm)": 1.2,
                "Afternoon (3-6pm)": 1.6,
                "Evening (7-10pm)": 1.1,
                "Night (11pm-1am)": 0.9
            }
            
            # Weather factor
            weather_factors = {
                "Clear": 1.0,
                "Light Rain": 1.2,
                "Heavy Rain": 1.5,
                "Snow": 1.7,
                "Severe Storm": 2.0
            }
            
            # Calculate simulated time
            sim_time = base_time * tod_factors[time_of_day] * weather_factors[weather]
            sim_time = round(sim_time, 1)
            
            # Determine if it meets the target response time (12 minutes)
            if sim_time <= 12:
                st.success(f"🚑 Estimated Response Time: {sim_time} minutes (Within target)")
            else:
                st.error(f"🚑 Estimated Response Time: {sim_time} minutes (Exceeds target)")
                
                # Suggest alternatives if available
                if len(selected_routes) > 1:
                    alt_route = np.random.choice([r for r in selected_routes if r != selected_route])
                    alt_time = round(sim_time * np.random.uniform(0.6, 0.9), 1)
                    st.info(f"🔄 Suggested Alternative: {alt_route} ({alt_time} minutes)")
    
    with col2:
        # Filter data based on selections
        road_data = road_network_df[
            (road_network_df["date"] >= road_start_date) &
            (road_network_df["date"] <= road_end_date) &
            (road_network_df["route"].isin(selected_routes))
        ]
        
        # Emergency response time chart
        st.subheader("Emergency Response Times")
        response_pivot = road_data.pivot(index="date", columns="route", values="emergency_response_time")
        
        fig_response = px.line(
            response_pivot, 
            labels={"value": "Response Time (minutes)", "date": "Date"},
            title="Daily Emergency Response Times by Route"
        )
        fig_response.update_layout(legend_title="Route")
        
        # Add target response time line
        fig_response.add_shape(
            type="line",
            x0=response_pivot.index.min(),
            y0=12,
            x1=response_pivot.index.max(),
            y1=12,
            line=dict(color="red", width=2, dash="dash"),
        )
        
        fig_response.add_annotation(
            x=response_pivot.index[len(response_pivot.index)//2],
            y=12.5,
            text="Target Response Time (12 min)",
            showarrow=False,
            font=dict(color="red")
        )
        
        st.plotly_chart(fig_response, use_container_width=True)
        
        # Road conditions and incidents
        col_a, col_b = st.columns(2)
        
        with col_a:
            # Road condition chart
            condition_pivot = road_data.pivot(index="date", columns="route", values="road_condition")
            
            fig_condition = px.line(
                condition_pivot,
                labels={"value": "Road Condition Score", "date": "Date"},
                title="Road Condition Scores"
            )
            fig_condition.update_layout(legend_title="Route")
            st.plotly_chart(fig_condition, use_container_width=True)
        
        with col_b:
            # Incidents by route
            incidents_by_route = road_data.groupby("route")["incidents"].sum().reset_index()
            incidents_by_route = incidents_by_route.sort_values("incidents", ascending=False)
            
            fig_incidents = px.bar(
                incidents_by_route,
                x="route",
                y="incidents",
                title="Total Incidents by Route",
                labels={"incidents": "Number of Incidents", "route": "Route"},
                color="incidents",
                color_continuous_scale="Reds"
            )
            st.plotly_chart(fig_incidents, use_container_width=True)
        
        # Weather impact analysis
        st.subheader("Weather Impact Analysis")
        
        # Group by weather and calculate average response time
        weather_impact = road_data.groupby("weather_impact")["emergency_response_time"].mean().reset_index()
        
        fig_weather = px.bar(
            weather_impact,
            x="weather_impact",
            y="emergency_response_time",
            title="Average Response Time by Weather Condition",
            labels={"emergency_response_time": "Response Time (minutes)", "weather_impact": "Weather Condition"},
            color="emergency_response_time",
            color_continuous_scale="RdYlGn_r"  # Red for high response times
        )
        st.plotly_chart(fig_weather, use_container_width=True)
        
        # Response time statistics table
        st.subheader("Route Statistics")
        
        # Create summary table
        route_stats = road_data.groupby("route").agg({
            "travel_time": "mean",
            "emergency_response_time": "mean",
            "traffic_density": "mean",
            "incidents": "sum",
            "road_condition": "mean"
        }).reset_index()
        
        # Rename columns for display
        route_stats.columns = [
            "Route", "Avg Travel Time (min)", "Avg Response Time (min)", 
            "Avg Traffic Density (%)", "Total Incidents", "Avg Road Condition"
        ]
        
        # Format floats
        for col in route_stats.columns[1:]:
            if route_stats[col].dtype in [np.float64, np.float32]:
                route_stats[col] = route_stats[col].round(1)
        
        # Color code based on response time
        def color_response_time(val):
            if val <= 12:
                return 'background-color: #c6efce'  # Green
            elif val <= 15:
                return 'background-color: #ffeb9c'  # Yellow
            else:
                return 'background-color: #ffc7ce'  # Red
        
        # Apply styling and display
        styled_stats = route_stats.style.applymap(
            color_response_time, 
            subset=["Avg Response Time (min)"]
        )
        
        st.dataframe(styled_stats, use_container_width=True)

# Update the network graph model to include healthcare facilities
with st.expander("Integration with QEAIMS Network"):
    st.markdown("""
    The healthcare monitoring system is fully integrated with the QEAIMS infrastructure monitoring:
    
    - **Electricity**: Hospital power consumption and backup generator status
    - **Water**: Hospital water usage and quality monitoring
    - **Transportation**: Emergency response routes and traffic conditions
    - **Communications**: Patient alert systems and emergency dispatch
    
    When a fault is detected in any utility system, the impact on healthcare facilities is
    automatically assessed and prioritized in the recovery process.
    """)
    
    # Show simulated integration metrics
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric(
            "Hospitals with Backup Power",
            "5/5",
            "100%"
        )
    
    with col2:
        st.metric(
            "Average Emergency Route Score",
            "83/100",
            "+2 from last week"
        )
    
    with col3:
        st.metric(
            "Critical Infrastructure Resilience",
            "94%",
            "+3% from baseline"
        )