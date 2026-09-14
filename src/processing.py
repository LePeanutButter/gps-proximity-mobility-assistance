"""
processing.py
Logica de negocio local del dispositivo:
    - ObstacleDetector: clasifica el riesgo de un obstaculo segun distancia.
    - NavigationManager: calcula distancia/rumbo hacia un destino guardado.
"""

import math

from models import Obstacle


class ObstacleDetector:
    """
    Evalua las lecturas de los sensores de proximidad y determina
    el nivel de riesgo asociado a un obstaculo.
    """

    RISK_NONE = "none"
    RISK_WARNING = "warning"
    RISK_DANGER = "danger"
    RISK_CRITICAL = "critical"

    def __init__(self, warning_threshold=150, danger_threshold=60, critical_threshold=20):
        # Umbrales en centimetros. warning > danger > critical
        self.warning_threshold = warning_threshold
        self.danger_threshold = danger_threshold
        self.critical_threshold = critical_threshold

    def classify_risk(self, distance):
        if distance <= self.critical_threshold:
            return self.RISK_CRITICAL
        if distance <= self.danger_threshold:
            return self.RISK_DANGER
        if distance <= self.warning_threshold:
            return self.RISK_WARNING
        return self.RISK_NONE

    def detect_obstacle(self, distance, direction):
        """Devuelve un Obstacle si hay riesgo, o None si el camino esta despejado."""
        risk_level = self.classify_risk(distance)
        if risk_level == self.RISK_NONE:
            return None
        return Obstacle(distance, direction, risk_level)


class NavigationManager:
    """
    Maneja el destino activo y calcula distancia/rumbo usando la
    posicion GPS actual mediante la formula de Haversine.
    """

    EARTH_RADIUS_M = 6371000
    ARRIVAL_THRESHOLD_M = 5

    def __init__(self):
        self.destination = None

    def set_destination(self, destination):
        self.destination = destination

    def calculate_distance(self, position):
        """Distancia en metros entre la posicion actual y el destino."""
        if self.destination is None or position is None:
            return None

        lat1 = math.radians(position.latitude)
        lon1 = math.radians(position.longitude)
        lat2 = math.radians(self.destination.latitude)
        lon2 = math.radians(self.destination.longitude)

        delta_lat = lat2 - lat1
        delta_lon = lon2 - lon1

        a = (math.sin(delta_lat / 2) ** 2
             + math.cos(lat1) * math.cos(lat2) * math.sin(delta_lon / 2) ** 2)
        c = 2 * math.asin(math.sqrt(a))
        return c * self.EARTH_RADIUS_M

    def calculate_direction(self, position):
        """Rumbo en grados (0-360, 0 = norte) hacia el destino."""
        if self.destination is None or position is None:
            return None

        lat1 = math.radians(position.latitude)
        lon1 = math.radians(position.longitude)
        lat2 = math.radians(self.destination.latitude)
        lon2 = math.radians(self.destination.longitude)

        delta_lon = lon2 - lon1
        x = math.sin(delta_lon) * math.cos(lat2)
        y = (math.cos(lat1) * math.sin(lat2)
             - math.sin(lat1) * math.cos(lat2) * math.cos(delta_lon))
        bearing_rad = math.atan2(x, y)
        bearing_deg = math.degrees(bearing_rad)
        return (bearing_deg + 360) % 360

    def evaluate_route(self, position):
        """Resume el estado de la ruta actual: distancia, rumbo y si ya llego."""
        if self.destination is None or position is None:
            return None

        distance_m = self.calculate_distance(position)
        direction_deg = self.calculate_direction(position)
        arrived = distance_m is not None and distance_m <= self.ARRIVAL_THRESHOLD_M

        return {
            "distance": distance_m,
            "direction": direction_deg,
            "arrived": arrived,
        }
