# Guía de Contribución - Tests

**Versión:** 1.0  
**Última actualización:** 2025-10-29

---

## 📋 Índice

- [Cómo Contribuir](#cómo-contribuir)
- [Estándares de Código](#estándares-de-código)
- [Escribir Nuevos Tests](#escribir-nuevos-tests)
- [Estructura de Tests](#estructura-de-tests)
- [Naming Conventions](#naming-conventions)
- [Checklist de PR](#checklist-de-pr)
- [Code Review](#code-review)

---

## 🤝 Cómo Contribuir

### Proceso

1. **Fork** el repositorio
2. **Crea** una rama para tu feature: `git checkout -b feature/nuevos-tests`
3. **Escribe** tus tests
4. **Ejecuta** todos los tests: `pytest`
5. **Asegúrate** que todos pasan
6. **Commit** tus cambios: `git commit -m "test: agregar tests para X"`
7. **Push** a tu fork: `git push origin feature/nuevos-tests`
8. **Abre** un Pull Request

---

## 📝 Estándares de Código

### Python

```python
# ✅ BIEN: Código claro y legible
def test_products_with_auth():
    """Test que verifica acceso a productos con autenticación"""
    app = make_app()
    with app.test_client() as c:
        token = login_get_token(c)
        rv = c.get('/api/products', 
                   headers={'Authorization': f'Bearer {token}'})
        assert rv.status_code == 200

# ❌ MAL: Código confuso
def test1():
    app = make_app()
    c = app.test_client()
    t = login_get_token(c)
    r = c.get('/api/products', headers={'Authorization': f'Bearer {t}'})
    assert r.status_code == 200
```

### JavaScript

```javascript
// ✅ BIEN: Código claro con nombres descriptivos
async function testHealthEndpoint() {
    try {
        const response = await axios.get('http://localhost:5000/api/health');
        console.log('✅ Health endpoint OK:', response.status);
        return true;
    } catch (error) {
        console.error('❌ Health endpoint FAILED:', error.message);
        return false;
    }
}

// ❌ MAL: Código confuso
async function t() {
    try {
        const r = await axios.get('http://localhost:5000/api/health');
        return true;
    } catch (e) {
        return false;
    }
}
```

---

## ✍️ Escribir Nuevos Tests

### Paso 1: Identificar qué testear

**Preguntas:**
- ¿Qué funcionalidad estoy testando?
- ¿Cuáles son los casos de éxito?
- ¿Cuáles son los casos de error?
- ¿Hay casos límite?

### Paso 2: Elegir tipo de test

**Unit Test:** Función individual
```python
def test_format_currency():
    assert format_currency(100) == "$100.00"
```

**Integration Test:** Múltiples componentes
```python
def test_products_with_auth():
    # Test que integra auth + products
```

**Smoke Test:** Verificación básica
```python
def test_health_endpoint():
    # Test básico de que endpoint funciona
```

### Paso 3: Escribir el test

```python
def test_nombre_descriptivo():
    """
    Descripción clara de qué testea este test.
    
    Ejemplo:
    Test que verifica que el endpoint de productos
    requiere autenticación y retorna datos válidos.
    """
    # Arrange: Preparar
    app = make_app()
    
    # Act: Ejecutar
    with app.test_client() as c:
        token = login_get_token(c)
        rv = c.get('/api/products', 
                   headers={'Authorization': f'Bearer {token}'})
    
    # Assert: Verificar
    assert rv.status_code == 200
    data = rv.get_json()
    assert isinstance(data, list)
```

### Paso 4: Verificar que funciona

```bash
# Ejecutar el nuevo test
pytest Tests/test_nuevo.py::test_nombre_descriptivo -v

# Verificar que pasa
```

---

## 🏗️ Estructura de Tests

### Archivo de Test

```python
"""
Tests para [Módulo/Funcionalidad]

Este archivo contiene tests para:
- [Funcionalidad 1]
- [Funcionalidad 2]
- [Funcionalidad 3]
"""

import pytest
from app import create_app

# Helpers compartidos
def make_app():
    """Factory para crear app de test"""
    import os
    os.environ.setdefault('FLASK_ENV', 'testing')
    return create_app('testing')

def login_get_token(c):
    """Helper para obtener token"""
    rv = c.post('/api/auth/login', 
                json={'username': 'admin', 'password': 'admin123'})
    return rv.get_json()['token']

# Tests
def test_caso_1():
    """Test caso 1"""
    pass

def test_caso_2():
    """Test caso 2"""
    pass
```

### Organización

```
Tests/
├── test_api_smoke.py          # Tests básicos de API
├── test_auth_products.py       # Tests de autenticación
├── test_products.py            # Tests de productos
├── test_users.py               # Tests de usuarios
└── Scripts/
    ├── test_utils.py           # Tests de utilidades
    └── test_validators.py      # Tests de validadores
```

---

## 🏷️ Naming Conventions

### Nombres de Archivos

```python
# ✅ BIEN
test_api_smoke.py
test_auth_products.py
test_utils.py

# ❌ MAL
tests.py
test.py
api_tests.py
```

### Nombres de Tests

```python
# ✅ BIEN: Descriptivo y claro
def test_health_endpoint_returns_200():
def test_products_requires_authentication():
def test_format_currency_with_valid_input():

# ❌ MAL: Vago o confuso
def test1():
def test_health():
def test_products():
```

### Patrón Recomendado

```
test_[qué]_[cuándo/condición]_[resultado_esperado]
```

**Ejemplos:**
- `test_health_endpoint_when_api_running_returns_200`
- `test_products_when_not_authenticated_returns_401`
- `test_format_currency_with_negative_number_raises_error`

---

## ✅ Checklist de PR

### Antes de Abrir PR

- [ ] **Todos los tests pasan**
  ```bash
  pytest
  ```

- [ ] **Tests nuevos pasan**
  ```bash
  pytest Tests/test_nuevo.py -v
  ```

- [ ] **Cobertura no disminuye**
  ```bash
  pytest --cov=app --cov-report=term-missing
  ```

- [ ] **Código sigue estándares**
  - Nombres descriptivos
  - Docstrings en tests
  - Código limpio y legible

- [ ] **Tests son rápidos**
  - Cada test < 1 segundo
  - Suite completa < 30 segundos

- [ ] **Tests son independientes**
  - No dependen de otros tests
  - Pueden ejecutarse en cualquier orden

- [ ] **No hay warnings**
  ```bash
  pytest -W error
  ```

- [ ] **Documentación actualizada**
  - README si es necesario
  - Comentarios en código complejo

### Template de PR

```markdown
## Descripción
[Descripción de qué tests agregas y por qué]

## Tests Agregados
- [ ] test_...
- [ ] test_...

## Cobertura
- Antes: X%
- Después: Y%

## Checklist
- [ ] Todos los tests pasan
- [ ] Cobertura no disminuye
- [ ] Código sigue estándares
- [ ] Tests son rápidos
- [ ] Tests son independientes
```

---

## 👀 Code Review

### Qué Revisar

1. **¿El test es claro?**
   - ¿Se entiende qué testea?
   - ¿Los nombres son descriptivos?

2. **¿El test es correcto?**
   - ¿Testea lo que dice testear?
   - ¿Las assertions son correctas?

3. **¿El test es útil?**
   - ¿Agrega valor?
   - ¿No es redundante?

4. **¿El test es mantenible?**
   - ¿Es fácil de modificar?
   - ¿No tiene dependencias innecesarias?

### Comentarios de Review

```python
# ✅ BIEN: Comentario constructivo
# "Considera agregar un test para el caso límite cuando X es None"

# ❌ MAL: Comentario no constructivo
# "Esto está mal"
```

---

## 📚 Ejemplos

### Ejemplo 1: Test Simple

```python
def test_health_endpoint():
    """Test que verifica que el endpoint de health responde"""
    app = make_app()
    with app.test_client() as c:
        rv = c.get('/api/health')
        assert rv.status_code in (200, 503)
        data = rv.get_json()
        assert 'status' in data
```

### Ejemplo 2: Test con Autenticación

```python
def test_products_requires_auth():
    """Test que verifica que productos requiere autenticación"""
    app = make_app()
    with app.test_client() as c:
        rv = c.get('/api/products')
        assert rv.status_code in (401, 403)

def test_products_with_auth():
    """Test que verifica acceso a productos con autenticación"""
    app = make_app()
    with app.test_client() as c:
        token = login_get_token(c)
        rv = c.get('/api/products', 
                   headers={'Authorization': f'Bearer {token}'})
        assert rv.status_code == 200
        data = rv.get_json()
        assert isinstance(data, (list, dict))
```

### Ejemplo 3: Test con Múltiples Casos

```python
@pytest.mark.parametrize("input,expected", [
    (100, "$100.00"),
    (1000, "$1,000.00"),
    (0, "$0.00"),
])
def test_format_currency(input, expected):
    """Test que verifica formato de moneda con diferentes valores"""
    assert format_currency(input) == expected
```

---

## 🎯 Mejores Prácticas

### DO ✅

- ✅ Tests descriptivos y claros
- ✅ Un test por caso de uso
- ✅ Tests independientes
- ✅ Tests rápidos
- ✅ Documentación clara

### DON'T ❌

- ❌ Tests que dependen de otros
- ❌ Tests que tardan mucho
- ❌ Tests sin documentación
- ❌ Nombres vagos
- ❌ Código duplicado sin razón

---

## 📞 Preguntas Frecuentes

### ¿Dónde pongo mi nuevo test?

**Respuesta:** 
- Si es test de API: `test_api_*.py`
- Si es test de utilidad: `Scripts/test_utils.py`
- Si es test nuevo módulo: `test_[modulo].py`

### ¿Cómo testear casos de error?

```python
def test_error_case():
    """Test que verifica manejo de errores"""
    app = make_app()
    with app.test_client() as c:
        rv = c.get('/api/products/invalid')
        assert rv.status_code == 404
```

### ¿Cómo testear con datos de prueba?

```python
def test_with_test_data():
    """Test con datos de prueba"""
    app = make_app()
    with app.app_context():
        # Crear datos de prueba
        product = Product(name='Test')
        db.session.add(product)
        db.session.commit()
        
        # Test
        with app.test_client() as c:
            rv = c.get('/api/products/1')
            assert rv.status_code == 200
```

---

**Última actualización:** 2025-10-29


