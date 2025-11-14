# Storyboard Video 15s — IA Bulk Documentos (1080×1920)

> Uso: Adaptación desde `ad_ia_bulk_1080x1920.svg` con animación de contador y grid.

---

## Objetivo
- Mostrar escala: de 1 consulta → 100+ documentos generados.
- Subrayar “un clic” y export masivo.

## Versión recomendada: Counter (V1)

### Estructura (30fps)
- 00:00–02:00: Hook — “1 → 100” (counter grande)
- 02:00–06:00: Grid documentos llenándose (10×)
- 06:00–10:00: Export masivo (iconos: PDF/Doc/Drive)
- 10:00–13:00: Casos de uso (contratos, briefs, informes)
- 13:00–15:00: CTA “Prueba ahora” + slogan + logo

### Timecode + On-screen + VO
- 00:00–02:00: “De 1 a 100 documentos” — VO: “De una consulta a cientos de documentos”
- 02:00–06:00: “Lotes automáticos” — VO: “Genera en lote, sin esfuerzo”
- 06:00–10:00: “Exporta a PDF, Doc, Drive” — VO: “Exporta en un clic”
- 10:00–13:00: “Casos: legal, marketing, ops” — VO: “Listo para tus procesos”
- 13:00–15:00: “[ESLOGAN]” + CTA — VO: “[ESLOGAN]”

### Motion/AE
- Counter: easeOutExpo, 0→100 en 24f, con blur sutil al inicio
- Grid fill: stagger por filas, 2f de delay
- Icon sweep: path animation 18f
- CTA pulse: 1.05x cada 45f

### Assets
- SVG base: `ad_ia_bulk_1080x1920.svg` (o 1200×627 adaptado)
- Iconos export: pdf.svg, doc.svg, drive.svg
- Paleta oscura: `ANUNCIO_VIDEO_PALETA_BRANDING.json` (colors.900)

### Markers CSV
```
label,time
COUNTER,00:00:00:00
GRID,00:00:00:60
EXPORT,00:00:00:180
USE_CASES,00:00:00:300
CTA,00:00:00:390
```

### Export
- 1080×1920, 15s, H.264, 12–16 Mbps
- Audio -14 LUFS, SRT opcional

### Variantes rápidas
- Operativa B2B (V2): énfasis en integraciones y QA
- UGC (V3): testimonio + pantalla real

---

## Checklist
- Safe zone respetada (150px)
- CTA alto contraste
- Logos integraciones con permisos de marca

