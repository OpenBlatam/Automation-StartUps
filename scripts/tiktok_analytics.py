#!/usr/bin/env python3
"""
Sistema de analytics para tracking de videos procesados
Registra métricas, estadísticas y genera reportes
"""

import os
import json
import sqlite3
import logging
from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
from collections import defaultdict

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class TikTokAnalytics:
    """Sistema de analytics para videos de TikTok"""
    
    def __init__(self, db_path: Optional[str] = None):
        """
        Inicializa el sistema de analytics
        
        Args:
            db_path: Ruta a la base de datos SQLite (opcional)
        """
        self.db_path = db_path or os.path.join(
            os.path.expanduser("~"), ".tiktok_analytics.db"
        )
        self._init_database()
    
    def _init_database(self):
        """Inicializa la base de datos con las tablas necesarias"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Tabla de procesamientos
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS processings (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                url TEXT NOT NULL,
                video_id TEXT,
                status TEXT NOT NULL,
                started_at TIMESTAMP NOT NULL,
                completed_at TIMESTAMP,
                processing_time REAL,
                file_size INTEGER,
                duration REAL,
                from_cache BOOLEAN DEFAULT 0,
                error_message TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Tabla de estadísticas diarias
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS daily_stats (
                date DATE PRIMARY KEY,
                total_processed INTEGER DEFAULT 0,
                successful INTEGER DEFAULT 0,
                failed INTEGER DEFAULT 0,
                avg_processing_time REAL,
                total_size_mb REAL,
                cache_hits INTEGER DEFAULT 0
            )
        """)
        
        # Índices para mejor rendimiento
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_url ON processings(url)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_status ON processings(status)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_started_at ON processings(started_at)")
        
        conn.commit()
        conn.close()
        logger.info(f"Base de datos inicializada: {self.db_path}")
    
    def record_processing(self, data: Dict[str, Any]) -> int:
        """
        Registra un procesamiento de video
        
        Args:
            data: Diccionario con datos del procesamiento
            
        Returns:
            ID del registro creado
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO processings (
                url, video_id, status, started_at, completed_at,
                processing_time, file_size, duration, from_cache, error_message
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            data.get('url'),
            data.get('video_id'),
            data.get('status', 'unknown'),
            data.get('started_at'),
            data.get('completed_at'),
            data.get('processing_time'),
            data.get('file_size'),
            data.get('duration'),
            1 if data.get('from_cache') else 0,
            data.get('error_message')
        ))
        
        record_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        # Actualizar estadísticas diarias
        self._update_daily_stats(data.get('started_at', datetime.now().isoformat()))
        
        return record_id
    
    def _update_daily_stats(self, timestamp: str):
        """Actualiza las estadísticas diarias"""
        date = datetime.fromisoformat(timestamp).date().isoformat()
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Obtener estadísticas del día
        cursor.execute("""
            SELECT 
                COUNT(*) as total,
                SUM(CASE WHEN status = 'completed' THEN 1 ELSE 0 END) as successful,
                SUM(CASE WHEN status = 'error' THEN 1 ELSE 0 END) as failed,
                AVG(processing_time) as avg_time,
                SUM(file_size) / 1024.0 / 1024.0 as total_mb,
                SUM(CASE WHEN from_cache = 1 THEN 1 ELSE 0 END) as cache_hits
            FROM processings
            WHERE DATE(started_at) = ?
        """, (date,))
        
        row = cursor.fetchone()
        if row:
            cursor.execute("""
                INSERT OR REPLACE INTO daily_stats 
                (date, total_processed, successful, failed, avg_processing_time, total_size_mb, cache_hits)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (date, *row))
        
        conn.commit()
        conn.close()
    
    def get_stats(self, days: int = 7) -> Dict[str, Any]:
        """
        Obtiene estadísticas de los últimos N días
        
        Args:
            days: Número de días a analizar
            
        Returns:
            Diccionario con estadísticas
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        start_date = (datetime.now() - timedelta(days=days)).isoformat()
        
        # Estadísticas generales
        cursor.execute("""
            SELECT 
                COUNT(*) as total,
                SUM(CASE WHEN status = 'completed' THEN 1 ELSE 0 END) as successful,
                SUM(CASE WHEN status = 'error' THEN 1 ELSE 0 END) as failed,
                AVG(processing_time) as avg_time,
                SUM(file_size) / 1024.0 / 1024.0 as total_mb,
                SUM(CASE WHEN from_cache = 1 THEN 1 ELSE 0 END) as cache_hits
            FROM processings
            WHERE started_at >= ?
        """, (start_date,))
        
        row = cursor.fetchone()
        stats = {
            'period_days': days,
            'total_processed': row[0] or 0,
            'successful': row[1] or 0,
            'failed': row[2] or 0,
            'success_rate': (row[1] / row[0] * 100) if row[0] > 0 else 0,
            'avg_processing_time': row[3] or 0,
            'total_size_mb': row[4] or 0,
            'cache_hits': row[5] or 0,
            'cache_hit_rate': (row[5] / row[0] * 100) if row[0] > 0 else 0
        }
        
        # Estadísticas por día
        cursor.execute("""
            SELECT date, total_processed, successful, failed, avg_processing_time
            FROM daily_stats
            WHERE date >= ?
            ORDER BY date DESC
        """, (start_date.split('T')[0],))
        
        stats['daily_breakdown'] = [
            {
                'date': row[0],
                'total': row[1],
                'successful': row[2],
                'failed': row[3],
                'avg_time': row[4]
            }
            for row in cursor.fetchall()
        ]
        
        conn.close()
        return stats
    
    def get_top_urls(self, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Obtiene las URLs más procesadas
        
        Args:
            limit: Número máximo de resultados
            
        Returns:
            Lista de URLs con conteos
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT url, COUNT(*) as count, 
                   SUM(CASE WHEN status = 'completed' THEN 1 ELSE 0 END) as successful
            FROM processings
            GROUP BY url
            ORDER BY count DESC
            LIMIT ?
        """, (limit,))
        
        results = [
            {'url': row[0], 'count': row[1], 'successful': row[2]}
            for row in cursor.fetchall()
        ]
        
        conn.close()
        return results
    
    def export_report(self, output_path: str, days: int = 30):
        """
        Exporta un reporte completo en JSON
        
        Args:
            output_path: Ruta donde guardar el reporte
            days: Días a incluir en el reporte
        """
        stats = self.get_stats(days)
        top_urls = self.get_top_urls(20)
        
        report = {
            'generated_at': datetime.now().isoformat(),
            'period_days': days,
            'summary': stats,
            'top_urls': top_urls
        }
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        
        logger.info(f"Reporte exportado a: {output_path}")
        return report


def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='Analytics de videos de TikTok')
    parser.add_argument('command', choices=['stats', 'report', 'top'], help='Comando a ejecutar')
    parser.add_argument('-d', '--days', type=int, default=7, help='Días a analizar')
    parser.add_argument('-o', '--output', type=str, help='Archivo de salida para reporte')
    parser.add_argument('-l', '--limit', type=int, default=10, help='Límite para top URLs')
    
    args = parser.parse_args()
    
    analytics = TikTokAnalytics()
    
    if args.command == 'stats':
        stats = analytics.get_stats(args.days)
        print(json.dumps(stats, indent=2, ensure_ascii=False))
    
    elif args.command == 'report':
        output = args.output or f"tiktok_report_{datetime.now().strftime('%Y%m%d')}.json"
        report = analytics.export_report(output, args.days)
        print(f"✅ Reporte generado: {output}")
        print(f"📊 Total procesados: {report['summary']['total_processed']}")
        print(f"✅ Exitosos: {report['summary']['successful']}")
        print(f"❌ Fallidos: {report['summary']['failed']}")
    
    elif args.command == 'top':
        top = analytics.get_top_urls(args.limit)
        print(f"\n🔝 Top {args.limit} URLs más procesadas:\n")
        for i, item in enumerate(top, 1):
            print(f"{i}. {item['url']}")
            print(f"   Procesada {item['count']} veces ({item['successful']} exitosas)")


if __name__ == '__main__':
    main()


