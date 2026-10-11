"""VisorSense MicroPython entry point."""

from alerts import AlertManager
from config import (
    BUZZER_PIN,
    DESTINATION_LATITUDE,
    DESTINATION_LONGITUDE,
    DEVICE_ID,
    GPS_RX_PIN,
    GPS_TX_PIN,
    INFRARED_PIN,
    IR_ACTIVE_LEVEL,
    LED_PIN,
    LOOP_DELAY_MS,
    MQTT_BROKER,
    MQTT_CLIENT_ID,
    MQTT_ENABLED,
    MQTT_KEEPALIVE,
    MQTT_PASSWORD,
    MQTT_PORT,
    MQTT_QOS,
    MQTT_SSL_PARAMS,
    MQTT_TOPIC,
    MQTT_TLS,
    MQTT_USERNAME,
    WIFI_CONNECT_TIMEOUT_MS,
    WIFI_ENABLED,
    WIFI_PASSWORD,
    WIFI_RECONNECT_INITIAL_MS,
    WIFI_RECONNECT_MAX_MS,
    WIFI_SSID,
    mqtt_configuration_complete,
    SIMULATED_LATITUDE,
    SIMULATED_LONGITUDE,
    SIMULATION_MODE,
    TELEMETRY_ENABLED,
    ULTRASONIC_ECHO_PIN,
    ULTRASONIC_TRIGGER_PIN,
)
from device import VisorSense
from gps import NmeaGps, SimulatedGps
from navigation import NavigationManager
from sensors import InfraredSensor, UltrasonicSensor
from telemetry import TelemetryPublisher
from transport import MqttConfig, MqttTransport, SimulatedTransport
from wifi_manager import WifiConfig, WifiManager


def create_gps():
    """Create the real or simulated GPS implementation."""
    if SIMULATION_MODE:
        return SimulatedGps(SIMULATED_LATITUDE, SIMULATED_LONGITUDE)

    return NmeaGps(GPS_RX_PIN, GPS_TX_PIN)


def main():
    """Build the device and start continuous monitoring."""
    ultrasonic = UltrasonicSensor(
        ULTRASONIC_TRIGGER_PIN,
        ULTRASONIC_ECHO_PIN,
    )
    infrared = InfraredSensor(INFRARED_PIN, IR_ACTIVE_LEVEL)
    alerts = AlertManager(BUZZER_PIN, LED_PIN)
    gps = create_gps()
    navigation = NavigationManager(
        DESTINATION_LATITUDE,
        DESTINATION_LONGITUDE,
    )
    telemetry_publisher = None
    if TELEMETRY_ENABLED:
        wifi_manager = None
        mqtt_ready = mqtt_configuration_complete()
        if MQTT_ENABLED and not mqtt_ready:
            print("MQTT disabled: Wi-Fi or MQTT configuration is incomplete.")

        if mqtt_ready:
            wifi_manager = WifiManager(
                WifiConfig(
                    ssid=WIFI_SSID,
                    password=WIFI_PASSWORD,
                    connect_timeout_ms=WIFI_CONNECT_TIMEOUT_MS,
                    reconnect_initial_ms=WIFI_RECONNECT_INITIAL_MS,
                    reconnect_max_ms=WIFI_RECONNECT_MAX_MS,
                )
            )
            mqtt_config = MqttConfig(
                broker=MQTT_BROKER,
                port=MQTT_PORT,
                topic=MQTT_TOPIC,
                client_id=MQTT_CLIENT_ID,
                qos=MQTT_QOS,
                keepalive=MQTT_KEEPALIVE,
                username=MQTT_USERNAME,
                password=MQTT_PASSWORD,
                ssl=MQTT_TLS,
                ssl_params=MQTT_SSL_PARAMS,
            )
            telemetry_transport = MqttTransport(
                mqtt_config,
                connectivity=wifi_manager,
            )
        else:
            telemetry_transport = SimulatedTransport(max_payloads=10)
        telemetry_publisher = TelemetryPublisher(telemetry_transport)

    device = VisorSense(
        ultrasonic,
        infrared,
        alerts,
        gps,
        navigation,
        telemetry_publisher,
        DEVICE_ID,
    )

    print("VisorSense started.")
    print("Simulation mode:", SIMULATION_MODE)
    device.run_forever(LOOP_DELAY_MS)


main()
