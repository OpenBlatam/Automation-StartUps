# Meeting Scheduler Automático - Documentación

> **Versión**: 2.0 | **Estado**: Producción Ready ✅

Workflow de Kestra que programa reuniones automáticamente eliminando el "ping-pong" de correos. Incluye verificación de disponibilidad, detección de conflictos, generación de iCal y soporte multi-calendario.

## 🎯 Características Principales

### ✅ Automatización Completa
- **Elimina el ping-pong de correos**: Programa y confirma reuniones automáticamente
- **Verificación de disponibilidad**: Consulta calendarios en tiempo real o genera slots inteligentes
- **Selección inteligente**: Prioriza horarios según preferencias del usuario
- **Confirmación automática**: Envía invitaciones con adjunto iCal (.ics)

### 🔒 Seguridad y Validación
- **Verificación HMAC**: Validación opcional de firma webhook
- **Validación robusta**: Emails, duraciones, límites de asistentes
- **Detección de duplicados**: Previene crear reuniones similares
- **Sanitización de datos**: Limpieza y normalización de inputs

### 🌐 Integraciones Multi-Calendario
- **Google Calendar**: Soporte nativo con Google Meet
- **Microsoft Outlook**: Integración con Teams
- **CalDAV**: Soporte genérico para cualquier servidor CalDAV
- **Fallback inteligente**: Genera slots cuando la API no está disponible

### 📧 Notificaciones Mejoradas
- **Emails HTML**: Formato profesional con toda la información
- **Adjunto iCal**: Archivo .ics para agregar al calendario
- **Notificaciones Slack**: Alertas opcionales en tiempo real
- **Recordatorios Automáticos**: Programables antes de la reunión
- **Persistencia**: Guarda reuniones en base de datos

### ⏰ Gestión Avanzada de Tiempo
- **Buffer Time**: Tiempo de buffer configurable entre reuniones
- **Intervalos Inteligentes**: Ajusta intervalos según duración de reunión
- **Recordatorios Configurables**: Minutos antes de la reunión personalizables
- **Horarios de Negocio**: Respeta horas de trabajo configurables

## 🚀 Uso Rápido

### 1. Configuración de Inputs

```yaml
inputs:
  calendar_api_url: "https://calendar.google.com/api/v3"
  calendar_api_token: "ya29.xxx..."  # Token OAuth2
  calendar_provider: "google"  # google | outlook | caldav
  email_api_url: "https://api.sendgrid.com/v3/mail/send"
  email_api_key: "SG.xxx..."
  database_url: "postgresql://user:pass@host/db"  # Opcional
  slack_webhook_url: "https://hooks.slack.com/..."  # Opcional
  webhook_secret: "your-secret-key"  # Opcional pero recomendado
```

### 2. Payload del Webhook

```json
{
  "organizer_email": "juan@example.com",
  "attendees": [
    "maria@example.com",
    "pedro@example.com"
  ],
  "subject": "Reunión de seguimiento Q1",
  "description": "Revisar objetivos del primer trimestre",
  "duration_minutes": 30,
  "timezone": "America/Mexico_City",
  "location": "Sala de conferencias A",
  "preferred_date": "2025-02-15",
  "preferred_times": ["14:00", "16:00"],
  "auto_confirm": true,
  "send_multiple_options": false
}
```

### 3. Ejemplo de Respuesta Exitosa

El workflow devuelve:
- **Calendario creado**: Evento en Google Calendar/Outlook
- **Invitaciones enviadas**: Email a todos los participantes
- **Archivo iCal**: Adjunto .ics para agregar al calendario
- **Notificación Slack**: (si está configurado)
- **Persistencia DB**: (si está configurado)

## 📋 Campos del Payload

### Campos Requeridos
- `organizer_email` (string): Email del organizador
- `attendees` (array|string): Lista de emails de asistentes
- `subject` (string): Título de la reunión (máx. 200 caracteres)
- `duration_minutes` (integer): Duración entre 15 y 480 minutos

### Campos Opcionales
- `description` (string): Descripción de la reunión
- `location` (string): Ubicación física o virtual
- `timezone` (string): Zona horaria (default: "America/Mexico_City")
- `preferred_date` (string): Fecha preferida (YYYY-MM-DD)
- `preferred_times` (array): Horarios preferidos (ej: ["14:00", "16:00"])
- `preferred_date_range` (object): Rango de fechas preferidas
- `auto_confirm` (boolean): Confirmar automáticamente (default: true)
- `require_confirmation` (boolean): Requerir confirmación (default: false)
- `send_multiple_options` (boolean): Enviar múltiples opciones (default: false)

## 🔧 Variables Configurables

```yaml
variables:
  default_meeting_duration_minutes: 30
  business_hours_start: "09:00"
  business_hours_end: "18:00"
  default_timezone: "America/Mexico_City"
  max_attendees: 50
  min_duration_minutes: 15
  max_duration_minutes: 480
  availability_days_ahead: 14
```

## 🔄 Flujo del Workflow

```
1. verify_webhook_signature (opcional)
   └─ Verifica HMAC si webhook_secret está configurado

2. parse_meeting_request
   └─ Parsea y valida payload
   └─ Normaliza emails, remueve duplicados
   └─ Valida duración, asistentes, subject

3. check_duplicate_meeting (opcional)
   └─ Verifica en DB si existe reunión similar
   └─ Previene duplicados en próximos 7 días

4. check_availability
   └─ Consulta API de calendario
   └─ Fallback: Genera slots inteligentes
   └─ Detecta conflictos potenciales

5. select_best_slot
   └─ Prioriza horarios preferidos
   └─ Selecciona mejor slot disponible
   └─ Opcional: Proporciona múltiples opciones

6. generate_ical
   └─ Genera archivo .ics estándar
   └─ Incluye todos los detalles de la reunión

7. create_calendar_event
   └─ Crea evento en calendario (Google/Outlook)
   └─ Configura reunión virtual (Meet/Teams)
   └─ Invita a todos los participantes

8. send_invitations
   └─ Envía email HTML con detalles
   └─ Adjunta archivo .ics
   └─ Incluye enlace al calendario

9. persist_meeting (opcional)
   └─ Guarda reunión en base de datos
   └─ Tracking de estado y metadata

10. calculate_reminder_time (opcional)
    └─ Calcula tiempo óptimo para recordatorio
    └─ Previene recordatorios en el pasado

11. schedule_reminder (opcional)
    └─ Programa recordatorio automático
    └─ Configurable minutos antes de la reunión

12. notify_slack (opcional)
    └─ Envía notificación a Slack
    └─ Incluye resumen de la reunión
```

## 🔐 Seguridad del Webhook

Para habilitar verificación HMAC, configura `webhook_secret` y envía el header:

```
X-Hub-Signature-256: sha256=<hash>
```

El workflow calcula el hash SHA256 del body usando el secret y compara con el header.

## 📊 Base de Datos (Opcional)

Si configuras `database_url`, el workflow crea/usa esta tabla:

```sql
CREATE TABLE scheduled_meetings (
    id SERIAL PRIMARY KEY,
    execution_id VARCHAR(255) UNIQUE,
    organizer_email VARCHAR(255),
    attendees TEXT[],
    subject TEXT,
    start_time TIMESTAMP,
    end_time TIMESTAMP,
    duration_minutes INTEGER,
    calendar_event_id VARCHAR(255),
    calendar_provider VARCHAR(50),
    status VARCHAR(50) DEFAULT 'confirmed',
    ical_attachment BOOLEAN DEFAULT true,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);
```

## 🎨 Ejemplos de Uso

### Ejemplo 1: Reunión Simple

```bash
curl -X POST https://kestra.example.com/api/v1/executions/trigger/webhook/meeting_scheduler \
  -H "Content-Type: application/json" \
  -d '{
    "organizer_email": "juan@example.com",
    "attendees": ["maria@example.com"],
    "subject": "1:1 Semanal",
    "duration_minutes": 30
  }'
```

### Ejemplo 2: Reunión con Preferencias

```bash
curl -X POST https://kestra.example.com/api/v1/executions/trigger/webhook/meeting_scheduler \
  -H "Content-Type: application/json" \
  -d '{
    "organizer_email": "juan@example.com",
    "attendees": ["maria@example.com", "pedro@example.com"],
    "subject": "Revisión de Proyecto",
    "description": "Discutir avances y próximos pasos",
    "duration_minutes": 60,
    "preferred_date": "2025-02-20",
    "preferred_times": ["14:00", "15:00"],
    "location": "Sala A",
    "send_multiple_options": true
  }'
```

### Ejemplo 3: Reunión con Verificación HMAC

```bash
SECRET="your-webhook-secret"
BODY='{"organizer_email":"juan@example.com","attendees":["maria@example.com"],"subject":"Reunión","duration_minutes":30}'
SIGNATURE=$(echo -n "$BODY" | openssl dgst -sha256 -hmac "$SECRET" | cut -d' ' -f2)

curl -X POST https://kestra.example.com/api/v1/executions/trigger/webhook/meeting_scheduler \
  -H "Content-Type: application/json" \
  -H "X-Hub-Signature-256: sha256=$SIGNATURE" \
  -d "$BODY"
```

## 🛠️ Troubleshooting

### Problema: No se encuentran slots disponibles
**Solución**: 
- Verifica configuración de `availability_days_ahead`
- Revisa que `business_hours_start/end` sean correctos
- El workflow usa fallback automático si la API falla

### Problema: Email no llega
**Solución**:
- Verifica `email_api_url` y `email_api_key`
- Revisa logs del task `send_invitations`
- Confirma que el servicio de email acepta adjuntos .ics

### Problema: Calendario no se crea
**Solución**:
- Verifica token de `calendar_api_token`
- Confirma permisos del token (calendars.readonly + calendars.events)
- Revisa logs del task `create_calendar_event`

### Problema: Duplicados detectados incorrectamente
**Solución**:
- El workflow compara `subject` + `organizer_email` en próximos 7 días
- Ajusta la lógica en `check_duplicate_meeting` si es necesario
- Desactiva el check configurando `database_url` como opcional

## 📈 Métricas y Observabilidad

El workflow genera logs estructurados en cada paso:
- **INFO**: Operaciones exitosas
- **WARNING**: Fallbacks o datos no ideales
- **ERROR**: Fallos críticos que detienen el flujo

Ejemplo de logs:
```
INFO: Parsed meeting request - organizer: juan@example.com, attendees: 2, duration: 30m
INFO: Found 15 available slots via calendar API
INFO: Selected slot - 2025-02-15 14:00, reason: preferred_match
INFO: iCal file generated successfully
INFO: Meeting persisted to database successfully
```

## 🔄 Integraciones con Otros Workflows

Este workflow puede ser llamado desde:
- **Airflow DAGs**: Via API de Kestra
- **Webhooks externos**: Slack, Discord, etc.
- **Otros workflows Kestra**: Como subflow
- **APIs REST**: Cualquier cliente HTTP

## 📚 Referencias

- [Documentación Kestra](https://kestra.io/docs)
- [RFC 5545 - iCalendar](https://tools.ietf.org/html/rfc5545)
- [Google Calendar API](https://developers.google.com/calendar)
- [Microsoft Graph Calendar API](https://learn.microsoft.com/en-us/graph/api/resources/calendar)

## ✨ Nuevas Funcionalidades v2.0

- ✅ **Recordatorios Automáticos**: Configurables con `enable_reminders` y `reminder_minutes_before`
- ✅ **Buffer Time**: Soporte para tiempo de buffer entre reuniones
- ✅ **Intervalos Inteligentes**: Ajusta espacios según duración de reunión
- ✅ **Validación Mejorada**: Detección de duplicados y validación robusta
- ✅ **Documentación Completa**: README detallado con ejemplos

## 🚧 Mejoras Futuras

- [ ] Soporte para timezones múltiples en una misma reunión
- [ ] Detección automática de timezone del usuario
- [ ] Integración con sistemas de videoconferencia adicionales (Zoom, Webex)
- [ ] Dashboard de reuniones programadas
- [ ] Análisis de patrones de disponibilidad
- [ ] Soporte para eventos recurrentes
- [ ] Cancelación automática con notificaciones
- [ ] Múltiples recordatorios (1 día antes, 1 hora antes, etc.)
- [ ] Sincronización bidireccional con calendarios

---

**Última actualización**: 2025-01 | **Versión del Workflow**: 2.0

