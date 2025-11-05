---
title: "20 Crm Integrations Playbook"
category: "20_crm_integrations_playbook.md"
tags: []
created: "2025-10-29"
path: "20_crm_integrations_playbook.md"
---

# 🔗 CRM Integrations Playbook

## 📑 ÍNDICE

- [🏗️ Arquitectura de Datos](#️-arquitectura-de-datos)
- [🗺️ Mapeos (DMs → CRM)](#️-mapeos-dms--crm)
- [⚙️ Automatizaciones Clave](#️-automatizaciones-clave)
- [🧪 Tracking y Atribución](#-tracking-y-atribución)
- [📤 Pipelines de Export/Import](#-pipelines-de-exportimport)
- [🔐 Compliance y Seguridad](#-compliance-y-seguridad)

---

## 🏗️ ARQUITECTURA DE DATOS

### Objetos base
- `Lead`: persona/empresa objetivo
- `Interaction`: DM/Email/Call con metadata
- `Meeting`: demo agendada, show/no-show
- `Deal/Opportunity`: pipeline por producto
- `Account`: empresa (B2B)

### Campos recomendados
- `lead.source`: linkedin/email/referral
- `lead.product_interest`: curso/marketing/docs
- `lead.industry`, `lead.company_size`
- `lead.lead_score` (numérico)
- `interaction.channel`: linkedin/email/whatsapp
- `interaction.variant`, `interaction.personalization_level`
- `meeting.no_show_reason`
- `deal.use_case`: monetización/roas/docs

---

## 🗺️ MAPEOS (DMs → CRM)

| Origen | Campo | CRM (ej.) |
|--------|-------|-----------|
| DM enviado | channel | Interaction.channel |
| DM enviado | variant | Interaction.variant |
| DM enviado | personalization_level | Interaction.personalization_level |
| Respuesta | reply_type | Interaction.reply_type |
| Demo agendada | date | Meeting.scheduled_at |
| Demo asistida | attended | Meeting.attended |
| Oferta | monto | Deal.amount |
| Cierre | won/lost | Deal.closed_won |

Reglas:
- Un `Lead` por persona; agrupar bajo `Account`
- Encadenar `Interaction` → `Meeting` → `Deal`
- Mantener `product_interest` y `use_case` actualizados

---

## ⚙️ AUTOMATIZACIONES CLAVE

1) Auto lead scoring
- +3 si reply positiva
- +2 si DM con métrica pública citada
- +2 si perfil match (industria/tamaño)
- +1 si actividad reciente <7 días
- -2 si reply negativa

2) Auto follow-up tasks
- Sin respuesta 48h → crear tarea LKD bump
- No-show → tarea reprogramar en 24h
- Reply "info" → enviar secuencia email #2

3) Auto-stage deals
- Reply positiva + demo agendada → Stage: Discovery
- Demo realizada + interés → Stage: Proposal
- Piloto aceptado → Stage: Pilot

---

## 🧪 TRACKING Y ATRIBUCIÓN

UTM/Params sugeridos (para links):
- `utm_source=linkedin|email|whatsapp`
- `utm_campaign=dm_outreach_vX`
- `utm_content=variant_A|B|C`
- `lead_id=<id>`

Atribución simple
- First-touch: primer canal con interacción
- Last-touch: canal previo a demo
- Assisted: múltiples canales en 14 días

Dashboards sugeridos
- Conversión por canal y variante
- Time-to-meeting y time-to-close
- Reply→Demo→Close por producto

---

## 📤 PIPELINES DE EXPORT/IMPORT

Export (semanal)
- Leads nuevos con score ≥6
- Interactions de últimos 30 días
- Meetings y outcomes de semana
- Deals creados/ganados/perdidos

Import (diario)
- Respuestas desde inbox/email parser
- Demos desde calendario
- Deals desde facturación (monto real)

Formatos
- CSV/Parquet para batch
- Webhooks/REST para tiempo real

---

## 🔐 COMPLIANCE Y SEGURIDAD

- GDPR/CCPA: opt-out claro y registro
- Minimizar PII: solo datos necesarios
- Encriptar datos sensibles en tránsito/descanso
- Roles y permisos por equipo (ventas/marketing)
- Retención: borrar/anonimizar a 12-18 meses

---

**FIN DEL DOCUMENTO**



