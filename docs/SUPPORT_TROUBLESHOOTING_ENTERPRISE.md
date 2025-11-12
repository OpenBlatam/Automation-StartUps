# 🏢 Sistema Enterprise de Troubleshooting - Guía Completa

## 📋 Resumen

Sistema enterprise completo que aprovecha todas las funcionalidades avanzadas del schema de troubleshooting, incluyendo API keys, SLAs, escalación automática, y métricas de calidad.

## 🎯 Funcionalidades Enterprise

### 1. Sistema de API Keys

**Autenticación y autorización avanzada:**
- Generación segura de API keys
- Validación con IP y origen
- Rate limiting por key
- Permisos granulares
- Expiración automática
- Revocación de keys

```python
from workflow.kestra.flows.lib.support_troubleshooting_enterprise import (
    TroubleshootingEnterprise
)

enterprise = TroubleshootingEnterprise(db_connection=db_conn)

# Crear API key
result = enterprise.create_api_key(
    key_name="Production API",
    owner_email="admin@example.com",
    permissions={"read": True, "write": False},
    rate_limit=1000,
    allowed_ips=["192.168.1.0/24"],
    expires_at=datetime.now() + timedelta(days=90)
)

# Validar API key
validation = enterprise.validate_api_key(
    api_key="ts_...",
    ip_address="192.168.1.100",
    origin="https://app.example.com"
)
```

### 2. SLAs (Service Level Agreements)

**Cumplimiento y métricas de SLA:**
- Definición de SLAs por problema y cliente
- Cálculo automático de cumplimiento
- Métricas de tiempo de resolución
- Alertas de incumplimiento
- Reportes de cumplimiento

```python
# Verificar cumplimiento de SLA
compliance = enterprise.check_sla_compliance(session_id="TSESS-123")

print(f"Score de cumplimiento: {compliance['overall_compliance_score']}")
print(f"Todos los SLAs cumplidos: {compliance['all_slas_met']}")

# Obtener métricas de SLA
metrics = enterprise.get_sla_metrics(
    date_from=datetime.now() - timedelta(days=30)
)

for sla in metrics["metrics"]:
    print(f"{sla['sla_name']}: {sla['overall_compliance_rate']:.1f}%")
```

### 3. Escalación Automática

**Escalación basada en reglas:**
- Reglas configurables de escalación
- Escalación automática por tiempo
- Escalación por fallos consecutivos
- Escalación por prioridad
- Notificaciones automáticas

```python
# Verificar y ejecutar escalación automática
escalation = enterprise.auto_escalate_if_needed(session_id="TSESS-123")

if escalation:
    print(f"Escalado a: {escalation['target_department']}")
    print(f"Nivel: {escalation['escalation_level']}")
```

### 4. Métricas de Calidad

**Análisis de calidad del servicio:**
- Tasa de resolución
- Tasa de escalación
- Satisfacción del cliente
- Tiempo promedio de resolución
- Tasa de completación

```python
# Obtener métricas de calidad
quality = enterprise.get_quality_metrics(
    date_from=datetime.now() - timedelta(days=30)
)

print(f"Tasa de resolución: {quality['quality_metrics']['resolution_rate']:.1f}%")
print(f"Satisfacción promedio: {quality['quality_metrics']['avg_satisfaction']:.1f}/5.0")
```

### 5. Mantenimiento Automático

**Tareas de mantenimiento:**
- Limpieza de cache
- Refresco de vistas materializadas
- Optimización de índices
- Limpieza de datos antiguos

```python
# Ejecutar mantenimiento
maintenance = enterprise.perform_maintenance(maintenance_type="all")

print(f"Tareas completadas: {len(maintenance['tasks_completed'])}")
print(f"Cache limpiado: {maintenance['cache_cleaned']} entradas")
```

## 🔄 Integración Completa

### Con Sistema de ML

```python
from workflow.kestra.flows.lib.support_troubleshooting_ml_integration import (
    TroubleshootingMLIntegration
)
from workflow.kestra.flows.lib.support_troubleshooting_enterprise import (
    TroubleshootingEnterprise
)

ml = TroubleshootingMLIntegration(db_connection=db_conn)
enterprise = TroubleshootingEnterprise(db_connection=db_conn)

# Predecir resultado
prediction = ml.predict_outcome(problem_description="...")

# Verificar SLA
compliance = enterprise.check_sla_compliance(session_id="...")

# Escalar si es necesario
escalation = enterprise.auto_escalate_if_needed(session_id="...")
```

### Con Templates

```python
from workflow.kestra.flows.lib.support_troubleshooting_templates import (
    get_troubleshooting_escalation_template
)

# Si se detecta escalación automática
if escalation:
    response = get_troubleshooting_escalation_template(
        ticket_data=ticket_data,
        escalation_reason=f"Escalado automáticamente a {escalation['target_department']}",
        steps_attempted=current_step,
        language="es"
    )
```

## 📊 Dashboard Enterprise

### Métricas Clave

1. **Cumplimiento de SLA**
   - Tasa de cumplimiento por SLA
   - Tiempo promedio de resolución vs objetivo
   - Sesiones en riesgo de incumplimiento

2. **Calidad del Servicio**
   - Tasa de resolución
   - Satisfacción del cliente
   - Tasa de escalación
   - Tiempo promedio de resolución

3. **Performance**
   - Sesiones activas
   - Throughput diario
   - Tiempo promedio por paso
   - Problemas más comunes

4. **Seguridad**
   - Uso de API keys
   - Intentos de acceso fallidos
   - Rate limiting activo

## 🛠️ Configuración Enterprise

### SLAs

```sql
-- Crear SLA para clientes Enterprise
INSERT INTO support_troubleshooting_slas (
    sla_name,
    description,
    target_resolution_time_minutes,
    target_response_time_minutes,
    priority_level,
    applicable_customer_tiers
) VALUES (
    'Enterprise SLA',
    'SLA para clientes Enterprise',
    60,  -- 1 hora
    15,  -- 15 minutos
    'high',
    ARRAY['enterprise', 'vip']
);
```

### Reglas de Escalación

```sql
-- Crear regla de escalación automática
INSERT INTO support_troubleshooting_escalation_rules (
    rule_name,
    condition_type,
    condition_value,
    escalation_level,
    target_department
) VALUES (
    'Timeout Escalation',
    'duration_exceeds',
    3600,  -- 1 hora
    2,
    'technical_support'
);
```

## 📈 Reportes Enterprise

### Reporte de Cumplimiento de SLA

```python
metrics = enterprise.get_sla_metrics(
    date_from=datetime.now() - timedelta(days=30)
)

# Generar reporte
for sla in metrics["metrics"]:
    print(f"""
    SLA: {sla['sla_name']}
    Sesiones totales: {sla['total_sessions']}
    Tasa de cumplimiento: {sla['overall_compliance_rate']:.1f}%
    Score promedio: {sla['avg_compliance_score']:.1f}/100
    Tiempo promedio de retraso: {sla['avg_time_overdue_minutes']:.1f} minutos
    """)
```

### Reporte de Calidad

```python
quality = enterprise.get_quality_metrics()

print(f"""
REPORTE DE CALIDAD
==================
Período: {quality['period']['from']} a {quality['period']['to']}

Sesiones:
  Total: {quality['sessions']['total']}
  Resueltas: {quality['sessions']['resolved']}
  Escaladas: {quality['sessions']['escalated']}

Métricas de Calidad:
  Tasa de resolución: {quality['quality_metrics']['resolution_rate']:.1f}%
  Satisfacción promedio: {quality['quality_metrics']['avg_satisfaction']:.1f}/5.0
  Tasa de alta satisfacción: {quality['quality_metrics']['high_satisfaction_rate']:.1f}%
  Tasa de completación: {quality['quality_metrics']['completion_rate']:.1f}%
""")
```

## 🔒 Seguridad Enterprise

### Gestión de API Keys

```python
# Crear key con restricciones
key = enterprise.create_api_key(
    key_name="Mobile App",
    owner_email="mobile@example.com",
    permissions={"read": True, "write": False, "escalate": False},
    rate_limit=500,
    allowed_ips=["10.0.0.0/8"],
    allowed_origins=["https://mobile.example.com"],
    expires_at=datetime.now() + timedelta(days=180)
)

# Revocar key comprometida
enterprise.revoke_api_key(api_key_hash="...")
```

## 🎯 Mejores Prácticas Enterprise

1. **SLAs**
   - Definir SLAs realistas
   - Monitorear cumplimiento diariamente
   - Ajustar SLAs según datos históricos

2. **Escalación**
   - Configurar reglas de escalación claras
   - Revisar reglas regularmente
   - Ajustar umbrales según performance

3. **API Keys**
   - Usar keys específicas por aplicación
   - Implementar rate limiting apropiado
   - Rotar keys regularmente
   - Revocar keys no utilizadas

4. **Mantenimiento**
   - Ejecutar mantenimiento semanalmente
   - Monitorear tamaño de cache
   - Optimizar índices mensualmente

## 📚 Referencias

- [Sistema Avanzado](./SUPPORT_TROUBLESHOOTING_ADVANCED.md)
- [Integración ML](./support_troubleshooting_ml_integration.py)
- [Templates](./support_troubleshooting_templates.py)
- [Schema de BD](../../data/db/support_troubleshooting_schema.sql)

---

**Versión**: 3.0 Enterprise  
**Última actualización**: Diciembre 2024  
**Mantenido por**: Equipo de Automatización de Soporte



