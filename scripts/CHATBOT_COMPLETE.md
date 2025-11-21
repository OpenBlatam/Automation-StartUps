# 🤖 Sistema de Chatbots - Documentación Completa

## 📋 Tabla de Contenidos

1. [Resumen Ejecutivo](#resumen-ejecutivo)
2. [Instalación Rápida](#instalación-rápida)
3. [Uso Básico](#uso-básico)
4. [Funcionalidades](#funcionalidades)
5. [Integración](#integración)
6. [API REST](#api-rest)
7. [Configuración](#configuración)
8. [Deployment](#deployment)
9. [Monitoreo](#monitoreo)
10. [Troubleshooting](#troubleshooting)

---

## 🎯 Resumen Ejecutivo

Sistema completo de **3 chatbots profesionales** con **20+ funcionalidades avanzadas** cada uno, diseñados para:

- ✅ Reducir tiempos de espera en consultas iniciales
- ✅ Mejorar satisfacción del cliente
- ✅ Proporcionar datos precisos
- ✅ Escalar problemas complejos a agentes humanos

**Estado**: ✅ Producción Ready

---

## ⚡ Instalación Rápida

### Opción 1: Directo (Sin dependencias)

```bash
cd /Users/adan/IA
python3 scripts/chatbot_curso_ia_webinars.py
```

### Opción 2: Con API REST

```bash
pip install flask flask-cors
python3 scripts/chatbot_api.py
```

### Opción 3: Docker

```bash
docker-compose -f scripts/docker-compose.chatbot.yml up
```

---

## 🚀 Uso Básico

### Ejemplo Mínimo

```python
from chatbot_curso_ia_webinars import CursoIAWebinarChatbot

chatbot = CursoIAWebinarChatbot()
response = chatbot.process_message("¿Cuánto cuesta el curso?")

print(response["response"])
```

### Con Configuración

```python
chatbot = CursoIAWebinarChatbot(
    enable_logging=True,
    persist_conversations=True,
    enable_rate_limiting=True,
    enable_feedback=True
)
```

---

## ✨ Funcionalidades

### Core (6)
1. Logging estructurado
2. Persistencia de conversaciones
3. Métricas y estadísticas
4. Manejo de errores
5. Contexto de historial
6. Validación de entrada

### Avanzadas (6)
7. Cache de respuestas
8. Exportación de métricas
9. Análisis de sentimiento
10. Búsqueda mejorada de FAQs
11. Resumen de conversaciones
12. Utilidades compartidas

### Premium (5)
13. Rate limiting
14. Sistema de feedback
15. Análisis de tendencias
16. Sugerencias de IA
17. Health checks

### Infraestructura (3)
18. API REST
19. Tests unitarios
20. Seguridad

---

## 🔌 Integración

Ver `INTEGRATION_GUIDE.md` para ejemplos completos de:
- Flask/Django
- FastAPI
- Webhooks
- Telegram
- WhatsApp
- Slack
- Discord

---

## 🌐 API REST

### Endpoints

- `POST /api/<chatbot_id>/message` - Procesar mensaje
- `GET /api/<chatbot_id>/metrics` - Obtener métricas
- `GET /api/<chatbot_id>/health` - Health check
- `POST /api/<chatbot_id>/feedback` - Agregar feedback
- `GET /api/<chatbot_id>/trends` - Análisis de tendencias
- `GET /api/<chatbot_id>/suggestions` - Sugerencias de IA
- `GET /api/docs` - Documentación

### Ejemplo cURL

```bash
curl -X POST http://localhost:5000/api/curso_ia/message \
  -H "Content-Type: application/json" \
  -d '{"message": "¿Cuánto cuesta el curso?"}'
```

---

## ⚙️ Configuración

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
```

---

## 🚢 Deployment

### Script Automático

```bash
bash scripts/deploy_chatbot.sh
```

### Docker

```bash
docker build -f scripts/Dockerfile.chatbot -t chatbot:latest .
docker run -p 5000:5000 chatbot:latest
```

### Docker Compose

```bash
docker-compose -f scripts/docker-compose.chatbot.yml up -d
```

---

## 📊 Monitoreo

### Métricas

```python
metrics = chatbot.get_metrics()
# Total mensajes, escalaciones, confianza, etc.
```

### Health Check

```python
health = chatbot.health_check()
# Estado, problemas detectados, métricas
```

### Tendencias

```python
trends = chatbot.get_trends(days=7)
# Intenciones, escalaciones, horas pico
```

### Exportación

```python
chatbot.export_metrics(format="json")  # o "csv"
```

---

## 🐛 Troubleshooting

### Problema: Module not found
**Solución**: Asegúrate de estar en `/Users/adan/IA`

### Problema: Rate limited
**Solución**: Espera o ajusta límites en configuración

### Problema: API no responde
**Solución**: Verifica que Flask esté instalado

### Problema: Logs no aparecen
**Solución**: Verifica permisos de escritura

---

## 📚 Documentación Adicional

- `QUICK_START.md` - Inicio en 5 minutos
- `INTEGRATION_GUIDE.md` - Guías de integración
- `CHATBOT_FEATURES_COMPLETE.md` - Todas las funcionalidades
- `INDEX_CHATBOTS.md` - Índice completo
- `CHATBOT_EXECUTIVE_SUMMARY.md` - Resumen ejecutivo

---

## ✅ Checklist de Implementación

- [x] 3 chatbots creados
- [x] 20+ funcionalidades implementadas
- [x] Documentación completa
- [x] Tests unitarios
- [x] API REST
- [x] Docker y deployment
- [x] Seguridad
- [x] Monitoreo
- [x] Ejemplos de integración

---

**Versión**: 2.0  
**Estado**: ✅ Producción Ready  
**Última actualización**: 2024





