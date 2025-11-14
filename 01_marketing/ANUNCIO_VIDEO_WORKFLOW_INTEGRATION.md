# Integración Videos 15s → Workflow de Creativos Existente

> Conexión de los nuevos videos 15s con tu workflow automatizado de SVG y creativos.

---

## 🔗 Mapeo de Videos a Workflow Actual

### Tu Workflow Existente (de `CREATIVES_WORKFLOWS_INTEGRATION.md`)

**Flujo SVG estático**:
```
Evento/Campaign → Seleccionar template SVG → Personalizar variables → Export PNG → Upload plataforma → Tracking
```

**Flujo Video 15s** (nuevo):
```
Evento/Campaign → Seleccionar guión video → Personalizar VO/variables → Animar SVG base → Export MP4 → Upload → Tracking
```

---

## 🔄 Integración en Workflows Make/Zapier

### Workflow 1: Video desde Template SVG (Automático)

**Aprovecha tu `ad_*_1080x1920.svg` existente**:

```
1. Trigger: Campaign created o Webinar event
   - Campos: product, hook_variant, platform_target

2. Router: Seleccionar SVG base
   - product = "curso_ia" → ad_curso_ia_1080x1920.svg
   - product = "saas_marketing" → ad_saas_ia_marketing_1080x1920.svg
   - product = "ia_bulk" → ad_ia_bulk_1080x1920.svg
   - Si hook_variant = "metrics" → usar *_metrics.svg

3. SVG → Video Processing:
   a) Leer SVG base
   b) Aplicar variables (reemplazar placeholders)
   c) Importar a After Effects (vía API o script)
   d) Aplicar animaciones (usar expresiones de ANUNCIO_VIDEO_EXPRESIONES_AFTER_EFFECTS.md)
   e) Añadir VO (TTS o audio grabado)
   f) Exportar MP4 (1080×1920, 15s, H.264)

4. Multi-Platform Upload:
   - Instagram Reels API
   - Facebook Reels API
   - LinkedIn (si soporta video)
   - TikTok API

5. UTM Tracking:
   - utm_source = [plataforma]
   - utm_medium = video
   - utm_content = [product]-[variant]-video-15s

6. CRM Log:
   - Guardar video URL
   - Trackear performance
```

---

### Workflow 2: Video Batch desde Campaign CSV

**Similar a tu Receta 3 (LinkedIn Ads Batch)** pero para video:

```
1. Trigger: CSV upload con campaign details
   - Columnas: product, hook_variant, cta_variant, audience, utm_campaign

2. For each row:
   a) Seleccionar SVG base (1080×1920)
   b) Seleccionar guión VO (de ANUNCIO_VIDEO_*_15s.md)
   c) Personalizar:
      - Variables en SVG
      - Texto en guión VO
      - Timing según storyboard
   
   d) Generar video:
      - SVG → After Effects (automatizado)
      - Animaciones aplicadas (expresiones)
      - VO generado (TTS) o grabado
      - Export MP4
   
   e) Upload a plataforma
   
   f) UTM tracking
   
   g) Log en CRM

3. Batch Complete: Summary report
   - Videos generados
   - URLs
   - Performance tracking links
```

---

### Workflow 3: Carousel → Video Secuencial

**Aprovecha tus 5 slides de carousel**:

```
1. Trigger: Campaign brief (carousel definido)

2. Loop: Para cada slide (1-5):
   a) Template: carousel_slide_*_1080x1080.svg
   b) Convertir a frame de video (3s cada uno)
   c) Aplicar transición entre frames

3. Assembly:
   - Frame 1: 0-3s (hook)
   - Frame 2: 3-6s (curso)
   - Frame 3: 6-9s (saas)
   - Frame 4: 9-12s (bulk)
   - Frame 5: 12-15s (CTA)

4. Añadir:
   - VO narrativo (guión unificado)
   - Música de fondo
   - Transiciones entre frames

5. Export: Video 15s completo

6. Upload: Instagram Reels, TikTok, YouTube Shorts

7. Tracking: UTM por frame (opcional)
```

---

## 🤖 Script de Automatización: SVG → Video

### Python Script (Integra con tu workflow)

```python
#!/usr/bin/env python3
"""
Convierte SVG 1080×1920 a video 15s automáticamente.
Integra con workflow Make/Zapier.
"""

import json
import sys
from pathlib import Path
import subprocess

def svg_to_video_workflow(svg_path, variables, output_path, vo_script=None):
    """
    Workflow completo: SVG → Video 15s.
    
    Args:
        svg_path: Path al SVG base (1080×1920)
        variables: Dict de variables a reemplazar
        output_path: Path de salida MP4
        vo_script: Path al guión VO (opcional)
    """
    
    # 1. Personalizar SVG
    personalized_svg = personalize_svg(svg_path, variables)
    
    # 2. Preparar assets para After Effects
    # (requiere proyecto AE template)
    ae_project_data = {
        "svg_path": str(personalized_svg),
        "timing": get_timing_from_storyboard(svg_path),
        "vo_script": vo_script,
        "output": str(output_path)
    }
    
    # 3. Renderizar (requiere After Effects con scripting)
    # O usar servicio externo (RunwayML, etc.)
    render_video(ae_project_data)
    
    return output_path

def personalize_svg(svg_path, variables):
    """Reemplaza variables en SVG."""
    with open(svg_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    for var, value in variables.items():
        content = content.replace(f'[{var}]', str(value))
    
    output_svg = svg_path.parent / f"{svg_path.stem}_personalized.svg"
    with open(output_svg, 'w', encoding='utf-8') as f:
        f.write(content)
    
    return output_svg

def get_timing_from_storyboard(svg_path):
    """Extrae timing del storyboard correspondiente."""
    # Mapear SVG a storyboard
    storyboards = {
        "ad_curso_ia_1080x1920": "ANUNCIO_VIDEO_SVG_TO_VIDEO_STORYBOARD.md",
        "ad_saas_ia_marketing_1080x1920": "ANUNCIO_VIDEO_SVG_TO_VIDEO_STORYBOARD.md",
        "ad_ia_bulk_1080x1920": "ANUNCIO_VIDEO_SVG_TO_VIDEO_STORYBOARD.md"
    }
    
    svg_name = Path(svg_path).stem
    for key, storyboard in storyboards.items():
        if key in svg_name:
            # Leer timing del storyboard
            return load_storyboard_timing(storyboard)
    
    return get_default_timing()

def render_video(ae_project_data):
    """Renderiza video usando After Effects (via scripting)."""
    # Opción 1: After Effects scripting
    # Opción 2: Servicio externo (RunwayML API, etc.)
    # Opción 3: FFmpeg con animaciones básicas
    
    # Para implementación completa, ver:
    # - After Effects scripting guide
    # - RunwayML API integration
    # - FFmpeg animation pipeline
    pass

if __name__ == "__main__":
    # Ejemplo uso
    svg = sys.argv[1]
    vars_json = sys.argv[2]
    output = sys.argv[3]
    
    variables = json.loads(vars_json)
    result = svg_to_video_workflow(svg, variables, output)
    print(f"Video generado: {result}")
```

---

## 📊 Matriz de Integración: SVG ↔ Video

| Asset SVG Actual | Workflow SVG | Workflow Video | Integración |
|-----------------|--------------|----------------|-------------|
| `ad_*_1080x1920.svg` | Export PNG → Upload | **Animar SVG → Export MP4 → Upload** | ✅ Usar SVG como base, añadir animaciones |
| `webinar-preroll-*.svg` | Export PNG/MP4 | **Adaptar a 1080×1920 → Animaciones** | ✅ Portar preroll a formato video |
| `carousel_slide_*.svg` | Batch 5 PNGs | **Secuencia video 15s** | ✅ Unificar slides en video narrativo |
| `ad_*_1200x627.svg` | Export PNG → LinkedIn | **Adaptar a 1080×1920 → Video** | ⚠️ Requiere conversión formato |

---

## 🔄 Workflow Unificado (SVG + Video)

### Opción 1: Pipeline Paralelo

**Generar ambos formatos simultáneamente**:

```
1. Trigger: Campaign/Event created

2. Seleccionar template base

3. Personalizar variables

4. Branch paralelo:
   A) SVG Path:
      - Export PNG estático
      - Upload a plataformas (Feed)
   
   B) Video Path:
      - Animar SVG
      - Añadir VO
      - Export MP4
      - Upload a plataformas (Reels/Stories)

5. Tracking unificado:
   - Mismo utm_campaign
   - utm_content diferente (estatico vs video)
   - Comparar performance: PNG vs MP4
```

---

### Opción 2: Video como Variante A/B

**Añadir video como variante adicional**:

```
1. Campaign creada

2. Generar creativos estáticos (tu workflow actual)

3. Añadir variante video:
   - Usar mismo SVG base (1080×1920)
   - Aplicar animaciones
   - Añadir VO

4. Upload ambas variantes en paralelo

5. A/B test automático:
   - Estático vs Video
   - Trackear: CTR, engagement, cost per result
   - Auto-pausar peor performing
```

---

## 🎯 Receta Make/Zapier: Video Automático

### Receta Completa (Lista para usar)

```
1. Trigger: Google Calendar Event Created
   - Event type: Webinar
   - Campos: title, date, time, speaker

2. Router: Seleccionar template
   - Si product = "curso_ia" → ad_curso_ia_1080x1920.svg
   - Si hook = "metrics" → *_metrics.svg

3. Variables Setup:
   {
     "EVENTO": "{{event.title}}",
     "FECHA": "{{event.date}}",
     "MÉTRICA": "+27% leads",
     "CTA": "Únete gratis"
   }

4. HTTP: POST a servicio de procesamiento
   POST https://tu-servicio.com/svg-to-video
   Body: {
     "svg_template": "ad_curso_ia_1080x1920.svg",
     "variables": {...},
     "vo_script": "guion_vo_curso_ia_directo.txt",
     "output_format": "mp4"
   }

5. Servicio procesa:
   - Personaliza SVG
   - Aplica animaciones (expresiones AE)
   - Genera VO (TTS o audio)
   - Renderiza MP4

6. Receive: MP4 file

7. Instagram Reels API: Upload video
   - Video: MP4 recibido
   - Caption: "{{event.title}} | {{event.date}}"
   - Link: {{calendly_link}}?utm_source=instagram&utm_medium=reel

8. Facebook Reels API: Upload video

9. CRM: Log video asset
   - URL video
   - Platform
   - UTM tracking
   - Campaign ID
```

---

## 📝 Variables Unificadas (SVG + Video)

**De tu workflow SVG actual**:
```json
{
  "FECHA": "{{event.date}}",
  "HORA": "{{event.time}}",
  "EVENTO": "{{event.title}}",
  "CTA": "Únete gratis",
  "URL": "{{event.calendly_link}}"
}
```

**Para video, añadir**:
```json
{
  "VO_SCRIPT": "guion_vo_curso_ia_directo",
  "MUSIC_TRACK": "background_positive_110bpm",
  "ANIMATION_SPEED": "normal",
  "PLATFORM": "instagram"
}
```

---

## 🚀 Quick Integration Checklist

- [ ] Servicio de procesamiento SVG→Video configurado
- [ ] Templates SVG 1080×1920 identificados
- [ ] Storyboards mapeados (SVG → timing)
- [ ] Expresiones AE aplicables automatizadas
- [ ] VO scripts disponibles (TTS o grabados)
- [ ] Make/Zapier workflow extendido
- [ ] Tracking UTM configurado para videos
- [ ] CRM campos para video assets

---

## 📊 Dashboard de Performance Unificado

**Trackear SVG estático + Video juntos**:

| Métrica | SVG Estático | Video 15s | Comparación |
|---------|--------------|-----------|-------------|
| **CTR** | X% | Y% | Video vs Estático |
| **Engagement** | X% | Y% | Engagement rate |
| **Cost per Result** | $X | $Y | ROI comparativo |
| **Platform** | LinkedIn Feed | Instagram Reels | Por plataforma |

**Decisión automática**:
- Si Video CTR > SVG +20% → Priorizar video
- Si SVG más eficiente → Mantener estático
- Si ambos funcionan → Combinar en campaña

---

**Última actualización**: [FECHA]  
**Versión**: 1.0  
**Integración con**: `CREATIVES_WORKFLOWS_INTEGRATION.md`



