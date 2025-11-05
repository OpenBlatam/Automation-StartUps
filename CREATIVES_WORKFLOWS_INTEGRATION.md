---
title: "Integración Creativos SVG + Workflows Automatizados"
category: "automation"
tags: ["svg","creatives","workflows","make","zapier"]
created: "2025-10-30"
path: "CREATIVES_WORKFLOWS_INTEGRATION.md"
---

# 🎨 Integración Creativos SVG + Workflows Automatizados

Guía para conectar tus plantillas SVG (webinar prerolls, LinkedIn ads, Instagram templates) con automatizaciones en Make/Zapier.

## ✨ Últimas Mejoras

**v2.0** - 2025-10-30:
- ✅ Catálogo completo actualizado con **todos los formatos** (cuadrado 1080×1080, carousels)
- ✅ **5 recetas Make/Zapier** listas para usar (webinar, testimonial, batch ads, carousel, multi-platform)
- ✅ **Workflow de carousels** automatizado (5 slides en batch)
- ✅ **Routing inteligente** multi-criterio (formato + plataforma + audiencia)
- ✅ **Multi-platform distribution** (Instagram + LinkedIn + Facebook en paralelo)
- ✅ Config JSON actualizado con todos los templates y variables
- ✅ Sistema de A/B testing integrado en workflows

## 📑 ÍNDICE

- [Catálogo de Creativos SVG](#catálogo-de-creativos-svg)
- [Workflows por Tipo de Creativo](#workflows-por-tipo-de-creativo)
- [Automatización de Personalización](#automatización-de-personalización)
- [Integración con Campañas](#integración-con-campañas)
- [Recetas Make/Zapier](#recetas-makezapier)

---

## 📦 Catálogo de Creativos SVG

### Webinar Prerolls

#### Horizontal (1920×1080)

| Archivo | Estilo | Caso de uso | Variables editables |
|---------|--------|-------------|---------------------|
| `webinar-preroll-benefits-focused.svg` | Beneficios destacados | Webinar educativo, curso IA | `[FECHA]`, `[HORA]`, `[EVENTO]`, `[CTA]` |
| `webinar-preroll-social-proof.svg` | Prueba social | Webinars con testimonios | `[TESTIMONIO]`, `[NOMBRE]`, `[COMPANY]`, `[FECHA]` |
| `webinar-preroll-elegant.svg` | Minimal elegante | Webinars premium | `[EVENTO]`, `[PONENTE]`, `[FECHA]`, `[HORA]` |
| `webinar-preroll-center-card.svg` | Centro destacado | CTA principal visible | `[CTA]`, `[URL]`, `[EVENTO]` |
| `webinar-preroll-speaker-focused.svg` | Ponente destacado | Webinars con expertos | `[PONENTE]`, `[BIO]`, `[EVENTO]`, `[FECHA]` |
| `webinar-preroll-urgent-v2.svg` | Urgencia | Cupos limitados | `[FECHA_CIERRE]`, `[CUPOS]`, `[EVENTO]` |
| `webinar-preroll-minimal.svg` | Minimal | Versión limpia | `[EVENTO]`, `[FECHA]`, `[HORA]` |
| `webinar-preroll-video-thumbnail.svg` | Thumbnail optimizado | YouTube thumbnails | `[TÍTULO]`, `[MÉTRICA]`, `[CTA]` |
| `webinar-preroll-compare.svg` | Comparación Antes/Después | Casos de éxito, transformación | `[ANTES]`, `[DESPUÉS]`, `[MÉTRICA]`, `[EVENTO]` |
| `webinar-preroll-numbers.svg` | Métricas destacadas | Resultados numéricos | `[NÚMERO]`, `[LABEL]`, `[EVENTO]`, `[CTA]` |

**Dimensiones**: 1920×1080 (16:9 horizontal)
**Uso**: Videos de YouTube, presentaciones, intros de webinar

#### Cuadrado (1080×1080)

| Archivo | Estilo | Caso de uso | Variables editables |
|---------|--------|-------------|---------------------|
| `webinar-square-1080x1080-dark.svg` | Dark mode | Instagram Stories, LinkedIn | `[FECHA]`, `[HORA]`, `[EVENTO]`, `[CTA]`, `[URL]` |
| `webinar-square-1080x1080-light.svg` | Light mode | LinkedIn, Facebook Stories | `[FECHA]`, `[HORA]`, `[EVENTO]`, `[CTA]` |
| `webinar-square-1080x1080-benefits.svg` | Beneficios destacados | Webinars con valor | `[BENEFICIO_1]`, `[BENEFICIO_2]`, `[BENEFICIO_3]`, `[EVENTO]` |
| `webinar-square-1080x1080-social-proof.svg` | Prueba social | Webinars con testimonios | `[TESTIMONIO]`, `[NOMBRE]`, `[EVENTO]`, `[CTA]` |

**Dimensiones**: 1080×1080 (1:1 cuadrado)
**Uso**: Instagram Stories, LinkedIn Posts, Facebook Stories, Twitter

---

### Instagram Templates (1080×1350)

| Archivo | Estilo | Caso de uso | Variables |
|---------|--------|-------------|-----------|
| `instagram_antes_despues_template.svg` | Antes/Después | Casos de éxito, transformación | `[PROBLEMA]`, `[RESULTADO]`, `[MÉTRICA]` |

**Dimensiones**: 1080×1350 (4:5 vertical)
**Uso**: Instagram Feed, Stories (con recorte)

---

### Formatos Verticales (1080×1920) - Stories/Reels

#### Webinar Vertical

| Archivo | Estilo | Caso de uso | Variables editables |
|---------|--------|-------------|---------------------|
| `webinar-vertical-1080x1920.svg` | Vertical completo | Instagram Stories, TikTok | `[EVENTO]`, `[FECHA]`, `[HORA]`, `[CTA]`, `[URL]` |

**Dimensiones**: 1080×1920 (9:16 vertical)
**Uso**: Instagram Stories, TikTok, YouTube Shorts, Facebook Stories

#### LinkedIn Ads Vertical (1080×1920)

**Ubicación**: `ads/linkedin/`

| Archivo | Producto | Estilo | Variables |
|---------|---------|--------|-----------|
| `ad_curso_ia_1080x1920.svg` | Curso IA | Vertical Stories | `[MÉTRICA]`, `[BENEFICIO]`, `[TESTIMONIO]`, `[CTA]` |
| `ad_curso_ia_1080x1920_metrics.svg` | Curso IA | Métricas verticales | `[MÉTRICA]`, `[HOOK]`, `[CTA]` |
| `ad_saas_ia_marketing_1080x1920.svg` | SaaS Marketing | Vertical Stories | `[MÉTRICA]`, `[BENEFICIO]`, `[TESTIMONIO]`, `[CTA]` |
| `ad_saas_ia_marketing_1080x1920_metrics.svg` | SaaS Marketing | Métricas verticales | `[CTR]`, `[CPA]`, `[CTA]` |
| `ad_ia_bulk_1080x1920.svg` | IA Bulk | Vertical Stories | `[MÉTRICA]`, `[BENEFICIO]`, `[TESTIMONIO]`, `[CTA]` |
| `ad_ia_bulk_1080x1920_metrics.svg` | IA Bulk | Métricas verticales | `[MÉTRICA]`, `[HOOK]`, `[CTA]` |

**Dimensiones**: 1080×1920 (9:16 vertical)
**Uso**: Instagram Stories, TikTok, LinkedIn Stories (vertical), Facebook Stories

---

### LinkedIn Ads

**Ubicación**: `ads/linkedin/`

#### Horizontal (1200×627)

| Archivo | Producto | Estilo | Variables |
|---------|---------|--------|-----------|
| `ad_curso_ia_1200x627_metrics.svg` | Curso IA | Métricas destacadas | `[MÉTRICA]`, `[BENEFICIO]`, `[HOOK]`, `[CTA]` |
| `ad_curso_ia_1200x627_v2.svg` | Curso IA | Variante 2 | `[HOOK]`, `[CTA]`, `[BENEFICIO]` |
| `ad_saas_ia_marketing_1200x627_metrics.svg` | SaaS Marketing | CTR/CPA destacados | `[CTR]`, `[CPA]`, `[MÉTRICA]`, `[CTA]` |
| `ad_saas_ia_marketing_1200x627_urgency.svg` | SaaS Marketing | Urgencia | `[FECHA]`, `[OFERTA]`, `[CTA]` |
| `ad_saas_ia_marketing_1200x627_v2.svg` | SaaS Marketing | Variante 2 | `[BENEFICIO]`, `[CTA]`, `[HOOK]` |
| `ad_ia_bulk_1200x627_metrics.svg` | IA Bulk | Métricas | `[MÉTRICA]`, `[BENEFICIO]`, `[CTA]` |
| `ad_ia_bulk_1200x627_v2.svg` | IA Bulk | Variante 2 | `[BENEFICIO]`, `[CTA]`, `[HOOK]` |

**Dimensiones**: 1200×627 (1.91:1 horizontal)
**Uso**: LinkedIn Sponsored Content, Facebook Feed

#### Cuadrado (1080×1080)

| Archivo | Producto | Estilo | Variables |
|---------|---------|--------|-----------|
| `ad_curso_ia_1080x1080.svg` | Curso IA | Estilo moderno | `[MÉTRICA]`, `[BENEFICIO]`, `[TESTIMONIO]`, `[CTA]` |
| `ad_curso_ia_1080x1080_metrics.svg` | Curso IA | Métricas destacadas | `[MÉTRICA]`, `[HOOK]`, `[CTA]` |
| `ad_saas_ia_marketing_1080x1080.svg` | SaaS Marketing | Estilo moderno | `[MÉTRICA]`, `[BENEFICIO]`, `[TESTIMONIO]`, `[CTA]` |
| `ad_saas_ia_marketing_1080x1080_metrics.svg` | SaaS Marketing | Métricas destacadas | `[CTR]`, `[CPA]`, `[CTA]` |
| `ad_ia_bulk_1080x1080.svg` | IA Bulk | Estilo moderno | `[MÉTRICA]`, `[BENEFICIO]`, `[TESTIMONIO]`, `[CTA]` |
| `ad_ia_bulk_1080x1080_metrics.svg` | IA Bulk | Métricas destacadas | `[MÉTRICA]`, `[HOOK]`, `[CTA]` |

**Dimensiones**: 1080×1080 (1:1 cuadrado)
**Uso**: LinkedIn Sponsored Content (cuadrado), Instagram Feed, Facebook Feed

#### Carousels (1080×1080 cada slide)

| Archivo | Orden | Contenido | Variables |
|---------|-------|-----------|-----------|
| `carousel_slide_1_hook_1080x1080.svg` | 1/5 | Hook principal | `[HOOK]`, `[MÉTRICA]`, `[PRODUCTO]` |
| `carousel_slide_2_curso_1080x1080.svg` | 2/5 | Curso IA | `[BENEFICIO_1]`, `[BENEFICIO_2]`, `[CTA]` |
| `carousel_slide_3_saas_1080x1080.svg` | 3/5 | SaaS Marketing | `[MÉTRICA]`, `[TESTIMONIO]`, `[CTA]` |
| `carousel_slide_4_bulk_1080x1080.svg` | 4/5 | IA Bulk | `[BENEFICIO]`, `[CASO_USO]`, `[CTA]` |
| `carousel_slide_5_cta_1080x1080.svg` | 5/5 | CTA final | `[CTA]`, `[URL]`, `[OFERTA]` |

**Dimensiones**: 1080×1080 cada slide (carousel 5 slides)
**Uso**: LinkedIn Carousel Ads, Facebook Carousel
**Workflow especial**: Generar secuencia completa automáticamente

---

## 🔄 Workflows por Tipo de Creativo

### Webinar Preroll → Automatización

**Flujo completo:**
```
Evento creado → Seleccionar template SVG → Personalizar variables → Exportar PNG/MP4 → Subir a YouTube/Plataforma
```

**Workflow Make/Zapier:**

1. **Trigger**: Calendly event created o Google Calendar event
   - Campos: `event_name`, `date`, `time`, `speaker_name`, `topic`

2. **Router**: Seleccionar template según tipo webinar
   - Si `topic` contiene "curso" → `webinar-preroll-benefits-focused.svg`
   - Si tiene ponente destacado → `webinar-preroll-speaker-focused.svg`
   - Si es urgente → `webinar-preroll-urgent-v2.svg`

3. **SVG Processing** (Make/Zapier + herramienta):
   - Option A: **Make HTTP module** → Servicio que procesa SVG (Node.js/Python)
   - Option B: **Canva API** → Crear diseño desde template + variables
   - Option C: **Figma API** → Actualizar componentes + exportar

4. **Variables a reemplazar**:
   ```json
   {
     "FECHA": "{{event.date}}",
     "HORA": "{{event.time}} (GMT-5)",
     "EVENTO": "{{event.title}}",
     "PONENTE": "{{event.speaker}}",
     "CTA": "Reserva tu plaza",
     "URL": "{{event.calendly_link}}"
   }
   ```

5. **Export**: Convertir SVG → PNG/MP4 (ImageMagick, FFmpeg, o servicio)
6. **Upload**: Subir a YouTube como thumbnail o intro video
7. **Log**: Guardar URL del asset en CRM (campaign asset)

---

### Instagram Template → Story/Post Automatizado

**Flujo completo:**
```
Caso éxito detectado → Generar antes/después → Post en Instagram → Trackear performance
```

**Workflow Make/Zapier:**

1. **Trigger**: Deal won en CRM o Testimonial form submit
   - Campos: `customer_name`, `before_metric`, `after_metric`, `product`

2. **Template Selection**: `instagram_antes_despues_template.svg`

3. **Variables a reemplazar**:
   ```json
   {
     "PROBLEMA": "Antes: {{before_metric}}",
     "RESULTADO": "Después: {{after_metric}}",
     "MÉTRICA": "{{improvement_percentage}}% mejora",
     "PRODUCTO": "{{product_name}}",
     "TESTIMONIO": "{{testimonial_quote}}"
   }
   ```

4. **Processing**: SVG → PNG (1080×1350)
5. **Instagram API**: Upload como Feed Post
6. **Tracking**: Crear UTM campaign `instagram_post_case_study_[date]`
7. **CRM Update**: Log post URL en Contact/Deal

---

### LinkedIn Ads → Rotación Automatizada

**Flujo completo:**
```
Campaign creada → Seleccionar variantes A/B → Personalizar por audiencia → Publicar → Optimizar
```

**Workflow Make/Zapier:**

1. **Trigger**: Campaign created en Meta Ads Manager o CSV upload
   - Campos: `product`, `audience`, `hook_variant`, `cta_variant`

2. **Template Selection** (router):
   - Producto = "curso_ia" → `ad_curso_ia_1200x627_*.svg`
   - Producto = "saas_marketing" → `ad_saas_ia_marketing_1200x627_*.svg`
   - Producto = "ia_bulk" → `ad_ia_bulk_1200x627_*.svg`

3. **Variant Selection**:
   - Si `hook_variant = "metrics"` → `*_metrics.svg`
   - Si `hook_variant = "urgency"` → `*_urgency.svg`
   - Si `hook_variant = "social_proof"` → `*_social_proof.svg`

4. **Variables personalizadas**:
   ```json
   {
     "MÉTRICA": "{{industry_metric}}",
     "BENEFICIO": "{{value_prop}}",
     "CTA": "{{cta_text}}",
     "FECHA": "{{campaign_end_date}}",
     "HOOK": "{{hook_variant_text}}"
   }
   ```

5. **Export**: SVG → PNG 1200×627
6. **Meta Ads API**: Crear Ad Creative + Ad Set
7. **UTM Tracking**: `utm_content` = `[product]-[variant]-[hook]-[cta]`
8. **Performance Monitoring**: Trackear CTR, CPC por variante

---

### Webinar Square (1080×1080) → Multi-Platform

**Flujo completo:**
```
Webinar creado → Generar formato cuadrado → Distribuir a Instagram/Linkedin/Facebook → Trackear engagement
```

**Workflow Make/Zapier:**

1. **Trigger**: Calendly/Google Calendar event created
   - Campos: `event_name`, `date`, `time`, `event_type`

2. **Template Selection** (router):
   - Si `event_type = "webinar"` y `platform_preference = "instagram"` → `webinar-square-1080x1080-dark.svg`
   - Si `platform_preference = "linkedin"` → `webinar-square-1080x1080-light.svg`
   - Si `audience_demographic = "young"` → dark mode
   - Si `audience_demographic = "professional"` → light mode

3. **Variables**:
   ```json
   {
     "FECHA": "{{event.date}}",
     "HORA": "{{event.time}}",
     "EVENTO": "{{event.title}}",
     "CTA": "Únete gratis",
     "URL": "{{event.calendly_link}}"
   }
   ```

4. **Processing**: SVG → PNG (1080×1080)
5. **Multi-Platform Upload** (paralelo):
   - **Instagram API**: Upload como Story (puede auto-postear)
   - **LinkedIn API**: Create post con imagen
   - **Facebook API**: Upload a página como post
6. **UTM Tracking**:
   - `utm_source` = `instagram`|`linkedin`|`facebook`
   - `utm_medium` = `story`|`post`
   - `utm_content` = `webinar-square-[event_date]`
7. **Performance Tracking**: Monitorear engagement por plataforma

---

### Carousel Campaign → Batch Generation

**Flujo completo:**
```
Campaign definida → Generar 5 slides personalizados → Crear carousel → Publicar → A/B test
```

**Workflow Make/Zapier:**

1. **Trigger**: Campaign brief creado (CSV, Google Sheet, o Form)
   - Campos: `product`, `target_audience`, `hook_variant`, `cta_variant`, `metrics`

2. **Slide Generation Loop** (5 iteraciones):
   
   **Slide 1 (Hook)**:
   - Template: `carousel_slide_1_hook_1080x1080.svg`
   - Variables:
     ```json
     {
       "HOOK": "{{hook_variant}}",
       "MÉTRICA": "{{primary_metric}}",
       "PRODUCTO": "{{product_name}}"
     }
     ```
   
   **Slide 2 (Curso IA)**:
   - Template: `carousel_slide_2_curso_1080x1080.svg`
   - Variables:
     ```json
     {
       "BENEFICIO_1": "Prompts que bajan CPA",
       "BENEFICIO_2": "Creatividades en minutos",
       "CTA": "Ver temario"
     }
     ```
   
   **Slide 3 (SaaS Marketing)**:
   - Template: `carousel_slide_3_saas_1080x1080.svg`
   - Variables:
     ```json
     {
       "MÉTRICA": "{{ctr_metric}}% CTR",
       "TESTIMONIO": "{{testimonial_quote}}",
       "CTA": "Prueba gratis"
     }
     ```
   
   **Slide 4 (IA Bulk)**:
   - Template: `carousel_slide_4_bulk_1080x1080.svg`
   - Variables:
     ```json
     {
       "BENEFICIO": "Documentos en minutos",
       "CASO_USO": "{{use_case_example}}",
       "CTA": "Ver demo"
     }
     ```
   
   **Slide 5 (CTA Final)**:
   - Template: `carousel_slide_5_cta_1080x1080.svg`
   - Variables:
     ```json
     {
       "CTA": "{{final_cta}}",
       "URL": "{{landing_url}}?utm_content=carousel-cta",
       "OFERTA": "{{special_offer}}"
     }
     ```

3. **Processing**: Cada SVG → PNG (1080×1080)
4. **Carousel Assembly**:
   - **LinkedIn API**: Create carousel ad with 5 images
   - **Facebook API**: Create carousel ad
   - Orden: Mantener secuencia lógica (hook → producto → CTA)
5. **UTM Tracking**:
   - `utm_content` = `carousel-[product]-[hook]-[date]`
   - Cada slide puede tener UTM diferente para tracking granular
6. **A/B Testing Setup**:
   - Variante A: Hook directo
   - Variante B: Hook con métrica
   - Variante C: Hook con testimonial
7. **Performance Monitoring**:
   - Trackear engagement por slide (swipe-through rate)
   - Optimizar orden de slides según performance

---

### Vertical Stories (1080×1920) → Multi-Platform Distribution

**Flujo completo:**
```
Evento/Campaign → Generar formato vertical → Distribuir a Stories/Reels → Trackear engagement por plataforma
```

**Workflow Make/Zapier:**

1. **Trigger**: Webinar event o Campaign launch
   - Campos: `event_name`, `date`, `product`, `platform_target`

2. **Template Selection** (router por producto):
   - `product = "webinar"` → `webinar-vertical-1080x1920.svg`
   - `product = "curso_ia"` → `ad_curso_ia_1080x1920.svg` o `ad_curso_ia_1080x1920_metrics.svg`
   - `product = "saas_marketing"` → `ad_saas_ia_marketing_1080x1920.svg` o `ad_saas_ia_marketing_1080x1920_metrics.svg`
   - `product = "ia_bulk"` → `ad_ia_bulk_1080x1920.svg` o `ad_ia_bulk_1080x1920_metrics.svg`

3. **Variant Selection** (si aplica):
   - Si `hook_variant = "metrics"` → usar template `*_metrics.svg`
   - Si `hook_variant = "social_proof"` → usar template base

4. **Variables**:
   ```json
   {
     "EVENTO": "{{event.title}}",
     "FECHA": "{{event.date}}",
     "HORA": "{{event.time}}",
     "CTA": "Únete gratis",
     "URL": "{{event.calendly_link}}",
     "MÉTRICA": "{{primary_metric}}",
     "BENEFICIO": "{{value_prop}}",
     "TESTIMONIO": "{{testimonial_quote}}"
   }
   ```

5. **Processing**: SVG → PNG (1080×1920)
6. **Multi-Platform Upload** (paralelo):
   - **Instagram Stories API**: Upload como Story (24h)
     * Link sticker: `{{url}}?utm_source=instagram&utm_medium=story&utm_content=vertical-{{product}}`
   - **TikTok API**: Upload como video/image ad
   - **LinkedIn Stories API**: Upload como Story
   - **Facebook Stories API**: Upload a página como Story
   - **YouTube Shorts**: Upload como Short (si es video)
7. **UTM Tracking por plataforma**:
   - `utm_source` = `instagram`|`tiktok`|`linkedin`|`facebook`|`youtube`
   - `utm_medium` = `story`|`reel`|`short`
   - `utm_content` = `vertical-{{product}}-{{variant}}`
8. **Performance Tracking**:
   - Instagram: Views, exits, link clicks, replies
   - TikTok: Views, engagement, clicks
   - LinkedIn: Impressions, clicks
   - Comparar CTR por plataforma para optimización

---

### Routing Inteligente Mejorado

**Sistema de decisión multi-criterio:**

```javascript
function selectTemplate(context) {
  const { product, format, hook_variant, audience, platform } = context;
  
  // Prioridad 1: Formato y plataforma
  if (format === "square" && platform === "instagram") {
    if (product === "webinar") {
      return audience === "young" 
        ? "webinar-square-1080x1080-dark.svg"
        : "webinar-square-1080x1080-light.svg";
    }
    if (product === "curso_ia") {
      return hook_variant === "metrics"
        ? "ad_curso_ia_1080x1080_metrics.svg"
        : "ad_curso_ia_1080x1080.svg";
    }
  }
  
  // Prioridad 2: Hook variant
  if (hook_variant === "metrics") {
    return `ad_${product}_1080x1080_metrics.svg`;
  }
  
  // Prioridad 3: Default por producto
  const defaults = {
    "curso_ia": "ad_curso_ia_1080x1080.svg",
    "saas_marketing": "ad_saas_ia_marketing_1080x1080.svg",
    "ia_bulk": "ad_ia_bulk_1080x1080.svg"
  };
  
  return defaults[product] || defaults["curso_ia"];
}
```

**Implementación en Make/Zapier:**
1. **Router Module**: Evaluar criterios en orden de prioridad
2. **Data Store**: Guardar mapeo de decisiones para aprendizaje
3. **A/B Testing**: Rotar entre 2-3 templates automáticamente
4. **Auto-Optimize**: Pausar templates con <15% CTR, escalar >25% CTR

---

## 🤖 Automatización de Personalización

### Opción 1: Script Python (procesamiento local)

**Archivo**: `svg_processor.py`

```python
#!/usr/bin/env python3
import re
import sys
from pathlib import Path

def replace_svg_variables(svg_path, variables):
    """Reemplaza variables [VAR] en SVG con valores."""
    with open(svg_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    for var, value in variables.items():
        pattern = rf'\[{var}\]'
        content = re.sub(pattern, str(value), content)
    
    output_path = svg_path.parent / f"{svg_path.stem}_personalized.svg"
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    return output_path

if __name__ == "__main__":
    svg_file = sys.argv[1]
    vars_json = sys.argv[2]  # JSON string
    import json
    variables = json.loads(vars_json)
    result = replace_svg_variables(Path(svg_file), variables)
    print(str(result))
```

**Uso en Make/Zapier:**
1. Code/Python module: Ejecutar script con variables
2. HTTP module: POST a servicio que procesa SVG
3. File storage: Guardar resultado

---

### Opción 2: Node.js Service (recomendado)

**Archivo**: `svg-processor-service.js`

```javascript
const express = require('express');
const fs = require('fs').promises;
const { exec } = require('child_process').promises;

const app = express();
app.use(express.json());

app.post('/process-svg', async (req, res) => {
  const { template_path, variables, output_format = 'png' } = req.body;
  
  // Leer SVG
  let svg = await fs.readFile(template_path, 'utf-8');
  
  // Reemplazar variables
  Object.entries(variables).forEach(([key, value]) => {
    svg = svg.replace(new RegExp(`\\[${key}\\]`, 'g'), value);
  });
  
  // Guardar temporal
  const temp_svg = `/tmp/${Date.now()}.svg`;
  await fs.writeFile(temp_svg, svg);
  
  // Convertir a PNG (ImageMagick) o mantener SVG
  if (output_format === 'png') {
    await exec(`convert ${temp_svg} ${temp_svg.replace('.svg', '.png')}`);
    const png = await fs.readFile(temp_svg.replace('.svg', '.png'));
    res.type('image/png').send(png);
  } else {
    res.type('image/svg+xml').send(svg);
  }
  
  await fs.unlink(temp_svg);
});

app.listen(3000, () => console.log('SVG Processor running on :3000'));
```

---

### Opción 3: Make/Zapier HTTP + Servicio

**Receta Make:**

1. **Trigger**: Webhook o CRM event
2. **Data Store**: Obtener template path y variables
3. **HTTP**: POST a servicio de procesamiento SVG
   ```
   POST https://tu-servicio.com/process-svg
   Body: {
     "template": "webinar-preroll-benefits-focused.svg",
     "variables": {
       "FECHA": "2025-11-15",
       "HORA": "14:00 (GMT-5)",
       "EVENTO": "Curso IA Avanzado"
     },
     "output": "png"
   }
   ```
4. **HTTP Response**: Recibir PNG/MP4
5. **Storage**: Guardar en Google Drive/Dropbox
6. **Platform Upload**: Subir a YouTube/Instagram/LinkedIn
7. **CRM Log**: Guardar asset URL en campaign

---

## 📊 Integración con Campañas

### Mapeo SVG → UTM Content

**Convención**: `[product]-[template]-[variant]-[hook]-[cta]`

**Ejemplos:**
- `curso-ia-webinar-benefits-focused-fecha_cta_reserva`
- `saas-marketing-linkedin-metrics-cta_empieza-gratis`
- `instagram-antes-despues-metrica_65pct-cta_ver_caso`

**En Make/Zapier:**
```
1. Router: Determinar producto desde campaign/product field
2. Template Selection: Seleccionar SVG según variante
3. UTM Builder: Construir utm_content = [product]-[template]-[variant]
4. Asset Naming: Nombre archivo = IGS_[product]_[template]_[variant]_vA_[date].png
5. Log: Guardar mapeo en CSV/campaign log
```

---

## 📋 Recetas Make/Zapier

### Receta 1: Webinar Event → Preroll Automático

```
1. Trigger: Calendly Invitee Created o Google Calendar event
   - Campos: title, date, time, speaker

2. Router: Seleccionar template según keywords en title
   - "curso" → benefits-focused
   - "ponente" o "speaker" → speaker-focused
   - "último" o "cupos" → urgent-v2

3. HTTP/Code: Procesar SVG con variables
   Variables:
   {
     "FECHA": "{{event.date}}",
     "HORA": "{{event.time}}",
     "EVENTO": "{{event.title}}",
     "PONENTE": "{{event.speaker}}"
   }

4. Convert: SVG → PNG (1920×1080)
   - Usar ImageMagick o servicio externo

5. YouTube API: Upload como thumbnail
   - Video ID: {{youtube_video_id}}
   - Thumbnail: PNG generado

6. CRM: Update Campaign Asset
   - Template usado, URL thumbnail, fecha creación
```

---

### Receta 2: Testimonial → Instagram Post Automático

```
1. Trigger: Testimonial form submit o Deal won con testimonial
   - Campos: customer_name, before, after, product

2. Template: instagram_antes_despues_template.svg

3. Variables:
   {
     "PROBLEMA": "Antes: {{before_metric}}",
     "RESULTADO": "Después: {{after_metric}}",
     "MÉTRICA": "{{improvement}}% mejora",
     "PRODUCTO": "{{product}}"
   }

4. Process SVG: Reemplazar variables

5. Export: SVG → PNG (1080×1350)

6. Instagram Basic Display API: Upload Post
   - Image: PNG generado
   - Caption: "{{customer_name}} logró {{improvement}}% mejora con {{product}}. 👇 Ver caso completo"

7. UTM Tracking:
   utm_campaign = "instagram_case_study_{{date}}"
   utm_content = "antes-despues-{{product}}-{{customer}}"

8. CRM: Log post URL en Contact/Deal
   - Interaction logged
   - Campaign asset created
```

---

### Receta 3: Campaign Launch → LinkedIn Ads Batch

```
1. Trigger: CSV upload o Campaign created en Meta
   - Filas: product, audience, hook_variant, cta_variant, utm_campaign

2. For each row:
   
   a) Template Selection (router):
      - product + hook_variant → seleccionar SVG correcto
   
   b) Variables:
      {
        "MÉTRICA": "{{industry_metric}}",
        "BENEFICIO": "{{value_prop}}",
        "CTA": "{{cta_text}}",
        "HOOK": "{{hook_variant_text}}"
      }
   
   c) Process SVG → PNG (1200×627)
   
   d) Meta Ads API: Create Ad Creative
      - Name: "[product]_[variant]_[hook]_[cta]_vA"
      - Image: PNG generado
      - Link: {{landing_url}}?utm_content={{utm_content}}
   
   e) Log: Guardar creative ID, URL, utm_content

3. Batch Complete: Summary report (Slack/Email)
   - Total creatives creados
   - URLs de assets
   - Campaign IDs
```

---

### Receta 4: Carousel Campaign → 5 Slides Automáticos

```
1. Trigger: Campaign brief creado (CSV, Google Sheet, o Webhook)
   - Campos: product, hook_variant, cta_variant, metrics, testimonials

2. Loop: Generar 5 slides en secuencia
   
   Slide 1 (Hook):
   - Template: carousel_slide_1_hook_1080x1080.svg
   - Variables: HOOK, MÉTRICA, PRODUCTO
   - Output: slide_1_hook.png
   
   Slide 2 (Curso IA):
   - Template: carousel_slide_2_curso_1080x1080.svg
   - Variables: BENEFICIO_1, BENEFICIO_2, CTA
   - Output: slide_2_curso.png
   
   Slide 3 (SaaS Marketing):
   - Template: carousel_slide_3_saas_1080x1080.svg
   - Variables: MÉTRICA, TESTIMONIO, CTA
   - Output: slide_3_saas.png
   
   Slide 4 (IA Bulk):
   - Template: carousel_slide_4_bulk_1080x1080.svg
   - Variables: BENEFICIO, CASO_USO, CTA
   - Output: slide_4_bulk.png
   
   Slide 5 (CTA Final):
   - Template: carousel_slide_5_cta_1080x1080.svg
   - Variables: CTA, URL, OFERTA
   - Output: slide_5_cta.png

3. Batch Processing: Convertir todos los SVG → PNG (1080×1080)

4. Carousel Assembly:
   - LinkedIn API: Create carousel ad
     * Upload 5 images en orden
     * Set landing page URL con UTM
     * Configure headline y description
   
   - Facebook API: Create carousel ad (alternativa)
   
5. UTM Tracking por slide:
   - slide_1: utm_content=carousel-hook-{{hook_variant}}
   - slide_2: utm_content=carousel-curso-beneficios
   - slide_3: utm_content=carousel-saas-metrica
   - slide_4: utm_content=carousel-bulk-caso-uso
   - slide_5: utm_content=carousel-cta-final

6. A/B Testing Setup:
   - Crear 3 variantes del carousel:
     * Variante A: Hook directo (slide 1)
     * Variante B: Hook con métrica (slide 1)
     * Variante C: Hook con testimonial (slide 1)
   - Activar todas en paralelo
   - Budget split: 33% cada una

7. Performance Monitoring:
   - Trackear swipe-through rate por slide
   - Monitorear CTR por slide
   - Optimizar orden si slide 3 > slide 2 en engagement

8. Logging:
   - CRM: Guardar carousel ad IDs
   - Google Sheets: Log performance por slide
   - Slack Alert: Notificar cuando carousel activo
```

---

### Receta 5: Vertical Stories → Multi-Platform (Instagram + TikTok + LinkedIn)

```
1. Trigger: Campaign launch o Webinar event
   - Campos: product, hook_variant, platform_target, metrics

2. Router: Seleccionar template vertical según producto
   - product = "curso_ia" → ad_curso_ia_1080x1920.svg
   - product = "webinar" → webinar-vertical-1080x1920.svg
   - Si hook_variant = "metrics" → usar *_metrics.svg

3. Variables:
   {
     "EVENTO": "{{event.title}}",
     "FECHA": "{{event.date}}",
     "HORA": "{{event.time}}",
     "MÉTRICA": "{{primary_metric}}",
     "CTA": "{{cta_text}}",
     "URL": "{{landing_url}}"
   }

4. Process SVG → PNG (1080×1920)

5. Multi-Platform Upload (paralelo):
   
   a) Instagram Stories API:
      - Upload image as Story
      - Add link sticker: {{url}}?utm_source=instagram&utm_medium=story
      - Caption automático: "{{event.title}} | Link arriba 👆"
   
   b) TikTok API:
      - Upload as image ad o video thumbnail
      - Link: {{url}}?utm_source=tiktok&utm_medium=ad
   
   c) LinkedIn Stories API:
      - Upload as Story
      - Link en comentarios: {{url}}?utm_source=linkedin&utm_medium=story
   
   d) Facebook Stories API:
      - Upload to page as Story
      - Link: {{url}}?utm_source=facebook&utm_medium=story

6. UTM Tracking:
   - utm_source = instagram|tiktok|linkedin|facebook
   - utm_medium = story|reel|ad
   - utm_campaign = {{campaign_name}}
   - utm_content = vertical-{{product}}-{{hook_variant}}

7. Performance Monitoring:
   - Trackear views, clicks, engagement rate por plataforma
   - Comparar CTR: Instagram vs TikTok vs LinkedIn
   - Optimizar budget hacia mejor performing platform

8. CRM Update:
   - Log Story URLs por plataforma
   - Trackear leads por utm_source
   - Asignar a campaign tracking
```

---

### Receta 6: Multi-Platform Square Format (Instagram + LinkedIn + Facebook)

```
1. Trigger: Webinar event created (Calendly/Google Calendar)
   - Campos: event_title, date, time, platform_preference, audience_demographic

2. Router: Seleccionar template cuadrado
   - platform = "instagram" → webinar-square-1080x1080-dark.svg
   - platform = "linkedin" → webinar-square-1080x1080-light.svg
   - audience = "young" → dark
   - audience = "professional" → light

3. Variables:
   {
     "FECHA": "{{event.date}}",
     "HORA": "{{event.time}}",
     "EVENTO": "{{event.title}}",
     "CTA": "Únete gratis",
     "URL": "{{event.calendly_link}}"
   }

4. Process SVG → PNG (1080×1080)

5. Multi-Platform Upload (paralelo):
   
   a) Instagram API:
      - Upload como Story (temporal 24h)
      - O Feed Post (permanente)
      - Caption: "{{event.title}} | {{event.date}} | Link en bio"
      - Link sticker: {{calendly_link}}?utm_source=instagram&utm_medium=story
   
   b) LinkedIn API:
      - Create post con imagen
      - Caption: "🚀 {{event.title}} | {{event.date}} | Link en comentarios"
      - Add link: {{calendly_link}}?utm_source=linkedin&utm_medium=post
   
   c) Facebook API:
      - Upload a página como post
      - Caption: "{{event.title}} | Regístrate gratis"
      - Link: {{calendly_link}}?utm_source=facebook&utm_medium=post

6. UTM Tracking:
   - utm_source = instagram|linkedin|facebook
   - utm_medium = story|post
   - utm_campaign = webinar_{{event_date}}
   - utm_content = square-{{platform}}

7. Performance Tracking:
   - Instagram: Trackear story views, link clicks
   - LinkedIn: Trackear impressions, clicks, comments
   - Facebook: Trackear reach, engagement, link clicks
   - Comparar engagement rate por plataforma

8. CRM Update:
   - Log post URLs en campaign asset
   - Trackear registrations por utm_source
   - Asignar leads a campaign correcto
```

---

## 🎯 Casos de Uso Avanzados

### Dynamic Creative Optimization (DCO)

**Concepto**: Generar variantes automáticas según audiencia/contexto.

**Workflow:**
```
Audience Segment → Seleccionar template → Personalizar hook/CTA → Test A/B → Optimizar
```

**Ejemplo Make/Zapier:**
1. Router por `utm_term`:
   - `mx_cmo` → Template con métricas B2B
   - `es_founder` → Template con lenguaje startup
   - `co_agency` → Template con casos agencia

2. Dynamic variables:
   - Hook cambia según industria
   - CTA cambia según persona (CMO vs Founder)
   - Métricas específicas por vertical

3. Batch generation: Crear 10-20 variantes automáticas
4. Test en paralelo: Todas las variantes activas
5. Auto-optimize: Pausar <15% CTR, escalar >25% CTR

---

### Seasonal/Campaign Rotation

**Concepto**: Rotar templates según fecha/campaña activa.

**Workflow:**
```
Fecha actual → Check campaign calendar → Seleccionar template seasonal → Personalizar
```

**Lógica:**
- Black Friday (nov): Templates con urgencia/precio
- Año nuevo (ene): Templates con "nuevo año, nuevos objetivos"
- Q4 cierre (dic): Templates con "cierre de año, resultados"
- Default: Templates estándar benefits-focused

---

## 🔗 Integración con Documentos Relacionados

- **Workflows**: Ver `26_ADVANCED_AUTOMATION_WORKFLOWS.md` para automatizaciones base
- **UTMs**: Ver `UTM_GUIDE_OUTREACH.md` para tracking de creativos
- **CRMs**: Ver `TOOLS_CRM_COMPARISON.md` para campos de assets
- **DMs**: Ver `Variantes_RealEstate_Tu.md` para copy que acompañe creativos

---

## 📝 Checklist de Implementación

- [ ] Servicio de procesamiento SVG configurado (local o cloud)
- [ ] Templates SVG con variables `[VAR]` identificadas
- [ ] Make/Zapier workflows creados para cada tipo de creativo
- [ ] Mapeo UTM definido para tracking por asset
- [ ] Integración con plataformas (YouTube/Instagram/LinkedIn APIs)
- [ ] Logging en CRM de assets generados
- [ ] Dashboard de performance por template/variante

---

**Última actualización**: 2025-10-30 (v2.0)

