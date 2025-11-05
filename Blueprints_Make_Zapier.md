# 🧰 Blueprints Make/Zapier (Listos para replicar)

## Make: WF1 Inbound → Respuesta + Tracking
- Trigger: Instagram > Watch Messages
- Router:
  - If text ~ regex optout → Send Opt-out + Tag
  - Else → Classifier (Regex) → Intent
- Tools: CSV > Search Rows (DM_Variants_Master.csv)
- Compose: mensaje (hook/benefit/proof/scarcity + cta_text)
- Action: Instagram > Send Message
- Log: Google Sheets > Append Row (CTA_Experimentos_Log.csv)

## Make: WF2 Confirmación + ICS + Zoom
- Trigger: Label "interés" o texto ~ sí/ok
- Tools: Text aggregator (hora local), HTTP (Zoom/Calendly), Text (ICS)
- Actions: Instagram/WhatsApp/Email send + Google Calendar create

## Zapier: WF5 Ghosting
- Trigger: Delay 24/48h
- Lookup: Bumps_UltraCortos.md (por nicho/idioma)
- Action: Send DM + Update CRM tag

## Campos mínimos por paso
- first_name, language, niche, variant_id, cta_group, utm_*, timezone
