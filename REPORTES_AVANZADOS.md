# 📊 Reportes Avanzados - Documentación Completa

## 🎯 Funcionalidades de Reportes Avanzados

El workflow ahora incluye un módulo completo de **Advanced Analytics & Insights** que genera reportes empresariales de nivel ejecutivo.

### 1. **Análisis Comparativo** 📈

Compara métricas actuales vs. período anterior:

```python
comparative_analysis = {
    'revenue': {
        'current': 45000.00,
        'previous': 38000.00,
        'change_pct': 18.42,
        'change_abs': 7000.00,
        'trend': 'up'
    },
    'deals': { ... },
    'new_customers': { ... }
}
```

**Métricas incluidas:**
- Revenue: Cambio porcentual y absoluto
- Deals: Comparación de volumen
- New Customers: Crecimiento de clientes
- Indicadores de tendencia (up/down)

### 2. **Detección de Anomalías (Z-Score)** ⚠️

Detecta valores fuera de lo normal usando estadística:

```python
anomaly_detection = {
    'revenue': {
        'current': 45000.00,
        'mean': 38000.00,
        'std_dev': 5000.00,
        'z_score': 1.4,
        'is_anomaly': False,
        'severity': 'none',
        'message': 'Revenue normal: z-score=1.40'
    }
}
```

**Umbrales:**
- Normal: |z-score| < 2.0
- Medio: 2.0 ≤ |z-score| < 3.0
- Alto: |z-score| ≥ 3.0

### 3. **Análisis de Tendencias** 📊

Calcula tendencias lineales y proyecciones:

```python
trend_analysis = {
    'revenue': {
        'trend': 'increasing',  # increasing/decreasing/stable
        'slope': 1250.50,
        'growth_rate_pct': 3.25,
        'last_7_days': [35000, 38000, ..., 45000],
        'projection_next_day': 46250.50,
        'momentum': 'strong'  # strong/weak
    }
}
```

**Características:**
- Ajuste lineal por mínimos cuadrados
- Cálculo de tasa de crecimiento
- Proyección para el próximo día
- Indicador de momentum

### 4. **KPIs Calculados Automáticamente** 🎯

Genera KPIs derivados de métricas básicas:

```python
kpis = {
    'total_revenue': 45000.00,
    'total_deals': 25,
    'new_customers': 30,
    'average_deal_value': 1800.00,
    'revenue_per_customer': 1500.00,
    'estimated_ltv': 4500.00,  # Lifetime Value estimado
    'conversion_rate_pct': 83.33,
    'customer_growth_rate': 15.5,
    'revenue_growth_rate': 18.42
}
```

**KPIs Incluidos:**
- Revenue per Customer
- Conversion Rate (%)
- Estimated Lifetime Value (LTV)
- Growth Rates (Customer & Revenue)

### 5. **Análisis Temporal (Distribución por Horas)** ⏰

Analiza patrones temporales de actividad:

```python
time_analysis = {
    'hourly_distribution': {
        0: 0.15, 1: 0.12, ..., 14: 1.85, ...
    },
    'peak_hour': 14,
    'peak_performance': 1.85,
    'business_hours_ratio': 0.72  # 72% de actividad en horario comercial
}
```

**Insights:**
- Hora pico de actividad
- Distribución de actividad por hora
- Ratio de actividad en horario comercial

### 6. **Segmentación y Análisis por Categorías** 🏷️

Analiza datos segmentados por diferentes dimensiones:

```python
segmentation = {
    'deals_by_stage': {
        'breakdown': {'Closed Won': 15, 'Negotiation': 8, ...},
        'total': 25,
        'top_stage': 'Closed Won',
        'distribution_pct': {'Closed Won': 60.0, 'Negotiation': 32.0, ...}
    },
    'charges_by_status': {
        'breakdown': {'succeeded': 145, 'pending': 5},
        'success_rate': 96.67
    }
}
```

**Segmentaciones:**
- Deals por Stage (HubSpot)
- Deals por Pipeline
- Charges por Status (Stripe)
- Tasa de éxito de transacciones

### 7. **Alertas Inteligentes** 🚨

Sistema de alertas basado en umbrales y condiciones:

```python
alerts = [
    {
        'type': 'revenue_low',
        'severity': 'warning',
        'message': 'Revenue (8500.00) está por debajo del umbral (10000)',
        'value': 8500.00,
        'threshold': 10000.0
    },
    {
        'type': 'revenue_anomaly',
        'severity': 'medium',
        'message': 'Revenue anomalía detectada: z-score=-2.45',
        'z_score': -2.45
    }
]
```

**Tipos de Alertas:**
- `revenue_low`: Revenue bajo umbral configurable
- `revenue_anomaly`: Anomalía estadística detectada
- `revenue_declining`: Tendencia descendente fuerte (>10%)
- `low_conversion`: Tasa de conversión baja (<5%)

**Niveles de Severidad:**
- `info`: Informativo
- `warning`: Requiere atención
- `medium`: Requiere investigación
- `high`: Acción inmediata requerida

### 8. **Resumen Ejecutivo** 📋

Genera un resumen ejecutivo con highlights y recomendaciones:

```python
executive_summary = {
    'status': 'healthy',  # healthy/warning/info
    'key_metrics': {
        'total_revenue': 45000.00,
        'revenue_change': 18.42,
        'total_deals': 25,
        'new_customers': 30
    },
    'highlights': [
        'Revenue: $45,000.00 📈',
        'Anomalías: ✅ Ninguna',
        'Alertas activas: 0'
    ],
    'recommendations': [
        'Optimizar tasa de conversión',
        'Mantener momentum positivo'
    ]
}
```

## 🎨 Reporte HTML Visual

Se genera automáticamente un reporte HTML profesional con:

### Características del Reporte HTML:

1. **Diseño Moderno y Responsive**
   - Gradiente morado/azul en header
   - Grid de métricas responsive
   - Cards con indicadores de cambio

2. **Secciones Incluidas:**
   - **Executive Summary**: Métricas clave con cambios porcentuales
   - **Alertas**: Visualización de alertas por severidad
   - **KPIs**: Tabla completa de indicadores
   - **Trend Analysis**: Tendencias y proyecciones
   - **Anomaly Detection**: Estado de anomalías
   - **Recommendations**: Recomendaciones accionables

3. **Indicadores Visuales:**
   - Emojis para tendencias (📈 📉)
   - Colores por cambio (verde/rojo)
   - Badges de severidad de alertas
   - Formato de moneda y porcentajes

## 📦 Estructura de Datos Completa

El resultado final incluye toda la estructura de análisis:

```json
{
  "summary": { /* Métricas básicas */ },
  "advanced_analytics": {
    "execution_id": "1234567890-abc123",
    "report_date": "2024-01-15T08:00:00Z",
    "comparative_analysis": { /* ... */ },
    "anomaly_detection": { /* ... */ },
    "trend_analysis": { /* ... */ },
    "kpis": { /* ... */ },
    "time_analysis": { /* ... */ },
    "segmentation": { /* ... */ },
    "alerts": [ /* ... */ ],
    "executive_summary": { /* ... */ }
  },
  "hyperFile": "daily_report_20240115.hyper",
  "htmlFile": "daily_report_20240115.html"
}
```

## 🔧 Configuración y Personalización

### Umbrales Configurables:

```python
# En el código de Advanced Analytics, puedes ajustar:

revenue_threshold = 10000.0  # Umbral mínimo de revenue
z_score_threshold = 2.0    # Umbral de anomalías (desviaciones estándar)
conversion_threshold = 5.0  # Umbral mínimo de conversión (%)
```

### Integración con Datos Históricos:

**Nota Actual:** El código usa simulaciones para datos históricos. Para producción:

1. **Conexión a Base de Datos:**
```python
# Reemplazar simulaciones con:
historical_data = pd.read_sql(
    "SELECT revenue, date FROM daily_reports WHERE date >= CURRENT_DATE - 7",
    connection
)
```

2. **Almacenamiento de Historial:**
- Guardar cada ejecución en tabla de histórico
- Leer últimos N días para comparaciones
- Mantener rolling averages

## 📊 Métricas Exportadas

Todos los análisis avanzados se incluyen en:

1. **Archivo Hyper (.hyper)**: Para Tableau
   - Tabla `daily_summary`: Resumen con métricas avanzadas
   - Tabla `daily_details`: Transacciones individuales

2. **Archivo HTML (.html)**: Reporte visual
   - Formato ejecutivo listo para compartir
   - Estilo profesional y responsive

3. **JSON Output**: Para integraciones
   - Estructura completa de `advanced_analytics`
   - Disponible en nodos posteriores del workflow

## 🚀 Uso en Producción

### Pasos para Implementación Completa:

1. **Configurar Almacén Histórico:**
   - Base de datos para guardar ejecuciones diarias
   - Tabla: `daily_report_history`

2. **Reemplazar Simulaciones:**
   - Conectar a BD para datos históricos
   - Usar API de n8n para leer ejecuciones previas

3. **Configurar Umbrales:**
   - Ajustar según tu negocio
   - Definir KPIs objetivo

4. **Integrar Notificaciones:**
   - Slack para alertas críticas
   - Email para resumen diario
   - Dashboard para visualización continua

## 💡 Ejemplos de Insights Generados

### Ejemplo 1: Revenue Anomalía Detectada

```
⚠️ Revenue Anomaly Detected
- Current: $45,000
- Mean (7d): $32,000
- Z-Score: 2.8 (High Severity)
- Recommendation: Investigar causa de aumento inusual
```

### Ejemplo 2: Tendencia Positiva Fuerte

```
📈 Strong Positive Trend
- Growth Rate: +12.5% (last 7 days)
- Momentum: Strong
- Projected Next Day: $48,250
- Recommendation: Mantener estrategia actual
```

### Ejemplo 3: Conversión Baja

```
ℹ️ Low Conversion Rate Alert
- Current Rate: 3.2%
- Threshold: 5.0%
- Recommendation: Revisar funnel de conversión
```

## 📈 Mejoras Futuras Sugeridas

1. **Machine Learning:**
   - Modelo de predicción de revenue
   - Detección avanzada de anomalías (Isolation Forest)
   - Forecasting con Prophet o ARIMA

2. **Análisis de Cohortes:**
   - Seguimiento de cohorts de clientes
   - Análisis de retención

3. **Correlaciones:**
   - Análisis de correlación entre métricas
   - Identificación de drivers clave

4. **Visualizaciones Interactivas:**
   - Gráficos con Plotly/Chart.js
   - Dashboard interactivo en HTML

5. **Integración con APIs Externas:**
   - Google Analytics
   - Facebook Ads
   - LinkedIn Analytics

## 🎓 Conclusión

El sistema de reportes avanzados proporciona:

✅ **Análisis Automático Completo**
✅ **Detección Proactiva de Problemas**
✅ **Insights Accionables**
✅ **Visualización Profesional**
✅ **Escalabilidad y Extensibilidad**

¡Listo para proporcionar insights de nivel ejecutivo diariamente!


