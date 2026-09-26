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
