"""Provider-neutral telemetry transports and MQTT adapter."""

import time


def _ticks_diff(current, previous):
    """Use MicroPython ticks when available and remain host-testable."""
    if hasattr(time, "ticks_diff"):
        return time.ticks_diff(current, previous)
    return current - previous


def _ticks_ms():
    """Return a monotonic millisecond clock on MicroPython or CPython."""
    if hasattr(time, "ticks_ms"):
        return time.ticks_ms()
    return int(time.time() * 1000)


class TelemetryTransport:
    """Interface implemented by local, MQTT, or HTTP transports."""

    def send(self, payload):
        """Return True only when the destination confirms delivery."""
        raise NotImplementedError


class SimulatedTransport(TelemetryTransport):
    """Store payloads locally for demonstrations and deterministic tests."""

    def __init__(self, accept=True, max_payloads=10):
        self.accept = accept
        self._max_payloads = max_payloads
        self.payloads = []

    def send(self, payload):
        """Record an attempted payload and return the configured outcome."""
        if len(self.payloads) >= self._max_payloads:
            self.payloads.pop(0)
        self.payloads.append(payload)
        return self.accept


class MqttConfig:
    """Validated MQTT connection settings without storing any secret values."""

    def __init__(
        self,
        broker,
        port=8883,
        topic=None,
        client_id=None,
        qos=1,
        keepalive=60,
        connect_timeout_ms=5000,
        reconnect_initial_ms=1000,
        reconnect_max_ms=30000,
        username=None,
        password=None,
        ssl=True,
        ssl_params=None,
    ):
        if not broker:
            raise ValueError("MQTT broker is required")
        if not topic:
            raise ValueError("MQTT topic is required")
        if not client_id:
            raise ValueError("MQTT client_id is required")
        if port < 1 or port > 65535:
            raise ValueError("MQTT port is invalid")
        if qos not in (0, 1, 2):
            raise ValueError("MQTT QoS must be 0, 1, or 2")
        if keepalive < 0:
            raise ValueError("MQTT keepalive cannot be negative")
        if connect_timeout_ms < 0:
            raise ValueError("MQTT connect timeout cannot be negative")
        if reconnect_initial_ms < 0 or reconnect_max_ms < reconnect_initial_ms:
            raise ValueError("MQTT reconnect backoff is invalid")
        if (username is None) != (password is None):
            raise ValueError("MQTT username and password must be provided together")

        self.broker = broker
        self.port = port
        self.topic = topic
        self.client_id = client_id
        self.qos = qos
        self.keepalive = keepalive
        self.connect_timeout_ms = connect_timeout_ms
        self.reconnect_initial_ms = reconnect_initial_ms
        self.reconnect_max_ms = reconnect_max_ms
        self.username = username
        self.password = password
        self.ssl = ssl
        self.ssl_params = ssl_params or {}


def default_mqtt_client_factory(config):
    """Create an umqtt.simple client only when a real MQTT transport is used."""
    from umqtt.simple import MQTTClient

    return MQTTClient(
        client_id=config.client_id,
        server=config.broker,
        port=config.port,
        user=config.username,
        password=config.password,
        keepalive=config.keepalive,
        ssl=config.ssl,
        ssl_params=config.ssl_params,
    )


class MqttTransport(TelemetryTransport):
    """Non-blocking MQTT transport compatible with umqtt.simple clients.

    A send call makes at most one connection attempt and one publish attempt.
    Failed attempts schedule a later retry using bounded exponential backoff,
    so sensor acquisition is not held while a broker is unavailable.
    """

    def __init__(
        self,
        config,
        client_factory=default_mqtt_client_factory,
        clock=None,
        logger=None,
        connectivity=None,
    ):
        if not isinstance(config, MqttConfig):
            raise TypeError("config must be an MqttConfig")
        self.config = config
        self._client_factory = client_factory
        self._clock = clock or _ticks_ms
        self._logger = logger or self._default_logger
        self._connectivity = connectivity
        self._client = None
        self._connected = False
        self._next_retry_at = 0
        self._backoff_ms = config.reconnect_initial_ms
        self.connect_attempts = 0
        self.publish_attempts = 0
        self.publish_failures = 0

    @staticmethod
    def _default_logger(level, message):
        print("MQTT {}: {}".format(level, message))

    @property
    def connected(self):
        """Return whether the adapter's last operation established a session."""
        return self._connected

    def send(self, payload):
        """Publish a payload and return true only when the client accepts it."""
        if not isinstance(payload, str):
            raise TypeError("MQTT payload must be a serialized string")
        if not self._ensure_connected():
            self.publish_failures += 1
            return False

        self.publish_attempts += 1
        try:
            result = self._client.publish(
                self.config.topic,
                payload,
                qos=self.config.qos,
                retain=False,
            )
            if result is False:
                raise OSError("MQTT client rejected publish")
            return True
        except (OSError, RuntimeError) as error:
            self.publish_failures += 1
            self._connected = False
            self._schedule_retry()
            self._logger("ERROR", "publish failed: {}".format(error))
            self._safe_disconnect()
            return False

    def disconnect(self):
        """Close the MQTT session and prevent an implicit reconnect."""
        self._safe_disconnect()
        self._connected = False

    def _ensure_connected(self):
        if self._connected:
            return True
        if self._connectivity is not None and not self._connectivity.ensure_connected():
            return False
        now = self._clock()
        if _ticks_diff(now, self._next_retry_at) < 0:
            return False

        self.connect_attempts += 1
        try:
            self._client = self._client_factory(self.config)
            self._client.connect()
            self._connected = True
            self._backoff_ms = self.config.reconnect_initial_ms
            self._logger("INFO", "connected to {}".format(self.config.broker))
            return True
        except (OSError, RuntimeError) as error:
            self._connected = False
            self._schedule_retry()
            self._logger("ERROR", "connection failed: {}".format(error))
            self._safe_disconnect()
            return False

    def _schedule_retry(self):
        self._next_retry_at = self._clock() + self._backoff_ms
        self._backoff_ms = min(
            max(self._backoff_ms * 2, self.config.reconnect_initial_ms),
            self.config.reconnect_max_ms,
        )

    def _safe_disconnect(self):
        if self._client is None:
            return
        try:
            self._client.disconnect()
        except (OSError, RuntimeError) as error:
            self._logger("ERROR", "disconnect failed: {}".format(error))
        finally:
            self._client = None
