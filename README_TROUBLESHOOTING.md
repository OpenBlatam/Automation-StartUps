# 🔧 Sistema de Troubleshooting Automatizado - Documentación Completa

## 📋 Descripción

Sistema completo de automatización de troubleshooting que guía a los clientes paso a paso para resolver problemas técnicos comunes, ahorrando tiempo en tickets repetitivos y mejorando la experiencia del cliente.

## ✨ Características Principales

- ✅ **Detección Inteligente** - Algoritmo híbrido + LLM para detectar problemas
- ✅ **Guía Paso a Paso** - Instrucciones claras y accesibles para no técnicos
- ✅ **Webhooks** - Integración con sistemas externos
- ✅ **Plantillas Personalizables** - Guías reutilizables con variables
- ✅ **Feedback del Cliente** - Sistema completo de recolección y análisis
- ✅ **Analytics Avanzado** - Métricas en tiempo real y reportes
- ✅ **Notificaciones Multi-Canal** - Email, SMS, Slack, Teams, etc.
- ✅ **Performance Optimizada** - Vistas materializadas, cache, índices
- ✅ **Auditoría Completa** - Log de todas las operaciones
- ✅ **Tests Automatizados** - Suite completa de tests
- ✅ **API REST Completa** - Endpoints documentados
- ✅ **Rate Limiting** - Protección contra abuso
- ✅ **Búsqueda Full-Text** - Búsqueda optimizada en español

## 🚀 Inicio Rápido

### Instalación en 5 Minutos

```bash
# 1. Clonar repositorio
git clone <repo-url>
cd IA

# 2. Instalar dependencias
pip install -r requirements.txt
cd web/kpis-next && npm install && cd ../..

# 3. Configurar base de datos
export DATABASE_URL="postgresql://user:pass@host:5432/dbname"
psql $DATABASE_URL < data/db/support_troubleshooting_schema.sql
psql $DATABASE_URL < data/db/support_troubleshooting_feedback_schema.sql
psql $DATABASE_URL < data/db/support_webhooks_schema.sql
psql $DATABASE_URL < data/db/support_troubleshooting_advanced_schema.sql
psql $DATABASE_URL < data/db/support_troubleshooting_performance_schema.sql

# 4. Configurar variables de entorno
cp .env.example .env
# Editar .env con tus credenciales

# 5. Probar instalación
python3 data/integrations/examples/troubleshooting_example.py
```

### Uso Básico

```python
from data.integrations.support_troubleshooting_agent import TroubleshootingAgent

# Inicializar agente
agent = TroubleshootingAgent(use_llm=True, openai_api_key="sk-...")

# Iniciar troubleshooting
session = agent.start_troubleshooting(
    problem_description="No puedo instalar el software",
    customer_email="cliente@example.com"
)

# Obtener primer paso
step = agent.get_current_step(session.session_id)
print(agent.format_step_response(step))

# Completar paso
result = agent.complete_step(session.session_id, success=True)
```

## 📚 Documentación

### Guías Principales

- **[Guía de Implementación](./docs/IMPLEMENTATION_GUIDE_TROUBLESHOOTING.md)** - Instalación y configuración completa
- **[Documentación API](./docs/API_TROUBLESHOOTING.md)** - Referencia completa de endpoints
- **[Optimizaciones de Performance](./docs/TROUBLESHOOTING_PERFORMANCE_OPTIMIZATION.md)** - Mejoras de velocidad
- **[Características Avanzadas](./docs/TROUBLESHOOTING_ADVANCED_FEATURES.md)** - Webhooks y plantillas
- **[Sistema Completo](./docs/TROUBLESHOOTING_COMPLETE_SYSTEM.md)** - Visión general

### Documentación Técnica

- **[Mejoras Implementadas](./docs/TROUBLESHOOTING_IMPROVEMENTS.md)** - Historial de mejoras
- **[Inicio Rápido](./docs/QUICK_START_TROUBLESHOOTING.md)** - Guía rápida
- **[Troubleshooting del Sistema](./scripts/support_troubleshooting_guide.md)** - Solución de problemas

## 🏗️ Arquitectura

```
┌─────────────────────────────────────────────────────────┐
│              Cliente / Usuario Final                     │
│  (Web, Email, Chat, API, WhatsApp, etc.)                │
└────────────────────┬────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────┐
│              API REST (Next.js)                          │
│  - Troubleshooting                                      │
│  - Webhooks                                            │
│  - Templates                                           │
│  - Notifications                                       │
│  - Analytics                                           │
│  - Realtime Metrics                                    │
└────────────────────┬────────────────────────────────────┘
                     │
        ┌────────────┴────────────┐
        │                         │
        ▼                         ▼
┌──────────────────┐    ┌──────────────────┐
│  Agente Python   │    │  Base de Datos   │
│  - Detección     │    │  - Sesiones      │
│  - Guía pasos    │    │  - Intentos      │
│  - Webhooks      │    │  - Feedback      │
│  - Templates     │    │  - Notificaciones│
│  - Notificaciones│    │  - Reportes      │
│  - Reportes      │    │  - Config        │
│  - Analytics     │    │  - Cache         │
└──────────────────┘    └──────────────────┘
        │
        ▼
┌──────────────────┐
│  Servicios        │
│  - Email          │
│  - SMS            │
│  - Slack          │
│  - Teams          │
│  - OpenAI (LLM)   │
└──────────────────┘
```

## 📦 Componentes

### Core
- `support_troubleshooting_agent.py` - Agente principal
- `support_troubleshooting_kb.json` - Base de conocimiento
- `support_troubleshooting_webhooks.py` - Sistema de webhooks
- `support_troubleshooting_templates.py` - Sistema de plantillas
- `support_troubleshooting_notifications.py` - Notificaciones
- `support_troubleshooting_reports.py` - Reportes

### Base de Datos
- `support_troubleshooting_schema.sql` - Esquema base
- `support_troubleshooting_feedback_schema.sql` - Feedback
- `support_webhooks_schema.sql` - Webhooks
- `support_troubleshooting_advanced_schema.sql` - Avanzado
- `support_troubleshooting_performance_schema.sql` - Performance

### API REST
- `/api/support/troubleshooting/start` - Iniciar sesión
- `/api/support/troubleshooting/:sessionId` - Estado
- `/api/support/troubleshooting/:sessionId/step` - Completar paso
- `/api/support/troubleshooting/:sessionId/feedback` - Feedback
- `/api/support/troubleshooting/analytics` - Analytics
- `/api/support/troubleshooting/realtime` - Métricas en tiempo real
- `/api/support/troubleshooting/webhooks` - Gestión de webhooks
- `/api/support/troubleshooting/templates` - Plantillas

### Tests
- `test_troubleshooting_system.py` - Suite de tests

## 🔧 Configuración

### Variables de Entorno

```bash
# Base de datos
DATABASE_URL=postgresql://user:pass@host:5432/dbname

# LLM (opcional)
OPENAI_API_KEY=sk-...

# Kestra (opcional)
KESTRA_WEBHOOK_URL=https://kestra.example.com/...

# Notificaciones (opcional)
SLACK_WEBHOOK_URL=https://hooks.slack.com/...
TEAMS_WEBHOOK_URL=https://outlook.office.com/webhook/...
EMAIL_API_KEY=your-email-api-key
SMS_API_KEY=your-sms-api-key
```

### Configuración del Sistema

```sql
-- Ver configuración actual
SELECT * FROM support_troubleshooting_config;

-- Actualizar configuración
UPDATE support_troubleshooting_config 
SET config_value = '3', updated_at = NOW() 
WHERE config_key = 'auto_escalate_after_failures';
```

## 📊 Métricas y Monitoreo

### Métricas Disponibles

- Tasa de resolución
- Tiempo promedio de resolución
- Problemas más comunes
- Feedback promedio
- Sesiones activas
- Pasos más problemáticos

### Consultas Útiles

```sql
-- Métricas en tiempo real
SELECT * FROM vw_troubleshooting_realtime_metrics;

-- Resumen diario
SELECT * FROM mv_daily_troubleshooting_summary
WHERE date >= CURRENT_DATE - INTERVAL '7 days';

-- Top problemas
SELECT * FROM mv_top_problems
ORDER BY total_sessions DESC
LIMIT 10;
```

## 🧪 Tests

```bash
# Ejecutar todos los tests
pytest tests/test_troubleshooting_system.py -v

# Con coverage
pytest tests/test_troubleshooting_system.py --cov=data.integrations --cov-report=html

# Test específico
pytest tests/test_troubleshooting_system.py::TestTroubleshootingAgent::test_problem_detection -v
```

## 🚀 Deployment

### Producción

```bash
# 1. Ejecutar migraciones
psql $DATABASE_URL < data/db/support_troubleshooting_schema.sql
# ... (todos los esquemas)

# 2. Configurar mantenimiento automático
psql $DATABASE_URL < data/db/support_troubleshooting_maintenance.sql

# 3. Refresh vistas iniciales
psql $DATABASE_URL -c "SELECT refresh_troubleshooting_views();"

# 4. Iniciar servicios
# API REST
cd web/kpis-next && npm run start

# Workflows (Kestra)
# Configurar según documentación de Kestra
```

### Docker (Opcional)

```dockerfile
# Dockerfile de ejemplo
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["python", "-m", "data.integrations.support_troubleshooting_agent"]
```

## 🔒 Seguridad

### Mejores Prácticas

1. **Autenticación**: Usar Bearer tokens para API
2. **Rate Limiting**: Configurado automáticamente
3. **Webhooks**: Usar firma HMAC para validación
4. **Auditoría**: Todas las operaciones están logueadas
5. **Validación**: Validar inputs en todos los endpoints

### Configuración de Seguridad

```python
# Rate limiting por IP
SELECT check_rate_limit('192.168.1.1', 'api_calls_per_minute', 100, 60);

# Webhook con firma
config = WebhookConfig(
    url="https://example.com/webhook",
    secret="strong-secret-key",  # Usar HMAC
    events=[...]
)
```

## 🤝 Contribuir

1. Fork el repositorio
2. Crea una rama para tu feature (`git checkout -b feature/nueva-funcionalidad`)
3. Commit tus cambios (`git commit -am 'Agregar nueva funcionalidad'`)
4. Push a la rama (`git push origin feature/nueva-funcionalidad`)
5. Abre un Pull Request

### Agregar Nuevo Problema

1. Edita `data/integrations/support_troubleshooting_kb.json`
2. Agrega el problema con sus pasos
3. Prueba manualmente
4. Actualiza documentación si es necesario
5. Crea PR

## 📈 Roadmap

### Próximas Mejoras

- [ ] Soporte multi-idioma completo
- [ ] Integración con más sistemas (Zendesk, Intercom)
- [ ] Dashboard visual interactivo
- [ ] Machine Learning para mejor detección
- [ ] A/B testing de guías
- [ ] Integración con video llamadas
- [ ] Chatbot mejorado con contexto

## 📞 Soporte

Para problemas o preguntas:

1. Revisa la [documentación](./docs/)
2. Consulta los [tests](./tests/) para ejemplos
3. Revisa los [logs](./logs/) del sistema
4. Abre un issue en GitHub

## 📄 Licencia

[Especificar licencia]

## 🙏 Agradecimientos

- OpenAI por GPT para mejoras de detección
- Comunidad de código abierto
- Contribuidores del proyecto

---

**Versión**: 6.0.0  
**Última actualización**: 2025-01-27  
**Mantenido por**: [Tu equipo]



