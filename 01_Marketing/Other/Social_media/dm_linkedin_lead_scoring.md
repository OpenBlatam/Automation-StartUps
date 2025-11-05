---
title: "Dm Linkedin Lead Scoring"
category: "01_marketing"
tags: ["business", "marketing"]
created: "2025-10-29"
path: "01_marketing/Other/Social_media/dm_linkedin_lead_scoring.md"
---

# ⭐ Lead Scoring y Priorización (LinkedIn DMs)

## Modelo Simple (inicial)
- SENT: +1
- FAILED: 0
- ERROR: -1
- SKIPPED_*: 0 (no afecta)

Salida: `dm_linkedin_lead_scores.csv` (recipient, score, last_status, last_error, last_timestamp)

Generar:
```bash
cd 01_Marketing
node dm_linkedin_score_from_logs.js
```

## Priorización de Follow-up
- Score ≥ 3 → lista A (follow-up inmediato)
- Score 1-2 → lista B (follow-up estándar)
- Score ≤ 0 → lista C (pausa, revisar calidad)

## Mejoras futuras (si capturas eventos)
- RESPUESTA: +3
- CLIC: +2
- CONVERSIÓN: +5
- OPT-OUT: -5 y mover a supresión 90 días

## Integración con Sheets
- Importa `dm_linkedin_lead_scores.csv` a una hoja
- Usa formato condicional (verde ≥3, amarillo 1-2, rojo ≤0)
- Filtra por fecha (`last_timestamp`) para ver los más recientes

## Reglas de acción
- Lista A: respuesta personalizada en <24h
- Lista B: follow-up de valor (recurso/caso) en 48-72h
- Lista C: revisar mensaje/segmento antes de insistir
