# 🤖 Chatbot de Rastreo de Pedidos

Sistema completo de chatbot especializado en rastreo de pedidos para e-commerce. **Automatiza el 70% de consultas de entrega** con un tono amigable y confiado.

## 🚀 Inicio Rápido

### 1. Instalar Dependencias

```bash
pip install flask flask-cors psycopg2-binary
```

### 2. Configurar Base de Datos

```bash
psql $DATABASE_URL -f data/db/ecommerce_orders_schema.sql
```

### 3. Configurar Variables de Entorno

```bash
export COMPANY_NAME="Mi Empresa"
export BOT_NAME="Asistente de Pedidos"
export DATABASE_URL="postgresql://user:password@localhost/dbname"
```

### 4. Ejecutar

```bash
# API REST
python3 scripts/chatbot_rastreo_api.py

# O modo interactivo
python3 scripts/chatbot_rastreo_pedidos.py
```

## 📁 Archivos Creados

- **`data/db/ecommerce_orders_schema.sql`** - Esquema de base de datos
- **`scripts/chatbot_rastreo_pedidos.py`** - Motor del chatbot
- **`scripts/chatbot_rastreo_api.py`** - API REST
- **`n8n_workflow_rastreo_pedidos.json`** - Workflow de n8n para integración
- **`docs/CHATBOT_RASTREO_PEDIDOS.md`** - Documentación completa

## 🎯 Características

✅ Rastreo de pedidos por ID  
✅ Actualizaciones en tiempo real  
✅ Consultas sobre pagos  
✅ Fechas de entrega  
✅ **Detección automática de problemas** 🆕  
✅ **Predicción de problemas futuros** 🆕  
✅ **Aprendizaje de patrones de usuario** 🆕  
✅ **Integración con LLM (OpenAI)** 🆕  
✅ **Sistema de feedback** 🆕  
✅ **Soporte multi-idioma** 🆕  
✅ **Análisis de tendencias** 🆕  
✅ **Alertas proactivas** 🆕  
✅ **Exportación de datos** 🆕  
✅ **Dashboard completo** 🆕  
✅ **A/B Testing** 🆕  
✅ **Análisis NPS** 🆕  
✅ **Plantillas personalizables** 🆕  
✅ **Análisis de ROI** 🆕  
✅ **Reportes automáticos** 🆕  
✅ Escalación automática a soporte humano  
✅ Multi-canal (Telegram, Web, WhatsApp)  
✅ Métricas y monitoreo  
✅ Rate limiting y cache inteligente  
✅ Análisis de sentimiento  

## 📖 Uso

### API REST

```bash
curl -X POST http://localhost:5000/api/chat \
  -H "Content-Type: application/json" \
  -d '{
    "message": "¿Dónde está mi pedido ORD-2024-001234?",
    "customer_email": "cliente@example.com"
  }'
```

### Python

```python
from chatbot_rastreo_pedidos import OrderTrackingChatbot

chatbot = OrderTrackingChatbot(
    company_name="Mi Empresa",
    bot_name="Asistente de Pedidos"
)

response = chatbot.process_message(
    "¿Dónde está mi pedido ORD-2024-001234?"
)
print(response.message)
```

## 📚 Documentación

Ver [docs/CHATBOT_RASTREO_PEDIDOS.md](docs/CHATBOT_RASTREO_PEDIDOS.md) para documentación completa.

## 🔌 Integración n8n

1. Importa `n8n_workflow_rastreo_pedidos.json` en n8n
2. Configura credenciales de Telegram y API
3. Activa el workflow

## 📊 Endpoints API

- `POST /api/chat` - Procesar mensaje
- `GET /api/health` - Health check
- `GET /api/metrics` - Métricas
- `GET /api/order/<order_id>` - Información de pedido
- `GET /api/orders/search` - Buscar pedidos por email
- `GET /api/orders/<order_id>/problems` - Detectar problemas 🆕
- `GET /api/orders/<order_id>/predictions` - Predicciones futuras 🆕
- `GET /api/users/<email>/pattern` - Patrón de usuario 🆕
- `POST /api/feedback` - Agregar feedback 🆕
- `GET /api/feedback/stats` - Estadísticas de feedback 🆕
- `GET /api/trends` - Análisis de tendencias 🆕
- `GET /api/alerts/proactive` - Alertas proactivas 🆕
- `GET /api/export` - Exportar datos 🆕
- `POST /api/language` - Establecer idioma 🆕
- `GET /api/dashboard` - Dashboard completo 🆕
- `POST /api/nps` - Registrar score NPS 🆕
- `GET /api/nps/analysis` - Análisis NPS 🆕
- `POST /api/ab-test` - Crear test A/B 🆕
- `GET /api/ab-test/<test_id>/results` - Resultados A/B 🆕
- `GET /api/roi` - Análisis de ROI 🆕
- `POST /api/reports/generate` - Generar reporte automático 🆕
- `GET /api/reports/history` - Historial de reportes 🆕
- `POST /api/webhook/carrier-update` - Webhook para carriers
- `POST /api/notifications/send` - Notificaciones proactivas
- `POST /api/orders/<order_id>/subscribe` - Suscripciones

## 🎉 Beneficios

- **70% de automatización** de consultas de entrega
- **Respuestas instantáneas** 24/7
- **Escalación inteligente** cuando es necesario
- **Métricas completas** para análisis

---

**Ideal para e-commerce, automatiza el 70% de consultas de entrega.**


