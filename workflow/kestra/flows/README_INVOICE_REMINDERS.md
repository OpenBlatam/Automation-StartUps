# Recordatorios de Cobranza de Facturas Vencidas

## Descripción

Sistema automatizado de recordatorios de cobranza para facturas vencidas que **reduce la morosidad y mejora significativamente el flujo de caja**.

### Características Principales

- ✅ **Recordatorios escalonados** según días de vencimiento
- ✅ **Validación robusta** de inputs y datos
- ✅ **Prevención de duplicados** - evita enviar el mismo recordatorio dos veces
- ✅ **Mensajes HTML profesionales** con estilos CSS integrados
- ✅ **Multi-canal** - Email, Slack, WhatsApp (opcional)
- ✅ **Escalación automática** a gerencia/finanzas
- ✅ **Análisis de efectividad** - tracking de qué funciona mejor
- ✅ **Análisis de tendencias** - comparación día a día
- ✅ **Exportación de reportes** CSV/JSON (opcional)
- ✅ **Health checks** automáticos con alertas
- ✅ **Logging estructurado** integrado con métricas
- ✅ **Rate limiting inteligente** para prevenir sobrecarga
- ✅ **Optimización batch** de base de datos

## Mejoras Implementadas

### v2.0 - Fundamentos Sólidos
- Validación robusta
- Prevención de duplicados
- Mensajes HTML profesionales
- Optimizaciones básicas de BD

### v3.0 - Funcionalidades Avanzadas
- Notificaciones WhatsApp para críticas
- Escalación automática
- Análisis de efectividad
- Análisis de tendencias

### v3.5 - Optimizaciones
- Rate limiting inteligente
- Batch processing optimizado
- Métricas de performance
- Recomendaciones automáticas

### v4.0 - Observabilidad y Exportación (NUEVO) 🚀

#### 📊 Logging Estructurado
- Integración con `subflow_metrics_logger`
- Métricas exportables a sistemas de observabilidad
- Labels detallados para filtrado y análisis

#### 📁 Exportación de Reportes
- **CSV de facturas procesadas**: Lista completa con todos los detalles
- **Resumen ejecutivo JSON**: Métricas completas de la ejecución
- **Reporte de morosidad CSV**: Estadísticas detalladas
- Configurable mediante `enable_export_reports`

#### 🏥 Health Checks Automáticos
- Verificación de estado del sistema después de cada ejecución
- Detección automática de problemas:
  - Alto número de facturas críticas (>50)
  - Monto vencido muy alto (>$100,000)
  - Promedio de días vencidos crítico (>60 días)
  - Falta de recordatorios cuando debería haberlos
- Estados: `healthy`, `warning`, `error`

#### 🚨 Alertas Automáticas
- Notificaciones en Slack cuando se detectan errores críticos
- Solo se activa si hay problemas reales
- Incluye detalles de todos los errores detectados

## Configuración

### Inputs Requeridos

```yaml
inputs:
  - jdbc_url: "jdbc:postgresql://host:5432/database"
  - jdbc_user: "username"
  - jdbc_password: "password"
```

### Inputs Opcionales

```yaml
inputs:
  # Notificaciones
  - email_webhook_url: "https://email-service/api/send"
  - slack_webhook_url: "https://hooks.slack.com/..."
  - whatsapp_webhook_url: "https://whatsapp-service/..."
  
  # Configuración de recordatorios
  - reminder_days: "-3,0,7,14,30,60"
  - payment_terms_days: "30"
  - min_amount: "0"
  - max_daily_reminders_per_invoice: "1"
  - payment_portal_url: "https://pay.example.com"
  
  # Escalación
  - finance_team_email: "finanzas@example.com"
  - critical_amount_threshold: "10000"
  
  # Features avanzados
  - enable_whatsapp_critical: true
  - enable_effectiveness_tracking: true
  - enable_performance_metrics: true
  - enable_export_reports: false  # NUEVO
  - rate_limit_per_minute: "60"
```

## Flujo de Trabajo Completo

1. **validate_inputs**: Validación de todos los inputs
2. **ensure_schema**: Crear/validar estructura de BD
3. **update_due_dates**: Actualizar fechas de vencimiento faltantes
4. **find_overdue_invoices**: Buscar facturas que necesitan recordatorios
5. **validate_and_process_invoices**: Validar y procesar facturas
6. **apply_rate_limiting**: Aplicar rate limiting inteligente
7. **send_email_reminders**: Enviar emails (con rate limiting)
8. **send_whatsapp_critical**: WhatsApp para críticas (opcional)
9. **escalation_to_finance_team**: Escalación automática (opcional)
10. **send_slack_summary**: Resumen a Slack
11. **analyze_reminder_effectiveness**: Análisis de efectividad (opcional)
12. **analyze_trends**: Análisis de tendencias
13. **log_reminder_history**: Registrar en BD (batch optimizado)
14. **generate_delinquency_report**: Generar reporte de morosidad
15. **log_metrics**: Métricas finales
16. **performance_metrics**: Análisis de performance (opcional)
17. **log_key_metrics**: Logging estructurado (NUEVO)
18. **export_reports**: Exportar reportes CSV/JSON (NUEVO - opcional)
19. **final_health_check**: Health check final (NUEVO)
20. **notify_critical_errors**: Alertas de errores críticos (NUEVO)

## Exportación de Reportes

Cuando `enable_export_reports: true`, el workflow genera:

1. **`invoices_processed_TIMESTAMP.csv`**
   - Lista completa de facturas procesadas
   - Campos: invoice_id, serie, customer, email, total, currency, days_overdue, urgency, template, due_date

2. **`execution_summary_TIMESTAMP.json`**
   - Resumen completo de la ejecución
   - Incluye: execution_summary, delinquency_report, trends, effectiveness

3. **`delinquency_report_TIMESTAMP.csv`**
   - Reporte de morosidad detallado
   - Todas las métricas clave en formato CSV

## Health Checks

El sistema realiza verificaciones automáticas:

### Warnings (Amarillo)
- Más de 50 facturas críticas
- Monto total vencido > $100,000

### Errors (Rojo)
- Promedio de días vencidos > 60
- No se enviaron recordatorios cuando debería haberlos

### Alertas Automáticas
- Se envía notificación en Slack si el estado es `error`
- Incluye detalles de todos los problemas detectados

## Logging Estructurado

El workflow integra `subflow_metrics_logger` para:

- **Métricas de ejecución**: Total de recordatorios enviados con labels detallados
- **Métricas de morosidad**: Monto total vencido y estadísticas
- Compatible con sistemas de observabilidad (ELK, Prometheus, etc.)
- Labels para filtrado: workflow, urgency_critical, urgency_error, total_amount

## Casos de Uso

### Escenario 1: Facturas Críticas
Cuando una factura tiene 60+ días vencida:
1. Se envía email normal
2. Se envía WhatsApp (si está configurado)
3. Se escalará al equipo de finanzas
4. Se registrará como crítica en health check

### Escenario 2: Alto Volumen
Cuando hay muchas facturas:
1. Rate limiting previene sobrecarga
2. Procesamiento en batches
3. Priorización automática (críticas primero)

### Escenario 3: Problemas del Sistema
Si se detectan problemas:
1. Health check marca estado de error
2. Se envía alerta automática a Slack
3. Se incluyen recomendaciones en métricas

## Métricas y KPIs

### Métricas de Ejecución
- Recordatorios enviados/omitidos
- Monto total procesado
- Distribución por urgencia

### Métricas de Morosidad
- Total de facturas vencidas
- Monto total vencido
- Promedio/máximo de días vencidos
- Clientes únicos afectados

### Métricas de Efectividad
- Tasa de efectividad por tipo de recordatorio
- Tiempo promedio hasta pago
- Monto total cobrado post-recordatorio

### Métricas de Tendencias
- Cambio día a día
- Cambio semana a semana
- Evolución de facturas críticas

### Métricas de Performance
- Throughput (recordatorios por ejecución)
- Eficiencia (potencial de cobro)
- Recomendaciones automáticas

## Troubleshooting

### Problema: No se envían recordatorios
**Verificar:**
1. Configuración de webhooks (email_webhook_url)
2. Validación de emails en facturas
3. Filtros de reminder_days
4. Health check para errores

### Problema: Rate limiting muy agresivo
**Solución:**
- Aumentar `rate_limit_per_minute`
- Revisar límites del servicio de email

### Problema: Exportación no funciona
**Verificar:**
- `enable_export_reports` debe ser `true`
- Permisos de escritura en el sistema de archivos
- Tamaño de archivos generados

### Problema: Health check siempre en error
**Revisar:**
- Umbrales en el script de health check
- Datos reales del sistema
- Configuración de alertas

## Mejores Prácticas

1. **Monitoreo Regular**: Revisar métricas y health checks diariamente
2. **Ajuste de Umbrales**: Personalizar según tu negocio
3. **Exportación Semanal**: Habilitar exportación para reportes ejecutivos
4. **Revisión de Efectividad**: Analizar qué tipos de recordatorios funcionan mejor
5. **Escalación Proactiva**: Revisar facturas críticas manualmente si hay muchas

## Referencias

- [Documentación de Kestra](https://kestra.io/docs)
- [Plugins JDBC PostgreSQL](https://kestra.io/plugins/plugin-jdbc-postgresql)
- [Subflows Reutilizables](../README.md#subflows)

