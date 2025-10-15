"""
Predictive Analytics Engine for Ultimate Launch Planning System
Provides advanced forecasting, trend analysis, and predictive insights
"""

import numpy as np
import pandas as pd
import json
import time
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple, Union
from dataclasses import dataclass, asdict
from collections import defaultdict, deque
import logging
from enum import Enum
import warnings
from sklearn.ensemble import IsolationForest
from sklearn.cluster import KMeans
from sklearn.decomposition import PCA
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import silhouette_score
import matplotlib.pyplot as plt
import seaborn as sns
warnings.filterwarnings('ignore')

logger = logging.getLogger(__name__)

class ForecastType(Enum):
    SUCCESS_PROBABILITY = "success_probability"
    BUDGET_UTILIZATION = "budget_utilization"
    TIMELINE_ADHERENCE = "timeline_adherence"
    MARKET_RESPONSE = "market_response"
    TEAM_PERFORMANCE = "team_performance"
    RISK_ESCALATION = "risk_escalation"

class TrendDirection(Enum):
    INCREASING = "increasing"
    DECREASING = "decreasing"
    STABLE = "stable"
    VOLATILE = "volatile"

@dataclass
class ForecastResult:
    forecast_type: ForecastType
    current_value: float
    predicted_value: float
    confidence_interval: Tuple[float, float]
    trend_direction: TrendDirection
    trend_strength: float
    forecast_horizon_days: int
    timestamp: datetime
    metadata: Dict[str, Any]
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "forecast_type": self.forecast_type.value,
            "current_value": self.current_value,
            "predicted_value": self.predicted_value,
            "confidence_interval": self.confidence_interval,
            "trend_direction": self.trend_direction.value,
            "trend_strength": self.trend_strength,
            "forecast_horizon_days": self.forecast_horizon_days,
            "timestamp": self.timestamp.isoformat(),
            "metadata": self.metadata
        }

@dataclass
class AnomalyDetection:
    anomaly_type: str
    severity: str
    detected_at: datetime
    value: float
    expected_value: float
    deviation: float
    context: Dict[str, Any]
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "anomaly_type": self.anomaly_type,
            "severity": self.severity,
            "detected_at": self.detected_at.isoformat(),
            "value": self.value,
            "expected_value": self.expected_value,
            "deviation": self.deviation,
            "context": self.context
        }

@dataclass
class ClusterAnalysis:
    cluster_id: int
    cluster_size: int
    centroid: List[float]
    characteristics: Dict[str, Any]
    similarity_score: float
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "cluster_id": self.cluster_id,
            "cluster_size": self.cluster_size,
            "centroid": self.centroid,
            "characteristics": self.characteristics,
            "similarity_score": self.similarity_score
        }

class TimeSeriesAnalyzer:
    """Advanced time series analysis for launch metrics"""
    
    def __init__(self, window_size: int = 30):
        self.window_size = window_size
        self.data_buffer: Dict[str, deque] = defaultdict(lambda: deque(maxlen=1000))
        self.trend_cache: Dict[str, Dict] = {}
    
    def add_data_point(self, metric_name: str, value: float, timestamp: datetime = None):
        """Add a data point to time series"""
        if timestamp is None:
            timestamp = datetime.now()
        
        self.data_buffer[metric_name].append({
            'timestamp': timestamp,
            'value': value
        })
    
    def detect_trend(self, metric_name: str, lookback_days: int = 7) -> Dict[str, Any]:
        """Detect trend in time series data"""
        if metric_name not in self.data_buffer:
            return {"error": "No data available"}
        
        data = list(self.data_buffer[metric_name])
        if len(data) < 3:
            return {"error": "Insufficient data"}
        
        # Filter data by lookback period
        cutoff_time = datetime.now() - timedelta(days=lookback_days)
        recent_data = [d for d in data if d['timestamp'] >= cutoff_time]
        
        if len(recent_data) < 3:
            return {"error": "Insufficient recent data"}
        
        # Calculate trend
        values = [d['value'] for d in recent_data]
        timestamps = [d['timestamp'] for d in recent_data]
        
        # Simple linear regression for trend
        x = np.arange(len(values))
        y = np.array(values)
        
        # Calculate slope
        slope = np.polyfit(x, y, 1)[0]
        
        # Calculate trend strength (R²)
        y_pred = np.polyval(np.polyfit(x, y, 1), x)
        ss_res = np.sum((y - y_pred) ** 2)
        ss_tot = np.sum((y - np.mean(y)) ** 2)
        r_squared = 1 - (ss_res / ss_tot) if ss_tot != 0 else 0
        
        # Determine trend direction
        if abs(slope) < 0.01:
            direction = TrendDirection.STABLE
        elif slope > 0:
            direction = TrendDirection.INCREASING
        else:
            direction = TrendDirection.DECREASING
        
        # Check for volatility
        volatility = np.std(values) / np.mean(values) if np.mean(values) != 0 else 0
        if volatility > 0.2:
            direction = TrendDirection.VOLATILE
        
        trend_info = {
            "metric_name": metric_name,
            "direction": direction.value,
            "slope": slope,
            "strength": r_squared,
            "volatility": volatility,
            "data_points": len(recent_data),
            "current_value": values[-1],
            "change_percent": ((values[-1] - values[0]) / values[0] * 100) if values[0] != 0 else 0
        }
        
        self.trend_cache[metric_name] = trend_info
        return trend_info
    
    def forecast_value(self, metric_name: str, horizon_days: int = 7) -> ForecastResult:
        """Forecast future value based on trend"""
        trend_info = self.detect_trend(metric_name)
        
        if "error" in trend_info:
            return ForecastResult(
                forecast_type=ForecastType.SUCCESS_PROBABILITY,
                current_value=0.0,
                predicted_value=0.0,
                confidence_interval=(0.0, 0.0),
                trend_direction=TrendDirection.STABLE,
                trend_strength=0.0,
                forecast_horizon_days=horizon_days,
                timestamp=datetime.now(),
                metadata={"error": trend_info["error"]}
            )
        
        current_value = trend_info["current_value"]
        slope = trend_info["slope"]
        strength = trend_info["strength"]
        
        # Simple linear forecast
        predicted_value = current_value + (slope * horizon_days)
        
        # Calculate confidence interval (simplified)
        volatility = trend_info["volatility"]
        confidence_margin = current_value * volatility * 0.5
        confidence_interval = (
            max(0, predicted_value - confidence_margin),
            predicted_value + confidence_margin
        )
        
        return ForecastResult(
            forecast_type=ForecastType.SUCCESS_PROBABILITY,
            current_value=current_value,
            predicted_value=predicted_value,
            confidence_interval=confidence_interval,
            trend_direction=TrendDirection(trend_info["direction"]),
            trend_strength=strength,
            forecast_horizon_days=horizon_days,
            timestamp=datetime.now(),
            metadata=trend_info
        )

class AnomalyDetector:
    """Advanced anomaly detection for launch metrics"""
    
    def __init__(self):
        self.isolation_forest = IsolationForest(contamination=0.1, random_state=42)
        self.scaler = StandardScaler()
        self.is_fitted = False
        self.anomaly_history: deque = deque(maxlen=1000)
    
    def fit_model(self, data: np.ndarray):
        """Fit anomaly detection model"""
        if len(data) < 10:
            logger.warning("Insufficient data for anomaly detection model fitting")
            return
        
        try:
            # Scale data
            data_scaled = self.scaler.fit_transform(data)
            
            # Fit isolation forest
            self.isolation_forest.fit(data_scaled)
            self.is_fitted = True
            
            logger.info("Anomaly detection model fitted successfully")
        except Exception as e:
            logger.error(f"Error fitting anomaly detection model: {e}")
    
    def detect_anomalies(self, data: np.ndarray, context: Dict[str, Any] = None) -> List[AnomalyDetection]:
        """Detect anomalies in data"""
        if not self.is_fitted:
            logger.warning("Anomaly detection model not fitted")
            return []
        
        try:
            # Scale data
            data_scaled = self.scaler.transform(data)
            
            # Predict anomalies
            anomaly_scores = self.isolation_forest.decision_function(data_scaled)
            anomaly_predictions = self.isolation_forest.predict(data_scaled)
            
            anomalies = []
            for i, (score, prediction) in enumerate(zip(anomaly_scores, anomaly_predictions)):
                if prediction == -1:  # Anomaly detected
                    severity = "high" if score < -0.5 else "medium" if score < -0.2 else "low"
                    
                    anomaly = AnomalyDetection(
                        anomaly_type="statistical_anomaly",
                        severity=severity,
                        detected_at=datetime.now(),
                        value=float(data[i].mean()) if len(data[i].shape) > 0 else float(data[i]),
                        expected_value=float(data.mean()),
                        deviation=abs(score),
                        context=context or {}
                    )
                    
                    anomalies.append(anomaly)
                    self.anomaly_history.append(anomaly)
            
            return anomalies
            
        except Exception as e:
            logger.error(f"Error detecting anomalies: {e}")
            return []
    
    def get_anomaly_summary(self) -> Dict[str, Any]:
        """Get summary of detected anomalies"""
        if not self.anomaly_history:
            return {"total_anomalies": 0}
        
        anomalies = list(self.anomaly_history)
        severity_counts = defaultdict(int)
        
        for anomaly in anomalies:
            severity_counts[anomaly.severity] += 1
        
        return {
            "total_anomalies": len(anomalies),
            "severity_breakdown": dict(severity_counts),
            "recent_anomalies": [a.to_dict() for a in anomalies[-5:]]
        }

class ClusterAnalyzer:
    """Advanced clustering analysis for launch data"""
    
    def __init__(self):
        self.kmeans = KMeans(n_clusters=3, random_state=42)
        self.pca = PCA(n_components=2)
        self.scaler = StandardScaler()
        self.is_fitted = False
        self.cluster_centers = None
    
    def fit_model(self, data: np.ndarray, n_clusters: int = 3):
        """Fit clustering model"""
        if len(data) < n_clusters * 2:
            logger.warning("Insufficient data for clustering")
            return
        
        try:
            # Scale data
            data_scaled = self.scaler.fit_transform(data)
            
            # Fit K-means
            self.kmeans = KMeans(n_clusters=n_clusters, random_state=42)
            self.kmeans.fit(data_scaled)
            
            # Fit PCA for visualization
            self.pca.fit(data_scaled)
            
            self.is_fitted = True
            self.cluster_centers = self.kmeans.cluster_centers_
            
            # Calculate silhouette score
            labels = self.kmeans.labels_
            silhouette_avg = silhouette_score(data_scaled, labels)
            
            logger.info(f"Clustering model fitted with {n_clusters} clusters, silhouette score: {silhouette_avg:.3f}")
            
        except Exception as e:
            logger.error(f"Error fitting clustering model: {e}")
    
    def analyze_clusters(self, data: np.ndarray, feature_names: List[str] = None) -> List[ClusterAnalysis]:
        """Analyze clusters in data"""
        if not self.is_fitted:
            logger.warning("Clustering model not fitted")
            return []
        
        try:
            # Scale data
            data_scaled = self.scaler.transform(data)
            
            # Predict clusters
            cluster_labels = self.kmeans.predict(data_scaled)
            
            # Analyze each cluster
            clusters = []
            for cluster_id in range(self.kmeans.n_clusters):
                cluster_mask = cluster_labels == cluster_id
                cluster_data = data[cluster_mask]
                
                if len(cluster_data) == 0:
                    continue
                
                # Calculate cluster characteristics
                centroid = self.kmeans.cluster_centers_[cluster_id].tolist()
                characteristics = {}
                
                if feature_names:
                    for i, feature_name in enumerate(feature_names):
                        if i < len(centroid):
                            characteristics[feature_name] = {
                                "mean": float(cluster_data[:, i].mean()) if len(cluster_data) > 0 else 0,
                                "std": float(cluster_data[:, i].std()) if len(cluster_data) > 0 else 0,
                                "centroid": centroid[i]
                            }
                
                # Calculate similarity score (distance from centroid)
                distances = np.linalg.norm(data_scaled[cluster_mask] - centroid, axis=1)
                similarity_score = 1.0 - (distances.mean() / np.linalg.norm(centroid))
                
                cluster_analysis = ClusterAnalysis(
                    cluster_id=cluster_id,
                    cluster_size=int(cluster_mask.sum()),
                    centroid=centroid,
                    characteristics=characteristics,
                    similarity_score=float(similarity_score)
                )
                
                clusters.append(cluster_analysis)
            
            return clusters
            
        except Exception as e:
            logger.error(f"Error analyzing clusters: {e}")
            return []

class PredictiveAnalyticsEngine:
    """Main predictive analytics engine"""
    
    def __init__(self):
        self.time_series_analyzer = TimeSeriesAnalyzer()
        self.anomaly_detector = AnomalyDetector()
        self.cluster_analyzer = ClusterAnalyzer()
        self.forecast_cache: Dict[str, ForecastResult] = {}
        self.analytics_history: deque = deque(maxlen=1000)
    
    def add_metric_data(self, metric_name: str, value: float, timestamp: datetime = None):
        """Add metric data for analysis"""
        self.time_series_analyzer.add_data_point(metric_name, value, timestamp)
    
    def generate_forecasts(self, metric_names: List[str], horizon_days: int = 7) -> Dict[str, ForecastResult]:
        """Generate forecasts for multiple metrics"""
        forecasts = {}
        
        for metric_name in metric_names:
            try:
                forecast = self.time_series_analyzer.forecast_value(metric_name, horizon_days)
                forecasts[metric_name] = forecast
                self.forecast_cache[metric_name] = forecast
            except Exception as e:
                logger.error(f"Error generating forecast for {metric_name}: {e}")
        
        return forecasts
    
    def detect_metric_anomalies(self, metric_data: Dict[str, List[float]]) -> Dict[str, List[AnomalyDetection]]:
        """Detect anomalies in metric data"""
        anomalies = {}
        
        for metric_name, values in metric_data.items():
            if len(values) < 10:
                continue
            
            try:
                data_array = np.array(values).reshape(-1, 1)
                
                # Fit model if not already fitted
                if not self.anomaly_detector.is_fitted:
                    self.anomaly_detector.fit_model(data_array)
                
                # Detect anomalies
                metric_anomalies = self.anomaly_detector.detect_anomalies(
                    data_array, 
                    context={"metric_name": metric_name}
                )
                
                if metric_anomalies:
                    anomalies[metric_name] = metric_anomalies
                    
            except Exception as e:
                logger.error(f"Error detecting anomalies for {metric_name}: {e}")
        
        return anomalies
    
    def analyze_launch_patterns(self, launch_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze patterns in launch data"""
        if len(launch_data) < 5:
            return {"error": "Insufficient data for pattern analysis"}
        
        try:
            # Prepare data for clustering
            feature_columns = [
                'budget', 'team_size', 'timeline_days', 'success_rate',
                'market_size', 'competition_level', 'product_complexity'
            ]
            
            data_matrix = []
            for launch in launch_data:
                row = []
                for col in feature_columns:
                    value = launch.get(col, 0)
                    if isinstance(value, str):
                        value = hash(value) % 100  # Simple encoding
                    row.append(float(value))
                data_matrix.append(row)
            
            data_array = np.array(data_matrix)
            
            # Perform clustering
            self.cluster_analyzer.fit_model(data_array, n_clusters=min(3, len(launch_data) // 2))
            clusters = self.cluster_analyzer.analyze_clusters(data_array, feature_columns)
            
            # Analyze trends
            trends = {}
            for col in feature_columns:
                values = [launch.get(col, 0) for launch in launch_data]
                if all(isinstance(v, (int, float)) for v in values):
                    for i, value in enumerate(values):
                        self.add_metric_data(f"{col}_trend", float(value))
                    trend_info = self.time_series_analyzer.detect_trend(f"{col}_trend")
                    if "error" not in trend_info:
                        trends[col] = trend_info
            
            return {
                "clusters": [cluster.to_dict() for cluster in clusters],
                "trends": trends,
                "total_launches": len(launch_data),
                "analysis_timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error analyzing launch patterns: {e}")
            return {"error": str(e)}
    
    def generate_insights(self, launch_id: str, metrics: Dict[str, List[float]]) -> Dict[str, Any]:
        """Generate comprehensive predictive insights"""
        insights = {
            "launch_id": launch_id,
            "timestamp": datetime.now().isoformat(),
            "forecasts": {},
            "anomalies": {},
            "trends": {},
            "recommendations": [],
            "risk_indicators": []
        }
        
        # Generate forecasts
        metric_names = list(metrics.keys())
        forecasts = self.generate_forecasts(metric_names, horizon_days=14)
        insights["forecasts"] = {name: forecast.to_dict() for name, forecast in forecasts.items()}
        
        # Detect anomalies
        anomalies = self.detect_metric_anomalies(metrics)
        insights["anomalies"] = {
            name: [anomaly.to_dict() for anomaly in anomaly_list] 
            for name, anomaly_list in anomalies.items()
        }
        
        # Analyze trends
        for metric_name in metric_names:
            trend_info = self.time_series_analyzer.detect_trend(metric_name)
            if "error" not in trend_info:
                insights["trends"][metric_name] = trend_info
        
        # Generate recommendations based on analysis
        for metric_name, forecast in forecasts.items():
            if forecast.trend_direction == TrendDirection.DECREASING:
                insights["recommendations"].append({
                    "type": "trend_alert",
                    "metric": metric_name,
                    "message": f"{metric_name} is trending downward. Consider intervention.",
                    "priority": "medium"
                })
            
            if forecast.confidence_interval[0] < 0.3:  # Low confidence
                insights["recommendations"].append({
                    "type": "confidence_alert",
                    "metric": metric_name,
                    "message": f"Low confidence in {metric_name} forecast. More data needed.",
                    "priority": "low"
                })
        
        # Risk indicators
        for metric_name, anomaly_list in anomalies.items():
            high_severity_anomalies = [a for a in anomaly_list if a.severity == "high"]
            if high_severity_anomalies:
                insights["risk_indicators"].append({
                    "type": "anomaly_risk",
                    "metric": metric_name,
                    "count": len(high_severity_anomalies),
                    "message": f"High severity anomalies detected in {metric_name}"
                })
        
        self.analytics_history.append(insights)
        return insights
    
    def get_analytics_summary(self) -> Dict[str, Any]:
        """Get summary of analytics activities"""
        return {
            "total_forecasts": len(self.forecast_cache),
            "anomaly_summary": self.anomaly_detector.get_anomaly_summary(),
            "analytics_history_count": len(self.analytics_history),
            "trend_cache_size": len(self.time_series_analyzer.trend_cache),
            "last_analysis": self.analytics_history[-1] if self.analytics_history else None
        }

# Global predictive analytics instance
_predictive_analytics = None

def get_predictive_analytics() -> PredictiveAnalyticsEngine:
    """Get global predictive analytics instance"""
    global _predictive_analytics
    if _predictive_analytics is None:
        _predictive_analytics = PredictiveAnalyticsEngine()
    return _predictive_analytics

# Example usage
if __name__ == "__main__":
    # Initialize predictive analytics
    analytics = get_predictive_analytics()
    
    # Simulate some metric data
    import random
    
    # Add time series data
    for i in range(30):
        success_rate = 0.5 + 0.3 * np.sin(i * 0.2) + random.gauss(0, 0.05)
        budget_util = 0.3 + 0.4 * (i / 30) + random.gauss(0, 0.1)
        timeline_adherence = 0.8 - 0.2 * (i / 30) + random.gauss(0, 0.1)
        
        analytics.add_metric_data("success_rate", max(0, min(1, success_rate)))
        analytics.add_metric_data("budget_utilization", max(0, min(1, budget_util)))
        analytics.add_metric_data("timeline_adherence", max(0, min(1, timeline_adherence)))
    
    # Generate forecasts
    forecasts = analytics.generate_forecasts(["success_rate", "budget_utilization", "timeline_adherence"])
    print("Forecasts:")
    for name, forecast in forecasts.items():
        print(f"{name}: {forecast.predicted_value:.3f} ({forecast.trend_direction.value})")
    
    # Detect anomalies
    metric_data = {
        "success_rate": [0.8, 0.7, 0.9, 0.2, 0.8, 0.7, 0.8, 0.9, 0.1, 0.8],  # 0.2 and 0.1 are anomalies
        "budget_utilization": [0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0, 0.2, 0.3]  # 0.2 is anomaly
    }
    
    anomalies = analytics.detect_metric_anomalies(metric_data)
    print(f"\nAnomalies detected: {len(anomalies)} metrics with anomalies")
    
    # Analyze launch patterns
    launch_data = [
        {"budget": 100000, "team_size": 8, "timeline_days": 90, "success_rate": 0.8, "market_size": 1000000, "competition_level": 0.6, "product_complexity": 0.7},
        {"budget": 150000, "team_size": 12, "timeline_days": 120, "success_rate": 0.9, "market_size": 2000000, "competition_level": 0.4, "product_complexity": 0.5},
        {"budget": 80000, "team_size": 6, "timeline_days": 60, "success_rate": 0.6, "market_size": 500000, "competition_level": 0.8, "product_complexity": 0.9},
        {"budget": 200000, "team_size": 15, "timeline_days": 150, "success_rate": 0.95, "market_size": 5000000, "competition_level": 0.3, "product_complexity": 0.4},
        {"budget": 120000, "team_size": 10, "timeline_days": 100, "success_rate": 0.75, "market_size": 1500000, "competition_level": 0.5, "product_complexity": 0.6}
    ]
    
    patterns = analytics.analyze_launch_patterns(launch_data)
    print(f"\nPattern Analysis:")
    print(f"Clusters found: {len(patterns.get('clusters', []))}")
    print(f"Trends analyzed: {len(patterns.get('trends', {}))}")
    
    # Generate comprehensive insights
    insights = analytics.generate_insights("launch_001", metric_data)
    print(f"\nInsights generated:")
    print(f"Forecasts: {len(insights['forecasts'])}")
    print(f"Anomalies: {len(insights['anomalies'])}")
    print(f"Recommendations: {len(insights['recommendations'])}")
    print(f"Risk indicators: {len(insights['risk_indicators'])}")
    
    # Get analytics summary
    summary = analytics.get_analytics_summary()
    print(f"\nAnalytics Summary:")
    print(json.dumps(summary, indent=2))







