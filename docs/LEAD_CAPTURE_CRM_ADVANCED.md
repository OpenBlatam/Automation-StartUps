# Sistema de Captura de Leads - Funcionalidades Avanzadas

## 🤖 Machine Learning Scoring

### Configuración

El sistema incluye scoring ML predictivo que aprende de datos históricos.

**Requisitos:**
```bash
pip install scikit-learn pandas numpy
```

**Modelos Disponibles:**
1. **Gradient Boosting** (recomendado)
2. **Random Forest**
3. **Neural Network** (próximamente)

### Entrenamiento del Modelo

El modelo se entrena automáticamente con:
- Leads históricos (últimos 90 días)
- Features: score inicial, valor estimado, probabilidad, tiempo de contacto
- Target: Conversión (closed_won = 1, otros = 0)

**Reentrenar Modelo:**
```python
# En Airflow UI, configurar:
{
    "retrain_model": true,
    "ml_model_type": "gradient_boosting"
}
```

### Interpretación de Scores ML

- **ML Score**: 0-100, probabilidad de conversión
- **ML Conversion Probability**: Probabilidad decimal (0.0-1.0)
- Se combina con score inicial para obtener score final

## 🌱 Nurturing Avanzado

### Secuencias Personalizadas

Cada segmento tiene su propia secuencia:

**Premium Segment:**
```
Día 1: Email Welcome (premium_welcome)
Día 3: Email Value Prop (premium_value_prop)
Día 5: Email Case Study (premium_case_study)
Día 7: Email Demo Request (premium_demo_request)
```

**High Priority Segment:**
```
Día 1: Email Welcome
Día 3: Email Benefits
Día 5: SMS Followup
```

### Personalización de Templates

Los templates se pueden personalizar en tu servicio de email:

```json
{
  "template": "premium_welcome",
  "data": {
    "first_name": "Juan",
    "company": "Mi Empresa",
    "lead_ext_id": "WEB-ABC123"
  }
}
```

### Pausa Automática

El nurturing se pausa automáticamente si:
- El lead responde
- El lead cambia de stage
- El lead es contactado manualmente

### Reactivación

Leads fríos se reactivan automáticamente después de 30 días sin contacto.

## 📈 Forecasting

### Pipeline Value Forecast

Predice el valor del pipeline basado en:
- Tasa de conversión histórica
- Valor promedio de deals
- Leads actuales en pipeline

**Ejemplo:**
```json
{
  "pipeline_value": {
    "current_pipeline_value": 500000,
    "forecasted_value": 350000,
    "conversion_rate": 0.25,
    "avg_deal_value": 50000,
    "confidence": 0.8
  }
}
```

### Time to Close Forecast

Predice tiempo promedio hasta cierre basado en datos históricos.

### Lead Generation Forecast

Predice cuántos leads se generarán en los próximos N días con intervalo de confianza.

## 🔧 Integración con Servicios Externos

### Email Service

```python
# Ejemplo de integración con SendGrid
EMAIL_API_URL = "https://api.sendgrid.com/v3/mail/send"

# El sistema envía:
{
    "to": "lead@example.com",
    "template": "premium_welcome",
    "data": {...}
}
```

### SMS Service

```python
# Ejemplo de integración con Twilio
SMS_API_URL = "https://api.twilio.com/2010-04-01/Accounts/.../Messages.json"

# El sistema envía:
{
    "to": "+34612345678",
    "template": "high_priority_followup",
    "data": {...}
}
```

## 📊 Analytics Avanzados

### Métricas Personalizadas

El sistema calcula automáticamente:
- Conversión por etapa
- Tiempo promedio en cada etapa
- Performance por vendedor
- Performance por fuente
- Trends diarios
- Pipeline value

### Exportación de Datos

Los analytics se guardan en:
- Tabla `lead_analytics` (diario)
- Tabla `lead_forecasts` (semanal)
- Disponibles vía API REST

## 🎯 Mejores Prácticas

### Scoring ML

1. **Reentrenar Regularmente**: Cada mes o cuando haya cambios significativos
2. **Validar Métricas**: Verificar accuracy, precision, recall
3. **Ajustar Features**: Agregar features relevantes según tu negocio
4. **Monitorear Drift**: Detectar cambios en distribución de datos

### Nurturing

1. **Personalizar Templates**: Adaptar mensajes a tu marca
2. **Ajustar Frecuencia**: Según respuesta de leads
3. **Segmentar Bien**: Usar segmentación para personalización
4. **Testear Secuencias**: A/B testing de diferentes secuencias

### Forecasting

1. **Actualizar Regularmente**: Semanal para predicciones precisas
2. **Ajustar Confianza**: Según volatilidad de tu negocio
3. **Comparar con Realidad**: Validar predicciones con resultados reales
4. **Usar para Planning**: Para planificación de recursos

## 🔐 Seguridad y Compliance

### GDPR Compliance

- Datos personales se guardan de forma segura
- Opción de eliminación de datos
- Consentimiento tracking en metadata

### Rate Limiting

Los servicios incluyen rate limiting para:
- Prevenir spam
- Proteger APIs externas
- Mantener costos bajo control

## 🚀 Escalamiento

### Performance

- Procesamiento en lotes (batch)
- Caché de resultados
- Optimización de queries

### Escalabilidad

- Horizontal scaling de servicios
- Load balancing de APIs
- Database connection pooling

## 📚 Referencias Adicionales

- [Scikit-learn Documentation](https://scikit-learn.org/)
- [Forecasting Best Practices](https://www.forecastpro.com/)
- [Email Marketing Best Practices](https://mailchimp.com/marketing-guide/)

