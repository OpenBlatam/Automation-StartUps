# 🎯 Mejores Prácticas - Sistema de Ventas

Guía de mejores prácticas para usar y mantener el sistema de automatización de ventas.

## 📊 Configuración de Scores

### Factores de Scoring Recomendados

**Prioridad Alta:**
- Email válido: +10 puntos
- Teléfono: +5 puntos
- Reply a email: +15-25 puntos
- Demo solicitado: +10 puntos

**Prioridad Media:**
- Clicks en emails: +8-12 puntos
- Opens múltiples: +5-15 puntos
- Página de precios visitada: +5 puntos

**Prioridad Baja:**
- UTM parameters: +2 puntos
- Source quality: +1-5 puntos
- Recency bonus: +5-10 puntos

### Ajuste de Thresholds

**Score mínimo para calificar:**
- **50 puntos**: Estándar recomendado
- **40 puntos**: Si quieres más leads en pipeline
- **60 puntos**: Si quieres solo leads de alta calidad

**Ajuste según tus datos:**
```sql
-- Ver distribución de scores
SELECT 
    CASE 
        WHEN score < 35 THEN 'Low'
        WHEN score < 50 THEN 'Medium'
        WHEN score < 70 THEN 'High'
        ELSE 'Very High'
    END AS score_range,
    COUNT(*) AS count,
    COUNT(*) FILTER (WHERE ext_id IN (SELECT lead_ext_id FROM sales_pipeline WHERE stage = 'closed_won')) AS won
FROM leads
WHERE score IS NOT NULL
GROUP BY score_range
ORDER BY score_range;
```

## 🎪 Gestión de Campañas

### Estructura de Campañas Recomendada

**Campaña de Onboarding (Qualified Leads):**
```json
{
  "trigger_criteria": {
    "stage": "qualified",
    "score_min": 50
  },
  "steps": [
    {
      "step": 1,
      "type": "email",
      "delay_hours": 0,
      "subject": "Bienvenido {{first_name}}"
    },
    {
      "step": 2,
      "type": "email",
      "delay_hours": 48,
      "subject": "Seguimiento {{first_name}}"
    },
    {
      "step": 3,
      "type": "call",
      "delay_hours": 96,
      "subject": "Llamada de seguimiento"
    }
  ]
}
```

### Timing Óptimo

**Basado en análisis:**
- **Día óptimo**: Martes-Miércoles (mejor respuesta)
- **Hora óptima**: 10-11 AM, 2-3 PM
- **Intervalo entre contactos**: 2-3 días (máxima conversión)

**Ajustar según tu audiencia:**
```sql
-- Analizar timing de éxito
SELECT 
    EXTRACT(DOW FROM completed_at) AS day_of_week,
    EXTRACT(HOUR FROM completed_at) AS hour,
    COUNT(*) AS total,
    COUNT(*) FILTER (WHERE p.stage = 'closed_won') AS won,
    ROUND(COUNT(*) FILTER (WHERE p.stage = 'closed_won')::NUMERIC / COUNT(*) * 100, 2) AS win_rate
FROM sales_followup_tasks t
JOIN sales_pipeline p ON t.pipeline_id = p.id
WHERE t.status = 'completed'
GROUP BY day_of_week, hour
ORDER BY win_rate DESC;
```

## 👥 Asignación de Vendedores

### Configuración de Equipo

**Tamaño óptimo de pipeline por vendedor:**
- **Junior**: 20-30 leads activos
- **Mid-level**: 30-50 leads activos
- **Senior**: 50-70 leads activos

**Round-robin vs Intelligent Routing:**
- **Round-robin**: Para equipos pequeños (< 5 vendedores)
- **Intelligent Routing**: Para equipos grandes o especializados

### Balanceo de Carga

**Monitorear carga:**
```sql
SELECT 
    assigned_to,
    COUNT(*) AS active_leads,
    COUNT(*) FILTER (WHERE priority = 'high') AS high_priority,
    SUM(estimated_value) AS total_value
FROM sales_pipeline
WHERE stage NOT IN ('closed_won', 'closed_lost')
GROUP BY assigned_to
ORDER BY active_leads DESC;
```

**Re-balancear si:**
- Diferencia > 20 leads entre vendedores
- Un vendedor tiene > 50% de tareas vencidas
- Pipeline value muy desbalanceado

## 🔔 Configuración de Alertas

### Thresholds Recomendados

**Alertas Críticas:**
- Leads > $10k sin contacto en 7 días
- Tareas urgentes vencidas > 1 día
- ML risk score > 0.8

**Alertas de Advertencia:**
- Leads sin contacto en 14 días
- Caída de conversión > 10 puntos
- Vendedor con > 10 tareas vencidas

**Alertas Informativas:**
- Vendedor con > 50 leads activos
- Pipeline value > $500k
- Win rate < 20%

### Frecuencia de Alertas

- **Críticas**: Inmediatas (cada 2 horas)
- **Advertencias**: Diarias
- **Informativas**: Semanales

## 📈 Optimización de Pipeline

### Gestión por Etapa

**Qualified:**
- Primer contacto en < 24 horas
- Tarea de seguimiento automática
- Score mínimo: 50

**Contacted:**
- Llamada de seguimiento en 48 horas
- Email de valor agregado
- Actualizar next_followup_at

**Meeting Scheduled:**
- Enviar agenda 24h antes
- Materiales de preparación
- Confirmar día anterior

**Proposal Sent:**
- Seguimiento en 48-72 horas
- Responder preguntas rápidamente
- Actualizar probability basado en feedback

**Negotiating:**
- Seguimiento diario
- Prioridad máxima
- Alertas automáticas

### Métricas a Monitorear

**Por Etapa:**
- Tiempo promedio en cada etapa
- Tasa de conversión entre etapas
- Valor promedio por etapa

**Por Vendedor:**
- Win rate
- Tiempo promedio a cierre
- Pipeline value
- Tareas completadas vs vencidas

## 🤖 Uso de ML Predictions

### Configuración del Modelo

**Features importantes:**
- Lead score
- Days in pipeline
- Days since contact
- Completed tasks
- Engagement metrics

**Thresholds:**
- Probabilidad mínima: 20%
- Confianza mínima: 0.6
- Actualizar probability_pct si diferencia > 10 puntos

### Interpretación de Predicciones

**Risk Score:**
- < 0.3: Bajo riesgo
- 0.3-0.6: Riesgo medio
- 0.6-0.8: Alto riesgo
- > 0.8: Crítico - acción inmediata

**Recomendaciones:**
- `send_proposal`: Enviar propuesta
- `schedule_call`: Programar llamada
- `escalate`: Escalar a manager
- `nurture`: Continuar nutrición

## 🔄 Mantenimiento Regular

### Tareas Diarias
- Revisar alertas críticas
- Verificar health check
- Monitorear leads sin asignar

### Tareas Semanales
- Revisar reportes de analytics
- Analizar performance de vendedores
- Ajustar campañas según resultados
- Validar integridad de datos

### Tareas Mensuales
- Revisar y optimizar scoring
- Analizar timing de seguimiento
- Actualizar thresholds de alertas
- Revisar y limpiar datos antiguos

## 🧹 Limpieza de Datos

### Datos Antiguos

**Archivar leads cerrados:**
```sql
-- Mover leads cerrados hace > 1 año a tabla de archivo
CREATE TABLE sales_pipeline_archive AS
SELECT * FROM sales_pipeline
WHERE stage IN ('closed_won', 'closed_lost')
AND (
    (stage = 'closed_won' AND closed_at < NOW() - INTERVAL '1 year')
    OR (stage = 'closed_lost' AND closed_at < NOW() - INTERVAL '6 months')
);
```

**Limpiar historial de scores:**
```sql
-- Mantener solo últimos 90 días de historial
DELETE FROM lead_score_history
WHERE calculated_at < NOW() - INTERVAL '90 days'
AND lead_ext_id NOT IN (
    SELECT lead_ext_id FROM sales_pipeline
    WHERE stage NOT IN ('closed_won', 'closed_lost')
);
```

### Validación de Datos

**Ejecutar regularmente:**
```bash
python scripts/validate_sales_system.py --db "..." --all
```

**Verificar:**
- Leads sin email
- Tareas huérfanas
- Campañas sin pasos
- Ejecuciones sin eventos

## 📊 Análisis y Optimización

### Revisar Métricas Semanalmente

**Pipeline Health:**
```sql
SELECT * FROM v_sales_dashboard
WHERE days_since_contact > 7
ORDER BY estimated_value DESC;
```

**Conversion Funnel:**
```sql
SELECT * FROM v_conversion_funnel;
```

**Forecast:**
```sql
SELECT * FROM v_sales_forecast;
```

### Ajustar Basado en Datos

**Si win rate bajo:**
- Aumentar score mínimo para calificar
- Mejorar calidad de leads en fuente
- Optimizar proceso de seguimiento

**Si tiempo a cierre largo:**
- Reducir intervalos entre contactos
- Mejorar calidad de propuestas
- Identificar cuellos de botella

**Si pipeline value bajo:**
- Enfocarse en leads de alto valor
- Mejorar qualification criteria
- Aumentar estimated_value accuracy

## 🔐 Seguridad y Privacidad

### Datos Sensibles

- **Encriptar**: Emails y teléfonos en tránsito
- **Acceso**: Restringir acceso a datos de ventas
- **Auditoría**: Log de cambios importantes
- **GDPR**: Permite eliminar datos de leads

### Backup

**Frecuencia:**
- Backup diario de datos críticos
- Backup semanal completo
- Backup antes de migraciones

**Retención:**
- 30 días de backups diarios
- 12 meses de backups semanales
- Permanente de backups de migración

## 📚 Referencias

- [README Principal](README_SALES_AUTOMATION.md)
- [Quick Start](QUICK_START_SALES.md)
- [Queries](README_SALES_QUERIES.md)
- [Migration Guide](MIGRATION_GUIDE.md)


