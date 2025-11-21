# ❓ Preguntas Frecuentes (FAQ) - Documentos BLATAM

Respuestas a las preguntas más comunes sobre Documentos BLATAM.

---

## 📋 Tabla de Contenidos

- [General](#general)
- [Uso](#uso)
- [Templates](#templates)
- [Scripts y Herramientas](#scripts-y-herramientas)
- [Contribución](#contribución)
- [Troubleshooting](#troubleshooting)

---

## 🌐 General

### ¿Qué es Documentos BLATAM?

**Documentos BLATAM** es un ecosistema completo de documentación empresarial que incluye más de 1,000 documentos especializados en marketing, ventas, IA, analítica, estrategia y más.

### ¿Es gratuito?

Sí, todo el contenido está disponible gratuitamente. Puedes usar, modificar y distribuir según la licencia del proyecto.

### ¿Necesito instalar algo?

No necesariamente. Puedes usar los templates y documentación directamente. Los scripts opcionales requieren Node.js o Python.

### ¿Qué idiomas están disponibles?

Principalmente español, con planes de expandir a inglés y portugués.

---

## 📝 Uso

### ¿Por dónde empiezo?

1. Lee el [`README.md`](README.md)
2. Revisa [`start_here.md`](06_documentation/start_here.md)
3. Explora según tu necesidad

### ¿Cómo encuentro lo que busco?

- Usa el [`INDEX.md`](06_documentation/INDEX.md)
- Busca en tu editor (Ctrl+F / Cmd+F)
- Navega por categorías en el README

### ¿Puedo usar los templates comercialmente?

Sí, puedes usar los templates para proyectos comerciales. Revisa la licencia para detalles específicos.

### ¿Cómo personalizo un template?

1. Copia el template
2. Busca variables `{{variable}}`
3. Reemplázalas con tus datos
4. Guarda tu versión personalizada

---

## 📄 Templates

### ¿Dónde están los templates?

- Marketing: `01_marketing/Sequences/`
- Ventas: `09_sales/Templates/`
- Generales: `06_documentation/Templates/`

### ¿Cómo uso las variables en templates?

```markdown
# Template
Hola {{nombre}}, tu evento es el {{fecha}}.

# Personalizado
Hola María, tu evento es el 15 de enero.
```

### ¿Puedo crear mis propios templates?

¡Sí! Sigue las convenciones en [`CONTRIBUTING.md`](CONTRIBUTING.md) y compártelos.

### ¿Los templates funcionan en todas las plataformas?

La mayoría son multiplataforma. Algunos están específicos para Instagram, LinkedIn, Email, etc.

---

## 🔧 Scripts y Herramientas

### ¿Qué necesito para usar los scripts?

- **Python scripts**: Python 3.9+
- **Node.js scripts**: Node.js 18+
- **Bash scripts**: Terminal (macOS/Linux) o WSL (Windows)

### ¿Cómo ejecuto un script?

```bash
# Python
python script.py

# Node.js
node script.js

# Bash
bash script.sh
```

### ¿Los scripts son seguros?

Sí, pero siempre revisa el código antes de ejecutar. No ejecutes scripts de fuentes no confiables.

### ¿Puedo modificar los scripts?

Sí, puedes modificar los scripts para tus necesidades. Considera contribuir mejoras.

---

## 🤝 Contribución

### ¿Cómo contribuyo?

1. Lee [`CONTRIBUTING.md`](CONTRIBUTING.md)
2. Encuentra un área de mejora
3. Crea un PR con tus cambios

### ¿Qué tipo de contribuciones necesitan?

- Mejoras de documentación
- Nuevos templates
- Corrección de bugs
- Nuevas funcionalidades
- Traducciones

### ¿Necesito experiencia técnica?

No necesariamente. Las contribuciones de documentación, templates y mejoras de contenido son muy valiosas.

### ¿Cómo reporto un bug?

Abre un issue en el repositorio con:
- Descripción del problema
- Pasos para reproducir
- Comportamiento esperado vs actual

---

## 🐛 Troubleshooting

### Los enlaces no funcionan

```bash
# Verifica enlaces rotos
python 06_documentation/Scripts/find_broken_links.py
```

### El frontmatter tiene errores

```bash
# Valida frontmatter
python 06_documentation/Scripts/frontmatter_validator.py
```

### No encuentro un archivo

- Usa el [`INDEX.md`](06_documentation/INDEX.md)
- Busca con tu editor
- Revisa la estructura en [`ARCHITECTURE.md`](ARCHITECTURE.md)

### Los scripts no funcionan

1. Verifica que tienes las dependencias instaladas
2. Revisa los permisos de ejecución
3. Consulta [`SETUP.md`](SETUP.md) para configuración

### ¿Dónde obtengo ayuda?

- Revisa [`Troubleshooting/`](06_documentation/Troubleshooting/)
- Consulta el [`README.md`](README.md)
- Abre un issue en el repositorio

---

## 📊 Específicas por Área

### Marketing

**P: ¿Cómo envío DMs de Instagram?**
R: Ve a `01_marketing/Sequences/` y usa los templates de DM.

**P: ¿Cómo genero URLs con UTM?**
R: Usa `node tools/build_utm_url.js` o los templates en `tools/`.

**P: ¿Dónde están los scripts de automatización?**
R: En `01_marketing/Scripts/` y `04_operations/`.

### Ventas

**P: ¿Dónde están los playbooks?**
R: En `09_sales/Sales_playbooks/`.

**P: ¿Cómo respondo objeciones?**
R: Revisa `09_sales/Objection_handling/`.

**P: ¿Hay scripts de descubrimiento?**
R: Sí, en `09_sales/Scripts/discovery*.md`.

### Analítica

**P: ¿Cómo calculo ROI?**
R: Usa `16_data_analytics/calculadora_roi.md`.

**P: ¿Dónde están los dashboards?**
R: En `16_data_analytics/` hay templates de Google Sheets.

**P: ¿Cómo configuro métricas?**
R: Revisa `16_data_analytics/` y las guías de Google Sheets.

---

## 🔄 Actualización y Versiones

### ¿Con qué frecuencia se actualiza?

El proyecto se actualiza regularmente. Revisa [`CHANGELOG.md`](CHANGELOG.md) para cambios recientes.

### ¿Cómo sé qué hay de nuevo?

- Revisa [`CHANGELOG.md`](CHANGELOG.md)
- Consulta [`ROADMAP.md`](ROADMAP.md)
- Revisa los commits recientes

### ¿Cómo actualizo mi copia local?

```bash
# Si usas Git
git pull origin main

# O descarga la última versión
```

---

## 📚 Recursos Adicionales

### Documentación

- [`README.md`](README.md) - Visión general
- [`QUICK_START.md`](QUICK_START.md) - Inicio rápido
- [`ARCHITECTURE.md`](ARCHITECTURE.md) - Estructura
- [`BEST_PRACTICES.md`](BEST_PRACTICES.md) - Mejores prácticas

### Guías

- [`06_documentation/start_here.md`](06_documentation/start_here.md) - Guía de inicio
- [`06_documentation/QuickStart.md`](06_documentation/QuickStart.md) - Setup completo
- [`SETUP.md`](SETUP.md) - Configuración

---

## 💬 ¿No Encuentras tu Pregunta?

- Revisa la documentación completa
- Busca en issues existentes
- Abre un nuevo issue con tu pregunta
- Consulta [`Troubleshooting/`](06_documentation/Troubleshooting/)

---

**Última actualización**: 2025-01-XX

