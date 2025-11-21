"""
Framework principal de sincronización
=====================================

Orquesta la sincronización entre múltiples sistemas con características avanzadas:
- Sincronización bidireccional
- Resolución de conflictos
- Circuit breaker
- Retry logic
- Caché inteligente
- Validación de datos
- Auditoría completa
"""
from typing import Dict, Any, List, Optional, Tuple, Callable
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
import logging
import json
import time
from functools import lru_cache

from .connectors import BaseConnector, SyncRecord, create_connector

logger = logging.getLogger(__name__)


class SyncDirection(Enum):
    """Dirección de sincronización"""
    SOURCE_TO_TARGET = "source_to_target"
    TARGET_TO_SOURCE = "target_to_source"
    BIDIRECTIONAL = "bidirectional"


class SyncStatus(Enum):
    """Estado de sincronización"""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    PARTIAL = "partial"
    CANCELLED = "cancelled"


@dataclass
class SyncConfig:
    """Configuración de sincronización"""
    sync_id: str
    source_connector_type: str
    source_config: Dict[str, Any]
    target_connector_type: str
    target_config: Dict[str, Any]
    direction: SyncDirection = SyncDirection.BIDIRECTIONAL
    batch_size: int = 50
    retry_attempts: int = 3
    retry_delay_seconds: int = 5
    enable_circuit_breaker: bool = True
    circuit_breaker_threshold: int = 5
    enable_caching: bool = True
    cache_ttl_seconds: int = 300
    enable_validation: bool = True
    enable_audit: bool = True
    conflict_resolution: str = "source_wins"  # source_wins, target_wins, manual, latest
    filters: Optional[Dict[str, Any]] = None
    transform_function: Optional[Callable] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class SyncResult:
    """Resultado de sincronización"""
    sync_id: str
    status: SyncStatus
    total_records: int = 0
    successful: int = 0
    failed: int = 0
    conflicted: int = 0
    skipped: int = 0
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    duration_seconds: float = 0.0
    errors: List[Dict[str, Any]] = field(default_factory=list)
    records: List[SyncRecord] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convierte resultado a diccionario"""
        return {
            "sync_id": self.sync_id,
            "status": self.status.value,
            "total_records": self.total_records,
            "successful": self.successful,
            "failed": self.failed,
            "conflicted": self.conflicted,
            "skipped": self.skipped,
            "start_time": self.start_time.isoformat() if self.start_time else None,
            "end_time": self.end_time.isoformat() if self.end_time else None,
            "duration_seconds": self.duration_seconds,
            "error_count": len(self.errors),
            "metadata": self.metadata
        }


class CircuitBreaker:
    """Circuit breaker pattern para proteger contra fallos en cascada"""
    
    def __init__(self, threshold: int = 5, timeout_seconds: int = 60):
        self.threshold = threshold
        self.timeout_seconds = timeout_seconds
        self.failure_count = 0
        self.last_failure_time: Optional[datetime] = None
        self.state = "closed"  # closed, open, half_open
    
    def record_success(self):
        """Registra éxito y resetea contador"""
        self.failure_count = 0
        self.state = "closed"
    
    def record_failure(self):
        """Registra fallo y verifica si debe abrir el circuito"""
        self.failure_count += 1
        self.last_failure_time = datetime.now()
        
        if self.failure_count >= self.threshold:
            self.state = "open"
            logger.warning(f"Circuit breaker abierto después de {self.failure_count} fallos")
    
    def can_execute(self) -> bool:
        """Verifica si se puede ejecutar"""
        if self.state == "closed":
            return True
        
        if self.state == "open":
            # Verificar si ha pasado el timeout
            if self.last_failure_time:
                elapsed = (datetime.now() - self.last_failure_time).total_seconds()
                if elapsed >= self.timeout_seconds:
                    self.state = "half_open"
                    logger.info("Circuit breaker en estado half_open, intentando")
                    return True
            return False
        
        # half_open
        return True
    
    def get_status(self) -> Dict[str, Any]:
        """Obtiene estado del circuit breaker"""
        return {
            "state": self.state,
            "failure_count": self.failure_count,
            "last_failure_time": self.last_failure_time.isoformat() if self.last_failure_time else None
        }


class SyncFramework:
    """Framework principal de sincronización"""
    
    def __init__(self, db_connection_string: Optional[str] = None):
        self.db_connection_string = db_connection_string
        self.circuit_breakers: Dict[str, CircuitBreaker] = {}
        self.cache: Dict[str, Tuple[Any, float]] = {}
        self.logger = logging.getLogger(__name__)
        
        # Crear tablas de auditoría si hay conexión a BD
        if db_connection_string:
            self._init_database()
    
    def _init_database(self):
        """Inicializa tablas de auditoría en base de datos"""
        try:
            import psycopg2
            conn = psycopg2.connect(self.db_connection_string)
            cur = conn.cursor()
            
            # Tabla de historial de sincronizaciones
            cur.execute("""
                CREATE TABLE IF NOT EXISTS sync_history (
                    id SERIAL PRIMARY KEY,
                    sync_id VARCHAR(128) NOT NULL,
                    status VARCHAR(32) NOT NULL,
                    source_type VARCHAR(64) NOT NULL,
                    target_type VARCHAR(64) NOT NULL,
                    total_records INTEGER DEFAULT 0,
                    successful INTEGER DEFAULT 0,
                    failed INTEGER DEFAULT 0,
                    conflicted INTEGER DEFAULT 0,
                    skipped INTEGER DEFAULT 0,
                    duration_seconds FLOAT,
                    errors JSONB,
                    metadata JSONB,
                    started_at TIMESTAMPTZ DEFAULT NOW(),
                    completed_at TIMESTAMPTZ,
                    created_at TIMESTAMPTZ DEFAULT NOW()
                )
            """)
            
            # Tabla de registros sincronizados
            cur.execute("""
                CREATE TABLE IF NOT EXISTS sync_records (
                    id SERIAL PRIMARY KEY,
                    sync_history_id INTEGER REFERENCES sync_history(id),
                    source_id VARCHAR(256) NOT NULL,
                    source_type VARCHAR(64) NOT NULL,
                    target_id VARCHAR(256),
                    target_type VARCHAR(64),
                    checksum VARCHAR(64),
                    status VARCHAR(32) NOT NULL,
                    error_message TEXT,
                    data JSONB,
                    metadata JSONB,
                    synced_at TIMESTAMPTZ DEFAULT NOW(),
                    created_at TIMESTAMPTZ DEFAULT NOW(),
                    UNIQUE(source_id, source_type, target_type)
                )
            """)
            
            # Índices
            cur.execute("CREATE INDEX IF NOT EXISTS idx_sync_history_sync_id ON sync_history(sync_id)")
            cur.execute("CREATE INDEX IF NOT EXISTS idx_sync_history_status ON sync_history(status)")
            cur.execute("CREATE INDEX IF NOT EXISTS idx_sync_history_started_at ON sync_history(started_at)")
            cur.execute("CREATE INDEX IF NOT EXISTS idx_sync_records_source ON sync_records(source_id, source_type)")
            cur.execute("CREATE INDEX IF NOT EXISTS idx_sync_records_target ON sync_records(target_id, target_type)")
            cur.execute("CREATE INDEX IF NOT EXISTS idx_sync_records_checksum ON sync_records(checksum)")
            
            conn.commit()
            cur.close()
            conn.close()
            self.logger.info("Base de datos de sincronización inicializada")
        except Exception as e:
            self.logger.warning(f"No se pudo inicializar base de datos: {e}")
    
    def _get_circuit_breaker(self, connector_type: str) -> CircuitBreaker:
        """Obtiene o crea circuit breaker para un conector"""
        if connector_type not in self.circuit_breakers:
            self.circuit_breakers[connector_type] = CircuitBreaker()
        return self.circuit_breakers[connector_type]
    
    def _get_from_cache(self, key: str, ttl_seconds: int = 300) -> Optional[Any]:
        """Obtiene valor del caché si no ha expirado"""
        if key not in self.cache:
            return None
        
        value, timestamp = self.cache[key]
        elapsed = time.time() - timestamp
        
        if elapsed > ttl_seconds:
            del self.cache[key]
            return None
        
        return value
    
    def _set_cache(self, key: str, value: Any):
        """Almacena valor en caché"""
        self.cache[key] = (value, time.time())
    
    def _validate_record(self, record: SyncRecord) -> Tuple[bool, Optional[str]]:
        """Valida un registro antes de sincronizar"""
        if not record.source_id:
            return False, "source_id es requerido"
        if not record.data:
            return False, "data no puede estar vacío"
        return True, None
    
    def _transform_record(
        self,
        record: SyncRecord,
        transform_function: Optional[Callable] = None
    ) -> SyncRecord:
        """Transforma un registro usando función personalizada"""
        if transform_function:
            try:
                transformed_data = transform_function(record.data)
                record.data = transformed_data
                record.checksum = None  # Recalcular checksum
            except Exception as e:
                self.logger.warning(f"Error en transformación: {e}")
        return record
    
    def _resolve_conflict(
        self,
        source_record: SyncRecord,
        target_record: SyncRecord,
        strategy: str
    ) -> SyncRecord:
        """Resuelve conflicto entre registros"""
        if strategy == "source_wins":
            return source_record
        elif strategy == "target_wins":
            return target_record
        elif strategy == "latest":
            # Usar el más reciente basado en synced_at
            if source_record.synced_at and target_record.synced_at:
                if source_record.synced_at > target_record.synced_at:
                    return source_record
                return target_record
            return source_record
        else:
            # manual - marcar como conflicto
            source_record.status = "conflicted"
            return source_record
    
    def sync(
        self,
        config: SyncConfig,
        dry_run: bool = False
    ) -> SyncResult:
        """
        Ejecuta sincronización según configuración
        
        Args:
            config: Configuración de sincronización
            dry_run: Si True, solo simula sin escribir cambios
        
        Returns:
            SyncResult con resultados de la sincronización
        """
        result = SyncResult(
            sync_id=config.sync_id,
            status=SyncStatus.IN_PROGRESS,
            start_time=datetime.now()
        )
        
        try:
            # Crear conectores
            source_connector = create_connector(
                config.source_connector_type,
                config.source_config
            )
            target_connector = create_connector(
                config.target_connector_type,
                config.target_config
            )
            
            # Health checks
            source_health = source_connector.health_check()
            target_health = target_connector.health_check()
            
            if source_health.get("status") != "healthy":
                raise ValueError(f"Source connector no saludable: {source_health}")
            if target_health.get("status") != "healthy":
                raise ValueError(f"Target connector no saludable: {target_health}")
            
            # Verificar circuit breakers
            source_cb = self._get_circuit_breaker(config.source_connector_type)
            target_cb = self._get_circuit_breaker(config.target_connector_type)
            
            if not source_cb.can_execute():
                raise ValueError(f"Circuit breaker abierto para source: {config.source_connector_type}")
            if not target_cb.can_execute():
                raise ValueError(f"Circuit breaker abierto para target: {config.target_connector_type}")
            
            # Conectar
            if not source_connector.connect():
                raise ValueError("No se pudo conectar a source")
            if not target_connector.connect():
                raise ValueError("No se pudo conectar a target")
            
            try:
                # Leer registros del source
                source_records = source_connector.read_records(
                    filters=config.filters,
                    limit=config.batch_size * 10  # Leer más para procesar en batches
                )
                
                result.total_records = len(source_records)
                
                # Procesar en batches
                batch_size = config.batch_size
                for i in range(0, len(source_records), batch_size):
                    batch = source_records[i:i + batch_size]
                    batch_result = self._sync_batch(
                        batch,
                        source_connector,
                        target_connector,
                        config,
                        dry_run
                    )
                    
                    # Actualizar contadores
                    result.successful += batch_result["successful"]
                    result.failed += batch_result["failed"]
                    result.conflicted += batch_result["conflicted"]
                    result.skipped += batch_result["skipped"]
                    result.records.extend(batch_result["records"])
                    result.errors.extend(batch_result["errors"])
                    
                    # Registrar en circuit breaker
                    if batch_result["failed"] > 0:
                        source_cb.record_failure()
                        target_cb.record_failure()
                    else:
                        source_cb.record_success()
                        target_cb.record_success()
                
                # Actualizar estado final
                if result.failed == 0:
                    result.status = SyncStatus.COMPLETED
                elif result.successful > 0:
                    result.status = SyncStatus.PARTIAL
                else:
                    result.status = SyncStatus.FAILED
                
            finally:
                source_connector.disconnect()
                target_connector.disconnect()
        
        except Exception as e:
            result.status = SyncStatus.FAILED
            result.errors.append({
                "error": str(e),
                "type": type(e).__name__,
                "timestamp": datetime.now().isoformat()
            })
            self.logger.error(f"Error en sincronización {config.sync_id}: {e}", exc_info=True)
        
        finally:
            result.end_time = datetime.now()
            if result.start_time:
                result.duration_seconds = (result.end_time - result.start_time).total_seconds()
            
            # Guardar en base de datos si está disponible
            if self.db_connection_string and config.enable_audit:
                self._save_sync_result(result, config)
        
        return result
    
    def _sync_batch(
        self,
        records: List[SyncRecord],
        source_connector: BaseConnector,
        target_connector: BaseConnector,
        config: SyncConfig,
        dry_run: bool
    ) -> Dict[str, Any]:
        """Sincroniza un batch de registros"""
        batch_result = {
            "successful": 0,
            "failed": 0,
            "conflicted": 0,
            "skipped": 0,
            "records": [],
            "errors": []
        }
        
        for record in records:
            try:
                # Validar registro
                if config.enable_validation:
                    is_valid, error_msg = self._validate_record(record)
                    if not is_valid:
                        record.status = "failed"
                        record.error_message = error_msg
                        batch_result["failed"] += 1
                        batch_result["errors"].append({
                            "record_id": record.source_id,
                            "error": error_msg
                        })
                        continue
                
                # Transformar si hay función de transformación
                record = self._transform_record(record, config.transform_function)
                
                # Verificar si ya existe en target (usando caché si está habilitado)
                cache_key = f"{record.source_id}_{record.source_type}_{config.target_connector_type}"
                existing_record = None
                
                if config.enable_caching:
                    existing_record = self._get_from_cache(cache_key, config.cache_ttl_seconds)
                
                if not existing_record:
                    # Buscar en target
                    target_records = target_connector.read_records(
                        filters={"source_id": record.source_id},
                        limit=1
                    )
                    if target_records:
                        existing_record = target_records[0]
                        if config.enable_caching:
                            self._set_cache(cache_key, existing_record)
                
                if existing_record:
                    # Verificar si hay cambios (checksum)
                    if record.checksum and existing_record.checksum:
                        if record.checksum == existing_record.checksum:
                            record.status = "skipped"
                            batch_result["skipped"] += 1
                            continue
                    
                    # Resolver conflicto
                    record = self._resolve_conflict(
                        record,
                        existing_record,
                        config.conflict_resolution
                    )
                    
                    if record.status == "conflicted":
                        batch_result["conflicted"] += 1
                        continue
                    
                    # Actualizar
                    if not dry_run:
                        updated_records = target_connector.update_records([record])
                        if updated_records[0].status == "synced":
                            batch_result["successful"] += 1
                        else:
                            batch_result["failed"] += 1
                            batch_result["errors"].append({
                                "record_id": record.source_id,
                                "error": updated_records[0].error_message
                            })
                    else:
                        batch_result["successful"] += 1
                else:
                    # Crear nuevo
                    if not dry_run:
                        created_records = target_connector.write_records([record])
                        if created_records[0].status == "synced":
                            batch_result["successful"] += 1
                            record.target_id = created_records[0].target_id
                        else:
                            batch_result["failed"] += 1
                            batch_result["errors"].append({
                                "record_id": record.source_id,
                                "error": created_records[0].error_message
                            })
                    else:
                        batch_result["successful"] += 1
                
                batch_result["records"].append(record)
                
            except Exception as e:
                record.status = "failed"
                record.error_message = str(e)
                batch_result["failed"] += 1
                batch_result["errors"].append({
                    "record_id": record.source_id,
                    "error": str(e),
                    "type": type(e).__name__
                })
                self.logger.error(f"Error sincronizando registro {record.source_id}: {e}")
        
        return batch_result
    
    def _save_sync_result(self, result: SyncResult, config: SyncConfig):
        """Guarda resultado de sincronización en base de datos"""
        try:
            import psycopg2
            from psycopg2.extras import Json
            
            conn = psycopg2.connect(self.db_connection_string)
            cur = conn.cursor()
            
            # Insertar en sync_history
            cur.execute("""
                INSERT INTO sync_history (
                    sync_id, status, source_type, target_type,
                    total_records, successful, failed, conflicted, skipped,
                    duration_seconds, errors, metadata, started_at, completed_at
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                RETURNING id
            """, (
                result.sync_id,
                result.status.value,
                config.source_connector_type,
                config.target_connector_type,
                result.total_records,
                result.successful,
                result.failed,
                result.conflicted,
                result.skipped,
                result.duration_seconds,
                Json(result.errors),
                Json(result.metadata),
                result.start_time,
                result.end_time
            ))
            
            history_id = cur.fetchone()[0]
            
            # Insertar registros sincronizados
            for record in result.records:
                cur.execute("""
                    INSERT INTO sync_records (
                        sync_history_id, source_id, source_type,
                        target_id, target_type, checksum, status,
                        error_message, data, metadata, synced_at
                    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    ON CONFLICT (source_id, source_type, target_type)
                    DO UPDATE SET
                        target_id = EXCLUDED.target_id,
                        checksum = EXCLUDED.checksum,
                        status = EXCLUDED.status,
                        error_message = EXCLUDED.error_message,
                        data = EXCLUDED.data,
                        metadata = EXCLUDED.metadata,
                        synced_at = EXCLUDED.synced_at
                """, (
                    history_id,
                    record.source_id,
                    record.source_type,
                    record.target_id,
                    record.target_type,
                    record.checksum,
                    record.status,
                    record.error_message,
                    Json(record.data),
                    Json(record.metadata),
                    record.synced_at or datetime.now()
                ))
            
            conn.commit()
            cur.close()
            conn.close()
        except Exception as e:
            self.logger.error(f"Error guardando resultado en BD: {e}")



