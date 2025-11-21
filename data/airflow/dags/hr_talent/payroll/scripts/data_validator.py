#!/usr/bin/env python3
"""
Script de Validación de Datos
Valida y reporta problemas en datos de nómina
"""

import argparse
import sys
import json
from datetime import date, datetime
from decimal import Decimal

from airflow.providers.postgres.hooks.postgres import PostgresHook

# Agregar path para imports
sys.path.insert(0, '/Users/adan/IA/data/airflow/dags')

from payroll import (
    PayrollStorage,
    PayrollValidator,
    AdvancedPayrollValidator,
    PayrollDataTransformer,
)


def validate_employees(conn_id: str, output_format: str = "text") -> int:
    """Valida todos los empleados"""
    storage = PayrollStorage(postgres_conn_id=conn_id)
    validator = AdvancedPayrollValidator()
    transformer = PayrollDataTransformer()
    
    # Obtener todos los empleados
    sql = """
        SELECT 
            employee_id, name, email, position,
            hourly_rate, salary_monthly, employee_type,
            tax_rate, benefits_rate, department,
            start_date, end_date, active
        FROM payroll_employees
        WHERE active = true
        ORDER BY employee_id
    """
    
    hook = storage.hook
    employees = hook.get_records(sql)
    
    issues = []
    validated = 0
    
    for emp in employees:
        employee = {
            "employee_id": emp[0],
            "name": emp[1],
            "email": emp[2],
            "position": emp[3],
            "hourly_rate": emp[4],
            "salary_monthly": emp[5],
            "employee_type": emp[6],
            "tax_rate": emp[7],
            "benefits_rate": emp[8],
            "department": emp[9],
            "start_date": emp[10],
            "end_date": emp[11],
            "active": emp[12]
        }
        
        # Transformar y normalizar
        normalized = transformer.transform_employee(employee)
        
        # Validar
        validation = validator.validate_employee_data(normalized)
        
        if not validation["valid"]:
            issues.append({
                "employee_id": employee["employee_id"],
                "errors": validation["errors"],
                "warnings": validation["warnings"]
            })
        else:
            validated += 1
    
    # Reportar
    if output_format == "json":
        print(json.dumps({
            "total": len(employees),
            "valid": validated,
            "issues": issues
        }, indent=2, default=str))
    else:
        print(f"\n=== Employee Validation ===")
        print(f"Total: {len(employees)}")
        print(f"Valid: {validated}")
        print(f"Issues: {len(issues)}")
        
        if issues:
            print("\nIssues found:")
            for issue in issues[:10]:  # Mostrar primeros 10
                print(f"  {issue['employee_id']}: {issue['errors']}")
    
    return 0 if len(issues) == 0 else 1


def validate_time_entries(conn_id: str, days: int = 30, output_format: str = "text") -> int:
    """Valida entradas de tiempo recientes"""
    storage = PayrollStorage(postgres_conn_id=conn_id)
    validator = PayrollValidator()
    transformer = PayrollDataTransformer()
    
    # Obtener entradas recientes
    from datetime import timedelta
    cutoff_date = date.today() - timedelta(days=days)
    
    sql = """
        SELECT 
            employee_id, work_date, clock_in, clock_out,
            hours_worked, hours_type, hourly_rate
        FROM payroll_time_entries
        WHERE work_date >= %s
        ORDER BY work_date DESC, employee_id
        LIMIT 1000
    """
    
    hook = storage.hook
    entries = hook.get_records(sql, parameters=(cutoff_date,))
    
    issues = []
    validated = 0
    
    for entry in entries:
        time_entry = {
            "employee_id": entry[0],
            "work_date": entry[1],
            "clock_in": entry[2],
            "clock_out": entry[3],
            "hours_worked": entry[4],
            "hours_type": entry[5],
            "hourly_rate": entry[6]
        }
        
        # Normalizar
        normalized = transformer.transform_time_entry(time_entry)
        
        # Validaciones básicas
        if normalized["hours_worked"] > Decimal("24.0"):
            issues.append({
                "employee_id": normalized["employee_id"],
                "date": str(normalized["work_date"]),
                "error": f"Hours exceed 24: {normalized['hours_worked']}"
            })
        elif normalized["hours_worked"] < Decimal("0.00"):
            issues.append({
                "employee_id": normalized["employee_id"],
                "date": str(normalized["work_date"]),
                "error": f"Negative hours: {normalized['hours_worked']}"
            })
        else:
            validated += 1
    
    # Reportar
    if output_format == "json":
        print(json.dumps({
            "total": len(entries),
            "valid": validated,
            "issues": issues
        }, indent=2, default=str))
    else:
        print(f"\n=== Time Entries Validation (last {days} days) ===")
        print(f"Total: {len(entries)}")
        print(f"Valid: {validated}")
        print(f"Issues: {len(issues)}")
        
        if issues:
            print("\nIssues found:")
            for issue in issues[:10]:
                print(f"  {issue['employee_id']} ({issue['date']}): {issue['error']}")
    
    return 0 if len(issues) == 0 else 1


def main():
    parser = argparse.ArgumentParser(description="Validate payroll data")
    parser.add_argument(
        "--conn-id",
        default="postgres_default",
        help="PostgreSQL connection ID"
    )
    parser.add_argument(
        "--type",
        choices=["employees", "time_entries", "all"],
        default="all",
        help="Type of data to validate"
    )
    parser.add_argument(
        "--days",
        type=int,
        default=30,
        help="Days to look back for time entries"
    )
    parser.add_argument(
        "--format",
        choices=["text", "json"],
        default="text",
        help="Output format"
    )
    
    args = parser.parse_args()
    
    exit_code = 0
    
    if args.type in ["employees", "all"]:
        exit_code |= validate_employees(args.conn_id, args.format)
    
    if args.type in ["time_entries", "all"]:
        exit_code |= validate_time_entries(args.conn_id, args.days, args.format)
    
    sys.exit(exit_code)


if __name__ == "__main__":
    main()


