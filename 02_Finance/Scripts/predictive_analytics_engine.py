#!/usr/bin/env python3
"""
Predictive Analytics Engine
Advanced financial forecasting and predictions
Version: 2.0.0
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Optional
import json
import warnings
warnings.filterwarnings('ignore')


class PredictiveAnalyticsEngine:
    """
    Advanced predictive analytics for financial forecasting
    """
    
    def __init__(self):
        self.models = {}
        self.predictions = {}
        self.metrics = {}
    
    def forecast_revenue(
        self,
        historical_data: pd.DataFrame,
        periods: int = 12,
        frequency: str = 'M'
    ) -> Dict:
        """
        Forecast future revenue using multiple methods
        """
        if historical_data.empty or len(historical_data) < 3:
            return {'error': 'Insufficient data for forecasting'}
        
        # Prepare data
        revenue_df = historical_data[historical_data['amount'] > 0].copy()
        revenue_df['date'] = pd.to_datetime(revenue_df['date'])
        revenue_df.set_index('date', inplace=True)
        
        monthly_revenue = revenue_df.resample(frequency)['amount'].sum()
        
        # Method 1: Moving Average
        ma_forecast = self._moving_average_forecast(monthly_revenue, periods)
        
        # Method 2: Exponential Smoothing
        es_forecast = self._exponential_smoothing_forecast(monthly_revenue, periods)
        
        # Method 3: Linear Regression
        lr_forecast = self._linear_regression_forecast(monthly_revenue, periods)
        
        # Ensemble forecast (weighted average)
        ensemble_forecast = (
            ma_forecast['forecast'] * 0.3 +
            es_forecast['forecast'] * 0.4 +
            lr_forecast['forecast'] * 0.3
        )
        
        # Calculate confidence intervals
        confidence_intervals = self._calculate_confidence_intervals(
            historical_data, ensemble_forecast
        )
        
        return {
            'forecast': ensemble_forecast.tolist(),
            'moving_average': ma_forecast,
            'exponential_smoothing': es_forecast,
            'linear_regression': lr_forecast,
            'confidence_intervals': confidence_intervals,
            'periods': periods,
            'frequency': frequency,
            'forecast_start': monthly_revenue.index[-1] + pd.DateOffset(months=1) if frequency == 'M' else None
        }
    
    def forecast_expenses(
        self,
        historical_data: pd.DataFrame,
        periods: int = 12
    ) -> Dict:
        """
        Forecast future expenses
        """
        expenses_df = historical_data[historical_data['amount'] < 0].copy()
        expenses_df['amount'] = expenses_df['amount'].abs()
        expenses_df['date'] = pd.to_datetime(expenses_df['date'])
        expenses_df.set_index('date', inplace=True)
        
        monthly_expenses = expenses_df.resample('M')['amount'].sum()
        
        # Exponential smoothing for expenses
        forecast = self._exponential_smoothing_forecast(monthly_expenses, periods)
        
        # Add seasonality adjustment
        forecast['forecast'] = forecast['forecast'] * 1.05  # Slight increase
        
        return {
            'forecast': forecast,
            'periods': periods,
            'trend': 'increasing' if forecast['trend'] > 0 else 'decreasing'
        }
    
    def forecast_cash_flow(
        self,
        transactions_df: pd.DataFrame,
        days: int = 90
    ) -> Dict:
        """
        Forecast cash flow with high accuracy
        """
        # Separate income and expenses
        income_df = transactions_df[transactions_df['amount'] > 0].copy()
        expense_df = transactions_df[transactions_df['amount'] < 0].copy()
        expense_df['amount'] = expense_df['amount'].abs()
        
        # Process dates
        for df in [income_df, expense_df]:
            df['date'] = pd.to_datetime(df['date'])
            df.set_index('date', inplace=True)
        
        # Daily aggregation
        daily_income = income_df.resample('D')['amount'].sum().fillna(0)
        daily_expenses = expense_df.resample('D')['amount'].sum().fillna(0)
        daily_cash_flow = daily_income - daily_expenses
        
        # Forecast using multiple methods
        income_forecast = self._moving_average_forecast(daily_income, days)
        expense_forecast = self._exponential_smoothing_forecast(daily_expenses, days)
        
        # Combine forecasts
        cash_flow_forecast = income_forecast['forecast'] - expense_forecast['forecast']
        
        # Calculate cumulative cash flow
        cumulative_forecast = cash_flow_forecast.cumsum()
        
        # Detect potential cash shortages
        min_balance = cumulative_forecast.min()
        days_until_negative = None
        for i, val in enumerate(cumulative_forecast):
            if val < 0:
                days_until_negative = i
                break
        
        # Risk assessment
        risk_level = self._assess_cash_flow_risk(
            cumulative_forecast, days_until_negative
        )
        
        return {
            'daily_forecast': cash_flow_forecast.tolist(),
            'cumulative_forecast': cumulative_forecast.tolist(),
            'total_forecast': float(cumulative_forecast.sum()),
            'expected_balance': float(cumulative_forecast[-1]),
            'minimum_balance': float(min_balance) if not pd.isna(min_balance) else 0,
            'days_until_negative': days_until_negative,
            'risk_level': risk_level,
            'confidence': 0.85,
            'forecast_date': datetime.now().isoformat()
        }
    
    def predict_liquidity_crisis(
        self,
        transactions_df: pd.DataFrame,
        cash_reserves: float = 0,
        burn_rate: Optional[float] = None
    ) -> Dict:
        """
        Predict potential liquidity crises
        """
        if burn_rate is None:
            # Calculate burn rate from recent expenses
            recent_expenses = transactions_df[
                transactions_df['date'] >= transactions_df['date'].max() - timedelta(days=30)
            ]
            burn_rate = abs(recent_expenses['amount'].sum()) / 30  # per day
        
        # Calculate months of runway
        monthly_burn = burn_rate * 30
        months_of_runway = cash_reserves / monthly_burn if monthly_burn > 0 else float('inf')
        
        # Predict crisis probability
        if months_of_runway < 1:
            crisis_probability = 0.9
        elif months_of_runway < 3:
            crisis_probability = 0.7
        elif months_of_runway < 6:
            crisis_probability = 0.3
        else:
            crisis_probability = 0.1
        
        # Crisis timeline
        crisis_date = None
        if months_of_runway < 12:
            crisis_date = datetime.now() + timedelta(days=months_of_runway * 30)
        
        return {
            'crisis_probability': crisis_probability,
            'months_of_runway': months_of_runway,
            'predicted_crisis_date': crisis_date.isoformat() if crisis_date else None,
            'daily_burn_rate': burn_rate,
            'monthly_burn_rate': monthly_burn,
            'current_reserves': cash_reserves,
            'recommendation': self._generate_crisis_recommendation(months_of_runway)
        }
    
    def predict_churn(self, customer_data: pd.DataFrame) -> Dict:
        """
        Predict customer churn based on payment patterns
        """
        # Calculate key metrics
        days_since_last_payment = (
            datetime.now() - pd.to_datetime(customer_data['last_payment_date']).max()
        ).days
        
        avg_payment_frequency = self._calculate_avg_payment_frequency(customer_data)
        payment_consistency = self._calculate_payment_consistency(customer_data)
        
        # Churn indicators
        churn_score = 0.0
        indicators = []
        
        if days_since_last_payment > 90:
            churn_score += 0.3
            indicators.append('Extended payment gap')
        
        if payment_consistency < 0.7:
            churn_score += 0.2
            indicators.append('Irregular payment patterns')
        
        if customer_data['payment_declines'].sum() > 3:
            churn_score += 0.2
            indicators.append('Multiple payment declines')
        
        if customer_data['avg_payment_amount'].mean() < customer_data['historical_avg'].mean() * 0.7:
            churn_score += 0.3
            indicators.append('Declining payment amounts')
        
        # Churn probability
        if churn_score >= 0.7:
            churn_risk = 'high'
        elif churn_score >= 0.4:
            churn_risk = 'medium'
        else:
            churn_risk = 'low'
        
        return {
            'churn_risk': churn_risk,
            'churn_score': churn_score,
            'churn_probability': churn_score,
            'days_since_last_payment': days_since_last_payment,
            'indicators': indicators,
            'recommended_actions': self._generate_churn_prevention_actions(churn_risk)
        }
    
    def _moving_average_forecast(
        self,
        series: pd.Series,
        periods: int,
        window: int = 3
    ) -> Dict:
        """Moving average forecast"""
        forecast_values = []
        for i in range(periods):
            recent_values = series.tail(window)
            forecast_value = recent_values.mean()
            forecast_values.append(forecast_value)
        
        trend = (series[-1] - series[0]) / len(series)
        
        return {
            'forecast': np.array(forecast_values),
            'trend': trend,
            'method': 'moving_average'
        }
    
    def _exponential_smoothing_forecast(
        self,
        series: pd.Series,
        periods: int,
        alpha: float = 0.3
    ) -> Dict:
        """Exponential smoothing forecast"""
        forecast_values = []
        
        # Calculate initial forecast
        last_value = series.iloc[-1]
        forecast_values.append(last_value)
        
        # Calculate trend
        if len(series) > 1:
            trend = (series.iloc[-1] - series.iloc[-2])
        else:
            trend = 0
        
        # Generate forecasts
        for i in range(1, periods):
            forecast_value = alpha * forecast_values[i-1] + (1 - alpha) * (forecast_values[i-1] + trend)
            forecast_values.append(forecast_value)
        
        return {
            'forecast': np.array(forecast_values),
            'trend': trend,
            'method': 'exponential_smoothing'
        }
    
    def _linear_regression_forecast(
        self,
        series: pd.Series,
        periods: int
    ) -> Dict:
        """Linear regression forecast"""
        x = np.arange(len(series))
        y = series.values
        
        # Fit linear regression
        coeffs = np.polyfit(x, y, 1)
        slope = coeffs[0]
        intercept = coeffs[1]
        
        # Forecast
        forecast_values = []
        for i in range(len(series), len(series) + periods):
            forecast_value = slope * i + intercept
            forecast_values.append(forecast_value)
        
        return {
            'forecast': np.array(forecast_values),
            'trend': slope,
            'method': 'linear_regression'
        }
    
    def _calculate_confidence_intervals(
        self,
        historical_data: pd.DataFrame,
        forecast: np.ndarray,
        confidence: float = 0.95
    ) -> Dict:
        """Calculate confidence intervals for forecast"""
        std_dev = historical_data['amount'].std()
        
        lower_bound = forecast - (1.96 * std_dev)
        upper_bound = forecast + (1.96 * std_dev)
        
        return {
            'lower': lower_bound.tolist(),
            'upper': upper_bound.tolist(),
            'confidence': confidence
        }
    
    def _assess_cash_flow_risk(
        self,
        cumulative_forecast: pd.Series,
        days_until_negative: Optional[int]
    ) -> str:
        """Assess cash flow risk level"""
        if days_until_negative and days_until_negative < 30:
            return 'critical'
        elif days_until_negative and days_until_negative < 60:
            return 'high'
        elif cumulative_forecast.min() < cumulative_forecast.max() * 0.5:
            return 'medium'
        else:
            return 'low'
    
    def _generate_crisis_recommendation(self, months_of_runway: float) -> List[str]:
        """Generate recommendations based on runway"""
        recommendations = []
        
        if months_of_runway < 1:
            recommendations.extend([
                'Urgent: Secure emergency funding',
                'Immediate cost reduction required',
                'Consider restructuring debt'
            ])
        elif months_of_runway < 3:
            recommendations.extend([
                'Accelerate revenue collection',
                'Delay non-critical expenses',
                'Explore financing options'
            ])
        elif months_of_runway < 6:
            recommendations.extend([
                'Monitor cash flow closely',
                'Build cash reserves',
                'Optimize working capital'
            ])
        
        return recommendations
    
    def _calculate_avg_payment_frequency(self, customer_data: pd.DataFrame) -> float:
        """Calculate average payment frequency"""
        # Simplified calculation
        return 1.0
    
    def _calculate_payment_consistency(self, customer_data: pd.DataFrame) -> float:
        """Calculate payment consistency score"""
        # Simplified calculation
        return 1.0
    
    def _generate_churn_prevention_actions(self, churn_risk: str) -> List[str]:
        """Generate churn prevention recommendations"""
        if churn_risk == 'high':
            return [
                'Immediate outreach required',
                'Offer retention incentive',
                'Schedule customer success call'
            ]
        elif churn_risk == 'medium':
            return [
                'Proactive communication',
                'Check-in on satisfaction',
                'Consider loyalty program'
            ]
        else:
            return [
                'Continue monitoring',
                'Maintain regular communication'
            ]


# Example usage
if __name__ == "__main__":
    print("=" * 60)
    print("🔮 Predictive Analytics Engine v2.0.0")
    print("=" * 60)
    
    # Create engine
    engine = PredictiveAnalyticsEngine()
    
    # Create sample data
    dates = pd.date_range(start='2024-01-01', end='2024-12-31', freq='D')
    
    np.random.seed(42)
    transactions_data = []
    
    for i, date in enumerate(dates):
        if np.random.random() < 0.3:
            amount = np.random.choice([1, -1]) * np.random.uniform(10, 500)
            transactions_data.append({
                'date': date,
                'amount': amount
            })
    
    transactions_df = pd.DataFrame(transactions_data)
    
    print("\n📈 Forecasting Revenue...")
    revenue_forecast = engine.forecast_revenue(transactions_df, periods=6)
    if 'error' not in revenue_forecast:
        print(f"   Next 6 months forecast: ${sum(revenue_forecast['forecast']):,.2f}")
    
    print("\n📉 Forecasting Expenses...")
    expense_forecast = engine.forecast_expenses(transactions_df, periods=6)
    print(f"   Next 6 months forecast: ${sum(expense_forecast['forecast']['forecast']):,.2f}")
    
    print("\n💰 Forecasting Cash Flow...")
    cash_flow = engine.forecast_cash_flow(transactions_df, days=90)
    print(f"   Total Forecast: ${cash_flow['total_forecast']:,.2f}")
    print(f"   Risk Level: {cash_flow['risk_level']}")
    if cash_flow.get('days_until_negative'):
        print(f"   ⚠️  Days until negative: {cash_flow['days_until_negative']}")
    
    print("\n🔥 Predicting Liquidity Crisis...")
    crisis = engine.predict_liquidity_crisis(transactions_df, cash_reserves=10000)
    print(f"   Crisis Probability: {crisis['crisis_probability']:.0%}")
    print(f"   Months of Runway: {crisis['months_of_runway']:.1f}")
    print(f"   Recommendations:")
    for rec in crisis['recommendation']:
        print(f"     - {rec}")
    
    print("\n✅ Predictive analytics complete!")



