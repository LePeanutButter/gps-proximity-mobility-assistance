import json
import sys
import unittest
from pathlib import Path


sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from telemetry import (  # noqa: E402
    TelemetryBuilder,
    TelemetryPublisher,
    TelemetryValidator,
    TelemetryValidationError,
)
from device import VisorSense  # noqa: E402
from transport import SimulatedTransport  # noqa: E402
from transport import MqttConfig, MqttTransport  # noqa: E402


class Position:
    def __init__(self, latitude, longitude):
        self.latitude = latitude
        self.longitude = longitude


class FakeUltrasonic:
    def distance_cm(self):
        return 42.5


class FakeInfrared:
    def obstacle_detected(self):
        return False


class FakeAlerts:
    def update(self, distance_cm, infrared_obstacle):
        return "NEAR"


class FakeGps:
    def read_position(self):
        return Position(4.7, -74.0)


class FakeNavigation:
    def instruction(self, position):
        return "MOVE NORTH"


class FakeClock:
    def __init__(self):
        self.now = 0

    def __call__(self):
        return self.now


class FakeMqttClient:
    def __init__(self, should_connect=True, should_publish=True):
        self.should_connect = should_connect
        self.should_publish = should_publish
        self.connected = False
        self.published = []
        self.disconnects = 0

    def connect(self):
        if not self.should_connect:
            raise OSError("broker unavailable")
        self.connected = True

    def publish(self, topic, payload, qos=0, retain=False):
        if not self.should_publish:
            raise OSError("publish failed")
        self.published.append((topic, payload, qos, retain))

    def disconnect(self):
        self.disconnects += 1
        self.connected = False


def fixed_timestamp():
    return "2026-10-10T23:26:10Z"


class TelemetryTests(unittest.TestCase):
    def make_message(self, distance=42.5, position=None):
        return TelemetryBuilder(
            "visor-test",
            timestamp_factory=fixed_timestamp,
        ).build(distance, False, "CLEAR", "GPS WAIT", position)

    def test_message_contains_versioned_sensor_measurements(self):
        message = self.make_message(position=Position(4.7, -74.0))

        self.assertEqual(message["schema_version"], "1.0")
        self.assertEqual(message["sequence_number"], 1)
        self.assertEqual(message["measurements"]["distance"]["unit"], "cm")
        self.assertEqual(message["measurements"]["latitude"]["value"], 4.7)
        self.assertEqual(message["status"]["wifi_connected"], False)

    def test_serialization_is_valid_json(self):
        message = self.make_message()
        serialized = TelemetryValidator.serialize(message)
        self.assertEqual(json.loads(serialized)["device_id"], "visor-test")

    def test_invalid_distance_is_rejected(self):
        with self.assertRaises(TelemetryValidationError):
            self.make_message(distance=401)

    def test_publisher_counts_confirmation_and_failure(self):
        confirmed_transport = SimulatedTransport(accept=True)
        failed_transport = SimulatedTransport(accept=False)
        confirmed = TelemetryPublisher(confirmed_transport)
        failed = TelemetryPublisher(failed_transport)

        confirmed_message = self.make_message()
        failed_message = self.make_message()

        self.assertTrue(confirmed.publish(confirmed_message))
        self.assertFalse(failed.publish(failed_message))
        self.assertEqual(confirmed.counters(), {
            "generated": 1,
            "confirmed": 1,
            "failed": 0,
        })
        self.assertEqual(failed.counters(), {
            "generated": 1,
            "confirmed": 0,
            "failed": 1,
        })
        self.assertEqual(confirmed_message["status"]["transmission"], "confirmed")
        self.assertEqual(failed_message["status"]["transmission"], "failed")

    def test_simulated_transport_keeps_bounded_history(self):
        transport = SimulatedTransport(max_payloads=1)
        transport.send("first")
        transport.send("second")

        self.assertEqual(transport.payloads, ["second"])

    def test_device_cycle_publishes_existing_sensor_results(self):
        transport = SimulatedTransport()
        publisher = TelemetryPublisher(transport)
        device = VisorSense(
            FakeUltrasonic(),
            FakeInfrared(),
            FakeAlerts(),
            FakeGps(),
            FakeNavigation(),
            publisher,
            "visor-integration",
        )

        message = device.run_cycle()

        self.assertEqual(message["measurements"]["distance"]["value"], 42.5)
        self.assertEqual(publisher.counters()["confirmed"], 1)
        self.assertEqual(len(transport.payloads), 1)
        self.assertEqual(json.loads(transport.payloads[0])["device_id"], "visor-integration")

    def test_mqtt_transport_publishes_with_configured_topic_and_qos(self):
        client = FakeMqttClient()
        clock = FakeClock()
        config = MqttConfig(
            broker="mqtt.example.invalid",
            topic="visorsense/test",
            client_id="test-client",
            ssl=True,
            reconnect_initial_ms=100,
            reconnect_max_ms=1000,
        )
        transport = MqttTransport(
            config,
            client_factory=lambda unused_config: client,
            clock=clock,
        )

        message = self.make_message()
        publisher = TelemetryPublisher(transport)

        self.assertTrue(publisher.publish(message))
        self.assertEqual(client.published[0][0], "visorsense/test")
        self.assertEqual(client.published[0][2], 1)
        self.assertEqual(publisher.counters()["confirmed"], 1)

    def test_mqtt_transport_retries_after_backoff(self):
        clients = [FakeMqttClient(should_connect=False), FakeMqttClient()]
        clock = FakeClock()
        config = MqttConfig(
            broker="mqtt.example.invalid",
            topic="visorsense/test",
            client_id="test-client",
            reconnect_initial_ms=100,
            reconnect_max_ms=1000,
        )
        transport = MqttTransport(
            config,
            client_factory=lambda unused_config: clients.pop(0),
            clock=clock,
        )

        self.assertFalse(transport.send("{}"))
        self.assertEqual(transport.connect_attempts, 1)
        self.assertFalse(transport.send("{}"))
        clock.now = 100
        self.assertTrue(transport.send("{}"))
        self.assertEqual(transport.connect_attempts, 2)

    def test_mqtt_transport_reports_publish_failure(self):
        client = FakeMqttClient(should_publish=False)
        config = MqttConfig(
            broker="mqtt.example.invalid",
            topic="visorsense/test",
            client_id="test-client",
        )
        transport = MqttTransport(
            config,
            client_factory=lambda unused_config: client,
            clock=FakeClock(),
        )

        self.assertFalse(transport.send("{}"))
        self.assertEqual(transport.publish_failures, 1)
        self.assertFalse(transport.connected)
        self.assertEqual(client.disconnects, 1)

    def test_mqtt_config_rejects_invalid_values(self):
        with self.assertRaises(ValueError):
            MqttConfig("", topic="test", client_id="client")
        with self.assertRaises(ValueError):
            MqttConfig("broker", topic="test", client_id="client", qos=3)
        with self.assertRaises(ValueError):
            MqttConfig(
                "broker",
                topic="test",
                client_id="client",
                username="user",
            )


if __name__ == "__main__":
    unittest.main()
