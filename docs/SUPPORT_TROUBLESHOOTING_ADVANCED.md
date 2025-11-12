# 🚀 Sistema Avanzado de Troubleshooting - Guía Completa

## 📋 Resumen

Sistema avanzado de troubleshooting con Machine Learning, optimización automática de pasos, personalización según historial del cliente, y analytics avanzadas.

## 🎯 Características Principales

### 1. Detección Inteligente de Problemas

**Múltiples métodos de detección:**
- **Keyword Matching**: Coincidencias por palabras clave
- **Semantic Similarity**: Similitud semántica
- **ML Classification**: Clasificación con machine learning
- **LLM Analysis**: Análisis con Large Language Models
- **Hybrid**: Combinación de todos los métodos (recomendado)

```python
from workflow.kestra.flows.lib.support_troubleshooting_advanced import (
    TroubleshootingAdvanced,
    ProblemDetectionMethod
)

advanced = TroubleshootingAdvanced(db_connection=db_conn)

result = advanced.detect_problem_advanced(
    problem_description="No puedo conectarme a la base de datos",
    customer_email="cliente@example.com",
    method=ProblemDetectionMethod.HYBRID
)
```

### 2. Optimización Automática de Pasos

**Estrategias de optimización:**
- **Success Rate**: Ordenar pasos por tasa de éxito
- **Duration**: Ordenar por duración promedio
- **Customer Satisfaction**: Ordenar por satisfacción
- **Hybrid**: Combinación de factores (recomendado)

```python
optimized_steps = advanced.optimize_steps(
    problem_id="connection_error",
    customer_email="cliente@example.com",
    strategy=StepOptimizationStrategy.HYBRID
)
```

### 3. Predicción de Tiempo de Resolución

Predice el tiempo de resolución basado en:
- Datos históricos del problema
- Historial del cliente
- Nivel técnico del cliente

```python
prediction = advanced.predict_resolution_time(
    problem_id="connection_error",
    customer_email="cliente@example.com",
    technical_level="intermediate"
)

# Resultado:
# {
#   "estimated_minutes": 12,
#   "confidence": 0.85,
#   "min_minutes": 8,
#   "max_minutes": 18,
#   "sample_size": 45
# }
```

### 4. Personalización Según Historial

Guía personalizada basada en:
- Intentos previos del cliente
- Problemas comunes encontrados
- Tiempo promedio por paso
- Problemas recurrentes

```python
personalized = advanced.get_personalized_guidance(
    problem_id="connection_error",
    customer_email="cliente@example.com",
    step_number=2
)
```

### 5. Analytics y Métricas Avanzadas

```python
analytics = advanced.get_analytics(
    problem_id="connection_error",
    date_from=datetime.now() - timedelta(days=30),
    date_to=datetime.now()
)

# Resultado:
# {
#   "sessions": {
#     "total": 150,
#     "resolved": 120,
#     "escalated": 20,
#     "abandoned": 10
#   },
#   "metrics": {
#     "resolution_rate": 80.0,
#     "escalation_rate": 13.3,
#     "avg_duration_minutes": 12.5,
#     "avg_steps_completed": 4.2,
#     "avg_satisfaction": 4.5
#   }
# }
```

## 🔄 Workflow de Automatización

**Archivo**: `workflow/kestra/flows/troubleshooting_advanced_automation.yaml`

**Flujo completo:**
1. Obtiene información del cliente
2. Detecta problema usando métodos avanzados
3. Predice tiempo de resolución
4. Optimiza pasos según datos históricos
5. Crea sesión de troubleshooting
6. Genera respuesta inicial personalizada
7. Envía email al cliente
8. Actualiza ticket
9. Registra métricas

## 📊 Métricas y KPIs

### Métricas Clave

- **Tasa de resolución**: % de problemas resueltos sin escalación
- **Tasa de escalación**: % de casos que requieren especialista
- **Tiempo promedio de resolución**: Duración promedio en minutos
- **Pasos promedio completados**: Número promedio de pasos
- **Satisfacción del cliente**: Score promedio (1-5)
- **Tasa de abandono**: % de sesiones abandonadas

### Impacto Esperado

- ✅ **Mejora en detección**: +40-60% de precisión
- ✅ **Reducción de tiempo**: -30-50% tiempo de resolución
- ✅ **Mejora en satisfacción**: +25-35% satisfacción del cliente
- ✅ **Reducción de escalaciones**: -20-30% escalaciones innecesarias

## 🛠️ Integración

### Con Sistema de Tickets

```python
# Cuando se crea un ticket técnico
if ticket.category == "technical":
    # Iniciar troubleshooting avanzado
    workflow.trigger(
        "troubleshooting_advanced_automation",
        inputs={
            "ticket_id": ticket.ticket_id,
            "problem_description": ticket.description,
            "customer_email": ticket.customer_email,
            "customer_name": ticket.customer_name
        }
    )
```

### Con Templates

```python
from workflow.kestra.flows.lib.support_troubleshooting_templates import (
    get_troubleshooting_start_template,
    get_troubleshooting_step_template
)

# Usar templates con datos optimizados
response = get_troubleshooting_start_template(
    ticket_data=ticket_data,
    problem_description=problem_description,
    detected_problem={
        "title": detected_problem["title"],
        "estimated_steps": len(optimized_steps),
        "estimated_time_minutes": prediction["estimated_minutes"]
    },
    technical_level=detected_technical_level,
    complexity=detected_complexity
)
```

## 📈 Aprendizaje Automático

### Tracking de Pasos

```python
# Registrar finalización de paso
advanced.track_step_completion(
    session_id="TSESS-123",
    step_number=2,
    success=True,
    duration_seconds=45,
    notes="Cliente completó exitosamente"
)
```

### Optimización Continua

El sistema aprende automáticamente de:
- Tasa de éxito de cada paso
- Duración promedio por paso
- Problemas comunes encontrados
- Satisfacción del cliente

## 🔧 Configuración

### Variables de Entorno

```bash
# Base de datos
POSTGRES_URL=postgresql://user:pass@host:5432/db
POSTGRES_USER=user
POSTGRES_PASSWORD=pass

# Email
SUPPORT_EMAIL_FROM=support@example.com

# ML/LLM (opcional)
OPENAI_API_KEY=sk-...
ML_MODEL_ENDPOINT=https://...
```

### Configuración de Kestra

1. Importar workflow: `troubleshooting_advanced_automation.yaml`
2. Configurar webhooks desde sistema de tickets
3. Configurar variables de entorno
4. Probar con ticket de prueba

## 📚 Ejemplos de Uso

### Ejemplo 1: Detección Básica

```python
from workflow.kestra.flows.lib.support_troubleshooting_advanced import (
    TroubleshootingAdvanced,
    ProblemDetectionMethod
)

advanced = TroubleshootingAdvanced(db_connection=db_conn)

result = advanced.detect_problem_advanced(
    problem_description="Error al conectarse a la base de datos",
    method=ProblemDetectionMethod.KEYWORD_MATCHING
)

print(f"Problema: {result['problem_id']}")
print(f"Confianza: {result['confidence']:.2%}")
```

### Ejemplo 2: Optimización Completa

```python
from workflow.kestra.flows.lib.support_troubleshooting_advanced import (
    TroubleshootingAdvanced,
    ProblemDetectionMethod,
    StepOptimizationStrategy
)

advanced = TroubleshootingAdvanced(db_connection=db_conn)

# Detectar problema
detection = advanced.detect_problem_advanced(
    problem_description="No puedo iniciar sesión",
    method=ProblemDetectionMethod.HYBRID
)

# Optimizar pasos
steps = advanced.optimize_steps(
    problem_id=detection["problem_id"],
    strategy=StepOptimizationStrategy.HYBRID
)

# Predecir tiempo
prediction = advanced.predict_resolution_time(
    problem_id=detection["problem_id"]
)

print(f"Pasos optimizados: {len(steps)}")
print(f"Tiempo estimado: {prediction['estimated_minutes']} minutos")
```

### Ejemplo 3: Analytics

```python
# Obtener analytics del último mes
analytics = advanced.get_analytics(
    date_from=datetime.now() - timedelta(days=30)
)

print(f"Tasa de resolución: {analytics['metrics']['resolution_rate']:.1f}%")
print(f"Tiempo promedio: {analytics['metrics']['avg_duration_minutes']:.1f} minutos")
print(f"Satisfacción: {analytics['metrics']['avg_satisfaction']:.1f}/5.0")
```

## 🎯 Mejores Prácticas

1. **Usar detección híbrida**: Mejor precisión
2. **Optimización híbrida**: Mejor balance
3. **Tracking continuo**: Aprender de cada sesión
4. **Personalización**: Usar historial del cliente
5. **Analytics regular**: Monitorear métricas semanalmente

## 🔄 Mejoras Futuras

- [ ] Modelos ML entrenados específicamente
- [ ] Integración con más LLMs
- [ ] Predicción de escalación
- [ ] Recomendaciones proactivas
- [ ] Dashboard en tiempo real
- [ ] A/B testing de estrategias

## 📞 Soporte

Para preguntas o problemas:
- Revisar documentación completa
- Ejecutar ejemplos de uso
- Revisar logs del workflow
- Contactar al equipo de desarrollo

---

**Versión**: 2.0  
**Última actualización**: Diciembre 2024  
**Mantenido por**: Equipo de Automatización de Soporte



