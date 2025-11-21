# 🤖 Sistema de Chatbots - Guía Completa

## 📚 Índice

1. [Introducción](#introducción)
2. [Instalación](#instalación)
3. [Uso Básico](#uso-básico)
4. [Uso Avanzado](#uso-avanzado)
5. [API REST](#api-rest)
6. [Tests](#tests)
7. [Seguridad](#seguridad)
8. [Troubleshooting](#troubleshooting)

---

## 🎯 Introducción

Sistema completo de chatbots con más de 17 funcionalidades avanzadas cada uno, listo para producción.

### Chatbots Disponibles

1. **Curso de IA y Webinars** (`chatbot_curso_ia_webinars.py`)
2. **SaaS de IA para Marketing** (`chatbot_saas_ia_marketing.py`)
3. **IA Bulk para Documentos** (`chatbot_ia_bulk_documentos.py`)

---

## 📦 Instalación

### Requisitos

- Python 3.7+
- Sin dependencias externas requeridas (funciona con librerías estándar)

### Instalación Opcional

Para funcionalidades avanzadas:

```bash
# Para API REST
pip install flask flask-cors

# Para tests
pip install pytest  # o usar unittest incluido
```

---

## 🚀 Uso Básico

### Ejemplo Simple

```python
from chatbot_curso_ia_webinars import CursoIAWebinarChatbot

# Crear instancia
chatbot = CursoIAWebinarChatbot()

# Procesar mensaje
response = chatbot.process_message("¿Cuánto cuesta el curso?")

print(response["response"])
print(f"Confianza: {response['confidence']:.2f}")
```

### Modo Interactivo

```bash
python scripts/chatbot_curso_ia_webinars.py
```

---

## 🔧 Uso Avanzado

### Configuración Completa

```python
chatbot = CursoIAWebinarChatbot(
    enable_logging=True,           # Logging estructurado
    persist_conversations=True,    # Guardar conversaciones
    enable_rate_limiting=True,     # Rate limiting
    enable_feedback=True           # Sistema de feedback
)
```

### Con Historial de Conversación

```python
conversation_history = [
    {"role": "user", "content": "¿Cuánto cuesta?"},
    {"role": "assistant", "content": "El curso cuesta..."}
]

response = chatbot.process_message(
    "¿Y qué incluye?",
    conversation_history=conversation_history
)
```

### Obtener Métricas

```python
metrics = chatbot.get_metrics()
print(f"Total mensajes: {metrics['total_messages']}")
print(f"Tasa de escalación: {metrics['escalation_rate']:.1%}")
```

### Exportar Métricas

```python
# JSON
chatbot.export_metrics(format="json")

# CSV
chatbot.export_metrics(format="csv")
```

### Análisis de Tendencias

```python
trends = chatbot.get_trends(days=7)
print(f"Intención más común: {trends['intent_trends']['most_common_intent']}")
```

### Health Check

```python
health = chatbot.health_check()
if health['status'] != 'healthy':
    for issue in health['issues']:
        print(f"⚠️ {issue}")
```

### Agregar Feedback

```python
chatbot.add_feedback(
    conversation_id="conv_123",
    message_id="msg_1",
    feedback_type="positive",
    comment="Muy útil!"
)
```

---

## 🌐 API REST

### Iniciar Servidor

```bash
python scripts/chatbot_api.py
```

El servidor estará disponible en `http://localhost:5000`

### Endpoints Disponibles

#### Health Check
```bash
GET /health
```

#### Procesar Mensaje
```bash
POST /api/<chatbot_id>/message
Content-Type: application/json

{
    "message": "¿Cuánto cuesta el curso?",
    "user_id": "user123",
    "conversation_history": []
}
```

#### Obtener Métricas
```bash
GET /api/<chatbot_id>/metrics
```

#### Health Check del Chatbot
```bash
GET /api/<chatbot_id>/health
```

#### Agregar Feedback
```bash
POST /api/<chatbot_id>/feedback
Content-Type: application/json

{
    "conversation_id": "conv_123",
    "message_id": "msg_1",
    "feedback_type": "positive",
    "comment": "Muy útil"
}
```

#### Obtener Tendencias
```bash
GET /api/<chatbot_id>/trends?days=7
```

#### Obtener Sugerencias
```bash
GET /api/<chatbot_id>/suggestions
```

#### Documentación
```bash
GET /api/docs
```

### Ejemplo con cURL

```bash
curl -X POST http://localhost:5000/api/curso_ia/message \
  -H "Content-Type: application/json" \
  -d '{"message": "¿Cuánto cuesta el curso?"}'
```

---

## 🧪 Tests

### Ejecutar Tests

```bash
python scripts/test_chatbot.py
```

### Tests Incluidos

- ✅ Inicialización
- ✅ Detección de intención
- ✅ Búsqueda de FAQ
- ✅ Procesamiento de mensajes
- ✅ Validación de entrada
- ✅ Detección de escalación
- ✅ Métricas
- ✅ Cache
- ✅ Rate limiting
- ✅ Sistema de feedback
- ✅ Health check
- ✅ Exportación de métricas

---

## 🔒 Seguridad

### Validador de Seguridad

```python
from chatbot_security import SecurityValidator

validator = SecurityValidator()

# Validar entrada
is_valid, error = validator.validate_input(user_message)
if not is_valid:
    print(f"Error: {error}")

# Sanitizar entrada
sanitized = validator.sanitize_input(user_message)
```

### Protecciones Incluidas

- ✅ Protección contra SQL Injection
- ✅ Protección contra XSS
- ✅ Protección contra Command Injection
- ✅ Validación de longitud
- ✅ Sanitización de entrada
- ✅ Rate limiting por usuario

---

## 🐛 Troubleshooting

### Problema: "Module not found"

**Solución**: Asegúrate de estar en el directorio correcto:
```bash
cd /Users/adan/IA
python scripts/chatbot_curso_ia_webinars.py
```

### Problema: Rate Limited

**Solución**: Espera unos minutos o ajusta el límite:
```python
from chatbot_advanced_features import RateLimitConfig

config = RateLimitConfig(max_requests=100, time_window=60)
```

### Problema: Cache muy grande

**Solución**: Reducir tamaño del cache:
```python
chatbot.cache_max_size = 50
```

### Problema: Logs no aparecen

**Solución**: Verificar permisos de escritura:
```bash
touch chatbot_curso_ia.log
chmod 666 chatbot_curso_ia.log
```

---

## 📊 Comandos Interactivos

Cuando uses el modo interactivo, estos comandos están disponibles:

- `métricas` - Ver estadísticas
- `exportar métricas json` - Exportar a JSON
- `exportar métricas csv` - Exportar a CSV
- `tendencias` - Ver análisis de tendencias
- `sugerencias` - Ver sugerencias de IA
- `health check` - Verificar estado
- `feedback positive/negative/helpful/not_helpful` - Dar feedback
- `resumen conversación <id>` - Ver resumen
- `salir` - Terminar

---

## 📈 Métricas y Monitoreo

### Métricas Disponibles

- Total de mensajes
- Tasa de escalación
- Confianza promedio
- Tiempo de procesamiento
- Tasa de match de FAQs
- Distribución de intenciones

### Archivos Generados

- `chatbot_*.log` - Logs
- `chatbot_conversations/*.json` - Conversaciones
- `chatbot_feedback.json` - Feedback
- `chatbot_*_metrics_*.json/csv` - Métricas exportadas

---

## 🔗 Integración

### Con Flask/Django

```python
from chatbot_curso_ia_webinars import CursoIAWebinarChatbot

chatbot = CursoIAWebinarChatbot()

@app.route('/chat', methods=['POST'])
def chat():
    data = request.json
    response = chatbot.process_message(data['message'])
    return jsonify(response)
```

### Con FastAPI

```python
from fastapi import FastAPI
from chatbot_curso_ia_webinars import CursoIAWebinarChatbot

app = FastAPI()
chatbot = CursoIAWebinarChatbot()

@app.post("/chat")
async def chat(message: str):
    return chatbot.process_message(message)
```

---

## 📚 Documentación Adicional

- `CHATBOT_MEJORAS.md` - Detalles de mejoras
- `CHATBOT_FEATURES_COMPLETE.md` - Lista completa de funcionalidades
- Código fuente con docstrings completos

---

## 🆘 Soporte

Para problemas o preguntas:
1. Revisa los logs en `chatbot_*.log`
2. Ejecuta `health check` en modo interactivo
3. Revisa la documentación en los archivos `.md`

---

**Versión**: 2.0  
**Última actualización**: 2024  
**Estado**: ✅ Producción Ready






