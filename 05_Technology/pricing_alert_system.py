#!/usr/bin/env python3
"""
Pricing Alert and Notification System
=====================================

Automated alert system for competitive pricing analysis that monitors price changes,
market conditions, and competitive threats. Sends notifications via multiple channels.

Features:
- Real-time price change monitoring
- Competitive threat detection
- Market opportunity alerts
- Multi-channel notifications (email, SMS, webhook)
- Customizable alert rules and thresholds
- Alert history and analytics
"""

import smtplib
import sqlite3
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass, asdict
from email.mime.text import MimeText
from email.mime.multipart import MimeMultipart
from email.mime.base import MimeBase
from email import encoders
import requests
import schedule
import time
import threading
from enum import Enum
import yaml
import pandas as pd
import numpy as np

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AlertType(Enum):
    """Types of pricing alerts"""
    PRICE_INCREASE = "price_increase"
    PRICE_DECREASE = "price_decrease"
    NEW_COMPETITOR = "new_competitor"
    PRICE_GAP = "price_gap"
    MARKET_OPPORTUNITY = "market_opportunity"
    COMPETITIVE_THREAT = "competitive_threat"
    DATA_QUALITY = "data_quality"
    SYSTEM_ERROR = "system_error"

class AlertSeverity(Enum):
    """Alert severity levels"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class NotificationChannel(Enum):
    """Notification channels"""
    EMAIL = "email"
    SMS = "sms"
    WEBHOOK = "webhook"
    SLACK = "slack"
    TEAMS = "teams"

@dataclass
class AlertRule:
    """Alert rule configuration"""
    rule_id: str
    name: str
    alert_type: AlertType
    severity: AlertSeverity
    conditions: Dict[str, Any]
    thresholds: Dict[str, float]
    enabled: bool = True
    notification_channels: List[NotificationChannel] = None
    recipients: List[str] = None
    cooldown_minutes: int = 60  # Minimum time between alerts of same type

@dataclass
class Alert:
    """Alert data structure"""
    alert_id: str
    rule_id: str
    alert_type: AlertType
    severity: AlertSeverity
    title: str
    message: str
    product_id: Optional[str] = None
    competitor: Optional[str] = None
    price_data: Optional[Dict[str, Any]] = None
    created_at: datetime = None
    sent_at: Optional[datetime] = None
    acknowledged: bool = False

class PricingAlertSystem:
    """
    Main pricing alert system
    """
    
    def __init__(self, config_file: str = "alert_config.yaml"):
        """Initialize the alert system"""
        self.config = self._load_config(config_file)
        self.db_path = self.config.get('database_path', 'pricing_analysis.db')
        self.alert_rules = {}
        self.alert_history = []
        self.notification_handlers = {}
        
        # Initialize notification handlers
        self._initialize_notification_handlers()
        
        # Load alert rules
        self._load_alert_rules()
        
        # Initialize database
        self._init_database()
        
        logger.info("Pricing Alert System initialized successfully")
    
    def _load_config(self, config_file: str) -> Dict:
        """Load configuration from YAML file"""
        try:
            with open(config_file, 'r') as f:
                return yaml.safe_load(f)
        except FileNotFoundError:
            logger.warning(f"Config file {config_file} not found, using defaults")
            return self._get_default_config()
    
    def _get_default_config(self) -> Dict:
        """Get default configuration"""
        return {
            'database_path': 'pricing_analysis.db',
            'email': {
                'smtp_server': 'smtp.gmail.com',
                'smtp_port': 587,
                'username': '',
                'password': '',
                'from_email': ''
            },
            'sms': {
                'provider': 'twilio',
                'account_sid': '',
                'auth_token': '',
                'from_number': ''
            },
            'webhook': {
                'url': '',
                'headers': {}
            },
            'slack': {
                'webhook_url': '',
                'channel': '#pricing-alerts'
            },
            'teams': {
                'webhook_url': ''
            },
            'alert_rules': []
        }
    
    def _initialize_notification_handlers(self):
        """Initialize notification handlers for different channels"""
        self.notification_handlers = {
            NotificationChannel.EMAIL: self._send_email_notification,
            NotificationChannel.SMS: self._send_sms_notification,
            NotificationChannel.WEBHOOK: self._send_webhook_notification,
            NotificationChannel.SLACK: self._send_slack_notification,
            NotificationChannel.TEAMS: self._send_teams_notification
        }
    
    def _load_alert_rules(self):
        """Load alert rules from configuration"""
        try:
            rules_config = self.config.get('alert_rules', [])
            
            for rule_config in rules_config:
                rule = AlertRule(
                    rule_id=rule_config['rule_id'],
                    name=rule_config['name'],
                    alert_type=AlertType(rule_config['alert_type']),
                    severity=AlertSeverity(rule_config['severity']),
                    conditions=rule_config.get('conditions', {}),
                    thresholds=rule_config.get('thresholds', {}),
                    enabled=rule_config.get('enabled', True),
                    notification_channels=[NotificationChannel(ch) for ch in rule_config.get('notification_channels', ['email'])],
                    recipients=rule_config.get('recipients', []),
                    cooldown_minutes=rule_config.get('cooldown_minutes', 60)
                )
                self.alert_rules[rule.rule_id] = rule
            
            logger.info(f"Loaded {len(self.alert_rules)} alert rules")
            
        except Exception as e:
            logger.error(f"Error loading alert rules: {e}")
    
    def _init_database(self):
        """Initialize database for alert storage"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Create alerts table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS alerts (
                alert_id TEXT PRIMARY KEY,
                rule_id TEXT NOT NULL,
                alert_type TEXT NOT NULL,
                severity TEXT NOT NULL,
                title TEXT NOT NULL,
                message TEXT NOT NULL,
                product_id TEXT,
                competitor TEXT,
                price_data TEXT,
                created_at TIMESTAMP NOT NULL,
                sent_at TIMESTAMP,
                acknowledged BOOLEAN DEFAULT FALSE
            )
        ''')
        
        # Create alert rules table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS alert_rules (
                rule_id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                alert_type TEXT NOT NULL,
                severity TEXT NOT NULL,
                conditions TEXT NOT NULL,
                thresholds TEXT NOT NULL,
                enabled BOOLEAN DEFAULT TRUE,
                notification_channels TEXT NOT NULL,
                recipients TEXT NOT NULL,
                cooldown_minutes INTEGER DEFAULT 60,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def check_price_changes(self) -> List[Alert]:
        """Check for significant price changes"""
        alerts = []
        
        try:
            conn = sqlite3.connect(self.db_path)
            
            # Get recent price changes
            query = '''
                SELECT 
                    product_id,
                    product_name,
                    competitor,
                    price,
                    date_collected,
                    LAG(price) OVER (PARTITION BY product_id, competitor ORDER BY date_collected) as prev_price
                FROM pricing_data
                WHERE date_collected >= date('now', '-1 day')
                ORDER BY date_collected DESC
            '''
            
            df = pd.read_sql_query(query, conn)
            conn.close()
            
            if df.empty:
                return alerts
            
            # Calculate price changes
            df['price_change'] = df['price'] - df['prev_price']
            df['price_change_pct'] = (df['price_change'] / df['prev_price']) * 100
            
            # Check for significant changes
            for _, row in df.iterrows():
                if pd.isna(row['prev_price']) or pd.isna(row['price_change_pct']):
                    continue
                
                price_change_pct = abs(row['price_change_pct'])
                
                # Check against thresholds
                if price_change_pct >= 10:  # 10% or more change
                    alert_type = AlertType.PRICE_INCREASE if row['price_change'] > 0 else AlertType.PRICE_DECREASE
                    severity = AlertSeverity.HIGH if price_change_pct >= 20 else AlertSeverity.MEDIUM
                    
                    alert = Alert(
                        alert_id=f"price_change_{row['product_id']}_{row['competitor']}_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                        rule_id="price_change_monitor",
                        alert_type=alert_type,
                        severity=severity,
                        title=f"{alert_type.value.replace('_', ' ').title()} Alert",
                        message=f"{row['competitor']} changed price for {row['product_name']} from ${row['prev_price']:.2f} to ${row['price']:.2f} ({row['price_change_pct']:+.1f}%)",
                        product_id=row['product_id'],
                        competitor=row['competitor'],
                        price_data={
                            'current_price': row['price'],
                            'previous_price': row['prev_price'],
                            'price_change': row['price_change'],
                            'price_change_pct': row['price_change_pct']
                        },
                        created_at=datetime.now()
                    )
                    
                    alerts.append(alert)
            
            return alerts
            
        except Exception as e:
            logger.error(f"Error checking price changes: {e}")
            return []
    
    def check_price_gaps(self) -> List[Alert]:
        """Check for significant price gaps between competitors"""
        alerts = []
        
        try:
            conn = sqlite3.connect(self.db_path)
            
            # Get latest prices by product
            query = '''
                SELECT 
                    product_id,
                    product_name,
                    competitor,
                    price
                FROM pricing_data
                WHERE date_collected >= date('now', '-1 day')
                AND price IS NOT NULL
                ORDER BY product_id, price
            '''
            
            df = pd.read_sql_query(query, conn)
            conn.close()
            
            if df.empty:
                return alerts
            
            # Group by product and analyze price gaps
            for product_id, product_data in df.groupby('product_id'):
                if len(product_data) < 2:
                    continue
                
                prices = product_data['price'].values
                competitors = product_data['competitor'].values
                
                min_price = np.min(prices)
                max_price = np.max(prices)
                price_range = max_price - min_price
                price_gap_pct = (price_range / min_price) * 100
                
                # Check for significant price gaps
                if price_gap_pct >= 30:  # 30% or more gap
                    min_competitor = competitors[np.argmin(prices)]
                    max_competitor = competitors[np.argmax(prices)]
                    
                    alert = Alert(
                        alert_id=f"price_gap_{product_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                        rule_id="price_gap_monitor",
                        alert_type=AlertType.PRICE_GAP,
                        severity=AlertSeverity.HIGH if price_gap_pct >= 50 else AlertSeverity.MEDIUM,
                        title="Significant Price Gap Detected",
                        message=f"Large price gap for {product_data.iloc[0]['product_name']}: {min_competitor} at ${min_price:.2f} vs {max_competitor} at ${max_price:.2f} ({price_gap_pct:.1f}% gap)",
                        product_id=product_id,
                        price_data={
                            'min_price': min_price,
                            'max_price': max_price,
                            'price_gap': price_range,
                            'price_gap_pct': price_gap_pct,
                            'min_competitor': min_competitor,
                            'max_competitor': max_competitor
                        },
                        created_at=datetime.now()
                    )
                    
                    alerts.append(alert)
            
            return alerts
            
        except Exception as e:
            logger.error(f"Error checking price gaps: {e}")
            return []
    
    def check_market_opportunities(self) -> List[Alert]:
        """Check for market opportunities"""
        alerts = []
        
        try:
            conn = sqlite3.connect(self.db_path)
            
            # Get market data
            query = '''
                SELECT 
                    product_id,
                    product_name,
                    competitor,
                    price,
                    date_collected
                FROM pricing_data
                WHERE date_collected >= date('now', '-7 days')
                ORDER BY product_id, price
            '''
            
            df = pd.read_sql_query(query, conn)
            conn.close()
            
            if df.empty:
                return alerts
            
            # Analyze market opportunities
            for product_id, product_data in df.groupby('product_id'):
                if len(product_data) < 3:
                    continue
                
                prices = product_data['price'].values
                avg_price = np.mean(prices)
                median_price = np.median(prices)
                
                # Check for pricing opportunities
                if median_price > avg_price * 1.2:  # Median significantly higher than average
                    alert = Alert(
                        alert_id=f"market_opportunity_{product_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                        rule_id="market_opportunity_monitor",
                        alert_type=AlertType.MARKET_OPPORTUNITY,
                        severity=AlertSeverity.MEDIUM,
                        title="Market Pricing Opportunity",
                        message=f"Pricing opportunity for {product_data.iloc[0]['product_name']}: Market median (${median_price:.2f}) is significantly higher than average (${avg_price:.2f})",
                        product_id=product_id,
                        price_data={
                            'average_price': avg_price,
                            'median_price': median_price,
                            'price_variance': np.var(prices),
                            'competitor_count': len(product_data)
                        },
                        created_at=datetime.now()
                    )
                    
                    alerts.append(alert)
            
            return alerts
            
        except Exception as e:
            logger.error(f"Error checking market opportunities: {e}")
            return []
    
    def check_data_quality(self) -> List[Alert]:
        """Check for data quality issues"""
        alerts = []
        
        try:
            conn = sqlite3.connect(self.db_path)
            
            # Check for missing data
            query = '''
                SELECT 
                    product_id,
                    COUNT(*) as data_points,
                    MAX(date_collected) as latest_data
                FROM pricing_data
                WHERE date_collected >= date('now', '-7 days')
                GROUP BY product_id
            '''
            
            df = pd.read_sql_query(query, conn)
            conn.close()
            
            if df.empty:
                alert = Alert(
                    alert_id=f"data_quality_no_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                    rule_id="data_quality_monitor",
                    alert_type=AlertType.DATA_QUALITY,
                    severity=AlertSeverity.CRITICAL,
                    title="No Pricing Data Available",
                    message="No pricing data has been collected in the last 7 days",
                    created_at=datetime.now()
                )
                alerts.append(alert)
                return alerts
            
            # Check for products with insufficient data
            for _, row in df.iterrows():
                if row['data_points'] < 3:  # Less than 3 data points
                    alert = Alert(
                        alert_id=f"data_quality_insufficient_{row['product_id']}_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                        rule_id="data_quality_monitor",
                        alert_type=AlertType.DATA_QUALITY,
                        severity=AlertSeverity.MEDIUM,
                        title="Insufficient Pricing Data",
                        message=f"Product {row['product_id']} has only {row['data_points']} data points in the last 7 days",
                        product_id=row['product_id'],
                        created_at=datetime.now()
                    )
                    alerts.append(alert)
            
            return alerts
            
        except Exception as e:
            logger.error(f"Error checking data quality: {e}")
            return []
    
    def run_alert_checks(self) -> List[Alert]:
        """Run all alert checks"""
        all_alerts = []
        
        logger.info("Running alert checks...")
        
        # Check price changes
        price_change_alerts = self.check_price_changes()
        all_alerts.extend(price_change_alerts)
        
        # Check price gaps
        price_gap_alerts = self.check_price_gaps()
        all_alerts.extend(price_gap_alerts)
        
        # Check market opportunities
        opportunity_alerts = self.check_market_opportunities()
        all_alerts.extend(opportunity_alerts)
        
        # Check data quality
        data_quality_alerts = self.check_data_quality()
        all_alerts.extend(data_quality_alerts)
        
        logger.info(f"Generated {len(all_alerts)} alerts")
        
        return all_alerts
    
    def process_alerts(self, alerts: List[Alert]):
        """Process and send alerts"""
        for alert in alerts:
            try:
                # Check if alert should be sent (cooldown, etc.)
                if self._should_send_alert(alert):
                    # Store alert in database
                    self._store_alert(alert)
                    
                    # Send notifications
                    self._send_alert_notifications(alert)
                    
                    logger.info(f"Processed alert: {alert.title}")
                else:
                    logger.info(f"Skipped alert due to cooldown: {alert.title}")
                    
            except Exception as e:
                logger.error(f"Error processing alert {alert.alert_id}: {e}")
    
    def _should_send_alert(self, alert: Alert) -> bool:
        """Check if alert should be sent based on cooldown rules"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Check for recent alerts of the same type
            query = '''
                SELECT created_at
                FROM alerts
                WHERE alert_type = ? AND product_id = ? AND competitor = ?
                AND created_at >= datetime('now', '-{} minutes')
                ORDER BY created_at DESC
                LIMIT 1
            '''.format(60)  # Default cooldown of 60 minutes
            
            cursor.execute(query, (alert.alert_type.value, alert.product_id, alert.competitor))
            result = cursor.fetchone()
            
            conn.close()
            
            if result:
                last_alert_time = datetime.fromisoformat(result[0])
                cooldown_period = timedelta(minutes=60)  # Default cooldown
                
                if datetime.now() - last_alert_time < cooldown_period:
                    return False
            
            return True
            
        except Exception as e:
            logger.error(f"Error checking alert cooldown: {e}")
            return True
    
    def _store_alert(self, alert: Alert):
        """Store alert in database"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO alerts 
                (alert_id, rule_id, alert_type, severity, title, message, product_id, competitor, price_data, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                alert.alert_id,
                alert.rule_id,
                alert.alert_type.value,
                alert.severity.value,
                alert.title,
                alert.message,
                alert.product_id,
                alert.competitor,
                json.dumps(alert.price_data) if alert.price_data else None,
                alert.created_at.isoformat()
            ))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            logger.error(f"Error storing alert: {e}")
    
    def _send_alert_notifications(self, alert: Alert):
        """Send alert notifications through configured channels"""
        try:
            # Get notification channels from alert rules
            rule = self.alert_rules.get(alert.rule_id)
            if not rule:
                # Use default channels
                channels = [NotificationChannel.EMAIL]
                recipients = self.config.get('email', {}).get('recipients', [])
            else:
                channels = rule.notification_channels
                recipients = rule.recipients
            
            # Send notifications
            for channel in channels:
                try:
                    handler = self.notification_handlers.get(channel)
                    if handler:
                        handler(alert, recipients)
                        logger.info(f"Sent {channel.value} notification for alert: {alert.title}")
                    else:
                        logger.warning(f"No handler for notification channel: {channel.value}")
                        
                except Exception as e:
                    logger.error(f"Error sending {channel.value} notification: {e}")
            
            # Update alert as sent
            self._update_alert_sent(alert.alert_id)
            
        except Exception as e:
            logger.error(f"Error sending alert notifications: {e}")
    
    def _send_email_notification(self, alert: Alert, recipients: List[str]):
        """Send email notification"""
        try:
            email_config = self.config.get('email', {})
            
            if not email_config.get('username') or not recipients:
                logger.warning("Email configuration incomplete or no recipients")
                return
            
            # Create message
            msg = MimeMultipart()
            msg['From'] = email_config['from_email']
            msg['To'] = ', '.join(recipients)
            msg['Subject'] = f"[{alert.severity.value.upper()}] {alert.title}"
            
            # Create email body
            body = f"""
            <html>
            <body>
                <h2>{alert.title}</h2>
                <p><strong>Severity:</strong> {alert.severity.value.upper()}</p>
                <p><strong>Type:</strong> {alert.alert_type.value.replace('_', ' ').title()}</p>
                <p><strong>Time:</strong> {alert.created_at.strftime('%Y-%m-%d %H:%M:%S')}</p>
                <p><strong>Message:</strong> {alert.message}</p>
                
                {self._format_price_data_html(alert.price_data) if alert.price_data else ''}
                
                <hr>
                <p><em>This is an automated alert from the Competitive Pricing Analysis System.</em></p>
            </body>
            </html>
            """
            
            msg.attach(MimeText(body, 'html'))
            
            # Send email
            server = smtplib.SMTP(email_config['smtp_server'], email_config['smtp_port'])
            server.starttls()
            server.login(email_config['username'], email_config['password'])
            server.send_message(msg)
            server.quit()
            
        except Exception as e:
            logger.error(f"Error sending email notification: {e}")
    
    def _send_sms_notification(self, alert: Alert, recipients: List[str]):
        """Send SMS notification"""
        try:
            sms_config = self.config.get('sms', {})
            
            if not sms_config.get('account_sid') or not recipients:
                logger.warning("SMS configuration incomplete or no recipients")
                return
            
            # Create message
            message = f"[{alert.severity.value.upper()}] {alert.title}\n{alert.message}"
            
            # Send SMS using Twilio (example)
            from twilio.rest import Client
            
            client = Client(sms_config['account_sid'], sms_config['auth_token'])
            
            for recipient in recipients:
                client.messages.create(
                    body=message,
                    from_=sms_config['from_number'],
                    to=recipient
                )
            
        except Exception as e:
            logger.error(f"Error sending SMS notification: {e}")
    
    def _send_webhook_notification(self, alert: Alert, recipients: List[str]):
        """Send webhook notification"""
        try:
            webhook_config = self.config.get('webhook', {})
            
            if not webhook_config.get('url'):
                logger.warning("Webhook URL not configured")
                return
            
            # Prepare payload
            payload = {
                'alert_id': alert.alert_id,
                'alert_type': alert.alert_type.value,
                'severity': alert.severity.value,
                'title': alert.title,
                'message': alert.message,
                'product_id': alert.product_id,
                'competitor': alert.competitor,
                'price_data': alert.price_data,
                'created_at': alert.created_at.isoformat()
            }
            
            # Send webhook
            response = requests.post(
                webhook_config['url'],
                json=payload,
                headers=webhook_config.get('headers', {}),
                timeout=30
            )
            
            response.raise_for_status()
            
        except Exception as e:
            logger.error(f"Error sending webhook notification: {e}")
    
    def _send_slack_notification(self, alert: Alert, recipients: List[str]):
        """Send Slack notification"""
        try:
            slack_config = self.config.get('slack', {})
            
            if not slack_config.get('webhook_url'):
                logger.warning("Slack webhook URL not configured")
                return
            
            # Prepare message
            color = {
                AlertSeverity.LOW: "good",
                AlertSeverity.MEDIUM: "warning",
                AlertSeverity.HIGH: "danger",
                AlertSeverity.CRITICAL: "danger"
            }.get(alert.severity, "good")
            
            payload = {
                "channel": slack_config.get('channel', '#pricing-alerts'),
                "username": "Pricing Alert Bot",
                "icon_emoji": ":chart_with_upwards_trend:",
                "attachments": [
                    {
                        "color": color,
                        "title": alert.title,
                        "text": alert.message,
                        "fields": [
                            {
                                "title": "Severity",
                                "value": alert.severity.value.upper(),
                                "short": True
                            },
                            {
                                "title": "Type",
                                "value": alert.alert_type.value.replace('_', ' ').title(),
                                "short": True
                            },
                            {
                                "title": "Time",
                                "value": alert.created_at.strftime('%Y-%m-%d %H:%M:%S'),
                                "short": True
                            }
                        ],
                        "footer": "Competitive Pricing Analysis System",
                        "ts": int(alert.created_at.timestamp())
                    }
                ]
            }
            
            # Add price data if available
            if alert.price_data:
                for key, value in alert.price_data.items():
                    payload["attachments"][0]["fields"].append({
                        "title": key.replace('_', ' ').title(),
                        "value": str(value),
                        "short": True
                    })
            
            # Send to Slack
            response = requests.post(slack_config['webhook_url'], json=payload, timeout=30)
            response.raise_for_status()
            
        except Exception as e:
            logger.error(f"Error sending Slack notification: {e}")
    
    def _send_teams_notification(self, alert: Alert, recipients: List[str]):
        """Send Microsoft Teams notification"""
        try:
            teams_config = self.config.get('teams', {})
            
            if not teams_config.get('webhook_url'):
                logger.warning("Teams webhook URL not configured")
                return
            
            # Prepare message
            color = {
                AlertSeverity.LOW: "00ff00",
                AlertSeverity.MEDIUM: "ffff00",
                AlertSeverity.HIGH: "ff6600",
                AlertSeverity.CRITICAL: "ff0000"
            }.get(alert.severity, "00ff00")
            
            payload = {
                "@type": "MessageCard",
                "@context": "http://schema.org/extensions",
                "themeColor": color,
                "summary": alert.title,
                "sections": [
                    {
                        "activityTitle": alert.title,
                        "activitySubtitle": f"Severity: {alert.severity.value.upper()}",
                        "activityImage": "https://img.icons8.com/color/48/000000/price-tag.png",
                        "facts": [
                            {
                                "name": "Type",
                                "value": alert.alert_type.value.replace('_', ' ').title()
                            },
                            {
                                "name": "Time",
                                "value": alert.created_at.strftime('%Y-%m-%d %H:%M:%S')
                            }
                        ],
                        "markdown": True
                    }
                ]
            }
            
            # Add message
            payload["sections"][0]["text"] = alert.message
            
            # Add price data if available
            if alert.price_data:
                for key, value in alert.price_data.items():
                    payload["sections"][0]["facts"].append({
                        "name": key.replace('_', ' ').title(),
                        "value": str(value)
                    })
            
            # Send to Teams
            response = requests.post(teams_config['webhook_url'], json=payload, timeout=30)
            response.raise_for_status()
            
        except Exception as e:
            logger.error(f"Error sending Teams notification: {e}")
    
    def _format_price_data_html(self, price_data: Dict[str, Any]) -> str:
        """Format price data as HTML"""
        if not price_data:
            return ""
        
        html = "<h3>Price Data:</h3><ul>"
        for key, value in price_data.items():
            html += f"<li><strong>{key.replace('_', ' ').title()}:</strong> {value}</li>"
        html += "</ul>"
        
        return html
    
    def _update_alert_sent(self, alert_id: str):
        """Update alert as sent in database"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                UPDATE alerts 
                SET sent_at = ?
                WHERE alert_id = ?
            ''', (datetime.now().isoformat(), alert_id))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            logger.error(f"Error updating alert sent status: {e}")
    
    def get_alert_history(self, limit: int = 100) -> List[Dict[str, Any]]:
        """Get alert history from database"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT 
                    alert_id,
                    rule_id,
                    alert_type,
                    severity,
                    title,
                    message,
                    product_id,
                    competitor,
                    price_data,
                    created_at,
                    sent_at,
                    acknowledged
                FROM alerts
                ORDER BY created_at DESC
                LIMIT ?
            ''', (limit,))
            
            rows = cursor.fetchall()
            conn.close()
            
            alerts = []
            for row in rows:
                alert = {
                    'alert_id': row[0],
                    'rule_id': row[1],
                    'alert_type': row[2],
                    'severity': row[3],
                    'title': row[4],
                    'message': row[5],
                    'product_id': row[6],
                    'competitor': row[7],
                    'price_data': json.loads(row[8]) if row[8] else None,
                    'created_at': row[9],
                    'sent_at': row[10],
                    'acknowledged': bool(row[11])
                }
                alerts.append(alert)
            
            return alerts
            
        except Exception as e:
            logger.error(f"Error getting alert history: {e}")
            return []
    
    def acknowledge_alert(self, alert_id: str):
        """Acknowledge an alert"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                UPDATE alerts 
                SET acknowledged = TRUE
                WHERE alert_id = ?
            ''', (alert_id,))
            
            conn.commit()
            conn.close()
            
            logger.info(f"Alert {alert_id} acknowledged")
            
        except Exception as e:
            logger.error(f"Error acknowledging alert: {e}")
    
    def start_monitoring(self, interval_minutes: int = 15):
        """Start continuous monitoring"""
        logger.info(f"Starting alert monitoring with {interval_minutes} minute intervals")
        
        def monitor():
            while True:
                try:
                    # Run alert checks
                    alerts = self.run_alert_checks()
                    
                    # Process alerts
                    if alerts:
                        self.process_alerts(alerts)
                    
                    # Wait for next check
                    time.sleep(interval_minutes * 60)
                    
                except Exception as e:
                    logger.error(f"Error in monitoring loop: {e}")
                    time.sleep(60)  # Wait 1 minute before retrying
        
        # Start monitoring in background thread
        monitor_thread = threading.Thread(target=monitor, daemon=True)
        monitor_thread.start()
        
        return monitor_thread

def main():
    """Main function to demonstrate alert system"""
    # Initialize alert system
    alert_system = PricingAlertSystem()
    
    # Run alert checks
    print("Running alert checks...")
    alerts = alert_system.run_alert_checks()
    
    if alerts:
        print(f"Generated {len(alerts)} alerts:")
        for alert in alerts:
            print(f"- {alert.severity.value.upper()}: {alert.title}")
            print(f"  {alert.message}")
            print()
        
        # Process alerts (this would normally send notifications)
        print("Processing alerts...")
        alert_system.process_alerts(alerts)
    else:
        print("No alerts generated")
    
    # Show alert history
    print("\nAlert History:")
    history = alert_system.get_alert_history(10)
    for alert in history:
        print(f"- {alert['created_at']}: {alert['title']} ({alert['severity']})")

if __name__ == "__main__":
    main()






