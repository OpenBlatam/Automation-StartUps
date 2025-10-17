#!/usr/bin/env python3
"""
Sistema de Integración IoT para Conectividad Empresarial Avanzada
"""

import os
import json
import sqlite3
import threading
import time
from datetime import datetime
import random
import math

class IoTIntegrationSystem:
    def __init__(self, base_path="/Users/adan/frontier"):
        self.base_path = base_path
        self.iot_db = os.path.join(base_path, "iot_integration.db")
        self.iot_devices = {}
        self.device_sensors = {}
        self.analytics_engine = {}
        self.init_iot_database()
    
    def init_iot_database(self):
        """Inicializar base de datos IoT"""
        conn = sqlite3.connect(self.iot_db)
        cursor = conn.cursor()
        
        # Tabla de dispositivos IoT
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS iot_devices (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                device_id TEXT UNIQUE,
                device_name TEXT,
                device_type TEXT,
                location TEXT,
                status TEXT,
                last_seen TEXT,
                capabilities TEXT,
                created_at TEXT
            )
        ''')
        
        # Tabla de sensores
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS iot_sensors (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                device_id TEXT,
                sensor_name TEXT,
                sensor_type TEXT,
                unit TEXT,
                min_value REAL,
                max_value REAL,
                current_value REAL,
                last_reading TEXT,
                FOREIGN KEY (device_id) REFERENCES iot_devices (device_id)
            )
        ''')
        
        # Tabla de datos de sensores
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS sensor_data (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                device_id TEXT,
                sensor_name TEXT,
                value REAL,
                timestamp TEXT,
                quality_score REAL,
                FOREIGN KEY (device_id) REFERENCES iot_devices (device_id)
            )
        ''')
        
        # Tabla de alertas IoT
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS iot_alerts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                device_id TEXT,
                alert_type TEXT,
                severity TEXT,
                message TEXT,
                threshold_value REAL,
                actual_value REAL,
                created_at TEXT,
                resolved_at TEXT,
                FOREIGN KEY (device_id) REFERENCES iot_devices (device_id)
            )
        ''')
        
        # Tabla de automatizaciones IoT
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS iot_automations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                automation_name TEXT,
                trigger_condition TEXT,
                action_type TEXT,
                target_device TEXT,
                parameters TEXT,
                is_active BOOLEAN DEFAULT TRUE,
                created_at TEXT
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def register_iot_device(self, device_id, device_name, device_type, location, capabilities):
        """Registrar dispositivo IoT"""
        conn = sqlite3.connect(self.iot_db)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT OR REPLACE INTO iot_devices 
            (device_id, device_name, device_type, location, status, last_seen, 
             capabilities, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (device_id, device_name, device_type, location, 'online', 
              datetime.now().isoformat(), json.dumps(capabilities), datetime.now().isoformat()))
        
        conn.commit()
        conn.close()
        
        # Almacenar en memoria
        self.iot_devices[device_id] = {
            'name': device_name,
            'type': device_type,
            'location': location,
            'status': 'online',
            'capabilities': capabilities,
            'last_seen': datetime.now()
        }
        
        return device_id
    
    def add_sensor_to_device(self, device_id, sensor_name, sensor_type, unit, min_val=0, max_val=100):
        """Agregar sensor a dispositivo IoT"""
        conn = sqlite3.connect(self.iot_db)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO iot_sensors 
            (device_id, sensor_name, sensor_type, unit, min_value, max_value, 
             current_value, last_reading)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (device_id, sensor_name, sensor_type, unit, min_val, max_val, 
              random.uniform(min_val, max_val), datetime.now().isoformat()))
        
        sensor_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        # Almacenar en memoria
        if device_id not in self.device_sensors:
            self.device_sensors[device_id] = {}
        
        self.device_sensors[device_id][sensor_name] = {
            'type': sensor_type,
            'unit': unit,
            'min_value': min_val,
            'max_value': max_val,
            'current_value': random.uniform(min_val, max_val)
        }
        
        return sensor_id
    
    def collect_sensor_data(self, device_id, sensor_name, value, quality_score=1.0):
        """Recopilar datos de sensor"""
        conn = sqlite3.connect(self.iot_db)
        cursor = conn.cursor()
        
        # Insertar dato del sensor
        cursor.execute('''
            INSERT INTO sensor_data 
            (device_id, sensor_name, value, timestamp, quality_score)
            VALUES (?, ?, ?, ?, ?)
        ''', (device_id, sensor_name, value, datetime.now().isoformat(), quality_score))
        
        # Actualizar valor actual del sensor
        cursor.execute('''
            UPDATE iot_sensors 
            SET current_value = ?, last_reading = ?
            WHERE device_id = ? AND sensor_name = ?
        ''', (value, datetime.now().isoformat(), device_id, sensor_name))
        
        conn.commit()
        conn.close()
        
        # Actualizar en memoria
        if device_id in self.device_sensors and sensor_name in self.device_sensors[device_id]:
            self.device_sensors[device_id][sensor_name]['current_value'] = value
        
        # Verificar alertas
        self._check_sensor_alerts(device_id, sensor_name, value)
        
        return True
    
    def _check_sensor_alerts(self, device_id, sensor_name, value):
        """Verificar alertas de sensor"""
        if device_id not in self.device_sensors or sensor_name not in self.device_sensors[device_id]:
            return
        
        sensor_info = self.device_sensors[device_id][sensor_name]
        min_val = sensor_info['min_value']
        max_val = sensor_info['max_value']
        
        # Verificar umbrales
        if value < min_val * 0.9:  # 10% por debajo del mínimo
            self._create_iot_alert(device_id, 'low_value', 'warning', 
                                 f'Sensor {sensor_name} value below threshold', 
                                 min_val, value)
        elif value > max_val * 1.1:  # 10% por encima del máximo
            self._create_iot_alert(device_id, 'high_value', 'critical', 
                                 f'Sensor {sensor_name} value above threshold', 
                                 max_val, value)
    
    def _create_iot_alert(self, device_id, alert_type, severity, message, threshold, actual):
        """Crear alerta IoT"""
        conn = sqlite3.connect(self.iot_db)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO iot_alerts 
            (device_id, alert_type, severity, message, threshold_value, 
             actual_value, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (device_id, alert_type, severity, message, threshold, actual, 
              datetime.now().isoformat()))
        
        conn.commit()
        conn.close()
    
    def create_iot_automation(self, automation_name, trigger_condition, action_type, target_device, parameters):
        """Crear automatización IoT"""
        conn = sqlite3.connect(self.iot_db)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO iot_automations 
            (automation_name, trigger_condition, action_type, target_device, 
             parameters, created_at)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (automation_name, trigger_condition, action_type, target_device, 
              json.dumps(parameters), datetime.now().isoformat()))
        
        automation_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        return automation_id
    
    def execute_iot_automation(self, device_id, sensor_name, value):
        """Ejecutar automatizaciones IoT"""
        conn = sqlite3.connect(self.iot_db)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT * FROM iot_automations 
            WHERE is_active = TRUE AND trigger_condition LIKE ?
        ''', (f'%{sensor_name}%',))
        
        automations = cursor.fetchall()
        
        executed_actions = []
        
        for automation in automations:
            automation_id, name, trigger, action_type, target, params, is_active, created = automation
            
            # Verificar condición de disparo
            if self._evaluate_trigger_condition(trigger, sensor_name, value):
                # Ejecutar acción
                action_result = self._execute_iot_action(action_type, target, json.loads(params))
                executed_actions.append({
                    'automation_name': name,
                    'action_type': action_type,
                    'target_device': target,
                    'result': action_result
                })
        
        conn.close()
        return executed_actions
    
    def _evaluate_trigger_condition(self, condition, sensor_name, value):
        """Evaluar condición de disparo"""
        # Simular evaluación de condición
        if 'temperature' in condition.lower() and 'sensor_name' in condition:
            return value > 25  # Temperatura alta
        elif 'humidity' in condition.lower():
            return value > 80  # Humedad alta
        elif 'pressure' in condition.lower():
            return value < 1000  # Presión baja
        else:
            return random.random() > 0.7  # 30% de probabilidad
    
    def _execute_iot_action(self, action_type, target_device, parameters):
        """Ejecutar acción IoT"""
        actions = {
            'send_notification': self._send_iot_notification,
            'adjust_setting': self._adjust_device_setting,
            'activate_device': self._activate_device,
            'deactivate_device': self._deactivate_device,
            'log_event': self._log_iot_event
        }
        
        if action_type in actions:
            return actions[action_type](target_device, parameters)
        else:
            return {'status': 'unknown_action', 'message': 'Action type not supported'}
    
    def _send_iot_notification(self, target_device, params):
        """Enviar notificación IoT"""
        message = params.get('message', 'IoT automation triggered')
        return {'status': 'notification_sent', 'message': message}
    
    def _adjust_device_setting(self, target_device, params):
        """Ajustar configuración de dispositivo"""
        setting = params.get('setting', 'unknown')
        value = params.get('value', 0)
        return {'status': 'setting_adjusted', 'setting': setting, 'value': value}
    
    def _activate_device(self, target_device, params):
        """Activar dispositivo"""
        return {'status': 'device_activated', 'device': target_device}
    
    def _deactivate_device(self, target_device, params):
        """Desactivar dispositivo"""
        return {'status': 'device_deactivated', 'device': target_device}
    
    def _log_iot_event(self, target_device, params):
        """Registrar evento IoT"""
        event = params.get('event', 'automation_triggered')
        return {'status': 'event_logged', 'event': event}
    
    def analyze_iot_data(self, device_id, time_range_hours=24):
        """Analizar datos IoT"""
        conn = sqlite3.connect(self.iot_db)
        cursor = conn.cursor()
        
        # Obtener datos recientes
        since_time = datetime.now().timestamp() - (time_range_hours * 3600)
        
        cursor.execute('''
            SELECT sensor_name, value, timestamp, quality_score
            FROM sensor_data 
            WHERE device_id = ? AND timestamp > ?
            ORDER BY timestamp DESC
        ''', (device_id, datetime.fromtimestamp(since_time).isoformat()))
        
        data_points = cursor.fetchall()
        conn.close()
        
        if not data_points:
            return {'status': 'no_data', 'message': 'No data available for analysis'}
        
        # Agrupar por sensor
        sensor_data = {}
        for sensor_name, value, timestamp, quality in data_points:
            if sensor_name not in sensor_data:
                sensor_data[sensor_name] = []
            sensor_data[sensor_name].append({'value': value, 'timestamp': timestamp, 'quality': quality})
        
        # Análisis por sensor
        analysis_results = {}
        
        for sensor_name, data in sensor_data.items():
            values = [d['value'] for d in data]
            
            analysis = {
                'sensor_name': sensor_name,
                'data_points': len(values),
                'average': sum(values) / len(values),
                'min_value': min(values),
                'max_value': max(values),
                'trend': self._calculate_trend(values),
                'anomalies': self._detect_anomalies(values),
                'quality_score': sum(d['quality'] for d in data) / len(data)
            }
            
            analysis_results[sensor_name] = analysis
        
        return {
            'device_id': device_id,
            'time_range_hours': time_range_hours,
            'total_data_points': len(data_points),
            'sensor_analysis': analysis_results
        }
    
    def _calculate_trend(self, values):
        """Calcular tendencia de datos"""
        if len(values) < 2:
            return 'insufficient_data'
        
        # Calcular pendiente simple
        x = list(range(len(values)))
        n = len(values)
        sum_x = sum(x)
        sum_y = sum(values)
        sum_xy = sum(x[i] * values[i] for i in range(n))
        sum_x2 = sum(xi**2 for xi in x)
        
        slope = (n * sum_xy - sum_x * sum_y) / (n * sum_x2 - sum_x**2)
        
        if slope > 0.1:
            return 'increasing'
        elif slope < -0.1:
            return 'decreasing'
        else:
            return 'stable'
    
    def _detect_anomalies(self, values):
        """Detectar anomalías en datos"""
        if len(values) < 3:
            return []
        
        mean = sum(values) / len(values)
        variance = sum((x - mean)**2 for x in values) / len(values)
        std_dev = math.sqrt(variance)
        
        anomalies = []
        threshold = 2 * std_dev  # 2 desviaciones estándar
        
        for i, value in enumerate(values):
            if abs(value - mean) > threshold:
                anomalies.append({
                    'index': i,
                    'value': value,
                    'deviation': abs(value - mean),
                    'severity': 'high' if abs(value - mean) > 3 * std_dev else 'medium'
                })
        
        return anomalies
    
    def get_iot_dashboard_data(self):
        """Obtener datos para dashboard IoT"""
        conn = sqlite3.connect(self.iot_db)
        cursor = conn.cursor()
        
        # Estadísticas generales
        cursor.execute('SELECT COUNT(*) FROM iot_devices')
        total_devices = cursor.fetchone()[0]
        
        cursor.execute('SELECT COUNT(*) FROM iot_devices WHERE status = "online"')
        online_devices = cursor.fetchone()[0]
        
        cursor.execute('SELECT COUNT(*) FROM iot_sensors')
        total_sensors = cursor.fetchone()[0]
        
        cursor.execute('SELECT COUNT(*) FROM iot_alerts WHERE resolved_at IS NULL')
        active_alerts = cursor.fetchone()[0]
        
        cursor.execute('SELECT COUNT(*) FROM iot_automations WHERE is_active = TRUE')
        active_automations = cursor.fetchone()[0]
        
        # Dispositivos por tipo
        cursor.execute('''
            SELECT device_type, COUNT(*) FROM iot_devices
            GROUP BY device_type
        ''')
        devices_by_type = dict(cursor.fetchall())
        
        # Alertas por severidad
        cursor.execute('''
            SELECT severity, COUNT(*) FROM iot_alerts
            WHERE resolved_at IS NULL
            GROUP BY severity
        ''')
        alerts_by_severity = dict(cursor.fetchall())
        
        conn.close()
        
        return {
            'total_devices': total_devices,
            'online_devices': online_devices,
            'total_sensors': total_sensors,
            'active_alerts': active_alerts,
            'active_automations': active_automations,
            'devices_by_type': devices_by_type,
            'alerts_by_severity': alerts_by_severity
        }

def main():
    iot_system = IoTIntegrationSystem()
    
    print("🌐 Sistema de Integración IoT")
    print("=" * 50)
    print("1. Registrar dispositivo IoT")
    print("2. Agregar sensor a dispositivo")
    print("3. Recopilar datos de sensor")
    print("4. Crear automatización IoT")
    print("5. Analizar datos IoT")
    print("6. Ver dashboard IoT")
    print("7. Salir")
    
    while True:
        choice = input("\nSeleccione una opción (1-7): ").strip()
        
        if choice == '1':
            device_id = input("ID del dispositivo: ").strip()
            device_name = input("Nombre del dispositivo: ").strip()
            device_type = input("Tipo de dispositivo: ").strip()
            location = input("Ubicación: ").strip()
            capabilities = input("Capacidades (separadas por coma): ").strip().split(',')
            capabilities = [cap.strip() for cap in capabilities if cap.strip()]
            
            if device_id and device_name and device_type and location:
                registered_id = iot_system.register_iot_device(device_id, device_name, device_type, location, capabilities)
                print(f"✅ Dispositivo IoT registrado: {registered_id}")
                print(f"📍 Ubicación: {location}")
                print(f"🛠️ Capacidades: {', '.join(capabilities)}")
            else:
                print("❌ Datos del dispositivo requeridos")
        
        elif choice == '2':
            device_id = input("ID del dispositivo: ").strip()
            sensor_name = input("Nombre del sensor: ").strip()
            sensor_type = input("Tipo de sensor: ").strip()
            unit = input("Unidad de medida: ").strip()
            min_val = input("Valor mínimo (default 0): ").strip()
            max_val = input("Valor máximo (default 100): ").strip()
            
            min_val = float(min_val) if min_val.replace('.', '').isdigit() else 0
            max_val = float(max_val) if max_val.replace('.', '').isdigit() else 100
            
            if device_id and sensor_name and sensor_type and unit:
                sensor_id = iot_system.add_sensor_to_device(device_id, sensor_name, sensor_type, unit, min_val, max_val)
                print(f"✅ Sensor agregado con ID: {sensor_id}")
                print(f"📊 Rango: {min_val} - {max_val} {unit}")
            else:
                print("❌ Datos del sensor requeridos")
        
        elif choice == '3':
            device_id = input("ID del dispositivo: ").strip()
            sensor_name = input("Nombre del sensor: ").strip()
            value = input("Valor del sensor: ").strip()
            quality = input("Calidad (0-1, default 1): ").strip()
            
            try:
                value = float(value)
                quality = float(quality) if quality.replace('.', '').isdigit() else 1.0
                
                if iot_system.collect_sensor_data(device_id, sensor_name, value, quality):
                    print(f"✅ Datos recopilados: {sensor_name} = {value}")
                    print(f"📊 Calidad: {quality:.2f}")
                else:
                    print("❌ Error recopilando datos")
            except ValueError:
                print("❌ Valor numérico requerido")
        
        elif choice == '4':
            automation_name = input("Nombre de la automatización: ").strip()
            trigger_condition = input("Condición de disparo: ").strip()
            action_type = input("Tipo de acción: ").strip()
            target_device = input("Dispositivo objetivo: ").strip()
            parameters = input("Parámetros (JSON): ").strip()
            
            try:
                params = json.loads(parameters) if parameters else {}
                automation_id = iot_system.create_iot_automation(
                    automation_name, trigger_condition, action_type, target_device, params
                )
                print(f"✅ Automatización creada con ID: {automation_id}")
            except json.JSONDecodeError:
                print("❌ Parámetros JSON inválidos")
            except Exception as e:
                print(f"❌ Error: {e}")
        
        elif choice == '5':
            device_id = input("ID del dispositivo: ").strip()
            time_range = input("Rango de tiempo en horas (default 24): ").strip()
            time_range = int(time_range) if time_range.isdigit() else 24
            
            if device_id:
                print(f"🔍 Analizando datos de {device_id}...")
                analysis = iot_system.analyze_iot_data(device_id, time_range)
                
                if analysis.get('status') == 'no_data':
                    print("❌ No hay datos disponibles para análisis")
                else:
                    print(f"✅ Análisis completado:")
                    print(f"  📊 Puntos de datos: {analysis['total_data_points']}")
                    print(f"  📈 Sensores analizados: {len(analysis['sensor_analysis'])}")
                    
                    for sensor_name, sensor_analysis in analysis['sensor_analysis'].items():
                        print(f"    • {sensor_name}: {sensor_analysis['average']:.2f} (tendencia: {sensor_analysis['trend']})")
            else:
                print("❌ ID del dispositivo requerido")
        
        elif choice == '6':
            dashboard = iot_system.get_iot_dashboard_data()
            print(f"\n📊 Dashboard IoT:")
            print(f"  🌐 Dispositivos totales: {dashboard['total_devices']}")
            print(f"  ✅ Dispositivos online: {dashboard['online_devices']}")
            print(f"  📡 Sensores totales: {dashboard['total_sensors']}")
            print(f"  🚨 Alertas activas: {dashboard['active_alerts']}")
            print(f"  🔄 Automatizaciones activas: {dashboard['active_automations']}")
            
            if dashboard['devices_by_type']:
                print(f"\n📱 Dispositivos por tipo:")
                for device_type, count in dashboard['devices_by_type'].items():
                    print(f"  • {device_type}: {count}")
            
            if dashboard['alerts_by_severity']:
                print(f"\n🚨 Alertas por severidad:")
                for severity, count in dashboard['alerts_by_severity'].items():
                    print(f"  • {severity.upper()}: {count}")
        
        elif choice == '7':
            print("👋 ¡Hasta luego!")
            break
        
        else:
            print("❌ Opción no válida")

if __name__ == "__main__":
    main()


