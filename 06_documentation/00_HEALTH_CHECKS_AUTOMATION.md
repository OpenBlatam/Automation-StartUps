# 🩺 Health Checks Automáticos (Make → Slack)

## Objetivo
Detectar caídas de performance/errores y alertar a tiempo para evitar daño en KPIs y reputación.

## Checks y Umbrales
- Reply rate (rolling 24h) < 10% → WARN; < 7% → CRITICAL
- Errores/hora (HTTP 4xx/5xx) > 2% → WARN; > 5% → CRITICAL
- 429 consecutivos ≥ 5 en 15 min → CRITICAL (rate limit)
- Mensajes enviados fuera de ventana local > 1% → WARN
- DM→Demo (7d) < 5% → WARN

## Escenario Make: Health Monitor (cada 15 min)
1) Aggregator: leer logs/CRM de últimas 24h (DM_SENT/REPLY/ERROR)
2) Calcular métricas: reply, error rate, 429 streak, DM→Demo 7d
3) Evaluar umbrales → construir payload de alerta
4) Slack: enviar a #sales-ops con severidad y quick actions
5) (Opcional) Crear tarea en HubSpot para revisión si CRITICAL

## Payload Slack (ejemplo)
```
Severidad: CRITICAL
Métrica: 429 consecutivos (7 en 10 min)
Acción: activar backoff y pausar canal LinkedIn 60 min
Link: Dashboard salud | Runbook
```

## Runbook (Acciones por alerta)
- Reply < 7%: pausar variantes de bajo perform, rotar hooks, revisar horarios
- Errores > 5%: revisar credenciales/APIs, reintentos con jitter, DLQ
- 429 streak: activar backoff, reducir envíos 50% por 60 min, alternar canal
- Fuera de ventana: corregir timezone/best_send_hour; auditar 10% de muestra

## Integración de Datos
- Fuente: HubSpot (propiedades y deals) + logs de Make (Data Store/Sheets)
- Identificadores: leadId, dealId, eventId (correlación)

## Buenas Prácticas
- Guardarraíles antes de alertar (filtrar ruido)
- Enlaces en alerta: Dashboard, Runbook, Contact/Deal en CRM
- Revisión semanal de umbrales según baseline
