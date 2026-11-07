"""VisorSense device orchestration."""

import time

from telemetry import TelemetryBuilder
from transport import _ticks_diff, _ticks_ms


class VisorSense:
    """Coordinate sensors, alerts, GPS, and basic navigation."""

    def __init__(
        self,
        ultrasonic,
        infrared,
        alerts,
        gps,
        navigation,
        telemetry_publisher=None,
        device_id="visor-esp32-001",
        telemetry_interval_ms=0,
        clock=None,
    ):
        self._ultrasonic = ultrasonic
        self._infrared = infrared
        self._alerts = alerts
        self._gps = gps
        self._navigation = navigation
        self._position = None
        self._telemetry_builder = TelemetryBuilder(device_id)
        self._telemetry_publisher = telemetry_publisher
        self._telemetry_interval_ms = telemetry_interval_ms
        self._clock = clock or _ticks_ms
        self._last_telemetry_at = None

    def run_cycle(self):
        """Execute one monitoring cycle; return the telemetry sent, if any."""
        distance = self._ultrasonic.distance_cm()
        infrared_obstacle = self._infrared.obstacle_detected()

        risk = self._alerts.update(distance, infrared_obstacle)

        new_position = self._gps.read_position()
        if new_position is not None:
            self._position = new_position

        instruction = self._navigation.instruction(self._position)

        self._print_status(distance, infrared_obstacle, risk, instruction, self._position)
        if not self._telemetry_due():
            return None

        self._last_telemetry_at = self._clock()
        # Obstacle alerts must keep running whatever happens to telemetry.
        try:
            self._telemetry_publisher.prepare()
            telemetry = self._telemetry_builder.build(
                distance,
                infrared_obstacle,
                risk,
                instruction,
                self._position,
            )
            self._telemetry_publisher.publish(telemetry)
            return telemetry
        except Exception as error:
            print("Telemetry ERROR: {}".format(error))
            return None

    def _telemetry_due(self):
        if self._telemetry_publisher is None:
            return False
        if self._last_telemetry_at is None:
            return True
        elapsed = _ticks_diff(self._clock(), self._last_telemetry_at)
        return elapsed >= self._telemetry_interval_ms

    @staticmethod
    def _print_status(distance, infrared_obstacle, risk, instruction, position):
        """Print a compact status line for testing and demonstration."""
        if distance is None:
            distance_text = "N/A"
        else:
            distance_text = "{:.1f} cm".format(distance)

        if position is None:
            gps_text = "WAIT"
        else:
            gps_text = "{:.6f}, {:.6f}".format(
                position.latitude,
                position.longitude,
        )

        print(
            "Distance: {} | GPS: {} | IR: {} | Risk: {} | Navigation: {}".format(
                distance_text,
                gps_text,
                "OBSTACLE" if infrared_obstacle else "CLEAR",
                risk,
                instruction,
            )
        )

    def run_forever(self, delay_ms):
        """Run the monitoring loop continuously."""
        while True:
            self.run_cycle()
            time.sleep_ms(delay_ms)
