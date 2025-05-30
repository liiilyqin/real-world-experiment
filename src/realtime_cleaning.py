import pandas as pd
import numpy as np
from scipy.stats import median_abs_deviation
from collections import deque
import time
import serial  # for reading sensor data

class RealTimeHampelFilter:
    def __init__(self, window_size=10, n_sigmas=3):
        self.window_size = window_size
        self.n_sigmas = n_sigmas
        # Initialize sliding windows for each sensor
        self.co2_window = deque(maxlen=window_size)
        self.temp_window = deque(maxlen=window_size)
        self.humidity_window = deque(maxlen=window_size)

    def hampel_filter_point(self, value, window):
        """Apply Hampel filter to a single point"""
        if len(window) < self.window_size:
            return value
        
        window_array = np.array(window)
        median = np.median(window_array)
        mad = median_abs_deviation(window_array, nan_policy='omit')
        threshold = self.n_sigmas * mad
        
        if np.abs(value - median) > threshold:
            return median
        return value

    def process_reading(self, co2, temperature, humidity):
        """Process new sensor readings"""
        # Add new values to windows
        self.co2_window.append(co2)
        self.temp_window.append(temperature)
        self.humidity_window.append(humidity)
        
        # Apply Hampel filter
        cleaned_co2 = self.hampel_filter_point(co2, self.co2_window)
        cleaned_temp = self.hampel_filter_point(temperature, self.temp_window)
        cleaned_humidity = self.hampel_filter_point(humidity, self.humidity_window)
        
        return cleaned_co2, cleaned_temp, cleaned_humidity

def read_sensor_data(serial_port):
    """Read data from sensor via serial port"""
    try:
        line = serial_port.readline().decode('utf-8').strip()
        # Assuming format: "co2,temperature,humidity"
        co2, temp, humidity = map(float, line.split(','))
        return co2, temp, humidity
    except Exception as e:
        print(f"Error reading sensor: {e}")
        return None, None, None

def main():
    # Initialize serial connection (adjust port and baud rate as needed)
    SERIAL_PORT = 'COM3'  # Change to your sensor's port
    BAUD_RATE = 9600
    
    try:
        ser = serial.Serial(SERIAL_PORT, BAUD_RATE)
        print(f"Connected to sensor on {SERIAL_PORT}")
        
        # Initialize Hampel filter
        hampel = RealTimeHampelFilter(window_size=10, n_sigmas=3)
        
        while True:
            # Read sensor data
            co2, temp, humidity = read_sensor_data(ser)
            
            if all(v is not None for v in [co2, temp, humidity]):
                # Clean data using Hampel filter
                cleaned_co2, cleaned_temp, cleaned_humidity = hampel.process_reading(
                    co2, temp, humidity
                )
                
                # Print results
                print("\nRaw Readings:")
                print(f"CO2: {co2:.2f}, Temp: {temp:.2f}, Humidity: {humidity:.2f}")
                print("Cleaned Readings:")
                print(f"CO2: {cleaned_co2:.2f}, Temp: {cleaned_temp:.2f}, "
                      f"Humidity: {cleaned_humidity:.2f}")
            
            # Add small delay to prevent excessive CPU usage
            time.sleep(0.1)
            
    except KeyboardInterrupt:
        print("\nStopping sensor reading...")
    except Exception as e:
        print(f"Error: {e}")
    finally:
        if 'ser' in locals():
            ser.close()
            print("Serial connection closed")

if __name__ == "__main__":
    main()