## Índice Maestro – Sistema de DMs de LinkedIn

Última actualización: {{AUTO}}

### Núcleo operativo
- Scripts clave:
  - `Scripts/dm_linkedin_auto_documentation.js` – Genera documentación automática consolidada.
  - `Scripts/dm_linkedin_realtime_metrics.js` – Métricas en tiempo (casi) real desde logs.
  - `Scripts/dm_linkedin_performance_optimizer.js` – Análisis de rendimiento y recomendaciones.

### Documentación y reportes
- Auto-doc generado: `01_Marketing/Reports/dm_linkedin_auto_documentacion.md`
- Guía de automatización: `01_Marketing/dm_linkedin_AUTOMATION_GUIDE.md`
- Índices globales: `indice_navegacion_maestro.md`, `index_dm_outreach.md`

### Datos y fuentes esperadas
- Config: `config.json`
- Variantes: `dm_variants_master.csv` o `DM_Variants_Short.csv`
- Logs de envíos: `Logs/dm_send_log.csv`
- Logs de respuestas: `Logs/dm_responses.csv`

### Ejecución rápida
1) Documentación automática:
   - `npm run dm:docs` (o `node Scripts/dm_linkedin_auto_documentation.js`)
2) Métricas en vivo:
   - `npm run dm:realtime` (o `node Scripts/dm_linkedin_realtime_metrics.js`)
3) Optimización de performance:
   - `npm run dm:optimize` (o `node Scripts/dm_linkedin_performance_optimizer.js`)

### Encabezados mínimos esperados (CSVs)
```
Logs/dm_send_log.csv
timestamp,recipient,variant,campaign,link

Logs/dm_responses.csv
timestamp,recipient,responded,sentiment,variant,campaign
```

### Notas
- Todos los scripts toleran ausencia de archivos y reportan avisos en consola.
- Ajusta rutas en los scripts si moviste `Logs/` o `01_Marketing/Reports/`.

