# Guía de Exportación: SVG → PNG/PDF para LinkedIn Ads Manager

## Requisitos de formato LinkedIn

| Tipo de Anuncio | Dimensiones (px) | Formato | Peso máximo |
|----------------|------------------|---------|-------------|
| **Feed Single Image** | 1200×627 | JPG/PNG | 5 MB |
| **Feed Square** | 1080×1080 | JPG/PNG | 5 MB |
| **Feed Carousel** | 1080×1080 (por slide) | JPG/PNG | 5 MB por slide |
| **Stories** | 1080×1920 | JPG/PNG | 10 MB |

## Exportar SVG a PNG

### Opción 1: Inkscape (Gratis, Multiplataforma)
```bash
# Instalar Inkscape
# macOS: brew install inkscape
# Windows: Descargar desde inkscape.org
# Linux: sudo apt install inkscape

# Exportar SVG a PNG (1200×627)
inkscape --export-filename=ad_curso_ia_1200x627.png --export-width=1200 --export-height=627 ad_curso_ia_1200x627.svg

# Exportar SVG a PNG (1080×1080)
inkscape --export-filename=ad_curso_ia_1080x1080.png --export-width=1080 --export-height=1080 ad_curso_ia_1080x1080.svg

# Exportar SVG a PNG (1080×1920)
inkscape --export-filename=ad_curso_ia_1080x1920.png --export-width=1080 --export-height=1920 ad_curso_ia_1080x1920.svg
```

### Opción 2: Script Automático (Node.js + sharp)
```javascript
// export_svg_to_png.js
const sharp = require('sharp');
const fs = require('fs');
const path = require('path');

const sizes = [
  { name: '1200x627', width: 1200, height: 627 },
  { name: '1080x1080', width: 1080, height: 1080 },
  { name: '1080x1920', width: 1080, height: 1920 }
];

const svgFiles = fs.readdirSync('./ads/linkedin').filter(f => f.endsWith('.svg'));

svgFiles.forEach(file => {
  const svgPath = path.join('./ads/linkedin', file);
  const svgBuffer = fs.readFileSync(svgPath);
  
  sizes.forEach(size => {
    const outputPath = svgPath.replace('.svg', `_${size.name}.png`);
    sharp(svgBuffer)
      .resize(size.width, size.height)
      .png({ quality: 100 })
      .toFile(outputPath)
      .then(() => console.log(`✓ ${outputPath}`))
      .catch(err => console.error(`✗ ${outputPath}:`, err));
  });
});
```

Ejecutar:
```bash
npm install sharp
node export_svg_to_png.js
```

### Opción 3: Online (Rápido para pruebas)
- **CloudConvert**: cloudconvert.com (SVG → PNG, gratis 25 conversiones/día)
- **Convertio**: convertio.co/es (SVG → PNG)
- **Adobe Express**: express.adobe.com/tools/convert-to-png

## Exportar SVG a PDF (para impresión/documentación)

### Inkscape
```bash
inkscape --export-filename=ad_curso_ia_1200x627.pdf ad_curso_ia_1200x627.svg
```

### Script Node.js (pdfkit + svg2pdf)
```javascript
// export_svg_to_pdf.js
const { SVG } = require('@svgdotjs/svg.js');
const PDFDocument = require('pdfkit');
const fs = require('fs');

// Implementación específica según librerías disponibles
// Ejemplo conceptual:
const svg = fs.readFileSync('./ads/linkedin/ad_curso_ia_1200x627.svg', 'utf8');
// Convertir SVG a PDF usando librería apropiada
```

## Configuración de UTMs para LinkedIn Ads

### Plantilla UTM base
```
utm_source=linkedin
utm_medium=paid
utm_campaign={campaign_name}
utm_content={ad_name}
utm_term={audience_segment}
```

### Ejemplos por servicio

#### Curso de IA + Webinars
```
https://tusitio.com/curso-ia?utm_source=linkedin&utm_medium=paid&utm_campaign=curso_ia_2025q1&utm_content=ad_curso_1200x627&utm_term=dm_mid_empresas
```

#### SaaS de IA para Marketing
```
https://tusitio.com/saas-ia?utm_source=linkedin&utm_medium=paid&utm_campaign=saas_ia_2025q1&utm_content=ad_saas_1200x627&utm_term=dm_mid_empresas
```

#### IA Bulk
```
https://tusitio.com/ia-bulk?utm_source=linkedin&utm_medium=paid&utm_campaign=ia_bulk_2025q1&utm_content=ad_bulk_1200x627&utm_term=dm_mid_empresas
```

### Configurar UTMs en LinkedIn Ads Manager

1. **Crear campaña** → Nombre: `curso_ia_2025q1_linkedin`
2. **Crear anuncio** → Destino del enlace:
   - URL base: `https://tusitio.com/curso-ia`
   - Parámetros UTM: Añadir en "Parámetros de seguimiento"
     ```
     utm_source=linkedin
     utm_medium=paid
     utm_campaign={{campaign.name}}
     utm_content={{ad.name}}
     utm_term={{audience.name}}
     ```
3. **Verificar**: LinkedIn añade automáticamente `li_fat_id` para seguimiento interno.

### Captura de UTMs en tu CRM/Formulario

Asegúrate de que tus formularios capturen los parámetros UTM:
```html
<!-- Ejemplo: Campo oculto en formulario -->
<input type="hidden" name="utm_source" id="utm_source">
<input type="hidden" name="utm_medium" id="utm_medium">
<input type="hidden" name="utm_campaign" id="utm_campaign">
<input type="hidden" name="utm_content" id="utm_content">
<input type="hidden" name="utm_term" id="utm_term">

<script>
// Capturar UTMs de URL y rellenar campos ocultos
const params = new URLSearchParams(window.location.search);
['utm_source', 'utm_medium', 'utm_campaign', 'utm_content', 'utm_term'].forEach(param => {
  const value = params.get(param);
  const field = document.getElementById(param);
  if (field && value) field.value = value;
});
</script>
```

## Checklist pre-publicación

- [ ] **Imágenes exportadas** en PNG (JPG como fallback)
- [ ] **Dimensiones correctas** (1200×627, 1080×1080, 1080×1920)
- [ ] **Peso < 5 MB** por imagen (optimizar si necesario)
- [ ] **Texto legible** a tamaño reducido (mínimo 12px efectivo)
- [ ] **Colores contrastados** (WCAG AA mínimo)
- [ ] **UTMs configurados** en Ads Manager
- [ ] **Landing pages** con captura de UTMs
- [ ] **Prueba de clic** en modo preview de LinkedIn
- [ ] **A/B test** preparado (2-3 variantes por anuncio)

## Optimización de imágenes

### Reducir peso PNG (ImageOptim, TinyPNG)
```bash
# macOS: ImageOptim (GUI) o
brew install imageoptim-cli
imageoptim --directory ./ads/linkedin/*.png

# Online: TinyPNG (tinypng.com) - hasta 5MB gratis
```

### Comprimir PNG con pngquant
```bash
brew install pngquant
pngquant --quality=80-95 ad_curso_ia_1200x627.png --output ad_curso_ia_1200x627_compressed.png
```

## Organización de archivos

```
ads/linkedin/
├── svg/
│   ├── ad_curso_ia_1200x627.svg
│   ├── ad_curso_ia_1080x1080.svg
│   └── ...
├── png/
│   ├── ad_curso_ia_1200x627.png
│   ├── ad_curso_ia_1080x1080.png
│   └── ...
├── pdf/
│   ├── ad_curso_ia_1200x627.pdf
│   └── ...
└── carousel/
    ├── carousel_slide_1_hook_1080x1080.png
    ├── carousel_slide_2_curso_1080x1080.png
    └── ...
```

## Notas adicionales

- **Text overlay limit**: LinkedIn limita texto a <20% del área (feed). Usa más imágenes y menos texto.
- **Video alternativo**: Considera versiones video (MP4, 2560×1440 o 1080×1080) para mejor engagement.
- **Dynamic Ads**: Si usas Dynamic Ads, prepara templates con áreas variables para personalización automática.

## Soporte

Para dudas sobre exportación o configuración de UTMs, consultar:
- [LinkedIn Ads Specs](https://www.linkedin.com/help/linkedin/answer/a427660)
- [UTM Guide Outreach](./UTM_GUIDE_OUTREACH.md)



