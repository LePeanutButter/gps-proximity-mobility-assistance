"""VisorSense MicroPython entry point."""

from alerts import AlertManager
from config import (
    BUZZER_PIN,
    DESTINATION_LATITUDE,
    DESTINATION_LONGITUDE,
    GPS_RX_PIN,
    GPS_TX_PIN,
    INFRARED_PIN,
    IR_ACTIVE_LEVEL,
    LED_PIN,
    LOOP_DELAY_MS,
    SIMULATED_LATITUDE,
    SIMULATED_LONGITUDE,
    SIMULATION_MODE,
    ULTRASONIC_ECHO_PIN,
    ULTRASONIC_TRIGGER_PIN,
)
from device import VisorSense
from gps import NmeaGps, SimulatedGps
from navigation import NavigationManager
from sensors import InfraredSensor, UltrasonicSensor


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

    device = VisorSense(
        ultrasonic,
        infrared,
        alerts,
        gps,
        navigation,
    )

    print("VisorSense started.")
    print("Simulation mode:", SIMULATION_MODE)
    device.run_forever(LOOP_DELAY_MS)


main()
