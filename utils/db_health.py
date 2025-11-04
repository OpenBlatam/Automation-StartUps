#!/usr/bin/env python3
"""
Database Health Check Utility
Provides comprehensive database health checks including connectivity, tables, indexes, and performance metrics.
"""

import os
import sys
import time
import json
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, asdict
from contextlib import contextmanager

try:
    import psycopg
    from psycopg.rows import dict_row
except ImportError:
    try:
        import psycopg2 as psycopg
        from psycopg2.extras import RealDictCursor
    except ImportError:
        print("ERROR: psycopg or psycopg2 not installed. Install with: pip install psycopg[binary]")
        sys.exit(1)


@dataclass
class HealthCheckResult:
    """Result of a health check"""
    name: str
    status: str  # 'ok', 'warning', 'error'
    message: str
    metrics: Optional[Dict[str, Any]] = None
    latency_ms: Optional[float] = None


@dataclass
class DatabaseHealthReport:
    """Complete database health report"""
    overall_status: str
    timestamp: str
    connection_latency_ms: float
    checks: List[HealthCheckResult]
    summary: Dict[str, Any]


class DatabaseHealthChecker:
    """Database health checker utility"""
    
    def __init__(self, dsn: Optional[str] = None):
        """
        Initialize health checker
        
        Args:
            dsn: PostgreSQL connection string. If not provided, reads from env vars.
        """
        if dsn:
            self.dsn = dsn
        else:
            self.dsn = os.environ.get(
                "KPIS_PG_DSN",
                f"postgresql://{os.environ.get('KPIS_PG_USER', 'analytics')}"
                f":{os.environ.get('KPIS_PG_PASSWORD', '')}"
                f"@{os.environ.get('KPIS_PG_HOST', 'localhost')}"
                f":{os.environ.get('KPIS_PG_PORT', '5432')}"
                f"/{os.environ.get('KPIS_PG_DB', 'analytics')}"
            )
        self.conn = None
    
    @contextmanager
    def get_connection(self):
        """Get database connection with context manager"""
        try:
            if hasattr(psycopg, 'connect'):
                conn = psycopg.connect(self.dsn)
            else:
                import psycopg2
                conn = psycopg2.connect(self.dsn)
            
            # Set row factory for dict-like results
            if hasattr(conn, 'cursor'):
                if hasattr(psycopg.rows, 'dict_row'):
                    self.conn = conn
                else:
                    conn.cursor_factory = RealDictCursor
            yield conn
        except Exception as e:
            raise Exception(f"Connection failed: {e}")
        finally:
            if conn:
                conn.close()
    
    def check_connectivity(self) -> HealthCheckResult:
        """Check basic database connectivity"""
        start = time.time()
        try:
            with self.get_connection() as conn:
                with conn.cursor() as cur:
                    cur.execute("SELECT 1")
                    cur.fetchone()
                latency = (time.time() - start) * 1000
                return HealthCheckResult(
                    name="connectivity",
                    status="ok",
                    message="Connected successfully",
                    latency_ms=latency
                )
        except Exception as e:
            latency = (time.time() - start) * 1000
            return HealthCheckResult(
                name="connectivity",
                status="error",
                message=f"Connection failed: {str(e)}",
                latency_ms=latency
            )
    
    def check_tables(self) -> HealthCheckResult:
        """Check if required tables exist"""
        required_tables = ['payments', 'leads']
        missing = []
        existing = []
        
        try:
            with self.get_connection() as conn:
                with conn.cursor() as cur:
                    for table in required_tables:
                        cur.execute(
                            """
                            SELECT EXISTS (
                                SELECT FROM information_schema.tables 
                                WHERE table_schema = 'public' AND table_name = %s
                            )
                            """,
                            (table,)
                        )
                        exists = cur.fetchone()[0]
                        if exists:
                            existing.append(table)
                        else:
                            missing.append(table)
            
            if missing:
                return HealthCheckResult(
                    name="tables",
                    status="error",
                    message=f"Missing tables: {', '.join(missing)}",
                    metrics={"existing": existing, "missing": missing}
                )
            else:
                return HealthCheckResult(
                    name="tables",
                    status="ok",
                    message=f"All required tables exist ({', '.join(existing)})",
                    metrics={"existing": existing, "missing": []}
                )
        except Exception as e:
            return HealthCheckResult(
                name="tables",
                status="error",
                message=f"Error checking tables: {str(e)}"
            )
    
    def check_indexes(self) -> HealthCheckResult:
        """Check index health"""
        try:
            with self.get_connection() as conn:
                with conn.cursor() as cur:
                    cur.execute("""
                        SELECT 
                            schemaname,
                            tablename,
                            indexname,
                            idx_scan as index_scans,
                            idx_tup_read as tuples_read,
                            idx_tup_fetch as tuples_fetched
                        FROM pg_stat_user_indexes
                        WHERE schemaname = 'public'
                        ORDER BY idx_scan DESC
                        LIMIT 20
                    """)
                    indexes = cur.fetchall()
                    
                    # Check for unused indexes
                    cur.execute("""
                        SELECT COUNT(*) 
                        FROM pg_stat_user_indexes
                        WHERE schemaname = 'public' AND idx_scan = 0
                    """)
                    unused_count = cur.fetchone()[0]
            
            metrics = {
                "total_checked": len(indexes),
                "unused_indexes": unused_count
            }
            
            status = "ok"
            message = f"Found {len(indexes)} indexes, {unused_count} unused"
            if unused_count > 10:
                status = "warning"
                message += " (consider removing unused indexes)"
            
            return HealthCheckResult(
                name="indexes",
                status=status,
                message=message,
                metrics=metrics
            )
        except Exception as e:
            return HealthCheckResult(
                name="indexes",
                status="error",
                message=f"Error checking indexes: {str(e)}"
            )
    
    def check_materialized_views(self) -> HealthCheckResult:
        """Check materialized views"""
        try:
            with self.get_connection() as conn:
                with conn.cursor() as cur:
                    cur.execute("""
                        SELECT 
                            matviewname,
                            hasindexes,
                            ispopulated
                        FROM pg_matviews
                        WHERE schemaname = 'public'
                        ORDER BY matviewname
                    """)
                    mvs = cur.fetchall()
                    
                    not_populated = [mv[0] for mv in mvs if not mv[2]]
            
            if not_populated:
                return HealthCheckResult(
                    name="materialized_views",
                    status="warning",
                    message=f"Some views not populated: {', '.join(not_populated)}",
                    metrics={"total": len(mvs), "not_populated": not_populated}
                )
            else:
                return HealthCheckResult(
                    name="materialized_views",
                    status="ok",
                    message=f"All {len(mvs)} materialized views are populated",
                    metrics={"total": len(mvs), "not_populated": []}
                )
        except Exception as e:
            return HealthCheckResult(
                name="materialized_views",
                status="error",
                message=f"Error checking materialized views: {str(e)}"
            )
    
    def check_connection_pool(self) -> HealthCheckResult:
        """Check connection pool stats"""
        try:
            with self.get_connection() as conn:
                with conn.cursor() as cur:
                    cur.execute("""
                        SELECT 
                            count(*) as total_connections,
                            count(*) FILTER (WHERE state = 'active') as active,
                            count(*) FILTER (WHERE state = 'idle') as idle
                        FROM pg_stat_activity
                        WHERE datname = current_database()
                    """)
                    row = cur.fetchone()
                    
                    total = row[0] if row else 0
                    active = row[1] if row else 0
                    idle = row[2] if row else 0
            
            metrics = {
                "total": total,
                "active": active,
                "idle": idle
            }
            
            status = "ok"
            message = f"{total} connections ({active} active, {idle} idle)"
            if total > 100:
                status = "warning"
                message += " (high connection count)"
            
            return HealthCheckResult(
                name="connection_pool",
                status=status,
                message=message,
                metrics=metrics
            )
        except Exception as e:
            return HealthCheckResult(
                name="connection_pool",
                status="error",
                message=f"Error checking connection pool: {str(e)}"
            )
    
    def check_recent_activity(self) -> HealthCheckResult:
        """Check recent data activity"""
        try:
            with self.get_connection() as conn:
                with conn.cursor() as cur:
                    # Check payments in last 24h
                    cur.execute("""
                        SELECT COUNT(*) as count
                        FROM payments
                        WHERE created_at >= NOW() - INTERVAL '24 hours'
                    """)
                    payments_24h = cur.fetchone()[0]
                    
                    # Check leads in last 24h
                    cur.execute("""
                        SELECT COUNT(*) as count
                        FROM leads
                        WHERE created_at >= NOW() - INTERVAL '24 hours'
                    """)
                    leads_24h = cur.fetchone()[0]
            
            metrics = {
                "payments_24h": payments_24h,
                "leads_24h": leads_24h
            }
            
            status = "ok"
            message = f"{payments_24h} payments, {leads_24h} leads (24h)"
            if payments_24h == 0 and leads_24h == 0:
                status = "warning"
                message += " (no recent activity)"
            
            return HealthCheckResult(
                name="recent_activity",
                status=status,
                message=message,
                metrics=metrics
            )
        except Exception as e:
            return HealthCheckResult(
                name="recent_activity",
                status="error",
                message=f"Error checking activity: {str(e)}"
            )
    
    def run_all_checks(self) -> DatabaseHealthReport:
        """Run all health checks"""
        checks = []
        
        # Run checks
        checks.append(self.check_connectivity())
        if checks[-1].status == "ok":
            checks.append(self.check_tables())
            checks.append(self.check_indexes())
            checks.append(self.check_materialized_views())
            checks.append(self.check_connection_pool())
            checks.append(self.check_recent_activity())
        
        # Determine overall status
        error_count = sum(1 for c in checks if c.status == "error")
        warning_count = sum(1 for c in checks if c.status == "warning")
        
        if error_count > 0:
            overall_status = "error"
        elif warning_count > 0:
            overall_status = "warning"
        else:
            overall_status = "ok"
        
        # Calculate summary
        connectivity_check = next((c for c in checks if c.name == "connectivity"), None)
        latency = connectivity_check.latency_ms if connectivity_check else None
        
        summary = {
            "total_checks": len(checks),
            "ok": sum(1 for c in checks if c.status == "ok"),
            "warnings": warning_count,
            "errors": error_count
        }
        
        return DatabaseHealthReport(
            overall_status=overall_status,
            timestamp=time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            connection_latency_ms=latency or 0.0,
            checks=checks,
            summary=summary
        )


def main():
    """CLI entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Database Health Check Utility")
    parser.add_argument("--dsn", help="PostgreSQL connection string")
    parser.add_argument("--json", action="store_true", help="Output JSON format")
    parser.add_argument("--check", help="Run specific check only", 
                       choices=["connectivity", "tables", "indexes", "mvs", "pool", "activity"])
    
    args = parser.parse_args()
    
    checker = DatabaseHealthChecker(dsn=args.dsn)
    
    if args.check:
        # Run single check
        check_map = {
            "connectivity": checker.check_connectivity,
            "tables": checker.check_tables,
            "indexes": checker.check_indexes,
            "mvs": checker.check_materialized_views,
            "pool": checker.check_connection_pool,
            "activity": checker.check_recent_activity
        }
        
        result = check_map[args.check]()
        if args.json:
            print(json.dumps(asdict(result), indent=2))
        else:
            print(f"[{result.status.upper()}] {result.name}: {result.message}")
            if result.metrics:
                print(f"  Metrics: {json.dumps(result.metrics, indent=2)}")
    else:
        # Run all checks
        report = checker.run_all_checks()
        
        if args.json:
            print(json.dumps(asdict(report), indent=2, default=str))
        else:
            print("=" * 60)
            print(f"Database Health Check Report")
            print(f"Timestamp: {report.timestamp}")
            print(f"Overall Status: {report.overall_status.upper()}")
            print(f"Connection Latency: {report.connection_latency_ms:.2f}ms")
            print("=" * 60)
            print()
            
            for check in report.checks:
                status_icon = "✓" if check.status == "ok" else "⚠" if check.status == "warning" else "✗"
                print(f"{status_icon} [{check.status.upper()}] {check.name}")
                print(f"   {check.message}")
                if check.latency_ms:
                    print(f"   Latency: {check.latency_ms:.2f}ms")
                if check.metrics:
                    print(f"   Metrics: {json.dumps(check.metrics)}")
                print()
            
            print("=" * 60)
            print(f"Summary: {report.summary['ok']} OK, {report.summary['warnings']} warnings, {report.summary['errors']} errors")
            print("=" * 60)
    
    # Exit with appropriate code
    if args.check:
        sys.exit(0 if result.status != "error" else 1)
    else:
        sys.exit(0 if report.overall_status != "error" else 1)


if __name__ == "__main__":
    main()
