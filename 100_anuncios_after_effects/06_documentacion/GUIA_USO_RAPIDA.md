# 🚀 Guía de Uso Rápida - 100 Anuncios After Effects

> Guía rápida para crear y exportar 100 anuncios en After Effects

---

## ⚡ Inicio Rápido (10 minutos) - Versión 2.0 Mejorada

### Paso 1: Preparar After Effects

1. Abrir Adobe After Effects
2. Crear nuevo proyecto: `File > New > New Project`
3. Guardar proyecto: `File > Save As...` → `100_anuncios_after_effects.aep`

### Paso 2: Ejecutar Script de Creación

1. Ir a: `File > Scripts > Run Script File...`
2. Seleccionar: `02_scripts/bulk_create_ads.jsx`
3. Esperar confirmación: "✅ Creadas 100 composiciones exitosamente!"

### Paso 3: Aplicar Variaciones

1. Ir a: `File > Scripts > Run Script File...`
2. Seleccionar: `02_scripts/apply_variations.jsx`
3. Esperar confirmación: "✅ Aplicadas variaciones..."

### Paso 4: Aplicar CTAs (NUEVO v2.0)

1. Ir a: `File > Scripts > Run Script File...`
2. Seleccionar: `02_scripts/apply_cta_templates.jsx`
3. Esperar confirmación: "✅ Aplicadas plantillas de CTA!"

### Paso 5: Añadir Animaciones Avanzadas (NUEVO v2.0)

1. Ir a: `File > Scripts > Run Script File...`
2. Seleccionar: `02_scripts/advanced_animations.jsx`
3. Esperar confirmación: "✅ Aplicadas animaciones avanzadas!"

### Paso 6: Añadir Logo (NUEVO v2.0)

1. Ir a: `File > Scripts > Run Script File...`
2. Seleccionar: `02_scripts/add_logo_batch.jsx`
3. Seleccionar archivo de logo cuando se solicite
4. Esperar confirmación

### Paso 7: Añadir Música (NUEVO v2.0)

1. Ir a: `File > Scripts > Run Script File...`
2. Seleccionar: `02_scripts/add_music_batch.jsx`
3. Seleccionar archivo de música cuando se solicite
4. Esperar confirmación

### Paso 8: Personalizar Textos

1. Editar: `02_scripts/replace_text.jsx`
2. Cambiar valores en objeto `replacements`
3. Ejecutar: `File > Scripts > Run Script File...`
4. Seleccionar: `02_scripts/replace_text.jsx`

### Paso 9: QA y Optimización (NUEVO v2.0)

1. **Quality Check:**
   - `File > Scripts > Run Script File...`
   - Seleccionar: `02_scripts/quality_check.jsx`
   - Revisar reporte generado

2. **Optimización:**
   - `File > Scripts > Run Script File...`
   - Seleccionar: `02_scripts/optimize_project.jsx`
   - Revisar optimizaciones aplicadas

### Paso 10: Exportar Masivamente

1. Editar ruta en: `02_scripts/batch_export.jsx`
2. Ir a: `File > Scripts > Run Script File...`
3. Seleccionar: `02_scripts/batch_export.jsx`
4. Confirmar inicio de render
5. Esperar a que termine (puede tardar varias horas)

---

## 📋 Checklist Pre-Export

Antes de exportar, verificar:

- [ ] 100 composiciones creadas
- [ ] Textos personalizados con valores reales
- [ ] Colores de marca aplicados
- [ ] Logo añadido (si aplica)
- [ ] Música sincronizada (si aplica)
- [ ] CTAs visibles y legibles
- [ ] Ruta de exportación correcta

---

## 🎨 Personalización Manual

### Añadir Logo

1. Importar logo: `File > Import > File...`
2. Arrastrar a composición
3. Posicionar y escalar
4. Añadir fade in si es necesario

### Añadir Música

1. Importar música: `File > Import > File...`
2. Arrastrar a composición
3. Ajustar volumen: `Layer > Audio > Audio Levels`
4. Aplicar ducking si hay VO

### Personalizar Anuncios Individuales

1. Abrir composición específica
2. Seguir guía paso a paso del documento principal
3. Aplicar animaciones personalizadas
4. Ajustar timing según necesidad

---

## 🔧 Solución de Problemas

### Error: "Script no se ejecuta"

**Solución:**
- Verificar que ExtendScript Toolkit esté instalado
- Habilitar scripts: `Edit > Preferences > Scripting & Expressions > Allow Scripts to Write Files`

### Error: "No se encuentran composiciones"

**Solución:**
- Verificar que las composiciones tengan nombres que empiecen con "Comp_"
- Ejecutar primero `bulk_create_ads.jsx`

### Error: "Ruta de exportación no válida"

**Solución:**
- Editar `batch_export.jsx`
- Cambiar `baseOutputPath` a una ruta válida en tu sistema
- Crear la carpeta manualmente si no existe

### Render muy lento

**Solución:**
- Reducir calidad temporalmente para pruebas
- Usar Media Encoder para render más eficiente
- Renderizar en lotes pequeños (10-20 a la vez)

---

## 📊 Estructura de Archivos Generados

Después de exportar, tendrás:

```
/05_exports/mp4/
  anuncio_001.mp4
  anuncio_002.mp4
  anuncio_003.mp4
  ...
  anuncio_100.mp4
```

---

## 🎯 Próximos Pasos

1. **Revisar calidad** de los primeros 5 anuncios
2. **Ajustar scripts** si es necesario
3. **Personalizar anuncios** según guía detallada
4. **Exportar lote final**
5. **Optimizar** basado en resultados

---

## 💡 Tips Pro

- **Usar expresiones** para animaciones reutilizables
- **Crear precomps** para elementos comunes
- **Usar null objects** para controlar múltiples capas
- **Aplicar efectos** de forma consistente
- **Guardar versiones** antes de cambios grandes

---

**¡Listo para crear 100 anuncios! 🚀**

