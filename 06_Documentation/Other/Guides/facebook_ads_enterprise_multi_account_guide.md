---
title: "Facebook Ads Enterprise Multi Account Guide"
category: "06_documentation"
tags: ["guide"]
created: "2025-10-29"
path: "06_documentation/Other/Guides/facebook_ads_enterprise_multi_account_guide.md"
---

# Guía de Características Enterprise y Multi-Cuenta para Facebook Ads
## Gestión de Múltiples Cuentas y Funcionalidades Empresariales

---

## 1. Introducción a las Características Enterprise

Esta guía proporciona técnicas avanzadas para gestionar múltiples cuentas de Facebook Ads y implementar funcionalidades empresariales, incluyendo gestión centralizada, control de acceso, compliance, escalabilidad y optimización a nivel enterprise. Está diseñada para organizaciones grandes que manejan múltiples cuentas publicitarias.

### Objetivos de las Características Enterprise
- Gestionar múltiples cuentas de manera centralizada
- Implementar control de acceso granular
- Asegurar compliance y auditoría
- Escalar operaciones a nivel enterprise
- Optimizar performance a través de múltiples cuentas

---

## 2. Fundamentos de Gestión Multi-Cuenta

### 2.1 Arquitectura Enterprise

**Estructura de Cuentas:**
```
Business Manager (Nivel Superior)
├── Ad Accounts (Cuentas Publicitarias)
├── Pages (Páginas de Facebook)
├── Instagram Accounts (Cuentas de Instagram)
├── Apps (Aplicaciones)
└── Catalogs (Catálogos)
```

**Jerarquía de Permisos:**
```
Admin: Control total sobre Business Manager
Editor: Puede editar configuraciones
Advertiser: Puede crear y gestionar anuncios
Analyst: Solo puede ver datos y reportes
```

**Gestión de Recursos:**
```
Centralized Billing: Facturación centralizada
Shared Audiences: Audiencias compartidas
Cross-Account Optimization: Optimización entre cuentas
Unified Reporting: Reportes unificados
```

### 2.2 Tipos de Configuraciones Enterprise

**Configuración Centralizada:**
```
Single Business Manager: Un Business Manager para toda la organización
Centralized Control: Control centralizado de todas las cuentas
Unified Billing: Facturación unificada
Shared Resources: Recursos compartidos entre cuentas
```

**Configuración Distribuida:**
```
Multiple Business Managers: Múltiples Business Managers por región/departamento
Distributed Control: Control distribuido por región
Local Billing: Facturación local
Independent Resources: Recursos independientes
```

**Configuración Híbrida:**
```
Regional Business Managers: Business Managers por región
Centralized Oversight: Supervisión centralizada
Mixed Billing: Facturación mixta
Selective Sharing: Compartir recursos selectivamente
```

---

## 3. Gestión Multi-Cuenta

### 3.1 Sistema de Gestión Centralizada

**Gestor de Múltiples Cuentas:**
```python
import requests
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import json
from typing import Dict, List, Optional
import logging

class EnterpriseAccountManager:
    def __init__(self, business_manager_id: str, access_token: str):
        self.business_manager_id = business_manager_id
        self.access_token = access_token
        self.base_url = "https://graph.facebook.com/v18.0"
        self.accounts = {}
        self.users = {}
        self.roles = {}
        self.setup_logging()
        
    def setup_logging(self):
        """Configurar logging para auditoría"""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('enterprise_audit.log'),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)
    
    def get_all_ad_accounts(self) -> Dict:
        """Obtener todas las cuentas publicitarias"""
        try:
            url = f"{self.base_url}/{self.business_manager_id}/owned_ad_accounts"
            params = {
                'access_token': self.access_token,
                'fields': 'id,name,account_status,currency,timezone_name,amount_spent,balance'
            }
            
            response = requests.get(url, params=params)
            data = response.json()
            
            if data.get('data'):
                for account in data['data']:
                    self.accounts[account['id']] = account
                
                self.logger.info(f"Retrieved {len(data['data'])} ad accounts")
                return data
            else:
                self.logger.warning("No ad accounts found")
                return {}
                
        except Exception as e:
            self.logger.error(f"Error retrieving ad accounts: {e}")
            return {}
    
    def get_account_permissions(self, account_id: str) -> Dict:
        """Obtener permisos de una cuenta"""
        try:
            url = f"{self.base_url}/{account_id}/users"
            params = {
                'access_token': self.access_token,
                'fields': 'id,name,role,permissions'
            }
            
            response = requests.get(url, params=params)
            data = response.json()
            
            if data.get('data'):
                self.logger.info(f"Retrieved permissions for account {account_id}")
                return data
            else:
                self.logger.warning(f"No permissions found for account {account_id}")
                return {}
                
        except Exception as e:
            self.logger.error(f"Error retrieving permissions for account {account_id}: {e}")
            return {}
    
    def add_user_to_account(self, account_id: str, user_id: str, role: str) -> bool:
        """Agregar usuario a una cuenta"""
        try:
            url = f"{self.base_url}/{account_id}/users"
            data = {
                'user': user_id,
                'role': role,
                'access_token': self.access_token
            }
            
            response = requests.post(url, data=data)
            
            if response.status_code == 200:
                self.logger.info(f"User {user_id} added to account {account_id} with role {role}")
                return True
            else:
                self.logger.error(f"Failed to add user {user_id} to account {account_id}: {response.text}")
                return False
                
        except Exception as e:
            self.logger.error(f"Error adding user {user_id} to account {account_id}: {e}")
            return False
    
    def remove_user_from_account(self, account_id: str, user_id: str) -> bool:
        """Remover usuario de una cuenta"""
        try:
            url = f"{self.base_url}/{account_id}/users"
            data = {
                'user': user_id,
                'access_token': self.access_token
            }
            
            response = requests.delete(url, data=data)
            
            if response.status_code == 200:
                self.logger.info(f"User {user_id} removed from account {account_id}")
                return True
            else:
                self.logger.error(f"Failed to remove user {user_id} from account {account_id}: {response.text}")
                return False
                
        except Exception as e:
            self.logger.error(f"Error removing user {user_id} from account {account_id}: {e}")
            return False
    
    def get_cross_account_insights(self, start_date: str, end_date: str) -> pd.DataFrame:
        """Obtener insights de todas las cuentas"""
        all_insights = []
        
        for account_id in self.accounts.keys():
            try:
                url = f"{self.base_url}/{account_id}/insights"
                params = {
                    'access_token': self.access_token,
                    'fields': 'impressions,clicks,spend,ctr,cpc,cpm,conversions,cost_per_conversion',
                    'time_range': f'{{"since":"{start_date}","until":"{end_date}"}}',
                    'level': 'account'
                }
                
                response = requests.get(url, params=params)
                data = response.json()
                
                if data.get('data'):
                    for insight in data['data']:
                        insight['account_id'] = account_id
                        insight['account_name'] = self.accounts[account_id]['name']
                        all_insights.append(insight)
                
            except Exception as e:
                self.logger.error(f"Error retrieving insights for account {account_id}: {e}")
        
        if all_insights:
            df = pd.DataFrame(all_insights)
            self.logger.info(f"Retrieved insights for {len(df)} account-date combinations")
            return df
        else:
            self.logger.warning("No insights retrieved")
            return pd.DataFrame()
    
    def create_shared_audience(self, name: str, description: str, source_account_id: str) -> Optional[str]:
        """Crear audiencia compartida"""
        try:
            # Obtener audiencia de cuenta fuente
            url = f"{self.base_url}/{source_account_id}/customaudiences"
            params = {
                'access_token': self.access_token,
                'fields': 'id,name,description,approximate_count'
            }
            
            response = requests.get(url, params=params)
            data = response.json()
            
            if data.get('data'):
                # Crear audiencia compartida en Business Manager
                share_url = f"{self.base_url}/{self.business_manager_id}/shared_audiences"
                share_data = {
                    'name': name,
                    'description': description,
                    'source_audience_id': data['data'][0]['id'],
                    'access_token': self.access_token
                }
                
                share_response = requests.post(share_url, data=share_data)
                
                if share_response.status_code == 200:
                    shared_audience_id = share_response.json()['id']
                    self.logger.info(f"Created shared audience {name} with ID {shared_audience_id}")
                    return shared_audience_id
                else:
                    self.logger.error(f"Failed to create shared audience: {share_response.text}")
                    return None
            else:
                self.logger.warning(f"No audiences found in source account {source_account_id}")
                return None
                
        except Exception as e:
            self.logger.error(f"Error creating shared audience: {e}")
            return None
    
    def distribute_shared_audience(self, shared_audience_id: str, target_accounts: List[str]) -> Dict:
        """Distribuir audiencia compartida a cuentas objetivo"""
        results = {}
        
        for account_id in target_accounts:
            try:
                url = f"{self.base_url}/{account_id}/customaudiences"
                data = {
                    'shared_audience_id': shared_audience_id,
                    'access_token': self.access_token
                }
                
                response = requests.post(url, data=data)
                
                if response.status_code == 200:
                    results[account_id] = {'success': True, 'audience_id': response.json()['id']}
                    self.logger.info(f"Shared audience distributed to account {account_id}")
                else:
                    results[account_id] = {'success': False, 'error': response.text}
                    self.logger.error(f"Failed to distribute audience to account {account_id}: {response.text}")
                    
            except Exception as e:
                results[account_id] = {'success': False, 'error': str(e)}
                self.logger.error(f"Error distributing audience to account {account_id}: {e}")
        
        return results
    
    def get_unified_report(self, start_date: str, end_date: str) -> Dict:
        """Generar reporte unificado de todas las cuentas"""
        # Obtener insights de todas las cuentas
        insights_df = self.get_cross_account_insights(start_date, end_date)
        
        if insights_df.empty:
            return {'error': 'No data available'}
        
        # Calcular métricas agregadas
        total_spend = insights_df['spend'].sum()
        total_impressions = insights_df['impressions'].sum()
        total_clicks = insights_df['clicks'].sum()
        total_conversions = insights_df['conversions'].sum()
        
        # Calcular métricas promedio
        avg_ctr = (total_clicks / total_impressions * 100) if total_impressions > 0 else 0
        avg_cpc = (total_spend / total_clicks) if total_clicks > 0 else 0
        avg_cpa = (total_spend / total_conversions) if total_conversions > 0 else 0
        
        # Métricas por cuenta
        account_metrics = insights_df.groupby('account_name').agg({
            'spend': 'sum',
            'impressions': 'sum',
            'clicks': 'sum',
            'conversions': 'sum'
        }).reset_index()
        
        account_metrics['ctr'] = (account_metrics['clicks'] / account_metrics['impressions'] * 100).fillna(0)
        account_metrics['cpc'] = (account_metrics['spend'] / account_metrics['clicks']).fillna(0)
        account_metrics['cpa'] = (account_metrics['spend'] / account_metrics['conversions']).fillna(0)
        
        # Identificar mejores y peores cuentas
        best_account = account_metrics.loc[account_metrics['cpa'].idxmin()]
        worst_account = account_metrics.loc[account_metrics['cpa'].idxmax()]
        
        report = {
            'summary': {
                'total_spend': total_spend,
                'total_impressions': total_impressions,
                'total_clicks': total_clicks,
                'total_conversions': total_conversions,
                'avg_ctr': avg_ctr,
                'avg_cpc': avg_cpc,
                'avg_cpa': avg_cpa
            },
            'account_metrics': account_metrics.to_dict('records'),
            'best_account': best_account.to_dict(),
            'worst_account': worst_account.to_dict(),
            'date_range': f"{start_date} to {end_date}"
        }
        
        self.logger.info(f"Generated unified report for {len(account_metrics)} accounts")
        return report
    
    def optimize_cross_account_budgets(self, total_budget: float) -> Dict:
        """Optimizar presupuestos entre cuentas"""
        # Obtener insights recientes
        end_date = datetime.now().strftime('%Y-%m-%d')
        start_date = (datetime.now() - timedelta(days=7)).strftime('%Y-%m-%d')
        
        insights_df = self.get_cross_account_insights(start_date, end_date)
        
        if insights_df.empty:
            return {'error': 'No data available for optimization'}
        
        # Calcular performance por cuenta
        account_performance = insights_df.groupby('account_name').agg({
            'spend': 'sum',
            'conversions': 'sum'
        }).reset_index()
        
        account_performance['cpa'] = account_performance['spend'] / account_performance['conversions']
        account_performance['efficiency_score'] = 1 / account_performance['cpa']  # Inverso del CPA
        
        # Normalizar scores de eficiencia
        account_performance['normalized_score'] = (
            account_performance['efficiency_score'] / account_performance['efficiency_score'].sum()
        )
        
        # Asignar presupuestos basándose en eficiencia
        account_performance['recommended_budget'] = (
            account_performance['normalized_score'] * total_budget
        )
        
        # Crear recomendaciones
        recommendations = {}
        for _, row in account_performance.iterrows():
            recommendations[row['account_name']] = {
                'current_spend': row['spend'],
                'recommended_budget': row['recommended_budget'],
                'budget_change': row['recommended_budget'] - row['spend'],
                'efficiency_score': row['efficiency_score'],
                'cpa': row['cpa']
            }
        
        self.logger.info(f"Generated budget optimization recommendations for {len(recommendations)} accounts")
        return recommendations

# Uso del gestor de cuentas enterprise
if __name__ == "__main__":
    # Configurar credenciales
    BUSINESS_MANAGER_ID = "your_business_manager_id"
    ACCESS_TOKEN = "your_access_token"
    
    # Crear gestor de cuentas
    account_manager = EnterpriseAccountManager(BUSINESS_MANAGER_ID, ACCESS_TOKEN)
    
    # Obtener todas las cuentas
    accounts = account_manager.get_all_ad_accounts()
    
    # Generar reporte unificado
    start_date = (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d')
    end_date = datetime.now().strftime('%Y-%m-%d')
    
    unified_report = account_manager.get_unified_report(start_date, end_date)
    print("Unified Report:", json.dumps(unified_report, indent=2))
    
    # Optimizar presupuestos
    budget_recommendations = account_manager.optimize_cross_account_budgets(100000)
    print("Budget Recommendations:", json.dumps(budget_recommendations, indent=2))
```

### 3.2 Sistema de Control de Acceso

**Gestor de Permisos:**
```python
import requests
import json
from typing import Dict, List, Optional
from datetime import datetime
import logging

class AccessControlManager:
    def __init__(self, business_manager_id: str, access_token: str):
        self.business_manager_id = business_manager_id
        self.access_token = access_token
        self.base_url = "https://graph.facebook.com/v18.0"
        self.role_permissions = self.define_role_permissions()
        self.setup_logging()
        
    def setup_logging(self):
        """Configurar logging para auditoría de acceso"""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('access_control_audit.log'),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)
    
    def define_role_permissions(self) -> Dict:
        """Definir permisos por rol"""
        return {
            'ADMIN': {
                'can_create_campaigns': True,
                'can_edit_campaigns': True,
                'can_delete_campaigns': True,
                'can_view_insights': True,
                'can_manage_users': True,
                'can_manage_billing': True,
                'can_export_data': True
            },
            'EDITOR': {
                'can_create_campaigns': True,
                'can_edit_campaigns': True,
                'can_delete_campaigns': False,
                'can_view_insights': True,
                'can_manage_users': False,
                'can_manage_billing': False,
                'can_export_data': True
            },
            'ADVERTISER': {
                'can_create_campaigns': True,
                'can_edit_campaigns': True,
                'can_delete_campaigns': False,
                'can_view_insights': True,
                'can_manage_users': False,
                'can_manage_billing': False,
                'can_export_data': False
            },
            'ANALYST': {
                'can_create_campaigns': False,
                'can_edit_campaigns': False,
                'can_delete_campaigns': False,
                'can_view_insights': True,
                'can_manage_users': False,
                'can_manage_billing': False,
                'can_export_data': True
            }
        }
    
    def create_user_group(self, name: str, description: str, role: str) -> Optional[str]:
        """Crear grupo de usuarios"""
        try:
            url = f"{self.base_url}/{self.business_manager_id}/user_groups"
            data = {
                'name': name,
                'description': description,
                'role': role,
                'access_token': self.access_token
            }
            
            response = requests.post(url, data=data)
            
            if response.status_code == 200:
                group_id = response.json()['id']
                self.logger.info(f"Created user group {name} with ID {group_id}")
                return group_id
            else:
                self.logger.error(f"Failed to create user group: {response.text}")
                return None
                
        except Exception as e:
            self.logger.error(f"Error creating user group: {e}")
            return None
    
    def add_user_to_group(self, group_id: str, user_id: str) -> bool:
        """Agregar usuario a grupo"""
        try:
            url = f"{self.base_url}/{group_id}/users"
            data = {
                'user': user_id,
                'access_token': self.access_token
            }
            
            response = requests.post(url, data=data)
            
            if response.status_code == 200:
                self.logger.info(f"User {user_id} added to group {group_id}")
                return True
            else:
                self.logger.error(f"Failed to add user {user_id} to group {group_id}: {response.text}")
                return False
                
        except Exception as e:
            self.logger.error(f"Error adding user to group: {e}")
            return False
    
    def assign_group_to_account(self, group_id: str, account_id: str, role: str) -> bool:
        """Asignar grupo a cuenta publicitaria"""
        try:
            url = f"{self.base_url}/{account_id}/user_groups"
            data = {
                'user_group': group_id,
                'role': role,
                'access_token': self.access_token
            }
            
            response = requests.post(url, data=data)
            
            if response.status_code == 200:
                self.logger.info(f"Group {group_id} assigned to account {account_id} with role {role}")
                return True
            else:
                self.logger.error(f"Failed to assign group to account: {response.text}")
                return False
                
        except Exception as e:
            self.logger.error(f"Error assigning group to account: {e}")
            return False
    
    def check_user_permissions(self, user_id: str, account_id: str, action: str) -> bool:
        """Verificar permisos de usuario para una acción específica"""
        try:
            # Obtener rol del usuario en la cuenta
            url = f"{self.base_url}/{account_id}/users"
            params = {
                'access_token': self.access_token,
                'fields': 'id,role'
            }
            
            response = requests.get(url, params=params)
            data = response.json()
            
            if data.get('data'):
                for user in data['data']:
                    if user['id'] == user_id:
                        role = user['role']
                        permissions = self.role_permissions.get(role, {})
                        
                        if action in permissions:
                            has_permission = permissions[action]
                            self.logger.info(f"User {user_id} permission for {action}: {has_permission}")
                            return has_permission
                        else:
                            self.logger.warning(f"Action {action} not defined for role {role}")
                            return False
            
            self.logger.warning(f"User {user_id} not found in account {account_id}")
            return False
            
        except Exception as e:
            self.logger.error(f"Error checking user permissions: {e}")
            return False
    
    def audit_user_access(self, account_id: str) -> Dict:
        """Auditar acceso de usuarios a una cuenta"""
        try:
            url = f"{self.base_url}/{account_id}/users"
            params = {
                'access_token': self.access_token,
                'fields': 'id,name,role,permissions,created_time'
            }
            
            response = requests.get(url, params=params)
            data = response.json()
            
            if data.get('data'):
                audit_results = {
                    'account_id': account_id,
                    'audit_date': datetime.now().isoformat(),
                    'users': []
                }
                
                for user in data['data']:
                    user_info = {
                        'user_id': user['id'],
                        'name': user.get('name', 'Unknown'),
                        'role': user['role'],
                        'permissions': user.get('permissions', []),
                        'created_time': user.get('created_time', 'Unknown'),
                        'permissions_summary': self.role_permissions.get(user['role'], {})
                    }
                    audit_results['users'].append(user_info)
                
                self.logger.info(f"Audited access for {len(audit_results['users'])} users in account {account_id}")
                return audit_results
            else:
                self.logger.warning(f"No users found in account {account_id}")
                return {'error': 'No users found'}
                
        except Exception as e:
            self.logger.error(f"Error auditing user access: {e}")
            return {'error': str(e)}
    
    def create_access_policy(self, policy_name: str, rules: Dict) -> Optional[str]:
        """Crear política de acceso"""
        try:
            # Guardar política en archivo (en implementación real, usar base de datos)
            policy = {
                'name': policy_name,
                'rules': rules,
                'created_date': datetime.now().isoformat(),
                'status': 'active'
            }
            
            filename = f"access_policy_{policy_name.replace(' ', '_')}.json"
            with open(filename, 'w') as f:
                json.dump(policy, f, indent=2)
            
            self.logger.info(f"Created access policy {policy_name}")
            return filename
            
        except Exception as e:
            self.logger.error(f"Error creating access policy: {e}")
            return None
    
    def enforce_access_policy(self, policy_name: str, user_id: str, account_id: str, action: str) -> bool:
        """Aplicar política de acceso"""
        try:
            # Cargar política
            filename = f"access_policy_{policy_name.replace(' ', '_')}.json"
            with open(filename, 'r') as f:
                policy = json.load(f)
            
            rules = policy['rules']
            
            # Verificar reglas
            for rule in rules:
                if self.evaluate_rule(rule, user_id, account_id, action):
                    self.logger.info(f"Access policy {policy_name} applied: {rule['action']}")
                    return rule['action'] == 'allow'
            
            # Regla por defecto
            default_action = rules.get('default', 'deny')
            self.logger.info(f"Default access policy applied: {default_action}")
            return default_action == 'allow'
            
        except Exception as e:
            self.logger.error(f"Error enforcing access policy: {e}")
            return False
    
    def evaluate_rule(self, rule: Dict, user_id: str, account_id: str, action: str) -> bool:
        """Evaluar regla de acceso"""
        # Verificar condiciones de la regla
        if 'conditions' in rule:
            for condition in rule['conditions']:
                if not self.evaluate_condition(condition, user_id, account_id, action):
                    return False
        
        return True
    
    def evaluate_condition(self, condition: Dict, user_id: str, account_id: str, action: str) -> bool:
        """Evaluar condición de acceso"""
        condition_type = condition['type']
        
        if condition_type == 'user_role':
            # Verificar rol del usuario
            user_role = self.get_user_role(user_id, account_id)
            return user_role == condition['value']
        
        elif condition_type == 'time_based':
            # Verificar restricciones de tiempo
            current_hour = datetime.now().hour
            return condition['start_hour'] <= current_hour <= condition['end_hour']
        
        elif condition_type == 'action_type':
            # Verificar tipo de acción
            return action == condition['value']
        
        return True
    
    def get_user_role(self, user_id: str, account_id: str) -> Optional[str]:
        """Obtener rol de usuario en una cuenta"""
        try:
            url = f"{self.base_url}/{account_id}/users"
            params = {
                'access_token': self.access_token,
                'fields': 'id,role'
            }
            
            response = requests.get(url, params=params)
            data = response.json()
            
            if data.get('data'):
                for user in data['data']:
                    if user['id'] == user_id:
                        return user['role']
            
            return None
            
        except Exception as e:
            self.logger.error(f"Error getting user role: {e}")
            return None

# Uso del gestor de control de acceso
if __name__ == "__main__":
    # Configurar credenciales
    BUSINESS_MANAGER_ID = "your_business_manager_id"
    ACCESS_TOKEN = "your_access_token"
    
    # Crear gestor de control de acceso
    access_manager = AccessControlManager(BUSINESS_MANAGER_ID, ACCESS_TOKEN)
    
    # Crear grupo de usuarios
    group_id = access_manager.create_user_group(
        name="Marketing Team",
        description="Marketing team members",
        role="ADVERTISER"
    )
    
    # Crear política de acceso
    policy_rules = {
        'default': 'deny',
        'rules': [
            {
                'conditions': [
                    {'type': 'user_role', 'value': 'ADMIN'}
                ],
                'action': 'allow'
            },
            {
                'conditions': [
                    {'type': 'user_role', 'value': 'ADVERTISER'},
                    {'type': 'time_based', 'start_hour': 9, 'end_hour': 17}
                ],
                'action': 'allow'
            }
        ]
    }
    
    policy_file = access_manager.create_access_policy("Marketing Policy", policy_rules)
    
    # Auditar acceso
    audit_results = access_manager.audit_user_access("account_id")
    print("Audit Results:", json.dumps(audit_results, indent=2))
```

---

## 4. Compliance y Auditoría

### 4.1 Sistema de Compliance

**Gestor de Compliance:**
```python
import requests
import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import logging

class ComplianceManager:
    def __init__(self, business_manager_id: str, access_token: str):
        self.business_manager_id = business_manager_id
        self.access_token = access_token
        self.base_url = "https://graph.facebook.com/v18.0"
        self.compliance_rules = self.load_compliance_rules()
        self.setup_logging()
        
    def setup_logging(self):
        """Configurar logging para compliance"""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('compliance_audit.log'),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)
    
    def load_compliance_rules(self) -> Dict:
        """Cargar reglas de compliance"""
        return {
            'data_retention': {
                'max_retention_days': 365,
                'required_encryption': True,
                'audit_frequency': 'monthly'
            },
            'access_control': {
                'max_inactive_days': 90,
                'require_mfa': True,
                'role_review_frequency': 'quarterly'
            },
            'advertising_policies': {
                'prohibited_content': ['discrimination', 'misleading_claims', 'illegal_products'],
                'required_disclaimers': ['privacy_policy', 'terms_of_service'],
                'review_frequency': 'weekly'
            },
            'financial_compliance': {
                'max_daily_spend': 10000,
                'approval_threshold': 5000,
                'audit_frequency': 'daily'
            }
        }
    
    def check_data_retention_compliance(self, account_id: str) -> Dict:
        """Verificar compliance de retención de datos"""
        try:
            # Obtener datos de la cuenta
            url = f"{self.base_url}/{account_id}/insights"
            params = {
                'access_token': self.access_token,
                'fields': 'date_start,date_stop',
                'time_range': '{"since":"2020-01-01","until":"2024-12-31"}',
                'level': 'account'
            }
            
            response = requests.get(url, params=params)
            data = response.json()
            
            if data.get('data'):
                # Verificar retención de datos
                max_retention_days = self.compliance_rules['data_retention']['max_retention_days']
                cutoff_date = datetime.now() - timedelta(days=max_retention_days)
                
                compliance_results = {
                    'account_id': account_id,
                    'check_date': datetime.now().isoformat(),
                    'max_retention_days': max_retention_days,
                    'cutoff_date': cutoff_date.isoformat(),
                    'data_points_checked': len(data['data']),
                    'compliant': True,
                    'violations': []
                }
                
                for insight in data['data']:
                    data_date = datetime.strptime(insight['date_start'], '%Y-%m-%d')
                    if data_date < cutoff_date:
                        compliance_results['compliant'] = False
                        compliance_results['violations'].append({
                            'date': insight['date_start'],
                            'violation_type': 'data_retention_exceeded',
                            'days_old': (datetime.now() - data_date).days
                        })
                
                self.logger.info(f"Data retention compliance check completed for account {account_id}")
                return compliance_results
            else:
                return {'error': 'No data available for compliance check'}
                
        except Exception as e:
            self.logger.error(f"Error checking data retention compliance: {e}")
            return {'error': str(e)}
    
    def check_access_control_compliance(self, account_id: str) -> Dict:
        """Verificar compliance de control de acceso"""
        try:
            # Obtener usuarios de la cuenta
            url = f"{self.base_url}/{account_id}/users"
            params = {
                'access_token': self.access_token,
                'fields': 'id,name,role,permissions,created_time'
            }
            
            response = requests.get(url, params=params)
            data = response.json()
            
            if data.get('data'):
                compliance_results = {
                    'account_id': account_id,
                    'check_date': datetime.now().isoformat(),
                    'total_users': len(data['data']),
                    'compliant': True,
                    'violations': []
                }
                
                max_inactive_days = self.compliance_rules['access_control']['max_inactive_days']
                cutoff_date = datetime.now() - timedelta(days=max_inactive_days)
                
                for user in data['data']:
                    # Verificar usuarios inactivos
                    if 'created_time' in user:
                        created_date = datetime.strptime(user['created_time'], '%Y-%m-%dT%H:%M:%S%z')
                        if created_date < cutoff_date:
                            compliance_results['violations'].append({
                                'user_id': user['id'],
                                'violation_type': 'inactive_user',
                                'days_inactive': (datetime.now() - created_date.replace(tzinfo=None)).days
                            })
                    
                    # Verificar roles apropiados
                    if user['role'] not in ['ADMIN', 'EDITOR', 'ADVERTISER', 'ANALYST']:
                        compliance_results['violations'].append({
                            'user_id': user['id'],
                            'violation_type': 'invalid_role',
                            'role': user['role']
                        })
                
                if compliance_results['violations']:
                    compliance_results['compliant'] = False
                
                self.logger.info(f"Access control compliance check completed for account {account_id}")
                return compliance_results
            else:
                return {'error': 'No users found for compliance check'}
                
        except Exception as e:
            self.logger.error(f"Error checking access control compliance: {e}")
            return {'error': str(e)}
    
    def check_advertising_policy_compliance(self, account_id: str) -> Dict:
        """Verificar compliance de políticas publicitarias"""
        try:
            # Obtener campañas de la cuenta
            url = f"{self.base_url}/{account_id}/campaigns"
            params = {
                'access_token': self.access_token,
                'fields': 'id,name,status,objective,created_time'
            }
            
            response = requests.get(url, params=params)
            data = response.json()
            
            if data.get('data'):
                compliance_results = {
                    'account_id': account_id,
                    'check_date': datetime.now().isoformat(),
                    'total_campaigns': len(data['data']),
                    'compliant': True,
                    'violations': []
                }
                
                prohibited_content = self.compliance_rules['advertising_policies']['prohibited_content']
                
                for campaign in data['data']:
                    # Verificar contenido prohibido en nombres de campaña
                    campaign_name = campaign['name'].lower()
                    for prohibited in prohibited_content:
                        if prohibited in campaign_name:
                            compliance_results['violations'].append({
                                'campaign_id': campaign['id'],
                                'violation_type': 'prohibited_content',
                                'content': prohibited,
                                'campaign_name': campaign['name']
                            })
                    
                    # Verificar estado de campaña
                    if campaign['status'] not in ['ACTIVE', 'PAUSED', 'DELETED']:
                        compliance_results['violations'].append({
                            'campaign_id': campaign['id'],
                            'violation_type': 'invalid_status',
                            'status': campaign['status']
                        })
                
                if compliance_results['violations']:
                    compliance_results['compliant'] = False
                
                self.logger.info(f"Advertising policy compliance check completed for account {account_id}")
                return compliance_results
            else:
                return {'error': 'No campaigns found for compliance check'}
                
        except Exception as e:
            self.logger.error(f"Error checking advertising policy compliance: {e}")
            return {'error': str(e)}
    
    def check_financial_compliance(self, account_id: str) -> Dict:
        """Verificar compliance financiero"""
        try:
            # Obtener insights de gasto
            url = f"{self.base_url}/{account_id}/insights"
            params = {
                'access_token': self.access_token,
                'fields': 'spend,date_start',
                'time_range': '{"since":"2024-01-01","until":"2024-12-31"}',
                'level': 'account'
            }
            
            response = requests.get(url, params=params)
            data = response.json()
            
            if data.get('data'):
                compliance_results = {
                    'account_id': account_id,
                    'check_date': datetime.now().isoformat(),
                    'compliant': True,
                    'violations': []
                }
                
                max_daily_spend = self.compliance_rules['financial_compliance']['max_daily_spend']
                approval_threshold = self.compliance_rules['financial_compliance']['approval_threshold']
                
                for insight in data['data']:
                    daily_spend = float(insight['spend'])
                    
                    # Verificar límite diario
                    if daily_spend > max_daily_spend:
                        compliance_results['violations'].append({
                            'date': insight['date_start'],
                            'violation_type': 'daily_spend_exceeded',
                            'spend': daily_spend,
                            'limit': max_daily_spend
                        })
                    
                    # Verificar umbral de aprobación
                    if daily_spend > approval_threshold:
                        compliance_results['violations'].append({
                            'date': insight['date_start'],
                            'violation_type': 'approval_threshold_exceeded',
                            'spend': daily_spend,
                            'threshold': approval_threshold
                        })
                
                if compliance_results['violations']:
                    compliance_results['compliant'] = False
                
                self.logger.info(f"Financial compliance check completed for account {account_id}")
                return compliance_results
            else:
                return {'error': 'No financial data available for compliance check'}
                
        except Exception as e:
            self.logger.error(f"Error checking financial compliance: {e}")
            return {'error': str(e)}
    
    def generate_compliance_report(self, account_ids: List[str]) -> Dict:
        """Generar reporte de compliance para múltiples cuentas"""
        report = {
            'report_date': datetime.now().isoformat(),
            'accounts_checked': len(account_ids),
            'overall_compliance': True,
            'account_results': {},
            'summary': {
                'data_retention_violations': 0,
                'access_control_violations': 0,
                'advertising_policy_violations': 0,
                'financial_violations': 0
            }
        }
        
        for account_id in account_ids:
            account_results = {
                'data_retention': self.check_data_retention_compliance(account_id),
                'access_control': self.check_access_control_compliance(account_id),
                'advertising_policies': self.check_advertising_policy_compliance(account_id),
                'financial': self.check_financial_compliance(account_id)
            }
            
            report['account_results'][account_id] = account_results
            
            # Contar violaciones
            for check_type, result in account_results.items():
                if not result.get('compliant', True):
                    report['overall_compliance'] = False
                    violation_count = len(result.get('violations', []))
                    report['summary'][f'{check_type}_violations'] += violation_count
        
        self.logger.info(f"Compliance report generated for {len(account_ids)} accounts")
        return report
    
    def create_compliance_dashboard(self, report: Dict) -> str:
        """Crear dashboard de compliance"""
        dashboard_html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Compliance Dashboard</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 20px; }}
                .header {{ background-color: #1877f2; color: white; padding: 20px; text-align: center; }}
                .summary {{ display: flex; justify-content: space-around; margin: 20px 0; }}
                .metric-card {{ background-color: #f0f2f5; padding: 20px; border-radius: 8px; text-align: center; }}
                .compliant {{ color: green; }}
                .non-compliant {{ color: red; }}
                .violations {{ background-color: #fff3cd; padding: 15px; border-radius: 8px; margin: 10px 0; }}
            </style>
        </head>
        <body>
            <div class="header">
                <h1>Compliance Dashboard</h1>
                <p>Report Date: {report['report_date']}</p>
            </div>
            
            <div class="summary">
                <div class="metric-card">
                    <h3>Overall Compliance</h3>
                    <p class="{'compliant' if report['overall_compliance'] else 'non-compliant'}">
                        {'✅ Compliant' if report['overall_compliance'] else '❌ Non-Compliant'}
                    </p>
                </div>
                <div class="metric-card">
                    <h3>Accounts Checked</h3>
                    <p>{report['accounts_checked']}</p>
                </div>
                <div class="metric-card">
                    <h3>Total Violations</h3>
                    <p>{sum(report['summary'].values())}</p>
                </div>
            </div>
            
            <h2>Violation Summary</h2>
            <ul>
                <li>Data Retention Violations: {report['summary']['data_retention_violations']}</li>
                <li>Access Control Violations: {report['summary']['access_control_violations']}</li>
                <li>Advertising Policy Violations: {report['summary']['advertising_policy_violations']}</li>
                <li>Financial Violations: {report['summary']['financial_violations']}</li>
            </ul>
            
            <h2>Account Details</h2>
        """
        
        for account_id, results in report['account_results'].items():
            dashboard_html += f"""
            <div class="violations">
                <h3>Account: {account_id}</h3>
            """
            
            for check_type, result in results.items():
                status = "✅ Compliant" if result.get('compliant', True) else "❌ Non-Compliant"
                dashboard_html += f"<p><strong>{check_type.replace('_', ' ').title()}:</strong> {status}</p>"
                
                if result.get('violations'):
                    dashboard_html += "<ul>"
                    for violation in result['violations']:
                        dashboard_html += f"<li>{violation.get('violation_type', 'Unknown')}: {violation}</li>"
                    dashboard_html += "</ul>"
            
            dashboard_html += "</div>"
        
        dashboard_html += """
            </body>
        </html>
        """
        
        return dashboard_html

# Uso del gestor de compliance
if __name__ == "__main__":
    # Configurar credenciales
    BUSINESS_MANAGER_ID = "your_business_manager_id"
    ACCESS_TOKEN = "your_access_token"
    
    # Crear gestor de compliance
    compliance_manager = ComplianceManager(BUSINESS_MANAGER_ID, ACCESS_TOKEN)
    
    # Generar reporte de compliance
    account_ids = ["account_1", "account_2", "account_3"]
    compliance_report = compliance_manager.generate_compliance_report(account_ids)
    
    # Crear dashboard
    dashboard_html = compliance_manager.create_compliance_dashboard(compliance_report)
    
    # Guardar dashboard
    with open('compliance_dashboard.html', 'w') as f:
        f.write(dashboard_html)
    
    print("Compliance report generated successfully")
```

---

## 5. Escalabilidad y Optimización Enterprise

### 5.1 Sistema de Escalabilidad

**Gestor de Escalabilidad:**
```python
import requests
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import logging
import asyncio
import aiohttp

class EnterpriseScalabilityManager:
    def __init__(self, business_manager_id: str, access_token: str):
        self.business_manager_id = business_manager_id
        self.access_token = access_token
        self.base_url = "https://graph.facebook.com/v18.0"
        self.performance_metrics = {}
        self.setup_logging()
        
    def setup_logging(self):
        """Configurar logging para escalabilidad"""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('scalability_audit.log'),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)
    
    async def fetch_account_data_async(self, session: aiohttp.ClientSession, account_id: str) -> Dict:
        """Obtener datos de cuenta de manera asíncrona"""
        try:
            url = f"{self.base_url}/{account_id}/insights"
            params = {
                'access_token': self.access_token,
                'fields': 'impressions,clicks,spend,ctr,cpc,cpm,conversions',
                'time_range': '{"since":"2024-01-01","until":"2024-12-31"}',
                'level': 'account'
            }
            
            async with session.get(url, params=params) as response:
                data = await response.json()
                return {'account_id': account_id, 'data': data}
                
        except Exception as e:
            self.logger.error(f"Error fetching data for account {account_id}: {e}")
            return {'account_id': account_id, 'error': str(e)}
    
    async def fetch_all_accounts_data(self, account_ids: List[str]) -> List[Dict]:
        """Obtener datos de todas las cuentas de manera asíncrona"""
        async with aiohttp.ClientSession() as session:
            tasks = [self.fetch_account_data_async(session, account_id) for account_id in account_ids]
            results = await asyncio.gather(*tasks)
            return results
    
    def analyze_scalability_metrics(self, account_data: List[Dict]) -> Dict:
        """Analizar métricas de escalabilidad"""
        scalability_metrics = {
            'total_accounts': len(account_data),
            'successful_fetches': 0,
            'failed_fetches': 0,
            'total_spend': 0,
            'total_impressions': 0,
            'total_clicks': 0,
            'total_conversions': 0,
            'performance_distribution': {},
            'bottlenecks': []
        }
        
        for account_result in account_data:
            if 'error' in account_result:
                scalability_metrics['failed_fetches'] += 1
                scalability_metrics['bottlenecks'].append({
                    'account_id': account_result['account_id'],
                    'error': account_result['error']
                })
            else:
                scalability_metrics['successful_fetches'] += 1
                data = account_result['data']
                
                if data.get('data'):
                    for insight in data['data']:
                        scalability_metrics['total_spend'] += float(insight.get('spend', 0))
                        scalability_metrics['total_impressions'] += int(insight.get('impressions', 0))
                        scalability_metrics['total_clicks'] += int(insight.get('clicks', 0))
                        scalability_metrics['total_conversions'] += int(insight.get('conversions', 0))
        
        # Calcular distribución de performance
        if scalability_metrics['successful_fetches'] > 0:
            scalability_metrics['performance_distribution'] = {
                'success_rate': scalability_metrics['successful_fetches'] / scalability_metrics['total_accounts'],
                'avg_spend_per_account': scalability_metrics['total_spend'] / scalability_metrics['successful_fetches'],
                'avg_impressions_per_account': scalability_metrics['total_impressions'] / scalability_metrics['successful_fetches'],
                'avg_clicks_per_account': scalability_metrics['total_clicks'] / scalability_metrics['successful_fetches'],
                'avg_conversions_per_account': scalability_metrics['total_conversions'] / scalability_metrics['successful_fetches']
            }
        
        return scalability_metrics
    
    def optimize_api_usage(self, account_ids: List[str]) -> Dict:
        """Optimizar uso de API"""
        optimization_recommendations = {
            'batch_requests': [],
            'rate_limiting': {},
            'caching_strategies': [],
            'data_compression': [],
            'async_processing': []
        }
        
        # Recomendaciones de batch requests
        if len(account_ids) > 10:
            optimization_recommendations['batch_requests'].append({
                'recommendation': 'Use batch requests for multiple accounts',
                'benefit': 'Reduce API calls by up to 80%',
                'implementation': 'Group accounts into batches of 10'
            })
        
        # Recomendaciones de rate limiting
        optimization_recommendations['rate_limiting'] = {
            'current_limit': '200 calls per hour per user',
            'recommended_strategy': 'Implement exponential backoff',
            'benefit': 'Prevent API throttling and improve reliability'
        }
        
        # Recomendaciones de caching
        optimization_recommendations['caching_strategies'] = [
            {
                'strategy': 'Cache account insights for 1 hour',
                'benefit': 'Reduce API calls for frequently accessed data',
                'implementation': 'Use Redis or similar caching system'
            },
            {
                'strategy': 'Cache user permissions for 24 hours',
                'benefit': 'Reduce permission check API calls',
                'implementation': 'Store in memory with TTL'
            }
        ]
        
        # Recomendaciones de compresión de datos
        optimization_recommendations['data_compression'] = [
            {
                'strategy': 'Compress large datasets before storage',
                'benefit': 'Reduce storage costs and improve transfer speed',
                'implementation': 'Use gzip compression for historical data'
            }
        ]
        
        # Recomendaciones de procesamiento asíncrono
        optimization_recommendations['async_processing'] = [
            {
                'strategy': 'Use async/await for API calls',
                'benefit': 'Improve performance by up to 300%',
                'implementation': 'Implement aiohttp for concurrent requests'
            },
            {
                'strategy': 'Process large datasets in parallel',
                'benefit': 'Reduce processing time significantly',
                'implementation': 'Use multiprocessing for CPU-intensive tasks'
            }
        ]
        
        return optimization_recommendations
    
    def create_scalability_report(self, account_ids: List[str]) -> Dict:
        """Crear reporte de escalabilidad"""
        # Obtener datos de todas las cuentas
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        account_data = loop.run_until_complete(self.fetch_all_accounts_data(account_ids))
        loop.close()
        
        # Analizar métricas de escalabilidad
        scalability_metrics = self.analyze_scalability_metrics(account_data)
        
        # Obtener recomendaciones de optimización
        optimization_recommendations = self.optimize_api_usage(account_ids)
        
        # Crear reporte
        report = {
            'report_date': datetime.now().isoformat(),
            'scalability_metrics': scalability_metrics,
            'optimization_recommendations': optimization_recommendations,
            'implementation_priority': self.prioritize_implementations(optimization_recommendations)
        }
        
        self.logger.info(f"Scalability report generated for {len(account_ids)} accounts")
        return report
    
    def prioritize_implementations(self, recommendations: Dict) -> List[Dict]:
        """Priorizar implementaciones"""
        priorities = []
        
        # Alta prioridad: Batch requests
        if recommendations['batch_requests']:
            priorities.append({
                'priority': 'High',
                'implementation': 'Batch Requests',
                'effort': 'Medium',
                'impact': 'High',
                'timeline': '1-2 weeks'
            })
        
        # Alta prioridad: Async processing
        if recommendations['async_processing']:
            priorities.append({
                'priority': 'High',
                'implementation': 'Async Processing',
                'effort': 'High',
                'impact': 'High',
                'timeline': '2-4 weeks'
            })
        
        # Media prioridad: Caching
        if recommendations['caching_strategies']:
            priorities.append({
                'priority': 'Medium',
                'implementation': 'Caching Strategies',
                'effort': 'Medium',
                'impact': 'Medium',
                'timeline': '1-3 weeks'
            })
        
        # Baja prioridad: Data compression
        if recommendations['data_compression']:
            priorities.append({
                'priority': 'Low',
                'implementation': 'Data Compression',
                'effort': 'Low',
                'impact': 'Low',
                'timeline': '1 week'
            })
        
        return priorities

# Uso del gestor de escalabilidad
if __name__ == "__main__":
    # Configurar credenciales
    BUSINESS_MANAGER_ID = "your_business_manager_id"
    ACCESS_TOKEN = "your_access_token"
    
    # Crear gestor de escalabilidad
    scalability_manager = EnterpriseScalabilityManager(BUSINESS_MANAGER_ID, ACCESS_TOKEN)
    
    # Crear reporte de escalabilidad
    account_ids = ["account_1", "account_2", "account_3", "account_4", "account_5"]
    scalability_report = scalability_manager.create_scalability_report(account_ids)
    
    print("Scalability Report:", json.dumps(scalability_report, indent=2))
```

---

## Conclusión

Las características enterprise y multi-cuenta proporcionan una ventaja competitiva significativa al permitir la gestión centralizada, el control de acceso granular y la escalabilidad a nivel organizacional. La implementación exitosa requiere:

**Elementos Clave:**
1. **Gestión Multi-Cuenta**: Control centralizado de múltiples cuentas publicitarias
2. **Control de Acceso**: Permisos granulares y políticas de seguridad
3. **Compliance y Auditoría**: Cumplimiento de regulaciones y monitoreo continuo
4. **Escalabilidad**: Optimización de performance y recursos
5. **Reportes Unificados**: Análisis consolidado a nivel enterprise

**Beneficios:**
- Gestión centralizada de múltiples cuentas
- Control de acceso granular y seguro
- Cumplimiento de regulaciones y compliance
- Escalabilidad y optimización de recursos
- Reportes unificados y análisis consolidado

**Próximos Pasos:**
1. Implementar gestión multi-cuenta
2. Configurar control de acceso granular
3. Establecer sistemas de compliance
4. Optimizar para escalabilidad
5. Desarrollar reportes unificados

La implementación exitosa de características enterprise resultará en un sistema de Facebook Ads altamente escalable, seguro y eficiente para organizaciones grandes.


