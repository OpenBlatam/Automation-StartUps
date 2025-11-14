# Templates de Preroll Webinar — Adaptación a Video 15s

> Plantillas basadas en tus prerolls de webinar existentes, adaptadas para anuncios de video 15s.

---

## 🎬 Adaptación de Elementos de Preroll

### Elementos Clave de Preroll → Video 15s

**De tu `webinar-preroll-social-proof.svg`**:
- ✅ Stats boxes (2,500+, 4.9★, 87%)
- ✅ Testimonial box
- ✅ CTA "Únete gratis"
- ✅ Badges fecha/hora

**Adaptación para video**:
- Simplificar a 3-4 elementos máximo
- Animación secuencial (no todo junto)
- Timing: Stats (0-5s) → Testimonial (5-9s) → CTA (9-15s)

---

## 📐 Template: Preroll Social Proof → Video 15s

### Timecode Adaptado

```
00:00-02:00: Stats aparecen secuencialmente
  - "+2,500 inscritos"
  - "+4.9★ calificación"
  - "+87% aplican lo aprendido"

02:00-07:00: Testimonial aparece
  - "Aumenté mis ventas 3x..."
  - Autor: "María G., E-commerce Manager"

07:00-10:00: Badge fecha/hora (si aplica)
  - [FECHA] | [HORA] GMT-5

10:00-15:00: CTA aparece
  - "Únete gratis" (botón)
  - Logo + [ESLOGAN]
```

---

## 🎨 Template SVG: Video Version (1080×1920)

```svg
<svg xmlns="http://www.w3.org/2000/svg" width="1080" height="1920" viewBox="0 0 1080 1920">
  <defs>
    <linearGradient id="bg" x1="0" y1="0" x2="1" y2="1">
      <stop offset="0%" stop-color="#0B1229"/>
      <stop offset="100%" stop-color="#10314A"/>
    </linearGradient>
    <linearGradient id="accent" x1="0" y1="0" x2="1" y2="0">
      <stop offset="0%" stop-color="#00E5A8"/>
      <stop offset="100%" stop-color="#00B4D8"/>
    </linearGradient>
    <filter id="sh" x="-50%" y="-50%" width="200%" height="200%">
      <feGaussianBlur in="SourceAlpha" stdDeviation="4"/>
      <feOffset dx="0" dy="4" result="offsetblur"/>
      <feComponentTransfer>
        <feFuncA type="linear" slope="0.3"/>
      </feComponentTransfer>
      <feMerge>
        <feMergeNode/>
        <feMergeNode in="SourceGraphic"/>
      </feMerge>
    </filter>
    <style>
      .headline { font: 800 72px/1.1 'Inter', system-ui, sans-serif; fill: #FFFFFF; }
      .metric { font: 900 96px/1 'Inter', sans-serif; fill: #00E5A8; }
      .metric-label { font: 600 32px/1 'Inter', sans-serif; fill: #C7FFFA; }
      .testimonial { font: 400 48px/1.5 'Inter', sans-serif; fill: #DBEAFE; font-style: italic; }
      .author { font: 600 36px/1.3 'Inter', sans-serif; fill: #93C5FD; }
      .cta { font: 900 64px/1 'Inter', sans-serif; fill: #062A2D; }
    </style>
  </defs>
  
  <rect width="1080" height="1920" fill="url(#bg)"/>
  
  <!-- Safe zones marcadas -->
  <rect x="0" y="0" width="1080" height="150" fill="none" opacity="0.05"/>
  <rect x="0" y="1770" width="1080" height="150" fill="none" opacity="0.05"/>
  
  <!-- Stats boxes (aparecen secuencial 0-5s) -->
  <g transform="translate(90, 300)" opacity="0.9">
    <!-- Box 1: Inscritos -->
    <rect x="0" y="0" width="280" height="220" rx="24" fill="#0E3740" stroke="#00C1BE" stroke-width="3" filter="url(#sh)"/>
    <text x="140" y="90" text-anchor="middle" class="metric">2,500+</text>
    <text x="140" y="140" text-anchor="middle" class="metric-label">Inscritos</text>
    <text x="140" y="175" text-anchor="middle" class="metric-label" font-size="24px" fill="#9FB6FF">último webinar</text>
  </g>
  
  <g transform="translate(400, 300)" opacity="0.9">
    <!-- Box 2: Calificación -->
    <rect x="0" y="0" width="280" height="220" rx="24" fill="#0E3740" stroke="#00C1BE" stroke-width="3" filter="url(#sh)"/>
    <text x="140" y="90" text-anchor="middle" class="metric">4.9★</text>
    <text x="140" y="140" text-anchor="middle" class="metric-label">Calificación</text>
    <text x="140" y="175" text-anchor="middle" class="metric-label" font-size="24px" fill="#9FB6FF">de 850 reviews</text>
  </g>
  
  <g transform="translate(710, 300)" opacity="0.9">
    <!-- Box 3: Aplican -->
    <rect x="0" y="0" width="280" height="220" rx="24" fill="#0E3740" stroke="#00C1BE" stroke-width="3" filter="url(#sh)"/>
    <text x="140" y="90" text-anchor="middle" class="metric">87%</text>
    <text x="140" y="140" text-anchor="middle" class="metric-label">Aplican</text>
    <text x="140" y="175" text-anchor="middle" class="metric-label" font-size="24px" fill="#9FB6FF">lo aprendido</text>
  </g>
  
  <!-- Testimonial box (aparece 5-9s) -->
  <g transform="translate(90, 600)">
    <rect x="0" y="0" width="900" height="280" rx="24" fill="rgba(255,255,255,0.08)" stroke="rgba(255,255,255,0.15)" stroke-width="2"/>
    <text x="450" y="90" text-anchor="middle" class="testimonial">"Aumenté mis ventas 3x en 2 semanas</text>
    <text x="450" y="150" text-anchor="middle" class="testimonial">con las estrategias del webinar"</text>
    <text x="450" y="220" text-anchor="middle" class="author">— María G., E-commerce Manager</text>
  </g>
  
  <!-- Badge fecha/hora (opcional, 7-10s) -->
  <g transform="translate(90, 920)">
    <rect x="0" y="0" width="420" height="100" rx="16" fill="#0E3740" stroke="#00C1BE" stroke-width="2"/>
    <text x="210" y="60" text-anchor="middle" class="metric-label" font-size="40px">[FECHA]</text>
    <rect x="440" y="0" width="460" height="100" rx="16" fill="#0E3740" stroke="#00C1BE" stroke-width="2"/>
    <text x="670" y="60" text-anchor="middle" class="metric-label" font-size="40px">[HORA] (GMT-5)</text>
  </g>
  
  <!-- CTA Button (aparece 10-15s) -->
  <g transform="translate(270, 1550)" filter="url(#sh)">
    <rect x="0" y="0" width="540" height="140" rx="20" fill="url(#accent)"/>
    <rect x="0" y="0" width="540" height="140" rx="20" fill="none" stroke="rgba(255,255,255,0.65)" stroke-width="3"/>
    <text x="270" y="88" text-anchor="middle" class="cta">Únete gratis</text>
    <path d="M470,70 L500,88 L470,106" fill="#062A2D" opacity="0.8"/>
  </g>
  
  <!-- Logo + ESLOGAN (últimos 2s) -->
  <g transform="translate(390, 1750)">
    <text x="150" y="40" text-anchor="middle" fill="#E9FFFB" font-family="Inter" font-size="32px" font-weight="800">[ESLOGAN]</text>
  </g>
</svg>
```

---

## 📊 Template: Métricas Destacadas (de ad_curso_ia_metrics)

### Adaptación Video 15s

**Elementos del SVG original**:
- Métricas: +27% Leads, -32% CPA
- Testimonial con cifras
- Gráfico de crecimiento

**Timing para video**:
```
00:00-01:00: Headline aparece
  "Mejora tu ROI en +20%"

01:00-04:00: Métricas aparecen secuencialmente
  "+27% Leads"
  "-32% CPA"

04:00-08:00: Testimonial
  "Resultados medibles: +27% leads..."

08:00-12:00: Gráfico animado (opcional)
  Barras creciendo

12:00-15:00: CTA
  "Ver temario" / "Inscríbete hoy"
```

---

## 🎨 Template SVG: Métricas Video (1080×1920)

```svg
<svg xmlns="http://www.w3.org/2000/svg" width="1080" height="1920" viewBox="0 0 1080 1920">
  <defs>
    <linearGradient id="bg" x1="0" y1="0" x2="1" y2="1">
      <stop offset="0%" stop-color="#092A44"/>
      <stop offset="100%" stop-color="#1F2D3D"/>
    </linearGradient>
    <linearGradient id="accent" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0%" stop-color="#2E86DE"/>
      <stop offset="100%" stop-color="#54A0FF"/>
    </linearGradient>
    <style>
      .headline { font: 800 88px/1.1 'Inter', sans-serif; fill: #FFFFFF; }
      .metric { font: 900 120px/1 'Inter', sans-serif; fill: url(#accent); }
      .metric-label { font: 600 40px/1 'Inter', sans-serif; fill: #94A3B8; text-transform: uppercase; }
      .testimonial { font: 400 52px/1.5 'Inter', sans-serif; fill: #DBEAFE; font-style: italic; }
      .cta { font: 900 64px/1 'Inter', sans-serif; fill: #0A2740; }
    </style>
  </defs>
  
  <rect width="1080" height="1920" fill="url(#bg)"/>
  
  <!-- Headline -->
  <text x="540" y="400" text-anchor="middle" class="headline">Mejora tu ROI en</text>
  <text x="540" y="520" text-anchor="middle" class="headline" fill="url(#accent)">+20%</text>
  
  <!-- Métricas boxes (secuencial) -->
  <g transform="translate(140, 700)">
    <rect x="0" y="0" width="380" height="240" rx="24" fill="#0F2130" stroke="#2B3A4A" stroke-width="2"/>
    <text x="190" y="80" text-anchor="middle" class="metric-label">Leads</text>
    <text x="190" y="160" text-anchor="middle" class="metric">+27%</text>
    <text x="190" y="210" text-anchor="middle" class="metric-label" font-size="32px">incremento</text>
  </g>
  
  <g transform="translate(560, 700)">
    <rect x="0" y="0" width="380" height="240" rx="24" fill="#0F2130" stroke="#2B3A4A" stroke-width="2"/>
    <text x="190" y="80" text-anchor="middle" class="metric-label">CPA</text>
    <text x="190" y="160" text-anchor="middle" class="metric">-32%</text>
    <text x="190" y="210" text-anchor="middle" class="metric-label" font-size="32px">reducción</text>
  </g>
  
  <!-- Testimonial -->
  <g transform="translate(90, 1050)">
    <rect x="0" y="0" width="900" height="300" rx="24" fill="#0F2130" stroke="#2E86DE" stroke-width="2" opacity="0.8"/>
    <text x="450" y="100" text-anchor="middle" class="testimonial">"Resultados medibles:</text>
    <text x="450" y="170" text-anchor="middle" class="testimonial">+27% leads y -32% CPA</text>
    <text x="450" y="240" text-anchor="middle" class="testimonial">en 6 semanas."</text>
  </g>
  
  <!-- CTA -->
  <g transform="translate(340, 1500)">
    <rect x="0" y="0" width="400" height="120" rx="20" fill="url(#accent)"/>
    <text x="200" y="75" text-anchor="middle" class="cta">Ver temario</text>
  </g>
</svg>
```

---

## ⚡ Template: Urgencia (de ad_saas_ia_marketing_urgency)

### Adaptación Video 15s

**Elementos clave**:
- Badge urgencia top (rojo)
- Headline con ROI
- Double CTA (primario + secundario)
- Scarcity indicator

**Timing**:
```
00:00-01:00: Badge urgencia aparece
  "⚡ Prueba gratis 30 días"

01:00-04:00: Headline + ROI
  "Mejora tu ROI en +20%"

04:00-08:00: Beneficios/features
  "Sin tarjeta · 15 min setup"

08:00-12:00: Double CTA
  "Empieza gratis" (primario)
  "Ver demo" (secundario)

12:00-15:00: Logo + [ESLOGAN]
```

---

## 🎨 Template SVG: Urgencia Video (1080×1920)

```svg
<svg xmlns="http://www.w3.org/2000/svg" width="1080" height="1920" viewBox="0 0 1080 1920">
  <defs>
    <linearGradient id="bg" x1="0" y1="0" x2="1" y2="1">
      <stop offset="0%" stop-color="#0B2B45"/>
      <stop offset="100%" stop-color="#17202B"/>
    </linearGradient>
    <linearGradient id="accent" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0%" stop-color="#3B82F6"/>
      <stop offset="100%" stop-color="#60A5FA"/>
    </linearGradient>
    <linearGradient id="urgent" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0%" stop-color="#FF6B6B"/>
      <stop offset="100%" stop-color="#FF8787"/>
    </linearGradient>
    <style>
      .headline { font: 800 88px/1.1 'Inter', sans-serif; fill: #FFFFFF; }
      .headline-accent { font: 800 88px/1.1 'Inter', sans-serif; fill: url(#accent); }
      .urgentText { font: 700 40px/1.2 'Inter', sans-serif; fill: #FFFFFF; }
      .cta-primary { font: 900 64px/1 'Inter', sans-serif; fill: #0B2B45; }
      .cta-secondary { font: 700 56px/1 'Inter', sans-serif; fill: #60A5FA; }
      .scarcity { font: 600 44px/1 'Inter', sans-serif; fill: #FFD93D; }
    </style>
  </defs>
  
  <rect width="1080" height="1920" fill="url(#bg)"/>
  
  <!-- Badge Urgencia Top -->
  <g transform="translate(90, 150)">
    <rect width="900" height="100" rx="50" fill="url(#urgent)"/>
    <text x="450" y="64" text-anchor="middle" class="urgentText">⚡ Prueba gratis 30 días</text>
  </g>
  
  <!-- Headline -->
  <text x="540" y="500" text-anchor="middle" class="headline">Mejora tu ROI en</text>
  <text x="540" y="620" text-anchor="middle" class="headline-accent">+20%</text>
  
  <!-- Scarcity -->
  <text x="540" y="750" text-anchor="middle" class="scarcity">🎁 Sin tarjeta · Configuración en 15 min</text>
  
  <!-- Double CTA -->
  <g transform="translate(140, 1000)">
    <rect x="0" y="0" width="800" height="140" rx="18" fill="url(#accent)"/>
    <text x="400" y="88" text-anchor="middle" class="cta-primary">Empieza gratis</text>
  </g>
  
  <g transform="translate(140, 1180)">
    <rect x="0" y="0" width="800" height="140" rx="18" fill="none" stroke="#60A5FA" stroke-width="4"/>
    <text x="400" y="88" text-anchor="middle" class="cta-secondary">Ver demo</text>
  </g>
  
  <!-- Logo + ESLOGAN -->
  <text x="540" y="1650" text-anchor="middle" fill="#E9FFFB" font-family="Inter" font-size="48px" font-weight="800">[ESLOGAN]</text>
</svg>
```

---

## 📝 Instrucciones de Uso

### Para After Effects
1. Importar SVG como comp
2. Separar capas por tiempo (stats, testimonial, CTA)
3. Animar aparición secuencial (opacity 0→1, 200ms)
4. Aplicar motion blur en transiciones

### Animaciones Sugeridas
- **Stats boxes**: Slide-up + fade (secuencial, delay 300ms)
- **Testimonial**: Fade-in + slide-right (400ms)
- **CTA**: Scale 0.9→1.0 + fade (300ms) + pulso continuo

---

## ✅ Checklist de Adaptación

- [ ] Colores sincronizados con paleta extraída
- [ ] Safe zones respetadas (150px top/bottom)
- [ ] Texto legible (≥96px headlines, ≥64px CTA)
- [ ] Contraste verificado (≥ 4.5:1)
- [ ] Timing ajustado (15s total)
- [ ] Animaciones definidas

---

**Última actualización**: [FECHA]  
**Versión**: 1.0  
**Basado en**: webinar-preroll-*.svg, ad_*_*.svg



