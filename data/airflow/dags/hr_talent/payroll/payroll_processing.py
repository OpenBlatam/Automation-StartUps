"""
DAG de Procesamiento de Nómina y Gastos
Automatiza el cálculo de horas, deducciones, pagos y procesamiento de recibos con OCR
"""

from __future__ import annotations

from datetime import timedelta, datetime, date
from typing import Any, Dict, List, Optional
import logging
import base64
import os

import pendulum
from airflow.decorators import dag, task
from airflow.models.param import Param
from airflow.providers.postgres.hooks.postgres import PostgresHook

from payroll import (
    HourCalculator,
    DeductionCalculator,
    PaymentCalculator,
    OCRProcessor,
    PayrollStorage,
    PayrollConfig,
    TimeEntry,
    HoursType,
    get_pay_period_dates,
    format_currency,
    PayrollError,
    ValidationError,
    CalculationError,
    PayrollNotifier,
    PayrollReporter,
    PayrollValidator,
    PayrollMetricsCollector,
    PayrollHealthChecker,
    PayrollApprovalSystem,
    ApprovalLevel,
    BatchProcessor,
    performance_monitor,
    PayrollAnalytics,
    PayrollDashboard,
    PayrollAlertSystem,
    AlertType,
    AlertSeverity,
)
from payroll.deduction_calculator import DeductionRule

logger = logging.getLogger(__name__)


@dag(
    dag_id="payroll_processing",
    start_date=pendulum.datetime(2025, 1, 1, tz="UTC"),
    schedule="0 8 * * 1",  # Cada lunes a las 8 AM
    catchup=False,
    default_args={
        "owner": "hr",
        "retries": 2,
        "retry_delay": timedelta(minutes=5),
        "retry_exponential_backoff": True,
        "max_retry_delay": timedelta(minutes=30),
        "depends_on_past": False,
    },
    doc_md="""
    ### Procesamiento Automatizado de Nómina y Gastos
    
    Sistema completo para automatizar el procesamiento de nómina:
    
    **Funcionalidades principales:**
    - Procesamiento de recibos de gastos con OCR (Tesseract, AWS Textract, Google Vision)
    - Cálculo automático de horas trabajadas (regulares, overtime, double time)
    - Cálculo de deducciones (impuestos, beneficios, personalizadas)
    - Cálculo de pagos netos
    - Almacenamiento completo en PostgreSQL
    - Reportes y métricas
    
    **Parámetros:**
    - `postgres_conn_id`: Connection ID para Postgres (default: postgres_default)
    - `ocr_provider`: Proveedor OCR (tesseract, aws_textract, google_vision)
    - `period_start`: Fecha inicio del período (formato: YYYY-MM-DD)
    - `period_end`: Fecha fin del período (formato: YYYY-MM-DD)
    - `pay_date`: Fecha de pago (formato: YYYY-MM-DD)
    - `auto_approve_expenses`: Auto-aprobar gastos bajo un monto (default: false)
    - `auto_approve_expenses_threshold`: Umbral para auto-aprobación (default: 50.0)
    - `process_all_employees`: Procesar todos los empleados activos (default: true)
    - `employee_ids`: Lista de IDs de empleados específicos (opcional, formato: "id1,id2,id3")
    
    **Requisitos:**
    - Schema `payroll_schema.sql` debe estar ejecutado en Postgres
    - Para OCR: instalar dependencias según proveedor:
      - Tesseract: `pip install pytesseract pillow`
      - AWS Textract: `pip install boto3`
      - Google Vision: `pip install google-cloud-vision`
    """,
    params={
        "postgres_conn_id": Param("postgres_default", type="string", minLength=1),
        "ocr_provider": Param("tesseract", type="string", enum=["tesseract", "aws_textract", "google_vision"]),
        "period_start": Param("", type="string"),  # Se calculará automáticamente si está vacío
        "period_end": Param("", type="string"),  # Se calculará automáticamente si está vacío
        "pay_date": Param("", type="string"),  # Se calculará automáticamente si está vacío
        "auto_approve_expenses": Param(False, type="boolean"),
        "auto_approve_expenses_threshold": Param(50.0, type="number", minimum=0),
        "process_all_employees": Param(True, type="boolean"),
        "employee_ids": Param("", type="string"),  # CSV de IDs
        "dry_run": Param(False, type="boolean"),
    },
    tags=["payroll", "hr", "automation", "ocr", "financial"],
)
def payroll_processing() -> None:
    """DAG principal para procesamiento de nómina"""
    
    @task
    def ensure_schema(**context) -> bool:
        """Verifica que el schema de nómina esté creado"""
        params = context["params"]
        config = PayrollConfig.from_env()
        config.postgres_conn_id = params.get("postgres_conn_id", "postgres_default")
        
        storage = PayrollStorage(postgres_conn_id=config.postgres_conn_id)
        exists = storage.ensure_schema()
        
        if not exists:
            logger.warning(
                "Payroll schema not found. Please execute: "
                "psql $DATABASE_URL -f data/db/payroll_schema.sql"
            )
        
        # Verificar salud del sistema
        health_checker = PayrollHealthChecker(postgres_conn_id=config.postgres_conn_id)
        health = health_checker.comprehensive_health_check()
        
        if health["overall_status"] == "critical":
            logger.error(f"Critical health issues detected: {health}")
            raise PayrollError("System health check failed")
        
        return exists
    
    @task
    def process_expense_receipts(**context) -> Dict[str, Any]:
        """Procesa recibos de gastos pendientes con OCR"""
        params = context["params"]
        config = PayrollConfig.from_env()
        
        # Configurar OCR
        ocr_provider = params.get("ocr_provider", "tesseract")
        ocr_config = {
            "ocr_provider": ocr_provider,
            "ocr_confidence_threshold": config.ocr_confidence_threshold,
        }
        
        # Agregar configuración específica del proveedor
        if ocr_provider == "aws_textract":
            ocr_config.update({
                "aws_access_key_id": config.aws_access_key_id,
                "aws_secret_access_key": config.aws_secret_access_key,
                "aws_region": config.aws_region,
            })
        elif ocr_provider == "google_vision":
            ocr_config.update({
                "google_credentials_path": config.google_credentials_path,
                "google_project_id": config.google_project_id,
            })
        elif ocr_provider == "tesseract":
            ocr_config.update({
                "tesseract_cmd": config.tesseract_cmd,
                "tesseract_lang": config.tesseract_lang,
            })
        
        ocr_processor = OCRProcessor(**ocr_config)
        storage = PayrollStorage(postgres_conn_id=config.postgres_conn_id)
        
        # Obtener recibos pendientes
        hook = PostgresHook(postgres_conn_id=config.postgres_conn_id)
        sql = """
            SELECT id, employee_id, receipt_image_base64, expense_date
            FROM payroll_expense_receipts
            WHERE ocr_status IN ('pending', 'failed')
            ORDER BY created_at
            LIMIT 100
        """
        
        receipts = hook.get_records(sql)
        
        processed = 0
        successful = 0
        failed = 0
        
        for receipt_id, employee_id, image_base64, expense_date in receipts:
            try:
                if not image_base64:
                    logger.warning(f"Receipt {receipt_id} has no image data")
                    continue
                
                # Decodificar imagen
                image_data = base64.b64decode(image_base64)
                
                # Procesar con OCR
                ocr_result = ocr_processor.process_receipt(image_data)
                
                if ocr_result.success and ocr_result.confidence >= config.ocr_confidence_threshold:
                    # Actualizar recibo con datos extraídos
                    extracted = ocr_result.extracted_data
                    amount = Decimal(str(extracted.get("amount") or extracted.get("total") or 0))
                    
                    update_sql = """
                        UPDATE payroll_expense_receipts
                        SET 
                            amount = COALESCE(amount, %s),
                            vendor = COALESCE(vendor, %s),
                            description = COALESCE(description, %s),
                            ocr_status = 'completed',
                            ocr_confidence = %s,
                            ocr_extracted_data = %s,
                            ocr_processed_at = NOW(),
                            updated_at = NOW()
                        WHERE id = %s
                    """
                    
                    hook.run(
                        update_sql,
                        parameters=(
                            float(amount),
                            extracted.get("vendor"),
                            str(extracted),
                            float(ocr_result.confidence),
                            str(ocr_result.extracted_data),
                            receipt_id
                        )
                    )
                    
                    successful += 1
                    
                    # Auto-aprobar si está configurado
                    if params.get("auto_approve_expenses", False):
                        threshold = Decimal(str(params.get("auto_approve_expenses_threshold", 50.0)))
                        if amount <= threshold:
                            storage.approve_expense_receipt(receipt_id, "system_auto")
                            logger.info(f"Auto-approved receipt {receipt_id} (amount: {amount})")
                else:
                    # Marcar como fallido o necesitando revisión manual
                    status = "failed" if not ocr_result.success else "manual_review"
                    update_sql = """
                        UPDATE payroll_expense_receipts
                        SET ocr_status = %s,
                            ocr_confidence = %s,
                            ocr_processed_at = NOW(),
                            updated_at = NOW()
                        WHERE id = %s
                    """
                    hook.run(
                        update_sql,
                        parameters=(
                            status,
                            float(ocr_result.confidence) if ocr_result else 0.0,
                            receipt_id
                        )
                    )
                    failed += 1
                
                processed += 1
                
            except Exception as e:
                logger.error(f"Error processing receipt {receipt_id}: {e}")
                failed += 1
        
        return {
            "processed": processed,
            "successful": successful,
            "failed": failed
        }
    
    @task
    def calculate_payroll(**context) -> Dict[str, Any]:
        """Calcula nómina para el período especificado"""
        params = context["params"]
        config = PayrollConfig.from_env()
        
        # Determinar período
        period_start_str = params.get("period_start", "")
        period_end_str = params.get("period_end", "")
        pay_date_str = params.get("pay_date", "")
        
        if not period_start_str or not period_end_str:
            # Calcular período automáticamente (biweekly)
            period_start, period_end = get_pay_period_dates(period_type="biweekly")
        else:
            period_start = datetime.strptime(period_start_str, "%Y-%m-%d").date()
            period_end = datetime.strptime(period_end_str, "%Y-%m-%d").date()
        
        if not pay_date_str:
            pay_date = period_end + timedelta(days=7)  # Una semana después del período
        else:
            pay_date = datetime.strptime(pay_date_str, "%Y-%m-%d").date()
        
        # Validar rango de fechas
        from payroll.utils import validate_date_range
        is_valid, error = validate_date_range(period_start, period_end)
        if not is_valid:
            raise ValidationError(f"Invalid date range: {error}")
        
        logger.info(f"Processing payroll for period: {period_start} to {period_end}, pay date: {pay_date}")
        
        # Inicializar calculadoras
        hour_calculator = HourCalculator(
            regular_hours_per_week=config.regular_hours_per_week,
            overtime_multiplier=config.overtime_multiplier,
            double_time_multiplier=config.double_time_multiplier,
        )
        
        deduction_calculator = DeductionCalculator(
            default_tax_rate=config.default_tax_rate,
            default_benefits_rate=config.default_benefits_rate,
        )
        
        # Cargar reglas de deducción desde DB
        hook = PostgresHook(postgres_conn_id=config.postgres_conn_id)
        rules_sql = """
            SELECT rule_name, deduction_type, employee_type, amount_type,
                   amount_value, percentage_value, formula, conditions, priority
            FROM payroll_deduction_rules
            WHERE enabled = true
            ORDER BY priority DESC
        """
        rules_data = hook.get_records(rules_sql)
        
        for rule_data in rules_data:
            rule = DeductionRule(
                rule_name=rule_data[0],
                deduction_type=rule_data[1],
                employee_type=rule_data[2],
                amount_type=rule_data[3],
                amount_value=Decimal(str(rule_data[4])) if rule_data[4] else None,
                percentage_value=Decimal(str(rule_data[5])) if rule_data[5] else None,
                formula=rule_data[6],
                conditions=rule_data[7] if isinstance(rule_data[7], dict) else (rule_data[7] if rule_data[7] else {}),
                priority=rule_data[8] or 0,
            )
            deduction_calculator.add_rule(rule)
        
        payment_calculator = PaymentCalculator(hour_calculator, deduction_calculator)
        storage = PayrollStorage(postgres_conn_id=config.postgres_conn_id)
        
        # Obtener empleados a procesar
        if params.get("process_all_employees", True):
            employees = storage.list_active_employees()
        else:
            employee_ids_str = params.get("employee_ids", "")
            employee_ids = [eid.strip() for eid in employee_ids_str.split(",") if eid.strip()]
            employees = [storage.get_employee(eid) for eid in employee_ids]
            employees = [e for e in employees if e]
        
        results = {
            "processed": 0,
            "successful": 0,
            "failed": 0,
            "total_gross_pay": 0.0,
            "total_net_pay": 0.0,
            "employees": []
        }
        
        dry_run = params.get("dry_run", False)
        
        # Inicializar notificador
        notifier = PayrollNotifier(
            slack_webhook_url=os.getenv("SLACK_WEBHOOK_URL"),
            email_api_url=os.getenv("EMAIL_API_URL"),
            webhook_url=os.getenv("PAYROLL_WEBHOOK_URL")
        )
        
        # Inicializar validador
        validator = PayrollValidator()
        
        # Inicializar sistema de aprobaciones
        approval_system = PayrollApprovalSystem(
            postgres_conn_id=config.postgres_conn_id
        )
        approval_system.ensure_approval_tables()
        
        # Procesar empleados en lotes para mejor rendimiento
        @performance_monitor
        def process_employee(employee: Dict[str, Any]) -> Dict[str, Any]:
            """Procesa un empleado individual"""
            employee_id = employee["employee_id"]
            hourly_rate = employee["hourly_rate"] or Decimal("0.00")
            employee_type = employee["employee_type"]
            
            try:
                # Obtener entradas de tiempo
                time_entries = storage.get_time_entries(employee_id, period_start, period_end)
                
                # Validar entradas de tiempo
                is_valid, error, warnings = validator.validate_time_entries(
                    time_entries, period_start, period_end
                )
                if not is_valid:
                    error_msg = f"Validation failed for {employee_id}: {error}"
                    logger.error(error_msg)
                    if not dry_run:
                        notifier.notify_payroll_error(employee_id, error_msg)
                    return {"success": False, "employee_id": employee_id, "error": error_msg}
                
                if warnings:
                    for warning in warnings:
                        logger.warning(f"{employee_id}: {warning}")
                
                # Obtener total de gastos
                expenses_total = storage.get_expenses_total(employee_id, period_start, period_end)
                
                # Calcular pago
                calculation = payment_calculator.calculate_pay_period(
                    employee_id=employee_id,
                    hourly_rate=hourly_rate,
                    employee_type=employee_type,
                    period_start=period_start,
                    period_end=period_end,
                    pay_date=pay_date,
                    time_entries=time_entries,
                    expenses_total=expenses_total,
                    employee_context=employee.get("metadata", {})
                )
                
                # Validar cálculo
                is_valid, error = payment_calculator.validate_calculation(calculation)
                if not is_valid:
                    error_msg = f"Invalid calculation for {employee_id}: {error}"
                    logger.error(error_msg)
                    if not dry_run:
                        raise CalculationError(error_msg, employee_id=employee_id)
                    return {"success": False, "employee_id": employee_id, "error": error_msg}
                
                # Validar cálculo con reglas de negocio
                is_valid, error = validator.validate_gross_pay(
                    calculation.gross_pay,
                    calculation.total_hours,
                    hourly_rate
                )
                if not is_valid:
                    logger.warning(f"{employee_id}: {error}")
                
                is_valid, error = validator.validate_deductions(
                    calculation.gross_pay,
                    calculation.total_deductions
                )
                if not is_valid:
                    logger.warning(f"{employee_id}: {error}")
                
                # Guardar en DB (si no es dry_run)
                pay_period_id = None
                if not dry_run:
                    pay_period_id = storage.save_pay_period(calculation)
                    logger.info(
                        f"Saved pay period {pay_period_id} for {employee_id}: "
                        f"${calculation.net_pay} (gross: ${calculation.gross_pay}, "
                        f"deductions: ${calculation.total_deductions}, "
                        f"expenses: ${calculation.total_expenses})"
                    )
                    
                    # Solicitar aprobación si el monto es alto
                    if calculation.net_pay > Decimal("5000.00"):
                        approval_id = approval_system.request_approval(
                            entity_type="pay_period",
                            entity_id=pay_period_id,
                            employee_id=employee_id,
                            approval_level=ApprovalLevel.MANAGER,
                            requested_by="system",
                            metadata={
                                "net_pay": float(calculation.net_pay),
                                "gross_pay": float(calculation.gross_pay)
                            }
                        )
                        logger.info(f"Approval requested for pay period {pay_period_id}: {approval_id}")
                    
                    # Notificar
                    notifier.notify_payroll_completed(
                        employee_id=employee_id,
                        employee_name=employee["name"],
                        period_start=period_start,
                        period_end=period_end,
                        net_pay=calculation.net_pay,
                        details={
                            "hours": float(calculation.total_hours),
                            "deductions": float(calculation.total_deductions),
                            "expenses": float(calculation.total_expenses)
                        }
                    )
                else:
                    logger.info(
                        f"[DRY RUN] Would save for {employee_id}: "
                        f"net_pay=${calculation.net_pay}, "
                        f"hours={calculation.total_hours}"
                    )
                
                return {
                    "success": True,
                    "employee_id": employee_id,
                    "net_pay": float(calculation.net_pay),
                    "gross_pay": float(calculation.gross_pay),
                    "hours": float(calculation.total_hours),
                    "pay_period_id": pay_period_id
                }
                
            except Exception as e:
                logger.error(f"Error processing payroll for {employee.get('employee_id', 'unknown')}: {e}")
                if not dry_run:
                    notifier.notify_payroll_error(
                        employee.get("employee_id", "unknown"),
                        str(e)
                    )
                return {"success": False, "employee_id": employee.get("employee_id"), "error": str(e)}
        
        # Procesar en lotes para mejor rendimiento
        batch_processor = BatchProcessor()
        batch_results = batch_processor.process_batch(
            items=employees,
            processor_func=process_employee,
            batch_size=50,
            max_workers=4
        )
        
        # Procesar resultados del batch processor
        # Los resultados ya vienen en el formato correcto del BatchProcessor
        results["processed"] = batch_results.get("processed", 0)
        results["successful"] = batch_results.get("successful", 0)
        results["failed"] = batch_results.get("failed", 0)
        
        # Extraer totales de los resultados procesados
        # Necesitamos procesar los items originales para obtener los totales
        for item_result in batch_results.get("results", []):
            if item_result.get("success"):
                results["total_gross_pay"] += item_result.get("gross_pay", 0.0)
                results["total_net_pay"] += item_result.get("net_pay", 0.0)
                results["employees"].append({
                    "employee_id": item_result.get("employee_id"),
                    "net_pay": item_result.get("net_pay", 0.0),
                    "hours": item_result.get("hours", 0.0)
                })
        
        logger.info(
            f"Payroll processing complete: {results['successful']} successful, "
            f"{results['failed']} failed. Total gross: ${results['total_gross_pay']:.2f}, "
            f"Total net: ${results['total_net_pay']:.2f}"
        )
        
        # Notificar resumen
        if not dry_run:
            notifier.notify_batch_summary(
                total_processed=results["processed"],
                successful=results["successful"],
                failed=results["failed"],
                total_gross=Decimal(str(results["total_gross_pay"])),
                total_net=Decimal(str(results["total_net_pay"]))
            )
        
        return results
    
    @task
    def generate_reports(**context) -> Dict[str, Any]:
        """Genera reportes del período procesado"""
        params = context["params"]
        config = PayrollConfig.from_env()
        
        # Determinar período
        period_start_str = params.get("period_start", "")
        period_end_str = params.get("period_end", "")
        
        if not period_start_str or not period_end_str:
            period_start, period_end = get_pay_period_dates(period_type="biweekly")
        else:
            period_start = datetime.strptime(period_start_str, "%Y-%m-%d").date()
            period_end = datetime.strptime(period_end_str, "%Y-%m-%d").date()
        
        reporter = PayrollReporter(postgres_conn_id=config.postgres_conn_id)
        
        # Generar reportes
        period_report = reporter.generate_period_report(period_start, period_end)
        expense_report = reporter.generate_expense_report(period_start, period_end)
        
        logger.info(
            f"Generated reports for period {period_start} to {period_end}: "
            f"{period_report.employee_count} employees, "
            f"${period_report.total_net_pay} total net pay"
        )
        
        return {
            "period_report": reporter.export_to_dict(period_report),
            "expense_report": expense_report,
            "period_start": str(period_start),
            "period_end": str(period_end)
        }
    
    @task
    def detect_anomalies(**context) -> Dict[str, Any]:
        """Detecta anomalías en los cálculos de nómina"""
        params = context["params"]
        config = PayrollConfig.from_env()
        
        # Determinar período
        period_start_str = params.get("period_start", "")
        period_end_str = params.get("period_end", "")
        
        if not period_start_str or not period_end_str:
            period_start, period_end = get_pay_period_dates(period_type="biweekly")
        else:
            period_start = datetime.strptime(period_start_str, "%Y-%m-%d").date()
            period_end = datetime.strptime(period_end_str, "%Y-%m-%d").date()
        
        analytics = PayrollAnalytics(postgres_conn_id=config.postgres_conn_id)
        
        # Detectar anomalías
        anomalies = analytics.detect_anomalies(
            period_start, period_end,
            threshold_std=2.0
        )
        
        # Agrupar por severidad
        high_severity = [a for a in anomalies if a.severity == "high"]
        medium_severity = [a for a in anomalies if a.severity == "medium"]
        low_severity = [a for a in anomalies if a.severity == "low"]
        
        logger.info(
            f"Anomalies detected: {len(high_severity)} high, "
            f"{len(medium_severity)} medium, {len(low_severity)} low"
        )
        
        # Notificar anomalías críticas
        if high_severity:
            notifier = PayrollNotifier(
                slack_webhook_url=os.getenv("SLACK_WEBHOOK_URL")
            )
            
            for anomaly in high_severity:
                notifier._send_notification(
                    f"⚠️ Anomalía detectada: {anomaly.employee_id} - {anomaly.description}",
                    "anomaly_detected",
                    {
                        "employee_id": anomaly.employee_id,
                        "anomaly_type": anomaly.anomaly_type,
                        "severity": anomaly.severity,
                        "value": float(anomaly.value)
                    }
                )
        
        return {
            "total_anomalies": len(anomalies),
            "high_severity": len(high_severity),
            "medium_severity": len(medium_severity),
            "low_severity": len(low_severity),
            "anomalies": [
                {
                    "employee_id": a.employee_id,
                    "type": a.anomaly_type,
                    "severity": a.severity,
                    "value": float(a.value),
                    "description": a.description
                }
                for a in anomalies
            ]
        }
    
    @task
    def collect_metrics(**context) -> Dict[str, Any]:
        """Recolecta métricas del período procesado"""
        params = context["params"]
        config = PayrollConfig.from_env()
        
        # Determinar período
        period_start_str = params.get("period_start", "")
        period_end_str = params.get("period_end", "")
        
        if not period_start_str or not period_end_str:
            period_start, period_end = get_pay_period_dates(period_type="biweekly")
        else:
            period_start = datetime.strptime(period_start_str, "%Y-%m-%d").date()
            period_end = datetime.strptime(period_end_str, "%Y-%m-%d").date()
        
        metrics_collector = PayrollMetricsCollector(
            postgres_conn_id=config.postgres_conn_id
        )
        
        # Recolectar métricas
        period_metrics = metrics_collector.collect_period_metrics(
            period_start, period_end
        )
        
        department_metrics = metrics_collector.get_department_metrics(
            period_start, period_end
        )
        
        expense_metrics = metrics_collector.get_expense_metrics(
            period_start, period_end
        )
        
        logger.info(
            f"Metrics collected: {period_metrics.total_employees} employees, "
            f"${period_metrics.total_net_pay} total net pay"
        )
        
        return {
            "period_metrics": {
                "total_employees": period_metrics.total_employees,
                "total_gross_pay": float(period_metrics.total_gross_pay),
                "total_net_pay": float(period_metrics.total_net_pay),
                "total_hours": float(period_metrics.total_hours),
                "overtime_percentage": float(period_metrics.overtime_percentage)
            },
            "department_metrics": department_metrics,
            "expense_metrics": expense_metrics
        }
    
    @task
    def check_alerts(**context) -> Dict[str, Any]:
        """Verifica y genera alertas del sistema"""
        params = context["params"]
        config = PayrollConfig.from_env()
        
        # Determinar período
        period_start_str = params.get("period_start", "")
        period_end_str = params.get("period_end", "")
        
        if not period_start_str or not period_end_str:
            period_start, period_end = get_pay_period_dates(period_type="biweekly")
        else:
            period_start = datetime.strptime(period_start_str, "%Y-%m-%d").date()
            period_end = datetime.strptime(period_end_str, "%Y-%m-%d").date()
        
        alert_system = PayrollAlertSystem(postgres_conn_id=config.postgres_conn_id)
        
        # Obtener presupuesto si está configurado
        budget = None
        budget_str = os.getenv("PAYROLL_BUDGET")
        if budget_str:
            budget = Decimal(budget_str)
        
        # Ejecutar todas las verificaciones
        alerts = alert_system.run_all_checks(period_start, period_end, budget)
        
        # Obtener resumen
        summary = alert_system.get_alerts_summary(alerts)
        
        logger.info(
            f"Alerts check: {summary['total']} total, "
            f"{summary['by_severity']['critical']} critical, "
            f"{summary['by_severity']['warning']} warning"
        )
        
        # Notificar alertas críticas
        if summary['by_severity']['critical'] > 0:
            notifier = PayrollNotifier(
                slack_webhook_url=os.getenv("SLACK_WEBHOOK_URL")
            )
            
            critical_alerts = [a for a in alerts if a.severity == AlertSeverity.CRITICAL]
            for alert in critical_alerts:
                notifier._send_notification(
                    f"🚨 CRITICAL: {alert.message}",
                    "critical_alert",
                    {
                        "alert_type": alert.alert_type.value,
                        "employee_id": alert.employee_id,
                        "value": float(alert.value) if alert.value else None
                    }
                )
        
        return summary
    
    @task
    def generate_dashboard_data(**context) -> Dict[str, Any]:
        """Genera datos para dashboard"""
        params = context["params"]
        config = PayrollConfig.from_env()
        
        dashboard = PayrollDashboard(postgres_conn_id=config.postgres_conn_id)
        
        # Obtener datos del dashboard
        dashboard_data = dashboard.get_dashboard_data()
        
        # Obtener KPIs
        kpis = dashboard.get_kpi_summary()
        
        # Obtener series temporales
        time_series = dashboard.get_time_series_data(periods=12)
        
        logger.info(
            f"Dashboard data generated: {dashboard_data.total_employees} employees, "
            f"${dashboard_data.total_net_pay} total net pay"
        )
        
        return {
            "dashboard": dashboard.export_for_dashboard(dashboard_data),
            "kpis": kpis,
            "time_series": time_series
        }
    
    @task
    def refresh_materialized_views(**context) -> bool:
        """Refresca vistas materializadas para reportes"""
        params = context["params"]
        config = PayrollConfig.from_env()
        
        hook = PostgresHook(postgres_conn_id=config.postgres_conn_id)
        
        try:
            hook.run("SELECT refresh_payroll_materialized_views();")
            logger.info("Materialized views refreshed successfully")
            return True
        except Exception as e:
            logger.error(f"Error refreshing materialized views: {e}")
            return False
    
    # Pipeline
    schema_check = ensure_schema()
    receipts_processed = process_expense_receipts()
    payroll_calculated = calculate_payroll()
    
    # Análisis y reportes (paralelo)
    alerts_checked = check_alerts()
    anomalies_detected = detect_anomalies()
    metrics_collected = collect_metrics()
    reports_generated = generate_reports()
    dashboard_data = generate_dashboard_data()
    views_refreshed = refresh_materialized_views()
    
    schema_check >> receipts_processed >> payroll_calculated >> [
        alerts_checked,
        anomalies_detected,
        metrics_collected,
        reports_generated,
        dashboard_data,
        views_refreshed
    ]


# Instanciar DAG
payroll_processing_dag = payroll_processing()

