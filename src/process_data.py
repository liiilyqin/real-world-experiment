import pandas as pd
import numpy as np
from scipy.stats import median_abs_deviation
import os

def hampel_filter(series, window_size=10, n_sigmas=3):
    """Apply Hampel filter for outlier detection and removal"""
    rolling_median = series.rolling(window=window_size, center=True).median()
    mad = median_abs_deviation(series, nan_policy='omit')
    threshold = n_sigmas * mad
    difference = np.abs(series - rolling_median)
    
    return np.where(difference > threshold, rolling_median, series)

def process_data(input_file):
    """Process single file with Hampel filter and percentile clipping"""
    # Read data
    df = pd.read_csv(input_file)
    df['timestamp'] = pd.to_datetime(df['timestamp'])
    
    # Process each sensor column
    for col in ['co2', 'temperature', 'humidity']:
        # Apply Hampel filter
        df[col] = hampel_filter(df[col])
        
        # Apply percentile clipping
        upper = np.percentile(df[col], 99.5)
        lower = np.percentile(df[col], 0.5)
        df[col] = df[col].clip(lower, upper)
    
    return df[['timestamp', 'timestamp_ms', 'co2', 'temperature', 'humidity']]

def main():
    export_dir = "exports"
    
    # Process both conditions
    for condition in ['worm', 'withoutworm']:
        input_file = os.path.join(export_dir, f'{condition}_merged_all.csv')
        output_file = os.path.join(export_dir, f'{condition}_cleaned.csv')
        
        # Process and save
        cleaned_df = process_data(input_file)
        cleaned_df.to_csv(output_file, index=False)
        print(f"Saved cleaned data to: {output_file}")

if __name__ == "__main__":
    main()