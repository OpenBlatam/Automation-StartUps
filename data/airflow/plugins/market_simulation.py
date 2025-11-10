"""
Sistema de Simulación de Mercado

Simula diferentes escenarios de mercado:
- Simulación Monte Carlo
- Escenarios de "what-if"
- Análisis de sensibilidad avanzado
- Optimización de estrategias
"""

from __future__ import annotations

import logging
from datetime import datetime
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
import random

logger = logging.getLogger(__name__)


@dataclass
class MarketSimulation:
    """Simulación de mercado."""
    simulation_id: str
    scenario_name: str
    simulation_type: str  # 'monte_carlo', 'what_if', 'optimization'
    iterations: int
    results: Dict[str, Any]
    confidence_intervals: Dict[str, List[float]]  # {metric: [lower, upper]}
    key_insights: List[str]


class MarketSimulator:
    """Simulador de mercado."""
    
    def __init__(self):
        """Inicializa el simulador."""
        self.logger = logging.getLogger(__name__)
    
    def run_monte_carlo_simulation(
        self,
        base_metrics: Dict[str, float],
        volatility: Dict[str, float],
        iterations: int = 1000,
        time_horizon_months: int = 6
    ) -> MarketSimulation:
        """
        Ejecuta simulación Monte Carlo.
        
        Args:
            base_metrics: Métricas base {metric_name: value}
            volatility: Volatilidad por métrica {metric_name: std_dev}
            iterations: Número de iteraciones
            time_horizon_months: Horizonte temporal
            
        Returns:
            Resultado de simulación
        """
        logger.info(f"Running Monte Carlo simulation with {iterations} iterations")
        
        # Simular múltiples escenarios
        all_results = {metric: [] for metric in base_metrics.keys()}
        
        for i in range(iterations):
            scenario_results = {}
            for metric, base_value in base_metrics.items():
                # Simular valor usando distribución normal
                vol = volatility.get(metric, base_value * 0.1)
                simulated_value = random.gauss(base_value, vol)
                scenario_results[metric] = max(0, simulated_value)  # No valores negativos
                all_results[metric].append(simulated_value)
        
        # Calcular estadísticas
        statistics = {}
        confidence_intervals = {}
        
        for metric, values in all_results.items():
            values_sorted = sorted(values)
            statistics[metric] = {
                "mean": sum(values) / len(values),
                "median": values_sorted[len(values_sorted) // 2],
                "std": (sum((v - statistics.get(metric, {}).get("mean", 0)) ** 2 for v in values) / len(values)) ** 0.5 if metric in statistics else 0,
                "min": min(values),
                "max": max(values)
            }
            
            # Intervalos de confianza (95%)
            lower_idx = int(len(values_sorted) * 0.025)
            upper_idx = int(len(values_sorted) * 0.975)
            confidence_intervals[metric] = [
                values_sorted[lower_idx],
                values_sorted[upper_idx]
            ]
        
        # Generar insights
        insights = self._generate_simulation_insights(statistics, confidence_intervals)
        
        return MarketSimulation(
            simulation_id=f"monte_carlo_{datetime.utcnow().timestamp()}",
            scenario_name="Monte Carlo Market Simulation",
            simulation_type="monte_carlo",
            iterations=iterations,
            results=statistics,
            confidence_intervals=confidence_intervals,
            key_insights=insights
        )
    
    def run_what_if_scenario(
        self,
        base_scenario: Dict[str, Any],
        what_if_changes: Dict[str, float],  # {metric: percentage_change}
        industry: str
    ) -> MarketSimulation:
        """
        Ejecuta escenario "what-if".
        
        Args:
            base_scenario: Escenario base
            what_if_changes: Cambios a simular {metric: % change}
            industry: Industria
            
        Returns:
            Resultado de simulación
        """
        logger.info(f"Running what-if scenario for {industry}")
        
        # Aplicar cambios
        simulated_results = {}
        for metric, change_pct in what_if_changes.items():
            base_value = base_scenario.get(metric, {}).get("value", 0)
            new_value = base_value * (1 + change_pct / 100)
            simulated_results[metric] = {
                "base_value": base_value,
                "new_value": new_value,
                "change": new_value - base_value,
                "change_percentage": change_pct
            }
        
        # Calcular impacto agregado
        total_impact = sum(r["change"] for r in simulated_results.values())
        
        insights = [
            f"Total impact: ${total_impact:,.0f}",
            f"Largest change: {max(what_if_changes.items(), key=lambda x: abs(x[1]))[0]}"
        ]
        
        return MarketSimulation(
            simulation_id=f"what_if_{datetime.utcnow().timestamp()}",
            scenario_name="What-If Scenario Analysis",
            simulation_type="what_if",
            iterations=1,
            results=simulated_results,
            confidence_intervals={},
            key_insights=insights
        )
    
    def _generate_simulation_insights(
        self,
        statistics: Dict[str, Dict[str, float]],
        confidence_intervals: Dict[str, List[float]]
    ) -> List[str]:
        """Genera insights de simulación."""
        insights = []
        
        # Identificar métricas más volátiles
        volatilities = {
            metric: stats.get("std", 0) / stats.get("mean", 1) if stats.get("mean", 0) > 0 else 0
            for metric, stats in statistics.items()
        }
        
        if volatilities:
            most_volatile = max(volatilities.items(), key=lambda x: x[1])
            insights.append(f"Most volatile metric: {most_volatile[0]} (CV: {most_volatile[1]:.2f})")
        
        # Identificar rangos de confianza más amplios
        ranges = {
            metric: interval[1] - interval[0]
            for metric, interval in confidence_intervals.items()
        }
        
        if ranges:
            widest_range = max(ranges.items(), key=lambda x: x[1])
            insights.append(f"Widest confidence interval: {widest_range[0]} (range: {widest_range[1]:.2f})")
        
        return insights






