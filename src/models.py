"""
models.py
Clases de datos simples usadas por el resto del sistema.
Corresponden a: GPSPosition, Obstacle, Destination del diagrama de clases.
"""


class GPSPosition:
    """Representa una posicion geografica obtenida del modulo GPS."""

    def __init__(self, latitude=0.0, longitude=0.0, accuracy=99.0):
        self.latitude = latitude
        self.longitude = longitude
        self.accuracy = accuracy  # HDOP aproximado (menor = mejor precision)

    def __repr__(self):
        return "GPSPosition(lat={}, lon={}, acc={})".format(
            self.latitude, self.longitude, self.accuracy
        )


class Obstacle:
    """Representa un obstaculo detectado por los sensores de proximidad."""

    def __init__(self, distance, direction, risk_level):
        self.distance = distance        # cm
        self.direction = direction      # "front", "left", "right"
        self.risk_level = risk_level    # "warning", "danger", "critical"

    def __repr__(self):
        return "Obstacle(dist={}cm, dir={}, risk={})".format(
            self.distance, self.direction, self.risk_level
        )


class Destination:
    """Representa un destino de navegacion almacenado por el usuario."""

    def __init__(self, name, latitude, longitude):
        self.name = name
        self.latitude = latitude
        self.longitude = longitude

    def __repr__(self):
        return "Destination(name={}, lat={}, lon={})".format(
            self.name, self.latitude, self.longitude
        )
