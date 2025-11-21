# 📚 Casos de Uso Avanzados - Sistema de Troubleshooting

## Casos de Uso Reales

### Caso 1: E-commerce - Problemas de Pago

**Escenario**: Cliente no puede completar una compra.

**Implementación**:
```python
# Agregar a knowledge base
{
  "problema_pago_ecommerce": {
    "problem_title": "No puedo completar mi compra",
    "problem_description": "El cliente tiene problemas al intentar pagar",
    "category": "facturación",
    "steps": [
      {
        "step_number": 1,
        "title": "Verificar método de pago",
        "instructions": [
          "Revisa que tu tarjeta no haya expirado",
          "Verifica que tienes fondos suficientes",
          "Confirma que los datos de facturación son correctos"
        ]
      },
      {
        "step_number": 2,
        "title": "Limpiar caché del navegador",
        "instructions": [
          "Presiona Ctrl+Shift+Delete (Windows) o Cmd+Shift+Delete (Mac)",
          "Selecciona 'Cookies' y 'Caché'",
          "Haz clic en 'Eliminar datos'",
          "Intenta la compra nuevamente"
        ]
      }
    ]
  }
}
```

### Caso 2: SaaS - Problemas de Integración API

**Escenario**: Cliente necesita integrar nuestra API con su sistema.

**Implementación con Plantilla**:
```python
template_manager.create_template(
    template_id="api_integration_custom",
    name="Integración API - {{api_name}}",
    description="Guía para integrar {{api_name}} con nuestra API",
    category="configuración",
    variables=[
        {"name": "api_name", "required": True},
        {"name": "api_endpoint", "required": True},
        {"name": "auth_method", "default": "Bearer Token"}
    ],
    steps_template=[...]
)

# Usar la plantilla
rendered = template_manager.render_template(
    "api_integration_custom",
    {
        "api_name": "Mi Sistema CRM",
        "api_endpoint": "https://api.example.com/v1",
        "auth_method": "Bearer Token"
    }
)
```

### Caso 3: Soporte Multi-Idioma

**Escenario**: Clientes en diferentes países necesitan soporte.

**Implementación**:
```python
# Detectar idioma del problema
def detect_language(text: str) -> str:
    # Usar biblioteca de detección de idioma
    from langdetect import detect
    return detect(text)

# Cargar KB según idioma
agent_es = TroubleshootingAgent(
    knowledge_base_path="data/integrations/support_troubleshooting_kb_es.json"
)
agent_en = TroubleshootingAgent(
    knowledge_base_path="data/integrations/support_troubleshooting_kb_en.json"
)

# Seleccionar agente según idioma
language = detect_language(problem_description)
agent = agent_es if language == 'es' else agent_en
```

### Caso 4: Integración con Chatbot Existente

**Escenario**: Integrar con chatbot de WhatsApp o Telegram.

**Implementación**:
```python
def handle_whatsapp_message(message: str, customer_id: str):
    agent = TroubleshootingAgent()
    
    # Intentar resolver con chatbot primero
    chatbot_response = chatbot.process_message(message)
    
    if chatbot_response.confidence < 0.7:
        # Si el chatbot no está seguro, iniciar troubleshooting
        session = agent.start_troubleshooting(
            problem_description=message,
            customer_email=f"{customer_id}@whatsapp.local"
        )
        
        step = agent.get_current_step(session.session_id)
        return agent.format_step_response(step)
    
    return chatbot_response.text
```

### Caso 5: Escalación Inteligente

**Escenario**: Escalar automáticamente según tipo de cliente.

**Implementación**:
```python
def should_escalate_immediately(session: TroubleshootingSession, customer_tier: str) -> bool:
    # Clientes VIP siempre escalar inmediatamente
    if customer_tier == "VIP":
        return True
    
    # Clientes Enterprise después de 1 fallo
    if customer_tier == "Enterprise":
        failed_steps = sum(1 for a in session.attempted_steps if not a.get("success"))
        return failed_steps >= 1
    
    # Clientes normales después de 2 fallos (comportamiento por defecto)
    return False
```

### Caso 6: A/B Testing de Guías

**Escenario**: Probar diferentes versiones de guías para mejorar efectividad.

**Implementación**:
```python
def get_step_with_ab_test(session_id: str, variant: str = None):
    agent = TroubleshootingAgent()
    session = agent.active_sessions.get(session_id)
    
    if not session or not session.detected_problem:
        return None
    
    step = session.detected_problem.steps[session.current_step]
    
    # Variante A: Instrucciones detalladas
    # Variante B: Instrucciones concisas
    if variant == "A":
        return format_detailed_step(step)
    elif variant == "B":
        return format_concise_step(step)
    else:
        # Asignar aleatoriamente
        import random
        variant = random.choice(["A", "B"])
        return get_step_with_ab_test(session_id, variant)
```

### Caso 7: Notificaciones Proactivas

**Escenario**: Notificar al cliente cuando hay actualizaciones.

**Implementación**:
```python
def send_proactive_update(session_id: str, update_type: str):
    agent = TroubleshootingAgent()
    session = agent.active_sessions.get(session_id)
    
    if not session:
        return
    
    notification_manager = TroubleshootingNotificationManager()
    
    if update_type == "step_reminder":
        # Recordatorio si no hay actividad en 1 hora
        config = NotificationConfig(
            channel=NotificationChannel.EMAIL,
            recipient=session.customer_email,
            template="step_reminder"
        )
        notification_manager.send_notification(config, {
            "customer_name": session.customer_name,
            "current_step": session.current_step,
            "session_id": session_id
        })
```

### Caso 8: Análisis Predictivo

**Escenario**: Predecir qué problemas necesitarán escalación.

**Implementación**:
```python
def predict_escalation_risk(session: TroubleshootingSession) -> float:
    """Calcula probabilidad de escalación (0.0 a 1.0)"""
    risk_score = 0.0
    
    # Factor 1: Pasos fallidos
    failed_steps = sum(1 for a in session.attempted_steps if not a.get("success"))
    risk_score += failed_steps * 0.2
    
    # Factor 2: Tiempo transcurrido
    elapsed_hours = (datetime.now() - session.started_at).total_seconds() / 3600
    if elapsed_hours > 2:
        risk_score += 0.3
    
    # Factor 3: Problema conocido por tener alta tasa de escalación
    if session.detected_problem:
        # Consultar estadísticas históricas
        escalation_rate = get_historical_escalation_rate(
            session.detected_problem.problem_id
        )
        risk_score += escalation_rate * 0.5
    
    return min(risk_score, 1.0)
```

### Caso 9: Integración con CRM

**Escenario**: Sincronizar datos con HubSpot/Salesforce.

**Implementación**:
```python
def sync_to_crm(session: TroubleshootingSession, crm_type: str = "hubspot"):
    if crm_type == "hubspot":
        import requests
        
        # Crear/actualizar contacto
        contact_data = {
            "properties": {
                "email": session.customer_email,
                "firstname": session.customer_name.split()[0] if session.customer_name else "",
                "lastname": " ".join(session.customer_name.split()[1:]) if session.customer_name else "",
                "troubleshooting_session_id": session.session_id,
                "troubleshooting_status": session.status.value
            }
        }
        
        requests.post(
            f"https://api.hubapi.com/contacts/v1/contact",
            headers={"Authorization": f"Bearer {HUBSPOT_TOKEN}"},
            json=contact_data
        )
```

### Caso 10: Dashboard Personalizado por Rol

**Escenario**: Diferentes vistas según el rol del usuario.

**Implementación**:
```typescript
// Componente React
function RoleBasedDashboard({ userRole }: { userRole: string }) {
  if (userRole === 'admin') {
    return <AdminDashboard />;
  } else if (userRole === 'agent') {
    return <AgentDashboard />;
  } else if (userRole === 'manager') {
    return <ManagerDashboard />;
  }
  return <BasicDashboard />;
}
```

## Patrones de Integración

### Patrón 1: Webhook Chain

```python
# Cuando se resuelve una sesión, disparar múltiples webhooks
def on_session_resolved(session_id: str):
    webhook_manager.trigger_webhook(
        WebhookEvent.SESSION_RESOLVED,
        get_session_data(session_id)
    )
    
    # También notificar a CRM
    sync_to_crm(session_id)
    
    # Y enviar encuesta de satisfacción
    send_satisfaction_survey(session_id)
```

### Patrón 2: Fallback Chain

```python
def resolve_problem(description: str):
    # 1. Intentar con chatbot
    chatbot_result = chatbot.process(description)
    if chatbot_result.confidence > 0.8:
        return chatbot_result
    
    # 2. Intentar con troubleshooting
    session = agent.start_troubleshooting(description)
    if session.detected_problem:
        return get_first_step(session)
    
    # 3. Escalar a humano
    return escalate_to_human(description)
```

### Patrón 3: Caching Inteligente

```python
def get_cached_problem_detection(description: str):
    cache_key = f"detection_{hash(description)}"
    
    # Verificar cache
    cached = get_from_cache(cache_key)
    if cached:
        return cached
    
    # Detectar problema
    result = agent.detect_problem(description)
    
    # Guardar en cache (1 hora)
    save_to_cache(cache_key, result, ttl=3600)
    
    return result
```

## Mejores Prácticas por Caso de Uso

### E-commerce
- Priorizar problemas de pago
- Integrar con sistema de pagos
- Notificaciones inmediatas

### SaaS
- Enfoque en integraciones
- Documentación técnica detallada
- Soporte para desarrolladores

### B2B Enterprise
- Escalación rápida
- SLA estrictos
- Reportes personalizados

### B2C
- Autoservicio primero
- Guías muy simples
- Feedback continuo

---

**Versión**: 1.0.0  
**Última actualización**: 2025-01-27



