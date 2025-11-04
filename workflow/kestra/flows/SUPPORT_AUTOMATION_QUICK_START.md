# 🚀 Quick Start - Sistema de Automatización de Soporte

Guía rápida para poner en marcha el sistema de automatización de soporte.

## Paso 1: Crear Esquema de Base de Datos

```bash
psql -U postgres -d your_database -f data/db/support_tickets_schema.sql
```

## Paso 2: Cargar FAQs de Ejemplo

```bash
psql -U postgres -d your_database -f data/db/support_faq_seed.sql
```

## Paso 3: Configurar Agentes y Reglas

```bash
# Configurar variables de entorno
export DB_HOST=localhost
export DB_NAME=support_db
export DB_USER=postgres
export DB_PASSWORD=your_password

# Ejecutar script de setup
python scripts/support_setup_example.py
```

## Paso 4: Configurar Variables en Kestra

En la UI de Kestra o mediante API, configurar las variables del workflow:

```yaml
# Base de datos
jdbc_url: "jdbc:postgresql://localhost:5432/support_db"
jdbc_user: "postgres"
jdbc_password: "your_password"
enable_db_persistence: true

# Chatbot (opcional pero recomendado)
openai_api_key: "sk-..."
openai_model: "gpt-4o-mini"
enable_chatbot: true
chatbot_confidence_threshold: 0.7

# Notificaciones (opcional)
slack_webhook_url: "https://hooks.slack.com/services/..."
enable_notifications: true
```

## Paso 5: Probar el Webhook

```bash
curl -X POST https://kestra.example.com/api/v1/executions/webhook/workflows/support_ticket_automation/support-ticket \
  -H "Content-Type: application/json" \
  -d '{
    "subject": "Problema con mi factura",
    "description": "No puedo descargar mi factura del mes pasado",
    "customer_email": "cliente@example.com",
    "customer_name": "Juan Pérez",
    "source": "web",
    "category": "billing"
  }'
```

## Paso 6: Verificar Resultados

```sql
-- Ver tickets creados
SELECT ticket_id, subject, priority, status, assigned_department 
FROM support_tickets 
ORDER BY created_at DESC 
LIMIT 10;

-- Ver interacciones con chatbot
SELECT ticket_id, intent_detected, resolved_by_chatbot, confidence_score
FROM support_chatbot_interactions
ORDER BY created_at DESC
LIMIT 10;

-- Verificar agentes
SELECT agent_id, agent_name, department, is_available, current_active_tickets
FROM support_agents;
```

## Paso 7: Activar Monitoreo (Opcional)

El DAG de Airflow `support_tickets_monitor` se ejecutará automáticamente cada 15 minutos si está configurado.

Para ejecutar manualmente:
```bash
airflow dags trigger support_tickets_monitor
```

## ✅ Checklist de Verificación

- [ ] Esquema de BD creado
- [ ] FAQs cargados (al menos 3-5 artículos)
- [ ] Agentes configurados (al menos 2-3 agentes)
- [ ] Reglas de enrutamiento creadas
- [ ] Variables de Kestra configuradas
- [ ] Webhook probado exitosamente
- [ ] Ticket creado en BD
- [ ] Chatbot funcionando (si OpenAI está configurado)
- [ ] Priorización calculada correctamente
- [ ] Enrutamiento funcionando

## 🔧 Troubleshooting Rápido

### El chatbot no responde
- Verificar que hay FAQs en la BD: `SELECT COUNT(*) FROM support_faq_articles;`
- Verificar API key de OpenAI si está habilitado
- Revisar logs de Kestra

### Priorización incorrecta
- Verificar factores en `urgency_factors` del ticket
- Ajustar pesos en `support_priority.py` si es necesario

### Enrutamiento no funciona
- Verificar reglas: `SELECT * FROM support_routing_rules WHERE is_active = true;`
- Verificar agentes disponibles: `SELECT * FROM support_agents WHERE is_available = true;`

### No se guarda en BD
- Verificar conexión JDBC en Kestra
- Verificar permisos de usuario de BD
- Revisar logs de errores en Kestra

## 📖 Próximos Pasos

1. Personalizar FAQs según tu negocio
2. Agregar más agentes según necesidad
3. Ajustar reglas de enrutamiento
4. Configurar notificaciones (Slack/Teams)
5. Integrar con HubSpot si lo usas
6. Revisar métricas en el DAG de monitoreo
7. Ajustar umbrales de priorización según tus necesidades

## 📚 Documentación Completa

Ver [README_SUPPORT_AUTOMATION.md](README_SUPPORT_AUTOMATION.md) para documentación detallada.

