"""
sensors.py
Jerarquia de sensores para MicroPython (ESP32 / Wokwi):

    Sensor (abstracta)
      +-- ProximitySensor (abstracta)
      |     +-- UltrasonicSensor   (HC-SR04)
      |     +-- InfraredSensor     (sensor IR digital de obstaculos)
      +-- GPSSensor                (NEO-6M via UART, protocolo NMEA)
"""

import time
from machine import Pin, time_pulse_us, UART

from models import GPSPosition


class Sensor:
    """Clase base abstracta para cualquier sensor del sistema."""

    def read(self):
        raise NotImplementedError("Las subclases deben implementar read()")


class ProximitySensor(Sensor):
    """Clase base abstracta para sensores que miden distancia a un obstaculo."""

    def read_distance(self):
        raise NotImplementedError("Las subclases deben implementar read_distance()")

    def read(self):
        # read() generico delega en read_distance() para sensores de proximidad
        return self.read_distance()


class UltrasonicSensor(ProximitySensor):
    """
    Sensor ultrasonico HC-SR04.
    En Wokwi el componente se llama 'hc-sr04' y expone pines trig/echo.
    """

    def __init__(self, trigger_pin, echo_pin, max_range=400):
        self.trigger_pin = Pin(trigger_pin, Pin.OUT)
        self.echo_pin = Pin(echo_pin, Pin.IN)
        self.max_range = max_range  # cm
        self.trigger_pin.value(0)

    def read_distance(self):
        # Pulso de disparo de 10us
        self.trigger_pin.value(0)
        time.sleep_us(2)
        self.trigger_pin.value(1)
        time.sleep_us(10)
        self.trigger_pin.value(0)

        try:
            # Espera flanco alto y mide duracion (timeout 30ms ~ 5m)
            duration_us = time_pulse_us(self.echo_pin, 1, 30000)
        except OSError:
            return self.max_range

        if duration_us < 0:
            return self.max_range

        distance_cm = (duration_us / 2) / 29.1
        if distance_cm <= 0 or distance_cm > self.max_range:
            return self.max_range
        return distance_cm

    def read(self):
        return self.read_distance()


class InfraredSensor(ProximitySensor):
    """
    Sensor infrarrojo digital de obstaculos (tipo FC-51 / TCRT5000).
    Salida digital: 0 = obstaculo detectado dentro de su rango fijo,
    1 = sin obstaculo. Se traduce a una distancia aproximada en cm
    para mantener una interfaz homogenea con UltrasonicSensor.
    """

    NEAR_DISTANCE_CM = 10
    FAR_DISTANCE_CM = 200

    def __init__(self, signal_pin):
        self.signal_pin = Pin(signal_pin, Pin.IN)

    def read_distance(self):
        obstacle_detected = self.signal_pin.value() == 0
        return self.NEAR_DISTANCE_CM if obstacle_detected else self.FAR_DISTANCE_CM

    def read(self):
        return self.read_distance()


class GPSSensor(Sensor):
    """
    Modulo GPS NEO-6M conectado por UART, usando tramas NMEA GGA.
    En Wokwi: componente 'gps-neo-6m' conectado a UART1 (por defecto).
    """

    def __init__(self, uart_id=1, tx_pin=17, rx_pin=16, baudrate=9600):
        self.uart = UART(uart_id, baudrate=baudrate, tx=tx_pin, rx=rx_pin)
        self.last_position = None

    def read(self):
        return self._parse_next_sentence()

    def get_position(self):
        """Devuelve la ultima posicion valida conocida (o None si nunca hubo fix)."""
        parsed = self._parse_next_sentence()
        return parsed if parsed is not None else self.last_position

    def _parse_next_sentence(self):
        if not self.uart.any():
            return None
        try:
            raw_line = self.uart.readline()
            if not raw_line:
                return None
            sentence = raw_line.decode("utf-8", "ignore").strip()
        except Exception:
            return None

        if sentence.startswith("$GPGGA") or sentence.startswith("$GNGGA"):
            position = self._parse_gga(sentence)
            if position is not None:
                self.last_position = position
            return position
        return None

    def _parse_gga(self, sentence):
        """
        Formato NMEA GGA:
        $GPGGA,hhmmss.ss,lat,N/S,lon,E/W,fix,numSat,hdop,alt,M,...
        """
        fields = sentence.split(",")
        if len(fields) < 9:
            return None
        if fields[2] == "" or fields[4] == "" or fields[6] == "0":
            return None  # sin fix valido

        try:
            latitude = self._nmea_to_decimal(fields[2], fields[3])
            longitude = self._nmea_to_decimal(fields[4], fields[5])
            hdop = float(fields[8]) if fields[8] else 99.0
            return GPSPosition(latitude, longitude, hdop)
        except (ValueError, IndexError):
            return None

    @staticmethod
    def _nmea_to_decimal(raw_value, hemisphere):
        """Convierte formato NMEA (ddmm.mmmm) a grados decimales."""
        if not raw_value:
            return 0.0
        dot_index = raw_value.find(".")
        degrees = float(raw_value[0:dot_index - 2])
        minutes = float(raw_value[dot_index - 2:])
        decimal_degrees = degrees + (minutes / 60.0)
        if hemisphere in ("S", "W"):
            decimal_degrees = -decimal_degrees
        return decimal_degrees
