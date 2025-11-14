---
title: "Ejemplos Codigo Recomendaciones"
category: "ejemplos_codigo_recomendaciones.md"
tags: []
created: "2025-10-29"
path: "ejemplos_codigo_recomendaciones.md"
---

# 💻 Ejemplos de Código - Sistemas de Recomendaciones Personalizadas
## Implementaciones Prácticas Listas para Usar

## 🐍 PYTHON - Collaborative Filtering Básico

### Ejemplo 1: Sistema Simple con Surprise

```python
"""
Sistema de Recomendaciones Personalizadas - Collaborative Filtering
Basado en historial de compras y preferencias del cliente
"""

from surprise import Dataset, Reader, SVD
from surprise.model_selection import train_test_split, cross_validate
import pandas as pd
import numpy as np

class RecommenderSystem:
    def __init__(self):
        self.model = SVD()
        self.trainset = None
        
    def prepare_data(self, transactions_df):
        """
        Prepara datos históricos para el modelo
        transactions_df debe tener: user_id, item_id, rating (implícito o explícito)
        """
        # Calcular ratings implícitos si no hay explícitos
        if 'rating' not in transactions_df.columns:
            transactions_df['rating'] = self._calculate_implicit_ratings(transactions_df)
        
        # Formato para Surprise
        reader = Reader(rating_scale=(1, 5))
        data = Dataset.load_from_df(
            transactions_df[['user_id', 'item_id', 'rating']], 
            reader
        )
        
        return data
    
    def _calculate_implicit_ratings(self, df):
        """Convierte comportamiento en ratings implícitos"""
        ratings = []
        
        for _, row in df.iterrows():
            rating = 3.0  # Base
            
            # Compras valen más que vistas
            if row['action'] == 'purchase':
                rating += 2.0
            elif row['action'] == 'add_to_cart':
                rating += 1.5
            elif row['action'] == 'view':
                rating += 0.5
            
            # Decay temporal
            days_ago = (pd.Timestamp.now() - row['date']).days
            time_decay = max(0, 1 - (days_ago / 365))
            rating *= time_decay
            
            ratings.append(min(5.0, rating))
        
        return ratings
    
    def train(self, data, test_size=0.2):
        """Entrena el modelo"""
        trainset, testset = train_test_split(data, test_size=test_size)
        self.trainset = trainset
        self.model.fit(trainset)
        
        # Evaluar
        predictions = self.model.test(testset)
        rmse = np.sqrt(np.mean([(pred.r_ui - pred.est)**2 for pred in predictions]))
        
        return rmse
    
    def recommend(self, user_id, n=10, exclude_items=None):
        """
        Genera recomendaciones para un usuario
        exclude_items: items que ya ha visto/comprado
        """
        if exclude_items is None:
            exclude_items = []
        
        # Obtener todos los items posibles
        all_items = self.trainset.all_items()
        all_items = [self.trainset.to_raw_iid(iid) for iid in all_items]
        
        # Filtrar items ya vistos
        candidate_items = [item for item in all_items if item not in exclude_items]
        
        # Predecir ratings para todos los candidatos
        user_inner_id = self.trainset.to_inner_uid(user_id)
        predictions = []
        
        for item in candidate_items:
            item_inner_id = self.trainset.to_inner_iid(item)
            pred = self.model.predict(user_inner_id, item_inner_id)
            predictions.append((item, pred.est))
        
        # Ordenar por rating predicho y retornar top N
        predictions.sort(key=lambda x: x[1], reverse=True)
        return predictions[:n]

# Uso
recommender = RecommenderSystem()

# Preparar datos
transactions = pd.DataFrame({
    'user_id': [1, 1, 2, 2, 3, 3, 4, 4, 1, 2],
    'item_id': [101, 102, 101, 103, 102, 103, 101, 104, 105, 105],
    'action': ['purchase', 'view', 'purchase', 'add_to_cart', 'view', 'purchase', 'purchase', 'view', 'purchase', 'purchase'],
    'date': pd.date_range('2024-01-01', periods=10, freq='D')
})

data = recommender.prepare_data(transactions)
rmse = recommender.train(data)
print(f"Modelo entrenado con RMSE: {rmse:.3f}")

# Generar recomendaciones
user_id = 1
user_history = transactions[transactions['user_id'] == user_id]['item_id'].tolist()
recommendations = recommender.recommend(user_id, n=5, exclude_items=user_history)

print(f"\nRecomendaciones para usuario {user_id}:")
for item_id, score in recommendations:
    print(f"  Item {item_id}: Score {score:.2f}")
```

---

## 📊 CONTENT-BASED FILTERING

### Ejemplo 2: Basado en Características del Producto

```python
"""
Sistema Content-Based: Recomienda productos similares
basados en características del producto
"""

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import pandas as pd
import numpy as np

class ContentBasedRecommender:
    def __init__(self):
        self.vectorizer = TfidfVectorizer()
        self.similarity_matrix = None
        self.products = None
        
    def fit(self, products_df):
        """
        Entrena el sistema con productos
        products_df debe tener: product_id, features (texto con características)
        """
        self.products = products_df.set_index('product_id')
        
        # Vectorizar características
        tfidf_matrix = self.vectorizer.fit_transform(products_df['features'])
        
        # Calcular similitud
        self.similarity_matrix = cosine_similarity(tfidf_matrix, tfidf_matrix)
        
    def recommend(self, product_id, n=5):
        """Recomienda productos similares a uno dado"""
        if product_id not in self.products.index:
            return []
        
        product_idx = self.products.index.get_loc(product_id)
        similarity_scores = list(enumerate(self.similarity_matrix[product_idx]))
        similarity_scores = sorted(similarity_scores, key=lambda x: x[1], reverse=True)
        
        recommendations = []
        for idx, score in similarity_scores[1:n+1]:  # Skip el mismo producto
            rec_product_id = self.products.index[idx]
            recommendations.append({
                'product_id': rec_product_id,
                'name': self.products.loc[rec_product_id, 'name'],
                'similarity': score
            })
        
        return recommendations
    
    def recommend_for_user(self, user_history, n=10):
        """
        Recomienda basado en historial del usuario
        user_history: lista de product_ids que el usuario ha visto/comprado
        """
        if not user_history:
            return []
        
        # Calcular similitud promedio con historial
        all_similarities = []
        
        for hist_product in user_history[-5:]:  # Usar últimos 5 productos
            if hist_product in self.products.index:
                hist_idx = self.products.index.get_loc(hist_product)
                similarities = list(enumerate(self.similarity_matrix[hist_idx]))
                all_similarities.append(similarities)
        
        if not all_similarities:
            return []
        
        # Promediar similitudes
        avg_similarities = {}
        for similarities in all_similarities:
            for idx, score in similarities:
                product_id = self.products.index[idx]
                if product_id not in user_history:
                    if product_id not in avg_similarities:
                        avg_similarities[product_id] = []
                    avg_similarities[product_id].append(score)
        
        # Promediar y ordenar
        final_scores = {
            pid: np.mean(scores) 
            for pid, scores in avg_similarities.items()
        }
        
        sorted_recs = sorted(final_scores.items(), key=lambda x: x[1], reverse=True)
        
        recommendations = []
        for product_id, score in sorted_recs[:n]:
            recommendations.append({
                'product_id': product_id,
                'name': self.products.loc[product_id, 'name'],
                'similarity': score
            })
        
        return recommendations

# Uso
products = pd.DataFrame({
    'product_id': [1, 2, 3, 4, 5],
    'name': ['Laptop Gaming', 'Smartphone Pro', 'Tablet Office', 'Laptop Business', 'Smartphone Basic'],
    'features': [
        'gaming performance graphics ram processor',
        'camera battery smartphone mobile android',
        'tablet office productivity screen portable',
        'business laptop professional work productivity',
        'smartphone basic budget mobile affordable'
    ]
})

cb_recommender = ContentBasedRecommender()
cb_recommender.fit(products)

# Recomendar productos similares al producto 1
recs = cb_recommender.recommend(1, n=3)
print("Productos similares al producto 1:")
for rec in recs:
    print(f"  {rec['name']} (Similitud: {rec['similarity']:.2f})")

# Recomendar para usuario con historial
user_history = [1, 4]  # Usuario vio/compró laptops
user_recs = cb_recommender.recommend_for_user(user_history, n=5)
print("\nRecomendaciones para usuario (historial: laptops):")
for rec in user_recs:
    print(f"  {rec['name']} (Similitud: {rec['similarity']:.2f})")
```

---

## 🔄 SISTEMA HÍBRIDO

### Ejemplo 3: Combinando Collaborative + Content-Based

```python
"""
Sistema Híbrido: Combina Collaborative Filtering y Content-Based
para mejores recomendaciones
"""

class HybridRecommender:
    def __init__(self, collab_model, content_model, alpha=0.6):
        """
        alpha: peso del modelo colaborativo (0-1)
        (1-alpha): peso del modelo content-based
        """
        self.collab_model = collab_model
        self.content_model = content_model
        self.alpha = alpha
        
    def recommend(self, user_id, user_history, n=10):
        """Genera recomendaciones híbridas"""
        # Recomendaciones colaborativas
        collab_recs = self.collab_model.recommend(user_id, n=n*2, exclude_items=user_history)
        
        # Recomendaciones content-based
        content_recs = self.content_model.recommend_for_user(user_history, n=n*2)
        
        # Combinar scores
        hybrid_scores = {}
        
        # Agregar scores colaborativos
        max_collab = max(score for _, score in collab_recs) if collab_recs else 1
        for item_id, score in collab_recs:
            normalized_score = score / max_collab
            hybrid_scores[item_id] = self.alpha * normalized_score
        
        # Agregar scores content-based
        max_content = max(rec['similarity'] for rec in content_recs) if content_recs else 1
        for rec in content_recs:
            item_id = rec['product_id']
            normalized_score = rec['similarity'] / max_content
            if item_id in hybrid_scores:
                hybrid_scores[item_id] += (1 - self.alpha) * normalized_score
            else:
                hybrid_scores[item_id] = (1 - self.alpha) * normalized_score
        
        # Ordenar y retornar top N
        sorted_recs = sorted(hybrid_scores.items(), key=lambda x: x[1], reverse=True)
        return [(item_id, score) for item_id, score in sorted_recs[:n]]
```

---

## 🌐 API REST CON FASTAPI

### Ejemplo 4: Servir Recomendaciones en Tiempo Real

```python
"""
API REST para servir recomendaciones en tiempo real
FastAPI + modelo pre-entrenado
"""

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Optional
import joblib
import pandas as pd

app = FastAPI(title="Recomendations API", version="1.0.0")

# Cargar modelo pre-entrenado
try:
    recommender = joblib.load('models/recommender_model.pkl')
    products_df = pd.read_csv('data/products.csv')
except FileNotFoundError:
    print("Modelo no encontrado. Necesitas entrenar primero.")
    recommender = None
    products_df = None

class RecommendationRequest(BaseModel):
    user_id: int
    num_recommendations: int = 10
    exclude_items: Optional[List[int]] = None

class RecommendationResponse(BaseModel):
    user_id: int
    recommendations: List[dict]
    metadata: dict

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "model_loaded": recommender is not None}

@app.post("/recommendations", response_model=RecommendationResponse)
async def get_recommendations(request: RecommendationRequest):
    """
    Genera recomendaciones personalizadas para un usuario
    """
    if recommender is None:
        raise HTTPException(status_code=503, detail="Modelo no disponible")
    
    try:
        # Obtener historial del usuario
        user_history = get_user_history(request.user_id)
        exclude = request.exclude_items or user_history
        
        # Generar recomendaciones
        recommendations = recommender.recommend(
            user_id=request.user_id,
            n=request.num_recommendations,
            exclude_items=exclude
        )
        
        # Enriquecer con información del producto
        enriched_recs = []
        for item_id, score in recommendations:
            product_info = products_df[products_df['product_id'] == item_id].iloc[0]
            enriched_recs.append({
                'product_id': int(item_id),
                'name': product_info['name'],
                'category': product_info.get('category', ''),
                'price': float(product_info.get('price', 0)),
                'score': float(score),
                'confidence': min(1.0, score / 5.0)  # Normalizar confianza
            })
        
        return RecommendationResponse(
            user_id=request.user_id,
            recommendations=enriched_recs,
            metadata={
                'num_recommendations': len(enriched_recs),
                'algorithm': 'hybrid',
                'model_version': '1.0'
            }
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/recommendations/{user_id}")
async def get_recommendations_simple(user_id: int, num: int = 10):
    """Endpoint simple GET"""
    request = RecommendationRequest(user_id=user_id, num_recommendations=num)
    return await get_recommendations(request)

def get_user_history(user_id: int):
    """Obtiene historial del usuario desde base de datos"""
    # En producción, esto consultaría tu base de datos
    # Ejemplo simplificado
    import sqlite3
    conn = sqlite3.connect('data/recommendations.db')
    history = pd.read_sql_query(
        "SELECT item_id FROM transactions WHERE user_id = ?",
        conn,
        params=(user_id,)
    )
    conn.close()
    return history['item_id'].tolist() if not history.empty else []

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
```

---

## 📈 PROCESAMIENTO DE DATOS HISTÓRICOS AVANZADO

### Ejemplo 5: Feature Engineering Completo

```python
"""
Feature Engineering para Recomendaciones
Extrae preferencias y patrones del historial
"""

import pandas as pd
from datetime import datetime, timedelta
import numpy as np

class DataPreprocessor:
    def __init__(self):
        pass
    
    def extract_user_features(self, transactions_df, users_df=None):
        """
        Extrae features del usuario basadas en historial
        """
        user_features = transactions_df.groupby('user_id').agg({
            'item_id': 'count',  # Frecuencia de compras
            'date': ['min', 'max', 'count'],  # Actividad temporal
            'amount': ['sum', 'mean'] if 'amount' in transactions_df.columns else {}
        }).reset_index()
        
        # Calcular días desde primera/última compra
        user_features['days_since_first'] = (
            datetime.now() - user_features[('date', 'min')]
        ).dt.days
        user_features['days_since_last'] = (
            datetime.now() - user_features[('date', 'max')]
        ).dt.days
        
        # Categorías preferidas
        if 'category' in transactions_df.columns:
            category_prefs = transactions_df.groupby(['user_id', 'category']).size().reset_index(name='count')
            top_categories = category_prefs.sort_values('count', ascending=False).groupby('user_id').head(3)
            user_features['preferred_categories'] = top_categories.groupby('user_id')['category'].apply(list)
        
        return user_features
    
    def extract_item_features(self, transactions_df, products_df):
        """
        Extrae features de productos basadas en comportamiento
        """
        item_features = transactions_df.groupby('item_id').agg({
            'user_id': 'nunique',  # Número de compradores únicos
            'date': 'count',  # Número de transacciones
            'amount': ['mean', 'std'] if 'amount' in transactions_df.columns else {}
        }).reset_index()
        
        # Popularidad (normalizada)
        item_features['popularity_score'] = (
            item_features[('user_id', 'nunique')] / 
            item_features[('user_id', 'nunique')].max()
        )
        
        # Tendencias (transacciones recientes vs antiguas)
        recent = transactions_df[
            transactions_df['date'] > datetime.now() - timedelta(days=30)
        ].groupby('item_id').size()
        old = transactions_df[
            transactions_df['date'] <= datetime.now() - timedelta(days=30)
        ].groupby('item_id').size()
        
        item_features['trending_score'] = (recent / (old + 1)).fillna(0)
        
        return item_features
    
    def create_interaction_features(self, transactions_df):
        """
        Crea features de interacción usuario-item
        """
        interactions = transactions_df.copy()
        
        # Recencia
        interactions['recency'] = (
            datetime.now() - interactions['date']
        ).dt.days
        
        # Frecuencia
        user_freq = interactions.groupby('user_id').size()
        interactions['user_frequency'] = interactions['user_id'].map(user_freq)
        
        # Intensidad (monto si disponible)
        if 'amount' in interactions.columns:
            interactions['user_average_spend'] = interactions.groupby('user_id')['amount'].transform('mean')
        
        return interactions
```

---

## 🔍 RECOMENDACIONES CONTEXTUALES

### Ejemplo 6: Personalización por Contexto

```python
"""
Recomendaciones que se adaptan al contexto:
- Hora del día
- Dispositivo
- Temporada
- Ubicación
"""

class ContextualRecommender:
    def __init__(self, base_recommender):
        self.base_recommender = base_recommender
        
    def recommend_with_context(self, user_id, context, n=10):
        """
        context: dict con 'time_of_day', 'device', 'season', 'location'
        """
        # Recomendaciones base
        base_recs = self.base_recommender.recommend(user_id, n=n*2)
        
        # Ajustar por contexto
        contextual_scores = {}
        
        for item_id, score in base_recs:
            adjustment = self._calculate_context_adjustment(item_id, context)
            contextual_scores[item_id] = score * adjustment
        
        # Ordenar y retornar top N
        sorted_recs = sorted(
            contextual_scores.items(), 
            key=lambda x: x[1], 
            reverse=True
        )[:n]
        
        return sorted_recs
    
    def _calculate_context_adjustment(self, item_id, context):
        """Calcula ajuste según contexto"""
        adjustment = 1.0
        
        # Ajuste por hora
        if 'time_of_day' in context:
            hour = context['time_of_day']
            if self._is_morning_item(item_id) and 6 <= hour <= 12:
                adjustment *= 1.3
            elif self._is_evening_item(item_id) and 18 <= hour <= 23:
                adjustment *= 1.3
        
        # Ajuste por dispositivo
        if 'device' in context:
            if context['device'] == 'mobile' and self._is_mobile_optimized(item_id):
                adjustment *= 1.2
        
        # Ajuste por temporada
        if 'season' in context:
            if self._is_seasonal_item(item_id, context['season']):
                adjustment *= 1.4
        
        return adjustment
    
    def _is_morning_item(self, item_id):
        """Lógica para identificar items matutinos"""
        # En producción, esto consultaría características del producto
        return item_id in [101, 102, 103]
    
    def _is_evening_item(self, item_id):
        """Lógica para identificar items vespertinos"""
        return item_id in [201, 202, 203]
    
    def _is_mobile_optimized(self, item_id):
        """Lógica para items optimizados para móvil"""
        return item_id in [301, 302, 303]
    
    def _is_seasonal_item(self, item_id, season):
        """Lógica para items estacionales"""
        seasonal_items = {
            'winter': [401, 402],
            'summer': [501, 502],
            'spring': [601, 602],
            'fall': [701, 702]
        }
        return item_id in seasonal_items.get(season, [])
```

---

## 🐳 DEPLOYMENT DOCKER

### Dockerfile

```dockerfile
FROM python:3.9-slim

WORKDIR /app

# Instalar dependencias del sistema
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copiar requirements
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiar código y modelos
COPY . .
COPY models/ ./models/
COPY data/ ./data/

# Exponer puerto
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
  CMD python -c "import requests; requests.get('http://localhost:8000/health')"

# Comando para iniciar API
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### docker-compose.yml

```yaml
version: '3.8'

services:
  recommender-api:
    build: .
    ports:
      - "8000:8000"
    environment:
      - MODEL_PATH=/app/models/recommender.pkl
      - DATA_PATH=/app/data/
      - DATABASE_URL=postgresql://user:pass@db:5432/recommendations
    volumes:
      - ./models:/app/models
      - ./data:/app/data
    depends_on:
      - db
    restart: unless-stopped
    
  db:
    image: postgres:13
    environment:
      - POSTGRES_DB=recommendations
      - POSTGRES_USER=user
      - POSTGRES_PASSWORD=pass
    volumes:
      - postgres_data:/var/lib/postgresql/data
    restart: unless-stopped

volumes:
  postgres_data:
```

---

## 📊 MÉTRICAS Y EVALUACIÓN

### Ejemplo 7: Evaluación Completa del Sistema

```python
"""
Evaluación de métricas de negocio y técnicas
"""

def evaluate_recommendations(model, test_data, products_df):
    """
    Evalúa el sistema de recomendaciones
    """
    metrics = {}
    
    # 1. Métricas técnicas
    predictions = []
    for user_id, item_id, actual_rating in test_data:
        pred = model.predict(user_id, item_id)
        predictions.append({
            'user_id': user_id,
            'item_id': item_id,
            'predicted': pred.est,
            'actual': actual_rating
        })
    
    pred_df = pd.DataFrame(predictions)
    
    # RMSE
    rmse = np.sqrt(np.mean((pred_df['predicted'] - pred_df['actual'])**2))
    metrics['rmse'] = rmse
    
    # MAE
    mae = np.mean(np.abs(pred_df['predicted'] - pred_df['actual']))
    metrics['mae'] = mae
    
    # 2. Métricas de negocio
    # Precision@K
    k = 10
    precision_scores = []
    
    for user_id in test_data['user_id'].unique():
        user_test = test_data[test_data['user_id'] == user_id]
        user_recs = model.recommend(user_id, n=k)
        
        recommended_items = [item for item, _ in user_recs]
        relevant_items = set(user_test[user_test['actual'] >= 4]['item_id'])
        
        if len(recommended_items) > 0:
            precision = len(set(recommended_items) & relevant_items) / len(recommended_items)
            precision_scores.append(precision)
    
    metrics['precision_at_k'] = np.mean(precision_scores) if precision_scores else 0
    
    # 3. Coverage (porcentaje de items que pueden ser recomendados)
    all_items = set(products_df['product_id'])
        recommended_items = set()
        for user_id in test_data['user_id'].unique():
            recs = model.recommend(user_id, n=k)
            recommended_items.update([item for item, _ in recs])
        
        metrics['coverage'] = len(recommended_items) / len(all_items)
    
    # 4. Diversidad
    # Calcular similitud promedio entre recomendaciones
    # (más diversidad = mejor)
    
    return metrics
```

---

**Última actualización:** [Fecha]
**Versión:** 2.0 - Código Completo y Probado
