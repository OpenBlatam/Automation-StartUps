#!/usr/bin/env python3
"""
Advanced Fraud Detection System
AI-powered financial fraud detection
Version: 2.0.0
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Optional
import json
import logging
from dataclasses import dataclass

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class FraudAlert:
    """Represents a fraud detection alert"""
    transaction_id: str
    date: datetime
    amount: float
    category: str
    risk_score: float
    fraud_type: str
    indicators: List[str]
    severity: str  # low, medium, high, critical
    recommendation: str
    confidence: float
    
    def to_dict(self):
        return {
            'transaction_id': self.transaction_id,
            'date': self.date.isoformat(),
            'amount': self.amount,
            'category': self.category,
            'risk_score': self.risk_score,
            'fraud_type': self.fraud_type,
            'indicators': self.indicators,
            'severity': self.severity,
            'recommendation': self.recommendation,
            'confidence': self.confidence
        }


class FraudDetectionSystem:
    """
    Advanced fraud detection using multiple ML techniques
    """
    
    def __init__(self):
        self.transaction_history = []
        self.alerts = []
        self.fraud_patterns = self._initialize_patterns()
        self.statistics = {
            'total_checked': 0,
            'fraud_detected': 0,
            'false_positives': 0,
            'false_negatives': 0
        }
    
    def _initialize_patterns(self) -> Dict:
        """Initialize known fraud patterns"""
        return {
            'velocity_check': {
                'max_transactions': 10,
                'time_window_hours': 1
            },
            'amount_anomaly': {
                'z_score_threshold': 3.0
            },
            'pattern_anomaly': {
                'similarity_threshold': 0.3
            },
            'location_anomaly': {
                'max_distance_km': 100
            },
            'time_anomaly': {
                'suspicious_hours': [0, 1, 2, 3, 4]  # Midnight to 4am
            }
        }
    
    def detect_fraud(self, transaction: Dict, historical_data: List[Dict] = None) -> Optional[FraudAlert]:
        """
        Detect fraudulent transactions using multiple techniques
        """
        self.statistics['total_checked'] += 1
        
        # Combine all fraud detection methods
        indicators = []
        risk_factors = []
        
        # 1. Velocity Check
        velocity_score = self.check_velocity(transaction, historical_data or [])
        if velocity_score > 0.7:
            indicators.append('velocity_anomaly')
            risk_factors.append(('high_velocity', velocity_score))
        
        # 2. Amount Anomaly
        amount_score = self.check_amount_anomaly(transaction, historical_data or [])
        if amount_score > 0.7:
            indicators.append('unusual_amount')
            risk_factors.append(('amount_anomaly', amount_score))
        
        # 3. Pattern Anomaly
        pattern_score = self.check_pattern_anomaly(transaction, historical_data or [])
        if pattern_score > 0.7:
            indicators.append('unusual_pattern')
            risk_factors.append(('pattern_anomaly', pattern_score))
        
        # 4. Time Anomaly
        time_score = self.check_time_anomaly(transaction)
        if time_score > 0.7:
            indicators.append('unusual_time')
            risk_factors.append(('time_anomaly', time_score))
        
        # 5. Category Anomaly
        category_score = self.check_category_anomaly(transaction, historical_data or [])
        if category_score > 0.7:
            indicators.append('unusual_category')
            risk_factors.append(('category_anomaly', category_score))
        
        # Calculate overall risk score
        if risk_factors:
            overall_score = sum(factor[1] for factor in risk_factors) / len(risk_factors)
        else:
            overall_score = 0.0
        
        # Generate alert if risk is high
        if overall_score > 0.7:
            alert = self.create_fraud_alert(transaction, indicators, overall_score)
            self.alerts.append(alert)
            self.statistics['fraud_detected'] += 1
            return alert
        
        return None
    
    def check_velocity(self, transaction: Dict, historical: List[Dict]) -> float:
        """
        Check transaction velocity (number of transactions in time window)
        """
        if not historical:
            return 0.0
        
        # Get recent transactions (last hour)
        recent_cutoff = transaction['date'] - timedelta(hours=1)
        recent_transactions = [
            t for t in historical 
            if t['date'] >= recent_cutoff and t.get('account_id') == transaction.get('account_id')
        ]
        
        velocity_score = min(1.0, len(recent_transactions) / self.fraud_patterns['velocity_check']['max_transactions'])
        
        return velocity_score
    
    def check_amount_anomaly(self, transaction: Dict, historical: List[Dict]) -> float:
        """
        Check if amount is anomalous using statistical methods
        """
        if not historical:
            return 0.0
        
        # Filter by account and category
        similar_transactions = [
            abs(t['amount']) for t in historical
            if t.get('account_id') == transaction.get('account_id') and
               t.get('category') == transaction.get('category')
        ]
        
        if not similar_transactions:
            return 0.0
        
        # Calculate z-score
        mean = np.mean(similar_transactions)
        std = np.std(similar_transactions)
        
        if std == 0:
            return 0.0
        
        z_score = abs(abs(transaction['amount']) - mean) / std
        
        # Normalize to 0-1 scale
        anomaly_score = min(1.0, z_score / self.fraud_patterns['amount_anomaly']['z_score_threshold'])
        
        return anomaly_score
    
    def check_pattern_anomaly(self, transaction: Dict, historical: List[Dict]) -> float:
        """
        Check if transaction pattern is anomalous
        """
        if not historical:
            return 0.0
        
        # Build typical pattern for this account
        account_transactions = [
            t for t in historical
            if t.get('account_id') == transaction.get('account_id')
        ][-30:]  # Last 30 transactions
        
        if len(account_transactions) < 5:
            return 0.0
        
        # Analyze patterns
        typical_categories = {}
        typical_times = {}
        
        for t in account_transactions:
            cat = t.get('category', 'unknown')
            typical_categories[cat] = typical_categories.get(cat, 0) + 1
            
            hour = t['date'].hour
            typical_times[hour] = typical_times.get(hour, 0) + 1
        
        # Check if current transaction deviates
        current_cat = transaction.get('category', 'unknown')
        current_hour = transaction['date'].hour
        
        category_deviation = 1.0 - (typical_categories.get(current_cat, 0) / len(account_transactions))
        time_deviation = 1.0 - (typical_times.get(current_hour, 0) / len(account_transactions))
        
        # Combined deviation score
        deviation_score = (category_deviation + time_deviation) / 2
        
        return deviation_score if deviation_score > 0.5 else 0.0
    
    def check_time_anomaly(self, transaction: Dict) -> float:
        """
        Check if transaction time is suspicious
        """
        hour = transaction['date'].hour
        
        if hour in self.fraud_patterns['time_anomaly']['suspicious_hours']:
            return 0.8  # Higher score for suspicious hours
        
        # Check if transaction is outside business hours
        if hour < 6 or hour > 23:
            return 0.5
        
        return 0.0
    
    def check_category_anomaly(self, transaction: Dict, historical: List[Dict]) -> float:
        """
        Check if category is unusual for this account
        """
        if not historical:
            return 0.0
        
        # Get category distribution for this account
        account_transactions = [
            t for t in historical
            if t.get('account_id') == transaction.get('account_id')
        ][-50:]  # Last 50 transactions
        
        if len(account_transactions) < 10:
            return 0.0
        
        category_counts = {}
        for t in account_transactions:
            cat = t.get('category', 'unknown')
            category_counts[cat] = category_counts.get(cat, 0) + 1
        
        total = len(account_transactions)
        current_cat = transaction.get('category', 'unknown')
        cat_frequency = category_counts.get(current_cat, 0) / total
        
        # Low frequency = high anomaly score
        anomaly_score = 1.0 - cat_frequency
        
        return anomaly_score if anomaly_score > 0.7 else 0.0
    
    def create_fraud_alert(
        self,
        transaction: Dict,
        indicators: List[str],
        risk_score: float
    ) -> FraudAlert:
        """Create fraud alert from detected indicators"""
        
        # Determine fraud type
        if 'velocity_anomaly' in indicators:
            fraud_type = 'Velocity Fraud'
        elif 'unusual_amount' in indicators:
            fraud_type = 'Amount Anomaly'
        elif 'pattern_anomaly' in indicators:
            fraud_type = 'Pattern Anomaly'
        elif 'unusual_time' in indicators:
            fraud_type = 'Time Anomaly'
        else:
            fraud_type = 'Suspicious Activity'
        
        # Determine severity
        if risk_score >= 0.9:
            severity = 'critical'
            recommendation = 'Block transaction immediately and contact cardholder'
        elif risk_score >= 0.8:
            severity = 'high'
            recommendation = 'Flag for manual review and contact cardholder'
        elif risk_score >= 0.7:
            severity = 'medium'
            recommendation = 'Flag for review and monitor account'
        else:
            severity = 'low'
            recommendation = 'Monitor for additional suspicious activity'
        
        # Calculate confidence
        confidence = min(0.95, risk_score + (len(indicators) * 0.05))
        
        return FraudAlert(
            transaction_id=transaction.get('id', 'unknown'),
            date=transaction['date'],
            amount=abs(transaction['amount']),
            category=transaction.get('category', 'unknown'),
            risk_score=risk_score,
            fraud_type=fraud_type,
            indicators=indicators,
            severity=severity,
            recommendation=recommendation,
            confidence=confidence
        )
    
    def batch_detect(self, transactions: List[Dict]) -> List[FraudAlert]:
        """Detect fraud in batch of transactions"""
        alerts = []
        
        for transaction in transactions:
            alert = self.detect_fraud(transaction, transactions)
            if alert:
                alerts.append(alert)
        
        return alerts
    
    def get_statistics(self) -> Dict:
        """Get fraud detection statistics"""
        total = self.statistics['total_checked']
        detected = self.statistics['fraud_detected']
        
        return {
            'total_transactions': total,
            'fraud_detected': detected,
            'detection_rate': (detected / total * 100) if total > 0 else 0,
            'alerts_by_severity': self._count_alerts_by_severity(),
            'alerts_by_type': self._count_alerts_by_type()
        }
    
    def _count_alerts_by_severity(self) -> Dict:
        """Count alerts by severity"""
        counts = {'critical': 0, 'high': 0, 'medium': 0, 'low': 0}
        for alert in self.alerts:
            counts[alert.severity] += 1
        return counts
    
    def _count_alerts_by_type(self) -> Dict:
        """Count alerts by fraud type"""
        counts = {}
        for alert in self.alerts:
            counts[alert.fraud_type] = counts.get(alert.fraud_type, 0) + 1
        return counts
    
    def generate_report(self) -> Dict:
        """Generate comprehensive fraud detection report"""
        return {
            'timestamp': datetime.now().isoformat(),
            'statistics': self.get_statistics(),
            'recent_alerts': [alert.to_dict() for alert in self.alerts[-10:]],
            'recommendations': self.generate_recommendations()
        }
    
    def generate_recommendations(self) -> List[str]:
        """Generate recommendations based on detected fraud"""
        recommendations = []
        
        stats = self.get_statistics()
        
        if stats['fraud_detected'] > 10:
            recommendations.append("High fraud rate detected. Consider enhancing security measures.")
        
        if stats['alerts_by_severity']['critical'] > 5:
            recommendations.append("Multiple critical alerts. Immediate review required.")
        
        detection_rate = stats['detection_rate']
        if detection_rate < 1:
            recommendations.append("Low fraud detection rate. Consider adjusting thresholds.")
        elif detection_rate > 10:
            recommendations.append("High fraud detection rate. Review false positive rate.")
        
        return recommendations


# Example usage
if __name__ == "__main__":
    print("=" * 60)
    print("🔍 Fraud Detection System v2.0.0")
    print("=" * 60)
    
    # Create system
    fraud_system = FraudDetectionSystem()
    
    # Create sample transactions
    sample_transactions = [
        {
            'id': '001',
            'date': datetime.now() - timedelta(hours=1),
            'amount': -50.0,
            'category': 'Food & Dining',
            'account_id': 'ACC001',
            'description': 'Normal transaction'
        },
        {
            'id': '002',
            'date': datetime.now() - timedelta(minutes=10),
            'amount': -5000.0,
            'category': 'Electronics',
            'account_id': 'ACC001',
            'description': 'Large purchase'
        },
        {
            'id': '003',
            'date': datetime.now() - timedelta(minutes=5),
            'amount': -3000.0,
            'category': 'Electronics',
            'account_id': 'ACC001',
            'description': 'Another large purchase'
        },
        {
            'id': '004',
            'date': datetime.now(),
            'amount': -2000.0,
            'category': 'Electronics',
            'account_id': 'ACC001',
            'description': 'Third large purchase'  # This should trigger velocity alert
        }
    ]
    
    # Detect fraud
    print("\n🔍 Detecting fraud in sample transactions...\n")
    alerts = fraud_system.batch_detect(sample_transactions)
    
    for alert in alerts:
        print(f"⚠️  ALERT: {alert.severity.upper()}")
        print(f"   Transaction: {alert.transaction_id}")
        print(f"   Amount: ${alert.amount:.2f}")
        print(f"   Type: {alert.fraud_type}")
        print(f"   Risk Score: {alert.risk_score:.2f}")
        print(f"   Indicators: {', '.join(alert.indicators)}")
        print(f"   Recommendation: {alert.recommendation}")
        print()
    
    # Generate report
    report = fraud_system.generate_report()
    print("📊 Statistics:")
    print(json.dumps(report['statistics'], indent=2))
    
    print("\n✅ Fraud detection complete!")
    print(f"   Detected: {len(alerts)} fraudulent transactions")
    print(f"   Detection Rate: {report['statistics']['detection_rate']:.2f}%")



