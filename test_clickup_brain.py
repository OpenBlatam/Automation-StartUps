#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Simple test script for ClickUp Brain system
"""

def test_basic_functionality():
    """Test basic functionality of ClickUp Brain system"""
    print("🧠 Testing ClickUp Brain System...")
    
    try:
        # Test import
        from clickup_brain_system import ClickUpBrainSystem
        print("✅ Import successful")
        
        # Initialize system
        brain = ClickUpBrainSystem()
        print("✅ System initialization successful")
        
        # Test basic engagement tactics
        tactics = brain.engagement_system.get_budget_friendly_tactics(5000, ["increase_engagement"])
        print(f"✅ Engagement tactics generated: {len(tactics['recommended_tactics'])} tactics")
        
        # Test external data integration
        insights = brain.data_integration.get_social_media_trends("tiktok")
        print("✅ External data integration working")
        
        # Test trend analysis
        trend_summary = brain.get_trend_summary("technology", "30d")
        print(f"✅ Trend analysis working: {trend_summary['trends_analyzed']} trends")
        
        print("\n🎉 All tests passed! ClickUp Brain system is working correctly.")
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {str(e)}")
        return False

if __name__ == "__main__":
    test_basic_functionality()








