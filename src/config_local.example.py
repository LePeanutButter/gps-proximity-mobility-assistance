"""Copy to config_local.py on the device; do not commit real values."""

WIFI_ENABLED = True
WIFI_SSID = "replace-with-lan-ssid"
WIFI_PASSWORD = "replace-with-local-password"

MQTT_ENABLED = True
MQTT_BROKER = "192.0.2.10"
MQTT_PORT = 1883
MQTT_TOPIC = "visorsense/telemetry"
MQTT_CLIENT_ID = "visor-esp32-001"
MQTT_QOS = 1
MQTT_KEEPALIVE = 60
MQTT_TLS = False

# Use credentials only when the local broker requires them.
MQTT_USERNAME = None
MQTT_PASSWORD = None
MQTT_SSL_PARAMS = {}
