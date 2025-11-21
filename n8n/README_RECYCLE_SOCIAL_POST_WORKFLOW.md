# 🔄 Workflow n8n - Reciclar Publicaciones Sociales

Workflow de n8n para automatizar el reciclaje de publicaciones antiguas de redes sociales usando el script `recycle_social_post.py`.

## 🎯 Funcionalidades

- ✅ **Webhook trigger**: Recibe publicaciones antiguas vía POST
- ✅ **Validación automática**: Verifica datos antes de procesar
- ✅ **Ejecución del script**: Ejecuta el script de reciclaje automáticamente
- ✅ **Procesamiento de resultados**: Estructura y procesa los resultados
- ✅ **Notificaciones Telegram**: Opcional, envía resumen a Telegram
- ✅ **Respuesta estructurada**: Retorna JSON con todos los resultados

## 🚀 Instalación

### Paso 1: Importar el Workflow

1. Abre n8n
2. Ve a "Workflows" → "Import from File"
3. Selecciona el archivo `n8n_workflow_recycle_social_post.json`
4. El workflow se importará con todos los nodos configurados

### Paso 2: Configurar Variables de Entorno

Configura las siguientes variables de entorno en n8n (Settings → Environment Variables):

```bash
# Opcional: Para usar IA mejorada
OPENAI_API_KEY=sk-...

# Opcional: Para notificaciones Telegram
TELEGRAM_BOT_TOKEN=tu_token_del_bot
TELEGRAM_CHAT_ID=tu_chat_id
```

### Paso 3: Activar el Workflow

1. Haz clic en el botón "Active" en la esquina superior derecha
2. El workflow estará listo para recibir requests vía webhook

## 📡 Uso del Webhook

### Endpoint

```
POST https://tu-n8n-instance.com/webhook/recycle-social-post
```

### Formato del Request

```json
{
  "post": "La automatización puede ahorrarte hasta 10 horas semanales. #Productividad #IA",
  "use_ai": false,
  "format": "json",
  "output": "mi_resultado.json"
}
```

### Parámetros

- `post` o `original_post` o `text` (requerido): Texto de la publicación antigua
- `use_ai` (opcional, boolean): Usar IA para generar contenido más creativo
- `format` (opcional, string): Formato de exportación (`json`, `markdown`, `csv`, `all`)
- `output` (opcional, string): Nombre del archivo de salida

### Ejemplo con cURL

```bash
curl -X POST https://tu-n8n-instance.com/webhook/recycle-social-post \
  -H "Content-Type: application/json" \
  -d '{
    "post": "La automatización puede ahorrarte hasta 10 horas semanales. ¿Qué proceso de tu negocio te gustaría automatizar primero? #Productividad #IA",
    "use_ai": false,
    "format": "json"
  }'
```

### Ejemplo con JavaScript/Node.js

```javascript
const response = await fetch('https://tu-n8n-instance.com/webhook/recycle-social-post', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
  },
  body: JSON.stringify({
    post: 'Tu publicación antigua aquí',
    use_ai: true,
    format: 'all'
  })
});

const result = await response.json();
console.log(result);
```

### Ejemplo con Python

```python
import requests

url = 'https://tu-n8n-instance.com/webhook/recycle-social-post'
data = {
    'post': 'Tu publicación antigua aquí',
    'use_ai': True,
    'format': 'json'
}

response = requests.post(url, json=data)
result = response.json()
print(result)
```

## 📊 Respuesta del Webhook

### Respuesta Exitosa

```json
{
  "success": true,
  "executionId": "1234567890-abc123",
  "originalPost": "La automatización puede ahorrarte...",
  "timestamp": "2025-11-12 09:45:00",
  "analysis": {
    "content_type": "question",
    "tone": "curious",
    "main_topic": "negocios",
    "keywords": ["automatización", "ahorrarte", "horas"]
  },
  "versions": {
    "static_post": { ... },
    "short_video": { ... },
    "story": { ... }
  },
  "engagementMetrics": {
    "static": {
      "engagement_score": 80,
      "estimated_likes": 800,
      "estimated_comments": 120
    },
    "video": {
      "engagement_score": 100,
      "estimated_likes": 1000,
      "estimated_comments": 150
    },
    "story": {
      "engagement_score": 72,
      "estimated_likes": 720,
      "estimated_comments": 108
    }
  },
  "bestVersion": "short_video",
  "recommendation": "Publica como video corto para máximo alcance",
  "imagePrompts": [ ... ],
  "relatedContent": [ ... ],
  "trendingHashtags": [ ... ],
  "jsonFile": "/Users/adan/IA/recycled_post_20251112_094500.json"
}
```

### Respuesta de Error

```json
{
  "success": false,
  "error": "El campo \"post\" es requerido",
  "details": {
    "received": { ... }
  }
}
```

## 🔧 Configuración Avanzada

### Integración con Otros Servicios

El workflow puede extenderse fácilmente para:

1. **Guardar en Base de Datos**: Agregar nodo después de "Process Results"
2. **Enviar a Slack**: Agregar nodo de Slack después de "Process Results"
3. **Publicar Automáticamente**: Agregar nodos de Instagram/Twitter API
4. **Programar Publicaciones**: Integrar con Buffer o Hootsuite

### Modificar el Workflow

Para personalizar el workflow:

1. **Cambiar ruta del script**: Edita el nodo "Initialize & Validate"
2. **Agregar más validaciones**: Modifica el nodo "Check Can Proceed"
3. **Cambiar formato de respuesta**: Edita el nodo "Format Response"
4. **Agregar más notificaciones**: Crea nuevos nodos después de "Process Results"

## 📝 Ejemplos de Uso

### Caso 1: Reciclar una publicación simple

```bash
curl -X POST https://tu-n8n-instance.com/webhook/recycle-social-post \
  -H "Content-Type: application/json" \
  -d '{"post": "Mi publicación antigua aquí"}'
```

### Caso 2: Con IA mejorada

```bash
curl -X POST https://tu-n8n-instance.com/webhook/recycle-social-post \
  -H "Content-Type: application/json" \
  -d '{
    "post": "Mi publicación antigua aquí",
    "use_ai": true
  }'
```

### Caso 3: Exportar a múltiples formatos

```bash
curl -X POST https://tu-n8n-instance.com/webhook/recycle-social-post \
  -H "Content-Type: application/json" \
  -d '{
    "post": "Mi publicación antigua aquí",
    "format": "all",
    "output": "mi_resultado"
  }'
```

## 🐛 Troubleshooting

### Error: Script no encontrado

**Problema**: El script no se encuentra en la ruta especificada.

**Solución**: Verifica que el script esté en `/Users/adan/IA/scripts/recycle_social_post.py` o modifica la ruta en el nodo "Initialize & Validate".

### Error: OPENAI_API_KEY no configurada

**Problema**: Se solicita usar IA pero no hay API key.

**Solución**: Configura `OPENAI_API_KEY` en las variables de entorno de n8n o no uses `use_ai: true`.

### Error: Timeout

**Problema**: El script tarda demasiado en ejecutarse.

**Solución**: Aumenta el timeout en el nodo "Execute Recycle Script" (actualmente 5 minutos).

### No se encuentra el archivo JSON

**Problema**: El workflow no encuentra el archivo JSON generado.

**Solución**: Verifica que el script tenga permisos de escritura en `/Users/adan/IA/` o modifica la ruta de salida.

## 📚 Recursos Relacionados

- [Script de Reciclaje](./README_RECYCLE_SOCIAL_POST.md): Documentación completa del script
- [n8n Documentation](https://docs.n8n.io/): Documentación oficial de n8n
- [Webhook Guide](https://docs.n8n.io/integrations/builtin/core-nodes/n8n-nodes-base.webhook/): Guía de webhooks en n8n

## 🎨 Próximas Mejoras

- [ ] Integración con APIs de redes sociales para publicación automática
- [ ] Programación automática de publicaciones recicladas
- [ ] Dashboard para visualizar métricas de engagement
- [ ] Análisis histórico de publicaciones recicladas
- [ ] Integración con calendario de contenido

---

**Creado para**: Automatización de reciclaje de contenido en redes sociales  
**Versión**: 1.0  
**Última actualización**: Noviembre 2025



