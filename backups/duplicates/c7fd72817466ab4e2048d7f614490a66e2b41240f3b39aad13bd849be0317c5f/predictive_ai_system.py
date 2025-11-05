#!/usr/bin/env python3
"""
Sistema de Inteligencia Artificial Predictiva para Análisis Empresarial
"""

import os
import json
import sqlite3
import numpy as np
from datetime import datetime, timedelta
import random
import math

class PredictiveAISystem:
    def __init__(self, base_path="/Users/adan/frontier"):
        self.base_path = base_path
        self.predictive_db = os.path.join(base_path, "predictive_ai.db")
        self.business_areas = [
            '01_Marketing', '02_Finance', '03_Human_Resources', '04_Operations',
            '05_Technology', '06_Strategy', '07_Risk_Management', '08_AI_Artificial_Intelligence',
            '09_Sales', '10_Customer_Service', '11_Research_Development', '12_Quality_Assurance',
            '13_Legal_Compliance', '14_Procurement', '15_Logistics', '16_Data_Analytics',
            '17_Innovation', '18_Sustainability', '19_International_Business', '20_Project_Management'
        ]
        self.init_predictive_database()
        self.models = {}
    
    def init_predictive_database(self):
        """Inicializar base de datos predictiva"""
        conn = sqlite3.connect(self.predictive_db)
        cursor = conn.cursor()
        
        # Tabla de modelos predictivos
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS predictive_models (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                model_name TEXT,
                model_type TEXT,
                target_variable TEXT,
                features TEXT,
                accuracy REAL,
                created_at TEXT,
                last_trained TEXT
            )
        ''')
        
        # Tabla de predicciones
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS predictions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                model_id INTEGER,
                input_data TEXT,
                prediction_value REAL,
                confidence REAL,
                prediction_date TEXT,
                actual_value REAL,
                accuracy REAL,
                FOREIGN KEY (model_id) REFERENCES predictive_models (id)
            )
        ''')
        
        # Tabla de tendencias
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS trends (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                trend_name TEXT,
                trend_type TEXT,
                current_value REAL,
                predicted_value REAL,
                trend_direction TEXT,
                confidence REAL,
                time_horizon TEXT,
                created_at TEXT
            )
        ''')
        
        # Tabla de alertas predictivas
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS predictive_alerts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                alert_type TEXT,
                alert_message TEXT,
                severity TEXT,
                predicted_date TEXT,
                confidence REAL,
                is_active BOOLEAN DEFAULT TRUE,
                created_at TEXT
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def create_time_series_model(self, data, model_name):
        """Crear modelo de series temporales"""
        # Simular modelo ARIMA simplificado
        n = len(data)
        if n < 3:
            return None
        
        # Calcular tendencia
        x = np.arange(n)
        trend = np.polyfit(x, data, 1)[0]
        
        # Calcular estacionalidad (simplificado)
        seasonal_pattern = np.sin(2 * np.pi * x / 12) * 0.1  # Patrón anual
        
        # Calcular ruido
        noise = np.random.normal(0, 0.05, n)
        
        # Crear modelo
        model = {
            'trend': trend,
            'seasonal_amplitude': 0.1,
            'noise_std': 0.05,
            'data_length': n,
            'last_value': data[-1],
            'created_at': datetime.now().isoformat()
        }
        
        # Guardar modelo
        conn = sqlite3.connect(self.predictive_db)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO predictive_models 
            (model_name, model_type, target_variable, features, accuracy, created_at, last_trained)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (model_name, 'time_series', 'value', json.dumps(['time', 'trend', 'seasonal']), 
              0.85, datetime.now().isoformat(), datetime.now().isoformat()))
        
        model_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        self.models[model_name] = model
        return model_id
    
    def predict_future_values(self, model_name, periods=12):
        """Predecir valores futuros"""
        if model_name not in self.models:
            return None
        
        model = self.models[model_name]
        predictions = []
        
        for i in range(periods):
            # Calcular valor predicho
            time_index = model['data_length'] + i
            trend_value = model['trend'] * time_index
            seasonal_value = model['seasonal_amplitude'] * np.sin(2 * np.pi * time_index / 12)
            noise_value = np.random.normal(0, model['noise_std'])
            
            predicted_value = model['last_value'] + trend_value + seasonal_value + noise_value
            predictions.append({
                'period': i + 1,
                'value': predicted_value,
                'confidence': max(0.5, 1.0 - (i * 0.05))  # Confianza decreciente
            })
        
        return predictions
    
    def analyze_business_trends(self, business_metrics):
        """Analizar tendencias empresariales"""
        trends = []
        
        for metric_name, values in business_metrics.items():
            if len(values) < 2:
                continue
            
            # Calcular tendencia
            x = np.arange(len(values))
            slope = np.polyfit(x, values, 1)[0]
            
            # Determinar dirección de tendencia
            if slope > 0.1:
                direction = 'increasing'
                severity = 'high' if slope > 0.5 else 'medium'
            elif slope < -0.1:
                direction = 'decreasing'
                severity = 'high' if slope < -0.5 else 'medium'
            else:
                direction = 'stable'
                severity = 'low'
            
            # Calcular confianza
            confidence = min(0.95, max(0.5, abs(slope) * 2))
            
            trend = {
                'metric': metric_name,
                'direction': direction,
                'severity': severity,
                'slope': slope,
                'confidence': confidence,
                'current_value': values[-1],
                'change_percent': ((values[-1] - values[0]) / values[0]) * 100 if values[0] != 0 else 0
            }
            
            trends.append(trend)
            
            # Guardar tendencia
            conn = sqlite3.connect(self.predictive_db)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO trends 
                (trend_name, trend_type, current_value, predicted_value, trend_direction, 
                 confidence, time_horizon, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (metric_name, 'business_metric', values[-1], values[-1] + slope, 
                  direction, confidence, '3_months', datetime.now().isoformat()))
            
            conn.commit()
            conn.close()
        
        return trends
    
    def predict_risk_factors(self, business_data):
        """Predecir factores de riesgo"""
        risk_factors = []
        
        # Análisis de riesgo financiero
        if 'revenue' in business_data and 'expenses' in business_data:
            profit_margin = (business_data['revenue'] - business_data['expenses']) / business_data['revenue']
            if profit_margin < 0.1:
                risk_factors.append({
                    'type': 'financial',
                    'description': 'Margen de beneficio bajo',
                    'severity': 'high',
                    'probability': 0.8,
                    'impact': 'high'
                })
        
        # Análisis de riesgo operacional
        if 'employee_count' in business_data and 'productivity' in business_data:
            if business_data['productivity'] < 0.7:
                risk_factors.append({
                    'type': 'operational',
                    'description': 'Productividad baja detectada',
                    'severity': 'medium',
                    'probability': 0.6,
                    'impact': 'medium'
                })
        
        # Análisis de riesgo de mercado
        if 'market_share' in business_data:
            if business_data['market_share'] < 0.05:
                risk_factors.append({
                    'type': 'market',
                    'description': 'Cuota de mercado baja',
                    'severity': 'high',
                    'probability': 0.7,
                    'impact': 'high'
                })
        
        # Análisis de riesgo tecnológico
        if 'tech_investment' in business_data and 'revenue' in business_data:
            tech_ratio = business_data['tech_investment'] / business_data['revenue']
            if tech_ratio < 0.05:
                risk_factors.append({
                    'type': 'technology',
                    'description': 'Inversión tecnológica insuficiente',
                    'severity': 'medium',
                    'probability': 0.5,
                    'impact': 'medium'
                })
        
        return risk_factors
    
    def generate_predictive_insights(self, historical_data):
        """Generar insights predictivos"""
        insights = []
        
        # Insight de crecimiento
        if 'revenue' in historical_data and len(historical_data['revenue']) > 1:
            revenue_growth = (historical_data['revenue'][-1] - historical_data['revenue'][0]) / historical_data['revenue'][0]
            if revenue_growth > 0.2:
                insights.append({
                    'type': 'growth',
                    'title': 'Crecimiento Sólido Detectado',
                    'description': f'El crecimiento de ingresos es del {revenue_growth:.1%}',
                    'confidence': 0.9,
                    'recommendation': 'Mantener estrategia actual y considerar expansión'
                })
        
        # Insight de eficiencia
        if 'efficiency' in historical_data:
            avg_efficiency = np.mean(historical_data['efficiency'])
            if avg_efficiency > 0.8:
                insights.append({
                    'type': 'efficiency',
                    'title': 'Alta Eficiencia Operacional',
                    'description': f'Eficiencia promedio del {avg_efficiency:.1%}',
                    'confidence': 0.85,
                    'recommendation': 'Optimizar procesos para mantener ventaja competitiva'
                })
        
        # Insight de tendencias
        if 'customer_satisfaction' in historical_data:
            satisfaction_trend = np.polyfit(range(len(historical_data['customer_satisfaction'])), 
                                          historical_data['customer_satisfaction'], 1)[0]
            if satisfaction_trend > 0.05:
                insights.append({
                    'type': 'customer',
                    'title': 'Satisfacción del Cliente en Aumento',
                    'description': 'Tendencia positiva en satisfacción del cliente',
                    'confidence': 0.8,
                    'recommendation': 'Capitalizar en la satisfacción del cliente para crecimiento'
                })
        
        return insights
    
    def create_predictive_alerts(self, predictions, thresholds):
        """Crear alertas predictivas"""
        alerts = []
        
        for prediction in predictions:
            metric = prediction['metric']
            predicted_value = prediction['predicted_value']
            threshold = thresholds.get(metric, {})
            
            # Alerta por umbral alto
            if 'high_threshold' in threshold and predicted_value > threshold['high_threshold']:
                alerts.append({
                    'type': 'high_value',
                    'metric': metric,
                    'message': f'{metric} predicho a superar umbral alto: {predicted_value:.2f}',
                    'severity': 'warning',
                    'predicted_date': prediction['date'],
                    'confidence': prediction['confidence']
                })
            
            # Alerta por umbral bajo
            if 'low_threshold' in threshold and predicted_value < threshold['low_threshold']:
                alerts.append({
                    'type': 'low_value',
                    'metric': metric,
                    'message': f'{metric} predicho a caer por debajo del umbral: {predicted_value:.2f}',
                    'severity': 'critical',
                    'predicted_date': prediction['date'],
                    'confidence': prediction['confidence']
                })
        
        # Guardar alertas
        conn = sqlite3.connect(self.predictive_db)
        cursor = conn.cursor()
        
        for alert in alerts:
            cursor.execute('''
                INSERT INTO predictive_alerts 
                (alert_type, alert_message, severity, predicted_date, confidence, created_at)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (alert['type'], alert['message'], alert['severity'], 
                  alert['predicted_date'], alert['confidence'], datetime.now().isoformat()))
        
        conn.commit()
        conn.close()
        
        return alerts
    
    def optimize_business_strategy(self, current_metrics, goals):
        """Optimizar estrategia empresarial"""
        recommendations = []
        
        # Análisis de brechas
        for goal_name, target_value in goals.items():
            if goal_name in current_metrics:
                current_value = current_metrics[goal_name]
                gap = target_value - current_value
                gap_percent = (gap / target_value) * 100 if target_value != 0 else 0
                
                if gap_percent > 20:
                    recommendations.append({
                        'goal': goal_name,
                        'current': current_value,
                        'target': target_value,
                        'gap': gap,
                        'gap_percent': gap_percent,
                        'priority': 'high',
                        'action': f'Implementar estrategia agresiva para {goal_name}'
                    })
                elif gap_percent > 10:
                    recommendations.append({
                        'goal': goal_name,
                        'current': current_value,
                        'target': target_value,
                        'gap': gap,
                        'gap_percent': gap_percent,
                        'priority': 'medium',
                        'action': f'Optimizar procesos para {goal_name}'
                    })
        
        # Recomendaciones estratégicas
        if 'revenue' in current_metrics and 'market_share' in current_metrics:
            if current_metrics['market_share'] < 0.1:
                recommendations.append({
                    'type': 'strategic',
                    'title': 'Expansión de Mercado',
                    'description': 'Oportunidad de crecimiento en cuota de mercado',
                    'priority': 'high',
                    'action': 'Desarrollar estrategia de penetración de mercado'
                })
        
        return recommendations
    
    def get_predictive_statistics(self):
        """Obtener estadísticas del sistema predictivo"""
        conn = sqlite3.connect(self.predictive_db)
        cursor = conn.cursor()
        
        # Estadísticas generales
        cursor.execute('SELECT COUNT(*) FROM predictive_models')
        total_models = cursor.fetchone()[0]
        
        cursor.execute('SELECT COUNT(*) FROM predictions')
        total_predictions = cursor.fetchone()[0]
        
        cursor.execute('SELECT COUNT(*) FROM trends')
        total_trends = cursor.fetchone()[0]
        
        cursor.execute('SELECT COUNT(*) FROM predictive_alerts WHERE is_active = TRUE')
        active_alerts = cursor.fetchone()[0]
        
        # Precisión promedio
        cursor.execute('SELECT AVG(accuracy) FROM predictions WHERE accuracy IS NOT NULL')
        avg_accuracy = cursor.fetchone()[0] or 0
        
        # Modelos más precisos
        cursor.execute('''
            SELECT pm.model_name, AVG(p.accuracy) as avg_accuracy
            FROM predictive_models pm
            LEFT JOIN predictions p ON pm.id = p.model_id
            GROUP BY pm.id, pm.model_name
            ORDER BY avg_accuracy DESC
        ''')
        best_models = cursor.fetchall()
        
        conn.close()
        
        return {
            'total_models': total_models,
            'total_predictions': total_predictions,
            'total_trends': total_trends,
            'active_alerts': active_alerts,
            'avg_accuracy': avg_accuracy,
            'best_models': best_models
        }

def main():
    predictive_ai = PredictiveAISystem()
    
    print("🔮 Sistema de Inteligencia Artificial Predictiva")
    print("=" * 50)
    print("1. Crear modelo de series temporales")
    print("2. Predecir valores futuros")
    print("3. Analizar tendencias empresariales")
    print("4. Predecir factores de riesgo")
    print("5. Generar insights predictivos")
    print("6. Crear alertas predictivas")
    print("7. Optimizar estrategia empresarial")
    print("8. Ver estadísticas predictivas")
    print("9. Salir")
    
    while True:
        choice = input("\nSeleccione una opción (1-9): ").strip()
        
        if choice == '1':
            model_name = input("Nombre del modelo: ").strip()
            if model_name:
                # Datos de ejemplo
                data = [100, 105, 110, 108, 115, 120, 118, 125, 130, 128, 135, 140]
                model_id = predictive_ai.create_time_series_model(data, model_name)
                print(f"✅ Modelo de series temporales creado con ID: {model_id}")
                print(f"📊 Datos de entrenamiento: {len(data)} puntos")
            else:
                print("❌ Nombre de modelo requerido")
        
        elif choice == '2':
            model_name = input("Nombre del modelo: ").strip()
            periods = input("Períodos a predecir (default 12): ").strip()
            periods = int(periods) if periods.isdigit() else 12
            
            if model_name:
                predictions = predictive_ai.predict_future_values(model_name, periods)
                if predictions:
                    print(f"✅ Predicciones generadas para {periods} períodos:")
                    for pred in predictions[:5]:  # Mostrar solo las primeras 5
                        print(f"  • Período {pred['period']}: {pred['value']:.2f} (confianza: {pred['confidence']:.2f})")
                else:
                    print("❌ Modelo no encontrado")
            else:
                print("❌ Nombre de modelo requerido")
        
        elif choice == '3':
            print("📈 Analizando tendencias empresariales...")
            business_metrics = {
                'revenue': [100000, 105000, 110000, 108000, 115000, 120000],
                'customers': [500, 520, 540, 535, 550, 570],
                'satisfaction': [0.8, 0.82, 0.85, 0.83, 0.87, 0.89],
                'efficiency': [0.75, 0.78, 0.80, 0.79, 0.82, 0.85]
            }
            
            trends = predictive_ai.analyze_business_trends(business_metrics)
            print(f"✅ Tendencias analizadas: {len(trends)}")
            for trend in trends:
                print(f"  • {trend['metric']}: {trend['direction']} ({trend['severity']}) - {trend['change_percent']:.1f}%")
        
        elif choice == '4':
            print("⚠️ Analizando factores de riesgo...")
            business_data = {
                'revenue': 1000000,
                'expenses': 950000,
                'employee_count': 50,
                'productivity': 0.75,
                'market_share': 0.03,
                'tech_investment': 20000
            }
            
            risks = predictive_ai.predict_risk_factors(business_data)
            print(f"✅ Factores de riesgo identificados: {len(risks)}")
            for risk in risks:
                print(f"  • {risk['type'].upper()}: {risk['description']} ({risk['severity']})")
        
        elif choice == '5':
            print("💡 Generando insights predictivos...")
            historical_data = {
                'revenue': [100000, 105000, 110000, 108000, 115000, 120000],
                'efficiency': [0.75, 0.78, 0.80, 0.79, 0.82, 0.85],
                'customer_satisfaction': [0.8, 0.82, 0.85, 0.83, 0.87, 0.89]
            }
            
            insights = predictive_ai.generate_predictive_insights(historical_data)
            print(f"✅ Insights generados: {len(insights)}")
            for insight in insights:
                print(f"  • {insight['title']}: {insight['description']}")
                print(f"    Recomendación: {insight['recommendation']}")
        
        elif choice == '6':
            print("🚨 Creando alertas predictivas...")
            predictions = [
                {'metric': 'revenue', 'predicted_value': 150000, 'date': '2024-03-01', 'confidence': 0.85},
                {'metric': 'customers', 'predicted_value': 450, 'date': '2024-03-01', 'confidence': 0.78}
            ]
            thresholds = {
                'revenue': {'high_threshold': 200000, 'low_threshold': 80000},
                'customers': {'high_threshold': 600, 'low_threshold': 400}
            }
            
            alerts = predictive_ai.create_predictive_alerts(predictions, thresholds)
            print(f"✅ Alertas creadas: {len(alerts)}")
            for alert in alerts:
                print(f"  • {alert['severity'].upper()}: {alert['message']}")
        
        elif choice == '7':
            print("🎯 Optimizando estrategia empresarial...")
            current_metrics = {
                'revenue': 1000000,
                'market_share': 0.08,
                'customer_satisfaction': 0.85,
                'efficiency': 0.80
            }
            goals = {
                'revenue': 1500000,
                'market_share': 0.15,
                'customer_satisfaction': 0.90,
                'efficiency': 0.85
            }
            
            recommendations = predictive_ai.optimize_business_strategy(current_metrics, goals)
            print(f"✅ Recomendaciones generadas: {len(recommendations)}")
            for rec in recommendations:
                if 'goal' in rec:
                    print(f"  • {rec['goal']}: {rec['gap_percent']:.1f}% brecha ({rec['priority']})")
                else:
                    print(f"  • {rec['title']}: {rec['description']}")
        
        elif choice == '8':
            stats = predictive_ai.get_predictive_statistics()
            print(f"\n📊 Estadísticas Predictivas:")
            print(f"  🧠 Modelos: {stats['total_models']}")
            print(f"  🔮 Predicciones: {stats['total_predictions']}")
            print(f"  📈 Tendencias: {stats['total_trends']}")
            print(f"  🚨 Alertas activas: {stats['active_alerts']}")
            print(f"  📊 Precisión promedio: {stats['avg_accuracy']:.2f}")
            
            if stats['best_models']:
                print(f"\n🏆 Mejores modelos:")
                for name, accuracy in stats['best_models'][:3]:
                    print(f"  • {name}: {accuracy:.2f}")
        
        elif choice == '9':
            print("👋 ¡Hasta luego!")
            break
        
        else:
            print("❌ Opción no válida")

if __name__ == "__main__":
    main()


