"""Versioned telemetry model and validation for VisorSense."""

import json
import time


SCHEMA_VERSION = "1.0"
MAX_DISTANCE_CM = 400.0


def utc_timestamp():
    """Return the current UTC time in a compact ISO-8601 representation."""
    now = time.gmtime()
    return "{:04d}-{:02d}-{:02d}T{:02d}:{:02d}:{:02d}Z".format(
        now[0],
        now[1],
        now[2],
        now[3],
        now[4],
        now[5],
    )


class TelemetryValidationError(ValueError):
    """Raised when a telemetry message cannot be accepted."""


class TelemetryBuilder:
    """Build telemetry from the measurements already captured by the device."""

    def __init__(self, device_id, timestamp_factory=utc_timestamp):
        if not device_id:
            raise ValueError("device_id is required")
        self._device_id = device_id
        self._timestamp_factory = timestamp_factory
        self._sequence = 0

    def build(self, distance_cm, infrared_obstacle, risk, instruction, position):
        """Create one validated message without performing network I/O."""
        self._sequence += 1
        message = {
            "schema_version": SCHEMA_VERSION,
            "device_id": self._device_id,
            "timestamp": self._timestamp_factory(),
            "sequence_number": self._sequence,
            "message_id": "{}:{}".format(self._device_id, self._sequence),
            "measurements": {
                "distance": {
                    "value": distance_cm,
                    "unit": "cm",
                    "valid": distance_cm is not None,
                },
                "infrared_obstacle": {
                    "value": infrared_obstacle,
                    "unit": "bool",
                    "valid": True,
                },
            },
            "status": {
                "sensor_ok": distance_cm is not None,
                "gps_valid": position is not None,
                "wifi_connected": False,
                "transmission": "not_attempted",
            },
            "event": {
                "risk": risk,
                "navigation": instruction,
            },
        }
        if position is not None:
            message["measurements"]["latitude"] = {
                "value": position.latitude,
                "unit": "degrees",
                "valid": True,
            }
            message["measurements"]["longitude"] = {
                "value": position.longitude,
                "unit": "degrees",
                "valid": True,
            }

        TelemetryValidator.validate(message)
        return message


class TelemetryValidator:
    """Validate the stable contract before serialization or delivery."""

    @staticmethod
    def validate(message):
        """Raise TelemetryValidationError when required fields are invalid."""
        required = (
            "schema_version",
            "device_id",
            "timestamp",
            "sequence_number",
            "message_id",
            "measurements",
            "status",
            "event",
        )
        for field in required:
            if field not in message:
                raise TelemetryValidationError("missing field: {}".format(field))

        if message["schema_version"] != SCHEMA_VERSION:
            raise TelemetryValidationError("unsupported schema version")
        if not isinstance(message["device_id"], str) or not message["device_id"]:
            raise TelemetryValidationError("invalid device_id")
        if (
            not isinstance(message["timestamp"], str)
            or len(message["timestamp"]) != 20
            or message["timestamp"][-1] != "Z"
        ):
            raise TelemetryValidationError("timestamp must be UTC ISO-8601")
        if not isinstance(message["sequence_number"], int):
            raise TelemetryValidationError("invalid sequence_number")

        measurements = message["measurements"]
        distance = measurements.get("distance")
        if distance is None or distance.get("unit") != "cm":
            raise TelemetryValidationError("distance measurement is required")
        distance_value = distance.get("value")
        if distance_value is not None and (
            not isinstance(distance_value, (int, float))
            or distance_value < 0
            or distance_value > MAX_DISTANCE_CM
        ):
            raise TelemetryValidationError("distance is outside physical range")

        infrared = measurements.get("infrared_obstacle")
        if infrared is None or not isinstance(infrared.get("value"), bool):
            raise TelemetryValidationError("invalid infrared measurement")

        for coordinate in ("latitude", "longitude"):
            measurement = measurements.get(coordinate)
            if measurement is None:
                continue
            value = measurement.get("value")
            limits = (-90, 90) if coordinate == "latitude" else (-180, 180)
            if not isinstance(value, (int, float)) or value < limits[0] or value > limits[1]:
                raise TelemetryValidationError("{} is outside geographic range".format(coordinate))

        status = message["status"]
        for field in ("sensor_ok", "gps_valid", "wifi_connected"):
            if not isinstance(status.get(field), bool):
                raise TelemetryValidationError("invalid status: {}".format(field))

    @staticmethod
    def serialize(message):
        """Validate and serialize a message for a future MQTT/HTTP adapter."""
        TelemetryValidator.validate(message)
        return json.dumps(message, separators=(",", ":"))


class TelemetryPublisher:
    """Deliver telemetry through an injected transport and expose counters."""

    def __init__(self, transport):
        self._transport = transport
        self.generated = 0
        self.confirmed = 0
        self.failed = 0

    def publish(self, message):
        """Attempt delivery and return True only on transport confirmation."""
        message["status"]["transmission"] = "pending"
        payload = TelemetryValidator.serialize(message)
        self.generated += 1
        delivered = self._transport.send(payload)
        if delivered:
            self.confirmed += 1
            message["status"]["transmission"] = "confirmed"
            return True

        self.failed += 1
        message["status"]["transmission"] = "failed"
        return False

    def counters(self):
        """Return a copy of delivery counters for diagnostics."""
        return {
            "generated": self.generated,
            "confirmed": self.confirmed,
            "failed": self.failed,
        }
