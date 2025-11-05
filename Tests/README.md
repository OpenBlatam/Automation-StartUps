# Tests - Documentación Completa

**Versión:** 1.0  
**Última actualización:** 2025-10-29  
**Estado:** Activo

---

## 📋 Índice

- [Descripción General](#descripción-general)
- [Estructura del Proyecto](#estructura-del-proyecto)
- [Quick Start](#quick-start)
- [Ejecutar Tests](#ejecutar-tests)
- [Tipos de Tests](#tipos-de-tests)
- [Scripts y Utilidades](#scripts-y-utilidades)
- [Configuración](#configuración)
- [Cobertura de Tests](#cobertura-de-tests)
- [Troubleshooting](#troubleshooting)
- [Contribuir](#contribuir)

---

## 🎯 Descripción General

Este directorio contiene toda la suite de tests para el proyecto, incluyendo:

- ✅ **Tests de integración** para API endpoints
- ✅ **Tests de autenticación** y autorización
- ✅ **Tests unitarios** para utilidades y validadores
- ✅ **Scripts de testing** en Python y JavaScript
- ✅ **Documentación** completa de uso

### Objetivos

- Validar que la API funciona correctamente
- Verificar seguridad y autenticación
- Asegurar calidad de código
- Facilitar desarrollo continuo
- Proporcionar feedback rápido

---

## 📁 Estructura del Proyecto

```
Tests/
├── README.md                    # Este archivo
├── INDEX.md                     # Índice generado automáticamente
│
├── Documentation/               # Documentación detallada
│   └── index.md                # Índice de documentación
│
├── Scripts/                     # Scripts y utilidades de testing
│   ├── __init__.py             # Inicialización del módulo
│   ├── test_utils.py           # Tests de funciones utilitarias
│   ├── test_validators.py      # Tests de validadores
│   ├── apitest.js              # Tests de API en JavaScript
│   ├── validadortest.js        # Tests de validadores en JS
│   ├── setup.js                # Configuración para tests JS
│   └── INDEX.md                # Índice de scripts
│
├── test_api_smoke.py           # Tests básicos de API (smoke tests)
└── test_auth_products.py       # Tests de autenticación y productos
```

---

## 🚀 Quick Start

### Prerrequisitos

```bash
# Python 3.8+
python --version

# Node.js 14+ (para tests JavaScript)
node --version

# Instalar dependencias Python
pip install -r requirements.txt

# Instalar dependencias JavaScript (si aplica)
npm install
```

### Ejecutar Todos los Tests

```bash
# Desde la raíz del proyecto
cd Tests

# Tests de Python
pytest

# Tests con verbose
pytest -v

# Tests con cobertura
pytest --cov=app --cov-report=html
```

---

## 🧪 Ejecutar Tests

### Tests Individuales

```bash
# Smoke tests (verificación rápida)
pytest test_api_smoke.py -v

# Tests de autenticación y productos
pytest test_auth_products.py -v

# Tests de utilidades
pytest Scripts/test_utils.py -v

# Tests de validadores
pytest Scripts/test_validators.py -v
```

### Tests con Opciones Avanzadas

```bash
# Tests con salida detallada
pytest -v -s

# Tests específicos por nombre
pytest -k "test_health" -v

# Tests con timeout
pytest --timeout=10

# Tests en paralelo
pytest -n auto

# Tests con marcadores
pytest -m "smoke" -v
```

### Tests de JavaScript

```bash
# Ejecutar tests de API
node Scripts/apitest.js

# Ejecutar tests de validadores
node Scripts/validadortest.js

# Ejecutar setup
node Scripts/setup.js
```

---

## 📊 Tipos de Tests

### 1. Smoke Tests (`test_api_smoke.py`)

**Propósito:** Verificación rápida de que la API está funcionando

**Tests incluidos:**
- ✅ `/api/health` - Endpoint de salud
- ✅ `/api/openapi.json` - Especificación OpenAPI
- ✅ `/api/docs` - Documentación Swagger

**Ejecutar:**
```bash
pytest test_api_smoke.py -v
```

**Ejemplo de salida esperada:**
```
test_api_smoke.py::test_health_endpoint PASSED
test_api_smoke.py::test_openapi_and_docs PASSED
```

### 2. Tests de Autenticación (`test_auth_products.py`)

**Propósito:** Validar seguridad y acceso a recursos protegidos

**Tests incluidos:**
- ✅ Autenticación requerida para productos
- ✅ Acceso con token válido
- ✅ Login y generación de tokens

**Ejecutar:**
```bash
pytest test_auth_products.py -v
```

**Ejemplo de salida esperada:**
```
test_auth_products.py::test_products_requires_auth PASSED
test_auth_products.py::test_products_with_auth PASSED
```

### 3. Tests de Utilidades (`Scripts/test_utils.py`)

**Propósito:** Validar funciones utilitarias

**Funciones testeadas:**
- Formatters: currency, date, percentage, stock status
- Helpers: safe divide, percentage change, filename sanitization
- SKU generation

**Ejecutar:**
```bash
pytest Scripts/test_utils.py -v
```

### 4. Tests de Validadores (`Scripts/test_validators.py`)

**Propósito:** Validar reglas de negocio y entrada de datos

**Validadores testeados:**
- Validación de entrada de datos
- Reglas de negocio
- Validación de formatos

**Ejecutar:**
```bash
pytest Scripts/test_validators.py -v
```

---

## 🔧 Scripts y Utilidades

### Scripts Python

#### `test_utils.py`
Tests para funciones utilitarias del proyecto.

**Funciones testeadas:**
```python
# Formatters
- format_currency()
- format_date()
- format_percentage()
- format_stock_status()

# Helpers
- safe_divide()
- percentage_change()
- sanitize_filename()
- generate_sku()
```

#### `test_validators.py`
Tests para validadores de datos y reglas de negocio.

**Validadores testeados:**
- Validación de entrada
- Reglas de negocio
- Validación de formatos

### Scripts JavaScript

#### `apitest.js`
Tests de API en Node.js para verificación de endpoints.

**Uso:**
```bash
node Scripts/apitest.js
```

#### `validadortest.js`
Tests de validadores en JavaScript.

**Uso:**
```bash
node Scripts/validadortest.js
```

#### `setup.js`
Configuración y setup para tests JavaScript.

**Uso:**
```bash
node Scripts/setup.js
```

---

## ⚙️ Configuración

### Variables de Entorno

Crear archivo `.env.test` en la raíz del proyecto:

```env
# Testing
FLASK_ENV=testing
TESTING=True

# Database (si aplica)
TEST_DATABASE_URL=sqlite:///test.db

# API
API_BASE_URL=http://localhost:5000
API_TIMEOUT=10

# Auth (para tests)
TEST_USERNAME=admin
TEST_PASSWORD=admin123
```

### Configuración de pytest

Crear `pytest.ini` en la raíz del proyecto:

```ini
[pytest]
testpaths = Tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*
addopts = 
    -v
    --strict-markers
    --tb=short
markers =
    smoke: Smoke tests
    integration: Integration tests
    unit: Unit tests
    slow: Slow running tests
```

### Configuración de cobertura

Crear `.coveragerc` en la raíz del proyecto:

```ini
[run]
source = app
omit = 
    */tests/*
    */venv/*
    */__pycache__/*

[report]
exclude_lines =
    pragma: no cover
    def __repr__
    raise AssertionError
    raise NotImplementedError
    if __name__ == .__main__.:
    if TYPE_CHECKING:
```

---

## 📈 Cobertura de Tests

### Ver Cobertura

```bash
# Cobertura en consola
pytest --cov=app --cov-report=term-missing

# Cobertura HTML
pytest --cov=app --cov-report=html
open htmlcov/index.html

# Cobertura JSON
pytest --cov=app --cov-report=json
```

### Objetivos de Cobertura

- **Mínimo:** 70% de cobertura
- **Objetivo:** 80% de cobertura
- **Ideal:** 90%+ de cobertura

### Áreas Críticas (100% cobertura requerida)

- ✅ Autenticación y autorización
- ✅ Validadores de datos
- ✅ Endpoints de API críticos
- ✅ Funciones utilitarias

---

## 🐛 Troubleshooting

### Problemas Comunes

#### 1. Tests fallan por falta de dependencias

```bash
# Instalar dependencias
pip install -r requirements.txt
pip install pytest pytest-cov
```

#### 2. Tests fallan por configuración

```bash
# Verificar variables de entorno
python -c "import os; print(os.environ.get('FLASK_ENV'))"

# Ejecutar con variables explícitas
FLASK_ENV=testing pytest
```

#### 3. Tests de autenticación fallan

```bash
# Verificar credenciales de test
# En test_auth_products.py, verificar:
# username: 'admin'
# password: 'admin123'
```

#### 4. Tests de API fallan por conexión

```bash
# Verificar que la API está corriendo
curl http://localhost:5000/api/health

# O ejecutar con mock
pytest --mock-api
```

#### 5. Problemas con imports

```bash
# Verificar PYTHONPATH
export PYTHONPATH="${PYTHONPATH}:$(pwd)"

# O instalar en modo desarrollo
pip install -e .
```

### Debug de Tests

```bash
# Ejecutar con debug
pytest -v -s --pdb

# Ejecutar test específico con debug
pytest -v -s --pdb test_api_smoke.py::test_health_endpoint

# Mostrar prints
pytest -v -s
```

---

## 🤝 Contribuir

### Cómo Agregar Nuevos Tests

1. **Crear archivo de test**
   ```bash
   touch Tests/test_nuevo_feature.py
   ```

2. **Estructura básica**
   ```python
   import pytest
   from app import create_app
   
   def test_nuevo_feature():
       app = create_app('testing')
       with app.test_client() as c:
           # Tu test aquí
           assert True
   ```

3. **Ejecutar el nuevo test**
   ```bash
   pytest Tests/test_nuevo_feature.py -v
   ```

### Convenciones

- ✅ Nombres descriptivos: `test_descripcion_funcionalidad`
- ✅ Un test por función/caso de uso
- ✅ Tests independientes (no dependen de otros)
- ✅ Tests rápidos (< 1 segundo cada uno)
- ✅ Documentación clara de qué testea cada test

### Checklist antes de hacer PR

- [ ] Todos los tests pasan: `pytest`
- [ ] Cobertura no disminuye: `pytest --cov`
- [ ] Tests nuevos tienen nombres descriptivos
- [ ] Tests nuevos están documentados
- [ ] No hay warnings de pytest
- [ ] Tests son rápidos (< 1s cada uno)

---

## 📚 Recursos Adicionales

### Documentación

- [Índice de Tests](./INDEX.md)
- [Documentación Detallada](./Documentation/index.md)
- [Índice de Scripts](./Scripts/INDEX.md)

### Enlaces Útiles

- [pytest Documentation](https://docs.pytest.org/)
- [Flask Testing](https://flask.palletsprojects.com/en/2.3.x/testing/)
- [Python Testing Best Practices](https://realpython.com/python-testing/)

---

## 📝 Changelog

### v1.0 (2025-10-29)
- ✅ Documentación inicial completa
- ✅ README principal
- ✅ Guías de uso
- ✅ Troubleshooting
- ✅ Ejemplos de uso

---

## 📞 Soporte

Para preguntas o problemas:

1. Revisar [Troubleshooting](#troubleshooting)
2. Consultar [Documentación](./Documentation/index.md)
3. Crear issue en el repositorio

---

**Última actualización:** 2025-10-29  
**Mantenido por:** Equipo de Desarrollo


