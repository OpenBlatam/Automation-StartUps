#!/usr/bin/env python3
"""
ClickUp Brain Monitoring System
==============================

Comprehensive monitoring and alerting system with metrics collection,
health checks, and real-time dashboards.
"""

import asyncio
import json
import time
import psutil
from typing import Any, Dict, List, Optional, Union, Callable
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from pathlib import Path
import logging
from enum import Enum
import threading
from contextlib import asynccontextmanager
import aiohttp
from aiohttp import web
import yaml

ROOT = Path(__file__).parent

class MetricType(Enum):
    """Metric types."""
    COUNTER = "counter"
    GAUGE = "gauge"
    HISTOGRAM = "histogram"
    SUMMARY = "summary"

class AlertSeverity(Enum):
    """Alert severity levels."""
    INFO = "info"
    WARNING = "warning"
    CRITICAL = "critical"
    EMERGENCY = "emergency"

class HealthStatus(Enum):
    """Health status levels."""
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"
    UNKNOWN = "unknown"

@dataclass
class Metric:
    """Metric data structure."""
    name: str
    value: float
    metric_type: MetricType
    labels: Dict[str, str] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.now)
    help_text: str = ""

@dataclass
class Alert:
    """Alert data structure."""
    id: str
    name: str
    description: str
    severity: AlertSeverity
    status: str = "firing"  # firing, resolved
    labels: Dict[str, str] = field(default_factory=dict)
    annotations: Dict[str, str] = field(default_factory=dict)
    starts_at: datetime = field(default_factory=datetime.now)
    ends_at: Optional[datetime] = None
    generator_url: str = ""

@dataclass
class HealthCheck:
    """Health check configuration."""
    name: str
    check_function: Callable
    interval: int = 30  # seconds
    timeout: int = 10  # seconds
    retries: int = 3
    enabled: bool = True
    labels: Dict[str, str] = field(default_factory=dict)

@dataclass
class AlertRule:
    """Alert rule configuration."""
    name: str
    expression: str
    severity: AlertSeverity
    description: str
    runbook_url: str = ""
    labels: Dict[str, str] = field(default_factory=dict)
    annotations: Dict[str, str] = field(default_factory=dict)
    for_duration: int = 0  # seconds
    enabled: bool = True

class MetricsCollector:
    """Metrics collection and storage."""
    
    def __init__(self, retention_days: int = 30):
        self.retention_days = retention_days
        self.metrics: Dict[str, List[Metric]] = {}
        self.logger = logging.getLogger("metrics_collector")
        self._lock = threading.RLock()
        self._cleanup_task = None
    
    def add_metric(self, metric: Metric) -> None:
        """Add metric to collector."""
        with self._lock:
            if metric.name not in self.metrics:
                self.metrics[metric.name] = []
            
            self.metrics[metric.name].append(metric)
            
            # Keep only recent metrics
            cutoff_time = datetime.now() - timedelta(days=self.retention_days)
            self.metrics[metric.name] = [
                m for m in self.metrics[metric.name] 
                if m.timestamp > cutoff_time
            ]
    
    def get_metric(self, name: str, labels: Dict[str, str] = None) -> List[Metric]:
        """Get metrics by name and optional labels."""
        with self._lock:
            if name not in self.metrics:
                return []
            
            metrics = self.metrics[name]
            
            if labels:
                filtered_metrics = []
                for metric in metrics:
                    if all(metric.labels.get(k) == v for k, v in labels.items()):
                        filtered_metrics.append(metric)
                return filtered_metrics
            
            return metrics.copy()
    
    def get_metric_summary(self, name: str, time_range: timedelta = timedelta(hours=1)) -> Dict[str, Any]:
        """Get metric summary for time range."""
        with self._lock:
            if name not in self.metrics:
                return {}
            
            cutoff_time = datetime.now() - time_range
            recent_metrics = [
                m for m in self.metrics[name] 
                if m.timestamp > cutoff_time
            ]
            
            if not recent_metrics:
                return {}
            
            values = [m.value for m in recent_metrics]
            
            return {
                'count': len(values),
                'min': min(values),
                'max': max(values),
                'avg': sum(values) / len(values),
                'latest': values[-1] if values else None,
                'time_range': time_range.total_seconds()
            }
    
    def list_metrics(self) -> List[str]:
        """List all metric names."""
        with self._lock:
            return list(self.metrics.keys())
    
    async def start_cleanup(self) -> None:
        """Start periodic cleanup of old metrics."""
        if self._cleanup_task:
            return
        
        async def cleanup_loop():
            while True:
                try:
                    await asyncio.sleep(3600)  # Run every hour
                    self._cleanup_old_metrics()
                except Exception as e:
                    self.logger.error(f"Error in metrics cleanup: {e}")
        
        self._cleanup_task = asyncio.create_task(cleanup_loop())
    
    def _cleanup_old_metrics(self) -> None:
        """Remove old metrics."""
        with self._lock:
            cutoff_time = datetime.now() - timedelta(days=self.retention_days)
            
            for metric_name in list(self.metrics.keys()):
                self.metrics[metric_name] = [
                    m for m in self.metrics[metric_name] 
                    if m.timestamp > cutoff_time
                ]
                
                # Remove empty metric lists
                if not self.metrics[metric_name]:
                    del self.metrics[metric_name]

class AlertManager:
    """Alert management and notification."""
    
    def __init__(self):
        self.alerts: Dict[str, Alert] = {}
        self.rules: Dict[str, AlertRule] = {}
        self.notification_channels: List[Callable] = []
        self.logger = logging.getLogger("alert_manager")
        self._lock = threading.RLock()
        self._evaluation_task = None
    
    def add_rule(self, rule: AlertRule) -> None:
        """Add alert rule."""
        with self._lock:
            self.rules[rule.name] = rule
            self.logger.info(f"Added alert rule: {rule.name}")
    
    def remove_rule(self, rule_name: str) -> None:
        """Remove alert rule."""
        with self._lock:
            if rule_name in self.rules:
                del self.rules[rule_name]
                self.logger.info(f"Removed alert rule: {rule_name}")
    
    def add_notification_channel(self, channel: Callable) -> None:
        """Add notification channel."""
        self.notification_channels.append(channel)
        self.logger.info("Added notification channel")
    
    async def evaluate_rules(self, metrics_collector: MetricsCollector) -> None:
        """Evaluate alert rules against metrics."""
        with self._lock:
            active_rules = [rule for rule in self.rules.values() if rule.enabled]
        
        for rule in active_rules:
            try:
                if await self._evaluate_rule(rule, metrics_collector):
                    await self._fire_alert(rule)
                else:
                    await self._resolve_alert(rule.name)
            except Exception as e:
                self.logger.error(f"Error evaluating rule {rule.name}: {e}")
    
    async def _evaluate_rule(self, rule: AlertRule, metrics_collector: MetricsCollector) -> bool:
        """Evaluate a single alert rule."""
        # Simple expression evaluation - can be extended with more complex logic
        try:
            # Parse expression (simplified)
            if ">" in rule.expression:
                parts = rule.expression.split(">")
                metric_name = parts[0].strip()
                threshold = float(parts[1].strip())
                
                summary = metrics_collector.get_metric_summary(metric_name)
                if summary and summary.get('latest') is not None:
                    return summary['latest'] > threshold
            
            elif "<" in rule.expression:
                parts = rule.expression.split("<")
                metric_name = parts[0].strip()
                threshold = float(parts[1].strip())
                
                summary = metrics_collector.get_metric_summary(metric_name)
                if summary and summary.get('latest') is not None:
                    return summary['latest'] < threshold
            
            return False
            
        except Exception as e:
            self.logger.error(f"Error parsing expression {rule.expression}: {e}")
            return False
    
    async def _fire_alert(self, rule: AlertRule) -> None:
        """Fire an alert."""
        alert_id = f"{rule.name}-{int(time.time())}"
        
        if alert_id in self.alerts:
            return  # Alert already firing
        
        alert = Alert(
            id=alert_id,
            name=rule.name,
            description=rule.description,
            severity=rule.severity,
            labels=rule.labels.copy(),
            annotations=rule.annotations.copy(),
            generator_url=rule.runbook_url
        )
        
        with self._lock:
            self.alerts[alert_id] = alert
        
        self.logger.warning(f"Alert fired: {rule.name}")
        
        # Send notifications
        await self._send_notifications(alert)
    
    async def _resolve_alert(self, rule_name: str) -> None:
        """Resolve an alert."""
        with self._lock:
            alerts_to_resolve = [
                alert for alert in self.alerts.values()
                if alert.name == rule_name and alert.status == "firing"
            ]
        
        for alert in alerts_to_resolve:
            alert.status = "resolved"
            alert.ends_at = datetime.now()
            
            self.logger.info(f"Alert resolved: {alert.name}")
            
            # Send resolution notifications
            await self._send_notifications(alert)
    
    async def _send_notifications(self, alert: Alert) -> None:
        """Send notifications to all channels."""
        for channel in self.notification_channels:
            try:
                await channel(alert)
            except Exception as e:
                self.logger.error(f"Error sending notification: {e}")
    
    def get_active_alerts(self) -> List[Alert]:
        """Get all active alerts."""
        with self._lock:
            return [alert for alert in self.alerts.values() if alert.status == "firing"]
    
    def get_alert_history(self, hours: int = 24) -> List[Alert]:
        """Get alert history."""
        cutoff_time = datetime.now() - timedelta(hours=hours)
        
        with self._lock:
            return [
                alert for alert in self.alerts.values()
                if alert.starts_at > cutoff_time
            ]
    
    async def start_evaluation(self, metrics_collector: MetricsCollector, interval: int = 30) -> None:
        """Start periodic rule evaluation."""
        if self._evaluation_task:
            return
        
        async def evaluation_loop():
            while True:
                try:
                    await self.evaluate_rules(metrics_collector)
                    await asyncio.sleep(interval)
                except Exception as e:
                    self.logger.error(f"Error in alert evaluation: {e}")
        
        self._evaluation_task = asyncio.create_task(evaluation_loop())

class HealthChecker:
    """Health check management."""
    
    def __init__(self):
        self.health_checks: Dict[str, HealthCheck] = {}
        self.health_status: Dict[str, HealthStatus] = {}
        self.logger = logging.getLogger("health_checker")
        self._lock = threading.RLock()
        self._check_tasks: Dict[str, asyncio.Task] = {}
    
    def add_health_check(self, health_check: HealthCheck) -> None:
        """Add health check."""
        with self._lock:
            self.health_checks[health_check.name] = health_check
            self.health_status[health_check.name] = HealthStatus.UNKNOWN
        
        self.logger.info(f"Added health check: {health_check.name}")
    
    def remove_health_check(self, name: str) -> None:
        """Remove health check."""
        with self._lock:
            if name in self.health_checks:
                del self.health_checks[name]
                del self.health_status[name]
        
        # Cancel check task
        if name in self._check_tasks:
            self._check_tasks[name].cancel()
            del self._check_tasks[name]
        
        self.logger.info(f"Removed health check: {name}")
    
    async def start_health_checks(self) -> None:
        """Start all health checks."""
        with self._lock:
            for name, health_check in self.health_checks.items():
                if health_check.enabled and name not in self._check_tasks:
                    task = asyncio.create_task(self._run_health_check(name, health_check))
                    self._check_tasks[name] = task
    
    async def stop_health_checks(self) -> None:
        """Stop all health checks."""
        for task in self._check_tasks.values():
            task.cancel()
        
        await asyncio.gather(*self._check_tasks.values(), return_exceptions=True)
        self._check_tasks.clear()
    
    async def _run_health_check(self, name: str, health_check: HealthCheck) -> None:
        """Run a single health check."""
        while True:
            try:
                # Run health check with timeout
                result = await asyncio.wait_for(
                    health_check.check_function(),
                    timeout=health_check.timeout
                )
                
                # Update status based on result
                if result is True:
                    new_status = HealthStatus.HEALTHY
                elif result is False:
                    new_status = HealthStatus.UNHEALTHY
                else:
                    new_status = HealthStatus.DEGRADED
                
                with self._lock:
                    if self.health_status[name] != new_status:
                        self.health_status[name] = new_status
                        self.logger.info(f"Health check {name} status changed to {new_status.value}")
                
                await asyncio.sleep(health_check.interval)
                
            except asyncio.TimeoutError:
                with self._lock:
                    self.health_status[name] = HealthStatus.UNHEALTHY
                self.logger.warning(f"Health check {name} timed out")
                await asyncio.sleep(health_check.interval)
                
            except Exception as e:
                with self._lock:
                    self.health_status[name] = HealthStatus.UNHEALTHY
                self.logger.error(f"Health check {name} failed: {e}")
                await asyncio.sleep(health_check.interval)
    
    def get_health_status(self, name: str = None) -> Union[HealthStatus, Dict[str, HealthStatus]]:
        """Get health status."""
        with self._lock:
            if name:
                return self.health_status.get(name, HealthStatus.UNKNOWN)
            return self.health_status.copy()
    
    def get_overall_health(self) -> HealthStatus:
        """Get overall system health."""
        with self._lock:
            if not self.health_status:
                return HealthStatus.UNKNOWN
            
            statuses = list(self.health_status.values())
            
            if HealthStatus.UNHEALTHY in statuses:
                return HealthStatus.UNHEALTHY
            elif HealthStatus.DEGRADED in statuses:
                return HealthStatus.DEGRADED
            elif all(s == HealthStatus.HEALTHY for s in statuses):
                return HealthStatus.HEALTHY
            else:
                return HealthStatus.UNKNOWN

class MonitoringDashboard:
    """Web-based monitoring dashboard."""
    
    def __init__(self, metrics_collector: MetricsCollector, alert_manager: AlertManager, health_checker: HealthChecker):
        self.metrics_collector = metrics_collector
        self.alert_manager = alert_manager
        self.health_checker = health_checker
        self.logger = logging.getLogger("monitoring_dashboard")
    
    async def create_app(self) -> web.Application:
        """Create web application for dashboard."""
        app = web.Application()
        
        # Add routes
        app.router.add_get('/', self._dashboard_handler)
        app.router.add_get('/metrics', self._metrics_handler)
        app.router.add_get('/alerts', self._alerts_handler)
        app.router.add_get('/health', self._health_handler)
        app.router.add_get('/api/metrics/{metric_name}', self._metric_detail_handler)
        
        return app
    
    async def _dashboard_handler(self, request: web.Request) -> web.Response:
        """Dashboard main page."""
        html = """
        <!DOCTYPE html>
        <html>
        <head>
            <title>ClickUp Brain Monitoring</title>
            <style>
                body { font-family: Arial, sans-serif; margin: 20px; }
                .metric { margin: 10px 0; padding: 10px; border: 1px solid #ccc; }
                .alert { margin: 10px 0; padding: 10px; border-left: 4px solid #f00; background: #ffe6e6; }
                .health { margin: 10px 0; padding: 10px; border: 1px solid #ccc; }
                .healthy { border-left: 4px solid #0f0; background: #e6ffe6; }
                .unhealthy { border-left: 4px solid #f00; background: #ffe6e6; }
                .degraded { border-left: 4px solid #ff0; background: #fff9e6; }
            </style>
        </head>
        <body>
            <h1>ClickUp Brain Monitoring Dashboard</h1>
            
            <h2>System Health</h2>
            <div id="health"></div>
            
            <h2>Active Alerts</h2>
            <div id="alerts"></div>
            
            <h2>Metrics</h2>
            <div id="metrics"></div>
            
            <script>
                async function loadData() {
                    // Load health status
                    const healthResponse = await fetch('/health');
                    const health = await healthResponse.json();
                    document.getElementById('health').innerHTML = formatHealth(health);
                    
                    // Load alerts
                    const alertsResponse = await fetch('/alerts');
                    const alerts = await alertsResponse.json();
                    document.getElementById('alerts').innerHTML = formatAlerts(alerts);
                    
                    // Load metrics
                    const metricsResponse = await fetch('/metrics');
                    const metrics = await metricsResponse.json();
                    document.getElementById('metrics').innerHTML = formatMetrics(metrics);
                }
                
                function formatHealth(health) {
                    let html = '';
                    for (const [name, status] of Object.entries(health)) {
                        html += `<div class="health ${status}">${name}: ${status}</div>`;
                    }
                    return html;
                }
                
                function formatAlerts(alerts) {
                    if (alerts.length === 0) {
                        return '<div>No active alerts</div>';
                    }
                    
                    let html = '';
                    for (const alert of alerts) {
                        html += `<div class="alert">${alert.name}: ${alert.description}</div>`;
                    }
                    return html;
                }
                
                function formatMetrics(metrics) {
                    let html = '';
                    for (const metric of metrics) {
                        html += `<div class="metric">${metric}: <a href="/api/metrics/${metric}">View Details</a></div>`;
                    }
                    return html;
                }
                
                // Load data on page load and refresh every 30 seconds
                loadData();
                setInterval(loadData, 30000);
            </script>
        </body>
        </html>
        """
        
        return web.Response(text=html, content_type='text/html')
    
    async def _metrics_handler(self, request: web.Request) -> web.Response:
        """List all metrics."""
        metrics = self.metrics_collector.list_metrics()
        return web.json_response(metrics)
    
    async def _alerts_handler(self, request: web.Request) -> web.Response:
        """Get active alerts."""
        alerts = self.alert_manager.get_active_alerts()
        alert_data = [
            {
                'id': alert.id,
                'name': alert.name,
                'description': alert.description,
                'severity': alert.severity.value,
                'status': alert.status,
                'starts_at': alert.starts_at.isoformat()
            }
            for alert in alerts
        ]
        return web.json_response(alert_data)
    
    async def _health_handler(self, request: web.Request) -> web.Response:
        """Get health status."""
        health = self.health_checker.get_health_status()
        health_data = {name: status.value for name, status in health.items()}
        return web.json_response(health_data)
    
    async def _metric_detail_handler(self, request: web.Request) -> web.Response:
        """Get metric details."""
        metric_name = request.match_info['metric_name']
        summary = self.metrics_collector.get_metric_summary(metric_name)
        return web.json_response(summary)

class MonitoringSystem:
    """Main monitoring system."""
    
    def __init__(self):
        self.metrics_collector = MetricsCollector()
        self.alert_manager = AlertManager()
        self.health_checker = HealthChecker()
        self.dashboard = MonitoringDashboard(
            self.metrics_collector,
            self.alert_manager,
            self.health_checker
        )
        self.logger = logging.getLogger("monitoring_system")
        self._running = False
    
    def add_metric(self, name: str, value: float, metric_type: MetricType = MetricType.GAUGE, 
                   labels: Dict[str, str] = None, help_text: str = "") -> None:
        """Add metric."""
        metric = Metric(
            name=name,
            value=value,
            metric_type=metric_type,
            labels=labels or {},
            help_text=help_text
        )
        self.metrics_collector.add_metric(metric)
    
    def add_alert_rule(self, rule: AlertRule) -> None:
        """Add alert rule."""
        self.alert_manager.add_rule(rule)
    
    def add_health_check(self, health_check: HealthCheck) -> None:
        """Add health check."""
        self.health_checker.add_health_check(health_check)
    
    def add_notification_channel(self, channel: Callable) -> None:
        """Add notification channel."""
        self.alert_manager.add_notification_channel(channel)
    
    async def start(self, dashboard_port: int = 8080) -> None:
        """Start monitoring system."""
        if self._running:
            return
        
        self._running = True
        
        # Start background tasks
        await self.metrics_collector.start_cleanup()
        await self.alert_manager.start_evaluation(self.metrics_collector)
        await self.health_checker.start_health_checks()
        
        # Start dashboard
        app = await self.dashboard.create_app()
        runner = web.AppRunner(app)
        await runner.setup()
        
        site = web.TCPSite(runner, '0.0.0.0', dashboard_port)
        await site.start()
        
        self.logger.info(f"Monitoring system started on port {dashboard_port}")
    
    async def stop(self) -> None:
        """Stop monitoring system."""
        if not self._running:
            return
        
        self._running = False
        
        # Stop background tasks
        await self.health_checker.stop_health_checks()
        
        if self.alert_manager._evaluation_task:
            self.alert_manager._evaluation_task.cancel()
        
        if self.metrics_collector._cleanup_task:
            self.metrics_collector._cleanup_task.cancel()
        
        self.logger.info("Monitoring system stopped")
    
    def get_system_status(self) -> Dict[str, Any]:
        """Get overall system status."""
        return {
            'overall_health': self.health_checker.get_overall_health().value,
            'active_alerts': len(self.alert_manager.get_active_alerts()),
            'total_metrics': len(self.metrics_collector.list_metrics()),
            'health_checks': len(self.health_checker.health_checks),
            'alert_rules': len(self.alert_manager.rules)
        }

# Global monitoring system
monitoring_system = MonitoringSystem()

def get_monitoring_system() -> MonitoringSystem:
    """Get global monitoring system."""
    return monitoring_system

async def start_monitoring(dashboard_port: int = 8080) -> None:
    """Start global monitoring system."""
    await monitoring_system.start(dashboard_port)

async def stop_monitoring() -> None:
    """Stop global monitoring system."""
    await monitoring_system.stop()

if __name__ == "__main__":
    # Demo monitoring system
    print("ClickUp Brain Monitoring System Demo")
    print("=" * 50)
    
    # Setup logging
    logging.basicConfig(level=logging.INFO)
    
    async def demo():
        # Get monitoring system
        monitoring = get_monitoring_system()
        
        # Add some metrics
        monitoring.add_metric("cpu_usage", 75.5, MetricType.GAUGE, {"host": "server1"})
        monitoring.add_metric("memory_usage", 60.2, MetricType.GAUGE, {"host": "server1"})
        monitoring.add_metric("request_count", 1000, MetricType.COUNTER, {"endpoint": "/api"})
        
        # Add alert rules
        cpu_rule = AlertRule(
            name="high_cpu_usage",
            expression="cpu_usage > 80",
            severity=AlertSeverity.WARNING,
            description="CPU usage is above 80%"
        )
        monitoring.add_alert_rule(cpu_rule)
        
        memory_rule = AlertRule(
            name="high_memory_usage",
            expression="memory_usage > 90",
            severity=AlertSeverity.CRITICAL,
            description="Memory usage is above 90%"
        )
        monitoring.add_alert_rule(memory_rule)
        
        # Add health checks
        async def database_health():
            # Simulate database health check
            return True
        
        async def api_health():
            # Simulate API health check
            return True
        
        monitoring.add_health_check(HealthCheck("database", database_health))
        monitoring.add_health_check(HealthCheck("api", api_health))
        
        # Add notification channel
        async def console_notification(alert: Alert):
            print(f"ALERT: {alert.name} - {alert.description} [{alert.severity.value}]")
        
        monitoring.add_notification_channel(console_notification)
        
        # Start monitoring
        await monitoring.start(dashboard_port=8080)
        
        print("Monitoring system started!")
        print("Dashboard: http://localhost:8080")
        print("Metrics: http://localhost:8080/metrics")
        print("Health: http://localhost:8080/health")
        print("Alerts: http://localhost:8080/alerts")
        
        # Simulate some activity
        for i in range(10):
            await asyncio.sleep(5)
            
            # Add more metrics
            monitoring.add_metric("cpu_usage", 70 + i, MetricType.GAUGE, {"host": "server1"})
            monitoring.add_metric("memory_usage", 50 + i * 2, MetricType.GAUGE, {"host": "server1"})
            
            # Check system status
            status = monitoring.get_system_status()
            print(f"System status: {status}")
        
        # Stop monitoring
        await monitoring.stop()
        
        print("\nMonitoring system demo completed!")
    
    asyncio.run(demo())









