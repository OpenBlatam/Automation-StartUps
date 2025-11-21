#!/usr/bin/env python3
"""
Utilidades para el Sistema de Troubleshooting
Scripts de mantenimiento y utilidades comunes
"""

import sys
import argparse
import json
from pathlib import Path
from datetime import datetime, timedelta
import psycopg2
from psycopg2.extras import RealDictCursor

# Agregar path para imports
sys.path.insert(0, str(Path(__file__).parent.parent / "data" / "integrations"))

from support_troubleshooting_agent import TroubleshootingAgent


def health_check(db_url: str):
    """Verifica el estado del sistema"""
    print("🔍 Verificando salud del sistema...")
    
    try:
        conn = psycopg2.connect(db_url)
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        
        # Verificar tablas
        cursor.execute("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public' 
            AND table_name LIKE 'support_troubleshooting%'
            ORDER BY table_name
        """)
        tables = cursor.fetchall()
        print(f"✅ Tablas encontradas: {len(tables)}")
        for table in tables:
            print(f"   - {table['table_name']}")
        
        # Verificar sesiones activas
        cursor.execute("""
            SELECT COUNT(*) as count 
            FROM support_troubleshooting_sessions 
            WHERE status IN ('started', 'in_progress')
        """)
        active = cursor.fetchone()
        print(f"✅ Sesiones activas: {active['count']}")
        
        # Verificar base de conocimiento
        agent = TroubleshootingAgent()
        print(f"✅ Problemas en KB: {len(agent.knowledge_base)}")
        
        # Verificar vistas materializadas
        cursor.execute("""
            SELECT matviewname 
            FROM pg_matviews 
            WHERE schemaname = 'public' 
            AND matviewname LIKE 'mv_%troubleshooting%'
        """)
        views = cursor.fetchall()
        print(f"✅ Vistas materializadas: {len(views)}")
        
        cursor.close()
        conn.close()
        
        print("\n✅ Sistema saludable")
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False


def cleanup_old_sessions(db_url: str, days: int = 90):
    """Limpia sesiones antiguas"""
    print(f"🧹 Limpiando sesiones más antiguas de {days} días...")
    
    try:
        conn = psycopg2.connect(db_url)
        cursor = conn.cursor()
        
        cutoff_date = datetime.now() - timedelta(days=days)
        
        # Contar sesiones a eliminar
        cursor.execute("""
            SELECT COUNT(*) 
            FROM support_troubleshooting_sessions 
            WHERE started_at < %s 
            AND status IN ('resolved', 'escalated', 'closed')
        """, (cutoff_date,))
        count = cursor.fetchone()[0]
        
        if count == 0:
            print("✅ No hay sesiones antiguas para limpiar")
            cursor.close()
            conn.close()
            return
        
        # Confirmar
        response = input(f"¿Eliminar {count} sesiones antiguas? (yes/no): ")
        if response.lower() != 'yes':
            print("❌ Operación cancelada")
            cursor.close()
            conn.close()
            return
        
        # Eliminar
        cursor.execute("""
            DELETE FROM support_troubleshooting_sessions 
            WHERE started_at < %s 
            AND status IN ('resolved', 'escalated', 'closed')
        """, (cutoff_date,))
        
        deleted = cursor.rowcount
        conn.commit()
        
        print(f"✅ Eliminadas {deleted} sesiones antiguas")
        
        cursor.close()
        conn.close()
        
    except Exception as e:
        print(f"❌ Error: {e}")


def refresh_views(db_url: str):
    """Refresca vistas materializadas"""
    print("🔄 Refrescando vistas materializadas...")
    
    try:
        conn = psycopg2.connect(db_url)
        cursor = conn.cursor()
        
        cursor.execute("SELECT refresh_troubleshooting_views();")
        conn.commit()
        
        print("✅ Vistas materializadas refrescadas")
        
        cursor.close()
        conn.close()
        
    except Exception as e:
        print(f"❌ Error: {e}")


def export_stats(db_url: str, days: int = 30, output_file: str = None):
    """Exporta estadísticas a JSON"""
    print(f"📊 Exportando estadísticas de últimos {days} días...")
    
    try:
        conn = psycopg2.connect(db_url)
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        
        start_date = datetime.now() - timedelta(days=days)
        
        # Obtener estadísticas
        cursor.execute("""
            SELECT * FROM get_troubleshooting_stats(%s, %s)
        """, (start_date, datetime.now()))
        
        stats = cursor.fetchone()
        
        # Top problemas
        cursor.execute("""
            SELECT * FROM mv_top_problems
            ORDER BY total_sessions DESC
            LIMIT 10
        """)
        top_problems = cursor.fetchall()
        
        # Feedback summary
        cursor.execute("""
            SELECT 
                COUNT(*) as total_feedback,
                AVG(rating) as avg_rating,
                COUNT(CASE WHEN was_helpful = true THEN 1 END) as helpful_count
            FROM support_troubleshooting_feedback
            WHERE collected_at >= %s
        """, (start_date,))
        feedback = cursor.fetchone()
        
        result = {
            "export_date": datetime.now().isoformat(),
            "period_days": days,
            "summary": dict(stats) if stats else {},
            "top_problems": [dict(p) for p in top_problems],
            "feedback": dict(feedback) if feedback else {}
        }
        
        if output_file:
            with open(output_file, 'w') as f:
                json.dump(result, f, indent=2, default=str)
            print(f"✅ Estadísticas exportadas a {output_file}")
        else:
            print(json.dumps(result, indent=2, default=str))
        
        cursor.close()
        conn.close()
        
    except Exception as e:
        print(f"❌ Error: {e}")


def add_problem(kb_file: str, problem_id: str):
    """Agrega un nuevo problema interactivamente"""
    print(f"➕ Agregando nuevo problema: {problem_id}")
    
    kb_path = Path(kb_file)
    if not kb_path.exists():
        print(f"❌ Archivo no encontrado: {kb_file}")
        return
    
    with open(kb_path, 'r', encoding='utf-8') as f:
        kb = json.load(f)
    
    if problem_id in kb:
        response = input(f"El problema {problem_id} ya existe. ¿Sobrescribir? (yes/no): ")
        if response.lower() != 'yes':
            print("❌ Operación cancelada")
            return
    
    print("\nIngresa la información del problema:")
    title = input("Título: ")
    description = input("Descripción: ")
    category = input("Categoría (instalación/configuración/conectividad/etc): ")
    estimated_time = input("Tiempo estimado (ej: 15 minutos): ")
    difficulty = input("Dificultad (fácil/medio/avanzado): ")
    
    steps = []
    print("\nAgrega pasos (deja título vacío para terminar):")
    step_num = 1
    while True:
        step_title = input(f"\nPaso {step_num} - Título: ")
        if not step_title:
            break
        
        step_desc = input("Descripción: ")
        instructions = []
        print("Instrucciones (una por línea, línea vacía para terminar):")
        while True:
            inst = input("  > ")
            if not inst:
                break
            instructions.append(inst)
        
        expected = input("Resultado esperado: ")
        
        warnings = []
        print("Precauciones (una por línea, línea vacía para terminar):")
        while True:
            warn = input("  > ")
            if not warn:
                break
            warnings.append(warn)
        
        steps.append({
            "step_number": step_num,
            "title": step_title,
            "description": step_desc,
            "instructions": instructions,
            "expected_result": expected,
            "warnings": warnings,
            "resources": []
        })
        
        step_num += 1
    
    kb[problem_id] = {
        "problem_title": title,
        "problem_description": description,
        "category": category,
        "estimated_time": estimated_time,
        "difficulty": difficulty,
        "prerequisites": [],
        "steps": steps,
        "common_issues": [],
        "escalation_criteria": []
    }
    
    with open(kb_path, 'w', encoding='utf-8') as f:
        json.dump(kb, f, indent=2, ensure_ascii=False)
    
    print(f"\n✅ Problema {problem_id} agregado exitosamente")


def main():
    parser = argparse.ArgumentParser(description='Utilidades para Sistema de Troubleshooting')
    parser.add_argument('--db-url', required=True, help='URL de conexión a PostgreSQL')
    
    subparsers = parser.add_subparsers(dest='command', help='Comando a ejecutar')
    
    # Health check
    subparsers.add_parser('health', help='Verificar salud del sistema')
    
    # Cleanup
    cleanup_parser = subparsers.add_parser('cleanup', help='Limpiar datos antiguos')
    cleanup_parser.add_argument('--days', type=int, default=90, help='Días hacia atrás')
    
    # Refresh views
    subparsers.add_parser('refresh-views', help='Refrescar vistas materializadas')
    
    # Export stats
    export_parser = subparsers.add_parser('export-stats', help='Exportar estadísticas')
    export_parser.add_argument('--days', type=int, default=30, help='Días hacia atrás')
    export_parser.add_argument('--output', help='Archivo de salida (JSON)')
    
    # Add problem
    add_parser = subparsers.add_parser('add-problem', help='Agregar nuevo problema')
    add_parser.add_argument('--kb-file', default='data/integrations/support_troubleshooting_kb.json')
    add_parser.add_argument('problem_id', help='ID del problema')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    if args.command == 'health':
        health_check(args.db_url)
    elif args.command == 'cleanup':
        cleanup_old_sessions(args.db_url, args.days)
    elif args.command == 'refresh-views':
        refresh_views(args.db_url)
    elif args.command == 'export-stats':
        export_stats(args.db_url, args.days, args.output)
    elif args.command == 'add-problem':
        add_problem(args.kb_file, args.problem_id)


if __name__ == '__main__':
    main()



