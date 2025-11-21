# ⚡ Quick Start Guide

> **Versión**: 1.0 | **Última actualización**: 2024

Guía rápida para empezar a trabajar con la plataforma en 15 minutos.

## 📋 Tabla de Contenidos

- [Setup Inicial (5 minutos)](#-setup-inicial-5-minutos)
- [Crear tu Primer DAG (5 minutos)](#-crear-tu-primer-dag-5-minutos)
- [Ejecutar y Monitorear (5 minutos)](#-ejecutar-y-monitorear-5-minutos)
- [Siguientes Pasos](#-siguientes-pasos)

---

## 🚀 Setup Inicial (5 minutos)

### 1. Clonar y Configurar

```bash
# Clonar repositorio
git clone <repository-url>
cd IA

# Crear entorno virtual
python -m venv venv
source venv/bin/activate  # En Windows: venv\Scripts\activate

# Instalar dependencias
pip install -r data/airflow/requirements.txt
```

### 2. Configurar Variables de Entorno

```bash
# Copiar archivo de ejemplo
cp data/airflow/ENV_EXAMPLE .env

# Editar con tus valores
vim .env  # o nano, o tu editor preferido
```

### 3. Iniciar Airflow Localmente (Opcional)

```bash
cd data/airflow
docker-compose up -d

# Verificar que está corriendo
docker-compose ps
```

### 4. Acceder a Airflow UI

```bash
# Abrir en navegador
open http://localhost:8080  # macOS
# o
xdg-open http://localhost:8080  # Linux

# Credenciales por defecto:
# Usuario: airflow
# Contraseña: airflow
```

---

## ✈️ Crear tu Primer DAG (5 minutos)

### DAG Mínimo

Crea el archivo `data/airflow/dags/mi_primer_dag.py`:

```python
"""
Mi primer DAG de Airflow.
"""
from __future__ import annotations
from datetime import timedelta
import pendulum
from airflow.decorators import dag, task

@dag(
    dag_id="mi_primer_dag",
    description="Mi primer DAG de ejemplo",
    schedule_interval="@daily",
    start_date=pendulum.datetime(2024, 1, 1, tz="UTC"),
    catchup=False,
    tags=["ejemplo", "quickstart"],
)
def mi_primer_dag():
    
    @task
    def saludar():
        """Tarea que imprime un saludo."""
        print("¡Hola desde Airflow!")
        return {"mensaje": "¡Hola desde Airflow!"}
    
    @task
    def procesar(saludo):
        """Procesa el resultado anterior."""
        mensaje = saludo["mensaje"]
        print(f"Procesando: {mensaje}")
        return {"procesado": True, "mensaje": mensaje}
    
    # Flujo del DAG
    saludo = saludar()
    procesar(saludo)

mi_primer_dag()
```

### Verificar que el DAG se Cargó

```bash
# Listar DAGs
airflow dags list | grep mi_primer_dag

# Ver detalles
airflow dags show mi_primer_dag

# Verificar que no hay errores
airflow dags list-import-errors
```

---

## 🎯 Ejecutar y Monitorear (5 minutos)

### Ejecutar el DAG

```bash
# Ejecutar manualmente
airflow dags trigger mi_primer_dag

# O desde la UI de Airflow
# 1. Ir a http://localhost:8080
# 2. Encontrar "mi_primer_dag" en la lista
# 3. Click en el botón "Play" (▶️)
```

### Monitorear Ejecución

```bash
# Ver estado del DAG
airflow dags state mi_primer_dag 2024-01-01

# Ver logs
airflow tasks logs mi_primer_dag saludar 2024-01-01

# O desde la UI:
# 1. Click en el DAG
# 2. Click en la ejecución
# 3. Ver logs de cada tarea
```

### Verificar Resultados

```bash
# Ver logs de una tarea específica
airflow tasks logs mi_primer_dag procesar 2024-01-01

# Deberías ver:
# "Procesando: ¡Hola desde Airflow!"
```

---

## 📚 Siguientes Pasos

### 1. Explorar Ejemplos

- Ver [`docs/EJEMPLOS_PRACTICOS.md`](./EJEMPLOS_PRACTICOS.md) para más ejemplos
- Explorar DAGs existentes en `data/airflow/dags/`

### 2. Leer Documentación Completa

- [`docs/DESARROLLO.md`](./DESARROLLO.md) - Guía completa de desarrollo
- [`docs/ARQUITECTURA.md`](./ARQUITECTURA.md) - Arquitectura del sistema
- [`data/airflow/dags/INDEX_ETL_IMPROVED.md`](../data/airflow/dags/INDEX_ETL_IMPROVED.md) - Guía ETL

### 3. Crear DAGs Más Complejos

- Agregar conexiones a base de datos
- Usar plugins modulares
- Implementar retry logic
- Agregar notificaciones

### 4. Ejemplos Avanzados

```python
# DAG con base de datos
from airflow.providers.postgres.hooks.postgres import PostgresHook

@task
def consultar_bd():
    hook = PostgresHook(postgres_conn_id="postgres_default")
    result = hook.get_records("SELECT COUNT(*) FROM tabla")
    return {"count": result[0][0]}

# DAG con retry
@task(retries=3, retry_delay=timedelta(minutes=2))
def tarea_con_retry():
    # Tu código aquí
    pass
```

---

## 🐛 Problemas Comunes

### El DAG no aparece en la UI

**Solución**:
```bash
# Verificar que no hay errores de importación
airflow dags list-import-errors

# Verificar que el archivo está en el directorio correcto
ls -la data/airflow/dags/mi_primer_dag.py

# Reiniciar scheduler
docker-compose restart airflow-scheduler
```

### Error de conexión a base de datos

**Solución**:
```bash
# Verificar que la conexión existe
airflow connections list | grep postgres

# Crear conexión si no existe
airflow connections add postgres_default \
  --conn-type postgres \
  --conn-host localhost \
  --conn-login user \
  --conn-password password \
  --conn-port 5432 \
  --conn-schema mydb
```

### Tarea falla

**Solución**:
```bash
# Ver logs detallados
airflow tasks logs mi_primer_dag saludar 2024-01-01

# Verificar que las dependencias están instaladas
pip list | grep airflow
```

---

## 📖 Recursos Adicionales

- [Documentación de Airflow](https://airflow.apache.org/docs/)
- [Ejemplos Oficiales](https://airflow.apache.org/docs/apache-airflow/stable/howto/operator/index.html)
- [`docs/EJEMPLOS_PRACTICOS.md`](./EJEMPLOS_PRACTICOS.md) - Más ejemplos

---

## ✅ Checklist de Quick Start

- [ ] Repositorio clonado
- [ ] Entorno virtual creado
- [ ] Dependencias instaladas
- [ ] Variables de entorno configuradas
- [ ] Primer DAG creado
- [ ] DAG ejecutado exitosamente
- [ ] Logs verificados
- [ ] Documentación explorada

---

**Versión**: 1.0 | **Estado**: Producción Ready ✅  
**Mantenido por**: platform-team  
**Última actualización**: 2024

