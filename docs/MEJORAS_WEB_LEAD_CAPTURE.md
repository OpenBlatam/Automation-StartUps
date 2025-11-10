# 🚀 Mejoras para el Sistema de Captura de Leads Web

> **Versión**: 1.0 | **Fecha**: 2024

Mejoras avanzadas implementadas para el DAG `web_lead_capture`.

---

## ✨ Mejoras Implementadas

### 1. Scoring con IA

**Antes:**
- Scoring básico con reglas fijas
- Factores limitados

**Ahora:**
- ✅ Scoring con IA (OpenAI, DeepSeek)
- ✅ Análisis contextual del lead
- ✅ Razonamiento detallado
- ✅ Recomendaciones automáticas
- ✅ Fallback a scoring básico

**Ejemplo:**
```python
from web_lead_capture_improvements import calculate_lead_score_ai

score_result = calculate_lead_score_ai(lead_data)
# {
#     "score": 85,
#     "priority": "high",
#     "ai_reasoning": "Lead con empresa reconocida y mensaje detallado...",
#     "confidence": 0.9,
#     "recommendations": ["Contactar inmediatamente", "Enviar propuesta personalizada"]
# }
```

---

### 2. Enriquecimiento de Datos

**Características:**
- ✅ Datos de empresa desde Clearbit
- ✅ Ubicación desde IP
- ✅ Información adicional automática

**APIs Soportadas:**
- Clearbit (datos de empresa)
- ip-api.com (geolocalización)
- Extensible a más APIs

**Configuración:**
```bash
airflow variables set CLEARBIT_API_KEY "cb-..."
```

---

### 3. Detección de Spam Mejorada

**Indicadores Detectados:**
- ✅ Emails genéricos
- ✅ Palabras spam comunes
- ✅ Velocidad de envío sospechosa
- ✅ Falta de datos de contacto
- ✅ Patrones de teléfono genéricos

**Resultado:**
```python
{
    "is_spam": True,
    "spam_score": 75,
    "indicators": ["email_generic", "spam_words", "high_submission_rate"],
    "confidence": 0.75
}
```

---

### 4. Analytics y Métricas

**Datos Capturados:**
- Score y prioridad
- Método de scoring (AI vs básico)
- Spam score
- Datos de enriquecimiento
- Timestamp y fuente

**Vista SQL:**
```sql
SELECT * FROM lead_analytics_summary
WHERE is_spam = false
ORDER BY score DESC
LIMIT 10;
```

---

### 5. Sistema de Caché

**Características:**
- ✅ Evita procesamiento duplicado
- ✅ Verificación rápida de leads existentes
- ✅ TTL de 24 horas
- ✅ Limpieza automática

**Uso:**
```python
# Verificar duplicado
duplicate = check_duplicate_lead(lead_data)
if duplicate:
    logger.info("Lead ya procesado")
    return duplicate

# Guardar en caché
save_to_cache(lead_data)
```

---

### 6. Integración con Sistema de Descripciones de Puesto

**Características:**
- ✅ Detecta candidatos potenciales
- ✅ Identifica interés en trabajo
- ✅ Puede triggerear DAG de descripciones
- ✅ Marca leads como candidatos

**Detección:**
- Palabras clave: "trabajo", "empleo", "carrera", "oportunidad", "cv", "resume"
- Si se detecta, marca `is_candidate: true`

---

## 🔧 Integración con DAG Existente

### Opción 1: Agregar como Tasks Adicionales

```python
# En web_lead_capture.py, agregar después de validate_lead_data:

@task(task_id="enrich_lead_data")
def enrich_lead(lead_data: Dict[str, Any]) -> Dict[str, Any]:
    from web_lead_capture_improvements import enrich_lead_data
    return enrich_lead_data(lead_data)

@task(task_id="detect_spam")
def detect_spam_task(lead_data: Dict[str, Any]) -> Dict[str, Any]:
    from web_lead_capture_improvements import detect_spam
    spam_result = detect_spam(lead_data)
    lead_data.update(spam_result)
    return lead_data

@task(task_id="calculate_lead_score_ai")
def score_with_ai(lead_data: Dict[str, Any]) -> Dict[str, Any]:
    from web_lead_capture_improvements import calculate_lead_score_ai
    score_result = calculate_lead_score_ai(lead_data)
    lead_data.update(score_result)
    return lead_data

# Actualizar pipeline:
validated_lead = validate_lead_data()
enriched_lead = enrich_lead(validated_lead)
spam_checked = detect_spam_task(enriched_lead)
scored_lead = score_with_ai(spam_checked)  # Reemplazar calculate_lead_score
saved_lead = save_lead_to_db(scored_lead)
# ... resto del pipeline
```

### Opción 2: Reemplazar Funciones Existentes

```python
# Reemplazar calculate_lead_score con versión mejorada
from web_lead_capture_improvements import calculate_lead_score_ai as calculate_lead_score
```

---

## 📊 Esquema de Base de Datos

Ejecutar:
```bash
psql -d tu_base_de_datos -f data/db/schema/lead_analytics.sql
```

**Nuevas Tablas:**
- `lead_analytics` - Analytics de leads
- `lead_cache` - Caché para evitar duplicados

**Vistas:**
- `lead_analytics_summary` - Resumen de analytics

---

## 🎯 Casos de Uso

### Caso 1: Lead de Alta Calidad

```python
lead_data = {
    "email": "juan.perez@empresa.com",
    "first_name": "Juan",
    "last_name": "Pérez",
    "company": "Tech Corp",
    "phone": "+1234567890",
    "message": "Interesado en su solución para automatización"
}

# Scoring con IA
score_result = calculate_lead_score_ai(lead_data)
# Score: 90, Priority: high

# Enriquecimiento
enriched = enrich_lead_data(lead_data)
# Agrega datos de empresa desde Clearbit

# Spam check
spam_result = detect_spam(lead_data)
# is_spam: false, spam_score: 5
```

### Caso 2: Detección de Spam

```python
lead_data = {
    "email": "abc@xyz.com",
    "message": "Click here for amazing prize! Limited time offer!"
}

spam_result = detect_spam(lead_data)
# is_spam: true, spam_score: 85
# indicators: ["email_generic", "spam_words"]
```

---

## 📈 Métricas y Analytics

### Consultas Útiles

**Leads de alta calidad:**
```sql
SELECT * FROM lead_analytics_summary
WHERE is_spam = false AND score >= 70
ORDER BY score DESC;
```

**Spam rate:**
```sql
SELECT 
    COUNT(*) as total,
    COUNT(CASE WHEN is_spam THEN 1 END) as spam_count,
    ROUND(COUNT(CASE WHEN is_spam THEN 1 END)::FLOAT / COUNT(*) * 100, 2) as spam_rate
FROM lead_analytics_summary
WHERE created_at > NOW() - INTERVAL '7 days';
```

**Performance de scoring con IA:**
```sql
SELECT 
    scoring_method,
    AVG(score) as avg_score,
    COUNT(*) as count
FROM lead_analytics_summary
WHERE scoring_method IS NOT NULL
GROUP BY scoring_method;
```

---

## 🔧 Configuración

### Variables de Airflow

```bash
# IA para scoring
airflow variables set OPENAI_API_KEY "sk-..."
airflow variables set DEFAULT_LLM_PROVIDER "openai"

# Enriquecimiento
airflow variables set CLEARBIT_API_KEY "cb-..."

# Opcional: DeepSeek
airflow variables set DEEPSEEK_API_KEY "..."
```

---

## 🚀 Próximas Mejoras Sugeridas

1. **ML Model para Spam**
   - Modelo entrenado específicamente
   - Mejor precisión que reglas

2. **Más APIs de Enriquecimiento**
   - FullContact
   - ZoomInfo
   - LinkedIn Sales Navigator

3. **Predictive Scoring**
   - Predicción de conversión
   - Lifetime value estimado
   - Churn risk

4. **A/B Testing de Scoring**
   - Comparar métodos
   - Optimizar thresholds

5. **Dashboard de Analytics**
   - Visualización de métricas
   - Tendencias y patrones

---

**Última actualización**: 2024  
**Versión**: 1.0  
**Mantenido por**: Sales Team & Platform Team






