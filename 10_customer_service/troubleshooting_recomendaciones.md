---
title: "Troubleshooting Recomendaciones"
category: "troubleshooting_recomendaciones.md"
tags: []
created: "2025-10-29"
path: "troubleshooting_recomendaciones.md"
---

# 🔧 Troubleshooting Completo - Sistemas de Recomendaciones
## Soluciones a Problemas Comunes

## 🚨 PROBLEMAS CRÍTICOS

### Problema 1: Recomendaciones No Aparecen en el Sitio

#### Síntomas
- No se muestran recomendaciones
- Error en consola del navegador
- Widgets vacíos

#### Diagnóstico
1. **Verificar API está funcionando**
   ```bash
   curl http://your-api/recommendations/123
   ```
   - ¿Responde? → Problema frontend
   - ¿No responde? → Problema backend

2. **Verificar logs del servidor**
   - Errores en API
   - Timeouts
   - Errores de base de datos

3. **Verificar integración frontend**
   - JavaScript ejecutándose
   - Llamadas a API correctas
   - Manejo de errores funcionando

#### Soluciones

**Si API no responde:**
```python
# Verificar que modelo está cargado
if model is None:
    load_model()

# Verificar que datos están disponibles
if not data_available:
    use_fallback_recommendations()
```

**Si Frontend no muestra:**
```javascript
// Verificar que API responde
fetch('/api/recommendations/123')
  .then(response => {
    if (!response.ok) {
      console.error('API error:', response.status);
      showPopularProducts(); // Fallback
    }
    return response.json();
  })
  .catch(error => {
    console.error('Network error:', error);
    showPopularProducts(); // Fallback
  });
```

**Fallbacks recomendados:**
- Productos populares
- Productos trending
- Categorías más visitadas

---

### Problema 2: Recomendaciones Son Irrelevantes

#### Síntomas
- CTR bajo (<5%)
- Usuarios no clickean
- Conversión baja desde recomendaciones
- Feedback negativo

#### Diagnóstico
1. **Validar datos de entrada**
   - ¿Datos históricos suficientes?
   - ¿Datos actualizados?
   - ¿Calidad de datos OK?

2. **Validar modelo**
   - ¿Modelo entrenado correctamente?
   - ¿Métricas de evaluación buenas?
   - ¿Última vez re-entrenado?

3. **Validar algoritmo**
   - ¿Algoritmo adecuado para tus datos?
   - ¿Hyperparámetros optimizados?
   - ¿Features relevantes?

#### Soluciones

**Mejorar datos:**
```python
# Validar suficiencia de datos
if interactions_count < 1000:
    print("Advertencia: Datos insuficientes")
    use_content_based_instead()

# Validar actualidad
if latest_interaction_age_days > 90:
    print("Advertencia: Datos muy viejos")
    retrain_with_recent_data_only()
```

**Mejorar modelo:**
```python
# Re-entrenar con más datos
model.fit(updated_data)

# Probar diferentes algoritmos
from surprise import SVD, NMF, KNNBaseline

algorithms = [SVD(), NMF(), KNNBaseline()]
best_rmse = float('inf')
best_model = None

for algo in algorithms:
    rmse = evaluate_model(algo, data)
    if rmse < best_rmse:
        best_rmse = rmse
        best_model = algo

# Usar mejor modelo
```

**Validar relevancia manualmente:**
- Revisar recomendaciones para usuarios conocidos
- Comparar con productos que realmente compraron después
- Ajustar según feedback

---

### Problema 3: Performance Lenta (>500ms response time)

#### Síntomas
- Tiempo de respuesta API alto
- Página carga lenta
- Usuarios reportan lag
- Timeouts

#### Diagnóstico
1. **Identificar cuello de botella**
   - API lenta?
   - Database queries lentas?
   - Modelo pesado?
   - Sin caching?

2. **Profiling**
   ```python
   import time
   
   start = time.time()
   recommendations = generate_recommendations(user_id)
   elapsed = time.time() - start
   print(f"Generation time: {elapsed:.3f}s")
   ```

#### Soluciones

**Optimizar queries:**
```python
# Indexar columnas usadas frecuentemente
# En SQL:
CREATE INDEX idx_user_transactions ON transactions(user_id, item_id, date);

# Limitar resultados temprano
SELECT * FROM transactions 
WHERE user_id = ? 
ORDER BY date DESC 
LIMIT 100;  # No necesitas todo el historial
```

**Caching:**
```python
from functools import lru_cache
import redis

redis_client = redis.Redis()

def get_recommendations_cached(user_id):
    cache_key = f"recs:{user_id}"
    
    # Verificar cache
    cached = redis_client.get(cache_key)
    if cached:
        return json.loads(cached)
    
    # Generar recomendaciones
    recommendations = generate_recommendations(user_id)
    
    # Cachear (expira en 1 hora)
    redis_client.setex(
        cache_key, 
        3600, 
        json.dumps(recommendations)
    )
    
    return recommendations
```

**Optimizar modelo:**
```python
# Usar modelo más ligero si posible
# Surprise es más rápido que TensorFlow para casos simples

# Pre-calcular recomendaciones populares
popular_items = precompute_popular_items()  # Una vez al día

# Para usuarios nuevos, usar pre-calculado
if is_new_user(user_id):
    return popular_items
```

**Scaling:**
- Load balancing
- Horizontal scaling (múltiples instancias)
- CDN para contenido estático

---

### Problema 4: Cold Start (Usuarios/Productos Nuevos)

#### Síntomas
- Usuarios nuevos ven recomendaciones genéricas
- Productos nuevos nunca recomendados
- CTR bajo en nuevos usuarios

#### Soluciones

**Para usuarios nuevos:**
```python
def recommend_for_new_user(user_id, demographic_data=None):
    """
    Estrategia para usuarios sin historial
    """
    recommendations = []
    
    # 1. Basado en demografía si disponible
    if demographic_data:
        age = demographic_data.get('age')
        location = demographic_data.get('location')
        
        # Recomendar popular en su demografía
        recommendations.extend(
            get_popular_by_demographic(age, location, n=5)
        )
    
    # 2. Productos trending/populares
    recommendations.extend(get_trending_products(n=5))
    
    # 3. Categorías más visitadas del sitio
    recommendations.extend(
        get_popular_by_category(most_viewed_categories(), n=5)
    )
    
    # Combinar y diversificar
    return diversify_recommendations(recommendations, n=10)
```

**Para productos nuevos:**
```python
def recommend_new_product(product_id, product_features):
    """
    Estrategia para productos sin historial
    """
    # Content-based: productos similares por características
    similar_products = find_similar_by_features(product_features)
    
    # Popular en misma categoría
    category_popular = get_popular_in_category(product_features['category'])
    
    # Combinar estrategias
    return combine_recommendations(similar_products, category_popular)
```

**Sistema híbrido para cold start:**
- Combinar demografía + trending + categorías
- Aumentar exposición de productos nuevos estratégicamente
- Solicitar preferencias explícitas (onboarding)

---

## ⚠️ PROBLEMAS COMUNES

### Problema 5: Filter Bubble (Sobre-Filtrado)

#### Síntomas
- Solo productos muy similares
- Usuario ve siempre lo mismo
- Menos exploración
- Engagement cae con el tiempo

#### Soluciones

**Agregar diversidad:**
```python
def diversify_recommendations(recommendations, diversity_ratio=0.2):
    """
    Agrega diversidad a recomendaciones
    diversity_ratio: % de recomendaciones que deben ser exploratorias
    """
    n_exploratory = int(len(recommendations) * diversity_ratio)
    
    # Separar similares y exploratorias
    similar = recommendations[:len(recommendations) - n_exploratory]
    exploratory = get_exploratory_products(n_exploratory)
    
    # Combinar manteniendo orden (similar primero, luego exploratorio)
    return similar + exploratory
```

**Rotar recomendaciones:**
```python
# No mostrar siempre lo mismo
def rotate_recommendations(user_id, base_recommendations):
    """
    Rota recomendaciones para evitar repetición
    """
    # Obtener último mostrado
    last_shown = get_last_recommendations(user_id, n=5)
    
    # Filtrar ya mostrados recientemente
    candidates = [
        r for r in base_recommendations 
        if r['item_id'] not in last_shown
    ]
    
    return candidates[:10]
```

---

### Problema 6: Datos Desactualizados

#### Síntomas
- Recomendaciones basadas en comportamiento viejo
- Preferencias cambiaron pero recomendaciones no
- CTR/conversión cae progresivamente

#### Soluciones

**Decay temporal:**
```python
def apply_temporal_decay(interactions, decay_factor=0.9):
    """
    Da más peso a interacciones recientes
    decay_factor: cuánto decae por mes (0.9 = 10% menos peso/mes)
    """
    current_date = datetime.now()
    
    for interaction in interactions:
        months_ago = (current_date - interaction['date']).days / 30
        decay = decay_factor ** months_ago
        
        # Aplicar decay al rating/score
        interaction['weighted_score'] = interaction['score'] * decay
    
    return interactions
```

**Re-entrenamiento frecuente:**
```python
# Re-entrenar cada semana con datos últimos 3 meses
def retrain_with_recent_data():
    # Solo datos últimos 90 días
    recent_data = get_data_last_n_days(90)
    
    # Entrenar modelo
    model.fit(recent_data)
    
    # Evaluar
    metrics = evaluate_model(model, recent_data)
    
    # Si mejoró, actualizar modelo en producción
    if metrics['rmse'] < current_production_rmse:
        deploy_model(model)
```

---

### Problema 7: Modelo Tarda Mucho en Entrenar

#### Síntomas
- Entrenamiento toma horas/días
- No puedes re-entrenar frecuentemente
- Modelo se vuelve obsoleto

#### Soluciones

**Optimizar entrenamiento:**
```python
# Usar solo muestra representativa si datos muy grandes
if len(data) > 100000:
    # Sample representativo
    data = data.sample(n=100000, random_state=42)

# Usar algoritmos más rápidos
# Surprise SVD es más rápido que TensorFlow para muchos casos

# Paralelizar si posible
from joblib import Parallel, delayed

def train_models_parallel():
    results = Parallel(n_jobs=4)(
        delayed(train_model)(algo, data) 
        for algo in algorithms
    )
    return results
```

**Incremental training:**
```python
# Entrenar solo con datos nuevos, no desde cero
def incremental_train(model, new_data):
    """
    Ajusta modelo con datos nuevos sin re-entrenar completo
    """
    # Solo nuevos datos desde último entrenamiento
    new_interactions = get_data_since_last_training()
    
    # Ajuste parcial
    model.fit_partial(new_interactions)
    
    return model
```

---

## 🔍 DIAGNÓSTICO SISTEMÁTICO

### Checklist de Diagnóstico

**Si recomendaciones no aparecen:**
- [ ] API está funcionando? (curl/Postman)
- [ ] Frontend haciendo llamadas correctas?
- [ ] Errores en consola del navegador?
- [ ] Errores en logs del servidor?
- [ ] Modelo cargado correctamente?
- [ ] Datos disponibles?

**Si recomendaciones son malas:**
- [ ] Datos suficientes? (>1000 interacciones)
- [ ] Datos actualizados? (<6 meses)
- [ ] Modelo re-entrenado recientemente?
- [ ] Algoritmo adecuado para datos?
- [ ] Features relevantes creadas?
- [ ] Validación manual: ¿son realmente malas?

**Si performance es lenta:**
- [ ] Cuello de botella identificado? (API/DB/Modelo)
- [ ] Caching implementado?
- [ ] Indexes en database?
- [ ] Queries optimizadas?
- [ ] Modelo muy pesado? (considerar más ligero)
- [ ] Infraestructura adecuada? (RAM/CPU)

**Si cold start es problema:**
- [ ] Estrategia para usuarios nuevos implementada?
- [ ] Estrategia para productos nuevos implementada?
- [ ] Demografía disponible?
- [ ] Trending/popular funcionando?
- [ ] Onboarding con preferencias explícitas?

---

## 🛠️ HERRAMIENTAS DE DEBUGGING

### Logging Recomendado

```python
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def generate_recommendations(user_id):
    logger.info(f"Generating recommendations for user {user_id}")
    
    try:
        # Check if user exists
        if not user_exists(user_id):
            logger.warning(f"User {user_id} not found, using cold start")
            return get_cold_start_recommendations()
        
        # Get recommendations
        start_time = time.time()
        recommendations = model.recommend(user_id, n=10)
        elapsed = time.time() - start_time
        
        logger.info(f"Generated {len(recommendations)} recommendations in {elapsed:.3f}s")
        
        # Log if recommendations seem odd
        if len(recommendations) == 0:
            logger.warning(f"No recommendations for user {user_id}")
        if all(r['score'] < 2.0 for r in recommendations):
            logger.warning(f"Low scores for user {user_id}")
        
        return recommendations
    
    except Exception as e:
        logger.error(f"Error generating recommendations for {user_id}: {e}")
        return get_fallback_recommendations()
```

---

### Monitoring y Alertas

```python
# Alertas automáticas
def check_recommendations_health():
    """
    Verifica salud del sistema de recomendaciones
    """
    issues = []
    
    # Check CTR
    current_ctr = get_current_ctr()
    avg_ctr = get_average_ctr()
    if current_ctr < avg_ctr * 0.8:  # 20% debajo del promedio
        issues.append(f"CTR bajo: {current_ctr:.2f}% vs {avg_ctr:.2f}%")
    
    # Check conversion
    current_conv = get_current_conversion()
    avg_conv = get_average_conversion()
    if current_conv < avg_conv * 0.85:  # 15% debajo del promedio
        issues.append(f"Conversión baja: {current_conv:.2f}% vs {avg_conv:.2f}%")
    
    # Check response time
    avg_response = get_average_response_time()
    if avg_response > 500:  # >500ms
        issues.append(f"Response time alto: {avg_response:.0f}ms")
    
    # Check errors
    error_rate = get_error_rate()
    if error_rate > 0.01:  # >1%
        issues.append(f"Error rate alto: {error_rate:.2%}")
    
    # Send alerts if issues
    if issues:
        send_alert("Recomendations System Issues", issues)
    
    return issues
```

---

## 📋 TEMPLATE DE REPORTE DE PROBLEMA

### Cuando Reportar Bug/Issue

**Información necesaria:**
```
PROBLEMA: [Descripción clara]
USER_ID (si aplica): [id]
FECHA/HORA: [timestamp]
SÍNTOMAS:
- [Síntoma 1]
- [Síntoma 2]

CONTEXTO:
- [Qué estaba haciendo el usuario]
- [Qué se esperaba vs qué pasó]

LOG/ERRORES:
[Pegar logs relevantes]

REPRODUCIBILIDAD:
- [Siempre / A veces / Solo con X]
- [Pasos para reproducir]

IMPACTO:
- [Usuarios afectados]
- [Métricas afectadas]
```

---

**Última actualización:** [Fecha]
**Versión:** 1.0 - Troubleshooting Completo




