---
title: "Ejemplos Codigo Recomendaciones"
category: "06_documentation"
tags: []
created: "2025-10-29"
path: "06_documentation/Best_practices/ejemplos_codigo_recomendaciones.md"
---

# 💻 Ejemplos de Código - Sistemas de Recomendaciones Personalizadas

## 🐍 PYTHON - Collaborative Filtering

### Ejemplo 1: Básico con Surprise

```python
from surprise import Dataset, Reader, SVD
from surprise.model_selection import train_test_split
import pandas as pd

# Datos: user_id, item_id, rating
data = {
    'user_id': [1, 1, 2, 2, 3, 3, 4, 4],
    'item_id': [101, 102, 101, 103, 102, 103, 101, 104],
    'rating': [5, 4, 5, 3, 4, 5, 5, 4]
}

df = pd.DataFrame(data)

# Configurar formato Surprise
reader = Reader(rating_scale=(1, 5))
dataset = Dataset.load_from_df(df[['user_id', 'item_id', 'rating']], reader)

# Entrenar modelo
trainset, testset = train_test_split(dataset, test_size=0.2)
model = SVD()
model.fit(trainset)

# Generar recomendaciones para usuario
user_id = 1
user_items = df[df['user_id'] == user_id]['item_id'].tolist()
all_items = df['item_id'].unique()
recommendations = []

for item_id in all_items:
    if item_id not in user_items:
        pred = model.predict(user_id, item_id)
        recommendations.append((item_id, pred.est))

# Top 5 recomendaciones
top_recommendations = sorted(recommendations, key=lambda x: x[1], reverse=True)[:5]
print("Recomendaciones para usuario", user_id)
for item_id, score in top_recommendations:
    print(f"Item {item_id}: Score {score:.2f}")
```

---

### Ejemplo 2: Content-Based Filtering

```python
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import pandas as pd

# Datos de productos con características
products = pd.DataFrame({
    'product_id': [1, 2, 3, 4, 5],
    'name': ['Laptop Gaming', 'Smartphone Pro', 'Tablet Office', 'Laptop Business', 'Smartphone Basic'],
    'category': ['Electronics', 'Electronics', 'Electronics', 'Electronics', 'Electronics'],
    'features': [
        'gaming performance graphics ram',
        'camera battery smartphone mobile',
        'tablet office productivity screen',
        'business laptop professional work',
        'smartphone basic budget mobile'
    ]
})

# Vectorizar características
vectorizer = TfidfVectorizer()
tfidf_matrix = vectorizer.fit_transform(products['features'])

# Calcular similitud
similarity_matrix = cosine_similarity(tfidf_matrix, tfidf_matrix)

# Función para recomendar productos similares
def recommend_similar_products(product_id, num_recommendations=3):
    product_idx = products[products['product_id'] == product_id].index[0]
    similarity_scores = list(enumerate(similarity_matrix[product_idx]))
    similarity_scores = sorted(similarity_scores, key=lambda x: x[1], reverse=True)
    
    recommendations = []
    for idx, score in similarity_scores[1:num_recommendations+1]:
        recommendations.append({
            'product_id': products.iloc[idx]['product_id'],
            'name': products.iloc[idx]['name'],
            'similarity': score
        })
    
    return recommendations

# Ejemplo: Recomendar productos similares al producto 1
recs = recommend_similar_products(1)
print("Productos similares al producto 1:")
for rec in recs:
    print(f"- {rec['name']} (Similitud: {rec['similarity']:.2f})")
```

---

### Ejemplo 3: Sistema Híbrido

```python
import numpy as np
from surprise import SVD, Dataset, Reader
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import pandas as pd

class HybridRecommender:
    def __init__(self):
        self.collab_model = None
        self.content_similarity = None
        self.products = None
        
    def fit(self, ratings_df, products_df):
        """Entrenar modelos colaborativo y content-based"""
        
        # 1. Modelo Colaborativo
        reader = Reader(rating_scale=(1, 5))
        dataset = Dataset.load_from_df(
            ratings_df[['user_id', 'item_id', 'rating']], 
            reader
        )
        trainset = dataset.build_full_trainset()
        self.collab_model = SVD()
        self.collab_model.fit(trainset)
        
        # 2. Content-Based
        self.products = products_df
        vectorizer = TfidfVectorizer()
        tfidf_matrix = vectorizer.fit_transform(products_df['features'])
        self.content_similarity = cosine_similarity(tfidf_matrix)
        
    def recommend(self, user_id, num_recommendations=5, alpha=0.7):
        """
        Recomendaciones híbridas
        alpha: peso del modelo colaborativo (0-1)
        """
        # Predicciones colaborativas
        collab_scores = []
        for item_id in self.products['product_id'].unique():
            pred = self.collab_model.predict(user_id, item_id)
            collab_scores.append((item_id, pred.est))
        
        # Normalizar scores colaborativos
        max_collab = max(score for _, score in collab_scores)
        collab_scores = [(item, score/max_collab) for item, score in collab_scores]
        
        # Combinar con content-based
        user_history = ratings_df[ratings_df['user_id'] == user_id]['item_id'].tolist()
        hybrid_scores = {}
        
        for item_id, collab_score in collab_scores:
            # Calcular score content-based (promedio de similitud con historial)
            content_score = 0
            if user_history:
                item_idx = self.products[self.products['product_id'] == item_id].index[0]
                similarities = []
                for hist_item in user_history[:5]:  # Top 5 más recientes
                    hist_idx = self.products[self.products['product_id'] == hist_item].index[0]
                    sim = self.content_similarity[item_idx][hist_idx]
                    similarities.append(sim)
                content_score = np.mean(similarities)
            
            # Combinar scores
            hybrid_score = alpha * collab_score + (1 - alpha) * content_score
            hybrid_scores[item_id] = hybrid_score
        
        # Top recomendaciones
        top_items = sorted(hybrid_scores.items(), key=lambda x: x[1], reverse=True)[:num_recommendations]
        return top_items

# Uso
recommender = HybridRecommender()
recommender.fit(ratings_df, products_df)
recommendations = recommender.recommend(user_id=1, num_recommendations=5, alpha=0.6)
```

---

## 🔧 INTEGRACIÓN API REST (FastAPI)

```python
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List
import pandas as pd
from surprise import SVD

app = FastAPI(title="Recomendaciones API")

# Modelo pre-entrenado (cargar desde archivo)
model = SVD()
# model = load_model('recommender_model.pkl')

class RecommendationRequest(BaseModel):
    user_id: int
    num_recommendations: int = 10

class RecommendationResponse(BaseModel):
    user_id: int
    recommendations: List[dict]

@app.post("/recommendations", response_model=RecommendationResponse)
async def get_recommendations(request: RecommendationRequest):
    """
    Genera recomendaciones personalizadas para un usuario
    """
    try:
        # Obtener todos los items disponibles
        all_items = get_all_items()  # Función que retorna lista de items
        
        # Obtener items que el usuario ya ha visto/comprado
        user_history = get_user_history(request.user_id)
        user_items = [item['item_id'] for item in user_history]
        
        # Generar predicciones
        recommendations = []
        for item_id in all_items:
            if item_id not in user_items:
                pred = model.predict(request.user_id, item_id)
                recommendations.append({
                    'item_id': item_id,
                    'score': pred.est,
                    'confidence': 1 - abs(pred.actual - pred.est) / 5  # Normalizar
                })
        
        # Ordenar y tomar top N
        recommendations.sort(key=lambda x: x['score'], reverse=True)
        top_recommendations = recommendations[:request.num_recommendations]
        
        return RecommendationResponse(
            user_id=request.user_id,
            recommendations=top_recommendations
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/recommendations/{user_id}")
async def get_recommendations_simple(user_id: int, num: int = 10):
    """Endpoint simple GET"""
    request = RecommendationRequest(user_id=user_id, num_recommendations=num)
    return await get_recommendations(request)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
```

---

## 📊 PROCESAMIENTO DE DATOS HISTÓRICOS

```python
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

def prepare_user_data(transactions_df):
    """
    Prepara datos históricos para sistema de recomendaciones
    """
    # Agregar features útiles
    transactions_df['date'] = pd.to_datetime(transactions_df['date'])
    
    # Ratings implícitos basados en comportamiento
    def calculate_rating(row):
        rating = 3.0  # Base
        
        # Aumentar rating por compra
        if row['action'] == 'purchase':
            rating += 2.0
        elif row['action'] == 'add_to_cart':
            rating += 1.0
        elif row['action'] == 'view':
            rating += 0.5
        
        # Decay temporal (más reciente = más peso)
        days_ago = (datetime.now() - row['date']).days
        time_decay = max(0, 1 - (days_ago / 365))  # 1 año máximo
        rating *= time_decay
        
        return min(5.0, rating)
    
    transactions_df['rating'] = transactions_df.apply(calculate_rating, axis=1)
    
    # Agregar features de usuario
    user_features = transactions_df.groupby('user_id').agg({
        'item_id': 'count',  # Total interacciones
        'rating': 'mean',     # Rating promedio
        'date': 'max'        # Última actividad
    }).rename(columns={
        'item_id': 'total_interactions',
        'rating': 'avg_rating',
        'date': 'last_activity'
    })
    
    return transactions_df, user_features

def get_user_preferences(user_id, transactions_df, products_df):
    """
    Extrae preferencias del usuario basado en historial
    """
    user_transactions = transactions_df[transactions_df['user_id'] == user_id]
    
    # Preferencias por categoría
    user_cats = user_transactions.merge(
        products_df[['product_id', 'category']], 
        left_on='item_id', 
        right_on='product_id'
    )
    category_prefs = user_cats['category'].value_counts(normalize=True).to_dict()
    
    # Preferencias por precio
    user_transactions_with_price = user_transactions.merge(
        products_df[['product_id', 'price']], 
        left_on='item_id', 
        right_on='product_id'
    )
    avg_price = user_transactions_with_price['price'].mean()
    price_range = {
        'min': avg_price * 0.5,
        'max': avg_price * 1.5
    }
    
    # Preferencias por marca
    if 'brand' in products_df.columns:
        user_brands = user_transactions.merge(
            products_df[['product_id', 'brand']], 
            left_on='item_id', 
            right_on='product_id'
        )
        brand_prefs = user_brands['brand'].value_counts(normalize=True).head(5).to_dict()
    else:
        brand_prefs = {}
    
    return {
        'categories': category_prefs,
        'price_range': price_range,
        'brands': brand_prefs,
        'total_purchases': len(user_transactions)
    }
```

---

## 🎯 RECOMENDACIONES CONTEXTUALES (Tiempo Real)

```python
from datetime import datetime
import json

class ContextualRecommender:
    def __init__(self, base_model):
        self.base_model = base_model
        
    def recommend_with_context(self, user_id, context, num_recommendations=10):
        """
        Recomendaciones considerando contexto
        context: dict con 'time_of_day', 'device', 'location', etc.
        """
        # Obtener recomendaciones base
        base_recs = self.base_model.recommend(user_id, num_recommendations * 2)
        
        # Ajustar por contexto
        contextual_scores = {}
        for item_id, score in base_recs:
            context_adjustment = self._calculate_context_adjustment(item_id, context)
            contextual_scores[item_id] = score * context_adjustment
        
        # Ordenar y retornar top N
        sorted_recs = sorted(
            contextual_scores.items(), 
            key=lambda x: x[1], 
            reverse=True
        )[:num_recommendations]
        
        return sorted_recs
    
    def _calculate_context_adjustment(self, item_id, context):
        """Calcula ajuste según contexto"""
        adjustment = 1.0
        
        # Ajuste por hora del día
        if 'time_of_day' in context:
            hour = datetime.now().hour
            if item_id in self._get_morning_items() and 6 <= hour <= 12:
                adjustment *= 1.3
            elif item_id in self._get_evening_items() and 18 <= hour <= 23:
                adjustment *= 1.3
        
        # Ajuste por dispositivo
        if 'device' in context:
            if context['device'] == 'mobile' and item_id in self._get_mobile_optimized():
                adjustment *= 1.2
        
        # Ajuste por estación/promociones
        if 'season' in context or 'promotion' in context:
            # Lógica específica según estación/promoción
            adjustment *= 1.1
        
        return adjustment
    
    def _get_morning_items(self):
        """Items populares en la mañana (ej: café, desayunos)"""
        return [101, 102, 103]  # IDs de ejemplo
    
    def _get_evening_items(self):
        """Items populares en la tarde/noche"""
        return [201, 202, 203]
    
    def _get_mobile_optimized(self):
        """Items optimizados para móvil"""
        return [301, 302, 303]
```

---

## 📈 MÉTRICAS Y EVALUACIÓN

```python
from surprise import accuracy
from surprise.model_selection import cross_validate
import pandas as pd

def evaluate_model(model, dataset, cv=5):
    """
    Evalúa modelo con cross-validation
    """
    results = cross_validate(
        model, 
        dataset, 
        measures=['RMSE', 'MAE'], 
        cv=cv, 
        verbose=True
    )
    
    print(f"RMSE promedio: {results['test_rmse'].mean():.3f}")
    print(f"MAE promedio: {results['test_mae'].mean():.3f}")
    
    return results

def calculate_business_metrics(recommendations, actual_purchases):
    """
    Métricas de negocio: Precision@K, Recall@K, Revenue
    """
    # Precision@10: % de recomendaciones que resultan en compra
    recommended_items = set([r['item_id'] for r in recommendations[:10]])
    purchased_items = set(actual_purchases)
    
    relevant_recommended = recommended_items.intersection(purchased_items)
    precision_at_10 = len(relevant_recommended) / 10 if len(recommendations) >= 10 else 0
    
    # Recall@10: % de compras que fueron recomendadas
    recall_at_10 = len(relevant_recommended) / len(purchased_items) if purchased_items else 0
    
    # Revenue de recomendaciones
    revenue = sum(
        item['price'] for item in recommendations[:10] 
        if item['item_id'] in purchased_items
    )
    
    return {
        'precision_at_10': precision_at_10,
        'recall_at_10': recall_at_10,
        'revenue_from_recommendations': revenue,
        'conversion_rate': precision_at_10
    }
```

---

## 🔄 RE-ENTRENAMIENTO AUTOMÁTICO

```python
import schedule
import time
import joblib
from datetime import datetime

def retrain_model():
    """
    Función para re-entrenar modelo periódicamente
    Ejecutar con scheduler (cron, schedule, etc.)
    """
    print(f"Iniciando re-entrenamiento: {datetime.now()}")
    
    # Cargar datos actualizados
    new_data = load_latest_transactions()
    
    # Preparar datos
    dataset = prepare_dataset(new_data)
    
    # Entrenar nuevo modelo
    model = SVD()
    trainset = dataset.build_full_trainset()
    model.fit(trainset)
    
    # Guardar modelo
    model_path = f'models/recommender_{datetime.now().strftime("%Y%m%d_%H%M%S")}.pkl'
    joblib.dump(model, model_path)
    
    # Actualizar modelo en producción
    update_production_model(model)
    
    print(f"Modelo actualizado: {model_path}")

# Configurar re-entrenamiento semanal
schedule.every().sunday.at("02:00").do(retrain_model)

# Ejecutar scheduler (en producción usar mejor sistema de tareas)
while True:
    schedule.run_pending()
    time.sleep(3600)  # Verificar cada hora
```

---

## 🚀 DEPLOYMENT (Docker + FastAPI)

```dockerfile
# Dockerfile
FROM python:3.9-slim

WORKDIR /app

# Instalar dependencias
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiar código
COPY . .

# Exponer puerto
EXPOSE 8000

# Comando para iniciar API
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

```yaml
# docker-compose.yml
version: '3.8'

services:
  recommender-api:
    build: .
    ports:
      - "8000:8000"
    environment:
      - MODEL_PATH=/app/models/recommender.pkl
      - DATA_PATH=/app/data/
    volumes:
      - ./models:/app/models
      - ./data:/app/data
    restart: unless-stopped
```

---

**Última actualización:** [Fecha]
**Versión:** 1.0 - Ejemplos de Código Prácticos

