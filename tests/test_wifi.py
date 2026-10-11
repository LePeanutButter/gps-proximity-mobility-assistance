import sys
import importlib.util
import tempfile
import unittest
from pathlib import Path


sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from transport import MqttConfig, MqttTransport  # noqa: E402
from telemetry import TelemetryPublisher  # noqa: E402
from device import VisorSense  # noqa: E402
from wifi_manager import WifiConfig, WifiManager  # noqa: E402


class FakeClock:
    def __init__(self):
        self.now = 0

    def __call__(self):
        return self.now


class FakeWlan:
    def __init__(self, connect_error=False):
        self.connected = False
        self.connect_error = connect_error
        self.connect_calls = []
        self.disconnect_calls = 0

    def isconnected(self):
        return self.connected

    def connect(self, ssid, password):
        if self.connect_error:
            raise OSError("network unavailable")
        self.connect_calls.append((ssid, password))

    def disconnect(self):
        self.disconnect_calls += 1
        self.connected = False


class FakeUltrasonic:
    def distance_cm(self):
        return 40


class FakeInfrared:
    def obstacle_detected(self):
        return False


class FakeAlerts:
    def update(self, distance, infrared):
        return "NEAR"


class FakeGps:
    def read_position(self):
        return None


class FakeNavigation:
    def instruction(self, position):
        return "GPS WAIT"


class WifiTests(unittest.TestCase):
    def make_config(self, **overrides):
        values = {
            "ssid": "test-network",
            "password": "not-a-real-password",
            "connect_timeout_ms": 100,
            "reconnect_initial_ms": 50,
            "reconnect_max_ms": 200,
        }
        values.update(overrides)
        return WifiConfig(**values)

    def test_wifi_connection_succeeds_without_logging_password(self):
        wlan = FakeWlan()
        clock = FakeClock()
        logs = []
        manager = WifiManager(
            self.make_config(),
            wlan_factory=lambda: wlan,
            clock=clock,
            logger=lambda level, message: logs.append((level, message)),
        )

        self.assertFalse(manager.ensure_connected())
        self.assertEqual(wlan.connect_calls, [("test-network", "not-a-real-password")])
        wlan.connected = True
        self.assertTrue(manager.ensure_connected())
        self.assertFalse(any("password" in message for _, message in logs))
        self.assertFalse(any("not-a-real-password" in message for _, message in logs))

    def test_wifi_connection_failure_uses_backoff(self):
        wlan = FakeWlan(connect_error=True)
        clock = FakeClock()
        manager = WifiManager(
            self.make_config(),
            wlan_factory=lambda: wlan,
            clock=clock,
        )

        self.assertFalse(manager.ensure_connected())
        self.assertEqual(manager.connect_attempts, 1)
        self.assertFalse(manager.ensure_connected())
        clock.now = 50
        self.assertFalse(manager.ensure_connected())
        self.assertEqual(manager.connect_attempts, 2)

    def test_wifi_recovers_after_timeout_and_retry_window(self):
        wlan = FakeWlan()
        clock = FakeClock()
        manager = WifiManager(
            self.make_config(),
            wlan_factory=lambda: wlan,
            clock=clock,
        )

        self.assertFalse(manager.ensure_connected())
        clock.now = 100
        self.assertFalse(manager.ensure_connected())
        clock.now = 150
        self.assertFalse(manager.ensure_connected())
        wlan.connected = True
        self.assertTrue(manager.ensure_connected())
        self.assertEqual(manager.connection_failures, 1)

    def test_incomplete_wifi_configuration_is_rejected(self):
        with self.assertRaises(ValueError):
            WifiConfig("", "password")
        with self.assertRaises(ValueError):
            WifiConfig("network", None)
        with self.assertRaises(ValueError):
            WifiConfig("network", "password", reconnect_max_ms=10, reconnect_initial_ms=20)

    def test_config_local_overrides_are_loaded(self):
        config_path = Path(__file__).resolve().parents[1] / "src" / "config.py"
        with tempfile.TemporaryDirectory() as directory:
            local_path = Path(directory) / "config_local.py"
            local_path.write_text(
                "WIFI_ENABLED = True\n"
                "WIFI_SSID = 'test-network'\n"
                "WIFI_PASSWORD = 'local-only'\n"
                "MQTT_ENABLED = True\n"
                "MQTT_BROKER = '192.0.2.10'\n",
                encoding="utf-8",
            )
            sys.path.insert(0, directory)
            try:
                spec = importlib.util.spec_from_file_location("config_override_test", config_path)
                module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(module)
            finally:
                sys.path.pop(0)
                sys.modules.pop("config_local", None)

        self.assertTrue(module.mqtt_configuration_complete())
        self.assertEqual(module.WIFI_SSID, "test-network")
        self.assertEqual(module.MQTT_BROKER, "192.0.2.10")

    def test_default_configuration_does_not_enable_mqtt(self):
        config_path = Path(__file__).resolve().parents[1] / "src" / "config.py"
        spec = importlib.util.spec_from_file_location("config_default_test", config_path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)

        self.assertFalse(module.mqtt_configuration_complete())

    def test_empty_wifi_password_does_not_enable_mqtt(self):
        config_path = Path(__file__).resolve().parents[1] / "src" / "config.py"
        with tempfile.TemporaryDirectory() as directory:
            local_path = Path(directory) / "config_local.py"
            local_path.write_text(
                "WIFI_ENABLED = True\n"
                "WIFI_SSID = 'test-network'\n"
                "WIFI_PASSWORD = ''\n"
                "MQTT_ENABLED = True\n"
                "MQTT_BROKER = '192.0.2.10'\n",
                encoding="utf-8",
            )
            sys.path.insert(0, directory)
            try:
                spec = importlib.util.spec_from_file_location("config_empty_password_test", config_path)
                module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(module)
            finally:
                sys.path.pop(0)
                sys.modules.pop("config_local", None)

        self.assertFalse(module.mqtt_configuration_complete())

    def test_mqtt_waits_for_wifi_and_sensor_loop_can_continue(self):
        wlan = FakeWlan()
        clock = FakeClock()
        wifi = WifiManager(
            self.make_config(),
            wlan_factory=lambda: wlan,
            clock=clock,
        )
        mqtt = MqttTransport(
            MqttConfig(
                broker="mqtt.example.invalid",
                topic="visorsense/test",
                client_id="test-client",
            ),
            client_factory=lambda unused_config: None,
            clock=clock,
            connectivity=wifi,
        )

        self.assertFalse(mqtt.send("{}"))
        self.assertEqual(mqtt.connect_attempts, 0)
        self.assertEqual(wifi.connect_attempts, 1)

        device = VisorSense(
            FakeUltrasonic(),
            FakeInfrared(),
            FakeAlerts(),
            FakeGps(),
            FakeNavigation(),
            TelemetryPublisher(mqtt),
            "wifi-offline-device",
        )
        message = device.run_cycle()

        self.assertEqual(message["measurements"]["distance"]["value"], 40)
        self.assertEqual(message["status"]["transmission"], "failed")
