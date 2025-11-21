"""
Herramientas de Análisis Avanzado para Troubleshooting
Scripts para análisis profundo y optimización
"""

import sys
import json
import argparse
from pathlib import Path
from datetime import datetime, timedelta
import psycopg2
from psycopg2.extras import RealDictCursor, Json

sys.path.insert(0, str(Path(__file__).parent.parent / "data" / "integrations"))


class TroubleshootingAnalyzer:
    """Analizador avanzado de troubleshooting"""
    
    def __init__(self, db_url: str):
        self.db_url = db_url
        self.conn = None
    
    def connect(self):
        """Conectar a base de datos"""
        self.conn = psycopg2.connect(self.db_url)
    
    def close(self):
        """Cerrar conexión"""
        if self.conn:
            self.conn.close()
    
    def analyze_trends(self, days: int = 30, group_by: str = "day"):
        """Analizar tendencias temporales"""
        cursor = self.conn.cursor(cursor_factory=RealDictCursor)
        cursor.execute("""
            SELECT * FROM analyze_troubleshooting_trends(%s, %s)
        """, (days, group_by))
        
        trends = cursor.fetchall()
        cursor.close()
        
        return [dict(t) for t in trends]
    
    def identify_improvements(self, min_sessions: int = 5, max_resolution_rate: float = 70.0):
        """Identificar problemas que necesitan mejora"""
        cursor = self.conn.cursor(cursor_factory=RealDictCursor)
        cursor.execute("""
            SELECT * FROM identify_problems_needing_improvement(%s, %s)
        """, (min_sessions, max_resolution_rate))
        
        improvements = cursor.fetchall()
        cursor.close()
        
        return [dict(i) for i in improvements]
    
    def analyze_satisfaction(self, days: int = 30):
        """Analizar satisfacción del cliente"""
        cursor = self.conn.cursor(cursor_factory=RealDictCursor)
        cursor.execute("""
            SELECT * FROM analyze_customer_satisfaction(%s)
        """, (days,))
        
        satisfaction = cursor.fetchall()
        cursor.close()
        
        return [dict(s) for s in satisfaction]
    
    def generate_executive_report(self, days: int = 30):
        """Generar reporte ejecutivo"""
        start_date = datetime.now() - timedelta(days=days)
        end_date = datetime.now()
        
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT generate_executive_report(%s, %s)
        """, (start_date, end_date))
        
        report_json = cursor.fetchone()[0]
        cursor.close()
        
        return json.loads(json.dumps(report_json))
    
    def get_executive_summary(self):
        """Obtener resumen ejecutivo"""
        cursor = self.conn.cursor(cursor_factory=RealDictCursor)
        cursor.execute("SELECT * FROM vw_executive_summary")
        
        summary = cursor.fetchone()
        cursor.close()
        
        return dict(summary) if summary else {}
    
    def optimize_tables(self):
        """Optimizar tablas"""
        cursor = self.conn.cursor(cursor_factory=RealDictCursor)
        cursor.execute("SELECT * FROM optimize_troubleshooting_tables()")
        
        optimizations = cursor.fetchall()
        cursor.close()
        
        return [dict(o) for o in optimizations]


def main():
    parser = argparse.ArgumentParser(description='Análisis avanzado de troubleshooting')
    parser.add_argument('--db-url', required=True, help='URL de conexión a PostgreSQL')
    parser.add_argument('--command', required=True, 
                       choices=['trends', 'improvements', 'satisfaction', 'executive', 'summary', 'optimize'],
                       help='Comando a ejecutar')
    parser.add_argument('--days', type=int, default=30, help='Días hacia atrás')
    parser.add_argument('--group-by', default='day', choices=['day', 'week', 'month'],
                       help='Agrupar por (para trends)')
    parser.add_argument('--output', help='Archivo de salida (JSON)')
    
    args = parser.parse_args()
    
    analyzer = TroubleshootingAnalyzer(args.db_url)
    analyzer.connect()
    
    try:
        if args.command == 'trends':
            results = analyzer.analyze_trends(args.days, args.group_by)
        elif args.command == 'improvements':
            results = analyzer.identify_improvements()
        elif args.command == 'satisfaction':
            results = analyzer.analyze_satisfaction(args.days)
        elif args.command == 'executive':
            results = analyzer.generate_executive_report(args.days)
        elif args.command == 'summary':
            results = analyzer.get_executive_summary()
        elif args.command == 'optimize':
            results = analyzer.optimize_tables()
        
        if args.output:
            with open(args.output, 'w') as f:
                json.dump(results, f, indent=2, default=str)
            print(f"Resultados guardados en {args.output}")
        else:
            print(json.dumps(results, indent=2, default=str))
            
    finally:
        analyzer.close()


if __name__ == '__main__':
    main()



