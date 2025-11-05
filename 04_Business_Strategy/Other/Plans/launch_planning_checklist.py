"""
Launch Planning Checklist System
Simplifies launch planning with a ready-to-use checklist and ClickUp Brain integration.
"""

import json
import re
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta

@dataclass
class ChecklistItem:
    """Individual checklist item with metadata"""
    id: str
    title: str
    description: str
    category: str
    priority: str  # high, medium, low
    estimated_duration: str
    dependencies: List[str]
    assignee: Optional[str] = None
    status: str = "pending"  # pending, in_progress, completed, blocked
    due_date: Optional[str] = None
    tags: List[str] = None

    def __post_init__(self):
        if self.tags is None:
            self.tags = []

@dataclass
class LaunchPhase:
    """Launch phase containing multiple checklist items"""
    name: str
    description: str
    items: List[ChecklistItem]
    start_date: Optional[str] = None
    end_date: Optional[str] = None

class LaunchPlanningChecklist:
    """Main class for managing launch planning checklist"""
    
    def __init__(self):
        self.phases: List[LaunchPhase] = []
        self.template_loaded = False
        
    def load_default_template(self):
        """Load a comprehensive default launch planning template"""
        self.phases = [
            LaunchPhase(
                name="Pre-Launch Planning",
                description="Initial planning and preparation phase",
                items=[
                    ChecklistItem(
                        id="market_research",
                        title="Conduct Market Research",
                        description="Analyze target market, competitors, and user needs",
                        category="Research",
                        priority="high",
                        estimated_duration="1-2 weeks",
                        dependencies=[],
                        tags=["research", "market-analysis"]
                    ),
                    ChecklistItem(
                        id="define_goals",
                        title="Define Launch Goals & KPIs",
                        description="Set clear objectives and key performance indicators",
                        category="Strategy",
                        priority="high",
                        estimated_duration="2-3 days",
                        dependencies=["market_research"],
                        tags=["strategy", "goals", "kpis"]
                    ),
                    ChecklistItem(
                        id="budget_planning",
                        title="Create Budget Plan",
                        description="Allocate resources and create financial projections",
                        category="Finance",
                        priority="high",
                        estimated_duration="1 week",
                        dependencies=["define_goals"],
                        tags=["budget", "finance", "planning"]
                    )
                ]
            ),
            LaunchPhase(
                name="Product Development",
                description="Core product development and testing",
                items=[
                    ChecklistItem(
                        id="mvp_development",
                        title="Develop MVP",
                        description="Build minimum viable product with core features",
                        category="Development",
                        priority="high",
                        estimated_duration="4-8 weeks",
                        dependencies=["define_goals"],
                        tags=["development", "mvp", "product"]
                    ),
                    ChecklistItem(
                        id="testing",
                        title="Conduct Testing",
                        description="Perform QA testing, user testing, and bug fixes",
                        category="Quality Assurance",
                        priority="high",
                        estimated_duration="1-2 weeks",
                        dependencies=["mvp_development"],
                        tags=["testing", "qa", "bugs"]
                    ),
                    ChecklistItem(
                        id="security_audit",
                        title="Security Audit",
                        description="Conduct security review and vulnerability assessment",
                        category="Security",
                        priority="high",
                        estimated_duration="1 week",
                        dependencies=["testing"],
                        tags=["security", "audit", "vulnerability"]
                    )
                ]
            ),
            LaunchPhase(
                name="Marketing & Branding",
                description="Marketing strategy and brand development",
                items=[
                    ChecklistItem(
                        id="brand_identity",
                        title="Develop Brand Identity",
                        description="Create logo, brand guidelines, and visual identity",
                        category="Branding",
                        priority="medium",
                        estimated_duration="1-2 weeks",
                        dependencies=["define_goals"],
                        tags=["branding", "logo", "identity"]
                    ),
                    ChecklistItem(
                        id="content_strategy",
                        title="Create Content Strategy",
                        description="Develop content calendar and marketing materials",
                        category="Marketing",
                        priority="medium",
                        estimated_duration="1 week",
                        dependencies=["brand_identity"],
                        tags=["content", "marketing", "strategy"]
                    ),
                    ChecklistItem(
                        id="social_media",
                        title="Set Up Social Media",
                        description="Create and optimize social media profiles",
                        category="Marketing",
                        priority="medium",
                        estimated_duration="3-5 days",
                        dependencies=["brand_identity"],
                        tags=["social-media", "profiles", "optimization"]
                    )
                ]
            ),
            LaunchPhase(
                name="Launch Preparation",
                description="Final preparations before launch",
                items=[
                    ChecklistItem(
                        id="legal_compliance",
                        title="Legal Compliance Check",
                        description="Ensure compliance with regulations and terms of service",
                        category="Legal",
                        priority="high",
                        estimated_duration="1 week",
                        dependencies=[],
                        tags=["legal", "compliance", "regulations"]
                    ),
                    ChecklistItem(
                        id="infrastructure",
                        title="Infrastructure Setup",
                        description="Set up servers, databases, and monitoring systems",
                        category="Infrastructure",
                        priority="high",
                        estimated_duration="1-2 weeks",
                        dependencies=["security_audit"],
                        tags=["infrastructure", "servers", "monitoring"]
                    ),
                    ChecklistItem(
                        id="launch_plan",
                        title="Create Launch Plan",
                        description="Develop detailed launch day execution plan",
                        category="Strategy",
                        priority="high",
                        estimated_duration="3-5 days",
                        dependencies=["infrastructure", "legal_compliance"],
                        tags=["launch", "execution", "plan"]
                    )
                ]
            ),
            LaunchPhase(
                name="Launch & Post-Launch",
                description="Launch execution and post-launch activities",
                items=[
                    ChecklistItem(
                        id="soft_launch",
                        title="Soft Launch",
                        description="Limited release to beta users for feedback",
                        category="Launch",
                        priority="high",
                        estimated_duration="1 week",
                        dependencies=["launch_plan"],
                        tags=["soft-launch", "beta", "feedback"]
                    ),
                    ChecklistItem(
                        id="full_launch",
                        title="Full Launch",
                        description="Public launch with marketing campaign",
                        category="Launch",
                        priority="high",
                        estimated_duration="1 day",
                        dependencies=["soft_launch"],
                        tags=["full-launch", "public", "campaign"]
                    ),
                    ChecklistItem(
                        id="monitor_metrics",
                        title="Monitor Launch Metrics",
                        description="Track KPIs and user feedback post-launch",
                        category="Analytics",
                        priority="medium",
                        estimated_duration="ongoing",
                        dependencies=["full_launch"],
                        tags=["metrics", "analytics", "monitoring"]
                    )
                ]
            )
        ]
        self.template_loaded = True
        
    def get_all_items(self) -> List[ChecklistItem]:
        """Get all checklist items from all phases"""
        all_items = []
        for phase in self.phases:
            all_items.extend(phase.items)
        return all_items
    
    def get_items_by_category(self, category: str) -> List[ChecklistItem]:
        """Get items filtered by category"""
        return [item for item in self.get_all_items() if item.category.lower() == category.lower()]
    
    def get_items_by_priority(self, priority: str) -> List[ChecklistItem]:
        """Get items filtered by priority"""
        return [item for item in self.get_all_items() if item.priority.lower() == priority.lower()]
    
    def get_items_by_status(self, status: str) -> List[ChecklistItem]:
        """Get items filtered by status"""
        return [item for item in self.get_all_items() if item.status.lower() == status.lower()]
    
    def update_item_status(self, item_id: str, status: str):
        """Update the status of a specific item"""
        for phase in self.phases:
            for item in phase.items:
                if item.id == item_id:
                    item.status = status
                    return True
        return False
    
    def assign_item(self, item_id: str, assignee: str):
        """Assign an item to a team member"""
        for phase in self.phases:
            for item in phase.items:
                if item.id == item_id:
                    item.assignee = assignee
                    return True
        return False
    
    def set_due_date(self, item_id: str, due_date: str):
        """Set due date for an item"""
        for phase in self.phases:
            for item in phase.items:
                if item.id == item_id:
                    item.due_date = due_date
                    return True
        return False
    
    def export_to_json(self) -> str:
        """Export checklist to JSON format"""
        data = {
            "phases": [asdict(phase) for phase in self.phases],
            "exported_at": datetime.now().isoformat(),
            "total_items": len(self.get_all_items())
        }
        return json.dumps(data, indent=2)
    
    def import_from_json(self, json_data: str):
        """Import checklist from JSON format"""
        data = json.loads(json_data)
        self.phases = []
        for phase_data in data["phases"]:
            items = [ChecklistItem(**item_data) for item_data in phase_data["items"]]
            phase = LaunchPhase(
                name=phase_data["name"],
                description=phase_data["description"],
                items=items,
                start_date=phase_data.get("start_date"),
                end_date=phase_data.get("end_date")
            )
            self.phases.append(phase)
        self.template_loaded = True

def main():
    """Example usage of the Launch Planning Checklist"""
    checklist = LaunchPlanningChecklist()
    checklist.load_default_template()
    
    print("Launch Planning Checklist System")
    print("=" * 40)
    
    # Display summary
    all_items = checklist.get_all_items()
    print(f"Total phases: {len(checklist.phases)}")
    print(f"Total items: {len(all_items)}")
    
    # Display high priority items
    high_priority = checklist.get_items_by_priority("high")
    print(f"\nHigh Priority Items ({len(high_priority)}):")
    for item in high_priority:
        print(f"  - {item.title} ({item.category})")
    
    # Export to JSON
    json_export = checklist.export_to_json()
    print(f"\nExported {len(json_export)} characters to JSON")

if __name__ == "__main__":
    main()




