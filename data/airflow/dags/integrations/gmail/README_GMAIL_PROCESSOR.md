# Gmail Processor DAG

## Descripción

Este DAG procesa correos de Gmail que no tienen la etiqueta 'SinRevisar':
- Obtiene los últimos correos sin la etiqueta 'SinRevisar'
- Añade la etiqueta 'Procesado' a cada correo procesado exitosamente
- Envía los detalles (de, asunto, fecha) a un log externo vía webhook
- Retorna un resumen con el número de correos procesados y fallidos

## Configuración

### 1. Instalar dependencias

**Para desarrollo local (docker-compose):**
Agregar al `requirements.txt` de Airflow (ver `data/airflow/docker-compose.yml`):
```
# Dependencias base requeridas
google-auth>=2.23.0
google-auth-oauthlib>=1.1.0
google-auth-httplib2>=0.1.1
google-api-python-client>=2.100.0
requests>=2.31.0

# Librerías mejoradas (opcionales pero recomendadas)
tenacity>=8.2.3          # Retry con backoff exponencial
httpx>=0.25.0            # Cliente HTTP moderno (reemplaza requests)
pydantic>=2.5.0          # Validación de datos y tipos
cachetools>=5.3.0        # Cache con TTL para optimización
```

**Para Kubernetes (Helm):**
Las dependencias deben instalarse en la imagen de Airflow. Agregar a la imagen base o usar un Dockerfile personalizado con estas dependencias.

```bash
# Instalación mínima (funcional)
pip install google-auth google-auth-oauthlib google-auth-httplib2 google-api-python-client requests

# Instalación completa (recomendada para producción)
pip install google-auth google-auth-oauthlib google-auth-httplib2 google-api-python-client \
    tenacity httpx pydantic cachetools
```

**Nota:** El DAG funciona con las dependencias base, pero las librerías mejoradas proporcionan:
- **tenacity**: Retry automático con backoff exponencial
- **httpx**: Cliente HTTP más moderno y eficiente
- **pydantic**: Validación robusta de datos
- **cachetools**: Cache TTL para optimizar llamadas a API

### 2. Obtener credenciales OAuth2 de Gmail

1. Ir a [Google Cloud Console](https://console.cloud.google.com/)
2. Crear un proyecto o seleccionar uno existente
3. Habilitar la API de Gmail
4. Crear credenciales OAuth 2.0 Client ID (tipo: Desktop app)
5. Descargar el archivo JSON de credenciales

### 3. Autorización inicial

**Nota:** La primera vez necesitarás autorizar la aplicación ejecutando el DAG en modo desarrollo o ejecutando un script de inicialización.

El proceso OAuth2 abrirá un navegador para autorizar el acceso. Una vez autorizado, se guardará un token que se usará en ejecuciones futuras.

### 4. Configurar External Secrets (Integración con Stack)

**Para producción**, las credenciales se gestionan mediante External Secrets Operator:

1. **Almacenar credenciales en Secrets Manager:**
   - AWS Secrets Manager: Guardar en path `integrations/gmail/credentials_json`
   - Azure Key Vault: Guardar como `integrations-gmail-credentials-json`
   - HashiCorp Vault: Guardar en path `integrations/gmail/credentials_json`

2. **Aplicar External Secret:**
   ```bash
   kubectl apply -f security/secrets/externalsecrets-gmail.yaml
   ```

3. **Verificar sincronización:**
   ```bash
   kubectl get externalsecrets -n data
   kubectl describe externalsecret gmail-credentials -n data
   kubectl get secret gmail-secrets -n data
   ```

4. **Configurar variables en Airflow:**
   Las variables de entorno se configuran automáticamente en `data/airflow/values.yaml`.

### 4.1 Variables de Entorno Configurables

El DAG soporta múltiples variables de entorno para personalizar el comportamiento:

**Configuración de Retries y Timeouts:**
- `GMAIL_DAG_RETRIES` (default: `2`): Número de reintentos del DAG
- `GMAIL_RETRY_DELAY_MINUTES` (default: `5`): Delay base entre reintentos
- `GMAIL_MAX_RETRY_DELAY_MINUTES` (default: `30`): Delay máximo entre reintentos
- `GMAIL_DAG_TIMEOUT_MINUTES` (default: `60`): Timeout total del DAG run
- `GMAIL_TASK_TIMEOUT_MINUTES` (default: `45`): Timeout de la tarea principal

**Timeouts de API y Webhooks:**
- `GMAIL_API_TIMEOUT` (default: `30`): Timeout general para operaciones API (segundos)
- `GMAIL_LIST_TIMEOUT` (default: `30`): Timeout para operación list (segundos)
- `GMAIL_GET_TIMEOUT` (default: `10`): Timeout para operación get (segundos)
- `GMAIL_MODIFY_TIMEOUT` (default: `15`): Timeout para operación modify (segundos)
- `GMAIL_LOG_WEBHOOK_TIMEOUT` (default: `30`): Timeout para webhook de logs (segundos)
- `GMAIL_HEALTH_CHECK_TIMEOUT` (default: `10`): Timeout para health check (segundos)

**Rate Limiting:**
- `GMAIL_RATE_LIMIT_DELAY` (default: `0.2`): Delay base para rate limiting (segundos)
- `GMAIL_MAX_RETRY_AFTER` (default: `300`): Máximo Retry-After a respetar (segundos)

**Circuit Breaker:**
- `GMAIL_CB_FAILURE_THRESHOLD` (default: `10`): Fallos antes de abrir circuit breaker
- `GMAIL_CB_RESET_MINUTES` (default: `15`): Minutos antes de resetear circuit breaker

**Batch Processing:**
- `GMAIL_BATCH_SIZE` (default: `10`): Emails por batch
- `GMAIL_BATCH_DELAY` (default: `1.0`): Delay entre batches (segundos)

**Health Check:**
- `GMAIL_HEALTH_CHECK_ENABLED` (default: `true`): Habilitar health check al inicio

**Otras configuraciones:**
- `GMAIL_MAX_EMAILS` (default: `50`): Máximo de emails a procesar por ejecución
- `GMAIL_LABEL_SIN_REVISAR` (default: `SinRevisar`): Nombre de etiqueta a excluir
- `GMAIL_LABEL_PROCESADO` (default: `Procesado`): Nombre de etiqueta a añadir

### 5. Configurar parámetros del DAG (Opcional)

**Nota:** Si las variables de entorno están configuradas (integración con stack), los parámetros son opcionales y solo sobreescriben valores por defecto.

Al ejecutar el DAG manualmente, puedes proporcionar los siguientes parámetros:

```json
{
  "gmail_credentials_json": "/path/to/credentials.json",
  "gmail_token_json": "/path/to/token.json",
  "max_emails": 50,
  "log_webhook_url": "https://tu-servicio.com/api/logs",
  "label_sin_revisar": "SinRevisar",
  "label_procesado": "Procesado",
  "dry_run": false
}
```

#### Parámetros:

- **gmail_credentials_json** (requerido): Path al archivo JSON de credenciales OAuth2 o JSON string
- **gmail_token_json** (opcional): Path al archivo donde guardar/cargar el token, o JSON string del token
- **max_emails** (default: 50): Máximo de correos a procesar por ejecución
- **log_webhook_url** (requerido): URL del webhook para enviar logs externos
- **label_sin_revisar** (default: "SinRevisar"): Nombre de la etiqueta a excluir
- **label_procesado** (default: "Procesado"): Nombre de la etiqueta a añadir
- **dry_run** (default: false): Si es true, solo simula sin modificar correos

### 5. Formato del log externo

El DAG envía los detalles de cada correo procesado al webhook con el siguiente formato:

```json
{
  "timestamp": "2025-01-15T10:30:00.123456Z",
  "source": "gmail_processor",
  "email": {
    "id": "18a1234567890abc",
    "from": "remitente@example.com",
    "subject": "Asunto del correo",
    "date": "Mon, 15 Jan 2025 10:30:00 +0000",
    "threadId": "18b1234567890def",
    "snippet": "Primeros 200 caracteres del cuerpo..."
  }
}
```

### 6. Respuesta del DAG

El DAG retorna un resumen con la siguiente estructura:

```json
{
  "processed": 45,
  "failed": 2,
  "total": 47,
  "dry_run": false,
  "failed_details": [
    {
      "id": "18a1234567890xyz",
      "error": "log_send_failed"
    },
    {
      "id": "18a9876543210abc",
      "error": "label_add_failed"
    }
  ]
}
```

## Ejecución

### Ejecución programada

El DAG está configurado para ejecutarse cada 6 horas automáticamente.

### Ejecución manual

Desde la UI de Airflow:
1. Ir al DAG `gmail_processor`
2. Clic en "Trigger DAG w/ config"
3. Ingresar los parámetros en formato JSON

O vía API:

```bash
curl -X POST \
  http://airflow.example.com/api/v1/dags/gmail_processor/dagRuns \
  -H "Authorization: Basic <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "conf": {
      "gmail_credentials_json": "/path/to/credentials.json",
      "gmail_token_json": "/path/to/token.json",
      "max_emails": 50,
      "log_webhook_url": "https://tu-servicio.com/api/logs",
      "label_sin_revisar": "SinRevisar",
      "label_procesado": "Procesado",
      "dry_run": false
    }
  }'
```

## Almacenamiento seguro de credenciales

**Recomendado:** Para producción, almacenar credenciales en un Secret Manager (Vault, AWS Secrets Manager, etc.) y exponerlas como variables de entorno o Secrets de Kubernetes.

### Ejemplo con External Secrets Operator:

```yaml
apiVersion: external-secrets.io/v1beta1
kind: ExternalSecret
metadata:
  name: gmail-credentials
  namespace: airflow
spec:
  secretStoreRef:
    name: vault-backend
    kind: SecretStore
  target:
    name: gmail-credentials
    creationPolicy: Owner
  data:
    - secretKey: credentials.json
      remoteRef:
        key: gmail/credentials
```

Luego, en el DAG, leer desde el secret o variable de entorno.

## Troubleshooting

### Error: "Gmail API libraries not available"

Instalar las dependencias requeridas (ver sección 1).

### Error: "New OAuth authorization required"

El token ha expirado o es inválido. Ejecutar una vez en modo desarrollo para obtener un nuevo token.

### Error: "Could not get/create label"

Verificar que la cuenta de Gmail tenga permisos para crear etiquetas. Algunas cuentas corporativas pueden tener restricciones.

### No se encuentran correos

Verificar que:
1. La etiqueta 'SinRevisar' existe en Gmail
2. Hay correos que realmente no tienen esa etiqueta
3. La query de búsqueda es correcta

## Limitaciones

- La API de Gmail tiene límites de cuota (250,000 unidades por usuario por día)
- El procesamiento es secuencial por correo
- En producción, el flujo OAuth2 puede requerir configuración adicional si no hay navegador disponible

## Características Avanzadas

### Manejo Inteligente de Errores

El DAG categoriza automáticamente los errores de Gmail API y los maneja según su naturaleza:

- **Errores recuperables** (429, 500, 502, 503, 504): Se reintentan automáticamente con backoff exponencial
- **Errores no recuperables** (400, 401, 403, 404): Se registran y se continúa con el siguiente email

Las categorías de error incluyen:
- `rate_limit`: Rate limiting (429)
- `server_error`: Errores del servidor (500, 502, 503, 504)
- `auth_invalid`: Token inválido (401)
- `auth_forbidden`: Permisos insuficientes (403)
- `not_found`: Recurso no encontrado (404)
- `bad_request`: Solicitud inválida (400)

### Métricas Detalladas

El DAG registra métricas detalladas usando Airflow Stats (si está disponible):

**Métricas de ejecución:**
- `gmail_processor.run_started`: Inicio de ejecución
- `gmail_processor.run_completed`: Finalización de ejecución
- `gmail_processor.emails_found`: Emails encontrados
- `gmail_processor.emails_processed`: Emails procesados exitosamente
- `gmail_processor.emails_failed`: Emails fallidos
- `gmail_processor.emails_skipped`: Emails omitidos (idempotencia)

**Métricas de API:**
- `gmail_processor.api.list_calls`: Llamadas a list
- `gmail_processor.api.get_calls`: Llamadas a get
- `gmail_processor.api.list_errors`: Errores en list
- `gmail_processor.api.get_errors`: Errores en get
- `gmail_processor.api.modify_errors`: Errores en modify

**Métricas de errores:**
- `gmail_processor.rate_limit.hit`: Rate limits encontrados
- `gmail_processor.health_check.success`: Health checks exitosos
- `gmail_processor.health_check.failed`: Health checks fallidos

Todas las métricas incluyen tags con información contextual (run_id, status_code, error_category, etc.).

### Idempotencia

El DAG implementa idempotencia usando Airflow Variables para evitar procesar el mismo email múltiples veces:
- Verifica si un email ya fue procesado antes de procesarlo
- Marca emails como procesados después de éxito
- Soporta múltiples runs del mismo DAG sin duplicados

## Mejoras Implementadas

- [x] Procesamiento en batch para múltiples correos
- [x] Retry automático con backoff exponencial (tenacity)
- [x] Métricas detalladas con Airflow Stats
- [x] Integración con sistema de logs estructurados (plugins.etl_logging)
- [x] Manejo inteligente de errores con categorización
- [x] Circuit breaker para prevenir fallos en cascada
- [x] Rate limiting adaptativo con Retry-After
- [x] Health checks antes de procesar
- [x] Timeouts configurables para todas las operaciones
- [x] Validación de datos con Pydantic
- [x] Idempotencia para evitar reprocesamiento

## Mejoras futuras

- [ ] Soporte para Service Account (sin OAuth2)
- [ ] Exportación de métricas a Prometheus directamente
- [ ] Procesamiento asíncrono con threading
- [ ] Cache de resultados de queries complejas

