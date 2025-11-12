# 🚀 Inicio Rápido - Sistema de Chatbot

## Instalación en 5 Minutos

### 1. Instalar Dependencias

```bash
# Crear entorno virtual
python3 -m venv venv
source venv/bin/activate  # En Windows: venv\Scripts\activate

# Instalar dependencias
pip install -r requirements.txt
```

### 2. Configuración Básica

Edita `chatbot_config.json` con tu información:

```json
{
  "company_name": "Tu Empresa",
  "product": "Tu Producto",
  "tone": "profesional pero cálido",
  "use_emojis": true
}
```

### 3. Personalizar FAQs

Edita `faqs.json` y agrega tus preguntas frecuentes (ya hay 10 ejemplos).

### 4. Iniciar el Sistema

**Terminal 1 - API REST:**
```bash
python api_rest.py
```

**Terminal 2 - Dashboard:**
```bash
python dashboard_metrics.py
```

### 5. Probar el Chatbot

**Opción A: Usar el widget web**
- Abre `widget_web.html` en tu navegador
- Asegúrate de que la API esté corriendo en `http://localhost:8000`

**Opción B: Usar curl**
```bash
curl -X POST http://localhost:8000/api/v1/chat \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "test_user",
    "message": "¿Cómo exportar reportes?",
    "channel": "web"
  }'
```

**Opción C: Usar Python**
```python
python ejemplo_uso.py
```

## 📊 Ver Dashboard

Abre en tu navegador: `http://localhost:5000`

## 🔧 Configuración Avanzada

### Integrar con Salesforce

1. Edita `chatbot_config.json`
2. Agrega credenciales en la sección `integrations.crm`
3. El chatbot sincronizará automáticamente

### Integrar con Zapier

1. Crea un webhook en Zapier
2. Agrega la URL en `chatbot_config.json` → `integrations.zapier.webhook_url`
3. Configura tus automatizaciones en Zapier

### Integrar con WhatsApp

1. Obtén credenciales de WhatsApp Business API
2. Agrega en `chatbot_config.json` → `integrations.whatsapp`
3. El chatbot responderá automáticamente

## 📈 Monitoreo

### Ver Métricas
```python
from chatbot_engine import ChatbotEngine

chatbot = ChatbotEngine()
metrics = chatbot.get_metrics()
print(metrics)
```

### Generar Reportes
```python
from analytics_report import AnalyticsReport
from learning_system import LearningSystem

chatbot = ChatbotEngine()
learning = LearningSystem(chatbot)
analytics = AnalyticsReport(chatbot, learning)

# Reporte diario
report = analytics.generate_daily_report()
analytics.export_report_to_json(report)
```

## 🧪 Ejecutar Tests

```bash
pytest test_chatbot.py -v
```

## 🆘 Solución de Problemas

### El chatbot no responde
- Verifica que la API esté corriendo
- Revisa los logs en la consola
- Verifica que `faqs.json` esté cargado

### Dashboard no muestra datos
- Asegúrate de que el chatbot haya procesado mensajes
- Verifica la conexión a la API
- Revisa la consola del navegador (F12)

### Integraciones no funcionan
- Verifica credenciales en `chatbot_config.json`
- Revisa logs para errores específicos
- Prueba las integraciones individualmente

## 📚 Recursos

- [README completo](README.md)
- [Plan de implementación](PLAN_IMPLEMENTACION.md)
- [Flujo de trabajo](FLUJO_TRABAJO.md)
- [Ejemplos de uso](ejemplo_uso.py)

## 🎯 Próximos Pasos

1. ✅ Personalizar FAQs
2. ✅ Configurar integraciones
3. ✅ Probar con usuarios reales
4. ✅ Analizar métricas semanalmente
5. ✅ Mejorar basado en feedback

---

**¿Necesitas ayuda?** Revisa la documentación completa o contacta al equipo de soporte.






