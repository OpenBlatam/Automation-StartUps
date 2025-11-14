# 🔗 Guía de Integración Completa - Engagement Tracking

## 📋 Integración Paso a Paso

### Paso 1: Agregar Nodos de Tracking

#### 1.1 Después de "Save Processing Results"

Agrega el nodo **"Save Upload IDs for Tracking"**:

```json
{
  "name": "Save Upload IDs for Tracking",
  "type": "n8n-nodes-base.code",
  "parameters": {
    "jsCode": "// Código del nodo (ver nodos_engagement_optimization.json)"
  },
  "position": [4650, 400]
}
```

**Conexión**: 
- Entrada: Desde "Save Processing Results"
- Salida: Continúa al flujo normal

#### 1.2 Crear Workflow Separado para Tracking

Crea un nuevo workflow **"Sora Engagement Tracker"**:

**Trigger**: Schedule Trigger cada 6 horas

**Nodos**:
1. Get Pending Engagement Checks
2. Fetch Instagram Metrics
3. Fetch TikTok Metrics  
4. Fetch YouTube Metrics
5. Calculate Engagement Metrics
6. Save Engagement Data
7. Detect Viral Content
8. Analyze Top Hashtags
9. Analyze Best Hours
10. Update Learning Model

### Paso 2: Modificar Generación de Contenido

#### 2.1 Antes de "Process AI Generated Content"

Agrega el nodo **"Optimize Hashtags with Learning"**:

```json
{
  "name": "Optimize Hashtags with Learning",
  "type": "n8n-nodes-base.code",
  "position": [3850, 400],
  "parameters": {
    "jsCode": "// Ver código en nodos_engagement_optimization.json"
  }
}
```

**Conexión**:
- Entrada: Desde "Generate Content with ChatGPT/Gemini"
- Salida: A "Process AI Generated Content"

### Paso 3: Configurar APIs de Métricas

#### 3.1 Instagram Graph API

1. Ve a [Facebook Developers](https://developers.facebook.com/)
2. Crea una app o usa existente
3. Agrega producto "Instagram Graph API"
4. Obtén `INSTAGRAM_ACCESS_TOKEN` con permisos:
   - `instagram_basic`
   - `instagram_manage_insights`
   - `pages_read_engagement`

#### 3.2 TikTok Analytics API

1. Ve a [TikTok for Developers](https://developers.tiktok.com/)
2. Crea una app de Business
3. Solicita acceso a Analytics API
4. Obtén access token

#### 3.3 YouTube Analytics API

1. Ve a [Google Cloud Console](https://console.cloud.google.com/)
2. Habilita YouTube Analytics API
3. Crea credenciales OAuth2
4. Obtén `YOUTUBE_API_KEY`

### Paso 4: Configurar Variables de Entorno

```bash
# Tracking
ENABLE_ENGAGEMENT_TRACKING=true

# APIs de Métricas
INSTAGRAM_ACCESS_TOKEN=tu-token-con-insights
TIKTOK_ANALYTICS_TOKEN=tu-tiktok-token
YOUTUBE_API_KEY=tu-youtube-key

# Umbrales
VIRAL_THRESHOLD_ENGAGEMENT_RATE=10.0
VIRAL_THRESHOLD_TOTAL_ENGAGEMENT=500

# Optimización
ENABLE_AUTO_OPTIMIZATION=true
LEARNING_WINDOW_DAYS=30
MIN_VIDEOS_FOR_LEARNING=10
```

## 🔄 Flujo Completo Integrado

### Workflow Principal (Publicación)

```
Schedule Trigger (cada 6h)
    ↓
Initialize Workflow
    ↓
... (búsqueda, descarga, edición) ...
    ↓
Upload to Platforms
    ↓
Save Processing Results
    ↓
Save Upload IDs for Tracking ⭐ NUEVO
    ↓
Cleanup Files
    ↓
Send Notifications
```

### Workflow de Tracking (Separado)

```
Schedule Trigger (cada 6h)
    ↓
Get Pending Engagement Checks
    ↓
Fetch Metrics (Paralelo)
    ├─→ Fetch Instagram Metrics
    ├─→ Fetch TikTok Metrics
    └─→ Fetch YouTube Metrics
    ↓
Calculate Engagement Metrics
    ↓
Save Engagement Data
    ↓
Detect Viral Content
    ↓
Analyze Top Hashtags
    ↓
Analyze Best Hours
    ↓
Update Learning Model
    ↓
Generate Recommendations (Opcional)
```

### Optimización en Generación

```
Generate Content with ChatGPT/Gemini
    ↓
Optimize Hashtags with Learning ⭐ NUEVO
    ↓
Process AI Generated Content
    ↓
(Usa hashtags optimizados)
```

## 📊 Estructura de Datos

### Engagement Queue

```javascript
$workflow.staticData.engagementQueue = [
  {
    videoId: "abc123",
    title: "Video Title",
    hashtags: ["#AI", "#Sora"],
    caption: "Caption text",
    publishedAt: "2024-01-01T12:00:00Z",
    platforms: {
      instagram: { postId: "ig_123", url: "..." },
      tiktok: { postId: "tt_456", url: "..." },
      youtube: { videoId: "yt_789", url: "..." }
    },
    scheduledChecks: {
      after6h: "2024-01-01T18:00:00Z",
      after24h: "2024-01-02T12:00:00Z",
      after48h: "2024-01-03T12:00:00Z",
      after7d: "2024-01-08T12:00:00Z"
    },
    status: "pending"
  }
];
```

### Engagement History

```javascript
$workflow.staticData.engagementHistory = [
  {
    videoId: "abc123",
    platformMetrics: {
      instagram: {
        likes: 1250,
        comments: 45,
        shares: 120,
        impressions: 5000,
        engagementRate: 28.3,
        engagementScore: 2115,
        isViral: true
      }
    },
    overallMetrics: {
      totalEngagement: 1415,
      avgEngagementRate: 28.3,
      bestPlatform: "instagram",
      viralOn: ["instagram"]
    },
    trackedAt: "2024-01-02T12:00:00Z"
  }
];
```

### Learning Model

```javascript
$workflow.staticData.learningModel = {
  updatedAt: "2024-01-15T00:00:00Z",
  totalVideosAnalyzed: 50,
  successfulVideos: 12,
  successRate: 24.0,
  patterns: {
    avgCaptionLength: 245,
    avgHashtagCount: 12,
    bestPlatforms: [
      { platform: "instagram", avgEngagementRate: 15.2 },
      { platform: "tiktok", avgEngagementRate: 8.5 }
    ]
  },
  recommendations: {
    targetCaptionLength: 245,
    targetHashtagCount: 12,
    preferredPlatforms: ["instagram", "tiktok"]
  }
};
```

## 🎯 Casos de Uso

### Caso 1: Primer Video

1. Video se publica
2. IDs se guardan
3. Se programa tracking
4. **Aún no hay aprendizaje** → Usa hashtags generados normalmente

### Caso 2: Después de 10 Videos

1. Sistema tiene datos suficientes
2. Se generan top hashtags
3. Se identifican mejores horarios
4. **Optimización comienza** → Combina hashtags generados + aprendidos

### Caso 3: Después de 50 Videos

1. Sistema tiene mucho aprendizaje
2. Optimización muy precisa
3. Programación inteligente activa
4. **Máxima optimización** → 70% generados, 30% aprendidos (probados)

### Caso 4: Contenido Viral Detectado

1. Sistema detecta contenido viral
2. Analiza qué lo hizo viral
3. Aprende patrones específicos
4. **Replica éxito** → Aplica patrones similares

## 📈 Métricas de Éxito

### KPIs a Monitorear

1. **Engagement Rate Promedio**
   - Objetivo: >10%
   - Mejora esperada: +50% con optimización

2. **Tasa de Contenido Viral**
   - Objetivo: >5% de videos virales
   - Mejora esperada: +100% con aprendizaje

3. **Precisión de Hashtags**
   - Objetivo: Hashtags aprendidos >50% más efectivos
   - Mejora esperada: +40% engagement con hashtags optimizados

4. **Optimización de Horarios**
   - Objetivo: +30% engagement en horarios optimizados
   - Mejora esperada: Programación inteligente funciona

## 🔧 Mantenimiento

### Limpieza de Datos

```javascript
// Limpiar engagement queue (videos completados >30 días)
const engagementQueue = $workflow.staticData.engagementQueue || [];
const thirtyDaysAgo = Date.now() - (30 * 24 * 60 * 60 * 1000);
const cleanedQueue = engagementQueue.filter(q => {
  const publishDate = new Date(q.publishedAt).getTime();
  return publishDate > thirtyDaysAgo || q.status !== 'completed';
});
$workflow.staticData.engagementQueue = cleanedQueue;
```

### Actualización de Modelo

```javascript
// Recalcular modelo de aprendizaje cada semana
const learningModel = $workflow.staticData.learningModel || {};
const lastUpdate = new Date(learningModel.updatedAt || 0);
const weekAgo = Date.now() - (7 * 24 * 60 * 60 * 1000);

if (lastUpdate.getTime() < weekAgo) {
  // Recalcular modelo
  // (ejecutar análisis completo)
}
```

## 🚀 Mejoras Futuras

### Fase 1 (Implementación Inicial)
- ✅ Tracking básico de métricas
- ✅ Cálculo de engagement
- ✅ Detección de contenido viral

### Fase 2 (Aprendizaje Básico)
- ✅ Análisis de top hashtags
- ✅ Análisis de mejores horarios
- ✅ Optimización básica

### Fase 3 (Optimización Avanzada)
- [ ] Análisis de sentimiento de comentarios
- [ ] Análisis de competencia
- [ ] Predicción de engagement antes de publicar
- [ ] A/B testing automático de variantes

### Fase 4 (IA Avanzada)
- [ ] Generación de contenido basada en aprendizaje
- [ ] Predicción de contenido viral
- [ ] Recomendaciones personalizadas por nicho
- [ ] Optimización multi-objetivo

---

**Versión**: 1.0  
**Estado**: ✅ Listo para implementar  
**Requisitos**: APIs de métricas configuradas



