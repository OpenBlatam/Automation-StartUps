# 🛠️ Guía de Scripts Avanzados

Esta guía describe todos los scripts avanzados disponibles para gestión y análisis del proyecto.

---

## 📋 Índice de Scripts

1. [Búsqueda Avanzada](#búsqueda-avanzada)
2. [Análisis de Contenido](#análisis-de-contenido)
3. [Limpieza de Duplicados](#limpieza-de-duplicados)
4. [Estadísticas Rápidas](#estadísticas-rápidas)
5. [Organización](#organización)
6. [Verificación](#verificación)
7. [Generación de Índices](#generación-de-índices)

---

## 🔍 Búsqueda Avanzada

### `search_files.py`

Script de búsqueda avanzada con múltiples modos.

#### Modo Interactivo
```bash
python3 06_documentation/Scripts/search_files.py
```

Opciones disponibles:
1. **Buscar por nombre**: Busca archivos cuyo nombre coincida con un patrón (regex)
2. **Buscar por contenido**: Busca archivos que contengan un texto específico
3. **Buscar por categoría**: Busca archivos en una categoría específica
4. **Buscar por extensión**: Busca archivos por tipo de archivo
5. **Búsqueda combinada**: Combina múltiples criterios

#### Modo Línea de Comandos
```bash
# Buscar por nombre
python3 06_documentation/Scripts/search_files.py name "marketing"

# Buscar por contenido
python3 06_documentation/Scripts/search_files.py content "ROI"

# Buscar por categoría
python3 06_documentation/Scripts/search_files.py category marketing

# Buscar por extensión
python3 06_documentation/Scripts/search_files.py ext md
```

#### Ejemplos de Uso

**Buscar todos los archivos de email:**
```bash
python3 06_documentation/Scripts/search_files.py name "email"
```

**Buscar archivos que mencionen "ROI":**
```bash
python3 06_documentation/Scripts/search_files.py content "ROI"
```

**Buscar templates en marketing:**
```bash
python3 06_documentation/Scripts/search_files.py
# Seleccionar opción 5 (Búsqueda combinada)
# Nombre: template
# Categoría: marketing
```

---

## 📊 Análisis de Contenido

### `analyze_content.py`

Analiza el contenido de archivos Markdown para extraer insights.

#### Uso
```bash
python3 06_documentation/Scripts/analyze_content.py
```

#### Información Generada

- **Estadísticas generales**:
  - Total de archivos Markdown
  - Total de palabras y líneas
  - Promedios por archivo

- **Estructura de contenido**:
  - Bloques de código
  - Enlaces
  - Imágenes
  - Headers por nivel

- **Metadatos**:
  - Tags más comunes
  - Categorías más usadas
  - Lenguajes de código más frecuentes

- **Análisis de palabras clave**:
  - Palabras clave de negocio
  - Palabras más comunes (excluyendo comunes)

#### Ejemplo de Salida
```
📄 REPORTE DE ANÁLISIS DE CONTENIDO
================================================================================

📁 ESTADÍSTICAS DE MARKDOWN
  Total de archivos .md: 11,422
  Total de palabras: 2,456,789
  Total de líneas: 456,123
  Promedio de palabras por archivo: 215
  Promedio de líneas por archivo: 40

📝 ESTRUCTURA DE CONTENIDO
  Bloques de código: 1,234
  Enlaces: 5,678
  Imágenes: 890
```

---

## 🧹 Limpieza de Duplicados

### `cleanup_duplicates.py`

Identifica archivos duplicados por contenido y nombres similares.

#### Uso
```bash
python3 06_documentation/Scripts/cleanup_duplicates.py
```

#### Funcionalidades

1. **Duplicados por hash**:
   - Compara archivos por contenido (MD5)
   - Identifica archivos idénticos
   - Muestra tamaño y ubicación

2. **Nombres similares**:
   - Encuentra archivos con nombres similares
   - Útil para encontrar variantes

3. **Reporte JSON**:
   - Guarda reporte en `06_documentation/duplicados_report.json`
   - Incluye hasta 100 grupos de cada tipo

#### Ejemplo de Salida
```
📋 REPORTE DE ARCHIVOS DUPLICADOS
================================================================================

🔴 ARCHIVOS DUPLICADOS (mismo contenido): 15 grupos
   Total de archivos duplicados: 32

   Grupo 1 (3 archivos):
     - 01_marketing/template.md (1,234 bytes)
     - 06_documentation/Templates/template.md (1,234 bytes)
     - backups/template_backup.md (1,234 bytes)
```

---

## ⚡ Estadísticas Rápidas

### `quick_stats.py`

Obtiene estadísticas rápidas del proyecto sin análisis profundo.

#### Uso
```bash
python3 06_documentation/Scripts/quick_stats.py
```

#### Información Mostrada

- Total de archivos
- Total de carpetas
- Tamaño total del proyecto
- Top 5 extensiones
- Top 5 categorías

#### Ejemplo de Salida
```
📊 ESTADÍSTICAS RÁPIDAS
==================================================
Archivos: 17,967
Carpetas: 2,506
Tamaño: 841.39 MB

Top 5 extensiones:
  .md            : 11,422
  (sin ext)      : 3,083
  .py            : 994
  .js            : 299
  .html          : 246

Top 5 categorías:
  Marketing              : 5,697
  Documentation          : 2,190
  Technology             : 1,413
  AI                     : 1,354
  Business Strategy      : 736
```

---

## 📁 Organización

### `organize_root_files.py`

Organiza archivos del directorio raíz en carpetas apropiadas.

Ver [GUIA_ORGANIZACION_MEJORADA.md](./GUIA_ORGANIZACION_MEJORADA.md) para detalles completos.

---

## ✅ Verificación

### `verify_organization.py`

Verifica la organización y genera estadísticas detalladas.

Ver [GUIA_ORGANIZACION_MEJORADA.md](./GUIA_ORGANIZACION_MEJORADA.md) para detalles completos.

---

## 📝 Generación de Índices

### `generate_index.py`

Genera índices automáticos (INDEX.md) para carpetas principales.

Ver [GUIA_ORGANIZACION_MEJORADA.md](./GUIA_ORGANIZACION_MEJORADA.md) para detalles completos.

---

## 🎯 Casos de Uso Comunes

### Encontrar un archivo específico
```bash
python3 06_documentation/Scripts/search_files.py name "roi"
```

### Analizar contenido del proyecto
```bash
python3 06_documentation/Scripts/analyze_content.py
```

### Verificar duplicados antes de limpiar
```bash
python3 06_documentation/Scripts/cleanup_duplicates.py
```

### Obtener estadísticas rápidas
```bash
python3 06_documentation/Scripts/quick_stats.py
```

### Buscar archivos que mencionen un tema
```bash
python3 06_documentation/Scripts/search_files.py content "automatización"
```

### Encontrar todos los templates
```bash
python3 06_documentation/Scripts/search_files.py name "template"
```

---

## 🔧 Configuración y Requisitos

### Requisitos
- Python 3.6+
- Acceso de lectura/escritura al proyecto
- Permisos para ejecutar scripts

### Configuración
Todos los scripts están listos para usar. Solo necesitas:
```bash
chmod +x 06_documentation/Scripts/*.py
```

---

## 📊 Reportes Generados

Los scripts generan los siguientes reportes:

1. **`organizacion_raiz_report.json`**: Reporte de organización
2. **`estadisticas_organizacion.json`**: Estadísticas completas
3. **`duplicados_report.json`**: Reporte de duplicados

Todos los reportes se guardan en `06_documentation/`

---

## 🚀 Mejores Prácticas

1. **Ejecuta verificación periódicamente**:
   ```bash
   python3 06_documentation/Scripts/verify_organization.py
   ```

2. **Busca antes de crear**:
   ```bash
   python3 06_documentation/Scripts/search_files.py name "nuevo_archivo"
   ```

3. **Revisa duplicados regularmente**:
   ```bash
   python3 06_documentation/Scripts/cleanup_duplicates.py
   ```

4. **Analiza contenido para insights**:
   ```bash
   python3 06_documentation/Scripts/analyze_content.py
   ```

---

## 📞 Soporte

Para problemas o preguntas:
1. Revisa esta guía
2. Consulta los reportes JSON generados
3. Verifica los logs de los scripts
4. Revisa la documentación de cada script

---

**Última actualización**: 2025-01-XX  
**Versión**: 2.0







