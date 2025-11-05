from datetime import datetime, timedelta
from app import db
from models import Product, InventoryRecord, Alert
import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Tuple
import logging
from dataclasses import dataclass
import json
import os
import threading
import time
import random
from enum import Enum

class SensorType(Enum):
    """Tipos de sensores IoT"""
    TEMPERATURE = "temperature"
    HUMIDITY = "humidity"
    PRESSURE = "pressure"
    MOTION = "motion"
    LIGHT = "light"
    SOUND = "sound"
    VIBRATION = "vibration"
    WEIGHT = "weight"
    RFID = "rfid"
    CAMERA = "camera"

class SensorStatus(Enum):
    """Estado de sensores"""
    ONLINE = "online"
    OFFLINE = "offline"
    MAINTENANCE = "maintenance"
    ERROR = "error"

@dataclass
class SensorData:
    """Datos de sensor IoT"""
    sensor_id: str
    sensor_type: SensorType
    value: float
    unit: str
    timestamp: datetime
    location: str
    quality: float  # 0-1, calidad de la señal
    battery_level: Optional[float] = None
    signal_strength: Optional[float] = None

@dataclass
class IoTDevice:
    """Dispositivo IoT"""
    device_id: str
    name: str
    device_type: str
    location: str
    status: SensorStatus
    sensors: List[str]
    last_seen: datetime
    firmware_version: str
    battery_level: Optional[float] = None
    signal_strength: Optional[float] = None

class IoTMonitoringService:
    """Servicio de monitoreo IoT"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.devices = {}
        self.sensor_data_history = []
        self.alerts = []
        self.is_monitoring = False
        self.monitoring_thread = None
        
        # Configurar dispositivos IoT simulados
        self._setup_simulated_devices()
    
    def _setup_simulated_devices(self):
        """Configura dispositivos IoT simulados"""
        devices = [
            IoTDevice(
                device_id="WH001",
                name="Sensor de Almacén Principal",
                device_type="Environmental Monitor",
                location="Almacén Principal",
                status=SensorStatus.ONLINE,
                sensors=["temp_001", "humidity_001", "motion_001"],
                last_seen=datetime.utcnow(),
                firmware_version="2.1.3",
                battery_level=85.0,
                signal_strength=-45.0
            ),
            IoTDevice(
                device_id="WH002",
                name="Sensor de Almacén Secundario",
                device_type="Environmental Monitor",
                location="Almacén Secundario",
                status=SensorStatus.ONLINE,
                sensors=["temp_002", "humidity_002", "pressure_002"],
                last_seen=datetime.utcnow(),
                firmware_version="2.1.3",
                battery_level=92.0,
                signal_strength=-38.0
            ),
            IoTDevice(
                device_id="RFID001",
                name="Lector RFID Principal",
                device_type="RFID Reader",
                location="Entrada Principal",
                status=SensorStatus.ONLINE,
                sensors=["rfid_001"],
                last_seen=datetime.utcnow(),
                firmware_version="1.8.2",
                battery_level=100.0,
                signal_strength=-25.0
            ),
            IoTDevice(
                device_id="CAM001",
                name="Cámara de Seguridad",
                device_type="Security Camera",
                location="Almacén Principal",
                status=SensorStatus.ONLINE,
                sensors=["camera_001"],
                last_seen=datetime.utcnow(),
                firmware_version="3.2.1",
                battery_level=78.0,
                signal_strength=-52.0
            ),
            IoTDevice(
                device_id="WEIGHT001",
                name="Báscula Inteligente",
                device_type="Smart Scale",
                location="Zona de Recepción",
                status=SensorStatus.ONLINE,
                sensors=["weight_001"],
                last_seen=datetime.utcnow(),
                firmware_version="1.5.0",
                battery_level=65.0,
                signal_strength=-41.0
            )
        ]
        
        for device in devices:
            self.devices[device.device_id] = device
    
    def start_monitoring(self):
        """Inicia el monitoreo IoT"""
        if self.is_monitoring:
            return
        
        self.is_monitoring = True
        self.monitoring_thread = threading.Thread(target=self._monitoring_loop)
        self.monitoring_thread.daemon = True
        self.monitoring_thread.start()
        
        self.logger.info('Monitoreo IoT iniciado')
    
    def stop_monitoring(self):
        """Detiene el monitoreo IoT"""
        self.is_monitoring = False
        if self.monitoring_thread:
            self.monitoring_thread.join(timeout=5)
        
        self.logger.info('Monitoreo IoT detenido')
    
    def _monitoring_loop(self):
        """Loop principal de monitoreo IoT"""
        while self.is_monitoring:
            try:
                # Generar datos de sensores simulados
                self._generate_sensor_data()
                
                # Verificar estado de dispositivos
                self._check_device_status()
                
                # Analizar datos y generar alertas
                self._analyze_sensor_data()
                
                # Limpiar datos antiguos
                self._cleanup_old_data()
                
                # Esperar antes de la siguiente verificación
                time.sleep(30)  # Verificar cada 30 segundos
                
            except Exception as e:
                self.logger.error(f'Error en loop de monitoreo IoT: {str(e)}')
                time.sleep(60)  # Esperar 1 minuto en caso de error
    
    def _generate_sensor_data(self):
        """Genera datos de sensores simulados"""
        try:
            current_time = datetime.utcnow()
            
            for device_id, device in self.devices.items():
                if device.status != SensorStatus.ONLINE:
                    continue
                
                # Generar datos para cada sensor del dispositivo
                for sensor_id in device.sensors:
                    sensor_type = self._get_sensor_type_from_id(sensor_id)
                    
                    if sensor_type == SensorType.TEMPERATURE:
                        value = random.uniform(18.0, 25.0)  # Temperatura ambiente
                        unit = "°C"
                    elif sensor_type == SensorType.HUMIDITY:
                        value = random.uniform(40.0, 60.0)  # Humedad relativa
                        unit = "%"
                    elif sensor_type == SensorType.PRESSURE:
                        value = random.uniform(1010.0, 1020.0)  # Presión atmosférica
                        unit = "hPa"
                    elif sensor_type == SensorType.MOTION:
                        value = random.choice([0.0, 1.0])  # Movimiento detectado
                        unit = "binary"
                    elif sensor_type == SensorType.LIGHT:
                        value = random.uniform(200.0, 800.0)  # Intensidad de luz
                        unit = "lux"
                    elif sensor_type == SensorType.SOUND:
                        value = random.uniform(30.0, 80.0)  # Nivel de sonido
                        unit = "dB"
                    elif sensor_type == SensorType.VIBRATION:
                        value = random.uniform(0.0, 5.0)  # Nivel de vibración
                        unit = "g"
                    elif sensor_type == SensorType.WEIGHT:
                        value = random.uniform(0.0, 1000.0)  # Peso
                        unit = "kg"
                    elif sensor_type == SensorType.RFID:
                        value = random.choice([0.0, 1.0])  # Tag detectado
                        unit = "binary"
                    elif sensor_type == SensorType.CAMERA:
                        value = random.uniform(0.0, 1.0)  # Calidad de imagen
                        unit = "quality"
                    else:
                        value = random.uniform(0.0, 100.0)
                        unit = "units"
                    
                    # Crear dato de sensor
                    sensor_data = SensorData(
                        sensor_id=sensor_id,
                        sensor_type=sensor_type,
                        value=value,
                        unit=unit,
                        timestamp=current_time,
                        location=device.location,
                        quality=random.uniform(0.8, 1.0),
                        battery_level=device.battery_level,
                        signal_strength=device.signal_strength
                    )
                    
                    self.sensor_data_history.append(sensor_data)
                    
                    # Actualizar último visto del dispositivo
                    device.last_seen = current_time
        
        except Exception as e:
            self.logger.error(f'Error generando datos de sensores: {str(e)}')
    
    def _get_sensor_type_from_id(self, sensor_id: str) -> SensorType:
        """Obtiene el tipo de sensor desde su ID"""
        if sensor_id.startswith('temp_'):
            return SensorType.TEMPERATURE
        elif sensor_id.startswith('humidity_'):
            return SensorType.HUMIDITY
        elif sensor_id.startswith('pressure_'):
            return SensorType.PRESSURE
        elif sensor_id.startswith('motion_'):
            return SensorType.MOTION
        elif sensor_id.startswith('light_'):
            return SensorType.LIGHT
        elif sensor_id.startswith('sound_'):
            return SensorType.SOUND
        elif sensor_id.startswith('vibration_'):
            return SensorType.VIBRATION
        elif sensor_id.startswith('weight_'):
            return SensorType.WEIGHT
        elif sensor_id.startswith('rfid_'):
            return SensorType.RFID
        elif sensor_id.startswith('camera_'):
            return SensorType.CAMERA
        else:
            return SensorType.TEMPERATURE
    
    def _check_device_status(self):
        """Verifica el estado de los dispositivos"""
        try:
            current_time = datetime.utcnow()
            
            for device_id, device in self.devices.items():
                # Verificar si el dispositivo está offline
                time_since_last_seen = current_time - device.last_seen
                
                if time_since_last_seen.total_seconds() > 300:  # 5 minutos
                    if device.status == SensorStatus.ONLINE:
                        device.status = SensorStatus.OFFLINE
                        self._create_device_alert(device, "Dispositivo offline detectado")
                
                # Verificar nivel de batería
                if device.battery_level is not None and device.battery_level < 20:
                    if device.status == SensorStatus.ONLINE:
                        self._create_device_alert(device, f"Batería baja: {device.battery_level:.1f}%")
                
                # Verificar fuerza de señal
                if device.signal_strength is not None and device.signal_strength < -70:
                    self._create_device_alert(device, f"Señal débil: {device.signal_strength:.1f} dBm")
                
                # Simular cambios de estado
                if random.random() < 0.01:  # 1% de probabilidad
                    if device.status == SensorStatus.ONLINE:
                        device.status = SensorStatus.ERROR
                        self._create_device_alert(device, "Error de dispositivo detectado")
                    elif device.status == SensorStatus.ERROR:
                        device.status = SensorStatus.ONLINE
                        self._create_device_alert(device, "Dispositivo recuperado")
        
        except Exception as e:
            self.logger.error(f'Error verificando estado de dispositivos: {str(e)}')
    
    def _create_device_alert(self, device: IoTDevice, message: str):
        """Crea alerta de dispositivo"""
        try:
            alert = {
                'device_id': device.device_id,
                'device_name': device.name,
                'message': message,
                'timestamp': datetime.utcnow(),
                'severity': 'medium',
                'location': device.location
            }
            
            self.alerts.append(alert)
            self.logger.info(f'Alerta IoT: {device.device_id} - {message}')
            
        except Exception as e:
            self.logger.error(f'Error creando alerta de dispositivo: {str(e)}')
    
    def _analyze_sensor_data(self):
        """Analiza datos de sensores y genera alertas"""
        try:
            if not self.sensor_data_history:
                return
            
            # Obtener datos recientes (últimos 5 minutos)
            cutoff_time = datetime.utcnow() - timedelta(minutes=5)
            recent_data = [
                data for data in self.sensor_data_history 
                if data.timestamp > cutoff_time
            ]
            
            # Agrupar por tipo de sensor
            sensor_groups = {}
            for data in recent_data:
                sensor_type = data.sensor_type
                if sensor_type not in sensor_groups:
                    sensor_groups[sensor_type] = []
                sensor_groups[sensor_type].append(data)
            
            # Analizar cada tipo de sensor
            for sensor_type, data_list in sensor_groups.items():
                if len(data_list) < 3:  # Necesitamos al menos 3 puntos de datos
                    continue
                
                values = [d.value for d in data_list]
                
                # Detectar anomalías
                if sensor_type == SensorType.TEMPERATURE:
                    if any(v > 30.0 or v < 10.0 for v in values):
                        self._create_sensor_alert(sensor_type, "Temperatura fuera de rango", values[-1])
                
                elif sensor_type == SensorType.HUMIDITY:
                    if any(v > 80.0 or v < 20.0 for v in values):
                        self._create_sensor_alert(sensor_type, "Humedad fuera de rango", values[-1])
                
                elif sensor_type == SensorType.MOTION:
                    if sum(values) > len(values) * 0.8:  # Mucho movimiento
                        self._create_sensor_alert(sensor_type, "Actividad inusual detectada", values[-1])
                
                elif sensor_type == SensorType.WEIGHT:
                    if any(v > 800.0 for v in values):  # Peso muy alto
                        self._create_sensor_alert(sensor_type, "Peso excesivo detectado", values[-1])
                
                # Detectar tendencias
                if len(values) >= 5:
                    trend = np.polyfit(range(len(values)), values, 1)[0]
                    
                    if sensor_type == SensorType.TEMPERATURE and abs(trend) > 0.5:
                        trend_direction = "aumentando" if trend > 0 else "disminuyendo"
                        self._create_sensor_alert(sensor_type, f"Temperatura {trend_direction} rápidamente", values[-1])
        
        except Exception as e:
            self.logger.error(f'Error analizando datos de sensores: {str(e)}')
    
    def _create_sensor_alert(self, sensor_type: SensorType, message: str, value: float):
        """Crea alerta de sensor"""
        try:
            alert = {
                'sensor_type': sensor_type.value,
                'message': message,
                'value': value,
                'timestamp': datetime.utcnow(),
                'severity': 'high' if 'fuera de rango' in message else 'medium'
            }
            
            self.alerts.append(alert)
            self.logger.info(f'Alerta de sensor: {sensor_type.value} - {message}')
            
        except Exception as e:
            self.logger.error(f'Error creando alerta de sensor: {str(e)}')
    
    def _cleanup_old_data(self):
        """Limpia datos antiguos"""
        try:
            cutoff_time = datetime.utcnow() - timedelta(hours=24)
            
            # Limpiar datos de sensores antiguos
            self.sensor_data_history = [
                data for data in self.sensor_data_history 
                if data.timestamp > cutoff_time
            ]
            
            # Limpiar alertas antiguas
            self.alerts = [
                alert for alert in self.alerts 
                if alert['timestamp'] > cutoff_time
            ]
        
        except Exception as e:
            self.logger.error(f'Error limpiando datos antiguos: {str(e)}')
    
    def get_device_status(self) -> Dict:
        """Obtiene estado de todos los dispositivos"""
        try:
            devices_data = []
            
            for device_id, device in self.devices.items():
                devices_data.append({
                    'device_id': device.device_id,
                    'name': device.name,
                    'device_type': device.device_type,
                    'location': device.location,
                    'status': device.status.value,
                    'sensors': device.sensors,
                    'last_seen': device.last_seen.isoformat(),
                    'firmware_version': device.firmware_version,
                    'battery_level': device.battery_level,
                    'signal_strength': device.signal_strength
                })
            
            return {
                'success': True,
                'devices': devices_data,
                'total_devices': len(devices_data),
                'online_devices': len([d for d in devices_data if d['status'] == 'online']),
                'offline_devices': len([d for d in devices_data if d['status'] == 'offline'])
            }
            
        except Exception as e:
            self.logger.error(f'Error obteniendo estado de dispositivos: {str(e)}')
            return {'success': False, 'error': str(e)}
    
    def get_sensor_data(self, sensor_id: str = None, hours: int = 24) -> Dict:
        """Obtiene datos de sensores"""
        try:
            cutoff_time = datetime.utcnow() - timedelta(hours=hours)
            
            if sensor_id:
                data = [
                    data for data in self.sensor_data_history 
                    if data.sensor_id == sensor_id and data.timestamp > cutoff_time
                ]
            else:
                data = [
                    data for data in self.sensor_data_history 
                    if data.timestamp > cutoff_time
                ]
            
            # Convertir a formato JSON serializable
            data_json = []
            for d in data:
                data_json.append({
                    'sensor_id': d.sensor_id,
                    'sensor_type': d.sensor_type.value,
                    'value': d.value,
                    'unit': d.unit,
                    'timestamp': d.timestamp.isoformat(),
                    'location': d.location,
                    'quality': d.quality,
                    'battery_level': d.battery_level,
                    'signal_strength': d.signal_strength
                })
            
            return {
                'success': True,
                'sensor_data': data_json,
                'total_records': len(data_json),
                'sensor_id': sensor_id,
                'hours': hours
            }
            
        except Exception as e:
            self.logger.error(f'Error obteniendo datos de sensores: {str(e)}')
            return {'success': False, 'error': str(e)}
    
    def get_alerts(self) -> Dict:
        """Obtiene alertas IoT"""
        try:
            # Ordenar alertas por timestamp (más recientes primero)
            sorted_alerts = sorted(self.alerts, key=lambda x: x['timestamp'], reverse=True)
            
            return {
                'success': True,
                'alerts': sorted_alerts[:50],  # Últimas 50 alertas
                'total_alerts': len(self.alerts)
            }
            
        except Exception as e:
            self.logger.error(f'Error obteniendo alertas IoT: {str(e)}')
            return {'success': False, 'error': str(e)}
    
    def get_dashboard_data(self) -> Dict:
        """Obtiene datos para dashboard IoT"""
        try:
            # Estadísticas de dispositivos
            total_devices = len(self.devices)
            online_devices = len([d for d in self.devices.values() if d.status == SensorStatus.ONLINE])
            offline_devices = len([d for d in self.devices.values() if d.status == SensorStatus.OFFLINE])
            
            # Estadísticas de sensores
            total_sensors = sum(len(device.sensors) for device in self.devices.values())
            
            # Datos recientes
            recent_data = [
                data for data in self.sensor_data_history 
                if data.timestamp > datetime.utcnow() - timedelta(minutes=10)
            ]
            
            # Alertas recientes
            recent_alerts = [
                alert for alert in self.alerts 
                if alert['timestamp'] > datetime.utcnow() - timedelta(hours=1)
            ]
            
            # Métricas por tipo de sensor
            sensor_metrics = {}
            for data in recent_data:
                sensor_type = data.sensor_type.value
                if sensor_type not in sensor_metrics:
                    sensor_metrics[sensor_type] = {
                        'count': 0,
                        'avg_value': 0,
                        'min_value': float('inf'),
                        'max_value': float('-inf')
                    }
                
                metrics = sensor_metrics[sensor_type]
                metrics['count'] += 1
                metrics['avg_value'] += data.value
                metrics['min_value'] = min(metrics['min_value'], data.value)
                metrics['max_value'] = max(metrics['max_value'], data.value)
            
            # Calcular promedios
            for sensor_type, metrics in sensor_metrics.items():
                if metrics['count'] > 0:
                    metrics['avg_value'] /= metrics['count']
                if metrics['min_value'] == float('inf'):
                    metrics['min_value'] = 0
                if metrics['max_value'] == float('-inf'):
                    metrics['max_value'] = 0
            
            return {
                'success': True,
                'dashboard': {
                    'devices': {
                        'total': total_devices,
                        'online': online_devices,
                        'offline': offline_devices,
                        'uptime_percentage': (online_devices / total_devices * 100) if total_devices > 0 else 0
                    },
                    'sensors': {
                        'total': total_sensors,
                        'active': len(recent_data),
                        'metrics': sensor_metrics
                    },
                    'alerts': {
                        'total': len(self.alerts),
                        'recent': len(recent_alerts),
                        'critical': len([a for a in recent_alerts if a.get('severity') == 'high'])
                    },
                    'monitoring': {
                        'is_active': self.is_monitoring,
                        'last_update': datetime.utcnow().isoformat()
                    }
                }
            }
            
        except Exception as e:
            self.logger.error(f'Error obteniendo datos de dashboard IoT: {str(e)}')
            return {'success': False, 'error': str(e)}

# Instancia global del servicio IoT
iot_monitoring_service = IoTMonitoringService()



