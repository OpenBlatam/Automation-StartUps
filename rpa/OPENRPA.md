# OpenRPA / OpenFlow

- Server: OpenFlow (API/broker) recomendado para coordinar bots; despliegue en Kubernetes (imagen docker oficial), con base de datos (MongoDB) para persistencia.
- Bots: OpenRPA en estaciones/VMs; comunican con OpenFlow vía WebSocket/API.
- Integración:
  - Dispare bots desde Kestra o Flowable vía HTTP/Webhook a OpenFlow.
  - Use Kafka para eventos y correlación de ejecuciones.
- Seguridad: OIDC en el gateway + mTLS si expone OpenFlow externamente.
- Observabilidad: emita métricas/logs a Prometheus/ELK; traceo opcional con OpenTelemetry.


