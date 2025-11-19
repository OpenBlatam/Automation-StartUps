"""
Sistema de A/B Testing para Contenido de Nurturing

Permite probar diferentes variantes de contenido y medir
qué funciona mejor para aumentar engagement y conversión.
"""

from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
import logging
import random
import json
import hashlib

logger = logging.getLogger(__name__)


class ABTestingManager:
    """
    Gestor de A/B testing para contenido de nurturing.
    """
    
    def __init__(self, db_hook=None):
        """
        Inicializa el gestor de A/B testing.
        
        Args:
            db_hook: Hook de base de datos
        """
        self.db_hook = db_hook
        self.active_tests = {}
    
    def create_test(
        self,
        test_name: str,
        content_type: str,
        variant_a: Dict[str, Any],
        variant_b: Dict[str, Any],
        traffic_split: float = 0.5,
        target_metric: str = "engagement_rate"
    ) -> Dict[str, Any]:
        """
        Crea un nuevo test A/B.
        
        Args:
            test_name: Nombre del test
            content_type: Tipo de contenido (blog, guide, video, etc.)
            variant_a: Configuración de variante A
            variant_b: Configuración de variante B
            traffic_split: Porcentaje de tráfico para A (0.0-1.0)
            target_metric: Métrica objetivo (engagement_rate, conversion_rate, etc.)
        
        Returns:
            Dict con información del test creado
        """
        test_id = f"ab_test_{hashlib.md5(test_name.encode()).hexdigest()[:12]}"
        
        test_config = {
            "test_id": test_id,
            "test_name": test_name,
            "content_type": content_type,
            "variant_a": variant_a,
            "variant_b": variant_b,
            "traffic_split": traffic_split,
            "target_metric": target_metric,
            "status": "active",
            "created_at": datetime.now(),
            "results": {
                "variant_a": {"exposed": 0, "engaged": 0, "converted": 0},
                "variant_b": {"exposed": 0, "engaged": 0, "converted": 0}
            }
        }
        
        # Guardar en base de datos si hay hook
        if self.db_hook:
            try:
                self.db_hook.run(
                    """
                    INSERT INTO ab_tests (
                        test_id,
                        test_name,
                        content_type,
                        variant_a_config,
                        variant_b_config,
                        traffic_split,
                        target_metric,
                        status,
                        created_at
                    ) VALUES (%s, %s, %s, %s, %s, %s, %s, 'active', NOW())
                    ON CONFLICT (test_id) DO UPDATE
                    SET status = 'active', updated_at = NOW()
                    """,
                    parameters=(
                        test_id,
                        test_name,
                        content_type,
                        json.dumps(variant_a),
                        json.dumps(variant_b),
                        traffic_split,
                        target_metric
                    )
                )
            except Exception as e:
                logger.error(f"Error guardando test A/B: {e}")
        
        self.active_tests[test_id] = test_config
        
        logger.info(f"Test A/B creado: {test_id} - {test_name}")
        
        return test_config
    
    def assign_variant(
        self,
        test_id: str,
        lead_id: str
    ) -> str:
        """
        Asigna una variante a un lead.
        
        Args:
            test_id: ID del test
            lead_id: ID del lead
        
        Returns:
            'A' o 'B' según asignación
        """
        if test_id not in self.active_tests:
            # Si no está en memoria, buscar en BD
            if self.db_hook:
                test = self._load_test_from_db(test_id)
                if not test:
                    return 'A'  # Default
            else:
                return 'A'
        
        test = self.active_tests[test_id]
        
        # Usar hash determinístico del lead_id para consistencia
        hash_value = int(hashlib.md5(f"{test_id}{lead_id}".encode()).hexdigest(), 16)
        random.seed(hash_value)
        split = random.random()
        
        variant = 'A' if split < test["traffic_split"] else 'B'
        
        # Registrar asignación
        if self.db_hook:
            try:
                self.db_hook.run(
                    """
                    INSERT INTO ab_test_assignments (
                        test_id,
                        lead_id,
                        variant,
                        assigned_at
                    ) VALUES (%s, %s, %s, NOW())
                    ON CONFLICT (test_id, lead_id) DO NOTHING
                    """,
                    parameters=(test_id, lead_id, variant)
                )
            except Exception as e:
                logger.error(f"Error registrando asignación: {e}")
        
        return variant
    
    def get_variant_content(
        self,
        test_id: str,
        variant: str
    ) -> Dict[str, Any]:
        """
        Obtiene el contenido de una variante.
        
        Args:
            test_id: ID del test
            variant: 'A' o 'B'
        
        Returns:
            Dict con contenido de la variante
        """
        if test_id not in self.active_tests:
            if self.db_hook:
                test = self._load_test_from_db(test_id)
                if test:
                    self.active_tests[test_id] = test
                else:
                    return {}
            else:
                return {}
        
        test = self.active_tests[test_id]
        variant_key = f"variant_{variant.lower()}"
        return test.get(variant_key, {})
    
    def record_engagement(
        self,
        test_id: str,
        lead_id: str,
        engaged: bool
    ) -> None:
        """
        Registra engagement para un test.
        
        Args:
            test_id: ID del test
            lead_id: ID del lead
            engaged: Si el lead se enganchó
        """
        # Obtener variante asignada
        variant = self._get_assigned_variant(test_id, lead_id)
        if not variant:
            return
        
        # Actualizar resultados
        if test_id in self.active_tests:
            test = self.active_tests[test_id]
            variant_key = f"variant_{variant.lower()}"
            if variant_key in test["results"]:
                test["results"][variant_key]["exposed"] += 1
                if engaged:
                    test["results"][variant_key]["engaged"] += 1
        
        # Guardar en BD
        if self.db_hook:
            try:
                self.db_hook.run(
                    """
                    UPDATE ab_test_assignments
                    SET engaged = %s, engaged_at = NOW()
                    WHERE test_id = %s AND lead_id = %s
                    """,
                    parameters=(engaged, test_id, lead_id)
                )
            except Exception as e:
                logger.error(f"Error registrando engagement: {e}")
    
    def get_test_results(
        self,
        test_id: str,
        min_sample_size: int = 100
    ) -> Dict[str, Any]:
        """
        Obtiene resultados de un test A/B.
        
        Args:
            test_id: ID del test
            min_sample_size: Tamaño mínimo de muestra para considerar válido
        
        Returns:
            Dict con resultados y análisis estadístico
        """
        if not self.db_hook:
            return {"error": "No hay conexión a base de datos"}
        
        try:
            # Obtener estadísticas de cada variante
            query = """
                SELECT 
                    variant,
                    COUNT(*) as total,
                    COUNT(CASE WHEN engaged = true THEN 1 END) as engaged,
                    COUNT(CASE WHEN converted = true THEN 1 END) as converted
                FROM ab_test_assignments
                WHERE test_id = %s
                GROUP BY variant
            """
            
            results = self.db_hook.get_records(query, parameters=(test_id,))
            
            variant_stats = {}
            for row in results:
                variant, total, engaged, converted = row
                variant_stats[variant] = {
                    "total": total,
                    "engaged": engaged,
                    "converted": converted,
                    "engagement_rate": (engaged / total * 100) if total > 0 else 0,
                    "conversion_rate": (converted / total * 100) if total > 0 else 0
                }
            
            # Análisis estadístico
            analysis = self._calculate_statistical_significance(variant_stats)
            
            # Determinar ganador
            winner = None
            if analysis["is_significant"]:
                if variant_stats.get("A", {}).get("engagement_rate", 0) > \
                   variant_stats.get("B", {}).get("engagement_rate", 0):
                    winner = "A"
                else:
                    winner = "B"
            
            return {
                "test_id": test_id,
                "variant_stats": variant_stats,
                "analysis": analysis,
                "winner": winner,
                "is_valid": min(variant_stats.get("A", {}).get("total", 0),
                               variant_stats.get("B", {}).get("total", 0)) >= min_sample_size
            }
            
        except Exception as e:
            logger.error(f"Error obteniendo resultados: {e}")
            return {"error": str(e)}
    
    def _calculate_statistical_significance(
        self,
        variant_stats: Dict[str, Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Calcula significancia estadística entre variantes.
        
        Implementación simplificada de test de proporciones.
        """
        variant_a = variant_stats.get("A", {})
        variant_b = variant_stats.get("B", {})
        
        n_a = variant_a.get("total", 0)
        n_b = variant_b.get("total", 0)
        
        if n_a == 0 or n_b == 0:
            return {
                "is_significant": False,
                "confidence": 0.0,
                "p_value": 1.0
            }
        
        p_a = variant_a.get("engagement_rate", 0) / 100
        p_b = variant_b.get("engagement_rate", 0) / 100
        
        # Pooled proportion
        p_pool = (variant_a.get("engaged", 0) + variant_b.get("engaged", 0)) / (n_a + n_b)
        
        # Z-score
        if p_pool == 0 or p_pool == 1:
            z_score = 0
        else:
            se = (p_pool * (1 - p_pool) * (1/n_a + 1/n_b)) ** 0.5
            if se == 0:
                z_score = 0
            else:
                z_score = abs(p_a - p_b) / se
        
        # P-value aproximado (two-tailed)
        # Para 95% confidence, z > 1.96
        is_significant = z_score > 1.96
        confidence = min(95.0, (z_score / 1.96) * 95.0) if z_score > 0 else 0.0
        
        return {
            "is_significant": is_significant,
            "confidence": confidence,
            "z_score": z_score,
            "p_value": max(0.0, 1.0 - (confidence / 100))
        }
    
    def _get_assigned_variant(
        self,
        test_id: str,
        lead_id: str
    ) -> Optional[str]:
        """Obtiene la variante asignada a un lead."""
        if self.db_hook:
            try:
                result = self.db_hook.get_first(
                    "SELECT variant FROM ab_test_assignments WHERE test_id = %s AND lead_id = %s",
                    parameters=(test_id, lead_id)
                )
                return result[0] if result else None
            except:
                return None
        return None
    
    def _load_test_from_db(self, test_id: str) -> Optional[Dict[str, Any]]:
        """Carga un test desde la base de datos."""
        if not self.db_hook:
            return None
        
        try:
            result = self.db_hook.get_first(
                """
                SELECT 
                    test_id, test_name, content_type,
                    variant_a_config, variant_b_config,
                    traffic_split, target_metric, status
                FROM ab_tests
                WHERE test_id = %s AND status = 'active'
                """,
                parameters=(test_id,)
            )
            
            if result:
                return {
                    "test_id": result[0],
                    "test_name": result[1],
                    "content_type": result[2],
                    "variant_a": json.loads(result[3] or "{}"),
                    "variant_b": json.loads(result[4] or "{}"),
                    "traffic_split": float(result[5]),
                    "target_metric": result[6],
                    "status": result[7],
                    "results": {
                        "variant_a": {"exposed": 0, "engaged": 0, "converted": 0},
                        "variant_b": {"exposed": 0, "engaged": 0, "converted": 0}
                    }
                }
        except Exception as e:
            logger.error(f"Error cargando test desde BD: {e}")
        
        return None


# Schema SQL adicional para A/B testing
AB_TESTING_SCHEMA = """
-- Tabla de tests A/B
CREATE TABLE IF NOT EXISTS ab_tests (
    test_id VARCHAR(128) PRIMARY KEY,
    test_name VARCHAR(256) NOT NULL,
    content_type VARCHAR(64) NOT NULL,
    variant_a_config JSONB NOT NULL,
    variant_b_config JSONB NOT NULL,
    traffic_split DECIMAL(3,2) DEFAULT 0.5 CHECK (traffic_split BETWEEN 0 AND 1),
    target_metric VARCHAR(64) DEFAULT 'engagement_rate',
    status VARCHAR(32) DEFAULT 'active' CHECK (status IN ('active', 'paused', 'completed')),
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW()
);

-- Tabla de asignaciones de variantes
CREATE TABLE IF NOT EXISTS ab_test_assignments (
    test_id VARCHAR(128) NOT NULL,
    lead_id VARCHAR(128) NOT NULL,
    variant VARCHAR(1) NOT NULL CHECK (variant IN ('A', 'B')),
    assigned_at TIMESTAMP NOT NULL DEFAULT NOW(),
    engaged BOOLEAN DEFAULT false,
    engaged_at TIMESTAMP,
    converted BOOLEAN DEFAULT false,
    converted_at TIMESTAMP,
    PRIMARY KEY (test_id, lead_id),
    FOREIGN KEY (test_id) REFERENCES ab_tests(test_id) ON DELETE CASCADE,
    FOREIGN KEY (lead_id) REFERENCES organic_leads(lead_id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_ab_test_assignments_test ON ab_test_assignments(test_id);
CREATE INDEX IF NOT EXISTS idx_ab_test_assignments_lead ON ab_test_assignments(lead_id);
CREATE INDEX IF NOT EXISTS idx_ab_tests_status ON ab_tests(status) WHERE status = 'active';
"""

