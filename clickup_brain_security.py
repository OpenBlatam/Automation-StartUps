#!/usr/bin/env python3
"""
ClickUp Brain Security System
============================

Comprehensive security system with authentication, authorization,
encryption, and threat detection.
"""

import asyncio
import hashlib
import hmac
import secrets
import jwt
import bcrypt
from typing import Any, Dict, List, Optional, Union, Callable
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from pathlib import Path
import logging
from enum import Enum
import threading
from contextlib import asynccontextmanager
import json
import ipaddress
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import base64

ROOT = Path(__file__).parent

class SecurityLevel(Enum):
    """Security levels."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class ThreatType(Enum):
    """Threat types."""
    BRUTE_FORCE = "brute_force"
    SQL_INJECTION = "sql_injection"
    XSS = "xss"
    CSRF = "csrf"
    DDOS = "ddos"
    UNAUTHORIZED_ACCESS = "unauthorized_access"
    DATA_BREACH = "data_breach"
    MALWARE = "malware"

class UserRole(Enum):
    """User roles."""
    ADMIN = "admin"
    USER = "user"
    MODERATOR = "moderator"
    GUEST = "guest"
    SERVICE = "service"

@dataclass
class User:
    """User data structure."""
    id: str
    username: str
    email: str
    password_hash: str
    roles: List[UserRole] = field(default_factory=lambda: [UserRole.USER])
    is_active: bool = True
    is_verified: bool = False
    created_at: datetime = field(default_factory=datetime.now)
    last_login: Optional[datetime] = None
    failed_login_attempts: int = 0
    locked_until: Optional[datetime] = None
    mfa_enabled: bool = False
    mfa_secret: Optional[str] = None
    permissions: List[str] = field(default_factory=list)

@dataclass
class SecurityEvent:
    """Security event data structure."""
    id: str
    event_type: str
    severity: SecurityLevel
    threat_type: Optional[ThreatType] = None
    user_id: Optional[str] = None
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    description: str = ""
    metadata: Dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.now)
    resolved: bool = False

@dataclass
class SecurityPolicy:
    """Security policy configuration."""
    name: str
    description: str
    rules: List[Dict[str, Any]] = field(default_factory=list)
    enabled: bool = True
    severity: SecurityLevel = SecurityLevel.MEDIUM

class PasswordManager:
    """Password management utilities."""
    
    @staticmethod
    def hash_password(password: str) -> str:
        """Hash password using bcrypt."""
        salt = bcrypt.gensalt()
        return bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')
    
    @staticmethod
    def verify_password(password: str, password_hash: str) -> bool:
        """Verify password against hash."""
        return bcrypt.checkpw(password.encode('utf-8'), password_hash.encode('utf-8'))
    
    @staticmethod
    def generate_secure_password(length: int = 16) -> str:
        """Generate secure random password."""
        alphabet = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789!@#$%^&*"
        return ''.join(secrets.choice(alphabet) for _ in range(length))
    
    @staticmethod
    def validate_password_strength(password: str) -> Dict[str, Any]:
        """Validate password strength."""
        score = 0
        feedback = []
        
        if len(password) >= 8:
            score += 1
        else:
            feedback.append("Password should be at least 8 characters long")
        
        if any(c.islower() for c in password):
            score += 1
        else:
            feedback.append("Password should contain lowercase letters")
        
        if any(c.isupper() for c in password):
            score += 1
        else:
            feedback.append("Password should contain uppercase letters")
        
        if any(c.isdigit() for c in password):
            score += 1
        else:
            feedback.append("Password should contain numbers")
        
        if any(c in "!@#$%^&*()_+-=[]{}|;:,.<>?" for c in password):
            score += 1
        else:
            feedback.append("Password should contain special characters")
        
        strength_levels = ["Very Weak", "Weak", "Fair", "Good", "Strong"]
        strength = strength_levels[min(score, len(strength_levels) - 1)]
        
        return {
            'score': score,
            'strength': strength,
            'feedback': feedback,
            'is_strong': score >= 4
        }

class EncryptionManager:
    """Encryption and decryption utilities."""
    
    def __init__(self, master_key: Optional[str] = None):
        self.master_key = master_key or Fernet.generate_key()
        self.fernet = Fernet(self.master_key)
        self.logger = logging.getLogger("encryption_manager")
    
    def encrypt_data(self, data: str) -> str:
        """Encrypt string data."""
        try:
            encrypted_data = self.fernet.encrypt(data.encode('utf-8'))
            return base64.b64encode(encrypted_data).decode('utf-8')
        except Exception as e:
            self.logger.error(f"Encryption error: {e}")
            raise
    
    def decrypt_data(self, encrypted_data: str) -> str:
        """Decrypt string data."""
        try:
            decoded_data = base64.b64decode(encrypted_data.encode('utf-8'))
            decrypted_data = self.fernet.decrypt(decoded_data)
            return decrypted_data.decode('utf-8')
        except Exception as e:
            self.logger.error(f"Decryption error: {e}")
            raise
    
    def encrypt_dict(self, data: Dict[str, Any]) -> str:
        """Encrypt dictionary data."""
        json_data = json.dumps(data)
        return self.encrypt_data(json_data)
    
    def decrypt_dict(self, encrypted_data: str) -> Dict[str, Any]:
        """Decrypt dictionary data."""
        json_data = self.decrypt_data(encrypted_data)
        return json.loads(json_data)
    
    def generate_key_pair(self) -> tuple[str, str]:
        """Generate RSA key pair."""
        private_key = rsa.generate_private_key(
            public_exponent=65537,
            key_size=2048
        )
        
        public_key = private_key.public_key()
        
        # Serialize keys
        private_pem = private_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=serialization.NoEncryption()
        )
        
        public_pem = public_key.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo
        )
        
        return private_pem.decode('utf-8'), public_pem.decode('utf-8')
    
    def sign_data(self, data: str, private_key_pem: str) -> str:
        """Sign data with private key."""
        private_key = serialization.load_pem_private_key(
            private_key_pem.encode('utf-8'),
            password=None
        )
        
        signature = private_key.sign(
            data.encode('utf-8'),
            padding.PSS(
                mgf=padding.MGF1(hashes.SHA256()),
                salt_length=padding.PSS.MAX_LENGTH
            ),
            hashes.SHA256()
        )
        
        return base64.b64encode(signature).decode('utf-8')
    
    def verify_signature(self, data: str, signature: str, public_key_pem: str) -> bool:
        """Verify signature with public key."""
        try:
            public_key = serialization.load_pem_public_key(
                public_key_pem.encode('utf-8')
            )
            
            signature_bytes = base64.b64decode(signature.encode('utf-8'))
            
            public_key.verify(
                signature_bytes,
                data.encode('utf-8'),
                padding.PSS(
                    mgf=padding.MGF1(hashes.SHA256()),
                    salt_length=padding.PSS.MAX_LENGTH
                ),
                hashes.SHA256()
            )
            
            return True
        except Exception:
            return False

class AuthenticationManager:
    """Authentication and session management."""
    
    def __init__(self, secret_key: str, token_expiry: int = 3600):
        self.secret_key = secret_key
        self.token_expiry = token_expiry
        self.users: Dict[str, User] = {}
        self.sessions: Dict[str, Dict[str, Any]] = {}
        self.logger = logging.getLogger("auth_manager")
        self._lock = threading.RLock()
    
    def create_user(self, username: str, email: str, password: str, roles: List[UserRole] = None) -> User:
        """Create new user."""
        user_id = secrets.token_urlsafe(16)
        password_hash = PasswordManager.hash_password(password)
        
        user = User(
            id=user_id,
            username=username,
            email=email,
            password_hash=password_hash,
            roles=roles or [UserRole.USER]
        )
        
        with self._lock:
            self.users[user_id] = user
        
        self.logger.info(f"Created user: {username}")
        return user
    
    def authenticate_user(self, username: str, password: str, ip_address: str = None) -> Optional[User]:
        """Authenticate user with username and password."""
        with self._lock:
            user = next((u for u in self.users.values() if u.username == username), None)
        
        if not user:
            return None
        
        # Check if account is locked
        if user.locked_until and user.locked_until > datetime.now():
            self.logger.warning(f"Account locked for user: {username}")
            return None
        
        # Verify password
        if not PasswordManager.verify_password(password, user.password_hash):
            # Increment failed attempts
            with self._lock:
                user.failed_login_attempts += 1
                
                # Lock account after 5 failed attempts
                if user.failed_login_attempts >= 5:
                    user.locked_until = datetime.now() + timedelta(minutes=30)
                    self.logger.warning(f"Account locked due to failed attempts: {username}")
            
            return None
        
        # Reset failed attempts on successful login
        with self._lock:
            user.failed_login_attempts = 0
            user.locked_until = None
            user.last_login = datetime.now()
        
        self.logger.info(f"User authenticated: {username}")
        return user
    
    def generate_token(self, user: User) -> str:
        """Generate JWT token for user."""
        payload = {
            'user_id': user.id,
            'username': user.username,
            'roles': [role.value for role in user.roles],
            'exp': datetime.utcnow() + timedelta(seconds=self.token_expiry),
            'iat': datetime.utcnow()
        }
        
        return jwt.encode(payload, self.secret_key, algorithm='HS256')
    
    def verify_token(self, token: str) -> Optional[Dict[str, Any]]:
        """Verify JWT token."""
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=['HS256'])
            return payload
        except jwt.ExpiredSignatureError:
            self.logger.warning("Token expired")
            return None
        except jwt.InvalidTokenError:
            self.logger.warning("Invalid token")
            return None
    
    def create_session(self, user: User, ip_address: str = None, user_agent: str = None) -> str:
        """Create user session."""
        session_id = secrets.token_urlsafe(32)
        
        session_data = {
            'user_id': user.id,
            'username': user.username,
            'roles': [role.value for role in user.roles],
            'ip_address': ip_address,
            'user_agent': user_agent,
            'created_at': datetime.now(),
            'last_activity': datetime.now()
        }
        
        with self._lock:
            self.sessions[session_id] = session_data
        
        self.logger.info(f"Created session for user: {user.username}")
        return session_id
    
    def get_session(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Get session data."""
        with self._lock:
            return self.sessions.get(session_id)
    
    def invalidate_session(self, session_id: str) -> bool:
        """Invalidate user session."""
        with self._lock:
            if session_id in self.sessions:
                del self.sessions[session_id]
                self.logger.info(f"Invalidated session: {session_id}")
                return True
            return False
    
    def cleanup_expired_sessions(self) -> int:
        """Clean up expired sessions."""
        current_time = datetime.now()
        expired_sessions = []
        
        with self._lock:
            for session_id, session_data in self.sessions.items():
                if current_time - session_data['last_activity'] > timedelta(hours=24):
                    expired_sessions.append(session_id)
            
            for session_id in expired_sessions:
                del self.sessions[session_id]
        
        if expired_sessions:
            self.logger.info(f"Cleaned up {len(expired_sessions)} expired sessions")
        
        return len(expired_sessions)

class AuthorizationManager:
    """Authorization and permission management."""
    
    def __init__(self):
        self.permissions: Dict[str, List[str]] = {}
        self.role_permissions: Dict[UserRole, List[str]] = {}
        self.logger = logging.getLogger("authz_manager")
        self._setup_default_permissions()
    
    def _setup_default_permissions(self) -> None:
        """Setup default role permissions."""
        self.role_permissions = {
            UserRole.ADMIN: [
                "user.create", "user.read", "user.update", "user.delete",
                "system.admin", "security.admin", "monitoring.admin"
            ],
            UserRole.MODERATOR: [
                "user.read", "user.update", "content.moderate", "reports.read"
            ],
            UserRole.USER: [
                "user.read", "user.update", "content.create", "content.read"
            ],
            UserRole.GUEST: [
                "content.read"
            ],
            UserRole.SERVICE: [
                "api.access", "system.monitor"
            ]
        }
    
    def check_permission(self, user: User, permission: str) -> bool:
        """Check if user has permission."""
        # Check role-based permissions
        for role in user.roles:
            if permission in self.role_permissions.get(role, []):
                return True
        
        # Check direct user permissions
        if permission in user.permissions:
            return True
        
        return False
    
    def check_resource_access(self, user: User, resource: str, action: str) -> bool:
        """Check if user can access resource."""
        permission = f"{resource}.{action}"
        return self.check_permission(user, permission)
    
    def grant_permission(self, user: User, permission: str) -> None:
        """Grant permission to user."""
        if permission not in user.permissions:
            user.permissions.append(permission)
            self.logger.info(f"Granted permission {permission} to user {user.username}")
    
    def revoke_permission(self, user: User, permission: str) -> None:
        """Revoke permission from user."""
        if permission in user.permissions:
            user.permissions.remove(permission)
            self.logger.info(f"Revoked permission {permission} from user {user.username}")
    
    def get_user_permissions(self, user: User) -> List[str]:
        """Get all permissions for user."""
        permissions = set()
        
        # Add role permissions
        for role in user.roles:
            permissions.update(self.role_permissions.get(role, []))
        
        # Add direct permissions
        permissions.update(user.permissions)
        
        return list(permissions)

class ThreatDetector:
    """Threat detection and analysis."""
    
    def __init__(self):
        self.security_events: List[SecurityEvent] = []
        self.threat_patterns: Dict[ThreatType, List[str]] = {}
        self.ip_blacklist: set = set()
        self.logger = logging.getLogger("threat_detector")
        self._setup_threat_patterns()
    
    def _setup_threat_patterns(self) -> None:
        """Setup threat detection patterns."""
        self.threat_patterns = {
            ThreatType.SQL_INJECTION: [
                "'; DROP TABLE",
                "UNION SELECT",
                "OR 1=1",
                "'; INSERT INTO",
                "'; UPDATE SET"
            ],
            ThreatType.XSS: [
                "<script>",
                "javascript:",
                "onload=",
                "onerror=",
                "onclick="
            ],
            ThreatType.CSRF: [
                "csrf_token",
                "authenticity_token"
            ]
        }
    
    def detect_threat(self, request_data: Dict[str, Any]) -> Optional[SecurityEvent]:
        """Detect potential threats in request data."""
        threat_type = None
        severity = SecurityLevel.LOW
        description = ""
        
        # Check for SQL injection
        for pattern in self.threat_patterns.get(ThreatType.SQL_INJECTION, []):
            if self._contains_pattern(request_data, pattern):
                threat_type = ThreatType.SQL_INJECTION
                severity = SecurityLevel.HIGH
                description = f"Potential SQL injection detected: {pattern}"
                break
        
        # Check for XSS
        if not threat_type:
            for pattern in self.threat_patterns.get(ThreatType.XSS, []):
                if self._contains_pattern(request_data, pattern):
                    threat_type = ThreatType.XSS
                    severity = SecurityLevel.MEDIUM
                    description = f"Potential XSS detected: {pattern}"
                    break
        
        # Check for brute force
        if not threat_type:
            ip_address = request_data.get('ip_address')
            if ip_address and self._is_brute_force(ip_address):
                threat_type = ThreatType.BRUTE_FORCE
                severity = SecurityLevel.HIGH
                description = f"Brute force attack detected from IP: {ip_address}"
        
        # Check IP blacklist
        if not threat_type:
            ip_address = request_data.get('ip_address')
            if ip_address and ip_address in self.ip_blacklist:
                threat_type = ThreatType.UNAUTHORIZED_ACCESS
                severity = SecurityLevel.CRITICAL
                description = f"Request from blacklisted IP: {ip_address}"
        
        if threat_type:
            event = SecurityEvent(
                id=secrets.token_urlsafe(16),
                event_type="threat_detected",
                severity=severity,
                threat_type=threat_type,
                ip_address=request_data.get('ip_address'),
                user_agent=request_data.get('user_agent'),
                description=description,
                metadata=request_data
            )
            
            self.security_events.append(event)
            self.logger.warning(f"Threat detected: {description}")
            
            return event
        
        return None
    
    def _contains_pattern(self, data: Dict[str, Any], pattern: str) -> bool:
        """Check if data contains threat pattern."""
        for value in data.values():
            if isinstance(value, str) and pattern.lower() in value.lower():
                return True
            elif isinstance(value, dict):
                if self._contains_pattern(value, pattern):
                    return True
        return False
    
    def _is_brute_force(self, ip_address: str) -> bool:
        """Check if IP is performing brute force attack."""
        # Count recent failed attempts from this IP
        recent_events = [
            event for event in self.security_events
            if (event.ip_address == ip_address and 
                event.threat_type == ThreatType.BRUTE_FORCE and
                event.timestamp > datetime.now() - timedelta(minutes=5))
        ]
        
        return len(recent_events) >= 10
    
    def add_to_blacklist(self, ip_address: str) -> None:
        """Add IP to blacklist."""
        self.ip_blacklist.add(ip_address)
        self.logger.warning(f"Added IP to blacklist: {ip_address}")
    
    def remove_from_blacklist(self, ip_address: str) -> None:
        """Remove IP from blacklist."""
        self.ip_blacklist.discard(ip_address)
        self.logger.info(f"Removed IP from blacklist: {ip_address}")
    
    def get_security_events(self, hours: int = 24) -> List[SecurityEvent]:
        """Get security events from last N hours."""
        cutoff_time = datetime.now() - timedelta(hours=hours)
        return [
            event for event in self.security_events
            if event.timestamp > cutoff_time
        ]
    
    def get_threat_statistics(self) -> Dict[str, Any]:
        """Get threat statistics."""
        recent_events = self.get_security_events(24)
        
        threat_counts = {}
        severity_counts = {}
        
        for event in recent_events:
            if event.threat_type:
                threat_counts[event.threat_type.value] = threat_counts.get(event.threat_type.value, 0) + 1
            severity_counts[event.severity.value] = severity_counts.get(event.severity.value, 0) + 1
        
        return {
            'total_events': len(recent_events),
            'threat_types': threat_counts,
            'severity_levels': severity_counts,
            'blacklisted_ips': len(self.ip_blacklist)
        }

class SecuritySystem:
    """Main security system."""
    
    def __init__(self, secret_key: str = None):
        self.secret_key = secret_key or secrets.token_urlsafe(32)
        self.auth_manager = AuthenticationManager(self.secret_key)
        self.authz_manager = AuthorizationManager()
        self.encryption_manager = EncryptionManager()
        self.threat_detector = ThreatDetector()
        self.logger = logging.getLogger("security_system")
        self._cleanup_task = None
    
    async def start(self) -> None:
        """Start security system."""
        # Start session cleanup task
        async def cleanup_loop():
            while True:
                try:
                    await asyncio.sleep(3600)  # Run every hour
                    self.auth_manager.cleanup_expired_sessions()
                except Exception as e:
                    self.logger.error(f"Error in security cleanup: {e}")
        
        self._cleanup_task = asyncio.create_task(cleanup_loop())
        self.logger.info("Security system started")
    
    async def stop(self) -> None:
        """Stop security system."""
        if self._cleanup_task:
            self._cleanup_task.cancel()
        self.logger.info("Security system stopped")
    
    def create_user(self, username: str, email: str, password: str, roles: List[UserRole] = None) -> User:
        """Create new user."""
        return self.auth_manager.create_user(username, email, password, roles)
    
    def authenticate_user(self, username: str, password: str, ip_address: str = None) -> Optional[User]:
        """Authenticate user."""
        return self.auth_manager.authenticate_user(username, password, ip_address)
    
    def generate_token(self, user: User) -> str:
        """Generate JWT token."""
        return self.auth_manager.generate_token(user)
    
    def verify_token(self, token: str) -> Optional[Dict[str, Any]]:
        """Verify JWT token."""
        return self.auth_manager.verify_token(token)
    
    def check_permission(self, user: User, permission: str) -> bool:
        """Check user permission."""
        return self.authz_manager.check_permission(user, permission)
    
    def encrypt_data(self, data: str) -> str:
        """Encrypt data."""
        return self.encryption_manager.encrypt_data(data)
    
    def decrypt_data(self, encrypted_data: str) -> str:
        """Decrypt data."""
        return self.encryption_manager.decrypt_data(encrypted_data)
    
    def detect_threat(self, request_data: Dict[str, Any]) -> Optional[SecurityEvent]:
        """Detect security threats."""
        return self.threat_detector.detect_threat(request_data)
    
    def get_security_status(self) -> Dict[str, Any]:
        """Get security system status."""
        return {
            'total_users': len(self.auth_manager.users),
            'active_sessions': len(self.auth_manager.sessions),
            'security_events_24h': len(self.threat_detector.get_security_events(24)),
            'blacklisted_ips': len(self.threat_detector.ip_blacklist),
            'threat_statistics': self.threat_detector.get_threat_statistics()
        }

# Global security system
security_system = SecuritySystem()

def get_security_system() -> SecuritySystem:
    """Get global security system."""
    return security_system

async def start_security() -> None:
    """Start global security system."""
    await security_system.start()

async def stop_security() -> None:
    """Stop global security system."""
    await security_system.stop()

if __name__ == "__main__":
    # Demo security system
    print("ClickUp Brain Security System Demo")
    print("=" * 50)
    
    # Setup logging
    logging.basicConfig(level=logging.INFO)
    
    async def demo():
        # Get security system
        security = get_security_system()
        await security.start()
        
        # Create users
        admin_user = security.create_user("admin", "admin@example.com", "admin123", [UserRole.ADMIN])
        regular_user = security.create_user("user", "user@example.com", "user123", [UserRole.USER])
        
        print(f"Created admin user: {admin_user.username}")
        print(f"Created regular user: {regular_user.username}")
        
        # Test authentication
        auth_user = security.authenticate_user("admin", "admin123", "192.168.1.1")
        if auth_user:
            print(f"Authentication successful: {auth_user.username}")
            
            # Generate token
            token = security.generate_token(auth_user)
            print(f"Generated token: {token[:50]}...")
            
            # Verify token
            payload = security.verify_token(token)
            if payload:
                print(f"Token verified for user: {payload['username']}")
        
        # Test authorization
        can_admin = security.check_permission(admin_user, "system.admin")
        can_user_admin = security.check_permission(regular_user, "system.admin")
        
        print(f"Admin can access system.admin: {can_admin}")
        print(f"User can access system.admin: {can_user_admin}")
        
        # Test encryption
        test_data = "Sensitive information"
        encrypted = security.encrypt_data(test_data)
        decrypted = security.decrypt_data(encrypted)
        
        print(f"Original: {test_data}")
        print(f"Encrypted: {encrypted[:50]}...")
        print(f"Decrypted: {decrypted}")
        
        # Test threat detection
        malicious_request = {
            "username": "admin",
            "password": "'; DROP TABLE users; --",
            "ip_address": "192.168.1.100",
            "user_agent": "Mozilla/5.0"
        }
        
        threat = security.detect_threat(malicious_request)
        if threat:
            print(f"Threat detected: {threat.description}")
            print(f"Threat type: {threat.threat_type.value}")
            print(f"Severity: {threat.severity.value}")
        
        # Test password strength
        weak_password = "123456"
        strong_password = "MyStr0ng!P@ssw0rd"
        
        weak_strength = PasswordManager.validate_password_strength(weak_password)
        strong_strength = PasswordManager.validate_password_strength(strong_password)
        
        print(f"Weak password strength: {weak_strength['strength']} (score: {weak_strength['score']})")
        print(f"Strong password strength: {strong_strength['strength']} (score: {strong_strength['score']})")
        
        # Get security status
        status = security.get_security_status()
        print(f"Security status: {status}")
        
        # Stop security system
        await security.stop()
        
        print("\nSecurity system demo completed!")
    
    asyncio.run(demo())