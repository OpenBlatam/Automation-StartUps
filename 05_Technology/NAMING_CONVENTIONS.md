# 📝 NAMING CONVENTIONS
## 📁 Convenciones de Nomenclatura para Archivos y Carpetas

### 🎯 **CONVENCIONES PRINCIPALES**

#### 📁 **Carpetas**
```
Formato: [NÚMERO]_[ÁREA]_[SUBCATEGORÍA]
Ejemplos:
- 01_Marketing_Content
- 02_VC_Investments
- 03_AI_Tools
- 04_Business_Strategy
```

#### 📄 **Archivos Markdown**
```
Formato: [TIPO]_[ÁREA]_[DESCRIPCIÓN]_[VERSIÓN].md
Ejemplos:
- Strategy_VC_Negotiation_v1.0.md
- Template_Marketing_Content_v2.1.md
- Analysis_AI_Performance_v1.5.md
- Guide_Business_Planning_v3.0.md
```

#### 📊 **Archivos de Datos**
```
Formato: [TIPO]_[ÁREA]_[FECHA]_[VERSIÓN].[EXTENSIÓN]
Ejemplos:
- Report_VC_Analysis_2024-10-06_v1.0.xlsx
- Data_Marketing_Metrics_2024-10-06_v2.1.csv
- Model_AI_Predictions_2024-10-06_v1.5.json
```

### 🎯 **TIPOS DE ARCHIVOS**

#### 📋 **Estrategias**
- `Strategy_[Área]_[Descripción]_v[Versión].md`
- Ejemplo: `Strategy_VC_Negotiation_v1.0.md`

#### 📄 **Templates**
- `Template_[Área]_[Descripción]_v[Versión].md`
- Ejemplo: `Template_Marketing_Content_v2.1.md`

#### 📊 **Análisis**
- `Analysis_[Área]_[Descripción]_v[Versión].md`
- Ejemplo: `Analysis_AI_Performance_v1.5.md`

#### 📖 **Guías**
- `Guide_[Área]_[Descripción]_v[Versión].md`
- Ejemplo: `Guide_Business_Planning_v3.0.md`

#### ✅ **Checklists**
- `Checklist_[Área]_[Descripción]_v[Versión].md`
- Ejemplo: `Checklist_VC_DueDiligence_v1.0.md`

#### 🛠️ **Herramientas**
- `Tool_[Área]_[Descripción]_v[Versión].[extensión]`
- Ejemplo: `Tool_AI_ContentGenerator_v1.0.py`

### 🎯 **ÁREAS PRINCIPALES**

#### 🚀 **Venture Capital**
- `VC` - Venture Capital
- `Investment` - Inversiones
- `Negotiation` - Negociación
- `DueDiligence` - Due Diligence

#### 📈 **Marketing**
- `Marketing` - Marketing
- `Content` - Contenido
- `SocialMedia` - Redes Sociales
- `SEO` - SEO

#### 🤖 **Inteligencia Artificial**
- `AI` - Inteligencia Artificial
- `ML` - Machine Learning
- `NLP` - Procesamiento de Lenguaje Natural
- `ComputerVision` - Visión por Computadora

#### 🎯 **Estrategia de Negocio**
- `Business` - Negocio
- `Strategy` - Estrategia
- `Planning` - Planificación
- `Operations` - Operaciones

### 📊 **VERSIONADO**

#### 🔢 **Formato de Versión**
```
v[MAJOR].[MINOR].[PATCH]
- MAJOR: Cambios importantes
- MINOR: Nuevas características
- PATCH: Correcciones menores
```

#### 📈 **Ejemplos de Versionado**
- `v1.0.0` - Versión inicial
- `v1.1.0` - Nueva característica
- `v1.1.1` - Corrección menor
- `v2.0.0` - Cambio importante

### 🎯 **FECHAS**

#### 📅 **Formato de Fecha**
```
YYYY-MM-DD
Ejemplo: 2024-10-06
```

#### 📊 **Uso en Archivos**
- **Reportes**: Incluir fecha en el nombre
- **Análisis**: Incluir fecha de creación
- **Datos**: Incluir fecha de recolección

### 🚀 **IMPLEMENTACIÓN**

#### 📝 **Pasos para Implementar**
1. **Revisar** archivos existentes
2. **Renombrar** según convenciones
3. **Actualizar** referencias
4. **Documentar** cambios

#### 🔍 **Herramientas de Renombrado**
```bash
# Renombrar archivos masivamente
for file in *.md; do
    mv "$file" "Template_Marketing_${file%.md}_v1.0.md"
done

# Buscar archivos que no siguen convenciones
find . -name "*.md" | grep -v -E "^[A-Z][a-z]+_[A-Z][a-z]+_.*_v[0-9]+\.[0-9]+\.md$"
```

### 📈 **BENEFICIOS**

#### ✅ **Organización Mejorada**
- Nombres consistentes
- Fácil identificación
- Navegación intuitiva

#### ✅ **Gestión de Versiones**
- Control de versiones
- Seguimiento de cambios
- Historial claro

#### ✅ **Búsqueda Eficiente**
- Búsqueda por patrones
- Filtrado automático
- Resultados precisos
