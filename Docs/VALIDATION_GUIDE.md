# 🔍 Guía de Validación de Assets

Guía completa para validar la calidad e integridad de todos los assets generados.

## Herramientas de Validación

### 1. Health Check Completo

Verificación rápida del estado general del sistema:

```bash
bash tools/health_check.sh
```

**Verifica:**
- ✅ Estructura de directorios requeridos
- ✅ Configuración de tokens (valores por defecto vs. personalizados)
- ✅ SVGs vacíos o rotos
- ✅ Rutas del preview
- ✅ Dependencias instaladas (Node.js, qrcode, svgo)

**Salida:**
- `✅ Sistema saludable` - Todo está bien
- `⚠️ Se encontraron N problema(s)` - Lista de problemas y sugerencias

### 2. Validación de Integridad SVG

Análisis detallado de todos los archivos SVG:

```bash
bash tools/validate_svg_integrity.sh
```

**Verifica:**
- ❌ SVGs vacíos (0 bytes)
- ❌ SVGs sin estructura válida (`<svg>` tag)
- ⚠️ SVGs muy pequeños (< 100 bytes, probablemente rotos)
- ⚠️ SVGs sin dimensiones (viewBox o width/height)

**Salida:** `exports/svg_integrity_report.txt` con:
- Resumen: válidos vs. inválidos
- Lista detallada de problemas por archivo

### 3. Validación de Rutas del Preview

Asegura que todas las rutas referenciadas en el preview HTML existan:

```bash
node tools/validate_preview_paths.js
```

**Verifica:**
- ❌ Rutas que no existen
- ⚠️ Archivos referenciados pero vacíos

**Salida:** Lista de rutas rotas (si las hay)

### 4. Análisis Completo de Assets

Análisis estadístico y de calidad de todos los assets:

```bash
bash tools/analyze_assets.sh
```

**Analiza:**
- 📊 Cantidad de SVGs por categoría (Feed, Stories, Reels, etc.)
- 💾 Tamaño total de SVGs y PNGs
- 🔑 Estado de tokens (aplicados vs. sin aplicar)
- 🖼️ Placeholders de logo pendientes
- ⚠️ SVGs vacíos detectados
- ⚠️ Rutas rotas en preview
- 📱 Assets con QR placeholder
- 📐 Assets con safe area

**Salida:** `exports/assets_report.txt`

### 5. Reparación de SVGs Rotos

Herramienta interactiva para limpiar SVGs vacíos:

```bash
bash tools/fix_broken_svgs.sh
```

**Acciones:**
- Lista todos los SVGs vacíos encontrados
- Pregunta si desea eliminarlos
- Elimina solo los confirmados

## Flujo de Validación Recomendado

### Antes de un Build

```bash
# 1. Health check rápido
bash tools/health_check.sh

# 2. Si hay problemas, validar integridad SVG
bash tools/validate_svg_integrity.sh

# 3. Reparar SVGs rotos si es necesario
bash tools/fix_broken_svgs.sh
```

### Después de un Build

```bash
# 1. Validar rutas del preview
node tools/validate_preview_paths.js

# 2. Análisis completo
bash tools/analyze_assets.sh

# 3. Revisar reportes
cat exports/assets_report.txt
cat exports/svg_integrity_report.txt
```

### Validación Continua (CI/CD)

```bash
# Validación estricta (falla si hay errores)
bash tools/health_check.sh && \
bash tools/validate_svg_integrity.sh && \
node tools/validate_preview_paths.js
```

## Checklist de Calidad

Usa este checklist manual además de las herramientas automáticas:

- [ ] **Tokens aplicados**: No quedan `{{TOKEN}}` en los SVG
- [ ] **Logos reemplazados**: No quedan placeholders `LOGO`
- [ ] **QR generado**: El QR code existe y es válido
- [ ] **Dimensiones correctas**: Todos los SVG tienen viewBox/width/height correctos
- [ ] **Safe areas**: Assets para Stories/Reels tienen guías de safe area
- [ ] **Contraste**: Texto legible sobre fondos (verificar con `qa_checklist.md`)
- [ ] **Accesibilidad**: Todos los SVG tienen `aria-label` y `title`
- [ ] **PNG exportados**: Todos los SVG tienen PNG 1x y 2x correspondientes
- [ ] **Optimización**: SVGs optimizados con SVGO
- [ ] **Rutas válidas**: Preview funciona sin errores 404

## Interpretación de Resultados

### Health Check

- **✅ Sistema saludable**: Todo listo para build
- **⚠️ Problemas detectados**: Revisar antes de build (no bloqueante)
- **❌ Errores críticos**: Deben resolverse antes de continuar

### Integridad SVG

- **Válidos: 100%**: Todos los SVG están bien
- **Inválidos > 0**: Revisar lista y reparar con `fix_broken_svgs.sh`

### Análisis de Assets

- **Tokens sin aplicar**: Ejecutar `node tools/apply_tokens.js`
- **SVGs vacíos**: Ejecutar `bash tools/fix_broken_svgs.sh`
- **Rutas rotas**: Actualizar `exports/preview/index.html` o regenerar assets

## Troubleshooting

### "Sistema no saludable"

1. Revisa los errores listados en la salida
2. Ejecuta las herramientas sugeridas
3. Consulta los reportes generados
4. Vuelve a ejecutar el health check

### "SVG vacío detectado"

1. Ejecuta `bash tools/validate_svg_integrity.sh` para ver detalles
2. Revisa si el archivo es necesario
3. Si no, elimínalo con `bash tools/fix_broken_svgs.sh`
4. Si sí, restáuralo desde git o regenéralo

### "Rutas rotas en preview"

1. Ejecuta `node tools/validate_preview_paths.js` para ver la lista
2. Verifica que los assets existan en las rutas esperadas
3. Si el preview está desactualizado, regenera con `node tools/auto_update_preview.js`
4. Si los assets no existen, regenera con `bash tools/build_all_platforms.sh`

---

**Integración en build automático:**

El script `build_all_platforms.sh` ejecuta un health check opcional al inicio. Los errores no bloquean el build, pero se muestran como advertencias.


