#!/usr/bin/env python3
"""
Advanced Testing Framework
Framework completo para testing A/B/C/D y multivariado
"""

import json
import requests
import statistics
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from enum import Enum


class TestType(Enum):
    """Tipos de tests disponibles"""
    AB = "ab"
    ABC = "abc"
    MULTIVARIATE = "multivariate"
    SEQUENTIAL = "sequential"


@dataclass
class TestVariant:
    """Variante de test"""
    id: str
    name: str
    config: Dict[str, Any]
    traffic_percentage: float
    conversions: int = 0
    visitors: int = 0
    revenue: float = 0.0


@dataclass
class TestResult:
    """Resultado de un test"""
    variant_id: str
    conversion_rate: float
    revenue_per_visitor: float
    statistical_significance: float
    confidence_level: float
    is_winner: bool = False


class AdvancedTestingFramework:
    """
    Framework avanzado para testing A/B/C/D y multivariado
    """
    
    def __init__(self, api_base_url: str, api_key: str):
        self.api_base_url = api_base_url
        self.api_key = api_key
        self.headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
    
    def create_test(
        self,
        test_name: str,
        test_type: TestType,
        variants: List[TestVariant],
        target_metric: str = "conversion_rate",
        significance_level: float = 0.95,
        min_sample_size: int = 1000
    ) -> Dict[str, Any]:
        """
        Crea un nuevo test
        
        Args:
            test_name: Nombre del test
            test_type: Tipo de test (AB, ABC, Multivariate, Sequential)
            variants: Lista de variantes
            target_metric: Métrica objetivo (conversion_rate, revenue, engagement)
            significance_level: Nivel de significancia (0.95 = 95%)
            min_sample_size: Tamaño mínimo de muestra
        
        Returns:
            Dict con información del test creado
        """
        # Validar que el tráfico suma 100%
        total_traffic = sum(v.traffic_percentage for v in variants)
        if abs(total_traffic - 100.0) > 0.01:
            raise ValueError(f"Traffic percentages must sum to 100%, got {total_traffic}%")
        
        test_config = {
            "name": test_name,
            "type": test_type.value,
            "variants": [
                {
                    "id": v.id,
                    "name": v.name,
                    "config": v.config,
                    "traffic_percentage": v.traffic_percentage
                }
                for v in variants
            ],
            "target_metric": target_metric,
            "significance_level": significance_level,
            "min_sample_size": min_sample_size,
            "status": "active",
            "created_at": datetime.now().isoformat()
        }
        
        # En producción, guardar en DB
        # response = requests.post(
        #     f"{self.api_base_url}/tests",
        #     json=test_config,
        #     headers=self.headers
        # )
        # response.raise_for_status()
        
        return {
            "test_id": f"test_{datetime.now().timestamp()}",
            "config": test_config
        }
    
    def assign_variant(
        self,
        test_id: str,
        visitor_id: str,
        visitor_attributes: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Asigna una variante a un visitante
        
        Args:
            test_id: ID del test
            visitor_id: ID del visitante
            visitor_attributes: Atributos del visitante (para segmentación)
        
        Returns:
            ID de la variante asignada
        """
        # Obtener configuración del test
        test_config = self.get_test_config(test_id)
        
        # Determinar variante basado en tráfico
        import random
        random.seed(hash(f"{test_id}_{visitor_id}"))
        roll = random.random() * 100
        
        cumulative = 0
        for variant in test_config["variants"]:
            cumulative += variant["traffic_percentage"]
            if roll <= cumulative:
                return variant["id"]
        
        # Fallback a primera variante
        return test_config["variants"][0]["id"]
    
    def track_conversion(
        self,
        test_id: str,
        visitor_id: str,
        variant_id: str,
        value: float = 1.0,
        metadata: Optional[Dict[str, Any]] = None
    ) -> bool:
        """
        Registra una conversión
        
        Args:
            test_id: ID del test
            visitor_id: ID del visitante
            variant_id: ID de la variante
            value: Valor de la conversión (para revenue)
            metadata: Metadatos adicionales
        
        Returns:
            True si se registró correctamente
        """
        conversion = {
            "test_id": test_id,
            "visitor_id": visitor_id,
            "variant_id": variant_id,
            "value": value,
            "metadata": metadata or {},
            "timestamp": datetime.now().isoformat()
        }
        
        # En producción, guardar en DB
        # response = requests.post(
        #     f"{self.api_base_url}/tests/{test_id}/conversions",
        #     json=conversion,
        #     headers=self.headers
        # )
        # response.raise_for_status()
        
        return True
    
    def get_test_results(
        self,
        test_id: str,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> Dict[str, Any]:
        """
        Obtiene resultados de un test
        
        Args:
            test_id: ID del test
            start_date: Fecha de inicio (opcional)
            end_date: Fecha de fin (opcional)
        
        Returns:
            Dict con resultados del test
        """
        # Obtener configuración
        test_config = self.get_test_config(test_id)
        
        # Obtener datos (simulado - en producción vendría de DB)
        results = self._simulate_test_results(test_config)
        
        # Calcular estadísticas
        analyzed_results = []
        for variant_data in results:
            analyzed = self._analyze_variant(variant_data, test_config)
            analyzed_results.append(analyzed)
        
        # Determinar ganador
        winner = self._determine_winner(analyzed_results, test_config)
        
        return {
            "test_id": test_id,
            "test_name": test_config["name"],
            "status": "active",
            "results": analyzed_results,
            "winner": winner,
            "recommendation": self._generate_recommendation(analyzed_results, winner, test_config),
            "period": {
                "start": start_date.isoformat() if start_date else None,
                "end": end_date.isoformat() if end_date else None
            }
        }
    
    def _simulate_test_results(self, test_config: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Simula resultados de test (para demo)"""
        results = []
        for variant in test_config["variants"]:
            visitors = 1000
            conversion_rate = 0.15 + (hash(variant["id"]) % 10) / 100  # 15-25%
            conversions = int(visitors * conversion_rate)
            revenue = conversions * 50.0  # $50 promedio
            
            results.append({
                "variant_id": variant["id"],
                "visitors": visitors,
                "conversions": conversions,
                "revenue": revenue
            })
        return results
    
    def _analyze_variant(
        self,
        variant_data: Dict[str, Any],
        test_config: Dict[str, Any]
    ) -> TestResult:
        """Analiza una variante y calcula estadísticas"""
        visitors = variant_data["visitors"]
        conversions = variant_data["conversions"]
        revenue = variant_data["revenue"]
        
        conversion_rate = (conversions / visitors) if visitors > 0 else 0.0
        revenue_per_visitor = (revenue / visitors) if visitors > 0 else 0.0
        
        # Calcular significancia estadística (simplificado)
        # En producción usaría test estadístico apropiado (t-test, chi-square, etc.)
        statistical_significance = self._calculate_significance(
            conversions,
            visitors,
            test_config.get("significance_level", 0.95)
        )
        
        confidence_level = statistical_significance * 100
        
        return TestResult(
            variant_id=variant_data["variant_id"],
            conversion_rate=conversion_rate,
            revenue_per_visitor=revenue_per_visitor,
            statistical_significance=statistical_significance,
            confidence_level=confidence_level
        )
    
    def _calculate_significance(
        self,
        conversions: int,
        visitors: int,
        significance_level: float
    ) -> float:
        """Calcula significancia estadística (simplificado)"""
        if visitors < 100:
            return 0.0
        
        # Aproximación simplificada
        # En producción usar biblioteca estadística apropiada
        base_rate = 0.15  # Tasa base esperada
        observed_rate = conversions / visitors
        
        # Z-score simplificado
        z_score = abs(observed_rate - base_rate) / (base_rate * (1 - base_rate) / visitors) ** 0.5
        
        # Convertir a p-value aproximado
        p_value = 1 - (z_score / 3)  # Aproximación muy simplificada
        
        return max(0.0, min(1.0, p_value))
    
    def _determine_winner(
        self,
        results: List[TestResult],
        test_config: Dict[str, Any]
    ) -> Optional[str]:
        """Determina el ganador del test"""
        target_metric = test_config.get("target_metric", "conversion_rate")
        significance_level = test_config.get("significance_level", 0.95)
        
        # Filtrar variantes con significancia suficiente
        significant_results = [
            r for r in results
            if r.statistical_significance >= significance_level
        ]
        
        if not significant_results:
            return None
        
        # Ordenar por métrica objetivo
        if target_metric == "conversion_rate":
            significant_results.sort(key=lambda x: x.conversion_rate, reverse=True)
        elif target_metric == "revenue":
            significant_results.sort(key=lambda x: x.revenue_per_visitor, reverse=True)
        
        winner = significant_results[0]
        winner.is_winner = True
        
        return winner.variant_id
    
    def _generate_recommendation(
        self,
        results: List[TestResult],
        winner: Optional[str],
        test_config: Dict[str, Any]
    ) -> str:
        """Genera recomendación basada en resultados"""
        if not winner:
            return "Test aún no tiene significancia estadística. Continuar recopilando datos."
        
        winner_result = next(r for r in results if r.variant_id == winner)
        
        if winner_result.confidence_level >= 95:
            return f"Variante '{winner}' es claramente superior ({winner_result.conversion_rate*100:.2f}% conversión). Implementar inmediatamente."
        elif winner_result.confidence_level >= 80:
            return f"Variante '{winner}' muestra mejor performance ({winner_result.conversion_rate*100:.2f}% conversión). Considerar implementar."
        else:
            return f"Variante '{winner}' tiene ligera ventaja. Continuar test para mayor confianza."
    
    def get_test_config(self, test_id: str) -> Dict[str, Any]:
        """Obtiene configuración de un test (simulado)"""
        # En producción, obtener de DB
        return {
            "name": "Sample Test",
            "type": "ab",
            "variants": [
                {"id": "control", "name": "Control", "traffic_percentage": 50.0},
                {"id": "variant_a", "name": "Variant A", "traffic_percentage": 50.0}
            ],
            "target_metric": "conversion_rate",
            "significance_level": 0.95
        }


def main():
    """Ejemplo de uso"""
    framework = AdvancedTestingFramework(
        api_base_url="https://api.example.com",
        api_key="your_api_key"
    )
    
    # Crear test A/B
    variants = [
        TestVariant(
            id="control",
            name="Control",
            config={"headline": "Original Headline"},
            traffic_percentage=50.0
        ),
        TestVariant(
            id="variant_a",
            name="Variant A",
            config={"headline": "New Headline"},
            traffic_percentage=50.0
        )
    ]
    
    test = framework.create_test(
        test_name="Homepage Headline Test",
        test_type=TestType.AB,
        variants=variants,
        target_metric="conversion_rate"
    )
    
    print(f"Test creado: {test['test_id']}")
    
    # Asignar variante
    variant = framework.assign_variant(test["test_id"], "visitor_123")
    print(f"Variante asignada: {variant}")
    
    # Obtener resultados
    results = framework.get_test_results(test["test_id"])
    print(f"\nResultados:")
    print(json.dumps(results, indent=2, default=str))


if __name__ == "__main__":
    main()










