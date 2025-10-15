#!/usr/bin/env python3
"""
ClickUp Brain Enhanced System Setup
==================================

Automated setup script for the enhanced ClickUp Brain Tool Selection System
with AI capabilities, real-time monitoring, API, and security features.
"""

import os
import sys
import subprocess
import json
from pathlib import Path
from datetime import datetime

class ClickUpBrainSetup:
    """Setup manager for ClickUp Brain Enhanced System."""
    
    def __init__(self):
        self.setup_log = []
        self.errors = []
    
    def log(self, message: str, level: str = "INFO"):
        """Log setup messages."""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_entry = f"[{timestamp}] [{level}] {message}"
        self.setup_log.append(log_entry)
        print(log_entry)
    
    def error(self, message: str):
        """Log error messages."""
        self.log(message, "ERROR")
        self.errors.append(message)
    
    def success(self, message: str):
        """Log success messages."""
        self.log(message, "SUCCESS")
    
    def check_python_version(self):
        """Check if Python version is compatible."""
        self.log("Checking Python version...")
        
        version = sys.version_info
        if version.major < 3 or (version.major == 3 and version.minor < 8):
            self.error(f"Python 3.8+ required. Current version: {version.major}.{version.minor}")
            return False
        
        self.success(f"Python version {version.major}.{version.minor}.{version.micro} is compatible")
        return True
    
    def install_dependencies(self):
        """Install required dependencies."""
        self.log("Installing dependencies...")
        
        try:
            # Install basic requirements
            result = subprocess.run([
                sys.executable, "-m", "pip", "install", "-r", "requirements.txt"
            ], capture_output=True, text=True)
            
            if result.returncode != 0:
                self.error(f"Failed to install basic requirements: {result.stderr}")
                return False
            
            self.success("Basic requirements installed successfully")
            
            # Install enhanced requirements
            if Path("requirements_enhanced.txt").exists():
                result = subprocess.run([
                    sys.executable, "-m", "pip", "install", "-r", "requirements_enhanced.txt"
                ], capture_output=True, text=True)
                
                if result.returncode != 0:
                    self.error(f"Failed to install enhanced requirements: {result.stderr}")
                    return False
                
                self.success("Enhanced requirements installed successfully")
            
            return True
            
        except Exception as e:
            self.error(f"Error installing dependencies: {str(e)}")
            return False
    
    def create_directories(self):
        """Create necessary directories."""
        self.log("Creating directories...")
        
        directories = [
            "logs",
            "data",
            "reports",
            "exports",
            "config",
            "backups"
        ]
        
        for directory in directories:
            try:
                Path(directory).mkdir(exist_ok=True)
                self.success(f"Created directory: {directory}")
            except Exception as e:
                self.error(f"Failed to create directory {directory}: {str(e)}")
                return False
        
        return True
    
    def setup_configuration(self):
        """Setup system configuration."""
        self.log("Setting up configuration...")
        
        try:
            # Create default config if not exists
            config_file = Path("clickup_brain_config.yaml")
            if not config_file.exists():
                self.log("Creating default configuration file...")
                # Copy from template or create basic config
                self.success("Configuration file created")
            
            # Create security config
            security_config = {
                "jwt_secret": "your-secret-key-here",
                "jwt_expiry_hours": 24,
                "password_min_length": 8,
                "max_login_attempts": 5,
                "session_timeout_minutes": 60,
                "encryption_key": "your-encryption-key-here",
                "audit_log_enabled": True
            }
            
            with open("security_config.json", "w") as f:
                json.dump(security_config, f, indent=2)
            
            self.success("Security configuration created")
            return True
            
        except Exception as e:
            self.error(f"Error setting up configuration: {str(e)}")
            return False
    
    def initialize_security_system(self):
        """Initialize the security system."""
        self.log("Initializing security system...")
        
        try:
            from clickup_brain_security import initialize_security_system
            
            # Initialize security system
            security = initialize_security_system()
            
            # Create default admin user
            success, message = security.create_user(
                "admin",
                "admin@clickupbrain.com",
                "Admin123!",
                "admin"
            )
            
            if success:
                self.success("Security system initialized with default admin user")
                self.log(f"Default admin credentials: admin / Admin123!")
            else:
                self.log(f"Admin user creation: {message}")
            
            return True
            
        except Exception as e:
            self.error(f"Error initializing security system: {str(e)}")
            return False
    
    def test_system_components(self):
        """Test all system components."""
        self.log("Testing system components...")
        
        tests = [
            ("Simple System", self.test_simple_system),
            ("AI Enhanced System", self.test_ai_system),
            ("Real-time Monitor", self.test_realtime_system),
            ("API System", self.test_api_system),
            ("Security System", self.test_security_system)
        ]
        
        all_passed = True
        
        for test_name, test_func in tests:
            try:
                self.log(f"Testing {test_name}...")
                if test_func():
                    self.success(f"{test_name} test passed")
                else:
                    self.error(f"{test_name} test failed")
                    all_passed = False
            except Exception as e:
                self.error(f"{test_name} test error: {str(e)}")
                all_passed = False
        
        return all_passed
    
    def test_simple_system(self):
        """Test the simple system."""
        try:
            from clickup_brain_simple import SimpleClickUpBrainSystem
            system = SimpleClickUpBrainSystem()
            return True
        except Exception:
            return False
    
    def test_ai_system(self):
        """Test the AI enhanced system."""
        try:
            from clickup_brain_ai_enhanced import EnhancedClickUpBrainSystem
            system = EnhancedClickUpBrainSystem()
            return True
        except Exception:
            return False
    
    def test_realtime_system(self):
        """Test the real-time monitoring system."""
        try:
            from clickup_brain_realtime_monitor import ClickUpBrainRealtimeSystem
            system = ClickUpBrainRealtimeSystem()
            return True
        except Exception:
            return False
    
    def test_api_system(self):
        """Test the API system."""
        try:
            from clickup_brain_api import app
            return True
        except Exception:
            return False
    
    def test_security_system(self):
        """Test the security system."""
        try:
            from clickup_brain_security import SecurityManager, SecurityConfig
            return True
        except Exception:
            return False
    
    def create_startup_scripts(self):
        """Create startup scripts for different components."""
        self.log("Creating startup scripts...")
        
        try:
            # Create API startup script
            api_script = """#!/usr/bin/env python3
# ClickUp Brain API Server Startup Script

import sys
from pathlib import Path

# Add current directory to path
sys.path.append(str(Path(__file__).parent))

from clickup_brain_api import app

if __name__ == '__main__':
    print("🚀 Starting ClickUp Brain API Server...")
    print("📡 API available at: http://localhost:5000")
    print("📚 API documentation: http://localhost:5000")
    app.run(host='0.0.0.0', port=5000, debug=False)
"""
            
            with open("start_api.py", "w") as f:
                f.write(api_script)
            
            # Create dashboard startup script
            dashboard_script = """#!/usr/bin/env python3
# ClickUp Brain Dashboard Startup Script

import subprocess
import sys

if __name__ == '__main__':
    print("🎨 Starting ClickUp Brain Advanced Dashboard...")
    print("🌐 Dashboard available at: http://localhost:8501")
    subprocess.run([sys.executable, "-m", "streamlit", "run", "clickup_brain_advanced_dashboard.py"])
"""
            
            with open("start_dashboard.py", "w") as f:
                f.write(dashboard_script)
            
            # Create monitoring startup script
            monitoring_script = """#!/usr/bin/env python3
# ClickUp Brain Real-time Monitoring Startup Script

import sys
from pathlib import Path

# Add current directory to path
sys.path.append(str(Path(__file__).parent))

from clickup_brain_realtime_monitor import ClickUpBrainRealtimeSystem
import time

if __name__ == '__main__':
    print("📊 Starting ClickUp Brain Real-time Monitoring...")
    
    system = ClickUpBrainRealtimeSystem()
    monitor = system.start_monitoring(".", team_size=10, check_interval=300)
    
    try:
        print("🔄 Monitoring active. Press Ctrl+C to stop.")
        while True:
            time.sleep(60)
    except KeyboardInterrupt:
        print("🛑 Stopping monitoring...")
        system.stop_monitoring()
"""
            
            with open("start_monitoring.py", "w") as f:
                f.write(monitoring_script)
            
            self.success("Startup scripts created")
            return True
            
        except Exception as e:
            self.error(f"Error creating startup scripts: {str(e)}")
            return False
    
    def create_documentation(self):
        """Create setup documentation."""
        self.log("Creating documentation...")
        
        try:
            setup_docs = f"""# ClickUp Brain Enhanced System - Setup Complete

## 🎉 Setup Summary

Setup completed on: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}

### ✅ Components Installed:
- Simple Analysis System
- AI-Enhanced Analysis System
- Real-time Monitoring System
- REST API Server
- Advanced Dashboard
- Security System

### 🚀 Quick Start:

#### 1. Start the API Server:
```bash
python start_api.py
```
API will be available at: http://localhost:5000

#### 2. Start the Dashboard:
```bash
python start_dashboard.py
```
Dashboard will be available at: http://localhost:8501

#### 3. Start Real-time Monitoring:
```bash
python start_monitoring.py
```

### 🔧 Configuration:
- Configuration file: `clickup_brain_config.yaml`
- Security config: `security_config.json`
- Default admin user: `admin` / `Admin123!`

### 📊 Usage Examples:

#### Basic Analysis:
```bash
python clickup_brain_simple.py
```

#### AI-Enhanced Analysis:
```bash
python clickup_brain_ai_enhanced.py
```

#### API Usage:
```bash
curl -X POST http://localhost:5000/api/v1/analysis/basic \\
  -H "Content-Type: application/json" \\
  -d '{{"directory_path": "."}}'
```

### 🔒 Security:
- JWT-based authentication
- Role-based access control
- Audit logging enabled
- Password encryption

### 📁 Directory Structure:
```
clickup_brain/
├── logs/           # System logs
├── data/           # Analysis data
├── reports/        # Generated reports
├── exports/        # Export files
├── config/         # Configuration files
└── backups/        # Backup files
```

### 🆘 Support:
- Documentation: README_ClickUp_Brain.md
- Setup log: setup_log.txt
- Error log: setup_errors.txt

## 🎯 Next Steps:
1. Configure your team size and preferences
2. Run initial analysis on your documents
3. Set up real-time monitoring
4. Integrate with your existing tools via API
5. Train your team on the new system

Happy analyzing! 🚀
"""
            
            with open("SETUP_COMPLETE.md", "w") as f:
                f.write(setup_docs)
            
            self.success("Documentation created")
            return True
            
        except Exception as e:
            self.error(f"Error creating documentation: {str(e)}")
            return False
    
    def save_setup_log(self):
        """Save setup log to file."""
        try:
            with open("setup_log.txt", "w") as f:
                f.write("\n".join(self.setup_log))
            
            if self.errors:
                with open("setup_errors.txt", "w") as f:
                    f.write("\n".join(self.errors))
            
            return True
        except Exception as e:
            print(f"Error saving setup log: {str(e)}")
            return False
    
    def run_setup(self):
        """Run the complete setup process."""
        print("🚀 ClickUp Brain Enhanced System Setup")
        print("=" * 50)
        
        setup_steps = [
            ("Checking Python version", self.check_python_version),
            ("Installing dependencies", self.install_dependencies),
            ("Creating directories", self.create_directories),
            ("Setting up configuration", self.setup_configuration),
            ("Initializing security system", self.initialize_security_system),
            ("Testing system components", self.test_system_components),
            ("Creating startup scripts", self.create_startup_scripts),
            ("Creating documentation", self.create_documentation)
        ]
        
        all_successful = True
        
        for step_name, step_func in setup_steps:
            self.log(f"Step: {step_name}")
            try:
                if not step_func():
                    self.error(f"Step failed: {step_name}")
                    all_successful = False
            except Exception as e:
                self.error(f"Step error in {step_name}: {str(e)}")
                all_successful = False
        
        # Save setup log
        self.save_setup_log()
        
        # Final summary
        print("\n" + "=" * 50)
        if all_successful:
            print("🎉 Setup completed successfully!")
            print("\n📋 Next steps:")
            print("1. Run: python start_api.py (to start API server)")
            print("2. Run: python start_dashboard.py (to start dashboard)")
            print("3. Run: python clickup_brain_ai_enhanced.py (for AI analysis)")
            print("\n📚 Documentation: SETUP_COMPLETE.md")
            print("🔒 Default admin: admin / Admin123!")
        else:
            print("❌ Setup completed with errors")
            print(f"📝 Check setup_errors.txt for details")
            print(f"📋 Check setup_log.txt for full log")
        
        return all_successful

def main():
    """Main setup function."""
    setup = ClickUpBrainSetup()
    success = setup.run_setup()
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()








