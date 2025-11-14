# 🛠️ Guía Completa de Herramientas - Suite Completa

**Versión**: 4.0  
**Total de Scripts**: 20

---

## 📋 Índice Completo de Herramientas

### 🔧 Organización y Estructura
1. [organize_root_files.py](#organize_root_filespy)
2. [verify_organization.py](#verify_organizationpy)
3. [generate_index.py](#generate_indexpy)

### 🔍 Búsqueda y Descubrimiento
4. [search_files.py](#search_filespy)

### 📊 Análisis y Estadísticas
5. [analyze_content.py](#analyze_contentpy)
6. [analyze_document_structure.py](#analyze_document_structurepy)
7. [quick_stats.py](#quick_statspy)
8. [extract_metadata.py](#extract_metadatapy)

### ✅ Validación y Calidad
9. [validate_templates.py](#validate_templatespy)
10. [find_broken_links.py](#find_broken_linkspy)

### 🧹 Limpieza y Mantenimiento
11. [cleanup_duplicates.py](#cleanup_duplicatespy)

---

## 🔧 Organización y Estructura

### `organize_root_files.py`

Organiza archivos del directorio raíz en carpetas apropiadas.

**Uso**:
```bash
python3 06_documentation/Scripts/organize_root_files.py
```

**Características**:
- Mapeo inteligente de archivos
- Detección de duplicados
- Generación de reporte JSON
- Estadísticas por carpeta

**Salida**: `06_documentation/organizacion_raiz_report.json`

---

### `verify_organization.py`

Verifica la organización y genera estadísticas detalladas.

**Uso**:
```bash
python3 06_documentation/Scripts/verify_organization.py
```

**Características**:
- Estadísticas por extensión
- Estadísticas por categoría
- Archivos más grandes
- Archivos más recientes
- Carpetas con más archivos

**Salida**: `06_documentation/estadisticas_organizacion.json`

---

### `generate_index.py`

Genera índices automáticos (INDEX.md) para carpetas principales.

**Uso**:
```bash
python3 06_documentation/Scripts/generate_index.py
```

**Características**:
- Índices automáticos por carpeta
- Lista de archivos con tamaños
- Lista de subcarpetas
- Formato Markdown con frontmatter

---

## 🔍 Búsqueda y Descubrimiento

### `search_files.py`

Búsqueda avanzada con múltiples modos.

**Uso Interactivo**:
```bash
python3 06_documentation/Scripts/search_files.py
```

**Uso CLI**:
```bash
# Por nombre
python3 06_documentation/Scripts/search_files.py name "marketing"

# Por contenido
python3 06_documentation/Scripts/search_files.py content "ROI"

# Por categoría
python3 06_documentation/Scripts/search_files.py category marketing

# Por extensión
python3 06_documentation/Scripts/search_files.py ext md
```

**Características**:
- Búsqueda por nombre (regex)
- Búsqueda por contenido
- Búsqueda por categoría
- Búsqueda por extensión
- Búsqueda combinada

---

## 📊 Análisis y Estadísticas

### `analyze_content.py`

Analiza el contenido de archivos Markdown.

**Uso**:
```bash
python3 06_documentation/Scripts/analyze_content.py
```

**Información**:
- Estadísticas de palabras y líneas
- Estructura (headers, código, enlaces)
- Tags y categorías
- Lenguajes de código
- Palabras clave de negocio

---

### `analyze_document_structure.py`

Analiza la estructura de documentos en detalle.

**Uso**:
```bash
# Analizar carpeta específica
python3 06_documentation/Scripts/analyze_document_structure.py 08_ai_artificial_intelligence

# Limitar número de archivos
python3 06_documentation/Scripts/analyze_document_structure.py . 50
```

**Información**:
- Estructura de headers
- Secciones y organización
- Score de complejidad
- Distribución de elementos
- Archivos más complejos

---

### `quick_stats.py`

Estadísticas rápidas sin análisis profundo.

**Uso**:
```bash
python3 06_documentation/Scripts/quick_stats.py
```

**Información**:
- Total de archivos y carpetas
- Tamaño total
- Top 5 extensiones
- Top 5 categorías

---

### `extract_metadata.py`

Extrae y analiza metadatos de archivos Markdown.

**Uso**:
```bash
# Analizar todo el proyecto
python3 06_documentation/Scripts/extract_metadata.py

# Analizar carpeta específica
python3 06_documentation/Scripts/extract_metadata.py 08_ai_artificial_intelligence

# Limitar archivos
python3 06_documentation/Scripts/extract_metadata.py . 200
```

**Requisitos**: `pip install pyyaml`

**Información**:
- Campos de frontmatter
- Categorías y tags
- Fechas de creación
- Campos faltantes
- Archivos sin frontmatter

---

## ✅ Validación y Calidad

### `validate_templates.py`

Valida estructura y formato de plantillas y documentos.

**Uso**:
```bash
# Validar todo
python3 06_documentation/Scripts/validate_templates.py

# Validar carpeta específica
python3 06_documentation/Scripts/validate_templates.py 06_documentation/Templates

# Validar archivos con patrón
python3 06_documentation/Scripts/validate_templates.py . "template"
```

**Validaciones**:
- Frontmatter YAML
- Jerarquía de headers
- Enlaces rotos
- Imágenes faltantes
- Estructura de plantillas
- Campos variables

---

### `find_broken_links.py`

Encuentra enlaces rotos en documentos.

**Uso**:
```bash
# Escanear todo
python3 06_documentation/Scripts/find_broken_links.py

# Escanear carpeta específica
python3 06_documentation/Scripts/find_broken_links.py 08_ai_artificial_intelligence

# Limitar archivos
python3 06_documentation/Scripts/find_broken_links.py . 200
```

**Información**:
- Enlaces rotos (internos)
- Enlaces válidos
- Enlaces externos
- Agrupación por archivo
- Línea donde está el enlace

---

## 🧹 Limpieza y Mantenimiento

### `cleanup_duplicates.py`

Identifica archivos duplicados.

**Uso**:
```bash
python3 06_documentation/Scripts/cleanup_duplicates.py
```

**Información**:
- Duplicados por hash (MD5)
- Nombres similares
- Ubicaciones de duplicados
- Tamaños de archivos

**Salida**: `06_documentation/duplicados_report.json`

---

## 🎯 Flujos de Trabajo Recomendados

### Flujo Diario

```bash
# 1. Verificar organización
python3 06_documentation/Scripts/quick_stats.py

# 2. Buscar archivos si es necesario
python3 06_documentation/Scripts/search_files.py name "archivo_buscado"

# 3. Organizar archivos nuevos
python3 06_documentation/Scripts/organize_root_files.py
```

### Flujo Semanal

```bash
# 1. Verificación completa
python3 06_documentation/Scripts/verify_organization.py

# 2. Validar plantillas
python3 06_documentation/Scripts/validate_templates.py

# 3. Buscar enlaces rotos
python3 06_documentation/Scripts/find_broken_links.py

# 4. Buscar duplicados
python3 06_documentation/Scripts/cleanup_duplicates.py

# 5. Actualizar índices
python3 06_documentation/Scripts/generate_index.py
```

### Flujo Mensual

```bash
# 1. Análisis completo de contenido
python3 06_documentation/Scripts/analyze_content.py

# 2. Análisis de estructura
python3 06_documentation/Scripts/analyze_document_structure.py

# 3. Análisis de metadatos
python3 06_documentation/Scripts/extract_metadata.py

# 4. Estadísticas completas
python3 06_documentation/Scripts/verify_organization.py
```

---

## 📊 Reportes Generados

Todos los scripts generan reportes en `06_documentation/`:

1. **`organizacion_raiz_report.json`** - Organización de archivos
2. **`estadisticas_organizacion.json`** - Estadísticas completas
3. **`duplicados_report.json`** - Archivos duplicados

---

## 🔧 Instalación de Dependencias

Algunos scripts requieren dependencias adicionales:

```bash
# Para extract_metadata.py
pip install pyyaml

# Para otros scripts (si es necesario)
pip install -r requirements.txt
```

---

## 📈 Estadísticas del Proyecto

### Totales
- **20 scripts** disponibles
- **17,986 archivos** catalogados
- **2,524 carpetas** mapeadas
- **841.81 MB** de contenido

### Por Categoría de Scripts
- **Organización**: 3 scripts
- **Búsqueda**: 1 script
- **Análisis**: 4 scripts
- **Validación**: 2 scripts
- **Limpieza**: 1 script
- **Otros**: 9 scripts adicionales

---

## 🚀 Mejores Prácticas

1. **Ejecuta validaciones regularmente** para mantener calidad
2. **Busca antes de crear** para evitar duplicados
3. **Actualiza índices** después de cambios grandes
4. **Revisa enlaces rotos** periódicamente
5. **Analiza metadatos** para mantener consistencia

---

## 📞 Soporte

Para problemas o preguntas:
1. Revisa esta guía
2. Consulta los reportes JSON
3. Verifica los logs de los scripts
4. Revisa la documentación específica de cada script

---

**Última actualización**: 2025-01-XX  
**Versión**: 4.0  
**Total de Scripts**: 20







