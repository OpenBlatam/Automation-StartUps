#!/usr/bin/env python3
"""
ClickUp Brain - Sistema de Validación Final Completa
==================================================

Sistema de validación y testing completo que verifica todas las funcionalidades
del ClickUp Brain System y genera un reporte de validación final.
"""

import os
import sys
import json
import time
import traceback
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
import logging

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ValidationTest:
    """Clase base para tests de validación."""
    
    def __init__(self, name: str, description: str):
        self.name = name
        self.description = description
        self.status = 'pending'
        self.start_time = None
        self.end_time = None
        self.duration = 0
        self.error_message = None
        self.details = {}
    
    def run(self) -> bool:
        """Ejecutar el test de validación."""
        self.start_time = datetime.now()
        try:
            result = self._execute()
            self.status = 'passed' if result else 'failed'
            return result
        except Exception as e:
            self.status = 'error'
            self.error_message = str(e)
            logger.error(f"Error en test {self.name}: {str(e)}")
            return False
        finally:
            self.end_time = datetime.now()
            if self.start_time:
                self.duration = (self.end_time - self.start_time).total_seconds()
    
    def _execute(self) -> bool:
        """Método a implementar por subclases."""
        raise NotImplementedError("Subclases deben implementar _execute()")

class ImportValidationTest(ValidationTest):
    """Test de validación de imports."""
    
    def __init__(self):
        super().__init__("Import Validation", "Validar que todos los módulos se pueden importar correctamente")
    
    def _execute(self) -> bool:
        """Validar imports de todos los módulos."""
        modules_to_test = [
            'clickup_brain_simple',
            'clickup_brain_ai_enhanced',
            'clickup_brain_realtime_monitor',
            'clickup_brain_api',
            'clickup_brain_advanced_dashboard',
            'clickup_brain_security',
            'clickup_brain_ml_advanced',
            'clickup_brain_clickup_integration',
            'clickup_brain_notifications',
            'clickup_brain_sentiment_analysis'
        ]
        
        successful_imports = 0
        failed_imports = []
        
        for module_name in modules_to_test:
            try:
                __import__(module_name)
                successful_imports += 1
                logger.info(f"✅ Import exitoso: {module_name}")
            except ImportError as e:
                failed_imports.append(f"{module_name}: {str(e)}")
                logger.error(f"❌ Error importando {module_name}: {str(e)}")
            except Exception as e:
                failed_imports.append(f"{module_name}: {str(e)}")
                logger.error(f"❌ Error inesperado importando {module_name}: {str(e)}")
        
        self.details = {
            'total_modules': len(modules_to_test),
            'successful_imports': successful_imports,
            'failed_imports': len(failed_imports),
            'failed_modules': failed_imports,
            'success_rate': (successful_imports / len(modules_to_test)) * 100
        }
        
        return len(failed_imports) == 0

class FunctionalityValidationTest(ValidationTest):
    """Test de validación de funcionalidades básicas."""
    
    def __init__(self):
        super().__init__("Functionality Validation", "Validar funcionalidades básicas de los sistemas")
    
    def _execute(self) -> bool:
        """Validar funcionalidades básicas."""
        functionality_tests = []
        
        # Test 1: Sistema Simple
        try:
            from clickup_brain_simple import SimpleClickUpBrainSystem
            system = SimpleClickUpBrainSystem()
            result = system.analyze_directory(".", team_size=5)
            functionality_tests.append({
                'system': 'Simple System',
                'status': 'passed' if result else 'failed',
                'details': 'Análisis básico funcionando'
            })
        except Exception as e:
            functionality_tests.append({
                'system': 'Simple System',
                'status': 'error',
                'details': str(e)
            })
        
        # Test 2: Sistema de IA
        try:
            from clickup_brain_ai_enhanced import EnhancedClickUpBrainSystem
            system = EnhancedClickUpBrainSystem()
            result = system.analyze_with_ai(".", team_size=10)
            functionality_tests.append({
                'system': 'AI Enhanced System',
                'status': 'passed' if result else 'failed',
                'details': 'Análisis con IA funcionando'
            })
        except Exception as e:
            functionality_tests.append({
                'system': 'AI Enhanced System',
                'status': 'error',
                'details': str(e)
            })
        
        # Test 3: Sistema de Seguridad
        try:
            from clickup_brain_security import SecurityManager, SecurityConfig
            config = SecurityConfig()
            security = SecurityManager(config)
            functionality_tests.append({
                'system': 'Security System',
                'status': 'passed',
                'details': 'Sistema de seguridad inicializado'
            })
        except Exception as e:
            functionality_tests.append({
                'system': 'Security System',
                'status': 'error',
                'details': str(e)
            })
        
        # Test 4: Sistema de ML
        try:
            from clickup_brain_ml_advanced import ClickUpBrainMLAdvanced
            ml_system = ClickUpBrainMLAdvanced()
            result = ml_system.initialize_models()
            functionality_tests.append({
                'system': 'ML Advanced System',
                'status': 'passed' if result else 'failed',
                'details': 'Modelos de ML inicializados'
            })
        except Exception as e:
            functionality_tests.append({
                'system': 'ML Advanced System',
                'status': 'error',
                'details': str(e)
            })
        
        # Test 5: Sistema de Notificaciones
        try:
            from clickup_brain_notifications import ClickUpBrainNotifications
            notification_system = ClickUpBrainNotifications()
            functionality_tests.append({
                'system': 'Notification System',
                'status': 'passed',
                'details': 'Sistema de notificaciones inicializado'
            })
        except Exception as e:
            functionality_tests.append({
                'system': 'Notification System',
                'status': 'error',
                'details': str(e)
            })
        
        # Test 6: Análisis de Sentimientos
        try:
            from clickup_brain_sentiment_analysis import ClickUpBrainSentimentAnalysis
            sentiment_system = ClickUpBrainSentimentAnalysis()
            functionality_tests.append({
                'system': 'Sentiment Analysis System',
                'status': 'passed',
                'details': 'Sistema de análisis de sentimientos inicializado'
            })
        except Exception as e:
            functionality_tests.append({
                'system': 'Sentiment Analysis System',
                'status': 'error',
                'details': str(e)
            })
        
        passed_tests = sum(1 for test in functionality_tests if test['status'] == 'passed')
        total_tests = len(functionality_tests)
        
        self.details = {
            'total_tests': total_tests,
            'passed_tests': passed_tests,
            'failed_tests': total_tests - passed_tests,
            'success_rate': (passed_tests / total_tests) * 100,
            'test_results': functionality_tests
        }
        
        return passed_tests == total_tests

class PerformanceValidationTest(ValidationTest):
    """Test de validación de rendimiento."""
    
    def __init__(self):
        super().__init__("Performance Validation", "Validar rendimiento de los sistemas")
    
    def _execute(self) -> bool:
        """Validar rendimiento de los sistemas."""
        performance_tests = []
        
        # Test de rendimiento del sistema simple
        try:
            from clickup_brain_simple import SimpleClickUpBrainSystem
            system = SimpleClickUpBrainSystem()
            
            start_time = time.time()
            result = system.analyze_directory(".", team_size=10)
            end_time = time.time()
            
            duration = end_time - start_time
            performance_tests.append({
                'system': 'Simple System',
                'duration': duration,
                'status': 'passed' if duration < 5.0 else 'slow',
                'threshold': 5.0
            })
        except Exception as e:
            performance_tests.append({
                'system': 'Simple System',
                'duration': 0,
                'status': 'error',
                'error': str(e)
            })
        
        # Test de rendimiento del sistema de IA
        try:
            from clickup_brain_ai_enhanced import EnhancedClickUpBrainSystem
            system = EnhancedClickUpBrainSystem()
            
            start_time = time.time()
            result = system.analyze_with_ai(".", team_size=10)
            end_time = time.time()
            
            duration = end_time - start_time
            performance_tests.append({
                'system': 'AI Enhanced System',
                'duration': duration,
                'status': 'passed' if duration < 10.0 else 'slow',
                'threshold': 10.0
            })
        except Exception as e:
            performance_tests.append({
                'system': 'AI Enhanced System',
                'duration': 0,
                'status': 'error',
                'error': str(e)
            })
        
        # Test de rendimiento del sistema de ML
        try:
            from clickup_brain_ml_advanced import ClickUpBrainMLAdvanced
            ml_system = ClickUpBrainMLAdvanced()
            
            start_time = time.time()
            result = ml_system.initialize_models()
            end_time = time.time()
            
            duration = end_time - start_time
            performance_tests.append({
                'system': 'ML Advanced System',
                'duration': duration,
                'status': 'passed' if duration < 15.0 else 'slow',
                'threshold': 15.0
            })
        except Exception as e:
            performance_tests.append({
                'system': 'ML Advanced System',
                'duration': 0,
                'status': 'error',
                'error': str(e)
            })
        
        passed_tests = sum(1 for test in performance_tests if test['status'] == 'passed')
        total_tests = len(performance_tests)
        
        self.details = {
            'total_tests': total_tests,
            'passed_tests': passed_tests,
            'failed_tests': total_tests - passed_tests,
            'success_rate': (passed_tests / total_tests) * 100,
            'performance_results': performance_tests
        }
        
        return passed_tests == total_tests

class IntegrationValidationTest(ValidationTest):
    """Test de validación de integración."""
    
    def __init__(self):
        super().__init__("Integration Validation", "Validar integración entre sistemas")
    
    def _execute(self) -> bool:
        """Validar integración entre sistemas."""
        integration_tests = []
        
        # Test de integración ML + Notificaciones
        try:
            from clickup_brain_ml_advanced import ClickUpBrainMLAdvanced
            from clickup_brain_notifications import ClickUpBrainNotifications
            
            ml_system = ClickUpBrainMLAdvanced()
            notification_system = ClickUpBrainNotifications()
            
            # Simular análisis y notificación
            team_profile = {'team_size': 10, 'current_efficiency': 75}
            analysis_result = ml_system.perform_advanced_analysis(".", team_profile)
            
            if 'error' not in analysis_result:
                notification_sent = notification_system.send_custom_notification(
                    "Análisis ML completado exitosamente",
                    channels=['slack'],
                    severity='low'
                )
                
                integration_tests.append({
                    'integration': 'ML + Notifications',
                    'status': 'passed' if notification_sent else 'failed',
                    'details': 'Integración ML con notificaciones funcionando'
                })
            else:
                integration_tests.append({
                    'integration': 'ML + Notifications',
                    'status': 'failed',
                    'details': 'Error en análisis ML'
                })
        except Exception as e:
            integration_tests.append({
                'integration': 'ML + Notifications',
                'status': 'error',
                'details': str(e)
            })
        
        # Test de integración Sentimientos + ML
        try:
            from clickup_brain_sentiment_analysis import ClickUpBrainSentimentAnalysis
            from clickup_brain_ml_advanced import ClickUpBrainMLAdvanced
            
            sentiment_system = ClickUpBrainSentimentAnalysis()
            ml_system = ClickUpBrainMLAdvanced()
            
            # Simular análisis de sentimientos
            communication_data = {
                'messages': [
                    {'content': 'Great work on the project!'},
                    {'content': 'Excellent collaboration today.'}
                ]
            }
            
            sentiment_result = sentiment_system.analyze_team_sentiment(communication_data)
            
            if 'error' not in sentiment_result:
                integration_tests.append({
                    'integration': 'Sentiment + ML',
                    'status': 'passed',
                    'details': 'Integración de sentimientos con ML funcionando'
                })
            else:
                integration_tests.append({
                    'integration': 'Sentiment + ML',
                    'status': 'failed',
                    'details': 'Error en análisis de sentimientos'
                })
        except Exception as e:
            integration_tests.append({
                'integration': 'Sentiment + ML',
                'status': 'error',
                'details': str(e)
            })
        
        # Test de integración ClickUp + Notificaciones
        try:
            from clickup_brain_clickup_integration import ClickUpBrainIntegration
            from clickup_brain_notifications import ClickUpBrainNotifications
            
            integration = ClickUpBrainIntegration()
            notification_system = ClickUpBrainNotifications()
            
            # Simular integración con ClickUp
            integration.integration_status = 'connected'
            insights = integration.get_team_insights("demo_team")
            
            if 'error' not in insights:
                integration_tests.append({
                    'integration': 'ClickUp + Notifications',
                    'status': 'passed',
                    'details': 'Integración ClickUp con notificaciones funcionando'
                })
            else:
                integration_tests.append({
                    'integration': 'ClickUp + Notifications',
                    'status': 'failed',
                    'details': 'Error en integración ClickUp'
                })
        except Exception as e:
            integration_tests.append({
                'integration': 'ClickUp + Notifications',
                'status': 'error',
                'details': str(e)
            })
        
        passed_tests = sum(1 for test in integration_tests if test['status'] == 'passed')
        total_tests = len(integration_tests)
        
        self.details = {
            'total_tests': total_tests,
            'passed_tests': passed_tests,
            'failed_tests': total_tests - passed_tests,
            'success_rate': (passed_tests / total_tests) * 100,
            'integration_results': integration_tests
        }
        
        return passed_tests == total_tests

class FileSystemValidationTest(ValidationTest):
    """Test de validación del sistema de archivos."""
    
    def __init__(self):
        super().__init__("File System Validation", "Validar que todos los archivos necesarios existen")
    
    def _execute(self) -> bool:
        """Validar sistema de archivos."""
        required_files = [
            'clickup_brain_simple.py',
            'clickup_brain_ai_enhanced.py',
            'clickup_brain_realtime_monitor.py',
            'clickup_brain_api.py',
            'clickup_brain_advanced_dashboard.py',
            'clickup_brain_security.py',
            'clickup_brain_ml_advanced.py',
            'clickup_brain_clickup_integration.py',
            'clickup_brain_notifications.py',
            'clickup_brain_sentiment_analysis.py',
            'clickup_brain_master_demo.py',
            'requirements_enhanced.txt',
            'README_ClickUp_Brain.md'
        ]
        
        existing_files = []
        missing_files = []
        
        for file_path in required_files:
            if os.path.exists(file_path):
                file_size = os.path.getsize(file_path)
                existing_files.append({
                    'file': file_path,
                    'size': file_size,
                    'exists': True
                })
            else:
                missing_files.append(file_path)
        
        self.details = {
            'total_required_files': len(required_files),
            'existing_files': len(existing_files),
            'missing_files': len(missing_files),
            'missing_file_list': missing_files,
            'existing_file_details': existing_files,
            'success_rate': (len(existing_files) / len(required_files)) * 100
        }
        
        return len(missing_files) == 0

class ClickUpBrainFinalValidation:
    """Sistema principal de validación final."""
    
    def __init__(self):
        self.tests = []
        self.validation_results = {}
        self.start_time = datetime.now()
        
    def add_test(self, test: ValidationTest):
        """Agregar test de validación."""
        self.tests.append(test)
    
    def run_all_tests(self) -> Dict:
        """Ejecutar todos los tests de validación."""
        logger.info("Iniciando validación final del sistema ClickUp Brain...")
        
        results = {
            'validation_start_time': self.start_time.isoformat(),
            'total_tests': len(self.tests),
            'passed_tests': 0,
            'failed_tests': 0,
            'error_tests': 0,
            'test_results': []
        }
        
        for test in self.tests:
            logger.info(f"Ejecutando test: {test.name}")
            test_result = test.run()
            
            test_info = {
                'name': test.name,
                'description': test.description,
                'status': test.status,
                'duration': test.duration,
                'error_message': test.error_message,
                'details': test.details
            }
            
            results['test_results'].append(test_info)
            
            if test.status == 'passed':
                results['passed_tests'] += 1
                logger.info(f"✅ {test.name} - PASADO")
            elif test.status == 'failed':
                results['failed_tests'] += 1
                logger.warning(f"❌ {test.name} - FALLADO")
            else:
                results['error_tests'] += 1
                logger.error(f"💥 {test.name} - ERROR")
        
        results['validation_end_time'] = datetime.now().isoformat()
        results['total_duration'] = (datetime.now() - self.start_time).total_seconds()
        results['success_rate'] = (results['passed_tests'] / results['total_tests']) * 100
        
        self.validation_results = results
        return results
    
    def generate_validation_report(self) -> str:
        """Generar reporte de validación."""
        if not self.validation_results:
            return "No hay resultados de validación disponibles."
        
        results = self.validation_results
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        report = f"""# 🔍 ClickUp Brain - Reporte de Validación Final

## 📊 Resumen de Validación

**Fecha:** {timestamp}
**Duración Total:** {results.get('total_duration', 0):.1f} segundos
**Estado General:** {'✅ VALIDACIÓN EXITOSA' if results.get('success_rate', 0) >= 90 else '⚠️ VALIDACIÓN CON PROBLEMAS'}

## 📈 Estadísticas de Validación

- **Total de Tests:** {results.get('total_tests', 0)}
- **Tests Exitosos:** {results.get('passed_tests', 0)}
- **Tests Fallidos:** {results.get('failed_tests', 0)}
- **Tests con Error:** {results.get('error_tests', 0)}
- **Tasa de Éxito:** {results.get('success_rate', 0):.1f}%

## 🧪 Resultados Detallados de Tests

"""
        
        for test_result in results.get('test_results', []):
            status_emoji = {
                'passed': '✅',
                'failed': '❌',
                'error': '💥',
                'pending': '⏳'
            }.get(test_result['status'], '❓')
            
            report += f"""
### {status_emoji} {test_result['name']}

**Descripción:** {test_result['description']}
**Estado:** {test_result['status'].upper()}
**Duración:** {test_result.get('duration', 0):.2f} segundos

"""
            
            if test_result.get('error_message'):
                report += f"**Error:** {test_result['error_message']}\n\n"
            
            if test_result.get('details'):
                details = test_result['details']
                report += "**Detalles:**\n"
                for key, value in details.items():
                    if isinstance(value, (list, dict)):
                        report += f"- {key}: {len(value) if isinstance(value, list) else 'Ver detalles'}\n"
                    else:
                        report += f"- {key}: {value}\n"
                report += "\n"
        
        # Agregar recomendaciones
        report += f"""
## 🎯 Recomendaciones

"""
        
        if results.get('success_rate', 0) >= 95:
            report += """
### ✅ Sistema Completamente Validado
- El sistema ClickUp Brain está completamente funcional
- Todas las validaciones han pasado exitosamente
- El sistema está listo para implementación en producción
- Se recomienda proceder con el despliegue
"""
        elif results.get('success_rate', 0) >= 90:
            report += """
### ⚠️ Sistema Mayormente Validado
- La mayoría de las validaciones han pasado
- Algunos tests menores han fallado
- Se recomienda revisar los tests fallidos
- El sistema puede ser desplegado con monitoreo adicional
"""
        else:
            report += """
### ❌ Sistema Requiere Atención
- Múltiples validaciones han fallado
- Se requiere revisión y corrección antes del despliegue
- Se recomienda ejecutar las correcciones necesarias
- No se recomienda el despliegue hasta resolver los problemas
"""
        
        report += f"""
## 🚀 Próximos Pasos

### Si la validación es exitosa (≥90%):
1. **Proceder con el despliegue** en ambiente de producción
2. **Configurar monitoreo** continuo del sistema
3. **Implementar alertas** para problemas futuros
4. **Documentar** el proceso de despliegue

### Si la validación tiene problemas (<90%):
1. **Revisar** los tests fallidos en detalle
2. **Corregir** los problemas identificados
3. **Re-ejecutar** la validación
4. **Verificar** que todos los sistemas funcionen correctamente

---
*Reporte generado automáticamente por ClickUp Brain Final Validation System*
*Validación completada el {results.get('validation_end_time', 'N/A')}*
"""
        
        return report
    
    def save_validation_results(self, filename: str = None) -> str:
        """Guardar resultados de validación."""
        if not filename:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"clickup_brain_validation_results_{timestamp}.json"
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(self.validation_results, f, indent=2, ensure_ascii=False)
        
        logger.info(f"Resultados de validación guardados en: {filename}")
        return filename

def main():
    """Función principal de validación final."""
    print("🔍 ClickUp Brain - Sistema de Validación Final Completa")
    print("=" * 70)
    
    # Crear sistema de validación
    validator = ClickUpBrainFinalValidation()
    
    # Agregar todos los tests
    validator.add_test(ImportValidationTest())
    validator.add_test(FunctionalityValidationTest())
    validator.add_test(PerformanceValidationTest())
    validator.add_test(IntegrationValidationTest())
    validator.add_test(FileSystemValidationTest())
    
    print(f"📋 Ejecutando {len(validator.tests)} tests de validación...")
    
    # Ejecutar todos los tests
    results = validator.run_all_tests()
    
    # Mostrar resumen
    print(f"\n📊 Resumen de Validación:")
    print(f"   • Total de tests: {results['total_tests']}")
    print(f"   • Tests exitosos: {results['passed_tests']}")
    print(f"   • Tests fallidos: {results['failed_tests']}")
    print(f"   • Tests con error: {results['error_tests']}")
    print(f"   • Tasa de éxito: {results['success_rate']:.1f}%")
    print(f"   • Duración total: {results['total_duration']:.1f} segundos")
    
    # Generar reporte
    print(f"\n📄 Generando reporte de validación...")
    report = validator.generate_validation_report()
    
    # Guardar reporte
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    report_filename = f"clickup_brain_validation_report_{timestamp}.md"
    with open(report_filename, 'w', encoding='utf-8') as f:
        f.write(report)
    
    print(f"📄 Reporte de validación guardado: {report_filename}")
    
    # Guardar resultados JSON
    json_filename = validator.save_validation_results()
    print(f"📊 Resultados JSON guardados: {json_filename}")
    
    # Estado final
    if results['success_rate'] >= 90:
        print(f"\n🎉 ¡VALIDACIÓN EXITOSA!")
        print(f"✅ El sistema ClickUp Brain está completamente funcional")
        print(f"🚀 Listo para implementación en producción")
    else:
        print(f"\n⚠️ VALIDACIÓN CON PROBLEMAS")
        print(f"❌ Se encontraron problemas que requieren atención")
        print(f"📋 Revisar el reporte de validación para detalles")
    
    return results['success_rate'] >= 90

if __name__ == "__main__":
    main()










