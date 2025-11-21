# 🏗️ Arquitectura del Proyecto - Documentos BLATAM

Este documento describe la arquitectura, estructura y organización del proyecto Documentos BLATAM.

---

## 📋 Tabla de Contenidos

- [Visión General](#visión-general)
- [Estructura de Directorios](#estructura-de-directorios)
- [Organización por Categorías](#organización-por-categorías)
- [Sistema de Metadatos](#sistema-de-metadatos)
- [Flujo de Documentación](#flujo-de-documentación)
- [Herramientas y Scripts](#herramientas-y-scripts)
- [Convenciones](#convenciones)

---

## 🎯 Visión General

**Documentos BLATAM** es un ecosistema de documentación empresarial organizado por categorías funcionales. Cada categoría contiene documentación especializada, scripts, templates y recursos relacionados.

### Principios de Diseño

1. **Modularidad**: Cada categoría es independiente pero interconectada
2. **Escalabilidad**: Fácil agregar nuevas categorías y contenido
3. **Navegabilidad**: Sistema de índices y enlaces claro
4. **Mantenibilidad**: Estructura consistente y documentada

---

## 📁 Estructura de Directorios

### Estructura Principal

```
documentos_blatam/
├── README.md                    # Punto de entrada principal
├── CONTRIBUTING.md              # Guía de contribución
├── CHANGELOG.md                 # Historial de cambios
├── SETUP.md                     # Guía de configuración
├── ARCHITECTURE.md              # Este archivo
├── ROADMAP.md                   # Hoja de ruta
│
├── 00_version_management/       # Gestión de versiones
├── 01_marketing/                # Marketing digital
├── 01_webinar_campaign/         # Campañas de webinars
├── 02_consciousness_systems/   # Sistemas de consciencia
├── 02_finance/                  # Finanzas
├── 03_human_resources/          # Recursos humanos
├── 04_business_strategy/        # Estrategia empresarial
├── 04_operations/               # Operaciones
├── 05_technology/               # Tecnología
├── 06_documentation/           # Documentación central
├── 06_strategy/                 # Estrategia
├── 07_advanced_features/       # Características avanzadas
├── 07_risk_management/         # Gestión de riesgos
├── 08_ai_artificial_intelligence/ # IA
├── 08_research_development/    # I+D
├── 09_sales/                    # Ventas
├── 10_customer_service/        # Atención al cliente
├── 11_research_development/    # I+D
├── 11_system_architecture/     # Arquitectura de sistemas
├── 12_quality_assurance/       # Aseguramiento de calidad
├── 12_user_guides/             # Guías de usuario
├── 13_legal_compliance/        # Legal y compliance
├── 14_procurement/             # Compras
├── 14_product_management/      # Gestión de productos
├── 14_thought_leadership/      # Liderazgo de pensamiento
├── 15_customer_experience/    # Experiencia de cliente
├── 16_data_analytics/          # Analítica de datos
├── 17_innovation/              # Innovación
├── 18_sustainability/          # Sostenibilidad
├── 19_international_business/   # Negocios internacionales
├── 20_project_management/     # Gestión de proyectos
└── ... (más categorías)
```

### Directorios Especiales

```
documentos_blatam/
├── tools/                      # Herramientas y scripts globales
├── Scripts/                    # Scripts de automatización
├── Templates/                  # Templates globales
├── Tests/                      # Tests y validaciones
├── Docs/                       # Documentación adicional
├── Static/                     # Archivos estáticos
├── Routes/                     # Rutas de API (si aplica)
├── Utils/                      # Utilidades
└── backups/                    # Backups y archivos antiguos
```

---

## 🗂️ Organización por Categorías

### Sistema de Numeración

Las categorías principales usan numeración de dos dígitos:
- `00-09`: Infraestructura y gestión
- `01-09`: Funciones principales de negocio
- `10-19`: Funciones de soporte
- `20+`: Categorías especializadas

### Estructura Interna de Categorías

Cada categoría típicamente contiene:

```
categoria/
├── readme.md                   # README de la categoría
├── Documentation/              # Documentación técnica
├── Guides/                    # Guías de usuario
├── Templates/                 # Templates específicos
├── Scripts/                   # Scripts relacionados
├── Examples/                  # Ejemplos prácticos
├── Checklists/                # Checklists
└── Other/                     # Otros recursos
```

### Ejemplo: Categoría de Marketing

```
01_marketing/
├── readme.md                  # Índice de marketing
├── Campaigns/                 # Campañas
├── Automations/               # Automatizaciones
├── Sequences/                 # Secuencias de email/DM
├── Scripts/                   # Scripts de marketing
├── Templates/                 # Templates de contenido
├── Guides/                    # Guías de marketing
├── Analytics/                 # Analítica de marketing
└── Other/                     # Otros recursos
```

---

## 📊 Sistema de Metadatos

### Frontmatter YAML

Todos los documentos Markdown incluyen frontmatter:

```yaml
---
title: "Título del Documento"
category: "categoria"
tags: ["tag1", "tag2", "tag3"]
created: "2025-01-15"
updated: "2025-01-20"
path: "ruta/completa/al/archivo.md"
author: "Nombre del Autor" (opcional)
version: "1.0.0" (opcional)
---
```

### Campos del Frontmatter

| Campo | Requerido | Descripción |
|-------|-----------|-------------|
| `title` | ✅ | Título del documento |
| `category` | ✅ | Categoría principal |
| `tags` | ✅ | Tags para búsqueda |
| `created` | ✅ | Fecha de creación (YYYY-MM-DD) |
| `updated` | ⚠️ | Fecha de última actualización |
| `path` | ✅ | Ruta relativa al archivo |
| `author` | ❌ | Autor del documento |
| `version` | ❌ | Versión del documento |

---

## 🔄 Flujo de Documentación

### Creación de Nuevo Documento

```
1. Identificar categoría apropiada
   ↓
2. Crear archivo con frontmatter
   ↓
3. Escribir contenido siguiendo estándares
   ↓
4. Agregar enlaces relevantes
   ↓
5. Actualizar índice de la categoría
   ↓
6. Validar formato y enlaces
   ↓
7. Commit y push
```

### Actualización de Documento Existente

```
1. Localizar documento
   ↓
2. Actualizar contenido
   ↓
3. Actualizar campo "updated" en frontmatter
   ↓
4. Verificar enlaces
   ↓
5. Actualizar índice si es necesario
   ↓
6. Commit cambios
```

---

## 🛠️ Herramientas y Scripts

### Scripts de Organización

- **`organize_root_files.py`**: Organiza archivos del directorio raíz
- **`organize_folders.py`**: Organiza archivos en carpetas
- **`verify_organization.py`**: Verifica organización

### Scripts de Validación

- **`frontmatter_validator.py`**: Valida frontmatter
- **`find_broken_links.py`**: Encuentra enlaces rotos
- **`validate_templates.py`**: Valida templates

### Scripts de Análisis

- **`analyze_content.py`**: Analiza contenido
- **`generate_index.py`**: Genera índices
- **`quick_stats.py`**: Estadísticas rápidas

### Herramientas de Marketing

- **`tools/apply_tokens.js`**: Aplica tokens a templates
- **`tools/build_utm_url.js`**: Genera URLs con UTM
- **`tools/generate_qr.js`**: Genera códigos QR

---

## 📝 Convenciones

### Nomenclatura de Archivos

- **Markdown**: `snake_case.md` o `kebab-case.md`
- **Scripts Python**: `snake_case.py`
- **Scripts JavaScript**: `camelCase.js` o `kebab-case.js`
- **Templates**: `template_name.md` o `TEMPLATE_NAME.md`

### Estructura de Documentos

1. **Frontmatter** (obligatorio)
2. **Título principal** (`#`)
3. **Introducción** (opcional)
4. **Tabla de contenidos** (para documentos largos)
5. **Contenido principal** (secciones con `##`, `###`)
6. **Ejemplos** (si aplica)
7. **Recursos relacionados** (enlaces)
8. **Referencias** (opcional)

### Enlaces

- **Enlaces internos**: Usar rutas relativas
- **Enlaces externos**: URLs completas
- **Enlaces a secciones**: Usar IDs de encabezados

### Ejemplo de Estructura

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

Descripción breve...

## Contenido Principal

### Sección 1

Contenido...

### Sección 2

Contenido...

## Ejemplos

\`\`\`bash
comando ejemplo
\`\`\`

## Recursos Relacionados

- [Enlace 1](ruta)
- [Enlace 2](ruta)
```

---

## 🔗 Interconexión

### Sistema de Índices

- **Índice Principal**: `06_documentation/INDEX.md`
- **Índices por Categoría**: `categoria/readme.md`
- **Índices Especializados**: Varios según necesidad

### Enlaces Cruzados

Los documentos se enlazan entre sí usando:
- Enlaces relativos para documentos internos
- Referencias a categorías relacionadas
- Sistema de tags para descubrimiento

---

## 📈 Escalabilidad

### Agregar Nueva Categoría

1. Crear directorio con nombre descriptivo
2. Agregar `readme.md` con índice
3. Actualizar `06_documentation/INDEX.md`
4. Crear estructura interna estándar

### Agregar Nuevo Tipo de Documento

1. Seguir convenciones de nomenclatura
2. Incluir frontmatter completo
3. Agregar a índice correspondiente
4. Crear enlaces relevantes

---

## 🔍 Búsqueda y Descubrimiento

### Métodos de Búsqueda

1. **Por categoría**: Navegar directorios
2. **Por tags**: Buscar en frontmatter
3. **Por índice**: Usar índices maestros
4. **Por búsqueda de texto**: Buscar en contenido

### Tags Comunes

- `guia`, `guide`: Guías de usuario
- `template`: Templates
- `script`: Scripts
- `checklist`: Checklists
- `troubleshooting`: Solución de problemas
- `api`: Documentación de API
- `setup`: Configuración

---

## 🎯 Mejores Prácticas

1. **Consistencia**: Seguir convenciones establecidas
2. **Documentación**: Documentar decisiones importantes
3. **Enlaces**: Mantener enlaces actualizados
4. **Validación**: Validar antes de commit
5. **Organización**: Mantener estructura clara
6. **Actualización**: Actualizar fechas y versiones

---

## 📚 Recursos Adicionales

- [README.md](README.md) - Visión general
- [CONTRIBUTING.md](CONTRIBUTING.md) - Guía de contribución
- [SETUP.md](SETUP.md) - Configuración
- [06_documentation/INDEX.md](06_documentation/INDEX.md) - Índice completo

---

**Última actualización**: 2025-01-XX

