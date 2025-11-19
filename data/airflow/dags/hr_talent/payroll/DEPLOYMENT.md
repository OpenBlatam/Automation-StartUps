# Guía de Despliegue - Sistema de Nómina

Guía completa para desplegar el sistema de nómina en producción.

## 📋 Requisitos Previos

### Base de Datos
- PostgreSQL 12+ instalado y configurado
- Acceso con permisos de creación de tablas
- Connection ID configurado en Airflow

### Dependencias Python
```bash
pip install -r requirements.txt
```

### Dependencias del Sistema (para OCR)
```bash
# Tesseract (Ubuntu/Debian)
sudo apt-get install tesseract-ocr

# Tesseract (macOS)
brew install tesseract

# Tesseract (Windows)
# Descargar desde: https://github.com/UB-Mannheim/tesseract/wiki
```

## 🚀 Instalación

### 1. Configurar Base de Datos

```bash
# Crear schema
psql $DATABASE_URL -f data/db/payroll_schema.sql

# O usando el script
python -m payroll.scripts.setup_schema --conn-id postgres_default
```

### 2. Configurar Variables de Entorno

```bash
# PostgreSQL
export PAYROLL_POSTGRES_CONN_ID=postgres_default

# OCR - Tesseract
export TESSERACT_CMD=/usr/bin/tesseract
export TESSERACT_LANG=eng

# OCR - AWS Textract (opcional)
export AWS_ACCESS_KEY_ID=your_key
export AWS_SECRET_ACCESS_KEY=your_secret
export AWS_REGION=us-east-1

# OCR - Google Vision (opcional)
export GOOGLE_APPLICATION_CREDENTIALS=/path/to/credentials.json
export GOOGLE_PROJECT_ID=your-project-id

# Notificaciones
export SLACK_WEBHOOK_URL=https://hooks.slack.com/...
export EMAIL_API_URL=https://api.example.com/email
export PAYROLL_WEBHOOK_URL=https://api.example.com/webhook

# Configuración de Nómina
export PAYROLL_REGULAR_HOURS_PER_WEEK=40.0
export PAYROLL_OVERTIME_MULTIPLIER=1.5
export PAYROLL_DEFAULT_TAX_RATE=0.25
export PAYROLL_DEFAULT_BENEFITS_RATE=0.10
```

### 3. Verificar Instalación

```bash
# Health check
python -m payroll.scripts.health_check --conn-id postgres_default

# Debe mostrar todos los checks como "healthy"
```

### 4. Configurar Airflow

```bash
# Los DAGs se detectarán automáticamente si están en dags/
# Verificar en Airflow UI:
# - payroll_processing
# - payroll_maintenance
```

## 🔧 Configuración Inicial

### 1. Crear Empleados

```sql
INSERT INTO payroll_employees (
    employee_id, name, email, position,
    hourly_rate, employee_type, department
) VALUES (
    'EMP001', 'John Doe', 'john@example.com', 'Engineer',
    25.00, 'hourly', 'Engineering'
);
```

### 2. Configurar Reglas de Deducción

```sql
INSERT INTO payroll_deduction_rules (
    rule_name, deduction_type, amount_type,
    percentage_value, priority
) VALUES (
    'Impuesto Federal', 'impuestos', 'percentage',
    0.15, 1
);
```

### 3. Configurar Períodos de Pago

Los períodos se calculan automáticamente, pero puedes configurarlos manualmente si es necesario.

## 📊 Monitoreo

### Health Checks

```bash
# Verificar salud del sistema
python -m payroll.scripts.health_check --conn-id postgres_default

# En JSON para automatización
python -m payroll.scripts.health_check --json
```

### Métricas en Airflow

- Verificar logs de los DAGs
- Monitorear métricas de Airflow
- Revisar XComs para datos intermedios

## 🧪 Testing

### Tests Unitarios

```bash
# Ejecutar tests
pytest data/airflow/dags/payroll/tests/

# Con coverage
pytest --cov=payroll data/airflow/dags/payroll/tests/
```

### Datos de Prueba

```python
from payroll.testing import PayrollTestData

# Crear empleado de prueba
employee = PayrollTestData.create_test_employee("TEST001")

# Crear entradas de tiempo
entries = PayrollTestData.create_test_time_entries(
    "TEST001",
    date(2025, 1, 1),
    date(2025, 1, 14)
)
```

## 🔄 Mantenimiento

### Mantenimiento Automático

El DAG `payroll_maintenance` se ejecuta automáticamente cada domingo a las 2 AM.

### Mantenimiento Manual

```python
from payroll import PayrollMaintenance

maintenance = PayrollMaintenance()

# Archivado
result = maintenance.archive_old_pay_periods(retention_days=365)

# Optimización
result = maintenance.optimize_tables()

# Limpieza
result = maintenance.cleanup_old_expense_receipts(retention_days=730)
```

## 🔐 Seguridad

### Configuración de Seguridad

1. **Variables de Entorno**: Nunca commitear secrets
2. **Acceso a Base de Datos**: Usar conexiones seguras
3. **Webhooks**: Configurar secret keys para verificación
4. **Auditoría**: Revisar logs regularmente

### Best Practices

- Usar secrets management (Vault, AWS Secrets Manager)
- Rotar credenciales regularmente
- Monitorear acceso a datos sensibles
- Implementar rate limiting en APIs

## 📈 Escalabilidad

### Optimización de Rendimiento

- Ajustar `batch_size` en BatchProcessor
- Configurar `max_workers` según recursos
- Usar caché para consultas frecuentes
- Optimizar índices de base de datos

### Monitoreo de Recursos

- Monitorear uso de CPU/memoria
- Ajustar recursos de Airflow workers
- Optimizar queries según necesidad
- Usar connection pooling

## 🐛 Troubleshooting

### Problemas Comunes

#### Schema no encontrado
```bash
# Verificar schema
psql $DATABASE_URL -c "\dt payroll_*"

# Recrear si es necesario
psql $DATABASE_URL -f data/db/payroll_schema.sql
```

#### OCR falla
```bash
# Verificar Tesseract
tesseract --version

# Verificar variables de entorno
echo $TESSERACT_CMD
```

#### Errores de conexión
```bash
# Verificar conexión
python -m payroll.scripts.health_check --conn-id postgres_default
```

## 📚 Recursos

- [README.md](README.md) - Documentación completa
- [API.md](API.md) - Referencia de API
- [EXAMPLES.md](EXAMPLES.md) - Ejemplos de uso
- [FEATURES.md](FEATURES.md) - Lista de características

## 🆘 Soporte

Para problemas o preguntas:
1. Revisar logs de Airflow
2. Verificar health checks
3. Consultar documentación
4. Revisar CHANGELOG.md para cambios recientes

