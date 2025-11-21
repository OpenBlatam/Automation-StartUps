"""
Sistema de Analytics y Métricas para Documentos
================================================

Genera reportes, estadísticas y métricas del procesamiento de documentos.
"""

from typing import Dict, Any, List, Optional
from dataclasses import dataclass
from datetime import datetime, timedelta
import logging
from collections import Counter, defaultdict

logger = logging.getLogger(__name__)


@dataclass
class ProcessingStats:
    """Estadísticas de procesamiento"""
    total_documents: int
    by_type: Dict[str, int]
    by_ocr_provider: Dict[str, int]
    avg_confidence: float
    avg_processing_time: float
    success_rate: float
    error_rate: float


@dataclass
class PeriodStats:
    """Estadísticas por período"""
    period: str  # day, week, month
    date: str
    documents_processed: int
    total_size: int
    avg_quality_score: float
    top_types: List[Dict[str, Any]]
    top_issues: List[str]


class DocumentAnalytics:
    """Generador de analytics y métricas"""
    
    def __init__(self, db_connection=None):
        self.db = db_connection
        self.logger = logging.getLogger(__name__)
    
    def get_processing_stats(
        self,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> ProcessingStats:
        """Obtiene estadísticas generales de procesamiento"""
        if not self.db:
            raise ValueError("Conexión a BD requerida")
        
        try:
            cursor = self.db.cursor()
            
            date_filter = ""
            params = []
            if start_date:
                date_filter += " AND processed_at >= %s"
                params.append(start_date)
            if end_date:
                date_filter += " AND processed_at <= %s"
                params.append(end_date)
            
            # Total de documentos
            cursor.execute(f"""
                SELECT COUNT(*) FROM processed_documents
                WHERE 1=1 {date_filter}
            """, params)
            total = cursor.fetchone()[0]
            
            # Por tipo
            cursor.execute(f"""
                SELECT document_type, COUNT(*) as count
                FROM processed_documents
                WHERE 1=1 {date_filter}
                GROUP BY document_type
            """, params)
            by_type = {row[0]: row[1] for row in cursor.fetchall()}
            
            # Por proveedor OCR
            cursor.execute(f"""
                SELECT ocr_provider, COUNT(*) as count
                FROM processed_documents
                WHERE ocr_provider IS NOT NULL {date_filter}
                GROUP BY ocr_provider
            """, params)
            by_provider = {row[0]: row[1] for row in cursor.fetchall()}
            
            # Promedios
            cursor.execute(f"""
                SELECT 
                    AVG(classification_confidence) as avg_class,
                    AVG(ocr_confidence) as avg_ocr
                FROM processed_documents
                WHERE 1=1 {date_filter}
            """, params)
            avg_row = cursor.fetchone()
            avg_confidence = (avg_row[0] + avg_row[1]) / 2 if avg_row[0] and avg_row[1] else 0.0
            
            # Tasa de éxito (basada en logs)
            cursor.execute(f"""
                SELECT 
                    COUNT(*) FILTER (WHERE status = 'completed') as success,
                    COUNT(*) as total
                FROM document_processing_log
                WHERE 1=1 {date_filter.replace('processed_at', 'created_at')}
            """, params)
            success_row = cursor.fetchone()
            success_rate = success_row[0] / success_row[1] if success_row[1] > 0 else 0.0
            error_rate = 1 - success_rate
            
            return ProcessingStats(
                total_documents=total,
                by_type=by_type,
                by_ocr_provider=by_provider,
                avg_confidence=float(avg_confidence) if avg_confidence else 0.0,
                avg_processing_time=0.0,  # Requeriría tracking adicional
                success_rate=success_rate,
                error_rate=error_rate
            )
            
        except Exception as e:
            self.logger.error(f"Error obteniendo estadísticas: {e}")
            raise
    
    def get_daily_stats(
        self,
        days: int = 30
    ) -> List[PeriodStats]:
        """Obtiene estadísticas diarias"""
        if not self.db:
            raise ValueError("Conexión a BD requerida")
        
        try:
            cursor = self.db.cursor()
            
            cursor.execute("""
                SELECT 
                    DATE(processed_at) as process_date,
                    COUNT(*) as count,
                    SUM(file_size) as total_size,
                    AVG(classification_confidence) as avg_quality
                FROM processed_documents
                WHERE processed_at >= CURRENT_DATE - INTERVAL '%s days'
                GROUP BY DATE(processed_at)
                ORDER BY process_date DESC
            """, (days,))
            
            daily_stats = []
            for row in cursor.fetchall():
                date_str, count, total_size, avg_quality = row
                
                # Top tipos del día
                cursor.execute("""
                    SELECT document_type, COUNT(*) as count
                    FROM processed_documents
                    WHERE DATE(processed_at) = %s
                    GROUP BY document_type
                    ORDER BY count DESC
                    LIMIT 5
                """, (date_str,))
                
                top_types = [
                    {"type": r[0], "count": r[1]}
                    for r in cursor.fetchall()
                ]
                
                daily_stats.append(PeriodStats(
                    period="day",
                    date=date_str.isoformat() if hasattr(date_str, 'isoformat') else str(date_str),
                    documents_processed=count,
                    total_size=int(total_size or 0),
                    avg_quality_score=float(avg_quality or 0),
                    top_types=top_types,
                    top_issues=[]
                ))
            
            return daily_stats
            
        except Exception as e:
            self.logger.error(f"Error obteniendo estadísticas diarias: {e}")
            return []
    
    def get_quality_trends(self, days: int = 30) -> Dict[str, Any]:
        """Obtiene tendencias de calidad"""
        if not self.db:
            raise ValueError("Conexión a BD requerida")
        
        try:
            cursor = self.db.cursor()
            
            cursor.execute("""
                SELECT 
                    DATE(processed_at) as process_date,
                    AVG(ocr_confidence) as avg_ocr,
                    AVG(classification_confidence) as avg_class,
                    COUNT(*) as count
                FROM processed_documents
                WHERE processed_at >= CURRENT_DATE - INTERVAL '%s days'
                GROUP BY DATE(processed_at)
                ORDER BY process_date ASC
            """, (days,))
            
            trends = {
                "dates": [],
                "ocr_confidence": [],
                "classification_confidence": [],
                "counts": []
            }
            
            for row in cursor.fetchall():
                date_str, avg_ocr, avg_class, count = row
                trends["dates"].append(str(date_str))
                trends["ocr_confidence"].append(float(avg_ocr or 0))
                trends["classification_confidence"].append(float(avg_class or 0))
                trends["counts"].append(count)
            
            return trends
            
        except Exception as e:
            self.logger.error(f"Error obteniendo tendencias: {e}")
            return {"dates": [], "ocr_confidence": [], "classification_confidence": [], "counts": []}
    
    def get_error_analysis(self, days: int = 30) -> Dict[str, Any]:
        """Analiza errores de procesamiento"""
        if not self.db:
            raise ValueError("Conexión a BD requerida")
        
        try:
            cursor = self.db.cursor()
            
            cursor.execute("""
                SELECT 
                    error_message,
                    COUNT(*) as count
                FROM document_processing_log
                WHERE status = 'failed'
                    AND created_at >= CURRENT_DATE - INTERVAL '%s days'
                GROUP BY error_message
                ORDER BY count DESC
                LIMIT 10
            """, (days,))
            
            errors = [
                {"error": row[0], "count": row[1]}
                for row in cursor.fetchall()
            ]
            
            return {
                "total_errors": sum(e["count"] for e in errors),
                "error_distribution": errors,
                "top_error": errors[0]["error"] if errors else None
            }
            
        except Exception as e:
            self.logger.error(f"Error analizando errores: {e}")
            return {"total_errors": 0, "error_distribution": [], "top_error": None}
    
    def get_performance_report(self) -> Dict[str, Any]:
        """Genera reporte de performance completo"""
        stats = self.get_processing_stats()
        daily_stats = self.get_daily_stats(30)
        trends = self.get_quality_trends(30)
        errors = self.get_error_analysis(30)
        
        return {
            "summary": {
                "total_documents": stats.total_documents,
                "avg_confidence": stats.avg_confidence,
                "success_rate": stats.success_rate,
                "error_rate": stats.error_rate
            },
            "distribution": {
                "by_type": stats.by_type,
                "by_provider": stats.by_ocr_provider
            },
            "daily_stats": [
                {
                    "date": s.date,
                    "count": s.documents_processed,
                    "avg_quality": s.avg_quality_score
                }
                for s in daily_stats[:7]  # Últimos 7 días
            ],
            "trends": trends,
            "errors": errors,
            "generated_at": datetime.now().isoformat()
        }

