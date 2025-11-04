"""
Sistema de Load Balancing Inteligente.

Distribuye carga de trabajo entre múltiples recursos.
"""
import logging
import random
from typing import Dict, Any, List, Optional
from dataclasses import dataclass
from datetime import datetime
from enum import Enum

logger = logging.getLogger(__name__)


class LoadBalanceStrategy(Enum):
    """Estrategias de load balancing."""
    ROUND_ROBIN = "round_robin"
    LEAST_CONNECTIONS = "least_connections"
    LEAST_LOAD = "least_load"
    WEIGHTED = "weighted"
    RANDOM = "random"
    IP_HASH = "ip_hash"


@dataclass
class Resource:
    """Recurso para balanceo."""
    resource_id: str
    name: str
    weight: int = 1  # Para weighted balancing
    current_load: int = 0
    max_capacity: int = 100
    is_healthy: bool = True
    last_health_check: datetime = None
    metadata: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.last_health_check is None:
            self.last_health_check = datetime.now()
        if self.metadata is None:
            self.metadata = {}


class LoadBalancer:
    """Load balancer inteligente."""
    
    def __init__(self, strategy: LoadBalanceStrategy = LoadBalanceStrategy.ROUND_ROBIN):
        """
        Inicializa load balancer.
        
        Args:
            strategy: Estrategia de balanceo
        """
        self.strategy = strategy
        self.resources: Dict[str, Resource] = {}
        self.current_index: Dict[str, int] = {}  # Para round robin
        self.connection_count: Dict[str, int] = {}  # Para least connections
    
    def add_resource(self, resource: Resource):
        """Agrega un recurso."""
        self.resources[resource.resource_id] = resource
        self.connection_count[resource.resource_id] = 0
        logger.info(f"Added resource: {resource.name} (ID: {resource.resource_id})")
    
    def remove_resource(self, resource_id: str):
        """Elimina un recurso."""
        if resource_id in self.resources:
            del self.resources[resource_id]
            if resource_id in self.connection_count:
                del self.connection_count[resource_id]
            logger.info(f"Removed resource: {resource_id}")
    
    def select_resource(self, context: Dict[str, Any] = None) -> Optional[str]:
        """
        Selecciona un recurso según la estrategia.
        
        Args:
            context: Contexto adicional (IP, user_id, etc.)
            
        Returns:
            ID del recurso seleccionado
        """
        # Filtrar recursos saludables
        healthy_resources = [
            r for r in self.resources.values()
            if r.is_healthy and r.current_load < r.max_capacity
        ]
        
        if not healthy_resources:
            logger.warning("No healthy resources available")
            return None
        
        if self.strategy == LoadBalanceStrategy.ROUND_ROBIN:
            return self._round_robin_select(healthy_resources)
        elif self.strategy == LoadBalanceStrategy.LEAST_CONNECTIONS:
            return self._least_connections_select(healthy_resources)
        elif self.strategy == LoadBalanceStrategy.LEAST_LOAD:
            return self._least_load_select(healthy_resources)
        elif self.strategy == LoadBalanceStrategy.WEIGHTED:
            return self._weighted_select(healthy_resources)
        elif self.strategy == LoadBalanceStrategy.RANDOM:
            return self._random_select(healthy_resources)
        elif self.strategy == LoadBalanceStrategy.IP_HASH:
            return self._ip_hash_select(healthy_resources, context)
        else:
            return self._round_robin_select(healthy_resources)
    
    def _round_robin_select(self, resources: List[Resource]) -> str:
        """Selección round robin."""
        resource_ids = [r.resource_id for r in resources]
        
        if "round_robin" not in self.current_index:
            self.current_index["round_robin"] = 0
        
        idx = self.current_index["round_robin"]
        selected_id = resource_ids[idx % len(resource_ids)]
        self.current_index["round_robin"] = (idx + 1) % len(resource_ids)
        
        return selected_id
    
    def _least_connections_select(self, resources: List[Resource]) -> str:
        """Selección por menor número de conexiones."""
        selected = min(
            resources,
            key=lambda r: self.connection_count.get(r.resource_id, 0)
        )
        return selected.resource_id
    
    def _least_load_select(self, resources: List[Resource]) -> str:
        """Selección por menor carga."""
        selected = min(resources, key=lambda r: r.current_load)
        return selected.resource_id
    
    def _weighted_select(self, resources: List[Resource]) -> str:
        """Selección ponderada."""
        total_weight = sum(r.weight for r in resources)
        rand = random.uniform(0, total_weight)
        
        cumulative = 0
        for resource in resources:
            cumulative += resource.weight
            if rand <= cumulative:
                return resource.resource_id
        
        return resources[-1].resource_id
    
    def _random_select(self, resources: List[Resource]) -> str:
        """Selección aleatoria."""
        return random.choice(resources).resource_id
    
    def _ip_hash_select(self, resources: List[Resource], context: Dict[str, Any]) -> str:
        """Selección por hash de IP."""
        client_ip = context.get("client_ip", "unknown") if context else "unknown"
        hash_value = hash(client_ip)
        idx = abs(hash_value) % len(resources)
        return resources[idx].resource_id
    
    def allocate_load(self, resource_id: str, load: int = 1):
        """Asigna carga a un recurso."""
        if resource_id in self.resources:
            self.resources[resource_id].current_load += load
            self.connection_count[resource_id] = self.connection_count.get(resource_id, 0) + 1
    
    def release_load(self, resource_id: str, load: int = 1):
        """Libera carga de un recurso."""
        if resource_id in self.resources:
            self.resources[resource_id].current_load = max(0, self.resources[resource_id].current_load - load)
            self.connection_count[resource_id] = max(0, self.connection_count.get(resource_id, 0) - 1)
    
    def update_resource_health(self, resource_id: str, is_healthy: bool):
        """Actualiza estado de salud de un recurso."""
        if resource_id in self.resources:
            self.resources[resource_id].is_healthy = is_healthy
            self.resources[resource_id].last_health_check = datetime.now()
            logger.info(f"Resource {resource_id} health updated: {is_healthy}")
    
    def get_load_distribution(self) -> Dict[str, Any]:
        """Obtiene distribución de carga."""
        distribution = {}
        
        for resource in self.resources.values():
            load_percentage = (resource.current_load / resource.max_capacity * 100) if resource.max_capacity > 0 else 0
            
            distribution[resource.resource_id] = {
                "name": resource.name,
                "current_load": resource.current_load,
                "max_capacity": resource.max_capacity,
                "load_percentage": load_percentage,
                "is_healthy": resource.is_healthy,
                "connections": self.connection_count.get(resource.resource_id, 0),
                "weight": resource.weight
            }
        
        return {
            "strategy": self.strategy.value,
            "total_resources": len(self.resources),
            "healthy_resources": sum(1 for r in self.resources.values() if r.is_healthy),
            "distribution": distribution
        }

