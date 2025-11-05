#!/usr/bin/env python3
"""
ClickUp Brain Connectors
========================

Pre-built connectors for popular services and platforms.
"""

import asyncio
import json
import aiohttp
from typing import Any, Dict, List, Optional, Union
from dataclasses import dataclass
from datetime import datetime, timedelta
from pathlib import Path
import logging
from enum import Enum
import base64
import hashlib
import hmac
from urllib.parse import urlencode, parse_qs
import xml.etree.ElementTree as ET

ROOT = Path(__file__).parent

class ConnectorType(Enum):
    """Connector types."""
    CLICKUP = "clickup"
    SLACK = "slack"
    GITHUB = "github"
    GOOGLE_WORKSPACE = "google_workspace"
    MICROSOFT_365 = "microsoft_365"
    SALESFORCE = "salesforce"
    HUBSPOT = "hubspot"
    ZAPIER = "zapier"
    TRELLO = "trello"
    ASANA = "asana"
    JIRA = "jira"
    CONFLUENCE = "confluence"
    NOTION = "notion"
    AIRTABLE = "airtable"
    MAILCHIMP = "mailchimp"
    STRIPE = "stripe"
    PAYPAL = "paypal"
    SHOPIFY = "shopify"
    WOOCOMMERCE = "woocommerce"
    WORDPRESS = "wordpress"
    DISCORD = "discord"
    TELEGRAM = "telegram"
    TWITTER = "twitter"
    FACEBOOK = "facebook"
    INSTAGRAM = "instagram"
    LINKEDIN = "linkedin"
    YOUTUBE = "youtube"
    TIKTOK = "tiktok"
    SPOTIFY = "spotify"
    DROPBOX = "dropbox"
    GOOGLE_DRIVE = "google_drive"
    ONEDRIVE = "onedrive"
    AWS_S3 = "aws_s3"
    AZURE_BLOB = "azure_blob"
    GCP_STORAGE = "gcp_storage"
    MYSQL = "mysql"
    POSTGRESQL = "postgresql"
    MONGODB = "mongodb"
    REDIS = "redis"
    ELASTICSEARCH = "elasticsearch"
    KAFKA = "kafka"
    RABBITMQ = "rabbitmq"
    SENDGRID = "sendgrid"
    TWILIO = "twilio"
    PUSHER = "pusher"
    FIREBASE = "firebase"
    HEROKU = "heroku"
    VERCEL = "vercel"
    NETLIFY = "netlify"
    DIGITAL_OCEAN = "digital_ocean"
    AWS = "aws"
    AZURE = "azure"
    GCP = "gcp"

@dataclass
class ConnectorConfig:
    """Connector configuration."""
    name: str
    type: ConnectorType
    api_key: Optional[str] = None
    api_secret: Optional[str] = None
    access_token: Optional[str] = None
    refresh_token: Optional[str] = None
    base_url: Optional[str] = None
    webhook_url: Optional[str] = None
    credentials: Dict[str, str] = None
    headers: Dict[str, str] = None
    timeout: int = 30
    rate_limit: int = 100
    retry_count: int = 3
    retry_delay: float = 1.0
    enabled: bool = True
    metadata: Dict[str, Any] = None

    def __post_init__(self):
        if self.credentials is None:
            self.credentials = {}
        if self.headers is None:
            self.headers = {}
        if self.metadata is None:
            self.metadata = {}

class BaseConnector:
    """Base connector class."""
    
    def __init__(self, config: ConnectorConfig):
        self.config = config
        self.logger = logging.getLogger(f"connector_{config.name}")
        self._session: Optional[aiohttp.ClientSession] = None
        self._rate_limiter = asyncio.Semaphore(config.rate_limit)
    
    async def connect(self) -> bool:
        """Establish connection."""
        try:
            self._session = aiohttp.ClientSession(
                timeout=aiohttp.ClientTimeout(total=self.config.timeout),
                headers=self._get_headers()
            )
            
            # Test connection
            await self._test_connection()
            self.logger.info(f"Connected to {self.config.name}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to connect to {self.config.name}: {e}")
            return False
    
    async def disconnect(self) -> None:
        """Close connection."""
        if self._session:
            await self._session.close()
            self._session = None
        self.logger.info(f"Disconnected from {self.config.name}")
    
    def _get_headers(self) -> Dict[str, str]:
        """Get request headers."""
        headers = self.config.headers.copy()
        
        if self.config.access_token:
            headers["Authorization"] = f"Bearer {self.config.access_token}"
        elif self.config.api_key:
            headers["X-API-Key"] = self.config.api_key
        
        return headers
    
    async def _test_connection(self) -> None:
        """Test connection to service."""
        if not self._session:
            raise ConnectionError("Session not initialized")
        
        # Default test - try to get user info or health check
        test_url = self._get_test_url()
        if test_url:
            async with self._session.get(test_url) as response:
                if response.status >= 400:
                    raise ConnectionError(f"Connection test failed with status {response.status}")
    
    def _get_test_url(self) -> Optional[str]:
        """Get test URL for connection testing."""
        return None
    
    async def _make_request(self, method: str, url: str, **kwargs) -> aiohttp.ClientResponse:
        """Make rate-limited request."""
        async with self._rate_limiter:
            if not self._session:
                raise ConnectionError("Session not initialized")
            
            return await self._session.request(method, url, **kwargs)

class ClickUpConnector(BaseConnector):
    """ClickUp API connector."""
    
    def __init__(self, config: ConnectorConfig):
        super().__init__(config)
        if not self.config.base_url:
            self.config.base_url = "https://api.clickup.com/api/v2"
    
    def _get_test_url(self) -> str:
        return f"{self.config.base_url}/user"
    
    async def get_teams(self) -> List[Dict[str, Any]]:
        """Get all teams."""
        async with self._make_request("GET", f"{self.config.base_url}/team") as response:
            if response.status == 200:
                data = await response.json()
                return data.get("teams", [])
            else:
                raise Exception(f"Failed to get teams: {response.status}")
    
    async def get_spaces(self, team_id: str) -> List[Dict[str, Any]]:
        """Get spaces for team."""
        async with self._make_request("GET", f"{self.config.base_url}/team/{team_id}/space") as response:
            if response.status == 200:
                data = await response.json()
                return data.get("spaces", [])
            else:
                raise Exception(f"Failed to get spaces: {response.status}")
    
    async def get_folders(self, space_id: str) -> List[Dict[str, Any]]:
        """Get folders for space."""
        async with self._make_request("GET", f"{self.config.base_url}/space/{space_id}/folder") as response:
            if response.status == 200:
                data = await response.json()
                return data.get("folders", [])
            else:
                raise Exception(f"Failed to get folders: {response.status}")
    
    async def get_lists(self, folder_id: str) -> List[Dict[str, Any]]:
        """Get lists for folder."""
        async with self._make_request("GET", f"{self.config.base_url}/folder/{folder_id}/list") as response:
            if response.status == 200:
                data = await response.json()
                return data.get("lists", [])
            else:
                raise Exception(f"Failed to get lists: {response.status}")
    
    async def get_tasks(self, list_id: str, include_closed: bool = False) -> List[Dict[str, Any]]:
        """Get tasks for list."""
        params = {"include_closed": str(include_closed).lower()}
        url = f"{self.config.base_url}/list/{list_id}/task?{urlencode(params)}"
        
        async with self._make_request("GET", url) as response:
            if response.status == 200:
                data = await response.json()
                return data.get("tasks", [])
            else:
                raise Exception(f"Failed to get tasks: {response.status}")
    
    async def create_task(self, list_id: str, task_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create new task."""
        async with self._make_request("POST", f"{self.config.base_url}/list/{list_id}/task", json=task_data) as response:
            if response.status == 201:
                return await response.json()
            else:
                raise Exception(f"Failed to create task: {response.status}")
    
    async def update_task(self, task_id: str, task_data: Dict[str, Any]) -> Dict[str, Any]:
        """Update task."""
        async with self._make_request("PUT", f"{self.config.base_url}/task/{task_id}", json=task_data) as response:
            if response.status == 200:
                return await response.json()
            else:
                raise Exception(f"Failed to update task: {response.status}")

class SlackConnector(BaseConnector):
    """Slack API connector."""
    
    def __init__(self, config: ConnectorConfig):
        super().__init__(config)
        if not self.config.base_url:
            self.config.base_url = "https://slack.com/api"
    
    def _get_test_url(self) -> str:
        return f"{self.config.base_url}/auth.test"
    
    async def get_channels(self) -> List[Dict[str, Any]]:
        """Get all channels."""
        async with self._make_request("GET", f"{self.config.base_url}/conversations.list") as response:
            if response.status == 200:
                data = await response.json()
                return data.get("channels", [])
            else:
                raise Exception(f"Failed to get channels: {response.status}")
    
    async def send_message(self, channel: str, text: str, blocks: List[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Send message to channel."""
        payload = {
            "channel": channel,
            "text": text
        }
        
        if blocks:
            payload["blocks"] = blocks
        
        async with self._make_request("POST", f"{self.config.base_url}/chat.postMessage", json=payload) as response:
            if response.status == 200:
                data = await response.json()
                if data.get("ok"):
                    return data
                else:
                    raise Exception(f"Slack API error: {data.get('error')}")
            else:
                raise Exception(f"Failed to send message: {response.status}")
    
    async def get_messages(self, channel: str, limit: int = 100) -> List[Dict[str, Any]]:
        """Get messages from channel."""
        params = {"channel": channel, "limit": limit}
        url = f"{self.config.base_url}/conversations.history?{urlencode(params)}"
        
        async with self._make_request("GET", url) as response:
            if response.status == 200:
                data = await response.json()
                return data.get("messages", [])
            else:
                raise Exception(f"Failed to get messages: {response.status}")

class GitHubConnector(BaseConnector):
    """GitHub API connector."""
    
    def __init__(self, config: ConnectorConfig):
        super().__init__(config)
        if not self.config.base_url:
            self.config.base_url = "https://api.github.com"
    
    def _get_test_url(self) -> str:
        return f"{self.config.base_url}/user"
    
    async def get_repositories(self, username: str = None) -> List[Dict[str, Any]]:
        """Get repositories."""
        if username:
            url = f"{self.config.base_url}/users/{username}/repos"
        else:
            url = f"{self.config.base_url}/user/repos"
        
        async with self._make_request("GET", url) as response:
            if response.status == 200:
                return await response.json()
            else:
                raise Exception(f"Failed to get repositories: {response.status}")
    
    async def get_issues(self, owner: str, repo: str, state: str = "open") -> List[Dict[str, Any]]:
        """Get issues for repository."""
        params = {"state": state}
        url = f"{self.config.base_url}/repos/{owner}/{repo}/issues?{urlencode(params)}"
        
        async with self._make_request("GET", url) as response:
            if response.status == 200:
                return await response.json()
            else:
                raise Exception(f"Failed to get issues: {response.status}")
    
    async def create_issue(self, owner: str, repo: str, title: str, body: str = None, labels: List[str] = None) -> Dict[str, Any]:
        """Create new issue."""
        payload = {"title": title}
        
        if body:
            payload["body"] = body
        if labels:
            payload["labels"] = labels
        
        async with self._make_request("POST", f"{self.config.base_url}/repos/{owner}/{repo}/issues", json=payload) as response:
            if response.status == 201:
                return await response.json()
            else:
                raise Exception(f"Failed to create issue: {response.status}")
    
    async def get_pull_requests(self, owner: str, repo: str, state: str = "open") -> List[Dict[str, Any]]:
        """Get pull requests for repository."""
        params = {"state": state}
        url = f"{self.config.base_url}/repos/{owner}/{repo}/pulls?{urlencode(params)}"
        
        async with self._make_request("GET", url) as response:
            if response.status == 200:
                return await response.json()
            else:
                raise Exception(f"Failed to get pull requests: {response.status}")

class GoogleWorkspaceConnector(BaseConnector):
    """Google Workspace API connector."""
    
    def __init__(self, config: ConnectorConfig):
        super().__init__(config)
        if not self.config.base_url:
            self.config.base_url = "https://www.googleapis.com"
    
    def _get_test_url(self) -> str:
        return f"{self.config.base_url}/oauth2/v1/userinfo"
    
    async def get_gmail_messages(self, query: str = None, max_results: int = 10) -> List[Dict[str, Any]]:
        """Get Gmail messages."""
        params = {"maxResults": max_results}
        if query:
            params["q"] = query
        
        url = f"{self.config.base_url}/gmail/v1/users/me/messages?{urlencode(params)}"
        
        async with self._make_request("GET", url) as response:
            if response.status == 200:
                data = await response.json()
                return data.get("messages", [])
            else:
                raise Exception(f"Failed to get Gmail messages: {response.status}")
    
    async def get_calendar_events(self, calendar_id: str = "primary", time_min: str = None, time_max: str = None) -> List[Dict[str, Any]]:
        """Get calendar events."""
        params = {}
        if time_min:
            params["timeMin"] = time_min
        if time_max:
            params["timeMax"] = time_max
        
        url = f"{self.config.base_url}/calendar/v3/calendars/{calendar_id}/events?{urlencode(params)}"
        
        async with self._make_request("GET", url) as response:
            if response.status == 200:
                data = await response.json()
                return data.get("items", [])
            else:
                raise Exception(f"Failed to get calendar events: {response.status}")
    
    async def get_drive_files(self, query: str = None, page_size: int = 10) -> List[Dict[str, Any]]:
        """Get Google Drive files."""
        params = {"pageSize": page_size}
        if query:
            params["q"] = query
        
        url = f"{self.config.base_url}/drive/v3/files?{urlencode(params)}"
        
        async with self._make_request("GET", url) as response:
            if response.status == 200:
                data = await response.json()
                return data.get("files", [])
            else:
                raise Exception(f"Failed to get Drive files: {response.status}")

class SalesforceConnector(BaseConnector):
    """Salesforce API connector."""
    
    def __init__(self, config: ConnectorConfig):
        super().__init__(config)
        if not self.config.base_url:
            self.config.base_url = "https://your-instance.salesforce.com"
    
    def _get_test_url(self) -> str:
        return f"{self.config.base_url}/services/data/v52.0/sobjects"
    
    async def query(self, soql: str) -> List[Dict[str, Any]]:
        """Execute SOQL query."""
        params = {"q": soql}
        url = f"{self.config.base_url}/services/data/v52.0/query?{urlencode(params)}"
        
        async with self._make_request("GET", url) as response:
            if response.status == 200:
                data = await response.json()
                return data.get("records", [])
            else:
                raise Exception(f"Failed to execute query: {response.status}")
    
    async def get_sobject_describe(self, sobject_name: str) -> Dict[str, Any]:
        """Get SObject describe information."""
        async with self._make_request("GET", f"{self.config.base_url}/services/data/v52.0/sobjects/{sobject_name}/describe") as response:
            if response.status == 200:
                return await response.json()
            else:
                raise Exception(f"Failed to get SObject describe: {response.status}")
    
    async def create_record(self, sobject_name: str, record_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create new record."""
        async with self._make_request("POST", f"{self.config.base_url}/services/data/v52.0/sobjects/{sobject_name}", json=record_data) as response:
            if response.status == 201:
                return await response.json()
            else:
                raise Exception(f"Failed to create record: {response.status}")

class StripeConnector(BaseConnector):
    """Stripe API connector."""
    
    def __init__(self, config: ConnectorConfig):
        super().__init__(config)
        if not self.config.base_url:
            self.config.base_url = "https://api.stripe.com/v1"
    
    def _get_headers(self) -> Dict[str, str]:
        """Get Stripe-specific headers."""
        headers = self.config.headers.copy()
        if self.config.api_key:
            headers["Authorization"] = f"Bearer {self.config.api_key}"
        return headers
    
    def _get_test_url(self) -> str:
        return f"{self.config.base_url}/account"
    
    async def get_customers(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get customers."""
        params = {"limit": limit}
        url = f"{self.config.base_url}/customers?{urlencode(params)}"
        
        async with self._make_request("GET", url) as response:
            if response.status == 200:
                data = await response.json()
                return data.get("data", [])
            else:
                raise Exception(f"Failed to get customers: {response.status}")
    
    async def create_customer(self, email: str, name: str = None, metadata: Dict[str, str] = None) -> Dict[str, Any]:
        """Create new customer."""
        payload = {"email": email}
        
        if name:
            payload["name"] = name
        if metadata:
            payload["metadata"] = metadata
        
        async with self._make_request("POST", f"{self.config.base_url}/customers", data=payload) as response:
            if response.status == 200:
                return await response.json()
            else:
                raise Exception(f"Failed to create customer: {response.status}")
    
    async def get_charges(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get charges."""
        params = {"limit": limit}
        url = f"{self.config.base_url}/charges?{urlencode(params)}"
        
        async with self._make_request("GET", url) as response:
            if response.status == 200:
                data = await response.json()
                return data.get("data", [])
            else:
                raise Exception(f"Failed to get charges: {response.status}")

class ConnectorFactory:
    """Factory for creating connectors."""
    
    @staticmethod
    def create_connector(config: ConnectorConfig) -> BaseConnector:
        """Create connector based on type."""
        if config.type == ConnectorType.CLICKUP:
            return ClickUpConnector(config)
        elif config.type == ConnectorType.SLACK:
            return SlackConnector(config)
        elif config.type == ConnectorType.GITHUB:
            return GitHubConnector(config)
        elif config.type == ConnectorType.GOOGLE_WORKSPACE:
            return GoogleWorkspaceConnector(config)
        elif config.type == ConnectorType.SALESFORCE:
            return SalesforceConnector(config)
        elif config.type == ConnectorType.STRIPE:
            return StripeConnector(config)
        else:
            raise ValueError(f"Unsupported connector type: {config.type}")

# Global connector registry
connector_registry: Dict[str, BaseConnector] = {}

async def register_connector(config: ConnectorConfig) -> BaseConnector:
    """Register and connect to service."""
    connector = ConnectorFactory.create_connector(config)
    
    connected = await connector.connect()
    if not connected:
        raise ConnectionError(f"Failed to connect to {config.name}")
    
    connector_registry[config.name] = connector
    return connector

async def get_connector(name: str) -> Optional[BaseConnector]:
    """Get registered connector."""
    return connector_registry.get(name)

async def disconnect_all_connectors() -> None:
    """Disconnect all registered connectors."""
    for connector in connector_registry.values():
        try:
            await connector.disconnect()
        except Exception as e:
            logging.error(f"Error disconnecting connector: {e}")
    
    connector_registry.clear()

if __name__ == "__main__":
    # Demo connectors
    print("ClickUp Brain Connectors Demo")
    print("=" * 50)
    
    # Setup logging
    logging.basicConfig(level=logging.INFO)
    
    async def demo():
        # Demo ClickUp connector (would need real API key)
        clickup_config = ConnectorConfig(
            name="clickup_demo",
            type=ConnectorType.CLICKUP,
            api_key="your_clickup_api_key_here"
        )
        
        try:
            clickup_connector = await register_connector(clickup_config)
            print("ClickUp connector registered successfully")
            
            # Get teams (would work with real API key)
            # teams = await clickup_connector.get_teams()
            # print(f"Found {len(teams)} teams")
            
        except Exception as e:
            print(f"ClickUp connector demo failed: {e}")
        
        # Demo GitHub connector (public API, no auth needed for basic requests)
        github_config = ConnectorConfig(
            name="github_demo",
            type=ConnectorType.GITHUB,
            base_url="https://api.github.com"
        )
        
        try:
            github_connector = await register_connector(github_config)
            print("GitHub connector registered successfully")
            
            # Get repositories (public data)
            repos = await github_connector.get_repositories("octocat")
            print(f"Found {len(repos)} repositories for octocat")
            
            if repos:
                repo = repos[0]
                print(f"First repo: {repo['name']} - {repo['description']}")
            
        except Exception as e:
            print(f"GitHub connector demo failed: {e}")
        
        # Disconnect all
        await disconnect_all_connectors()
        print("\nConnectors demo completed!")
    
    asyncio.run(demo())









