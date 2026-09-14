"""
controller.py
Controller: orquesta sensores, deteccion de obstaculos,
navegacion, alertas y bateria en el bucle principal del dispositivo.
"""

import time

from sensors import UltrasonicSensor, InfraredSensor, GPSSensor
from processing import ObstacleDetector, NavigationManager
from alerts import AlertManager
from power import BatteryManager


class Controller:
    """
    Composicion de subsistemas segun el diagrama de clases:
        - sensors: diccionario con instancias de Sensor
        - obstacleDetector, navigationManager, alertManager, batteryManager
    Los numeros de pin son los usados en el diagram.json de Wokwi
    incluido junto a este proyecto; ajustalos si cambias el cableado.
    """

    BATTERY_CHECK_INTERVAL_MS = 30000
    LOOP_DELAY_MS = 100

    def __init__(self):
        self.sensors = {
            "front": UltrasonicSensor(trigger_pin=5, echo_pin=18, max_range=400),
            "left": InfraredSensor(signal_pin=19),
            "right": InfraredSensor(signal_pin=21),
            "gps": GPSSensor(uart_id=1, tx_pin=17, rx_pin=16, baudrate=9600),
        }

        self.obstacle_detector = ObstacleDetector(
            warning_threshold=150, danger_threshold=60, critical_threshold=20
        )
        self.navigation_manager = NavigationManager()
        self.alert_manager = AlertManager(buzzer_pin=25)
        self.battery_manager = BatteryManager(battery_pin=34, low_battery_threshold=20)

        self._latest_readings = {}
        self._last_battery_check_ms = time.ticks_ms()

    def run(self):
        """Bucle principal: inicializacion + monitoreo continuo."""
        self.alert_manager.alert_system("startup")
        while True:
            self.update_sensors()
            self.process_obstacles()
            self.process_navigation()
            self.check_battery()
            time.sleep_ms(self.LOOP_DELAY_MS)

    def update_sensors(self):
        """Lee todos los sensores de proximidad y actualiza el GPS."""
        self._latest_readings = {
            "front": self.sensors["front"].read_distance(),
            "left": self.sensors["left"].read_distance(),
            "right": self.sensors["right"].read_distance(),
        }
        self.sensors["gps"].read()

    def process_obstacles(self):
        """Clasifica riesgo por direccion y dispara alertas si corresponde."""
        for direction, distance in self._latest_readings.items():
            obstacle = self.obstacle_detector.detect_obstacle(distance, direction)
            if obstacle is not None:
                print("Obstaculo detectado:", obstacle)
                self.alert_manager.alert_obstacle(obstacle.risk_level)

    def process_navigation(self):
        """Si hay destino y posicion GPS validas, evalua la ruta y avisa."""
        position = self.sensors["gps"].get_position()
        if position is None or self.navigation_manager.destination is None:
            return

        route = self.navigation_manager.evaluate_route(position)
        if route is None:
            return

        if route["arrived"]:
            self.alert_manager.alert_system("arrived")
        else:
            self.alert_manager.alert_navigation(route["direction"])

    def check_battery(self):
        """Revisa el nivel de bateria cada BATTERY_CHECK_INTERVAL_MS."""
        now_ms = time.ticks_ms()
        elapsed = time.ticks_diff(now_ms, self._last_battery_check_ms)
        if elapsed < self.BATTERY_CHECK_INTERVAL_MS:
            return

        self._last_battery_check_ms = now_ms
        if self.battery_manager.is_low_battery():
            self.alert_manager.alert_system("low_battery")

    def set_destination(self, destination):
        """Permite configurar un destino desde main.py u otra interfaz."""
        self.navigation_manager.set_destination(destination)
