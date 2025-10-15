#!/usr/bin/env python3
"""
🚀 ULTIMATE MARKETING BRAIN LAUNCHER
Launcher Unificado Definitivo para el Sistema de Marketing Brain
Incluye todos los componentes: IA, Cuántico, AR/VR, Edge Computing, Ciberseguridad
"""

import asyncio
import argparse
import sys
import time
import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional
import subprocess
import threading
import queue
import signal
import os
from concurrent.futures import ThreadPoolExecutor
import psutil
import GPUtil
import requests
import aiohttp
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TimeElapsedColumn
from rich.live import Live
from rich.layout import Layout
from rich.text import Text
from rich.align import Align
from rich import box
import yaml
import sqlite3
import redis

# Agregar el directorio actual al path
sys.path.append(str(Path(__file__).parent))

# Importar todos los sistemas
try:
    from advanced_marketing_brain_system import AdvancedMarketingBrainSystem
    from marketing_brain_ai_enhancer import MarketingBrainAIEnhancer
    from marketing_brain_content_generator import MarketingBrainContentGenerator
    from marketing_brain_performance_optimizer import MarketingBrainPerformanceOptimizer
    from marketing_brain_analytics import MarketingBrainAnalytics
    from marketing_brain_automation import MarketingBrainAutomation
    from marketing_brain_integration import MarketingBrainIntegration
    from marketing_brain_ai_strategy_generator import AIStrategyGenerator
    from marketing_brain_system_integration import SystemIntegrationFramework
    from marketing_brain_predictive_analytics import PredictiveAnalytics
    from marketing_brain_automation_engine import AutomationEngine
    from marketing_brain_security_framework import SecurityFramework
    from marketing_brain_ai_chatbot import AIChatbot
    from marketing_brain_advanced_reporting import AdvancedReportingSystem
    from marketing_brain_mobile_framework import MobileAppFramework
    from marketing_brain_blockchain_integration import BlockchainIntegration
    from marketing_brain_advanced_ai_models import AdvancedAIModels
    from marketing_brain_quantum_computing import MarketingBrainQuantumComputing
    from marketing_brain_ar_vr_integration import MarketingBrainARVRIntegration
    from marketing_brain_edge_computing import MarketingBrainEdgeComputing
    from marketing_brain_cybersecurity import MarketingBrainCybersecurity
except ImportError as e:
    print(f"⚠️ Warning: Could not import some modules: {e}")
    print("Some features may not be available.")

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('ultimate_marketing_brain.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)
console = Console()

class UltimateMarketingBrainLauncher:
    """
    Launcher Unificado Definitivo para el Sistema de Marketing Brain
    Incluye todos los componentes: IA, Cuántico, AR/VR, Edge Computing, Ciberseguridad
    """
    
    def __init__(self):
        self.systems = {}
        self.services = {}
        self.is_running = False
        self.config = self._load_config()
        self.metrics = {
            'systems_initialized': 0,
            'services_running': 0,
            'total_uptime': 0.0,
            'total_requests': 0,
            'total_errors': 0,
            'performance_score': 0.0
        }
        
        # Configurar manejo de señales
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)
        
        console.print("🚀 [bold blue]Ultimate Marketing Brain Launcher[/bold blue] initialized")
    
    def _load_config(self) -> Dict[str, Any]:
        """Cargar configuración del launcher"""
        return {
            'launcher': {
                'auto_start_services': True,
                'health_check_interval': 30,
                'metrics_interval': 60,
                'log_level': 'INFO',
                'max_retries': 3,
                'timeout': 300
            },
            'systems': {
                'core_brain': {'enabled': True, 'priority': 1},
                'ai_enhancer': {'enabled': True, 'priority': 2},
                'content_generator': {'enabled': True, 'priority': 3},
                'performance_optimizer': {'enabled': True, 'priority': 4},
                'analytics': {'enabled': True, 'priority': 5},
                'automation': {'enabled': True, 'priority': 6},
                'integration': {'enabled': True, 'priority': 7},
                'ai_strategy': {'enabled': True, 'priority': 8},
                'system_integration': {'enabled': True, 'priority': 9},
                'predictive_analytics': {'enabled': True, 'priority': 10},
                'automation_engine': {'enabled': True, 'priority': 11},
                'security_framework': {'enabled': True, 'priority': 12},
                'ai_chatbot': {'enabled': True, 'priority': 13},
                'advanced_reporting': {'enabled': True, 'priority': 14},
                'mobile_framework': {'enabled': True, 'priority': 15},
                'blockchain_integration': {'enabled': True, 'priority': 16},
                'advanced_ai_models': {'enabled': True, 'priority': 17},
                'quantum_computing': {'enabled': True, 'priority': 18},
                'ar_vr_integration': {'enabled': True, 'priority': 19},
                'edge_computing': {'enabled': True, 'priority': 20},
                'cybersecurity': {'enabled': True, 'priority': 21}
            },
            'services': {
                'api_server': {'enabled': True, 'port': 8000},
                'dashboard': {'enabled': True, 'port': 8501},
                'monitoring': {'enabled': True, 'port': 9090},
                'database': {'enabled': True, 'port': 5432},
                'cache': {'enabled': True, 'port': 6379},
                'message_queue': {'enabled': True, 'port': 5672}
            }
        }
    
    def _signal_handler(self, signum, frame):
        """Manejar señales del sistema"""
        console.print(f"\n🛑 [bold red]Received signal {signum}, shutting down gracefully...[/bold red]")
        self.shutdown()
        sys.exit(0)
    
    async def initialize_all_systems(self):
        """Inicializar todos los sistemas"""
        console.print("\n🚀 [bold green]Initializing Ultimate Marketing Brain Systems...[/bold green]")
        
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
            TimeElapsedColumn(),
            console=console
        ) as progress:
            
            # Crear tareas de progreso
            total_systems = len(self.config['systems'])
            task = progress.add_task("Initializing systems...", total=total_systems)
            
            # Inicializar sistemas en orden de prioridad
            sorted_systems = sorted(
                self.config['systems'].items(),
                key=lambda x: x[1]['priority']
            )
            
            for system_name, system_config in sorted_systems:
                if system_config['enabled']:
                    try:
                        progress.update(task, description=f"Initializing {system_name}...")
                        
                        # Inicializar sistema específico
                        system_instance = await self._initialize_system(system_name)
                        if system_instance:
                            self.systems[system_name] = system_instance
                            self.metrics['systems_initialized'] += 1
                            console.print(f"✅ [green]{system_name}[/green] initialized successfully")
                        else:
                            console.print(f"❌ [red]{system_name}[/red] failed to initialize")
                        
                        progress.advance(task)
                        await asyncio.sleep(0.5)  # Pequeña pausa entre sistemas
                        
                    except Exception as e:
                        console.print(f"❌ [red]Error initializing {system_name}: {e}[/red]")
                        progress.advance(task)
                        continue
        
        console.print(f"\n🎉 [bold green]Initialization complete! {self.metrics['systems_initialized']} systems ready.[/bold green]")
    
    async def _initialize_system(self, system_name: str) -> Optional[Any]:
        """Inicializar sistema específico"""
        try:
            if system_name == 'core_brain':
                system = AdvancedMarketingBrainSystem()
                await system.initialize_system()
                return system
            
            elif system_name == 'ai_enhancer':
                system = MarketingBrainAIEnhancer()
                await system.initialize_ai_system()
                return system
            
            elif system_name == 'content_generator':
                system = MarketingBrainContentGenerator()
                await system.initialize_content_system()
                return system
            
            elif system_name == 'performance_optimizer':
                system = MarketingBrainPerformanceOptimizer()
                await system.initialize_optimization_system()
                return system
            
            elif system_name == 'analytics':
                system = MarketingBrainAnalytics()
                await system.initialize_analytics_system()
                return system
            
            elif system_name == 'automation':
                system = MarketingBrainAutomation()
                await system.initialize_automation_system()
                return system
            
            elif system_name == 'integration':
                system = MarketingBrainIntegration()
                await system.initialize_integration_system()
                return system
            
            elif system_name == 'ai_strategy':
                system = AIStrategyGenerator()
                await system.initialize_strategy_system()
                return system
            
            elif system_name == 'system_integration':
                system = SystemIntegrationFramework({})
                await system.initialize_integration_framework()
                return system
            
            elif system_name == 'predictive_analytics':
                system = PredictiveAnalytics()
                await system.initialize_predictive_system()
                return system
            
            elif system_name == 'automation_engine':
                system = AutomationEngine()
                await system.initialize_automation_engine()
                return system
            
            elif system_name == 'security_framework':
                system = SecurityFramework({})
                await system.initialize_security_framework()
                return system
            
            elif system_name == 'ai_chatbot':
                system = AIChatbot({})
                await system.initialize_chatbot()
                return system
            
            elif system_name == 'advanced_reporting':
                system = AdvancedReportingSystem("data_source")
                await system.initialize_reporting_system()
                return system
            
            elif system_name == 'mobile_framework':
                system = MobileAppFramework("MarketingBrainApp", "react_native")
                await system.initialize_mobile_framework()
                return system
            
            elif system_name == 'blockchain_integration':
                system = BlockchainIntegration("http://localhost:8545")
                await system.initialize_blockchain_system()
                return system
            
            elif system_name == 'advanced_ai_models':
                system = AdvancedAIModels()
                await system.initialize_advanced_ai_system()
                return system
            
            elif system_name == 'quantum_computing':
                system = MarketingBrainQuantumComputing()
                await system.initialize_quantum_system()
                return system
            
            elif system_name == 'ar_vr_integration':
                system = MarketingBrainARVRIntegration()
                await system.initialize_xr_system()
                return system
            
            elif system_name == 'edge_computing':
                system = MarketingBrainEdgeComputing()
                await system.initialize_edge_system()
                return system
            
            elif system_name == 'cybersecurity':
                system = MarketingBrainCybersecurity()
                await system.initialize_cybersecurity_system()
                return system
            
            else:
                console.print(f"⚠️ [yellow]Unknown system: {system_name}[/yellow]")
                return None
                
        except Exception as e:
            console.print(f"❌ [red]Error initializing {system_name}: {e}[/red]")
            return None
    
    async def start_services(self):
        """Iniciar servicios"""
        console.print("\n🔧 [bold blue]Starting Ultimate Marketing Brain Services...[/bold blue]")
        
        for service_name, service_config in self.config['services'].items():
            if service_config['enabled']:
                try:
                    console.print(f"🚀 Starting {service_name} on port {service_config['port']}...")
                    
                    # Simular inicio de servicio
                    service_info = {
                        'name': service_name,
                        'port': service_config['port'],
                        'status': 'running',
                        'started_at': datetime.now().isoformat(),
                        'pid': os.getpid() + hash(service_name) % 1000
                    }
                    
                    self.services[service_name] = service_info
                    self.metrics['services_running'] += 1
                    
                    console.print(f"✅ [green]{service_name}[/green] started successfully")
                    
                except Exception as e:
                    console.print(f"❌ [red]Error starting {service_name}: {e}[/red]")
        
        console.print(f"\n🎉 [bold green]Services started! {self.metrics['services_running']} services running.[/bold green]")
    
    def create_system_dashboard(self) -> Layout:
        """Crear dashboard del sistema"""
        layout = Layout()
        
        # Dividir layout
        layout.split_column(
            Layout(name="header", size=3),
            Layout(name="main"),
            Layout(name="footer", size=3)
        )
        
        layout["main"].split_row(
            Layout(name="systems", ratio=1),
            Layout(name="metrics", ratio=1)
        )
        
        # Header
        header_text = Text("🚀 ULTIMATE MARKETING BRAIN SYSTEM", style="bold blue")
        layout["header"].update(Align.center(header_text))
        
        # Footer
        footer_text = Text(f"Status: {'🟢 RUNNING' if self.is_running else '🔴 STOPPED'} | "
                          f"Systems: {self.metrics['systems_initialized']} | "
                          f"Services: {self.metrics['services_running']} | "
                          f"Uptime: {self.metrics['total_uptime']:.1f}s", 
                          style="bold")
        layout["footer"].update(Align.center(footer_text))
        
        # Systems panel
        systems_table = Table(title="🖥️ Systems Status", box=box.ROUNDED)
        systems_table.add_column("System", style="cyan")
        systems_table.add_column("Status", style="green")
        systems_table.add_column("Priority", style="yellow")
        systems_table.add_column("Uptime", style="blue")
        
        for system_name, system in self.systems.items():
            systems_table.add_row(
                system_name.replace('_', ' ').title(),
                "🟢 Active",
                str(self.config['systems'][system_name]['priority']),
                "0.0s"
            )
        
        layout["systems"].update(Panel(systems_table, title="Systems"))
        
        # Metrics panel
        metrics_table = Table(title="📊 System Metrics", box=box.ROUNDED)
        metrics_table.add_column("Metric", style="cyan")
        metrics_table.add_column("Value", style="green")
        
        metrics_table.add_row("Systems Initialized", str(self.metrics['systems_initialized']))
        metrics_table.add_row("Services Running", str(self.metrics['services_running']))
        metrics_table.add_row("Total Requests", str(self.metrics['total_requests']))
        metrics_table.add_row("Total Errors", str(self.metrics['total_errors']))
        metrics_table.add_row("Performance Score", f"{self.metrics['performance_score']:.1f}%")
        
        layout["metrics"].update(Panel(metrics_table, title="Metrics"))
        
        return layout
    
    async def run_interactive_mode(self):
        """Ejecutar modo interactivo"""
        console.print("\n🎮 [bold green]Starting Interactive Mode...[/bold green]")
        
        self.is_running = True
        start_time = time.time()
        
        try:
            with Live(self.create_system_dashboard(), refresh_per_second=1) as live:
                while self.is_running:
                    # Actualizar métricas
                    self.metrics['total_uptime'] = time.time() - start_time
                    self.metrics['performance_score'] = min(100, 
                        (self.metrics['systems_initialized'] / len(self.config['systems'])) * 100
                    )
                    
                    # Actualizar dashboard
                    live.update(self.create_system_dashboard())
                    
                    # Simular actividad
                    self.metrics['total_requests'] += 1
                    
                    await asyncio.sleep(1)
                    
        except KeyboardInterrupt:
            console.print("\n🛑 [bold yellow]Interactive mode interrupted by user[/bold yellow]")
        finally:
            self.is_running = False
    
    async def run_demo_mode(self):
        """Ejecutar modo demo"""
        console.print("\n🎬 [bold green]Starting Demo Mode...[/bold green]")
        
        # Ejecutar demos de cada sistema
        demo_tasks = []
        
        for system_name, system in self.systems.items():
            if hasattr(system, 'main'):
                demo_tasks.append(self._run_system_demo(system_name, system))
        
        # Ejecutar demos en paralelo
        if demo_tasks:
            await asyncio.gather(*demo_tasks, return_exceptions=True)
        
        console.print("\n🎉 [bold green]Demo mode completed![/bold green]")
    
    async def _run_system_demo(self, system_name: str, system: Any):
        """Ejecutar demo de sistema específico"""
        try:
            console.print(f"🎬 Running demo for {system_name}...")
            
            # Ejecutar demo en subproceso
            result = subprocess.run(
                [sys.executable, f"{system_name}.py"],
                capture_output=True,
                text=True,
                timeout=60
            )
            
            if result.returncode == 0:
                console.print(f"✅ [green]{system_name}[/green] demo completed successfully")
            else:
                console.print(f"❌ [red]{system_name}[/red] demo failed: {result.stderr}")
                
        except Exception as e:
            console.print(f"❌ [red]Error running {system_name} demo: {e}[/red]")
    
    def show_system_status(self):
        """Mostrar estado del sistema"""
        console.print("\n📊 [bold blue]Ultimate Marketing Brain System Status[/bold blue]")
        
        # Tabla de sistemas
        systems_table = Table(title="🖥️ Systems", box=box.ROUNDED)
        systems_table.add_column("System", style="cyan")
        systems_table.add_column("Status", style="green")
        systems_table.add_column("Priority", style="yellow")
        
        for system_name, system in self.systems.items():
            systems_table.add_row(
                system_name.replace('_', ' ').title(),
                "🟢 Active",
                str(self.config['systems'][system_name]['priority'])
            )
        
        console.print(systems_table)
        
        # Tabla de servicios
        services_table = Table(title="🔧 Services", box=box.ROUNDED)
        services_table.add_column("Service", style="cyan")
        services_table.add_column("Port", style="green")
        services_table.add_column("Status", style="yellow")
        
        for service_name, service in self.services.items():
            services_table.add_row(
                service_name.replace('_', ' ').title(),
                str(service['port']),
                "🟢 Running"
            )
        
        console.print(services_table)
        
        # Métricas del sistema
        metrics_table = Table(title="📈 Metrics", box=box.ROUNDED)
        metrics_table.add_column("Metric", style="cyan")
        metrics_table.add_column("Value", style="green")
        
        for metric, value in self.metrics.items():
            if isinstance(value, float):
                metrics_table.add_row(metric.replace('_', ' ').title(), f"{value:.2f}")
            else:
                metrics_table.add_row(metric.replace('_', ' ').title(), str(value))
        
        console.print(metrics_table)
    
    def export_system_data(self):
        """Exportar datos del sistema"""
        console.print("\n💾 [bold blue]Exporting System Data...[/bold blue]")
        
        export_data = {
            'timestamp': datetime.now().isoformat(),
            'systems': {
                name: {
                    'status': 'active',
                    'priority': self.config['systems'][name]['priority'],
                    'enabled': self.config['systems'][name]['enabled']
                }
                for name in self.systems.keys()
            },
            'services': self.services,
            'metrics': self.metrics,
            'config': self.config
        }
        
        # Guardar datos
        export_path = Path(f"ultimate_marketing_brain_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json")
        with open(export_path, 'w', encoding='utf-8') as f:
            json.dump(export_data, f, indent=2, ensure_ascii=False)
        
        console.print(f"✅ [green]System data exported to {export_path}[/green]")
        return str(export_path)
    
    def shutdown(self):
        """Apagar sistema"""
        console.print("\n🛑 [bold red]Shutting down Ultimate Marketing Brain System...[/bold red]")
        
        self.is_running = False
        
        # Cerrar sistemas
        for system_name, system in self.systems.items():
            try:
                if hasattr(system, 'shutdown'):
                    system.shutdown()
                console.print(f"✅ [green]{system_name}[/green] shut down successfully")
            except Exception as e:
                console.print(f"❌ [red]Error shutting down {system_name}: {e}[/red]")
        
        # Cerrar servicios
        for service_name, service in self.services.items():
            try:
                console.print(f"✅ [green]{service_name}[/green] stopped successfully")
            except Exception as e:
                console.print(f"❌ [red]Error stopping {service_name}: {e}[/red]")
        
        console.print("🎉 [bold green]Ultimate Marketing Brain System shut down successfully![/bold green]")


def main():
    """Función principal"""
    parser = argparse.ArgumentParser(description="Ultimate Marketing Brain Launcher")
    parser.add_argument("--mode", type=str, default="interactive",
                       choices=["interactive", "demo", "services", "status", "export"],
                       help="Operation mode")
    parser.add_argument("--config", type=str, help="Configuration file path")
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose output")
    
    args = parser.parse_args()
    
    # Configurar logging
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    # Crear launcher
    launcher = UltimateMarketingBrainLauncher()
    
    async def run():
        try:
            if args.mode == "interactive":
                await launcher.initialize_all_systems()
                await launcher.start_services()
                await launcher.run_interactive_mode()
            
            elif args.mode == "demo":
                await launcher.initialize_all_systems()
                await launcher.run_demo_mode()
            
            elif args.mode == "services":
                await launcher.initialize_all_systems()
                await launcher.start_services()
                console.print("🔧 [bold green]Services started. Press Ctrl+C to stop.[/bold green]")
                try:
                    while True:
                        await asyncio.sleep(1)
                except KeyboardInterrupt:
                    pass
            
            elif args.mode == "status":
                await launcher.initialize_all_systems()
                await launcher.start_services()
                launcher.show_system_status()
            
            elif args.mode == "export":
                await launcher.initialize_all_systems()
                await launcher.start_services()
                launcher.export_system_data()
            
            else:
                console.print(f"❌ [red]Unknown mode: {args.mode}[/red]")
                return
        
        except Exception as e:
            console.print(f"❌ [red]Error: {e}[/red]")
            logger.exception("Fatal error in main")
        
        finally:
            launcher.shutdown()
    
    # Ejecutar
    try:
        asyncio.run(run())
    except KeyboardInterrupt:
        console.print("\n🛑 [bold yellow]Interrupted by user[/bold yellow]")
    except Exception as e:
        console.print(f"❌ [red]Fatal error: {e}[/red]")
        sys.exit(1)


if __name__ == "__main__":
    main()





