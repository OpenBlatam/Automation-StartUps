# ✅ Go/No-Go & Rollback Criteria

Ventana de evaluación: 7/14/30 días.

Go (promover):
- Reply 7d ≥ objetivo (DM ≥12%, Email ≥4%)
- Demo rate ≥20% de replies
- No-show ≤20%
- Lift vs baseline ≥3 p.p. en reply

No-Go (pausar y revisar):
- Reply 7d < umbral (ver `config_template.csv`)
- 2+ métricas bajo umbral simultáneamente
- Señales de fatiga (unsubscribe/negative feedback ↑)

Rollback inmediato:
- Entregabilidad crítica (bounce >5% en email)
- Bloqueos/suspensiones en canal
- Error de segmentación/compliance

Acciones:
- Documentar en `experiments_ab_log_template.csv`
- Ajustar hipótesis (hook, CTA, timing, segmento)
- Re-lanzar piloto controlado tras corrección

