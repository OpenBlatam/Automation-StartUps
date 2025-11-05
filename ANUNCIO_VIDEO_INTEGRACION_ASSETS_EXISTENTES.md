# Integración con Assets Existentes — Guía de Consistencia

> Guía para integrar los nuevos anuncios de video 15s con tus assets SVG existentes en `/ads/linkedin/`.

---

## 📁 Estructura de Assets Actual

Según tu estructura existente:

```
/ads/
  /linkedin/
    ad_curso_ia_*.svg (múltiples variantes)
    ad_saas_ia_marketing_*.svg
    ad_ia_bulk_*.svg
    carousel_slide_*.svg
    copy_variantes.md
    GUIA_EXPORTACION_ADS.md
    INDEX_ASSETS.md
```

---

## 🎯 Mapeo de Assets a Videos

### Curso IA + Webinar

**Assets SVG existentes → Video 15s**:
- `ad_curso_ia_1200x627_urgency.svg` → Versión V2 (Pain→Relief) con badge urgencia
- `ad_curso_ia_1200x627_social_proof.svg` → Versión V3 (UGC) con testimoniales
- `ad_curso_ia_1200x627_metrics.svg` → Versión V1 (Outcome) con cifras

**Adaptaciones necesarias**:
1. **Formato**: 1200×627 → 1080×1920 (vertical)
2. **Elementos clave a portar**:
   - Headline principal
   - Badge urgencia (si aplica)
   - Social proof (cifras/alumnos)
   - CTA button

**Elementos nuevos para video**:
- B-roll: UI curso, speaker webinar
- On-screen text animado
- Transiciones entre escenas

---

### SaaS IA Marketing

**Assets SVG existentes → Video 15s**:
- `ad_saas_ia_marketing_1200x627_metrics.svg` → Versión V3 (ROI-First)
- `ad_saas_ia_marketing_1200x627_light.svg` → Versión V1 (Speed-Run)
- `ad_saas_ia_marketing_1200x627_social_proof.svg` → Versión V2 (Consistencia)

**Elementos a portar**:
- Métricas destacadas (-60% tiempo, +ROI)
- UI mockup simplificado
- Logos integraciones
- CTA "Probar gratis"

---

### IA Bulk Docs

**Assets SVG existentes → Video 15s**:
- `ad_ia_bulk_1200x627_urgency.svg` → Versión V1 (Counter) con urgencia
- `ad_ia_bulk_1200x627_metrics.svg` → Versión V2 (Operativa)
- `ad_ia_bulk_1200x627_social_proof.svg` → Versión V3 (UGC)

**Elementos clave**:
- Counter visual (1→100)
- Grid documentos
- Badge exportación múltiple

---

## 🎨 Paleta de Colores Consistente

### Extraer de SVG Existente

Revisa tus SVG actuales para extraer:

```css
/* Ejemplo basado en ad_ia_bulk_1200x627_urgency.svg */
--color-primary: #0A2F4A;
--color-accent: #22C1A7 (o #2DD4BF);
--color-dark: #1E2B3A;
--color-urgent: #FF6B6B;
```

**Aplicar en**:
1. `ANUNCIO_VIDEO_PALETA_BRANDING.json` → Actualizar hex codes
2. Plantillas SVG de video → Reemplazar placeholders
3. Guiones de video → Referencias de color

---

## 📝 Copy Consistency Check

### Alinear Copy entre SVG y Video

**SVG Assets** (LinkedIn/Facebook Feed):
- Headline: Corto, punchy (≤10 palabras)
- Body: Detalle y beneficios
- CTA: "Solicitar demo" / "Ver más"

**Video 15s**:
- Hook: Mismo beneficio, formato audio
- On-screen: Resumen visual (≤8 palabras)
- CTA: "Inscríbete hoy" / "Probar gratis" (más directo)

**Checklist de alineación**:
- [ ] Mismo mensaje principal (beneficio clave)
- [ ] CTA coherente (mismo objetivo, diferente wording)
- [ ] Prueba social igual (cifras, testimonios)
- [ ] Urgencia/escasez consistente

---

## 🔄 Workflow de Integración

### Paso 1: Auditoría de Assets Existentes
```bash
# Revisar todos los SVG
ls -la ads/linkedin/*.svg

# Extraer copy/textos
grep -r "headline\|text" ads/linkedin/*.svg > copy_extract.txt

# Identificar paleta
grep -r "stop-color\|fill=" ads/linkedin/*.svg > colors_extract.txt
```

### Paso 2: Sincronizar Paleta
1. Abrir `ANUNCIO_VIDEO_PALETA_BRANDING.json`
2. Reemplazar placeholders con colores extraídos
3. Verificar contraste (≥ 4.5:1)

### Paso 3: Alinear Copy
1. Revisar `copy_variantes.md` (si existe)
2. Comparar con guiones de video
3. Asegurar mensaje consistente

### Paso 4: Crear Assets Video desde SVG
1. Usar plantillas de `ANUNCIO_VIDEO_PLANTILLAS_SVG_VIDEO.md`
2. Portar elementos clave (headlines, badges, CTAs)
3. Adaptar formato 1200×627 → 1080×1920

---

## 📊 Matriz de Consistencia

| Elemento | SVG Assets (LinkedIn) | Video 15s | Consistencia Requerida |
|----------|----------------------|----------|------------------------|
| **Headline** | "Mejora tu ROI en +20%" | "30 piezas en 5 min" | ✅ Mismo beneficio, formato diferente |
| **CTA** | "Solicitar demo" | "Probar gratis" | ⚠️ Objetivo igual, wording puede variar |
| **Social Proof** | "+2,000 alumnos" | "+2,000 alumnos" | ✅ Exacto |
| **Urgencia** | "⚡ Lanzamiento: 50% descuento" | "Cupos limitados" | ⚠️ Ajustar según necesidad |
| **Colores** | #22C1A7 (acento) | [COLORES MARCA-acento] | ✅ Debe ser igual |

---

## 🎬 Adaptación de Elementos Visuales

### Badges y Tags

**De SVG a Video**:
- **Tamaño**: Aumentar proporcionalmente (627→1920 = ×3.06)
- **Posición**: Respetar safe zones (150px top/bottom)
- **Animación**: Añadir entrada (slide-up + fade)

**Ejemplo adaptación badge urgencia**:
```svg
<!-- SVG original: 400×80 -->
<!-- Video adaptado: 1224×245 (mantener proporción, ajustar a safe zone) -->
```

### Headlines

**De SVG a Video**:
- **Fuente**: Mantener (Poppins/Inter)
- **Tamaño**: Ajustar para legibilidad (96-112px en video)
- **Animación**: Añadir motion (no estático)

### CTAs

**De SVG a Video**:
- **Forma**: Mantener (botón redondeado)
- **Tamaño**: Mínimo 360×112px
- **Posición**: Fixed desde 9-10s hasta final
- **Animación**: Pulso cada 1.5s

---

## ✅ Checklist de Integración Completa

### Pre-Producción
- [ ] Colores extraídos de SVG existentes
- [ ] Paleta sincronizada en JSON
- [ ] Copy alineado entre assets
- [ ] Headlines consistentes
- [ ] CTAs coherentes (mismo objetivo)

### Producción
- [ ] Assets SVG portados a formato video
- [ ] Safe zones respetadas
- [ ] Elementos visuales escalados correctamente
- [ ] Animaciones añadidas (no estático)

### Post-Producción
- [ ] Preview comparado con SVG original
- [ ] Mensaje verificado (consistente)
- [ ] Branding verificado (colores/logo)
- [ ] Export con mismo naming convention

---

## 🔗 Referencias Cruzadas

**Documentos relacionados**:
- `ads/linkedin/INDEX_ASSETS.md` → Inventario de assets
- `ads/linkedin/GUIA_EXPORTACION_ADS.md` → Especificaciones export
- `ads/linkedin/copy_variantes.md` → Variantes de copy

**Integración con nuevos documentos**:
- `ANUNCIO_VIDEO_PALETA_BRANDING.json` ← Sincronizar colores
- `ANUNCIO_VIDEO_PLANTILLAS_SVG_VIDEO.md` ← Usar templates
- Guiones de video ← Alinear copy

---

## 🚀 Quick Start Integración

1. **Extraer paleta**:
   ```bash
   grep -o "#[0-9A-Fa-f]\{6\}" ads/linkedin/*.svg | sort -u > colores_extract.txt
   ```

2. **Actualizar JSON**:
   - Abrir `ANUNCIO_VIDEO_PALETA_BRANDING.json`
   - Reemplazar placeholders con colores extraídos

3. **Portar copy**:
   - Revisar headlines de SVG
   - Adaptar a formato audio (guiones VO)
   - Mantener mismo mensaje

4. **Crear assets video**:
   - Usar plantillas SVG de video
   - Portar elementos clave
   - Añadir animaciones

---

**Última actualización**: [FECHA]  
**Versión**: 1.0  
**Estado**: ✅ Listo para integrar con assets existentes



