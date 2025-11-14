# Índice Maestro — Paquete Completo Anuncios Video 15s

> Navegación centralizada de todos los recursos para producir y optimizar los 3 anuncios de video (Curso, SaaS, Bulk).

---

## 📚 Documentos Principales (Guiones)

### 🎬 Anuncios por Producto

1. **[ANUNCIO_VIDEO_01_CURSO_IA_WEBINAR_15s.md](./ANUNCIO_VIDEO_01_CURSO_IA_WEBINAR_15s.md)**
   - 3 versiones completas (Outcome, Pain→Relief, UGC)
   - Timecodes exactos a 30fps
   - Guiones VO (3 tonos)
   - B-roll checklist
   - Subtítulos SRT incluidos

2. **[ANUNCIO_VIDEO_02_SAAS_IA_MARKETING_15s.md](./ANUNCIO_VIDEO_02_SAAS_IA_MARKETING_15s.md)**
   - 3 versiones (Speed-Run, Consistencia, ROI-First)
   - Especificaciones técnicas
   - Métricas objetivo
   - Markers CSV

3. **[ANUNCIO_VIDEO_03_IA_BULK_DOCUMENTOS_15s.md](./ANUNCIO_VIDEO_03_IA_BULK_DOCUMENTOS_15s.md)**
   - 3 versiones (Counter, Operativa, UGC)
   - Paleta oscura especializada
   - Assets técnicos

---

## 🎨 Recursos de Branding y Diseño

### **[ANUNCIO_VIDEO_PALETA_BRANDING.json](./ANUNCIO_VIDEO_PALETA_BRANDING.json)**
- Paleta completa [COLORES MARCA]
- Tipografía (Poppins/Inter)
- Especificaciones CTA
- Safe zones
- Configuración audio/video
- Naming conventions

**Uso**: Importar en herramientas de diseño (Figma, Canva, After Effects)

---

## 🎯 Recursos de Estrategia y Decisión

### **[ANUNCIO_VIDEO_MATRIZ_DECISION_VERSIONES.md](./ANUNCIO_VIDEO_MATRIZ_DECISION_VERSIONES.md)**
- Matriz de decisión por producto
- Selección por objetivo (Awareness/Consideración/Conversión)
- Selección por audiencia (Frío/Tibio/Caliente)
- Selección por persona (Early Adopter/Cauteloso/B2B)
- Tabla de puntuación rápida
- Decision tree visual

**Uso**: Elegir qué versión usar según tu situación

### **[ANUNCIO_VIDEO_VARIANTES_HOOKS_EXTRA.md](./ANUNCIO_VIDEO_VARIANTES_HOOKS_EXTRA.md)**
- 50+ hooks alternativos
- Organizados por producto y tipo
- Matriz Hook × CTA
- Rotación recomendada por semana
- Priorización de testing

**Uso**: A/B testing y rotación de creativos

---

## ✅ Recursos Operativos

### **[ANUNCIO_VIDEO_CHECKLIST_PRODUCCION_COMPLETA.md](./ANUNCIO_VIDEO_CHECKLIST_PRODUCCION_COMPLETA.md)**
- Checklist exhaustivo (7 fases)
- Pre-producción
- Edición
- Branding y compliance
- Export y archivo
- QA y validación
- Metadata y tracking
- Lanzamiento

**Uso**: Asegurar producción sin errores

---

## 🚀 Flujo de Trabajo Recomendado

### Paso 1: Decisión Estratégica
1. Leer **[ANUNCIO_VIDEO_MATRIZ_DECISION_VERSIONES.md](./ANUNCIO_VIDEO_MATRIZ_DECISION_VERSIONES.md)**
2. Definir objetivo, audiencia, etapa
3. Elegir versión (V1/V2/V3) por producto

### Paso 2: Configuración de Branding
1. Abrir **[ANUNCIO_VIDEO_PALETA_BRANDING.json](./ANUNCIO_VIDEO_PALETA_BRANDING.json)**
2. Reemplazar placeholders:
   - `[NOMBRE DEL PRODUCTO]`
   - `[COLORES MARCA-*]` (hex codes)
   - `[ESLOGAN]`
   - `[PLATAFORMA]`
3. Guardar configuración final

### Paso 3: Pre-Producción
1. Abrir guion del producto seleccionado:
   - `ANUNCIO_VIDEO_01_CURSO_IA_WEBINAR_15s.md`
   - `ANUNCIO_VIDEO_02_SAAS_IA_MARKETING_15s.md`
   - `ANUNCIO_VIDEO_03_IA_BULK_DOCUMENTOS_15s.md`
2. Revisar checklist B-roll en el documento
3. Usar **[ANUNCIO_VIDEO_CHECKLIST_PRODUCCION_COMPLETA.md](./ANUNCIO_VIDEO_CHECKLIST_PRODUCCION_COMPLETA.md)** Fase 1

### Paso 4: Producción
1. Seguir timecodes exactos del guion
2. Aplicar paleta desde JSON
3. Revisar compliance (disclaimers, contrastes)
4. Usar checklist Fase 2-4

### Paso 5: Testing y Optimización
1. Consultar **[ANUNCIO_VIDEO_VARIANTES_HOOKS_EXTRA.md](./ANUNCIO_VIDEO_VARIANTES_HOOKS_EXTRA.md)** para alternativas
2. Configurar A/B testing (3 variantes día 1)
3. Monitorear métricas (Fase 6-7 del checklist)

---

## 📊 Estructura de Archivos Sugerida

```
/anuncios_video_15s/
  /documentos/
    ANUNCIO_VIDEO_INDICE_MAESTRO.md
    ANUNCIO_VIDEO_01_CURSO_IA_WEBINAR_15s.md
    ANUNCIO_VIDEO_02_SAAS_IA_MARKETING_15s.md
    ANUNCIO_VIDEO_03_IA_BULK_DOCUMENTOS_15s.md
    ANUNCIO_VIDEO_PALETA_BRANDING.json
    ANUNCIO_VIDEO_MATRIZ_DECISION_VERSIONES.md
    ANUNCIO_VIDEO_CHECKLIST_PRODUCCION_COMPLETA.md
    ANUNCIO_VIDEO_VARIANTES_HOOKS_EXTRA.md
    ANUNCIO_VIDEO_TEMPLATE_ANTES_DESPUES.md
    ANUNCIO_VIDEO_TEMPLATE_NUMEROS_GRANDES.md
    ANUNCIO_VIDEO_STORYBOARD_IA_BULK.md
  /exports/
    /curso_ia_webinar/
      v1-outcome.mp4
      v2-pain-relief.mp4
      v3-ugc.mp4
      subtitles_es.srt
      markers.csv
    /saas_ia_marketing/
      v1-speedrun.mp4
      v2-consistencia.mp4
      v3-roi.mp4
      subtitles_es.srt
      markers.csv
    /ia_bulk_docs/
      v1-counter.mp4
      v2-operativa.mp4
      v3-ugc.mp4
      subtitles_es.srt
      markers.csv
  /assets/
    /b-roll/
      curso_ui_screenshot_01.png
      speaker_webinar_clip.mp4
      testimonios/
    /branding/
      logo.svg
      logo.png
      fuentes/
  /thumbnails/
    curso-ia-thumb-v1.png
    saas-marketing-thumb-v1.png
    bulk-docs-thumb-v1.png
```

---

## 🎯 Quick Reference (Referencia Rápida)

### Por Urgencia

**Necesito empezar YA**:
1. Lee `ANUNCIO_VIDEO_MATRIZ_DECISION_VERSIONES.md` → Elige versión
2. Abre guion del producto → Sigue timecodes
3. Usa `ANUNCIO_VIDEO_CHECKLIST_PRODUCCION_COMPLETA.md` → Fase 1-2

**Necesito optimizar creativo existente**:
1. Lee `ANUNCIO_VIDEO_VARIANTES_HOOKS_EXTRA.md` → Prueba hook alternativo
2. Revisa métricas objetivo en guion del producto
3. Ajusta según reglas de optimización

**Necesito validar compliance**:
1. `ANUNCIO_VIDEO_CHECKLIST_PRODUCCION_COMPLETA.md` → Fase 3 (Branding y Compliance)
2. Revisa disclaimers en guion del producto

### Por Rol

**Director Creativo**:
- `ANUNCIO_VIDEO_MATRIZ_DECISION_VERSIONES.md`
- `ANUNCIO_VIDEO_VARIANTES_HOOKS_EXTRA.md`
- Guiones de producto (sección Copy)

**Editor/Productor**:
- Guiones de producto (timecodes, motion)
- `ANUNCIO_VIDEO_CHECKLIST_PRODUCCION_COMPLETA.md`
- `ANUNCIO_VIDEO_PALETA_BRANDING.json`

**Marketing Manager**:
- `ANUNCIO_VIDEO_MATRIZ_DECISION_VERSIONES.md`
- Guiones de producto (métricas objetivo, A/B testing)
- Checklist Fase 6-7 (lanzamiento)

---

## 📈 Métricas Objetivo por Producto

### Curso IA + Webinar
- **VTR 15s**: ≥22%
- **CTR**: ≥1.5%
- **Lead→Compra**: 6-8%

### SaaS IA Marketing
- **VTR 15s**: ≥24%
- **CTR**: ≥2.0%
- **Free→Active Day-1**: ≥30%

### IA Bulk Docs
- **VTR 15s**: ≥24%
- **CTR**: ≥2.0%
- **Demo→Trial**: ≥12%

---

## 🔄 Versiones y Changelog

**v1.0** (2025-01-XX)
- ✅ 3 guiones completos (9 versiones totales)
- ✅ Paleta JSON
- ✅ Matriz de decisión
- ✅ Checklist completo
- ✅ 50+ hooks alternativos
- ✅ Índice maestro

**Próximas mejoras**:
- [ ] Plantillas After Effects (.aep)
- [ ] Scripts de automatización (Python/JS)
- [ ] Dashboard métricas (Looker Studio)
- [ ] Guías por plataforma específica (TikTok, YouTube Shorts)

---

## 📞 Soporte y Preguntas

**Dudas sobre guiones**: Revisa sección FAQ en cada guion  
**Dudas sobre estrategia**: `ANUNCIO_VIDEO_MATRIZ_DECISION_VERSIONES.md`  
**Dudas técnicas**: `ANUNCIO_VIDEO_CHECKLIST_PRODUCCION_COMPLETA.md`

---

## 🆕 Recursos Avanzados (Nuevos)

### **[ANUNCIO_VIDEO_PLANTILLAS_SVG_VIDEO.md](./ANUNCIO_VIDEO_PLANTILLAS_SVG_VIDEO.md)**
- Plantillas SVG para covers (1080×1920)
- Overlays de texto on-screen
- Badges (urgencia, social proof)
- Contadores animados
- Compatible con After Effects, Premiere, CapCut

**Uso**: Importar SVG, reemplazar placeholders, animar

---

### **[ANUNCIO_VIDEO_AUTOMATION_SCRIPTS.md](./ANUNCIO_VIDEO_AUTOMATION_SCRIPTS.md)**
- Generador de variantes de guiones VO (Python)
- Batch processor de SRT
- Generador de markers CSV
- Validador de metadata (JavaScript)
- Batch export con FFmpeg
- Generador de UTM links
- Calculadora de métricas objetivo

**Uso**: Automatizar generación masiva de variantes

---

### **[ANUNCIO_VIDEO_INTEGRACION_ASSETS_EXISTENTES.md](./ANUNCIO_VIDEO_INTEGRACION_ASSETS_EXISTENTES.md)**
- Mapeo de assets SVG existentes → Video
- Guía de consistencia de copy
- Extracción de paleta de colores
- Workflow de integración
- Matriz de consistencia
- Checklist de integración completa

**Uso**: Sincronizar nuevos videos con assets actuales

---

### **[ANUNCIO_VIDEO_PALETA_EXTRAIDA.json](./ANUNCIO_VIDEO_PALETA_EXTRAIDA.json)**
- ✅ Paleta extraída directamente de tus SVG existentes
- Colores exactos de prerolls y anuncios LinkedIn
- Aplicación por producto (Curso, SaaS, Bulk)
- Fuentes y sombras configuradas
- Listo para usar (sin placeholders)

**Uso**: Importar en After Effects/Premiere, aplicar directamente

---

### **[ANUNCIO_VIDEO_TEMPLATES_WEBINAR_PREROLL.md](./ANUNCIO_VIDEO_TEMPLATES_WEBINAR_PREROLL.md)**
- Templates basados en tus prerolls de webinar
- Adaptación de `webinar-preroll-social-proof.svg` → Video 15s
- Adaptación de métricas destacadas (stats boxes)
- Templates SVG listos (1080×1920)
- Timing y animaciones sugeridas

**Uso**: Portar elementos de prerolls a videos de anuncios

---

### **[ANUNCIO_VIDEO_QUICK_START_GUIDE.md](./ANUNCIO_VIDEO_QUICK_START_GUIDE.md)**
- ⚡ Producción en 30 minutos
- Setup rápido (5 min)
- Producción CapCut/Premiere (15 min)
- Checklist express (5 min)
- Publicación Meta Ads (5 min)
- Troubleshooting común

**Uso**: Primer anuncio rápido, paso a paso simplificado

---

### **[ANUNCIO_VIDEO_ADAPTACION_FORMATOS.md](./ANUNCIO_VIDEO_ADAPTACION_FORMATOS.md)**
- 🔄 Conversión 1080×1080 → 1080×1920
- Conversión 1200×627 → 1080×1920
- Script Python para adaptar coordenadas
- Templates de conversión por formato
- Matriz de elementos (posición original → video)
- Estrategias de adaptación (reutilizar, extraer, portar)

**Uso**: Convertir tus assets estáticos existentes a video

---

### **[ANUNCIO_VIDEO_BEST_PRACTICES_EXTRACTED.md](./ANUNCIO_VIDEO_BEST_PRACTICES_EXTRACTED.md)**
- 📊 Patrones extraídos de tus 30+ assets SVG
- Jerarquía visual consistente
- Paleta de colores aplicada
- Espaciado y proporciones
- Tipografía (pesos y tamaños)
- Timing sugerido por elemento
- Checklist de aplicación

**Uso**: Aplicar tus propios estándares de diseño en videos

---

### **[ANUNCIO_VIDEO_CAROUSEL_TO_VIDEO.md](./ANUNCIO_VIDEO_CAROUSEL_TO_VIDEO.md)**
- 🎠 Conversión de carousel slides → Video
- Timing por slide (hook, productos, CTA)
- Estrategias (unificar vs individual)
- Templates de conversión
- Transiciones sugeridas
- Guiones VO adaptados

**Uso**: Convertir tus 5 slides de carousel en video narrativo

---

### **[ANUNCIO_VIDEO_SVG_TO_VIDEO_STORYBOARD.md](./ANUNCIO_VIDEO_SVG_TO_VIDEO_STORYBOARD.md)**
- 🎬 Storyboard temporal de tus SVG 1080×1920
- Timing exacto por elemento (logo, headline, métricas, CTA)
- Animaciones sugeridas (fade, slide, scale, pulse)
- VO sincronizado con elementos
- Tabla de timecode completo

**Uso**: Animar directamente tus SVG existentes sin recrear layout

---

### **Nuevas Plantillas y Storyboard**
- **[ANUNCIO_VIDEO_TEMPLATE_ANTES_DESPUES.md](./ANUNCIO_VIDEO_TEMPLATE_ANTES_DESPUES.md)** — Comparativa antes/después
- **[ANUNCIO_VIDEO_TEMPLATE_NUMEROS_GRANDES.md](./ANUNCIO_VIDEO_TEMPLATE_NUMEROS_GRANDES.md)** — Métricas con tipografía grande
- **[ANUNCIO_VIDEO_STORYBOARD_IA_BULK.md](./ANUNCIO_VIDEO_STORYBOARD_IA_BULK.md)** — Flujo IA Bulk (Counter)

**Uso**: Elegir plantilla según ángulo creativo y adaptar al producto

---

### **[ANUNCIO_VIDEO_EXPRESIONES_AFTER_EFFECTS.md](./ANUNCIO_VIDEO_EXPRESIONES_AFTER_EFFECTS.md)**
- ⚙️ Expresiones AE listas para copiar/pegar
- Counter numérico (métricas animadas)
- Pulso continuo (CTA)
- Fade-in con slide-up
- Scale con glow (headline accent)
- Barras creciendo (growth chart)
- Helper functions (ease-out, etc.)

**Uso**: Automatizar animaciones en After Effects sin keyframes manuales

---

### **[ANUNCIO_VIDEO_MAPEO_SVG_GUIONES.md](./ANUNCIO_VIDEO_MAPEO_SVG_GUIONES.md)**
- 🔗 Correspondencia exacta SVG ↔ Guiones
- Mapeo por producto (SaaS, Curso, Bulk)
- Timing comparativo (SVG vs Guión)
- Estrategias híbridas (combinar ambos)
- VO adaptado para SVG
- Workflow recomendado

**Uso**: Elegir qué usar: SVG directo, guión completo, o híbrido

