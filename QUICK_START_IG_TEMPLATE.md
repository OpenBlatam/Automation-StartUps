# 🚀 Quick Start: Template Instagram "Antes/Después" con UTMs

Guía rápida para usar `instagram_antes_despues_template.svg` con tracking completo.

---

## ⚡ Setup rápido (5 minutos)

### 1. Editar template SVG

**Abrir**: `instagram_antes_despues_template.svg` en Illustrator/Inkscape/Figma

**Buscar por ID** (ver líneas 93-200 del SVG):
- `headlineText` → Editar titular
- `beforeMetric` / `afterMetric` → Editar métricas antes/después
- `cta-link` o elemento con `href` → **Añadir URL con UTMs**

### 2. Generar URL con UTMs

**Opción A: Usar helper script** (`IG_TEMPLATE_UTM_HELPER.js`)
```bash
node IG_TEMPLATE_UTM_HELPER.js
```

**Opción B: Manual**
```
https://tusitio.com/landing?
  utm_source=instagram&
  utm_medium=feed&
  utm_campaign=cursoia_resultados_ig_2025-11&
  utm_content=antes_despues_v1&
  utm_term=mx_buyer
```

### 3. Actualizar URL en SVG

**En el elemento CTA**, reemplazar:
```xml
<!-- ANTES -->
<a href="https://tu-sitio.com">

<!-- DESPUÉS -->
<a href="https://tusitio.com/landing?utm_source=instagram&utm_medium=feed&utm_campaign=cursoia_resultados_ig_2025-11&utm_content=antes_despues_v1&utm_term=mx_buyer">
```

### 4. Exportar PNG

- **Dimensiones**: 1080×1350 px
- **Formato**: PNG o JPG (calidad 90%+)
- **Nombre**: `antes_despues_v1_ig_2025-11-30.png` (coincide con `utm_content`)

---

## 📱 Publicar en Instagram

### Post principal
1. **Imagen**: Subir PNG exportado
2. **Caption**: Incluir hashtags y call-to-action
3. **URL**: Añadir en primera comentario O en bio (si usas link único)

### Stories
1. **Sticker**: "Más información"
2. **URL**: Usar misma URL pero cambiar `utm_medium=stories`
   ```
   https://tusitio.com/landing?utm_source=instagram&utm_medium=stories&utm_campaign=cursoia_resultados_ig_2025-11&utm_content=antes_despues_v1&utm_term=mx_buyer
   ```

---

## 📊 Tracking y reportes

### Ver en GA4
1. **Adquisición** → Tráfico de adquisición
2. Filtro: `Campaign = cursoia_resultados_ig_2025-11`
3. Ver `Ad content` = `antes_despues_v1` para este post específico

### Ver en CRM
1. Buscar contactos con `utm_campaign = cursoia_resultados_ig_2025-11`
2. Filtrar por `utm_content = antes_despues_v1`
3. Ver cuántos leads vinieron de este post específico

---

## 🔄 Workflow completo

```
1. Editar SVG → 2. Generar URL con UTMs → 3. Actualizar CTA → 
4. Exportar PNG → 5. Publicar IG → 6. Trackear en GA4/CRM
```

---

## ✅ Checklist antes de publicar

- [ ] URL del CTA actualizada con UTMs completos
- [ ] Nombre del archivo coincide con `utm_content`
- [ ] URL añadida en primera comentario o bio
- [ ] Stories: Sticker con URL (medium=stories)
- [ ] Anotado en calendario editorial (`INSTAGRAM_CALENDAR_UTM.csv`)
- [ ] Captura de pantalla guardada para referencia

---

## 📚 Referencias

- **Guía unificada (todas las plataformas)**: [`UNIFIED_TEMPLATE_TRACKING.md`](./UNIFIED_TEMPLATE_TRACKING.md) ⭐ **NUEVO**
- **Guía completa UTMs**: [`UTM_GUIDE_OUTREACH.md`](./UTM_GUIDE_OUTREACH.md)
- **Template SVG**: [`instagram_antes_despues_template.svg`](./instagram_antes_despues_template.svg)
- **Helper script (unificado)**: [`IG_TEMPLATE_UTM_HELPER.js`](./IG_TEMPLATE_UTM_HELPER.js) - Soporta Instagram, LinkedIn, Webinar
- **Calendario maestro**: [`TEMPLATES_MASTER_CALENDAR.csv`](./TEMPLATES_MASTER_CALENDAR.csv) ⭐ **NUEVO**
- **Calendario IG específico**: [`INSTAGRAM_CALENDAR_UTM.csv`](./INSTAGRAM_CALENDAR_UTM.csv)

---

## 🐛 Troubleshooting

### Problema: URL no funciona al hacer clic
- ✅ Verificar que no haya espacios en la URL
- ✅ Comprobar que todos los parámetros UTMs están presentes
- ✅ Testear URL manualmente en navegador

### Problema: No aparecen datos en GA4
- ✅ Verificar que `utm_capture.js` está instalado en el sitio
- ✅ Revisar que la landing page tiene GA4 configurado
- ✅ Esperar 24-48h para que aparezcan datos

### Problema: UTMs no llegan al CRM
- ✅ Verificar campos UTM creados en CRM
- ✅ Revisar que `utm_capture.js` llena inputs ocultos
- ✅ Comprobar que formulario envía campos ocultos

---

**¡Listo! 🎉 Ahora puedes trackear efectivamente cada post de Instagram.**

