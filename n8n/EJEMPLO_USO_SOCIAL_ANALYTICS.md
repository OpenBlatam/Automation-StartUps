# 📖 Ejemplo de Uso - Análisis de Estadísticas Orgánicas

## Escenario: Análisis Semanal de Contenido

Imagina que publicas contenido regularmente en Instagram, TikTok y YouTube, y quieres entender qué tipo de contenido funciona mejor para replicar el éxito.

### Paso 1: Configuración Inicial

```bash
# Ejecuta el script de configuración
cd /Users/adan/IA/n8n
./setup_social_analytics.sh
```

O configura manualmente las variables de entorno en n8n:
- `OPENAI_API_KEY`: Tu clave de OpenAI
- `INSTAGRAM_ACCESS_TOKEN`: Token de Instagram
- `INSTAGRAM_ACCOUNT_ID`: ID de tu cuenta de Instagram
- `TIKTOK_ACCESS_TOKEN`: Token de TikTok
- `YOUTUBE_API_KEY`: Clave de API de YouTube
- `TELEGRAM_BOT_TOKEN`: Token de tu bot de Telegram (opcional)
- `TELEGRAM_CHAT_ID`: Tu Chat ID de Telegram (opcional)

### Paso 2: Importar el Workflow en n8n

1. Abre n8n
2. Ve a "Workflows" → "Import from File"
3. Selecciona `n8n_workflow_social_analytics_ai.json`
4. Configura las credenciales:
   - OpenAI API
   - Telegram Bot API (si usas notificaciones)

### Paso 3: Ejecución Automática

El workflow se ejecutará automáticamente cada **lunes a las 8:00 AM UTC** y analizará los posts de los últimos 7 días.

### Paso 4: Ejecución Manual (Opcional)

Puedes ejecutar el workflow manualmente:

**Opción A: Desde n8n**
- Haz clic en "Execute Workflow" en la interfaz de n8n

**Opción B: Vía Webhook**
```bash
curl -X POST http://localhost:5678/webhook/social-analytics
```

**Opción C: Con parámetros personalizados**
Modifica las variables de entorno antes de ejecutar:
```bash
export DAYS_BACK=30  # Analizar último mes
export TOP_N_POSTS=20  # Top 20 posts
```

### Paso 5: Revisar Resultados

#### Notificación en Telegram

Recibirás un mensaje como este:

```
📊 Análisis de Estadísticas Orgánicas - Reporte Generado

📅 Período: 2024-01-01 al 2024-01-08

📈 Resumen:
• Total de posts: 45
• Engagement promedio: 5.23%
• Score viral promedio: 42.15
• Por plataforma: Instagram (20), TikTok (15), YouTube (10)

🏆 Top 5 Posts Más Virales:

1. Instagram - 2024-01-05
   Engagement: 12.45% | Score: 78.32
   Vistas: 50,000
   Likes: 5,000
   Este post sobre marketing digital generó...

2. TikTok - 2024-01-03
   Engagement: 8.92% | Score: 65.18
   Vistas: 100,000
   Likes: 8,000
   Video corto sobre tips de productividad...

🤖 Análisis de IA:
Los posts más exitosos comparten varios patrones comunes...
[Análisis completo de ChatGPT]

📁 Reporte completo guardado en: /Users/adan/IA/reports/social_analytics/social_analytics_1234567890-abc123.json
```

#### Reporte JSON

El reporte completo se guarda en:
```
/Users/adan/IA/reports/social_analytics/social_analytics_[executionId].json
```

Ejemplo de estructura:

```json
{
  "executionId": "1704700800000-abc123",
  "dateRange": {
    "start": "2024-01-01",
    "end": "2024-01-08"
  },
  "summary": {
    "totalPosts": 45,
    "avgEngagementRate": "5.23",
    "avgViralScore": "42.15",
    "postsByPlatform": {
      "Instagram": 20,
      "TikTok": 15,
      "YouTube": 10
    }
  },
  "topPosts": [
    {
      "rank": 1,
      "platform": "Instagram",
      "date": "2024-01-05",
      "caption": "5 estrategias de marketing que funcionan en 2024...",
      "engagementRate": "12.45%",
      "viralScore": "78.32",
      "metrics": {
        "likes": 5000,
        "comments": 250,
        "impressions": 50000,
        "reach": 45000
      },
      "link": "https://instagram.com/p/ABC123"
    }
  ],
  "aiAnalysis": "ANÁLISIS COMPLETO DE CHATGPT:\n\n1. PATRONES COMUNES:\nLos posts más exitosos comparten...\n\n2. FACTORES DE ÉXITO:\n- Hooks emocionales fuertes...\n\n3. RECOMENDACIONES ACCIONABLES:\n- Crear contenido educativo con formato carrusel...\n\n4. QUÉ EVITAR:\n- Posts demasiado promocionales...\n\n5. PLAN DE ACCIÓN:\n1. Crear 3 carruseles educativos por semana...\n2. Publicar entre 6-8 PM hora local...\n..."
}
```

### Paso 6: Implementar Recomendaciones

Basándote en el análisis de ChatGPT:

1. **Revisa los patrones comunes** identificados
2. **Implementa las recomendaciones** en tus próximos posts
3. **Evita los errores** mencionados en el análisis
4. **Sigue el plan de acción** sugerido

### Ejemplo Práctico: Interpretando los Resultados

**Escenario**: El análisis muestra que tus posts de Instagram sobre "tips de productividad" tienen un engagement rate del 12%, mientras que los posts promocionales solo tienen 2%.

**Análisis de ChatGPT podría decir**:
> "Los posts educativos con formato carrusel generan 6x más engagement que los posts promocionales. Los usuarios valoran contenido que les enseña algo nuevo."

**Recomendación**:
- Crear más contenido educativo (80% del contenido)
- Reducir contenido promocional directo (20% del contenido)
- Usar formato carrusel para posts educativos
- Incluir números y estadísticas en los títulos

## Casos de Uso Avanzados

### Análisis Mensual

Para analizar un mes completo:

```bash
export DAYS_BACK=30
export TOP_N_POSTS=20
```

Luego ejecuta el workflow manualmente.

### Comparar Períodos

1. Ejecuta el workflow para la semana pasada
2. Guarda el reporte con un nombre específico
3. Ejecuta el workflow para esta semana
4. Compara los resultados manualmente o con un script

### Análisis de una Plataforma Específica

Si solo quieres analizar Instagram:
- Configura solo las credenciales de Instagram
- El workflow funcionará solo con Instagram
- Los reportes mostrarán solo datos de Instagram

## Troubleshooting Rápido

**Problema**: No recibo datos de Instagram
- ✅ Verifica que el token tenga permisos de `instagram_manage_insights`
- ✅ Asegúrate de que tu cuenta sea Business Account
- ✅ Verifica que haya posts en el período seleccionado

**Problema**: ChatGPT no responde
- ✅ Verifica que tengas créditos en OpenAI
- ✅ Revisa que el API key sea válido
- ✅ Verifica que el modelo esté disponible (gpt-4 o gpt-3.5-turbo)

**Problema**: No recibo notificaciones en Telegram
- ✅ Verifica que `TELEGRAM_BOT_TOKEN` y `TELEGRAM_CHAT_ID` estén configurados
- ✅ Asegúrate de haber iniciado una conversación con tu bot
- ✅ Verifica que el bot tenga permisos para enviar mensajes

## Próximos Pasos

1. ✅ Configura el workflow
2. ✅ Ejecuta tu primer análisis
3. ✅ Revisa el reporte y análisis de IA
4. ✅ Implementa las recomendaciones
5. ✅ Compara resultados en la próxima ejecución
6. ✅ Ajusta tu estrategia basándote en los datos

---

**¿Necesitas ayuda?** Revisa `README_SOCIAL_ANALYTICS_AI.md` para documentación completa.



