# SVG a Video Storyboard — De Tus Assets 1080×1920

> Análisis y conversión directa de tus SVG existentes en formato 1080×1920 a storyboards de video con timing.

---

## 📊 Análisis de SVG Existentes

### Estructura Identificada (de `ad_saas_ia_marketing_1080x1920.svg` y `ad_curso_ia_1080x1920.svg`)

**Elementos y posiciones**:
1. **Logo** (72, 84) - Top-left
2. **Eyebrow** (72, 340) - Uppercase, color #93C5FD
3. **Headline** (72, 340-620) - "Mejora tu ROI en +20%"
4. **Métricas** (72, 440) - Box horizontal con +27% Leads, -32% CPA
5. **Testimonial** (72, 610) - Box grande con quote
6. **CTA** (72, 770) - Botón "Solicita demo" / "Ver temario"
7. **Badge** (512, 778) - "✨ Demo en 15 min" / "✨ Plantillas incluidas"
8. **Growth chart** (820, 520) - Icono decorativo

---

## 🎬 Storyboard Temporal (15s)

### SaaS IA Marketing (de tu SVG)

```
TIEMPO     | ELEMENTO                    | POSICIÓN Y (del SVG) | ANIMACIÓN
-----------|----------------------------|---------------------|------------------
00:00-01:00| Logo fade-in                | 84                  | Opacity 0→1 (300ms)
01:00-02:00| Eyebrow slide-up            | 340                 | Y: +50px → 0 (400ms)
02:00-04:00| Headline "Mejora tu ROI"    | 440                 | Y: +30px → 0 (500ms)
           | Headline-accent "+20%"       | 530                 | Scale 0.9→1.0 (400ms)
04:00-05:00| Sub texto                   | 700                 | Fade-in (300ms)
05:00-07:00| Métricas aparecen            | 440                 | Opacity 0→1 + counter
           |   - "+27% Leads" primero    | 476                 | Counter 0→27% (1s)
           |   - "-32% CPA" después      | 476                 | Counter 0→-32% (1s)
07:00-09:00| Testimonial fade-in          | 610                 | Opacity 0→1 (400ms)
           |   + slide-right             |                     | X: -50px → 0 (400ms)
09:00-11:00| CTA aparece                 | 770                 | Scale 0.8→1.0 (400ms)
           |   + pulso continuo          |                     | Scale 1.0→1.05 (1.5s loop)
11:00-13:00| Badge aparece                | 778                 | Opacity 0→1 (300ms)
13:00-15:00| Growth chart anima           | 520                 | Barras crecen 0→100%
```

---

### Curso IA (de tu SVG)

```
TIEMPO     | ELEMENTO                    | POSICIÓN Y (del SVG) | ANIMACIÓN
-----------|----------------------------|---------------------|------------------
00:00-01:00| Logo fade-in                | 84                  | Opacity 0→1 (300ms)
01:00-02:00| Eyebrow "Formación aplicada"| 340                 | Slide-up (400ms)
02:00-04:00| Headline "Mejora tu ROI"    | 440                 | Slide-up (500ms)
           | Headline-accent "+20%"      | 530                 | Scale + glow (400ms)
04:00-05:00| Sub "Casos reales..."       | 700                 | Fade-in (300ms)
05:00-07:00| Métricas (mismo timing)     | 440                 | Counter animado
07:00-09:00| Testimonial                 | 610                 | Fade + slide
09:00-11:00| CTA "Ver temario"           | 770                 | Scale + pulso
11:00-13:00| Badge "Plantillas incluidas"| 778                 | Fade-in
13:00-15:00| Growth chart                | 520                 | Animación barras
```

---

## 🎨 Guía de Animaciones por Elemento

### 1. Logo (Top-left)

**Estado inicial**: Opacity 0, Y = 84px  
**Estado final**: Opacity 1, Y = 84px  
**Duración**: 300ms  
**Easing**: Ease-out

**Código After Effects**:
```javascript
// Opacity
opacity.keyframeValueAtTime(0, 0);
opacity.keyframeValueAtTime(0.3, 100);

// Opcional: Scale ligero
scale.keyframeValueAtTime(0, [90, 90]);
scale.keyframeValueAtTime(0.3, [100, 100]);
```

---

### 2. Eyebrow (Uppercase label)

**Estado inicial**: Opacity 0, Y = 390px (340 + 50)  
**Estado final**: Opacity 1, Y = 340px  
**Duración**: 400ms  
**Easing**: Ease-out

**Código After Effects**:
```javascript
// Position Y
position.keyframeValueAtTime(1.0, [540, 390]);
position.keyframeValueAtTime(1.4, [540, 340]);

// Opacity
opacity.keyframeValueAtTime(1.0, 0);
opacity.keyframeValueAtTime(1.4, 100);
```

---

### 3. Headline Principal

**Estado inicial**: Opacity 0, Y = 470px (440 + 30)  
**Estado final**: Opacity 1, Y = 440px  
**Duración**: 500ms  
**Easing**: Ease-out

**Variante con split**: Palabra "ROI" aparece primero, luego "+20%" con scale.

---

### 4. Headline-Accent (+20%)

**Efecto especial**: Scale + glow  
**Estado inicial**: Scale 0.8, opacity 0  
**Estado final**: Scale 1.0, opacity 1  
**Glow**: Añadir efecto "Glow" con color acento

**Código After Effects**:
```javascript
// Scale
scale.keyframeValueAtTime(2.5, [80, 80]);
scale.keyframeValueAtTime(2.9, [100, 100]);

// Glow effect (aplicar efecto nativo)
// Glow: Intensity 150, Radius 30, Color: #3B82F6
```

---

### 5. Métricas (Counter Animation)

**Estado inicial**: Opacity 0, valor numérico = 0  
**Estado final**: Opacity 1, valor numérico = +27% o -32%  
**Duración counter**: 1000ms  
**Easing**: Ease-out

**Código After Effects** (usando expresiones):
```javascript
// Expression para counter
n = 0;
if (time >= 5.0) {
  dur = 1.0; // 1 segundo para animar
  startTime = 5.0;
  endValue = 27; // o -32
  progress = (time - startTime) / dur;
  if (progress <= 1) {
    n = Math.round(easeOut(progress, 0, endValue));
  } else {
    n = endValue;
  }
}
n + "%";
```

---

### 6. Testimonial Box

**Estado inicial**: Opacity 0, X = -50px (fuera de pantalla)  
**Estado final**: Opacity 1, X = 540px (centrado)  
**Duración**: 400ms  
**Easing**: Ease-out

**Código After Effects**:
```javascript
// Position X
position.keyframeValueAtTime(7.0, [490, 610]); // X -50px
position.keyframeValueAtTime(7.4, [540, 610]); // X centrado

// Opacity
opacity.keyframeValueAtTime(7.0, 0);
opacity.keyframeValueAtTime(7.4, 100);
```

---

### 7. CTA Button

**Estado inicial**: Scale 0.8, opacity 0  
**Estado final**: Scale 1.0, opacity 1  
**Luego**: Pulso continuo 1.0 → 1.05 cada 1.5s

**Código After Effects**:
```javascript
// Initial appearance (9.0s)
scale.keyframeValueAtTime(9.0, [80, 80]);
scale.keyframeValueAtTime(9.4, [100, 100]);
opacity.keyframeValueAtTime(9.0, 0);
opacity.keyframeValueAtTime(9.4, 100);

// Pulse loop (desde 9.4s hasta final)
function pulse() {
  freq = 1.5; // 1.5 segundos por ciclo
  amp = 5; // 5% de scale
  baseScale = 100;
  return baseScale + Math.sin((time - 9.4) * 2 * Math.PI / freq) * amp;
}
[pulse(), pulse()];
```

---

### 8. Badge (✨ Demo en 15 min)

**Estado inicial**: Opacity 0, Y = 800px (778 + 22)  
**Estado final**: Opacity 1, Y = 778px  
**Duración**: 300ms  
**Easing**: Ease-out

---

### 9. Growth Chart (Decorativo)

**Animación**: Barras crecen secuencialmente  
**Timing**: Últimos 2s del video (13-15s)  
**Efecto**: Cada barra crece de 0 a su altura final con delay

**Código After Effects**:
```javascript
// Para cada barra (3 barras)
// Barra 1 (izquierda)
bar1_scaleY.keyframeValueAtTime(13.0, 0);
bar1_scaleY.keyframeValueAtTime(13.5, 100);

// Barra 2 (centro)
bar2_scaleY.keyframeValueAtTime(13.2, 0);
bar2_scaleY.keyframeValueAtTime(13.7, 100);

// Barra 3 (derecha)
bar3_scaleY.keyframeValueAtTime(13.4, 0);
bar3_scaleY.keyframeValueAtTime(13.9, 100);
```

---

## 📝 VO Timing Sincronizado

### Para SaaS IA Marketing (basado en elementos del SVG):

```
00:00-01:00: [Silencio o música suave]
01:00-02:00: "Automatización con datos propios"
02:00-04:00: "Mejora tu ROI en veinte por ciento"
04:00-05:00: "con SaaS de IA para marketing"
05:00-07:00: "Segmentación y reporting conectados"
07:00-09:00: "CPA menos treinta y dos por ciento y veintisiete por ciento más leads"
09:00-11:00: "La automatización nos liberó doce horas semanales"
11:00-13:00: "Solicita una demo en quince minutos"
13:00-15:00: [ESLOGAN]
```

**Total palabras**: ~45 | **Duración**: ~13s | **WPM**: ~160

---

## 🎯 Checklist de Conversión SVG → Video

### Pre-producción
- [ ] SVG importado en After Effects/Premiere
- [ ] Elementos separados en capas
- [ ] Timing definido (usar tabla de arriba)
- [ ] VO grabado/sincronizado

### Animación
- [ ] Logo: Fade-in (0-1s)
- [ ] Eyebrow: Slide-up (1-2s)
- [ ] Headline: Slide-up + glow accent (2-4s)
- [ ] Métricas: Counter animado (5-7s)
- [ ] Testimonial: Fade + slide (7-9s)
- [ ] CTA: Scale + pulso (9-15s)
- [ ] Badge: Fade-in (11-13s)
- [ ] Growth chart: Barras crecen (13-15s)

### Post-producción
- [ ] Duración exacta: 15s
- [ ] Audio sincronizado
- [ ] Safe zones respetadas
- [ ] Export: 1080×1920, H.264, 15-20 Mbps

---

## 🚀 Quick Start: Usar Tu SVG Directamente

1. **Abrir SVG en After Effects**:
   - File → Import → SVG
   - Convertir a comp editable
   - Separar elementos en capas

2. **Aplicar timing**:
   - Usar tabla de storyboard arriba
   - Añadir keyframes según timing

3. **Añadir animaciones**:
   - Usar código de arriba (expresiones)
   - O animaciones predefinidas de AE

4. **Sincronizar VO**:
   - Importar audio VO
   - Ajustar timing de elementos al audio

5. **Exportar**:
   - H.264, 1080×1920, 15s

---

**Última actualización**: [FECHA]  
**Versión**: 1.0  
**Fuente**: Análisis directo de `ad_*_1080x1920.svg`



