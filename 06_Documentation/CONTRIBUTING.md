# 🤝 Guía de Contribución - ClickUp Brain

## ¡Bienvenido a ClickUp Brain!

Gracias por tu interés en contribuir a ClickUp Brain. Este documento proporciona las pautas y procesos para contribuir al proyecto.

## 📋 Tabla de Contenidos

- [Código de Conducta](#código-de-conducta)
- [Cómo Contribuir](#cómo-contribuir)
- [Configuración del Entorno](#configuración-del-entorno)
- [Proceso de Desarrollo](#proceso-de-desarrollo)
- [Estándares de Código](#estándares-de-código)
- [Documentación](#documentación)
- [Testing](#testing)
- [Pull Requests](#pull-requests)
- [Reportar Issues](#reportar-issues)

## 📜 Código de Conducta

### Nuestro Compromiso

Nos comprometemos a hacer de la participación en nuestro proyecto una experiencia libre de acoso para todos, independientemente de la edad, tamaño corporal, discapacidad, etnia, características sexuales, identidad y expresión de género, nivel de experiencia, educación, estatus socioeconómico, nacionalidad, apariencia personal, raza, religión o identidad y orientación sexual.

### Comportamiento Esperado

- Uso de lenguaje acogedor e inclusivo
- Respeto por diferentes puntos de vista y experiencias
- Aceptación de críticas constructivas
- Enfoque en lo que es mejor para la comunidad
- Empatía hacia otros miembros de la comunidad

### Comportamiento Inaceptable

- Uso de lenguaje o imágenes sexualizadas
- Comentarios insultantes o despectivos
- Acoso público o privado
- Publicación de información privada sin permiso
- Cualquier conducta inapropiada en un contexto profesional

## 🚀 Cómo Contribuir

### Tipos de Contribuciones

#### 🐛 Reportar Bugs
- Usa el template de issue para bugs
- Incluye pasos para reproducir
- Proporciona información del entorno
- Adjunta logs y screenshots si es relevante

#### ✨ Sugerir Mejoras
- Usa el template de feature request
- Describe el problema que resuelve
- Proporciona ejemplos de uso
- Considera alternativas

#### 📝 Mejorar Documentación
- Corrige errores tipográficos
- Mejora la claridad
- Añade ejemplos
- Traduce contenido

#### 💻 Contribuir Código
- Implementa nuevas funcionalidades
- Corrige bugs existentes
- Optimiza performance
- Mejora la arquitectura

### Proceso de Contribución

1. **Fork** el repositorio
2. **Clone** tu fork localmente
3. **Crea** una rama para tu feature
4. **Haz** tus cambios
5. **Testea** tus cambios
6. **Commit** con mensajes descriptivos
7. **Push** a tu fork
8. **Abre** un Pull Request

## 🛠️ Configuración del Entorno

### Prerrequisitos

- Python 3.11+
- Node.js 18+
- Docker y Docker Compose
- Git

### Configuración Local

```bash
# 1. Fork y clone el repositorio
git clone https://github.com/tu-usuario/clickup-brain.git
cd clickup-brain

# 2. Configurar entorno virtual
python -m venv venv
source venv/bin/activate  # En Windows: venv\Scripts\activate

# 3. Instalar dependencias
pip install -r requirements.txt
npm install

# 4. Configurar variables de entorno
cp .env.example .env
# Editar .env con tus configuraciones

# 5. Inicializar base de datos
python scripts/setup_database.py

# 6. Ejecutar tests
python -m pytest
npm test

# 7. Iniciar servidor de desarrollo
python app.py
npm run dev
```

### Configuración con Docker

```bash
# Construir y ejecutar con Docker Compose
docker-compose up --build

# Ejecutar tests en contenedor
docker-compose exec app python -m pytest

# Acceder al contenedor
docker-compose exec app bash
```

## 🔄 Proceso de Desarrollo

### Flujo de Git

```bash
# 1. Sincronizar con upstream
git fetch upstream
git checkout main
git merge upstream/main

# 2. Crear rama de feature
git checkout -b feature/nueva-funcionalidad

# 3. Hacer cambios y commits
git add .
git commit -m "feat: añadir nueva funcionalidad X"

# 4. Push a tu fork
git push origin feature/nueva-funcionalidad

# 5. Crear Pull Request
# Ir a GitHub y crear PR desde tu fork
```

### Convenciones de Naming

#### Ramas
- `feature/nombre-funcionalidad`
- `bugfix/descripcion-bug`
- `hotfix/descripcion-hotfix`
- `docs/descripcion-documentacion`
- `refactor/descripcion-refactor`

#### Commits
- `feat: nueva funcionalidad`
- `fix: corrección de bug`
- `docs: actualización de documentación`
- `style: cambios de formato`
- `refactor: refactorización de código`
- `test: añadir o corregir tests`
- `chore: tareas de mantenimiento`

## 📏 Estándares de Código

### Python

```python
# Usar Black para formateo
black --line-length 88 .

# Usar isort para imports
isort .

# Usar flake8 para linting
flake8 .

# Ejemplo de código bien formateado
class StrategicAnalyzer:
    """Analizador estratégico para ClickUp Brain."""
    
    def __init__(self, config: Dict[str, Any]) -> None:
        """Inicializar analizador con configuración.
        
        Args:
            config: Configuración del analizador
        """
        self.config = config
        self.logger = logging.getLogger(__name__)
    
    def analyze_strategy(self, data: pd.DataFrame) -> Dict[str, float]:
        """Analizar datos estratégicos.
        
        Args:
            data: DataFrame con datos estratégicos
            
        Returns:
            Diccionario con métricas de análisis
            
        Raises:
            ValueError: Si los datos no son válidos
        """
        if data.empty:
            raise ValueError("Los datos no pueden estar vacíos")
        
        # Implementación del análisis
        return {"score": 0.85, "confidence": 0.92}
```

### JavaScript/TypeScript

```typescript
// Usar Prettier para formateo
prettier --write .

// Usar ESLint para linting
eslint .

// Ejemplo de código bien formateado
interface StrategicConfig {
  readonly apiKey: string;
  readonly organizationId: string;
  readonly timeout?: number;
}

class ClickUpBrainClient {
  private readonly config: StrategicConfig;
  private readonly logger: Logger;

  constructor(config: StrategicConfig) {
    this.config = config;
    this.logger = new Logger('ClickUpBrainClient');
  }

  /**
   * Analizar estrategia usando AI
   * @param query - Consulta estratégica
   * @returns Promesa con resultados del análisis
   */
  async analyzeStrategy(query: string): Promise<StrategicAnalysis> {
    try {
      const response = await this.makeRequest('/api/v1/analyze', {
        method: 'POST',
        body: JSON.stringify({ query }),
      });

      return this.parseResponse(response);
    } catch (error) {
      this.logger.error('Error analyzing strategy', error);
      throw new StrategicAnalysisError('Failed to analyze strategy', error);
    }
  }
}
```

## 📚 Documentación

### Estándares de Documentación

#### Docstrings (Python)
```python
def calculate_strategic_score(
    metrics: Dict[str, float],
    weights: Optional[Dict[str, float]] = None
) -> float:
    """Calcular score estratégico basado en métricas.
    
    Esta función calcula un score estratégico ponderado basado en
    las métricas proporcionadas y sus pesos correspondientes.
    
    Args:
        metrics: Diccionario con métricas y sus valores
        weights: Pesos opcionales para cada métrica. Si no se proporciona,
                 se usan pesos por defecto.
    
    Returns:
        Score estratégico calculado (0.0 - 1.0)
    
    Raises:
        ValueError: Si las métricas están vacías o contienen valores inválidos
        TypeError: Si los tipos de datos no son correctos
    
    Example:
        >>> metrics = {"alignment": 0.8, "execution": 0.9}
        >>> score = calculate_strategic_score(metrics)
        >>> print(f"Score: {score:.2f}")
        Score: 0.85
    """
    # Implementación...
```

#### JSDoc (JavaScript/TypeScript)
```typescript
/**
 * Calcula el score estratégico basado en métricas
 * @param metrics - Objeto con métricas y sus valores
 * @param weights - Pesos opcionales para cada métrica
 * @returns Score estratégico calculado (0.0 - 1.0)
 * @throws {Error} Si las métricas están vacías
 * @example
 * ```typescript
 * const metrics = { alignment: 0.8, execution: 0.9 };
 * const score = calculateStrategicScore(metrics);
 * console.log(`Score: ${score.toFixed(2)}`);
 * ```
 */
function calculateStrategicScore(
  metrics: Record<string, number>,
  weights?: Record<string, number>
): number {
  // Implementación...
}
```

### Documentación de APIs

```yaml
# Ejemplo de documentación OpenAPI
paths:
  /api/v1/strategic-analysis:
    post:
      summary: Realizar análisis estratégico
      description: Analiza datos estratégicos y genera insights
      parameters:
        - name: Authorization
          in: header
          required: true
          schema:
            type: string
            format: bearer
      requestBody:
        required: true
        content:
          application/json:
            schema:
              type: object
              properties:
                query:
                  type: string
                  description: Consulta estratégica
                context:
                  type: object
                  description: Contexto adicional
      responses:
        200:
          description: Análisis completado exitosamente
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/StrategicAnalysis'
```

## 🧪 Testing

### Estrategia de Testing

#### Python
```python
# tests/test_strategic_analyzer.py
import pytest
from unittest.mock import Mock, patch
from clickup_brain.analyzer import StrategicAnalyzer

class TestStrategicAnalyzer:
    """Tests para StrategicAnalyzer."""
    
    @pytest.fixture
    def analyzer(self):
        """Fixture para crear instancia de analyzer."""
        config = {"model": "test_model", "threshold": 0.8}
        return StrategicAnalyzer(config)
    
    @pytest.fixture
    def sample_data(self):
        """Fixture con datos de prueba."""
        return {
            "alignment": 0.85,
            "execution": 0.92,
            "innovation": 0.78
        }
    
    def test_analyze_strategy_success(self, analyzer, sample_data):
        """Test análisis exitoso de estrategia."""
        result = analyzer.analyze_strategy(sample_data)
        
        assert "score" in result
        assert "confidence" in result
        assert 0.0 <= result["score"] <= 1.0
        assert 0.0 <= result["confidence"] <= 1.0
    
    def test_analyze_strategy_empty_data(self, analyzer):
        """Test análisis con datos vacíos."""
        with pytest.raises(ValueError, match="Los datos no pueden estar vacíos"):
            analyzer.analyze_strategy({})
    
    @patch('clickup_brain.analyzer.AIModel')
    def test_analyze_strategy_with_mock(self, mock_model, analyzer, sample_data):
        """Test análisis usando mock."""
        mock_model.return_value.predict.return_value = 0.85
        
        result = analyzer.analyze_strategy(sample_data)
        
        assert result["score"] == 0.85
        mock_model.return_value.predict.assert_called_once()
```

#### JavaScript/TypeScript
```typescript
// tests/strategic-analyzer.test.ts
import { describe, it, expect, beforeEach, vi } from 'vitest';
import { StrategicAnalyzer } from '../src/strategic-analyzer';

describe('StrategicAnalyzer', () => {
  let analyzer: StrategicAnalyzer;
  let mockConfig: StrategicConfig;

  beforeEach(() => {
    mockConfig = {
      apiKey: 'test-key',
      organizationId: 'test-org',
      timeout: 5000,
    };
    analyzer = new StrategicAnalyzer(mockConfig);
  });

  it('should analyze strategy successfully', async () => {
    const sampleData = {
      alignment: 0.85,
      execution: 0.92,
      innovation: 0.78,
    };

    const result = await analyzer.analyzeStrategy(sampleData);

    expect(result).toHaveProperty('score');
    expect(result).toHaveProperty('confidence');
    expect(result.score).toBeGreaterThanOrEqual(0);
    expect(result.score).toBeLessThanOrEqual(1);
  });

  it('should throw error for empty data', async () => {
    await expect(analyzer.analyzeStrategy({})).rejects.toThrow(
      'Los datos no pueden estar vacíos'
    );
  });
});
```

### Cobertura de Tests

```bash
# Python
pytest --cov=clickup_brain --cov-report=html --cov-report=term

# JavaScript/TypeScript
npm run test:coverage
```

## 🔀 Pull Requests

### Proceso de Pull Request

1. **Crear Issue** (opcional pero recomendado)
2. **Fork y crear rama**
3. **Implementar cambios**
4. **Escribir tests**
5. **Actualizar documentación**
6. **Crear Pull Request**

### Template de Pull Request

```markdown
## Descripción
Breve descripción de los cambios realizados.

## Tipo de Cambio
- [ ] Bug fix (cambio que corrige un problema)
- [ ] Nueva funcionalidad (cambio que añade funcionalidad)
- [ ] Breaking change (cambio que rompe compatibilidad)
- [ ] Documentación (cambio solo en documentación)

## Cambios Realizados
- Lista de cambios específicos
- Cambio 1
- Cambio 2

## Testing
- [ ] Tests unitarios añadidos/actualizados
- [ ] Tests de integración añadidos/actualizados
- [ ] Tests manuales realizados

## Screenshots (si aplica)
Añadir screenshots para cambios de UI.

## Checklist
- [ ] Código sigue los estándares del proyecto
- [ ] Self-review del código realizado
- [ ] Comentarios añadidos en código complejo
- [ ] Documentación actualizada
- [ ] Tests pasan localmente
- [ ] No hay conflictos de merge

## Issues Relacionados
Closes #123
```

### Review Process

1. **Automated Checks**: CI/CD pipeline
2. **Code Review**: Al menos 2 reviewers
3. **Testing**: Todos los tests deben pasar
4. **Documentation**: Documentación actualizada
5. **Approval**: Aprobación de maintainers

## 🐛 Reportar Issues

### Template de Bug Report

```markdown
## Descripción del Bug
Descripción clara y concisa del bug.

## Pasos para Reproducir
1. Ir a '...'
2. Hacer click en '...'
3. Scroll hasta '...'
4. Ver error

## Comportamiento Esperado
Descripción de lo que esperabas que pasara.

## Comportamiento Actual
Descripción de lo que realmente pasó.

## Screenshots
Si aplica, añadir screenshots.

## Información del Entorno
- OS: [e.g. Windows 10, macOS 12.0, Ubuntu 20.04]
- Browser: [e.g. Chrome 91, Firefox 89]
- Versión: [e.g. 1.2.3]

## Logs
```
Pegar logs relevantes aquí
```

## Contexto Adicional
Cualquier otro contexto sobre el problema.
```

### Template de Feature Request

```markdown
## Descripción de la Feature
Descripción clara y concisa de la funcionalidad deseada.

## Problema que Resuelve
¿Qué problema resuelve esta feature?

## Solución Propuesta
Descripción de la solución que te gustaría ver.

## Alternativas Consideradas
Descripción de soluciones alternativas consideradas.

## Contexto Adicional
Cualquier otro contexto o screenshots sobre la feature request.
```

## 🏷️ Versionado

### Semantic Versioning

- **MAJOR**: Cambios incompatibles en la API
- **MINOR**: Nueva funcionalidad compatible
- **PATCH**: Correcciones de bugs compatibles

### Changelog

```markdown
# Changelog

## [1.2.0] - 2024-01-15
### Added
- Nueva funcionalidad de análisis predictivo
- Soporte para múltiples idiomas

### Changed
- Mejorado performance del AI Knowledge Manager
- Actualizada interfaz de usuario

### Fixed
- Corregido bug en reportes automáticos
- Solucionado problema de sincronización cross-timezone

## [1.1.0] - 2024-01-01
### Added
- Integración con sistemas CRM
- Dashboard de métricas en tiempo real
```

## 📞 Contacto y Soporte

### Canales de Comunicación

- **GitHub Issues**: Para bugs y feature requests
- **Discussions**: Para preguntas y discusiones
- **Discord**: Para chat en tiempo real
- **Email**: contributors@clickupbrain.ai

### Maintainers

- **Lead Maintainer**: @maintainer1
- **Core Team**: @maintainer2, @maintainer3
- **Community Managers**: @community1, @community2

### Horarios de Disponibilidad

- **Lunes - Viernes**: 9:00 AM - 6:00 PM EST
- **Respuesta a Issues**: 24-48 horas
- **Code Review**: 2-3 días hábiles

## 🎉 Reconocimientos

### Contributors

Gracias a todos los contributors que han ayudado a hacer ClickUp Brain posible:

- @contributor1 - Implementación de AI Knowledge Manager
- @contributor2 - Mejoras en la documentación
- @contributor3 - Optimización de performance

### Sponsors

- [Empresa 1](https://empresa1.com) - Patrocinador principal
- [Empresa 2](https://empresa2.com) - Soporte de infraestructura

---

¡Gracias por contribuir a ClickUp Brain! Tu contribución hace que el proyecto sea mejor para todos. 🌟



