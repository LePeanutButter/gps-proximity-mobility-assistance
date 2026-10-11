# VisorSense

A MicroPython firmware for an ESP32-based obstacle-monitoring and GPS-guidance prototype, designed to run in the Wokwi simulator and on compatible ESP32 hardware.

## Overview

This repository implements a local, self-contained embedded application for:

- obstacle detection using an HC-SR04 ultrasonic sensor
- digital infrared obstruction detection
- GPS-based navigation guidance toward a destination
- local audible/visual alarms through a buzzer and LED
- continuous status monitoring in the serial console

The implementation is intentionally local-first: sensor acquisition, risk assessment, and navigation decisions happen directly on the ESP32 without requiring cloud connectivity or external services.

## Repository structure

| File | Purpose |
| --- | --- |
| `src/main.py` | Runtime entry point and device assembly |
| `src/config.py` | GPIO mappings, thresholds, and simulation settings |
| `src/device.py` | Main orchestration loop and printed status reporting |
| `src/sensors.py` | Sensor abstractions for ultrasonic and IR inputs |
| `src/gps.py` | NMEA GPS parsing and simulated GPS implementation |
| `src/navigation.py` | Simple directional guidance relative to a destination |
| `src/alerts.py` | Buzzer and LED alert patterns by risk level |
| `src/telemetry.py` | Versioned telemetry model, validation, JSON serialization, and counters |
| `src/transport.py` | Provider-neutral transport contract and bounded simulated transport |
| `src/wifi_manager.py` | Non-blocking ESP32 station-mode Wi-Fi management |
| `src/config_local.example.py` | Safe template for untracked device configuration |
| `tests/test_telemetry.py` | Host-side tests for telemetry and device-cycle integration |
| `src/diagram.json` | Wokwi hardware circuit definition |
| `docs/` | Project documentation and architecture analysis |
| `LICENSE` | MIT license |

## Hardware platform

The application targets an ESP32 DevKit C V4 running MicroPython and is compatible with the Wokwi simulator configuration in `src/diagram.json`.

### Default pins

| Signal | ESP32 pin |
| --- | --- |
| HC-SR04 trigger | GPIO25 |
| HC-SR04 echo | GPIO26 |
| Infrared obstacle sensor | GPIO27 |
| Buzzer | GPIO33 |
| LED | GPIO2 |
| GPS TX (ESP32 RX) | GPIO16 |
| GPS RX (ESP32 TX) | GPIO17 |

## Runtime behavior

The device loop in `VisorSense.run_cycle()` performs the following:

1. Measures distance using the ultrasonic sensor.
2. Reads the IR obstacle input state.
3. Updates the buzzer/LED alert state based on risk.
4. Reads the latest GPS position if available.
5. Computes directional guidance toward the configured destination.
6. Prints a compact telemetry summary to the console.

The system exposes status through the serial console and can select a
configurable Wi-Fi-backed MQTT transport when explicitly enabled. Wi-Fi and
MQTT are disabled by default and no cloud endpoint or credentials are
included.

Each monitoring cycle also produces a versioned JSON telemetry message. The
current `SimulatedTransport` confirms local acceptance only; it does not send
data to AWS or Adafruit IO. A future MQTT or REST adapter can implement the
same transport interface without changing sensor or alert logic.

For physical testing, copy `src/config_local.example.py` to
`src/config_local.py`, set the local Wi-Fi and broker values, and transfer the
local file to the ESP32. The local file is ignored by Git and is never required
for the default simulated transport.

## Simulation and testing

The project is designed for Wokwi-based simulation. The `SIMULATION_MODE` flag in `src/config.py` can be used to substitute a fixed simulated GPS position instead of a real NMEA GPS receiver.

The project includes host-side unit tests for telemetry and the MQTT adapter.
There is no cloud deployment automation or real broker integration test.

## Current limitations

This implementation is a prototype and is intentionally limited to local processing. It does not yet include:

- AWS IoT Core or Adafruit IO integration
- cloud ingestion or persistence
- device heartbeat or state registry
- storage of historical measurements
- dashboards with real-time analytics

Telemetry schema validation, JSON serialization, delivery counters, and a
bounded local transport are implemented and covered by host-side tests. Cloud
transport, persistence, dashboards, and remote alerting remain pending.

These limitations are documented in the architecture and diagnostic notes under `docs/`.

## License

[MIT](LICENSE)
