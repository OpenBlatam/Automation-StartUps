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
import math
from enum import Enum

class VehicleType(Enum):
    """Tipos de vehículos"""
    SMALL_VAN = "small_van"
    MEDIUM_TRUCK = "medium_truck"
    LARGE_TRUCK = "large_truck"
    MOTORCYCLE = "motorcycle"
    BICYCLE = "bicycle"

class DeliveryStatus(Enum):
    """Estado de entrega"""
    PENDING = "pending"
    IN_TRANSIT = "in_transit"
    DELIVERED = "delivered"
    FAILED = "failed"
    RETURNED = "returned"

@dataclass
class Location:
    """Ubicación geográfica"""
    id: str
    name: str
    latitude: float
    longitude: float
    address: str
    delivery_window_start: str  # HH:MM format
    delivery_window_end: str    # HH:MM format
    priority: int  # 1-5, 5 being highest
    is_depot: bool = False

@dataclass
class Vehicle:
    """Vehículo de entrega"""
    id: str
    vehicle_type: VehicleType
    capacity_kg: float
    capacity_volume: float
    fuel_efficiency: float  # km/liter
    driver_id: str
    current_location: Location
    is_available: bool = True
    maintenance_due: Optional[datetime] = None

@dataclass
class DeliveryOrder:
    """Orden de entrega"""
    id: str
    customer_id: str
    products: List[Dict]  # [{'product_id': int, 'quantity': int, 'weight': float}]
    delivery_location: Location
    order_date: datetime
    delivery_date: datetime
    priority: int
    status: DeliveryStatus
    special_instructions: str = ""
    estimated_duration: int = 30  # minutes

@dataclass
class Route:
    """Ruta de entrega"""
    id: str
    vehicle_id: str
    driver_id: str
    orders: List[DeliveryOrder]
    start_location: Location
    end_location: Location
    total_distance: float
    total_duration: int  # minutes
    total_weight: float
    total_volume: float
    fuel_cost: float
    created_at: datetime
    status: str = "planned"

class LogisticsOptimizationService:
    """Servicio de optimización de logística"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.locations = {}
        self.vehicles = {}
        self.delivery_orders = {}
        self.routes = {}
        
        # Configurar ubicaciones por defecto
        self._setup_default_locations()
        self._setup_default_vehicles()
    
    def _setup_default_locations(self):
        """Configura ubicaciones por defecto"""
        locations = [
            Location(
                id="DEPOT_001",
                name="Depósito Principal",
                latitude=40.7128,
                longitude=-74.0060,
                address="123 Main St, New York, NY",
                delivery_window_start="08:00",
                delivery_window_end="18:00",
                priority=5,
                is_depot=True
            ),
            Location(
                id="CUSTOMER_001",
                name="Cliente Centro",
                latitude=40.7589,
                longitude=-73.9851,
                address="456 Broadway, New York, NY",
                delivery_window_start="09:00",
                delivery_window_end="17:00",
                priority=4
            ),
            Location(
                id="CUSTOMER_002",
                name="Cliente Norte",
                latitude=40.7831,
                longitude=-73.9712,
                address="789 5th Ave, New York, NY",
                delivery_window_start="10:00",
                delivery_window_end="16:00",
                priority=3
            ),
            Location(
                id="CUSTOMER_003",
                name="Cliente Sur",
                latitude=40.6892,
                longitude=-74.0445,
                address="321 Wall St, New York, NY",
                delivery_window_start="09:30",
                delivery_window_end="17:30",
                priority=4
            ),
            Location(
                id="CUSTOMER_004",
                name="Cliente Este",
                latitude=40.7282,
                longitude=-73.7949,
                address="654 Queens Blvd, Queens, NY",
                delivery_window_start="11:00",
                delivery_window_end="15:00",
                priority=2
            ),
            Location(
                id="CUSTOMER_005",
                name="Cliente Oeste",
                latitude=40.7505,
                longitude=-74.0014,
                address="987 Hudson St, New York, NY",
                delivery_window_start="10:30",
                delivery_window_end="16:30",
                priority=3
            )
        ]
        
        for location in locations:
            self.locations[location.id] = location
    
    def _setup_default_vehicles(self):
        """Configura vehículos por defecto"""
        depot = self.locations["DEPOT_001"]
        
        vehicles = [
            Vehicle(
                id="VEHICLE_001",
                vehicle_type=VehicleType.SMALL_VAN,
                capacity_kg=1000.0,
                capacity_volume=5.0,
                fuel_efficiency=12.0,
                driver_id="DRIVER_001",
                current_location=depot
            ),
            Vehicle(
                id="VEHICLE_002",
                vehicle_type=VehicleType.MEDIUM_TRUCK,
                capacity_kg=2500.0,
                capacity_volume=12.0,
                fuel_efficiency=8.0,
                driver_id="DRIVER_002",
                current_location=depot
            ),
            Vehicle(
                id="VEHICLE_003",
                vehicle_type=VehicleType.LARGE_TRUCK,
                capacity_kg=5000.0,
                capacity_volume=25.0,
                fuel_efficiency=6.0,
                driver_id="DRIVER_003",
                current_location=depot
            ),
            Vehicle(
                id="VEHICLE_004",
                vehicle_type=VehicleType.MOTORCYCLE,
                capacity_kg=50.0,
                capacity_volume=0.5,
                fuel_efficiency=25.0,
                driver_id="DRIVER_004",
                current_location=depot
            )
        ]
        
        for vehicle in vehicles:
            self.vehicles[vehicle.id] = vehicle
    
    def calculate_distance(self, loc1: Location, loc2: Location) -> float:
        """Calcula distancia entre dos ubicaciones usando fórmula de Haversine"""
        try:
            R = 6371  # Radio de la Tierra en kilómetros
            
            lat1_rad = math.radians(loc1.latitude)
            lat2_rad = math.radians(loc2.latitude)
            delta_lat = math.radians(loc2.latitude - loc1.latitude)
            delta_lon = math.radians(loc2.longitude - loc1.longitude)
            
            a = (math.sin(delta_lat / 2) ** 2 + 
                 math.cos(lat1_rad) * math.cos(lat2_rad) * 
                 math.sin(delta_lon / 2) ** 2)
            c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
            
            distance = R * c
            return distance
            
        except Exception as e:
            self.logger.error(f'Error calculando distancia: {str(e)}')
            return 0.0
    
    def calculate_duration(self, distance: float, vehicle_type: VehicleType) -> int:
        """Calcula duración de viaje en minutos"""
        try:
            # Velocidades promedio por tipo de vehículo (km/h)
            speeds = {
                VehicleType.SMALL_VAN: 30,
                VehicleType.MEDIUM_TRUCK: 25,
                VehicleType.LARGE_TRUCK: 20,
                VehicleType.MOTORCYCLE: 35,
                VehicleType.BICYCLE: 15
            }
            
            speed = speeds.get(vehicle_type, 25)
            duration_hours = distance / speed
            duration_minutes = int(duration_hours * 60)
            
            # Añadir tiempo de entrega (30 minutos por entrega)
            return duration_minutes + 30
            
        except Exception as e:
            self.logger.error(f'Error calculando duración: {str(e)}')
            return 60
    
    def create_delivery_order(self, customer_id: str, products: List[Dict], 
                             delivery_location_id: str, delivery_date: datetime, 
                             priority: int = 3) -> Dict:
        """Crea orden de entrega"""
        try:
            if delivery_location_id not in self.locations:
                return {'error': 'Ubicación de entrega no encontrada'}
            
            delivery_location = self.locations[delivery_location_id]
            
            # Calcular peso y volumen total
            total_weight = sum(product.get('weight', 1.0) * product['quantity'] for product in products)
            total_volume = sum(product.get('volume', 0.1) * product['quantity'] for product in products)
            
            order_id = f"ORDER_{len(self.delivery_orders) + 1:03d}"
            
            delivery_order = DeliveryOrder(
                id=order_id,
                customer_id=customer_id,
                products=products,
                delivery_location=delivery_location,
                order_date=datetime.utcnow(),
                delivery_date=delivery_date,
                priority=priority,
                status=DeliveryStatus.PENDING,
                estimated_duration=30
            )
            
            self.delivery_orders[order_id] = delivery_order
            
            return {
                'success': True,
                'order_id': order_id,
                'delivery_order': {
                    'id': delivery_order.id,
                    'customer_id': delivery_order.customer_id,
                    'products': delivery_order.products,
                    'delivery_location': {
                        'id': delivery_location.id,
                        'name': delivery_location.name,
                        'address': delivery_location.address
                    },
                    'delivery_date': delivery_order.delivery_date.isoformat(),
                    'priority': delivery_order.priority,
                    'status': delivery_order.status.value
                }
            }
            
        except Exception as e:
            self.logger.error(f'Error creando orden de entrega: {str(e)}')
            return {'error': str(e)}
    
    def optimize_routes(self, date: datetime = None) -> Dict:
        """Optimiza rutas de entrega"""
        try:
            if date is None:
                date = datetime.utcnow().date()
            
            # Obtener órdenes pendientes para la fecha
            pending_orders = [
                order for order in self.delivery_orders.values()
                if order.status == DeliveryStatus.PENDING and 
                   order.delivery_date.date() == date
            ]
            
            if not pending_orders:
                return {'error': 'No hay órdenes pendientes para esta fecha'}
            
            # Obtener vehículos disponibles
            available_vehicles = [
                vehicle for vehicle in self.vehicles.values()
                if vehicle.is_available
            ]
            
            if not available_vehicles:
                return {'error': 'No hay vehículos disponibles'}
            
            # Algoritmo de optimización simple (Closest Neighbor)
            routes = []
            remaining_orders = pending_orders.copy()
            
            for vehicle in available_vehicles:
                if not remaining_orders:
                    break
                
                # Crear ruta para este vehículo
                route_orders = []
                current_location = vehicle.current_location
                total_weight = 0.0
                total_volume = 0.0
                total_distance = 0.0
                total_duration = 0
                
                # Seleccionar órdenes que quepan en el vehículo
                vehicle_orders = []
                for order in remaining_orders:
                    order_weight = sum(product.get('weight', 1.0) * product['quantity'] for product in order.products)
                    order_volume = sum(product.get('volume', 0.1) * product['quantity'] for product in order.products)
                    
                    if (total_weight + order_weight <= vehicle.capacity_kg and 
                        total_volume + order_volume <= vehicle.capacity_volume):
                        vehicle_orders.append(order)
                
                # Ordenar por prioridad y distancia
                vehicle_orders.sort(key=lambda o: (o.priority, self.calculate_distance(current_location, o.delivery_location)))
                
                # Construir ruta usando algoritmo del vecino más cercano
                for order in vehicle_orders:
                    distance = self.calculate_distance(current_location, order.delivery_location)
                    duration = self.calculate_duration(distance, vehicle.vehicle_type)
                    
                    route_orders.append(order)
                    total_distance += distance
                    total_duration += duration
                    total_weight += sum(product.get('weight', 1.0) * product['quantity'] for product in order.products)
                    total_volume += sum(product.get('volume', 0.1) * product['quantity'] for product in order.products)
                    
                    current_location = order.delivery_location
                    
                    # Remover de órdenes pendientes
                    remaining_orders.remove(order)
                
                # Calcular costo de combustible
                fuel_cost = (total_distance / vehicle.fuel_efficiency) * 1.5  # $1.5 por litro
                
                if route_orders:
                    route_id = f"ROUTE_{len(routes) + 1:03d}"
                    
                    route = Route(
                        id=route_id,
                        vehicle_id=vehicle.id,
                        driver_id=vehicle.driver_id,
                        orders=route_orders,
                        start_location=vehicle.current_location,
                        end_location=route_orders[-1].delivery_location,
                        total_distance=total_distance,
                        total_duration=total_duration,
                        total_weight=total_weight,
                        total_volume=total_volume,
                        fuel_cost=fuel_cost,
                        created_at=datetime.utcnow()
                    )
                    
                    routes.append(route)
                    self.routes[route_id] = route
            
            return {
                'success': True,
                'routes_created': len(routes),
                'routes': [
                    {
                        'id': route.id,
                        'vehicle_id': route.vehicle_id,
                        'driver_id': route.driver_id,
                        'orders_count': len(route.orders),
                        'total_distance': route.total_distance,
                        'total_duration': route.total_duration,
                        'total_weight': route.total_weight,
                        'total_volume': route.total_volume,
                        'fuel_cost': route.fuel_cost,
                        'orders': [
                            {
                                'id': order.id,
                                'customer_id': order.customer_id,
                                'delivery_location': order.delivery_location.name,
                                'priority': order.priority
                            } for order in route.orders
                        ]
                    } for route in routes
                ],
                'unassigned_orders': len(remaining_orders)
            }
            
        except Exception as e:
            self.logger.error(f'Error optimizando rutas: {str(e)}')
            return {'error': str(e)}
    
    def get_route_details(self, route_id: str) -> Dict:
        """Obtiene detalles de una ruta"""
        try:
            if route_id not in self.routes:
                return {'error': 'Ruta no encontrada'}
            
            route = self.routes[route_id]
            vehicle = self.vehicles[route.vehicle_id]
            
            # Calcular estadísticas detalladas
            route_stats = {
                'id': route.id,
                'vehicle': {
                    'id': vehicle.id,
                    'type': vehicle.vehicle_type.value,
                    'capacity_kg': vehicle.capacity_kg,
                    'capacity_volume': vehicle.capacity_volume,
                    'fuel_efficiency': vehicle.fuel_efficiency
                },
                'driver_id': route.driver_id,
                'orders': [],
                'total_distance': route.total_distance,
                'total_duration': route.total_duration,
                'total_weight': route.total_weight,
                'total_volume': route.total_volume,
                'fuel_cost': route.fuel_cost,
                'efficiency': {
                    'weight_utilization': (route.total_weight / vehicle.capacity_kg) * 100,
                    'volume_utilization': (route.total_volume / vehicle.capacity_volume) * 100,
                    'distance_per_order': route.total_distance / len(route.orders) if route.orders else 0
                },
                'created_at': route.created_at.isoformat(),
                'status': route.status
            }
            
            # Detalles de órdenes
            current_location = route.start_location
            for i, order in enumerate(route.orders):
                distance = self.calculate_distance(current_location, order.delivery_location)
                duration = self.calculate_duration(distance, vehicle.vehicle_type)
                
                route_stats['orders'].append({
                    'sequence': i + 1,
                    'order_id': order.id,
                    'customer_id': order.customer_id,
                    'delivery_location': {
                        'id': order.delivery_location.id,
                        'name': order.delivery_location.name,
                        'address': order.delivery_location.address,
                        'latitude': order.delivery_location.latitude,
                        'longitude': order.delivery_location.longitude
                    },
                    'products': order.products,
                    'priority': order.priority,
                    'delivery_window': f"{order.delivery_location.delivery_window_start} - {order.delivery_location.delivery_window_end}",
                    'distance_from_previous': distance,
                    'estimated_duration': duration,
                    'special_instructions': order.special_instructions
                })
                
                current_location = order.delivery_location
            
            return {
                'success': True,
                'route': route_stats
            }
            
        except Exception as e:
            self.logger.error(f'Error obteniendo detalles de ruta: {str(e)}')
            return {'error': str(e)}
    
    def get_logistics_dashboard(self) -> Dict:
        """Obtiene datos para dashboard de logística"""
        try:
            # Estadísticas de vehículos
            total_vehicles = len(self.vehicles)
            available_vehicles = len([v for v in self.vehicles.values() if v.is_available])
            
            # Estadísticas de órdenes
            total_orders = len(self.delivery_orders)
            pending_orders = len([o for o in self.delivery_orders.values() if o.status == DeliveryStatus.PENDING])
            in_transit_orders = len([o for o in self.delivery_orders.values() if o.status == DeliveryStatus.IN_TRANSIT])
            delivered_orders = len([o for o in self.delivery_orders.values() if o.status == DeliveryStatus.DELIVERED])
            
            # Estadísticas de rutas
            total_routes = len(self.routes)
            planned_routes = len([r for r in self.routes.values() if r.status == "planned"])
            active_routes = len([r for r in self.routes.values() if r.status == "active"])
            
            # Métricas de eficiencia
            total_distance = sum(route.total_distance for route in self.routes.values())
            total_fuel_cost = sum(route.fuel_cost for route in self.routes.values())
            total_duration = sum(route.total_duration for route in self.routes.values())
            
            # Rutas recientes
            recent_routes = sorted(self.routes.values(), key=lambda r: r.created_at, reverse=True)[:5]
            
            return {
                'success': True,
                'dashboard': {
                    'vehicles': {
                        'total': total_vehicles,
                        'available': available_vehicles,
                        'utilization_rate': ((total_vehicles - available_vehicles) / total_vehicles * 100) if total_vehicles > 0 else 0
                    },
                    'orders': {
                        'total': total_orders,
                        'pending': pending_orders,
                        'in_transit': in_transit_orders,
                        'delivered': delivered_orders,
                        'delivery_rate': (delivered_orders / total_orders * 100) if total_orders > 0 else 0
                    },
                    'routes': {
                        'total': total_routes,
                        'planned': planned_routes,
                        'active': active_routes
                    },
                    'efficiency': {
                        'total_distance_km': total_distance,
                        'total_fuel_cost': total_fuel_cost,
                        'total_duration_hours': total_duration / 60,
                        'average_distance_per_route': total_distance / total_routes if total_routes > 0 else 0,
                        'average_cost_per_route': total_fuel_cost / total_routes if total_routes > 0 else 0
                    },
                    'recent_routes': [
                        {
                            'id': route.id,
                            'vehicle_id': route.vehicle_id,
                            'orders_count': len(route.orders),
                            'total_distance': route.total_distance,
                            'fuel_cost': route.fuel_cost,
                            'created_at': route.created_at.isoformat()
                        } for route in recent_routes
                    ]
                }
            }
            
        except Exception as e:
            self.logger.error(f'Error obteniendo dashboard de logística: {str(e)}')
            return {'error': str(e)}
    
    def update_delivery_status(self, order_id: str, status: DeliveryStatus) -> Dict:
        """Actualiza estado de entrega"""
        try:
            if order_id not in self.delivery_orders:
                return {'error': 'Orden no encontrada'}
            
            order = self.delivery_orders[order_id]
            order.status = status
            
            return {
                'success': True,
                'order_id': order_id,
                'new_status': status.value,
                'updated_at': datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f'Error actualizando estado de entrega: {str(e)}')
            return {'error': str(e)}
    
    def get_vehicle_status(self) -> Dict:
        """Obtiene estado de vehículos"""
        try:
            vehicles_data = []
            
            for vehicle_id, vehicle in self.vehicles.items():
                vehicles_data.append({
                    'id': vehicle.id,
                    'vehicle_type': vehicle.vehicle_type.value,
                    'capacity_kg': vehicle.capacity_kg,
                    'capacity_volume': vehicle.capacity_volume,
                    'fuel_efficiency': vehicle.fuel_efficiency,
                    'driver_id': vehicle.driver_id,
                    'current_location': {
                        'id': vehicle.current_location.id,
                        'name': vehicle.current_location.name,
                        'address': vehicle.current_location.address
                    },
                    'is_available': vehicle.is_available,
                    'maintenance_due': vehicle.maintenance_due.isoformat() if vehicle.maintenance_due else None
                })
            
            return {
                'success': True,
                'vehicles': vehicles_data,
                'total_vehicles': len(vehicles_data),
                'available_vehicles': len([v for v in vehicles_data if v['is_available']])
            }
            
        except Exception as e:
            self.logger.error(f'Error obteniendo estado de vehículos: {str(e)}')
            return {'error': str(e)}

# Instancia global del servicio de logística
logistics_optimization_service = LogisticsOptimizationService()



