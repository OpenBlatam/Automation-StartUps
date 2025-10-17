# 🤝 Guía de Contribución - SaaS de IA para Marketing

## 🎯 ¡Gracias por tu interés en contribuir!

Agradecemos cualquier contribución que ayude a mejorar nuestra plataforma de IA para marketing. Esta guía te ayudará a comenzar.

## 🚀 Cómo Contribuir

### 1. Fork y Clone
```bash
# Fork el repositorio en GitHub
# Luego clona tu fork
git clone https://github.com/tu-usuario/ia-marketing-saas.git
cd ia-marketing-saas

# Agregar upstream
git remote add upstream https://github.com/original/ia-marketing-saas.git
```

### 2. Configurar Entorno de Desarrollo
```bash
# Instalar dependencias
npm install

# Configurar variables de entorno
cp .env.example .env
# Editar .env con tus configuraciones

# Iniciar base de datos
docker-compose up -d db redis

# Ejecutar migraciones
npm run migrate

# Iniciar en modo desarrollo
npm run dev
```

### 3. Crear una Rama
```bash
# Crear rama para tu feature
git checkout -b feature/nueva-funcionalidad

# O para bugfix
git checkout -b bugfix/corregir-error
```

## 📝 Tipos de Contribuciones

### 🐛 Reportar Bugs
1. Verifica que no exista un issue similar
2. Crea un nuevo issue con:
   - Descripción clara del problema
   - Pasos para reproducir
   - Comportamiento esperado vs actual
   - Screenshots si aplica
   - Información del sistema

### ✨ Sugerir Funcionalidades
1. Verifica que no exista una sugerencia similar
2. Crea un issue con:
   - Descripción detallada de la funcionalidad
   - Casos de uso específicos
   - Beneficios para los usuarios
   - Consideraciones técnicas

### 🔧 Contribuir Código
1. Fork el repositorio
2. Crea una rama para tu contribución
3. Implementa los cambios
4. Añade tests si es necesario
5. Actualiza documentación
6. Crea un Pull Request

## 🎨 Estándares de Código

### TypeScript/JavaScript
```typescript
// Usar TypeScript para todo el código
interface User {
  id: string;
  email: string;
  subscriptionPlan: 'starter' | 'professional' | 'enterprise';
}

// Usar async/await en lugar de callbacks
async function getUser(id: string): Promise<User> {
  const user = await db.user.findUnique({ where: { id } });
  if (!user) {
    throw new Error('User not found');
  }
  return user;
}

// Usar const/let en lugar de var
const API_BASE_URL = process.env.API_BASE_URL;
let currentUser: User | null = null;
```

### Naming Conventions
```typescript
// Variables y funciones: camelCase
const userName = 'john_doe';
function getUserById(id: string) { }

// Constantes: UPPER_SNAKE_CASE
const MAX_RETRY_ATTEMPTS = 3;

// Clases: PascalCase
class UserService { }

// Interfaces: PascalCase con prefijo I
interface IUserRepository { }

// Archivos: kebab-case
// user-service.ts
// copywriting-controller.ts
```

### Estructura de Archivos
```
src/
├── controllers/          # Controladores de API
├── services/            # Lógica de negocio
├── models/              # Modelos de datos
├── middleware/          # Middleware personalizado
├── utils/               # Utilidades
├── types/               # Definiciones de tipos
├── tests/               # Tests unitarios
└── docs/                # Documentación
```

## 🧪 Testing

### Tests Unitarios
```typescript
// tests/services/user-service.test.ts
import { UserService } from '../../src/services/user-service';

describe('UserService', () => {
  let userService: UserService;

  beforeEach(() => {
    userService = new UserService();
  });

  it('should create user successfully', async () => {
    const userData = {
      email: 'test@example.com',
      password: 'password123'
    };

    const result = await userService.createUser(userData);
    
    expect(result).toBeDefined();
    expect(result.email).toBe(userData.email);
  });
});
```

### Tests de Integración
```typescript
// tests/integration/api.test.ts
import request from 'supertest';
import app from '../../src/app';

describe('API Integration Tests', () => {
  it('should create copywriting request', async () => {
    const response = await request(app)
      .post('/api/v1/copywriting/generate')
      .send({
        type: 'landing_page',
        industry: 'saas',
        prompt: 'Test prompt'
      })
      .expect(200);

    expect(response.body).toHaveProperty('content');
    expect(response.body.content).toHaveProperty('headline');
  });
});
```

### Ejecutar Tests
```bash
# Todos los tests
npm test

# Tests unitarios
npm run test:unit

# Tests de integración
npm run test:integration

# Tests con coverage
npm run test:coverage

# Tests en modo watch
npm run test:watch
```

## 📚 Documentación

### Documentar Código
```typescript
/**
 * Genera contenido de marketing usando IA
 * @param options - Opciones para la generación de contenido
 * @param options.type - Tipo de contenido a generar
 * @param options.industry - Industria del cliente
 * @param options.prompt - Prompt específico para la IA
 * @returns Promise con el contenido generado
 * @throws {ValidationError} Si las opciones son inválidas
 * @throws {AIError} Si hay error en la generación
 * @example
 * ```typescript
 * const content = await generateContent({
 *   type: 'landing_page',
 *   industry: 'saas',
 *   prompt: 'Landing page para gestión de proyectos'
 * });
 * ```
 */
async function generateContent(options: ContentOptions): Promise<ContentResult> {
  // Implementación...
}
```

### Actualizar README
- Mantén la documentación actualizada
- Incluye ejemplos de uso
- Documenta cambios importantes
- Actualiza la lista de funcionalidades

### Documentar APIs
```typescript
/**
 * @swagger
 * /api/v1/copywriting/generate:
 *   post:
 *     summary: Genera contenido de marketing
 *     tags: [Copywriting]
 *     requestBody:
 *       required: true
 *       content:
 *         application/json:
 *           schema:
 *             type: object
 *             properties:
 *               type:
 *                 type: string
 *                 enum: [landing_page, email, ad]
 *               industry:
 *                 type: string
 *                 enum: [saas, ecommerce, fintech]
 *     responses:
 *       200:
 *         description: Contenido generado exitosamente
 *       400:
 *         description: Request inválido
 */
```

## 🔄 Proceso de Pull Request

### 1. Antes de Crear el PR
- [ ] Código compila sin errores
- [ ] Tests pasan exitosamente
- [ ] Código sigue los estándares
- [ ] Documentación actualizada
- [ ] Commit messages descriptivos

### 2. Crear el PR
```bash
# Push tu rama
git push origin feature/nueva-funcionalidad

# Crear PR en GitHub
# Incluir descripción detallada
```

### 3. Template de PR
```markdown
## Descripción
Breve descripción de los cambios realizados.

## Tipo de Cambio
- [ ] Bug fix
- [ ] Nueva funcionalidad
- [ ] Breaking change
- [ ] Documentación

## Cambios Realizados
- Lista de cambios específicos
- Archivos modificados
- Nuevas funcionalidades

## Testing
- [ ] Tests unitarios añadidos/actualizados
- [ ] Tests de integración añadidos/actualizados
- [ ] Tests manuales realizados

## Screenshots (si aplica)
Incluir screenshots de la UI si hay cambios visuales.

## Checklist
- [ ] Código sigue los estándares del proyecto
- [ ] Self-review del código realizado
- [ ] Documentación actualizada
- [ ] Tests añadidos que prueban la funcionalidad
```

### 4. Review Process
- Al menos 2 aprobaciones requeridas
- Todos los tests deben pasar
- No conflictos de merge
- Code review completado

## 🏷️ Convenciones de Commits

### Formato
```
tipo(scope): descripción

Cuerpo del commit (opcional)

Footer (opcional)
```

### Tipos
- `feat`: Nueva funcionalidad
- `fix`: Corrección de bug
- `docs`: Cambios en documentación
- `style`: Cambios de formato/estilo
- `refactor`: Refactoring de código
- `test`: Añadir o modificar tests
- `chore`: Cambios en build/tools

### Ejemplos
```bash
feat(copywriting): añadir generación de landing pages
fix(auth): corregir validación de JWT
docs(api): actualizar documentación de endpoints
test(user-service): añadir tests para createUser
chore(deps): actualizar dependencias de seguridad
```

## 🐛 Reportar Issues

### Template de Bug Report
```markdown
**Describe el bug**
Descripción clara y concisa del problema.

**Pasos para reproducir**
1. Ve a '...'
2. Haz clic en '...'
3. Scroll hasta '...'
4. Ve el error

**Comportamiento esperado**
Descripción de lo que esperabas que pasara.

**Screenshots**
Si aplica, añade screenshots.

**Información del sistema:**
- OS: [e.g. Windows 10, macOS 12]
- Browser: [e.g. Chrome 91, Firefox 89]
- Versión: [e.g. 1.2.3]

**Contexto adicional**
Cualquier otra información relevante.
```

### Template de Feature Request
```markdown
**¿Es tu feature request relacionada con un problema?**
Descripción clara del problema.

**Describe la solución que te gustaría**
Descripción clara de lo que quieres que pase.

**Describe alternativas consideradas**
Descripción de soluciones alternativas.

**Contexto adicional**
Cualquier otra información o screenshots.
```

## 🎯 Roadmap de Contribuciones

### Prioridades Actuales
1. **Performance**: Optimización de APIs de IA
2. **Testing**: Aumentar cobertura de tests
3. **Documentación**: Mejorar guías de usuario
4. **Integraciones**: Nuevas integraciones con CRM
5. **Mobile**: App móvil nativa

### Ideas para Contribuir
- Nuevos tipos de contenido
- Mejoras en el análisis de propuestas
- Optimizaciones de performance
- Nuevas integraciones
- Mejoras en UX/UI
- Tests automatizados
- Documentación

## 🏆 Reconocimientos

### Contributors
- [Lista de contribuidores](https://github.com/original/ia-marketing-saas/graphs/contributors)

### Hall of Fame
- **Top Contributors**: Reconocimiento especial
- **Bug Hunters**: Encuentra bugs críticos
- **Documentation Heroes**: Mejoras en docs
- **Community Champions**: Ayuda en la comunidad

## 📞 Contacto

### Para Contribuidores
- **Email**: contributors@ia-marketing.com
- **Discord**: [Canal de contribuidores](https://discord.gg/contributors)
- **Slack**: #contributors

### Para Maintainers
- **Email**: maintainers@ia-marketing.com
- **GitHub**: @maintainers

## 📄 Licencia

Al contribuir, aceptas que tu código será licenciado bajo la [MIT License](LICENSE).

---

## 🎉 ¡Gracias!

Tu contribución hace que esta plataforma sea mejor para todos. ¡Esperamos ver tus ideas y mejoras!

---

*"Juntos construimos el futuro del marketing con IA."* 🤖✨

