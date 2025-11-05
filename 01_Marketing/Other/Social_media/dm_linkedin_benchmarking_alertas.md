---
title: "Dm Linkedin Benchmarking Alertas"
category: "01_marketing"
tags: ["business", "marketing"]
created: "2025-10-29"
path: "01_marketing/Other/Social_media/dm_linkedin_benchmarking_alertas.md"
---

# 📈 Benchmarking de Variantes + Alertas

## Benchmarks (punto de partida)
- Tasa de respuesta:
  - Excelente: ≥25%
  - Buena: 15-24%
  - Aceptable: 10-14%
  - Riesgo: <10%
- CTR DM:
  - Excelente: ≥20%
  - Bueno: 12-19%
  - Aceptable: 8-11%
  - Riesgo: <8%
- Conversión:
  - Excelente: ≥15%
  - Buena: 8-14%
  - Aceptable: 5-7%
  - Riesgo: <5%
- Bloqueos/Reportes: Riesgo si ≥2%
- Opt-outs: Riesgo si ≥5%

---

## Reglas de alerta (condiciones)
- Alerta Roja: respuesta <10% O bloqueos ≥2%
- Alerta Amarilla: respuesta 10-12% O CTR <8%
- Alerta Verde: respuesta ≥20% Y conversión ≥10%

---

## Scoring simple (0-100)
```
score = (respuesta% * 0.4) + (ctr% * 0.2) + (conversion% * 0.4)
penalización = (bloqueos% * 10) + (optouts% * 5)
score_final = MAX(0, score - penalización)
```

Interpretación:
- 80-100: Escalar
- 60-79: Optimizar
- 40-59: Iterar fuerte
- <40: Pausar

---

## Tabla sugerida (Sheets)
- variante
- enviados
- respuestas
- respuesta%
- clics
- ctr%
- conversiones
- conversion%
- bloqueos%
- optouts%
- score_final
- alerta (Verde/Amarilla/Roja)

---

## Acciones según alerta
- Verde: Escalar + documentar lo que funcionó
- Amarilla: Mejorar hook o CTA + cambiar timing
- Roja: Pausar variante + revisar tono/claims/segmento
