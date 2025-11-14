# Runbook — Curso de IA y Webinars

## P0 — Envíos masivos fallidos
- Síntomas: múltiples errores en confirmaciones/recordatorios/replay
- Acciones:
  1. Pausar Zaps afectados
  2. Revisar límites API y credenciales
  3. Ejecutar rollback de plantillas
  4. Comunicar en Slack #incidentes (ETA ≤ 2h)
  5. Reanudar y monitorizar métricas

## P1 — Certificados duplicados o faltantes
- Síntomas: duplicados en bandeja o estado "pendiente" prolongado
- Acciones:
  1. Desactivar Apps Script de certificados
  2. Limpiar filas afectadas y recomputar idempotencia
  3. Reenviar únicos y registrar JobID
  4. Informe postmortem en 24h

## Validaciones rápidas
- DKIM/SPF ok; cuotas Gmail/Zoom; IDs de plantilla válidos

## Contactos
- Responsable: Operaciones Marketing
- Aprobador: Lead del Curso

