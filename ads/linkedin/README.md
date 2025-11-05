# 📢 Anuncios LinkedIn - Kit Completo

Kit completo de anuncios para LinkedIn Ads Manager con **44 archivos SVG optimizados** en múltiples formatos y variantes.

## 🎯 Servicios Incluidos

1. **Curso de IA + Webinars** - Formación aplicada para marketing
2. **SaaS de IA para Marketing** - Automatización con datos propios
3. **IA Bulk** - Generación de 3 documentos con 1 consulta

## 📐 Formatos Disponibles

### Feed Principal (1200×627)
- ✅ Versiones base
- ✅ Versiones v2 (mejoradas)
- ✅ Versiones con métricas
- ✅ Versiones fondo claro (light)
- ✅ Versiones con prueba social
- ✅ Versiones con urgencia/performance

### Feed Cuadrado (1080×1080)
- ✅ Versiones principales
- ✅ Versiones con métricas
- ✅ Carrusel completo (5 slides)

### Stories/Móvil (1080×1920)
- ✅ Versiones principales
- ✅ Versiones con métricas

## 🚀 Inicio Rápido

### 1. Exportar SVGs a PNG

```bash
# Dar permisos de ejecución
chmod +x export_svg_to_png.sh

# Ejecutar script de exportación
./export_svg_to_png.sh
```

Los PNGs se generarán en `png_exports/` organizados por formato.

### 2. Revisar Copy y Variantes

Consulta `copy_variantes.md` para:
- Titulares A/B testing
- CTAs por etapa del funnel (TOFU/MOFU/BOFU)
- Variantes por audiencia

### 3. Configurar UTMs

Sigue `GUIA_EXPORTACION_ADS.md` para:
- Exportar SVG → PNG
- Configurar parámetros UTM
- Subir a LinkedIn Ads Manager

## 📁 Estructura de Archivos

```
ads/linkedin/
├── ad_*_1200x627*.svg          # Feed principal
├── ad_*_1080x1080*.svg          # Feed cuadrado
├── ad_*_1080x1920*.svg          # Stories
├── carousel_slide_*.svg         # Carrusel (5 slides)
├── copy_variantes.md            # Titulares y CTAs
├── GUIA_EXPORTACION_ADS.md      # Guía de exportación
├── INDEX_ASSETS.md              # Índice completo
├── MEJORAS_APLICADAS.md         # Mejoras implementadas
└── export_svg_to_png.sh         # Script de exportación
```

## ✨ Características de Diseño

### Estilo Visual
- 🎨 Colores: Azul/Gris corporativo
- 📊 Iconografía: Crecimiento/gráficos minimalistas
- 🔤 Tipografía: Inter/Arial (bold para headlines)
- 🎯 Estilo: Minimalista, corporativo, profesional

### Elementos Incluidos
- ✅ Headlines con "Mejora tu ROI en +20%" (acento destacado)
- ✅ Métricas destacadas (+27% leads, -32% CPA)
- ✅ Testimonios con comillas decorativas
- ✅ CTAs mejorados con sombras y flechas
- ✅ Filtros SVG para profundidad visual
- ✅ Badges de valor y urgencia
- ✅ Eyebrow text para categorización

## 🔧 Requisitos

### Para Exportar a PNG:
- **Inkscape** (gratis, multiplataforma)
  - macOS: `brew install inkscape`
  - Windows: [Descargar desde inkscape.org](https://inkscape.org/release/)
  - Linux: `sudo apt install inkscape`

### Alternativa (Sin Inkscape):
- Abrir SVG en navegador
- Exportar como PNG con herramientas de desarrollo
- O usar herramientas online (SVGtoPNG, CloudConvert)

## 📊 Matriz de Uso Recomendado

| Formato | Uso | Archivos Clave |
|---------|-----|----------------|
| **1200×627** | Feed principal LinkedIn | `*_v2.svg` o `*_metrics.svg` |
| **1080×1080** | Feed cuadrado, carrusel | `carousel_slide_*.svg` |
| **1080×1920** | Stories, móvil vertical | `*_1080x1920.svg` |
| **Light** | Tests A/B (fondo claro) | `*_light.svg` |
| **Metrics** | Audiencias performance | `*_metrics.svg` |
| **Social Proof** | Prueba social | `*_social_proof.svg` |
| **Urgency** | Ofertas limitadas | `*_urgency.svg` |

## 🎯 Flujo de Trabajo

### 1. Preparación
1. Revisar `copy_variantes.md` para seleccionar titulares/CTAs
2. Elegir formato según objetivo (feed/carrusel/stories)
3. Seleccionar variante (base/metrics/light/social_proof/urgency)

### 2. Personalización (Opcional)
1. Integrar logo propio (reemplazar placeholder "Marca/Logo")
2. Ajustar colores si necesario
3. Validar texto según audiencia (ES/MX/AR)

### 3. Exportación
1. Ejecutar `./export_svg_to_png.sh`
2. Revisar PNGs en `png_exports/`
3. Verificar tamaños (< 5 MB)

### 4. Configuración Ads Manager
1. Subir imágenes a LinkedIn Ads Manager
2. Configurar UTMs según `GUIA_EXPORTACION_ADS.md`
3. Configurar carrusel (si aplica) con 5 slides en orden

### 5. Testing
1. A/B test: Base vs Metrics vs Light
2. Monitorear CTR, conversión por formato
3. Iterar según resultados

## 📝 Notas Importantes

- Todos los archivos están en formato **SVG** para escalabilidad
- **Exportar a PNG** antes de subir a LinkedIn Ads Manager
- **Revisar pesos** de archivos (< 5 MB recomendado)
- **Mantener consistencia** visual entre variantes
- Los logos son placeholders: reemplazar con logo real

## 🔄 Actualizaciones

- **Última actualización**: 2025-01-XX
- **Total assets**: 44 archivos SVG + documentación
- **Mejoras aplicadas**: Ver `MEJORAS_APLICADAS.md`

## 📚 Documentación Adicional

- `copy_variantes.md` - Titulares A/B y CTAs por funnel
- `GUIA_EXPORTACION_ADS.md` - Instrucciones SVG → PNG + UTMs
- `INDEX_ASSETS.md` - Índice completo de archivos
- `MEJORAS_APLICADAS.md` - Detalles de mejoras implementadas

## 🤝 Soporte

Para preguntas o mejoras, consulta la documentación incluida o revisa los comentarios en los archivos SVG.

---

**¿Listo para empezar?** Ejecuta `./export_svg_to_png.sh` y sube los PNGs a LinkedIn Ads Manager! 🚀


