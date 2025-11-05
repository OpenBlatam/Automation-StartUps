# Documentación Técnica - Tests

**Versión:** 1.0  
**Última actualización:** 2025-10-29

---

## 📋 Índice

- [Arquitectura](#arquitectura)
- [Estructura de Tests](#estructura-de-tests)
- [Fixtures y Configuración](#fixtures-y-configuración)
- [Mocks y Stubs](#mocks-y-stubs)
- [Test Client](#test-client)
- [Autenticación en Tests](#autenticación-en-tests)
- [Base de Datos de Test](#base-de-datos-de-test)
- [Scripts JavaScript](#scripts-javascript)
- [Integración Continua](#integración-continua)

---

## 🏗️ Arquitectura

### Estructura General

```
Tests/
├── test_api_smoke.py      # Tests de integración básicos
├── test_auth_products.py  # Tests de autenticación
└── Scripts/               # Tests unitarios y utilidades
    ├── test_utils.py      # Tests de funciones utilitarias
    ├── test_validators.py # Tests de validadores
    ├── apitest.js         # Tests JS de API
    └── validadortest.js   # Tests JS de validadores
```

### Flujo de Ejecución

```
1. pytest encuentra archivos test_*.py
2. Carga fixtures y configuración
3. Ejecuta cada test en orden
4. Recopila resultados
5. Genera reporte
```

---

## 📝 Estructura de Tests

### Template Básico

```python
import pytest
from app import create_app

def make_app():
    """Factory para crear app de test"""
    import os
    os.environ.setdefault('FLASK_ENV', 'testing')
    app = create_app('testing')
    return app

def test_nombre_descriptivo():
    """Descripción de qué testea este test"""
    app = make_app()
    with app.test_client() as c:
        # Arrange
        # Act
        # Assert
        assert True
```

### Patrón AAA (Arrange-Act-Assert)

```python
def test_products_with_auth():
    app = make_app()
    with app.test_client() as c:
        # Arrange: Preparar datos
        token = login_get_token(c)
        
        # Act: Ejecutar acción
        rv = c.get('/api/products', 
                  headers={'Authorization': f'Bearer {token}'})
        
        # Assert: Verificar resultado
        assert rv.status_code == 200
        data = rv.get_json()
        assert isinstance(data, (list, dict))
```

---

## 🔧 Fixtures y Configuración

### Fixture de App

```python
@pytest.fixture
def app():
    """Fixture para crear app de test"""
    import os
    os.environ.setdefault('FLASK_ENV', 'testing')
    app = create_app('testing')
    return app

@pytest.fixture
def client(app):
    """Fixture para test client"""
    return app.test_client()
```

### Uso de Fixtures

```python
def test_with_fixtures(client):
    """Test usando fixtures"""
    rv = client.get('/api/health')
    assert rv.status_code == 200
```

### Fixture de Autenticación

```python
@pytest.fixture
def auth_token(client):
    """Fixture para token de autenticación"""
    rv = client.post('/api/auth/login', 
                     json={'username': 'admin', 'password': 'admin123'})
    assert rv.status_code == 200
    return rv.get_json()['token']

def test_protected_endpoint(client, auth_token):
    """Test usando token de fixture"""
    rv = client.get('/api/products', 
                    headers={'Authorization': f'Bearer {auth_token}'})
    assert rv.status_code == 200
```

---

## 🎭 Mocks y Stubs

### Mock de Requests Externos

```python
from unittest.mock import patch, Mock

@patch('app.external_api.requests.get')
def test_with_external_api_mock(mock_get):
    """Test con mock de API externa"""
    # Configurar mock
    mock_get.return_value.json.return_value = {'status': 'ok'}
    mock_get.return_value.status_code = 200
    
    # Ejecutar test
    result = app.external_api.fetch_data()
    
    # Verificar
    assert result == {'status': 'ok'}
    mock_get.assert_called_once()
```

### Mock de Base de Datos

```python
@patch('app.database.get_user')
def test_with_db_mock(mock_get_user):
    """Test con mock de base de datos"""
    mock_get_user.return_value = {'id': 1, 'name': 'Test'}
    
    result = app.get_user_profile(1)
    
    assert result['name'] == 'Test'
    mock_get_user.assert_called_once_with(1)
```

---

## 🌐 Test Client

### Uso Básico

```python
def test_get_endpoint():
    app = make_app()
    with app.test_client() as c:
        rv = c.get('/api/health')
        assert rv.status_code == 200
```

### Métodos HTTP

```python
# GET
rv = c.get('/api/products')

# POST
rv = c.post('/api/products', json={'name': 'Product'})

# PUT
rv = c.put('/api/products/1', json={'name': 'Updated'})

# DELETE
rv = c.delete('/api/products/1')

# PATCH
rv = c.patch('/api/products/1', json={'name': 'Patched'})
```

### Headers

```python
# Headers personalizados
rv = c.get('/api/products', 
           headers={
               'Authorization': 'Bearer token',
               'Content-Type': 'application/json'
           })
```

### JSON Data

```python
# Enviar JSON
rv = c.post('/api/products', 
            json={'name': 'Product', 'price': 100})

# O con data
rv = c.post('/api/products', 
            data=json.dumps({'name': 'Product'}),
            content_type='application/json')
```

---

## 🔐 Autenticación en Tests

### Helper de Login

```python
def login_get_token(c):
    """Helper para obtener token de autenticación"""
    rv = c.post('/api/auth/login', 
                json={'username': 'admin', 'password': 'admin123'})
    assert rv.status_code == 200
    data = rv.get_json()
    return data['token']
```

### Uso en Tests

```python
def test_protected_endpoint():
    app = make_app()
    with app.test_client() as c:
        # Obtener token
        token = login_get_token(c)
        
        # Usar token
        rv = c.get('/api/products', 
                   headers={'Authorization': f'Bearer {token}'})
        assert rv.status_code == 200
```

### Verificar Autenticación Requerida

```python
def test_requires_auth():
    """Verificar que endpoint requiere autenticación"""
    app = make_app()
    with app.test_client() as c:
        rv = c.get('/api/products')
        # Debe fallar sin auth
        assert rv.status_code in (401, 403)
```

---

## 🗄️ Base de Datos de Test

### Configuración

```python
import os
import tempfile
import pytest
from app import create_app, db

@pytest.fixture
def app():
    """App con base de datos de test"""
    # Base de datos temporal
    db_fd, db_path = tempfile.mkstemp()
    
    app = create_app('testing')
    app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{db_path}'
    
    with app.app_context():
        db.create_all()
        yield app
        db.drop_all()
    
    os.close(db_fd)
    os.unlink(db_path)
```

### Uso en Tests

```python
def test_with_db(app):
    """Test usando base de datos"""
    with app.app_context():
        # Crear datos de test
        user = User(name='Test')
        db.session.add(user)
        db.session.commit()
        
        # Test
        user = User.query.filter_by(name='Test').first()
        assert user is not None
```

---

## 📜 Scripts JavaScript

### Estructura de apitest.js

```javascript
// apitest.js
const axios = require('axios');

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

// Ejecutar tests
(async () => {
    const results = await Promise.all([
        testHealthEndpoint(),
        // más tests...
    ]);
    
    const passed = results.filter(r => r).length;
    console.log(`\n${passed}/${results.length} tests passed`);
    process.exit(passed === results.length ? 0 : 1);
})();
```

### Estructura de validadortest.js

```javascript
// validadortest.js
function testValidator() {
    // Tests de validadores
    const validator = require('./validator');
    
    // Test caso válido
    const valid = validator.validate({ field: 'value' });
    console.assert(valid, 'Validator should pass');
    
    // Test caso inválido
    const invalid = validator.validate({ field: '' });
    console.assert(!invalid, 'Validator should fail');
}

testValidator();
```

---

## 🔄 Integración Continua

### GitHub Actions

```yaml
# .github/workflows/tests.yml
name: Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    
    steps:
    - uses: actions/checkout@v2
    
    - name: Set up Python
      uses: actions/setup-python@v2
      with:
        python-version: '3.8'
    
    - name: Install dependencies
      run: |
        pip install -r requirements.txt
        pip install pytest pytest-cov
    
    - name: Run tests
      run: |
        pytest --cov=app --cov-report=xml
    
    - name: Upload coverage
      uses: codecov/codecov-action@v2
```

### GitLab CI

```yaml
# .gitlab-ci.yml
test:
  image: python:3.8
  script:
    - pip install -r requirements.txt
    - pip install pytest pytest-cov
    - pytest --cov=app --cov-report=xml
  coverage: '/TOTAL.*\s+(\d+%)$/'
```

---

## 📚 Referencias

### Documentación Oficial

- [pytest Documentation](https://docs.pytest.org/)
- [Flask Testing](https://flask.palletsprojects.com/en/2.3.x/testing/)
- [unittest.mock](https://docs.python.org/3/library/unittest.mock.html)

### Artículos

- [Testing Best Practices](https://realpython.com/python-testing/)
- [pytest Fixtures](https://docs.pytest.org/en/stable/fixture.html)

---

**Última actualización:** 2025-10-29


