# Guía de Uso - Tests

**Versión:** 1.0  
**Última actualización:** 2025-10-29

---

## 📋 Índice

- [Introducción](#introducción)
- [Primeros Pasos](#primeros-pasos)
- [Ejemplos Prácticos](#ejemplos-prácticos)
- [Casos de Uso Comunes](#casos-de-uso-comunes)
- [Mejores Prácticas](#mejores-prácticas)
- [Workflows](#workflows)

---

## 🎯 Introducción

Esta guía te ayudará a entender y usar efectivamente la suite de tests del proyecto.

### ¿Para qué sirven estos tests?

- ✅ **Validación rápida:** Verificar que todo funciona después de cambios
- ✅ **Detección temprana:** Encontrar bugs antes de producción
- ✅ **Documentación viva:** Los tests documentan cómo funciona el código
- ✅ **Confianza:** Poder refactorizar sin miedo
- ✅ **CI/CD:** Integración continua automática

---

## 🚀 Primeros Pasos

### 1. Verificar Instalación

```bash
# Verificar Python
python --version  # Debe ser 3.8+

# Verificar pytest
pytest --version

# Verificar Node.js (para tests JS)
node --version  # Debe ser 14+
```

### 2. Ejecutar Primer Test

```bash
# Test más simple (smoke test)
pytest Tests/test_api_smoke.py -v

# Deberías ver:
# test_api_smoke.py::test_health_endpoint PASSED
# test_api_smoke.py::test_openapi_and_docs PASSED
```

### 3. Entender la Salida

```
test_api_smoke.py::test_health_endpoint PASSED    [ 50%]
test_api_smoke.py::test_openapi_and_docs PASSED   [100%]

========================= 2 passed in 0.15s =========================
```

**Significado:**
- `PASSED` = Test exitoso
- `FAILED` = Test falló (revisar error)
- `SKIPPED` = Test omitido (condición no cumplida)
- Porcentaje = Progreso

---

## 💡 Ejemplos Prácticos

### Ejemplo 1: Verificar que la API está funcionando

```bash
# Ejecutar smoke tests
pytest Tests/test_api_smoke.py::test_health_endpoint -v

# Salida esperada:
# test_api_smoke.py::test_health_endpoint PASSED
```

**Cuándo usar:** Antes de empezar a trabajar, después de cambios en la API

### Ejemplo 2: Verificar autenticación

```bash
# Ejecutar tests de auth
pytest Tests/test_auth_products.py -v

# Salida esperada:
# test_auth_products.py::test_products_requires_auth PASSED
# test_auth_products.py::test_products_with_auth PASSED
```

**Cuándo usar:** Cuando cambias lógica de autenticación o permisos

### Ejemplo 3: Verificar utilidades

```bash
# Tests de funciones utilitarias
pytest Tests/Scripts/test_utils.py -v

# Salida esperada:
# test_utils.py::test_format_currency PASSED
# test_utils.py::test_safe_divide PASSED
# ... (más tests)
```

**Cuándo usar:** Cuando modificas funciones utilitarias

### Ejemplo 4: Verificar validadores

```bash
# Tests de validadores
pytest Tests/Scripts/test_validators.py -v
```

**Cuándo usar:** Cuando cambias reglas de validación

---

## 🎯 Casos de Uso Comunes

### Caso 1: Antes de hacer commit

```bash
# Ejecutar todos los tests
pytest

# Si todo pasa, hacer commit
git add .
git commit -m "feat: nueva funcionalidad"
```

### Caso 2: Después de merge

```bash
# Actualizar código
git pull

# Verificar que todo sigue funcionando
pytest

# Si algo falla, revisar cambios del merge
```

### Caso 3: Antes de hacer PR

```bash
# Ejecutar tests con cobertura
pytest --cov=app --cov-report=term-missing

# Verificar que cobertura no bajó
# Si bajó, agregar tests para nuevas funcionalidades
```

### Caso 4: Debug de un test específico

```bash
# Ejecutar test específico con debug
pytest Tests/test_api_smoke.py::test_health_endpoint -v -s

# -v = verbose
# -s = mostrar prints
```

### Caso 5: Tests que fallan

```bash
# Ver qué tests fallan
pytest

# Ver detalles del error
pytest -v

# Ver traceback completo
pytest --tb=long

# Ejecutar solo los que fallaron
pytest --lf  # last failed
```

---

## ✨ Mejores Prácticas

### 1. Ejecutar tests frecuentemente

```bash
# ✅ BIEN: Ejecutar después de cada cambio pequeño
pytest Tests/test_api_smoke.py

# ❌ MAL: Esperar hasta el final para ejecutar todos
```

### 2. Usar tests específicos durante desarrollo

```bash
# ✅ BIEN: Ejecutar solo el test relevante
pytest Tests/test_auth_products.py::test_products_with_auth

# ❌ MAL: Ejecutar todos los tests cada vez
```

### 3. Verificar cobertura regularmente

```bash
# ✅ BIEN: Verificar cobertura periódicamente
pytest --cov=app --cov-report=term-missing

# ❌ MAL: Ignorar cobertura
```

### 4. Mantener tests rápidos

```bash
# ✅ BIEN: Tests individuales < 1 segundo
# ❌ MAL: Tests que tardan minutos
```

### 5. Tests independientes

```bash
# ✅ BIEN: Cada test es independiente
# ❌ MAL: Tests que dependen de otros tests
```

---

## 🔄 Workflows

### Workflow 1: Desarrollo Normal

```bash
# 1. Crear feature branch
git checkout -b feature/nueva-funcionalidad

# 2. Hacer cambios
# ... código ...

# 3. Ejecutar tests relevantes
pytest Tests/test_api_smoke.py

# 4. Si pasan, continuar
# 5. Ejecutar todos los tests antes de commit
pytest

# 6. Hacer commit
git commit -m "feat: nueva funcionalidad"
```

### Workflow 2: Debug de Bug

```bash
# 1. Reproducir bug
# 2. Crear test que falle (test del bug)
pytest Tests/test_bug.py::test_bug_reproduccion

# 3. Arreglar bug
# 4. Verificar que test pasa
pytest Tests/test_bug.py::test_bug_reproduccion

# 5. Verificar que otros tests siguen pasando
pytest
```

### Workflow 3: Refactoring

```bash
# 1. Ejecutar todos los tests (baseline)
pytest --cov=app > baseline.txt

# 2. Hacer refactoring
# ... código ...

# 3. Ejecutar tests de nuevo
pytest --cov=app > after.txt

# 4. Comparar resultados
diff baseline.txt after.txt

# 5. Si todo igual, refactoring exitoso
```

### Workflow 4: CI/CD

```bash
# En CI/CD pipeline:

# 1. Instalar dependencias
pip install -r requirements.txt

# 2. Ejecutar tests
pytest --cov=app --cov-report=xml

# 3. Subir cobertura
# (depende de tu servicio de CI)
```

---

## 📊 Interpretando Resultados

### Tests que pasan

```
test_api_smoke.py::test_health_endpoint PASSED    [ 50%]
test_api_smoke.py::test_openapi_and_docs PASSED   [100%]

========================= 2 passed in 0.15s =========================
```

✅ **Todo está bien, puedes continuar**

### Tests que fallan

```
test_api_smoke.py::test_health_endpoint FAILED    [ 50%]
test_api_smoke.py::test_openapi_and_docs PASSED   [100%]

========================= 1 failed, 1 passed in 0.20s =========================

FAILED Tests/test_api_smoke.py::test_health_endpoint
AssertionError: assert 'status' in data
```

❌ **Revisar el error y arreglar**

### Tests con warnings

```
test_api_smoke.py::test_health_endpoint PASSED    [ 50%]
========================= warnings summary =========================
Warning: Deprecated function used
```

⚠️ **Revisar warnings, pero tests pasan**

---

## 🎓 Siguiente Paso

Ahora que entiendes cómo usar los tests:

1. ✅ Ejecuta todos los tests: `pytest`
2. ✅ Revisa la [documentación técnica](./TECHNICAL_DOCS.md)
3. ✅ Consulta [troubleshooting](../README.md#troubleshooting)
4. ✅ Contribuye agregando más tests

---

**Última actualización:** 2025-10-29


