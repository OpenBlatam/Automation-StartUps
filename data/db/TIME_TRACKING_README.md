# Sistema de Gestión de Tiempo y Asistencia - Guía Completa

## 📋 Resumen Ejecutivo

Sistema completo para gestión automática de tiempo y asistencia que:
- ✅ Registra entradas/salidas automáticamente
- ✅ Calcula horas trabajadas con precisión
- ✅ Procesa nómina automáticamente
- ✅ Gestiona vacaciones y permisos
- ✅ Reduce errores y disputas de tiempo trabajado

## 🚀 Instalación Rápida

### 1. Ejecutar Esquema de Base de Datos

```bash
# Ejecutar esquema de time tracking
psql $DATABASE_URL -f data/db/time_tracking_schema.sql

# Asegurar que el esquema de nómina esté creado (si no existe)
psql $DATABASE_URL -f data/db/payroll_schema.sql
```

### 2. Verificar DAGs en Airflow

Los siguientes DAGs estarán disponibles:

- `time_tracking_automation` - Ejecuta cada 15 minutos
- `time_tracking_vacations` - Ejecuta diariamente a las 9 AM
- `time_tracking_disputes` - Ejecuta cada 6 horas

## 📊 Estructura de Tablas

### Tablas Principales

1. **time_tracking_clock_events**
   - Almacena todos los eventos de clock in/out
   - Soporta múltiples métodos (web, móvil, kiosk, API, biométrico)
   - Tracking de ubicación y dispositivo

2. **time_tracking_work_sessions**
   - Sesiones de trabajo completas
   - Cálculo de horas regulares y overtime
   - Estado: open, closed, disputed, approved, rejected

3. **time_tracking_vacations**
   - Solicitudes de vacaciones
   - Tipos: vacation, sick, personal, bereavement, jury_duty, military
   - Estados: pending, approved, rejected, cancelled, taken

4. **time_tracking_leave_requests**
   - Solicitudes de permisos
   - Soporta medio día y horas específicas

5. **time_tracking_vacation_balances**
   - Saldos de vacaciones por empleado
   - Acumulación automática
   - Tracking de días usados y disponibles

6. **time_tracking_disputes**
   - Disputas de tiempo trabajado
   - Flujo de resolución completo
   - Evidencia y documentación

7. **time_tracking_schedules**
   - Configuración de horarios por empleado
   - Soporta horarios fijos, flexibles, por turnos y remotos

8. **time_tracking_alerts**
   - Sistema de alertas y notificaciones
   - Tipos: missing_clock_in, missing_clock_out, late_clock_in, etc.

## 🔄 Flujos Automatizados

### 1. Registro de Clock In/Out

```
Empleado → Clock In → Sesión Abierta
              ↓
        Trabajo
              ↓
         Clock Out → Cálculo de Horas → Aprobación → Sincronización con Nómina
```

### 2. Gestión de Vacaciones

```
Solicitud → Validación → Aprobación/Rechazo → Actualización de Saldo
```

### 3. Disputas

```
Disputa → Revisión → Resolución → Actualización de Registros
```

## 💻 Uso Programático

### Clock In/Out

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

# Iniciar sesión
session_id = session_manager.start_session(
    employee_id="EMP001",
    location="Office A"
)

# Cerrar sesión
session_manager.end_session(employee_id="EMP001")
```

### Solicitud de Vacaciones

```python
from time_tracking import VacationManager, VacationType
from datetime import date

vacation_manager = VacationManager(storage)

request_id = vacation_manager.request_vacation(
    employee_id="EMP001",
    vacation_type=VacationType.VACATION,
    start_date=date(2025, 2, 1),
    end_date=date(2025, 2, 5)
)
```

### Envío de Disputa

```python
from time_tracking import DisputeManager, DisputeType
from decimal import Decimal

dispute_manager = DisputeManager(storage)

dispute_id = dispute_manager.submit_dispute(
    employee_id="EMP001",
    dispute_type=DisputeType.MISSING_CLOCK,
    dispute_date=date(2025, 1, 15),
    description="I forgot to clock out",
    requested_hours=Decimal("8.0")
)
```

## 📈 Consultas Útiles

### Horas Trabajadas por Empleado

```sql
SELECT 
    employee_id,
    work_date,
    total_hours,
    regular_hours,
    overtime_hours,
    status
FROM time_tracking_work_sessions
WHERE employee_id = 'EMP001'
    AND work_date >= CURRENT_DATE - INTERVAL '30 days'
ORDER BY work_date DESC;
```

### Resumen Mensual

```sql
SELECT 
    employee_id,
    month,
    days_worked,
    total_hours,
    regular_hours,
    overtime_hours
FROM mv_time_tracking_monthly_summary
WHERE employee_id = 'EMP001'
ORDER BY month DESC;
```

### Disputas Abiertas

```sql
SELECT 
    id,
    employee_id,
    dispute_type,
    dispute_date,
    description,
    status,
    priority
FROM time_tracking_disputes
WHERE status IN ('open', 'under_review')
ORDER BY priority DESC, dispute_date DESC;
```

### Saldos de Vacaciones

```sql
SELECT 
    employee_id,
    vacation_days_available,
    sick_days_available,
    personal_days_available
FROM time_tracking_vacation_balances
WHERE employee_id = 'EMP001'
    AND year = EXTRACT(YEAR FROM CURRENT_DATE);
```

## 🔔 Notificaciones Automáticas

El sistema envía notificaciones automáticas para:

1. **Clock Out Faltante**: Cuando un empleado tiene más de 8 horas sin clock out
2. **Saldos Bajos**: Cuando quedan menos de 5 días de vacaciones
3. **Disputas**: Cuando se envía o resuelve una disputa
4. **Discrepancias**: Cuando se detectan anomalías en registros

## ⚙️ Configuración

### Parámetros de DAG

#### time_tracking_automation
- `auto_close_stale_hours`: Horas después de las cuales cerrar sesiones (default: 24)
- `check_all_employees`: Verificar todos los empleados (default: true)
- `employee_ids`: Lista de IDs específicos (opcional)

#### time_tracking_vacations
- `auto_approve_vacations`: Auto-aprobar solicitudes válidas (default: false)
- `notify_balance_threshold`: Días para notificar saldo bajo (default: 5)

#### time_tracking_disputes
- `auto_resolve_disputes`: Auto-resolver disputas válidas (default: false)

## 🔍 Validaciones Implementadas

1. **Clock In**: Verifica que no haya sesión abierta y que el empleado esté activo
2. **Clock Out**: Verifica que haya sesión abierta y que el tiempo sea válido
3. **Vacaciones**: Valida saldo disponible y solapamiento con otras solicitudes
4. **Disputas**: Valida evidencia y reglas de negocio

## 📊 Integración con Nómina

El sistema se integra automáticamente con `payroll_time_entries`:

1. Las sesiones cerradas y aprobadas se sincronizan automáticamente
2. Las horas se calculan (regulares, overtime)
3. Los períodos de pago se generan desde las entradas de tiempo

## 🛡️ Mejores Prácticas

1. **Configurar Horarios**: Definir horarios esperados para cada empleado
2. **Revisar Disputas**: Revisar disputas regularmente
3. **Actualizar Saldos**: Ejecutar actualización de acumulación mensualmente
4. **Monitorear Alertas**: Revisar alertas activas regularmente
5. **Validar Sincronización**: Verificar que las horas se sincronicen con nómina

## 🐛 Troubleshooting

### Sesiones No Se Cierran Automáticamente

Verificar que el DAG `time_tracking_automation` esté ejecutándose correctamente.

### Horas No Se Sincronizan con Nómina

Verificar:
1. Que las sesiones estén aprobadas (`approved = true`)
2. Que el estado sea `closed`
3. Que no existan entradas duplicadas en `payroll_time_entries`

### Saldos de Vacaciones Incorrectos

Ejecutar manualmente la actualización de acumulación:
```sql
-- Ver saldo actual
SELECT * FROM time_tracking_vacation_balances
WHERE employee_id = 'EMP001';

-- Actualizar acumulación (ejemplo)
UPDATE time_tracking_vacation_balances
SET vacation_days_accrued = 10.0,
    vacation_days_available = 10.0 - vacation_days_used
WHERE employee_id = 'EMP001';
```

## 📚 Referencias

- Esquema completo: `/data/db/time_tracking_schema.sql`
- Módulos Python: `/data/airflow/dags/time_tracking/`
- DAGs: 
  - `/data/airflow/dags/time_tracking_automation.py`
  - `/data/airflow/dags/time_tracking_vacations.py`
  - `/data/airflow/dags/time_tracking_disputes.py`
- Documentación detallada: `/data/airflow/dags/time_tracking/README.md`

