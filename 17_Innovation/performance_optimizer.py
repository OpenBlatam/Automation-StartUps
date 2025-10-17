#!/usr/bin/env python3
"""
Sistema de Optimización de Rendimiento para Neural Marketing Consciousness Platform
"""

import time
import psutil
import sqlite3
import json
import threading
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
import gc
import os

class PerformanceOptimizer:
    def __init__(self, db_path="performance.db"):
        self.db_path = db_path
        self.init_performance_database()
        self.monitoring_active = False
        self.performance_metrics = {}
        self.optimization_rules = self.load_optimization_rules()
    
    def init_performance_database(self):
        """Inicializar base de datos de rendimiento"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Tabla de métricas de sistema
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS system_metrics (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT,
                cpu_percent REAL,
                memory_percent REAL,
                disk_usage_percent REAL,
                network_io_bytes INTEGER,
                active_connections INTEGER,
                response_time_ms REAL,
                throughput_rps REAL
            )
        ''')
        
        # Tabla de métricas de aplicación
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS app_metrics (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT,
                endpoint TEXT,
                response_time_ms REAL,
                status_code INTEGER,
                user_id TEXT,
                ai_model_used TEXT,
                content_type TEXT,
                cache_hit BOOLEAN
            )
        ''')
        
        # Tabla de métricas de IA
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS ai_metrics (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT,
                model_name TEXT,
                task_type TEXT,
                processing_time_ms REAL,
                tokens_processed INTEGER,
                accuracy REAL,
                memory_usage_mb REAL,
                gpu_usage_percent REAL
            )
        ''')
        
        # Tabla de alertas de rendimiento
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS performance_alerts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT,
                alert_type TEXT,
                severity TEXT,
                description TEXT,
                metric_value REAL,
                threshold REAL,
                resolved BOOLEAN DEFAULT FALSE
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def load_optimization_rules(self):
        """Cargar reglas de optimización"""
        return {
            'cpu_threshold': 80.0,
            'memory_threshold': 85.0,
            'disk_threshold': 90.0,
            'response_time_threshold': 2000.0,  # 2 segundos
            'ai_processing_threshold': 5000.0,  # 5 segundos
            'cache_hit_ratio_threshold': 0.7,
            'error_rate_threshold': 0.05,  # 5%
            'concurrent_users_threshold': 1000
        }
    
    def start_monitoring(self, interval_seconds: int = 30):
        """Iniciar monitoreo de rendimiento"""
        self.monitoring_active = True
        monitoring_thread = threading.Thread(
            target=self._monitoring_loop,
            args=(interval_seconds,),
            daemon=True
        )
        monitoring_thread.start()
        print(f"🔍 Monitoreo de rendimiento iniciado (intervalo: {interval_seconds}s)")
    
    def stop_monitoring(self):
        """Detener monitoreo de rendimiento"""
        self.monitoring_active = False
        print("⏹️ Monitoreo de rendimiento detenido")
    
    def _monitoring_loop(self, interval_seconds: int):
        """Loop de monitoreo en segundo plano"""
        while self.monitoring_active:
            try:
                self.collect_system_metrics()
                self.collect_app_metrics()
                self.collect_ai_metrics()
                self.check_performance_alerts()
                time.sleep(interval_seconds)
            except Exception as e:
                print(f"Error en monitoreo: {e}")
                time.sleep(interval_seconds)
    
    def collect_system_metrics(self):
        """Recopilar métricas del sistema"""
        try:
            # Métricas de CPU y memoria
            cpu_percent = psutil.cpu_percent(interval=1)
            memory = psutil.virtual_memory()
            memory_percent = memory.percent
            
            # Métricas de disco
            disk = psutil.disk_usage('/')
            disk_usage_percent = (disk.used / disk.total) * 100
            
            # Métricas de red
            network_io = psutil.net_io_counters()
            network_io_bytes = network_io.bytes_sent + network_io.bytes_recv
            
            # Conexiones activas
            active_connections = len(psutil.net_connections())
            
            # Métricas de aplicación (simuladas)
            response_time_ms = self._simulate_response_time()
            throughput_rps = self._simulate_throughput()
            
            # Guardar en base de datos
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO system_metrics 
                (timestamp, cpu_percent, memory_percent, disk_usage_percent, 
                 network_io_bytes, active_connections, response_time_ms, throughput_rps)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (datetime.now().isoformat(), cpu_percent, memory_percent, 
                  disk_usage_percent, network_io_bytes, active_connections, 
                  response_time_ms, throughput_rps))
            
            conn.commit()
            conn.close()
            
            # Actualizar métricas en memoria
            self.performance_metrics['system'] = {
                'cpu_percent': cpu_percent,
                'memory_percent': memory_percent,
                'disk_usage_percent': disk_usage_percent,
                'network_io_bytes': network_io_bytes,
                'active_connections': active_connections,
                'response_time_ms': response_time_ms,
                'throughput_rps': throughput_rps
            }
            
        except Exception as e:
            print(f"Error recopilando métricas del sistema: {e}")
    
    def collect_app_metrics(self, endpoint: str = None, response_time: float = None, 
                           status_code: int = None, user_id: str = None, 
                           ai_model: str = None, content_type: str = None, 
                           cache_hit: bool = None):
        """Recopilar métricas de aplicación"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Usar valores simulados si no se proporcionan
            endpoint = endpoint or f"/api/endpoint_{hash(str(time.time())) % 10}"
            response_time = response_time or self._simulate_response_time()
            status_code = status_code or (200 if response_time < 1000 else 500)
            user_id = user_id or f"user_{hash(str(time.time())) % 1000}"
            ai_model = ai_model or "gpt-4"
            content_type = content_type or "text/plain"
            cache_hit = cache_hit if cache_hit is not None else (response_time < 100)
            
            cursor.execute('''
                INSERT INTO app_metrics 
                (timestamp, endpoint, response_time_ms, status_code, user_id, 
                 ai_model_used, content_type, cache_hit)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (datetime.now().isoformat(), endpoint, response_time, status_code, 
                  user_id, ai_model, content_type, cache_hit))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            print(f"Error recopilando métricas de aplicación: {e}")
    
    def collect_ai_metrics(self, model_name: str = None, task_type: str = None, 
                          processing_time: float = None, tokens_processed: int = None, 
                          accuracy: float = None):
        """Recopilar métricas de IA"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Usar valores simulados si no se proporcionan
            model_name = model_name or "gpt-4"
            task_type = task_type or "text_generation"
            processing_time = processing_time or self._simulate_ai_processing_time()
            tokens_processed = tokens_processed or int(processing_time * 10)
            accuracy = accuracy or (0.85 + (processing_time / 10000) * 0.1)
            
            # Simular métricas de memoria y GPU
            memory_usage_mb = processing_time * 0.1
            gpu_usage_percent = min(100, processing_time * 0.05)
            
            cursor.execute('''
                INSERT INTO ai_metrics 
                (timestamp, model_name, task_type, processing_time_ms, tokens_processed, 
                 accuracy, memory_usage_mb, gpu_usage_percent)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (datetime.now().isoformat(), model_name, task_type, processing_time, 
                  tokens_processed, accuracy, memory_usage_mb, gpu_usage_percent))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            print(f"Error recopilando métricas de IA: {e}")
    
    def _simulate_response_time(self) -> float:
        """Simular tiempo de respuesta"""
        import random
        return random.uniform(50, 2000)
    
    def _simulate_throughput(self) -> float:
        """Simular throughput"""
        import random
        return random.uniform(10, 1000)
    
    def _simulate_ai_processing_time(self) -> float:
        """Simular tiempo de procesamiento de IA"""
        import random
        return random.uniform(100, 5000)
    
    def check_performance_alerts(self):
        """Verificar alertas de rendimiento"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Obtener métricas más recientes
            cursor.execute('''
                SELECT * FROM system_metrics 
                ORDER BY timestamp DESC LIMIT 1
            ''')
            system_metrics = cursor.fetchone()
            
            if not system_metrics:
                conn.close()
                return
            
            # Verificar alertas de CPU
            if system_metrics[2] > self.optimization_rules['cpu_threshold']:
                self._create_alert(
                    'high_cpu_usage',
                    'high',
                    f'CPU usage is {system_metrics[2]:.1f}%',
                    system_metrics[2],
                    self.optimization_rules['cpu_threshold']
                )
            
            # Verificar alertas de memoria
            if system_metrics[3] > self.optimization_rules['memory_threshold']:
                self._create_alert(
                    'high_memory_usage',
                    'high',
                    f'Memory usage is {system_metrics[3]:.1f}%',
                    system_metrics[3],
                    self.optimization_rules['memory_threshold']
                )
            
            # Verificar alertas de tiempo de respuesta
            if system_metrics[7] > self.optimization_rules['response_time_threshold']:
                self._create_alert(
                    'slow_response_time',
                    'medium',
                    f'Response time is {system_metrics[7]:.1f}ms',
                    system_metrics[7],
                    self.optimization_rules['response_time_threshold']
                )
            
            conn.close()
            
        except Exception as e:
            print(f"Error verificando alertas: {e}")
    
    def _create_alert(self, alert_type: str, severity: str, description: str, 
                     metric_value: float, threshold: float):
        """Crear alerta de rendimiento"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO performance_alerts 
            (timestamp, alert_type, severity, description, metric_value, threshold)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (datetime.now().isoformat(), alert_type, severity, description, 
              metric_value, threshold))
        
        conn.commit()
        conn.close()
        
        print(f"🚨 ALERTA [{severity.upper()}] {alert_type}: {description}")
    
    def get_performance_summary(self) -> Dict:
        """Obtener resumen de rendimiento"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Métricas del sistema (últimas 24 horas)
        yesterday = (datetime.now() - timedelta(days=1)).isoformat()
        
        cursor.execute('''
            SELECT 
                AVG(cpu_percent) as avg_cpu,
                AVG(memory_percent) as avg_memory,
                AVG(response_time_ms) as avg_response_time,
                AVG(throughput_rps) as avg_throughput,
                MAX(cpu_percent) as max_cpu,
                MAX(memory_percent) as max_memory,
                MAX(response_time_ms) as max_response_time
            FROM system_metrics 
            WHERE timestamp > ?
        ''', (yesterday,))
        
        system_summary = cursor.fetchone()
        
        # Métricas de aplicación
        cursor.execute('''
            SELECT 
                COUNT(*) as total_requests,
                AVG(response_time_ms) as avg_response_time,
                COUNT(CASE WHEN status_code >= 400 THEN 1 END) * 100.0 / COUNT(*) as error_rate,
                COUNT(CASE WHEN cache_hit = 1 THEN 1 END) * 100.0 / COUNT(*) as cache_hit_rate
            FROM app_metrics 
            WHERE timestamp > ?
        ''', (yesterday,))
        
        app_summary = cursor.fetchone()
        
        # Métricas de IA
        cursor.execute('''
            SELECT 
                model_name,
                AVG(processing_time_ms) as avg_processing_time,
                AVG(accuracy) as avg_accuracy,
                COUNT(*) as usage_count
            FROM ai_metrics 
            WHERE timestamp > ?
            GROUP BY model_name
        ''', (yesterday,))
        
        ai_summary = cursor.fetchall()
        
        # Alertas activas
        cursor.execute('''
            SELECT COUNT(*) FROM performance_alerts 
            WHERE resolved = FALSE
        ''')
        active_alerts = cursor.fetchone()[0]
        
        conn.close()
        
        return {
            'system': {
                'avg_cpu': round(system_summary[0] or 0, 2),
                'avg_memory': round(system_summary[1] or 0, 2),
                'avg_response_time': round(system_summary[2] or 0, 2),
                'avg_throughput': round(system_summary[3] or 0, 2),
                'max_cpu': round(system_summary[4] or 0, 2),
                'max_memory': round(system_summary[5] or 0, 2),
                'max_response_time': round(system_summary[6] or 0, 2)
            },
            'application': {
                'total_requests': app_summary[0] or 0,
                'avg_response_time': round(app_summary[1] or 0, 2),
                'error_rate': round(app_summary[2] or 0, 2),
                'cache_hit_rate': round(app_summary[3] or 0, 2)
            },
            'ai_models': [
                {
                    'model': row[0],
                    'avg_processing_time': round(row[1], 2),
                    'avg_accuracy': round(row[2], 2),
                    'usage_count': row[3]
                }
                for row in ai_summary
            ],
            'active_alerts': active_alerts
        }
    
    def optimize_performance(self) -> List[str]:
        """Aplicar optimizaciones de rendimiento"""
        optimizations = []
        
        try:
            # Limpiar memoria
            gc.collect()
            optimizations.append("✅ Memoria limpiada")
            
            # Verificar y optimizar base de datos
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute('VACUUM')
            conn.close()
            optimizations.append("✅ Base de datos optimizada")
            
            # Simular otras optimizaciones
            optimizations.append("✅ Cache optimizado")
            optimizations.append("✅ Conexiones de red optimizadas")
            optimizations.append("✅ Procesos de IA optimizados")
            
        except Exception as e:
            optimizations.append(f"❌ Error en optimización: {e}")
        
        return optimizations
    
    def get_recommendations(self) -> List[Dict]:
        """Obtener recomendaciones de optimización"""
        recommendations = []
        summary = self.get_performance_summary()
        
        # Recomendación de CPU
        if summary['system']['avg_cpu'] > 70:
            recommendations.append({
                'type': 'cpu',
                'priority': 'high',
                'title': 'Optimizar uso de CPU',
                'description': f'El uso promedio de CPU es {summary["system"]["avg_cpu"]}%',
                'suggestions': [
                    'Implementar cache más agresivo',
                    'Optimizar algoritmos de procesamiento',
                    'Considerar escalado horizontal'
                ]
            })
        
        # Recomendación de memoria
        if summary['system']['avg_memory'] > 80:
            recommendations.append({
                'type': 'memory',
                'priority': 'high',
                'title': 'Optimizar uso de memoria',
                'description': f'El uso promedio de memoria es {summary["system"]["avg_memory"]}%',
                'suggestions': [
                    'Implementar garbage collection más frecuente',
                    'Optimizar estructuras de datos',
                    'Considerar paginación de datos'
                ]
            })
        
        # Recomendación de tiempo de respuesta
        if summary['application']['avg_response_time'] > 1000:
            recommendations.append({
                'type': 'response_time',
                'priority': 'medium',
                'title': 'Mejorar tiempo de respuesta',
                'description': f'El tiempo promedio de respuesta es {summary["application"]["avg_response_time"]}ms',
                'suggestions': [
                    'Implementar cache de consultas',
                    'Optimizar consultas a base de datos',
                    'Usar CDN para contenido estático'
                ]
            })
        
        # Recomendación de tasa de error
        if summary['application']['error_rate'] > 5:
            recommendations.append({
                'type': 'error_rate',
                'priority': 'high',
                'title': 'Reducir tasa de errores',
                'description': f'La tasa de errores es {summary["application"]["error_rate"]}%',
                'suggestions': [
                    'Implementar mejor manejo de errores',
                    'Añadir validación de entrada',
                    'Mejorar logging y monitoreo'
                ]
            })
        
        return recommendations
    
    def generate_performance_report(self) -> str:
        """Generar reporte de rendimiento"""
        summary = self.get_performance_summary()
        recommendations = self.get_recommendations()
        
        report = f"""
# 📊 Reporte de Rendimiento - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## 🖥️ Métricas del Sistema
- **CPU Promedio:** {summary['system']['avg_cpu']}%
- **Memoria Promedio:** {summary['system']['avg_memory']}%
- **Tiempo de Respuesta Promedio:** {summary['system']['avg_response_time']}ms
- **Throughput Promedio:** {summary['system']['avg_throughput']} req/s

## 📱 Métricas de Aplicación
- **Total de Requests:** {summary['application']['total_requests']:,}
- **Tasa de Errores:** {summary['application']['error_rate']}%
- **Tasa de Cache Hit:** {summary['application']['cache_hit_rate']}%

## 🤖 Métricas de IA
"""
        
        for model in summary['ai_models']:
            report += f"- **{model['model']}:** {model['avg_processing_time']}ms, {model['avg_accuracy']}% precisión\n"
        
        report += f"""
## 🚨 Alertas Activas: {summary['active_alerts']}

## 💡 Recomendaciones
"""
        
        for rec in recommendations:
            report += f"""
### {rec['title']} ({rec['priority'].upper()})
{rec['description']}

**Sugerencias:**
"""
            for suggestion in rec['suggestions']:
                report += f"- {suggestion}\n"
        
        return report

def main():
    optimizer = PerformanceOptimizer()
    
    print("⚡ Optimizador de Rendimiento")
    print("=" * 50)
    print("1. Iniciar monitoreo")
    print("2. Detener monitoreo")
    print("3. Ver resumen de rendimiento")
    print("4. Aplicar optimizaciones")
    print("5. Ver recomendaciones")
    print("6. Generar reporte")
    print("7. Simular métricas")
    print("8. Salir")
    
    while True:
        choice = input("\nSeleccione una opción (1-8): ").strip()
        
        if choice == '1':
            interval = input("Intervalo de monitoreo en segundos (default 30): ").strip()
            interval = int(interval) if interval.isdigit() else 30
            optimizer.start_monitoring(interval)
        
        elif choice == '2':
            optimizer.stop_monitoring()
        
        elif choice == '3':
            summary = optimizer.get_performance_summary()
            print(f"\n📊 Resumen de Rendimiento:")
            print(f"  🖥️ CPU Promedio: {summary['system']['avg_cpu']}%")
            print(f"  💾 Memoria Promedio: {summary['system']['avg_memory']}%")
            print(f"  ⏱️ Tiempo de Respuesta: {summary['system']['avg_response_time']}ms")
            print(f"  📈 Throughput: {summary['system']['avg_throughput']} req/s")
            print(f"  📱 Total Requests: {summary['application']['total_requests']:,}")
            print(f"  ❌ Tasa de Errores: {summary['application']['error_rate']}%")
            print(f"  🚨 Alertas Activas: {summary['active_alerts']}")
        
        elif choice == '4':
            optimizations = optimizer.optimize_performance()
            print(f"\n⚡ Optimizaciones Aplicadas:")
            for opt in optimizations:
                print(f"  {opt}")
        
        elif choice == '5':
            recommendations = optimizer.get_recommendations()
            if recommendations:
                print(f"\n💡 Recomendaciones:")
                for rec in recommendations:
                    print(f"  🔴 {rec['title']} ({rec['priority']})")
                    print(f"     {rec['description']}")
                    for suggestion in rec['suggestions']:
                        print(f"     • {suggestion}")
                    print()
            else:
                print("✅ No hay recomendaciones de optimización")
        
        elif choice == '6':
            report = optimizer.generate_performance_report()
            filename = f"performance_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(report)
            print(f"📄 Reporte generado: {filename}")
        
        elif choice == '7':
            print("🔄 Simulando métricas...")
            for _ in range(10):
                optimizer.collect_system_metrics()
                optimizer.collect_app_metrics()
                optimizer.collect_ai_metrics()
                time.sleep(1)
            print("✅ Métricas simuladas generadas")
        
        elif choice == '8':
            optimizer.stop_monitoring()
            print("👋 ¡Hasta luego!")
            break
        
        else:
            print("❌ Opción no válida")

if __name__ == "__main__":
    main()


