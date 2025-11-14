# 📈 Plan de Escalamiento por Fases (4 Semanas)

## Objetivo
Escalar envíos manteniendo calidad (QA), cumplimiento y KPIs mínimos.

## Semana 1 — Foundation (Manual + Semi-Automático)
- Volumen: 15–25 DMs/día
- Personal: 1 owner (0.5 FTE)
- Enfoque: validar prompts, horarios y canal ganador por vertical
- QA: 25% de muestras; checklist de marca
- KPIs meta: Reply ≥ 15%, DM→Demo ≥ 5%
- Riesgos: drift de tono → Mitigación: revisión diaria + changelog

## Semana 2 — Optimization (Semi-Auto + Follow-ups)
- Volumen: 40–60 DMs/día
- Personal: 1 owner + 1 apoyo QA (0.2 FTE)
- Enfoque: activar Seguimiento 1; A/B en 2 variantes top
- QA: 15% de muestras; rollback si reply < 12%
- KPIs meta: Reply ≥ 18%, DM→Demo ≥ 6%
- Riesgos: bloqueos canal → Mitigación: rate limits y alternar canal

## Semana 3 — Scaling (Automatizado controlado)
- Volumen: 80–120 DMs/día
- Personal: 1 owner + 1 QA compartido (0.2 FTE)
- Enfoque: scoring v2, horarios por timezone, objeciones top
- QA: 10% de muestras; alertas de salud activas (errores, 429, reply<10%)
- KPIs meta: Reply ≥ 20%, DM→Demo ≥ 7%, Demo→Win ≥ 22%
- Riesgos: fatiga → Mitigación: rotar hooks/verticales semanalmente

## Semana 4 — Scale-Up (Operación estable)
- Volumen: 150–250 DMs/día
- Personal: 1 owner + 1 QA (0.3 FTE) + soporte de datos (0.1 FTE)
- Enfoque: outcome pricing pilots, partners, bundles por vertical
- QA: 10% de muestras; auditoría semanal de privacidad
- KPIs meta: Reply ≥ 22%, DM→Demo ≥ 8%, Demo→Win ≥ 25%
- Riesgos: caída de calidad → Mitigación: circuit breaker y hardening

## Cadencia de Gestión
- Diario: 15 min salud (alertas, errores, reply por canal)
- Semanal: 30 min aprendizaje (duplicar/pausar/testear)
- Mensual: pricing/membresías, partners, casos públicos

## Reglas Go/No-Go por Fase
- Avanza si: KPIs meta alcanzados 5/7 días y errores < 2%/h
- Mantén si: 1 KPI bajo pero en recuperación (<1 semana)
- Retrocede si: 2+ KPIs bajo meta 3 días seguidos o alertas críticas

## Recursos y Herramientas
- Make/Zapier (workflows), HubSpot/Salesforce (CRM), Airtable/Notion (dashboard)
- Referencias: `00_HARDENING_CHECKLIST.md`, `00_AUTOMATIONS_BLUEPRINTS.md`, `00_CHECKLIST_OPERATIVO_SEMANAL.md`
