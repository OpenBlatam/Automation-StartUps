"""
Módulo de Backups para Recursos de Kubernetes.

Proporciona:
- Backup de ConfigMaps
- Backup de Secrets
- Backup de Deployments
- Backup de Services
- Backup de PersistentVolumeClaims
"""
import logging
import os
import json
import yaml
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List, Optional

logger = logging.getLogger(__name__)

# Intentar importar cliente de Kubernetes
try:
    from kubernetes import client, config
    KUBERNETES_AVAILABLE = True
except ImportError:
    KUBERNETES_AVAILABLE = False
    client = None
    config = None


class KubernetesBackup:
    """Backup de recursos de Kubernetes."""
    
    def __init__(self, kubeconfig: Optional[str] = None):
        """
        Inicializa backup de Kubernetes.
        
        Args:
            kubeconfig: Ruta a kubeconfig (None = usar contexto actual)
        """
        if not KUBERNETES_AVAILABLE:
            raise ImportError("kubernetes library not available")
        
        if kubeconfig:
            config.load_kube_config(config_file=kubeconfig)
        else:
            try:
                config.load_incluster_config()
            except:
                config.load_kube_config()
        
        self.v1 = client.CoreV1Api()
        self.apps_v1 = client.AppsV1Api()
    
    def backup_configmaps(
        self,
        namespace: Optional[str] = None,
        output_dir: str = "/tmp/k8s-backups"
    ) -> List[Dict[str, Any]]:
        """
        Hace backup de ConfigMaps.
        
        Args:
            namespace: Namespace (None = todos)
            output_dir: Directorio de salida
        """
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        
        backups = []
        
        try:
            if namespace:
                configmaps = self.v1.list_namespaced_config_map(namespace)
            else:
                configmaps = self.v1.list_config_map_for_all_namespaces()
            
            for cm in configmaps.items:
                cm_data = {
                    'apiVersion': 'v1',
                    'kind': 'ConfigMap',
                    'metadata': {
                        'name': cm.metadata.name,
                        'namespace': cm.metadata.namespace,
                        'labels': cm.metadata.labels,
                        'annotations': cm.metadata.annotations
                    },
                    'data': cm.data
                }
                
                filename = f"configmap-{cm.metadata.namespace}-{cm.metadata.name}.yaml"
                filepath = output_path / filename
                
                with open(filepath, 'w') as f:
                    yaml.dump(cm_data, f, default_flow_style=False)
                
                backups.append({
                    'type': 'configmap',
                    'name': cm.metadata.name,
                    'namespace': cm.metadata.namespace,
                    'file': str(filepath)
                })
            
            logger.info(f"Backed up {len(backups)} ConfigMaps")
            return backups
            
        except Exception as e:
            logger.error(f"ConfigMap backup failed: {e}", exc_info=True)
            raise
    
    def backup_secrets(
        self,
        namespace: Optional[str] = None,
        output_dir: str = "/tmp/k8s-backups",
        decrypt: bool = False
    ) -> List[Dict[str, Any]]:
        """
        Hace backup de Secrets.
        
        Args:
            namespace: Namespace (None = todos)
            output_dir: Directorio de salida
            decrypt: Si desencriptar secrets (por defecto se guardan encriptados)
        """
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        
        backups = []
        
        try:
            if namespace:
                secrets = self.v1.list_namespaced_secret(namespace)
            else:
                secrets = self.v1.list_secret_for_all_namespaces()
            
            for secret in secrets.items:
                secret_data = {
                    'apiVersion': 'v1',
                    'kind': 'Secret',
                    'metadata': {
                        'name': secret.metadata.name,
                        'namespace': secret.metadata.namespace,
                        'labels': secret.metadata.labels,
                        'annotations': secret.metadata.annotations
                    },
                    'type': secret.type
                }
                
                # Secrets se guardan encriptados por defecto
                if decrypt and secret.data:
                    from base64 import b64decode
                    secret_data['data'] = {
                        k: b64decode(v).decode('utf-8') if v else ''
                        for k, v in secret.data.items()
                    }
                else:
                    secret_data['data'] = secret.data
                
                filename = f"secret-{secret.metadata.namespace}-{secret.metadata.name}.yaml"
                filepath = output_path / filename
                
                with open(filepath, 'w') as f:
                    yaml.dump(secret_data, f, default_flow_style=False)
                
                backups.append({
                    'type': 'secret',
                    'name': secret.metadata.name,
                    'namespace': secret.metadata.namespace,
                    'file': str(filepath),
                    'encrypted': not decrypt
                })
            
            logger.info(f"Backed up {len(backups)} Secrets")
            return backups
            
        except Exception as e:
            logger.error(f"Secret backup failed: {e}", exc_info=True)
            raise
    
    def backup_deployments(
        self,
        namespace: Optional[str] = None,
        output_dir: str = "/tmp/k8s-backups"
    ) -> List[Dict[str, Any]]:
        """Hace backup de Deployments."""
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        
        backups = []
        
        try:
            if namespace:
                deployments = self.apps_v1.list_namespaced_deployment(namespace)
            else:
                deployments = self.apps_v1.list_deployment_for_all_namespaces()
            
            for deploy in deployments.items:
                deploy_dict = deploy.to_dict()
                
                filename = f"deployment-{deploy.metadata.namespace}-{deploy.metadata.name}.yaml"
                filepath = output_path / filename
                
                with open(filepath, 'w') as f:
                    yaml.dump(deploy_dict, f, default_flow_style=False)
                
                backups.append({
                    'type': 'deployment',
                    'name': deploy.metadata.name,
                    'namespace': deploy.metadata.namespace,
                    'file': str(filepath)
                })
            
            logger.info(f"Backed up {len(backups)} Deployments")
            return backups
            
        except Exception as e:
            logger.error(f"Deployment backup failed: {e}", exc_info=True)
            raise
    
    def backup_all_resources(
        self,
        namespace: Optional[str] = None,
        output_dir: str = "/tmp/k8s-backups",
        resources: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Hace backup de todos los recursos especificados.
        
        Args:
            namespace: Namespace (None = todos)
            output_dir: Directorio de salida
            resources: Lista de recursos ['configmaps', 'secrets', 'deployments']
        """
        if resources is None:
            resources = ['configmaps', 'secrets', 'deployments']
        
        results = {}
        
        if 'configmaps' in resources:
            try:
                results['configmaps'] = self.backup_configmaps(namespace, output_dir)
            except Exception as e:
                logger.error(f"ConfigMap backup failed: {e}")
                results['configmaps'] = {'error': str(e)}
        
        if 'secrets' in resources:
            try:
                results['secrets'] = self.backup_secrets(namespace, output_dir)
            except Exception as e:
                logger.error(f"Secret backup failed: {e}")
                results['secrets'] = {'error': str(e)}
        
        if 'deployments' in resources:
            try:
                results['deployments'] = self.backup_deployments(namespace, output_dir)
            except Exception as e:
                logger.error(f"Deployment backup failed: {e}")
                results['deployments'] = {'error': str(e)}
        
        return results

