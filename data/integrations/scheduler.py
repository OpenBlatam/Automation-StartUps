"""
Scheduler para sincronizaciones programadas
============================================

Permite programar sincronizaciones recurrentes usando cron expressions.
"""
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
import json
import logging

from croniter import croniter

from .sync_framework import SyncFramework, SyncConfig, SyncDirection
from .incremental_sync import IncrementalSyncManager

logger = logging.getLogger(__name__)


class SyncScheduler:
    """Gestiona sincronizaciones programadas"""
    
    def __init__(self, framework: SyncFramework, db_connection_string: str):
        self.framework = framework
        self.db_connection_string = db_connection_string
        self.incremental_manager = IncrementalSyncManager(framework, db_connection_string)
        self._init_schedules_table()
    
    def _init_schedules_table(self):
        """Inicializa tabla de schedules"""
        try:
            import psycopg2
            conn = psycopg2.connect(self.db_connection_string)
            cur = conn.cursor()
            
            cur.execute("""
                CREATE TABLE IF NOT EXISTS sync_schedules (
                    id SERIAL PRIMARY KEY,
                    name VARCHAR(128) NOT NULL UNIQUE,
                    source_type VARCHAR(64) NOT NULL,
                    target_type VARCHAR(64) NOT NULL,
                    direction VARCHAR(32) NOT NULL DEFAULT 'bidirectional',
                    schedule_cron VARCHAR(64),
                    enabled BOOLEAN DEFAULT TRUE,
                    incremental BOOLEAN DEFAULT TRUE,
                    config JSONB NOT NULL,
                    last_run_at TIMESTAMPTZ,
                    next_run_at TIMESTAMPTZ,
                    created_at TIMESTAMPTZ DEFAULT NOW(),
                    updated_at TIMESTAMPTZ DEFAULT NOW()
                )
            """)
            
            conn.commit()
            cur.close()
            conn.close()
        except Exception as e:
            logger.error(f"Error inicializando tabla de schedules: {e}")
    
    def create_schedule(
        self,
        name: str,
        source_type: str,
        target_type: str,
        config: Dict[str, Any],
        schedule_cron: str,
        direction: str = "bidirectional",
        incremental: bool = True
    ) -> Dict[str, Any]:
        """
        Crea una sincronización programada.
        
        Args:
            name: Nombre único del schedule
            source_type: Tipo de conector fuente
            target_type: Tipo de conector destino
            config: Configuración de sincronización
            schedule_cron: Expresión cron (ej: "0 */6 * * *" para cada 6 horas)
            direction: Dirección de sincronización
            incremental: Si usar sincronización incremental
        """
        try:
            import psycopg2
            from psycopg2.extras import Json
            
            # Validar cron expression
            if not croniter.is_valid(schedule_cron):
                raise ValueError(f"Invalid cron expression: {schedule_cron}")
            
            # Calcular próximo run
            cron = croniter(schedule_cron, datetime.now())
            next_run = cron.get_next(datetime)
            
            conn = psycopg2.connect(self.db_connection_string)
            cur = conn.cursor()
            
            cur.execute("""
                INSERT INTO sync_schedules (
                    name, source_type, target_type, direction,
                    schedule_cron, enabled, incremental, config, next_run_at
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (name) DO UPDATE SET
                    source_type = EXCLUDED.source_type,
                    target_type = EXCLUDED.target_type,
                    direction = EXCLUDED.direction,
                    schedule_cron = EXCLUDED.schedule_cron,
                    incremental = EXCLUDED.incremental,
                    config = EXCLUDED.config,
                    next_run_at = EXCLUDED.next_run_at,
                    updated_at = NOW()
                RETURNING id
            """, (
                name, source_type, target_type, direction,
                schedule_cron, True, incremental, Json(config), next_run
            ))
            
            schedule_id = cur.fetchone()[0]
            conn.commit()
            cur.close()
            conn.close()
            
            logger.info(f"Schedule creado: {name} (ID: {schedule_id})")
            return {"id": schedule_id, "name": name, "next_run_at": next_run}
        
        except Exception as e:
            logger.error(f"Error creando schedule: {e}")
            raise
    
    def get_due_schedules(self) -> List[Dict[str, Any]]:
        """Obtiene schedules que deben ejecutarse"""
        try:
            import psycopg2
            from psycopg2.extras import RealDictCursor
            
            conn = psycopg2.connect(self.db_connection_string)
            cur = conn.cursor(cursor_factory=RealDictCursor)
            
            cur.execute("""
                SELECT * FROM sync_schedules
                WHERE enabled = TRUE
                    AND next_run_at <= NOW()
                ORDER BY next_run_at ASC
            """)
            
            schedules = [dict(row) for row in cur.fetchall()]
            
            cur.close()
            conn.close()
            
            return schedules
        
        except Exception as e:
            logger.error(f"Error obteniendo schedules: {e}")
            return []
    
    def execute_schedule(self, schedule_id: int) -> Dict[str, Any]:
        """Ejecuta un schedule"""
        try:
            import psycopg2
            from psycopg2.extras import RealDictCursor
            
            conn = psycopg2.connect(self.db_connection_string)
            cur = conn.cursor(cursor_factory=RealDictCursor)
            
            cur.execute("""
                SELECT * FROM sync_schedules WHERE id = %s AND enabled = TRUE
            """, (schedule_id,))
            
            schedule = cur.fetchone()
            if not schedule:
                return {"error": "Schedule no encontrado o deshabilitado"}
            
            schedule = dict(schedule)
            
            # Construir configuración
            config_dict = schedule['config']
            direction_map = {
                'source_to_target': SyncDirection.SOURCE_TO_TARGET,
                'target_to_source': SyncDirection.TARGET_TO_SOURCE,
                'bidirectional': SyncDirection.BIDIRECTIONAL
            }
            
            sync_config = SyncConfig(
                sync_id=f"schedule_{schedule['name']}_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                source_connector_type=schedule['source_type'],
                source_config=config_dict.get('source_config', {}),
                target_connector_type=schedule['target_type'],
                target_config=config_dict.get('target_config', {}),
                direction=direction_map.get(schedule['direction'], SyncDirection.BIDIRECTIONAL),
                batch_size=config_dict.get('batch_size', 50),
                conflict_resolution=config_dict.get('conflict_resolution', 'source_wins'),
                filters=config_dict.get('filters'),
                metadata=config_dict.get('metadata', {})
            )
            
            # Ejecutar sincronización
            if schedule['incremental']:
                sync_key = f"{schedule['source_type']}_{schedule['target_type']}_{schedule['direction']}"
                result = self.incremental_manager.sync_incremental(
                    sync_config,
                    sync_key
                )
            else:
                result = self.framework.sync(sync_config, dry_run=False)
            
            # Actualizar schedule
            cron = croniter(schedule['schedule_cron'], datetime.now())
            next_run = cron.get_next(datetime)
            
            cur.execute("""
                UPDATE sync_schedules
                SET last_run_at = NOW(),
                    next_run_at = %s,
                    updated_at = NOW()
                WHERE id = %s
            """, (next_run, schedule_id))
            
            conn.commit()
            cur.close()
            conn.close()
            
            logger.info(f"Schedule ejecutado: {schedule['name']}")
            return result.to_dict()
        
        except Exception as e:
            logger.error(f"Error ejecutando schedule: {e}")
            return {"error": str(e)}
    
    def run_scheduler(self):
        """Ejecuta scheduler (debe correr periódicamente)"""
        due_schedules = self.get_due_schedules()
        
        for schedule in due_schedules:
            try:
                logger.info(f"Ejecutando schedule: {schedule['name']}")
                result = self.execute_schedule(schedule['id'])
                logger.info(f"Schedule completado: {schedule['name']} - {result.get('status')}")
            except Exception as e:
                logger.error(f"Error ejecutando schedule {schedule['name']}: {e}")


