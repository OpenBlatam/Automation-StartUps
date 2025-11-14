"""
Marketing Brain Influence & Advocacy Analyzer
Sistema avanzado de análisis de influencia y advocacy
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
import networkx as nx
import warnings
warnings.filterwarnings('ignore')

class InfluenceAdvocacyAnalyzer:
    def __init__(self):
        self.influence_data = {}
        self.advocacy_analysis = {}
        self.influencer_network = {}
        self.advocacy_segments = {}
        self.influence_models = {}
        self.viral_analysis = {}
        self.advocacy_insights = {}
        
    def load_influence_data(self, influence_data):
        """Cargar datos de influencia y advocacy"""
        if isinstance(influence_data, str):
            if influence_data.endswith('.csv'):
                self.influence_data = pd.read_csv(influence_data)
            elif influence_data.endswith('.json'):
                with open(influence_data, 'r') as f:
                    data = json.load(f)
                self.influence_data = pd.DataFrame(data)
        else:
            self.influence_data = pd.DataFrame(influence_data)
        
        print(f"✅ Datos de influencia cargados: {len(self.influence_data)} registros")
        return True
    
    def analyze_influencer_network(self):
        """Analizar red de influenciadores"""
        if self.influence_data.empty:
            return None
        
        # Crear grafo de red
        G = nx.Graph()
        
        # Agregar nodos (usuarios)
        users = self.influence_data['user_id'].unique()
        G.add_nodes_from(users)
        
        # Agregar edges (conexiones)
        for _, row in self.influence_data.iterrows():
            if 'connected_to' in row and pd.notna(row['connected_to']):
                G.add_edge(row['user_id'], row['connected_to'])
        
        # Calcular métricas de red
        network_metrics = {
            'total_nodes': G.number_of_nodes(),
            'total_edges': G.number_of_edges(),
            'density': nx.density(G),
            'average_clustering': nx.average_clustering(G),
            'connected_components': nx.number_connected_components(G)
        }
        
        # Análisis de centralidad
        centrality_analysis = self._analyze_centrality(G)
        
        # Análisis de comunidades
        community_analysis = self._analyze_communities(G)
        
        # Análisis de influencia
        influence_analysis = self._analyze_influence_metrics()
        
        network_results = {
            'network_metrics': network_metrics,
            'centrality_analysis': centrality_analysis,
            'community_analysis': community_analysis,
            'influence_analysis': influence_analysis,
            'top_influencers': self._identify_top_influencers(centrality_analysis, influence_analysis)
        }
        
        self.influencer_network = network_results
        return network_results
    
    def _analyze_centrality(self, G):
        """Analizar centralidad de la red"""
        centrality_metrics = {}
        
        # Degree centrality
        degree_centrality = nx.degree_centrality(G)
        centrality_metrics['degree_centrality'] = degree_centrality
        
        # Betweenness centrality
        betweenness_centrality = nx.betweenness_centrality(G)
        centrality_metrics['betweenness_centrality'] = betweenness_centrality
        
        # Closeness centrality
        closeness_centrality = nx.closeness_centrality(G)
        centrality_metrics['closeness_centrality'] = closeness_centrality
        
        # Eigenvector centrality
        try:
            eigenvector_centrality = nx.eigenvector_centrality(G)
            centrality_metrics['eigenvector_centrality'] = eigenvector_centrality
        except:
            centrality_metrics['eigenvector_centrality'] = {}
        
        return centrality_metrics
    
    def _analyze_communities(self, G):
        """Analizar comunidades en la red"""
        try:
            # Usar algoritmo de detección de comunidades
            communities = nx.community.greedy_modularity_communities(G)
            
            community_analysis = {
                'number_of_communities': len(communities),
                'modularity': nx.community.modularity(G, communities),
                'community_sizes': [len(community) for community in communities],
                'largest_community_size': max([len(community) for community in communities]) if communities else 0
            }
            
            # Análisis de cada comunidad
            community_details = []
            for i, community in enumerate(communities):
                community_data = {
                    'community_id': i,
                    'size': len(community),
                    'members': list(community),
                    'avg_influence': np.mean([self._get_user_influence_score(user) for user in community])
                }
                community_details.append(community_data)
            
            community_analysis['community_details'] = community_details
            
        except Exception as e:
            community_analysis = {
                'number_of_communities': 0,
                'modularity': 0,
                'community_sizes': [],
                'largest_community_size': 0,
                'community_details': []
            }
        
        return community_analysis
    
    def _get_user_influence_score(self, user_id):
        """Obtener score de influencia de un usuario"""
        user_data = self.influence_data[self.influence_data['user_id'] == user_id]
        if user_data.empty:
            return 0
        
        # Calcular score de influencia basado en métricas
        influence_score = 0
        
        if 'followers' in user_data.columns:
            influence_score += user_data['followers'].mean() * 0.3
        
        if 'engagement_rate' in user_data.columns:
            influence_score += user_data['engagement_rate'].mean() * 100 * 0.4
        
        if 'content_quality' in user_data.columns:
            influence_score += user_data['content_quality'].mean() * 0.3
        
        return influence_score
    
    def _analyze_influence_metrics(self):
        """Analizar métricas de influencia"""
        influence_metrics = {}
        
        # Análisis de followers
        if 'followers' in self.influence_data.columns:
            influence_metrics['followers_analysis'] = {
                'avg_followers': self.influence_data['followers'].mean(),
                'median_followers': self.influence_data['followers'].median(),
                'max_followers': self.influence_data['followers'].max(),
                'followers_distribution': self._categorize_followers()
            }
        
        # Análisis de engagement
        if 'engagement_rate' in self.influence_data.columns:
            influence_metrics['engagement_analysis'] = {
                'avg_engagement': self.influence_data['engagement_rate'].mean(),
                'median_engagement': self.influence_data['engagement_rate'].median(),
                'high_engagement_users': len(self.influence_data[self.influence_data['engagement_rate'] > 0.05])
            }
        
        # Análisis de contenido
        if 'content_quality' in self.influence_data.columns:
            influence_metrics['content_analysis'] = {
                'avg_content_quality': self.influence_data['content_quality'].mean(),
                'high_quality_content_users': len(self.influence_data[self.influence_data['content_quality'] > 4.0])
            }
        
        return influence_metrics
    
    def _categorize_followers(self):
        """Categorizar usuarios por número de followers"""
        if 'followers' not in self.influence_data.columns:
            return {}
        
        followers = self.influence_data['followers']
        
        categories = {
            'nano_influencers': len(followers[(followers >= 1000) & (followers < 10000)]),
            'micro_influencers': len(followers[(followers >= 10000) & (followers < 100000)]),
            'macro_influencers': len(followers[(followers >= 100000) & (followers < 1000000)]),
            'mega_influencers': len(followers[followers >= 1000000])
        }
        
        return categories
    
    def _identify_top_influencers(self, centrality_analysis, influence_analysis):
        """Identificar top influenciadores"""
        top_influencers = []
        
        # Combinar métricas de centralidad e influencia
        for user_id in self.influence_data['user_id'].unique():
            user_data = self.influence_data[self.influence_data['user_id'] == user_id]
            
            # Calcular score combinado
            combined_score = 0
            
            # Score de centralidad
            degree_centrality = centrality_analysis.get('degree_centrality', {}).get(user_id, 0)
            betweenness_centrality = centrality_analysis.get('betweenness_centrality', {}).get(user_id, 0)
            eigenvector_centrality = centrality_analysis.get('eigenvector_centrality', {}).get(user_id, 0)
            
            combined_score += degree_centrality * 0.3
            combined_score += betweenness_centrality * 0.3
            combined_score += eigenvector_centrality * 0.4
            
            # Score de influencia
            influence_score = self._get_user_influence_score(user_id)
            combined_score += influence_score * 0.1
            
            top_influencers.append({
                'user_id': user_id,
                'combined_score': combined_score,
                'degree_centrality': degree_centrality,
                'betweenness_centrality': betweenness_centrality,
                'eigenvector_centrality': eigenvector_centrality,
                'influence_score': influence_score
            })
        
        # Ordenar por score combinado
        top_influencers.sort(key=lambda x: x['combined_score'], reverse=True)
        
        return top_influencers[:20]  # Top 20 influenciadores
    
    def analyze_advocacy_behavior(self):
        """Analizar comportamiento de advocacy"""
        if self.influence_data.empty:
            return None
        
        # Análisis de advocacy por usuario
        advocacy_analysis = {}
        
        for user_id in self.influence_data['user_id'].unique():
            user_data = self.influence_data[self.influence_data['user_id'] == user_id]
            
            # Calcular métricas de advocacy
            advocacy_score = 0
            
            if 'recommendations' in user_data.columns:
                advocacy_score += user_data['recommendations'].sum() * 0.3
            
            if 'shares' in user_data.columns:
                advocacy_score += user_data['shares'].sum() * 0.2
            
            if 'mentions' in user_data.columns:
                advocacy_score += user_data['mentions'].sum() * 0.2
            
            if 'reviews' in user_data.columns:
                advocacy_score += user_data['reviews'].sum() * 0.3
            
            advocacy_analysis[user_id] = {
                'advocacy_score': advocacy_score,
                'recommendations': user_data['recommendations'].sum() if 'recommendations' in user_data.columns else 0,
                'shares': user_data['shares'].sum() if 'shares' in user_data.columns else 0,
                'mentions': user_data['mentions'].sum() if 'mentions' in user_data.columns else 0,
                'reviews': user_data['reviews'].sum() if 'reviews' in user_data.columns else 0
            }
        
        # Análisis de segmentos de advocacy
        advocacy_segments = self._analyze_advocacy_segments(advocacy_analysis)
        
        # Análisis de viralidad
        viral_analysis = self._analyze_viral_behavior()
        
        advocacy_results = {
            'advocacy_analysis': advocacy_analysis,
            'advocacy_segments': advocacy_segments,
            'viral_analysis': viral_analysis,
            'top_advocates': self._identify_top_advocates(advocacy_analysis)
        }
        
        self.advocacy_analysis = advocacy_results
        return advocacy_results
    
    def _analyze_advocacy_segments(self, advocacy_analysis):
        """Analizar segmentos de advocacy"""
        advocacy_scores = [data['advocacy_score'] for data in advocacy_analysis.values()]
        
        # Crear segmentos basados en score de advocacy
        segments = {
            'champions': len([score for score in advocacy_scores if score > 100]),
            'advocates': len([score for score in advocacy_scores if 50 < score <= 100]),
            'supporters': len([score for score in advocacy_scores if 20 < score <= 50]),
            'neutrals': len([score for score in advocacy_scores if 5 < score <= 20]),
            'detractors': len([score for score in advocacy_scores if score <= 5])
        }
        
        return segments
    
    def _analyze_viral_behavior(self):
        """Analizar comportamiento viral"""
        viral_analysis = {}
        
        # Análisis de contenido viral
        if 'viral_coefficient' in self.influence_data.columns:
            viral_analysis['viral_coefficient'] = {
                'avg_viral_coefficient': self.influence_data['viral_coefficient'].mean(),
                'high_viral_content': len(self.influence_data[self.influence_data['viral_coefficient'] > 2.0]),
                'viral_distribution': self._analyze_viral_distribution()
            }
        
        # Análisis de reach
        if 'reach' in self.influence_data.columns:
            viral_analysis['reach_analysis'] = {
                'avg_reach': self.influence_data['reach'].mean(),
                'total_reach': self.influence_data['reach'].sum(),
                'reach_growth': self._analyze_reach_growth()
            }
        
        return viral_analysis
    
    def _analyze_viral_distribution(self):
        """Analizar distribución de contenido viral"""
        if 'viral_coefficient' not in self.influence_data.columns:
            return {}
        
        viral_coeff = self.influence_data['viral_coefficient']
        
        distribution = {
            'low_viral': len(viral_coeff[viral_coeff < 1.0]),
            'medium_viral': len(viral_coeff[(viral_coeff >= 1.0) & (viral_coeff < 2.0)]),
            'high_viral': len(viral_coeff[(viral_coeff >= 2.0) & (viral_coeff < 5.0)]),
            'super_viral': len(viral_coeff[viral_coeff >= 5.0])
        }
        
        return distribution
    
    def _analyze_reach_growth(self):
        """Analizar crecimiento de reach"""
        if 'reach' not in self.influence_data.columns or 'date' not in self.influence_data.columns:
            return {}
        
        # Análisis de crecimiento temporal
        self.influence_data['date'] = pd.to_datetime(self.influence_data['date'])
        self.influence_data['month'] = self.influence_data['date'].dt.to_period('M')
        
        monthly_reach = self.influence_data.groupby('month')['reach'].sum()
        
        if len(monthly_reach) > 1:
            growth_rate = ((monthly_reach.iloc[-1] - monthly_reach.iloc[0]) / monthly_reach.iloc[0]) * 100
        else:
            growth_rate = 0
        
        return {
            'monthly_reach': monthly_reach.to_dict(),
            'growth_rate': growth_rate
        }
    
    def _identify_top_advocates(self, advocacy_analysis):
        """Identificar top advocates"""
        top_advocates = []
        
        for user_id, data in advocacy_analysis.items():
            top_advocates.append({
                'user_id': user_id,
                'advocacy_score': data['advocacy_score'],
                'recommendations': data['recommendations'],
                'shares': data['shares'],
                'mentions': data['mentions'],
                'reviews': data['reviews']
            })
        
        # Ordenar por score de advocacy
        top_advocates.sort(key=lambda x: x['advocacy_score'], reverse=True)
        
        return top_advocates[:20]  # Top 20 advocates
    
    def build_influence_prediction_model(self, target_variable='influence_score'):
        """Construir modelo de predicción de influencia"""
        if target_variable not in self.influence_data.columns:
            # Crear variable objetivo si no existe
            self.influence_data[target_variable] = self.influence_data.apply(
                lambda row: self._get_user_influence_score(row['user_id']), axis=1
            )
        
        # Preparar datos
        feature_columns = [col for col in self.influence_data.columns if col != target_variable and col != 'user_id']
        X = self.influence_data[feature_columns]
        y = self.influence_data[target_variable]
        
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
        self.influence_models['influence_predictor'] = {
            'model': model,
            'label_encoders': label_encoders,
            'feature_columns': feature_columns,
            'scaler': scaler,
            'metrics': model_metrics
        }
        
        return model_metrics
    
    def predict_influence_potential(self, user_data):
        """Predecir potencial de influencia"""
        if 'influence_predictor' not in self.influence_models:
            raise ValueError("Modelo de predicción de influencia no encontrado")
        
        model_info = self.influence_models['influence_predictor']
        model = model_info['model']
        feature_columns = model_info['feature_columns']
        label_encoders = model_info['label_encoders']
        scaler = model_info['scaler']
        
        # Preparar datos
        X = user_data[feature_columns]
        
        # Codificar variables categóricas
        for column in X.select_dtypes(include=['object']).columns:
            if column in label_encoders:
                le = label_encoders[column]
                X[column] = le.transform(X[column].astype(str))
        
        # Escalar datos
        X_scaled = scaler.transform(X)
        
        # Predecir influencia
        influence_predictions = model.predict(X_scaled)
        
        return influence_predictions
    
    def generate_advocacy_insights(self):
        """Generar insights de advocacy"""
        insights = []
        
        # Insights de red de influenciadores
        if self.influencer_network:
            network_metrics = self.influencer_network.get('network_metrics', {})
            density = network_metrics.get('density', 0)
            
            if density < 0.1:
                insights.append({
                    'category': 'Network Analysis',
                    'insight': f'Densidad de red baja: {density:.3f}',
                    'recommendation': 'Fomentar conexiones entre influenciadores',
                    'priority': 'medium'
                })
            
            top_influencers = self.influencer_network.get('top_influencers', [])
            if top_influencers:
                insights.append({
                    'category': 'Influencer Identification',
                    'insight': f'{len(top_influencers)} top influenciadores identificados',
                    'recommendation': 'Desarrollar estrategias de colaboración con top influenciadores',
                    'priority': 'high'
                })
        
        # Insights de advocacy
        if self.advocacy_analysis:
            advocacy_segments = self.advocacy_analysis.get('advocacy_segments', {})
            champions = advocacy_segments.get('champions', 0)
            total_users = sum(advocacy_segments.values())
            
            if champions > 0 and total_users > 0:
                champion_percentage = champions / total_users * 100
                if champion_percentage < 5:
                    insights.append({
                        'category': 'Advocacy',
                        'insight': f'Solo {champion_percentage:.1f}% de usuarios son champions',
                        'recommendation': 'Implementar programa de advocacy para aumentar champions',
                        'priority': 'high'
                    })
        
        # Insights de viralidad
        if self.advocacy_analysis:
            viral_analysis = self.advocacy_analysis.get('viral_analysis', {})
            viral_coeff = viral_analysis.get('viral_coefficient', {})
            
            if viral_coeff:
                avg_viral = viral_coeff.get('avg_viral_coefficient', 0)
                if avg_viral < 1.0:
                    insights.append({
                        'category': 'Viral Content',
                        'insight': f'Coeficiente viral promedio bajo: {avg_viral:.2f}',
                        'recommendation': 'Mejorar estrategias de contenido viral',
                        'priority': 'medium'
                    })
        
        self.advocacy_insights = insights
        return insights
    
    def create_influence_dashboard(self):
        """Crear dashboard de análisis de influencia"""
        if not self.influence_data.empty:
            return None
        
        # Crear subplots
        fig = make_subplots(
            rows=2, cols=2,
            subplot_titles=('Influencer Network', 'Advocacy Segments',
                          'Viral Content Analysis', 'Top Influencers'),
            specs=[[{"type": "scatter"}, {"type": "pie"}],
                   [{"type": "bar"}, {"type": "bar"}]]
        )
        
        # Gráfico de red de influenciadores
        if self.influencer_network:
            network_metrics = self.influencer_network.get('network_metrics', {})
            centrality_analysis = self.influencer_network.get('centrality_analysis', {})
            
            if centrality_analysis:
                degree_centrality = centrality_analysis.get('degree_centrality', {})
                if degree_centrality:
                    users = list(degree_centrality.keys())
                    centrality_values = list(degree_centrality.values())
                    
                    fig.add_trace(
                        go.Scatter(x=users, y=centrality_values, mode='markers', name='Degree Centrality'),
                        row=1, col=1
                    )
        
        # Gráfico de segmentos de advocacy
        if self.advocacy_analysis:
            advocacy_segments = self.advocacy_analysis.get('advocacy_segments', {})
            if advocacy_segments:
                segments = list(advocacy_segments.keys())
                values = list(advocacy_segments.values())
                
                fig.add_trace(
                    go.Pie(labels=segments, values=values, name='Advocacy Segments'),
                    row=1, col=2
                )
        
        # Gráfico de análisis de contenido viral
        if self.advocacy_analysis:
            viral_analysis = self.advocacy_analysis.get('viral_analysis', {})
            viral_dist = viral_analysis.get('viral_coefficient', {}).get('viral_distribution', {})
            if viral_dist:
                categories = list(viral_dist.keys())
                counts = list(viral_dist.values())
                
                fig.add_trace(
                    go.Bar(x=categories, y=counts, name='Viral Content Distribution'),
                    row=2, col=1
                )
        
        # Gráfico de top influenciadores
        if self.influencer_network:
            top_influencers = self.influencer_network.get('top_influencers', [])
            if top_influencers:
                user_ids = [inf['user_id'] for inf in top_influencers[:10]]
                scores = [inf['combined_score'] for inf in top_influencers[:10]]
                
                fig.add_trace(
                    go.Bar(x=user_ids, y=scores, name='Top Influencers'),
                    row=2, col=2
                )
        
        fig.update_layout(
            title="Dashboard de Análisis de Influencia y Advocacy",
            showlegend=False,
            height=800
        )
        
        return fig
    
    def export_influence_analysis(self, filename='influence_advocacy_analysis.json'):
        """Exportar análisis de influencia y advocacy"""
        export_data = {
            'timestamp': datetime.now().isoformat(),
            'influencer_network': self.influencer_network,
            'advocacy_analysis': self.advocacy_analysis,
            'influence_models': {k: {'metrics': v['metrics']} for k, v in self.influence_models.items()},
            'advocacy_insights': self.advocacy_insights,
            'summary': {
                'total_users': len(self.influence_data['user_id'].unique()) if 'user_id' in self.influence_data.columns else 0,
                'analysis_date': datetime.now().isoformat()
            }
        }
        
        with open(filename, 'w') as f:
            json.dump(export_data, f, indent=2, default=str)
        
        print(f"✅ Análisis de influencia exportado a {filename}")
        return export_data

# Ejemplo de uso
if __name__ == "__main__":
    # Crear instancia del analizador de influencia
    influence_analyzer = InfluenceAdvocacyAnalyzer()
    
    # Datos de ejemplo
    sample_data = pd.DataFrame({
        'user_id': np.random.randint(1, 500, 1000),
        'connected_to': np.random.randint(1, 500, 1000),
        'followers': np.random.poisson(10000, 1000),
        'engagement_rate': np.random.uniform(0.01, 0.1, 1000),
        'content_quality': np.random.uniform(1, 5, 1000),
        'recommendations': np.random.poisson(5, 1000),
        'shares': np.random.poisson(10, 1000),
        'mentions': np.random.poisson(3, 1000),
        'reviews': np.random.poisson(2, 1000),
        'viral_coefficient': np.random.uniform(0.5, 3.0, 1000),
        'reach': np.random.poisson(5000, 1000),
        'date': pd.date_range('2023-01-01', periods=1000, freq='D')
    })
    
    # Cargar datos de influencia
    print("📊 Cargando datos de influencia...")
    influence_analyzer.load_influence_data(sample_data)
    
    # Analizar red de influenciadores
    print("🕸️ Analizando red de influenciadores...")
    network_analysis = influence_analyzer.analyze_influencer_network()
    
    # Analizar comportamiento de advocacy
    print("💬 Analizando comportamiento de advocacy...")
    advocacy_analysis = influence_analyzer.analyze_advocacy_behavior()
    
    # Construir modelo de predicción de influencia
    print("🔮 Construyendo modelo de predicción de influencia...")
    influence_model = influence_analyzer.build_influence_prediction_model()
    
    # Generar insights de advocacy
    print("💡 Generando insights de advocacy...")
    advocacy_insights = influence_analyzer.generate_advocacy_insights()
    
    # Crear dashboard
    print("📊 Creando dashboard de influencia...")
    dashboard = influence_analyzer.create_influence_dashboard()
    
    # Exportar análisis
    print("💾 Exportando análisis de influencia...")
    export_data = influence_analyzer.export_influence_analysis()
    
    print("✅ Sistema de análisis de influencia y advocacy completado!")






