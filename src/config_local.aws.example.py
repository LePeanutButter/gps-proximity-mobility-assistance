"""AWS IoT Core from Wokwi. Copy to config_local.py; never commit real values.

config_local.py is ignored by Git. It holds the device private key, so do not
save it in a public Wokwi project.
"""

import ssl as _ssl

# Wokwi's virtual access point is open and has no password.
WIFI_ENABLED = True
WIFI_OPEN_NETWORK = True
WIFI_SSID = "Wokwi-GUEST"
WIFI_PASSWORD = ""

MQTT_ENABLED = True
# Output of: terraform output aws_iot_endpoint
MQTT_BROKER = "replace-with-endpoint-ats.iot.us-east-1.amazonaws.com"
MQTT_PORT = 8883
MQTT_TLS = True
# Must equal the Thing name: the IoT policy only allows this client ID.
MQTT_CLIENT_ID = "visor-esp32-001"
# Must stay below "visorsense/telemetry/" to satisfy the IoT policy.
MQTT_TOPIC = "visorsense/telemetry/visor-esp32-001"
MQTT_QOS = 1

TELEMETRY_INTERVAL_MS = 10000

# Paste the full PEM contents, including the BEGIN and END lines.
_AWS_ROOT_CA = b"""replace-with-AmazonRootCA1.pem
"""
_DEVICE_CERT = b"""replace-with-certificate.pem
"""
_DEVICE_KEY = b"""replace-with-private-key.pem
"""

MQTT_SSL_PARAMS = {
    "server_hostname": MQTT_BROKER,
    "cert_reqs": _ssl.CERT_REQUIRED,
    "cadata": _AWS_ROOT_CA,
    "cert": _DEVICE_CERT,
    "key": _DEVICE_KEY,
}
