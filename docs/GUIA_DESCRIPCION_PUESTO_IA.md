# 🚀 Guía de Uso: Generación Automatizada de Descripciones de Puesto con IA

> **Propósito**: Guía completa para usar el sistema automatizado de generación de descripciones de puesto y onboarding
> **Audiencia**: Equipo de HR, Recruiters, Hiring Managers

---

## 📋 Tabla de Contenidos

1. [Introducción](#introducción)
2. [Configuración Inicial](#configuración-inicial)
3. [Uso Básico](#uso-básico)
4. [Personalización](#personalización)
5. [Proceso de Onboarding Automatizado](#proceso-de-onboarding-automatizado)
6. [Integraciones](#integraciones)
7. [Troubleshooting](#troubleshooting)

---

## 🎯 Introducción

Este sistema automatiza la creación de descripciones de puesto optimizadas para atraer talento con experiencia en IA, y gestiona el proceso de onboarding de nuevos empleados.

### Características Principales

- ✅ **Generación con IA**: Descripciones personalizadas usando modelos de lenguaje
- ✅ **Publicación Automática**: Publica en múltiples portales de trabajo simultáneamente
- ✅ **Procesamiento de Aplicaciones**: Clasificación automática de candidatos
- ✅ **Onboarding Automatizado**: Proceso estructurado de incorporación
- ✅ **Notificaciones**: Alertas automáticas al equipo de HR

---

## ⚙️ Configuración Inicial

### 1. Variables de Airflow

Configura las siguientes variables en Airflow:

```bash
# API de IA (OpenAI, Anthropic, etc.)
airflow variables set AI_API_KEY "tu-api-key"
airflow variables set AI_MODEL "gpt-4"

# Portales de trabajo
airflow variables set JOB_BOARDS '["linkedin", "indeed", "glassdoor"]'

# API de aplicaciones (ATS)
airflow variables set APPLICATIONS_API_URL "https://api.ats.com"

# Notificaciones
airflow variables set HR_TEAM_EMAIL "hr@empresa.com"
```

### 2. Dependencias

El DAG requiere las siguientes librerías (ya incluidas en `requirements.txt`):

```python
requests>=2.31.0
```

### 3. Permisos

Asegúrate de que el usuario de Airflow tenga permisos para:
- Crear DAG runs
- Acceder a variables de Airflow
- Trigger otros DAGs (para onboarding)

---

## 🚀 Uso Básico

### Ejemplo 1: Generar Descripción para Gerente de Operaciones

#### Opción A: Desde la UI de Airflow

1. Ve a la UI de Airflow
2. Encuentra el DAG `job_description_ai_generator`
3. Haz clic en "Trigger DAG w/ config"
4. Ingresa la siguiente configuración JSON:

```json
{
  "role": "Gerente de Operaciones",
  "level": "Senior",
  "department": "Operaciones",
  "ai_experience_years": 3,
  "skills": ["Python", "Machine Learning", "Airflow", "Kubernetes"],
  "preferred_skills": ["MLOps", "NLP", "TensorFlow"],
  "location": "Remoto",
  "salary_range": "Competitivo"
}
```

5. Haz clic en "Trigger"

#### Opción B: Desde la CLI

```bash
airflow dags trigger job_description_ai_generator \
  --conf '{
    "role": "Gerente de Operaciones",
    "level": "Senior",
    "department": "Operaciones",
    "ai_experience_years": 3,
    "skills": ["Python", "Machine Learning", "Airflow", "Kubernetes"],
    "preferred_skills": ["MLOps", "NLP", "TensorFlow"],
    "location": "Remoto"
  }'
```

#### Opción C: Desde Python

```python
from airflow.api.client.local_client import Client

client = Client(None, None)

config = {
    "role": "Gerente de Operaciones",
    "level": "Senior",
    "department": "Operaciones",
    "ai_experience_years": 3,
    "skills": ["Python", "Machine Learning", "Airflow", "Kubernetes"],
    "preferred_skills": ["MLOps", "NLP", "TensorFlow"],
    "location": "Remoto"
}

dag_run = client.trigger_dag(
    dag_id='job_description_ai_generator',
    conf=config
)
```

### Ejemplo 2: Otros Roles

#### Data Scientist

```json
{
  "role": "Data Scientist",
  "level": "Mid",
  "department": "Data Science",
  "ai_experience_years": 2,
  "skills": ["Python", "Pandas", "Scikit-learn", "SQL"],
  "preferred_skills": ["TensorFlow", "PyTorch", "MLflow"],
  "location": "Híbrido"
}
```

#### MLOps Engineer

```json
{
  "role": "MLOps Engineer",
  "level": "Senior",
  "department": "Engineering",
  "ai_experience_years": 4,
  "skills": ["Python", "Kubernetes", "Docker", "MLflow"],
  "preferred_skills": ["Kubeflow", "KServe", "Terraform"],
  "location": "Remoto"
}
```

---

## 🎨 Personalización

### Parámetros Disponibles

| Parámetro | Tipo | Requerido | Descripción | Ejemplo |
|-----------|------|-----------|-------------|---------|
| `role` | string | Sí | Nombre del puesto | "Gerente de Operaciones" |
| `level` | string | No | Nivel (Junior/Mid/Senior) | "Senior" |
| `department` | string | No | Departamento | "Operaciones" |
| `ai_experience_years` | int | No | Años de experiencia en IA | 3 |
| `skills` | array | No | Habilidades requeridas | ["Python", "ML"] |
| `preferred_skills` | array | No | Habilidades preferidas | ["TensorFlow"] |
| `location` | string | No | Ubicación del trabajo | "Remoto" |
| `salary_range` | string | No | Rango salarial | "Competitivo" |

### Personalización Avanzada

#### Modificar el Template

Edita el archivo `/docs/DESCRIPCION_PUESTO_IA.md` para personalizar:
- Estructura de la descripción
- Secciones adicionales
- Formato y estilo

#### Integrar con tu ATS

Modifica la función `process_applications` en el DAG para integrar con tu ATS:

```python
def process_applications(**context):
    # Integración con tu ATS (Greenhouse, Lever, etc.)
    ats_client = YourATSClient(api_key="...")
    applications = ats_client.get_new_applications()
    # ... procesamiento
```

---

## 👥 Proceso de Onboarding Automatizado

### Activación Automática

El onboarding se activa automáticamente cuando:
1. Un candidato acepta una oferta
2. Se ejecuta el DAG con configuración de candidato

### Configuración de Onboarding

```json
{
  "candidate": {
    "name": "Juan Pérez",
    "email": "juan.perez@example.com",
    "role": "Gerente de Operaciones",
    "start_date": "2024-02-15",
    "manager": "manager@example.com",
    "department": "Operaciones"
  }
}
```

### Pasos del Onboarding

El sistema ejecuta automáticamente:

1. **Semana 1: Configuración**
   - ✅ Creación de cuentas (email, Slack, etc.)
   - ✅ Configuración de VPN y accesos
   - ✅ Asignación de hardware
   - ✅ Acceso a documentación

2. **Semana 2-3: Capacitación**
   - ✅ Curso de arquitectura del sistema
   - ✅ Hands-on labs
   - ✅ Shadowing con equipo
   - ✅ Primer proyecto asignado

3. **Semana 4-8: Integración**
   - ✅ Proyectos incrementales
   - ✅ Code reviews
   - ✅ Mentoría activa
   - ✅ Feedback continuo

### Verificar Estado del Onboarding

```bash
# Ver DAG runs de onboarding
airflow dags list-runs -d employee_onboarding

# Ver logs de un run específico
airflow tasks logs employee_onboarding setup_access <run_id>
```

---

## 🔌 Integraciones

### Portales de Trabajo

#### LinkedIn

```python
# Configurar en variables de Airflow
airflow variables set LINKEDIN_API_KEY "tu-key"
airflow variables set LINKEDIN_COMPANY_ID "123456"
```

#### Indeed

```python
airflow variables set INDEED_PUBLISHER_ID "tu-id"
airflow variables set INDEED_API_KEY "tu-key"
```

### Sistemas ATS

#### Greenhouse

```python
# Modificar process_applications para integrar con Greenhouse
from greenhouse import GreenhouseAPI

def process_applications(**context):
    api = GreenhouseAPI(api_key=Variable.get("GREENHOUSE_API_KEY"))
    jobs = api.get_jobs()
    # ... procesamiento
```

### APIs de IA

#### OpenAI

```python
# Ya configurado en el DAG
airflow variables set AI_API_KEY "sk-..."
airflow variables set AI_MODEL "gpt-4"
```

#### Anthropic (Claude)

```python
# Modificar generate_job_description_ai para usar Claude
import anthropic

client = anthropic.Anthropic(api_key=Variable.get("ANTHROPIC_API_KEY"))
response = client.messages.create(
    model="claude-3-opus-20240229",
    messages=[{"role": "user", "content": prompt}]
)
```

---

## 🐛 Troubleshooting

### Problema: La descripción no se genera

**Solución:**
1. Verifica que `AI_API_KEY` esté configurada
2. Revisa los logs del task `generate_description`
3. Si no hay API key, el sistema usa un template básico

```bash
airflow tasks logs job_description_ai_generator generate_description <run_id>
```

### Problema: No se publica en portales

**Solución:**
1. Verifica las credenciales de cada portal
2. Revisa los logs del task `publish_job_boards`
3. Algunos portales pueden requerir aprobación manual

### Problema: Onboarding no se activa

**Solución:**
1. Verifica que el DAG `employee_onboarding` exista
2. Asegúrate de que el usuario tenga permisos para trigger DAGs
3. Revisa que la configuración del candidato sea correcta

```bash
# Verificar que el DAG existe
airflow dags list | grep employee_onboarding

# Verificar permisos
airflow users list
```

### Problema: Aplicaciones no se procesan

**Solución:**
1. Verifica que `APPLICATIONS_API_URL` esté configurada
2. Si no hay API, el sistema funciona en modo simulación
3. Integra con tu ATS siguiendo la sección de integraciones

---

## 📊 Monitoreo y Métricas

### Métricas Clave

- **Tiempo de generación**: Tiempo promedio para generar una descripción
- **Tasa de publicación**: % de portales donde se publicó exitosamente
- **Aplicaciones procesadas**: Número de aplicaciones clasificadas
- **Tasa de onboarding**: % de candidatos que completan onboarding

### Dashboards

Crea un dashboard en Grafana o similar para monitorear:
- Ejecuciones del DAG
- Aplicaciones recibidas
- Estado de onboarding
- Tiempos de proceso

---

## 🔄 Mejores Prácticas

### 1. Revisión Manual

Aunque el sistema es automatizado, siempre revisa:
- ✅ Descripciones generadas antes de publicar
- ✅ Aplicaciones clasificadas como "qualified"
- ✅ Configuración de onboarding

### 2. Personalización por Rol

Crea templates específicos para diferentes tipos de roles:
- Técnicos (Engineers, Data Scientists)
- Liderazgo (Managers, Directors)
- Especializados (MLOps, Researchers)

### 3. Actualización Continua

- Actualiza los templates periódicamente
- Ajusta los criterios de evaluación de aplicaciones
- Mejora el proceso de onboarding basado en feedback

### 4. Seguridad

- ✅ Nunca commitees API keys al repositorio
- ✅ Usa Variables de Airflow para secretos
- ✅ Rota las credenciales regularmente
- ✅ Limita el acceso al DAG

---

## 📚 Recursos Adicionales

- [Template de Descripción de Puesto](./DESCRIPCION_PUESTO_IA.md)
- [DAG de Onboarding](../data/airflow/dags/employee_onboarding.py)
- [Documentación de Airflow](https://airflow.apache.org/docs/)

---

## 🆘 Soporte

¿Necesitas ayuda?

1. Revisa esta guía y el troubleshooting
2. Consulta los logs de Airflow
3. Contacta al equipo de plataforma

---

**Última actualización**: 2024  
**Versión**: 1.0  
**Mantenido por**: HR Team & Platform Team






