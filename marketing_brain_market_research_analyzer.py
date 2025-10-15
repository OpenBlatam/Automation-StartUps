"""
Marketing Brain Market Research Analyzer
Sistema avanzado de análisis de market research
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import json
from sklearn.ensemble import RandomForestClassifier, GradientBoostingRegressor
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score
from sklearn.cluster import KMeans
from sklearn.decomposition import PCA
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import warnings
warnings.filterwarnings('ignore')

class MarketResearchAnalyzer:
    def __init__(self):
        self.research_data = {}
        self.market_analysis = {}
        self.competitor_analysis = {}
        self.customer_insights = {}
        self.market_opportunities = {}
        self.research_models = {}
        self.research_insights = {}
        
    def load_research_data(self, research_data):
        """Cargar datos de market research"""
        if isinstance(research_data, str):
            if research_data.endswith('.csv'):
                self.research_data = pd.read_csv(research_data)
            elif research_data.endswith('.json'):
                with open(research_data, 'r') as f:
                    data = json.load(f)
                self.research_data = pd.DataFrame(data)
        else:
            self.research_data = pd.DataFrame(research_data)
        
        print(f"✅ Datos de market research cargados: {len(self.research_data)} registros")
        return True
    
    def analyze_market_size(self):
        """Analizar tamaño del mercado"""
        if self.research_data.empty:
            return None
        
        # Análisis de tamaño de mercado por segmento
        market_size_analysis = {}
        
        if 'market_segment' in self.research_data.columns:
            segment_analysis = self.research_data.groupby('market_segment').agg({
                'market_size': 'sum',
                'growth_rate': 'mean',
                'competition_level': 'mean',
                'customer_count': 'sum'
            }).reset_index()
            
            # Calcular métricas adicionales
            segment_analysis['market_share_potential'] = segment_analysis['market_size'] / segment_analysis['market_size'].sum() * 100
            segment_analysis['growth_potential'] = segment_analysis['growth_rate'] * segment_analysis['market_size']
            
            market_size_analysis['segment_analysis'] = segment_analysis.to_dict('records')
        
        # Análisis de tendencias de mercado
        trend_analysis = self._analyze_market_trends()
        
        # Análisis de estacionalidad
        seasonality_analysis = self._analyze_market_seasonality()
        
        # Análisis de geografía
        geography_analysis = self._analyze_market_geography()
        
        market_results = {
            'market_size_analysis': market_size_analysis,
            'trend_analysis': trend_analysis,
            'seasonality_analysis': seasonality_analysis,
            'geography_analysis': geography_analysis,
            'total_market_size': self.research_data['market_size'].sum() if 'market_size' in self.research_data.columns else 0,
            'avg_growth_rate': self.research_data['growth_rate'].mean() if 'growth_rate' in self.research_data.columns else 0
        }
        
        self.market_analysis = market_results
        return market_results
    
    def _analyze_market_trends(self):
        """Analizar tendencias de mercado"""
        trend_analysis = {}
        
        if 'date' in self.research_data.columns:
            # Análisis de tendencias temporales
            self.research_data['date'] = pd.to_datetime(self.research_data['date'])
            self.research_data['year'] = self.research_data['date'].dt.year
            self.research_data['month'] = self.research_data['date'].dt.month
            
            # Tendencias anuales
            yearly_trends = self.research_data.groupby('year').agg({
                'market_size': 'sum',
                'growth_rate': 'mean',
                'customer_count': 'sum'
            }).reset_index()
            
            # Calcular crecimiento año a año
            yearly_trends['market_growth'] = yearly_trends['market_size'].pct_change() * 100
            yearly_trends['customer_growth'] = yearly_trends['customer_count'].pct_change() * 100
            
            trend_analysis['yearly_trends'] = yearly_trends.to_dict('records')
            
            # Tendencias mensuales
            monthly_trends = self.research_data.groupby('month').agg({
                'market_size': 'mean',
                'growth_rate': 'mean'
            }).reset_index()
            
            trend_analysis['monthly_trends'] = monthly_trends.to_dict('records')
        
        # Análisis de tendencias por categoría
        if 'category' in self.research_data.columns:
            category_trends = self.research_data.groupby('category').agg({
                'market_size': 'sum',
                'growth_rate': 'mean',
                'competition_level': 'mean'
            }).reset_index()
            
            trend_analysis['category_trends'] = category_trends.to_dict('records')
        
        return trend_analysis
    
    def _analyze_market_seasonality(self):
        """Analizar estacionalidad del mercado"""
        seasonality_analysis = {}
        
        if 'date' in self.research_data.columns:
            # Análisis de estacionalidad por mes
            monthly_seasonality = self.research_data.groupby('month').agg({
                'market_size': 'mean',
                'growth_rate': 'mean',
                'customer_count': 'mean'
            }).reset_index()
            
            # Calcular coeficiente de variación estacional
            seasonal_variance = monthly_seasonality['market_size'].std() / monthly_seasonality['market_size'].mean()
            
            seasonality_analysis['monthly_seasonality'] = monthly_seasonality.to_dict('records')
            seasonality_analysis['seasonal_variance'] = seasonal_variance
            seasonality_analysis['seasonality_strength'] = 'high' if seasonal_variance > 0.3 else 'medium' if seasonal_variance > 0.1 else 'low'
        
        return seasonality_analysis
    
    def _analyze_market_geography(self):
        """Analizar geografía del mercado"""
        geography_analysis = {}
        
        if 'region' in self.research_data.columns:
            # Análisis por región
            regional_analysis = self.research_data.groupby('region').agg({
                'market_size': 'sum',
                'growth_rate': 'mean',
                'customer_count': 'sum',
                'competition_level': 'mean'
            }).reset_index()
            
            # Calcular densidad de mercado
            regional_analysis['market_density'] = regional_analysis['market_size'] / regional_analysis['customer_count']
            regional_analysis['market_share'] = regional_analysis['market_size'] / regional_analysis['market_size'].sum() * 100
            
            geography_analysis['regional_analysis'] = regional_analysis.to_dict('records')
            
            # Identificar regiones de alto potencial
            high_potential_regions = regional_analysis[
                (regional_analysis['growth_rate'] > regional_analysis['growth_rate'].mean()) &
                (regional_analysis['competition_level'] < regional_analysis['competition_level'].mean())
            ]
            
            geography_analysis['high_potential_regions'] = high_potential_regions.to_dict('records')
        
        return geography_analysis
    
    def analyze_competitors(self):
        """Analizar competidores"""
        if self.research_data.empty:
            return None
        
        # Análisis de competidores por segmento
        competitor_analysis = {}
        
        if 'competitor_name' in self.research_data.columns:
            # Análisis de competidores
            competitor_data = self.research_data.groupby('competitor_name').agg({
                'market_share': 'mean',
                'revenue': 'sum',
                'customer_count': 'sum',
                'growth_rate': 'mean',
                'price': 'mean'
            }).reset_index()
            
            # Calcular métricas adicionales
            competitor_data['revenue_per_customer'] = competitor_data['revenue'] / competitor_data['customer_count']
            competitor_data['market_position'] = competitor_data['market_share'].rank(ascending=False)
            
            competitor_analysis['competitor_data'] = competitor_data.to_dict('records')
            
            # Análisis de posicionamiento
            positioning_analysis = self._analyze_competitor_positioning(competitor_data)
            competitor_analysis['positioning_analysis'] = positioning_analysis
            
            # Análisis de gaps de mercado
            market_gaps = self._identify_market_gaps(competitor_data)
            competitor_analysis['market_gaps'] = market_gaps
        
        # Análisis de competencia por categoría
        if 'category' in self.research_data.columns:
            category_competition = self.research_data.groupby('category').agg({
                'competition_level': 'mean',
                'market_share': 'sum',
                'competitor_count': 'mean'
            }).reset_index()
            
            competitor_analysis['category_competition'] = category_competition.to_dict('records')
        
        self.competitor_analysis = competitor_analysis
        return competitor_analysis
    
    def _analyze_competitor_positioning(self, competitor_data):
        """Analizar posicionamiento de competidores"""
        positioning_analysis = {}
        
        # Análisis de posicionamiento por precio
        price_positioning = competitor_data.nlargest(3, 'price')
        positioning_analysis['premium_competitors'] = price_positioning.to_dict('records')
        
        # Análisis de posicionamiento por market share
        share_positioning = competitor_data.nlargest(3, 'market_share')
        positioning_analysis['market_leaders'] = share_positioning.to_dict('records')
        
        # Análisis de posicionamiento por crecimiento
        growth_positioning = competitor_data.nlargest(3, 'growth_rate')
        positioning_analysis['fastest_growing'] = growth_positioning.to_dict('records')
        
        return positioning_analysis
    
    def _identify_market_gaps(self, competitor_data):
        """Identificar gaps de mercado"""
        market_gaps = []
        
        # Gap de precio
        price_range = competitor_data['price'].max() - competitor_data['price'].min()
        if price_range > competitor_data['price'].mean() * 0.5:
            market_gaps.append({
                'gap_type': 'Price Gap',
                'description': 'Oportunidad en rango de precios',
                'opportunity_level': 'medium'
            })
        
        # Gap de market share
        total_share = competitor_data['market_share'].sum()
        if total_share < 80:  # Menos del 80% del mercado cubierto
            market_gaps.append({
                'gap_type': 'Market Share Gap',
                'description': 'Oportunidad para capturar market share',
                'opportunity_level': 'high'
            })
        
        # Gap de crecimiento
        avg_growth = competitor_data['growth_rate'].mean()
        if avg_growth < 5:  # Crecimiento bajo
            market_gaps.append({
                'gap_type': 'Growth Gap',
                'description': 'Oportunidad para innovación y crecimiento',
                'opportunity_level': 'high'
            })
        
        return market_gaps
    
    def analyze_customer_insights(self):
        """Analizar insights de clientes"""
        if self.research_data.empty:
            return None
        
        # Análisis de comportamiento de clientes
        customer_insights = {}
        
        if 'customer_segment' in self.research_data.columns:
            # Análisis por segmento de cliente
            segment_analysis = self.research_data.groupby('customer_segment').agg({
                'customer_count': 'sum',
                'satisfaction_score': 'mean',
                'purchase_frequency': 'mean',
                'avg_order_value': 'mean',
                'loyalty_score': 'mean'
            }).reset_index()
            
            customer_insights['segment_analysis'] = segment_analysis.to_dict('records')
            
            # Análisis de satisfacción
            satisfaction_analysis = self._analyze_customer_satisfaction()
            customer_insights['satisfaction_analysis'] = satisfaction_analysis
            
            # Análisis de lealtad
            loyalty_analysis = self._analyze_customer_loyalty()
            customer_insights['loyalty_analysis'] = loyalty_analysis
        
        # Análisis de necesidades de clientes
        if 'customer_needs' in self.research_data.columns:
            needs_analysis = self._analyze_customer_needs()
            customer_insights['needs_analysis'] = needs_analysis
        
        # Análisis de pain points
        if 'pain_points' in self.research_data.columns:
            pain_points_analysis = self._analyze_pain_points()
            customer_insights['pain_points_analysis'] = pain_points_analysis
        
        self.customer_insights = customer_insights
        return customer_insights
    
    def _analyze_customer_satisfaction(self):
        """Analizar satisfacción del cliente"""
        satisfaction_analysis = {}
        
        if 'satisfaction_score' in self.research_data.columns:
            satisfaction_scores = self.research_data['satisfaction_score']
            
            satisfaction_analysis = {
                'avg_satisfaction': satisfaction_scores.mean(),
                'satisfaction_distribution': {
                    'very_satisfied': len(satisfaction_scores[satisfaction_scores >= 4.5]),
                    'satisfied': len(satisfaction_scores[(satisfaction_scores >= 3.5) & (satisfaction_scores < 4.5)]),
                    'neutral': len(satisfaction_scores[(satisfaction_scores >= 2.5) & (satisfaction_scores < 3.5)]),
                    'dissatisfied': len(satisfaction_scores[(satisfaction_scores >= 1.5) & (satisfaction_scores < 2.5)]),
                    'very_dissatisfied': len(satisfaction_scores[satisfaction_scores < 1.5])
                },
                'satisfaction_trend': self._calculate_satisfaction_trend()
            }
        
        return satisfaction_analysis
    
    def _analyze_customer_loyalty(self):
        """Analizar lealtad del cliente"""
        loyalty_analysis = {}
        
        if 'loyalty_score' in self.research_data.columns:
            loyalty_scores = self.research_data['loyalty_score']
            
            loyalty_analysis = {
                'avg_loyalty': loyalty_scores.mean(),
                'loyalty_distribution': {
                    'highly_loyal': len(loyalty_scores[loyalty_scores >= 4.5]),
                    'loyal': len(loyalty_scores[(loyalty_scores >= 3.5) & (loyalty_scores < 4.5)]),
                    'moderate': len(loyalty_scores[(loyalty_scores >= 2.5) & (loyalty_scores < 3.5)]),
                    'low_loyalty': len(loyalty_scores[(loyalty_scores >= 1.5) & (loyalty_scores < 2.5)]),
                    'no_loyalty': len(loyalty_scores[loyalty_scores < 1.5])
                },
                'loyalty_trend': self._calculate_loyalty_trend()
            }
        
        return loyalty_analysis
    
    def _analyze_customer_needs(self):
        """Analizar necesidades de clientes"""
        needs_analysis = {}
        
        if 'customer_needs' in self.research_data.columns:
            # Análisis de necesidades más mencionadas
            needs_frequency = self.research_data['customer_needs'].value_counts()
            
            needs_analysis = {
                'top_needs': needs_frequency.head(10).to_dict(),
                'needs_categories': self._categorize_customer_needs(),
                'unmet_needs': self._identify_unmet_needs()
            }
        
        return needs_analysis
    
    def _analyze_pain_points(self):
        """Analizar pain points de clientes"""
        pain_points_analysis = {}
        
        if 'pain_points' in self.research_data.columns:
            # Análisis de pain points más mencionados
            pain_points_frequency = self.research_data['pain_points'].value_counts()
            
            pain_points_analysis = {
                'top_pain_points': pain_points_frequency.head(10).to_dict(),
                'pain_point_categories': self._categorize_pain_points(),
                'pain_point_severity': self._analyze_pain_point_severity()
            }
        
        return pain_points_analysis
    
    def _categorize_customer_needs(self):
        """Categorizar necesidades de clientes"""
        # Categorías predefinidas de necesidades
        need_categories = {
            'Quality': ['quality', 'durability', 'reliability'],
            'Price': ['price', 'cost', 'affordable', 'value'],
            'Convenience': ['convenience', 'easy', 'simple', 'quick'],
            'Service': ['service', 'support', 'help', 'assistance'],
            'Innovation': ['innovation', 'new', 'advanced', 'modern']
        }
        
        categorized_needs = {}
        for category, keywords in need_categories.items():
            count = 0
            for need in self.research_data['customer_needs']:
                if any(keyword in need.lower() for keyword in keywords):
                    count += 1
            categorized_needs[category] = count
        
        return categorized_needs
    
    def _categorize_pain_points(self):
        """Categorizar pain points de clientes"""
        # Categorías predefinidas de pain points
        pain_categories = {
            'Technical Issues': ['bug', 'error', 'problem', 'issue', 'broken'],
            'Customer Service': ['service', 'support', 'response', 'help'],
            'Price Concerns': ['expensive', 'cost', 'price', 'overpriced'],
            'Quality Issues': ['quality', 'poor', 'bad', 'defective'],
            'Usability': ['difficult', 'hard', 'complicated', 'confusing']
        }
        
        categorized_pains = {}
        for category, keywords in pain_categories.items():
            count = 0
            for pain in self.research_data['pain_points']:
                if any(keyword in pain.lower() for keyword in keywords):
                    count += 1
            categorized_pains[category] = count
        
        return categorized_pains
    
    def _identify_unmet_needs(self):
        """Identificar necesidades no satisfechas"""
        unmet_needs = []
        
        if 'customer_needs' in self.research_data.columns and 'satisfaction_score' in self.research_data.columns:
            # Identificar necesidades con baja satisfacción
            for need in self.research_data['customer_needs'].unique():
                need_data = self.research_data[self.research_data['customer_needs'] == need]
                avg_satisfaction = need_data['satisfaction_score'].mean()
                
                if avg_satisfaction < 3.0:  # Baja satisfacción
                    unmet_needs.append({
                        'need': need,
                        'satisfaction_score': avg_satisfaction,
                        'customer_count': len(need_data)
                    })
        
        return unmet_needs
    
    def _analyze_pain_point_severity(self):
        """Analizar severidad de pain points"""
        pain_severity = {}
        
        if 'pain_points' in self.research_data.columns and 'satisfaction_score' in self.research_data.columns:
            for pain in self.research_data['pain_points'].unique():
                pain_data = self.research_data[self.research_data['pain_points'] == pain]
                avg_satisfaction = pain_data['satisfaction_score'].mean()
                
                if avg_satisfaction < 2.0:
                    severity = 'High'
                elif avg_satisfaction < 3.0:
                    severity = 'Medium'
                else:
                    severity = 'Low'
                
                pain_severity[pain] = {
                    'severity': severity,
                    'satisfaction_impact': avg_satisfaction,
                    'customer_count': len(pain_data)
                }
        
        return pain_severity
    
    def _calculate_satisfaction_trend(self):
        """Calcular tendencia de satisfacción"""
        if 'date' in self.research_data.columns and 'satisfaction_score' in self.research_data.columns:
            # Análisis de tendencia temporal
            self.research_data['date'] = pd.to_datetime(self.research_data['date'])
            monthly_satisfaction = self.research_data.groupby(self.research_data['date'].dt.to_period('M'))['satisfaction_score'].mean()
            
            if len(monthly_satisfaction) > 1:
                trend = monthly_satisfaction.iloc[-1] - monthly_satisfaction.iloc[0]
                return 'increasing' if trend > 0 else 'decreasing' if trend < 0 else 'stable'
        
        return 'stable'
    
    def _calculate_loyalty_trend(self):
        """Calcular tendencia de lealtad"""
        if 'date' in self.research_data.columns and 'loyalty_score' in self.research_data.columns:
            # Análisis de tendencia temporal
            self.research_data['date'] = pd.to_datetime(self.research_data['date'])
            monthly_loyalty = self.research_data.groupby(self.research_data['date'].dt.to_period('M'))['loyalty_score'].mean()
            
            if len(monthly_loyalty) > 1:
                trend = monthly_loyalty.iloc[-1] - monthly_loyalty.iloc[0]
                return 'increasing' if trend > 0 else 'decreasing' if trend < 0 else 'stable'
        
        return 'stable'
    
    def identify_market_opportunities(self):
        """Identificar oportunidades de mercado"""
        opportunities = []
        
        # Oportunidades basadas en análisis de mercado
        if self.market_analysis:
            market_size_analysis = self.market_analysis.get('market_size_analysis', {})
            segment_analysis = market_size_analysis.get('segment_analysis', [])
            
            for segment in segment_analysis:
                growth_rate = segment.get('growth_rate', 0)
                market_size = segment.get('market_size', 0)
                competition_level = segment.get('competition_level', 0)
                
                if growth_rate > 10 and competition_level < 0.7:  # Alto crecimiento, baja competencia
                    opportunities.append({
                        'opportunity_type': 'High Growth Segment',
                        'segment': segment.get('market_segment'),
                        'description': f'Segmento de alto crecimiento con baja competencia',
                        'potential_value': market_size * growth_rate / 100,
                        'priority': 'high'
                    })
        
        # Oportunidades basadas en análisis de competidores
        if self.competitor_analysis:
            market_gaps = self.competitor_analysis.get('market_gaps', [])
            
            for gap in market_gaps:
                opportunities.append({
                    'opportunity_type': 'Market Gap',
                    'gap_type': gap.get('gap_type'),
                    'description': gap.get('description'),
                    'priority': gap.get('opportunity_level', 'medium')
                })
        
        # Oportunidades basadas en insights de clientes
        if self.customer_insights:
            unmet_needs = self.customer_insights.get('needs_analysis', {}).get('unmet_needs', [])
            
            for need in unmet_needs:
                opportunities.append({
                    'opportunity_type': 'Unmet Need',
                    'need': need.get('need'),
                    'description': f'Necesidad no satisfecha con {need.get("customer_count")} clientes afectados',
                    'potential_value': need.get('customer_count', 0) * 100,  # Estimación
                    'priority': 'high'
                })
        
        self.market_opportunities = opportunities
        return opportunities
    
    def build_market_prediction_model(self, target_variable='market_size'):
        """Construir modelo de predicción de mercado"""
        if target_variable not in self.research_data.columns:
            raise ValueError(f"Variable objetivo '{target_variable}' no encontrada")
        
        # Preparar datos
        feature_columns = [col for col in self.research_data.columns if col != target_variable and col not in ['date', 'competitor_name']]
        X = self.research_data[feature_columns]
        y = self.research_data[target_variable]
        
        # Codificar variables categóricas
        label_encoders = {}
        for column in X.select_dtypes(include=['object']).columns:
            le = LabelEncoder()
            X[column] = le.fit_transform(X[column].astype(str))
            label_encoders[column] = le
        
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
            'feature_importance': dict(zip(feature_columns, model.feature_importances_))
        }
        
        # Guardar modelo
        self.research_models['market_predictor'] = {
            'model': model,
            'label_encoders': label_encoders,
            'feature_columns': feature_columns,
            'scaler': scaler,
            'metrics': model_metrics
        }
        
        return model_metrics
    
    def generate_research_insights(self):
        """Generar insights de market research"""
        insights = []
        
        # Insights de tamaño de mercado
        if self.market_analysis:
            total_market_size = self.market_analysis.get('total_market_size', 0)
            avg_growth_rate = self.market_analysis.get('avg_growth_rate', 0)
            
            if total_market_size > 0:
                insights.append({
                    'category': 'Market Size',
                    'insight': f'Tamaño total del mercado: ${total_market_size:,.0f}',
                    'recommendation': 'Evaluar potencial de entrada al mercado',
                    'priority': 'high'
                })
            
            if avg_growth_rate > 10:
                insights.append({
                    'category': 'Market Growth',
                    'insight': f'Tasa de crecimiento promedio: {avg_growth_rate:.1f}%',
                    'recommendation': 'Mercado en crecimiento, oportunidad de expansión',
                    'priority': 'high'
                })
        
        # Insights de competidores
        if self.competitor_analysis:
            market_gaps = self.competitor_analysis.get('market_gaps', [])
            
            if market_gaps:
                insights.append({
                    'category': 'Competition',
                    'insight': f'{len(market_gaps)} gaps de mercado identificados',
                    'recommendation': 'Explorar gaps para diferenciación',
                    'priority': 'medium'
                })
        
        # Insights de clientes
        if self.customer_insights:
            satisfaction_analysis = self.customer_insights.get('satisfaction_analysis', {})
            avg_satisfaction = satisfaction_analysis.get('avg_satisfaction', 0)
            
            if avg_satisfaction < 3.0:
                insights.append({
                    'category': 'Customer Satisfaction',
                    'insight': f'Satisfacción promedio baja: {avg_satisfaction:.2f}',
                    'recommendation': 'Mejorar satisfacción del cliente',
                    'priority': 'high'
                })
        
        # Insights de oportunidades
        if self.market_opportunities:
            high_priority_opportunities = [opp for opp in self.market_opportunities if opp.get('priority') == 'high']
            
            if high_priority_opportunities:
                insights.append({
                    'category': 'Market Opportunities',
                    'insight': f'{len(high_priority_opportunities)} oportunidades de alta prioridad',
                    'recommendation': 'Priorizar desarrollo de oportunidades de alto valor',
                    'priority': 'high'
                })
        
        self.research_insights = insights
        return insights
    
    def create_research_dashboard(self):
        """Crear dashboard de market research"""
        if not self.research_data.empty:
            return None
        
        # Crear subplots
        fig = make_subplots(
            rows=2, cols=2,
            subplot_titles=('Market Size by Segment', 'Competitor Analysis',
                          'Customer Satisfaction', 'Market Opportunities'),
            specs=[[{"type": "bar"}, {"type": "scatter"}],
                   [{"type": "pie"}, {"type": "bar"}]]
        )
        
        # Gráfico de tamaño de mercado por segmento
        if self.market_analysis:
            market_size_analysis = self.market_analysis.get('market_size_analysis', {})
            segment_analysis = market_size_analysis.get('segment_analysis', [])
            
            if segment_analysis:
                segments = [segment['market_segment'] for segment in segment_analysis]
                market_sizes = [segment['market_size'] for segment in segment_analysis]
                
                fig.add_trace(
                    go.Bar(x=segments, y=market_sizes, name='Market Size by Segment'),
                    row=1, col=1
                )
        
        # Gráfico de análisis de competidores
        if self.competitor_analysis:
            competitor_data = self.competitor_analysis.get('competitor_data', [])
            
            if competitor_data:
                competitors = [comp['competitor_name'] for comp in competitor_data]
                market_shares = [comp['market_share'] for comp in competitor_data]
                
                fig.add_trace(
                    go.Scatter(x=competitors, y=market_shares, mode='markers', name='Competitor Market Share'),
                    row=1, col=2
                )
        
        # Gráfico de satisfacción del cliente
        if self.customer_insights:
            satisfaction_analysis = self.customer_insights.get('satisfaction_analysis', {})
            satisfaction_dist = satisfaction_analysis.get('satisfaction_distribution', {})
            
            if satisfaction_dist:
                categories = list(satisfaction_dist.keys())
                values = list(satisfaction_dist.values())
                
                fig.add_trace(
                    go.Pie(labels=categories, values=values, name='Customer Satisfaction'),
                    row=2, col=1
                )
        
        # Gráfico de oportunidades de mercado
        if self.market_opportunities:
            opportunity_types = [opp['opportunity_type'] for opp in self.market_opportunities]
            opportunity_counts = {}
            
            for opp_type in opportunity_types:
                opportunity_counts[opp_type] = opportunity_counts.get(opp_type, 0) + 1
            
            types = list(opportunity_counts.keys())
            counts = list(opportunity_counts.values())
            
            fig.add_trace(
                go.Bar(x=types, y=counts, name='Market Opportunities'),
                row=2, col=2
            )
        
        fig.update_layout(
            title="Dashboard de Market Research",
            showlegend=False,
            height=800
        )
        
        return fig
    
    def export_research_analysis(self, filename='market_research_analysis.json'):
        """Exportar análisis de market research"""
        export_data = {
            'timestamp': datetime.now().isoformat(),
            'market_analysis': self.market_analysis,
            'competitor_analysis': self.competitor_analysis,
            'customer_insights': self.customer_insights,
            'market_opportunities': self.market_opportunities,
            'research_models': {k: {'metrics': v['metrics']} for k, v in self.research_models.items()},
            'research_insights': self.research_insights,
            'summary': {
                'total_market_size': self.market_analysis.get('total_market_size', 0),
                'analysis_date': datetime.now().isoformat()
            }
        }
        
        with open(filename, 'w') as f:
            json.dump(export_data, f, indent=2, default=str)
        
        print(f"✅ Análisis de market research exportado a {filename}")
        return export_data

# Ejemplo de uso
if __name__ == "__main__":
    # Crear instancia del analizador de market research
    research_analyzer = MarketResearchAnalyzer()
    
    # Datos de ejemplo
    sample_data = pd.DataFrame({
        'market_segment': np.random.choice(['Enterprise', 'SMB', 'Consumer'], 1000),
        'market_size': np.random.normal(1000000, 200000, 1000),
        'growth_rate': np.random.uniform(5, 25, 1000),
        'competition_level': np.random.uniform(0.3, 0.9, 1000),
        'customer_count': np.random.poisson(10000, 1000),
        'competitor_name': np.random.choice(['Competitor A', 'Competitor B', 'Competitor C'], 1000),
        'market_share': np.random.uniform(5, 30, 1000),
        'revenue': np.random.normal(500000, 100000, 1000),
        'price': np.random.normal(100, 20, 1000),
        'category': np.random.choice(['Technology', 'Healthcare', 'Finance'], 1000),
        'region': np.random.choice(['North', 'South', 'East', 'West'], 1000),
        'customer_segment': np.random.choice(['Premium', 'Standard', 'Basic'], 1000),
        'satisfaction_score': np.random.uniform(1, 5, 1000),
        'loyalty_score': np.random.uniform(1, 5, 1000),
        'customer_needs': np.random.choice(['Quality', 'Price', 'Service', 'Innovation'], 1000),
        'pain_points': np.random.choice(['Technical Issues', 'Customer Service', 'Price Concerns'], 1000),
        'date': pd.date_range('2023-01-01', periods=1000, freq='D')
    })
    
    # Cargar datos de market research
    print("📊 Cargando datos de market research...")
    research_analyzer.load_research_data(sample_data)
    
    # Analizar tamaño del mercado
    print("📈 Analizando tamaño del mercado...")
    market_analysis = research_analyzer.analyze_market_size()
    
    # Analizar competidores
    print("🏆 Analizando competidores...")
    competitor_analysis = research_analyzer.analyze_competitors()
    
    # Analizar insights de clientes
    print("👥 Analizando insights de clientes...")
    customer_insights = research_analyzer.analyze_customer_insights()
    
    # Identificar oportunidades de mercado
    print("🎯 Identificando oportunidades de mercado...")
    market_opportunities = research_analyzer.identify_market_opportunities()
    
    # Construir modelo de predicción de mercado
    print("🔮 Construyendo modelo de predicción de mercado...")
    market_model = research_analyzer.build_market_prediction_model()
    
    # Generar insights de research
    print("💡 Generando insights de research...")
    research_insights = research_analyzer.generate_research_insights()
    
    # Crear dashboard
    print("📊 Creando dashboard de market research...")
    dashboard = research_analyzer.create_research_dashboard()
    
    # Exportar análisis
    print("💾 Exportando análisis de market research...")
    export_data = research_analyzer.export_research_analysis()
    
    print("✅ Sistema de análisis de market research completado!")




