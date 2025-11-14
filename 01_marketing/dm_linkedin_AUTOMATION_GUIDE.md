## Guía de Automatización – Sistema de DMs de LinkedIn

### Requisitos
- Node.js 16+ instalado (`node -v`)
- Archivos esperados:
  - `config.json`
  - `dm_variants_master.csv` o `DM_Variants_Short.csv`
  - `Logs/dm_send_log.csv` y `Logs/dm_responses.csv`
  - Opcional: `SLACK_WEBHOOK_URL` para notificaciones

### Setup inicial (1 vez)
```
npm run dm:setup
```
Esto crea `01_Marketing/Reports/` y `Logs/`, y CSVs vacíos si no existen.

### Estructura recomendada de CSVs
```
Logs/dm_send_log.csv
timestamp,recipient,variant,campaign,link
2025-01-01T10:00:00Z,https://linkedin.com/in/user123,V1,CursoIA,https://...utm_source=li

Logs/dm_responses.csv
timestamp,recipient,responded,sentiment,variant,campaign
2025-01-02T11:00:00Z,https://linkedin.com/in/user123,true,positive,V1,CursoIA
```

### Comandos principales
1) Generar documentación automática:
```
node Scripts/dm_linkedin_auto_documentation.js [--no-notify]
```
Salida: `01_Marketing/Reports/dm_linkedin_auto_documentacion.md`

2) Métricas casi en tiempo real:
```
node Scripts/dm_linkedin_realtime_metrics.js [--silent] [--no-notify] [--json]
```
Muestra: enviados, respondidos, últimos 5 envíos, top variantes.

3) Optimización de rendimiento:
```
node Scripts/dm_linkedin_performance_optimizer.js [--silent] [--no-notify] [--json]
```
Muestra: top variantes (>=10 envíos), mejores horas, recomendaciones.

4) Health check (archivos y encabezados):
```
npm run dm:health
```
Valida existencia de `Logs/` y encabezados de `dm_send_log.csv` y `dm_responses.csv`.

5) Archivado/rotación de logs (mensual recomendado):
```
npm run dm:archive
```
Copia los CSV actuales a `Archives/YYYMM/` y reinicia los actuales con solo encabezados.

6) Seed de datos (para pruebas rápidas):
```
SEED_COUNT=200 npm run dm:seed
```
Genera envíos y respuestas sintéticas (con variantes y campañas) para probar métricas y reportes.

7) KPI Snapshot (por rango de fechas):
```
# Markdown a consola
npm run dm:snapshot -- --from=2025-01-01 --to=2025-01-31

# JSON + guardar en archivo
node Scripts/dm_linkedin_kpi_snapshot.js --json --from=2025-01-01 --to=2025-01-31 --out=01_Marketing/Reports/kpi_snapshot_2025_01.json
```
Muestra envíos, respuestas, errores y top campañas para el rango.

8) Detección de anomalías (tasa diaria):
```
npm run dm:anomaly
```
Calcula z-score sobre la tasa de respuesta diaria y alerta por Slack si hay anomalía significativa.

9) Consistency check (variantes/campañas):
```
npm run dm:check
```
Compara variantes definidas (CSV/JSON) vs usadas en logs; lista desconocidas/no usadas y top campañas.

10) Suppression manager (dedupe + listas de supresión):
```
# Entrada/salida personalizadas
node Scripts/dm_linkedin_suppression_manager.js --in=01_Marketing/Recipients.csv --out=01_Marketing/Recipients_clean.csv

# Uso rápido
npm run dm:suppress
```
Elimina duplicados, perfiles en `dm_linkedin_suppression_list.csv` y empresas en `dm_linkedin_company_suppression.csv`.

11) Linter de mensajes (calidad/compliance):
```
# Límite de caracteres y opt-out por variables
LINT_MAX_CHARS=280 LINT_REQUIRE_OPTOUT=1 npm run dm:linter

# Seleccionar archivo de entrada
node Scripts/dm_linkedin_message_linter.js --in=DM_Variants_Short.csv --json
```
Valida longitud, opt-out, placeholders sin resolver y claims riesgosos. Retorna código 1 si hay violaciones.

12) Preflight (validaciones antes de enviar):
```
# Solo validar (salida con código 1 si falla health o linter)
npm run dm:preflight

# Intentar corregir automáticamente (crear carpetas/CSVs y limpiar recipients)
npm run dm:preflight -- --fix
```
Ejecuta: health → linter → consistency (y suppression si --fix). Ideal para CI/CD.

13) Weekly report (últimos 7 días):
```
npm run dm:weekly
# Ruta personalizada
node Scripts/dm_linkedin_weekly_report.js --out=01_Marketing/Reports/weekly_custom.md --no-notify
```
Genera un resumen semanal con KPIs, top variantes/horas y recomendaciones en `01_Marketing/Reports/`.

14) Queue builder (generación de cola de envíos):
```
# Básico
npm run dm:queue

# Inteligente (agrega send_at con mejores horas detectadas)
npm run dm:queue:smart

# Especificar horas manualmente
node Scripts/dm_linkedin_queue_builder.js --schedule --hours=9,11,14 --in=01_Marketing/Recipients_clean.csv --out=01_Marketing/Send_Queue.csv --campaign=curso_ia_q1

# Enrutar por locale (usa columna `locale` o flag `--locale=`)
node Scripts/dm_linkedin_queue_builder.js --locale-route --locale=es-MX

# Evitar fines de semana y días de blackout (YYYY-MM-DD, separados por coma)
node Scripts/dm_linkedin_queue_builder.js --schedule --no-weekend --blackout=2025-12-24,2025-12-25
```
Genera `Send_Queue.csv` con `recipient,variant,campaign` y opcionalmente `send_at`.

15) Queue dry-run (simula envíos y escribe logs):
```
# Semilla cola y simula envíos a 30/min
npm run dm:queue
npm run dm:queue:dryrun

# Personalizar tasa y archivo de cola
DRYRUN_RATE=60 node Scripts/dm_linkedin_queue_dry_run.js --in=01_Marketing/Send_Queue.csv
```
Escribe en `Logs/dm_send_log.csv` con estados SENT/ERROR (simulados) y respeta listas de supresión.

16) Queue validator (calidad de cola antes de enviar):
```
# Validar cola por defecto
npm run dm:queue:validate

# Validar archivo específico y salida JSON
node Scripts/dm_linkedin_queue_validator.js --in=01_Marketing/Send_Queue.csv --json
```
Chequea: URL de LinkedIn válida, variante definida, campaign presente, `send_at` válido/futuro y duplicados recipient+campaign. Sale con código 1 si hay problemas.

17) Queue chunker (dividir cola en partes manejables):
```
# Dividir por campaña en partes de 200
npm run dm:queue:chunk

# Personalizar tamaño, prefijo y carpeta de salida
node Scripts/dm_linkedin_queue_chunker.js --size=150 --prefix=Queue_ --by-campaign --out=01_Marketing/Queues
```
Crea archivos `Send_Queue_part_XXX.csv` (o por campaña) listos para ejecución gradual.

18) Queue retry (reintentos por errores o sin respuesta):
```
# Construir cola de reintentos para elementos con ERROR o sin respuesta >= 7 días
npm run dm:queue:retry

# Personalizar antigüedad y límite de intentos
RETRY_MIN_AGE_DAYS=10 RETRY_MAX_ATTEMPTS=3 node Scripts/dm_linkedin_queue_retry.js --age=10
```
Genera `01_Marketing/Send_Queue_Retry.csv` tomando la última variante enviada por cada recipient+campaign, respetando un máximo de intentos.

19) Opt-out catcher (actualiza listas de supresión desde respuestas):
```
npm run dm:optout
# Personalizar frases de opt-out (regex OR)
OPTOUT_PHRASES="STOP|BAJA|NO CONTACTAR|UNSUBSCRIBE|REMOVE" npm run dm:optout
```
Detecta frases de baja en `dm_responses.csv` y agrega perfiles a `dm_linkedin_suppression_list.csv` y empresas a `dm_linkedin_company_suppression.csv`.

20) Queue cooldown guard (evitar recontacto prematuro):
```
# Filtrar cola para respetar enfriamiento de 7 días desde el último envío
npm run dm:queue:cooldown

# Personalizar ventana
COOLDOWN_MIN_DAYS=10 node Scripts/dm_linkedin_queue_cooldown_guard.js --min-days=10
```
Genera `01_Marketing/Send_Queue_Cooldown.csv` manteniendo solo recipient+campaign cuya última interacción sea ≥ ventana definida.

17) Campaign/Variant Guard (pausa automática por bajo desempeño):
```
# Evaluar últimos 14 días y generar listas de pausa
npm run dm:guard

# Aplicar a la cola actual (filtra campañas/variantes pausadas)
node Scripts/dm_linkedin_campaign_guard.js --apply
```
Umbrales (env): `GUARD_MIN_SENDS` (50), `GUARD_MIN_RESP_RATE` (2%), `GUARD_MAX_ERR_RATE` (10%), `GUARD_DAYS` (14). Genera `paused_campaigns.json` y `paused_variants.json` en `01_Marketing/Reports/` y alerta por Slack si hay pausas.

18) Export CRM (leads desde logs):
```
npm run dm:export:crm
```
Genera un CSV en `01_Marketing/Exports/` con columnas: `recipient,campaign,variant,last_sent_at,status` apto para import a CRM.

### Notificaciones (opcional)
- Exporta una variable de entorno con tu webhook de Slack:
```
export SLACK_WEBHOOK_URL="https://hooks.slack.com/services/..."
```
- Los tres scripts enviarán un resumen al finalizar si la variable está definida.
 - Puedes usar `.env` (copia de `.env.example`).

#### Alertas (umbrales)
Configura umbrales para alertas automáticas en métricas en tiempo real:
```
# Porcentaje mínimo de respuesta antes de alertar (ej. 5)
export ALERT_MIN_RESP_RATE=5
# Porcentaje máximo de errores antes de alertar (ej. 10)
export ALERT_MAX_ERROR_RATE=10
```

### Scheduling (cron)
Ejemplos de cron en macOS/Linux (`crontab -e`):
```
# Docs cada día a las 08:00
0 8 * * * cd /Users/adan/Documents/documentos_blatam && /usr/local/bin/npm run dm:docs

# Realtime cada hora al minuto 5
5 * * * * cd /Users/adan/Documents/documentos_blatam && /usr/local/bin/npm run dm:realtime

# Optimizer diario a las 08:05
5 8 * * * cd /Users/adan/Documents/documentos_blatam && /usr/local/bin/npm run dm:optimize
```

### Buenas prácticas
- Mantén consistentes los `recipient` entre envíos y respuestas.
- Usa UTM en `link` para atribución en dashboards.
- Versiona `dm_variants_master.csv` cuando hagas cambios significativos.

### Solución de problemas
- Si no ves datos: valida rutas y encabezados de CSV.
- Si faltan carpetas: crea `Logs/` y `01_Marketing/Reports/`.
- Archivos grandes: archiva históricos mensualmente para mantener rendimiento.


