# ⚙️ Blueprints de Automatización (Make/Zapier)

## Workflow 1: Nueva conexión LinkedIn → DM Variante + CRM + Follow-up
- Trigger: New LinkedIn Connection (Sales Navigator/Phantombuster)
- Steps:
  1) Enriquecer (Apollo/Hunter/Clearbit) → industry, companySize, email.
  2) Score (rule-set) → set lead_score.
  3) Seleccionar dm_variant por score/industria.
  4) Generar DM (OpenAI/Claude) usando plantilla.
  5) Enviar por canal (LI/Email) con ventana horaria local.
  6) Crear/actualizar contacto en CRM con propiedades del YAML.
  7) Programar task follow-up 48h.

## Workflow 2: 48h sin respuesta → Seguimiento y cambio de canal
- Trigger: 48h desde DM_SENT y DM_REPLY = false
- Steps: Enviar Seguimiento 1, actualizar primary_objection si responde, reprogramar segundo follow-up a 5 días, alternar canal si aplica.

## Workflow 3: Respuesta positiva → Demo y Deal
- Trigger: DM_REPLY con intención positiva
- Steps: Enviar enlace Calendly, crear Deal (stage "Demo Booked"), set demo_booked_at, notificar a Sales, checklist pre-demo.

## Workflow 4: Post-Demo → Propuesta automática y Tarea de Cierre
- Trigger: Event "Demo Completed"
- Steps: Generar propuesta con 00_CONTRATO_OUTCOME_TEMPLATE.md + 00_CALCULADORA_ROI.md, enviar, crear tarea de cierre a 7 días.

## Guardarraíles
- Límite de envíos/día por canal, lista de exclusión, horarios locales, muestreo QA 10%.

## Métricas (enviar a BI)
- Por evento: variant, canal, hora local, lead_score, reply, time_to_reply, demo, win.

