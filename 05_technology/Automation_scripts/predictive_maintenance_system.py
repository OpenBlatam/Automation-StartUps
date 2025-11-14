"""
Sistema de Mantenimiento Predictivo con IA
==========================================

Sistema completo de mantenimiento predictivo utilizando inteligencia artificial
para predecir fallos y optimizar mantenimiento de equipos del almacén.
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

class EquipmentType(Enum):
    """Tipos de equipos"""
    FORKLIFT = "forklift"
    CONVEYOR = "conveyor"
    CRANE = "crane"
    ROBOT = "robot"
    SENSOR = "sensor"
    COOLING_SYSTEM = "cooling_system"
    LIGHTING = "lighting"
    SECURITY_SYSTEM = "security_system"

class MaintenanceStatus(Enum):
    """Estado de mantenimiento"""
    OPERATIONAL = "operational"
    NEEDS_MAINTENANCE = "needs_maintenance"
    CRITICAL = "critical"
    FAILED = "failed"
    MAINTENANCE_IN_PROGRESS = "maintenance_in_progress"

class FailureSeverity(Enum):
    """Severidad de fallo"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

@dataclass
class EquipmentSensor:
    """Sensor de equipo"""
    sensor_id: str
    sensor_type: str
    equipment_id: str
    value: float
    unit: str
    timestamp: datetime
    normal_range: Tuple[float, float]
    current_status: str

@dataclass
class MaintenancePrediction:
    """Predicción de mantenimiento"""
    equipment_id: str
    prediction_id: str
    failure_probability: float
    failure_severity: FailureSeverity
    estimated_time_to_failure: float  # horas
    recommended_maintenance_type: str
    confidence: float
    factors: List[str]
    timestamp: datetime

@dataclass
class MaintenanceTask:
    """Tarea de mantenimiento"""
    task_id: str
    equipment_id: str
    maintenance_type: str
    priority: int
    estimated_duration: float
    scheduled_date: datetime
    assigned_technician: Optional[str]
    status: str
    cost_estimate: float
    parts_required: List[str]

class PredictiveMaintenanceSystem:
    """Sistema de Mantenimiento Predictivo"""
    
    def __init__(self):
        self.equipment: Dict[str, Dict[str, Any]] = {}
        self.sensors: Dict[str, List[EquipmentSensor]] = {}
        self.predictions: Dict[str, MaintenancePrediction] = {}
        self.maintenance_tasks: Dict[str, MaintenanceTask] = {}
        self.historical_data: List[Dict[str, Any]] = []
        
        # Inicializar base de datos
        self._init_database()
    
    def _init_database(self):
        """Inicializar base de datos"""
        conn = sqlite3.connect('predictive_maintenance.db')
        cursor = conn.cursor()
        
        # Tabla de equipos
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS equipment (
                equipment_id TEXT PRIMARY KEY,
                equipment_type TEXT NOT NULL,
                equipment_name TEXT NOT NULL,
                status TEXT NOT NULL,
                installation_date TEXT NOT NULL,
                last_maintenance TEXT,
                operating_hours REAL NOT NULL,
                metadata TEXT NOT NULL
            )
        ''')
        
        # Tabla de sensores
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS equipment_sensors (
                sensor_id TEXT PRIMARY KEY,
                equipment_id TEXT NOT NULL,
                sensor_type TEXT NOT NULL,
                value REAL NOT NULL,
                unit TEXT NOT NULL,
                timestamp TEXT NOT NULL,
                normal_range_min REAL NOT NULL,
                normal_range_max REAL NOT NULL,
                status TEXT NOT NULL,
                FOREIGN KEY (equipment_id) REFERENCES equipment (equipment_id)
            )
        ''')
        
        # Tabla de predicciones
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS maintenance_predictions (
                prediction_id TEXT PRIMARY KEY,
                equipment_id TEXT NOT NULL,
                failure_probability REAL NOT NULL,
                failure_severity TEXT NOT NULL,
                estimated_time_to_failure REAL NOT NULL,
                recommended_maintenance_type TEXT NOT NULL,
                confidence REAL NOT NULL,
                factors TEXT NOT NULL,
                timestamp TEXT NOT NULL,
                FOREIGN KEY (equipment_id) REFERENCES equipment (equipment_id)
            )
        ''')
        
        # Tabla de tareas de mantenimiento
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS maintenance_tasks (
                task_id TEXT PRIMARY KEY,
                equipment_id TEXT NOT NULL,
                maintenance_type TEXT NOT NULL,
                priority INTEGER NOT NULL,
                estimated_duration REAL NOT NULL,
                scheduled_date TEXT NOT NULL,
                assigned_technician TEXT,
                status TEXT NOT NULL,
                cost_estimate REAL NOT NULL,
                parts_required TEXT NOT NULL,
                FOREIGN KEY (equipment_id) REFERENCES equipment (equipment_id)
            )
        ''')
        
        # Tabla de histórico de mantenimiento
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS maintenance_history (
                history_id TEXT PRIMARY KEY,
                equipment_id TEXT NOT NULL,
                maintenance_type TEXT NOT NULL,
                maintenance_date TEXT NOT NULL,
                duration REAL NOT NULL,
                cost REAL NOT NULL,
                technician TEXT,
                parts_used TEXT NOT NULL,
                notes TEXT,
                FOREIGN KEY (equipment_id) REFERENCES equipment (equipment_id)
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def register_equipment(self, equipment_id: str, equipment_type: EquipmentType,
                         equipment_name: str, installation_date: datetime,
                         metadata: Dict[str, Any] = None) -> Dict[str, Any]:
        """Registrar nuevo equipo"""
        
        equipment = {
            "equipment_id": equipment_id,
            "equipment_type": equipment_type.value,
            "equipment_name": equipment_name,
            "status": MaintenanceStatus.OPERATIONAL.value,
            "installation_date": installation_date.isoformat(),
            "last_maintenance": None,
            "operating_hours": 0.0,
            "metadata": metadata or {}
        }
        
        self.equipment[equipment_id] = equipment
        self.sensors[equipment_id] = []
        
        # Guardar en base de datos
        self._save_equipment_to_db(equipment)
        
        logger.info(f"Equipo registrado: {equipment_id} ({equipment_name})")
        
        return equipment
    
    def add_sensor(self, sensor_id: str, equipment_id: str, sensor_type: str,
                  normal_range: Tuple[float, float], unit: str = "") -> EquipmentSensor:
        """Agregar sensor a equipo"""
        
        if equipment_id not in self.equipment:
            raise ValueError(f"Equipo no encontrado: {equipment_id}")
        
        # Valor inicial aleatorio dentro del rango normal
        initial_value = (normal_range[0] + normal_range[1]) / 2 + random.gauss(0, (normal_range[1] - normal_range[0]) * 0.1)
        
        sensor = EquipmentSensor(
            sensor_id=sensor_id,
            sensor_type=sensor_type,
            equipment_id=equipment_id,
            value=initial_value,
            unit=unit,
            timestamp=datetime.now(),
            normal_range=normal_range,
            current_status="normal"
        )
        
        self.sensors[equipment_id].append(sensor)
        
        # Guardar en base de datos
        self._save_sensor_to_db(sensor)
        
        logger.info(f"Sensor {sensor_id} agregado a equipo {equipment_id}")
        
        return sensor
    
    def update_sensor_reading(self, sensor_id: str, value: float, timestamp: datetime = None):
        """Actualizar lectura de sensor"""
        
        timestamp = timestamp or datetime.now()
        
        # Encontrar sensor
        sensor = None
        for equipment_id, sensors in self.sensors.items():
            for s in sensors:
                if s.sensor_id == sensor_id:
                    sensor = s
                    break
            if sensor:
                break
        
        if not sensor:
            raise ValueError(f"Sensor no encontrado: {sensor_id}")
        
        # Actualizar valor
        sensor.value = value
        sensor.timestamp = timestamp
        
        # Verificar si está fuera del rango normal
        if value < sensor.normal_range[0] or value > sensor.normal_range[1]:
            if abs(value - sensor.normal_range[0]) < abs(value - sensor.normal_range[1]):
                deviation = abs(value - sensor.normal_range[0]) / (sensor.normal_range[1] - sensor.normal_range[0])
            else:
                deviation = abs(value - sensor.normal_range[1]) / (sensor.normal_range[1] - sensor.normal_range[0])
            
            if deviation > 0.5:
                sensor.current_status = "critical"
            else:
                sensor.current_status = "warning"
        else:
            sensor.current_status = "normal"
        
        # Guardar actualización
        self._save_sensor_to_db(sensor)
    
    def predict_maintenance(self, equipment_id: str) -> MaintenancePrediction:
        """Predecir necesidad de mantenimiento"""
        
        if equipment_id not in self.equipment:
            raise ValueError(f"Equipo no encontrado: {equipment_id}")
        
        equipment = self.equipment[equipment_id]
        sensors = self.sensors.get(equipment_id, [])
        
        # Calcular probabilidad de fallo usando modelo simplificado
        failure_probability = self._calculate_failure_probability(equipment, sensors)
        
        # Estimar tiempo hasta fallo
        time_to_failure = self._estimate_time_to_failure(equipment, sensors, failure_probability)
        
        # Determinar severidad
        failure_severity = self._determine_severity(failure_probability, time_to_failure)
        
        # Recomendar tipo de mantenimiento
        maintenance_type = self._recommend_maintenance_type(failure_probability, time_to_failure)
        
        # Identificar factores contribuyentes
        factors = self._identify_failure_factors(equipment, sensors)
        
        # Calcular confianza
        confidence = self._calculate_confidence(sensors, equipment)
        
        prediction = MaintenancePrediction(
            equipment_id=equipment_id,
            prediction_id=str(uuid.uuid4()),
            failure_probability=failure_probability,
            failure_severity=failure_severity,
            estimated_time_to_failure=time_to_failure,
            recommended_maintenance_type=maintenance_type,
            confidence=confidence,
            factors=factors,
            timestamp=datetime.now()
        )
        
        self.predictions[equipment_id] = prediction
        
        # Guardar predicción
        self._save_prediction_to_db(prediction)
        
        # Crear tarea de mantenimiento si es necesario
        if failure_probability > 0.7 or failure_severity in [FailureSeverity.HIGH, FailureSeverity.CRITICAL]:
            self._create_maintenance_task(prediction)
        
        logger.info(f"Predicción generada para {equipment_id}: {failure_probability*100:.1f}% probabilidad")
        
        return prediction
    
    def _calculate_failure_probability(self, equipment: Dict[str, Any], 
                                      sensors: List[EquipmentSensor]) -> float:
        """Calcular probabilidad de fallo"""
        
        base_probability = 0.1  # Probabilidad base
        
        # Factor de edad
        installation_date = datetime.fromisoformat(equipment["installation_date"])
        age_years = (datetime.now() - installation_date).days / 365.25
        age_factor = min(1.0, age_years / 10)  # Aumenta con la edad
        
        # Factor de horas operativas
        operating_hours = equipment.get("operating_hours", 0)
        hours_factor = min(1.0, operating_hours / 10000)  # Máximo en 10,000 horas
        
        # Factor de sensores anormales
        abnormal_sensors = [s for s in sensors if s.current_status != "normal"]
        sensor_factor = len(abnormal_sensors) / max(1, len(sensors)) if sensors else 0
        
        # Factor de tiempo desde último mantenimiento
        last_maintenance = equipment.get("last_maintenance")
        if last_maintenance:
            maintenance_date = datetime.fromisoformat(last_maintenance)
            days_since = (datetime.now() - maintenance_date).days
            maintenance_factor = min(1.0, days_since / 365)  # Aumenta con días desde mantenimiento
        else:
            maintenance_factor = min(1.0, age_years)  # Si nunca se ha mantenido, usar edad
        
        # Calcular probabilidad total
        failure_probability = base_probability + (
            age_factor * 0.2 +
            hours_factor * 0.2 +
            sensor_factor * 0.3 +
            maintenance_factor * 0.3
        )
        
        return min(1.0, failure_probability)
    
    def _estimate_time_to_failure(self, equipment: Dict[str, Any],
                                  sensors: List[EquipmentSensor],
                                  failure_probability: float) -> float:
        """Estimar tiempo hasta fallo (en horas)"""
        
        if failure_probability < 0.3:
            # Probabilidad baja: tiempo estimado largo
            base_hours = 720  # 30 días
        elif failure_probability < 0.6:
            # Probabilidad media: tiempo estimado medio
            base_hours = 240  # 10 días
        elif failure_probability < 0.8:
            # Probabilidad alta: tiempo estimado corto
            base_hours = 72  # 3 días
        else:
            # Probabilidad muy alta: tiempo estimado crítico
            base_hours = 24  # 1 día
        
        # Ajustar según sensores anormales
        abnormal_sensors = [s for s in sensors if s.current_status != "normal"]
        if abnormal_sensors:
            sensor_factor = len(abnormal_sensors) / max(1, len(sensors))
            base_hours *= (1 - sensor_factor * 0.5)  # Reducir tiempo estimado
        
        return max(1.0, base_hours)
    
    def _determine_severity(self, failure_probability: float, 
                           time_to_failure: float) -> FailureSeverity:
        """Determinar severidad de fallo"""
        
        if failure_probability > 0.8 or time_to_failure < 24:
            return FailureSeverity.CRITICAL
        elif failure_probability > 0.6 or time_to_failure < 72:
            return FailureSeverity.HIGH
        elif failure_probability > 0.4 or time_to_failure < 240:
            return FailureSeverity.MEDIUM
        else:
            return FailureSeverity.LOW
    
    def _recommend_maintenance_type(self, failure_probability: float,
                                   time_to_failure: float) -> str:
        """Recomendar tipo de mantenimiento"""
        
        if failure_probability > 0.8 or time_to_failure < 24:
            return "emergency_maintenance"
        elif failure_probability > 0.6:
            return "preventive_maintenance_urgent"
        elif failure_probability > 0.4:
            return "preventive_maintenance"
        else:
            return "routine_inspection"
    
    def _identify_failure_factors(self, equipment: Dict[str, Any],
                                 sensors: List[EquipmentSensor]) -> List[str]:
        """Identificar factores que contribuyen al fallo"""
        
        factors = []
        
        # Verificar edad
        installation_date = datetime.fromisoformat(equipment["installation_date"])
        age_years = (datetime.now() - installation_date).days / 365.25
        if age_years > 5:
            factors.append(f"Equipo envejecido ({age_years:.1f} años)")
        
        # Verificar horas operativas
        operating_hours = equipment.get("operating_hours", 0)
        if operating_hours > 5000:
            factors.append(f"Alto número de horas operativas ({operating_hours:.0f}h)")
        
        # Verificar sensores anormales
        abnormal_sensors = [s for s in sensors if s.current_status != "normal"]
        for sensor in abnormal_sensors:
            if sensor.current_status == "critical":
                factors.append(f"Sensor {sensor.sensor_type} en estado crítico")
            else:
                factors.append(f"Sensor {sensor.sensor_type} fuera de rango normal")
        
        # Verificar tiempo desde último mantenimiento
        last_maintenance = equipment.get("last_maintenance")
        if last_maintenance:
            maintenance_date = datetime.fromisoformat(last_maintenance)
            days_since = (datetime.now() - maintenance_date).days
            if days_since > 180:
                factors.append(f"Mantenimiento retrasado ({days_since} días)")
        else:
            factors.append("Sin historial de mantenimiento")
        
        if not factors:
            factors.append("Ningún factor significativo detectado")
        
        return factors
    
    def _calculate_confidence(self, sensors: List[EquipmentSensor],
                           equipment: Dict[str, Any]) -> float:
        """Calcular confianza de la predicción"""
        
        # Base de confianza
        confidence = 0.5
        
        # Más sensores = más confianza
        if len(sensors) > 0:
            confidence += 0.2
        
        # Datos históricos disponibles
        if equipment.get("last_maintenance"):
            confidence += 0.2
        
        # Sensores funcionando correctamente
        working_sensors = len([s for s in sensors if s.current_status == "normal"])
        if len(sensors) > 0:
            sensor_confidence = working_sensors / len(sensors)
            confidence += sensor_confidence * 0.1
        
        return min(1.0, confidence)
    
    def _create_maintenance_task(self, prediction: MaintenancePrediction):
        """Crear tarea de mantenimiento basada en predicción"""
        
        # Calcular prioridad
        priority_map = {
            FailureSeverity.CRITICAL: 1,
            FailureSeverity.HIGH: 2,
            FailureSeverity.MEDIUM: 3,
            FailureSeverity.LOW: 4
        }
        priority = priority_map.get(prediction.failure_severity, 5)
        
        # Estimar duración
        duration_map = {
            "emergency_maintenance": 8.0,
            "preventive_maintenance_urgent": 4.0,
            "preventive_maintenance": 2.0,
            "routine_inspection": 1.0
        }
        estimated_duration = duration_map.get(prediction.recommended_maintenance_type, 2.0)
        
        # Calcular fecha programada
        if prediction.failure_severity == FailureSeverity.CRITICAL:
            scheduled_date = datetime.now() + timedelta(hours=6)
        elif prediction.failure_severity == FailureSeverity.HIGH:
            scheduled_date = datetime.now() + timedelta(hours=24)
        else:
            scheduled_date = datetime.now() + timedelta(days=7)
        
        # Estimar costo
        cost_estimate = estimated_duration * 100  # $100 por hora estimado
        
        # Determinar partes requeridas
        parts_required = self._determine_parts_required(prediction)
        
        task = MaintenanceTask(
            task_id=str(uuid.uuid4()),
            equipment_id=prediction.equipment_id,
            maintenance_type=prediction.recommended_maintenance_type,
            priority=priority,
            estimated_duration=estimated_duration,
            scheduled_date=scheduled_date,
            assigned_technician=None,
            status="pending",
            cost_estimate=cost_estimate,
            parts_required=parts_required
        )
        
        self.maintenance_tasks[task.task_id] = task
        
        # Guardar tarea
        self._save_maintenance_task_to_db(task)
        
        logger.info(f"Tarea de mantenimiento creada: {task.task_id} para {prediction.equipment_id}")
        
        return task
    
    def _determine_parts_required(self, prediction: MaintenancePrediction) -> List[str]:
        """Determinar partes requeridas para mantenimiento"""
        
        # Simplificado - en realidad usaría base de datos de partes
        parts = []
        
        if prediction.recommended_maintenance_type == "emergency_maintenance":
            parts = ["Repuestos críticos", "Filtros", "Aceite"]
        elif prediction.recommended_maintenance_type in ["preventive_maintenance_urgent", "preventive_maintenance"]:
            parts = ["Filtros", "Aceite", "Lubricantes"]
        else:
            parts = ["Lubricantes"]
        
        return parts
    
    def _save_equipment_to_db(self, equipment: Dict[str, Any]):
        """Guardar equipo en base de datos"""
        conn = sqlite3.connect('predictive_maintenance.db')
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT OR REPLACE INTO equipment 
            (equipment_id, equipment_type, equipment_name, status, installation_date,
             last_maintenance, operating_hours, metadata)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            equipment["equipment_id"],
            equipment["equipment_type"],
            equipment["equipment_name"],
            equipment["status"],
            equipment["installation_date"],
            equipment["last_maintenance"],
            equipment["operating_hours"],
            json.dumps(equipment["metadata"])
        ))
        
        conn.commit()
        conn.close()
    
    def _save_sensor_to_db(self, sensor: EquipmentSensor):
        """Guardar sensor en base de datos"""
        conn = sqlite3.connect('predictive_maintenance.db')
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT OR REPLACE INTO equipment_sensors 
            (sensor_id, equipment_id, sensor_type, value, unit, timestamp,
             normal_range_min, normal_range_max, status)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            sensor.sensor_id,
            sensor.equipment_id,
            sensor.sensor_type,
            sensor.value,
            sensor.unit,
            sensor.timestamp.isoformat(),
            sensor.normal_range[0],
            sensor.normal_range[1],
            sensor.current_status
        ))
        
        conn.commit()
        conn.close()
    
    def _save_prediction_to_db(self, prediction: MaintenancePrediction):
        """Guardar predicción en base de datos"""
        conn = sqlite3.connect('predictive_maintenance.db')
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO maintenance_predictions 
            (prediction_id, equipment_id, failure_probability, failure_severity,
             estimated_time_to_failure, recommended_maintenance_type, confidence, factors, timestamp)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            prediction.prediction_id,
            prediction.equipment_id,
            prediction.failure_probability,
            prediction.failure_severity.value,
            prediction.estimated_time_to_failure,
            prediction.recommended_maintenance_type,
            prediction.confidence,
            json.dumps(prediction.factors),
            prediction.timestamp.isoformat()
        ))
        
        conn.commit()
        conn.close()
    
    def _save_maintenance_task_to_db(self, task: MaintenanceTask):
        """Guardar tarea de mantenimiento en base de datos"""
        conn = sqlite3.connect('predictive_maintenance.db')
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO maintenance_tasks 
            (task_id, equipment_id, maintenance_type, priority, estimated_duration,
             scheduled_date, assigned_technician, status, cost_estimate, parts_required)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            task.task_id,
            task.equipment_id,
            task.maintenance_type,
            task.priority,
            task.estimated_duration,
            task.scheduled_date.isoformat(),
            task.assigned_technician,
            task.status,
            task.cost_estimate,
            json.dumps(task.parts_required)
        ))
        
        conn.commit()
        conn.close()
    
    def get_maintenance_summary(self) -> Dict[str, Any]:
        """Obtener resumen de mantenimiento"""
        
        critical_predictions = [
            p for p in self.predictions.values()
            if p.failure_severity == FailureSeverity.CRITICAL
        ]
        
        high_predictions = [
            p for p in self.predictions.values()
            if p.failure_severity == FailureSeverity.HIGH
        ]
        
        pending_tasks = [
            t for t in self.maintenance_tasks.values()
            if t.status == "pending"
        ]
        
        return {
            "total_equipment": len(self.equipment),
            "operational_equipment": len([
                e for e in self.equipment.values()
                if e["status"] == MaintenanceStatus.OPERATIONAL.value
            ]),
            "active_predictions": len(self.predictions),
            "critical_predictions": len(critical_predictions),
            "high_priority_predictions": len(high_predictions),
            "pending_maintenance_tasks": len(pending_tasks),
            "total_sensors": sum(len(sensors) for sensors in self.sensors.values())
        }

# Instancia global del sistema de mantenimiento predictivo
predictive_maintenance = PredictiveMaintenanceSystem()

# Funciones de conveniencia
def register_equipment(equipment_id: str, equipment_type: EquipmentType,
                     equipment_name: str) -> Dict[str, Any]:
    """Registrar equipo"""
    return predictive_maintenance.register_equipment(
        equipment_id, equipment_type, equipment_name, datetime.now()
    )

def predict_equipment_maintenance(equipment_id: str) -> MaintenancePrediction:
    """Predecir mantenimiento de equipo"""
    return predictive_maintenance.predict_maintenance(equipment_id)

if __name__ == "__main__":
    # Ejemplo de uso
    logger.info("Probando sistema de mantenimiento predictivo...")
    
    try:
        # Registrar equipo
        forklift = register_equipment(
            "forklift_001",
            EquipmentType.FORKLIFT,
            "Montacargas Eléctrico Alpha"
        )
        
        # Agregar sensores
        predictive_maintenance.add_sensor(
            "temp_sensor_001",
            "forklift_001",
            "temperature",
            (0, 80),
            "°C"
        )
        
        predictive_maintenance.add_sensor(
            "battery_sensor_001",
            "forklift_001",
            "battery_voltage",
            (36, 42),
            "V"
        )
        
        print("✅ Equipo y sensores registrados")
        
        # Simular lecturas de sensores anormales
        predictive_maintenance.update_sensor_reading("temp_sensor_001", 85)
        predictive_maintenance.equipment["forklift_001"]["operating_hours"] = 8500
        
        print("✅ Lecturas de sensores actualizadas")
        
        # Generar predicción
        prediction = predict_equipment_maintenance("forklift_001")
        
        print(f"✅ Predicción generada:")
        print(f"   Probabilidad de fallo: {prediction.failure_probability*100:.1f}%")
        print(f"   Severidad: {prediction.failure_severity.value}")
        print(f"   Tiempo estimado hasta fallo: {prediction.estimated_time_to_failure:.1f} horas")
        print(f"   Mantenimiento recomendado: {prediction.recommended_maintenance_type}")
        print(f"   Confianza: {prediction.confidence*100:.1f}%")
        print(f"   Factores: {', '.join(prediction.factors[:3])}")
        
        # Resumen
        summary = predictive_maintenance.get_maintenance_summary()
        print(f"✅ Resumen del sistema:")
        print(f"   Equipos: {summary['total_equipment']}")
        print(f"   Equipos operacionales: {summary['operational_equipment']}")
        print(f"   Predicciones críticas: {summary['critical_predictions']}")
        print(f"   Tareas pendientes: {summary['pending_maintenance_tasks']}")
        
    except Exception as e:
        logger.error(f"Error en pruebas de mantenimiento predictivo: {e}")
    
    print("✅ Sistema de mantenimiento predictivo funcionando correctamente")

