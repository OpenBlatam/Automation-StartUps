#!/usr/bin/env python3
"""
Real-time Monitoring Dashboard for Frontier AI Projects
Provides live monitoring of system performance, metrics, and health.
"""

import asyncio
import json
import time
import logging
from typing import Dict, List, Any, Optional
from pathlib import Path
import sys
from datetime import datetime, timedelta
import threading
from collections import deque
import psutil
import numpy as np

# Add project paths
sys.path.append(str(Path(__file__).parent / "TruthGPT" / "brandkit"))

import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import pandas as pd
from dataclasses import dataclass, asdict
import requests
from contextlib import asynccontextmanager

# Import our modules
from brand_analyzer import ProductionBrandAnalyzer

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class SystemMetrics:
    """System metrics data structure."""
    timestamp: float
    cpu_percent: float
    memory_percent: float
    memory_used_gb: float
    memory_available_gb: float
    disk_usage_percent: float
    network_sent_mb: float
    network_recv_mb: float
    load_average: List[float]
    process_count: int
    uptime_seconds: float

@dataclass
class ApplicationMetrics:
    """Application-specific metrics."""
    timestamp: float
    total_requests: int
    successful_requests: int
    failed_requests: int
    average_response_time: float
    cache_hit_rate: float
    active_connections: int
    queue_size: int
    error_rate: float
    throughput_per_second: float

class MetricsCollector:
    """Collects and stores system and application metrics."""
    
    def __init__(self, max_history: int = 1000):
        self.max_history = max_history
        self.system_metrics = deque(maxlen=max_history)
        self.app_metrics = deque(maxlen=max_history)
        self.start_time = time.time()
        self.last_network_stats = psutil.net_io_counters()
        self.collecting = False
        self.collector_thread = None
        
    def start_collection(self):
        """Start metrics collection in background thread."""
        if not self.collecting:
            self.collecting = True
            self.collector_thread = threading.Thread(target=self._collect_metrics_loop)
            self.collector_thread.daemon = True
            self.collector_thread.start()
            logger.info("Metrics collection started")
    
    def stop_collection(self):
        """Stop metrics collection."""
        self.collecting = False
        if self.collector_thread:
            self.collector_thread.join()
        logger.info("Metrics collection stopped")
    
    def _collect_metrics_loop(self):
        """Main metrics collection loop."""
        while self.collecting:
            try:
                # Collect system metrics
                system_metrics = self._collect_system_metrics()
                self.system_metrics.append(system_metrics)
                
                # Collect application metrics
                app_metrics = self._collect_app_metrics()
                self.app_metrics.append(app_metrics)
                
                time.sleep(1)  # Collect every second
                
            except Exception as e:
                logger.error(f"Error collecting metrics: {e}")
                time.sleep(5)  # Wait longer on error
    
    def _collect_system_metrics(self) -> SystemMetrics:
        """Collect system-level metrics."""
        # CPU and memory
        cpu_percent = psutil.cpu_percent(interval=0.1)
        memory = psutil.virtual_memory()
        
        # Disk usage
        disk = psutil.disk_usage('/')
        
        # Network stats
        network = psutil.net_io_counters()
        network_sent = (network.bytes_sent - self.last_network_stats.bytes_sent) / (1024 * 1024)
        network_recv = (network.bytes_recv - self.last_network_stats.bytes_recv) / (1024 * 1024)
        self.last_network_stats = network
        
        # Load average (Unix only)
        try:
            load_avg = list(psutil.getloadavg())
        except AttributeError:
            load_avg = [0.0, 0.0, 0.0]
        
        # Process count
        process_count = len(psutil.pids())
        
        return SystemMetrics(
            timestamp=time.time(),
            cpu_percent=cpu_percent,
            memory_percent=memory.percent,
            memory_used_gb=memory.used / (1024**3),
            memory_available_gb=memory.available / (1024**3),
            disk_usage_percent=disk.percent,
            network_sent_mb=network_sent,
            network_recv_mb=network_recv,
            load_average=load_avg,
            process_count=process_count,
            uptime_seconds=time.time() - self.start_time
        )
    
    def _collect_app_metrics(self) -> ApplicationMetrics:
        """Collect application-specific metrics."""
        # This would typically connect to your application's metrics endpoint
        # For now, we'll simulate some metrics
        
        # Simulate some realistic metrics
        total_requests = len(self.app_metrics) * 10 + np.random.randint(0, 5)
        successful_requests = int(total_requests * np.random.uniform(0.85, 0.99))
        failed_requests = total_requests - successful_requests
        
        return ApplicationMetrics(
            timestamp=time.time(),
            total_requests=total_requests,
            successful_requests=successful_requests,
            failed_requests=failed_requests,
            average_response_time=np.random.uniform(0.1, 2.0),
            cache_hit_rate=np.random.uniform(0.6, 0.9),
            active_connections=np.random.randint(5, 50),
            queue_size=np.random.randint(0, 20),
            error_rate=failed_requests / max(total_requests, 1),
            throughput_per_second=np.random.uniform(10, 100)
        )
    
    def get_latest_metrics(self) -> Dict[str, Any]:
        """Get the latest metrics."""
        latest_system = self.system_metrics[-1] if self.system_metrics else None
        latest_app = self.app_metrics[-1] if self.app_metrics else None
        
        return {
            'system': asdict(latest_system) if latest_system else None,
            'application': asdict(latest_app) if latest_app else None,
            'collection_active': self.collecting
        }
    
    def get_metrics_history(self, minutes: int = 60) -> Dict[str, List[Dict[str, Any]]]:
        """Get metrics history for the last N minutes."""
        cutoff_time = time.time() - (minutes * 60)
        
        system_history = [
            asdict(metric) for metric in self.system_metrics 
            if metric.timestamp >= cutoff_time
        ]
        
        app_history = [
            asdict(metric) for metric in self.app_metrics 
            if metric.timestamp >= cutoff_time
        ]
        
        return {
            'system': system_history,
            'application': app_history
        }

class MonitoringDashboard:
    """Streamlit-based monitoring dashboard."""
    
    def __init__(self):
        self.metrics_collector = MetricsCollector()
        self.api_url = "http://localhost:8000"  # Default API URL
        
    def run(self):
        """Run the Streamlit dashboard."""
        st.set_page_config(
            page_title="Frontier AI Monitoring Dashboard",
            page_icon="🚀",
            layout="wide",
            initial_sidebar_state="expanded"
        )
        
        # Start metrics collection
        if not self.metrics_collector.collecting:
            self.metrics_collector.start_collection()
        
        # Main dashboard
        self._render_dashboard()
    
    def _render_dashboard(self):
        """Render the main dashboard."""
        st.title("🚀 Frontier AI Monitoring Dashboard")
        st.markdown("Real-time monitoring of system performance and application metrics")
        
        # Sidebar controls
        self._render_sidebar()
        
        # Main content
        col1, col2 = st.columns([2, 1])
        
        with col1:
            self._render_system_overview()
            self._render_performance_charts()
        
        with col2:
            self._render_health_status()
            self._render_quick_metrics()
        
        # Additional sections
        self._render_detailed_metrics()
        self._render_alerts()
    
    def _render_sidebar(self):
        """Render sidebar controls."""
        st.sidebar.title("Controls")
        
        # Refresh interval
        refresh_interval = st.sidebar.slider(
            "Refresh Interval (seconds)", 
            min_value=1, 
            max_value=60, 
            value=5
        )
        
        # Time range
        time_range = st.sidebar.selectbox(
            "Time Range",
            ["Last 5 minutes", "Last 15 minutes", "Last hour", "Last 6 hours"]
        )
        
        # Auto-refresh
        auto_refresh = st.sidebar.checkbox("Auto Refresh", value=True)
        
        if auto_refresh:
            time.sleep(refresh_interval)
            st.rerun()
        
        # API Status
        st.sidebar.subheader("API Status")
        try:
            response = requests.get(f"{self.api_url}/health", timeout=5)
            if response.status_code == 200:
                st.sidebar.success("✅ API Online")
                health_data = response.json()
                st.sidebar.metric("Uptime", f"{health_data['uptime_hours']:.1f}h")
                st.sidebar.metric("Success Rate", f"{health_data['success_rate']:.1%}")
            else:
                st.sidebar.error("❌ API Error")
        except:
            st.sidebar.error("❌ API Offline")
    
    def _render_system_overview(self):
        """Render system overview section."""
        st.subheader("🖥️ System Overview")
        
        latest_metrics = self.metrics_collector.get_latest_metrics()
        
        if latest_metrics['system']:
            system = latest_metrics['system']
            
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric(
                    "CPU Usage",
                    f"{system['cpu_percent']:.1f}%",
                    delta=f"{system['cpu_percent'] - 50:.1f}%" if system['cpu_percent'] > 50 else None
                )
            
            with col2:
                st.metric(
                    "Memory Usage",
                    f"{system['memory_percent']:.1f}%",
                    delta=f"{system['memory_percent'] - 70:.1f}%" if system['memory_percent'] > 70 else None
                )
            
            with col3:
                st.metric(
                    "Memory Used",
                    f"{system['memory_used_gb']:.1f} GB"
                )
            
            with col4:
                st.metric(
                    "Disk Usage",
                    f"{system['disk_usage_percent']:.1f}%"
                )
    
    def _render_performance_charts(self):
        """Render performance charts."""
        st.subheader("📊 Performance Charts")
        
        # Get metrics history
        history = self.metrics_collector.get_metrics_history(minutes=60)
        
        if history['system'] and len(history['system']) > 1:
            # Create DataFrame
            df_system = pd.DataFrame(history['system'])
            df_system['timestamp'] = pd.to_datetime(df_system['timestamp'], unit='s')
            
            # CPU and Memory chart
            fig = make_subplots(
                rows=2, cols=2,
                subplot_titles=('CPU Usage', 'Memory Usage', 'Network I/O', 'Load Average'),
                specs=[[{"secondary_y": False}, {"secondary_y": False}],
                       [{"secondary_y": False}, {"secondary_y": False}]]
            )
            
            # CPU Usage
            fig.add_trace(
                go.Scatter(
                    x=df_system['timestamp'],
                    y=df_system['cpu_percent'],
                    name='CPU %',
                    line=dict(color='blue')
                ),
                row=1, col=1
            )
            
            # Memory Usage
            fig.add_trace(
                go.Scatter(
                    x=df_system['timestamp'],
                    y=df_system['memory_percent'],
                    name='Memory %',
                    line=dict(color='red')
                ),
                row=1, col=2
            )
            
            # Network I/O
            fig.add_trace(
                go.Scatter(
                    x=df_system['timestamp'],
                    y=df_system['network_sent_mb'],
                    name='Sent MB',
                    line=dict(color='green')
                ),
                row=2, col=1
            )
            
            fig.add_trace(
                go.Scatter(
                    x=df_system['timestamp'],
                    y=df_system['network_recv_mb'],
                    name='Received MB',
                    line=dict(color='orange')
                ),
                row=2, col=1
            )
            
            # Load Average
            if 'load_average' in df_system.columns:
                load_avg = df_system['load_average'].apply(lambda x: x[0] if isinstance(x, list) and len(x) > 0 else 0)
                fig.add_trace(
                    go.Scatter(
                        x=df_system['timestamp'],
                        y=load_avg,
                        name='Load Avg',
                        line=dict(color='purple')
                    ),
                    row=2, col=2
                )
            
            fig.update_layout(height=600, showlegend=True)
            st.plotly_chart(fig, use_container_width=True)
    
    def _render_health_status(self):
        """Render health status section."""
        st.subheader("🏥 Health Status")
        
        try:
            response = requests.get(f"{self.api_url}/health", timeout=5)
            if response.status_code == 200:
                health_data = response.json()
                
                # Status indicator
                status_color = "green" if health_data['status'] == 'healthy' else "red"
                st.markdown(f"**Status:** :{status_color}[{health_data['status'].upper()}]")
                
                # Key metrics
                st.metric("Total Requests", health_data['total_requests'])
                st.metric("Success Rate", f"{health_data['success_rate']:.1%}")
                st.metric("Avg Response Time", f"{health_data['average_response_time']:.3f}s")
                st.metric("Memory Usage", f"{health_data['memory_usage_gb']:.1f} GB")
                st.metric("CPU Usage", f"{health_data['cpu_usage_percent']:.1f}%")
                
            else:
                st.error("❌ Unable to fetch health data")
        except Exception as e:
            st.error(f"❌ Health check failed: {str(e)}")
    
    def _render_quick_metrics(self):
        """Render quick metrics section."""
        st.subheader("⚡ Quick Metrics")
        
        latest_metrics = self.metrics_collector.get_latest_metrics()
        
        if latest_metrics['application']:
            app = latest_metrics['application']
            
            st.metric("Cache Hit Rate", f"{app['cache_hit_rate']:.1%}")
            st.metric("Error Rate", f"{app['error_rate']:.1%}")
            st.metric("Active Connections", app['active_connections'])
            st.metric("Queue Size", app['queue_size'])
            st.metric("Throughput/sec", f"{app['throughput_per_second']:.1f}")
    
    def _render_detailed_metrics(self):
        """Render detailed metrics section."""
        st.subheader("📈 Detailed Metrics")
        
        try:
            response = requests.get(f"{self.api_url}/metrics", timeout=5)
            if response.status_code == 200:
                metrics_data = response.json()
                
                # Create tabs for different metric categories
                tab1, tab2, tab3 = st.tabs(["Request Metrics", "Performance", "System"])
                
                with tab1:
                    col1, col2 = st.columns(2)
                    with col1:
                        st.metric("Total Requests", metrics_data['total_requests'])
                        st.metric("Successful Requests", metrics_data['successful_requests'])
                        st.metric("Failed Requests", metrics_data['failed_requests'])
                    with col2:
                        st.metric("Success Rate", f"{metrics_data['successful_requests']/max(metrics_data['total_requests'], 1):.1%}")
                        st.metric("Error Rate", f"{metrics_data['failed_requests']/max(metrics_data['total_requests'], 1):.1%}")
                        st.metric("Cache Hit Rate", f"{metrics_data['cache_hit_rate']:.1%}")
                
                with tab2:
                    st.metric("Average Response Time", f"{metrics_data['average_response_time']:.3f}s")
                    
                    # Response time distribution
                    if 'response_times' in metrics_data and metrics_data['response_times']:
                        response_times = metrics_data['response_times']
                        fig = go.Figure(data=[go.Histogram(x=response_times, nbinsx=20)])
                        fig.update_layout(
                            title="Response Time Distribution",
                            xaxis_title="Response Time (seconds)",
                            yaxis_title="Frequency"
                        )
                        st.plotly_chart(fig, use_container_width=True)
                
                with tab3:
                    health = metrics_data['health_status']
                    col1, col2 = st.columns(2)
                    with col1:
                        st.metric("Uptime", f"{health['uptime_hours']:.1f} hours")
                        st.metric("Memory Usage", f"{health['memory_usage_gb']:.1f} GB")
                    with col2:
                        st.metric("CPU Usage", f"{health['cpu_usage_percent']:.1f}%")
                        st.metric("Status", health['status'])
            
            else:
                st.error("Unable to fetch detailed metrics")
        except Exception as e:
            st.error(f"Failed to fetch metrics: {str(e)}")
    
    def _render_alerts(self):
        """Render alerts section."""
        st.subheader("🚨 Alerts")
        
        # Check for various alert conditions
        alerts = []
        
        latest_metrics = self.metrics_collector.get_latest_metrics()
        
        if latest_metrics['system']:
            system = latest_metrics['system']
            
            if system['cpu_percent'] > 90:
                alerts.append(("High CPU Usage", f"CPU usage is {system['cpu_percent']:.1f}%", "error"))
            
            if system['memory_percent'] > 90:
                alerts.append(("High Memory Usage", f"Memory usage is {system['memory_percent']:.1f}%", "error"))
            
            if system['disk_usage_percent'] > 90:
                alerts.append(("High Disk Usage", f"Disk usage is {system['disk_usage_percent']:.1f}%", "warning"))
        
        if latest_metrics['application']:
            app = latest_metrics['application']
            
            if app['error_rate'] > 0.1:
                alerts.append(("High Error Rate", f"Error rate is {app['error_rate']:.1%}", "error"))
            
            if app['average_response_time'] > 5.0:
                alerts.append(("Slow Response Time", f"Average response time is {app['average_response_time']:.2f}s", "warning"))
        
        # Display alerts
        if alerts:
            for title, message, level in alerts:
                if level == "error":
                    st.error(f"🔴 **{title}**: {message}")
                elif level == "warning":
                    st.warning(f"🟡 **{title}**: {message}")
        else:
            st.success("✅ No alerts - All systems operating normally")

def main():
    """Main function to run the dashboard."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Frontier AI Monitoring Dashboard")
    parser.add_argument("--api-url", default="http://localhost:8000", help="API server URL")
    parser.add_argument("--port", type=int, default=8501, help="Dashboard port")
    
    args = parser.parse_args()
    
    # Create and run dashboard
    dashboard = MonitoringDashboard()
    dashboard.api_url = args.api_url
    
    # Run with Streamlit
    import subprocess
    subprocess.run([
        "streamlit", "run", __file__, 
        "--server.port", str(args.port),
        "--server.address", "0.0.0.0"
    ])

if __name__ == "__main__":
    main()










