"""Acoustic and visual alert handling for VisorSense."""

from machine import Pin
import time


class AlertManager:
    """Generate acoustic patterns for obstacle risk levels."""

    def __init__(self, buzzer_pin, led_pin):
        self._buzzer = Pin(buzzer_pin, Pin.OUT, value=0)
        self._led = Pin(led_pin, Pin.OUT, value=0)

    def update(self, distance_cm, infrared_obstacle):
        """Apply the alert pattern required by the current obstacle state."""
        if infrared_obstacle:
            self._continuous_alert()
            return "INFRARED"

        if distance_cm is None:
            self._silent()
            return "NO_READING"

        if distance_cm <= 20:
            self._continuous_alert()
            return "IMMEDIATE"

        if distance_cm <= 50:
            self._pulse_alert(100, 150)
            return "NEAR"

        if distance_cm <= 150:
            self._pulse_alert(100, 900)
            return "DISTANT"

        self._silent()
        return "CLEAR"

    def _continuous_alert(self):
        """Turn the buzzer on for the current monitoring cycle."""
        self._buzzer.value(1)
        self._led.value(1)

    def _pulse_alert(self, on_ms, off_ms):
        """Generate one short alert pulse."""
        self._buzzer.value(1)
        self._led.value(1)
        time.sleep_ms(on_ms)
        self._buzzer.value(0)
        self._led.value(0)
        time.sleep_ms(off_ms)

    def _silent(self):
        """Disable acoustic and visual alerts."""
        self._buzzer.value(0)
        self._led.value(0)
