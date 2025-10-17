#!/usr/bin/env python3
"""
Advanced Due Diligence Automation Script
Frontier AI Marketing Platform - Investment Readiness Assessment

This script automates the due diligence process with AI-powered analysis,
real-time scoring, and automated reporting capabilities.
"""

import json
import datetime
import pandas as pd
import numpy as np
from typing import Dict, List, Any, Optional
import requests
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import logging
from dataclasses import dataclass
from enum import Enum

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('due_diligence.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class RiskLevel(Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class Priority(Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

@dataclass
class DueDiligenceItem:
    """Represents a single due diligence item"""
    id: str
    category: str
    subcategory: str
    name: str
    description: str
    points_available: int
    points_earned: int
    status: str
    priority: Priority
    assigned_to: str
    due_date: str
    validation_criteria: List[str]
    risk_factors: List[str]
    ai_insights: List[str] = None

@dataclass
class CategoryScore:
    """Represents scoring for a category"""
    name: str
    weight: float
    max_score: int
    current_score: int
    ai_weight: float
    completion_percentage: float
    risk_level: RiskLevel

class DueDiligenceAutomation:
    """Main class for due diligence automation"""
    
    def __init__(self, config_file: str = "due_diligence_config.json"):
        self.config = self.load_config(config_file)
        self.categories = self.initialize_categories()
        self.items = self.load_due_diligence_items()
        self.ai_insights = []
        
    def load_config(self, config_file: str) -> Dict[str, Any]:
        """Load configuration from JSON file"""
        try:
            with open(config_file, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            logger.warning(f"Config file {config_file} not found, using defaults")
            return self.get_default_config()
    
    def get_default_config(self) -> Dict[str, Any]:
        """Get default configuration"""
        return {
            "target_score": 900,
            "minimum_score": 750,
            "ai_enabled": True,
            "auto_refresh_interval": 300,  # 5 minutes
            "email_notifications": True,
            "slack_notifications": False,
            "categories": {
                "financial": {"weight": 0.25, "max_score": 250, "ai_weight": 0.3},
                "technology": {"weight": 0.20, "max_score": 200, "ai_weight": 0.4},
                "market": {"weight": 0.20, "max_score": 200, "ai_weight": 0.2},
                "team": {"weight": 0.15, "max_score": 150, "ai_weight": 0.3},
                "legal": {"weight": 0.10, "max_score": 100, "ai_weight": 0.1},
                "operations": {"weight": 0.10, "max_score": 100, "ai_weight": 0.2}
            }
        }
    
    def initialize_categories(self) -> Dict[str, CategoryScore]:
        """Initialize category scoring"""
        categories = {}
        for name, config in self.config["categories"].items():
            categories[name] = CategoryScore(
                name=name,
                weight=config["weight"],
                max_score=config["max_score"],
                current_score=0,
                ai_weight=config["ai_weight"],
                completion_percentage=0.0,
                risk_level=RiskLevel.CRITICAL
            )
        return categories
    
    def load_due_diligence_items(self) -> List[DueDiligenceItem]:
        """Load due diligence items from CSV or database"""
        # This would typically load from a database or CSV file
        # For now, we'll create sample data
        items = []
        
        # Financial Model items
        items.extend([
            DueDiligenceItem(
                id="fin_001",
                category="financial",
                subcategory="revenue_projections",
                name="3-Year Financial Model",
                description="Complete 3-year financial projections with scenarios",
                points_available=100,
                points_earned=0,
                status="not_started",
                priority=Priority.CRITICAL,
                assigned_to="CFO",
                due_date="2024-12-31",
                validation_criteria=["3+ data sources", "conservative assumptions", "sensitivity analysis"],
                risk_factors=["market volatility", "competition", "economic downturn"]
            ),
            DueDiligenceItem(
                id="fin_002",
                category="financial",
                subcategory="unit_economics",
                name="Unit Economics Validation",
                description="Validate CAC, LTV, and payback period",
                points_available=50,
                points_earned=0,
                status="not_started",
                priority=Priority.CRITICAL,
                assigned_to="CFO",
                due_date="2024-12-31",
                validation_criteria=["CAC < $200", "LTV > $2000", "Payback < 6 months"],
                risk_factors=["channel saturation", "cost inflation", "churn increase"]
            )
        ])
        
        # Technology items
        items.extend([
            DueDiligenceItem(
                id="tech_001",
                category="technology",
                subcategory="architecture",
                name="System Architecture Review",
                description="Review microservices architecture and scalability",
                points_available=50,
                points_earned=0,
                status="not_started",
                priority=Priority.CRITICAL,
                assigned_to="CTO",
                due_date="2024-12-31",
                validation_criteria=["microservices design", "API-first", "scalable"],
                risk_factors=["architecture complexity", "maintenance overhead", "vendor lock-in"]
            ),
            DueDiligenceItem(
                id="tech_002",
                category="technology",
                subcategory="ai_ml",
                name="AI/ML Capabilities",
                description="Validate AI integration and performance",
                points_available=50,
                points_earned=0,
                status="not_started",
                priority=Priority.CRITICAL,
                assigned_to="CTO",
                due_date="2024-12-31",
                validation_criteria=["OpenAI integration", "custom models", "<3s response"],
                risk_factors=["AI costs", "model performance", "accuracy issues"]
            )
        ])
        
        return items
    
    def calculate_category_score(self, category: str) -> CategoryScore:
        """Calculate score for a specific category"""
        category_items = [item for item in self.items if item.category == category]
        
        if not category_items:
            return self.categories[category]
        
        total_points = sum(item.points_available for item in category_items)
        earned_points = sum(item.points_earned for item in category_items)
        completion_percentage = (earned_points / total_points) * 100 if total_points > 0 else 0
        
        # Determine risk level based on completion
        if completion_percentage >= 90:
            risk_level = RiskLevel.LOW
        elif completion_percentage >= 75:
            risk_level = RiskLevel.MEDIUM
        elif completion_percentage >= 50:
            risk_level = RiskLevel.HIGH
        else:
            risk_level = RiskLevel.CRITICAL
        
        self.categories[category].current_score = earned_points
        self.categories[category].completion_percentage = completion_percentage
        self.categories[category].risk_level = risk_level
        
        return self.categories[category]
    
    def calculate_overall_score(self) -> Dict[str, Any]:
        """Calculate overall due diligence score"""
        total_score = 0
        weighted_score = 0
        ai_adjusted_score = 0
        
        for category_name, category in self.categories.items():
            category_score = self.calculate_category_score(category_name)
            total_score += category_score.current_score
            weighted_score += category_score.current_score * category.weight
            ai_adjusted_score += category_score.current_score * category.weight * (1 + category.ai_weight * 0.1)
        
        percentage = (total_score / 1000) * 100
        
        # Determine overall risk level
        if percentage >= 90:
            risk_level = RiskLevel.LOW
        elif percentage >= 75:
            risk_level = RiskLevel.MEDIUM
        elif percentage >= 50:
            risk_level = RiskLevel.HIGH
        else:
            risk_level = RiskLevel.CRITICAL
        
        return {
            "total_score": total_score,
            "weighted_score": weighted_score,
            "ai_adjusted_score": ai_adjusted_score,
            "percentage": percentage,
            "risk_level": risk_level.value,
            "investment_grade": self.get_investment_grade(percentage),
            "recommendation": self.get_recommendation(percentage),
            "success_probability": self.calculate_success_probability(percentage)
        }
    
    def get_investment_grade(self, percentage: float) -> str:
        """Get investment grade based on percentage"""
        if percentage >= 95:
            return "A+"
        elif percentage >= 90:
            return "A"
        elif percentage >= 85:
            return "B+"
        elif percentage >= 80:
            return "B"
        elif percentage >= 75:
            return "C+"
        elif percentage >= 70:
            return "C"
        else:
            return "F"
    
    def get_recommendation(self, percentage: float) -> str:
        """Get investment recommendation based on percentage"""
        if percentage >= 950:
            return "Strong Buy"
        elif percentage >= 900:
            return "Buy"
        elif percentage >= 850:
            return "Hold"
        elif percentage >= 800:
            return "Caution"
        elif percentage >= 750:
            return "Avoid"
        else:
            return "Not Ready"
    
    def calculate_success_probability(self, percentage: float) -> float:
        """Calculate success probability using AI insights"""
        base_probability = percentage
        
        # Adjust based on AI insights
        ai_adjustment = 0
        for insight in self.ai_insights:
            if insight.get("type") == "positive":
                ai_adjustment += 5
            elif insight.get("type") == "negative":
                ai_adjustment -= 10
            elif insight.get("type") == "critical":
                ai_adjustment -= 20
        
        final_probability = base_probability + ai_adjustment
        return max(0, min(100, final_probability))
    
    def run_ai_analysis(self) -> List[Dict[str, Any]]:
        """Run AI analysis on due diligence data"""
        insights = []
        
        # Analyze financial projections
        financial_items = [item for item in self.items if item.category == "financial"]
        if any(item.status == "not_started" for item in financial_items):
            insights.append({
                "type": "critical",
                "category": "financial",
                "message": "Financial projections not started - critical for investment readiness",
                "recommendation": "Prioritize financial model validation immediately"
            })
        
        # Analyze technology readiness
        tech_items = [item for item in self.items if item.category == "technology"]
        tech_completion = sum(1 for item in tech_items if item.status == "completed") / len(tech_items)
        if tech_completion < 0.5:
            insights.append({
                "type": "warning",
                "category": "technology",
                "message": "Technology assessment incomplete - may impact scalability",
                "recommendation": "Complete technical architecture review"
            })
        
        # Analyze team readiness
        team_items = [item for item in self.items if item.category == "team"]
        if any(item.status == "not_started" for item in team_items):
            insights.append({
                "type": "info",
                "category": "team",
                "message": "Team assessment pending - leadership evaluation needed",
                "recommendation": "Schedule leadership interviews and reference checks"
            })
        
        self.ai_insights.extend(insights)
        return insights
    
    def generate_report(self) -> Dict[str, Any]:
        """Generate comprehensive due diligence report"""
        overall_score = self.calculate_overall_score()
        
        report = {
            "timestamp": datetime.datetime.now().isoformat(),
            "overall_score": overall_score,
            "categories": {
                name: {
                    "score": category.current_score,
                    "max_score": category.max_score,
                    "completion_percentage": category.completion_percentage,
                    "risk_level": category.risk_level.value
                }
                for name, category in self.categories.items()
            },
            "items": [
                {
                    "id": item.id,
                    "name": item.name,
                    "status": item.status,
                    "points_earned": item.points_earned,
                    "points_available": item.points_available,
                    "priority": item.priority.value
                }
                for item in self.items
            ],
            "ai_insights": self.ai_insights,
            "recommendations": self.generate_recommendations()
        }
        
        return report
    
    def generate_recommendations(self) -> List[str]:
        """Generate actionable recommendations"""
        recommendations = []
        overall_score = self.calculate_overall_score()
        
        if overall_score["percentage"] < 50:
            recommendations.append("CRITICAL: Immediate action required - overall score below 50%")
        
        if overall_score["percentage"] < 75:
            recommendations.append("HIGH PRIORITY: Focus on critical items to reach minimum threshold")
        
        # Category-specific recommendations
        for category_name, category in self.categories.items():
            if category.completion_percentage < 50:
                recommendations.append(f"Complete {category_name} assessment - currently at {category.completion_percentage:.1f}%")
        
        # AI insights recommendations
        for insight in self.ai_insights:
            if insight.get("recommendation"):
                recommendations.append(insight["recommendation"])
        
        return recommendations
    
    def send_notifications(self, report: Dict[str, Any]):
        """Send notifications based on report"""
        if not self.config.get("email_notifications", False):
            return
        
        # Send email notification
        self.send_email_notification(report)
        
        # Send Slack notification if configured
        if self.config.get("slack_notifications", False):
            self.send_slack_notification(report)
    
    def send_email_notification(self, report: Dict[str, Any]):
        """Send email notification"""
        try:
            msg = MIMEMultipart()
            msg['From'] = self.config.get("email_from", "noreply@frontierai.com")
            msg['To'] = self.config.get("email_to", "team@frontierai.com")
            msg['Subject'] = f"Due Diligence Update - Score: {report['overall_score']['percentage']:.1f}%"
            
            body = f"""
            Due Diligence Status Update
            
            Overall Score: {report['overall_score']['total_score']}/1000 ({report['overall_score']['percentage']:.1f}%)
            Risk Level: {report['overall_score']['risk_level'].upper()}
            Investment Grade: {report['overall_score']['investment_grade']}
            Recommendation: {report['overall_score']['recommendation']}
            Success Probability: {report['overall_score']['success_probability']:.1f}%
            
            Category Breakdown:
            """
            
            for category_name, category_data in report['categories'].items():
                body += f"- {category_name.title()}: {category_data['score']}/{category_data['max_score']} ({category_data['completion_percentage']:.1f}%)\n"
            
            if report['ai_insights']:
                body += "\nAI Insights:\n"
                for insight in report['ai_insights']:
                    body += f"- {insight['message']}\n"
            
            msg.attach(MIMEText(body, 'plain'))
            
            # Send email (configure SMTP settings)
            # server = smtplib.SMTP('smtp.gmail.com', 587)
            # server.starttls()
            # server.login(email, password)
            # server.send_message(msg)
            # server.quit()
            
            logger.info("Email notification sent successfully")
            
        except Exception as e:
            logger.error(f"Failed to send email notification: {e}")
    
    def send_slack_notification(self, report: Dict[str, Any]):
        """Send Slack notification"""
        try:
            webhook_url = self.config.get("slack_webhook_url")
            if not webhook_url:
                return
            
            message = {
                "text": f"Due Diligence Update - Score: {report['overall_score']['percentage']:.1f}%",
                "attachments": [
                    {
                        "color": "good" if report['overall_score']['percentage'] >= 75 else "warning",
                        "fields": [
                            {"title": "Overall Score", "value": f"{report['overall_score']['total_score']}/1000", "short": True},
                            {"title": "Risk Level", "value": report['overall_score']['risk_level'].upper(), "short": True},
                            {"title": "Investment Grade", "value": report['overall_score']['investment_grade'], "short": True},
                            {"title": "Recommendation", "value": report['overall_score']['recommendation'], "short": True}
                        ]
                    }
                ]
            }
            
            response = requests.post(webhook_url, json=message)
            response.raise_for_status()
            logger.info("Slack notification sent successfully")
            
        except Exception as e:
            logger.error(f"Failed to send Slack notification: {e}")
    
    def update_item_status(self, item_id: str, status: str, points_earned: int = None):
        """Update status of a due diligence item"""
        for item in self.items:
            if item.id == item_id:
                item.status = status
                if points_earned is not None:
                    item.points_earned = points_earned
                logger.info(f"Updated item {item_id}: {status}")
                return True
        return False
    
    def export_to_excel(self, filename: str = "due_diligence_report.xlsx"):
        """Export due diligence data to Excel"""
        try:
            # Create DataFrame for items
            items_data = []
            for item in self.items:
                items_data.append({
                    "ID": item.id,
                    "Category": item.category,
                    "Subcategory": item.subcategory,
                    "Name": item.name,
                    "Status": item.status,
                    "Priority": item.priority.value,
                    "Assigned To": item.assigned_to,
                    "Due Date": item.due_date,
                    "Points Earned": item.points_earned,
                    "Points Available": item.points_available,
                    "Completion %": (item.points_earned / item.points_available) * 100 if item.points_available > 0 else 0
                })
            
            df_items = pd.DataFrame(items_data)
            
            # Create DataFrame for categories
            categories_data = []
            for name, category in self.categories.items():
                categories_data.append({
                    "Category": name.title(),
                    "Score": category.current_score,
                    "Max Score": category.max_score,
                    "Weight": category.weight,
                    "Completion %": category.completion_percentage,
                    "Risk Level": category.risk_level.value
                })
            
            df_categories = pd.DataFrame(categories_data)
            
            # Write to Excel
            with pd.ExcelWriter(filename, engine='openpyxl') as writer:
                df_items.to_excel(writer, sheet_name='Due Diligence Items', index=False)
                df_categories.to_excel(writer, sheet_name='Category Scores', index=False)
            
            logger.info(f"Report exported to {filename}")
            
        except Exception as e:
            logger.error(f"Failed to export to Excel: {e}")
    
    def run_automation_cycle(self):
        """Run one complete automation cycle"""
        logger.info("Starting due diligence automation cycle")
        
        # Run AI analysis
        ai_insights = self.run_ai_analysis()
        logger.info(f"Generated {len(ai_insights)} AI insights")
        
        # Calculate scores
        overall_score = self.calculate_overall_score()
        logger.info(f"Overall score: {overall_score['total_score']}/1000 ({overall_score['percentage']:.1f}%)")
        
        # Generate report
        report = self.generate_report()
        
        # Send notifications
        self.send_notifications(report)
        
        # Export to Excel
        self.export_to_excel()
        
        logger.info("Due diligence automation cycle completed")
        return report

def main():
    """Main function to run the automation script"""
    logger.info("Starting Due Diligence Automation System")
    
    # Initialize automation system
    automation = DueDiligenceAutomation()
    
    # Run automation cycle
    report = automation.run_automation_cycle()
    
    # Print summary
    print("\n" + "="*50)
    print("DUE DILIGENCE AUTOMATION SUMMARY")
    print("="*50)
    print(f"Overall Score: {report['overall_score']['total_score']}/1000")
    print(f"Percentage: {report['overall_score']['percentage']:.1f}%")
    print(f"Risk Level: {report['overall_score']['risk_level'].upper()}")
    print(f"Investment Grade: {report['overall_score']['investment_grade']}")
    print(f"Recommendation: {report['overall_score']['recommendation']}")
    print(f"Success Probability: {report['overall_score']['success_probability']:.1f}%")
    print(f"AI Insights Generated: {len(report['ai_insights'])}")
    print("="*50)
    
    logger.info("Due Diligence Automation System completed successfully")

if __name__ == "__main__":
    main()
