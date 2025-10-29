#!/usr/bin/env python3
"""
Financial Insights AI
Advanced AI-powered financial analysis and recommendations
Version: 2.0.0
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import json
from typing import List, Dict, Optional
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class FinancialInsightsAI:
    """
    AI-powered financial insights and recommendations
    """
    
    def __init__(self):
        self.transactions = []
        self.budgets = {}
        self.insights_cache = {}
    
    def analyze_financial_health(self, transactions_df: pd.DataFrame) -> Dict:
        """
        Comprehensive financial health analysis
        """
        insights = {}
        
        # 1. Income Analysis
        income = transactions_df[transactions_df['amount'] > 0]['amount'].sum()
        expenses = abs(transactions_df[transactions_df['amount'] < 0]['amount'].sum())
        
        insights['income_expense_ratio'] = income / expenses if expenses > 0 else float('inf')
        insights['savings_rate'] = ((income - expenses) / income * 100) if income > 0 else 0
        
        # 2. Expense Patterns
        category_expenses = transactions_df[transactions_df['amount'] < 0].groupby('category')['amount'].sum().abs()
        insights['top_expense_categories'] = category_expenses.nlargest(5).to_dict()
        insights['expense_concentration'] = self.calculate_concentration(category_expenses)
        
        # 3. Cash Flow Analysis
        monthly_cash_flow = transactions_df.groupby(transactions_df['date'].dt.to_period('M'))['amount'].sum()
        insights['average_monthly_cash_flow'] = monthly_cash_flow.mean()
        insights['cash_flow_volatility'] = monthly_cash_flow.std()
        insights['cash_flow_trend'] = self.analyze_trend(monthly_cash_flow.values)
        
        # 4. Spending Trends
        insights['spending_patterns'] = self.analyze_spending_patterns(transactions_df)
        
        # 5. Financial Health Score
        insights['health_score'] = self.calculate_health_score(insights)
        
        return insights
    
    def calculate_concentration(self, series: pd.Series) -> float:
        """Calculate Herfindahl index for expense concentration"""
        percentages = series / series.sum()
        return (percentages ** 2).sum()
    
    def analyze_trend(self, values: np.ndarray) -> Dict:
        """Analyze trend using linear regression"""
        if len(values) < 2:
            return {'direction': 'neutral', 'strength': 0}
        
        x = np.arange(len(values))
        slope = np.polyfit(x, values, 1)[0]
        
        direction = 'increasing' if slope > 0 else 'decreasing' if slope < 0 else 'stable'
        strength = abs(slope) / np.std(values) if np.std(values) > 0 else 0
        
        return {
            'direction': direction,
            'strength': float(strength),
            'slope': float(slope)
        }
    
    def analyze_spending_patterns(self, df: pd.DataFrame) -> Dict:
        """Analyze spending patterns"""
        patterns = {}
        
        # Weekly patterns
        df['day_of_week'] = df['date'].dt.dayofweek
        weekly_pattern = df[df['amount'] < 0].groupby('day_of_week')['amount'].sum().abs()
        patterns['weekly'] = weekly_pattern.to_dict()
        
        # Monthly patterns
        df['day_of_month'] = df['date'].dt.day
        monthly_pattern = df[df['amount'] < 0].groupby('day_of_month')['amount'].sum().abs()
        patterns['monthly'] = monthly_pattern.to_dict()
        
        return patterns
    
    def calculate_health_score(self, insights: Dict) -> Dict:
        """Calculate overall financial health score"""
        score = 100.0
        
        # Factor 1: Savings rate
        savings_rate = insights.get('savings_rate', 0)
        if savings_rate < 0:
            score -= 30
        elif savings_rate < 10:
            score -= 20
        elif savings_rate < 20:
            score -= 10
        
        # Factor 2: Income/Expense ratio
        ratio = insights.get('income_expense_ratio', 0)
        if ratio < 0.5:
            score -= 25
        elif ratio < 1.0:
            score -= 15
        
        # Factor 3: Cash flow volatility
        volatility = insights.get('cash_flow_volatility', 0)
        if volatility > insights.get('average_monthly_cash_flow', 1) * 0.5:
            score -= 15
        
        score = max(0, min(100, score))
        
        # Determine category
        if score >= 80:
            category = 'excellent'
        elif score >= 60:
            category = 'good'
        elif score >= 40:
            category = 'fair'
        else:
            category = 'needs_improvement'
        
        return {
            'score': score,
            'category': category,
            'factors': self.identify_factors(insights, score)
        }
    
    def identify_factors(self, insights: Dict, score: float) -> List[str]:
        """Identify factors affecting health score"""
        factors = []
        
        if insights.get('savings_rate', 0) < 10:
            factors.append("Low savings rate - consider reducing expenses")
        
        if insights.get('income_expense_ratio', 0) < 1.0:
            factors.append("Expenses exceeding income - review spending")
        
        volatility = insights.get('cash_flow_volatility', 0)
        avg_flow = insights.get('average_monthly_cash_flow', 1)
        if volatility > avg_flow * 0.5:
            factors.append("High cash flow volatility - create emergency fund")
        
        concentration = insights.get('expense_concentration', 0)
        if concentration > 0.5:
            factors.append("High expense concentration - diversify spending")
        
        return factors
    
    def generate_recommendations(self, insights: Dict) -> List[Dict]:
        """Generate AI-powered recommendations"""
        recommendations = []
        
        # Recommendation 1: Savings Optimization
        if insights['health_score']['score'] < 70:
            recommendations.append({
                'type': 'savings',
                'priority': 'high',
                'title': 'Optimize Savings Rate',
                'description': f"Your savings rate is {insights.get('savings_rate', 0):.1f}%. Target: 20%+",
                'action': 'Review top expense categories and identify reduction opportunities',
                'potential_savings': self.estimate_savings(insights)
            })
        
        # Recommendation 2: Expense Concentration
        concentration = insights.get('expense_concentration', 0)
        if concentration > 0.5:
            recommendations.append({
                'type': 'diversification',
                'priority': 'medium',
                'title': 'Diversify Expenses',
                'description': 'High concentration in specific categories',
                'action': 'Spread expenses more evenly across categories',
                'top_category': list(insights.get('top_expense_categories', {}).keys())[0] if insights.get('top_expense_categories') else 'unknown'
            })
        
        # Recommendation 3: Cash Flow Management
        if insights.get('cash_flow_volatility', 0) > insights.get('average_monthly_cash_flow', 1) * 0.5:
            recommendations.append({
                'type': 'cash_flow',
                'priority': 'high',
                'title': 'Stabilize Cash Flow',
                'description': 'High variability in monthly cash flow',
                'action': 'Create monthly budget and track adherence',
                'suggested_budget': self.suggest_budget(insights)
            })
        
        return recommendations
    
    def estimate_savings(self, insights: Dict) -> Dict:
        """Estimate potential savings"""
        top_categories = insights.get('top_expense_categories', {})
        
        if not top_categories:
            return {}
        
        # Estimate 10-15% reduction potential in top 3 categories
        estimated = {}
        for i, (category, amount) in enumerate(list(top_categories.items())[:3]):
            reduction_rate = 0.10 + (0.05 * (i + 1) / 3)
            estimated[category] = {
                'current': amount,
                'potential_savings': amount * reduction_rate,
                'reduction_rate': reduction_rate
            }
        
        return estimated
    
    def suggest_budget(self, insights: Dict) -> Dict:
        """Suggest optimized budget allocation"""
        avg_monthly_income = insights.get('average_monthly_cash_flow', 1000)
        
        # Use 50-30-20 rule as baseline
        budget = {
            'essential': avg_monthly_income * 0.50,
            'discretionary': avg_monthly_income * 0.30,
            'savings': avg_monthly_income * 0.20
        }
        
        return budget
    
    def predict_future(self, transactions_df: pd.DataFrame, months: int = 3) -> Dict:
        """Predict future financial performance"""
        # Prepare data for prediction
        monthly_data = transactions_df.groupby(
            transactions_df['date'].dt.to_period('M')
        )['amount'].sum().reset_index()
        monthly_data['month_num'] = range(len(monthly_data))
        
        if len(monthly_data) < 3:
            return {'error': 'Insufficient data for prediction'}
        
        # Simple linear trend projection
        x = monthly_data['month_num'].values
        y = monthly_data['amount'].values
        
        slope = np.polyfit(x, y, 1)[0]
        intercept = np.polyfit(x, y, 1)[1]
        
        # Predict next months
        future_months = []
        for i in range(1, months + 1):
            predicted_value = slope * (len(monthly_data) + i) + intercept
            future_months.append({
                'month': (datetime.now() + timedelta(days=30*i)).strftime('%Y-%m'),
                'predicted': float(predicted_value)
            })
        
        return {
            'predictions': future_months,
            'trend': 'increasing' if slope > 0 else 'decreasing',
            'confidence': min(0.85, len(monthly_data) / 24)
        }
    
    def detect_anomalies(self, transactions_df: pd.DataFrame) -> List[Dict]:
        """Detect anomalous spending patterns"""
        anomalies = []
        
        # Z-score based anomaly detection
        for category in transactions_df['category'].unique():
            category_df = transactions_df[transactions_df['category'] == category]
            
            amounts = category_df['amount'].abs()
            mean = amounts.mean()
            std = amounts.std()
            
            if std > 0:
                for _, row in category_df.iterrows():
                    z_score = abs((abs(row['amount']) - mean) / std)
                    
                    if z_score > 2.5:
                        anomalies.append({
                            'date': str(row['date']),
                            'amount': abs(row['amount']),
                            'category': category,
                            'description': row.get('description', ''),
                            'z_score': float(z_score),
                            'severity': 'high' if z_score > 3.5 else 'medium'
                        })
        
        return sorted(anomalies, key=lambda x: x['z_score'], reverse=True)
    
    def generate_report(self, transactions_df: pd.DataFrame) -> Dict:
        """Generate comprehensive financial report"""
        logger.info("Generating comprehensive financial report...")
        
        # Analyze financial health
        insights = self.analyze_financial_health(transactions_df)
        
        # Generate recommendations
        recommendations = self.generate_recommendations(insights)
        
        # Predict future
        predictions = self.predict_future(transactions_df, months=3)
        
        # Detect anomalies
        anomalies = self.detect_anomalies(transactions_df)
        
        report = {
            'timestamp': datetime.now().isoformat(),
            'summary': {
                'total_transactions': len(transactions_df),
                'total_income': float(transactions_df[transactions_df['amount'] > 0]['amount'].sum()),
                'total_expenses': float(abs(transactions_df[transactions_df['amount'] < 0]['amount'].sum())),
                'net_flow': float(transactions_df['amount'].sum())
            },
            'health': insights['health_score'],
            'recommendations': recommendations,
            'predictions': predictions,
            'anomalies': anomalies,
            'insights': insights
        }
        
        return report


# Example usage
if __name__ == "__main__":
    print("=" * 60)
    print("Financial Insights AI v2.0.0")
    print("=" * 60)
    
    # Create sample data
    dates = pd.date_range(start='2024-01-01', end='2024-12-31', freq='D')
    
    np.random.seed(42)
    transactions_data = []
    categories = ['Food & Dining', 'Transportation', 'Bills & Utilities', 'Shopping', 'Entertainment']
    
    for i, date in enumerate(dates):
        if np.random.random() < 0.7:  # 70% chance of transaction
            amount = np.random.choice([1, -1]) * np.random.uniform(10, 200)
            transactions_data.append({
                'date': date,
                'amount': amount,
                'category': np.random.choice(categories),
                'description': f'Sample transaction {i}'
            })
    
    df = pd.DataFrame(transactions_data)
    
    # Analyze
    ai = FinancialInsightsAI()
    report = ai.generate_report(df)
    
    print("\n" + "=" * 60)
    print("FINANCIAL HEALTH REPORT")
    print("=" * 60)
    print(f"\n📊 Health Score: {report['health']['score']:.0f}/100 ({report['health']['category']})")
    print(f"\n💰 Total Income: ${report['summary']['total_income']:,.2f}")
    print(f"💸 Total Expenses: ${report['summary']['total_expenses']:,.2f}")
    print(f"📈 Net Flow: ${report['summary']['net_flow']:,.2f}")
    
    print(f"\n🎯 Recommendations ({len(report['recommendations'])}):")
    for i, rec in enumerate(report['recommendations'], 1):
        print(f"  {i}. [{rec['priority'].upper()}] {rec['title']}")
        print(f"     {rec['description']}")
    
    if report['anomalies']:
        print(f"\n⚠️  Anomalies Detected ({len(report['anomalies'])}):")
        for i, anomaly in enumerate(report['anomalies'][:5], 1):
            print(f"  {i}. {anomaly['date']} - ${anomaly['amount']:.2f} in {anomaly['category']}")
    
    print("\n✅ Report generation complete!")
    print("\nSaving report to: financial_insights_report.json")
    
    # Save report
    with open('financial_insights_report.json', 'w') as f:
        json.dump(report, f, indent=2, default=str)
    
    print("\n✅ Financial Insights AI Demo Complete!")



