#!/usr/bin/env python3
"""
ClickUp Brain Tool Selection System - Example Usage
==================================================

This script demonstrates how to use the ClickUp Brain Tool Selection System
to analyze documents and generate insights about software tool usage.
"""

import os
import json
from pathlib import Path
from clickup_brain_tool_selection_system import ToolSelectionSystem

def main():
    """Demonstrate the ClickUp Brain Tool Selection System."""
    
    print("🧠 ClickUp Brain Tool Selection System - Example Usage")
    print("=" * 60)
    
    # Initialize the system
    print("\n1. Initializing the system...")
    system = ToolSelectionSystem()
    print("✅ System initialized successfully!")
    
    # Example 1: Analyze current directory
    print("\n2. Analyzing current directory...")
    current_dir = "."
    
    try:
        results = system.scan_directory(current_dir)
        print(f"✅ Successfully analyzed {results['total_files_scanned']} files")
        
        # Display key metrics
        efficiency = results['efficiency_analysis']
        clickup = results['clickup_insights']
        
        print(f"\n📊 Key Metrics:")
        print(f"   • Efficiency Score: {efficiency['efficiency_score']:.1f}/100")
        print(f"   • Tools Found: {len(efficiency['tool_usage'])}")
        print(f"   • ClickUp Mentions: {clickup['clickup_mentions']}")
        print(f"   • Potential Efficiency Boost: {clickup['team_efficiency_boost']:.1f}%")
        
        # Display top tools
        if efficiency['tool_usage']:
            print(f"\n🛠️ Top Software Tools Found:")
            sorted_tools = sorted(efficiency['tool_usage'].items(), key=lambda x: x[1], reverse=True)
            for tool, count in sorted_tools[:5]:
                print(f"   • {tool}: {count} mentions")
        
        # Display insights
        if efficiency['insights']:
            print(f"\n💡 Key Insights:")
            for insight in efficiency['insights'][:3]:
                print(f"   • {insight}")
        
        # Display recommendations
        if efficiency['recommendations']:
            print(f"\n📈 Top Recommendations:")
            for rec in efficiency['recommendations'][:3]:
                print(f"   • {rec}")
        
        # Generate and save report
        print(f"\n3. Generating comprehensive report...")
        report = system.generate_report(results)
        
        # Save report to file
        report_file = "clickup_brain_example_report.md"
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write(report)
        print(f"✅ Report saved to: {report_file}")
        
        # Save analysis results
        results_file = "clickup_brain_example_results.json"
        system.save_analysis(results, results_file)
        print(f"✅ Analysis results saved to: {results_file}")
        
    except Exception as e:
        print(f"❌ Error analyzing directory: {str(e)}")
        return
    
    # Example 2: Search for specific tools
    print(f"\n4. Searching for specific tools...")
    
    # Search for project management tools
    pm_tools = system.software_db.search_tools("project management")
    print(f"\n📋 Project Management Tools Found:")
    for tool in pm_tools[:3]:
        print(f"   • {tool.name} (Score: {tool.popularity_score}/10)")
        print(f"     {tool.description}")
        print(f"     Benefits: {', '.join(tool.benefits[:2])}...")
        print()
    
    # Search for communication tools
    comm_tools = system.software_db.search_tools("communication")
    print(f"💬 Communication Tools Found:")
    for tool in comm_tools[:3]:
        print(f"   • {tool.name} (Score: {tool.popularity_score}/10)")
        print(f"     {tool.description}")
        print(f"     Benefits: {', '.join(tool.benefits[:2])}...")
        print()
    
    # Example 3: Get detailed tool information
    print(f"\n5. Getting detailed tool information...")
    
    # Get ClickUp details
    clickup_tool = system.software_db.get_tool_by_name("ClickUp")
    if clickup_tool:
        print(f"🔍 ClickUp Tool Details:")
        print(f"   • Category: {clickup_tool.category}")
        print(f"   • Popularity Score: {clickup_tool.popularity_score}/10")
        print(f"   • Efficiency Impact: {clickup_tool.efficiency_impact}")
        print(f"   • Team Size Recommendation: {clickup_tool.team_size_recommendation}")
        print(f"   • Cost Tier: {clickup_tool.cost_tier}")
        print(f"   • Learning Curve: {clickup_tool.learning_curve}")
        print(f"   • Support Quality: {clickup_tool.support_quality}")
        print(f"   • Integration Capabilities: {', '.join(clickup_tool.integration_capabilities[:3])}...")
        print(f"   • Key Benefits:")
        for benefit in clickup_tool.benefits[:3]:
            print(f"     - {benefit}")
    
    # Example 4: Analyze specific document types
    print(f"\n6. Analyzing specific document types...")
    
    # Find Python files
    python_files = list(Path(".").rglob("*.py"))
    if python_files:
        print(f"🐍 Found {len(python_files)} Python files")
        
        # Analyze first few Python files
        for py_file in python_files[:3]:
            try:
                analysis = system.document_scanner.scan_document(str(py_file))
                if analysis.software_mentions:
                    print(f"   • {py_file.name}: {len(analysis.software_mentions)} software mentions")
                    for mention in analysis.software_mentions[:2]:
                        print(f"     - {mention['tool_name']} ({mention['mention_type']})")
                else:
                    print(f"   • {py_file.name}: No software mentions found")
            except Exception as e:
                print(f"   • {py_file.name}: Error analyzing - {str(e)}")
    
    # Find Markdown files
    md_files = list(Path(".").rglob("*.md"))
    if md_files:
        print(f"\n📝 Found {len(md_files)} Markdown files")
        
        # Analyze first few Markdown files
        for md_file in md_files[:3]:
            try:
                analysis = system.document_scanner.scan_document(str(md_file))
                if analysis.software_mentions:
                    print(f"   • {md_file.name}: {len(analysis.software_mentions)} software mentions")
                    for mention in analysis.software_mentions[:2]:
                        print(f"     - {mention['tool_name']} ({mention['mention_type']})")
                else:
                    print(f"   • {md_file.name}: No software mentions found")
            except Exception as e:
                print(f"   • {md_file.name}: Error analyzing - {str(e)}")
    
    # Example 5: Generate ClickUp-specific insights
    print(f"\n7. Generating ClickUp-specific insights...")
    
    if 'results' in locals():
        clickup_insights = results['clickup_insights']
        
        print(f"🧠 ClickUp Brain Insights:")
        print(f"   • ClickUp Mentions: {clickup_insights['clickup_mentions']}")
        print(f"   • Potential Efficiency Boost: {clickup_insights['team_efficiency_boost']:.1f}%")
        
        if clickup_insights['integration_opportunities']:
            print(f"   • Integration Opportunities:")
            for opp in clickup_insights['integration_opportunities'][:3]:
                print(f"     - {opp}")
        
        if clickup_insights['workflow_optimizations']:
            print(f"   • Workflow Optimizations:")
            for opt in clickup_insights['workflow_optimizations'][:3]:
                print(f"     - {opt}")
        
        if clickup_insights['recommended_clickup_features']:
            print(f"   • Recommended ClickUp Features:")
            for feature in clickup_insights['recommended_clickup_features'][:3]:
                print(f"     - {feature}")
    
    # Summary
    print(f"\n" + "=" * 60)
    print(f"🎉 Example completed successfully!")
    print(f"\n📁 Generated Files:")
    print(f"   • {report_file} - Comprehensive analysis report")
    print(f"   • {results_file} - Detailed analysis results (JSON)")
    
    print(f"\n🚀 Next Steps:")
    print(f"   1. Review the generated report for insights")
    print(f"   2. Run the web dashboard: streamlit run clickup_brain_dashboard.py")
    print(f"   3. Implement the recommended tool optimizations")
    print(f"   4. Monitor efficiency improvements over time")
    
    print(f"\n💡 Pro Tips:")
    print(f"   • Use the web dashboard for interactive analysis")
    print(f"   • Regularly scan your documents to track tool usage")
    print(f"   • Focus on high-impact recommendations first")
    print(f"   • Consider ClickUp adoption for maximum efficiency gains")

if __name__ == "__main__":
    main()








