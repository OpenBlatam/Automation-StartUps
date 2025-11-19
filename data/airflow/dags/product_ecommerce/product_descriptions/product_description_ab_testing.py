"""
Sistema de pruebas A/B automatizado para descripciones de productos.

Incluye:
- Configuración de tests A/B
- Distribución automática de tráfico
- Análisis estadístico de resultados
- Recomendaciones de ganadores
- Detección de significancia estadística
"""

import logging
from typing import Dict, List, Optional
from datetime import datetime, timedelta
from collections import defaultdict
import math

logger = logging.getLogger(__name__)


class ABTestManager:
    """Gestor de pruebas A/B para descripciones."""
    
    def __init__(self):
        self.active_tests = {}
        self.test_results = defaultdict(list)
    
    def create_test(
        self,
        test_name: str,
        description_id: str,
        variations: List[Dict],
        traffic_split: Dict[str, float] = None,
        duration_days: int = 14,
        min_sample_size: int = 100
    ) -> Dict:
        """
        Crea una nueva prueba A/B.
        
        Args:
            test_name: Nombre del test
            description_id: ID de la descripción base
            variations: Lista de variaciones a probar
            traffic_split: Distribución de tráfico (ej: {'A': 0.5, 'B': 0.5})
            duration_days: Duración del test en días
            min_sample_size: Tamaño mínimo de muestra por variación
        
        Returns:
            Dict con información del test creado
        """
        if not variations or len(variations) < 2:
            raise ValueError("Se requieren al menos 2 variaciones")
        
        # Validar que traffic_split suma 1.0
        if traffic_split:
            total = sum(traffic_split.values())
            if abs(total - 1.0) > 0.01:
                raise ValueError("traffic_split debe sumar 1.0")
        else:
            # Distribución equitativa por defecto
            split = 1.0 / len(variations)
            traffic_split = {f'variation_{i}': split for i in range(len(variations))}
        
        test_id = f"ab_test_{description_id}_{int(datetime.now().timestamp())}"
        
        test_config = {
            'test_id': test_id,
            'test_name': test_name,
            'description_id': description_id,
            'variations': variations,
            'traffic_split': traffic_split,
            'start_date': datetime.now().isoformat(),
            'end_date': (datetime.now() + timedelta(days=duration_days)).isoformat(),
            'min_sample_size': min_sample_size,
            'status': 'active',
            'created_at': datetime.now().isoformat()
        }
        
        self.active_tests[test_id] = test_config
        
        logger.info(f"Test A/B creado: {test_id}")
        return test_config
    
    def record_conversion(self, test_id: str, variation_id: str, converted: bool, metadata: Dict = None):
        """
        Registra una conversión para un test A/B.
        
        Args:
            test_id: ID del test
            variation_id: ID de la variación
            converted: Si hubo conversión
            metadata: Metadata adicional
        """
        if test_id not in self.active_tests:
            logger.warning(f"Test {test_id} no encontrado")
            return
        
        self.test_results[test_id].append({
            'variation_id': variation_id,
            'converted': converted,
            'timestamp': datetime.now().isoformat(),
            'metadata': metadata or {}
        })
    
    def get_test_results(self, test_id: str) -> Dict:
        """
        Obtiene resultados de un test A/B.
        
        Args:
            test_id: ID del test
        
        Returns:
            Dict con resultados y análisis
        """
        if test_id not in self.active_tests:
            return {'error': 'Test no encontrado'}
        
        test_config = self.active_tests[test_id]
        results = self.test_results.get(test_id, [])
        
        # Agrupar por variación
        variation_stats = defaultdict(lambda: {'views': 0, 'conversions': 0})
        
        for result in results:
            var_id = result['variation_id']
            variation_stats[var_id]['views'] += 1
            if result['converted']:
                variation_stats[var_id]['conversions'] += 1
        
        # Calcular métricas
        analysis = {}
        for var_id, stats in variation_stats.items():
            conversion_rate = (stats['conversions'] / stats['views'] * 100) if stats['views'] > 0 else 0
            analysis[var_id] = {
                **stats,
                'conversion_rate': round(conversion_rate, 2),
                'sample_size': stats['views']
            }
        
        # Determinar ganador
        winner = self._determine_winner(analysis, test_config)
        
        # Verificar significancia estadística
        significance = self._calculate_significance(analysis, test_config)
        
        # Verificar si el test está completo
        is_complete = self._is_test_complete(test_config, analysis)
        
        return {
            'test_id': test_id,
            'test_name': test_config['test_name'],
            'status': 'complete' if is_complete else 'active',
            'variation_results': analysis,
            'winner': winner,
            'statistical_significance': significance,
            'recommendations': self._generate_recommendations(analysis, winner, significance),
            'total_samples': sum(s['views'] for s in analysis.values())
        }
    
    def _determine_winner(self, analysis: Dict, test_config: Dict) -> Optional[str]:
        """Determina la variación ganadora."""
        if not analysis:
            return None
        
        # Encontrar variación con mayor conversión
        winner = max(analysis.items(), key=lambda x: x[1]['conversion_rate'])
        
        # Verificar que tenga muestra suficiente
        if winner[1]['sample_size'] >= test_config['min_sample_size']:
            return winner[0]
        
        return None
    
    def _calculate_significance(self, analysis: Dict, test_config: Dict) -> Dict:
        """
        Calcula significancia estadística usando test de chi-cuadrado.
        
        Args:
            analysis: Análisis de variaciones
            test_config: Configuración del test
        
        Returns:
            Dict con resultados de significancia
        """
        if len(analysis) < 2:
            return {
                'is_significant': False,
                'p_value': 1.0,
                'confidence_level': 0
            }
        
        # Obtener dos primeras variaciones para comparar
        variations = list(analysis.items())[:2]
        var1_id, var1_stats = variations[0]
        var2_id, var2_stats = variations[1]
        
        # Test de chi-cuadrado simplificado
        n1 = var1_stats['views']
        c1 = var1_stats['conversions']
        n2 = var2_stats['views']
        c2 = var2_stats['conversions']
        
        if n1 == 0 or n2 == 0:
            return {
                'is_significant': False,
                'p_value': 1.0,
                'confidence_level': 0
            }
        
        p1 = c1 / n1
        p2 = c2 / n2
        
        # Pooled proportion
        p_pool = (c1 + c2) / (n1 + n2)
        
        # Standard error
        se = math.sqrt(p_pool * (1 - p_pool) * (1/n1 + 1/n2))
        
        if se == 0:
            return {
                'is_significant': False,
                'p_value': 1.0,
                'confidence_level': 0
            }
        
        # Z-score
        z_score = abs(p1 - p2) / se
        
        # P-value aproximado (two-tailed)
        # Simplificado: z > 1.96 = 95% confianza, z > 2.58 = 99% confianza
        if z_score >= 2.58:
            p_value = 0.01
            confidence = 99
        elif z_score >= 1.96:
            p_value = 0.05
            confidence = 95
        elif z_score >= 1.65:
            p_value = 0.10
            confidence = 90
        else:
            p_value = 0.50
            confidence = 50
        
        return {
            'is_significant': confidence >= 95,
            'p_value': round(p_value, 3),
            'confidence_level': confidence,
            'z_score': round(z_score, 2)
        }
    
    def _is_test_complete(self, test_config: Dict, analysis: Dict) -> bool:
        """Verifica si el test está completo."""
        # Verificar fecha de fin
        end_date = datetime.fromisoformat(test_config['end_date'])
        if datetime.now() >= end_date:
            return True
        
        # Verificar tamaño de muestra mínimo
        min_size = test_config['min_sample_size']
        for stats in analysis.values():
            if stats['sample_size'] < min_size:
                return False
        
        return True
    
    def _generate_recommendations(self, analysis: Dict, winner: Optional[str], significance: Dict) -> List[str]:
        """Genera recomendaciones basadas en resultados."""
        recommendations = []
        
        if not winner:
            recommendations.append("El test necesita más datos para determinar un ganador")
            return recommendations
        
        if significance['is_significant']:
            recommendations.append(f"Variación {winner} es el ganador con {significance['confidence_level']}% de confianza")
            recommendations.append(f"Implementa la variación {winner} en producción")
        else:
            recommendations.append(f"Variación {winner} tiene mejor rendimiento pero no es estadísticamente significativo")
            recommendations.append("Considera extender el test o aumentar el tamaño de muestra")
        
        # Recomendaciones adicionales
        if len(analysis) > 2:
            recommendations.append("Considera hacer tests binarios (A vs B) para mayor claridad")
        
        return recommendations
    
    def stop_test(self, test_id: str, reason: str = None) -> Dict:
        """
        Detiene un test A/B.
        
        Args:
            test_id: ID del test
            reason: Razón para detener
        
        Returns:
            Resultados finales del test
        """
        if test_id not in self.active_tests:
            return {'error': 'Test no encontrado'}
        
        self.active_tests[test_id]['status'] = 'stopped'
        self.active_tests[test_id]['stopped_at'] = datetime.now().isoformat()
        self.active_tests[test_id]['stop_reason'] = reason
        
        return self.get_test_results(test_id)






