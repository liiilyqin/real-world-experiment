import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os
import numpy as np
from scipy import stats

def calculate_window_rates(df, sensor, window_size=30):
    """Calculate rate of change for sensor using fixed number of rows"""
    # Calculate number of complete windows
    n_windows = len(df) // window_size
    
    # Initialize list to store window data
    window_data_list = []
    
    for i in range(n_windows):
        start_idx = i * window_size
        end_idx = start_idx + window_size
        window_data = df.iloc[start_idx:end_idx]
        
        # Calculate window statistics
        window_stats = {
            'start_time': window_data['timestamp'].iloc[0],
            'end_time': window_data['timestamp'].iloc[-1],
            'mean_value': window_data[sensor].mean(),
            'start_ms': window_data['timestamp_ms'].iloc[0],
            'end_ms': window_data['timestamp_ms'].iloc[-1],
            'time_span_ms': window_data['timestamp_ms'].iloc[-1] - window_data['timestamp_ms'].iloc[0],
            'total_change': window_data[sensor].iloc[-1] - window_data[sensor].iloc[0],
        }
        window_data_list.append(window_stats)
    
    # Create DataFrame from list of dictionaries
    window_rates = pd.DataFrame(window_data_list)
    
    # Calculate rate
    window_rates['rate'] = window_rates['total_change'] / (window_rates['time_span_ms'] / 1000)
    
    return window_rates

def analyze_window_stats(window_rates, title):
    """Calculate statistics for window-based rates"""
    stats_dict = {
        'mean_rate': window_rates['rate'].mean(),
        'median_rate': window_rates['rate'].median(),
        'std_rate': window_rates['rate'].std(),
        'max_increase': window_rates['rate'].max(),
        'max_decrease': window_rates['rate'].min(),
        'positive_windows': (window_rates['rate'] > 0).sum(),
        'negative_windows': (window_rates['rate'] < 0).sum()
    }
    
    print(f"\n{title} 30-Minute Window Statistics:")
    for key, value in stats_dict.items():
        print(f"{key}: {value:.4f}")
    
    return stats_dict

def plot_window_comparison(worm_windows, withoutworm_windows, sensor, export_dir):
    """Create comparison plots for window-based rates"""
    fig, (ax1, ax2, ax3) = plt.subplots(3, 1, figsize=(15, 15))
    
    # Time series of rates
    ax1.plot(worm_windows['start_time'], worm_windows['rate'], 
             label='With Worm', color='blue', marker='o')
    ax1.plot(withoutworm_windows['start_time'], withoutworm_windows['rate'], 
             label='Without Worm', color='red', marker='o')
    ax1.set_title(f'{sensor} Rate of Change Over Time (30-min windows)')
    ax1.set_xlabel('Window Start Time')
    ax1.set_ylabel('Rate of Change per Second')
    ax1.grid(True)
    ax1.legend()
    
    # Rate distribution
    sns.kdeplot(data=worm_windows['rate'], ax=ax2, label='With Worm', color='blue')
    sns.kdeplot(data=withoutworm_windows['rate'], ax=ax2, label='Without Worm', color='red')
    ax2.set_title(f'{sensor} Rate Distribution (30-min windows)')
    ax2.set_xlabel('Rate of Change per Second')
    ax2.grid(True)
    ax2.legend()
    
    # Box plot
    box_data = [worm_windows['rate'], withoutworm_windows['rate']]
    ax3.boxplot(box_data, labels=['With Worm', 'Without Worm'])
    ax3.set_title(f'{sensor} Rate Comparison (30-min windows)')
    ax3.set_ylabel('Rate of Change per Second')
    ax3.grid(True)
    
    plt.tight_layout()
    plt.savefig(os.path.join(export_dir, f'{sensor}_window_analysis.png'))
    plt.close()

def main():
    export_dir = "exports"
    sensors = ['co2', 'temperature', 'humidity']
    
    # Read data
    worm_df = pd.read_csv(os.path.join(export_dir, 'worm_cleaned.csv'))
    withoutworm_df = pd.read_csv(os.path.join(export_dir, 'withoutworm_cleaned.csv'))
    
    # Analyze each sensor
    for sensor in sensors:
        print(f"\n{'='*50}")
        print(f"Analyzing {sensor.upper()} (30-row windows)")
        print(f"{'='*50}")
        
        # Calculate window-based rates
        worm_windows = calculate_window_rates(worm_df, sensor)
        withoutworm_windows = calculate_window_rates(withoutworm_df, sensor)
        
        # Analyze window statistics
        worm_stats = analyze_window_stats(worm_windows, f"{sensor} With Worm")
        withoutworm_stats = analyze_window_stats(withoutworm_windows, f"{sensor} Without Worm")
        
        # Perform statistical test on window rates
        t_stat, p_value = stats.ttest_ind(
            worm_windows['rate'].dropna(),
            withoutworm_windows['rate'].dropna()
        )
        
        print(f"\n30-Minute Window Statistical Test Results:")
        print(f"t-statistic: {t_stat:.4f}")
        print(f"p-value: {p_value:.4f}")
        
        # Create visualization
        plot_window_comparison(worm_windows, withoutworm_windows, sensor, export_dir)
        print(f"Created window analysis plot: {sensor}_window_analysis.png")

if __name__ == "__main__":
    main()