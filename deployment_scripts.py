#!/usr/bin/env python3
"""
Deployment and Monitoring Scripts for Competitive Pricing Analysis System
========================================================================

Scripts for deploying, monitoring, and maintaining the pricing analysis system in production.

Features:
- Docker containerization
- Kubernetes deployment
- Health monitoring
- Performance metrics
- Log aggregation
- Backup and recovery
- Auto-scaling
- Security monitoring
"""

import os
import sys
import json
import yaml
import subprocess
import time
import logging
import psutil
import requests
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
import sqlite3
import shutil
import gzip
import tarfile
from pathlib import Path
import docker
import kubernetes
from kubernetes import client, config
import schedule
import threading

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SystemMonitor:
    """System monitoring and health checks"""
    
    def __init__(self, config_file: str = "monitoring_config.yaml"):
        """Initialize system monitor"""
        self.config = self._load_config(config_file)
        self.db_path = self.config.get('database_path', 'pricing_analysis.db')
        self.api_url = self.config.get('api_url', 'http://localhost:8080')
        self.metrics = {}
        
        logger.info("System Monitor initialized")
    
    def _load_config(self, config_file: str) -> Dict:
        """Load monitoring configuration"""
        try:
            with open(config_file, 'r') as f:
                return yaml.safe_load(f)
        except FileNotFoundError:
            return self._get_default_config()
    
    def _get_default_config(self) -> Dict:
        """Get default monitoring configuration"""
        return {
            'database_path': 'pricing_analysis.db',
            'api_url': 'http://localhost:8080',
            'monitoring': {
                'cpu_threshold': 80,
                'memory_threshold': 80,
                'disk_threshold': 90,
                'response_time_threshold': 5.0
            },
            'alerts': {
                'enabled': True,
                'email_recipients': [],
                'webhook_url': None
            }
        }
    
    def check_system_health(self) -> Dict[str, Any]:
        """Check overall system health"""
        health_status = {
            'timestamp': datetime.now().isoformat(),
            'overall_status': 'healthy',
            'checks': {}
        }
        
        # Check CPU usage
        cpu_usage = psutil.cpu_percent(interval=1)
        health_status['checks']['cpu'] = {
            'status': 'healthy' if cpu_usage < self.config['monitoring']['cpu_threshold'] else 'warning',
            'value': cpu_usage,
            'threshold': self.config['monitoring']['cpu_threshold']
        }
        
        # Check memory usage
        memory = psutil.virtual_memory()
        health_status['checks']['memory'] = {
            'status': 'healthy' if memory.percent < self.config['monitoring']['memory_threshold'] else 'warning',
            'value': memory.percent,
            'threshold': self.config['monitoring']['memory_threshold']
        }
        
        # Check disk usage
        disk = psutil.disk_usage('/')
        health_status['checks']['disk'] = {
            'status': 'healthy' if disk.percent < self.config['monitoring']['disk_threshold'] else 'warning',
            'value': disk.percent,
            'threshold': self.config['monitoring']['disk_threshold']
        }
        
        # Check API response time
        api_response = self._check_api_health()
        health_status['checks']['api'] = api_response
        
        # Check database connectivity
        db_response = self._check_database_health()
        health_status['checks']['database'] = db_response
        
        # Determine overall status
        if any(check['status'] == 'error' for check in health_status['checks'].values()):
            health_status['overall_status'] = 'error'
        elif any(check['status'] == 'warning' for check in health_status['checks'].values()):
            health_status['overall_status'] = 'warning'
        
        return health_status
    
    def _check_api_health(self) -> Dict[str, Any]:
        """Check API health and response time"""
        try:
            start_time = time.time()
            response = requests.get(f"{self.api_url}/api/status", timeout=10)
            response_time = time.time() - start_time
            
            if response.status_code == 200:
                return {
                    'status': 'healthy' if response_time < self.config['monitoring']['response_time_threshold'] else 'warning',
                    'response_time': response_time,
                    'status_code': response.status_code,
                    'threshold': self.config['monitoring']['response_time_threshold']
                }
            else:
                return {
                    'status': 'error',
                    'response_time': response_time,
                    'status_code': response.status_code,
                    'error': f'HTTP {response.status_code}'
                }
        except Exception as e:
            return {
                'status': 'error',
                'response_time': None,
                'status_code': None,
                'error': str(e)
            }
    
    def _check_database_health(self) -> Dict[str, Any]:
        """Check database health"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Test basic query
            start_time = time.time()
            cursor.execute("SELECT COUNT(*) FROM pricing_data")
            result = cursor.fetchone()
            query_time = time.time() - start_time
            
            conn.close()
            
            return {
                'status': 'healthy',
                'query_time': query_time,
                'record_count': result[0] if result else 0
            }
            
        except Exception as e:
            return {
                'status': 'error',
                'query_time': None,
                'error': str(e)
            }
    
    def get_performance_metrics(self) -> Dict[str, Any]:
        """Get system performance metrics"""
        metrics = {
            'timestamp': datetime.now().isoformat(),
            'system': {
                'cpu_percent': psutil.cpu_percent(),
                'memory_percent': psutil.virtual_memory().percent,
                'disk_percent': psutil.disk_usage('/').percent,
                'load_average': os.getloadavg() if hasattr(os, 'getloadavg') else None
            },
            'application': {}
        }
        
        # Get application-specific metrics
        try:
            response = requests.get(f"{self.api_url}/api/metrics", timeout=5)
            if response.status_code == 200:
                metrics['application'] = response.json()
        except Exception as e:
            logger.warning(f"Could not fetch application metrics: {e}")
        
        return metrics
    
    def send_health_alert(self, health_status: Dict[str, Any]):
        """Send health alert if system is unhealthy"""
        if health_status['overall_status'] in ['warning', 'error']:
            alert_config = self.config.get('alerts', {})
            
            if alert_config.get('enabled', False):
                message = f"System Health Alert: {health_status['overall_status'].upper()}\n\n"
                
                for check_name, check_data in health_status['checks'].items():
                    if check_data['status'] in ['warning', 'error']:
                        message += f"{check_name}: {check_data['status']} - {check_data.get('value', 'N/A')}\n"
                
                # Send email alert
                if alert_config.get('email_recipients'):
                    self._send_email_alert(message, health_status)
                
                # Send webhook alert
                if alert_config.get('webhook_url'):
                    self._send_webhook_alert(message, health_status)
    
    def _send_email_alert(self, message: str, health_status: Dict[str, Any]):
        """Send email alert"""
        # Implementation would depend on email service
        logger.info(f"Email alert: {message}")
    
    def _send_webhook_alert(self, message: str, health_status: Dict[str, Any]):
        """Send webhook alert"""
        try:
            webhook_url = self.config['alerts']['webhook_url']
            payload = {
                'message': message,
                'health_status': health_status,
                'timestamp': datetime.now().isoformat()
            }
            
            response = requests.post(webhook_url, json=payload, timeout=10)
            response.raise_for_status()
            
        except Exception as e:
            logger.error(f"Failed to send webhook alert: {e}")

class DatabaseManager:
    """Database management and maintenance"""
    
    def __init__(self, db_path: str):
        """Initialize database manager"""
        self.db_path = db_path
        self.backup_dir = "backups"
        os.makedirs(self.backup_dir, exist_ok=True)
        
        logger.info(f"Database Manager initialized for {db_path}")
    
    def create_backup(self) -> str:
        """Create database backup"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_filename = f"pricing_analysis_backup_{timestamp}.db"
        backup_path = os.path.join(self.backup_dir, backup_filename)
        
        try:
            # Copy database file
            shutil.copy2(self.db_path, backup_path)
            
            # Compress backup
            compressed_path = f"{backup_path}.gz"
            with open(backup_path, 'rb') as f_in:
                with gzip.open(compressed_path, 'wb') as f_out:
                    shutil.copyfileobj(f_in, f_out)
            
            # Remove uncompressed backup
            os.remove(backup_path)
            
            logger.info(f"Database backup created: {compressed_path}")
            return compressed_path
            
        except Exception as e:
            logger.error(f"Failed to create database backup: {e}")
            raise
    
    def restore_backup(self, backup_path: str):
        """Restore database from backup"""
        try:
            # Decompress if needed
            if backup_path.endswith('.gz'):
                decompressed_path = backup_path[:-3]  # Remove .gz extension
                with gzip.open(backup_path, 'rb') as f_in:
                    with open(decompressed_path, 'wb') as f_out:
                        shutil.copyfileobj(f_in, f_out)
                backup_path = decompressed_path
            
            # Restore database
            shutil.copy2(backup_path, self.db_path)
            
            logger.info(f"Database restored from: {backup_path}")
            
        except Exception as e:
            logger.error(f"Failed to restore database backup: {e}")
            raise
    
    def cleanup_old_backups(self, days_to_keep: int = 30):
        """Clean up old backup files"""
        try:
            cutoff_date = datetime.now() - timedelta(days=days_to_keep)
            
            for filename in os.listdir(self.backup_dir):
                file_path = os.path.join(self.backup_dir, filename)
                
                if os.path.isfile(file_path):
                    file_time = datetime.fromtimestamp(os.path.getmtime(file_path))
                    
                    if file_time < cutoff_date:
                        os.remove(file_path)
                        logger.info(f"Removed old backup: {filename}")
            
        except Exception as e:
            logger.error(f"Failed to cleanup old backups: {e}")
    
    def optimize_database(self):
        """Optimize database performance"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Analyze tables for query optimization
            cursor.execute("ANALYZE")
            
            # Vacuum database to reclaim space
            cursor.execute("VACUUM")
            
            # Reindex for better performance
            cursor.execute("REINDEX")
            
            conn.close()
            
            logger.info("Database optimization completed")
            
        except Exception as e:
            logger.error(f"Failed to optimize database: {e}")
    
    def get_database_stats(self) -> Dict[str, Any]:
        """Get database statistics"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            stats = {}
            
            # Get table sizes
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
            tables = cursor.fetchall()
            
            for table in tables:
                table_name = table[0]
                cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
                count = cursor.fetchone()[0]
                stats[table_name] = count
            
            # Get database file size
            stats['file_size_mb'] = os.path.getsize(self.db_path) / (1024 * 1024)
            
            conn.close()
            
            return stats
            
        except Exception as e:
            logger.error(f"Failed to get database stats: {e}")
            return {}

class DockerManager:
    """Docker container management"""
    
    def __init__(self):
        """Initialize Docker manager"""
        try:
            self.client = docker.from_env()
            logger.info("Docker client initialized")
        except Exception as e:
            logger.error(f"Failed to initialize Docker client: {e}")
            self.client = None
    
    def build_image(self, dockerfile_path: str, image_name: str, tag: str = "latest") -> bool:
        """Build Docker image"""
        if not self.client:
            logger.error("Docker client not available")
            return False
        
        try:
            image, build_logs = self.client.images.build(
                path=dockerfile_path,
                tag=f"{image_name}:{tag}",
                rm=True
            )
            
            logger.info(f"Docker image built: {image_name}:{tag}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to build Docker image: {e}")
            return False
    
    def run_container(self, image_name: str, container_name: str, 
                     ports: Dict[str, str] = None, environment: Dict[str, str] = None) -> bool:
        """Run Docker container"""
        if not self.client:
            logger.error("Docker client not available")
            return False
        
        try:
            container = self.client.containers.run(
                image_name,
                name=container_name,
                ports=ports,
                environment=environment,
                detach=True,
                restart_policy={"Name": "unless-stopped"}
            )
            
            logger.info(f"Docker container started: {container_name}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to run Docker container: {e}")
            return False
    
    def stop_container(self, container_name: str) -> bool:
        """Stop Docker container"""
        if not self.client:
            logger.error("Docker client not available")
            return False
        
        try:
            container = self.client.containers.get(container_name)
            container.stop()
            
            logger.info(f"Docker container stopped: {container_name}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to stop Docker container: {e}")
            return False
    
    def get_container_status(self, container_name: str) -> Dict[str, Any]:
        """Get container status"""
        if not self.client:
            return {'status': 'error', 'message': 'Docker client not available'}
        
        try:
            container = self.client.containers.get(container_name)
            
            return {
                'status': container.status,
                'state': container.attrs['State'],
                'created': container.attrs['Created'],
                'ports': container.attrs['NetworkSettings']['Ports']
            }
            
        except Exception as e:
            return {'status': 'error', 'message': str(e)}

class KubernetesManager:
    """Kubernetes deployment management"""
    
    def __init__(self, config_file: str = None):
        """Initialize Kubernetes manager"""
        try:
            if config_file:
                config.load_kube_config(config_file)
            else:
                config.load_incluster_config()
            
            self.v1 = client.CoreV1Api()
            self.apps_v1 = client.AppsV1Api()
            
            logger.info("Kubernetes client initialized")
            
        except Exception as e:
            logger.error(f"Failed to initialize Kubernetes client: {e}")
            self.v1 = None
            self.apps_v1 = None
    
    def deploy_application(self, deployment_config: Dict[str, Any]) -> bool:
        """Deploy application to Kubernetes"""
        if not self.apps_v1:
            logger.error("Kubernetes client not available")
            return False
        
        try:
            # Create deployment
            deployment = client.V1Deployment(
                metadata=client.V1ObjectMeta(name=deployment_config['name']),
                spec=client.V1DeploymentSpec(
                    replicas=deployment_config.get('replicas', 1),
                    selector=client.V1LabelSelector(
                        match_labels={"app": deployment_config['name']}
                    ),
                    template=client.V1PodTemplateSpec(
                        metadata=client.V1ObjectMeta(
                            labels={"app": deployment_config['name']}
                        ),
                        spec=client.V1PodSpec(
                            containers=[
                                client.V1Container(
                                    name=deployment_config['name'],
                                    image=deployment_config['image'],
                                    ports=[client.V1ContainerPort(container_port=8080)]
                                )
                            ]
                        )
                    )
                )
            )
            
            self.apps_v1.create_namespaced_deployment(
                namespace=deployment_config.get('namespace', 'default'),
                body=deployment
            )
            
            logger.info(f"Kubernetes deployment created: {deployment_config['name']}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to deploy to Kubernetes: {e}")
            return False
    
    def get_deployment_status(self, name: str, namespace: str = "default") -> Dict[str, Any]:
        """Get deployment status"""
        if not self.apps_v1:
            return {'status': 'error', 'message': 'Kubernetes client not available'}
        
        try:
            deployment = self.apps_v1.read_namespaced_deployment(name, namespace)
            
            return {
                'name': deployment.metadata.name,
                'replicas': deployment.spec.replicas,
                'ready_replicas': deployment.status.ready_replicas,
                'available_replicas': deployment.status.available_replicas,
                'conditions': deployment.status.conditions
            }
            
        except Exception as e:
            return {'status': 'error', 'message': str(e)}

class DeploymentManager:
    """Main deployment manager"""
    
    def __init__(self, config_file: str = "deployment_config.yaml"):
        """Initialize deployment manager"""
        self.config = self._load_config(config_file)
        self.monitor = SystemMonitor()
        self.db_manager = DatabaseManager(self.config.get('database_path', 'pricing_analysis.db'))
        self.docker_manager = DockerManager()
        self.k8s_manager = KubernetesManager()
        
        logger.info("Deployment Manager initialized")
    
    def _load_config(self, config_file: str) -> Dict:
        """Load deployment configuration"""
        try:
            with open(config_file, 'r') as f:
                return yaml.safe_load(f)
        except FileNotFoundError:
            return self._get_default_config()
    
    def _get_default_config(self) -> Dict:
        """Get default deployment configuration"""
        return {
            'database_path': 'pricing_analysis.db',
            'deployment': {
                'type': 'docker',  # docker, kubernetes, local
                'image_name': 'pricing-analysis-system',
                'container_name': 'pricing-analysis',
                'ports': {'8080': '8080'},
                'environment': {}
            },
            'monitoring': {
                'enabled': True,
                'interval_minutes': 5
            },
            'backup': {
                'enabled': True,
                'interval_hours': 24,
                'retention_days': 30
            }
        }
    
    def deploy(self) -> bool:
        """Deploy the application"""
        deployment_config = self.config.get('deployment', {})
        deployment_type = deployment_config.get('type', 'local')
        
        if deployment_type == 'docker':
            return self._deploy_docker()
        elif deployment_type == 'kubernetes':
            return self._deploy_kubernetes()
        else:
            return self._deploy_local()
    
    def _deploy_docker(self) -> bool:
        """Deploy using Docker"""
        deployment_config = self.config.get('deployment', {})
        
        # Build image
        if not self.docker_manager.build_image(
            dockerfile_path=".",
            image_name=deployment_config.get('image_name', 'pricing-analysis-system')
        ):
            return False
        
        # Run container
        return self.docker_manager.run_container(
            image_name=deployment_config.get('image_name', 'pricing-analysis-system'),
            container_name=deployment_config.get('container_name', 'pricing-analysis'),
            ports=deployment_config.get('ports', {'8080': '8080'}),
            environment=deployment_config.get('environment', {})
        )
    
    def _deploy_kubernetes(self) -> bool:
        """Deploy using Kubernetes"""
        deployment_config = self.config.get('deployment', {})
        
        k8s_config = {
            'name': deployment_config.get('container_name', 'pricing-analysis'),
            'image': f"{deployment_config.get('image_name', 'pricing-analysis-system')}:latest",
            'replicas': deployment_config.get('replicas', 1),
            'namespace': deployment_config.get('namespace', 'default')
        }
        
        return self.k8s_manager.deploy_application(k8s_config)
    
    def _deploy_local(self) -> bool:
        """Deploy locally"""
        logger.info("Deploying locally - starting API server")
        
        # Start API server in background
        import subprocess
        try:
            subprocess.Popen([
                sys.executable, 'pricing_api_server.py'
            ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            
            logger.info("Local deployment started")
            return True
            
        except Exception as e:
            logger.error(f"Failed to start local deployment: {e}")
            return False
    
    def start_monitoring(self):
        """Start system monitoring"""
        monitoring_config = self.config.get('monitoring', {})
        
        if not monitoring_config.get('enabled', True):
            logger.info("Monitoring is disabled")
            return
        
        interval_minutes = monitoring_config.get('interval_minutes', 5)
        
        def monitor_loop():
            while True:
                try:
                    # Check system health
                    health_status = self.monitor.check_system_health()
                    
                    # Send alerts if needed
                    self.monitor.send_health_alert(health_status)
                    
                    # Log metrics
                    metrics = self.monitor.get_performance_metrics()
                    logger.info(f"System metrics: CPU {metrics['system']['cpu_percent']:.1f}%, "
                               f"Memory {metrics['system']['memory_percent']:.1f}%")
                    
                    time.sleep(interval_minutes * 60)
                    
                except Exception as e:
                    logger.error(f"Error in monitoring loop: {e}")
                    time.sleep(60)
        
        # Start monitoring in background thread
        monitor_thread = threading.Thread(target=monitor_loop, daemon=True)
        monitor_thread.start()
        
        logger.info(f"Monitoring started with {interval_minutes} minute intervals")
    
    def start_backup_scheduler(self):
        """Start backup scheduler"""
        backup_config = self.config.get('backup', {})
        
        if not backup_config.get('enabled', True):
            logger.info("Backup is disabled")
            return
        
        interval_hours = backup_config.get('interval_hours', 24)
        retention_days = backup_config.get('retention_days', 30)
        
        # Schedule daily backup
        schedule.every(interval_hours).hours.do(self._run_backup, retention_days)
        
        def backup_scheduler():
            while True:
                schedule.run_pending()
                time.sleep(3600)  # Check every hour
        
        # Start backup scheduler in background thread
        backup_thread = threading.Thread(target=backup_scheduler, daemon=True)
        backup_thread.start()
        
        logger.info(f"Backup scheduler started with {interval_hours} hour intervals")
    
    def _run_backup(self, retention_days: int):
        """Run backup and cleanup"""
        try:
            # Create backup
            backup_path = self.db_manager.create_backup()
            logger.info(f"Backup completed: {backup_path}")
            
            # Cleanup old backups
            self.db_manager.cleanup_old_backups(retention_days)
            
            # Optimize database
            self.db_manager.optimize_database()
            
        except Exception as e:
            logger.error(f"Backup failed: {e}")
    
    def get_deployment_status(self) -> Dict[str, Any]:
        """Get deployment status"""
        deployment_config = self.config.get('deployment', {})
        deployment_type = deployment_config.get('type', 'local')
        
        status = {
            'deployment_type': deployment_type,
            'timestamp': datetime.now().isoformat()
        }
        
        if deployment_type == 'docker':
            container_name = deployment_config.get('container_name', 'pricing-analysis')
            status['container'] = self.docker_manager.get_container_status(container_name)
        
        elif deployment_type == 'kubernetes':
            app_name = deployment_config.get('container_name', 'pricing-analysis')
            namespace = deployment_config.get('namespace', 'default')
            status['deployment'] = self.k8s_manager.get_deployment_status(app_name, namespace)
        
        # Add system health
        status['health'] = self.monitor.check_system_health()
        
        # Add database stats
        status['database'] = self.db_manager.get_database_stats()
        
        return status

def create_dockerfile():
    """Create Dockerfile for containerization"""
    dockerfile_content = """
FROM python:3.9-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \\
    gcc \\
    g++ \\
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements_pricing.txt .
RUN pip install --no-cache-dir -r requirements_pricing.txt

# Copy application code
COPY . .

# Create non-root user
RUN useradd -m -u 1000 appuser && chown -R appuser:appuser /app
USER appuser

# Expose port
EXPOSE 8080

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \\
    CMD curl -f http://localhost:8080/api/status || exit 1

# Start application
CMD ["python", "pricing_api_server.py"]
"""
    
    with open('Dockerfile', 'w') as f:
        f.write(dockerfile_content)
    
    logger.info("Dockerfile created")

def create_kubernetes_manifests():
    """Create Kubernetes deployment manifests"""
    # Deployment manifest
    deployment_manifest = {
        'apiVersion': 'apps/v1',
        'kind': 'Deployment',
        'metadata': {
            'name': 'pricing-analysis-system',
            'labels': {
                'app': 'pricing-analysis-system'
            }
        },
        'spec': {
            'replicas': 2,
            'selector': {
                'matchLabels': {
                    'app': 'pricing-analysis-system'
                }
            },
            'template': {
                'metadata': {
                    'labels': {
                        'app': 'pricing-analysis-system'
                    }
                },
                'spec': {
                    'containers': [
                        {
                            'name': 'pricing-analysis-system',
                            'image': 'pricing-analysis-system:latest',
                            'ports': [
                                {
                                    'containerPort': 8080
                                }
                            ],
                            'env': [
                                {
                                    'name': 'DATABASE_PATH',
                                    'value': '/data/pricing_analysis.db'
                                }
                            ],
                            'volumeMounts': [
                                {
                                    'name': 'data-volume',
                                    'mountPath': '/data'
                                }
                            ],
                            'resources': {
                                'requests': {
                                    'memory': '256Mi',
                                    'cpu': '250m'
                                },
                                'limits': {
                                    'memory': '512Mi',
                                    'cpu': '500m'
                                }
                            },
                            'livenessProbe': {
                                'httpGet': {
                                    'path': '/api/status',
                                    'port': 8080
                                },
                                'initialDelaySeconds': 30,
                                'periodSeconds': 10
                            },
                            'readinessProbe': {
                                'httpGet': {
                                    'path': '/api/status',
                                    'port': 8080
                                },
                                'initialDelaySeconds': 5,
                                'periodSeconds': 5
                            }
                        }
                    ],
                    'volumes': [
                        {
                            'name': 'data-volume',
                            'persistentVolumeClaim': {
                                'claimName': 'pricing-analysis-data'
                            }
                        }
                    ]
                }
            }
        }
    }
    
    # Service manifest
    service_manifest = {
        'apiVersion': 'v1',
        'kind': 'Service',
        'metadata': {
            'name': 'pricing-analysis-service'
        },
        'spec': {
            'selector': {
                'app': 'pricing-analysis-system'
            },
            'ports': [
                {
                    'port': 80,
                    'targetPort': 8080
                }
            ],
            'type': 'LoadBalancer'
        }
    }
    
    # PersistentVolumeClaim manifest
    pvc_manifest = {
        'apiVersion': 'v1',
        'kind': 'PersistentVolumeClaim',
        'metadata': {
            'name': 'pricing-analysis-data'
        },
        'spec': {
            'accessModes': ['ReadWriteOnce'],
            'resources': {
                'requests': {
                    'storage': '10Gi'
                }
            }
        }
    }
    
    # Save manifests
    with open('k8s-deployment.yaml', 'w') as f:
        yaml.dump(deployment_manifest, f, default_flow_style=False)
    
    with open('k8s-service.yaml', 'w') as f:
        yaml.dump(service_manifest, f, default_flow_style=False)
    
    with open('k8s-pvc.yaml', 'w') as f:
        yaml.dump(pvc_manifest, f, default_flow_style=False)
    
    logger.info("Kubernetes manifests created")

def main():
    """Main deployment function"""
    print("=" * 60)
    print("COMPETITIVE PRICING ANALYSIS SYSTEM - DEPLOYMENT")
    print("=" * 60)
    
    # Create deployment artifacts
    print("\n1. Creating deployment artifacts...")
    create_dockerfile()
    create_kubernetes_manifests()
    
    # Initialize deployment manager
    print("\n2. Initializing deployment manager...")
    deployment_manager = DeploymentManager()
    
    # Deploy application
    print("\n3. Deploying application...")
    if deployment_manager.deploy():
        print("✓ Deployment successful")
    else:
        print("✗ Deployment failed")
        return
    
    # Start monitoring
    print("\n4. Starting monitoring...")
    deployment_manager.start_monitoring()
    
    # Start backup scheduler
    print("\n5. Starting backup scheduler...")
    deployment_manager.start_backup_scheduler()
    
    # Show deployment status
    print("\n6. Deployment Status:")
    status = deployment_manager.get_deployment_status()
    print(json.dumps(status, indent=2))
    
    print("\n" + "=" * 60)
    print("DEPLOYMENT COMPLETED")
    print("=" * 60)
    
    # Keep running for monitoring
    try:
        while True:
            time.sleep(60)
    except KeyboardInterrupt:
        print("\nShutting down...")

if __name__ == '__main__':
    main()






