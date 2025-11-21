# 🤖 Sistema Avanzado de Chatbot para Servicio al Cliente

Sistema completo de chatbot inteligente con análisis de sentimientos, detección de intención, A/B testing, integraciones multi-canal y dashboard de métricas en tiempo real.

## 📋 Características Principales

### ✨ Funcionalidades Core
- **Respuestas Inteligentes**: Sistema de matching semántico con FAQs
- **Análisis de Sentimientos**: Detecta positivo, neutral, negativo y frustrado
- **Detección de Intención**: Identifica preguntas, quejas, solicitudes, etc.
- **Contexto Conversacional**: Mantiene historial de hasta 20 mensajes
- **Escalamiento Automático**: Detecta casos críticos y crea tickets automáticamente
- **A/B Testing**: Prueba diferentes variantes de respuestas
- **Multilingüe**: Soporta Español, Inglés, Portugués y Francés

### 🔌 Integraciones
- **Salesforce CRM**: Sincronización automática de leads y casos
- **Zapier**: Webhooks para automatizaciones
- **WhatsApp Business API**: Respuestas por WhatsApp
- **Email (SendGrid)**: Notificaciones y respuestas por email
- **Intercom**: Integración con plataforma de mensajería
- **Dialogflow**: Compatible con Google Dialogflow

### 📊 Dashboard y Métricas
- **Dashboard en Tiempo Real**: Visualización de KPIs y gráficos
- **Métricas Avanzadas**: 
  - Tasa de resolución en primera interacción
  - Satisfacción del cliente (>90% objetivo)
  - Tiempo medio de respuesta (<1 min)
  - Distribución de sentimientos
  - Análisis de intenciones
  - Resultados de A/B testing

### 🎯 Objetivos de Rendimiento
- **Tasa de Resolución**: >80%
- **Satisfacción**: >4.5/5
- **Tiempo de Respuesta**: <60 segundos
- **Automatización**: 85% de interacciones

## 🚀 Instalación

### Requisitos
```bash
pip install flask flask-cors requests
```

### Estructura de Archivos
```
chatbot/
├── chatbot_engine.py      # Motor principal del chatbot
├── dashboard_metrics.py   # Dashboard de métricas
├── api_rest.py           # API REST para integraciones
├── integrations.py       # Integraciones externas
├── chatbot_config.json   # Configuración
├── faqs.json            # Base de conocimiento
├── responses.json       # Respuestas personalizadas
└── escalation_keywords.json  # Palabras clave para escalamiento
```

## 📖 Uso Básico

### 1. Inicializar el Chatbot
```python
from chatbot_engine import ChatbotEngine, ChatMessage, Channel, Language

chatbot = ChatbotEngine()

# Crear mensaje
message = ChatMessage(
    user_id="user_123",
    message="¿Cómo exportar reportes?",
    timestamp=datetime.now(),
    channel=Channel.WEB,
    language=Language.ES
)

# Procesar mensaje
response = await chatbot.process_message(message)
print(response.message)
```

### 2. Usar la API REST
```bash
# Iniciar servidor API
python api_rest.py

# Enviar mensaje
curl -X POST http://localhost:8000/api/v1/chat \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "user_123",
    "message": "¿Cuál es el precio del plan Pro?",
    "channel": "web"
  }'
```

### 3. Ver Dashboard de Métricas
```bash
# Iniciar dashboard
python dashboard_metrics.py

# Abrir en navegador
# http://localhost:5000
```

## 🔧 Configuración

### chatbot_config.json
```json
{
  "company_name": "Tu Empresa",
  "product": "Tu Producto/Servicio",
  "tone": "profesional pero cálido",
  "use_emojis": true,
  "auto_escalate_critical": true,
  "languages": ["es", "en"],
  "channels": ["web", "whatsapp", "email"],
  "settings": {
    "max_conversation_history": 10,
    "confidence_threshold": 0.7,
    "enable_sentiment_analysis": true,
    "enable_ab_testing": true
  },
  "integrations": {
    "crm": {
      "enabled": true,
      "type": "salesforce",
      "instance_url": "https://yourinstance.salesforce.com",
      "client_id": "your_client_id",
      "client_secret": "your_secret",
      "username": "your_username",
      "password": "your_password"
    },
    "zapier": {
      "enabled": true,
      "webhook_url": "https://hooks.zapier.com/hooks/catch/..."
    },
    "whatsapp": {
      "enabled": true,
      "api_key": "your_whatsapp_token",
      "phone_number_id": "your_phone_number_id"
    }
  }
}
```

## 📝 FAQs Personalizadas

Edita `faqs.json` para agregar tus propias preguntas frecuentes:

```json
{
  "es": [
    {
      "id": "faq_001",
      "question": "¿Cómo exportar reportes?",
      "keywords": ["exportar", "reporte", "descargar"],
      "synonyms": ["generar reporte", "obtener reporte"],
      "answer": "Para exportar reportes...",
      "confidence": 0.95,
      "category": "funcionalidad"
    }
  ]
}
```

## 🔄 Integraciones

### Salesforce
```python
from integrations import IntegrationManager

config = {
    "integrations": {
        "crm": {
            "enabled": True,
            "type": "salesforce",
            "instance_url": "...",
            "client_id": "...",
            "client_secret": "...",
            "username": "...",
            "password": "..."
        }
    }
}

manager = IntegrationManager(config)
manager.sync_ticket_to_crm(ticket_id, ticket_data)
```

### Zapier
```python
# El chatbot automáticamente envía eventos a Zapier cuando está configurado
# Configura el webhook URL en chatbot_config.json
```

## 📊 Métricas y Análisis

### Obtener Métricas
```python
metrics = chatbot.get_metrics()
print(f"Tasa de resolución: {metrics['resolution_rate']}%")
print(f"Satisfacción: {metrics['avg_satisfaction']}/5")
print(f"Tiempo de respuesta: {metrics['avg_response_time']}s")
```

### Dashboard Web
Accede al dashboard en `http://localhost:5000` para ver:
- KPIs en tiempo real
- Gráficos de sentimientos
- Distribución de intenciones
- Resultados de A/B testing
- Tendencias de resolución

## 🎯 Plan de Implementación (2 Semanas)

### Semana 1: Configuración y Pruebas
- **Día 1-2**: Configuración inicial y personalización de FAQs
- **Día 3-4**: Integración con canales (web, WhatsApp, email)
- **Día 5**: Pruebas con 100 interacciones iniciales
- **Día 6-7**: Ajustes y optimización

### Semana 2: Integraciones y Optimización
- **Día 8-9**: Integración con CRM (Salesforce)
- **Día 10**: Configuración de Zapier
- **Día 11-12**: A/B Testing y optimización de respuestas
- **Día 13-14**: Análisis de resultados y ajustes finales

## 💰 Estimación de Ahorros

### Métricas Esperadas
- **Reducción de costos de soporte**: 30-40%
- **Automatización**: 85% de interacciones
- **Tiempo de respuesta**: <1 minuto (vs 2-4 horas humano)
- **Disponibilidad**: 24/7 sin costos adicionales

### ROI Estimado
- **Inversión inicial**: Configuración y personalización
- **Ahorro mensual**: 30% de costos de soporte
- **ROI**: Positivo desde el mes 2-3

## 🔍 Análisis y Mejora Continua

### Análisis Semanal
1. Revisar transcripciones del chatbot
2. Identificar preguntas no resueltas
3. Agregar nuevas FAQs
4. Ajustar respuestas según feedback
5. Analizar resultados de A/B testing

### Optimización
- Refinar palabras clave de escalamiento
- Mejorar detección de intención
- Personalizar respuestas según sentimiento
- Ajustar umbrales de confianza

## 🛠️ Troubleshooting

### El chatbot no responde correctamente
1. Verificar que `faqs.json` esté cargado
2. Revisar logs para errores
3. Ajustar `confidence_threshold` en configuración

### Integraciones no funcionan
1. Verificar credenciales en `chatbot_config.json`
2. Revisar logs de integraciones
3. Probar conexiones individualmente

### Dashboard no muestra datos
1. Verificar que el chatbot esté procesando mensajes
2. Revisar que las métricas se estén registrando
3. Verificar conexión a la API

## 📚 Recursos Adicionales

- [Documentación de Salesforce API](https://developer.salesforce.com/docs/atlas.en-us.api_rest.meta/api_rest/)
- [WhatsApp Business API](https://developers.facebook.com/docs/whatsapp)
- [Zapier Webhooks](https://zapier.com/help/create/basics/get-started-with-webhooks)
- [SendGrid API](https://docs.sendgrid.com/api-reference)

## 📞 Soporte

Para preguntas o problemas:
1. Revisar logs del sistema
2. Consultar documentación
3. Contactar al equipo de desarrollo

## 📄 Licencia

Sistema desarrollado para automatización de servicio al cliente.

---

**Versión**: 2.0.0  
**Última actualización**: 2024






