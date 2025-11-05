# 🧪 Primera Corrida E2E (3 Leads de Prueba)

## Preparación (10 min)
- [ ] Completar `.env` con claves (ver `00_ENV_EXAMPLE.env`).
- [ ] Crear propiedades en HubSpot (usar `00_HUBSPOT_PROPERTY_DEFINITIONS.json`).
- [ ] Importar `00_MAKE_SCENARIO_BLUEPRINT.json` en Make y setear variables.
- [ ] Crear base en Airtable/Notion con `00_DASHBOARD_TEMPLATE_AIRTABLE.md` (opcional).

## Cargar 3 leads (5 min)
- [ ] Duplicar `00_CSV_IMPORT_CONTACTS_SAMPLE.csv` → `contacts_test.csv` y editar 3 filas reales.
- [ ] Importar en HubSpot y verificar propiedades pobladas.

## Escenario 1: Conexión → DM (15 min)
- [ ] Disparar escenario con 1 lead (mock o conexión real).
- [ ] Validar: contacto en CRM, `dm_variant`, `lead_score`, `channel`, `language`, `best_send_hour`.
- [ ] QA de marca: revisar 1 DM (tono, CTA con 2 horarios).

## Escenario 2: 48h sin respuesta → Seguimiento (simulado) (5 min)
- [ ] Cambiar reloj del escenario o marcar lead como no respondido.
- [ ] Validar que se envía Seguimiento 1 y se loguea evento.

## Escenario 3: Respuesta positiva → Demo y Deal (10 min)
- [ ] Simular reply positivo.
- [ ] Validar creación de Deal (stage "Demo Booked") + `demo_booked_at`.

## Escenario 4: Post‑Demo → Propuesta (10 min)
- [ ] Simular "Demo Completed".
- [ ] Generar propuesta usando `00_CONTRATO_OUTCOME_TEMPLATE.md` + `00_CALCULADORA_ROI.md`.
- [ ] Enviar y crear tarea de cierre +7 días.

## Métricas y Reporte (10 min)
- [ ] Capturar reply rate, DM→Demo y tiempos en dashboard.
- [ ] Documentar decisiones (duplicar/pausar) en `00_CHECKLIST_OPERATIVO_SEMANAL.md`.

## Criterios de Éxito
- [ ] 1 DM enviado con QA ✓
- [ ] 1 Seguimiento programado ✓
- [ ] 1 Demo creada (deal) ✓
- [ ] 1 Propuesta enviada ✓

## Siguientes Pasos
- [ ] Escalar a 10 leads y activar cadencia semanal.
- [ ] Ajustar prompts con aprendizajes de la corrida.
