# ClickUp Brain: Security & Compliance Guide
## Guía Completa de Seguridad y Cumplimiento Normativo

### Resumen Ejecutivo

Este documento proporciona una guía integral de seguridad y cumplimiento normativo para ClickUp Brain, asegurando la protección de datos, privacidad del usuario y cumplimiento con regulaciones internacionales en el contexto de cursos de IA y SaaS de IA aplicado al marketing.

---

## Framework de Seguridad

### Arquitectura de Seguridad

#### **Defense in Depth Strategy**
```
┌─────────────────────────────────────────────────────────────┐
│                    Security Layers                          │
├─────────────────────────────────────────────────────────────┤
│  🔐 Application Security  │  🛡️ Network Security          │
│  • Authentication        │  • Firewalls                   │
│  • Authorization         │  • VPN                         │
│  • Input Validation      │  • DDoS Protection             │
│  • Session Management    │  • Intrusion Detection         │
├─────────────────────────────────────────────────────────────┤
│  💾 Data Security        │  🔒 Infrastructure Security    │
│  • Encryption at Rest    │  • Server Hardening            │
│  • Encryption in Transit │  • Container Security          │
│  • Key Management        │  • Cloud Security              │
│  • Data Masking          │  • Monitoring & Logging        │
└─────────────────────────────────────────────────────────────┘
```

#### **Security Controls Matrix**
```yaml
Physical Security:
  - Data center access controls
  - Biometric authentication
  - 24/7 security monitoring
  - Environmental controls

Network Security:
  - WAF (Web Application Firewall)
  - DDoS protection
  - Network segmentation
  - VPN access controls

Application Security:
  - OAuth 2.0 / SAML authentication
  - Role-based access control (RBAC)
  - API rate limiting
  - Input validation & sanitization

Data Security:
  - AES-256 encryption at rest
  - TLS 1.3 encryption in transit
  - Database encryption
  - PII data masking

Infrastructure Security:
  - Container security scanning
  - Vulnerability management
  - Security monitoring
  - Incident response procedures
```

---

## Cumplimiento Normativo

### Regulaciones Aplicables

#### **GDPR (General Data Protection Regulation)**
```yaml
Data Protection Principles:
  - Lawfulness, fairness and transparency
  - Purpose limitation
  - Data minimization
  - Accuracy
  - Storage limitation
  - Integrity and confidentiality
  - Accountability

Key Requirements:
  - Data Protection Impact Assessment (DPIA)
  - Privacy by Design
  - Data Subject Rights
  - Breach Notification (72 hours)
  - Data Protection Officer (DPO)
  - Records of Processing Activities

Implementation:
  - Privacy Policy
  - Cookie Consent Management
  - Data Subject Access Requests
  - Right to Erasure
  - Data Portability
  - Consent Management
```

#### **CCPA (California Consumer Privacy Act)**
```yaml
Consumer Rights:
  - Right to Know
  - Right to Delete
  - Right to Opt-Out
  - Right to Non-Discrimination
  - Right to Data Portability

Business Obligations:
  - Privacy Notice
  - Data Collection Disclosure
  - Third-party Sharing Disclosure
  - Opt-out Mechanisms
  - Data Security Requirements

Implementation:
  - CCPA-compliant Privacy Policy
  - Consumer Request Portal
  - Data Inventory
  - Vendor Management
  - Employee Training
```

#### **SOC 2 Type II**
```yaml
Trust Service Criteria:
  - Security: Protection against unauthorized access
  - Availability: System operational availability
  - Processing Integrity: Complete, valid, accurate processing
  - Confidentiality: Information designated as confidential
  - Privacy: Personal information collection, use, retention

Controls Framework:
  - Access Controls
  - System Operations
  - Change Management
  - Risk Management
  - Monitoring
```

#### **ISO 27001**
```yaml
Information Security Management:
  - Information Security Policies
  - Organization of Information Security
  - Human Resource Security
  - Asset Management
  - Access Control
  - Cryptography
  - Physical and Environmental Security
  - Operations Security
  - Communications Security
  - System Acquisition and Development
  - Supplier Relationships
  - Information Security Incident Management
  - Business Continuity Management
  - Compliance
```

---

## Implementación de Seguridad

### Autenticación y Autorización

#### **Multi-Factor Authentication (MFA)**
```python
import pyotp
import qrcode
from cryptography.fernet import Fernet
import hashlib
import secrets

class MFAManager:
    def __init__(self):
        self.secret_key = Fernet.generate_key()
        self.cipher = Fernet(self.secret_key)
    
    def generate_totp_secret(self, user_id):
        """Generate TOTP secret for user"""
        secret = pyotp.random_base32()
        
        # Encrypt and store secret
        encrypted_secret = self.cipher.encrypt(secret.encode())
        self.store_encrypted_secret(user_id, encrypted_secret)
        
        return secret
    
    def generate_qr_code(self, user_email, secret):
        """Generate QR code for MFA setup"""
        totp_uri = pyotp.totp.TOTP(secret).provisioning_uri(
            name=user_email,
            issuer_name="ClickUp Brain"
        )
        
        qr = qrcode.QRCode(version=1, box_size=10, border=5)
        qr.add_data(totp_uri)
        qr.make(fit=True)
        
        return qr.make_image(fill_color="black", back_color="white")
    
    def verify_totp(self, user_id, token):
        """Verify TOTP token"""
        encrypted_secret = self.get_encrypted_secret(user_id)
        secret = self.cipher.decrypt(encrypted_secret).decode()
        
        totp = pyotp.TOTP(secret)
        return totp.verify(token, valid_window=1)
    
    def generate_backup_codes(self, user_id):
        """Generate backup codes for MFA"""
        backup_codes = []
        for _ in range(10):
            code = secrets.token_hex(4).upper()
            backup_codes.append(code)
        
        # Hash and store backup codes
        hashed_codes = [hashlib.sha256(code.encode()).hexdigest() for code in backup_codes]
        self.store_backup_codes(user_id, hashed_codes)
        
        return backup_codes
```

#### **Role-Based Access Control (RBAC)**
```python
from enum import Enum
from typing import List, Dict, Set
import json

class Permission(Enum):
    READ_DASHBOARD = "read:dashboard"
    WRITE_DASHBOARD = "write:dashboard"
    DELETE_DASHBOARD = "delete:dashboard"
    READ_REPORTS = "read:reports"
    WRITE_REPORTS = "write:reports"
    EXPORT_DATA = "export:data"
    MANAGE_USERS = "manage:users"
    SYSTEM_ADMIN = "system:admin"

class Role:
    def __init__(self, name: str, permissions: List[Permission]):
        self.name = name
        self.permissions = set(permissions)
    
    def has_permission(self, permission: Permission) -> bool:
        return permission in self.permissions
    
    def add_permission(self, permission: Permission):
        self.permissions.add(permission)
    
    def remove_permission(self, permission: Permission):
        self.permissions.discard(permission)

class RBACManager:
    def __init__(self):
        self.roles = self._initialize_roles()
        self.user_roles = {}
    
    def _initialize_roles(self) -> Dict[str, Role]:
        """Initialize default roles"""
        roles = {
            'viewer': Role('viewer', [
                Permission.READ_DASHBOARD,
                Permission.READ_REPORTS
            ]),
            'analyst': Role('analyst', [
                Permission.READ_DASHBOARD,
                Permission.WRITE_DASHBOARD,
                Permission.READ_REPORTS,
                Permission.WRITE_REPORTS,
                Permission.EXPORT_DATA
            ]),
            'admin': Role('admin', [
                Permission.READ_DASHBOARD,
                Permission.WRITE_DASHBOARD,
                Permission.DELETE_DASHBOARD,
                Permission.READ_REPORTS,
                Permission.WRITE_REPORTS,
                Permission.EXPORT_DATA,
                Permission.MANAGE_USERS
            ]),
            'super_admin': Role('super_admin', [
                Permission.READ_DASHBOARD,
                Permission.WRITE_DASHBOARD,
                Permission.DELETE_DASHBOARD,
                Permission.READ_REPORTS,
                Permission.WRITE_REPORTS,
                Permission.EXPORT_DATA,
                Permission.MANAGE_USERS,
                Permission.SYSTEM_ADMIN
            ])
        }
        return roles
    
    def assign_role(self, user_id: str, role_name: str):
        """Assign role to user"""
        if role_name not in self.roles:
            raise ValueError(f"Role {role_name} does not exist")
        
        self.user_roles[user_id] = role_name
    
    def check_permission(self, user_id: str, permission: Permission) -> bool:
        """Check if user has permission"""
        if user_id not in self.user_roles:
            return False
        
        role_name = self.user_roles[user_id]
        role = self.roles[role_name]
        
        return role.has_permission(permission)
    
    def get_user_permissions(self, user_id: str) -> Set[Permission]:
        """Get all permissions for user"""
        if user_id not in self.user_roles:
            return set()
        
        role_name = self.user_roles[user_id]
        role = self.roles[role_name]
        
        return role.permissions.copy()
    
    def create_custom_role(self, name: str, permissions: List[Permission]):
        """Create custom role"""
        self.roles[name] = Role(name, permissions)
```

### Encriptación de Datos

#### **Data Encryption at Rest**
```python
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import base64
import os

class DataEncryption:
    def __init__(self, master_password: str):
        self.master_password = master_password.encode()
        self.key = self._derive_key()
        self.cipher = Fernet(self.key)
    
    def _derive_key(self) -> bytes:
        """Derive encryption key from master password"""
        salt = b'clickup_brain_salt_2024'  # In production, use random salt
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,
        )
        key = base64.urlsafe_b64encode(kdf.derive(self.master_password))
        return key
    
    def encrypt_data(self, data: str) -> str:
        """Encrypt data"""
        encrypted_data = self.cipher.encrypt(data.encode())
        return base64.urlsafe_b64encode(encrypted_data).decode()
    
    def decrypt_data(self, encrypted_data: str) -> str:
        """Decrypt data"""
        encrypted_bytes = base64.urlsafe_b64decode(encrypted_data.encode())
        decrypted_data = self.cipher.decrypt(encrypted_bytes)
        return decrypted_data.decode()
    
    def encrypt_file(self, file_path: str, output_path: str):
        """Encrypt file"""
        with open(file_path, 'rb') as file:
            file_data = file.read()
        
        encrypted_data = self.cipher.encrypt(file_data)
        
        with open(output_path, 'wb') as file:
            file.write(encrypted_data)
    
    def decrypt_file(self, encrypted_file_path: str, output_path: str):
        """Decrypt file"""
        with open(encrypted_file_path, 'rb') as file:
            encrypted_data = file.read()
        
        decrypted_data = self.cipher.decrypt(encrypted_data)
        
        with open(output_path, 'wb') as file:
            file.write(decrypted_data)

class DatabaseEncryption:
    def __init__(self):
        self.encryption_key = Fernet.generate_key()
        self.cipher = Fernet(self.encryption_key)
    
    def encrypt_sensitive_columns(self, df, sensitive_columns):
        """Encrypt sensitive columns in DataFrame"""
        encrypted_df = df.copy()
        
        for column in sensitive_columns:
            if column in encrypted_df.columns:
                encrypted_df[column] = encrypted_df[column].apply(
                    lambda x: self.cipher.encrypt(str(x).encode()).decode() 
                    if pd.notna(x) else x
                )
        
        return encrypted_df
    
    def decrypt_sensitive_columns(self, df, sensitive_columns):
        """Decrypt sensitive columns in DataFrame"""
        decrypted_df = df.copy()
        
        for column in sensitive_columns:
            if column in decrypted_df.columns:
                decrypted_df[column] = decrypted_df[column].apply(
                    lambda x: self.cipher.decrypt(x.encode()).decode() 
                    if pd.notna(x) and isinstance(x, str) else x
                )
        
        return decrypted_df
```

#### **Data Encryption in Transit**
```python
import ssl
import socket
from cryptography import x509
from cryptography.x509.oid import NameOID
import datetime

class TLSManager:
    def __init__(self):
        self.cert_path = "certs/server.crt"
        self.key_path = "certs/server.key"
        self.ca_path = "certs/ca.crt"
    
    def create_self_signed_cert(self, hostname="localhost"):
        """Create self-signed certificate for development"""
        from cryptography.hazmat.primitives import serialization
        from cryptography.hazmat.primitives.asymmetric import rsa
        
        # Generate private key
        private_key = rsa.generate_private_key(
            public_exponent=65537,
            key_size=2048,
        )
        
        # Create certificate
        subject = issuer = x509.Name([
            x509.NameAttribute(NameOID.COUNTRY_NAME, "US"),
            x509.NameAttribute(NameOID.STATE_OR_PROVINCE_NAME, "CA"),
            x509.NameAttribute(NameOID.LOCALITY_NAME, "San Francisco"),
            x509.NameAttribute(NameOID.ORGANIZATION_NAME, "ClickUp Brain"),
            x509.NameAttribute(NameOID.COMMON_NAME, hostname),
        ])
        
        cert = x509.CertificateBuilder().subject_name(
            subject
        ).issuer_name(
            issuer
        ).public_key(
            private_key.public_key()
        ).serial_number(
            x509.random_serial_number()
        ).not_valid_before(
            datetime.datetime.utcnow()
        ).not_valid_after(
            datetime.datetime.utcnow() + datetime.timedelta(days=365)
        ).add_extension(
            x509.SubjectAlternativeName([
                x509.DNSName(hostname),
            ]),
            critical=False,
        ).sign(private_key, hashes.SHA256())
        
        # Write certificate and key to files
        with open(self.cert_path, "wb") as f:
            f.write(cert.public_bytes(serialization.Encoding.PEM))
        
        with open(self.key_path, "wb") as f:
            f.write(private_key.private_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PrivateFormat.PKCS8,
                encryption_algorithm=serialization.NoEncryption()
            ))
    
    def create_ssl_context(self):
        """Create SSL context for secure connections"""
        context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
        context.load_cert_chain(self.cert_path, self.key_path)
        context.load_verify_locations(self.ca_path)
        context.check_hostname = False
        context.verify_mode = ssl.CERT_REQUIRED
        
        return context
    
    def verify_certificate(self, hostname, port=443):
        """Verify SSL certificate"""
        try:
            context = ssl.create_default_context()
            with socket.create_connection((hostname, port), timeout=10) as sock:
                with context.wrap_socket(sock, server_hostname=hostname) as ssock:
                    cert = ssock.getpeercert()
                    return {
                        'valid': True,
                        'subject': cert.get('subject'),
                        'issuer': cert.get('issuer'),
                        'expires': cert.get('notAfter')
                    }
        except Exception as e:
            return {
                'valid': False,
                'error': str(e)
            }
```

### Gestión de Secretos

#### **Secret Management System**
```python
import os
import json
import base64
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import boto3
from azure.keyvault.secrets import SecretClient
from azure.identity import DefaultAzureCredential

class SecretManager:
    def __init__(self, provider='local'):
        self.provider = provider
        self.secrets = {}
        
        if provider == 'aws':
            self.aws_client = boto3.client('secretsmanager')
        elif provider == 'azure':
            self.azure_client = SecretClient(
                vault_url="https://clickup-brain-vault.vault.azure.net/",
                credential=DefaultAzureCredential()
            )
        elif provider == 'local':
            self._load_local_secrets()
    
    def _load_local_secrets(self):
        """Load secrets from local encrypted file"""
        secrets_file = "secrets/encrypted_secrets.json"
        if os.path.exists(secrets_file):
            with open(secrets_file, 'r') as f:
                encrypted_data = json.load(f)
            
            # Decrypt secrets
            master_key = os.getenv('MASTER_ENCRYPTION_KEY')
            if master_key:
                cipher = Fernet(master_key.encode())
                decrypted_data = cipher.decrypt(encrypted_data['data'].encode())
                self.secrets = json.loads(decrypted_data.decode())
    
    def get_secret(self, secret_name: str) -> str:
        """Get secret value"""
        if self.provider == 'aws':
            response = self.aws_client.get_secret_value(SecretId=secret_name)
            return response['SecretString']
        
        elif self.provider == 'azure':
            secret = self.azure_client.get_secret(secret_name)
            return secret.value
        
        elif self.provider == 'local':
            return self.secrets.get(secret_name, '')
        
        else:
            raise ValueError(f"Unsupported provider: {self.provider}")
    
    def set_secret(self, secret_name: str, secret_value: str):
        """Set secret value"""
        if self.provider == 'aws':
            self.aws_client.update_secret(
                SecretId=secret_name,
                SecretString=secret_value
            )
        
        elif self.provider == 'azure':
            self.azure_client.set_secret(secret_name, secret_value)
        
        elif self.provider == 'local':
            self.secrets[secret_name] = secret_value
            self._save_local_secrets()
        
        else:
            raise ValueError(f"Unsupported provider: {self.provider}")
    
    def _save_local_secrets(self):
        """Save secrets to local encrypted file"""
        os.makedirs("secrets", exist_ok=True)
        
        master_key = os.getenv('MASTER_ENCRYPTION_KEY')
        if not master_key:
            master_key = Fernet.generate_key().decode()
            os.environ['MASTER_ENCRYPTION_KEY'] = master_key
        
        cipher = Fernet(master_key.encode())
        encrypted_data = cipher.encrypt(json.dumps(self.secrets).encode())
        
        with open("secrets/encrypted_secrets.json", 'w') as f:
            json.dump({'data': encrypted_data.decode()}, f)
    
    def rotate_secret(self, secret_name: str, new_value: str):
        """Rotate secret value"""
        old_value = self.get_secret(secret_name)
        self.set_secret(secret_name, new_value)
        
        # Log rotation event
        self._log_secret_rotation(secret_name, old_value, new_value)
    
    def _log_secret_rotation(self, secret_name: str, old_value: str, new_value: str):
        """Log secret rotation event"""
        log_entry = {
            'timestamp': datetime.now().isoformat(),
            'action': 'secret_rotation',
            'secret_name': secret_name,
            'old_value_hash': hashlib.sha256(old_value.encode()).hexdigest(),
            'new_value_hash': hashlib.sha256(new_value.encode()).hexdigest()
        }
        
        # Log to security audit log
        self._write_audit_log(log_entry)
```

---

## Monitoreo y Auditoría

### Security Monitoring

#### **Security Event Monitoring**
```python
import logging
import json
from datetime import datetime, timedelta
from typing import Dict, List, Any
import redis
from elasticsearch import Elasticsearch

class SecurityMonitor:
    def __init__(self):
        self.logger = logging.getLogger('security_monitor')
        self.redis_client = redis.Redis(host='localhost', port=6379, db=0)
        self.es_client = Elasticsearch(['localhost:9200'])
        self.alert_thresholds = {
            'failed_login_attempts': 5,
            'suspicious_api_calls': 100,
            'data_access_anomalies': 10,
            'privilege_escalation': 1
        }
    
    def log_security_event(self, event_type: str, user_id: str, details: Dict[str, Any]):
        """Log security event"""
        event = {
            'timestamp': datetime.now().isoformat(),
            'event_type': event_type,
            'user_id': user_id,
            'details': details,
            'severity': self._calculate_severity(event_type, details)
        }
        
        # Log to file
        self.logger.warning(f"Security Event: {json.dumps(event)}")
        
        # Store in Redis for real-time monitoring
        self.redis_client.lpush('security_events', json.dumps(event))
        
        # Store in Elasticsearch for long-term analysis
        self.es_client.index(
            index='security-events',
            body=event
        )
        
        # Check for alerts
        self._check_security_alerts(event)
    
    def _calculate_severity(self, event_type: str, details: Dict[str, Any]) -> str:
        """Calculate event severity"""
        severity_map = {
            'login_failure': 'low',
            'multiple_login_failures': 'medium',
            'privilege_escalation': 'high',
            'data_breach': 'critical',
            'suspicious_api_usage': 'medium',
            'unauthorized_access': 'high'
        }
        
        return severity_map.get(event_type, 'low')
    
    def _check_security_alerts(self, event: Dict[str, Any]):
        """Check if event triggers security alert"""
        event_type = event['event_type']
        user_id = event['user_id']
        
        # Check for multiple failed login attempts
        if event_type == 'login_failure':
            self._check_failed_login_attempts(user_id)
        
        # Check for suspicious API usage
        elif event_type == 'api_call':
            self._check_suspicious_api_usage(user_id, event['details'])
        
        # Check for data access anomalies
        elif event_type == 'data_access':
            self._check_data_access_anomalies(user_id, event['details'])
    
    def _check_failed_login_attempts(self, user_id: str):
        """Check for multiple failed login attempts"""
        key = f"failed_logins:{user_id}"
        count = self.redis_client.incr(key)
        self.redis_client.expire(key, 3600)  # 1 hour window
        
        if count >= self.alert_thresholds['failed_login_attempts']:
            self._trigger_alert('multiple_login_failures', {
                'user_id': user_id,
                'attempts': count,
                'time_window': '1 hour'
            })
    
    def _check_suspicious_api_usage(self, user_id: str, details: Dict[str, Any]):
        """Check for suspicious API usage patterns"""
        key = f"api_calls:{user_id}"
        count = self.redis_client.incr(key)
        self.redis_client.expire(key, 300)  # 5 minute window
        
        if count >= self.alert_thresholds['suspicious_api_calls']:
            self._trigger_alert('suspicious_api_usage', {
                'user_id': user_id,
                'api_calls': count,
                'time_window': '5 minutes',
                'endpoint': details.get('endpoint')
            })
    
    def _trigger_alert(self, alert_type: str, details: Dict[str, Any]):
        """Trigger security alert"""
        alert = {
            'timestamp': datetime.now().isoformat(),
            'alert_type': alert_type,
            'details': details,
            'status': 'active'
        }
        
        # Send alert to security team
        self._send_security_alert(alert)
        
        # Store alert in database
        self._store_alert(alert)
    
    def _send_security_alert(self, alert: Dict[str, Any]):
        """Send security alert to security team"""
        # Implementation would send email, Slack notification, etc.
        self.logger.critical(f"SECURITY ALERT: {json.dumps(alert)}")
    
    def get_security_events(self, start_time: datetime, end_time: datetime) -> List[Dict[str, Any]]:
        """Get security events for time period"""
        query = {
            "query": {
                "range": {
                    "timestamp": {
                        "gte": start_time.isoformat(),
                        "lte": end_time.isoformat()
                    }
                }
            }
        }
        
        response = self.es_client.search(
            index='security-events',
            body=query,
            size=1000
        )
        
        return [hit['_source'] for hit in response['hits']['hits']]
```

#### **Audit Logging System**
```python
class AuditLogger:
    def __init__(self):
        self.logger = logging.getLogger('audit_logger')
        self.audit_handler = logging.FileHandler('logs/audit.log')
        self.audit_handler.setLevel(logging.INFO)
        
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        self.audit_handler.setFormatter(formatter)
        self.logger.addHandler(self.audit_handler)
    
    def log_user_action(self, user_id: str, action: str, resource: str, 
                       details: Dict[str, Any] = None):
        """Log user action for audit trail"""
        audit_entry = {
            'timestamp': datetime.now().isoformat(),
            'user_id': user_id,
            'action': action,
            'resource': resource,
            'details': details or {},
            'ip_address': self._get_client_ip(),
            'user_agent': self._get_user_agent()
        }
        
        self.logger.info(f"AUDIT: {json.dumps(audit_entry)}")
    
    def log_data_access(self, user_id: str, data_type: str, 
                       access_type: str, record_count: int):
        """Log data access for compliance"""
        audit_entry = {
            'timestamp': datetime.now().isoformat(),
            'user_id': user_id,
            'action': 'data_access',
            'data_type': data_type,
            'access_type': access_type,
            'record_count': record_count,
            'ip_address': self._get_client_ip()
        }
        
        self.logger.info(f"DATA_ACCESS: {json.dumps(audit_entry)}")
    
    def log_system_change(self, admin_user: str, change_type: str, 
                         before_state: Dict[str, Any], after_state: Dict[str, Any]):
        """Log system configuration changes"""
        audit_entry = {
            'timestamp': datetime.now().isoformat(),
            'admin_user': admin_user,
            'action': 'system_change',
            'change_type': change_type,
            'before_state': before_state,
            'after_state': after_state,
            'ip_address': self._get_client_ip()
        }
        
        self.logger.info(f"SYSTEM_CHANGE: {json.dumps(audit_entry)}")
    
    def _get_client_ip(self) -> str:
        """Get client IP address"""
        # Implementation would get IP from request context
        return "127.0.0.1"
    
    def _get_user_agent(self) -> str:
        """Get user agent string"""
        # Implementation would get user agent from request context
        return "ClickUp Brain Client"
```

---

## Cumplimiento de Privacidad

### GDPR Compliance

#### **Data Subject Rights Management**
```python
class GDPRCompliance:
    def __init__(self):
        self.data_controller = "ClickUp Brain Inc."
        self.dpo_email = "dpo@clickupbrain.com"
        self.audit_logger = AuditLogger()
    
    def handle_data_subject_request(self, request_type: str, user_id: str, 
                                   additional_info: Dict[str, Any] = None):
        """Handle GDPR data subject requests"""
        request_id = self._generate_request_id()
        
        request_record = {
            'request_id': request_id,
            'timestamp': datetime.now().isoformat(),
            'request_type': request_type,
            'user_id': user_id,
            'status': 'received',
            'additional_info': additional_info or {}
        }
        
        # Log request
        self.audit_logger.log_user_action(
            user_id, f"gdpr_request_{request_type}", "data_subject_rights"
        )
        
        # Process request based on type
        if request_type == 'access':
            return self._handle_access_request(request_record)
        elif request_type == 'rectification':
            return self._handle_rectification_request(request_record)
        elif request_type == 'erasure':
            return self._handle_erasure_request(request_record)
        elif request_type == 'portability':
            return self._handle_portability_request(request_record)
        elif request_type == 'restriction':
            return self._handle_restriction_request(request_record)
        else:
            raise ValueError(f"Unknown request type: {request_type}")
    
    def _handle_access_request(self, request_record: Dict[str, Any]):
        """Handle data access request (Article 15)"""
        user_id = request_record['user_id']
        
        # Collect all personal data
        personal_data = {
            'profile_data': self._get_user_profile_data(user_id),
            'activity_data': self._get_user_activity_data(user_id),
            'preferences': self._get_user_preferences(user_id),
            'consent_records': self._get_consent_records(user_id)
        }
        
        # Generate response
        response = {
            'request_id': request_record['request_id'],
            'data_controller': self.data_controller,
            'personal_data': personal_data,
            'processing_purposes': self._get_processing_purposes(),
            'data_retention_periods': self._get_retention_periods(),
            'third_party_sharing': self._get_third_party_sharing(),
            'data_subject_rights': self._get_data_subject_rights()
        }
        
        # Update request status
        self._update_request_status(request_record['request_id'], 'completed')
        
        return response
    
    def _handle_erasure_request(self, request_record: Dict[str, Any]):
        """Handle data erasure request (Article 17)"""
        user_id = request_record['user_id']
        
        # Check if erasure is legally permissible
        if not self._can_erase_data(user_id):
            return {
                'request_id': request_record['request_id'],
                'status': 'rejected',
                'reason': 'Legal obligation to retain data'
            }
        
        # Perform data erasure
        erasure_result = {
            'profile_data': self._erase_user_profile_data(user_id),
            'activity_data': self._erase_user_activity_data(user_id),
            'preferences': self._erase_user_preferences(user_id),
            'consent_records': self._erase_consent_records(user_id)
        }
        
        # Update request status
        self._update_request_status(request_record['request_id'], 'completed')
        
        return {
            'request_id': request_record['request_id'],
            'status': 'completed',
            'erasure_result': erasure_result
        }
    
    def _handle_portability_request(self, request_record: Dict[str, Any]):
        """Handle data portability request (Article 20)"""
        user_id = request_record['user_id']
        
        # Get portable data
        portable_data = {
            'profile_data': self._get_user_profile_data(user_id),
            'preferences': self._get_user_preferences(user_id),
            'exported_data': self._export_user_data(user_id)
        }
        
        # Generate machine-readable format
        export_file = self._generate_export_file(portable_data, user_id)
        
        return {
            'request_id': request_record['request_id'],
            'status': 'completed',
            'export_file': export_file,
            'format': 'JSON',
            'download_url': self._generate_download_url(export_file)
        }
    
    def _can_erase_data(self, user_id: str) -> bool:
        """Check if data can be erased legally"""
        # Check for legal obligations
        legal_obligations = self._check_legal_obligations(user_id)
        
        # Check for legitimate interests
        legitimate_interests = self._check_legitimate_interests(user_id)
        
        return not (legal_obligations or legitimate_interests)
    
    def _check_legal_obligations(self, user_id: str) -> bool:
        """Check if there are legal obligations to retain data"""
        # Implementation would check against applicable laws
        return False
    
    def _check_legitimate_interests(self, user_id: str) -> bool:
        """Check if there are legitimate interests to retain data"""
        # Implementation would check business needs
        return False
```

#### **Consent Management**
```python
class ConsentManager:
    def __init__(self):
        self.consent_types = {
            'marketing_emails': 'Marketing email communications',
            'analytics_tracking': 'Analytics and performance tracking',
            'third_party_sharing': 'Sharing data with third parties',
            'data_processing': 'Processing of personal data',
            'cookies': 'Cookie usage and tracking'
        }
    
    def record_consent(self, user_id: str, consent_type: str, 
                      granted: bool, consent_method: str, 
                      ip_address: str = None, user_agent: str = None):
        """Record user consent"""
        consent_record = {
            'user_id': user_id,
            'consent_type': consent_type,
            'granted': granted,
            'timestamp': datetime.now().isoformat(),
            'consent_method': consent_method,
            'ip_address': ip_address,
            'user_agent': user_agent,
            'version': self._get_consent_version(consent_type)
        }
        
        # Store consent record
        self._store_consent_record(consent_record)
        
        # Update user consent status
        self._update_user_consent_status(user_id, consent_type, granted)
        
        return consent_record
    
    def get_user_consent_status(self, user_id: str) -> Dict[str, bool]:
        """Get current consent status for user"""
        consent_status = {}
        
        for consent_type in self.consent_types.keys():
            consent_status[consent_type] = self._get_consent_status(
                user_id, consent_type
            )
        
        return consent_status
    
    def withdraw_consent(self, user_id: str, consent_type: str):
        """Withdraw user consent"""
        consent_record = {
            'user_id': user_id,
            'consent_type': consent_type,
            'granted': False,
            'timestamp': datetime.now().isoformat(),
            'consent_method': 'withdrawal',
            'version': self._get_consent_version(consent_type)
        }
        
        # Store withdrawal record
        self._store_consent_record(consent_record)
        
        # Update user consent status
        self._update_user_consent_status(user_id, consent_type, False)
        
        # Stop processing if consent withdrawn
        self._stop_processing_on_withdrawal(user_id, consent_type)
    
    def _get_consent_version(self, consent_type: str) -> str:
        """Get current version of consent text"""
        # Implementation would return current version
        return "1.0"
    
    def _store_consent_record(self, consent_record: Dict[str, Any]):
        """Store consent record in database"""
        # Implementation would store in database
        pass
    
    def _update_user_consent_status(self, user_id: str, consent_type: str, granted: bool):
        """Update user consent status"""
        # Implementation would update user record
        pass
    
    def _stop_processing_on_withdrawal(self, user_id: str, consent_type: str):
        """Stop processing when consent is withdrawn"""
        # Implementation would stop relevant processing
        pass
```

---

## Incident Response

### Security Incident Response Plan

#### **Incident Classification**
```python
from enum import Enum
from typing import List, Dict, Any
import json

class IncidentSeverity(Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class IncidentType(Enum):
    DATA_BREACH = "data_breach"
    UNAUTHORIZED_ACCESS = "unauthorized_access"
    MALWARE = "malware"
    DDOS = "ddos"
    INSIDER_THREAT = "insider_threat"
    PHISHING = "phishing"
    SYSTEM_COMPROMISE = "system_compromise"

class SecurityIncident:
    def __init__(self, incident_id: str, incident_type: IncidentType, 
                 severity: IncidentSeverity, description: str):
        self.incident_id = incident_id
        self.incident_type = incident_type
        self.severity = severity
        self.description = description
        self.status = "open"
        self.created_at = datetime.now()
        self.updated_at = datetime.now()
        self.assigned_to = None
        self.evidence = []
        self.actions_taken = []
        self.resolution = None
    
    def add_evidence(self, evidence_type: str, evidence_data: Dict[str, Any]):
        """Add evidence to incident"""
        evidence = {
            'type': evidence_type,
            'data': evidence_data,
            'timestamp': datetime.now().isoformat(),
            'collected_by': self._get_current_user()
        }
        self.evidence.append(evidence)
    
    def add_action(self, action: str, details: Dict[str, Any]):
        """Add action taken to incident"""
        action_record = {
            'action': action,
            'details': details,
            'timestamp': datetime.now().isoformat(),
            'taken_by': self._get_current_user()
        }
        self.actions_taken.append(action_record)
        self.updated_at = datetime.now()
    
    def resolve(self, resolution: str, resolution_details: Dict[str, Any]):
        """Resolve incident"""
        self.status = "resolved"
        self.resolution = {
            'resolution': resolution,
            'details': resolution_details,
            'resolved_at': datetime.now().isoformat(),
            'resolved_by': self._get_current_user()
        }
        self.updated_at = datetime.now()
    
    def _get_current_user(self) -> str:
        """Get current user (implementation would get from context)"""
        return "system"
```

#### **Incident Response Workflow**
```python
class IncidentResponseManager:
    def __init__(self):
        self.incidents = {}
        self.response_team = {
            'incident_commander': 'security@clickupbrain.com',
            'technical_lead': 'tech@clickupbrain.com',
            'legal_counsel': 'legal@clickupbrain.com',
            'communications': 'comms@clickupbrain.com'
        }
        self.escalation_matrix = {
            IncidentSeverity.LOW: ['incident_commander'],
            IncidentSeverity.MEDIUM: ['incident_commander', 'technical_lead'],
            IncidentSeverity.HIGH: ['incident_commander', 'technical_lead', 'legal_counsel'],
            IncidentSeverity.CRITICAL: ['incident_commander', 'technical_lead', 'legal_counsel', 'communications']
        }
    
    def create_incident(self, incident_type: IncidentType, severity: IncidentSeverity, 
                       description: str, initial_evidence: List[Dict[str, Any]] = None):
        """Create new security incident"""
        incident_id = self._generate_incident_id()
        
        incident = SecurityIncident(incident_id, incident_type, severity, description)
        
        # Add initial evidence
        if initial_evidence:
            for evidence in initial_evidence:
                incident.add_evidence(evidence['type'], evidence['data'])
        
        # Store incident
        self.incidents[incident_id] = incident
        
        # Notify response team
        self._notify_response_team(incident)
        
        # Start response workflow
        self._start_response_workflow(incident)
        
        return incident_id
    
    def _notify_response_team(self, incident: SecurityIncident):
        """Notify incident response team"""
        team_members = self.escalation_matrix[incident.severity]
        
        for role in team_members:
            email = self.response_team[role]
            self._send_incident_notification(email, incident, role)
    
    def _send_incident_notification(self, email: str, incident: SecurityIncident, role: str):
        """Send incident notification email"""
        subject = f"Security Incident {incident.incident_id} - {incident.severity.value.upper()}"
        
        body = f"""
        Security Incident Alert
        
        Incident ID: {incident.incident_id}
        Type: {incident.incident_type.value}
        Severity: {incident.severity.value.upper()}
        Description: {incident.description}
        Created: {incident.created_at.isoformat()}
        
        Role: {role}
        
        Please review the incident and take appropriate action.
        
        ClickUp Brain Security Team
        """
        
        # Implementation would send email
        print(f"Sending notification to {email}: {subject}")
    
    def _start_response_workflow(self, incident: SecurityIncident):
        """Start incident response workflow"""
        if incident.severity == IncidentSeverity.CRITICAL:
            self._immediate_response(incident)
        elif incident.severity == IncidentSeverity.HIGH:
            self._high_priority_response(incident)
        else:
            self._standard_response(incident)
    
    def _immediate_response(self, incident: SecurityIncident):
        """Immediate response for critical incidents"""
        # Isolate affected systems
        incident.add_action("system_isolation", {
            "action": "Isolate affected systems",
            "systems": self._identify_affected_systems(incident)
        })
        
        # Preserve evidence
        incident.add_action("evidence_preservation", {
            "action": "Preserve evidence",
            "evidence_types": ["logs", "memory_dumps", "network_traces"]
        })
        
        # Notify authorities if required
        if incident.incident_type == IncidentType.DATA_BREACH:
            self._notify_authorities(incident)
    
    def _notify_authorities(self, incident: SecurityIncident):
        """Notify relevant authorities of data breach"""
        # GDPR: Notify supervisory authority within 72 hours
        # Implementation would send notification to relevant authorities
        incident.add_action("authority_notification", {
            "action": "Notify supervisory authority",
            "authority": "Data Protection Authority",
            "deadline": "72 hours"
        })
    
    def _generate_incident_id(self) -> str:
        """Generate unique incident ID"""
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        return f"INC-{timestamp}"
```

---

## Testing de Seguridad

### Security Testing Framework

#### **Automated Security Testing**
```python
import requests
import subprocess
import json
from typing import List, Dict, Any

class SecurityTester:
    def __init__(self):
        self.test_results = []
        self.vulnerability_scanner = None
    
    def run_security_tests(self, target_url: str) -> Dict[str, Any]:
        """Run comprehensive security tests"""
        test_results = {
            'vulnerability_scan': self._run_vulnerability_scan(target_url),
            'ssl_tls_test': self._test_ssl_tls(target_url),
            'authentication_test': self._test_authentication(target_url),
            'authorization_test': self._test_authorization(target_url),
            'input_validation_test': self._test_input_validation(target_url),
            'session_management_test': self._test_session_management(target_url),
            'api_security_test': self._test_api_security(target_url)
        }
        
        return test_results
    
    def _run_vulnerability_scan(self, target_url: str) -> Dict[str, Any]:
        """Run vulnerability scan using OWASP ZAP"""
        try:
            # Run OWASP ZAP scan
            cmd = [
                'zap-baseline.py',
                '-t', target_url,
                '-J', 'vulnerability_report.json'
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            # Parse results
            with open('vulnerability_report.json', 'r') as f:
                scan_results = json.load(f)
            
            return {
                'status': 'completed',
                'high_risk': scan_results.get('high', 0),
                'medium_risk': scan_results.get('medium', 0),
                'low_risk': scan_results.get('low', 0),
                'informational': scan_results.get('informational', 0)
            }
            
        except Exception as e:
            return {
                'status': 'failed',
                'error': str(e)
            }
    
    def _test_ssl_tls(self, target_url: str) -> Dict[str, Any]:
        """Test SSL/TLS configuration"""
        try:
            # Test SSL configuration
            response = requests.get(target_url, verify=True, timeout=10)
            
            # Get certificate info
            cert_info = self._get_certificate_info(target_url)
            
            return {
                'status': 'completed',
                'ssl_enabled': True,
                'certificate_valid': cert_info['valid'],
                'certificate_expires': cert_info['expires'],
                'tls_version': cert_info['tls_version']
            }
            
        except requests.exceptions.SSLError as e:
            return {
                'status': 'failed',
                'ssl_enabled': False,
                'error': str(e)
            }
    
    def _test_authentication(self, target_url: str) -> Dict[str, Any]:
        """Test authentication mechanisms"""
        auth_tests = {
            'brute_force_protection': self._test_brute_force_protection(target_url),
            'password_policy': self._test_password_policy(target_url),
            'account_lockout': self._test_account_lockout(target_url),
            'multi_factor_auth': self._test_mfa(target_url)
        }
        
        return auth_tests
    
    def _test_brute_force_protection(self, target_url: str) -> Dict[str, Any]:
        """Test brute force protection"""
        # Attempt multiple failed logins
        failed_attempts = 0
        max_attempts = 10
        
        for i in range(max_attempts):
            try:
                response = requests.post(
                    f"{target_url}/login",
                    json={'username': 'test', 'password': 'wrong_password'},
                    timeout=5
                )
                
                if response.status_code == 429:  # Rate limited
                    return {
                        'status': 'protected',
                        'rate_limiting': True,
                        'attempts_before_limit': i + 1
                    }
                
                failed_attempts += 1
                
            except Exception as e:
                break
        
        return {
            'status': 'vulnerable',
            'rate_limiting': False,
            'failed_attempts': failed_attempts
        }
    
    def _test_authorization(self, target_url: str) -> Dict[str, Any]:
        """Test authorization mechanisms"""
        auth_tests = {
            'privilege_escalation': self._test_privilege_escalation(target_url),
            'horizontal_privilege_escalation': self._test_horizontal_escalation(target_url),
            'vertical_privilege_escalation': self._test_vertical_escalation(target_url)
        }
        
        return auth_tests
    
    def _test_privilege_escalation(self, target_url: str) -> Dict[str, Any]:
        """Test for privilege escalation vulnerabilities"""
        # Test with low-privilege user trying to access admin functions
        test_cases = [
            {'endpoint': '/admin/users', 'method': 'GET'},
            {'endpoint': '/admin/settings', 'method': 'POST'},
            {'endpoint': '/admin/delete-user', 'method': 'DELETE'}
        ]
        
        vulnerabilities = []
        
        for test_case in test_cases:
            try:
                response = requests.request(
                    test_case['method'],
                    f"{target_url}{test_case['endpoint']}",
                    headers={'Authorization': 'Bearer low_privilege_token'},
                    timeout=5
                )
                
                if response.status_code == 200:
                    vulnerabilities.append({
                        'endpoint': test_case['endpoint'],
                        'method': test_case['method'],
                        'status_code': response.status_code
                    })
                    
            except Exception as e:
                continue
        
        return {
            'status': 'vulnerable' if vulnerabilities else 'secure',
            'vulnerabilities': vulnerabilities
        }
    
    def _test_input_validation(self, target_url: str) -> Dict[str, Any]:
        """Test input validation"""
        # Test for SQL injection
        sql_injection_tests = [
            "'; DROP TABLE users; --",
            "1' OR '1'='1",
            "admin'--",
            "1' UNION SELECT * FROM users--"
        ]
        
        # Test for XSS
        xss_tests = [
            "<script>alert('XSS')</script>",
            "javascript:alert('XSS')",
            "<img src=x onerror=alert('XSS')>",
            "';alert('XSS');//"
        ]
        
        vulnerabilities = {
            'sql_injection': [],
            'xss': []
        }
        
        # Test SQL injection
        for payload in sql_injection_tests:
            try:
                response = requests.post(
                    f"{target_url}/search",
                    json={'query': payload},
                    timeout=5
                )
                
                if 'error' in response.text.lower() or 'sql' in response.text.lower():
                    vulnerabilities['sql_injection'].append(payload)
                    
            except Exception as e:
                continue
        
        # Test XSS
        for payload in xss_tests:
            try:
                response = requests.post(
                    f"{target_url}/comment",
                    json={'comment': payload},
                    timeout=5
                )
                
                if payload in response.text:
                    vulnerabilities['xss'].append(payload)
                    
            except Exception as e:
                continue
        
        return {
            'status': 'vulnerable' if any(vulnerabilities.values()) else 'secure',
            'vulnerabilities': vulnerabilities
        }
```

---

## Conclusiones

### Beneficios de la Implementación de Seguridad

#### **1. Protección Integral**
- **Defense in Depth**: Múltiples capas de seguridad
- **Real-time Monitoring**: Monitoreo en tiempo real
- **Automated Response**: Respuesta automática a incidentes
- **Compliance**: Cumplimiento con regulaciones

#### **2. Gestión de Riesgos**
- **Risk Assessment**: Evaluación continua de riesgos
- **Vulnerability Management**: Gestión de vulnerabilidades
- **Incident Response**: Respuesta rápida a incidentes
- **Business Continuity**: Continuidad del negocio

#### **3. Cumplimiento Normativo**
- **GDPR Compliance**: Cumplimiento con GDPR
- **CCPA Compliance**: Cumplimiento con CCPA
- **SOC 2**: Cumplimiento con SOC 2
- **ISO 27001**: Cumplimiento con ISO 27001

#### **4. Confianza del Cliente**
- **Data Protection**: Protección de datos del cliente
- **Privacy by Design**: Privacidad por diseño
- **Transparency**: Transparencia en el procesamiento
- **Accountability**: Responsabilidad y rendición de cuentas

### Próximos Pasos

#### **1. Implementación**
- **Security Framework**: Implementación del framework de seguridad
- **Compliance Program**: Programa de cumplimiento
- **Monitoring System**: Sistema de monitoreo
- **Incident Response**: Plan de respuesta a incidentes

#### **2. Training**
- **Security Awareness**: Concienciación en seguridad
- **Incident Response**: Training en respuesta a incidentes
- **Compliance Training**: Training en cumplimiento
- **Regular Updates**: Actualizaciones regulares

#### **3. Continuous Improvement**
- **Regular Assessments**: Evaluaciones regulares
- **Penetration Testing**: Testing de penetración
- **Security Audits**: Auditorías de seguridad
- **Framework Updates**: Actualizaciones del framework

---

**La implementación de un framework de seguridad robusto y cumplimiento normativo es esencial para el éxito de ClickUp Brain, proporcionando protección integral, gestión de riesgos efectiva y cumplimiento con regulaciones internacionales.**

---

*Guía de seguridad y cumplimiento preparada para ClickUp Brain en el contexto de cursos de IA y SaaS de IA aplicado al marketing.*










