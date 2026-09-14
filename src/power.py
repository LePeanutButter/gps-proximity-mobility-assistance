"""
power.py
BatteryManager: lee el nivel de bateria a traves de un divisor de
voltaje conectado a un pin ADC del ESP32. En Wokwi puede simularse
con un potenciometro conectado al pin analogico configurado.
"""

from machine import ADC, Pin


class BatteryManager:
    """Estima el porcentaje de bateria restante y detecta nivel bajo."""

    def __init__(self, battery_pin, low_battery_threshold=20,
                 max_voltage=4.2, min_voltage=3.3):
        self.adc = ADC(Pin(battery_pin))
        try:
            self.adc.atten(ADC.ATTN_11DB)  # rango completo ~0-3.3V en ESP32
        except AttributeError:
            pass
        self.low_battery_threshold = low_battery_threshold  # %
        self.max_voltage = max_voltage
        self.min_voltage = min_voltage

    def _read_voltage(self):
        """Lee el voltaje de bateria asumiendo un divisor resistivo 1:2."""
        try:
            microvolts = self.adc.read_uv()
            return (microvolts / 1_000_000) * 2
        except AttributeError:
            raw = self.adc.read()  # 0-4095 en ESP32
            return (raw / 4095) * 3.3 * 2

    def get_battery_level(self):
        """Devuelve el porcentaje de bateria (0-100) segun el voltaje leido."""
        voltage = self._read_voltage()
        span = self.max_voltage - self.min_voltage
        percentage = ((voltage - self.min_voltage) / span) * 100
        return max(0, min(100, percentage))

    def is_low_battery(self):
        return self.get_battery_level() <= self.low_battery_threshold
