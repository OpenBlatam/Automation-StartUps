---
title: "Dm Linkedin Compliance Scanner"
category: "01_marketing"
tags: ["business", "marketing"]
created: "2025-10-29"
path: "01_marketing/Other/Social_media/dm_linkedin_compliance_scanner.md"
---

# 🔍 Escáner de Compliance/Voz (Node Sender)

## Qué valida
- Longitud mínima/máxima
- Phrasing de alto riesgo (claims absolutos)
- Presencia de opt-out ("stop")

## Dónde está
- Función `scanMessageCompliance()` en `dm_linkedin_sender_node.js`
- Se ejecuta antes de enviar cada DM
- Si falla: registra `SKIPPED_COMPLIANCE` con razones en logs

## Cómo ajustarlo
- Palabras/regex de riesgo: edita el array `risky` en el script
- Longitudes: ajusta condiciones de 10/1200 caracteres
- Política: revisa `dm_linkedin_compliance_best_practices.md`

## Logs
- Archivo: `dm_linkedin_logs.csv`
- Campos: timestamp, recipient, variant, campaign, status, error
- Errores de compliance aparecen como lista separada por `|`

## Recomendación
- Comienza estricto (más filtros)
- Suaviza tras 1-2 semanas con métricas reales
