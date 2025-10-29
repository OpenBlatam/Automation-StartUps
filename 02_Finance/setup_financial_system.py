#!/usr/bin/env python3
"""
Financial System Setup Script
Automated setup and configuration
Version: 2.0.0
"""

import os
import sys
import json
import subprocess
from pathlib import Path


class FinancialSystemSetup:
    """
    Automated setup for Financial System
    """
    
    def __init__(self):
        self.base_dir = Path(__file__).parent
        self.config_file = self.base_dir / 'config.json'
        self.env_file = self.base_dir / '.env'
        self.env_example = self.base_dir / '.env.example'
    
    def check_requirements(self):
        """Check Python version and required packages"""
        print("🔍 Checking requirements...")
        
        # Check Python version
        if sys.version_info < (3, 8):
            print("❌ Python 3.8+ required")
            return False
        
        print(f"✅ Python {sys.version_info.major}.{sys.version_info.minor}")
        
        # Check required packages
        required_packages = [
            'pandas',
            'numpy',
            'requests'
        ]
        
        for package in required_packages:
            try:
                __import__(package)
                print(f"✅ {package}")
            except ImportError:
                print(f"❌ {package} not installed")
                return False
        
        return True
    
    def install_dependencies(self):
        """Install required dependencies"""
        print("\n📦 Installing dependencies...")
        
        try:
            subprocess.run(['pip', 'install', '-r', 'requirements.txt'], check=True)
            print("✅ Dependencies installed successfully")
            return True
        except subprocess.CalledProcessError:
            print("❌ Failed to install dependencies")
            return False
        except FileNotFoundError:
            print("⚠️  requirements.txt not found, skipping")
            return True
    
    def create_env_file(self):
        """Create .env file from template"""
        print("\n📝 Creating .env file...")
        
        if self.env_file.exists():
            response = input("⚠️  .env file exists. Overwrite? (y/n): ")
            if response.lower() != 'y':
                print("⏭️  Skipping .env creation")
                return True
        
        env_template = """# Financial System Configuration
# Last Updated: 2025-01-27

# Banking APIs
PLAID_CLIENT_ID=your_client_id_here
PLAID_SECRET=your_secret_here
PLAID_ENVIRONMENT=sandbox

# Payment Platforms
STRIPE_SECRET_KEY=your_stripe_key_here
PAYPAL_CLIENT_ID=your_paypal_id_here

# ERP Systems
SAP_SERVER=your_sap_server_here
SAP_USERNAME=your_username_here

# Analytics
TABLEAU_SERVER=your_tableau_server_here
POWER_BI_CLIENT_ID=your_power_bi_id_here

# Encryption
ENCRYPTION_KEY=your_encryption_key_here
"""
        
        try:
            with open(self.env_file, 'w') as f:
                f.write(env_template)
            print("✅ .env file created")
            print("⚠️  Please update .env with your actual credentials")
            return True
        except Exception as e:
            print(f"❌ Failed to create .env: {e}")
            return False
    
    def create_config_file(self):
        """Create default config.json"""
        print("\n⚙️  Creating config.json...")
        
        if self.config_file.exists():
            response = input("⚠️  config.json exists. Overwrite? (y/n): ")
            if response.lower() != 'y':
                print("⏭️  Skipping config creation")
                return True
        
        config = {
            "version": "2.0.0",
            "automation": {
                "enabled": True,
                "ocr_enabled": True,
                "auto_categorization": True,
                "auto_reconciliation": True
            },
            "alerts": {
                "budget_alert_threshold": 90,
                "large_transaction_threshold": 1000,
                "anomaly_threshold": 2.5
            },
            "reporting": {
                "daily_summary": True,
                "weekly_report": True,
                "monthly_analysis": True
            },
            "forecasting": {
                "model": "lstm",
                "horizon_days": 90,
                "confidence_threshold": 0.85
            },
            "integrations": {
                "banking": "plaid",
                "payments": "stripe",
                "erp": "none"
            }
        }
        
        try:
            with open(self.config_file, 'w') as f:
                json.dump(config, f, indent=2)
            print("✅ config.json created")
            return True
        except Exception as e:
            print(f"❌ Failed to create config.json: {e}")
            return False
    
    def create_directories(self):
        """Create necessary directories"""
        print("\n📁 Creating directories...")
        
        directories = [
            'data',
            'reports',
            'exports',
            'logs',
            'backups'
        ]
        
        for directory in directories:
            dir_path = self.base_dir / directory
            try:
                dir_path.mkdir(exist_ok=True)
                print(f"✅ {directory}/")
            except Exception as e:
                print(f"❌ Failed to create {directory}: {e}")
                return False
        
        return True
    
    def test_system(self):
        """Test system functionality"""
        print("\n🧪 Testing system...")
        
        try:
            # Test imports
            from financial_automation_engine import FinancialAutomationEngine
            from financial_insights_ai import FinancialInsightsAI
            
            print("✅ Module imports successful")
            
            # Test basic functionality
            engine = FinancialAutomationEngine()
            print("✅ Engine initialization successful")
            
            ai = FinancialInsightsAI()
            print("✅ AI module initialization successful")
            
            return True
        except Exception as e:
            print(f"❌ System test failed: {e}")
            return False
    
    def display_summary(self):
        """Display setup summary"""
        print("\n" + "=" * 60)
        print("📊 SETUP SUMMARY")
        print("=" * 60)
        
        files_check = {
            '.env': self.env_file.exists(),
            'config.json': self.config_file.exists(),
            'financial_automation_engine.py': (self.base_dir / 'financial_automation_engine.py').exists(),
            'financial_insights_ai.py': (self.base_dir / 'financial_insights_ai.py').exists(),
            'FINANCIAL_DASHBOARD.html': (self.base_dir / 'FINANCIAL_DASHBOARD.html').exists()
        }
        
        for file, exists in files_check.items():
            status = "✅" if exists else "❌"
            print(f"{status} {file}")
        
        print("\n" + "=" * 60)
        print("🎉 Setup Complete!")
        print("=" * 60)
        print("\n📋 Next Steps:")
        print("1. Update .env with your credentials")
        print("2. Customize config.json as needed")
        print("3. Run: python financial_automation_engine.py")
        print("4. Open: FINANCIAL_DASHBOARD.html")
        print("\n📚 Documentation:")
        print("- README_FINANCIAL_SYSTEM.md")
        print("- AUTOMATIZACION_FINANCIERA_AVANZADA_2025.md")
        print("- IA_INTELIGENCIA_FINANCIERA_2025.md")
        print("\n✅ Happy Financial Management!")
    
    def run_setup(self):
        """Run complete setup process"""
        print("\n" + "=" * 60)
        print("💰 Financial System Setup v2.0.0")
        print("=" * 60)
        
        steps = [
            ("Check Requirements", self.check_requirements),
            ("Install Dependencies", self.install_dependencies),
            ("Create .env File", self.create_env_file),
            ("Create Config", self.create_config_file),
            ("Create Directories", self.create_directories),
            ("Test System", self.test_system)
        ]
        
        for step_name, step_func in steps:
            if not step_func():
                print(f"\n❌ Setup failed at: {step_name}")
                return False
        
        self.display_summary()
        return True


if __name__ == "__main__":
    setup = FinancialSystemSetup()
    success = setup.run_setup()
    
    sys.exit(0 if success else 1)



