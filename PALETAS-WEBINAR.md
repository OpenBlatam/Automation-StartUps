# Paletas de Colores - Anuncios Webinar

## Paletas disponibles

### 1. Navy + Teal (Dark Pro) ⭐ Recomendado
**Archivo:** `webinar-preroll-dark-pro.svg`
- Fondo: `#0B1229` → `#10314A`
- CTA: `#00E5A8` → `#00B4D8`
- Texto: `#FFFFFF` / `#BFEFE8`
- **Uso:** Versátil, alto contraste, profesional

### 2. Light Blue (Light Pro) ⭐ Recomendado
**Archivo:** `webinar-preroll-light-pro.svg`
- Fondo: `#F7FAFF` → `#ECF3FF`
- CTA: `#2F57E5` → `#6A8CFF`
- Texto: `#0B1229` / `#34405B`
- **Uso:** Corporativo, limpio, legible

### 3. Magenta + Purple
**Archivo:** `webinar-preroll-magenta-purple.svg`
- Fondo: `#160027` → `#1C255A`
- CTA: `#FF3CAC` → `#784BA0`
- Texto: `#FFE9F6` / `#F9BEE3`
- **Uso:** Creativo, tech, SaaS

### 4. Emerald + Lime
**Archivo:** `webinar-preroll-emerald-lime.svg`
- Fondo: `#071A14` → `#0E2A1F`
- CTA: `#34D399` → `#10B981`
- Texto: `#EFFFF8` / `#CFFAE6`
- **Uso:** Sostenible, crecimiento, verde

### 5. Onyx + Neon
**Archivo:** `webinar-preroll-onyx-neon.svg`
- Fondo: `#0A0A0A` → `#151515`
- CTA: `#39FF14` → `#00FFA3`
- Texto: `#F5FFF7` / `#CFFDE1`
- **Uso:** Tech, futurista, disruptivo

## Matriz de decisión

| Paleta | Contraste | Profesional | Creativo | Tech |
|--------|-----------|-------------|----------|------|
| Navy+Teal | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐⭐ |
| Light Blue | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐ | ⭐⭐⭐ |
| Magenta+Purple | ⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ |
| Emerald+Lime | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐ |
| Onyx+Neon | ⭐⭐⭐⭐⭐ | ⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ |

## Accesibilidad (WCAG AA)

Todas las paletas cumplen con:
- ✅ Contraste texto/fondo ≥ 4.5:1
- ✅ Contraste CTA ≥ 3:1
- ✅ Texto legible en todos los tamaños

## Personalización rápida

Para cambiar colores en cualquier SVG:

1. Busca `<linearGradient id="bg">` para fondo
2. Busca `<linearGradient id="accent">` para CTA
3. Reemplaza los valores `stop-color`
4. Ajusta colores de texto (`fill`) según nuevo fondo

## Ejemplo de cambio rápido

```svg
<!-- Cambiar fondo a negro puro -->
<linearGradient id="bg" x1="0" y1="0" x2="1" y2="1">
  <stop offset="0%" stop-color="#000000"/>
  <stop offset="100%" stop-color="#0A0A0A"/>
</linearGradient>

<!-- Cambiar CTA a rojo -->
<linearGradient id="accent" x1="0" y1="0" x2="1" y2="0">
  <stop offset="0%" stop-color="#FF3B3B"/>
  <stop offset="100%" stop-color="#FF7A59"/>
</linearGradient>
```



