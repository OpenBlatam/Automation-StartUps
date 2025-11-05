### Checklist de QA — Anuncios Instagram 35% OFF

Contraste y legibilidad
- Verifica contraste AA entre texto y fondo (especialmente “-35 %” y CTA).
- Comprueba tamaños mínimos: título ≥ 48 px, CTA ≥ 36 px.

Safe area y recortes
- Feed 1080×1080: mantener elementos clave dentro de 60 px del borde.
- Stories 1080×1920: activa `safe-area` y respeta 250 px superior/inferior.
- Reels cover: asegúrate que el `grid-safe` no corte titulares en la grilla.

Consistencia visual
- Logo en esquina superior derecha, margen uniforme.
- Alineación y espaciado consistentes entre las tres piezas.

Contenido y copy
- “Solo 48 horas”/“Últimas 24 horas” correcto según variante.
- CTA y cupón visibles y sin solaparse.
- URL/handle correcto (tokens aplicados).

Accesibilidad
- Alt text asignado (ver `accessibility/alt_text.csv`).
- Títulos/aria-label presentes en SVG donde aplique.

Exportación
- Exportar PNG 1x (1080) y 2x (2160), sin artefactos.
- Peso razonable (usar `optimize_svg.sh` y revisar PNG si es necesario).



