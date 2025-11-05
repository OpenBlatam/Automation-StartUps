from datetime import datetime, timedelta
from app import db
from models import Product, SalesRecord, InventoryRecord, Supplier
import pandas as pd
import numpy as np
from typing import Dict, List, Tuple, Optional
import logging
import random
from dataclasses import dataclass
import json

@dataclass
class OptimizationResult:
    """Resultado de optimización de inventario"""
    total_cost: float
    total_value: float
    service_level: float
    solution: Dict[int, int]  # product_id -> optimal_stock
    iterations: int
    convergence_time: float
    fitness_history: List[float]

class InventoryOptimizationService:
    """Servicio de optimización de inventario usando algoritmos genéticos"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        
        # Parámetros del algoritmo genético
        self.population_size = 50
        self.generations = 100
        self.mutation_rate = 0.1
        self.crossover_rate = 0.8
        self.elite_size = 5
        
        # Parámetros de optimización
        self.holding_cost_rate = 0.02  # 2% anual
        self.stockout_cost_rate = 0.1  # 10% del valor del producto
        self.service_level_target = 0.95  # 95%
        
    def optimize_inventory(self, products: List[int] = None, 
                          budget_constraint: float = None,
                          warehouse_capacity: float = None) -> OptimizationResult:
        """Optimiza el inventario usando algoritmo genético"""
        try:
            # Obtener productos a optimizar
            if products is None:
                products = [p.id for p in Product.query.all()]
            
            # Preparar datos de productos
            product_data = self._prepare_product_data(products)
            
            if not product_data:
                return OptimizationResult(0, 0, 0, {}, 0, 0, [])
            
            # Inicializar población
            population = self._initialize_population(product_data, budget_constraint, warehouse_capacity)
            
            # Evolución
            fitness_history = []
            best_solution = None
            best_fitness = float('inf')
            
            start_time = datetime.utcnow()
            
            for generation in range(self.generations):
                # Evaluar fitness
                fitness_scores = []
                for individual in population:
                    fitness = self._calculate_fitness(individual, product_data, budget_constraint, warehouse_capacity)
                    fitness_scores.append(fitness)
                    
                    if fitness < best_fitness:
                        best_fitness = fitness
                        best_solution = individual.copy()
                
                fitness_history.append(min(fitness_scores))
                
                # Selección, crossover y mutación
                population = self._evolve_population(population, fitness_scores)
                
                # Log de progreso
                if generation % 10 == 0:
                    self.logger.info(f'Generación {generation}: Mejor fitness = {min(fitness_scores):.2f}')
            
            end_time = datetime.utcnow()
            convergence_time = (end_time - start_time).total_seconds()
            
            # Crear resultado
            if best_solution:
                solution_dict = {product_data[i]['id']: best_solution[i] for i in range(len(product_data))}
                total_cost, total_value, service_level = self._calculate_metrics(best_solution, product_data)
                
                return OptimizationResult(
                    total_cost=total_cost,
                    total_value=total_value,
                    service_level=service_level,
                    solution=solution_dict,
                    iterations=self.generations,
                    convergence_time=convergence_time,
                    fitness_history=fitness_history
                )
            
            return OptimizationResult(0, 0, 0, {}, 0, 0, [])
            
        except Exception as e:
            self.logger.error(f'Error optimizando inventario: {str(e)}')
            return OptimizationResult(0, 0, 0, {}, 0, 0, [])
    
    def _prepare_product_data(self, product_ids: List[int]) -> List[Dict]:
        """Prepara datos de productos para optimización"""
        try:
            product_data = []
            
            for product_id in product_ids:
                product = Product.query.get(product_id)
                if not product:
                    continue
                
                # Calcular demanda promedio
                demand_data = self._calculate_demand_stats(product_id)
                
                # Calcular costos
                holding_cost = product.unit_price * self.holding_cost_rate / 365  # Costo diario
                stockout_cost = product.unit_price * self.stockout_cost_rate
                
                product_info = {
                    'id': product_id,
                    'name': product.name,
                    'unit_price': product.unit_price,
                    'cost_price': product.cost_price,
                    'min_stock': product.min_stock_level,
                    'max_stock': product.max_stock_level,
                    'current_stock': self._get_current_stock(product_id),
                    'demand_mean': demand_data['mean'],
                    'demand_std': demand_data['std'],
                    'holding_cost': holding_cost,
                    'stockout_cost': stockout_cost,
                    'volume_per_unit': 1.0,  # Simplificado
                    'lead_time': 7  # Días promedio
                }
                
                product_data.append(product_info)
            
            return product_data
            
        except Exception as e:
            self.logger.error(f'Error preparando datos de productos: {str(e)}')
            return []
    
    def _calculate_demand_stats(self, product_id: int, days_back: int = 90) -> Dict:
        """Calcula estadísticas de demanda"""
        try:
            end_date = datetime.utcnow()
            start_date = end_date - timedelta(days=days_back)
            
            sales = SalesRecord.query.filter(
                SalesRecord.product_id == product_id,
                SalesRecord.sale_date >= start_date,
                SalesRecord.sale_date <= end_date
            ).all()
            
            if not sales:
                return {'mean': 1.0, 'std': 0.5}
            
            quantities = [sale.quantity_sold for sale in sales]
            return {
                'mean': np.mean(quantities),
                'std': np.std(quantities) if len(quantities) > 1 else 0.5
            }
            
        except Exception as e:
            self.logger.error(f'Error calculando estadísticas de demanda: {str(e)}')
            return {'mean': 1.0, 'std': 0.5}
    
    def _get_current_stock(self, product_id: int) -> int:
        """Obtiene el stock actual de un producto"""
        try:
            # Calcular stock actual basado en movimientos
            entries = db.session.query(db.func.sum(InventoryRecord.quantity)).filter(
                InventoryRecord.product_id == product_id,
                InventoryRecord.movement_type == 'in'
            ).scalar() or 0
            
            exits = db.session.query(db.func.sum(InventoryRecord.quantity)).filter(
                InventoryRecord.product_id == product_id,
                InventoryRecord.movement_type == 'out'
            ).scalar() or 0
            
            adjustments = db.session.query(db.func.sum(InventoryRecord.quantity)).filter(
                InventoryRecord.product_id == product_id,
                InventoryRecord.movement_type == 'adjustment'
            ).scalar() or 0
            
            return max(0, entries - exits + adjustments)
            
        except Exception as e:
            self.logger.error(f'Error obteniendo stock actual: {str(e)}')
            return 0
    
    def _initialize_population(self, product_data: List[Dict], 
                             budget_constraint: float = None,
                             warehouse_capacity: float = None) -> List[List[int]]:
        """Inicializa la población del algoritmo genético"""
        population = []
        
        for _ in range(self.population_size):
            individual = []
            
            for product in product_data:
                # Generar stock aleatorio dentro de límites
                min_stock = product['min_stock']
                max_stock = product['max_stock']
                
                # Stock aleatorio con distribución normal centrada en la demanda promedio
                mean_demand = product['demand_mean']
                std_demand = product['demand_std']
                
                # Generar valor con distribución normal
                stock = int(np.random.normal(mean_demand * 30, std_demand * 10))  # Stock para 30 días
                stock = max(min_stock, min(max_stock, stock))
                
                individual.append(stock)
            
            # Verificar restricciones
            if self._check_constraints(individual, product_data, budget_constraint, warehouse_capacity):
                population.append(individual)
            else:
                # Ajustar individual para cumplir restricciones
                adjusted_individual = self._adjust_for_constraints(
                    individual, product_data, budget_constraint, warehouse_capacity
                )
                population.append(adjusted_individual)
        
        return population
    
    def _check_constraints(self, individual: List[int], product_data: List[Dict],
                          budget_constraint: float = None,
                          warehouse_capacity: float = None) -> bool:
        """Verifica si un individuo cumple las restricciones"""
        try:
            # Restricción de presupuesto
            if budget_constraint:
                total_cost = sum(
                    individual[i] * product_data[i]['cost_price'] 
                    for i in range(len(individual))
                )
                if total_cost > budget_constraint:
                    return False
            
            # Restricción de capacidad de almacén
            if warehouse_capacity:
                total_volume = sum(
                    individual[i] * product_data[i]['volume_per_unit'] 
                    for i in range(len(individual))
                )
                if total_volume > warehouse_capacity:
                    return False
            
            return True
            
        except Exception as e:
            self.logger.error(f'Error verificando restricciones: {str(e)}')
            return False
    
    def _adjust_for_constraints(self, individual: List[int], product_data: List[Dict],
                               budget_constraint: float = None,
                               warehouse_capacity: float = None) -> List[int]:
        """Ajusta un individuo para cumplir las restricciones"""
        adjusted = individual.copy()
        
        # Ajustar por presupuesto
        if budget_constraint:
            while True:
                total_cost = sum(
                    adjusted[i] * product_data[i]['cost_price'] 
                    for i in range(len(adjusted))
                )
                
                if total_cost <= budget_constraint:
                    break
                
                # Reducir stock del producto más caro
                max_cost_idx = max(range(len(adjusted)), 
                                 key=lambda i: adjusted[i] * product_data[i]['cost_price'])
                
                if adjusted[max_cost_idx] > product_data[max_cost_idx]['min_stock']:
                    adjusted[max_cost_idx] -= 1
                else:
                    break
        
        # Ajustar por capacidad
        if warehouse_capacity:
            while True:
                total_volume = sum(
                    adjusted[i] * product_data[i]['volume_per_unit'] 
                    for i in range(len(adjusted))
                )
                
                if total_volume <= warehouse_capacity:
                    break
                
                # Reducir stock del producto con mayor volumen
                max_volume_idx = max(range(len(adjusted)), 
                                   key=lambda i: adjusted[i] * product_data[i]['volume_per_unit'])
                
                if adjusted[max_volume_idx] > product_data[max_volume_idx]['min_stock']:
                    adjusted[max_volume_idx] -= 1
                else:
                    break
        
        return adjusted
    
    def _calculate_fitness(self, individual: List[int], product_data: List[Dict],
                          budget_constraint: float = None,
                          warehouse_capacity: float = None) -> float:
        """Calcula el fitness de un individuo"""
        try:
            total_cost = 0
            total_service_level = 0
            
            for i, stock in enumerate(individual):
                product = product_data[i]
                
                # Costo de mantenimiento
                holding_cost = stock * product['holding_cost']
                
                # Costo de stockout (probabilidad de quedarse sin stock)
                stockout_probability = self._calculate_stockout_probability(stock, product)
                stockout_cost = stockout_probability * product['stockout_cost']
                
                total_cost += holding_cost + stockout_cost
                
                # Nivel de servicio
                service_level = 1 - stockout_probability
                total_service_level += service_level
            
            # Fitness = costo total + penalización por bajo nivel de servicio
            avg_service_level = total_service_level / len(individual)
            service_penalty = max(0, (self.service_level_target - avg_service_level) * 10000)
            
            fitness = total_cost + service_penalty
            
            return fitness
            
        except Exception as e:
            self.logger.error(f'Error calculando fitness: {str(e)}')
            return float('inf')
    
    def _calculate_stockout_probability(self, stock: int, product: Dict) -> float:
        """Calcula la probabilidad de stockout"""
        try:
            # Usar distribución normal para modelar la demanda
            mean_demand = product['demand_mean']
            std_demand = product['demand_std']
            lead_time = product['lead_time']
            
            # Demanda durante el lead time
            lead_time_demand_mean = mean_demand * lead_time
            lead_time_demand_std = std_demand * np.sqrt(lead_time)
            
            # Probabilidad de que la demanda exceda el stock
            if lead_time_demand_std > 0:
                z_score = (stock - lead_time_demand_mean) / lead_time_demand_std
                # Usar aproximación de la función de distribución normal
                stockout_prob = max(0, min(1, 0.5 * (1 - np.tanh(z_score * 0.8))))
            else:
                stockout_prob = 0 if stock >= lead_time_demand_mean else 1
            
            return stockout_prob
            
        except Exception as e:
            self.logger.error(f'Error calculando probabilidad de stockout: {str(e)}')
            return 0.5
    
    def _evolve_population(self, population: List[List[int]], 
                         fitness_scores: List[float]) -> List[List[int]]:
        """Evoluciona la población usando selección, crossover y mutación"""
        try:
            new_population = []
            
            # Elitismo: mantener los mejores individuos
            elite_indices = sorted(range(len(fitness_scores)), 
                                 key=lambda i: fitness_scores[i])[:self.elite_size]
            
            for idx in elite_indices:
                new_population.append(population[idx].copy())
            
            # Generar el resto de la población
            while len(new_population) < self.population_size:
                # Selección por torneo
                parent1 = self._tournament_selection(population, fitness_scores)
                parent2 = self._tournament_selection(population, fitness_scores)
                
                # Crossover
                if random.random() < self.crossover_rate:
                    child1, child2 = self._crossover(parent1, parent2)
                else:
                    child1, child2 = parent1.copy(), parent2.copy()
                
                # Mutación
                child1 = self._mutate(child1)
                child2 = self._mutate(child2)
                
                new_population.extend([child1, child2])
            
            # Asegurar que no excedamos el tamaño de población
            return new_population[:self.population_size]
            
        except Exception as e:
            self.logger.error(f'Error evolucionando población: {str(e)}')
            return population
    
    def _tournament_selection(self, population: List[List[int]], 
                            fitness_scores: List[float], 
                            tournament_size: int = 3) -> List[int]:
        """Selección por torneo"""
        try:
            tournament_indices = random.sample(range(len(population)), tournament_size)
            tournament_fitness = [fitness_scores[i] for i in tournament_indices]
            
            winner_idx = tournament_indices[min(range(len(tournament_fitness)), 
                                              key=lambda i: tournament_fitness[i])]
            
            return population[winner_idx].copy()
            
        except Exception as e:
            self.logger.error(f'Error en selección por torneo: {str(e)}')
            return population[0].copy()
    
    def _crossover(self, parent1: List[int], parent2: List[int]) -> Tuple[List[int], List[int]]:
        """Crossover de dos puntos"""
        try:
            if len(parent1) < 2:
                return parent1.copy(), parent2.copy()
            
            # Seleccionar dos puntos de corte
            point1 = random.randint(0, len(parent1) - 1)
            point2 = random.randint(point1, len(parent1))
            
            child1 = parent1[:point1] + parent2[point1:point2] + parent1[point2:]
            child2 = parent2[:point1] + parent1[point1:point2] + parent2[point2:]
            
            return child1, child2
            
        except Exception as e:
            self.logger.error(f'Error en crossover: {str(e)}')
            return parent1.copy(), parent2.copy()
    
    def _mutate(self, individual: List[int]) -> List[int]:
        """Mutación gaussiana"""
        try:
            mutated = individual.copy()
            
            for i in range(len(mutated)):
                if random.random() < self.mutation_rate:
                    # Mutación gaussiana
                    mutation = int(np.random.normal(0, 2))
                    mutated[i] = max(0, mutated[i] + mutation)
            
            return mutated
            
        except Exception as e:
            self.logger.error(f'Error en mutación: {str(e)}')
            return individual.copy()
    
    def _calculate_metrics(self, solution: List[int], product_data: List[Dict]) -> Tuple[float, float, float]:
        """Calcula métricas del resultado"""
        try:
            total_cost = 0
            total_value = 0
            total_service_level = 0
            
            for i, stock in enumerate(solution):
                product = product_data[i]
                
                # Costo total
                holding_cost = stock * product['holding_cost']
                stockout_prob = self._calculate_stockout_probability(stock, product)
                stockout_cost = stockout_prob * product['stockout_cost']
                total_cost += holding_cost + stockout_cost
                
                # Valor total
                total_value += stock * product['unit_price']
                
                # Nivel de servicio
                service_level = 1 - stockout_prob
                total_service_level += service_level
            
            avg_service_level = total_service_level / len(solution)
            
            return total_cost, total_value, avg_service_level
            
        except Exception as e:
            self.logger.error(f'Error calculando métricas: {str(e)}')
            return 0, 0, 0
    
    def get_optimization_recommendations(self, result: OptimizationResult) -> List[Dict]:
        """Genera recomendaciones basadas en el resultado de optimización"""
        try:
            recommendations = []
            
            for product_id, optimal_stock in result.solution.items():
                product = Product.query.get(product_id)
                if not product:
                    continue
                
                current_stock = self._get_current_stock(product_id)
                difference = optimal_stock - current_stock
                
                if abs(difference) > 0:
                    recommendation = {
                        'product_id': product_id,
                        'product_name': product.name,
                        'current_stock': current_stock,
                        'optimal_stock': optimal_stock,
                        'difference': difference,
                        'action': 'increase' if difference > 0 else 'decrease',
                        'priority': 'high' if abs(difference) > current_stock * 0.5 else 'medium',
                        'estimated_cost': abs(difference) * product.cost_price,
                        'reason': self._get_recommendation_reason(difference, current_stock)
                    }
                    
                    recommendations.append(recommendation)
            
            # Ordenar por prioridad y diferencia
            recommendations.sort(key=lambda x: (x['priority'] == 'high', abs(x['difference'])), reverse=True)
            
            return recommendations
            
        except Exception as e:
            self.logger.error(f'Error generando recomendaciones: {str(e)}')
            return []
    
    def _get_recommendation_reason(self, difference: int, current_stock: int) -> str:
        """Genera la razón para la recomendación"""
        if difference > 0:
            if current_stock == 0:
                return "Producto sin stock - necesita reabastecimiento urgente"
            elif difference > current_stock * 0.5:
                return "Stock insuficiente para mantener nivel de servicio objetivo"
            else:
                return "Aumentar stock para optimizar nivel de servicio"
        else:
            if abs(difference) > current_stock * 0.5:
                return "Stock excesivo - reducir para minimizar costos de mantenimiento"
            else:
                return "Reducir stock para optimizar costos"

# Instancia global del servicio de optimización
inventory_optimization_service = InventoryOptimizationService()



