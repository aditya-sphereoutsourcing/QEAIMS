import numpy as np
from sklearn.ensemble import IsolationForest
import pandas as pd

def get_anomaly_status(system, latest_data):
    """
    Determine if the current system state is anomalous.
    
    Args:
        system (str): The system to check ('electricity', 'water', 'sewage', 'banking')
        latest_data (dict): Dictionary containing the latest data from all systems
        
    Returns:
        str: 'Normal' or 'Anomaly Detected'
    """
    # Extract system-specific data from latest_data
    system_data = latest_data.get(system, {})
    
    # Define thresholds for each system
    thresholds = {
        'electricity': {
            'load': (350, 550),  # Min and max acceptable load in MW
            'health_score': 80   # Minimum acceptable health score
        },
        'water': {
            'flow': (900, 1500), # Min and max acceptable flow in kL/h
            'health_score': 75   # Minimum acceptable health score
        },
        'sewage': {
            'flow': (700, 1200), # Min and max acceptable flow in kL/h
            'health_score': 70   # Minimum acceptable health score
        },
        'banking': {
            'transactions': (1500, 3500),  # Min and max transactions per second
            'health_score': 85   # Minimum acceptable health score
        }
    }
    
    # Get thresholds for the specific system
    system_thresholds = thresholds.get(system, {})
    
    # Check if system exists in our data
    if not system_data or not system_thresholds:
        return "Unknown"
    
    # Check main metric for each system
    if system == 'electricity':
        load = system_data.get('load', 0)
        if load < system_thresholds['load'][0] or load > system_thresholds['load'][1]:
            return "Anomaly Detected"
    
    elif system == 'water':
        flow = system_data.get('flow', 0)
        if flow < system_thresholds['flow'][0] or flow > system_thresholds['flow'][1]:
            return "Anomaly Detected"
    
    elif system == 'sewage':
        flow = system_data.get('flow', 0)
        if flow < system_thresholds['flow'][0] or flow > system_thresholds['flow'][1]:
            return "Anomaly Detected"
    
    elif system == 'banking':
        transactions = system_data.get('transactions', 0)
        if transactions < system_thresholds['transactions'][0] or transactions > system_thresholds['transactions'][1]:
            return "Anomaly Detected"
    
    # Check health score for all systems
    health_score = system_data.get('health_score', 0)
    if health_score < system_thresholds.get('health_score', 0):
        return "Anomaly Detected"
    
    # If we passed all checks, the system is normal
    return "Normal"

def detect_anomalies(data, columns=None, contamination=0.05):
    """
    Detect anomalies in the provided data using Isolation Forest algorithm.
    
    Args:
        data (pd.DataFrame): DataFrame containing the data to analyze
        columns (list): List of column names to use for anomaly detection
        contamination (float): Expected proportion of anomalies in the data
        
    Returns:
        pd.Series: Boolean series indicating anomalies (True for anomalies)
    """
    if not isinstance(data, pd.DataFrame):
        raise ValueError("Input data must be a pandas DataFrame")
    
    # If columns not specified, use all numeric columns
    if columns is None:
        columns = data.select_dtypes(include=np.number).columns.tolist()
    
    # Make sure we have data to work with
    if len(columns) == 0 or data.empty:
        return pd.Series([False] * len(data))
    
    # Create and fit the model
    model = IsolationForest(contamination=contamination, random_state=42)
    
    # Predict anomalies
    predictions = model.fit_predict(data[columns])
    
    # Convert predictions to boolean (Isolation Forest returns -1 for anomalies, 1 for normal)
    return pd.Series(predictions == -1, index=data.index)

def analyze_system_health(data, system):
    """
    Analyze system health and identify potential issues.
    
    Args:
        data (pd.DataFrame): DataFrame containing system-specific data
        system (str): System name ('electricity', 'water', 'sewage', 'banking')
        
    Returns:
        dict: Analysis results including health status and recommendations
    """
    # Define key metrics for each system
    metrics = {
        'electricity': ['load_mw', 'voltage', 'frequency', 'power_factor'],
        'water': ['flow_kl_h', 'pressure_bar', 'turbidity_ntu', 'ph_level'],
        'sewage': ['flow_kl_h', 'treatment_efficiency', 'contaminant_level', 'dissolved_oxygen'],
        'banking': ['transactions_per_second', 'response_time_ms', 'success_rate', 'error_rate']
    }
    
    # Get relevant metrics for the system
    system_metrics = metrics.get(system, [])
    
    # Check if we have the required data
    if not all(metric in data.columns for metric in system_metrics):
        return {
            'status': 'Unknown',
            'issues': ['Insufficient data for analysis'],
            'recommendations': ['Ensure all required sensors are operational']
        }
    
    # Run anomaly detection on the data
    anomalies = detect_anomalies(data, columns=system_metrics)
    
    # Calculate summary statistics
    anomaly_rate = anomalies.mean()
    health_score = data.get('health_score', pd.Series([0] * len(data))).mean()
    
    # Define health status
    if health_score >= 90:
        status = 'Excellent'
    elif health_score >= 80:
        status = 'Good'
    elif health_score >= 70:
        status = 'Fair'
    elif health_score >= 60:
        status = 'Concerning'
    else:
        status = 'Critical'
    
    # Identify specific issues
    issues = []
    
    # System-specific checks
    if system == 'electricity':
        if data['frequency'].mean() < 49.5 or data['frequency'].mean() > 50.5:
            issues.append('Frequency instability detected')
        if data['voltage'].mean() < 220 or data['voltage'].mean() > 240:
            issues.append('Voltage outside acceptable range')
        if data['power_factor'].mean() < 0.9:
            issues.append('Low power factor')
    
    elif system == 'water':
        if data['pressure_bar'].mean() < 4.5:
            issues.append('Low water pressure')
        if data['turbidity_ntu'].mean() > 1.0:
            issues.append('High water turbidity')
        if data['ph_level'].mean() < 6.5 or data['ph_level'].mean() > 8.5:
            issues.append('pH level outside acceptable range')
    
    elif system == 'sewage':
        if data['treatment_efficiency'].mean() < 85:
            issues.append('Treatment efficiency below target')
        if data['contaminant_level'].mean() > 10:
            issues.append('High contaminant levels')
        if data['dissolved_oxygen'].mean() < 5:
            issues.append('Low dissolved oxygen levels')
    
    elif system == 'banking':
        if data['response_time_ms'].mean() > 300:
            issues.append('High response times')
        if data['success_rate'].mean() < 99:
            issues.append('Transaction success rate below target')
        if data['error_rate'].mean() > 1:
            issues.append('High error rate')
    
    # Add general issues based on anomaly detection
    if anomaly_rate > 0.1:
        issues.append(f'High rate of anomalies detected ({anomaly_rate*100:.1f}%)')
    
    # If no specific issues found, note that
    if not issues:
        issues.append('No specific issues detected')
    
    # Generate recommendations
    recommendations = []
    
    # System-specific recommendations
    if system == 'electricity':
        if 'Frequency instability detected' in issues:
            recommendations.append('Check grid balancing systems')
        if 'Voltage outside acceptable range' in issues:
            recommendations.append('Inspect voltage regulators and transformers')
        if 'Low power factor' in issues:
            recommendations.append('Consider installing power factor correction capacitors')
    
    elif system == 'water':
        if 'Low water pressure' in issues:
            recommendations.append('Check pump operations and inspect for leaks')
        if 'High water turbidity' in issues:
            recommendations.append('Optimize filtration systems')
        if 'pH level outside acceptable range' in issues:
            recommendations.append('Adjust chemical treatment processes')
    
    elif system == 'sewage':
        if 'Treatment efficiency below target' in issues:
            recommendations.append('Review treatment process and chemical dosing')
        if 'High contaminant levels' in issues:
            recommendations.append('Investigate potential industrial discharge events')
        if 'Low dissolved oxygen levels' in issues:
            recommendations.append('Check aeration systems')
    
    elif system == 'banking':
        if 'High response times' in issues:
            recommendations.append('Optimize database queries and increase server capacity')
        if 'Transaction success rate below target' in issues:
            recommendations.append('Investigate failed transactions and implement retry mechanisms')
        if 'High error rate' in issues:
            recommendations.append('Review error logs and address common failure points')
    
    # Add general recommendations based on anomaly detection
    if anomaly_rate > 0.1:
        recommendations.append('Conduct comprehensive system diagnostic')
    
    # If no specific recommendations, add a general one
    if not recommendations:
        recommendations.append('Continue regular monitoring and maintenance')
    
    return {
        'status': status,
        'health_score': health_score,
        'anomaly_rate': anomaly_rate,
        'issues': issues,
        'recommendations': recommendations
    }
