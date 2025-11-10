# Automatización de Investigación de Mercado

## 📊 Sistema Completo de Investigación de Mercado Automatizada

Sistema enterprise para automatizar investigación de mercado y generar insights accionables sobre tendencias de mercado para cualquier industria en los próximos 6 meses.

### 🎯 Objetivo

Automatizar investigación de mercado para decisiones informadas y escalabilidad, proporcionando insights accionables sobre tendencias de mercado alineados con estrategia de crecimiento basada en datos en tiempo real.

---

## 🚀 Las 5 Automatizaciones Principales

### 1. **Análisis Automático de Tendencias de Mercado**

**Descripción:**
Análisis continuo y automatizado de tendencias de mercado desde múltiples fuentes de datos.

**Funcionalidades:**
- Análisis de volumen de búsquedas (Google Trends)
- Análisis de cobertura de noticias
- Análisis de sentimiento en redes sociales
- Análisis de actividad de competidores
- Detección automática de patrones y cambios significativos

**Configuración:**
```python
# En el DAG de Airflow
{
    "industry": "tech",
    "timeframe_months": 6,
    "keywords": ["AI", "cloud computing", "digital transformation"],
    "competitors": ["competitor1", "competitor2"]
}
```

**Frecuencia:** Semanal (cada lunes)

**Output:**
- Tendencias identificadas con métricas de cambio
- Dirección de tendencia (alcista/bajista/estable)
- Nivel de confianza
- Fuentes de datos

**Beneficios:**
- Detección temprana de cambios en el mercado
- Identificación de oportunidades emergentes
- Monitoreo continuo sin intervención manual

---

### 2. **Integración Automática con Múltiples Fuentes de Datos**

**Descripción:**
Recolección automática de datos de mercado desde múltiples APIs y fuentes externas.

**Fuentes Integradas:**
- **Google Trends API**: Volumen de búsquedas y tendencias
- **News APIs**: Cobertura de noticias y artículos relevantes
- **Social Media APIs**: Sentimiento y menciones en redes sociales
- **Financial Data APIs**: Datos financieros y de mercado
- **Competitor Analysis**: Actividad y movimientos de competidores

**Configuración:**
```bash
# Variables de entorno
export GOOGLE_TRENDS_API_KEY="your_key"
export NEWS_API_KEY="your_key"
export SOCIAL_API_KEY="your_key"
export FINANCIAL_API_KEY="your_key"
```

**Características:**
- Circuit breakers para resiliencia
- Cache inteligente (30 minutos)
- Retry automático con backoff exponencial
- Rate limiting para evitar límites de API

**Output:**
- Datos consolidados de todas las fuentes
- Métricas agregadas
- Análisis comparativo entre fuentes

**Beneficios:**
- Datos actualizados en tiempo real
- Redundancia y confiabilidad
- Escalabilidad automática

---

### 3. **Generación Automática de Insights Accionables**

**Descripción:**
Sistema inteligente que genera insights accionables basados en análisis de tendencias.

**Tipos de Insights Generados:**

#### a) Insights de Tendencias
- Identificación de tendencias alcistas/bajistas
- Magnitud del cambio
- Pasos accionables específicos por categoría

#### b) Insights de Oportunidades
- Oportunidades de mercado detectadas
- Potencial de crecimiento
- Planes de acción recomendados

#### c) Insights de Riesgos
- Riesgos identificados
- Nivel de amenaza
- Estrategias de mitigación

#### d) Recomendaciones Estratégicas
- Recomendaciones basadas en momentum
- Estrategias de diversificación
- Planes de acción a corto/medio plazo

#### e) Insights Predictivos
- Predicciones basadas en patrones históricos
- Tendencias futuras esperadas
- Preparación proactiva

**Priorización:**
- **Alta**: Cambios significativos (>20%) con alta confianza
- **Media**: Cambios moderados (10-20%) con confianza media
- **Baja**: Cambios menores (<10%) o baja confianza

**Output:**
- Lista de insights con:
  - Título y descripción
  - Categoría y prioridad
  - Pasos accionables específicos
  - Impacto esperado
  - Timeframe
  - Nivel de confianza

**Beneficios:**
- Decisiones basadas en datos
- Acciones claras y específicas
- Priorización automática

---

### 4. **Alertas y Notificaciones Automáticas**

**Descripción:**
Sistema de alertas automáticas para insights críticos y cambios significativos.

**Tipos de Alertas:**

#### Alertas de Alta Prioridad
- Oportunidades de alto impacto detectadas
- Riesgos significativos identificados
- Cambios abruptos en tendencias

#### Alertas de Momentum
- Momentum positivo detectado
- Cambios de dirección en tendencias
- Patrones emergentes

#### Resúmenes Semanales
- Resumen de insights generados
- Tendencias principales
- Recomendaciones destacadas

**Canales de Notificación:**
- Slack (webhook)
- Email (configurable)
- Dashboard en tiempo real
- Base de datos para integración

**Configuración:**
```python
{
    "slack_webhook_url": "https://hooks.slack.com/services/...",
    "alert_threshold": "high",  # high, medium, low
    "notification_frequency": "weekly"
}
```

**Beneficios:**
- Respuesta rápida a cambios
- Visibilidad continua
- Sin necesidad de monitoreo manual

---

### 5. **Reportes Automáticos y Almacenamiento**

**Descripción:**
Generación automática de reportes y almacenamiento persistente de análisis.

**Tipos de Reportes:**

#### Reporte Markdown
- Formato legible para humanos
- Estructurado por prioridad
- Incluye todos los insights con pasos accionables

#### Reporte JSON
- Formato estructurado para integración
- Datos completos para procesamiento
- Compatible con APIs y sistemas externos

#### Dashboard Interactivo
- Visualización de tendencias
- Gráficos y métricas
- Filtros por categoría y prioridad

**Almacenamiento:**
- Base de datos PostgreSQL
- Historial completo de análisis
- Consultas históricas y comparativas
- Análisis de tendencias a largo plazo

**Configuración:**
```python
{
    "save_to_db": True,
    "generate_report": True,
    "report_formats": ["markdown", "json"],
    "retention_days": 365
}
```

**Beneficios:**
- Historial completo de análisis
- Trazabilidad de decisiones
- Análisis comparativo temporal
- Documentación automática

---

## 📋 Guía de Uso

### Instalación y Configuración

#### 1. Instalar Dependencias

Las dependencias ya están incluidas en `requirements.txt`:
- `httpx`: Cliente HTTP moderno
- `pandas`, `numpy`: Análisis de datos
- `tenacity`: Retry logic
- `pybreaker`: Circuit breakers
- `cachetools`: Cache

#### 2. Configurar Variables de Entorno

```bash
# APIs de datos de mercado
export GOOGLE_TRENDS_API_KEY="your_google_trends_api_key"
export NEWS_API_KEY="your_news_api_key"
export SOCIAL_API_KEY="your_social_api_key"
export FINANCIAL_API_KEY="your_financial_api_key"

# Base de datos
export POSTGRES_CONN_ID="postgres_default"

# Notificaciones
export SLACK_WEBHOOK_URL="https://hooks.slack.com/services/..."
```

#### 3. Configurar Base de Datos

El sistema creará automáticamente las tablas necesarias. Asegúrate de tener:
- PostgreSQL configurado
- Connection ID configurado en Airflow
- Permisos de escritura

### Uso Básico

#### Ejecutar Análisis Manual

```python
# Desde Airflow UI
# 1. Ir a DAGs > market_research_automation
# 2. Click en "Trigger DAG w/ config"
# 3. Configurar parámetros:
{
    "industry": "tech",
    "timeframe_months": 6,
    "keywords": ["AI", "cloud computing"],
    "competitors": ["competitor1", "competitor2"]
}
```

#### Ejecutar desde CLI

```bash
# Trigger DAG con parámetros
airflow dags trigger market_research_automation \
  --conf '{"industry": "tech", "timeframe_months": 6}'
```

### Ejemplos de Uso por Industria

#### Tecnología
```python
{
    "industry": "tech",
    "keywords": ["AI", "machine learning", "cloud computing", "SaaS"],
    "competitors": ["Microsoft", "Google", "Amazon"]
}
```

#### Healthcare
```python
{
    "industry": "healthcare",
    "keywords": ["telemedicine", "health tech", "digital health"],
    "competitors": ["Teladoc", "Amwell"]
}
```

#### Fintech
```python
{
    "industry": "fintech",
    "keywords": ["digital banking", "blockchain", "cryptocurrency"],
    "competitors": ["Stripe", "Square", "PayPal"]
}
```

#### Retail/E-commerce
```python
{
    "industry": "retail",
    "keywords": ["e-commerce", "online shopping", "omnichannel"],
    "competitors": ["Amazon", "Walmart", "Target"]
}
```

### Acceder a Resultados

#### 1. Desde Airflow UI
- Ver logs de cada tarea
- Descargar reportes generados
- Ver resumen final

#### 2. Desde Base de Datos
```sql
-- Ver análisis recientes
SELECT industry, analysis_date, analysis_data
FROM market_trends_analysis
WHERE industry = 'tech'
ORDER BY analysis_date DESC
LIMIT 10;

-- Ver insights de alta prioridad
SELECT analysis_data->'insights' as insights
FROM market_trends_analysis
WHERE analysis_data->'insights' @> '[{"priority": "high"}]';
```

#### 3. Desde Reportes
- Reportes Markdown: Descargar desde Airflow UI
- Reportes JSON: Para integración con otros sistemas

---

## 🔧 Configuración Avanzada

### Personalizar Análisis

#### Agregar Keywords Personalizados
```python
{
    "keywords": [
        "keyword1",
        "keyword2",
        "keyword específico de tu negocio"
    ]
}
```

#### Configurar Competidores
```python
{
    "competitors": [
        "competitor1",
        "competitor2",
        "competitor3"
    ]
}
```

### Ajustar Frecuencia

Modificar el schedule en el DAG:
```python
@dag(
    schedule="0 0 * * 1",  # Semanal (lunes)
    # schedule="0 0 * * *",  # Diario
    # schedule="0 0 1 * *",  # Mensual
)
```

### Configurar Notificaciones

#### Slack
```python
{
    "slack_webhook_url": "https://hooks.slack.com/services/...",
    "alert_threshold": "high"
}
```

#### Email (futuro)
```python
{
    "email_notifications": True,
    "email_recipients": ["team@company.com"]
}
```

---

## 📊 Interpretación de Resultados

### Insights de Alta Prioridad

**Qué buscar:**
- Cambios >20% en tendencias
- Oportunidades con alta confianza (>0.8)
- Riesgos significativos

**Acción recomendada:**
- Revisar inmediatamente
- Desarrollar plan de acción
- Asignar recursos

### Insights de Media Prioridad

**Qué buscar:**
- Cambios 10-20% en tendencias
- Oportunidades con confianza media (0.6-0.8)

**Acción recomendada:**
- Monitorear evolución
- Preparar respuesta
- Evaluar recursos necesarios

### Insights de Baja Prioridad

**Qué buscar:**
- Cambios <10%
- Tendencias con baja confianza

**Acción recomendada:**
- Mantener en radar
- Revisar en próximo ciclo
- No requiere acción inmediata

---

## 🎯 Casos de Uso

### 1. Lanzamiento de Producto
- Analizar mercado antes del lanzamiento
- Identificar oportunidades de posicionamiento
- Monitorear competencia

### 2. Expansión de Mercado
- Analizar nuevos mercados/industrias
- Identificar oportunidades de crecimiento
- Evaluar competencia

### 3. Monitoreo Continuo
- Detectar cambios en el mercado
- Identificar nuevas oportunidades
- Alertar sobre riesgos

### 4. Planificación Estratégica
- Informar decisiones estratégicas
- Identificar tendencias a largo plazo
- Preparar para cambios futuros

---

## 🔍 Troubleshooting

### Error: "Industry parameter is required"
**Solución:** Asegúrate de proporcionar el parámetro `industry` al trigger el DAG.

### Error: "API key not configured"
**Solución:** Configura las variables de entorno necesarias o el sistema usará datos simulados.

### Error: "Database connection failed"
**Solución:** Verifica la conexión PostgreSQL en Airflow Connections.

### No se generan insights
**Solución:** Verifica que haya suficientes datos de tendencias. Ajusta `timeframe_months` si es necesario.

---

## 📈 Mejores Prácticas

1. **Ejecutar regularmente**: Semanal o quincenal para mantener datos actualizados
2. **Revisar insights de alta prioridad**: Acción inmediata en insights críticos
3. **Monitorear tendencias históricas**: Usar base de datos para análisis comparativo
4. **Personalizar keywords**: Ajustar keywords según tu industria y negocio
5. **Configurar notificaciones**: Mantener alertas activas para no perder oportunidades

---

## 🚀 Mejoras Implementadas

### ✨ Nuevas Funcionalidades

1. **Machine Learning para Predicciones**
   - Predicción de tendencias futuras usando Random Forest y Gradient Boosting
   - Detección automática de anomalías en tendencias
   - Scoring inteligente de oportunidades (0-100)
   - Entrenamiento automático de modelos por métrica

2. **Dashboards Visuales Interactivos**
   - Dashboard HTML con Chart.js
   - Visualizaciones de tendencias en tiempo real
   - Filtros por prioridad, categoría, oportunidades y riesgos
   - Métricas clave destacadas
   - Diseño responsive y moderno

3. **Análisis de Anomalías**
   - Detección automática de spikes y drops
   - Severidad de anomalías (alta/media/baja)
   - Explicaciones automáticas de anomalías
   - Alertas proactivas

4. **Sistema de Scoring de Oportunidades**
   - Score 0-100 basado en múltiples factores
   - Priorización automática de oportunidades
   - Top 5 oportunidades destacadas
   - Contexto de mercado integrado

### 📊 Parámetros Nuevos

```python
{
    "enable_ml_predictions": True,  # Habilitar predicciones ML
    "generate_dashboard": True,      # Generar dashboard visual
    "dashboard_output_path": "/tmp/market_dashboard.html"
}
```

### 🎯 Uso de Mejoras

#### Predicciones ML
```python
# El sistema automáticamente:
# 1. Entrena modelos para cada métrica
# 2. Genera predicciones a 30 días
# 3. Detecta anomalías
# 4. Calcula scores de oportunidades
```

#### Dashboard Visual
```python
# Acceder al dashboard generado:
# - Ruta: /tmp/market_dashboard.html (configurable)
# - Abrir en navegador para visualización interactiva
# - Incluye gráficos, insights y predicciones
```

## 🚀 Próximos Pasos

1. **Configurar APIs reales**: Reemplazar simulaciones con APIs reales
2. **Personalizar análisis**: Ajustar según necesidades específicas
3. **Integrar con otros sistemas**: Conectar con CRM, BI tools, etc.
4. **Automatizar acciones**: Integrar con sistemas de automatización para acciones automáticas
5. **Mejorar modelos ML**: Agregar más features y fine-tuning
6. **Exportar a Excel/PDF**: Agregar exportación a múltiples formatos

---

## 📞 Soporte

Para preguntas o problemas:
1. Revisar logs en Airflow UI
2. Consultar documentación de plugins
3. Verificar configuración de APIs y base de datos

---

## 📝 Notas

- El sistema incluye circuit breakers y retry logic para resiliencia
- Los datos se cachean para optimizar uso de APIs
- Los análisis se guardan históricamente para comparación
- El sistema es escalable y puede manejar múltiples industrias simultáneamente

