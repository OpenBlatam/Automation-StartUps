# Documentos BLATAM — Automatizaciones IA

Versión: v1.0.3  ·  Última actualización: 2025-10-30

## Índice
- Curso de IA y Webinars: `curso-ia-webinars.md`
- SaaS IA para Marketing: `saas-ia-marketing.md`
- IA Bulk (3 documentos por consulta): `ia-bulk-3docs.md`
- Runbooks: `runbook-curso-webinars.md`, `runbook-saas-marketing.md`, `runbook-ia-bulk.md`
- Plantillas CSV: `asistencia.csv`, `pedidos.csv`, `costosIA.csv`, `leads.csv`
- Kanban CSV: `kanban_automatizaciones.csv`
- Postman Collection: `ia_automation_collection.postman_collection.json`
- Quickstart y configuración: `QUICKSTART.md`, `SHEETS_SETUP.md`, `CREDENTIALS_CHECKLIST.md`, `ENV-PLANTILLA.env`
- Plantillas y prompts: `PLANTILLAS_COMUNICACION.md`, `PROMPTS_BASE.md`

## Orden de despliegue sugerido
1) Curso/Webinars: registro→recordatorios→replay→certificados→NPS
2) SaaS: dunning + suspensión/reactivación → enriquecimiento + scoring → reportes → soporte IA
3) IA Bulk: lote 3-docs → QA semántico → distribución → costos
4) Dashboards, SLAs/SLOs, alertas y hardening (idempotencia, rate limit)

## Requisitos previos
- Accesos: Zoom, Gmail/Calendar, Stripe, CRM, Twilio, Drive/Docs, OpenAI
- Plantillas e IDs definidos en cada documento
- Google Sheets creadas desde los CSV provistos

## Métricas clave (resumen)
- No-show ≤ 25%, Certificados T95 ≤ 2h, Recovery ≥ 35%, FCR IA ≥ 40%, Éxito lotes ≥ 90%, Costo/doc ≤ $0.12

## Contactos (roles sugeridos)
- Aprobadores: Lead del Curso, Head of Growth, Marketing Lead
- Responsables: Operaciones Marketing, RevOps, Content Ops
- Soporte: Ingeniería, Soporte, Legal, Finanzas

