# Mejoras Avanzadas V2 - Sistema de Adquisición Orgánica

## Resumen Ejecutivo

Se han agregado **6 nuevas funcionalidades avanzadas** al DAG de Airflow para mejorar aún más las capacidades del sistema de adquisición orgánica:

1. **Análisis de Sentimiento** - Analiza feedback y respuestas de leads
2. **Sistema de Tags Avanzado** - Segmentación automática con tags inteligentes
3. **Exportación de Datos** - Exporta datos en JSON o CSV para análisis externo
4. **Webhooks de Eventos** - Notificaciones en tiempo real para eventos importantes
5. **Recomendaciones Inteligentes** - Sugerencias basadas en datos para optimización
6. **Análisis de Tendencias** - Identifica patrones y tendencias en los datos

---

## 1. Análisis de Sentimiento (`sentiment_analysis`)

### Descripción
Analiza el sentimiento de feedback y respuestas de leads para identificar satisfacción, problemas o áreas de mejora.

### Funcionalidades
- **Análisis de texto**: Detecta palabras positivas y negativas en feedback
- **Scoring de sentimiento**: Calcula un score de -1 a 1 para cada feedback
- **Clasificación**: Categoriza como positivo, negativo o neutral
- **Estadísticas agregadas**: Genera métricas de satisfacción general

### Implementación
- Busca feedbacks de los últimos 30 días
- Analiza texto usando diccionarios de palabras clave
- Calcula score basado en frecuencia de palabras positivas/negativas
- Retorna estadísticas y top 20 resultados

### Métricas Retornadas
```json
{
  "analyzed": 100,
  "positive": 65,
  "negative": 15,
  "neutral": 20,
  "positive_rate": 65.0,
  "results": [...]
}
```

### Requisitos
- Tabla `lead_feedback` con columnas: `lead_id`, `feedback_text`, `created_at`

---

## 2. Sistema de Tags Avanzado (`advanced_tagging`)

### Descripción
Aplica tags automáticamente a leads basándose en su comportamiento, engagement, fuente y actividad para facilitar segmentación.

### Tags Aplicados
- **Por Engagement**:
  - `high_engagement` (score >= 10)
  - `medium_engagement` (score >= 5)
  - `low_engagement` (score < 5)

- **Por Comportamiento**:
  - `content_consumer` (3+ contenidos completados)
  - `active_reader` (5+ contenidos enviados)

- **Por Fuente**:
  - `referred` (si viene de referido)
  - `interest_{area}` (según área de interés)

- **Por Status**:
  - `engaged`
  - `in_nurturing`

- **Por Tiempo**:
  - `inactive` (sin actividad >7 días)
  - `recent_activity` (actividad <3 días)

### Implementación
- Analiza leads de los últimos 30 días
- Calcula tags basándose en múltiples criterios
- Actualiza columna `tags` (JSONB) en base de datos
- Retorna estadísticas de tags aplicados

### Métricas Retornadas
```json
{
  "tagged": 200,
  "tags_applied": {
    "high_engagement": 45,
    "content_consumer": 32,
    "referred": 18,
    ...
  },
  "total_tags": 350
}
```

### Requisitos
- Columna `tags` tipo JSONB en tabla `organic_leads`

---

## 3. Exportación de Datos (`export_data`)

### Descripción
Exporta datos de leads, engagement y referidos en formatos JSON o CSV para análisis externo, reportes o integraciones.

### Funcionalidades
- **Múltiples formatos**: JSON y CSV
- **Datos completos**: Incluye leads, engagement, referidos
- **Período configurable**: Últimos 30 días por defecto
- **Archivos únicos**: Genera IDs únicos para cada exportación

### Datos Exportados
- Información básica del lead
- Status y engagement score
- Total de contenidos enviados
- Total de referidos generados
- Fechas de creación y engagement

### Implementación
- Consulta datos agregados de leads
- Formatea según tipo de exportación
- Guarda archivo en `/tmp/` con ID único
- Retorna ruta y estadísticas

### Parámetros
- `export_format`: "json" o "csv" (default: "json")

### Métricas Retornadas
```json
{
  "exported": 150,
  "export_id": "export_a1b2c3d4",
  "export_path": "/tmp/organic_acquisition_export_a1b2c3d4.json",
  "format": "json"
}
```

---

## 4. Webhooks de Eventos (`event_webhooks`)

### Descripción
Envía notificaciones en tiempo real vía webhooks cuando ocurren eventos importantes (leads engaged, referidos validados).

### Eventos Soportados
- **`lead_engaged`**: Cuando un lead alcanza status "engaged"
- **`referral_validated`**: Cuando un referido es validado exitosamente

### Funcionalidades
- **Notificaciones en tiempo real**: Eventos de la última hora
- **Payload estructurado**: JSON con toda la información del evento
- **Prevención de duplicados**: Marca eventos como enviados
- **Manejo de errores**: Registra fallos sin interrumpir el flujo

### Payload del Webhook
```json
{
  "event_type": "lead_engaged",
  "lead_id": 123,
  "email": "lead@example.com",
  "event_time": "2024-01-15T10:30:00",
  "timestamp": "2024-01-15T10:30:05"
}
```

### Implementación
- Busca eventos recientes sin webhook enviado
- Envía POST request a URL configurada
- Marca eventos como procesados
- Usa HTTP session pooling para eficiencia

### Parámetros
- `event_webhook_url`: URL del endpoint webhook (opcional)

### Métricas Retornadas
```json
{
  "sent": 25,
  "failed": 2
}
```

### Requisitos
- Columnas `webhook_sent` (boolean) en tablas `organic_leads` y `referrals`

---

## 5. Recomendaciones Inteligentes (`intelligent_recommendations`)

### Descripción
Genera recomendaciones automáticas basadas en análisis de datos para optimizar el sistema.

### Tipos de Recomendaciones

#### 1. Optimización de Timing
- Analiza mejor hora para envío de contenido
- Basado en completion rate por hora
- Prioridad: **Alta** si completion rate > 30%

#### 2. Priorización de Contenido
- Identifica tipo de contenido con mejor performance
- Basado en completion rate por tipo
- Prioridad: **Media**

#### 3. Mejora de Engagement
- Detecta engagement promedio bajo
- Compara con objetivo (>2)
- Prioridad: **Alta** si score < 2

#### 4. Optimización de Referidos
- Analiza tasa de validación de referidos
- Detecta alta tasa de fraude
- Prioridad: **Media/Alta** según métricas

### Estructura de Recomendación
```json
{
  "type": "timing",
  "priority": "high",
  "title": "Optimizar Horario de Envío",
  "message": "Mejor hora para envío: 14:00 (completion rate: 45.2%)",
  "action": "Programar envíos a las 14:00"
}
```

### Métricas Retornadas
```json
{
  "recommendations": [
    {...},
    {...}
  ],
  "total": 4,
  "high_priority": 2
}
```

---

## 6. Análisis de Tendencias (`trend_analysis`)

### Descripción
Analiza tendencias y patrones en los datos para identificar cambios, mejores fuentes y comportamiento temporal.

### Análisis Incluidos

#### 1. Tendencias Diarias
- Leads y engagement por día (últimos 14 días)
- Cálculo de engagement rate diario
- Identificación de tendencia: creciente, decreciente o estable

#### 2. Análisis de Fuentes
- Performance por fuente de adquisición
- Engagement rate por fuente
- Identificación de mejor fuente

#### 3. Cálculo de Tendencia
- Compara promedio de últimos 7 días vs anteriores
- Calcula porcentaje de cambio
- Clasifica como:
  - `increasing` (>10% aumento)
  - `decreasing` (>10% disminución)
  - `stable` (cambio <10%)

### Métricas Retornadas
```json
{
  "daily_trends": [
    {
      "date": "2024-01-15",
      "leads": 25,
      "engaged": 8,
      "engagement_rate": 32.0
    },
    ...
  ],
  "trend_direction": "increasing",
  "trend_percentage": 15.5,
  "source_trends": [
    {
      "source": "organic",
      "total": 150,
      "engaged": 45,
      "engagement_rate": 30.0
    },
    ...
  ],
  "best_source": {
    "source": "referral",
    "engagement_rate": 55.0
  }
}
```

---

## Integración en el Pipeline

Todas las nuevas tareas se ejecutan en **paralelo** después de las tareas principales:

```python
# Tareas avanzadas V2 (paralelas)
sentiment = sentiment_analysis()
tagging = advanced_tagging()
export = export_data()
webhooks = event_webhooks()
recommendations = intelligent_recommendations()
trends = trend_analysis()
```

### Dependencias
- Todas las tareas dependen de `schema_ok` (esquema de BD)
- Se ejecutan en paralelo con otras tareas avanzadas
- No bloquean el flujo principal

---

## Nuevos Parámetros del DAG

```python
# Exportación y webhooks
"export_format": Param("json", type="string", enum=["json", "csv"]),
"event_webhook_url": Param("", type="string"),
```

---

## Requisitos de Base de Datos

### Tablas/Columnas Adicionales Necesarias

1. **Tabla `lead_feedback`** (para análisis de sentimiento):
```sql
CREATE TABLE IF NOT EXISTS lead_feedback (
    feedback_id SERIAL PRIMARY KEY,
    lead_id INTEGER REFERENCES organic_leads(lead_id),
    feedback_text TEXT,
    created_at TIMESTAMP DEFAULT NOW()
);
```

2. **Columna `tags` en `organic_leads`** (para tagging):
```sql
ALTER TABLE organic_leads 
ADD COLUMN IF NOT EXISTS tags JSONB DEFAULT '[]'::jsonb;
```

3. **Columnas `webhook_sent`** (para webhooks):
```sql
ALTER TABLE organic_leads 
ADD COLUMN IF NOT EXISTS webhook_sent BOOLEAN DEFAULT false;

ALTER TABLE referrals 
ADD COLUMN IF NOT EXISTS webhook_sent BOOLEAN DEFAULT false;
```

---

## Beneficios

### 1. **Mejor Comprensión del Cliente**
- Análisis de sentimiento identifica satisfacción y problemas
- Tags facilitan segmentación y personalización

### 2. **Integración y Extensibilidad**
- Exportación permite análisis externo
- Webhooks habilitan integraciones en tiempo real

### 3. **Optimización Continua**
- Recomendaciones guían mejoras
- Análisis de tendencias identifica oportunidades

### 4. **Automatización Completa**
- Todo el proceso es automático
- Sin intervención manual requerida

---

## Próximos Pasos Sugeridos

1. **Implementar tablas/columnas** necesarias en base de datos
2. **Configurar webhook URL** si se requiere notificaciones
3. **Revisar recomendaciones** generadas en cada ejecución
4. **Analizar tendencias** para ajustar estrategias
5. **Usar exports** para análisis en herramientas externas (BI, Excel, etc.)

---

## Notas Técnicas

- Todas las tareas manejan errores gracefully
- Si faltan tablas/columnas, las tareas se saltan sin fallar
- Las tareas son idempotentes (pueden ejecutarse múltiples veces)
- Performance optimizado con queries eficientes
- Logging detallado para debugging

---

## Conclusión

Estas 6 nuevas funcionalidades complementan el sistema existente con:
- **Análisis avanzado** (sentimiento, tendencias)
- **Segmentación inteligente** (tags)
- **Integración externa** (exportación, webhooks)
- **Optimización guiada** (recomendaciones)

El sistema ahora es aún más completo y capaz de proporcionar insights valiosos para mejorar continuamente la adquisición orgánica.

