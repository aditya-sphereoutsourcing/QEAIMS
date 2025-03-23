import pandas as pd
import numpy as np
from datetime import datetime, timedelta

def get_latest_data():
    """
    Generate latest data for the utilities monitoring system.
    This simulates real-time data from sensors across different utility systems.
    """
    # Generate current timestamp
    now = datetime.now()
    
    # Generate realistic values with some randomness to simulate real data
    # Electricity data
    electricity = {
        'load': 450 + np.random.normal(0, 15),  # MW with some variation
        'voltage': 230 + np.random.normal(0, 2),  # V
        'frequency': 50 + np.random.normal(0, 0.1),  # Hz
        'health_score': 95 + np.random.normal(0, 3),  # %
        'load_change': np.random.normal(0, 5)  # MW change
    }
    
    # Water data
    water = {
        'flow': 1200 + np.random.normal(0, 50),  # kL/h
        'pressure': 5 + np.random.normal(0, 0.2),  # bar
        'quality': 98 + np.random.normal(0, 1),  # %
        'health_score': 93 + np.random.normal(0, 3),  # %
        'flow_change': np.random.normal(0, 20)  # kL/h change
    }
    
    # Sewage data
    sewage = {
        'flow': 900 + np.random.normal(0, 40),  # kL/h
        'treatment_efficiency': 92 + np.random.normal(0, 2),  # %
        'contaminant_level': 5 + np.random.normal(0, 1),  # ppm
        'health_score': 90 + np.random.normal(0, 4),  # %
        'flow_change': np.random.normal(0, 15)  # kL/h change
    }
    
    # Banking data
    banking = {
        'transactions': 2500 + np.random.normal(0, 100),  # transactions per second
        'response_time': 0.2 + np.random.normal(0, 0.05),  # seconds
        'success_rate': 99.5 + np.random.normal(0, 0.3),  # %
        'health_score': 97 + np.random.normal(0, 2),  # %
        'transaction_change': np.random.normal(0, 50)  # tps change
    }
    
    # Combine data
    latest_data = {
        'timestamp': now,
        'electricity': electricity,
        'water': water,
        'sewage': sewage,
        'banking': banking
    }
    
    return latest_data

def get_historical_data(hours=24, interval_minutes=15):
    """
    Generate historical data for the utilities monitoring system.
    
    Args:
        hours (int): Number of hours of historical data to generate
        interval_minutes (int): Interval between data points in minutes
        
    Returns:
        dict: Historical data for all utility systems
    """
    # Calculate number of data points
    data_points = int((hours * 60) / interval_minutes)
    
    # Generate timestamps
    now = datetime.now()
    start_time = now - timedelta(hours=hours)
    timestamps = [start_time + timedelta(minutes=i*interval_minutes) for i in range(data_points)]
    
    # Create base patterns with daily cycles
    hours_of_day = [(t.hour + t.minute/60) for t in timestamps]
    
    # Electricity load follows typical daily pattern with peak in evening
    electricity_base = [300 + 150 * np.sin((h - 18) * np.pi / 12) for h in hours_of_day]
    
    # Water follows morning and evening peaks
    water_base = [1000 + 300 * (np.sin((h - 8) * np.pi / 12) + np.sin((h - 20) * np.pi / 12)) for h in hours_of_day]
    
    # Sewage follows water with delay
    sewage_base = [800 + 250 * (np.sin((h - 9) * np.pi / 12) + np.sin((h - 21) * np.pi / 12)) for h in hours_of_day]
    
    # Banking transactions follow business hours
    banking_base = [1500 + 1500 * np.sin((h - 13) * np.pi / 8) if 8 <= h <= 20 else 500 for h in hours_of_day]
    
    # Add noise and anomalies
    electricity_load = []
    electricity_anomaly = []
    water_flow = []
    water_anomaly = []
    sewage_flow = []
    sewage_anomaly = []
    banking_transactions = []
    banking_anomaly = []
    
    # Create health scores that generally follow the main metrics but can vary independently
    electricity_health = []
    water_health = []
    sewage_health = []
    banking_health = []
    
    # Generate random anomaly points
    # For simplicity, we'll create a few random anomalies
    anomaly_points = np.random.choice(range(data_points), size=5, replace=False)
    
    for i in range(data_points):
        # Add normal variation
        elec_noise = np.random.normal(0, 20)
        water_noise = np.random.normal(0, 50)
        sewage_noise = np.random.normal(0, 40)
        banking_noise = np.random.normal(0, 100)
        
        # Check if this is an anomaly point
        is_elec_anomaly = i in anomaly_points[:1]  # First anomaly for electricity
        is_water_anomaly = i in anomaly_points[1:3]  # Next two for water
        is_sewage_anomaly = i in anomaly_points[3:4]  # One for sewage
        is_banking_anomaly = i in anomaly_points[4:5]  # One for banking
        
        # Add anomaly if needed
        elec_anomaly_value = np.random.normal(100, 20) if is_elec_anomaly else 0
        water_anomaly_value = np.random.normal(200, 50) if is_water_anomaly else 0
        sewage_anomaly_value = np.random.normal(150, 30) if is_sewage_anomaly else 0
        banking_anomaly_value = np.random.normal(-500, 100) if is_banking_anomaly else 0
        
        # Calculate final values
        elec_value = electricity_base[i] + elec_noise + elec_anomaly_value
        water_value = water_base[i] + water_noise + water_anomaly_value
        sewage_value = sewage_base[i] + sewage_noise + sewage_anomaly_value
        banking_value = banking_base[i] + banking_noise + banking_anomaly_value
        
        # Make sure values are realistic (especially for health scores)
        elec_value = max(50, min(elec_value, 800))
        water_value = max(500, min(water_value, 2000))
        sewage_value = max(400, min(sewage_value, 1500))
        banking_value = max(100, min(banking_value, 4000))
        
        # Calculate health scores (inversely affected by anomalies)
        elec_health = 95 - (abs(elec_anomaly_value) / 10) + np.random.normal(0, 2)
        water_health_value = 93 - (abs(water_anomaly_value) / 20) + np.random.normal(0, 2)
        sewage_health_value = 90 - (abs(sewage_anomaly_value) / 15) + np.random.normal(0, 2)
        banking_health_value = 97 - (abs(banking_anomaly_value) / 50) + np.random.normal(0, 2)
        
        # Ensure health scores are between 0 and 100
        elec_health = max(0, min(elec_health, 100))
        water_health_value = max(0, min(water_health_value, 100))
        sewage_health_value = max(0, min(sewage_health_value, 100))
        banking_health_value = max(0, min(banking_health_value, 100))
        
        # Append values and anomaly flags
        electricity_load.append(elec_value)
        electricity_anomaly.append(is_elec_anomaly)
        water_flow.append(water_value)
        water_anomaly.append(is_water_anomaly)
        sewage_flow.append(sewage_value)
        sewage_anomaly.append(is_sewage_anomaly)
        banking_transactions.append(banking_value)
        banking_anomaly.append(is_banking_anomaly)
        
        # Append health scores
        electricity_health.append(elec_health)
        water_health.append(water_health_value)
        sewage_health.append(sewage_health_value)
        banking_health.append(banking_health_value)
    
    # Create historical data structure
    historical_data = {
        'timestamp': timestamps,
        'electricity': {
            'load': electricity_load,
            'anomaly': electricity_anomaly,
            'health_score': electricity_health
        },
        'water': {
            'flow': water_flow,
            'anomaly': water_anomaly,
            'health_score': water_health
        },
        'sewage': {
            'flow': sewage_flow,
            'anomaly': sewage_anomaly,
            'health_score': sewage_health
        },
        'banking': {
            'transactions': banking_transactions,
            'anomaly': banking_anomaly,
            'health_score': banking_health
        }
    }
    
    return historical_data

def get_detailed_data(system, hours=24):
    """
    Generate more detailed data for a specific utility system.
    
    Args:
        system (str): The utility system to generate data for ('electricity', 'water', 'sewage', 'banking')
        hours (int): Number of hours of historical data to generate
        
    Returns:
        pd.DataFrame: Detailed data for the specified system
    """
    # Get base historical data
    historical = get_historical_data(hours=hours)
    timestamps = historical['timestamp']
    
    if system == 'electricity':
        # Generate additional electricity metrics
        data = {
            'timestamp': timestamps,
            'load_mw': historical['electricity']['load'],
            'voltage': [230 + np.random.normal(0, 2) for _ in range(len(timestamps))],
            'frequency': [50 + np.random.normal(0, 0.1) for _ in range(len(timestamps))],
            'power_factor': [0.95 + np.random.normal(0, 0.02) for _ in range(len(timestamps))],
            'grid_stability': [95 + np.random.normal(0, 3) for _ in range(len(timestamps))],
            'anomaly': historical['electricity']['anomaly'],
            'health_score': historical['electricity']['health_score']
        }
    
    elif system == 'water':
        # Generate additional water metrics
        data = {
            'timestamp': timestamps,
            'flow_kl_h': historical['water']['flow'],
            'pressure_bar': [5 + np.random.normal(0, 0.2) for _ in range(len(timestamps))],
            'turbidity_ntu': [0.5 + np.random.normal(0, 0.1) for _ in range(len(timestamps))],
            'ph_level': [7.2 + np.random.normal(0, 0.2) for _ in range(len(timestamps))],
            'chlorine_ppm': [1.2 + np.random.normal(0, 0.1) for _ in range(len(timestamps))],
            'anomaly': historical['water']['anomaly'],
            'health_score': historical['water']['health_score']
        }
    
    elif system == 'sewage':
        # Generate additional sewage metrics
        data = {
            'timestamp': timestamps,
            'flow_kl_h': historical['sewage']['flow'],
            'treatment_efficiency': [92 + np.random.normal(0, 2) for _ in range(len(timestamps))],
            'contaminant_level': [5 + np.random.normal(0, 1) for _ in range(len(timestamps))],
            'dissolved_oxygen': [6.5 + np.random.normal(0, 0.5) for _ in range(len(timestamps))],
            'methane_level': [2.5 + np.random.normal(0, 0.3) for _ in range(len(timestamps))],
            'anomaly': historical['sewage']['anomaly'],
            'health_score': historical['sewage']['health_score']
        }
    
    elif system == 'banking':
        # Generate additional banking metrics
        data = {
            'timestamp': timestamps,
            'transactions_per_second': historical['banking']['transactions'],
            'response_time_ms': [200 + np.random.normal(0, 20) for _ in range(len(timestamps))],
            'success_rate': [99.5 + np.random.normal(0, 0.3) for _ in range(len(timestamps))],
            'error_rate': [0.5 + np.random.normal(0, 0.3) for _ in range(len(timestamps))],
            'security_index': [98 + np.random.normal(0, 1) for _ in range(len(timestamps))],
            'anomaly': historical['banking']['anomaly'],
            'health_score': historical['banking']['health_score']
        }
    
    else:
        # Default case with basic data
        data = {
            'timestamp': timestamps,
            'value': [np.random.normal(100, 10) for _ in range(len(timestamps))],
            'anomaly': [False for _ in range(len(timestamps))],
            'health_score': [90 + np.random.normal(0, 3) for _ in range(len(timestamps))]
        }
    
    return pd.DataFrame(data)

def get_fault_simulation_data():
    """
    Generate data for fault simulation scenarios.
    
    Returns:
        dict: Data for different fault simulation scenarios
    """
    # Create baseline normal data
    normal_data = {
        'electricity': {
            'load': 450,
            'voltage': 230,
            'frequency': 50,
            'health_score': 95
        },
        'water': {
            'flow': 1200,
            'pressure': 5,
            'quality': 98,
            'health_score': 93
        },
        'sewage': {
            'flow': 900,
            'treatment_efficiency': 92,
            'contaminant_level': 5,
            'health_score': 90
        },
        'banking': {
            'transactions': 2500,
            'response_time': 0.2,
            'success_rate': 99.5,
            'health_score': 97
        }
    }
    
    # Define fault scenarios
    fault_scenarios = {
        'power_outage': {
            'description': 'Simulates a power outage affecting the electricity grid',
            'affected_systems': ['electricity', 'water', 'banking'],
            'recovery_time': '15 minutes',
            'data': {
                'electricity': {
                    'load': 0,
                    'voltage': 0,
                    'frequency': 0,
                    'health_score': 0
                },
                'water': {
                    'flow': 800,  # Reduced flow due to backup generators
                    'pressure': 3.5,
                    'quality': 92,
                    'health_score': 70
                },
                'sewage': {
                    'flow': 850,  # Slightly affected
                    'treatment_efficiency': 85,
                    'contaminant_level': 8,
                    'health_score': 80
                },
                'banking': {
                    'transactions': 500,  # Significantly reduced capacity
                    'response_time': 0.8,
                    'success_rate': 85.0,
                    'health_score': 60
                }
            }
        },
        'water_main_break': {
            'description': 'Simulates a major water main break',
            'affected_systems': ['water', 'sewage'],
            'recovery_time': '4 hours',
            'data': {
                'electricity': {
                    'load': 470,  # Slight increase due to emergency pumps
                    'voltage': 228,
                    'frequency': 49.8,
                    'health_score': 92
                },
                'water': {
                    'flow': 400,  # Significantly reduced flow
                    'pressure': 2.0,
                    'quality': 85,
                    'health_score': 40
                },
                'sewage': {
                    'flow': 700,  # Reduced flow in sewage system
                    'treatment_efficiency': 88,
                    'contaminant_level': 7,
                    'health_score': 75
                },
                'banking': {
                    'transactions': 2450,  # Nearly unaffected
                    'response_time': 0.21,
                    'success_rate': 99.3,
                    'health_score': 96
                }
            }
        },
        'cyber_attack': {
            'description': 'Simulates a coordinated cyber attack on banking and electricity systems',
            'affected_systems': ['banking', 'electricity'],
            'recovery_time': '2 hours',
            'data': {
                'electricity': {
                    'load': 430,  # Slightly affected
                    'voltage': 225,
                    'frequency': 49.5,
                    'health_score': 75
                },
                'water': {
                    'flow': 1150,  # Slightly affected
                    'pressure': 4.9,
                    'quality': 97,
                    'health_score': 91
                },
                'sewage': {
                    'flow': 890,  # Nearly unaffected
                    'treatment_efficiency': 91,
                    'contaminant_level': 5.2,
                    'health_score': 89
                },
                'banking': {
                    'transactions': 500,  # Significantly reduced
                    'response_time': 1.5,
                    'success_rate': 70.0,
                    'health_score': 30
                }
            }
        },
        'sewage_system_overflow': {
            'description': 'Simulates a sewage system overflow after heavy rainfall',
            'affected_systems': ['sewage', 'water'],
            'recovery_time': '8 hours',
            'data': {
                'electricity': {
                    'load': 460,  # Slight increase due to emergency systems
                    'voltage': 229,
                    'frequency': 50.1,
                    'health_score': 94
                },
                'water': {
                    'flow': 1100,  # Reduced to prevent contamination
                    'pressure': 4.8,
                    'quality': 85,
                    'health_score': 75
                },
                'sewage': {
                    'flow': 1500,  # Significantly increased flow
                    'treatment_efficiency': 70,
                    'contaminant_level': 15,
                    'health_score': 35
                },
                'banking': {
                    'transactions': 2480,  # Nearly unaffected
                    'response_time': 0.2,
                    'success_rate': 99.4,
                    'health_score': 97
                }
            }
        }
    }
    
    return {
        'normal': normal_data,
        'scenarios': fault_scenarios
    }
