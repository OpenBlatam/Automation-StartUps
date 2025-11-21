# 🎬 Sistema de Producción Masiva - 100 Anuncios After Effects

> Sistema completo para crear, personalizar y exportar 100 anuncios de video en After Effects de forma automatizada

---

## 📋 Contenido del Sistema

### 📁 Estructura de Archivos

```
/100_anuncios_after_effects/
├── 01_plantillas/          # Plantillas base de After Effects
├── 02_scripts/             # Scripts de automatización
│   ├── bulk_create_ads.jsx      # Crea 100 composiciones
│   ├── apply_variations.jsx    # Aplica variaciones de color
│   ├── batch_export.jsx        # Exporta masivamente
│   └── replace_text.jsx        # Reemplaza placeholders
├── 03_assets/              # Assets necesarios
│   ├── logos/              # Logos de marca
│   ├── musica/             # Música de fondo
│   ├── broll/               # B-roll opcional
│   └── fuentes/             # Fuentes personalizadas
├── 04_proyectos/           # Proyectos de After Effects
├── 05_exports/             # Videos exportados
│   ├── mp4/                # Formatos MP4
│   ├── mov/                # Formatos MOV
│   └── subtitulos/         # Archivos SRT
└── 06_documentacion/       # Documentación
    ├── GUIA_USO_RAPIDA.md      # Guía rápida de uso
    └── EXPRESIONES_AFTER_EFFECTS.md  # Expresiones útiles
```

---

## 🚀 Inicio Rápido

### Requisitos

- Adobe After Effects 2023 o superior
- Adobe Media Encoder (para exportación)
- ExtendScript Toolkit (opcional, para editar scripts)

### Pasos Básicos

1. **Abrir After Effects**
   ```
   File > New > New Project
   ```

2. **Ejecutar script de creación**
   ```
   File > Scripts > Run Script File...
   → Seleccionar: 02_scripts/bulk_create_ads.jsx
   ```

3. **Aplicar variaciones**
   ```
   File > Scripts > Run Script File...
   → Seleccionar: 02_scripts/apply_variations.jsx
   ```

4. **Personalizar textos**
   ```
   Editar: 02_scripts/replace_text.jsx
   → Cambiar valores en objeto 'replacements'
   → Ejecutar script
   ```

5. **Exportar**
   ```
   File > Scripts > Run Script File...
   → Seleccionar: 02_scripts/batch_export.jsx
   → Confirmar render
   ```

---

## 📚 Documentación Completa

### Documentos Principales

1. **[100_ANUNCIOS_AFTER_EFFECTS_PASO_A_PASO.md](../100_ANUNCIOS_AFTER_EFFECTS_PASO_A_PASO.md)**
   - Guía completa con los 100 anuncios paso a paso
   - Instrucciones detalladas para cada anuncio
   - Configuraciones y especificaciones

2. **[GUIA_USO_RAPIDA.md](06_documentacion/GUIA_USO_RAPIDA.md)**
   - Guía rápida de 5 minutos
   - Checklist pre-export
   - Solución de problemas comunes

3. **[EXPRESIONES_AFTER_EFFECTS.md](06_documentacion/EXPRESIONES_AFTER_EFFECTS.md)**
   - Colección de expresiones útiles
   - Animaciones pre-configuradas
   - Contadores y efectos

---

## 🎨 Personalización

### Cambiar Colores de Marca

1. Editar `02_scripts/apply_variations.jsx`
2. Modificar valores RGB en objeto `variations`
3. Ejecutar script nuevamente

### Cambiar Textos

1. Editar `02_scripts/replace_text.jsx`
2. Modificar objeto `replacements`
3. Ejecutar script

### Añadir Logo

1. Importar logo: `File > Import > File...`
2. Arrastrar a cada composición
3. Posicionar y escalar
4. Añadir animación si es necesario

### Añadir Música

1. Importar música: `File > Import > File...`
2. Arrastrar a composición
3. Ajustar volumen: `Layer > Audio > Audio Levels`
4. Aplicar ducking si hay VO

---

## 🔧 Scripts Incluidos

### Scripts Básicos

#### 1. bulk_create_ads.jsx
**Función:** Crea 100 composiciones automáticamente
- Composición base: 1080×1920, 30fps, 15s
- Background layer con color
- Texto hook con animación
- CTA placeholder
- Marcadores de tiempo

#### 2. apply_variations.jsx
**Función:** Aplica variaciones de color y estilo
- 5 variaciones de color diferentes
- Actualiza backgrounds
- Cambia colores de texto
- Modifica CTAs

#### 3. batch_export.jsx
**Función:** Exporta todos los anuncios a MP4
- Añade todas las composiciones a la cola
- Configura formato H.264
- Nombra archivos automáticamente
- Inicia render automático

#### 4. replace_text.jsx
**Función:** Reemplaza placeholders con valores reales
- Reemplazo masivo de texto
- Múltiples placeholders
- Actualiza todas las composiciones

---

### Scripts Avanzados (NUEVO v2.0)

#### 5. advanced_animations.jsx ⭐ NUEVO
**Función:** Aplica animaciones avanzadas automáticamente
- Fade in + Slide up
- Zoom in + Fade
- Slide from left
- Bounce in
- Elastic in
- Scale pulse

#### 6. quality_check.jsx ⭐ NUEVO
**Función:** Valida calidad de todos los anuncios
- Verifica resolución, frame rate, duración
- Verifica presencia de CTA y textos
- Verifica safe zones
- Genera reporte detallado

#### 7. apply_cta_templates.jsx ⭐ NUEVO
**Función:** Aplica plantillas de CTA predefinidas
- 5 plantillas diferentes
- Colores variados
- Animaciones automáticas
- Expresión de pulso incluida

#### 8. optimize_project.jsx ⭐ NUEVO
**Función:** Optimiza proyecto para mejor rendimiento
- Desactiva motion blur innecesario
- Optimiza calidad de capas
- Identifica items no usados
- Genera reporte

#### 9. add_music_batch.jsx ⭐ NUEVO
**Función:** Añade música de fondo masivamente
- Selecciona archivo de música
- Añade a todas las composiciones
- Ajusta volumen automáticamente
- Fade in/out automático

#### 10. add_logo_batch.jsx ⭐ NUEVO
**Función:** Añade logo masivamente
- Selecciona archivo de logo
- Escala automáticamente
- Posiciona correctamente
- Fade in automático

---

**📖 Ver [MEJORAS_SISTEMA.md](06_documentacion/MEJORAS_SISTEMA.md) para detalles completos**

---

## 📊 Especificaciones Técnicas

### Composición Base

- **Resolución:** 1080×1920 (9:16 vertical)
- **Frame Rate:** 30fps
- **Duración:** 15 segundos (450 frames)
- **Color Space:** sRGB

### Exportación

- **Formato:** MP4 (H.264)
- **Bitrate:** 15-20 Mbps
- **Audio:** AAC, 192 kbps
- **Resolución:** 1080×1920

### Safe Zones

- **Superior:** 150px libre
- **Inferior:** 150px libre
- **Laterales:** 50px libre

---

## ✅ Checklist de Producción

### Pre-Producción

- [ ] Estructura de carpetas creada
- [ ] Assets importados (logos, música)
- [ ] Fuentes instaladas
- [ ] Scripts descargados

### Producción

- [ ] 100 composiciones creadas
- [ ] Variaciones aplicadas
- [ ] Textos personalizados
- [ ] Logo añadido
- [ ] Música sincronizada
- [ ] CTAs visibles

### Post-Producción

- [ ] QA de primeros 5 anuncios
- [ ] Ajustes realizados
- [ ] Exportación configurada
- [ ] Render completado
- [ ] Archivos verificados

---

## 🎯 Workflow Recomendado

### Día 1: Setup y Creación

1. Crear estructura de carpetas
2. Importar assets
3. Ejecutar `bulk_create_ads.jsx`
4. Verificar composiciones creadas

### Día 2: Personalización

1. Ejecutar `apply_variations.jsx`
2. Editar y ejecutar `replace_text.jsx`
3. Añadir logo manualmente
4. Añadir música

### Día 3: Refinamiento

1. Revisar primeros 10 anuncios
2. Aplicar guías paso a paso
3. Ajustar animaciones
4. Optimizar timing

### Día 4: Exportación

1. Configurar `batch_export.jsx`
2. Iniciar render
3. Monitorear progreso
4. Verificar archivos exportados

---

## 🔍 Solución de Problemas

### Scripts no se ejecutan

**Solución:**
1. Verificar preferencias: `Edit > Preferences > Scripting & Expressions`
2. Habilitar: "Allow Scripts to Write Files"
3. Reiniciar After Effects

### Ruta de exportación no válida

**Solución:**
1. Editar `batch_export.jsx`
2. Cambiar `baseOutputPath` a ruta válida
3. Crear carpeta manualmente si no existe

### Render muy lento

**Solución:**
1. Reducir calidad temporalmente
2. Renderizar en lotes (10-20 a la vez)
3. Usar Media Encoder para mejor rendimiento

### Compositions no encontradas

**Solución:**
1. Verificar nombres empiezan con "Comp_"
2. Ejecutar `bulk_create_ads.jsx` primero
3. Verificar que sean CompItem

---

## 📈 Optimización

### Para Mejor Rendimiento

1. **Usar precomps** para elementos repetidos
2. **Aplicar expresiones** en lugar de keyframes cuando sea posible
3. **Renderizar en lotes** pequeños
4. **Usar proxies** para B-roll pesado

### Para Mejor Calidad

1. **Revisar cada anuncio** antes de exportar
2. **Ajustar timing** según guía
3. **Optimizar animaciones** para fluidez
4. **Verificar contraste** de textos

---

## 🎓 Recursos Adicionales

### Documentación Externa

- [After Effects Scripting Guide](https://ae-scripting.docsforadobe.dev/)
- [Expressions Reference](https://helpx.adobe.com/after-effects/using/expression-language-reference.html)
- [Best Practices](https://helpx.adobe.com/after-effects/using/best-practices.html)

### Comunidades

- [After Effects Reddit](https://www.reddit.com/r/AfterEffects/)
- [Creative COW](https://forums.creativecow.net/after-effects)
- [Video Copilot](https://www.videocopilot.net/)

---

## 📝 Notas Importantes

1. **Backup:** Siempre guardar copias del proyecto antes de cambios grandes
2. **Versiones:** Mantener versiones numeradas del proyecto
3. **Testing:** Probar scripts en proyecto de prueba primero
4. **Personalización:** Ajustar scripts según necesidades específicas

---

## 🚀 Próximos Pasos

1. ✅ Leer [GUIA_USO_RAPIDA.md](06_documentacion/GUIA_USO_RAPIDA.md)
2. ✅ Ejecutar scripts de creación
3. ✅ Personalizar con valores reales
4. ✅ Seguir guías paso a paso
5. ✅ Exportar y optimizar

---

**¡Sistema completo listo para usar! 🎬**

**Versión:** 5.1 (Final)  
**Última actualización:** 2025-01-27

### 🆕 Funcionalidades por Versión

#### v2.0 (Mejorada)
- ✅ 6 scripts avanzados nuevos
- ✅ Validación automática de calidad
- ✅ Añadir logo y música masivamente
- ✅ Optimización automática de proyecto
- ✅ Plantillas de CTA predefinidas
- ✅ Animaciones avanzadas automáticas

#### v3.0 (Completa)
- ✅ Generación automática de subtítulos (SRT)
- ✅ Creación de variantes A/B para testing
- ✅ Generación automática de thumbnails
- ✅ Análisis de métricas avanzado
- ✅ Exportación a múltiples formatos simultánea
- ✅ Sistema de backup automático
- ✅ Tags y categorización automática

#### v4.0 (Premium)
- ✅ Generación automática de metadata (JSON)
- ✅ Estructura de playlists por categoría
- ✅ Renombrado masivo inteligente
- ✅ Duplicación con variaciones automáticas
- ✅ Exportación optimizada por plataforma
- ✅ Reporte de producción completo

#### v5.0 (Enterprise)
- ✅ Optimización automática de CTAs
- ✅ Paletas de color inteligentes (psicología del color)
- ✅ Aplicación masiva de efectos profesionales
- ✅ Analizador de rendimiento avanzado

#### v5.1 (Final)
- ✅ Generación de índice maestro (JSON)
- ✅ Validación de compliance legal
- ✅ Sincronización de assets
- ✅ Biblioteca de templates reutilizables
- ✅ Estadísticas rápidas
- ✅ Actualización de timing
- ✅ Limpieza de items no usados
- ✅ Presets de exportación

**📖 Ver documentación:**
- [MEJORAS_SISTEMA.md](06_documentacion/MEJORAS_SISTEMA.md) - v2.0
- [FUNCIONALIDADES_AVANZADAS.md](06_documentacion/FUNCIONALIDADES_AVANZADAS.md) - v3.0
- [FUNCIONALIDADES_PREMIUM.md](06_documentacion/FUNCIONALIDADES_PREMIUM.md) - v4.0
- [MEJORAS_ULTIMAS.md](06_documentacion/MEJORAS_ULTIMAS.md) - v5.0

