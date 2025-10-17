#!/usr/bin/env python3
"""
ClickUp Brain Integration Hub
============================

Universal integration system with connectors, adapters, and data synchronization
for seamless connectivity with external systems and services.
"""

import asyncio
import json
import yaml
import aiohttp
from typing import Any, Dict, List, Optional, Union, Callable, Type
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from pathlib import Path
import logging
from enum import Enum
import threading
from contextlib import asynccontextmanager
import uuid
from abc import ABC, abstractmethod
import hashlib
import hmac
import base64

ROOT = Path(__file__).parent

class IntegrationType(Enum):
    """Integration types."""
    API = "api"
    WEBHOOK = "webhook"
    DATABASE = "database"
    FILE = "file"
    MESSAGE_QUEUE = "message_queue"
    EMAIL = "email"
    SMS = "sms"
    SOCIAL_MEDIA = "social_media"
    CLOUD_STORAGE = "cloud_storage"
    CRM = "crm"
    ERP = "erp"
    HR = "hr"
    FINANCE = "finance"

class SyncDirection(Enum):
    """Data synchronization direction."""
    INBOUND = "inbound"
    OUTBOUND = "outbound"
    BIDIRECTIONAL = "bidirectional"

class SyncStatus(Enum):
    """Synchronization status."""
    ACTIVE = "active"
    PAUSED = "paused"
    ERROR = "error"
    DISABLED = "disabled"

@dataclass
class IntegrationConfig:
    """Integration configuration."""
    name: str
    type: IntegrationType
    endpoint: str
    credentials: Dict[str, str] = field(default_factory=dict)
    headers: Dict[str, str] = field(default_factory=dict)
    timeout: int = 30
    retry_count: int = 3
    retry_delay: float = 1.0
    rate_limit: int = 100
    sync_direction: SyncDirection = SyncDirection.BIDIRECTIONAL
    sync_interval: int = 300  # seconds
    enabled: bool = True
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class DataMapping:
    """Data field mapping configuration."""
    source_field: str
    target_field: str
    transformation: Optional[str] = None
    required: bool = False
    default_value: Any = None

@dataclass
class SyncJob:
    """Data synchronization job."""
    id: str
    integration_id: str
    status: SyncStatus
    direction: SyncDirection
    records_processed: int = 0
    records_successful: int = 0
    records_failed: int = 0
    start_time: datetime = field(default_factory=datetime.now)
    end_time: Optional[datetime] = None
    error_message: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

class IntegrationConnector(ABC):
    """Base class for integration connectors."""
    
    def __init__(self, config: IntegrationConfig):
        self.config = config
        self.logger = logging.getLogger(f"connector_{config.name}")
        self._session: Optional[aiohttp.ClientSession] = None
    
    async def connect(self) -> bool:
        """Establish connection to external system."""
        try:
            self._session = aiohttp.ClientSession(
                timeout=aiohttp.ClientTimeout(total=self.config.timeout),
                headers=self.config.headers
            )
            
            # Test connection
            await self._test_connection()
            self.logger.info(f"Connected to {self.config.name}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to connect to {self.config.name}: {e}")
            return False
    
    async def disconnect(self) -> None:
        """Close connection to external system."""
        if self._session:
            await self._session.close()
            self._session = None
        self.logger.info(f"Disconnected from {self.config.name}")
    
    @abstractmethod
    async def _test_connection(self) -> None:
        """Test connection to external system."""
        pass
    
    @abstractmethod
    async def pull_data(self, filters: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        """Pull data from external system."""
        pass
    
    @abstractmethod
    async def push_data(self, data: List[Dict[str, Any]]) -> bool:
        """Push data to external system."""
        pass
    
    @abstractmethod
    async def get_schema(self) -> Dict[str, Any]:
        """Get data schema from external system."""
        pass

class APIConnector(IntegrationConnector):
    """REST API integration connector."""
    
    async def _test_connection(self) -> None:
        """Test API connection."""
        if not self._session:
            raise ConnectionError("Session not initialized")
        
        # Test with a simple GET request
        async with self._session.get(f"{self.config.endpoint}/health") as response:
            if response.status >= 400:
                raise ConnectionError(f"API returned status {response.status}")
    
    async def pull_data(self, filters: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        """Pull data from API."""
        if not self._session:
            raise ConnectionError("Session not initialized")
        
        params = filters or {}
        
        async with self._session.get(self.config.endpoint, params=params) as response:
            if response.status == 200:
                data = await response.json()
                return data if isinstance(data, list) else [data]
            else:
                raise Exception(f"API request failed with status {response.status}")
    
    async def push_data(self, data: List[Dict[str, Any]]) -> bool:
        """Push data to API."""
        if not self._session:
            raise ConnectionError("Session not initialized")
        
        try:
            for record in data:
                async with self._session.post(self.config.endpoint, json=record) as response:
                    if response.status >= 400:
                        raise Exception(f"API request failed with status {response.status}")
            return True
        except Exception as e:
            self.logger.error(f"Failed to push data: {e}")
            return False
    
    async def get_schema(self) -> Dict[str, Any]:
        """Get API schema."""
        if not self._session:
            raise ConnectionError("Session not initialized")
        
        # Try to get schema from /schema endpoint
        try:
            async with self._session.get(f"{self.config.endpoint}/schema") as response:
                if response.status == 200:
                    return await response.json()
        except Exception:
            pass
        
        # Fallback: analyze sample data
        sample_data = await self.pull_data()
        if sample_data:
            return {
                "fields": list(sample_data[0].keys()),
                "sample": sample_data[0]
            }
        
        return {}

class DatabaseConnector(IntegrationConnector):
    """Database integration connector."""
    
    async def _test_connection(self) -> None:
        """Test database connection."""
        # Database connection testing would be implemented here
        # This is a simplified version
        pass
    
    async def pull_data(self, filters: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        """Pull data from database."""
        # Database query implementation would go here
        # This is a simplified version
        return []
    
    async def push_data(self, data: List[Dict[str, Any]]) -> bool:
        """Push data to database."""
        # Database insert/update implementation would go here
        # This is a simplified version
        return True
    
    async def get_schema(self) -> Dict[str, Any]:
        """Get database schema."""
        # Database schema introspection would go here
        # This is a simplified version
        return {}

class WebhookConnector(IntegrationConnector):
    """Webhook integration connector."""
    
    async def _test_connection(self) -> None:
        """Test webhook connection."""
        # Webhook connection testing would be implemented here
        pass
    
    async def pull_data(self, filters: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        """Pull data from webhook (not applicable)."""
        raise NotImplementedError("Webhooks don't support data pulling")
    
    async def push_data(self, data: List[Dict[str, Any]]) -> bool:
        """Push data to webhook."""
        if not self._session:
            raise ConnectionError("Session not initialized")
        
        try:
            for record in data:
                async with self._session.post(self.config.endpoint, json=record) as response:
                    if response.status >= 400:
                        raise Exception(f"Webhook request failed with status {response.status}")
            return True
        except Exception as e:
            self.logger.error(f"Failed to push data to webhook: {e}")
            return False
    
    async def get_schema(self) -> Dict[str, Any]:
        """Get webhook schema."""
        return {
            "type": "webhook",
            "description": "Webhook endpoint for receiving data"
        }

class DataTransformer:
    """Data transformation engine."""
    
    def __init__(self):
        self.logger = logging.getLogger("data_transformer")
    
    def transform_data(self, data: List[Dict[str, Any]], mappings: List[DataMapping]) -> List[Dict[str, Any]]:
        """Transform data using field mappings."""
        transformed_data = []
        
        for record in data:
            transformed_record = {}
            
            for mapping in mappings:
                source_value = record.get(mapping.source_field)
                
                if source_value is not None:
                    # Apply transformation if specified
                    if mapping.transformation:
                        transformed_value = self._apply_transformation(source_value, mapping.transformation)
                    else:
                        transformed_value = source_value
                    
                    transformed_record[mapping.target_field] = transformed_value
                elif mapping.required:
                    if mapping.default_value is not None:
                        transformed_record[mapping.target_field] = mapping.default_value
                    else:
                        self.logger.warning(f"Required field {mapping.source_field} is missing")
                else:
                    # Optional field, skip if not present
                    pass
            
            transformed_data.append(transformed_record)
        
        return transformed_data
    
    def _apply_transformation(self, value: Any, transformation: str) -> Any:
        """Apply data transformation."""
        try:
            if transformation == "uppercase":
                return str(value).upper()
            elif transformation == "lowercase":
                return str(value).lower()
            elif transformation == "trim":
                return str(value).strip()
            elif transformation.startswith("format:"):
                format_str = transformation[7:]  # Remove "format:" prefix
                return format_str.format(value)
            elif transformation.startswith("replace:"):
                parts = transformation[8:].split("|")
                if len(parts) == 2:
                    return str(value).replace(parts[0], parts[1])
            elif transformation == "to_int":
                return int(value)
            elif transformation == "to_float":
                return float(value)
            elif transformation == "to_string":
                return str(value)
            else:
                return value
        except Exception as e:
            self.logger.error(f"Transformation failed: {e}")
            return value

class SyncManager:
    """Data synchronization manager."""
    
    def __init__(self):
        self.sync_jobs: Dict[str, SyncJob] = {}
        self.logger = logging.getLogger("sync_manager")
        self._lock = threading.RLock()
    
    async def start_sync(self, integration_id: str, direction: SyncDirection, 
                        connector: IntegrationConnector, transformer: DataTransformer = None,
                        mappings: List[DataMapping] = None) -> str:
        """Start data synchronization job."""
        job_id = str(uuid.uuid4())
        
        job = SyncJob(
            id=job_id,
            integration_id=integration_id,
            status=SyncStatus.ACTIVE,
            direction=direction
        )
        
        with self._lock:
            self.sync_jobs[job_id] = job
        
        # Start sync in background
        asyncio.create_task(self._run_sync(job, connector, transformer, mappings))
        
        self.logger.info(f"Started sync job {job_id} for integration {integration_id}")
        return job_id
    
    async def _run_sync(self, job: SyncJob, connector: IntegrationConnector,
                       transformer: DataTransformer, mappings: List[DataMapping]) -> None:
        """Run synchronization job."""
        try:
            if job.direction in [SyncDirection.INBOUND, SyncDirection.BIDIRECTIONAL]:
                # Pull data from external system
                data = await connector.pull_data()
                job.records_processed += len(data)
                
                # Transform data if transformer and mappings provided
                if transformer and mappings:
                    data = transformer.transform_data(data, mappings)
                
                # Process inbound data (save to local system)
                # This would be implemented based on the target system
                job.records_successful += len(data)
            
            if job.direction in [SyncDirection.OUTBOUND, SyncDirection.BIDIRECTIONAL]:
                # Get data from local system
                # This would be implemented based on the source system
                local_data = []  # Placeholder
                
                # Transform data if transformer and mappings provided
                if transformer and mappings:
                    local_data = transformer.transform_data(local_data, mappings)
                
                # Push data to external system
                success = await connector.push_data(local_data)
                if success:
                    job.records_successful += len(local_data)
                else:
                    job.records_failed += len(local_data)
                
                job.records_processed += len(local_data)
            
            job.status = SyncStatus.ACTIVE
            job.end_time = datetime.now()
            
            self.logger.info(f"Sync job {job.id} completed successfully")
            
        except Exception as e:
            job.status = SyncStatus.ERROR
            job.error_message = str(e)
            job.end_time = datetime.now()
            
            self.logger.error(f"Sync job {job.id} failed: {e}")
    
    def get_sync_status(self, job_id: str) -> Optional[SyncJob]:
        """Get synchronization job status."""
        with self._lock:
            return self.sync_jobs.get(job_id)
    
    def list_sync_jobs(self) -> List[SyncJob]:
        """List all synchronization jobs."""
        with self._lock:
            return list(self.sync_jobs.values())

class IntegrationHub:
    """Main integration hub."""
    
    def __init__(self):
        self.integrations: Dict[str, IntegrationConfig] = {}
        self.connectors: Dict[str, IntegrationConnector] = {}
        self.sync_manager = SyncManager()
        self.data_transformer = DataTransformer()
        self.logger = logging.getLogger("integration_hub")
        self._lock = threading.RLock()
    
    def register_integration(self, config: IntegrationConfig) -> None:
        """Register integration configuration."""
        with self._lock:
            self.integrations[config.name] = config
        
        self.logger.info(f"Registered integration: {config.name}")
    
    async def create_connector(self, integration_name: str) -> IntegrationConnector:
        """Create connector for integration."""
        with self._lock:
            if integration_name not in self.integrations:
                raise ValueError(f"Integration {integration_name} not found")
            
            config = self.integrations[integration_name]
        
        # Create connector based on type
        if config.type == IntegrationType.API:
            connector = APIConnector(config)
        elif config.type == IntegrationType.DATABASE:
            connector = DatabaseConnector(config)
        elif config.type == IntegrationType.WEBHOOK:
            connector = WebhookConnector(config)
        else:
            raise ValueError(f"Unsupported integration type: {config.type}")
        
        # Connect to external system
        connected = await connector.connect()
        if not connected:
            raise ConnectionError(f"Failed to connect to {integration_name}")
        
        with self._lock:
            self.connectors[integration_name] = connector
        
        return connector
    
    async def start_sync(self, integration_name: str, direction: SyncDirection = SyncDirection.BIDIRECTIONAL,
                        mappings: List[DataMapping] = None) -> str:
        """Start data synchronization."""
        connector = await self.create_connector(integration_name)
        
        return await self.sync_manager.start_sync(
            integration_name,
            direction,
            connector,
            self.data_transformer,
            mappings
        )
    
    async def pull_data(self, integration_name: str, filters: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        """Pull data from integration."""
        connector = await self.create_connector(integration_name)
        return await connector.pull_data(filters)
    
    async def push_data(self, integration_name: str, data: List[Dict[str, Any]]) -> bool:
        """Push data to integration."""
        connector = await self.create_connector(integration_name)
        return await connector.push_data(data)
    
    async def get_schema(self, integration_name: str) -> Dict[str, Any]:
        """Get integration schema."""
        connector = await self.create_connector(integration_name)
        return await connector.get_schema()
    
    def list_integrations(self) -> List[IntegrationConfig]:
        """List all integrations."""
        with self._lock:
            return list(self.integrations.values())
    
    def get_integration(self, name: str) -> Optional[IntegrationConfig]:
        """Get integration by name."""
        with self._lock:
            return self.integrations.get(name)
    
    async def disconnect_all(self) -> None:
        """Disconnect all connectors."""
        with self._lock:
            connectors = list(self.connectors.values())
        
        for connector in connectors:
            try:
                await connector.disconnect()
            except Exception as e:
                self.logger.error(f"Error disconnecting connector: {e}")
        
        with self._lock:
            self.connectors.clear()
    
    def create_data_mapping(self, source_field: str, target_field: str, 
                           transformation: str = None, required: bool = False,
                           default_value: Any = None) -> DataMapping:
        """Create data field mapping."""
        return DataMapping(
            source_field=source_field,
            target_field=target_field,
            transformation=transformation,
            required=required,
            default_value=default_value
        )

# Global integration hub
integration_hub = IntegrationHub()

def get_integration_hub() -> IntegrationHub:
    """Get global integration hub."""
    return integration_hub

async def register_integration(config: IntegrationConfig) -> None:
    """Register integration using global hub."""
    integration_hub.register_integration(config)

async def start_sync(integration_name: str, direction: SyncDirection = SyncDirection.BIDIRECTIONAL) -> str:
    """Start sync using global hub."""
    return await integration_hub.start_sync(integration_name, direction)

if __name__ == "__main__":
    # Demo integration system
    print("ClickUp Brain Integration Hub Demo")
    print("=" * 50)
    
    # Setup logging
    logging.basicConfig(level=logging.INFO)
    
    async def demo():
        # Get integration hub
        hub = get_integration_hub()
        
        # Register API integration
        api_config = IntegrationConfig(
            name="external_api",
            type=IntegrationType.API,
            endpoint="https://jsonplaceholder.typicode.com/posts",
            headers={"Content-Type": "application/json"},
            sync_direction=SyncDirection.INBOUND,
            sync_interval=300
        )
        hub.register_integration(api_config)
        
        # Register webhook integration
        webhook_config = IntegrationConfig(
            name="notification_webhook",
            type=IntegrationType.WEBHOOK,
            endpoint="https://webhook.site/your-webhook-url",
            sync_direction=SyncDirection.OUTBOUND
        )
        hub.register_integration(webhook_config)
        
        # Create data mappings
        mappings = [
            hub.create_data_mapping("id", "external_id", "to_string"),
            hub.create_data_mapping("title", "subject", "uppercase"),
            hub.create_data_mapping("body", "content", "trim"),
            hub.create_data_mapping("userId", "author_id", "to_int")
        ]
        
        # Pull data from API
        try:
            data = await hub.pull_data("external_api")
            print(f"Pulled {len(data)} records from external API")
            
            # Transform data
            transformed_data = hub.data_transformer.transform_data(data[:3], mappings)
            print(f"Transformed data: {transformed_data}")
            
        except Exception as e:
            print(f"Error pulling data: {e}")
        
        # Start synchronization
        try:
            sync_job_id = await hub.start_sync("external_api", SyncDirection.INBOUND, mappings)
            print(f"Started sync job: {sync_job_id}")
            
            # Check sync status
            await asyncio.sleep(2)
            sync_job = hub.sync_manager.get_sync_status(sync_job_id)
            if sync_job:
                print(f"Sync status: {sync_job.status.value}")
                print(f"Records processed: {sync_job.records_processed}")
                print(f"Records successful: {sync_job.records_successful}")
            
        except Exception as e:
            print(f"Error starting sync: {e}")
        
        # Get integration schema
        try:
            schema = await hub.get_schema("external_api")
            print(f"API schema: {schema}")
        except Exception as e:
            print(f"Error getting schema: {e}")
        
        # List integrations
        integrations = hub.list_integrations()
        print(f"Registered integrations: {[i.name for i in integrations]}")
        
        # Disconnect all
        await hub.disconnect_all()
        
        print("\nIntegration hub demo completed!")
    
    asyncio.run(demo())