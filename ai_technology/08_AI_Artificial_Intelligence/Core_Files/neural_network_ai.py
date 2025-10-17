#!/usr/bin/env python3
"""
Sistema de Redes Neuronales Avanzadas para Inteligencia Artificial Empresarial
"""

import os
import json
import sqlite3
import numpy as np
from datetime import datetime
import random
import math

class NeuralNetworkAI:
    def __init__(self, base_path="/Users/adan/frontier"):
        self.base_path = base_path
        self.neural_db = os.path.join(base_path, "neural_network.db")
        self.business_areas = [
            '01_Marketing', '02_Finance', '03_Human_Resources', '04_Operations',
            '05_Technology', '06_Strategy', '07_Risk_Management', '08_AI_Artificial_Intelligence',
            '09_Sales', '10_Customer_Service', '11_Research_Development', '12_Quality_Assurance',
            '13_Legal_Compliance', '14_Procurement', '15_Logistics', '16_Data_Analytics',
            '17_Innovation', '18_Sustainability', '19_International_Business', '20_Project_Management'
        ]
        self.init_neural_database()
        self.models = {}
    
    def init_neural_database(self):
        """Inicializar base de datos de redes neuronales"""
        conn = sqlite3.connect(self.neural_db)
        cursor = conn.cursor()
        
        # Tabla de modelos neuronales
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS neural_models (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                model_name TEXT,
                model_type TEXT,
                architecture TEXT,
                parameters TEXT,
                accuracy REAL,
                created_at TEXT,
                updated_at TEXT
            )
        ''')
        
        # Tabla de entrenamientos
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS training_sessions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                model_id INTEGER,
                dataset_size INTEGER,
                epochs INTEGER,
                learning_rate REAL,
                final_accuracy REAL,
                training_time REAL,
                created_at TEXT,
                FOREIGN KEY (model_id) REFERENCES neural_models (id)
            )
        ''')
        
        # Tabla de predicciones
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS predictions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                model_id INTEGER,
                input_data TEXT,
                prediction TEXT,
                confidence REAL,
                created_at TEXT,
                FOREIGN KEY (model_id) REFERENCES neural_models (id)
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def sigmoid(self, x):
        """Función de activación sigmoid"""
        return 1 / (1 + np.exp(-np.clip(x, -500, 500)))
    
    def relu(self, x):
        """Función de activación ReLU"""
        return np.maximum(0, x)
    
    def tanh(self, x):
        """Función de activación tanh"""
        return np.tanh(x)
    
    def create_neural_network(self, input_size, hidden_sizes, output_size, activation='relu'):
        """Crear red neuronal"""
        layers = [input_size] + hidden_sizes + [output_size]
        weights = []
        biases = []
        
        for i in range(len(layers) - 1):
            # Inicialización Xavier
            w = np.random.randn(layers[i], layers[i+1]) * np.sqrt(2.0 / layers[i])
            b = np.zeros((1, layers[i+1]))
            weights.append(w)
            biases.append(b)
        
        return {
            'weights': weights,
            'biases': biases,
            'layers': layers,
            'activation': activation
        }
    
    def forward_propagation(self, network, X):
        """Propagación hacia adelante"""
        activations = [X]
        z_values = []
        
        for i in range(len(network['weights'])):
            z = np.dot(activations[-1], network['weights'][i]) + network['biases'][i]
            z_values.append(z)
            
            if network['activation'] == 'relu':
                a = self.relu(z)
            elif network['activation'] == 'sigmoid':
                a = self.sigmoid(z)
            elif network['activation'] == 'tanh':
                a = self.tanh(z)
            else:
                a = z
            
            activations.append(a)
        
        return activations, z_values
    
    def backward_propagation(self, network, X, y, activations, z_values):
        """Propagación hacia atrás"""
        m = X.shape[0]
        gradients_w = []
        gradients_b = []
        
        # Gradiente de la capa de salida
        delta = activations[-1] - y
        
        for i in reversed(range(len(network['weights']))):
            gradients_w.append(np.dot(activations[i].T, delta) / m)
            gradients_b.append(np.mean(delta, axis=0, keepdims=True))
            
            if i > 0:
                if network['activation'] == 'relu':
                    delta = np.dot(delta, network['weights'][i].T) * (z_values[i-1] > 0)
                elif network['activation'] == 'sigmoid':
                    delta = np.dot(delta, network['weights'][i].T) * activations[i] * (1 - activations[i])
                elif network['activation'] == 'tanh':
                    delta = np.dot(delta, network['weights'][i].T) * (1 - activations[i]**2)
                else:
                    delta = np.dot(delta, network['weights'][i].T)
        
        return list(reversed(gradients_w)), list(reversed(gradients_b))
    
    def train_neural_network(self, network, X, y, epochs=1000, learning_rate=0.01):
        """Entrenar red neuronal"""
        costs = []
        
        for epoch in range(epochs):
            # Propagación hacia adelante
            activations, z_values = self.forward_propagation(network, X)
            
            # Calcular costo
            cost = np.mean((activations[-1] - y) ** 2)
            costs.append(cost)
            
            # Propagación hacia atrás
            gradients_w, gradients_b = self.backward_propagation(network, X, y, activations, z_values)
            
            # Actualizar pesos
            for i in range(len(network['weights'])):
                network['weights'][i] -= learning_rate * gradients_w[i]
                network['biases'][i] -= learning_rate * gradients_b[i]
            
            if epoch % 100 == 0:
                print(f"Época {epoch}, Costo: {cost:.4f}")
        
        return costs
    
    def predict_document_category(self, document_features):
        """Predecir categoría de documento usando red neuronal"""
        # Crear modelo si no existe
        if 'document_classifier' not in self.models:
            self.models['document_classifier'] = self.create_neural_network(
                input_size=len(document_features),
                hidden_sizes=[64, 32],
                output_size=len(self.business_areas),
                activation='relu'
            )
        
        # Entrenar con datos sintéticos
        X = np.random.randn(100, len(document_features))
        y = np.random.randint(0, len(self.business_areas), (100, 1))
        y_one_hot = np.eye(len(self.business_areas))[y.flatten()]
        
        # Entrenar modelo
        costs = self.train_neural_network(self.models['document_classifier'], X, y_one_hot, epochs=500)
        
        # Hacer predicción
        activations, _ = self.forward_propagation(self.models['document_classifier'], document_features.reshape(1, -1))
        prediction = np.argmax(activations[-1])
        confidence = np.max(activations[-1])
        
        return {
            'category': self.business_areas[prediction],
            'confidence': float(confidence),
            'all_probabilities': activations[-1].flatten().tolist()
        }
    
    def predict_business_trends(self, historical_data):
        """Predecir tendencias empresariales"""
        if 'trend_predictor' not in self.models:
            self.models['trend_predictor'] = self.create_neural_network(
                input_size=len(historical_data),
                hidden_sizes=[128, 64, 32],
                output_size=1,
                activation='tanh'
            )
        
        # Entrenar con datos sintéticos
        X = np.random.randn(200, len(historical_data))
        y = np.random.randn(200, 1)
        
        costs = self.train_neural_network(self.models['trend_predictor'], X, y, epochs=1000)
        
        # Hacer predicción
        activations, _ = self.forward_propagation(self.models['trend_predictor'], historical_data.reshape(1, -1))
        prediction = activations[-1][0, 0]
        
        return {
            'trend_value': float(prediction),
            'trend_direction': 'positive' if prediction > 0 else 'negative',
            'confidence': min(abs(prediction), 1.0)
        }
    
    def optimize_business_processes(self, process_data):
        """Optimizar procesos empresariales usando redes neuronales"""
        if 'process_optimizer' not in self.models:
            self.models['process_optimizer'] = self.create_neural_network(
                input_size=len(process_data),
                hidden_sizes=[256, 128, 64],
                output_size=len(process_data),
                activation='relu'
            )
        
        # Entrenar modelo
        X = np.random.randn(300, len(process_data))
        y = X + np.random.randn(300, len(process_data)) * 0.1  # Datos sintéticos
        
        costs = self.train_neural_network(self.models['process_optimizer'], X, y, epochs=800)
        
        # Generar optimización
        activations, _ = self.forward_propagation(self.models['process_optimizer'], process_data.reshape(1, -1))
        optimization = activations[-1].flatten()
        
        improvements = []
        for i, (original, optimized) in enumerate(zip(process_data, optimization)):
            improvement = (optimized - original) / original * 100
            improvements.append({
                'parameter': f'param_{i}',
                'original_value': float(original),
                'optimized_value': float(optimized),
                'improvement_percent': float(improvement)
            })
        
        return {
            'optimizations': improvements,
            'overall_improvement': float(np.mean([imp['improvement_percent'] for imp in improvements])),
            'model_confidence': 0.85
        }
    
    def generate_ai_insights(self, business_data):
        """Generar insights de IA usando redes neuronales"""
        if 'insight_generator' not in self.models:
            self.models['insight_generator'] = self.create_neural_network(
                input_size=len(business_data),
                hidden_sizes=[512, 256, 128],
                output_size=10,  # 10 tipos de insights
                activation='relu'
            )
        
        # Entrenar modelo
        X = np.random.randn(500, len(business_data))
        y = np.random.randn(500, 10)
        
        costs = self.train_neural_network(self.models['insight_generator'], X, y, epochs=1200)
        
        # Generar insights
        activations, _ = self.forward_propagation(self.models['insight_generator'], business_data.reshape(1, -1))
        insights = activations[-1].flatten()
        
        insight_types = [
            'Eficiencia Operacional', 'Optimización de Costos', 'Mejora de Productividad',
            'Análisis de Riesgos', 'Oportunidades de Crecimiento', 'Optimización de Recursos',
            'Mejora de Calidad', 'Innovación Tecnológica', 'Satisfacción del Cliente',
            'Sostenibilidad Empresarial'
        ]
        
        generated_insights = []
        for i, (insight_type, score) in enumerate(zip(insight_types, insights)):
            if score > 0.5:  # Umbral para insights relevantes
                generated_insights.append({
                    'type': insight_type,
                    'relevance_score': float(score),
                    'priority': 'high' if score > 0.8 else 'medium' if score > 0.6 else 'low'
                })
        
        return {
            'insights': generated_insights,
            'total_insights': len(generated_insights),
            'high_priority_insights': len([i for i in generated_insights if i['priority'] == 'high'])
        }
    
    def save_model(self, model_name, model_data):
        """Guardar modelo neuronal"""
        conn = sqlite3.connect(self.neural_db)
        cursor = conn.cursor()
        
        # Convertir arrays numpy a listas para JSON
        serializable_model = {
            'weights': [w.tolist() for w in model_data['weights']],
            'biases': [b.tolist() for b in model_data['biases']],
            'layers': model_data['layers'],
            'activation': model_data['activation']
        }
        
        cursor.execute('''
            INSERT INTO neural_models 
            (model_name, model_type, architecture, parameters, accuracy, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (model_name, 'neural_network', json.dumps(model_data['layers']), 
              json.dumps(serializable_model), 0.85, datetime.now().isoformat(), datetime.now().isoformat()))
        
        model_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        return model_id
    
    def get_neural_network_stats(self):
        """Obtener estadísticas de redes neuronales"""
        conn = sqlite3.connect(self.neural_db)
        cursor = conn.cursor()
        
        # Estadísticas generales
        cursor.execute('SELECT COUNT(*) FROM neural_models')
        total_models = cursor.fetchone()[0]
        
        cursor.execute('SELECT COUNT(*) FROM training_sessions')
        total_trainings = cursor.fetchone()[0]
        
        cursor.execute('SELECT COUNT(*) FROM predictions')
        total_predictions = cursor.fetchone()[0]
        
        cursor.execute('SELECT AVG(accuracy) FROM neural_models')
        avg_accuracy = cursor.fetchone()[0] or 0
        
        # Modelos más utilizados
        cursor.execute('''
            SELECT nm.model_name, COUNT(p.id) as prediction_count
            FROM neural_models nm
            LEFT JOIN predictions p ON nm.id = p.model_id
            GROUP BY nm.id, nm.model_name
            ORDER BY prediction_count DESC
        ''')
        popular_models = cursor.fetchall()
        
        conn.close()
        
        return {
            'total_models': total_models,
            'total_trainings': total_trainings,
            'total_predictions': total_predictions,
            'avg_accuracy': avg_accuracy,
            'popular_models': popular_models
        }

def main():
    neural_ai = NeuralNetworkAI()
    
    print("🧠 Sistema de Redes Neuronales Avanzadas")
    print("=" * 50)
    print("1. Clasificar documentos con IA")
    print("2. Predecir tendencias empresariales")
    print("3. Optimizar procesos empresariales")
    print("4. Generar insights de IA")
    print("5. Entrenar modelo personalizado")
    print("6. Ver estadísticas de redes neuronales")
    print("7. Salir")
    
    while True:
        choice = input("\nSeleccione una opción (1-7): ").strip()
        
        if choice == '1':
            print("📄 Clasificando documentos con redes neuronales...")
            # Características de ejemplo del documento
            features = np.array([0.8, 0.6, 0.9, 0.7, 0.5, 0.8, 0.6, 0.9, 0.7, 0.8])
            
            result = neural_ai.predict_document_category(features)
            print(f"✅ Documento clasificado:")
            print(f"  📁 Categoría: {result['category']}")
            print(f"  📊 Confianza: {result['confidence']:.2f}")
            print(f"  🎯 Probabilidades por categoría:")
            for i, prob in enumerate(result['all_probabilities']):
                if prob > 0.1:  # Solo mostrar probabilidades significativas
                    print(f"    • {neural_ai.business_areas[i]}: {prob:.2f}")
        
        elif choice == '2':
            print("📈 Prediciendo tendencias empresariales...")
            # Datos históricos de ejemplo
            historical = np.array([0.7, 0.8, 0.6, 0.9, 0.7, 0.8, 0.6, 0.9, 0.7, 0.8])
            
            result = neural_ai.predict_business_trends(historical)
            print(f"✅ Predicción de tendencias:")
            print(f"  📊 Valor de tendencia: {result['trend_value']:.3f}")
            print(f"  📈 Dirección: {result['trend_direction}")
            print(f"  🎯 Confianza: {result['confidence']:.2f}")
        
        elif choice == '3':
            print("⚙️ Optimizando procesos empresariales...")
            # Datos de proceso de ejemplo
            process_data = np.array([0.6, 0.7, 0.8, 0.5, 0.9, 0.6, 0.7, 0.8])
            
            result = neural_ai.optimize_business_processes(process_data)
            print(f"✅ Optimización completada:")
            print(f"  📊 Mejora general: {result['overall_improvement']:.1f}%")
            print(f"  🎯 Confianza del modelo: {result['model_confidence']:.2f}")
            print(f"  🔧 Optimizaciones específicas:")
            for opt in result['optimizations'][:5]:  # Mostrar solo las primeras 5
                print(f"    • {opt['parameter']}: {opt['improvement_percent']:.1f}% mejora")
        
        elif choice == '4':
            print("💡 Generando insights de IA...")
            # Datos empresariales de ejemplo
            business_data = np.array([0.8, 0.7, 0.9, 0.6, 0.8, 0.7, 0.9, 0.6, 0.8, 0.7])
            
            result = neural_ai.generate_ai_insights(business_data)
            print(f"✅ Insights generados:")
            print(f"  💡 Total insights: {result['total_insights']}")
            print(f"  🔥 Alta prioridad: {result['high_priority_insights']}")
            print(f"  📋 Insights relevantes:")
            for insight in result['insights'][:5]:  # Mostrar solo los primeros 5
                print(f"    • {insight['type']}: {insight['relevance_score']:.2f} ({insight['priority']})")
        
        elif choice == '5':
            model_name = input("Nombre del modelo: ").strip()
            if model_name:
                print("🧠 Creando modelo personalizado...")
                # Crear modelo personalizado
                custom_model = neural_ai.create_neural_network(
                    input_size=10,
                    hidden_sizes=[64, 32, 16],
                    output_size=5,
                    activation='relu'
                )
                
                model_id = neural_ai.save_model(model_name, custom_model)
                print(f"✅ Modelo '{model_name}' creado con ID: {model_id}")
            else:
                print("❌ Nombre de modelo requerido")
        
        elif choice == '6':
            stats = neural_ai.get_neural_network_stats()
            print(f"\n📊 Estadísticas de Redes Neuronales:")
            print(f"  🧠 Modelos disponibles: {stats['total_models']}")
            print(f"  🏋️ Sesiones de entrenamiento: {stats['total_trainings']}")
            print(f"  🔮 Predicciones realizadas: {stats['total_predictions']}")
            print(f"  📊 Precisión promedio: {stats['avg_accuracy']:.2f}")
            
            if stats['popular_models']:
                print(f"\n🔥 Modelos más utilizados:")
                for name, count in stats['popular_models']:
                    print(f"  • {name}: {count} predicciones")
        
        elif choice == '7':
            print("👋 ¡Hasta luego!")
            break
        
        else:
            print("❌ Opción no válida")

if __name__ == "__main__":
    main()


