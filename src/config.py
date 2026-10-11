"""Hardware and application configuration for VisorSense."""

# GPIO assignments from the system electrical design.
GPS_RX_PIN = 16
GPS_TX_PIN = 17

ULTRASONIC_TRIGGER_PIN = 25
ULTRASONIC_ECHO_PIN = 26

INFRARED_PIN = 27
BUZZER_PIN = 33
LED_PIN = 2
BUTTON_PIN = 32

# Obstacle thresholds in centimeters.
NEAR_DISTANCE_CM = 50
IMMEDIATE_DISTANCE_CM = 20

# Main loop period.
LOOP_DELAY_MS = 100

# IR obstacle modules commonly use an active-low output.
IR_ACTIVE_LEVEL = 0

# Academic simulation mode.
# Set to False when using the physical NEO-6M GPS module.
SIMULATION_MODE = True

# Simulated GPS position and destination used only in Wokwi.
SIMULATED_LATITUDE = 4.7110
SIMULATED_LONGITUDE = -74.0721
DESTINATION_LATITUDE = 4.7118
DESTINATION_LONGITUDE = -74.0721

# Telemetry identity and local transport. No cloud credentials are stored here.
DEVICE_ID = "visor-esp32-001"
TELEMETRY_ENABLED = True
MQTT_ENABLED = False
MQTT_BROKER = ""
MQTT_PORT = 8883
MQTT_TOPIC = "visorsense/telemetry"
MQTT_CLIENT_ID = DEVICE_ID
MQTT_QOS = 1
MQTT_KEEPALIVE = 60
MQTT_TLS = True

# Wi-Fi credentials must be supplied in a local, untracked configuration.
WIFI_ENABLED = False
WIFI_SSID = ""
WIFI_PASSWORD = None
WIFI_CONNECT_TIMEOUT_MS = 10000
WIFI_RECONNECT_INITIAL_MS = 1000
WIFI_RECONNECT_MAX_MS = 30000


def _apply_local_overrides():
    """Load optional untracked settings for a physical device."""
    try:
        import config_local
    except ImportError:
        return

    names = (
        "DEVICE_ID",
        "TELEMETRY_ENABLED",
        "MQTT_ENABLED",
        "MQTT_BROKER",
        "MQTT_PORT",
        "MQTT_TOPIC",
        "MQTT_CLIENT_ID",
        "MQTT_QOS",
        "MQTT_KEEPALIVE",
        "MQTT_TLS",
        "MQTT_USERNAME",
        "MQTT_PASSWORD",
        "MQTT_SSL_PARAMS",
        "WIFI_ENABLED",
        "WIFI_SSID",
        "WIFI_PASSWORD",
        "WIFI_CONNECT_TIMEOUT_MS",
        "WIFI_RECONNECT_INITIAL_MS",
        "WIFI_RECONNECT_MAX_MS",
    )
    module_globals = globals()
    for name in names:
        if hasattr(config_local, name):
            module_globals[name] = getattr(config_local, name)


MQTT_USERNAME = None
MQTT_PASSWORD = None
MQTT_SSL_PARAMS = {}

_apply_local_overrides()


def wifi_configuration_complete():
    """Return whether the minimum Wi-Fi settings are present."""
    return bool(
        isinstance(WIFI_ENABLED, bool)
        and WIFI_ENABLED
        and isinstance(WIFI_SSID, str)
        and WIFI_SSID
        and isinstance(WIFI_PASSWORD, str)
        and WIFI_PASSWORD
    )


def mqtt_configuration_complete():
    """Return whether Wi-Fi and MQTT settings are complete and valid."""
    return bool(
        MQTT_ENABLED
        and wifi_configuration_complete()
        and isinstance(MQTT_BROKER, str)
        and MQTT_BROKER
        and isinstance(MQTT_TOPIC, str)
        and MQTT_TOPIC
        and isinstance(MQTT_CLIENT_ID, str)
        and MQTT_CLIENT_ID
        and isinstance(MQTT_PORT, int)
        and MQTT_PORT >= 1
        and MQTT_PORT <= 65535
        and isinstance(MQTT_QOS, int)
        and MQTT_QOS in (0, 1, 2)
        and ((MQTT_USERNAME is None) == (MQTT_PASSWORD is None))
    )
