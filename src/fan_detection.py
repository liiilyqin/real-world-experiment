import pandas as pd
import numpy as np
import os
from datetime import datetime, timedelta

class FanDetector:
    def __init__(self):
        self.thresholds = {
            'temp_max_change': 0.4,    # Maximum temperature change (°C/min)
            'humid_max_change': 2.0,    # Maximum humidity change (%/min)
        }
        self.window_size = '30min'     # Define window size
    
    def analyze_window(self, window_data):
        """Analyze a 30-minute window of temperature and humidity data"""
        # Ensure data is within 30-minute window
        window_data = window_data.copy()
        window_data['timestamp'] = pd.to_datetime(window_data['timestamp'])
        window_start = window_data['timestamp'].min()
        window_end = window_start + pd.Timedelta(self.window_size)
        window_data = window_data[
            (window_data['timestamp'] >= window_start) & 
            (window_data['timestamp'] < window_end)
        ]
        
        # Calculate rate of change per minute
        temp_changes = window_data['temperature'].diff() 
        humid_changes = window_data['humidity'].diff()
        
        # Simple peak detection
        temp_peak = temp_changes.abs().max() > self.thresholds['temp_max_change']
        humid_peak = humid_changes.abs().max() > self.thresholds['humid_max_change']
        
        # Malfunction if either temperature or humidity shows a peak
        fan_detect = temp_peak or humid_peak
        
        
        return fan_detect