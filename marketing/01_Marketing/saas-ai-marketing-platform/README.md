# AI Marketing SaaS Platform

Una plataforma SaaS completa de marketing con IA que incluye un curso integral y herramientas de generación de contenido, similar a Copy.ai pero con funcionalidades avanzadas.

## 🚀 Características Principales

### 📚 Curso de Marketing con IA
- **12 módulos completos** de marketing con IA
- **48 horas de contenido** estructurado
- **Certificación profesional** al completar
- **Casos de estudio reales** y ejercicios prácticos
- **Mentoría 1-on-1** y comunidad de estudiantes

### 🤖 Generador de Contenido con IA
- **100+ plantillas profesionales** para diferentes tipos de contenido
- **Múltiples modelos de IA** (GPT-3.5, GPT-4, Claude)
- **Generación de variaciones** automática
- **Optimización de contenido** para SEO, conversión, engagement
- **Análisis de rendimiento** del contenido generado

### 📊 Analytics y Métricas
- **Dashboard completo** de analytics
- **Seguimiento de ROI** de campañas
- **Métricas de engagement** en tiempo real
- **Reportes personalizados** y exportables

### 💳 Sistema de Suscripciones
- **4 planes de suscripción** (Free, Basic, Professional, Enterprise)
- **Integración con Stripe** para pagos
- **Gestión de facturación** automática
- **Límites de uso** por plan

## 🛠️ Tecnologías Utilizadas

### Backend
- **Node.js** con Express.js
- **MongoDB** con Mongoose
- **JWT** para autenticación
- **OpenAI API** para generación de contenido
- **Stripe** para pagos
- **Redis** para caché y sesiones
- **Cloudinary** para gestión de archivos

### Frontend
- **React 18** con hooks modernos
- **React Router** para navegación
- **React Query** para gestión de estado del servidor
- **Framer Motion** para animaciones
- **Tailwind CSS** para estilos
- **Lucide React** para iconos

### Herramientas de Desarrollo
- **ESLint** y **Prettier** para calidad de código
- **Jest** para testing
- **Docker** para containerización
- **GitHub Actions** para CI/CD

## 📦 Instalación y Configuración

### Prerrequisitos
- Node.js 16+ y npm 8+
- MongoDB 4.4+
- Redis 6+
- Cuenta de OpenAI con API key
- Cuenta de Stripe (para pagos)

### 1. Clonar el Repositorio
```bash
git clone https://github.com/tu-usuario/ai-marketing-saas-platform.git
cd ai-marketing-saas-platform
```

### 2. Instalar Dependencias
```bash
# Backend
npm install

# Frontend
cd client
npm install
cd ..
```

### 3. Configurar Variables de Entorno
```bash
cp env.example .env
```

Edita el archivo `.env` con tus configuraciones:
```env
# Configuración básica
NODE_ENV=development
PORT=5000
MONGODB_URI=mongodb://localhost:27017/ai-marketing-saas
JWT_SECRET=tu-jwt-secret-super-seguro

# OpenAI
OPENAI_API_KEY=tu-openai-api-key

# Stripe
STRIPE_SECRET_KEY=sk_test_tu-stripe-secret-key
STRIPE_PUBLISHABLE_KEY=pk_test_tu-stripe-publishable-key

# Email
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USER=tu-email@gmail.com
EMAIL_PASS=tu-app-password
```

### 4. Inicializar la Base de Datos
```bash
npm run db:seed
```

### 5. Ejecutar en Desarrollo
```bash
# Terminal 1 - Backend
npm run dev

# Terminal 2 - Frontend
cd client
npm start
```

La aplicación estará disponible en:
- Frontend: http://localhost:3000
- Backend API: http://localhost:5000

## 🏗️ Estructura del Proyecto

```
ai-marketing-saas-platform/
├── client/                 # Frontend React
│   ├── src/
│   │   ├── components/     # Componentes reutilizables
│   │   ├── pages/         # Páginas principales
│   │   ├── contexts/      # Contextos de React
│   │   ├── hooks/         # Custom hooks
│   │   └── utils/         # Utilidades
│   └── public/            # Archivos estáticos
├── models/                # Modelos de MongoDB
├── routes/                # Rutas de la API
├── services/              # Servicios (AI, Email, etc.)
├── middleware/            # Middleware personalizado
├── utils/                 # Utilidades del servidor
├── tests/                 # Tests
└── docs/                  # Documentación
```

## 📚 Módulos del Curso

### Módulo 1: Fundamentos de IA en Marketing (Semanas 1-2)
- Introducción a la IA en marketing
- Ecosistema de herramientas de IA
- Marketing basado en datos
- Ética y cumplimiento de IA

### Módulo 2: Creación de Contenido con IA (Semanas 3-4)
- Fundamentos de copywriting con IA
- Email marketing automatizado
- Contenido para redes sociales
- Escritura de blogs y artículos

### Módulo 3: Sistemas de Evaluación de Rendimiento (Semanas 5-6)
- Evaluaciones de rendimiento con IA
- Desarrollo de empleados
- Analytics de rendimiento del equipo
- Adquisición de talento

### Módulo 4: Automatización de Marketing (Semanas 7-8)
- Automatización de flujos de trabajo
- Optimización del viaje del cliente
- Puntuación y calificación de leads
- Retargeting y remarketing

### Módulo 5: Analytics y Optimización (Semanas 9-10)
- Analytics de marketing con IA
- Pruebas A/B automatizadas
- Optimización de rendimiento
- Análisis competitivo

### Módulo 6: Aplicaciones Avanzadas (Semanas 11-12)
- Marketing específico por industria
- Tecnologías emergentes
- Desarrollo de estrategias
- Proyecto final

## 🔧 API Endpoints

### Autenticación
- `POST /api/auth/register` - Registro de usuario
- `POST /api/auth/login` - Inicio de sesión
- `POST /api/auth/logout` - Cerrar sesión
- `GET /api/auth/me` - Obtener perfil actual

### Contenido
- `POST /api/content/generate` - Generar contenido
- `POST /api/content/generate-variations` - Generar variaciones
- `POST /api/content/optimize` - Optimizar contenido
- `GET /api/content/history` - Historial de contenido

### Plantillas
- `GET /api/templates` - Listar plantillas
- `GET /api/templates/:id` - Obtener plantilla específica
- `POST /api/templates` - Crear plantilla personalizada

### Cursos
- `GET /api/courses` - Listar cursos
- `GET /api/courses/:id` - Obtener curso específico
- `POST /api/courses/:id/enroll` - Inscribirse en curso
- `GET /api/courses/:id/progress` - Progreso del curso

## 💰 Planes de Suscripción

### Plan Gratuito
- 10 generaciones de contenido por mes
- Acceso a plantillas básicas
- Soporte por email
- Comunidad de usuarios

### Plan Básico ($29/mes)
- 100 generaciones de contenido por mes
- Acceso a todas las plantillas
- 2 sesiones de mentoría
- Soporte prioritario
- Certificación

### Plan Profesional ($99/mes)
- 500 generaciones de contenido por mes
- Plantillas personalizadas
- 5 sesiones de mentoría
- Soporte 24/7
- API access
- Analytics avanzados

### Plan Enterprise ($299/mes)
- Generaciones ilimitadas
- Plantillas personalizadas
- Mentoría ilimitada
- Soporte dedicado
- Integraciones personalizadas
- White-label options

## 🧪 Testing

```bash
# Ejecutar todos los tests
npm test

# Tests con coverage
npm run test:coverage

# Tests en modo watch
npm run test:watch

# Tests de integración
npm run test:integration
```

## 🚀 Despliegue

### Docker
```bash
# Construir imagen
docker build -t ai-marketing-saas .

# Ejecutar contenedor
docker run -p 5000:5000 ai-marketing-saas
```

### Docker Compose
```bash
docker-compose up -d
```

### Heroku
```bash
# Instalar Heroku CLI
npm install -g heroku

# Login y crear app
heroku login
heroku create tu-app-name

# Desplegar
git push heroku main
```

## 📈 Métricas y Monitoreo

- **Google Analytics** para métricas de usuario
- **Sentry** para monitoreo de errores
- **New Relic** para performance
- **LogRocket** para sesiones de usuario

## 🤝 Contribución

1. Fork el proyecto
2. Crea una rama para tu feature (`git checkout -b feature/AmazingFeature`)
3. Commit tus cambios (`git commit -m 'Add some AmazingFeature'`)
4. Push a la rama (`git push origin feature/AmazingFeature`)
5. Abre un Pull Request

## 📄 Licencia

Este proyecto está bajo la Licencia MIT. Ver el archivo `LICENSE` para más detalles.

## 🆘 Soporte

- **Email**: soporte@ai-marketing-saas.com
- **Discord**: [Únete a nuestra comunidad](https://discord.gg/ai-marketing-saas)
- **Documentación**: [docs.ai-marketing-saas.com](https://docs.ai-marketing-saas.com)

## 🎯 Roadmap

### Q1 2024
- [ ] Integración con más modelos de IA
- [ ] App móvil nativa
- [ ] Integración con CRM populares
- [ ] Marketplace de plantillas

### Q2 2024
- [ ] IA para análisis de competencia
- [ ] Automatización de campañas
- [ ] Integración con redes sociales
- [ ] API pública

### Q3 2024
- [ ] IA para optimización de landing pages
- [ ] Análisis predictivo de ventas
- [ ] Integración con herramientas de email marketing
- [ ] Funciones de colaboración en equipo

## 🙏 Agradecimientos

- OpenAI por la API de GPT
- Stripe por el procesamiento de pagos
- MongoDB por la base de datos
- React team por el framework frontend
- Todos los contribuidores del proyecto

---

**¿Listo para revolucionar tu marketing con IA?** 🚀

[Regístrate ahora](https://ai-marketing-saas.com/register) y comienza tu transformación digital.









