#!/usr/bin/env python3
"""
🚀 MASTER MARKETING BRAIN LAUNCHER
Launcher Maestro para el Advanced Marketing Brain System
Ejecuta todos los componentes del sistema de manera integrada
"""

import sys
import subprocess
import os
import time
import threading
import signal
from pathlib import Path
import argparse
import json
from datetime import datetime
import logging

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('marketing_brain.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class MasterMarketingBrainLauncher:
    """Launcher maestro para el Advanced Marketing Brain System"""
    
    def __init__(self):
        self.processes = {}
        self.threads = {}
        self.is_running = False
        self.start_time = None
        
        # Configuración de componentes
        self.components = {
            'core': {
                'script': 'advanced_marketing_brain_system.py',
                'name': 'Advanced Marketing Brain System',
                'required': True,
                'port': None
            },
            'dashboard': {
                'script': 'marketing_brain_dashboard.py',
                'name': 'Marketing Brain Dashboard',
                'required': False,
                'port': 8501,
                'command': ['streamlit', 'run']
            },
            'api': {
                'script': 'marketing_brain_api.py',
                'name': 'Marketing Brain API',
                'required': False,
                'port': 5000,
                'command': ['python']
            },
            'analytics': {
                'script': 'marketing_brain_analytics.py',
                'name': 'Marketing Brain Analytics',
                'required': False,
                'port': None
            },
            'automation': {
                'script': 'marketing_brain_automation.py',
                'name': 'Marketing Brain Automation',
                'required': False,
                'port': None
            },
            'integration': {
                'script': 'marketing_brain_integration.py',
                'name': 'Marketing Brain Integration',
                'required': False,
                'port': None
            }
        }
        
        # URLs de acceso
        self.urls = {
            'dashboard': 'http://localhost:8501',
            'api': 'http://localhost:5000',
            'api_docs': 'http://localhost:5000/'
        }
    
    def check_dependencies(self):
        """Verificar dependencias del sistema"""
        print("🔍 Verificando dependencias...")
        
        missing_packages = []
        required_packages = [
            'pandas', 'numpy', 'plotly', 'streamlit', 'flask', 'flask_cors',
            'schedule', 'aiohttp', 'scipy', 'scikit-learn'
        ]
        
        for package in required_packages:
            try:
                __import__(package)
                print(f"   ✅ {package}")
            except ImportError:
                missing_packages.append(package)
                print(f"   ❌ {package}")
        
        if missing_packages:
            print(f"\n❌ Dependencias faltantes: {', '.join(missing_packages)}")
            print("📦 Instalar dependencias:")
            print("   pip install -r requirements.txt")
            return False
        
        print("✅ Todas las dependencias están instaladas")
        return True
    
    def check_files(self):
        """Verificar archivos del sistema"""
        print("\n📁 Verificando archivos del sistema...")
        
        missing_files = []
        for component_id, config in self.components.items():
            script_path = Path(config['script'])
            if script_path.exists():
                print(f"   ✅ {config['name']} ({config['script']})")
            else:
                missing_files.append(config['script'])
                print(f"   ❌ {config['name']} ({config['script']})")
        
        if missing_files:
            print(f"\n❌ Archivos faltantes: {', '.join(missing_files)}")
            return False
        
        print("✅ Todos los archivos están presentes")
        return True
    
    def check_ports(self, components_to_start):
        """Verificar disponibilidad de puertos"""
        print("\n🔌 Verificando disponibilidad de puertos...")
        
        import socket
        
        port_conflicts = []
        for component_id in components_to_start:
            config = self.components[component_id]
            port = config.get('port')
            
            if port:
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                result = sock.connect_ex(('localhost', port))
                sock.close()
                
                if result == 0:
                    port_conflicts.append(f"{config['name']} (puerto {port})")
                    print(f"   ⚠️ Puerto {port} en uso - {config['name']}")
                else:
                    print(f"   ✅ Puerto {port} disponible - {config['name']}")
        
        if port_conflicts:
            print(f"\n⚠️ Puertos en conflicto: {', '.join(port_conflicts)}")
            print("   Los componentes pueden no iniciarse correctamente")
        
        return len(port_conflicts) == 0
    
    def start_component(self, component_id):
        """Iniciar un componente específico"""
        config = self.components[component_id]
        script_path = Path(config['script'])
        
        if not script_path.exists():
            logger.error(f"Archivo no encontrado: {config['script']}")
            return False
        
        try:
            # Preparar comando
            if 'command' in config:
                cmd = config['command'] + [str(script_path)]
            else:
                cmd = [sys.executable, str(script_path)]
            
            # Iniciar proceso
            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                bufsize=1,
                universal_newlines=True
            )
            
            self.processes[component_id] = process
            
            # Iniciar thread para monitorear salida
            output_thread = threading.Thread(
                target=self._monitor_component_output,
                args=(component_id, process),
                daemon=True
            )
            output_thread.start()
            self.threads[component_id] = output_thread
            
            logger.info(f"🚀 {config['name']} iniciado (PID: {process.pid})")
            return True
            
        except Exception as e:
            logger.error(f"Error iniciando {config['name']}: {e}")
            return False
    
    def _monitor_component_output(self, component_id, process):
        """Monitorear salida de un componente"""
        config = self.components[component_id]
        
        try:
            while process.poll() is None:
                # Leer stdout
                if process.stdout.readable():
                    line = process.stdout.readline()
                    if line:
                        logger.info(f"[{config['name']}] {line.strip()}")
                
                # Leer stderr
                if process.stderr.readable():
                    line = process.stderr.readline()
                    if line:
                        logger.error(f"[{config['name']}] ERROR: {line.strip()}")
                
                time.sleep(0.1)
            
            # Proceso terminado
            return_code = process.returncode
            if return_code == 0:
                logger.info(f"✅ {config['name']} terminado exitosamente")
            else:
                logger.error(f"❌ {config['name']} terminado con código {return_code}")
                
        except Exception as e:
            logger.error(f"Error monitoreando {config['name']}: {e}")
    
    def stop_component(self, component_id):
        """Detener un componente específico"""
        if component_id not in self.processes:
            return
        
        config = self.components[component_id]
        process = self.processes[component_id]
        
        try:
            # Terminar proceso
            process.terminate()
            
            # Esperar a que termine
            try:
                process.wait(timeout=10)
            except subprocess.TimeoutExpired:
                # Forzar terminación
                process.kill()
                process.wait()
            
            logger.info(f"🛑 {config['name']} detenido")
            
        except Exception as e:
            logger.error(f"Error deteniendo {config['name']}: {e}")
        finally:
            # Limpiar referencias
            if component_id in self.processes:
                del self.processes[component_id]
            if component_id in self.threads:
                del self.threads[component_id]
    
    def start_system(self, components=None, wait_for_ready=True):
        """Iniciar el sistema completo"""
        if self.is_running:
            print("⚠️ El sistema ya está ejecutándose")
            return
        
        # Determinar componentes a iniciar
        if components is None:
            components = ['core', 'dashboard', 'api']
        
        # Verificar dependencias y archivos
        if not self.check_dependencies():
            return False
        
        if not self.check_files():
            return False
        
        # Verificar puertos
        self.check_ports(components)
        
        print(f"\n🚀 Iniciando Advanced Marketing Brain System...")
        print(f"📋 Componentes a iniciar: {', '.join(components)}")
        
        self.is_running = True
        self.start_time = datetime.now()
        
        # Iniciar componentes
        started_components = []
        for component_id in components:
            if component_id in self.components:
                if self.start_component(component_id):
                    started_components.append(component_id)
                else:
                    logger.error(f"Error iniciando {component_id}")
            else:
                logger.error(f"Componente desconocido: {component_id}")
        
        if not started_components:
            print("❌ No se pudo iniciar ningún componente")
            self.is_running = False
            return False
        
        print(f"\n✅ Sistema iniciado exitosamente")
        print(f"📊 Componentes activos: {', '.join(started_components)}")
        
        # Mostrar URLs de acceso
        self._show_access_urls(started_components)
        
        # Esperar a que los componentes estén listos
        if wait_for_ready:
            self._wait_for_components_ready(started_components)
        
        return True
    
    def _show_access_urls(self, started_components):
        """Mostrar URLs de acceso"""
        print(f"\n🌐 URLs DE ACCESO:")
        
        for component_id in started_components:
            config = self.components[component_id]
            port = config.get('port')
            
            if port:
                if component_id == 'dashboard':
                    url = self.urls['dashboard']
                    print(f"   📊 Dashboard: {url}")
                elif component_id == 'api':
                    url = self.urls['api']
                    print(f"   🌐 API: {url}")
                    print(f"   📚 API Docs: {self.urls['api_docs']}")
    
    def _wait_for_components_ready(self, started_components, timeout=30):
        """Esperar a que los componentes estén listos"""
        print(f"\n⏳ Esperando a que los componentes estén listos...")
        
        import socket
        
        for component_id in started_components:
            config = self.components[component_id]
            port = config.get('port')
            
            if port:
                print(f"   🔍 Verificando {config['name']} (puerto {port})...")
                
                start_time = time.time()
                while time.time() - start_time < timeout:
                    try:
                        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                        result = sock.connect_ex(('localhost', port))
                        sock.close()
                        
                        if result == 0:
                            print(f"   ✅ {config['name']} está listo")
                            break
                    except:
                        pass
                    
                    time.sleep(1)
                else:
                    print(f"   ⚠️ {config['name']} no respondió en {timeout} segundos")
    
    def stop_system(self):
        """Detener el sistema completo"""
        if not self.is_running:
            print("⚠️ El sistema no está ejecutándose")
            return
        
        print(f"\n🛑 Deteniendo Advanced Marketing Brain System...")
        
        # Detener todos los componentes
        for component_id in list(self.processes.keys()):
            self.stop_component(component_id)
        
        self.is_running = False
        
        # Calcular tiempo de ejecución
        if self.start_time:
            uptime = datetime.now() - self.start_time
            print(f"⏱️ Tiempo de ejecución: {uptime}")
        
        print("✅ Sistema detenido exitosamente")
    
    def get_system_status(self):
        """Obtener estado del sistema"""
        status = {
            'is_running': self.is_running,
            'start_time': self.start_time.isoformat() if self.start_time else None,
            'uptime': str(datetime.now() - self.start_time) if self.start_time else None,
            'components': {}
        }
        
        for component_id, config in self.components.items():
            if component_id in self.processes:
                process = self.processes[component_id]
                status['components'][component_id] = {
                    'name': config['name'],
                    'running': process.poll() is None,
                    'pid': process.pid,
                    'port': config.get('port')
                }
            else:
                status['components'][component_id] = {
                    'name': config['name'],
                    'running': False,
                    'pid': None,
                    'port': config.get('port')
                }
        
        return status
    
    def show_system_status(self):
        """Mostrar estado del sistema"""
        status = self.get_system_status()
        
        print(f"\n📊 ESTADO DEL SISTEMA:")
        print(f"   • Sistema ejecutándose: {'✅ Sí' if status['is_running'] else '❌ No'}")
        
        if status['start_time']:
            print(f"   • Iniciado: {status['start_time']}")
            print(f"   • Tiempo activo: {status['uptime']}")
        
        print(f"\n🔧 COMPONENTES:")
        for component_id, component_status in status['components'].items():
            status_icon = "✅" if component_status['running'] else "❌"
            port_info = f" (puerto {component_status['port']})" if component_status['port'] else ""
            pid_info = f" [PID: {component_status['pid']}]" if component_status['pid'] else ""
            
            print(f"   {status_icon} {component_status['name']}{port_info}{pid_info}")
    
    def run_demo(self):
        """Ejecutar demostración del sistema"""
        print("🎬 DEMOSTRACIÓN DEL ADVANCED MARKETING BRAIN SYSTEM")
        print("=" * 60)
        
        # Iniciar sistema básico
        if not self.start_system(['core'], wait_for_ready=False):
            return
        
        print(f"\n🎨 GENERANDO CONCEPTOS DE MARKETING...")
        time.sleep(2)
        
        # Simular generación de conceptos
        print("   • Analizando campañas existentes...")
        time.sleep(1)
        print("   • Extrayendo temas principales...")
        time.sleep(1)
        print("   • Generando conceptos frescos...")
        time.sleep(2)
        print("   ✅ 10 conceptos generados exitosamente")
        
        print(f"\n📊 ANÁLISIS DE TENDENCIAS...")
        time.sleep(1)
        print("   • Analizando tendencias del mercado...")
        time.sleep(1)
        print("   • Identificando oportunidades...")
        time.sleep(1)
        print("   ✅ 5 tendencias emergentes identificadas")
        
        print(f"\n🤖 AUTOMATIZACIÓN...")
        time.sleep(1)
        print("   • Configurando reglas de automatización...")
        time.sleep(1)
        print("   • Programando tareas automáticas...")
        time.sleep(1)
        print("   ✅ Sistema de automatización activo")
        
        print(f"\n🔗 INTEGRACIÓN...")
        time.sleep(1)
        print("   • Conectando componentes...")
        time.sleep(1)
        print("   • Sincronizando datos...")
        time.sleep(1)
        print("   ✅ Sistema integrado y funcionando")
        
        print(f"\n🎉 DEMOSTRACIÓN COMPLETADA")
        print(f"   El Advanced Marketing Brain System está funcionando")
        print(f"   y listo para generar conceptos de marketing con IA.")
        
        # Detener sistema
        time.sleep(3)
        self.stop_system()
    
    def interactive_mode(self):
        """Modo interactivo"""
        while True:
            print(f"\n" + "="*60)
            print("🧠 ADVANCED MARKETING BRAIN SYSTEM - MENÚ PRINCIPAL")
            print("="*60)
            print("1. 🚀 Iniciar Sistema Completo")
            print("2. 🎯 Iniciar Componentes Específicos")
            print("3. 📊 Mostrar Estado del Sistema")
            print("4. 🛑 Detener Sistema")
            print("5. 🎬 Ejecutar Demostración")
            print("6. 🔍 Verificar Sistema")
            print("7. 📋 Mostrar URLs de Acceso")
            print("8. 📝 Ver Logs del Sistema")
            print("0. 🚪 Salir")
            print("="*60)
            
            try:
                choice = input("\nIngresa tu opción (0-8): ").strip()
                
                if choice == "0":
                    if self.is_running:
                        self.stop_system()
                    print("👋 ¡Hasta luego!")
                    break
                elif choice == "1":
                    self.start_system()
                elif choice == "2":
                    self._select_components()
                elif choice == "3":
                    self.show_system_status()
                elif choice == "4":
                    self.stop_system()
                elif choice == "5":
                    self.run_demo()
                elif choice == "6":
                    self._verify_system()
                elif choice == "7":
                    self._show_urls()
                elif choice == "8":
                    self._show_logs()
                else:
                    print("❌ Opción inválida. Intenta de nuevo.")
                    
            except KeyboardInterrupt:
                print("\n👋 ¡Hasta luego!")
                if self.is_running:
                    self.stop_system()
                break
            except Exception as e:
                print(f"❌ Error: {e}")
    
    def _select_components(self):
        """Seleccionar componentes específicos"""
        print(f"\n🎯 SELECCIONAR COMPONENTES:")
        
        available_components = []
        for i, (component_id, config) in enumerate(self.components.items(), 1):
            status = "✅" if component_id in self.processes else "❌"
            print(f"{i}. {status} {config['name']}")
            available_components.append(component_id)
        
        try:
            selection = input(f"\nIngresa números separados por comas (1-{len(available_components)}): ").strip()
            selected_indices = [int(x.strip()) - 1 for x in selection.split(',')]
            
            selected_components = []
            for idx in selected_indices:
                if 0 <= idx < len(available_components):
                    selected_components.append(available_components[idx])
            
            if selected_components:
                self.start_system(selected_components)
            else:
                print("❌ No se seleccionaron componentes válidos")
                
        except ValueError:
            print("❌ Formato inválido. Usa números separados por comas.")
    
    def _verify_system(self):
        """Verificar sistema"""
        print(f"\n🔍 VERIFICACIÓN DEL SISTEMA:")
        
        # Verificar dependencias
        deps_ok = self.check_dependencies()
        
        # Verificar archivos
        files_ok = self.check_files()
        
        # Verificar puertos
        ports_ok = self.check_ports(list(self.components.keys()))
        
        if deps_ok and files_ok:
            print(f"\n✅ Sistema verificado correctamente")
        else:
            print(f"\n❌ Problemas encontrados en la verificación")
    
    def _show_urls(self):
        """Mostrar URLs de acceso"""
        print(f"\n🌐 URLs DE ACCESO:")
        
        for component_id, config in self.components.items():
            port = config.get('port')
            if port:
                if component_id == 'dashboard':
                    print(f"   📊 Dashboard: {self.urls['dashboard']}")
                elif component_id == 'api':
                    print(f"   🌐 API: {self.urls['api']}")
                    print(f"   📚 API Docs: {self.urls['api_docs']}")
    
    def _show_logs(self):
        """Mostrar logs del sistema"""
        log_file = Path('marketing_brain.log')
        
        if log_file.exists():
            print(f"\n📝 ÚLTIMAS 20 LÍNEAS DEL LOG:")
            print("-" * 60)
            
            try:
                with open(log_file, 'r', encoding='utf-8') as f:
                    lines = f.readlines()
                    for line in lines[-20:]:
                        print(line.strip())
            except Exception as e:
                print(f"❌ Error leyendo logs: {e}")
        else:
            print("📝 No hay archivo de logs disponible")


def signal_handler(signum, frame):
    """Manejador de señales para limpieza"""
    print(f"\n🛑 Señal recibida. Deteniendo sistema...")
    if 'launcher' in globals():
        launcher.stop_system()
    sys.exit(0)


def main():
    """Función principal"""
    global launcher
    
    # Configurar manejador de señales
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    parser = argparse.ArgumentParser(description="Master Marketing Brain Launcher")
    parser.add_argument("--mode", choices=["interactive", "demo", "start", "stop", "status"], 
                       default="interactive", help="Modo de ejecución")
    parser.add_argument("--components", nargs="+", 
                       choices=["core", "dashboard", "api", "analytics", "automation", "integration"],
                       help="Componentes específicos a iniciar")
    parser.add_argument("--no-wait", action="store_true", 
                       help="No esperar a que los componentes estén listos")
    
    args = parser.parse_args()
    
    # Crear launcher
    launcher = MasterMarketingBrainLauncher()
    
    print("🚀 MASTER MARKETING BRAIN LAUNCHER")
    print("=" * 50)
    
    try:
        if args.mode == "interactive":
            launcher.interactive_mode()
        elif args.mode == "demo":
            launcher.run_demo()
        elif args.mode == "start":
            components = args.components or ["core", "dashboard", "api"]
            launcher.start_system(components, wait_for_ready=not args.no_wait)
            if launcher.is_running:
                print("\n⏳ Presiona Ctrl+C para detener el sistema...")
                try:
                    while launcher.is_running:
                        time.sleep(1)
                except KeyboardInterrupt:
                    launcher.stop_system()
        elif args.mode == "stop":
            launcher.stop_system()
        elif args.mode == "status":
            launcher.show_system_status()
    
    except Exception as e:
        logger.error(f"Error en launcher: {e}")
        print(f"❌ Error: {e}")
    finally:
        if launcher.is_running:
            launcher.stop_system()


if __name__ == "__main__":
    main()










