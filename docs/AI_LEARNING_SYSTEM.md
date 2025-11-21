# 🤖 Sistema de IA y Aprendizaje Automático - Troubleshooting

## Características de IA Implementadas

### 1. Predicción de Problemas

El sistema puede predecir qué problemas son más probables para un usuario específico basándose en su historial.

**Componente**: `TroubleshootingPredictor`

**Funcionalidades**:
- Analiza historial del usuario (últimos 90 días)
- Identifica patrones de problemas recurrentes
- Calcula probabilidad de ocurrencia
- Genera recomendaciones proactivas

**Ejemplo de uso**:
```python
from data.integrations.support_troubleshooting_ai import TroubleshootingPredictor

predictor = TroubleshootingPredictor(db_connection)
prediction = predictor.predict_next_problem("usuario@ejemplo.com")

if prediction:
    print(f"Problema probable: {prediction.problem_title}")
    print(f"Probabilidad: {prediction.probability:.1f}%")
    print(f"Confianza: {prediction.confidence:.1f}%")
    print(f"Razones: {prediction.reasons}")
    print(f"Acciones recomendadas: {prediction.recommended_actions}")
```

### 2. Recomendaciones Inteligentes

Sistema que recomienda soluciones basadas en descripción y contexto del usuario.

**Componente**: `TroubleshootingRecommender`

**Funcionalidades**:
- Recomendaciones basadas en historial del usuario
- Búsqueda de problemas similares
- Guías personalizadas según intentos previos
- Identificación de pasos problemáticos

**Ejemplo de uso**:
```python
from data.integrations.support_troubleshooting_ai import TroubleshootingRecommender

recommender = TroubleshootingRecommender(db_connection)

# Recomendar soluciones
recommendations = recommender.recommend_solutions(
    "No puedo instalar el software",
    customer_email="usuario@ejemplo.com"
)

# Obtener guía personalizada
personalized_guide = recommender.get_personalized_guide(
    "instalacion_software",
    "usuario@ejemplo.com"
)
```

### 3. Motor de Aprendizaje

Analiza la efectividad de las guías y sugiere mejoras automáticamente.

**Componente**: `TroubleshootingLearningEngine`

**Funcionalidades**:
- Análisis de efectividad por paso
- Identificación de pasos problemáticos
- Sugerencias de mejora automáticas
- Cálculo de tasas de éxito

**Ejemplo de uso**:
```python
from data.integrations.support_troubleshooting_ai import TroubleshootingLearningEngine

engine = TroubleshootingLearningEngine(db_connection)

# Analizar efectividad
analysis = engine.analyze_step_effectiveness("instalacion_software")

# Obtener sugerencias
suggestions = engine.suggest_guide_improvements("instalacion_software")
```

## Base de Datos

### Tablas Nuevas

1. **support_troubleshooting_user_patterns**
   - Almacena patrones de comportamiento de usuarios
   - Actualización automática mediante triggers

2. **support_troubleshooting_predictions**
   - Registra predicciones realizadas
   - Permite verificar precisión

3. **support_troubleshooting_step_effectiveness**
   - Analiza efectividad de cada paso
   - Identifica pasos que necesitan mejora

4. **support_troubleshooting_recommendations**
   - Almacena recomendaciones proactivas
   - Tracking de interacciones

### Funciones SQL

- `update_user_patterns()` - Actualiza patrones automáticamente
- `register_prediction()` - Registra una predicción
- `verify_prediction()` - Verifica si una predicción fue correcta
- `update_step_effectiveness()` - Actualiza efectividad de pasos

### Vistas

- `vw_active_predictions` - Predicciones activas sin verificar
- `vw_steps_needing_improvement` - Pasos que necesitan mejora

## API Endpoints

### POST `/api/support/troubleshooting/ai/predict`
Predice el siguiente problema probable del usuario.

**Request**:
```json
{
  "customer_email": "usuario@ejemplo.com",
  "context": {}
}
```

**Response**:
```json
{
  "prediction_id": "uuid",
  "problem_id": "instalacion_software",
  "problem_title": "Problemas con instalación",
  "probability": 75.5,
  "confidence": 80.0,
  "reasons": ["Este problema ha ocurrido 3 veces"],
  "recommended_actions": ["Revisar guía preventiva"],
  "estimated_impact": "medium"
}
```

### GET `/api/support/troubleshooting/ai/recommendations/{email}`
Obtiene recomendaciones proactivas.

**Response**:
```json
{
  "customer_email": "usuario@ejemplo.com",
  "recommendations": [
    {
      "type": "preventive",
      "title": "Problema frecuente",
      "description": "...",
      "priority": "high",
      "action": "view_preventive_guide"
    }
  ],
  "count": 1
}
```

### POST `/api/support/troubleshooting/ai/recommend-solutions`
Recomienda soluciones basadas en descripción.

**Request**:
```json
{
  "problem_description": "No puedo instalar",
  "customer_email": "usuario@ejemplo.com"
}
```

### GET `/api/support/troubleshooting/ai/personalized-guide/{problem_id}/{email}`
Obtiene guía personalizada.

### GET `/api/support/troubleshooting/ai/step-effectiveness/{problem_id}`
Analiza efectividad de pasos.

### GET `/api/support/troubleshooting/ai/improvement-suggestions/{problem_id}`
Obtiene sugerencias de mejora.

### POST `/api/support/troubleshooting/ai/verify-prediction/{prediction_id}`
Verifica si una predicción fue correcta.

### GET `/api/support/troubleshooting/ai/user-patterns/{email}`
Obtiene patrones de comportamiento del usuario.

## Instalación

### 1. Aplicar Schema SQL

```bash
psql $DATABASE_URL -f data/db/support_troubleshooting_ai_schema.sql
```

### 2. Verificar Instalación

```sql
-- Verificar tablas
SELECT table_name FROM information_schema.tables 
WHERE table_name LIKE 'support_troubleshooting%ai%';

-- Verificar funciones
SELECT proname FROM pg_proc 
WHERE proname LIKE '%prediction%' OR proname LIKE '%pattern%';
```

## Casos de Uso

### Caso 1: Predicción Proactiva

```python
# Cuando un usuario inicia sesión, predecir problemas
predictor = TroubleshootingPredictor(db)
prediction = predictor.predict_next_problem(user_email)

if prediction and prediction.probability > 70:
    # Enviar notificación proactiva
    send_notification(user_email, {
        "title": "Problema probable detectado",
        "message": f"Basado en tu historial, es probable que tengas problemas con: {prediction.problem_title}",
        "actions": prediction.recommended_actions
    })
```

### Caso 2: Guía Personalizada

```python
# Cuando un usuario inicia troubleshooting, personalizar guía
recommender = TroubleshootingRecommender(db)
guide = recommender.get_personalized_guide(problem_id, user_email)

if guide and guide.get("problematic_steps"):
    # Resaltar pasos problemáticos
    for step in guide["problematic_steps"]:
        highlight_step(step["step_number"], 
                      f"Este paso ha fallado {step['failure_count']} veces")
```

### Caso 3: Mejora Continua

```python
# Análisis semanal de efectividad
engine = TroubleshootingLearningEngine(db)

for problem_id in get_all_problem_ids():
    analysis = engine.analyze_step_effectiveness(problem_id)
    
    if analysis["overall_success_rate"] < 70:
        suggestions = engine.suggest_guide_improvements(problem_id)
        
        # Enviar sugerencias al equipo de contenido
        send_to_content_team(problem_id, suggestions)
```

## Métricas de IA

### Precisión de Predicciones

```sql
SELECT 
    COUNT(*) as total_predictions,
    COUNT(CASE WHEN was_correct = true THEN 1 END) as correct,
    COUNT(CASE WHEN was_correct = false THEN 1 END) as incorrect,
    ROUND(
        COUNT(CASE WHEN was_correct = true THEN 1 END)::NUMERIC / 
        NULLIF(COUNT(*), 0)::NUMERIC * 100, 
        2
    ) as accuracy_percentage
FROM support_troubleshooting_predictions
WHERE verified_at IS NOT NULL;
```

### Efectividad de Pasos

```sql
SELECT 
    problem_id,
    step_number,
    success_rate,
    total_attempts
FROM support_troubleshooting_step_effectiveness
WHERE needs_improvement = true
ORDER BY success_rate ASC;
```

## Beneficios

1. **Proactividad**: Identifica problemas antes de que ocurran
2. **Personalización**: Guías adaptadas al historial del usuario
3. **Mejora Continua**: Aprendizaje automático de efectividad
4. **Eficiencia**: Reduce tiempo de resolución
5. **Satisfacción**: Mejor experiencia del usuario

---

**Versión**: 1.0.0  
**Fecha**: 2025-01-27  
**Estado**: ✅ Completo



