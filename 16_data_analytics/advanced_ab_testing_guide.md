# 🧪 Guía Avanzada de A/B Testing (Outreach)

## Diseño experimental
- Variable única por test (hook, CTA, timing, longitud)
- Tamaño de muestra por variante: ≥100 envíos o hasta CI ±5 p.p.
- Split balanceado por segmento/rol/país (evitar sesgos)

## Poder estadístico (rápido)
- Regla práctica: eventos mínimos (replies) ≥25 por variante
- Duración mínima: 7 días (evitar sesgo de día/hora)
- Evitar “peeking” diario para parar sin evidencia

## Métricas principales
- Reply rate (primaria), Demo rate (secundaria), No-show, Win rate
- Efecto mínimo detectable (EMD): 3–5 p.p. en reply

## Análisis
- IC 95% para diferencia de proporciones (Sheets: `CONFIDENCE.NORM`)
- Aporte por subsegmento (rol/industria) para interacción
- Revisión de entregabilidad (si email) y throttling (si DM)

## Decisiones
- Promover ganador si: IC95% no cruza 0 y ≥3 p.p. lift
- Empate: mantener 50/50 y re-probar con nueva hipótesis
- Perdedor: retirar y registrar aprendizaje

## Operación
- Log en `experiments_ab_log_template.csv`
- Consolidado semanal en `variant_results_rollup_template.csv`
- Alertas si reply 7d < umbral (ver `38_APPS_SCRIPT_ALERTS.md`)

