"""
Sistema de A/B Testing para Mejora Continua del Chatbot.

Características:
- Testing de diferentes prompts de LLM
- Testing de umbrales de confianza
- Testing de estrategias de enrutamiento
- Tracking de métricas por variante
- Análisis estadístico de resultados
"""
import logging
import random
import hashlib
from typing import Dict, Any, Optional, List
from dataclasses import dataclass
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)


@dataclass
class ABTestVariant:
    """Variante de un test A/B."""
    variant_id: str
    name: str
    config: Dict[str, Any]
    traffic_percentage: float  # 0.0 a 1.0


@dataclass
class ABTestResult:
    """Resultado de un test A/B."""
    test_id: str
    variant_id: str
    success: bool
    metrics: Dict[str, float]
    timestamp: str


class SupportABTesting:
    """Sistema de A/B testing para soporte."""
    
    def __init__(self, db_connection: Any = None):
        """
        Inicializa el sistema de A/B testing.
        
        Args:
            db_connection: Conexión a BD para tracking
        """
        self.db_connection = db_connection
        self.active_tests: Dict[str, List[ABTestVariant]] = {}
    
    def create_test(
        self,
        test_id: str,
        variants: List[ABTestVariant],
        description: str = ""
    ) -> bool:
        """
        Crea un nuevo test A/B.
        
        Args:
            test_id: ID único del test
            variants: Lista de variantes
            description: Descripción del test
            
        Returns:
            True si se creó exitosamente
        """
        # Validar que percentages sumen ~1.0
        total_percentage = sum(v.traffic_percentage for v in variants)
        if abs(total_percentage - 1.0) > 0.01:
            logger.error(f"Traffic percentages must sum to 1.0, got {total_percentage}")
            return False
        
        self.active_tests[test_id] = variants
        
        # Crear tabla de tracking si no existe
        if self.db_connection:
            try:
                cursor = self.db_connection.cursor()
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS support_ab_test_results (
                        id SERIAL PRIMARY KEY,
                        test_id VARCHAR(128) NOT NULL,
                        variant_id VARCHAR(128) NOT NULL,
                        ticket_id VARCHAR(128),
                        success BOOLEAN,
                        metrics JSONB,
                        created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
                    );
                    
                    CREATE INDEX IF NOT EXISTS idx_ab_test_test_id ON support_ab_test_results(test_id);
                    CREATE INDEX IF NOT EXISTS idx_ab_test_variant ON support_ab_test_results(variant_id);
                """)
                self.db_connection.commit()
                cursor.close()
            except Exception as e:
                logger.warning(f"Error creating AB test table: {e}")
        
        logger.info(f"Created AB test: {test_id} with {len(variants)} variants")
        return True
    
    def assign_variant(
        self,
        test_id: str,
        ticket_id: str
    ) -> Optional[str]:
        """
        Asigna una variante a un ticket.
        
        Args:
            test_id: ID del test
            ticket_id: ID del ticket
            
        Returns:
            ID de la variante asignada o None
        """
        if test_id not in self.active_tests:
            return None
        
        variants = self.active_tests[test_id]
        
        # Usar hash determinístico del ticket_id para consistencia
        hash_value = int(hashlib.md5(f"{test_id}:{ticket_id}".encode()).hexdigest(), 16)
        random_value = (hash_value % 10000) / 10000.0
        
        cumulative = 0.0
        for variant in variants:
            cumulative += variant.traffic_percentage
            if random_value <= cumulative:
                return variant.variant_id
        
        # Fallback al último
        return variants[-1].variant_id if variants else None
    
    def get_variant_config(
        self,
        test_id: str,
        variant_id: str
    ) -> Optional[Dict[str, Any]]:
        """Obtiene configuración de una variante."""
        if test_id not in self.active_tests:
            return None
        
        for variant in self.active_tests[test_id]:
            if variant.variant_id == variant_id:
                return variant.config
        
        return None
    
    def record_result(
        self,
        test_id: str,
        variant_id: str,
        ticket_id: str,
        success: bool,
        metrics: Dict[str, float]
    ) -> bool:
        """Registra resultado de un test."""
        if not self.db_connection:
            return False
        
        try:
            cursor = self.db_connection.cursor()
            cursor.execute("""
                INSERT INTO support_ab_test_results (
                    test_id,
                    variant_id,
                    ticket_id,
                    success,
                    metrics
                ) VALUES (%s, %s, %s, %s, %s::jsonb)
            """, (test_id, variant_id, ticket_id, success, metrics))
            
            self.db_connection.commit()
            cursor.close()
            return True
            
        except Exception as e:
            logger.error(f"Error recording AB test result: {e}")
            return False
    
    def get_test_results(
        self,
        test_id: str,
        days: int = 7
    ) -> Dict[str, Any]:
        """Obtiene resultados de un test."""
        if not self.db_connection:
            return {}
        
        try:
            cursor = self.db_connection.cursor()
            cursor.execute("""
                SELECT 
                    variant_id,
                    COUNT(*) as total,
                    COUNT(*) FILTER (WHERE success = true) as successful,
                    AVG((metrics->>'confidence')::float) as avg_confidence,
                    AVG((metrics->>'response_time_ms')::float) as avg_response_time
                FROM support_ab_test_results
                WHERE test_id = %s
                AND created_at >= NOW() - INTERVAL '%s days'
                GROUP BY variant_id
            """, (test_id, days))
            
            results = {}
            for row in cursor.fetchall():
                results[row[0]] = {
                    "total": row[1],
                    "successful": row[2],
                    "success_rate": (row[2] / row[1] * 100) if row[1] > 0 else 0.0,
                    "avg_confidence": float(row[3]) if row[3] else 0.0,
                    "avg_response_time_ms": float(row[4]) if row[4] else 0.0
                }
            
            cursor.close()
            return results
            
        except Exception as e:
            logger.error(f"Error getting AB test results: {e}")
            return {}


# Tests predefinidos comunes
def create_chatbot_prompt_test(
    ab_tester: SupportABTesting,
    test_id: str = "chatbot_prompt_v1"
) -> bool:
    """Crea test A/B para diferentes prompts del chatbot."""
    variants = [
        ABTestVariant(
            variant_id="control",
            name="Control (prompt actual)",
            config={
                "prompt_version": "v1",
                "temperature": 0.7,
                "max_tokens": 500
            },
            traffic_percentage=0.5
        ),
        ABTestVariant(
            variant_id="experimental",
            name="Experimental (prompt mejorado)",
            config={
                "prompt_version": "v2",
                "temperature": 0.8,
                "max_tokens": 600,
                "include_examples": True
            },
            traffic_percentage=0.5
        )
    ]
    
    return ab_tester.create_test(test_id, variants)


def create_confidence_threshold_test(
    ab_tester: SupportABTesting,
    test_id: str = "confidence_threshold_v1"
) -> bool:
    """Crea test A/B para diferentes umbrales de confianza."""
    variants = [
        ABTestVariant(
            variant_id="threshold_0.7",
            name="Threshold 0.7 (actual)",
            config={"confidence_threshold": 0.7},
            traffic_percentage=0.5
        ),
        ABTestVariant(
            variant_id="threshold_0.65",
            name="Threshold 0.65 (más permisivo)",
            config={"confidence_threshold": 0.65},
            traffic_percentage=0.5
        )
    ]
    
    return ab_tester.create_test(test_id, variants)

