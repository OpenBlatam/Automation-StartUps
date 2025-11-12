# 🚀 Quick Start - Chatbots

## Inicio Rápido en 5 Minutos

### 1. Ejecutar un Chatbot (30 segundos)

```bash
cd /Users/adan/IA
python3 scripts/chatbot_curso_ia_webinars.py
```

¡Listo! Ya puedes chatear con el chatbot.

---

### 2. Usar desde Python (1 minuto)

```python
from scripts.chatbot_curso_ia_webinars import CursoIAWebinarChatbot

chatbot = CursoIAWebinarChatbot()
response = chatbot.process_message("¿Cuánto cuesta el curso?")

print(response["response"])
```

---

### 3. Iniciar API REST (2 minutos)

```bash
# Instalar dependencias (opcional)
pip install flask flask-cors

# Iniciar servidor
python3 scripts/chatbot_api.py
```

La API estará en `http://localhost:5000`

**Probar:**
```bash
curl -X POST http://localhost:5000/api/curso_ia/message \
  -H "Content-Type: application/json" \
  -d '{"message": "¿Cuánto cuesta el curso?"}'
```

---

### 4. Con Docker (3 minutos)

```bash
# Construir imagen
docker build -f scripts/Dockerfile.chatbot -t chatbot:latest .

# Ejecutar
docker run -p 5000:5000 chatbot:latest
```

O con docker-compose:
```bash
docker-compose -f scripts/docker-compose.chatbot.yml up
```

---

## 📋 Comandos Útiles

### Modo Interactivo

Cuando ejecutes un chatbot, estos comandos están disponibles:

- `métricas` - Ver estadísticas
- `tendencias` - Ver análisis de tendencias  
- `sugerencias` - Ver sugerencias de IA
- `health check` - Verificar estado
- `feedback positive/negative` - Dar feedback
- `exportar métricas json` - Exportar métricas
- `salir` - Terminar

---

## 🎯 Casos de Uso Comunes

### Caso 1: Respuesta Simple

```python
chatbot = CursoIAWebinarChatbot()
response = chatbot.process_message("¿Cuánto cuesta?")
print(response["response"])
```

### Caso 2: Conversación con Contexto

```python
history = []
response1 = chatbot.process_message("¿Cuánto cuesta?", history)
history.append({"role": "user", "content": "¿Cuánto cuesta?"})
history.append({"role": "assistant", "content": response1["response"]})

response2 = chatbot.process_message("¿Y qué incluye?", history)
```

### Caso 3: Obtener Métricas

```python
metrics = chatbot.get_metrics()
print(f"Mensajes: {metrics['total_messages']}")
print(f"Escalaciones: {metrics['total_escalations']}")
```

### Caso 4: Health Check

```python
health = chatbot.health_check()
if health['status'] != 'healthy':
    print("⚠️ Problemas detectados:", health['issues'])
```

---

## 🔧 Configuración Rápida

### Variables de Entorno

```bash
export CHATBOT_ENABLE_LOGGING=true
export CHATBOT_PERSIST_CONVERSATIONS=true
export CHATBOT_ENABLE_RATE_LIMITING=true
export CHATBOT_RATE_LIMIT_MAX=100
```

### Archivo de Configuración

```python
from chatbot_config import ConfigManager

config_manager = ConfigManager()
config = config_manager.get_config("curso_ia")

# Modificar
config.cache_max_size = 200
config_manager.set_config("curso_ia", config)
```

---

## 📊 Ver Resultados

### Logs
```bash
tail -f chatbot_curso_ia.log
```

### Conversaciones Guardadas
```bash
ls chatbot_conversations/
cat chatbot_conversations/conv_*.json
```

### Métricas Exportadas
```bash
ls chatbot_*_metrics_*.json
```

---

## 🆘 Problemas Comunes

### "Module not found"
```bash
# Asegúrate de estar en el directorio correcto
cd /Users/adan/IA
python3 scripts/chatbot_curso_ia_webinars.py
```

### "Rate Limited"
Espera unos minutos o ajusta el límite en la configuración.

### API no responde
Verifica que Flask esté instalado:
```bash
pip install flask flask-cors
```

---

## 📚 Más Información

- **Documentación completa**: `scripts/README_CHATBOTS.md`
- **Lista de funcionalidades**: `scripts/CHATBOT_FEATURES_COMPLETE.md`
- **Ejemplos de integración**: `scripts/examples/integration_example.py`

---

## ✅ Checklist de Inicio

- [ ] Python 3.7+ instalado
- [ ] Scripts de chatbot ejecutables
- [ ] Directorio `chatbot_conversations/` creado
- [ ] (Opcional) Flask instalado para API
- [ ] (Opcional) Docker instalado para containers

---

**¡Listo para empezar! 🎉**






