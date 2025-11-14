# Carousel Slides → Video 15s — Adaptación

> Guía para convertir tus carousel slides (1080×1080) en un video 15s narrativo.

---

## 📊 Estructura de Carousel Actual

Según tus archivos:
- `carousel_slide_1_hook_1080x1080.svg` → Hook
- `carousel_slide_2_curso_1080x1080.svg` → Curso
- `carousel_slide_3_saas_1080x1080.svg` → SaaS
- `carousel_slide_4_bulk_1080x1080.svg` → Bulk
- `carousel_slide_5_cta_1080x1080.svg` → CTA

---

## 🎬 Estrategia de Conversión

### Opción 1: Unificar (Todo en Uno)

**Ideal para**: Video promocional de todos los productos

**Timing sugerido**:
```
00:00-02:00: Slide 1 (Hook general)
02:00-05:00: Slide 2 (Curso - rápido)
05:00-08:00: Slide 3 (SaaS - rápido)
08:00-11:00: Slide 4 (Bulk - rápido)
11:00-15:00: Slide 5 (CTA unificado)
```

**Desventaja**: Muy rápido por producto, poco detalle

---

### Opción 2: Por Producto Individual (Recomendado)

**Ideal para**: Video específico por producto

**Ejemplo: Curso IA** (de `carousel_slide_2_curso_1080x1080.svg`):

```
00:00-02:00: Hook del slide 1 (adaptado)
02:00-06:00: Elementos del slide 2 (curso) expandidos
06:00-09:00: Beneficios adicionales (no en carousel)
09:00-12:00: Prueba social
12:00-15:00: CTA del slide 5
```

---

## 🎨 Template: Carousel Slide → Video Frame

### Estructura Base

**De carousel (estático)**:
- Slide individual con 1-2 elementos principales
- Layout optimizado para swipe

**A video (temporal)**:
- Elementos aparecen secuencialmente
- Más espacio para cada elemento
- Transiciones entre "slides" como cortes

---

## 📐 Ejemplo: Slide 2 (Curso) → Video 15s

### Elementos del carousel:
1. Hook/Headline principal
2. Icono/visual
3. Beneficio clave
4. CTA pequeño

### Adaptación video:

```svg
<svg xmlns="http://www.w3.org/2000/svg" width="1080" height="1920" viewBox="0 0 1080 1920">
  <!-- Frame 1: Hook (0-2s) -->
  <g opacity="1">
    <text x="540" y="400" text-anchor="middle" font-size="96px" fill="#FFFFFF" font-weight="800">
      [Hook del slide 1]
    </text>
  </g>
  
  <!-- Frame 2: Contenido curso (2-8s) -->
  <g opacity="1">
    <!-- Icono/visual -->
    <g transform="translate(432, 600)">
      <!-- Icono del slide 2 -->
    </g>
    
    <!-- Headline -->
    <text x="540" y="900" text-anchor="middle" font-size="88px" fill="#FFFFFF" font-weight="800">
      [Headline del slide 2]
    </text>
    
    <!-- Beneficios expandidos -->
    <g transform="translate(90, 1100)">
      <rect width="900" height="200" rx="20" fill="rgba(255,255,255,0.08)"/>
      <text x="450" y="100" text-anchor="middle" font-size="48px" fill="#E5E7EB">
        [Beneficios del slide expandidos]
      </text>
    </g>
  </g>
  
  <!-- Frame 3: CTA (8-15s) -->
  <g opacity="1">
    <g transform="translate(290, 1650)">
      <rect width="500" height="140" rx="20" fill="url(#accent)"/>
      <text x="250" y="88" text-anchor="middle" font-size="64px" fill="#0F3554" font-weight="900">
        [CTA del slide 5]
      </text>
    </g>
  </g>
</svg>
```

---

## 🎬 Timing por Tipo de Slide

### Slide 1 (Hook)
**En carousel**: Aparece primero
**En video**: 0-2s
**Animación**: Fade-in rápido (200ms)

---

### Slide 2-4 (Productos)
**En carousel**: Swipe horizontal
**En video**: 2-10s (expandido)
**Animación**: 
- Icono: Scale 0.8→1.0 (400ms)
- Headline: Slide-up (300ms)
- Beneficios: Fade-in secuencial

---

### Slide 5 (CTA)
**En carousel**: Último slide
**En video**: 10-15s
**Animación**: 
- Aparece: Scale 0.9→1.0 (300ms)
- Continúa: Pulso 1.05x cada 1.5s

---

## 🔄 Transiciones entre Slides

### En Carousel: Swipe horizontal

### En Video: Cut o Dissolve

**Recomendación**:
- **Cut rápido** (50ms): Para cambios de producto
- **Dissolve** (300ms): Para mismo producto, cambio de elemento

---

## 📝 Guión VO Adaptado

### Si unificas todos los productos:

```
"Hook del slide 1. [Producto 1] con [beneficio]. 
[Producto 2] con [beneficio]. [Producto 3] con [beneficio]. 
Empieza hoy con [CTA]."
```

**Duración**: ~14s

---

### Si por producto individual:

```
"[Hook]. [Producto] te ayuda a [beneficio principal]. 
Incluye [feature 1], [feature 2] y [feature 3]. 
[Prueba social]. [CTA]."
```

**Duración**: ~12-14s

---

## ✅ Checklist de Conversión

### Pre-conversión
- [ ] Identificar qué slides usar (todos o uno)
- [ ] Decidir estrategia (unificar vs individual)
- [ ] Extraer elementos clave de cada slide

### Conversión
- [ ] Coordenadas adaptadas (1080×1080 → 1080×1920)
- [ ] Elementos expandidos (más espacio vertical)
- [ ] Timing definido (qué aparece cuándo)
- [ ] Transiciones decididas (cut vs dissolve)

### Post-conversión
- [ ] Preview en 1080×1920
- [ ] Timing total: 15s
- [ ] VO sincronizado
- [ ] CTA visible desde 10s

---

## 🚀 Quick Conversion Template

1. **Abrir slide carousel** (ej. `carousel_slide_2_curso_1080x1080.svg`)
2. **Extraer elementos**:
   - Headline
   - Icono/visual
   - Beneficios
   - CTA (si tiene)
3. **Usar template base** de arriba
4. **Aplicar timing**:
   - Frame 1: 0-2s
   - Frame 2: 2-10s
   - Frame 3: 10-15s
5. **Añadir animaciones** (fade, slide, scale)
6. **Exportar** como base para video

---

**Última actualización**: [FECHA]  
**Versión**: 1.0  
**Formato origen**: Carousel 1080×1080 (5 slides)  
**Formato destino**: Video 1080×1920 (15s)



