#!/usr/bin/env python3
"""
Enhanced Startup Script for Competitive Pricing Analysis System
==============================================================

Script de inicio mejorado que incluye todas las funcionalidades avanzadas:
- Sistema de análisis de precios competitivos
- Mejoras avanzadas con IA
- Dashboard interactivo con Streamlit
- Motor de automatización
- Sistema de alertas inteligentes
- Integración con sistemas externos
"""

import argparse
import sys
import os
import yaml
import asyncio
import logging
import time
import threading
from datetime import datetime
from typing import Dict, List, Optional
import subprocess
import webbrowser
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('enhanced_pricing_system.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class EnhancedPricingSystem:
    """Sistema de precios competitivos mejorado"""
    
    def __init__(self, config_file: str = "enhanced_config.yaml"):
        """Inicializar sistema mejorado"""
        self.config = self._load_config(config_file)
        self.components = {}
        self.processes = {}
        self.status = {
            'core_system': False,
            'advanced_features': False,
            'ai_intelligence': False,
            'automation_engine': False,
            'streamlit_dashboard': False,
            'api_server': False
        }
        
        logger.info("Enhanced Pricing System initialized")
    
    def _load_config(self, config_file: str) -> Dict:
        """Cargar configuración"""
        try:
            with open(config_file, 'r') as f:
                return yaml.safe_load(f)
        except FileNotFoundError:
            logger.warning(f"Config file {config_file} not found, using defaults")
            return self._get_default_config()
    
    def _get_default_config(self) -> Dict:
        """Obtener configuración por defecto"""
        return {
            'system': {
                'name': 'Enhanced Competitive Pricing Analysis System',
                'version': '2.0.0',
                'database_path': 'pricing_analysis.db',
                'log_level': 'INFO'
            },
            'components': {
                'core_system': {
                    'enabled': True,
                    'port': 8080,
                    'auto_start': True
                },
                'advanced_features': {
                    'enabled': True,
                    'ml_models': True,
                    'sentiment_analysis': True,
                    'price_forecasting': True
                },
                'ai_intelligence': {
                    'enabled': True,
                    'deep_learning': True,
                    'pattern_analysis': True,
                    'anomaly_detection': True
                },
                'automation_engine': {
                    'enabled': True,
                    'workflows': True,
                    'triggers': True,
                    'scheduled_tasks': True
                },
                'streamlit_dashboard': {
                    'enabled': True,
                    'port': 8501,
                    'auto_open_browser': True
                },
                'api_server': {
                    'enabled': True,
                    'port': 8080,
                    'cors_enabled': True
                }
            },
            'features': {
                'real_time_monitoring': True,
                'price_optimization': True,
                'competitive_analysis': True,
                'market_sentiment': True,
                'ai_insights': True,
                'automated_alerts': True,
                'integration_tools': True,
                'export_capabilities': True
            },
            'integrations': {
                'crm_systems': ['salesforce', 'hubspot', 'pipedrive'],
                'bi_tools': ['tableau', 'power_bi', 'looker'],
                'communication': ['slack', 'teams', 'email'],
                'apis': ['rest', 'graphql', 'webhooks']
            }
        }
    
    def start_system(self, components: List[str] = None, sample_data: bool = False):
        """Iniciar sistema completo"""
        print("=" * 80)
        print("🏆 ENHANCED COMPETITIVE PRICING ANALYSIS SYSTEM")
        print("=" * 80)
        print(f"Version: {self.config['system']['version']}")
        print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 80)
        
        # Cargar datos de muestra si se solicita
        if sample_data:
            self._load_sample_data()
        
        # Iniciar componentes
        if components is None:
            components = ['core_system', 'advanced_features', 'ai_intelligence', 
                         'automation_engine', 'streamlit_dashboard', 'api_server']
        
        for component in components:
            if self.config['components'].get(component, {}).get('enabled', True):
                self._start_component(component)
            else:
                logger.info(f"Component {component} is disabled")
        
        # Mostrar estado del sistema
        self._show_system_status()
        
        # Mantener sistema ejecutándose
        self._keep_system_running()
    
    def _start_component(self, component: str):
        """Iniciar componente específico"""
        try:
            if component == 'core_system':
                self._start_core_system()
            elif component == 'advanced_features':
                self._start_advanced_features()
            elif component == 'ai_intelligence':
                self._start_ai_intelligence()
            elif component == 'automation_engine':
                self._start_automation_engine()
            elif component == 'streamlit_dashboard':
                self._start_streamlit_dashboard()
            elif component == 'api_server':
                self._start_api_server()
            
            self.status[component] = True
            logger.info(f"✓ {component} started successfully")
            
        except Exception as e:
            logger.error(f"✗ Failed to start {component}: {e}")
            self.status[component] = False
    
    def _start_core_system(self):
        """Iniciar sistema principal"""
        try:
            from competitive_pricing_analyzer import CompetitivePricingAnalyzer
            
            # Inicializar analizador principal
            self.components['core_analyzer'] = CompetitivePricingAnalyzer()
            
            # Ejecutar análisis inicial
            asyncio.run(self.components['core_analyzer'].collect_pricing_data())
            
            logger.info("Core pricing analysis system started")
            
        except Exception as e:
            logger.error(f"Error starting core system: {e}")
            raise
    
    def _start_advanced_features(self):
        """Iniciar características avanzadas"""
        try:
            from advanced_pricing_enhancements import AdvancedPricingEnhancements, RealTimePricingOptimizer
            
            # Inicializar mejoras avanzadas
            self.components['enhancements'] = AdvancedPricingEnhancements()
            self.components['optimizer'] = RealTimePricingOptimizer()
            
            # Iniciar optimización en tiempo real
            products = ['product_001', 'product_002', 'product_003']
            self.components['optimizer'].start_real_time_optimization(products)
            
            logger.info("Advanced pricing features started")
            
        except Exception as e:
            logger.error(f"Error starting advanced features: {e}")
            raise
    
    def _start_ai_intelligence(self):
        """Iniciar inteligencia artificial"""
        try:
            from ai_pricing_intelligence import AIPricingIntelligence
            
            # Inicializar sistema de IA
            self.components['ai_intelligence'] = AIPricingIntelligence()
            
            # Ejecutar análisis de IA inicial
            analysis = self.components['ai_intelligence'].run_comprehensive_analysis('product_001')
            
            logger.info("AI pricing intelligence started")
            
        except Exception as e:
            logger.error(f"Error starting AI intelligence: {e}")
            raise
    
    def _start_automation_engine(self):
        """Iniciar motor de automatización"""
        try:
            from automation_engine import AutomationEngine, create_default_workflows
            
            # Inicializar motor de automatización
            self.components['automation'] = AutomationEngine()
            
            # Crear flujos de trabajo por defecto
            default_workflows = create_default_workflows()
            for workflow in default_workflows:
                self.components['automation'].create_workflow(workflow)
            
            # Iniciar automatización
            self.components['automation'].start_automation()
            
            logger.info("Automation engine started")
            
        except Exception as e:
            logger.error(f"Error starting automation engine: {e}")
            raise
    
    def _start_streamlit_dashboard(self):
        """Iniciar dashboard de Streamlit"""
        try:
            port = self.config['components']['streamlit_dashboard'].get('port', 8501)
            
            # Iniciar Streamlit en proceso separado
            cmd = [
                sys.executable, '-m', 'streamlit', 'run', 
                'streamlit_dashboard.py', 
                '--server.port', str(port),
                '--server.headless', 'true'
            ]
            
            self.processes['streamlit'] = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
            
            # Esperar a que Streamlit se inicie
            time.sleep(5)
            
            # Abrir navegador si está habilitado
            if self.config['components']['streamlit_dashboard'].get('auto_open_browser', True):
                webbrowser.open(f'http://localhost:{port}')
            
            logger.info(f"Streamlit dashboard started on port {port}")
            
        except Exception as e:
            logger.error(f"Error starting Streamlit dashboard: {e}")
            raise
    
    def _start_api_server(self):
        """Iniciar servidor API"""
        try:
            port = self.config['components']['api_server'].get('port', 8080)
            
            # Iniciar servidor API en proceso separado
            cmd = [sys.executable, 'pricing_api_server.py']
            
            self.processes['api_server'] = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
            
            # Esperar a que el servidor se inicie
            time.sleep(3)
            
            logger.info(f"API server started on port {port}")
            
        except Exception as e:
            logger.error(f"Error starting API server: {e}")
            raise
    
    def _load_sample_data(self):
        """Cargar datos de muestra"""
        try:
            import pandas as pd
            from competitive_pricing_analyzer import PricingData, DataSource
            
            # Leer datos de muestra
            sample_file = 'sample_pricing_data.csv'
            if os.path.exists(sample_file):
                df = pd.read_csv(sample_file)
                
                # Convertir a objetos PricingData
                pricing_data = []
                for _, row in df.iterrows():
                    data = PricingData(
                        product_id=row['product_id'],
                        product_name=row['product_name'],
                        competitor=row['competitor'],
                        price=float(row['price']),
                        currency=row['currency'],
                        date_collected=datetime.now(),
                        source=DataSource.CSV_IMPORT,
                        additional_data={'sample_data': True}
                    )
                    pricing_data.append(data)
                
                # Almacenar datos
                if 'core_analyzer' in self.components:
                    self.components['core_analyzer']._store_pricing_data(pricing_data)
                
                logger.info(f"Loaded {len(pricing_data)} sample data points")
            else:
                logger.warning("Sample data file not found")
                
        except Exception as e:
            logger.error(f"Error loading sample data: {e}")
    
    def _show_system_status(self):
        """Mostrar estado del sistema"""
        print("\n" + "=" * 80)
        print("📊 SYSTEM STATUS")
        print("=" * 80)
        
        for component, status in self.status.items():
            status_icon = "✅" if status else "❌"
            component_name = component.replace('_', ' ').title()
            print(f"{status_icon} {component_name}: {'Running' if status else 'Stopped'}")
        
        print("\n🌐 ACCESS POINTS:")
        if self.status['streamlit_dashboard']:
            port = self.config['components']['streamlit_dashboard'].get('port', 8501)
            print(f"   📊 Interactive Dashboard: http://localhost:{port}")
        
        if self.status['api_server']:
            port = self.config['components']['api_server'].get('port', 8080)
            print(f"   🔌 API Server: http://localhost:{port}")
            print(f"   📋 API Documentation: http://localhost:{port}/api/docs")
        
        print("\n🚀 FEATURES ENABLED:")
        features = self.config.get('features', {})
        for feature, enabled in features.items():
            if enabled:
                feature_name = feature.replace('_', ' ').title()
                print(f"   ✨ {feature_name}")
        
        print("\n🔗 INTEGRATIONS AVAILABLE:")
        integrations = self.config.get('integrations', {})
        for integration_type, systems in integrations.items():
            if systems:
                type_name = integration_type.replace('_', ' ').title()
                print(f"   🔌 {type_name}: {', '.join(systems)}")
        
        print("=" * 80)
    
    def _keep_system_running(self):
        """Mantener sistema ejecutándose"""
        print("\n🎯 System is running! Press Ctrl+C to stop.")
        print("📊 Monitor the dashboard and API endpoints above.")
        print("🔄 The system will automatically collect data and generate insights.")
        
        try:
            while True:
                time.sleep(60)
                
                # Verificar estado de procesos
                self._check_process_health()
                
        except KeyboardInterrupt:
            print("\n🛑 Shutting down system...")
            self._shutdown_system()
    
    def _check_process_health(self):
        """Verificar salud de procesos"""
        for process_name, process in self.processes.items():
            if process.poll() is not None:
                logger.warning(f"Process {process_name} has stopped")
                # Reiniciar proceso si es necesario
                if process_name == 'streamlit':
                    self._start_streamlit_dashboard()
                elif process_name == 'api_server':
                    self._start_api_server()
    
    def _shutdown_system(self):
        """Apagar sistema"""
        print("🔄 Stopping all components...")
        
        # Detener procesos
        for process_name, process in self.processes.items():
            try:
                process.terminate()
                process.wait(timeout=10)
                print(f"✓ Stopped {process_name}")
            except subprocess.TimeoutExpired:
                process.kill()
                print(f"⚠️ Force stopped {process_name}")
            except Exception as e:
                print(f"✗ Error stopping {process_name}: {e}")
        
        # Limpiar componentes
        self.components.clear()
        self.processes.clear()
        
        print("✅ System shutdown completed")
    
    def run_demo(self):
        """Ejecutar demostración del sistema"""
        print("=" * 80)
        print("🎬 ENHANCED PRICING SYSTEM DEMO")
        print("=" * 80)
        
        # Iniciar sistema con datos de muestra
        self.start_system(sample_data=True)
    
    def run_analysis_only(self):
        """Ejecutar solo análisis"""
        print("=" * 80)
        print("🔍 RUNNING PRICING ANALYSIS")
        print("=" * 80)
        
        try:
            # Iniciar solo componentes de análisis
            self._start_core_system()
            self._start_advanced_features()
            self._start_ai_intelligence()
            
            # Ejecutar análisis completo
            print("\n📊 Running comprehensive analysis...")
            
            if 'core_analyzer' in self.components:
                # Recopilar datos
                asyncio.run(self.components['core_analyzer'].collect_pricing_data())
                
                # Analizar diferencias de precios
                insights = self.components['core_analyzer'].analyze_pricing_differences()
                
                # Generar reporte
                report = self.components['core_analyzer'].generate_pricing_report()
                
                print(f"✅ Analysis completed!")
                print(f"📈 Generated {len(insights)} insights")
                print(f"📊 Report generated with {len(report.get('insights', []))} recommendations")
            
            if 'enhancements' in self.components:
                # Ejecutar optimización de estrategia
                strategy = self.components['enhancements'].optimize_pricing_strategy('product_001')
                if strategy:
                    print(f"🎯 Optimal strategy: {strategy['recommended_strategy']['pricing_action']}")
                    print(f"💰 Price adjustment: {strategy['recommended_strategy']['price_adjustment']:.1%}")
            
            if 'ai_intelligence' in self.components:
                # Ejecutar análisis de IA
                ai_analysis = self.components['ai_intelligence'].run_comprehensive_analysis('product_001')
                if 'error' not in ai_analysis:
                    print(f"🤖 AI Analysis: {ai_analysis['summary']}")
            
        except Exception as e:
            logger.error(f"Error in analysis: {e}")
            print(f"❌ Analysis failed: {e}")

def create_enhanced_config():
    """Crear archivo de configuración mejorado"""
    config = {
        'system': {
            'name': 'Enhanced Competitive Pricing Analysis System',
            'version': '2.0.0',
            'database_path': 'pricing_analysis.db',
            'log_level': 'INFO'
        },
        'components': {
            'core_system': {
                'enabled': True,
                'port': 8080,
                'auto_start': True
            },
            'advanced_features': {
                'enabled': True,
                'ml_models': True,
                'sentiment_analysis': True,
                'price_forecasting': True,
                'elasticity_analysis': True
            },
            'ai_intelligence': {
                'enabled': True,
                'deep_learning': True,
                'pattern_analysis': True,
                'anomaly_detection': True,
                'competitor_behavior': True
            },
            'automation_engine': {
                'enabled': True,
                'workflows': True,
                'triggers': True,
                'scheduled_tasks': True,
                'max_concurrent_executions': 10
            },
            'streamlit_dashboard': {
                'enabled': True,
                'port': 8501,
                'auto_open_browser': True,
                'theme': 'light'
            },
            'api_server': {
                'enabled': True,
                'port': 8080,
                'cors_enabled': True,
                'rate_limiting': True
            }
        },
        'features': {
            'real_time_monitoring': True,
            'price_optimization': True,
            'competitive_analysis': True,
            'market_sentiment': True,
            'ai_insights': True,
            'automated_alerts': True,
            'integration_tools': True,
            'export_capabilities': True,
            'price_forecasting': True,
            'elasticity_analysis': True,
            'pattern_detection': True,
            'anomaly_detection': True
        },
        'integrations': {
            'crm_systems': ['salesforce', 'hubspot', 'pipedrive'],
            'bi_tools': ['tableau', 'power_bi', 'looker'],
            'communication': ['slack', 'teams', 'email', 'sms'],
            'apis': ['rest', 'graphql', 'webhooks'],
            'databases': ['postgresql', 'mysql', 'mongodb']
        },
        'alerts': {
            'enabled': True,
            'channels': ['email', 'slack', 'teams', 'webhook'],
            'thresholds': {
                'price_change': 0.1,
                'price_gap': 0.3,
                'market_opportunity': 0.2
            }
        },
        'monitoring': {
            'enabled': True,
            'health_checks': True,
            'performance_metrics': True,
            'error_tracking': True
        }
    }
    
    with open('enhanced_config.yaml', 'w') as f:
        yaml.dump(config, f, default_flow_style=False, indent=2)
    
    print("✅ Enhanced configuration file created: enhanced_config.yaml")

def main():
    """Función principal"""
    parser = argparse.ArgumentParser(
        description='Enhanced Competitive Pricing Analysis System',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python enhanced_startup.py                    # Start full system
  python enhanced_startup.py --demo             # Run demo with sample data
  python enhanced_startup.py --analysis-only    # Run analysis only
  python enhanced_startup.py --create-config    # Create configuration file
  python enhanced_startup.py --components core,ai # Start specific components
        """
    )
    
    parser.add_argument(
        '--demo',
        action='store_true',
        help='Run system demo with sample data'
    )
    
    parser.add_argument(
        '--analysis-only',
        action='store_true',
        help='Run analysis only without starting servers'
    )
    
    parser.add_argument(
        '--create-config',
        action='store_true',
        help='Create enhanced configuration file'
    )
    
    parser.add_argument(
        '--components',
        type=str,
        help='Comma-separated list of components to start'
    )
    
    parser.add_argument(
        '--config',
        default='enhanced_config.yaml',
        help='Configuration file path'
    )
    
    args = parser.parse_args()
    
    # Crear configuración si se solicita
    if args.create_config:
        create_enhanced_config()
        return
    
    # Inicializar sistema
    system = EnhancedPricingSystem(args.config)
    
    # Ejecutar según argumentos
    if args.demo:
        system.run_demo()
    elif args.analysis_only:
        system.run_analysis_only()
    else:
        # Determinar componentes a iniciar
        components = None
        if args.components:
            components = [c.strip() for c in args.components.split(',')]
        
        # Iniciar sistema
        system.start_system(components=components, sample_data=True)

if __name__ == '__main__':
    main()






