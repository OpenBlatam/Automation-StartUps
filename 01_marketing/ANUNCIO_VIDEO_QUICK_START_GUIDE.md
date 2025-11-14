# Quick Start Guide — Anuncios Video 15s en 30 Minutos

> Guía rápida para producir tu primer anuncio de video 15s en menos de 30 minutos.

---

## ⚡ Setup Rápido (5 minutos)

### 1. Reemplazar Placeholders

Abre `ANUNCIO_VIDEO_PALETA_EXTRAIDA.json` y ajusta:

```json
{
  "aplicacion_por_producto": {
    "curso_ia": {
      "fondo": "#092A44",  // ✅ Ya extraído de tus SVG
      "accent": "#2E86DE",  // ✅ Ya extraído
      "texto": "#FFFFFF",
      "urgencia": "#FF6B6B"
    }
  }
}
```

**✅ Colores ya están sincronizados** — Solo verifica que coincidan.

---

### 2. Elegir Versión (2 minutos)

Consulta `ANUNCIO_VIDEO_MATRIZ_DECISION_VERSIONES.md`:

- **Primera vez / Alcance**: V1 (Outcome/Speed-Run/Counter)
- **Retargeting**: V2 (Pain→Relief/Consistencia/Operativa)
- **Cierre**: V3 (UGC/ROI-First)

**Decisión rápida**: Si es día 1, usa **V1** de cada producto.

---

### 3. Copiar Guion VO (1 minuto)

Del guion elegido (ej. `ANUNCIO_VIDEO_01_CURSO_IA_WEBINAR_15s.md`):

1. Abre sección "Guiones VO"
2. Copia el tono "Directo" (más universal)
3. Reemplaza `[NOMBRE DEL PRODUCTO]` y `[ESLOGAN]`
4. Guarda como `guion_vo.txt`

**Ejemplo rápido**:
```
¿Listo para dominar IA en semanas, no meses? [Tu Producto] te guía con clases prácticas, proyectos reales y webinar en vivo con Q&A. Obtén certificado y acceso de por vida. Inscríbete hoy. [Tu Eslogan].
```

---

## 🎬 Producción Rápida (15 minutos)

### Opción A: CapCut (Más Rápido)

1. **Importar assets** (2 min):
   - B-roll: 2-3 clips (UI, speaker, testimonios)
   - Música: 105-115 BPM
   - Logo

2. **Montaje básico** (5 min):
   - Capa 1: B-roll (0-12s)
   - Capa 2: VO audio (importar `guion_vo.txt` → TTS o grabar)
   - Capa 3: Textos on-screen (usar plantillas SVG si tienes)

3. **Texto on-screen** (3 min):
   - Hook: "IA en 4 semanas" (0-2s)
   - Beneficio: "Webinar en vivo" (3-6s)
   - Prueba social: "+2,000 alumnos" (7-10s)
   - CTA: "Inscríbete hoy" (10-15s)

4. **CTA Button** (3 min):
   - Importar overlay SVG de `ANUNCIO_VIDEO_PLANTILLAS_SVG_VIDEO.md`
   - Posicionar: 10s hasta final
   - Añadir animación: Pulso (opcional)

5. **Ajustes finales** (2 min):
   - Duración exacta: 15s
   - Audio: Ducking VO -8dB
   - Export: 1080×1920, H.264

**Tiempo total: ~15 minutos**

---

### Opción B: Premiere (Más Control)

1. **Setup proyecto** (1 min):
   - Nuevo: 1080×1920, 30fps
   - Importar: B-roll, VO, música

2. **Markers CSV** (2 min):
   - Copiar de guion: `markers_curso_ia.csv`
   - Importar markers en Premiere
   - Usar como referencia de tiempo

3. **Edición** (8 min):
   - B-roll + VO sincronizado
   - Textos on-screen (Essential Graphics)
   - CTA desde 9-10s

4. **Export** (2 min):
   - H.264, 15-20 Mbps
   - 1080×1920
   - Nombre: `instagram-curso-ia-15s-v1-outcome.mp4`

5. **SRT subtítulos** (2 min):
   - Copiar de guion: `subtitles_curso_ia_es.srt`
   - Importar en Premiere o quemar

**Tiempo total: ~15 minutos**

---

## 📝 Checklist Express (5 minutos)

Antes de publicar:

### Técnico
- [ ] Duración: 15s exactos (±0.1s)
- [ ] Resolución: 1080×1920
- [ ] Audio: -14 LUFS (o normalizado)
- [ ] Sin clipping/glitches

### Contenido
- [ ] VO completo en ≤14s
- [ ] CTA visible desde 9-10s
- [ ] [ESLOGAN] en últimos 2s
- [ ] Subtítulos quemados (opcional pero recomendado)

### Branding
- [ ] Colores correctos (de `PALETA_EXTRAIDA.json`)
- [ ] Logo visible
- [ ] Fuentes: Inter/Poppins
- [ ] Contraste ≥ 4.5:1

### Compliance
- [ ] Disclaimers si aplica ("Imágenes simuladas")
- [ ] Sin claims garantistas
- [ ] Prueba social verificable

---

## 🚀 Publicación (5 minutos)

### Meta Ads Manager

1. **Crear anuncio**:
   - Formato: Reels/Stories
   - Video: Subir export
   - Thumbnail: Generar o usar cover SVG

2. **Copy**:
   - Título: Del guion (ej. "IA en 4 semanas")
   - Primario: Del guion (ej. "Aplica IA con clases prácticas...")
   - CTA: "Inscríbete hoy"

3. **UTMs**:
   - Usar script: `generar_utm_link()` de `AUTOMATION_SCRIPTS.md`
   - O manual: `?utm_source=instagram&utm_medium=video&utm_campaign=curso_ia_launch&utm_content=v1_outcome`

4. **Configurar**:
   - Objetivo: Conversiones
   - Audiencia: Frío (si primera vez)
   - Presupuesto: $XX/día
   - Publicar

---

## 🎯 Variantes Rápidas (Opcional)

Si tienes 10 minutos extra:

### Variante 1: Cambiar Hook
1. Del guion, sección "Hooks alternativos"
2. Reemplazar hook principal
3. Re-grabar VO (o TTS) con nuevo hook
4. Re-exportar

### Variante 2: Cambiar CTA
1. Del guion, sección "CTA alternativos"
2. Cambiar texto botón
3. Re-exportar solo últimos 5s (si es overlay)

### Variante 3: Thumbnail Alternativo
1. Usar template SVG cover
2. Cambiar texto (3-4 palabras)
3. Exportar PNG 1080×1920

---

## 📊 Métricas a Revisar (Primeros 3 Días)

### Día 1
- **6h después**: VTR15 ≥ 20%? Si no, probar hook alternativo
- **12h después**: CTR ≥ 1.5%? Si no, cambiar thumbnail

### Día 2
- Comparar variantes A/B/C
- Pausar peores 50% si CPA > 1.5× meta

### Día 3
- Duplicar ganadora con nuevo hook
- Introducir V2 o V3 según métricas

---

## 🔧 Troubleshooting Rápido

### Problema: VO no cabe en 15s
**Solución**: Usar tono "Inspiracional" (más corto) o reducir pausas.

### Problema: CTA no se ve
**Solución**: Verificar contraste, aumentar tamaño (mín 360×112px), añadir sombra.

### Problema: Thumbnail no se genera
**Solución**: Usar template SVG cover manual o screenshot del frame 01:00.

### Problema: Export pesado (>50MB)
**Solución**: Reducir bitrate a 15 Mbps o comprimir con HandBrake.

---

## ✅ Resumen: 30 Minutos Totales

| Paso | Tiempo | Herramienta |
|------|--------|-------------|
| Setup (placeholders, versión) | 5 min | JSON, Matriz decisión |
| Producción | 15 min | CapCut/Premiere |
| QA y ajustes | 5 min | Checklist |
| Publicación | 5 min | Meta Ads Manager |
| **TOTAL** | **30 min** | |

---

## 🎁 Recursos Adicionales (Si Tienes Más Tiempo)

- **Plantillas SVG avanzadas**: `ANUNCIO_VIDEO_PLANTILLAS_SVG_VIDEO.md`
- **Scripts automatización**: `ANUNCIO_VIDEO_AUTOMATION_SCRIPTS.md`
- **50+ hooks alternativos**: `ANUNCIO_VIDEO_VARIANTES_HOOKS_EXTRA.md`
- **Integración assets**: `ANUNCIO_VIDEO_INTEGRACION_ASSETS_EXISTENTES.md`

---

**Última actualización**: [FECHA]  
**Versión**: 1.0  
**Objetivo**: Primer anuncio en 30 minutos



