#!/usr/bin/env python3
"""
ClickUp Brain Tool Selection System
==================================

A comprehensive system that scans documents to identify popular software tools
and summarizes their key benefits to boost team efficiency.

Features:
- Document scanning and analysis
- Software tool identification
- Benefits summarization
- Team efficiency recommendations
- ClickUp Brain integration
"""

import os
import re
import json
import logging
from typing import Dict, List, Tuple, Optional, Any
from dataclasses import dataclass, asdict
from pathlib import Path
import hashlib
from datetime import datetime
import yaml

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@dataclass
class SoftwareTool:
    """Represents a software tool with its properties and benefits."""
    name: str
    category: str
    description: str
    benefits: List[str]
    popularity_score: float
    efficiency_impact: str
    team_size_recommendation: str
    cost_tier: str
    integration_capabilities: List[str]
    learning_curve: str
    support_quality: str
    last_updated: str

@dataclass
class DocumentAnalysis:
    """Represents the analysis of a document."""
    file_path: str
    file_hash: str
    software_mentions: List[Dict[str, Any]]
    analysis_timestamp: str
    confidence_score: float
    recommendations: List[str]

class SoftwareDatabase:
    """Database of known software tools and their characteristics."""
    
    def __init__(self):
        self.tools = self._initialize_tools_database()
        self.categories = self._get_categories()
    
    def _initialize_tools_database(self) -> Dict[str, SoftwareTool]:
        """Initialize the software tools database."""
        tools = {
            # Project Management Tools
            "clickup": SoftwareTool(
                name="ClickUp",
                category="Project Management",
                description="All-in-one project management platform with customizable views",
                benefits=[
                    "Unified workspace for all project needs",
                    "Customizable views (List, Board, Calendar, Gantt)",
                    "Time tracking and reporting",
                    "Collaborative features with real-time updates",
                    "Integration with 1000+ tools",
                    "AI-powered automation and insights"
                ],
                popularity_score=9.2,
                efficiency_impact="High - Reduces context switching by 60%",
                team_size_recommendation="5-500+ team members",
                cost_tier="Freemium to Enterprise",
                integration_capabilities=["Slack", "Google Workspace", "GitHub", "Figma", "Zapier"],
                learning_curve="Medium - 2-3 weeks for full adoption",
                support_quality="Excellent - 24/7 support with extensive documentation",
                last_updated="2025-01-06"
            ),
            
            "notion": SoftwareTool(
                name="Notion",
                category="Productivity & Documentation",
                description="All-in-one workspace for notes, docs, wikis, and project management",
                benefits=[
                    "Flexible database and page structure",
                    "Powerful collaboration features",
                    "Template library for common workflows",
                    "API for custom integrations",
                    "Mobile and desktop apps",
                    "Version history and permissions"
                ],
                popularity_score=8.8,
                efficiency_impact="High - Centralizes knowledge management",
                team_size_recommendation="1-100+ team members",
                cost_tier="Freemium to Enterprise",
                integration_capabilities=["Slack", "Google Drive", "GitHub", "Figma", "Zapier"],
                learning_curve="Medium - 1-2 weeks for basic usage",
                support_quality="Good - Community-driven with official support",
                last_updated="2025-01-06"
            ),
            
            "slack": SoftwareTool(
                name="Slack",
                category="Communication",
                description="Business communication platform with channels, direct messages, and integrations",
                benefits=[
                    "Organized communication channels",
                    "File sharing and collaboration",
                    "Voice and video calls",
                    "Workflow automation with bots",
                    "Searchable message history",
                    "Integration with 2000+ apps"
                ],
                popularity_score=9.5,
                efficiency_impact="Very High - Reduces email by 40%",
                team_size_recommendation="2-10000+ team members",
                cost_tier="Freemium to Enterprise",
                integration_capabilities=["Google Workspace", "Microsoft 365", "GitHub", "Salesforce", "Zapier"],
                learning_curve="Low - 1 week for basic usage",
                support_quality="Excellent - Comprehensive support and training",
                last_updated="2025-01-06"
            ),
            
            "figma": SoftwareTool(
                name="Figma",
                category="Design & Prototyping",
                description="Collaborative interface design tool with real-time editing",
                benefits=[
                    "Real-time collaborative design",
                    "Prototyping and user testing",
                    "Design system management",
                    "Developer handoff tools",
                    "Version control for designs",
                    "Plugin ecosystem"
                ],
                popularity_score=9.0,
                efficiency_impact="High - Accelerates design-to-development workflow",
                team_size_recommendation="1-500+ team members",
                cost_tier="Freemium to Enterprise",
                integration_capabilities=["Slack", "Jira", "GitHub", "Zeplin", "Principle"],
                learning_curve="Medium - 2-4 weeks for proficiency",
                support_quality="Good - Community and official support",
                last_updated="2025-01-06"
            ),
            
            "github": SoftwareTool(
                name="GitHub",
                category="Development & Version Control",
                description="Code hosting platform with collaboration and project management features",
                benefits=[
                    "Version control and code collaboration",
                    "Issue tracking and project management",
                    "CI/CD pipeline integration",
                    "Code review workflows",
                    "Package registry",
                    "Security scanning and alerts"
                ],
                popularity_score=9.7,
                efficiency_impact="Very High - Essential for development teams",
                team_size_recommendation="1-10000+ developers",
                cost_tier="Freemium to Enterprise",
                integration_capabilities=["Slack", "Jira", "Figma", "VS Code", "Jenkins"],
                learning_curve="Medium - 1-2 weeks for Git basics",
                support_quality="Excellent - Extensive documentation and community",
                last_updated="2025-01-06"
            ),
            
            "jira": SoftwareTool(
                name="Jira",
                category="Project Management & Issue Tracking",
                description="Issue and project tracking tool for software development teams",
                benefits=[
                    "Agile project management",
                    "Customizable workflows",
                    "Advanced reporting and analytics",
                    "Integration with development tools",
                    "Time tracking and estimation",
                    "Automation rules"
                ],
                popularity_score=8.5,
                efficiency_impact="High - Streamlines development processes",
                team_size_recommendation="5-1000+ team members",
                cost_tier="Paid to Enterprise",
                integration_capabilities=["GitHub", "Slack", "Confluence", "Bitbucket", "Jenkins"],
                learning_curve="High - 3-4 weeks for full adoption",
                support_quality="Excellent - Comprehensive enterprise support",
                last_updated="2025-01-06"
            ),
            
            "trello": SoftwareTool(
                name="Trello",
                category="Project Management",
                description="Visual project management tool using boards, lists, and cards",
                benefits=[
                    "Simple, visual project management",
                    "Easy to learn and use",
                    "Powerful automation with Butler",
                    "Team collaboration features",
                    "Mobile apps",
                    "Integration with popular tools"
                ],
                popularity_score=8.0,
                efficiency_impact="Medium - Good for simple project tracking",
                team_size_recommendation="1-100 team members",
                cost_tier="Freemium to Enterprise",
                integration_capabilities=["Slack", "Google Drive", "Dropbox", "Evernote", "Zapier"],
                learning_curve="Low - 1 week for basic usage",
                support_quality="Good - Community and official support",
                last_updated="2025-01-06"
            ),
            
            "asana": SoftwareTool(
                name="Asana",
                category="Project Management",
                description="Work management platform for teams to organize and track work",
                benefits=[
                    "Task and project management",
                    "Timeline and calendar views",
                    "Team collaboration and communication",
                    "Workflow automation",
                    "Reporting and insights",
                    "Portfolio management"
                ],
                popularity_score=8.3,
                efficiency_impact="High - Improves task visibility and accountability",
                team_size_recommendation="2-500+ team members",
                cost_tier="Freemium to Enterprise",
                integration_capabilities=["Slack", "Google Workspace", "Microsoft 365", "Salesforce", "Zapier"],
                learning_curve="Medium - 2-3 weeks for full adoption",
                support_quality="Good - Comprehensive support resources",
                last_updated="2025-01-06"
            ),
            
            "monday": SoftwareTool(
                name="Monday.com",
                category="Project Management & Work OS",
                description="Work operating system for managing projects, processes, and workflows",
                benefits=[
                    "Visual project management",
                    "Customizable workflows",
                    "Automation and integrations",
                    "Time tracking and reporting",
                    "Team collaboration",
                    "Resource management"
                ],
                popularity_score=8.1,
                efficiency_impact="High - Centralizes work management",
                team_size_recommendation="2-500+ team members",
                cost_tier="Paid to Enterprise",
                integration_capabilities=["Slack", "Google Workspace", "Microsoft 365", "Salesforce", "Zapier"],
                learning_curve="Medium - 2-3 weeks for proficiency",
                support_quality="Good - Dedicated customer success",
                last_updated="2025-01-06"
            ),
            
            "zoom": SoftwareTool(
                name="Zoom",
                category="Video Conferencing",
                description="Video conferencing and communication platform",
                benefits=[
                    "High-quality video and audio",
                    "Screen sharing and collaboration",
                    "Recording and transcription",
                    "Webinar capabilities",
                    "Breakout rooms",
                    "Integration with calendar systems"
                ],
                popularity_score=9.3,
                efficiency_impact="Very High - Enables remote collaboration",
                team_size_recommendation="2-10000+ participants",
                cost_tier="Freemium to Enterprise",
                integration_capabilities=["Google Calendar", "Outlook", "Slack", "Salesforce", "HubSpot"],
                learning_curve="Low - Immediate usability",
                support_quality="Excellent - 24/7 support",
                last_updated="2025-01-06"
            )
        }
        
        return tools
    
    def _get_categories(self) -> List[str]:
        """Get list of software categories."""
        return [
            "Project Management",
            "Communication",
            "Design & Prototyping",
            "Development & Version Control",
            "Productivity & Documentation",
            "Video Conferencing",
            "Marketing & Sales",
            "Analytics & Reporting",
            "Security & Compliance",
            "Cloud & Infrastructure"
        ]
    
    def get_tool_by_name(self, name: str) -> Optional[SoftwareTool]:
        """Get a software tool by name (case-insensitive)."""
        name_lower = name.lower().strip()
        for tool_name, tool in self.tools.items():
            if tool_name.lower() == name_lower or tool.name.lower() == name_lower:
                return tool
        return None
    
    def search_tools(self, query: str) -> List[SoftwareTool]:
        """Search for tools by name, category, or description."""
        query_lower = query.lower()
        results = []
        
        for tool in self.tools.values():
            if (query_lower in tool.name.lower() or 
                query_lower in tool.category.lower() or 
                query_lower in tool.description.lower() or
                any(query_lower in benefit.lower() for benefit in tool.benefits)):
                results.append(tool)
        
        # Sort by popularity score
        results.sort(key=lambda x: x.popularity_score, reverse=True)
        return results

class DocumentScanner:
    """Scans documents to identify software mentions and analyze content."""
    
    def __init__(self, software_db: SoftwareDatabase):
        self.software_db = software_db
        self.supported_extensions = {'.txt', '.md', '.py', '.js', '.html', '.css', '.json', '.yaml', '.yml', '.csv'}
    
    def scan_document(self, file_path: str) -> DocumentAnalysis:
        """Scan a single document for software mentions."""
        try:
            file_path = Path(file_path)
            
            if not file_path.exists():
                raise FileNotFoundError(f"File not found: {file_path}")
            
            if file_path.suffix.lower() not in self.supported_extensions:
                logger.warning(f"Unsupported file type: {file_path.suffix}")
                return self._create_empty_analysis(file_path)
            
            # Read file content
            content = self._read_file_content(file_path)
            if not content:
                return self._create_empty_analysis(file_path)
            
            # Calculate file hash
            file_hash = hashlib.md5(content.encode()).hexdigest()
            
            # Find software mentions
            software_mentions = self._find_software_mentions(content)
            
            # Calculate confidence score
            confidence_score = self._calculate_confidence_score(software_mentions, content)
            
            # Generate recommendations
            recommendations = self._generate_recommendations(software_mentions)
            
            return DocumentAnalysis(
                file_path=str(file_path),
                file_hash=file_hash,
                software_mentions=software_mentions,
                analysis_timestamp=datetime.now().isoformat(),
                confidence_score=confidence_score,
                recommendations=recommendations
            )
            
        except Exception as e:
            logger.error(f"Error scanning document {file_path}: {str(e)}")
            return self._create_empty_analysis(file_path)
    
    def _read_file_content(self, file_path: Path) -> str:
        """Read file content with proper encoding handling."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return f.read()
        except UnicodeDecodeError:
            try:
                with open(file_path, 'r', encoding='latin-1') as f:
                    return f.read()
            except Exception:
                logger.error(f"Could not read file: {file_path}")
                return ""
        except Exception as e:
            logger.error(f"Error reading file {file_path}: {str(e)}")
            return ""
    
    def _find_software_mentions(self, content: str) -> List[Dict[str, Any]]:
        """Find software tool mentions in content."""
        mentions = []
        content_lower = content.lower()
        
        for tool_name, tool in self.software_db.tools.items():
            # Check for exact name matches
            if tool.name.lower() in content_lower:
                mentions.append({
                    'tool_name': tool.name,
                    'tool_category': tool.category,
                    'mention_type': 'exact_match',
                    'context': self._extract_context(content, tool.name),
                    'confidence': 0.9
                })
            
            # Check for partial matches
            elif tool_name.lower() in content_lower:
                mentions.append({
                    'tool_name': tool.name,
                    'tool_category': tool.category,
                    'mention_type': 'partial_match',
                    'context': self._extract_context(content, tool_name),
                    'confidence': 0.7
                })
        
        # Remove duplicates and sort by confidence
        unique_mentions = []
        seen_tools = set()
        for mention in mentions:
            if mention['tool_name'] not in seen_tools:
                unique_mentions.append(mention)
                seen_tools.add(mention['tool_name'])
        
        return sorted(unique_mentions, key=lambda x: x['confidence'], reverse=True)
    
    def _extract_context(self, content: str, tool_name: str, context_length: int = 100) -> str:
        """Extract context around a tool mention."""
        content_lower = content.lower()
        tool_lower = tool_name.lower()
        
        index = content_lower.find(tool_lower)
        if index == -1:
            return ""
        
        start = max(0, index - context_length // 2)
        end = min(len(content), index + len(tool_name) + context_length // 2)
        
        return content[start:end].strip()
    
    def _calculate_confidence_score(self, mentions: List[Dict], content: str) -> float:
        """Calculate confidence score for the analysis."""
        if not mentions:
            return 0.0
        
        # Base score from mentions
        base_score = sum(mention['confidence'] for mention in mentions) / len(mentions)
        
        # Boost score if content seems to be about software/tools
        content_lower = content.lower()
        software_keywords = ['software', 'tool', 'platform', 'application', 'system', 'integration', 'workflow']
        keyword_boost = sum(1 for keyword in software_keywords if keyword in content_lower) * 0.05
        
        return min(1.0, base_score + keyword_boost)
    
    def _generate_recommendations(self, mentions: List[Dict]) -> List[str]:
        """Generate recommendations based on software mentions."""
        recommendations = []
        
        if not mentions:
            recommendations.append("Consider documenting your current software stack for better team visibility.")
            return recommendations
        
        # Group by category
        categories = {}
        for mention in mentions:
            category = mention['tool_category']
            if category not in categories:
                categories[category] = []
            categories[category].append(mention['tool_name'])
        
        # Generate category-specific recommendations
        for category, tools in categories.items():
            if category == "Project Management":
                recommendations.append(f"Your team uses {', '.join(tools)} for project management. Consider consolidating to reduce tool sprawl.")
            elif category == "Communication":
                recommendations.append(f"Communication tools: {', '.join(tools)}. Ensure proper integration between these tools.")
            elif category == "Development & Version Control":
                recommendations.append(f"Development workflow includes {', '.join(tools)}. Review CI/CD integration opportunities.")
        
        # General recommendations
        if len(mentions) > 5:
            recommendations.append("Your team uses many different tools. Consider a tool audit to identify redundancies.")
        
        return recommendations
    
    def _create_empty_analysis(self, file_path: Path) -> DocumentAnalysis:
        """Create an empty analysis for failed scans."""
        return DocumentAnalysis(
            file_path=str(file_path),
            file_hash="",
            software_mentions=[],
            analysis_timestamp=datetime.now().isoformat(),
            confidence_score=0.0,
            recommendations=["Unable to analyze this document. Check file format and permissions."]
        )

class TeamEfficiencyAnalyzer:
    """Analyzes team efficiency based on software tool usage."""
    
    def __init__(self, software_db: SoftwareDatabase):
        self.software_db = software_db
    
    def analyze_team_efficiency(self, document_analyses: List[DocumentAnalysis]) -> Dict[str, Any]:
        """Analyze team efficiency based on multiple document analyses."""
        # Aggregate software mentions
        all_mentions = []
        for analysis in document_analyses:
            all_mentions.extend(analysis.software_mentions)
        
        # Count tool usage
        tool_usage = {}
        for mention in all_mentions:
            tool_name = mention['tool_name']
            if tool_name not in tool_usage:
                tool_usage[tool_name] = 0
            tool_usage[tool_name] += 1
        
        # Analyze by category
        category_analysis = self._analyze_by_category(all_mentions)
        
        # Generate efficiency insights
        insights = self._generate_efficiency_insights(tool_usage, category_analysis)
        
        # Calculate efficiency score
        efficiency_score = self._calculate_efficiency_score(tool_usage, category_analysis)
        
        return {
            'efficiency_score': efficiency_score,
            'tool_usage': tool_usage,
            'category_analysis': category_analysis,
            'insights': insights,
            'recommendations': self._generate_efficiency_recommendations(tool_usage, category_analysis),
            'analysis_timestamp': datetime.now().isoformat()
        }
    
    def _analyze_by_category(self, mentions: List[Dict]) -> Dict[str, Any]:
        """Analyze software usage by category."""
        categories = {}
        
        for mention in mentions:
            category = mention['tool_category']
            if category not in categories:
                categories[category] = {
                    'tools': [],
                    'total_mentions': 0,
                    'avg_confidence': 0.0
                }
            
            categories[category]['tools'].append(mention['tool_name'])
            categories[category]['total_mentions'] += 1
        
        # Calculate average confidence for each category
        for category, data in categories.items():
            category_mentions = [m for m in mentions if m['tool_category'] == category]
            if category_mentions:
                data['avg_confidence'] = sum(m['confidence'] for m in category_mentions) / len(category_mentions)
        
        return categories
    
    def _generate_efficiency_insights(self, tool_usage: Dict[str, int], category_analysis: Dict[str, Any]) -> List[str]:
        """Generate efficiency insights based on tool usage."""
        insights = []
        
        # Tool diversity analysis
        total_tools = len(tool_usage)
        if total_tools > 10:
            insights.append(f"High tool diversity ({total_tools} tools) - consider consolidation to reduce complexity")
        elif total_tools < 3:
            insights.append(f"Low tool diversity ({total_tools} tools) - consider expanding your toolkit")
        else:
            insights.append(f"Moderate tool diversity ({total_tools} tools) - good balance of functionality")
        
        # Category coverage analysis
        essential_categories = ["Project Management", "Communication", "Development & Version Control"]
        covered_categories = [cat for cat in essential_categories if cat in category_analysis]
        
        if len(covered_categories) == len(essential_categories):
            insights.append("Good coverage of essential tool categories")
        else:
            missing = [cat for cat in essential_categories if cat not in category_analysis]
            insights.append(f"Missing essential tool categories: {', '.join(missing)}")
        
        # Popular tool analysis
        if tool_usage:
            most_used = max(tool_usage.items(), key=lambda x: x[1])
            insights.append(f"Most mentioned tool: {most_used[0]} ({most_used[1]} mentions)")
        
        return insights
    
    def _calculate_efficiency_score(self, tool_usage: Dict[str, int], category_analysis: Dict[str, Any]) -> float:
        """Calculate overall efficiency score (0-100)."""
        score = 0.0
        
        # Tool diversity score (30 points)
        total_tools = len(tool_usage)
        if 3 <= total_tools <= 8:
            score += 30
        elif total_tools < 3:
            score += 15
        else:
            score += max(0, 30 - (total_tools - 8) * 2)
        
        # Category coverage score (40 points)
        essential_categories = ["Project Management", "Communication", "Development & Version Control"]
        covered_categories = len([cat for cat in essential_categories if cat in category_analysis])
        score += (covered_categories / len(essential_categories)) * 40
        
        # Tool quality score (30 points)
        if tool_usage:
            quality_tools = ["ClickUp", "Slack", "GitHub", "Figma", "Notion"]
            quality_count = sum(1 for tool in tool_usage.keys() if tool in quality_tools)
            score += min(30, (quality_count / len(tool_usage)) * 30)
        
        return min(100.0, score)
    
    def _generate_efficiency_recommendations(self, tool_usage: Dict[str, int], category_analysis: Dict[str, Any]) -> List[str]:
        """Generate efficiency recommendations."""
        recommendations = []
        
        # Tool consolidation recommendations
        if len(tool_usage) > 8:
            recommendations.append("Consider consolidating similar tools to reduce complexity and training overhead")
        
        # Missing category recommendations
        essential_categories = ["Project Management", "Communication", "Development & Version Control"]
        missing_categories = [cat for cat in essential_categories if cat not in category_analysis]
        
        for category in missing_categories:
            if category == "Project Management":
                recommendations.append("Consider implementing a project management tool like ClickUp or Asana")
            elif category == "Communication":
                recommendations.append("Consider implementing a team communication tool like Slack or Microsoft Teams")
            elif category == "Development & Version Control":
                recommendations.append("Consider implementing version control with GitHub or GitLab")
        
        # Integration recommendations
        if len(tool_usage) > 3:
            recommendations.append("Ensure proper integration between your tools to avoid data silos")
        
        return recommendations

class ClickUpBrainIntegration:
    """Integration with ClickUp Brain for enhanced functionality."""
    
    def __init__(self, software_db: SoftwareDatabase):
        self.software_db = software_db
    
    def generate_clickup_insights(self, document_analyses: List[DocumentAnalysis]) -> Dict[str, Any]:
        """Generate ClickUp Brain specific insights."""
        insights = {
            'clickup_mentions': 0,
            'integration_opportunities': [],
            'workflow_optimizations': [],
            'team_efficiency_boost': 0.0,
            'recommended_clickup_features': []
        }
        
        # Count ClickUp mentions
        for analysis in document_analyses:
            for mention in analysis.software_mentions:
                if mention['tool_name'].lower() == 'clickup':
                    insights['clickup_mentions'] += 1
        
        # Generate integration opportunities
        insights['integration_opportunities'] = self._identify_integration_opportunities(document_analyses)
        
        # Generate workflow optimizations
        insights['workflow_optimizations'] = self._suggest_workflow_optimizations(document_analyses)
        
        # Calculate efficiency boost
        insights['team_efficiency_boost'] = self._calculate_efficiency_boost(document_analyses)
        
        # Recommend ClickUp features
        insights['recommended_clickup_features'] = self._recommend_clickup_features(document_analyses)
        
        return insights
    
    def _identify_integration_opportunities(self, document_analyses: List[DocumentAnalysis]) -> List[str]:
        """Identify opportunities for ClickUp integrations."""
        opportunities = []
        
        # Collect all mentioned tools
        mentioned_tools = set()
        for analysis in document_analyses:
            for mention in analysis.software_mentions:
                mentioned_tools.add(mention['tool_name'])
        
        # Check for integration opportunities
        clickup_tool = self.software_db.get_tool_by_name("ClickUp")
        if clickup_tool:
            for tool_name in mentioned_tools:
                if tool_name != "ClickUp" and tool_name in clickup_tool.integration_capabilities:
                    opportunities.append(f"Integrate {tool_name} with ClickUp for seamless workflow")
        
        return opportunities
    
    def _suggest_workflow_optimizations(self, document_analyses: List[DocumentAnalysis]) -> List[str]:
        """Suggest workflow optimizations using ClickUp."""
        optimizations = []
        
        # Analyze project management needs
        pm_tools = []
        for analysis in document_analyses:
            for mention in analysis.software_mentions:
                if mention['tool_category'] == "Project Management":
                    pm_tools.append(mention['tool_name'])
        
        if len(pm_tools) > 1:
            optimizations.append("Consolidate project management tools into ClickUp for unified project tracking")
        
        # Analyze communication needs
        comm_tools = []
        for analysis in document_analyses:
            for mention in analysis.software_mentions:
                if mention['tool_category'] == "Communication":
                    comm_tools.append(mention['tool_name'])
        
        if comm_tools:
            optimizations.append("Use ClickUp's built-in communication features to reduce context switching")
        
        return optimizations
    
    def _calculate_efficiency_boost(self, document_analyses: List[DocumentAnalysis]) -> float:
        """Calculate potential efficiency boost from ClickUp adoption."""
        # Simple calculation based on tool diversity and current ClickUp usage
        total_tools = 0
        clickup_usage = 0
        
        for analysis in document_analyses:
            for mention in analysis.software_mentions:
                total_tools += 1
                if mention['tool_name'].lower() == 'clickup':
                    clickup_usage += 1
        
        if total_tools == 0:
            return 0.0
        
        # Efficiency boost calculation
        if clickup_usage == 0:
            # No ClickUp usage - potential for high efficiency gain
            return min(60.0, total_tools * 5.0)
        else:
            # Some ClickUp usage - moderate efficiency gain
            return min(30.0, (total_tools - clickup_usage) * 3.0)
    
    def _recommend_clickup_features(self, document_analyses: List[DocumentAnalysis]) -> List[str]:
        """Recommend specific ClickUp features based on analysis."""
        features = []
        
        # Analyze team size and complexity
        total_mentions = sum(len(analysis.software_mentions) for analysis in document_analyses)
        
        if total_mentions > 20:
            features.append("ClickUp Enterprise features for large team management")
            features.append("Advanced automation and custom fields")
        
        # Analyze project management needs
        pm_categories = ["Project Management", "Development & Version Control"]
        has_pm_tools = any(
            any(mention['tool_category'] in pm_categories for mention in analysis.software_mentions)
            for analysis in document_analyses
        )
        
        if has_pm_tools:
            features.append("ClickUp's Gantt charts and timeline views")
            features.append("Custom workflows and automation")
        
        # Analyze collaboration needs
        has_comm_tools = any(
            any(mention['tool_category'] == "Communication" for mention in analysis.software_mentions)
            for analysis in document_analyses
        )
        
        if has_comm_tools:
            features.append("ClickUp's built-in chat and comments")
            features.append("Real-time collaboration features")
        
        return features

class ToolSelectionSystem:
    """Main system class that orchestrates all components."""
    
    def __init__(self):
        self.software_db = SoftwareDatabase()
        self.document_scanner = DocumentScanner(self.software_db)
        self.efficiency_analyzer = TeamEfficiencyAnalyzer(self.software_db)
        self.clickup_integration = ClickUpBrainIntegration(self.software_db)
    
    def scan_directory(self, directory_path: str) -> Dict[str, Any]:
        """Scan a directory for documents and analyze software usage."""
        directory = Path(directory_path)
        
        if not directory.exists():
            raise FileNotFoundError(f"Directory not found: {directory_path}")
        
        # Find all supported files
        supported_files = []
        for ext in self.document_scanner.supported_extensions:
            supported_files.extend(directory.rglob(f"*{ext}"))
        
        logger.info(f"Found {len(supported_files)} supported files to analyze")
        
        # Scan each file
        document_analyses = []
        for file_path in supported_files:
            logger.info(f"Scanning: {file_path}")
            analysis = self.document_scanner.scan_document(str(file_path))
            document_analyses.append(analysis)
        
        # Analyze team efficiency
        efficiency_analysis = self.efficiency_analyzer.analyze_team_efficiency(document_analyses)
        
        # Generate ClickUp Brain insights
        clickup_insights = self.clickup_integration.generate_clickup_insights(document_analyses)
        
        return {
            'directory_path': str(directory),
            'total_files_scanned': len(supported_files),
            'document_analyses': [asdict(analysis) for analysis in document_analyses],
            'efficiency_analysis': efficiency_analysis,
            'clickup_insights': clickup_insights,
            'scan_timestamp': datetime.now().isoformat()
        }
    
    def generate_report(self, analysis_results: Dict[str, Any]) -> str:
        """Generate a comprehensive report from analysis results."""
        report = []
        report.append("# ClickUp Brain Tool Selection Analysis Report")
        report.append(f"Generated on: {analysis_results['scan_timestamp']}")
        report.append(f"Directory: {analysis_results['directory_path']}")
        report.append(f"Files scanned: {analysis_results['total_files_scanned']}")
        report.append("")
        
        # Efficiency Analysis
        efficiency = analysis_results['efficiency_analysis']
        report.append("## Team Efficiency Analysis")
        report.append(f"**Overall Efficiency Score: {efficiency['efficiency_score']:.1f}/100**")
        report.append("")
        
        # Tool Usage
        if efficiency['tool_usage']:
            report.append("### Software Tools Identified")
            for tool, count in sorted(efficiency['tool_usage'].items(), key=lambda x: x[1], reverse=True):
                report.append(f"- **{tool}**: {count} mentions")
            report.append("")
        
        # Insights
        if efficiency['insights']:
            report.append("### Key Insights")
            for insight in efficiency['insights']:
                report.append(f"- {insight}")
            report.append("")
        
        # Recommendations
        if efficiency['recommendations']:
            report.append("### Efficiency Recommendations")
            for rec in efficiency['recommendations']:
                report.append(f"- {rec}")
            report.append("")
        
        # ClickUp Brain Insights
        clickup = analysis_results['clickup_insights']
        report.append("## ClickUp Brain Insights")
        report.append(f"**ClickUp Mentions**: {clickup['clickup_mentions']}")
        report.append(f"**Potential Efficiency Boost**: {clickup['team_efficiency_boost']:.1f}%")
        report.append("")
        
        if clickup['integration_opportunities']:
            report.append("### Integration Opportunities")
            for opp in clickup['integration_opportunities']:
                report.append(f"- {opp}")
            report.append("")
        
        if clickup['workflow_optimizations']:
            report.append("### Workflow Optimizations")
            for opt in clickup['workflow_optimizations']:
                report.append(f"- {opt}")
            report.append("")
        
        if clickup['recommended_clickup_features']:
            report.append("### Recommended ClickUp Features")
            for feature in clickup['recommended_clickup_features']:
                report.append(f"- {feature}")
            report.append("")
        
        return "\n".join(report)
    
    def save_analysis(self, analysis_results: Dict[str, Any], output_path: str):
        """Save analysis results to a JSON file."""
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(analysis_results, f, indent=2, ensure_ascii=False)
        logger.info(f"Analysis saved to: {output_path}")

def main():
    """Main function to demonstrate the system."""
    # Initialize the system
    system = ToolSelectionSystem()
    
    # Example usage
    try:
        # Scan the current directory
        current_dir = "."
        logger.info(f"Scanning directory: {current_dir}")
        
        # Perform analysis
        results = system.scan_directory(current_dir)
        
        # Generate and display report
        report = system.generate_report(results)
        print(report)
        
        # Save results
        output_file = "clickup_brain_analysis_results.json"
        system.save_analysis(results, output_file)
        
        # Save report
        report_file = "clickup_brain_analysis_report.md"
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write(report)
        logger.info(f"Report saved to: {report_file}")
        
    except Exception as e:
        logger.error(f"Error in main execution: {str(e)}")
        raise

if __name__ == "__main__":
    main()










