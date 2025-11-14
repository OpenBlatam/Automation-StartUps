# 🚀 Quick Start: Templates LinkedIn Ads (1200×627) con UTMs

Guía rápida para usar templates de LinkedIn con tracking completo.

---

## ⚡ Setup rápido (5 minutos)

### 0. Elegir formato (dimensiones)

**LinkedIn acepta múltiples formatos**:

| Formato | Dimensiones | Mejor para | Uso en Campaign Manager |
|---------|-------------|------------|------------------------|
| Landscape | 1200×627 | Desktop, Sponsored Content | Sponsored Content (single image) |
| Cuadrado | 1080×1080 | Móvil, Feed, Carruseles | Carousel Ads, Sponsored Content |
| Vertical | 1080×1350 | Móvil, Stories | Document Ads (PDF) |

**Recomendación**: Usa landscape (1200×627) para Sponsored Content principal y cuadrado (1080×1080) para carruseles o A/B testing.

### 1. Elegir template según ángulo

**Urgencia** (`*_urgency.svg`):
- Usar cuando hay oferta/descuento limitado
- Badge rojo "Termina hoy" o similar
- CTA: "Reservar ahora", "Activar hoy"

**Prueba Social** (`*_social_proof.svg`):
- Usar para B2B/SaaS con logos de clientes
- Incluir número de usuarios/clientes
- CTA: "Probar gratis", "Ver demo"

**Métricas** (`*_metrics.svg`):
- Usar para destacar números/resultados
- ROI, tiempo ahorrado, velocidad
- CTA: "Calcular ahorro", "Ver resultados"

**V2** (`*_v2.svg`):
- Variante alternativa del diseño base
- Usar para A/B testing

### 2. Editar template SVG

**Abrir**: Template en Illustrator/Inkscape/Figma

**Buscar elementos editables**:
- Textos: `headline`, `sub`, `eyebrow`
- CTA: elemento con `cta` class o ID
- Métricas: elementos con `metric` class
- URL: elemento con `href` (línea ~770 en algunos templates)

### 3. Generar URL con UTMs

**Opción A: Helper script**
```bash
node IG_TEMPLATE_UTM_HELPER.js
# Ejemplo LinkedIn:
# generateLinkedInAdURL({
#   template: 'urgency',
#   angle: 'h1direct',
#   cta: 'reserva',
#   product: 'cursoia',
#   role: 'cmo',
#   region: 'mx'
# })
```

**Opción B: Manual**
```
https://tusitio.com/demo?
  utm_source=linkedin&
  utm_medium=cpc&
  utm_campaign=cursoia_demo_linkedin_2025-11&
  utm_content=urgency_h1direct_cta_reserva_v1&
  utm_term=cmo_mx
```

### 4. Actualizar URL en SVG

**Buscar**:
```xml
<!-- Buscar elemento con href -->
<a href="https://tu-sitio.com">
```

**Reemplazar con URL completa con UTMs**

### 5. Exportar PNG

- **Dimensiones**: 1200×627 px (exacto, LinkedIn es estricto)
- **Formato**: PNG (preferido) o JPG alta calidad
- **Nombre**: `urgency_h1direct_v1_linkedin_2025-11-30.png`

---

## 📱 Subir a LinkedIn Campaign Manager

### Pasos en LinkedIn

1. **Asset Library** → Upload nuevo asset
2. **Seleccionar archivo**: PNG 1200×627
3. **Añadir URL**: Pegar URL con UTMs completos
4. **Naming en LinkedIn**: Usar mismo `utm_content` para fácil tracking
   - Ej: `urgency_h1direct_cta_reserva_v1`

### Campaign setup

- **Campaign name**: `[producto]_demo_linkedin_[yyyy-mm]`
- **Ad name**: `[template]_[angle]_[cta]_v[n]` (coincide con `utm_content`)

---

## 📊 Tracking y reportes

### En LinkedIn Analytics
- Impressions, Clicks, CTR
- CPC, CPL (si trackeas leads)
- Engagement rate

### En GA4
1. **Adquisición** → Tráfico de adquisición
2. Filtro: `Campaign = cursoia_demo_linkedin_2025-11`
3. Ver `Ad content` = `urgency_h1direct_cta_reserva_v1`

### En CRM
- Contactos con `utm_campaign = cursoia_demo_linkedin_2025-11`
- Filtrar por `utm_content` para ver qué template convirtió mejor

---

## ✅ Checklist antes de publicar

### Validación técnica
- [ ] URL actualizada en SVG con UTMs completos
- [ ] Dimensiones exactas según formato:
  - Landscape: **1200×627 px** (exacto)
  - Cuadrado: **1080×1080 px** (exacto)
- [ ] Texto legible y CTA claro (máx 2 palabras)
- [ ] Logo visible con clearspace adecuado
- [ ] Contraste AA verificado
- [ ] Safe area respetada (texto no en bordes)

### Validación de tracking
- [ ] Nombre de archivo coincide con `utm_content`
- [ ] Ad name en LinkedIn coincide con `utm_content`
- [ ] URL testada manualmente (200 OK)
- [ ] UTMs validados (no espacios, minúsculas)

### Validación de contenido
- [ ] Sin errores ortográficos
- [ ] Métricas/claims verificables
- [ ] Brand guidelines respetadas

---

## 🔄 Workflow completo

```
1. Elegir template (urgency/social_proof/metrics) →
2. Editar SVG (texto/CTA) →
3. Generar URL con UTMs →
4. Actualizar URL en SVG →
5. Exportar 1200×627 PNG →
6. Subir a LinkedIn →
7. Trackear en GA4/CRM
```

---

## 🎯 A/B Testing recomendado

**Test 1**: Urgencia vs Social Proof
- Urgencia: `urgency_h1direct_cta_reserva_v1`
- Social Proof: `social_proof_beneficio_cta_demo_v1`
- Comparar: CTR, CVR, CPL

**Test 2**: Métricas vs Urgencia
- Métricas: `metrics_roi_v1`
- Urgencia: `urgency_h1direct_v1`
- Comparar: Clicks, Leads, CPC

**Regla**: ≥200 clics por variante antes de decidir ganador.

---

## 📚 Referencias

- **Guía unificada**: [`UNIFIED_TEMPLATE_TRACKING.md`](./UNIFIED_TEMPLATE_TRACKING.md)
- **Helper Script**: [`IG_TEMPLATE_UTM_HELPER.js`](./IG_TEMPLATE_UTM_HELPER.js)
- **Guía UTMs**: [`UTM_GUIDE_OUTREACH.md`](./UTM_GUIDE_OUTREACH.md)
- **Calendario maestro**: [`TEMPLATES_MASTER_CALENDAR.csv`](./TEMPLATES_MASTER_CALENDAR.csv)

---

## 🐛 Troubleshooting LinkedIn

### Problema: Ad rechazado por dimensiones
- ✅ Verificar exactamente 1200×627 px (no 1201×628)
- ✅ Exportar desde SVG sin escalar
- ✅ Revisar que viewBox esté correcto

### Problema: URL no clickeable en ad
- ✅ Verificar que URL está completa en Asset Library
- ✅ Comprobar que no hay caracteres especiales sin encoding
- ✅ Testear URL manualmente antes de subir

### Problema: No aparecen datos en GA4
- ✅ Verificar que `utm_capture.js` está en landing page
- ✅ Esperar 24-48h para datos
- ✅ Revisar filtros en GA4 (puede que necesites remover algunos)

---

**¡Listo! 🎉 Ahora puedes trackear efectivamente cada ad de LinkedIn.**

