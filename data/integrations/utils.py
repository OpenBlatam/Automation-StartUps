"""
Utilidades para el framework de sincronización
==============================================

Funciones auxiliares para gestión, monitoreo y troubleshooting.
"""
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
import json
import logging

logger = logging.getLogger(__name__)


def get_sync_stats(
    db_connection_string: str,
    days: int = 7,
    source_type: Optional[str] = None,
    target_type: Optional[str] = None
) -> Dict[str, Any]:
    """
    Obtiene estadísticas de sincronizaciones recientes.
    
    Args:
        db_connection_string: String de conexión a PostgreSQL
        days: Días hacia atrás para analizar
        source_type: Filtrar por tipo de fuente (opcional)
        target_type: Filtrar por tipo de destino (opcional)
    
    Returns:
        Diccionario con estadísticas
    """
    try:
        import psycopg2
        from psycopg2.extras import RealDictCursor
        
        conn = psycopg2.connect(db_connection_string)
        cur = conn.cursor(cursor_factory=RealDictCursor)
        
        where_clauses = ["started_at >= NOW() - INTERVAL '%s days'" % days]
        params = []
        
        if source_type:
            where_clauses.append("source_type = %s")
            params.append(source_type)
        
        if target_type:
            where_clauses.append("target_type = %s")
            params.append(target_type)
        
        where_sql = " AND ".join(where_clauses)
        
        # Estadísticas generales
        cur.execute(f"""
            SELECT 
                COUNT(*) as total_syncs,
                COUNT(CASE WHEN status = 'completed' THEN 1 END) as successful,
                COUNT(CASE WHEN status = 'failed' THEN 1 END) as failed,
                COUNT(CASE WHEN status = 'partial' THEN 1 END) as partial,
                SUM(total_records) as total_records,
                SUM(successful) as total_successful,
                SUM(failed) as total_failed,
                AVG(duration_seconds) as avg_duration,
                MAX(duration_seconds) as max_duration
            FROM sync_history
            WHERE {where_sql}
        """, params)
        
        stats = dict(cur.fetchone())
        
        # Top errores
        cur.execute(f"""
            SELECT 
                error_message,
                COUNT(*) as count
            FROM sync_records
            WHERE status = 'failed'
                AND synced_at >= NOW() - INTERVAL '%s days'
            GROUP BY error_message
            ORDER BY count DESC
            LIMIT 10
        """, (days,))
        
        top_errors = [dict(row) for row in cur.fetchall()]
        stats['top_errors'] = top_errors
        
        # Sincronizaciones por tipo
        cur.execute(f"""
            SELECT 
                source_type,
                target_type,
                COUNT(*) as sync_count,
                AVG(duration_seconds) as avg_duration,
                AVG(successful::float / NULLIF(total_records, 0)) * 100 as success_rate
            FROM sync_history
            WHERE {where_sql}
            GROUP BY source_type, target_type
            ORDER BY sync_count DESC
        """, params)
        
        by_type = [dict(row) for row in cur.fetchall()]
        stats['by_type'] = by_type
        
        cur.close()
        conn.close()
        
        return stats
    except Exception as e:
        logger.error(f"Error obteniendo estadísticas: {e}")
        return {"error": str(e)}


def get_pending_conflicts(
    db_connection_string: str,
    limit: int = 100
) -> List[Dict[str, Any]]:
    """
    Obtiene conflictos pendientes de resolución.
    
    Args:
        db_connection_string: String de conexión a PostgreSQL
        limit: Límite de resultados
    
    Returns:
        Lista de conflictos pendientes
    """
    try:
        import psycopg2
        from psycopg2.extras import RealDictCursor
        
        conn = psycopg2.connect(db_connection_string)
        cur = conn.cursor(cursor_factory=RealDictCursor)
        
        cur.execute("""
            SELECT 
                sc.id,
                sc.conflict_type,
                sc.conflict_fields,
                sc.source_data,
                sc.target_data,
                sc.created_at,
                sr.source_id,
                sr.source_type,
                sr.target_id,
                sr.target_type
            FROM sync_conflicts sc
            JOIN sync_records sr ON sc.sync_record_id = sr.id
            WHERE sc.resolved_at IS NULL
            ORDER BY sc.created_at DESC
            LIMIT %s
        """, (limit,))
        
        conflicts = [dict(row) for row in cur.fetchall()]
        
        cur.close()
        conn.close()
        
        return conflicts
    except Exception as e:
        logger.error(f"Error obteniendo conflictos: {e}")
        return []


def resolve_conflict(
    db_connection_string: str,
    conflict_id: int,
    resolution_data: Dict[str, Any],
    resolved_by: str = "system"
) -> bool:
    """
    Resuelve un conflicto manualmente.
    
    Args:
        db_connection_string: String de conexión a PostgreSQL
        conflict_id: ID del conflicto
        resolution_data: Datos de resolución
        resolved_by: Usuario que resuelve
    
    Returns:
        True si se resolvió exitosamente
    """
    try:
        import psycopg2
        from psycopg2.extras import Json
        
        conn = psycopg2.connect(db_connection_string)
        cur = conn.cursor()
        
        cur.execute("""
            UPDATE sync_conflicts
            SET resolved_by = %s,
                resolved_at = NOW(),
                resolution_data = %s
            WHERE id = %s
                AND resolved_at IS NULL
        """, (resolved_by, Json(resolution_data), conflict_id))
        
        conn.commit()
        updated = cur.rowcount > 0
        
        cur.close()
        conn.close()
        
        return updated
    except Exception as e:
        logger.error(f"Error resolviendo conflicto: {e}")
        return False


def cleanup_old_sync_history(
    db_connection_string: str,
    days: int = 90,
    dry_run: bool = True
) -> Dict[str, Any]:
    """
    Limpia historial de sincronizaciones antiguo.
    
    Args:
        db_connection_string: String de conexión a PostgreSQL
        days: Mantener registros de los últimos N días
        dry_run: Si True, solo muestra qué se eliminaría
    
    Returns:
        Diccionario con resultados
    """
    try:
        import psycopg2
        
        conn = psycopg2.connect(db_connection_string)
        cur = conn.cursor()
        
        # Contar registros a eliminar
        cur.execute("""
            SELECT COUNT(*) 
            FROM sync_history
            WHERE started_at < NOW() - INTERVAL '%s days'
        """, (days,))
        
        count = cur.fetchone()[0]
        
        result = {
            "records_to_delete": count,
            "dry_run": dry_run
        }
        
        if not dry_run:
            # Eliminar registros antiguos (cascade eliminará sync_records relacionados)
            cur.execute("""
                DELETE FROM sync_history
                WHERE started_at < NOW() - INTERVAL '%s days'
            """, (days,))
            
            deleted = cur.rowcount
            conn.commit()
            
            result["deleted"] = deleted
        else:
            result["deleted"] = 0
        
        cur.close()
        conn.close()
        
        return result
    except Exception as e:
        logger.error(f"Error limpiando historial: {e}")
        return {"error": str(e)}


def export_sync_report(
    db_connection_string: str,
    sync_id: Optional[str] = None,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    output_format: str = "json"
) -> str:
    """
    Exporta reporte de sincronización.
    
    Args:
        db_connection_string: String de conexión a PostgreSQL
        sync_id: ID de sincronización específica (opcional)
        start_date: Fecha de inicio (opcional)
        end_date: Fecha de fin (opcional)
        output_format: Formato de salida (json, csv)
    
    Returns:
        Reporte en formato solicitado
    """
    try:
        import psycopg2
        from psycopg2.extras import RealDictCursor
        
        conn = psycopg2.connect(db_connection_string)
        cur = conn.cursor(cursor_factory=RealDictCursor)
        
        where_clauses = []
        params = []
        
        if sync_id:
            where_clauses.append("sync_id = %s")
            params.append(sync_id)
        
        if start_date:
            where_clauses.append("started_at >= %s")
            params.append(start_date)
        
        if end_date:
            where_clauses.append("started_at <= %s")
            params.append(end_date)
        
        where_sql = " AND ".join(where_clauses) if where_clauses else "1=1"
        
        cur.execute(f"""
            SELECT 
                sync_id,
                status,
                source_type,
                target_type,
                total_records,
                successful,
                failed,
                conflicted,
                skipped,
                duration_seconds,
                started_at,
                completed_at
            FROM sync_history
            WHERE {where_sql}
            ORDER BY started_at DESC
        """, params)
        
        rows = [dict(row) for row in cur.fetchall()]
        
        cur.close()
        conn.close()
        
        if output_format == "json":
            return json.dumps(rows, indent=2, default=str)
        elif output_format == "csv":
            if not rows:
                return ""
            
            import csv
            from io import StringIO
            
            output = StringIO()
            writer = csv.DictWriter(output, fieldnames=rows[0].keys())
            writer.writeheader()
            writer.writerows(rows)
            
            return output.getvalue()
        else:
            raise ValueError(f"Formato no soportado: {output_format}")
    
    except Exception as e:
        logger.error(f"Error exportando reporte: {e}")
        return json.dumps({"error": str(e)})


def validate_sync_config(config: Dict[str, Any]) -> tuple[bool, Optional[str]]:
    """
    Valida configuración de sincronización.
    
    Args:
        config: Configuración a validar
    
    Returns:
        (is_valid, error_message)
    """
    required_fields = [
        "source_connector_type",
        "source_config",
        "target_connector_type",
        "target_config"
    ]
    
    for field in required_fields:
        if field not in config:
            return False, f"Campo requerido faltante: {field}"
    
    # Validar tipos de conectores
    valid_connectors = [
        "hubspot", "quickbooks", "google_sheets",
        "database", "postgresql", "mysql", "salesforce"
    ]
    
    source_type = config.get("source_connector_type")
    target_type = config.get("target_connector_type")
    
    if source_type not in valid_connectors:
        return False, f"Tipo de conector fuente inválido: {source_type}"
    
    if target_type not in valid_connectors:
        return False, f"Tipo de conector destino inválido: {target_type}"
    
    # Validar credenciales básicas
    source_config = config.get("source_config", {})
    target_config = config.get("target_config", {})
    
    if source_type == "hubspot" and not source_config.get("api_token"):
        return False, "HubSpot requiere api_token"
    
    if source_type == "quickbooks":
        if not source_config.get("access_token") or not source_config.get("realm_id"):
            return False, "QuickBooks requiere access_token y realm_id"
    
    if source_type == "google_sheets":
        if not source_config.get("credentials_json") and not source_config.get("credentials_path"):
            return False, "Google Sheets requiere credentials_json o credentials_path"
        if not source_config.get("spreadsheet_id"):
            return False, "Google Sheets requiere spreadsheet_id"
    
    # Mismas validaciones para target
    if target_type == "hubspot" and not target_config.get("api_token"):
        return False, "HubSpot (target) requiere api_token"
    
    if target_type == "quickbooks":
        if not target_config.get("access_token") or not target_config.get("realm_id"):
            return False, "QuickBooks (target) requiere access_token y realm_id"
    
    if target_type == "google_sheets":
        if not target_config.get("credentials_json") and not target_config.get("credentials_path"):
            return False, "Google Sheets (target) requiere credentials_json o credentials_path"
        if not target_config.get("spreadsheet_id"):
            return False, "Google Sheets (target) requiere spreadsheet_id"
    
    return True, None


