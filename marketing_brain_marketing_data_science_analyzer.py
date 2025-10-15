"""
Marketing Brain Marketing Data Science Analyzer
Sistema avanzado de análisis de data science de marketing
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import json
from sklearn.ensemble import RandomForestClassifier, GradientBoostingRegressor, IsolationForest
from sklearn.model_selection import train_test_split, cross_val_score, GridSearchCV
from sklearn.preprocessing import StandardScaler, LabelEncoder, MinMaxScaler
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, classification_report, confusion_matrix
from sklearn.cluster import KMeans, DBSCAN, AgglomerativeClustering
from sklearn.decomposition import PCA, FactorAnalysis, FastICA
from sklearn.feature_selection import SelectKBest, RFE, SelectFromModel
from sklearn.linear_model import LinearRegression, LogisticRegression, Ridge, Lasso
from sklearn.svm import SVC, SVR
from sklearn.neural_network import MLPClassifier, MLPRegressor
from sklearn.tree import DecisionTreeClassifier, DecisionTreeRegressor
from sklearn.naive_bayes import GaussianNB
from sklearn.neighbors import KNeighborsClassifier, KNeighborsRegressor
from sklearn.ensemble import VotingClassifier, BaggingClassifier, AdaBoostClassifier
from sklearn.pipeline import Pipeline
from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import OneHotEncoder
from scipy import stats
from scipy.cluster.hierarchy import dendrogram, linkage
from scipy.spatial.distance import pdist, squareform
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import seaborn as sns
import matplotlib.pyplot as plt
import warnings
warnings.filterwarnings('ignore')

class MarketingDataScienceAnalyzer:
    def __init__(self):
        self.data_science_data = {}
        self.data_science_analysis = {}
        self.data_science_models = {}
        self.data_science_strategies = {}
        self.data_science_insights = {}
        self.data_science_recommendations = {}
        
    def load_data_science_data(self, data_science_data):
        """Cargar datos de data science de marketing"""
        if isinstance(data_science_data, str):
            if data_science_data.endswith('.csv'):
                self.data_science_data = pd.read_csv(data_science_data)
            elif data_science_data.endswith('.json'):
                with open(data_science_data, 'r') as f:
                    data = json.load(f)
                self.data_science_data = pd.DataFrame(data)
        else:
            self.data_science_data = pd.DataFrame(data_science_data)
        
        print(f"✅ Datos de data science de marketing cargados: {len(self.data_science_data)} registros")
        return True
    
    def analyze_data_science_insights(self):
        """Analizar insights de data science"""
        if self.data_science_data.empty:
            return None
        
        # Análisis exploratorio de datos
        exploratory_analysis = self._perform_exploratory_data_analysis()
        
        # Análisis de calidad de datos
        data_quality_analysis = self._analyze_data_quality()
        
        # Análisis estadístico
        statistical_analysis = self._perform_statistical_analysis()
        
        # Análisis de correlaciones
        correlation_analysis = self._analyze_correlations()
        
        # Análisis de outliers
        outlier_analysis = self._analyze_outliers()
        
        # Análisis de distribuciones
        distribution_analysis = self._analyze_distributions()
        
        # Análisis de patrones
        pattern_analysis = self._analyze_patterns()
        
        data_science_results = {
            'exploratory_analysis': exploratory_analysis,
            'data_quality_analysis': data_quality_analysis,
            'statistical_analysis': statistical_analysis,
            'correlation_analysis': correlation_analysis,
            'outlier_analysis': outlier_analysis,
            'distribution_analysis': distribution_analysis,
            'pattern_analysis': pattern_analysis,
            'overall_insights': self._calculate_overall_insights()
        }
        
        self.data_science_analysis = data_science_results
        return data_science_results
    
    def _perform_exploratory_data_analysis(self):
        """Realizar análisis exploratorio de datos"""
        eda_results = {}
        
        # Información básica del dataset
        eda_results['dataset_info'] = {
            'shape': self.data_science_data.shape,
            'columns': list(self.data_science_data.columns),
            'dtypes': self.data_science_data.dtypes.to_dict(),
            'memory_usage': self.data_science_data.memory_usage(deep=True).sum()
        }
        
        # Estadísticas descriptivas
        eda_results['descriptive_stats'] = self.data_science_data.describe().to_dict()
        
        # Información de valores nulos
        eda_results['missing_values'] = {
            'total_missing': self.data_science_data.isnull().sum().sum(),
            'missing_by_column': self.data_science_data.isnull().sum().to_dict(),
            'missing_percentage': (self.data_science_data.isnull().sum() / len(self.data_science_data) * 100).to_dict()
        }
        
        # Información de valores únicos
        eda_results['unique_values'] = {
            'unique_by_column': self.data_science_data.nunique().to_dict(),
            'duplicate_rows': self.data_science_data.duplicated().sum()
        }
        
        # Análisis de tipos de datos
        eda_results['data_types'] = {
            'numeric_columns': list(self.data_science_data.select_dtypes(include=[np.number]).columns),
            'categorical_columns': list(self.data_science_data.select_dtypes(include=['object']).columns),
            'datetime_columns': list(self.data_science_data.select_dtypes(include=['datetime64']).columns)
        }
        
        return eda_results
    
    def _analyze_data_quality(self):
        """Analizar calidad de datos"""
        quality_results = {}
        
        # Completitud de datos
        completeness = (1 - self.data_science_data.isnull().sum().sum() / (len(self.data_science_data) * len(self.data_science_data.columns))) * 100
        quality_results['completeness'] = completeness
        
        # Consistencia de datos
        consistency_score = self._calculate_consistency_score()
        quality_results['consistency'] = consistency_score
        
        # Precisión de datos
        accuracy_score = self._calculate_accuracy_score()
        quality_results['accuracy'] = accuracy_score
        
        # Validez de datos
        validity_score = self._calculate_validity_score()
        quality_results['validity'] = validity_score
        
        # Unicidad de datos
        uniqueness_score = self._calculate_uniqueness_score()
        quality_results['uniqueness'] = uniqueness_score
        
        # Score general de calidad
        overall_quality = (completeness + consistency_score + accuracy_score + validity_score + uniqueness_score) / 5
        quality_results['overall_quality'] = overall_quality
        
        # Recomendaciones de calidad
        quality_recommendations = []
        if completeness < 80:
            quality_recommendations.append("Mejorar completitud de datos")
        if consistency_score < 70:
            quality_recommendations.append("Mejorar consistencia de datos")
        if accuracy_score < 80:
            quality_recommendations.append("Mejorar precisión de datos")
        if validity_score < 75:
            quality_recommendations.append("Mejorar validez de datos")
        if uniqueness_score < 90:
            quality_recommendations.append("Mejorar unicidad de datos")
        
        quality_results['recommendations'] = quality_recommendations
        
        return quality_results
    
    def _calculate_consistency_score(self):
        """Calcular score de consistencia"""
        consistency_score = 0
        
        # Verificar consistencia en formatos de fecha
        date_columns = self.data_science_data.select_dtypes(include=['datetime64']).columns
        if len(date_columns) > 0:
            consistency_score += 20
        
        # Verificar consistencia en valores categóricos
        categorical_columns = self.data_science_data.select_dtypes(include=['object']).columns
        for col in categorical_columns:
            if self.data_science_data[col].dtype == 'object':
                # Verificar si hay valores inconsistentes (espacios extra, mayúsculas/minúsculas)
                unique_values = self.data_science_data[col].dropna().unique()
                cleaned_values = [str(val).strip().lower() for val in unique_values]
                if len(unique_values) == len(set(cleaned_values)):
                    consistency_score += 10
        
        # Verificar consistencia en valores numéricos
        numeric_columns = self.data_science_data.select_dtypes(include=[np.number]).columns
        for col in numeric_columns:
            if self.data_science_data[col].dtype in ['int64', 'float64']:
                # Verificar si hay valores fuera de rango esperado
                if col in ['age', 'revenue', 'cost']:
                    if col == 'age' and self.data_science_data[col].between(0, 120).all():
                        consistency_score += 10
                    elif col in ['revenue', 'cost'] and (self.data_science_data[col] >= 0).all():
                        consistency_score += 10
        
        return min(consistency_score, 100)
    
    def _calculate_accuracy_score(self):
        """Calcular score de precisión"""
        accuracy_score = 0
        
        # Verificar precisión en valores numéricos
        numeric_columns = self.data_science_data.select_dtypes(include=[np.number]).columns
        for col in numeric_columns:
            if self.data_science_data[col].dtype in ['int64', 'float64']:
                # Verificar si hay valores que parecen incorrectos
                if col in ['revenue', 'cost', 'profit']:
                    if (self.data_science_data[col] >= 0).all():
                        accuracy_score += 15
                elif col in ['conversion_rate', 'ctr', 'engagement_rate']:
                    if (self.data_science_data[col] >= 0).all() and (self.data_science_data[col] <= 100).all():
                        accuracy_score += 15
        
        # Verificar precisión en valores categóricos
        categorical_columns = self.data_science_data.select_dtypes(include=['object']).columns
        for col in categorical_columns:
            if self.data_science_data[col].dtype == 'object':
                # Verificar si hay valores que parecen incorrectos
                unique_values = self.data_science_data[col].dropna().unique()
                if len(unique_values) > 0:
                    accuracy_score += 10
        
        return min(accuracy_score, 100)
    
    def _calculate_validity_score(self):
        """Calcular score de validez"""
        validity_score = 0
        
        # Verificar validez en valores numéricos
        numeric_columns = self.data_science_data.select_dtypes(include=[np.number]).columns
        for col in numeric_columns:
            if self.data_science_data[col].dtype in ['int64', 'float64']:
                # Verificar si hay valores que parecen inválidos
                if col in ['age']:
                    if (self.data_science_data[col] >= 0).all() and (self.data_science_data[col] <= 120).all():
                        validity_score += 20
                elif col in ['revenue', 'cost']:
                    if (self.data_science_data[col] >= 0).all():
                        validity_score += 20
                elif col in ['conversion_rate', 'ctr']:
                    if (self.data_science_data[col] >= 0).all() and (self.data_science_data[col] <= 100).all():
                        validity_score += 20
        
        # Verificar validez en valores categóricos
        categorical_columns = self.data_science_data.select_dtypes(include=['object']).columns
        for col in categorical_columns:
            if self.data_science_data[col].dtype == 'object':
                # Verificar si hay valores que parecen inválidos
                unique_values = self.data_science_data[col].dropna().unique()
                if len(unique_values) > 0:
                    validity_score += 10
        
        return min(validity_score, 100)
    
    def _calculate_uniqueness_score(self):
        """Calcular score de unicidad"""
        uniqueness_score = 0
        
        # Verificar unicidad en identificadores
        id_columns = [col for col in self.data_science_data.columns if 'id' in col.lower()]
        for col in id_columns:
            if self.data_science_data[col].nunique() == len(self.data_science_data):
                uniqueness_score += 25
        
        # Verificar unicidad en combinaciones de columnas
        if len(self.data_science_data.columns) > 1:
            # Verificar si hay filas duplicadas
            if self.data_science_data.duplicated().sum() == 0:
                uniqueness_score += 25
        
        # Verificar unicidad en valores categóricos
        categorical_columns = self.data_science_data.select_dtypes(include=['object']).columns
        for col in categorical_columns:
            if self.data_science_data[col].dtype == 'object':
                # Verificar si hay valores duplicados que deberían ser únicos
                if col in ['email', 'phone', 'customer_id']:
                    if self.data_science_data[col].nunique() == len(self.data_science_data):
                        uniqueness_score += 25
        
        return min(uniqueness_score, 100)
    
    def _perform_statistical_analysis(self):
        """Realizar análisis estadístico"""
        statistical_results = {}
        
        # Análisis de variables numéricas
        numeric_columns = self.data_science_data.select_dtypes(include=[np.number]).columns
        if len(numeric_columns) > 0:
            numeric_analysis = {}
            for col in numeric_columns:
                numeric_analysis[col] = {
                    'mean': self.data_science_data[col].mean(),
                    'median': self.data_science_data[col].median(),
                    'mode': self.data_science_data[col].mode().iloc[0] if len(self.data_science_data[col].mode()) > 0 else None,
                    'std': self.data_science_data[col].std(),
                    'var': self.data_science_data[col].var(),
                    'skewness': self.data_science_data[col].skew(),
                    'kurtosis': self.data_science_data[col].kurtosis(),
                    'min': self.data_science_data[col].min(),
                    'max': self.data_science_data[col].max(),
                    'range': self.data_science_data[col].max() - self.data_science_data[col].min(),
                    'iqr': self.data_science_data[col].quantile(0.75) - self.data_science_data[col].quantile(0.25)
                }
            statistical_results['numeric_analysis'] = numeric_analysis
        
        # Análisis de variables categóricas
        categorical_columns = self.data_science_data.select_dtypes(include=['object']).columns
        if len(categorical_columns) > 0:
            categorical_analysis = {}
            for col in categorical_columns:
                value_counts = self.data_science_data[col].value_counts()
                categorical_analysis[col] = {
                    'unique_count': self.data_science_data[col].nunique(),
                    'most_frequent': value_counts.index[0] if len(value_counts) > 0 else None,
                    'most_frequent_count': value_counts.iloc[0] if len(value_counts) > 0 else 0,
                    'most_frequent_percentage': (value_counts.iloc[0] / len(self.data_science_data) * 100) if len(value_counts) > 0 else 0,
                    'entropy': self._calculate_entropy(self.data_science_data[col])
                }
            statistical_results['categorical_analysis'] = categorical_analysis
        
        # Análisis de correlaciones
        if len(numeric_columns) > 1:
            correlation_matrix = self.data_science_data[numeric_columns].corr()
            statistical_results['correlation_matrix'] = correlation_matrix.to_dict()
            
            # Encontrar correlaciones fuertes
            strong_correlations = []
            for i in range(len(correlation_matrix.columns)):
                for j in range(i+1, len(correlation_matrix.columns)):
                    corr_value = correlation_matrix.iloc[i, j]
                    if abs(corr_value) > 0.7:
                        strong_correlations.append({
                            'variable1': correlation_matrix.columns[i],
                            'variable2': correlation_matrix.columns[j],
                            'correlation': corr_value
                        })
            statistical_results['strong_correlations'] = strong_correlations
        
        return statistical_results
    
    def _calculate_entropy(self, series):
        """Calcular entropía de una serie"""
        value_counts = series.value_counts()
        probabilities = value_counts / len(series)
        entropy = -np.sum(probabilities * np.log2(probabilities + 1e-10))
        return entropy
    
    def _analyze_correlations(self):
        """Analizar correlaciones"""
        correlation_results = {}
        
        # Análisis de correlaciones numéricas
        numeric_columns = self.data_science_data.select_dtypes(include=[np.number]).columns
        if len(numeric_columns) > 1:
            correlation_matrix = self.data_science_data[numeric_columns].corr()
            
            # Análisis de correlaciones por fuerza
            correlation_strength = {
                'very_strong': [],
                'strong': [],
                'moderate': [],
                'weak': []
            }
            
            for i in range(len(correlation_matrix.columns)):
                for j in range(i+1, len(correlation_matrix.columns)):
                    corr_value = correlation_matrix.iloc[i, j]
                    corr_abs = abs(corr_value)
                    
                    correlation_info = {
                        'variable1': correlation_matrix.columns[i],
                        'variable2': correlation_matrix.columns[j],
                        'correlation': corr_value,
                        'abs_correlation': corr_abs
                    }
                    
                    if corr_abs >= 0.8:
                        correlation_strength['very_strong'].append(correlation_info)
                    elif corr_abs >= 0.6:
                        correlation_strength['strong'].append(correlation_info)
                    elif corr_abs >= 0.4:
                        correlation_strength['moderate'].append(correlation_info)
                    else:
                        correlation_strength['weak'].append(correlation_info)
            
            correlation_results['correlation_matrix'] = correlation_matrix.to_dict()
            correlation_results['correlation_strength'] = correlation_strength
            
            # Análisis de multicolinealidad
            multicollinearity = self._analyze_multicollinearity(correlation_matrix)
            correlation_results['multicollinearity'] = multicollinearity
        
        return correlation_results
    
    def _analyze_multicollinearity(self, correlation_matrix):
        """Analizar multicolinealidad"""
        multicollinearity_results = {}
        
        # Calcular VIF (Variance Inflation Factor) simplificado
        vif_scores = {}
        for col in correlation_matrix.columns:
            # Calcular R² con otras variables
            other_cols = [c for c in correlation_matrix.columns if c != col]
            if len(other_cols) > 0:
                # Usar correlación promedio como proxy de R²
                avg_correlation = correlation_matrix.loc[col, other_cols].abs().mean()
                vif = 1 / (1 - avg_correlation**2) if avg_correlation < 0.99 else float('inf')
                vif_scores[col] = vif
        
        multicollinearity_results['vif_scores'] = vif_scores
        
        # Identificar variables con alta multicolinealidad
        high_vif_variables = [var for var, vif in vif_scores.items() if vif > 10]
        multicollinearity_results['high_vif_variables'] = high_vif_variables
        
        # Recomendaciones
        recommendations = []
        if high_vif_variables:
            recommendations.append(f"Considerar eliminar variables con alta multicolinealidad: {', '.join(high_vif_variables)}")
        else:
            recommendations.append("No se detectó multicolinealidad significativa")
        
        multicollinearity_results['recommendations'] = recommendations
        
        return multicollinearity_results
    
    def _analyze_outliers(self):
        """Analizar outliers"""
        outlier_results = {}
        
        # Análisis de outliers numéricos
        numeric_columns = self.data_science_data.select_dtypes(include=[np.number]).columns
        if len(numeric_columns) > 0:
            outlier_analysis = {}
            for col in numeric_columns:
                # Método IQR
                Q1 = self.data_science_data[col].quantile(0.25)
                Q3 = self.data_science_data[col].quantile(0.75)
                IQR = Q3 - Q1
                lower_bound = Q1 - 1.5 * IQR
                upper_bound = Q3 + 1.5 * IQR
                
                iqr_outliers = self.data_science_data[(self.data_science_data[col] < lower_bound) | (self.data_science_data[col] > upper_bound)]
                
                # Método Z-score
                z_scores = np.abs(stats.zscore(self.data_science_data[col].dropna()))
                z_outliers = self.data_science_data[z_scores > 3]
                
                # Método Isolation Forest
                isolation_forest = IsolationForest(contamination=0.1, random_state=42)
                outlier_labels = isolation_forest.fit_predict(self.data_science_data[[col]].dropna())
                isolation_outliers = self.data_science_data[outlier_labels == -1]
                
                outlier_analysis[col] = {
                    'iqr_outliers_count': len(iqr_outliers),
                    'iqr_outliers_percentage': (len(iqr_outliers) / len(self.data_science_data)) * 100,
                    'z_score_outliers_count': len(z_outliers),
                    'z_score_outliers_percentage': (len(z_outliers) / len(self.data_science_data)) * 100,
                    'isolation_outliers_count': len(isolation_outliers),
                    'isolation_outliers_percentage': (len(isolation_outliers) / len(self.data_science_data)) * 100,
                    'outlier_values': iqr_outliers[col].tolist() if len(iqr_outliers) > 0 else []
                }
            
            outlier_results['numeric_outliers'] = outlier_analysis
        
        # Análisis de outliers categóricos
        categorical_columns = self.data_science_data.select_dtypes(include=['object']).columns
        if len(categorical_columns) > 0:
            categorical_outliers = {}
            for col in categorical_columns:
                value_counts = self.data_science_data[col].value_counts()
                total_count = len(self.data_science_data)
                
                # Identificar valores que aparecen muy poco (menos del 1%)
                rare_values = value_counts[value_counts / total_count < 0.01]
                
                categorical_outliers[col] = {
                    'rare_values_count': len(rare_values),
                    'rare_values': rare_values.to_dict(),
                    'most_common_value': value_counts.index[0] if len(value_counts) > 0 else None,
                    'most_common_percentage': (value_counts.iloc[0] / total_count * 100) if len(value_counts) > 0 else 0
                }
            
            outlier_results['categorical_outliers'] = categorical_outliers
        
        return outlier_results
    
    def _analyze_distributions(self):
        """Analizar distribuciones"""
        distribution_results = {}
        
        # Análisis de distribuciones numéricas
        numeric_columns = self.data_science_data.select_dtypes(include=[np.number]).columns
        if len(numeric_columns) > 0:
            distribution_analysis = {}
            for col in numeric_columns:
                # Test de normalidad
                shapiro_stat, shapiro_p = stats.shapiro(self.data_science_data[col].dropna().sample(min(5000, len(self.data_science_data))))
                ks_stat, ks_p = stats.kstest(self.data_science_data[col].dropna(), 'norm')
                
                # Análisis de asimetría y curtosis
                skewness = self.data_science_data[col].skew()
                kurtosis = self.data_science_data[col].kurtosis()
                
                # Clasificación de la distribución
                if abs(skewness) < 0.5 and abs(kurtosis) < 0.5:
                    distribution_type = 'normal'
                elif abs(skewness) > 1:
                    distribution_type = 'highly_skewed'
                elif abs(skewness) > 0.5:
                    distribution_type = 'moderately_skewed'
                else:
                    distribution_type = 'approximately_normal'
                
                distribution_analysis[col] = {
                    'shapiro_stat': shapiro_stat,
                    'shapiro_p': shapiro_p,
                    'ks_stat': ks_stat,
                    'ks_p': ks_p,
                    'skewness': skewness,
                    'kurtosis': kurtosis,
                    'distribution_type': distribution_type,
                    'is_normal': shapiro_p > 0.05
                }
            
            distribution_results['numeric_distributions'] = distribution_analysis
        
        # Análisis de distribuciones categóricas
        categorical_columns = self.data_science_data.select_dtypes(include=['object']).columns
        if len(categorical_columns) > 0:
            categorical_distributions = {}
            for col in categorical_columns:
                value_counts = self.data_science_data[col].value_counts()
                total_count = len(self.data_science_data)
                
                # Calcular entropía
                entropy = self._calculate_entropy(self.data_science_data[col])
                
                # Calcular índice de diversidad
                diversity_index = 1 - sum((value_counts / total_count) ** 2)
                
                # Clasificar la distribución
                if entropy < 1:
                    distribution_type = 'low_diversity'
                elif entropy < 2:
                    distribution_type = 'moderate_diversity'
                else:
                    distribution_type = 'high_diversity'
                
                categorical_distributions[col] = {
                    'entropy': entropy,
                    'diversity_index': diversity_index,
                    'distribution_type': distribution_type,
                    'unique_values': len(value_counts),
                    'most_common_value': value_counts.index[0] if len(value_counts) > 0 else None,
                    'most_common_percentage': (value_counts.iloc[0] / total_count * 100) if len(value_counts) > 0 else 0
                }
            
            distribution_results['categorical_distributions'] = categorical_distributions
        
        return distribution_results
    
    def _analyze_patterns(self):
        """Analizar patrones"""
        pattern_results = {}
        
        # Análisis de patrones temporales
        if 'date' in self.data_science_data.columns:
            temporal_patterns = self._analyze_temporal_patterns()
            pattern_results['temporal_patterns'] = temporal_patterns
        
        # Análisis de patrones de agrupación
        clustering_patterns = self._analyze_clustering_patterns()
        pattern_results['clustering_patterns'] = clustering_patterns
        
        # Análisis de patrones de asociación
        association_patterns = self._analyze_association_patterns()
        pattern_results['association_patterns'] = association_patterns
        
        return pattern_results
    
    def _analyze_temporal_patterns(self):
        """Analizar patrones temporales"""
        temporal_results = {}
        
        if 'date' in self.data_science_data.columns:
            self.data_science_data['date'] = pd.to_datetime(self.data_science_data['date'])
            
            # Análisis por día de la semana
            self.data_science_data['day_of_week'] = self.data_science_data['date'].dt.day_name()
            daily_patterns = self.data_science_data.groupby('day_of_week').size().to_dict()
            
            # Análisis por mes
            self.data_science_data['month'] = self.data_science_data['date'].dt.month
            monthly_patterns = self.data_science_data.groupby('month').size().to_dict()
            
            # Análisis por hora
            self.data_science_data['hour'] = self.data_science_data['date'].dt.hour
            hourly_patterns = self.data_science_data.groupby('hour').size().to_dict()
            
            temporal_results = {
                'daily_patterns': daily_patterns,
                'monthly_patterns': monthly_patterns,
                'hourly_patterns': hourly_patterns,
                'peak_day': max(daily_patterns, key=daily_patterns.get) if daily_patterns else None,
                'peak_month': max(monthly_patterns, key=monthly_patterns.get) if monthly_patterns else None,
                'peak_hour': max(hourly_patterns, key=hourly_patterns.get) if hourly_patterns else None
            }
        
        return temporal_results
    
    def _analyze_clustering_patterns(self):
        """Analizar patrones de agrupación"""
        clustering_results = {}
        
        # Seleccionar variables numéricas para clustering
        numeric_columns = self.data_science_data.select_dtypes(include=[np.number]).columns
        if len(numeric_columns) > 1:
            # Preparar datos
            clustering_data = self.data_science_data[numeric_columns].dropna()
            
            if len(clustering_data) > 10:
                # K-Means clustering
                kmeans = KMeans(n_clusters=3, random_state=42)
                kmeans_labels = kmeans.fit_predict(clustering_data)
                
                # DBSCAN clustering
                dbscan = DBSCAN(eps=0.5, min_samples=5)
                dbscan_labels = dbscan.fit_predict(clustering_data)
                
                # Análisis de clusters
                clustering_results = {
                    'kmeans_clusters': {
                        'n_clusters': len(set(kmeans_labels)),
                        'cluster_sizes': [list(kmeans_labels).count(i) for i in range(len(set(kmeans_labels)))],
                        'inertia': kmeans.inertia_
                    },
                    'dbscan_clusters': {
                        'n_clusters': len(set(dbscan_labels)) - (1 if -1 in dbscan_labels else 0),
                        'n_noise': list(dbscan_labels).count(-1),
                        'cluster_sizes': [list(dbscan_labels).count(i) for i in set(dbscan_labels) if i != -1]
                    }
                }
        
        return clustering_results
    
    def _analyze_association_patterns(self):
        """Analizar patrones de asociación"""
        association_results = {}
        
        # Análisis de asociación entre variables categóricas
        categorical_columns = self.data_science_data.select_dtypes(include=['object']).columns
        if len(categorical_columns) > 1:
            association_analysis = {}
            for i, col1 in enumerate(categorical_columns):
                for j, col2 in enumerate(categorical_columns[i+1:], i+1):
                    # Crear tabla de contingencia
                    contingency_table = pd.crosstab(self.data_science_data[col1], self.data_science_data[col2])
                    
                    # Calcular chi-cuadrado
                    chi2, p_value, dof, expected = stats.chi2_contingency(contingency_table)
                    
                    # Calcular Cramér's V
                    n = contingency_table.sum().sum()
                    cramers_v = np.sqrt(chi2 / (n * (min(contingency_table.shape) - 1)))
                    
                    association_analysis[f"{col1}_vs_{col2}"] = {
                        'chi2': chi2,
                        'p_value': p_value,
                        'cramers_v': cramers_v,
                        'association_strength': 'strong' if cramers_v > 0.5 else 'moderate' if cramers_v > 0.3 else 'weak'
                    }
            
            association_results['categorical_associations'] = association_analysis
        
        return association_results
    
    def _calculate_overall_insights(self):
        """Calcular insights generales"""
        overall_insights = {}
        
        if not self.data_science_data.empty:
            overall_insights = {
                'total_records': len(self.data_science_data),
                'total_columns': len(self.data_science_data.columns),
                'data_quality_score': self._calculate_overall_data_quality(),
                'insights_summary': self._generate_insights_summary()
            }
        
        return overall_insights
    
    def _calculate_overall_data_quality(self):
        """Calcular score general de calidad de datos"""
        if self.data_science_analysis and 'data_quality_analysis' in self.data_science_analysis:
            return self.data_science_analysis['data_quality_analysis'].get('overall_quality', 0)
        return 0
    
    def _generate_insights_summary(self):
        """Generar resumen de insights"""
        insights = []
        
        # Insights de calidad de datos
        if self.data_science_analysis and 'data_quality_analysis' in self.data_science_analysis:
            data_quality = self.data_science_analysis['data_quality_analysis']
            overall_quality = data_quality.get('overall_quality', 0)
            
            if overall_quality >= 80:
                insights.append("Calidad de datos excelente")
            elif overall_quality >= 60:
                insights.append("Calidad de datos buena")
            else:
                insights.append("Calidad de datos necesita mejora")
        
        # Insights de correlaciones
        if self.data_science_analysis and 'correlation_analysis' in self.data_science_analysis:
            correlation_analysis = self.data_science_analysis['correlation_analysis']
            strong_correlations = correlation_analysis.get('correlation_strength', {}).get('strong', [])
            
            if len(strong_correlations) > 0:
                insights.append(f"{len(strong_correlations)} correlaciones fuertes encontradas")
        
        # Insights de outliers
        if self.data_science_analysis and 'outlier_analysis' in self.data_science_analysis:
            outlier_analysis = self.data_science_analysis['outlier_analysis']
            numeric_outliers = outlier_analysis.get('numeric_outliers', {})
            
            high_outlier_columns = [col for col, data in numeric_outliers.items() 
                                  if data.get('iqr_outliers_percentage', 0) > 5]
            
            if high_outlier_columns:
                insights.append(f"Outliers significativos en: {', '.join(high_outlier_columns)}")
        
        return insights
    
    def build_data_science_models(self, target_variable, model_type='classification'):
        """Construir modelos de data science"""
        if target_variable not in self.data_science_data.columns:
            raise ValueError(f"Variable objetivo '{target_variable}' no encontrada")
        
        # Preparar datos
        feature_columns = [col for col in self.data_science_data.columns if col != target_variable]
        X = self.data_science_data[feature_columns]
        y = self.data_science_data[target_variable]
        
        # Preprocesamiento
        X_processed, y_processed = self._preprocess_data(X, y)
        
        # Dividir datos
        X_train, X_test, y_train, y_test = train_test_split(X_processed, y_processed, test_size=0.2, random_state=42)
        
        # Construir modelos
        models = {}
        
        if model_type == 'classification':
            models = self._build_classification_models(X_train, X_test, y_train, y_test)
        elif model_type == 'regression':
            models = self._build_regression_models(X_train, X_test, y_train, y_test)
        elif model_type == 'clustering':
            models = self._build_clustering_models(X_processed)
        elif model_type == 'dimensionality_reduction':
            models = self._build_dimensionality_reduction_models(X_processed)
        
        # Evaluar modelos
        model_evaluation = self._evaluate_models(models, X_test, y_test, model_type)
        
        self.data_science_models = {
            'models': models,
            'model_evaluation': model_evaluation,
            'model_type': model_type,
            'target_variable': target_variable
        }
        
        return self.data_science_models
    
    def _preprocess_data(self, X, y):
        """Preprocesar datos"""
        # Identificar columnas numéricas y categóricas
        numeric_columns = X.select_dtypes(include=[np.number]).columns
        categorical_columns = X.select_dtypes(include=['object']).columns
        
        # Crear transformador de columnas
        numeric_transformer = Pipeline(steps=[
            ('imputer', SimpleImputer(strategy='median')),
            ('scaler', StandardScaler())
        ])
        
        categorical_transformer = Pipeline(steps=[
            ('imputer', SimpleImputer(strategy='constant', fill_value='missing')),
            ('onehot', OneHotEncoder(handle_unknown='ignore'))
        ])
        
        preprocessor = ColumnTransformer(
            transformers=[
                ('num', numeric_transformer, numeric_columns),
                ('cat', categorical_transformer, categorical_columns)
            ]
        )
        
        # Aplicar preprocesamiento
        X_processed = preprocessor.fit_transform(X)
        
        # Preprocesar variable objetivo si es categórica
        if y.dtype == 'object':
            label_encoder = LabelEncoder()
            y_processed = label_encoder.fit_transform(y)
        else:
            y_processed = y
        
        return X_processed, y_processed
    
    def _build_classification_models(self, X_train, X_test, y_train, y_test):
        """Construir modelos de clasificación"""
        models = {}
        
        # Random Forest
        rf_model = RandomForestClassifier(n_estimators=100, random_state=42)
        rf_model.fit(X_train, y_train)
        models['Random Forest'] = rf_model
        
        # Gradient Boosting
        gb_model = GradientBoostingRegressor(n_estimators=100, random_state=42)
        gb_model.fit(X_train, y_train)
        models['Gradient Boosting'] = gb_model
        
        # SVM
        svm_model = SVC(random_state=42)
        svm_model.fit(X_train, y_train)
        models['SVM'] = svm_model
        
        # Logistic Regression
        lr_model = LogisticRegression(random_state=42)
        lr_model.fit(X_train, y_train)
        models['Logistic Regression'] = lr_model
        
        # Naive Bayes
        nb_model = GaussianNB()
        nb_model.fit(X_train, y_train)
        models['Naive Bayes'] = nb_model
        
        # K-Nearest Neighbors
        knn_model = KNeighborsClassifier()
        knn_model.fit(X_train, y_train)
        models['K-Nearest Neighbors'] = knn_model
        
        # Decision Tree
        dt_model = DecisionTreeClassifier(random_state=42)
        dt_model.fit(X_train, y_train)
        models['Decision Tree'] = dt_model
        
        # Neural Network
        nn_model = MLPClassifier(random_state=42)
        nn_model.fit(X_train, y_train)
        models['Neural Network'] = nn_model
        
        return models
    
    def _build_regression_models(self, X_train, X_test, y_train, y_test):
        """Construir modelos de regresión"""
        models = {}
        
        # Linear Regression
        lr_model = LinearRegression()
        lr_model.fit(X_train, y_train)
        models['Linear Regression'] = lr_model
        
        # Ridge Regression
        ridge_model = Ridge(random_state=42)
        ridge_model.fit(X_train, y_train)
        models['Ridge Regression'] = ridge_model
        
        # Lasso Regression
        lasso_model = Lasso(random_state=42)
        lasso_model.fit(X_train, y_train)
        models['Lasso Regression'] = lasso_model
        
        # Random Forest
        rf_model = RandomForestRegressor(n_estimators=100, random_state=42)
        rf_model.fit(X_train, y_train)
        models['Random Forest'] = rf_model
        
        # Gradient Boosting
        gb_model = GradientBoostingRegressor(n_estimators=100, random_state=42)
        gb_model.fit(X_train, y_train)
        models['Gradient Boosting'] = gb_model
        
        # SVM
        svr_model = SVR()
        svr_model.fit(X_train, y_train)
        models['SVM'] = svr_model
        
        # K-Nearest Neighbors
        knn_model = KNeighborsRegressor()
        knn_model.fit(X_train, y_train)
        models['K-Nearest Neighbors'] = knn_model
        
        # Decision Tree
        dt_model = DecisionTreeRegressor(random_state=42)
        dt_model.fit(X_train, y_train)
        models['Decision Tree'] = dt_model
        
        # Neural Network
        nn_model = MLPRegressor(random_state=42)
        nn_model.fit(X_train, y_train)
        models['Neural Network'] = nn_model
        
        return models
    
    def _build_clustering_models(self, X):
        """Construir modelos de clustering"""
        models = {}
        
        # K-Means
        kmeans_model = KMeans(n_clusters=3, random_state=42)
        kmeans_model.fit(X)
        models['K-Means'] = kmeans_model
        
        # DBSCAN
        dbscan_model = DBSCAN(eps=0.5, min_samples=5)
        dbscan_model.fit(X)
        models['DBSCAN'] = dbscan_model
        
        # Agglomerative Clustering
        agg_model = AgglomerativeClustering(n_clusters=3)
        agg_model.fit(X)
        models['Agglomerative Clustering'] = agg_model
        
        return models
    
    def _build_dimensionality_reduction_models(self, X):
        """Construir modelos de reducción de dimensionalidad"""
        models = {}
        
        # PCA
        pca_model = PCA(n_components=0.95)
        pca_model.fit(X)
        models['PCA'] = pca_model
        
        # Factor Analysis
        fa_model = FactorAnalysis(n_components=5)
        fa_model.fit(X)
        models['Factor Analysis'] = fa_model
        
        # FastICA
        ica_model = FastICA(n_components=5, random_state=42)
        ica_model.fit(X)
        models['FastICA'] = ica_model
        
        return models
    
    def _evaluate_models(self, models, X_test, y_test, model_type):
        """Evaluar modelos"""
        evaluation_results = {}
        
        for model_name, model in models.items():
            try:
                if model_type == 'classification':
                    y_pred = model.predict(X_test)
                    evaluation_results[model_name] = {
                        'accuracy': accuracy_score(y_test, y_pred),
                        'precision': precision_score(y_test, y_pred, average='weighted'),
                        'recall': recall_score(y_test, y_pred, average='weighted'),
                        'f1_score': f1_score(y_test, y_pred, average='weighted')
                    }
                elif model_type == 'regression':
                    y_pred = model.predict(X_test)
                    from sklearn.metrics import mean_squared_error, r2_score, mean_absolute_error
                    evaluation_results[model_name] = {
                        'mse': mean_squared_error(y_test, y_pred),
                        'rmse': np.sqrt(mean_squared_error(y_test, y_pred)),
                        'mae': mean_absolute_error(y_test, y_pred),
                        'r2': r2_score(y_test, y_pred)
                    }
                elif model_type == 'clustering':
                    if hasattr(model, 'labels_'):
                        labels = model.labels_
                        evaluation_results[model_name] = {
                            'n_clusters': len(set(labels)) - (1 if -1 in labels else 0),
                            'n_noise': list(labels).count(-1) if -1 in labels else 0
                        }
                    else:
                        evaluation_results[model_name] = {
                            'n_clusters': model.n_clusters if hasattr(model, 'n_clusters') else 'unknown'
                        }
                elif model_type == 'dimensionality_reduction':
                    if hasattr(model, 'explained_variance_ratio_'):
                        evaluation_results[model_name] = {
                            'explained_variance_ratio': model.explained_variance_ratio_.tolist(),
                            'n_components': model.n_components_
                        }
                    else:
                        evaluation_results[model_name] = {
                            'n_components': model.n_components if hasattr(model, 'n_components') else 'unknown'
                        }
            except Exception as e:
                evaluation_results[model_name] = {'error': str(e)}
        
        return evaluation_results
    
    def generate_data_science_strategies(self):
        """Generar estrategias de data science"""
        strategies = []
        
        # Estrategias basadas en calidad de datos
        if self.data_science_analysis and 'data_quality_analysis' in self.data_science_analysis:
            data_quality = self.data_science_analysis['data_quality_analysis']
            overall_quality = data_quality.get('overall_quality', 0)
            
            if overall_quality < 70:
                strategies.append({
                    'strategy_type': 'Data Quality Improvement',
                    'description': f'Mejorar calidad de datos: {overall_quality:.1f}%',
                    'priority': 'high',
                    'expected_impact': 'high'
                })
            
            recommendations = data_quality.get('recommendations', [])
            for recommendation in recommendations:
                strategies.append({
                    'strategy_type': 'Data Quality Action',
                    'description': recommendation,
                    'priority': 'medium',
                    'expected_impact': 'medium'
                })
        
        # Estrategias basadas en correlaciones
        if self.data_science_analysis and 'correlation_analysis' in self.data_science_analysis:
            correlation_analysis = self.data_science_analysis['correlation_analysis']
            strong_correlations = correlation_analysis.get('correlation_strength', {}).get('strong', [])
            
            if len(strong_correlations) > 0:
                strategies.append({
                    'strategy_type': 'Correlation Analysis',
                    'description': f'Explotar {len(strong_correlations)} correlaciones fuertes',
                    'priority': 'medium',
                    'expected_impact': 'medium'
                })
        
        # Estrategias basadas en outliers
        if self.data_science_analysis and 'outlier_analysis' in self.data_science_analysis:
            outlier_analysis = self.data_science_analysis['outlier_analysis']
            numeric_outliers = outlier_analysis.get('numeric_outliers', {})
            
            high_outlier_columns = [col for col, data in numeric_outliers.items() 
                                  if data.get('iqr_outliers_percentage', 0) > 5]
            
            if high_outlier_columns:
                strategies.append({
                    'strategy_type': 'Outlier Treatment',
                    'description': f'Tratar outliers en: {", ".join(high_outlier_columns)}',
                    'priority': 'medium',
                    'expected_impact': 'medium'
                })
        
        # Estrategias basadas en modelos
        if self.data_science_models:
            model_evaluation = self.data_science_models.get('model_evaluation', {})
            if model_evaluation:
                # Encontrar mejor modelo
                best_model = None
                best_score = 0
                
                for model_name, metrics in model_evaluation.items():
                    if 'error' not in metrics:
                        if 'accuracy' in metrics:
                            score = metrics['accuracy']
                        elif 'r2' in metrics:
                            score = metrics['r2']
                        else:
                            score = 0
                        
                        if score > best_score:
                            best_score = score
                            best_model = model_name
                
                if best_model:
                    strategies.append({
                        'strategy_type': 'Model Deployment',
                        'description': f'Desplegar mejor modelo: {best_model}',
                        'priority': 'high',
                        'expected_impact': 'high'
                    })
        
        self.data_science_strategies = strategies
        return strategies
    
    def generate_data_science_insights(self):
        """Generar insights de data science"""
        insights = []
        
        # Insights de calidad de datos
        if self.data_science_analysis and 'data_quality_analysis' in self.data_science_analysis:
            data_quality = self.data_science_analysis['data_quality_analysis']
            overall_quality = data_quality.get('overall_quality', 0)
            
            if overall_quality >= 80:
                insights.append({
                    'category': 'Data Quality',
                    'insight': f'Calidad de datos excelente: {overall_quality:.1f}%',
                    'recommendation': 'Mantener estándares de calidad',
                    'priority': 'low'
                })
            elif overall_quality >= 60:
                insights.append({
                    'category': 'Data Quality',
                    'insight': f'Calidad de datos buena: {overall_quality:.1f}%',
                    'recommendation': 'Mejorar áreas específicas',
                    'priority': 'medium'
                })
            else:
                insights.append({
                    'category': 'Data Quality',
                    'insight': f'Calidad de datos necesita mejora: {overall_quality:.1f}%',
                    'recommendation': 'Implementar mejoras de calidad',
                    'priority': 'high'
                })
        
        # Insights de correlaciones
        if self.data_science_analysis and 'correlation_analysis' in self.data_science_analysis:
            correlation_analysis = self.data_science_analysis['correlation_analysis']
            strong_correlations = correlation_analysis.get('correlation_strength', {}).get('strong', [])
            
            if len(strong_correlations) > 0:
                insights.append({
                    'category': 'Correlations',
                    'insight': f'{len(strong_correlations)} correlaciones fuertes encontradas',
                    'recommendation': 'Explotar correlaciones para insights',
                    'priority': 'medium'
                })
        
        # Insights de outliers
        if self.data_science_analysis and 'outlier_analysis' in self.data_science_analysis:
            outlier_analysis = self.data_science_analysis['outlier_analysis']
            numeric_outliers = outlier_analysis.get('numeric_outliers', {})
            
            high_outlier_columns = [col for col, data in numeric_outliers.items() 
                                  if data.get('iqr_outliers_percentage', 0) > 5]
            
            if high_outlier_columns:
                insights.append({
                    'category': 'Outliers',
                    'insight': f'Outliers significativos en: {", ".join(high_outlier_columns)}',
                    'recommendation': 'Investigar y tratar outliers',
                    'priority': 'medium'
                })
        
        # Insights de modelos
        if self.data_science_models:
            model_evaluation = self.data_science_models.get('model_evaluation', {})
            if model_evaluation:
                # Encontrar mejor modelo
                best_model = None
                best_score = 0
                
                for model_name, metrics in model_evaluation.items():
                    if 'error' not in metrics:
                        if 'accuracy' in metrics:
                            score = metrics['accuracy']
                        elif 'r2' in metrics:
                            score = metrics['r2']
                        else:
                            score = 0
                        
                        if score > best_score:
                            best_score = score
                            best_model = model_name
                
                if best_model:
                    insights.append({
                        'category': 'Model Performance',
                        'insight': f'Mejor modelo: {best_model} con score {best_score:.3f}',
                        'recommendation': 'Usar este modelo para predicciones',
                        'priority': 'high'
                    })
        
        self.data_science_insights = insights
        return insights
    
    def create_data_science_dashboard(self):
        """Crear dashboard de data science"""
        if not self.data_science_data.empty:
            return None
        
        # Crear subplots
        fig = make_subplots(
            rows=2, cols=2,
            subplot_titles=('Data Quality', 'Correlations',
                          'Distributions', 'Model Performance'),
            specs=[[{"type": "bar"}, {"type": "heatmap"}],
                   [{"type": "histogram"}, {"type": "bar"}]]
        )
        
        # Gráfico de calidad de datos
        if self.data_science_analysis and 'data_quality_analysis' in self.data_science_analysis:
            data_quality = self.data_science_analysis['data_quality_analysis']
            quality_metrics = ['completeness', 'consistency', 'accuracy', 'validity', 'uniqueness']
            quality_scores = [data_quality.get(metric, 0) for metric in quality_metrics]
            
            fig.add_trace(
                go.Bar(x=quality_metrics, y=quality_scores, name='Data Quality Scores'),
                row=1, col=1
            )
        
        # Gráfico de correlaciones
        if self.data_science_analysis and 'correlation_analysis' in self.data_science_analysis:
            correlation_analysis = self.data_science_analysis['correlation_analysis']
            correlation_matrix = correlation_analysis.get('correlation_matrix', {})
            
            if correlation_matrix:
                # Crear heatmap de correlaciones
                corr_data = list(correlation_matrix.values())
                corr_labels = list(correlation_matrix.keys())
                
                fig.add_trace(
                    go.Heatmap(z=corr_data, x=corr_labels, y=corr_labels, name='Correlations'),
                    row=1, col=2
                )
        
        # Gráfico de distribuciones
        if self.data_science_analysis and 'distribution_analysis' in self.data_science_analysis:
            distribution_analysis = self.data_science_analysis['distribution_analysis']
            numeric_distributions = distribution_analysis.get('numeric_distributions', {})
            
            if numeric_distributions:
                # Seleccionar primera variable numérica para histograma
                first_numeric_col = list(numeric_distributions.keys())[0]
                if first_numeric_col in self.data_science_data.columns:
                    fig.add_trace(
                        go.Histogram(x=self.data_science_data[first_numeric_col], name='Distribution'),
                        row=2, col=1
                    )
        
        # Gráfico de performance de modelos
        if self.data_science_models:
            model_evaluation = self.data_science_models.get('model_evaluation', {})
            if model_evaluation:
                model_names = list(model_evaluation.keys())
                model_scores = []
                
                for model_name, metrics in model_evaluation.items():
                    if 'error' not in metrics:
                        if 'accuracy' in metrics:
                            score = metrics['accuracy']
                        elif 'r2' in metrics:
                            score = metrics['r2']
                        else:
                            score = 0
                        model_scores.append(score)
                    else:
                        model_scores.append(0)
                
                fig.add_trace(
                    go.Bar(x=model_names, y=model_scores, name='Model Performance'),
                    row=2, col=2
                )
        
        fig.update_layout(
            title="Dashboard de Data Science",
            showlegend=False,
            height=800
        )
        
        return fig
    
    def export_data_science_analysis(self, filename='marketing_data_science_analysis.json'):
        """Exportar análisis de data science"""
        export_data = {
            'timestamp': datetime.now().isoformat(),
            'data_science_analysis': self.data_science_analysis,
            'data_science_models': {k: {'model_evaluation': v.get('model_evaluation', {})} for k, v in self.data_science_models.items()},
            'data_science_strategies': self.data_science_strategies,
            'data_science_insights': self.data_science_insights,
            'summary': {
                'total_records': len(self.data_science_data),
                'total_columns': len(self.data_science_data.columns),
                'data_quality_score': self._calculate_overall_data_quality(),
                'analysis_date': datetime.now().isoformat()
            }
        }
        
        with open(filename, 'w') as f:
            json.dump(export_data, f, indent=2, default=str)
        
        print(f"✅ Análisis de data science exportado a {filename}")
        return export_data

# Ejemplo de uso
if __name__ == "__main__":
    # Crear instancia del analizador de data science de marketing
    data_science_analyzer = MarketingDataScienceAnalyzer()
    
    # Datos de ejemplo
    sample_data = pd.DataFrame({
        'customer_id': np.random.randint(1, 1000, 1000),
        'age': np.random.normal(35, 10, 1000),
        'income': np.random.normal(50000, 15000, 1000),
        'spending': np.random.normal(1000, 300, 1000),
        'conversion_rate': np.random.uniform(0, 100, 1000),
        'ctr': np.random.uniform(0, 10, 1000),
        'engagement_rate': np.random.uniform(0, 100, 1000),
        'channel': np.random.choice(['Email', 'Social', 'Paid Search', 'Display'], 1000),
        'device': np.random.choice(['Desktop', 'Mobile', 'Tablet'], 1000),
        'location': np.random.choice(['US', 'UK', 'CA', 'AU'], 1000),
        'segment': np.random.choice(['New', 'Active', 'Inactive', 'VIP'], 1000),
        'date': pd.date_range('2023-01-01', periods=1000, freq='D')
    })
    
    # Cargar datos de data science de marketing
    print("📊 Cargando datos de data science de marketing...")
    data_science_analyzer.load_data_science_data(sample_data)
    
    # Analizar insights de data science
    print("🔬 Analizando insights de data science...")
    data_science_analysis = data_science_analyzer.analyze_data_science_insights()
    
    # Construir modelos de data science
    print("🤖 Construyendo modelos de data science...")
    data_science_models = data_science_analyzer.build_data_science_models(target_variable='conversion_rate', model_type='regression')
    
    # Generar estrategias de data science
    print("🎯 Generando estrategias de data science...")
    data_science_strategies = data_science_analyzer.generate_data_science_strategies()
    
    # Generar insights de data science
    print("💡 Generando insights de data science...")
    data_science_insights = data_science_analyzer.generate_data_science_insights()
    
    # Crear dashboard
    print("📊 Creando dashboard de data science...")
    dashboard = data_science_analyzer.create_data_science_dashboard()
    
    # Exportar análisis
    print("💾 Exportando análisis de data science...")
    export_data = data_science_analyzer.export_data_science_analysis()
    
    print("✅ Sistema de análisis de data science de marketing completado!")




