#!/usr/bin/env python3
"""
ClickUp Brain IoT Integration System
==================================

IoT device integration for smart office monitoring, environmental sensors,
device management, and automated efficiency optimization.
"""

import os
import json
import logging
import time
import asyncio
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, asdict
from enum import Enum
import uuid
import threading
import random
import math

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class IoTDeviceType(Enum):
    """IoT device types"""
    ENVIRONMENTAL_SENSOR = "environmental_sensor"
    OCCUPANCY_SENSOR = "occupancy_sensor"
    ENERGY_MONITOR = "energy_monitor"
    AIR_QUALITY_SENSOR = "air_quality_sensor"
    NOISE_SENSOR = "noise_sensor"
    LIGHTING_CONTROL = "lighting_control"
    TEMPERATURE_CONTROL = "temperature_control"
    SMART_DESK = "smart_desk"
    MEETING_ROOM_SENSOR = "meeting_room_sensor"
    BIOMETRIC_SENSOR = "biometric_sensor"
    PRODUCTIVITY_TRACKER = "productivity_tracker"
    WEARABLE_DEVICE = "wearable_device"

class DeviceStatus(Enum):
    """Device status"""
    ONLINE = "online"
    OFFLINE = "offline"
    MAINTENANCE = "maintenance"
    ERROR = "error"
    CALIBRATING = "calibrating"
    SLEEPING = "sleeping"

class DataType(Enum):
    """Data types"""
    TEMPERATURE = "temperature"
    HUMIDITY = "humidity"
    AIR_QUALITY = "air_quality"
    NOISE_LEVEL = "noise_level"
    LIGHT_LEVEL = "light_level"
    OCCUPANCY = "occupancy"
    ENERGY_USAGE = "energy_usage"
    MOTION = "motion"
    HEART_RATE = "heart_rate"
    STRESS_LEVEL = "stress_level"
    PRODUCTIVITY_SCORE = "productivity_score"
    FOCUS_TIME = "focus_time"

@dataclass
class IoTDevice:
    """IoT device data structure"""
    device_id: str
    device_type: IoTDeviceType
    name: str
    location: str
    status: DeviceStatus
    ip_address: str
    mac_address: str
    firmware_version: str
    battery_level: Optional[int] = None
    signal_strength: Optional[int] = None
    last_seen: str = None
    created_at: str = None
    is_active: bool = True

@dataclass
class SensorData:
    """Sensor data structure"""
    data_id: str
    device_id: str
    data_type: DataType
    value: float
    unit: str
    timestamp: str
    quality_score: float
    location: str
    metadata: Dict[str, Any] = None

@dataclass
class IoTAlert:
    """IoT alert data structure"""
    alert_id: str
    device_id: str
    alert_type: str
    severity: str
    message: str
    timestamp: str
    is_resolved: bool = False
    resolution_notes: str = None

@dataclass
class EnvironmentalConditions:
    """Environmental conditions data structure"""
    location: str
    temperature: float
    humidity: float
    air_quality_index: float
    noise_level: float
    light_level: float
    occupancy_count: int
    timestamp: str
    comfort_score: float

class IoTDeviceManager:
    """IoT device manager"""
    
    def __init__(self):
        """Initialize IoT device manager"""
        self.devices = {}
        self.device_types = {
            IoTDeviceType.ENVIRONMENTAL_SENSOR: {
                'name': 'Environmental Sensor',
                'data_types': [DataType.TEMPERATURE, DataType.HUMIDITY, DataType.AIR_QUALITY],
                'update_interval': 60,  # seconds
                'battery_life': 365  # days
            },
            IoTDeviceType.OCCUPANCY_SENSOR: {
                'name': 'Occupancy Sensor',
                'data_types': [DataType.OCCUPANCY, DataType.MOTION],
                'update_interval': 30,
                'battery_life': 180
            },
            IoTDeviceType.ENERGY_MONITOR: {
                'name': 'Energy Monitor',
                'data_types': [DataType.ENERGY_USAGE],
                'update_interval': 15,
                'battery_life': 90
            },
            IoTDeviceType.AIR_QUALITY_SENSOR: {
                'name': 'Air Quality Sensor',
                'data_types': [DataType.AIR_QUALITY],
                'update_interval': 120,
                'battery_life': 200
            },
            IoTDeviceType.NOISE_SENSOR: {
                'name': 'Noise Sensor',
                'data_types': [DataType.NOISE_LEVEL],
                'update_interval': 10,
                'battery_life': 150
            },
            IoTDeviceType.SMART_DESK: {
                'name': 'Smart Desk',
                'data_types': [DataType.OCCUPANCY, DataType.PRODUCTIVITY_SCORE],
                'update_interval': 5,
                'battery_life': 30
            },
            IoTDeviceType.WEARABLE_DEVICE: {
                'name': 'Wearable Device',
                'data_types': [DataType.HEART_RATE, DataType.STRESS_LEVEL, DataType.FOCUS_TIME],
                'update_interval': 1,
                'battery_life': 7
            }
        }
    
    def register_device(self, device_type: IoTDeviceType, name: str, 
                       location: str, ip_address: str) -> IoTDevice:
        """Register new IoT device"""
        try:
            device_id = str(uuid.uuid4())
            
            device = IoTDevice(
                device_id=device_id,
                device_type=device_type,
                name=name,
                location=location,
                status=DeviceStatus.ONLINE,
                ip_address=ip_address,
                mac_address=f"MAC:{':'.join([f'{random.randint(0, 255):02x}' for _ in range(6)])}",
                firmware_version="1.0.0",
                battery_level=100,
                signal_strength=random.randint(80, 100),
                last_seen=datetime.now().isoformat(),
                created_at=datetime.now().isoformat()
            )
            
            self.devices[device_id] = device
            logger.info(f"Registered IoT device: {name} ({device_type.value})")
            return device
            
        except Exception as e:
            logger.error(f"Error registering device: {e}")
            return None
    
    def get_device_status(self, device_id: str) -> Dict[str, Any]:
        """Get device status"""
        try:
            if device_id not in self.devices:
                return {"error": "Device not found"}
            
            device = self.devices[device_id]
            device_info = self.device_types.get(device.device_type, {})
            
            return {
                'device_id': device_id,
                'name': device.name,
                'type': device.device_type.value,
                'status': device.status.value,
                'location': device.location,
                'battery_level': device.battery_level,
                'signal_strength': device.signal_strength,
                'last_seen': device.last_seen,
                'data_types': [dt.value for dt in device_info.get('data_types', [])],
                'update_interval': device_info.get('update_interval', 60),
                'is_healthy': device.status == DeviceStatus.ONLINE
            }
            
        except Exception as e:
            logger.error(f"Error getting device status: {e}")
            return {"error": str(e)}
    
    def update_device_status(self, device_id: str, status: DeviceStatus, 
                           battery_level: Optional[int] = None) -> bool:
        """Update device status"""
        try:
            if device_id not in self.devices:
                return False
            
            device = self.devices[device_id]
            device.status = status
            device.last_seen = datetime.now().isoformat()
            
            if battery_level is not None:
                device.battery_level = battery_level
            
            logger.info(f"Updated device status: {device_id} -> {status.value}")
            return True
            
        except Exception as e:
            logger.error(f"Error updating device status: {e}")
            return False

class SensorDataCollector:
    """Sensor data collector"""
    
    def __init__(self, device_manager: IoTDeviceManager):
        """Initialize sensor data collector"""
        self.device_manager = device_manager
        self.sensor_data = []
        self.data_collection_active = False
        self.collection_thread = None
    
    def start_data_collection(self):
        """Start continuous data collection"""
        try:
            if not self.data_collection_active:
                self.data_collection_active = True
                self.collection_thread = threading.Thread(target=self._collect_data_loop)
                self.collection_thread.daemon = True
                self.collection_thread.start()
                logger.info("Started IoT data collection")
            
        except Exception as e:
            logger.error(f"Error starting data collection: {e}")
    
    def stop_data_collection(self):
        """Stop data collection"""
        try:
            self.data_collection_active = False
            if self.collection_thread:
                self.collection_thread.join(timeout=5)
            logger.info("Stopped IoT data collection")
            
        except Exception as e:
            logger.error(f"Error stopping data collection: {e}")
    
    def _collect_data_loop(self):
        """Data collection loop"""
        while self.data_collection_active:
            try:
                for device_id, device in self.device_manager.devices.items():
                    if device.status == DeviceStatus.ONLINE:
                        self._collect_device_data(device)
                
                time.sleep(10)  # Collect data every 10 seconds
                
            except Exception as e:
                logger.error(f"Error in data collection loop: {e}")
                time.sleep(5)
    
    def _collect_device_data(self, device: IoTDevice):
        """Collect data from specific device"""
        try:
            device_info = self.device_manager.device_types.get(device.device_type, {})
            data_types = device_info.get('data_types', [])
            
            for data_type in data_types:
                sensor_data = self._generate_sensor_data(device, data_type)
                if sensor_data:
                    self.sensor_data.append(sensor_data)
            
            # Keep only last 10000 data points
            if len(self.sensor_data) > 10000:
                self.sensor_data = self.sensor_data[-10000:]
                
        except Exception as e:
            logger.error(f"Error collecting device data: {e}")
    
    def _generate_sensor_data(self, device: IoTDevice, data_type: DataType) -> SensorData:
        """Generate realistic sensor data"""
        try:
            # Generate realistic values based on data type
            if data_type == DataType.TEMPERATURE:
                value = random.uniform(18.0, 25.0)  # Celsius
                unit = "°C"
            elif data_type == DataType.HUMIDITY:
                value = random.uniform(30.0, 70.0)  # Percentage
                unit = "%"
            elif data_type == DataType.AIR_QUALITY:
                value = random.uniform(0, 500)  # AQI
                unit = "AQI"
            elif data_type == DataType.NOISE_LEVEL:
                value = random.uniform(30.0, 80.0)  # dB
                unit = "dB"
            elif data_type == DataType.LIGHT_LEVEL:
                value = random.uniform(100, 1000)  # Lux
                unit = "lux"
            elif data_type == DataType.OCCUPANCY:
                value = random.randint(0, 10)  # People count
                unit = "people"
            elif data_type == DataType.ENERGY_USAGE:
                value = random.uniform(0.5, 5.0)  # kWh
                unit = "kWh"
            elif data_type == DataType.HEART_RATE:
                value = random.uniform(60, 100)  # BPM
                unit = "BPM"
            elif data_type == DataType.STRESS_LEVEL:
                value = random.uniform(0, 100)  # Stress index
                unit = "index"
            elif data_type == DataType.PRODUCTIVITY_SCORE:
                value = random.uniform(0, 100)  # Productivity score
                unit = "score"
            elif data_type == DataType.FOCUS_TIME:
                value = random.uniform(0, 480)  # Minutes
                unit = "minutes"
            else:
                value = random.uniform(0, 100)
                unit = "units"
            
            # Calculate quality score based on device status
            quality_score = 1.0
            if device.battery_level and device.battery_level < 20:
                quality_score *= 0.8
            if device.signal_strength and device.signal_strength < 70:
                quality_score *= 0.9
            
            return SensorData(
                data_id=str(uuid.uuid4()),
                device_id=device.device_id,
                data_type=data_type,
                value=value,
                unit=unit,
                timestamp=datetime.now().isoformat(),
                quality_score=quality_score,
                location=device.location,
                metadata={
                    'device_type': device.device_type.value,
                    'firmware_version': device.firmware_version,
                    'battery_level': device.battery_level,
                    'signal_strength': device.signal_strength
                }
            )
            
        except Exception as e:
            logger.error(f"Error generating sensor data: {e}")
            return None
    
    def get_latest_data(self, device_id: Optional[str] = None, 
                       data_type: Optional[DataType] = None) -> List[SensorData]:
        """Get latest sensor data"""
        try:
            filtered_data = self.sensor_data
            
            if device_id:
                filtered_data = [d for d in filtered_data if d.device_id == device_id]
            
            if data_type:
                filtered_data = [d for d in filtered_data if d.data_type == data_type]
            
            # Sort by timestamp and return latest
            filtered_data.sort(key=lambda x: x.timestamp, reverse=True)
            return filtered_data[:100]  # Return latest 100 data points
            
        except Exception as e:
            logger.error(f"Error getting latest data: {e}")
            return []

class EnvironmentalAnalyzer:
    """Environmental conditions analyzer"""
    
    def __init__(self, data_collector: SensorDataCollector):
        """Initialize environmental analyzer"""
        self.data_collector = data_collector
    
    def analyze_environmental_conditions(self, location: str) -> EnvironmentalConditions:
        """Analyze environmental conditions for location"""
        try:
            # Get latest data for location
            latest_data = self.data_collector.get_latest_data()
            location_data = [d for d in latest_data if d.location == location]
            
            if not location_data:
                return self._generate_default_conditions(location)
            
            # Calculate averages for each data type
            conditions = {
                'temperature': self._calculate_average(location_data, DataType.TEMPERATURE, 22.0),
                'humidity': self._calculate_average(location_data, DataType.HUMIDITY, 50.0),
                'air_quality_index': self._calculate_average(location_data, DataType.AIR_QUALITY, 100.0),
                'noise_level': self._calculate_average(location_data, DataType.NOISE_LEVEL, 50.0),
                'light_level': self._calculate_average(location_data, DataType.LIGHT_LEVEL, 500.0),
                'occupancy_count': int(self._calculate_average(location_data, DataType.OCCUPANCY, 0))
            }
            
            # Calculate comfort score
            comfort_score = self._calculate_comfort_score(conditions)
            
            return EnvironmentalConditions(
                location=location,
                temperature=conditions['temperature'],
                humidity=conditions['humidity'],
                air_quality_index=conditions['air_quality_index'],
                noise_level=conditions['noise_level'],
                light_level=conditions['light_level'],
                occupancy_count=conditions['occupancy_count'],
                timestamp=datetime.now().isoformat(),
                comfort_score=comfort_score
            )
            
        except Exception as e:
            logger.error(f"Error analyzing environmental conditions: {e}")
            return self._generate_default_conditions(location)
    
    def _calculate_average(self, data: List[SensorData], data_type: DataType, default: float) -> float:
        """Calculate average for specific data type"""
        try:
            filtered_data = [d for d in data if d.data_type == data_type]
            if not filtered_data:
                return default
            
            return sum(d.value for d in filtered_data) / len(filtered_data)
            
        except Exception as e:
            logger.error(f"Error calculating average: {e}")
            return default
    
    def _calculate_comfort_score(self, conditions: Dict[str, float]) -> float:
        """Calculate environmental comfort score"""
        try:
            score = 100.0
            
            # Temperature comfort (optimal: 20-24°C)
            temp = conditions['temperature']
            if temp < 18 or temp > 26:
                score -= 20
            elif temp < 20 or temp > 24:
                score -= 10
            
            # Humidity comfort (optimal: 40-60%)
            humidity = conditions['humidity']
            if humidity < 30 or humidity > 70:
                score -= 15
            elif humidity < 40 or humidity > 60:
                score -= 5
            
            # Air quality (optimal: < 100 AQI)
            aqi = conditions['air_quality_index']
            if aqi > 200:
                score -= 25
            elif aqi > 100:
                score -= 10
            
            # Noise level (optimal: < 50 dB)
            noise = conditions['noise_level']
            if noise > 70:
                score -= 20
            elif noise > 50:
                score -= 10
            
            # Light level (optimal: 300-700 lux)
            light = conditions['light_level']
            if light < 200 or light > 1000:
                score -= 15
            elif light < 300 or light > 700:
                score -= 5
            
            return max(0, min(100, score))
            
        except Exception as e:
            logger.error(f"Error calculating comfort score: {e}")
            return 50.0
    
    def _generate_default_conditions(self, location: str) -> EnvironmentalConditions:
        """Generate default environmental conditions"""
        return EnvironmentalConditions(
            location=location,
            temperature=22.0,
            humidity=50.0,
            air_quality_index=100.0,
            noise_level=50.0,
            light_level=500.0,
            occupancy_count=0,
            timestamp=datetime.now().isoformat(),
            comfort_score=75.0
        )

class IoTAlertManager:
    """IoT alert manager"""
    
    def __init__(self):
        """Initialize alert manager"""
        self.alerts = []
        self.alert_rules = {
            'high_temperature': {'threshold': 26.0, 'severity': 'warning'},
            'low_temperature': {'threshold': 18.0, 'severity': 'warning'},
            'high_humidity': {'threshold': 70.0, 'severity': 'info'},
            'low_humidity': {'threshold': 30.0, 'severity': 'info'},
            'poor_air_quality': {'threshold': 150.0, 'severity': 'critical'},
            'high_noise': {'threshold': 70.0, 'severity': 'warning'},
            'low_battery': {'threshold': 20, 'severity': 'warning'},
            'device_offline': {'threshold': 300, 'severity': 'critical'}  # 5 minutes
        }
    
    def check_alerts(self, sensor_data: List[SensorData], devices: Dict[str, IoTDevice]) -> List[IoTAlert]:
        """Check for alerts based on sensor data"""
        try:
            new_alerts = []
            
            # Check environmental alerts
            for data in sensor_data:
                alert = self._check_data_alerts(data)
                if alert:
                    new_alerts.append(alert)
            
            # Check device alerts
            for device_id, device in devices.items():
                alert = self._check_device_alerts(device)
                if alert:
                    new_alerts.append(alert)
            
            # Add new alerts
            self.alerts.extend(new_alerts)
            
            # Keep only last 1000 alerts
            if len(self.alerts) > 1000:
                self.alerts = self.alerts[-1000:]
            
            return new_alerts
            
        except Exception as e:
            logger.error(f"Error checking alerts: {e}")
            return []
    
    def _check_data_alerts(self, data: SensorData) -> Optional[IoTAlert]:
        """Check alerts for sensor data"""
        try:
            if data.data_type == DataType.TEMPERATURE:
                if data.value > self.alert_rules['high_temperature']['threshold']:
                    return self._create_alert(
                        data.device_id,
                        'high_temperature',
                        self.alert_rules['high_temperature']['severity'],
                        f"High temperature detected: {data.value:.1f}°C"
                    )
                elif data.value < self.alert_rules['low_temperature']['threshold']:
                    return self._create_alert(
                        data.device_id,
                        'low_temperature',
                        self.alert_rules['low_temperature']['severity'],
                        f"Low temperature detected: {data.value:.1f}°C"
                    )
            
            elif data.data_type == DataType.HUMIDITY:
                if data.value > self.alert_rules['high_humidity']['threshold']:
                    return self._create_alert(
                        data.device_id,
                        'high_humidity',
                        self.alert_rules['high_humidity']['severity'],
                        f"High humidity detected: {data.value:.1f}%"
                    )
                elif data.value < self.alert_rules['low_humidity']['threshold']:
                    return self._create_alert(
                        data.device_id,
                        'low_humidity',
                        self.alert_rules['low_humidity']['severity'],
                        f"Low humidity detected: {data.value:.1f}%"
                    )
            
            elif data.data_type == DataType.AIR_QUALITY:
                if data.value > self.alert_rules['poor_air_quality']['threshold']:
                    return self._create_alert(
                        data.device_id,
                        'poor_air_quality',
                        self.alert_rules['poor_air_quality']['severity'],
                        f"Poor air quality detected: {data.value:.1f} AQI"
                    )
            
            elif data.data_type == DataType.NOISE_LEVEL:
                if data.value > self.alert_rules['high_noise']['threshold']:
                    return self._create_alert(
                        data.device_id,
                        'high_noise',
                        self.alert_rules['high_noise']['severity'],
                        f"High noise level detected: {data.value:.1f} dB"
                    )
            
            return None
            
        except Exception as e:
            logger.error(f"Error checking data alerts: {e}")
            return None
    
    def _check_device_alerts(self, device: IoTDevice) -> Optional[IoTAlert]:
        """Check alerts for device status"""
        try:
            # Check battery level
            if device.battery_level and device.battery_level < self.alert_rules['low_battery']['threshold']:
                return self._create_alert(
                    device.device_id,
                    'low_battery',
                    self.alert_rules['low_battery']['severity'],
                    f"Low battery level: {device.battery_level}%"
                )
            
            # Check if device is offline
            if device.status == DeviceStatus.OFFLINE:
                last_seen = datetime.fromisoformat(device.last_seen)
                offline_duration = (datetime.now() - last_seen).total_seconds()
                
                if offline_duration > self.alert_rules['device_offline']['threshold']:
                    return self._create_alert(
                        device.device_id,
                        'device_offline',
                        self.alert_rules['device_offline']['severity'],
                        f"Device offline for {offline_duration/60:.1f} minutes"
                    )
            
            return None
            
        except Exception as e:
            logger.error(f"Error checking device alerts: {e}")
            return None
    
    def _create_alert(self, device_id: str, alert_type: str, 
                     severity: str, message: str) -> IoTAlert:
        """Create new alert"""
        return IoTAlert(
            alert_id=str(uuid.uuid4()),
            device_id=device_id,
            alert_type=alert_type,
            severity=severity,
            message=message,
            timestamp=datetime.now().isoformat()
        )
    
    def get_active_alerts(self) -> List[IoTAlert]:
        """Get active alerts"""
        return [alert for alert in self.alerts if not alert.is_resolved]
    
    def resolve_alert(self, alert_id: str, resolution_notes: str) -> bool:
        """Resolve alert"""
        try:
            for alert in self.alerts:
                if alert.alert_id == alert_id:
                    alert.is_resolved = True
                    alert.resolution_notes = resolution_notes
                    logger.info(f"Resolved alert: {alert_id}")
                    return True
            
            return False
            
        except Exception as e:
            logger.error(f"Error resolving alert: {e}")
            return False

class ClickUpBrainIoTSystem:
    """Main IoT integration system for ClickUp Brain"""
    
    def __init__(self):
        """Initialize IoT system"""
        self.device_manager = IoTDeviceManager()
        self.data_collector = SensorDataCollector(self.device_manager)
        self.environmental_analyzer = EnvironmentalAnalyzer(self.data_collector)
        self.alert_manager = IoTAlertManager()
        
        # Setup default devices
        self._setup_default_devices()
    
    def _setup_default_devices(self):
        """Setup default IoT devices"""
        try:
            # Environmental sensors
            self.device_manager.register_device(
                IoTDeviceType.ENVIRONMENTAL_SENSOR,
                "Office Environmental Sensor",
                "Main Office",
                "192.168.1.100"
            )
            
            self.device_manager.register_device(
                IoTDeviceType.ENVIRONMENTAL_SENSOR,
                "Meeting Room Sensor",
                "Conference Room A",
                "192.168.1.101"
            )
            
            # Occupancy sensors
            self.device_manager.register_device(
                IoTDeviceType.OCCUPANCY_SENSOR,
                "Office Occupancy Sensor",
                "Main Office",
                "192.168.1.102"
            )
            
            # Energy monitors
            self.device_manager.register_device(
                IoTDeviceType.ENERGY_MONITOR,
                "Office Energy Monitor",
                "Main Office",
                "192.168.1.103"
            )
            
            # Smart desks
            self.device_manager.register_device(
                IoTDeviceType.SMART_DESK,
                "Smart Desk 1",
                "Desk Area 1",
                "192.168.1.104"
            )
            
            self.device_manager.register_device(
                IoTDeviceType.SMART_DESK,
                "Smart Desk 2",
                "Desk Area 2",
                "192.168.1.105"
            )
            
            # Wearable devices
            self.device_manager.register_device(
                IoTDeviceType.WEARABLE_DEVICE,
                "Team Lead Wearable",
                "Main Office",
                "192.168.1.106"
            )
            
            logger.info("Setup default IoT devices")
            
        except Exception as e:
            logger.error(f"Error setting up default devices: {e}")
    
    def start_monitoring(self):
        """Start IoT monitoring"""
        try:
            self.data_collector.start_data_collection()
            logger.info("Started IoT monitoring")
            
        except Exception as e:
            logger.error(f"Error starting monitoring: {e}")
    
    def stop_monitoring(self):
        """Stop IoT monitoring"""
        try:
            self.data_collector.stop_data_collection()
            logger.info("Stopped IoT monitoring")
            
        except Exception as e:
            logger.error(f"Error stopping monitoring: {e}")
    
    def get_environmental_analysis(self, location: str) -> EnvironmentalConditions:
        """Get environmental analysis for location"""
        return self.environmental_analyzer.analyze_environmental_conditions(location)
    
    def get_device_status_summary(self) -> Dict[str, Any]:
        """Get device status summary"""
        try:
            total_devices = len(self.device_manager.devices)
            online_devices = len([d for d in self.device_manager.devices.values() 
                                if d.status == DeviceStatus.ONLINE])
            offline_devices = len([d for d in self.device_manager.devices.values() 
                                 if d.status == DeviceStatus.OFFLINE])
            
            device_types = {}
            for device in self.device_manager.devices.values():
                device_type = device.device_type.value
                device_types[device_type] = device_types.get(device_type, 0) + 1
            
            return {
                'total_devices': total_devices,
                'online_devices': online_devices,
                'offline_devices': offline_devices,
                'device_types': device_types,
                'data_points_collected': len(self.data_collector.sensor_data),
                'active_alerts': len(self.alert_manager.get_active_alerts()),
                'monitoring_active': self.data_collector.data_collection_active
            }
            
        except Exception as e:
            logger.error(f"Error getting device status summary: {e}")
            return {"error": str(e)}
    
    def get_productivity_insights(self) -> Dict[str, Any]:
        """Get productivity insights from IoT data"""
        try:
            # Get latest sensor data
            latest_data = self.data_collector.get_latest_data()
            
            # Analyze productivity-related data
            productivity_data = [d for d in latest_data 
                               if d.data_type in [DataType.PRODUCTIVITY_SCORE, DataType.FOCUS_TIME]]
            
            if not productivity_data:
                return {"error": "No productivity data available"}
            
            # Calculate insights
            avg_productivity = sum(d.value for d in latest_data 
                                 if d.data_type == DataType.PRODUCTIVITY_SCORE) / max(
                len([d for d in latest_data if d.data_type == DataType.PRODUCTIVITY_SCORE]), 1)
            
            avg_focus_time = sum(d.value for d in latest_data 
                               if d.data_type == DataType.FOCUS_TIME) / max(
                len([d for d in latest_data if d.data_type == DataType.FOCUS_TIME]), 1)
            
            # Environmental impact on productivity
            environmental_conditions = self.get_environmental_analysis("Main Office")
            
            return {
                'average_productivity_score': avg_productivity,
                'average_focus_time': avg_focus_time,
                'environmental_comfort_score': environmental_conditions.comfort_score,
                'optimal_conditions': environmental_conditions.comfort_score > 80,
                'recommendations': self._generate_productivity_recommendations(
                    avg_productivity, avg_focus_time, environmental_conditions
                ),
                'data_points_analyzed': len(productivity_data)
            }
            
        except Exception as e:
            logger.error(f"Error getting productivity insights: {e}")
            return {"error": str(e)}
    
    def _generate_productivity_recommendations(self, productivity_score: float, 
                                             focus_time: float, 
                                             conditions: EnvironmentalConditions) -> List[str]:
        """Generate productivity recommendations"""
        recommendations = []
        
        if conditions.comfort_score < 70:
            recommendations.append("Improve environmental conditions for better productivity")
        
        if conditions.temperature < 20 or conditions.temperature > 24:
            recommendations.append("Adjust temperature to optimal range (20-24°C)")
        
        if conditions.humidity < 40 or conditions.humidity > 60:
            recommendations.append("Maintain humidity between 40-60%")
        
        if conditions.noise_level > 60:
            recommendations.append("Reduce noise levels for better focus")
        
        if conditions.light_level < 300 or conditions.light_level > 700:
            recommendations.append("Optimize lighting levels (300-700 lux)")
        
        if productivity_score < 70:
            recommendations.append("Consider productivity training or workspace optimization")
        
        if focus_time < 120:  # Less than 2 hours
            recommendations.append("Implement focus time blocks and minimize distractions")
        
        return recommendations
    
    def export_iot_data(self, export_format: str = 'json') -> Dict[str, Any]:
        """Export IoT data"""
        try:
            export_data = {
                'devices': [asdict(device) for device in self.device_manager.devices.values()],
                'sensor_data': [asdict(data) for data in self.data_collector.sensor_data[-1000:]],  # Last 1000 points
                'alerts': [asdict(alert) for alert in self.alert_manager.alerts[-100:]],  # Last 100 alerts
                'environmental_conditions': asdict(self.get_environmental_analysis("Main Office")),
                'device_status_summary': self.get_device_status_summary(),
                'productivity_insights': self.get_productivity_insights(),
                'export_timestamp': datetime.now().isoformat(),
                'export_format': export_format
            }
            
            return export_data
            
        except Exception as e:
            logger.error(f"Error exporting IoT data: {e}")
            return {"error": str(e)}

def main():
    """Main function for testing"""
    print("🌐 ClickUp Brain IoT Integration System")
    print("=" * 50)
    
    # Initialize IoT system
    iot_system = ClickUpBrainIoTSystem()
    
    print("🌐 IoT Features:")
    print("  • Environmental monitoring (temperature, humidity, air quality)")
    print("  • Occupancy and motion detection")
    print("  • Energy usage monitoring")
    print("  • Smart desk integration")
    print("  • Wearable device tracking")
    print("  • Real-time alert system")
    print("  • Productivity insights")
    print("  • Environmental comfort analysis")
    print("  • Device health monitoring")
    print("  • Automated recommendations")
    
    print(f"\n📊 Device Status Summary:")
    status_summary = iot_system.get_device_status_summary()
    print(f"  • Total Devices: {status_summary.get('total_devices', 0)}")
    print(f"  • Online Devices: {status_summary.get('online_devices', 0)}")
    print(f"  • Offline Devices: {status_summary.get('offline_devices', 0)}")
    print(f"  • Data Points: {status_summary.get('data_points_collected', 0)}")
    print(f"  • Active Alerts: {status_summary.get('active_alerts', 0)}")
    print(f"  • Monitoring Active: {status_summary.get('monitoring_active', False)}")
    
    # Start monitoring
    print(f"\n🔄 Starting IoT Monitoring:")
    iot_system.start_monitoring()
    
    # Wait for some data collection
    print("  ⏳ Collecting data for 30 seconds...")
    time.sleep(30)
    
    # Get environmental analysis
    print(f"\n🌡️ Environmental Analysis:")
    env_analysis = iot_system.get_environmental_analysis("Main Office")
    print(f"  • Location: {env_analysis.location}")
    print(f"  • Temperature: {env_analysis.temperature:.1f}°C")
    print(f"  • Humidity: {env_analysis.humidity:.1f}%")
    print(f"  • Air Quality: {env_analysis.air_quality_index:.1f} AQI")
    print(f"  • Noise Level: {env_analysis.noise_level:.1f} dB")
    print(f"  • Light Level: {env_analysis.light_level:.1f} lux")
    print(f"  • Occupancy: {env_analysis.occupancy_count} people")
    print(f"  • Comfort Score: {env_analysis.comfort_score:.1f}/100")
    
    # Get productivity insights
    print(f"\n📈 Productivity Insights:")
    productivity_insights = iot_system.get_productivity_insights()
    
    if 'error' not in productivity_insights:
        print(f"  • Average Productivity Score: {productivity_insights.get('average_productivity_score', 0):.1f}")
        print(f"  • Average Focus Time: {productivity_insights.get('average_focus_time', 0):.1f} minutes")
        print(f"  • Environmental Comfort: {productivity_insights.get('environmental_comfort_score', 0):.1f}/100")
        print(f"  • Optimal Conditions: {productivity_insights.get('optimal_conditions', False)}")
        print(f"  • Data Points Analyzed: {productivity_insights.get('data_points_analyzed', 0)}")
        
        recommendations = productivity_insights.get('recommendations', [])
        if recommendations:
            print(f"  • Recommendations:")
            for rec in recommendations[:3]:  # Show first 3 recommendations
                print(f"    - {rec}")
    else:
        print(f"  ❌ Error: {productivity_insights['error']}")
    
    # Check alerts
    print(f"\n🚨 Active Alerts:")
    active_alerts = iot_system.alert_manager.get_active_alerts()
    if active_alerts:
        for alert in active_alerts[:5]:  # Show first 5 alerts
            print(f"  • {alert.alert_type.upper()}: {alert.message}")
            print(f"    Device: {alert.device_id}, Severity: {alert.severity}")
    else:
        print("  ✅ No active alerts")
    
    # Stop monitoring
    print(f"\n⏹️ Stopping IoT Monitoring:")
    iot_system.stop_monitoring()
    
    print(f"\n🎯 IoT System Ready!")
    print(f"Smart office monitoring for ClickUp Brain system")

if __name__ == "__main__":
    main()










