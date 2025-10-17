"""
Marketing Brain Email Marketing Analyzer
Sistema avanzado de análisis de email marketing
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

class EmailMarketingAnalyzer:
    def __init__(self):
        self.email_data = {}
        self.campaign_analysis = {}
        self.audience_analysis = {}
        self.content_analysis = {}
        self.email_models = {}
        self.optimization_strategies = {}
        self.email_insights = {}
        
    def load_email_data(self, email_data):
        """Cargar datos de email marketing"""
        if isinstance(email_data, str):
            if email_data.endswith('.csv'):
                self.email_data = pd.read_csv(email_data)
            elif email_data.endswith('.json'):
                with open(email_data, 'r') as f:
                    data = json.load(f)
                self.email_data = pd.DataFrame(data)
        else:
            self.email_data = pd.DataFrame(email_data)
        
        print(f"✅ Datos de email marketing cargados: {len(self.email_data)} registros")
        return True
    
    def analyze_email_campaigns(self):
        """Analizar campañas de email"""
        if self.email_data.empty:
            return None
        
        # Análisis de campañas por performance
        campaign_analysis = self.email_data.groupby('campaign_id').agg({
            'sent': 'sum',
            'delivered': 'sum',
            'opened': 'sum',
            'clicked': 'sum',
            'converted': 'sum',
            'unsubscribed': 'sum',
            'bounced': 'sum',
            'revenue': 'sum',
            'cost': 'sum'
        }).reset_index()
        
        # Calcular métricas de performance
        campaign_analysis['delivery_rate'] = (campaign_analysis['delivered'] / campaign_analysis['sent']) * 100
        campaign_analysis['open_rate'] = (campaign_analysis['opened'] / campaign_analysis['delivered']) * 100
        campaign_analysis['click_rate'] = (campaign_analysis['clicked'] / campaign_analysis['opened']) * 100
        campaign_analysis['conversion_rate'] = (campaign_analysis['converted'] / campaign_analysis['clicked']) * 100
        campaign_analysis['unsubscribe_rate'] = (campaign_analysis['unsubscribed'] / campaign_analysis['delivered']) * 100
        campaign_analysis['bounce_rate'] = (campaign_analysis['bounced'] / campaign_analysis['sent']) * 100
        campaign_analysis['roi'] = (campaign_analysis['revenue'] - campaign_analysis['cost']) / campaign_analysis['cost']
        campaign_analysis['revenue_per_email'] = campaign_analysis['revenue'] / campaign_analysis['sent']
        
        # Análisis de eficiencia
        efficiency_analysis = self._analyze_campaign_efficiency(campaign_analysis)
        
        # Análisis de tendencias
        trend_analysis = self._analyze_campaign_trends()
        
        # Análisis de segmentos
        segment_analysis = self._analyze_campaign_segments()
        
        campaign_results = {
            'campaign_analysis': campaign_analysis.to_dict('records'),
            'efficiency_analysis': efficiency_analysis,
            'trend_analysis': trend_analysis,
            'segment_analysis': segment_analysis,
            'total_sent': campaign_analysis['sent'].sum(),
            'total_revenue': campaign_analysis['revenue'].sum(),
            'overall_open_rate': (campaign_analysis['opened'].sum() / campaign_analysis['delivered'].sum()) * 100,
            'overall_click_rate': (campaign_analysis['clicked'].sum() / campaign_analysis['opened'].sum()) * 100
        }
        
        self.campaign_analysis = campaign_results
        return campaign_results
    
    def _analyze_campaign_efficiency(self, campaign_analysis):
        """Analizar eficiencia de campañas"""
        efficiency_metrics = {}
        
        for _, campaign in campaign_analysis.iterrows():
            # Score de eficiencia basado en múltiples métricas
            efficiency_score = 0
            
            # Open rate (25% del score)
            open_rate = campaign['open_rate']
            if open_rate > 25:
                efficiency_score += 25
            elif open_rate > 20:
                efficiency_score += 20
            elif open_rate > 15:
                efficiency_score += 15
            else:
                efficiency_score += 10
            
            # Click rate (25% del score)
            click_rate = campaign['click_rate']
            if click_rate > 5:
                efficiency_score += 25
            elif click_rate > 3:
                efficiency_score += 20
            elif click_rate > 2:
                efficiency_score += 15
            else:
                efficiency_score += 10
            
            # Conversion rate (20% del score)
            conversion_rate = campaign['conversion_rate']
            if conversion_rate > 10:
                efficiency_score += 20
            elif conversion_rate > 5:
                efficiency_score += 15
            elif conversion_rate > 2:
                efficiency_score += 10
            else:
                efficiency_score += 5
            
            # ROI (15% del score)
            roi = campaign['roi']
            if roi > 3:
                efficiency_score += 15
            elif roi > 2:
                efficiency_score += 10
            elif roi > 1:
                efficiency_score += 5
            
            # Delivery rate (10% del score)
            delivery_rate = campaign['delivery_rate']
            if delivery_rate > 95:
                efficiency_score += 10
            elif delivery_rate > 90:
                efficiency_score += 7
            elif delivery_rate > 85:
                efficiency_score += 5
            
            # Unsubscribe rate (5% del score)
            unsubscribe_rate = campaign['unsubscribe_rate']
            if unsubscribe_rate < 0.5:
                efficiency_score += 5
            elif unsubscribe_rate < 1:
                efficiency_score += 3
            elif unsubscribe_rate < 2:
                efficiency_score += 1
            
            efficiency_metrics[campaign['campaign_id']] = {
                'efficiency_score': efficiency_score,
                'open_rate': open_rate,
                'click_rate': click_rate,
                'conversion_rate': conversion_rate,
                'roi': roi,
                'delivery_rate': delivery_rate,
                'unsubscribe_rate': unsubscribe_rate
            }
        
        # Clasificar campañas por eficiencia
        efficiency_categories = {
            'high_efficiency': [],
            'medium_efficiency': [],
            'low_efficiency': []
        }
        
        for campaign_id, metrics in efficiency_metrics.items():
            score = metrics['efficiency_score']
            if score >= 80:
                efficiency_categories['high_efficiency'].append(campaign_id)
            elif score >= 60:
                efficiency_categories['medium_efficiency'].append(campaign_id)
            else:
                efficiency_categories['low_efficiency'].append(campaign_id)
        
        return {
            'efficiency_metrics': efficiency_metrics,
            'efficiency_categories': efficiency_categories
        }
    
    def _analyze_campaign_trends(self):
        """Analizar tendencias de campañas"""
        trend_analysis = {}
        
        if 'send_date' in self.email_data.columns:
            # Análisis de tendencias temporales
            self.email_data['send_date'] = pd.to_datetime(self.email_data['send_date'])
            self.email_data['month'] = self.email_data['send_date'].dt.to_period('M')
            
            # Tendencias mensuales
            monthly_trends = self.email_data.groupby('month').agg({
                'sent': 'sum',
                'opened': 'sum',
                'clicked': 'sum',
                'converted': 'sum',
                'revenue': 'sum'
            }).reset_index()
            
            # Calcular métricas mensuales
            monthly_trends['open_rate'] = (monthly_trends['opened'] / monthly_trends['sent']) * 100
            monthly_trends['click_rate'] = (monthly_trends['clicked'] / monthly_trends['opened']) * 100
            monthly_trends['conversion_rate'] = (monthly_trends['converted'] / monthly_trends['clicked']) * 100
            
            trend_analysis['monthly_trends'] = monthly_trends.to_dict('records')
            
            # Análisis de tendencias por tipo de campaña
            if 'campaign_type' in self.email_data.columns:
                type_trends = self.email_data.groupby(['month', 'campaign_type']).agg({
                    'open_rate': 'mean',
                    'click_rate': 'mean',
                    'conversion_rate': 'mean'
                }).reset_index()
                
                trend_analysis['type_trends'] = type_trends.to_dict('records')
        
        return trend_analysis
    
    def _analyze_campaign_segments(self):
        """Analizar segmentos de campañas"""
        segment_analysis = {}
        
        if 'audience_segment' in self.email_data.columns:
            # Análisis por segmento de audiencia
            segment_performance = self.email_data.groupby('audience_segment').agg({
                'sent': 'sum',
                'opened': 'sum',
                'clicked': 'sum',
                'converted': 'sum',
                'revenue': 'sum'
            }).reset_index()
            
            # Calcular métricas por segmento
            segment_performance['open_rate'] = (segment_performance['opened'] / segment_performance['sent']) * 100
            segment_performance['click_rate'] = (segment_performance['clicked'] / segment_performance['opened']) * 100
            segment_performance['conversion_rate'] = (segment_performance['converted'] / segment_performance['clicked']) * 100
            segment_performance['revenue_per_email'] = segment_performance['revenue'] / segment_performance['sent']
            
            segment_analysis['audience_segments'] = segment_performance.to_dict('records')
        
        return segment_analysis
    
    def analyze_email_audience(self):
        """Analizar audiencia de email"""
        if self.email_data.empty:
            return None
        
        # Análisis de audiencia
        audience_analysis = {}
        
        # Análisis de comportamiento de audiencia
        if 'subscriber_id' in self.email_data.columns:
            subscriber_behavior = self.email_data.groupby('subscriber_id').agg({
                'opened': 'sum',
                'clicked': 'sum',
                'converted': 'sum',
                'unsubscribed': 'sum',
                'revenue': 'sum'
            }).reset_index()
            
            # Calcular métricas de comportamiento
            subscriber_behavior['open_frequency'] = subscriber_behavior['opened']
            subscriber_behavior['click_frequency'] = subscriber_behavior['clicked']
            subscriber_behavior['conversion_frequency'] = subscriber_behavior['converted']
            subscriber_behavior['lifetime_value'] = subscriber_behavior['revenue']
            
            # Segmentación de audiencia
            audience_segments = self._create_audience_segments(subscriber_behavior)
            audience_analysis['audience_segments'] = audience_segments
        
        # Análisis de engagement
        engagement_analysis = self._analyze_audience_engagement()
        audience_analysis['engagement_analysis'] = engagement_analysis
        
        # Análisis de churn
        churn_analysis = self._analyze_audience_churn()
        audience_analysis['churn_analysis'] = churn_analysis
        
        self.audience_analysis = audience_analysis
        return audience_analysis
    
    def _create_audience_segments(self, subscriber_behavior):
        """Crear segmentos de audiencia"""
        # Segmentación basada en comportamiento
        segments = []
        
        for _, subscriber in subscriber_behavior.iterrows():
            open_freq = subscriber['open_frequency']
            click_freq = subscriber['click_frequency']
            conversion_freq = subscriber['conversion_frequency']
            ltv = subscriber['lifetime_value']
            
            if open_freq >= 10 and click_freq >= 5 and conversion_freq >= 2:
                segment = 'Champions'
            elif open_freq >= 5 and click_freq >= 2 and conversion_freq >= 1:
                segment = 'Loyal Customers'
            elif open_freq >= 3 and click_freq >= 1:
                segment = 'Potential Loyalists'
            elif open_freq >= 1:
                segment = 'New Customers'
            elif open_freq == 0:
                segment = 'At Risk'
            else:
                segment = 'Need Attention'
            
            segments.append({
                'subscriber_id': subscriber['subscriber_id'],
                'segment': segment,
                'open_frequency': open_freq,
                'click_frequency': click_freq,
                'conversion_frequency': conversion_freq,
                'lifetime_value': ltv
            })
        
        # Análisis de segmentos
        segment_analysis = pd.DataFrame(segments).groupby('segment').agg({
            'subscriber_id': 'count',
            'open_frequency': 'mean',
            'click_frequency': 'mean',
            'conversion_frequency': 'mean',
            'lifetime_value': 'mean'
        }).reset_index()
        
        segment_analysis.columns = [
            'segment', 'subscriber_count', 'avg_open_frequency',
            'avg_click_frequency', 'avg_conversion_frequency', 'avg_lifetime_value'
        ]
        
        return segment_analysis.to_dict('records')
    
    def _analyze_audience_engagement(self):
        """Analizar engagement de audiencia"""
        engagement_analysis = {}
        
        if 'subscriber_id' in self.email_data.columns:
            # Análisis de engagement por período
            if 'send_date' in self.email_data.columns:
                self.email_data['send_date'] = pd.to_datetime(self.email_data['send_date'])
                self.email_data['month'] = self.email_data['send_date'].dt.to_period('M')
                
                monthly_engagement = self.email_data.groupby('month').agg({
                    'opened': 'sum',
                    'clicked': 'sum',
                    'converted': 'sum'
                }).reset_index()
                
                engagement_analysis['monthly_engagement'] = monthly_engagement.to_dict('records')
            
            # Análisis de engagement por tipo de contenido
            if 'content_type' in self.email_data.columns:
                content_engagement = self.email_data.groupby('content_type').agg({
                    'open_rate': 'mean',
                    'click_rate': 'mean',
                    'conversion_rate': 'mean'
                }).reset_index()
                
                engagement_analysis['content_engagement'] = content_engagement.to_dict('records')
        
        return engagement_analysis
    
    def _analyze_audience_churn(self):
        """Analizar churn de audiencia"""
        churn_analysis = {}
        
        if 'subscriber_id' in self.email_data.columns and 'unsubscribed' in self.email_data.columns:
            # Análisis de churn por período
            if 'send_date' in self.email_data.columns:
                self.email_data['send_date'] = pd.to_datetime(self.email_data['send_date'])
                self.email_data['month'] = self.email_data['send_date'].dt.to_period('M')
                
                monthly_churn = self.email_data.groupby('month').agg({
                    'unsubscribed': 'sum',
                    'sent': 'sum'
                }).reset_index()
                
                monthly_churn['churn_rate'] = (monthly_churn['unsubscribed'] / monthly_churn['sent']) * 100
                
                churn_analysis['monthly_churn'] = monthly_churn.to_dict('records')
            
            # Análisis de churn por segmento
            if 'audience_segment' in self.email_data.columns:
                segment_churn = self.email_data.groupby('audience_segment').agg({
                    'unsubscribed': 'sum',
                    'sent': 'sum'
                }).reset_index()
                
                segment_churn['churn_rate'] = (segment_churn['unsubscribed'] / segment_churn['sent']) * 100
                
                churn_analysis['segment_churn'] = segment_churn.to_dict('records')
        
        return churn_analysis
    
    def analyze_email_content(self):
        """Analizar contenido de email"""
        if self.email_data.empty:
            return None
        
        # Análisis de contenido
        content_analysis = {}
        
        # Análisis por tipo de contenido
        if 'content_type' in self.email_data.columns:
            content_type_analysis = self.email_data.groupby('content_type').agg({
                'sent': 'sum',
                'opened': 'sum',
                'clicked': 'sum',
                'converted': 'sum',
                'revenue': 'sum'
            }).reset_index()
            
            # Calcular métricas de performance
            content_type_analysis['open_rate'] = (content_type_analysis['opened'] / content_type_analysis['sent']) * 100
            content_type_analysis['click_rate'] = (content_type_analysis['clicked'] / content_type_analysis['opened']) * 100
            content_type_analysis['conversion_rate'] = (content_type_analysis['converted'] / content_type_analysis['clicked']) * 100
            content_type_analysis['revenue_per_email'] = content_type_analysis['revenue'] / content_type_analysis['sent']
            
            content_analysis['content_type_analysis'] = content_type_analysis.to_dict('records')
        
        # Análisis por tema de contenido
        if 'content_topic' in self.email_data.columns:
            topic_analysis = self.email_data.groupby('content_topic').agg({
                'open_rate': 'mean',
                'click_rate': 'mean',
                'conversion_rate': 'mean',
                'revenue': 'sum'
            }).reset_index()
            
            content_analysis['topic_analysis'] = topic_analysis.to_dict('records')
        
        # Análisis por formato de contenido
        if 'content_format' in self.email_data.columns:
            format_analysis = self.email_data.groupby('content_format').agg({
                'open_rate': 'mean',
                'click_rate': 'mean',
                'conversion_rate': 'mean',
                'revenue': 'sum'
            }).reset_index()
            
            content_analysis['format_analysis'] = format_analysis.to_dict('records')
        
        # Análisis de subject lines
        subject_analysis = self._analyze_subject_lines()
        content_analysis['subject_analysis'] = subject_analysis
        
        # Análisis de timing
        timing_analysis = self._analyze_content_timing()
        content_analysis['timing_analysis'] = timing_analysis
        
        self.content_analysis = content_analysis
        return content_analysis
    
    def _analyze_subject_lines(self):
        """Analizar subject lines"""
        subject_analysis = {}
        
        if 'subject_line' in self.email_data.columns:
            # Análisis de subject lines más efectivos
            subject_performance = self.email_data.groupby('subject_line').agg({
                'open_rate': 'mean',
                'click_rate': 'mean',
                'conversion_rate': 'mean',
                'sent': 'sum'
            }).reset_index()
            
            # Filtrar subject lines con suficiente volumen
            subject_performance = subject_performance[subject_performance['sent'] >= 100]
            
            # Ordenar por open rate
            top_subject_lines = subject_performance.nlargest(10, 'open_rate')
            
            subject_analysis = {
                'top_subject_lines': top_subject_lines.to_dict('records'),
                'subject_performance': subject_performance.to_dict('records'),
                'avg_open_rate': subject_performance['open_rate'].mean()
            }
        
        return subject_analysis
    
    def _analyze_content_timing(self):
        """Analizar timing de contenido"""
        timing_analysis = {}
        
        if 'send_date' in self.email_data.columns:
            # Análisis de timing por día de la semana
            self.email_data['send_date'] = pd.to_datetime(self.email_data['send_date'])
            self.email_data['day_of_week'] = self.email_data['send_date'].dt.day_name()
            
            daily_timing = self.email_data.groupby('day_of_week').agg({
                'open_rate': 'mean',
                'click_rate': 'mean',
                'conversion_rate': 'mean',
                'sent': 'sum'
            }).reset_index()
            
            # Análisis de timing por hora del día
            self.email_data['hour'] = self.email_data['send_date'].dt.hour
            
            hourly_timing = self.email_data.groupby('hour').agg({
                'open_rate': 'mean',
                'click_rate': 'mean',
                'conversion_rate': 'mean',
                'sent': 'sum'
            }).reset_index()
            
            timing_analysis = {
                'daily_timing': daily_timing.to_dict('records'),
                'hourly_timing': hourly_timing.to_dict('records'),
                'best_day': daily_timing.loc[daily_timing['open_rate'].idxmax(), 'day_of_week'],
                'best_hour': hourly_timing.loc[hourly_timing['open_rate'].idxmax(), 'hour']
            }
        
        return timing_analysis
    
    def build_email_prediction_model(self, target_variable='open_rate'):
        """Construir modelo de predicción de email"""
        if target_variable not in self.email_data.columns:
            raise ValueError(f"Variable objetivo '{target_variable}' no encontrada")
        
        # Preparar datos
        feature_columns = [col for col in self.email_data.columns if col != target_variable and col not in ['send_date', 'subject_line']]
        X = self.email_data[feature_columns]
        y = self.email_data[target_variable]
        
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
        
        from sklearn.metrics import mean_squared_error, r2_score, mean_absolute_error
        model_metrics = {
            'mse': mean_squared_error(y_test, y_pred),
            'rmse': np.sqrt(mean_squared_error(y_test, y_pred)),
            'mae': mean_absolute_error(y_test, y_pred),
            'r2': r2_score(y_test, y_pred),
            'feature_importance': dict(zip(feature_columns, model.feature_importances_))
        }
        
        # Guardar modelo
        self.email_models['email_predictor'] = {
            'model': model,
            'label_encoders': label_encoders,
            'feature_columns': feature_columns,
            'scaler': scaler,
            'metrics': model_metrics
        }
        
        return model_metrics
    
    def generate_email_strategies(self):
        """Generar estrategias de email marketing"""
        strategies = []
        
        # Estrategias basadas en análisis de campañas
        if self.campaign_analysis:
            efficiency_analysis = self.campaign_analysis.get('efficiency_analysis', {})
            efficiency_categories = efficiency_analysis.get('efficiency_categories', {})
            
            # Estrategias para campañas de alta eficiencia
            high_efficiency_campaigns = efficiency_categories.get('high_efficiency', [])
            if high_efficiency_campaigns:
                strategies.append({
                    'strategy_type': 'Scale High Efficiency Campaigns',
                    'description': f'Escalar campañas de alta eficiencia: {len(high_efficiency_campaigns)} campañas',
                    'priority': 'high',
                    'expected_impact': 'high'
                })
            
            # Estrategias para campañas de baja eficiencia
            low_efficiency_campaigns = efficiency_categories.get('low_efficiency', [])
            if low_efficiency_campaigns:
                strategies.append({
                    'strategy_type': 'Optimize Low Efficiency Campaigns',
                    'description': f'Optimizar campañas de baja eficiencia: {len(low_efficiency_campaigns)} campañas',
                    'priority': 'medium',
                    'expected_impact': 'medium'
                })
        
        # Estrategias basadas en análisis de audiencia
        if self.audience_analysis:
            audience_segments = self.audience_analysis.get('audience_segments', [])
            
            # Identificar segmentos de alto valor
            high_value_segments = [seg for seg in audience_segments if seg.get('avg_lifetime_value', 0) > 100]
            if high_value_segments:
                strategies.append({
                    'strategy_type': 'Target High Value Segments',
                    'description': f'Enfocar en segmentos de alto valor: {len(high_value_segments)} segmentos',
                    'priority': 'high',
                    'expected_impact': 'high'
                })
            
            # Identificar segmentos en riesgo
            at_risk_segments = [seg for seg in audience_segments if seg.get('segment') == 'At Risk']
            if at_risk_segments:
                strategies.append({
                    'strategy_type': 'Re-engage At Risk Segments',
                    'description': f'Re-enganchar segmentos en riesgo: {len(at_risk_segments)} segmentos',
                    'priority': 'high',
                    'expected_impact': 'medium'
                })
        
        # Estrategias basadas en análisis de contenido
        if self.content_analysis:
            content_type_analysis = self.content_analysis.get('content_type_analysis', [])
            
            if content_type_analysis:
                # Identificar tipo de contenido más efectivo
                best_content_type = max(content_type_analysis, key=lambda x: x['open_rate'])
                strategies.append({
                    'strategy_type': 'Content Optimization',
                    'description': f'Aumentar contenido de tipo: {best_content_type["content_type"]}',
                    'priority': 'medium',
                    'expected_impact': 'medium'
                })
            
            # Estrategias basadas en timing
            timing_analysis = self.content_analysis.get('timing_analysis', {})
            if timing_analysis:
                best_day = timing_analysis.get('best_day')
                best_hour = timing_analysis.get('best_hour')
                
                if best_day and best_hour:
                    strategies.append({
                        'strategy_type': 'Timing Optimization',
                        'description': f'Publicar en {best_day} a las {best_hour}:00 para máximo engagement',
                        'priority': 'medium',
                        'expected_impact': 'medium'
                    })
        
        # Estrategias basadas en subject lines
        if self.content_analysis:
            subject_analysis = self.content_analysis.get('subject_analysis', {})
            top_subject_lines = subject_analysis.get('top_subject_lines', [])
            
            if top_subject_lines:
                strategies.append({
                    'strategy_type': 'Subject Line Optimization',
                    'description': f'Usar subject lines similares a los más efectivos',
                    'priority': 'low',
                    'expected_impact': 'low'
                })
        
        self.optimization_strategies = strategies
        return strategies
    
    def generate_email_insights(self):
        """Generar insights de email marketing"""
        insights = []
        
        # Insights de campañas
        if self.campaign_analysis:
            overall_open_rate = self.campaign_analysis.get('overall_open_rate', 0)
            
            if overall_open_rate < 20:
                insights.append({
                    'category': 'Campaign Performance',
                    'insight': f'Open rate general bajo: {overall_open_rate:.1f}%',
                    'recommendation': 'Mejorar open rate en todas las campañas',
                    'priority': 'high'
                })
            
            overall_click_rate = self.campaign_analysis.get('overall_click_rate', 0)
            if overall_click_rate < 3:
                insights.append({
                    'category': 'Campaign Performance',
                    'insight': f'Click rate general bajo: {overall_click_rate:.1f}%',
                    'recommendation': 'Mejorar click rate en todas las campañas',
                    'priority': 'high'
                })
        
        # Insights de audiencia
        if self.audience_analysis:
            audience_segments = self.audience_analysis.get('audience_segments', [])
            
            # Analizar distribución de segmentos
            at_risk_count = len([seg for seg in audience_segments if seg.get('segment') == 'At Risk'])
            total_segments = len(audience_segments)
            
            if at_risk_count > 0 and total_segments > 0:
                at_risk_percentage = at_risk_count / total_segments * 100
                if at_risk_percentage > 20:
                    insights.append({
                        'category': 'Audience Health',
                        'insight': f'{at_risk_percentage:.1f}% de segmentos en riesgo',
                        'recommendation': 'Implementar estrategias de re-engagement',
                        'priority': 'high'
                    })
        
        # Insights de contenido
        if self.content_analysis:
            content_type_analysis = self.content_analysis.get('content_type_analysis', [])
            
            if content_type_analysis:
                # Identificar tipo de contenido con mejor performance
                best_content = max(content_type_analysis, key=lambda x: x['open_rate'])
                insights.append({
                    'category': 'Content Performance',
                    'insight': f'Mejor tipo de contenido: {best_content["content_type"]} con {best_content["open_rate"]:.1f}% open rate',
                    'recommendation': 'Aumentar producción de este tipo de contenido',
                    'priority': 'medium'
                })
        
        # Insights de timing
        if self.content_analysis:
            timing_analysis = self.content_analysis.get('timing_analysis', {})
            best_day = timing_analysis.get('best_day')
            best_hour = timing_analysis.get('best_hour')
            
            if best_day and best_hour:
                insights.append({
                    'category': 'Content Timing',
                    'insight': f'Mejor momento para enviar: {best_day} a las {best_hour}:00',
                    'recommendation': 'Optimizar horarios de envío',
                    'priority': 'low'
                })
        
        # Insights de churn
        if self.audience_analysis:
            churn_analysis = self.audience_analysis.get('churn_analysis', {})
            monthly_churn = churn_analysis.get('monthly_churn', [])
            
            if monthly_churn:
                # Analizar tendencia de churn
                recent_churn = monthly_churn[-1]['churn_rate'] if monthly_churn else 0
                if recent_churn > 2:
                    insights.append({
                        'category': 'Audience Churn',
                        'insight': f'Tasa de churn alta: {recent_churn:.1f}%',
                        'recommendation': 'Implementar estrategias de retención',
                        'priority': 'high'
                    })
        
        self.email_insights = insights
        return insights
    
    def create_email_dashboard(self):
        """Crear dashboard de email marketing"""
        if not self.email_data.empty:
            return None
        
        # Crear subplots
        fig = make_subplots(
            rows=2, cols=2,
            subplot_titles=('Campaign Performance', 'Audience Segments',
                          'Content Performance', 'Timing Analysis'),
            specs=[[{"type": "bar"}, {"type": "pie"}],
                   [{"type": "bar"}, {"type": "scatter"}]]
        )
        
        # Gráfico de performance de campañas
        if self.campaign_analysis:
            campaign_analysis = self.campaign_analysis.get('campaign_analysis', [])
            if campaign_analysis:
                campaigns = [campaign['campaign_id'] for campaign in campaign_analysis]
                open_rates = [campaign['open_rate'] for campaign in campaign_analysis]
                
                fig.add_trace(
                    go.Bar(x=campaigns, y=open_rates, name='Campaign Open Rate'),
                    row=1, col=1
                )
        
        # Gráfico de segmentos de audiencia
        if self.audience_analysis:
            audience_segments = self.audience_analysis.get('audience_segments', [])
            if audience_segments:
                segments = [seg['segment'] for seg in audience_segments]
                subscriber_counts = [seg['subscriber_count'] for seg in audience_segments]
                
                fig.add_trace(
                    go.Pie(labels=segments, values=subscriber_counts, name='Audience Segments'),
                    row=1, col=2
                )
        
        # Gráfico de performance de contenido
        if self.content_analysis:
            content_type_analysis = self.content_analysis.get('content_type_analysis', [])
            if content_type_analysis:
                content_types = [content['content_type'] for content in content_type_analysis]
                open_rates = [content['open_rate'] for content in content_type_analysis]
                
                fig.add_trace(
                    go.Bar(x=content_types, y=open_rates, name='Content Open Rate'),
                    row=2, col=1
                )
        
        # Gráfico de análisis de timing
        if self.content_analysis:
            timing_analysis = self.content_analysis.get('timing_analysis', {})
            hourly_timing = timing_analysis.get('hourly_timing', [])
            
            if hourly_timing:
                hours = [data['hour'] for data in hourly_timing]
                open_rates = [data['open_rate'] for data in hourly_timing]
                
                fig.add_trace(
                    go.Scatter(x=hours, y=open_rates, mode='lines+markers', name='Hourly Open Rate'),
                    row=2, col=2
                )
        
        fig.update_layout(
            title="Dashboard de Email Marketing",
            showlegend=False,
            height=800
        )
        
        return fig
    
    def export_email_analysis(self, filename='email_marketing_analysis.json'):
        """Exportar análisis de email marketing"""
        export_data = {
            'timestamp': datetime.now().isoformat(),
            'campaign_analysis': self.campaign_analysis,
            'audience_analysis': self.audience_analysis,
            'content_analysis': self.content_analysis,
            'email_models': {k: {'metrics': v['metrics']} for k, v in self.email_models.items()},
            'optimization_strategies': self.optimization_strategies,
            'email_insights': self.email_insights,
            'summary': {
                'total_campaigns': len(self.email_data['campaign_id'].unique()) if 'campaign_id' in self.email_data.columns else 0,
                'total_sent': self.email_data['sent'].sum() if 'sent' in self.email_data.columns else 0,
                'analysis_date': datetime.now().isoformat()
            }
        }
        
        with open(filename, 'w') as f:
            json.dump(export_data, f, indent=2, default=str)
        
        print(f"✅ Análisis de email marketing exportado a {filename}")
        return export_data

# Ejemplo de uso
if __name__ == "__main__":
    # Crear instancia del analizador de email marketing
    email_analyzer = EmailMarketingAnalyzer()
    
    # Datos de ejemplo
    sample_data = pd.DataFrame({
        'campaign_id': np.random.randint(1, 50, 1000),
        'subscriber_id': np.random.randint(1, 500, 1000),
        'sent': np.random.poisson(1000, 1000),
        'delivered': np.random.poisson(950, 1000),
        'opened': np.random.poisson(200, 1000),
        'clicked': np.random.poisson(50, 1000),
        'converted': np.random.poisson(10, 1000),
        'unsubscribed': np.random.poisson(5, 1000),
        'bounced': np.random.poisson(50, 1000),
        'revenue': np.random.normal(500, 100, 1000),
        'cost': np.random.normal(100, 20, 1000),
        'open_rate': np.random.uniform(15, 30, 1000),
        'click_rate': np.random.uniform(2, 8, 1000),
        'conversion_rate': np.random.uniform(1, 15, 1000),
        'campaign_type': np.random.choice(['Newsletter', 'Promotional', 'Transactional', 'Welcome'], 1000),
        'audience_segment': np.random.choice(['New', 'Active', 'Inactive', 'VIP'], 1000),
        'content_type': np.random.choice(['Text', 'HTML', 'Image', 'Video'], 1000),
        'content_topic': np.random.choice(['Product', 'News', 'Promotion', 'Education'], 1000),
        'content_format': np.random.choice(['Single', 'Multi-column', 'Responsive'], 1000),
        'subject_line': np.random.choice(['Special Offer', 'News Update', 'Product Launch', 'Sale Alert'], 1000),
        'send_date': pd.date_range('2023-01-01', periods=1000, freq='D')
    })
    
    # Cargar datos de email marketing
    print("📊 Cargando datos de email marketing...")
    email_analyzer.load_email_data(sample_data)
    
    # Analizar campañas de email
    print("📧 Analizando campañas de email...")
    campaign_analysis = email_analyzer.analyze_email_campaigns()
    
    # Analizar audiencia de email
    print("👥 Analizando audiencia de email...")
    audience_analysis = email_analyzer.analyze_email_audience()
    
    # Analizar contenido de email
    print("📝 Analizando contenido de email...")
    content_analysis = email_analyzer.analyze_email_content()
    
    # Construir modelo de predicción de email
    print("🔮 Construyendo modelo de predicción de email...")
    email_model = email_analyzer.build_email_prediction_model()
    
    # Generar estrategias de email marketing
    print("🎯 Generando estrategias de email marketing...")
    email_strategies = email_analyzer.generate_email_strategies()
    
    # Generar insights de email marketing
    print("💡 Generando insights de email marketing...")
    email_insights = email_analyzer.generate_email_insights()
    
    # Crear dashboard
    print("📊 Creando dashboard de email marketing...")
    dashboard = email_analyzer.create_email_dashboard()
    
    # Exportar análisis
    print("💾 Exportando análisis de email marketing...")
    export_data = email_analyzer.export_email_analysis()
    
    print("✅ Sistema de análisis de email marketing completado!")






