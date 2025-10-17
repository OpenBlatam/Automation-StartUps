#!/usr/bin/env python3
"""
Sistema de Testing y Control de Calidad para Neural Marketing Consciousness Platform
"""

import json
import time
import sqlite3
import unittest
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
import random
import statistics

class TestingQualitySystem:
    def __init__(self, db_path="testing_quality.db"):
        self.db_path = db_path
        self.test_suites = {}
        self.quality_metrics = {}
        self.init_testing_database()
        self.load_test_configurations()
    
    def init_testing_database(self):
        """Inicializar base de datos de testing"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Tabla de suites de pruebas
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS test_suites (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT UNIQUE NOT NULL,
                description TEXT,
                category TEXT NOT NULL,
                status TEXT DEFAULT 'active',
                created_at TEXT,
                updated_at TEXT
            )
        ''')
        
        # Tabla de casos de prueba
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS test_cases (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                suite_id INTEGER,
                name TEXT NOT NULL,
                description TEXT,
                test_type TEXT NOT NULL,
                priority TEXT DEFAULT 'medium',
                status TEXT DEFAULT 'active',
                steps TEXT,
                expected_result TEXT,
                created_at TEXT,
                FOREIGN KEY (suite_id) REFERENCES test_suites (id)
            )
        ''')
        
        # Tabla de ejecuciones de pruebas
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS test_executions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                test_case_id INTEGER,
                execution_time TEXT,
                status TEXT NOT NULL,
                duration_ms INTEGER,
                error_message TEXT,
                actual_result TEXT,
                environment TEXT,
                executed_by TEXT,
                FOREIGN KEY (test_case_id) REFERENCES test_cases (id)
            )
        ''')
        
        # Tabla de métricas de calidad
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS quality_metrics (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                metric_name TEXT NOT NULL,
                metric_value REAL NOT NULL,
                metric_type TEXT NOT NULL,
                component TEXT,
                timestamp TEXT,
                environment TEXT
            )
        ''')
        
        # Tabla de reportes de calidad
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS quality_reports (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                report_name TEXT NOT NULL,
                report_type TEXT NOT NULL,
                data TEXT,
                generated_at TEXT,
                generated_by TEXT
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def load_test_configurations(self):
        """Cargar configuraciones de testing"""
        self.test_suites = {
            'unit_tests': {
                'name': 'Unit Tests',
                'description': 'Pruebas unitarias para componentes individuales',
                'category': 'functional',
                'test_cases': [
                    {
                        'name': 'test_ai_model_selection',
                        'description': 'Verificar selección correcta de modelos de IA',
                        'test_type': 'unit',
                        'priority': 'high',
                        'steps': [
                            'Inicializar sistema de IA',
                            'Proporcionar requisitos de contenido',
                            'Verificar selección de modelo óptimo'
                        ],
                        'expected_result': 'Modelo correcto seleccionado según requisitos'
                    },
                    {
                        'name': 'test_consciousness_calculation',
                        'description': 'Verificar cálculo de nivel de conciencia',
                        'test_type': 'unit',
                        'priority': 'high',
                        'steps': [
                            'Proporcionar datos de usuario',
                            'Calcular nivel de conciencia',
                            'Verificar resultado dentro del rango esperado'
                        ],
                        'expected_result': 'Nivel de conciencia calculado correctamente'
                    }
                ]
            },
            'integration_tests': {
                'name': 'Integration Tests',
                'description': 'Pruebas de integración entre componentes',
                'category': 'functional',
                'test_cases': [
                    {
                        'name': 'test_api_integration',
                        'description': 'Verificar integración de APIs externas',
                        'test_type': 'integration',
                        'priority': 'high',
                        'steps': [
                            'Configurar integración con API externa',
                            'Realizar llamada de prueba',
                            'Verificar respuesta y datos'
                        ],
                        'expected_result': 'Integración exitosa con API externa'
                    },
                    {
                        'name': 'test_database_integration',
                        'description': 'Verificar integración con base de datos',
                        'test_type': 'integration',
                        'priority': 'high',
                        'steps': [
                            'Conectar a base de datos',
                            'Realizar operaciones CRUD',
                            'Verificar consistencia de datos'
                        ],
                        'expected_result': 'Operaciones de base de datos exitosas'
                    }
                ]
            },
            'performance_tests': {
                'name': 'Performance Tests',
                'description': 'Pruebas de rendimiento y escalabilidad',
                'category': 'non_functional',
                'test_cases': [
                    {
                        'name': 'test_response_time',
                        'description': 'Verificar tiempos de respuesta de API',
                        'test_type': 'performance',
                        'priority': 'medium',
                        'steps': [
                            'Realizar múltiples llamadas a API',
                            'Medir tiempos de respuesta',
                            'Verificar que estén dentro de límites'
                        ],
                        'expected_result': 'Tiempo de respuesta < 2 segundos'
                    },
                    {
                        'name': 'test_concurrent_users',
                        'description': 'Verificar comportamiento con usuarios concurrentes',
                        'test_type': 'performance',
                        'priority': 'high',
                        'steps': [
                            'Simular 1000 usuarios concurrentes',
                            'Monitorear rendimiento del sistema',
                            'Verificar estabilidad'
                        ],
                        'expected_result': 'Sistema estable con 1000 usuarios concurrentes'
                    }
                ]
            },
            'security_tests': {
                'name': 'Security Tests',
                'description': 'Pruebas de seguridad y vulnerabilidades',
                'category': 'security',
                'test_cases': [
                    {
                        'name': 'test_authentication',
                        'description': 'Verificar sistema de autenticación',
                        'test_type': 'security',
                        'priority': 'high',
                        'steps': [
                            'Intentar acceso sin credenciales',
                            'Probar con credenciales inválidas',
                            'Verificar con credenciales válidas'
                        ],
                        'expected_result': 'Solo acceso autorizado permitido'
                    },
                    {
                        'name': 'test_input_validation',
                        'description': 'Verificar validación de entrada',
                        'test_type': 'security',
                        'priority': 'high',
                        'steps': [
                            'Enviar datos maliciosos',
                            'Probar inyección SQL',
                            'Verificar sanitización'
                        ],
                        'expected_result': 'Datos maliciosos rechazados'
                    }
                ]
            },
            'ai_quality_tests': {
                'name': 'AI Quality Tests',
                'description': 'Pruebas de calidad de IA y contenido generado',
                'category': 'ai_quality',
                'test_cases': [
                    {
                        'name': 'test_content_quality',
                        'description': 'Verificar calidad del contenido generado',
                        'test_type': 'ai_quality',
                        'priority': 'high',
                        'steps': [
                            'Generar contenido con IA',
                            'Evaluar calidad del contenido',
                            'Verificar métricas de calidad'
                        ],
                        'expected_result': 'Calidad de contenido > 80%'
                    },
                    {
                        'name': 'test_ai_accuracy',
                        'description': 'Verificar precisión de modelos de IA',
                        'test_type': 'ai_quality',
                        'priority': 'high',
                        'steps': [
                            'Probar modelo con datos conocidos',
                            'Calcular precisión',
                            'Verificar que supere umbral'
                        ],
                        'expected_result': 'Precisión > 90%'
                    }
                ]
            }
        }
    
    def create_test_suite(self, name: str, description: str, category: str) -> Dict:
        """Crear nueva suite de pruebas"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO test_suites (name, description, category, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?)
            ''', (name, description, category, datetime.now().isoformat(), datetime.now().isoformat()))
            
            suite_id = cursor.lastrowid
            
            # Agregar casos de prueba si existen en configuración
            if name in self.test_suites:
                for test_case in self.test_suites[name]['test_cases']:
                    cursor.execute('''
                        INSERT INTO test_cases (suite_id, name, description, test_type, priority, steps, expected_result, created_at)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                    ''', (suite_id, test_case['name'], test_case['description'], 
                          test_case['test_type'], test_case['priority'], 
                          json.dumps(test_case['steps']), test_case['expected_result'],
                          datetime.now().isoformat()))
            
            conn.commit()
            conn.close()
            
            return {'success': True, 'message': f'Test suite {name} created successfully', 'suite_id': suite_id}
            
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def add_test_case(self, suite_name: str, name: str, description: str, 
                     test_type: str, priority: str = 'medium', steps: List[str] = None, 
                     expected_result: str = '') -> Dict:
        """Agregar caso de prueba"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Obtener ID de suite
            cursor.execute('SELECT id FROM test_suites WHERE name = ?', (suite_name,))
            result = cursor.fetchone()
            if not result:
                return {'success': False, 'error': 'Test suite not found'}
            
            suite_id = result[0]
            
            cursor.execute('''
                INSERT INTO test_cases (suite_id, name, description, test_type, priority, steps, expected_result, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (suite_id, name, description, test_type, priority, 
                  json.dumps(steps or []), expected_result, datetime.now().isoformat()))
            
            conn.commit()
            conn.close()
            
            return {'success': True, 'message': f'Test case {name} added successfully'}
            
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def execute_test_case(self, test_case_name: str, environment: str = 'test', 
                         executed_by: str = 'system') -> Dict:
        """Ejecutar caso de prueba individual"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Obtener caso de prueba
            cursor.execute('''
                SELECT id, name, test_type, steps, expected_result
                FROM test_cases WHERE name = ? AND status = 'active'
            ''', (test_case_name,))
            
            result = cursor.fetchone()
            if not result:
                return {'success': False, 'error': 'Test case not found'}
            
            test_case_id, name, test_type, steps_json, expected_result = result
            steps = json.loads(steps_json) if steps_json else []
            
            # Ejecutar prueba
            start_time = time.time()
            execution_result = self.run_test_execution(test_type, steps, expected_result)
            duration_ms = int((time.time() - start_time) * 1000)
            
            # Registrar ejecución
            cursor.execute('''
                INSERT INTO test_executions (test_case_id, execution_time, status, duration_ms, 
                                           error_message, actual_result, environment, executed_by)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (test_case_id, datetime.now().isoformat(), execution_result['status'], 
                  duration_ms, execution_result.get('error_message'), 
                  execution_result.get('actual_result'), environment, executed_by))
            
            conn.commit()
            conn.close()
            
            return {
                'success': True,
                'test_case': name,
                'status': execution_result['status'],
                'duration_ms': duration_ms,
                'result': execution_result
            }
            
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def run_test_execution(self, test_type: str, steps: List[str], expected_result: str) -> Dict:
        """Ejecutar lógica de prueba"""
        try:
            if test_type == 'unit':
                return self.run_unit_test(steps, expected_result)
            elif test_type == 'integration':
                return self.run_integration_test(steps, expected_result)
            elif test_type == 'performance':
                return self.run_performance_test(steps, expected_result)
            elif test_type == 'security':
                return self.run_security_test(steps, expected_result)
            elif test_type == 'ai_quality':
                return self.run_ai_quality_test(steps, expected_result)
            else:
                return {'status': 'failed', 'error_message': 'Unknown test type'}
                
        except Exception as e:
            return {'status': 'failed', 'error_message': str(e)}
    
    def run_unit_test(self, steps: List[str], expected_result: str) -> Dict:
        """Ejecutar prueba unitaria"""
        # Simular ejecución de prueba unitaria
        success_rate = random.uniform(0.85, 0.98)
        
        if success_rate > 0.9:
            return {
                'status': 'passed',
                'actual_result': 'Test passed successfully',
                'metrics': {'coverage': 95.5, 'execution_time': 0.1}
            }
        else:
            return {
                'status': 'failed',
                'error_message': 'Assertion failed: Expected value not found',
                'actual_result': 'Test failed'
            }
    
    def run_integration_test(self, steps: List[str], expected_result: str) -> Dict:
        """Ejecutar prueba de integración"""
        # Simular ejecución de prueba de integración
        success_rate = random.uniform(0.80, 0.95)
        
        if success_rate > 0.85:
            return {
                'status': 'passed',
                'actual_result': 'Integration test passed',
                'metrics': {'response_time': 1.2, 'data_consistency': 100}
            }
        else:
            return {
                'status': 'failed',
                'error_message': 'Integration failed: API timeout',
                'actual_result': 'Connection error'
            }
    
    def run_performance_test(self, steps: List[str], expected_result: str) -> Dict:
        """Ejecutar prueba de rendimiento"""
        # Simular ejecución de prueba de rendimiento
        response_time = random.uniform(0.5, 3.0)
        memory_usage = random.uniform(60, 90)
        
        if response_time < 2.0 and memory_usage < 85:
            return {
                'status': 'passed',
                'actual_result': f'Performance test passed - Response time: {response_time:.2f}s',
                'metrics': {
                    'response_time': response_time,
                    'memory_usage': memory_usage,
                    'throughput': 1000
                }
            }
        else:
            return {
                'status': 'failed',
                'error_message': f'Performance threshold exceeded - Response time: {response_time:.2f}s',
                'actual_result': 'Performance test failed'
            }
    
    def run_security_test(self, steps: List[str], expected_result: str) -> Dict:
        """Ejecutar prueba de seguridad"""
        # Simular ejecución de prueba de seguridad
        vulnerability_score = random.uniform(0, 10)
        
        if vulnerability_score < 3:
            return {
                'status': 'passed',
                'actual_result': 'Security test passed - No vulnerabilities found',
                'metrics': {
                    'vulnerability_score': vulnerability_score,
                    'security_level': 'high'
                }
            }
        else:
            return {
                'status': 'failed',
                'error_message': f'Security vulnerability detected - Score: {vulnerability_score:.1f}',
                'actual_result': 'Security test failed'
            }
    
    def run_ai_quality_test(self, steps: List[str], expected_result: str) -> Dict:
        """Ejecutar prueba de calidad de IA"""
        # Simular ejecución de prueba de calidad de IA
        quality_score = random.uniform(75, 95)
        accuracy = random.uniform(85, 98)
        
        if quality_score > 80 and accuracy > 90:
            return {
                'status': 'passed',
                'actual_result': f'AI quality test passed - Quality: {quality_score:.1f}%',
                'metrics': {
                    'quality_score': quality_score,
                    'accuracy': accuracy,
                    'coherence': 92.5
                }
            }
        else:
            return {
                'status': 'failed',
                'error_message': f'AI quality below threshold - Quality: {quality_score:.1f}%',
                'actual_result': 'AI quality test failed'
            }
    
    def execute_test_suite(self, suite_name: str, environment: str = 'test') -> Dict:
        """Ejecutar suite completa de pruebas"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Obtener casos de prueba de la suite
            cursor.execute('''
                SELECT tc.id, tc.name, tc.test_type, tc.steps, tc.expected_result
                FROM test_cases tc
                JOIN test_suites ts ON tc.suite_id = ts.id
                WHERE ts.name = ? AND tc.status = 'active'
            ''', (suite_name,))
            
            test_cases = cursor.fetchall()
            if not test_cases:
                return {'success': False, 'error': 'No test cases found for suite'}
            
            # Ejecutar todos los casos de prueba
            results = []
            passed = 0
            failed = 0
            total_duration = 0
            
            for test_case in test_cases:
                test_case_id, name, test_type, steps_json, expected_result = test_case
                steps = json.loads(steps_json) if steps_json else []
                
                start_time = time.time()
                execution_result = self.run_test_execution(test_type, steps, expected_result)
                duration_ms = int((time.time() - start_time) * 1000)
                total_duration += duration_ms
                
                # Registrar ejecución
                cursor.execute('''
                    INSERT INTO test_executions (test_case_id, execution_time, status, duration_ms, 
                                               error_message, actual_result, environment, executed_by)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                ''', (test_case_id, datetime.now().isoformat(), execution_result['status'], 
                      duration_ms, execution_result.get('error_message'), 
                      execution_result.get('actual_result'), environment, 'system'))
                
                if execution_result['status'] == 'passed':
                    passed += 1
                else:
                    failed += 1
                
                results.append({
                    'test_case': name,
                    'status': execution_result['status'],
                    'duration_ms': duration_ms,
                    'result': execution_result
                })
            
            conn.commit()
            conn.close()
            
            return {
                'success': True,
                'suite_name': suite_name,
                'total_tests': len(test_cases),
                'passed': passed,
                'failed': failed,
                'pass_rate': (passed / len(test_cases)) * 100,
                'total_duration_ms': total_duration,
                'results': results
            }
            
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def record_quality_metric(self, metric_name: str, metric_value: float, 
                            metric_type: str, component: str = None, 
                            environment: str = 'production') -> Dict:
        """Registrar métrica de calidad"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO quality_metrics (metric_name, metric_value, metric_type, component, timestamp, environment)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (metric_name, metric_value, metric_type, component, 
                  datetime.now().isoformat(), environment))
            
            conn.commit()
            conn.close()
            
            return {'success': True, 'message': f'Quality metric {metric_name} recorded'}
            
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def generate_quality_report(self, report_type: str = 'comprehensive', 
                              start_date: str = None, end_date: str = None) -> Dict:
        """Generar reporte de calidad"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Obtener métricas de calidad
            date_filter = ""
            params = []
            if start_date and end_date:
                date_filter = "WHERE timestamp BETWEEN ? AND ?"
                params = [start_date, end_date]
            
            cursor.execute(f'''
                SELECT metric_name, metric_value, metric_type, component, timestamp
                FROM quality_metrics {date_filter}
                ORDER BY timestamp DESC
            ''', params)
            
            metrics = cursor.fetchall()
            
            # Obtener estadísticas de pruebas
            cursor.execute('''
                SELECT 
                    COUNT(*) as total_executions,
                    SUM(CASE WHEN status = 'passed' THEN 1 ELSE 0 END) as passed,
                    AVG(duration_ms) as avg_duration,
                    MAX(execution_time) as last_execution
                FROM test_executions
            ''')
            
            test_stats = cursor.fetchone()
            
            # Generar reporte
            report_data = {
                'report_type': report_type,
                'generated_at': datetime.now().isoformat(),
                'test_statistics': {
                    'total_executions': test_stats[0] or 0,
                    'passed_tests': test_stats[1] or 0,
                    'pass_rate': (test_stats[1] / test_stats[0] * 100) if test_stats[0] > 0 else 0,
                    'avg_duration_ms': test_stats[2] or 0,
                    'last_execution': test_stats[3]
                },
                'quality_metrics': self.analyze_quality_metrics(metrics),
                'recommendations': self.generate_quality_recommendations(metrics, test_stats)
            }
            
            # Guardar reporte
            cursor.execute('''
                INSERT INTO quality_reports (report_name, report_type, data, generated_at, generated_by)
                VALUES (?, ?, ?, ?, ?)
            ''', (f'Quality Report {datetime.now().strftime("%Y-%m-%d")}', report_type, 
                  json.dumps(report_data), datetime.now().isoformat(), 'system'))
            
            conn.commit()
            conn.close()
            
            return {
                'success': True,
                'report_data': report_data,
                'message': 'Quality report generated successfully'
            }
            
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def analyze_quality_metrics(self, metrics: List) -> Dict:
        """Analizar métricas de calidad"""
        if not metrics:
            return {}
        
        # Agrupar métricas por nombre
        metric_groups = {}
        for metric in metrics:
            name = metric[0]
            value = metric[1]
            if name not in metric_groups:
                metric_groups[name] = []
            metric_groups[name].append(value)
        
        # Calcular estadísticas
        analysis = {}
        for name, values in metric_groups.items():
            analysis[name] = {
                'count': len(values),
                'average': statistics.mean(values),
                'min': min(values),
                'max': max(values),
                'trend': 'stable'  # Simplificado
            }
        
        return analysis
    
    def generate_quality_recommendations(self, metrics: List, test_stats: tuple) -> List[str]:
        """Generar recomendaciones de calidad"""
        recommendations = []
        
        # Análisis de tasa de éxito de pruebas
        if test_stats[0] > 0:
            pass_rate = (test_stats[1] / test_stats[0]) * 100
            if pass_rate < 80:
                recommendations.append("⚠️ Tasa de éxito de pruebas baja - Revisar casos de prueba fallidos")
            elif pass_rate > 95:
                recommendations.append("✅ Excelente tasa de éxito de pruebas")
        
        # Análisis de duración promedio
        if test_stats[2] and test_stats[2] > 5000:  # 5 segundos
            recommendations.append("🐌 Pruebas lentas detectadas - Optimizar casos de prueba")
        
        # Análisis de métricas de calidad
        if metrics:
            # Buscar métricas de rendimiento
            performance_metrics = [m for m in metrics if 'response_time' in m[0].lower() or 'performance' in m[0].lower()]
            if performance_metrics:
                avg_response_time = statistics.mean([m[1] for m in performance_metrics])
                if avg_response_time > 2000:  # 2 segundos
                    recommendations.append("⚡ Tiempo de respuesta alto - Optimizar rendimiento")
        
        if not recommendations:
            recommendations.append("✅ Sistema funcionando dentro de parámetros normales")
        
        return recommendations
    
    def get_test_summary(self) -> Dict:
        """Obtener resumen de pruebas"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Estadísticas generales
            cursor.execute('''
                SELECT 
                    COUNT(DISTINCT ts.id) as total_suites,
                    COUNT(tc.id) as total_test_cases,
                    COUNT(te.id) as total_executions,
                    SUM(CASE WHEN te.status = 'passed' THEN 1 ELSE 0 END) as passed_executions,
                    AVG(te.duration_ms) as avg_duration
                FROM test_suites ts
                LEFT JOIN test_cases tc ON ts.id = tc.suite_id
                LEFT JOIN test_executions te ON tc.id = te.test_case_id
            ''')
            
            stats = cursor.fetchone()
            
            # Últimas ejecuciones
            cursor.execute('''
                SELECT tc.name, te.status, te.execution_time, te.duration_ms
                FROM test_executions te
                JOIN test_cases tc ON te.test_case_id = tc.id
                ORDER BY te.execution_time DESC
                LIMIT 10
            ''')
            
            recent_executions = cursor.fetchall()
            
            conn.close()
            
            return {
                'total_suites': stats[0] or 0,
                'total_test_cases': stats[1] or 0,
                'total_executions': stats[2] or 0,
                'passed_executions': stats[3] or 0,
                'pass_rate': (stats[3] / stats[2] * 100) if stats[2] > 0 else 0,
                'avg_duration_ms': stats[4] or 0,
                'recent_executions': [
                    {
                        'test_case': row[0],
                        'status': row[1],
                        'execution_time': row[2],
                        'duration_ms': row[3]
                    }
                    for row in recent_executions
                ]
            }
            
        except Exception as e:
            return {'error': str(e)}

def main():
    testing = TestingQualitySystem()
    
    print("🧪 Sistema de Testing y Control de Calidad")
    print("=" * 50)
    print("1. Crear suite de pruebas")
    print("2. Agregar caso de prueba")
    print("3. Ejecutar caso de prueba")
    print("4. Ejecutar suite completa")
    print("5. Registrar métrica de calidad")
    print("6. Generar reporte de calidad")
    print("7. Ver resumen de pruebas")
    print("8. Ejecutar todas las pruebas")
    print("9. Salir")
    
    while True:
        choice = input("\nSeleccione una opción (1-9): ").strip()
        
        if choice == '1':
            print("\nSuites de prueba disponibles:")
            for name, config in testing.test_suites.items():
                print(f"  • {name}: {config['name']} ({config['category']})")
            
            suite_name = input("Nombre de suite: ").strip()
            if suite_name in testing.test_suites:
                config = testing.test_suites[suite_name]
                result = testing.create_test_suite(suite_name, config['description'], config['category'])
                print(f"✅ {result['message']}" if result['success'] else f"❌ {result['error']}")
            else:
                description = input("Descripción: ").strip()
                category = input("Categoría: ").strip()
                result = testing.create_test_suite(suite_name, description, category)
                print(f"✅ {result['message']}" if result['success'] else f"❌ {result['error']}")
        
        elif choice == '2':
            suite_name = input("Nombre de suite: ").strip()
            name = input("Nombre del caso de prueba: ").strip()
            description = input("Descripción: ").strip()
            test_type = input("Tipo de prueba (unit/integration/performance/security/ai_quality): ").strip()
            priority = input("Prioridad (low/medium/high): ").strip() or 'medium'
            
            result = testing.add_test_case(suite_name, name, description, test_type, priority)
            print(f"✅ {result['message']}" if result['success'] else f"❌ {result['error']}")
        
        elif choice == '3':
            test_case_name = input("Nombre del caso de prueba: ").strip()
            environment = input("Entorno (test/staging/production): ").strip() or 'test'
            
            result = testing.execute_test_case(test_case_name, environment)
            if result['success']:
                print(f"✅ {result['test_case']} - {result['status']} ({result['duration_ms']}ms)")
            else:
                print(f"❌ {result['error']}")
        
        elif choice == '4':
            suite_name = input("Nombre de suite: ").strip()
            environment = input("Entorno (test/staging/production): ").strip() or 'test'
            
            result = testing.execute_test_suite(suite_name, environment)
            if result['success']:
                print(f"✅ Suite {result['suite_name']} ejecutada:")
                print(f"   Total: {result['total_tests']}")
                print(f"   Pasaron: {result['passed']}")
                print(f"   Fallaron: {result['failed']}")
                print(f"   Tasa de éxito: {result['pass_rate']:.1f}%")
                print(f"   Duración total: {result['total_duration_ms']}ms")
            else:
                print(f"❌ {result['error']}")
        
        elif choice == '5':
            metric_name = input("Nombre de métrica: ").strip()
            metric_value = float(input("Valor: ").strip())
            metric_type = input("Tipo (performance/quality/security): ").strip()
            component = input("Componente (opcional): ").strip() or None
            
            result = testing.record_quality_metric(metric_name, metric_value, metric_type, component)
            print(f"✅ {result['message']}" if result['success'] else f"❌ {result['error']}")
        
        elif choice == '6':
            report_type = input("Tipo de reporte (comprehensive/summary): ").strip() or 'comprehensive'
            
            result = testing.generate_quality_report(report_type)
            if result['success']:
                print(f"✅ {result['message']}")
                report = result['report_data']
                print(f"\n📊 Resumen del Reporte:")
                print(f"   Tasa de éxito: {report['test_statistics']['pass_rate']:.1f}%")
                print(f"   Total ejecuciones: {report['test_statistics']['total_executions']}")
                print(f"   Recomendaciones: {len(report['recommendations'])}")
            else:
                print(f"❌ {result['error']}")
        
        elif choice == '7':
            summary = testing.get_test_summary()
            if 'error' in summary:
                print(f"❌ {summary['error']}")
            else:
                print(f"\n📊 Resumen de Pruebas:")
                print(f"   Suites: {summary['total_suites']}")
                print(f"   Casos de prueba: {summary['total_test_cases']}")
                print(f"   Ejecuciones: {summary['total_executions']}")
                print(f"   Tasa de éxito: {summary['pass_rate']:.1f}%")
                print(f"   Duración promedio: {summary['avg_duration_ms']:.1f}ms")
        
        elif choice == '8':
            print("🚀 Ejecutando todas las pruebas...")
            for suite_name in testing.test_suites.keys():
                print(f"\n📋 Ejecutando suite: {suite_name}")
                result = testing.execute_test_suite(suite_name)
                if result['success']:
                    print(f"   ✅ {result['passed']}/{result['total_tests']} pasaron ({result['pass_rate']:.1f}%)")
                else:
                    print(f"   ❌ Error: {result['error']}")
        
        elif choice == '9':
            print("👋 ¡Hasta luego!")
            break
        
        else:
            print("❌ Opción no válida")

if __name__ == "__main__":
    main()


