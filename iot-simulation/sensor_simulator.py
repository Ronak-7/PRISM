import paho.mqtt.client as mqtt
import random
import time
import json
from datetime import datetime

# MQTT Broker settings
BROKER = "localhost"
PORT = 1883

# Virtual IoT devices
DEVICES = [
    "sensor/temperature",
    "sensor/humidity",
    "sensor/cpu_load",
    "sensor/network_traffic",
    "sensor/power_consumption",
    "sensor/motion",
    "sensor/door_access",
    "sensor/packet_loss"
]

# Connect to MQTT broker
client = mqtt.Client()
client.connect(BROKER, PORT)
client.loop_start()

print("PRISM IoT Sensor Simulator started...")
print(f"Publishing to {len(DEVICES)} virtual sensors")
print("-" * 40)

def generate_reading(device):
    """Generate realistic sensor readings with occasional anomalies"""
    if device == "sensor/temperature":
        # Normal: 20-25°C, Anomaly: spike above 40°C
        if random.random() < 0.05:
            return round(random.uniform(40, 60), 2)
        return round(random.uniform(20, 25), 2)

    elif device == "sensor/humidity":
        # Normal: 40-60%, Anomaly: drop below 10%
        if random.random() < 0.05:
            return round(random.uniform(1, 10), 2)
        return round(random.uniform(40, 60), 2)

    elif device == "sensor/cpu_load":
        # Normal: 10-50%, Anomaly: spike above 90%
        if random.random() < 0.05:
            return round(random.uniform(90, 100), 2)
        return round(random.uniform(10, 50), 2)

    elif device == "sensor/network_traffic":
        # Normal: 100-500 KB/s, Anomaly: spike above 2000 KB/s
        if random.random() < 0.05:
            return round(random.uniform(2000, 5000), 2)
        return round(random.uniform(100, 500), 2)

    elif device == "sensor/power_consumption":
        # Normal: 50-150W, Anomaly: spike above 400W
        if random.random() < 0.05:
            return round(random.uniform(400, 600), 2)
        return round(random.uniform(50, 150), 2)

    elif device == "sensor/motion":
        # Normal: 0 (no motion), Anomaly: repeated motion at unusual frequency
        if random.random() < 0.05:
            return 1  # Anomalous motion detected
        return random.choice([0, 0, 0, 1])  # Mostly no motion

    elif device == "sensor/door_access":
        # Normal: 0-3 access attempts/min, Anomaly: spike above 10
        if random.random() < 0.05:
            return random.randint(10, 20)
        return random.randint(0, 3)

    elif device == "sensor/packet_loss":
        # Normal: 0-2%, Anomaly: spike above 20%
        if random.random() < 0.05:
            return round(random.uniform(20, 50), 2)
        return round(random.uniform(0, 2), 2)

try:
    while True:
        for device in DEVICES:
            reading = generate_reading(device)
            payload = json.dumps({
                "device": device,
                "value": reading,
                "timestamp": datetime.now().isoformat()
            })
            client.publish(device, payload)
            print(f"[{datetime.now().strftime('%H:%M:%S')}] {device}: {reading}")

        print("-" * 40)
        time.sleep(2)  # Publish every 2 seconds

except KeyboardInterrupt:
    print("\nSimulator stopped.")
    client.loop_stop()
    client.disconnect()