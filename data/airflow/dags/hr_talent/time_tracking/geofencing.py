"""
Sistema de Geofencing para Validación de Ubicación
Valida que los clock in/out se realicen desde ubicaciones autorizadas
"""

import logging
from typing import Optional, Dict, Any, Tuple
from decimal import Decimal
import math

logger = logging.getLogger(__name__)


class GeofencingValidator:
    """Valida ubicaciones usando geofencing"""
    
    # Radio de la Tierra en kilómetros
    EARTH_RADIUS_KM = 6371.0
    
    def __init__(self, storage):
        self.storage = storage
    
    def calculate_distance(
        self,
        lat1: float,
        lon1: float,
        lat2: float,
        lon2: float
    ) -> float:
        """
        Calcula distancia entre dos puntos GPS usando fórmula de Haversine
        
        Returns:
            Distancia en kilómetros
        """
        # Convertir a radianes
        lat1_rad = math.radians(lat1)
        lat2_rad = math.radians(lat2)
        delta_lat = math.radians(lat2 - lat1)
        delta_lon = math.radians(lon2 - lon1)
        
        # Fórmula de Haversine
        a = (
            math.sin(delta_lat / 2) ** 2 +
            math.cos(lat1_rad) * math.cos(lat2_rad) *
            math.sin(delta_lon / 2) ** 2
        )
        c = 2 * math.asin(math.sqrt(a))
        distance = self.EARTH_RADIUS_KM * c
        
        return distance
    
    def is_within_radius(
        self,
        lat: float,
        lon: float,
        center_lat: float,
        center_lon: float,
        radius_km: float = 0.5
    ) -> bool:
        """
        Verifica si un punto está dentro de un radio
        
        Args:
            lat, lon: Coordenadas del punto a verificar
            center_lat, center_lon: Coordenadas del centro
            radius_km: Radio permitido en kilómetros (default: 500m)
        
        Returns:
            True si está dentro del radio
        """
        distance = self.calculate_distance(lat, lon, center_lat, center_lon)
        return distance <= radius_km
    
    def get_employee_authorized_locations(
        self,
        employee_id: str
    ) -> list[Dict[str, Any]]:
        """Obtiene ubicaciones autorizadas para un empleado"""
        sql = """
            SELECT 
                location_name,
                latitude,
                longitude,
                allowed_radius_km,
                is_active
            FROM time_tracking_authorized_locations
            WHERE employee_id = %s AND is_active = true
        """
        
        results = self.storage.hook.get_records(sql, parameters=(employee_id,))
        
        locations = []
        for row in results:
            locations.append({
                "name": row[0],
                "latitude": float(row[1]),
                "longitude": float(row[2]),
                "radius_km": float(row[3]) if row[3] else 0.5,
                "active": row[4]
            })
        
        return locations
    
    def validate_location(
        self,
        employee_id: str,
        latitude: Optional[float],
        longitude: Optional[float],
        location_name: Optional[str] = None
    ) -> Tuple[bool, Optional[str], Optional[Dict[str, Any]]]:
        """
        Valida que la ubicación esté autorizada
        
        Returns:
            (is_valid, error_message, matched_location)
        """
        # Si no hay coordenadas GPS, verificar por nombre de ubicación
        if latitude is None or longitude is None:
            if location_name:
                # Verificar si el nombre de ubicación está autorizado
                sql = """
                    SELECT latitude, longitude, allowed_radius_km
                    FROM time_tracking_authorized_locations
                    WHERE employee_id = %s
                        AND location_name = %s
                        AND is_active = true
                """
                result = self.storage.hook.get_first(
                    sql,
                    parameters=(employee_id, location_name)
                )
                
                if result:
                    return True, None, {
                        "name": location_name,
                        "latitude": float(result[0]),
                        "longitude": float(result[1])
                    }
                else:
                    return False, f"Location '{location_name}' not authorized", None
            
            # Si no hay coordenadas ni nombre, permitir (puede ser trabajo remoto)
            return True, None, None
        
        # Validar con GPS
        authorized_locations = self.get_employee_authorized_locations(employee_id)
        
        if not authorized_locations:
            # Si no hay ubicaciones autorizadas, permitir (trabajo remoto)
            return True, None, None
        
        # Verificar si está dentro de alguna ubicación autorizada
        for loc in authorized_locations:
            if self.is_within_radius(
                latitude,
                longitude,
                loc["latitude"],
                loc["longitude"],
                loc["radius_km"]
            ):
                return True, None, loc
        
        # No está dentro de ninguna ubicación autorizada
        nearest = self._find_nearest_location(
            latitude, longitude, authorized_locations
        )
        distance = self.calculate_distance(
            latitude, longitude,
            nearest["latitude"], nearest["longitude"]
        )
        
        return (
            False,
            f"Location not authorized. Nearest: {nearest['name']} ({distance:.2f} km away)",
            nearest
        )
    
    def _find_nearest_location(
        self,
        lat: float,
        lon: float,
        locations: list[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Encuentra la ubicación autorizada más cercana"""
        if not locations:
            return {"name": "Unknown", "latitude": 0, "longitude": 0}
        
        nearest = None
        min_distance = float('inf')
        
        for loc in locations:
            distance = self.calculate_distance(
                lat, lon,
                loc["latitude"], loc["longitude"]
            )
            if distance < min_distance:
                min_distance = distance
                nearest = loc
        
        return nearest or locations[0]

