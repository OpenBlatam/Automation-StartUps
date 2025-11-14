# Plantillas SVG para Video — Covers, Overlays y Assets

> Plantillas SVG listas para usar en anuncios de video 15s. Compatibles con After Effects, Premiere, CapCut.

---

## 📐 Formatos por Plataforma

### Instagram Reels / Facebook Reels (1080×1920)
- Cover thumbnail
- Overlay CTA button
- Overlay badges (Urgencia, Social Proof)

### Facebook Feed (1080×1080 o 1080×1350)
- Versión cuadrada 1:1
- Versión 4:5 vertical

---

## 🎨 Plantillas SVG por Producto

### Curso IA + Webinar

#### Cover Thumbnail (1080×1920)
```svg
<svg xmlns="http://www.w3.org/2000/svg" width="1080" height="1920" viewBox="0 0 1080 1920">
  <defs>
    <linearGradient id="bgCurso" x1="0" y1="0" x2="1" y2="1">
      <stop offset="0%" stop-color="[COLORES MARCA-claro]"/>
      <stop offset="100%" stop-color="[COLORES MARCA-primario]"/>
    </linearGradient>
    <linearGradient id="accentCurso" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0%" stop-color="[COLORES MARCA-acento]"/>
      <stop offset="100%" stop-color="[COLORES MARCA-acento-dark]"/>
    </linearGradient>
    <style>
      .headline { font: 800 96px/1.1 'Poppins', 'Inter', sans-serif; fill: [COLORES MARCA-oscuro]; }
      .subtitle { font: 600 48px/1.2 'Inter', sans-serif; fill: [COLORES MARCA-acento]; }
    </style>
  </defs>
  
  <!-- Fondo -->
  <rect width="1080" height="1920" fill="url(#bgCurso)"/>
  
  <!-- Safe zone (150px top/bottom) -->
  <rect x="0" y="0" width="1080" height="150" fill="none" opacity="0.1"/>
  <rect x="0" y="1770" width="1080" height="150" fill="none" opacity="0.1"/>
  
  <!-- Logo/Icon -->
  <g transform="translate(432, 200)">
    <circle cx="108" cy="108" r="108" fill="url(#accentCurso)" opacity="0.2"/>
    <text x="108" y="140" text-anchor="middle" class="headline">IA</text>
  </g>
  
  <!-- Headline -->
  <text x="540" y="900" text-anchor="middle" class="headline">IA en</text>
  <text x="540" y="1020" text-anchor="middle" class="headline">4 semanas</text>
  
  <!-- Subtitle -->
  <text x="540" y="1150" text-anchor="middle" class="subtitle">Webinar incluido</text>
  
  <!-- Badge Urgencia (opcional) -->
  <g transform="translate(290, 1650)">
    <rect width="500" height="80" rx="40" fill="url(#accentCurso)"/>
    <text x="250" y="52" text-anchor="middle" class="headline" fill="#FFFFFF" font-size="36px">Cupos limitados</text>
  </g>
</svg>
```

#### Overlay CTA Button (360×112)
```svg
<svg xmlns="http://www.w3.org/2000/svg" width="360" height="112" viewBox="0 0 360 112">
  <defs>
    <linearGradient id="ctaCurso" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0%" stop-color="[COLORES MARCA-acento]"/>
      <stop offset="100%" stop-color="[COLORES MARCA-acento-dark]"/>
    </linearGradient>
    <filter id="shadow">
      <feGaussianBlur in="SourceAlpha" stdDeviation="3"/>
      <feOffset dx="0" dy="6" result="offsetblur"/>
      <feComponentTransfer>
        <feFuncA type="linear" slope="0.18"/>
      </feComponentTransfer>
      <feMerge>
        <feMergeNode/>
        <feMergeNode in="SourceGraphic"/>
      </feMerge>
    </filter>
    <style>
      .ctaText { font: 700 64px/1 'Inter', sans-serif; fill: #FFFFFF; }
    </style>
  </defs>
  
  <rect width="360" height="112" rx="16" fill="url(#ctaCurso)" filter="url(#shadow)"/>
  <text x="180" y="72" text-anchor="middle" class="ctaText">Inscríbete hoy</text>
</svg>
```

---

### SaaS IA Marketing

#### Cover Thumbnail (1080×1920)
```svg
<svg xmlns="http://www.w3.org/2000/svg" width="1080" height="1920" viewBox="0 0 1080 1920">
  <defs>
    <linearGradient id="bgSaaS" x1="0" y1="0" x2="1" y2="1">
      <stop offset="0%" stop-color="#FFFFFF"/>
      <stop offset="100%" stop-color="[COLORES MARCA-claro]"/>
    </linearGradient>
    <style>
      .headline { font: 800 112px/1.1 'Poppins', sans-serif; fill: [COLORES MARCA-oscuro]; }
      .number { font: 900 140px/1 'Inter', sans-serif; fill: [COLORES MARCA-acento]; }
      .sub { font: 600 56px/1.2 'Inter', sans-serif; fill: #6B7280; }
    </style>
  </defs>
  
  <rect width="1080" height="1920" fill="url(#bgSaaS)"/>
  
  <!-- UI Mockup -->
  <g transform="translate(140, 300)" opacity="0.1">
    <rect width="800" height="600" rx="24" fill="[COLORES MARCA-oscuro]"/>
    <!-- Grid de resultados simulado -->
    <rect x="80" y="80" width="640" height="440" rx="12" fill="[COLORES MARCA-acento]" opacity="0.3"/>
  </g>
  
  <!-- Headline con número -->
  <text x="540" y="1100" text-anchor="middle" class="number">30</text>
  <text x="540" y="1250" text-anchor="middle" class="headline">piezas</text>
  <text x="540" y="1380" text-anchor="middle" class="sub">en 5 minutos</text>
  
  <!-- CTA Badge -->
  <g transform="translate(340, 1700)">
    <rect width="400" height="100" rx="50" fill="[COLORES MARCA-acento]"/>
    <text x="200" y="65" text-anchor="middle" class="headline" fill="#FFFFFF" font-size="48px">Probar gratis</text>
  </g>
</svg>
```

---

### IA Bulk Docs

#### Cover Thumbnail (1080×1920) — Fondo Oscuro
```svg
<svg xmlns="http://www.w3.org/2000/svg" width="1080" height="1920" viewBox="0 0 1080 1920">
  <defs>
    <linearGradient id="bgBulk" x1="0" y1="0" x2="1" y2="1">
      <stop offset="0%" stop-color="[COLORES MARCA-900]"/>
      <stop offset="100%" stop-color="#0A0F1A"/>
    </linearGradient>
    <style>
      .headline { font: 800 120px/1.1 'Poppins', sans-serif; fill: #FFFFFF; }
      .counter { font: 900 200px/1 'Inter', sans-serif; fill: [COLORES MARCA-acento]; }
      .arrow { font: 800 120px/1 'Inter', sans-serif; fill: [COLORES MARCA-acento]; }
    </style>
  </defs>
  
  <rect width="1080" height="1920" fill="url(#bgBulk)"/>
  
  <!-- Grid de documentos (visual) -->
  <g transform="translate(90, 400)" opacity="0.15">
    <!-- 4x4 grid simulado -->
    <rect x="0" y="0" width="200" height="260" rx="8" fill="[COLORES MARCA-acento]"/>
    <rect x="220" y="0" width="200" height="260" rx="8" fill="[COLORES MARCA-acento]"/>
    <rect x="440" y="0" width="200" height="260" rx="8" fill="[COLORES MARCA-acento]"/>
    <rect x="660" y="0" width="200" height="260" rx="8" fill="[COLORES MARCA-acento]"/>
    <!-- Repetir para segunda fila... -->
  </g>
  
  <!-- Counter grande -->
  <text x="400" y="1200" text-anchor="end" class="counter">1</text>
  <text x="480" y="1200" text-anchor="middle" class="arrow">→</text>
  <text x="680" y="1200" text-anchor="start" class="counter">100</text>
  
  <!-- Subtitle -->
  <text x="540" y="1400" text-anchor="middle" class="headline" font-size="64px">Docs</text>
</svg>
```

---

## 🎬 Overlays para Video (On-Screen Text)

### Template Genérico Overlay Text
```svg
<svg xmlns="http://www.w3.org/2000/svg" width="1080" height="1920" viewBox="0 0 1080 1920">
  <defs>
    <filter id="textShadow">
      <feGaussianBlur in="SourceAlpha" stdDeviation="2"/>
      <feOffset dx="0" dy="2" result="offsetblur"/>
      <feComponentTransfer>
        <feFuncA type="linear" slope="0.3"/>
      </feComponentTransfer>
      <feMerge>
        <feMergeNode/>
        <feMergeNode in="SourceGraphic"/>
      </feMerge>
    </filter>
    <style>
      .headline { 
        font: 800 96px/1.1 'Poppins', 'Inter', sans-serif; 
        fill: #FFFFFF; 
        filter: url(#textShadow);
        stroke: rgba(0,0,0,0.8);
        stroke-width: 1px;
      }
    </style>
  </defs>
  
  <!-- Overlay semitransparente (opcional) -->
  <rect x="0" y="1500" width="1080" height="420" fill="rgba(0,0,0,0.4)"/>
  
  <!-- Texto on-screen -->
  <text x="540" y="1650" text-anchor="middle" class="headline">[TEXTO AQUÍ]</text>
  <text x="540" y="1770" text-anchor="middle" class="headline" font-size="72px">[SUBTEXTO]</text>
</svg>
```

---

## 🏷️ Badges y Tags

### Badge Urgencia
```svg
<svg xmlns="http://www.w3.org/2000/svg" width="400" height="80" viewBox="0 0 400 80">
  <defs>
    <linearGradient id="urgent" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0%" stop-color="#FF6B6B"/>
      <stop offset="100%" stop-color="#FF8787"/>
    </linearGradient>
    <style>
      .badgeText { font: 700 36px/1 'Inter', sans-serif; fill: #FFFFFF; }
    </style>
  </defs>
  
  <rect width="400" height="80" rx="40" fill="url(#urgent)"/>
  <text x="200" y="50" text-anchor="middle" class="badgeText">⚡ Cupos limitados</text>
</svg>
```

### Badge Social Proof
```svg
<svg xmlns="http://www.w3.org/2000/svg" width="500" height="90" viewBox="0 0 500 90">
  <defs>
    <style>
      .proofText { font: 700 40px/1 'Inter', sans-serif; fill: [COLORES MARCA-acento]; }
      .subProof { font: 500 32px/1 'Inter', sans-serif; fill: #6B7280; }
    </style>
  </defs>
  
  <rect width="500" height="90" rx="45" fill="#F3F4F6" stroke="[COLORES MARCA-acento]" stroke-width="3"/>
  <text x="250" y="45" text-anchor="middle" class="proofText">+2,000 alumnos</text>
  <text x="250" y="75" text-anchor="middle" class="subProof">Certificado incluido</text>
</svg>
```

---

## 📊 Indicadores de Progreso

### Barra de Progreso (72%)
```svg
<svg xmlns="http://www.w3.org/2000/svg" width="800" height="40" viewBox="0 0 800 40">
  <defs>
    <linearGradient id="progress" x1="0" y1="0" x2="1" y2="0">
      <stop offset="0%" stop-color="[COLORES MARCA-acento]"/>
      <stop offset="100%" stop-color="[COLORES MARCA-acento-dark]"/>
    </linearGradient>
  </defs>
  
  <!-- Fondo -->
  <rect width="800" height="40" rx="20" fill="#E5E7EB"/>
  
  <!-- Progreso 72% -->
  <rect width="576" height="40" rx="20" fill="url(#progress)"/>
  
  <!-- Texto porcentaje -->
  <text x="400" y="28" text-anchor="middle" fill="#FFFFFF" font-size="24px" font-weight="700">72%</text>
</svg>
```

---

## 🔢 Contadores Animados

### Counter 1→100 (Plantilla)
```svg
<svg xmlns="http://www.w3.org/2000/svg" width="800" height="200" viewBox="0 0 800 200">
  <defs>
    <style>
      .counter { font: 900 180px/1 'Inter', sans-serif; fill: [COLORES MARCA-acento]; }
      .label { font: 600 48px/1 'Inter', sans-serif; fill: #FFFFFF; }
    </style>
  </defs>
  
  <!-- Valor inicial (animar con JS/CSS) -->
  <text x="400" y="140" text-anchor="middle" class="counter">1</text>
  
  <!-- Flecha -->
  <text x="500" y="140" text-anchor="middle" class="counter" font-size="120px">→</text>
  
  <!-- Valor final -->
  <text x="650" y="140" text-anchor="middle" class="counter">100</text>
  
  <!-- Label -->
  <text x="400" y="190" text-anchor="middle" class="label">docs</text>
</svg>
```

---

## 📝 Instrucciones de Uso

### Para After Effects
1. Importar SVG como comp
2. Convertir a formas editables
3. Reemplazar placeholders:
   - `[COLORES MARCA-*]` → Tu hex code
   - `[TEXTO AQUÍ]` → Tu copy
4. Aplicar animaciones (pulse, fade, slide)

### Para Premiere
1. Importar SVG como gráfico
2. Usar Essential Graphics para editar texto
3. Animar posición/opacidad con keyframes

### Para CapCut
1. Importar como overlay
2. Editar texto directamente en app
3. Aplicar animaciones predefinidas

---

## 🎨 Paleta de Colores para SVG

Reemplaza en todos los SVGs:
- `[COLORES MARCA-primario]` → Tu color principal
- `[COLORES MARCA-acento]` → Tu color CTA
- `[COLORES MARCA-oscuro]` → Tu color texto oscuro
- `[COLORES MARCA-claro]` → Tu color fondo claro
- `[COLORES MARCA-900]` → Tu color fondo oscuro
- `[COLORES MARCA-acento-dark]` → Tu acento -20% brillo

---

## ✅ Checklist de Customización

Antes de usar plantillas SVG:
- [ ] Colores reemplazados con hex codes reales
- [ ] Fuentes verificadas (Poppins/Inter instaladas)
- [ ] Textos personalizados
- [ ] Safe zones respetadas (150px top/bottom)
- [ ] Contraste verificado (≥ 4.5:1)
- [ ] Exportado en tamaño correcto (1080×1920)
- [ ] Probar en preview de plataforma

---

**Última actualización**: [FECHA]  
**Versión**: 1.0  
**Compatible con**: After Effects, Premiere Pro, CapCut, Figma



