#!/usr/bin/env python3
"""
ClickUp Brain Real-time Monitor
==============================

Real-time monitoring system for continuous tool usage analysis and optimization.
"""

import os
import json
import logging
import threading
import time
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict
import schedule

# Import other systems
from clickup_brain_simple import SimpleClickUpBrainSystem, ToolUsage
from clickup_brain_ai_enhanced import EnhancedClickUpBrainSystem

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class MonitoringData:
    """Real-time monitoring data structure"""
    timestamp: str
    directory_path: str
    team_size: int
    tool_usage: Dict[str, ToolUsage]
    efficiency_score: float
    changes_detected: List[str]
    performance_metrics: Dict[str, float]
    alerts: List[str]

@dataclass
class MonitoringStatus:
    """Monitoring status data structure"""
    is_active: bool
    start_time: str
    last_check: str
    total_checks: int
    directory_path: str
    team_size: int
    check_interval: int
    alerts_count: int
    efficiency_trend: List[float]

class ClickUpBrainRealtimeSystem:
    """Real-time monitoring system for ClickUp Brain"""
    
    def __init__(self):
        """Initialize real-time monitoring system"""
        self.simple_system = SimpleClickUpBrainSystem()
        self.enhanced_system = EnhancedClickUpBrainSystem()
        
        # Monitoring state
        self.is_monitoring = False
        self.monitoring_thread = None
        self.monitoring_data = []
        self.baseline_data = None
        self.alerts = []
        
        # Configuration
        self.directory_path = None
        self.team_size = 10
        self.check_interval = 300  # 5 minutes default
        self.max_data_points = 1000  # Keep last 1000 data points
        
        # Performance tracking
        self.efficiency_history = []
        self.tool_usage_history = []
        self.change_history = []
    
    def start_monitoring(self, directory_path: str, team_size: int = 10, check_interval: int = 300) -> bool:
        """
        Start real-time monitoring
        
        Args:
            directory_path: Directory to monitor
            team_size: Team size for analysis
            check_interval: Check interval in seconds
        
        Returns:
            True if monitoring started successfully
        """
        try:
            if self.is_monitoring:
                logger.warning("Monitoring is already active")
                return False
            
            # Validate directory
            if not Path(directory_path).exists():
                logger.error(f"Directory not found: {directory_path}")
                return False
            
            # Set configuration
            self.directory_path = directory_path
            self.team_size = team_size
            self.check_interval = check_interval
            
            # Establish baseline
            self._establish_baseline()
            
            # Start monitoring thread
            self.is_monitoring = True
            self.monitoring_thread = threading.Thread(target=self._monitoring_loop, daemon=True)
            self.monitoring_thread.start()
            
            logger.info(f"Real-time monitoring started for {directory_path}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to start monitoring: {str(e)}")
            return False
    
    def stop_monitoring(self) -> bool:
        """
        Stop real-time monitoring
        
        Returns:
            True if monitoring stopped successfully
        """
        try:
            if not self.is_monitoring:
                logger.warning("Monitoring is not active")
                return False
            
            self.is_monitoring = False
            
            if self.monitoring_thread and self.monitoring_thread.is_alive():
                self.monitoring_thread.join(timeout=5)
            
            logger.info("Real-time monitoring stopped")
            return True
            
        except Exception as e:
            logger.error(f"Failed to stop monitoring: {str(e)}")
            return False
    
    def get_status(self) -> Dict[str, Any]:
        """
        Get current monitoring status
        
        Returns:
            Monitoring status information
        """
        status = MonitoringStatus(
            is_active=self.is_monitoring,
            start_time=self.monitoring_data[0].timestamp if self.monitoring_data else None,
            last_check=self.monitoring_data[-1].timestamp if self.monitoring_data else None,
            total_checks=len(self.monitoring_data),
            directory_path=self.directory_path or "Not set",
            team_size=self.team_size,
            check_interval=self.check_interval,
            alerts_count=len(self.alerts),
            efficiency_trend=self.efficiency_history[-10:] if self.efficiency_history else []
        )
        
        return asdict(status)
    
    def get_latest_data(self) -> Optional[Dict[str, Any]]:
        """
        Get latest monitoring data
        
        Returns:
            Latest monitoring data or None
        """
        if not self.monitoring_data:
            return None
        
        return asdict(self.monitoring_data[-1])
    
    def get_efficiency_trend(self, hours: int = 24) -> List[Dict[str, Any]]:
        """
        Get efficiency trend over specified hours
        
        Args:
            hours: Number of hours to look back
        
        Returns:
            Efficiency trend data
        """
        cutoff_time = datetime.now() - timedelta(hours=hours)
        trend_data = []
        
        for data in self.monitoring_data:
            data_time = datetime.fromisoformat(data.timestamp)
            if data_time >= cutoff_time:
                trend_data.append({
                    "timestamp": data.timestamp,
                    "efficiency_score": data.efficiency_score,
                    "tool_count": len(data.tool_usage)
                })
        
        return trend_data
    
    def get_alerts(self, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Get recent alerts
        
        Args:
            limit: Maximum number of alerts to return
        
        Returns:
            List of recent alerts
        """
        return self.alerts[-limit:] if self.alerts else []
    
    def export_data(self, output_file: str) -> bool:
        """
        Export monitoring data to file
        
        Args:
            output_file: Output file path
        
        Returns:
            True if export successful
        """
        try:
            export_data = {
                "export_timestamp": datetime.now().isoformat(),
                "monitoring_config": {
                    "directory_path": self.directory_path,
                    "team_size": self.team_size,
                    "check_interval": self.check_interval
                },
                "monitoring_data": [asdict(data) for data in self.monitoring_data],
                "efficiency_history": self.efficiency_history,
                "alerts": self.alerts,
                "summary": {
                    "total_checks": len(self.monitoring_data),
                    "average_efficiency": sum(self.efficiency_history) / len(self.efficiency_history) if self.efficiency_history else 0,
                    "total_alerts": len(self.alerts),
                    "monitoring_duration": self._calculate_monitoring_duration()
                }
            }
            
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(export_data, f, ensure_ascii=False, indent=2, default=str)
            
            logger.info(f"Monitoring data exported to {output_file}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to export data: {str(e)}")
            return False
    
    def _establish_baseline(self):
        """Establish baseline data for comparison"""
        try:
            baseline_results = self.simple_system.scan_directory(self.directory_path)
            
            if "error" in baseline_results:
                logger.error(f"Failed to establish baseline: {baseline_results['error']}")
                return
            
            self.baseline_data = {
                "timestamp": datetime.now().isoformat(),
                "tool_usage": baseline_results['tool_usage'],
                "efficiency_score": baseline_results['efficiency_score'],
                "categories": baseline_results['categories']
            }
            
            logger.info("Baseline data established")
            
        except Exception as e:
            logger.error(f"Failed to establish baseline: {str(e)}")
    
    def _monitoring_loop(self):
        """Main monitoring loop"""
        logger.info("Monitoring loop started")
        
        while self.is_monitoring:
            try:
                # Perform analysis
                current_data = self._perform_analysis()
                
                if current_data:
                    # Store data
                    self.monitoring_data.append(current_data)
                    
                    # Keep only recent data
                    if len(self.monitoring_data) > self.max_data_points:
                        self.monitoring_data = self.monitoring_data[-self.max_data_points:]
                    
                    # Update efficiency history
                    self.efficiency_history.append(current_data.efficiency_score)
                    
                    # Check for changes and generate alerts
                    self._check_for_changes(current_data)
                    
                    # Update tool usage history
                    self.tool_usage_history.append({
                        "timestamp": current_data.timestamp,
                        "tools": list(current_data.tool_usage.keys())
                    })
                
                # Wait for next check
                time.sleep(self.check_interval)
                
            except Exception as e:
                logger.error(f"Error in monitoring loop: {str(e)}")
                time.sleep(60)  # Wait 1 minute before retry
        
        logger.info("Monitoring loop stopped")
    
    def _perform_analysis(self) -> Optional[MonitoringData]:
        """Perform current analysis"""
        try:
            # Get current analysis
            current_results = self.simple_system.scan_directory(self.directory_path)
            
            if "error" in current_results:
                logger.error(f"Analysis failed: {current_results['error']}")
                return None
            
            # Convert tool usage data
            tool_usage = {}
            for name, data in current_results['tool_usage'].items():
                tool_usage[name] = ToolUsage(**data)
            
            # Calculate performance metrics
            performance_metrics = self._calculate_performance_metrics(current_results)
            
            # Create monitoring data
            monitoring_data = MonitoringData(
                timestamp=datetime.now().isoformat(),
                directory_path=self.directory_path,
                team_size=self.team_size,
                tool_usage=tool_usage,
                efficiency_score=current_results['efficiency_score'],
                changes_detected=[],  # Will be populated by change detection
                performance_metrics=performance_metrics,
                alerts=[]  # Will be populated by alert generation
            )
            
            return monitoring_data
            
        except Exception as e:
            logger.error(f"Failed to perform analysis: {str(e)}")
            return None
    
    def _calculate_performance_metrics(self, analysis_results: Dict[str, Any]) -> Dict[str, float]:
        """Calculate performance metrics"""
        metrics = {}
        
        # Tool count
        metrics['tool_count'] = len(analysis_results.get('tool_usage', {}))
        
        # Category diversity
        metrics['category_diversity'] = len(analysis_results.get('categories', []))
        
        # Average efficiency
        tool_usage = analysis_results.get('tool_usage', {})
        if tool_usage:
            metrics['average_efficiency'] = sum(tool['efficiency_score'] for tool in tool_usage.values()) / len(tool_usage)
        else:
            metrics['average_efficiency'] = 0.0
        
        # Cost efficiency
        total_cost = sum(tool.get('cost_per_user', 0) for tool in tool_usage.values())
        metrics['total_cost_per_user'] = total_cost
        metrics['cost_efficiency'] = metrics['average_efficiency'] / max(1, total_cost)
        
        # Integration score
        total_integrations = sum(tool.get('integration_count', 0) for tool in tool_usage.values())
        metrics['integration_score'] = total_integrations / max(1, len(tool_usage))
        
        return metrics
    
    def _check_for_changes(self, current_data: MonitoringData):
        """Check for changes and generate alerts"""
        if not self.baseline_data:
            return
        
        changes = []
        alerts = []
        
        # Check for new tools
        current_tools = set(current_data.tool_usage.keys())
        baseline_tools = set(self.baseline_data['tool_usage'].keys())
        
        new_tools = current_tools - baseline_tools
        removed_tools = baseline_tools - current_tools
        
        if new_tools:
            changes.append(f"New tools detected: {', '.join(new_tools)}")
            alerts.append({
                "type": "info",
                "message": f"New tools added: {', '.join(new_tools)}",
                "timestamp": current_data.timestamp,
                "severity": "low"
            })
        
        if removed_tools:
            changes.append(f"Tools removed: {', '.join(removed_tools)}")
            alerts.append({
                "type": "warning",
                "message": f"Tools removed: {', '.join(removed_tools)}",
                "timestamp": current_data.timestamp,
                "severity": "medium"
            })
        
        # Check efficiency changes
        efficiency_change = current_data.efficiency_score - self.baseline_data['efficiency_score']
        
        if abs(efficiency_change) > 1.0:  # Significant change
            if efficiency_change > 0:
                changes.append(f"Efficiency improved by {efficiency_change:.1f}")
                alerts.append({
                    "type": "success",
                    "message": f"Efficiency improved by {efficiency_change:.1f} points",
                    "timestamp": current_data.timestamp,
                    "severity": "low"
                })
            else:
                changes.append(f"Efficiency decreased by {abs(efficiency_change):.1f}")
                alerts.append({
                    "type": "warning",
                    "message": f"Efficiency decreased by {abs(efficiency_change):.1f} points",
                    "timestamp": current_data.timestamp,
                    "severity": "high"
                })
        
        # Check for ClickUp adoption
        if "ClickUp" in current_tools and "ClickUp" not in baseline_tools:
            changes.append("ClickUp adopted!")
            alerts.append({
                "type": "success",
                "message": "ClickUp has been adopted - great choice!",
                "timestamp": current_data.timestamp,
                "severity": "low"
            })
        
        # Update data with changes and alerts
        current_data.changes_detected = changes
        current_data.alerts = alerts
        
        # Store alerts
        self.alerts.extend(alerts)
        
        # Keep only recent alerts
        if len(self.alerts) > 100:
            self.alerts = self.alerts[-100:]
        
        # Log significant changes
        if changes:
            logger.info(f"Changes detected: {', '.join(changes)}")
    
    def _calculate_monitoring_duration(self) -> str:
        """Calculate monitoring duration"""
        if not self.monitoring_data:
            return "0 minutes"
        
        start_time = datetime.fromisoformat(self.monitoring_data[0].timestamp)
        end_time = datetime.fromisoformat(self.monitoring_data[-1].timestamp)
        duration = end_time - start_time
        
        if duration.days > 0:
            return f"{duration.days} days, {duration.seconds // 3600} hours"
        elif duration.seconds > 3600:
            return f"{duration.seconds // 3600} hours, {(duration.seconds % 3600) // 60} minutes"
        else:
            return f"{duration.seconds // 60} minutes"

def main():
    """Main function for testing"""
    print("📊 ClickUp Brain Real-time Monitor")
    print("=" * 50)
    
    # Initialize system
    monitor = ClickUpBrainRealtimeSystem()
    
    # Test monitoring
    test_directory = "."
    team_size = 10
    check_interval = 30  # 30 seconds for testing
    
    print(f"Starting monitoring for: {test_directory}")
    print(f"Team size: {team_size}")
    print(f"Check interval: {check_interval} seconds")
    
    # Start monitoring
    if monitor.start_monitoring(test_directory, team_size, check_interval):
        print("✅ Monitoring started successfully")
        
        try:
            # Monitor for 2 minutes
            for i in range(4):
                time.sleep(30)
                
                # Get status
                status = monitor.get_status()
                print(f"\n📊 Status Check {i+1}:")
                print(f"  Active: {status['is_active']}")
                print(f"  Total checks: {status['total_checks']}")
                print(f"  Alerts: {status['alerts_count']}")
                
                # Get latest data
                latest_data = monitor.get_latest_data()
                if latest_data:
                    print(f"  Current efficiency: {latest_data['efficiency_score']:.1f}/10")
                    print(f"  Tools detected: {len(latest_data['tool_usage'])}")
                
                # Get recent alerts
                alerts = monitor.get_alerts(3)
                if alerts:
                    print(f"  Recent alerts: {len(alerts)}")
                    for alert in alerts:
                        print(f"    - {alert['message']}")
            
            # Stop monitoring
            monitor.stop_monitoring()
            print("\n🛑 Monitoring stopped")
            
            # Export data
            export_file = f"monitoring_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            if monitor.export_data(export_file):
                print(f"📄 Data exported to: {export_file}")
            
        except KeyboardInterrupt:
            print("\n🛑 Monitoring interrupted by user")
            monitor.stop_monitoring()
    else:
        print("❌ Failed to start monitoring")

if __name__ == "__main__":
    main()