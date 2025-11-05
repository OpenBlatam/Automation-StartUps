#!/usr/bin/env python3
"""
ClickUp Brain Simple System
===========================

Basic tool analysis and recommendation system for team efficiency optimization.
"""

import os
import json
import logging
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict
import re

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class ToolUsage:
    """Tool usage data structure"""
    tool_name: str
    category: str
    usage_frequency: str
    team_size: int
    efficiency_score: float
    cost_per_user: float
    integration_count: int

@dataclass
class AnalysisResult:
    """Analysis result data structure"""
    directory_path: str
    total_files: int
    tool_usage: Dict[str, ToolUsage]
    categories: List[str]
    efficiency_score: float
    recommendations: List[str]
    timestamp: str

class SoftwareDatabase:
    """Software tools database"""
    
    def __init__(self):
        """Initialize software database"""
        self.tools = self._load_tools_database()
    
    def _load_tools_database(self) -> Dict[str, Dict]:
        """Load comprehensive software tools database"""
        return {
            # Project Management
            "ClickUp": {
                "name": "ClickUp",
                "category": "Project Management",
                "description": "All-in-one project management platform",
                "efficiency_score": 9.2,
                "cost_per_user": 5.0,
                "team_size_optimal": "5-1000+",
                "integrations": ["Slack", "GitHub", "Figma", "Google Workspace", "Zoom"],
                "learning_curve": "Medium",
                "roi_timeline": "1-2 months"
            },
            "Asana": {
                "name": "Asana",
                "category": "Project Management",
                "description": "Task and project management tool",
                "efficiency_score": 8.5,
                "cost_per_user": 10.99,
                "team_size_optimal": "5-500",
                "integrations": ["Slack", "Google Workspace", "Microsoft Teams"],
                "learning_curve": "Easy",
                "roi_timeline": "2-3 months"
            },
            "Trello": {
                "name": "Trello",
                "category": "Project Management",
                "description": "Visual project management with boards",
                "efficiency_score": 7.8,
                "cost_per_user": 5.0,
                "team_size_optimal": "2-100",
                "integrations": ["Slack", "Google Workspace", "GitHub"],
                "learning_curve": "Easy",
                "roi_timeline": "1 month"
            },
            "Monday.com": {
                "name": "Monday.com",
                "category": "Project Management",
                "description": "Work operating system for teams",
                "efficiency_score": 8.8,
                "cost_per_user": 8.0,
                "team_size_optimal": "5-200",
                "integrations": ["Slack", "Google Workspace", "Microsoft Teams", "Zoom"],
                "learning_curve": "Medium",
                "roi_timeline": "2-3 months"
            },
            "Jira": {
                "name": "Jira",
                "category": "Project Management",
                "description": "Issue and project tracking for software teams",
                "efficiency_score": 8.0,
                "cost_per_user": 7.0,
                "team_size_optimal": "10-1000+",
                "integrations": ["Confluence", "Bitbucket", "Slack", "GitHub"],
                "learning_curve": "Hard",
                "roi_timeline": "3-4 months"
            },
            
            # Communication
            "Slack": {
                "name": "Slack",
                "category": "Communication",
                "description": "Team communication and collaboration platform",
                "efficiency_score": 9.0,
                "cost_per_user": 6.67,
                "team_size_optimal": "5-1000+",
                "integrations": ["ClickUp", "Google Workspace", "GitHub", "Zoom"],
                "learning_curve": "Easy",
                "roi_timeline": "1 month"
            },
            "Microsoft Teams": {
                "name": "Microsoft Teams",
                "category": "Communication",
                "description": "Unified communication and collaboration platform",
                "efficiency_score": 8.5,
                "cost_per_user": 5.0,
                "team_size_optimal": "10-1000+",
                "integrations": ["Office 365", "SharePoint", "OneDrive"],
                "learning_curve": "Medium",
                "roi_timeline": "1-2 months"
            },
            "Discord": {
                "name": "Discord",
                "category": "Communication",
                "description": "Voice, video, and text communication",
                "efficiency_score": 7.5,
                "cost_per_user": 0.0,
                "team_size_optimal": "5-100",
                "integrations": ["GitHub", "Spotify", "YouTube"],
                "learning_curve": "Easy",
                "roi_timeline": "1 month"
            },
            
            # Development
            "GitHub": {
                "name": "GitHub",
                "category": "Development",
                "description": "Code repository and collaboration platform",
                "efficiency_score": 9.5,
                "cost_per_user": 4.0,
                "team_size_optimal": "2-1000+",
                "integrations": ["ClickUp", "Slack", "Jira", "Figma"],
                "learning_curve": "Medium",
                "roi_timeline": "1 month"
            },
            "GitLab": {
                "name": "GitLab",
                "category": "Development",
                "description": "DevOps platform with Git repository management",
                "efficiency_score": 8.8,
                "cost_per_user": 4.0,
                "team_size_optimal": "5-1000+",
                "integrations": ["Slack", "Jira", "Confluence"],
                "learning_curve": "Medium",
                "roi_timeline": "2-3 months"
            },
            "Bitbucket": {
                "name": "Bitbucket",
                "category": "Development",
                "description": "Git repository management by Atlassian",
                "efficiency_score": 8.0,
                "cost_per_user": 3.0,
                "team_size_optimal": "5-500",
                "integrations": ["Jira", "Confluence", "Slack"],
                "learning_curve": "Medium",
                "roi_timeline": "1-2 months"
            },
            "Docker": {
                "name": "Docker",
                "category": "Development",
                "description": "Containerization platform",
                "efficiency_score": 9.0,
                "cost_per_user": 0.0,
                "team_size_optimal": "5-1000+",
                "integrations": ["GitHub", "AWS", "Azure", "Google Cloud"],
                "learning_curve": "Hard",
                "roi_timeline": "2-3 months"
            },
            
            # Design
            "Figma": {
                "name": "Figma",
                "category": "Design",
                "description": "Collaborative interface design tool",
                "efficiency_score": 9.2,
                "cost_per_user": 12.0,
                "team_size_optimal": "2-1000+",
                "integrations": ["ClickUp", "Slack", "GitHub", "Notion"],
                "learning_curve": "Medium",
                "roi_timeline": "1-2 months"
            },
            "Adobe Creative Suite": {
                "name": "Adobe Creative Suite",
                "category": "Design",
                "description": "Professional creative software suite",
                "efficiency_score": 8.5,
                "cost_per_user": 52.99,
                "team_size_optimal": "1-100",
                "integrations": ["Creative Cloud", "Behance", "Stock"],
                "learning_curve": "Hard",
                "roi_timeline": "3-6 months"
            },
            "Sketch": {
                "name": "Sketch",
                "category": "Design",
                "description": "Digital design toolkit",
                "efficiency_score": 8.0,
                "cost_per_user": 9.0,
                "team_size_optimal": "1-50",
                "integrations": ["Zeplin", "InVision", "Abstract"],
                "learning_curve": "Medium",
                "roi_timeline": "2-3 months"
            },
            "Canva": {
                "name": "Canva",
                "category": "Design",
                "description": "Graphic design platform",
                "efficiency_score": 7.5,
                "cost_per_user": 12.99,
                "team_size_optimal": "1-100",
                "integrations": ["Google Workspace", "Microsoft Office", "Slack"],
                "learning_curve": "Easy",
                "roi_timeline": "1 month"
            },
            
            # Documentation
            "Notion": {
                "name": "Notion",
                "category": "Documentation",
                "description": "All-in-one workspace for notes and docs",
                "efficiency_score": 8.8,
                "cost_per_user": 8.0,
                "team_size_optimal": "2-1000+",
                "integrations": ["Slack", "Google Workspace", "GitHub"],
                "learning_curve": "Medium",
                "roi_timeline": "1-2 months"
            },
            "Confluence": {
                "name": "Confluence",
                "category": "Documentation",
                "description": "Team collaboration and documentation platform",
                "efficiency_score": 8.0,
                "cost_per_user": 5.0,
                "team_size_optimal": "10-1000+",
                "integrations": ["Jira", "Slack", "Microsoft Teams"],
                "learning_curve": "Medium",
                "roi_timeline": "2-3 months"
            },
            "Google Workspace": {
                "name": "Google Workspace",
                "category": "Documentation",
                "description": "Cloud-based productivity suite",
                "efficiency_score": 8.5,
                "cost_per_user": 6.0,
                "team_size_optimal": "5-1000+",
                "integrations": ["Slack", "Zoom", "ClickUp", "Figma"],
                "learning_curve": "Easy",
                "roi_timeline": "1 month"
            },
            "Microsoft Office 365": {
                "name": "Microsoft Office 365",
                "category": "Documentation",
                "description": "Productivity suite with cloud services",
                "efficiency_score": 8.2,
                "cost_per_user": 6.0,
                "team_size_optimal": "5-1000+",
                "integrations": ["Teams", "SharePoint", "OneDrive"],
                "learning_curve": "Easy",
                "roi_timeline": "1 month"
            },
            
            # Analytics
            "Google Analytics": {
                "name": "Google Analytics",
                "category": "Analytics",
                "description": "Web analytics service",
                "efficiency_score": 8.5,
                "cost_per_user": 0.0,
                "team_size_optimal": "1-1000+",
                "integrations": ["Google Ads", "Google Tag Manager", "Data Studio"],
                "learning_curve": "Medium",
                "roi_timeline": "1-2 months"
            },
            "Mixpanel": {
                "name": "Mixpanel",
                "category": "Analytics",
                "description": "Product analytics platform",
                "efficiency_score": 8.8,
                "cost_per_user": 25.0,
                "team_size_optimal": "5-500",
                "integrations": ["Slack", "Segment", "Zapier"],
                "learning_curve": "Medium",
                "roi_timeline": "2-3 months"
            },
            "Amplitude": {
                "name": "Amplitude",
                "category": "Analytics",
                "description": "Digital analytics platform",
                "efficiency_score": 8.7,
                "cost_per_user": 20.0,
                "team_size_optimal": "5-1000+",
                "integrations": ["Slack", "Segment", "Zapier"],
                "learning_curve": "Medium",
                "roi_timeline": "2-3 months"
            },
            
            # CRM
            "Salesforce": {
                "name": "Salesforce",
                "category": "CRM",
                "description": "Customer relationship management platform",
                "efficiency_score": 9.0,
                "cost_per_user": 25.0,
                "team_size_optimal": "10-1000+",
                "integrations": ["Slack", "Google Workspace", "Microsoft Teams"],
                "learning_curve": "Hard",
                "roi_timeline": "3-6 months"
            },
            "HubSpot": {
                "name": "HubSpot",
                "category": "CRM",
                "description": "Inbound marketing and sales platform",
                "efficiency_score": 8.5,
                "cost_per_user": 45.0,
                "team_size_optimal": "5-500",
                "integrations": ["Slack", "Google Workspace", "Zoom"],
                "learning_curve": "Medium",
                "roi_timeline": "2-3 months"
            },
            "Pipedrive": {
                "name": "Pipedrive",
                "category": "CRM",
                "description": "Sales-focused CRM platform",
                "efficiency_score": 8.2,
                "cost_per_user": 12.5,
                "team_size_optimal": "5-200",
                "integrations": ["Slack", "Google Workspace", "Zapier"],
                "learning_curve": "Easy",
                "roi_timeline": "1-2 months"
            }
        }
    
    def get_tool_by_name(self, name: str) -> Optional[Dict]:
        """Get tool by name"""
        return self.tools.get(name)
    
    def search_tools(self, query: str) -> List[Dict]:
        """Search tools by name or description"""
        query_lower = query.lower()
        results = []
        
        for tool in self.tools.values():
            if (query_lower in tool['name'].lower() or 
                query_lower in tool['description'].lower() or
                query_lower in tool['category'].lower()):
                results.append(tool)
        
        return results
    
    def get_tools_by_category(self, category: str) -> List[Dict]:
        """Get tools by category"""
        return [tool for tool in self.tools.values() if tool['category'] == category]

class SimpleClickUpBrainSystem:
    """Simple ClickUp Brain system for basic analysis"""
    
    def __init__(self):
        """Initialize simple system"""
        self.software_db = SoftwareDatabase()
        self.analysis_cache = {}
    
    def scan_directory(self, directory_path: str) -> Dict[str, Any]:
        """
        Scan directory for tool usage patterns
        
        Args:
            directory_path: Path to directory to analyze
        
        Returns:
            Analysis results
        """
        try:
            directory_path = Path(directory_path)
            
            if not directory_path.exists():
                return {"error": f"Directory not found: {directory_path}"}
            
            # Analyze files for tool usage patterns
            tool_usage = self._analyze_tool_usage(directory_path)
            categories = list(set(tool['category'] for tool in tool_usage.values()))
            
            # Calculate efficiency score
            efficiency_score = self._calculate_efficiency_score(tool_usage)
            
            # Generate recommendations
            recommendations = self._generate_recommendations(tool_usage, categories)
            
            result = AnalysisResult(
                directory_path=str(directory_path),
                total_files=len(list(directory_path.rglob('*'))),
                tool_usage=tool_usage,
                categories=categories,
                efficiency_score=efficiency_score,
                recommendations=recommendations,
                timestamp=datetime.now().isoformat()
            )
            
            return asdict(result)
            
        except Exception as e:
            logger.error(f"Error scanning directory: {str(e)}")
            return {"error": f"Analysis failed: {str(e)}"}
    
    def _analyze_tool_usage(self, directory_path: Path) -> Dict[str, ToolUsage]:
        """Analyze tool usage patterns in directory"""
        tool_usage = {}
        
        # File patterns that indicate tool usage
        tool_patterns = {
            "ClickUp": [".clickup", "clickup", "CLICKUP"],
            "GitHub": [".git", "github", "GITHUB", ".github"],
            "Slack": ["slack", "SLACK", ".slack"],
            "Figma": ["figma", "FIGMA", ".figma"],
            "Notion": ["notion", "NOTION", ".notion"],
            "Jira": ["jira", "JIRA", ".jira"],
            "Trello": ["trello", "TRELLO", ".trello"],
            "Asana": ["asana", "ASANA", ".asana"],
            "Docker": ["Dockerfile", "docker-compose", ".docker"],
            "Google Workspace": ["google", "GOOGLE", ".google"],
            "Microsoft Teams": ["teams", "TEAMS", ".teams"],
            "Confluence": ["confluence", "CONFLUENCE", ".confluence"],
            "Salesforce": ["salesforce", "SALESFORCE", ".salesforce"],
            "HubSpot": ["hubspot", "HUBSPOT", ".hubspot"]
        }
        
        # Scan files for tool indicators
        for file_path in directory_path.rglob('*'):
            if file_path.is_file():
                try:
                    # Check filename
                    filename = file_path.name.lower()
                    
                    # Check file content (first 1000 characters)
                    try:
                        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                            content = f.read(1000).lower()
                    except:
                        content = ""
                    
                    # Check for tool patterns
                    for tool_name, patterns in tool_patterns.items():
                        if any(pattern.lower() in filename or pattern.lower() in content for pattern in patterns):
                            if tool_name not in tool_usage:
                                tool_info = self.software_db.get_tool_by_name(tool_name)
                                if tool_info:
                                    tool_usage[tool_name] = ToolUsage(
                                        tool_name=tool_name,
                                        category=tool_info['category'],
                                        usage_frequency="High",
                                        team_size=10,  # Default
                                        efficiency_score=tool_info['efficiency_score'],
                                        cost_per_user=tool_info['cost_per_user'],
                                        integration_count=len(tool_info.get('integrations', []))
                                    )
                except Exception as e:
                    continue
        
        return tool_usage
    
    def _calculate_efficiency_score(self, tool_usage: Dict[str, ToolUsage]) -> float:
        """Calculate overall efficiency score"""
        if not tool_usage:
            return 0.0
        
        total_score = sum(tool.efficiency_score for tool in tool_usage.values())
        return total_score / len(tool_usage)
    
    def _generate_recommendations(self, tool_usage: Dict[str, ToolUsage], categories: List[str]) -> List[str]:
        """Generate basic recommendations"""
        recommendations = []
        
        # Check for missing ClickUp
        if "ClickUp" not in tool_usage:
            recommendations.append("Consider adopting ClickUp for comprehensive project management")
        
        # Check for tool diversity
        if len(tool_usage) < 3:
            recommendations.append("Consider diversifying your tool stack for better efficiency")
        
        # Category-specific recommendations
        if "Project Management" not in categories:
            recommendations.append("Add a project management tool to improve team coordination")
        
        if "Communication" not in categories:
            recommendations.append("Implement a team communication platform")
        
        if "Development" not in categories and any("dev" in cat.lower() for cat in categories):
            recommendations.append("Consider development tools for better code management")
        
        return recommendations
    
    def generate_report(self, analysis_results: Dict[str, Any]) -> str:
        """Generate analysis report"""
        report = f"""
# ClickUp Brain Analysis Report

## Executive Summary
- **Directory**: {analysis_results.get('directory_path', 'N/A')}
- **Total Files**: {analysis_results.get('total_files', 0)}
- **Tools Detected**: {len(analysis_results.get('tool_usage', {}))}
- **Efficiency Score**: {analysis_results.get('efficiency_score', 0):.1f}/10
- **Analysis Date**: {analysis_results.get('timestamp', 'N/A')}

## Tool Usage Analysis

"""
        
        tool_usage = analysis_results.get('tool_usage', {})
        if tool_usage:
            for tool_name, tool_data in tool_usage.items():
                report += f"""
### {tool_name}
- **Category**: {tool_data.get('category', 'N/A')}
- **Efficiency Score**: {tool_data.get('efficiency_score', 0):.1f}/10
- **Cost per User**: ${tool_data.get('cost_per_user', 0):.2f}
- **Usage Frequency**: {tool_data.get('usage_frequency', 'N/A')}
"""
        else:
            report += "No tools detected in the analyzed directory.\n"
        
        report += f"""
## Categories
{', '.join(analysis_results.get('categories', []))}

## Recommendations
"""
        
        recommendations = analysis_results.get('recommendations', [])
        if recommendations:
            for i, rec in enumerate(recommendations, 1):
                report += f"{i}. {rec}\n"
        else:
            report += "No specific recommendations at this time.\n"
        
        report += f"""
## Next Steps
1. Review the tool usage analysis
2. Consider implementing recommended tools
3. Evaluate current tool efficiency
4. Plan tool integration strategy

---
*Report generated by ClickUp Brain Simple System*
"""
        
        return report

def main():
    """Main function for testing"""
    print("🧠 ClickUp Brain Simple System")
    print("=" * 40)
    
    # Initialize system
    system = SimpleClickUpBrainSystem()
    
    # Test directory analysis
    test_directory = "."
    print(f"Analyzing directory: {test_directory}")
    
    results = system.scan_directory(test_directory)
    
    if "error" in results:
        print(f"Error: {results['error']}")
    else:
        print(f"Analysis complete!")
        print(f"Tools detected: {len(results['tool_usage'])}")
        print(f"Efficiency score: {results['efficiency_score']:.1f}/10")
        print(f"Categories: {', '.join(results['categories'])}")
        
        # Generate report
        report = system.generate_report(results)
        print("\n" + "="*50)
        print("ANALYSIS REPORT")
        print("="*50)
        print(report)

if __name__ == "__main__":
    main()