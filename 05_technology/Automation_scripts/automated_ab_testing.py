#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Sistema de A/B Testing Automatizado para Campañas de Marketing con IA
====================================================================
Sistema avanzado para realizar pruebas A/B automáticas y optimizar campañas.
"""

import json
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Any, Tuple
import random
from scipy import stats
import warnings
warnings.filterwarnings('ignore')

class AutomatedABTesting:
    def __init__(self, campaigns_file='enhanced_1000_ai_marketing_campaigns.json'):
        """Inicializa el sistema de A/B testing automatizado"""
        with open(campaigns_file, 'r', encoding='utf-8') as f:
            self.campaigns = json.load(f)
        
        self.df = pd.DataFrame(self.campaigns)
        
        # Configuración de pruebas A/B
        self.test_config = {
            'min_sample_size': 100,  # Tamaño mínimo de muestra
            'max_test_duration_days': 30,  # Duración máxima de prueba
            'confidence_level': 0.95,  # Nivel de confianza
            'power': 0.8,  # Poder estadístico
            'min_effect_size': 0.1,  # Tamaño mínimo del efecto
            'max_variants': 5,  # Máximo número de variantes
            'auto_stop_threshold': 0.99  # Umbral para parar automáticamente
        }
        
        # Métricas de prueba
        self.test_metrics = {
            'conversion_rate': {'primary': True, 'type': 'ratio'},
            'click_through_rate': {'primary': False, 'type': 'ratio'},
            'cost_per_acquisition': {'primary': False, 'type': 'continuous'},
            'return_on_ad_spend': {'primary': False, 'type': 'continuous'},
            'engagement_rate': {'primary': False, 'type': 'ratio'},
            'bounce_rate': {'primary': False, 'type': 'ratio'}
        }
        
        # Historial de pruebas
        self.test_history = []
        
        # Configurar logging
        import logging
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)
    
    def create_ab_test(self, campaign_id: int, 
                      test_name: str,
                      variants: List[Dict],
                      test_metric: str = 'conversion_rate',
                      traffic_split: List[float] = None,
                      test_duration_days: int = 14) -> Dict[str, Any]:
        """Crea una nueva prueba A/B"""
        
        campaign = next((c for c in self.campaigns if c['id'] == campaign_id), None)
        if not campaign:
            return {"error": f"Campaña {campaign_id} no encontrada"}
        
        # Validar variantes
        if len(variants) < 2:
            return {"error": "Se requieren al menos 2 variantes para A/B testing"}
        
        if len(variants) > self.test_config['max_variants']:
            return {"error": f"Máximo {self.test_config['max_variants']} variantes permitidas"}
        
        # Validar métrica de prueba
        if test_metric not in self.test_metrics:
            return {"error": f"Métrica '{test_metric}' no válida"}
        
        # Configurar división de tráfico
        if traffic_split is None:
            traffic_split = [1.0 / len(variants)] * len(variants)
        
        if abs(sum(traffic_split) - 1.0) > 0.01:
            return {"error": "La división de tráfico debe sumar 1.0"}
        
        # Calcular tamaño de muestra requerido
        required_sample_size = self._calculate_required_sample_size(
            variants, test_metric, test_duration_days
        )
        
        # Crear prueba
        test_id = len(self.test_history) + 1
        test = {
            'test_id': test_id,
            'campaign_id': campaign_id,
            'campaign_name': campaign['name'],
            'test_name': test_name,
            'test_metric': test_metric,
            'variants': variants,
            'traffic_split': traffic_split,
            'required_sample_size': required_sample_size,
            'test_duration_days': test_duration_days,
            'status': 'created',
            'created_at': datetime.now().isoformat(),
            'started_at': None,
            'ended_at': None,
            'results': None,
            'winner': None,
            'confidence': None
        }
        
        # Agregar a historial
        self.test_history.append(test)
        
        return {
            'test_id': test_id,
            'status': 'created',
            'message': 'Prueba A/B creada exitosamente',
            'test_details': test
        }
    
    def _calculate_required_sample_size(self, variants: List[Dict], 
                                      test_metric: str, 
                                      test_duration_days: int) -> int:
        """Calcula el tamaño de muestra requerido para la prueba"""
        # Estimación basada en la métrica
        if self.test_metrics[test_metric]['type'] == 'ratio':
            # Para métricas de ratio (conversión, CTR, etc.)
            base_rate = 0.1  # Tasa base estimada del 10%
            effect_size = self.test_config['min_effect_size']
            
            # Fórmula para tamaño de muestra en pruebas de proporciones
            z_alpha = stats.norm.ppf(1 - (1 - self.test_config['confidence_level']) / 2)
            z_beta = stats.norm.ppf(self.test_config['power'])
            
            p1 = base_rate
            p2 = base_rate * (1 + effect_size)
            p_pool = (p1 + p2) / 2
            
            n = ((z_alpha * np.sqrt(2 * p_pool * (1 - p_pool)) + 
                  z_beta * np.sqrt(p1 * (1 - p1) + p2 * (1 - p2))) ** 2) / ((p1 - p2) ** 2)
            
            return max(int(n), self.test_config['min_sample_size'])
        
        else:
            # Para métricas continuas (CPA, ROAS, etc.)
            # Usar regla empírica: 1000 muestras por variante
            return max(1000, self.test_config['min_sample_size'])
    
    def start_ab_test(self, test_id: int) -> Dict[str, Any]:
        """Inicia una prueba A/B"""
        test = next((t for t in self.test_history if t['test_id'] == test_id), None)
        if not test:
            return {"error": f"Prueba {test_id} no encontrada"}
        
        if test['status'] != 'created':
            return {"error": f"La prueba {test_id} no está en estado 'created'"}
        
        # Actualizar estado
        test['status'] = 'running'
        test['started_at'] = datetime.now().isoformat()
        
        # Simular datos de prueba
        test['results'] = self._simulate_test_data(test)
        
        return {
            'test_id': test_id,
            'status': 'started',
            'message': 'Prueba A/B iniciada exitosamente',
            'started_at': test['started_at']
        }
    
    def _simulate_test_data(self, test: Dict) -> Dict[str, Any]:
        """Simula datos de prueba para demostración"""
        variants = test['variants']
        test_metric = test['test_metric']
        traffic_split = test['traffic_split']
        required_sample_size = test['required_sample_size']
        
        results = {
            'variants': [],
            'overall_stats': {},
            'statistical_tests': {}
        }
        
        # Generar datos para cada variante
        for i, variant in enumerate(variants):
            # Calcular tamaño de muestra para esta variante
            variant_sample_size = int(required_sample_size * traffic_split[i])
            
            # Generar datos simulados basados en la métrica
            if test_metric == 'conversion_rate':
                # Simular tasa de conversión
                base_rate = 0.1 + (i * 0.02)  # Variar ligeramente entre variantes
                conversions = np.random.binomial(variant_sample_size, base_rate)
                conversion_rate = conversions / variant_sample_size
                
                variant_data = {
                    'variant_id': i + 1,
                    'variant_name': variant.get('name', f'Variante {i + 1}'),
                    'sample_size': variant_sample_size,
                    'conversions': conversions,
                    'conversion_rate': conversion_rate,
                    'confidence_interval': self._calculate_confidence_interval(
                        conversion_rate, variant_sample_size
                    )
                }
            
            elif test_metric == 'click_through_rate':
                # Simular CTR
                base_rate = 0.05 + (i * 0.01)
                clicks = np.random.binomial(variant_sample_size, base_rate)
                ctr = clicks / variant_sample_size
                
                variant_data = {
                    'variant_id': i + 1,
                    'variant_name': variant.get('name', f'Variante {i + 1}'),
                    'sample_size': variant_sample_size,
                    'clicks': clicks,
                    'click_through_rate': ctr,
                    'confidence_interval': self._calculate_confidence_interval(
                        ctr, variant_sample_size
                    )
                }
            
            elif test_metric == 'cost_per_acquisition':
                # Simular CPA
                base_cpa = 50 + (i * 10)
                cpa_values = np.random.normal(base_cpa, base_cpa * 0.2, variant_sample_size)
                
                variant_data = {
                    'variant_id': i + 1,
                    'variant_name': variant.get('name', f'Variante {i + 1}'),
                    'sample_size': variant_sample_size,
                    'mean_cpa': np.mean(cpa_values),
                    'std_cpa': np.std(cpa_values),
                    'confidence_interval': self._calculate_confidence_interval(
                        np.mean(cpa_values), variant_sample_size, is_continuous=True
                    )
                }
            
            else:
                # Métrica genérica
                base_value = 1.0 + (i * 0.1)
                values = np.random.normal(base_value, base_value * 0.1, variant_sample_size)
                
                variant_data = {
                    'variant_id': i + 1,
                    'variant_name': variant.get('name', f'Variante {i + 1}'),
                    'sample_size': variant_sample_size,
                    'mean_value': np.mean(values),
                    'std_value': np.std(values),
                    'confidence_interval': self._calculate_confidence_interval(
                        np.mean(values), variant_sample_size, is_continuous=True
                    )
                }
            
            results['variants'].append(variant_data)
        
        # Calcular estadísticas generales
        results['overall_stats'] = self._calculate_overall_stats(results['variants'], test_metric)
        
        # Realizar pruebas estadísticas
        results['statistical_tests'] = self._perform_statistical_tests(results['variants'], test_metric)
        
        return results
    
    def _calculate_confidence_interval(self, mean: float, sample_size: int, 
                                     is_continuous: bool = False) -> Tuple[float, float]:
        """Calcula el intervalo de confianza"""
        confidence_level = self.test_config['confidence_level']
        alpha = 1 - confidence_level
        
        if is_continuous:
            # Para variables continuas (usar t-distribution)
            df = sample_size - 1
            t_critical = stats.t.ppf(1 - alpha/2, df)
            margin_error = t_critical * (1 / np.sqrt(sample_size))  # Asumiendo std = 1
        else:
            # Para proporciones (usar normal distribution)
            z_critical = stats.norm.ppf(1 - alpha/2)
            margin_error = z_critical * np.sqrt((mean * (1 - mean)) / sample_size)
        
        return (mean - margin_error, mean + margin_error)
    
    def _calculate_overall_stats(self, variants: List[Dict], test_metric: str) -> Dict[str, Any]:
        """Calcula estadísticas generales de la prueba"""
        total_sample_size = sum(v['sample_size'] for v in variants)
        
        if test_metric == 'conversion_rate':
            total_conversions = sum(v['conversions'] for v in variants)
            overall_conversion_rate = total_conversions / total_sample_size
            
            return {
                'total_sample_size': total_sample_size,
                'total_conversions': total_conversions,
                'overall_conversion_rate': overall_conversion_rate
            }
        
        elif test_metric == 'click_through_rate':
            total_clicks = sum(v['clicks'] for v in variants)
            overall_ctr = total_clicks / total_sample_size
            
            return {
                'total_sample_size': total_sample_size,
                'total_clicks': total_clicks,
                'overall_ctr': overall_ctr
            }
        
        else:
            # Para métricas continuas
            weighted_mean = sum(v['mean_value'] * v['sample_size'] for v in variants) / total_sample_size
            
            return {
                'total_sample_size': total_sample_size,
                'weighted_mean': weighted_mean
            }
    
    def _perform_statistical_tests(self, variants: List[Dict], test_metric: str) -> Dict[str, Any]:
        """Realiza pruebas estadísticas para determinar significancia"""
        if len(variants) < 2:
            return {"error": "Se requieren al menos 2 variantes para pruebas estadísticas"}
        
        # Prueba de chi-cuadrado para proporciones
        if test_metric in ['conversion_rate', 'click_through_rate']:
            if test_metric == 'conversion_rate':
                successes = [v['conversions'] for v in variants]
                sample_sizes = [v['sample_size'] for v in variants]
            else:
                successes = [v['clicks'] for v in variants]
                sample_sizes = [v['sample_size'] for v in variants]
            
            # Crear tabla de contingencia
            failures = [sample_sizes[i] - successes[i] for i in range(len(variants))]
            
            # Prueba de chi-cuadrado
            chi2, p_value, dof, expected = stats.chi2_contingency([
                successes, failures
            ])
            
            return {
                'test_type': 'chi_square',
                'chi2_statistic': chi2,
                'p_value': p_value,
                'degrees_of_freedom': dof,
                'is_significant': p_value < (1 - self.test_config['confidence_level']),
                'expected_frequencies': expected.tolist()
            }
        
        else:
            # Prueba ANOVA para variables continuas
            if test_metric == 'cost_per_acquisition':
                values = []
                groups = []
                for i, variant in enumerate(variants):
                    # Simular valores basados en la media y std
                    variant_values = np.random.normal(
                        variant['mean_cpa'], 
                        variant['std_cpa'], 
                        variant['sample_size']
                    )
                    values.extend(variant_values)
                    groups.extend([i] * variant['sample_size'])
                
                # Prueba ANOVA
                f_statistic, p_value = stats.f_oneway(*[
                    [values[i] for i in range(len(values)) if groups[i] == j]
                    for j in range(len(variants))
                ])
                
                return {
                    'test_type': 'anova',
                    'f_statistic': f_statistic,
                    'p_value': p_value,
                    'is_significant': p_value < (1 - self.test_config['confidence_level'])
                }
        
        return {"error": "Tipo de prueba no implementado"}
    
    def analyze_ab_test(self, test_id: int) -> Dict[str, Any]:
        """Analiza los resultados de una prueba A/B"""
        test = next((t for t in self.test_history if t['test_id'] == test_id), None)
        if not test:
            return {"error": f"Prueba {test_id} no encontrada"}
        
        if test['status'] != 'running':
            return {"error": f"La prueba {test_id} no está en ejecución"}
        
        if not test['results']:
            return {"error": f"No hay resultados disponibles para la prueba {test_id}"}
        
        results = test['results']
        test_metric = test['test_metric']
        
        # Determinar ganador
        winner = self._determine_winner(results['variants'], test_metric)
        
        # Calcular confianza
        confidence = self._calculate_test_confidence(results['statistical_tests'])
        
        # Generar recomendaciones
        recommendations = self._generate_test_recommendations(
            test, results, winner, confidence
        )
        
        # Actualizar prueba
        test['winner'] = winner
        test['confidence'] = confidence
        
        return {
            'test_id': test_id,
            'test_name': test['test_name'],
            'campaign_name': test['campaign_name'],
            'test_metric': test_metric,
            'winner': winner,
            'confidence': confidence,
            'results': results,
            'recommendations': recommendations,
            'analysis_timestamp': datetime.now().isoformat()
        }
    
    def _determine_winner(self, variants: List[Dict], test_metric: str) -> Dict[str, Any]:
        """Determina el ganador de la prueba A/B"""
        if not variants:
            return {"error": "No hay variantes para analizar"}
        
        # Determinar métrica de comparación
        if test_metric == 'conversion_rate':
            metric_key = 'conversion_rate'
            higher_is_better = True
        elif test_metric == 'click_through_rate':
            metric_key = 'click_through_rate'
            higher_is_better = True
        elif test_metric == 'cost_per_acquisition':
            metric_key = 'mean_cpa'
            higher_is_better = False
        else:
            metric_key = 'mean_value'
            higher_is_better = True
        
        # Encontrar mejor variante
        if higher_is_better:
            best_variant = max(variants, key=lambda x: x[metric_key])
        else:
            best_variant = min(variants, key=lambda x: x[metric_key])
        
        # Calcular mejora sobre la variante de control
        control_variant = variants[0]  # Asumir que la primera es el control
        if control_variant[metric_key] > 0:
            improvement = ((best_variant[metric_key] - control_variant[metric_key]) / 
                          control_variant[metric_key]) * 100
        else:
            improvement = 0
        
        return {
            'variant_id': best_variant['variant_id'],
            'variant_name': best_variant['variant_name'],
            'metric_value': best_variant[metric_key],
            'improvement_percent': improvement,
            'is_significant': True  # Se determinará en el análisis estadístico
        }
    
    def _calculate_test_confidence(self, statistical_tests: Dict) -> float:
        """Calcula la confianza de la prueba"""
        if 'p_value' in statistical_tests:
            p_value = statistical_tests['p_value']
            # Convertir p-value a confianza
            confidence = (1 - p_value) * 100
            return min(99.9, max(0.1, confidence))
        
        return 50.0  # Confianza por defecto si no hay datos
    
    def _generate_test_recommendations(self, test: Dict, results: Dict, 
                                     winner: Dict, confidence: float) -> List[str]:
        """Genera recomendaciones basadas en los resultados de la prueba"""
        recommendations = []
        
        # Recomendaciones basadas en confianza
        if confidence >= 95:
            recommendations.append("🎯 **Alta confianza**: Los resultados son estadísticamente significativos")
        elif confidence >= 80:
            recommendations.append("⚠️ **Confianza moderada**: Considerar extender la prueba para mayor certeza")
        else:
            recommendations.append("❌ **Baja confianza**: Los resultados no son estadísticamente significativos")
        
        # Recomendaciones basadas en el ganador
        if winner and winner['improvement_percent'] > 0:
            recommendations.append(f"🏆 **Ganador identificado**: {winner['variant_name']} con {winner['improvement_percent']:.1f}% de mejora")
            
            if winner['improvement_percent'] > 20:
                recommendations.append("📈 **Mejora significativa**: Implementar inmediatamente la variante ganadora")
            elif winner['improvement_percent'] > 10:
                recommendations.append("👍 **Mejora moderada**: Implementar la variante ganadora con monitoreo")
            else:
                recommendations.append("📊 **Mejora menor**: Considerar si la mejora justifica el cambio")
        else:
            recommendations.append("🤔 **Sin ganador claro**: Considerar ajustar la prueba o probar nuevas variantes")
        
        # Recomendaciones basadas en el tamaño de muestra
        total_sample_size = results['overall_stats']['total_sample_size']
        if total_sample_size < test['required_sample_size']:
            recommendations.append("📊 **Muestra insuficiente**: Extender la prueba para alcanzar el tamaño de muestra requerido")
        
        # Recomendaciones específicas por métrica
        test_metric = test['test_metric']
        if test_metric == 'conversion_rate' and confidence >= 80:
            recommendations.append("🔄 **Optimizar conversiones**: Implementar elementos de la variante ganadora en otras campañas")
        elif test_metric == 'click_through_rate' and confidence >= 80:
            recommendations.append("👆 **Mejorar CTR**: Aplicar elementos de la variante ganadora a otros creativos")
        elif test_metric == 'cost_per_acquisition' and confidence >= 80:
            recommendations.append("💰 **Reducir CPA**: Implementar la estrategia de la variante ganadora")
        
        return recommendations
    
    def stop_ab_test(self, test_id: int, reason: str = "manual_stop") -> Dict[str, Any]:
        """Detiene una prueba A/B"""
        test = next((t for t in self.test_history if t['test_id'] == test_id), None)
        if not test:
            return {"error": f"Prueba {test_id} no encontrada"}
        
        if test['status'] != 'running':
            return {"error": f"La prueba {test_id} no está en ejecución"}
        
        # Actualizar estado
        test['status'] = 'stopped'
        test['ended_at'] = datetime.now().isoformat()
        test['stop_reason'] = reason
        
        # Realizar análisis final
        final_analysis = self.analyze_ab_test(test_id)
        
        return {
            'test_id': test_id,
            'status': 'stopped',
            'reason': reason,
            'stopped_at': test['ended_at'],
            'final_analysis': final_analysis
        }
    
    def get_test_status(self, test_id: int) -> Dict[str, Any]:
        """Obtiene el estado actual de una prueba A/B"""
        test = next((t for t in self.test_history if t['test_id'] == test_id), None)
        if not test:
            return {"error": f"Prueba {test_id} no encontrada"}
        
        return {
            'test_id': test_id,
            'test_name': test['test_name'],
            'campaign_name': test['campaign_name'],
            'status': test['status'],
            'created_at': test['created_at'],
            'started_at': test['started_at'],
            'ended_at': test['ended_at'],
            'test_metric': test['test_metric'],
            'variants_count': len(test['variants']),
            'winner': test.get('winner'),
            'confidence': test.get('confidence')
        }
    
    def get_all_tests(self) -> List[Dict[str, Any]]:
        """Obtiene todas las pruebas A/B"""
        return [
            {
                'test_id': test['test_id'],
                'test_name': test['test_name'],
                'campaign_name': test['campaign_name'],
                'status': test['status'],
                'created_at': test['created_at'],
                'test_metric': test['test_metric'],
                'variants_count': len(test['variants']),
                'winner': test.get('winner'),
                'confidence': test.get('confidence')
            }
            for test in self.test_history
        ]

def main():
    """Función principal de demostración"""
    print("=== SISTEMA DE A/B TESTING AUTOMATIZADO ===")
    
    # Inicializar sistema de A/B testing
    ab_testing = AutomatedABTesting()
    
    # Crear prueba A/B
    print("Creando prueba A/B...")
    variants = [
        {'name': 'Control', 'description': 'Versión original'},
        {'name': 'Variante A', 'description': 'Nuevo diseño de botón'},
        {'name': 'Variante B', 'description': 'Nuevo copy de texto'}
    ]
    
    test_creation = ab_testing.create_ab_test(
        campaign_id=1,
        test_name="Prueba de Conversión - Botón vs Copy",
        variants=variants,
        test_metric='conversion_rate',
        test_duration_days=14
    )
    
    if 'error' not in test_creation:
        test_id = test_creation['test_id']
        print(f"✅ Prueba creada: ID {test_id}")
        
        # Iniciar prueba
        print("Iniciando prueba...")
        start_result = ab_testing.start_ab_test(test_id)
        
        if 'error' not in start_result:
            print("✅ Prueba iniciada")
            
            # Analizar resultados
            print("Analizando resultados...")
            analysis = ab_testing.analyze_ab_test(test_id)
            
            if 'error' not in analysis:
                print(f"\n📊 RESULTADOS DE LA PRUEBA")
                print(f"Prueba: {analysis['test_name']}")
                print(f"Métrica: {analysis['test_metric']}")
                print(f"Ganador: {analysis['winner']['variant_name']}")
                print(f"Mejora: {analysis['winner']['improvement_percent']:.1f}%")
                print(f"Confianza: {analysis['confidence']:.1f}%")
                
                print(f"\n💡 RECOMENDACIONES")
                for recommendation in analysis['recommendations']:
                    print(f"• {recommendation}")
                
                # Detener prueba
                print(f"\nDeteniendo prueba...")
                stop_result = ab_testing.stop_ab_test(test_id, "análisis_completo")
                print("✅ Prueba detenida")
    
    # Mostrar todas las pruebas
    print(f"\n📋 TODAS LAS PRUEBAS")
    all_tests = ab_testing.get_all_tests()
    for test in all_tests:
        print(f"• {test['test_name']} (ID: {test['test_id']}) - {test['status']}")
    
    print(f"\n✅ Sistema de A/B testing configurado y funcionando")

if __name__ == "__main__":
    main()
