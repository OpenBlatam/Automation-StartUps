# Workflow de Análisis de Engagement - n8n

## 📋 Descripción

Este workflow de n8n analiza automáticamente las publicaciones del último mes, identifica qué tipo de contenido obtuvo más engagement, explica por qué funcionó mejor, y genera 5 nuevas ideas de contenido basadas en ese patrón exitoso.

## 🎯 Funcionalidades

### Funcionalidades Principales
1. **Análisis Automático**: Obtiene publicaciones del último mes desde la base de datos
2. **Clasificación Inteligente**: Clasifica posts por tipo de contenido (tutorial, noticia, opinión, caso de estudio, infografía, etc.)
3. **Cálculo de Métricas**: Calcula engagement total, tasas de engagement, promedios por tipo
4. **Análisis con IA**: Usa OpenAI GPT-4 para analizar por qué un tipo de contenido fue más exitoso
5. **Generación de Ideas**: Crea 5 nuevas ideas de contenido basadas en el patrón exitoso
6. **Reportes**: Genera reportes en múltiples formatos (texto, JSON) y los envía por Telegram/Email

### Mejoras Avanzadas (v2.0)
7. **Validación Avanzada**: Verifica configuración y APIs antes de ejecutar
8. **Health Checks**: Monitorea el estado de APIs (OpenAI, PostgreSQL)
9. **Sistema de Retry**: Reintentos automáticos con exponential backoff para llamadas a IA
10. **Validación de Datos**: Verifica mínimo de posts antes de analizar
11. **Analytics del Workflow**: Tracking de ejecuciones, tasas de éxito, tiempos promedio
12. **Manejo Robusto de Errores**: Captura y reporta errores de forma estructurada
13. **Configuración Flexible**: Múltiples opciones de configuración vía variables de entorno

### Nuevas Funcionalidades (v3.0)
14. **Análisis por Plataforma**: Identifica qué plataforma genera mejor engagement
15. **Análisis de Mejor Hora**: Determina el mejor día y hora para publicar
16. **Análisis de Hashtags**: Identifica los hashtags más efectivos
17. **Comparación con Períodos Anteriores**: Compara métricas con análisis previos
18. **Reportes Mejorados**: Incluye todas las nuevas métricas en el reporte final

### Funcionalidades Avanzadas (v4.0)
19. **Detección de Anomalías**: Detecta posts con engagement anómalo (spikes/drops)
20. **Predicciones de Engagement**: Predice engagement futuro basado en tendencias
21. **Exportación a CSV**: Exporta datos detallados y resúmenes a CSV
22. **Alertas Inteligentes**: Identifica cambios significativos y anomalías
23. **Análisis de Tendencias**: Analiza tendencias históricas para predicciones

### Funcionalidades Premium (v5.0)
24. **Detección de Contenido Viral**: Identifica posts virales (engagement rate > 10%, total > 500)
25. **Análisis de Correlaciones**: Analiza relación entre variables (media, longitud título, hashtags)
26. **Análisis de ROI**: Calcula retorno de inversión por tipo y plataforma
27. **Benchmarking de Industria**: Compara métricas contra estándares de la industria
28. **Recomendaciones Avanzadas**: Sugerencias basadas en correlaciones y ROI

### Funcionalidades Estratégicas (v6.0)
29. **Análisis de Palabras Clave**: Identifica palabras más efectivas en títulos
30. **Calendario Optimizado**: Genera calendario de contenido para próximas semanas
31. **Detección de Contenido Mejorable**: Identifica posts con potencial de mejora
32. **Recomendaciones de Mejora**: Sugerencias específicas para cada post mejorable
33. **Planificación Estratégica**: Calendario basado en mejores prácticas identificadas

### Sistema de Alertas Inteligentes (v7.0)
34. **Alertas Críticas Automáticas**: Detecta problemas críticos y genera alertas
35. **Sistema de Priorización**: Clasifica alertas por nivel (Crítico/Alta/Media)
36. **Alertas de Tendencia**: Detecta tendencias decrecientes automáticamente
37. **Alertas de Benchmarking**: Notifica cuando el rendimiento está por debajo del estándar
38. **Alertas de Plataforma**: Identifica plataformas con bajo rendimiento
39. **Recomendaciones de Acción**: Cada alerta incluye acciones específicas a tomar

### Análisis Avanzado y Estrategia (v8.0)
40. **Estrategia Optimizada**: Genera estrategia completa basada en todos los análisis
41. **Análisis de Patrones Temporales**: Detecta patrones semanales, horarios y tendencias
42. **Detección de Picos y Valles**: Identifica momentos de máximo y mínimo engagement
43. **Análisis de Tendencia General**: Compara primera vs segunda mitad del período
44. **Recomendaciones Estratégicas Integradas**: Combina insights de múltiples análisis
45. **Frecuencia Sugerida**: Calcula frecuencia óptima basada en datos históricos

### Detección de Oportunidades y A/B Testing (v9.0)
46. **Detección Automática de Oportunidades**: Identifica oportunidades de contenido no aprovechadas
47. **Análisis de Contenido Subutilizado**: Detecta tipos/plataformas con alto potencial pero poco uso
48. **Análisis de Timing Oportunidades**: Identifica horarios óptimos no aprovechados
49. **Análisis de Hashtags Oportunidades**: Detecta hashtags efectivos subutilizados
50. **Detección de Patrones Virales**: Identifica oportunidades de replicar contenido viral
51. **Sistema de A/B Testing**: Realiza tests estadísticos en diferentes variables
52. **Análisis de Significancia**: Calcula si diferencias son estadísticamente significativas
53. **Recomendaciones Basadas en Tests**: Sugerencias basadas en resultados de A/B testing

### Funcionalidades Premium Avanzadas (v10.0) ⭐ NUEVO
54. **Sistema de Scoring de Contenido en Tiempo Real**: Evalúa contenido antes de publicar con score 0-100
55. **Análisis Multifactorial**: Evalúa tipo, timing, hashtags, longitud, plataforma y performance
56. **Probabilidad Viral**: Calcula probabilidad de que contenido se vuelva viral
57. **Recomendaciones de Mejora**: Sugerencias específicas para optimizar cada post
58. **Análisis de Tendencias de Mercado Avanzado**: Detecta palabras clave emergentes y declinantes
59. **Clasificación de Tendencias**: Identifica tendencias EMERGENTES, CRECIENTES, ESTABLES, DECRECIENTES, DECLINANTES
60. **Recomendaciones Estratégicas de Tendencias**: Acciones específicas basadas en tendencias detectadas
61. **Análisis de Sentimiento Avanzado**: Analiza sentimiento de contenido con NLP
62. **Análisis por Aspectos**: Evalúa sentimiento en calidad, precio y servicio
63. **Score de Sentimiento**: Calcula score de -100 a +100 con nivel de confianza
64. **ROI Predictivo Avanzado**: Proyecciones de ROI a 6 meses con escenarios
65. **Tendencias de ROI**: Identifica si ROI será creciente, decreciente o estable
66. **Recomendaciones de Inversión**: Sugerencias de aumentar/optimizar inversión basadas en proyecciones
67. **Break-Even Proyectado**: Calcula cuándo se alcanzará ROI positivo
68. **Análisis Cross-Platform Avanzado**: Comparación profunda entre plataformas
69. **Oportunidades Cross-Platform**: Identifica plataformas con potencial de mejora
70. **Estrategia Cross-Platform**: Recomendaciones de distribución de contenido entre plataformas
71. **Análisis de Distribución**: Porcentaje de contenido y engagement por plataforma

## 🔧 Configuración

### Variables de Entorno Requeridas

```bash
# Base de datos PostgreSQL
DB_HOST=localhost
DB_PORT=5432
DB_NAME=content_marketing
DB_USER=postgres
DB_PASSWORD=tu_password

# OpenAI API (para análisis y generación de ideas)
OPENAI_API_KEY=tu_api_key

# Telegram (opcional, para notificaciones)
TELEGRAM_BOT_TOKEN=tu_bot_token
TELEGRAM_CHAT_ID=tu_chat_id

# Email (opcional, para reportes)
EMAIL_FROM=noreply@example.com
EMAIL_TO=tu_email@example.com
SMTP_HOST=smtp.example.com
SMTP_PORT=587
SMTP_USER=tu_usuario
SMTP_PASSWORD=tu_password

# Configuración del análisis
DAYS_BACK=30  # Días hacia atrás para analizar (default: 30)
REPORTS_DIR=./reports  # Directorio donde guardar reportes
USE_MOCK_DATA=false  # Usar datos simulados en lugar de BD (útil para pruebas)
MIN_POSTS_REQUIRED=10  # Mínimo de posts requeridos para análisis (default: 10)
MAX_RETRIES=3  # Intentos máximos para llamadas a IA (default: 3)
ENABLE_CACHE=true  # Habilitar caché de análisis previos
ENABLE_COMPARISON=true  # Habilitar comparación con períodos anteriores
ENABLE_TRENDS=true  # Habilitar análisis de tendencias temporales
ENABLE_ANALYTICS=true  # Habilitar tracking de analytics del workflow

# Notificaciones adicionales (opcionales)
SLACK_WEBHOOK_URL=  # URL de webhook de Slack para notificaciones

# Configuración avanzada (opcionales)
CALENDAR_WEEKS=4  # Número de semanas para calendario optimizado (default: 4)
COSTO_POR_HORA=50  # Costo por hora para cálculo de ROI en dólares (default: 50)
```

### Credenciales en n8n

Necesitas configurar las siguientes credenciales en n8n:

1. **PostgreSQL**: Para acceder a la base de datos de contenido
2. **OpenAI API**: Para análisis y generación de ideas
3. **Telegram Bot API** (opcional): Para notificaciones
4. **SMTP** (opcional): Para envío de emails

## 📊 Estructura de Datos Esperada

El workflow espera las siguientes tablas en PostgreSQL:

- `content_scheduled_posts`: Publicaciones programadas/publicadas
- `content_articles`: Artículos originales con categorías
- `content_engagement`: Métricas de engagement por post

### Campos Importantes

- `content_scheduled_posts.category` o `content_articles.category`: Tipo de contenido
- `content_scheduled_posts.metadata`: JSONB con metadatos adicionales
- `content_engagement.likes`, `comments`, `shares`, `impressions`, etc.: Métricas

## 🚀 Uso

### Modo de Prueba con Datos Simulados

Si no tienes acceso a la base de datos o quieres probar el workflow, puedes usar datos simulados:

1. **Opción 1**: Configura la variable de entorno:
   ```bash
   USE_MOCK_DATA=true
   ```

2. **Opción 2**: El workflow automáticamente generará datos de prueba si:
   - La conexión a la BD falla
   - No se encuentran publicaciones en el rango de fechas
   - El nodo de BD no devuelve datos

Los datos simulados incluyen ~45 posts distribuidos en los últimos 30 días, con diferentes tipos de contenido y métricas de engagement realistas. Los **tutoriales** tendrán mejor engagement por defecto para demostrar el análisis.

### Ejecución Automática

El workflow se ejecuta automáticamente el primer día de cada mes a las 9:00 AM UTC.

### Ejecución Manual

Puedes ejecutar el workflow manualmente de dos formas:

1. **Desde la interfaz de n8n**: Haz clic en "Execute Workflow"
2. **Vía Webhook**: Envía un POST a:
   ```
   POST http://tu-n8n-instance/webhook/analyze-engagement
   Content-Type: application/json
   
   {
     "daysBack": 30,
     "contentTypes": ["tutorial", "noticia", "opinion", "caso_estudio", "infografia"]
   }
   ```

### Parámetros del Webhook

- `daysBack` (opcional): Número de días hacia atrás para analizar (default: 30)
- `contentTypes` (opcional): Array de tipos de contenido a analizar

## 📈 Tipos de Contenido Soportados

El workflow clasifica automáticamente el contenido en estos tipos:

- **tutorial**: Contenido educativo paso a paso
- **noticia**: Anuncios y actualizaciones
- **opinion**: Opiniones y puntos de vista
- **caso_estudio**: Casos de éxito y ejemplos reales
- **infografia**: Contenido visual y gráficos
- **general**: Contenido que no encaja en las categorías anteriores

La clasificación se hace basándose en:
1. Campo `category` de la tabla `content_articles`
2. Campo `metadata.content_type` del post
3. Análisis de palabras clave en el contenido y título

## 📝 Formato del Reporte

El reporte incluye:

1. **Resumen por Tipo de Contenido**:
   - Número de publicaciones
   - Engagement total y promedio
   - Tasas de engagement
   - Métricas detalladas (likes, comentarios, shares)

2. **Tipo Ganador**:
   - Identificación del tipo con mayor engagement
   - Métricas destacadas
   - Top 3 posts más exitosos

3. **Análisis de IA**:
   - Explicación de por qué funcionó mejor
   - Características específicas que contribuyeron al éxito
   - Patrones identificados

4. **5 Nuevas Ideas**:
   - Título/tema sugerido
   - Formato recomendado
   - Plataforma sugerida
   - Hashtags recomendados
   - Longitud aproximada
   - Elementos visuales sugeridos
   - Justificación de por qué funcionará

## 📁 Archivos Generados

El workflow guarda múltiples archivos en el directorio `REPORTS_DIR`:

1. `engagement_analysis_{executionId}.json`: Datos completos en JSON
2. `engagement_report_{executionId}.txt`: Reporte formateado en texto
3. `engagement_data_{executionId}.csv`: Datos detallados de todos los posts (CSV)
4. `engagement_summary_{executionId}.csv`: Resumen por tipo de contenido (CSV)

Los archivos CSV están listos para importar en Excel, Google Sheets o herramientas de análisis de datos.

## 🔍 Ejemplo de Salida

```
📊 ANÁLISIS DE ENGAGEMENT - ÚLTIMO MES
═══════════════════════════════════════

📅 Período analizado: 01/12/2024 - 31/12/2024
📝 Total de publicaciones: 45

📈 RESUMEN POR TIPO DE CONTENIDO:
─────────────────────────────────────

🎯 TUTORIAL:
   • Publicaciones: 12
   • Engagement total: 3450
   • Promedio por post: 287.50
   • Tasa de engagement: 4.25%
   ...

🏆 TIPO DE CONTENIDO CON MAYOR ENGAGEMENT:
─────────────────────────────────────
✨ TUTORIAL

Métricas destacadas:
• Engagement promedio: 287.50
• Tasa de engagement: 4.25%
...

🔍 ANÁLISIS: ¿POR QUÉ FUNCIONÓ?
─────────────────────────────────────
[Análisis detallado generado por IA]

💡 5 NUEVAS IDEAS DE CONTENIDO:
─────────────────────────────────────
1. [Idea 1]
2. [Idea 2]
...
```

## 🛠️ Troubleshooting

### Error: "No se encontraron publicaciones"

- Verifica que haya publicaciones con `status = 'published'` en el rango de fechas
- Revisa la configuración de `DAYS_BACK`
- Verifica la conexión a la base de datos

### Error: "OpenAI API Error"

- Verifica que `OPENAI_API_KEY` esté configurada correctamente
- Asegúrate de tener créditos disponibles en tu cuenta de OpenAI
- Revisa los límites de rate limiting

### Clasificación Incorrecta de Tipos

- Asegúrate de que los posts tengan `category` o `metadata.content_type` definidos
- El workflow usa análisis de palabras clave como fallback, pero es menos preciso

### Reporte No Se Envía

- Verifica las credenciales de Telegram/Email
- Revisa los logs de n8n para errores específicos
- El workflow continúa aunque falle el envío de notificaciones

## ✨ Nuevas Características v9.0

### Detección Automática de Oportunidades
- ✅ Identificación de tipos de contenido subutilizados con alto potencial
- ✅ Detección de plataformas subutilizadas
- ✅ Identificación de horarios óptimos no aprovechados
- ✅ Detección de hashtags efectivos subutilizados
- ✅ Oportunidades de replicar contenido viral
- ✅ Cálculo de impacto potencial de cada oportunidad
- ✅ Priorización automática (Alta/Media/Baja)
- ✅ Acciones específicas recomendadas

### Sistema de A/B Testing
- ✅ Tests automáticos de Media vs Sin Media
- ✅ Tests de longitud de título (largos vs cortos)
- ✅ Tests de número de hashtags (óptimo vs fuera de rango)
- ✅ Cálculo de significancia estadística
- ✅ Comparación de variantes con métricas
- ✅ Recomendaciones basadas en resultados significativos
- ✅ Identificación de diferencias porcentuales

## ✨ Características v8.0

### Estrategia Optimizada
- ✅ Generación automática de estrategia completa
- ✅ Recomendaciones integradas de múltiples análisis
- ✅ Tipo de contenido, plataforma, horario y formato optimizados
- ✅ Frecuencia sugerida basada en datos históricos
- ✅ Hashtags estratégicos recomendados
- ✅ Plan de acción claro y accionable

### Análisis de Patrones Temporales
- ✅ Análisis de tendencia semanal (mejor/peor día)
- ✅ Análisis de tendencia horaria (mejor/peor hora)
- ✅ Detección de picos de engagement
- ✅ Detección de valles de engagement
- ✅ Análisis de tendencia general (creciente/decreciente/estable)
- ✅ Comparación primera vs segunda mitad del período

## ✨ Características v7.0

### Sistema de Alertas Inteligentes
- ✅ Detección automática de problemas críticos
- ✅ Clasificación por nivel de severidad (Crítico/Alta/Media)
- ✅ Alertas de tendencias decrecientes
- ✅ Alertas de benchmarking bajo
- ✅ Alertas de plataformas subóptimas
- ✅ Alertas de contenido mejorable significativo
- ✅ Recomendaciones de acción específicas por alerta
- ✅ Priorización automática de alertas

## ✨ Características v6.0

### Análisis de Palabras Clave
- ✅ Identificación de palabras más efectivas en títulos
- ✅ Análisis de impacto por palabra clave
- ✅ Recomendaciones de palabras a usar en futuros títulos
- ✅ Estadísticas de uso y engagement promedio

### Calendario Optimizado
- ✅ Generación automática de calendario para próximas semanas
- ✅ Programación basada en mejores días y horarios
- ✅ Sugerencias de tipo de contenido y plataforma
- ✅ Hashtags sugeridos para cada publicación
- ✅ Predicción de engagement esperado

### Detección de Contenido Mejorable
- ✅ Identificación de posts con bajo rendimiento
- ✅ Análisis de problemas específicos por post
- ✅ Cálculo de potencial de mejora
- ✅ Recomendaciones personalizadas de mejora
- ✅ Priorización por impacto potencial

## ✨ Características v5.0

### Análisis de Contenido Viral
- ✅ Detección automática de posts virales
- ✅ Análisis de patrones en contenido viral
- ✅ Top posts virales identificados
- ✅ Distribución de contenido viral por tipo

### Análisis de Correlaciones
- ✅ Impacto de media (imágenes/videos) en engagement
- ✅ Correlación entre longitud del título y engagement
- ✅ Análisis de número óptimo de hashtags
- ✅ Recomendaciones basadas en correlaciones

### Análisis de ROI
- ✅ Cálculo de ROI por tipo de contenido
- ✅ Cálculo de ROI por plataforma
- ✅ Costos estimados vs valor generado
- ✅ Identificación del tipo con mejor ROI

### Benchmarking
- ✅ Comparación con estándares de industria
- ✅ Clasificación (excelente/bueno/promedio/bajo)
- ✅ Identificación de áreas de mejora
- ✅ Métricas comparativas por tipo

## ✨ Características v4.0

### Análisis Predictivo y Detección
- ✅ Detección automática de anomalías (spikes y drops de engagement)
- ✅ Predicciones de engagement para el próximo mes
- ✅ Análisis de tendencias históricas
- ✅ Alertas de cambios significativos
- ✅ Clasificación de severidad (alta/media/baja)

### Exportación y Datos
- ✅ Exportación a CSV (datos detallados y resúmenes)
- ✅ Archivos listos para análisis en Excel/Google Sheets
- ✅ Formato estructurado para integraciones

## ✨ Características v3.0

### Análisis Avanzado
- ✅ Análisis por plataforma (Twitter, LinkedIn, Facebook, Instagram)
- ✅ Identificación de mejor hora y día para publicar
- ✅ Análisis de performance de hashtags
- ✅ Comparación con períodos anteriores
- ✅ Detección de cambios significativos

### Reportes Mejorados
- ✅ Sección de análisis por plataforma
- ✅ Recomendaciones de mejor momento para publicar
- ✅ Top hashtags más efectivos
- ✅ Comparación temporal con indicadores de cambio (📈📉)

## ✨ Características v2.0

### Validación y Robustez
- ✅ Validación de configuración antes de ejecutar
- ✅ Health checks de APIs (OpenAI, PostgreSQL)
- ✅ Validación de mínimo de posts requeridos
- ✅ Sistema de retry con exponential backoff

### Analytics y Tracking
- ✅ Tracking de ejecuciones del workflow
- ✅ Métricas de éxito/fallo
- ✅ Tiempo promedio de ejecución
- ✅ Historial de mejores tipos de contenido
- ✅ Estadísticas acumuladas

### Configuración Avanzada
- ✅ Múltiples variables de entorno para personalización
- ✅ Soporte para Slack (además de Telegram/Email)
- ✅ Flags para habilitar/deshabilitar características

## 📊 Ejemplo de Reporte Completo

El reporte ahora incluye:

1. **Resumen por Tipo de Contenido**: Métricas detalladas por cada tipo
2. **Tipo Ganador**: Análisis del tipo con mayor engagement
3. **Análisis por Plataforma**: Comparación entre plataformas
4. **Mejor Momento para Publicar**: Hora y día óptimos
5. **Top Hashtags**: Los hashtags más efectivos
6. **Anomalías Detectadas**: Posts con engagement inusual
7. **Predicciones**: Forecast para el próximo mes
8. **Comparación Temporal**: Cambios vs período anterior
9. **Análisis de IA**: Explicación de por qué funcionó
10. **5 Nuevas Ideas**: Recomendaciones basadas en datos
11. **Archivos Exportados**: Referencias a CSVs generados
12. **Estadísticas del Workflow**: Métricas de ejecución

## 🔄 Mejoras Futuras

- [ ] Análisis de sentimiento de comentarios
- [ ] Dashboard visual con gráficos interactivos
- [ ] Integración con Google Analytics
- [ ] Exportación a Excel (formato .xlsx)
- [ ] Análisis de competidores
- [ ] Recomendaciones de contenido basadas en tendencias de industria
- [ ] Alertas automáticas por email/Slack cuando hay anomalías
- [ ] API REST para consultar análisis históricos

## 📚 Referencias

- [Documentación de n8n](https://docs.n8n.io/)
- [OpenAI API Documentation](https://platform.openai.com/docs)
- [Esquema de Base de Datos](./../data/db/content_marketing_schema.sql)

## 📄 Licencia

Este workflow es parte del proyecto IA y sigue la misma licencia del proyecto principal.

