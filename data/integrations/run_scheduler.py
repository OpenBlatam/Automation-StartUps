#!/usr/bin/env python3
"""
Script para ejecutar scheduler de sincronizaciones
===================================================

Ejecuta sincronizaciones programadas periódicamente.
"""
import os
import sys
import time
import logging
from datetime import datetime

# Agregar path
sys.path.insert(0, os.path.dirname(__file__))

from sync_framework import SyncFramework
from scheduler import SyncScheduler

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def main():
    """Función principal"""
    db_connection_string = os.getenv(
        "SYNC_DB_CONNECTION_STRING",
        "postgresql://localhost/sync"
    )
    
    if not db_connection_string:
        logger.error("SYNC_DB_CONNECTION_STRING no configurado")
        sys.exit(1)
    
    # Crear framework y scheduler
    framework = SyncFramework(db_connection_string=db_connection_string)
    scheduler = SyncScheduler(framework, db_connection_string)
    
    logger.info("Scheduler iniciado")
    
    # Loop principal
    check_interval = int(os.getenv("SCHEDULER_CHECK_INTERVAL", "60"))  # Segundos
    
    try:
        while True:
            logger.debug("Verificando schedules...")
            scheduler.run_scheduler()
            time.sleep(check_interval)
    
    except KeyboardInterrupt:
        logger.info("Scheduler detenido")
    except Exception as e:
        logger.error(f"Error en scheduler: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()


