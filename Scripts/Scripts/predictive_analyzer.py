#!/usr/bin/env python3
"""
Analizador Predictivo Avanzado
Sistema que predice y optimiza la organización futura del proyecto
"""

import os
import re
import json
import hashlib
import math
from pathlib import Path
from datetime import datetime, timedelta
from collections import defaultdict, Counter
import difflib

class PredictiveAnalyzer:
    def __init__(self, project_root):
        self.project_root = Path(project_root)
        self.prediction_models = defaultdict(dict)
        self.future_scenarios = []
        self.optimization_predictions = []
        self.growth_patterns = {}
        self.trend_analysis = {}
        
    def analyze_historical_patterns(self):
        """Analiza patrones históricos de organización"""
        print("📈 Analizando patrones históricos...")
        
        # Analizar crecimiento por categoría
        category_growth = defaultdict(list)
        
        for category_dir in self.project_root.iterdir():
            if category_dir.is_dir() and category_dir.name.startswith(('01_', '02_', '03_', '04_', '05_', '06_', '07_', '08_', '09_', '10_')):
                files = list(category_dir.rglob("*"))
                file_count = len([f for f in files if f.is_file()])
                category_growth[category_dir.name].append(file_count)
        
        # Calcular tasas de crecimiento
        for category, counts in category_growth.items():
            if len(counts) > 1:
                growth_rate = (counts[-1] - counts[0]) / len(counts)
                self.growth_patterns[category] = {
                    'current_count': counts[-1],
                    'growth_rate': growth_rate,
                    'historical_data': counts
                }
        
        print(f"  ✅ Patrones históricos analizados para {len(self.growth_patterns)} categorías")
    
    def create_prediction_models(self):
        """Crea modelos de predicción para organización futura"""
        print("🔮 Creando modelos de predicción...")
        
        # Modelo de crecimiento exponencial
        for category, data in self.growth_patterns.items():
            current_count = data['current_count']
            growth_rate = data['growth_rate']
            
            # Predicciones a 30, 60, 90 días
            predictions = {}
            for days in [30, 60, 90]:
                predicted_count = current_count * (1 + growth_rate * days / 30)
                predictions[f"{days}_days"] = max(0, int(predicted_count))
            
            self.prediction_models[category] = {
                'current': current_count,
                'growth_rate': growth_rate,
                'predictions': predictions,
                'confidence': min(0.95, abs(growth_rate) * 10 + 0.5)
            }
        
        print(f"  ✅ {len(self.prediction_models)} modelos de predicción creados")
    
    def generate_future_scenarios(self):
        """Genera escenarios futuros de organización"""
        print("🌅 Generando escenarios futuros...")
        
        scenarios = [
            {
                'name': 'Crecimiento Conservador',
                'growth_multiplier': 1.2,
                'probability': 0.3,
                'description': 'Crecimiento moderado y estable'
            },
            {
                'name': 'Crecimiento Acelerado',
                'growth_multiplier': 2.0,
                'probability': 0.4,
                'description': 'Crecimiento rápido y expansión'
            },
            {
                'name': 'Crecimiento Exponencial',
                'growth_multiplier': 3.5,
                'probability': 0.2,
                'description': 'Crecimiento explosivo y transformación'
            },
            {
                'name': 'Crecimiento Estable',
                'growth_multiplier': 1.0,
                'probability': 0.1,
                'description': 'Mantenimiento del estado actual'
            }
        ]
        
        for scenario in scenarios:
            scenario_data = {
                'name': scenario['name'],
                'probability': scenario['probability'],
                'description': scenario['description'],
                'predictions': {}
            }
            
            for category, model in self.prediction_models.items():
                current = model['current']
                growth_rate = model['growth_rate']
                multiplier = scenario['growth_multiplier']
                
                # Predicción ajustada por escenario
                adjusted_growth = growth_rate * multiplier
                predicted_90_days = current * (1 + adjusted_growth * 3)
                
                scenario_data['predictions'][category] = {
                    'current': current,
                    'predicted_90_days': max(0, int(predicted_90_days)),
                    'growth_change': predicted_90_days - current
                }
            
            self.future_scenarios.append(scenario_data)
        
        print(f"  ✅ {len(self.future_scenarios)} escenarios futuros generados")
    
    def predict_optimization_needs(self):
        """Predice necesidades de optimización futuras"""
        print("🎯 Prediciendo necesidades de optimización...")
        
        for scenario in self.future_scenarios:
            scenario_name = scenario['name']
            predictions = scenario['predictions']
            
            optimization_needs = []
            
            for category, data in predictions.items():
                current = data['current']
                predicted = data['predicted_90_days']
                growth_change = data['growth_change']
                
                if growth_change > 50:  # Umbral de optimización
                    optimization_needs.append({
                        'category': category,
                        'current_files': current,
                        'predicted_files': predicted,
                        'growth_change': growth_change,
                        'optimization_type': 'Subcategorización Intensiva',
                        'priority': 'Alta' if growth_change > 100 else 'Media'
                    })
                elif growth_change > 20:
                    optimization_needs.append({
                        'category': category,
                        'current_files': current,
                        'predicted_files': predicted,
                        'growth_change': growth_change,
                        'optimization_type': 'Reorganización Moderada',
                        'priority': 'Media'
                    })
            
            self.optimization_predictions.append({
                'scenario': scenario_name,
                'probability': scenario['probability'],
                'optimization_needs': optimization_needs
            })
        
        print(f"  ✅ Necesidades de optimización predichas para {len(self.optimization_predictions)} escenarios")
    
    def analyze_trends(self):
        """Analiza tendencias de organización"""
        print("📊 Analizando tendencias organizacionales...")
        
        # Tendencias por tipo de archivo
        file_type_trends = defaultdict(int)
        content_trends = defaultdict(int)
        
        for file_path in self.project_root.rglob("*"):
            if file_path.is_file():
                # Tendencias por extensión
                extension = file_path.suffix.lower()
                file_type_trends[extension] += 1
                
                # Tendencias por contenido (para archivos de texto)
                if extension == '.md':
                    try:
                        with open(file_path, 'r', encoding='utf-8') as f:
                            content = f.read()[:500].lower()
                            
                        # Palabras clave de tendencia
                        trend_keywords = ['ai', 'artificial intelligence', 'machine learning', 'automation', 'digital', 'cloud', 'data', 'analytics']
                        for keyword in trend_keywords:
                            if keyword in content:
                                content_trends[keyword] += 1
                    except:
                        continue
        
        self.trend_analysis = {
            'file_type_trends': dict(file_type_trends),
            'content_trends': dict(content_trends),
            'analysis_date': datetime.now().isoformat()
        }
        
        print(f"  ✅ Tendencias analizadas: {len(file_type_trends)} tipos de archivo, {len(content_trends)} tendencias de contenido")
    
    def create_predictive_recommendations(self):
        """Crea recomendaciones predictivas"""
        print("💡 Creando recomendaciones predictivas...")
        
        recommendations = []
        
        # Recomendaciones basadas en predicciones de crecimiento
        for prediction in self.optimization_predictions:
            scenario_name = prediction['scenario']
            probability = prediction['probability']
            
            for need in prediction['optimization_needs']:
                if need['priority'] == 'Alta':
                    recommendations.append({
                        'type': 'Preparación Proactiva',
                        'category': need['category'],
                        'action': f"Preparar subcategorías para {need['predicted_files']} archivos",
                        'scenario': scenario_name,
                        'probability': probability,
                        'urgency': 'Inmediata',
                        'description': f"La categoría {need['category']} crecerá {need['growth_change']} archivos en 90 días"
                    })
        
        # Recomendaciones basadas en tendencias
        top_content_trends = sorted(self.trend_analysis['content_trends'].items(), key=lambda x: x[1], reverse=True)[:5]
        
        for trend, count in top_content_trends:
            recommendations.append({
                'type': 'Tendencia Emergente',
                'category': 'Nueva Categoría Sugerida',
                'action': f"Crear categoría especializada para '{trend}'",
                'scenario': 'Tendencia Actual',
                'probability': 0.8,
                'urgency': 'Media',
                'description': f"Tendencia '{trend}' aparece en {count} archivos"
            })
        
        # Recomendaciones de optimización estructural
        recommendations.extend([
            {
                'type': 'Optimización Estructural',
                'category': 'Sistema General',
                'action': 'Implementar sistema de versionado automático',
                'scenario': 'Todos',
                'probability': 0.9,
                'urgency': 'Alta',
                'description': 'Preparar para manejo de versiones múltiples'
            },
            {
                'type': 'Optimización Estructural',
                'category': 'Sistema General',
                'action': 'Crear sistema de metadatos avanzado',
                'scenario': 'Todos',
                'probability': 0.85,
                'urgency': 'Media',
                'description': 'Mejorar búsqueda y navegación'
            }
        ])
        
        return recommendations
    
    def create_predictive_report(self):
        """Crea reporte predictivo completo"""
        print("📊 Creando reporte predictivo...")
        
        report_path = self.project_root / "97_Analysis_Reports" / "Predictive_Analysis_Report.md"
        
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write("# 🔮 Reporte de Análisis Predictivo\n\n")
            f.write(f"Generado el: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            
            # Resumen ejecutivo
            f.write("## 📋 Resumen Ejecutivo\n\n")
            f.write(f"- **Modelos de predicción creados**: {len(self.prediction_models)}\n")
            f.write(f"- **Escenarios futuros generados**: {len(self.future_scenarios)}\n")
            f.write(f"- **Necesidades de optimización predichas**: {sum(len(p['optimization_needs']) for p in self.optimization_predictions)}\n")
            f.write(f"- **Tendencias identificadas**: {len(self.trend_analysis['content_trends'])}\n\n")
            
            # Modelos de predicción
            f.write("## 📈 Modelos de Predicción por Categoría\n\n")
            for category, model in self.prediction_models.items():
                f.write(f"### {category}\n")
                f.write(f"- **Archivos actuales**: {model['current']}\n")
                f.write(f"- **Tasa de crecimiento**: {model['growth_rate']:.3f}\n")
                f.write(f"- **Confianza del modelo**: {model['confidence']:.1%}\n")
                f.write(f"- **Predicción 30 días**: {model['predictions']['30_days']}\n")
                f.write(f"- **Predicción 60 días**: {model['predictions']['60_days']}\n")
                f.write(f"- **Predicción 90 días**: {model['predictions']['90_days']}\n\n")
            
            # Escenarios futuros
            f.write("## 🌅 Escenarios Futuros\n\n")
            for scenario in self.future_scenarios:
                f.write(f"### {scenario['name']} (Probabilidad: {scenario['probability']:.1%})\n")
                f.write(f"{scenario['description']}\n\n")
                
                f.write("**Predicciones por categoría:**\n")
                for category, data in scenario['predictions'].items():
                    f.write(f"- **{category}**: {data['current']} → {data['predicted_90_days']} (+{data['growth_change']})\n")
                f.write("\n")
            
            # Necesidades de optimización
            f.write("## 🎯 Necesidades de Optimización Predichas\n\n")
            for prediction in self.optimization_predictions:
                f.write(f"### Escenario: {prediction['scenario']}\n")
                if prediction['optimization_needs']:
                    for need in prediction['optimization_needs']:
                        f.write(f"- **{need['category']}**: {need['optimization_type']} (Prioridad: {need['priority']})\n")
                        f.write(f"  - Archivos actuales: {need['current_files']}\n")
                        f.write(f"  - Archivos predichos: {need['predicted_files']}\n")
                        f.write(f"  - Cambio: +{need['growth_change']}\n")
                else:
                    f.write("- No se requieren optimizaciones significativas\n")
                f.write("\n")
            
            # Análisis de tendencias
            f.write("## 📊 Análisis de Tendencias\n\n")
            f.write("### Tendencias por Tipo de Archivo\n")
            for file_type, count in sorted(self.trend_analysis['file_type_trends'].items(), key=lambda x: x[1], reverse=True)[:10]:
                f.write(f"- **{file_type or 'Sin extensión'}**: {count} archivos\n")
            
            f.write("\n### Tendencias de Contenido\n")
            for trend, count in sorted(self.trend_analysis['content_trends'].items(), key=lambda x: x[1], reverse=True):
                f.write(f"- **{trend}**: {count} menciones\n")
            
            f.write("\n")
            
            # Recomendaciones
            f.write("## 💡 Recomendaciones Predictivas\n\n")
            recommendations = self.create_predictive_recommendations()
            for i, rec in enumerate(recommendations, 1):
                f.write(f"{i}. **{rec['action']}**\n")
                f.write(f"   - Tipo: {rec['type']}\n")
                f.write(f"   - Categoría: {rec['category']}\n")
                f.write(f"   - Escenario: {rec['scenario']}\n")
                f.write(f"   - Probabilidad: {rec['probability']:.1%}\n")
                f.write(f"   - Urgencia: {rec['urgency']}\n")
                f.write(f"   - Descripción: {rec['description']}\n\n")
    
    def create_predictive_dashboard(self):
        """Crea dashboard predictivo"""
        print("📊 Creando dashboard predictivo...")
        
        dashboard_path = self.project_root / "97_Analysis_Reports" / "Predictive_Dashboard.json"
        
        dashboard_data = {
            'timestamp': datetime.now().isoformat(),
            'prediction_models': dict(self.prediction_models),
            'future_scenarios': self.future_scenarios,
            'optimization_predictions': self.optimization_predictions,
            'trend_analysis': self.trend_analysis,
            'recommendations': self.create_predictive_recommendations()
        }
        
        with open(dashboard_path, 'w', encoding='utf-8') as f:
            json.dump(dashboard_data, f, indent=2, ensure_ascii=False)
        
        print(f"  💾 Dashboard predictivo guardado en: {dashboard_path}")
    
    def run_predictive_analysis(self):
        """Ejecuta análisis predictivo completo"""
        print("🚀 Iniciando análisis predictivo avanzado...")
        
        self.analyze_historical_patterns()
        self.create_prediction_models()
        self.generate_future_scenarios()
        self.predict_optimization_needs()
        self.analyze_trends()
        self.create_predictive_report()
        self.create_predictive_dashboard()
        
        print(f"\n✅ Análisis predictivo completado!")
        print(f"Modelos de predicción: {len(self.prediction_models)}")
        print(f"Escenarios futuros: {len(self.future_scenarios)}")
        print(f"Necesidades de optimización: {sum(len(p['optimization_needs']) for p in self.optimization_predictions)}")
        
        return {
            'prediction_models': len(self.prediction_models),
            'future_scenarios': len(self.future_scenarios),
            'optimization_needs': sum(len(p['optimization_needs']) for p in self.optimization_predictions),
            'trends_identified': len(self.trend_analysis['content_trends'])
        }

if __name__ == "__main__":
    analyzer = PredictiveAnalyzer("/Users/adan/frontier")
    results = analyzer.run_predictive_analysis()
    
    print(f"\n📋 RESUMEN DE ANÁLISIS PREDICTIVO:")
    print(f"Modelos de predicción: {results['prediction_models']}")
    print(f"Escenarios futuros: {results['future_scenarios']}")
    print(f"Necesidades de optimización: {results['optimization_needs']}")
    print(f"Tendencias identificadas: {results['trends_identified']}")
