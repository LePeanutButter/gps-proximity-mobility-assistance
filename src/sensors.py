"""Sensor abstractions used by the VisorSense firmware."""

from machine import Pin, time_pulse_us


class UltrasonicSensor:
    """Measure distance with an HC-SR04 ultrasonic sensor."""

    def __init__(self, trigger_pin, echo_pin):
        self._trigger = Pin(trigger_pin, Pin.OUT, value=0)
        self._echo = Pin(echo_pin, Pin.IN)

    def distance_cm(self):
        """Return the measured distance in centimeters or None on timeout."""
        self._trigger.value(0)
        self._trigger.value(1)
        self._trigger.value(0)

        duration = time_pulse_us(self._echo, 1, 30000)
        if duration < 0:
            return None

        return duration / 58.0


class InfraredSensor:
    """Read a digital infrared obstacle sensor."""

    def __init__(self, pin, active_level=0):
        self._sensor = Pin(pin, Pin.IN)
        self._active_level = active_level

    def obstacle_detected(self):
        """Return True when the sensor reports an obstacle."""
        return self._sensor.value() == self._active_level
