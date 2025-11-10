"""
Módulo de Analytics para Categorización Automática.

Características:
- Tracking de precisión de categorización
- Ajuste automático de umbrales
- Aprendizaje de correcciones manuales
- Métricas de performance
"""
import logging
from typing import Dict, Any, Optional, List
from dataclasses import dataclass
from datetime import datetime, timedelta
from collections import defaultdict

logger = logging.getLogger(__name__)


@dataclass
class CategorizationAccuracy:
    """Métrica de precisión de categorización."""
    category: str
    total_classified: int
    correct: int
    incorrect: int
    accuracy_rate: float
    avg_confidence: float
    manual_corrections: int


@dataclass
class CategorizationMetrics:
    """Métricas de categorización."""
    period_start: datetime
    period_end: datetime
    total_classified: int
    overall_accuracy: float
    avg_confidence: float
    category_accuracy: List[CategorizationAccuracy]
    top_misclassified: List[Dict[str, Any]]


class SupportCategorizationAnalytics:
    """Analytics para categorización automática."""
    
    def __init__(self, db_connection: Any = None):
        """
        Inicializa el analizador de categorización.
        
        Args:
            db_connection: Conexión a BD
        """
        self.db_connection = db_connection
    
    def track_categorization(
        self,
        ticket_id: str,
        auto_category: str,
        auto_subcategory: Optional[str],
        confidence: float,
        final_category: Optional[str] = None,
        final_subcategory: Optional[str] = None,
        manually_corrected: bool = False
    ) -> bool:
        """
        Registra una categorización para analytics.
        
        Args:
            ticket_id: ID del ticket
            auto_category: Categoría asignada automáticamente
            auto_subcategory: Subcategoría asignada automáticamente
            confidence: Confianza de la categorización
            final_category: Categoría final (si fue corregida)
            final_subcategory: Subcategoría final (si fue corregida)
            manually_corrected: Si fue corregida manualmente
            
        Returns:
            True si se registró correctamente
        """
        if not self.db_connection:
            return False
        
        try:
            cursor = self.db_connection.cursor()
            
            # Registrar en metadata del ticket
            cursor.execute("""
                UPDATE support_tickets
                SET metadata = COALESCE(metadata, '{}'::jsonb) || 
                    jsonb_build_object(
                        'auto_categorization', jsonb_build_object(
                            'category', %s,
                            'subcategory', %s,
                            'confidence', %s,
                            'timestamp', NOW(),
                            'manually_corrected', %s,
                            'final_category', %s,
                            'final_subcategory', %s
                        )
                    ),
                    updated_at = NOW()
                WHERE ticket_id = %s
            """, (
                auto_category,
                auto_subcategory,
                confidence,
                manually_corrected,
                final_category or auto_category,
                final_subcategory or auto_subcategory,
                ticket_id
            ))
            
            self.db_connection.commit()
            cursor.close()
            return True
            
        except Exception as e:
            logger.error(f"Error registrando categorización para ticket {ticket_id}: {e}")
            if self.db_connection:
                self.db_connection.rollback()
            return False
    
    def calculate_accuracy_metrics(
        self,
        days: int = 30
    ) -> CategorizationMetrics:
        """
        Calcula métricas de precisión de categorización.
        
        Args:
            days: Días hacia atrás para analizar
            
        Returns:
            CategorizationMetrics con métricas
        """
        if not self.db_connection:
            return CategorizationMetrics(
                period_start=datetime.now() - timedelta(days=days),
                period_end=datetime.now(),
                total_classified=0,
                overall_accuracy=0.0,
                avg_confidence=0.0,
                category_accuracy=[],
                top_misclassified=[]
            )
        
        try:
            cursor = self.db_connection.cursor()
            
            # Obtener tickets con categorización automática
            cursor.execute("""
                SELECT 
                    ticket_id,
                    category,
                    subcategory,
                    metadata->'auto_categorization'->>'category' as auto_category,
                    metadata->'auto_categorization'->>'subcategory' as auto_subcategory,
                    (metadata->'auto_categorization'->>'confidence')::float as confidence,
                    (metadata->'auto_categorization'->>'manually_corrected')::boolean as corrected
                FROM support_tickets
                WHERE created_at >= NOW() - INTERVAL '%s days'
                AND metadata->'auto_categorization' IS NOT NULL
            """, (days,))
            
            tickets = cursor.fetchall()
            
            # Calcular métricas por categoría
            category_stats = defaultdict(lambda: {
                "total": 0,
                "correct": 0,
                "confidence_sum": 0.0,
                "corrections": 0
            })
            
            misclassified = []
            
            for row in tickets:
                ticket_id, final_cat, final_subcat, auto_cat, auto_subcat, confidence, corrected = row
                
                if not auto_cat:
                    continue
                
                category_stats[auto_cat]["total"] += 1
                category_stats[auto_cat]["confidence_sum"] += confidence or 0.0
                
                # Verificar si fue correcto
                is_correct = (final_cat == auto_cat) and not corrected
                
                if is_correct:
                    category_stats[auto_cat]["correct"] += 1
                else:
                    category_stats[auto_cat]["corrections"] += 1
                    misclassified.append({
                        "ticket_id": ticket_id,
                        "auto_category": auto_cat,
                        "final_category": final_cat,
                        "confidence": confidence
                    })
            
            # Construir resultados
            total_classified = len(tickets)
            total_correct = sum(stats["correct"] for stats in category_stats.values())
            overall_accuracy = (total_correct / total_classified * 100) if total_classified > 0 else 0.0
            
            avg_confidence = (
                sum(stats["confidence_sum"] for stats in category_stats.values()) / total_classified
                if total_classified > 0 else 0.0
            )
            
            category_accuracy = []
            for category, stats in category_stats.items():
                accuracy_rate = (stats["correct"] / stats["total"] * 100) if stats["total"] > 0 else 0.0
                avg_conf = stats["confidence_sum"] / stats["total"] if stats["total"] > 0 else 0.0
                
                category_accuracy.append(CategorizationAccuracy(
                    category=category,
                    total_classified=stats["total"],
                    correct=stats["correct"],
                    incorrect=stats["total"] - stats["correct"],
                    accuracy_rate=accuracy_rate,
                    avg_confidence=avg_conf,
                    manual_corrections=stats["corrections"]
                ))
            
            # Ordenar por precisión
            category_accuracy.sort(key=lambda x: x.accuracy_rate, reverse=True)
            
            # Top misclassifications
            top_misclassified = sorted(
                misclassified,
                key=lambda x: x.get("confidence", 0),
                reverse=True
            )[:10]
            
            cursor.close()
            
            return CategorizationMetrics(
                period_start=datetime.now() - timedelta(days=days),
                period_end=datetime.now(),
                total_classified=total_classified,
                overall_accuracy=overall_accuracy,
                avg_confidence=avg_confidence,
                category_accuracy=category_accuracy,
                top_misclassified=top_misclassified
            )
            
        except Exception as e:
            logger.error(f"Error calculando métricas de categorización: {e}")
            return CategorizationMetrics(
                period_start=datetime.now() - timedelta(days=days),
                period_end=datetime.now(),
                total_classified=0,
                overall_accuracy=0.0,
                avg_confidence=0.0,
                category_accuracy=[],
                top_misclassified=[]
            )
    
    def get_optimal_confidence_threshold(
        self,
        category: Optional[str] = None,
        target_accuracy: float = 0.85
    ) -> float:
        """
        Calcula el umbral óptimo de confianza para una categoría.
        
        Args:
            category: Categoría específica (None = general)
            target_accuracy: Precisión objetivo (default: 85%)
            
        Returns:
            Umbral de confianza óptimo
        """
        if not self.db_connection:
            return 0.7  # Default
        
        try:
            cursor = self.db_connection.cursor()
            
            # Obtener distribución de confianza vs precisión
            query = """
                SELECT 
                    CASE 
                        WHEN (metadata->'auto_categorization'->>'confidence')::float >= 0.9 THEN '0.9-1.0'
                        WHEN (metadata->'auto_categorization'->>'confidence')::float >= 0.8 THEN '0.8-0.9'
                        WHEN (metadata->'auto_categorization'->>'confidence')::float >= 0.7 THEN '0.7-0.8'
                        WHEN (metadata->'auto_categorization'->>'confidence')::float >= 0.6 THEN '0.6-0.7'
                        ELSE '0.0-0.6'
                    END as confidence_range,
                    COUNT(*) as total,
                    COUNT(*) FILTER (
                        WHERE category = (metadata->'auto_categorization'->>'category')
                        AND (metadata->'auto_categorization'->>'manually_corrected')::boolean IS NOT TRUE
                    ) as correct
                FROM support_tickets
                WHERE created_at >= NOW() - INTERVAL '30 days'
                AND metadata->'auto_categorization' IS NOT NULL
            """
            
            if category:
                query += " AND (metadata->'auto_categorization'->>'category') = %s"
                cursor.execute(query, (category,))
            else:
                cursor.execute(query)
            
            ranges = cursor.fetchall()
            
            # Encontrar el rango mínimo que cumple con target_accuracy
            for conf_range, total, correct in ranges:
                if total > 0:
                    accuracy = correct / total
                    if accuracy >= target_accuracy:
                        # Extraer el valor mínimo del rango
                        min_val = float(conf_range.split('-')[0])
                        cursor.close()
                        return min_val
            
            cursor.close()
            return 0.7  # Default si no se encuentra
            
        except Exception as e:
            logger.error(f"Error calculando umbral óptimo: {e}")
            return 0.7

