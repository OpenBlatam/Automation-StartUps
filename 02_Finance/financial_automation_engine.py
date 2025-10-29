#!/usr/bin/env python3
"""
Financial Automation Engine
Advanced AI-powered financial automation system
Version: 2.0.0
Author: Financial AI Team
"""

import json
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
import logging
from dataclasses import dataclass, asdict
import warnings
warnings.filterwarnings('ignore')

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


@dataclass
class Transaction:
    """Represents a financial transaction"""
    id: str
    date: datetime
    amount: float
    category: str
    description: str
    account: str
    type: str  # 'income' or 'expense'
    
    def to_dict(self):
        return asdict(self)


@dataclass
class Budget:
    """Represents a budget allocation"""
    category: str
    allocated: float
    spent: float = 0.0
    remaining: float = None
    
    def __post_init__(self):
        if self.remaining is None:
            self.remaining = self.allocated - self.spent
    
    def utilization_rate(self) -> float:
        """Calculate budget utilization rate"""
        if self.allocated == 0:
            return 0.0
        return (self.spent / self.allocated) * 100


class FinancialAutomationEngine:
    """
    Core engine for financial automation
    """
    
    def __init__(self):
        self.transactions = []
        self.budgets = {}
        self.forecasts = {}
        self.alerts = []
        
    def add_transaction(self, transaction: Transaction) -> bool:
        """Add a new transaction"""
        try:
            self.transactions.append(transaction)
            logger.info(f"Added transaction: {transaction.id}")
            
            # Update budget
            if transaction.category in self.budgets:
                self.budgets[transaction.category].spent += abs(transaction.amount)
                self.budgets[transaction.category].remaining = (
                    self.budgets[transaction.category].allocated -
                    self.budgets[transaction.category].spent
                )
            
            # Check alerts
            self._check_alerts(transaction)
            return True
        except Exception as e:
            logger.error(f"Error adding transaction: {e}")
            return False
    
    def auto_categorize(self, description: str) -> str:
        """
        Automatic transaction categorization using AI/ML
        """
        description_lower = description.lower()
        
        # Category patterns (in real implementation, this would use NLP/ML)
        patterns = {
            'Food & Dining': ['restaurant', 'cafe', 'food', 'lunch', 'dinner', 'starbucks'],
            'Transportation': ['uber', 'lyft', 'gas', 'parking', 'metro', 'bus'],
            'Shopping': ['amazon', 'target', 'walmart', 'store', 'shop'],
            'Entertainment': ['netflix', 'spotify', 'theater', 'movie', 'concert'],
            'Bills & Utilities': ['electric', 'water', 'gas', 'internet', 'phone'],
            'Healthcare': ['pharmacy', 'doctor', 'hospital', 'medical'],
            'Salary': ['salary', 'payroll', 'income'],
            'Investment': ['dividend', 'stock', 'investment'],
        }
        
        for category, keywords in patterns.items():
            if any(keyword in description_lower for keyword in keywords):
                return category
        
        return 'Other'
    
    def set_budget(self, category: str, amount: float):
        """Set budget for a category"""
        if category not in self.budgets:
            self.budgets[category] = Budget(
                category=category,
                allocated=amount,
                spent=0.0
            )
        else:
            self.budgets[category].allocated = amount
            self.budgets[category].remaining = amount - self.budgets[category].spent
        
        logger.info(f"Budget set for {category}: ${amount}")
    
    def get_budget_status(self, category: str) -> Optional[Dict]:
        """Get budget status for a category"""
        if category not in self.budgets:
            return None
        
        budget = self.budgets[category]
        utilization = budget.utilization_rate()
        
        status = 'green'
        if utilization > 90:
            status = 'red'
        elif utilization > 75:
            status = 'yellow'
        
        return {
            'category': category,
            'allocated': budget.allocated,
            'spent': budget.spent,
            'remaining': budget.remaining,
            'utilization_rate': utilization,
            'status': status
        }
    
    def forecast_cash_flow(self, days: int = 30) -> Dict:
        """
        Forecast cash flow using historical data
        """
        if not self.transactions:
            return {'forecast': [], 'confidence': 0}
        
        # Convert transactions to DataFrame
        df = self._transactions_to_dataframe()
        
        # Simple moving average forecast (in production, use LSTM/Prophet)
        if len(df) > 0:
            avg_daily = df.groupby('date')['amount'].sum().mean()
            forecast_value = avg_daily * days
            
            confidence = min(0.85, len(df) / 100)
        else:
            forecast_value = 0
            confidence = 0
        
        return {
            'forecast': forecast_value,
            'period_days': days,
            'confidence': confidence,
            'date': datetime.now().strftime('%Y-%m-%d')
        }
    
    def detect_anomalies(self, threshold: float = 2.0) -> List[Dict]:
        """
        Detect anomalous transactions
        """
        if len(self.transactions) < 10:
            return []
        
        df = self._transactions_to_dataframe()
        
        # Calculate statistics
        mean = df['amount'].mean()
        std = df['amount'].std()
        
        anomalies = []
        for _, transaction in df.iterrows():
            z_score = abs((transaction['amount'] - mean) / std) if std > 0 else 0
            
            if z_score > threshold:
                anomalies.append({
                    'transaction_id': transaction.get('id', 'unknown'),
                    'date': str(transaction.get('date', '')),
                    'amount': transaction['amount'],
                    'category': transaction.get('category', 'unknown'),
                    'z_score': z_score,
                    'severity': 'high' if z_score > 3 else 'medium'
                })
        
        return anomalies
    
    def generate_report(self) -> Dict:
        """
        Generate comprehensive financial report
        """
        if not self.transactions:
            return {'error': 'No transactions available'}
        
        df = self._transactions_to_dataframe()
        
        report = {
            'summary': {
                'total_income': float(df[df['type'] == 'income']['amount'].sum()),
                'total_expenses': float(abs(df[df['type'] == 'expense']['amount'].sum())),
                'net_cash_flow': float(df['amount'].sum()),
                'transaction_count': len(df)
            },
            'by_category': self._summarize_by_category(df),
            'by_month': self._summarize_by_month(df),
            'budgets': self._summarize_budgets(),
            'alerts': self.alerts,
            'forecast': self.forecast_cash_flow(30),
            'anomalies': self.detect_anomalies()
        }
        
        return report
    
    def _check_alerts(self, transaction: Transaction):
        """Check and generate alerts"""
        # Check budget alerts
        if transaction.category in self.budgets:
            budget = self.budgets[transaction.category]
            if budget.utilization_rate() > 90:
                self.alerts.append({
                    'type': 'budget_alert',
                    'severity': 'high',
                    'message': f"{budget.category} budget exceeded 90%",
                    'date': datetime.now().isoformat()
                })
        
        # Check large transaction alerts
        if abs(transaction.amount) > 1000:
            self.alerts.append({
                'type': 'large_transaction',
                'severity': 'medium',
                'message': f"Large transaction detected: ${transaction.amount}",
                'date': datetime.now().isoformat()
            })
    
    def _transactions_to_dataframe(self) -> pd.DataFrame:
        """Convert transactions to pandas DataFrame"""
        data = []
        for t in self.transactions:
            data.append({
                'id': t.id,
                'date': t.date,
                'amount': t.amount if t.type == 'income' else -abs(t.amount),
                'category': t.category,
                'description': t.description,
                'type': t.type
            })
        
        df = pd.DataFrame(data)
        if not df.empty:
            df['date'] = pd.to_datetime(df['date'])
        return df
    
    def _summarize_by_category(self, df: pd.DataFrame) -> Dict:
        """Summarize transactions by category"""
        return df.groupby('category')['amount'].sum().to_dict()
    
    def _summarize_by_month(self, df: pd.DataFrame) -> Dict:
        """Summarize transactions by month"""
        df['year_month'] = df['date'].dt.to_period('M')
        return df.groupby('year_month')['amount'].sum().to_dict()
    
    def _summarize_budgets(self) -> List[Dict]:
        """Summarize all budgets"""
        return [asdict(budget) for budget in self.budgets.values()]
    
    def export_data(self, filename: str):
        """Export data to JSON"""
        data = {
            'transactions': [t.to_dict() for t in self.transactions],
            'budgets': self._summarize_budgets(),
            'report': self.generate_report()
        }
        
        with open(filename, 'w') as f:
            json.dump(data, f, default=str, indent=2)
        
        logger.info(f"Data exported to {filename}")


# Example usage
if __name__ == "__main__":
    print("=" * 60)
    print("Financial Automation Engine v2.0.0")
    print("=" * 60)
    
    # Create engine
    engine = FinancialAutomationEngine()
    
    # Set budgets
    engine.set_budget('Food & Dining', 500.0)
    engine.set_budget('Transportation', 200.0)
    engine.set_budget('Bills & Utilities', 300.0)
    
    # Add sample transactions
    transactions = [
        Transaction(
            id='001',
            date=datetime.now() - timedelta(days=5),
            amount=50.0,
            category='Food & Dining',
            description='Restaurant lunch',
            account='Credit Card',
            type='expense'
        ),
        Transaction(
            id='002',
            date=datetime.now() - timedelta(days=3),
            amount=25.0,
            category='Transportation',
            description='Uber ride',
            account='Credit Card',
            type='expense'
        ),
        Transaction(
            id='003',
            date=datetime.now() - timedelta(days=1),
            amount=5000.0,
            category='Salary',
            description='Monthly salary',
            account='Bank Account',
            type='income'
        ),
        Transaction(
            id='004',
            date=datetime.now(),
            amount=450.0,
            category='Food & Dining',
            description='Grocery shopping',
            account='Credit Card',
            type='expense'
        ),
    ]
    
    for transaction in transactions:
        engine.add_transaction(transaction)
    
    # Generate report
    print("\n" + "=" * 60)
    print("FINANCIAL REPORT")
    print("=" * 60)
    
    report = engine.generate_report()
    print(json.dumps(report, indent=2, default=str))
    
    # Export data
    engine.export_data('financial_data.json')
    
    print("\n✅ Financial Automation Engine Demo Complete!")
    print("\nReport saved to: financial_data.json")



