# Monitoreo y alertas

## Estado actual

El repositorio implementa alertas locales visibles en buzzer y LED, pero no cuenta con métricas operativas ni mecanismos de alertas remotas.

## Señales actuales y umbrales

| Condición | Variable | Umbral actual | Acción |
| --- | --- | --- | --- |
| Obstáculo IR | `infrared_obstacle` | Estado lógico según `IR_ACTIVE_LEVEL` | alerta contínua |
| Distancia inmediata | `distance_cm` | `<= 20` | alerta continua |
| Distancia cercana | `distance_cm` | `<= 50` | pulso intermitente |
| Distancia distante | `distance_cm` | `<= 150` | pulso lento |
| Fuera de rango | `distance_cm` | `> 150` | silencio |

## Comportamiento de alarma

La lógica se encuentra en `src/alerts.py`:

- `AlertManager.update()` envía un código de riesgo: `IMMEDIATE`, `NEAR`, `DISTANT`, `NO_READING`, `CLEAR` o `INFRARED`.
- El buzzer y the LED se activan según la severidad.

## Métricas operativas recomendadas

Aunque no están implementadas, estas son las métricas que deberían registrarse en una evolución del sistema:

- mensajes generados / recibidos / descartados
- última lectura recibida por dispositivo
- tiempo desde la última medición
- tasa de errores de sensor
- cantidad de lecturas inválidas
- número de reconexiones
- latencia de publicación
- estado del dispositivo (online/offline)

## Alertas recomendadas en la siguiente fase

| Scenario | Como detectar | Acción |
| --- | --- | --- |
| Dispositivo sin datos | no se reciben mediciones por X minutos | alarma operativa |
| Sensor fuera de rango | valor fuera del umbral físico | registro + alarma |
| Pérdida de conexión | falla de transmisión o heartbeat | alarma y contador |
| Publicación fallida | errores de MQTT/HTTP | reintento + alerta |
| Mensajes duplicados | mismo `sequence_number` repetido | cuarentena y análisis |

## Recomendación de implementación

Para una versión posterior, una combinación de:

- monitoreo local con LED y buzzer,
- almacenamiento de eventos en un registro estructurado,
- alertas cloud en CloudWatch o dashboards equivalentes,

es la ruta menos riesgosa y más mantenible.
