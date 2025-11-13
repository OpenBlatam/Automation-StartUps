# Exportación Avanzada - Sistema de Testimonios

## 📤 Nuevo Módulo: Export Manager

Sistema completo de exportación a múltiples formatos profesionales.

### Formatos Soportados

- ✅ **JSON**: Estructurado y completo
- ✅ **CSV**: Para análisis en Excel/Google Sheets
- ✅ **TXT**: Texto plano legible
- ✅ **PDF**: Documento profesional con formato
- ✅ **Excel**: Libro avanzado con múltiples hojas
- ✅ **PowerPoint**: Presentación lista para compartir

### Uso Básico

#### Exportar a Formato Específico

```bash
python scripts/testimonial_to_social_post.py \
  "[TESTIMONIO]" \
  "[PROBLEMA]" \
  --export-formats pdf excel \
  --predict-engagement
```

#### Exportar a Todos los Formatos

```bash
python scripts/testimonial_to_social_post.py \
  "[TESTIMONIO]" \
  "[PROBLEMA]" \
  --export-all \
  --predict-engagement
```

### Uso Programático

```python
from testimonial_export_manager import ExportManager

manager = ExportManager()

# Exportar a PDF
pdf_file = manager.export_to_pdf(
    post_data=post_data,
    output_file="reports/testimonial.pdf"
)

# Exportar a Excel avanzado
excel_file = manager.export_to_excel_advanced(
    posts=[post1, post2, post3],
    output_file="reports/testimonials.xlsx"
)

# Exportar a PowerPoint
pptx_file = manager.export_to_powerpoint(
    post_data=post_data,
    output_file="presentations/testimonial.pptx"
)

# Exportar a todos los formatos
all_files = manager.export_all_formats(
    post_data=post_data,
    base_filename="reports/testimonial",
    formats=['pdf', 'excel', 'pptx']
)
```

## 📄 Características por Formato

### PDF

- **Formato profesional** con estilos y colores
- **Tablas de métricas** formateadas
- **Contenido completo** del post
- **Recomendaciones** incluidas
- **Listo para compartir** o imprimir

**Requisitos**: `pip install reportlab`

### Excel Avanzado

- **Múltiples hojas**:
  - Resumen: Tabla con métricas principales
  - Detalles: Contenido completo de cada post
- **Formato automático** de celdas
- **Encabezados estilizados**
- **Ancho de columnas ajustado**

**Requisitos**: `pip install openpyxl`

### PowerPoint

- **Presentación lista** para compartir
- **Múltiples slides**:
  - Slide 1: Título y plataforma
  - Slide 2: Contenido generado
  - Slide 3: Métricas principales
- **Formato profesional**

**Requisitos**: `pip install python-pptx`

### CSV

- **Formato simple** para análisis
- **Compatible** con Excel, Google Sheets
- **Fácil importación** a bases de datos
- **UTF-8** para caracteres especiales

### TXT

- **Texto plano** legible
- **Formato estructurado**
- **Sin dependencias** adicionales
- **Fallback automático** si otros formatos fallan

## 🎯 Casos de Uso

### Caso 1: Reporte Ejecutivo

```bash
python scripts/testimonial_to_social_post.py \
  "[TESTIMONIO]" \
  "[PROBLEMA]" \
  --export-formats pdf \
  --generate-report \
  --predict-engagement
```

Genera un PDF profesional listo para presentar a stakeholders.

### Caso 2: Análisis en Excel

```bash
python scripts/testimonial_to_social_post.py \
  "[TESTIMONIO]" \
  "[PROBLEMA]" \
  --variations 5 \
  --export-formats excel csv \
  --predict-engagement
```

Genera Excel con todas las variaciones para análisis comparativo.

### Caso 3: Presentación Completa

```bash
python scripts/testimonial_to_social_post.py \
  "[TESTIMONIO]" \
  "[PROBLEMA]" \
  --export-formats pptx pdf \
  --generate-dashboard \
  --predict-engagement
```

Genera PowerPoint para presentación y PDF para documentación.

### Caso 4: Archivo Completo

```bash
python scripts/testimonial_to_social_post.py \
  "[TESTIMONIO]" \
  "[PROBLEMA]" \
  --export-all \
  --predict-engagement \
  --generate-report
```

Exporta a todos los formatos disponibles para máxima flexibilidad.

## 📊 Estructura de Archivos Exportados

### PDF

```
Análisis de Testimonio
├── Contenido Generado
├── Métricas Principales (tabla)
├── Hashtags
└── Recomendaciones
```

### Excel

```
Libro de Excel
├── Hoja "Resumen"
│   └── Tabla con métricas de todos los posts
└── Hoja "Detalles"
    └── Contenido completo de cada post
```

### PowerPoint

```
Presentación
├── Slide 1: Título
├── Slide 2: Contenido
└── Slide 3: Métricas
```

## 🔧 Personalización

### Exportar Solo Formatos Específicos

```python
manager.export_all_formats(
    post_data=post_data,
    base_filename="reports/testimonial",
    formats=['pdf', 'excel']  # Solo estos formatos
)
```

### Configurar Estilos PDF

Modifica `export_to_pdf` para personalizar:
- Colores
- Fuentes
- Tamaños
- Espaciado
- Gráficos

### Configurar Excel

Modifica `export_to_excel_advanced` para:
- Agregar más hojas
- Personalizar estilos
- Agregar gráficos
- Fórmulas automáticas

## 📝 Notas

- Los formatos avanzados (PDF, Excel, PowerPoint) requieren librerías adicionales
- Si una librería no está disponible, el sistema usa fallback automático
- Los archivos se guardan en el directorio especificado o `exports/` por defecto
- Todos los formatos mantienen la misma información, solo cambia la presentación

## 🚀 Próximas Mejoras

- [ ] Exportación a Word (.docx)
- [ ] Exportación a Google Sheets directa
- [ ] Plantillas personalizables para PDF
- [ ] Gráficos en Excel automáticos
- [ ] Exportación batch de múltiples testimonios
- [ ] Compresión automática en ZIP


