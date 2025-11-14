# Adaptación de Formatos — De Assets Estáticos a Video 15s

> Guía completa para convertir tus assets SVG existentes (1080×1080, 1200×627) a videos 15s (1080×1920).

---

## 📐 Mapeo de Formatos Existentes

### Formatos que tienes:
- **1080×1080** (cuadrado) → Feed Instagram/Facebook
- **1200×627** (horizontal) → LinkedIn Feed
- **1080×1920** (vertical) → Reels/Stories
- **1920×1080** (horizontal) → Prerolls webinar

### Formato objetivo video:
- **1080×1920** (vertical 9:16) → Reels/Facebook Reels

---

## 🔄 Estrategias de Adaptación

### Estrategia 1: Reutilizar Layout (1080×1080 → 1080×1920)

**Tu formato actual** (1080×1080):
- Logo top-left (72,72)
- Headline central (540,540)
- CTA bottom (540,900)
- Métricas sidebar derecho

**Adaptación a video** (1080×1920):
- **Aspecto**: Más espacio vertical, mantener ancho
- **Logo**: Mover a top-center (540,80)
- **Headline**: Escalar y reposicionar (540,500)
- **Métricas**: Apilar verticalmente (no sidebar)
- **CTA**: Mantener bottom-center (540,1700)
- **Safe zones**: Respetar 150px top/bottom

**Ventajas**:
- ✅ Mantiene identidad visual
- ✅ Reutiliza copy y elementos
- ✅ Consistencia con feed

**Desventajas**:
- ⚠️ Requiere reajuste de proporciones
- ⚠️ Métricas necesitan apilamiento

---

### Estrategia 2: Extract Key Elements (1200×627 → 1080×1920)

**Tu formato actual** (1200×627):
- Layout horizontal con sidebar métricas
- Headline largo horizontal
- Testimonial box horizontal

**Adaptación a video**:
- **Extraer elementos clave**:
  1. Headline (simplificar a 1-2 líneas)
  2. Métricas (convertir a boxes apilados)
  3. Testimonial (mantener pero vertical)
  4. CTA (centrar)

**Timing sugerido**:
```
00:00-03:00: Headline simplificado
03:00-08:00: Métricas aparecen secuencialmente
08:00-12:00: Testimonial
12:00-15:00: CTA + Logo
```

---

### Estrategia 3: Portar Preroll (1920×1080 → 1080×1920)

**De `webinar-preroll-benefits-focused.svg`**:
- Header con título
- 3 benefits boxes horizontales
- CTA grande

**Adaptación video**:
- **Rotar y reorganizar**:
  1. Header → Top (0-2s)
  2. Benefits → Secuencial vertical (2-10s)
  3. CTA → Bottom (10-15s)

**Template específico**: Ver `ANUNCIO_VIDEO_TEMPLATES_WEBINAR_PREROLL.md`

---

## 🎨 Template: 1080×1080 → 1080×1920 Video

### Ejemplo: SaaS IA Marketing (de tu `ad_saas_ia_marketing_1080x1080.svg`)

**Elementos originales**:
- Eyebrow: "Automatización · Datos propios"
- Headline: "Mejora tu ROI en +20% con SaaS de IA"
- Métricas: +27% Leads, -32% CPA (sidebar)
- Testimonial: Compacto horizontal
- CTA: "Solicita demo"

**Versión video adaptada**:

```svg
<svg xmlns="http://www.w3.org/2000/svg" width="1080" height="1920" viewBox="0 0 1080 1920">
  <defs>
    <!-- Mismos gradientes y estilos de tu 1080x1080 -->
    <linearGradient id="bg" x1="0" y1="0" x2="1" y2="1">
      <stop offset="0%" stop-color="#0F3554"/>
      <stop offset="100%" stop-color="#1F2937"/>
    </linearGradient>
    <linearGradient id="accent" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0%" stop-color="#3B82F6"/>
      <stop offset="100%" stop-color="#60A5FA"/>
    </linearGradient>
    <style>
      .eyebrow { font: 700 20px/1.2 'Inter', sans-serif; fill: #93C5FD; text-transform: uppercase; }
      .headline { font: 800 96px/1.1 'Inter', sans-serif; fill: #FFFFFF; }
      .headline-accent { font: 800 96px/1.1 'Inter', sans-serif; fill: url(#accent); }
      .metric { font: 900 120px/1 'Inter', sans-serif; fill: url(#accent); }
      .metric-label { font: 600 40px/1 'Inter', sans-serif; fill: #94A3B8; }
      .testimonial { font: 400 48px/1.5 'Inter', sans-serif; fill: #DBEAFE; font-style: italic; }
      .cta { font: 900 64px/1 'Inter', sans-serif; fill: #0F3554; }
    </style>
  </defs>
  
  <rect width="1080" height="1920" fill="url(#bg)"/>
  
  <!-- Logo top-center (adaptado de top-left) -->
  <g transform="translate(432, 80)">
    <rect width="216" height="216" rx="28" fill="#111827" stroke="#374151"/>
    <!-- Icono simplificado -->
  </g>
  
  <!-- Eyebrow -->
  <text x="540" y="350" text-anchor="middle" class="eyebrow">Automatización · Datos propios</text>
  
  <!-- Headline (centralizado, escalado) -->
  <text x="540" y="480" text-anchor="middle" class="headline">Mejora tu ROI en</text>
  <text x="540" y="600" text-anchor="middle" class="headline-accent">+20%</text>
  <text x="540" y="720" text-anchor="middle" class="headline" font-size="72px">con SaaS de IA</text>
  
  <!-- Métricas apiladas verticalmente (no sidebar) -->
  <g transform="translate(340, 850)">
    <rect x="0" y="0" width="400" height="220" rx="24" fill="#0F2130" stroke="#293545" stroke-width="2"/>
    <text x="200" y="70" text-anchor="middle" class="metric-label">Leads</text>
    <text x="200" y="150" text-anchor="middle" class="metric">+27%</text>
  </g>
  
  <g transform="translate(340, 1100)">
    <rect x="0" y="0" width="400" height="220" rx="24" fill="#0F2130" stroke="#293545" stroke-width="2"/>
    <text x="200" y="70" text-anchor="middle" class="metric-label">CPA</text>
    <text x="200" y="150" text-anchor="middle" class="metric">-32%</text>
  </g>
  
  <!-- Testimonial (vertical, más ancho) -->
  <g transform="translate(90, 1380)">
    <rect x="0" y="0" width="900" height="200" rx="20" fill="#0F2130" stroke="#3B82F6" stroke-width="2"/>
    <text x="450" y="60" text-anchor="middle" class="testimonial">"CPA -32% y +27% leads.</text>
    <text x="450" y="120" text-anchor="middle" class="testimonial">Automatización que funciona."</text>
    <text x="450" y="170" text-anchor="middle" font-size="36px" fill="#93C5FD" font-weight="600">— María G., Head of Growth</text>
  </g>
  
  <!-- CTA (bottom-center) -->
  <g transform="translate(290, 1650)">
    <rect x="0" y="0" width="500" height="140" rx="20" fill="url(#accent)"/>
    <text x="250" y="88" text-anchor="middle" class="cta">Solicita demo</text>
  </g>
  
  <!-- Badge (opcional) -->
  <g transform="translate(340, 1820)">
    <rect x="0" y="0" width="400" height="60" rx="30" fill="#0F2130" stroke="#293545"/>
    <text x="200" y="38" text-anchor="middle" font-size="32px" fill="#93C5FD" font-weight="600">✨ Demo en 15 min</text>
  </g>
</svg>
```

---

## 📊 Matriz de Conversión de Elementos

| Elemento Original | Formato Original | Adaptación Video | Nuevo Posicionamiento |
|------------------|------------------|------------------|----------------------|
| **Logo** | Top-left (72,72) | Top-center (540,80) | Centrado horizontalmente |
| **Headline** | Central (540,540) | Escalado (540,500) | Mantener centro, mover arriba |
| **Métricas** | Sidebar derecho | Apiladas verticalmente | Centro, una debajo de otra |
| **Testimonial** | Horizontal compacto | Vertical ancho | Más espacio para texto |
| **CTA** | Bottom-left (72,540) | Bottom-center (540,1700) | Centrado, más grande |
| **Badge** | Cerca de CTA | Bottom-absolute | Últimos 2s del video |

---

## 🎬 Timing por Elemento (Adaptado)

### De formato estático a secuencia temporal:

**Original (estático)**: Todo visible simultáneamente

**Video (temporal)**: Aparece secuencialmente

```
00:00-01:00: Logo fade-in (top)
01:00-03:00: Headline slide-up (central)
03:00-06:00: Métricas aparecen una por una (secuencial)
06:00-09:00: Testimonial fade-in
09:00-12:00: CTA aparece con pulso
12:00-15:00: Badge + ESLOGAN (cierre)
```

---

## 🔧 Script de Conversión Automática

### Python: Adaptar Coordenadas

```python
#!/usr/bin/env python3
"""
Convierte coordenadas de formato 1080x1080 a 1080x1920 para video.
"""

def adaptar_coordenada(x_orig, y_orig, formato_orig="1080x1080", formato_dest="1080x1920"):
    """
    Adapta coordenadas manteniendo proporción horizontal.
    """
    # Ancho igual (1080), alto aumenta (1080 → 1920)
    ratio_vertical = 1920 / 1080  # 1.777...
    
    # X se mantiene igual (mismo ancho)
    x_dest = x_orig
    
    # Y se ajusta proporcionalmente + offset para centrar verticalmente
    # Offset: 420px (centrar contenido vertical en más espacio)
    y_dest = y_orig * ratio_vertical + 420
    
    return int(x_dest), int(y_dest)

def adaptar_tamaño(width_orig, height_orig):
    """
    Adapta tamaños (mantiene ancho, escala alto proporcionalmente).
    """
    ratio = 1920 / 1080
    width_dest = width_orig
    height_dest = int(height_orig * ratio)
    return width_dest, height_dest

# Ejemplo: Logo original en (72, 72)
x_new, y_new = adaptar_coordenada(72, 72)
print(f"Logo original (72, 72) → Video ({x_new}, {y_new})")
# Output: Logo original (72, 72) → Video (72, 548)

# Ejemplo: CTA original en (72, 540)
x_cta, y_cta = adaptar_coordenada(72, 540)
print(f"CTA original (72, 540) → Video ({x_cta}, {y_cta})")
# Output: CTA original (72, 540) → Video (72, 1380)
```

---

## ✅ Checklist de Adaptación

### Pre-adaptación
- [ ] Identificar formato origen (1080×1080, 1200×627, etc.)
- [ ] Listar elementos clave a portar
- [ ] Decidir estrategia (reutilizar, extraer, portar)

### Durante adaptación
- [ ] Coordenadas ajustadas (X centrado, Y escalado)
- [ ] Tamaños escalados proporcionalmente
- [ ] Safe zones respetadas (150px top/bottom)
- [ ] Elementos secuencializados (timing)

### Post-adaptación
- [ ] Preview en formato 1080×1920
- [ ] Texto legible (≥96px headlines)
- [ ] Contraste verificado (≥ 4.5:1)
- [ ] Timing total: 15s exactos

---

## 📝 Ejemplos de Conversión por Producto

### Curso IA (1080×1080 → Video)

**Elementos a portar**:
1. Logo + eyebrow → 0-2s
2. "Mejora tu ROI en +20%" → 2-5s
3. Métricas (stats boxes) → 5-9s
4. Testimonial → 9-12s
5. "Ver temario" CTA → 12-15s

### SaaS Marketing (1080×1080 → Video)

**Elementos a portar**:
1. Eyebrow → 0-1s
2. "Mejora tu ROI en +20% con SaaS de IA" → 1-4s
3. Métricas apiladas → 4-8s
4. Testimonial compacto → 8-11s
5. "Solicita demo" + badge → 11-15s

### IA Bulk (1200×627 → Video)

**Elementos a portar**:
1. Hook "¿100 docs? 1 consulta." → 0-2s
2. Plantillas + variables → 2-6s
3. Export icons → 6-10s
4. CTA "Compra ahora" → 10-15s

---

## 🚀 Quick Conversion Workflow

1. **Abrir SVG original** (ej. `ad_saas_ia_marketing_1080x1080.svg`)
2. **Copiar elementos clave** (headline, métricas, CTA)
3. **Usar template** de `ANUNCIO_VIDEO_PLANTILLAS_SVG_VIDEO.md`
4. **Aplicar coordenadas adaptadas** (usar script Python)
5. **Añadir timing** (convertir estático → temporal)
6. **Exportar** como base para video

---

**Última actualización**: [FECHA]  
**Versión**: 1.0  
**Formato origen**: 1080×1080, 1200×627, 1920×1080  
**Formato destino**: 1080×1920 (video 15s)



