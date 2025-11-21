# 🔌 Integrations DAGs

DAGs relacionados con integraciones externas: Gmail, HubSpot, CRM y sistemas de aprobación.

## Estructura

### 📧 **gmail/** - Procesamiento de Gmail
- **Procesador principal**: `gmail_processor.py`
- **Clasificación HubSpot**: `gmail_classify_hubspot.py`
- **Backup**: `gmail_processor.py.backup`
- **Documentación**: 
  - `GMAIL_ADVANCED_FEATURES.md`
  - `GMAIL_IMPROVEMENTS.md`
  - `INTEGRATION_GMAIL.md`
  - `README_GMAIL_PROCESSOR.md`

### 🎯 **hubspot/** - Integraciones HubSpot
- **Actualización de contactos**: `hubspot_update_contact.py`
- **Actualización de estado de interés**: `hubspot_update_estado_interes.py`
- **Actualización por lotes**: `hubspot_batch_update.py`
- **Sincronización con QuickBooks**: `hubspot_quickbooks_sync.py`
- **Sincronización de leads**: `leads_sync_hubspot.py`

### 🔄 **crm/** - Sincronización CRM
- Archivos de sincronización con sistemas CRM

### ✅ **approvals/** - Sistema de Aprobaciones
- **Analytics**: `approval_analytics.py`
- **Limpieza**: `approval_cleanup.py`, `approval_cleanup_simplified_example.py`
- **Exportación**: `approval_export.py`
- **Chequeo de salud**: `approval_health_check.py`
- **Monitoreo**: `approval_monitoring.py`
- **Recordatorios**: `approval_reminders.py`
- **Reportes**: `approval_reports.py`
- **Documentación**: 
  - `APPROVAL_CLEANUP_ADVANCED_IMPROVEMENTS.md`
  - `approval_cleanup_BEST_PRACTICES.md`
  - `approval_cleanup_COMPLETE_SUMMARY.md`
  - `approval_cleanup_IMPROVEMENTS_SUMMARY.md`
  - `APPROVAL_CLEANUP_IMPROVEMENTS.md`
  - `approval_cleanup_REFACTORING.md`
  - `approval_cleanup_TOOLS.md`
  - `README_APPROVAL_CLEANUP.md`

## Estadísticas
- **Total de DAGs**: 14 archivos Python
- **Documentación**: 12 archivos Markdown

