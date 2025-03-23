import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import time
import datetime
from utils.data_generator import get_latest_data, get_fault_simulation_data
from utils.anomaly_detection import analyze_system_health

st.set_page_config(
    page_title="QEAIMS - Stakeholder Communication",
    page_icon="📢",
    layout="wide"
)

st.title("Stakeholder Communication Module")
st.markdown("Generate tailored reports and alerts for different stakeholder groups during system events")

# Get data
latest_data = get_latest_data()
fault_data = get_fault_simulation_data()

# Create main layout
col1, col2 = st.columns([1, 2])

with col1:
    st.subheader("Communication Settings")
    
    # Incident selection
    incident_type = st.selectbox(
        "Select Incident Scenario:",
        [
            "current_status",
            "power_outage",
            "water_main_break",
            "cyber_attack",
            "sewage_overflow",
            "grid_instability"
        ],
        format_func=lambda x: "Current System Status" if x == "current_status" else x.replace('_', ' ').title()
    )
    
    # Stakeholder group selection
    stakeholder_group = st.selectbox(
        "Select Stakeholder Group:",
        [
            "technical_team",
            "executive_management",
            "regulatory_bodies",
            "public_relations",
            "general_public"
        ],
        format_func=lambda x: x.replace('_', ' ').title()
    )
    
    # Communication urgency
    if incident_type != "current_status":
        urgency_level = st.select_slider(
            "Urgency Level:",
            options=["Low", "Medium", "High", "Critical"],
            value="Medium"
        )
    else:
        urgency_level = "Low"
    
    # Communication channels
    st.subheader("Distribution Channels")
    
    channels = {
        "email": st.checkbox("Email", value=True),
        "sms": st.checkbox("SMS/Text Messages", value=stakeholder_group in ["technical_team", "executive_management"]),
        "dashboard": st.checkbox("Dashboard Alert", value=True),
        "api": st.checkbox("API Integration", value=stakeholder_group == "technical_team"),
        "social_media": st.checkbox("Social Media", value=stakeholder_group in ["public_relations", "general_public"]),
        "emergency_system": st.checkbox("Emergency Notification System", value=urgency_level in ["High", "Critical"])
    }
    
    # Generate report button
    generate_report = st.button("Generate Communication")

# Main content area
with col2:
    if generate_report:
        # Display report generation progress
        with st.spinner("Generating stakeholder communication..."):
            # Simulate report generation delay
            time.sleep(1)
            
            # Get incident data
            if incident_type == "current_status":
                incident_data = {
                    "title": "Current System Status Report",
                    "timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "systems": {
                        "electricity": analyze_system_health(pd.DataFrame(), "electricity"),
                        "water": analyze_system_health(pd.DataFrame(), "water"),
                        "sewage": analyze_system_health(pd.DataFrame(), "sewage"),
                        "banking": analyze_system_health(pd.DataFrame(), "banking")
                    },
                    "description": "Regular status update on all integrated utility systems",
                    "severity": "Informational"
                }
            else:
                scenario = fault_data['scenarios'][incident_type]
                incident_data = {
                    "title": f"Incident Report: {incident_type.replace('_', ' ').title()}",
                    "timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "systems": {
                        system: {"status": "Critical" if system in scenario["affected_systems"] else "Healthy"}
                        for system in ["electricity", "water", "sewage", "banking"]
                    },
                    "description": scenario["description"],
                    "severity": urgency_level,
                    "estimated_recovery": scenario["recovery_time"]
                }
            
            # Display generated communication
            st.subheader("Generated Communication")
            
            # Create the appropriate communication template based on stakeholder group
            if stakeholder_group == "technical_team":
                generate_technical_report(incident_data, channels)
            elif stakeholder_group == "executive_management":
                generate_executive_report(incident_data, channels)
            elif stakeholder_group == "regulatory_bodies":
                generate_regulatory_report(incident_data, channels)
            elif stakeholder_group == "public_relations":
                generate_pr_report(incident_data, channels)
            elif stakeholder_group == "general_public":
                generate_public_report(incident_data, channels)
            
            # Display channel distribution summary
            st.subheader("Distribution Summary")
            
            # Check which channels are selected
            active_channels = [name.replace('_', ' ').title() for name, active in channels.items() if active]
            
            if active_channels:
                # Create dataframe for channel distribution
                distribution_data = {
                    "Channel": active_channels,
                    "Recipients": [
                        "On-call engineers, System administrators, IT security team" if c == "Email" and stakeholder_group == "technical_team"
                        else "CTO, CIO, Operations Director" if c == "Email" and stakeholder_group == "executive_management"
                        else "Regulatory compliance team, Government liaisons" if c == "Email" and stakeholder_group == "regulatory_bodies"
                        else "PR team, Media relations" if c == "Email" and stakeholder_group == "public_relations"
                        else "Subscribed users" if c == "Email" and stakeholder_group == "general_public"
                        else "On-call personnel" if c == "Sms/Text Messages"
                        else "All authenticated users" if c == "Dashboard Alert"
                        else "Connected systems" if c == "Api Integration"
                        else "Twitter, Facebook, Instagram followers" if c == "Social Media"
                        else "All registered users in affected areas" if c == "Emergency Notification System"
                        else "Unknown"
                        for c in active_channels
                    ],
                    "Status": ["Queued for immediate delivery"] * len(active_channels)
                }
                
                # Display as table
                st.dataframe(pd.DataFrame(distribution_data))
                
                # Display mock preview based on most important channel
                if "Emergency Notification System" in active_channels:
                    preview_channel = "Emergency Notification System"
                elif "Sms/Text Messages" in active_channels:
                    preview_channel = "SMS/Text Message"
                elif "Email" in active_channels:
                    preview_channel = "Email"
                else:
                    preview_channel = active_channels[0]
                
                st.subheader(f"{preview_channel} Preview")
                
                if preview_channel == "Email":
                    display_email_preview(incident_data, stakeholder_group)
                elif preview_channel == "SMS/Text Message":
                    display_sms_preview(incident_data, stakeholder_group)
                elif preview_channel == "Emergency Notification System":
                    display_emergency_preview(incident_data)
            else:
                st.warning("No distribution channels selected. Please select at least one channel.")
            
            # Display notification of completed report
            st.success("Communication generated and ready for distribution!")
            
            # Add send button (non-functional in demo)
            if st.button("Send Communication"):
                st.success(f"Communication sent via {len(active_channels)} channels!")
    else:
        # Display instructions
        st.info("Configure the incident scenario and stakeholder group, then click 'Generate Communication' to create a tailored report.")
        
        # Display module information
        st.subheader("About This Module")
        
        st.markdown("""
        The Stakeholder Communication Module automatically generates targeted communications for different audiences
        during normal operations and emergency situations. Benefits include:
        
        - **Tailored messaging** for different stakeholder needs and technical levels
        - **Multi-channel distribution** across email, SMS, social media, and more
        - **Consistent information** across all communication channels
        - **Automated generation** reduces response time during critical incidents
        - **Compliance support** with built-in regulatory reporting templates
        """)
        
        # Display example communication flow
        st.subheader("Communication Flow")
        
        # Create a simplified flow diagram
        flow_data = pd.DataFrame([
            ["Incident Detection", "Message Generation", 1],
            ["Message Generation", "Stakeholder Targeting", 1],
            ["Stakeholder Targeting", "Channel Selection", 1],
            ["Channel Selection", "Distribution", 1],
            ["Distribution", "Delivery Confirmation", 1],
            ["Delivery Confirmation", "Response Tracking", 1]
        ], columns=["From", "To", "Value"])
        
        fig = px.parallel_categories(
            flow_data, 
            dimensions=['From', 'To'],
            color="Value",
            color_continuous_scale=px.colors.sequential.Blues,
            labels={'From': 'Stage', 'To': 'Next Stage'}
        )
        
        st.plotly_chart(fig, use_container_width=True)

# Helper functions for generating different reports
def generate_technical_report(incident_data, channels):
    """Generate a technical team report."""
    # Create report container with technical styling
    report_container = st.container()
    
    with report_container:
        # Technical header
        st.markdown(f"## {incident_data['title']} [TECHNICAL]")
        st.markdown(f"**Incident ID:** INC-{hash(incident_data['timestamp']) % 10000:04d}")
        st.markdown(f"**Timestamp:** {incident_data['timestamp']} UTC")
        st.markdown(f"**Severity:** {incident_data['severity']}")
        
        if incident_data['severity'] in ["High", "Critical"]:
            st.error("IMMEDIATE ACTION REQUIRED")
        
        # System status with technical details
        st.markdown("### System Status (Technical)")
        
        for system, details in incident_data['systems'].items():
            if details.get('status', '') == "Critical":
                st.error(f"**{system.upper()}:** {details.get('status', 'Unknown')} - All hands required")
            elif details.get('status', '') == "Warning":
                st.warning(f"**{system.upper()}:** {details.get('status', 'Unknown')} - Monitoring required")
            else:
                st.success(f"**{system.upper()}:** {details.get('status', 'Healthy')} - Normal operation")
        
        # Technical details about the incident
        st.markdown("### Technical Assessment")
        
        if incident_data['title'] != "Current System Status Report":
            # For fault scenarios
            st.markdown(f"**Incident Description:** {incident_data['description']}")
            st.markdown(f"**Estimated Recovery Time:** {incident_data.get('estimated_recovery', 'Unknown')}")
            
            # Add technical fault details specific to each scenario
            if "power_outage" in incident_data['title'].lower():
                st.markdown("""
                **Technical Details:**
                - Outage detected in main grid connection at substations Alpha and Delta
                - Automatic transfer switches engaged at 60% of backup sites
                - UPS systems reporting 87% capacity across network
                - Load shedding protocol Alpha-3 automatically initiated
                
                **Required Actions:**
                1. Initiate fault isolation procedure TS-1045
                2. Activate backup generators at remaining critical sites
                3. Begin sequential restoration as per SOP-E3
                4. Prepare contingency for extended outage > 2 hours
                """)
            elif "water_main_break" in incident_data['title'].lower():
                st.markdown("""
                **Technical Details:**
                - Pressure drop detected in sectors 3B, 4A, and 4C
                - Flow meters indicating 4500L/min loss at junction B17
                - Backflow preventers activated at residential connections
                - Automated valves V47, V52, and V53 closed per protocol
                
                **Required Actions:**
                1. Deploy emergency response team to GPS coordinates 40.7128, -74.0060
                2. Initiate bypass pumping at stations P3 and P7
                3. Increase pressure gradually in adjacent sectors per SOP-W12
                4. Monitor water quality parameters at downstream sampling points
                """)
            elif "cyber_attack" in incident_data['title'].lower():
                st.markdown("""
                **Technical Details:**
                - Anomalous traffic detected from IP ranges 192.168.45.x and 10.72.18.x
                - 347 failed authentication attempts in last 15 minutes
                - Command injection attempts detected at API endpoints
                - IDS signature matches for known attack pattern EMERGENT-BADGER
                
                **Required Actions:**
                1. Activate security incident response plan IR-C42
                2. Implement firewall rules from security playbook SW-37
                3. Isolate affected systems and engage air-gapped backups
                4. Begin malware scanning and log analysis on all tier-1 systems
                """)
            elif "sewage_overflow" in incident_data['title'].lower():
                st.markdown("""
                **Technical Details:**
                - Flow meters reporting 178% capacity at stations S7, S12, and S15
                - Pump #3 and #4 at main station showing irregular current draw
                - Overflow sensors triggered at containment areas CA-3 and CA-4
                - Weather system contributing additional 75mm precipitation in service area
                
                **Required Actions:**
                1. Activate high-capacity backup pumps at all affected stations
                2. Divert flow to emergency retention basins per procedure SD-08
                3. Increase chemical treatment at primary treatment facility
                4. Deploy mobile pumping units to coordinates in emergency plan SE-22
                """)
            elif "grid_instability" in incident_data['title'].lower():
                st.markdown("""
                **Technical Details:**
                - Frequency fluctuations detected: 49.2-50.7 Hz, exceeding operational limits
                - Phase imbalance of 12.3% measured at main transformers
                - Protective relays triggered at 7 distribution substations
                - Harmonics exceeding IEEE 519 standards detected across grid
                
                **Required Actions:**
                1. Engage power quality correction systems at substations 3, 7, and 12
                2. Implement load balancing procedure LB-17 across affected phases
                3. Activate synchronous condensers for voltage support
                4. Prepare for potential islanding of critical infrastructure microgrids
                """)
        else:
            # For normal status report
            system_details = {
                "electricity": {
                    "load": f"{latest_data['electricity']['load']:.1f} MW",
                    "voltage": f"{latest_data['electricity']['voltage']:.1f} kV",
                    "frequency": f"{latest_data['electricity']['frequency']:.2f} Hz"
                },
                "water": {
                    "flow": f"{latest_data['water']['flow']:.1f} kL/h",
                    "pressure": f"{latest_data['water']['pressure']:.2f} bar",
                    "quality": f"{latest_data['water']['quality']:.1f}%"
                },
                "sewage": {
                    "flow": f"{latest_data['sewage']['flow']:.1f} kL/h",
                    "treatment": f"{latest_data['sewage']['treatment_efficiency']:.1f}%",
                    "contaminants": f"{latest_data['sewage']['contaminant_level']:.2f} ppm"
                },
                "banking": {
                    "transactions": f"{latest_data['banking']['transactions']:.1f} tps",
                    "response": f"{latest_data['banking']['response_time']:.3f} sec",
                    "success_rate": f"{latest_data['banking']['success_rate']:.2f}%"
                }
            }
            
            # Create detailed technical metrics table
            metrics_data = {
                "System": [],
                "Metric": [],
                "Value": [],
                "Status": []
            }
            
            for system, details in system_details.items():
                for metric, value in details.items():
                    metrics_data["System"].append(system.capitalize())
                    metrics_data["Metric"].append(metric.replace("_", " ").capitalize())
                    metrics_data["Value"].append(value)
                    
                    # Determine status based on system health
                    health_score = latest_data[system]["health_score"]
                    if health_score >= 90:
                        metrics_data["Status"].append("Normal")
                    elif health_score >= 75:
                        metrics_data["Status"].append("Acceptable")
                    elif health_score >= 60:
                        metrics_data["Status"].append("Warning")
                    else:
                        metrics_data["Status"].append("Critical")
            
            # Display metrics table
            metrics_df = pd.DataFrame(metrics_data)
            st.dataframe(metrics_df)
            
            # Display scheduled maintenance
            st.markdown("### Scheduled Maintenance")
            
            maintenance_data = {
                "System": ["Water", "Electricity", "Sewage", "Banking"],
                "Component": [
                    "Pumping Station 3",
                    "Substation Beta",
                    "Treatment Facility 2",
                    "Backup Data Center"
                ],
                "Schedule": [
                    "2025-03-24 02:00 - 06:00",
                    "2025-03-26 22:00 - 03:00",
                    "2025-03-25 08:00 - 14:00",
                    "2025-03-27 01:00 - 05:00"
                ],
                "Impact": [
                    "Reduced pressure in Zone 3",
                    "No impact (redundant systems)",
                    "30% capacity reduction",
                    "Increased latency (2-5ms)"
                ]
            }
            
            st.dataframe(pd.DataFrame(maintenance_data))

def generate_executive_report(incident_data, channels):
    """Generate an executive management report."""
    # Create report container with executive styling
    report_container = st.container()
    
    with report_container:
        # Executive header
        st.markdown(f"## {incident_data['title']} [EXECUTIVE SUMMARY]")
        st.markdown(f"**Report Time:** {incident_data['timestamp']}")
        st.markdown(f"**Priority Level:** {incident_data['severity']}")
        
        if incident_data['severity'] in ["High", "Critical"]:
            st.error("URGENT EXECUTIVE NOTIFICATION")
        
        # Executive dashboard with key metrics
        col1, col2 = st.columns(2)
        
        with col1:
            # System status overview
            st.markdown("### System Status")
            
            # Display status for each system with executive-friendly metrics
            for system, details in incident_data['systems'].items():
                status = details.get('status', 'Healthy')
                
                if status == "Critical":
                    st.error(f"**{system.capitalize()}:** {status}")
                elif status == "Warning":
                    st.warning(f"**{system.capitalize()}:** {status}")
                else:
                    st.success(f"**{system.capitalize()}:** {status}")
        
        with col2:
            # Business impact assessment
            st.markdown("### Business Impact")
            
            if incident_data['title'] != "Current System Status Report":
                # For fault scenarios
                affected_systems = [
                    system for system, details in incident_data['systems'].items()
                    if details.get('status', '') == "Critical"
                ]
                
                if affected_systems:
                    # Calculate financial impact based on affected systems
                    hourly_impact = len(affected_systems) * 75000  # Simplified calculation
                    
                    recovery_time = incident_data.get('estimated_recovery', '0 hours')
                    hours = int(recovery_time.split(' ')[0]) if 'hours' in recovery_time else 1
                    
                    total_impact = hourly_impact * hours
                    
                    # Display financial impact
                    st.metric(
                        "Estimated Financial Impact",
                        f"${total_impact:,}",
                        f"${hourly_impact:,} per hour"
                    )
                    
                    # Display service level impacts
                    service_impact = (len(affected_systems) / 4) * 100
                    st.metric(
                        "Service Level Impact",
                        f"{service_impact:.1f}%",
                        f"{len(affected_systems)} out of 4 systems affected"
                    )
                    
                    # Display estimated recovery
                    st.metric(
                        "Estimated Recovery",
                        incident_data.get('estimated_recovery', 'Unknown'),
                        f"{datetime.datetime.now() + datetime.timedelta(hours=hours):%H:%M:%S} completion"
                    )
                else:
                    st.success("No significant business impact detected")
            else:
                # For normal status report
                st.success("All systems operating within normal parameters")
                
                # Display aggregated health score
                avg_health = sum(latest_data[system]["health_score"] for system in ["electricity", "water", "sewage", "banking"]) / 4
                st.metric(
                    "Overall System Health",
                    f"{avg_health:.1f}%",
                    "Within operational targets"
                )
                
                # Display operational efficiency
                efficiency = np.random.randint(92, 99)
                st.metric(
                    "Operational Efficiency",
                    f"{efficiency}%",
                    f"+{efficiency - 91}% over target"
                )
        
        # Executive summary of the situation
        st.markdown("### Executive Summary")
        
        if incident_data['title'] != "Current System Status Report":
            # For fault scenarios
            st.markdown(f"**Incident Overview:** {incident_data['description']}")
            
            # Add executive summaries specific to each scenario
            if "power_outage" in incident_data['title'].lower():
                st.markdown("""
                **Executive Brief:**
                
                A significant power outage is affecting our main electricity distribution systems. Our emergency protocols have been activated and backup systems are currently being deployed. Critical operations are being maintained through UPS and generator systems.
                
                **Business Continuity:**
                - All Tier 1 services remain operational
                - Financial processing temporarily running at reduced capacity (78%)
                - Customer-facing systems operating on backup power with no service interruption
                
                **Key Decisions Required:**
                1. Approve emergency resource allocation for extended recovery operations
                2. Determine messaging strategy for external stakeholders
                3. Consider invoking force majeure clauses if outage extends beyond 4 hours
                """)
            elif "water_main_break" in incident_data['title'].lower():
                st.markdown("""
                **Executive Brief:**
                
                A major water main break has occurred, affecting water distribution in key service areas. Emergency repair crews have been dispatched, and service rerouting is in progress to minimize customer impact.
                
                **Business Continuity:**
                - Critical water services maintained at 65% capacity through alternate routing
                - Estimated 28,000 customers experiencing low pressure or service interruption
                - Water quality monitoring intensified to ensure continued safe water delivery
                
                **Key Decisions Required:**
                1. Authorize emergency procurement for specialized repair components
                2. Approve public notification plan for affected service areas
                3. Determine compensation strategy for severely impacted commercial customers
                """)
            elif "cyber_attack" in incident_data['title'].lower():
                st.markdown("""
                **Executive Brief:**
                
                We are experiencing a sophisticated cyber attack targeting our banking and financial systems. Security protocols have been activated and affected systems isolated to prevent unauthorized access to sensitive data.
                
                **Business Continuity:**
                - Core financial transactions diverted to secure backup systems
                - Customer data remains secure with no evidence of exfiltration
                - Authentication services temporarily operating with enhanced verification
                
                **Key Decisions Required:**
                1. Authorize engagement of external cybersecurity incident response team
                2. Approve customer communication strategy regarding security measures
                3. Determine timing for law enforcement and regulatory notifications
                """)
            elif "sewage_overflow" in incident_data['title'].lower():
                st.markdown("""
                **Executive Brief:**
                
                Heavy rainfall has triggered a sewage system overflow at key collection points. Emergency containment measures have been activated to minimize environmental impact, and regulatory authorities have been notified.
                
                **Business Continuity:**
                - Primary treatment facilities operating at 135% of normal capacity
                - Environmental monitoring teams deployed to affected waterways
                - Containment systems successfully capturing 82% of overflow volume
                
                **Key Decisions Required:**
                1. Authorize emergency expenditure for additional treatment chemicals
                2. Approve public health advisory for potentially affected areas
                3. Determine approach for regulatory compliance reporting
                """)
            elif "grid_instability" in incident_data['title'].lower():
                st.markdown("""
                **Executive Brief:**
                
                Electrical grid instability is affecting multiple utility systems. Stabilization procedures are in progress, and automated protection systems have engaged to prevent cascading failures.
                
                **Business Continuity:**
                - Critical infrastructure operating through conditioned power systems
                - Load balancing implemented to maintain essential services
                - Microgrids activated for hospital and emergency service support
                
                **Key Decisions Required:**
                1. Authorize implementation of voluntary load reduction program
                2. Approve reallocation of maintenance crews from scheduled to emergency work
                3. Determine coordination strategy with regional grid operators
                """)
            
            # Add resolution timeline
            st.markdown("### Resolution Timeline")
            
            recovery_time = incident_data.get('estimated_recovery', '0 hours')
            hours = int(recovery_time.split(' ')[0]) if 'hours' in recovery_time else 1
            
            # Create timeline with 4 key phases
            now = datetime.datetime.now()
            detection_time = now - datetime.timedelta(minutes=np.random.randint(5, 15))
            resolution_phases = [
                {"Phase": "Detection", "Time": detection_time.strftime("%H:%M:%S"), "Status": "Completed"},
                {"Phase": "Response Initiated", "Time": (detection_time + datetime.timedelta(minutes=5)).strftime("%H:%M:%S"), "Status": "Completed"},
                {"Phase": "Containment", "Time": (now + datetime.timedelta(minutes=30)).strftime("%H:%M:%S"), "Status": "In Progress"},
                {"Phase": "Resolution", "Time": (now + datetime.timedelta(hours=hours)).strftime("%H:%M:%S"), "Status": "Pending"}
            ]
            
            st.dataframe(pd.DataFrame(resolution_phases))
        else:
            # For normal status report
            st.markdown("""
            All integrated utility systems are operating within normal parameters. Regular monitoring and 
            maintenance activities continue as scheduled, with no significant deviations or anomalies detected 
            in the past 24 hours.
            
            The quarterly efficiency initiatives are showing positive results, with an overall 3% reduction 
            in operational costs across all utility systems compared to the previous quarter.
            """)
            
            # Add upcoming significant events
            st.markdown("### Strategic Initiatives & Key Metrics")
            
            # Create a simple metrics visualization
            metrics = {
                "Metric": ["System Uptime", "Cost Efficiency", "Customer Satisfaction", "Regulatory Compliance"],
                "Target": [99.99, 93.0, 90.0, 100.0],
                "Current": [99.98, 94.5, 92.3, 100.0],
                "Status": ["On Target", "Exceeding", "Exceeding", "On Target"]
            }
            
            metrics_df = pd.DataFrame(metrics)
            
            # Create a bar chart showing targets vs current performance
            fig = go.Figure()
            
            # Add target bars
            fig.add_trace(go.Bar(
                x=metrics_df["Metric"],
                y=metrics_df["Target"],
                name="Target",
                marker_color="lightgray"
            ))
            
            # Add current performance bars
            fig.add_trace(go.Bar(
                x=metrics_df["Metric"],
                y=metrics_df["Current"],
                name="Current Performance",
                marker_color="green"
            ))
            
            # Update layout
            fig.update_layout(
                title="Key Performance Indicators",
                barmode="group",
                xaxis_title="Metric",
                yaxis_title="Percentage (%)",
                legend_title="Measure"
            )
            
            st.plotly_chart(fig, use_container_width=True)

def generate_regulatory_report(incident_data, channels):
    """Generate a regulatory compliance report."""
    # Create report container with regulatory styling
    report_container = st.container()
    
    with report_container:
        # Regulatory header
        st.markdown(f"## {incident_data['title']} [REGULATORY NOTIFICATION]")
        st.markdown(f"**Report ID:** REG-{hash(incident_data['timestamp']) % 10000:04d}")
        st.markdown(f"**Submission Timestamp:** {incident_data['timestamp']} UTC")
        st.markdown(f"**Notification Type:** {incident_data['severity']} Priority")
        
        if incident_data['severity'] in ["High", "Critical"]:
            st.error("MANDATORY REGULATORY DISCLOSURE")
        
        # Systems status with regulatory focus
        st.markdown("### Affected Systems and Regulatory Domains")
        
        regulatory_domains = {
            "electricity": "Energy Regulatory Commission (ERC-2023-471)",
            "water": "Water Quality Control Board (WQCB-2024-33)",
            "sewage": "Environmental Protection Authority (EPA-SW-2022-19)",
            "banking": "Financial Systems Regulatory Authority (FSRA-2025-102)"
        }
        
        for system, details in incident_data['systems'].items():
            status = details.get('status', 'Compliant')
            
            if status == "Critical":
                st.error(f"**{system.capitalize()}:** {status} - {regulatory_domains[system]}")
            elif status == "Warning":
                st.warning(f"**{system.capitalize()}:** {status} - {regulatory_domains[system]}")
            else:
                st.success(f"**{system.capitalize()}:** Compliant - {regulatory_domains[system]}")
        
        # Incident details with regulatory implications
        if incident_data['title'] != "Current System Status Report":
            st.markdown("### Incident Description and Regulatory Implications")
            st.markdown(f"**Incident Summary:** {incident_data['description']}")
            
            # Add regulatory compliance details specific to each scenario
            if "power_outage" in incident_data['title'].lower():
                st.markdown("""
                **Regulatory Notification Requirements:**
                
                This incident requires notification under the following regulatory frameworks:
                - Energy Reliability Standards Act (Section 47.3) - Mandatory reporting of outages affecting >5000 customers
                - Critical Infrastructure Protection Protocol (CIPP-2023) - Notification of critical service disruption
                - Grid Resilience Reporting Requirements (GRRR-2024-17) - Documentation of backup system engagement
                
                **Mitigation Measures (Regulatory Compliance):**
                1. Backup generation activated in compliance with NERC Standard BAL-002-3
                2. Load shedding implemented according to approved Emergency Response Plan ERP-2023-05
                3. Critical customer notification completed per Customer Protection Rule 7.4
                4. Environmental monitoring of generator emissions initiated per EPA requirements
                
                **Regulatory Submission Timeline:**
                - Initial notification: Completed via this report
                - 24-hour detailed assessment: To be submitted by {(datetime.datetime.now() + datetime.timedelta(hours=24)).strftime("%Y-%m-%d %H:%M")}
                - 7-day comprehensive report: Required by {(datetime.datetime.now() + datetime.timedelta(days=7)).strftime("%Y-%m-%d")}
                """)
            elif "water_main_break" in incident_data['title'].lower():
                st.markdown("""
                **Regulatory Notification Requirements:**
                
                This incident requires notification under the following regulatory frameworks:
                - Safe Drinking Water Act (Section 1433) - Reporting of significant main breaks
                - Public Health Protection Standards (PHPS-2024-07) - Notification of service interruption
                - Water Infrastructure Integrity Program (WIIP) - Emergency repair documentation
                
                **Mitigation Measures (Regulatory Compliance):**
                1. Emergency chlorination implemented at affected junctions per EPA Standard 5.7
                2. Water quality sampling frequency increased in compliance with SDWA requirements
                3. Public notification issued according to Community Right-to-Know provisions
                4. Pressure monitoring implemented per Distribution System Rule 12.3
                
                **Regulatory Submission Timeline:**
                - Initial notification: Completed via this report
                - Water quality test results: To be submitted by {(datetime.datetime.now() + datetime.timedelta(hours=12)).strftime("%Y-%m-%d %H:%M")}
                - Infrastructure assessment: Required by {(datetime.datetime.now() + datetime.timedelta(days=5)).strftime("%Y-%m-%d")}
                """)
            elif "cyber_attack" in incident_data['title'].lower():
                st.markdown("""
                **Regulatory Notification Requirements:**
                
                This incident requires notification under the following regulatory frameworks:
                - Financial Systems Security Regulation (FSSR-2024) - Mandatory reporting of security incidents
                - Personal Data Protection Act (Section 33.2) - Notification of potential data breach events
                - Critical Infrastructure Cybersecurity Framework - Threat notification requirements
                
                **Mitigation Measures (Regulatory Compliance):**
                1. Incident containment implemented per NIST Cybersecurity Framework v1.1
                2. Customer data protected with encryption compliant with FIPS 140-3
                3. Forensic investigation initiated in accordance with regulatory preservation requirements
                4. System segregation implemented per defense-in-depth regulatory guidance
                
                **Regulatory Submission Timeline:**
                - Initial notification: Completed via this report
                - Preliminary security assessment: To be submitted by {(datetime.datetime.now() + datetime.timedelta(hours=24)).strftime("%Y-%m-%d %H:%M")}
                - Data impact analysis: Required by {(datetime.datetime.now() + datetime.timedelta(days=3)).strftime("%Y-%m-%d")}
                """)
            elif "sewage_overflow" in incident_data['title'].lower():
                st.markdown("""
                **Regulatory Notification Requirements:**
                
                This incident requires notification under the following regulatory frameworks:
                - Clean Water Act (Section 402) - Reporting of sanitary sewer overflows
                - Environmental Emergency Notification Protocol (EENP-2023) - Water contamination reporting
                - Public Watershed Protection Standards - Emergency discharge documentation
                
                **Mitigation Measures (Regulatory Compliance):**
                1. Containment systems deployed in compliance with EPA Overflow Response Plan
                2. Water sampling initiated at discharge points per Section 304(a)(1) requirements
                3. Public health advisory issued according to regulatory requirements
                4. Remediation plan activated per approved Sanitary Sewer Overflow Response Plan
                
                **Regulatory Submission Timeline:**
                - Initial notification: Completed via this report
                - Discharge volume estimation: To be submitted by {(datetime.datetime.now() + datetime.timedelta(hours=24)).strftime("%Y-%m-%d %H:%M")}
                - Environmental impact assessment: Required by {(datetime.datetime.now() + datetime.timedelta(days=5)).strftime("%Y-%m-%d")}
                """)
            elif "grid_instability" in incident_data['title'].lower():
                st.markdown("""
                **Regulatory Notification Requirements:**
                
                This incident requires notification under the following regulatory frameworks:
                - Grid Reliability Standards (GRS-2024-05) - Reporting of stability events
                - Energy Infrastructure Security Protocol - Notification of multi-system impacts
                - Interconnection Reliability Operating Limits (IROL) - Exceedance reporting
                
                **Mitigation Measures (Regulatory Compliance):**
                1. Frequency stabilization measures implemented per NERC Standard BAL-003-2
                2. Load balancing activated in compliance with approved Emergency Operations Plan
                3. Interconnection protection systems engaged per regulatory requirements
                4. Critical load preservation prioritized according to regulatory guidance
                
                **Regulatory Submission Timeline:**
                - Initial notification: Completed via this report
                - Stability event analysis: To be submitted by {(datetime.datetime.now() + datetime.timedelta(hours=24)).strftime("%Y-%m-%d %H:%M")}
                - Root cause determination: Required by {(datetime.datetime.now() + datetime.timedelta(days=7)).strftime("%Y-%m-%d")}
                """)
            
            # Add compliance certification
            st.markdown("### Compliance Certification")
            st.markdown("""
            I certify that this notification meets all applicable regulatory requirements for timeliness 
            and completeness. The information provided is true and accurate to the best of my knowledge, 
            and additional information will be provided as it becomes available in accordance with 
            regulatory submission timelines.
            
            **Compliance Officer:** J. Smith, CCRO
            **Regulatory ID:** REG-7724-EX
            """)
        else:
            # For normal status report
            st.markdown("### Compliance Status Summary")
            
            # Create compliance summary table
            compliance_data = {
                "Regulatory Framework": [
                    "Energy Reliability Standards (ERS)",
                    "Safe Drinking Water Act (SDWA)",
                    "Environmental Discharge Permits",
                    "Financial System Security Requirements"
                ],
                "Compliance Status": [
                    "Fully Compliant",
                    "Fully Compliant",
                    "Fully Compliant",
                    "Fully Compliant"
                ],
                "Last Audit": [
                    "2025-02-15",
                    "2025-01-22",
                    "2025-03-07",
                    "2025-02-28"
                ],
                "Next Reporting Due": [
                    "2025-04-15",
                    "2025-04-30",
                    "2025-06-30",
                    "2025-05-15"
                ]
            }
            
            st.dataframe(pd.DataFrame(compliance_data))
            
            # Add details on monitoring and verification
            st.markdown("### Monitoring and Verification")
            st.markdown("""
            All integrated utility systems remain in full compliance with applicable regulatory requirements.
            Continuous monitoring systems are operational, with no reportable events or threshold exceedances
            in the current reporting period.
            
            Regular compliance testing and verification are proceeding according to the approved annual 
            compliance plan. All documentation is being maintained in accordance with regulatory retention 
            requirements.
            """)
            
            # Add upcoming regulatory activities
            st.markdown("### Upcoming Regulatory Activities")
            
            upcoming_data = {
                "Activity": [
                    "Quarterly Compliance Report - Electricity",
                    "Annual Water Quality Certification",
                    "Environmental Impact Assessment Renewal",
                    "Cybersecurity Compliance Audit"
                ],
                "Due Date": [
                    "2025-04-15",
                    "2025-05-30",
                    "2025-06-12",
                    "2025-04-22"
                ],
                "Status": [
                    "In Preparation (75% complete)",
                    "In Preparation (30% complete)",
                    "Not Started",
                    "In Preparation (60% complete)"
                ],
                "Responsible Officer": [
                    "M. Johnson",
                    "A. Williams",
                    "R. Davis",
                    "J. Smith"
                ]
            }
            
            st.dataframe(pd.DataFrame(upcoming_data))

def generate_pr_report(incident_data, channels):
    """Generate a public relations team report."""
    # Create report container with PR styling
    report_container = st.container()
    
    with report_container:
        # PR header
        st.markdown(f"## {incident_data['title']} [PR TEAM BRIEF]")
        st.markdown(f"**Briefing Time:** {incident_data['timestamp']}")
        st.markdown(f"**Public Interest Level:** {incident_data['severity']}")
        
        if incident_data['severity'] in ["High", "Critical"]:
            st.error("IMMEDIATE PR RESPONSE REQUIRED")
        
        # Situation overview for PR team
        st.markdown("### Situation Overview")
        
        if incident_data['title'] != "Current System Status Report":
            # For fault scenarios
            st.markdown(f"**Incident Summary (Internal):** {incident_data['description']}")
            
            # Add PR response guidance specific to each scenario
            if "power_outage" in incident_data['title'].lower():
                st.markdown("""
                **Public Relations Strategy:**
                
                A major power outage is affecting our electricity distribution network. This will likely generate
                significant public interest and potential customer concern. Social media monitoring indicates
                conversation volume has increased 450% in the past 30 minutes.
                
                **Key Messages:**
                1. Our teams are actively working to restore power as quickly and safely as possible
                2. Backup systems have been activated to maintain critical services
                3. Real-time updates are available through our customer app and website
                4. We have activated mutual aid agreements with neighboring utilities to expedite restoration
                
                **Anticipated Questions:**
                - What caused the outage? _(Initial response: "We're investigating the root cause")_
                - When will power be restored? _(Emphasize safety and avoid specific timing commitments)_
                - Will this happen again? _(Focus on resilience investments and continuous improvement)_
                
                **Communication Channels:**
                - Social media updates every 30 minutes
                - Traditional media statement ready for distribution
                - Customer service briefed with approved talking points
                - Emergency notification system activated for affected areas
                """)
            elif "water_main_break" in incident_data['title'].lower():
                st.markdown("""
                **Public Relations Strategy:**
                
                A significant water main break is affecting service in multiple neighborhoods. This will
                generate immediate public health concerns and service questions from affected customers.
                Visual media impact will be high due to visible flooding and repair activity.
                
                **Key Messages:**
                1. Repairs are underway to restore service as quickly as possible
                2. Water quality is being continuously monitored to ensure safety
                3. Alternative water sources are being provided in severely affected areas
                4. Traffic detours are in place around the repair zone for public safety
                
                **Anticipated Questions:**
                - Is my water safe to drink? _(Emphasize monitoring and testing protocols)_
                - Why did this happen? _(Focus on aging infrastructure and renewal programs)_
                - When will service be restored? _(Provide realistic timeframes with contingencies)_
                
                **Communication Channels:**
                - Door-to-door notifications in directly affected areas
                - Community alert system for service updates
                - Local media briefing scheduled for next update window
                - Service map updated on company website and app
                """)
            elif "cyber_attack" in incident_data['title'].lower():
                st.markdown("""
                **Public Relations Strategy:**
                
                We are responding to a cybersecurity incident affecting our banking systems. This is a highly
                sensitive matter requiring careful communication to maintain public confidence while meeting
                regulatory disclosure requirements.
                
                **Key Messages:**
                1. Customer data protection is our highest priority
                2. We are working with cybersecurity experts to address the situation
                3. Additional security measures have been implemented as a precaution
                4. Regular operations continue through secure backup systems
                
                **Anticipated Questions:**
                - Has my personal information been compromised? _(Emphasize no evidence of data exfiltration)_
                - Who is responsible for the attack? _(Avoid attribution until investigation complete)_
                - How can I protect my accounts? _(Provide practical security advice for customers)_
                
                **Communication Channels:**
                - Direct customer communication through secure channels only
                - Prepared statement for media inquiries (reactive only)
                - Regulatory disclosures as legally required
                - Security advisory posted on company websites
                """)
            elif "sewage_overflow" in incident_data['title'].lower():
                st.markdown("""
                **Public Relations Strategy:**
                
                A sewage overflow event is occurring due to heavy rainfall. This presents both environmental
                and public health communication challenges. Visibility will be high, with potential for
                negative public reaction and community concern.
                
                **Key Messages:**
                1. All available resources are deployed to contain and mitigate the overflow
                2. Public health and environmental protection are our top priorities
                3. The system is operating as designed during extreme weather conditions
                4. Water quality monitoring has been increased in affected areas
                
                **Anticipated Questions:**
                - Is there a health risk? _(Provide clear guidance from public health authorities)_
                - Will this contaminate drinking water? _(Emphasize separation of systems)_
                - Why wasn't this prevented? _(Discuss infrastructure capacity and climate adaptation)_
                
                **Communication Channels:**
                - Public health advisory through official channels
                - Environmental impact updates on company website
                - Community briefing for affected neighborhoods
                - Regular updates to environmental agencies and local officials
                """)
            elif "grid_instability" in incident_data['title'].lower():
                st.markdown("""
                **Public Relations Strategy:**
                
                Grid instability is affecting multiple utility systems. This is a technical issue that will
                require clear, simplified communication to help the public understand the situation without
                creating unnecessary alarm.
                
                **Key Messages:**
                1. Our engineers are implementing grid stabilization measures
                2. Critical services remain operational through backup systems
                3. The situation is being actively managed to prevent wider impacts
                4. Conservation measures will help support system stability
                
                **Anticipated Questions:**
                - Will there be blackouts? _(Be honest about possibility while emphasizing prevention efforts)_
                - What's causing the instability? _(Explain in simple, non-technical terms)_
                - How can I prepare? _(Provide practical guidance for temporary service interruptions)_
                
                **Communication Channels:**
                - Conservation request through broad media channels
                - System status updates on company website and social media
                - Pre-emptive outreach to critical service providers
                - Regular updates to public officials and emergency management agencies
                """)
            
            # Media statement draft
            st.markdown("### Draft Media Statement")
            
            # Create a draft statement based on the incident type
            if "power_outage" in incident_data['title'].lower():
                draft_statement = """
                [UTILITY NAME] is responding to a power outage affecting portions of our service area. Our crews have been dispatched and are working to safely restore power as quickly as possible. We understand the inconvenience this causes and appreciate our customers' patience.
                
                Backup systems have been activated to maintain service to critical facilities, including hospitals and emergency services. Real-time outage information and restoration updates are available on our website and mobile app.
                
                For customers with medical needs requiring electricity, please activate your emergency plans and contact our priority service line if you require assistance. We are working closely with emergency management agencies to support those with critical needs.
                
                We will provide updates as more information becomes available. Customer service representatives are available at [PHONE NUMBER] to answer questions.
                """
            elif "water_main_break" in incident_data['title'].lower():
                draft_statement = """
                [UTILITY NAME] crews are responding to a significant water main break affecting service in the [AREA] region. Emergency repairs are underway, and we expect to restore normal water service within [TIMEFRAME].
                
                Water quality testing is being conducted throughout the affected area, and we are working closely with public health officials to ensure water safety. As a precaution, customers in the affected area may notice reduced water pressure or temporary discoloration when service is restored.
                
                We have established water distribution points at [LOCATIONS] for residents experiencing service disruptions. For elderly or disabled customers needing assistance, please call our customer service center at [PHONE NUMBER].
                
                We apologize for the inconvenience and thank you for your patience as we complete these emergency repairs.
                """
            elif "cyber_attack" in incident_data['title'].lower():
                draft_statement = """
                [ORGANIZATION NAME] is currently addressing a cybersecurity incident affecting certain systems. We have implemented our security response protocols and are working with cybersecurity experts to resolve the situation.
                
                We have no evidence at this time that customer personal information has been compromised. As a precaution, we have implemented additional security measures and customers may experience temporary delays in some online services.
                
                Protecting our customers' data is our highest priority. We will provide updates as our investigation continues, and we encourage customers to monitor their accounts and report any unusual activity to our secure customer service line at [PHONE NUMBER].
                
                We recommend that all customers maintain good security practices, including using strong passwords and enabling two-factor authentication where available.
                """
            elif "sewage_overflow" in incident_data['title'].lower():
                draft_statement = """
                Due to extraordinary rainfall, [UTILITY NAME] is managing a sewage overflow situation at [LOCATION]. Our emergency response teams are on site implementing containment and mitigation measures.
                
                We are working closely with environmental agencies and public health officials to monitor and address any potential impacts. As a precaution, the public is advised to avoid contact with water in [AFFECTED WATERWAYS] until further notice.
                
                The overflow is a result of the collection system receiving rainfall volumes exceeding its designed capacity. Our long-term infrastructure improvement plan includes projects to increase system capacity and resilience to extreme weather events.
                
                We will continue to provide updates as the situation develops. For more information, please visit our website or contact our environmental response team at [PHONE NUMBER].
                """
            elif "grid_instability" in incident_data['title'].lower():
                draft_statement = """
                [UTILITY NAME] engineers are currently addressing grid instability affecting our electricity distribution network. Our technical teams have implemented stabilization measures to prevent wider impacts.
                
                At this time, we are asking customers to conserve electricity where possible by reducing usage of high-consumption appliances, particularly between [PEAK TIMES]. These conservation efforts will help maintain system stability as we complete necessary technical adjustments.
                
                Critical services including hospitals, emergency response facilities, and essential infrastructure remain operational through dedicated backup systems. We are coordinating closely with emergency management agencies throughout this event.
                
                We will provide updates as our stabilization efforts progress. For real-time system status information, please visit our website or contact our customer service center at [PHONE NUMBER].
                """
            else:
                draft_statement = "Draft statement will be generated based on incident details."
            
            st.text_area("Media Statement", draft_statement, height=300)
            
            # Social media content suggestions
            st.markdown("### Social Media Content")
            
            twitter_updates = [
                f"We're aware of the {incident_type.replace('_', ' ')} affecting our services and are working to resolve it. Updates to follow. #ServiceAlert",
                f"UPDATE: Crews are on site responding to the {incident_type.replace('_', ' ')}. Estimated restoration time: {incident_data.get('estimated_recovery', 'TBD')}. #ServiceUpdate",
                "Safety reminder: Report any [hazardous conditions] to our emergency line at XXX-XXX-XXXX. #PublicSafety"
            ]
            
            for i, tweet in enumerate(twitter_updates):
                st.markdown(f"**Tweet {i+1}:** {tweet}")
            
            # Talking points for media interviews
            st.markdown("### Key Talking Points")
            
            talking_points = [
                "We are fully mobilized to address this situation and restore normal service",
                "Public safety remains our highest priority throughout our response",
                "We have activated our emergency response plan and all necessary resources",
                "We understand the inconvenience this causes and appreciate our customers' patience",
                "We will provide regular updates as new information becomes available"
            ]
            
            for point in talking_points:
                st.markdown(f"- {point}")
        else:
            # For normal status report
            st.markdown("""
            All utility systems are operating normally. This regular status update provides an opportunity
            to share positive operational news and reinforce public confidence in our services.
            """)
            
            # Proactive communication opportunities
            st.markdown("### Proactive Communication Opportunities")
            
            opportunities = [
                "Highlight recent system reliability improvements",
                "Share progress on infrastructure modernization projects",
                "Promote conservation and efficiency programs",
                "Showcase community engagement and corporate sustainability initiatives",
                "Remind customers of available self-service tools and resources"
            ]
            
            for opp in opportunities:
                st.markdown(f"- {opp}")
            
            # Upcoming public engagement
            st.markdown("### Upcoming Public Engagement")
            
            engagement_data = {
                "Activity": [
                    "Community Advisory Board Meeting",
                    "Infrastructure Open House",
                    "School Safety Education Program",
                    "Customer Appreciation Event"
                ],
                "Date": [
                    "2025-04-10",
                    "2025-04-22",
                    "2025-05-05",
                    "2025-05-15"
                ],
                "Status": [
                    "Confirmed",
                    "Planning",
                    "Confirmed",
                    "Planning"
                ],
                "Lead": [
                    "J. Roberts",
                    "M. Williams",
                    "A. Johnson",
                    "T. Martinez"
                ]
            }
            
            st.dataframe(pd.DataFrame(engagement_data))
            
            # Positive news items
            st.markdown("### Positive News Opportunities")
            
            st.markdown("""
            1. **System Reliability Milestone:** Our electricity distribution network has achieved 99.98% uptime for the third consecutive quarter, exceeding industry benchmarks.
            
            2. **Water Quality Recognition:** Recent independent testing has recognized our water treatment facilities for excellence in exceeding quality standards.
            
            3. **Environmental Leadership:** Our wastewater recycling initiative has reduced freshwater consumption by 15% in industrial applications this year.
            
            4. **Technology Innovation:** The new customer self-service portal has reduced call center volume by 22% while improving satisfaction scores.
            """)

def generate_public_report(incident_data, channels):
    """Generate a public-facing report."""
    # Create report container with public-friendly styling
    report_container = st.container()
    
    with report_container:
        # Public-friendly header
        if incident_data['title'] != "Current System Status Report":
            # For fault scenarios, use a service alert format
            st.markdown(f"## Service Alert: {incident_data['title'].replace('Incident Report: ', '')}")
            
            # Display a clear status indicator
            if incident_data['severity'] in ["High", "Critical"]:
                st.error("⚠️ SERVICE DISRUPTION IN PROGRESS")
            else:
                st.warning("⚠️ POTENTIAL SERVICE IMPACT")
        else:
            # For normal status report
            st.markdown("## System Status: All Services Operating Normally")
            st.success("✅ All systems are currently operating as expected")
        
        st.markdown(f"*Last updated: {incident_data['timestamp']}*")
        
        # Simple system status display
        st.markdown("### Current Status")
        
        # Create columns for each system
        col1, col2, col3, col4 = st.columns(4)
        
        # Display status for each system with public-friendly descriptions
        with col1:
            electricity_status = incident_data['systems']['electricity'].get('status', 'Healthy')
            if electricity_status == "Critical":
                st.error("⚠️ Electricity: Outage")
            elif electricity_status == "Warning":
                st.warning("⚠️ Electricity: Issues")
            else:
                st.success("✅ Electricity: Normal")
                
        with col2:
            water_status = incident_data['systems']['water'].get('status', 'Healthy')
            if water_status == "Critical":
                st.error("⚠️ Water: Disruption")
            elif water_status == "Warning":
                st.warning("⚠️ Water: Issues")
            else:
                st.success("✅ Water: Normal")
                
        with col3:
            sewage_status = incident_data['systems']['sewage'].get('status', 'Healthy')
            if sewage_status == "Critical":
                st.error("⚠️ Sewage: Disruption")
            elif sewage_status == "Warning":
                st.warning("⚠️ Sewage: Issues")
            else:
                st.success("✅ Sewage: Normal")
                
        with col4:
            banking_status = incident_data['systems']['banking'].get('status', 'Healthy')
            if banking_status == "Critical":
                st.error("⚠️ Banking: Disruption")
            elif banking_status == "Warning":
                st.warning("⚠️ Banking: Issues")
            else:
                st.success("✅ Banking: Normal")
        
        # Public information based on incident type
        if incident_data['title'] != "Current System Status Report":
            # For fault scenarios
            st.markdown("### What's Happening")
            
            # Create simple, public-friendly description based on scenario
            if "power_outage" in incident_data['title'].lower():
                st.markdown("""
                We're currently experiencing a power outage in parts of our service area. Our repair teams are working to restore service as quickly as possible.
                
                **What to expect:**
                - Affected areas may be without power
                - Traffic signals may be affected in some areas
                - Some water services may experience reduced pressure
                
                **Estimated restoration time:** We expect to restore service within the next few hours. We'll update this estimate as our work progresses.
                """)
            elif "water_main_break" in incident_data['title'].lower():
                st.markdown("""
                A water main break is affecting water service in some areas. Repairs are underway to fix the break and restore normal water service.
                
                **What to expect:**
                - Some areas may have low water pressure or no water service
                - Water may appear cloudy or discolored when service is restored
                - Road closures near the repair area
                
                **Estimated restoration time:** Repairs typically take 4-6 hours to complete. We'll update this page as work progresses.
                """)
            elif "cyber_attack" in incident_data['title'].lower():
                st.markdown("""
                We're addressing a technical issue affecting some of our online banking services. Our security team is working to resolve the situation.
                
                **What to expect:**
                - Some online banking features may be temporarily unavailable
                - Longer wait times for electronic transactions
                - In-person services remain available at all locations
                
                **Service updates:** We expect to restore full service within the next few hours. Your account information remains secure.
                """)
            elif "sewage_overflow" in incident_data['title'].lower():
                st.markdown("""
                Due to heavy rainfall, we're experiencing sewage system overflows in some areas. Our response teams are working to manage the situation.
                
                **What to expect:**
                - Avoid contact with standing water in affected areas
                - Possible odors in areas near overflow points
                - Cleanup crews working in affected areas
                
                **Public health notice:** Please avoid recreational activities in affected waterways until further notice. We are working with health officials to monitor the situation.
                """)
            elif "grid_instability" in incident_data['title'].lower():
                st.markdown("""
                We're currently managing some instability in our electrical grid. Our engineers are working to stabilize the system and prevent outages.
                
                **What to expect:**
                - Possible brief power fluctuations
                - Potential for short, localized outages
                - Emergency systems operating normally
                
                **How you can help:** Please conserve electricity where possible, especially between 5-8 PM. Reducing usage of high-consumption appliances will help maintain stability.
                """)
            
            # What we're doing section
            st.markdown("### What We're Doing")
            
            # Create simple, public-friendly action description
            if "power_outage" in incident_data['title'].lower():
                st.markdown("""
                - Our emergency response teams are identifying and repairing the cause of the outage
                - Backup generators have been activated for critical services
                - Additional crews have been called in to speed up restoration
                - We're updating our outage map and alerts in real-time
                """)
            elif "water_main_break" in incident_data['title'].lower():
                st.markdown("""
                - Repair crews are on site fixing the broken water main
                - Water has been rerouted where possible to minimize service disruptions
                - Water quality testing is being conducted throughout the system
                - We've set up water distribution points in severely affected areas
                """)
            elif "cyber_attack" in incident_data['title'].lower():
                st.markdown("""
                - Our security team is working to resolve the technical issues
                - Additional safeguards have been implemented to protect customer data
                - We're processing critical transactions through backup systems
                - Customer service staff are available to assist with urgent needs
                """)
            elif "sewage_overflow" in incident_data['title'].lower():
                st.markdown("""
                - Emergency teams are managing overflow at affected locations
                - Pumping systems are operating at maximum capacity
                - Environmental monitoring is ongoing at affected waterways
                - We're coordinating with environmental and health agencies
                """)
            elif "grid_instability" in incident_data['title'].lower():
                st.markdown("""
                - Engineers are implementing grid stabilization measures
                - Critical infrastructure has been secured with backup power
                - We're adjusting generation and distribution to balance the system
                - Additional resources have been activated to prevent outages
                """)
            
            # What you should do section
            st.markdown("### What You Should Do")
            
            # Create simple, public-friendly advice
            if "power_outage" in incident_data['title'].lower():
                st.markdown("""
                - Keep refrigerator and freezer doors closed to maintain cold temperatures
                - Unplug sensitive electronics to protect from power surges when service is restored
                - Use flashlights instead of candles for safety
                - Check on elderly neighbors or those with medical needs
                
                **Report emergencies:** Call 911 for life-threatening emergencies
                
                **Report outages:** Use our app or call (555) 123-4567
                """)
            elif "water_main_break" in incident_data['title'].lower():
                st.markdown("""
                - Store water for essential needs if you're in an affected area
                - Run cold water taps for a few minutes when service is restored
                - Avoid doing laundry or running dishwashers until water runs clear
                - Use bottled water for drinking and cooking if you notice discoloration
                
                **Water distribution:** If you need emergency water, visit the following locations:
                - Community Center at 123 Main St (7 AM - 7 PM)
                - North Side Fire Station (24 hours)
                """)
            elif "cyber_attack" in incident_data['title'].lower():
                st.markdown("""
                - Monitor your accounts for any unusual activity
                - Consider using in-person services for urgent banking needs
                - Be alert for potential phishing attempts related to this incident
                - Keep your contact information updated so we can reach you with important updates
                
                **Customer support:** Call (555) 234-5678 for assistance
                """)
            elif "sewage_overflow" in incident_data['title'].lower():
                st.markdown("""
                - Avoid contact with standing water in affected areas
                - Stay away from marked overflow areas and affected waterways
                - Report any sewage backups in your home immediately
                - Follow public health guidance regarding recreational water activities
                
                **Report issues:** Call (555) 345-6789 to report sewage emergencies
                """)
            elif "grid_instability" in incident_data['title'].lower():
                st.markdown("""
                - Reduce electricity usage during peak hours (5-8 PM)
                - Avoid using large appliances like washers, dryers, and dishwashers
                - Keep devices charged in case of brief outages
                - Check on vulnerable family members or neighbors
                
                **Energy conservation tips:**
                - Adjust thermostat settings by 2-3 degrees
                - Turn off unnecessary lights and electronics
                - Delay high-energy activities until after 8 PM
                """)
            
            # Updates section
            st.markdown("### Updates")
            
            # Create a simple timeline of updates
            updates = [
                {
                    "time": (datetime.datetime.now() - datetime.timedelta(minutes=np.random.randint(30, 60))).strftime("%H:%M"),
                    "message": f"Issue identified: {incident_data['description']}"
                },
                {
                    "time": (datetime.datetime.now() - datetime.timedelta(minutes=np.random.randint(15, 29))).strftime("%H:%M"),
                    "message": "Response teams dispatched to affected areas"
                },
                {
                    "time": datetime.datetime.now().strftime("%H:%M"),
                    "message": f"Current estimate: Service restoration within {incident_data.get('estimated_recovery', 'a few hours')}"
                }
            ]
            
            for update in updates:
                st.markdown(f"**{update['time']}:** {update['message']}")
            
            # Where to get more information
            st.markdown("### Stay Informed")
            
            st.markdown("""
            - Download our mobile app for real-time alerts
            - Follow us on social media @UtilityServiceUpdates
            - Call our automated status line: (555) 456-7890
            - Sign up for text alerts by texting UPDATES to 12345
            """)
        else:
            # For normal status report
            st.markdown("### Everything is Working Normally")
            
            st.markdown("""
            All utility systems are currently operating as expected. There are no service disruptions or scheduled maintenance activities affecting our services at this time.
            
            - **Electricity:** Operating normally
            - **Water:** Operating normally
            - **Sewage:** Operating normally
            - **Banking Systems:** Operating normally
            """)
            
            # Upcoming planned maintenance
            st.markdown("### Upcoming Planned Maintenance")
            
            maintenance_data = {
                "System": ["Water"],
                "Date": ["April 15, 2025"],
                "Time": ["2:00 AM - 6:00 AM"],
                "Areas Affected": ["Downtown, North Side"],
                "Impact": ["Possible low water pressure"]
            }
            
            st.dataframe(pd.DataFrame(maintenance_data))
            
            # Helpful resources
            st.markdown("### Customer Resources")
            
            st.markdown("""
            - **Report an issue:** Use our mobile app or call (555) 123-4567
            - **Billing questions:** Call (555) 234-5678 (Mon-Fri, 8 AM - 7 PM)
            - **Energy saving tips:** Visit our website for seasonal efficiency advice
            - **Emergency preparedness:** Download our family emergency planning guide
            """)

# Helper functions for communication previews
def display_email_preview(incident_data, stakeholder_group):
    """Display a preview of an email communication."""
    st.markdown("#### Email Preview")
    
    # Create different email content based on stakeholder group
    if stakeholder_group == "technical_team":
        subject = f"ALERT: {incident_data['title']} - TECHNICAL RESPONSE REQUIRED"
        
        content = f"""
        TO: Technical Response Team <technical-team@organization.com>
        FROM: QEAIMS Alert System <alerts@organization.com>
        SUBJECT: {subject}
        PRIORITY: High
        
        TECHNICAL ALERT - IMMEDIATE RESPONSE REQUIRED
        
        Incident: {incident_data['title']}
        Time: {incident_data['timestamp']}
        Severity: {incident_data['severity']}
        
        Affected systems:
        """
        
        for system, details in incident_data['systems'].items():
            status = details.get('status', 'Healthy')
            if status in ["Critical", "Warning"]:
                content += f"- {system.upper()}: {status}\n"
        
        content += f"""
        Response protocol: TP-{hash(incident_data['title']) % 100 + 1:02d}
        
        Technical team assembly required in EOC. Remote team members join conference bridge Alpha.
        
        Login to QEAIMS dashboard for detailed system status and response coordination.
        
        --
        This is an automated alert from the QEAIMS Alert System.
        """
    elif stakeholder_group == "executive_management":
        subject = f"Executive Brief: {incident_data['title']}"
        
        content = f"""
        TO: Executive Leadership Team <executive-team@organization.com>
        FROM: Incident Response <incident-response@organization.com>
        SUBJECT: {subject}
        
        Executive Leadership Team,
        
        This is to inform you of an operational incident affecting our utility systems:
        
        Incident: {incident_data['title']}
        Time: {incident_data['timestamp']}
        Priority: {incident_data['severity']}
        Estimated Recovery: {incident_data.get('estimated_recovery', 'To be determined')}
        
        Business Impact:
        """
        
        affected_systems = [
            system for system, details in incident_data['systems'].items()
            if details.get('status', '') == "Critical"
        ]
        
        if affected_systems:
            content += f"- {len(affected_systems)} critical systems affected\n"
            content += f"- Estimated financial impact: ${len(affected_systems) * 75000 * 2:,}\n"
            content += f"- Service level impact: {(len(affected_systems) / 4) * 100:.1f}%\n"
        else:
            content += "- Minimal business impact at this time\n"
        
        content += f"""
        Our incident response teams are fully engaged and executing our response plan. A detailed briefing has been scheduled for {(datetime.datetime.now() + datetime.timedelta(hours=1)).strftime("%H:%M")} in the Executive Briefing Room.
        
        A comprehensive situation report will follow within the next hour.
        
        Regards,
        Incident Response Team
        """
    else:
        subject = f"Important: {incident_data['title']}"
        
        content = f"""
        TO: [Recipient]
        FROM: Utility Service Alerts <alerts@utility.com>
        SUBJECT: {subject}
        
        Dear Customer,
        
        We want to inform you about a service issue that may affect you:
        
        {incident_data['description']}
        
        Our teams are working to resolve this issue as quickly as possible. The estimated restoration time is {incident_data.get('estimated_recovery', 'as soon as possible')}.
        
        What this means for you:
        """
        
        if "power_outage" in incident_data['title'].lower():
            content += """
        - You may experience a temporary power outage
        - Keep refrigerator doors closed to maintain cold temperatures
        - Unplug sensitive electronics to protect from power surges
        """
        elif "water_main_break" in incident_data['title'].lower():
            content += """
        - You may experience low water pressure or temporary service interruption
        - Store water for essential needs if you're in an affected area
        - Run cold water taps for a few minutes when service is restored
        """
        elif "cyber_attack" in incident_data['title'].lower():
            content += """
        - Some online banking services may be temporarily unavailable
        - Monitor your accounts for any unusual activity
        - Consider using in-person services for urgent banking needs
        """
        elif "sewage_overflow" in incident_data['title'].lower():
            content += """
        - Avoid contact with standing water in affected areas
        - Stay away from marked overflow areas
        - Follow public health guidance regarding recreational water activities
        """
        elif "grid_instability" in incident_data['title'].lower():
            content += """
        - You may experience brief power fluctuations
        - Please reduce electricity usage during peak hours (5-8 PM)
        - Keep devices charged in case of brief outages
        """
        
        content += """
        
        For updates and more information:
        - Visit our website: www.utility.com/servicealerts
        - Download our mobile app for real-time alerts
        - Call our service line: (555) 123-4567
        
        We apologize for any inconvenience and thank you for your patience.
        
        Sincerely,
        Customer Service Team
        """
    
    # Display email in a box
    st.text_area("Email Content", content, height=400)

def display_sms_preview(incident_data, stakeholder_group):
    """Display a preview of an SMS communication."""
    st.markdown("#### SMS Message Preview")
    
    # Create different SMS content based on stakeholder group
    if stakeholder_group == "technical_team":
        message = f"ALERT: {incident_data['title']} - Technical response required. Login to dashboard and join bridge Alpha immediately. Protocol TP-{hash(incident_data['title']) % 100 + 1:02d} activated."
    elif stakeholder_group == "executive_management":
        message = f"EXEC ALERT: {incident_data['title']} - Severity: {incident_data['severity']}. Briefing at {(datetime.datetime.now() + datetime.timedelta(hours=1)).strftime('%H:%M')} in Exec Briefing Room. Situation report to follow."
    else:
        if "power_outage" in incident_data['title'].lower():
            message = f"UTILITY ALERT: Power outage affecting your area. Crews working to restore service. Est. restoration: {incident_data.get('estimated_recovery', 'ASAP')}. Updates: utility.com/alerts"
        elif "water_main_break" in incident_data['title'].lower():
            message = f"UTILITY ALERT: Water main break may affect your service. Store water for essential needs. Est. restoration: {incident_data.get('estimated_recovery', 'ASAP')}. Updates: utility.com/alerts"
        elif "cyber_attack" in incident_data['title'].lower():
            message = "BANK ALERT: We're addressing technical issues affecting online banking. Your data remains secure. Use mobile app or visit a branch for urgent needs."
        elif "sewage_overflow" in incident_data['title'].lower():
            message = "UTILITY ALERT: Heavy rainfall causing sewage system issues. Avoid standing water in affected areas. Follow health guidance. Updates: utility.com/alerts"
        elif "grid_instability" in incident_data['title'].lower():
            message = "UTILITY ALERT: Grid instability may cause power fluctuations. Please reduce electricity usage 5-8 PM. Keep devices charged. Updates: utility.com/alerts"
    
    # Style the SMS preview
    st.markdown(f"""
    <div style="background-color: #f0f0f0; border-radius: 10px; padding: 15px; max-width: 300px; font-family: sans-serif;">
    <div style="font-weight: bold; margin-bottom: 5px;">SMS Alert</div>
    <div style="background-color: white; border-radius: 10px; padding: 10px;">
    {message}
    </div>
    <div style="font-size: 0.8em; text-align: right; margin-top: 5px;">Now</div>
    </div>
    """, unsafe_allow_html=True)
    
    # Show character count
    st.caption(f"Character count: {len(message)} (Standard SMS limit: 160 characters)")

def display_emergency_preview(incident_data):
    """Display a preview of an emergency notification."""
    st.markdown("#### Emergency Notification Preview")
    
    # Create emergency notification content
    if "power_outage" in incident_data['title'].lower():
        alert_type = "Power Outage"
        message = f"EMERGENCY ALERT: Power outage affecting {np.random.randint(5, 20)} neighborhoods. Estimated restoration: {incident_data.get('estimated_recovery', 'Unknown')}. Critical medical needs: Call (555) 999-7777."
    elif "water_main_break" in incident_data['title'].lower():
        alert_type = "Water Emergency"
        message = f"EMERGENCY ALERT: Water main break affecting service in {np.random.randint(3, 10)} neighborhoods. Bottled water available at community centers. Health concerns: Call (555) 999-8888."
    elif "cyber_attack" in incident_data['title'].lower():
        alert_type = "Important Alert"
        message = "IMPORTANT ALERT: Banking systems temporarily affected by security measures. Limit non-essential transactions. In-person services available at all branches."
    elif "sewage_overflow" in incident_data['title'].lower():
        alert_type = "Public Health Alert"
        message = "PUBLIC HEALTH ALERT: Sewage overflow in multiple areas due to heavy rainfall. Avoid contact with affected waterways. Health concerns: Call Public Health at (555) 999-9999."
    elif "grid_instability" in incident_data['title'].lower():
        alert_type = "Utility Alert"
        message = "UTILITY ALERT: Electrical grid instability may cause intermittent outages. Reduce power usage 5-8 PM. Medical equipment users activate backup plans."
    else:
        alert_type = "Emergency Alert"
        message = f"EMERGENCY ALERT: {incident_data['title']}. Follow safety instructions. More information at utility.com/emergencies"
    
    # Style the emergency notification preview
    st.markdown(f"""
    <div style="background-color: #ffebee; border: 2px solid #f44336; border-radius: 5px; padding: 15px; font-family: sans-serif;">
    <div style="color: #f44336; font-weight: bold; font-size: 1.2em; display: flex; align-items: center; margin-bottom: 10px;">
    <span style="background-color: #f44336; color: white; padding: 3px 8px; border-radius: 3px; margin-right: 10px;">{alert_type}</span>
    <span>{datetime.datetime.now().strftime('%m/%d/%Y %H:%M')}</span>
    </div>
    <div style="font-size: 1.1em; margin-bottom: 15px;">
    {message}
    </div>
    <div style="display: flex; justify-content: space-between;">
    <button style="background-color: #f44336; color: white; border: none; padding: 8px 15px; border-radius: 5px; cursor: pointer;">Get More Info</button>
    <button style="background-color: #9e9e9e; color: white; border: none; padding: 8px 15px; border-radius: 5px; cursor: pointer;">Acknowledge</button>
    </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Distribution details
    st.caption(f"This alert would be distributed via: SMS, Email, Mobile App Push Notification, Public Alert System")