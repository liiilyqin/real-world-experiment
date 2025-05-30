import serial
from google.cloud import firestore
from google.oauth2 import service_account
from datetime import datetime
import os
import csv

# 设置串口参数
PORT = 'COM25'  # 替换为你的串口号
BAUDRATE = 115200

# Create local test directory structure
test_dir = "test"
subdirs = ["co2", "temperature", "humidity"]
for subdir in [test_dir] + [os.path.join(test_dir, d) for d in subdirs]:
    if not os.path.exists(subdir):
        os.makedirs(subdir)

# Firestore 初始化
key_path = "cloud/experiment-sdk.json"  # 替换为你的 JSON 密钥路径
credentials = service_account.Credentials.from_service_account_file(key_path)
db = firestore.Client(credentials=credentials)

# 获取 test collection reference
test_ref = db.collection('test')

# 打开串口
ser = serial.Serial(PORT, BAUDRATE)
print(f"Listening on {PORT}... Uploading to Firestore")

try:
    while True:
        line = ser.readline().decode('utf-8').strip()
        print(f"Received: {line}")
        parts = line.split(',')
        if len(parts) == 4:
            timestamp_ms = int(parts[0])
            co2 = int(parts[1])
            temperature = float(parts[2])
            humidity = float(parts[3])

            current_time = datetime.utcnow()
            time_str = current_time.strftime("%Y-%m-%d_%H-%M-%S")
            date_str = current_time.strftime("%Y-%m-%d")

            # Save all data to a single CSV file with date as filename
            csv_path = os.path.join(test_dir, f"{date_str}.csv")
            
            # Create file with headers if it doesn't exist
            if not os.path.exists(csv_path):
                with open(csv_path, 'w', newline='') as f:
                    writer = csv.writer(f)
                    writer.writerow(["timestamp", "co2", "temperature", "humidity"])

            # Append the new data
            with open(csv_path, 'a', newline='') as f:
                writer = csv.writer(f)
                writer.writerow([time_str, co2, temperature, humidity])

            # 写入 co2_data 集合
            test_ref.document("co2_data").collection(date_str).add({
                "timestamp": current_time,
                "timestamp_ms": timestamp_ms,
                "value": co2
            })

            # 写入 temperature_data 集合
            test_ref.document("temperature_data").collection(date_str).add({
                "timestamp": current_time,
                "timestamp_ms": timestamp_ms,
                "value": temperature
            })

            # 写入 humidity_data 集合
            test_ref.document("humidity_data").collection(date_str).add({
                "timestamp": current_time,
                "timestamp_ms": timestamp_ms,
                "value": humidity
            })

            print("Uploaded all to Firestore.")

except KeyboardInterrupt:
    print("Stopped by user.")
finally:
    ser.close()
