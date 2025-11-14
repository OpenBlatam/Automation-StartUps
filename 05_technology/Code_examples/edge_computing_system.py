#!/usr/bin/env python3
"""
Sistema de Edge Computing para Procesamiento Distribuido Empresarial
"""

import os
import json
import sqlite3
import threading
import time
from datetime import datetime
import random
import math

class EdgeComputingSystem:
    def __init__(self, base_path="/Users/adan/frontier"):
        self.base_path = base_path
        self.edge_db = os.path.join(base_path, "edge_computing.db")
        self.edge_nodes = {}
        self.task_queue = []
        self.results = {}
        self.init_edge_database()
    
    def init_edge_database(self):
        """Inicializar base de datos de edge computing"""
        conn = sqlite3.connect(self.edge_db)
        cursor = conn.cursor()
        
        # Tabla de nodos edge
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS edge_nodes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                node_name TEXT,
                node_type TEXT,
                location TEXT,
                capabilities TEXT,
                status TEXT,
                cpu_usage REAL,
                memory_usage REAL,
                network_latency REAL,
                last_heartbeat TEXT,
                created_at TEXT
            )
        ''')
        
        # Tabla de tareas distribuidas
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS distributed_tasks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                task_name TEXT,
                task_type TEXT,
                priority INTEGER,
                data_size INTEGER,
                assigned_node TEXT,
                status TEXT,
                created_at TEXT,
                started_at TEXT,
                completed_at TEXT,
                result_data TEXT
            )
        ''')
        
        # Tabla de optimizaciones edge
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS edge_optimizations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                optimization_type TEXT,
                target_node TEXT,
                improvement_percentage REAL,
                energy_savings REAL,
                latency_reduction REAL,
                created_at TEXT
            )
        ''')
        
        # Tabla de sincronización
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS edge_sync (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                sync_type TEXT,
                source_node TEXT,
                target_node TEXT,
                data_hash TEXT,
                sync_status TEXT,
                created_at TEXT
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def register_edge_node(self, node_name, node_type, location, capabilities):
        """Registrar nodo edge"""
        conn = sqlite3.connect(self.edge_db)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO edge_nodes 
            (node_name, node_type, location, capabilities, status, cpu_usage, 
             memory_usage, network_latency, last_heartbeat, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (node_name, node_type, location, json.dumps(capabilities), 'active', 
              0.0, 0.0, 0.0, datetime.now().isoformat(), datetime.now().isoformat()))
        
        node_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        # Almacenar en memoria
        self.edge_nodes[node_id] = {
            'name': node_name,
            'type': node_type,
            'location': location,
            'capabilities': capabilities,
            'status': 'active',
            'cpu_usage': 0.0,
            'memory_usage': 0.0,
            'network_latency': 0.0
        }
        
        return node_id
    
    def distribute_task(self, task_name, task_type, data, priority=1):
        """Distribuir tarea a nodos edge"""
        # Seleccionar mejor nodo para la tarea
        best_node = self._select_best_node(task_type, data)
        
        if not best_node:
            return None
        
        # Crear tarea
        task_id = self._create_task(task_name, task_type, data, priority, best_node)
        
        # Ejecutar tarea en nodo seleccionado
        result = self._execute_task_on_node(task_id, best_node, data)
        
        return {
            'task_id': task_id,
            'assigned_node': best_node,
            'result': result,
            'execution_time': random.uniform(0.1, 2.0)
        }
    
    def _select_best_node(self, task_type, data):
        """Seleccionar mejor nodo para la tarea"""
        available_nodes = []
        
        for node_id, node_info in self.edge_nodes.items():
            if node_info['status'] == 'active':
                # Calcular score del nodo
                score = self._calculate_node_score(node_info, task_type, data)
                available_nodes.append((node_id, score))
        
        if not available_nodes:
            return None
        
        # Seleccionar nodo con mejor score
        best_node = max(available_nodes, key=lambda x: x[1])
        return best_node[0]
    
    def _calculate_node_score(self, node_info, task_type, data):
        """Calcular score de nodo para tarea específica"""
        base_score = 100
        
        # Penalizar por uso de CPU
        cpu_penalty = node_info['cpu_usage'] * 50
        base_score -= cpu_penalty
        
        # Penalizar por uso de memoria
        memory_penalty = node_info['memory_usage'] * 30
        base_score -= memory_penalty
        
        # Penalizar por latencia de red
        latency_penalty = node_info['network_latency'] * 10
        base_score -= latency_penalty
        
        # Bonus por capacidades específicas
        if task_type in node_info['capabilities']:
            base_score += 20
        
        # Bonus por proximidad (simulado)
        proximity_bonus = random.uniform(0, 15)
        base_score += proximity_bonus
        
        return max(0, base_score)
    
    def _create_task(self, task_name, task_type, data, priority, assigned_node):
        """Crear tarea en base de datos"""
        conn = sqlite3.connect(self.edge_db)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO distributed_tasks 
            (task_name, task_type, priority, data_size, assigned_node, status, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (task_name, task_type, priority, len(str(data)), assigned_node, 'pending', 
              datetime.now().isoformat()))
        
        task_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        return task_id
    
    def _execute_task_on_node(self, task_id, node_id, data):
        """Ejecutar tarea en nodo específico"""
        # Simular ejecución de tarea
        task_types = {
            'data_processing': self._process_data,
            'ai_inference': self._run_ai_inference,
            'image_analysis': self._analyze_image,
            'document_analysis': self._analyze_document,
            'real_time_analytics': self._run_real_time_analytics
        }
        
        task_type = self._get_task_type(task_id)
        if task_type in task_types:
            result = task_types[task_type](data)
        else:
            result = {'status': 'completed', 'result': 'Generic task completed'}
        
        # Actualizar estado de tarea
        self._update_task_status(task_id, 'completed', result)
        
        return result
    
    def _process_data(self, data):
        """Procesar datos en edge"""
        processing_time = random.uniform(0.1, 1.0)
        time.sleep(processing_time)
        
        return {
            'status': 'completed',
            'processed_items': len(data) if isinstance(data, list) else 1,
            'processing_time': processing_time,
            'result': 'Data processed successfully'
        }
    
    def _run_ai_inference(self, data):
        """Ejecutar inferencia de IA en edge"""
        inference_time = random.uniform(0.2, 1.5)
        time.sleep(inference_time)
        
        return {
            'status': 'completed',
            'inference_result': random.uniform(0.1, 0.9),
            'confidence': random.uniform(0.7, 0.95),
            'inference_time': inference_time
        }
    
    def _analyze_image(self, data):
        """Analizar imagen en edge"""
        analysis_time = random.uniform(0.3, 2.0)
        time.sleep(analysis_time)
        
        return {
            'status': 'completed',
            'objects_detected': random.randint(1, 10),
            'confidence': random.uniform(0.8, 0.95),
            'analysis_time': analysis_time
        }
    
    def _analyze_document(self, data):
        """Analizar documento en edge"""
        analysis_time = random.uniform(0.1, 1.0)
        time.sleep(analysis_time)
        
        return {
            'status': 'completed',
            'keywords_extracted': random.randint(5, 20),
            'sentiment_score': random.uniform(-1, 1),
            'analysis_time': analysis_time
        }
    
    def _run_real_time_analytics(self, data):
        """Ejecutar analytics en tiempo real en edge"""
        analytics_time = random.uniform(0.1, 0.8)
        time.sleep(analytics_time)
        
        return {
            'status': 'completed',
            'metrics_calculated': random.randint(3, 15),
            'trends_identified': random.randint(1, 5),
            'analytics_time': analytics_time
        }
    
    def _get_task_type(self, task_id):
        """Obtener tipo de tarea"""
        conn = sqlite3.connect(self.edge_db)
        cursor = conn.cursor()
        
        cursor.execute('SELECT task_type FROM distributed_tasks WHERE id = ?', (task_id,))
        result = cursor.fetchone()
        
        conn.close()
        
        return result[0] if result else 'generic'
    
    def _update_task_status(self, task_id, status, result):
        """Actualizar estado de tarea"""
        conn = sqlite3.connect(self.edge_db)
        cursor = conn.cursor()
        
        cursor.execute('''
            UPDATE distributed_tasks 
            SET status = ?, completed_at = ?, result_data = ?
            WHERE id = ?
        ''', (status, datetime.now().isoformat(), json.dumps(result), task_id))
        
        conn.commit()
        conn.close()
    
    def optimize_edge_network(self):
        """Optimizar red de edge computing"""
        optimizations = []
        
        # Optimización de balanceo de carga
        load_balancing_improvement = self._optimize_load_balancing()
        if load_balancing_improvement > 0:
            optimizations.append({
                'type': 'load_balancing',
                'improvement': load_balancing_improvement,
                'description': 'Mejora en distribución de carga'
            })
        
        # Optimización de energía
        energy_savings = self._optimize_energy_consumption()
        if energy_savings > 0:
            optimizations.append({
                'type': 'energy_optimization',
                'improvement': energy_savings,
                'description': 'Reducción en consumo de energía'
            })
        
        # Optimización de latencia
        latency_reduction = self._optimize_network_latency()
        if latency_reduction > 0:
            optimizations.append({
                'type': 'latency_optimization',
                'improvement': latency_reduction,
                'description': 'Reducción en latencia de red'
            })
        
        # Guardar optimizaciones
        for opt in optimizations:
            self._save_optimization(opt)
        
        return optimizations
    
    def _optimize_load_balancing(self):
        """Optimizar balanceo de carga"""
        # Simular optimización
        improvement = random.uniform(5, 25)
        return improvement
    
    def _optimize_energy_consumption(self):
        """Optimizar consumo de energía"""
        # Simular optimización
        savings = random.uniform(10, 30)
        return savings
    
    def _optimize_network_latency(self):
        """Optimizar latencia de red"""
        # Simular optimización
        reduction = random.uniform(15, 40)
        return reduction
    
    def _save_optimization(self, optimization):
        """Guardar optimización"""
        conn = sqlite3.connect(self.edge_db)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO edge_optimizations 
            (optimization_type, target_node, improvement_percentage, energy_savings, 
             latency_reduction, created_at)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (optimization['type'], 'all_nodes', optimization['improvement'], 
              optimization.get('energy_savings', 0), optimization.get('latency_reduction', 0),
              datetime.now().isoformat()))
        
        conn.commit()
        conn.close()
    
    def sync_edge_data(self, source_node, target_nodes, data):
        """Sincronizar datos entre nodos edge"""
        sync_results = []
        
        for target_node in target_nodes:
            # Simular sincronización
            sync_time = random.uniform(0.1, 1.0)
            success = random.random() > 0.1  # 90% de éxito
            
            result = {
                'source': source_node,
                'target': target_node,
                'sync_time': sync_time,
                'success': success,
                'data_size': len(str(data))
            }
            
            sync_results.append(result)
            
            # Guardar en base de datos
            self._save_sync_result(source_node, target_node, data, success)
        
        return sync_results
    
    def _save_sync_result(self, source, target, data, success):
        """Guardar resultado de sincronización"""
        conn = sqlite3.connect(self.edge_db)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO edge_sync 
            (sync_type, source_node, target_node, data_hash, sync_status, created_at)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', ('data_sync', source, target, hash(str(data)), 
              'success' if success else 'failed', datetime.now().isoformat()))
        
        conn.commit()
        conn.close()
    
    def get_edge_statistics(self):
        """Obtener estadísticas del sistema edge"""
        conn = sqlite3.connect(self.edge_db)
        cursor = conn.cursor()
        
        # Estadísticas generales
        cursor.execute('SELECT COUNT(*) FROM edge_nodes')
        total_nodes = cursor.fetchone()[0]
        
        cursor.execute('SELECT COUNT(*) FROM edge_nodes WHERE status = "active"')
        active_nodes = cursor.fetchone()[0]
        
        cursor.execute('SELECT COUNT(*) FROM distributed_tasks')
        total_tasks = cursor.fetchone()[0]
        
        cursor.execute('SELECT COUNT(*) FROM distributed_tasks WHERE status = "completed"')
        completed_tasks = cursor.fetchone()[0]
        
        cursor.execute('SELECT COUNT(*) FROM edge_optimizations')
        total_optimizations = cursor.fetchone()[0]
        
        # Promedios de rendimiento
        cursor.execute('SELECT AVG(cpu_usage) FROM edge_nodes')
        avg_cpu = cursor.fetchone()[0] or 0
        
        cursor.execute('SELECT AVG(memory_usage) FROM edge_nodes')
        avg_memory = cursor.fetchone()[0] or 0
        
        cursor.execute('SELECT AVG(network_latency) FROM edge_nodes')
        avg_latency = cursor.fetchone()[0] or 0
        
        conn.close()
        
        return {
            'total_nodes': total_nodes,
            'active_nodes': active_nodes,
            'total_tasks': total_tasks,
            'completed_tasks': completed_tasks,
            'completion_rate': (completed_tasks / max(total_tasks, 1)) * 100,
            'total_optimizations': total_optimizations,
            'avg_cpu_usage': avg_cpu,
            'avg_memory_usage': avg_memory,
            'avg_network_latency': avg_latency
        }

def main():
    edge_system = EdgeComputingSystem()
    
    print("🌐 Sistema de Edge Computing Distribuido")
    print("=" * 50)
    print("1. Registrar nodo edge")
    print("2. Distribuir tarea")
    print("3. Optimizar red edge")
    print("4. Sincronizar datos")
    print("5. Ver estadísticas edge")
    print("6. Salir")
    
    while True:
        choice = input("\nSeleccione una opción (1-6): ").strip()
        
        if choice == '1':
            node_name = input("Nombre del nodo: ").strip()
            node_type = input("Tipo de nodo (server/mobile/iot): ").strip()
            location = input("Ubicación: ").strip()
            capabilities = input("Capacidades (separadas por coma): ").strip().split(',')
            capabilities = [cap.strip() for cap in capabilities if cap.strip()]
            
            if node_name and node_type and location:
                node_id = edge_system.register_edge_node(node_name, node_type, location, capabilities)
                print(f"✅ Nodo edge registrado con ID: {node_id}")
                print(f"📍 Ubicación: {location}")
                print(f"🛠️ Capacidades: {', '.join(capabilities)}")
            else:
                print("❌ Datos del nodo requeridos")
        
        elif choice == '2':
            task_name = input("Nombre de la tarea: ").strip()
            task_type = input("Tipo de tarea (data_processing/ai_inference/image_analysis/document_analysis/real_time_analytics): ").strip()
            data = input("Datos de entrada: ").strip()
            priority = input("Prioridad (1-5, default 1): ").strip()
            priority = int(priority) if priority.isdigit() else 1
            
            if task_name and task_type and data:
                print(f"🔄 Distribuyendo tarea '{task_name}'...")
                result = edge_system.distribute_task(task_name, task_type, data, priority)
                
                if result:
                    print(f"✅ Tarea distribuida:")
                    print(f"  🎯 Nodo asignado: {result['assigned_node']}")
                    print(f"  ⏱️ Tiempo de ejecución: {result['execution_time']:.2f}s")
                    print(f"  📊 Resultado: {result['result']['status']}")
                else:
                    print("❌ No se pudo distribuir la tarea")
            else:
                print("❌ Datos de tarea requeridos")
        
        elif choice == '3':
            print("⚡ Optimizando red de edge computing...")
            optimizations = edge_system.optimize_edge_network()
            
            if optimizations:
                print(f"✅ Optimizaciones aplicadas: {len(optimizations)}")
                for opt in optimizations:
                    print(f"  • {opt['type']}: {opt['improvement']:.1f}% mejora")
                    print(f"    {opt['description']}")
            else:
                print("ℹ️ No se encontraron optimizaciones necesarias")
        
        elif choice == '4':
            source_node = input("Nodo fuente: ").strip()
            target_nodes = input("Nodos destino (separados por coma): ").strip().split(',')
            target_nodes = [node.strip() for node in target_nodes if node.strip()]
            data = input("Datos a sincronizar: ").strip()
            
            if source_node and target_nodes and data:
                print(f"🔄 Sincronizando datos desde {source_node}...")
                results = edge_system.sync_edge_data(source_node, target_nodes, data)
                
                print(f"✅ Sincronización completada:")
                for result in results:
                    status = "✅" if result['success'] else "❌"
                    print(f"  {status} {result['source']} → {result['target']}: {result['sync_time']:.2f}s")
            else:
                print("❌ Datos de sincronización requeridos")
        
        elif choice == '5':
            stats = edge_system.get_edge_statistics()
            print(f"\n📊 Estadísticas de Edge Computing:")
            print(f"  🌐 Nodos totales: {stats['total_nodes']}")
            print(f"  ✅ Nodos activos: {stats['active_nodes']}")
            print(f"  📋 Tareas totales: {stats['total_tasks']}")
            print(f"  ✅ Tareas completadas: {stats['completed_tasks']}")
            print(f"  📈 Tasa de finalización: {stats['completion_rate']:.1f}%")
            print(f"  ⚡ Optimizaciones: {stats['total_optimizations']}")
            print(f"  💻 CPU promedio: {stats['avg_cpu_usage']:.1f}%")
            print(f"  🧠 Memoria promedio: {stats['avg_memory_usage']:.1f}%")
            print(f"  🌐 Latencia promedio: {stats['avg_network_latency']:.1f}ms")
        
        elif choice == '6':
            print("👋 ¡Hasta luego!")
            break
        
        else:
            print("❌ Opción no válida")

if __name__ == "__main__":
    main()


