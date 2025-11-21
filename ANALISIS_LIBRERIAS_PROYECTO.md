# Análisis Completo de Librerías del Proyecto

## 📁 Estructura del Proyecto

```
/Users/adan/IA/
├── data/
│   ├── airflow/          # Apache Airflow DAGs y workflows
│   ├── db/               # Scripts de base de datos
│   └── integrations/     # Integraciones con servicios externos
├── web/
│   ├── kpis/             # API Express/TypeScript
│   └── kpis-next/        # Frontend Next.js/React
├── workflow/             # Workflows Kestra
├── ml/                   # Machine Learning (MLflow, Kubeflow, KServe)
├── infra/                # Infraestructura (Terraform, Ansible, Puppet, Salt)
├── kubernetes/           # Configuraciones Kubernetes
├── observability/        # Monitoring (Prometheus, Grafana, Loki, Elastic)
├── security/             # Configuraciones de seguridad
└── scripts/              # Scripts de utilidad
```

---

## 🐍 Librerías Python

### **Core & Framework**
- **Apache Airflow Providers**
  - `apache-airflow-providers-mysql>=5.0.0`
  - `apache-airflow-providers-postgres>=5.8.0`
  - `apache-airflow-providers-http>=4.5.0`
  - `apache-airflow-providers-amazon>=8.0.0`
  - `apache-airflow-providers-google>=10.0.0`
  - `apache-airflow-providers-microsoft-azure>=7.0.0`

- **Web Frameworks**
  - `flask>=3.0.0`
  - `flask-cors>=4.0.0`
  - `fastapi>=0.104.1`
  - `uvicorn[standard]>=0.24.0`
  - `starlette>=0.27.0`

### **Base de Datos**
- `psycopg2-binary>=2.9.7` - PostgreSQL driver
- `asyncpg>=0.29.0` - Async PostgreSQL driver
- `sqlalchemy>=2.0.23` - ORM
- `alembic>=1.13.0` - Database migrations

### **HTTP & API Clients**
- `requests>=2.31.0` - HTTP library
- `httpx>=0.25.0` - Modern async HTTP client
- `httpx[http2]>=0.25.0` - HTTP/2 support
- `aiohttp>=3.9.0` - Alternative async HTTP
- `httpcore>=1.0.0` - Low-level HTTP

### **Cloud Storage**
- `boto3>=1.34.0` - AWS S3
- `azure-storage-blob>=12.19.0` - Azure Blob Storage
- `google-cloud-storage>=2.14.0` - GCP Cloud Storage
- `s3fs>=2023.12.0` - S3 filesystem interface

### **Resiliencia & Circuit Breakers**
- `tenacity>=8.2.2` - Retry logic
- `backoff>=2.2.1` - Alternative retry decorator
- `pybreaker>=1.0.1` - Advanced circuit breaker
- `circuitbreaker>=2.0.0` - Circuit breaker pattern

### **Rate Limiting & Throttling**
- `aiolimiter>=1.1.0` - Async rate limiter
- `asyncio-throttle>=1.0.2`
- `limits>=3.6.0` - Generic rate limiting
- `slowapi>=0.1.9` - Rate limiting for Flask/FastAPI

### **Logging & Observabilidad**
- `structlog>=23.2.0` - Structured logging
- `loguru>=0.7.2` - Modern logging
- `python-json-logger>=2.0.7`

### **OpenTelemetry - Distributed Tracing**
- `opentelemetry-api>=1.21.0`
- `opentelemetry-sdk>=1.21.0`
- `opentelemetry-instrumentation>=0.42b0`
- `opentelemetry-instrumentation-requests>=0.42b0`
- `opentelemetry-instrumentation-httpx>=0.42b0`
- `opentelemetry-instrumentation-flask>=0.42b0`
- `opentelemetry-instrumentation-sqlalchemy>=0.42b0`
- `opentelemetry-exporter-jaeger>=1.21.0`
- `opentelemetry-exporter-otlp>=1.21.0`

### **Métricas & Monitoring**
- `prometheus-client>=0.19.0`
- `psutil>=5.9.8` - System monitoring

### **Caching**
- `redis>=5.0.1`
- `aioredis>=2.0.1` - Async Redis
- `cachetools>=5.3.2`
- `diskcache>=5.6.3`
- `aiocache>=0.12.2` - Async cache

### **OCR & Document Processing**
- `pytesseract>=0.3.10` - Tesseract OCR
- `Pillow>=10.1.0` - Image processing
- `google-cloud-vision>=3.4.5` - Google Vision API
- `PyPDF2>=3.0.1` - PDF processing
- `pdf2image>=1.16.3` - PDF to image
- `opencv-python>=4.8.1.78` - Computer vision
- `PyMuPDF>=1.23.8` - PDF compression

### **Data Processing**
- `pandas>=2.1.3` - Data manipulation
- `numpy>=1.26.2` - Numerical computing
- `polars>=0.19.19` - Fast DataFrame alternative
- `pyarrow>=14.0.1` - Columnar data processing
- `openpyxl>=3.1.2` - Excel support

### **Machine Learning**
- `scikit-learn>=1.3.2` - ML library
- `sentence-transformers>=2.2.2` - Sentence embeddings
- `transformers>=4.36.0` - Hugging Face transformers
- `torch>=2.1.0` - PyTorch (required by transformers)

### **NLP & Text Processing**
- `spacy>=3.7.2` - NLP and NER
- `vaderSentiment>=3.3.2` - Sentiment analysis
- `textblob>=0.17.1` - Text processing

### **Translation**
- `googletrans==4.0.0-rc1` - Google Translate
- `deepl>=1.15.0` - DeepL (better quality)

### **Vector Databases**
- `pinecone-client>=2.2.4` - Pinecone
- `qdrant-client>=1.6.9` - Qdrant
- `elasticsearch>=8.11.0` - Search indexing

### **Serialización Rápida**
- `orjson>=3.9.10` - Ultra-fast JSON serializer
- `ujson>=5.9.0` - Fast JSON alternative
- `msgpack>=1.0.7` - Binary serialization

### **Security**
- `cryptography>=41.0.3`
- `PyJWT>=2.8.0`
- `python-jose[cryptography]>=3.3.0` - JWT handling
- `passlib[bcrypt]>=1.7.4` - Password hashing
- `authlib>=1.2.1` - OAuth/OpenID Connect
- `bleach>=6.1.0` - HTML sanitization
- `markupsafe>=2.1.3`
- `defusedxml>=0.7.1` - Safe XML parsing

### **Data Quality & Validation**
- `great-expectations>=0.18.0`
- `pydantic>=2.5.0`
- `pydantic-settings>=2.1.0`
- `pydantic-extra-types>=2.3.0`
- `email-validator>=2.1.0`
- `pandera>=0.17.0`
- `marshmallow>=3.20.1` - Serialization/deserialization
- `cattrs>=23.2.0` - Structured data transformation
- `jsonschema>=4.20.0` - JSON schema validation
- `voluptuous>=0.13.1` - Declarative validation
- `typeguard>=4.1.0` - Runtime type checking

### **Utilities**
- `python-dateutil>=2.8.2`
- `pendulum>=3.0.0` - Date/time handling
- `arrow>=1.3.0` - Modern date handling
- `pytz>=2023.3.post1`
- `python-dotenv>=1.0.0` - Environment variables
- `dynaconf>=3.2.4` - Dynamic configuration
- `click>=8.1.7` - CLI framework
- `rich>=13.7.0` - Rich terminal formatting
- `tqdm>=4.66.1` - Progress bars
- `humanize>=4.8.0` - Human-readable formatting
- `croniter>=1.3.0` - Cron scheduling

### **Kubernetes & Infrastructure**
- `kubernetes>=28.1.0` - Kubernetes client
- `pyyaml>=6.0.1` - YAML handling

### **Message Queue**
- `kafka-python>=2.0.2`
- `celery>=5.3.4` - Task queue
- `celery[redis]>=5.3.4`

### **Async Utilities**
- `asyncio-timeout>=4.0.3`
- `aiofiles>=23.2.1` - Async file I/O

### **Image Processing**
- `scikit-image>=0.22.0` - Advanced image processing
- `scipy>=1.10.0` - Scientific computing

### **Web Scraping**
- `beautifulsoup4>=4.12.2` - HTML parsing
- `lxml>=4.9.3` - Fast XML/HTML parser

### **Reporting**
- `reportlab>=4.0.7` - PDF reports

### **Google APIs**
- `google-api-python-client>=2.0.0`
- `google-auth>=2.0.0`
- `google-auth-oauthlib>=0.5.0`
- `google-auth-httplib2>=0.1.0`

### **Third-party Integrations**
- `stripe>=7.0.0` - Stripe payments
- `facebook-business>=19.0.0` - Facebook Marketing API
- `google-ads>=24.0.0` - Google Ads API
- `dropbox>=11.36.0` - Dropbox integration
- `graphql-core>=3.2.0` - GraphQL

### **Testing (Development)**
- `pytest>=7.4.3`
- `pytest-asyncio>=0.21.1`
- `pytest-cov>=4.1.0`
- `pytest-mock>=3.12.0`
- `pytest-timeout>=2.2.0`
- `pytest-xdist>=3.5.0`
- `pytest-benchmark>=4.0.0`
- `pytest-html>=4.1.1`
- `pytest-json-report>=1.5.1`
- `responses>=0.24.1`
- `pytest-httpx>=0.27.0`
- `freezegun>=1.2.2`
- `fakeredis>=2.20.1`
- `hypothesis>=6.92.0`
- `faker>=20.1.0`

### **Code Quality (Development)**
- `black>=23.12.1` - Code formatter
- `ruff>=0.1.8` - Fast linter
- `mypy>=1.7.1` - Type checker
- `mypy-extensions>=1.0.0`
- `isort>=5.13.2` - Import sorter
- `flake8>=6.1.0` - Linter
- `pylint>=3.0.3` - Linter
- `bandit>=1.7.5` - Security linter

### **Documentation (Development)**
- `sphinx>=7.2.6`
- `sphinx-rtd-theme>=2.0.0`
- `mkdocs>=1.5.3`
- `mkdocs-material>=9.5.3`

### **Development Tools**
- `ipython>=8.18.1` - Enhanced REPL
- `ipdb>=0.13.13` - Enhanced debugger
- `pre-commit>=3.6.0` - Git hooks
- `watchdog>=3.0.0` - File system events

### **Profiling & Debugging**
- `py-spy>=0.3.14` - Sampling profiler
- `pyinstrument>=5.5.0` - Performance profiler
- `memory-profiler>=0.61.0` - Memory profiler
- `line-profiler>=4.1.1` - Line-by-line profiling

---

## 📦 Librerías JavaScript/TypeScript

### **Frontend (Next.js)**
- `next>=14.2.5` - Next.js framework
- `react>=18.2.0` - React library
- `react-dom>=18.2.0` - React DOM
- `typescript>=5.6.3` - TypeScript

### **Backend (Express)**
- `express>=4.21.1` - Web framework
- `cors>=2.8.5` - CORS middleware
- `helmet>=7.1.0` - Security headers
- `express-rate-limit>=7.4.0` - Rate limiting
- `prom-client>=15.1.3` - Prometheus metrics
- `envalid>=8.0.0` - Environment validation
- `dotenv>=16.4.5` - Environment variables
- `pg>=8.13.1` - PostgreSQL client
- `swagger-ui-express>=5.0.1` - API documentation

### **Testing (JavaScript/TypeScript)**
- `jest>=29.7.0` - Testing framework
- `ts-jest>=29.2.5` - TypeScript Jest preset
- `@testing-library/jest-dom>=6.6.3`
- `@testing-library/react>=16.0.1`
- `supertest>=7.0.0` - HTTP assertions

### **Code Quality (JavaScript/TypeScript)**
- `eslint>=9.13.0`
- `@typescript-eslint/eslint-plugin>=8.6.0`
- `@typescript-eslint/parser>=8.6.0`
- `eslint-config-prettier>=9.1.0`
- `eslint-plugin-import>=2.31.0`
- `eslint-config-next>=14.2.5`
- `prettier>=3.3.3` - Code formatter

### **Development Tools (JavaScript/TypeScript)**
- `husky>=9.1.6` - Git hooks
- `lint-staged>=15.2.10` - Lint staged files
- `nodemon>=3.1.7` - Development server
- `tsx>=4.19.0` - TypeScript execution
- `morgan>=1.10.0` - HTTP request logger

### **Type Definitions**
- `@types/express>=4.17.21`
- `@types/node>=22.7.0`
- `@types/jest>=29.5.12`
- `@types/cors>=2.8.17`
- `@types/morgan>=1.9.9`
- `@types/supertest>=2.0.16`
- `@types/express-rate-limit>=6.0.3`
- `@types/swagger-ui-express>=4.1.7`
- `@types/react>=18.3.6`
- `@types/react-dom>=18.3.0`

---

## 🗂️ Archivos de Dependencias Encontrados

### Python
1. `/requirements-dev.txt` - Dependencias de desarrollo
2. `/data/airflow/requirements.txt` - Dependencias principales de Airflow
3. `/data/airflow/requirements-base.txt` - Dependencias base mínimas
4. `/data/integrations/requirements.txt` - Dependencias de integraciones
5. `/data/integrations/chatbot/requirements.txt` - Dependencias del chatbot
6. `/workflow/kestra/flows/lib/requirements.txt` - Dependencias de workflows Kestra
7. `/data/airflow/dags/REQUIREMENTS_ads_reporting.txt` - Dependencias para reporting de ads
8. `/data/airflow/dags/REQUIREMENTS_stripe_quickbooks.txt` - Dependencias para Stripe/QuickBooks
9. `/pyproject.toml` - Configuración de herramientas (Black, Ruff)

### JavaScript/TypeScript
1. `/web/kpis/package.json` - Dependencias del backend Express
2. `/web/kpis-next/package.json` - Dependencias del frontend Next.js

---

## 📊 Resumen por Categoría

### Total de Librerías Python: ~150+
### Total de Librerías JavaScript/TypeScript: ~30+

### Categorías Principales:
1. **Orquestación**: Apache Airflow, Kestra
2. **Web Frameworks**: Flask, FastAPI, Express, Next.js
3. **Base de Datos**: PostgreSQL, Redis, Vector DBs
4. **ML/AI**: PyTorch, Transformers, scikit-learn, spaCy
5. **Cloud**: AWS (boto3), Azure, GCP
6. **Observabilidad**: OpenTelemetry, Prometheus, Grafana
7. **Testing**: pytest, jest
8. **Code Quality**: black, ruff, eslint, prettier
9. **Integraciones**: Stripe, Facebook, Google APIs, Dropbox

---

## 🛠️ Herramientas de Infraestructura (No son librerías, pero son dependencias del proyecto)

### **Infrastructure as Code**
- **Terraform** - IaC para AWS, Azure, GCP
- **Helmfile** - Gestión de Helm charts
- **Kustomize** - Personalización de configuraciones Kubernetes

### **Configuration Management**
- **Ansible** - Automatización de configuración
- **Salt** - Gestión de configuración
- **Puppet** - Gestión de configuración
- **Chef** - Gestión de configuración (mencionado en Makefile)

### **Container & Orchestration**
- **Docker** - Contenedores
- **Docker Compose** - Orquestación de contenedores
- **Kubernetes (kubectl)** - Orquestación de contenedores
- **Helm** - Gestión de paquetes Kubernetes

### **CI/CD**
- **Jenkins** - Servidor de CI/CD (opcional)

### **Observability Stack**
- **Prometheus** - Métricas
- **Grafana** - Visualización
- **Loki** - Logs
- **Elasticsearch** - Búsqueda y análisis
- **OpenCost** - Análisis de costos

### **ML/AI Infrastructure**
- **MLflow** - Gestión del ciclo de vida de ML
- **Kubeflow** - ML en Kubernetes
- **KServe** - Servir modelos ML

### **Message Queue**
- **Kafka (Strimzi)** - Message broker
- **Kafka Connect** - Integración de datos

### **Backup**
- **Velero** - Backup de Kubernetes

---

## 🔍 Observaciones

1. **Stack Moderno**: El proyecto utiliza tecnologías modernas y actualizadas
2. **Arquitectura Completa**: Cubre desde infraestructura hasta ML/AI
3. **Observabilidad**: Sistema completo de monitoring y tracing
4. **Resiliencia**: Múltiples librerías para retry, circuit breakers, rate limiting
5. **ML/AI**: Stack completo para procesamiento de lenguaje natural y ML
6. **Multi-cloud**: Soporte para AWS, Azure y GCP
7. **Type Safety**: TypeScript en frontend, type hints y validación en Python

---

## 📝 Notas

- Algunas librerías están marcadas como opcionales en los comentarios
- El proyecto tiene fallbacks para librerías opcionales
- Hay múltiples archivos de requirements para diferentes contextos
- El proyecto está bien estructurado con separación de concerns

