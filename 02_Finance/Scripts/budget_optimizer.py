#!/usr/bin/env python3
"""
Budget Optimizer
AI-powered budget optimization and recommendations
Version: 2.0.0
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Optional
import json
from dataclasses import dataclass


@dataclass
class BudgetRecommendation:
    """Represents a budget optimization recommendation"""
    category: str
    current_budget: float
    recommended_budget: float
    adjustment: float
    adjustment_percentage: float
    reason: str
    potential_savings: float
    priority: str  # high, medium, low
    confidence: float
    
    def to_dict(self):
        return {
            'category': self.category,
            'current_budget': self.current_budget,
            'recommended_budget': self.recommended_budget,
            'adjustment': self.adjustment,
            'adjustment_percentage': self.adjustment_percentage,
            'reason': self.reason,
            'potential_savings': self.potential_savings,
            'priority': self.priority,
            'confidence': self.confidence
        }


class BudgetOptimizer:
    """
    AI-powered budget optimization system
    """
    
    def __init__(self):
        self.transactions = []
        self.budgets = {}
        self.optimization_history = []
    
    def analyze_budget_performance(self, transactions_df: pd.DataFrame) -> Dict:
        """Analyze how well budgets are being utilized"""
        
        analysis = {}
        
        for category, budget_amount in self.budgets.items():
            category_transactions = transactions_df[transactions_df['category'] == category]
            
            if category_transactions.empty:
                continue
            
            spent = abs(category_transactions['amount'].sum())
            utilization_rate = (spent / budget_amount * 100) if budget_amount > 0 else 0
            
            # Analyze spending patterns
            avg_monthly_spending = spent / (category_transactions['date'].max() - category_transactions['date'].min()).days * 30
            
            analysis[category] = {
                'budget': budget_amount,
                'spent': spent,
                'remaining': budget_amount - spent,
                'utilization_rate': utilization_rate,
                'average_monthly_spending': avg_monthly_spending,
                'variance': abs(budget_amount - avg_monthly_spending),
                'efficiency': self.calculate_efficiency(category_transactions),
                'trend': self.analyze_trend(category_transactions)
            }
        
        return analysis
    
    def calculate_efficiency(self, category_df: pd.DataFrame) -> float:
        """Calculate spending efficiency (transactions per dollar)"""
        if category_df.empty or len(category_df) == 0:
            return 0.0
        
        total_spent = abs(category_df['amount'].sum())
        num_transactions = len(category_df)
        
        # Efficiency: transactions per $100 spent
        efficiency = (num_transactions / total_spent * 100) if total_spent > 0 else 0
        
        return efficiency
    
    def analyze_trend(self, category_df: pd.DataFrame) -> Dict:
        """Analyze spending trend over time"""
        if category_df.empty or len(category_df) < 2:
            return {'direction': 'stable', 'strength': 0.0}
        
        # Group by month
        category_df['year_month'] = pd.to_datetime(category_df['date']).dt.to_period('M')
        monthly_spending = category_df.groupby('year_month')['amount'].sum().abs()
        
        if len(monthly_spending) < 2:
            return {'direction': 'stable', 'strength': 0.0}
        
        # Calculate trend using linear regression
        x = np.arange(len(monthly_spending))
        y = monthly_spending.values
        
        if len(y) > 1:
            slope = np.polyfit(x, y, 1)[0]
            
            direction = 'increasing' if slope > 0 else 'decreasing' if slope < 0 else 'stable'
            strength = abs(slope) / np.std(y) if np.std(y) > 0 else 0
        else:
            direction = 'stable'
            strength = 0.0
        
        return {
            'direction': direction,
            'strength': float(strength),
            'slope': float(slope) if 'slope' in locals() else 0.0
        }
    
    def optimize_budgets(
        self,
        transactions_df: pd.DataFrame,
        target_total: Optional[float] = None
    ) -> List[BudgetRecommendation]:
        """
        Generate budget optimization recommendations
        """
        recommendations = []
        
        # Analyze current performance
        performance = self.analyze_budget_performance(transactions_df)
        
        for category, data in performance.items():
            # Identify optimization opportunities
            if data['utilization_rate'] < 20:
                # Underutilized budget
                recommendation = BudgetRecommendation(
                    category=category,
                    current_budget=data['budget'],
                    recommended_budget=data['budget'] * 0.8,  # Reduce by 20%
                    adjustment=-data['budget'] * 0.2,
                    adjustment_percentage=-20.0,
                    reason=f"Underutilized (only {data['utilization_rate']:.1f}% used)",
                    potential_savings=data['budget'] * 0.2,
                    priority='medium',
                    confidence=0.85
                )
                recommendations.append(recommendation)
            
            elif data['utilization_rate'] > 90:
                # Overutilized budget
                avg_spending = data['average_monthly_spending']
                
                if avg_spending > data['budget']:
                    # Consistently over budget
                    recommended_increase = avg_spending * 1.1  # 10% buffer
                    
                    recommendation = BudgetRecommendation(
                        category=category,
                        current_budget=data['budget'],
                        recommended_budget=recommended_increase,
                        adjustment=recommended_increase - data['budget'],
                        adjustment_percentage=((recommended_increase - data['budget']) / data['budget'] * 100),
                        reason=f"Consistently over budget (avg: ${avg_spending:.2f}/month)",
                        potential_savings=0,  # Actually an increase needed
                        priority='high',
                        confidence=0.90
                    )
                    recommendations.append(recommendation)
            
            # Efficiency optimization
            if data['efficiency'] > 5:  # Many small transactions
                # Opportunity to consolidate
                recommendation = BudgetRecommendation(
                    category=category,
                    current_budget=data['budget'],
                    recommended_budget=data['budget'] * 0.95,  # Reduce by 5%
                    adjustment=-data['budget'] * 0.05,
                    adjustment_percentage=-5.0,
                    reason=f"High transaction count ({data['efficiency']:.1f} tx per $100)",
                    potential_savings=data['budget'] * 0.05,
                    priority='low',
                    confidence=0.70
                )
                recommendations.append(recommendation)
        
        # If target total specified, normalize budgets
        if target_total and recommendations:
            current_total = sum(data['budget'] for data in performance.values())
            scale_factor = target_total / current_total
            
            for rec in recommendations:
                rec.recommended_budget *= scale_factor
                rec.adjustment *= scale_factor
        
        # Sort by priority and potential savings
        recommendations.sort(
            key=lambda x: (
                {'high': 3, 'medium': 2, 'low': 1}[x.priority],
                x.potential_savings
            ),
            reverse=True
        )
        
        return recommendations
    
    def suggest_budget_allocation(
        self,
        total_budget: float,
        historical_spending: Dict[str, float],
        strategic_priorities: Optional[Dict[str, float]] = None
    ) -> Dict[str, float]:
        """
        Suggest optimal budget allocation using historical data and priorities
        """
        total_historical = sum(historical_spending.values())
        
        if total_historical == 0:
            # Equal distribution if no historical data
            num_categories = len(historical_spending)
            return {cat: total_budget / num_categories for cat in historical_spending.keys()}
        
        # Base allocation on historical spending
        allocation = {}
        for category, spent in historical_spending.items():
            # Proportional allocation based on historical spending
            proportion = spent / total_historical
            
            # Apply strategic priority if provided
            if strategic_priorities and category in strategic_priorities:
                priority_factor = strategic_priorities[category]
                proportion *= priority_factor
            
            allocation[category] = total_budget * proportion
        
        # Normalize to ensure total equals target
        actual_total = sum(allocation.values())
        scale_factor = total_budget / actual_total if actual_total > 0 else 1.0
        
        allocation = {cat: amount * scale_factor for cat, amount in allocation.items()}
        
        return allocation
    
    def analyze_variance(self, transactions_df: pd.DataFrame) -> Dict:
        """Analyze budget variances"""
        variances = {}
        
        for category in self.budgets.keys():
            category_df = transactions_df[transactions_df['category'] == category]
            
            if category_df.empty:
                continue
            
            budget = self.budgets[category]
            spent = abs(category_df['amount'].sum())
            
            variance = spent - budget
            variance_percentage = (variance / budget * 100) if budget > 0 else 0
            
            variances[category] = {
                'budget': budget,
                'spent': spent,
                'variance': variance,
                'variance_percentage': variance_percentage,
                'status': 'over' if variance > 0 else 'under' if variance < 0 else 'met'
            }
        
        return variances
    
    def generate_budget_report(self, transactions_df: pd.DataFrame) -> Dict:
        """Generate comprehensive budget report"""
        performance = self.analyze_budget_performance(transactions_df)
        variances = self.analyze_variance(transactions_df)
        recommendations = self.optimize_budgets(transactions_df)
        
        total_budget = sum(data['budget'] for data in performance.values())
        total_spent = sum(data['spent'] for data in performance.values())
        total_savings = sum(rec.potential_savings for rec in recommendations if rec.potential_savings > 0)
        
        return {
            'timestamp': datetime.now().isoformat(),
            'summary': {
                'total_budget': total_budget,
                'total_spent': total_spent,
                'total_remaining': total_budget - total_spent,
                'utilization_rate': (total_spent / total_budget * 100) if total_budget > 0 else 0,
                'potential_savings': total_savings,
                'num_categories': len(performance)
            },
            'performance': performance,
            'variances': variances,
            'recommendations': [rec.to_dict() for rec in recommendations],
            'optimized_allocation': self._calculate_optimized_allocation(recommendations)
        }
    
    def _calculate_optimized_allocation(self, recommendations: List[BudgetRecommendation]) -> Dict:
        """Calculate optimized budget allocation"""
        optimized = {}
        
        for rec in recommendations:
            optimized[rec.category] = rec.recommended_budget
        
        return optimized


# Example usage
if __name__ == "__main__":
    print("=" * 60)
    print("💰 Budget Optimizer v2.0.0")
    print("=" * 60)
    
    # Create optimizer
    optimizer = BudgetOptimizer()
    
    # Set budgets
    budgets = {
        'Food & Dining': 500.0,
        'Transportation': 200.0,
        'Bills & Utilities': 300.0,
        'Shopping': 250.0,
        'Entertainment': 150.0
    }
    
    for category, amount in budgets.items():
        optimizer.budgets[category] = amount
    
    # Create sample transactions
    dates = pd.date_range(start='2024-01-01', end='2024-12-31', freq='D')
    
    np.random.seed(42)
    transactions_data = []
    
    for date in dates:
        if np.random.random() < 0.3:
            category = np.random.choice(list(budgets.keys()))
            amount = -np.random.uniform(10, budgets[category] / 30)
            transactions_data.append({
                'date': date,
                'amount': amount,
                'category': category
            })
    
    transactions_df = pd.DataFrame(transactions_data)
    
    # Analyze
    print("\n📊 Generating budget report...\n")
    report = optimizer.generate_budget_report(transactions_df)
    
    print("📈 Summary:")
    print(f"  Total Budget: ${report['summary']['total_budget']:,.2f}")
    print(f"  Total Spent: ${report['summary']['total_spent']:,.2f}")
    print(f"  Utilization: {report['summary']['utilization_rate']:.1f}%")
    print(f"  Potential Savings: ${report['summary']['potential_savings']:,.2f}")
    
    print(f"\n🎯 Top Recommendations ({len(report['recommendations'])}):")
    for i, rec in enumerate(report['recommendations'][:5], 1):
        print(f"  {i}. [{rec['priority'].upper()}] {rec['category']}")
        print(f"     {rec['reason']}")
        print(f"     Adjustment: {rec['adjustment_percentage']:+.1f}%")
        if rec['potential_savings'] > 0:
            print(f"     Potential savings: ${rec['potential_savings']:.2f}")
    
    print("\n✅ Budget optimization complete!")
    
    # Save report
    with open('budget_optimization_report.json', 'w') as f:
        json.dump(report, f, indent=2, default=str)
    
    print("\nReport saved to: budget_optimization_report.json")
