# 📝 Ejemplos de Uso: Generación de Descripciones de Puesto

Este documento contiene ejemplos prácticos de cómo usar el sistema de generación automatizada de descripciones de puesto.

---

## 🚀 Ejemplo 1: Gerente de Operaciones (Básico)

### Desde la CLI

```bash
python scripts/generate_job_description.py \
  --role "Gerente de Operaciones" \
  --level Senior \
  --department "Operaciones" \
  --ai-experience-years 3 \
  --skills "Python, Machine Learning, Airflow, Kubernetes" \
  --preferred-skills "MLOps, NLP, TensorFlow, MLflow" \
  --location "Remoto"
```

### Desde la UI de Airflow

1. Ve a la UI de Airflow
2. Encuentra el DAG `job_description_ai_generator`
3. Haz clic en "Trigger DAG w/ config"
4. Pega esta configuración:

```json
{
  "role": "Gerente de Operaciones",
  "level": "Senior",
  "department": "Operaciones",
  "ai_experience_years": 3,
  "skills": ["Python", "Machine Learning", "Airflow", "Kubernetes"],
  "preferred_skills": ["MLOps", "NLP", "TensorFlow", "MLflow"],
  "location": "Remoto",
  "salary_range": "Competitivo"
}
```

---

## 🚀 Ejemplo 2: Data Scientist

### Configuración JSON

```json
{
  "role": "Data Scientist",
  "level": "Mid",
  "department": "Data Science",
  "ai_experience_years": 2,
  "skills": ["Python", "Pandas", "Scikit-learn", "SQL", "Jupyter"],
  "preferred_skills": ["TensorFlow", "PyTorch", "MLflow", "Spark"],
  "location": "Híbrido",
  "salary_range": "$70k-$100k"
}
```

### Comando CLI

```bash
python scripts/generate_job_description.py \
  --role "Data Scientist" \
  --level Mid \
  --department "Data Science" \
  --ai-experience-years 2 \
  --skills "Python, Pandas, Scikit-learn, SQL, Jupyter" \
  --preferred-skills "TensorFlow, PyTorch, MLflow, Spark" \
  --location "Híbrido" \
  --salary-range "$70k-$100k"
```

---

## 🚀 Ejemplo 3: MLOps Engineer

### Configuración JSON

```json
{
  "role": "MLOps Engineer",
  "level": "Senior",
  "department": "Engineering",
  "ai_experience_years": 4,
  "skills": ["Python", "Kubernetes", "Docker", "MLflow", "CI/CD"],
  "preferred_skills": ["Kubeflow", "KServe", "Terraform", "Helm", "Prometheus"],
  "location": "Remoto",
  "salary_range": "$120k-$160k"
}
```

---

## 🚀 Ejemplo 4: AI Researcher

### Configuración JSON

```json
{
  "role": "AI Researcher",
  "level": "Senior",
  "department": "Research",
  "ai_experience_years": 5,
  "skills": ["Python", "PyTorch", "TensorFlow", "Research", "Papers"],
  "preferred_skills": ["Transformers", "LLMs", "NLP", "Computer Vision", "Publications"],
  "location": "Híbrido",
  "salary_range": "Competitivo + Equity"
}
```

---

## 🚀 Ejemplo 5: Tech Lead - AI/ML

### Configuración JSON

```json
{
  "role": "Tech Lead - AI/ML",
  "level": "Lead",
  "department": "Engineering",
  "ai_experience_years": 6,
  "skills": ["Python", "Leadership", "Architecture", "ML", "System Design"],
  "preferred_skills": ["Team Management", "MLOps", "Cloud Architecture", "Strategy"],
  "location": "Remoto",
  "salary_range": "$150k-$200k + Equity"
}
```

---

## 📋 Activación de Onboarding

Una vez que un candidato acepta la oferta, activa el onboarding:

### Desde la UI de Airflow

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

### Desde Python

```python
from airflow.api.client.local_client import Client

client = Client(None, None)

config = {
    "candidate": {
        "name": "Juan Pérez",
        "email": "juan.perez@example.com",
        "role": "Gerente de Operaciones",
        "start_date": "2024-02-15",
        "manager": "manager@example.com",
        "department": "Operaciones"
    }
}

dag_run = client.trigger_dag(
    dag_id='job_description_ai_generator',
    conf=config
)
```

---

## 🔄 Flujo Completo

### Paso 1: Generar Descripción

```bash
python scripts/generate_job_description.py \
  --role "Gerente de Operaciones" \
  --level Senior \
  --output job_config.json
```

### Paso 2: Revisar y Publicar

1. Revisa la descripción generada en Airflow
2. Si está correcta, se publica automáticamente en los portales configurados

### Paso 3: Procesar Aplicaciones

Las aplicaciones se procesan automáticamente cuando llegan al sistema.

### Paso 4: Activar Onboarding

Cuando un candidato acepta:

```bash
# Activar onboarding manualmente
airflow dags trigger job_description_ai_generator \
  --conf '{
    "candidate": {
      "name": "Juan Pérez",
      "email": "juan.perez@example.com",
      "role": "Gerente de Operaciones",
      "start_date": "2024-02-15"
    }
  }'
```

---

## 📊 Monitoreo

### Ver Estado del DAG

```bash
# Listar ejecuciones
airflow dags list-runs -d job_description_ai_generator

# Ver logs de una tarea específica
airflow tasks logs job_description_ai_generator generate_description <run_id>
```

### Ver Resultados

Los resultados se pueden ver en:
- **XComs de Airflow**: Para la descripción generada
- **Variables de Airflow**: Para configuraciones
- **Logs**: Para debugging

---

## 🎯 Personalización por Industria

### Fintech

```json
{
  "role": "ML Engineer - Fintech",
  "skills": ["Python", "ML", "Risk Modeling", "Fraud Detection"],
  "preferred_skills": ["Time Series", "Anomaly Detection", "Regulatory Compliance"]
}
```

### Healthcare

```json
{
  "role": "AI Researcher - Healthcare",
  "skills": ["Python", "Medical Imaging", "NLP", "Clinical Data"],
  "preferred_skills": ["HIPAA Compliance", "Medical AI", "Research Publications"]
}
```

### E-commerce

```json
{
  "role": "Recommendation Systems Engineer",
  "skills": ["Python", "Recommendation Systems", "Collaborative Filtering"],
  "preferred_skills": ["Real-time ML", "A/B Testing", "Personalization"]
}
```

---

## 💡 Tips y Mejores Prácticas

1. **Sé específico con las habilidades**: Lista tecnologías concretas
2. **Ajusta el nivel según experiencia**: Junior (0-2 años), Mid (2-4), Senior (4+)
3. **Incluye ubicación clara**: Remoto, Híbrido, o ubicación específica
4. **Revisa siempre la descripción generada**: Aunque use IA, siempre revisa antes de publicar
5. **Personaliza por departamento**: Ajusta el lenguaje según la cultura del departamento

---

**Última actualización**: 2024






