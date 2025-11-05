---
title: "Performance Optimization"
category: "06_documentation"
tags: []
created: "2025-10-29"
path: "06_documentation/Other/performance_optimization.md"
---

# ⚡ Guía de Optimización de Performance - ClickUp Brain

## Visión General

Esta guía proporciona estrategias avanzadas para optimizar el rendimiento de ClickUp Brain, desde la optimización de consultas de base de datos hasta la implementación de técnicas de caching y escalabilidad horizontal.

## 🎯 Métricas de Performance

### KPIs de Performance

```python
# performance_metrics.py
from dataclasses import dataclass
from typing import Dict, List
import time
import psutil
import asyncio

@dataclass
class PerformanceMetrics:
    """Métricas de performance del sistema."""
    
    # Métricas de respuesta
    api_response_time: float  # ms
    database_query_time: float  # ms
    ai_inference_time: float  # ms
    cache_hit_rate: float  # %
    
    # Métricas de recursos
    cpu_usage: float  # %
    memory_usage: float  # %
    disk_io: float  # MB/s
    network_throughput: float  # Mbps
    
    # Métricas de concurrencia
    active_connections: int
    requests_per_second: float
    concurrent_users: int
    queue_length: int
    
    # Métricas de calidad
    error_rate: float  # %
    availability: float  # %
    data_accuracy: float  # %
    user_satisfaction: float  # %

class PerformanceMonitor:
    """Monitor de performance en tiempo real."""
    
    def __init__(self):
        self.metrics_history = []
        self.alert_thresholds = {
            'api_response_time': 1000,  # 1 segundo
            'database_query_time': 500,  # 500ms
            'ai_inference_time': 2000,  # 2 segundos
            'cpu_usage': 80,  # 80%
            'memory_usage': 85,  # 85%
            'error_rate': 5,  # 5%
            'cache_hit_rate': 70  # 70%
        }
    
    async def collect_metrics(self) -> PerformanceMetrics:
        """Recolectar métricas del sistema."""
        
        # Métricas de sistema
        cpu_usage = psutil.cpu_percent(interval=1)
        memory = psutil.virtual_memory()
        disk_io = psutil.disk_io_counters()
        
        # Métricas de aplicación
        app_metrics = await self.get_application_metrics()
        
        metrics = PerformanceMetrics(
            api_response_time=app_metrics.get('avg_response_time', 0),
            database_query_time=app_metrics.get('avg_query_time', 0),
            ai_inference_time=app_metrics.get('avg_inference_time', 0),
            cache_hit_rate=app_metrics.get('cache_hit_rate', 0),
            cpu_usage=cpu_usage,
            memory_usage=memory.percent,
            disk_io=disk_io.read_bytes + disk_io.write_bytes if disk_io else 0,
            network_throughput=app_metrics.get('network_throughput', 0),
            active_connections=app_metrics.get('active_connections', 0),
            requests_per_second=app_metrics.get('rps', 0),
            concurrent_users=app_metrics.get('concurrent_users', 0),
            queue_length=app_metrics.get('queue_length', 0),
            error_rate=app_metrics.get('error_rate', 0),
            availability=app_metrics.get('availability', 100),
            data_accuracy=app_metrics.get('data_accuracy', 100),
            user_satisfaction=app_metrics.get('user_satisfaction', 100)
        )
        
        self.metrics_history.append(metrics)
        
        # Verificar alertas
        await self.check_performance_alerts(metrics)
        
        return metrics
    
    async def check_performance_alerts(self, metrics: PerformanceMetrics):
        """Verificar alertas de performance."""
        
        alerts = []
        
        if metrics.api_response_time > self.alert_thresholds['api_response_time']:
            alerts.append(f"API response time alto: {metrics.api_response_time}ms")
        
        if metrics.cpu_usage > self.alert_thresholds['cpu_usage']:
            alerts.append(f"CPU usage alto: {metrics.cpu_usage}%")
        
        if metrics.memory_usage > self.alert_thresholds['memory_usage']:
            alerts.append(f"Memory usage alto: {metrics.memory_usage}%")
        
        if metrics.error_rate > self.alert_thresholds['error_rate']:
            alerts.append(f"Error rate alto: {metrics.error_rate}%")
        
        if metrics.cache_hit_rate < self.alert_thresholds['cache_hit_rate']:
            alerts.append(f"Cache hit rate bajo: {metrics.cache_hit_rate}%")
        
        if alerts:
            await self.send_performance_alerts(alerts)
    
    async def send_performance_alerts(self, alerts: List[str]):
        """Enviar alertas de performance."""
        # Implementar notificaciones (Slack, email, etc.)
        for alert in alerts:
            print(f"🚨 ALERTA DE PERFORMANCE: {alert}")
```

## 🗄️ Optimización de Base de Datos

### Optimización de Consultas

```python
# database_optimization.py
from sqlalchemy import text, Index, func
from sqlalchemy.orm import joinedload, selectinload
import time

class DatabaseOptimizer:
    """Optimizador de consultas de base de datos."""
    
    def __init__(self, db_session):
        self.db = db_session
    
    def optimize_strategic_opportunities_query(self, filters: dict):
        """Optimizar consulta de oportunidades estratégicas."""
        
        # Query original (lenta)
        # opportunities = Opportunity.query.filter(
        #     Opportunity.market_segment == filters['market_segment'],
        #     Opportunity.created_at > filters['start_date']
        # ).all()
        
        # Query optimizada
        query = self.db.query(Opportunity).options(
            # Eager loading para evitar N+1 queries
            joinedload(Opportunity.market_analysis),
            selectinload(Opportunity.competitive_landscape)
        ).filter(
            Opportunity.market_segment == filters['market_segment'],
            Opportunity.created_at > filters['start_date']
        )
        
        # Usar índices compuestos
        if 'priority' in filters:
            query = query.filter(Opportunity.priority == filters['priority'])
        
        # Paginación para grandes datasets
        page = filters.get('page', 1)
        per_page = filters.get('per_page', 50)
        
        return query.paginate(page=page, per_page=per_page, error_out=False)
    
    def create_performance_indexes(self):
        """Crear índices para optimizar performance."""
        
        indexes = [
            # Índice compuesto para consultas frecuentes
            Index('idx_opportunities_market_created', 
                  'market_segment', 'created_at'),
            
            # Índice para búsquedas por prioridad
            Index('idx_opportunities_priority_status', 
                  'priority', 'status'),
            
            # Índice para análisis de tendencias
            Index('idx_opportunities_trend_analysis', 
                  'market_segment', 'created_at', 'success_probability'),
            
            # Índice para usuarios y equipos
            Index('idx_opportunities_user_team', 
                  'created_by', 'team_id', 'created_at')
        ]
        
        for index in indexes:
            try:
                index.create(self.db.bind)
                print(f"✅ Índice creado: {index.name}")
            except Exception as e:
                print(f"❌ Error creando índice {index.name}: {e}")
    
    def analyze_slow_queries(self):
        """Analizar consultas lentas."""
        
        # Habilitar query logging
        self.db.execute(text("SET log_min_duration_statement = 1000"))  # Log queries > 1s
        
        # Consulta para obtener queries lentas
        slow_queries = self.db.execute(text("""
            SELECT query, mean_time, calls, total_time
            FROM pg_stat_statements
            WHERE mean_time > 1000  -- Queries > 1 segundo
            ORDER BY mean_time DESC
            LIMIT 10
        """)).fetchall()
        
        print("🐌 Consultas lentas detectadas:")
        for query in slow_queries:
            print(f"  • Tiempo promedio: {query.mean_time}ms")
            print(f"  • Llamadas: {query.calls}")
            print(f"  • Query: {query.query[:100]}...")
            print()
    
    def optimize_bulk_operations(self, data: list):
        """Optimizar operaciones en lote."""
        
        # Usar bulk_insert_mappings para inserción masiva
        self.db.bulk_insert_mappings(Opportunity, data)
        
        # Usar bulk_update_mappings para actualización masiva
        self.db.bulk_update_mappings(Opportunity, data)
        
        # Commit en lotes para evitar transacciones largas
        batch_size = 1000
        for i in range(0, len(data), batch_size):
            batch = data[i:i + batch_size]
            self.db.bulk_insert_mappings(Opportunity, batch)
            self.db.commit()
    
    def implement_query_caching(self):
        """Implementar cache de consultas."""
        
        from functools import lru_cache
        import hashlib
        
        @lru_cache(maxsize=1000)
        def cached_query(query_hash: str, params: tuple):
            """Cache de consultas frecuentes."""
            # Reconstruir query desde hash y parámetros
            # Ejecutar query y retornar resultados
            pass
        
        def get_cached_opportunities(market_segment: str, start_date: str):
            """Obtener oportunidades con cache."""
            
            # Crear hash de la consulta
            query_string = f"market_segment={market_segment}&start_date={start_date}"
            query_hash = hashlib.md5(query_string.encode()).hexdigest()
            
            # Verificar cache
            cached_result = cached_query(query_hash, (market_segment, start_date))
            
            if cached_result:
                return cached_result
            
            # Ejecutar query si no está en cache
            result = self.optimize_strategic_opportunities_query({
                'market_segment': market_segment,
                'start_date': start_date
            })
            
            return result
```

### Optimización de Esquema

```sql
-- database_schema_optimization.sql

-- 1. Particionado de tablas por fecha
CREATE TABLE strategic_opportunities (
    id SERIAL PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    market_segment VARCHAR(100) NOT NULL,
    created_at TIMESTAMP NOT NULL,
    success_probability DECIMAL(5,2),
    -- Otros campos...
) PARTITION BY RANGE (created_at);

-- Crear particiones mensuales
CREATE TABLE strategic_opportunities_2024_01 
PARTITION OF strategic_opportunities
FOR VALUES FROM ('2024-01-01') TO ('2024-02-01');

CREATE TABLE strategic_opportunities_2024_02 
PARTITION OF strategic_opportunities
FOR VALUES FROM ('2024-02-01') TO ('2024-03-01');

-- 2. Índices parciales para consultas específicas
CREATE INDEX idx_high_priority_opportunities 
ON strategic_opportunities (created_at, market_segment)
WHERE priority = 'high';

-- 3. Índices de expresión para búsquedas complejas
CREATE INDEX idx_opportunities_title_search 
ON strategic_opportunities USING gin(to_tsvector('english', title));

-- 4. Materialized views para agregaciones costosas
CREATE MATERIALIZED VIEW mv_market_opportunities_summary AS
SELECT 
    market_segment,
    DATE_TRUNC('month', created_at) as month,
    COUNT(*) as total_opportunities,
    AVG(success_probability) as avg_success_probability,
    SUM(CASE WHEN status = 'won' THEN 1 ELSE 0 END) as won_opportunities
FROM strategic_opportunities
GROUP BY market_segment, DATE_TRUNC('month', created_at);

-- Refrescar materialized view periódicamente
CREATE OR REPLACE FUNCTION refresh_market_summary()
RETURNS void AS $$
BEGIN
    REFRESH MATERIALIZED VIEW CONCURRENTLY mv_market_opportunities_summary;
END;
$$ LANGUAGE plpgsql;

-- 5. Configuración de PostgreSQL para performance
-- postgresql.conf optimizations
ALTER SYSTEM SET shared_buffers = '256MB';
ALTER SYSTEM SET effective_cache_size = '1GB';
ALTER SYSTEM SET maintenance_work_mem = '64MB';
ALTER SYSTEM SET checkpoint_completion_target = 0.9;
ALTER SYSTEM SET wal_buffers = '16MB';
ALTER SYSTEM SET default_statistics_target = 100;
```

## 🚀 Optimización de APIs

### Caching Estratégico

```python
# api_optimization.py
from flask import Flask, request, jsonify
from flask_caching import Cache
import redis
import json
import hashlib
from functools import wraps

app = Flask(__name__)
cache = Cache(app, config={'CACHE_TYPE': 'redis'})

class APIOptimizer:
    """Optimizador de APIs."""
    
    def __init__(self):
        self.redis_client = redis.Redis(host='localhost', port=6379, db=0)
        self.cache_ttl = {
            'strategic_opportunities': 300,  # 5 minutos
            'market_analysis': 600,  # 10 minutos
            'user_preferences': 1800,  # 30 minutos
            'ai_predictions': 900  # 15 minutos
        }
    
    def cache_response(self, ttl: int = 300):
        """Decorator para cachear respuestas de API."""
        
        def decorator(func):
            @wraps(func)
            def wrapper(*args, **kwargs):
                # Generar clave de cache basada en parámetros
                cache_key = self.generate_cache_key(func.__name__, request.args)
                
                # Verificar cache
                cached_response = self.redis_client.get(cache_key)
                if cached_response:
                    return jsonify(json.loads(cached_response))
                
                # Ejecutar función y cachear resultado
                result = func(*args, **kwargs)
                self.redis_client.setex(
                    cache_key, 
                    ttl, 
                    json.dumps(result, default=str)
                )
                
                return jsonify(result)
            
            return wrapper
        return decorator
    
    def generate_cache_key(self, function_name: str, params: dict) -> str:
        """Generar clave de cache única."""
        
        # Ordenar parámetros para consistencia
        sorted_params = sorted(params.items())
        param_string = '&'.join([f"{k}={v}" for k, v in sorted_params])
        
        # Crear hash único
        key_string = f"{function_name}:{param_string}"
        return hashlib.md5(key_string.encode()).hexdigest()
    
    def implement_response_compression(self):
        """Implementar compresión de respuestas."""
        
        from flask_compress import Compress
        Compress(app)
        
        # Configurar compresión
        app.config['COMPRESS_MIMETYPES'] = [
            'text/html',
            'text/css',
            'text/xml',
            'application/json',
            'application/javascript'
        ]
    
    def optimize_pagination(self, query, page: int, per_page: int):
        """Optimizar paginación de resultados."""
        
        # Usar cursor-based pagination para grandes datasets
        if page > 100:  # Para páginas muy altas, usar cursor
            return self.cursor_based_pagination(query, page, per_page)
        
        # Paginación tradicional para páginas bajas
        return query.paginate(page=page, per_page=per_page, error_out=False)
    
    def cursor_based_pagination(self, query, cursor: str, per_page: int):
        """Paginación basada en cursor para mejor performance."""
        
        # Decodificar cursor
        cursor_data = json.loads(cursor) if cursor else {}
        last_id = cursor_data.get('last_id', 0)
        
        # Query optimizada con cursor
        results = query.filter(Opportunity.id > last_id)\
                      .order_by(Opportunity.id)\
                      .limit(per_page + 1).all()
        
        # Determinar si hay más páginas
        has_next = len(results) > per_page
        if has_next:
            results = results[:-1]  # Remover último elemento
        
        # Generar nuevo cursor
        next_cursor = None
        if has_next and results:
            next_cursor = json.dumps({
                'last_id': results[-1].id
            })
        
        return {
            'results': results,
            'has_next': has_next,
            'next_cursor': next_cursor
        }
    
    def implement_rate_limiting(self):
        """Implementar rate limiting inteligente."""
        
        from flask_limiter import Limiter
        from flask_limiter.util import get_remote_address
        
        limiter = Limiter(
            app,
            key_func=get_remote_address,
            default_limits=["1000 per hour", "100 per minute"]
        )
        
        # Rate limiting específico por endpoint
        @app.route('/api/v1/strategic-opportunities')
        @limiter.limit("50 per minute")
        def get_opportunities():
            # Implementación del endpoint
            pass
        
        @app.route('/api/v1/ai-analysis')
        @limiter.limit("10 per minute")
        def ai_analysis():
            # Implementación del endpoint
            pass
    
    def optimize_database_connections(self):
        """Optimizar conexiones de base de datos."""
        
        from sqlalchemy import create_engine
        from sqlalchemy.pool import QueuePool
        
        # Configurar connection pooling
        engine = create_engine(
            DATABASE_URL,
            poolclass=QueuePool,
            pool_size=20,  # Conexiones en el pool
            max_overflow=30,  # Conexiones adicionales
            pool_pre_ping=True,  # Verificar conexiones antes de usar
            pool_recycle=3600  # Reciclar conexiones cada hora
        )
        
        return engine
```

### Optimización de Serialización

```python
# serialization_optimization.py
from marshmallow import Schema, fields, post_dump
import orjson
from typing import Dict, Any

class OptimizedOpportunitySchema(Schema):
    """Schema optimizado para serialización de oportunidades."""
    
    id = fields.Int()
    title = fields.Str()
    market_segment = fields.Str()
    success_probability = fields.Decimal(places=2)
    created_at = fields.DateTime()
    
    # Campos calculados
    priority_score = fields.Method('calculate_priority_score')
    
    def calculate_priority_score(self, obj):
        """Calcular score de prioridad."""
        return (obj.success_probability * 0.7 + 
                obj.market_potential * 0.3)
    
    @post_dump
    def optimize_output(self, data: Dict[str, Any], **kwargs) -> Dict[str, Any]:
        """Optimizar output de serialización."""
        
        # Remover campos None
        return {k: v for k, v in data.items() if v is not None}

class FastJSONEncoder:
    """Encoder JSON optimizado."""
    
    @staticmethod
    def encode(data: Any) -> bytes:
        """Codificar datos usando orjson (más rápido que json estándar)."""
        return orjson.dumps(data, option=orjson.OPT_SERIALIZE_NUMPY)
    
    @staticmethod
    def decode(data: bytes) -> Any:
        """Decodificar datos JSON."""
        return orjson.loads(data)

class ResponseOptimizer:
    """Optimizador de respuestas de API."""
    
    def __init__(self):
        self.schema = OptimizedOpportunitySchema()
        self.json_encoder = FastJSONEncoder()
    
    def optimize_api_response(self, data: list, include_metadata: bool = True):
        """Optimizar respuesta de API."""
        
        # Serializar datos
        serialized_data = self.schema.dump(data, many=True)
        
        # Comprimir datos si es necesario
        if len(serialized_data) > 1000:  # Si hay muchos elementos
            serialized_data = self.compress_large_response(serialized_data)
        
        response = {
            'data': serialized_data,
            'count': len(serialized_data)
        }
        
        if include_metadata:
            response['metadata'] = {
                'timestamp': datetime.utcnow().isoformat(),
                'version': '1.0',
                'optimized': True
            }
        
        return response
    
    def compress_large_response(self, data: list) -> list:
        """Comprimir respuestas grandes."""
        
        # Implementar compresión de datos
        # Por ejemplo, agrupar por market_segment
        grouped_data = {}
        for item in data:
            segment = item.get('market_segment', 'other')
            if segment not in grouped_data:
                grouped_data[segment] = []
            grouped_data[segment].append(item)
        
        return grouped_data
```

## 🤖 Optimización de AI Services

### Optimización de Modelos

```python
# ai_optimization.py
import torch
import numpy as np
from transformers import AutoTokenizer, AutoModel
import onnx
import onnxruntime as ort
from typing import List, Dict, Any

class AIModelOptimizer:
    """Optimizador de modelos de AI."""
    
    def __init__(self):
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        self.optimized_models = {}
    
    def optimize_model_inference(self, model, input_data):
        """Optimizar inferencia de modelo."""
        
        # 1. Usar mixed precision para acelerar
        with torch.cuda.amp.autocast():
            with torch.no_grad():
                outputs = model(input_data)
        
        return outputs
    
    def convert_to_onnx(self, model, input_shape, output_path):
        """Convertir modelo PyTorch a ONNX para mejor performance."""
        
        model.eval()
        dummy_input = torch.randn(1, *input_shape)
        
        torch.onnx.export(
            model,
            dummy_input,
            output_path,
            export_params=True,
            opset_version=11,
            do_constant_folding=True,
            input_names=['input'],
            output_names=['output'],
            dynamic_axes={
                'input': {0: 'batch_size'},
                'output': {0: 'batch_size'}
            }
        )
        
        print(f"✅ Modelo convertido a ONNX: {output_path}")
    
    def optimize_onnx_model(self, onnx_path: str, optimized_path: str):
        """Optimizar modelo ONNX."""
        
        # Cargar modelo ONNX
        model = onnx.load(onnx_path)
        
        # Optimizar modelo
        from onnxruntime.tools import optimizer
        optimized_model = optimizer.optimize_model(model)
        
        # Guardar modelo optimizado
        onnx.save(optimized_model.model, optimized_path)
        
        print(f"✅ Modelo ONNX optimizado: {optimized_path}")
    
    def implement_model_caching(self):
        """Implementar cache de modelos."""
        
        from functools import lru_cache
        
        @lru_cache(maxsize=10)
        def get_cached_model(model_name: str, model_version: str):
            """Cache de modelos cargados."""
            
            model_path = f"models/{model_name}_{model_version}"
            
            # Cargar modelo ONNX optimizado
            session = ort.InferenceSession(
                f"{model_path}.onnx",
                providers=['CUDAExecutionProvider', 'CPUExecutionProvider']
            )
            
            return session
        
        return get_cached_model
    
    def batch_inference(self, model, input_batch: List[Any], batch_size: int = 32):
        """Optimizar inferencia en lotes."""
        
        results = []
        
        for i in range(0, len(input_batch), batch_size):
            batch = input_batch[i:i + batch_size]
            
            # Procesar lote
            batch_results = self.optimize_model_inference(model, batch)
            results.extend(batch_results)
        
        return results
    
    def implement_model_quantization(self, model):
        """Implementar cuantización de modelo para reducir tamaño."""
        
        # Cuantización dinámica
        quantized_model = torch.quantization.quantize_dynamic(
            model,
            {torch.nn.Linear, torch.nn.Conv2d},
            dtype=torch.qint8
        )
        
        return quantized_model
    
    def optimize_embedding_generation(self, texts: List[str], model_name: str = "sentence-transformers/all-MiniLM-L6-v2"):
        """Optimizar generación de embeddings."""
        
        # Cargar tokenizer y modelo
        tokenizer = AutoTokenizer.from_pretrained(model_name)
        model = AutoModel.from_pretrained(model_name)
        
        # Tokenizar textos en lotes
        batch_size = 32
        embeddings = []
        
        for i in range(0, len(texts), batch_size):
            batch_texts = texts[i:i + batch_size]
            
            # Tokenizar
            inputs = tokenizer(
                batch_texts,
                padding=True,
                truncation=True,
                return_tensors='pt',
                max_length=512
            )
            
            # Generar embeddings
            with torch.no_grad():
                outputs = model(**inputs)
                batch_embeddings = outputs.last_hidden_state.mean(dim=1)
                embeddings.append(batch_embeddings)
        
        # Concatenar embeddings
        return torch.cat(embeddings, dim=0)
```

### Optimización de Vector Search

```python
# vector_search_optimization.py
import faiss
import numpy as np
from typing import List, Tuple, Dict
import pickle

class VectorSearchOptimizer:
    """Optimizador de búsqueda vectorial."""
    
    def __init__(self, dimension: int = 384):
        self.dimension = dimension
        self.index = None
        self.id_to_text = {}
    
    def build_faiss_index(self, embeddings: np.ndarray, index_type: str = "IVF"):
        """Construir índice FAISS optimizado."""
        
        if index_type == "IVF":
            # Índice IVF para búsquedas rápidas
            quantizer = faiss.IndexFlatL2(self.dimension)
            self.index = faiss.IndexIVFFlat(quantizer, self.dimension, 100)
            
        elif index_type == "HNSW":
            # Índice HNSW para búsquedas de alta calidad
            self.index = faiss.IndexHNSWFlat(self.dimension, 32)
        
        # Entrenar índice
        self.index.train(embeddings)
        self.index.add(embeddings)
        
        print(f"✅ Índice FAISS construido: {self.index.ntotal} vectores")
    
    def optimize_search_parameters(self, nprobe: int = 10, ef_search: int = 64):
        """Optimizar parámetros de búsqueda."""
        
        if hasattr(self.index, 'nprobe'):
            self.index.nprobe = nprobe
        
        if hasattr(self.index, 'hnsw'):
            self.index.hnsw.efSearch = ef_search
    
    def search_similar_opportunities(self, query_embedding: np.ndarray, k: int = 10) -> List[Tuple[int, float]]:
        """Buscar oportunidades similares."""
        
        # Normalizar query
        query_embedding = query_embedding.reshape(1, -1)
        faiss.normalize_L2(query_embedding)
        
        # Búsqueda
        distances, indices = self.index.search(query_embedding, k)
        
        # Retornar resultados con scores
        results = []
        for i, (idx, distance) in enumerate(zip(indices[0], distances[0])):
            if idx != -1:  # Índice válido
                score = 1 - distance  # Convertir distancia a score
                results.append((idx, score))
        
        return results
    
    def implement_approximate_search(self, query_embedding: np.ndarray, k: int = 10, threshold: float = 0.7):
        """Implementar búsqueda aproximada para mejor performance."""
        
        # Búsqueda rápida con menos precisión
        self.optimize_search_parameters(nprobe=5, ef_search=32)
        
        results = self.search_similar_opportunities(query_embedding, k * 2)
        
        # Filtrar por threshold
        filtered_results = [(idx, score) for idx, score in results if score >= threshold]
        
        return filtered_results[:k]
    
    def cache_search_results(self, query_hash: str, results: List[Tuple[int, float]], ttl: int = 3600):
        """Cachear resultados de búsqueda."""
        
        cache_data = {
            'results': results,
            'timestamp': time.time()
        }
        
        # Guardar en Redis o archivo
        with open(f"cache/{query_hash}.pkl", 'wb') as f:
            pickle.dump(cache_data, f)
    
    def load_cached_results(self, query_hash: str, ttl: int = 3600) -> List[Tuple[int, float]]:
        """Cargar resultados cacheados."""
        
        try:
            with open(f"cache/{query_hash}.pkl", 'rb') as f:
                cache_data = pickle.load(f)
            
            # Verificar TTL
            if time.time() - cache_data['timestamp'] < ttl:
                return cache_data['results']
            
        except FileNotFoundError:
            pass
        
        return None
```

## 📊 Monitoreo de Performance

### Dashboard de Performance

```python
# performance_dashboard.py
from flask import Flask, render_template, jsonify
import plotly.graph_objs as go
import plotly.utils
import json

app = Flask(__name__)

class PerformanceDashboard:
    """Dashboard de performance en tiempo real."""
    
    def __init__(self):
        self.metrics_collector = PerformanceMonitor()
    
    def generate_performance_charts(self, time_range: str = "1h"):
        """Generar gráficos de performance."""
        
        # Recopilar métricas
        metrics = self.metrics_collector.get_metrics_history(time_range)
        
        charts = {
            'response_time': self.create_response_time_chart(metrics),
            'throughput': self.create_throughput_chart(metrics),
            'error_rate': self.create_error_rate_chart(metrics),
            'resource_usage': self.create_resource_usage_chart(metrics)
        }
        
        return charts
    
    def create_response_time_chart(self, metrics: List[Dict]) -> str:
        """Crear gráfico de tiempo de respuesta."""
        
        timestamps = [m['timestamp'] for m in metrics]
        response_times = [m['api_response_time'] for m in metrics]
        
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=timestamps,
            y=response_times,
            mode='lines+markers',
            name='Response Time',
            line=dict(color='blue')
        ))
        
        # Línea de threshold
        fig.add_hline(y=1000, line_dash="dash", line_color="red", 
                     annotation_text="Threshold: 1000ms")
        
        fig.update_layout(
            title="API Response Time",
            xaxis_title="Time",
            yaxis_title="Response Time (ms)",
            hovermode='x unified'
        )
        
        return json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)
    
    def create_throughput_chart(self, metrics: List[Dict]) -> str:
        """Crear gráfico de throughput."""
        
        timestamps = [m['timestamp'] for m in metrics]
        rps = [m['requests_per_second'] for m in metrics]
        
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=timestamps,
            y=rps,
            mode='lines+markers',
            name='Requests/Second',
            line=dict(color='green'),
            fill='tonexty'
        ))
        
        fig.update_layout(
            title="Requests Per Second",
            xaxis_title="Time",
            yaxis_title="RPS",
            hovermode='x unified'
        )
        
        return json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)
    
    def create_error_rate_chart(self, metrics: List[Dict]) -> str:
        """Crear gráfico de tasa de errores."""
        
        timestamps = [m['timestamp'] for m in metrics]
        error_rates = [m['error_rate'] for m in metrics]
        
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=timestamps,
            y=error_rates,
            mode='lines+markers',
            name='Error Rate',
            line=dict(color='red'),
            fill='tozeroy'
        ))
        
        # Línea de threshold
        fig.add_hline(y=5, line_dash="dash", line_color="orange",
                     annotation_text="Threshold: 5%")
        
        fig.update_layout(
            title="Error Rate",
            xaxis_title="Time",
            yaxis_title="Error Rate (%)",
            hovermode='x unified'
        )
        
        return json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)
    
    def create_resource_usage_chart(self, metrics: List[Dict]) -> str:
        """Crear gráfico de uso de recursos."""
        
        timestamps = [m['timestamp'] for m in metrics]
        cpu_usage = [m['cpu_usage'] for m in metrics]
        memory_usage = [m['memory_usage'] for m in metrics]
        
        fig = go.Figure()
        
        fig.add_trace(go.Scatter(
            x=timestamps,
            y=cpu_usage,
            mode='lines',
            name='CPU Usage',
            line=dict(color='blue')
        ))
        
        fig.add_trace(go.Scatter(
            x=timestamps,
            y=memory_usage,
            mode='lines',
            name='Memory Usage',
            line=dict(color='red')
        ))
        
        fig.update_layout(
            title="Resource Usage",
            xaxis_title="Time",
            yaxis_title="Usage (%)",
            hovermode='x unified'
        )
        
        return json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)
    
    @app.route('/performance-dashboard')
    def performance_dashboard():
        """Endpoint del dashboard de performance."""
        
        charts = PerformanceDashboard().generate_performance_charts()
        
        return render_template('performance_dashboard.html', charts=charts)
    
    @app.route('/api/performance-metrics')
    def api_performance_metrics():
        """API endpoint para métricas de performance."""
        
        metrics = PerformanceMonitor().collect_metrics()
        
        return jsonify({
            'timestamp': datetime.utcnow().isoformat(),
            'metrics': metrics
        })
```

## 🔧 Herramientas de Optimización

### Profiler de Performance

```python
# performance_profiler.py
import cProfile
import pstats
import io
from functools import wraps
import time
import memory_profiler
import line_profiler

class PerformanceProfiler:
    """Profiler de performance para identificar cuellos de botella."""
    
    def __init__(self):
        self.profiles = {}
    
    def profile_function(self, func):
        """Decorator para perfilar funciones."""
        
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Profiling de tiempo
            start_time = time.time()
            
            # Profiling de memoria
            mem_before = memory_profiler.memory_usage()[0]
            
            # Ejecutar función
            result = func(*args, **kwargs)
            
            # Calcular métricas
            end_time = time.time()
            mem_after = memory_profiler.memory_usage()[0]
            
            execution_time = end_time - start_time
            memory_used = mem_after - mem_before
            
            # Guardar métricas
            self.profiles[func.__name__] = {
                'execution_time': execution_time,
                'memory_used': memory_used,
                'timestamp': time.time()
            }
            
            print(f"⏱️ {func.__name__}: {execution_time:.4f}s, {memory_used:.2f}MB")
            
            return result
        
        return wrapper
    
    def profile_with_cprofile(self, func):
        """Profiling detallado con cProfile."""
        
        @wraps(func)
        def wrapper(*args, **kwargs):
            profiler = cProfile.Profile()
            profiler.enable()
            
            result = func(*args, **kwargs)
            
            profiler.disable()
            
            # Generar reporte
            s = io.StringIO()
            ps = pstats.Stats(profiler, stream=s).sort_stats('cumulative')
            ps.print_stats(10)  # Top 10 funciones más lentas
            
            print(f"📊 Profile de {func.__name__}:")
            print(s.getvalue())
            
            return result
        
        return wrapper
    
    def analyze_bottlenecks(self):
        """Analizar cuellos de botella en el sistema."""
        
        print("🔍 Análisis de Cuellos de Botella:")
        print("=" * 50)
        
        # Ordenar por tiempo de ejecución
        sorted_profiles = sorted(
            self.profiles.items(),
            key=lambda x: x[1]['execution_time'],
            reverse=True
        )
        
        for func_name, metrics in sorted_profiles[:10]:
            print(f"🐌 {func_name}:")
            print(f"   Tiempo: {metrics['execution_time']:.4f}s")
            print(f"   Memoria: {metrics['memory_used']:.2f}MB")
            print()
    
    def generate_optimization_recommendations(self):
        """Generar recomendaciones de optimización."""
        
        recommendations = []
        
        for func_name, metrics in self.profiles.items():
            if metrics['execution_time'] > 1.0:  # > 1 segundo
                recommendations.append({
                    'function': func_name,
                    'issue': 'Slow execution time',
                    'recommendation': 'Consider caching or algorithm optimization',
                    'priority': 'high'
                })
            
            if metrics['memory_used'] > 100:  # > 100MB
                recommendations.append({
                    'function': func_name,
                    'issue': 'High memory usage',
                    'recommendation': 'Consider memory optimization or streaming',
                    'priority': 'medium'
                })
        
        return recommendations

# Ejemplo de uso
profiler = PerformanceProfiler()

@profiler.profile_function
def slow_function():
    """Función lenta para demostrar profiling."""
    time.sleep(2)
    return sum(range(1000000))

@profiler.profile_with_cprofile
def complex_function():
    """Función compleja para profiling detallado."""
    result = []
    for i in range(1000):
        result.append(i ** 2)
    return result
```

---

Esta guía de optimización de performance proporciona herramientas y técnicas avanzadas para maximizar el rendimiento de ClickUp Brain, desde optimización de base de datos hasta técnicas de AI y monitoreo en tiempo real.



