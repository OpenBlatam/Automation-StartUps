# 🔧 Sistema de Troubleshooting Automatizado para Soporte Técnico

## 📋 Resumen Ejecutivo

Sistema completo de automatización de troubleshooting que guía a los clientes paso a paso para resolver problemas técnicos comunes, ahorrando tiempo en tickets repetitivos y mejorando la experiencia del cliente.

### Características Principales

- ✅ **Detección automática de problemas** - Identifica problemas comunes en la descripción del cliente
- ✅ **Guía paso a paso** - Instrucciones claras y accesibles para no técnicos
- ✅ **Precauciones y advertencias** - Información de seguridad y mejores prácticas
- ✅ **Enlaces a recursos** - Documentación y guías relacionadas
- ✅ **Sugerencia de escalación** - Escala automáticamente si el problema no se resuelve
- ✅ **Integración con tickets** - Se integra perfectamente con el sistema de tickets existente
- ✅ **API REST completa** - Endpoints para iniciar y gestionar sesiones de troubleshooting
- ✅ **Base de conocimiento extensible** - Fácil agregar nuevos problemas y soluciones

## 🏗️ Arquitectura

```
┌─────────────────────────────────────────────────────────┐
│              Cliente / Usuario Final                     │
│  (Web, Email, Chat, API, etc.)                          │
└────────────────────┬────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────┐
│              API REST (Next.js)                          │
│  POST /api/support/troubleshooting/start                 │
│  GET  /api/support/troubleshooting/:sessionId            │
│  POST /api/support/troubleshooting/:sessionId/step       │
└────────────────────┬────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────┐
│         Workflow Kestra                                  │
│  support_troubleshooting_automation.yaml                 │
│  - Detecta problema                                     │
│  - Inicia sesión                                        │
│  - Envía respuesta inicial                              │
└────────────────────┬────────────────────────────────────┘
                     │
        ┌────────────┴────────────┐
        │                         │
        ▼                         ▼
┌──────────────────┐    ┌──────────────────┐
│  Agente Python   │    │  Base de Datos   │
│  Troubleshooting │    │  PostgreSQL      │
│  Agent           │    │  - Sesiones      │
│                  │    │  - Intentos     │
│  - Detecta       │    │  - Estadísticas  │
│  - Guía pasos    │    └──────────────────┘
│  - Escala        │
└──────────────────┘
        │
        ▼
┌──────────────────┐
│  Base de         │
│  Conocimiento    │
│  (JSON)          │
│  - Problemas     │
│  - Soluciones    │
│  - Pasos         │
└──────────────────┘
```

## 📦 Componentes

### 1. Agente de Troubleshooting (`support_troubleshooting_agent.py`)

Motor principal que:
- Detecta problemas en la descripción del usuario
- Inicia y gestiona sesiones de troubleshooting
- Proporciona pasos guiados
- Monitorea el progreso
- Sugiere escalación cuando es necesario

**Ubicación**: `data/integrations/support_troubleshooting_agent.py`

**Clases principales**:
- `TroubleshootingAgent` - Agente principal
- `TroubleshootingSession` - Sesión activa
- `TroubleshootingGuide` - Guía de un problema
- `TroubleshootingStep` - Paso individual

### 2. Base de Conocimiento (`support_troubleshooting_kb.json`)

Archivo JSON con problemas comunes y sus soluciones paso a paso.

**Estructura**:
```json
{
  "problema_id": {
    "problem_title": "Título del problema",
    "problem_description": "Descripción",
    "category": "categoría",
    "estimated_time": "15 minutos",
    "difficulty": "fácil|medio|avanzado",
    "steps": [
      {
        "step_number": 1,
        "title": "Título del paso",
        "description": "Descripción",
        "instructions": ["Instrucción 1", "Instrucción 2"],
        "expected_result": "Qué debería pasar",
        "warnings": ["Precaución 1"],
        "resources": [{"title": "Recurso", "url": "https://..."}]
      }
    ],
    "common_issues": ["Problema común 1"],
    "escalation_criteria": ["Cuándo escalar"]
  }
}
```

**Problemas incluidos por defecto**:
- `instalacion_software` - Problemas con instalación
- `conexion_internet` - Problemas de conectividad
- `error_aplicacion` - Errores y cierres inesperados
- `problema_facturacion` - Problemas con pagos
- `recuperar_cuenta` - Problemas de acceso a cuenta

### 3. Workflow de Kestra (`support_troubleshooting_automation.yaml`)

Workflow automatizado que:
- Recibe solicitudes de troubleshooting
- Inicia sesiones
- Detecta problemas
- Envía respuestas iniciales
- Actualiza tickets

**Webhook**: `/api/v1/executions/webhook/workflows/workflows/support-troubleshooting-automation/support-troubleshooting`

### 4. API REST (Next.js)

Endpoints para interactuar con el sistema:

#### Iniciar Troubleshooting
```http
POST /api/support/troubleshooting/start
Content-Type: application/json

{
  "problem_description": "No puedo instalar el software",
  "customer_email": "cliente@example.com",
  "customer_name": "Juan Pérez",
  "ticket_id": "TKT-12345",
  "source": "web"
}
```

**Respuesta**:
```json
{
  "success": true,
  "session_id": "uuid-session-id",
  "ticket_id": "TKT-12345",
  "status": "started",
  "problem_detected": "instalacion_software",
  "message": "Sesión iniciada",
  "first_step": {
    "step_number": 1,
    "title": "Verificar requisitos del sistema",
    "instructions": [...],
    "warnings": [...],
    "resources": [...]
  }
}
```

#### Obtener Estado de Sesión
```http
GET /api/support/troubleshooting?session_id=uuid-session-id
```

#### Completar Paso
```http
POST /api/support/troubleshooting/{sessionId}/step
Content-Type: application/json

{
  "success": true,
  "notes": "Funcionó correctamente",
  "step_number": 1,
  "step_title": "Verificar requisitos del sistema"
}
```

### 5. Base de Datos

**Tablas**:
- `support_troubleshooting_sessions` - Sesiones activas
- `support_troubleshooting_attempts` - Intentos de pasos

**Vistas**:
- `vw_troubleshooting_sessions_summary` - Resumen de sesiones

**Funciones**:
- `get_troubleshooting_stats()` - Estadísticas de troubleshooting

**Esquema**: `data/db/support_troubleshooting_schema.sql`

## 🚀 Inicio Rápido

### 1. Instalación

```bash
# 1. Ejecutar esquema SQL
psql $DATABASE_URL < data/db/support_troubleshooting_schema.sql

# 2. Verificar que el agente Python está disponible
python3 -c "from data.integrations.support_troubleshooting_agent import TroubleshootingAgent; print('OK')"

# 3. Desplegar workflow de Kestra
kestra workflow create workflow/kestra/flows/support_troubleshooting_automation.yaml
```

### 2. Configuración

**Variables de entorno**:
```bash
# Base de datos
DATABASE_URL=postgresql://user:pass@host:5432/dbname

# Kestra
KESTRA_WEBHOOK_URL=https://kestra.example.com/api/v1/executions/webhook

# Notificaciones (opcional)
EMAIL_API_KEY=your-email-api-key
```

### 3. Uso Básico

#### Desde API REST

```python
import requests

# Iniciar troubleshooting
response = requests.post(
    'https://api.example.com/api/support/troubleshooting/start',
    json={
        'problem_description': 'No puedo instalar el software',
        'customer_email': 'cliente@example.com',
        'customer_name': 'Juan Pérez'
    }
)

session_id = response.json()['session_id']

# Obtener paso actual
step_response = requests.get(
    f'https://api.example.com/api/support/troubleshooting?session_id={session_id}'
)

# Completar paso
complete_response = requests.post(
    f'https://api.example.com/api/support/troubleshooting/{session_id}/step',
    json={
        'success': True,
        'step_number': 1
    }
)
```

#### Desde Python

```python
from data.integrations.support_troubleshooting_agent import TroubleshootingAgent

# Inicializar agente
agent = TroubleshootingAgent()

# Iniciar sesión
session = agent.start_troubleshooting(
    problem_description="No puedo conectarme a internet",
    customer_email="cliente@example.com",
    customer_name="Juan Pérez"
)

# Obtener primer paso
first_step = agent.get_current_step(session.session_id)
print(agent.format_step_response(first_step))

# Completar paso
result = agent.complete_step(
    session_id=session.session_id,
    success=True,
    notes="Funcionó correctamente"
)
```

## 📝 Agregar Nuevos Problemas

Para agregar un nuevo problema a la base de conocimiento:

1. **Editar `support_troubleshooting_kb.json`**:
```json
{
  "nuevo_problema": {
    "problem_title": "Título del problema",
    "problem_description": "Descripción del problema",
    "category": "categoría",
    "estimated_time": "20 minutos",
    "difficulty": "medio",
    "prerequisites": ["Requisito 1", "Requisito 2"],
    "steps": [
      {
        "step_number": 1,
        "title": "Paso 1",
        "description": "Descripción del paso",
        "instructions": [
          "Instrucción 1",
          "Instrucción 2"
        ],
        "expected_result": "Resultado esperado",
        "warnings": ["Precaución importante"],
        "resources": [
          {
            "title": "Recurso útil",
            "url": "https://docs.example.com/recurso"
          }
        ]
      }
    ],
    "common_issues": [
      "Problema común 1",
      "Problema común 2"
    ],
    "escalation_criteria": [
      "Criterio de escalación 1"
    ]
  }
}
```

2. **Reiniciar el agente** (si está en memoria) o recargar la base de conocimiento

## 🔍 Monitoreo y Estadísticas

### Consultas SQL Útiles

```sql
-- Resumen de sesiones
SELECT * FROM vw_troubleshooting_sessions_summary
WHERE started_at >= NOW() - INTERVAL '7 days';

-- Estadísticas generales
SELECT * FROM get_troubleshooting_stats(
    NOW() - INTERVAL '30 days',
    NOW()
);

-- Problemas más comunes
SELECT 
    detected_problem_title,
    COUNT(*) as total_sessions,
    COUNT(CASE WHEN status = 'resolved' THEN 1 END) as resolved,
    COUNT(CASE WHEN status = 'escalated' THEN 1 END) as escalated
FROM support_troubleshooting_sessions
WHERE started_at >= NOW() - INTERVAL '30 days'
GROUP BY detected_problem_title
ORDER BY total_sessions DESC;

-- Tasa de resolución por problema
SELECT 
    detected_problem_title,
    COUNT(*) as total,
    COUNT(CASE WHEN status = 'resolved' THEN 1 END) as resolved,
    ROUND(
        COUNT(CASE WHEN status = 'resolved' THEN 1 END)::NUMERIC / 
        COUNT(*)::NUMERIC * 100, 
        2
    ) as resolution_rate_percent
FROM support_troubleshooting_sessions
WHERE started_at >= NOW() - INTERVAL '30 days'
GROUP BY detected_problem_title
ORDER BY resolution_rate_percent DESC;
```

## 🎯 Mejores Prácticas

### Para Desarrolladores

1. **Mantén las instrucciones simples**: Escribe para usuarios no técnicos
2. **Incluye precauciones**: Advierte sobre riesgos potenciales
3. **Proporciona recursos**: Enlaces a documentación relevante
4. **Define criterios de escalación claros**: Cuándo debe escalarse
5. **Prueba los pasos**: Asegúrate de que funcionan antes de agregarlos

### Para Agentes de Soporte

1. **Usa el sistema primero**: Antes de escalar, intenta el troubleshooting
2. **Revisa el historial**: Ve qué pasos ya se intentaron
3. **Actualiza la KB**: Agrega problemas comunes que encuentres
4. **Monitorea estadísticas**: Identifica problemas que necesitan mejoras

## 🔧 Troubleshooting del Sistema

### Problema: No se detecta ningún problema

**Solución**:
1. Verifica que el problema existe en `support_troubleshooting_kb.json`
2. Revisa que las palabras clave coinciden con la descripción
3. Ajusta el umbral de confianza si es necesario (por defecto 30%)

### Problema: Los pasos no se completan

**Solución**:
1. Verifica la conexión a la base de datos
2. Revisa los logs del workflow de Kestra
3. Verifica que la sesión existe en la BD

### Problema: No se envían notificaciones

**Solución**:
1. Verifica `enable_notifications` en el workflow
2. Revisa la configuración del servicio de email
3. Verifica los logs de notificaciones

## 📊 Métricas y KPIs

Métricas importantes a monitorear:

- **Tasa de resolución**: % de sesiones resueltas sin escalación
- **Tiempo promedio**: Tiempo promedio para resolver
- **Problemas más comunes**: Qué problemas aparecen más
- **Tasa de escalación**: % de sesiones que requieren escalación
- **Satisfacción del cliente**: Feedback después de resolver

## 🔗 Integraciones

### Con Sistema de Tickets

El sistema se integra automáticamente con `support_tickets`:
- Crea sesiones vinculadas a tickets
- Actualiza el estado del ticket
- Registra el progreso en metadata

### Con Chatbot

Puede usarse junto con el chatbot existente:
- El chatbot intenta resolver primero
- Si no resuelve, inicia troubleshooting
- Si troubleshooting no resuelve, escala

### Con Notificaciones

Envía notificaciones cuando:
- Se inicia una sesión
- Se completa un paso
- Se requiere escalación
- Se resuelve el problema

## 📚 Recursos Adicionales

- [Sistema de Tickets](./SUPPORT_AUTOMATION.md)
- [Chatbot de Soporte](./README_SUPPORT_AUTOMATION.md)
- [API de Soporte](../web/kpis-next/app/api/support/README.md)

## 🤝 Contribuir

Para agregar nuevos problemas o mejorar existentes:

1. Edita `support_troubleshooting_kb.json`
2. Prueba los pasos manualmente
3. Actualiza la documentación
4. Crea un pull request

## 📞 Soporte

Para problemas o preguntas sobre el sistema de troubleshooting:
1. Revisa esta documentación
2. Consulta los logs del sistema
3. Contacta al equipo de desarrollo

---

**Versión**: 1.0.0  
**Última actualización**: 2025-01-27



