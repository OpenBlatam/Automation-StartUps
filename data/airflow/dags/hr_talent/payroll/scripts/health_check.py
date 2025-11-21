#!/usr/bin/env python3
"""
Script para verificar la salud del sistema de nómina
"""

import sys
import json
import argparse
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from payroll.health_checks import PayrollHealthChecker


def main():
    """Función principal"""
    parser = argparse.ArgumentParser(description="Check payroll system health")
    parser.add_argument(
        "--conn-id",
        default="postgres_default",
        help="PostgreSQL connection ID"
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Output as JSON"
    )
    
    args = parser.parse_args()
    
    health_checker = PayrollHealthChecker(postgres_conn_id=args.conn_id)
    health_status = health_checker.comprehensive_health_check()
    
    if args.json:
        print(json.dumps(health_status, indent=2, default=str))
    else:
        print(f"Overall Status: {health_status['overall_status'].upper()}")
        print(f"Timestamp: {health_status['timestamp']}")
        print("\nChecks:")
        for name, check in health_status['checks'].items():
            status_icon = {
                "healthy": "✅",
                "warning": "⚠️",
                "critical": "❌",
                "unknown": "❓"
            }.get(check['status'], "❓")
            
            print(f"  {status_icon} {name}: {check['message']}")
        
        print("\nSummary:")
        summary = health_status['summary']
        print(f"  Healthy: {summary['healthy']}")
        print(f"  Warnings: {summary['warnings']}")
        print(f"  Critical: {summary['critical']}")
        print(f"  Unknown: {summary['unknown']}")
    
    # Exit code basado en estado
    if health_status['overall_status'] == 'critical':
        sys.exit(2)
    elif health_status['overall_status'] == 'warning':
        sys.exit(1)
    else:
        sys.exit(0)


if __name__ == "__main__":
    main()

