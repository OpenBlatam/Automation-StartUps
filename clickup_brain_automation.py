#!/usr/bin/env python3
"""
ClickUp Brain Automation System
==============================

Workflow automation and smart triggers for intelligent task management
and automated efficiency optimization.
"""

import os
import json
import logging
import asyncio
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Callable
from dataclasses import dataclass, asdict
import schedule
import threading
import time
from enum import Enum

# Import our systems
from clickup_brain_simple import SimpleClickUpBrainSystem
from clickup_brain_ai_enhanced import EnhancedClickUpBrainSystem
from clickup_brain_ml_enhanced import MLEnhancedClickUpBrainSystem
from clickup_brain_integrations import ClickUpBrainIntegrationSystem

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class TriggerType(Enum):
    """Trigger types for automation"""
    TIME_BASED = "time_based"
    EFFICIENCY_THRESHOLD = "efficiency_threshold"
    TOOL_CHANGE = "tool_change"
    PERFORMANCE_DROP = "performance_drop"
    INTEGRATION_ERROR = "integration_error"
    CUSTOM_EVENT = "custom_event"

class ActionType(Enum):
    """Action types for automation"""
    SEND_NOTIFICATION = "send_notification"
    RUN_ANALYSIS = "run_analysis"
    UPDATE_TOOLS = "update_tools"
    GENERATE_REPORT = "generate_report"
    OPTIMIZE_WORKFLOW = "optimize_workflow"
    BACKUP_DATA = "backup_data"
    CUSTOM_ACTION = "custom_action"

@dataclass
class AutomationTrigger:
    """Automation trigger configuration"""
    trigger_id: str
    trigger_type: TriggerType
    name: str
    description: str
    conditions: Dict[str, Any]
    enabled: bool = True
    created_at: str = None
    last_triggered: str = None
    trigger_count: int = 0

@dataclass
class AutomationAction:
    """Automation action configuration"""
    action_id: str
    action_type: ActionType
    name: str
    description: str
    parameters: Dict[str, Any]
    enabled: bool = True
    created_at: str = None
    last_executed: str = None
    execution_count: int = 0

@dataclass
class AutomationRule:
    """Automation rule combining trigger and action"""
    rule_id: str
    name: str
    description: str
    trigger: AutomationTrigger
    action: AutomationAction
    enabled: bool = True
    priority: int = 1
    created_at: str = None
    last_executed: str = None
    execution_count: int = 0

@dataclass
class AutomationEvent:
    """Automation event log"""
    event_id: str
    rule_id: str
    trigger_type: str
    action_type: str
    status: str
    message: str
    timestamp: str
    execution_time: float
    error_details: Optional[str] = None

class WorkflowOptimizer:
    """Workflow optimization engine"""
    
    def __init__(self):
        """Initialize workflow optimizer"""
        self.optimization_history = []
        self.performance_metrics = {}
    
    def analyze_workflow_efficiency(self, tool_usage: Dict[str, Any], 
                                  team_size: int) -> Dict[str, Any]:
        """Analyze workflow efficiency"""
        try:
            analysis = {
                'current_efficiency': 0.0,
                'optimization_opportunities': [],
                'recommended_changes': [],
                'estimated_improvement': 0.0,
                'implementation_effort': 'medium'
            }
            
            # Calculate current efficiency
            if tool_usage:
                total_efficiency = sum(tool.get('efficiency_score', 0) for tool in tool_usage.values())
                analysis['current_efficiency'] = total_efficiency / len(tool_usage)
            
            # Identify optimization opportunities
            if analysis['current_efficiency'] < 7.0:
                analysis['optimization_opportunities'].append({
                    'type': 'tool_upgrade',
                    'description': 'Upgrade to more efficient tools',
                    'impact': 'high',
                    'effort': 'medium'
                })
            
            if len(tool_usage) < 5:
                analysis['optimization_opportunities'].append({
                    'type': 'tool_diversification',
                    'description': 'Add more tools for better coverage',
                    'impact': 'medium',
                    'effort': 'low'
                })
            
            # Generate recommendations
            if "ClickUp" not in tool_usage:
                analysis['recommended_changes'].append({
                    'change': 'Implement ClickUp',
                    'reason': 'Centralized project management',
                    'expected_improvement': 2.5,
                    'effort': 'medium'
                })
            
            # Calculate estimated improvement
            total_improvement = sum(change['expected_improvement'] for change in analysis['recommended_changes'])
            analysis['estimated_improvement'] = total_improvement
            
            return analysis
            
        except Exception as e:
            logger.error(f"Error analyzing workflow efficiency: {e}")
            return {'error': str(e)}
    
    def optimize_workflow(self, current_workflow: Dict[str, Any], 
                         optimization_goals: List[str]) -> Dict[str, Any]:
        """Optimize workflow based on goals"""
        try:
            optimization_plan = {
                'optimization_goals': optimization_goals,
                'current_state': current_workflow,
                'optimized_state': {},
                'changes_required': [],
                'implementation_plan': [],
                'expected_benefits': {},
                'risk_assessment': {}
            }
            
            # Generate optimization plan based on goals
            for goal in optimization_goals:
                if goal == 'improve_efficiency':
                    optimization_plan['changes_required'].append({
                        'change': 'Implement ClickUp',
                        'priority': 'high',
                        'effort': 'medium',
                        'expected_benefit': '25% efficiency improvement'
                    })
                
                elif goal == 'reduce_costs':
                    optimization_plan['changes_required'].append({
                        'change': 'Consolidate tools',
                        'priority': 'medium',
                        'effort': 'high',
                        'expected_benefit': '30% cost reduction'
                    })
                
                elif goal == 'improve_collaboration':
                    optimization_plan['changes_required'].append({
                        'change': 'Add communication tools',
                        'priority': 'high',
                        'effort': 'low',
                        'expected_benefit': '40% collaboration improvement'
                    })
            
            # Create implementation plan
            optimization_plan['implementation_plan'] = [
                {'phase': 1, 'duration': '1-2 weeks', 'changes': ['Setup ClickUp']},
                {'phase': 2, 'duration': '2-4 weeks', 'changes': ['Integrate tools']},
                {'phase': 3, 'duration': '1-2 months', 'changes': ['Optimize workflows']}
            ]
            
            return optimization_plan
            
        except Exception as e:
            logger.error(f"Error optimizing workflow: {e}")
            return {'error': str(e)}

class SmartTriggerEngine:
    """Smart trigger engine for automation"""
    
    def __init__(self):
        """Initialize smart trigger engine"""
        self.triggers = {}
        self.trigger_conditions = {}
        self.performance_history = []
    
    def register_trigger(self, trigger: AutomationTrigger):
        """Register a new trigger"""
        self.triggers[trigger.trigger_id] = trigger
        logger.info(f"Registered trigger: {trigger.name}")
    
    def check_triggers(self, current_data: Dict[str, Any]) -> List[AutomationTrigger]:
        """Check all registered triggers"""
        triggered = []
        
        for trigger_id, trigger in self.triggers.items():
            if not trigger.enabled:
                continue
            
            try:
                if self._evaluate_trigger_condition(trigger, current_data):
                    triggered.append(trigger)
                    trigger.last_triggered = datetime.now().isoformat()
                    trigger.trigger_count += 1
                    logger.info(f"Trigger activated: {trigger.name}")
            except Exception as e:
                logger.error(f"Error checking trigger {trigger.name}: {e}")
        
        return triggered
    
    def _evaluate_trigger_condition(self, trigger: AutomationTrigger, 
                                  current_data: Dict[str, Any]) -> bool:
        """Evaluate trigger condition"""
        try:
            conditions = trigger.conditions
            
            if trigger.trigger_type == TriggerType.EFFICIENCY_THRESHOLD:
                current_efficiency = current_data.get('efficiency_score', 0)
                threshold = conditions.get('threshold', 7.0)
                return current_efficiency < threshold
            
            elif trigger.trigger_type == TriggerType.TOOL_CHANGE:
                current_tools = set(current_data.get('tool_usage', {}).keys())
                previous_tools = set(conditions.get('previous_tools', []))
                return current_tools != previous_tools
            
            elif trigger.trigger_type == TriggerType.PERFORMANCE_DROP:
                current_performance = current_data.get('efficiency_score', 0)
                previous_performance = conditions.get('previous_performance', 0)
                drop_threshold = conditions.get('drop_threshold', 1.0)
                return (previous_performance - current_performance) > drop_threshold
            
            elif trigger.trigger_type == TriggerType.INTEGRATION_ERROR:
                error_count = current_data.get('integration_errors', 0)
                max_errors = conditions.get('max_errors', 3)
                return error_count > max_errors
            
            return False
            
        except Exception as e:
            logger.error(f"Error evaluating trigger condition: {e}")
            return False

class ActionExecutor:
    """Action executor for automation"""
    
    def __init__(self):
        """Initialize action executor"""
        self.actions = {}
        self.execution_history = []
        self.simple_system = SimpleClickUpBrainSystem()
        self.enhanced_system = EnhancedClickUpBrainSystem()
        self.ml_system = MLEnhancedClickUpBrainSystem()
        self.integration_system = ClickUpBrainIntegrationSystem()
    
    def register_action(self, action: AutomationAction):
        """Register a new action"""
        self.actions[action.action_id] = action
        logger.info(f"Registered action: {action.name}")
    
    async def execute_action(self, action: AutomationAction, 
                           context: Dict[str, Any]) -> Dict[str, Any]:
        """Execute an action"""
        start_time = time.time()
        
        try:
            logger.info(f"Executing action: {action.name}")
            
            if action.action_type == ActionType.SEND_NOTIFICATION:
                result = await self._send_notification(action, context)
            
            elif action.action_type == ActionType.RUN_ANALYSIS:
                result = await self._run_analysis(action, context)
            
            elif action.action_type == ActionType.UPDATE_TOOLS:
                result = await self._update_tools(action, context)
            
            elif action.action_type == ActionType.GENERATE_REPORT:
                result = await self._generate_report(action, context)
            
            elif action.action_type == ActionType.OPTIMIZE_WORKFLOW:
                result = await self._optimize_workflow(action, context)
            
            elif action.action_type == ActionType.BACKUP_DATA:
                result = await self._backup_data(action, context)
            
            else:
                result = {'status': 'error', 'message': 'Unknown action type'}
            
            execution_time = time.time() - start_time
            
            # Log execution
            event = AutomationEvent(
                event_id=f"event_{int(time.time())}",
                rule_id=context.get('rule_id', 'unknown'),
                trigger_type=context.get('trigger_type', 'unknown'),
                action_type=action.action_type.value,
                status=result.get('status', 'unknown'),
                message=result.get('message', ''),
                timestamp=datetime.now().isoformat(),
                execution_time=execution_time
            )
            
            self.execution_history.append(event)
            action.last_executed = datetime.now().isoformat()
            action.execution_count += 1
            
            return result
            
        except Exception as e:
            execution_time = time.time() - start_time
            error_event = AutomationEvent(
                event_id=f"event_{int(time.time())}",
                rule_id=context.get('rule_id', 'unknown'),
                trigger_type=context.get('trigger_type', 'unknown'),
                action_type=action.action_type.value,
                status='error',
                message=f'Action execution failed: {str(e)}',
                timestamp=datetime.now().isoformat(),
                execution_time=execution_time,
                error_details=str(e)
            )
            
            self.execution_history.append(error_event)
            return {'status': 'error', 'message': str(e)}
    
    async def _send_notification(self, action: AutomationAction, 
                               context: Dict[str, Any]) -> Dict[str, Any]:
        """Send notification action"""
        try:
            message = action.parameters.get('message', 'Automation notification')
            service = action.parameters.get('service', 'slack')
            
            if service == 'slack':
                success = await self.integration_system.send_team_notification(message)
                return {'status': 'success', 'message': 'Notification sent via Slack'}
            
            return {'status': 'success', 'message': 'Notification sent'}
            
        except Exception as e:
            return {'status': 'error', 'message': str(e)}
    
    async def _run_analysis(self, action: AutomationAction, 
                          context: Dict[str, Any]) -> Dict[str, Any]:
        """Run analysis action"""
        try:
            directory_path = action.parameters.get('directory_path', '.')
            team_size = action.parameters.get('team_size', 10)
            analysis_type = action.parameters.get('analysis_type', 'ai_enhanced')
            
            if analysis_type == 'ml_enhanced':
                results = self.ml_system.analyze_with_ml(directory_path, team_size)
            elif analysis_type == 'ai_enhanced':
                results = self.enhanced_system.analyze_with_ai(directory_path, team_size)
            else:
                results = self.simple_system.scan_directory(directory_path)
            
            return {'status': 'success', 'message': 'Analysis completed', 'results': results}
            
        except Exception as e:
            return {'status': 'error', 'message': str(e)}
    
    async def _update_tools(self, action: AutomationAction, 
                          context: Dict[str, Any]) -> Dict[str, Any]:
        """Update tools action"""
        try:
            # This would integrate with actual tool management systems
            tool_updates = action.parameters.get('tool_updates', [])
            
            return {'status': 'success', 'message': f'Updated {len(tool_updates)} tools'}
            
        except Exception as e:
            return {'status': 'error', 'message': str(e)}
    
    async def _generate_report(self, action: AutomationAction, 
                             context: Dict[str, Any]) -> Dict[str, Any]:
        """Generate report action"""
        try:
            report_type = action.parameters.get('report_type', 'basic')
            output_format = action.parameters.get('output_format', 'markdown')
            
            # Generate report based on type
            if report_type == 'analytics':
                from clickup_brain_analytics import AdvancedAnalyticsEngine
                analytics_system = AdvancedAnalyticsEngine()
                results = analytics_system.generate_comprehensive_analytics('.', 10)
                report = analytics_system.generate_analytics_report(results)
            else:
                results = self.simple_system.scan_directory('.')
                report = self.simple_system.generate_report(results)
            
            # Save report
            filename = f"automated_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(report)
            
            return {'status': 'success', 'message': f'Report generated: {filename}'}
            
        except Exception as e:
            return {'status': 'error', 'message': str(e)}
    
    async def _optimize_workflow(self, action: AutomationAction, 
                               context: Dict[str, Any]) -> Dict[str, Any]:
        """Optimize workflow action"""
        try:
            from clickup_brain_analytics import AdvancedAnalyticsEngine
            analytics_system = AdvancedAnalyticsEngine()
            
            # Get current analysis
            results = analytics_system.generate_comprehensive_analytics('.', 10)
            
            # Generate optimization recommendations
            optimization = results.get('optimization_recommendations', {})
            
            return {'status': 'success', 'message': 'Workflow optimization completed', 'optimization': optimization}
            
        except Exception as e:
            return {'status': 'error', 'message': str(e)}
    
    async def _backup_data(self, action: AutomationAction, 
                         context: Dict[str, Any]) -> Dict[str, Any]:
        """Backup data action"""
        try:
            backup_path = action.parameters.get('backup_path', './backups')
            os.makedirs(backup_path, exist_ok=True)
            
            # Backup execution history
            backup_file = os.path.join(backup_path, f"automation_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json")
            
            backup_data = {
                'timestamp': datetime.now().isoformat(),
                'execution_history': [asdict(event) for event in self.execution_history[-100:]],
                'system_state': context
            }
            
            with open(backup_file, 'w', encoding='utf-8') as f:
                json.dump(backup_data, f, ensure_ascii=False, indent=2)
            
            return {'status': 'success', 'message': f'Data backed up to {backup_file}'}
            
        except Exception as e:
            return {'status': 'error', 'message': str(e)}

class ClickUpBrainAutomationSystem:
    """Main automation system for ClickUp Brain"""
    
    def __init__(self):
        """Initialize automation system"""
        self.trigger_engine = SmartTriggerEngine()
        self.action_executor = ActionExecutor()
        self.workflow_optimizer = WorkflowOptimizer()
        self.automation_rules = {}
        self.is_running = False
        self.automation_thread = None
        
        # Initialize default automation rules
        self._setup_default_automation_rules()
    
    def _setup_default_automation_rules(self):
        """Setup default automation rules"""
        try:
            # Efficiency monitoring rule
            efficiency_trigger = AutomationTrigger(
                trigger_id="efficiency_monitor",
                trigger_type=TriggerType.EFFICIENCY_THRESHOLD,
                name="Efficiency Threshold Monitor",
                description="Monitor team efficiency and trigger actions when below threshold",
                conditions={'threshold': 6.0},
                created_at=datetime.now().isoformat()
            )
            
            efficiency_action = AutomationAction(
                action_id="efficiency_notification",
                action_type=ActionType.SEND_NOTIFICATION,
                name="Efficiency Alert",
                description="Send notification when efficiency drops",
                parameters={
                    'message': 'Team efficiency has dropped below threshold. Consider tool optimization.',
                    'service': 'slack'
                },
                created_at=datetime.now().isoformat()
            )
            
            efficiency_rule = AutomationRule(
                rule_id="efficiency_rule",
                name="Efficiency Monitoring Rule",
                description="Monitor and alert on efficiency drops",
                trigger=efficiency_trigger,
                action=efficiency_action,
                created_at=datetime.now().isoformat()
            )
            
            # Daily analysis rule
            daily_trigger = AutomationTrigger(
                trigger_id="daily_analysis",
                trigger_type=TriggerType.TIME_BASED,
                name="Daily Analysis Trigger",
                description="Run daily analysis at 9 AM",
                conditions={'time': '09:00', 'days': ['monday', 'tuesday', 'wednesday', 'thursday', 'friday']},
                created_at=datetime.now().isoformat()
            )
            
            daily_action = AutomationAction(
                action_id="daily_analysis_action",
                action_type=ActionType.RUN_ANALYSIS,
                name="Daily Analysis",
                description="Run daily team efficiency analysis",
                parameters={
                    'directory_path': '.',
                    'team_size': 10,
                    'analysis_type': 'ai_enhanced'
                },
                created_at=datetime.now().isoformat()
            )
            
            daily_rule = AutomationRule(
                rule_id="daily_analysis_rule",
                name="Daily Analysis Rule",
                description="Run daily analysis and generate reports",
                trigger=daily_trigger,
                action=daily_action,
                created_at=datetime.now().isoformat()
            )
            
            # Register rules
            self.add_automation_rule(efficiency_rule)
            self.add_automation_rule(daily_rule)
            
            logger.info("Default automation rules setup completed")
            
        except Exception as e:
            logger.error(f"Error setting up default automation rules: {e}")
    
    def add_automation_rule(self, rule: AutomationRule):
        """Add automation rule"""
        self.automation_rules[rule.rule_id] = rule
        self.trigger_engine.register_trigger(rule.trigger)
        self.action_executor.register_action(rule.action)
        logger.info(f"Added automation rule: {rule.name}")
    
    def remove_automation_rule(self, rule_id: str):
        """Remove automation rule"""
        if rule_id in self.automation_rules:
            rule = self.automation_rules[rule_id]
            del self.automation_rules[rule_id]
            logger.info(f"Removed automation rule: {rule.name}")
    
    def start_automation(self):
        """Start automation system"""
        if not self.is_running:
            self.is_running = True
            self.automation_thread = threading.Thread(target=self._automation_loop, daemon=True)
            self.automation_thread.start()
            logger.info("Automation system started")
    
    def stop_automation(self):
        """Stop automation system"""
        self.is_running = False
        if self.automation_thread:
            self.automation_thread.join(timeout=5)
        logger.info("Automation system stopped")
    
    def _automation_loop(self):
        """Main automation loop"""
        logger.info("Automation loop started")
        
        while self.is_running:
            try:
                # Get current system state
                current_data = self._get_current_system_state()
                
                # Check triggers
                triggered = self.trigger_engine.check_triggers(current_data)
                
                # Execute actions for triggered rules
                for trigger in triggered:
                    rule = self._find_rule_by_trigger(trigger.trigger_id)
                    if rule and rule.enabled:
                        asyncio.run(self._execute_rule(rule, current_data))
                
                # Sleep for 60 seconds before next check
                time.sleep(60)
                
            except Exception as e:
                logger.error(f"Error in automation loop: {e}")
                time.sleep(60)
        
        logger.info("Automation loop stopped")
    
    def _get_current_system_state(self) -> Dict[str, Any]:
        """Get current system state"""
        try:
            # Get basic analysis
            basic_analysis = self.action_executor.simple_system.scan_directory('.')
            
            return {
                'efficiency_score': basic_analysis.get('efficiency_score', 0),
                'tool_usage': basic_analysis.get('tool_usage', {}),
                'categories': basic_analysis.get('categories', []),
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error getting current system state: {e}")
            return {}
    
    def _find_rule_by_trigger(self, trigger_id: str) -> Optional[AutomationRule]:
        """Find rule by trigger ID"""
        for rule in self.automation_rules.values():
            if rule.trigger.trigger_id == trigger_id:
                return rule
        return None
    
    async def _execute_rule(self, rule: AutomationRule, context: Dict[str, Any]):
        """Execute automation rule"""
        try:
            logger.info(f"Executing rule: {rule.name}")
            
            # Add rule context
            context['rule_id'] = rule.rule_id
            context['trigger_type'] = rule.trigger.trigger_type.value
            
            # Execute action
            result = await self.action_executor.execute_action(rule.action, context)
            
            # Update rule statistics
            rule.last_executed = datetime.now().isoformat()
            rule.execution_count += 1
            
            logger.info(f"Rule executed successfully: {rule.name}")
            
        except Exception as e:
            logger.error(f"Error executing rule {rule.name}: {e}")
    
    def get_automation_status(self) -> Dict[str, Any]:
        """Get automation system status"""
        return {
            'is_running': self.is_running,
            'total_rules': len(self.automation_rules),
            'enabled_rules': len([r for r in self.automation_rules.values() if r.enabled]),
            'total_triggers': len(self.trigger_engine.triggers),
            'total_actions': len(self.action_executor.actions),
            'execution_history_count': len(self.action_executor.execution_history),
            'last_execution': self.action_executor.execution_history[-1].timestamp if self.action_executor.execution_history else None
        }
    
    def get_automation_rules(self) -> List[Dict[str, Any]]:
        """Get all automation rules"""
        return [asdict(rule) for rule in self.automation_rules.values()]
    
    def get_execution_history(self, limit: int = 50) -> List[Dict[str, Any]]:
        """Get execution history"""
        history = self.action_executor.execution_history[-limit:] if self.action_executor.execution_history else []
        return [asdict(event) for event in history]
    
    def create_custom_rule(self, name: str, description: str, 
                          trigger_config: Dict[str, Any], 
                          action_config: Dict[str, Any]) -> str:
        """Create custom automation rule"""
        try:
            rule_id = f"custom_rule_{int(time.time())}"
            
            # Create trigger
            trigger = AutomationTrigger(
                trigger_id=f"{rule_id}_trigger",
                trigger_type=TriggerType(trigger_config['type']),
                name=f"{name} Trigger",
                description=description,
                conditions=trigger_config.get('conditions', {}),
                created_at=datetime.now().isoformat()
            )
            
            # Create action
            action = AutomationAction(
                action_id=f"{rule_id}_action",
                action_type=ActionType(action_config['type']),
                name=f"{name} Action",
                description=description,
                parameters=action_config.get('parameters', {}),
                created_at=datetime.now().isoformat()
            )
            
            # Create rule
            rule = AutomationRule(
                rule_id=rule_id,
                name=name,
                description=description,
                trigger=trigger,
                action=action,
                created_at=datetime.now().isoformat()
            )
            
            # Add rule
            self.add_automation_rule(rule)
            
            return rule_id
            
        except Exception as e:
            logger.error(f"Error creating custom rule: {e}")
            return None

def main():
    """Main function for testing"""
    print("🤖 ClickUp Brain Automation System")
    print("=" * 50)
    
    # Initialize automation system
    automation_system = ClickUpBrainAutomationSystem()
    
    print("🤖 Automation Features:")
    print("  • Smart trigger engine")
    print("  • Action executor")
    print("  • Workflow optimizer")
    print("  • Custom rule creation")
    print("  • Real-time monitoring")
    print("  • Automated reporting")
    
    print(f"\n📊 Automation Status:")
    status = automation_system.get_automation_status()
    print(f"  • Total Rules: {status['total_rules']}")
    print(f"  • Enabled Rules: {status['enabled_rules']}")
    print(f"  • Total Triggers: {status['total_triggers']}")
    print(f"  • Total Actions: {status['total_actions']}")
    
    print(f"\n🔧 Available Rules:")
    rules = automation_system.get_automation_rules()
    for rule in rules:
        print(f"  • {rule['name']}: {rule['description']}")
    
    # Start automation system
    print(f"\n🚀 Starting automation system...")
    automation_system.start_automation()
    
    try:
        # Run for 2 minutes to demonstrate
        print("⏱️ Running automation for 2 minutes...")
        time.sleep(120)
        
        # Get execution history
        history = automation_system.get_execution_history(10)
        print(f"\n📈 Recent Executions: {len(history)}")
        for event in history[-5:]:
            print(f"  • {event['timestamp']}: {event['action_type']} - {event['status']}")
        
    except KeyboardInterrupt:
        print("\n🛑 Automation interrupted by user")
    finally:
        automation_system.stop_automation()
        print("👋 Automation system stopped")

if __name__ == "__main__":
    main()










