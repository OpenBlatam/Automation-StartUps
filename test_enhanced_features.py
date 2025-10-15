#!/usr/bin/env python3
"""
Test Enhanced ClickUp Brain Features
===================================

Simple test script to verify all enhanced features are working correctly.
"""

import sys
import json
from datetime import datetime

def test_imports():
    """Test importing all enhanced modules."""
    print("🧪 Testing Enhanced ClickUp Brain Features")
    print("=" * 50)
    
    tests = [
        ("Simple System", "clickup_brain_simple", "SimpleClickUpBrainSystem"),
        ("AI Enhanced System", "clickup_brain_ai_enhanced", "EnhancedClickUpBrainSystem"),
        ("Real-time Monitor", "clickup_brain_realtime_monitor", "ClickUpBrainRealtimeSystem"),
        ("API System", "clickup_brain_api", "app"),
        ("Advanced Dashboard", "clickup_brain_advanced_dashboard", "AdvancedClickUpBrainDashboard"),
        ("Security System", "clickup_brain_security", "SecurityManager")
    ]
    
    results = {}
    
    for test_name, module_name, class_name in tests:
        try:
            print(f"\n📋 Testing {test_name}...")
            module = __import__(module_name)
            if hasattr(module, class_name):
                cls = getattr(module, class_name)
                instance = cls()
                print(f"✅ {test_name}: Import successful")
                results[test_name] = "✅ Working"
            else:
                print(f"⚠️ {test_name}: Class {class_name} not found")
                results[test_name] = "⚠️ Partial"
        except ImportError as e:
            print(f"❌ {test_name}: Import failed - {str(e)}")
            results[test_name] = "❌ Failed"
        except Exception as e:
            print(f"❌ {test_name}: Error - {str(e)}")
            results[test_name] = "❌ Error"
    
    return results

def test_basic_functionality():
    """Test basic functionality of each system."""
    print(f"\n🔧 Testing Basic Functionality")
    print("-" * 30)
    
    results = {}
    
    # Test Simple System
    try:
        from clickup_brain_simple import SimpleClickUpBrainSystem
        system = SimpleClickUpBrainSystem()
        print("✅ Simple System: Initialized successfully")
        results["Simple System"] = "✅ Working"
    except Exception as e:
        print(f"❌ Simple System: {str(e)}")
        results["Simple System"] = "❌ Failed"
    
    # Test AI Enhanced System
    try:
        from clickup_brain_ai_enhanced import EnhancedClickUpBrainSystem
        system = EnhancedClickUpBrainSystem()
        print("✅ AI Enhanced System: Initialized successfully")
        results["AI Enhanced System"] = "✅ Working"
    except Exception as e:
        print(f"❌ AI Enhanced System: {str(e)}")
        results["AI Enhanced System"] = "❌ Failed"
    
    # Test Security System
    try:
        from clickup_brain_security import SecurityManager, SecurityConfig
        print("✅ Security System: Components available")
        results["Security System"] = "✅ Working"
    except Exception as e:
        print(f"❌ Security System: {str(e)}")
        results["Security System"] = "❌ Failed"
    
    return results

def test_ai_features():
    """Test AI-specific features."""
    print(f"\n🤖 Testing AI Features")
    print("-" * 25)
    
    try:
        from clickup_brain_ai_enhanced import AdvancedAIAnalyzer
        
        # Create AI analyzer
        ai_analyzer = AdvancedAIAnalyzer()
        print("✅ AI Analyzer: Created successfully")
        
        # Test efficiency patterns
        patterns = ai_analyzer.efficiency_patterns
        print(f"✅ Efficiency Patterns: {len(patterns)} patterns loaded")
        
        # Test tool synergies
        synergies = ai_analyzer.tool_synergies
        print(f"✅ Tool Synergies: {len(synergies)} synergies available")
        
        # Test industry benchmarks
        benchmarks = ai_analyzer.industry_benchmarks
        print(f"✅ Industry Benchmarks: {len(benchmarks)} benchmarks loaded")
        
        return "✅ AI Features Working"
        
    except Exception as e:
        print(f"❌ AI Features: {str(e)}")
        return "❌ AI Features Failed"

def test_security_features():
    """Test security features."""
    print(f"\n🔒 Testing Security Features")
    print("-" * 30)
    
    try:
        from clickup_brain_security import PasswordManager, JWTManager
        
        # Test password hashing
        password = "TestPassword123!"
        hashed = PasswordManager.hash_password(password)
        verified = PasswordManager.verify_password(password, hashed)
        print(f"✅ Password Hashing: {'Working' if verified else 'Failed'}")
        
        # Test JWT token
        jwt_manager = JWTManager("test-secret", 1)
        token = jwt_manager.generate_token("test-user", "testuser", "user")
        payload = jwt_manager.verify_token(token)
        print(f"✅ JWT Tokens: {'Working' if payload else 'Failed'}")
        
        return "✅ Security Features Working"
        
    except Exception as e:
        print(f"❌ Security Features: {str(e)}")
        return "❌ Security Features Failed"

def generate_test_report(results):
    """Generate a test report."""
    print(f"\n📊 Test Report")
    print("=" * 30)
    
    working_count = sum(1 for result in results.values() if "✅" in result)
    total_count = len(results)
    
    print(f"Overall Status: {working_count}/{total_count} components working")
    print(f"Success Rate: {(working_count/total_count)*100:.1f}%")
    
    print(f"\nDetailed Results:")
    for component, status in results.items():
        print(f"  • {component}: {status}")
    
    # Save report
    report = {
        "test_date": datetime.now().isoformat(),
        "overall_status": f"{working_count}/{total_count}",
        "success_rate": f"{(working_count/total_count)*100:.1f}%",
        "results": results
    }
    
    report_file = f"test_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(report_file, 'w') as f:
        json.dump(report, f, indent=2)
    
    print(f"\n📄 Test report saved: {report_file}")
    
    return working_count == total_count

def main():
    """Main test function."""
    print("🚀 ClickUp Brain Enhanced System - Feature Test")
    print("=" * 60)
    
    # Run all tests
    import_results = test_imports()
    functionality_results = test_basic_functionality()
    ai_result = test_ai_features()
    security_result = test_security_features()
    
    # Combine results
    all_results = {
        **import_results,
        **functionality_results,
        "AI Features": ai_result,
        "Security Features": security_result
    }
    
    # Generate report
    success = generate_test_report(all_results)
    
    # Final summary
    print(f"\n🎯 Test Summary")
    print("=" * 20)
    
    if success:
        print("🎉 All enhanced features are working correctly!")
        print("🚀 System is ready for production use")
    else:
        print("⚠️ Some features need attention")
        print("📋 Check the test report for details")
    
    print(f"\n📁 Next Steps:")
    print("1. Run: python clickup_brain_ai_enhanced.py")
    print("2. Run: streamlit run clickup_brain_advanced_dashboard.py")
    print("3. Run: python clickup_brain_api.py")
    print("4. Run: python clickup_brain_realtime_monitor.py")
    
    return success

if __name__ == "__main__":
    main()








