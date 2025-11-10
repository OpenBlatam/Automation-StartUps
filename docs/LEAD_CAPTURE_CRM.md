# Sistema de Captura Automática de Leads con Integración CRM

## 📋 Visión General

Sistema completo que captura leads automáticamente desde tu web, asigna vendedores, actualiza estados y programa seguimientos. Integra con **Salesforce** o **Pipedrive** para mantener tu pipeline organizado sin esfuerzo.

## 🎯 Características Principales

✅ **Captura Automática**: Endpoint webhook para recibir leads desde formularios web  
✅ **Scoring Inteligente**: Sistema automático de scoring basado en múltiples factores  
✅ **Asignación Automática**: Asigna leads a vendedores usando routing inteligente  
✅ **Sincronización Bidireccional**: Mantiene BD y CRM sincronizados automáticamente  
✅ **Programación de Seguimientos**: Crea tareas de seguimiento automáticamente  
✅ **Actualización de Estados**: Sincroniza cambios de estado en tiempo real  
✅ **Soporte Multi-CRM**: Salesforce y Pipedrive  
✅ **Enriquecimiento Automático**: Enriquece datos de leads con información adicional  
✅ **Detección de Duplicados**: Identifica y consolida leads duplicados automáticamente  
✅ **Notificaciones Automáticas**: Alertas sobre eventos importantes del pipeline  
✅ **API REST Completa**: API para consultar y gestionar leads programáticamente  

## 🏗️ Arquitectura

```
┌─────────────────────────────────────────────────────────┐
│              Formulario Web / Landing Page              │
└────────────────────┬────────────────────────────────────┘
                     │ POST /webhook/lead
                     ▼
┌─────────────────────────────────────────────────────────┐
│         Webhook Endpoint (webhook_lead_capture.py)      │
│  - Validación de datos                                  │
│  - Verificación de firma                                │
│  - Trigger DAG de Airflow                               │
└────────────────────┬────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────┐
│         DAG: web_lead_capture                           │
│  1. Validar y normalizar datos                          │
│  2. Calcular score y prioridad                          │
│  3. Guardar en base de datos                            │
│  4. Asignar vendedor                                    │
│  5. Sincronizar con CRM                                 │
│  6. Crear tareas de seguimiento                         │
└────────────────────┬────────────────────────────────────┘
                     │
        ┌────────────┴────────────┐
        ▼                         ▼
┌───────────────┐        ┌───────────────┐
│  PostgreSQL  │        │  Salesforce   │
│  (Pipeline)   │◄──────►│  o Pipedrive  │
└───────────────┘        └───────────────┘
        │                         │
        └─────────────────────────┘
                     │
        ┌────────────┴────────────┐
        ▼                         ▼
┌───────────────┐        ┌───────────────┐
│  DAG:         │        │  DAG:         │
│  sales_       │        │  crm_         │
│  intelligent_ │        │  bidirectional_│
│  routing      │        │  sync         │
└───────────────┘        └───────────────┘
```

## 🚀 Configuración Inicial

### 1. Configurar Base de Datos

Asegúrate de que las tablas estén creadas:

```bash
psql -U postgres -d your_database -f data/db/sales_tracking_schema.sql
```

### 2. Configurar Variables de Entorno

#### Para Salesforce:
```bash
export CRM_TYPE="salesforce"
export SALESFORCE_USERNAME="tu_usuario"
export SALESFORCE_PASSWORD="tu_password"
export SALESFORCE_SECURITY_TOKEN="tu_security_token"
export SALESFORCE_CLIENT_ID="tu_client_id"
export SALESFORCE_CLIENT_SECRET="tu_client_secret"
export SALESFORCE_SANDBOX="false"  # o "true" para sandbox
```

#### Para Pipedrive:
```bash
export CRM_TYPE="pipedrive"
export PIPEDRIVE_API_TOKEN="tu_api_token"
export PIPEDRIVE_COMPANY_DOMAIN="tu_dominio"  # ej: "mycompany"
export PIPEDRIVE_DEFAULT_STAGE_ID="1"  # ID del stage por defecto
```

#### Webhook:
```bash
export WEBHOOK_SECRET_KEY="tu_secret_key_para_firmas"  # Opcional pero recomendado
export WEBHOOK_PORT="5000"
export WEBHOOK_DEBUG="false"
```

### 3. Configurar Airflow Connections

En Airflow UI, crear conexión PostgreSQL:

```
Connection ID: postgres_default
Connection Type: Postgres
Host: tu_host
Schema: tu_database
Login: tu_usuario
Password: tu_password
Port: 5432
```

## 📡 Uso del Webhook

### Endpoint Principal

**POST** `/webhook/lead`

Recibe un lead desde un formulario web.

#### Request Body:
```json
{
  "email": "cliente@empresa.com",
  "first_name": "Juan",
  "last_name": "Pérez",
  "phone": "+34612345678",
  "company": "Mi Empresa SL",
  "source": "web",
  "message": "Interesado en conocer más sobre el producto",
  "utm_source": "google",
  "utm_campaign": "summer_2024",
  "utm_medium": "cpc",
  "landing_page": "https://tuweb.com/landing",
  "metadata": {
    "custom_field": "valor"
  }
}
```

#### Response (202 Accepted):
```json
{
  "success": true,
  "message": "Lead recibido y en proceso",
  "lead_email": "cliente@empresa.com",
  "status": "queued",
  "dag_run_id": "webhook_20250101_120000_123456",
  "mode": "airflow"
}
```

### Endpoint Batch

**POST** `/webhook/lead/batch`

Recibe múltiples leads en un lote.

#### Request Body:
```json
{
  "leads": [
    {
      "email": "cliente1@empresa.com",
      "first_name": "Juan",
      "last_name": "Pérez"
    },
    {
      "email": "cliente2@empresa.com",
      "first_name": "María",
      "last_name": "García"
    }
  ]
}
```

### Verificación de Firma (Opcional)

Si configuraste `WEBHOOK_SECRET_KEY`, incluye el header:

```
X-Webhook-Signature: <HMAC_SHA256_signature>
```

La firma se calcula como:
```python
import hmac
import hashlib

signature = hmac.new(
    secret_key.encode(),
    request_body.encode(),
    hashlib.sha256
).hexdigest()
```

## 🔄 Sincronización con CRM

### DAG: `crm_bidirectional_sync`

Sincroniza automáticamente el pipeline con CRM cada 6 horas.

#### Parámetros:
- `crm_type`: `salesforce` o `pipedrive`
- `crm_config`: JSON con configuración del CRM
- `sync_direction`: `bidirectional`, `to_crm`, o `from_crm`
- `max_records_per_run`: Máximo de registros a sincronizar (default: 100)
- `sync_stages`: Sincronizar cambios de estado (default: true)
- `create_deals`: Crear deals en CRM para leads calificados (default: true)

#### Ejemplo de Configuración:

**Salesforce:**
```json
{
  "username": "tu_usuario",
  "password": "tu_password",
  "security_token": "tu_token",
  "client_id": "tu_client_id",
  "client_secret": "tu_client_secret",
  "sandbox": false
}
```

**Pipedrive:**
```json
{
  "api_token": "tu_api_token",
  "company_domain": "tu_dominio",
  "default_stage_id": "1"
}
```

## 📊 Sistema de Scoring

El sistema calcula automáticamente un score (0-100) basado en:

### Factores Básicos (40 puntos):
- ✅ Nombre completo: +10 puntos
- ✅ Teléfono: +10 puntos
- ✅ Empresa: +10 puntos
- ✅ Mensaje: +10 puntos

### UTM Tracking (20 puntos):
- ✅ Campaign: +10 puntos
- ✅ Source: +5 puntos
- ✅ Medium: +5 puntos

### Source Quality (20 puntos):
- ✅ Organic/Direct/Referral: +10 puntos
- ✅ Paid/Social: +5 puntos

### Metadata Signals (20 puntos):
- ✅ Landing page: +5 puntos

### Prioridad:
- **High**: Score ≥ 70
- **Medium**: Score 40-69
- **Low**: Score < 40

## 🎯 Asignación de Vendedores

El sistema asigna automáticamente leads a vendedores usando:

1. **Routing Inteligente** (`sales_intelligent_routing` DAG):
   - Carga de trabajo actual
   - Especialización por industria/producto
   - Performance histórica
   - Disponibilidad

2. **Round-Robin** (fallback):
   - Asigna al vendedor con menos leads activos

## 📅 Seguimientos Automáticos

El sistema crea automáticamente tareas de seguimiento:

- **High Priority**: 1 día
- **Medium Priority**: 2 días
- **Low Priority**: 3 días

Las tareas se crean en la tabla `sales_followup_tasks` y se pueden integrar con sistemas externos de gestión de tareas.

## 🔧 Ejecución Manual

### Desde Airflow UI:

1. **Capturar Lead Manualmente:**
   - Ir a DAG `web_lead_capture`
   - Click en "Trigger DAG w/ config"
   - Configurar parámetros:
   ```json
   {
     "lead_data": "{\"email\":\"test@example.com\",\"first_name\":\"Test\",\"last_name\":\"User\"}",
     "crm_type": "salesforce",
     "crm_config": "{\"username\":\"...\",\"password\":\"...\"}",
     "auto_assign_enabled": true,
     "auto_sync_crm": true,
     "create_followup_tasks": true
   }
   ```

2. **Sincronizar con CRM:**
   - Ir a DAG `crm_bidirectional_sync`
   - Trigger manual o esperar ejecución programada

### Desde Python:

```python
from airflow.api.client.local_client import Client

client = Client()

# Capturar lead
config = {
    "lead_data": json.dumps({
        "email": "cliente@empresa.com",
        "first_name": "Juan",
        "last_name": "Pérez"
    }),
    "crm_type": "salesforce",
    "auto_assign_enabled": True
}

dag_run = client.trigger_dag(
    dag_id="web_lead_capture",
    conf=config
)
```

### Desde cURL:

```bash
curl -X POST http://localhost:5000/webhook/lead \
  -H "Content-Type: application/json" \
  -H "X-Webhook-Signature: <signature>" \
  -d '{
    "email": "cliente@empresa.com",
    "first_name": "Juan",
    "last_name": "Pérez",
    "phone": "+34612345678",
    "company": "Mi Empresa SL",
    "source": "web"
  }'
```

## 🐛 Troubleshooting

### Error: "No se pudo conectar al CRM"

**Causa**: Credenciales incorrectas o CRM no disponible  
**Solución**: 
- Verificar credenciales en variables de entorno
- Verificar conectividad de red
- Para Salesforce, verificar que el Security Token sea correcto

### Error: "Lead no encontrado en BD"

**Causa**: El lead no existe en la tabla `sales_pipeline`  
**Solución**: Verificar que el lead fue guardado correctamente en el paso anterior

### Error: "Invalid signature"

**Causa**: Firma HMAC incorrecta  
**Solución**: Verificar que `WEBHOOK_SECRET_KEY` sea el mismo en cliente y servidor

### Sincronización lenta

**Causa**: Muchos registros o problemas de red  
**Solución**: 
- Reducir `max_records_per_run`
- Verificar latencia de API del CRM
- Considerar ejecutar sincronización en horarios de menor carga

## 📈 Métricas y Monitoreo

El sistema registra métricas en Airflow Stats:

- `sales_routing.assigned`: Leads asignados
- `sales_routing.reassigned`: Leads re-asignados
- `crm_sync.total_synced`: Total sincronizado
- `crm_sync.to_crm`: Sincronizados hacia CRM
- `crm_sync.from_crm`: Sincronizados desde CRM

## 🔄 Funcionalidades Avanzadas

### Enriquecimiento Automático de Leads

El DAG `lead_enrichment` enriquece automáticamente los datos de leads:

**Características:**
- Validación de email y teléfono
- Búsqueda de información de empresa
- Perfiles en redes sociales
- Detección de dominio empresarial
- Scoring adicional basado en datos enriquecidos

**Configuración:**
```python
# Parámetros del DAG
{
    "enable_email_validation": true,
    "enable_company_lookup": true,
    "enable_social_lookup": false,  # Requiere API keys externas
    "max_leads_per_run": 50
}
```

### Detección de Duplicados

El DAG `lead_deduplication` detecta y consolida leads duplicados:

**Criterios de Detección:**
- Email (principal)
- Teléfono
- Nombre + Empresa
- Dominio de email

**Modo de Operación:**
- **Auto-merge**: Consolidación automática de datos
- **Manual Review**: Marca duplicados para revisión manual

**Ejemplo:**
```python
# Parámetros del DAG
{
    "auto_merge": true,  # o false para solo marcar
    "similarity_threshold": 0.85,
    "max_leads_per_run": 200
}
```

### Notificaciones Automáticas

El DAG `lead_notifications` envía alertas sobre:

- **Leads de Alta Prioridad**: Nuevos leads con score alto
- **Leads Stale**: Leads sin contacto por X días
- **Seguimientos Próximos**: Recordatorios de tareas próximas
- **Cambios Importantes**: Cambios de stage críticos

**Configuración Slack:**
```bash
export SLACK_WEBHOOK_URL="https://hooks.slack.com/services/YOUR/WEBHOOK/URL"
```

### API REST para Leads

Endpoint completo para gestionar leads programáticamente:

**Endpoints Disponibles:**

1. **GET** `/api/leads` - Listar leads con filtros
   ```bash
   curl "http://localhost:5001/api/leads?stage=qualified&priority=high&limit=50"
   ```

2. **GET** `/api/leads/<lead_ext_id>` - Obtener lead específico
   ```bash
   curl "http://localhost:5001/api/leads/WEB-ABC123"
   ```

3. **PUT** `/api/leads/<lead_ext_id>/stage` - Actualizar stage
   ```bash
   curl -X PUT "http://localhost:5001/api/leads/WEB-ABC123/stage" \
     -H "Content-Type: application/json" \
     -d '{"stage": "contacted", "notes": "Contactado por teléfono"}'
   ```

4. **PUT** `/api/leads/<lead_ext_id>/assign` - Asignar lead
   ```bash
   curl -X PUT "http://localhost:5001/api/leads/WEB-ABC123/assign" \
     -H "Content-Type: application/json" \
     -d '{"assigned_to": "vendedor@empresa.com"}'
   ```

5. **GET** `/api/leads/statistics` - Estadísticas del pipeline
   ```bash
   curl "http://localhost:5001/api/leads/statistics"
   ```

**Ejemplo de Respuesta:**
```json
{
  "success": true,
  "count": 25,
  "leads": [
    {
      "lead_ext_id": "WEB-ABC123",
      "email": "cliente@empresa.com",
      "first_name": "Juan",
      "last_name": "Pérez",
      "score": 85,
      "priority": "high",
      "stage": "qualified",
      "assigned_to": "vendedor@empresa.com",
      "estimated_value": 50000.00,
      "probability_pct": 20
    }
  ]
}
```

## 🚀 Iniciar Servicios

### 1. Webhook de Captura

```bash
cd data/integrations
python webhook_lead_capture.py
```

### 2. API REST

```bash
cd data/integrations
python lead_api.py
```

### 3. Configurar Variables de Entorno

```bash
# Webhook
export WEBHOOK_PORT=5000
export WEBHOOK_SECRET_KEY="tu_secret_key"

# API
export API_PORT=5001
export DATABASE_URL="postgresql://user:pass@localhost:5432/db"

# CRM
export CRM_TYPE="salesforce"
export SALESFORCE_USERNAME="..."
# ... más variables
```

## 📊 DAGs Disponibles

| DAG | Frecuencia | Descripción |
|-----|------------|-------------|
| `web_lead_capture` | Manual/Webhook | Captura y procesa leads desde web |
| `crm_bidirectional_sync` | Cada 6 horas | Sincroniza con CRM |
| `lead_enrichment` | Cada 4 horas | Enriquece datos de leads |
| `lead_deduplication` | Cada 12 horas | Detecta y consolida duplicados |
| `lead_segmentation` | Cada 6 horas | Segmenta leads automáticamente |
| `lead_ml_scoring` | Cada 12 horas | Scoring ML predictivo |
| `lead_nurturing_advanced` | Cada 4 horas | Nurturing avanzado multi-canal |
| `lead_forecasting` | Semanal (lunes) | Forecasting y predicciones |
| `lead_qualification` | Cada 3 horas | Qualificación BANT automática |
| `lead_behavioral_scoring` | Cada 2 horas | Scoring basado en comportamiento |
| `lead_calendar_integration` | Cada 4 horas | Integración con calendarios |
| `lead_analytics` | Diario (medianoche) | Genera analytics y reportes |
| `lead_notifications` | Cada 2 horas | Envía notificaciones |
| `sales_intelligent_routing` | Cada 3 horas | Asigna leads a vendedores |
| `sales_followup_automation` | Cada 2 horas | Gestiona seguimientos |

## 🎯 Segmentación Automática

El DAG `lead_segmentation` segmenta leads en categorías para personalización:

**Segmentos Calculados:**
- **Por Score**: Premium (80+), High (60-79), Medium (40-59), Low (<40)
- **Por Prioridad**: High, Medium, Low
- **Por Fuente**: Paid, Organic, Unknown
- **Por Tamaño de Empresa**: Enterprise, Mid-market, Small Business
- **Por Comportamiento**: Enterprise Contact, Engaged, New
- **Por Industria**: Si está disponible en datos enriquecidos

**Uso de Segmentos:**
Los segmentos se guardan en `metadata.segments` y se usan para:
- Personalización de campañas
- Routing inteligente
- Asignación de vendedores especializados
- Nurturing personalizado

## 📈 Analytics y Reportes

El DAG `lead_analytics` genera reportes diarios con:

**Métricas Calculadas:**
- Conversión por etapa
- Tiempo promedio en cada etapa
- Performance por vendedor
- Performance por fuente
- Trends diarios
- Pipeline value

**Acceso a Analytics:**
Los analytics se guardan en la tabla `lead_analytics` y están disponibles vía API:

```bash
# Obtener analytics del día
curl "http://localhost:5003/api/dashboard/summary?days=30"
```

## 🔄 Webhooks Bidireccionales

### Recibir Actualizaciones desde CRM

El servicio `crm_webhook_receiver` recibe webhooks cuando hay cambios en el CRM:

**Endpoints:**
- `/webhook/crm/salesforce` - Webhooks de Salesforce
- `/webhook/crm/pipedrive` - Webhooks de Pipedrive

**Configuración en CRM:**

**Salesforce:**
1. Setup → Process Automation → Workflows → Outbound Message
2. Configurar para Lead object
3. URL: `https://tu-servidor.com/webhook/crm/salesforce`
4. Campos a enviar: Id, Email, Status

**Pipedrive:**
1. Settings → Personal → Webhooks
2. Agregar webhook para Person updates
3. URL: `https://tu-servidor.com/webhook/crm/pipedrive`

**Iniciar Receiver:**
```bash
cd data/integrations
python crm_webhook_receiver.py
```

## 📊 Dashboard API

API completa para visualización de datos:

**Endpoints Disponibles:**

1. **GET** `/api/dashboard/summary` - Resumen del pipeline
   ```bash
   curl "http://localhost:5003/api/dashboard/summary?days=30"
   ```

2. **GET** `/api/dashboard/funnel` - Datos del funnel
   ```bash
   curl "http://localhost:5003/api/dashboard/funnel?days=30"
   ```

3. **GET** `/api/dashboard/recent-leads` - Leads recientes
   ```bash
   curl "http://localhost:5003/api/dashboard/recent-leads?limit=20"
   ```

4. **GET** `/api/dashboard/top-performers` - Top vendedores
   ```bash
   curl "http://localhost:5003/api/dashboard/top-performers?days=30"
   ```

5. **GET** `/api/dashboard/source-performance` - Performance por fuente
   ```bash
   curl "http://localhost:5003/api/dashboard/source-performance?days=30"
   ```

**Iniciar Dashboard API:**
```bash
cd data/integrations
python lead_dashboard_api.py
```

## 🤖 Machine Learning Scoring

El DAG `lead_ml_scoring` utiliza modelos ML para scoring predictivo:

**Características:**
- Entrenamiento automático con datos históricos
- Modelos disponibles: Gradient Boosting, Random Forest
- Predicción de probabilidad de conversión
- Actualización automática de scores
- Reentrenamiento opcional

**Uso:**
```python
# Parámetros del DAG
{
    "ml_model_type": "gradient_boosting",
    "retrain_model": true,  # Reentrenar modelo
    "max_leads_per_run": 200
}
```

**Métricas del Modelo:**
- Accuracy: Precisión del modelo
- Precision: Precisión de predicciones positivas
- Recall: Tasa de detección de conversiones

## 🌱 Nurturing Avanzado

El DAG `lead_nurturing_advanced` gestiona nurturing inteligente:

**Características:**
- Secuencias personalizadas por segmento
- Multi-canal (Email + SMS)
- Ajuste automático de frecuencia
- Pausa automática si hay respuesta
- Reactivación de leads fríos
- Personalización basada en comportamiento

**Secuencias Disponibles:**
- **Premium**: 4 emails en 7 días
- **High Priority**: 2 emails + 1 SMS en 5 días
- **Medium**: 3 emails en 10 días

**Configuración:**
```python
{
    "enable_email_nurturing": true,
    "enable_sms_nurturing": false,
    "email_api_url": "https://api.email-service.com/send",
    "sms_api_url": "https://api.sms-service.com/send"
}
```

## 📈 Forecasting y Predicciones

El DAG `lead_forecasting` genera predicciones:

**Predicciones Incluidas:**
- **Pipeline Value Forecast**: Valor predicho del pipeline
- **Time to Close Forecast**: Tiempo promedio hasta cierre
- **Lead Generation Forecast**: Predicción de generación de leads
- **Intervalos de Confianza**: Predicciones con niveles de confianza

**Uso:**
```python
{
    "forecast_days": 30,
    "confidence_level": 0.8  # 80% de confianza
}
```

**Métricas Calculadas:**
- Conversión histórica
- Valor promedio de deal
- Tiempo promedio de cierre
- Tendencia de generación de leads

## 🎯 Qualificación Automática BANT

El DAG `lead_qualification` qualifica leads usando criterios BANT:

**Criterios BANT:**
- **Budget**: Presupuesto disponible (1 punto)
- **Authority**: Autoridad para decidir (1 punto)
- **Need**: Necesidad real (1 punto)
- **Timeline**: Urgencia/timeline (1 punto)

**Qualificación:**
- 4/4 = Altamente qualificado
- 3/4 = Bien qualificado
- 2/4 = Moderadamente qualificado
- <2 = No qualificado

**Configuración:**
```python
{
    "bant_threshold": 3,  # Mínimo para considerar qualificado
    "auto_qualify_enabled": true
}
```

## 📊 Scoring Basado en Comportamiento

El DAG `lead_behavioral_scoring` calcula score dinámico:

**Eventos Rastreados:**
- Visitas a sitio web
- Descargas de contenido
- Clicks en emails
- Interacciones con chatbot
- Visualización de pricing
- Registro a webinars
- Solicitud de demo

**Peso de Eventos:**
- Demo Request: 20 puntos
- Webinar Register: 15 puntos
- Form Submit: 10 puntos
- Pricing View: 8 puntos
- Download: 5 puntos
- Email Click: 3 puntos
- Page Visit: 1 punto

**Decay Temporal:**
Los eventos pierden peso con el tiempo (decay over 30 días por defecto).

## 📅 Integración con Calendarios

El DAG `lead_calendar_integration` sincroniza con calendarios:

**Funcionalidades:**
- Crear eventos automáticamente para reuniones
- Sincronizar con Google Calendar, Outlook, Calendly
- Enviar recordatorios de reuniones
- Detectar disponibilidad de vendedores

**Soportado:**
- Google Calendar
- Microsoft Outlook
- Calendly

## 📄 Exportación de Reportes

El módulo `lead_report_exporter` exporta reportes en múltiples formatos:

**Formatos Disponibles:**
- **CSV**: Para análisis en Excel/Google Sheets
- **Excel**: Con múltiples hojas y formateo
- **PDF**: Reportes formateados para presentación

**Uso:**
```python
from data.integrations.lead_report_exporter import export_report

# Exportar a CSV
export_report('csv', 'leads_report.csv', days=30)

# Exportar a Excel
export_report('excel', 'leads_report.xlsx', days=30, filters={'stage': 'qualified'})

# Exportar a PDF
export_report('pdf', 'leads_report.pdf', days=30)
```

**Desde CLI:**
```bash
python data/integrations/lead_report_exporter.py csv leads.csv 30
python data/integrations/lead_report_exporter.py excel leads.xlsx 30
python data/integrations/lead_report_exporter.py pdf leads.pdf 30
```

## 🚀 Servicios Disponibles

| Servicio | Puerto | Descripción |
|----------|--------|-------------|
| Webhook Lead Capture | 5000 | Recibe leads desde formularios |
| Lead API REST | 5001 | API para gestión de leads |
| CRM Webhook Receiver | 5002 | Recibe actualizaciones desde CRM |
| Dashboard API | 5003 | API para dashboard y visualización |

## 🔐 Seguridad

1. **Firmas HMAC**: Siempre usa `WEBHOOK_SECRET_KEY` en producción
2. **HTTPS**: Usa HTTPS para endpoints webhook en producción
3. **Rate Limiting**: Considera agregar rate limiting al webhook
4. **Credenciales**: Nunca hardcodees credenciales, usa variables de entorno

## 📚 Referencias

- [Documentación de Salesforce API](https://developer.salesforce.com/docs/atlas.en-us.api_rest.meta/api_rest/)
- [Documentación de Pipedrive API](https://developers.pipedrive.com/docs/api/v1)
- [Airflow Documentation](https://airflow.apache.org/docs/)

## 🆘 Soporte

Para problemas o preguntas:
1. Revisar logs de Airflow
2. Verificar tablas de auditoría en BD
3. Consultar documentación de APIs de CRM

