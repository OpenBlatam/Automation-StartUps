"""
Marketing Brain Conversion Optimization Engine
Motor avanzado de optimización de conversión y A/B testing
"""

import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier, GradientBoostingRegressor
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import scipy.stats as stats
from scipy import optimize
import json
from datetime import datetime, timedelta
import warnings
warnings.filterwarnings('ignore')

class ConversionOptimizationEngine:
    def __init__(self):
        self.experiments = {}
        self.conversion_models = {}
        self.optimization_results = {}
        self.ab_test_results = {}
        self.funnel_analysis = {}
        self.insights = {}
        
    def create_ab_test(self, test_name, variants, traffic_split=None):
        """Crear experimento A/B test"""
        if traffic_split is None:
            traffic_split = [0.5, 0.5]  # 50/50 split por defecto
        
        experiment = {
            'name': test_name,
            'variants': variants,
            'traffic_split': traffic_split,
            'start_date': datetime.now().isoformat(),
            'status': 'active',
            'results': {},
            'statistical_significance': False,
            'confidence_level': 0.95
        }
        
        self.experiments[test_name] = experiment
        return experiment
    
    def run_ab_test(self, test_name, test_data):
        """Ejecutar experimento A/B test"""
        if test_name not in self.experiments:
            raise ValueError(f"Experimento {test_name} no encontrado")
        
        experiment = self.experiments[test_name]
        
        # Simular asignación de tráfico
        np.random.seed(42)
        test_data['variant'] = np.random.choice(
            experiment['variants'],
            size=len(test_data),
            p=experiment['traffic_split']
        )
        
        # Analizar resultados por variante
        results = {}
        for variant in experiment['variants']:
            variant_data = test_data[test_data['variant'] == variant]
            
            variant_results = {
                'visitors': len(variant_data),
                'conversions': variant_data['converted'].sum(),
                'conversion_rate': variant_data['converted'].mean(),
                'revenue': variant_data['revenue'].sum() if 'revenue' in variant_data.columns else 0,
                'avg_order_value': variant_data['revenue'].mean() if 'revenue' in variant_data.columns else 0
            }
            
            results[variant] = variant_results
        
        # Calcular significancia estadística
        statistical_analysis = self._calculate_statistical_significance(results)
        
        # Actualizar experimento
        experiment['results'] = results
        experiment['statistical_analysis'] = statistical_analysis
        experiment['statistical_significance'] = statistical_analysis['is_significant']
        
        self.ab_test_results[test_name] = {
            'experiment': experiment,
            'test_data': test_data
        }
        
        return experiment
    
    def _calculate_statistical_significance(self, results):
        """Calcular significancia estadística"""
        variants = list(results.keys())
        if len(variants) < 2:
            return {'is_significant': False, 'p_value': 1.0}
        
        # Obtener datos de conversión
        conversions = [results[variant]['conversions'] for variant in variants]
        visitors = [results[variant]['visitors'] for variant in variants]
        
        # Test de chi-cuadrado
        contingency_table = np.array([conversions, [v - c for v, c in zip(visitors, conversions)]])
        chi2, p_value, dof, expected = stats.chi2_contingency(contingency_table)
        
        # Determinar significancia
        is_significant = p_value < 0.05
        
        # Calcular intervalos de confianza
        confidence_intervals = {}
        for i, variant in enumerate(variants):
            conversion_rate = conversions[i] / visitors[i]
            se = np.sqrt(conversion_rate * (1 - conversion_rate) / visitors[i])
            ci_lower = conversion_rate - 1.96 * se
            ci_upper = conversion_rate + 1.96 * se
            
            confidence_intervals[variant] = {
                'conversion_rate': conversion_rate,
                'ci_lower': ci_lower,
                'ci_upper': ci_upper
            }
        
        return {
            'is_significant': is_significant,
            'p_value': p_value,
            'chi2_statistic': chi2,
            'confidence_intervals': confidence_intervals,
            'winner': variants[np.argmax(conversions)] if is_significant else None
        }
    
    def analyze_conversion_funnel(self, funnel_data):
        """Analizar embudo de conversión"""
        funnel_stages = ['awareness', 'interest', 'consideration', 'purchase', 'retention']
        
        funnel_analysis = {}
        for stage in funnel_stages:
            if stage in funnel_data.columns:
                stage_data = funnel_data[funnel_data[stage] == 1]
                funnel_analysis[stage] = {
                    'users': len(stage_data),
                    'conversion_rate': len(stage_data) / len(funnel_data),
                    'drop_off_rate': 1 - (len(stage_data) / len(funnel_data))
                }
        
        # Calcular tasas de conversión entre etapas
        conversion_rates = {}
        for i in range(len(funnel_stages) - 1):
            current_stage = funnel_stages[i]
            next_stage = funnel_stages[i + 1]
            
            if current_stage in funnel_analysis and next_stage in funnel_analysis:
                current_users = funnel_analysis[current_stage]['users']
                next_users = funnel_analysis[next_stage]['users']
                
                if current_users > 0:
                    conversion_rates[f"{current_stage}_to_{next_stage}"] = next_users / current_users
        
        funnel_analysis['stage_conversion_rates'] = conversion_rates
        
        # Identificar cuellos de botella
        bottlenecks = []
        for stage, data in funnel_analysis.items():
            if isinstance(data, dict) and 'drop_off_rate' in data:
                if data['drop_off_rate'] > 0.7:  # Más del 70% de abandono
                    bottlenecks.append({
                        'stage': stage,
                        'drop_off_rate': data['drop_off_rate'],
                        'users_lost': int(data['drop_off_rate'] * len(funnel_data))
                    })
        
        funnel_analysis['bottlenecks'] = bottlenecks
        
        self.funnel_analysis = funnel_analysis
        return funnel_analysis
    
    def build_conversion_prediction_model(self, training_data):
        """Construir modelo de predicción de conversión"""
        # Preparar datos
        feature_columns = [col for col in training_data.columns if col not in ['converted', 'user_id']]
        X = training_data[feature_columns]
        y = training_data['converted']
        
        # Codificar variables categóricas
        label_encoders = {}
        for column in X.select_dtypes(include=['object']).columns:
            le = LabelEncoder()
            X[column] = le.fit_transform(X[column].astype(str))
            label_encoders[column] = le
        
        # Dividir datos
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
        
        # Entrenar modelo
        model = RandomForestClassifier(n_estimators=100, random_state=42)
        model.fit(X_train, y_train)
        
        # Evaluar modelo
        y_pred = model.predict(X_test)
        y_pred_proba = model.predict_proba(X_test)[:, 1]
        
        model_metrics = {
            'accuracy': accuracy_score(y_test, y_pred),
            'precision': precision_score(y_test, y_pred),
            'recall': recall_score(y_test, y_pred),
            'f1_score': f1_score(y_test, y_pred),
            'feature_importance': dict(zip(feature_columns, model.feature_importances_))
        }
        
        # Guardar modelo
        self.conversion_models['conversion_predictor'] = {
            'model': model,
            'label_encoders': label_encoders,
            'feature_columns': feature_columns,
            'metrics': model_metrics
        }
        
        return model_metrics
    
    def optimize_landing_page(self, page_data):
        """Optimizar página de aterrizaje"""
        optimization_results = {}
        
        # Análisis de elementos de la página
        page_elements = {
            'headline': page_data.get('headline', ''),
            'subheadline': page_data.get('subheadline', ''),
            'cta_button': page_data.get('cta_button', ''),
            'images': page_data.get('images', []),
            'testimonials': page_data.get('testimonials', []),
            'social_proof': page_data.get('social_proof', [])
        }
        
        # Análisis de performance por elemento
        element_analysis = {}
        for element, content in page_elements.items():
            if content:
                element_analysis[element] = {
                    'present': True,
                    'length': len(str(content)),
                    'optimization_score': self._calculate_element_score(content, element)
                }
            else:
                element_analysis[element] = {
                    'present': False,
                    'length': 0,
                    'optimization_score': 0
                }
        
        # Generar recomendaciones de optimización
        recommendations = self._generate_optimization_recommendations(element_analysis)
        
        # Calcular score general de optimización
        overall_score = np.mean([elem['optimization_score'] for elem in element_analysis.values()])
        
        optimization_results = {
            'element_analysis': element_analysis,
            'overall_score': overall_score,
            'recommendations': recommendations,
            'priority_actions': self._prioritize_actions(recommendations)
        }
        
        self.optimization_results['landing_page'] = optimization_results
        return optimization_results
    
    def _calculate_element_score(self, content, element_type):
        """Calcular score de optimización para un elemento"""
        scores = {
            'headline': self._score_headline(content),
            'subheadline': self._score_subheadline(content),
            'cta_button': self._score_cta(content),
            'images': self._score_images(content),
            'testimonials': self._score_testimonials(content),
            'social_proof': self._score_social_proof(content)
        }
        
        return scores.get(element_type, 0)
    
    def _score_headline(self, headline):
        """Score para headline"""
        if not headline:
            return 0
        
        score = 0
        headline_lower = headline.lower()
        
        # Longitud óptima (6-12 palabras)
        word_count = len(headline.split())
        if 6 <= word_count <= 12:
            score += 30
        elif 3 <= word_count <= 15:
            score += 20
        
        # Palabras de poder
        power_words = ['free', 'new', 'proven', 'guaranteed', 'exclusive', 'limited']
        if any(word in headline_lower for word in power_words):
            score += 25
        
        # Números específicos
        if any(char.isdigit() for char in headline):
            score += 20
        
        # Beneficio claro
        benefit_words = ['save', 'earn', 'get', 'achieve', 'discover']
        if any(word in headline_lower for word in benefit_words):
            score += 25
        
        return min(score, 100)
    
    def _score_subheadline(self, subheadline):
        """Score para subheadline"""
        if not subheadline:
            return 0
        
        score = 0
        subheadline_lower = subheadline.lower()
        
        # Longitud óptima (10-20 palabras)
        word_count = len(subheadline.split())
        if 10 <= word_count <= 20:
            score += 40
        
        # Explica el beneficio
        if 'because' in subheadline_lower or 'so you can' in subheadline_lower:
            score += 30
        
        # Incluye prueba social
        social_proof_words = ['customers', 'users', 'people', 'clients']
        if any(word in subheadline_lower for word in social_proof_words):
            score += 30
        
        return min(score, 100)
    
    def _score_cta(self, cta):
        """Score para call-to-action"""
        if not cta:
            return 0
        
        score = 0
        cta_lower = cta.lower()
        
        # Longitud óptima (2-5 palabras)
        word_count = len(cta.split())
        if 2 <= word_count <= 5:
            score += 40
        
        # Verbos de acción
        action_verbs = ['get', 'start', 'try', 'download', 'buy', 'join', 'learn']
        if any(verb in cta_lower for verb in action_verbs):
            score += 30
        
        # Urgencia
        urgency_words = ['now', 'today', 'limited', 'exclusive']
        if any(word in cta_lower for word in urgency_words):
            score += 30
        
        return min(score, 100)
    
    def _score_images(self, images):
        """Score para imágenes"""
        if not images:
            return 0
        
        score = 0
        
        # Cantidad de imágenes
        if 1 <= len(images) <= 3:
            score += 40
        elif len(images) > 3:
            score += 20
        
        # Tipos de imágenes (simulado)
        score += 30  # Asumir que las imágenes son relevantes
        
        return min(score, 100)
    
    def _score_testimonials(self, testimonials):
        """Score para testimonios"""
        if not testimonials:
            return 0
        
        score = 0
        
        # Cantidad de testimonios
        if 1 <= len(testimonials) <= 5:
            score += 40
        elif len(testimonials) > 5:
            score += 30
        
        # Calidad (simulado)
        score += 30
        
        return min(score, 100)
    
    def _score_social_proof(self, social_proof):
        """Score para prueba social"""
        if not social_proof:
            return 0
        
        score = 0
        
        # Elementos de prueba social
        if len(social_proof) >= 1:
            score += 50
        
        # Diversidad de elementos
        if len(social_proof) >= 3:
            score += 30
        
        return min(score, 100)
    
    def _generate_optimization_recommendations(self, element_analysis):
        """Generar recomendaciones de optimización"""
        recommendations = []
        
        for element, analysis in element_analysis.items():
            if not analysis['present']:
                recommendations.append({
                    'element': element,
                    'action': 'add',
                    'priority': 'high',
                    'description': f'Agregar {element} a la página'
                })
            elif analysis['optimization_score'] < 50:
                recommendations.append({
                    'element': element,
                    'action': 'improve',
                    'priority': 'medium',
                    'description': f'Mejorar {element} (score actual: {analysis["optimization_score"]})'
                })
            elif analysis['optimization_score'] < 80:
                recommendations.append({
                    'element': element,
                    'action': 'optimize',
                    'priority': 'low',
                    'description': f'Optimizar {element} (score actual: {analysis["optimization_score"]})'
                })
        
        return recommendations
    
    def _prioritize_actions(self, recommendations):
        """Priorizar acciones de optimización"""
        priority_order = {'high': 3, 'medium': 2, 'low': 1}
        
        sorted_recommendations = sorted(
            recommendations,
            key=lambda x: priority_order.get(x['priority'], 0),
            reverse=True
        )
        
        return sorted_recommendations
    
    def create_conversion_dashboard(self):
        """Crear dashboard de optimización de conversión"""
        if not self.ab_test_results and not self.funnel_analysis:
            return None
        
        # Crear subplots
        fig = make_subplots(
            rows=2, cols=2,
            subplot_titles=('Resultados A/B Test', 'Análisis de Embudo',
                          'Optimización de Página', 'Métricas de Conversión'),
            specs=[[{"type": "bar"}, {"type": "bar"}],
                   [{"type": "pie"}, {"type": "scatter"}]]
        )
        
        # Gráfico de A/B test
        if self.ab_test_results:
            for test_name, test_data in self.ab_test_results.items():
                results = test_data['experiment']['results']
                variants = list(results.keys())
                conversion_rates = [results[variant]['conversion_rate'] for variant in variants]
                
                fig.add_trace(
                    go.Bar(x=variants, y=conversion_rates, name=f'{test_name} - Conversion Rate'),
                    row=1, col=1
                )
        
        # Gráfico de embudo
        if self.funnel_analysis:
            stages = list(self.funnel_analysis.keys())
            conversion_rates = [self.funnel_analysis[stage]['conversion_rate'] for stage in stages if isinstance(self.funnel_analysis[stage], dict) and 'conversion_rate' in self.funnel_analysis[stage]]
            
            if conversion_rates:
                fig.add_trace(
                    go.Bar(x=stages[:len(conversion_rates)], y=conversion_rates, name='Funnel Conversion Rates'),
                    row=1, col=2
                )
        
        # Gráfico de optimización
        if self.optimization_results:
            for optimization_name, optimization_data in self.optimization_results.items():
                element_analysis = optimization_data['element_analysis']
                elements = list(element_analysis.keys())
                scores = [element_analysis[element]['optimization_score'] for element in elements]
                
                fig.add_trace(
                    go.Pie(labels=elements, values=scores, name=f'{optimization_name} - Optimization Scores'),
                    row=2, col=1
                )
        
        # Gráfico de métricas
        if self.conversion_models:
            for model_name, model_data in self.conversion_models.items():
                metrics = model_data['metrics']
                metric_names = ['accuracy', 'precision', 'recall', 'f1_score']
                metric_values = [metrics[metric] for metric in metric_names]
                
                fig.add_trace(
                    go.Scatter(x=metric_names, y=metric_values, mode='markers+lines', name=f'{model_name} - Model Metrics'),
                    row=2, col=2
                )
        
        fig.update_layout(
            title="Dashboard de Optimización de Conversión",
            showlegend=False,
            height=800
        )
        
        return fig
    
    def export_optimization_data(self, filename='conversion_optimization_data.json'):
        """Exportar datos de optimización"""
        export_data = {
            'timestamp': datetime.now().isoformat(),
            'ab_test_results': self.ab_test_results,
            'funnel_analysis': self.funnel_analysis,
            'optimization_results': self.optimization_results,
            'conversion_models': {name: {'metrics': data['metrics']} for name, data in self.conversion_models.items()},
            'summary': {
                'total_experiments': len(self.experiments),
                'active_experiments': len([exp for exp in self.experiments.values() if exp['status'] == 'active']),
                'total_optimizations': len(self.optimization_results)
            }
        }
        
        with open(filename, 'w') as f:
            json.dump(export_data, f, indent=2, default=str)
        
        print(f"✅ Datos de optimización exportados a {filename}")
        return export_data

# Ejemplo de uso
if __name__ == "__main__":
    # Crear instancia del motor de optimización
    conversion_optimizer = ConversionOptimizationEngine()
    
    # Crear A/B test
    print("🧪 Creando A/B test...")
    ab_test = conversion_optimizer.create_ab_test(
        'Landing Page Test',
        ['Control', 'Variant A'],
        [0.5, 0.5]
    )
    
    # Datos de ejemplo para A/B test
    test_data = pd.DataFrame({
        'user_id': range(1000),
        'converted': np.random.choice([0, 1], 1000, p=[0.85, 0.15]),
        'revenue': np.random.normal(50, 20, 1000)
    })
    
    # Ejecutar A/B test
    print("📊 Ejecutando A/B test...")
    test_results = conversion_optimizer.run_ab_test('Landing Page Test', test_data)
    
    # Analizar embudo de conversión
    print("🔄 Analizando embudo de conversión...")
    funnel_data = pd.DataFrame({
        'awareness': np.random.choice([0, 1], 1000, p=[0.3, 0.7]),
        'interest': np.random.choice([0, 1], 1000, p=[0.5, 0.5]),
        'consideration': np.random.choice([0, 1], 1000, p=[0.7, 0.3]),
        'purchase': np.random.choice([0, 1], 1000, p=[0.9, 0.1]),
        'retention': np.random.choice([0, 1], 1000, p=[0.8, 0.2])
    })
    
    funnel_analysis = conversion_optimizer.analyze_conversion_funnel(funnel_data)
    
    # Optimizar página de aterrizaje
    print("🎯 Optimizando página de aterrizaje...")
    page_data = {
        'headline': 'Get Started Today - Free Trial',
        'subheadline': 'Join thousands of satisfied customers who have transformed their business',
        'cta_button': 'Start Free Trial',
        'images': ['hero_image.jpg', 'product_screenshot.png'],
        'testimonials': ['Great product!', 'Amazing results!'],
        'social_proof': ['10,000+ users', '4.9/5 rating']
    }
    
    optimization_results = conversion_optimizer.optimize_landing_page(page_data)
    
    # Crear dashboard
    print("📈 Creando dashboard de optimización...")
    dashboard = conversion_optimizer.create_conversion_dashboard()
    
    # Exportar datos
    print("💾 Exportando datos de optimización...")
    export_data = conversion_optimizer.export_optimization_data()
    
    print("✅ Sistema de optimización de conversión completado!")






