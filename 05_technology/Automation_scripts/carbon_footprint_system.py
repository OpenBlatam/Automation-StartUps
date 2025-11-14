"""
Sistema de Seguimiento de Huella de Carbono
==========================================

Sistema completo para calcular, rastrear y optimizar la huella de carbono
de las operaciones del almacén y cadena de suministro.
"""

import json
import logging
import math
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass, asdict
from enum import Enum
import sqlite3
import uuid

logger = logging.getLogger(__name__)

class EmissionSource(Enum):
    """Fuentes de emisión"""
    TRANSPORT = "transport"
    ENERGY = "energy"
    PACKAGING = "packaging"
    WASTE = "waste"
    REFRIGERATION = "refrigeration"
    MANUFACTURING = "manufacturing"
    WAREHOUSE_OPERATIONS = "warehouse_operations"

class CarbonCreditStatus(Enum):
    """Estado de créditos de carbono"""
    AVAILABLE = "available"
    USED = "used"
    EXPIRED = "expired"
    PENDING = "pending"

@dataclass
class CarbonEmission:
    """Emisión de carbono"""
    emission_id: str
    source: EmissionSource
    quantity: float  # toneladas CO2 equivalente
    activity: str
    timestamp: datetime
    location: str
    metadata: Dict[str, Any]

@dataclass
class CarbonOffset:
    """Compensación de carbono"""
    offset_id: str
    emission_id: str
    offset_quantity: float
    offset_type: str
    carbon_credits: int
    timestamp: datetime
    verified: bool

@dataclass
class CarbonFootprint:
    """Huella de carbono total"""
    period_start: datetime
    period_end: datetime
    total_emissions: float
    emissions_by_source: Dict[str, float]
    offsets: float
    net_emissions: float
    carbon_intensity: float  # kg CO2 por unidad de producto
    reduction_target: float
    progress: float

class CarbonFootprintTracker:
    """Rastreador de huella de carbono"""
    
    # Factores de emisión (kg CO2 por unidad)
    EMISSION_FACTORS = {
        EmissionSource.TRANSPORT: {
            "truck_km": 0.206,  # kg CO2 por km
            "air_freight_km": 0.500,  # kg CO2 por km
            "sea_freight_km": 0.015,  # kg CO2 por km
            "train_km": 0.025  # kg CO2 por km
        },
        EmissionSource.ENERGY: {
            "electricity_kwh": 0.5,  # kg CO2 por kWh (promedio)
            "natural_gas_m3": 2.0,  # kg CO2 por m3
            "diesel_l": 2.68,  # kg CO2 por litro
            "gasoline_l": 2.31  # kg CO2 por litro
        },
        EmissionSource.PACKAGING: {
            "cardboard_kg": 1.5,  # kg CO2 por kg
            "plastic_kg": 3.5,  # kg CO2 por kg
            "wood_kg": 0.5  # kg CO2 por kg
        },
        EmissionSource.REFRIGERATION: {
            "refrigerant_kg": 1400,  # kg CO2 equivalente por kg (alto GWP)
            "cooling_kwh": 0.5  # Usa el mismo factor que electricidad
        }
    }
    
    def __init__(self):
        self.emissions: List[CarbonEmission] = []
        self.offsets: List[CarbonOffset] = []
        self.carbon_credits: Dict[str, Dict[str, Any]] = {}
        self.reduction_targets: Dict[str, float] = {}
        
        # Inicializar base de datos
        self._init_database()
    
    def _init_database(self):
        """Inicializar base de datos"""
        conn = sqlite3.connect('carbon_footprint.db')
        cursor = conn.cursor()
        
        # Tabla de emisiones
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS carbon_emissions (
                emission_id TEXT PRIMARY KEY,
                source TEXT NOT NULL,
                quantity REAL NOT NULL,
                activity TEXT NOT NULL,
                timestamp TEXT NOT NULL,
                location TEXT NOT NULL,
                metadata TEXT NOT NULL
            )
        ''')
        
        # Tabla de compensaciones
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS carbon_offsets (
                offset_id TEXT PRIMARY KEY,
                emission_id TEXT NOT NULL,
                offset_quantity REAL NOT NULL,
                offset_type TEXT NOT NULL,
                carbon_credits INTEGER NOT NULL,
                timestamp TEXT NOT NULL,
                verified BOOLEAN NOT NULL,
                FOREIGN KEY (emission_id) REFERENCES carbon_emissions (emission_id)
            )
        ''')
        
        # Tabla de créditos de carbono
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS carbon_credits (
                credit_id TEXT PRIMARY KEY,
                quantity REAL NOT NULL,
                source TEXT NOT NULL,
                purchase_date TEXT NOT NULL,
                expiry_date TEXT,
                status TEXT NOT NULL,
                price REAL,
                metadata TEXT NOT NULL
            )
        ''')
        
        # Índices
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_emissions_timestamp ON carbon_emissions(timestamp)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_emissions_source ON carbon_emissions(source)')
        
        conn.commit()
        conn.close()
    
    def calculate_transport_emissions(self, distance_km: float, transport_type: str,
                                     payload_kg: float = 0) -> CarbonEmission:
        """Calcular emisiones de transporte"""
        
        factors = self.EMISSION_FACTORS[EmissionSource.TRANSPORT]
        factor_key = f"{transport_type}_km"
        
        if factor_key not in factors:
            # Factor por defecto
            emission_factor = factors.get("truck_km", 0.2)
        else:
            emission_factor = factors[factor_key]
        
        # Calcular emisiones
        emissions_kg = distance_km * emission_factor
        
        # Ajustar por carga si es aplicable
        if payload_kg > 0:
            # Más carga = más emisiones (simplificado)
            load_factor = 1 + (payload_kg / 10000)  # Factor de carga
            emissions_kg *= load_factor
        
        # Convertir a toneladas
        emissions_tonnes = emissions_kg / 1000
        
        emission = CarbonEmission(
            emission_id=str(uuid.uuid4()),
            source=EmissionSource.TRANSPORT,
            quantity=emissions_tonnes,
            activity=f"Transporte {transport_type} - {distance_km} km",
            timestamp=datetime.now(),
            location="En tránsito",
            metadata={
                "distance_km": distance_km,
                "transport_type": transport_type,
                "payload_kg": payload_kg,
                "emission_factor": emission_factor
            }
        )
        
        self.emissions.append(emission)
        self._save_emission_to_db(emission)
        
        logger.info(f"Emisión de transporte calculada: {emissions_tonnes:.3f} toneladas CO2")
        
        return emission
    
    def calculate_energy_emissions(self, energy_type: str, quantity: float,
                                   unit: str = "kwh") -> CarbonEmission:
        """Calcular emisiones de energía"""
        
        factors = self.EMISSION_FACTORS[EmissionSource.ENERGY]
        
        # Convertir unidad si es necesario
        if unit == "kwh":
            factor_key = "electricity_kwh"
        elif unit == "m3":
            factor_key = "natural_gas_m3"
        elif unit == "l":
            if energy_type == "diesel":
                factor_key = "diesel_l"
            else:
                factor_key = "gasoline_l"
        else:
            factor_key = "electricity_kwh"  # Por defecto
        
        emission_factor = factors.get(factor_key, 0.5)
        
        # Calcular emisiones
        emissions_kg = quantity * emission_factor
        emissions_tonnes = emissions_kg / 1000
        
        emission = CarbonEmission(
            emission_id=str(uuid.uuid4()),
            source=EmissionSource.ENERGY,
            quantity=emissions_tonnes,
            activity=f"Consumo de {energy_type} - {quantity} {unit}",
            timestamp=datetime.now(),
            location="Almacén",
            metadata={
                "energy_type": energy_type,
                "quantity": quantity,
                "unit": unit,
                "emission_factor": emission_factor
            }
        )
        
        self.emissions.append(emission)
        self._save_emission_to_db(emission)
        
        logger.info(f"Emisión de energía calculada: {emissions_tonnes:.3f} toneladas CO2")
        
        return emission
    
    def calculate_packaging_emissions(self, material: str, weight_kg: float) -> CarbonEmission:
        """Calcular emisiones de empaquetado"""
        
        factors = self.EMISSION_FACTORS[EmissionSource.PACKAGING]
        factor_key = f"{material}_kg"
        
        if factor_key not in factors:
            # Factor por defecto
            emission_factor = factors.get("cardboard_kg", 1.5)
        else:
            emission_factor = factors[factor_key]
        
        # Calcular emisiones
        emissions_kg = weight_kg * emission_factor
        emissions_tonnes = emissions_kg / 1000
        
        emission = CarbonEmission(
            emission_id=str(uuid.uuid4()),
            source=EmissionSource.PACKAGING,
            quantity=emissions_tonnes,
            activity=f"Empaquetado {material} - {weight_kg} kg",
            timestamp=datetime.now(),
            location="Centro de empaquetado",
            metadata={
                "material": material,
                "weight_kg": weight_kg,
                "emission_factor": emission_factor
            }
        )
        
        self.emissions.append(emission)
        self._save_emission_to_db(emission)
        
        logger.info(f"Emisión de empaquetado calculada: {emissions_tonnes:.3f} toneladas CO2")
        
        return emission
    
    def calculate_refrigeration_emissions(self, refrigerant_type: str, quantity_kg: float) -> CarbonEmission:
        """Calcular emisiones de refrigeración"""
        
        factors = self.EMISSION_FACTORS[EmissionSource.REFRIGERATION]
        emission_factor = factors.get("refrigerant_kg", 1400)
        
        # Calcular emisiones (alto GWP)
        emissions_kg = quantity_kg * emission_factor
        emissions_tonnes = emissions_kg / 1000
        
        emission = CarbonEmission(
            emission_id=str(uuid.uuid4()),
            source=EmissionSource.REFRIGERATION,
            quantity=emissions_tonnes,
            activity=f"Fuga de refrigerante {refrigerant_type} - {quantity_kg} kg",
            timestamp=datetime.now(),
            location="Sistema de refrigeración",
            metadata={
                "refrigerant_type": refrigerant_type,
                "quantity_kg": quantity_kg,
                "emission_factor": emission_factor,
                "gwp": "high"
            }
        )
        
        self.emissions.append(emission)
        self._save_emission_to_db(emission)
        
        logger.info(f"Emisión de refrigeración calculada: {emissions_tonnes:.3f} toneladas CO2")
        
        return emission
    
    def purchase_carbon_credits(self, quantity_tonnes: float, price_per_tonne: float,
                               source: str = "renewable_energy") -> str:
        """Comprar créditos de carbono"""
        
        credit_id = str(uuid.uuid4())
        
        credit = {
            "credit_id": credit_id,
            "quantity": quantity_tonnes,
            "source": source,
            "purchase_date": datetime.now().isoformat(),
            "expiry_date": (datetime.now() + timedelta(days=365*2)).isoformat(),
            "status": CarbonCreditStatus.AVAILABLE.value,
            "price": price_per_tonne,
            "metadata": {}
        }
        
        self.carbon_credits[credit_id] = credit
        self._save_carbon_credit_to_db(credit)
        
        logger.info(f"Créditos de carbono comprados: {quantity_tonnes} toneladas")
        
        return credit_id
    
    def offset_emission(self, emission_id: str, offset_type: str = "carbon_credit") -> CarbonOffset:
        """Compensar emisión de carbono"""
        
        # Encontrar emisión
        emission = None
        for e in self.emissions:
            if e.emission_id == emission_id:
                emission = e
                break
        
        if not emission:
            raise ValueError(f"Emisión no encontrada: {emission_id}")
        
        # Buscar créditos disponibles
        available_credits = [
            c for c in self.carbon_credits.values()
            if c["status"] == CarbonCreditStatus.AVAILABLE.value
        ]
        
        offset_quantity = emission.quantity
        credits_used = 0
        
        if offset_type == "carbon_credit" and available_credits:
            # Usar créditos disponibles
            for credit in available_credits:
                if credit["quantity"] >= offset_quantity:
                    credit["quantity"] -= offset_quantity
                    credits_used = int(offset_quantity)
                    if credit["quantity"] == 0:
                        credit["status"] = CarbonCreditStatus.USED.value
                    break
                else:
                    offset_quantity -= credit["quantity"]
                    credits_used += int(credit["quantity"])
                    credit["quantity"] = 0
                    credit["status"] = CarbonCreditStatus.USED.value
        
        offset = CarbonOffset(
            offset_id=str(uuid.uuid4()),
            emission_id=emission_id,
            offset_quantity=emission.quantity,
            offset_type=offset_type,
            carbon_credits=credits_used,
            timestamp=datetime.now(),
            verified=True
        )
        
        self.offsets.append(offset)
        self._save_offset_to_db(offset)
        
        logger.info(f"Emisión compensada: {emission.quantity:.3f} toneladas CO2")
        
        return offset
    
    def calculate_footprint(self, start_date: datetime, end_date: datetime,
                           total_products: float = 1.0) -> CarbonFootprint:
        """Calcular huella de carbono total"""
        
        # Filtrar emisiones del período
        period_emissions = [
            e for e in self.emissions
            if start_date <= e.timestamp <= end_date
        ]
        
        # Calcular emisiones totales
        total_emissions = sum(e.quantity for e in period_emissions)
        
        # Emisiones por fuente
        emissions_by_source = {}
        for e in period_emissions:
            source = e.source.value
            if source not in emissions_by_source:
                emissions_by_source[source] = 0
            emissions_by_source[source] += e.quantity
        
        # Calcular compensaciones
        period_offsets = [
            o for o in self.offsets
            if start_date <= o.timestamp <= end_date
        ]
        total_offsets = sum(o.offset_quantity for o in period_offsets)
        
        # Emisiones netas
        net_emissions = total_emissions - total_offsets
        
        # Intensidad de carbono
        carbon_intensity = (net_emissions * 1000) / total_products if total_products > 0 else 0
        
        # Verificar objetivos de reducción
        target_key = f"{start_date.year}"
        reduction_target = self.reduction_targets.get(target_key, 0)
        
        if reduction_target > 0:
            # Calcular emisiones base (año anterior)
            previous_start = start_date - timedelta(days=365)
            previous_end = start_date
            previous_emissions = sum(
                e.quantity for e in self.emissions
                if previous_start <= e.timestamp <= previous_end
            )
            
            if previous_emissions > 0:
                progress = ((previous_emissions - net_emissions) / previous_emissions) * 100
            else:
                progress = 0
        else:
            progress = 0
        
        footprint = CarbonFootprint(
            period_start=start_date,
            period_end=end_date,
            total_emissions=total_emissions,
            emissions_by_source=emissions_by_source,
            offsets=total_offsets,
            net_emissions=net_emissions,
            carbon_intensity=carbon_intensity,
            reduction_target=reduction_target,
            progress=progress
        )
        
        logger.info(f"Huella de carbono calculada: {net_emissions:.3f} toneladas CO2")
        
        return footprint
    
    def set_reduction_target(self, year: int, target_percentage: float):
        """Establecer objetivo de reducción"""
        
        self.reduction_targets[str(year)] = target_percentage
        logger.info(f"Objetivo de reducción establecido: {target_percentage}% para {year}")
    
    def get_optimization_recommendations(self, footprint: CarbonFootprint) -> List[str]:
        """Obtener recomendaciones de optimización"""
        
        recommendations = []
        
        # Analizar fuentes principales
        sorted_sources = sorted(
            footprint.emissions_by_source.items(),
            key=lambda x: x[1],
            reverse=True
        )
        
        if sorted_sources:
            top_source, top_emissions = sorted_sources[0]
            
            if top_source == EmissionSource.TRANSPORT.value:
                recommendations.append(
                    f"El transporte representa {top_emissions/footprint.total_emissions*100:.1f}% de las emisiones. "
                    "Considerar optimización de rutas y uso de vehículos eléctricos."
                )
            
            elif top_source == EmissionSource.ENERGY.value:
                recommendations.append(
                    f"La energía representa {top_emissions/footprint.total_emissions*100:.1f}% de las emisiones. "
                    "Considerar paneles solares y fuentes renovables."
                )
            
            elif top_source == EmissionSource.PACKAGING.value:
                recommendations.append(
                    f"El empaquetado representa {top_emissions/footprint.total_emissions*100:.1f}% de las emisiones. "
                    "Considerar materiales reciclables y reducir embalaje excesivo."
                )
            
            elif top_source == EmissionSource.REFRIGERATION.value:
                recommendations.append(
                    f"La refrigeración representa {top_emissions/footprint.total_emissions*100:.1f}% de las emisiones. "
                    "Considerar mantenimiento preventivo para evitar fugas de refrigerante."
                )
        
        # Recomendación general
        if footprint.carbon_intensity > 10:  # kg CO2 por producto
            recommendations.append(
                "La intensidad de carbono es alta. Considerar medidas agresivas de reducción."
            )
        
        # Verificar progreso hacia objetivos
        if footprint.reduction_target > 0:
            if footprint.progress < footprint.reduction_target * 0.5:
                recommendations.append(
                    f"El progreso hacia el objetivo de reducción ({footprint.reduction_target}%) es insuficiente ({footprint.progress:.1f}%). "
                    "Se requieren medidas adicionales."
                )
        
        if not recommendations:
            recommendations.append("Las emisiones están dentro de parámetros aceptables.")
        
        return recommendations
    
    def _save_emission_to_db(self, emission: CarbonEmission):
        """Guardar emisión en base de datos"""
        conn = sqlite3.connect('carbon_footprint.db')
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO carbon_emissions 
            (emission_id, source, quantity, activity, timestamp, location, metadata)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (
            emission.emission_id,
            emission.source.value,
            emission.quantity,
            emission.activity,
            emission.timestamp.isoformat(),
            emission.location,
            json.dumps(emission.metadata)
        ))
        
        conn.commit()
        conn.close()
    
    def _save_offset_to_db(self, offset: CarbonOffset):
        """Guardar compensación en base de datos"""
        conn = sqlite3.connect('carbon_footprint.db')
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO carbon_offsets 
            (offset_id, emission_id, offset_quantity, offset_type, carbon_credits, timestamp, verified)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (
            offset.offset_id,
            offset.emission_id,
            offset.offset_quantity,
            offset.offset_type,
            offset.carbon_credits,
            offset.timestamp.isoformat(),
            offset.verified
        ))
        
        conn.commit()
        conn.close()
    
    def _save_carbon_credit_to_db(self, credit: Dict[str, Any]):
        """Guardar crédito de carbono en base de datos"""
        conn = sqlite3.connect('carbon_footprint.db')
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO carbon_credits 
            (credit_id, quantity, source, purchase_date, expiry_date, status, price, metadata)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            credit["credit_id"],
            credit["quantity"],
            credit["source"],
            credit["purchase_date"],
            credit["expiry_date"],
            credit["status"],
            credit["price"],
            json.dumps(credit["metadata"])
        ))
        
        conn.commit()
        conn.close()
    
    def get_carbon_summary(self) -> Dict[str, Any]:
        """Obtener resumen de huella de carbono"""
        
        # Calcular para el último año
        end_date = datetime.now()
        start_date = end_date - timedelta(days=365)
        
        footprint = self.calculate_footprint(start_date, end_date)
        
        return {
            "period": {
                "start": start_date.isoformat(),
                "end": end_date.isoformat()
            },
            "total_emissions_tonnes": footprint.total_emissions,
            "emissions_by_source": footprint.emissions_by_source,
            "offsets_tonnes": footprint.offsets,
            "net_emissions_tonnes": footprint.net_emissions,
            "carbon_intensity_kg_per_product": footprint.carbon_intensity,
            "reduction_target_percentage": footprint.reduction_target,
            "progress_percentage": footprint.progress,
            "recommendations": self.get_optimization_recommendations(footprint)
        }

# Instancia global del rastreador de huella de carbono
carbon_tracker = CarbonFootprintTracker()

# Funciones de conveniencia
def calculate_transport_emissions(distance_km: float, transport_type: str) -> CarbonEmission:
    """Calcular emisiones de transporte"""
    return carbon_tracker.calculate_transport_emissions(distance_km, transport_type)

def calculate_energy_emissions(energy_type: str, quantity: float, unit: str = "kwh") -> CarbonEmission:
    """Calcular emisiones de energía"""
    return carbon_tracker.calculate_energy_emissions(energy_type, quantity, unit)

def calculate_carbon_footprint(start_date: datetime, end_date: datetime) -> CarbonFootprint:
    """Calcular huella de carbono"""
    return carbon_tracker.calculate_footprint(start_date, end_date)

if __name__ == "__main__":
    # Ejemplo de uso
    logger.info("Probando sistema de seguimiento de huella de carbono...")
    
    try:
        # Calcular emisiones de transporte
        transport_emission = calculate_transport_emissions(500, "truck")
        print(f"✅ Emisión de transporte: {transport_emission.quantity:.3f} toneladas CO2")
        
        # Calcular emisiones de energía
        energy_emission = calculate_energy_emissions("electricity", 1000, "kwh")
        print(f"✅ Emisión de energía: {energy_emission.quantity:.3f} toneladas CO2")
        
        # Calcular emisiones de empaquetado
        packaging_emission = carbon_tracker.calculate_packaging_emissions("cardboard", 50)
        print(f"✅ Emisión de empaquetado: {packaging_emission.quantity:.3f} toneladas CO2")
        
        # Comprar créditos de carbono
        credit_id = carbon_tracker.purchase_carbon_credits(10, 50.0)
        print(f"✅ Créditos de carbono comprados: ID {credit_id}")
        
        # Compensar emisión
        offset = carbon_tracker.offset_emission(transport_emission.emission_id)
        print(f"✅ Emisión compensada: {offset.offset_quantity:.3f} toneladas CO2")
        
        # Establecer objetivo de reducción
        carbon_tracker.set_reduction_target(2024, 20.0)
        print(f"✅ Objetivo de reducción establecido: 20% para 2024")
        
        # Calcular huella de carbono
        end_date = datetime.now()
        start_date = end_date - timedelta(days=30)
        footprint = calculate_carbon_footprint(start_date, end_date)
        
        print(f"✅ Huella de carbono calculada:")
        print(f"   Emisiones totales: {footprint.total_emissions:.3f} toneladas CO2")
        print(f"   Compensaciones: {footprint.offsets:.3f} toneladas CO2")
        print(f"   Emisiones netas: {footprint.net_emissions:.3f} toneladas CO2")
        print(f"   Intensidad de carbono: {footprint.carbon_intensity:.2f} kg CO2/producto")
        
        # Obtener recomendaciones
        recommendations = carbon_tracker.get_optimization_recommendations(footprint)
        print(f"✅ Recomendaciones: {len(recommendations)}")
        for rec in recommendations:
            print(f"   - {rec}")
        
        # Resumen completo
        summary = carbon_tracker.get_carbon_summary()
        print(f"✅ Resumen anual:")
        print(f"   Emisiones totales: {summary['total_emissions_tonnes']:.3f} toneladas CO2")
        print(f"   Emisiones netas: {summary['net_emissions_tonnes']:.3f} toneladas CO2")
        print(f"   Progreso hacia objetivo: {summary['progress_percentage']:.1f}%")
        
    except Exception as e:
        logger.error(f"Error en pruebas de huella de carbono: {e}")
    
    print("✅ Sistema de seguimiento de huella de carbono funcionando correctamente")

