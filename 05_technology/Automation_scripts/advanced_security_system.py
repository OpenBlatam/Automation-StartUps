#!/usr/bin/env python3
"""
Sistema de Seguridad Avanzado para Neural Marketing Consciousness Platform
"""

import hashlib
import secrets
import sqlite3
import json
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
import re

class AdvancedSecuritySystem:
    def __init__(self, db_path="security.db"):
        self.db_path = db_path
        self.init_security_database()
        self.security_config = self.load_security_config()
    
    def init_security_database(self):
        """Inicializar base de datos de seguridad"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Tabla de usuarios y autenticación
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                email TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                salt TEXT NOT NULL,
                role TEXT DEFAULT 'user',
                is_active BOOLEAN DEFAULT TRUE,
                created_at TEXT,
                last_login TEXT,
                failed_attempts INTEGER DEFAULT 0,
                locked_until TEXT
            )
        ''')
        
        # Tabla de sesiones
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS sessions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                session_token TEXT UNIQUE NOT NULL,
                created_at TEXT,
                expires_at TEXT,
                ip_address TEXT,
                user_agent TEXT,
                is_active BOOLEAN DEFAULT TRUE,
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
        ''')
        
        # Tabla de logs de seguridad
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS security_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                event_type TEXT NOT NULL,
                description TEXT,
                ip_address TEXT,
                user_agent TEXT,
                severity TEXT DEFAULT 'info',
                timestamp TEXT,
                metadata TEXT,
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
        ''')
        
        # Tabla de intentos de acceso
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS access_attempts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                ip_address TEXT,
                username TEXT,
                success BOOLEAN,
                timestamp TEXT,
                user_agent TEXT,
                failure_reason TEXT
            )
        ''')
        
        # Tabla de tokens de API
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS api_tokens (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                token_name TEXT,
                token_hash TEXT UNIQUE NOT NULL,
                permissions TEXT,
                created_at TEXT,
                expires_at TEXT,
                last_used TEXT,
                is_active BOOLEAN DEFAULT TRUE,
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def load_security_config(self):
        """Cargar configuración de seguridad"""
        return {
            'password_min_length': 12,
            'password_require_uppercase': True,
            'password_require_lowercase': True,
            'password_require_numbers': True,
            'password_require_special': True,
            'max_failed_attempts': 5,
            'lockout_duration_minutes': 30,
            'session_timeout_hours': 24,
            'api_token_expiry_days': 90,
            'rate_limit_requests_per_minute': 60,
            'encryption_algorithm': 'sha256',
            'jwt_secret': secrets.token_urlsafe(32),
            'require_2fa': False,
            'log_retention_days': 90
        }
    
    def hash_password(self, password: str, salt: str = None) -> Tuple[str, str]:
        """Hashear contraseña con salt"""
        if salt is None:
            salt = secrets.token_hex(16)
        
        # Combinar contraseña y salt
        combined = password + salt
        
        # Aplicar múltiples rondas de hash
        hash_obj = hashlib.sha256()
        for _ in range(10000):  # 10,000 rondas
            hash_obj.update(combined.encode('utf-8'))
            combined = hash_obj.hexdigest()
            hash_obj = hashlib.sha256()
        
        return combined, salt
    
    def validate_password_strength(self, password: str) -> Dict[str, bool]:
        """Validar fortaleza de contraseña"""
        validation = {
            'length': len(password) >= self.security_config['password_min_length'],
            'uppercase': bool(re.search(r'[A-Z]', password)) if self.security_config['password_require_uppercase'] else True,
            'lowercase': bool(re.search(r'[a-z]', password)) if self.security_config['password_require_lowercase'] else True,
            'numbers': bool(re.search(r'\d', password)) if self.security_config['password_require_numbers'] else True,
            'special': bool(re.search(r'[!@#$%^&*(),.?":{}|<>]', password)) if self.security_config['password_require_special'] else True
        }
        
        validation['overall'] = all(validation.values())
        return validation
    
    def register_user(self, username: str, email: str, password: str, role: str = 'user') -> Dict:
        """Registrar nuevo usuario"""
        # Validar contraseña
        password_validation = self.validate_password_strength(password)
        if not password_validation['overall']:
            return {
                'success': False,
                'error': 'Password does not meet security requirements',
                'validation': password_validation
            }
        
        # Verificar si usuario ya existe
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('SELECT id FROM users WHERE username = ? OR email = ?', (username, email))
        if cursor.fetchone():
            conn.close()
            return {'success': False, 'error': 'Username or email already exists'}
        
        # Hashear contraseña
        password_hash, salt = self.hash_password(password)
        
        # Crear usuario
        try:
            cursor.execute('''
                INSERT INTO users (username, email, password_hash, salt, role, created_at)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (username, email, password_hash, salt, role, datetime.now().isoformat()))
            
            user_id = cursor.lastrowid
            conn.commit()
            
            # Log de seguridad
            self.log_security_event(
                user_id=user_id,
                event_type='user_registration',
                description=f'User {username} registered successfully',
                severity='info'
            )
            
            conn.close()
            return {'success': True, 'user_id': user_id}
            
        except Exception as e:
            conn.close()
            return {'success': False, 'error': str(e)}
    
    def authenticate_user(self, username: str, password: str, ip_address: str = None, user_agent: str = None) -> Dict:
        """Autenticar usuario"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Obtener usuario
        cursor.execute('''
            SELECT id, username, password_hash, salt, role, is_active, 
                   failed_attempts, locked_until
            FROM users WHERE username = ? OR email = ?
        ''', (username, username))
        
        user = cursor.fetchone()
        if not user:
            self.log_access_attempt(username, ip_address, False, user_agent, 'User not found')
            conn.close()
            return {'success': False, 'error': 'Invalid credentials'}
        
        user_id, db_username, password_hash, salt, role, is_active, failed_attempts, locked_until = user
        
        # Verificar si cuenta está bloqueada
        if locked_until and datetime.fromisoformat(locked_until) > datetime.now():
            self.log_access_attempt(username, ip_address, False, user_agent, 'Account locked')
            conn.close()
            return {'success': False, 'error': 'Account is temporarily locked'}
        
        # Verificar si cuenta está activa
        if not is_active:
            self.log_access_attempt(username, ip_address, False, user_agent, 'Account inactive')
            conn.close()
            return {'success': False, 'error': 'Account is inactive'}
        
        # Verificar contraseña
        hashed_password, _ = self.hash_password(password, salt)
        if hashed_password != password_hash:
            # Incrementar intentos fallidos
            new_failed_attempts = failed_attempts + 1
            locked_until = None
            
            if new_failed_attempts >= self.security_config['max_failed_attempts']:
                locked_until = (datetime.now() + timedelta(minutes=self.security_config['lockout_duration_minutes'])).isoformat()
            
            cursor.execute('''
                UPDATE users 
                SET failed_attempts = ?, locked_until = ?
                WHERE id = ?
            ''', (new_failed_attempts, locked_until, user_id))
            conn.commit()
            
            self.log_access_attempt(username, ip_address, False, user_agent, 'Invalid password')
            conn.close()
            return {'success': False, 'error': 'Invalid credentials'}
        
        # Resetear intentos fallidos y actualizar último login
        cursor.execute('''
            UPDATE users 
            SET failed_attempts = 0, locked_until = NULL, last_login = ?
            WHERE id = ?
        ''', (datetime.now().isoformat(), user_id))
        conn.commit()
        
        # Crear sesión
        session_token = self.create_session(user_id, ip_address, user_agent)
        
        # Log de seguridad
        self.log_security_event(
            user_id=user_id,
            event_type='user_login',
            description=f'User {username} logged in successfully',
            severity='info',
            ip_address=ip_address,
            user_agent=user_agent
        )
        
        self.log_access_attempt(username, ip_address, True, user_agent)
        conn.close()
        
        return {
            'success': True,
            'user_id': user_id,
            'username': db_username,
            'role': role,
            'session_token': session_token
        }
    
    def create_session(self, user_id: int, ip_address: str = None, user_agent: str = None) -> str:
        """Crear nueva sesión"""
        session_token = secrets.token_urlsafe(32)
        expires_at = datetime.now() + timedelta(hours=self.security_config['session_timeout_hours'])
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO sessions (user_id, session_token, created_at, expires_at, ip_address, user_agent)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (user_id, session_token, datetime.now().isoformat(), expires_at.isoformat(), ip_address, user_agent))
        
        conn.commit()
        conn.close()
        
        return session_token
    
    def validate_session(self, session_token: str) -> Dict:
        """Validar sesión"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT s.user_id, s.expires_at, s.is_active, u.username, u.role, u.is_active
            FROM sessions s
            JOIN users u ON s.user_id = u.id
            WHERE s.session_token = ?
        ''', (session_token,))
        
        session = cursor.fetchone()
        if not session:
            conn.close()
            return {'valid': False, 'error': 'Invalid session'}
        
        user_id, expires_at, session_active, username, role, user_active = session
        
        # Verificar si sesión está activa
        if not session_active or not user_active:
            conn.close()
            return {'valid': False, 'error': 'Session inactive'}
        
        # Verificar expiración
        if datetime.fromisoformat(expires_at) < datetime.now():
            # Marcar sesión como inactiva
            cursor.execute('UPDATE sessions SET is_active = FALSE WHERE session_token = ?', (session_token,))
            conn.commit()
            conn.close()
            return {'valid': False, 'error': 'Session expired'}
        
        conn.close()
        return {
            'valid': True,
            'user_id': user_id,
            'username': username,
            'role': role
        }
    
    def logout_user(self, session_token: str) -> bool:
        """Cerrar sesión de usuario"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('UPDATE sessions SET is_active = FALSE WHERE session_token = ?', (session_token,))
        success = cursor.rowcount > 0
        conn.commit()
        conn.close()
        
        return success
    
    def create_api_token(self, user_id: int, token_name: str, permissions: List[str]) -> str:
        """Crear token de API"""
        token = secrets.token_urlsafe(32)
        token_hash = hashlib.sha256(token.encode()).hexdigest()
        expires_at = datetime.now() + timedelta(days=self.security_config['api_token_expiry_days'])
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO api_tokens (user_id, token_name, token_hash, permissions, created_at, expires_at)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (user_id, token_name, token_hash, json.dumps(permissions), datetime.now().isoformat(), expires_at.isoformat()))
        
        conn.commit()
        conn.close()
        
        return token
    
    def validate_api_token(self, token: str) -> Dict:
        """Validar token de API"""
        token_hash = hashlib.sha256(token.encode()).hexdigest()
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT at.user_id, at.permissions, at.expires_at, at.is_active, u.username, u.role
            FROM api_tokens at
            JOIN users u ON at.user_id = u.id
            WHERE at.token_hash = ?
        ''', (token_hash,))
        
        token_data = cursor.fetchone()
        if not token_data:
            conn.close()
            return {'valid': False, 'error': 'Invalid token'}
        
        user_id, permissions, expires_at, is_active, username, role = token_data
        
        # Verificar si token está activo
        if not is_active:
            conn.close()
            return {'valid': False, 'error': 'Token inactive'}
        
        # Verificar expiración
        if datetime.fromisoformat(expires_at) < datetime.now():
            conn.close()
            return {'valid': False, 'error': 'Token expired'}
        
        # Actualizar último uso
        cursor.execute('UPDATE api_tokens SET last_used = ? WHERE token_hash = ?', 
                      (datetime.now().isoformat(), token_hash))
        conn.commit()
        conn.close()
        
        return {
            'valid': True,
            'user_id': user_id,
            'username': username,
            'role': role,
            'permissions': json.loads(permissions)
        }
    
    def log_security_event(self, user_id: int = None, event_type: str = None, 
                          description: str = None, severity: str = 'info', 
                          ip_address: str = None, user_agent: str = None, 
                          metadata: Dict = None):
        """Registrar evento de seguridad"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO security_logs (user_id, event_type, description, ip_address, user_agent, severity, timestamp, metadata)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (user_id, event_type, description, ip_address, user_agent, severity, 
              datetime.now().isoformat(), json.dumps(metadata) if metadata else None))
        
        conn.commit()
        conn.close()
    
    def log_access_attempt(self, username: str, ip_address: str, success: bool, 
                          user_agent: str = None, failure_reason: str = None):
        """Registrar intento de acceso"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO access_attempts (ip_address, username, success, timestamp, user_agent, failure_reason)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (ip_address, username, success, datetime.now().isoformat(), user_agent, failure_reason))
        
        conn.commit()
        conn.close()
    
    def get_security_metrics(self) -> Dict:
        """Obtener métricas de seguridad"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Total de usuarios
        cursor.execute('SELECT COUNT(*) FROM users')
        total_users = cursor.fetchone()[0]
        
        # Usuarios activos
        cursor.execute('SELECT COUNT(*) FROM users WHERE is_active = TRUE')
        active_users = cursor.fetchone()[0]
        
        # Intentos de acceso fallidos en las últimas 24 horas
        yesterday = (datetime.now() - timedelta(days=1)).isoformat()
        cursor.execute('SELECT COUNT(*) FROM access_attempts WHERE success = FALSE AND timestamp > ?', (yesterday,))
        failed_attempts_24h = cursor.fetchone()[0]
        
        # Sesiones activas
        cursor.execute('SELECT COUNT(*) FROM sessions WHERE is_active = TRUE AND expires_at > ?', (datetime.now().isoformat(),))
        active_sessions = cursor.fetchone()[0]
        
        # Eventos de seguridad por severidad
        cursor.execute('''
            SELECT severity, COUNT(*) 
            FROM security_logs 
            WHERE timestamp > ?
            GROUP BY severity
        ''', (yesterday,))
        security_events = dict(cursor.fetchall())
        
        conn.close()
        
        return {
            'total_users': total_users,
            'active_users': active_users,
            'failed_attempts_24h': failed_attempts_24h,
            'active_sessions': active_sessions,
            'security_events': security_events
        }
    
    def get_security_logs(self, limit: int = 100, severity: str = None) -> List[Dict]:
        """Obtener logs de seguridad"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        query = '''
            SELECT sl.id, sl.user_id, u.username, sl.event_type, sl.description, 
                   sl.severity, sl.timestamp, sl.ip_address, sl.metadata
            FROM security_logs sl
            LEFT JOIN users u ON sl.user_id = u.id
        '''
        params = []
        
        if severity:
            query += ' WHERE sl.severity = ?'
            params.append(severity)
        
        query += ' ORDER BY sl.timestamp DESC LIMIT ?'
        params.append(limit)
        
        cursor.execute(query, params)
        logs = cursor.fetchall()
        conn.close()
        
        return [
            {
                'id': log[0],
                'user_id': log[1],
                'username': log[2],
                'event_type': log[3],
                'description': log[4],
                'severity': log[5],
                'timestamp': log[6],
                'ip_address': log[7],
                'metadata': json.loads(log[8]) if log[8] else None
            }
            for log in logs
        ]
    
    def detect_security_threats(self) -> List[Dict]:
        """Detectar amenazas de seguridad"""
        threats = []
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Detectar múltiples intentos fallidos desde la misma IP
        cursor.execute('''
            SELECT ip_address, COUNT(*) as attempts
            FROM access_attempts 
            WHERE success = FALSE AND timestamp > ?
            GROUP BY ip_address
            HAVING attempts > 10
        ''', ((datetime.now() - timedelta(hours=1)).isoformat(),))
        
        for ip, attempts in cursor.fetchall():
            threats.append({
                'type': 'brute_force',
                'severity': 'high',
                'description': f'Multiple failed login attempts from {ip} ({attempts} attempts)',
                'ip_address': ip,
                'recommendation': 'Consider blocking this IP address'
            })
        
        # Detectar sesiones sospechosas (múltiples sesiones desde diferentes IPs)
        cursor.execute('''
            SELECT user_id, COUNT(DISTINCT ip_address) as ip_count
            FROM sessions 
            WHERE is_active = TRUE AND created_at > ?
            GROUP BY user_id
            HAVING ip_count > 3
        ''', ((datetime.now() - timedelta(hours=1)).isoformat(),))
        
        for user_id, ip_count in cursor.fetchall():
            threats.append({
                'type': 'suspicious_activity',
                'severity': 'medium',
                'description': f'User {user_id} has active sessions from {ip_count} different IPs',
                'user_id': user_id,
                'recommendation': 'Review user activity and consider additional verification'
            })
        
        conn.close()
        return threats

def main():
    security = AdvancedSecuritySystem()
    
    print("🔒 Sistema de Seguridad Avanzado")
    print("=" * 50)
    print("1. Registrar usuario")
    print("2. Autenticar usuario")
    print("3. Validar sesión")
    print("4. Crear token de API")
    print("5. Validar token de API")
    print("6. Ver métricas de seguridad")
    print("7. Ver logs de seguridad")
    print("8. Detectar amenazas")
    print("9. Salir")
    
    while True:
        choice = input("\nSeleccione una opción (1-9): ").strip()
        
        if choice == '1':
            username = input("Username: ").strip()
            email = input("Email: ").strip()
            password = input("Password: ").strip()
            role = input("Role (user/admin): ").strip() or 'user'
            
            result = security.register_user(username, email, password, role)
            if result['success']:
                print("✅ Usuario registrado exitosamente")
            else:
                print(f"❌ Error: {result['error']}")
                if 'validation' in result:
                    print("Validación de contraseña:", result['validation'])
        
        elif choice == '2':
            username = input("Username/Email: ").strip()
            password = input("Password: ").strip()
            ip_address = input("IP Address (opcional): ").strip() or None
            
            result = security.authenticate_user(username, password, ip_address)
            if result['success']:
                print(f"✅ Autenticación exitosa")
                print(f"   Usuario: {result['username']}")
                print(f"   Rol: {result['role']}")
                print(f"   Token de sesión: {result['session_token']}")
            else:
                print(f"❌ Error: {result['error']}")
        
        elif choice == '3':
            session_token = input("Session Token: ").strip()
            result = security.validate_session(session_token)
            if result['valid']:
                print(f"✅ Sesión válida")
                print(f"   Usuario: {result['username']}")
                print(f"   Rol: {result['role']}")
            else:
                print(f"❌ Error: {result['error']}")
        
        elif choice == '4':
            user_id = int(input("User ID: ").strip())
            token_name = input("Token Name: ").strip()
            permissions = input("Permissions (comma-separated): ").strip().split(',')
            
            token = security.create_api_token(user_id, token_name, permissions)
            print(f"✅ Token de API creado: {token}")
        
        elif choice == '5':
            token = input("API Token: ").strip()
            result = security.validate_api_token(token)
            if result['valid']:
                print(f"✅ Token válido")
                print(f"   Usuario: {result['username']}")
                print(f"   Rol: {result['role']}")
                print(f"   Permisos: {result['permissions']}")
            else:
                print(f"❌ Error: {result['error']}")
        
        elif choice == '6':
            metrics = security.get_security_metrics()
            print(f"\n📊 Métricas de Seguridad:")
            print(f"  👥 Usuarios totales: {metrics['total_users']}")
            print(f"  ✅ Usuarios activos: {metrics['active_users']}")
            print(f"  ❌ Intentos fallidos (24h): {metrics['failed_attempts_24h']}")
            print(f"  🔐 Sesiones activas: {metrics['active_sessions']}")
            print(f"  📋 Eventos de seguridad:")
            for severity, count in metrics['security_events'].items():
                print(f"    • {severity}: {count}")
        
        elif choice == '7':
            severity = input("Filtrar por severidad (opcional): ").strip() or None
            logs = security.get_security_logs(severity=severity)
            print(f"\n📋 Logs de Seguridad:")
            for log in logs[:10]:  # Mostrar solo los primeros 10
                print(f"  [{log['severity']}] {log['timestamp']} - {log['event_type']}")
                print(f"    {log['description']}")
                if log['username']:
                    print(f"    Usuario: {log['username']}")
                print()
        
        elif choice == '8':
            threats = security.detect_security_threats()
            if threats:
                print(f"\n⚠️ Amenazas Detectadas:")
                for threat in threats:
                    print(f"  🔴 {threat['severity'].upper()}: {threat['description']}")
                    print(f"     Recomendación: {threat['recommendation']}")
                    print()
            else:
                print("✅ No se detectaron amenazas de seguridad")
        
        elif choice == '9':
            print("👋 ¡Hasta luego!")
            break
        
        else:
            print("❌ Opción no válida")

if __name__ == "__main__":
    main()


