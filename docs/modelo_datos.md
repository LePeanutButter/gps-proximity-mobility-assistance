# Modelo de datos

## Alcance actual

El firmware ahora construye y valida un esquema formal de telemetría en
`src/telemetry.py`. El mensaje se serializa a JSON antes de entregarse al
transporte inyectado. La entrega disponible en esta etapa es local y simulada;
no representa una publicación real en AWS o Adafruit IO.

## Sensores actuales y unidades

| Sensor | Variable | Unidad | Rango típico | Estado |
| --- | --- | --- | --- | --- |
| HC-SR04 | distancia | centímetros | 2 a 400 cm | Confirmado |
| IR digital | obstáculo detectado | boolean | 0/1 o True/False | Confirmado |
| GPS NMEA | latitud | grados decimales | -90 a 90 | Confirmado |
| GPS NMEA | longitud | grados decimales | -180 a 180 | Confirmado |

## Estructura implementada

```json
{
  "schema_version": "1.0",
  "device_id": "visor-esp32-001",
  "timestamp": "2026-10-10T12:00:00Z",
  "sequence_number": 12345,
  "measurements": {
    "distance": { "value": 42.5, "unit": "cm", "valid": true },
    "infrared_obstacle": { "value": false, "unit": "bool", "valid": true },
    "latitude": { "value": 4.7110, "unit": "degrees", "valid": true },
    "longitude": { "value": -74.0721, "unit": "degrees", "valid": true }
  },
  "status": {
    "sensor_ok": true,
    "gps_valid": true,
    "wifi_connected": false,
    "transmission": "confirmed"
  },
  "event": {
    "risk": "CLEAR",
    "navigation": "MOVE NORTH"
  }
}
```

`latitude` y `longitude` sólo se incluyen cuando existe una posición GPS
válida. Cuando el ultrasónico no entrega lectura, `distance.value` es `null` y
`distance.valid` es `false`; no se inventa un valor.

## Validaciones implementadas

- Campos obligatorios: `schema_version`, `device_id`, `timestamp`, `measurements`
- Valores numéricos solo cuando se esperen números
- Distancias fuera de `0..400 cm` se rechazan
- Coordenadas fuera de los límites geográficos se rechazan
- Timestamps deben tener formato UTC ISO-8601 terminado en `Z`
- El `sequence_number` incrementa por dispositivo y forma `message_id`
- Cambios incompatibles en el esquema se rechazan por versión

## Política de calidad de datos

- No eliminar un dato sin documentación de la razón.
- Mantener el registro original en caso de invalidación.
- Marcar la medición como `valid`, `invalid`, `missing` o `quarantined`.
- Registrar `reason_code` cuando un valor se rechace.

## Estado de entrega

`TelemetryPublisher` serializa, intenta enviar mediante un transporte y sólo
cuenta una entrega como confirmada cuando `send()` devuelve `True`. Expone los
contadores `generated`, `confirmed` y `failed`. `SimulatedTransport` mantiene
un historial acotado para evitar crecimiento ilimitado de memoria.

La retención, partición y almacenamiento cloud siguen pendientes.
