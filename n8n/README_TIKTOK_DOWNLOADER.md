# TikTok Downloader - Automatización Mejorada para WhatsApp y Telegram

Este workflow mejorado de n8n permite descargar automáticamente videos de TikTok sin marca de agua cuando se comparte un enlace en WhatsApp o Telegram, con características avanzadas de rate limiting, cache, y validaciones.

## 🎯 Funcionalidades Principales

- ✅ **Multi-plataforma**: Soporte para TikTok, Instagram Reels y YouTube Shorts
- ✅ **Comandos especiales**: `/audio`, `/hd`, `/info`, `/stats`, `/help`
- ✅ **Detección mejorada** de enlaces con validación robusta
- ✅ **Rate limiting** configurable por usuario (por hora y por día)
- ✅ **Sistema de cache** para URLs procesadas (24 horas)
- ✅ **4 APIs de respaldo** para máxima confiabilidad
- ✅ **Validación de tamaño** de video antes de descargar
- ✅ **Soporte para múltiples enlaces** en un solo mensaje
- ✅ **Control de acceso** (whitelist/blacklist de usuarios)
- ✅ **Estadísticas** de uso (total, exitosos, fallidos)
- ✅ **Manejo robusto de errores** con retry automático
- ✅ **Mensajes informativos** mejorados para el usuario

## 📋 Requisitos Previos

### 1. Credenciales de Telegram

1. Crea un bot en Telegram usando [@BotFather](https://t.me/botfather)
2. Obtén el token de acceso del bot
3. En n8n, crea una credencial de tipo "Telegram Bot API" con el token

### 2. Credenciales de WhatsApp (Opcional)

Para WhatsApp, necesitas configurar una de estas opciones:

**Opción A: WhatsApp Business API (Recomendado)**
- Configura WhatsApp Business API a través de Meta
- Obtén el token de acceso y número de teléfono
- Configura el webhook en n8n

**Opción B: WhatsApp Webhook personalizado**
- Usa servicios como Twilio, MessageBird, o similares
- Configura el webhook para recibir mensajes

### 3. Variables de Entorno (Opcionales)

Puedes configurar estas variables de entorno en n8n:

```bash
# URL de API de TikTok (opcional, tiene valor por defecto)
TIKTOK_API_URL=https://api.tiklydown.eu.org/api/download

# URL de API de WhatsApp (si usas servicio personalizado)
WHATSAPP_API_URL=https://api.whatsapp.com

# Rate Limiting (opcional)
MAX_REQUESTS_PER_HOUR=10    # Máximo de requests por hora por usuario
MAX_REQUESTS_PER_DAY=50     # Máximo de requests por día por usuario

# Control de acceso (opcional, separados por comas)
ALLOWED_USERS=123456789,987654321    # Solo estos usuarios pueden usar el bot
BLOCKED_USERS=111111111             # Estos usuarios están bloqueados

# Validación de tamaño (opcional)
MAX_VIDEO_SIZE_MB=50                # Tamaño máximo de video en MB

# Procesamiento en batch (opcional)
ENABLE_BATCH_PROCESSING=true         # Activar procesamiento en batch para múltiples enlaces
MAX_BATCH_SIZE=5                     # Máximo de enlaces a procesar en batch

# Compresión de videos (opcional)
ENABLE_COMPRESSION=true              # Activar compresión automática de videos grandes
COMPRESSION_THRESHOLD_MB=30          # Tamaño mínimo para comprimir (MB)

# Conversión de audio (opcional)
AUDIO_CONVERSION_API_URL=https://api.convertapi.com/convert  # API para conversión a MP3

# Webhooks (opcional)
ENABLE_WEBHOOKS=false                # Activar webhooks para notificaciones externas
WEBHOOK_URL=https://tu-webhook.com/api/notify  # URL del webhook

# Modo Administrador (opcional)
ADMIN_USERS=123456789,987654321      # IDs de usuarios administradores (separados por comas)

# API REST (opcional)
REST_API_KEY=tu-api-key-secreta      # API key para autenticación de API REST
```

## 🚀 Instalación

### Paso 1: Importar el Workflow

1. Abre n8n
2. Ve a "Workflows" → "Import from File"
3. Selecciona el archivo `n8n_workflow_tiktok_downloader.json`
4. El workflow se importará con todos los nodos configurados

### Paso 2: Configurar Credenciales

1. **Telegram:**
   - Haz clic en el nodo "Telegram Trigger"
   - Configura la credencial "Telegram Bot API" con tu token
   - Haz clic en "Save"

2. **WhatsApp (si aplica):**
   - Haz clic en el nodo "Send Video WhatsApp"
   - Configura la credencial "WhatsApp API Auth" con tus credenciales
   - Ajusta la URL en el nodo según tu proveedor

### Paso 3: Activar el Workflow

1. Haz clic en el botón "Active" en la esquina superior derecha
2. El workflow estará listo para recibir mensajes

## 📱 Uso

### Desde Telegram

1. Abre una conversación con tu bot de Telegram
2. Envía un mensaje con un enlace, por ejemplo:
   ```
   https://www.tiktok.com/@usuario/video/1234567890
   ```
   o
   ```
   https://vm.tiktok.com/ABC123XYZ
   ```
3. El bot detectará automáticamente el enlace
4. Recibirás una notificación de que está procesando
5. En unos segundos, recibirás el video sin marca de agua

### Comandos Especiales

El bot soporta varios comandos que puedes usar junto con los enlaces:

- **`/audio` o `audio`**: Descarga solo el audio del video en formato MP3
  ```
  https://tiktok.com/@user/video/123 audio
  ```
  El bot extraerá el audio y lo enviará como archivo MP3. Si el video es grande, puede tomar unos momentos para la conversión.

- **`/hd` o `hd`**: Descarga el video en alta calidad
  ```
  https://instagram.com/reel/ABC hd
  ```

- **`/info` o `info`**: Muestra información del video (título, autor, duración)
  ```
  https://youtube.com/shorts/XYZ info
  ```

- **`/stats` o `stats`**: Muestra tus estadísticas de uso y estadísticas globales
  ```
  /stats
  ```

- **`/history` o `history`**: Ver tu historial de descargas (últimos 20 videos)
  ```
  /history
  ```

- **`/favorite` o `favorite`**: Guardar un video en favoritos (usar junto con un enlace)
  ```
  https://tiktok.com/@user/video/123 favorite
  ```

- **`/favorites` o `favorites`**: Ver todos tus videos favoritos guardados
  ```
  /favorites
  ```

- **`/silent` o `silent`**: Activar modo silencioso (sin notificaciones intermedias)
  ```
  https://tiktok.com/@user/video/123 silent
  ```

- **`/help` o `help`**: Muestra la ayuda con todos los comandos disponibles
  ```
  /help
  ```

### Plataformas Soportadas

- ✅ **TikTok**: Todos los formatos de enlace
- ✅ **Instagram Reels**: Enlaces de reels
- ✅ **YouTube Shorts**: Videos cortos de YouTube

### Desde WhatsApp

1. Envía un mensaje al número configurado con un enlace
2. El sistema procesará el enlace automáticamente
3. Recibirás el video descargado sin marca de agua

## 🔧 Configuración Avanzada

### APIs de Descarga

El workflow utiliza 4 APIs en orden de prioridad:

1. **API 1 (Tiklydown)**: API principal para descargar sin marca de agua
2. **API 2 (TikTok oficial)**: API oficial de TikTok como respaldo
3. **API 3 (Snaptik)**: Servicio de terceros
4. **API 4 (Backup)**: API adicional de respaldo

Si una API falla, automáticamente intenta con la siguiente. Todas las APIs tienen retry automático (2-3 intentos).

### Rate Limiting

El sistema incluye rate limiting configurable:

- **Por hora**: Controla cuántos videos puede descargar un usuario por hora
- **Por día**: Controla el límite diario total
- **Persistente**: Los límites se mantienen entre ejecuciones del workflow

Si un usuario excede el límite, recibirá un mensaje informativo con el tiempo de espera.

### Sistema de Cache

- Las URLs procesadas se guardan en cache por 24 horas
- Si se solicita el mismo video, se envía desde cache (más rápido)
- El cache se almacena en `$workflow.staticData.urlCache`

### Control de Acceso

Puedes configurar listas de usuarios permitidos o bloqueados:

- **ALLOWED_USERS**: Solo estos usuarios pueden usar el bot (dejar vacío para permitir todos)
- **BLOCKED_USERS**: Estos usuarios están bloqueados permanentemente

### Validación de Tamaño

- El sistema verifica el tamaño del video antes de descargarlo
- Por defecto, el límite es 50MB (configurable)
- Si el video es muy grande, se informa al usuario sin descargarlo

### Compresión Automática

- Videos grandes (>30MB por defecto) se comprimen automáticamente
- Reducción de tamaño sin perder calidad significativa
- Notificaciones durante el proceso de compresión
- Configurable con `ENABLE_COMPRESSION` y `COMPRESSION_THRESHOLD_MB`

### Descarga de Audio

- Comando `/audio` para descargar solo el audio del video
- Conversión automática a MP3
- Calidad configurable (192kbps por defecto)
- Extracción directa si la API lo soporta, o conversión del video

### Webhooks

- Notificaciones a sistemas externos cuando se descarga un video
- Datos completos: usuario, video, metadatos, batch info
- Configurable con `ENABLE_WEBHOOKS` y `WEBHOOK_URL`
- No bloquea el flujo principal (asíncrono)

### Sistema de Favoritos

- Guarda videos en favoritos con el comando `/favorite`
- Hasta 50 favoritos por usuario
- Ver todos tus favoritos con `/favorites`
- Persistencia en workflow static data

### Historial de Descargas

- Comando `/history` para ver tu historial personal
- Últimos 20 videos descargados
- Información completa: título, autor, fecha, plataforma
- Opción de habilitar historial en base de datos

### Almacenamiento en Cloud

- Soporte para S3 y Google Cloud Storage
- Almacenamiento automático opcional de videos descargados
- Organización por fecha y plataforma
- Configurable con `ENABLE_CLOUD_STORAGE`, `CLOUD_STORAGE_TYPE`, `CLOUD_STORAGE_BUCKET`

### Modo Silencioso

- Comando `/silent` para activar modo silencioso
- Sin notificaciones intermedias durante el procesamiento
- Solo envía el video final
- Útil para procesamiento en batch o cuando no quieres interrupciones

### Modo Administrador

- Comando `/admin` para gestión avanzada del sistema
- Requiere permisos de administrador (configurar `ADMIN_USERS`)
- Comandos disponibles:
  - `/admin stats` - Estadísticas globales del sistema
  - `/admin users` - Lista de usuarios activos (top 20)
  - `/admin block <userId>` - Bloquear un usuario
  - `/admin unblock <userId>` - Desbloquear un usuario
  - `/admin cache clear` - Limpiar todo el cache
  - `/admin reset <userId>` - Resetear rate limits de un usuario
  - `/admin export` - Exportar todos los datos del sistema
  - `/admin help` - Mostrar ayuda de administración

### API REST

- Endpoint `/api/v1/download` para integraciones externas
- Autenticación mediante header `X-API-Key` o campo `apiKey` en el body
- Request ejemplo:
  ```json
  {
    "url": "https://tiktok.com/@user/video/123",
    "userId": "api-user-123",
    "options": {
      "hd": true,
      "audio": false
    }
  }
  ```
- Response ejemplo:
  ```json
  {
    "success": true,
    "data": {
      "videoUrl": "https://...",
      "title": "Video Title",
      "author": "Author Name",
      "duration": 30,
      "thumbnail": "https://...",
      "platform": "tiktok",
      "downloadMethod": "tiklydown",
      "timestamp": "2024-01-01T00:00:00.000Z"
    },
    "statusCode": 200
  }
  ```

### Sistema de Preferencias

- Preferencias persistentes por usuario
- Se aplican automáticamente a cada request
- Configurables mediante comandos (futuro)
- Incluye: calidad por defecto, modo silencioso, plataforma preferida, tamaño máximo

### Preview de Videos

- Preview automático antes de descargar
- Muestra thumbnail, título, autor y duración
- Mejora la experiencia de usuario
- Se puede desactivar en preferencias

### Personalizar el Workflow

#### Cambiar límites de rate limiting

Edita las variables de entorno `MAX_REQUESTS_PER_HOUR` y `MAX_REQUESTS_PER_DAY`.

#### Cambiar el mensaje de notificación

Edita el nodo "Notify Processing (Telegram)" o "Notify Processing (WhatsApp)" para cambiar el mensaje.

#### Agregar más canales

Puedes agregar más nodos de webhook para otros servicios (Discord, Slack, etc.) siguiendo el mismo patrón que WhatsApp.

#### Filtrar usuarios

Usa las variables de entorno `ALLOWED_USERS` y `BLOCKED_USERS` en lugar de modificar código.

#### Cambiar tiempo de cache

Edita el nodo "Check Cache" y modifica `maxCacheAge` (actualmente 24 horas).

#### Agregar más APIs

Puedes agregar más nodos HTTP Request siguiendo el patrón de las APIs existentes y agregarlos al nodo "Extract Video URL".

## 🐛 Solución de Problemas

### El bot no responde en Telegram

1. Verifica que el token del bot sea correcto
2. Asegúrate de que el workflow esté activo
3. Revisa los logs de ejecución en n8n

### No se descarga el video

1. Verifica que el enlace de TikTok sea válido
2. Revisa los logs de ejecución para ver qué API falló
3. Algunos videos pueden estar protegidos o eliminados

### Error en WhatsApp

1. Verifica las credenciales de la API de WhatsApp
2. Asegúrate de que el webhook esté correctamente configurado
3. Revisa que el formato del mensaje sea el esperado

### Timeout en la descarga

1. Aumenta el timeout en los nodos de descarga (actualmente 30-60 segundos)
2. Verifica tu conexión a internet
3. Algunos videos muy largos pueden tardar más

## 📝 Estructura del Workflow Mejorado

```
Telegram Trigger / WhatsApp Webhook
    ↓
Extract Message
    ↓
Filter Has Text
    ↓
Rate Limiting (nuevo)
    ↓
Check Rate Limit
    ├─→ Detect TikTok Link
    └─→ Send Rate Limit Error
    ↓
Check TikTok Link
    ├─→ Check Cache (nuevo)
    └─→ Send No Link Message
    ↓
Check If Cached
    ├─→ [Desde cache] → Check Has Video
    └─→ Notify Processing
        ↓
        Download TikTok (API 1, 2, 3, 4) [Paralelo]
        ↓
        Extract Video URL (mejorado)
        ↓
        Check Has Video
        ↓
        Check Video Size (nuevo)
        ↓
        Validate Video Size (nuevo)
        ↓
        Check Video Size OK
        ├─→ Download Video File
        └─→ Send Size Error
        ↓
        Check Source
        ├─→ Send Video Telegram
        └─→ Send Video WhatsApp
```

## 🆕 Mejoras Implementadas

### Versión 2.0 - Mejoras Principales

1. **Rate Limiting Avanzado**
   - Control por hora y por día
   - Persistencia entre ejecuciones
   - Mensajes informativos con tiempo de espera

2. **Sistema de Cache**
   - URLs procesadas se guardan por 24 horas
   - Respuestas instantáneas para videos repetidos
   - Ahorro de recursos y tiempo

3. **Validación de Tamaño**
   - Verificación antes de descargar
   - Prevención de descargas de videos muy grandes
   - Configurable por variable de entorno

4. **4 APIs de Respaldo**
   - Mayor confiabilidad
   - Retry automático en cada API
   - Mejor extracción de metadatos

5. **Detección Mejorada**
   - Soporte para múltiples enlaces
   - Validación robusta de URLs
   - Mejor manejo de diferentes formatos de enlace

6. **Control de Acceso**
   - Whitelist y blacklist de usuarios
   - Configuración simple por variables de entorno

7. **Estadísticas**
   - Tracking de requests totales
   - Contador de exitosos y fallidos
   - Almacenado en workflow static data

8. **Mensajes Mejorados**
   - Más informativos y claros
   - Indicación cuando viene de cache
   - Mejor manejo de errores

### Versión 2.1 - Nuevas Funcionalidades

9. **Soporte Multi-Plataforma** 🆕
   - TikTok (todos los formatos)
   - Instagram Reels
   - YouTube Shorts
   - Detección automática de plataforma

10. **Sistema de Comandos** 🆕
    - `/help` - Muestra ayuda completa
    - `/stats` - Estadísticas de uso
    - `/audio` - Descargar solo audio (MP3)
    - `/hd` - Descargar en alta calidad
    - `/info` - Información del video
    - Comandos en español e inglés

11. **Mejoras en Detección** 🆕
    - Detección simultánea de múltiples plataformas
    - Validación mejorada de URLs
    - Soporte para diferentes formatos de enlace

12. **Interfaz Mejorada** 🆕
    - Mensajes con formato Markdown
    - Ayuda interactiva con `/help`
    - Estadísticas detalladas con `/stats`
    - Mejor feedback al usuario

### Versión 2.2 - Funcionalidades Avanzadas 🆕

13. **Procesamiento en Batch** 🆕
    - Procesa múltiples enlaces de un solo mensaje
    - Notificaciones de progreso en tiempo real
    - Resumen final con estadísticas del batch
    - Configurable (máximo de enlaces por batch)

14. **Health Check de APIs** 🆕
    - Monitoreo automático del estado de las APIs
    - Rotación inteligente basada en éxito/fallos
    - Priorización automática de APIs más confiables
    - Auto-recuperación de APIs que fallan

15. **Notificaciones de Progreso** 🆕
    - Notificaciones al inicio de batch
    - Progreso individual por video
    - Resumen final con resultados
    - Indicadores de progreso [1/5], [2/5], etc.

### Versión 2.3 - Funcionalidades Premium 🆕

16. **Descarga de Audio** 🆕
    - Extracción de audio de videos
    - Conversión automática a MP3
    - Comando `/audio` para descargar solo audio
    - Calidad configurable (192kbps por defecto)

17. **Compresión de Videos** 🆕
    - Compresión automática de videos grandes
    - Reducción de tamaño sin perder calidad significativa
    - Configurable (umbral de compresión)
    - Notificaciones durante la compresión

18. **Webhooks para Integraciones** 🆕
    - Notificaciones a sistemas externos
    - Eventos de descarga completada
    - Datos completos del video y usuario
    - Configuración opcional

19. **Mejoras en Metadatos** 🆕
    - Extracción mejorada de thumbnails
    - Información de duración del video
    - Metadatos completos en webhooks
    - Tracking de compresión y cache

### Versión 2.4 - Funcionalidades Enterprise 🆕

20. **Sistema de Favoritos** 🆕
    - Guardar videos en favoritos con `/favorite`
    - Ver todos tus favoritos con `/favorites`
    - Historial personalizado por usuario
    - Hasta 50 favoritos por usuario

21. **Historial de Descargas** 🆕
    - Comando `/history` para ver tu historial
    - Últimos 20 videos descargados
    - Información completa de cada descarga
    - Persistencia en workflow data

22. **Almacenamiento en Cloud** 🆕
    - Soporte para S3, Google Cloud Storage
    - Almacenamiento automático opcional
    - Organización por fecha y plataforma
    - Configuración flexible

23. **Modo Silencioso** 🆕
    - Comando `/silent` para modo silencioso
    - Sin notificaciones intermedias
    - Solo envía el video final
    - Útil para procesamiento en batch

24. **Comandos Adicionales** 🆕
    - `/history` - Ver historial de descargas
    - `/favorite` - Guardar video en favoritos
    - `/favorites` - Ver videos favoritos
    - `/silent` - Activar modo silencioso

### Versión 2.5 - Funcionalidades Avanzadas 🆕

25. **Sistema de Búsqueda** 🆕
    - Comando `/search` para buscar en historial y favoritos
    - Búsqueda por título, autor, URL o plataforma
    - Resultados de historial y favoritos combinados
    - Hasta 10 resultados por categoría

26. **Exportación de Datos** 🆕
    - Comando `/export` para exportar todos tus datos
    - Formato JSON con historial, favoritos y estadísticas
    - Archivo descargable directamente en Telegram
    - Incluye metadatos completos

27. **Análisis de Contenido** 🆕
    - Comando `/analyze` para analizar videos
    - Extracción automática de hashtags
    - Detección de categorías (Dance, Comedy, Music, etc.)
    - Score de engagement calculado
    - Análisis de duración y métricas

28. **Filtros Avanzados** 🆕
    - Filtro por duración mínima (`min:30s`)
    - Filtro por duración máxima (`max:60s`)
    - Filtro por calidad (`quality:hd`)
    - Validación automática antes de descargar
    - Mensajes informativos cuando no se cumplen filtros

## 🔒 Consideraciones Legales

⚠️ **Importante**: Este workflow es para uso personal y educativo. Asegúrate de:

- Respetar los derechos de autor del contenido
- No redistribuir contenido sin permiso
- Cumplir con los términos de servicio de TikTok
- Usar el contenido descargado de manera responsable

## 📚 Recursos Adicionales

- [Documentación de n8n](https://docs.n8n.io/)
- [API de Telegram Bot](https://core.telegram.org/bots/api)
- [WhatsApp Business API](https://developers.facebook.com/docs/whatsapp)

## 🤝 Contribuciones

Si encuentras problemas o tienes sugerencias, por favor:
1. Revisa los logs de ejecución
2. Verifica que todas las credenciales estén correctas
3. Prueba con diferentes enlaces de TikTok

## 📄 Licencia

Este workflow es proporcionado "tal cual" sin garantías. Úsalo bajo tu propia responsabilidad.

---

**Versión**: 2.8  
**Última actualización**: 2024  
**Autor**: Automatización n8n

---

## 📝 Changelog

### Versión 2.7 - Funcionalidades Enterprise Avanzadas 🆕

29. **Modo Administrador** 🆕
    - Comando `/admin` para gestión avanzada del sistema
    - Ver estadísticas globales con `/admin stats`
    - Listar usuarios activos con `/admin users`
    - Bloquear/desbloquear usuarios con `/admin block/unblock <userId>`
    - Limpiar cache con `/admin cache clear`
    - Resetear rate limits con `/admin reset <userId>`
    - Exportar todos los datos con `/admin export`
    - Control de acceso mediante variable `ADMIN_USERS`

30. **API REST para Integraciones** 🆕
    - Endpoint `/api/v1/download` para integraciones externas
    - Autenticación mediante API key (`REST_API_KEY`)
    - Respuestas JSON estructuradas
    - Soporte para opciones personalizadas en requests
    - Integración completa con el workflow principal

31. **Sistema de Preferencias de Usuario** 🆕
    - Preferencias persistentes por usuario
    - Calidad por defecto configurable (auto, hd, sd)
    - Modo silencioso persistente
    - Plataforma preferida
    - Tamaño máximo de video personalizable
    - Control de notificaciones

32. **Sistema de Preview/Thumbnail** 🆕
    - Preview automático antes de descargar
    - Muestra thumbnail, título, autor y duración
    - Mejora la experiencia de usuario
    - Configurable por preferencias

### Versión 2.6 - Soporte Multi-Plataforma Completo 🆕

28. **Soporte para Twitter/X y Facebook** 🆕
    - Detección automática de enlaces de Twitter/X
    - Detección automática de enlaces de Facebook
    - Procesamiento unificado con otras plataformas

### Versión 2.5
- ✅ Sistema de búsqueda en historial y favoritos
- ✅ Exportación de datos en formato JSON
- ✅ Análisis de contenido (hashtags, categorías, engagement)
- ✅ Filtros avanzados de contenido (duración, calidad)
- ✅ Comandos adicionales (/search, /export, /analyze)

### Versión 2.4
- ✅ Sistema de favoritos y guardados
- ✅ Historial de descargas personalizado
- ✅ Almacenamiento opcional en cloud storage (S3, GCS)
- ✅ Modo silencioso para notificaciones
- ✅ Comandos adicionales (/history, /favorite, /favorites, /silent)

### Versión 2.3
- ✅ Descarga de solo audio con conversión a MP3
- ✅ Compresión automática de videos grandes
- ✅ Webhooks para integraciones externas
- ✅ Mejoras en extracción de metadatos y thumbnails

### Versión 2.2
- ✅ Procesamiento en batch para múltiples enlaces
- ✅ Health check de APIs con rotación inteligente
- ✅ Notificaciones de progreso en tiempo real
- ✅ Auto-recuperación de APIs fallidas

### Versión 2.1
- ✅ Agregado soporte multi-plataforma (TikTok, Instagram Reels, YouTube Shorts)
- ✅ Sistema de comandos especiales (`/help`, `/stats`, `/audio`, `/hd`, `/info`)
- ✅ Mejoras en detección de enlaces
- ✅ Interfaz mejorada con Markdown

### Versión 2.0
- ✅ Rate limiting avanzado
- ✅ Sistema de cache
- ✅ Validación de tamaño
- ✅ 4 APIs de respaldo
- ✅ Control de acceso
- ✅ Estadísticas mejoradas

