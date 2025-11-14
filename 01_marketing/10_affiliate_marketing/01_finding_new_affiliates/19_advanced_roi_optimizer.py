#!/usr/bin/env python3
"""
Advanced ROI Optimizer for Affiliate Marketing
==============================================

This module provides comprehensive ROI optimization capabilities for affiliate marketing,
including predictive modeling, budget allocation, and performance maximization.

Author: AI Marketing System
Version: 2.0
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from typing import Dict, List, Optional, Tuple
import json
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
import scipy.optimize as optimize
from scipy import stats
import warnings
warnings.filterwarnings('ignore')

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class OptimizationStrategy(Enum):
    """ROI optimization strategies"""
    MAXIMIZE_REVENUE = "maximize_revenue"
    MINIMIZE_COST = "minimize_cost"
    MAXIMIZE_ROI = "maximize_roi"
    BALANCED = "balanced"

@dataclass
class ROIProjection:
    """ROI projection data structure"""
    period: str
    projected_revenue: float
    projected_cost: float
    projected_roi: float
    confidence_level: float
    risk_score: float

@dataclass
class BudgetAllocation:
    """Budget allocation data structure"""
    affiliate_id: str
    allocated_budget: float
    expected_roi: float
    risk_level: str
    priority_score: float

@dataclass
class PerformanceMetrics:
    """Performance metrics data structure"""
    affiliate_id: str
    revenue: float
    cost: float
    roi: float
    conversion_rate: float
    click_through_rate: float
    engagement_rate: float
    lifetime_value: float
    churn_rate: float

class AdvancedROIOptimizer:
    """
    Advanced ROI Optimizer for Affiliate Marketing
    """
    
    def __init__(self):
        self.performance_data = []
        self.roi_models = {}
        self.optimization_rules = []
        self.budget_allocations = []
        self.projection_models = {}
        
        # Initialize optimization parameters
        self.optimization_params = {
            'min_roi_threshold': 0.2,  # 20% minimum ROI
            'max_risk_tolerance': 0.3,  # 30% maximum risk
            'budget_constraint': 10000,  # $10,000 total budget
            'optimization_horizon': 30  # 30 days
        }
    
    def add_performance_data(self, metrics: PerformanceMetrics):
        """
        Add performance metrics data
        """
        self.performance_data.append(metrics)
        logger.info(f"Added performance data for affiliate {metrics.affiliate_id}")
    
    def calculate_roi(self, revenue: float, cost: float) -> float:
        """
        Calculate ROI
        """
        if cost == 0:
            return float('inf') if revenue > 0 else 0.0
        return (revenue - cost) / cost
    
    def calculate_roi_metrics(self) -> Dict:
        """
        Calculate comprehensive ROI metrics
        """
        if not self.performance_data:
            return {}
        
        # Convert to DataFrame for easier analysis
        df = pd.DataFrame([asdict(metric) for metric in self.performance_data])
        
        # Calculate overall metrics
        total_revenue = df['revenue'].sum()
        total_cost = df['cost'].sum()
        overall_roi = self.calculate_roi(total_revenue, total_cost)
        
        # Calculate per-affiliate metrics
        affiliate_metrics = df.groupby('affiliate_id').agg({
            'revenue': 'sum',
            'cost': 'sum',
            'roi': 'mean',
            'conversion_rate': 'mean',
            'click_through_rate': 'mean',
            'engagement_rate': 'mean',
            'lifetime_value': 'mean',
            'churn_rate': 'mean'
        }).reset_index()
        
        # Calculate ROI for each affiliate
        affiliate_metrics['calculated_roi'] = affiliate_metrics.apply(
            lambda row: self.calculate_roi(row['revenue'], row['cost']), axis=1
        )
        
        # Calculate performance scores
        affiliate_metrics['performance_score'] = self._calculate_performance_score(affiliate_metrics)
        
        # Calculate risk scores
        affiliate_metrics['risk_score'] = self._calculate_risk_score(affiliate_metrics)
        
        return {
            'overall': {
                'total_revenue': total_revenue,
                'total_cost': total_cost,
                'overall_roi': overall_roi,
                'num_affiliates': len(affiliate_metrics)
            },
            'affiliate_metrics': affiliate_metrics.to_dict('records'),
            'summary_stats': self._calculate_summary_stats(affiliate_metrics)
        }
    
    def _calculate_performance_score(self, df: pd.DataFrame) -> pd.Series:
        """
        Calculate performance score for each affiliate
        """
        # Normalize metrics to 0-1 scale
        normalized_roi = (df['calculated_roi'] - df['calculated_roi'].min()) / (df['calculated_roi'].max() - df['calculated_roi'].min())
        normalized_conversion = (df['conversion_rate'] - df['conversion_rate'].min()) / (df['conversion_rate'].max() - df['conversion_rate'].min())
        normalized_engagement = (df['engagement_rate'] - df['engagement_rate'].min()) / (df['engagement_rate'].max() - df['engagement_rate'].min())
        normalized_lifetime_value = (df['lifetime_value'] - df['lifetime_value'].min()) / (df['lifetime_value'].max() - df['lifetime_value'].min())
        
        # Calculate weighted performance score
        performance_score = (
            normalized_roi * 0.4 +
            normalized_conversion * 0.3 +
            normalized_engagement * 0.2 +
            normalized_lifetime_value * 0.1
        )
        
        return performance_score.fillna(0)
    
    def _calculate_risk_score(self, df: pd.DataFrame) -> pd.Series:
        """
        Calculate risk score for each affiliate
        """
        # Higher churn rate and lower engagement indicate higher risk
        risk_score = (
            df['churn_rate'] * 0.6 +
            (1 - df['engagement_rate']) * 0.4
        )
        
        return risk_score.fillna(0.5)
    
    def _calculate_summary_stats(self, df: pd.DataFrame) -> Dict:
        """
        Calculate summary statistics
        """
        return {
            'avg_roi': df['calculated_roi'].mean(),
            'median_roi': df['calculated_roi'].median(),
            'std_roi': df['calculated_roi'].std(),
            'min_roi': df['calculated_roi'].min(),
            'max_roi': df['calculated_roi'].max(),
            'avg_conversion_rate': df['conversion_rate'].mean(),
            'avg_engagement_rate': df['engagement_rate'].mean(),
            'avg_lifetime_value': df['lifetime_value'].mean(),
            'avg_churn_rate': df['churn_rate'].mean()
        }
    
    def train_roi_prediction_models(self) -> Dict:
        """
        Train ROI prediction models
        """
        if len(self.performance_data) < 10:
            logger.warning("Not enough data to train models")
            return {}
        
        # Convert to DataFrame
        df = pd.DataFrame([asdict(metric) for metric in self.performance_data])
        
        # Prepare features
        feature_columns = ['conversion_rate', 'click_through_rate', 'engagement_rate', 'lifetime_value', 'churn_rate']
        X = df[feature_columns].fillna(0)
        y = df['roi'].fillna(0)
        
        # Split data
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
        
        # Scale features
        scaler = StandardScaler()
        X_train_scaled = scaler.fit_transform(X_train)
        X_test_scaled = scaler.transform(X_test)
        
        # Train multiple models
        models = {
            'linear_regression': LinearRegression(),
            'ridge_regression': Ridge(alpha=1.0),
            'lasso_regression': Lasso(alpha=1.0),
            'random_forest': RandomForestRegressor(n_estimators=100, random_state=42),
            'gradient_boosting': GradientBoostingRegressor(n_estimators=100, random_state=42)
        }
        
        model_performance = {}
        
        for name, model in models.items():
            # Train model
            model.fit(X_train_scaled, y_train)
            
            # Make predictions
            y_pred = model.predict(X_test_scaled)
            
            # Calculate metrics
            mse = mean_squared_error(y_test, y_pred)
            r2 = r2_score(y_test, y_pred)
            mae = mean_absolute_error(y_test, y_pred)
            
            # Cross-validation score
            cv_scores = cross_val_score(model, X_train_scaled, y_train, cv=5)
            
            model_performance[name] = {
                'model': model,
                'mse': mse,
                'r2': r2,
                'mae': mae,
                'cv_mean': cv_scores.mean(),
                'cv_std': cv_scores.std()
            }
            
            # Store model
            self.roi_models[name] = {
                'model': model,
                'scaler': scaler,
                'feature_columns': feature_columns
            }
        
        # Select best model
        best_model_name = max(model_performance.keys(), key=lambda k: model_performance[k]['r2'])
        self.best_model = best_model_name
        
        logger.info(f"Best model: {best_model_name} (R² = {model_performance[best_model_name]['r2']:.3f})")
        
        return {
            'model_performance': model_performance,
            'best_model': best_model_name,
            'feature_importance': self._get_feature_importance(best_model_name)
        }
    
    def _get_feature_importance(self, model_name: str) -> Dict:
        """
        Get feature importance for the best model
        """
        if model_name not in self.roi_models:
            return {}
        
        model = self.roi_models[model_name]['model']
        feature_columns = self.roi_models[model_name]['feature_columns']
        
        if hasattr(model, 'feature_importances_'):
            importance = model.feature_importances_
        elif hasattr(model, 'coef_'):
            importance = np.abs(model.coef_)
        else:
            return {}
        
        return dict(zip(feature_columns, importance))
    
    def predict_roi(self, affiliate_data: Dict) -> Dict:
        """
        Predict ROI for affiliate
        """
        if not self.roi_models or self.best_model not in self.roi_models:
            logger.warning("No trained models available")
            return {}
        
        model_info = self.roi_models[self.best_model]
        model = model_info['model']
        scaler = model_info['scaler']
        feature_columns = model_info['feature_columns']
        
        # Prepare features
        features = np.array([[
            affiliate_data.get('conversion_rate', 0),
            affiliate_data.get('click_through_rate', 0),
            affiliate_data.get('engagement_rate', 0),
            affiliate_data.get('lifetime_value', 0),
            affiliate_data.get('churn_rate', 0)
        ]])
        
        # Scale features
        features_scaled = scaler.transform(features)
        
        # Make prediction
        predicted_roi = model.predict(features_scaled)[0]
        
        # Calculate confidence interval
        confidence_interval = self._calculate_confidence_interval(model, features_scaled)
        
        return {
            'predicted_roi': predicted_roi,
            'confidence_interval': confidence_interval,
            'model_used': self.best_model
        }
    
    def _calculate_confidence_interval(self, model, features: np.ndarray, confidence: float = 0.95) -> Tuple[float, float]:
        """
        Calculate confidence interval for prediction
        """
        # This is a simplified implementation
        # In practice, you'd use more sophisticated methods
        prediction = model.predict(features)[0]
        
        # Estimate standard error (simplified)
        std_error = 0.1  # This should be calculated properly
        
        # Calculate confidence interval
        alpha = 1 - confidence
        z_score = stats.norm.ppf(1 - alpha/2)
        
        margin_error = z_score * std_error
        
        return (prediction - margin_error, prediction + margin_error)
    
    def optimize_budget_allocation(self, strategy: OptimizationStrategy = OptimizationStrategy.MAXIMIZE_ROI) -> List[BudgetAllocation]:
        """
        Optimize budget allocation across affiliates
        """
        if not self.performance_data:
            logger.warning("No performance data available")
            return []
        
        # Calculate current metrics
        metrics = self.calculate_roi_metrics()
        affiliate_metrics = pd.DataFrame(metrics['affiliate_metrics'])
        
        if affiliate_metrics.empty:
            return []
        
        # Define optimization problem
        def objective(x):
            # x is the budget allocation vector
            total_roi = 0
            for i, row in affiliate_metrics.iterrows():
                if i < len(x):
                    # Calculate expected ROI based on allocated budget
                    expected_roi = self._calculate_expected_roi(row, x[i])
                    total_roi += expected_roi * x[i]
            return -total_roi  # Minimize negative ROI (maximize ROI)
        
        def constraint(x):
            # Budget constraint: sum of allocations <= total budget
            return self.optimization_params['budget_constraint'] - np.sum(x)
        
        # Initial guess
        n_affiliates = len(affiliate_metrics)
        x0 = np.ones(n_affiliates) * (self.optimization_params['budget_constraint'] / n_affiliates)
        
        # Bounds: each allocation must be >= 0
        bounds = [(0, self.optimization_params['budget_constraint']) for _ in range(n_affiliates)]
        
        # Constraints
        constraints = [{'type': 'ineq', 'fun': constraint}]
        
        # Optimize
        try:
            result = optimize.minimize(
                objective, x0, method='SLSQP',
                bounds=bounds, constraints=constraints
            )
            
            if result.success:
                optimized_allocations = result.x
            else:
                logger.warning("Optimization failed, using equal allocation")
                optimized_allocations = x0
                
        except Exception as e:
            logger.error(f"Optimization error: {str(e)}")
            optimized_allocations = x0
        
        # Create budget allocation objects
        allocations = []
        for i, row in affiliate_metrics.iterrows():
            if i < len(optimized_allocations):
                allocation = BudgetAllocation(
                    affiliate_id=row['affiliate_id'],
                    allocated_budget=optimized_allocations[i],
                    expected_roi=self._calculate_expected_roi(row, optimized_allocations[i]),
                    risk_level=self._get_risk_level(row['risk_score']),
                    priority_score=row['performance_score']
                )
                allocations.append(allocation)
        
        self.budget_allocations = allocations
        return allocations
    
    def _calculate_expected_roi(self, affiliate_data: pd.Series, budget: float) -> float:
        """
        Calculate expected ROI for given budget allocation
        """
        # Simplified calculation - in practice, use more sophisticated models
        base_roi = affiliate_data['calculated_roi']
        
        # Assume diminishing returns
        if budget > 0:
            # Scale ROI based on budget (diminishing returns)
            scaled_roi = base_roi * (1 - np.exp(-budget / 1000))
        else:
            scaled_roi = 0
        
        return max(0, scaled_roi)
    
    def _get_risk_level(self, risk_score: float) -> str:
        """
        Get risk level based on risk score
        """
        if risk_score < 0.3:
            return 'low'
        elif risk_score < 0.6:
            return 'medium'
        else:
            return 'high'
    
    def generate_roi_projections(self, days_ahead: int = 30) -> List[ROIProjection]:
        """
        Generate ROI projections
        """
        if not self.performance_data:
            return []
        
        # Convert to DataFrame
        df = pd.DataFrame([asdict(metric) for metric in self.performance_data])
        
        # Group by date (assuming we have date information)
        # For this example, we'll use the order of data points
        df['date'] = pd.date_range(start='2024-01-01', periods=len(df), freq='D')
        
        # Calculate daily ROI
        daily_roi = df.groupby('date').agg({
            'revenue': 'sum',
            'cost': 'sum'
        }).reset_index()
        
        daily_roi['roi'] = daily_roi.apply(
            lambda row: self.calculate_roi(row['revenue'], row['cost']), axis=1
        )
        
        # Generate projections
        projections = []
        
        for i in range(days_ahead):
            # Simple trend-based projection
            if len(daily_roi) > 1:
                # Calculate trend
                recent_roi = daily_roi['roi'].tail(7).mean()  # Last 7 days
                trend = np.polyfit(range(len(daily_roi)), daily_roi['roi'], 1)[0]
                
                # Project future ROI
                projected_roi = recent_roi + trend * (i + 1)
                
                # Project revenue and cost
                recent_revenue = daily_roi['revenue'].tail(7).mean()
                recent_cost = daily_roi['cost'].tail(7).mean()
                
                projected_revenue = recent_revenue * (1 + trend * 0.1)  # Assume 10% of trend affects revenue
                projected_cost = recent_cost * (1 + trend * 0.05)  # Assume 5% of trend affects cost
                
                # Calculate confidence level
                confidence = max(0.1, 1.0 - (i * 0.02))  # Decreasing confidence over time
                
                # Calculate risk score
                risk_score = min(1.0, abs(trend) * 10)  # Higher trend = higher risk
                
            else:
                # Use default values if not enough data
                projected_roi = 0.2
                projected_revenue = 1000
                projected_cost = 800
                confidence = 0.5
                risk_score = 0.5
            
            projection = ROIProjection(
                period=f"Day {i+1}",
                projected_revenue=projected_revenue,
                projected_cost=projected_cost,
                projected_roi=projected_roi,
                confidence_level=confidence,
                risk_score=risk_score
            )
            projections.append(projection)
        
        return projections
    
    def generate_optimization_report(self) -> Dict:
        """
        Generate comprehensive optimization report
        """
        # Calculate current metrics
        metrics = self.calculate_roi_metrics()
        
        # Train models if not already trained
        if not self.roi_models:
            model_results = self.train_roi_prediction_models()
        else:
            model_results = {}
        
        # Generate budget allocation
        budget_allocations = self.optimize_budget_allocation()
        
        # Generate projections
        projections = self.generate_roi_projections()
        
        # Calculate optimization impact
        optimization_impact = self._calculate_optimization_impact(metrics, budget_allocations)
        
        return {
            'timestamp': datetime.now().isoformat(),
            'current_metrics': metrics,
            'model_performance': model_results,
            'budget_allocations': [asdict(allocation) for allocation in budget_allocations],
            'projections': [asdict(projection) for projection in projections],
            'optimization_impact': optimization_impact,
            'recommendations': self._generate_optimization_recommendations(metrics, budget_allocations)
        }
    
    def _calculate_optimization_impact(self, metrics: Dict, allocations: List[BudgetAllocation]) -> Dict:
        """
        Calculate optimization impact
        """
        if not allocations:
            return {}
        
        # Calculate total expected ROI
        total_expected_roi = sum(allocation.expected_roi * allocation.allocated_budget for allocation in allocations)
        total_budget = sum(allocation.allocated_budget for allocation in allocations)
        
        # Calculate current ROI
        current_roi = metrics['overall']['overall_roi']
        
        # Calculate improvement
        roi_improvement = (total_expected_roi / total_budget) - current_roi if total_budget > 0 else 0
        
        return {
            'current_roi': current_roi,
            'projected_roi': total_expected_roi / total_budget if total_budget > 0 else 0,
            'roi_improvement': roi_improvement,
            'roi_improvement_percent': (roi_improvement / current_roi * 100) if current_roi > 0 else 0,
            'total_budget': total_budget,
            'expected_revenue': total_expected_roi
        }
    
    def _generate_optimization_recommendations(self, metrics: Dict, allocations: List[BudgetAllocation]) -> List[str]:
        """
        Generate optimization recommendations
        """
        recommendations = []
        
        # Analyze current performance
        if metrics['overall']['overall_roi'] < 0.2:
            recommendations.append("Overall ROI is below 20%. Consider optimizing affiliate selection and targeting.")
        
        # Analyze budget allocation
        if allocations:
            high_risk_allocations = [a for a in allocations if a.risk_level == 'high']
            if len(high_risk_allocations) > len(allocations) * 0.3:
                recommendations.append("More than 30% of budget is allocated to high-risk affiliates. Consider diversifying.")
            
            low_performance_allocations = [a for a in allocations if a.priority_score < 0.5]
            if len(low_performance_allocations) > 0:
                recommendations.append("Consider reducing budget for low-performance affiliates and reallocating to top performers.")
        
        # Analyze projections
        if hasattr(self, 'projections'):
            recent_projections = self.projections[-7:]  # Last 7 days
            if recent_projections:
                avg_projected_roi = np.mean([p.projected_roi for p in recent_projections])
                if avg_projected_roi < 0.15:
                    recommendations.append("Projected ROI is declining. Review and adjust strategy.")
        
        return recommendations
    
    def export_optimization_data(self, format: str = 'json') -> str:
        """
        Export optimization data
        """
        report = self.generate_optimization_report()
        
        if format == 'json':
            return json.dumps(report, indent=2, default=str)
        elif format == 'csv':
            # Export budget allocations as CSV
            if self.budget_allocations:
                df = pd.DataFrame([asdict(allocation) for allocation in self.budget_allocations])
                return df.to_csv(index=False)
            else:
                return ""
        else:
            raise ValueError(f"Unsupported format: {format}")

# Example usage
def main():
    """
    Example usage of Advanced ROI Optimizer
    """
    # Initialize optimizer
    optimizer = AdvancedROIOptimizer()
    
    # Add sample performance data
    sample_data = [
        PerformanceMetrics('affiliate_1', 5000, 2000, 1.5, 0.05, 0.02, 0.04, 100, 0.1),
        PerformanceMetrics('affiliate_2', 8000, 3000, 1.67, 0.06, 0.025, 0.05, 120, 0.08),
        PerformanceMetrics('affiliate_3', 3000, 1500, 1.0, 0.03, 0.015, 0.03, 80, 0.15),
        PerformanceMetrics('affiliate_4', 12000, 4000, 2.0, 0.08, 0.03, 0.06, 150, 0.05),
        PerformanceMetrics('affiliate_5', 2000, 1000, 1.0, 0.02, 0.01, 0.02, 60, 0.2)
    ]
    
    for data in sample_data:
        optimizer.add_performance_data(data)
    
    # Calculate ROI metrics
    metrics = optimizer.calculate_roi_metrics()
    print(f"Overall ROI: {metrics['overall']['overall_roi']:.2%}")
    
    # Train prediction models
    model_results = optimizer.train_roi_prediction_models()
    print(f"Best model: {model_results['best_model']}")
    
    # Optimize budget allocation
    allocations = optimizer.optimize_budget_allocation()
    print(f"Optimized {len(allocations)} budget allocations")
    
    # Generate projections
    projections = optimizer.generate_roi_projections()
    print(f"Generated {len(projections)} ROI projections")
    
    # Generate report
    report = optimizer.generate_optimization_report()
    print(f"Optimization report generated: {report['optimization_impact']}")

if __name__ == "__main__":
    main()


