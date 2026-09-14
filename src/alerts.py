"""
alerts.py
AlertManager: traduce eventos del sistema (obstaculos, navegacion,
bateria) en patrones acusticos sobre un buzzer activo/pasivo
manejado por PWM. Compatible con el componente 'buzzer' de Wokwi.
"""

import time
from machine import Pin, PWM


class AlertManager:
    """Genera los distintos patrones de sonido descritos en el
    documento de arquitectura (pitido lento, intermitente, continuo)."""

    def __init__(self, buzzer_pin):
        self.buzzer = PWM(Pin(buzzer_pin))
        self._silence()

    def _silence(self):
        try:
            self.buzzer.duty_u16(0)
        except AttributeError:
            self.buzzer.duty(0)

    def _beep(self, frequency_hz, duration_ms, volume=32768):
        self.buzzer.freq(frequency_hz)
        try:
            self.buzzer.duty_u16(volume)
        except AttributeError:
            self.buzzer.duty(512)
        time.sleep_ms(duration_ms)
        self._silence()

    def alert_obstacle(self, risk_level):
        """
        Distante  -> pitido lento
        Cercano   -> pitido intermitente rapido
        Riesgo inmediato -> pitido continuo
        """
        if risk_level == "warning":
            self._beep(1500, 100)
            time.sleep_ms(400)
        elif risk_level == "danger":
            self._beep(2000, 100)
            time.sleep_ms(100)
        elif risk_level == "critical":
            self._beep(3000, 300)

    def alert_navigation(self, direction_deg):
        """Tono corto para indicar un evento de navegacion (cambio de rumbo)."""
        self._beep(1000, 150)

    def alert_system(self, event):
        """Eventos generales del sistema: arranque, bateria baja, fix GPS, etc."""
        if event == "startup":
            self._beep(1200, 200)
        elif event == "low_battery":
            for _ in range(3):
                self._beep(500, 200)
                time.sleep_ms(200)
        elif event == "gps_fix":
            self._beep(1800, 150)
        elif event == "arrived":
            self._beep(2200, 400)
