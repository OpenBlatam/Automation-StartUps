# 🤖 Automatización Avanzada (Zapier/Make) – 7 Workflows

## Reglas Base
- Respeta `Cadencia_RateLimits.md`
- Usa `DM_Variants_Master.csv` y `DM_Variants_Short.csv`
- Campos clave: `cta_group`, `cta_text`, `experiment_id`, `utm_*`
- Log de pruebas: `CTA_Experimentos_Log.csv`

---

## WF1: Inbound Keyword → Selección de Variante
1) Trigger: IG DM recibido con keyword (p.ej., "WEBINAR")
2) Lookup: CSV maestro WHERE (dm_type, niche, language, cta_group opcional)
3) Compose: mensaje con merge tags ({{first_name}}, {{company}})
4) Acción: Responder DM + adjuntar link con UTM

## WF2: Confirmación + Calendario
1) Trigger: Reply positiva (regex sí/ok/agenda)
2) Generar ICS (ver `ICS_Templates.md`)
3) Enviar DM con ICS + link Zoom
4) Crear evento en Calendar

## WF3: Recordatorios 24h/2h/10m
1) Trigger: Evento programado
2) 24h: DM + WA + Email (si disponible)
3) 2h: DM breve
4) 10m: Último ping

## WF4: Clasificador de Respuestas
1) Trigger: DM entrante
2) Regex buckets: interés, objeción, precio, no-respuesta, opt-out
3) Rama: enviar desde `Respuestas_CopyPaste.md`
4) Log en CRM + etiqueta

## WF5: Ghosting → Escalamiento inteligente
1) Trigger: Sin respuesta 24/48h
2) Seleccionar bump en `Bumps_UltraCortos.md`
3) Escalar a canal alterno (WA/Email) si opt-in
4) Registrar resultado

## WF6: Post-Evento → Oferta 48h
1) Trigger: Asistió (o no)
2) +2h: feedback + recurso
3) +24h: oferta 48h (producto según interés)
4) +48h: cierre final / opt-out

## WF7: Ultra-Cortos por Keyword/Nicho
1) Trigger: DM con keyword (DEMO/RESERVA/SI)
2) Lookup: `DM_Variants_Short.csv` WHERE (offer, niche, language)
3) Enviar texto ultra-corto + `cta_text` + link UTM
4) Log: `CTA_Experimentos_Log.csv`

---

## Ejemplo Filtro por CTA Group (A/B/C)
- Param: `grupo=A|B|C`
- Lookup: CSV maestro WHERE `cta_group={{grupo}}`
- Envío: usar `cta_text` para CTA visible
- Log: (variant_id, cta_group, respuesta, clic)

## Campos UTM
- utm_source: instagram|whatsapp|email|linkedin|telegram
- utm_medium: dm|message|story|post|email
- utm_campaign: webinar_ia|saas_demo|iabulk_demo
- utm_content: {{variant_id}}

## Seguridad y Cumplimiento
- Opt-out claro: "Responde STOP para salir"
- Evitar claims absolutos; siempre "caso real"/"estimado"
- GDPR: no almacenar datos sensibles
