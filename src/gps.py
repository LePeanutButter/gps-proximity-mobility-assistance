"""Minimal NMEA GPS reader and simulation source."""

from machine import UART
import time


class GpsPosition:
    """Store a geographic position."""

    def __init__(self, latitude, longitude):
        self.latitude = latitude
        self.longitude = longitude


class NmeaGps:
    """Read latitude and longitude from a NEO-6M NMEA stream."""

    def __init__(self, rx_pin, tx_pin, baudrate=9600):
        self._uart = UART(
            2,
            baudrate=baudrate,
            rx=rx_pin,
            tx=tx_pin,
            timeout=100,
            timeout_char=10,
        )
        self._buffer = b""

    def read_position(self):
        """Return the latest valid GGA/RMC position or None."""
        data = self._uart.read()
        if not data:
            return None

        self._buffer += data
        lines = self._buffer.split(b"\n")
        self._buffer = lines[-1]

        for raw_line in lines[:-1]:
            line = raw_line.decode("ascii", "ignore").strip()
            position = self._parse_sentence(line)
            if position:
                return position

        return None

    @staticmethod
    def _parse_sentence(sentence):
        """Parse a GGA or RMC sentence containing a valid position."""
        if not sentence.startswith("$"):
            return None

        fields = sentence.split(",")
        sentence_type = fields[0][-3:]

        if sentence_type == "GGA" and len(fields) >= 7:
            if fields[6] == "0":
                return None
            latitude, longitude = fields[2], fields[4]
            latitude_direction, longitude_direction = fields[3], fields[5]
        elif sentence_type == "RMC" and len(fields) >= 7:
            if fields[2] != "A":
                return None
            latitude, longitude = fields[3], fields[5]
            latitude_direction, longitude_direction = fields[4], fields[6]
        else:
            return None

        lat = NmeaGps._to_decimal(latitude, latitude_direction)
        lon = NmeaGps._to_decimal(longitude, longitude_direction)

        if lat is None or lon is None:
            return None

        return GpsPosition(lat, lon)

    @staticmethod
    def _to_decimal(value, direction):
        """Convert NMEA degrees/minutes to signed decimal degrees."""
        if not value or len(value) < 4:
            return None

        try:
            degrees_length = 2 if direction in ("N", "S") else 3
            degrees = float(value[:degrees_length])
            minutes = float(value[degrees_length:])
            decimal = degrees + minutes / 60
            return -decimal if direction in ("S", "W") else decimal
        except ValueError:
            return None


class SimulatedGps:
    """Provide a fixed GPS position for Wokwi demonstrations."""

    def __init__(self, latitude, longitude):
        self._position = GpsPosition(latitude, longitude)
        self._last_read = 0

    def read_position(self):
        """Return the configured simulated position."""
        now = time.ticks_ms()
        if time.ticks_diff(now, self._last_read) >= 1000:
            self._last_read = now
            return self._position
        return None
