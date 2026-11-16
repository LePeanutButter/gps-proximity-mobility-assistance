"""Non-blocking Wi-Fi station management for the ESP32."""

import time


def _ticks_diff(current, previous):
    if hasattr(time, "ticks_diff"):
        return time.ticks_diff(current, previous)
    return current - previous


def _ticks_ms():
    if hasattr(time, "ticks_ms"):
        return time.ticks_ms()
    return int(time.time() * 1000)


class WifiConfig:
    """Validated Wi-Fi settings without exposing credentials in logs."""

    def __init__(
        self,
        ssid,
        password,
        connect_timeout_ms=10000,
        reconnect_initial_ms=1000,
        reconnect_max_ms=30000,
    ):
        if not ssid:
            raise ValueError("Wi-Fi SSID is required")
        if password is None:
            raise ValueError("Wi-Fi password is required")
        if connect_timeout_ms < 0:
            raise ValueError("Wi-Fi connect timeout cannot be negative")
        if reconnect_initial_ms < 0 or reconnect_max_ms < reconnect_initial_ms:
            raise ValueError("Wi-Fi reconnect backoff is invalid")

        self.ssid = ssid
        self.password = password
        self.connect_timeout_ms = connect_timeout_ms
        self.reconnect_initial_ms = reconnect_initial_ms
        self.reconnect_max_ms = reconnect_max_ms


def default_wlan_factory():
    """Create the ESP32 station interface only on the device."""
    import network

    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    return wlan


class WifiManager:
    """Manage station connectivity without sleeping inside sensor cycles."""

    def __init__(
        self,
        config,
        wlan_factory=default_wlan_factory,
        clock=None,
        logger=None,
    ):
        if not isinstance(config, WifiConfig):
            raise TypeError("config must be a WifiConfig")
        self.config = config
        self._wlan_factory = wlan_factory
        self._clock = clock or _ticks_ms
        self._logger = logger or self._default_logger
        self._wlan = None
        self._connecting = False
        self._connect_started_at = 0
        self._next_retry_at = 0
        self._backoff_ms = config.reconnect_initial_ms
        self.connect_attempts = 0
        self.connection_failures = 0

    @staticmethod
    def _default_logger(level, message):
        print("Wi-Fi {}: {}".format(level, message))

    @property
    def connected(self):
        """Return the current station association state."""
        return self._wlan is not None and self._wlan.isconnected()

    def ensure_connected(self):
        """Advance connection state and return whether Wi-Fi is connected."""
        if self.connected:
            self._connecting = False
            self._backoff_ms = self.config.reconnect_initial_ms
            return True

        if self._wlan is None:
            try:
                self._wlan = self._wlan_factory()
            except (OSError, RuntimeError) as error:
                self.connection_failures += 1
                self._schedule_retry()
                self._logger("ERROR", "interface initialization failed: {}".format(error))
                return False

        now = self._clock()
        if self._connecting:
            if _ticks_diff(now, self._connect_started_at) >= self.config.connect_timeout_ms:
                self._connecting = False
                self.connection_failures += 1
                self._schedule_retry()
                self._logger("ERROR", "connection timeout")
            return False

        if _ticks_diff(now, self._next_retry_at) < 0:
            return False

        try:
            self._wlan.connect(self.config.ssid, self.config.password)
            self.connect_attempts += 1
            self._connect_started_at = now
            self._connecting = True
            self._logger("INFO", "connecting to configured SSID")
        except (OSError, RuntimeError) as error:
            self.connect_attempts += 1
            self.connection_failures += 1
            self._schedule_retry()
            self._logger("ERROR", "connection start failed: {}".format(error))
        return self.connected

    def disconnect(self):
        """Disconnect the station interface without logging credentials."""
        if self._wlan is not None:
            self._wlan.disconnect()
        self._connecting = False

    def _schedule_retry(self):
        self._next_retry_at = self._clock() + self._backoff_ms
        self._backoff_ms = min(
            max(self._backoff_ms * 2, self.config.reconnect_initial_ms),
            self.config.reconnect_max_ms,
        )
