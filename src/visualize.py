import pandas as pd
import matplotlib.pyplot as plt
import os
from datetime import datetime

def load_and_prepare_data(export_dir):
    """Load and prepare both datasets"""
    # Read merged CSV files
    worm_df = pd.read_csv(os.path.join(export_dir, 'worm_cleaned.csv'))
    withoutworm_df = pd.read_csv(os.path.join(export_dir, 'withoutworm_cleaned.csv'))
    
    # Convert timestamp strings to datetime objects
    for df in [worm_df, withoutworm_df]:
        df['timestamp'] = pd.to_datetime(df['timestamp'])
    
    return worm_df, withoutworm_df

def create_comparison_plots(worm_df, withoutworm_df):
    """Create comparison plots for all sensors with average changes"""
    sensors = ['co2', 'temperature', 'humidity']
    # Create 2 rows of subplots: raw data and rate of change
    fig, axes = plt.subplots(3, 2, figsize=(20, 15))
    fig.suptitle('Sensor Data Comparison: With Worm vs Without Worm')
    
    for i, sensor in enumerate(sensors):
        # Left column: Raw data plot
        # Plot both datasets
        axes[i, 0].plot(worm_df['timestamp'], worm_df[sensor], 
                    label='With Worm', color='blue', alpha=0.7)
        axes[i, 0].plot(withoutworm_df['timestamp'], withoutworm_df[sensor], 
                    label='Without Worm', color='red', alpha=0.7)
        
        # Customize raw data plot
        axes[i, 0].set_title(f'{sensor.upper()} Values')
        axes[i, 0].set_xlabel('Time')
        axes[i, 0].set_ylabel(f'{sensor} value')
        axes[i, 0].grid(True)
        axes[i, 0].legend()
        
        # Right column: Rate of change plot
        # Calculate rates of change
        worm_changes = worm_df[sensor].diff() / (worm_df['timestamp_ms'].diff() / 1000)
        withoutworm_changes = withoutworm_df[sensor].diff() / (withoutworm_df['timestamp_ms'].diff() / 1000)
        
        # Calculate rolling average of changes (30-second window)
        window = 30
        worm_avg_changes = worm_changes.rolling(window=window, min_periods=1).mean()
        withoutworm_avg_changes = withoutworm_changes.rolling(window=window, min_periods=1).mean()
        
        # Plot rates of change
        axes[i, 1].plot(worm_df['timestamp'], worm_avg_changes,
                    label='With Worm (30s avg)', color='blue', alpha=0.7)
        axes[i, 1].plot(withoutworm_df['timestamp'], withoutworm_avg_changes,
                    label='Without Worm (30s avg)', color='red', alpha=0.7)
        
        # Add horizontal line at zero for reference
        axes[i, 1].axhline(y=0, color='gray', linestyle='--', alpha=0.5)
        
        # Customize rate of change plot
        axes[i, 1].set_title(f'{sensor.upper()} Rate of Change')
        axes[i, 1].set_xlabel('Time')
        axes[i, 1].set_ylabel(f'Change per second')
        axes[i, 1].grid(True)
        axes[i, 1].legend()
        
        # Rotate x-axis labels for both plots
        for ax in axes[i]:
            plt.setp(ax.xaxis.get_majorticklabels(), rotation=45)
    
    plt.tight_layout()
    return fig

def calculate_changes(df, sensor):
    """Calculate average changes for a sensor"""
    # Calculate changes between consecutive readings
    changes = df[sensor].diff()
    time_diff = df['timestamp_ms'].diff() / 1000  # Convert to seconds
    
    # Calculate rates of change (per second)
    rates = changes / time_diff
    
    stats = {
        'avg_change_per_second': rates.mean(),
        'std_change': rates.std(),
        'max_increase': rates.max(),
        'max_decrease': rates.min(),
        'positive_changes': (rates > 0).sum(),
        'negative_changes': (rates < 0).sum()
    }
    return stats

def main():
    export_dir = "exports"
    
    # Load data
    print("Loading data...")
    worm_df, withoutworm_df = load_and_prepare_data(export_dir)
    
    # Create plots
    print("Creating plots...")
    fig = create_comparison_plots(worm_df, withoutworm_df)
    
    # Save plot
    output_path = os.path.join(export_dir, 'sensor_comparison.png')
    fig.savefig(output_path, dpi=300, bbox_inches='tight')
    print(f"Saved plot to: {output_path}")
    
    # Display basic statistics
    print("\nData Statistics:")
    for condition, df in [("With Worm", worm_df), ("Without Worm", withoutworm_df)]:
        print(f"\n{condition}:")
        print(f"Date range: {df['timestamp'].min()} to {df['timestamp'].max()}")
        
        print("\nMean values and changes:")
        for sensor in ['co2', 'temperature', 'humidity']:
            print(f"\n{sensor.upper()}:")
            print(f"Mean value: {df[sensor].mean():.2f}")
            
            # Calculate and display change statistics
            changes = calculate_changes(df, sensor)
            print(f"Average change per second: {changes['avg_change_per_second']:.4f}")
            print(f"Standard deviation of changes: {changes['std_change']:.4f}")
            print(f"Maximum increase: {changes['max_increase']:.4f}")
            print(f"Maximum decrease: {changes['max_decrease']:.4f}")
            print(f"Number of increases: {changes['positive_changes']}")
            print(f"Number of decreases: {changes['negative_changes']}")

if __name__ == "__main__":
    main()