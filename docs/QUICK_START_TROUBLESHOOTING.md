# 🚀 Inicio Rápido - Sistema de Troubleshooting Automatizado

## Instalación en 5 Minutos

### Paso 1: Ejecutar el Esquema SQL

```bash
psql $DATABASE_URL < data/db/support_troubleshooting_schema.sql
```

### Paso 2: Verificar Instalación

```bash
# Probar el agente Python
python3 data/integrations/examples/troubleshooting_example.py
```

### Paso 3: Configurar Variables de Entorno

```bash
export DATABASE_URL="postgresql://user:pass@host:5432/dbname"
export KESTRA_WEBHOOK_URL="https://kestra.example.com/api/v1/executions/webhook"
```

### Paso 4: Probar desde API

```bash
# Iniciar troubleshooting
curl -X POST http://localhost:3000/api/support/troubleshooting/start \
  -H "Content-Type: application/json" \
  -d '{
    "problem_description": "No puedo instalar el software",
    "customer_email": "cliente@example.com",
    "customer_name": "Juan Pérez"
  }'
```

## Uso Básico

### Desde Python

```python
from data.integrations.support_troubleshooting_agent import TroubleshootingAgent

# Inicializar
agent = TroubleshootingAgent()

# Iniciar sesión
session = agent.start_troubleshooting(
    problem_description="No puedo conectarme a internet",
    customer_email="cliente@example.com"
)

# Obtener primer paso
step = agent.get_current_step(session.session_id)
print(agent.format_step_response(step))

# Completar paso
result = agent.complete_step(
    session_id=session.session_id,
    success=True
)
```

### Desde API REST

```bash
# 1. Iniciar troubleshooting
SESSION_ID=$(curl -X POST http://localhost:3000/api/support/troubleshooting/start \
  -H "Content-Type: application/json" \
  -d '{"problem_description": "Error al instalar", "customer_email": "test@example.com"}' \
  | jq -r '.session_id')

# 2. Obtener estado
curl "http://localhost:3000/api/support/troubleshooting?session_id=$SESSION_ID"

# 3. Completar paso
curl -X POST "http://localhost:3000/api/support/troubleshooting/$SESSION_ID/step" \
  -H "Content-Type: application/json" \
  -d '{"success": true, "step_number": 1}'
```

## Problemas Comunes Incluidos

El sistema incluye guías para:

1. **Instalación de software** - Problemas al instalar aplicaciones
2. **Conexión a internet** - Problemas de conectividad
3. **Errores de aplicación** - Cierres inesperados y errores
4. **Problemas de facturación** - Pagos y suscripciones
5. **Recuperar cuenta** - Acceso a cuenta

## Próximos Pasos

1. Revisa la [documentación completa](./SUPPORT_TROUBLESHOOTING_AUTOMATION.md)
2. Agrega tus propios problemas a `support_troubleshooting_kb.json`
3. Integra con tu sistema de tickets existente
4. Configura notificaciones por email

## ¿Necesitas Ayuda?

- Revisa los [ejemplos](../data/integrations/examples/troubleshooting_example.py)
- Consulta la [documentación completa](./SUPPORT_TROUBLESHOOTING_AUTOMATION.md)
- Revisa los logs del sistema



