# 📚 Data Dictionary — Eventos y Propiedades

## Eventos (mínimos)
- DM_SENT
  - channel (enum): LinkedIn | Email | WhatsApp
  - variant (enum): A..F
  - language (enum): es | en | pt
  - sendHourLocal (int 0-23)
  - leadScore (0-10)
- DM_REPLY
  - replyAt (datetime)
  - sentiment (enum): positive | neutral | negative
- DEMO_BOOKED
  - demo_booked_at (datetime)
  - durationMin (int)
- DEAL_WON
  - amount (currency)
  - currency (string)
- DEAL_LOST
  - reason (enum): timing | presupuesto | competidor | tono | otros

## Propiedades (Contact)
- dm_variant (enum A..F): última variante usada
- lead_score (0-10): puntaje de priorización
- best_send_hour (0-23): hora local con mejor perform
- primary_objection (enum): objeción más frecuente
- channel (enum): canal preferente
- industry (string)
- language (enum)
- timezone (string IANA)

## Propiedades (Deal)
- demo_booked_at (datetime)
- outcome_pricing (bool)
- package_tier (enum)
- mrr_delta_expected (currency)
- kpi_baseline (number)
- kpi_target (number)

## Métricas Derivadas (definiciones)
- reply_rate = replies / DMs_enviados
- dm_to_demo = demos / replies
- demo_to_win = wins / demos
- time_to_reply_min = replyAt − sentAt (min)
- roi_variante = ingresos_atrib − costo_tiempo

## Estándares
- snake_case para integraciones
- Enums documentados aquí son fuente de verdad
- No registrar PII en logs (ofuscar email)
