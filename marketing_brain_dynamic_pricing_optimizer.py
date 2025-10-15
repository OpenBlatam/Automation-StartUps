"""
Marketing Brain Dynamic Pricing Optimizer
Motor avanzado de optimización de pricing dinámico
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import json
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.metrics import mean_squared_error, r2_score, mean_absolute_error
from sklearn.cluster import KMeans
from sklearn.decomposition import PCA
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
from scipy.optimize import minimize
import warnings
warnings.filterwarnings('ignore')

class DynamicPricingOptimizer:
    def __init__(self):
        self.pricing_data = {}
        self.price_elasticity_models = {}
        self.demand_forecasting_models = {}
        self.competitive_pricing_analysis = {}
        self.pricing_strategies = {}
        self.optimization_results = {}
        self.pricing_insights = {}
        
    def load_pricing_data(self, pricing_data):
        """Cargar datos de pricing"""
        if isinstance(pricing_data, str):
            if pricing_data.endswith('.csv'):
                self.pricing_data = pd.read_csv(pricing_data)
            elif pricing_data.endswith('.json'):
                with open(pricing_data, 'r') as f:
                    data = json.load(f)
                self.pricing_data = pd.DataFrame(data)
        else:
            self.pricing_data = pd.DataFrame(pricing_data)
        
        print(f"✅ Datos de pricing cargados: {len(self.pricing_data)} registros")
        return True
    
    def analyze_price_elasticity(self, product_id=None):
        """Analizar elasticidad de precios"""
        if self.pricing_data.empty:
            return None
        
        # Filtrar por producto si se especifica
        if product_id:
            data = self.pricing_data[self.pricing_data['product_id'] == product_id]
        else:
            data = self.pricing_data
        
        # Análisis de elasticidad por producto
        elasticity_analysis = {}
        
        for product in data['product_id'].unique():
            product_data = data[data['product_id'] == product]
            
            # Calcular elasticidad de precio
            price_changes = product_data['price'].pct_change().dropna()
            demand_changes = product_data['demand'].pct_change().dropna()
            
            if len(price_changes) > 1 and len(demand_changes) > 1:
                # Elasticidad de precio
                price_elasticity = np.corrcoef(price_changes, demand_changes)[0, 1]
                
                # Análisis de sensibilidad
                if price_elasticity < -1:
                    sensitivity = 'Elastic'
                elif price_elasticity > -1 and price_elasticity < 0:
                    sensitivity = 'Inelastic'
                else:
                    sensitivity = 'Neutral'
                
                # Análisis de revenue optimization
                revenue_analysis = self._analyze_revenue_optimization(product_data)
                
                elasticity_analysis[product] = {
                    'price_elasticity': price_elasticity,
                    'sensitivity': sensitivity,
                    'revenue_analysis': revenue_analysis,
                    'price_range': {
                        'min': product_data['price'].min(),
                        'max': product_data['price'].max(),
                        'avg': product_data['price'].mean()
                    },
                    'demand_range': {
                        'min': product_data['demand'].min(),
                        'max': product_data['demand'].max(),
                        'avg': product_data['demand'].mean()
                    }
                }
        
        # Análisis agregado
        overall_elasticity = np.mean([analysis['price_elasticity'] for analysis in elasticity_analysis.values()])
        
        elasticity_results = {
            'product_elasticity': elasticity_analysis,
            'overall_elasticity': overall_elasticity,
            'elasticity_distribution': self._analyze_elasticity_distribution(elasticity_analysis),
            'revenue_impact': self._analyze_revenue_impact(elasticity_analysis)
        }
        
        self.price_elasticity_models = elasticity_results
        return elasticity_results
    
    def _analyze_revenue_optimization(self, product_data):
        """Analizar optimización de revenue"""
        # Calcular revenue por precio
        product_data['revenue'] = product_data['price'] * product_data['demand']
        
        # Encontrar precio óptimo
        optimal_price = product_data.loc[product_data['revenue'].idxmax(), 'price']
        max_revenue = product_data['revenue'].max()
        
        # Análisis de sensibilidad de revenue
        revenue_sensitivity = product_data['revenue'].std() / product_data['revenue'].mean()
        
        return {
            'optimal_price': optimal_price,
            'max_revenue': max_revenue,
            'revenue_sensitivity': revenue_sensitivity,
            'current_revenue': product_data['revenue'].mean()
        }
    
    def _analyze_elasticity_distribution(self, elasticity_analysis):
        """Analizar distribución de elasticidad"""
        elasticities = [analysis['price_elasticity'] for analysis in elasticity_analysis.values()]
        
        distribution = {
            'elastic_products': len([e for e in elasticities if e < -1]),
            'inelastic_products': len([e for e in elasticities if e > -1 and e < 0]),
            'neutral_products': len([e for e in elasticities if e >= 0]),
            'avg_elasticity': np.mean(elasticities),
            'elasticity_std': np.std(elasticities)
        }
        
        return distribution
    
    def _analyze_revenue_impact(self, elasticity_analysis):
        """Analizar impacto en revenue"""
        revenue_impact = {
            'total_revenue_potential': 0,
            'products_with_optimization_potential': 0,
            'avg_revenue_improvement': 0
        }
        
        improvements = []
        for product, analysis in elasticity_analysis.items():
            revenue_analysis = analysis['revenue_analysis']
            current_revenue = revenue_analysis['current_revenue']
            max_revenue = revenue_analysis['max_revenue']
            
            if max_revenue > current_revenue:
                improvement = (max_revenue - current_revenue) / current_revenue
                improvements.append(improvement)
                revenue_impact['total_revenue_potential'] += max_revenue - current_revenue
                revenue_impact['products_with_optimization_potential'] += 1
        
        if improvements:
            revenue_impact['avg_revenue_improvement'] = np.mean(improvements)
        
        return revenue_impact
    
    def build_demand_forecasting_model(self, product_id=None):
        """Construir modelo de forecasting de demanda"""
        if product_id:
            data = self.pricing_data[self.pricing_data['product_id'] == product_id]
        else:
            data = self.pricing_data
        
        # Preparar datos para forecasting
        feature_columns = ['price', 'competitor_price', 'seasonality', 'promotion', 'inventory']
        available_features = [col for col in feature_columns if col in data.columns]
        
        if not available_features:
            return None
        
        X = data[available_features]
        y = data['demand']
        
        # Dividir datos
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
        
        # Escalar datos
        scaler = StandardScaler()
        X_train_scaled = scaler.fit_transform(X_train)
        X_test_scaled = scaler.transform(X_test)
        
        # Entrenar modelo
        model = GradientBoostingRegressor(n_estimators=100, random_state=42)
        model.fit(X_train_scaled, y_train)
        
        # Evaluar modelo
        y_pred = model.predict(X_test_scaled)
        
        model_metrics = {
            'mse': mean_squared_error(y_test, y_pred),
            'rmse': np.sqrt(mean_squared_error(y_test, y_pred)),
            'mae': mean_absolute_error(y_test, y_pred),
            'r2': r2_score(y_test, y_pred),
            'feature_importance': dict(zip(available_features, model.feature_importances_))
        }
        
        # Guardar modelo
        model_key = f'demand_forecast_{product_id}' if product_id else 'demand_forecast_overall'
        self.demand_forecasting_models[model_key] = {
            'model': model,
            'feature_columns': available_features,
            'scaler': scaler,
            'metrics': model_metrics
        }
        
        return model_metrics
    
    def forecast_demand(self, product_id, price_scenarios):
        """Predecir demanda para diferentes escenarios de precio"""
        model_key = f'demand_forecast_{product_id}'
        
        if model_key not in self.demand_forecasting_models:
            raise ValueError(f"Modelo de forecasting para producto {product_id} no encontrado")
        
        model_info = self.demand_forecasting_models[model_key]
        model = model_info['model']
        feature_columns = model_info['feature_columns']
        scaler = model_info['scaler']
        
        # Preparar datos base
        base_data = self.pricing_data[self.pricing_data['product_id'] == product_id].iloc[-1]
        
        # Crear escenarios de predicción
        predictions = []
        
        for price in price_scenarios:
            # Crear fila de datos para predicción
            prediction_data = base_data[feature_columns].copy()
            prediction_data['price'] = price
            
            # Escalar datos
            prediction_data_scaled = scaler.transform([prediction_data])
            
            # Predecir demanda
            predicted_demand = model.predict(prediction_data_scaled)[0]
            
            # Calcular revenue
            predicted_revenue = price * predicted_demand
            
            predictions.append({
                'price': price,
                'predicted_demand': predicted_demand,
                'predicted_revenue': predicted_revenue,
                'price_change': (price - base_data['price']) / base_data['price'] * 100
            })
        
        return predictions
    
    def analyze_competitive_pricing(self):
        """Analizar pricing competitivo"""
        if self.pricing_data.empty:
            return None
        
        # Análisis de posicionamiento de precios
        competitive_analysis = {}
        
        for product in self.pricing_data['product_id'].unique():
            product_data = self.pricing_data[self.pricing_data['product_id'] == product]
            
            # Análisis de precios vs competencia
            if 'competitor_price' in product_data.columns:
                price_vs_competition = product_data['price'] - product_data['competitor_price']
                
                competitive_analysis[product] = {
                    'price_premium': price_vs_competition.mean(),
                    'price_premium_std': price_vs_competition.std(),
                    'competitive_position': self._determine_competitive_position(price_vs_competition),
                    'price_volatility': product_data['price'].std() / product_data['price'].mean(),
                    'competitor_price_volatility': product_data['competitor_price'].std() / product_data['competitor_price'].mean()
                }
        
        # Análisis de estrategias competitivas
        competitive_strategies = self._analyze_competitive_strategies(competitive_analysis)
        
        # Análisis de oportunidades de pricing
        pricing_opportunities = self._identify_pricing_opportunities(competitive_analysis)
        
        competitive_results = {
            'competitive_analysis': competitive_analysis,
            'competitive_strategies': competitive_strategies,
            'pricing_opportunities': pricing_opportunities,
            'market_positioning': self._analyze_market_positioning(competitive_analysis)
        }
        
        self.competitive_pricing_analysis = competitive_results
        return competitive_results
    
    def _determine_competitive_position(self, price_vs_competition):
        """Determinar posición competitiva"""
        avg_premium = price_vs_competition.mean()
        
        if avg_premium > 0.1:
            return 'Premium'
        elif avg_premium < -0.1:
            return 'Budget'
        else:
            return 'Competitive'
    
    def _analyze_competitive_strategies(self, competitive_analysis):
        """Analizar estrategias competitivas"""
        strategies = []
        
        for product, analysis in competitive_analysis.items():
            position = analysis['competitive_position']
            premium = analysis['price_premium']
            
            if position == 'Premium' and premium > 0.2:
                strategies.append({
                    'product': product,
                    'strategy': 'Premium Positioning',
                    'description': 'Mantener posición premium con valor agregado',
                    'priority': 'medium'
                })
            elif position == 'Budget' and premium < -0.2:
                strategies.append({
                    'product': product,
                    'strategy': 'Value Positioning',
                    'description': 'Enfocarse en valor y eficiencia de costos',
                    'priority': 'medium'
                })
            elif position == 'Competitive':
                strategies.append({
                    'product': product,
                    'strategy': 'Competitive Pricing',
                    'description': 'Mantener precios competitivos con diferenciación',
                    'priority': 'high'
                })
        
        return strategies
    
    def _identify_pricing_opportunities(self, competitive_analysis):
        """Identificar oportunidades de pricing"""
        opportunities = []
        
        for product, analysis in competitive_analysis.items():
            premium = analysis['price_premium']
            volatility = analysis['price_volatility']
            
            # Oportunidad de aumento de precio
            if premium < -0.1 and volatility < 0.1:
                opportunities.append({
                    'product': product,
                    'opportunity': 'Price Increase',
                    'description': 'Oportunidad para aumentar precios sin perder competitividad',
                    'potential_impact': 'medium'
                })
            
            # Oportunidad de optimización de precios
            if volatility > 0.2:
                opportunities.append({
                    'product': product,
                    'opportunity': 'Price Stabilization',
                    'description': 'Oportunidad para estabilizar precios y mejorar previsibilidad',
                    'potential_impact': 'high'
                })
        
        return opportunities
    
    def _analyze_market_positioning(self, competitive_analysis):
        """Analizar posicionamiento de mercado"""
        positioning = {
            'premium_products': 0,
            'competitive_products': 0,
            'budget_products': 0,
            'avg_price_premium': 0
        }
        
        premiums = []
        for product, analysis in competitive_analysis.items():
            position = analysis['competitive_position']
            premium = analysis['price_premium']
            
            if position == 'Premium':
                positioning['premium_products'] += 1
            elif position == 'Competitive':
                positioning['competitive_products'] += 1
            else:
                positioning['budget_products'] += 1
            
            premiums.append(premium)
        
        if premiums:
            positioning['avg_price_premium'] = np.mean(premiums)
        
        return positioning
    
    def optimize_pricing_strategy(self, product_id, optimization_goal='revenue'):
        """Optimizar estrategia de pricing"""
        if product_id not in self.pricing_data['product_id'].values:
            raise ValueError(f"Producto {product_id} no encontrado")
        
        product_data = self.pricing_data[self.pricing_data['product_id'] == product_id]
        
        # Obtener modelo de forecasting
        model_key = f'demand_forecast_{product_id}'
        if model_key not in self.demand_forecasting_models:
            # Construir modelo si no existe
            self.build_demand_forecasting_model(product_id)
        
        model_info = self.demand_forecasting_models[model_key]
        model = model_info['model']
        feature_columns = model_info['feature_columns']
        scaler = model_info['scaler']
        
        # Función objetivo
        def objective(price):
            # Preparar datos para predicción
            base_data = product_data.iloc[-1][feature_columns].copy()
            base_data['price'] = price
            
            # Escalar datos
            prediction_data_scaled = scaler.transform([base_data])
            
            # Predecir demanda
            predicted_demand = model.predict(prediction_data_scaled)[0]
            
            if optimization_goal == 'revenue':
                return -(price * predicted_demand)  # Maximizar revenue
            elif optimization_goal == 'profit':
                # Asumir costo variable
                variable_cost = price * 0.6  # 60% del precio
                profit = (price - variable_cost) * predicted_demand
                return -profit  # Maximizar profit
            else:  # demand
                return -predicted_demand  # Maximizar demanda
        
        # Restricciones
        current_price = product_data['price'].iloc[-1]
        price_bounds = (current_price * 0.5, current_price * 2.0)  # ±50% del precio actual
        
        # Optimización
        result = minimize(objective, current_price, method='L-BFGS-B', bounds=[price_bounds])
        
        # Resultados
        optimal_price = result.x[0]
        optimal_demand = -result.fun if optimization_goal == 'demand' else None
        
        # Calcular métricas
        current_demand = product_data['demand'].iloc[-1]
        current_revenue = current_price * current_demand
        
        # Predecir demanda y revenue con precio óptimo
        base_data = product_data.iloc[-1][feature_columns].copy()
        base_data['price'] = optimal_price
        prediction_data_scaled = scaler.transform([base_data])
        predicted_demand = model.predict(prediction_data_scaled)[0]
        predicted_revenue = optimal_price * predicted_demand
        
        optimization_results = {
            'product_id': product_id,
            'current_price': current_price,
            'optimal_price': optimal_price,
            'price_change': (optimal_price - current_price) / current_price * 100,
            'current_demand': current_demand,
            'predicted_demand': predicted_demand,
            'demand_change': (predicted_demand - current_demand) / current_demand * 100,
            'current_revenue': current_revenue,
            'predicted_revenue': predicted_revenue,
            'revenue_change': (predicted_revenue - current_revenue) / current_revenue * 100,
            'optimization_goal': optimization_goal,
            'optimization_status': result.success
        }
        
        return optimization_results
    
    def generate_pricing_strategies(self):
        """Generar estrategias de pricing"""
        strategies = []
        
        # Estrategias basadas en elasticidad
        if self.price_elasticity_models:
            elasticity_analysis = self.price_elasticity_models.get('product_elasticity', {})
            
            for product, analysis in elasticity_analysis.items():
                sensitivity = analysis['sensitivity']
                revenue_analysis = analysis['revenue_analysis']
                
                if sensitivity == 'Elastic':
                    strategies.append({
                        'product': product,
                        'strategy': 'Price Reduction',
                        'description': 'Reducir precios para aumentar demanda y revenue',
                        'priority': 'high',
                        'expected_impact': 'high'
                    })
                elif sensitivity == 'Inelastic':
                    strategies.append({
                        'product': product,
                        'strategy': 'Price Increase',
                        'description': 'Aumentar precios para maximizar revenue',
                        'priority': 'medium',
                        'expected_impact': 'medium'
                    })
        
        # Estrategias basadas en análisis competitivo
        if self.competitive_pricing_analysis:
            competitive_analysis = self.competitive_pricing_analysis.get('competitive_analysis', {})
            
            for product, analysis in competitive_analysis.items():
                position = analysis['competitive_position']
                premium = analysis['price_premium']
                
                if position == 'Premium' and premium > 0.2:
                    strategies.append({
                        'product': product,
                        'strategy': 'Premium Maintenance',
                        'description': 'Mantener posición premium con valor agregado',
                        'priority': 'medium',
                        'expected_impact': 'medium'
                    })
                elif position == 'Budget' and premium < -0.2:
                    strategies.append({
                        'product': product,
                        'strategy': 'Value Enhancement',
                        'description': 'Mejorar valor para justificar precios más altos',
                        'priority': 'high',
                        'expected_impact': 'high'
                    })
        
        # Estrategias basadas en optimización
        if self.optimization_results:
            for product, results in self.optimization_results.items():
                revenue_change = results.get('revenue_change', 0)
                
                if revenue_change > 10:
                    strategies.append({
                        'product': product,
                        'strategy': 'Price Optimization',
                        'description': 'Implementar precio óptimo para maximizar revenue',
                        'priority': 'high',
                        'expected_impact': 'high'
                    })
        
        self.pricing_strategies = strategies
        return strategies
    
    def generate_pricing_insights(self):
        """Generar insights de pricing"""
        insights = []
        
        # Insights de elasticidad
        if self.price_elasticity_models:
            elasticity_models = self.price_elasticity_models
            overall_elasticity = elasticity_models.get('overall_elasticity', 0)
            
            if overall_elasticity < -1:
                insights.append({
                    'category': 'Price Elasticity',
                    'insight': f'Demanda elástica general: {overall_elasticity:.2f}',
                    'recommendation': 'Considerar reducción de precios para aumentar demanda',
                    'priority': 'high'
                })
            elif overall_elasticity > -0.5:
                insights.append({
                    'category': 'Price Elasticity',
                    'insight': f'Demanda inelástica general: {overall_elasticity:.2f}',
                    'recommendation': 'Oportunidad para aumentar precios sin perder demanda',
                    'priority': 'medium'
                })
        
        # Insights de análisis competitivo
        if self.competitive_pricing_analysis:
            competitive_analysis = self.competitive_pricing_analysis
            market_positioning = competitive_analysis.get('market_positioning', {})
            
            premium_products = market_positioning.get('premium_products', 0)
            total_products = sum(market_positioning.values())
            
            if premium_products > total_products * 0.5:
                insights.append({
                    'category': 'Competitive Positioning',
                    'insight': f'{premium_products} de {total_products} productos en posición premium',
                    'recommendation': 'Mantener diferenciación y valor agregado',
                    'priority': 'medium'
                })
        
        # Insights de optimización
        if self.optimization_results:
            total_revenue_improvement = 0
            optimized_products = 0
            
            for product, results in self.optimization_results.items():
                revenue_change = results.get('revenue_change', 0)
                if revenue_change > 0:
                    total_revenue_improvement += revenue_change
                    optimized_products += 1
            
            if optimized_products > 0:
                avg_improvement = total_revenue_improvement / optimized_products
                insights.append({
                    'category': 'Price Optimization',
                    'insight': f'Optimización promedio de {avg_improvement:.1f}% en {optimized_products} productos',
                    'recommendation': 'Implementar precios optimizados para maximizar revenue',
                    'priority': 'high'
                })
        
        self.pricing_insights = insights
        return insights
    
    def create_pricing_dashboard(self):
        """Crear dashboard de optimización de pricing"""
        if not self.pricing_data.empty:
            return None
        
        # Crear subplots
        fig = make_subplots(
            rows=2, cols=2,
            subplot_titles=('Price Elasticity', 'Demand Forecasting',
                          'Competitive Analysis', 'Optimization Results'),
            specs=[[{"type": "scatter"}, {"type": "scatter"}],
                   [{"type": "bar"}, {"type": "bar"}]]
        )
        
        # Gráfico de elasticidad de precios
        if self.price_elasticity_models:
            elasticity_analysis = self.price_elasticity_models.get('product_elasticity', {})
            if elasticity_analysis:
                products = list(elasticity_analysis.keys())
                elasticities = [analysis['price_elasticity'] for analysis in elasticity_analysis.values()]
                
                fig.add_trace(
                    go.Scatter(x=products, y=elasticities, mode='markers', name='Price Elasticity'),
                    row=1, col=1
                )
        
        # Gráfico de forecasting de demanda
        if self.demand_forecasting_models:
            # Simular datos de forecasting
            prices = np.linspace(10, 100, 20)
            demands = np.random.normal(100, 20, 20)
            
            fig.add_trace(
                go.Scatter(x=prices, y=demands, mode='lines', name='Demand Forecast'),
                row=1, col=2
            )
        
        # Gráfico de análisis competitivo
        if self.competitive_pricing_analysis:
            competitive_analysis = self.competitive_pricing_analysis.get('competitive_analysis', {})
            if competitive_analysis:
                products = list(competitive_analysis.keys())
                premiums = [analysis['price_premium'] for analysis in competitive_analysis.values()]
                
                fig.add_trace(
                    go.Bar(x=products, y=premiums, name='Price Premium'),
                    row=2, col=1
                )
        
        # Gráfico de resultados de optimización
        if self.optimization_results:
            products = list(self.optimization_results.keys())
            revenue_changes = [results.get('revenue_change', 0) for results in self.optimization_results.values()]
            
            fig.add_trace(
                go.Bar(x=products, y=revenue_changes, name='Revenue Change'),
                row=2, col=2
            )
        
        fig.update_layout(
            title="Dashboard de Optimización de Pricing Dinámico",
            showlegend=False,
            height=800
        )
        
        return fig
    
    def export_pricing_analysis(self, filename='dynamic_pricing_analysis.json'):
        """Exportar análisis de pricing"""
        export_data = {
            'timestamp': datetime.now().isoformat(),
            'price_elasticity_models': self.price_elasticity_models,
            'demand_forecasting_models': {k: {'metrics': v['metrics']} for k, v in self.demand_forecasting_models.items()},
            'competitive_pricing_analysis': self.competitive_pricing_analysis,
            'pricing_strategies': self.pricing_strategies,
            'optimization_results': self.optimization_results,
            'pricing_insights': self.pricing_insights,
            'summary': {
                'total_products': len(self.pricing_data['product_id'].unique()) if 'product_id' in self.pricing_data.columns else 0,
                'analysis_date': datetime.now().isoformat()
            }
        }
        
        with open(filename, 'w') as f:
            json.dump(export_data, f, indent=2, default=str)
        
        print(f"✅ Análisis de pricing exportado a {filename}")
        return export_data

# Ejemplo de uso
if __name__ == "__main__":
    # Crear instancia del optimizador de pricing
    pricing_optimizer = DynamicPricingOptimizer()
    
    # Datos de ejemplo
    sample_data = pd.DataFrame({
        'product_id': np.random.randint(1, 20, 1000),
        'price': np.random.normal(50, 15, 1000),
        'demand': np.random.normal(100, 30, 1000),
        'competitor_price': np.random.normal(45, 12, 1000),
        'seasonality': np.random.uniform(0.8, 1.2, 1000),
        'promotion': np.random.choice([0, 1], 1000, p=[0.8, 0.2]),
        'inventory': np.random.normal(500, 100, 1000),
        'date': pd.date_range('2023-01-01', periods=1000, freq='D')
    })
    
    # Cargar datos de pricing
    print("📊 Cargando datos de pricing...")
    pricing_optimizer.load_pricing_data(sample_data)
    
    # Analizar elasticidad de precios
    print("📈 Analizando elasticidad de precios...")
    elasticity_analysis = pricing_optimizer.analyze_price_elasticity()
    
    # Construir modelo de forecasting de demanda
    print("🔮 Construyendo modelo de forecasting de demanda...")
    demand_model = pricing_optimizer.build_demand_forecasting_model()
    
    # Analizar pricing competitivo
    print("🏆 Analizando pricing competitivo...")
    competitive_analysis = pricing_optimizer.analyze_competitive_pricing()
    
    # Optimizar estrategia de pricing
    print("💰 Optimizando estrategia de pricing...")
    optimization_results = {}
    for product_id in sample_data['product_id'].unique()[:5]:  # Optimizar primeros 5 productos
        try:
            result = pricing_optimizer.optimize_pricing_strategy(product_id, 'revenue')
            optimization_results[product_id] = result
        except Exception as e:
            print(f"Error optimizando producto {product_id}: {e}")
    
    # Generar estrategias de pricing
    print("🎯 Generando estrategias de pricing...")
    pricing_strategies = pricing_optimizer.generate_pricing_strategies()
    
    # Generar insights de pricing
    print("💡 Generando insights de pricing...")
    pricing_insights = pricing_optimizer.generate_pricing_insights()
    
    # Crear dashboard
    print("📊 Creando dashboard de pricing...")
    dashboard = pricing_optimizer.create_pricing_dashboard()
    
    # Exportar análisis
    print("💾 Exportando análisis de pricing...")
    export_data = pricing_optimizer.export_pricing_analysis()
    
    print("✅ Sistema de optimización de pricing dinámico completado!")




