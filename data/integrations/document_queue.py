"""
Sistema de Colas para Procesamiento Asíncrono
=============================================

Procesamiento asíncrono de documentos usando Redis o RabbitMQ.
"""

from typing import Dict, Any, Optional, Callable
from dataclasses import dataclass
from enum import Enum
import json
import logging
from datetime import datetime
import uuid

logger = logging.getLogger(__name__)


class QueueBackend(Enum):
    """Backends de cola soportados"""
    REDIS = "redis"
    RABBITMQ = "rabbitmq"
    DATABASE = "database"


@dataclass
class ProcessingJob:
    """Trabajo de procesamiento"""
    job_id: str
    file_path: str
    filename: str
    priority: int = 5  # 1-10
    config: Dict[str, Any] = None
    callback_url: Optional[str] = None
    created_at: str = None
    
    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now().isoformat()
        if self.config is None:
            self.config = {}
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "job_id": self.job_id,
            "file_path": self.file_path,
            "filename": self.filename,
            "priority": self.priority,
            "config": self.config,
            "callback_url": self.callback_url,
            "created_at": self.created_at
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ProcessingJob":
        return cls(
            job_id=data["job_id"],
            file_path=data["file_path"],
            filename=data["filename"],
            priority=data.get("priority", 5),
            config=data.get("config", {}),
            callback_url=data.get("callback_url"),
            created_at=data.get("created_at")
        )


class BaseQueue:
    """Clase base para colas"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.logger = logging.getLogger(__name__)
    
    def enqueue(self, job: ProcessingJob) -> bool:
        """Agrega trabajo a la cola"""
        raise NotImplementedError
    
    def dequeue(self) -> Optional[ProcessingJob]:
        """Obtiene trabajo de la cola"""
        raise NotImplementedError
    
    def get_job_status(self, job_id: str) -> Optional[Dict[str, Any]]:
        """Obtiene estado de un trabajo"""
        raise NotImplementedError
    
    def update_job_status(
        self,
        job_id: str,
        status: str,
        result: Optional[Dict[str, Any]] = None
    ) -> bool:
        """Actualiza estado de un trabajo"""
        raise NotImplementedError


class RedisQueue(BaseQueue):
    """Cola usando Redis"""
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        try:
            import redis
        except ImportError:
            raise ImportError(
                "redis es requerido. Instala con: pip install redis"
            )
        
        self.redis_host = config.get("host", "localhost")
        self.redis_port = config.get("port", 6379)
        self.redis_db = config.get("db", 0)
        self.queue_name = config.get("queue_name", "document_processing")
        self.status_prefix = config.get("status_prefix", "job_status:")
        
        self.redis_client = redis.Redis(
            host=self.redis_host,
            port=self.redis_port,
            db=self.redis_db,
            decode_responses=True
        )
    
    def enqueue(self, job: ProcessingJob) -> bool:
        """Agrega trabajo a la cola Redis"""
        try:
            # Serializar trabajo
            job_data = json.dumps(job.to_dict())
            
            # Usar sorted set para prioridad
            score = -job.priority  # Negativo para orden descendente
            self.redis_client.zadd(
                self.queue_name,
                {job.job_id: score}
            )
            
            # Guardar datos del trabajo
            self.redis_client.setex(
                f"{self.queue_name}:job:{job.job_id}",
                3600,  # TTL 1 hora
                job_data
            )
            
            # Estado inicial
            self.update_job_status(job.job_id, "pending")
            
            self.logger.info(f"Trabajo encolado: {job.job_id}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error encolando trabajo: {e}")
            return False
    
    def dequeue(self) -> Optional[ProcessingJob]:
        """Obtiene trabajo de mayor prioridad"""
        try:
            # Obtener trabajo con mayor prioridad
            results = self.redis_client.zrange(
                self.queue_name,
                0,
                0,
                withscores=True
            )
            
            if not results:
                return None
            
            job_id, _ = results[0]
            
            # Obtener datos del trabajo
            job_data = self.redis_client.get(f"{self.queue_name}:job:{job_id}")
            if not job_data:
                # Limpiar de la cola si no hay datos
                self.redis_client.zrem(self.queue_name, job_id)
                return None
            
            # Remover de la cola
            self.redis_client.zrem(self.queue_name, job_id)
            
            # Parsear y retornar
            job_dict = json.loads(job_data)
            job = ProcessingJob.from_dict(job_dict)
            
            self.update_job_status(job_id, "processing")
            
            return job
            
        except Exception as e:
            self.logger.error(f"Error desencolando trabajo: {e}")
            return None
    
    def get_job_status(self, job_id: str) -> Optional[Dict[str, Any]]:
        """Obtiene estado de un trabajo"""
        try:
            status_data = self.redis_client.get(
                f"{self.status_prefix}{job_id}"
            )
            if status_data:
                return json.loads(status_data)
            return None
        except Exception as e:
            self.logger.error(f"Error obteniendo estado: {e}")
            return None
    
    def update_job_status(
        self,
        job_id: str,
        status: str,
        result: Optional[Dict[str, Any]] = None
    ) -> bool:
        """Actualiza estado de un trabajo"""
        try:
            status_data = {
                "job_id": job_id,
                "status": status,
                "updated_at": datetime.now().isoformat()
            }
            if result:
                status_data["result"] = result
            
            self.redis_client.setex(
                f"{self.status_prefix}{job_id}",
                86400,  # TTL 24 horas
                json.dumps(status_data)
            )
            return True
        except Exception as e:
            self.logger.error(f"Error actualizando estado: {e}")
            return False


class DatabaseQueue(BaseQueue):
    """Cola usando base de datos PostgreSQL"""
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        import psycopg2
        
        self.connection_string = config.get("connection_string")
        if not self.connection_string:
            raise ValueError("connection_string es requerido para DatabaseQueue")
        
        self.conn = psycopg2.connect(self.connection_string)
    
    def enqueue(self, job: ProcessingJob) -> bool:
        """Agrega trabajo usando tabla pending_documents"""
        try:
            cursor = self.conn.cursor()
            cursor.execute("""
                INSERT INTO pending_documents
                (file_path, filename, priority, source, status)
                VALUES (%s, %s, %s, %s, 'pending')
                RETURNING id
            """, (
                job.file_path,
                job.filename,
                job.priority,
                "queue"
            ))
            
            job_db_id = cursor.fetchone()[0]
            self.conn.commit()
            
            # Guardar metadata del trabajo
            cursor.execute("""
                INSERT INTO document_metadata
                (document_id, metadata_key, metadata_value)
                VALUES (%s, %s, %s)
            """, (
                str(job_db_id),
                "job_config",
                json.dumps(job.config)
            ))
            
            self.conn.commit()
            
            self.logger.info(f"Trabajo encolado en BD: {job.job_id}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error encolando trabajo: {e}")
            self.conn.rollback()
            return False
    
    def dequeue(self) -> Optional[ProcessingJob]:
        """Obtiene trabajo de la BD"""
        try:
            cursor = self.conn.cursor()
            cursor.execute("""
                UPDATE pending_documents
                SET status = 'processing'
                WHERE id = (
                    SELECT id FROM pending_documents
                    WHERE status = 'pending'
                    ORDER BY priority DESC, created_at ASC
                    LIMIT 1
                    FOR UPDATE SKIP LOCKED
                )
                RETURNING id, file_path, filename, priority
            """)
            
            result = cursor.fetchone()
            if not result:
                return None
            
            job_db_id, file_path, filename, priority = result
            
            # Obtener configuración
            cursor.execute("""
                SELECT metadata_value FROM document_metadata
                WHERE document_id = %s AND metadata_key = 'job_config'
            """, (str(job_db_id),))
            
            config_row = cursor.fetchone()
            config = json.loads(config_row[0]) if config_row else {}
            
            self.conn.commit()
            
            job = ProcessingJob(
                job_id=str(job_db_id),
                file_path=file_path,
                filename=filename,
                priority=priority,
                config=config
            )
            
            return job
            
        except Exception as e:
            self.logger.error(f"Error desencolando trabajo: {e}")
            self.conn.rollback()
            return None
    
    def get_job_status(self, job_id: str) -> Optional[Dict[str, Any]]:
        """Obtiene estado de un trabajo"""
        try:
            cursor = self.conn.cursor()
            cursor.execute("""
                SELECT status, error_message, processed_at
                FROM pending_documents
                WHERE id = %s
            """, (job_id,))
            
            result = cursor.fetchone()
            if not result:
                return None
            
            status, error_message, processed_at = result
            
            return {
                "job_id": job_id,
                "status": status,
                "error_message": error_message,
                "processed_at": processed_at.isoformat() if processed_at else None
            }
        except Exception as e:
            self.logger.error(f"Error obteniendo estado: {e}")
            return None
    
    def update_job_status(
        self,
        job_id: str,
        status: str,
        result: Optional[Dict[str, Any]] = None
    ) -> bool:
        """Actualiza estado en BD"""
        try:
            cursor = self.conn.cursor()
            cursor.execute("""
                UPDATE pending_documents
                SET status = %s,
                    error_message = %s,
                    processed_at = CASE WHEN %s = 'completed' THEN CURRENT_TIMESTAMP ELSE processed_at END
                WHERE id = %s
            """, (
                status,
                result.get("error") if result and "error" in result else None,
                status,
                job_id
            ))
            
            self.conn.commit()
            return True
        except Exception as e:
            self.logger.error(f"Error actualizando estado: {e}")
            self.conn.rollback()
            return False


def create_queue(backend: str, config: Dict[str, Any]) -> BaseQueue:
    """Factory para crear colas"""
    backend_enum = QueueBackend(backend.lower())
    
    if backend_enum == QueueBackend.REDIS:
        return RedisQueue(config)
    elif backend_enum == QueueBackend.DATABASE:
        return DatabaseQueue(config)
    else:
        raise ValueError(f"Backend de cola no soportado: {backend}")

