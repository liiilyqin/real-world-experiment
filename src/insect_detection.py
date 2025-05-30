import pandas as pd
import numpy as np
from scipy import stats
import matplotlib.pyplot as plt
import os
from datetime import datetime

class InsectDetector:
    def __init__(self):
        # Thresholds based on light infestation experiment (0.4%~0.5% mealworms)
        self.thresholds = {
            'mean_level': 550,    # Base CO2 threshold
            'std_change': 0.25,   # Standard deviation threshold
            'min_change': 0.1,    # Minimum change threshold
            'peak_change': 1.0    # Peak change threshold
        }
    
    def analyze_window(self, window_data):
        """Analyze a 30-minute window of CO2 data"""
        # Calculate CO2 statistics
        mean_level = window_data['co2'].mean()
        changes = window_data['co2'].diff() / (window_data['timestamp_ms'].diff() / 1000)
        std_change = changes.std()
        max_change = changes.max()
        min_change = changes.abs().min()
        
        # Multiple detection criteria for CO2
        level_detected = mean_level > self.thresholds['mean_level']
        std_detected = std_change > self.thresholds['std_change']
        change_detected = (max_change > self.thresholds['peak_change'] or 
                         min_change > self.thresholds['min_change'])
        
        # Calculate detection score (weighted combination)
        score = (level_detected * 0.5 +    # Higher weight for mean level
                std_detected * 0.3 +       # Medium weight for variation
                change_detected * 0.2)      # Lower weight for peaks
        
        # Detection threshold lowered for better recall
        detection = score > 0.4
        
        results = {
            'mean_level': mean_level,
            'std_change': std_change,
            'max_change': max_change,
            'min_change': min_change,
            'score': score
        }
        
        return detection, results

def evaluate_detector(detector, worm_df, withoutworm_df, window_size='30min'):
    """Evaluate detector performance"""
    # Process data in 30-minute windows
    true_positives = 0
    false_positives = 0
    true_negatives = 0
    false_negatives = 0
    
    # Evaluate worm data (should detect insects)
    for start in pd.date_range(worm_df['timestamp'].min(), 
                             worm_df['timestamp'].max(), 
                             freq=window_size):
        end = start + pd.Timedelta(window_size)
        window = worm_df[(worm_df['timestamp'] >= start) & 
                        (worm_df['timestamp'] < end)]
        
        if len(window) > 0:
            detection, _ = detector.analyze_window(window)
            if detection:
                true_positives += 1
            else:
                false_negatives += 1
    
    # Evaluate without-worm data (should not detect insects)
    for start in pd.date_range(withoutworm_df['timestamp'].min(), 
                             withoutworm_df['timestamp'].max(), 
                             freq=window_size):
        end = start + pd.Timedelta(window_size)
        window = withoutworm_df[(withoutworm_df['timestamp'] >= start) & 
                               (withoutworm_df['timestamp'] < end)]
        
        if len(window) > 0:
            detection, _ = detector.analyze_window(window)
            if detection:
                false_positives += 1
            else:
                true_negatives += 1
    
    # Calculate metrics
    total = true_positives + false_positives + true_negatives + false_negatives
    accuracy = (true_positives + true_negatives) / total
    precision = true_positives / (true_positives + false_positives)
    recall = true_positives / (true_positives + false_negatives)
    f1_score = 2 * (precision * recall) / (precision + recall)
    
    return {
        'accuracy': accuracy,
        'precision': precision,
        'recall': recall,
        'f1_score': f1_score,
        'confusion_matrix': {
            'true_positives': true_positives,
            'false_positives': false_positives,
            'true_negatives': true_negatives,
            'false_negatives': false_negatives
        }
    }

def main():
    export_dir = "exports"
    
    # Load data
    worm_df = pd.read_csv(os.path.join(export_dir, 'worm_cleaned.csv'))
    withoutworm_df = pd.read_csv(os.path.join(export_dir, 'withoutworm_cleaned.csv'))
    
    # Convert timestamps
    for df in [worm_df, withoutworm_df]:
        df['timestamp'] = pd.to_datetime(df['timestamp'])
    
    # Initialize and evaluate detector
    detector = InsectDetector()
    metrics = evaluate_detector(detector, worm_df, withoutworm_df)
    
    # Print results
    print("\nInsect Detection Performance Metrics:")
    print(f"Accuracy: {metrics['accuracy']:.4f}")
    print(f"Precision: {metrics['precision']:.4f}")
    print(f"Recall: {metrics['recall']:.4f}")
    print(f"F1 Score: {metrics['f1_score']:.4f}")
    
    print("\nConfusion Matrix:")
    print(f"True Positives: {metrics['confusion_matrix']['true_positives']}")
    print(f"False Positives: {metrics['confusion_matrix']['false_positives']}")
    print(f"True Negatives: {metrics['confusion_matrix']['true_negatives']}")
    print(f"False Negatives: {metrics['confusion_matrix']['false_negatives']}")

if __name__ == "__main__":
    main()