"""
Marketing Brain Social Media Optimizer
Motor avanzado de optimización de social media marketing
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
from scipy.optimize import minimize
import warnings
warnings.filterwarnings('ignore')

class SocialMediaOptimizer:
    def __init__(self):
        self.social_data = {}
        self.platform_analysis = {}
        self.content_analysis = {}
        self.engagement_analysis = {}
        self.social_models = {}
        self.optimization_strategies = {}
        self.social_insights = {}
        
    def load_social_data(self, social_data):
        """Cargar datos de social media"""
        if isinstance(social_data, str):
            if social_data.endswith('.csv'):
                self.social_data = pd.read_csv(social_data)
            elif social_data.endswith('.json'):
                with open(social_data, 'r') as f:
                    data = json.load(f)
                self.social_data = pd.DataFrame(data)
        else:
            self.social_data = pd.DataFrame(social_data)
        
        print(f"✅ Datos de social media cargados: {len(self.social_data)} registros")
        return True
    
    def analyze_social_platforms(self):
        """Analizar plataformas de social media"""
        if self.social_data.empty:
            return None
        
        # Análisis de plataformas por performance
        platform_analysis = self.social_data.groupby('platform').agg({
            'followers': 'sum',
            'posts': 'sum',
            'likes': 'sum',
            'comments': 'sum',
            'shares': 'sum',
            'reach': 'sum',
            'impressions': 'sum',
            'clicks': 'sum',
            'conversions': 'sum',
            'cost': 'sum'
        }).reset_index()
        
        # Calcular métricas de performance
        platform_analysis['engagement_rate'] = ((platform_analysis['likes'] + platform_analysis['comments'] + platform_analysis['shares']) / platform_analysis['reach']) * 100
        platform_analysis['ctr'] = (platform_analysis['clicks'] / platform_analysis['impressions']) * 100
        platform_analysis['conversion_rate'] = (platform_analysis['conversions'] / platform_analysis['clicks']) * 100
        platform_analysis['cost_per_click'] = platform_analysis['cost'] / platform_analysis['clicks']
        platform_analysis['cost_per_conversion'] = platform_analysis['cost'] / platform_analysis['conversions']
        platform_analysis['roi'] = (platform_analysis['conversions'] * 100 - platform_analysis['cost']) / platform_analysis['cost']
        
        # Análisis de eficiencia
        efficiency_analysis = self._analyze_platform_efficiency(platform_analysis)
        
        # Análisis de tendencias
        trend_analysis = self._analyze_platform_trends()
        
        # Análisis de audiencia
        audience_analysis = self._analyze_platform_audience()
        
        platform_results = {
            'platform_analysis': platform_analysis.to_dict('records'),
            'efficiency_analysis': efficiency_analysis,
            'trend_analysis': trend_analysis,
            'audience_analysis': audience_analysis,
            'total_followers': platform_analysis['followers'].sum(),
            'total_engagement': (platform_analysis['likes'] + platform_analysis['comments'] + platform_analysis['shares']).sum(),
            'overall_engagement_rate': ((platform_analysis['likes'] + platform_analysis['comments'] + platform_analysis['shares']).sum() / platform_analysis['reach'].sum()) * 100
        }
        
        self.platform_analysis = platform_results
        return platform_results
    
    def _analyze_platform_efficiency(self, platform_analysis):
        """Analizar eficiencia de plataformas"""
        efficiency_metrics = {}
        
        for _, platform in platform_analysis.iterrows():
            # Score de eficiencia basado en múltiples métricas
            efficiency_score = 0
            
            # Engagement rate (30% del score)
            engagement_rate = platform['engagement_rate']
            if engagement_rate > 5:
                efficiency_score += 30
            elif engagement_rate > 3:
                efficiency_score += 20
            elif engagement_rate > 1:
                efficiency_score += 10
            
            # CTR (25% del score)
            ctr = platform['ctr']
            if ctr > 3:
                efficiency_score += 25
            elif ctr > 2:
                efficiency_score += 20
            elif ctr > 1:
                efficiency_score += 15
            else:
                efficiency_score += 5
            
            # Conversion rate (20% del score)
            conversion_rate = platform['conversion_rate']
            if conversion_rate > 5:
                efficiency_score += 20
            elif conversion_rate > 3:
                efficiency_score += 15
            elif conversion_rate > 1:
                efficiency_score += 10
            else:
                efficiency_score += 5
            
            # ROI (15% del score)
            roi = platform['roi']
            if roi > 3:
                efficiency_score += 15
            elif roi > 2:
                efficiency_score += 10
            elif roi > 1:
                efficiency_score += 5
            
            # Reach (10% del score)
            reach = platform['reach']
            if reach > 100000:
                efficiency_score += 10
            elif reach > 50000:
                efficiency_score += 7
            elif reach > 10000:
                efficiency_score += 5
            
            efficiency_metrics[platform['platform']] = {
                'efficiency_score': efficiency_score,
                'engagement_rate': engagement_rate,
                'ctr': ctr,
                'conversion_rate': conversion_rate,
                'roi': roi,
                'reach': reach
            }
        
        # Clasificar plataformas por eficiencia
        efficiency_categories = {
            'high_efficiency': [],
            'medium_efficiency': [],
            'low_efficiency': []
        }
        
        for platform, metrics in efficiency_metrics.items():
            score = metrics['efficiency_score']
            if score >= 80:
                efficiency_categories['high_efficiency'].append(platform)
            elif score >= 60:
                efficiency_categories['medium_efficiency'].append(platform)
            else:
                efficiency_categories['low_efficiency'].append(platform)
        
        return {
            'efficiency_metrics': efficiency_metrics,
            'efficiency_categories': efficiency_categories
        }
    
    def _analyze_platform_trends(self):
        """Analizar tendencias de plataformas"""
        trend_analysis = {}
        
        if 'date' in self.social_data.columns:
            # Análisis de tendencias temporales
            self.social_data['date'] = pd.to_datetime(self.social_data['date'])
            self.social_data['month'] = self.social_data['date'].dt.to_period('M')
            
            # Tendencias por plataforma
            for platform in self.social_data['platform'].unique():
                platform_data = self.social_data[self.social_data['platform'] == platform]
                
                monthly_trends = platform_data.groupby('month').agg({
                    'followers': 'sum',
                    'engagement_rate': 'mean',
                    'reach': 'sum',
                    'conversions': 'sum'
                }).reset_index()
                
                if len(monthly_trends) > 1:
                    # Calcular tendencias
                    followers_trend = self._calculate_trend(monthly_trends['followers'].values)
                    engagement_trend = self._calculate_trend(monthly_trends['engagement_rate'].values)
                    reach_trend = self._calculate_trend(monthly_trends['reach'].values)
                    conversions_trend = self._calculate_trend(monthly_trends['conversions'].values)
                    
                    trend_analysis[platform] = {
                        'followers_trend': followers_trend,
                        'engagement_trend': engagement_trend,
                        'reach_trend': reach_trend,
                        'conversions_trend': conversions_trend
                    }
        
        return trend_analysis
    
    def _analyze_platform_audience(self):
        """Analizar audiencia de plataformas"""
        audience_analysis = {}
        
        if 'audience_demographics' in self.social_data.columns:
            # Análisis de demografía por plataforma
            for platform in self.social_data['platform'].unique():
                platform_data = self.social_data[self.social_data['platform'] == platform]
                
                # Análisis de demografía
                demographics = platform_data['audience_demographics'].value_counts()
                
                audience_analysis[platform] = {
                    'demographics': demographics.to_dict(),
                    'audience_size': platform_data['followers'].sum(),
                    'avg_engagement_rate': platform_data['engagement_rate'].mean()
                }
        
        return audience_analysis
    
    def _calculate_trend(self, values):
        """Calcular tendencia de una serie de valores"""
        if len(values) < 2:
            return {'direction': 'stable', 'slope': 0, 'strength': 0}
        
        x = np.arange(len(values))
        y = values
        
        # Regresión lineal
        slope = np.polyfit(x, y, 1)[0]
        correlation = np.corrcoef(x, y)[0, 1]
        
        if slope > 0:
            direction = 'increasing'
        elif slope < 0:
            direction = 'decreasing'
        else:
            direction = 'stable'
        
        return {
            'direction': direction,
            'slope': slope,
            'strength': abs(correlation)
        }
    
    def analyze_content_performance(self):
        """Analizar performance de contenido"""
        if self.social_data.empty:
            return None
        
        # Análisis de contenido por tipo
        content_analysis = {}
        
        if 'content_type' in self.social_data.columns:
            # Análisis por tipo de contenido
            content_type_analysis = self.social_data.groupby('content_type').agg({
                'likes': 'sum',
                'comments': 'sum',
                'shares': 'sum',
                'reach': 'sum',
                'clicks': 'sum',
                'conversions': 'sum'
            }).reset_index()
            
            # Calcular métricas de performance
            content_type_analysis['engagement_rate'] = ((content_type_analysis['likes'] + content_type_analysis['comments'] + content_type_analysis['shares']) / content_type_analysis['reach']) * 100
            content_type_analysis['ctr'] = (content_type_analysis['clicks'] / content_type_analysis['reach']) * 100
            content_type_analysis['conversion_rate'] = (content_type_analysis['conversions'] / content_type_analysis['clicks']) * 100
            
            content_analysis['content_type_analysis'] = content_type_analysis.to_dict('records')
        
        # Análisis de contenido por tema
        if 'content_topic' in self.social_data.columns:
            topic_analysis = self.social_data.groupby('content_topic').agg({
                'likes': 'sum',
                'comments': 'sum',
                'shares': 'sum',
                'reach': 'sum',
                'clicks': 'sum',
                'conversions': 'sum'
            }).reset_index()
            
            # Calcular métricas de performance
            topic_analysis['engagement_rate'] = ((topic_analysis['likes'] + topic_analysis['comments'] + topic_analysis['shares']) / topic_analysis['reach']) * 100
            topic_analysis['ctr'] = (topic_analysis['clicks'] / topic_analysis['reach']) * 100
            topic_analysis['conversion_rate'] = (topic_analysis['conversions'] / topic_analysis['clicks']) * 100
            
            content_analysis['topic_analysis'] = topic_analysis.to_dict('records')
        
        # Análisis de contenido por formato
        if 'content_format' in self.social_data.columns:
            format_analysis = self.social_data.groupby('content_format').agg({
                'likes': 'sum',
                'comments': 'sum',
                'shares': 'sum',
                'reach': 'sum',
                'clicks': 'sum',
                'conversions': 'sum'
            }).reset_index()
            
            # Calcular métricas de performance
            format_analysis['engagement_rate'] = ((format_analysis['likes'] + format_analysis['comments'] + format_analysis['shares']) / format_analysis['reach']) * 100
            format_analysis['ctr'] = (format_analysis['clicks'] / format_analysis['reach']) * 100
            format_analysis['conversion_rate'] = (format_analysis['conversions'] / format_analysis['clicks']) * 100
            
            content_analysis['format_analysis'] = format_analysis.to_dict('records')
        
        # Análisis de timing de contenido
        timing_analysis = self._analyze_content_timing()
        content_analysis['timing_analysis'] = timing_analysis
        
        # Análisis de hashtags
        hashtag_analysis = self._analyze_hashtags()
        content_analysis['hashtag_analysis'] = hashtag_analysis
        
        self.content_analysis = content_analysis
        return content_analysis
    
    def _analyze_content_timing(self):
        """Analizar timing de contenido"""
        timing_analysis = {}
        
        if 'date' in self.social_data.columns:
            # Análisis de timing por hora del día
            self.social_data['hour'] = pd.to_datetime(self.social_data['date']).dt.hour
            hourly_analysis = self.social_data.groupby('hour').agg({
                'engagement_rate': 'mean',
                'reach': 'sum',
                'clicks': 'sum'
            }).reset_index()
            
            # Análisis de timing por día de la semana
            self.social_data['day_of_week'] = pd.to_datetime(self.social_data['date']).dt.day_name()
            daily_analysis = self.social_data.groupby('day_of_week').agg({
                'engagement_rate': 'mean',
                'reach': 'sum',
                'clicks': 'sum'
            }).reset_index()
            
            timing_analysis = {
                'hourly_analysis': hourly_analysis.to_dict('records'),
                'daily_analysis': daily_analysis.to_dict('records'),
                'best_hour': hourly_analysis.loc[hourly_analysis['engagement_rate'].idxmax(), 'hour'],
                'best_day': daily_analysis.loc[daily_analysis['engagement_rate'].idxmax(), 'day_of_week']
            }
        
        return timing_analysis
    
    def _analyze_hashtags(self):
        """Analizar hashtags"""
        hashtag_analysis = {}
        
        if 'hashtags' in self.social_data.columns:
            # Análisis de hashtags más efectivos
            hashtag_performance = {}
            
            for _, row in self.social_data.iterrows():
                hashtags = str(row['hashtags']).split(',')
                engagement_rate = row['engagement_rate']
                
                for hashtag in hashtags:
                    hashtag = hashtag.strip()
                    if hashtag:
                        if hashtag not in hashtag_performance:
                            hashtag_performance[hashtag] = []
                        hashtag_performance[hashtag].append(engagement_rate)
            
            # Calcular performance promedio por hashtag
            hashtag_avg_performance = {}
            for hashtag, rates in hashtag_performance.items():
                hashtag_avg_performance[hashtag] = {
                    'avg_engagement_rate': np.mean(rates),
                    'usage_count': len(rates),
                    'total_engagement': np.sum(rates)
                }
            
            # Ordenar por performance
            top_hashtags = sorted(hashtag_avg_performance.items(), key=lambda x: x[1]['avg_engagement_rate'], reverse=True)[:20]
            
            hashtag_analysis = {
                'top_hashtags': top_hashtags,
                'hashtag_performance': hashtag_avg_performance,
                'total_unique_hashtags': len(hashtag_avg_performance)
            }
        
        return hashtag_analysis
    
    def analyze_engagement_patterns(self):
        """Analizar patrones de engagement"""
        if self.social_data.empty:
            return None
        
        # Análisis de engagement por plataforma
        engagement_analysis = {}
        
        # Análisis de engagement por tipo de interacción
        interaction_analysis = self.social_data.groupby('platform').agg({
            'likes': 'sum',
            'comments': 'sum',
            'shares': 'sum',
            'reach': 'sum'
        }).reset_index()
        
        # Calcular ratios de engagement
        interaction_analysis['like_ratio'] = interaction_analysis['likes'] / interaction_analysis['reach']
        interaction_analysis['comment_ratio'] = interaction_analysis['comments'] / interaction_analysis['reach']
        interaction_analysis['share_ratio'] = interaction_analysis['shares'] / interaction_analysis['reach']
        
        engagement_analysis['interaction_analysis'] = interaction_analysis.to_dict('records')
        
        # Análisis de engagement por audiencia
        if 'audience_type' in self.social_data.columns:
            audience_engagement = self.social_data.groupby('audience_type').agg({
                'engagement_rate': 'mean',
                'reach': 'sum',
                'clicks': 'sum'
            }).reset_index()
            
            engagement_analysis['audience_engagement'] = audience_engagement.to_dict('records')
        
        # Análisis de engagement por contenido
        if 'content_type' in self.social_data.columns:
            content_engagement = self.social_data.groupby('content_type').agg({
                'engagement_rate': 'mean',
                'reach': 'sum',
                'clicks': 'sum'
            }).reset_index()
            
            engagement_analysis['content_engagement'] = content_engagement.to_dict('records')
        
        # Análisis de engagement por timing
        if 'date' in self.social_data.columns:
            timing_engagement = self._analyze_engagement_timing()
            engagement_analysis['timing_engagement'] = timing_engagement
        
        self.engagement_analysis = engagement_analysis
        return engagement_analysis
    
    def _analyze_engagement_timing(self):
        """Analizar timing de engagement"""
        timing_engagement = {}
        
        if 'date' in self.social_data.columns:
            # Análisis de engagement por hora del día
            self.social_data['hour'] = pd.to_datetime(self.social_data['date']).dt.hour
            hourly_engagement = self.social_data.groupby('hour').agg({
                'engagement_rate': 'mean',
                'likes': 'sum',
                'comments': 'sum',
                'shares': 'sum'
            }).reset_index()
            
            # Análisis de engagement por día de la semana
            self.social_data['day_of_week'] = pd.to_datetime(self.social_data['date']).dt.day_name()
            daily_engagement = self.social_data.groupby('day_of_week').agg({
                'engagement_rate': 'mean',
                'likes': 'sum',
                'comments': 'sum',
                'shares': 'sum'
            }).reset_index()
            
            timing_engagement = {
                'hourly_engagement': hourly_engagement.to_dict('records'),
                'daily_engagement': daily_engagement.to_dict('records'),
                'peak_engagement_hour': hourly_engagement.loc[hourly_engagement['engagement_rate'].idxmax(), 'hour'],
                'peak_engagement_day': daily_engagement.loc[daily_engagement['engagement_rate'].idxmax(), 'day_of_week']
            }
        
        return timing_engagement
    
    def build_social_prediction_model(self, target_variable='engagement_rate'):
        """Construir modelo de predicción de social media"""
        if target_variable not in self.social_data.columns:
            raise ValueError(f"Variable objetivo '{target_variable}' no encontrada")
        
        # Preparar datos
        feature_columns = [col for col in self.social_data.columns if col != target_variable and col not in ['date', 'hashtags']]
        X = self.social_data[feature_columns]
        y = self.social_data[target_variable]
        
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
        self.social_models['social_predictor'] = {
            'model': model,
            'label_encoders': label_encoders,
            'feature_columns': feature_columns,
            'scaler': scaler,
            'metrics': model_metrics
        }
        
        return model_metrics
    
    def optimize_social_strategies(self):
        """Optimizar estrategias de social media"""
        strategies = []
        
        # Estrategias basadas en análisis de plataformas
        if self.platform_analysis:
            efficiency_analysis = self.platform_analysis.get('efficiency_analysis', {})
            efficiency_categories = efficiency_analysis.get('efficiency_categories', {})
            
            # Estrategias para plataformas de alta eficiencia
            high_efficiency_platforms = efficiency_categories.get('high_efficiency', [])
            if high_efficiency_platforms:
                strategies.append({
                    'strategy_type': 'Scale High Efficiency Platforms',
                    'description': f'Escalar plataformas de alta eficiencia: {", ".join(high_efficiency_platforms)}',
                    'priority': 'high',
                    'expected_impact': 'high'
                })
            
            # Estrategias para plataformas de baja eficiencia
            low_efficiency_platforms = efficiency_categories.get('low_efficiency', [])
            if low_efficiency_platforms:
                strategies.append({
                    'strategy_type': 'Optimize Low Efficiency Platforms',
                    'description': f'Optimizar plataformas de baja eficiencia: {", ".join(low_efficiency_platforms)}',
                    'priority': 'medium',
                    'expected_impact': 'medium'
                })
        
        # Estrategias basadas en análisis de contenido
        if self.content_analysis:
            content_type_analysis = self.content_analysis.get('content_type_analysis', [])
            
            if content_type_analysis:
                # Identificar tipo de contenido más efectivo
                best_content_type = max(content_type_analysis, key=lambda x: x['engagement_rate'])
                strategies.append({
                    'strategy_type': 'Content Optimization',
                    'description': f'Aumentar contenido de tipo: {best_content_type["content_type"]}',
                    'priority': 'medium',
                    'expected_impact': 'medium'
                })
            
            # Estrategias basadas en timing
            timing_analysis = self.content_analysis.get('timing_analysis', {})
            if timing_analysis:
                best_hour = timing_analysis.get('best_hour')
                best_day = timing_analysis.get('best_day')
                
                if best_hour and best_day:
                    strategies.append({
                        'strategy_type': 'Timing Optimization',
                        'description': f'Publicar en {best_day} a las {best_hour}:00 para máximo engagement',
                        'priority': 'medium',
                        'expected_impact': 'medium'
                    })
        
        # Estrategias basadas en análisis de engagement
        if self.engagement_analysis:
            interaction_analysis = self.engagement_analysis.get('interaction_analysis', [])
            
            if interaction_analysis:
                # Identificar plataforma con mejor engagement
                best_platform = max(interaction_analysis, key=lambda x: x['engagement_rate'])
                strategies.append({
                    'strategy_type': 'Engagement Optimization',
                    'description': f'Focalizar en {best_platform["platform"]} para máximo engagement',
                    'priority': 'high',
                    'expected_impact': 'high'
                })
        
        # Estrategias basadas en hashtags
        if self.content_analysis:
            hashtag_analysis = self.content_analysis.get('hashtag_analysis', {})
            top_hashtags = hashtag_analysis.get('top_hashtags', [])
            
            if top_hashtags:
                top_hashtag = top_hashtags[0][0]
                strategies.append({
                    'strategy_type': 'Hashtag Optimization',
                    'description': f'Usar más el hashtag #{top_hashtag} para mejor engagement',
                    'priority': 'low',
                    'expected_impact': 'low'
                })
        
        self.optimization_strategies = strategies
        return strategies
    
    def generate_social_insights(self):
        """Generar insights de social media"""
        insights = []
        
        # Insights de plataformas
        if self.platform_analysis:
            overall_engagement_rate = self.platform_analysis.get('overall_engagement_rate', 0)
            
            if overall_engagement_rate < 2:
                insights.append({
                    'category': 'Platform Performance',
                    'insight': f'Engagement rate general bajo: {overall_engagement_rate:.1f}%',
                    'recommendation': 'Mejorar engagement en todas las plataformas',
                    'priority': 'high'
                })
            
            efficiency_analysis = self.platform_analysis.get('efficiency_analysis', {})
            efficiency_categories = efficiency_analysis.get('efficiency_categories', {})
            
            low_efficiency_count = len(efficiency_categories.get('low_efficiency', []))
            if low_efficiency_count > 0:
                insights.append({
                    'category': 'Platform Efficiency',
                    'insight': f'{low_efficiency_count} plataformas con baja eficiencia',
                    'recommendation': 'Optimizar plataformas de baja eficiencia',
                    'priority': 'medium'
                })
        
        # Insights de contenido
        if self.content_analysis:
            content_type_analysis = self.content_analysis.get('content_type_analysis', [])
            
            if content_type_analysis:
                # Identificar tipo de contenido con mejor performance
                best_content = max(content_type_analysis, key=lambda x: x['engagement_rate'])
                insights.append({
                    'category': 'Content Performance',
                    'insight': f'Mejor tipo de contenido: {best_content["content_type"]} con {best_content["engagement_rate"]:.1f}% engagement',
                    'recommendation': 'Aumentar producción de este tipo de contenido',
                    'priority': 'medium'
                })
        
        # Insights de engagement
        if self.engagement_analysis:
            interaction_analysis = self.engagement_analysis.get('interaction_analysis', [])
            
            if interaction_analysis:
                # Analizar ratios de interacción
                for platform in interaction_analysis:
                    like_ratio = platform.get('like_ratio', 0)
                    comment_ratio = platform.get('comment_ratio', 0)
                    share_ratio = platform.get('share_ratio', 0)
                    
                    if comment_ratio < 0.01:  # Menos del 1% de comentarios
                        insights.append({
                            'category': 'Engagement Patterns',
                            'insight': f'Bajo ratio de comentarios en {platform["platform"]}: {comment_ratio:.3f}',
                            'recommendation': 'Crear contenido que genere más comentarios',
                            'priority': 'medium'
                        })
        
        # Insights de timing
        if self.content_analysis:
            timing_analysis = self.content_analysis.get('timing_analysis', {})
            best_hour = timing_analysis.get('best_hour')
            best_day = timing_analysis.get('best_day')
            
            if best_hour and best_day:
                insights.append({
                    'category': 'Content Timing',
                    'insight': f'Mejor momento para publicar: {best_day} a las {best_hour}:00',
                    'recommendation': 'Optimizar horarios de publicación',
                    'priority': 'low'
                })
        
        self.social_insights = insights
        return insights
    
    def create_social_dashboard(self):
        """Crear dashboard de social media"""
        if not self.social_data.empty:
            return None
        
        # Crear subplots
        fig = make_subplots(
            rows=2, cols=2,
            subplot_titles=('Platform Performance', 'Content Performance',
                          'Engagement Analysis', 'Timing Analysis'),
            specs=[[{"type": "bar"}, {"type": "pie"}],
                   [{"type": "bar"}, {"type": "scatter"}]]
        )
        
        # Gráfico de performance de plataformas
        if self.platform_analysis:
            platform_analysis = self.platform_analysis.get('platform_analysis', [])
            if platform_analysis:
                platforms = [platform['platform'] for platform in platform_analysis]
                engagement_rates = [platform['engagement_rate'] for platform in platform_analysis]
                
                fig.add_trace(
                    go.Bar(x=platforms, y=engagement_rates, name='Platform Engagement Rate'),
                    row=1, col=1
                )
        
        # Gráfico de performance de contenido
        if self.content_analysis:
            content_type_analysis = self.content_analysis.get('content_type_analysis', [])
            if content_type_analysis:
                content_types = [content['content_type'] for content in content_type_analysis]
                engagement_rates = [content['engagement_rate'] for content in content_type_analysis]
                
                fig.add_trace(
                    go.Pie(labels=content_types, values=engagement_rates, name='Content Performance'),
                    row=1, col=2
                )
        
        # Gráfico de análisis de engagement
        if self.engagement_analysis:
            interaction_analysis = self.engagement_analysis.get('interaction_analysis', [])
            if interaction_analysis:
                platforms = [platform['platform'] for platform in interaction_analysis]
                like_ratios = [platform['like_ratio'] for platform in interaction_analysis]
                
                fig.add_trace(
                    go.Bar(x=platforms, y=like_ratios, name='Like Ratios'),
                    row=2, col=1
                )
        
        # Gráfico de análisis de timing
        if self.content_analysis:
            timing_analysis = self.content_analysis.get('timing_analysis', {})
            hourly_analysis = timing_analysis.get('hourly_analysis', [])
            
            if hourly_analysis:
                hours = [data['hour'] for data in hourly_analysis]
                engagement_rates = [data['engagement_rate'] for data in hourly_analysis]
                
                fig.add_trace(
                    go.Scatter(x=hours, y=engagement_rates, mode='lines+markers', name='Hourly Engagement'),
                    row=2, col=2
                )
        
        fig.update_layout(
            title="Dashboard de Social Media Marketing",
            showlegend=False,
            height=800
        )
        
        return fig
    
    def export_social_analysis(self, filename='social_media_optimization_analysis.json'):
        """Exportar análisis de social media"""
        export_data = {
            'timestamp': datetime.now().isoformat(),
            'platform_analysis': self.platform_analysis,
            'content_analysis': self.content_analysis,
            'engagement_analysis': self.engagement_analysis,
            'social_models': {k: {'metrics': v['metrics']} for k, v in self.social_models.items()},
            'optimization_strategies': self.optimization_strategies,
            'social_insights': self.social_insights,
            'summary': {
                'total_platforms': len(self.social_data['platform'].unique()) if 'platform' in self.social_data.columns else 0,
                'total_posts': self.social_data['posts'].sum() if 'posts' in self.social_data.columns else 0,
                'analysis_date': datetime.now().isoformat()
            }
        }
        
        with open(filename, 'w') as f:
            json.dump(export_data, f, indent=2, default=str)
        
        print(f"✅ Análisis de social media exportado a {filename}")
        return export_data

# Ejemplo de uso
if __name__ == "__main__":
    # Crear instancia del optimizador de social media
    social_optimizer = SocialMediaOptimizer()
    
    # Datos de ejemplo
    sample_data = pd.DataFrame({
        'platform': np.random.choice(['Facebook', 'Instagram', 'Twitter', 'LinkedIn', 'TikTok'], 1000),
        'followers': np.random.poisson(10000, 1000),
        'posts': np.random.poisson(50, 1000),
        'likes': np.random.poisson(500, 1000),
        'comments': np.random.poisson(50, 1000),
        'shares': np.random.poisson(100, 1000),
        'reach': np.random.poisson(5000, 1000),
        'impressions': np.random.poisson(8000, 1000),
        'clicks': np.random.poisson(200, 1000),
        'conversions': np.random.poisson(20, 1000),
        'cost': np.random.normal(500, 100, 1000),
        'engagement_rate': np.random.uniform(1, 10, 1000),
        'content_type': np.random.choice(['Image', 'Video', 'Text', 'Carousel'], 1000),
        'content_topic': np.random.choice(['Product', 'Lifestyle', 'Educational', 'Entertainment'], 1000),
        'content_format': np.random.choice(['Post', 'Story', 'Reel', 'IGTV'], 1000),
        'hashtags': np.random.choice(['#marketing', '#socialmedia', '#business', '#growth'], 1000),
        'audience_demographics': np.random.choice(['Gen Z', 'Millennials', 'Gen X'], 1000),
        'audience_type': np.random.choice(['Followers', 'Non-followers'], 1000),
        'date': pd.date_range('2023-01-01', periods=1000, freq='D')
    })
    
    # Cargar datos de social media
    print("📊 Cargando datos de social media...")
    social_optimizer.load_social_data(sample_data)
    
    # Analizar plataformas de social media
    print("📱 Analizando plataformas de social media...")
    platform_analysis = social_optimizer.analyze_social_platforms()
    
    # Analizar performance de contenido
    print("📝 Analizando performance de contenido...")
    content_analysis = social_optimizer.analyze_content_performance()
    
    # Analizar patrones de engagement
    print("💬 Analizando patrones de engagement...")
    engagement_analysis = social_optimizer.analyze_engagement_patterns()
    
    # Construir modelo de predicción de social media
    print("🔮 Construyendo modelo de predicción de social media...")
    social_model = social_optimizer.build_social_prediction_model()
    
    # Optimizar estrategias de social media
    print("🎯 Optimizando estrategias de social media...")
    social_strategies = social_optimizer.optimize_social_strategies()
    
    # Generar insights de social media
    print("💡 Generando insights de social media...")
    social_insights = social_optimizer.generate_social_insights()
    
    # Crear dashboard
    print("📊 Creando dashboard de social media...")
    dashboard = social_optimizer.create_social_dashboard()
    
    # Exportar análisis
    print("💾 Exportando análisis de social media...")
    export_data = social_optimizer.export_social_analysis()
    
    print("✅ Sistema de optimización de social media completado!")




