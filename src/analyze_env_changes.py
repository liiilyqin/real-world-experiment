import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os
from datetime import datetime

def analyze_env_changes(df, window_size='30min'):
    """Analyze temperature and humidity changes in 30-minute windows"""
    # Ensure timestamp is datetime
    df['timestamp'] = pd.to_datetime(df['timestamp'])
    
    # Group data into 30-minute windows
    window_stats = []
    for start_time in pd.date_range(df['timestamp'].min(), 
                                  df['timestamp'].max(), 
                                  freq=window_size):
        end_time = start_time + pd.Timedelta(window_size)
        window = df[(df['timestamp'] >= start_time) & 
                   (df['timestamp'] < end_time)]
        
        if len(window) > 0:
            stats = {
                'window_start': start_time,
                'temp_change': window['temperature'].iloc[-1] - window['temperature'].iloc[0],
                'humid_change': window['humidity'].iloc[-1] - window['humidity'].iloc[0],
                'temp_mean': window['temperature'].mean(),
                'humid_mean': window['humidity'].mean()
            }
            window_stats.append(stats)
    
    return pd.DataFrame(window_stats)

def plot_changes(results_df, title, export_dir):
    """Create visualization of temperature and humidity changes"""
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 10))
    
    # Temperature changes plot
    ax1.plot(results_df['window_start'], results_df['temp_change'], 
             marker='o', label='Temperature Change')
    ax1.set_title(f'Temperature Changes ({title})')
    ax1.set_ylabel('Temperature Change (°C)')
    ax1.grid(True)
    
    # Humidity changes plot
    ax2.plot(results_df['window_start'], results_df['humid_change'], 
             marker='o', color='green', label='Humidity Change')
    ax2.set_title(f'Humidity Changes ({title})')
    ax2.set_ylabel('Humidity Change (%)')
    ax2.grid(True)
    
    plt.tight_layout()
    plt.savefig(os.path.join(export_dir, f'env_changes_{title.lower()}.png'))
    plt.close()

def main():
    # Load data
    data_dir = "cleaned_data"
    export_dir = "pic"
    
    # Create export directory if it doesn't exist
    if not os.path.exists(export_dir):
        os.makedirs(export_dir)
    
    worm_df = pd.read_csv(os.path.join(data_dir, 'worm_cleaned.csv'))
    withoutworm_df = pd.read_csv(os.path.join(data_dir, 'withoutworm_cleaned.csv'))
    
    # Analyze both datasets
    worm_results = analyze_env_changes(worm_df)
    noworm_results = analyze_env_changes(withoutworm_df)
    
    # Print summary statistics
    print("=== With Worms ===")
    print(f"Average temperature change: {worm_results['temp_change'].mean():.2f}°C")
    print(f"Average humidity change: {worm_results['humid_change'].mean():.2f}%")
    print(f"Average temperature: {worm_results['temp_mean'].mean():.2f}°C")
    print(f"Average humidity: {worm_results['humid_mean'].mean():.2f}%\n")
    
    print("=== Without Worms ===")
    print(f"Average temperature change: {noworm_results['temp_change'].mean():.2f}°C")
    print(f"Average humidity change: {noworm_results['humid_change'].mean():.2f}%")
    print(f"Average temperature: {noworm_results['temp_mean'].mean():.2f}°C")
    print(f"Average humidity: {noworm_results['humid_mean'].mean():.2f}%")
    
    # Create visualizations 
    plot_changes(worm_results, "With_Worms", export_dir)
    plot_changes(noworm_results, "Without_Worms", export_dir)

if __name__ == "__main__":
    main()