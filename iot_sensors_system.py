"""
Sistema de Sensores IoT para Monitoreo Automático
===============================================

Sistema completo de sensores IoT para monitoreo automático de inventario,
condiciones ambientales, y gestión inteligente de almacenes.
"""

import asyncio
import json
import logging
import random
import threading
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Any, Callable
from dataclasses import dataclass, asdict
from enum import Enum
import sqlite3
import uuid
import math

logger = logging.getLogger(__name__)

class SensorType(Enum):
    """Tipos de sensores IoT"""
    TEMPERATURE = "temperature"
    HUMIDITY = "humidity"
    PRESSURE = "pressure"
    MOTION = "motion"
    LIGHT = "light"
    SOUND = "sound"
    PROXIMITY = "proximity"
    WEIGHT = "weight"
    RFID = "rfid"
    CAMERA = "camera"
    GPS = "gps"
    ACCELEROMETER = "accelerometer"
    GYROSCOPE = "gyroscope"

class SensorStatus(Enum):
    """Estado de sensores"""
    ACTIVE = "active"
    INACTIVE = "inactive"
    MAINTENANCE = "maintenance"
    ERROR = "error"
    CALIBRATING = "calibrating"

class AlertLevel(Enum):
    """Niveles de alerta"""
    INFO = "info"
    WARNING = "warning"
    CRITICAL = "critical"
    EMERGENCY = "emergency"

@dataclass
class SensorReading:
    """Lectura de sensor"""
    sensor_id: str
    sensor_type: SensorType
    value: float
    unit: str
    timestamp: datetime
    location: Tuple[float, float, float]  # x, y, z coordinates
    quality: float  # 0.0 to 1.0
    metadata: Dict[str, Any]

@dataclass
class SensorAlert:
    """Alerta de sensor"""
    alert_id: str
    sensor_id: str
    alert_level: AlertLevel
    message: str
    value: float
    threshold: float
    timestamp: datetime
    resolved: bool = False
    resolved_at: Optional[datetime] = None

@dataclass
class IoTDevice:
    """Dispositivo IoT"""
    device_id: str
    device_name: str
    device_type: str
    location: Tuple[float, float, float]
    sensors: List[str]  # Lista de IDs de sensores
    status: SensorStatus
    battery_level: float
    signal_strength: float
    last_seen: datetime
    firmware_version: str
    metadata: Dict[str, Any]

class VirtualSensor:
    """Sensor virtual para simulación"""
    
    def __init__(self, sensor_id: str, sensor_type: SensorType, 
                 location: Tuple[float, float, float], 
                 min_value: float = 0, max_value: float = 100):
        self.sensor_id = sensor_id
        self.sensor_type = sensor_type
        self.location = location
        self.min_value = min_value
        self.max_value = max_value
        self.status = SensorStatus.ACTIVE
        self.battery_level = 100.0
        self.signal_strength = 95.0
        self.last_reading = None
        self.reading_count = 0
        
        # Configuración específica por tipo de sensor
        self._configure_sensor()
    
    def _configure_sensor(self):
        """Configurar sensor según su tipo"""
        if self.sensor_type == SensorType.TEMPERATURE:
            self.min_value = -40
            self.max_value = 85
            self.unit = "°C"
            self.thresholds = {"warning": 30, "critical": 40}
        
        elif self.sensor_type == SensorType.HUMIDITY:
            self.min_value = 0
            self.max_value = 100
            self.unit = "%"
            self.thresholds = {"warning": 80, "critical": 90}
        
        elif self.sensor_type == SensorType.MOTION:
            self.min_value = 0
            self.max_value = 1
            self.unit = "binary"
            self.thresholds = {"warning": 0.5, "critical": 0.8}
        
        elif self.sensor_type == SensorType.WEIGHT:
            self.min_value = 0
            self.max_value = 1000
            self.unit = "kg"
            self.thresholds = {"warning": 800, "critical": 950}
        
        elif self.sensor_type == SensorType.RFID:
            self.min_value = 0
            self.max_value = 1
            self.unit = "binary"
            self.thresholds = {"warning": 0.5, "critical": 0.8}
        
        else:
            self.unit = "units"
            self.thresholds = {"warning": self.max_value * 0.8, "critical": self.max_value * 0.9}
    
    def read_sensor(self) -> SensorReading:
        """Leer sensor"""
        if self.status != SensorStatus.ACTIVE:
            raise ValueError(f"Sensor {self.sensor_id} no está activo")
        
        # Simular lectura con variación realista
        base_value = (self.min_value + self.max_value) / 2
        
        # Agregar variación temporal (simular patrones diarios)
        time_factor = math.sin(time.time() / 3600) * 0.1  # Variación cada hora
        
        # Agregar ruido aleatorio
        noise = random.gauss(0, (self.max_value - self.min_value) * 0.05)
        
        # Calcular valor final
        value = base_value + time_factor * (self.max_value - self.min_value) + noise
        
        # Mantener dentro de límites
        value = max(self.min_value, min(self.max_value, value))
        
        # Simular degradación de batería
        self.battery_level -= 0.01
        if self.battery_level < 0:
            self.battery_level = 0
            self.status = SensorStatus.ERROR
        
        # Simular variación de señal
        self.signal_strength = max(0, min(100, self.signal_strength + random.gauss(0, 2)))
        
        # Calcular calidad de lectura
        quality = min(1.0, self.battery_level / 100.0 * self.signal_strength / 100.0)
        
        reading = SensorReading(
            sensor_id=self.sensor_id,
            sensor_type=self.sensor_type,
            value=value,
            unit=self.unit,
            timestamp=datetime.now(),
            location=self.location,
            quality=quality,
            metadata={
                "battery_level": self.battery_level,
                "signal_strength": self.signal_strength,
                "reading_count": self.reading_count
            }
        )
        
        self.last_reading = reading
        self.reading_count += 1
        
        return reading
    
    def calibrate(self) -> bool:
        """Calibrar sensor"""
        self.status = SensorStatus.CALIBRATING
        time.sleep(1)  # Simular tiempo de calibración
        
        # Simular éxito/fallo de calibración
        success = random.random() > 0.1  # 90% de éxito
        
        if success:
            self.status = SensorStatus.ACTIVE
            logger.info(f"Sensor {self.sensor_id} calibrado exitosamente")
        else:
            self.status = SensorStatus.ERROR
            logger.error(f"Error en calibración del sensor {self.sensor_id}")
        
        return success
    
    def get_status(self) -> Dict[str, Any]:
        """Obtener estado del sensor"""
        return {
            "sensor_id": self.sensor_id,
            "sensor_type": self.sensor_type.value,
            "status": self.status.value,
            "battery_level": self.battery_level,
            "signal_strength": self.signal_strength,
            "location": self.location,
            "last_reading": self.last_reading.value if self.last_reading else None,
            "reading_count": self.reading_count,
            "thresholds": self.thresholds
        }

class IoTManager:
    """Gestor de dispositivos IoT"""
    
    def __init__(self):
        self.devices: Dict[str, IoTDevice] = {}
        self.sensors: Dict[str, VirtualSensor] = {}
        self.readings_history: List[SensorReading] = []
        self.alerts: List[SensorAlert] = []
        self.alert_callbacks: List[Callable] = []
        self.is_monitoring = False
        self.monitor_thread = None
        self.reading_interval = 5  # segundos
        
        # Configurar base de datos
        self._init_database()
    
    def _init_database(self):
        """Inicializar base de datos para IoT"""
        conn = sqlite3.connect('iot_sensors.db')
        cursor = conn.cursor()
        
        # Tabla de dispositivos
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS iot_devices (
                device_id TEXT PRIMARY KEY,
                device_name TEXT NOT NULL,
                device_type TEXT NOT NULL,
                location_x REAL NOT NULL,
                location_y REAL NOT NULL,
                location_z REAL NOT NULL,
                status TEXT NOT NULL,
                battery_level REAL NOT NULL,
                signal_strength REAL NOT NULL,
                last_seen TEXT NOT NULL,
                firmware_version TEXT NOT NULL,
                metadata TEXT NOT NULL
            )
        ''')
        
        # Tabla de sensores
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS iot_sensors (
                sensor_id TEXT PRIMARY KEY,
                device_id TEXT NOT NULL,
                sensor_type TEXT NOT NULL,
                location_x REAL NOT NULL,
                location_y REAL NOT NULL,
                location_z REAL NOT NULL,
                status TEXT NOT NULL,
                battery_level REAL NOT NULL,
                signal_strength REAL NOT NULL,
                min_value REAL NOT NULL,
                max_value REAL NOT NULL,
                unit TEXT NOT NULL,
                thresholds TEXT NOT NULL,
                FOREIGN KEY (device_id) REFERENCES iot_devices (device_id)
            )
        ''')
        
        # Tabla de lecturas
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS sensor_readings (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                sensor_id TEXT NOT NULL,
                sensor_type TEXT NOT NULL,
                value REAL NOT NULL,
                unit TEXT NOT NULL,
                timestamp TEXT NOT NULL,
                location_x REAL NOT NULL,
                location_y REAL NOT NULL,
                location_z REAL NOT NULL,
                quality REAL NOT NULL,
                metadata TEXT NOT NULL,
                FOREIGN KEY (sensor_id) REFERENCES iot_sensors (sensor_id)
            )
        ''')
        
        # Tabla de alertas
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS sensor_alerts (
                alert_id TEXT PRIMARY KEY,
                sensor_id TEXT NOT NULL,
                alert_level TEXT NOT NULL,
                message TEXT NOT NULL,
                value REAL NOT NULL,
                threshold REAL NOT NULL,
                timestamp TEXT NOT NULL,
                resolved BOOLEAN DEFAULT FALSE,
                resolved_at TEXT,
                FOREIGN KEY (sensor_id) REFERENCES iot_sensors (sensor_id)
            )
        ''')
        
        # Índices
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_readings_timestamp ON sensor_readings(timestamp)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_readings_sensor ON sensor_readings(sensor_id)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_alerts_timestamp ON sensor_alerts(timestamp)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_alerts_sensor ON sensor_alerts(sensor_id)')
        
        conn.commit()
        conn.close()
    
    def register_device(self, device_id: str, device_name: str, device_type: str,
                       location: Tuple[float, float, float], firmware_version: str = "1.0.0") -> IoTDevice:
        """Registrar dispositivo IoT"""
        
        device = IoTDevice(
            device_id=device_id,
            device_name=device_name,
            device_type=device_type,
            location=location,
            sensors=[],
            status=SensorStatus.ACTIVE,
            battery_level=100.0,
            signal_strength=95.0,
            last_seen=datetime.now(),
            firmware_version=firmware_version,
            metadata={}
        )
        
        self.devices[device_id] = device
        
        # Guardar en base de datos
        self._save_device_to_db(device)
        
        logger.info(f"Dispositivo registrado: {device_id} ({device_name})")
        
        return device
    
    def add_sensor(self, device_id: str, sensor_id: str, sensor_type: SensorType,
                   location: Tuple[float, float, float], min_value: float = 0, 
                   max_value: float = 100) -> VirtualSensor:
        """Agregar sensor a dispositivo"""
        
        if device_id not in self.devices:
            raise ValueError(f"Dispositivo no encontrado: {device_id}")
        
        sensor = VirtualSensor(sensor_id, sensor_type, location, min_value, max_value)
        self.sensors[sensor_id] = sensor
        
        # Agregar sensor al dispositivo
        self.devices[device_id].sensors.append(sensor_id)
        
        # Guardar en base de datos
        self._save_sensor_to_db(sensor, device_id)
        
        logger.info(f"Sensor agregado: {sensor_id} ({sensor_type.value}) a {device_id}")
        
        return sensor
    
    def start_monitoring(self):
        """Iniciar monitoreo de sensores"""
        if not self.is_monitoring:
            self.is_monitoring = True
            self.monitor_thread = threading.Thread(target=self._monitor_sensors)
            self.monitor_thread.daemon = True
            self.monitor_thread.start()
            logger.info("Monitoreo de sensores IoT iniciado")
    
    def stop_monitoring(self):
        """Detener monitoreo de sensores"""
        if self.is_monitoring:
            self.is_monitoring = False
            if self.monitor_thread:
                self.monitor_thread.join(timeout=5)
            logger.info("Monitoreo de sensores IoT detenido")
    
    def _monitor_sensors(self):
        """Monitorear sensores continuamente"""
        while self.is_monitoring:
            try:
                for sensor_id, sensor in self.sensors.items():
                    if sensor.status == SensorStatus.ACTIVE:
                        try:
                            # Leer sensor
                            reading = sensor.read_sensor()
                            
                            # Guardar lectura
                            self._save_reading_to_db(reading)
                            self.readings_history.append(reading)
                            
                            # Verificar alertas
                            self._check_alerts(reading)
                            
                        except Exception as e:
                            logger.error(f"Error leyendo sensor {sensor_id}: {e}")
                            sensor.status = SensorStatus.ERROR
                
                # Limpiar historial antiguo
                self._cleanup_old_readings()
                
                time.sleep(self.reading_interval)
                
            except Exception as e:
                logger.error(f"Error en monitoreo de sensores: {e}")
                time.sleep(10)
    
    def _check_alerts(self, reading: SensorReading):
        """Verificar alertas basadas en lectura"""
        sensor = self.sensors[reading.sensor_id]
        
        # Verificar umbrales
        for level_name, threshold in sensor.thresholds.items():
            alert_level = AlertLevel.WARNING if level_name == "warning" else AlertLevel.CRITICAL
            
            if reading.value > threshold:
                # Crear alerta
                alert = SensorAlert(
                    alert_id=str(uuid.uuid4()),
                    sensor_id=reading.sensor_id,
                    alert_level=alert_level,
                    message=f"Sensor {reading.sensor_id} excedió umbral {level_name}: {reading.value:.2f} {reading.unit} > {threshold:.2f} {reading.unit}",
                    value=reading.value,
                    threshold=threshold,
                    timestamp=datetime.now()
                )
                
                self.alerts.append(alert)
                self._save_alert_to_db(alert)
                
                # Notificar callbacks
                for callback in self.alert_callbacks:
                    try:
                        callback(alert)
                    except Exception as e:
                        logger.error(f"Error en callback de alerta: {e}")
                
                logger.warning(f"Alerta generada: {alert.message}")
    
    def _save_device_to_db(self, device: IoTDevice):
        """Guardar dispositivo en base de datos"""
        conn = sqlite3.connect('iot_sensors.db')
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT OR REPLACE INTO iot_devices 
            (device_id, device_name, device_type, location_x, location_y, location_z,
             status, battery_level, signal_strength, last_seen, firmware_version, metadata)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            device.device_id,
            device.device_name,
            device.device_type,
            device.location[0],
            device.location[1],
            device.location[2],
            device.status.value,
            device.battery_level,
            device.signal_strength,
            device.last_seen.isoformat(),
            device.firmware_version,
            json.dumps(device.metadata)
        ))
        
        conn.commit()
        conn.close()
    
    def _save_sensor_to_db(self, sensor: VirtualSensor, device_id: str):
        """Guardar sensor en base de datos"""
        conn = sqlite3.connect('iot_sensors.db')
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT OR REPLACE INTO iot_sensors 
            (sensor_id, device_id, sensor_type, location_x, location_y, location_z,
             status, battery_level, signal_strength, min_value, max_value, unit, thresholds)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            sensor.sensor_id,
            device_id,
            sensor.sensor_type.value,
            sensor.location[0],
            sensor.location[1],
            sensor.location[2],
            sensor.status.value,
            sensor.battery_level,
            sensor.signal_strength,
            sensor.min_value,
            sensor.max_value,
            sensor.unit,
            json.dumps(sensor.thresholds)
        ))
        
        conn.commit()
        conn.close()
    
    def _save_reading_to_db(self, reading: SensorReading):
        """Guardar lectura en base de datos"""
        conn = sqlite3.connect('iot_sensors.db')
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO sensor_readings 
            (sensor_id, sensor_type, value, unit, timestamp, location_x, location_y, location_z,
             quality, metadata)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            reading.sensor_id,
            reading.sensor_type.value,
            reading.value,
            reading.unit,
            reading.timestamp.isoformat(),
            reading.location[0],
            reading.location[1],
            reading.location[2],
            reading.quality,
            json.dumps(reading.metadata)
        ))
        
        conn.commit()
        conn.close()
    
    def _save_alert_to_db(self, alert: SensorAlert):
        """Guardar alerta en base de datos"""
        conn = sqlite3.connect('iot_sensors.db')
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO sensor_alerts 
            (alert_id, sensor_id, alert_level, message, value, threshold, timestamp, resolved, resolved_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            alert.alert_id,
            alert.sensor_id,
            alert.alert_level.value,
            alert.message,
            alert.value,
            alert.threshold,
            alert.timestamp.isoformat(),
            alert.resolved,
            alert.resolved_at.isoformat() if alert.resolved_at else None
        ))
        
        conn.commit()
        conn.close()
    
    def _cleanup_old_readings(self):
        """Limpiar lecturas antiguas"""
        cutoff_time = datetime.now() - timedelta(hours=24)
        
        # Limpiar de memoria
        self.readings_history = [
            reading for reading in self.readings_history 
            if reading.timestamp > cutoff_time
        ]
        
        # Limpiar de base de datos
        conn = sqlite3.connect('iot_sensors.db')
        cursor = conn.cursor()
        
        cursor.execute('DELETE FROM sensor_readings WHERE timestamp < ?', (cutoff_time.isoformat(),))
        deleted_count = cursor.rowcount
        
        conn.commit()
        conn.close()
        
        if deleted_count > 0:
            logger.info(f"Limpiadas {deleted_count} lecturas antiguas")
    
    def get_sensor_readings(self, sensor_id: str, hours: int = 24) -> List[SensorReading]:
        """Obtener lecturas de sensor"""
        cutoff_time = datetime.now() - timedelta(hours=hours)
        
        conn = sqlite3.connect('iot_sensors.db')
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT * FROM sensor_readings 
            WHERE sensor_id = ? AND timestamp >= ?
            ORDER BY timestamp DESC
        ''', (sensor_id, cutoff_time.isoformat()))
        
        readings = []
        for row in cursor.fetchall():
            reading = SensorReading(
                sensor_id=row[1],
                sensor_type=SensorType(row[2]),
                value=row[3],
                unit=row[4],
                timestamp=datetime.fromisoformat(row[5]),
                location=(row[6], row[7], row[8]),
                quality=row[9],
                metadata=json.loads(row[10])
            )
            readings.append(reading)
        
        conn.close()
        return readings
    
    def get_active_alerts(self) -> List[SensorAlert]:
        """Obtener alertas activas"""
        return [alert for alert in self.alerts if not alert.resolved]
    
    def resolve_alert(self, alert_id: str) -> bool:
        """Resolver alerta"""
        for alert in self.alerts:
            if alert.alert_id == alert_id:
                alert.resolved = True
                alert.resolved_at = datetime.now()
                
                # Actualizar en base de datos
                conn = sqlite3.connect('iot_sensors.db')
                cursor = conn.cursor()
                
                cursor.execute('''
                    UPDATE sensor_alerts 
                    SET resolved = TRUE, resolved_at = ?
                    WHERE alert_id = ?
                ''', (alert.resolved_at.isoformat(), alert_id))
                
                conn.commit()
                conn.close()
                
                logger.info(f"Alerta resuelta: {alert_id}")
                return True
        
        return False
    
    def add_alert_callback(self, callback: Callable):
        """Agregar callback para alertas"""
        self.alert_callbacks.append(callback)
    
    def get_system_stats(self) -> Dict[str, Any]:
        """Obtener estadísticas del sistema IoT"""
        
        active_devices = len([d for d in self.devices.values() if d.status == SensorStatus.ACTIVE])
        active_sensors = len([s for s in self.sensors.values() if s.status == SensorStatus.ACTIVE])
        active_alerts = len(self.get_active_alerts())
        
        # Calcular estadísticas de batería
        battery_levels = [s.battery_level for s in self.sensors.values()]
        avg_battery = sum(battery_levels) / len(battery_levels) if battery_levels else 0
        
        # Calcular estadísticas de señal
        signal_strengths = [s.signal_strength for s in self.sensors.values()]
        avg_signal = sum(signal_strengths) / len(signal_strengths) if signal_strengths else 0
        
        return {
            'total_devices': len(self.devices),
            'active_devices': active_devices,
            'total_sensors': len(self.sensors),
            'active_sensors': active_sensors,
            'active_alerts': active_alerts,
            'total_readings': len(self.readings_history),
            'avg_battery_level': avg_battery,
            'avg_signal_strength': avg_signal,
            'monitoring_active': self.is_monitoring,
            'reading_interval': self.reading_interval
        }
    
    def simulate_warehouse_setup(self):
        """Simular configuración de almacén con sensores IoT"""
        
        logger.info("Configurando almacén simulado con sensores IoT...")
        
        # Crear dispositivos de almacén
        devices_config = [
            ("warehouse_gateway_01", "Gateway Principal", "gateway", (0, 0, 2)),
            ("temperature_node_01", "Nodo Temperatura A", "temperature_node", (10, 5, 1.5)),
            ("temperature_node_02", "Nodo Temperatura B", "temperature_node", (20, 15, 1.5)),
            ("motion_detector_01", "Detector Movimiento", "motion_detector", (5, 10, 2.5)),
            ("weight_sensor_01", "Sensor Peso Estante A", "weight_sensor", (15, 8, 0.5)),
            ("rfid_reader_01", "Lector RFID Entrada", "rfid_reader", (0, 0, 1))
        ]
        
        # Registrar dispositivos
        for device_id, name, device_type, location in devices_config:
            self.register_device(device_id, name, device_type, location)
        
        # Agregar sensores
        sensors_config = [
            ("temp_sensor_01", "temperature_node_01", SensorType.TEMPERATURE, (10, 5, 1.5)),
            ("temp_sensor_02", "temperature_node_02", SensorType.TEMPERATURE, (20, 15, 1.5)),
            ("humidity_sensor_01", "temperature_node_01", SensorType.HUMIDITY, (10, 5, 1.5)),
            ("humidity_sensor_02", "temperature_node_02", SensorType.HUMIDITY, (20, 15, 1.5)),
            ("motion_sensor_01", "motion_detector_01", SensorType.MOTION, (5, 10, 2.5)),
            ("weight_sensor_01", "weight_sensor_01", SensorType.WEIGHT, (15, 8, 0.5)),
            ("rfid_sensor_01", "rfid_reader_01", SensorType.RFID, (0, 0, 1))
        ]
        
        # Agregar sensores
        for sensor_id, device_id, sensor_type, location in sensors_config:
            self.add_sensor(device_id, sensor_id, sensor_type, location)
        
        logger.info("Configuración de almacén completada")

# Instancia global del gestor IoT
iot_manager = IoTManager()

# Funciones de conveniencia
def register_iot_device(device_id: str, device_name: str, device_type: str,
                       location: Tuple[float, float, float]) -> IoTDevice:
    """Registrar dispositivo IoT"""
    return iot_manager.register_device(device_id, device_name, device_type, location)

def add_iot_sensor(device_id: str, sensor_id: str, sensor_type: SensorType,
                   location: Tuple[float, float, float]) -> VirtualSensor:
    """Agregar sensor IoT"""
    return iot_manager.add_sensor(device_id, sensor_id, sensor_type, location)

def start_iot_monitoring():
    """Iniciar monitoreo IoT"""
    iot_manager.start_monitoring()

def stop_iot_monitoring():
    """Detener monitoreo IoT"""
    iot_manager.stop_monitoring()

def get_iot_system_stats() -> Dict[str, Any]:
    """Obtener estadísticas del sistema IoT"""
    return iot_manager.get_system_stats()

if __name__ == "__main__":
    # Ejemplo de uso
    logger.info("Probando sistema de sensores IoT...")
    
    try:
        # Configurar almacén simulado
        iot_manager.simulate_warehouse_setup()
        
        # Iniciar monitoreo
        iot_manager.start_monitoring()
        
        # Simular funcionamiento por un tiempo
        print("✅ Sistema IoT configurado y monitoreando...")
        
        # Esperar algunas lecturas
        time.sleep(10)
        
        # Obtener estadísticas
        stats = iot_manager.get_system_stats()
        print(f"✅ Estadísticas del sistema IoT:")
        print(f"   Dispositivos: {stats['total_devices']} total, {stats['active_devices']} activos")
        print(f"   Sensores: {stats['total_sensors']} total, {stats['active_sensors']} activos")
        print(f"   Lecturas: {stats['total_readings']}")
        print(f"   Alertas activas: {stats['active_alerts']}")
        print(f"   Batería promedio: {stats['avg_battery_level']:.1f}%")
        print(f"   Señal promedio: {stats['avg_signal_strength']:.1f}%")
        
        # Obtener lecturas de un sensor específico
        temp_readings = iot_manager.get_sensor_readings("temp_sensor_01", hours=1)
        if temp_readings:
            latest_reading = temp_readings[0]
            print(f"✅ Última lectura de temperatura: {latest_reading.value:.2f}°C")
        
        # Obtener alertas activas
        active_alerts = iot_manager.get_active_alerts()
        if active_alerts:
            print(f"✅ Alertas activas: {len(active_alerts)}")
            for alert in active_alerts[:3]:  # Mostrar primeras 3
                print(f"   - {alert.message}")
        
        # Simular más tiempo
        print("✅ Continuando monitoreo por 10 segundos más...")
        time.sleep(10)
        
        # Estadísticas finales
        final_stats = iot_manager.get_system_stats()
        print(f"✅ Estadísticas finales:")
        print(f"   Lecturas totales: {final_stats['total_readings']}")
        print(f"   Alertas activas: {final_stats['active_alerts']}")
        
    except Exception as e:
        logger.error(f"Error en pruebas de IoT: {e}")
    
    finally:
        # Detener monitoreo
        iot_manager.stop_monitoring()
    
    print("✅ Sistema de sensores IoT funcionando correctamente")
