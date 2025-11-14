# 🎯 Guía Unificada: Tracking de Templates con UTMs

Sistema completo para trackear todos tus templates creativos (Instagram, LinkedIn Ads, Webinars) con UTMs.

---

## 📐 Templates disponibles y dimensiones

| Template | Dimensiones | Formato | Uso | Archivo |
|----------|------------|---------|-----|---------|
| Instagram Antes/Después | 1080×1350 | 4:5 | Post/Story | `instagram_antes_despues_template.svg` |
| LinkedIn Ad (Landscape) | 1200×627 | 1.91:1 | Sponsored Content | `ads/linkedin/ad_*_1200x627_*.svg` |
| LinkedIn Ad (Cuadrado) | 1080×1080 | 1:1 | Feed/Carousel | `ads/linkedin/ad_*_1080x1080.svg` |
| Webinar Preroll | Variable | 16:9 | Video intro | `webinar-preroll-*.svg` |

### Comparación de formatos LinkedIn

| Aspecto | 1200×627 (Landscape) | 1080×1080 (Cuadrado) |
|---------|---------------------|---------------------|
| **Mejor para** | Desktop, Sponsored Content | Móvil, Carruseles, Feed |
| **CTR esperado** | 0.5-1.5% | 0.6-1.8% (móvil) |
| **Uso principal** | Sponsored Content single image | Carousel Ads, Feed nativo |
| **Safe area texto** | Margen 60 px lateral, 44 px vertical | Margen 80 px todos lados |
| **CTA recomendado** | 2 palabras máx | 2 palabras máx |
| **Templates disponibles** | 12 (urgency, social_proof, metrics) | 2 (curso_ia, saas_ia) |

**Recomendación**:
- **Landscape (1200×627)**: Usa como formato principal para Sponsored Content
- **Cuadrado (1080×1080)**: Crea para carruseles o cuando quieras destacar en feed móvil
- **A/B testing**: Testa ambos formatos con mismo `utm_content` para comparar performance

---

## 🔗 Convención de UTMs por plataforma

### Instagram
```
utm_source=instagram
utm_medium=feed | stories | reels
utm_campaign=[producto]_resultados_ig_[yyyy-mm]
utm_content=[template]_v[version]
utm_term=[region]_[persona]
```

**Ejemplo**:
```
https://tusitio.com/landing?
  utm_source=instagram&
  utm_medium=feed&
  utm_campaign=cursoia_resultados_ig_2025-11&
  utm_content=antes_despues_v1&
  utm_term=mx_buyer
```

### LinkedIn Ads
```
utm_source=linkedin
utm_medium=cpc
utm_campaign=[producto]_demo_linkedin_[yyyy-mm]
utm_content=[template]_[angulo]_[cta]_v[version]
utm_term=[rol]_[region]
```

**Ejemplo**:
```
https://tusitio.com/demo?
  utm_source=linkedin&
  utm_medium=cpc&
  utm_campaign=cursoia_demo_linkedin_2025-11&
  utm_content=urgency_h1direct_cta_reserva_v1&
  utm_term=cmo_mx
```

### Webinar Preroll
```
utm_source=email | linkedin | meta
utm_medium=video | email | cpc
utm_campaign=[producto]_webinar_[tema]_[yyyy-mm]
utm_content=preroll_[style]_v[version]
utm_term=[audiencia]
```

**Ejemplo**:
```
https://tusitio.com/webinar?
  utm_source=email&
  utm_medium=email&
  utm_campaign=cursoia_webinar_ia_2025-11&
  utm_content=preroll_speaker_v1&
  utm_term=alumnos_activos
```

---

## 📋 CSV maestro de templates (calendario completo)

**Columnas sugeridas**:
```
fecha | plataforma | template | producto | angulo | dimensiones | utm_campaign | utm_content | utm_term | filename | url_feed | url_stories | status | owner
```

**Ejemplo de fila**:
```
2025-11-30 | instagram | antes_despues | cursoia | resultados | 1080x1350 | cursoia_resultados_ig_2025-11 | antes_despues_v1 | mx_buyer | antes_despues_v1_ig_2025-11-30.png | [url] | [url] | draft | adan
2025-12-01 | linkedin | urgency | saasia | urgencia | 1200x627 | saasia_demo_linkedin_2025-11 | urgency_h1direct_cta_reserva_v1 | cmo_mx | saasia_urgency_linkedin_2025-12-01.png | [url] | - | planned | adan
```

---

## 🛠️ Script maestro para generar URLs

Usa `IG_TEMPLATE_UTM_HELPER.js` como base y extiende con funciones para LinkedIn y Webinar:

```javascript
// Funciones adicionales para LinkedIn
function generateLinkedInAdURL(options = {}) {
  const utms = {
    utm_source: 'linkedin',
    utm_medium: 'cpc',
    utm_campaign: `${options.product}_demo_linkedin_${options.month}`,
    utm_content: `${options.template}_${options.angle}_${options.cta}_v${options.version}`,
    utm_term: `${options.role}_${options.region}`
  };
  
  const params = new URLSearchParams(utms);
  return `${options.urlBase}?${params.toString()}`;
}

// Función para Webinar
function generateWebinarURL(options = {}) {
  const utms = {
    utm_source: options.source || 'email',
    utm_medium: options.medium || 'email',
    utm_campaign: `${options.product}_webinar_${options.topic}_${options.month}`,
    utm_content: `preroll_${options.style}_v${options.version}`,
    utm_term: options.audience || 'general'
  };
  
  const params = new URLSearchParams(utms);
  return `${options.urlBase}?${params.toString()}`;
}
```

---

## 📊 Dashboard unificado (qué medir)

### Por plataforma
- **Instagram**: Sessions, CTR link, Leads, Stories vs Feed performance
- **LinkedIn**: Impressions, Clicks, CTR, Leads, CPC, CPL
- **Webinar**: Views, Completions, Registrations, Attendees

### Por template/ángulo
- **Instagram**: `antes_despues` vs `testimonio` vs `proceso`
- **LinkedIn**: `urgency` vs `social_proof` vs `beneficio`
- **Webinar**: `speaker_focused` vs `split_screen` vs `center_card`

### Métricas esperadas (benchmarks orientativos)

**Instagram Feed (orgánico)**:
- CTR link: 1.5-3.5% (según segmentación)
- CVR (click → lead): 10-25%
- Stories: CTR 2-5% (típicamente mayor que feed)

**LinkedIn Ads (Sponsored Content)**:
- CTR: 0.5-1.5% (B2B)
- CVR: 5-15%
- CPC: $2-8 (según audiencia)
- CPL: $15-50

**Webinar Preroll (video)**:
- VTR 8s: 35-50% (mínimo para considerar efectivo)
- Completion rate: 15-30%
- Registration rate: 20-40% (desde vista → registro)

### Dashboard mínimo (Sheets/Looker)
```
plataforma | template | utm_content | impressions | clicks | ctr | leads | deals | revenue | cpa | roas
```

### Fórmulas útiles (Sheets)
- CTR: `=IFERROR(Clicks/Impressions,0)`
- CVR: `=IFERROR(Leads/Clicks,0)`
- CPC: `=Cost/Clicks`
- CPL: `=Cost/Leads`
- ROAS: `=IFERROR(Revenue/Cost,0)`

---

## 🏷️ Naming estándar de archivos (convención)

### Formato general
```
[template]_[angulo]_v[version]_[plataforma]_[dimensiones?]_[yyyy-mm-dd].[ext]
```

**Dimensiones** (opcional, recomendado para LinkedIn):
- LinkedIn landscape: `_1200x627`
- LinkedIn cuadrado: `_1080x1080`
- Instagram: omitir (siempre 1080×1350)
- Webinar: omitir (variable)

### Ejemplos por plataforma

**Instagram**:
- `antes_despues_v1_ig_2025-11-30.png`
- `testimonio_v2_ig_2025-12-01.png`
- `proceso_v1_ig_2025-12-02.png`

**LinkedIn**:
- `urgency_h1direct_v1_linkedin_1200x627_2025-11-30.png` (landscape)
- `social_proof_beneficio_v2_linkedin_1080x1080_2025-12-01.png` (cuadrado)
- `beneficio_h1urgencia_v1_linkedin_1200x627_2025-12-02.png` (landscape)

**Webinar**:
- `preroll_speaker_v1_2025-11-30.png`
- `preroll_split_screen_v2_2025-12-01.png`
- `preroll_urgent_v2_2025-12-02.png`

### Reglas
- Todo en minúsculas
- Sin espacios (usar `_`)
- Versión siempre `v{n}` (sin ceros a la izquierda)
- Fecha en formato `YYYY-MM-DD`
- Extensión: `.png` (preferido) o `.jpg`

---

## 🔄 Workflow unificado

### 1. Preparar template
- Editar SVG (texto, imágenes, CTA)
- Generar URL con UTMs usando helper script
- Actualizar URL en SVG
- Exportar PNG/JPG según dimensiones

### 2. Subir a plataforma
- **Instagram**: Post + Stories (URLs diferentes para medium)
- **LinkedIn**: Campaign Manager (Asset Library)
- **Webinar**: Plataforma de hosting (Vimeo/YouTube)

### 3. Tracking automático
- `utm_capture.js` captura UTMs en landing
- Formulario → CRM con `utm_content` específico
- GA4 registra sessions por `utm_campaign`

### 4. Reporte
- Dashboard por `utm_campaign` y `utm_content`
- Comparar performance entre templates/ángulos
- Optimizar: escalar ganadores, pausar perdedores

---

## ✅ Checklist antes de publicar cualquier template

### Validación técnica
- [ ] URL actualizada en template con UTMs completos
- [ ] Nombre de archivo coincide con `utm_content`
- [ ] Dimensiones correctas para plataforma (ver tabla arriba)
- [ ] Texto legible y CTA claro
- [ ] Contraste de colores AA (verificar accesibilidad)
- [ ] Logo visible y con clearspace adecuado
- [ ] URLs generadas para Feed y Stories (si aplica)
- [ ] Test manual: click en URL y verificar que funciona

### Validación de contenido
- [ ] Texto sin errores ortográficos
- [ ] Métricas/claim verificables (no exagerar resultados)
- [ ] CTA claro y accionable (2 palabras máximo)
- [ ] Imágenes de calidad (si aplica)
- [ ] Brand guidelines respetadas

### Validación de tracking
- [ ] UTMs validados con regex (ver `UTM_GUIDE_OUTREACH.md`)
- [ ] URL testada en navegador (200 OK)
- [ ] `utm_capture.js` funcionando en staging
- [ ] Anotado en calendario CSV maestro
- [ ] Captura guardada para referencia

---

## 🔍 Validación automática de templates (scripts)

### Script: Validar SVG antes de exportar

```javascript
// validate_template.js
function validateTemplate(svgContent, platform, expectedDimensions) {
  const errors = [];
  const warnings = [];

  // Validar dimensiones
  const dimensions = svgContent.match(/width=['"](\d+)['"].*height=['"](\d+)['"]/i);
  if (dimensions) {
    const [width, height] = [parseInt(dimensions[1]), parseInt(dimensions[2])];
    if (width !== expectedDimensions.width || height !== expectedDimensions.height) {
      errors.push(`Dimensiones incorrectas: ${width}x${height}, esperado: ${expectedDimensions.width}x${expectedDimensions.height}`);
    }
  }

  // Validar URL con UTMs
  const urlMatch = svgContent.match(/href=['"]([^'"]+)['"]/i);
  if (urlMatch) {
    const url = urlMatch[1];
    if (!url.includes('utm_source=')) warnings.push('URL sin utm_source');
    if (!url.includes('utm_campaign=')) warnings.push('URL sin utm_campaign');
    if (!url.includes('utm_content=')) warnings.push('URL sin utm_content');
  } else {
    errors.push('No se encontró URL en el template');
  }

  // Validar texto legible (contraste)
  // Esto requiere análisis de colores más complejo, pero puedes validar que existe texto

  return { errors, warnings, valid: errors.length === 0 };
}
```

### Uso con batch_update_svg_urls.js

1. **Crear archivo config.json**:
```json
{
  "defaults": {
    "urlBase": "https://tusitio.com/landing",
    "month": "2025-11"
  },
  "templates": [
    {
      "platform": "instagram",
      "filePath": "./instagram_antes_despues_template.svg",
      "template": "antes_despues",
      "version": 1,
      "product": "cursoia",
      "region": "mx",
      "persona": "buyer"
    }
  ]
}
```

2. **Ejecutar**:
```bash
node batch_update_svg_urls.js config.json
```

---

## 🛠️ Scripts y herramientas

- **Helper URL Generator**: [`IG_TEMPLATE_UTM_HELPER.js`](./IG_TEMPLATE_UTM_HELPER.js) - Genera URLs con UTMs
- **Batch Update Script**: [`batch_update_svg_urls.js`](./batch_update_svg_urls.js) - Actualiza múltiples SVGs automáticamente
- **Config Example**: [`TEMPLATE_BATCH_CONFIG.example.json`](./TEMPLATE_BATCH_CONFIG.example.json) - Plantilla de configuración

### Uso rápido del batch update

1. **Copiar config example**:
```bash
cp TEMPLATE_BATCH_CONFIG.example.json config.json
```

2. **Editar config.json** con tus templates

3. **Ejecutar**:
```bash
node batch_update_svg_urls.js config.json
```

---

## 📚 Referencias rápidas

### Guías por plataforma
- **Instagram**: [`QUICK_START_IG_TEMPLATE.md`](./QUICK_START_IG_TEMPLATE.md)
- **LinkedIn Ads**: [`QUICK_START_LINKEDIN_TEMPLATES.md`](./QUICK_START_LINKEDIN_TEMPLATES.md) ⭐ **NUEVO**

### Scripts y herramientas
- **Helper Script**: [`IG_TEMPLATE_UTM_HELPER.js`](./IG_TEMPLATE_UTM_HELPER.js) — Genera URLs con UTMs
- **Batch Update**: [`batch_update_svg_urls.js`](./batch_update_svg_urls.js) — Actualiza múltiples SVGs
- **Config Example**: [`TEMPLATE_BATCH_CONFIG.example.json`](./TEMPLATE_BATCH_CONFIG.example.json)

### Tracking y UTMs
- **Guía UTMs**: [`UTM_GUIDE_OUTREACH.md`](./UTM_GUIDE_OUTREACH.md)
- **CRM Integration**: [`TOOLS_CRM_COMPARISON.md`](./TOOLS_CRM_COMPARISON.md)

### Calendarios
- **Calendario Maestro**: [`TEMPLATES_MASTER_CALENDAR.csv`](./TEMPLATES_MASTER_CALENDAR.csv)
- **Calendario IG**: [`INSTAGRAM_CALENDAR_UTM.csv`](./INSTAGRAM_CALENDAR_UTM.csv)

---

## 🎨 Templates disponibles (inventario completo)

### Instagram (1080×1350)
- ✅ `instagram_antes_despues_template.svg` — Template completo con paneles antes/después

### LinkedIn Ads

**Formato 1200×627 (landscape — Sponsored Content)**:
- ✅ `ad_curso_ia_1200x627_urgency.svg` — Urgencia con badge rojo
- ✅ `ad_curso_ia_1200x627_social_proof.svg` — Prueba social (+alumnos)
- ✅ `ad_curso_ia_1200x627_metrics.svg` — Métricas destacadas
- ✅ `ad_curso_ia_1200x627_v2.svg` — Versión alternativa

- ✅ `ad_saas_ia_marketing_1200x627_social_proof.svg` — Prueba social (+marcas)
- ✅ `ad_saas_ia_marketing_1200x627_urgency.svg` — Urgencia
- ✅ `ad_saas_ia_marketing_1200x627_metrics.svg` — Métricas ROI/tiempo
- ✅ `ad_saas_ia_marketing_1200x627_v2.svg` — Versión 2

- ✅ `ad_ia_bulk_1200x627_urgency.svg` — Urgencia
- ✅ `ad_ia_bulk_1200x627_social_proof.svg` — Prueba social
- ✅ `ad_ia_bulk_1200x627_metrics.svg` — Métricas (3 docs/consulta)
- ✅ `ad_ia_bulk_1200x627_v2.svg` — Versión 2

**Formato 1080×1080 (cuadrado — Feed/Carousel)**:
- ✅ `ad_curso_ia_1080x1080.svg` — Formato cuadrado Curso IA
- ✅ `ad_saas_ia_marketing_1080x1080.svg` — Formato cuadrado SaaS IA

**Nota**: LinkedIn acepta múltiples formatos. Usa 1200×627 para Sponsored Content y 1080×1080 para carruseles o feed nativo.

### Webinar Preroll (variable, típico 16:9)

**Estilos disponibles**:
- ✅ `webinar-preroll-speaker-focused.svg` — Speaker enfocado
- ✅ `webinar-preroll-center-card.svg` — Card central
- ✅ `webinar-preroll-split-screen.svg` — Pantalla dividida
- ✅ `webinar-preroll-urgent-v2.svg` — Urgencia v2
- ✅ `webinar-preroll-elegant.svg` — Estilo elegante
- ✅ `webinar-preroll-benefits-focused.svg` — Enfoque en beneficios
- ✅ `webinar-preroll-social-proof.svg` — Prueba social
- ✅ `webinar-preroll-video-thumbnail.svg` — Thumbnail de video

### Convención de ángulos por template

**LinkedIn Ads**:
- `urgency` → Badge de urgencia, CTA rojo, "Termina hoy"
- `social_proof` → Logos/clientes, "+X usuarios", testimonios
- `metrics` → Números destacados (ROI, tiempo ahorrado, velocidad)
- `v2` → Variante alternativa del diseño base

**Webinar Preroll**:
- `speaker-focused` → Speaker/presentador prominente
- `split-screen` → Pantalla dividida con información
- `center-card` → Card central con info clave
- `urgent` → Urgencia con contador/badge
- `elegant` → Diseño premium/minimalista
- `benefits-focused` → Lista de beneficios destacados
- `social-proof` → Testimonios/logos de participantes

**Nota**: Añade nuevos templates a esta lista cuando los crees. Usa el naming estándar definido arriba.

---

---

## 🎯 Guía de selección de template (qué usar cuándo)

### LinkedIn Ads

**Usa `urgency` cuando**:
- Hay oferta/descuento con fecha límite
- Oferta limitada (plazas, unidades)
- Lanzamiento con precio especial
- Cierre de mes/trimestre
- **CTA recomendado**: "Reservar ahora", "Activar hoy", "Termina hoy"

**Usa `social_proof` cuando**:
- Tienes clientes/logos reconocibles
- Números impresionantes de usuarios/clientes
- Testimonios con nombres/cargos
- Validación de industria (B2B/SaaS)
- **CTA recomendado**: "Probar gratis", "Ver demo", "Únete a +X marcas"

**Usa `metrics` cuando**:
- Puedes mostrar ROI concreto
- Tiempo/ahorro medible
- Velocidad/eficiencia como diferencial
- Comparación antes/después numérica
- **CTA recomendado**: "Calcular ahorro", "Ver resultados", "Descubrir cómo"

**Usa `v2` cuando**:
- Quieres testear variante del diseño base
- A/B testing de elementos visuales
- Refresh de creativo existente

### Instagram

**Usa `antes_despues` cuando**:
- Tienes transformación visual clara
- Resultados medibles (números antes/después)
- Testimonial con evidencia visual
- Caso de uso concreto

**Usa `testimonio` cuando**:
- Tienes testimonios con foto/nombre
- Cliente reconocible en tu industria
- Resultados verificables
- Prueba social fuerte

### Webinar Preroll

**Usa `speaker-focused` cuando**:
- Speaker reconocido o con autoridad
- Formato entrevista/presentación personal
- Quieres establecer confianza humana

**Usa `split-screen` cuando**:
- Quieres mostrar info + speaker simultáneamente
- Formato educativo con slides

**Usa `benefits-focused` cuando**:
- Lista clara de beneficios del webinar
- Formato más informativo que personal

**Usa `urgent` cuando**:
- Fecha límite de registro
- Capacidad limitada
- Webinar exclusivo

---

## 🚀 Próximos pasos

1. **Esta semana**: Implementa tracking en 1 template (Instagram o LinkedIn)
2. **Próxima semana**: Extiende a todos los templates activos
3. **Mes 1**: Dashboard unificado con todos los datos
4. **Mes 2**: Optimización basada en datos (A/B testing por `utm_content`)

---

**¡Sistema completo listo para trackear todos tus creativos! 🎉**

