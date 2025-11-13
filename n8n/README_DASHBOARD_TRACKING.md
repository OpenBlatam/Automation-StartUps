# Dashboard y Tracking - Sistema de Testimonios

## 🎨 Nuevo Módulo: Dashboard Generator

Sistema de generación de dashboards HTML interactivos con visualizaciones en tiempo real.

### Características

- ✅ **Visualizaciones Interactivas**: Gráficos usando Chart.js
- ✅ **Métricas en Tiempo Real**: Tarjetas con métricas clave
- ✅ **Gráficos Dinámicos**: Barras, radar, donut charts
- ✅ **Diseño Moderno**: UI profesional y responsive
- ✅ **Exportación HTML**: Listo para compartir o integrar

### Uso

```bash
python scripts/testimonial_to_social_post.py \
  "[TESTIMONIO]" \
  "[PROBLEMA]" \
  --predict-engagement \
  --generate-report \
  --generate-dashboard \
  --dashboard-output reports/mi_dashboard.html
```

### Elementos del Dashboard

1. **Tarjetas de Métricas**:
   - Score de Engagement
   - Engagement Rate Estimado
   - Score General con Calificación
   - Longitud del Contenido
   - Cantidad de Hashtags

2. **Gráficos Interactivos**:
   - Factores de Engagement (barras)
   - Comparación con Benchmarks (radar)
   - Distribución del Score (donut)

3. **Recomendaciones**:
   - Lista de recomendaciones accionables
   - Basadas en análisis completo

## 📊 Nuevo Módulo: Post Tracker

Sistema de tracking post-publicación que rastrea el rendimiento real y mejora predicciones.

### Funcionalidades

- ✅ **Tracking Automático**: Registra predicciones vs realidad
- ✅ **Cálculo de Precisión**: Mide qué tan acertadas fueron las predicciones
- ✅ **Estadísticas Agregadas**: Análisis de precisión por plataforma
- ✅ **Sugerencias de Mejora**: Detecta sesgos y áreas de mejora
- ✅ **Exportación ML**: Datos listos para entrenamiento de ML

### Uso Básico

```python
from testimonial_tracker import PostTracker

# Crear tracker
tracker = PostTracker(tracking_file="data/my_tracking.json")

# Registrar publicación
tracker.track_post(
    post_id="post_123",
    platform="linkedin",
    predicted_data={
        "predicted_engagement_rate": 5.2,
        "predicted_score": 85
    },
    actual_data={
        "likes": 120,
        "comments": 25,
        "shares": 10,
        "impressions": 2500,
        "reach": 2000
    }
)

# Obtener estadísticas
stats = tracker.get_tracking_stats()
print(f"Precisión promedio: {stats['average_accuracy']}%")
```

### Integración con el Sistema Principal

```bash
python scripts/testimonial_to_social_post.py \
  "[TESTIMONIO]" \
  "[PROBLEMA]" \
  --predict-engagement \
  --enable-tracking \
  --tracking-file data/tracking.json
```

Luego, después de publicar y obtener métricas reales:

```python
from testimonial_tracker import PostTracker

tracker = PostTracker(tracking_file="data/tracking.json")

# Registrar resultados reales
tracker.track_post(
    post_id="generated_post_001",
    platform="linkedin",
    predicted_data=predicted_data,  # De la generación original
    actual_data={
        "likes": 150,
        "comments": 30,
        "shares": 12,
        "impressions": 3000,
        "reach": 2500
    }
)

# Ver estadísticas
stats = tracker.get_tracking_stats()
print(stats)
```

## 📈 Estadísticas de Tracking

El tracker proporciona:

- **Precisión Promedio**: Qué tan acertadas son las predicciones
- **Sesgo de Predicción**: Si sobreestima o subestima
- **Estadísticas por Plataforma**: Precisión específica por red social
- **Mejores/Peores Predicciones**: Identifica casos extremos
- **Sugerencias de Mejora**: Recomendaciones basadas en datos

### Ejemplo de Output

```json
{
  "total_tracked": 25,
  "average_accuracy": 78.5,
  "average_predicted_rate": 5.2,
  "average_actual_rate": 5.8,
  "prediction_bias": -0.6,
  "platform_stats": {
    "linkedin": {
      "count": 15,
      "avg_accuracy": 82.3,
      "avg_predicted": 4.8,
      "avg_actual": 5.1
    },
    "instagram": {
      "count": 10,
      "avg_accuracy": 73.2,
      "avg_predicted": 6.1,
      "avg_actual": 6.9
    }
  },
  "improvement_suggestions": [
    "Las predicciones están subestimando en promedio 0.6%. El contenido puede ser mejor de lo esperado.",
    "La precisión en instagram es baja (73.2%). Considera recopilar más datos históricos para esta plataforma."
  ]
}
```

## 🔄 Flujo Completo con Tracking

1. **Generar Publicación**:
```bash
python scripts/testimonial_to_social_post.py \
  "[TESTIMONIO]" \
  "[PROBLEMA]" \
  --predict-engagement \
  --enable-tracking \
  --output json > post_data.json
```

2. **Publicar en Red Social** (manual o automático)

3. **Obtener Métricas Reales** (desde API de la red social)

4. **Registrar Resultados**:
```python
import json
from testimonial_tracker import PostTracker

# Cargar datos de predicción
with open('post_data.json') as f:
    post_data = json.load(f)

tracker = PostTracker()

# Registrar resultados reales
tracker.track_post(
    post_id=post_data['metadata'].get('post_id', 'post_001'),
    platform=post_data['platform'],
    predicted_data=post_data['engagement_prediction'],
    actual_data={
        "likes": 150,  # De API de red social
        "comments": 30,
        "shares": 12,
        "impressions": 3000,
        "reach": 2500
    }
)
```

5. **Analizar Precisión**:
```python
stats = tracker.get_tracking_stats()
print(f"Precisión: {stats['average_accuracy']}%")
for suggestion in stats['improvement_suggestions']:
    print(f"💡 {suggestion}")
```

## 🎯 Mejora Continua

El sistema aprende de los datos de tracking:

1. **Ajuste de Predicciones**: Las predicciones mejoran con más datos
2. **Detección de Sesgos**: Identifica si sobreestima o subestima
3. **Optimización por Plataforma**: Ajusta según precisión por red social
4. **Exportación ML**: Datos listos para modelos de ML avanzados

### Exportar para ML

```python
tracker.export_for_ml_training("data/ml_training_data.json")
```

Esto genera un archivo JSON con datos estructurados para entrenar modelos de ML que mejoren las predicciones.

## 📊 Dashboard Interactivo

### Características Visuales

- **Gráfico de Factores**: Muestra impacto de cada factor en engagement
- **Comparación Benchmark**: Radar chart comparando con industria
- **Distribución Score**: Donut chart mostrando componentes del score
- **Métricas Clave**: Tarjetas destacadas con valores importantes
- **Recomendaciones**: Lista visual de mejoras sugeridas

### Personalización

El dashboard se genera automáticamente con:
- Colores profesionales
- Diseño responsive
- Gráficos interactivos (hover para detalles)
- Badges de calificación visuales

## 🔧 Integración con Workflows

### n8n Workflow Example

1. **Webhook** → Recibe testimonio
2. **Code Node** → Genera publicación con predicción
3. **HTTP Request** → Publica en red social
4. **Wait** → Espera 24-48 horas
5. **HTTP Request** → Obtiene métricas reales
6. **Code Node** → Registra en tracker
7. **Email/Slack** → Notifica resultados y precisión

## 📝 Mejores Prácticas

1. **Tracking Consistente**: Registra todas las publicaciones
2. **Métricas Completas**: Incluye likes, comments, shares, impressions
3. **Revisar Regularmente**: Analiza estadísticas periódicamente
4. **Ajustar Estrategia**: Usa insights para mejorar contenido
5. **Exportar para ML**: Usa datos acumulados para entrenar modelos

## 🚀 Próximos Pasos

- [ ] Integración automática con APIs de redes sociales
- [ ] Dashboard en tiempo real con WebSockets
- [ ] Alertas automáticas cuando precisión baja
- [ ] Modelos ML entrenados con datos de tracking
- [ ] Comparación con competidores usando tracking


