# Changelog - Librerías de Workflows

Todos los cambios notables en las librerías se documentarán en este archivo.

## [2.2.0] - 2024-01-XX

### ✨ Añadido

#### Configuración Robusta
- Nueva librería `config.py` con dataclasses tipadas
- `HubSpotConfig` y `ManyChatConfig` para configuración estructurada
- Carga automática desde variables de entorno con `from_env()`
- Validación de configuración integrada
- Soporte para múltiples entornos (production, staging, development, test)
- Helper `load_config_from_env()` para cargar por nombre de API

#### Connection Pooling Avanzado
- Soporte para `httpx` con connection pooling (prioritario si está disponible)
- Fallback a `requests.Session` con `HTTPAdapter` y retry strategy
- Configuración de límites de conexiones (max_keepalive_connections, max_connections)
- Reutilización de conexiones HTTP para mejor performance

#### Mejoras en Gestión de Recursos
- Context managers mejorados para cierre automático de sesiones
- Soporte mejorado para httpx y requests
- Compatibilidad mejorada entre diferentes clientes HTTP

### 🔄 Mejorado

#### HubSpotClient
- ✅ Integración con `HubSpotConfig` desde `config.py`
- ✅ Connection pooling con httpx o requests
- ✅ Inicialización mejorada que carga configuración desde env automáticamente
- ✅ Soporte para pasar configuración explícita o parámetros individuales
- ✅ Mejor manejo de rate limiting con configuración desde config

#### ManyChatClient
- ✅ Integración con `ManyChatConfig` desde `config.py`
- ✅ Connection pooling con httpx o requests
- ✅ Inicialización mejorada que carga configuración desde env automáticamente
- ✅ Soporte para pasar configuración explícita o parámetros individuales
- ✅ `page_id` ahora se puede configurar desde config

#### Health Checks
- ✅ Compatibilidad mejorada con httpx y requests en health checks
- ✅ Mejor detección de status codes independiente del cliente HTTP

### 📝 Documentación

- ✅ README.md actualizado con ejemplos de configuración
- ✅ Documentación de variables de entorno
- ✅ Ejemplos de uso con context managers y configuración
- ✅ Guía de connection pooling

## [2.1.0] - 2024-01-XX

### ✨ Añadido

#### Health Checks
- Nueva librería `health.py` para health checks estructurados
- Health check integrado en `HubSpotClient` y `ManyChatClient`
- `HealthChecker` para checks agregados
- `HealthStatus` enum (HEALTHY, UNHEALTHY, DEGRADED, UNKNOWN)
- Validación de dependencias opcionales/requeridas

#### Batch Processing
- Nueva librería `batch.py` para procesamiento paralelo
- `BatchProcessor` con ThreadPoolExecutor
- Rate limiting por batch
- Retry automático en batch
- Procesamiento por chunks
- Estadísticas agregadas (success rate, duration, etc.)

#### Context Managers
- Soporte para `with` statement en `HubSpotClient` y `ManyChatClient`
- Cierre automático de sesiones HTTP

### 🔄 Mejorado

#### HubSpotClient
- ✅ Health check integrado
- ✅ Context manager para gestión de recursos

#### ManyChatClient
- ✅ Health check integrado
- ✅ Context manager para gestión de recursos

## [2.0.0] - 2024-01-XX

### ✨ Añadido

#### Circuit Breaker Pattern
- Nueva librería `circuit_breaker.py` para proteger APIs externas
- Estados: CLOSED, OPEN, HALF_OPEN
- Auto-recovery después de timeout
- Configuración flexible de thresholds
- Integrado en `HubSpotClient` y `ManyChatClient`

#### Caché Simple
- Nueva librería `cache.py` con TTL-based caching
- Key-based invalidation
- Auto-cleanup de entradas expiradas
- Estadísticas de hit/miss rate
- Integrado en `HubSpotClient` para reducir llamadas repetidas

#### Métricas Prometheus
- Nueva librería `metrics.py` para observabilidad
- Soporte para Counter, Gauge, Histogram
- Exportación en formato Prometheus text/plain y JSON
- Labels para segmentación
- Integrado en `HubSpotClient` y `ManyChatClient`

#### Tests Unitarios
- Suite inicial de tests en `tests/test_hubspot_client.py`
- Tests para HubSpotContact, HubSpotClient, HubSpotResult
- Ejemplos de mocking y testing

### 🔄 Mejorado

#### HubSpotClient
- ✅ Circuit Breaker integrado (protección automática)
- ✅ Caché integrado (reduce llamadas repetidas)
- ✅ Métricas Prometheus automáticas
- ✅ Parámetro `use_cache` en `get_contact()`
- ✅ Logging mejorado con contexto

#### ManyChatClient
- ✅ Circuit Breaker integrado
- ✅ Métricas Prometheus automáticas
- ✅ Logging mejorado con contexto

### 📝 Documentación

- ✅ README.md completo con ejemplos
- ✅ Documentación de cada módulo
- ✅ Guía de mejores prácticas
- ✅ Ejemplos de uso avanzado

## [1.0.0] - 2024-01-XX

### ✨ Añadido

- `HubSpotClient` con retry automático y rate limiting
- `ManyChatClient` con validación robusta
- `WebhookValidator` para verificación HMAC
- Modelos de datos tipados (HubSpotContact, ManyChatMessage, etc.)
- Logging estructurado
- Manejo de errores consistente

### 📝 Formato

El formato está basado en [Keep a Changelog](https://keepachangelog.com/es-ES/1.0.0/),
y este proyecto adhiere a [Semantic Versioning](https://semver.org/lang/es/).

[2.0.0]: https://github.com/yourorg/yourrepo/compare/v1.0.0...v2.0.0
[1.0.0]: https://github.com/yourorg/yourrepo/releases/tag/v1.0.0

