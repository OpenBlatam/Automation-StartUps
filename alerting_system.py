"""
Intelligent Alerting System for Ultimate Launch Planning System
Provides smart alerts, notifications, and escalation management
"""

import json
import time
import smtplib
import requests
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Callable
from dataclasses import dataclass, asdict
from enum import Enum
import logging
import threading
from email.mime.text import MimeText
from email.mime.multipart import MimeMultipart

logger = logging.getLogger(__name__)

class AlertSeverity(Enum):
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"

class AlertStatus(Enum):
    ACTIVE = "active"
    ACKNOWLEDGED = "acknowledged"
    RESOLVED = "resolved"
    SUPPRESSED = "suppressed"

@dataclass
class Alert:
    id: str
    title: str
    description: str
    severity: AlertSeverity
    status: AlertStatus
    source: str
    timestamp: datetime
    labels: Dict[str, str]
    resolved_at: Optional[datetime] = None
    acknowledged_by: Optional[str] = None
    acknowledged_at: Optional[datetime] = None
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "title": self.title,
            "description": self.description,
            "severity": self.severity.value,
            "status": self.status.value,
            "source": self.source,
            "timestamp": self.timestamp.isoformat(),
            "labels": self.labels,
            "resolved_at": self.resolved_at.isoformat() if self.resolved_at else None,
            "acknowledged_by": self.acknowledged_by,
            "acknowledged_at": self.acknowledged_at.isoformat() if self.acknowledged_at else None
        }

@dataclass
class AlertRule:
    name: str
    condition: str
    severity: AlertSeverity
    description: str
    enabled: bool = True
    cooldown_minutes: int = 5
    escalation_minutes: int = 30
    
    def evaluate(self, metrics: Dict[str, Any]) -> bool:
        """Evaluate alert rule condition"""
        try:
            # Simple condition evaluation (can be extended with more complex logic)
            return eval(self.condition, {"metrics": metrics, "__builtins__": {}})
        except Exception as e:
            logger.error(f"Error evaluating alert rule {self.name}: {e}")
            return False

class NotificationChannel:
    """Base class for notification channels"""
    
    def send(self, alert: Alert) -> bool:
        """Send notification for an alert"""
        raise NotImplementedError

class EmailNotificationChannel(NotificationChannel):
    """Email notification channel"""
    
    def __init__(self, smtp_server: str, smtp_port: int, username: str, password: str, 
                 from_email: str, to_emails: List[str]):
        self.smtp_server = smtp_server
        self.smtp_port = smtp_port
        self.username = username
        self.password = password
        self.from_email = from_email
        self.to_emails = to_emails
    
    def send(self, alert: Alert) -> bool:
        """Send email notification"""
        try:
            msg = MimeMultipart()
            msg['From'] = self.from_email
            msg['To'] = ", ".join(self.to_emails)
            msg['Subject'] = f"[{alert.severity.value.upper()}] {alert.title}"
            
            body = f"""
Alert Details:
- Title: {alert.title}
- Description: {alert.description}
- Severity: {alert.severity.value.upper()}
- Source: {alert.source}
- Timestamp: {alert.timestamp.isoformat()}
- Labels: {json.dumps(alert.labels, indent=2)}

Please take appropriate action.
            """
            
            msg.attach(MimeText(body, 'plain'))
            
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls()
                server.login(self.username, self.password)
                server.send_message(msg)
            
            logger.info(f"Email notification sent for alert {alert.id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to send email notification: {e}")
            return False

class SlackNotificationChannel(NotificationChannel):
    """Slack notification channel"""
    
    def __init__(self, webhook_url: str, channel: str = "#alerts"):
        self.webhook_url = webhook_url
        self.channel = channel
    
    def send(self, alert: Alert) -> bool:
        """Send Slack notification"""
        try:
            color_map = {
                AlertSeverity.INFO: "good",
                AlertSeverity.WARNING: "warning",
                AlertSeverity.ERROR: "danger",
                AlertSeverity.CRITICAL: "danger"
            }
            
            payload = {
                "channel": self.channel,
                "attachments": [{
                    "color": color_map.get(alert.severity, "good"),
                    "title": alert.title,
                    "text": alert.description,
                    "fields": [
                        {"title": "Severity", "value": alert.severity.value.upper(), "short": True},
                        {"title": "Source", "value": alert.source, "short": True},
                        {"title": "Timestamp", "value": alert.timestamp.isoformat(), "short": True},
                        {"title": "Labels", "value": json.dumps(alert.labels), "short": False}
                    ],
                    "footer": "Ultimate Launch Planning System",
                    "ts": int(alert.timestamp.timestamp())
                }]
            }
            
            response = requests.post(self.webhook_url, json=payload, timeout=10)
            response.raise_for_status()
            
            logger.info(f"Slack notification sent for alert {alert.id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to send Slack notification: {e}")
            return False

class WebhookNotificationChannel(NotificationChannel):
    """Generic webhook notification channel"""
    
    def __init__(self, webhook_url: str, headers: Dict[str, str] = None):
        self.webhook_url = webhook_url
        self.headers = headers or {"Content-Type": "application/json"}
    
    def send(self, alert: Alert) -> bool:
        """Send webhook notification"""
        try:
            payload = alert.to_dict()
            response = requests.post(self.webhook_url, json=payload, headers=self.headers, timeout=10)
            response.raise_for_status()
            
            logger.info(f"Webhook notification sent for alert {alert.id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to send webhook notification: {e}")
            return False

class AlertManager:
    """Main alert management system"""
    
    def __init__(self):
        self.alerts: Dict[str, Alert] = {}
        self.rules: List[AlertRule] = []
        self.channels: List[NotificationChannel] = []
        self.alert_history: List[Alert] = []
        self.lock = threading.RLock()
        self.last_rule_evaluation: Dict[str, datetime] = {}
        
        # Start background monitoring
        self.monitor_thread = threading.Thread(target=self._monitor_loop, daemon=True)
        self.monitor_thread.start()
    
    def add_rule(self, rule: AlertRule):
        """Add an alert rule"""
        with self.lock:
            self.rules.append(rule)
            logger.info(f"Added alert rule: {rule.name}")
    
    def add_channel(self, channel: NotificationChannel):
        """Add a notification channel"""
        with self.lock:
            self.channels.append(channel)
            logger.info(f"Added notification channel: {type(channel).__name__}")
    
    def create_alert(self, title: str, description: str, severity: AlertSeverity, 
                    source: str, labels: Dict[str, str] = None) -> Alert:
        """Create a new alert"""
        alert_id = f"{source}_{int(time.time())}"
        
        alert = Alert(
            id=alert_id,
            title=title,
            description=description,
            severity=severity,
            status=AlertStatus.ACTIVE,
            source=source,
            timestamp=datetime.now(),
            labels=labels or {}
        )
        
        with self.lock:
            self.alerts[alert_id] = alert
            self.alert_history.append(alert)
        
        # Send notifications
        self._send_notifications(alert)
        
        logger.warning(f"Alert created: {alert_id} - {title}")
        return alert
    
    def acknowledge_alert(self, alert_id: str, acknowledged_by: str) -> bool:
        """Acknowledge an alert"""
        with self.lock:
            if alert_id in self.alerts:
                alert = self.alerts[alert_id]
                alert.status = AlertStatus.ACKNOWLEDGED
                alert.acknowledged_by = acknowledged_by
                alert.acknowledged_at = datetime.now()
                logger.info(f"Alert {alert_id} acknowledged by {acknowledged_by}")
                return True
        return False
    
    def resolve_alert(self, alert_id: str) -> bool:
        """Resolve an alert"""
        with self.lock:
            if alert_id in self.alerts:
                alert = self.alerts[alert_id]
                alert.status = AlertStatus.RESOLVED
                alert.resolved_at = datetime.now()
                logger.info(f"Alert {alert_id} resolved")
                return True
        return False
    
    def get_active_alerts(self) -> List[Alert]:
        """Get all active alerts"""
        with self.lock:
            return [alert for alert in self.alerts.values() if alert.status == AlertStatus.ACTIVE]
    
    def get_alerts_by_severity(self, severity: AlertSeverity) -> List[Alert]:
        """Get alerts by severity"""
        with self.lock:
            return [alert for alert in self.alerts.values() if alert.severity == severity]
    
    def evaluate_rules(self, metrics: Dict[str, Any]):
        """Evaluate all alert rules against current metrics"""
        with self.lock:
            for rule in self.rules:
                if not rule.enabled:
                    continue
                
                # Check cooldown
                last_eval = self.last_rule_evaluation.get(rule.name)
                if last_eval and datetime.now() - last_eval < timedelta(minutes=rule.cooldown_minutes):
                    continue
                
                try:
                    if rule.evaluate(metrics):
                        # Check if we already have an active alert for this rule
                        existing_alert = None
                        for alert in self.alerts.values():
                            if (alert.source == rule.name and 
                                alert.status == AlertStatus.ACTIVE and
                                datetime.now() - alert.timestamp < timedelta(minutes=rule.cooldown_minutes)):
                                existing_alert = alert
                                break
                        
                        if not existing_alert:
                            self.create_alert(
                                title=f"Rule Triggered: {rule.name}",
                                description=rule.description,
                                severity=rule.severity,
                                source=rule.name,
                                labels={"rule": rule.name, "condition": rule.condition}
                            )
                    
                    self.last_rule_evaluation[rule.name] = datetime.now()
                    
                except Exception as e:
                    logger.error(f"Error evaluating rule {rule.name}: {e}")
    
    def _send_notifications(self, alert: Alert):
        """Send notifications for an alert"""
        for channel in self.channels:
            try:
                channel.send(alert)
            except Exception as e:
                logger.error(f"Failed to send notification via {type(channel).__name__}: {e}")
    
    def _monitor_loop(self):
        """Background monitoring loop"""
        while True:
            try:
                # Check for escalation
                self._check_escalations()
                time.sleep(60)  # Check every minute
            except Exception as e:
                logger.error(f"Error in monitoring loop: {e}")
                time.sleep(300)  # Wait 5 minutes on error
    
    def _check_escalations(self):
        """Check for alerts that need escalation"""
        with self.lock:
            for alert in self.alerts.values():
                if (alert.status == AlertStatus.ACTIVE and 
                    alert.severity in [AlertSeverity.ERROR, AlertSeverity.CRITICAL]):
                    
                    # Find the rule for this alert
                    rule = None
                    for r in self.rules:
                        if r.name == alert.source:
                            rule = r
                            break
                    
                    if rule and datetime.now() - alert.timestamp > timedelta(minutes=rule.escalation_minutes):
                        # Escalate alert
                        escalated_alert = Alert(
                            id=f"{alert.id}_escalated",
                            title=f"ESCALATED: {alert.title}",
                            description=f"Alert has been escalated after {rule.escalation_minutes} minutes without acknowledgment.\n\nOriginal: {alert.description}",
                            severity=AlertSeverity.CRITICAL if alert.severity == AlertSeverity.ERROR else alert.severity,
                            status=AlertStatus.ACTIVE,
                            source=alert.source,
                            timestamp=datetime.now(),
                            labels={**alert.labels, "escalated": "true", "original_alert": alert.id}
                        )
                        
                        self.alerts[escalated_alert.id] = escalated_alert
                        self.alert_history.append(escalated_alert)
                        self._send_notifications(escalated_alert)
                        
                        logger.critical(f"Alert escalated: {alert.id} -> {escalated_alert.id}")

class LaunchAlerting:
    """Specialized alerting for launch planning"""
    
    def __init__(self, alert_manager: AlertManager):
        self.alert_manager = alert_manager
        self._setup_launch_rules()
    
    def _setup_launch_rules(self):
        """Setup launch-specific alert rules"""
        rules = [
            AlertRule(
                name="high_cpu_usage",
                condition="metrics.get('system_cpu_percent', 0) > 80",
                severity=AlertSeverity.WARNING,
                description="High CPU usage detected",
                cooldown_minutes=5
            ),
            AlertRule(
                name="high_memory_usage",
                condition="metrics.get('system_memory_percent', 0) > 85",
                severity=AlertSeverity.WARNING,
                description="High memory usage detected",
                cooldown_minutes=5
            ),
            AlertRule(
                name="launch_task_failure_rate",
                condition="metrics.get('launch_tasks_failed', 0) > 3",
                severity=AlertSeverity.ERROR,
                description="High launch task failure rate",
                cooldown_minutes=10
            ),
            AlertRule(
                name="low_success_probability",
                condition="metrics.get('launch_success_probability', 1.0) < 0.5",
                severity=AlertSeverity.WARNING,
                description="Launch success probability is low",
                cooldown_minutes=15
            ),
            AlertRule(
                name="budget_overrun",
                condition="metrics.get('launch_budget_utilization', 0) > 0.9",
                severity=AlertSeverity.ERROR,
                description="Launch budget utilization is high",
                cooldown_minutes=10
            ),
            AlertRule(
                name="phase_duration_exceeded",
                condition="metrics.get('launch_phase_duration', 0) > 3600",  # 1 hour
                severity=AlertSeverity.WARNING,
                description="Launch phase duration exceeded expected time",
                cooldown_minutes=30
            )
        ]
        
        for rule in rules:
            self.alert_manager.add_rule(rule)
    
    def alert_launch_phase_delay(self, phase: str, expected_duration: float, actual_duration: float):
        """Alert on launch phase delay"""
        delay_percentage = ((actual_duration - expected_duration) / expected_duration) * 100
        
        if delay_percentage > 50:
            severity = AlertSeverity.ERROR
        elif delay_percentage > 25:
            severity = AlertSeverity.WARNING
        else:
            return  # No alert needed
        
        self.alert_manager.create_alert(
            title=f"Launch Phase Delay: {phase}",
            description=f"Phase '{phase}' is {delay_percentage:.1f}% behind schedule. Expected: {expected_duration:.1f}s, Actual: {actual_duration:.1f}s",
            severity=severity,
            source="launch_phase_monitor",
            labels={"phase": phase, "delay_percentage": str(delay_percentage)}
        )
    
    def alert_budget_concern(self, allocated: float, spent: float, phase: str):
        """Alert on budget concerns"""
        utilization = spent / allocated if allocated > 0 else 0
        
        if utilization > 0.95:
            severity = AlertSeverity.CRITICAL
            title = "Critical Budget Overrun"
        elif utilization > 0.8:
            severity = AlertSeverity.ERROR
            title = "High Budget Utilization"
        elif utilization > 0.6:
            severity = AlertSeverity.WARNING
            title = "Budget Utilization Warning"
        else:
            return  # No alert needed
        
        self.alert_manager.create_alert(
            title=title,
            description=f"Budget utilization at {utilization:.1%} in phase '{phase}'. Allocated: ${allocated:,.2f}, Spent: ${spent:,.2f}",
            severity=severity,
            source="budget_monitor",
            labels={"phase": phase, "utilization": str(utilization), "allocated": str(allocated), "spent": str(spent)}
        )
    
    def alert_ai_model_performance(self, model_name: str, accuracy: float, threshold: float = 0.8):
        """Alert on AI model performance issues"""
        if accuracy < threshold:
            severity = AlertSeverity.WARNING if accuracy > threshold * 0.7 else AlertSeverity.ERROR
            
            self.alert_manager.create_alert(
                title=f"AI Model Performance Issue: {model_name}",
                description=f"Model '{model_name}' accuracy ({accuracy:.3f}) is below threshold ({threshold:.3f})",
                severity=severity,
                source="ai_monitor",
                labels={"model": model_name, "accuracy": str(accuracy), "threshold": str(threshold)}
            )

# Global alert manager instance
_alert_manager = None

def get_alert_manager() -> AlertManager:
    """Get global alert manager instance"""
    global _alert_manager
    if _alert_manager is None:
        _alert_manager = AlertManager()
    return _alert_manager

def get_launch_alerting() -> LaunchAlerting:
    """Get global launch alerting instance"""
    return LaunchAlerting(get_alert_manager())

# Example usage
if __name__ == "__main__":
    # Initialize alerting
    alert_manager = get_alert_manager()
    launch_alerting = get_launch_alerting()
    
    # Add notification channels (example)
    # email_channel = EmailNotificationChannel(
    #     smtp_server="smtp.gmail.com",
    #     smtp_port=587,
    #     username="your-email@gmail.com",
    #     password="your-password",
    #     from_email="alerts@yourcompany.com",
    #     to_emails=["admin@yourcompany.com"]
    # )
    # alert_manager.add_channel(email_channel)
    
    # Test alerts
    launch_alerting.alert_launch_phase_delay("pre_launch", 3600, 5400)  # 50% delay
    launch_alerting.alert_budget_concern(100000, 85000, "pre_launch")  # 85% utilization
    launch_alerting.alert_ai_model_performance("success_predictor", 0.75, 0.8)  # Low accuracy
    
    # Simulate metrics evaluation
    test_metrics = {
        "system_cpu_percent": 85,
        "system_memory_percent": 90,
        "launch_tasks_failed": 5,
        "launch_success_probability": 0.4,
        "launch_budget_utilization": 0.95
    }
    
    alert_manager.evaluate_rules(test_metrics)
    
    # Show active alerts
    active_alerts = alert_manager.get_active_alerts()
    print(f"Active alerts: {len(active_alerts)}")
    for alert in active_alerts:
        print(f"- {alert.title} ({alert.severity.value})")







