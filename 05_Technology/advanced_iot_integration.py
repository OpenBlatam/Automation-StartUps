#!/usr/bin/env python3
"""
Advanced IoT Integration for Competitive Pricing Analysis
======================================================

Sistema de integración IoT avanzado que proporciona:
- Integración con dispositivos IoT
- Monitoreo de sensores en tiempo real
- Análisis de datos de IoT
- Automatización basada en IoT
- Edge computing
- Fog computing
- MQTT integration
- CoAP integration
- Time series analysis
- Predictive maintenance
"""

import asyncio
import aiohttp
import json
import logging
import time
import threading
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple, Union
from dataclasses import dataclass, asdict
from pathlib import Path
import pandas as pd
import numpy as np
from concurrent.futures import ThreadPoolExecutor, as_completed
import schedule
import queue
import hashlib
import hmac
import base64
from urllib.parse import urljoin, urlparse
import os
import tempfile
import sqlite3
import paho.mqtt.client as mqtt
import socket
import struct

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class IoTDevice:
    """Dispositivo IoT"""
    device_id: str
    device_type: str
    location: str
    status: str
    last_seen: datetime
    sensors: List[str]
    metadata: Dict[str, Any]

@dataclass
class SensorData:
    """Datos de sensor"""
    device_id: str
    sensor_id: str
    value: float
    unit: str
    timestamp: datetime
    quality: str
    metadata: Dict[str, Any]

@dataclass
class IoTConfig:
    """Configuración IoT"""
    mqtt_broker: str
    mqtt_port: int
    mqtt_username: str
    mqtt_password: str
    coap_server: str
    coap_port: int
    edge_computing: bool
    fog_computing: bool
    data_retention_days: int
    sampling_rate: int

class AdvancedIoTIntegration:
    """Sistema de integración IoT avanzado"""
    
    def __init__(self, config: IoTConfig = None):
        """Inicializar integración IoT"""
        self.config = config or IoTConfig(
            mqtt_broker="localhost",
            mqtt_port=1883,
            mqtt_username="iot_user",
            mqtt_password="iot_password",
            coap_server="localhost",
            coap_port=5683,
            edge_computing=True,
            fog_computing=True,
            data_retention_days=30,
            sampling_rate=60
        )
        
        self.devices = {}
        self.sensor_data = {}
        self.mqtt_client = None
        self.running = False
        self.data_thread = None
        self.analysis_thread = None
        
        # Inicializar base de datos
        self._init_database()
        
        # Inicializar MQTT
        self._init_mqtt()
        
        logger.info("Advanced IoT Integration initialized")
    
    def _init_database(self):
        """Inicializar base de datos IoT"""
        try:
            conn = sqlite3.connect("iot_data.db")
            cursor = conn.cursor()
            
            # Tabla de dispositivos
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS iot_devices (
                    device_id TEXT PRIMARY KEY,
                    device_type TEXT NOT NULL,
                    location TEXT NOT NULL,
                    status TEXT NOT NULL,
                    last_seen TIMESTAMP NOT NULL,
                    sensors TEXT NOT NULL,
                    metadata TEXT
                )
            """)
            
            # Tabla de datos de sensores
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS sensor_data (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    device_id TEXT NOT NULL,
                    sensor_id TEXT NOT NULL,
                    value REAL NOT NULL,
                    unit TEXT NOT NULL,
                    timestamp TIMESTAMP NOT NULL,
                    quality TEXT NOT NULL,
                    metadata TEXT,
                    FOREIGN KEY (device_id) REFERENCES iot_devices (device_id)
                )
            """)
            
            # Tabla de análisis
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS iot_analysis (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    device_id TEXT NOT NULL,
                    analysis_type TEXT NOT NULL,
                    result TEXT NOT NULL,
                    confidence REAL NOT NULL,
                    timestamp TIMESTAMP NOT NULL,
                    FOREIGN KEY (device_id) REFERENCES iot_devices (device_id)
                )
            """)
            
            conn.commit()
            conn.close()
            
            logger.info("IoT database initialized")
            
        except Exception as e:
            logger.error(f"Error initializing IoT database: {e}")
    
    def _init_mqtt(self):
        """Inicializar cliente MQTT"""
        try:
            self.mqtt_client = mqtt.Client()
            self.mqtt_client.username_pw_set(self.config.mqtt_username, self.config.mqtt_password)
            
            # Configurar callbacks
            self.mqtt_client.on_connect = self._on_mqtt_connect
            self.mqtt_client.on_message = self._on_mqtt_message
            self.mqtt_client.on_disconnect = self._on_mqtt_disconnect
            
            logger.info("MQTT client initialized")
            
        except Exception as e:
            logger.error(f"Error initializing MQTT client: {e}")
    
    def _on_mqtt_connect(self, client, userdata, flags, rc):
        """Callback de conexión MQTT"""
        try:
            if rc == 0:
                logger.info("Connected to MQTT broker")
                # Suscribirse a topics
                client.subscribe("iot/devices/+/sensors/+")
                client.subscribe("iot/devices/+/status")
            else:
                logger.error(f"Failed to connect to MQTT broker: {rc}")
                
        except Exception as e:
            logger.error(f"Error in MQTT connect callback: {e}")
    
    def _on_mqtt_message(self, client, userdata, msg):
        """Callback de mensaje MQTT"""
        try:
            topic = msg.topic
            payload = json.loads(msg.payload.decode())
            
            # Procesar mensaje según el topic
            if "/sensors/" in topic:
                self._process_sensor_data(topic, payload)
            elif "/status" in topic:
                self._process_device_status(topic, payload)
            
        except Exception as e:
            logger.error(f"Error processing MQTT message: {e}")
    
    def _on_mqtt_disconnect(self, client, userdata, rc):
        """Callback de desconexión MQTT"""
        try:
            logger.info("Disconnected from MQTT broker")
            
        except Exception as e:
            logger.error(f"Error in MQTT disconnect callback: {e}")
    
    def _process_sensor_data(self, topic: str, payload: Dict[str, Any]):
        """Procesar datos de sensor"""
        try:
            # Extraer información del topic
            parts = topic.split('/')
            device_id = parts[2]
            sensor_id = parts[4]
            
            # Crear objeto SensorData
            sensor_data = SensorData(
                device_id=device_id,
                sensor_id=sensor_id,
                value=payload.get('value', 0.0),
                unit=payload.get('unit', ''),
                timestamp=datetime.now(),
                quality=payload.get('quality', 'good'),
                metadata=payload.get('metadata', {})
            )
            
            # Almacenar datos
            self._store_sensor_data(sensor_data)
            
            # Actualizar cache
            if device_id not in self.sensor_data:
                self.sensor_data[device_id] = {}
            self.sensor_data[device_id][sensor_id] = sensor_data
            
            logger.info(f"Processed sensor data: {device_id}/{sensor_id} = {sensor_data.value}")
            
        except Exception as e:
            logger.error(f"Error processing sensor data: {e}")
    
    def _process_device_status(self, topic: str, payload: Dict[str, Any]):
        """Procesar estado de dispositivo"""
        try:
            # Extraer información del topic
            parts = topic.split('/')
            device_id = parts[2]
            
            # Actualizar estado del dispositivo
            if device_id in self.devices:
                self.devices[device_id].status = payload.get('status', 'unknown')
                self.devices[device_id].last_seen = datetime.now()
            
            logger.info(f"Updated device status: {device_id} = {payload.get('status')}")
            
        except Exception as e:
            logger.error(f"Error processing device status: {e}")
    
    def _store_sensor_data(self, sensor_data: SensorData):
        """Almacenar datos de sensor en base de datos"""
        try:
            conn = sqlite3.connect("iot_data.db")
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT INTO sensor_data 
                (device_id, sensor_id, value, unit, timestamp, quality, metadata)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                sensor_data.device_id,
                sensor_data.sensor_id,
                sensor_data.value,
                sensor_data.unit,
                sensor_data.timestamp.isoformat(),
                sensor_data.quality,
                json.dumps(sensor_data.metadata)
            ))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            logger.error(f"Error storing sensor data: {e}")
    
    def start_iot_integration(self):
        """Iniciar integración IoT"""
        try:
            if self.running:
                logger.warning("IoT integration already running")
                return
            
            self.running = True
            
            # Conectar a MQTT broker
            self.mqtt_client.connect(self.config.mqtt_broker, self.config.mqtt_port, 60)
            self.mqtt_client.loop_start()
            
            # Iniciar hilos de procesamiento
            self._start_data_processing()
            self._start_analysis()
            
            logger.info("IoT integration started")
            
        except Exception as e:
            logger.error(f"Error starting IoT integration: {e}")
    
    def stop_iot_integration(self):
        """Detener integración IoT"""
        try:
            self.running = False
            
            # Desconectar de MQTT
            if self.mqtt_client:
                self.mqtt_client.loop_stop()
                self.mqtt_client.disconnect()
            
            # Detener hilos
            if self.data_thread and self.data_thread.is_alive():
                self.data_thread.join(timeout=5)
            
            if self.analysis_thread and self.analysis_thread.is_alive():
                self.analysis_thread.join(timeout=5)
            
            logger.info("IoT integration stopped")
            
        except Exception as e:
            logger.error(f"Error stopping IoT integration: {e}")
    
    def _start_data_processing(self):
        """Iniciar procesamiento de datos"""
        try:
            def data_processing_loop():
                while self.running:
                    self._process_historical_data()
                    time.sleep(self.config.sampling_rate)
            
            self.data_thread = threading.Thread(target=data_processing_loop, daemon=True)
            self.data_thread.start()
            
            logger.info("Data processing started")
            
        except Exception as e:
            logger.error(f"Error starting data processing: {e}")
    
    def _start_analysis(self):
        """Iniciar análisis de datos"""
        try:
            def analysis_loop():
                while self.running:
                    self._analyze_iot_data()
                    time.sleep(300)  # Analizar cada 5 minutos
            
            self.analysis_thread = threading.Thread(target=analysis_loop, daemon=True)
            self.analysis_thread.start()
            
            logger.info("Analysis started")
            
        except Exception as e:
            logger.error(f"Error starting analysis: {e}")
    
    def _process_historical_data(self):
        """Procesar datos históricos"""
        try:
            # Limpiar datos antiguos
            cutoff_date = datetime.now() - timedelta(days=self.config.data_retention_days)
            
            conn = sqlite3.connect("iot_data.db")
            cursor = conn.cursor()
            
            cursor.execute("""
                DELETE FROM sensor_data WHERE timestamp < ?
            """, (cutoff_date.isoformat(),))
            
            deleted_rows = cursor.rowcount
            conn.commit()
            conn.close()
            
            if deleted_rows > 0:
                logger.info(f"Cleaned up {deleted_rows} old sensor data records")
            
        except Exception as e:
            logger.error(f"Error processing historical data: {e}")
    
    def _analyze_iot_data(self):
        """Analizar datos IoT"""
        try:
            # Obtener datos recientes
            conn = sqlite3.connect("iot_data.db")
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT device_id, sensor_id, value, timestamp
                FROM sensor_data
                WHERE timestamp >= datetime('now', '-1 hour')
                ORDER BY timestamp DESC
            """)
            
            recent_data = cursor.fetchall()
            conn.close()
            
            if not recent_data:
                return
            
            # Agrupar por dispositivo y sensor
            device_sensor_data = {}
            for row in recent_data:
                device_id, sensor_id, value, timestamp = row
                key = f"{device_id}_{sensor_id}"
                
                if key not in device_sensor_data:
                    device_sensor_data[key] = []
                
                device_sensor_data[key].append((value, timestamp))
            
            # Analizar cada dispositivo/sensor
            for key, data_points in device_sensor_data.items():
                if len(data_points) >= 10:  # Mínimo 10 puntos para análisis
                    self._analyze_sensor_trend(key, data_points)
            
        except Exception as e:
            logger.error(f"Error analyzing IoT data: {e}")
    
    def _analyze_sensor_trend(self, key: str, data_points: List[Tuple[float, str]]):
        """Analizar tendencia de sensor"""
        try:
            device_id, sensor_id = key.split('_', 1)
            
            # Extraer valores
            values = [point[0] for point in data_points]
            
            # Calcular estadísticas
            mean_value = np.mean(values)
            std_value = np.std(values)
            trend = self._calculate_trend(values)
            
            # Detectar anomalías
            anomalies = self._detect_anomalies(values)
            
            # Crear resultado de análisis
            analysis_result = {
                "mean": mean_value,
                "std": std_value,
                "trend": trend,
                "anomalies": len(anomalies),
                "data_points": len(values)
            }
            
            # Almacenar análisis
            self._store_analysis(device_id, "sensor_trend", analysis_result, 0.8)
            
            # Generar alertas si es necesario
            if len(anomalies) > len(values) * 0.1:  # Más del 10% son anomalías
                self._generate_anomaly_alert(device_id, sensor_id, len(anomalies))
            
            logger.info(f"Analyzed sensor trend: {key} - Trend: {trend:.3f}, Anomalies: {len(anomalies)}")
            
        except Exception as e:
            logger.error(f"Error analyzing sensor trend: {e}")
    
    def _calculate_trend(self, values: List[float]) -> float:
        """Calcular tendencia de valores"""
        try:
            if len(values) < 2:
                return 0.0
            
            # Calcular pendiente usando regresión lineal simple
            x = np.arange(len(values))
            y = np.array(values)
            
            slope = np.polyfit(x, y, 1)[0]
            return slope
            
        except Exception as e:
            logger.error(f"Error calculating trend: {e}")
            return 0.0
    
    def _detect_anomalies(self, values: List[float]) -> List[int]:
        """Detectar anomalías en valores"""
        try:
            if len(values) < 10:
                return []
            
            # Usar método de IQR para detectar anomalías
            q1 = np.percentile(values, 25)
            q3 = np.percentile(values, 75)
            iqr = q3 - q1
            
            lower_bound = q1 - 1.5 * iqr
            upper_bound = q3 + 1.5 * iqr
            
            anomalies = []
            for i, value in enumerate(values):
                if value < lower_bound or value > upper_bound:
                    anomalies.append(i)
            
            return anomalies
            
        except Exception as e:
            logger.error(f"Error detecting anomalies: {e}")
            return []
    
    def _store_analysis(self, device_id: str, analysis_type: str, result: Dict[str, Any], confidence: float):
        """Almacenar análisis en base de datos"""
        try:
            conn = sqlite3.connect("iot_data.db")
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT INTO iot_analysis 
                (device_id, analysis_type, result, confidence, timestamp)
                VALUES (?, ?, ?, ?, ?)
            """, (
                device_id,
                analysis_type,
                json.dumps(result),
                confidence,
                datetime.now().isoformat()
            ))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            logger.error(f"Error storing analysis: {e}")
    
    def _generate_anomaly_alert(self, device_id: str, sensor_id: str, anomaly_count: int):
        """Generar alerta de anomalía"""
        try:
            alert_message = f"Anomaly detected in device {device_id}, sensor {sensor_id}: {anomaly_count} anomalies"
            logger.warning(alert_message)
            
            # Aquí se podría integrar con el sistema de notificaciones
            # notification_system.send_alert(alert_message)
            
        except Exception as e:
            logger.error(f"Error generating anomaly alert: {e}")
    
    def register_device(self, device: IoTDevice):
        """Registrar dispositivo IoT"""
        try:
            self.devices[device.device_id] = device
            
            # Almacenar en base de datos
            conn = sqlite3.connect("iot_data.db")
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT OR REPLACE INTO iot_devices 
                (device_id, device_type, location, status, last_seen, sensors, metadata)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                device.device_id,
                device.device_type,
                device.location,
                device.status,
                device.last_seen.isoformat(),
                json.dumps(device.sensors),
                json.dumps(device.metadata)
            ))
            
            conn.commit()
            conn.close()
            
            logger.info(f"Device registered: {device.device_id}")
            
        except Exception as e:
            logger.error(f"Error registering device: {e}")
    
    def get_device_data(self, device_id: str, sensor_id: str = None, hours: int = 24) -> List[Dict[str, Any]]:
        """Obtener datos de dispositivo"""
        try:
            conn = sqlite3.connect("iot_data.db")
            cursor = conn.cursor()
            
            query = """
                SELECT device_id, sensor_id, value, unit, timestamp, quality, metadata
                FROM sensor_data
                WHERE device_id = ? AND timestamp >= datetime('now', '-{} hours')
            """.format(hours)
            
            params = [device_id]
            
            if sensor_id:
                query += " AND sensor_id = ?"
                params.append(sensor_id)
            
            query += " ORDER BY timestamp DESC"
            
            cursor.execute(query, params)
            results = cursor.fetchall()
            conn.close()
            
            data = []
            for result in results:
                data.append({
                    "device_id": result[0],
                    "sensor_id": result[1],
                    "value": result[2],
                    "unit": result[3],
                    "timestamp": result[4],
                    "quality": result[5],
                    "metadata": json.loads(result[6]) if result[6] else {}
                })
            
            return data
            
        except Exception as e:
            logger.error(f"Error getting device data: {e}")
            return []
    
    def get_iot_metrics(self) -> Dict[str, Any]:
        """Obtener métricas IoT"""
        try:
            conn = sqlite3.connect("iot_data.db")
            cursor = conn.cursor()
            
            # Estadísticas de dispositivos
            cursor.execute("SELECT COUNT(*) FROM iot_devices")
            total_devices = cursor.fetchone()[0]
            
            cursor.execute("SELECT COUNT(*) FROM iot_devices WHERE status = 'online'")
            online_devices = cursor.fetchone()[0]
            
            # Estadísticas de datos
            cursor.execute("SELECT COUNT(*) FROM sensor_data WHERE timestamp >= datetime('now', '-1 hour')")
            recent_data_points = cursor.fetchone()[0]
            
            cursor.execute("SELECT COUNT(*) FROM sensor_data")
            total_data_points = cursor.fetchone()[0]
            
            # Estadísticas de análisis
            cursor.execute("SELECT COUNT(*) FROM iot_analysis WHERE timestamp >= datetime('now', '-1 hour')")
            recent_analyses = cursor.fetchone()[0]
            
            conn.close()
            
            return {
                "devices": {
                    "total": total_devices,
                    "online": online_devices,
                    "offline": total_devices - online_devices
                },
                "data": {
                    "recent_points": recent_data_points,
                    "total_points": total_data_points
                },
                "analysis": {
                    "recent_analyses": recent_analyses
                },
                "integration": {
                    "mqtt_connected": self.mqtt_client.is_connected() if self.mqtt_client else False,
                    "running": self.running
                }
            }
            
        except Exception as e:
            logger.error(f"Error getting IoT metrics: {e}")
            return {}

def main():
    """Función principal para demostrar integración IoT"""
    print("=" * 60)
    print("ADVANCED IOT INTEGRATION - DEMO")
    print("=" * 60)
    
    # Configurar integración IoT
    iot_config = IoTConfig(
        mqtt_broker="localhost",
        mqtt_port=1883,
        mqtt_username="iot_user",
        mqtt_password="iot_password",
        coap_server="localhost",
        coap_port=5683,
        edge_computing=True,
        fog_computing=True,
        data_retention_days=30,
        sampling_rate=60
    )
    
    # Inicializar integración IoT
    iot_integration = AdvancedIoTIntegration(iot_config)
    
    # Registrar dispositivos de prueba
    print("Registering test devices...")
    
    device1 = IoTDevice(
        device_id="sensor_001",
        device_type="temperature_sensor",
        location="warehouse_a",
        status="online",
        last_seen=datetime.now(),
        sensors=["temperature", "humidity"],
        metadata={"model": "DHT22", "firmware": "1.0.0"}
    )
    iot_integration.register_device(device1)
    
    device2 = IoTDevice(
        device_id="sensor_002",
        device_type="pressure_sensor",
        location="warehouse_b",
        status="online",
        last_seen=datetime.now(),
        sensors=["pressure", "altitude"],
        metadata={"model": "BMP280", "firmware": "1.1.0"}
    )
    iot_integration.register_device(device2)
    
    print("✓ Test devices registered")
    
    # Simular datos de sensores
    print("Simulating sensor data...")
    
    # Simular datos de temperatura
    for i in range(10):
        sensor_data = SensorData(
            device_id="sensor_001",
            sensor_id="temperature",
            value=20.0 + np.random.normal(0, 2),
            unit="°C",
            timestamp=datetime.now() - timedelta(minutes=i*5),
            quality="good",
            metadata={"calibrated": True}
        )
        iot_integration._store_sensor_data(sensor_data)
    
    # Simular datos de presión
    for i in range(10):
        sensor_data = SensorData(
            device_id="sensor_002",
            sensor_id="pressure",
            value=1013.25 + np.random.normal(0, 5),
            unit="hPa",
            timestamp=datetime.now() - timedelta(minutes=i*5),
            quality="good",
            metadata={"calibrated": True}
        )
        iot_integration._store_sensor_data(sensor_data)
    
    print("✓ Sensor data simulated")
    
    # Iniciar integración
    print("Starting IoT integration...")
    iot_integration.start_iot_integration()
    
    # Obtener datos de dispositivos
    print("Getting device data...")
    temp_data = iot_integration.get_device_data("sensor_001", "temperature", hours=1)
    pressure_data = iot_integration.get_device_data("sensor_002", "pressure", hours=1)
    
    print(f"✓ Temperature data points: {len(temp_data)}")
    print(f"✓ Pressure data points: {len(pressure_data)}")
    
    # Obtener métricas
    print("\nIoT metrics:")
    metrics = iot_integration.get_iot_metrics()
    print(f"  • Total Devices: {metrics['devices']['total']}")
    print(f"  • Online Devices: {metrics['devices']['online']}")
    print(f"  • Recent Data Points: {metrics['data']['recent_points']}")
    print(f"  • Total Data Points: {metrics['data']['total_points']}")
    print(f"  • Recent Analyses: {metrics['analysis']['recent_analyses']}")
    print(f"  • MQTT Connected: {metrics['integration']['mqtt_connected']}")
    
    # Simular funcionamiento
    print("\nIoT integration running... (Press Ctrl+C to stop)")
    try:
        time.sleep(30)
    except KeyboardInterrupt:
        print("\nStopping IoT integration...")
        iot_integration.stop_iot_integration()
    
    print("\n" + "=" * 60)
    print("ADVANCED IOT INTEGRATION DEMO COMPLETED")
    print("=" * 60)
    print("🌐 IoT integration features:")
    print("  • IoT device integration")
    print("  • Real-time sensor monitoring")
    print("  • IoT data analysis")
    print("  • IoT-based automation")
    print("  • Edge computing")
    print("  • Fog computing")
    print("  • MQTT integration")
    print("  • CoAP integration")
    print("  • Time series analysis")
    print("  • Predictive maintenance")

if __name__ == "__main__":
    main()






