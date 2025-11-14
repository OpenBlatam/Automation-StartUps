# Template Video 15s — Antes/Después (1080×1920)

> Uso: Adaptación directa desde `webinar-preroll-compare.svg` y ads 1200×627 → 1080×1920.

---

## Objetivo
- Mostrar transformación rápida (antes → después) con métrica clara y CTA.
- Ideal para: Curso IA + Webinars, SaaS IA Marketing.

## Estructura narrativa (30fps)
- 00:00–02:00: Hook visual — “Antes” (pantalla gris, UI lenta)
- 02:00–06:00: “Después” (UI rápida + highlight de beneficio)
- 06:00–10:00: Métrica clave y prueba social
- 10:00–13:00: Demonstra UI en vivo (microflujo)
- 13:00–15:00: CTA final + slogan + logo

## Timecode + On-screen + VO
- 00:00–02:00
  - On-screen: “ANTES” (bajo contraste)
  - SFX: whoosh sutil
  - VO: “¿Tardas horas en…”
- 02:00–06:00
  - On-screen: “DESPUÉS” (alto contraste)
  - Motion: wipe diagonal + blur-out
  - VO: “…pásalo a minutos”
- 06:00–10:00
  - On-screen: “-60% tiempo | +ROI” (o “+27% leads”)
  - Motion: counter ease-out (0.4s)
  - VO: “Resultados medibles desde el día uno”
- 10:00–13:00
  - On-screen: “Brief → Creativos → Publicado”
  - B-roll: pantalla llenándose en 3 pasos
  - VO: “Del brief a campañas listas”
- 13:00–15:00
  - On-screen: “[ESLOGAN]” + CTA “Compra ahora / Probar gratis”
  - Motion: pulso 1.05x cada 45f

## Guía visual (layout)
- Safe zones: 150px top/bottom libres
- Headline zone: y=420–720
- Métrica: y=900–1080
- CTA: y=1700, ancho 560–680px

## AE: Expresiones útiles
- Counter (0→X): ver `ANUNCIO_VIDEO_EXPRESIONES_AFTER_EFFECTS.md` (contador y easing)
- Pulse CTA: escala 100%→105%→100% cada 45f
- Slide-up + fade: posición y opacidad linkeadas a slider global

## Assets requeridos
- SVG base: `webinar-preroll-compare.svg` o `ad_*_1200x627_metrics.svg`
- Logo (`/assets/branding/logo.svg`)
- Paleta: `ANUNCIO_VIDEO_PALETA_BRANDING.json`
- SFX whoosh corto, bed musical neutro 100–110 BPM

## Markers CSV (ejemplo)
```
label,time
ANTES,00:00:00:00
DESPUES,00:00:00:60
METRICA,00:00:00:180
MICROFLUJO,00:00:00:300
CTA,00:00:00:390
```

## Especificaciones de exportación
- 1080×1920, 15s, H.264, High, 12–16 Mbps
- Audio -14 LUFS, peak -1 dBFS, 48 kHz
- Subtítulos: SRT quemado o adjunto

## Variantes rápidas
- Hook 1: “Antes: caos → Después: control”
- Hook 2: “Manual → Automático”
- Hook 3: “Horas → Minutos”

---

## Checklist
- Texto ≤ 20% altura total
- Contraste CTA ≥ 4.5:1
- Logo visible 2+ segundos finales
- UTM en descripción (utm_medium=video)

