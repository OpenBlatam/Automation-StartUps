# 🔌 Guía de Integración - Chatbots

## Integración Rápida en 3 Pasos

### Paso 1: Importar (10 segundos)

```python
from chatbot_curso_ia_webinars import CursoIAWebinarChatbot
```

### Paso 2: Inicializar (5 segundos)

```python
chatbot = CursoIAWebinarChatbot()
```

### Paso 3: Usar (1 segundo)

```python
response = chatbot.process_message("¿Cuánto cuesta?")
print(response["response"])
```

---

## 🔗 Integraciones Comunes

### 1. Flask/Django Web App

```python
from flask import Flask, request, jsonify
from chatbot_curso_ia_webinars import CursoIAWebinarChatbot

app = Flask(__name__)
chatbot = CursoIAWebinarChatbot()

@app.route('/chat', methods=['POST'])
def chat():
    data = request.json
    response = chatbot.process_message(data['message'])
    return jsonify(response)
```

### 2. FastAPI

```python
from fastapi import FastAPI
from chatbot_curso_ia_webinars import CursoIAWebinarChatbot

app = FastAPI()
chatbot = CursoIAWebinarChatbot()

@app.post("/chat")
async def chat(message: str):
    return chatbot.process_message(message)
```

### 3. Webhook (Zapier, n8n, etc.)

```python
def webhook_handler(request_data):
    message = request_data.get('message')
    user_id = request_data.get('user_id')
    
    chatbot = CursoIAWebinarChatbot()
    response = chatbot.process_message(message, user_id=user_id)
    
    return {
        "reply": response["response"],
        "confidence": response["confidence"],
        "escalate": response["requires_escalation"]
    }
```

### 4. Telegram Bot

```python
import telegram
from chatbot_curso_ia_webinars import CursoIAWebinarChatbot

bot = telegram.Bot(token="YOUR_TOKEN")
chatbot = CursoIAWebinarChatbot()

def handle_message(update, context):
    user_message = update.message.text
    response = chatbot.process_message(user_message)
    update.message.reply_text(response["response"])
```

### 5. WhatsApp (via Twilio/WhatsApp Business API)

```python
from twilio.rest import Client
from chatbot_curso_ia_webinars import CursoIAWebinarChatbot

client = Client(account_sid, auth_token)
chatbot = CursoIAWebinarChatbot()

def handle_whatsapp(message_body, from_number):
    response = chatbot.process_message(message_body)
    client.messages.create(
        body=response["response"],
        from_='whatsapp:+14155238886',
        to=f'whatsapp:{from_number}'
    )
```

### 6. Slack Bot

```python
from slack_bolt import App
from chatbot_curso_ia_webinars import CursoIAWebinarChatbot

app = App(token="YOUR_TOKEN")
chatbot = CursoIAWebinarChatbot()

@app.message("")
def message_handler(message, say):
    response = chatbot.process_message(message['text'])
    say(response["response"])
```

### 7. Discord Bot

```python
import discord
from chatbot_curso_ia_webinars import CursoIAWebinarChatbot

client = discord.Client()
chatbot = CursoIAWebinarChatbot()

@client.event
async def on_message(message):
    if message.author == client.user:
        return
    
    response = chatbot.process_message(message.content)
    await message.channel.send(response["response"])
```

---

## 🎨 Personalización

### Cambiar FAQs

```python
# Modificar directamente en el código
chatbot.faqs[0]['answer'] = "Tu nueva respuesta aquí"
```

### Agregar Nuevas FAQs

```python
new_faq = {
    "id": "faq_013",
    "category": "nueva_categoria",
    "question": "¿Nueva pregunta?",
    "answer": "Nueva respuesta completa...",
    "keywords": ["palabra1", "palabra2"]
}
chatbot.faqs.append(new_faq)
```

### Configurar Rate Limits

```python
from chatbot_advanced_features import RateLimitConfig

config = RateLimitConfig(
    max_requests=100,  # Más requests
    time_window=60,
    block_duration=300
)
```

---

## 📊 Monitoreo

### Métricas en Tiempo Real

```python
metrics = chatbot.get_metrics()
print(f"Mensajes: {metrics['total_messages']}")
print(f"Escalaciones: {metrics['total_escalations']}")
```

### Health Check

```python
health = chatbot.health_check()
if health['status'] != 'healthy':
    # Enviar alerta
    send_alert(health['issues'])
```

### Exportar Métricas

```python
# Programar exportación diaria
chatbot.export_metrics(format="json")
```

---

## 🔄 Flujos de Trabajo

### Flujo Básico

```
Usuario → Chatbot → Respuesta
              ↓
         ¿Escalación?
              ↓
         Agente Humano
```

### Flujo con Feedback

```
Usuario → Chatbot → Respuesta
              ↓
         Feedback
              ↓
         Mejora Automática
```

### Flujo con Cache

```
Usuario → Cache Check → ¿Hit?
              ↓ No
         Procesamiento
              ↓
         Guardar en Cache
```

---

## 🎯 Mejores Prácticas

1. **Usar historial de conversación** para contexto
2. **Implementar rate limiting** en producción
3. **Monitorear métricas** regularmente
4. **Recopilar feedback** para mejoras
5. **Exportar métricas** periódicamente
6. **Health checks** automáticos
7. **Logs estructurados** para debugging

---

## 🆘 Troubleshooting

### Problema: Respuestas lentas
**Solución**: Habilitar cache, optimizar FAQs

### Problema: Muchas escalaciones
**Solución**: Agregar más FAQs, mejorar detección de intención

### Problema: Rate limited
**Solución**: Ajustar límites en configuración

---

**Para más detalles, consulta `README_CHATBOTS.md`**





