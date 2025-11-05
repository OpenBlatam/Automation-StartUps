"""
Health Check System for Ultimate Launch Planning System
Provides comprehensive health monitoring and status reporting
"""

import json
import time
import psutil
import sys
from datetime import datetime
from typing import Dict, Any, List
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class HealthChecker:
    """Comprehensive health monitoring system"""
    
    def __init__(self):
        self.start_time = time.time()
        self.checks = {}
        
    def check_system_resources(self) -> Dict[str, Any]:
        """Check system resource usage"""
        try:
            cpu_percent = psutil.cpu_percent(interval=1)
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage('/')
            
            return {
                "cpu_usage": cpu_percent,
                "memory_usage": memory.percent,
                "memory_available": memory.available,
                "disk_usage": disk.percent,
                "disk_free": disk.free,
                "status": "healthy" if cpu_percent < 80 and memory.percent < 80 else "warning"
            }
        except Exception as e:
            logger.error(f"System resource check failed: {e}")
            return {"status": "error", "error": str(e)}
    
    def check_python_dependencies(self) -> Dict[str, Any]:
        """Check if required Python packages are available"""
        required_packages = [
            'numpy', 'pandas', 'scikit-learn', 'requests', 
            'pydantic', 'fastapi', 'uvicorn'
        ]
        
        results = {}
        all_available = True
        
        for package in required_packages:
            try:
                __import__(package)
                results[package] = "available"
            except ImportError:
                results[package] = "missing"
                all_available = False
        
        return {
            "packages": results,
            "status": "healthy" if all_available else "warning"
        }
    
    def check_optional_dependencies(self) -> Dict[str, Any]:
        """Check optional dependencies"""
        optional_packages = [
            'qiskit', 'web3', 'streamlit', 'matplotlib', 'seaborn'
        ]
        
        results = {}
        available_count = 0
        
        for package in optional_packages:
            try:
                __import__(package)
                results[package] = "available"
                available_count += 1
            except ImportError:
                results[package] = "missing"
        
        return {
            "packages": results,
            "available_count": available_count,
            "total_count": len(optional_packages),
            "status": "healthy" if available_count > 0 else "info"
        }
    
    def check_application_files(self) -> Dict[str, Any]:
        """Check if core application files exist"""
        core_files = [
            'launch_planning_checklist.py',
            'clickup_brain_integration.py',
            'ultimate_launch_demo.py',
            'launch_planning_api.py'
        ]
        
        results = {}
        all_exist = True
        
        for file in core_files:
            try:
                with open(file, 'r') as f:
                    results[file] = "exists"
            except FileNotFoundError:
                results[file] = "missing"
                all_exist = False
        
        return {
            "files": results,
            "status": "healthy" if all_exist else "error"
        }
    
    def check_uptime(self) -> Dict[str, Any]:
        """Check system uptime"""
        uptime_seconds = time.time() - self.start_time
        uptime_hours = uptime_seconds / 3600
        
        return {
            "uptime_seconds": uptime_seconds,
            "uptime_hours": round(uptime_hours, 2),
            "start_time": datetime.fromtimestamp(self.start_time).isoformat(),
            "status": "healthy"
        }
    
    def run_all_checks(self) -> Dict[str, Any]:
        """Run all health checks and return comprehensive status"""
        logger.info("Running comprehensive health checks...")
        
        checks = {
            "timestamp": datetime.now().isoformat(),
            "system_resources": self.check_system_resources(),
            "python_dependencies": self.check_python_dependencies(),
            "optional_dependencies": self.check_optional_dependencies(),
            "application_files": self.check_application_files(),
            "uptime": self.check_uptime()
        }
        
        # Determine overall status
        statuses = [check.get("status", "unknown") for check in checks.values() if isinstance(check, dict)]
        
        if "error" in statuses:
            overall_status = "error"
        elif "warning" in statuses:
            overall_status = "warning"
        elif all(status == "healthy" for status in statuses if status != "unknown"):
            overall_status = "healthy"
        else:
            overall_status = "info"
        
        checks["overall_status"] = overall_status
        checks["version"] = "5.0.0"
        checks["service"] = "Ultimate Launch Planning System"
        
        return checks
    
    def get_health_summary(self) -> str:
        """Get a human-readable health summary"""
        checks = self.run_all_checks()
        
        summary = f"""
🏥 HEALTH CHECK SUMMARY
=======================
Service: {checks['service']} v{checks['version']}
Status: {checks['overall_status'].upper()}
Timestamp: {checks['timestamp']}

📊 SYSTEM RESOURCES
CPU Usage: {checks['system_resources'].get('cpu_usage', 'N/A')}%
Memory Usage: {checks['system_resources'].get('memory_usage', 'N/A')}%
Disk Usage: {checks['system_resources'].get('disk_usage', 'N/A')}%

🐍 PYTHON DEPENDENCIES
Status: {checks['python_dependencies']['status']}
Missing: {[pkg for pkg, status in checks['python_dependencies']['packages'].items() if status == 'missing']}

⚡ OPTIONAL DEPENDENCIES
Available: {checks['optional_dependencies']['available_count']}/{checks['optional_dependencies']['total_count']}

📁 APPLICATION FILES
Status: {checks['application_files']['status']}
Missing: {[f for f, status in checks['application_files']['files'].items() if status == 'missing']}

⏱️ UPTIME
Running for: {checks['uptime']['uptime_hours']} hours
Started: {checks['uptime']['start_time']}
        """
        
        return summary.strip()

def main():
    """Main health check function"""
    health_checker = HealthChecker()
    
    # Run checks
    health_data = health_checker.run_all_checks()
    
    # Print summary
    print(health_checker.get_health_summary())
    
    # Print JSON for API consumption
    print("\n" + "="*50)
    print("JSON OUTPUT:")
    print(json.dumps(health_data, indent=2))
    
    # Exit with appropriate code
    if health_data["overall_status"] == "error":
        sys.exit(1)
    elif health_data["overall_status"] == "warning":
        sys.exit(2)
    else:
        sys.exit(0)

if __name__ == "__main__":
    main()








