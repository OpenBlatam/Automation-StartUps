"""
Advanced Analytics and Machine Learning for Brand Analysis
Implements predictive analytics, trend analysis, and business intelligence.
"""

import numpy as np
import pandas as pd
import torch
import torch.nn as nn
from typing import Dict, List, Tuple, Optional, Any, Union
import logging
from datetime import datetime, timedelta
import json
from pathlib import Path
import pickle
from collections import defaultdict, deque
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.cluster import KMeans, DBSCAN
from sklearn.decomposition import PCA, t-SNE
from sklearn.preprocessing import StandardScaler, MinMaxScaler
from sklearn.metrics import silhouette_score, calinski_harabasz_score
from sklearn.model_selection import TimeSeriesSplit
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import warnings
warnings.filterwarnings('ignore')

logger = logging.getLogger(__name__)

class BrandTrendAnalyzer:
    """Advanced trend analysis for brand metrics over time."""
    
    def __init__(self, window_size: int = 30, min_data_points: int = 10):
        self.window_size = window_size
        self.min_data_points = min_data_points
        self.trend_data = defaultdict(list)
        self.trend_models = {}
        
    def add_data_point(self, timestamp: datetime, metric: str, value: float, 
                      metadata: Dict[str, Any] = None):
        """Add a new data point for trend analysis."""
        self.trend_data[metric].append({
            'timestamp': timestamp,
            'value': value,
            'metadata': metadata or {}
        })
        
        # Keep only recent data
        if len(self.trend_data[metric]) > self.window_size * 2:
            self.trend_data[metric] = self.trend_data[metric][-self.window_size:]
    
    def detect_trends(self, metric: str) -> Dict[str, Any]:
        """Detect trends in a specific metric."""
        if metric not in self.trend_data or len(self.trend_data[metric]) < self.min_data_points:
            return {'error': 'Insufficient data for trend analysis'}
        
        data = self.trend_data[metric]
        values = [d['value'] for d in data]
        timestamps = [d['timestamp'] for d in data]
        
        # Convert to numpy arrays
        x = np.array([(t - timestamps[0]).total_seconds() / 3600 for t in timestamps])  # Hours
        y = np.array(values)
        
        # Linear trend
        linear_coef = np.polyfit(x, y, 1)
        linear_trend = 'increasing' if linear_coef[0] > 0 else 'decreasing'
        linear_strength = abs(linear_coef[0])
        
        # Polynomial trend (quadratic)
        poly_coef = np.polyfit(x, y, 2)
        poly_trend = 'accelerating' if poly_coef[0] > 0 else 'decelerating'
        
        # Seasonal patterns
        seasonal_pattern = self._detect_seasonality(y)
        
        # Volatility
        volatility = np.std(y) / np.mean(y) if np.mean(y) != 0 else 0
        
        # Anomalies
        anomalies = self._detect_anomalies(y)
        
        # Forecast next period
        forecast = self._forecast_next_period(x, y)
        
        return {
            'metric': metric,
            'data_points': len(data),
            'time_range': {
                'start': timestamps[0].isoformat(),
                'end': timestamps[-1].isoformat()
            },
            'linear_trend': {
                'direction': linear_trend,
                'strength': float(linear_strength),
                'coefficient': float(linear_coef[0])
            },
            'polynomial_trend': {
                'type': poly_trend,
                'coefficients': poly_coef.tolist()
            },
            'seasonal_pattern': seasonal_pattern,
            'volatility': float(volatility),
            'anomalies': anomalies,
            'forecast': forecast,
            'confidence': self._calculate_confidence(x, y)
        }
    
    def _detect_seasonality(self, values: np.ndarray) -> Dict[str, Any]:
        """Detect seasonal patterns in the data."""
        if len(values) < 7:  # Need at least a week of data
            return {'detected': False, 'pattern': 'insufficient_data'}
        
        # Simple seasonality detection using autocorrelation
        from scipy import signal
        
        # Detrend the data
        detrended = signal.detrend(values)
        
        # Calculate autocorrelation
        autocorr = np.correlate(detrended, detrended, mode='full')
        autocorr = autocorr[autocorr.size // 2:]
        
        # Find peaks in autocorrelation
        peaks, _ = signal.find_peaks(autocorr[1:], height=0.1)
        
        if len(peaks) > 0:
            # Find the most significant period
            peak_periods = peaks + 1
            peak_strengths = autocorr[peaks + 1]
            dominant_period = peak_periods[np.argmax(peak_strengths)]
            
            return {
                'detected': True,
                'dominant_period': int(dominant_period),
                'strength': float(np.max(peak_strengths)),
                'all_periods': peak_periods.tolist()
            }
        else:
            return {'detected': False, 'pattern': 'no_seasonality'}
    
    def _detect_anomalies(self, values: np.ndarray, threshold: float = 2.0) -> List[Dict[str, Any]]:
        """Detect anomalies in the data using statistical methods."""
        mean_val = np.mean(values)
        std_val = np.std(values)
        
        anomalies = []
        for i, value in enumerate(values):
            z_score = abs((value - mean_val) / std_val) if std_val > 0 else 0
            if z_score > threshold:
                anomalies.append({
                    'index': i,
                    'value': float(value),
                    'z_score': float(z_score),
                    'severity': 'high' if z_score > 3 else 'medium'
                })
        
        return anomalies
    
    def _forecast_next_period(self, x: np.ndarray, y: np.ndarray, periods: int = 7) -> Dict[str, Any]:
        """Forecast the next period using linear regression."""
        if len(x) < 2:
            return {'forecast': [], 'confidence': 0.0}
        
        # Fit linear model
        coef = np.polyfit(x, y, 1)
        
        # Generate forecast
        last_x = x[-1]
        forecast_x = np.linspace(last_x, last_x + periods * 24, periods)  # Daily forecasts
        forecast_y = np.polyval(coef, forecast_x)
        
        # Calculate confidence interval
        residuals = y - np.polyval(coef, x)
        std_error = np.std(residuals)
        confidence_interval = 1.96 * std_error  # 95% confidence
        
        return {
            'forecast': forecast_y.tolist(),
            'forecast_dates': [(datetime.now() + timedelta(days=i)).isoformat() for i in range(1, periods + 1)],
            'confidence_interval': float(confidence_interval),
            'trend_coefficient': float(coef[0])
        }
    
    def _calculate_confidence(self, x: np.ndarray, y: np.ndarray) -> float:
        """Calculate confidence in the trend analysis."""
        if len(x) < 2:
            return 0.0
        
        # Calculate R-squared
        coef = np.polyfit(x, y, 1)
        y_pred = np.polyval(coef, x)
        ss_res = np.sum((y - y_pred) ** 2)
        ss_tot = np.sum((y - np.mean(y)) ** 2)
        r_squared = 1 - (ss_res / ss_tot) if ss_tot != 0 else 0
        
        # Adjust for data points
        data_quality = min(len(x) / self.window_size, 1.0)
        
        return float(r_squared * data_quality)

class BrandClusterAnalyzer:
    """Advanced clustering analysis for brand segmentation."""
    
    def __init__(self, n_clusters_range: Tuple[int, int] = (2, 10)):
        self.n_clusters_range = n_clusters_range
        self.cluster_models = {}
        self.scaler = StandardScaler()
        
    def analyze_brands(self, brand_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze brand clustering and segmentation."""
        if len(brand_data) < 5:
            return {'error': 'Insufficient data for clustering analysis'}
        
        # Extract features
        features = self._extract_features(brand_data)
        
        # Scale features
        features_scaled = self.scaler.fit_transform(features)
        
        # Find optimal number of clusters
        optimal_clusters = self._find_optimal_clusters(features_scaled)
        
        # Perform clustering
        kmeans = KMeans(n_clusters=optimal_clusters, random_state=42)
        cluster_labels = kmeans.fit_predict(features_scaled)
        
        # Analyze clusters
        cluster_analysis = self._analyze_clusters(brand_data, cluster_labels, features)
        
        # Dimensionality reduction for visualization
        pca_result = self._reduce_dimensions(features_scaled)
        tsne_result = self._reduce_dimensions(features_scaled, method='tsne')
        
        return {
            'optimal_clusters': optimal_clusters,
            'cluster_labels': cluster_labels.tolist(),
            'cluster_analysis': cluster_analysis,
            'pca_components': pca_result.tolist(),
            'tsne_components': tsne_result.tolist(),
            'silhouette_score': float(silhouette_score(features_scaled, cluster_labels)),
            'calinski_harabasz_score': float(calinski_harabasz_score(features_scaled, cluster_labels))
        }
    
    def _extract_features(self, brand_data: List[Dict[str, Any]]) -> np.ndarray:
        """Extract numerical features from brand data."""
        features = []
        
        for brand in brand_data:
            feature_vector = []
            
            # Color features
            if 'colors' in brand:
                colors = np.array(brand['colors'])
                feature_vector.extend([
                    np.mean(colors, axis=0).tolist(),  # Mean RGB
                    np.std(colors, axis=0).tolist(),   # Std RGB
                    len(colors)  # Number of colors
                ])
            else:
                feature_vector.extend([0, 0, 0, 0, 0, 0, 0])  # Default values
            
            # Typography features
            if 'typography' in brand:
                typography = np.array(brand['typography'])
                feature_vector.extend([
                    np.mean(typography),
                    np.std(typography),
                    len(typography)
                ])
            else:
                feature_vector.extend([0, 0, 0])
            
            # Layout features
            if 'layout' in brand:
                layout = np.array(brand['layout'])
                feature_vector.extend([
                    np.mean(layout),
                    np.std(layout),
                    len(layout)
                ])
            else:
                feature_vector.extend([0, 0, 0])
            
            # Text features
            if 'text_features' in brand:
                text_features = np.array(brand['text_features'])
                feature_vector.extend([
                    np.mean(text_features),
                    np.std(text_features),
                    len(text_features)
                ])
            else:
                feature_vector.extend([0, 0, 0])
            
            # Consistency score
            if 'consistency_score' in brand:
                feature_vector.append(brand['consistency_score'])
            else:
                feature_vector.append(0.5)  # Default consistency
            
            features.append(feature_vector)
        
        return np.array(features)
    
    def _find_optimal_clusters(self, features: np.ndarray) -> int:
        """Find optimal number of clusters using elbow method and silhouette analysis."""
        if features.shape[0] < 3:
            return 2
        
        silhouette_scores = []
        inertias = []
        
        for k in range(self.n_clusters_range[0], min(self.n_clusters_range[1] + 1, features.shape[0])):
            kmeans = KMeans(n_clusters=k, random_state=42)
            cluster_labels = kmeans.fit_predict(features)
            
            silhouette_scores.append(silhouette_score(features, cluster_labels))
            inertias.append(kmeans.inertia_)
        
        # Find optimal k using silhouette score
        optimal_k = self.n_clusters_range[0] + np.argmax(silhouette_scores)
        
        return optimal_k
    
    def _analyze_clusters(self, brand_data: List[Dict[str, Any]], 
                         cluster_labels: np.ndarray, 
                         features: np.ndarray) -> Dict[str, Any]:
        """Analyze the characteristics of each cluster."""
        n_clusters = len(np.unique(cluster_labels))
        cluster_analysis = {}
        
        for cluster_id in range(n_clusters):
            cluster_mask = cluster_labels == cluster_id
            cluster_brands = [brand_data[i] for i in range(len(brand_data)) if cluster_mask[i]]
            cluster_features = features[cluster_mask]
            
            # Calculate cluster statistics
            cluster_stats = {
                'size': int(np.sum(cluster_mask)),
                'percentage': float(np.sum(cluster_mask) / len(brand_data) * 100),
                'avg_consistency': float(np.mean([b.get('consistency_score', 0.5) for b in cluster_brands])),
                'feature_means': cluster_features.mean(axis=0).tolist(),
                'feature_stds': cluster_features.std(axis=0).tolist()
            }
            
            # Identify dominant characteristics
            dominant_characteristics = self._identify_dominant_characteristics(cluster_brands)
            cluster_stats['dominant_characteristics'] = dominant_characteristics
            
            cluster_analysis[f'cluster_{cluster_id}'] = cluster_stats
        
        return cluster_analysis
    
    def _identify_dominant_characteristics(self, cluster_brands: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Identify dominant characteristics of a cluster."""
        characteristics = {
            'color_diversity': 0,
            'typography_complexity': 0,
            'layout_consistency': 0,
            'text_sophistication': 0
        }
        
        if not cluster_brands:
            return characteristics
        
        # Analyze color diversity
        color_counts = []
        for brand in cluster_brands:
            if 'colors' in brand:
                color_counts.append(len(brand['colors']))
        characteristics['color_diversity'] = float(np.mean(color_counts)) if color_counts else 0
        
        # Analyze typography complexity
        typography_lengths = []
        for brand in cluster_brands:
            if 'typography' in brand:
                typography_lengths.append(len(brand['typography']))
        characteristics['typography_complexity'] = float(np.mean(typography_lengths)) if typography_lengths else 0
        
        # Analyze layout consistency
        consistency_scores = [brand.get('consistency_score', 0.5) for brand in cluster_brands]
        characteristics['layout_consistency'] = float(np.mean(consistency_scores))
        
        # Analyze text sophistication
        text_lengths = []
        for brand in cluster_brands:
            if 'text_features' in brand:
                text_lengths.append(len(brand['text_features']))
        characteristics['text_sophistication'] = float(np.mean(text_lengths)) if text_lengths else 0
        
        return characteristics
    
    def _reduce_dimensions(self, features: np.ndarray, method: str = 'pca') -> np.ndarray:
        """Reduce dimensions for visualization."""
        if method == 'pca':
            pca = PCA(n_components=2)
            return pca.fit_transform(features)
        elif method == 'tsne':
            from sklearn.manifold import TSNE
            tsne = TSNE(n_components=2, random_state=42)
            return tsne.fit_transform(features)
        else:
            raise ValueError(f"Unknown method: {method}")

class PredictiveAnalytics:
    """Predictive analytics for brand performance and trends."""
    
    def __init__(self):
        self.models = {}
        self.feature_importance = {}
        self.prediction_history = []
        
    def train_predictive_models(self, training_data: List[Dict[str, Any]], 
                              target_variable: str = 'consistency_score') -> Dict[str, Any]:
        """Train predictive models for brand performance."""
        logger.info(f"Training predictive models for target: {target_variable}")
        
        # Prepare training data
        X, y = self._prepare_training_data(training_data, target_variable)
        
        if len(X) < 10:
            return {'error': 'Insufficient training data'}
        
        # Split data for validation
        tscv = TimeSeriesSplit(n_splits=3)
        scores = {}
        
        # Train Random Forest
        rf_model = RandomForestRegressor(n_estimators=100, random_state=42)
        rf_scores = []
        for train_idx, val_idx in tscv.split(X):
            X_train, X_val = X[train_idx], X[val_idx]
            y_train, y_val = y[train_idx], y[val_idx]
            
            rf_model.fit(X_train, y_train)
            score = rf_model.score(X_val, y_val)
            rf_scores.append(score)
        
        self.models['random_forest'] = rf_model
        scores['random_forest'] = {
            'mean_score': float(np.mean(rf_scores)),
            'std_score': float(np.std(rf_scores))
        }
        
        # Train Gradient Boosting
        gb_model = GradientBoostingRegressor(n_estimators=100, random_state=42)
        gb_scores = []
        for train_idx, val_idx in tscv.split(X):
            X_train, X_val = X[train_idx], X[val_idx]
            y_train, y_val = y[train_idx], y[val_idx]
            
            gb_model.fit(X_train, y_train)
            score = gb_model.score(X_val, y_val)
            gb_scores.append(score)
        
        self.models['gradient_boosting'] = gb_model
        scores['gradient_boosting'] = {
            'mean_score': float(np.mean(gb_scores)),
            'std_score': float(np.std(gb_scores))
        }
        
        # Calculate feature importance
        self.feature_importance = {
            'random_forest': rf_model.feature_importances_.tolist(),
            'gradient_boosting': gb_model.feature_importances_.tolist()
        }
        
        return {
            'models_trained': list(self.models.keys()),
            'scores': scores,
            'feature_importance': self.feature_importance,
            'training_samples': len(X)
        }
    
    def predict_brand_performance(self, brand_data: Dict[str, Any]) -> Dict[str, Any]:
        """Predict brand performance for a given brand."""
        if not self.models:
            return {'error': 'No models trained. Call train_predictive_models first.'}
        
        # Prepare features
        X = self._prepare_single_sample(brand_data)
        
        predictions = {}
        for model_name, model in self.models.items():
            prediction = model.predict(X.reshape(1, -1))[0]
            predictions[model_name] = float(prediction)
        
        # Ensemble prediction
        ensemble_prediction = np.mean(list(predictions.values()))
        
        # Store prediction history
        self.prediction_history.append({
            'timestamp': datetime.now().isoformat(),
            'predictions': predictions,
            'ensemble_prediction': float(ensemble_prediction),
            'input_data': brand_data
        })
        
        return {
            'predictions': predictions,
            'ensemble_prediction': float(ensemble_prediction),
            'confidence': self._calculate_prediction_confidence(predictions),
            'feature_importance': self.feature_importance
        }
    
    def _prepare_training_data(self, data: List[Dict[str, Any]], 
                             target_variable: str) -> Tuple[np.ndarray, np.ndarray]:
        """Prepare training data for machine learning models."""
        X = []
        y = []
        
        for item in data:
            features = self._extract_ml_features(item)
            target = item.get(target_variable, 0.5)
            
            X.append(features)
            y.append(target)
        
        return np.array(X), np.array(y)
    
    def _prepare_single_sample(self, brand_data: Dict[str, Any]) -> np.ndarray:
        """Prepare a single sample for prediction."""
        return np.array(self._extract_ml_features(brand_data))
    
    def _extract_ml_features(self, brand_data: Dict[str, Any]) -> List[float]:
        """Extract features for machine learning models."""
        features = []
        
        # Color features
        if 'colors' in brand_data:
            colors = np.array(brand_data['colors'])
            features.extend([
                np.mean(colors, axis=0).tolist(),  # Mean RGB
                np.std(colors, axis=0).tolist(),   # Std RGB
                len(colors),  # Number of colors
                np.var(colors)  # Color variance
            ])
        else:
            features.extend([0, 0, 0, 0, 0, 0, 0, 0])  # Default values
        
        # Typography features
        if 'typography' in brand_data:
            typography = np.array(brand_data['typography'])
            features.extend([
                np.mean(typography),
                np.std(typography),
                len(typography),
                np.var(typography)
            ])
        else:
            features.extend([0, 0, 0, 0])
        
        # Layout features
        if 'layout' in brand_data:
            layout = np.array(brand_data['layout'])
            features.extend([
                np.mean(layout),
                np.std(layout),
                len(layout),
                np.var(layout)
            ])
        else:
            features.extend([0, 0, 0, 0])
        
        # Text features
        if 'text_features' in brand_data:
            text_features = np.array(brand_data['text_features'])
            features.extend([
                np.mean(text_features),
                np.std(text_features),
                len(text_features),
                np.var(text_features)
            ])
        else:
            features.extend([0, 0, 0, 0])
        
        return features
    
    def _calculate_prediction_confidence(self, predictions: Dict[str, float]) -> float:
        """Calculate confidence in predictions based on model agreement."""
        if len(predictions) < 2:
            return 1.0
        
        values = list(predictions.values())
        std_dev = np.std(values)
        mean_val = np.mean(values)
        
        # Confidence based on coefficient of variation
        if mean_val != 0:
            cv = std_dev / abs(mean_val)
            confidence = max(0, 1 - cv)
        else:
            confidence = 1.0
        
        return float(confidence)

class BusinessIntelligence:
    """Business intelligence and reporting for brand analytics."""
    
    def __init__(self):
        self.trend_analyzer = BrandTrendAnalyzer()
        self.cluster_analyzer = BrandClusterAnalyzer()
        self.predictive_analytics = PredictiveAnalytics()
        self.reports = {}
        
    def generate_comprehensive_report(self, brand_data: List[Dict[str, Any]], 
                                    time_series_data: Optional[Dict[str, List[Dict[str, Any]]]] = None) -> Dict[str, Any]:
        """Generate a comprehensive business intelligence report."""
        logger.info("Generating comprehensive BI report...")
        
        report = {
            'timestamp': datetime.now().isoformat(),
            'data_summary': self._summarize_data(brand_data),
            'trend_analysis': {},
            'cluster_analysis': {},
            'predictive_insights': {},
            'recommendations': []
        }
        
        # Trend analysis
        if time_series_data:
            for metric, data in time_series_data.items():
                for data_point in data:
                    self.trend_analyzer.add_data_point(
                        datetime.fromisoformat(data_point['timestamp']),
                        metric,
                        data_point['value'],
                        data_point.get('metadata', {})
                    )
                
                trend_result = self.trend_analyzer.detect_trends(metric)
                report['trend_analysis'][metric] = trend_result
        
        # Cluster analysis
        cluster_result = self.cluster_analyzer.analyze_brands(brand_data)
        report['cluster_analysis'] = cluster_result
        
        # Predictive analytics
        if len(brand_data) >= 10:
            predictive_result = self.predictive_analytics.train_predictive_models(brand_data)
            report['predictive_insights'] = predictive_result
        
        # Generate recommendations
        report['recommendations'] = self._generate_recommendations(report)
        
        # Store report
        report_id = f"report_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        self.reports[report_id] = report
        
        return report
    
    def _summarize_data(self, brand_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Summarize the input data."""
        if not brand_data:
            return {'error': 'No data provided'}
        
        consistency_scores = [brand.get('consistency_score', 0.5) for brand in brand_data]
        
        return {
            'total_brands': len(brand_data),
            'consistency_stats': {
                'mean': float(np.mean(consistency_scores)),
                'std': float(np.std(consistency_scores)),
                'min': float(np.min(consistency_scores)),
                'max': float(np.max(consistency_scores)),
                'median': float(np.median(consistency_scores))
            },
            'data_quality': self._assess_data_quality(brand_data)
        }
    
    def _assess_data_quality(self, brand_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Assess the quality of the input data."""
        total_brands = len(brand_data)
        
        # Check for missing fields
        missing_fields = defaultdict(int)
        for brand in brand_data:
            for field in ['colors', 'typography', 'layout', 'text_features']:
                if field not in brand or not brand[field]:
                    missing_fields[field] += 1
        
        # Calculate completeness
        completeness = {}
        for field, missing_count in missing_fields.items():
            completeness[field] = float((total_brands - missing_count) / total_brands)
        
        return {
            'overall_completeness': float(np.mean(list(completeness.values()))),
            'field_completeness': completeness,
            'total_brands': total_brands
        }
    
    def _generate_recommendations(self, report: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate actionable recommendations based on the analysis."""
        recommendations = []
        
        # Data quality recommendations
        data_summary = report.get('data_summary', {})
        data_quality = data_summary.get('data_quality', {})
        
        if data_quality.get('overall_completeness', 1.0) < 0.8:
            recommendations.append({
                'type': 'data_quality',
                'priority': 'high',
                'title': 'Improve Data Quality',
                'description': 'Data completeness is below 80%. Consider collecting more complete brand data.',
                'action': 'Review data collection process and ensure all required fields are populated.'
            })
        
        # Consistency recommendations
        consistency_stats = data_summary.get('consistency_stats', {})
        if consistency_stats.get('mean', 0.5) < 0.7:
            recommendations.append({
                'type': 'consistency',
                'priority': 'medium',
                'title': 'Improve Brand Consistency',
                'description': f"Average consistency score is {consistency_stats.get('mean', 0):.2f}. Consider standardizing brand elements.",
                'action': 'Review brand guidelines and ensure consistent application across all touchpoints.'
            })
        
        # Trend-based recommendations
        trend_analysis = report.get('trend_analysis', {})
        for metric, trend_data in trend_analysis.items():
            if isinstance(trend_data, dict) and 'linear_trend' in trend_data:
                trend_direction = trend_data['linear_trend'].get('direction', 'stable')
                if trend_direction == 'decreasing':
                    recommendations.append({
                        'type': 'trend',
                        'priority': 'medium',
                        'title': f'Address Declining {metric.title()}',
                        'description': f'{metric} is showing a declining trend. Immediate attention may be required.',
                        'action': f'Investigate causes of declining {metric} and implement corrective measures.'
                    })
        
        # Cluster-based recommendations
        cluster_analysis = report.get('cluster_analysis', {})
        if 'cluster_analysis' in cluster_analysis:
            cluster_count = cluster_analysis.get('optimal_clusters', 0)
            if cluster_count > 1:
                recommendations.append({
                    'type': 'segmentation',
                    'priority': 'low',
                    'title': 'Consider Brand Segmentation',
                    'description': f'Data shows {cluster_count} distinct brand clusters. Consider targeted strategies for each segment.',
                    'action': 'Develop cluster-specific brand strategies and messaging.'
                })
        
        return recommendations
    
    def export_report(self, report_id: str, format: str = 'json') -> str:
        """Export a report in the specified format."""
        if report_id not in self.reports:
            raise ValueError(f"Report {report_id} not found")
        
        report = self.reports[report_id]
        
        if format == 'json':
            return json.dumps(report, indent=2)
        elif format == 'csv':
            # Convert to CSV format (simplified)
            return self._convert_to_csv(report)
        else:
            raise ValueError(f"Unsupported format: {format}")
    
    def _convert_to_csv(self, report: Dict[str, Any]) -> str:
        """Convert report to CSV format."""
        # This is a simplified CSV conversion
        # In practice, you'd want more sophisticated CSV generation
        import io
        output = io.StringIO()
        
        # Write summary data
        output.write("Metric,Value\n")
        data_summary = report.get('data_summary', {})
        output.write(f"Total Brands,{data_summary.get('total_brands', 0)}\n")
        
        consistency_stats = data_summary.get('consistency_stats', {})
        for stat, value in consistency_stats.items():
            output.write(f"Consistency {stat},{value}\n")
        
        return output.getvalue()










