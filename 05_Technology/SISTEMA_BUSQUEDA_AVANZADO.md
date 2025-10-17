# 🔍 SISTEMA DE BÚSQUEDA AVANZADO
## 📁 Guía Completa para Encontrar Documentos Rápidamente

### 🎯 **BÚSQUEDA POR CATEGORÍAS**

#### 🚀 **Venture Capital & Inversiones**
```bash
# Buscar documentos VC
find vc/ -name "*VC*" -type f
find vc/ -name "*investment*" -type f
find vc/ -name "*investor*" -type f

# Documentos específicos
vc/Anexo_A_Templates_Legales_VC.md
vc/VC_NEGOTIATION_STRATEGY_ULTRA.md
vc/Investor_Presentation_Complete_Kit_v*.md
```

#### 📈 **Marketing & Contenido**
```bash
# Buscar documentos de marketing
find marketing/ -name "*marketing*" -type f
find marketing/ -name "*content*" -type f
find marketing/ -name "*tiktok*" -type f

# Documentos específicos
marketing/MARKETING_CANVA_IA.md
marketing/tiktok_content/
marketing/01_Marketing/
```

#### 🤖 **IA & Tecnología**
```bash
# Buscar documentos de IA
find ai_technology/ -name "*AI*" -type f
find ai_technology/ -name "*technology*" -type f
find ai_technology/ -name "*consciousness*" -type f

# Documentos específicos
ai_technology/ai_tools/
ai_technology/08_AI_Artificial_Intelligence/
ai_technology/05_Technology/
```

#### 🎯 **Estrategia de Negocio**
```bash
# Buscar documentos de estrategia
find business_strategy/ -name "*strategy*" -type f
find business_strategy/ -name "*business*" -type f
find business_strategy/ -name "*executive*" -type f

# Documentos específicos
business_strategy/executive_documents/
business_strategy/04_Business_Strategy/
business_strategy/06_Strategy/
```

### 🔍 **BÚSQUEDA POR TIPO DE ARCHIVO**

#### 📄 **Documentos Markdown**
```bash
find . -name "*.md" -type f | grep -E "(vc|marketing|ai_technology|business_strategy)"
```

#### 📊 **Presentaciones**
```bash
find . -name "*.pptx" -type f
find . -name "*.ppt" -type f
```

#### 📈 **Hojas de Cálculo**
```bash
find . -name "*.xlsx" -type f
find . -name "*.xls" -type f
```

#### 🐍 **Scripts Python**
```bash
find . -name "*.py" -type f
```

### 🎯 **BÚSQUEDA POR CONTENIDO**

#### 🔍 **Búsqueda Semántica**
```bash
# Buscar por palabras clave
grep -r "venture capital" . --include="*.md"
grep -r "marketing strategy" . --include="*.md"
grep -r "artificial intelligence" . --include="*.md"
```

#### 📊 **Búsqueda por Métricas**
```bash
# Buscar documentos con ROI
grep -r "ROI" . --include="*.md"
grep -r "conversion" . --include="*.md"
grep -r "revenue" . --include="*.md"
```

### 🚀 **BÚSQUEDA RÁPIDA POR ÁREA**

#### 💰 **Finanzas**
- `02_Finance/` - Documentos financieros
- `vc/` - Inversiones y VC
- `business_strategy/executive_documents/` - Resúmenes ejecutivos

#### 📈 **Marketing**
- `marketing/` - Estrategias de marketing
- `marketing/tiktok_content/` - Contenido TikTok
- `marketing/01_Marketing/` - Marketing principal

#### 🤖 **Tecnología**
- `ai_technology/` - IA y tecnología
- `ai_technology/ai_tools/` - Herramientas de IA
- `ai_technology/08_AI_Artificial_Intelligence/` - IA avanzada

#### 🎯 **Estrategia**
- `business_strategy/` - Estrategias de negocio
- `business_strategy/executive_documents/` - Documentos ejecutivos
- `business_strategy/04_Business_Strategy/` - Estrategias principales

### 📋 **COMANDOS ÚTILES**

#### 🔍 **Buscar archivos recientes**
```bash
find . -type f -name "*.md" -mtime -7 | head -10
```

#### 📊 **Contar archivos por categoría**
```bash
find vc/ -type f | wc -l
find marketing/ -type f | wc -l
find ai_technology/ -type f | wc -l
```

#### 🎯 **Buscar archivos grandes**
```bash
find . -type f -size +1M -name "*.md" | head -10
```

### 🚀 **ACCESO RÁPIDO**

#### 📁 **Carpetas Principales**
- `vc/` - Venture Capital
- `marketing/` - Marketing
- `ai_technology/` - IA & Tech
- `business_strategy/` - Estrategia
- `operations_management/` - Operaciones
- `sales_customer/` - Ventas
- `research_development/` - I+D
- `compliance_legal/` - Legal

#### 📄 **Documentos Clave**
- `INDICE_GENERAL_ORGANIZACION.md` - Índice principal
- `SISTEMA_BUSQUEDA_AVANZADO.md` - Esta guía
- `README.md` en cada carpeta principal
