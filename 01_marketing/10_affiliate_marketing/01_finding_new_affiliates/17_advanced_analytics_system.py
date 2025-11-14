#!/usr/bin/env python3
"""
Advanced Analytics System for Affiliate Marketing
================================================

This module provides comprehensive analytics capabilities for affiliate marketing,
including real-time monitoring, predictive analytics, and performance optimization.

Author: AI Marketing System
Version: 2.0
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import streamlit as st
from typing import Dict, List, Optional, Tuple
import json
from datetime import datetime, timedelta
import asyncio
import aiohttp
from dataclasses import dataclass, asdict
from enum import Enum
import logging
from sklearn.ensemble import IsolationForest
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA
import warnings
warnings.filterwarnings('ignore')

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class MetricType(Enum):
    """Types of metrics"""
    REVENUE = "revenue"
    CONVERSION = "conversion"
    ENGAGEMENT = "engagement"
    TRAFFIC = "traffic"
    CLICK_THROUGH = "click_through"

@dataclass
class Metric:
    """Metric data structure"""
    name: str
    value: float
    timestamp: datetime
    metric_type: MetricType
    affiliate_id: Optional[str] = None
    campaign_id: Optional[str] = None

@dataclass
class PerformanceAlert:
    """Performance alert data structure"""
    alert_id: str
    metric_name: str
    current_value: float
    threshold_value: float
    severity: str
    timestamp: datetime
    description: str

class AdvancedAnalyticsSystem:
    """
    Advanced Analytics System for Affiliate Marketing
    """
    
    def __init__(self):
        self.metrics = []
        self.alerts = []
        self.dashboards = {}
        self.reports = {}
        self.predictions = {}
        self.anomalies = []
        
    def add_metric(self, metric: Metric):
        """
        Add metric to the system
        """
        self.metrics.append(metric)
        logger.info(f"Added metric: {metric.name} = {metric.value}")
        
        # Check for alerts
        self._check_alerts(metric)
    
    def _check_alerts(self, metric: Metric):
        """
        Check if metric triggers any alerts
        """
        # Define thresholds
        thresholds = {
            'revenue': {'warning': 1000, 'critical': 500},
            'conversion_rate': {'warning': 0.05, 'critical': 0.02},
            'engagement_rate': {'warning': 0.03, 'critical': 0.01},
            'click_through_rate': {'warning': 0.02, 'critical': 0.01}
        }
        
        if metric.name in thresholds:
            threshold = thresholds[metric.name]
            
            if metric.value < threshold['critical']:
                alert = PerformanceAlert(
                    alert_id=f"alert_{len(self.alerts)}",
                    metric_name=metric.name,
                    current_value=metric.value,
                    threshold_value=threshold['critical'],
                    severity='critical',
                    timestamp=datetime.now(),
                    description=f"{metric.name} is critically low: {metric.value}"
                )
                self.alerts.append(alert)
                
            elif metric.value < threshold['warning']:
                alert = PerformanceAlert(
                    alert_id=f"alert_{len(self.alerts)}",
                    metric_name=metric.name,
                    current_value=metric.value,
                    threshold_value=threshold['warning'],
                    severity='warning',
                    timestamp=datetime.now(),
                    description=f"{metric.name} is below warning threshold: {metric.value}"
                )
                self.alerts.append(alert)
    
    def generate_dashboard(self, dashboard_type: str = 'overview') -> Dict:
        """
        Generate interactive dashboard
        """
        if dashboard_type == 'overview':
            return self._generate_overview_dashboard()
        elif dashboard_type == 'affiliate':
            return self._generate_affiliate_dashboard()
        elif dashboard_type == 'campaign':
            return self._generate_campaign_dashboard()
        elif dashboard_type == 'revenue':
            return self._generate_revenue_dashboard()
        else:
            return self._generate_custom_dashboard(dashboard_type)
    
    def _generate_overview_dashboard(self) -> Dict:
        """
        Generate overview dashboard
        """
        # Calculate key metrics
        total_revenue = sum([m.value for m in self.metrics if m.metric_type == MetricType.REVENUE])
        total_conversions = sum([m.value for m in self.metrics if m.metric_type == MetricType.CONVERSION])
        avg_engagement = np.mean([m.value for m in self.metrics if m.metric_type == MetricType.ENGAGEMENT])
        
        # Create charts
        revenue_chart = self._create_revenue_chart()
        conversion_chart = self._create_conversion_chart()
        engagement_chart = self._create_engagement_chart()
        
        return {
            'title': 'Affiliate Marketing Overview',
            'metrics': {
                'total_revenue': total_revenue,
                'total_conversions': total_conversions,
                'avg_engagement': avg_engagement,
                'active_affiliates': len(set([m.affiliate_id for m in self.metrics if m.affiliate_id])),
                'active_campaigns': len(set([m.campaign_id for m in self.metrics if m.campaign_id]))
            },
            'charts': {
                'revenue': revenue_chart,
                'conversion': conversion_chart,
                'engagement': engagement_chart
            },
            'alerts': self.alerts[-10:]  # Last 10 alerts
        }
    
    def _create_revenue_chart(self) -> Dict:
        """
        Create revenue chart
        """
        revenue_data = [m for m in self.metrics if m.metric_type == MetricType.REVENUE]
        
        if not revenue_data:
            return {'type': 'line', 'data': [], 'title': 'Revenue Over Time'}
        
        # Group by date
        df = pd.DataFrame([{
            'date': m.timestamp.date(),
            'value': m.value
        } for m in revenue_data])
        
        daily_revenue = df.groupby('date')['value'].sum().reset_index()
        
        return {
            'type': 'line',
            'data': daily_revenue.to_dict('records'),
            'title': 'Revenue Over Time',
            'x_axis': 'date',
            'y_axis': 'value'
        }
    
    def _create_conversion_chart(self) -> Dict:
        """
        Create conversion chart
        """
        conversion_data = [m for m in self.metrics if m.metric_type == MetricType.CONVERSION]
        
        if not conversion_data:
            return {'type': 'bar', 'data': [], 'title': 'Conversion Rates'}
        
        # Group by affiliate
        df = pd.DataFrame([{
            'affiliate_id': m.affiliate_id,
            'value': m.value
        } for m in conversion_data if m.affiliate_id])
        
        affiliate_conversions = df.groupby('affiliate_id')['value'].mean().reset_index()
        
        return {
            'type': 'bar',
            'data': affiliate_conversions.to_dict('records'),
            'title': 'Conversion Rates by Affiliate',
            'x_axis': 'affiliate_id',
            'y_axis': 'value'
        }
    
    def _create_engagement_chart(self) -> Dict:
        """
        Create engagement chart
        """
        engagement_data = [m for m in self.metrics if m.metric_type == MetricType.ENGAGEMENT]
        
        if not engagement_data:
            return {'type': 'scatter', 'data': [], 'title': 'Engagement Rates'}
        
        # Create scatter plot data
        df = pd.DataFrame([{
            'timestamp': m.timestamp,
            'value': m.value,
            'affiliate_id': m.affiliate_id
        } for m in engagement_data])
        
        return {
            'type': 'scatter',
            'data': df.to_dict('records'),
            'title': 'Engagement Rates Over Time',
            'x_axis': 'timestamp',
            'y_axis': 'value',
            'color': 'affiliate_id'
        }
    
    def _generate_affiliate_dashboard(self) -> Dict:
        """
        Generate affiliate-specific dashboard
        """
        # Group metrics by affiliate
        affiliate_metrics = {}
        for metric in self.metrics:
            if metric.affiliate_id:
                if metric.affiliate_id not in affiliate_metrics:
                    affiliate_metrics[metric.affiliate_id] = []
                affiliate_metrics[metric.affiliate_id].append(metric)
        
        # Calculate affiliate performance
        affiliate_performance = {}
        for affiliate_id, metrics in affiliate_metrics.items():
            revenue = sum([m.value for m in metrics if m.metric_type == MetricType.REVENUE])
            conversions = sum([m.value for m in metrics if m.metric_type == MetricType.CONVERSION])
            engagement = np.mean([m.value for m in metrics if m.metric_type == MetricType.ENGAGEMENT])
            
            affiliate_performance[affiliate_id] = {
                'revenue': revenue,
                'conversions': conversions,
                'engagement': engagement,
                'performance_score': self._calculate_performance_score(metrics)
            }
        
        return {
            'title': 'Affiliate Performance Dashboard',
            'affiliate_performance': affiliate_performance,
            'top_performers': self._get_top_performers(affiliate_performance),
            'underperformers': self._get_underperformers(affiliate_performance)
        }
    
    def _calculate_performance_score(self, metrics: List[Metric]) -> float:
        """
        Calculate performance score for affiliate
        """
        if not metrics:
            return 0.0
        
        # Weight different metric types
        weights = {
            MetricType.REVENUE: 0.4,
            MetricType.CONVERSION: 0.3,
            MetricType.ENGAGEMENT: 0.2,
            MetricType.TRAFFIC: 0.1
        }
        
        score = 0.0
        for metric in metrics:
            weight = weights.get(metric.metric_type, 0.1)
            score += metric.value * weight
        
        return score
    
    def _get_top_performers(self, performance: Dict) -> List[Dict]:
        """
        Get top performing affiliates
        """
        sorted_affiliates = sorted(
            performance.items(),
            key=lambda x: x[1]['performance_score'],
            reverse=True
        )
        
        return [
            {
                'affiliate_id': affiliate_id,
                'performance_score': data['performance_score'],
                'revenue': data['revenue'],
                'conversions': data['conversions']
            }
            for affiliate_id, data in sorted_affiliates[:5]
        ]
    
    def _get_underperformers(self, performance: Dict) -> List[Dict]:
        """
        Get underperforming affiliates
        """
        sorted_affiliates = sorted(
            performance.items(),
            key=lambda x: x[1]['performance_score']
        )
        
        return [
            {
                'affiliate_id': affiliate_id,
                'performance_score': data['performance_score'],
                'revenue': data['revenue'],
                'conversions': data['conversions']
            }
            for affiliate_id, data in sorted_affiliates[:5]
        ]
    
    def detect_anomalies(self) -> List[Dict]:
        """
        Detect anomalies in metrics
        """
        if len(self.metrics) < 10:
            return []
        
        # Prepare data for anomaly detection
        df = pd.DataFrame([{
            'value': m.value,
            'timestamp': m.timestamp,
            'metric_type': m.metric_type.value
        } for m in self.metrics])
        
        # Group by metric type
        anomalies = []
        for metric_type in df['metric_type'].unique():
            type_data = df[df['metric_type'] == metric_type]['value'].values
            
            if len(type_data) > 5:
                # Use Isolation Forest for anomaly detection
                iso_forest = IsolationForest(contamination=0.1, random_state=42)
                anomaly_labels = iso_forest.fit_predict(type_data.reshape(-1, 1))
                
                # Get anomalous values
                anomalous_indices = np.where(anomaly_labels == -1)[0]
                
                for idx in anomalous_indices:
                    anomalies.append({
                        'metric_type': metric_type,
                        'value': type_data[idx],
                        'timestamp': df[df['metric_type'] == metric_type].iloc[idx]['timestamp'],
                        'severity': 'high' if type_data[idx] > np.mean(type_data) else 'low'
                    })
        
        self.anomalies = anomalies
        return anomalies
    
    def generate_predictions(self, days_ahead: int = 30) -> Dict:
        """
        Generate predictions for future performance
        """
        predictions = {}
        
        # Group metrics by type
        metric_types = {}
        for metric in self.metrics:
            metric_type = metric.metric_type.value
            if metric_type not in metric_types:
                metric_types[metric_type] = []
            metric_types[metric_type].append(metric)
        
        # Generate predictions for each metric type
        for metric_type, metrics in metric_types.items():
            if len(metrics) < 5:
                continue
            
            # Create time series data
            df = pd.DataFrame([{
                'timestamp': m.timestamp,
                'value': m.value
            } for m in metrics])
            
            df = df.sort_values('timestamp')
            df['date'] = pd.to_datetime(df['timestamp']).dt.date
            
            # Group by date and sum values
            daily_data = df.groupby('date')['value'].sum().reset_index()
            
            if len(daily_data) < 3:
                continue
            
            # Simple linear regression for prediction
            x = np.arange(len(daily_data))
            y = daily_data['value'].values
            
            # Fit linear regression
            coeffs = np.polyfit(x, y, 1)
            
            # Predict future values
            future_x = np.arange(len(daily_data), len(daily_data) + days_ahead)
            future_y = coeffs[0] * future_x + coeffs[1]
            
            # Create prediction dates
            last_date = daily_data['date'].iloc[-1]
            future_dates = [last_date + timedelta(days=i+1) for i in range(days_ahead)]
            
            predictions[metric_type] = {
                'dates': [d.isoformat() for d in future_dates],
                'values': future_y.tolist(),
                'trend': 'increasing' if coeffs[0] > 0 else 'decreasing',
                'confidence': self._calculate_prediction_confidence(y, coeffs)
            }
        
        self.predictions = predictions
        return predictions
    
    def _calculate_prediction_confidence(self, actual_values: np.ndarray, coeffs: np.ndarray) -> float:
        """
        Calculate prediction confidence
        """
        # Calculate R-squared
        predicted_values = coeffs[0] * np.arange(len(actual_values)) + coeffs[1]
        ss_res = np.sum((actual_values - predicted_values) ** 2)
        ss_tot = np.sum((actual_values - np.mean(actual_values)) ** 2)
        
        r_squared = 1 - (ss_res / ss_tot) if ss_tot != 0 else 0
        return max(0, min(1, r_squared))
    
    def generate_report(self, report_type: str = 'comprehensive') -> Dict:
        """
        Generate comprehensive analytics report
        """
        if report_type == 'comprehensive':
            return self._generate_comprehensive_report()
        elif report_type == 'performance':
            return self._generate_performance_report()
        elif report_type == 'anomaly':
            return self._generate_anomaly_report()
        else:
            return self._generate_custom_report(report_type)
    
    def _generate_comprehensive_report(self) -> Dict:
        """
        Generate comprehensive analytics report
        """
        # Calculate key metrics
        total_metrics = len(self.metrics)
        total_revenue = sum([m.value for m in self.metrics if m.metric_type == MetricType.REVENUE])
        total_conversions = sum([m.value for m in self.metrics if m.metric_type == MetricType.CONVERSION])
        avg_engagement = np.mean([m.value for m in self.metrics if m.metric_type == MetricType.ENGAGEMENT])
        
        # Get time range
        if self.metrics:
            start_date = min([m.timestamp for m in self.metrics])
            end_date = max([m.timestamp for m in self.metrics])
        else:
            start_date = end_date = datetime.now()
        
        # Detect anomalies
        anomalies = self.detect_anomalies()
        
        # Generate predictions
        predictions = self.generate_predictions()
        
        return {
            'report_type': 'comprehensive',
            'generated_at': datetime.now().isoformat(),
            'time_range': {
                'start': start_date.isoformat(),
                'end': end_date.isoformat()
            },
            'summary': {
                'total_metrics': total_metrics,
                'total_revenue': total_revenue,
                'total_conversions': total_conversions,
                'avg_engagement': avg_engagement,
                'total_alerts': len(self.alerts),
                'total_anomalies': len(anomalies)
            },
            'performance': self._generate_affiliate_dashboard(),
            'anomalies': anomalies,
            'predictions': predictions,
            'recommendations': self._generate_recommendations()
        }
    
    def _generate_recommendations(self) -> List[str]:
        """
        Generate AI-powered recommendations
        """
        recommendations = []
        
        # Analyze performance
        if self.metrics:
            revenue_metrics = [m for m in self.metrics if m.metric_type == MetricType.REVENUE]
            if revenue_metrics:
                recent_revenue = np.mean([m.value for m in revenue_metrics[-10:]])
                if recent_revenue < 1000:
                    recommendations.append("Focus on increasing revenue through better affiliate selection")
            
            engagement_metrics = [m for m in self.metrics if m.metric_type == MetricType.ENGAGEMENT]
            if engagement_metrics:
                avg_engagement = np.mean([m.value for m in engagement_metrics])
                if avg_engagement < 0.03:
                    recommendations.append("Improve engagement rates through better content strategy")
        
        # Analyze anomalies
        if self.anomalies:
            high_severity_anomalies = [a for a in self.anomalies if a['severity'] == 'high']
            if high_severity_anomalies:
                recommendations.append("Investigate high-severity anomalies in performance metrics")
        
        return recommendations
    
    def export_data(self, format: str = 'json') -> str:
        """
        Export analytics data
        """
        if format == 'json':
            data = {
                'metrics': [asdict(m) for m in self.metrics],
                'alerts': [asdict(a) for a in self.alerts],
                'anomalies': self.anomalies,
                'predictions': self.predictions
            }
            return json.dumps(data, indent=2, default=str)
        elif format == 'csv':
            # Convert metrics to CSV
            df = pd.DataFrame([asdict(m) for m in self.metrics])
            return df.to_csv(index=False)
        else:
            raise ValueError(f"Unsupported format: {format}")

# Example usage
def main():
    """
    Example usage of Advanced Analytics System
    """
    # Initialize analytics system
    analytics = AdvancedAnalyticsSystem()
    
    # Add sample metrics
    sample_metrics = [
        Metric('revenue', 1500.0, datetime.now(), MetricType.REVENUE, 'affiliate_1', 'campaign_1'),
        Metric('conversion_rate', 0.05, datetime.now(), MetricType.CONVERSION, 'affiliate_1', 'campaign_1'),
        Metric('engagement_rate', 0.04, datetime.now(), MetricType.ENGAGEMENT, 'affiliate_1', 'campaign_1'),
        Metric('revenue', 2000.0, datetime.now(), MetricType.REVENUE, 'affiliate_2', 'campaign_2'),
        Metric('conversion_rate', 0.03, datetime.now(), MetricType.CONVERSION, 'affiliate_2', 'campaign_2'),
        Metric('engagement_rate', 0.02, datetime.now(), MetricType.ENGAGEMENT, 'affiliate_2', 'campaign_2')
    ]
    
    for metric in sample_metrics:
        analytics.add_metric(metric)
    
    # Generate dashboard
    dashboard = analytics.generate_dashboard('overview')
    print(f"Dashboard: {dashboard}")
    
    # Detect anomalies
    anomalies = analytics.detect_anomalies()
    print(f"Anomalies detected: {len(anomalies)}")
    
    # Generate predictions
    predictions = analytics.generate_predictions()
    print(f"Predictions: {predictions}")
    
    # Generate report
    report = analytics.generate_report()
    print(f"Report generated: {report['summary']}")
    
    # Export data
    json_data = analytics.export_data('json')
    print(f"Exported {len(json_data)} characters of data")

if __name__ == "__main__":
    main()






