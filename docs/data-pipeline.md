# 📊 Pipeline de Datos - ClickUp Brain

## Visión General

Esta guía detalla el pipeline de datos de ClickUp Brain, incluyendo ingesta, procesamiento, transformación y almacenamiento de datos estratégicos desde múltiples fuentes.

## 🏗️ Arquitectura del Pipeline

### Arquitectura de Datos

```yaml
data_architecture:
  ingestion_layer:
    - "Real-time streaming (Apache Kafka)"
    - "Batch processing (Apache Airflow)"
    - "API connectors (REST/GraphQL)"
    - "Database connectors (PostgreSQL, MongoDB)"
    - "File processors (CSV, JSON, Parquet)"
  
  processing_layer:
    - "Stream processing (Apache Flink)"
    - "Batch processing (Apache Spark)"
    - "Data transformation (dbt)"
    - "Data validation (Great Expectations)"
    - "Data quality monitoring"
  
  storage_layer:
    - "Data lake (S3/MinIO)"
    - "Data warehouse (BigQuery/Snowflake)"
    - "Operational database (PostgreSQL)"
    - "Cache layer (Redis)"
    - "Search engine (Elasticsearch)"
  
  serving_layer:
    - "API Gateway"
    - "GraphQL API"
    - "Real-time dashboards"
    - "ML model serving"
    - "Data export services"
```

## 🔄 Pipeline de Ingesta

### Ingesta en Tiempo Real

```python
# real_time_ingestion.py
import asyncio
import json
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from datetime import datetime
import aiokafka
import asyncpg
import redis.asyncio as redis
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
import logging

@dataclass
class DataEvent:
    """Evento de datos para el pipeline."""
    event_id: str
    event_type: str
    source: str
    timestamp: datetime
    data: Dict[str, Any]
    metadata: Dict[str, Any]

class RealTimeDataIngestion:
    """Sistema de ingesta de datos en tiempo real."""
    
    def __init__(self, kafka_config: Dict, db_config: Dict, redis_config: Dict):
        self.kafka_config = kafka_config
        self.db_config = db_config
        self.redis_config = redis_config
        
        # Configurar Kafka
        self.kafka_producer = None
        self.kafka_consumer = None
        
        # Configurar base de datos
        self.db_engine = None
        self.db_session = None
        
        # Configurar Redis
        self.redis_client = None
        
        # Configurar logging
        self.logger = logging.getLogger(__name__)
    
    async def initialize(self):
        """Inicializar componentes del sistema."""
        
        # Inicializar Kafka
        await self.initialize_kafka()
        
        # Inicializar base de datos
        await self.initialize_database()
        
        # Inicializar Redis
        await self.initialize_redis()
    
    async def initialize_kafka(self):
        """Inicializar Kafka producer y consumer."""
        
        try:
            # Crear producer
            self.kafka_producer = aiokafka.AIOKafkaProducer(
                bootstrap_servers=self.kafka_config['bootstrap_servers'],
                value_serializer=lambda v: json.dumps(v).encode('utf-8'),
                key_serializer=lambda k: k.encode('utf-8') if k else None
            )
            await self.kafka_producer.start()
            
            # Crear consumer
            self.kafka_consumer = aiokafka.AIOKafkaConsumer(
                self.kafka_config['topics'],
                bootstrap_servers=self.kafka_config['bootstrap_servers'],
                value_deserializer=lambda m: json.loads(m.decode('utf-8')),
                key_deserializer=lambda k: k.decode('utf-8') if k else None,
                group_id=self.kafka_config['group_id']
            )
            await self.kafka_consumer.start()
            
            self.logger.info("Kafka inicializado correctamente")
            
        except Exception as e:
            self.logger.error(f"Error inicializando Kafka: {e}")
            raise e
    
    async def initialize_database(self):
        """Inicializar conexión a base de datos."""
        
        try:
            # Crear engine asíncrono
            self.db_engine = create_async_engine(
                self.db_config['url'],
                echo=self.db_config.get('echo', False),
                pool_size=self.db_config.get('pool_size', 10),
                max_overflow=self.db_config.get('max_overflow', 20)
            )
            
            # Crear session factory
            self.db_session = sessionmaker(
                self.db_engine,
                class_=AsyncSession,
                expire_on_commit=False
            )
            
            self.logger.info("Base de datos inicializada correctamente")
            
        except Exception as e:
            self.logger.error(f"Error inicializando base de datos: {e}")
            raise e
    
    async def initialize_redis(self):
        """Inicializar conexión a Redis."""
        
        try:
            self.redis_client = redis.Redis(
                host=self.redis_config['host'],
                port=self.redis_config['port'],
                db=self.redis_config['db'],
                decode_responses=True
            )
            
            # Verificar conexión
            await self.redis_client.ping()
            
            self.logger.info("Redis inicializado correctamente")
            
        except Exception as e:
            self.logger.error(f"Error inicializando Redis: {e}")
            raise e
    
    async def ingest_opportunity_data(self, opportunity_data: Dict[str, Any]) -> str:
        """Ingerir datos de oportunidad estratégica."""
        
        try:
            # Crear evento de datos
            event = DataEvent(
                event_id=f"opp_{int(datetime.now().timestamp())}",
                event_type="opportunity_created",
                source="clickup_brain_api",
                timestamp=datetime.now(),
                data=opportunity_data,
                metadata={
                    'version': '1.0',
                    'schema': 'opportunity_v1'
                }
            )
            
            # Enviar a Kafka
            await self.send_to_kafka(event)
            
            # Almacenar en cache
            await self.cache_opportunity_data(event)
            
            # Almacenar en base de datos
            await self.store_opportunity_data(event)
            
            self.logger.info(f"Oportunidad {event.event_id} ingerida correctamente")
            
            return event.event_id
            
        except Exception as e:
            self.logger.error(f"Error ingiriendo datos de oportunidad: {e}")
            raise e
    
    async def ingest_market_data(self, market_data: Dict[str, Any]) -> str:
        """Ingerir datos de mercado."""
        
        try:
            # Crear evento de datos
            event = DataEvent(
                event_id=f"market_{int(datetime.now().timestamp())}",
                event_type="market_data_updated",
                source="market_data_provider",
                timestamp=datetime.now(),
                data=market_data,
                metadata={
                    'version': '1.0',
                    'schema': 'market_data_v1'
                }
            )
            
            # Enviar a Kafka
            await self.send_to_kafka(event)
            
            # Almacenar en cache
            await self.cache_market_data(event)
            
            # Almacenar en base de datos
            await self.store_market_data(event)
            
            self.logger.info(f"Datos de mercado {event.event_id} ingeridos correctamente")
            
            return event.event_id
            
        except Exception as e:
            self.logger.error(f"Error ingiriendo datos de mercado: {e}")
            raise e
    
    async def ingest_user_activity(self, user_activity: Dict[str, Any]) -> str:
        """Ingerir datos de actividad de usuario."""
        
        try:
            # Crear evento de datos
            event = DataEvent(
                event_id=f"activity_{int(datetime.now().timestamp())}",
                event_type="user_activity",
                source="clickup_brain_ui",
                timestamp=datetime.now(),
                data=user_activity,
                metadata={
                    'version': '1.0',
                    'schema': 'user_activity_v1'
                }
            )
            
            # Enviar a Kafka
            await self.send_to_kafka(event)
            
            # Almacenar en cache
            await self.cache_user_activity(event)
            
            # Almacenar en base de datos
            await self.store_user_activity(event)
            
            self.logger.info(f"Actividad de usuario {event.event_id} ingerida correctamente")
            
            return event.event_id
            
        except Exception as e:
            self.logger.error(f"Error ingiriendo actividad de usuario: {e}")
            raise e
    
    async def send_to_kafka(self, event: DataEvent):
        """Enviar evento a Kafka."""
        
        try:
            # Preparar mensaje
            message = {
                'event_id': event.event_id,
                'event_type': event.event_type,
                'source': event.source,
                'timestamp': event.timestamp.isoformat(),
                'data': event.data,
                'metadata': event.metadata
            }
            
            # Enviar mensaje
            await self.kafka_producer.send(
                topic=f"clickup_brain_{event.event_type}",
                key=event.event_id,
                value=message
            )
            
            self.logger.debug(f"Evento {event.event_id} enviado a Kafka")
            
        except Exception as e:
            self.logger.error(f"Error enviando evento a Kafka: {e}")
            raise e
    
    async def cache_opportunity_data(self, event: DataEvent):
        """Almacenar datos de oportunidad en cache."""
        
        try:
            # Almacenar en Redis con TTL
            cache_key = f"opportunity:{event.event_id}"
            await self.redis_client.setex(
                cache_key,
                3600,  # TTL de 1 hora
                json.dumps(event.data)
            )
            
            # Almacenar en índice de búsqueda
            search_key = f"opportunity_search:{event.data.get('market_segment', 'unknown')}"
            await self.redis_client.sadd(search_key, event.event_id)
            
            self.logger.debug(f"Datos de oportunidad {event.event_id} almacenados en cache")
            
        except Exception as e:
            self.logger.error(f"Error almacenando datos en cache: {e}")
            raise e
    
    async def cache_market_data(self, event: DataEvent):
        """Almacenar datos de mercado en cache."""
        
        try:
            # Almacenar en Redis con TTL
            cache_key = f"market_data:{event.event_id}"
            await self.redis_client.setex(
                cache_key,
                1800,  # TTL de 30 minutos
                json.dumps(event.data)
            )
            
            # Almacenar en índice de búsqueda
            search_key = f"market_data_search:{event.data.get('market_segment', 'unknown')}"
            await self.redis_client.sadd(search_key, event.event_id)
            
            self.logger.debug(f"Datos de mercado {event.event_id} almacenados en cache")
            
        except Exception as e:
            self.logger.error(f"Error almacenando datos de mercado en cache: {e}")
            raise e
    
    async def cache_user_activity(self, event: DataEvent):
        """Almacenar actividad de usuario en cache."""
        
        try:
            # Almacenar en Redis con TTL
            cache_key = f"user_activity:{event.event_id}"
            await self.redis_client.setex(
                cache_key,
                7200,  # TTL de 2 horas
                json.dumps(event.data)
            )
            
            # Almacenar en índice de búsqueda
            search_key = f"user_activity_search:{event.data.get('user_id', 'unknown')}"
            await self.redis_client.sadd(search_key, event.event_id)
            
            self.logger.debug(f"Actividad de usuario {event.event_id} almacenada en cache")
            
        except Exception as e:
            self.logger.error(f"Error almacenando actividad de usuario en cache: {e}")
            raise e
    
    async def store_opportunity_data(self, event: DataEvent):
        """Almacenar datos de oportunidad en base de datos."""
        
        try:
            async with self.db_session() as session:
                # Crear registro de oportunidad
                opportunity = Opportunity(
                    id=event.event_id,
                    title=event.data.get('title'),
                    market_segment=event.data.get('market_segment'),
                    estimated_value=event.data.get('estimated_value'),
                    success_probability=event.data.get('success_probability'),
                    priority=event.data.get('priority'),
                    status=event.data.get('status'),
                    created_at=event.timestamp,
                    updated_at=event.timestamp
                )
                
                session.add(opportunity)
                await session.commit()
                
                self.logger.debug(f"Oportunidad {event.event_id} almacenada en base de datos")
                
        except Exception as e:
            self.logger.error(f"Error almacenando oportunidad en base de datos: {e}")
            raise e
    
    async def store_market_data(self, event: DataEvent):
        """Almacenar datos de mercado en base de datos."""
        
        try:
            async with self.db_session() as session:
                # Crear registro de datos de mercado
                market_data = MarketData(
                    id=event.event_id,
                    market_segment=event.data.get('market_segment'),
                    market_size=event.data.get('market_size'),
                    growth_rate=event.data.get('growth_rate'),
                    competition_level=event.data.get('competition_level'),
                    created_at=event.timestamp,
                    updated_at=event.timestamp
                )
                
                session.add(market_data)
                await session.commit()
                
                self.logger.debug(f"Datos de mercado {event.event_id} almacenados en base de datos")
                
        except Exception as e:
            self.logger.error(f"Error almacenando datos de mercado en base de datos: {e}")
            raise e
    
    async def store_user_activity(self, event: DataEvent):
        """Almacenar actividad de usuario en base de datos."""
        
        try:
            async with self.db_session() as session:
                # Crear registro de actividad de usuario
                user_activity = UserActivity(
                    id=event.event_id,
                    user_id=event.data.get('user_id'),
                    activity_type=event.data.get('activity_type'),
                    resource_id=event.data.get('resource_id'),
                    resource_type=event.data.get('resource_type'),
                    created_at=event.timestamp
                )
                
                session.add(user_activity)
                await session.commit()
                
                self.logger.debug(f"Actividad de usuario {event.event_id} almacenada en base de datos")
                
        except Exception as e:
            self.logger.error(f"Error almacenando actividad de usuario en base de datos: {e}")
            raise e
    
    async def start_consumer(self):
        """Iniciar consumer de Kafka para procesar eventos."""
        
        try:
            async for message in self.kafka_consumer:
                # Procesar mensaje
                await self.process_kafka_message(message)
                
        except Exception as e:
            self.logger.error(f"Error en consumer de Kafka: {e}")
            raise e
    
    async def process_kafka_message(self, message):
        """Procesar mensaje de Kafka."""
        
        try:
            # Extraer datos del mensaje
            event_data = message.value
            
            # Procesar según tipo de evento
            if event_data['event_type'] == 'opportunity_created':
                await self.process_opportunity_event(event_data)
            elif event_data['event_type'] == 'market_data_updated':
                await self.process_market_data_event(event_data)
            elif event_data['event_type'] == 'user_activity':
                await self.process_user_activity_event(event_data)
            
            self.logger.debug(f"Mensaje {event_data['event_id']} procesado correctamente")
            
        except Exception as e:
            self.logger.error(f"Error procesando mensaje de Kafka: {e}")
            raise e
    
    async def process_opportunity_event(self, event_data: Dict[str, Any]):
        """Procesar evento de oportunidad."""
        
        try:
            # Actualizar métricas
            await self.update_opportunity_metrics(event_data)
            
            # Notificar a usuarios relevantes
            await self.notify_relevant_users(event_data)
            
            # Actualizar cache
            await self.update_opportunity_cache(event_data)
            
        except Exception as e:
            self.logger.error(f"Error procesando evento de oportunidad: {e}")
            raise e
    
    async def process_market_data_event(self, event_data: Dict[str, Any]):
        """Procesar evento de datos de mercado."""
        
        try:
            # Actualizar métricas de mercado
            await self.update_market_metrics(event_data)
            
            # Recalcular predicciones
            await self.recalculate_predictions(event_data)
            
            # Actualizar cache
            await self.update_market_cache(event_data)
            
        except Exception as e:
            self.logger.error(f"Error procesando evento de datos de mercado: {e}")
            raise e
    
    async def process_user_activity_event(self, event_data: Dict[str, Any]):
        """Procesar evento de actividad de usuario."""
        
        try:
            # Actualizar métricas de usuario
            await self.update_user_metrics(event_data)
            
            # Actualizar recomendaciones
            await self.update_user_recommendations(event_data)
            
            # Actualizar cache
            await self.update_user_cache(event_data)
            
        except Exception as e:
            self.logger.error(f"Error procesando evento de actividad de usuario: {e}")
            raise e
    
    async def cleanup(self):
        """Limpiar recursos."""
        
        try:
            # Cerrar Kafka
            if self.kafka_producer:
                await self.kafka_producer.stop()
            if self.kafka_consumer:
                await self.kafka_consumer.stop()
            
            # Cerrar base de datos
            if self.db_engine:
                await self.db_engine.dispose()
            
            # Cerrar Redis
            if self.redis_client:
                await self.redis_client.close()
            
            self.logger.info("Recursos limpiados correctamente")
            
        except Exception as e:
            self.logger.error(f"Error limpiando recursos: {e}")
            raise e
```

### Pipeline de Procesamiento por Lotes

```python
# batch_processing.py
import pandas as pd
import numpy as np
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
import asyncio
import aiofiles
import json
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
import logging
from dataclasses import dataclass

@dataclass
class BatchJob:
    """Trabajo de procesamiento por lotes."""
    job_id: str
    job_type: str
    status: str
    created_at: datetime
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    error_message: Optional[str] = None
    metadata: Dict[str, Any] = None

class BatchDataProcessing:
    """Sistema de procesamiento de datos por lotes."""
    
    def __init__(self, db_config: Dict, storage_config: Dict):
        self.db_config = db_config
        self.storage_config = storage_config
        
        # Configurar base de datos
        self.db_engine = create_engine(db_config['url'])
        self.db_session = sessionmaker(bind=self.db_engine)
        
        # Configurar logging
        self.logger = logging.getLogger(__name__)
        
        # Configurar trabajos
        self.batch_jobs = {}
    
    def create_batch_job(self, job_type: str, metadata: Dict[str, Any] = None) -> str:
        """Crear nuevo trabajo de procesamiento por lotes."""
        
        job_id = f"batch_{job_type}_{int(datetime.now().timestamp())}"
        
        job = BatchJob(
            job_id=job_id,
            job_type=job_type,
            status='created',
            created_at=datetime.now(),
            metadata=metadata or {}
        )
        
        self.batch_jobs[job_id] = job
        
        self.logger.info(f"Trabajo de procesamiento por lotes {job_id} creado")
        
        return job_id
    
    async def process_opportunity_analytics(self, job_id: str, date_range: Dict[str, str]) -> Dict[str, Any]:
        """Procesar análisis de oportunidades por lotes."""
        
        try:
            job = self.batch_jobs[job_id]
            job.status = 'running'
            job.started_at = datetime.now()
            
            # Obtener datos de oportunidades
            opportunities_data = await self.get_opportunities_data(date_range)
            
            # Procesar análisis
            analytics_results = await self.process_opportunity_analytics_data(opportunities_data)
            
            # Almacenar resultados
            await self.store_analytics_results(job_id, analytics_results)
            
            # Actualizar estado del trabajo
            job.status = 'completed'
            job.completed_at = datetime.now()
            
            self.logger.info(f"Análisis de oportunidades {job_id} completado")
            
            return analytics_results
            
        except Exception as e:
            job.status = 'failed'
            job.error_message = str(e)
            self.logger.error(f"Error procesando análisis de oportunidades {job_id}: {e}")
            raise e
    
    async def process_market_trends(self, job_id: str, date_range: Dict[str, str]) -> Dict[str, Any]:
        """Procesar tendencias de mercado por lotes."""
        
        try:
            job = self.batch_jobs[job_id]
            job.status = 'running'
            job.started_at = datetime.now()
            
            # Obtener datos de mercado
            market_data = await self.get_market_data(date_range)
            
            # Procesar tendencias
            trends_results = await self.process_market_trends_data(market_data)
            
            # Almacenar resultados
            await self.store_trends_results(job_id, trends_results)
            
            # Actualizar estado del trabajo
            job.status = 'completed'
            job.completed_at = datetime.now()
            
            self.logger.info(f"Análisis de tendencias de mercado {job_id} completado")
            
            return trends_results
            
        except Exception as e:
            job.status = 'failed'
            job.error_message = str(e)
            self.logger.error(f"Error procesando tendencias de mercado {job_id}: {e}")
            raise e
    
    async def process_user_behavior_analytics(self, job_id: str, date_range: Dict[str, str]) -> Dict[str, Any]:
        """Procesar análisis de comportamiento de usuario por lotes."""
        
        try:
            job = self.batch_jobs[job_id]
            job.status = 'running'
            job.started_at = datetime.now()
            
            # Obtener datos de actividad de usuario
            user_activity_data = await self.get_user_activity_data(date_range)
            
            # Procesar análisis de comportamiento
            behavior_results = await self.process_user_behavior_data(user_activity_data)
            
            # Almacenar resultados
            await self.store_behavior_results(job_id, behavior_results)
            
            # Actualizar estado del trabajo
            job.status = 'completed'
            job.completed_at = datetime.now()
            
            self.logger.info(f"Análisis de comportamiento de usuario {job_id} completado")
            
            return behavior_results
            
        except Exception as e:
            job.status = 'failed'
            job.error_message = str(e)
            self.logger.error(f"Error procesando análisis de comportamiento de usuario {job_id}: {e}")
            raise e
    
    async def get_opportunities_data(self, date_range: Dict[str, str]) -> pd.DataFrame:
        """Obtener datos de oportunidades para análisis."""
        
        try:
            query = text("""
                SELECT 
                    id, title, market_segment, estimated_value,
                    success_probability, priority, status,
                    created_at, updated_at
                FROM opportunities
                WHERE created_at BETWEEN :start_date AND :end_date
            """)
            
            with self.db_session() as session:
                result = session.execute(query, {
                    'start_date': date_range['start_date'],
                    'end_date': date_range['end_date']
                })
                
                data = result.fetchall()
                
                # Convertir a DataFrame
                df = pd.DataFrame(data, columns=[
                    'id', 'title', 'market_segment', 'estimated_value',
                    'success_probability', 'priority', 'status',
                    'created_at', 'updated_at'
                ])
                
                return df
                
        except Exception as e:
            self.logger.error(f"Error obteniendo datos de oportunidades: {e}")
            raise e
    
    async def get_market_data(self, date_range: Dict[str, str]) -> pd.DataFrame:
        """Obtener datos de mercado para análisis."""
        
        try:
            query = text("""
                SELECT 
                    id, market_segment, market_size, growth_rate,
                    competition_level, created_at, updated_at
                FROM market_data
                WHERE created_at BETWEEN :start_date AND :end_date
            """)
            
            with self.db_session() as session:
                result = session.execute(query, {
                    'start_date': date_range['start_date'],
                    'end_date': date_range['end_date']
                })
                
                data = result.fetchall()
                
                # Convertir a DataFrame
                df = pd.DataFrame(data, columns=[
                    'id', 'market_segment', 'market_size', 'growth_rate',
                    'competition_level', 'created_at', 'updated_at'
                ])
                
                return df
                
        except Exception as e:
            self.logger.error(f"Error obteniendo datos de mercado: {e}")
            raise e
    
    async def get_user_activity_data(self, date_range: Dict[str, str]) -> pd.DataFrame:
        """Obtener datos de actividad de usuario para análisis."""
        
        try:
            query = text("""
                SELECT 
                    id, user_id, activity_type, resource_id,
                    resource_type, created_at
                FROM user_activities
                WHERE created_at BETWEEN :start_date AND :end_date
            """)
            
            with self.db_session() as session:
                result = session.execute(query, {
                    'start_date': date_range['start_date'],
                    'end_date': date_range['end_date']
                })
                
                data = result.fetchall()
                
                # Convertir a DataFrame
                df = pd.DataFrame(data, columns=[
                    'id', 'user_id', 'activity_type', 'resource_id',
                    'resource_type', 'created_at'
                ])
                
                return df
                
        except Exception as e:
            self.logger.error(f"Error obteniendo datos de actividad de usuario: {e}")
            raise e
    
    async def process_opportunity_analytics_data(self, data: pd.DataFrame) -> Dict[str, Any]:
        """Procesar datos de análisis de oportunidades."""
        
        try:
            # Análisis básico
            total_opportunities = len(data)
            total_value = data['estimated_value'].sum()
            avg_success_probability = data['success_probability'].mean()
            
            # Análisis por segmento de mercado
            segment_analysis = data.groupby('market_segment').agg({
                'estimated_value': ['sum', 'mean', 'count'],
                'success_probability': 'mean'
            }).round(2)
            
            # Análisis por prioridad
            priority_analysis = data.groupby('priority').agg({
                'estimated_value': ['sum', 'mean', 'count'],
                'success_probability': 'mean'
            }).round(2)
            
            # Análisis temporal
            data['created_date'] = pd.to_datetime(data['created_at']).dt.date
            temporal_analysis = data.groupby('created_date').agg({
                'estimated_value': 'sum',
                'success_probability': 'mean'
            }).round(2)
            
            return {
                'total_opportunities': total_opportunities,
                'total_value': total_value,
                'avg_success_probability': avg_success_probability,
                'segment_analysis': segment_analysis.to_dict(),
                'priority_analysis': priority_analysis.to_dict(),
                'temporal_analysis': temporal_analysis.to_dict()
            }
            
        except Exception as e:
            self.logger.error(f"Error procesando análisis de oportunidades: {e}")
            raise e
    
    async def process_market_trends_data(self, data: pd.DataFrame) -> Dict[str, Any]:
        """Procesar datos de tendencias de mercado."""
        
        try:
            # Análisis básico
            total_market_data = len(data)
            avg_market_size = data['market_size'].mean()
            avg_growth_rate = data['growth_rate'].mean()
            avg_competition_level = data['competition_level'].mean()
            
            # Análisis por segmento de mercado
            segment_analysis = data.groupby('market_segment').agg({
                'market_size': ['mean', 'std'],
                'growth_rate': ['mean', 'std'],
                'competition_level': ['mean', 'std']
            }).round(2)
            
            # Análisis temporal
            data['created_date'] = pd.to_datetime(data['created_at']).dt.date
            temporal_analysis = data.groupby('created_date').agg({
                'market_size': 'mean',
                'growth_rate': 'mean',
                'competition_level': 'mean'
            }).round(2)
            
            # Identificar tendencias
            trends = self.identify_market_trends(data)
            
            return {
                'total_market_data': total_market_data,
                'avg_market_size': avg_market_size,
                'avg_growth_rate': avg_growth_rate,
                'avg_competition_level': avg_competition_level,
                'segment_analysis': segment_analysis.to_dict(),
                'temporal_analysis': temporal_analysis.to_dict(),
                'trends': trends
            }
            
        except Exception as e:
            self.logger.error(f"Error procesando tendencias de mercado: {e}")
            raise e
    
    async def process_user_behavior_data(self, data: pd.DataFrame) -> Dict[str, Any]:
        """Procesar datos de comportamiento de usuario."""
        
        try:
            # Análisis básico
            total_activities = len(data)
            unique_users = data['user_id'].nunique()
            avg_activities_per_user = total_activities / unique_users
            
            # Análisis por tipo de actividad
            activity_analysis = data.groupby('activity_type').agg({
                'id': 'count',
                'user_id': 'nunique'
            }).round(2)
            
            # Análisis por tipo de recurso
            resource_analysis = data.groupby('resource_type').agg({
                'id': 'count',
                'user_id': 'nunique'
            }).round(2)
            
            # Análisis temporal
            data['created_date'] = pd.to_datetime(data['created_at']).dt.date
            temporal_analysis = data.groupby('created_date').agg({
                'id': 'count',
                'user_id': 'nunique'
            }).round(2)
            
            # Identificar patrones de comportamiento
            behavior_patterns = self.identify_behavior_patterns(data)
            
            return {
                'total_activities': total_activities,
                'unique_users': unique_users,
                'avg_activities_per_user': avg_activities_per_user,
                'activity_analysis': activity_analysis.to_dict(),
                'resource_analysis': resource_analysis.to_dict(),
                'temporal_analysis': temporal_analysis.to_dict(),
                'behavior_patterns': behavior_patterns
            }
            
        except Exception as e:
            self.logger.error(f"Error procesando comportamiento de usuario: {e}")
            raise e
    
    def identify_market_trends(self, data: pd.DataFrame) -> List[Dict[str, Any]]:
        """Identificar tendencias en datos de mercado."""
        
        trends = []
        
        try:
            # Tendencia de crecimiento
            if 'growth_rate' in data.columns:
                avg_growth = data['growth_rate'].mean()
                if avg_growth > 0.1:
                    trends.append({
                        'type': 'growth',
                        'description': 'Mercado en crecimiento',
                        'value': avg_growth,
                        'direction': 'positive'
                    })
                elif avg_growth < -0.1:
                    trends.append({
                        'type': 'decline',
                        'description': 'Mercado en declive',
                        'value': avg_growth,
                        'direction': 'negative'
                    })
            
            # Tendencia de competencia
            if 'competition_level' in data.columns:
                avg_competition = data['competition_level'].mean()
                if avg_competition > 0.7:
                    trends.append({
                        'type': 'high_competition',
                        'description': 'Alta competencia en el mercado',
                        'value': avg_competition,
                        'direction': 'neutral'
                    })
            
            return trends
            
        except Exception as e:
            self.logger.error(f"Error identificando tendencias de mercado: {e}")
            return []
    
    def identify_behavior_patterns(self, data: pd.DataFrame) -> List[Dict[str, Any]]:
        """Identificar patrones de comportamiento de usuario."""
        
        patterns = []
        
        try:
            # Patrón de actividad por hora
            data['hour'] = pd.to_datetime(data['created_at']).dt.hour
            hourly_activity = data.groupby('hour')['id'].count()
            
            peak_hour = hourly_activity.idxmax()
            patterns.append({
                'type': 'peak_activity_hour',
                'description': f'Hora pico de actividad: {peak_hour}:00',
                'value': peak_hour,
                'direction': 'neutral'
            })
            
            # Patrón de actividad por día de la semana
            data['day_of_week'] = pd.to_datetime(data['created_at']).dt.day_name()
            daily_activity = data.groupby('day_of_week')['id'].count()
            
            peak_day = daily_activity.idxmax()
            patterns.append({
                'type': 'peak_activity_day',
                'description': f'Día pico de actividad: {peak_day}',
                'value': peak_day,
                'direction': 'neutral'
            })
            
            return patterns
            
        except Exception as e:
            self.logger.error(f"Error identificando patrones de comportamiento: {e}")
            return []
    
    async def store_analytics_results(self, job_id: str, results: Dict[str, Any]):
        """Almacenar resultados de análisis."""
        
        try:
            # Almacenar en archivo JSON
            file_path = f"{self.storage_config['analytics_path']}/opportunity_analytics_{job_id}.json"
            
            async with aiofiles.open(file_path, 'w') as f:
                await f.write(json.dumps(results, indent=2, default=str))
            
            self.logger.info(f"Resultados de análisis {job_id} almacenados en {file_path}")
            
        except Exception as e:
            self.logger.error(f"Error almacenando resultados de análisis: {e}")
            raise e
    
    async def store_trends_results(self, job_id: str, results: Dict[str, Any]):
        """Almacenar resultados de tendencias."""
        
        try:
            # Almacenar en archivo JSON
            file_path = f"{self.storage_config['trends_path']}/market_trends_{job_id}.json"
            
            async with aiofiles.open(file_path, 'w') as f:
                await f.write(json.dumps(results, indent=2, default=str))
            
            self.logger.info(f"Resultados de tendencias {job_id} almacenados en {file_path}")
            
        except Exception as e:
            self.logger.error(f"Error almacenando resultados de tendencias: {e}")
            raise e
    
    async def store_behavior_results(self, job_id: str, results: Dict[str, Any]):
        """Almacenar resultados de comportamiento."""
        
        try:
            # Almacenar en archivo JSON
            file_path = f"{self.storage_config['behavior_path']}/user_behavior_{job_id}.json"
            
            async with aiofiles.open(file_path, 'w') as f:
                await f.write(json.dumps(results, indent=2, default=str))
            
            self.logger.info(f"Resultados de comportamiento {job_id} almacenados en {file_path}")
            
        except Exception as e:
            self.logger.error(f"Error almacenando resultados de comportamiento: {e}")
            raise e
    
    def get_job_status(self, job_id: str) -> Dict[str, Any]:
        """Obtener estado de trabajo de procesamiento por lotes."""
        
        if job_id not in self.batch_jobs:
            raise ValueError(f"Trabajo {job_id} no encontrado")
        
        job = self.batch_jobs[job_id]
        
        return {
            'job_id': job.job_id,
            'job_type': job.job_type,
            'status': job.status,
            'created_at': job.created_at.isoformat(),
            'started_at': job.started_at.isoformat() if job.started_at else None,
            'completed_at': job.completed_at.isoformat() if job.completed_at else None,
            'error_message': job.error_message,
            'metadata': job.metadata
        }
    
    def list_batch_jobs(self) -> List[Dict[str, Any]]:
        """Listar trabajos de procesamiento por lotes."""
        
        return [
            {
                'job_id': job.job_id,
                'job_type': job.job_type,
                'status': job.status,
                'created_at': job.created_at.isoformat(),
                'started_at': job.started_at.isoformat() if job.started_at else None,
                'completed_at': job.completed_at.isoformat() if job.completed_at else None,
                'error_message': job.error_message
            }
            for job in self.batch_jobs.values()
        ]
```

---

Esta guía del pipeline de datos proporciona un framework completo para implementar sistemas de ingesta en tiempo real y procesamiento por lotes en ClickUp Brain, asegurando un manejo eficiente y escalable de datos estratégicos.


