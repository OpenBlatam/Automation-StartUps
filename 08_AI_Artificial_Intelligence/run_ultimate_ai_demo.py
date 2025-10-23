#!/usr/bin/env python3
"""
Ultimate AI-Powered Launch Planning System Demo Runner
Easy-to-use script to run the complete AI demonstration
"""

import sys
import os
import subprocess
import time
from pathlib import Path

def check_dependencies():
    """Check if required dependencies are installed"""
    required_packages = [
        'numpy', 'pandas', 'scikit-learn', 'requests', 
        'pydantic', 'python-dotenv', 'psutil', 'pyyaml'
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package)
        except ImportError:
            missing_packages.append(package)
    
    if missing_packages:
        print("❌ Missing required packages:")
        for package in missing_packages:
            print(f"   - {package}")
        print("\n💡 Install missing packages with:")
        print("   pip install -r requirements-base.txt")
        return False
    
    return True

def check_optional_dependencies():
    """Check optional dependencies for enhanced features"""
    optional_packages = [
        'matplotlib', 'seaborn', 'streamlit', 'joblib'
    ]
    
    available_packages = []
    missing_packages = []
    
    for package in optional_packages:
        try:
            __import__(package)
            available_packages.append(package)
        except ImportError:
            missing_packages.append(package)
    
    print("📦 Optional Dependencies Status:")
    print(f"   ✅ Available: {', '.join(available_packages) if available_packages else 'None'}")
    if missing_packages:
        print(f"   ⚠️  Missing: {', '.join(missing_packages)}")
        print("   💡 Install with: pip install -r requirements-extras-ml.txt")
    
    return len(available_packages) > 0

def run_demo():
    """Run the ultimate AI demo"""
    print("🚀 ULTIMATE AI-POWERED LAUNCH PLANNING SYSTEM")
    print("=" * 50)
    print("Starting comprehensive AI demonstration...")
    print()
    
    try:
        # Import and run the demo
        from ultimate_ai_demo import UltimateAIDemo
        import asyncio
        
        demo = UltimateAIDemo()
        asyncio.run(demo.run_complete_demo())
        
        print("\n🎉 Demo completed successfully!")
        return True
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("💡 Make sure all required files are present:")
        print("   - ultimate_ai_demo.py")
        print("   - ai_ml_engine.py")
        print("   - predictive_analytics.py")
        print("   - intelligent_automation.py")
        print("   - metrics_system.py")
        print("   - alerting_system.py")
        print("   - config_manager.py")
        print("   - telemetry_system.py")
        return False
        
    except Exception as e:
        print(f"❌ Demo error: {e}")
        print("💡 Check the logs for more details")
        return False

def run_quick_demo():
    """Run a quick demo with basic functionality"""
    print("⚡ QUICK AI DEMO")
    print("-" * 20)
    
    try:
        # Basic AI engine demo
        from ai_ml_engine import get_ai_engine
        
        ai_engine = get_ai_engine()
        
        # Sample launch data
        launch_data = {
            "budget": 100000,
            "team_size": 8,
            "market_size": 1000000,
            "competition_level": 0.6,
            "product_complexity": 0.7,
            "timeline_days": 90,
            "marketing_budget_ratio": 0.4,
            "development_budget_ratio": 0.3,
            "team_experience": 0.8,
            "market_readiness": 0.6
        }
        
        print("🤖 AI Predictions:")
        
        # Success prediction
        success_pred = ai_engine.predict_success_probability(launch_data)
        print(f"   Success Probability: {success_pred.prediction:.1%}")
        
        # Timeline prediction
        timeline_pred = ai_engine.predict_timeline(launch_data)
        print(f"   Predicted Timeline: {timeline_pred.prediction:.0f} days")
        
        # Budget optimization
        budget_opt = ai_engine.optimize_budget_allocation(launch_data)
        print(f"   Budget Allocation:")
        for category, percentage in budget_opt.items():
            print(f"     {category.title()}: {percentage*100:.1f}%")
        
        print("\n✅ Quick demo completed!")
        return True
        
    except Exception as e:
        print(f"❌ Quick demo error: {e}")
        return False

def show_system_info():
    """Show system information and capabilities"""
    print("📋 SYSTEM INFORMATION")
    print("-" * 25)
    
    # Check Python version
    python_version = sys.version_info
    print(f"🐍 Python Version: {python_version.major}.{python_version.minor}.{python_version.micro}")
    
    # Check available modules
    modules = [
        ('AI/ML Engine', 'ai_ml_engine'),
        ('Predictive Analytics', 'predictive_analytics'),
        ('Intelligent Automation', 'intelligent_automation'),
        ('Metrics System', 'metrics_system'),
        ('Alerting System', 'alerting_system'),
        ('Config Manager', 'config_manager'),
        ('Telemetry System', 'telemetry_system')
    ]
    
    print("\n📦 Available Modules:")
    for name, module in modules:
        try:
            __import__(module)
            print(f"   ✅ {name}")
        except ImportError:
            print(f"   ❌ {name}")
    
    # Check demo file
    demo_file = Path("ultimate_ai_demo.py")
    if demo_file.exists():
        print(f"   ✅ Ultimate AI Demo")
    else:
        print(f"   ❌ Ultimate AI Demo")

def main():
    """Main function"""
    print("🚀 ULTIMATE AI-POWERED LAUNCH PLANNING SYSTEM")
    print("=" * 50)
    print("Welcome to the most advanced AI-driven launch planning system!")
    print()
    
    # Show system info
    show_system_info()
    print()
    
    # Check dependencies
    print("🔍 Checking Dependencies...")
    if not check_dependencies():
        print("\n❌ Cannot run demo without required dependencies")
        return 1
    
    optional_available = check_optional_dependencies()
    print()
    
    # Ask user what to run
    print("🎯 What would you like to do?")
    print("1. Run Complete AI Demo (recommended)")
    print("2. Run Quick Demo (basic functionality)")
    print("3. Show System Information")
    print("4. Exit")
    
    try:
        choice = input("\nEnter your choice (1-4): ").strip()
        
        if choice == "1":
            print("\n🚀 Starting Complete AI Demo...")
            success = run_demo()
            return 0 if success else 1
            
        elif choice == "2":
            print("\n⚡ Starting Quick Demo...")
            success = run_quick_demo()
            return 0 if success else 1
            
        elif choice == "3":
            show_system_info()
            return 0
            
        elif choice == "4":
            print("👋 Goodbye!")
            return 0
            
        else:
            print("❌ Invalid choice. Please enter 1, 2, 3, or 4.")
            return 1
            
    except KeyboardInterrupt:
        print("\n\n👋 Demo interrupted by user. Goodbye!")
        return 0
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        return 1

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)








