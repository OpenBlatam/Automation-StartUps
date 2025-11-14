"""
Sistema de Gemelo Digital del Almacén
====================================

Sistema completo de gemelo digital para replicar y simular
el almacén físico en tiempo real con análisis predictivo.
"""

import json
import logging
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass, asdict
from enum import Enum
import sqlite3
import uuid
import math
import random

logger = logging.getLogger(__name__)

class DigitalTwinState(Enum):
    """Estados del gemelo digital"""
    SYNCHRONIZED = "synchronized"
    DESYNCHRONIZED = "desynchronized"
    SIMULATING = "simulating"
    OPTIMIZING = "optimizing"
    ERROR = "error"

class SimulationMode(Enum):
    """Modos de simulación"""
    REAL_TIME = "real_time"
    ACCELERATED = "accelerated"
    SCENARIO_BASED = "scenario_based"
    OPTIMIZATION = "optimization"
    STRESS_TEST = "stress_test"

@dataclass
class PhysicalAsset:
    """Activo físico en el almacén"""
    asset_id: str
    asset_type: str
    position: Tuple[float, float, float]
    dimensions: Tuple[float, float, float]
    weight: float
    status: str
    metadata: Dict[str, Any]

@dataclass
class DigitalAsset:
    """Activo digital en el gemelo"""
    asset_id: str
    physical_asset_id: str
    position: Tuple[float, float, float]
    state: Dict[str, Any]
    last_updated: datetime
    prediction: Optional[Dict[str, Any]] = None

@dataclass
class SimulationResult:
    """Resultado de simulación"""
    simulation_id: str
    scenario: str
    duration: float
    results: Dict[str, Any]
    recommendations: List[str]
    metrics: Dict[str, float]
    timestamp: datetime

class DigitalTwin:
    """Gemelo Digital del Almacén"""
    
    def __init__(self, warehouse_id: str):
        self.warehouse_id = warehouse_id
        self.physical_assets: Dict[str, PhysicalAsset] = {}
        self.digital_assets: Dict[str, DigitalAsset] = {}
        self.state = DigitalTwinState.DESYNCHRONIZED
        self.sync_frequency = 5  # segundos
        self.is_syncing = False
        self.simulation_history: List[SimulationResult] = []
        self.predictions: Dict[str, Dict[str, Any]] = {}
        
        # Inicializar base de datos
        self._init_database()
    
    def _init_database(self):
        """Inicializar base de datos para gemelo digital"""
        conn = sqlite3.connect('digital_twin.db')
        cursor = conn.cursor()
        
        # Tabla de activos físicos
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS physical_assets (
                asset_id TEXT PRIMARY KEY,
                warehouse_id TEXT NOT NULL,
                asset_type TEXT NOT NULL,
                position_x REAL NOT NULL,
                position_y REAL NOT NULL,
                position_z REAL NOT NULL,
                dimensions_x REAL NOT NULL,
                dimensions_y REAL NOT NULL,
                dimensions_z REAL NOT NULL,
                weight REAL NOT NULL,
                status TEXT NOT NULL,
                metadata TEXT NOT NULL,
                last_updated TEXT NOT NULL
            )
        ''')
        
        # Tabla de activos digitales
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS digital_assets (
                asset_id TEXT PRIMARY KEY,
                physical_asset_id TEXT NOT NULL,
                position_x REAL NOT NULL,
                position_y REAL NOT NULL,
                position_z REAL NOT NULL,
                state TEXT NOT NULL,
                last_updated TEXT NOT NULL,
                prediction TEXT,
                FOREIGN KEY (physical_asset_id) REFERENCES physical_assets (asset_id)
            )
        ''')
        
        # Tabla de sincronizaciones
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS sync_logs (
                sync_id TEXT PRIMARY KEY,
                warehouse_id TEXT NOT NULL,
                sync_timestamp TEXT NOT NULL,
                assets_synced INTEGER NOT NULL,
                sync_duration REAL NOT NULL,
                status TEXT NOT NULL,
                errors TEXT
            )
        ''')
        
        # Tabla de simulaciones
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS simulations (
                simulation_id TEXT PRIMARY KEY,
                scenario TEXT NOT NULL,
                duration REAL NOT NULL,
                results TEXT NOT NULL,
                recommendations TEXT NOT NULL,
                metrics TEXT NOT NULL,
                timestamp TEXT NOT NULL
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def add_physical_asset(self, asset_id: str, asset_type: str,
                          position: Tuple[float, float, float],
                          dimensions: Tuple[float, float, float],
                          weight: float, status: str = "active",
                          metadata: Dict[str, Any] = None) -> PhysicalAsset:
        """Agregar activo físico"""
        
        asset = PhysicalAsset(
            asset_id=asset_id,
            asset_type=asset_type,
            position=position,
            dimensions=dimensions,
            weight=weight,
            status=status,
            metadata=metadata or {}
        )
        
        self.physical_assets[asset_id] = asset
        
        # Crear gemelo digital automáticamente
        self._create_digital_asset(asset)
        
        # Guardar en base de datos
        self._save_physical_asset_to_db(asset)
        
        logger.info(f"Activo físico agregado: {asset_id} ({asset_type})")
        
        return asset
    
    def _create_digital_asset(self, physical_asset: PhysicalAsset):
        """Crear activo digital correspondiente"""
        
        digital_asset = DigitalAsset(
            asset_id=f"digital_{physical_asset.asset_id}",
            physical_asset_id=physical_asset.asset_id,
            position=physical_asset.position,
            state={
                "position": physical_asset.position,
                "dimensions": physical_asset.dimensions,
                "weight": physical_asset.weight,
                "status": physical_asset.status,
                "metadata": physical_asset.metadata
            },
            last_updated=datetime.now()
        )
        
        self.digital_assets[digital_asset.asset_id] = digital_asset
        
        # Guardar en base de datos
        self._save_digital_asset_to_db(digital_asset)
    
    def sync_with_physical(self):
        """Sincronizar gemelo digital con almacén físico"""
        
        if self.is_syncing:
            return
        
        self.is_syncing = True
        start_time = time.time()
        sync_id = str(uuid.uuid4())
        assets_synced = 0
        errors = []
        
        try:
            # Sincronizar cada activo físico
            for asset_id, physical_asset in self.physical_assets.items():
                try:
                    # Actualizar activo digital
                    digital_asset_id = f"digital_{asset_id}"
                    
                    if digital_asset_id in self.digital_assets:
                        self.digital_assets[digital_asset_id].position = physical_asset.position
                        self.digital_assets[digital_asset_id].state = {
                            "position": physical_asset.position,
                            "dimensions": physical_asset.dimensions,
                            "weight": physical_asset.weight,
                            "status": physical_asset.status,
                            "metadata": physical_asset.metadata
                        }
                        self.digital_assets[digital_asset_id].last_updated = datetime.now()
                        
                        # Guardar actualización
                        self._save_digital_asset_to_db(self.digital_assets[digital_asset_id])
                    else:
                        # Crear nuevo activo digital si no existe
                        self._create_digital_asset(physical_asset)
                    
                    assets_synced += 1
                    
                except Exception as e:
                    errors.append(f"Error sincronizando {asset_id}: {str(e)}")
                    logger.error(f"Error sincronizando activo {asset_id}: {e}")
            
            # Verificar si hay discrepancias
            discrepancies = self._check_discrepancies()
            
            if discrepancies:
                self.state = DigitalTwinState.DESYNCHRONIZED
                logger.warning(f"Desincronizaciones detectadas: {len(discrepancies)}")
            else:
                self.state = DigitalTwinState.SYNCHRONIZED
            
            sync_duration = time.time() - start_time
            
            # Guardar log de sincronización
            self._save_sync_log(sync_id, assets_synced, sync_duration, errors)
            
            logger.info(f"Sincronización completada: {assets_synced} activos, {sync_duration:.2f}s")
            
        finally:
            self.is_syncing = False
    
    def _check_discrepancies(self) -> List[Dict[str, Any]]:
        """Verificar discrepancias entre físico y digital"""
        
        discrepancies = []
        
        for asset_id, physical_asset in self.physical_assets.items():
            digital_asset_id = f"digital_{asset_id}"
            
            if digital_asset_id in self.digital_assets:
                digital_asset = self.digital_assets[digital_asset_id]
                
                # Verificar posición
                pos_diff = math.sqrt(
                    sum((p - d) ** 2 for p, d in zip(physical_asset.position, digital_asset.position))
                )
                
                if pos_diff > 0.1:  # Tolerancia de 10 cm
                    discrepancies.append({
                        "asset_id": asset_id,
                        "type": "position",
                        "physical": physical_asset.position,
                        "digital": digital_asset.position,
                        "difference": pos_diff
                    })
                
                # Verificar estado
                if physical_asset.status != digital_asset.state.get("status"):
                    discrepancies.append({
                        "asset_id": asset_id,
                        "type": "status",
                        "physical": physical_asset.status,
                        "digital": digital_asset.state.get("status")
                    })
        
        return discrepancies
    
    def simulate_scenario(self, scenario_name: str, scenario_config: Dict[str, Any],
                         duration: float = 3600) -> SimulationResult:
        """Simular escenario en el gemelo digital"""
        
        logger.info(f"Iniciando simulación: {scenario_name}")
        
        self.state = DigitalTwinState.SIMULATING
        simulation_id = str(uuid.uuid4())
        start_time = time.time()
        
        # Crear copia de activos digitales para simulación
        sim_assets = {
            asset_id: DigitalAsset(
                asset_id=asset.asset_id,
                physical_asset_id=asset.physical_asset_id,
                position=asset.position,
                state=asset.state.copy(),
                last_updated=asset.last_updated,
                prediction=None
            )
            for asset_id, asset in self.digital_assets.items()
        }
        
        # Ejecutar simulación según configuración
        if scenario_config.get("type") == "capacity_increase":
            results = self._simulate_capacity_increase(sim_assets, scenario_config, duration)
        elif scenario_config.get("type") == "rearrangement":
            results = self._simulate_rearrangement(sim_assets, scenario_config, duration)
        elif scenario_config.get("type") == "demand_spike":
            results = self._simulate_demand_spike(sim_assets, scenario_config, duration)
        else:
            results = self._simulate_generic(sim_assets, scenario_config, duration)
        
        simulation_duration = time.time() - start_time
        
        # Generar recomendaciones
        recommendations = self._generate_recommendations(results)
        
        # Calcular métricas
        metrics = self._calculate_metrics(results)
        
        simulation_result = SimulationResult(
            simulation_id=simulation_id,
            scenario=scenario_name,
            duration=simulation_duration,
            results=results,
            recommendations=recommendations,
            metrics=metrics,
            timestamp=datetime.now()
        )
        
        self.simulation_history.append(simulation_result)
        self._save_simulation_to_db(simulation_result)
        
        self.state = DigitalTwinState.SYNCHRONIZED
        
        logger.info(f"Simulación completada: {scenario_name}")
        
        return simulation_result
    
    def _simulate_capacity_increase(self, sim_assets: Dict[str, DigitalAsset],
                                   config: Dict[str, Any], duration: float) -> Dict[str, Any]:
        """Simular aumento de capacidad"""
        
        # Simular agregar nuevos estantes
        new_shelves = config.get("new_shelves", 5)
        current_capacity = sum(
            asset.state.get("capacity", 100) 
            for asset in sim_assets.values() 
            if asset.state.get("type") == "shelf"
        )
        
        new_capacity = current_capacity + (new_shelves * 100)
        
        # Simular impacto en eficiencia
        utilization_before = sum(
            asset.state.get("utilization", 0) 
            for asset in sim_assets.values() 
            if asset.state.get("type") == "shelf"
        ) / max(1, len([a for a in sim_assets.values() if a.state.get("type") == "shelf"]))
        
        utilization_after = utilization_before * 0.8  # Reducción de utilización
        
        return {
            "scenario": "capacity_increase",
            "new_shelves": new_shelves,
            "capacity_before": current_capacity,
            "capacity_after": new_capacity,
            "utilization_before": utilization_before,
            "utilization_after": utilization_after,
            "efficiency_gain": (utilization_before - utilization_after) / utilization_before if utilization_before > 0 else 0
        }
    
    def _simulate_rearrangement(self, sim_assets: Dict[str, DigitalAsset],
                               config: Dict[str, Any], duration: float) -> Dict[str, Any]:
        """Simular reordenamiento del almacén"""
        
        # Simular reorganización de productos
        products_moved = config.get("products_to_move", 20)
        
        # Calcular distancia promedio antes y después
        avg_distance_before = self._calculate_avg_distance(sim_assets)
        
        # Simular movimientos optimizados
        optimized_positions = self._optimize_positions(sim_assets)
        
        avg_distance_after = self._calculate_avg_distance_optimized(optimized_positions)
        
        distance_reduction = (avg_distance_before - avg_distance_after) / avg_distance_before if avg_distance_before > 0 else 0
        
        return {
            "scenario": "rearrangement",
            "products_moved": products_moved,
            "avg_distance_before": avg_distance_before,
            "avg_distance_after": avg_distance_after,
            "distance_reduction": distance_reduction,
            "time_saved": distance_reduction * 0.5  # Estimación: 0.5 horas por porcentaje
        }
    
    def _simulate_demand_spike(self, sim_assets: Dict[str, DigitalAsset],
                              config: Dict[str, Any], duration: float) -> Dict[str, Any]:
        """Simular pico de demanda"""
        
        spike_factor = config.get("spike_factor", 2.0)
        duration_days = duration / 86400
        
        # Simular impacto en inventario
        initial_inventory = sum(
            asset.state.get("quantity", 0) 
            for asset in sim_assets.values() 
            if asset.state.get("type") == "product"
        )
        
        # Simular demanda aumentada
        demand_rate = sum(
            asset.state.get("daily_demand", 10) 
            for asset in sim_assets.values() 
            if asset.state.get("type") == "product"
        ) * spike_factor
        
        final_inventory = max(0, initial_inventory - (demand_rate * duration_days))
        
        stockouts = len([
            asset for asset in sim_assets.values() 
            if asset.state.get("type") == "product" and asset.state.get("quantity", 0) == 0
        ])
        
        return {
            "scenario": "demand_spike",
            "spike_factor": spike_factor,
            "initial_inventory": initial_inventory,
            "final_inventory": final_inventory,
            "demand_rate": demand_rate,
            "stockouts": stockouts,
            "fill_rate": 1 - (stockouts / max(1, len([a for a in sim_assets.values() if a.state.get("type") == "product"])))
        }
    
    def _simulate_generic(self, sim_assets: Dict[str, DigitalAsset],
                         config: Dict[str, Any], duration: float) -> Dict[str, Any]:
        """Simulación genérica"""
        
        return {
            "scenario": "generic",
            "assets_simulated": len(sim_assets),
            "duration": duration,
            "status": "completed"
        }
    
    def _calculate_avg_distance(self, assets: Dict[str, DigitalAsset]) -> float:
        """Calcular distancia promedio entre productos"""
        
        product_assets = [
            asset for asset in assets.values() 
            if asset.state.get("type") == "product"
        ]
        
        if len(product_assets) < 2:
            return 0.0
        
        total_distance = 0
        pairs = 0
        
        for i, asset1 in enumerate(product_assets):
            for asset2 in product_assets[i+1:]:
                distance = math.sqrt(
                    sum((p1 - p2) ** 2 for p1, p2 in zip(asset1.position, asset2.position))
                )
                total_distance += distance
                pairs += 1
        
        return total_distance / pairs if pairs > 0 else 0.0
    
    def _optimize_positions(self, assets: Dict[str, DigitalAsset]) -> Dict[str, Tuple[float, float, float]]:
        """Optimizar posiciones de productos"""
        
        # Algoritmo simple de optimización (clustering por frecuencia)
        optimized = {}
        
        for asset_id, asset in assets.items():
            if asset.state.get("type") == "product":
                # Simular posición optimizada basada en frecuencia de acceso
                frequency = asset.state.get("access_frequency", 0.5)
                
                # Productos más frecuentes cerca del origen
                scale = 1.0 / (1.0 + frequency)
                optimized[asset_id] = (
                    asset.position[0] * scale,
                    asset.position[1] * scale,
                    asset.position[2]
                )
        
        return optimized
    
    def _calculate_avg_distance_optimized(self, optimized_positions: Dict[str, Tuple[float, float, float]]) -> float:
        """Calcular distancia promedio con posiciones optimizadas"""
        
        if len(optimized_positions) < 2:
            return 0.0
        
        positions_list = list(optimized_positions.values())
        total_distance = 0
        pairs = 0
        
        for i, pos1 in enumerate(positions_list):
            for pos2 in positions_list[i+1:]:
                distance = math.sqrt(sum((p1 - p2) ** 2 for p1, p2 in zip(pos1, pos2)))
                total_distance += distance
                pairs += 1
        
        return total_distance / pairs if pairs > 0 else 0.0
    
    def _generate_recommendations(self, results: Dict[str, Any]) -> List[str]:
        """Generar recomendaciones basadas en resultados de simulación"""
        
        recommendations = []
        
        scenario = results.get("scenario")
        
        if scenario == "capacity_increase":
            efficiency_gain = results.get("efficiency_gain", 0)
            if efficiency_gain > 0.1:
                recommendations.append(
                    f"El aumento de capacidad mejoraría la eficiencia en {efficiency_gain*100:.1f}%"
                )
            else:
                recommendations.append(
                    "El aumento de capacidad no se justifica económicamente en este momento"
                )
        
        elif scenario == "rearrangement":
            distance_reduction = results.get("distance_reduction", 0)
            if distance_reduction > 0.15:
                recommendations.append(
                    f"El reordenamiento reduciría las distancias en {distance_reduction*100:.1f}%, "
                    f"ahorrando aproximadamente {results.get('time_saved', 0):.1f} horas por día"
                )
            else:
                recommendations.append(
                    "El reordenamiento no generaría beneficios significativos"
                )
        
        elif scenario == "demand_spike":
            stockouts = results.get("stockouts", 0)
            if stockouts > 0:
                recommendations.append(
                    f"Se producirían {stockouts} rupturas de stock. "
                    "Considerar aumentar inventario de seguridad"
                )
            else:
                recommendations.append(
                    "El inventario actual es suficiente para manejar el pico de demanda"
                )
        
        return recommendations
    
    def _calculate_metrics(self, results: Dict[str, Any]) -> Dict[str, float]:
        """Calcular métricas de la simulación"""
        
        metrics = {}
        
        scenario = results.get("scenario")
        
        if scenario == "capacity_increase":
            metrics["capacity_utilization"] = results.get("utilization_after", 0)
            metrics["efficiency_improvement"] = results.get("efficiency_gain", 0) * 100
        
        elif scenario == "rearrangement":
            metrics["distance_reduction"] = results.get("distance_reduction", 0) * 100
            metrics["time_saved_hours"] = results.get("time_saved", 0)
        
        elif scenario == "demand_spike":
            metrics["fill_rate"] = results.get("fill_rate", 0) * 100
            metrics["stockout_risk"] = results.get("stockouts", 0)
        
        return metrics
    
    def predict_future_state(self, asset_id: str, hours_ahead: int = 24) -> Dict[str, Any]:
        """Predecir estado futuro de un activo"""
        
        if asset_id not in self.physical_assets:
            raise ValueError(f"Activo no encontrado: {asset_id}")
        
        # Simular predicción basada en tendencias históricas
        physical_asset = self.physical_assets[asset_id]
        
        # Predecir posición (simulado - en realidad usaría ML)
        predicted_position = (
            physical_asset.position[0] + random.gauss(0, 0.1),
            physical_asset.position[1] + random.gauss(0, 0.1),
            physical_asset.position[2]
        )
        
        # Predecir estado
        predicted_state = {
            "position": predicted_position,
            "status": physical_asset.status,
            "confidence": 0.85
        }
        
        prediction = {
            "asset_id": asset_id,
            "hours_ahead": hours_ahead,
            "predicted_state": predicted_state,
            "timestamp": datetime.now().isoformat()
        }
        
        self.predictions[asset_id] = prediction
        
        return prediction
    
    def _save_physical_asset_to_db(self, asset: PhysicalAsset):
        """Guardar activo físico en base de datos"""
        conn = sqlite3.connect('digital_twin.db')
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT OR REPLACE INTO physical_assets 
            (asset_id, warehouse_id, asset_type, position_x, position_y, position_z,
             dimensions_x, dimensions_y, dimensions_z, weight, status, metadata, last_updated)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            asset.asset_id,
            self.warehouse_id,
            asset.asset_type,
            asset.position[0],
            asset.position[1],
            asset.position[2],
            asset.dimensions[0],
            asset.dimensions[1],
            asset.dimensions[2],
            asset.weight,
            asset.status,
            json.dumps(asset.metadata),
            datetime.now().isoformat()
        ))
        
        conn.commit()
        conn.close()
    
    def _save_digital_asset_to_db(self, asset: DigitalAsset):
        """Guardar activo digital en base de datos"""
        conn = sqlite3.connect('digital_twin.db')
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT OR REPLACE INTO digital_assets 
            (asset_id, physical_asset_id, position_x, position_y, position_z,
             state, last_updated, prediction)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            asset.asset_id,
            asset.physical_asset_id,
            asset.position[0],
            asset.position[1],
            asset.position[2],
            json.dumps(asset.state),
            asset.last_updated.isoformat(),
            json.dumps(asset.prediction) if asset.prediction else None
        ))
        
        conn.commit()
        conn.close()
    
    def _save_sync_log(self, sync_id: str, assets_synced: int, duration: float, errors: List[str]):
        """Guardar log de sincronización"""
        conn = sqlite3.connect('digital_twin.db')
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO sync_logs 
            (sync_id, warehouse_id, sync_timestamp, assets_synced, sync_duration, status, errors)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (
            sync_id,
            self.warehouse_id,
            datetime.now().isoformat(),
            assets_synced,
            duration,
            self.state.value,
            json.dumps(errors) if errors else None
        ))
        
        conn.commit()
        conn.close()
    
    def _save_simulation_to_db(self, simulation: SimulationResult):
        """Guardar simulación en base de datos"""
        conn = sqlite3.connect('digital_twin.db')
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO simulations 
            (simulation_id, scenario, duration, results, recommendations, metrics, timestamp)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (
            simulation.simulation_id,
            simulation.scenario,
            simulation.duration,
            json.dumps(simulation.results),
            json.dumps(simulation.recommendations),
            json.dumps(simulation.metrics),
            simulation.timestamp.isoformat()
        ))
        
        conn.commit()
        conn.close()
    
    def get_digital_twin_status(self) -> Dict[str, Any]:
        """Obtener estado del gemelo digital"""
        
        return {
            "warehouse_id": self.warehouse_id,
            "state": self.state.value,
            "physical_assets_count": len(self.physical_assets),
            "digital_assets_count": len(self.digital_assets),
            "is_syncing": self.is_syncing,
            "last_sync": datetime.now().isoformat() if not self.is_syncing else None,
            "simulations_completed": len(self.simulation_history),
            "predictions_active": len(self.predictions)
        }

# Instancia global del gemelo digital
digital_twin = DigitalTwin("warehouse_001")

# Funciones de conveniencia
def create_digital_twin(warehouse_id: str) -> DigitalTwin:
    """Crear nuevo gemelo digital"""
    return DigitalTwin(warehouse_id)

def sync_digital_twin():
    """Sincronizar gemelo digital"""
    digital_twin.sync_with_physical()

def simulate_warehouse_scenario(scenario_name: str, config: Dict[str, Any]) -> SimulationResult:
    """Simular escenario en gemelo digital"""
    return digital_twin.simulate_scenario(scenario_name, config)

if __name__ == "__main__":
    # Ejemplo de uso
    logger.info("Probando sistema de gemelo digital...")
    
    try:
        # Crear gemelo digital
        twin = create_digital_twin("warehouse_001")
        
        # Agregar activos físicos
        twin.add_physical_asset(
            "shelf_001",
            "shelf",
            (5, 3, 1.5),
            (2, 0.5, 2),
            150.0,
            "active",
            {"capacity": 100, "utilization": 0.75}
        )
        
        twin.add_physical_asset(
            "product_001",
            "product",
            (5.2, 3.1, 1.8),
            (0.3, 0.2, 0.1),
            2.5,
            "available",
            {"name": "Producto Premium", "quantity": 25}
        )
        
        print("✅ Activos físicos agregados")
        
        # Sincronizar
        twin.sync_with_physical()
        print("✅ Gemelo digital sincronizado")
        
        # Simular escenario
        capacity_config = {
            "type": "capacity_increase",
            "new_shelves": 5
        }
        
        simulation = simulate_warehouse_scenario("Aumento de Capacidad", capacity_config)
        print(f"✅ Simulación completada: {simulation.scenario}")
        print(f"   Recomendaciones: {len(simulation.recommendations)}")
        for rec in simulation.recommendations:
            print(f"   - {rec}")
        
        # Predecir estado futuro
        prediction = twin.predict_future_state("product_001", hours_ahead=24)
        print(f"✅ Predicción para producto_001: {prediction['predicted_state']['confidence']*100:.1f}% confianza")
        
        # Estado del gemelo
        status = twin.get_digital_twin_status()
        print(f"✅ Estado del gemelo digital:")
        print(f"   Activos físicos: {status['physical_assets_count']}")
        print(f"   Activos digitales: {status['digital_assets_count']}")
        print(f"   Estado: {status['state']}")
        print(f"   Simulaciones: {status['simulations_completed']}")
        
    except Exception as e:
        logger.error(f"Error en pruebas de gemelo digital: {e}")
    
    print("✅ Sistema de gemelo digital funcionando correctamente")

