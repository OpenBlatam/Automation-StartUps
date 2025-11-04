"""
Framework de Integración y Sincronización de Datos
===================================================

Este módulo proporciona un framework unificado para sincronizar datos entre:
- CRM (HubSpot, Salesforce, etc.)
- ERP (QuickBooks, SAP, etc.)
- Hojas de Cálculo (Google Sheets, Excel)
- Bases de Datos

Características principales:
- Sincronización bidireccional
- Validación de datos robusta
- Manejo de errores resiliente
- Circuit breaker pattern
- Retry logic con exponential backoff
- Caché inteligente
- Métricas y monitoreo
- Auditoría completa
"""

__version__ = "1.0.0"
__all__ = [
    "IntegrationFramework",
    "SyncConfig",
    "SyncResult",
    "SyncStatus",
]



