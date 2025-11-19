# Casos de Uso - Sistema de Nómina

Casos de uso complejos y escenarios reales del sistema de nómina.

## 🎯 Caso de Uso 1: Procesamiento Completo de Nómina Semanal

### Escenario
Procesar nómina semanal para 500 empleados con múltiples tipos de horas, deducciones personalizadas y gastos reembolsables.

### Solución

```python
from payroll import (
    PayrollStorage,
    HourCalculator,
    DeductionCalculator,
    PaymentCalculator,
    BatchProcessor,
    PayrollNotifier,
    PayrollReporter,
    get_pay_period_dates
)
from datetime import date, timedelta

# Setup
storage = PayrollStorage()
period_start, period_end = get_pay_period_dates(period_type="weekly")
hour_calc = HourCalculator()
deduction_calc = DeductionCalculator()
payment_calc = PaymentCalculator(hour_calc, deduction_calc)
notifier = PayrollNotifier()

# Procesar en lotes
batch_processor = BatchProcessor()

def process_employee(employee):
    # Obtener datos
    time_entries = storage.get_time_entries(
        employee["employee_id"], period_start, period_end
    )
    expenses = storage.get_expenses_total(
        employee["employee_id"], period_start, period_end
    )
    
    # Calcular
    calculation = payment_calc.calculate_pay_period(
        employee_id=employee["employee_id"],
        hourly_rate=employee["hourly_rate"],
        employee_type=employee["employee_type"],
        period_start=period_start,
        period_end=period_end,
        pay_date=period_end + timedelta(days=3),
        time_entries=time_entries,
        expenses_total=expenses,
        employee_context=employee.get("metadata", {})
    )
    
    # Guardar
    pay_period_id = storage.save_pay_period(calculation)
    
    # Notificar
    notifier.notify_payroll_completed(
        employee_id=employee["employee_id"],
        employee_name=employee["name"],
        period_start=period_start,
        period_end=period_end,
        net_pay=calculation.net_pay
    )
    
    return {"success": True, "pay_period_id": pay_period_id}

# Obtener todos los empleados
employees = storage.list_active_employees()

# Procesar en lotes
results = batch_processor.process_batch(
    items=employees,
    processor_func=process_employee,
    batch_size=50,
    max_workers=4
)

# Generar reporte
reporter = PayrollReporter()
report = reporter.generate_period_report(period_start, period_end)

print(f"Processed {results['successful']} employees")
print(f"Total Net Pay: ${report.total_net_pay}")
```

## 🎯 Caso de Uso 2: Procesamiento OCR Masivo con Fallback

### Escenario
Procesar 1000 recibos de gastos con OCR, usando múltiples proveedores como fallback.

### Solución

```python
from payroll import (
    OCRProcessor,
    PayrollStorage,
    PayrollCircuitBreakers,
    PayrollRateLimiter
)

# Setup
storage = PayrollStorage()
circuit_breakers = PayrollCircuitBreakers()
rate_limiter = PayrollRateLimiter()

# Proveedores con orden de prioridad
providers = ["aws_textract", "google_vision", "tesseract"]

def process_receipt_with_fallback(receipt):
    """Procesa recibo con fallback automático"""
    image_data = receipt.get("image_data")
    
    for provider in providers:
        try:
            # Verificar rate limit
            if not rate_limiter.check_ocr_request():
                time.sleep(1)
                continue
            
            # Procesar con circuit breaker
            processor = OCRProcessor(provider=provider)
            result = circuit_breakers.call_ocr(
                processor.process_receipt,
                image_data
            )
            
            if result.success:
                # Guardar resultado
                storage.save_expense_receipt(
                    employee_id=receipt["employee_id"],
                    expense_date=receipt["expense_date"],
                    ocr_result=result,
                    receipt_image_base64=receipt["image_base64"]
                )
                return {"success": True, "provider": provider}
            
        except Exception as e:
            logger.warning(f"OCR failed with {provider}: {e}")
            continue
    
    # Si todos fallan, marcar para revisión manual
    return {"success": False, "requires_manual_review": True}

# Procesar todos los recibos
receipts = storage.get_pending_expense_receipts()

for receipt in receipts:
    result = process_receipt_with_fallback(receipt)
    if not result["success"]:
        # Notificar para revisión manual
        notifier.notify_expense_requires_review(
            receipt["employee_id"],
            receipt["id"],
            amount=None
        )
```

## 🎯 Caso de Uso 3: Sistema de Aprobaciones Multi-Nivel

### Escenario
Aprobaciones automáticas para gastos pequeños, aprobación de manager para gastos medianos, y aprobación de director para gastos grandes.

### Solución

```python
from payroll import (
    PayrollApprovalSystem,
    ApprovalLevel,
    PayrollStorage,
    PayrollNotifier
)

approval_system = PayrollApprovalSystem()
storage = PayrollStorage()
notifier = PayrollNotifier()

def process_expense_approval(expense):
    """Procesa aprobación de gasto según monto"""
    amount = expense["amount"]
    
    # Auto-aprobación para gastos pequeños
    if amount <= 50.00:
        storage.update_expense_status(expense["id"], "approved")
        return {"status": "auto_approved"}
    
    # Aprobación de manager para gastos medianos
    elif amount <= 500.00:
        approval_id = approval_system.request_approval(
            entity_type="expense",
            entity_id=expense["id"],
            employee_id=expense["employee_id"],
            approval_level=ApprovalLevel.MANAGER,
            requested_by="system",
            metadata={"amount": float(amount)}
        )
        notifier.notify_expense_requires_review(
            expense["employee_id"],
            expense["id"],
            amount
        )
        return {"status": "pending_manager", "approval_id": approval_id}
    
    # Aprobación de director para gastos grandes
    else:
        approval_id = approval_system.request_approval(
            entity_type="expense",
            entity_id=expense["id"],
            employee_id=expense["employee_id"],
            approval_level=ApprovalLevel.DIRECTOR,
            requested_by="system",
            metadata={"amount": float(amount)}
        )
        notifier.notify_expense_requires_review(
            expense["employee_id"],
            expense["id"],
            amount
        )
        return {"status": "pending_director", "approval_id": approval_id}
```

## 🎯 Caso de Uso 4: Detección y Alerta de Anomalías

### Escenario
Detectar anomalías en pagos y alertar automáticamente a los managers.

### Solución

```python
from payroll import (
    PayrollAnalytics,
    PayrollAlertSystem,
    PayrollNotifier,
    AlertSeverity
)

analytics = PayrollAnalytics()
alert_system = PayrollAlertSystem()
notifier = PayrollNotifier()

def detect_and_alert_anomalies(period_start, period_end):
    """Detecta anomalías y envía alertas"""
    # Detectar anomalías
    anomalies = analytics.detect_anomalies(
        period_start, period_end,
        threshold_std=2.0
    )
    
    # Filtrar anomalías críticas
    critical_anomalies = [
        a for a in anomalies
        if a.severity == "high"
    ]
    
    # Verificar alertas del sistema
    alerts = alert_system.run_all_checks(period_start, period_end)
    
    # Enviar notificaciones
    for anomaly in critical_anomalies:
        notifier._send_notification(
            f"🚨 Anomalía detectada: {anomaly.employee_id} - {anomaly.description}",
            "anomaly_detected",
            {
                "employee_id": anomaly.employee_id,
                "anomaly_type": anomaly.anomaly_type,
                "value": float(anomaly.value)
            }
        )
    
    for alert in alerts:
        if alert.severity == AlertSeverity.CRITICAL:
            notifier._send_notification(
                f"🚨 Alerta crítica: {alert.message}",
                "critical_alert",
                {
                    "alert_type": alert.alert_type.value,
                    "employee_id": alert.employee_id
                }
            )
    
    return {
        "anomalies": len(anomalies),
        "critical_anomalies": len(critical_anomalies),
        "alerts": len(alerts)
    }
```

## 🎯 Caso de Uso 5: Integración Completa con QuickBooks

### Escenario
Sincronizar períodos de pago completos con QuickBooks después de procesar nómina.

### Solución

```python
from payroll import (
    QuickBooksIntegration,
    PayrollStorage,
    PayrollSync,
    PayrollReporter
)

qb = QuickBooksIntegration(
    access_token="your_token",
    realm_id="your_realm_id"
)

storage = PayrollStorage()
sync = PayrollSync()
reporter = PayrollReporter()

def sync_period_to_quickbooks(period_start, period_end):
    """Sincroniza período completo con QuickBooks"""
    # Obtener datos del período
    report = reporter.generate_period_report(period_start, period_end)
    
    # Preparar datos para QuickBooks
    period_data = {
        "period_start": str(period_start),
        "period_end": str(period_end),
        "pay_date": str(report.pay_date),
        "total_net_pay": float(report.total_net_pay),
        "employees": []
    }
    
    # Obtener empleados del período
    sql = """
        SELECT DISTINCT employee_id, net_pay
        FROM payroll_pay_periods
        WHERE period_start = %s AND period_end = %s
    """
    
    results = storage.hook.get_records(
        sql,
        parameters=(period_start, period_end)
    )
    
    for row in results:
        employee = storage.get_employee(row[0])
        period_data["employees"].append({
            "employee_id": row[0],
            "name": employee["name"],
            "net_pay": float(row[1])
        })
    
    # Sincronizar con QuickBooks
    try:
        qb.sync_payroll_period(period_data)
        
        # Marcar como sincronizado
        pay_period_ids = storage.hook.get_records(
            "SELECT id FROM payroll_pay_periods WHERE period_start = %s AND period_end = %s",
            parameters=(period_start, period_end)
        )
        
        for pay_period_id, in pay_period_ids:
            sync.mark_synced(
                entity_type="pay_period",
                entity_id=pay_period_id,
                external_id=f"QB-{period_start}-{period_end}"
            )
        
        return {"success": True, "synced_employees": len(period_data["employees"])}
        
    except Exception as e:
        logger.error(f"Error syncing to QuickBooks: {e}")
        return {"success": False, "error": str(e)}
```

## 🎯 Caso de Uso 6: Sistema de Recovery Automático

### Escenario
Recuperación automática de cálculos fallidos con análisis de causa raíz.

### Solución

```python
from payroll import (
    PayrollRecovery,
    PayrollStorage,
    PaymentCalculator,
    PayrollNotifier
)

recovery = PayrollRecovery()
storage = PayrollStorage()
notifier = PayrollNotifier()

def recover_failed_calculations():
    """Recupera cálculos fallidos automáticamente"""
    # Obtener operaciones fallidas
    failed_ops = recovery.get_failed_operations(hours=24)
    
    recovered = 0
    needs_manual = []
    
    for op in failed_ops:
        if op["operation_type"] == "pay_period":
            # Generar plan de recuperación
            plan = recovery.recover_failed_calculation(
                op["employee_id"],
                op["period_start"],
                op["period_end"]
            )
            
            if plan.action == "retry":
                # Intentar recalcular
                try:
                    employee = storage.get_employee(op["employee_id"])
                    time_entries = storage.get_time_entries(
                        op["employee_id"],
                        op["period_start"],
                        op["period_end"]
                    )
                    
                    # Recalcular
                    calculation = payment_calc.calculate_pay_period(...)
                    storage.save_pay_period(calculation)
                    
                    recovered += 1
                    logger.info(f"Recovered pay period for {op['employee_id']}")
                    
                except Exception as e:
                    needs_manual.append({
                        "operation": op,
                        "error": str(e),
                        "plan": plan
                    })
            
            elif plan.action == "manual_intervention":
                needs_manual.append({
                    "operation": op,
                    "plan": plan
                })
    
    # Notificar resultados
    if recovered > 0:
        notifier._send_notification(
            f"✅ Recovered {recovered} failed calculations",
            "recovery_completed",
            {"recovered": recovered}
        )
    
    if needs_manual:
        notifier._send_notification(
            f"⚠️ {len(needs_manual)} operations need manual intervention",
            "manual_intervention_required",
            {"count": len(needs_manual)}
        )
    
    return {
        "recovered": recovered,
        "needs_manual": len(needs_manual),
        "manual_operations": needs_manual
    }
```

## 🎯 Caso de Uso 7: Dashboard en Tiempo Real

### Escenario
Generar datos para dashboard web en tiempo real con múltiples métricas.

### Solución

```python
from payroll import (
    PayrollDashboard,
    PayrollMetricsCollector,
    PayrollAnalytics,
    PayrollAlertSystem
)

dashboard = PayrollDashboard()
metrics = PayrollMetricsCollector()
analytics = PayrollAnalytics()
alerts = PayrollAlertSystem()

def generate_realtime_dashboard():
    """Genera datos completos para dashboard"""
    # Obtener datos del dashboard
    dashboard_data = dashboard.get_dashboard_data()
    
    # Obtener KPIs
    kpis = dashboard.get_kpi_summary()
    
    # Obtener métricas
    period_metrics = metrics.collect_period_metrics(
        dashboard_data.period_start,
        dashboard_data.period_end
    )
    
    # Obtener alertas
    alerts_summary = alerts.run_all_checks(
        dashboard_data.period_start,
        dashboard_data.period_end
    )
    
    # Obtener series temporales
    time_series = dashboard.get_time_series_data(periods=12)
    
    # Análisis de costos
    cost_analysis = analytics.cost_analysis(
        dashboard_data.period_start,
        dashboard_data.period_end
    )
    
    return {
        "dashboard": dashboard.export_for_dashboard(dashboard_data),
        "kpis": kpis,
        "metrics": {
            "period": period_metrics,
            "cost": cost_analysis
        },
        "alerts": alerts.get_alerts_summary(alerts_summary),
        "time_series": time_series
    }
```

## 🎯 Caso de Uso 8: Compliance Automático

### Escenario
Verificar compliance legal automáticamente antes de procesar pagos.

### Solución

```python
from payroll import (
    PayrollCompliance,
    PayrollStorage,
    PayrollNotifier
)

compliance = PayrollCompliance()
storage = PayrollStorage()
notifier = PayrollNotifier()

def verify_compliance_before_payment(employee_id, period_start, period_end):
    """Verifica compliance antes de procesar pago"""
    employee = storage.get_employee(employee_id)
    
    # Obtener datos del período
    sql = """
        SELECT gross_pay, total_deductions, pay_date
        FROM payroll_pay_periods
        WHERE employee_id = %s
            AND period_start = %s
            AND period_end = %s
    """
    
    result = storage.hook.get_first(
        sql,
        parameters=(employee_id, period_start, period_end)
    )
    
    if not result:
        return {"compliant": False, "error": "Period not found"}
    
    gross_pay = Decimal(str(result[0]))
    tax_withheld = Decimal(str(result[1]))
    pay_date = result[2]
    
    # Ejecutar todas las verificaciones
    violations = compliance.run_all_checks(
        employee_id=employee_id,
        period_start=period_start,
        period_end=period_end,
        hourly_rate=employee["hourly_rate"],
        pay_date=pay_date,
        gross_pay=gross_pay,
        tax_withheld=tax_withheld
    )
    
    # Filtrar violaciones legales
    legal_violations = [
        v for v in violations
        if v.severity == ComplianceSeverity.LEGAL
    ]
    
    if legal_violations:
        # Notificar violaciones legales
        notifier._send_notification(
            f"🚨 Legal compliance violations for {employee_id}",
            "compliance_violation",
            {
                "employee_id": employee_id,
                "violations": len(legal_violations),
                "details": [v.message for v in legal_violations]
            }
        )
        
        return {
            "compliant": False,
            "violations": legal_violations,
            "can_proceed": False
        }
    
    return {
        "compliant": True,
        "violations": violations,
        "can_proceed": True
    }
```

## 📚 Más Información

- [Examples](EXAMPLES.md) - Ejemplos básicos
- [API](API.md) - Referencia de API
- [Integration](INTEGRATION.md) - Guía de integraciones

