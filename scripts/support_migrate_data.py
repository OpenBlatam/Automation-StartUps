#!/usr/bin/env python3
"""
Script de Migración de Datos de Tickets de Soporte

Útil para:
- Migrar datos entre bases de datos
- Backup de datos
- Consolidación de datos históricos
- Limpieza de datos antiguos
"""
import os
import sys
import psycopg2
import argparse
from datetime import datetime, timedelta
from typing import Dict, Any, List

# Configuración
SOURCE_DB = {
    "host": os.getenv("SOURCE_DB_HOST", "localhost"),
    "database": os.getenv("SOURCE_DB_NAME", "support_db"),
    "user": os.getenv("SOURCE_DB_USER", "postgres"),
    "password": os.getenv("SOURCE_DB_PASSWORD", ""),
    "port": os.getenv("SOURCE_DB_PORT", "5432")
}

TARGET_DB = {
    "host": os.getenv("TARGET_DB_HOST", "localhost"),
    "database": os.getenv("TARGET_DB_NAME", "support_db_backup"),
    "user": os.getenv("TARGET_DB_USER", "postgres"),
    "password": os.getenv("TARGET_DB_PASSWORD", ""),
    "port": os.getenv("TARGET_DB_PORT", "5432")
}


def migrate_tickets(
    source_conn,
    target_conn,
    date_from: Optional[datetime] = None,
    date_to: Optional[datetime] = None,
    batch_size: int = 1000
) -> int:
    """Migra tickets entre bases de datos."""
    source_cur = source_conn.cursor()
    target_cur = target_conn.cursor()
    
    # Construir query con filtros de fecha
    query = """
        SELECT 
            ticket_id, source, subject, description,
            customer_email, customer_name, customer_id,
            category, tags, priority, priority_score,
            urgency_factors, assigned_department,
            assigned_agent_id, assigned_agent_name,
            routing_reason, status, chatbot_attempted,
            chatbot_resolved, chatbot_response,
            faq_matched, faq_article_id, metadata,
            created_at, updated_at, first_response_at,
            resolved_at, closed_at
        FROM support_tickets
    """
    
    params = []
    conditions = []
    
    if date_from:
        conditions.append("created_at >= %s")
        params.append(date_from)
    
    if date_to:
        conditions.append("created_at <= %s")
        params.append(date_to)
    
    if conditions:
        query += " WHERE " + " AND ".join(conditions)
    
    query += " ORDER BY created_at"
    
    source_cur.execute(query, params)
    
    migrated = 0
    batch = []
    
    for row in source_cur:
        batch.append(row)
        
        if len(batch) >= batch_size:
            # Insertar batch
            insert_query = """
                INSERT INTO support_tickets (
                    ticket_id, source, subject, description,
                    customer_email, customer_name, customer_id,
                    category, tags, priority, priority_score,
                    urgency_factors, assigned_department,
                    assigned_agent_id, assigned_agent_name,
                    routing_reason, status, chatbot_attempted,
                    chatbot_resolved, chatbot_response,
                    faq_matched, faq_article_id, metadata,
                    created_at, updated_at, first_response_at,
                    resolved_at, closed_at
                ) VALUES %s
                ON CONFLICT (ticket_id) DO NOTHING
            """
            
            # Usar execute_values para inserción eficiente
            from psycopg2.extras import execute_values
            execute_values(target_cur, insert_query, batch)
            target_conn.commit()
            
            migrated += len(batch)
            print(f"Migrated {migrated} tickets...")
            batch = []
    
    # Insertar batch final
    if batch:
        from psycopg2.extras import execute_values
        insert_query = """
            INSERT INTO support_tickets (...) VALUES %s
            ON CONFLICT (ticket_id) DO NOTHING
        """
        execute_values(target_cur, insert_query, batch)
        target_conn.commit()
        migrated += len(batch)
    
    source_cur.close()
    target_cur.close()
    
    return migrated


def backup_tables(
    source_conn,
    backup_path: str,
    tables: List[str]
) -> None:
    """Hace backup de tablas a archivos SQL."""
    source_cur = source_conn.cursor()
    
    os.makedirs(backup_path, exist_ok=True)
    
    for table in tables:
        print(f"Backing up table: {table}")
        
        # Exportar a CSV
        csv_path = f"{backup_path}/{table}_{datetime.now().strftime('%Y%m%d')}.csv"
        
        source_cur.execute(f"SELECT * FROM {table}")
        rows = source_cur.fetchall()
        columns = [desc[0] for desc in source_cur.description]
        
        import csv
        with open(csv_path, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(columns)
            writer.writerows(rows)
        
        print(f"  Exported {len(rows)} rows to {csv_path}")


def cleanup_old_data(
    conn,
    table: str,
    date_field: str,
    retention_days: int
) -> int:
    """Limpia datos antiguos."""
    cutoff_date = datetime.now() - timedelta(days=retention_days)
    
    cur = conn.cursor()
    
    query = f"""
        DELETE FROM {table}
        WHERE {date_field} < %s
    """
    
    cur.execute(query, (cutoff_date,))
    deleted = cur.rowcount
    
    conn.commit()
    cur.close()
    
    return deleted


def main():
    """Función principal."""
    parser = argparse.ArgumentParser(description="Migración de datos de soporte")
    parser.add_argument("--action", choices=["migrate", "backup", "cleanup"], required=True)
    parser.add_argument("--from-date", help="Fecha desde (YYYY-MM-DD)")
    parser.add_argument("--to-date", help="Fecha hasta (YYYY-MM-DD)")
    parser.add_argument("--tables", help="Tablas para backup (comma-separated)")
    parser.add_argument("--retention-days", type=int, help="Días de retención para cleanup")
    parser.add_argument("--batch-size", type=int, default=1000)
    
    args = parser.parse_args()
    
    try:
        source_conn = psycopg2.connect(**SOURCE_DB)
        print(f"✅ Conectado a BD origen: {SOURCE_DB['host']}/{SOURCE_DB['database']}")
        
        if args.action == "migrate":
            target_conn = psycopg2.connect(**TARGET_DB)
            print(f"✅ Conectado a BD destino: {TARGET_DB['host']}/{TARGET_DB['database']}")
            
            date_from = datetime.strptime(args.from_date, "%Y-%m-%d") if args.from_date else None
            date_to = datetime.strptime(args.to_date, "%Y-%m-%d") if args.to_date else None
            
            migrated = migrate_tickets(
                source_conn,
                target_conn,
                date_from,
                date_to,
                args.batch_size
            )
            
            print(f"\n✅ Migración completada: {migrated} tickets migrados")
            target_conn.close()
        
        elif args.action == "backup":
            backup_path = os.getenv("BACKUP_PATH", "/tmp/support_backup")
            tables = args.tables.split(",") if args.tables else [
                "support_tickets",
                "support_chatbot_interactions",
                "support_faq_articles",
                "support_ticket_history",
                "support_ticket_feedback"
            ]
            
            backup_tables(source_conn, backup_path, tables)
            print(f"\n✅ Backup completado en: {backup_path}")
        
        elif args.action == "cleanup":
            if not args.retention_days:
                print("❌ --retention-days es requerido para cleanup")
                sys.exit(1)
            
            deleted = cleanup_old_data(
                source_conn,
                "support_tickets",
                "created_at",
                args.retention_days
            )
            print(f"\n✅ Limpieza completada: {deleted} registros eliminados")
        
        source_conn.close()
        
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()

