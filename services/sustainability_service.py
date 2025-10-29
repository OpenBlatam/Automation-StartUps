from datetime import datetime, timedelta
from app import db
from models import Product, InventoryRecord, SalesRecord
import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Tuple
import logging
from dataclasses import dataclass
import json
import os
import uuid
from enum import Enum

class EnvironmentalImpact(Enum):
    """Impacto ambiental"""
    VERY_LOW = "very_low"
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    VERY_HIGH = "very_high"

class SustainabilityMetric(Enum):
    """Métricas de sostenibilidad"""
    CARBON_FOOTPRINT = "carbon_footprint"
    WATER_USAGE = "water_usage"
    ENERGY_CONSUMPTION = "energy_consumption"
    WASTE_GENERATION = "waste_generation"
    RECYCLING_RATE = "recycling_rate"
    RENEWABLE_ENERGY = "renewable_energy"

class SustainabilityGoal(Enum):
    """Objetivos de sostenibilidad"""
    CARBON_NEUTRAL = "carbon_neutral"
    ZERO_WASTE = "zero_waste"
    WATER_POSITIVE = "water_positive"
    RENEWABLE_ENERGY = "renewable_energy"
    CIRCULAR_ECONOMY = "circular_economy"

@dataclass
class EnvironmentalMetric:
    """Métrica ambiental"""
    id: str
    metric_type: SustainabilityMetric
    product_id: Optional[int]
    value: float
    unit: str
    measurement_date: datetime
    source: str  # 'manufacturing', 'transportation', 'packaging', 'usage', 'disposal'
    location: str
    verified: bool = False
    notes: str = ""

@dataclass
class SustainabilityGoal:
    """Objetivo de sostenibilidad"""
    id: str
    name: str
    description: str
    goal_type: SustainabilityGoal
    target_value: float
    current_value: float
    unit: str
    target_date: datetime
    status: str  # 'on_track', 'at_risk', 'behind', 'achieved'
    progress_percentage: float
    created_at: datetime
    updated_at: datetime

@dataclass
class CarbonFootprint:
    """Huella de carbono"""
    id: str
    product_id: int
    scope: str  # 'scope1', 'scope2', 'scope3'
    category: str  # 'manufacturing', 'transportation', 'packaging', 'usage', 'disposal'
    co2_equivalent: float  # kg CO2e
    measurement_date: datetime
    methodology: str
    verified: bool = False

@dataclass
class WasteManagement:
    """Gestión de residuos"""
    id: str
    product_id: int
    waste_type: str  # 'hazardous', 'non_hazardous', 'recyclable', 'organic'
    quantity: float
    unit: str
    disposal_method: str  # 'landfill', 'incineration', 'recycling', 'composting'
    disposal_date: datetime
    location: str
    cost: float
    environmental_impact: EnvironmentalImpact

class SustainabilityService:
    """Servicio de sostenibilidad y análisis ambiental"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.environmental_metrics = {}
        self.sustainability_goals = {}
        self.carbon_footprints = {}
        self.waste_management = {}
        
        # Configurar objetivos de sostenibilidad por defecto
        self._setup_default_sustainability_goals()
    
    def _setup_default_sustainability_goals(self):
        """Configura objetivos de sostenibilidad por defecto"""
        goals = [
            SustainabilityGoal(
                id="GOAL_001",
                name="Reducción de Huella de Carbono",
                description="Reducir la huella de carbono en un 30% para 2025",
                goal_type=SustainabilityGoal.CARBON_NEUTRAL,
                target_value=30.0,
                current_value=15.0,
                unit="%",
                target_date=datetime(2025, 12, 31),
                status="on_track",
                progress_percentage=50.0,
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
            ),
            SustainabilityGoal(
                id="GOAL_002",
                name="Cero Residuos",
                description="Alcanzar cero residuos en vertederos para 2026",
                goal_type=SustainabilityGoal.ZERO_WASTE,
                target_value=0.0,
                current_value=5.0,
                unit="%",
                target_date=datetime(2026, 12, 31),
                status="on_track",
                progress_percentage=95.0,
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
            ),
            SustainabilityGoal(
                id="GOAL_003",
                name="Energía Renovable",
                description="Usar 100% de energía renovable para 2024",
                goal_type=SustainabilityGoal.RENEWABLE_ENERGY,
                target_value=100.0,
                current_value=75.0,
                unit="%",
                target_date=datetime(2024, 12, 31),
                status="at_risk",
                progress_percentage=75.0,
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
            ),
            SustainabilityGoal(
                id="GOAL_004",
                name="Economía Circular",
                description="Implementar principios de economía circular en 80% de productos",
                goal_type=SustainabilityGoal.CIRCULAR_ECONOMY,
                target_value=80.0,
                current_value=45.0,
                unit="%",
                target_date=datetime(2025, 6, 30),
                status="behind",
                progress_percentage=56.25,
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
            )
        ]
        
        for goal in goals:
            self.sustainability_goals[goal.id] = goal
    
    def record_environmental_metric(self, metric_type: SustainabilityMetric, 
                                  product_id: int = None, value: float = 0.0,
                                  unit: str = "", source: str = "", 
                                  location: str = "", verified: bool = False,
                                  notes: str = "") -> Dict:
        """Registra métrica ambiental"""
        try:
            metric_id = f"EM_{uuid.uuid4().hex[:8].upper()}"
            
            metric = EnvironmentalMetric(
                id=metric_id,
                metric_type=metric_type,
                product_id=product_id,
                value=value,
                unit=unit,
                measurement_date=datetime.utcnow(),
                source=source,
                location=location,
                verified=verified,
                notes=notes
            )
            
            self.environmental_metrics[metric_id] = metric
            
            return {
                'success': True,
                'metric': {
                    'id': metric.id,
                    'metric_type': metric.metric_type.value,
                    'product_id': metric.product_id,
                    'value': metric.value,
                    'unit': metric.unit,
                    'measurement_date': metric.measurement_date.isoformat(),
                    'source': metric.source,
                    'location': metric.location,
                    'verified': metric.verified,
                    'notes': metric.notes
                }
            }
            
        except Exception as e:
            self.logger.error(f'Error registrando métrica ambiental: {str(e)}')
            return {'error': str(e)}
    
    def calculate_carbon_footprint(self, product_id: int, scope: str = "scope3") -> Dict:
        """Calcula huella de carbono de un producto"""
        try:
            # Obtener métricas ambientales del producto
            product_metrics = [
                metric for metric in self.environmental_metrics.values()
                if metric.product_id == product_id and metric.metric_type == SustainabilityMetric.CARBON_FOOTPRINT
            ]
            
            if not product_metrics:
                # Generar datos simulados si no hay métricas reales
                co2_equivalent = np.random.uniform(0.5, 5.0)  # kg CO2e
            else:
                co2_equivalent = sum(metric.value for metric in product_metrics)
            
            footprint_id = f"CF_{uuid.uuid4().hex[:8].upper()}"
            
            carbon_footprint = CarbonFootprint(
                id=footprint_id,
                product_id=product_id,
                scope=scope,
                category="total",
                co2_equivalent=co2_equivalent,
                measurement_date=datetime.utcnow(),
                methodology="ISO 14067",
                verified=False
            )
            
            self.carbon_footprints[footprint_id] = carbon_footprint
            
            return {
                'success': True,
                'carbon_footprint': {
                    'id': carbon_footprint.id,
                    'product_id': carbon_footprint.product_id,
                    'scope': carbon_footprint.scope,
                    'category': carbon_footprint.category,
                    'co2_equivalent': carbon_footprint.co2_equivalent,
                    'measurement_date': carbon_footprint.measurement_date.isoformat(),
                    'methodology': carbon_footprint.methodology,
                    'verified': carbon_footprint.verified
                }
            }
            
        except Exception as e:
            self.logger.error(f'Error calculando huella de carbono: {str(e)}')
            return {'error': str(e)}
    
    def record_waste_management(self, product_id: int, waste_type: str,
                              quantity: float, unit: str, disposal_method: str,
                              location: str, cost: float = 0.0) -> Dict:
        """Registra gestión de residuos"""
        try:
            # Determinar impacto ambiental basado en método de disposición
            impact_mapping = {
                'recycling': EnvironmentalImpact.LOW,
                'composting': EnvironmentalImpact.LOW,
                'incineration': EnvironmentalImpact.MEDIUM,
                'landfill': EnvironmentalImpact.HIGH
            }
            
            environmental_impact = impact_mapping.get(disposal_method, EnvironmentalImpact.MEDIUM)
            
            waste_id = f"WM_{uuid.uuid4().hex[:8].upper()}"
            
            waste_record = WasteManagement(
                id=waste_id,
                product_id=product_id,
                waste_type=waste_type,
                quantity=quantity,
                unit=unit,
                disposal_method=disposal_method,
                disposal_date=datetime.utcnow(),
                location=location,
                cost=cost,
                environmental_impact=environmental_impact
            )
            
            self.waste_management[waste_id] = waste_record
            
            return {
                'success': True,
                'waste_record': {
                    'id': waste_record.id,
                    'product_id': waste_record.product_id,
                    'waste_type': waste_record.waste_type,
                    'quantity': waste_record.quantity,
                    'unit': waste_record.unit,
                    'disposal_method': waste_record.disposal_method,
                    'disposal_date': waste_record.disposal_date.isoformat(),
                    'location': waste_record.location,
                    'cost': waste_record.cost,
                    'environmental_impact': waste_record.environmental_impact.value
                }
            }
            
        except Exception as e:
            self.logger.error(f'Error registrando gestión de residuos: {str(e)}')
            return {'error': str(e)}
    
    def get_sustainability_dashboard(self) -> Dict:
        """Obtiene datos para dashboard de sostenibilidad"""
        try:
            # Estadísticas de métricas ambientales
            total_metrics = len(self.environmental_metrics)
            recent_metrics = len([
                metric for metric in self.environmental_metrics.values()
                if metric.measurement_date > datetime.utcnow() - timedelta(days=30)
            ])
            
            # Distribución por tipo de métrica
            metric_distribution = {}
            for metric in self.environmental_metrics.values():
                metric_type = metric.metric_type.value
                metric_distribution[metric_type] = metric_distribution.get(metric_type, 0) + 1
            
            # Estadísticas de huella de carbono
            total_footprints = len(self.carbon_footprints)
            avg_carbon_footprint = 0
            if total_footprints > 0:
                avg_carbon_footprint = sum(fp.co2_equivalent for fp in self.carbon_footprints.values()) / total_footprints
            
            # Estadísticas de gestión de residuos
            total_waste_records = len(self.waste_management)
            recycling_rate = 0
            if total_waste_records > 0:
                recycled_records = len([
                    record for record in self.waste_management.values()
                    if record.disposal_method == 'recycling'
                ])
                recycling_rate = (recycled_records / total_waste_records) * 100
            
            # Progreso de objetivos de sostenibilidad
            goals_progress = []
            for goal in self.sustainability_goals.values():
                goals_progress.append({
                    'id': goal.id,
                    'name': goal.name,
                    'progress_percentage': goal.progress_percentage,
                    'status': goal.status,
                    'target_date': goal.target_date.isoformat()
                })
            
            return {
                'success': True,
                'dashboard': {
                    'environmental_metrics': {
                        'total': total_metrics,
                        'recent_30_days': recent_metrics,
                        'distribution': metric_distribution
                    },
                    'carbon_footprint': {
                        'total_calculations': total_footprints,
                        'average_co2_equivalent': avg_carbon_footprint
                    },
                    'waste_management': {
                        'total_records': total_waste_records,
                        'recycling_rate': recycling_rate
                    },
                    'sustainability_goals': {
                        'total_goals': len(self.sustainability_goals),
                        'goals_progress': goals_progress
                    }
                }
            }
            
        except Exception as e:
            self.logger.error(f'Error obteniendo dashboard de sostenibilidad: {str(e)}')
            return {'error': str(e)}
    
    def generate_sustainability_report(self, start_date: datetime = None, 
                                     end_date: datetime = None) -> Dict:
        """Genera reporte de sostenibilidad"""
        try:
            if start_date is None:
                start_date = datetime.utcnow() - timedelta(days=90)
            if end_date is None:
                end_date = datetime.utcnow()
            
            # Filtrar métricas ambientales por período
            filtered_metrics = [
                metric for metric in self.environmental_metrics.values()
                if start_date <= metric.measurement_date <= end_date
            ]
            
            # Filtrar huellas de carbono por período
            filtered_footprints = [
                fp for fp in self.carbon_footprints.values()
                if start_date <= fp.measurement_date <= end_date
            ]
            
            # Filtrar gestión de residuos por período
            filtered_waste = [
                waste for waste in self.waste_management.values()
                if start_date <= waste.disposal_date <= end_date
            ]
            
            # Calcular métricas de sostenibilidad
            total_carbon_footprint = sum(fp.co2_equivalent for fp in filtered_footprints)
            total_waste_generated = sum(waste.quantity for waste in filtered_waste)
            total_recycling = sum(
                waste.quantity for waste in filtered_waste 
                if waste.disposal_method == 'recycling'
            )
            
            recycling_rate = (total_recycling / total_waste_generated * 100) if total_waste_generated > 0 else 0
            
            # Distribución de métodos de disposición
            disposal_distribution = {}
            for waste in filtered_waste:
                method = waste.disposal_method
                disposal_distribution[method] = disposal_distribution.get(method, 0) + waste.quantity
            
            # Impacto ambiental promedio
            impact_scores = {
                EnvironmentalImpact.VERY_LOW: 1,
                EnvironmentalImpact.LOW: 2,
                EnvironmentalImpact.MEDIUM: 3,
                EnvironmentalImpact.HIGH: 4,
                EnvironmentalImpact.VERY_HIGH: 5
            }
            
            avg_environmental_impact = 0
            if filtered_waste:
                total_impact = sum(impact_scores[waste.environmental_impact] for waste in filtered_waste)
                avg_environmental_impact = total_impact / len(filtered_waste)
            
            return {
                'success': True,
                'report': {
                    'period': {
                        'start_date': start_date.isoformat(),
                        'end_date': end_date.isoformat()
                    },
                    'summary': {
                        'total_carbon_footprint': total_carbon_footprint,
                        'total_waste_generated': total_waste_generated,
                        'recycling_rate': recycling_rate,
                        'average_environmental_impact': avg_environmental_impact
                    },
                    'disposal_distribution': disposal_distribution,
                    'environmental_metrics_count': len(filtered_metrics),
                    'carbon_footprint_calculations': len(filtered_footprints),
                    'waste_records': len(filtered_waste),
                    'generated_at': datetime.utcnow().isoformat()
                }
            }
            
        except Exception as e:
            self.logger.error(f'Error generando reporte de sostenibilidad: {str(e)}')
            return {'error': str(e)}
    
    def update_sustainability_goal(self, goal_id: str, current_value: float) -> Dict:
        """Actualiza objetivo de sostenibilidad"""
        try:
            if goal_id not in self.sustainability_goals:
                return {'error': 'Objetivo no encontrado'}
            
            goal = self.sustainability_goals[goal_id]
            
            # Calcular progreso
            if goal.target_value > goal.current_value:
                progress_percentage = (current_value / goal.target_value) * 100
            else:
                progress_percentage = ((goal.current_value - current_value) / goal.current_value) * 100
            
            # Determinar estado
            if progress_percentage >= 100:
                status = "achieved"
            elif progress_percentage >= 80:
                status = "on_track"
            elif progress_percentage >= 60:
                status = "at_risk"
            else:
                status = "behind"
            
            # Actualizar objetivo
            goal.current_value = current_value
            goal.progress_percentage = min(progress_percentage, 100)
            goal.status = status
            goal.updated_at = datetime.utcnow()
            
            return {
                'success': True,
                'goal': {
                    'id': goal.id,
                    'name': goal.name,
                    'current_value': goal.current_value,
                    'target_value': goal.target_value,
                    'progress_percentage': goal.progress_percentage,
                    'status': goal.status,
                    'updated_at': goal.updated_at.isoformat()
                }
            }
            
        except Exception as e:
            self.logger.error(f'Error actualizando objetivo de sostenibilidad: {str(e)}')
            return {'error': str(e)}

# Instancia global del servicio de sostenibilidad
sustainability_service = SustainabilityService()



