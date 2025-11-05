# Runbook — IA Bulk (3 documentos por consulta)

## P0 — Costos fuera de control
- Síntomas: costo/doc > umbral; picos de tokens
- Acciones:
  1. Pausar trigger time-driven
  2. Bajar modelo/longitud y reintentos diferidos
  3. Notificar a stakeholders (ETA ≤ 1h)
  4. Auditar prompts y plantillas

## P1 — Riesgo legal en outputs
- Síntomas: claims sin fuente, datos sensibles
- Acciones:
  1. Detener distribución automática
  2. Marcar confidencial y enviar a Legal
  3. Ajustar reglas de QA; re-generar si aplica

## Validaciones rápidas
- Idempotencia por hash activa; cuotas dentro de límites
- Logs de JobID, tokens, costo presentes

## Contactos
- Responsable: Content Ops
- Aprobador: Marketing Lead

