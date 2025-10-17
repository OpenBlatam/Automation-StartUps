"""
Motor de Procesamiento en Tiempo Real Avanzado
Sistema de procesamiento de datos en tiempo real con streaming, análisis y alertas
"""

import asyncio
import json
import logging
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Callable, AsyncGenerator
from dataclasses import dataclass
from enum import Enum
import queue
import threading
from collections import deque
import websockets
import aiohttp
import kafka
from kafka import KafkaProducer, KafkaConsumer
import redis
import sqlite3
from concurrent.futures import ThreadPoolExecutor
import time

class StreamType(Enum):
    KAFKA = "kafka"
    WEBSOCKET = "websocket"
    HTTP = "http"
    FILE = "file"
    DATABASE = "database"
    CUSTOM = "custom"

class ProcessingMode(Enum):
    BATCH = "batch"
    STREAMING = "streaming"
    MICRO_BATCH = "micro_batch"
    CONTINUOUS = "continuous"

@dataclass
class StreamConfig:
    stream_id: str
    stream_type: StreamType
    source: str
    processing_mode: ProcessingMode
    batch_size: int = 100
    window_size: int = 1000
    processing_interval: float = 1.0
    buffer_size: int = 10000
    auto_commit: bool = True

@dataclass
class ProcessingRule:
    rule_id: str
    name: str
    condition: Callable
    action: Callable
    priority: int = 1
    enabled: bool = True
    cooldown: float = 0.0

@dataclass
class AlertConfig:
    alert_id: str
    name: str
    condition: Callable
    severity: str = "medium"
    channels: List[str] = None
    cooldown: float = 300.0  # 5 minutos
    enabled: bool = True

class AdvancedRealtimeProcessingEngine:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.streams = {}
        self.processing_rules = {}
        self.alert_configs = {}
        self.data_buffers = {}
        self.metrics = {}
        self.is_running = False
        self.executor = ThreadPoolExecutor(max_workers=10)
        self.redis_client = None
        self.kafka_producer = None
        self.kafka_consumer = None
        
        # Configuración por defecto
        self.default_config = {
            "max_buffer_size": 100000,
            "processing_timeout": 30.0,
            "alert_cooldown": 300.0,
            "metrics_interval": 60.0,
            "cleanup_interval": 3600.0
        }
        
    async def initialize(self) -> None:
        """Inicializar motor de procesamiento en tiempo real"""
        try:
            # Inicializar Redis
            self.redis_client = redis.Redis(host='localhost', port=6379, db=0)
            
            # Inicializar Kafka
            self.kafka_producer = KafkaProducer(
                bootstrap_servers=['localhost:9092'],
                value_serializer=lambda x: json.dumps(x).encode('utf-8')
            )
            
            self.logger.info("Realtime processing engine initialized successfully")
            
        except Exception as e:
            self.logger.error(f"Error initializing realtime processing engine: {e}")
            raise
    
    async def create_stream(self, config: StreamConfig) -> str:
        """Crear nuevo stream de datos"""
        try:
            stream_id = config.stream_id
            
            # Crear buffer para el stream
            self.data_buffers[stream_id] = deque(maxlen=config.buffer_size)
            
            # Configurar stream según tipo
            if config.stream_type == StreamType.KAFKA:
                await self._setup_kafka_stream(config)
            elif config.stream_type == StreamType.WEBSOCKET:
                await self._setup_websocket_stream(config)
            elif config.stream_type == StreamType.HTTP:
                await self._setup_http_stream(config)
            elif config.stream_type == StreamType.FILE:
                await self._setup_file_stream(config)
            elif config.stream_type == StreamType.DATABASE:
                await self._setup_database_stream(config)
            
            # Guardar configuración
            self.streams[stream_id] = config
            
            # Inicializar métricas
            self.metrics[stream_id] = {
                "messages_processed": 0,
                "messages_per_second": 0.0,
                "processing_time": 0.0,
                "error_count": 0,
                "last_processed": None
            }
            
            self.logger.info(f"Stream {stream_id} created successfully")
            return stream_id
            
        except Exception as e:
            self.logger.error(f"Error creating stream: {e}")
            raise
    
    async def _setup_kafka_stream(self, config: StreamConfig) -> None:
        """Configurar stream de Kafka"""
        try:
            self.kafka_consumer = KafkaConsumer(
                config.source,
                bootstrap_servers=['localhost:9092'],
                value_deserializer=lambda m: json.loads(m.decode('utf-8')),
                auto_offset_reset='latest',
                enable_auto_commit=config.auto_commit
            )
            
        except Exception as e:
            self.logger.error(f"Error setting up Kafka stream: {e}")
            raise
    
    async def _setup_websocket_stream(self, config: StreamConfig) -> None:
        """Configurar stream de WebSocket"""
        try:
            # WebSocket se configurará cuando se inicie el procesamiento
            pass
            
        except Exception as e:
            self.logger.error(f"Error setting up WebSocket stream: {e}")
            raise
    
    async def _setup_http_stream(self, config: StreamConfig) -> None:
        """Configurar stream HTTP"""
        try:
            # HTTP stream se configurará cuando se inicie el procesamiento
            pass
            
        except Exception as e:
            self.logger.error(f"Error setting up HTTP stream: {e}")
            raise
    
    async def _setup_file_stream(self, config: StreamConfig) -> None:
        """Configurar stream de archivo"""
        try:
            # File stream se configurará cuando se inicie el procesamiento
            pass
            
        except Exception as e:
            self.logger.error(f"Error setting up file stream: {e}")
            raise
    
    async def _setup_database_stream(self, config: StreamConfig) -> None:
        """Configurar stream de base de datos"""
        try:
            # Database stream se configurará cuando se inicie el procesamiento
            pass
            
        except Exception as e:
            self.logger.error(f"Error setting up database stream: {e}")
            raise
    
    async def start_processing(self, stream_id: str) -> None:
        """Iniciar procesamiento de stream"""
        try:
            if stream_id not in self.streams:
                raise ValueError(f"Stream {stream_id} not found")
            
            config = self.streams[stream_id]
            
            # Iniciar procesamiento según tipo
            if config.stream_type == StreamType.KAFKA:
                await self._start_kafka_processing(stream_id)
            elif config.stream_type == StreamType.WEBSOCKET:
                await self._start_websocket_processing(stream_id)
            elif config.stream_type == StreamType.HTTP:
                await self._start_http_processing(stream_id)
            elif config.stream_type == StreamType.FILE:
                await self._start_file_processing(stream_id)
            elif config.stream_type == StreamType.DATABASE:
                await self._start_database_processing(stream_id)
            
            self.is_running = True
            self.logger.info(f"Processing started for stream {stream_id}")
            
        except Exception as e:
            self.logger.error(f"Error starting processing: {e}")
            raise
    
    async def _start_kafka_processing(self, stream_id: str) -> None:
        """Iniciar procesamiento de Kafka"""
        try:
            config = self.streams[stream_id]
            
            async def kafka_processor():
                for message in self.kafka_consumer:
                    try:
                        data = message.value
                        await self._process_message(stream_id, data)
                    except Exception as e:
                        self.logger.error(f"Error processing Kafka message: {e}")
                        self.metrics[stream_id]["error_count"] += 1
            
            # Ejecutar en hilo separado
            asyncio.create_task(kafka_processor())
            
        except Exception as e:
            self.logger.error(f"Error starting Kafka processing: {e}")
            raise
    
    async def _start_websocket_processing(self, stream_id: str) -> None:
        """Iniciar procesamiento de WebSocket"""
        try:
            config = self.streams[stream_id]
            
            async def websocket_processor():
                async with websockets.connect(config.source) as websocket:
                    async for message in websocket:
                        try:
                            data = json.loads(message)
                            await self._process_message(stream_id, data)
                        except Exception as e:
                            self.logger.error(f"Error processing WebSocket message: {e}")
                            self.metrics[stream_id]["error_count"] += 1
            
            # Ejecutar en hilo separado
            asyncio.create_task(websocket_processor())
            
        except Exception as e:
            self.logger.error(f"Error starting WebSocket processing: {e}")
            raise
    
    async def _start_http_processing(self, stream_id: str) -> None:
        """Iniciar procesamiento HTTP"""
        try:
            config = self.streams[stream_id]
            
            async def http_processor():
                async with aiohttp.ClientSession() as session:
                    while self.is_running:
                        try:
                            async with session.get(config.source) as response:
                                if response.status == 200:
                                    data = await response.json()
                                    await self._process_message(stream_id, data)
                        except Exception as e:
                            self.logger.error(f"Error processing HTTP request: {e}")
                            self.metrics[stream_id]["error_count"] += 1
                        
                        await asyncio.sleep(config.processing_interval)
            
            # Ejecutar en hilo separado
            asyncio.create_task(http_processor())
            
        except Exception as e:
            self.logger.error(f"Error starting HTTP processing: {e}")
            raise
    
    async def _start_file_processing(self, stream_id: str) -> None:
        """Iniciar procesamiento de archivo"""
        try:
            config = self.streams[stream_id]
            
            async def file_processor():
                with open(config.source, 'r') as file:
                    for line in file:
                        try:
                            data = json.loads(line.strip())
                            await self._process_message(stream_id, data)
                        except Exception as e:
                            self.logger.error(f"Error processing file line: {e}")
                            self.metrics[stream_id]["error_count"] += 1
                        
                        await asyncio.sleep(config.processing_interval)
            
            # Ejecutar en hilo separado
            asyncio.create_task(file_processor())
            
        except Exception as e:
            self.logger.error(f"Error starting file processing: {e}")
            raise
    
    async def _start_database_processing(self, stream_id: str) -> None:
        """Iniciar procesamiento de base de datos"""
        try:
            config = self.streams[stream_id]
            
            async def database_processor():
                conn = sqlite3.connect(config.source)
                cursor = conn.cursor()
                
                while self.is_running:
                    try:
                        cursor.execute("SELECT * FROM data ORDER BY timestamp DESC LIMIT ?", (config.batch_size,))
                        rows = cursor.fetchall()
                        
                        for row in rows:
                            data = dict(zip([description[0] for description in cursor.description], row))
                            await self._process_message(stream_id, data)
                        
                    except Exception as e:
                        self.logger.error(f"Error processing database: {e}")
                        self.metrics[stream_id]["error_count"] += 1
                    
                    await asyncio.sleep(config.processing_interval)
                
                conn.close()
            
            # Ejecutar en hilo separado
            asyncio.create_task(database_processor())
            
        except Exception as e:
            self.logger.error(f"Error starting database processing: {e}")
            raise
    
    async def _process_message(self, stream_id: str, data: Dict[str, Any]) -> None:
        """Procesar mensaje individual"""
        try:
            start_time = time.time()
            
            # Agregar timestamp si no existe
            if 'timestamp' not in data:
                data['timestamp'] = datetime.now().isoformat()
            
            # Agregar a buffer
            self.data_buffers[stream_id].append(data)
            
            # Aplicar reglas de procesamiento
            await self._apply_processing_rules(stream_id, data)
            
            # Verificar alertas
            await self._check_alerts(stream_id, data)
            
            # Actualizar métricas
            processing_time = time.time() - start_time
            self.metrics[stream_id]["messages_processed"] += 1
            self.metrics[stream_id]["processing_time"] = processing_time
            self.metrics[stream_id]["last_processed"] = datetime.now().isoformat()
            
        except Exception as e:
            self.logger.error(f"Error processing message: {e}")
            self.metrics[stream_id]["error_count"] += 1
    
    async def _apply_processing_rules(self, stream_id: str, data: Dict[str, Any]) -> None:
        """Aplicar reglas de procesamiento"""
        try:
            for rule_id, rule in self.processing_rules.items():
                if rule.enabled:
                    try:
                        # Verificar condición
                        if rule.condition(data):
                            # Ejecutar acción
                            await rule.action(stream_id, data)
                    except Exception as e:
                        self.logger.error(f"Error applying rule {rule_id}: {e}")
                        
        except Exception as e:
            self.logger.error(f"Error applying processing rules: {e}")
    
    async def _check_alerts(self, stream_id: str, data: Dict[str, Any]) -> None:
        """Verificar alertas"""
        try:
            for alert_id, alert in self.alert_configs.items():
                if alert.enabled:
                    try:
                        # Verificar condición de alerta
                        if alert.condition(data):
                            # Enviar alerta
                            await self._send_alert(alert_id, stream_id, data)
                    except Exception as e:
                        self.logger.error(f"Error checking alert {alert_id}: {e}")
                        
        except Exception as e:
            self.logger.error(f"Error checking alerts: {e}")
    
    async def _send_alert(self, alert_id: str, stream_id: str, data: Dict[str, Any]) -> None:
        """Enviar alerta"""
        try:
            alert = self.alert_configs[alert_id]
            
            # Verificar cooldown
            last_alert_key = f"alert_{alert_id}_last_sent"
            if self.redis_client:
                last_sent = self.redis_client.get(last_alert_key)
                if last_sent:
                    last_sent_time = datetime.fromisoformat(last_sent.decode())
                    if (datetime.now() - last_sent_time).total_seconds() < alert.cooldown:
                        return
            
            # Crear mensaje de alerta
            alert_message = {
                "alert_id": alert_id,
                "alert_name": alert.name,
                "severity": alert.severity,
                "stream_id": stream_id,
                "data": data,
                "timestamp": datetime.now().isoformat()
            }
            
            # Enviar por canales configurados
            if alert.channels:
                for channel in alert.channels:
                    await self._send_alert_to_channel(channel, alert_message)
            
            # Guardar timestamp de última alerta
            if self.redis_client:
                self.redis_client.set(last_alert_key, datetime.now().isoformat())
            
            self.logger.info(f"Alert {alert_id} sent for stream {stream_id}")
            
        except Exception as e:
            self.logger.error(f"Error sending alert: {e}")
    
    async def _send_alert_to_channel(self, channel: str, alert_message: Dict[str, Any]) -> None:
        """Enviar alerta a canal específico"""
        try:
            if channel == "kafka":
                if self.kafka_producer:
                    self.kafka_producer.send("alerts", alert_message)
            elif channel == "email":
                # Implementar envío por email
                pass
            elif channel == "slack":
                # Implementar envío a Slack
                pass
            elif channel == "webhook":
                # Implementar webhook
                pass
                
        except Exception as e:
            self.logger.error(f"Error sending alert to channel {channel}: {e}")
    
    async def add_processing_rule(self, rule: ProcessingRule) -> str:
        """Agregar regla de procesamiento"""
        try:
            self.processing_rules[rule.rule_id] = rule
            self.logger.info(f"Processing rule {rule.rule_id} added")
            return rule.rule_id
            
        except Exception as e:
            self.logger.error(f"Error adding processing rule: {e}")
            raise
    
    async def add_alert_config(self, alert: AlertConfig) -> str:
        """Agregar configuración de alerta"""
        try:
            self.alert_configs[alert.alert_id] = alert
            self.logger.info(f"Alert config {alert.alert_id} added")
            return alert.alert_id
            
        except Exception as e:
            self.logger.error(f"Error adding alert config: {e}")
            raise
    
    async def get_stream_data(self, stream_id: str, limit: int = 100) -> List[Dict[str, Any]]:
        """Obtener datos del stream"""
        try:
            if stream_id not in self.data_buffers:
                return []
            
            buffer = self.data_buffers[stream_id]
            return list(buffer)[-limit:]
            
        except Exception as e:
            self.logger.error(f"Error getting stream data: {e}")
            return []
    
    async def get_stream_metrics(self, stream_id: str) -> Dict[str, Any]:
        """Obtener métricas del stream"""
        try:
            if stream_id not in self.metrics:
                return {}
            
            metrics = self.metrics[stream_id].copy()
            
            # Calcular métricas adicionales
            if metrics["messages_processed"] > 0:
                metrics["average_processing_time"] = metrics["processing_time"] / metrics["messages_processed"]
                metrics["error_rate"] = metrics["error_count"] / metrics["messages_processed"]
            
            return metrics
            
        except Exception as e:
            self.logger.error(f"Error getting stream metrics: {e}")
            return {}
    
    async def get_all_metrics(self) -> Dict[str, Any]:
        """Obtener métricas de todos los streams"""
        try:
            all_metrics = {}
            
            for stream_id in self.streams:
                all_metrics[stream_id] = await self.get_stream_metrics(stream_id)
            
            # Métricas globales
            total_messages = sum(metrics.get("messages_processed", 0) for metrics in all_metrics.values())
            total_errors = sum(metrics.get("error_count", 0) for metrics in all_metrics.values())
            
            all_metrics["global"] = {
                "total_streams": len(self.streams),
                "total_messages_processed": total_messages,
                "total_errors": total_errors,
                "global_error_rate": total_errors / total_messages if total_messages > 0 else 0,
                "active_processing_rules": len([r for r in self.processing_rules.values() if r.enabled]),
                "active_alerts": len([a for a in self.alert_configs.values() if a.enabled])
            }
            
            return all_metrics
            
        except Exception as e:
            self.logger.error(f"Error getting all metrics: {e}")
            return {}
    
    async def stop_processing(self, stream_id: str) -> None:
        """Detener procesamiento de stream"""
        try:
            if stream_id in self.streams:
                # Marcar como detenido
                self.is_running = False
                self.logger.info(f"Processing stopped for stream {stream_id}")
            else:
                self.logger.warning(f"Stream {stream_id} not found")
                
        except Exception as e:
            self.logger.error(f"Error stopping processing: {e}")
    
    async def cleanup(self) -> None:
        """Limpiar recursos"""
        try:
            # Detener todos los streams
            self.is_running = False
            
            # Cerrar conexiones
            if self.kafka_producer:
                self.kafka_producer.close()
            
            if self.kafka_consumer:
                self.kafka_consumer.close()
            
            if self.redis_client:
                self.redis_client.close()
            
            # Cerrar executor
            self.executor.shutdown(wait=True)
            
            self.logger.info("Realtime processing engine cleaned up")
            
        except Exception as e:
            self.logger.error(f"Error during cleanup: {e}")

# Función principal para inicializar el motor
async def initialize_realtime_processing_engine() -> AdvancedRealtimeProcessingEngine:
    """Inicializar motor de procesamiento en tiempo real"""
    engine = AdvancedRealtimeProcessingEngine()
    await engine.initialize()
    
    # Configurar logging
    logging.basicConfig(level=logging.INFO)
    
    return engine

if __name__ == "__main__":
    # Ejemplo de uso
    async def main():
        engine = await initialize_realtime_processing_engine()
        
        # Crear configuración de stream
        stream_config = StreamConfig(
            stream_id="pricing_stream",
            stream_type=StreamType.HTTP,
            source="http://localhost:8000/api/prices",
            processing_mode=ProcessingMode.STREAMING,
            batch_size=10,
            processing_interval=1.0
        )
        
        # Crear stream
        stream_id = await engine.create_stream(stream_config)
        
        # Agregar regla de procesamiento
        def price_condition(data):
            return data.get("price", 0) > 100
        
        async def price_action(stream_id, data):
            print(f"High price detected: {data['price']}")
        
        processing_rule = ProcessingRule(
            rule_id="high_price_rule",
            name="High Price Detection",
            condition=price_condition,
            action=price_action
        )
        
        await engine.add_processing_rule(processing_rule)
        
        # Agregar configuración de alerta
        def alert_condition(data):
            return data.get("price", 0) > 200
        
        alert_config = AlertConfig(
            alert_id="price_alert",
            name="Price Alert",
            condition=alert_condition,
            severity="high",
            channels=["kafka", "email"]
        )
        
        await engine.add_alert_config(alert_config)
        
        # Iniciar procesamiento
        await engine.start_processing(stream_id)
        
        # Esperar un poco
        await asyncio.sleep(10)
        
        # Obtener métricas
        metrics = await engine.get_all_metrics()
        print("Stream Metrics:", json.dumps(metrics, indent=2, default=str))
        
        # Limpiar
        await engine.cleanup()
    
    asyncio.run(main())



