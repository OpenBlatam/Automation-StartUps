#!/usr/bin/env python3
"""
ClickUp Brain Real-time Analytics System
========================================

Real-time analytics and streaming data processing with live dashboards,
event processing, and instant insights.
"""

import asyncio
import json
import numpy as np
import pandas as pd
from typing import Any, Dict, List, Optional, Union, Callable, AsyncGenerator
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from pathlib import Path
import logging
from enum import Enum
import threading
from contextlib import asynccontextmanager
import uuid
from abc import ABC, abstractmethod
import websockets
import aiohttp
from collections import deque, defaultdict
import time
import sqlite3
import redis
import kafka
from kafka import KafkaProducer, KafkaConsumer
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import dash
from dash import dcc, html, Input, Output, callback
import dash_bootstrap_components as dbc
from scipy import stats
from sklearn.cluster import DBSCAN
from sklearn.preprocessing import StandardScaler
import cv2
import base64
import io
from PIL import Image

ROOT = Path(__file__).parent

class StreamType(Enum):
    """Stream data types."""
    METRICS = "metrics"
    EVENTS = "events"
    LOGS = "logs"
    TRACES = "traces"
    ALERTS = "alerts"
    USER_ACTIVITY = "user_activity"
    SYSTEM_PERFORMANCE = "system_performance"
    BUSINESS_METRICS = "business_metrics"

class ProcessingMode(Enum):
    """Data processing modes."""
    BATCH = "batch"
    STREAMING = "streaming"
    MICRO_BATCH = "micro_batch"
    REAL_TIME = "real_time"

class AlertSeverity(Enum):
    """Alert severity levels."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

@dataclass
class StreamConfig:
    """Stream configuration."""
    name: str
    stream_type: StreamType
    processing_mode: ProcessingMode
    buffer_size: int = 1000
    batch_size: int = 100
    window_size: int = 60  # seconds
    retention_period: int = 86400  # seconds
    filters: Dict[str, Any] = field(default_factory=dict)
    transformations: List[str] = field(default_factory=list)
    aggregations: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class DataPoint:
    """Real-time data point."""
    timestamp: datetime
    value: Any
    metric_name: str
    tags: Dict[str, str] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class Event:
    """Real-time event."""
    id: str
    timestamp: datetime
    event_type: str
    source: str
    data: Dict[str, Any]
    severity: AlertSeverity = AlertSeverity.LOW
    tags: Dict[str, str] = field(default_factory=dict)

@dataclass
class Alert:
    """Real-time alert."""
    id: str
    timestamp: datetime
    severity: AlertSeverity
    message: str
    metric_name: str
    threshold: float
    current_value: float
    tags: Dict[str, str] = field(default_factory=dict)
    resolved: bool = False
    resolved_at: Optional[datetime] = None

@dataclass
class AggregationResult:
    """Aggregation result."""
    metric_name: str
    aggregation_type: str
    value: float
    timestamp: datetime
    window_size: int
    count: int
    tags: Dict[str, str] = field(default_factory=dict)

class StreamProcessor(ABC):
    """Base class for stream processors."""
    
    def __init__(self, config: StreamConfig):
        self.config = config
        self.logger = logging.getLogger(f"stream_processor_{config.name}")
        self.buffer = deque(maxlen=config.buffer_size)
        self.subscribers: List[Callable] = []
        self.is_running = False
        self._lock = threading.RLock()
    
    @abstractmethod
    async def process_data(self, data: Any) -> Any:
        """Process incoming data."""
        pass
    
    async def add_data(self, data: Any) -> None:
        """Add data to stream."""
        with self._lock:
            processed_data = await self.process_data(data)
            self.buffer.append(processed_data)
            
            # Notify subscribers
            for subscriber in self.subscribers:
                try:
                    await subscriber(processed_data)
                except Exception as e:
                    self.logger.error(f"Subscriber error: {e}")
    
    def subscribe(self, callback: Callable) -> None:
        """Subscribe to stream updates."""
        self.subscribers.append(callback)
    
    def unsubscribe(self, callback: Callable) -> None:
        """Unsubscribe from stream updates."""
        if callback in self.subscribers:
            self.subscribers.remove(callback)
    
    def get_latest_data(self, count: int = 100) -> List[Any]:
        """Get latest data points."""
        with self._lock:
            return list(self.buffer)[-count:]
    
    async def start(self) -> None:
        """Start stream processing."""
        self.is_running = True
        self.logger.info(f"Started stream processor: {self.config.name}")
    
    async def stop(self) -> None:
        """Stop stream processing."""
        self.is_running = False
        self.logger.info(f"Stopped stream processor: {self.config.name}")

class MetricsProcessor(StreamProcessor):
    """Metrics stream processor."""
    
    async def process_data(self, data: DataPoint) -> DataPoint:
        """Process metrics data."""
        # Apply transformations
        for transformation in self.config.transformations:
            if transformation == "normalize":
                data.value = self._normalize_value(data.value)
            elif transformation == "log_transform":
                data.value = np.log(data.value + 1)
            elif transformation == "smooth":
                data.value = self._smooth_value(data.value)
        
        return data
    
    def _normalize_value(self, value: float) -> float:
        """Normalize value using z-score."""
        if len(self.buffer) < 10:
            return value
        
        values = [dp.value for dp in self.buffer if isinstance(dp.value, (int, float))]
        if not values:
            return value
        
        mean = np.mean(values)
        std = np.std(values)
        
        if std == 0:
            return value
        
        return (value - mean) / std
    
    def _smooth_value(self, value: float) -> float:
        """Apply exponential smoothing."""
        if not self.buffer:
            return value
        
        alpha = 0.3  # Smoothing factor
        last_value = self.buffer[-1].value if isinstance(self.buffer[-1].value, (int, float)) else value
        
        return alpha * value + (1 - alpha) * last_value
    
    async def calculate_aggregations(self) -> List[AggregationResult]:
        """Calculate aggregations for current window."""
        if not self.buffer:
            return []
        
        current_time = datetime.now()
        window_start = current_time - timedelta(seconds=self.config.window_size)
        
        # Filter data within window
        window_data = [
            dp for dp in self.buffer 
            if dp.timestamp >= window_start and isinstance(dp.value, (int, float))
        ]
        
        if not window_data:
            return []
        
        values = [dp.value for dp in window_data]
        results = []
        
        for aggregation in self.config.aggregations:
            if aggregation == "mean":
                result_value = np.mean(values)
            elif aggregation == "median":
                result_value = np.median(values)
            elif aggregation == "std":
                result_value = np.std(values)
            elif aggregation == "min":
                result_value = np.min(values)
            elif aggregation == "max":
                result_value = np.max(values)
            elif aggregation == "sum":
                result_value = np.sum(values)
            elif aggregation == "count":
                result_value = len(values)
            else:
                continue
            
            result = AggregationResult(
                metric_name=window_data[0].metric_name,
                aggregation_type=aggregation,
                value=result_value,
                timestamp=current_time,
                window_size=self.config.window_size,
                count=len(values)
            )
            results.append(result)
        
        return results

class EventProcessor(StreamProcessor):
    """Event stream processor."""
    
    async def process_data(self, data: Event) -> Event:
        """Process event data."""
        # Apply event transformations
        for transformation in self.config.transformations:
            if transformation == "enrich":
                data = await self._enrich_event(data)
            elif transformation == "filter":
                data = await self._filter_event(data)
            elif transformation == "normalize":
                data = await self._normalize_event(data)
        
        return data
    
    async def _enrich_event(self, event: Event) -> Event:
        """Enrich event with additional data."""
        # Add geolocation if IP address is present
        if 'ip_address' in event.data:
            # This would typically call a geolocation service
            event.tags['country'] = 'US'  # Placeholder
            event.tags['city'] = 'New York'  # Placeholder
        
        # Add user agent parsing
        if 'user_agent' in event.data:
            # This would typically parse user agent
            event.tags['browser'] = 'Chrome'  # Placeholder
            event.tags['os'] = 'Windows'  # Placeholder
        
        return event
    
    async def _filter_event(self, event: Event) -> Event:
        """Filter event based on criteria."""
        # Apply filters from config
        for key, value in self.config.filters.items():
            if key in event.data and event.data[key] != value:
                return None  # Filter out event
        
        return event
    
    async def _normalize_event(self, event: Event) -> Event:
        """Normalize event data."""
        # Normalize event type
        event.event_type = event.event_type.lower().replace(' ', '_')
        
        # Normalize source
        event.source = event.source.lower()
        
        return event

class AlertProcessor(StreamProcessor):
    """Alert stream processor."""
    
    def __init__(self, config: StreamConfig):
        super().__init__(config)
        self.alert_rules: Dict[str, Dict[str, Any]] = {}
        self.active_alerts: Dict[str, Alert] = {}
    
    def add_alert_rule(self, metric_name: str, threshold: float, 
                      severity: AlertSeverity, condition: str = "greater_than") -> None:
        """Add alert rule."""
        self.alert_rules[metric_name] = {
            'threshold': threshold,
            'severity': severity,
            'condition': condition
        }
    
    async def process_data(self, data: DataPoint) -> Optional[Alert]:
        """Process data and generate alerts."""
        if data.metric_name not in self.alert_rules:
            return None
        
        rule = self.alert_rules[data.metric_name]
        threshold = rule['threshold']
        severity = rule['severity']
        condition = rule['condition']
        
        # Check if alert condition is met
        alert_triggered = False
        if condition == "greater_than" and data.value > threshold:
            alert_triggered = True
        elif condition == "less_than" and data.value < threshold:
            alert_triggered = True
        elif condition == "equals" and data.value == threshold:
            alert_triggered = True
        
        if alert_triggered:
            # Check if alert already exists
            alert_key = f"{data.metric_name}_{condition}_{threshold}"
            
            if alert_key not in self.active_alerts:
                # Create new alert
                alert = Alert(
                    id=str(uuid.uuid4()),
                    timestamp=datetime.now(),
                    severity=severity,
                    message=f"{data.metric_name} {condition} {threshold} (current: {data.value})",
                    metric_name=data.metric_name,
                    threshold=threshold,
                    current_value=data.value,
                    tags=data.tags
                )
                
                self.active_alerts[alert_key] = alert
                return alert
            else:
                # Update existing alert
                self.active_alerts[alert_key].current_value = data.value
                return self.active_alerts[alert_key]
        else:
            # Resolve alert if it exists
            alert_key = f"{data.metric_name}_{condition}_{threshold}"
            if alert_key in self.active_alerts:
                alert = self.active_alerts[alert_key]
                alert.resolved = True
                alert.resolved_at = datetime.now()
                del self.active_alerts[alert_key]
                return alert
        
        return None

class RealTimeAnalytics:
    """Real-time analytics engine."""
    
    def __init__(self):
        self.processors: Dict[str, StreamProcessor] = {}
        self.websocket_clients: List[websockets.WebSocketServerProtocol] = []
        self.logger = logging.getLogger("realtime_analytics")
        self._lock = threading.RLock()
    
    def add_processor(self, processor: StreamProcessor) -> None:
        """Add stream processor."""
        with self._lock:
            self.processors[processor.config.name] = processor
            processor.subscribe(self._broadcast_update)
        
        self.logger.info(f"Added processor: {processor.config.name}")
    
    async def _broadcast_update(self, data: Any) -> None:
        """Broadcast update to WebSocket clients."""
        if not self.websocket_clients:
            return
        
        message = {
            'type': 'data_update',
            'data': self._serialize_data(data),
            'timestamp': datetime.now().isoformat()
        }
        
        # Send to all connected clients
        disconnected_clients = []
        for client in self.websocket_clients:
            try:
                await client.send(json.dumps(message))
            except websockets.exceptions.ConnectionClosed:
                disconnected_clients.append(client)
            except Exception as e:
                self.logger.error(f"Error sending to client: {e}")
                disconnected_clients.append(client)
        
        # Remove disconnected clients
        for client in disconnected_clients:
            self.websocket_clients.remove(client)
    
    def _serialize_data(self, data: Any) -> Dict[str, Any]:
        """Serialize data for JSON transmission."""
        if isinstance(data, DataPoint):
            return {
                'type': 'datapoint',
                'timestamp': data.timestamp.isoformat(),
                'value': data.value,
                'metric_name': data.metric_name,
                'tags': data.tags
            }
        elif isinstance(data, Event):
            return {
                'type': 'event',
                'id': data.id,
                'timestamp': data.timestamp.isoformat(),
                'event_type': data.event_type,
                'source': data.source,
                'data': data.data,
                'severity': data.severity.value,
                'tags': data.tags
            }
        elif isinstance(data, Alert):
            return {
                'type': 'alert',
                'id': data.id,
                'timestamp': data.timestamp.isoformat(),
                'severity': data.severity.value,
                'message': data.message,
                'metric_name': data.metric_name,
                'threshold': data.threshold,
                'current_value': data.current_value,
                'resolved': data.resolved,
                'tags': data.tags
            }
        else:
            return {'type': 'unknown', 'data': str(data)}
    
    async def add_websocket_client(self, websocket: websockets.WebSocketServerProtocol) -> None:
        """Add WebSocket client for real-time updates."""
        self.websocket_clients.append(websocket)
        self.logger.info("Added WebSocket client")
    
    async def remove_websocket_client(self, websocket: websockets.WebSocketServerProtocol) -> None:
        """Remove WebSocket client."""
        if websocket in self.websocket_clients:
            self.websocket_clients.remove(websocket)
        self.logger.info("Removed WebSocket client")
    
    async def get_dashboard_data(self) -> Dict[str, Any]:
        """Get data for dashboard."""
        dashboard_data = {
            'timestamp': datetime.now().isoformat(),
            'processors': {},
            'summary': {
                'total_processors': len(self.processors),
                'active_alerts': 0,
                'total_events': 0,
                'total_metrics': 0
            }
        }
        
        for name, processor in self.processors.items():
            latest_data = processor.get_latest_data(100)
            
            processor_data = {
                'name': name,
                'type': processor.config.stream_type.value,
                'data_count': len(latest_data),
                'latest_data': [self._serialize_data(d) for d in latest_data[-10:]]
            }
            
            # Calculate aggregations for metrics
            if isinstance(processor, MetricsProcessor):
                aggregations = await processor.calculate_aggregations()
                processor_data['aggregations'] = [
                    {
                        'type': agg.aggregation_type,
                        'value': agg.value,
                        'timestamp': agg.timestamp.isoformat()
                    }
                    for agg in aggregations
                ]
            
            # Count alerts
            if isinstance(processor, AlertProcessor):
                dashboard_data['summary']['active_alerts'] += len(processor.active_alerts)
            
            dashboard_data['processors'][name] = processor_data
        
        return dashboard_data
    
    async def start_all_processors(self) -> None:
        """Start all processors."""
        for processor in self.processors.values():
            await processor.start()
    
    async def stop_all_processors(self) -> None:
        """Stop all processors."""
        for processor in self.processors.values():
            await processor.stop()

class RealTimeDashboard:
    """Real-time dashboard using Dash."""
    
    def __init__(self, analytics: RealTimeAnalytics):
        self.analytics = analytics
        self.app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])
        self._setup_layout()
        self._setup_callbacks()
    
    def _setup_layout(self):
        """Setup dashboard layout."""
        self.app.layout = dbc.Container([
            dbc.Row([
                dbc.Col([
                    html.H1("ClickUp Brain Real-time Analytics", className="text-center mb-4"),
                    dbc.Card([
                        dbc.CardBody([
                            html.H4("System Overview", className="card-title"),
                            dbc.Row([
                                dbc.Col([
                                    dbc.Card([
                                        dbc.CardBody([
                                            html.H5("Active Processors", className="card-title"),
                                            html.H3(id="processor-count", className="text-primary")
                                        ])
                                    ])
                                ], width=3),
                                dbc.Col([
                                    dbc.Card([
                                        dbc.CardBody([
                                            html.H5("Active Alerts", className="card-title"),
                                            html.H3(id="alert-count", className="text-danger")
                                        ])
                                    ])
                                ], width=3),
                                dbc.Col([
                                    dbc.Card([
                                        dbc.CardBody([
                                            html.H5("Total Events", className="card-title"),
                                            html.H3(id="event-count", className="text-info")
                                        ])
                                    ])
                                ], width=3),
                                dbc.Col([
                                    dbc.Card([
                                        dbc.CardBody([
                                            html.H5("Total Metrics", className="card-title"),
                                            html.H3(id="metric-count", className="text-success")
                                        ])
                                    ])
                                ], width=3)
                            ])
                        ])
                    ])
                ])
            ]),
            dbc.Row([
                dbc.Col([
                    dcc.Graph(id="metrics-chart")
                ], width=6),
                dbc.Col([
                    dcc.Graph(id="events-chart")
                ], width=6)
            ], className="mt-4"),
            dbc.Row([
                dbc.Col([
                    html.H4("Recent Alerts"),
                    html.Div(id="alerts-list")
                ], width=12)
            ], className="mt-4"),
            dcc.Interval(
                id='interval-component',
                interval=1000,  # Update every second
                n_intervals=0
            )
        ], fluid=True)
    
    def _setup_callbacks(self):
        """Setup dashboard callbacks."""
        @self.app.callback(
            [Output('processor-count', 'children'),
             Output('alert-count', 'children'),
             Output('event-count', 'children'),
             Output('metric-count', 'children')],
            [Input('interval-component', 'n_intervals')]
        )
        def update_summary(n):
            # This would be called asynchronously in a real implementation
            return "0", "0", "0", "0"
        
        @self.app.callback(
            Output('metrics-chart', 'figure'),
            [Input('interval-component', 'n_intervals')]
        )
        def update_metrics_chart(n):
            # Create sample chart
            fig = go.Figure()
            fig.add_trace(go.Scatter(
                x=list(range(10)),
                y=np.random.randn(10).cumsum(),
                mode='lines+markers',
                name='Sample Metric'
            ))
            fig.update_layout(title="Real-time Metrics", xaxis_title="Time", yaxis_title="Value")
            return fig
        
        @self.app.callback(
            Output('events-chart', 'figure'),
            [Input('interval-component', 'n_intervals')]
        )
        def update_events_chart(n):
            # Create sample chart
            fig = go.Figure()
            fig.add_trace(go.Bar(
                x=['Event Type 1', 'Event Type 2', 'Event Type 3'],
                y=np.random.randint(1, 100, 3),
                name='Event Count'
            ))
            fig.update_layout(title="Event Distribution", xaxis_title="Event Type", yaxis_title="Count")
            return fig
        
        @self.app.callback(
            Output('alerts-list', 'children'),
            [Input('interval-component', 'n_intervals')]
        )
        def update_alerts_list(n):
            # Create sample alerts
            alerts = [
                dbc.Alert("High CPU usage detected", color="danger"),
                dbc.Alert("Memory usage above threshold", color="warning"),
                dbc.Alert("Network latency increased", color="info")
            ]
            return alerts
    
    def run(self, host='0.0.0.0', port=8050, debug=False):
        """Run the dashboard."""
        self.app.run_server(host=host, port=port, debug=debug)

# Global real-time analytics
realtime_analytics = RealTimeAnalytics()

def get_realtime_analytics() -> RealTimeAnalytics:
    """Get global real-time analytics."""
    return realtime_analytics

async def create_metrics_processor(name: str, stream_type: StreamType = StreamType.METRICS) -> MetricsProcessor:
    """Create metrics processor."""
    config = StreamConfig(
        name=name,
        stream_type=stream_type,
        processing_mode=ProcessingMode.REAL_TIME,
        transformations=["normalize", "smooth"],
        aggregations=["mean", "std", "min", "max"]
    )
    
    processor = MetricsProcessor(config)
    realtime_analytics.add_processor(processor)
    return processor

async def create_event_processor(name: str) -> EventProcessor:
    """Create event processor."""
    config = StreamConfig(
        name=name,
        stream_type=StreamType.EVENTS,
        processing_mode=ProcessingMode.REAL_TIME,
        transformations=["enrich", "filter", "normalize"]
    )
    
    processor = EventProcessor(config)
    realtime_analytics.add_processor(processor)
    return processor

async def create_alert_processor(name: str) -> AlertProcessor:
    """Create alert processor."""
    config = StreamConfig(
        name=name,
        stream_type=StreamType.ALERTS,
        processing_mode=ProcessingMode.REAL_TIME
    )
    
    processor = AlertProcessor(config)
    realtime_analytics.add_processor(processor)
    return processor

if __name__ == "__main__":
    # Demo real-time analytics
    print("ClickUp Brain Real-time Analytics Demo")
    print("=" * 50)
    
    # Setup logging
    logging.basicConfig(level=logging.INFO)
    
    async def demo():
        # Get real-time analytics
        analytics = get_realtime_analytics()
        
        # Create processors
        metrics_processor = await create_metrics_processor("system_metrics")
        event_processor = await create_event_processor("user_events")
        alert_processor = await create_alert_processor("system_alerts")
        
        # Add alert rules
        alert_processor.add_alert_rule("cpu_usage", 80.0, AlertSeverity.HIGH, "greater_than")
        alert_processor.add_alert_rule("memory_usage", 90.0, AlertSeverity.CRITICAL, "greater_than")
        
        # Start processors
        await analytics.start_all_processors()
        
        # Simulate data
        for i in range(10):
            # Add metrics data
            metric = DataPoint(
                timestamp=datetime.now(),
                value=np.random.uniform(0, 100),
                metric_name="cpu_usage",
                tags={"host": "server1", "region": "us-east-1"}
            )
            await metrics_processor.add_data(metric)
            
            # Add event data
            event = Event(
                id=str(uuid.uuid4()),
                timestamp=datetime.now(),
                event_type="user_login",
                source="web_app",
                data={"user_id": f"user_{i}", "ip_address": "192.168.1.1"},
                severity=AlertSeverity.LOW
            )
            await event_processor.add_data(event)
            
            # Process alerts
            alert = await alert_processor.process_data(metric)
            if alert:
                print(f"Alert generated: {alert.message}")
            
            await asyncio.sleep(1)
        
        # Get dashboard data
        dashboard_data = await analytics.get_dashboard_data()
        print(f"Dashboard data: {json.dumps(dashboard_data, indent=2, default=str)}")
        
        # Stop processors
        await analytics.stop_all_processors()
        
        print("\nReal-time analytics demo completed!")
    
    asyncio.run(demo())









