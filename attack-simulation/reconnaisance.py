import paho.mqtt.client as mqtt
import time
import json
from datetime import datetime

# MQTT Broker settings
BROKER = "localhost"
PORT = 1883

# Topics to probe
TOPICS = [
    "sensor/temperature",
    "sensor/humidity",
    "sensor/cpu_load",
    "sensor/network_traffic",
    "sensor/power_consumption",
    "sensor/motion",
    "sensor/door_access",
    "sensor/packet_loss",
    "admin/#",
    "system/#",
    "config/#",
    "prism/#",
    "devices/#",
    "internal/#"
]

discovered_topics = []

def on_message(client, userdata, message):
    topic = message.topic
    if topic not in discovered_topics:
        discovered_topics.append(topic)
        print(f"[{datetime.now().strftime('%H:%M:%S')}] DISCOVERED topic: {topic}")

client = mqtt.Client()
client.on_message = on_message
client.connect(BROKER, PORT)

print("=" * 40)
print("PRISM ATTACK SIMULATION — Reconnaissance")
print("Scanning and enumerating MQTT topics...")
print("=" * 40)

# Subscribe to all topics using wildcard
client.subscribe("#")
client.loop_start()

try:
    while True:
        print(f"[{datetime.now().strftime('%H:%M:%S')}] Probing {len(TOPICS)} known topics...")
        
        # Probe each topic by publishing a reconnaissance packet
        for topic in TOPICS:
            payload = json.dumps({
                "probe": True,
                "timestamp": datetime.now().isoformat(),
                "attack": "Reconnaissance"
            })
            client.publish(topic, payload)
        
        print(f"[{datetime.now().strftime('%H:%M:%S')}] Topics discovered so far: {len(discovered_topics)}")
        print("-" * 40)
        time.sleep(3)

except KeyboardInterrupt:
    print(f"\nReconnaissance stopped.")
    print(f"Total topics discovered: {len(discovered_topics)}")
    for t in discovered_topics:
        print(f"  - {t}")
    client.loop_stop()
    client.disconnect()