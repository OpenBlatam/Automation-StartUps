# Sistema de Automatización de Marketing de Contenido

Sistema completo para automatizar la distribución de blogs a redes sociales, conversión de artículos a múltiples formatos, programación de publicaciones y tracking de engagement.

## 📋 Características

- ✅ **Conversión Automática**: Convierte artículos a tweets, LinkedIn posts, newsletters y más
- ✅ **Programación Inteligente**: Programa publicaciones en horarios óptimos
- ✅ **Multiplataforma**: Soporta Twitter, LinkedIn, Facebook, Instagram
- ✅ **Tracking de Engagement**: Rastrea métricas automáticamente
- ✅ **Análisis de Performance**: Analiza el rendimiento por artículo y plataforma
- ✅ **Rate Limiting**: Respeta límites de publicación por plataforma
- ✅ **Hilos de Twitter**: Soporte para crear hilos automáticos

## 🏗️ Arquitectura

```
┌─────────────────┐
│   Artículos     │
│   (Blogs)       │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│   Conversor     │───► Twitter
│   de Contenido  │───► LinkedIn
└────────┬────────┘───► Newsletter
         │
         ▼
┌─────────────────┐
│   Programador   │
│   de Posts      │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│   Publicador    │
│   Social Media  │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│   Tracker de    │
│   Engagement    │
└─────────────────┘
```

## 📦 Componentes

### 1. Esquema de Base de Datos

**Archivo**: `data/db/content_marketing_schema.sql`

Tablas principales:
- `content_articles`: Artículos/blogs
- `content_versions`: Versiones convertidas por plataforma
- `content_scheduled_posts`: Posts programados
- `content_engagement`: Métricas de engagement
- `content_platform_config`: Configuración de plataformas
- `content_performance_analysis`: Análisis de performance

### 2. Conversor de Contenido

**Archivo**: `data/airflow/plugins/content_converter.py`

Convierte artículos a múltiples formatos:

```python
from content_converter import ContentConverter, ContentFormat

converter = ContentConverter(db_connection)

versions = converter.convert_article(
    article_id="art-123",
    title="Cómo Automatizar Marketing",
    content="Contenido completo del artículo...",
    formats=[ContentFormat.TWITTER, ContentFormat.LINKEDIN, ContentFormat.NEWSLETTER],
    url="https://example.com/blog/art-123",
    author="Juan Pérez",
    tags=["marketing", "automatización"]
)
```

**Formatos soportados**:
- `TWITTER`: Tweets (280 caracteres)
- `LINKEDIN`: Posts de LinkedIn (3000 caracteres)
- `NEWSLETTER`: Versión para email
- `THREAD`: Hilos de Twitter (múltiples tweets)

### 3. Programador de Publicaciones

**Archivo**: `data/airflow/plugins/content_scheduler.py`

Programa publicaciones en horarios óptimos:

```python
from content_scheduler import ContentScheduler

scheduler = ContentScheduler(db_connection)

# Programar un post
post_id = scheduler.schedule_post(
    article_id="art-123",
    version_id=456,
    platform="twitter",
    account_id="acc-twitter-1",
    scheduled_at=datetime(2024, 1, 15, 9, 0)  # Opcional
)

# Programar artículo a múltiples plataformas
post_ids = scheduler.schedule_article_to_platforms(
    article_id="art-123",
    platforms=["twitter", "linkedin", "facebook"],
    delay_hours=2,  # Esperar 2 horas antes de primera publicación
    stagger_hours=3  # 3 horas entre cada plataforma
)
```

**Horarios óptimos por defecto**:
- Twitter: 09:00, 13:00, 17:00, 21:00
- LinkedIn: 08:00, 12:00, 17:00
- Facebook: 09:00, 15:00, 20:00
- Instagram: 11:00, 14:00, 17:00, 20:00

### 4. Publicador en Redes Sociales

**Archivo**: `data/airflow/plugins/social_media_publisher.py`

Publica contenido en redes sociales:

```python
from social_media_publisher import SocialMediaPublisher

publisher = SocialMediaPublisher(db_connection)

# Publicar en Twitter
result = publisher.publish_to_twitter(
    content="Nuevo artículo sobre automatización...",
    media_urls=["https://example.com/image.jpg"],
    account_id="acc-twitter-1"
)

if result.success:
    print(f"Publicado: {result.post_id}")
    print(f"URL: {result.post_url}")
```

**Plataformas soportadas**:
- Twitter/X
- LinkedIn
- Facebook
- Instagram (próximamente)

### 5. Tracker de Engagement

**Archivo**: `data/airflow/plugins/engagement_tracker.py`

Rastrea métricas de engagement:

```python
from engagement_tracker import EngagementTracker

tracker = EngagementTracker(db_connection)

# Rastrear todos los posts pendientes
stats = tracker.track_all_pending_posts()
print(f"Tracked: {stats['tracked']}, Failed: {stats['failed']}")

# Obtener performance de un artículo
performance = tracker.get_article_performance("art-123", days=30)
print(f"Total engagement: {performance['totals']['total_engagement']}")
print(f"Platform breakdown: {performance['platform_breakdown']}")
```

**Métricas rastreadas**:
- Likes, comentarios, shares, retweets
- Impresiones y reach
- Engagement rate
- Click-through rate

## 🚀 Configuración

### 1. Instalar Esquema de BD

```bash
psql -d tu_database -f data/db/content_marketing_schema.sql
```

### 2. Configurar Plataformas

```sql
-- Configurar Twitter
INSERT INTO content_platform_config
(platform, account_id, account_name, api_key, api_secret, access_token, access_token_secret, is_active)
VALUES
('twitter', 'acc-twitter-1', 'Mi Cuenta Twitter', 'api_key', 'api_secret', 'access_token', 'access_token_secret', TRUE);

-- Configurar LinkedIn
INSERT INTO content_platform_config
(platform, account_id, account_name, access_token, is_active, daily_post_limit, hourly_post_limit)
VALUES
('linkedin', 'acc-linkedin-1', 'Mi Cuenta LinkedIn', 'access_token', TRUE, 10, 2);
```

### 3. Configurar Conexión de Airflow

En Airflow UI, crear conexión:
- Connection ID: `postgres_default`
- Conn Type: `Postgres`
- Host: `tu_host`
- Schema: `tu_database`
- Login: `tu_usuario`
- Password: `tu_password`

### 4. Activar DAG

El DAG `content_marketing_automation` se ejecuta cada hora automáticamente.

## 📝 Uso

### Crear un Artículo

```sql
INSERT INTO content_articles
(article_id, title, content, author, source_url, status, published_at, tags)
VALUES
(
    'art-001',
    'Cómo Automatizar Marketing de Contenido',
    'Contenido completo del artículo...',
    'Juan Pérez',
    'https://example.com/blog/art-001',
    'published',
    NOW(),
    ARRAY['marketing', 'automatización', 'contenido']
);
```

### Convertir Manualmente

```python
from airflow.operators.python import PythonOperator

def convert_article():
    from content_converter import ContentConverter
    import psycopg2
    
    db = psycopg2.connect(...)
    converter = ContentConverter(db)
    
    versions = converter.convert_article(
        article_id="art-001",
        title="Título del artículo",
        content="Contenido...",
        formats=[ContentFormat.TWITTER, ContentFormat.LINKEDIN]
    )
    
    converter.save_versions(versions)
```

### Programar Publicación

```python
from content_scheduler import ContentScheduler

scheduler = ContentScheduler(db)

# Programar para mañana a las 9 AM
tomorrow_9am = datetime.now().replace(hour=9, minute=0) + timedelta(days=1)

post_id = scheduler.schedule_post(
    article_id="art-001",
    version_id=1,
    platform="twitter",
    scheduled_at=tomorrow_9am
)
```

## 📊 Análisis de Performance

### Ver Métricas por Artículo

```sql
SELECT 
    a.title,
    COUNT(DISTINCT sp.post_id) as total_posts,
    SUM(ce.likes) as total_likes,
    SUM(ce.comments) as total_comments,
    SUM(ce.shares) as total_shares,
    AVG(ce.engagement_rate) as avg_engagement_rate
FROM content_articles a
LEFT JOIN content_scheduled_posts sp ON a.article_id = sp.article_id
LEFT JOIN content_engagement ce ON sp.post_id = ce.post_id
WHERE a.published_at >= NOW() - INTERVAL '30 days'
GROUP BY a.article_id, a.title
ORDER BY avg_engagement_rate DESC;
```

### Ver Performance por Plataforma

```sql
SELECT 
    platform,
    COUNT(*) as total_posts,
    AVG(engagement_rate) as avg_engagement_rate,
    SUM(impressions) as total_impressions,
    SUM(reach) as total_reach
FROM content_engagement
WHERE tracked_at >= NOW() - INTERVAL '7 days'
GROUP BY platform
ORDER BY avg_engagement_rate DESC;
```

## 🔧 Personalización

### Crear Template de Conversión Personalizado

```sql
INSERT INTO content_conversion_templates
(template_name, platform, version_type, template_content, max_length, is_default)
VALUES
(
    'twitter_tech',
    'twitter',
    'twitter',
    '🚀 {title}\n\n{excerpt}\n\n{url}\n\n{hashtags}',
    280,
    FALSE
);
```

### Ajustar Horarios Óptimos

Modificar `OPTIMAL_TIMES` en `content_scheduler.py`:

```python
OPTIMAL_TIMES = {
    "twitter": ["10:00", "14:00", "18:00"],  # Personalizados
    "linkedin": ["09:00", "13:00", "17:00"],
}
```

## 🐛 Troubleshooting

### Posts no se publican

1. Verificar configuración de plataforma:
```sql
SELECT * FROM content_platform_config WHERE platform = 'twitter' AND is_active = TRUE;
```

2. Verificar rate limits:
```sql
SELECT COUNT(*) FROM content_scheduled_posts
WHERE platform = 'twitter'
AND DATE(scheduled_at) = CURRENT_DATE;
```

3. Revisar logs de Airflow para errores de API

### Engagement no se rastrea

1. Verificar que posts tengan `published_post_id`:
```sql
SELECT post_id, platform, published_post_id, published_at
FROM content_scheduled_posts
WHERE status = 'published'
AND published_post_id IS NULL;
```

2. Verificar tokens de API en `content_platform_config`

### Errores de conversión

1. Verificar que el contenido no esté vacío
2. Verificar límites de caracteres por plataforma
3. Revisar logs para mensajes de error específicos

## 📈 Mejores Prácticas

1. **Aprobar versiones antes de publicar**: Revisar versiones convertidas antes de aprobarlas
2. **Espaciar publicaciones**: Usar `stagger_hours` para no saturar redes
3. **Monitorear engagement**: Revisar métricas regularmente para optimizar
4. **Ajustar horarios**: Analizar cuándo tu audiencia está más activa
5. **Variar contenido**: No publicar el mismo contenido en todas las plataformas simultáneamente

## 🔐 Seguridad

- **Credenciales**: Almacenar tokens de API encriptados o usar Airflow Secrets
- **Rate Limits**: Respetar límites de cada plataforma
- **Validación**: Validar contenido antes de publicar
- **Logs**: No registrar tokens o credenciales en logs

## 📚 Recursos

- [Twitter API v2 Docs](https://developer.twitter.com/en/docs/twitter-api)
- [LinkedIn API Docs](https://docs.microsoft.com/en-us/linkedin/)
- [Facebook Graph API](https://developers.facebook.com/docs/graph-api)

## 🆘 Soporte

Para problemas o preguntas:
1. Revisar logs de Airflow
2. Verificar estado de la BD
3. Consultar documentación de APIs de cada plataforma

