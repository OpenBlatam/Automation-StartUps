# Best Practices Extraídas — De Tus Assets Existentes

> Patrones y mejores prácticas identificadas de tus SVG existentes para aplicar en videos 15s.

---

## 🎨 Patrones de Diseño Identificados

### 1. Jerarquía Visual Consistente

**En todos tus assets**:
- **Eyebrow** (uppercase, letter-spacing): 13-15px, #93C5FD
- **Headline** (800 weight): 64-68px, #FFFFFF
- **Headline-accent** (gradiente): Mismo tamaño, color acento
- **Sub** (400 weight): 24-26px, #E5E7EB
- **CTA** (700-900 weight): 24-26px, color oscuro sobre acento

**Aplicar en video**:
- Mantener misma jerarquía
- Escalar proporcionalmente (×1.4 para 1080×1920)
- Respetar spacing entre elementos

---

### 2. Uso de Gradientes

**Patrón identificado**:
- **Fondo**: `#0F3554 → #1F2937` (oscuro azul-gris)
- **Acento**: `#3B82F6 → #60A5FA` (azul brillante)
- **Urgencia**: `#FF6B6B → #FF8787` (rojo)

**En video**:
- ✅ Mantener gradientes (After Effects: gradient overlay)
- ✅ Añadir animación sutil (opcional: parallax effect)

---

### 3. Métricas Destacadas

**Patrón en tus `*_metrics.svg`**:
- Box oscuro (`#0F2130`) con borde (`#293545`)
- Label pequeño (uppercase, letter-spacing)
- Número grande (900 weight, color acento)
- Ubicación: Sidebar (horizontal) o apilado (vertical)

**Adaptación video**:
- **Horizontal**: Apilar verticalmente en video
- **Animación**: Contador (0 → valor final) en 1-2s
- **Timing**: Aparecen secuencialmente (delay 300ms cada uno)

---

### 4. Testimonials Box

**Patrón identificado**:
- Fondo semitransparente (`rgba(255,255,255,0.08)`)
- Borde acento (`stroke: #3B82F6`)
- Texto italic (#DBEAFE)
- Autor destacado (#93C5FD)

**En video**:
- Mantener mismo estilo
- Añadir fade-in + slide-right (400ms)
- Timing: 8-12s (antes de CTA)

---

### 5. CTAs Consistentes

**Patrón**:
- Botón sólido con gradiente acento
- Texto oscuro sobre claro
- Sombra (`filter: url(#shadow)`)
- Flecha opcional (indicador acción)

**En video**:
- Mantener diseño
- **Aparecer**: 9-10s (60% del video)
- **Animación**: Pulso 1.05x cada 1.5s
- **Tamaño mínimo**: 360×112px (video) vs 280×68px (estático)

---

## 📊 Estructura de Layout Recomendada

### Template Base (Extraído de tus assets)

```
┌─────────────────────────────┐
│ Safe Zone (150px)           │
│ ┌─────────────────────────┐ │
│ │ Logo (centrado top)     │ │
│ │ Eyebrow (centrado)      │ │
│ │ Headline (centrado)     │ │
│ │ Headline-accent         │ │
│ │                         │ │
│ │ Métricas (apiladas)     │ │
│ │                         │ │
│ │ Testimonial (ancho)     │ │
│ │                         │ │
│ │ CTA (centrado)          │ │
│ │ Badge (opcional)        │ │
│ └─────────────────────────┘ │
│ Safe Zone (150px)           │
└─────────────────────────────┘
```

---

## 🎯 Paleta de Colores Aplicada

### Extraída de tus assets (lista completa):

**Fondos**:
- `#0F3554` (SaaS base)
- `#092A44` (Curso base)
- `#0B2B45` (Urgencia base)
- `#1F2937` (Final gradiente)

**Acentos**:
- `#3B82F6` (Azul primario)
- `#60A5FA` (Azul claro)
- `#2E86DE` (Azul medio)
- `#2563EB` (Azul oscuro)

**Texto**:
- `#FFFFFF` (Headlines)
- `#E5E7EB` (Subtítulos)
- `#DBEAFE` (Testimonials)
- `#94A3B8` (Labels pequeños)

**Especiales**:
- `#FF6B6B` (Urgencia)
- `#93C5FD` (Eyebrow, autor)
- `#FFD93D` (Scarcity indicator)

**✅ Usar en video**: Ver `ANUNCIO_VIDEO_PALETA_EXTRAIDA.json`

---

## 📐 Espaciado y Proporciones

### Extraído de tus assets:

**Márgenes**:
- Horizontal: 56-72px (5-7% del ancho)
- Vertical: 48-72px (en 1080×1080)

**Adaptación video** (1080×1920):
- Horizontal: 72px (mantener)
- Vertical: 80px (top), 80px (bottom safe zone)

**Espaciado entre elementos**:
- Headline → Sub: 28px (estático) → 40px (video)
- Elementos bloques: 48px (estático) → 64px (video)

---

## 🔤 Tipografía Aplicada

### Pesos y tamaños (de tus SVG):

| Elemento | Peso | Tamaño (1080×1080) | Tamaño (1080×1920 video) |
|----------|------|---------------------|---------------------------|
| Eyebrow | 700 | 13-15px | 20px |
| Headline | 800 | 64-68px | 96px |
| Headline-accent | 800 | 64-68px | 96px |
| Sub | 400 | 24-26px | 36px |
| Métrica | 900 | 36px | 120px |
| Métrica-label | 500 | 15px | 40px |
| Testimonial | 400 | 20px | 48px |
| CTA | 700-900 | 24-26px | 64px |

**Fuente**: `Inter, Arial, sans-serif` (en todos)

---

## 🎬 Timing Sugerido (Basado en Elementos)

### De estructura estática a secuencia:

**Original (todo visible)**:
- Logo, headline, métricas, testimonial, CTA

**Video (secuencial)**:
```
00:00-01:00: Logo + Eyebrow (fade-in)
01:00-04:00: Headline slide-up (con accent destacado)
04:00-08:00: Métricas aparecen secuencialmente
08:00-11:00: Testimonial fade-in
11:00-13:00: CTA aparece con pulso
13:00-15:00: Badge + ESLOGAN (cierre)
```

---

## 🏷️ Elementos Especiales Identificados

### 1. Badges de Urgencia

**Tu patrón**:
- Fondo rojo gradiente
- Texto blanco bold
- Tamaño: 44px altura
- Posición: Top-right (en horizontal)

**Adaptación video**:
- Mover a top-center
- Aumentar tamaño (60px altura)
- Timing: Primeros 2s o últimos 2s

---

### 2. Growth Charts/Icons

**Tu patrón** (en `ad_*_metrics.svg`):
- Barras crecientes (azules)
- Línea de tendencia
- Círculo final destacado

**En video**:
- Animación: Barras crecen secuencialmente (0→100%)
- Timing: Durante métricas (4-8s)
- Motion: Ease-out para natural

---

### 3. Scarcity Indicators

**Tu patrón**:
- Texto amarillo (`#FFD93D`)
- Mensaje: "Sin tarjeta", "Demo en 15 min"
- Pequeño, cerca de CTA

**En video**:
- Mantener tamaño legible (44px)
- Aparecer con CTA (11-13s)
- Posición: Bajo botón CTA

---

## ✅ Checklist de Aplicación

### Al crear nuevo video:

**Diseño**:
- [ ] Jerarquía visual respetada (eyebrow → headline → sub)
- [ ] Gradientes aplicados (fondo, acento)
- [ ] Paleta extraída usada
- [ ] Tipografía Inter con pesos correctos

**Layout**:
- [ ] Márgenes consistentes (72px horizontal)
- [ ] Safe zones respetadas (150px top/bottom)
- [ ] Espaciado proporcional entre elementos

**Elementos**:
- [ ] Métricas con mismo estilo (box oscuro + borde)
- [ ] Testimonial con fondo semitransparente
- [ ] CTA con gradiente y sombra
- [ ] Badges (si aplica) con estilo urgencia

**Animación**:
- [ ] Secuencia temporal (no todo junto)
- [ ] Transiciones suaves (200-300ms)
- [ ] CTA con pulso continuo

---

## 🚀 Quick Reference

**Colores principales**:
- Fondo: `#0F3554` → `#1F2937`
- Acento: `#3B82F6` → `#60A5FA`
- Texto: `#FFFFFF` (headline), `#E5E7EB` (sub)

**Fuentes**:
- Principal: Inter
- Pesos: 400 (regular), 700 (bold), 800 (extrabold), 900 (black)

**Espaciado video**:
- Horizontal: 72px (márgenes)
- Vertical: 80px (top), safe 150px, 80px (bottom)

**Timing base**:
- Logo: 0-1s
- Headline: 1-4s
- Métricas: 4-8s
- Testimonial: 8-11s
- CTA: 11-15s

---

**Última actualización**: [FECHA]  
**Versión**: 1.0  
**Fuente**: Análisis de 30+ assets SVG existentes



