#!/usr/bin/env python3
"""
Script para ejecutar servidor de webhooks
==========================================

Inicia servidor Flask para recibir webhooks de sistemas externos.
"""
import os
import sys
import logging

# Agregar path
sys.path.insert(0, os.path.dirname(__file__))

from sync_framework import SyncFramework
from webhooks import create_webhook_server

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
    
    # Crear framework y servidor de webhooks
    framework = SyncFramework(db_connection_string=db_connection_string)
    webhook_server = create_webhook_server(framework)
    
    host = os.getenv("WEBHOOK_HOST", "0.0.0.0")
    port = int(os.getenv("WEBHOOK_PORT", "5000"))
    debug = os.getenv("WEBHOOK_DEBUG", "false").lower() == "true"
    
    logger.info(f"Iniciando servidor de webhooks en {host}:{port}")
    logger.info(f"Endpoints disponibles:")
    logger.info(f"  - POST /webhook/hubspot")
    logger.info(f"  - POST /webhook/quickbooks")
    logger.info(f"  - POST /webhook/generic")
    logger.info(f"  - GET /health")
    
    webhook_server.run(host=host, port=port, debug=debug)


if __name__ == "__main__":
    main()


