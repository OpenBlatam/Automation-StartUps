#!/usr/bin/env python3
"""
System Integration Manager for Competitive Pricing Analysis
=========================================================

Gestor de integración del sistema que coordina todos los componentes:
- Orquestación de procesos
- Gestión de dependencias
- Monitoreo de sistema
- Recuperación de errores
- Optimización de rendimiento
- Gestión de configuración
- Logging centralizado
- Métricas de sistema
"""

import asyncio
import logging
import json
import yaml
import sqlite3
import threading
import time
import psutil
import schedule
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass, asdict
from pathlib import Path
import subprocess
import signal
import sys
import os
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor
import queue
import multiprocessing as mp

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('system_integration.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

@dataclass
class SystemConfig:
    """Configuración del sistema"""
    system_name: str
    version: str
    components: List[str]
    dependencies: List[str]
    monitoring_interval: int = 60
    max_retries: int = 3
    timeout: int = 300
    parallel_workers: int = 4
    log_level: str = "INFO"
    auto_recovery: bool = True
    performance_monitoring: bool = True

@dataclass
class ComponentStatus:
    """Estado de componente"""
    name: str
    status: str  # running, stopped, error, maintenance
    last_check: datetime
    uptime: float
    memory_usage: float
    cpu_usage: float
    error_count: int
    last_error: Optional[str] = None

@dataclass
class SystemMetrics:
    """Métricas del sistema"""
    timestamp: datetime
    total_memory: float
    used_memory: float
    cpu_percent: float
    disk_usage: float
    active_connections: int
    component_count: int
    healthy_components: int
    error_rate: float

class SystemIntegrationManager:
    """Gestor de integración del sistema"""
    
    def __init__(self, config_path: str = "system_config.yaml"):
        """Inicializar gestor de integración"""
        self.config_path = config_path
        self.config = self._load_config()
        self.components = {}
        self.component_status = {}
        self.system_metrics = []
        self.task_queue = queue.Queue()
        self.executor = ThreadPoolExecutor(max_workers=self.config.parallel_workers)
        self.running = False
        self.monitoring_thread = None
        self.recovery_thread = None
        
        # Crear directorios necesarios
        self._create_directories()
        
        logger.info(f"System Integration Manager initialized: {self.config.system_name} v{self.config.version}")
    
    def _load_config(self) -> SystemConfig:
        """Cargar configuración del sistema"""
        try:
            if os.path.exists(self.config_path):
                with open(self.config_path, 'r') as f:
                    config_data = yaml.safe_load(f)
                return SystemConfig(**config_data)
            else:
                # Configuración por defecto
                return SystemConfig(
                    system_name="Competitive Pricing Analysis System",
                    version="1.0.0",
                    components=[
                        "competitive_pricing_analyzer",
                        "pricing_api_server",
                        "streamlit_dashboard",
                        "ai_pricing_intelligence",
                        "automation_engine",
                        "advanced_analytics_engine",
                        "advanced_reporting_system"
                    ],
                    dependencies=[
                        "sqlite3",
                        "flask",
                        "streamlit",
                        "pandas",
                        "numpy",
                        "scikit-learn",
                        "plotly"
                    ]
                )
        except Exception as e:
            logger.error(f"Error loading config: {e}")
            raise
    
    def _create_directories(self):
        """Crear directorios necesarios"""
        directories = [
            "logs",
            "data",
            "models",
            "reports",
            "charts",
            "config",
            "backups"
        ]
        
        for directory in directories:
            Path(directory).mkdir(exist_ok=True)
    
    def register_component(self, name: str, component: Any, dependencies: List[str] = None):
        """Registrar componente del sistema"""
        try:
            self.components[name] = {
                'instance': component,
                'dependencies': dependencies or [],
                'status': 'stopped',
                'start_time': None,
                'error_count': 0,
                'last_error': None
            }
            
            self.component_status[name] = ComponentStatus(
                name=name,
                status='stopped',
                last_check=datetime.now(),
                uptime=0.0,
                memory_usage=0.0,
                cpu_usage=0.0,
                error_count=0
            )
            
            logger.info(f"Component registered: {name}")
            
        except Exception as e:
            logger.error(f"Error registering component {name}: {e}")
            raise
    
    def start_system(self):
        """Iniciar sistema completo"""
        try:
            logger.info("Starting system...")
            self.running = True
            
            # Iniciar componentes en orden de dependencias
            self._start_components_by_dependencies()
            
            # Iniciar monitoreo
            self._start_monitoring()
            
            # Iniciar recuperación automática
            if self.config.auto_recovery:
                self._start_auto_recovery()
            
            # Programar tareas
            self._schedule_tasks()
            
            logger.info("System started successfully")
            
        except Exception as e:
            logger.error(f"Error starting system: {e}")
            self.stop_system()
            raise
    
    def _start_components_by_dependencies(self):
        """Iniciar componentes en orden de dependencias"""
        started = set()
        to_start = list(self.components.keys())
        
        while to_start:
            progress = False
            
            for component_name in to_start[:]:
                component = self.components[component_name]
                dependencies = component['dependencies']
                
                # Verificar si todas las dependencias están iniciadas
                if all(dep in started for dep in dependencies):
                    try:
                        self._start_component(component_name)
                        started.add(component_name)
                        to_start.remove(component_name)
                        progress = True
                    except Exception as e:
                        logger.error(f"Error starting component {component_name}: {e}")
                        component['error_count'] += 1
                        component['last_error'] = str(e)
            
            if not progress:
                logger.error("Circular dependency detected or unable to start components")
                break
    
    def _start_component(self, name: str):
        """Iniciar componente individual"""
        try:
            component = self.components[name]
            
            # Verificar si el componente tiene método start
            if hasattr(component['instance'], 'start'):
                component['instance'].start()
            elif hasattr(component['instance'], 'run'):
                # Ejecutar en hilo separado
                thread = threading.Thread(target=component['instance'].run, daemon=True)
                thread.start()
                component['thread'] = thread
            
            component['status'] = 'running'
            component['start_time'] = datetime.now()
            
            self.component_status[name].status = 'running'
            self.component_status[name].last_check = datetime.now()
            
            logger.info(f"Component started: {name}")
            
        except Exception as e:
            logger.error(f"Error starting component {name}: {e}")
            raise
    
    def _start_monitoring(self):
        """Iniciar monitoreo del sistema"""
        def monitor_loop():
            while self.running:
                try:
                    self._collect_system_metrics()
                    self._check_component_health()
                    time.sleep(self.config.monitoring_interval)
                except Exception as e:
                    logger.error(f"Error in monitoring loop: {e}")
        
        self.monitoring_thread = threading.Thread(target=monitor_loop, daemon=True)
        self.monitoring_thread.start()
        
        logger.info("System monitoring started")
    
    def _collect_system_metrics(self):
        """Recopilar métricas del sistema"""
        try:
            # Métricas del sistema
            memory = psutil.virtual_memory()
            cpu_percent = psutil.cpu_percent(interval=1)
            disk = psutil.disk_usage('/')
            
            # Contar componentes saludables
            healthy_components = sum(1 for status in self.component_status.values() 
                                   if status.status == 'running')
            
            # Calcular tasa de error
            total_errors = sum(comp['error_count'] for comp in self.components.values())
            error_rate = total_errors / len(self.components) if self.components else 0
            
            metrics = SystemMetrics(
                timestamp=datetime.now(),
                total_memory=memory.total,
                used_memory=memory.used,
                cpu_percent=cpu_percent,
                disk_usage=disk.percent,
                active_connections=0,  # Implementar según necesidad
                component_count=len(self.components),
                healthy_components=healthy_components,
                error_rate=error_rate
            )
            
            self.system_metrics.append(metrics)
            
            # Mantener solo las últimas 1000 métricas
            if len(self.system_metrics) > 1000:
                self.system_metrics = self.system_metrics[-1000:]
            
        except Exception as e:
            logger.error(f"Error collecting system metrics: {e}")
    
    def _check_component_health(self):
        """Verificar salud de componentes"""
        for name, component in self.components.items():
            try:
                status = self.component_status[name]
                
                # Verificar si el componente está respondiendo
                if hasattr(component['instance'], 'health_check'):
                    is_healthy = component['instance'].health_check()
                else:
                    # Verificación básica
                    is_healthy = component['status'] == 'running'
                
                if is_healthy:
                    status.status = 'running'
                    status.error_count = 0
                    status.last_error = None
                else:
                    status.status = 'error'
                    status.error_count += 1
                
                # Actualizar métricas de rendimiento
                if hasattr(component['instance'], 'get_metrics'):
                    metrics = component['instance'].get_metrics()
                    status.memory_usage = metrics.get('memory_usage', 0)
                    status.cpu_usage = metrics.get('cpu_usage', 0)
                
                # Calcular uptime
                if component['start_time']:
                    status.uptime = (datetime.now() - component['start_time']).total_seconds()
                
                status.last_check = datetime.now()
                
            except Exception as e:
                logger.error(f"Error checking health of component {name}: {e}")
                self.component_status[name].status = 'error'
                self.component_status[name].last_error = str(e)
                self.component_status[name].error_count += 1
    
    def _start_auto_recovery(self):
        """Iniciar recuperación automática"""
        def recovery_loop():
            while self.running:
                try:
                    self._attempt_recovery()
                    time.sleep(30)  # Verificar cada 30 segundos
                except Exception as e:
                    logger.error(f"Error in recovery loop: {e}")
        
        self.recovery_thread = threading.Thread(target=recovery_loop, daemon=True)
        self.recovery_thread.start()
        
        logger.info("Auto-recovery started")
    
    def _attempt_recovery(self):
        """Intentar recuperación de componentes con error"""
        for name, component in self.components.items():
            status = self.component_status[name]
            
            if status.status == 'error' and status.error_count < self.config.max_retries:
                try:
                    logger.info(f"Attempting recovery for component: {name}")
                    self._restart_component(name)
                except Exception as e:
                    logger.error(f"Recovery failed for component {name}: {e}")
    
    def _restart_component(self, name: str):
        """Reiniciar componente"""
        try:
            # Detener componente
            self._stop_component(name)
            
            # Esperar un momento
            time.sleep(5)
            
            # Reiniciar componente
            self._start_component(name)
            
            logger.info(f"Component restarted: {name}")
            
        except Exception as e:
            logger.error(f"Error restarting component {name}: {e}")
            raise
    
    def _stop_component(self, name: str):
        """Detener componente"""
        try:
            component = self.components[name]
            
            if hasattr(component['instance'], 'stop'):
                component['instance'].stop()
            elif 'thread' in component:
                # El hilo se detendrá automáticamente al ser daemon
            
            component['status'] = 'stopped'
            component['start_time'] = None
            
            self.component_status[name].status = 'stopped'
            self.component_status[name].last_check = datetime.now()
            
            logger.info(f"Component stopped: {name}")
            
        except Exception as e:
            logger.error(f"Error stopping component {name}: {e}")
    
    def _schedule_tasks(self):
        """Programar tareas del sistema"""
        # Tarea de limpieza diaria
        schedule.every().day.at("02:00").do(self._cleanup_old_data)
        
        # Tarea de respaldo semanal
        schedule.every().sunday.at("03:00").do(self._backup_system)
        
        # Tarea de optimización mensual
        schedule.every().month.do(self._optimize_system)
        
        def run_scheduler():
            while self.running:
                schedule.run_pending()
                time.sleep(60)
        
        scheduler_thread = threading.Thread(target=run_scheduler, daemon=True)
        scheduler_thread.start()
        
        logger.info("System tasks scheduled")
    
    def _cleanup_old_data(self):
        """Limpiar datos antiguos"""
        try:
            logger.info("Running cleanup task...")
            
            # Limpiar métricas antiguas
            cutoff_date = datetime.now() - timedelta(days=30)
            self.system_metrics = [m for m in self.system_metrics if m.timestamp > cutoff_date]
            
            # Limpiar logs antiguos
            logs_dir = Path("logs")
            if logs_dir.exists():
                for log_file in logs_dir.glob("*.log"):
                    if log_file.stat().st_mtime < (datetime.now() - timedelta(days=7)).timestamp():
                        log_file.unlink()
            
            logger.info("Cleanup task completed")
            
        except Exception as e:
            logger.error(f"Error in cleanup task: {e}")
    
    def _backup_system(self):
        """Respaldar sistema"""
        try:
            logger.info("Running backup task...")
            
            backup_dir = Path("backups")
            backup_dir.mkdir(exist_ok=True)
            
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            backup_file = backup_dir / f"system_backup_{timestamp}.json"
            
            backup_data = {
                'config': asdict(self.config),
                'component_status': {name: asdict(status) for name, status in self.component_status.items()},
                'system_metrics': [asdict(metric) for metric in self.system_metrics[-100:]]  # Últimas 100 métricas
            }
            
            with open(backup_file, 'w') as f:
                json.dump(backup_data, f, indent=2, default=str)
            
            logger.info(f"Backup completed: {backup_file}")
            
        except Exception as e:
            logger.error(f"Error in backup task: {e}")
    
    def _optimize_system(self):
        """Optimizar sistema"""
        try:
            logger.info("Running optimization task...")
            
            # Optimizar base de datos
            conn = sqlite3.connect("pricing_analysis.db")
            conn.execute("VACUUM")
            conn.execute("ANALYZE")
            conn.close()
            
            # Limpiar archivos temporales
            temp_dirs = ["temp", "cache", "tmp"]
            for temp_dir in temp_dirs:
                temp_path = Path(temp_dir)
                if temp_path.exists():
                    for file in temp_path.glob("*"):
                        if file.is_file():
                            file.unlink()
            
            logger.info("Optimization task completed")
            
        except Exception as e:
            logger.error(f"Error in optimization task: {e}")
    
    def stop_system(self):
        """Detener sistema completo"""
        try:
            logger.info("Stopping system...")
            self.running = False
            
            # Detener todos los componentes
            for name in list(self.components.keys()):
                self._stop_component(name)
            
            # Esperar a que terminen los hilos
            if self.monitoring_thread and self.monitoring_thread.is_alive():
                self.monitoring_thread.join(timeout=5)
            
            if self.recovery_thread and self.recovery_thread.is_alive():
                self.recovery_thread.join(timeout=5)
            
            # Cerrar executor
            self.executor.shutdown(wait=True)
            
            logger.info("System stopped")
            
        except Exception as e:
            logger.error(f"Error stopping system: {e}")
    
    def get_system_status(self) -> Dict[str, Any]:
        """Obtener estado del sistema"""
        return {
            'system_name': self.config.system_name,
            'version': self.config.version,
            'status': 'running' if self.running else 'stopped',
            'components': {name: asdict(status) for name, status in self.component_status.items()},
            'system_metrics': asdict(self.system_metrics[-1]) if self.system_metrics else None,
            'uptime': (datetime.now() - self.component_status[list(self.component_status.keys())[0]].last_check).total_seconds() if self.component_status else 0
        }
    
    def execute_task(self, task_name: str, task_func: Callable, *args, **kwargs):
        """Ejecutar tarea en el sistema"""
        try:
            future = self.executor.submit(task_func, *args, **kwargs)
            return future
        except Exception as e:
            logger.error(f"Error executing task {task_name}: {e}")
            raise

def main():
    """Función principal para demostrar gestor de integración"""
    print("=" * 60)
    print("SYSTEM INTEGRATION MANAGER - DEMO")
    print("=" * 60)
    
    # Inicializar gestor de integración
    integration_manager = SystemIntegrationManager()
    
    # Registrar componentes de ejemplo
    class MockComponent:
        def __init__(self, name):
            self.name = name
            self.running = False
        
        def start(self):
            self.running = True
            print(f"Mock component {self.name} started")
        
        def stop(self):
            self.running = False
            print(f"Mock component {self.name} stopped")
        
        def health_check(self):
            return self.running
        
        def get_metrics(self):
            return {'memory_usage': 50.0, 'cpu_usage': 10.0}
    
    # Registrar componentes
    integration_manager.register_component("database", MockComponent("database"))
    integration_manager.register_component("api_server", MockComponent("api_server"), ["database"])
    integration_manager.register_component("dashboard", MockComponent("dashboard"), ["api_server"])
    integration_manager.register_component("analytics", MockComponent("analytics"), ["database"])
    
    # Iniciar sistema
    print("\nStarting system...")
    integration_manager.start_system()
    
    # Mostrar estado del sistema
    print("\nSystem Status:")
    status = integration_manager.get_system_status()
    print(f"System: {status['system_name']} v{status['version']}")
    print(f"Status: {status['status']}")
    print(f"Components: {len(status['components'])}")
    
    for name, component_status in status['components'].items():
        print(f"  • {name}: {component_status['status']}")
    
    # Simular funcionamiento
    print("\nSystem running... (Press Ctrl+C to stop)")
    try:
        while True:
            time.sleep(10)
            # Mostrar métricas cada 10 segundos
            if integration_manager.system_metrics:
                metrics = integration_manager.system_metrics[-1]
                print(f"CPU: {metrics.cpu_percent:.1f}% | Memory: {metrics.used_memory/1024**3:.1f}GB | Components: {metrics.healthy_components}/{metrics.component_count}")
    except KeyboardInterrupt:
        print("\nStopping system...")
        integration_manager.stop_system()
    
    print("\n" + "=" * 60)
    print("SYSTEM INTEGRATION MANAGER DEMO COMPLETED")
    print("=" * 60)

if __name__ == "__main__":
    main()






