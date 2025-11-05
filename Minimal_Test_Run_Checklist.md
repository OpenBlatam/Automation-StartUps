## Checklist de Prueba Mínima (5-10 minutos)

1) Datos de prueba
- [ ] 3 leads ficticios con `first_name`, `niche`, `lang`, `thread_id`
- [ ] 2 variantes en `DM_Variants_Master.csv` con `cta_group` A/B

2) Clasificador
- [ ] Probar 4 textos (optout/interes/objecion/no_ahora) con `Reply_Classifier_TestSet.csv`
- [ ] Confirmar bucket correcto en log (Sheets/Logger)

3) Rate-limit
- [ ] Set `desired_rate_per_hour=4` y observar sleeps de 30–60s
- [ ] Forzar cap horario y ver sleep 120–180s

4) Envío y UTM
- [ ] Componer mensaje con UTM from `UTM_Builder.md`
- [ ] Enviar a sandbox/propio IG y validar recepción

5) Logging
- [ ] Append en `CTA_Experimentos_Log.csv` (sent=1, variant_id, cta_group)
- [ ] Registrar respuesta manual y verificar métricas en `KPI_Dashboard_Template_Enhanced.csv`

6) Ultra-corto
- [ ] Probar mensaje <=140c y validar guardas

7) ICS/Confirmación (opcional)
- [ ] Generar ICS desde `ICS_Templates.md` y enviar por canal alterno

