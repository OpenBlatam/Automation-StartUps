# Calendario de Contenido y ROI - Sistema de Testimonios

## 📅 Nuevo Módulo: Content Calendar Generator

Sistema de generación de calendarios optimizados para planificar publicaciones de testimonios.

### Funcionalidades

- ✅ **Calendario Semanal**: Genera calendario optimizado para 7 días
- ✅ **Calendario Mensual**: Planificación mensual completa
- ✅ **Horarios Óptimos**: Usa datos de mejores horarios por plataforma
- ✅ **Días Óptimos**: Considera mejores días de la semana
- ✅ **Exportación JSON**: Formato estructurado para integración
- ✅ **Exportación iCal**: Compatible con Google Calendar, Outlook, etc.

### Uso

#### Calendario Semanal

```bash
python scripts/testimonial_to_social_post.py \
  "[TESTIMONIO]" \
  "[PROBLEMA]" \
  --generate-calendar \
  --calendar-type weekly \
  --calendar-platforms linkedin instagram \
  --calendar-output calendars/semana_actual.json
```

#### Calendario Mensual

```bash
python scripts/testimonial_to_social_post.py \
  "[TESTIMONIO]" \
  "[PROBLEMA]" \
  --generate-calendar \
  --calendar-type monthly \
  --calendar-platforms linkedin instagram facebook \
  --calendar-output calendars/mes_actual.json
```

### Estructura del Calendario

```json
{
  "start_date": "2024-01-15T00:00:00",
  "end_date": "2024-01-21T23:59:59",
  "events": [
    {
      "date": "2024-01-16T09:00:00",
      "platform": "linkedin",
      "content_type": "testimonial",
      "optimal_time": "09:00-11:00",
      "day_name": "Tuesday",
      "notes": "Publicación optimizada para linkedin"
    }
  ],
  "summary": {
    "total_events": 12,
    "events_by_platform": {
      "linkedin": 6,
      "instagram": 6
    },
    "events_by_day": {
      "Tuesday": 3,
      "Wednesday": 3,
      "Thursday": 3
    }
  }
}
```

### Integración con Calendarios

El archivo `.ics` generado puede importarse en:
- Google Calendar
- Outlook
- Apple Calendar
- Cualquier aplicación compatible con iCal

## 💰 Nuevo Módulo: ROI Calculator

Calculadora de retorno de inversión para evaluar el valor potencial de publicaciones.

### Funcionalidades

- ✅ **Cálculo Individual**: ROI por publicación
- ✅ **Cálculo de Campaña**: ROI agregado de múltiples posts
- ✅ **Optimización de Presupuesto**: Distribución óptima de recursos
- ✅ **Métricas Completas**: Reach, engagement, clicks, conversiones, ingresos
- ✅ **Período de Recuperación**: Tiempo para recuperar inversión

### Uso Básico

```python
from testimonial_roi_calculator import ROICalculator

calculator = ROICalculator()

# Calcular ROI de una publicación
roi = calculator.calculate_roi(
    predicted_engagement_rate=5.2,
    estimated_reach=2000,
    platform="linkedin"
)

print(f"ROI: {roi.roi_percentage}%")
print(f"Ingresos estimados: ${roi.estimated_revenue}")
print(f"Conversiones: {roi.estimated_conversions}")
```

### Métricas Calculadas

- **Alcance Estimado**: Personas que verán el contenido
- **Engagement Estimado**: Interacciones esperadas
- **Clicks Estimados**: Clicks en enlaces/CTAs
- **Conversiones Estimadas**: Conversiones basadas en tasa promedio
- **Ingresos Estimados**: Valor generado por conversiones
- **ROI Porcentual**: Retorno sobre inversión (%)
- **ROI Multiplicador**: Múltiplo de retorno (x2.5 = 250% ROI)
- **Período de Recuperación**: Días para recuperar inversión

### Tasas de Conversión por Plataforma

- **LinkedIn**: 2.0% (más alto para B2B)
- **Instagram**: 1.5% (alto engagement visual)
- **Facebook**: 1.0% (audiencia amplia)
- **Twitter**: 0.8% (rápido, menos conversión)
- **TikTok**: 1.2% (audiencia joven)

### Optimización de Presupuesto

```python
# Optimizar distribución de presupuesto
optimization = calculator.optimize_for_roi(
    platforms=['linkedin', 'instagram', 'facebook'],
    budget=1000.0,
    target_roi=2.0
)

print(f"Presupuesto asignado: ${optimization['allocated_budget']}")
print(f"Posts totales: {optimization['total_posts']}")
print(f"ROI esperado: ${optimization['expected_roi']}")
```

### Cálculo de Campaña Completa

```python
# Calcular ROI de múltiples publicaciones
posts = [
    {
        'platform': 'linkedin',
        'engagement_prediction': {'predicted_engagement_rate': 5.2},
        'estimated_reach': 2000
    },
    {
        'platform': 'instagram',
        'engagement_prediction': {'predicted_engagement_rate': 4.8},
        'estimated_reach': 3000
    }
]

campaign_roi = calculator.calculate_campaign_roi(posts)
print(f"ROI de campaña: {campaign_roi['roi_percentage']}%")
print(f"Ingresos totales: ${campaign_roi['total_revenue']}")
```

## 📊 Ejemplo de Output de ROI

```
💰 Análisis de ROI:
  Alcance estimado: 2,000
  Engagement estimado: 104
  Conversiones estimadas: 1
  Ingresos estimados: $100.00
  Costo por post: $50.00
  ROI: 100.0% (x2.00)
  Período de recuperación: 3.5 días
```

## 🎯 Integración Completa

### Ejemplo con Todas las Funcionalidades

```bash
python scripts/testimonial_to_social_post.py \
  "[TESTIMONIO]" \
  "[PROBLEMA]" \
  --platform linkedin \
  --predict-engagement \
  --optimize-engagement \
  --generate-calendar \
  --calendar-type weekly \
  --generate-dashboard \
  --verbose
```

El sistema automáticamente:
1. Genera publicación optimizada
2. Predice engagement
3. Calcula ROI potencial
4. Genera calendario semanal
5. Crea dashboard visual

## 📈 Interpretación de Métricas ROI

### ROI Porcentual
- **> 200%**: Excelente inversión
- **100-200%**: Buena inversión
- **50-100%**: Inversión aceptable
- **< 50%**: Revisar estrategia

### ROI Multiplicador
- **x3.0+**: Retorno excelente (300% ROI)
- **x2.0-3.0**: Retorno bueno (200-300% ROI)
- **x1.5-2.0**: Retorno aceptable (150-200% ROI)
- **< x1.5**: Retorno bajo

### Período de Recuperación
- **< 3 días**: Recuperación rápida
- **3-7 días**: Recuperación normal
- **7-14 días**: Recuperación lenta
- **> 14 días**: Revisar estrategia

## 🔧 Personalización

### Ajustar Tasas de Conversión

```python
calculator = ROICalculator(
    conversion_rates={
        'linkedin': 0.03,  # 3% para tu industria
        'instagram': 0.02
    },
    value_per_conversion=150.0  # Valor por conversión
)
```

### Ajustar Costos por Post

```python
calculator = ROICalculator(
    cost_per_post={
        'linkedin': 75.0,  # Tu costo real
        'instagram': 60.0
    }
)
```

## 📝 Mejores Prácticas

1. **Usar Datos Reales**: Ajusta tasas de conversión según tu industria
2. **Monitorear Resultados**: Compara predicciones con resultados reales
3. **Optimizar Continuamente**: Usa datos de tracking para mejorar cálculos
4. **Planificar con Calendario**: Usa calendarios para distribución óptima
5. **Calcular ROI Regularmente**: Evalúa ROI de campañas completas

## 🚀 Próximos Pasos

- [ ] Integración con APIs de redes sociales para métricas reales
- [ ] Dashboard de ROI en tiempo real
- [ ] Alertas cuando ROI baja de umbral
- [ ] Comparación de ROI entre plataformas
- [ ] Predicción de ROI con ML


