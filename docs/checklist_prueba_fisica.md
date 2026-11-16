# Checklist de prueba física: ESP32 -> Wi-Fi -> Mosquitto

Esta lista registra una prueba de laboratorio. No debe marcarse como aprobada
sin observar el resultado en el hardware y en el suscriptor MQTT.

## Preparación

- [ ] ESP32 identificado y alimentado de forma estable.
- [ ] MicroPython instalado y versión registrada: `________________`.
- [ ] Sensor HC-SR04 conectado a GPIO25/GPIO26.
- [ ] Sensor IR conectado a GPIO27.
- [ ] Buzzer conectado a GPIO33.
- [ ] LED conectado a GPIO2.
- [ ] GPS conectado si se probará posición real.
- [ ] `umqtt.simple` compatible copiado al ESP32.
- [ ] `config_local.py` creado desde `config_local.example.py`.
- [ ] `config_local.py` no contiene credenciales en el repositorio.

## Computadora y broker

- [ ] Mosquitto instalado.
- [ ] IP LAN de la computadora identificada: `________________`.
- [ ] Red de prueba seleccionada: `________________`.
- [ ] Puerto 1883 permitido sólo desde la red de laboratorio.
- [ ] Regla temporal de firewall registrada y limitada a esa red.
- [ ] Broker iniciado con:

  ```text
  mosquitto -v -p 1883
  ```

- [ ] Suscriptor iniciado con la IP LAN del equipo:

  ```text
  mosquitto_sub -h IP_LAN_DEL_BROKER -p 1883 -t visorsense/telemetry -v
  ```

No usar `127.0.0.1` en la configuración del ESP32: allí significa el propio
ESP32, no la computadora.

## Configuración del ESP32

- [ ] `WIFI_ENABLED = True`.
- [ ] SSID configurado localmente.
- [ ] Contraseña configurada localmente y no registrada en logs.
- [ ] `MQTT_ENABLED = True`.
- [ ] `MQTT_BROKER` contiene la IP LAN de la computadora.
- [ ] `MQTT_PORT = 1883`.
- [ ] `MQTT_TLS = False` sólo para esta red de laboratorio aislada.
- [ ] `MQTT_TOPIC = "visorsense/telemetry"`.
- [ ] `MQTT_CLIENT_ID` es único.
- [ ] `SIMULATION_MODE` registrado como `True` o `False`: `________`.

## Ejecución y observación

- [ ] Archivos cargados en el ESP32.
- [ ] `main.py` ejecutado sin excepción de importación.
- [ ] Consola muestra `Wi-Fi INFO: connecting to configured SSID`.
- [ ] Consola muestra asociación exitosa o el estado equivalente del puerto.
- [ ] Consola muestra `MQTT INFO: connected`.
- [ ] El suscriptor recibe al menos un JSON.
- [ ] El JSON contiene `schema_version`.
- [ ] El JSON contiene `device_id` esperado.
- [ ] El JSON contiene `timestamp` terminado en `Z`.
- [ ] `distance` contiene unidad `cm`.
- [ ] `infrared_obstacle` contiene unidad `bool`.
- [ ] La distancia corresponde a una lectura real del HC-SR04.
- [ ] El estado GPS coincide con la disponibilidad real del GPS.
- [ ] Se verificó que no aparecen contraseñas, claves ni certificados en consola.

## Recuperación

- [ ] Se apagó temporalmente el broker.
- [ ] El ciclo de sensores continuó ejecutándose.
- [ ] Se observaron errores MQTT sin reinicios agresivos.
- [ ] Se inició nuevamente el broker.
- [ ] El ESP32 recuperó la conexión después del backoff.
- [ ] El suscriptor volvió a recibir mensajes.

## Resultado

- Fecha/hora: `________________`
- Firmware commit/version: `________________`
- Resultado: `PENDIENTE / APROBADO / FALLIDO`
- Observaciones: `________________________________________________________`
- Evidencia o captura: `__________________________________________________`

Esta checklist no demuestra compatibilidad con AWS IoT Core, Adafruit IO ni
TLS de producción. Es únicamente una validación local de conectividad.
