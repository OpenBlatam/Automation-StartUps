#!/usr/bin/env python3
"""
Integration Tools for Competitive Pricing Analysis System
=========================================================

Tools for integrating the pricing analysis system with external platforms and services.

Features:
- CRM integration (Salesforce, HubSpot, Pipedrive)
- Business Intelligence tools (Tableau, Power BI, Looker)
- Ticketing systems (Jira, ServiceNow, Zendesk)
- Marketing automation (Marketo, Pardot, Mailchimp)
- ERP systems (SAP, Oracle, NetSuite)
- API connectors and webhooks
- Data synchronization tools
"""

import requests
import json
import sqlite3
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass, asdict
import logging
import yaml
import base64
import hashlib
import hmac
from abc import ABC, abstractmethod
import asyncio
import aiohttp
from concurrent.futures import ThreadPoolExecutor
import schedule
import time

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class IntegrationConfig:
    """Configuration for external system integration"""
    system_name: str
    api_endpoint: str
    api_key: str
    api_secret: Optional[str] = None
    auth_type: str = "bearer"  # bearer, basic, oauth, api_key
    rate_limit: int = 100  # requests per minute
    timeout: int = 30
    retry_attempts: int = 3
    custom_headers: Dict[str, str] = None
    webhook_url: Optional[str] = None
    sync_interval_minutes: int = 60

@dataclass
class SyncResult:
    """Result of data synchronization"""
    success: bool
    records_processed: int
    records_created: int
    records_updated: int
    records_failed: int
    error_message: Optional[str] = None
    sync_duration: float = 0.0

class BaseIntegration(ABC):
    """Base class for all integrations"""
    
    def __init__(self, config: IntegrationConfig):
        self.config = config
        self.session = requests.Session()
        self._setup_session()
    
    def _setup_session(self):
        """Setup HTTP session with authentication"""
        if self.config.auth_type == "bearer":
            self.session.headers.update({
                'Authorization': f'Bearer {self.config.api_key}',
                'Content-Type': 'application/json'
            })
        elif self.config.auth_type == "basic":
            credentials = base64.b64encode(f"{self.config.api_key}:{self.config.api_secret}".encode()).decode()
            self.session.headers.update({
                'Authorization': f'Basic {credentials}',
                'Content-Type': 'application/json'
            })
        elif self.config.auth_type == "api_key":
            self.session.headers.update({
                'X-API-Key': self.config.api_key,
                'Content-Type': 'application/json'
            })
        
        # Add custom headers
        if self.config.custom_headers:
            self.session.headers.update(self.config.custom_headers)
    
    @abstractmethod
    def test_connection(self) -> bool:
        """Test connection to external system"""
        pass
    
    @abstractmethod
    def sync_data(self, data: List[Dict[str, Any]]) -> SyncResult:
        """Sync data to external system"""
        pass
    
    @abstractmethod
    def get_data(self, filters: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        """Get data from external system"""
        pass

class SalesforceIntegration(BaseIntegration):
    """Salesforce CRM integration"""
    
    def test_connection(self) -> bool:
        """Test Salesforce connection"""
        try:
            response = self.session.get(f"{self.config.api_endpoint}/services/data/v52.0/sobjects/")
            return response.status_code == 200
        except Exception as e:
            logger.error(f"Salesforce connection test failed: {e}")
            return False
    
    def sync_data(self, data: List[Dict[str, Any]]) -> SyncResult:
        """Sync pricing data to Salesforce"""
        start_time = time.time()
        records_processed = 0
        records_created = 0
        records_updated = 0
        records_failed = 0
        
        try:
            for record in data:
                try:
                    # Map pricing data to Salesforce fields
                    sf_record = self._map_to_salesforce_fields(record)
                    
                    # Check if record exists
                    existing_record = self._find_existing_record(record)
                    
                    if existing_record:
                        # Update existing record
                        response = self.session.patch(
                            f"{self.config.api_endpoint}/services/data/v52.0/sobjects/Pricing_Data__c/{existing_record['Id']}",
                            json=sf_record
                        )
                        if response.status_code == 204:
                            records_updated += 1
                        else:
                            records_failed += 1
                    else:
                        # Create new record
                        response = self.session.post(
                            f"{self.config.api_endpoint}/services/data/v52.0/sobjects/Pricing_Data__c",
                            json=sf_record
                        )
                        if response.status_code == 201:
                            records_created += 1
                        else:
                            records_failed += 1
                    
                    records_processed += 1
                    
                except Exception as e:
                    logger.error(f"Error syncing record to Salesforce: {e}")
                    records_failed += 1
                    records_processed += 1
            
            sync_duration = time.time() - start_time
            
            return SyncResult(
                success=records_failed == 0,
                records_processed=records_processed,
                records_created=records_created,
                records_updated=records_updated,
                records_failed=records_failed,
                sync_duration=sync_duration
            )
            
        except Exception as e:
            logger.error(f"Salesforce sync failed: {e}")
            return SyncResult(
                success=False,
                records_processed=records_processed,
                records_created=records_created,
                records_updated=records_updated,
                records_failed=records_failed,
                error_message=str(e),
                sync_duration=time.time() - start_time
            )
    
    def get_data(self, filters: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        """Get data from Salesforce"""
        try:
            # Build SOQL query
            query = "SELECT Id, Name, Product__c, Competitor__c, Price__c, Currency__c, Date_Collected__c FROM Pricing_Data__c"
            
            if filters:
                where_clause = " AND ".join([f"{k} = '{v}'" for k, v in filters.items()])
                query += f" WHERE {where_clause}"
            
            response = self.session.get(
                f"{self.config.api_endpoint}/services/data/v52.0/query",
                params={'q': query}
            )
            
            if response.status_code == 200:
                data = response.json()
                return data.get('records', [])
            else:
                logger.error(f"Salesforce query failed: {response.status_code}")
                return []
                
        except Exception as e:
            logger.error(f"Error getting data from Salesforce: {e}")
            return []
    
    def _map_to_salesforce_fields(self, record: Dict[str, Any]) -> Dict[str, Any]:
        """Map pricing data to Salesforce fields"""
        return {
            'Name': f"{record.get('product_name', '')} - {record.get('competitor', '')}",
            'Product__c': record.get('product_id', ''),
            'Competitor__c': record.get('competitor', ''),
            'Price__c': record.get('price', 0),
            'Currency__c': record.get('currency', 'USD'),
            'Date_Collected__c': record.get('date_collected', datetime.now().isoformat())
        }
    
    def _find_existing_record(self, record: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Find existing record in Salesforce"""
        try:
            query = f"SELECT Id FROM Pricing_Data__c WHERE Product__c = '{record.get('product_id', '')}' AND Competitor__c = '{record.get('competitor', '')}' AND Date_Collected__c = {record.get('date_collected', '')}"
            
            response = self.session.get(
                f"{self.config.api_endpoint}/services/data/v52.0/query",
                params={'q': query}
            )
            
            if response.status_code == 200:
                data = response.json()
                records = data.get('records', [])
                return records[0] if records else None
            
            return None
            
        except Exception as e:
            logger.error(f"Error finding existing Salesforce record: {e}")
            return None

class HubSpotIntegration(BaseIntegration):
    """HubSpot CRM integration"""
    
    def test_connection(self) -> bool:
        """Test HubSpot connection"""
        try:
            response = self.session.get(f"{self.config.api_endpoint}/crm/v3/objects/contacts?limit=1")
            return response.status_code == 200
        except Exception as e:
            logger.error(f"HubSpot connection test failed: {e}")
            return False
    
    def sync_data(self, data: List[Dict[str, Any]]) -> SyncResult:
        """Sync pricing data to HubSpot"""
        start_time = time.time()
        records_processed = 0
        records_created = 0
        records_updated = 0
        records_failed = 0
        
        try:
            for record in data:
                try:
                    # Map pricing data to HubSpot properties
                    hs_record = self._map_to_hubspot_fields(record)
                    
                    # Create/update record in HubSpot
                    response = self.session.post(
                        f"{self.config.api_endpoint}/crm/v3/objects/pricing_data",
                        json=hs_record
                    )
                    
                    if response.status_code in [200, 201]:
                        records_created += 1
                    else:
                        records_failed += 1
                    
                    records_processed += 1
                    
                except Exception as e:
                    logger.error(f"Error syncing record to HubSpot: {e}")
                    records_failed += 1
                    records_processed += 1
            
            sync_duration = time.time() - start_time
            
            return SyncResult(
                success=records_failed == 0,
                records_processed=records_processed,
                records_created=records_created,
                records_updated=records_updated,
                records_failed=records_failed,
                sync_duration=sync_duration
            )
            
        except Exception as e:
            logger.error(f"HubSpot sync failed: {e}")
            return SyncResult(
                success=False,
                records_processed=records_processed,
                records_created=records_created,
                records_updated=records_updated,
                records_failed=records_failed,
                error_message=str(e),
                sync_duration=time.time() - start_time
            )
    
    def get_data(self, filters: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        """Get data from HubSpot"""
        try:
            params = {'limit': 100}
            
            if filters:
                # Build filter query for HubSpot
                filter_query = " AND ".join([f"{k} = '{v}'" for k, v in filters.items()])
                params['filter'] = filter_query
            
            response = self.session.get(
                f"{self.config.api_endpoint}/crm/v3/objects/pricing_data",
                params=params
            )
            
            if response.status_code == 200:
                data = response.json()
                return data.get('results', [])
            else:
                logger.error(f"HubSpot query failed: {response.status_code}")
                return []
                
        except Exception as e:
            logger.error(f"Error getting data from HubSpot: {e}")
            return []
    
    def _map_to_hubspot_fields(self, record: Dict[str, Any]) -> Dict[str, Any]:
        """Map pricing data to HubSpot properties"""
        return {
            'properties': {
                'product_id': record.get('product_id', ''),
                'product_name': record.get('product_name', ''),
                'competitor': record.get('competitor', ''),
                'price': str(record.get('price', 0)),
                'currency': record.get('currency', 'USD'),
                'date_collected': record.get('date_collected', datetime.now().isoformat())
            }
        }

class JiraIntegration(BaseIntegration):
    """Jira ticketing system integration"""
    
    def test_connection(self) -> bool:
        """Test Jira connection"""
        try:
            response = self.session.get(f"{self.config.api_endpoint}/rest/api/3/myself")
            return response.status_code == 200
        except Exception as e:
            logger.error(f"Jira connection test failed: {e}")
            return False
    
    def sync_data(self, data: List[Dict[str, Any]]) -> SyncResult:
        """Create Jira tickets for pricing alerts"""
        start_time = time.time()
        records_processed = 0
        records_created = 0
        records_updated = 0
        records_failed = 0
        
        try:
            for record in data:
                try:
                    # Create Jira ticket for pricing alert
                    ticket = self._create_jira_ticket(record)
                    
                    response = self.session.post(
                        f"{self.config.api_endpoint}/rest/api/3/issue",
                        json=ticket
                    )
                    
                    if response.status_code == 201:
                        records_created += 1
                    else:
                        records_failed += 1
                    
                    records_processed += 1
                    
                except Exception as e:
                    logger.error(f"Error creating Jira ticket: {e}")
                    records_failed += 1
                    records_processed += 1
            
            sync_duration = time.time() - start_time
            
            return SyncResult(
                success=records_failed == 0,
                records_processed=records_processed,
                records_created=records_created,
                records_updated=records_updated,
                records_failed=records_failed,
                sync_duration=sync_duration
            )
            
        except Exception as e:
            logger.error(f"Jira sync failed: {e}")
            return SyncResult(
                success=False,
                records_processed=records_processed,
                records_created=records_created,
                records_updated=records_updated,
                records_failed=records_failed,
                error_message=str(e),
                sync_duration=time.time() - start_time
            )
    
    def get_data(self, filters: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        """Get Jira tickets"""
        try:
            jql = "project = PRICING AND type = 'Pricing Alert'"
            
            if filters:
                jql += f" AND {filters.get('jql', '')}"
            
            response = self.session.get(
                f"{self.config.api_endpoint}/rest/api/3/search",
                params={'jql': jql, 'maxResults': 100}
            )
            
            if response.status_code == 200:
                data = response.json()
                return data.get('issues', [])
            else:
                logger.error(f"Jira query failed: {response.status_code}")
                return []
                
        except Exception as e:
            logger.error(f"Error getting data from Jira: {e}")
            return []
    
    def _create_jira_ticket(self, record: Dict[str, Any]) -> Dict[str, Any]:
        """Create Jira ticket for pricing alert"""
        return {
            'fields': {
                'project': {'key': 'PRICING'},
                'summary': f"Pricing Alert: {record.get('title', 'Unknown Alert')}",
                'description': {
                    'type': 'doc',
                    'version': 1,
                    'content': [
                        {
                            'type': 'paragraph',
                            'content': [
                                {
                                    'type': 'text',
                                    'text': record.get('message', 'No message provided')
                                }
                            ]
                        }
                    ]
                },
                'issuetype': {'name': 'Pricing Alert'},
                'priority': {'name': self._map_priority(record.get('severity', 'medium'))},
                'labels': ['pricing', 'competitive-analysis'],
                'customfield_10001': record.get('product_id', ''),  # Product ID custom field
                'customfield_10002': record.get('competitor', ''),  # Competitor custom field
            }
        }
    
    def _map_priority(self, severity: str) -> str:
        """Map alert severity to Jira priority"""
        mapping = {
            'low': 'Low',
            'medium': 'Medium',
            'high': 'High',
            'critical': 'Highest'
        }
        return mapping.get(severity.lower(), 'Medium')

class TableauIntegration(BaseIntegration):
    """Tableau Business Intelligence integration"""
    
    def test_connection(self) -> bool:
        """Test Tableau connection"""
        try:
            # Tableau REST API authentication
            auth_data = {
                'credentials': {
                    'name': self.config.api_key,
                    'password': self.config.api_secret,
                    'site': {'contentUrl': ''}
                }
            }
            
            response = self.session.post(
                f"{self.config.api_endpoint}/api/3.9/auth/signin",
                json=auth_data
            )
            
            if response.status_code == 200:
                # Store authentication token
                auth_response = response.json()
                token = auth_response['credentials']['token']
                self.session.headers.update({'X-Tableau-Auth': token})
                return True
            else:
                return False
                
        except Exception as e:
            logger.error(f"Tableau connection test failed: {e}")
            return False
    
    def sync_data(self, data: List[Dict[str, Any]]) -> SyncResult:
        """Sync pricing data to Tableau datasource"""
        start_time = time.time()
        records_processed = 0
        records_created = 0
        records_updated = 0
        records_failed = 0
        
        try:
            # Convert data to CSV format for Tableau
            csv_data = self._convert_to_csv(data)
            
            # Upload to Tableau datasource
            response = self.session.post(
                f"{self.config.api_endpoint}/api/3.9/sites/{{site_id}}/datasources/{{datasource_id}}/refresh",
                data=csv_data,
                headers={'Content-Type': 'text/csv'}
            )
            
            if response.status_code == 200:
                records_created = len(data)
                records_processed = len(data)
            else:
                records_failed = len(data)
                records_processed = len(data)
            
            sync_duration = time.time() - start_time
            
            return SyncResult(
                success=records_failed == 0,
                records_processed=records_processed,
                records_created=records_created,
                records_updated=records_updated,
                records_failed=records_failed,
                sync_duration=sync_duration
            )
            
        except Exception as e:
            logger.error(f"Tableau sync failed: {e}")
            return SyncResult(
                success=False,
                records_processed=records_processed,
                records_created=records_created,
                records_updated=records_updated,
                records_failed=records_failed,
                error_message=str(e),
                sync_duration=time.time() - start_time
            )
    
    def get_data(self, filters: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        """Get data from Tableau"""
        try:
            # This would typically involve querying a Tableau datasource
            # Implementation depends on specific Tableau setup
            return []
            
        except Exception as e:
            logger.error(f"Error getting data from Tableau: {e}")
            return []
    
    def _convert_to_csv(self, data: List[Dict[str, Any]]) -> str:
        """Convert data to CSV format"""
        if not data:
            return ""
        
        df = pd.DataFrame(data)
        return df.to_csv(index=False)

class IntegrationManager:
    """Manager for all integrations"""
    
    def __init__(self, config_file: str = "integration_config.yaml"):
        """Initialize integration manager"""
        self.config = self._load_config(config_file)
        self.integrations = {}
        self.db_path = self.config.get('database_path', 'pricing_analysis.db')
        
        # Initialize integrations
        self._initialize_integrations()
        
        logger.info("Integration Manager initialized successfully")
    
    def _load_config(self, config_file: str) -> Dict:
        """Load configuration from YAML file"""
        try:
            with open(config_file, 'r') as f:
                return yaml.safe_load(f)
        except FileNotFoundError:
            logger.warning(f"Config file {config_file} not found, using defaults")
            return self._get_default_config()
    
    def _get_default_config(self) -> Dict:
        """Get default configuration"""
        return {
            'database_path': 'pricing_analysis.db',
            'integrations': {},
            'sync_settings': {
                'enabled': True,
                'interval_minutes': 60,
                'batch_size': 100
            }
        }
    
    def _initialize_integrations(self):
        """Initialize all configured integrations"""
        integrations_config = self.config.get('integrations', {})
        
        for name, config in integrations_config.items():
            try:
                integration_config = IntegrationConfig(
                    system_name=name,
                    api_endpoint=config['api_endpoint'],
                    api_key=config['api_key'],
                    api_secret=config.get('api_secret'),
                    auth_type=config.get('auth_type', 'bearer'),
                    rate_limit=config.get('rate_limit', 100),
                    timeout=config.get('timeout', 30),
                    retry_attempts=config.get('retry_attempts', 3),
                    custom_headers=config.get('custom_headers'),
                    webhook_url=config.get('webhook_url'),
                    sync_interval_minutes=config.get('sync_interval_minutes', 60)
                )
                
                # Create appropriate integration instance
                if name.lower() == 'salesforce':
                    self.integrations[name] = SalesforceIntegration(integration_config)
                elif name.lower() == 'hubspot':
                    self.integrations[name] = HubSpotIntegration(integration_config)
                elif name.lower() == 'jira':
                    self.integrations[name] = JiraIntegration(integration_config)
                elif name.lower() == 'tableau':
                    self.integrations[name] = TableauIntegration(integration_config)
                else:
                    logger.warning(f"Unknown integration type: {name}")
                    continue
                
                logger.info(f"Initialized {name} integration")
                
            except Exception as e:
                logger.error(f"Error initializing {name} integration: {e}")
    
    def test_all_connections(self) -> Dict[str, bool]:
        """Test connections to all integrations"""
        results = {}
        
        for name, integration in self.integrations.items():
            try:
                results[name] = integration.test_connection()
                logger.info(f"{name} connection: {'✓' if results[name] else '✗'}")
            except Exception as e:
                logger.error(f"Error testing {name} connection: {e}")
                results[name] = False
        
        return results
    
    def sync_pricing_data(self, integration_name: str = None) -> Dict[str, SyncResult]:
        """Sync pricing data to integrations"""
        results = {}
        
        # Get pricing data from database
        pricing_data = self._get_pricing_data()
        
        if not pricing_data:
            logger.warning("No pricing data to sync")
            return results
        
        # Sync to specific integration or all integrations
        integrations_to_sync = [integration_name] if integration_name else list(self.integrations.keys())
        
        for name in integrations_to_sync:
            if name not in self.integrations:
                logger.warning(f"Integration {name} not found")
                continue
            
            try:
                integration = self.integrations[name]
                result = integration.sync_data(pricing_data)
                results[name] = result
                
                logger.info(f"{name} sync: {result.records_processed} processed, "
                           f"{result.records_created} created, {result.records_failed} failed")
                
            except Exception as e:
                logger.error(f"Error syncing to {name}: {e}")
                results[name] = SyncResult(
                    success=False,
                    records_processed=0,
                    records_created=0,
                    records_updated=0,
                    records_failed=len(pricing_data),
                    error_message=str(e)
                )
        
        return results
    
    def sync_alerts(self, integration_name: str = None) -> Dict[str, SyncResult]:
        """Sync pricing alerts to integrations"""
        results = {}
        
        # Get recent alerts from database
        alerts = self._get_recent_alerts()
        
        if not alerts:
            logger.info("No recent alerts to sync")
            return results
        
        # Sync to specific integration or all integrations
        integrations_to_sync = [integration_name] if integration_name else list(self.integrations.keys())
        
        for name in integrations_to_sync:
            if name not in self.integrations:
                logger.warning(f"Integration {name} not found")
                continue
            
            try:
                integration = self.integrations[name]
                result = integration.sync_data(alerts)
                results[name] = result
                
                logger.info(f"{name} alerts sync: {result.records_processed} processed, "
                           f"{result.records_created} created, {result.records_failed} failed")
                
            except Exception as e:
                logger.error(f"Error syncing alerts to {name}: {e}")
                results[name] = SyncResult(
                    success=False,
                    records_processed=0,
                    records_created=0,
                    records_updated=0,
                    records_failed=len(alerts),
                    error_message=str(e)
                )
        
        return results
    
    def _get_pricing_data(self, limit: int = 1000) -> List[Dict[str, Any]]:
        """Get pricing data from database"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT 
                    product_id,
                    product_name,
                    competitor,
                    price,
                    currency,
                    date_collected,
                    source
                FROM pricing_data
                WHERE date_collected >= date('now', '-7 days')
                ORDER BY date_collected DESC
                LIMIT ?
            ''', (limit,))
            
            rows = cursor.fetchall()
            conn.close()
            
            data = []
            for row in rows:
                data.append({
                    'product_id': row[0],
                    'product_name': row[1],
                    'competitor': row[2],
                    'price': row[3],
                    'currency': row[4],
                    'date_collected': row[5],
                    'source': row[6]
                })
            
            return data
            
        except Exception as e:
            logger.error(f"Error getting pricing data: {e}")
            return []
    
    def _get_recent_alerts(self, limit: int = 100) -> List[Dict[str, Any]]:
        """Get recent alerts from database"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT 
                    alert_id,
                    rule_id,
                    alert_type,
                    severity,
                    title,
                    message,
                    product_id,
                    competitor,
                    price_data,
                    created_at
                FROM alerts
                WHERE created_at >= date('now', '-1 day')
                ORDER BY created_at DESC
                LIMIT ?
            ''', (limit,))
            
            rows = cursor.fetchall()
            conn.close()
            
            data = []
            for row in rows:
                data.append({
                    'alert_id': row[0],
                    'rule_id': row[1],
                    'alert_type': row[2],
                    'severity': row[3],
                    'title': row[4],
                    'message': row[5],
                    'product_id': row[6],
                    'competitor': row[7],
                    'price_data': json.loads(row[8]) if row[8] else None,
                    'created_at': row[9]
                })
            
            return data
            
        except Exception as e:
            logger.error(f"Error getting recent alerts: {e}")
            return []
    
    def start_scheduled_sync(self):
        """Start scheduled synchronization"""
        sync_settings = self.config.get('sync_settings', {})
        
        if not sync_settings.get('enabled', True):
            logger.info("Scheduled sync is disabled")
            return
        
        interval_minutes = sync_settings.get('interval_minutes', 60)
        
        # Schedule pricing data sync
        schedule.every(interval_minutes).minutes.do(self.sync_pricing_data)
        
        # Schedule alerts sync
        schedule.every(interval_minutes).minutes.do(self.sync_alerts)
        
        logger.info(f"Started scheduled sync every {interval_minutes} minutes")
        
        # Run scheduler
        while True:
            schedule.run_pending()
            time.sleep(60)  # Check every minute
    
    def send_webhook_notification(self, event_type: str, data: Dict[str, Any]):
        """Send webhook notification for events"""
        try:
            webhook_config = self.config.get('webhook', {})
            
            if not webhook_config.get('url'):
                logger.warning("Webhook URL not configured")
                return
            
            payload = {
                'event_type': event_type,
                'timestamp': datetime.now().isoformat(),
                'data': data
            }
            
            # Add signature for security
            if webhook_config.get('secret'):
                signature = hmac.new(
                    webhook_config['secret'].encode(),
                    json.dumps(payload).encode(),
                    hashlib.sha256
                ).hexdigest()
                headers = {'X-Signature': f'sha256={signature}'}
            else:
                headers = {}
            
            response = requests.post(
                webhook_config['url'],
                json=payload,
                headers=headers,
                timeout=30
            )
            
            response.raise_for_status()
            logger.info(f"Webhook notification sent for {event_type}")
            
        except Exception as e:
            logger.error(f"Error sending webhook notification: {e}")

def main():
    """Main function to demonstrate integration tools"""
    # Initialize integration manager
    manager = IntegrationManager()
    
    # Test all connections
    print("Testing integrations...")
    connection_results = manager.test_all_connections()
    
    for name, success in connection_results.items():
        print(f"{name}: {'✓ Connected' if success else '✗ Failed'}")
    
    # Sync pricing data
    print("\nSyncing pricing data...")
    sync_results = manager.sync_pricing_data()
    
    for name, result in sync_results.items():
        print(f"{name}: {result.records_processed} processed, "
              f"{result.records_created} created, {result.records_failed} failed")
    
    # Sync alerts
    print("\nSyncing alerts...")
    alert_results = manager.sync_alerts()
    
    for name, result in alert_results.items():
        print(f"{name}: {result.records_processed} processed, "
              f"{result.records_created} created, {result.records_failed} failed")

if __name__ == "__main__":
    main()






