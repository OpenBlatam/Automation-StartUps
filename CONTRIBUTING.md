# 🤝 Guía de Contribución - Documentos BLATAM

¡Gracias por tu interés en contribuir a Documentos BLATAM! Esta guía te ayudará a entender cómo puedes contribuir al proyecto.

---

## 📋 Tabla de Contenidos

- [Código de Conducta](#código-de-conducta)
- [¿Cómo Puedo Contribuir?](#cómo-puedo-contribuir)
- [Proceso de Contribución](#proceso-de-contribución)
- [Estándares de Documentación](#estándares-de-documentación)
- [Estructura de Archivos](#estructura-de-archivos)
- [Pull Requests](#pull-requests)
- [Reportar Problemas](#reportar-problemas)
- [Sugerir Mejoras](#sugerir-mejoras)

---

## 🤝 Código de Conducta

Este proyecto sigue el [Contributor Covenant Code of Conduct](https://www.contributor-covenant.org/). Al participar, se espera que mantengas este código. Sé respetuoso, inclusivo y profesional en todas tus interacciones.

---

## 💡 ¿Cómo Puedo Contribuir?

### Tipos de Contribuciones

1. **📝 Documentación**
   - Mejorar documentación existente
   - Crear nuevas guías
   - Corregir errores tipográficos
   - Traducir contenido

2. **🔧 Scripts y Herramientas**
   - Mejorar scripts existentes
   - Crear nuevas herramientas
   - Optimizar automatizaciones

3. **📊 Templates y Recursos**
   - Crear nuevos templates
   - Mejorar templates existentes
   - Agregar ejemplos prácticos

4. **🐛 Corrección de Errores**
   - Reportar bugs
   - Corregir errores encontrados
   - Mejorar validaciones

5. **✨ Nuevas Funcionalidades**
   - Proponer nuevas características
   - Implementar mejoras
   - Agregar integraciones

---

## 🔄 Proceso de Contribución

### 1. Preparar tu Entorno

```bash
# Clonar el repositorio
git clone https://github.com/blatam/documentos.git
cd documentos

# Crear una rama para tu contribución
git checkout -b feature/tu-nombre-de-rama

# Instalar dependencias (si aplica)
npm install
```

### 2. Hacer Cambios

- Trabaja en tu rama local
- Haz commits pequeños y descriptivos
- Sigue los estándares de documentación
- Prueba tus cambios antes de enviar

### 3. Crear Pull Request

```bash
# Asegúrate de estar actualizado
git pull origin main

# Sube tus cambios
git push origin feature/tu-nombre-de-rama
```

Luego crea un Pull Request en GitHub con:
- Descripción clara de los cambios
- Referencia a issues relacionados (si aplica)
- Screenshots o ejemplos (si aplica)

---

## 📝 Estándares de Documentación

### Estructura de Documentos Markdown

Todos los documentos deben incluir frontmatter YAML:

```yaml
---
title: "Título del Documento"
category: "categoria"
tags: ["tag1", "tag2"]
created: "2025-01-XX"
updated: "2025-01-XX"
path: "ruta/al/archivo.md"
---
```

### Convenciones de Nomenclatura

- **Archivos**: `snake_case.md` o `kebab-case.md`
- **Directorios**: `snake_case/` o `kebab-case/`
- **Títulos**: Capitalización de Título
- **Variables**: `{{variable_name}}`

### Formato de Contenido

- Usa encabezados jerárquicos (`#`, `##`, `###`)
- Incluye tablas cuando sea apropiado
- Usa listas para pasos o elementos
- Agrega ejemplos de código cuando sea relevante
- Incluye enlaces a recursos relacionados

### Ejemplo de Documento

```markdown
---
title: "Guía de Ejemplo"
category: "06_documentation"
tags: ["guia", "ejemplo"]
created: "2025-01-15"
path: "06_documentation/guia_ejemplo.md"
---

# Guía de Ejemplo

## Introducción

Descripción breve del contenido...

## Pasos

1. Paso uno
2. Paso dos
3. Paso tres

## Ejemplo de Código

\`\`\`bash
comando ejemplo
\`\`\`

## Recursos

- [Enlace relacionado](url)
```

---

## 📁 Estructura de Archivos

### Organización por Categoría

```
documentos_blatam/
├── 01_marketing/          # Marketing y campañas
├── 02_finance/            # Finanzas y modelos
├── 03_human_resources/   # Recursos humanos
├── 04_operations/         # Operaciones
├── 05_technology/         # Tecnología
├── 06_documentation/     # Documentación central
├── 07_risk_management/    # Gestión de riesgos
├── 08_ai_artificial_intelligence/ # IA
├── 09_sales/              # Ventas
└── ...
```

### Dónde Colocar Nuevos Archivos

- **Documentación general**: `06_documentation/`
- **Templates**: `06_documentation/Templates/`
- **Scripts**: `04_operations/` o `tools/`
- **Guías específicas**: Categoría correspondiente
- **Checklists**: `06_documentation/Checklists/`

---

## 🔀 Pull Requests

### Antes de Enviar un PR

- [ ] He leído y seguido los estándares de documentación
- [ ] He actualizado el frontmatter del documento
- [ ] He verificado que los enlaces funcionan
- [ ] He revisado la ortografía y gramática
- [ ] He probado los scripts (si aplica)
- [ ] He actualizado el índice si es necesario

### Título del PR

Usa un formato claro:
- `docs: Agregar guía de X`
- `fix: Corregir error en Y`
- `feat: Agregar funcionalidad Z`
- `refactor: Mejorar estructura de X`

### Descripción del PR

Incluye:
- **Qué cambiaste**: Descripción breve
- **Por qué**: Razón del cambio
- **Cómo**: Pasos para probar
- **Screenshots**: Si aplica

### Ejemplo de PR

```markdown
## Descripción
Agrega guía completa de automatización de DMs de Instagram

## Cambios
- Nuevo archivo: `01_marketing/Guides/dm_automation_guide.md`
- Actualizado índice en `06_documentation/INDEX.md`
- Agregados 3 ejemplos prácticos

## Testing
- [x] Verificado formato markdown
- [x] Probados todos los enlaces
- [x] Revisada ortografía

## Screenshots
[Si aplica]
```

---

## 🐛 Reportar Problemas

### Crear un Issue

Usa las plantillas de issues cuando sea posible:

1. **Bug Report**: Para errores encontrados
2. **Feature Request**: Para nuevas funcionalidades
3. **Documentation**: Para mejoras de documentación
4. **Question**: Para preguntas

### Información a Incluir

- **Descripción clara** del problema
- **Pasos para reproducir** (si aplica)
- **Comportamiento esperado**
- **Comportamiento actual**
- **Screenshots** (si aplica)
- **Contexto adicional**

---

## 💡 Sugerir Mejoras

### Proceso de Sugerencias

1. **Busca issues existentes** para evitar duplicados
2. **Crea un issue** con la etiqueta `enhancement`
3. **Describe claramente** la mejora propuesta
4. **Explica el beneficio** para los usuarios
5. **Proporciona ejemplos** si es posible

### Tipos de Mejoras

- **Nuevas guías**: Documentación sobre temas no cubiertos
- **Mejoras de UX**: Hacer la documentación más accesible
- **Nuevas herramientas**: Scripts o automatizaciones
- **Optimizaciones**: Mejorar rendimiento o claridad

---

## 📚 Recursos Adicionales

### Documentación Relacionada

- [README.md](README.md) - Visión general del proyecto
- [ARCHITECTURE.md](ARCHITECTURE.md) - Arquitectura del proyecto
- [06_documentation/INDEX.md](06_documentation/INDEX.md) - Índice completo

### Herramientas Útiles

- **Markdown Linter**: `markdownlint-cli2`
- **Spell Checker**: `cspell` o `aspell`
- **Link Checker**: `markdown-link-check`

### Scripts de Ayuda

```bash
# Validar formato de documentos
npm run lint:docs

# Verificar enlaces
npm run check:links

# Organizar archivos
python organize_root_files.py
```

---

## ✅ Checklist de Contribución

Antes de enviar tu contribución, verifica:

- [ ] He seguido el código de conducta
- [ ] Mi código/documentación sigue los estándares
- [ ] He actualizado la documentación relacionada
- [ ] He probado mis cambios
- [ ] He actualizado el índice si es necesario
- [ ] He escrito commits descriptivos
- [ ] He creado un PR claro y completo

---

## 🎯 Áreas que Necesitan Contribuciones

### Prioridad Alta

- 📝 Mejorar documentación de inicio rápido
- 🔧 Optimizar scripts de automatización
- 📊 Crear más templates de dashboards
- 🌐 Traducciones a otros idiomas

### Prioridad Media

- ✨ Nuevas guías de integración
- 🎨 Mejoras de diseño visual
- 📈 Más ejemplos de casos de uso
- 🔍 Mejorar búsqueda y navegación

### Prioridad Baja

- 🧪 Tests automatizados
- 📱 Documentación móvil
- 🎥 Tutoriales en video
- 📚 Casos de estudio adicionales

---

## 🙏 Reconocimientos

Agradecemos a todos los contribuidores que hacen posible este proyecto. Tu esfuerzo ayuda a crear el ecosistema de documentación más completo en español.

---

## 📞 Contacto

Si tienes preguntas sobre cómo contribuir:

- Abre un issue con la etiqueta `question`
- Revisa la documentación en `06_documentation/`
- Consulta el [README.md](README.md) para más información

---

**¡Gracias por contribuir a Documentos BLATAM! 🚀**

