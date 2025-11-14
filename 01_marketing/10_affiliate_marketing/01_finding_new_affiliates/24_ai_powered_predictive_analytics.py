#!/usr/bin/env python3
"""
AI-Powered Predictive Analytics for Affiliate Marketing
======================================================

This module provides advanced predictive analytics capabilities for affiliate marketing,
including revenue forecasting, trend analysis, and performance prediction.

Author: AI Marketing System
Version: 2.0
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from typing import Dict, List, Optional, Tuple, Any
from datetime import datetime, timedelta
import asyncio
import aiohttp
from dataclasses import dataclass, asdict
from enum import Enum
import logging
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.linear_model import LinearRegression, Ridge, Lasso
from sklearn.preprocessing import StandardScaler, PolynomialFeatures
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.metrics import mean_squared_error, r2_score, mean_absolute_error
from sklearn.neural_network import MLPRegressor
import xgboost as xgb
import lightgbm as lgb
from scipy import stats
import warnings
warnings.filterwarnings('ignore')

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class PredictionType(Enum):
    """Types of predictions"""
    REVENUE = "revenue"
    CONVERSION = "conversion"
    CLICK_THROUGH = "click_through"
    ENGAGEMENT = "engagement"
    CHURN = "churn"
    LIFETIME_VALUE = "lifetime_value"

class TimeHorizon(Enum):
    """Prediction time horizons"""
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"
    QUARTERLY = "quarterly"
    YEARLY = "yearly"

@dataclass
class PredictionResult:
    """Prediction result data structure"""
    prediction_id: str
    prediction_type: PredictionType
    time_horizon: TimeHorizon
    predicted_value: float
    confidence_interval: Tuple[float, float]
    confidence_level: float
    model_used: str
    accuracy_score: float
    created_at: datetime
    target_date: datetime

@dataclass
class TrendAnalysis:
    """Trend analysis data structure"""
    trend_id: str
    metric_name: str
    trend_direction: str  # increasing, decreasing, stable
    trend_strength: float  # 0-1
    trend_duration: int  # days
    seasonal_pattern: bool
    anomaly_detected: bool
    confidence_score: float
    created_at: datetime

@dataclass
class PerformanceForecast:
    """Performance forecast data structure"""
    forecast_id: str
    affiliate_id: str
    metric_type: PredictionType
    current_value: float
    predicted_value: float
    growth_rate: float
    confidence_score: float
    risk_factors: List[str]
    recommendations: List[str]
    created_at: datetime
    forecast_period: str

class AIPoweredPredictiveAnalytics:
    """
    AI-Powered Predictive Analytics for Affiliate Marketing
    """
    
    def __init__(self):
        self.historical_data = []
        self.prediction_models = {}
        self.trend_analyses = []
        self.performance_forecasts = []
        self.prediction_results = []
        
        # Initialize prediction parameters
        self.prediction_params = {
            'min_data_points': 30,
            'max_prediction_horizon': 365,  # days
            'confidence_level': 0.95,
            'seasonality_detection': True,
            'anomaly_detection': True
        }
        
        # Initialize models
        self._initialize_prediction_models()
    
    def _initialize_prediction_models(self):
        """
        Initialize prediction models
        """
        self.prediction_models = {
            'revenue': {
                'linear': LinearRegression(),
                'ridge': Ridge(alpha=1.0),
                'lasso': Lasso(alpha=1.0),
                'random_forest': RandomForestRegressor(n_estimators=100, random_state=42),
                'gradient_boosting': GradientBoostingRegressor(n_estimators=100, random_state=42),
                'xgboost': xgb.XGBRegressor(n_estimators=100, random_state=42),
                'lightgbm': lgb.LGBMRegressor(n_estimators=100, random_state=42),
                'neural_network': MLPRegressor(hidden_layer_sizes=(100, 50), random_state=42)
            },
            'conversion': {
                'linear': LinearRegression(),
                'random_forest': RandomForestRegressor(n_estimators=100, random_state=42),
                'gradient_boosting': GradientBoostingRegressor(n_estimators=100, random_state=42),
                'xgboost': xgb.XGBRegressor(n_estimators=100, random_state=42)
            },
            'engagement': {
                'linear': LinearRegression(),
                'random_forest': RandomForestRegressor(n_estimators=100, random_state=42),
                'neural_network': MLPRegressor(hidden_layer_sizes=(50, 25), random_state=42)
            }
        }
    
    def add_historical_data(self, data: Dict[str, Any]):
        """
        Add historical data for analysis
        """
        self.historical_data.append({
            **data,
            'timestamp': datetime.now()
        })
        
        logger.info(f"Added historical data: {len(self.historical_data)} records")
    
    def predict_revenue(self, time_horizon: TimeHorizon, 
                       days_ahead: int = 30) -> PredictionResult:
        """
        Predict revenue for specified time horizon
        """
        if len(self.historical_data) < self.prediction_params['min_data_points']:
            logger.warning("Insufficient data for prediction")
            return None
        
        # Prepare data
        df = self._prepare_revenue_data()
        
        # Train models
        best_model, accuracy = self._train_revenue_models(df)
        
        # Make prediction
        predicted_value = self._make_revenue_prediction(best_model, df, days_ahead)
        
        # Calculate confidence interval
        confidence_interval = self._calculate_confidence_interval(
            predicted_value, df, best_model
        )
        
        # Create prediction result
        result = PredictionResult(
            prediction_id=f"pred_{len(self.prediction_results)}",
            prediction_type=PredictionType.REVENUE,
            time_horizon=time_horizon,
            predicted_value=predicted_value,
            confidence_interval=confidence_interval,
            confidence_level=self.prediction_params['confidence_level'],
            model_used=best_model,
            accuracy_score=accuracy,
            created_at=datetime.now(),
            target_date=datetime.now() + timedelta(days=days_ahead)
        )
        
        self.prediction_results.append(result)
        return result
    
    def _prepare_revenue_data(self) -> pd.DataFrame:
        """
        Prepare revenue data for analysis
        """
        # Convert to DataFrame
        df = pd.DataFrame(self.historical_data)
        
        # Extract revenue data
        revenue_data = []
        for _, row in df.iterrows():
            if 'revenue' in row:
                revenue_data.append({
                    'date': row['timestamp'],
                    'revenue': row['revenue'],
                    'clicks': row.get('clicks', 0),
                    'conversions': row.get('conversions', 0),
                    'affiliates': row.get('affiliates', 0)
                })
        
        revenue_df = pd.DataFrame(revenue_data)
        
        # Sort by date
        revenue_df = revenue_df.sort_values('date')
        
        # Add time features
        revenue_df['day_of_week'] = revenue_df['date'].dt.dayofweek
        revenue_df['month'] = revenue_df['date'].dt.month
        revenue_df['quarter'] = revenue_df['date'].dt.quarter
        revenue_df['year'] = revenue_df['date'].dt.year
        
        # Add lag features
        revenue_df['revenue_lag_1'] = revenue_df['revenue'].shift(1)
        revenue_df['revenue_lag_7'] = revenue_df['revenue'].shift(7)
        revenue_df['revenue_lag_30'] = revenue_df['revenue'].shift(30)
        
        # Add rolling averages
        revenue_df['revenue_ma_7'] = revenue_df['revenue'].rolling(window=7).mean()
        revenue_df['revenue_ma_30'] = revenue_df['revenue'].rolling(window=30).mean()
        
        # Add trend features
        revenue_df['revenue_trend'] = revenue_df['revenue'].diff()
        revenue_df['revenue_trend_ma'] = revenue_df['revenue_trend'].rolling(window=7).mean()
        
        # Remove NaN values
        revenue_df = revenue_df.dropna()
        
        return revenue_df
    
    def _train_revenue_models(self, df: pd.DataFrame) -> Tuple[str, float]:
        """
        Train revenue prediction models
        """
        # Prepare features and target
        feature_columns = ['day_of_week', 'month', 'quarter', 'year', 
                          'clicks', 'conversions', 'affiliates',
                          'revenue_lag_1', 'revenue_lag_7', 'revenue_lag_30',
                          'revenue_ma_7', 'revenue_ma_30', 'revenue_trend', 'revenue_trend_ma']
        
        X = df[feature_columns]
        y = df['revenue']
        
        # Split data
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
        
        # Scale features
        scaler = StandardScaler()
        X_train_scaled = scaler.fit_transform(X_train)
        X_test_scaled = scaler.transform(X_test)
        
        # Train models
        models = self.prediction_models['revenue']
        best_model_name = None
        best_accuracy = -np.inf
        
        for model_name, model in models.items():
            try:
                # Train model
                if model_name in ['neural_network']:
                    model.fit(X_train_scaled, y_train)
                    y_pred = model.predict(X_test_scaled)
                else:
                    model.fit(X_train, y_train)
                    y_pred = model.predict(X_test)
                
                # Calculate accuracy
                accuracy = r2_score(y_test, y_pred)
                
                if accuracy > best_accuracy:
                    best_accuracy = accuracy
                    best_model_name = model_name
                
                # Store scaler for best model
                if model_name == best_model_name:
                    model.scaler = scaler
                    model.feature_columns = feature_columns
                
            except Exception as e:
                logger.error(f"Error training {model_name}: {str(e)}")
                continue
        
        return best_model_name, best_accuracy
    
    def _make_revenue_prediction(self, model_name: str, df: pd.DataFrame, 
                                days_ahead: int) -> float:
        """
        Make revenue prediction
        """
        model = self.prediction_models['revenue'][model_name]
        
        # Get latest data point
        latest_data = df.iloc[-1]
        
        # Create prediction features
        prediction_date = latest_data['date'] + timedelta(days=days_ahead)
        
        features = {
            'day_of_week': prediction_date.dayofweek,
            'month': prediction_date.month,
            'quarter': prediction_date.quarter,
            'year': prediction_date.year,
            'clicks': latest_data['clicks'],
            'conversions': latest_data['conversions'],
            'affiliates': latest_data['affiliates'],
            'revenue_lag_1': latest_data['revenue'],
            'revenue_lag_7': latest_data['revenue_lag_7'],
            'revenue_lag_30': latest_data['revenue_lag_30'],
            'revenue_ma_7': latest_data['revenue_ma_7'],
            'revenue_ma_30': latest_data['revenue_ma_30'],
            'revenue_trend': latest_data['revenue_trend'],
            'revenue_trend_ma': latest_data['revenue_trend_ma']
        }
        
        # Convert to array
        feature_array = np.array([list(features.values())])
        
        # Scale features if needed
        if hasattr(model, 'scaler'):
            feature_array = model.scaler.transform(feature_array)
        
        # Make prediction
        prediction = model.predict(feature_array)[0]
        
        return max(0, prediction)  # Ensure non-negative prediction
    
    def _calculate_confidence_interval(self, prediction: float, df: pd.DataFrame, 
                                     model_name: str) -> Tuple[float, float]:
        """
        Calculate confidence interval for prediction
        """
        # Calculate prediction error
        errors = []
        for i in range(len(df) - 7, len(df)):  # Use last 7 days for error calculation
            if i < 0:
                continue
            
            # Get features for this day
            features = df.iloc[i][model.feature_columns].values.reshape(1, -1)
            
            # Scale features if needed
            if hasattr(model, 'scaler'):
                features = model.scaler.transform(features)
            
            # Make prediction
            pred = model.predict(features)[0]
            actual = df.iloc[i]['revenue']
            error = abs(pred - actual)
            errors.append(error)
        
        # Calculate standard error
        if errors:
            std_error = np.std(errors)
        else:
            std_error = prediction * 0.1  # Default 10% error
        
        # Calculate confidence interval
        z_score = stats.norm.ppf(1 - (1 - self.prediction_params['confidence_level']) / 2)
        margin_error = z_score * std_error
        
        return (prediction - margin_error, prediction + margin_error)
    
    def predict_conversion_rate(self, time_horizon: TimeHorizon, 
                               days_ahead: int = 30) -> PredictionResult:
        """
        Predict conversion rate for specified time horizon
        """
        if len(self.historical_data) < self.prediction_params['min_data_points']:
            logger.warning("Insufficient data for prediction")
            return None
        
        # Prepare data
        df = self._prepare_conversion_data()
        
        # Train models
        best_model, accuracy = self._train_conversion_models(df)
        
        # Make prediction
        predicted_value = self._make_conversion_prediction(best_model, df, days_ahead)
        
        # Calculate confidence interval
        confidence_interval = self._calculate_confidence_interval(
            predicted_value, df, best_model
        )
        
        # Create prediction result
        result = PredictionResult(
            prediction_id=f"pred_{len(self.prediction_results)}",
            prediction_type=PredictionType.CONVERSION,
            time_horizon=time_horizon,
            predicted_value=predicted_value,
            confidence_interval=confidence_interval,
            confidence_level=self.prediction_params['confidence_level'],
            model_used=best_model,
            accuracy_score=accuracy,
            created_at=datetime.now(),
            target_date=datetime.now() + timedelta(days=days_ahead)
        )
        
        self.prediction_results.append(result)
        return result
    
    def _prepare_conversion_data(self) -> pd.DataFrame:
        """
        Prepare conversion data for analysis
        """
        # Convert to DataFrame
        df = pd.DataFrame(self.historical_data)
        
        # Extract conversion data
        conversion_data = []
        for _, row in df.iterrows():
            if 'conversions' in row and 'clicks' in row:
                conversion_rate = row['conversions'] / row['clicks'] if row['clicks'] > 0 else 0
                conversion_data.append({
                    'date': row['timestamp'],
                    'conversion_rate': conversion_rate,
                    'clicks': row['clicks'],
                    'conversions': row['conversions'],
                    'revenue': row.get('revenue', 0),
                    'affiliates': row.get('affiliates', 0)
                })
        
        conversion_df = pd.DataFrame(conversion_data)
        
        # Sort by date
        conversion_df = conversion_df.sort_values('date')
        
        # Add time features
        conversion_df['day_of_week'] = conversion_df['date'].dt.dayofweek
        conversion_df['month'] = conversion_df['date'].dt.month
        conversion_df['quarter'] = conversion_df['date'].dt.quarter
        
        # Add lag features
        conversion_df['conversion_rate_lag_1'] = conversion_df['conversion_rate'].shift(1)
        conversion_df['conversion_rate_lag_7'] = conversion_df['conversion_rate'].shift(7)
        
        # Add rolling averages
        conversion_df['conversion_rate_ma_7'] = conversion_df['conversion_rate'].rolling(window=7).mean()
        conversion_df['conversion_rate_ma_30'] = conversion_df['conversion_rate'].rolling(window=30).mean()
        
        # Remove NaN values
        conversion_df = conversion_df.dropna()
        
        return conversion_df
    
    def _train_conversion_models(self, df: pd.DataFrame) -> Tuple[str, float]:
        """
        Train conversion prediction models
        """
        # Prepare features and target
        feature_columns = ['day_of_week', 'month', 'quarter', 'clicks', 'conversions', 
                          'revenue', 'affiliates', 'conversion_rate_lag_1', 'conversion_rate_lag_7',
                          'conversion_rate_ma_7', 'conversion_rate_ma_30']
        
        X = df[feature_columns]
        y = df['conversion_rate']
        
        # Split data
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
        
        # Scale features
        scaler = StandardScaler()
        X_train_scaled = scaler.fit_transform(X_train)
        X_test_scaled = scaler.transform(X_test)
        
        # Train models
        models = self.prediction_models['conversion']
        best_model_name = None
        best_accuracy = -np.inf
        
        for model_name, model in models.items():
            try:
                # Train model
                model.fit(X_train, y_train)
                y_pred = model.predict(X_test)
                
                # Calculate accuracy
                accuracy = r2_score(y_test, y_pred)
                
                if accuracy > best_accuracy:
                    best_accuracy = accuracy
                    best_model_name = model_name
                
                # Store scaler for best model
                if model_name == best_model_name:
                    model.scaler = scaler
                    model.feature_columns = feature_columns
                
            except Exception as e:
                logger.error(f"Error training {model_name}: {str(e)}")
                continue
        
        return best_model_name, best_accuracy
    
    def _make_conversion_prediction(self, model_name: str, df: pd.DataFrame, 
                                   days_ahead: int) -> float:
        """
        Make conversion rate prediction
        """
        model = self.prediction_models['conversion'][model_name]
        
        # Get latest data point
        latest_data = df.iloc[-1]
        
        # Create prediction features
        prediction_date = latest_data['date'] + timedelta(days=days_ahead)
        
        features = {
            'day_of_week': prediction_date.dayofweek,
            'month': prediction_date.month,
            'quarter': prediction_date.quarter,
            'clicks': latest_data['clicks'],
            'conversions': latest_data['conversions'],
            'revenue': latest_data['revenue'],
            'affiliates': latest_data['affiliates'],
            'conversion_rate_lag_1': latest_data['conversion_rate'],
            'conversion_rate_lag_7': latest_data['conversion_rate_lag_7'],
            'conversion_rate_ma_7': latest_data['conversion_rate_ma_7'],
            'conversion_rate_ma_30': latest_data['conversion_rate_ma_30']
        }
        
        # Convert to array
        feature_array = np.array([list(features.values())])
        
        # Make prediction
        prediction = model.predict(feature_array)[0]
        
        return max(0, min(1, prediction))  # Ensure prediction is between 0 and 1
    
    def analyze_trends(self, metric_name: str, window_size: int = 30) -> TrendAnalysis:
        """
        Analyze trends for specified metric
        """
        if len(self.historical_data) < window_size:
            logger.warning("Insufficient data for trend analysis")
            return None
        
        # Prepare data
        df = pd.DataFrame(self.historical_data)
        df = df.sort_values('timestamp')
        
        # Get metric values
        if metric_name not in df.columns:
            logger.error(f"Metric {metric_name} not found in data")
            return None
        
        values = df[metric_name].values[-window_size:]
        dates = df['timestamp'].values[-window_size:]
        
        # Calculate trend direction
        trend_direction = self._calculate_trend_direction(values)
        
        # Calculate trend strength
        trend_strength = self._calculate_trend_strength(values)
        
        # Detect seasonal patterns
        seasonal_pattern = self._detect_seasonal_pattern(values)
        
        # Detect anomalies
        anomaly_detected = self._detect_anomalies(values)
        
        # Calculate confidence score
        confidence_score = self._calculate_trend_confidence(values, trend_direction)
        
        # Create trend analysis
        trend_analysis = TrendAnalysis(
            trend_id=f"trend_{len(self.trend_analyses)}",
            metric_name=metric_name,
            trend_direction=trend_direction,
            trend_strength=trend_strength,
            trend_duration=window_size,
            seasonal_pattern=seasonal_pattern,
            anomaly_detected=anomaly_detected,
            confidence_score=confidence_score,
            created_at=datetime.now()
        )
        
        self.trend_analyses.append(trend_analysis)
        return trend_analysis
    
    def _calculate_trend_direction(self, values: np.ndarray) -> str:
        """
        Calculate trend direction
        """
        if len(values) < 2:
            return 'stable'
        
        # Calculate slope
        x = np.arange(len(values))
        slope, _, _, _, _ = stats.linregress(x, values)
        
        if slope > 0.01:
            return 'increasing'
        elif slope < -0.01:
            return 'decreasing'
        else:
            return 'stable'
    
    def _calculate_trend_strength(self, values: np.ndarray) -> float:
        """
        Calculate trend strength
        """
        if len(values) < 2:
            return 0.0
        
        # Calculate R-squared
        x = np.arange(len(values))
        slope, intercept, r_value, _, _ = stats.linregress(x, values)
        
        return r_value ** 2
    
    def _detect_seasonal_pattern(self, values: np.ndarray) -> bool:
        """
        Detect seasonal patterns
        """
        if len(values) < 14:  # Need at least 2 weeks
            return False
        
        # Simple seasonal detection using autocorrelation
        # In practice, use more sophisticated methods like FFT
        autocorr = np.corrcoef(values[:-7], values[7:])[0, 1]
        
        return autocorr > 0.5
    
    def _detect_anomalies(self, values: np.ndarray) -> bool:
        """
        Detect anomalies in data
        """
        if len(values) < 10:
            return False
        
        # Use Z-score for anomaly detection
        z_scores = np.abs(stats.zscore(values))
        
        return np.any(z_scores > 2.5)
    
    def _calculate_trend_confidence(self, values: np.ndarray, trend_direction: str) -> float:
        """
        Calculate trend confidence score
        """
        if len(values) < 2:
            return 0.0
        
        # Calculate R-squared
        x = np.arange(len(values))
        slope, intercept, r_value, _, _ = stats.linregress(x, values)
        
        # Adjust confidence based on trend direction
        if trend_direction == 'stable':
            confidence = 1 - abs(r_value)
        else:
            confidence = r_value ** 2
        
        return max(0.0, min(1.0, confidence))
    
    def forecast_affiliate_performance(self, affiliate_id: str, 
                                     metric_type: PredictionType, 
                                     days_ahead: int = 30) -> PerformanceForecast:
        """
        Forecast performance for specific affiliate
        """
        # Get affiliate data
        affiliate_data = [d for d in self.historical_data if d.get('affiliate_id') == affiliate_id]
        
        if len(affiliate_data) < 10:
            logger.warning(f"Insufficient data for affiliate {affiliate_id}")
            return None
        
        # Prepare data
        df = pd.DataFrame(affiliate_data)
        df = df.sort_values('timestamp')
        
        # Get current value
        current_value = df.iloc[-1].get(metric_type.value, 0)
        
        # Calculate growth rate
        if len(df) > 1:
            previous_value = df.iloc[-2].get(metric_type.value, 0)
            growth_rate = (current_value - previous_value) / previous_value if previous_value > 0 else 0
        else:
            growth_rate = 0
        
        # Make prediction
        predicted_value = self._predict_affiliate_metric(df, metric_type, days_ahead)
        
        # Calculate confidence score
        confidence_score = self._calculate_affiliate_confidence(df, metric_type)
        
        # Identify risk factors
        risk_factors = self._identify_risk_factors(df, metric_type)
        
        # Generate recommendations
        recommendations = self._generate_affiliate_recommendations(
            df, metric_type, predicted_value, risk_factors
        )
        
        # Create performance forecast
        forecast = PerformanceForecast(
            forecast_id=f"forecast_{len(self.performance_forecasts)}",
            affiliate_id=affiliate_id,
            metric_type=metric_type,
            current_value=current_value,
            predicted_value=predicted_value,
            growth_rate=growth_rate,
            confidence_score=confidence_score,
            risk_factors=risk_factors,
            recommendations=recommendations,
            created_at=datetime.now(),
            forecast_period=f"{days_ahead} days"
        )
        
        self.performance_forecasts.append(forecast)
        return forecast
    
    def _predict_affiliate_metric(self, df: pd.DataFrame, metric_type: PredictionType, 
                                 days_ahead: int) -> float:
        """
        Predict metric for affiliate
        """
        # Simple linear trend prediction
        values = df[metric_type.value].values
        x = np.arange(len(values))
        
        # Fit linear regression
        slope, intercept, _, _, _ = stats.linregress(x, values)
        
        # Predict future value
        future_x = len(values) + days_ahead
        predicted_value = slope * future_x + intercept
        
        return max(0, predicted_value)
    
    def _calculate_affiliate_confidence(self, df: pd.DataFrame, metric_type: PredictionType) -> float:
        """
        Calculate confidence score for affiliate prediction
        """
        values = df[metric_type.value].values
        
        if len(values) < 2:
            return 0.0
        
        # Calculate R-squared
        x = np.arange(len(values))
        slope, intercept, r_value, _, _ = stats.linregress(x, values)
        
        return r_value ** 2
    
    def _identify_risk_factors(self, df: pd.DataFrame, metric_type: PredictionType) -> List[str]:
        """
        Identify risk factors for affiliate
        """
        risk_factors = []
        
        values = df[metric_type.value].values
        
        # Check for declining trend
        if len(values) > 5:
            recent_trend = np.mean(values[-3:]) - np.mean(values[-6:-3])
            if recent_trend < 0:
                risk_factors.append("Declining performance trend")
        
        # Check for high volatility
        if len(values) > 3:
            volatility = np.std(values) / np.mean(values) if np.mean(values) > 0 else 0
            if volatility > 0.5:
                risk_factors.append("High performance volatility")
        
        # Check for recent drops
        if len(values) > 2:
            recent_drop = (values[-1] - values[-2]) / values[-2] if values[-2] > 0 else 0
            if recent_drop < -0.2:
                risk_factors.append("Recent performance drop")
        
        return risk_factors
    
    def _generate_affiliate_recommendations(self, df: pd.DataFrame, metric_type: PredictionType,
                                          predicted_value: float, risk_factors: List[str]) -> List[str]:
        """
        Generate recommendations for affiliate
        """
        recommendations = []
        
        # Performance-based recommendations
        if metric_type == PredictionType.REVENUE:
            if predicted_value < df[metric_type.value].mean():
                recommendations.append("Focus on increasing conversion rates")
                recommendations.append("Optimize landing pages for better user experience")
        
        elif metric_type == PredictionType.CONVERSION:
            if predicted_value < 0.05:  # 5% conversion rate
                recommendations.append("Improve targeting and audience selection")
                recommendations.append("A/B test different ad creatives")
        
        # Risk-based recommendations
        if "Declining performance trend" in risk_factors:
            recommendations.append("Review and update marketing strategy")
            recommendations.append("Consider new traffic sources")
        
        if "High performance volatility" in risk_factors:
            recommendations.append("Implement more consistent marketing practices")
            recommendations.append("Diversify traffic sources")
        
        if "Recent performance drop" in risk_factors:
            recommendations.append("Investigate recent changes in campaign setup")
            recommendations.append("Check for technical issues")
        
        return recommendations
    
    def get_prediction_summary(self) -> Dict:
        """
        Get summary of all predictions
        """
        total_predictions = len(self.prediction_results)
        total_forecasts = len(self.performance_forecasts)
        total_trends = len(self.trend_analyses)
        
        # Calculate average accuracy
        if self.prediction_results:
            avg_accuracy = np.mean([r.accuracy_score for r in self.prediction_results])
        else:
            avg_accuracy = 0.0
        
        # Get prediction types distribution
        prediction_types = {}
        for result in self.prediction_results:
            pred_type = result.prediction_type.value
            if pred_type not in prediction_types:
                prediction_types[pred_type] = 0
            prediction_types[pred_type] += 1
        
        # Get trend directions
        trend_directions = {}
        for trend in self.trend_analyses:
            direction = trend.trend_direction
            if direction not in trend_directions:
                trend_directions[direction] = 0
            trend_directions[direction] += 1
        
        return {
            'total_predictions': total_predictions,
            'total_forecasts': total_forecasts,
            'total_trends': total_trends,
            'average_accuracy': avg_accuracy,
            'prediction_types': prediction_types,
            'trend_directions': trend_directions,
            'generated_at': datetime.now().isoformat()
        }
    
    def export_predictive_data(self, format: str = 'json') -> str:
        """
        Export predictive analytics data
        """
        data = {
            'predictions': [asdict(result) for result in self.prediction_results],
            'forecasts': [asdict(forecast) for forecast in self.performance_forecasts],
            'trends': [asdict(trend) for trend in self.trend_analyses],
            'summary': self.get_prediction_summary()
        }
        
        if format == 'json':
            return json.dumps(data, indent=2, default=str)
        elif format == 'csv':
            # Export predictions as CSV
            if self.prediction_results:
                df = pd.DataFrame([asdict(result) for result in self.prediction_results])
                return df.to_csv(index=False)
            else:
                return ""
        else:
            raise ValueError(f"Unsupported format: {format}")

# Example usage
def main():
    """
    Example usage of AI-Powered Predictive Analytics
    """
    # Initialize predictive analytics
    analytics = AIPoweredPredictiveAnalytics()
    
    # Add sample historical data
    for i in range(60):  # 60 days of data
        date = datetime.now() - timedelta(days=60-i)
        analytics.add_historical_data({
            'revenue': 1000 + np.random.normal(0, 100) + i * 10,
            'clicks': 1000 + np.random.normal(0, 50) + i * 5,
            'conversions': 50 + np.random.normal(0, 5) + i * 0.5,
            'affiliates': 10 + i // 10,
            'timestamp': date
        })
    
    # Make revenue prediction
    revenue_prediction = analytics.predict_revenue(TimeHorizon.MONTHLY, 30)
    print(f"Revenue prediction: ${revenue_prediction.predicted_value:.2f}")
    
    # Make conversion rate prediction
    conversion_prediction = analytics.predict_conversion_rate(TimeHorizon.MONTHLY, 30)
    print(f"Conversion rate prediction: {conversion_prediction.predicted_value:.2%}")
    
    # Analyze trends
    revenue_trend = analytics.analyze_trends('revenue', 30)
    print(f"Revenue trend: {revenue_trend.trend_direction} (strength: {revenue_trend.trend_strength:.2f})")
    
    # Forecast affiliate performance
    affiliate_forecast = analytics.forecast_affiliate_performance('affiliate_1', PredictionType.REVENUE, 30)
    if affiliate_forecast:
        print(f"Affiliate forecast: ${affiliate_forecast.predicted_value:.2f}")
        print(f"Risk factors: {affiliate_forecast.risk_factors}")
        print(f"Recommendations: {affiliate_forecast.recommendations}")
    
    # Get summary
    summary = analytics.get_prediction_summary()
    print(f"Prediction summary: {summary}")

if __name__ == "__main__":
    main()


