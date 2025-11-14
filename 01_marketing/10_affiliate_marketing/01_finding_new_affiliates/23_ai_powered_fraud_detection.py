#!/usr/bin/env python3
"""
AI-Powered Fraud Detection System for Affiliate Marketing
========================================================

This module provides advanced fraud detection capabilities for affiliate marketing,
including click fraud detection, conversion fraud prevention, and behavioral analysis.

Author: AI Marketing System
Version: 2.0
"""

import pandas as pd
import numpy as np
import json
from typing import Dict, List, Optional, Tuple, Any
from datetime import datetime, timedelta
import asyncio
import aiohttp
from dataclasses import dataclass, asdict
from enum import Enum
import logging
from sklearn.ensemble import IsolationForest, RandomForestClassifier
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, confusion_matrix
from sklearn.cluster import DBSCAN
import requests
import hashlib
import ipaddress
import re
import warnings
warnings.filterwarnings('ignore')

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class FraudType(Enum):
    """Types of fraud"""
    CLICK_FRAUD = "click_fraud"
    CONVERSION_FRAUD = "conversion_fraud"
    AFFILIATE_FRAUD = "affiliate_fraud"
    BOT_TRAFFIC = "bot_traffic"
    INFLATED_METRICS = "inflated_metrics"
    PAYMENT_FRAUD = "payment_fraud"

class RiskLevel(Enum):
    """Risk levels"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

@dataclass
class FraudAlert:
    """Fraud alert data structure"""
    alert_id: str
    fraud_type: FraudType
    risk_level: RiskLevel
    description: str
    evidence: Dict[str, Any]
    confidence_score: float
    affiliate_id: Optional[str]
    timestamp: datetime
    status: str  # pending, investigated, resolved, false_positive

@dataclass
class ClickData:
    """Click data structure"""
    click_id: str
    affiliate_id: str
    ip_address: str
    user_agent: str
    referrer: str
    timestamp: datetime
    country: str
    city: str
    device_type: str
    browser: str
    os: str

@dataclass
class ConversionData:
    """Conversion data structure"""
    conversion_id: str
    affiliate_id: str
    click_id: str
    amount: float
    timestamp: datetime
    ip_address: str
    user_agent: str
    payment_method: str
    customer_email: str

class AIPoweredFraudDetection:
    """
    AI-Powered Fraud Detection System for Affiliate Marketing
    """
    
    def __init__(self):
        self.click_data = []
        self.conversion_data = []
        self.fraud_alerts = []
        self.fraud_models = {}
        self.risk_rules = []
        self.blocked_ips = set()
        self.suspicious_affiliates = set()
        
        # Initialize fraud detection parameters
        self.fraud_params = {
            'click_fraud_threshold': 0.7,
            'conversion_fraud_threshold': 0.8,
            'bot_detection_threshold': 0.6,
            'max_clicks_per_hour': 100,
            'max_conversions_per_hour': 10,
            'min_conversion_time': 30,  # seconds
            'max_conversion_time': 86400  # 24 hours
        }
        
        # Initialize risk rules
        self._initialize_risk_rules()
        
        # Initialize fraud models
        self._initialize_fraud_models()
    
    def _initialize_risk_rules(self):
        """
        Initialize risk detection rules
        """
        self.risk_rules = [
            {
                'name': 'High Click Volume',
                'description': 'Affiliate generates unusually high click volume',
                'condition': lambda data: data['clicks_per_hour'] > self.fraud_params['max_clicks_per_hour'],
                'risk_level': RiskLevel.HIGH,
                'fraud_type': FraudType.CLICK_FRAUD
            },
            {
                'name': 'High Conversion Rate',
                'description': 'Affiliate has suspiciously high conversion rate',
                'condition': lambda data: data['conversion_rate'] > 0.5,
                'risk_level': RiskLevel.MEDIUM,
                'fraud_type': FraudType.CONVERSION_FRAUD
            },
            {
                'name': 'Bot Traffic',
                'description': 'Traffic appears to be from bots',
                'condition': lambda data: data['bot_score'] > self.fraud_params['bot_detection_threshold'],
                'risk_level': RiskLevel.HIGH,
                'fraud_type': FraudType.BOT_TRAFFIC
            },
            {
                'name': 'Suspicious IP',
                'description': 'IP address is known for fraudulent activity',
                'condition': lambda data: data['ip_risk_score'] > 0.8,
                'risk_level': RiskLevel.CRITICAL,
                'fraud_type': FraudType.CLICK_FRAUD
            },
            {
                'name': 'Rapid Conversions',
                'description': 'Conversions happen too quickly after clicks',
                'condition': lambda data: data['avg_conversion_time'] < self.fraud_params['min_conversion_time'],
                'risk_level': RiskLevel.MEDIUM,
                'fraud_type': FraudType.CONVERSION_FRAUD
            }
        ]
    
    def _initialize_fraud_models(self):
        """
        Initialize fraud detection models
        """
        # Click fraud detection model
        self.fraud_models['click_fraud'] = {
            'model': IsolationForest(contamination=0.1, random_state=42),
            'scaler': StandardScaler(),
            'features': ['clicks_per_hour', 'unique_ips', 'bot_score', 'ip_risk_score', 'user_agent_diversity']
        }
        
        # Conversion fraud detection model
        self.fraud_models['conversion_fraud'] = {
            'model': RandomForestClassifier(n_estimators=100, random_state=42),
            'scaler': StandardScaler(),
            'features': ['conversion_rate', 'avg_conversion_time', 'amount_variance', 'payment_risk_score']
        }
        
        # Bot detection model
        self.fraud_models['bot_detection'] = {
            'model': RandomForestClassifier(n_estimators=100, random_state=42),
            'scaler': StandardScaler(),
            'features': ['user_agent_length', 'javascript_enabled', 'cookie_enabled', 'screen_resolution', 'timezone_offset']
        }
    
    def add_click_data(self, click_data: ClickData):
        """
        Add click data for fraud analysis
        """
        self.click_data.append(click_data)
        
        # Check for immediate fraud indicators
        self._check_click_fraud(click_data)
        
        # Update fraud models if enough data
        if len(self.click_data) > 100:
            self._update_fraud_models()
    
    def add_conversion_data(self, conversion_data: ConversionData):
        """
        Add conversion data for fraud analysis
        """
        self.conversion_data.append(conversion_data)
        
        # Check for immediate fraud indicators
        self._check_conversion_fraud(conversion_data)
        
        # Update fraud models if enough data
        if len(self.conversion_data) > 50:
            self._update_fraud_models()
    
    def _check_click_fraud(self, click_data: ClickData):
        """
        Check for click fraud indicators
        """
        # Check if IP is blocked
        if click_data.ip_address in self.blocked_ips:
            self._create_fraud_alert(
                FraudType.CLICK_FRAUD,
                RiskLevel.CRITICAL,
                f"Click from blocked IP: {click_data.ip_address}",
                {'ip_address': click_data.ip_address, 'affiliate_id': click_data.affiliate_id},
                1.0,
                click_data.affiliate_id
            )
            return
        
        # Check for bot traffic
        bot_score = self._calculate_bot_score(click_data)
        if bot_score > self.fraud_params['bot_detection_threshold']:
            self._create_fraud_alert(
                FraudType.BOT_TRAFFIC,
                RiskLevel.HIGH,
                f"Bot traffic detected: {click_data.ip_address}",
                {'ip_address': click_data.ip_address, 'bot_score': bot_score, 'affiliate_id': click_data.affiliate_id},
                bot_score,
                click_data.affiliate_id
            )
        
        # Check for suspicious patterns
        self._check_suspicious_patterns(click_data)
    
    def _check_conversion_fraud(self, conversion_data: ConversionData):
        """
        Check for conversion fraud indicators
        """
        # Find corresponding click data
        click_data = next((c for c in self.click_data if c.click_id == conversion_data.click_id), None)
        if not click_data:
            return
        
        # Check conversion time
        conversion_time = (conversion_data.timestamp - click_data.timestamp).total_seconds()
        
        if conversion_time < self.fraud_params['min_conversion_time']:
            self._create_fraud_alert(
                FraudType.CONVERSION_FRAUD,
                RiskLevel.MEDIUM,
                f"Conversion too quick: {conversion_time}s",
                {'conversion_time': conversion_time, 'affiliate_id': conversion_data.affiliate_id},
                0.8,
                conversion_data.affiliate_id
            )
        
        # Check for suspicious payment patterns
        self._check_payment_fraud(conversion_data)
    
    def _calculate_bot_score(self, click_data: ClickData) -> float:
        """
        Calculate bot score for click data
        """
        score = 0.0
        
        # Check user agent patterns
        user_agent = click_data.user_agent.lower()
        
        # Common bot user agents
        bot_patterns = [
            'bot', 'crawler', 'spider', 'scraper', 'curl', 'wget',
            'python-requests', 'java', 'go-http-client'
        ]
        
        for pattern in bot_patterns:
            if pattern in user_agent:
                score += 0.3
        
        # Check for missing or suspicious user agent
        if not user_agent or len(user_agent) < 10:
            score += 0.4
        
        # Check for repetitive patterns
        if user_agent.count(' ') < 2:  # Simple user agents
            score += 0.2
        
        # Check IP reputation (simplified)
        ip_risk = self._check_ip_reputation(click_data.ip_address)
        score += ip_risk * 0.3
        
        return min(1.0, score)
    
    def _check_ip_reputation(self, ip_address: str) -> float:
        """
        Check IP reputation (simplified)
        """
        try:
            # Check if IP is in private range
            ip = ipaddress.ip_address(ip_address)
            if ip.is_private:
                return 0.8  # High risk for private IPs
            
            # Check if IP is in known VPN/proxy ranges (simplified)
            # In practice, use a proper IP reputation service
            if ip_address.startswith('10.') or ip_address.startswith('192.168.'):
                return 0.9
            
            return 0.1  # Low risk for public IPs
            
        except ValueError:
            return 0.5  # Medium risk for invalid IPs
    
    def _check_suspicious_patterns(self, click_data: ClickData):
        """
        Check for suspicious click patterns
        """
        # Check for rapid clicks from same IP
        recent_clicks = [c for c in self.click_data 
                        if c.ip_address == click_data.ip_address and 
                        (click_data.timestamp - c.timestamp).total_seconds() < 3600]  # Last hour
        
        if len(recent_clicks) > 50:  # More than 50 clicks per hour
            self._create_fraud_alert(
                FraudType.CLICK_FRAUD,
                RiskLevel.HIGH,
                f"High click volume from IP: {click_data.ip_address}",
                {'ip_address': click_data.ip_address, 'clicks_per_hour': len(recent_clicks)},
                0.9,
                click_data.affiliate_id
            )
        
        # Check for clicks from same affiliate with same IP
        affiliate_clicks = [c for c in self.click_data 
                           if c.affiliate_id == click_data.affiliate_id and 
                           c.ip_address == click_data.ip_address]
        
        if len(affiliate_clicks) > 20:  # Same affiliate, same IP
            self._create_fraud_alert(
                FraudType.AFFILIATE_FRAUD,
                RiskLevel.MEDIUM,
                f"Affiliate using same IP for multiple clicks: {click_data.affiliate_id}",
                {'affiliate_id': click_data.affiliate_id, 'ip_address': click_data.ip_address, 'clicks': len(affiliate_clicks)},
                0.7,
                click_data.affiliate_id
            )
    
    def _check_payment_fraud(self, conversion_data: ConversionData):
        """
        Check for payment fraud indicators
        """
        # Check for suspicious payment amounts
        if conversion_data.amount < 1.0 or conversion_data.amount > 10000:
            self._create_fraud_alert(
                FraudType.PAYMENT_FRAUD,
                RiskLevel.MEDIUM,
                f"Suspicious payment amount: ${conversion_data.amount}",
                {'amount': conversion_data.amount, 'affiliate_id': conversion_data.affiliate_id},
                0.6,
                conversion_data.affiliate_id
            )
        
        # Check for duplicate payments
        duplicate_payments = [c for c in self.conversion_data 
                            if c.customer_email == conversion_data.customer_email and 
                            c.amount == conversion_data.amount and
                            (conversion_data.timestamp - c.timestamp).total_seconds() < 3600]
        
        if len(duplicate_payments) > 1:
            self._create_fraud_alert(
                FraudType.PAYMENT_FRAUD,
                RiskLevel.HIGH,
                f"Duplicate payment detected: {conversion_data.customer_email}",
                {'customer_email': conversion_data.customer_email, 'duplicates': len(duplicate_payments)},
                0.8,
                conversion_data.affiliate_id
            )
    
    def _create_fraud_alert(self, fraud_type: FraudType, risk_level: RiskLevel, 
                           description: str, evidence: Dict, confidence: float, 
                           affiliate_id: str = None):
        """
        Create fraud alert
        """
        alert = FraudAlert(
            alert_id=f"alert_{len(self.fraud_alerts)}",
            fraud_type=fraud_type,
            risk_level=risk_level,
            description=description,
            evidence=evidence,
            confidence_score=confidence,
            affiliate_id=affiliate_id,
            timestamp=datetime.now(),
            status='pending'
        )
        
        self.fraud_alerts.append(alert)
        
        # Add affiliate to suspicious list if high risk
        if risk_level in [RiskLevel.HIGH, RiskLevel.CRITICAL] and affiliate_id:
            self.suspicious_affiliates.add(affiliate_id)
        
        logger.warning(f"Fraud alert created: {fraud_type.value} - {description}")
    
    def _update_fraud_models(self):
        """
        Update fraud detection models with new data
        """
        if len(self.click_data) < 100:
            return
        
        # Prepare click fraud data
        click_features = self._prepare_click_features()
        if len(click_features) > 0:
            self._train_click_fraud_model(click_features)
        
        # Prepare conversion fraud data
        conversion_features = self._prepare_conversion_features()
        if len(conversion_features) > 0:
            self._train_conversion_fraud_model(conversion_features)
    
    def _prepare_click_features(self) -> pd.DataFrame:
        """
        Prepare click features for model training
        """
        features = []
        
        for click in self.click_data:
            # Calculate features for this click
            recent_clicks = [c for c in self.click_data 
                           if c.ip_address == click.ip_address and 
                           (click.timestamp - c.timestamp).total_seconds() < 3600]
            
            unique_ips = len(set(c.ip_address for c in recent_clicks))
            user_agent_diversity = len(set(c.user_agent for c in recent_clicks))
            bot_score = self._calculate_bot_score(click)
            ip_risk_score = self._check_ip_reputation(click.ip_address)
            
            features.append({
                'clicks_per_hour': len(recent_clicks),
                'unique_ips': unique_ips,
                'bot_score': bot_score,
                'ip_risk_score': ip_risk_score,
                'user_agent_diversity': user_agent_diversity
            })
        
        return pd.DataFrame(features)
    
    def _prepare_conversion_features(self) -> pd.DataFrame:
        """
        Prepare conversion features for model training
        """
        features = []
        
        for conversion in self.conversion_data:
            # Find corresponding click
            click = next((c for c in self.click_data if c.click_id == conversion.click_id), None)
            if not click:
                continue
            
            # Calculate features
            conversion_time = (conversion.timestamp - click.timestamp).total_seconds()
            
            # Get affiliate's conversion history
            affiliate_conversions = [c for c in self.conversion_data 
                                   if c.affiliate_id == conversion.affiliate_id]
            
            conversion_rate = len(affiliate_conversions) / len([c for c in self.click_data 
                                                              if c.affiliate_id == conversion.affiliate_id])
            
            amounts = [c.amount for c in affiliate_conversions]
            amount_variance = np.var(amounts) if len(amounts) > 1 else 0
            
            payment_risk_score = self._calculate_payment_risk_score(conversion)
            
            features.append({
                'conversion_rate': conversion_rate,
                'avg_conversion_time': conversion_time,
                'amount_variance': amount_variance,
                'payment_risk_score': payment_risk_score
            })
        
        return pd.DataFrame(features)
    
    def _calculate_payment_risk_score(self, conversion: ConversionData) -> float:
        """
        Calculate payment risk score
        """
        score = 0.0
        
        # Check payment method
        if conversion.payment_method in ['crypto', 'wire_transfer']:
            score += 0.3
        
        # Check amount
        if conversion.amount > 5000:
            score += 0.2
        
        # Check email domain
        email_domain = conversion.customer_email.split('@')[-1]
        if email_domain in ['tempmail.com', '10minutemail.com']:
            score += 0.5
        
        return min(1.0, score)
    
    def _train_click_fraud_model(self, features: pd.DataFrame):
        """
        Train click fraud detection model
        """
        try:
            model_info = self.fraud_models['click_fraud']
            X = features[model_info['features']]
            
            # Scale features
            X_scaled = model_info['scaler'].fit_transform(X)
            
            # Train model
            model_info['model'].fit(X_scaled)
            
            logger.info("Click fraud model updated")
            
        except Exception as e:
            logger.error(f"Failed to train click fraud model: {str(e)}")
    
    def _train_conversion_fraud_model(self, features: pd.DataFrame):
        """
        Train conversion fraud detection model
        """
        try:
            model_info = self.fraud_models['conversion_fraud']
            X = features[model_info['features']]
            
            # Scale features
            X_scaled = model_info['scaler'].fit_transform(X)
            
            # Create labels (simplified - in practice, use historical fraud data)
            y = np.random.randint(0, 2, len(X_scaled))  # Random labels for demo
            
            # Train model
            model_info['model'].fit(X_scaled, y)
            
            logger.info("Conversion fraud model updated")
            
        except Exception as e:
            logger.error(f"Failed to train conversion fraud model: {str(e)}")
    
    def detect_fraud(self, data: Dict) -> List[FraudAlert]:
        """
        Detect fraud using trained models
        """
        alerts = []
        
        # Check click fraud
        if 'click_data' in data:
            click_alerts = self._detect_click_fraud(data['click_data'])
            alerts.extend(click_alerts)
        
        # Check conversion fraud
        if 'conversion_data' in data:
            conversion_alerts = self._detect_conversion_fraud(data['conversion_data'])
            alerts.extend(conversion_alerts)
        
        return alerts
    
    def _detect_click_fraud(self, click_data: ClickData) -> List[FraudAlert]:
        """
        Detect click fraud using trained model
        """
        alerts = []
        
        try:
            model_info = self.fraud_models['click_fraud']
            
            # Prepare features
            recent_clicks = [c for c in self.click_data 
                           if c.ip_address == click_data.ip_address and 
                           (click_data.timestamp - c.timestamp).total_seconds() < 3600]
            
            features = np.array([[
                len(recent_clicks),
                len(set(c.ip_address for c in recent_clicks)),
                self._calculate_bot_score(click_data),
                self._check_ip_reputation(click_data.ip_address),
                len(set(c.user_agent for c in recent_clicks))
            ]])
            
            # Scale features
            features_scaled = model_info['scaler'].transform(features)
            
            # Predict fraud
            fraud_score = model_info['model'].decision_function(features_scaled)[0]
            
            if fraud_score < -0.5:  # Threshold for fraud detection
                alert = FraudAlert(
                    alert_id=f"alert_{len(self.fraud_alerts)}",
                    fraud_type=FraudType.CLICK_FRAUD,
                    risk_level=RiskLevel.HIGH,
                    description=f"Click fraud detected: {click_data.ip_address}",
                    evidence={'fraud_score': fraud_score, 'ip_address': click_data.ip_address},
                    confidence_score=abs(fraud_score),
                    affiliate_id=click_data.affiliate_id,
                    timestamp=datetime.now(),
                    status='pending'
                )
                alerts.append(alert)
        
        except Exception as e:
            logger.error(f"Failed to detect click fraud: {str(e)}")
        
        return alerts
    
    def _detect_conversion_fraud(self, conversion_data: ConversionData) -> List[FraudAlert]:
        """
        Detect conversion fraud using trained model
        """
        alerts = []
        
        try:
            model_info = self.fraud_models['conversion_fraud']
            
            # Prepare features
            click = next((c for c in self.click_data if c.click_id == conversion_data.click_id), None)
            if not click:
                return alerts
            
            conversion_time = (conversion_data.timestamp - click.timestamp).total_seconds()
            
            affiliate_conversions = [c for c in self.conversion_data 
                                   if c.affiliate_id == conversion_data.affiliate_id]
            
            conversion_rate = len(affiliate_conversions) / len([c for c in self.click_data 
                                                              if c.affiliate_id == conversion_data.affiliate_id])
            
            amounts = [c.amount for c in affiliate_conversions]
            amount_variance = np.var(amounts) if len(amounts) > 1 else 0
            
            payment_risk_score = self._calculate_payment_risk_score(conversion_data)
            
            features = np.array([[
                conversion_rate,
                conversion_time,
                amount_variance,
                payment_risk_score
            ]])
            
            # Scale features
            features_scaled = model_info['scaler'].transform(features)
            
            # Predict fraud
            fraud_probability = model_info['model'].predict_proba(features_scaled)[0][1]
            
            if fraud_probability > 0.7:  # Threshold for fraud detection
                alert = FraudAlert(
                    alert_id=f"alert_{len(self.fraud_alerts)}",
                    fraud_type=FraudType.CONVERSION_FRAUD,
                    risk_level=RiskLevel.HIGH,
                    description=f"Conversion fraud detected: {conversion_data.conversion_id}",
                    evidence={'fraud_probability': fraud_probability, 'conversion_id': conversion_data.conversion_id},
                    confidence_score=fraud_probability,
                    affiliate_id=conversion_data.affiliate_id,
                    timestamp=datetime.now(),
                    status='pending'
                )
                alerts.append(alert)
        
        except Exception as e:
            logger.error(f"Failed to detect conversion fraud: {str(e)}")
        
        return alerts
    
    def get_fraud_summary(self) -> Dict:
        """
        Get fraud detection summary
        """
        total_alerts = len(self.fraud_alerts)
        pending_alerts = len([a for a in self.fraud_alerts if a.status == 'pending'])
        resolved_alerts = len([a for a in self.fraud_alerts if a.status == 'resolved'])
        false_positives = len([a for a in self.fraud_alerts if a.status == 'false_positive'])
        
        # Fraud type distribution
        fraud_type_dist = {}
        for alert in self.fraud_alerts:
            fraud_type = alert.fraud_type.value
            if fraud_type not in fraud_type_dist:
                fraud_type_dist[fraud_type] = 0
            fraud_type_dist[fraud_type] += 1
        
        # Risk level distribution
        risk_level_dist = {}
        for alert in self.fraud_alerts:
            risk_level = alert.risk_level.value
            if risk_level not in risk_level_dist:
                risk_level_dist[risk_level] = 0
            risk_level_dist[risk_level] += 1
        
        # Top suspicious affiliates
        affiliate_alerts = {}
        for alert in self.fraud_alerts:
            if alert.affiliate_id:
                if alert.affiliate_id not in affiliate_alerts:
                    affiliate_alerts[alert.affiliate_id] = 0
                affiliate_alerts[alert.affiliate_id] += 1
        
        top_suspicious = sorted(affiliate_alerts.items(), key=lambda x: x[1], reverse=True)[:10]
        
        return {
            'total_alerts': total_alerts,
            'pending_alerts': pending_alerts,
            'resolved_alerts': resolved_alerts,
            'false_positives': false_positives,
            'fraud_type_distribution': fraud_type_dist,
            'risk_level_distribution': risk_level_dist,
            'top_suspicious_affiliates': top_suspicious,
            'blocked_ips': len(self.blocked_ips),
            'suspicious_affiliates': len(self.suspicious_affiliates),
            'generated_at': datetime.now().isoformat()
        }
    
    def block_ip(self, ip_address: str, reason: str = "Fraudulent activity"):
        """
        Block IP address
        """
        self.blocked_ips.add(ip_address)
        logger.info(f"Blocked IP {ip_address}: {reason}")
    
    def unblock_ip(self, ip_address: str):
        """
        Unblock IP address
        """
        self.blocked_ips.discard(ip_address)
        logger.info(f"Unblocked IP {ip_address}")
    
    def suspend_affiliate(self, affiliate_id: str, reason: str = "Fraudulent activity"):
        """
        Suspend affiliate
        """
        self.suspicious_affiliates.add(affiliate_id)
        logger.info(f"Suspended affiliate {affiliate_id}: {reason}")
    
    def resolve_alert(self, alert_id: str, resolution: str, is_false_positive: bool = False):
        """
        Resolve fraud alert
        """
        alert = next((a for a in self.fraud_alerts if a.alert_id == alert_id), None)
        if not alert:
            logger.error(f"Alert {alert_id} not found")
            return
        
        alert.status = 'false_positive' if is_false_positive else 'resolved'
        alert.evidence['resolution'] = resolution
        alert.evidence['resolved_at'] = datetime.now().isoformat()
        
        logger.info(f"Resolved alert {alert_id}: {resolution}")
    
    def export_fraud_data(self, format: str = 'json') -> str:
        """
        Export fraud detection data
        """
        data = {
            'fraud_alerts': [asdict(alert) for alert in self.fraud_alerts],
            'blocked_ips': list(self.blocked_ips),
            'suspicious_affiliates': list(self.suspicious_affiliates),
            'fraud_summary': self.get_fraud_summary()
        }
        
        if format == 'json':
            return json.dumps(data, indent=2, default=str)
        elif format == 'csv':
            # Export fraud alerts as CSV
            if self.fraud_alerts:
                df = pd.DataFrame([asdict(alert) for alert in self.fraud_alerts])
                return df.to_csv(index=False)
            else:
                return ""
        else:
            raise ValueError(f"Unsupported format: {format}")

# Example usage
def main():
    """
    Example usage of AI-Powered Fraud Detection
    """
    # Initialize fraud detection system
    fraud_detection = AIPoweredFraudDetection()
    
    # Add sample click data
    click1 = ClickData(
        click_id="click_1",
        affiliate_id="affiliate_1",
        ip_address="192.168.1.1",
        user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
        referrer="https://google.com",
        timestamp=datetime.now(),
        country="US",
        city="New York",
        device_type="desktop",
        browser="Chrome",
        os="Windows"
    )
    
    click2 = ClickData(
        click_id="click_2",
        affiliate_id="affiliate_1",
        ip_address="192.168.1.1",  # Same IP
        user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
        referrer="https://google.com",
        timestamp=datetime.now() - timedelta(minutes=1),
        country="US",
        city="New York",
        device_type="desktop",
        browser="Chrome",
        os="Windows"
    )
    
    # Add click data
    fraud_detection.add_click_data(click1)
    fraud_detection.add_click_data(click2)
    
    # Add sample conversion data
    conversion1 = ConversionData(
        conversion_id="conv_1",
        affiliate_id="affiliate_1",
        click_id="click_1",
        amount=100.0,
        timestamp=datetime.now(),
        ip_address="192.168.1.1",
        user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
        payment_method="credit_card",
        customer_email="customer@example.com"
    )
    
    # Add conversion data
    fraud_detection.add_conversion_data(conversion1)
    
    # Get fraud summary
    summary = fraud_detection.get_fraud_summary()
    print(f"Fraud summary: {summary}")
    
    # Export data
    json_data = fraud_detection.export_fraud_data('json')
    print(f"Exported fraud data: {len(json_data)} characters")

if __name__ == "__main__":
    main()


