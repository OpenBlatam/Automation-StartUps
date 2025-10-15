#!/usr/bin/env python3
"""
ClickUp Brain Integration System
===============================

Direct integration with popular tool APIs for real-time data synchronization
and automated workflow management.
"""

import os
import json
import logging
import requests
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, asdict
import asyncio
import aiohttp
from urllib.parse import urlencode
import base64

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class IntegrationConfig:
    """Integration configuration data structure"""
    service_name: str
    api_endpoint: str
    auth_type: str
    api_key: Optional[str] = None
    access_token: Optional[str] = None
    webhook_url: Optional[str] = None
    rate_limit: int = 100
    enabled: bool = True

@dataclass
class IntegrationData:
    """Integration data structure"""
    service: str
    data_type: str
    data: Dict[str, Any]
    timestamp: str
    sync_status: str
    record_count: int

class ClickUpIntegration:
    """ClickUp API integration"""
    
    def __init__(self, api_key: str):
        """Initialize ClickUp integration"""
        self.api_key = api_key
        self.base_url = "https://api.clickup.com/api/v2"
        self.headers = {
            "Authorization": api_key,
            "Content-Type": "application/json"
        }
    
    async def get_teams(self) -> List[Dict[str, Any]]:
        """Get ClickUp teams"""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(f"{self.base_url}/team", headers=self.headers) as response:
                    if response.status == 200:
                        data = await response.json()
                        return data.get('teams', [])
                    else:
                        logger.error(f"ClickUp API error: {response.status}")
                        return []
        except Exception as e:
            logger.error(f"Error fetching ClickUp teams: {e}")
            return []
    
    async def get_spaces(self, team_id: str) -> List[Dict[str, Any]]:
        """Get ClickUp spaces"""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(f"{self.base_url}/team/{team_id}/space", headers=self.headers) as response:
                    if response.status == 200:
                        data = await response.json()
                        return data.get('spaces', [])
                    else:
                        logger.error(f"ClickUp API error: {response.status}")
                        return []
        except Exception as e:
            logger.error(f"Error fetching ClickUp spaces: {e}")
            return []
    
    async def get_tasks(self, list_id: str, limit: int = 100) -> List[Dict[str, Any]]:
        """Get ClickUp tasks"""
        try:
            params = {"limit": limit}
            async with aiohttp.ClientSession() as session:
                async with session.get(f"{self.base_url}/list/{list_id}/task", 
                                     headers=self.headers, params=params) as response:
                    if response.status == 200:
                        data = await response.json()
                        return data.get('tasks', [])
                    else:
                        logger.error(f"ClickUp API error: {response.status}")
                        return []
        except Exception as e:
            logger.error(f"Error fetching ClickUp tasks: {e}")
            return []
    
    async def get_team_activity(self, team_id: str) -> List[Dict[str, Any]]:
        """Get team activity"""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(f"{self.base_url}/team/{team_id}/activity", 
                                     headers=self.headers) as response:
                    if response.status == 200:
                        data = await response.json()
                        return data.get('activities', [])
                    else:
                        logger.error(f"ClickUp API error: {response.status}")
                        return []
        except Exception as e:
            logger.error(f"Error fetching ClickUp activity: {e}")
            return []

class SlackIntegration:
    """Slack API integration"""
    
    def __init__(self, bot_token: str):
        """Initialize Slack integration"""
        self.bot_token = bot_token
        self.base_url = "https://slack.com/api"
        self.headers = {
            "Authorization": f"Bearer {bot_token}",
            "Content-Type": "application/json"
        }
    
    async def get_channels(self) -> List[Dict[str, Any]]:
        """Get Slack channels"""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(f"{self.base_url}/conversations.list", 
                                     headers=self.headers) as response:
                    if response.status == 200:
                        data = await response.json()
                        return data.get('channels', [])
                    else:
                        logger.error(f"Slack API error: {response.status}")
                        return []
        except Exception as e:
            logger.error(f"Error fetching Slack channels: {e}")
            return []
    
    async def get_members(self) -> List[Dict[str, Any]]:
        """Get Slack members"""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(f"{self.base_url}/users.list", 
                                     headers=self.headers) as response:
                    if response.status == 200:
                        data = await response.json()
                        return data.get('members', [])
                    else:
                        logger.error(f"Slack API error: {response.status}")
                        return []
        except Exception as e:
            logger.error(f"Error fetching Slack members: {e}")
            return []
    
    async def send_message(self, channel: str, message: str) -> bool:
        """Send message to Slack channel"""
        try:
            payload = {
                "channel": channel,
                "text": message
            }
            async with aiohttp.ClientSession() as session:
                async with session.post(f"{self.base_url}/chat.postMessage", 
                                      headers=self.headers, json=payload) as response:
                    return response.status == 200
        except Exception as e:
            logger.error(f"Error sending Slack message: {e}")
            return False

class GitHubIntegration:
    """GitHub API integration"""
    
    def __init__(self, access_token: str):
        """Initialize GitHub integration"""
        self.access_token = access_token
        self.base_url = "https://api.github.com"
        self.headers = {
            "Authorization": f"token {access_token}",
            "Accept": "application/vnd.github.v3+json"
        }
    
    async def get_repositories(self, org: str = None) -> List[Dict[str, Any]]:
        """Get GitHub repositories"""
        try:
            url = f"{self.base_url}/orgs/{org}/repos" if org else f"{self.base_url}/user/repos"
            async with aiohttp.ClientSession() as session:
                async with session.get(url, headers=self.headers) as response:
                    if response.status == 200:
                        return await response.json()
                    else:
                        logger.error(f"GitHub API error: {response.status}")
                        return []
        except Exception as e:
            logger.error(f"Error fetching GitHub repositories: {e}")
            return []
    
    async def get_commits(self, owner: str, repo: str, since: str = None) -> List[Dict[str, Any]]:
        """Get GitHub commits"""
        try:
            params = {}
            if since:
                params['since'] = since
            
            async with aiohttp.ClientSession() as session:
                async with session.get(f"{self.base_url}/repos/{owner}/{repo}/commits", 
                                     headers=self.headers, params=params) as response:
                    if response.status == 200:
                        return await response.json()
                    else:
                        logger.error(f"GitHub API error: {response.status}")
                        return []
        except Exception as e:
            logger.error(f"Error fetching GitHub commits: {e}")
            return []
    
    async def get_issues(self, owner: str, repo: str) -> List[Dict[str, Any]]:
        """Get GitHub issues"""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(f"{self.base_url}/repos/{owner}/{repo}/issues", 
                                     headers=self.headers) as response:
                    if response.status == 200:
                        return await response.json()
                    else:
                        logger.error(f"GitHub API error: {response.status}")
                        return []
        except Exception as e:
            logger.error(f"Error fetching GitHub issues: {e}")
            return []

class GoogleWorkspaceIntegration:
    """Google Workspace API integration"""
    
    def __init__(self, credentials_file: str):
        """Initialize Google Workspace integration"""
        self.credentials_file = credentials_file
        self.scopes = [
            'https://www.googleapis.com/auth/drive',
            'https://www.googleapis.com/auth/documents',
            'https://www.googleapis.com/auth/spreadsheets'
        ]
    
    async def get_drive_files(self) -> List[Dict[str, Any]]:
        """Get Google Drive files"""
        try:
            # This would require proper Google API setup
            # For now, return mock data
            return [
                {
                    "id": "mock_file_1",
                    "name": "Project Document",
                    "mimeType": "application/vnd.google-apps.document",
                    "createdTime": datetime.now().isoformat(),
                    "modifiedTime": datetime.now().isoformat()
                }
            ]
        except Exception as e:
            logger.error(f"Error fetching Google Drive files: {e}")
            return []
    
    async def get_sheets_data(self, spreadsheet_id: str) -> List[Dict[str, Any]]:
        """Get Google Sheets data"""
        try:
            # This would require proper Google API setup
            # For now, return mock data
            return [
                {
                    "range": "Sheet1!A1:C10",
                    "values": [
                        ["Task", "Status", "Assignee"],
                        ["Task 1", "Completed", "John Doe"],
                        ["Task 2", "In Progress", "Jane Smith"]
                    ]
                }
            ]
        except Exception as e:
            logger.error(f"Error fetching Google Sheets data: {e}")
            return []

class IntegrationManager:
    """Manages all integrations"""
    
    def __init__(self):
        """Initialize integration manager"""
        self.integrations = {}
        self.configs = {}
        self.sync_status = {}
        self._load_integration_configs()
    
    def _load_integration_configs(self):
        """Load integration configurations"""
        # Default configurations (in production, these would come from a config file or database)
        self.configs = {
            'clickup': IntegrationConfig(
                service_name='ClickUp',
                api_endpoint='https://api.clickup.com/api/v2',
                auth_type='api_key',
                api_key=os.getenv('CLICKUP_API_KEY'),
                rate_limit=100,
                enabled=bool(os.getenv('CLICKUP_API_KEY'))
            ),
            'slack': IntegrationConfig(
                service_name='Slack',
                api_endpoint='https://slack.com/api',
                auth_type='bot_token',
                api_key=os.getenv('SLACK_BOT_TOKEN'),
                rate_limit=50,
                enabled=bool(os.getenv('SLACK_BOT_TOKEN'))
            ),
            'github': IntegrationConfig(
                service_name='GitHub',
                api_endpoint='https://api.github.com',
                auth_type='access_token',
                access_token=os.getenv('GITHUB_ACCESS_TOKEN'),
                rate_limit=5000,
                enabled=bool(os.getenv('GITHUB_ACCESS_TOKEN'))
            ),
            'google_workspace': IntegrationConfig(
                service_name='Google Workspace',
                api_endpoint='https://www.googleapis.com',
                auth_type='service_account',
                api_key=os.getenv('GOOGLE_CREDENTIALS_FILE'),
                rate_limit=100,
                enabled=bool(os.getenv('GOOGLE_CREDENTIALS_FILE'))
            )
        }
    
    def initialize_integrations(self):
        """Initialize all enabled integrations"""
        for service_name, config in self.configs.items():
            if config.enabled and config.api_key:
                try:
                    if service_name == 'clickup':
                        self.integrations[service_name] = ClickUpIntegration(config.api_key)
                    elif service_name == 'slack':
                        self.integrations[service_name] = SlackIntegration(config.api_key)
                    elif service_name == 'github':
                        self.integrations[service_name] = GitHubIntegration(config.access_token)
                    elif service_name == 'google_workspace':
                        self.integrations[service_name] = GoogleWorkspaceIntegration(config.api_key)
                    
                    self.sync_status[service_name] = {
                        'last_sync': None,
                        'status': 'initialized',
                        'error_count': 0
                    }
                    logger.info(f"Initialized {service_name} integration")
                    
                except Exception as e:
                    logger.error(f"Failed to initialize {service_name} integration: {e}")
                    self.sync_status[service_name] = {
                        'last_sync': None,
                        'status': 'error',
                        'error_count': 1
                    }
    
    async def sync_all_data(self) -> Dict[str, Any]:
        """Sync data from all integrations"""
        sync_results = {}
        
        for service_name, integration in self.integrations.items():
            try:
                logger.info(f"Syncing data from {service_name}...")
                
                if service_name == 'clickup':
                    sync_results[service_name] = await self._sync_clickup_data(integration)
                elif service_name == 'slack':
                    sync_results[service_name] = await self._sync_slack_data(integration)
                elif service_name == 'github':
                    sync_results[service_name] = await self._sync_github_data(integration)
                elif service_name == 'google_workspace':
                    sync_results[service_name] = await self._sync_google_data(integration)
                
                self.sync_status[service_name]['last_sync'] = datetime.now().isoformat()
                self.sync_status[service_name]['status'] = 'success'
                self.sync_status[service_name]['error_count'] = 0
                
            except Exception as e:
                logger.error(f"Error syncing {service_name}: {e}")
                self.sync_status[service_name]['status'] = 'error'
                self.sync_status[service_name]['error_count'] += 1
                sync_results[service_name] = {'error': str(e)}
        
        return sync_results
    
    async def _sync_clickup_data(self, integration: ClickUpIntegration) -> Dict[str, Any]:
        """Sync ClickUp data"""
        try:
            teams = await integration.get_teams()
            sync_data = {
                'teams': teams,
                'total_teams': len(teams),
                'sync_timestamp': datetime.now().isoformat()
            }
            
            # Get additional data for first team if available
            if teams:
                team_id = teams[0]['id']
                spaces = await integration.get_spaces(team_id)
                sync_data['spaces'] = spaces
                sync_data['total_spaces'] = len(spaces)
                
                # Get activity for the team
                activity = await integration.get_team_activity(team_id)
                sync_data['recent_activity'] = activity[:10]  # Last 10 activities
                sync_data['total_activities'] = len(activity)
            
            return sync_data
            
        except Exception as e:
            logger.error(f"Error syncing ClickUp data: {e}")
            return {'error': str(e)}
    
    async def _sync_slack_data(self, integration: SlackIntegration) -> Dict[str, Any]:
        """Sync Slack data"""
        try:
            channels = await integration.get_channels()
            members = await integration.get_members()
            
            sync_data = {
                'channels': channels,
                'members': members,
                'total_channels': len(channels),
                'total_members': len(members),
                'sync_timestamp': datetime.now().isoformat()
            }
            
            return sync_data
            
        except Exception as e:
            logger.error(f"Error syncing Slack data: {e}")
            return {'error': str(e)}
    
    async def _sync_github_data(self, integration: GitHubIntegration) -> Dict[str, Any]:
        """Sync GitHub data"""
        try:
            repos = await integration.get_repositories()
            sync_data = {
                'repositories': repos,
                'total_repos': len(repos),
                'sync_timestamp': datetime.now().isoformat()
            }
            
            # Get additional data for first repo if available
            if repos:
                repo = repos[0]
                owner = repo['owner']['login']
                repo_name = repo['name']
                
                # Get recent commits
                since_date = (datetime.now() - timedelta(days=7)).isoformat()
                commits = await integration.get_commits(owner, repo_name, since_date)
                sync_data['recent_commits'] = commits[:10]  # Last 10 commits
                
                # Get open issues
                issues = await integration.get_issues(owner, repo_name)
                sync_data['open_issues'] = [issue for issue in issues if issue['state'] == 'open']
                sync_data['total_open_issues'] = len(sync_data['open_issues'])
            
            return sync_data
            
        except Exception as e:
            logger.error(f"Error syncing GitHub data: {e}")
            return {'error': str(e)}
    
    async def _sync_google_data(self, integration: GoogleWorkspaceIntegration) -> Dict[str, Any]:
        """Sync Google Workspace data"""
        try:
            drive_files = await integration.get_drive_files()
            
            sync_data = {
                'drive_files': drive_files,
                'total_files': len(drive_files),
                'sync_timestamp': datetime.now().isoformat()
            }
            
            return sync_data
            
        except Exception as e:
            logger.error(f"Error syncing Google Workspace data: {e}")
            return {'error': str(e)}
    
    def get_sync_status(self) -> Dict[str, Any]:
        """Get sync status for all integrations"""
        return {
            'integrations': self.sync_status,
            'total_integrations': len(self.integrations),
            'enabled_integrations': len([s for s in self.sync_status.values() if s['status'] != 'error']),
            'last_full_sync': max([s['last_sync'] for s in self.sync_status.values() if s['last_sync']], default=None)
        }
    
    async def send_notification(self, service: str, message: str, channel: str = None) -> bool:
        """Send notification through integration"""
        try:
            if service == 'slack' and 'slack' in self.integrations:
                if not channel:
                    channels = await self.integrations['slack'].get_channels()
                    channel = channels[0]['id'] if channels else None
                
                if channel:
                    return await self.integrations['slack'].send_message(channel, message)
            
            return False
            
        except Exception as e:
            logger.error(f"Error sending notification via {service}: {e}")
            return False

class ClickUpBrainIntegrationSystem:
    """Main integration system for ClickUp Brain"""
    
    def __init__(self):
        """Initialize integration system"""
        self.integration_manager = IntegrationManager()
        self.integration_manager.initialize_integrations()
        self.sync_history = []
    
    async def perform_full_sync(self) -> Dict[str, Any]:
        """Perform full data synchronization"""
        logger.info("Starting full data synchronization...")
        
        sync_results = await self.integration_manager.sync_all_data()
        
        # Store sync history
        sync_record = {
            'timestamp': datetime.now().isoformat(),
            'results': sync_results,
            'status': 'completed',
            'total_services': len(sync_results),
            'successful_syncs': len([r for r in sync_results.values() if 'error' not in r])
        }
        
        self.sync_history.append(sync_record)
        
        # Keep only last 50 sync records
        if len(self.sync_history) > 50:
            self.sync_history = self.sync_history[-50:]
        
        logger.info(f"Full sync completed. {sync_record['successful_syncs']}/{sync_record['total_services']} services synced successfully")
        
        return sync_record
    
    def get_integration_analytics(self) -> Dict[str, Any]:
        """Get integration analytics"""
        sync_status = self.integration_manager.get_sync_status()
        
        analytics = {
            'integration_status': sync_status,
            'sync_history_summary': {
                'total_syncs': len(self.sync_history),
                'last_sync': self.sync_history[-1]['timestamp'] if self.sync_history else None,
                'average_success_rate': self._calculate_success_rate()
            },
            'data_insights': self._generate_data_insights(),
            'recommendations': self._generate_integration_recommendations()
        }
        
        return analytics
    
    def _calculate_success_rate(self) -> float:
        """Calculate sync success rate"""
        if not self.sync_history:
            return 0.0
        
        total_syncs = len(self.sync_history)
        successful_syncs = sum(1 for sync in self.sync_history if sync['status'] == 'completed')
        
        return successful_syncs / total_syncs
    
    def _generate_data_insights(self) -> List[Dict[str, Any]]:
        """Generate insights from integration data"""
        insights = []
        
        if self.sync_history:
            last_sync = self.sync_history[-1]
            
            # ClickUp insights
            if 'clickup' in last_sync['results'] and 'error' not in last_sync['results']['clickup']:
                clickup_data = last_sync['results']['clickup']
                insights.append({
                    'type': 'clickup_usage',
                    'title': 'ClickUp Activity',
                    'description': f"Active teams: {clickup_data.get('total_teams', 0)}, Spaces: {clickup_data.get('total_spaces', 0)}",
                    'impact': 'high' if clickup_data.get('total_teams', 0) > 0 else 'medium'
                })
            
            # Slack insights
            if 'slack' in last_sync['results'] and 'error' not in last_sync['results']['slack']:
                slack_data = last_sync['results']['slack']
                insights.append({
                    'type': 'slack_activity',
                    'title': 'Slack Communication',
                    'description': f"Channels: {slack_data.get('total_channels', 0)}, Members: {slack_data.get('total_members', 0)}",
                    'impact': 'high' if slack_data.get('total_members', 0) > 10 else 'medium'
                })
            
            # GitHub insights
            if 'github' in last_sync['results'] and 'error' not in last_sync['results']['github']:
                github_data = last_sync['results']['github']
                insights.append({
                    'type': 'github_activity',
                    'title': 'GitHub Development',
                    'description': f"Repositories: {github_data.get('total_repos', 0)}, Open Issues: {github_data.get('total_open_issues', 0)}",
                    'impact': 'high' if github_data.get('total_repos', 0) > 5 else 'medium'
                })
        
        return insights
    
    def _generate_integration_recommendations(self) -> List[Dict[str, Any]]:
        """Generate integration recommendations"""
        recommendations = []
        
        sync_status = self.integration_manager.get_sync_status()
        
        # Check for missing integrations
        available_integrations = ['clickup', 'slack', 'github', 'google_workspace']
        enabled_integrations = [name for name, status in sync_status['integrations'].items() if status['status'] != 'error']
        
        for integration in available_integrations:
            if integration not in enabled_integrations:
                recommendations.append({
                    'type': 'integration_setup',
                    'title': f'Setup {integration.title()} Integration',
                    'description': f'Enable {integration} integration for better data synchronization',
                    'priority': 'high' if integration == 'clickup' else 'medium',
                    'action': f'Configure {integration.upper()}_API_KEY environment variable'
                })
        
        # Check for sync issues
        for name, status in sync_status['integrations'].items():
            if status['error_count'] > 3:
                recommendations.append({
                    'type': 'sync_issue',
                    'title': f'{name.title()} Sync Issues',
                    'description': f'{name} integration has {status["error_count"]} consecutive errors',
                    'priority': 'high',
                    'action': 'Check API credentials and network connectivity'
                })
        
        return recommendations
    
    async def send_team_notification(self, message: str, priority: str = 'normal') -> Dict[str, Any]:
        """Send notification to team through available integrations"""
        results = {}
        
        # Try Slack first
        if 'slack' in self.integration_manager.integrations:
            success = await self.integration_manager.send_notification('slack', message)
            results['slack'] = {'sent': success, 'priority': priority}
        
        # Could add other notification methods here (email, webhook, etc.)
        
        return results

def main():
    """Main function for testing"""
    print("🔗 ClickUp Brain Integration System")
    print("=" * 50)
    
    # Initialize integration system
    integration_system = ClickUpBrainIntegrationSystem()
    
    print("🔗 Available Integrations:")
    for name, config in integration_system.integration_manager.configs.items():
        status = "✅ Enabled" if config.enabled else "❌ Disabled"
        print(f"  • {config.service_name}: {status}")
    
    print(f"\n📊 Integration Status:")
    status = integration_system.integration_manager.get_sync_status()
    print(f"  • Total Integrations: {status['total_integrations']}")
    print(f"  • Enabled Integrations: {status['enabled_integrations']}")
    
    # Test sync if any integrations are enabled
    if status['enabled_integrations'] > 0:
        print(f"\n🔄 Testing data synchronization...")
        
        async def test_sync():
            sync_result = await integration_system.perform_full_sync()
            print(f"✅ Sync completed: {sync_result['successful_syncs']}/{sync_result['total_services']} services")
            
            # Get analytics
            analytics = integration_system.get_integration_analytics()
            print(f"\n📈 Integration Analytics:")
            print(f"  • Success Rate: {analytics['sync_history_summary']['average_success_rate']:.1%}")
            print(f"  • Data Insights: {len(analytics['data_insights'])}")
            print(f"  • Recommendations: {len(analytics['recommendations'])}")
        
        # Run async test
        asyncio.run(test_sync())
    else:
        print(f"\n⚠️ No integrations enabled. Set environment variables to enable:")
        print(f"  • CLICKUP_API_KEY for ClickUp integration")
        print(f"  • SLACK_BOT_TOKEN for Slack integration")
        print(f"  • GITHUB_ACCESS_TOKEN for GitHub integration")
        print(f"  • GOOGLE_CREDENTIALS_FILE for Google Workspace integration")

if __name__ == "__main__":
    main()








