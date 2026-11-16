# Costos y condiciones AWS Free Tier (consulta 2026-10-10)

## Alcance y supuestos

Esta evaluación es informativa y no garantiza costo cero. Se asume
`us-east-1`, una cuenta elegida manualmente, un único ESP32 y mensajes de
telemetría pequeños. La elegibilidad depende del tipo de cuenta, la fecha de
creación, créditos restantes, región, uso acumulado y condiciones vigentes.

No se ejecutaron llamadas AWS ni se creó infraestructura para elaborar este
documento.

## Fuentes oficiales consultadas

- [AWS Free Tier](https://aws.amazon.com/free/) — consultada 2026-10-10.
- [AWS Free Tier FAQs](https://aws.amazon.com/free/free-tier-faqs/) —
  consultada 2026-10-10.
- [AWS Free Tier account documentation](https://docs.aws.amazon.com/awsaccountbilling/latest/aboutv2/free-tier.html) —
  consultada 2026-10-10.
- [AWS IoT Core pricing](https://aws.amazon.com/iot-core/pricing/) —
  consultada 2026-10-10.
- [Amazon S3 pricing](https://aws.amazon.com/s3/pricing/) —
  consultada 2026-10-10.
- [Amazon CloudWatch pricing](https://aws.amazon.com/cloudwatch/pricing/) —
  consultada 2026-10-10.

La página oficial de billing pricing indicada en el requerimiento devolvió
404 durante la consulta; por ello no se usa como fuente de una cifra.

## Condiciones verificadas

La documentación de AWS consultada distingue entre:

- plan Free, orientado a experimentar hasta seis meses o hasta agotar
  créditos, lo que ocurra primero;
- plan Paid, donde el uso que excede créditos u ofertas se factura a las
  tarifas estándar;
- ofertas Always Free y pruebas de duración limitada;
- créditos para cuentas nuevas, cuya elegibilidad y uso dependen del plan y
  condiciones de la cuenta.

AWS no debe considerarse gratuito sólo porque una arquitectura sea pequeña.
Los créditos no son una propiedad universal de cuentas existentes y pueden
expirar o no cubrir un servicio/uso concreto.

## Componentes propuestos y riesgos

| Componente | Uso | Riesgo de costo |
| --- | --- | --- |
| IoT Core | conexión MQTT/TLS y mensajes | minutos conectados, mensajes y tamaño de mensajes |
| S3 | objetos JSON crudos con expiración | almacenamiento, solicitudes, transferencia y funciones de administración |
| IoT Rule | escritura de cada mensaje a S3 | operaciones de reglas y destino S3 |
| CloudWatch Logs | diagnóstico mínimo | ingestión y almacenamiento de logs |
| IAM/Thing/Policy | control de acceso | normalmente no son el principal costo, pero deben revisarse en cuenta real |

La página de IoT Core indica que la conectividad se mide por minutos y que los
mensajes se facturan por uso/tamaño; la tarifa exacta debe confirmarse en la
región y fecha de despliegue. S3 y CloudWatch tienen precios dependientes de
clase, solicitudes, volumen y región. Este repositorio usa retención
configurable y no crea Athena, QuickSight, SageMaker, NAT Gateway, balanceador
ni cómputo permanente.

## Escenarios ilustrativos

Los siguientes son cálculos de volumen, no mediciones ni cotizaciones:

| Escenario | Supuesto | Mensajes/mes | Datos JSON aproximados |
| --- | --- | ---: | ---: |
| Desarrollo | 1 dispositivo, 1 mensaje/minuto, 30 días | 43.200 | 21,6 MB a 500 bytes |
| Integración | 1 dispositivo, 1 mensaje/10 s, 30 días | 259.200 | 129,6 MB a 500 bytes |
| Crecimiento | 10 dispositivos, 1 mensaje/10 s, 30 días | 2.592.000 | 1,30 GB a 500 bytes |

Fórmula:

```text
mensajes = dispositivos × mensajes_por_segundo × 2.592.000
bytes = mensajes × tamaño_promedio
```

No se incluyen overhead MQTT, logs, reintentos, solicitudes S3, conexiones,
transferencia, impuestos ni consultas. El tamaño real debe medirse con los
mensajes publicados.

## Controles de costo

- Mantener frecuencia y tamaño de mensaje configurables.
- Mantener `telemetry_retention_days` bajo y revisarlo antes de aplicar.
- Mantener `cloudwatch_log_retention_days` explícito.
- No habilitar recursos no requeridos.
- Activar alertas y presupuestos manualmente desde Billing and Cost
  Management antes de un despliegue real.
- Revisar Cost Explorer, Free Tier usage y facturación por región.
- Recordar que una alerta presupuestaria no necesariamente bloquea cargos.
- El plan Free puede pausar el proyecto bajo sus condiciones, pero no es un
  sustituto de revisar el consumo ni aplica a todas las cuentas/servicios.

## Estado

No se garantiza elegibilidad Free Tier para esta cuenta ni costo cero. Antes de
`terraform apply`, el operador debe verificar la oferta vigente, cuenta,
región, créditos, precios y límites directamente en AWS.
