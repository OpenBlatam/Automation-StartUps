#!/usr/bin/env python3
"""
Advanced Financial Reporting System
Automated report generation with AI insights
Version: 2.0.0
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import json
from dataclasses import dataclass


@dataclass
class FinancialReport:
    """Represents a comprehensive financial report"""
    report_id: str
    period_start: datetime
    period_end: datetime
    report_type: str
    summary: Dict
    detailed_analysis: Dict
    recommendations: List[str]
    charts_data: Dict
    metadata: Dict
    
    def to_dict(self):
        return {
            'report_id': self.report_id,
            'period_start': self.period_start.isoformat(),
            'period_end': self.period_end.isoformat(),
            'report_type': self.report_type,
            'summary': self.summary,
            'detailed_analysis': self.detailed_analysis,
            'recommendations': self.recommendations,
            'charts_data': self.charts_data,
            'metadata': self.metadata
        }


class AdvancedFinancialReporting:
    """
    Generate comprehensive financial reports with AI insights
    """
    
    def __init__(self):
        self.reports_generated = []
        self.report_templates = {}
    
    def generate_executive_summary(
        self,
        transactions_df: pd.DataFrame,
        period_start: datetime,
        period_end: datetime
    ) -> Dict:
        """
        Generate executive summary report
        """
        period_df = transactions_df[
            (transactions_df['date'] >= period_start) &
            (transactions_df['date'] <= period_end)
        ]
        
        # Calculate key metrics
        income = period_df[period_df['amount'] > 0]['amount'].sum()
        expenses = abs(period_df[period_df['amount'] < 0]['amount'].sum())
        net_flow = income - expenses
        
        # Growth metrics
        previous_period_df = transactions_df[
            (transactions_df['date'] >= period_start - timedelta(days=(period_end - period_start).days)) &
            (transactions_df['date'] < period_start)
        ]
        
        previous_income = previous_period_df[previous_period_df['amount'] > 0]['amount'].sum()
        income_growth = ((income - previous_income) / previous_income * 100) if previous_income > 0 else 0
        
        return {
            'period': {
                'start': period_start.isoformat(),
                'end': period_end.isoformat(),
                'duration_days': (period_end - period_start).days
            },
            'financials': {
                'total_income': float(income),
                'total_expenses': float(expenses),
                'net_cash_flow': float(net_flow),
                'profit_margin': (net_flow / income * 100) if income > 0 else 0
            },
            'growth': {
                'income_growth_rate': float(income_growth),
                'expense_growth_rate': 0,  # Calculate similarly
                'net_growth_rate': 0
            },
            'top_categories': self._get_top_categories(period_df),
            'key_insights': self._generate_executive_insights(income, expenses, net_flow, income_growth)
        }
    
    def generate_cash_flow_statement(
        self,
        transactions_df: pd.DataFrame,
        period_start: datetime,
        period_end: datetime
    ) -> Dict:
        """
        Generate detailed cash flow statement
        """
        period_df = transactions_df[
            (transactions_df['date'] >= period_start) &
            (transactions_df['date'] <= period_end)
        ]
        
        # Operating activities
        operating = period_df[period_df['category'].isin([
            'Food & Dining', 'Transportation', 'Shopping', 'Entertainment'
        ])]['amount'].sum()
        
        # Investing activities
        investing = period_df[period_df['category'].isin([
            'Investment', 'Equipment', 'Property'
        ])]['amount'].sum()
        
        # Financing activities
        financing = period_df[period_df['category'].isin([
            'Salary', 'Loan', 'Repayment'
        ])]['amount'].sum()
        
        total_cash_flow = operating + investing + financing
        
        return {
            'period': {
                'start': period_start.isoformat(),
                'end': period_end.isoformat()
            },
            'operating_activities': {
                'cash_in': float(operating) if operating > 0 else 0,
                'cash_out': abs(operating) if operating < 0 else 0,
                'net': float(operating)
            },
            'investing_activities': {
                'cash_in': float(investing) if investing > 0 else 0,
                'cash_out': abs(investing) if investing < 0 else 0,
                'net': float(investing)
            },
            'financing_activities': {
                'cash_in': float(financing) if financing > 0 else 0,
                'cash_out': abs(financing) if financing < 0 else 0,
                'net': float(financing)
            },
            'total_cash_flow': float(total_cash_flow),
            'period_end_balance': 0  # Would need opening balance
        }
    
    def generate_profit_loss_statement(
        self,
        transactions_df: pd.DataFrame,
        period_start: datetime,
        period_end: datetime
    ) -> Dict:
        """
        Generate profit and loss statement
        """
        period_df = transactions_df[
            (transactions_df['date'] >= period_start) &
            (transactions_df['date'] <= period_end)
        ]
        
        # Revenue
        revenue = period_df[period_df['amount'] > 0]['amount'].sum()
        
        # Expenses by category
        expenses_by_category = {}
        for category in period_df[period_df['amount'] < 0]['category'].unique():
            expenses_by_category[category] = abs(
                period_df[(period_df['category'] == category) & 
                          (period_df['amount'] < 0)]['amount'].sum()
            )
        
        # Net income
        net_income = revenue - sum(expenses_by_category.values())
        
        return {
            'period': {
                'start': period_start.isoformat(),
                'end': period_end.isoformat()
            },
            'revenue': {
                'total': float(revenue),
                'breakdown': {}
            },
            'expenses': {
                'total': float(sum(expenses_by_category.values())),
                'by_category': {k: float(v) for k, v in expenses_by_category.items()}
            },
            'net_income': float(net_income),
            'profit_margin': (net_income / revenue * 100) if revenue > 0 else 0
        }
    
    def generate_variance_analysis(
        self,
        actual_transactions: pd.DataFrame,
        budget_data: Dict,
        period_start: datetime,
        period_end: datetime
    ) -> Dict:
        """
        Generate budget variance analysis
        """
        period_df = actual_transactions[
            (actual_transactions['date'] >= period_start) &
            (actual_transactions['date'] <= period_end)
        ]
        
        variances = {}
        
        for category, budget_amount in budget_data.items():
            actual_amount = abs(
                period_df[(period_df['category'] == category) & 
                          (period_df['amount'] < 0)]['amount'].sum()
            )
            
            variance = actual_amount - budget_amount
            variance_percentage = (variance / budget_amount * 100) if budget_amount > 0 else 0
            
            variances[category] = {
                'budget': float(budget_amount),
                'actual': float(actual_amount),
                'variance': float(variance),
                'variance_percentage': float(variance_percentage),
                'status': 'over' if variance > 0 else 'under' if variance < 0 else 'met',
                'favorable': variance < 0  # Negative is favorable for expenses
            }
        
        return {
            'period': {
                'start': period_start.isoformat(),
                'end': period_end.isoformat()
            },
            'variances_by_category': variances,
            'summary': {
                'total_budget': sum(budget_data.values()),
                'total_actual': sum(v['actual'] for v in variances.values()),
                'total_variance': sum(budget_data.values()) - sum(v['actual'] for v in variances.values()),
                'over_budget_categories': sum(1 for v in variances.values() if not v['favorable']),
                'under_budget_categories': sum(1 for v in variances.values() if v['favorable'])
            }
        }
    
    def generate_trend_analysis(
        self,
        transactions_df: pd.DataFrame,
        periods: int = 6
    ) -> Dict:
        """
        Generate trend analysis report
        """
        # Group by month
        transactions_df['date'] = pd.to_datetime(transactions_df['date'])
        transactions_df['year_month'] = transactions_df['date'].dt.to_period('M')
        
        monthly_data = transactions_df.groupby('year_month').agg({
            'amount': ['sum', 'count']
        })
        
        monthly_data.columns = ['total', 'count']
        
        # Calculate trends
        income_trend = []
        expense_trend = []
        
        for month in monthly_data.index[-periods:]:
            month_df = transactions_df[transactions_df['year_month'] == month]
            
            income = month_df[month_df['amount'] > 0]['amount'].sum()
            expenses = abs(month_df[month_df['amount'] < 0]['amount'].sum())
            
            income_trend.append(float(income))
            expense_trend.append(float(expenses))
        
        # Calculate growth rates
        income_growth = self._calculate_growth_rate(income_trend)
        expense_growth = self._calculate_growth_rate(expense_trend)
        
        return {
            'periods_analyzed': periods,
            'income_trend': income_trend,
            'expense_trend': expense_trend,
            'income_growth_rate': income_growth,
            'expense_growth_rate': expense_growth,
            'trend_insights': self._analyze_trends(income_trend, expense_trend),
            'projections': self._project_trends(income_trend, expense_trend, periods=3)
        }
    
    def generate_comprehensive_report(
        self,
        transactions_df: pd.DataFrame,
        period_start: datetime,
        period_end: datetime,
        budget_data: Optional[Dict] = None
    ) -> FinancialReport:
        """
        Generate comprehensive financial report
        """
        report_id = f"FR_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        # Generate all report components
        executive_summary = self.generate_executive_summary(
            transactions_df, period_start, period_end
        )
        
        cash_flow = self.generate_cash_flow_statement(
            transactions_df, period_start, period_end
        )
        
        profit_loss = self.generate_profit_loss_statement(
            transactions_df, period_start, period_end
        )
        
        variance_analysis = None
        if budget_data:
            variance_analysis = self.generate_variance_analysis(
                transactions_df, budget_data, period_start, period_end
            )
        
        trend_analysis = self.generate_trend_analysis(transactions_df)
        
        # Generate recommendations
        recommendations = self._generate_recommendations(
            executive_summary,
            variance_analysis,
            trend_analysis
        )
        
        # Generate charts data
        charts_data = self._prepare_charts_data(
            transactions_df,
            executive_summary,
            trend_analysis
        )
        
        report = FinancialReport(
            report_id=report_id,
            period_start=period_start,
            period_end=period_end,
            report_type='comprehensive',
            summary=executive_summary,
            detailed_analysis={
                'cash_flow_statement': cash_flow,
                'profit_loss_statement': profit_loss,
                'variance_analysis': variance_analysis,
                'trend_analysis': trend_analysis
            },
            recommendations=recommendations,
            charts_data=charts_data,
            metadata={
                'generated_at': datetime.now().isoformat(),
                'report_version': '2.0.0',
                'data_points': len(transactions_df)
            }
        )
        
        self.reports_generated.append(report)
        return report
    
    def _get_top_categories(self, period_df: pd.DataFrame, top_n: int = 5) -> List[Dict]:
        """Get top spending categories"""
        category_spending = period_df[period_df['amount'] < 0].groupby('category')['amount'].sum().abs()
        top_categories = category_spending.nlargest(top_n)
        
        return [
            {'category': cat, 'amount': float(amt)}
            for cat, amt in top_categories.items()
        ]
    
    def _generate_executive_insights(
        self,
        income: float,
        expenses: float,
        net_flow: float,
        growth: float
    ) -> List[str]:
        """Generate executive insights"""
        insights = []
        
        if net_flow > 0:
            insights.append(f"✅ Positive cash flow: ${net_flow:,.2f}")
        
        if growth > 10:
            insights.append(f"📈 Strong revenue growth: {growth:.1f}%")
        elif growth < 0:
            insights.append(f"📉 Revenue decline: {growth:.1f}%")
        
        profit_margin = (net_flow / income * 100) if income > 0 else 0
        if profit_margin > 20:
            insights.append(f"💰 Healthy profit margin: {profit_margin:.1f}%")
        
        return insights
    
    def _calculate_growth_rate(self, values: List[float]) -> float:
        """Calculate growth rate"""
        if len(values) < 2:
            return 0.0
        
        first = values[0]
        last = values[-1]
        
        if first == 0:
            return 0.0
        
        return ((last - first) / first) * 100
    
    def _analyze_trends(
        self,
        income_trend: List[float],
        expense_trend: List[float]
    ) -> List[str]:
        """Analyze trends and generate insights"""
        insights = []
        
        if income_trend and len(income_trend) > 1:
            if income_trend[-1] > income_trend[0]:
                insights.append("📈 Income showing upward trend")
            else:
                insights.append("📉 Income showing downward trend")
        
        if expense_trend and len(expense_trend) > 1:
            if expense_trend[-1] > expense_trend[0]:
                insights.append("⚠️ Expenses increasing")
        
        return insights
    
    def _project_trends(
        self,
        income_trend: List[float],
        expense_trend: List[float],
        periods: int = 3
    ) -> Dict:
        """Project future trends"""
        income_projection = []
        expense_projection = []
        
        # Simple linear projection
        if len(income_trend) > 1:
            income_slope = (income_trend[-1] - income_trend[0]) / len(income_trend)
            for i in range(periods):
                income_projection.append(income_trend[-1] + (income_slope * (i + 1)))
        
        if len(expense_trend) > 1:
            expense_slope = (expense_trend[-1] - expense_trend[0]) / len(expense_trend)
            for i in range(periods):
                expense_projection.append(expense_trend[-1] + (expense_slope * (i + 1)))
        
        return {
            'income_projection': income_projection,
            'expense_projection': expense_projection,
            'periods': periods
        }
    
    def _generate_recommendations(
        self,
        summary: Dict,
        variance: Optional[Dict],
        trends: Dict
    ) -> List[str]:
        """Generate recommendations based on report data"""
        recommendations = []
        
        # Check profitability
        if summary['financials']['net_cash_flow'] < 0:
            recommendations.append("⚠️ Action required: Operating at a loss. Review expenses and pricing.")
        
        # Check growth
        if summary['growth']['income_growth_rate'] < 0:
            recommendations.append("📉 Revenue declining. Focus on customer acquisition and retention.")
        
        # Check variances
        if variance and variance['summary']['over_budget_categories'] > 0:
            recommendations.append(f"💰 {variance['summary']['over_budget_categories']} categories over budget. Review spending.")
        
        return recommendations
    
    def _prepare_charts_data(
        self,
        transactions_df: pd.DataFrame,
        summary: Dict,
        trends: Dict
    ) -> Dict:
        """Prepare data for charts"""
        return {
            'income_trend': summary['financials']['total_income'],
            'expense_trend': summary['financials']['total_expenses'],
            'net_flow': summary['financials']['net_cash_flow'],
            'category_breakdown': summary['top_categories'],
            'monthly_data': trends.get('income_trend', []),
            'expense_monthly_data': trends.get('expense_trend', [])
        }


# Example usage
if __name__ == "__main__":
    print("=" * 60)
    print("📊 Advanced Financial Reporting System v2.0.0")
    print("=" * 60)
    
    # Create reporting system
    reporting = AdvancedFinancialReporting()
    
    # Create sample data
    dates = pd.date_range(start='2024-01-01', end='2024-12-31', freq='D')
    
    np.random.seed(42)
    transactions_data = []
    
    categories = ['Food & Dining', 'Transportation', 'Shopping', 'Entertainment', 'Salary']
    
    for date in dates:
        if np.random.random() < 0.3:
            category = np.random.choice(categories)
            amount = np.random.choice([1, -1]) * np.random.uniform(10, 500)
            transactions_data.append({
                'date': date,
                'amount': amount,
                'category': category
            })
    
    transactions_df = pd.DataFrame(transactions_data)
    
    # Generate report
    period_start = datetime(2024, 1, 1)
    period_end = datetime(2024, 12, 31)
    
    budgets = {
        'Food & Dining': 500,
        'Transportation': 200,
        'Shopping': 250
    }
    
    print("\n📝 Generating comprehensive report...")
    report = reporting.generate_comprehensive_report(
        transactions_df,
        period_start,
        period_end,
        budgets
    )
    
    print(f"\n✅ Report Generated: {report.report_id}")
    print(f"\n📊 Summary:")
    print(f"   Total Income: ${report.summary['financials']['total_income']:,.2f}")
    print(f"   Total Expenses: ${report.summary['financials']['total_expenses']:,.2f}")
    print(f"   Net Cash Flow: ${report.summary['financials']['net_cash_flow']:,.2f}")
    print(f"   Income Growth: {report.summary['growth']['income_growth_rate']:+.1f}%")
    
    print(f"\n💡 Recommendations ({len(report.recommendations)}):")
    for i, rec in enumerate(report.recommendations, 1):
        print(f"   {i}. {rec}")
    
    # Save report
    with open('financial_report.json', 'w') as f:
        json.dump(report.to_dict(), f, indent=2, default=str)
    
    print("\n✅ Report saved to: financial_report.json")
    print("✅ Advanced reporting complete!")



