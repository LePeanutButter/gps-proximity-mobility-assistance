# Operación y mantenimiento

## Objetivo

Documentar cómo operar el prototipo actual y qué medidas de recuperación se aplican ante fallos locales.

## Diagnóstico de fallos comunes

| Problema | Síntoma | Posible causa | Acción |
| --- | --- | --- | --- |
| Lectura de distancia nula | `N/A` en consola | timeout ultrasónico | revisar cableado y pines |
| IR no responde | lectura constante | sensor o conexión inválida | revisar nivel activo y pull-up/pull-down |
| GPS sin posición | `WAIT` o valor no actualizado | sensor no alimentado o NMEA inválido | revisar UART y velocidad |
| Buzzer sin alarma | sin estados de riesgo | conexión, pin o error de lógica | validar GPIO y cabling |
| Loop no avanza | consola se congela | bloqueo de código o sleep prolongado | revisar temporización y condiciones |

## Recuperación después de reinicios

El sistema actual no tiene persistencia ni memoria de contexto. Al reiniciar:

- el firmware vuelve a iniciar desde `main.py`,
- la navegación se reconfigura con el destino fijo,
- se pierde el historial local y la última posición conocida.

Para una evolución posterior se recomienda:

- buffer local limitado,
- log persistente con rollover,
- estado de arranque y último `device_id`,
- reintento de publicación tras recuperación.

## Mantenimiento recomendado

- Validar pines y conexiones al cambiar hardware.
- Verificar que el GPS emita NMEA válido.
- Calibrar distancias operativas según entorno real.
- Mantener registros de pruebas en Wokwi y hardware real.
- Revisar que el firmware no dependa de rutas o archivos inexistentes.

## Mecanismos de salud del sistema

El sistema actual solo expone salud mediante:

- estado del console serial,
- indicador local de buzzer/LED,
- declaración de riesgo según distancia e IR.

Esto es suficiente para prototipo local, pero insuficiente para un entorno operativo desplegado.

## Siguientes pasos para madurez operativa

1. Definir `device_id` y heartbeat.
2. Añadir registro estructurado de eventos.
3. Empezar a publicar y persistir mediciones.
4. Conectar alertas del sistema a CloudWatch o equivalente.
5. Definir políticas de retención y recuperación.
