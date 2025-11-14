#!/usr/bin/env python3
"""
Advanced Integration System for Affiliate Marketing
==================================================

This module provides comprehensive integration capabilities for affiliate marketing,
including API management, webhook handling, and third-party service integration.

Author: AI Marketing System
Version: 2.0
"""

import asyncio
import aiohttp
import json
import hashlib
import hmac
import time
from typing import Dict, List, Optional, Tuple, Any, Callable
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
from enum import Enum
import logging
import requests
from urllib.parse import urlencode, urlparse
import jwt
from cryptography.fernet import Fernet
import base64
import uuid
import websockets
import ssl
import certifi
import pandas as pd
import numpy as np
from concurrent.futures import ThreadPoolExecutor
import threading
import queue
import warnings
warnings.filterwarnings('ignore')

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class IntegrationType(Enum):
    """Types of integrations"""
    API = "api"
    WEBHOOK = "webhook"
    WEBSOCKET = "websocket"
    DATABASE = "database"
    FILE = "file"
    EMAIL = "email"
    SMS = "sms"
    SOCIAL_MEDIA = "social_media"

class IntegrationStatus(Enum):
    """Integration status"""
    ACTIVE = "active"
    INACTIVE = "inactive"
    ERROR = "error"
    PENDING = "pending"
    CONFIGURING = "configuring"

@dataclass
class IntegrationConfig:
    """Integration configuration"""
    integration_id: str
    name: str
    integration_type: IntegrationType
    endpoint: str
    credentials: Dict[str, str]
    headers: Dict[str, str]
    parameters: Dict[str, Any]
    status: IntegrationStatus
    created_at: datetime
    updated_at: datetime

@dataclass
class WebhookEvent:
    """Webhook event data structure"""
    event_id: str
    integration_id: str
    event_type: str
    payload: Dict[str, Any]
    timestamp: datetime
    signature: str
    processed: bool
    retry_count: int

@dataclass
class APICall:
    """API call data structure"""
    call_id: str
    integration_id: str
    method: str
    endpoint: str
    headers: Dict[str, str]
    payload: Dict[str, Any]
    response: Dict[str, Any]
    status_code: int
    duration: float
    timestamp: datetime
    success: bool

class AdvancedIntegrationSystem:
    """
    Advanced Integration System for Affiliate Marketing
    """
    
    def __init__(self):
        self.integrations = {}
        self.webhook_events = []
        self.api_calls = []
        self.event_handlers = {}
        self.rate_limits = {}
        self.encryption_key = Fernet.generate_key()
        self.cipher_suite = Fernet(self.encryption_key)
        
        # Initialize thread pool for async operations
        self.executor = ThreadPoolExecutor(max_workers=10)
        
        # Initialize event queue
        self.event_queue = queue.Queue()
        
        # Start event processor
        self.event_processor_thread = threading.Thread(target=self._process_events, daemon=True)
        self.event_processor_thread.start()
    
    def create_integration(self, name: str, integration_type: IntegrationType, 
                          endpoint: str, credentials: Dict[str, str] = None,
                          headers: Dict[str, str] = None, parameters: Dict[str, Any] = None) -> IntegrationConfig:
        """
        Create new integration
        """
        integration_id = f"int_{uuid.uuid4().hex[:8]}"
        
        # Encrypt credentials
        encrypted_credentials = self._encrypt_credentials(credentials or {})
        
        config = IntegrationConfig(
            integration_id=integration_id,
            name=name,
            integration_type=integration_type,
            endpoint=endpoint,
            credentials=encrypted_credentials,
            headers=headers or {},
            parameters=parameters or {},
            status=IntegrationStatus.PENDING,
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        
        self.integrations[integration_id] = config
        
        # Test integration
        if self._test_integration(config):
            config.status = IntegrationStatus.ACTIVE
        else:
            config.status = IntegrationStatus.ERROR
        
        config.updated_at = datetime.now()
        
        logger.info(f"Created integration: {name} ({integration_id})")
        return config
    
    def _encrypt_credentials(self, credentials: Dict[str, str]) -> Dict[str, str]:
        """
        Encrypt credentials
        """
        encrypted = {}
        for key, value in credentials.items():
            if value:
                encrypted_value = self.cipher_suite.encrypt(value.encode())
                encrypted[key] = base64.b64encode(encrypted_value).decode()
        return encrypted
    
    def _decrypt_credentials(self, encrypted_credentials: Dict[str, str]) -> Dict[str, str]:
        """
        Decrypt credentials
        """
        decrypted = {}
        for key, value in encrypted_credentials.items():
            if value:
                encrypted_value = base64.b64decode(value.encode())
                decrypted_value = self.cipher_suite.decrypt(encrypted_value)
                decrypted[key] = decrypted_value.decode()
        return decrypted
    
    def _test_integration(self, config: IntegrationConfig) -> bool:
        """
        Test integration connectivity
        """
        try:
            if config.integration_type == IntegrationType.API:
                return self._test_api_integration(config)
            elif config.integration_type == IntegrationType.WEBHOOK:
                return self._test_webhook_integration(config)
            elif config.integration_type == IntegrationType.WEBSOCKET:
                return self._test_websocket_integration(config)
            else:
                return True  # Assume other types are valid
        except Exception as e:
            logger.error(f"Integration test failed: {str(e)}")
            return False
    
    def _test_api_integration(self, config: IntegrationConfig) -> bool:
        """
        Test API integration
        """
        try:
            # Decrypt credentials
            credentials = self._decrypt_credentials(config.credentials)
            
            # Prepare headers
            headers = config.headers.copy()
            if 'api_key' in credentials:
                headers['Authorization'] = f"Bearer {credentials['api_key']}"
            elif 'username' in credentials and 'password' in credentials:
                auth_string = f"{credentials['username']}:{credentials['password']}"
                auth_bytes = auth_string.encode('ascii')
                auth_b64 = base64.b64encode(auth_bytes).decode('ascii')
                headers['Authorization'] = f"Basic {auth_b64}"
            
            # Make test request
            response = requests.get(
                config.endpoint,
                headers=headers,
                timeout=10
            )
            
            return response.status_code < 400
            
        except Exception as e:
            logger.error(f"API integration test failed: {str(e)}")
            return False
    
    def _test_webhook_integration(self, config: IntegrationConfig) -> bool:
        """
        Test webhook integration
        """
        try:
            # Test webhook endpoint accessibility
            response = requests.get(config.endpoint, timeout=10)
            return response.status_code < 400
        except Exception as e:
            logger.error(f"Webhook integration test failed: {str(e)}")
            return False
    
    def _test_websocket_integration(self, config: IntegrationConfig) -> bool:
        """
        Test websocket integration
        """
        try:
            # Test websocket connection
            async def test_connection():
                async with websockets.connect(config.endpoint) as websocket:
                    await websocket.ping()
                    return True
            
            # Run async test
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            result = loop.run_until_complete(test_connection())
            loop.close()
            
            return result
            
        except Exception as e:
            logger.error(f"Websocket integration test failed: {str(e)}")
            return False
    
    def make_api_call(self, integration_id: str, method: str, endpoint: str,
                     payload: Dict[str, Any] = None, headers: Dict[str, str] = None) -> APICall:
        """
        Make API call through integration
        """
        if integration_id not in self.integrations:
            raise ValueError(f"Integration {integration_id} not found")
        
        config = self.integrations[integration_id]
        
        if config.status != IntegrationStatus.ACTIVE:
            raise ValueError(f"Integration {integration_id} is not active")
        
        # Check rate limits
        if not self._check_rate_limit(integration_id):
            raise ValueError(f"Rate limit exceeded for integration {integration_id}")
        
        # Prepare request
        full_url = f"{config.endpoint.rstrip('/')}/{endpoint.lstrip('/')}"
        request_headers = config.headers.copy()
        if headers:
            request_headers.update(headers)
        
        # Add authentication
        credentials = self._decrypt_credentials(config.credentials)
        if 'api_key' in credentials:
            request_headers['Authorization'] = f"Bearer {credentials['api_key']}"
        elif 'username' in credentials and 'password' in credentials:
            auth_string = f"{credentials['username']}:{credentials['password']}"
            auth_bytes = auth_string.encode('ascii')
            auth_b64 = base64.b64encode(auth_bytes).decode('ascii')
            request_headers['Authorization'] = f"Basic {auth_b64}"
        
        # Make API call
        call_id = f"call_{uuid.uuid4().hex[:8]}"
        start_time = time.time()
        
        try:
            if method.upper() == 'GET':
                response = requests.get(full_url, headers=request_headers, timeout=30)
            elif method.upper() == 'POST':
                response = requests.post(full_url, headers=request_headers, json=payload, timeout=30)
            elif method.upper() == 'PUT':
                response = requests.put(full_url, headers=request_headers, json=payload, timeout=30)
            elif method.upper() == 'DELETE':
                response = requests.delete(full_url, headers=request_headers, timeout=30)
            else:
                raise ValueError(f"Unsupported HTTP method: {method}")
            
            duration = time.time() - start_time
            
            # Create API call record
            api_call = APICall(
                call_id=call_id,
                integration_id=integration_id,
                method=method.upper(),
                endpoint=endpoint,
                headers=request_headers,
                payload=payload or {},
                response=response.json() if response.content else {},
                status_code=response.status_code,
                duration=duration,
                timestamp=datetime.now(),
                success=response.status_code < 400
            )
            
            self.api_calls.append(api_call)
            
            # Update rate limit
            self._update_rate_limit(integration_id)
            
            logger.info(f"API call completed: {method} {endpoint} - {response.status_code}")
            return api_call
            
        except Exception as e:
            duration = time.time() - start_time
            
            # Create failed API call record
            api_call = APICall(
                call_id=call_id,
                integration_id=integration_id,
                method=method.upper(),
                endpoint=endpoint,
                headers=request_headers,
                payload=payload or {},
                response={'error': str(e)},
                status_code=0,
                duration=duration,
                timestamp=datetime.now(),
                success=False
            )
            
            self.api_calls.append(api_call)
            
            logger.error(f"API call failed: {method} {endpoint} - {str(e)}")
            raise
    
    def _check_rate_limit(self, integration_id: str) -> bool:
        """
        Check rate limit for integration
        """
        if integration_id not in self.rate_limits:
            self.rate_limits[integration_id] = {
                'calls': 0,
                'window_start': time.time(),
                'max_calls': 100,  # Default rate limit
                'window_duration': 3600  # 1 hour
            }
        
        rate_limit = self.rate_limits[integration_id]
        current_time = time.time()
        
        # Reset window if needed
        if current_time - rate_limit['window_start'] > rate_limit['window_duration']:
            rate_limit['calls'] = 0
            rate_limit['window_start'] = current_time
        
        return rate_limit['calls'] < rate_limit['max_calls']
    
    def _update_rate_limit(self, integration_id: str):
        """
        Update rate limit for integration
        """
        if integration_id in self.rate_limits:
            self.rate_limits[integration_id]['calls'] += 1
    
    def register_webhook(self, integration_id: str, event_type: str, 
                        webhook_url: str, secret: str = None) -> str:
        """
        Register webhook for integration
        """
        if integration_id not in self.integrations:
            raise ValueError(f"Integration {integration_id} not found")
        
        webhook_id = f"webhook_{uuid.uuid4().hex[:8]}"
        
        # Store webhook configuration
        webhook_config = {
            'webhook_id': webhook_id,
            'integration_id': integration_id,
            'event_type': event_type,
            'webhook_url': webhook_url,
            'secret': secret,
            'created_at': datetime.now(),
            'active': True
        }
        
        # Store in integration config
        if 'webhooks' not in self.integrations[integration_id].parameters:
            self.integrations[integration_id].parameters['webhooks'] = []
        
        self.integrations[integration_id].parameters['webhooks'].append(webhook_config)
        
        logger.info(f"Registered webhook: {event_type} -> {webhook_url}")
        return webhook_id
    
    def send_webhook_event(self, integration_id: str, event_type: str, 
                          payload: Dict[str, Any]) -> WebhookEvent:
        """
        Send webhook event
        """
        if integration_id not in self.integrations:
            raise ValueError(f"Integration {integration_id} not found")
        
        config = self.integrations[integration_id]
        
        # Find webhook configuration
        webhook_config = None
        for webhook in config.parameters.get('webhooks', []):
            if webhook['event_type'] == event_type and webhook['active']:
                webhook_config = webhook
                break
        
        if not webhook_config:
            raise ValueError(f"No webhook found for event type: {event_type}")
        
        # Create webhook event
        event_id = f"event_{uuid.uuid4().hex[:8]}"
        timestamp = datetime.now()
        
        # Generate signature
        signature = self._generate_webhook_signature(
            payload, webhook_config['secret'], timestamp
        )
        
        webhook_event = WebhookEvent(
            event_id=event_id,
            integration_id=integration_id,
            event_type=event_type,
            payload=payload,
            timestamp=timestamp,
            signature=signature,
            processed=False,
            retry_count=0
        )
        
        # Add to event queue
        self.event_queue.put(webhook_event)
        
        logger.info(f"Webhook event queued: {event_type} ({event_id})")
        return webhook_event
    
    def _generate_webhook_signature(self, payload: Dict[str, Any], 
                                   secret: str, timestamp: datetime) -> str:
        """
        Generate webhook signature
        """
        if not secret:
            return ""
        
        # Create signature payload
        signature_payload = {
            'payload': payload,
            'timestamp': timestamp.isoformat()
        }
        
        # Convert to JSON
        json_payload = json.dumps(signature_payload, sort_keys=True)
        
        # Generate HMAC signature
        signature = hmac.new(
            secret.encode('utf-8'),
            json_payload.encode('utf-8'),
            hashlib.sha256
        ).hexdigest()
        
        return signature
    
    def _process_events(self):
        """
        Process webhook events from queue
        """
        while True:
            try:
                # Get event from queue
                event = self.event_queue.get(timeout=1)
                
                # Process event
                self._process_webhook_event(event)
                
                # Mark task as done
                self.event_queue.task_done()
                
            except queue.Empty:
                continue
            except Exception as e:
                logger.error(f"Error processing webhook event: {str(e)}")
    
    def _process_webhook_event(self, event: WebhookEvent):
        """
        Process webhook event
        """
        try:
            # Get webhook configuration
            config = self.integrations[event.integration_id]
            webhook_config = None
            
            for webhook in config.parameters.get('webhooks', []):
                if webhook['event_type'] == event.event_type:
                    webhook_config = webhook
                    break
            
            if not webhook_config:
                logger.error(f"No webhook configuration found for event {event.event_id}")
                return
            
            # Prepare webhook payload
            webhook_payload = {
                'event_id': event.event_id,
                'event_type': event.event_type,
                'payload': event.payload,
                'timestamp': event.timestamp.isoformat(),
                'signature': event.signature
            }
            
            # Send webhook
            response = requests.post(
                webhook_config['webhook_url'],
                json=webhook_payload,
                headers={'Content-Type': 'application/json'},
                timeout=30
            )
            
            if response.status_code < 400:
                event.processed = True
                logger.info(f"Webhook event processed successfully: {event.event_id}")
            else:
                logger.error(f"Webhook event failed: {event.event_id} - {response.status_code}")
                event.retry_count += 1
                
                # Retry if retry count is less than 3
                if event.retry_count < 3:
                    self.event_queue.put(event)
            
        except Exception as e:
            logger.error(f"Error processing webhook event {event.event_id}: {str(e)}")
            event.retry_count += 1
            
            # Retry if retry count is less than 3
            if event.retry_count < 3:
                self.event_queue.put(event)
    
    def register_event_handler(self, event_type: str, handler: Callable):
        """
        Register event handler
        """
        if event_type not in self.event_handlers:
            self.event_handlers[event_type] = []
        
        self.event_handlers[event_type].append(handler)
        logger.info(f"Registered event handler for: {event_type}")
    
    def trigger_event(self, event_type: str, data: Dict[str, Any]):
        """
        Trigger event
        """
        if event_type in self.event_handlers:
            for handler in self.event_handlers[event_type]:
                try:
                    handler(data)
                except Exception as e:
                    logger.error(f"Error in event handler for {event_type}: {str(e)}")
    
    def create_data_sync(self, source_integration_id: str, target_integration_id: str,
                        sync_config: Dict[str, Any]) -> str:
        """
        Create data synchronization between integrations
        """
        sync_id = f"sync_{uuid.uuid4().hex[:8]}"
        
        # Store sync configuration
        sync_config['sync_id'] = sync_id
        sync_config['source_integration_id'] = source_integration_id
        sync_config['target_integration_id'] = target_integration_id
        sync_config['created_at'] = datetime.now()
        sync_config['active'] = True
        
        # Store in source integration
        if 'syncs' not in self.integrations[source_integration_id].parameters:
            self.integrations[source_integration_id].parameters['syncs'] = []
        
        self.integrations[source_integration_id].parameters['syncs'].append(sync_config)
        
        logger.info(f"Created data sync: {source_integration_id} -> {target_integration_id}")
        return sync_id
    
    def sync_data(self, sync_id: str) -> Dict[str, Any]:
        """
        Execute data synchronization
        """
        # Find sync configuration
        sync_config = None
        for integration_id, config in self.integrations.items():
            for sync in config.parameters.get('syncs', []):
                if sync['sync_id'] == sync_id:
                    sync_config = sync
                    break
            if sync_config:
                break
        
        if not sync_config:
            raise ValueError(f"Sync configuration {sync_id} not found")
        
        source_config = self.integrations[sync_config['source_integration_id']]
        target_config = self.integrations[sync_config['target_integration_id']]
        
        # Get data from source
        source_data = self._get_integration_data(source_config, sync_config.get('source_query', {}))
        
        # Transform data if needed
        transformed_data = self._transform_data(source_data, sync_config.get('transformations', {}))
        
        # Send data to target
        target_result = self._send_integration_data(target_config, transformed_data, sync_config.get('target_endpoint', ''))
        
        # Update sync status
        sync_config['last_sync'] = datetime.now()
        sync_config['last_sync_status'] = 'success' if target_result['success'] else 'error'
        
        return {
            'sync_id': sync_id,
            'records_processed': len(transformed_data),
            'success': target_result['success'],
            'timestamp': datetime.now()
        }
    
    def _get_integration_data(self, config: IntegrationConfig, query: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Get data from integration
        """
        if config.integration_type == IntegrationType.API:
            # Make API call to get data
            endpoint = query.get('endpoint', '/data')
            response = self.make_api_call(
                config.integration_id,
                'GET',
                endpoint,
                headers=query.get('headers', {})
            )
            
            if response.success:
                return response.response.get('data', [])
            else:
                return []
        
        elif config.integration_type == IntegrationType.DATABASE:
            # Query database
            # This would be implemented based on specific database type
            return []
        
        else:
            return []
    
    def _transform_data(self, data: List[Dict[str, Any]], transformations: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Transform data according to transformation rules
        """
        if not transformations:
            return data
        
        transformed_data = []
        
        for record in data:
            transformed_record = record.copy()
            
            # Apply field mappings
            if 'field_mappings' in transformations:
                for source_field, target_field in transformations['field_mappings'].items():
                    if source_field in transformed_record:
                        transformed_record[target_field] = transformed_record.pop(source_field)
            
            # Apply field transformations
            if 'field_transformations' in transformations:
                for field, transformation in transformations['field_transformations'].items():
                    if field in transformed_record:
                        if transformation['type'] == 'format':
                            transformed_record[field] = transformation['format'].format(transformed_record[field])
                        elif transformation['type'] == 'calculate':
                            # Simple calculation (in practice, use more sophisticated expression evaluator)
                            expression = transformation['expression']
                            for key, value in transformed_record.items():
                                expression = expression.replace(f'{{{key}}}', str(value))
                            transformed_record[field] = eval(expression)
            
            transformed_data.append(transformed_record)
        
        return transformed_data
    
    def _send_integration_data(self, config: IntegrationConfig, data: List[Dict[str, Any]], 
                              endpoint: str) -> Dict[str, Any]:
        """
        Send data to integration
        """
        if config.integration_type == IntegrationType.API:
            # Send data via API
            response = self.make_api_call(
                config.integration_id,
                'POST',
                endpoint,
                payload={'data': data}
            )
            
            return {
                'success': response.success,
                'status_code': response.status_code,
                'response': response.response
            }
        
        elif config.integration_type == IntegrationType.DATABASE:
            # Insert data into database
            # This would be implemented based on specific database type
            return {'success': True, 'records_inserted': len(data)}
        
        else:
            return {'success': False, 'error': 'Unsupported integration type'}
    
    def get_integration_status(self, integration_id: str) -> Dict[str, Any]:
        """
        Get integration status
        """
        if integration_id not in self.integrations:
            return {'error': 'Integration not found'}
        
        config = self.integrations[integration_id]
        
        # Get recent API calls
        recent_calls = [call for call in self.api_calls 
                       if call.integration_id == integration_id and 
                       call.timestamp > datetime.now() - timedelta(hours=1)]
        
        # Calculate success rate
        if recent_calls:
            success_rate = sum(1 for call in recent_calls if call.success) / len(recent_calls)
        else:
            success_rate = 1.0
        
        # Get average response time
        if recent_calls:
            avg_response_time = np.mean([call.duration for call in recent_calls])
        else:
            avg_response_time = 0.0
        
        return {
            'integration_id': integration_id,
            'name': config.name,
            'type': config.integration_type.value,
            'status': config.status.value,
            'endpoint': config.endpoint,
            'success_rate': success_rate,
            'avg_response_time': avg_response_time,
            'recent_calls': len(recent_calls),
            'webhooks': len(config.parameters.get('webhooks', [])),
            'syncs': len(config.parameters.get('syncs', [])),
            'last_updated': config.updated_at.isoformat()
        }
    
    def get_integration_summary(self) -> Dict[str, Any]:
        """
        Get integration system summary
        """
        total_integrations = len(self.integrations)
        active_integrations = len([i for i in self.integrations.values() if i.status == IntegrationStatus.ACTIVE])
        
        # Get integration types distribution
        type_distribution = {}
        for integration in self.integrations.values():
            integration_type = integration.integration_type.value
            if integration_type not in type_distribution:
                type_distribution[integration_type] = 0
            type_distribution[integration_type] += 1
        
        # Get recent API calls
        recent_calls = [call for call in self.api_calls 
                       if call.timestamp > datetime.now() - timedelta(hours=24)]
        
        # Calculate overall success rate
        if recent_calls:
            overall_success_rate = sum(1 for call in recent_calls if call.success) / len(recent_calls)
        else:
            overall_success_rate = 1.0
        
        # Get webhook events
        recent_webhook_events = [event for event in self.webhook_events 
                               if event.timestamp > datetime.now() - timedelta(hours=24)]
        
        return {
            'total_integrations': total_integrations,
            'active_integrations': active_integrations,
            'type_distribution': type_distribution,
            'recent_api_calls': len(recent_calls),
            'overall_success_rate': overall_success_rate,
            'recent_webhook_events': len(recent_webhook_events),
            'processed_webhook_events': len([e for e in recent_webhook_events if e.processed]),
            'generated_at': datetime.now().isoformat()
        }
    
    def export_integration_data(self, format: str = 'json') -> str:
        """
        Export integration data
        """
        data = {
            'integrations': [asdict(config) for config in self.integrations.values()],
            'api_calls': [asdict(call) for call in self.api_calls[-1000:]],  # Last 1000 calls
            'webhook_events': [asdict(event) for event in self.webhook_events[-1000:]],  # Last 1000 events
            'summary': self.get_integration_summary()
        }
        
        if format == 'json':
            return json.dumps(data, indent=2, default=str)
        elif format == 'csv':
            # Export integrations as CSV
            df = pd.DataFrame([asdict(config) for config in self.integrations.values()])
            return df.to_csv(index=False)
        else:
            raise ValueError(f"Unsupported format: {format}")

# Example usage
def main():
    """
    Example usage of Advanced Integration System
    """
    # Initialize integration system
    integration_system = AdvancedIntegrationSystem()
    
    # Create API integration
    api_integration = integration_system.create_integration(
        name="Affiliate API",
        integration_type=IntegrationType.API,
        endpoint="https://api.affiliate.com/v1",
        credentials={
            'api_key': 'your-api-key',
            'username': 'your-username',
            'password': 'your-password'
        },
        headers={'Content-Type': 'application/json'}
    )
    
    # Create webhook integration
    webhook_integration = integration_system.create_integration(
        name="Webhook Receiver",
        integration_type=IntegrationType.WEBHOOK,
        endpoint="https://your-webhook.com/receive",
        parameters={'webhooks': []}
    )
    
    # Register webhook
    webhook_id = integration_system.register_webhook(
        api_integration.integration_id,
        'affiliate_signup',
        'https://your-webhook.com/affiliate-signup',
        'your-webhook-secret'
    )
    
    # Make API call
    try:
        api_call = integration_system.make_api_call(
            api_integration.integration_id,
            'GET',
            '/affiliates',
            headers={'Accept': 'application/json'}
        )
        print(f"API call successful: {api_call.status_code}")
    except Exception as e:
        print(f"API call failed: {str(e)}")
    
    # Send webhook event
    webhook_event = integration_system.send_webhook_event(
        api_integration.integration_id,
        'affiliate_signup',
        {'affiliate_id': 'aff_123', 'name': 'John Doe', 'email': 'john@example.com'}
    )
    print(f"Webhook event sent: {webhook_event.event_id}")
    
    # Create data sync
    sync_id = integration_system.create_data_sync(
        api_integration.integration_id,
        webhook_integration.integration_id,
        {
            'source_query': {'endpoint': '/affiliates'},
            'target_endpoint': '/sync/affiliates',
            'field_mappings': {'id': 'affiliate_id', 'name': 'affiliate_name'}
        }
    )
    
    # Execute sync
    sync_result = integration_system.sync_data(sync_id)
    print(f"Data sync completed: {sync_result}")
    
    # Get integration status
    status = integration_system.get_integration_status(api_integration.integration_id)
    print(f"Integration status: {status}")
    
    # Get summary
    summary = integration_system.get_integration_summary()
    print(f"Integration summary: {summary}")

if __name__ == "__main__":
    main()


