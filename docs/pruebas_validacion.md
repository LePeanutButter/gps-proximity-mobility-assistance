# Pruebas y validación

## Estado real del repositorio

El proyecto incluye pruebas host-side con `unittest`. No se requiere una
biblioteca MQTT para ejecutarlas porque el cliente MQTT se inyecta y se simula.

## Validación ejecutada

### Pruebas unitarias de telemetría

```bash
python -m unittest discover -s tests -v
```

Resultado real: **18 pruebas correctas**. Además del modelo de telemetría, se
verifican topic/QoS, reconexión con backoff, errores de publicación y rechazo
de configuraciones MQTT inválidas, conexión Wi-Fi, timeout, reconexión,
configuración incompleta y espera de MQTT mientras Wi-Fi no está disponible.

Se ejecutó la comprobación de sintaxis del código Python del proyecto:

```bash
python -c "import glob, py_compile; [py_compile.compile(f, doraise=True) for f in glob.glob('src/*.py')]"
```

### Resultado

La comprobación terminó correctamente y no reportó errores de sintaxis en los
archivos Python de `src` ni en las pruebas.

## Limitaciones

- No hay pruebas de integración con hardware real ni un broker MQTT real.
- No hay prueba física de asociación Wi-Fi.
- No existe validación cloud real.
- AWS IoT Core y Adafruit IO no se han probado.

## Recomendación

En la siguiente fase del proyecto, añadir pruebas para:

- validación de rangos de sensores,
- serialización JSON,
- manejo de estados de GPS,
- escenarios de pérdida de conexión,
- mensajes duplicados y fuera de orden,
- procesamiento de eventos y alarmas.

## Clasificación final

- Implementadas y verificadas: firmware local, lectura de sensores y navegación básica.
- Implementadas pero no verificadas en hardware real: comportamiento sobre ESP32 físico, GPS real, alertas acústicas en entorno real.
- Implementadas y verificadas: modelo, validación, serialización y transporte simulado.
- Implementadas y verificadas: integración de telemetría con el ciclo real de sensores mediante transporte simulado.
- Pendientes: validación contra broker real, Wi-Fi en ESP32, integración AWS/Adafruit IO, persistence, dashboards y alerting operativos.

La lista reproducible para ejecutar y registrar la prueba física está en
`docs/checklist_prueba_fisica.md`. No se marca como aprobada en este entorno
porque no se dispone de un ESP32 conectado ni de un broker Mosquitto en la red
local.
