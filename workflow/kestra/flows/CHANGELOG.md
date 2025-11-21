# Changelog - HubSpot → ManyChat Integration

## [2.0.0] - 2025-01-15

### ✨ Mejoras con Librerías

#### Nuevas Librerías
- ✅ `lib/hubspot_client.py` - Cliente HubSpot con retry automático y rate limiting
- ✅ `lib/manychat_client.py` - Cliente ManyChat con validación robusta
- ✅ `lib/webhook_validator.py` - Validador de webhooks con HMAC

#### Flujo Mejorado (`hubspot_lead_to_manychat_improved.yaml`)
- ✅ Usa librerías reutilizables en lugar de código inline
- ✅ Retry automático con exponential backoff (tenacity)
- ✅ Manejo inteligente de rate limiting (429)
- ✅ Validación robusta de datos
- ✅ Logging estructurado mejorado
- ✅ Fetch automático de datos faltantes desde HubSpot API
- ✅ Mejor manejo de errores

### 🔧 Mejoras en Flujo Original

#### `hubspot_lead_to_manychat.yaml` v1.1.0
- ✅ Mejorado `fetch_and_merge_contact_data`:
  - Retry con exponential backoff
  - Manejo de rate limiting (429)
  - Validación inteligente de datos faltantes
  - Preparación de mensaje integrada
- ✅ Simplificado flujo eliminando tarea redundante
- ✅ Mejor manejo de errores en todas las tareas
- ✅ Logging estructurado mejorado

### 📚 Documentación
- ✅ `lib/README.md` - Documentación completa de librerías
- ✅ `INTEGRATION_HUBSPOT_MANYCHAT.md` - Guía de integración completa
- ✅ README actualizado con versiones disponibles

### 🚀 Stack Integration
- ✅ External Secrets para ManyChat API key
- ✅ Ingress para webhooks de Kestra
- ✅ Documentación de deployment

## [1.0.0] - 2025-01-14

### Initial Release
- ✅ Webhook handler para HubSpot
- ✅ Validación de `interés_producto` y `manychat_user_id`
- ✅ Envío de mensajes personalizados a ManyChat
- ✅ Retorno de estado de envío



