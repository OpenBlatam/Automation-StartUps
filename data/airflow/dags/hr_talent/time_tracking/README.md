# Sistema de Gestión de Tiempo y Asistencia

Sistema completo para registro automático de entradas/salidas, cálculo de horas trabajadas, procesamiento de nómina, gestión de vacaciones y permisos. Reduce errores y disputas de tiempo trabajado.

## 📋 Características Principales

### 1. Registro Automático de Entradas/Salidas
- ✅ Clock in/out automático con múltiples métodos (web, móvil, kiosk, API, biométrico)
- ✅ Tracking de ubicación (GPS, IP, oficina)
- ✅ Detección automática de sesiones abiertas sin clock out
- ✅ Cierre automático de sesiones antiguas
- ✅ Validación de reglas de negocio

### 2. Cálculo Automático de Horas Trabajadas
- ✅ Cálculo preciso de horas regulares, overtime y double time
- ✅ Manejo automático de breaks y descansos
- ✅ Cálculo semanal y mensual
- ✅ Integración con sistema de nómina

### 3. Procesamiento de Nómina
- ✅ Sincronización automática con `payroll_time_entries`
- ✅ Cálculo de horas pagadas
- ✅ Aprobación automática de horas validadas
- ✅ Generación de períodos de pago

### 4. Gestión de Vacaciones y Permisos
- ✅ Solicitud y aprobación de vacaciones
- ✅ Cálculo automático de saldos de vacaciones
- ✅ Acumulación automática de días
- ✅ Notificaciones de saldos bajos
- ✅ Gestión de diferentes tipos de permisos

### 5. Sistema de Disputas
- ✅ Envío de disputas de tiempo trabajado
- ✅ Revisión y validación automática
- ✅ Resolución con evidencia
- ✅ Notificaciones automáticas
- ✅ Reducción de errores y malentendidos

## 🏗️ Arquitectura

```
time_tracking/
├── __init__.py              # Exports principales
├── storage.py               # Almacenamiento en PostgreSQL
├── clock_manager.py         # Gestión de clock in/out
├── session_manager.py       # Gestión de sesiones de trabajo
├── hour_calculator.py       # Cálculo de horas trabajadas
├── vacation_manager.py      # Gestión de vacaciones
├── dispute_manager.py       # Gestión de disputas
├── validators.py            # Validación de datos
└── notifications.py        # Sistema de notificaciones
```

## 📊 Esquema de Base de Datos

El esquema completo está en `/data/db/time_tracking_schema.sql` e incluye:

### Tablas Principales

1. **time_tracking_clock_events**: Eventos de clock in/out
2. **time_tracking_work_sessions**: Sesiones de trabajo
3. **time_tracking_breaks**: Breaks y descansos
4. **time_tracking_vacations**: Solicitudes de vacaciones
5. **time_tracking_leave_requests**: Solicitudes de permisos
6. **time_tracking_vacation_balances**: Saldos de vacaciones
7. **time_tracking_disputes**: Disputas de tiempo
8. **time_tracking_schedules**: Configuración de horarios
9. **time_tracking_alerts**: Alertas y notificaciones

### Vistas Materializadas

- `mv_time_tracking_daily_summary`: Resumen diario por empleado
- `mv_time_tracking_monthly_summary`: Resumen mensual por empleado

## 🔄 DAGs de Airflow

### 1. `time_tracking_automation`
**Schedule**: Cada 15 minutos

Funcionalidades:
- Cierre automático de sesiones antiguas
- Detección de clock out faltante
- Detección de discrepancias
- Sincronización con nómina

### 2. `time_tracking_vacations`
**Schedule**: Diario a las 9 AM

Funcionalidades:
- Procesamiento de solicitudes pendientes
- Verificación de saldos bajos
- Actualización de acumulación

### 3. `time_tracking_disputes`
**Schedule**: Cada 6 horas

Funcionalidades:
- Revisión de disputas abiertas
- Notificaciones de disputas pendientes

## 🚀 Uso

### Instalación

1. Ejecutar el esquema de base de datos:
```bash
psql $DATABASE_URL -f data/db/time_tracking_schema.sql
```

2. Asegurar que el esquema de nómina esté creado:
```bash
psql $DATABASE_URL -f data/db/payroll_schema.sql
```

### Registro de Clock In/Out

```python
from time_tracking import (
    TimeTrackingStorage,
    ClockManager,
    SessionManager,
    TimeTrackingHourCalculator,
)

storage = TimeTrackingStorage(postgres_conn_id="postgres_default")
clock_manager = ClockManager(storage)
hour_calculator = TimeTrackingHourCalculator(storage)
session_manager = SessionManager(storage, clock_manager, hour_calculator)

# Clock in
session_id = session_manager.start_session(
    employee_id="EMP001",
    location="Office A",
    notes="Starting work"
)

# Clock out
session_manager.end_session(
    employee_id="EMP001",
    notes="Ending work"
)
```

### Solicitud de Vacaciones

```python
from time_tracking import VacationManager, VacationType

vacation_manager = VacationManager(storage)

request_id = vacation_manager.request_vacation(
    employee_id="EMP001",
    vacation_type=VacationType.VACATION,
    start_date=date(2025, 2, 1),
    end_date=date(2025, 2, 5),
    notes="Family vacation"
)
```

### Envío de Disputa

```python
from time_tracking import DisputeManager, DisputeType

dispute_manager = DisputeManager(storage)

dispute_id = dispute_manager.submit_dispute(
    employee_id="EMP001",
    dispute_type=DisputeType.MISSING_CLOCK,
    dispute_date=date(2025, 1, 15),
    description="I forgot to clock out",
    requested_hours=Decimal("8.0"),
    current_hours=Decimal("0.0")
)
```

## 📈 Integración con Nómina

El sistema se integra automáticamente con el sistema de nómina existente:

1. Las sesiones de trabajo cerradas y aprobadas se sincronizan a `payroll_time_entries`
2. Las horas se calculan automáticamente (regulares, overtime)
3. Los períodos de pago se generan desde las entradas de tiempo

## 🔍 Validaciones

El sistema incluye validaciones robustas:

- Verificación de empleados activos
- Validación de fechas y horas
- Detección de sesiones duplicadas
- Verificación de saldos de vacaciones
- Detección de discrepancias automáticas

## 📊 Reportes

Las vistas materializadas proporcionan reportes rápidos:

```sql
-- Resumen diario
SELECT * FROM mv_time_tracking_daily_summary
WHERE employee_id = 'EMP001'
ORDER BY work_date DESC;

-- Resumen mensual
SELECT * FROM mv_time_tracking_monthly_summary
WHERE employee_id = 'EMP001'
ORDER BY month DESC;
```

## 🔔 Notificaciones

El sistema envía notificaciones automáticas para:

- Clock out faltante
- Saldos bajos de vacaciones
- Disputas enviadas
- Disputas resueltas
- Alertas de discrepancias

## 🛡️ Seguridad

- Validación de empleados activos
- Verificación de permisos
- Auditoría completa de cambios
- Trazabilidad de todas las operaciones

## 📝 Mejores Prácticas

1. **Configurar horarios**: Definir horarios esperados para cada empleado
2. **Revisar disputas**: Revisar disputas regularmente para mantener datos precisos
3. **Actualizar saldos**: Ejecutar actualización de acumulación mensualmente
4. **Monitorear alertas**: Revisar alertas activas regularmente
5. **Validar sincronización**: Verificar que las horas se sincronicen correctamente con nómina

## 🔧 Configuración

### Variables de Entorno

- `POSTGRES_CONN_ID`: ID de conexión de Airflow para PostgreSQL (default: `postgres_default`)

### Parámetros de DAG

Cada DAG acepta parámetros configurables para personalizar el comportamiento.

## 📚 Referencias

- Esquema de base de datos: `/data/db/time_tracking_schema.sql`
- Esquema de nómina: `/data/db/payroll_schema.sql`
- DAGs de nómina: `/data/airflow/dags/payroll_processing.py`

