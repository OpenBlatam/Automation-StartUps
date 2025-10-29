#!/usr/bin/env python3
"""
Script de Inicio del Sistema de Gestión de Inventario Mejorado
=============================================================

Este script inicia todos los componentes del sistema mejorado:
- Sistema principal mejorado
- API REST
- Dashboard avanzado
- Dashboard original
"""

import subprocess
import time
import signal
import sys
import os
from datetime import datetime
import logging

# Configuración de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('system_startup.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class SystemManager:
    """Gestor del sistema completo"""
    
    def __init__(self):
        self.processes = {}
        self.running = True
        
    def start_component(self, name, script, port=None):
        """Iniciar un componente del sistema"""
        try:
            logger.info(f"Iniciando {name}...")
            
            if port:
                logger.info(f"  Puerto: {port}")
            
            # Iniciar proceso
            process = subprocess.Popen(
                [sys.executable, script],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            self.processes[name] = {
                'process': process,
                'script': script,
                'port': port,
                'start_time': datetime.now()
            }
            
            logger.info(f"✅ {name} iniciado correctamente (PID: {process.pid})")
            return True
            
        except Exception as e:
            logger.error(f"❌ Error iniciando {name}: {e}")
            return False
    
    def stop_component(self, name):
        """Detener un componente del sistema"""
        if name in self.processes:
            try:
                process_info = self.processes[name]
                process = process_info['process']
                
                logger.info(f"Deteniendo {name}...")
                
                # Terminar proceso
                process.terminate()
                
                # Esperar a que termine
                try:
                    process.wait(timeout=10)
                    logger.info(f"✅ {name} detenido correctamente")
                except subprocess.TimeoutExpired:
                    logger.warning(f"⚠️ {name} no respondió, forzando terminación...")
                    process.kill()
                    process.wait()
                    logger.info(f"✅ {name} terminado forzosamente")
                
                del self.processes[name]
                
            except Exception as e:
                logger.error(f"❌ Error deteniendo {name}: {e}")
    
    def stop_all(self):
        """Detener todos los componentes"""
        logger.info("Deteniendo todos los componentes...")
        
        for name in list(self.processes.keys()):
            self.stop_component(name)
        
        logger.info("✅ Todos los componentes detenidos")
    
    def check_status(self):
        """Verificar estado de todos los componentes"""
        logger.info("\n" + "="*60)
        logger.info("ESTADO DEL SISTEMA")
        logger.info("="*60)
        
        if not self.processes:
            logger.info("❌ No hay componentes ejecutándose")
            return
        
        for name, info in self.processes.items():
            process = info['process']
            port = info['port']
            start_time = info['start_time']
            
            # Verificar si el proceso sigue ejecutándose
            if process.poll() is None:
                status = "✅ Ejecutándose"
                uptime = datetime.now() - start_time
                uptime_str = f"{uptime.seconds // 3600:02d}:{(uptime.seconds % 3600) // 60:02d}:{uptime.seconds % 60:02d}"
            else:
                status = "❌ Detenido"
                uptime_str = "N/A"
            
            logger.info(f"{name:20} | {status:15} | Puerto: {port or 'N/A':8} | Uptime: {uptime_str}")
        
        logger.info("="*60)
    
    def monitor_system(self):
        """Monitorear el sistema"""
        logger.info("Iniciando monitoreo del sistema...")
        
        try:
            while self.running:
                time.sleep(30)  # Verificar cada 30 segundos
                
                # Verificar procesos
                for name, info in list(self.processes.items()):
                    process = info['process']
                    
                    if process.poll() is not None:
                        logger.warning(f"⚠️ {name} se detuvo inesperadamente")
                        
                        # Intentar reiniciar
                        logger.info(f"🔄 Reiniciando {name}...")
                        self.stop_component(name)
                        time.sleep(2)
                        self.start_component(
                            name, 
                            info['script'], 
                            info['port']
                        )
                
        except KeyboardInterrupt:
            logger.info("\n🛑 Interrupción recibida, deteniendo sistema...")
            self.running = False
        except Exception as e:
            logger.error(f"❌ Error en monitoreo: {e}")
        finally:
            self.stop_all()
    
    def signal_handler(self, signum, frame):
        """Manejar señales del sistema"""
        logger.info(f"\n🛑 Señal {signum} recibida, deteniendo sistema...")
        self.running = False
        self.stop_all()
        sys.exit(0)

def main():
    """Función principal"""
    logger.info("🚀 Iniciando Sistema de Gestión de Inventario Mejorado")
    logger.info("="*60)
    
    # Crear gestor del sistema
    manager = SystemManager()
    
    # Configurar manejo de señales
    signal.signal(signal.SIGINT, manager.signal_handler)
    signal.signal(signal.SIGTERM, manager.signal_handler)
    
    # Verificar que los archivos existen
    scripts = {
        'Sistema Principal': ('enhanced_system.py', None),
        'API REST': ('api_rest.py', 5001),
        'Dashboard Avanzado': ('advanced_dashboard.py', 5002),
        'Dashboard Original': ('dashboard.py', 5000)
    }
    
    missing_files = []
    for name, (script, port) in scripts.items():
        if not os.path.exists(script):
            missing_files.append(script)
    
    if missing_files:
        logger.error(f"❌ Archivos faltantes: {', '.join(missing_files)}")
        logger.error("Asegúrate de que todos los archivos estén en el directorio actual")
        return
    
    # Iniciar componentes
    logger.info("📦 Iniciando componentes...")
    
    components_started = 0
    for name, (script, port) in scripts.items():
        if manager.start_component(name, script, port):
            components_started += 1
            time.sleep(2)  # Esperar entre inicios
    
    logger.info(f"✅ {components_started}/{len(scripts)} componentes iniciados")
    
    if components_started == 0:
        logger.error("❌ No se pudo iniciar ningún componente")
        return
    
    # Mostrar estado inicial
    manager.check_status()
    
    # Mostrar URLs de acceso
    logger.info("\n🌐 URLs DE ACCESO:")
    logger.info("="*40)
    logger.info("Dashboard Original:    http://localhost:5000")
    logger.info("Dashboard Avanzado:    http://localhost:5002")
    logger.info("API REST:             http://localhost:5001")
    logger.info("Documentación API:    http://localhost:5001/api/docs")
    logger.info("="*40)
    
    logger.info("\n📊 MONITOREO ACTIVO")
    logger.info("Presiona Ctrl+C para detener el sistema")
    logger.info("-" * 40)
    
    # Iniciar monitoreo
    try:
        manager.monitor_system()
    except Exception as e:
        logger.error(f"❌ Error en el sistema: {e}")
    finally:
        logger.info("👋 Sistema detenido")

if __name__ == "__main__":
    main()



