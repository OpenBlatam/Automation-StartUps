"""
Script Helper de Recovery para Nómina
Script CLI para operaciones de recuperación
"""

import argparse
import sys
from datetime import date, datetime
from decimal import Decimal

# Agregar path al módulo payroll
sys.path.insert(0, '/Users/adan/IA/data/airflow/dags')

from payroll import PayrollRecovery, PayrollStorage
from payroll.config import PayrollConfig


def rollback_pay_period(args):
    """Rollback de un período de pago"""
    recovery = PayrollRecovery(postgres_conn_id=args.conn_id)
    
    success = recovery.rollback_pay_period(args.pay_period_id)
    
    if success:
        print(f"✅ Pay period {args.pay_period_id} rolled back successfully")
        return 0
    else:
        print(f"❌ Failed to rollback pay period {args.pay_period_id}")
        return 1


def show_failed_operations(args):
    """Muestra operaciones fallidas"""
    recovery = PayrollRecovery(postgres_conn_id=args.conn_id)
    
    failed = recovery.get_failed_operations(hours=args.hours)
    
    if not failed:
        print("✅ No failed operations found")
        return 0
    
    print(f"\n⚠️  Found {len(failed)} failed operations:\n")
    
    for op in failed:
        print(f"  Type: {op['operation_type']}")
        print(f"  ID: {op['id']}")
        print(f"  Employee: {op['employee_id']}")
        print(f"  Status: {op['status']}")
        print(f"  Created: {op['created_at']}")
        print()
    
    return 0


def recovery_summary(args):
    """Muestra resumen de recuperación"""
    recovery = PayrollRecovery(postgres_conn_id=args.conn_id)
    
    summary = recovery.create_recovery_summary()
    
    print("\n📊 Recovery Summary\n")
    print(f"Total Failed Operations: {summary['total_failed']}")
    print(f"Needs Attention: {'Yes' if summary['needs_attention'] else 'No'}")
    
    if summary['by_type']:
        print("\nBy Type:")
        for op_type, count in summary['by_type'].items():
            print(f"  {op_type}: {count}")
    
    return 0


def main():
    """Main CLI entry point"""
    parser = argparse.ArgumentParser(
        description="Payroll Recovery Helper",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Rollback a pay period
  python recovery_helper.py rollback --pay-period-id 123

  # Show failed operations
  python recovery_helper.py failed --hours 24

  # Show recovery summary
  python recovery_helper.py summary
        """
    )
    
    parser.add_argument(
        "--conn-id",
        default="postgres_default",
        help="PostgreSQL connection ID"
    )
    
    subparsers = parser.add_subparsers(dest="command", help="Command to execute")
    
    # Rollback command
    rollback_parser = subparsers.add_parser("rollback", help="Rollback pay period")
    rollback_parser.add_argument(
        "--pay-period-id",
        type=int,
        required=True,
        help="Pay period ID to rollback"
    )
    rollback_parser.set_defaults(func=rollback_pay_period)
    
    # Failed operations command
    failed_parser = subparsers.add_parser("failed", help="Show failed operations")
    failed_parser.add_argument(
        "--hours",
        type=int,
        default=24,
        help="Hours to look back (default: 24)"
    )
    failed_parser.set_defaults(func=show_failed_operations)
    
    # Summary command
    summary_parser = subparsers.add_parser("summary", help="Show recovery summary")
    summary_parser.set_defaults(func=recovery_summary)
    
    args = parser.parse_args()
    
    if not hasattr(args, 'func'):
        parser.print_help()
        return 1
    
    try:
        return args.func(args)
    except Exception as e:
        print(f"❌ Error: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())

