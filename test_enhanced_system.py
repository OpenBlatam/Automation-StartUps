#!/usr/bin/env python3
"""
Test Enhanced ClickUp Brain System
==================================

Comprehensive test script for the enhanced ClickUp Brain Tool Selection System.
"""

import sys
import os
import json
import time
from pathlib import Path
from datetime import datetime

def test_imports():
    """Test all system imports"""
    print("🧪 Testing system imports...")
    
    try:
        from clickup_brain_simple import SimpleClickUpBrainSystem
        print("✅ Simple system imported successfully")
    except Exception as e:
        print(f"❌ Failed to import simple system: {e}")
        return False
    
    try:
        from clickup_brain_ai_enhanced import EnhancedClickUpBrainSystem
        print("✅ AI-enhanced system imported successfully")
    except Exception as e:
        print(f"❌ Failed to import AI-enhanced system: {e}")
        return False
    
    try:
        from clickup_brain_realtime_monitor import ClickUpBrainRealtimeSystem
        print("✅ Real-time monitor imported successfully")
    except Exception as e:
        print(f"❌ Failed to import real-time monitor: {e}")
        return False
    
    try:
        from clickup_brain_api import app
        print("✅ API system imported successfully")
    except Exception as e:
        print(f"❌ Failed to import API system: {e}")
        return False
    
    return True

def test_simple_system():
    """Test simple system functionality"""
    print("\n🔍 Testing Simple System...")
    
    try:
        from clickup_brain_simple import SimpleClickUpBrainSystem
        
        system = SimpleClickUpBrainSystem()
        print("✅ Simple system initialized")
        
        # Test directory scanning
        results = system.scan_directory(".")
        if "error" in results:
            print(f"❌ Directory scan failed: {results['error']}")
            return False
        
        print(f"✅ Directory scan successful")
        print(f"   - Tools detected: {len(results['tool_usage'])}")
        print(f"   - Efficiency score: {results['efficiency_score']:.1f}/10")
        print(f"   - Categories: {', '.join(results['categories'])}")
        
        # Test report generation
        report = system.generate_report(results)
        if len(report) > 100:
            print("✅ Report generation successful")
        else:
            print("❌ Report generation failed")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ Simple system test failed: {e}")
        return False

def test_ai_enhanced_system():
    """Test AI-enhanced system functionality"""
    print("\n🤖 Testing AI-Enhanced System...")
    
    try:
        from clickup_brain_ai_enhanced import EnhancedClickUpBrainSystem
        
        system = EnhancedClickUpBrainSystem()
        print("✅ AI-enhanced system initialized")
        
        # Test AI analysis
        results = system.analyze_with_ai(".", team_size=15)
        if "error" in results:
            print(f"❌ AI analysis failed: {results['error']}")
            return False
        
        print(f"✅ AI analysis successful")
        print(f"   - Current efficiency: {results['efficiency_score']:.1f}/10")
        print(f"   - Predicted ROI: {results['predicted_roi']:.1f}x")
        print(f"   - AI recommendations: {len(results['ai_recommendations'])}")
        print(f"   - Optimization opportunities: {len(results['optimization_opportunities'])}")
        
        # Test AI report generation
        report = system.generate_ai_report(results)
        if len(report) > 200:
            print("✅ AI report generation successful")
        else:
            print("❌ AI report generation failed")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ AI-enhanced system test failed: {e}")
        return False

def test_realtime_monitor():
    """Test real-time monitoring system"""
    print("\n📊 Testing Real-time Monitor...")
    
    try:
        from clickup_brain_realtime_monitor import ClickUpBrainRealtimeSystem
        
        monitor = ClickUpBrainRealtimeSystem()
        print("✅ Real-time monitor initialized")
        
        # Test monitoring start
        if monitor.start_monitoring(".", team_size=10, check_interval=10):
            print("✅ Monitoring started successfully")
            
            # Wait for one check cycle
            time.sleep(15)
            
            # Test status retrieval
            status = monitor.get_status()
            if status['is_active']:
                print("✅ Monitoring status retrieved")
                print(f"   - Total checks: {status['total_checks']}")
                print(f"   - Alerts: {status['alerts_count']}")
            else:
                print("❌ Monitoring not active")
                return False
            
            # Test data export
            export_file = f"test_monitoring_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            if monitor.export_data(export_file):
                print("✅ Data export successful")
                # Clean up test file
                if os.path.exists(export_file):
                    os.remove(export_file)
            else:
                print("❌ Data export failed")
                return False
            
            # Stop monitoring
            if monitor.stop_monitoring():
                print("✅ Monitoring stopped successfully")
            else:
                print("❌ Failed to stop monitoring")
                return False
            
        else:
            print("❌ Failed to start monitoring")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ Real-time monitor test failed: {e}")
        return False

def test_api_system():
    """Test API system functionality"""
    print("\n🌐 Testing API System...")
    
    try:
        from clickup_brain_api import app
        
        # Test Flask app creation
        with app.test_client() as client:
            print("✅ Flask app created successfully")
            
            # Test home endpoint
            response = client.get('/')
            if response.status_code == 200:
                print("✅ Home endpoint working")
                data = response.get_json()
                if 'name' in data and 'ClickUp Brain' in data['name']:
                    print("✅ API information correct")
                else:
                    print("❌ API information incorrect")
                    return False
            else:
                print(f"❌ Home endpoint failed: {response.status_code}")
                return False
            
            # Test health endpoint
            response = client.get('/api/v1/health')
            if response.status_code == 200:
                print("✅ Health endpoint working")
                data = response.get_json()
                if data['status'] == 'healthy':
                    print("✅ Health check passed")
                else:
                    print("❌ Health check failed")
                    return False
            else:
                print(f"❌ Health endpoint failed: {response.status_code}")
                return False
            
            # Test basic analysis endpoint
            test_data = {
                'directory_path': '.',
                'team_size': 10
            }
            response = client.post('/api/v1/analysis/basic', 
                                 json=test_data,
                                 content_type='application/json')
            if response.status_code == 200:
                print("✅ Basic analysis endpoint working")
                data = response.get_json()
                if data['success']:
                    print("✅ Basic analysis successful")
                else:
                    print("❌ Basic analysis failed")
                    return False
            else:
                print(f"❌ Basic analysis endpoint failed: {response.status_code}")
                return False
        
        return True
        
    except Exception as e:
        print(f"❌ API system test failed: {e}")
        return False

def test_software_database():
    """Test software database functionality"""
    print("\n🗄️ Testing Software Database...")
    
    try:
        from clickup_brain_simple import SoftwareDatabase
        
        db = SoftwareDatabase()
        print("✅ Software database initialized")
        
        # Test tool retrieval
        clickup_tool = db.get_tool_by_name("ClickUp")
        if clickup_tool and clickup_tool['name'] == 'ClickUp':
            print("✅ Tool retrieval working")
        else:
            print("❌ Tool retrieval failed")
            return False
        
        # Test search functionality
        search_results = db.search_tools("project")
        if len(search_results) > 0:
            print(f"✅ Search functionality working ({len(search_results)} results)")
        else:
            print("❌ Search functionality failed")
            return False
        
        # Test category filtering
        pm_tools = db.get_tools_by_category("Project Management")
        if len(pm_tools) > 0:
            print(f"✅ Category filtering working ({len(pm_tools)} PM tools)")
        else:
            print("❌ Category filtering failed")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ Software database test failed: {e}")
        return False

def run_comprehensive_test():
    """Run comprehensive system test"""
    print("🚀 ClickUp Brain Enhanced System - Comprehensive Test")
    print("=" * 60)
    
    test_results = []
    
    # Test imports
    test_results.append(("Imports", test_imports()))
    
    # Test software database
    test_results.append(("Software Database", test_software_database()))
    
    # Test simple system
    test_results.append(("Simple System", test_simple_system()))
    
    # Test AI-enhanced system
    test_results.append(("AI-Enhanced System", test_ai_enhanced_system()))
    
    # Test real-time monitor
    test_results.append(("Real-time Monitor", test_realtime_monitor()))
    
    # Test API system
    test_results.append(("API System", test_api_system()))
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 TEST SUMMARY")
    print("=" * 60)
    
    passed = 0
    total = len(test_results)
    
    for test_name, result in test_results:
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"{test_name:<25} {status}")
        if result:
            passed += 1
    
    print(f"\nOverall: {passed}/{total} tests passed ({passed/total*100:.1f}%)")
    
    if passed == total:
        print("\n🎉 All tests passed! System is ready for use.")
        return True
    else:
        print(f"\n⚠️ {total-passed} tests failed. Please check the issues above.")
        return False

def main():
    """Main test function"""
    try:
        success = run_comprehensive_test()
        
        if success:
            print("\n🚀 System Status: READY FOR PRODUCTION")
            print("\n📋 Available Components:")
            print("  • Simple Analysis System")
            print("  • AI-Enhanced Analysis System")
            print("  • Real-time Monitoring System")
            print("  • REST API Server")
            print("  • Software Tools Database")
            
            print("\n🔗 Usage Examples:")
            print("  • Run API server: python clickup_brain_api.py")
            print("  • Run simple analysis: python clickup_brain_simple.py")
            print("  • Run AI analysis: python clickup_brain_ai_enhanced.py")
            print("  • Run monitoring: python clickup_brain_realtime_monitor.py")
            
        else:
            print("\n❌ System Status: NEEDS ATTENTION")
            print("Please fix the failing tests before using the system.")
        
        return success
        
    except Exception as e:
        print(f"\n💥 Test suite failed with error: {e}")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)










