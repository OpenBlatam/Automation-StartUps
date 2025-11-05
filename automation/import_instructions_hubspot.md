# Import HubSpot – Instrucciones rápidas

1) Crea propiedades personalizadas si faltan (Settings → Properties):
   - producto (single-line)
   - etapa (dropdown)
   - score (number)
   - utm_source / utm_campaign (single-line)
2) Importa CSV Leads (Contacts):
   - Mapea con `automation/crm_field_mapping_hubspot.csv`
3) Crea Listas dinámicas:
   - High-intent: score ≥ 6 AND last_activity_date ≤ 7 días
   - No-asistentes: registró webinar AND no asistencia
4) Workflows (si no usas Zapier/Make):
   - On LM submit → enviar Email 0 → task follow-up 48h
   - On Tripwire purchase → onboarding + oferta Core (72h)
   - On Demo booked → task pre-demo + post-demo email
5) Emails: importa HTML/TXT desde `automation/email_templates_html/*` y `automation/email_templates_text/*`
6) UTM: verifica que los formularios capturen utm_* de `automation/utm_taxonomy.csv`
