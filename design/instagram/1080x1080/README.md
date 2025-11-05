# Artes Instagram 1080x1080 — 35% OFF (48h)

Archivos SVG:
- ig_descuento_curso_ia.svg
- ig_descuento_saas_marketing.svg
- ig_descuento_ia_bulk.svg
 - ../1080x1920/ig_story_descuento_curso_ia.svg
 - ../1080x1920/ig_story_descuento_saas_marketing.svg
 - ../1080x1920/ig_story_descuento_ia_bulk.svg
 - ../reels/cover_1080x1920/cover_reel_curso_ia.svg
 - ../reels/cover_1080x1920/cover_reel_saas_marketing.svg
 - ../reels/cover_1080x1920/cover_reel_ia_bulk.svg
 - carousel/carousel_slide1_hook.svg
 - carousel/carousel_slide2_benefits.svg
 - carousel/carousel_slide3_cta.svg
 - ig_descuento_curso_ia_dark.svg
 - ig_descuento_saas_marketing_dark.svg
 - ig_descuento_ia_bulk_dark.svg
 - ../1080x1920/ig_story_descuento_curso_ia_dark.svg
 - ../1080x1920/ig_story_descuento_saas_marketing_dark.svg
 - ../1080x1920/ig_story_descuento_ia_bulk_dark.svg
 - ig_descuento_curso_ia_ab.svg
 - ig_descuento_saas_marketing_ab.svg
 - ig_descuento_ia_bulk_ab.svg
 - ig_descuento_curso_ia_ultimas24.svg
 - ig_descuento_saas_marketing_ultimas24.svg
 - ig_descuento_ia_bulk_ultimas24.svg
 - ../highlights/cover_descuento.svg
 - ../highlights/cover_48h.svg
 - ../highlights/cover_ia.svg
 - ../highlights/cover_marketing.svg

Editar:
- Logo (arriba derecha): reemplaza el círculo y texto "LOGO" por tu logotipo (72x72 px aprox).
- Título/subcopy: edita los textos según tu marca.
- Descuento y CTA: "-35 %" y "Aprovecha hoy" pueden ajustarse con font-size.
- Colores: cambia stop-color en <linearGradient>.
 - Cupón: busca el grupo "Cupón" y cambia el texto (ej: "CUPÓN: 35IA").
 - QR: reemplaza el placeholder dentro del grupo "QR" por tu código (SVG/PNG cuadrado).

Exportar a PNG:
- Abre el SVG en Figma/Illustrator y exporta a 1080x1080 PNG.
- Recomendado: exporta también @2x (2160x2160) para mayor nitidez.
 - Script (requiere Inkscape o rsvg-convert):
   - macOS/Linux: `bash tools/export_png.sh`
   - Salida: `exports/png/1x` y `exports/png/2x`

QR, optimización y paquete final:
- Generar QR (requiere Node y paquete `qrcode`):
  - `npm install qrcode`
  - `node tools/generate_qr.js`
- Optimizar SVG (requiere `svgo`): `bash tools/optimize_svg.sh`
- Empaquetar todo en ZIP: `bash tools/package_assets.sh`

Stories (1080×1920):
- Reels (portadas 1080×1920):
- Usa las portadas en `reels/cover_1080x1920`.
- Ten en cuenta el recorte a 1080×1080 en la grilla. Activa el grupo `grid-safe` (rectángulo centrado) para no cortar textos clave.

Carrusel (1080×1080):
Tokens y reemplazo masivo:
- Edita `design/instagram/tokens.json` con tu `url`, `handle`, `coupon` y `cta`.
- Ejecuta el script para aplicar cambios a todos los SVG:
  - macOS/Linux:
    - `node tools/apply_tokens.js --dry` (vista previa)
    - `node tools/apply_tokens.js` (aplicar)
  - Windows:
    - `node tools\\apply_tokens.js --dry`
    - `node tools\\apply_tokens.js`
- El script reemplaza: `tu-sitio.com`, `@tu_marca`, `CUPÓN: 35IA`, `Aprovecha hoy`.

Tema de marca (colores):
- Define `brandColors` en `design/instagram/tokens.json`.
- Aplica el tema en todos los SVG: `node tools/apply_theme.js`

Generador de variantes (descuento/urgencia):
- Usa `tools/generate_variants.js` para crear variantes desde los SVG base del feed.
- Ejemplos:
  - `node tools/generate_variants.js --perc=25,40,50`
  - `node tools/generate_variants.js --urg="Solo 48 horas,Últimas 24 horas,Termina hoy"`
  - `node tools/generate_variants.js --perc=30 --targets=ig_descuento_curso_ia.svg`
- Los archivos se guardan en `1080x1080/variants/` con sufijos `_XXpct_urgencia.svg`.
- Consejo: combina con `apply_tokens.js` para preparar lotes por país/idioma.

UTM:
- Construir y aplicar UTM a `tokens.json`:
  - `node tools/build_utm_url.js --source=instagram --medium=social --campaign=35IA_48h --content=feed --apply`
  - Luego ejecuta `node tools/generate_qr.js` para actualizar QR.
 - Presets por mercado (ES/EN/PT):
   - Edita `design/instagram/utm_presets.json` si hace falta.
   - Aplica: `node tools/apply_market_utm.js es` (o en/pt) y luego `node tools/generate_qr.js`.

Preview web:
- Abre `exports/preview/index.html` para revisar todas las piezas rápidamente.

Calendario de publicación:
- Ver `design/instagram/calendar/post_calendar.csv` y ajusta fechas/horas según tu audiencia.

Tamaños Ads extra:
- Feed vertical 1080×1350 (ratio 4:5) en `design/instagram/1080x1350/`:
  - `ig_ads_curso_ia.svg`
  - `ig_ads_saas_marketing.svg`
  - `ig_ads_ia_bulk.svg`
- Versiones low-text (<20% texto para Ads Manager) en `1080x1080/`:
  - `ig_descuento_curso_ia_lowtext.svg`
  - `ig_descuento_saas_marketing_lowtext.svg`
  - `ig_descuento_ia_bulk_lowtext.svg`
  - Estas versiones cumplen con el límite de texto de Instagram Ads Manager y mejoran el alcance.

Tipografía:
- Inter / system-ui / -apple-system / Segoe UI / Roboto / Arial.

Notas:
- Mantener alto contraste entre fondo y texto.
- Personalizar URL/handle en el pie.
 - Dark mode: usa las variantes *_dark.svg en entornos con fondos oscuros o para variar la grilla.
 - A/B testing: publica las variantes *_ab.svg a una parte de la audiencia y compara CTR/Swipe-ups/Guardados.
 - Highlights: usa las portadas en `highlights/` y recuerda que Instagram las recorta en un círculo; manten contenido centrado.
 - Copys sugeridos: ver `../copys/copys_instagram_promos.md` para hooks, CTA y hashtags.
 - Accesibilidad: ver `../accessibility/alt_text.csv` para textos alternativos por asset.
 - QA previo a publicar: ver `../qa/qa_checklist.md`.
