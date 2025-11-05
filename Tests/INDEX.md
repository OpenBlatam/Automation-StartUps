---
title: "Index"
category: "Tests"
tags: []
encoded_with: "utf-8"
created: "2025-10-29"
path: "Tests/INDEX.md"
---

# 📋 Índice - Tests

<div align="center">

**Guía Completa del Sistema de Testing**

[![Tests](https://img.shields.io/badge/Tests-19+-green.svg)](./test_api_smoke.py)
[![Coverage](https://img.shields.io/badge/Coverage-80%25+-blue.svg)](#-estadísticas-y-cobertura)
[![Python](https://img.shields.io/badge/Python-3.9+-blue.svg)](./Scripts/)
[![Pytest](https://img.shields.io/badge/pytest-Latest-orange.svg)](https://docs.pytest.org/)
[![Status](https://img.shields.io/badge/Status-Active-success.svg)](#-estado-del-sistema)

**Generado:** 2025-10-29 19:35:20  
**Versión:** 5.3 | **Líneas:** 2300+ | **Secciones:** 50+

</div>

---

## 📑 Tabla de Contenidos

<div align="center">

> **💡 Búsqueda Rápida:** Usa `Ctrl+F` (o `Cmd+F` en Mac) para buscar cualquier término en este documento.  
> **⚡ Navegación Rápida:** Usa los enlaces internos para saltar directamente a cualquier sección.  
> **🔍 Búsqueda por Tema:** Ve a la sección [Búsqueda Rápida por Tema](#-búsqueda-rápida-por-tema) para encontrar temas específicos.

</div>

### 🔤 Búsqueda Rápida por Tema

| Tema | Sección |
|:-----|:--------|
| **Anti-Patrones** | [Anti-Patrones Comunes](#-anti-patrones-comunes) |
| **Best Practices** | [Mejores Prácticas](#-mejores-prácticas) |
| **CI/CD** | [Integración Continua](#-workflows-de-testing) |
| **Coverage** | [Estadísticas y Cobertura](#-estadísticas-y-cobertura) |
| **Debugging** | [Debugging Avanzado](#-debugging-avanzado) |
| **Diagramas** | [Diagramas Visuales](#-diagramas-visuales-de-flujos) |
| **Fixtures** | [Patrones Comunes](#-patrones-comunes-de-testing) |
| **Git Hooks** | [Integración con Git Hooks](#-integración-con-git-hooks) |
| **IDEs** | [Integración con IDEs](#️-integración-con-ides) |
| **Performance** | [Performance Optimization](#-performance-optimization) |
| **Quick Wins** | [Quick Wins](#-quick-wins-empezar-en-30-segundos) |
| **Roadmap** | [Roadmap y Próximos Pasos](#-roadmap-y-próximos-pasos) |
| **Seguridad** | [Seguridad en Tests](#-seguridad-en-tests) |
| **Templates** | [Templates de Tests](#-templates-de-tests) |
| **Troubleshooting** | [Troubleshooting](#-troubleshooting) |

### 🚀 Inicio Rápido
- [Quick Wins](#-quick-wins-empezar-en-30-segundos)
- [Resumen Ejecutivo](#-resumen-ejecutivo)
- [Acceso Rápido](#-acceso-rápido)
- [Quick Start](#-quick-start)

### 📚 Documentación
- [Estructura del Proyecto](#-estructura-del-proyecto)
- [Descripción de Tests](#-descripción-detallada-de-tests)
- [Guía Rápida de Uso](#-guía-rápida-de-uso)
- [Tipos de Tests](#-tipos-de-tests-cubiertos)

### 🛠️ Guías Prácticas
- [Troubleshooting](#-troubleshooting)
- [Mejores Prácticas](#-mejores-prácticas)
- [Workflows de Testing](#-workflows-de-testing)
- [Casos de Uso Avanzados](#-casos-de-uso-avanzados)

### 📊 Análisis y Métricas
- [Estadísticas y Cobertura](#-estadísticas-y-cobertura)
- [Dashboard de Métricas](#-dashboard-de-métricas)
- [Performance Optimization](#-performance-optimization)

### 🎓 Aprendizaje
- [Aprendizaje Progresivo](#-aprendizaje-progresivo)
- [Templates de Tests](#-templates-de-tests)
- [Tips y Tricks Avanzados](#-tips-y-tricks-avanzados)
- [Recursos de Aprendizaje](#-recursos-de-aprendizaje)

### 🔧 Recursos
- [Recursos Adicionales](#-recursos-adicionales)
- [FAQ](#-faq---preguntas-frecuentes)
- [Soporte y Contacto](#-soporte-y-contacto)

### ⚡ Herramientas Prácticas
- [Atajos y Comandos Rápidos](#️-atajos-y-comandos-rápidos)
- [Glosario de Términos](#-glosario-de-términos)
- [Patrones Comunes](#-patrones-comunes-de-testing)
- [Debugging Avanzado](#-debugging-avanzado)
- [Integración con IDEs](#️-integración-con-ides)

### 🔄 Automatización
- [Checklist de Calidad Pre-Commit](#-checklist-de-calidad-pre-commit)
- [Ejemplos de Flujos Completos](#-ejemplos-de-flujos-completos)
- [Integración con Git Hooks](#-integración-con-git-hooks)
- [Métricas y Reportes Automatizados](#-métricas-y-reportes-automatizados)
- [Best Practices Checklist Extendido](#-best-practices-checklist-extendido)

### 🎨 Visualización y Patrones
- [Diagramas Visuales de Flujos](#-diagramas-visuales-de-flujos)
- [Anti-Patrones Comunes](#-anti-patrones-comunes)
- [Seguridad en Tests](#-seguridad-en-tests)
- [Roadmap y Próximos Pasos](#-roadmap-y-próximos-pasos)

---

## ⚡ Quick Wins (Empezar en 30 segundos)

<div align="center">

| Acción | Comando | Resultado |
|:------:|:--------|:----------|
| 🚀 **Ejecutar tests** | `pytest` | Todos los tests |
| 🔥 **Smoke tests** | `pytest test_api_smoke.py -v` | Verificación rápida |
| 📊 **Ver cobertura** | `pytest --cov=app` | Reporte de cobertura |
| 🎯 **Test específico** | `pytest test_api_smoke.py::test_health_endpoint` | Un test único |
| ⚡ **Solo fallidos** | `pytest --lf` | Re-ejecutar fallidos |

</div>

---

## 📊 Resumen Ejecutivo

| Métrica | Valor | Estado |
|---------|-------|--------|
| **Carpetas** | 2 (Documentation, Scripts) | ✅ |
| **Tests principales** | 2 archivos | ✅ |
| **Scripts de testing** | 6 archivos | ✅ |
| **Documentación** | 6 archivos (README + 5 guías) | ✅ |
| **Total archivos** | 13 | ✅ |
| **Lenguajes** | Python 🐍, JavaScript 📜, Markdown 📝 | ✅ |
| **Frameworks** | pytest, Flask test client, Node.js | ✅ |
| **Cobertura objetivo** | 80%+ | 🎯 |
| **Tiempo ejecución** | < 30s (suite completa) | ⚡ |
| **Tests totales** | 19+ tests | ✅ |

### 🎯 Estado del Sistema

| Aspecto | Estado | Detalles |
|:--------|:------:|:---------|
| **Tests funcionales** | ✅ | Todos los tests pasan |
| **Documentación** | ✅ | Completa y actualizada (6 archivos) |
| **Cobertura** | ✅ | API, Auth, Products, Utils, Validators |
| **CI/CD Ready** | ✅ | Configurado para integración continua |
| **Mantenimiento** | ✅ | Activo y documentado |
| **Performance** | ⚡ | Tests rápidos (< 30s suite completa) |

### 📈 Métricas de Calidad

| Métrica | Objetivo | Actual | Estado |
|---------|----------|--------|--------|
| **Cobertura de código** | 80%+ | En progreso | 🎯 |
| **Tiempo de ejecución** | < 30s | < 30s | ✅ |
| **Tests independientes** | 100% | 100% | ✅ |
| **Documentación** | Completa | 100% | ✅ |
| **Tests por funcionalidad** | 2+ | 2+ | ✅ |

---

## 📁 Estructura del Proyecto

### 📂 Carpetas

| Carpeta | Archivos | Descripción |
|---------|----------|-------------|
| **[Documentation](./Documentation/)** | 5 | 📚 Documentación y guías de referencia para tests |
| **[Scripts](./Scripts/)** | 6 | 🛠️ Scripts de testing y utilidades (Python + JS) |

### 📄 Archivos en Raíz

| Archivo | Tipo | Descripción |
|---------|------|-------------|
| **[test_api_smoke.py](./test_api_smoke.py)** | 🧪 Test | Tests de smoke para verificación rápida de API |
| **[test_auth_products.py](./test_auth_products.py)** | 🔐 Test | Tests de autenticación y endpoints de productos |

---

## 🚀 Acceso Rápido

### 🧪 Tests Principales

| Test | Archivo | Tiempo | Descripción |
|------|---------|--------|-------------|
| 🔥 **Smoke Tests** | [test_api_smoke.py](./test_api_smoke.py) | < 1s | Verificación rápida de endpoints críticos |
| 🔐 **Auth & Products** | [test_auth_products.py](./test_auth_products.py) | < 2s | Tests de autenticación y productos |
| 🛠️ **Utils Tests** | [Scripts/test_utils.py](./Scripts/test_utils.py) | < 3s | Tests de funciones utilitarias |
| ✅ **Validators Tests** | [Scripts/test_validators.py](./Scripts/test_validators.py) | < 2s | Tests de validadores de datos |

### 📚 Documentación

| Documento | Tipo | Descripción |
|-----------|------|-------------|
| **[README Principal](./README.md)** | 📘 Guía principal | Documentación completa del sistema de tests |
| **[Guía de Uso](./Documentation/USAGE_GUIDE.md)** | 🚀 Tutorial | Guía práctica para usar los tests |
| **[Documentación Técnica](./Documentation/TECHNICAL_DOCS.md)** | ⚙️ Técnica | Detalles técnicos y arquitectura |
| **[Guía de Contribución](./Documentation/CONTRIBUTING.md)** | ✏️ Contribución | Cómo contribuir nuevos tests |
| **[Documentation Index](./Documentation/index.md)** | 📋 Índice | Índice de documentación |

### 🛠️ Scripts y Utilidades

| Recurso | Descripción |
|---------|-------------|
| [Scripts Index](./Scripts/INDEX.md) | Índice completo de scripts y utilidades |

---

## 📊 Desglose por Tecnología

| Lenguaje | Archivos | Tipo | Uso |
|----------|----------|------|-----|
| 🐍 **Python** | 4 | Tests + Utilidades | pytest, Flask test client |
| 📜 **JavaScript** | 3 | Scripts de testing | Node.js, validación API |
| 📝 **Markdown** | 6 | Documentación | README, índices y guías |

---

## 🧪 Descripción Detallada de Tests

### 🔥 Tests de API (Raíz)

#### `test_api_smoke.py` - Smoke Tests
**Tipo:** Tests de integración | **Framework:** Flask test client | **Propósito:** Verificación rápida

| Función | Endpoint | Validación |
|---------|----------|------------|
| `test_health_endpoint()` | `/api/health` | Status code 200/503, campo `status` presente |
| `test_openapi_and_docs()` | `/api/openapi.json` | OpenAPI 3.x, status 200 |
| | `/api/docs` | Swagger UI presente, status 200 |

**Características:**
- ✅ Verificación rápida de endpoints críticos
- ✅ Validación de formato OpenAPI 3.x
- ✅ Verificación de documentación Swagger
- ✅ Tests de integración básica con Flask test client

#### `test_auth_products.py` - Autenticación y Productos
**Tipo:** Tests de seguridad + integración | **Framework:** Flask test client | **Propósito:** Validación de seguridad

| Función | Endpoint | Validación |
|---------|----------|------------|
| `test_products_requires_auth()` | `/api/products` | Requiere autenticación (401/403) |
| `test_products_with_auth()` | `/api/products` | Acceso con token válido (200) |

**Características:**
- 🔐 Tests de autenticación (login, generación de tokens)
- 📦 Tests de endpoints de productos con y sin autenticación
- 🛡️ Validación de seguridad y acceso a recursos protegidos
- ✅ Verifica que endpoints requieren autenticación cuando corresponde

### 🛠️ Scripts de Testing

#### 🐍 Python Scripts

| Archivo | Tipo | Funcionalidad |
|---------|------|---------------|
| **test_utils.py** | Tests unitarios | Funciones utilitarias |
| **test_validators.py** | Tests unitarios | Validadores de datos |

**test_utils.py - Funciones Utilitarias:**
- 📊 **Formatters:** currency, date, percentage, stock status, text truncation
- 🔧 **Helpers:** safe divide, percentage change, filename sanitization, SKU generation
- ✅ Validación de formateo de datos y operaciones seguras

**test_validators.py - Validadores:**
- ✅ Validación de entrada de datos
- ✅ Verificación de reglas de negocio
- ✅ Tests de validación de esquemas

#### 📜 JavaScript Scripts

| Archivo | Tipo | Descripción |
|---------|------|-------------|
| **apitest.js** | Test API | Scripts de testing de API en Node.js |
| **validadortest.js** | Test validadores | Tests de validadores en JavaScript |
| **setup.js** | Configuración | Configuración y setup para tests |

---

## 💡 Guía Rápida de Uso

### 🚀 Ejecutar Tests

#### ⚡ Comandos Esenciales

```bash
# 🎯 Ejecutar todos los tests (< 30s)
pytest

# 🔥 Smoke tests rápidos (< 1s)
pytest test_api_smoke.py -v

# 🔐 Auth & Products tests (< 2s)
pytest test_auth_products.py -v

# 📦 Unit tests (Utils & Validators) (< 5s)
pytest Scripts/ -v

# 📊 Ver cobertura
pytest --cov=app --cov-report=term-missing

# 🎯 Test específico
pytest test_api_smoke.py::test_health_endpoint -v
```

#### Opciones Avanzadas

```bash
# Tests con output detallado (verbose)
python -m pytest -v test_api_smoke.py

# Tests con output muy detallado
python -m pytest -vv test_api_smoke.py

# Tests con cobertura de código
python -m pytest --cov=app test_api_smoke.py

# Tests con cobertura y reporte HTML
python -m pytest --cov=app --cov-report=html test_api_smoke.py

# Ejecutar un test específico
python -m pytest test_api_smoke.py::test_health_endpoint

# Tests con output en tiempo real
python -m pytest -s test_api_smoke.py

# Parar en el primer error
python -m pytest -x test_api_smoke.py

# Ejecutar solo tests que fallaron anteriormente
python -m pytest --lf
```

#### Variables de Entorno

```bash
# Configurar entorno de testing
export FLASK_ENV=testing

# Ejecutar tests con configuración específica
FLASK_ENV=testing python -m pytest
```

### Estructura recomendada

```
Tests/
├── README.md                    # 📚 Documentación principal completa
├── INDEX.md                     # 📋 Este índice
├── Documentation/               # 📖 Documentación detallada
│   ├── index.md                 # Índice de documentación
│   ├── USAGE_GUIDE.md          # Guía práctica de uso
│   ├── TECHNICAL_DOCS.md        # Documentación técnica
│   └── CONTRIBUTING.md          # Guía de contribución
├── Scripts/                     # 🛠️ Scripts y utilidades
│   ├── test_utils.py            # Tests de utilidades
│   ├── test_validators.py       # Tests de validadores
│   ├── apitest.js               # Tests API en JS
│   ├── validadortest.js         # Validadores en JS
│   ├── setup.js                 # Setup de tests
│   └── INDEX.md                 # Índice de scripts
├── test_api_smoke.py            # 🔥 Tests básicos de API
└── test_auth_products.py        # 🔐 Tests de autenticación
```

---

## 🎯 Tipos de tests cubiertos

### 📊 Matriz de Cobertura

| Tipo | Archivos | Tests | Cobertura | Tiempo |
|------|----------|-------|-----------|--------|
| **Smoke Tests** | 1 | 2 | API básica | < 1s |
| **Integration Tests** | 1 | 2 | Auth + Products | < 2s |
| **Unit Tests** | 2 | 10+ | Utils + Validators | < 5s |
| **API Tests (JS)** | 2 | 5+ | API endpoints | < 3s |
| **Total** | 6 | 19+ | 80%+ | < 30s |

### ✅ Tests de integración
- **API Smoke Tests:** Verificación básica de endpoints críticos
- **Auth Tests:** Validación de autenticación y autorización
- **Product Tests:** Tests de endpoints de productos con/sin auth
- **End-to-End:** Flujos completos de autenticación y acceso

### ✅ Tests unitarios
- **Utils Tests:** Funciones utilitarias (formatters, helpers)
- **Validator Tests:** Validadores de datos y reglas de negocio
- **Helpers Tests:** Funciones auxiliares compartidas

### ✅ Tests de API
- **JavaScript Tests:** Scripts de testing para API en Node.js
- **Python Tests:** Tests de integración con Flask test client
- **Cross-platform:** Tests que funcionan en ambos entornos

---

## 📈 Estadísticas y Cobertura

| Categoría | Detalles |
|-----------|----------|
| **Tests Python** | 2 archivos principales + 2 utilidades |
| **Scripts JavaScript** | 3 archivos (API tests + validadores) |
| **Documentación** | 6 archivos markdown (README + 4 guías) |
| **Cobertura** | API, autenticación, productos, utilidades, validadores |
| **Frameworks** | pytest (Python), Node.js (JavaScript), Flask test client |
| **Tipos de tests** | Integración, unitarios, smoke, seguridad |

---

## 🔧 Troubleshooting

### 🚨 Problemas Comunes y Soluciones

#### ❌ Error: Module not found
**Síntoma:** `ModuleNotFoundError: No module named 'app'`

**Solución:**
```bash
# 1. Asegúrate de estar en el directorio raíz del proyecto
cd /ruta/al/proyecto

# 2. Verifica que las dependencias estén instaladas
pip install -r requirements.txt
pip install pytest pytest-cov

# 3. Verifica PYTHONPATH
export PYTHONPATH="${PYTHONPATH}:$(pwd)"

# 4. Ejecuta desde la raíz
python -m pytest Tests/
```

#### ❌ Error: Flask app not found
**Síntoma:** `RuntimeError: Working outside of application context`

**Solución:**
```bash
# Opción 1: Variable de entorno
export FLASK_ENV=testing
pytest

# Opción 2: Inline
FLASK_ENV=testing python -m pytest

# Opción 3: Archivo .env.test
echo "FLASK_ENV=testing" > .env.test
pytest
```

#### ❌ Tests fallan por autenticación
**Síntoma:** `401 Unauthorized` o `403 Forbidden`

**Solución:**
```bash
# 1. Verifica credenciales de test
# En test_auth_products.py debe ser:
# username: 'admin'
# password: 'admin123'

# 2. Verifica que el endpoint de login funcione
curl -X POST http://localhost:5000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"admin123"}'

# 3. Verifica generación de token
pytest test_auth_products.py::test_products_with_auth -v -s
```

#### ❌ Error: ImportError
**Síntoma:** `ImportError: cannot import name 'create_app'`

**Solución:**
```bash
# 1. Verifica estructura de proyecto
ls -la app.py  # Debe existir

# 2. Instala en modo desarrollo
pip install -e .

# 3. Verifica imports
python -c "from app import create_app; print('OK')"

# 4. Ejecuta con PYTHONPATH
PYTHONPATH=. pytest
```

#### ❌ Tests muy lentos
**Síntoma:** Tests tardan más de 30 segundos

**Solución:**
```bash
# 1. Ejecuta en paralelo
pytest -n auto

# 2. Identifica tests lentos
pytest --durations=10

# 3. Usa marcadores para tests rápidos
pytest -m "not slow"

# 4. Verifica conexiones de red (si aplica)
pytest --disable-warnings
```

#### ❌ Cobertura baja
**Síntoma:** Cobertura < 80%

**Solución:**
```bash
# 1. Ver qué falta
pytest --cov=app --cov-report=term-missing

# 2. Agrega tests para código sin cubrir
# 3. Verifica exclusiones en .coveragerc
# 4. Ejecuta con detalle
pytest --cov=app --cov-report=html
open htmlcov/index.html
```

### 📋 Checklist de Diagnóstico

Antes de reportar un problema, verifica:

- [ ] ¿Estás en el directorio raíz del proyecto?
- [ ] ¿Están instaladas todas las dependencias?
- [ ] ¿FLASK_ENV=testing está configurado?
- [ ] ¿El servidor de desarrollo está corriendo? (si aplica)
- [ ] ¿Las credenciales de test son correctas?
- [ ] ¿PYTHONPATH incluye el directorio raíz?
- [ ] ¿Los tests pasan individualmente?
- [ ] ¿Hay errores en los logs?

---

## 💡 Mejores Prácticas

### ✅ Recomendaciones Esenciales

| Práctica | Prioridad | Impacto | Descripción |
|----------|-----------|----------|-------------|
| **Ejecuta smoke tests primero** | 🔴 Alta | Alto | Verifica API antes de tests complejos |
| **Usa variables de entorno** | 🔴 Alta | Alto | Configura `FLASK_ENV=testing` para aislamiento |
| **Tests independientes** | 🔴 Alta | Alto | Cada test debe poder ejecutarse aisladamente |
| **Usa fixtures** | 🟡 Media | Medio | Comparte setup común con pytest fixtures |
| **Verifica cobertura** | 🟡 Media | Medio | Mantén 80%+ de cobertura en código crítico |
| **Tests descriptivos** | 🟢 Baja | Alto | Nombres que describan qué prueban |
| **Tests rápidos** | 🟡 Media | Medio | Cada test < 1 segundo, suite < 30s |
| **Documentación clara** | 🟢 Baja | Medio | Docstrings en tests complejos |

### 📝 Ejemplo de Test Bien Estructurado

```python
def test_endpoint_health_check():
    """
    Test que verifica que el endpoint de health responde correctamente.
    
    Este test verifica:
    - El endpoint responde con status 200 o 503
    - La respuesta contiene el campo 'status'
    - El formato JSON es válido
    
    Args:
        None
        
    Returns:
        None
        
    Raises:
        AssertionError: Si el endpoint no responde correctamente
    """
    # Arrange: Preparar el entorno
    app = make_app()
    
    # Act: Ejecutar la acción
    with app.test_client() as client:
        response = client.get('/api/health')
    
    # Assert: Verificar el resultado
    assert response.status_code in (200, 503), \
        f"Expected 200 or 503, got {response.status_code}"
    data = response.get_json()
    assert 'status' in data, "Response should contain 'status' field"
    assert isinstance(data['status'], str), "Status should be a string"
```

### 🎯 Patrón AAA (Arrange-Act-Assert)

```python
def test_example_aaa_pattern():
    """
    Ejemplo del patrón AAA (Arrange-Act-Assert)
    
    Este patrón ayuda a estructurar tests de forma clara:
    1. Arrange: Preparar datos y configuración
    2. Act: Ejecutar la acción a testear
    3. Assert: Verificar los resultados
    """
    # Arrange: Preparar
    app = make_app()
    expected_status = 200
    
    # Act: Ejecutar
    with app.test_client() as client:
        response = client.get('/api/health')
    
    # Assert: Verificar
    assert response.status_code == expected_status
    assert response.is_json
```

### 🚫 Anti-Patrones (Evitar)

```python
# ❌ MAL: Test sin documentación
def test1():
    app = make_app()
    c = app.test_client()
    r = c.get('/api/health')
    assert r.status_code == 200

# ❌ MAL: Test dependiente de otros
def test_second():
    # Depende de test_first ejecutarse antes
    assert global_variable == "set_by_first_test"

# ❌ MAL: Test lento (> 1 segundo)
def test_slow():
    time.sleep(5)  # Demasiado lento
    assert True

# ✅ BIEN: Test bien estructurado
def test_health_endpoint_returns_valid_status():
    """Test que verifica respuesta válida del endpoint de health"""
    app = make_app()
    with app.test_client() as client:
        response = client.get('/api/health')
        assert response.status_code in (200, 503)
        assert 'status' in response.get_json()
```

---

## 📚 Recursos Adicionales

### 📖 Documentación Interna

| Documento | Descripción | Tipo |
|-----------|-------------|------|
| **[README Principal](./README.md)** | Documentación completa del sistema | 📘 Guía principal |
| **[Guía de Uso](./Documentation/USAGE_GUIDE.md)** | Cómo usar los tests paso a paso | 🚀 Tutorial |
| **[Documentación Técnica](./Documentation/TECHNICAL_DOCS.md)** | Detalles técnicos y arquitectura | ⚙️ Técnica |
| **[Guía de Contribución](./Documentation/CONTRIBUTING.md)** | Cómo contribuir nuevos tests | ✏️ Contribución |
| **[Documentation Index](./Documentation/index.md)** | Índice de documentación | 📋 Índice |

### 🔗 Recursos Externos

| Recurso | Descripción | Enlace |
|---------|-------------|--------|
| **pytest** | Framework de testing Python | [Documentación oficial](https://docs.pytest.org/) |
| **Flask Testing** | Guía de testing con Flask | [Flask Testing Guide](https://flask.palletsprojects.com/en/latest/testing/) |
| **Node.js Testing** | Mejores prácticas Node.js | [Node.js Testing](https://nodejs.org/en/docs/guides/testing/) |
| **Python Testing** | Mejores prácticas Python | [Real Python](https://realpython.com/python-testing/) |

---

## 🎯 Quick Start

### 🚀 Para Empezar Rápido

| Paso | Acción | Documentación |
|------|--------|---------------|
| **1** | Entender el sistema | [README Principal](./README.md) |
| **2** | Primeros pasos | [Guía de Uso](./Documentation/USAGE_GUIDE.md) |
| **3** | Detalles avanzados | [Documentación Técnica](./Documentation/TECHNICAL_DOCS.md) |

### ✏️ Para Contribuir

| Paso | Acción | Documentación |
|------|--------|---------------|
| **1** | Leer guía de contribución | [Guía de Contribución](./Documentation/CONTRIBUTING.md) |
| **2** | Revisar estándares | Ver sección de mejores prácticas |
| **3** | Enviar cambios | Seguir checklist de PR |

---

## 🔄 Workflows de Testing

### Flujo de Desarrollo con Tests

```
┌─────────────────────────────────────────────────────────┐
│                    DESARROLLO CON TESTS                  │
└─────────────────────────────────────────────────────────┘
                          │
                          ▼
        ┌─────────────────────────────────┐
        │  1. Escribir código             │
        └─────────────────────────────────┘
                          │
                          ▼
        ┌─────────────────────────────────┐
        │  2. Ejecutar smoke tests         │
        │     pytest test_api_smoke.py     │
        └─────────────────────────────────┘
                          │
                          ▼
        ┌─────────────────────────────────┐
        │  3. ¿Tests pasan?               │
        └─────────────────────────────────┘
                  │              │
            SÍ    │              │    NO
                  │              │
                  ▼              ▼
    ┌──────────────────┐  ┌──────────────────┐
    │ 4. Ejecutar      │  │ 4. Revisar error  │
    │    todos tests   │  │    y corregir     │
    └──────────────────┘  └──────────────────┘
                  │              │
                  │              │
                  ▼              │
    ┌──────────────────┐         │
    │ 5. Ver cobertura │         │
    │    --cov=app     │         │
    └──────────────────┘         │
                  │              │
                  │              │
                  ▼              │
    ┌──────────────────┐         │
    │ 6. Commit & Push │         │
    └──────────────────┘         │
                  │              │
                  └──────────────┘
                          │
                          ▼
              ┌───────────────────────┐
              │  CI/CD ejecuta tests  │
              └───────────────────────┘
```

### Flujo de Debug de Tests

```
┌─────────────────────────────────────────┐
│         DEBUG DE TEST FALLIDO          │
└─────────────────────────────────────────┘
                  │
                  ▼
    ┌─────────────────────────────┐
    │ 1. Ejecutar test específico │
    │    pytest test.py::test_x -v │
    └─────────────────────────────┘
                  │
                  ▼
    ┌─────────────────────────────┐
    │ 2. Ver output detallado     │
    │    pytest -vv -s test.py    │
    └─────────────────────────────┘
                  │
                  ▼
    ┌─────────────────────────────┐
    │ 3. Analizar traceback       │
    │    Identificar línea error   │
    └─────────────────────────────┘
                  │
                  ▼
    ┌─────────────────────────────┐
    │ 4. Ejecutar con debugger     │
    │    pytest --pdb test.py     │
    └─────────────────────────────┘
                  │
                  ▼
    ┌─────────────────────────────┐
    │ 5. Corregir código          │
    └─────────────────────────────┘
                  │
                  ▼
    ┌─────────────────────────────┐
    │ 6. Re-ejecutar test         │
    │    Verificar que pasa       │
    └─────────────────────────────┘
```

## 🎯 Casos de Uso Avanzados

### Caso 1: Pre-commit Hook

```bash
# Agregar a .git/hooks/pre-commit
#!/bin/bash
pytest Tests/test_api_smoke.py -v
if [ $? -ne 0 ]; then
    echo "Tests failed. Commit aborted."
    exit 1
fi
```

### Caso 2: CI/CD Pipeline

```yaml
# .github/workflows/tests.yml
name: Tests
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Run tests
        run: |
          pip install -r requirements.txt
          pytest --cov=app --cov-report=xml
      - name: Upload coverage
        uses: codecov/codecov-action@v2
```

### Caso 3: Test Selectivo por Cambios

```bash
# Ejecutar solo tests relacionados con cambios
git diff --name-only | grep -E '\.(py)$' | xargs pytest -k
```

### Caso 4: Performance Monitoring

```bash
# Identificar tests lentos
pytest --durations=10 --durations-min=1.0
```

## 📊 Dashboard de Métricas

### Métricas de Ejecución

| Métrica | Valor Actual | Objetivo | Tendencia |
|---------|--------------|----------|-----------|
| **Tests totales** | 19+ | 20+ | 📈 |
| **Tasa de éxito** | 100% | 100% | ✅ |
| **Tiempo promedio** | < 30s | < 30s | ✅ |
| **Cobertura** | En progreso | 80%+ | 📈 |
| **Tests por día** | Variable | 5+ | 📊 |

### Distribución de Tests

```
Smoke Tests:     ████████░░░░░░░░░░░░ 10% (2 tests)
Auth Tests:      ████████░░░░░░░░░░░░ 10% (2 tests)
Unit Tests:      ████████████████████ 50% (10+ tests)
Integration:     ████████████░░░░░░░░ 30% (5+ tests)
```

## 🛠️ Herramientas y Utilidades

### Scripts de Utilidad

| Script | Descripción | Uso |
|--------|-------------|-----|
| `pytest --cov=app` | Generar cobertura | Análisis de cobertura |
| `pytest --durations=10` | Identificar tests lentos | Optimización |
| `pytest -n auto` | Ejecución paralela | Performance |
| `pytest --lf` | Solo tests fallidos | Debug rápido |
| `pytest --profile` | Profiling de tests | Análisis de performance |

### Integraciones

- ✅ **GitHub Actions:** CI/CD automático
- ✅ **Codecov:** Reporte de cobertura
- ✅ **Coveralls:** Alternativa de cobertura
- ✅ **Travis CI:** CI/CD legacy support
- ✅ **Jenkins:** CI/CD enterprise

## 📝 Información del Documento

| Métrica | Valor |
|---------|-------|
| **Total de archivos** | 13 (2 tests principales + 6 scripts + 5 documentación) |
| **Última actualización** | 2025-10-29 |
| **Versión del índice** | 5.1 (Optimizado con navegación visual) |
| **Próxima revisión** | 2025-11-29 |
| **Mantenido por** | Equipo de Desarrollo |

### 📋 Changelog

#### v5.3 (2025-10-29)
- ✅ Agregada sección Quick Wins para inicio rápido
- ✅ Actualizada tabla de contenidos con nuevas secciones
- ✅ Mejorada navegación y organización visual
- ✅ Optimizado formato general del documento

#### v5.2 (2025-10-29)
- ✅ Agregados diagramas visuales de flujos
- ✅ Agregada sección de anti-patrones con ejemplos
- ✅ Agregada sección de seguridad en tests
- ✅ Agregado roadmap y próximos pasos
- ✅ Expandido con casos de uso avanzados

#### v5.1 (2025-10-29)
- ✅ Agregado header visual con badges
- ✅ Mejorada navegación con búsqueda por caso de uso
- ✅ Agregada tabla de información del documento
- ✅ Mejorado formato visual de secciones clave
- ✅ Optimizada estructura de navegación rápida

#### v5.0 (2025-10-29)
- ✅ Agregada sección de atajos y comandos rápidos
- ✅ Agregado glosario completo de términos
- ✅ Agregados patrones comunes de testing con ejemplos
- ✅ Agregada sección de debugging avanzado
- ✅ Agregada integración con IDEs (VS Code, PyCharm, Emacs)
- ✅ Agregado checklist de calidad pre-commit
- ✅ Agregados ejemplos de flujos completos paso a paso
- ✅ Agregada integración con Git hooks
- ✅ Agregados scripts de reportes automatizados
- ✅ Expandido best practices checklist

#### v4.0 (2025-10-29)
- ✅ Agregada tabla de contenidos completa
- ✅ Corregido frontmatter
- ✅ Consolidados comandos duplicados
- ✅ Mejorada navegación con enlaces internos
- ✅ Optimizada estructura general

#### v3.0 (2025-10-29)
- ✅ Agregado resumen ejecutivo mejorado con métricas
- ✅ Agregados workflows visuales
- ✅ Agregados casos de uso avanzados
- ✅ Agregado dashboard de métricas
- ✅ Mejorada sección de troubleshooting
- ✅ Agregados anti-patrones
- ✅ Mejorada documentación de comandos

#### v2.0 (2025-10-29)
- ✅ Agregada documentación completa
- ✅ Agregados ejemplos de código
- ✅ Mejorada estructura

#### v1.0 (2025-10-29)
- ✅ Versión inicial

---

## 🎓 Aprendizaje Progresivo

### 👶 Nivel Principiante

1. **Ejecutar tests básicos**
   ```bash
   pytest test_api_smoke.py -v
   ```

2. **Entender la salida**
   - `PASSED` = Test exitoso
   - `FAILED` = Test falló
   - `SKIPPED` = Test omitido

3. **Leer documentación básica**
   - [README Principal](./README.md)
   - [Guía de Uso](./Documentation/USAGE_GUIDE.md)

### 🧑 Nivel Intermedio

1. **Escribir tests simples**
   ```python
   def test_simple():
       app = make_app()
       with app.test_client() as c:
           rv = c.get('/api/health')
           assert rv.status_code == 200
   ```

2. **Usar fixtures**
   ```python
   @pytest.fixture
   def client():
       app = make_app()
       return app.test_client()
   ```

3. **Verificar cobertura**
   ```bash
   pytest --cov=app --cov-report=term-missing
   ```

### 🧙 Nivel Avanzado

1. **Mocks y stubs**
   ```python
   @patch('app.external_api.call')
   def test_with_mock(mock_call):
       mock_call.return_value = {'status': 'ok'}
       # Test code
   ```

2. **Parametrización**
   ```python
   @pytest.mark.parametrize("input,expected", [
       (100, "$100.00"),
       (1000, "$1,000.00"),
   ])
   def test_format(input, expected):
       assert format_currency(input) == expected
   ```

3. **Fixtures avanzadas**
   ```python
   @pytest.fixture(scope="module")
   def db_session():
       # Setup database
       yield session
       # Teardown
   ```

## 🏆 Best Practices Checklist

### ✅ Antes de Commit

- [ ] Todos los tests pasan: `pytest`
- [ ] Cobertura no disminuye: `pytest --cov=app`
- [ ] Tests nuevos tienen nombres descriptivos
- [ ] Tests nuevos están documentados
- [ ] No hay warnings de pytest
- [ ] Tests son rápidos (< 1s cada uno)
- [ ] Tests son independientes

### ✅ Al Escribir Tests

- [ ] Nombre descriptivo: `test_what_when_then`
- [ ] Docstring explicando qué testea
- [ ] Patrón AAA (Arrange-Act-Assert)
- [ ] Assertions claras con mensajes
- [ ] No depende de otros tests
- [ ] Limpia después (fixtures/teardown)

### ✅ Revisión de Código

- [ ] Test es necesario y útil
- [ ] Test es claro y mantenible
- [ ] Test es rápido
- [ ] Test cubre casos edge
- [ ] Test tiene buen nombre

## 📞 Soporte y Contacto

### 🆘 ¿Necesitas Ayuda?

1. **Consulta la documentación**
   - [README Principal](./README.md)
   - [Guía de Uso](./Documentation/USAGE_GUIDE.md)
   - [Troubleshooting](#-troubleshooting)

2. **Revisa ejemplos**
   - [Ejemplos de código](#-ejemplo-de-test-bien-estructurado)
   - [Anti-patrones](#-anti-patrones-evitar)

3. **Busca en recursos externos**
   - [pytest Documentation](https://docs.pytest.org/)
   - [Flask Testing Guide](https://flask.palletsprojects.com/en/latest/testing/)

---

## 📋 FAQ - Preguntas Frecuentes

### ❓ ¿Cómo ejecuto solo los tests que fallaron?

```bash
pytest --lf  # last failed
```

### ❓ ¿Cómo veo qué tests son más lentos?

```bash
pytest --durations=10
```

### ❓ ¿Cómo ejecuto tests en paralelo?

```bash
pytest -n auto  # Detecta CPU automáticamente
pytest -n 4     # 4 procesos paralelos
```

### ❓ ¿Cómo salto tests lentos?

```bash
pytest -m "not slow"
```

### ❓ ¿Cómo ejecuto un test específico?

```bash
pytest test_api_smoke.py::test_health_endpoint
```

### ❓ ¿Cómo veo cobertura de una función específica?

```bash
pytest --cov=app.function_name --cov-report=term-missing
```

### ❓ ¿Cómo ejecuto tests con output detallado?

```bash
pytest -vv -s  # Muy verbose + mostrar prints
```

### ❓ ¿Cómo ejecuto tests marcados?

```bash
pytest -m smoke      # Solo tests marcados como smoke
pytest -m "not slow" # Todos excepto slow
```

### ❓ ¿Cómo veo el código que falta en cobertura?

```bash
pytest --cov=app --cov-report=html
open htmlcov/index.html
```

### ❓ ¿Cómo ejecuto tests con debugger?

```bash
pytest --pdb  # Entra en debugger en fallos
```

## 🎨 Templates de Tests

### Template: Test de Endpoint Básico

```python
"""
Template para test de endpoint básico
"""
import pytest
from app import create_app

def make_app():
    """Factory para crear app de test"""
    import os
    os.environ.setdefault('FLASK_ENV', 'testing')
    return create_app('testing')

def test_endpoint_basico():
    """
    Test que verifica respuesta básica de endpoint
    
    TODO: Reemplazar '/api/endpoint' con tu endpoint
    """
    # Arrange
    app = make_app()
    expected_status = 200
    
    # Act
    with app.test_client() as client:
        response = client.get('/api/endpoint')
    
    # Assert
    assert response.status_code == expected_status
    assert response.is_json
    data = response.get_json()
    assert data is not None
```

### Template: Test con Autenticación

```python
"""
Template para test con autenticación
"""
import pytest
from app import create_app

def make_app():
    import os
    os.environ.setdefault('FLASK_ENV', 'testing')
    return create_app('testing')

def login_get_token(client):
    """Helper para obtener token"""
    response = client.post('/api/auth/login', 
                          json={'username': 'admin', 'password': 'admin123'})
    assert response.status_code == 200
    return response.get_json()['token']

def test_endpoint_con_auth():
    """
    Test que verifica endpoint protegido con autenticación
    
    TODO: Reemplazar '/api/protected' con tu endpoint protegido
    """
    # Arrange
    app = make_app()
    
    # Act - Sin autenticación (debe fallar)
    with app.test_client() as client:
        response_no_auth = client.get('/api/protected')
        assert response_no_auth.status_code in (401, 403)
    
    # Act - Con autenticación (debe pasar)
    with app.test_client() as client:
        token = login_get_token(client)
        response_auth = client.get('/api/protected',
                                   headers={'Authorization': f'Bearer {token}'})
        assert response_auth.status_code == 200
```

### Template: Test con Fixture

```python
"""
Template para test usando fixtures
"""
import pytest
from app import create_app

@pytest.fixture
def app():
    """Fixture para app de test"""
    import os
    os.environ.setdefault('FLASK_ENV', 'testing')
    return create_app('testing')

@pytest.fixture
def client(app):
    """Fixture para test client"""
    return app.test_client()

def test_con_fixture(client):
    """
    Test usando fixtures de app y client
    
    Ventajas:
    - Código más limpio
    - Reutilizable
    - Mejor organización
    """
    # Arrange
    expected_status = 200
    
    # Act
    response = client.get('/api/health')
    
    # Assert
    assert response.status_code == expected_status
```

### Template: Test Parametrizado

```python
"""
Template para test parametrizado
"""
import pytest
from app.utils import format_currency

@pytest.mark.parametrize("input_value,expected_output", [
    (100, "$100.00"),
    (1000, "$1,000.00"),
    (0, "$0.00"),
    (100.5, "$100.50"),
    (-100, "-$100.00"),
])
def test_format_currency_parametrizado(input_value, expected_output):
    """
    Test parametrizado que prueba múltiples casos
    
    Ventajas:
    - Un test para múltiples casos
    - Fácil agregar nuevos casos
    - Output claro por caso
    """
    result = format_currency(input_value)
    assert result == expected_output
```

### Template: Test con Mock

```python
"""
Template para test con mocks
"""
from unittest.mock import patch, Mock
import pytest
from app import create_app

def make_app():
    import os
    os.environ.setdefault('FLASK_ENV', 'testing')
    return create_app('testing')

@patch('app.external_service.api_call')
def test_con_mock_externo(mock_api_call):
    """
    Test que usa mock para servicio externo
    
    Ventajas:
    - No depende de servicios externos
    - Tests rápidos y confiables
    - Control total del comportamiento
    """
    # Arrange - Configurar mock
    mock_api_call.return_value = {'status': 'ok', 'data': 'test'}
    
    # Act
    app = make_app()
    with app.test_client() as client:
        response = client.get('/api/endpoint')
    
    # Assert
    assert response.status_code == 200
    mock_api_call.assert_called_once()
```

## 🚀 Performance Optimization

### Técnicas de Optimización

#### 1. Ejecución Paralela

```bash
# Instalar pytest-xdist
pip install pytest-xdist

# Ejecutar en paralelo
pytest -n auto        # Auto-detecta CPU
pytest -n 4           # 4 procesos
pytest -n 8           # 8 procesos
```

#### 2. Tests Rápidos Primero

```bash
# Ejecutar tests rápidos primero
pytest --ff  # failed first, luego otros
```

#### 3. Skip Tests Lentos

```python
# Marcar tests lentos
@pytest.mark.slow
def test_slow_operation():
    # Test que tarda mucho
    pass

# Ejecutar sin tests lentos
pytest -m "not slow"
```

#### 4. Caché de Fixtures

```python
@pytest.fixture(scope="module")  # Cache por módulo
def expensive_setup():
    # Setup costoso que se ejecuta una vez
    return expensive_operation()

@pytest.fixture(scope="session")  # Cache para toda la sesión
def shared_resource():
    # Recurso compartido entre todos los tests
    return shared_setup()
```

#### 5. Identificar Tests Lentos

```bash
# Ver tests más lentos
pytest --durations=10 --durations-min=1.0

# Ver distribución de tiempos
pytest --durations=0
```

## 🔍 Comparativa de Tipos de Tests

### Tabla Comparativa

| Tipo | Velocidad | Aislamiento | Complejidad | Cuándo Usar |
|------|----------|-------------|------------|-------------|
| **Unit Tests** | ⚡⚡⚡ Muy rápido | ✅✅✅ Alto | 🟢 Baja | Funciones individuales |
| **Integration Tests** | ⚡⚡ Medio | ✅✅ Medio | 🟡 Media | Interacción entre componentes |
| **Smoke Tests** | ⚡⚡⚡ Muy rápido | ✅✅✅ Alto | 🟢 Baja | Verificación básica |
| **E2E Tests** | ⚡ Lento | ✅ Bajo | 🔴 Alta | Flujos completos |
| **API Tests** | ⚡⚡ Medio | ✅✅ Medio | 🟡 Media | Endpoints REST |

### Cuándo Usar Cada Tipo

```
┌─────────────────────────────────────────────────┐
│              DECISIÓN DE TIPO DE TEST            │
└─────────────────────────────────────────────────┘
                    │
                    ▼
        ┌───────────────────────┐
        │ ¿Es función simple?   │
        └───────────────────────┘
              │            │
          SÍ  │            │  NO
              │            │
              ▼            ▼
    ┌─────────────┐  ┌─────────────┐
    │ Unit Test   │  │ ¿Interacción│
    │             │  │ componentes?│
    └─────────────┘  └─────────────┘
                            │
                    SÍ      │      NO
                            │
                            ▼
                    ┌─────────────┐
                    │ Integration │
                    │ Test        │
                    └─────────────┘
```

## 🎯 Tips y Tricks Avanzados

### Tip 1: Test Selectivo por Nombre

```bash
# Ejecutar tests que contengan "health"
pytest -k "health"

# Ejecutar tests que NO contengan "slow"
pytest -k "not slow"

# Múltiples condiciones
pytest -k "health or auth"
pytest -k "health and not slow"
```

### Tip 2: Capturar Output

```bash
# Capturar output en archivo
pytest --tb=short > test_output.txt

# Capturar con cobertura
pytest --cov=app --cov-report=html > coverage.txt
```

### Tip 3: Ejecutar Tests Modificados

```bash
# Solo tests de archivos modificados
git diff --name-only | grep test | xargs pytest

# Tests relacionados con cambios
git diff master --name-only | xargs pytest -k
```

### Tip 4: Timeout en Tests

```bash
# Instalar pytest-timeout
pip install pytest-timeout

# Timeout global
pytest --timeout=10

# Timeout por test
pytest --timeout=5 --timeout-method=thread
```

### Tip 5: Re-ejecutar Último Comando

```bash
# Re-ejecutar último pytest
!!  # En bash/zsh

# O configurar alias
alias pt='pytest'
alias ptv='pytest -v'
alias ptc='pytest --cov=app'
```

### Tip 6: Verbose Output Personalizado

```python
# En conftest.py
import pytest

def pytest_configure(config):
    """Configuración personalizada"""
    config.addinivalue_line(
        "markers", "slow: marks tests as slow (deselect with '-m \"not slow\"')"
    )
```

### Tip 7: Test con Context Manager

```python
from contextlib import contextmanager

@contextmanager
def test_database():
    """Context manager para base de datos de test"""
    db = create_test_db()
    try:
        yield db
    finally:
        db.cleanup()

def test_with_context():
    with test_database() as db:
        # Test code
        pass
```

## 📊 Matriz de Decisión: ¿Qué Test Crear?

### Decision Tree

```
¿Qué quieres testear?
│
├─ Función individual
│  └─> Unit Test
│
├─ Interacción entre componentes
│  └─> Integration Test
│
├─ Endpoint API
│  └─> API Test
│
├─ Flujo completo usuario
│  └─> E2E Test
│
└─ Verificación rápida
   └─> Smoke Test
```

### Checklist de Decisión

Para decidir qué tipo de test crear, responde:

- [ ] ¿Es una función simple y aislada? → Unit Test
- [ ] ¿Interactúa con otros componentes? → Integration Test
- [ ] ¿Es un endpoint de API? → API Test
- [ ] ¿Necesito verificar flujo completo? → E2E Test
- [ ] ¿Solo verificación básica? → Smoke Test

## 🔄 Migración y Actualización

### Actualizar Tests Existentes

#### Paso 1: Identificar Tests Obsoletos

```bash
# Buscar tests que no se ejecutan
pytest --collect-only | grep -i "skip"

# Buscar tests que fallan siempre
pytest --lf  # Ver últimos fallidos
```

#### Paso 2: Refactorizar Tests

```python
# ❌ ANTES: Test sin estructura
def test1():
    app = make_app()
    c = app.test_client()
    r = c.get('/api/health')
    assert r.status_code == 200

# ✅ DESPUÉS: Test bien estructurado
def test_health_endpoint_returns_200():
    """Test que verifica respuesta del endpoint de health"""
    app = make_app()
    with app.test_client() as client:
        response = client.get('/api/health')
        assert response.status_code == 200
        assert response.is_json
```

#### Paso 3: Agregar Cobertura

```bash
# Ver qué falta en cobertura
pytest --cov=app --cov-report=term-missing

# Agregar tests para código sin cubrir
# (usar templates anteriores)
```

## 🎓 Recursos de Aprendizaje

### 📚 Libros Recomendados

1. **"Python Testing with pytest"** - Brian Okken
   - Guía completa de pytest
   - Mejores prácticas
   - Ejemplos prácticos

2. **"Test-Driven Development"** - Kent Beck
   - Metodología TDD
   - Red-Green-Refactor
   - Ejemplos en Python

### 🎥 Videos y Tutoriales

- [pytest Official Tutorial](https://docs.pytest.org/en/stable/getting-started.html)
- [Real Python Testing](https://realpython.com/python-testing/)
- [Flask Testing Guide](https://flask.palletsprojects.com/en/latest/testing/)

### 🌐 Comunidades

- [pytest GitHub](https://github.com/pytest-dev/pytest)
- [Python Testing Slack](https://python-testing.slack.com)
- [Stack Overflow - pytest](https://stackoverflow.com/questions/tagged/pytest)

### 📦 Extensiones Útiles

```bash
# Instalar extensiones útiles
pip install pytest-cov        # Cobertura
pip install pytest-xdist      # Paralelización
pip install pytest-timeout    # Timeouts
pip install pytest-mock      # Mocks mejorados
pip install pytest-html      # Reportes HTML
pip install pytest-json      # Reportes JSON
```

## 🎁 Bonus: Scripts Útiles

### Script: Ejecutar Tests con Notificación

```bash
#!/bin/bash
# notify-test.sh
pytest --cov=app
if [ $? -eq 0 ]; then
    notify-send "Tests Passed" "All tests passed successfully!"
else
    notify-send "Tests Failed" "Some tests failed. Check output."
fi
```

### Script: Test Watcher

```bash
#!/bin/bash
# watch-tests.sh
while true; do
    clear
    echo "Running tests..."
    pytest test_api_smoke.py -v
    sleep 5
done
```

### Script: Test Coverage Trend

```bash
#!/bin/bash
# coverage-trend.sh
pytest --cov=app --cov-report=term-missing | \
    grep "TOTAL" | \
    awk '{print strftime("%Y-%m-%d %H:%M:%S"), $0}' >> coverage.log
```

---

## ⌨️ Atajos y Comandos Rápidos

### 🚀 Comandos Más Usados

| Comando | Descripción | Cuándo usar |
|---------|-------------|-------------|
| `pytest` | Ejecutar todos los tests | Desarrollo diario |
| `pytest -v` | Verbose output | Debugging |
| `pytest -x` | Parar en primer error | Desarrollo rápido |
| `pytest --lf` | Solo tests fallidos | Después de un error |
| `pytest -k "test_name"` | Filtrar por nombre | Test específico |
| `pytest -m smoke` | Solo smoke tests | Verificación rápida |
| `pytest --cov` | Con cobertura | Antes de commit |

### 🎯 Aliases Útiles (Agregar a `.bashrc` o `.zshrc`)

```bash
# Tests rápidos
alias pt='pytest'
alias ptv='pytest -v'
alias pts='pytest test_api_smoke.py -v'
alias pta='pytest test_auth_products.py -v'

# Tests con cobertura
alias ptc='pytest --cov=app --cov-report=term-missing'

# Tests fallidos
alias ptf='pytest --lf'

# Tests en paralelo
alias ptp='pytest -n auto'
```

---

## 📚 Glosario de Términos

### Terminología de Testing

| Término | Definición |
|---------|-----------|
| **Smoke Test** | Test rápido que verifica que lo básico funciona |
| **Unit Test** | Test de una función o método individual |
| **Integration Test** | Test que verifica interacción entre componentes |
| **Fixture** | Función que prepara el entorno para tests |
| **Mock** | Objeto simulado que reemplaza dependencias reales |
| **Coverage** | Porcentaje de código ejecutado por tests |
| **Test Suite** | Colección de todos los tests |
| **Assertion** | Verificación que debe ser verdadera |
| **Test Runner** | Herramienta que ejecuta tests (pytest) |
| **Test Client** | Cliente simulado para testing de APIs |
| **CI/CD** | Integración Continua / Despliegue Continuo |
| **TDD** | Test-Driven Development (desarrollo guiado por tests) |
| **BDD** | Behavior-Driven Development |
| **AAA Pattern** | Arrange-Act-Assert (patrón de estructura de tests) |

---

## 🎨 Patrones Comunes de Testing

### Patrón AAA (Arrange-Act-Assert)

```python
def test_example():
    # Arrange: Preparar el entorno
    app = make_app()
    client = app.test_client()
    
    # Act: Ejecutar la acción
    response = client.get('/api/health')
    
    # Assert: Verificar el resultado
    assert response.status_code == 200
    assert 'status' in response.get_json()
```

### Patrón Given-When-Then (BDD)

```python
def test_user_login():
    """
    Given: Un usuario válido
    When: Intenta hacer login
    Then: Debe recibir un token válido
    """
    app = make_app()
    with app.test_client() as client:
        response = client.post('/api/auth/login', json={
            'username': 'admin',
            'password': 'admin123'
        })
        assert response.status_code == 200
        assert 'token' in response.get_json()
```

### Patrón de Fixtures Compartidas

```python
# conftest.py
@pytest.fixture
def authenticated_client():
    """Client con autenticación preconfigurada"""
    app = make_app()
    client = app.test_client()
    # Login y obtener token
    token = login_get_token(client)
    client.environ_base['HTTP_AUTHORIZATION'] = f'Bearer {token}'
    return client

# test_file.py
def test_protected_endpoint(authenticated_client):
    """Test que usa el cliente autenticado"""
    response = authenticated_client.get('/api/products')
    assert response.status_code == 200
```

### Patrón de Test Parametrizado

```python
@pytest.mark.parametrize("endpoint,expected_status", [
    ('/api/health', 200),
    ('/api/products', 401),  # Sin auth
    ('/api/invalid', 404),
])
def test_endpoints_status(endpoint, expected_status):
    """Test múltiples endpoints con diferentes resultados esperados"""
    app = make_app()
    with app.test_client() as client:
        response = client.get(endpoint)
        assert response.status_code == expected_status
```

---

## 🔍 Debugging Avanzado

### Técnicas de Debugging

#### 1. Debugging con pdb

```python
def test_complex_scenario():
    app = make_app()
    with app.test_client() as client:
        response = client.get('/api/products')
        import pdb; pdb.set_trace()  # Breakpoint
        assert response.status_code == 200
```

#### 2. Debugging con print statements

```python
def test_with_debug_output():
    app = make_app()
    with app.test_client() as client:
        response = client.get('/api/products')
        print(f"Status: {response.status_code}")
        print(f"Headers: {response.headers}")
        print(f"Data: {response.get_json()}")
        assert response.status_code == 200
```

#### 3. Debugging con pytest-sugar

```bash
pip install pytest-sugar
pytest --tb=short -v
```

#### 4. Capturar output de tests

```python
def test_with_captured_output(capsys):
    """Captura output de print statements"""
    print("Debug message")
    captured = capsys.readouterr()
    assert "Debug message" in captured.out
```

---

## 🛠️ Integración con IDEs

### Visual Studio Code

#### Configuración `.vscode/settings.json`

```json
{
    "python.testing.pytestEnabled": true,
    "python.testing.unittestEnabled": false,
    "python.testing.pytestArgs": [
        "-v",
        "--cov=app",
        "--cov-report=term-missing"
    ],
    "python.testing.cwd": "${workspaceFolder}",
    "python.testing.autoTestDiscoverOnSaveEnabled": true
}
```

#### Launch Configuration `.vscode/launch.json`

```json
{
    "version": "0.2.0",
    "configurations": [
        {
            "name": "Python: Pytest",
            "type": "python",
            "request": "launch",
            "module": "pytest",
            "args": [
                "-v",
                "${file}"
            ],
            "console": "integratedTerminal",
            "env": {
                "FLASK_ENV": "testing"
            }
        }
    ]
}
```

### PyCharm

#### Configuración de Test Runner

1. **Settings → Tools → Python Integrated Tools**
   - Test runner: `pytest`
   - Default test runner: `pytest`

2. **Run Configuration**
   - Script: `pytest`
   - Parameters: `-v --cov=app`
   - Environment variables: `FLASK_ENV=testing`

### Emacs

#### Configuración con `use-package`

```elisp
(use-package python-pytest
  :ensure t
  :config
  (setq python-pytest-executable "pytest")
  (setq python-pytest-arguments '("-v" "--cov=app")))
```

---

## ✅ Checklist de Calidad Pre-Commit

### Antes de hacer commit, verifica:

#### 📋 Funcionalidad
- [ ] Todos los tests pasan: `pytest`
- [ ] Smoke tests pasan: `pytest test_api_smoke.py`
- [ ] Tests nuevos pasan individualmente
- [ ] No hay tests que fallen en el nuevo código

#### 📊 Cobertura
- [ ] Cobertura no disminuyó: `pytest --cov=app`
- [ ] Código nuevo tiene tests: verificar archivos modificados
- [ ] Cobertura > 80% en código crítico

#### 🧹 Calidad de Código
- [ ] Tests siguen convenciones de nombres
- [ ] Tests tienen docstrings descriptivos
- [ ] No hay código comentado innecesario
- [ ] Tests son independientes (no dependen de otros)

#### 📝 Documentación
- [ ] Tests nuevos están documentados
- [ ] Cambios importantes están reflejados en docs
- [ ] Ejemplos de uso están actualizados

#### ⚡ Performance
- [ ] Tests ejecutan rápidamente (< 30s suite completa)
- [ ] No hay tests lentos sin marcar como `@pytest.mark.slow`
- [ ] Tests no hacen llamadas innecesarias a APIs externas

#### 🔒 Seguridad
- [ ] Tests de autenticación pasan
- [ ] Tests de autorización pasan
- [ ] No hay credenciales hardcodeadas en tests

---

## 🎯 Ejemplos de Flujos Completos

### Flujo: Agregar un Nuevo Test

```bash
# 1. Crear archivo de test
touch test_new_feature.py

# 2. Escribir test básico
cat > test_new_feature.py << 'EOF'
def test_new_feature():
    app = make_app()
    with app.test_client() as client:
        response = client.get('/api/new-feature')
        assert response.status_code == 200
EOF

# 3. Ejecutar test
pytest test_new_feature.py -v

# 4. Verificar cobertura
pytest --cov=app test_new_feature.py

# 5. Commit
git add test_new_feature.py
git commit -m "Add test for new feature"
```

### Flujo: Debugging de Test Fallido

```bash
# 1. Identificar test fallido
pytest -v  # Ver qué test falla

# 2. Ejecutar solo el test fallido
pytest test_file.py::test_name -v

# 3. Ejecutar con más detalle
pytest test_file.py::test_name -vv -s

# 4. Ejecutar con debugger
pytest test_file.py::test_name --pdb

# 5. Ver traceback completo
pytest test_file.py::test_name --tb=long
```

### Flujo: Optimización de Tests Lentos

```bash
# 1. Identificar tests lentos
pytest --durations=10

# 2. Ejecutar en paralelo
pytest -n auto

# 3. Verificar tiempo de cada test
pytest --durations=0

# 4. Marcar tests lentos
# Agregar @pytest.mark.slow a tests que tardan > 1s

# 5. Ejecutar sin tests lentos
pytest -m "not slow"
```

---

## 🔄 Integración con Git Hooks

### Pre-commit Hook

Crear `.git/hooks/pre-commit`:

```bash
#!/bin/bash
# Pre-commit hook para ejecutar tests

echo "Running tests before commit..."
pytest test_api_smoke.py -v

if [ $? -ne 0 ]; then
    echo "Tests failed! Commit aborted."
    exit 1
fi

echo "All smoke tests passed!"
exit 0
```

### Pre-push Hook

Crear `.git/hooks/pre-push`:

```bash
#!/bin/bash
# Pre-push hook para ejecutar suite completa

echo "Running full test suite before push..."
pytest --cov=app

if [ $? -ne 0 ]; then
    echo "Tests failed! Push aborted."
    exit 1
fi

echo "All tests passed! Coverage check..."
# Verificar cobertura mínima
coverage=$(pytest --cov=app --cov-report=term | grep TOTAL | awk '{print $3}' | sed 's/%//')
if (( $(echo "$coverage < 80" | bc -l) )); then
    echo "Coverage below 80%! Current: ${coverage}%"
    exit 1
fi

echo "All checks passed!"
exit 0
```

---

## 📊 Métricas y Reportes Automatizados

### Script de Reporte Diario

```bash
#!/bin/bash
# daily-test-report.sh

DATE=$(date +%Y-%m-%d)
REPORT_FILE="test-reports/report-${DATE}.txt"

mkdir -p test-reports

echo "=== Test Report - ${DATE} ===" > $REPORT_FILE
echo "" >> $REPORT_FILE

# Ejecutar tests y capturar resultados
pytest --cov=app --cov-report=term --durations=10 >> $REPORT_FILE 2>&1

# Enviar reporte (opcional)
# mail -s "Daily Test Report ${DATE}" team@example.com < $REPORT_FILE

echo "Report generated: ${REPORT_FILE}"
```

---

## 🎯 Best Practices Checklist Extendido

### ✅ Estructura de Tests

- [ ] Cada test tiene un nombre descriptivo
- [ ] Cada test verifica una sola cosa
- [ ] Tests son independientes entre sí
- [ ] Tests usan fixtures cuando es apropiado
- [ ] Tests tienen docstrings claros

### ✅ Assertions

- [ ] Assertions son específicas y claras
- [ ] No hay assertions genéricas (`assert True`)
- [ ] Mensajes de error son descriptivos
- [ ] Se verifican tanto casos de éxito como de error

### ✅ Performance

- [ ] Tests individuales corren en < 1 segundo
- [ ] Suite completa corre en < 30 segundos
- [ ] Tests no hacen llamadas de red innecesarias
- [ ] Tests usan mocks para dependencias externas

### ✅ Mantenibilidad

- [ ] Tests son fáciles de entender
- [ ] Código duplicado está en fixtures
- [ ] Tests siguen patrones establecidos
- [ ] Tests están bien organizados por funcionalidad

---

## 🎯 Navegación Rápida

<div align="center">

### 📍 Enlaces Importantes

| 📚 Documentación | 🚀 Guías | ⚙️ Técnico | ✏️ Contribuir |
|:---:|:---:|:---:|:---:|
| [README Principal](./README.md) | [Guía de Uso](./Documentation/USAGE_GUIDE.md) | [Docs Técnicas](./Documentation/TECHNICAL_DOCS.md) | [Contribuir](./Documentation/CONTRIBUTING.md) |

</div>

### 🔍 Búsqueda por Caso de Uso

| Quiero... | Ve a... |
|-----------|---------|
| 🚀 **Empezar rápido** | [Quick Start](#-quick-start) |
| 🧪 **Ejecutar tests** | [Comandos Esenciales](#-comandos-esenciales) |
| 🐛 **Debuggear un test** | [Debugging Avanzado](#-debugging-avanzado) |
| ➕ **Agregar un test** | [Templates de Tests](#-templates-de-tests) |
| 🔧 **Configurar IDE** | [Integración con IDEs](#️-integración-con-ides) |
| ⚠️ **Resolver problemas** | [Troubleshooting](#-troubleshooting) |
| 📊 **Ver métricas** | [Dashboard de Métricas](#-dashboard-de-métricas) |
| ✅ **Verificar calidad** | [Checklist Pre-Commit](#-checklist-de-calidad-pre-commit) |
| 📚 **Aprender términos** | [Glosario](#-glosario-de-términos) |
| 🎯 **Ver patrones** | [Patrones Comunes](#-patrones-comunes-de-testing) |

---

## 🎨 Diagramas Visuales de Flujos

### Flujo de Ejecución de Tests

```
┌─────────────────────────────────────────────────────────┐
│                    Ejecutar Tests                       │
└────────────────────┬────────────────────────────────────┘
                     │
                     ▼
         ┌───────────────────────┐
         │  pytest discover      │
         │  (Buscar tests)        │
         └───────────┬────────────┘
                     │
                     ▼
         ┌───────────────────────┐
         │  Setup & Fixtures     │
         │  (Preparar entorno)   │
         └───────────┬────────────┘
                     │
                     ▼
         ┌───────────────────────┐
         │  Ejecutar Tests       │
         │  (Arrange-Act-Assert) │
         └───────────┬────────────┘
                     │
                     ▼
         ┌───────────────────────┐
         │  Recolectar Resultados│
         │  (Pass/Fail/Skip)     │
         └───────────┬────────────┘
                     │
                     ▼
         ┌───────────────────────┐
         │  Generar Reportes     │
         │  (Terminal/HTML/XML)   │
         └───────────────────────┘
```

### Arquitectura de Testing

```
┌──────────────────────────────────────────────────────────┐
│                    Test Suite                            │
├──────────────┬──────────────┬──────────────┬────────────┤
│  Smoke Tests │ Unit Tests   │ Integration  │  E2E Tests │
│  (2 tests)   │ (10+ tests) │ (5+ tests)   │ (2+ tests)│
└──────┬───────┴──────┬───────┴──────┬───────┴─────┬──────┘
       │             │               │             │
       ▼             ▼               ▼             ▼
┌──────────┐  ┌──────────┐   ┌──────────┐  ┌──────────┐
│  Flask   │  │ Utils    │   │  API     │  │  Full    │
│  Client  │  │ Modules  │   │ Endpoints│  │  Flow    │
└──────────┘  └──────────┘   └──────────┘  └──────────┘
```

---

## ❌ Anti-Patrones Comunes

### ❌ Anti-Patrón 1: Tests Dependientes

```python
# ❌ MAL: Tests que dependen de otros
def test_create_user():
    user = create_user('test')
    assert user.id == 1

def test_get_user():
    user = get_user(1)  # Depende de test_create_user
    assert user.name == 'test'
```

```python
# ✅ BIEN: Tests independientes
def test_create_user():
    user = create_user('test')
    assert user.id is not None
    assert user.name == 'test'

def test_get_user():
    user = create_user('test')  # Setup propio
    retrieved = get_user(user.id)
    assert retrieved.name == 'test'
```

### ❌ Anti-Patrón 2: Tests que no Limpian

```python
# ❌ MAL: Tests que dejan datos
def test_create_product():
    create_product('Test Product', 10.0)
    # No limpia después

def test_list_products():
    products = list_products()
    assert len(products) > 0  # Depende de datos previos
```

```python
# ✅ BIEN: Tests que limpian
@pytest.fixture(autouse=True)
def clean_database():
    """Limpia DB antes y después de cada test"""
    yield
    clean_test_data()

def test_create_product(clean_database):
    product = create_product('Test Product', 10.0)
    assert product.id is not None

def test_list_products(clean_database):
    create_product('Test Product', 10.0)
    products = list_products()
    assert len(products) == 1
```

---

## 🔐 Seguridad en Tests

### Validación de Seguridad

```python
"""
Tests de seguridad para endpoints
"""
import pytest

def test_sql_injection_protection():
    """Test que verifica protección contra SQL injection"""
    app = make_app()
    with app.test_client() as client:
        # Intentar SQL injection
        malicious_input = "'; DROP TABLE users; --"
        response = client.get(f'/api/products?search={malicious_input}')
        # No debe causar error 500
        assert response.status_code != 500
        # Debe ser manejado correctamente
        assert response.status_code in (200, 400, 404)

def test_xss_protection():
    """Test que verifica protección contra XSS"""
    app = make_app()
    with app.test_client() as client:
        # Intentar XSS
        xss_payload = "<script>alert('XSS')</script>"
        response = client.post('/api/products', json={
            'name': xss_payload,
            'price': 10.0
        })
        # El script no debe estar en la respuesta
        assert '<script>' not in response.get_data(as_text=True)
```

---

## 📈 Roadmap y Próximos Pasos

### 🎯 Mejoras Planificadas

| Prioridad | Mejora | Estado | ETA |
|:---------:|:------|:------:|:---:|
| 🔴 Alta | Aumentar cobertura a 85%+ | 🚧 En progreso | Q4 2025 |
| 🟡 Media | Agregar tests E2E completos | 📋 Planificado | Q1 2026 |
| 🟡 Media | Integración con SonarQube | 📋 Planificado | Q1 2026 |
| 🟢 Baja | Tests de performance | 💡 Idea | Q2 2026 |

---

## 📊 Información del Documento

<div align="center">

| Métrica | Valor |
|:-------:|:-----:|
| **📅 Última actualización** | 2025-10-29 |
| **🔢 Versión** | 5.3 |
| **📝 Estado** | Optimizado con quick wins y navegación mejorada |
| **👥 Mantenido por** | Equipo de Desarrollo |
| **📄 Total de líneas** | 2300+ |
| **📚 Secciones** | 50+ |
| **🎯 Objetivo** | Guía completa de testing |

</div>