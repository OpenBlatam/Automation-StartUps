---
title: "Contributing"
category: "contributing.md"
tags: []
created: "2025-10-29"
path: "contributing.md"
---

# Contribuyendo a CFDI 4.0 IA 2025

¡Gracias por tu interés en contribuir! Este documento proporciona directrices para contribuir al proyecto.

## 📋 Tabla de Contenidos

- [Código de Conducta](#código-de-conducta)
- [¿Cómo Puedo Contribuir?](#cómo-puedo-contribuir)
- [Configuración del Entorno](#configuración-del-entorno)
- [Proceso de Desarrollo](#proceso-de-desarrollo)
- [Estándares de Código](#estándares-de-código)
- [Testing](#testing)
- [Pull Requests](#pull-requests)
- [Reportar Bugs](#reportar-bugs)
- [Sugerir Mejoras](#sugerir-mejoras)

## 🤝 Código de Conducta

Este proyecto sigue el [Contributor Covenant Code of Conduct](https://www.contributor-covenant.org/). Al participar, se espera que mantengas este código.

## 💡 ¿Cómo Puedo Contribuir?

### Reportar Bugs

Si encuentras un bug:

1. Verifica que no haya sido reportado antes
2. Usa el issue template correspondiente
3. Proporciona información detallada:
   - Versión del proyecto
   - Pasos para reproducir
   - Comportamiento esperado vs actual
   - Capturas de pantalla si aplica

### Sugerir Mejoras

Si tienes una idea para mejorar el proyecto:

1. Verifica que no haya sido sugerida antes
2. Usa el issue template de feature request
3. Describe el problema que resuelve
4. Explica por qué sería útil
5. Si es posible, propón una solución

### Contribuir con Código

1. Fork el proyecto
2. Crea una rama para tu feature/fix
3. Commit tus cambios siguiendo los estándares
4. Push a tu fork
5. Abre un Pull Request

## 🛠️ Configuración del Entorno

### Prerrequisitos

- Node.js 18.x o superior
- npm 8.x o superior
- Git

### Setup

```bash
# 1. Clonar el repositorio
git clone https://github.com/blatam/cfdi-4.0-ia.git
cd cfdi-4.0-ia

# 2. Instalar dependencias
npm install

# 3. Configurar variables de entorno
cp env.example .env
# Editar .env con tus configuraciones

# 4. Ejecutar tests
npm test

# 5. Iniciar servidor de desarrollo
npm run dev
```

### Usando Docker

```bash
# Construir imagen
make docker-build

# Ejecutar contenedor
make docker-run

# O usar docker-compose
make docker-compose-up
```

## 🔄 Proceso de Desarrollo

### Ramas

- `main` - Código de producción estable
- `develop` - Código de desarrollo
- `feature/*` - Nuevas funcionalidades
- `bugfix/*` - Correcciones de bugs
- `hotfix/*` - Correcciones urgentes

### Flujo de Trabajo

1. Crear rama desde `develop`
2. Desarrollar funcionalidad
3. Ejecutar tests
4. Ejecutar linter
5. Hacer commit con mensaje descriptivo
6. Push a tu fork
7. Crear Pull Request

## 📝 Estándares de Código

### Convenciones

- **Lenguaje**: JavaScript ES2021
- **Formato**: 2 espacios de indentación
- **Comillas**: Singles quotes ('')
- **Punto y coma**: Requerido
- **Nombres**: camelCase para variables/funciones, PascalCase para clases

### Ejemplo de Código

```javascript
/**
 * Ejemplo de función bien documentada
 * @param {Object} params - Parámetros de la función
 * @param {string} params.name - Nombre del parámetro
 * @returns {Promise<Object>} Resultado de la operación
 */
async function ejemploFuncion(params) {
  const { name } = params;
  
  try {
    const resultado = await procesarDatos(name);
    return { success: true, data: resultado };
  } catch (error) {
    console.error('Error en ejemploFuncion:', error);
    throw new Error(`Error procesando: ${error.message}`);
  }
}
```

### JSDoc

Todas las funciones públicas deben tener JSDoc:

```javascript
/**
 * Descripción de la función
 * @param {Type} param - Descripción del parámetro
 * @returns {Type} Descripción del retorno
 * @throws {Error} Descripción del error
 */
```

### Validación de Código

Antes de hacer commit:

```bash
# Ejecutar linter
npm run lint

# Ejecutar formato
npm run format

# Ejecutar tests
npm test
```

## 🧪 Testing

### Escribir Tests

- Un test por funcionalidad
- Nombres descriptivos
- Arrange-Act-Assert pattern
- Cobertura mínima: 70%

### Ejemplo de Test

```javascript
describe('Componente o Funcionalidad', () => {
  test('debe comportarse de cierta manera', () => {
    // Arrange
    const input = 'test';
    
    // Act
    const result = procesar(input);
    
    // Assert
    expect(result).toBe('expected');
  });
});
```

### Ejecutar Tests

```bash
# Todos los tests
npm test

# Tests con coverage
npm test -- --coverage

# Tests en modo watch
npm test -- --watch
```

## 📤 Pull Requests

### Antes de Enviar

- [ ] Código sigue los estándares
- [ ] Tests pasan
- [ ] Linter no reporta errores
- [ ] Código está documentado
- [ ] Commits siguen formato
- [ ] PR tiene descripción clara

### Formato de Commits

```
tipo(scope): descripción

descripción detallada si es necesario

Refs: #issue-number
```

**Tipos:**
- `feat`: Nueva funcionalidad
- `fix`: Corrección de bug
- `docs`: Documentación
- `style`: Formato de código
- `refactor`: Refactorización
- `test`: Tests
- `chore`: Tareas de mantenimiento

**Ejemplos:**

```bash
feat(cfdi): agregar validación de UUID
fix(api): corregir error en generación de CFDI
docs(readme): actualizar documentación de instalación
```

### Proceso de Revisión

1. PR será revisado por maintainers
2. Feedback será proporcionado si es necesario
3. Una vez aprobado, será mergeado
4. PR será cerrado y referenciado en CHANGELOG

## 🐛 Reportar Bugs

### Template de Bug Report

```markdown
**Descripción:**
Descripción clara del bug

**Pasos para Reproducir:**
1. Paso 1
2. Paso 2
3. ...

**Comportamiento Esperado:**
Lo que debería pasar

**Comportamiento Actual:**
Lo que realmente pasa

**Screenshots:**
Si aplica

**Entorno:**
- Versión: x.x.x
- SO: 
- Node: 
- npm:
```

## 💡 Sugerir Mejoras

### Template de Feature Request

```markdown
**Problema:**
Descripción del problema a resolver

**Solución Propuesta:**
Tu idea para resolverlo

**Alternativas Consideradas:**
Otras opciones evaluadas

**Impacto:**
Efectos potenciales
```

## 📚 Recursos

- [Documentación Principal](./README.md)
- [Documentación API](05_technology/Api_documentation/api.md)
- [Changelog](./CHANGELOG.md)

## 🎯 Prioridades

### Alta Prioridad
- Fixes críticos de seguridad
- Bugs que afectan funcionalidad core
- Mejoras de performance críticas

### Media Prioridad
- Nuevas funcionalidades
- Mejoras de UX
- Optimizaciones

### Baja Prioridad
- Mejoras de documentación
- Refactorizaciones
- Tests adicionales

## ❓ Preguntas

¿Dudas sobre el proceso de contribución?

- Abre un issue con etiqueta `question`
- Contacta a los maintainers
- Revisa documentación existente

---

¡Gracias por contribuir! 🎉
