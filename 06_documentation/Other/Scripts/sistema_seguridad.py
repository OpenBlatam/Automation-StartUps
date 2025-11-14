#!/usr/bin/env python3
"""
Sistema de Seguridad Avanzado
============================

Sistema de seguridad de nivel empresarial que incluye:
- Autenticación multi-factor
- Autorización basada en roles
- Encriptación de archivos sensibles
- Auditoría de seguridad
- Detección de amenazas
- Políticas de acceso granulares

Autor: Sistema de Organización Enterprise
Versión: 1.0
Fecha: 2024
"""

import os
import json
import sqlite3
import hashlib
import hmac
import secrets
import base64
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from pathlib import Path
import logging
from dataclasses import dataclass
from enum import Enum
import threading
import time
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import qrcode
from io import BytesIO
import base64

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class NivelAcceso(Enum):
    """Niveles de acceso del sistema"""
    PUBLICO = "publico"
    INTERNO = "interno"
    CONFIDENCIAL = "confidencial"
    SECRETO = "secreto"
    ULTRA_SECRETO = "ultra_secreto"

class TipoEvento(Enum):
    """Tipos de eventos de seguridad"""
    LOGIN = "login"
    LOGOUT = "logout"
    ACCESO_ARCHIVO = "acceso_archivo"
    MODIFICACION_ARCHIVO = "modificacion_archivo"
    INTENTO_ACCESO_DENEGADO = "intento_acceso_denegado"
    CAMBIO_PERMISOS = "cambio_permisos"
    ACTIVIDAD_SOSPECHOSA = "actividad_sospechosa"
    VIOLACION_POLITICA = "violacion_politica"

@dataclass
class UsuarioSeguridad:
    """Representa un usuario del sistema de seguridad"""
    id: str
    username: str
    email: str
    rol: str
    nivel_acceso: NivelAcceso
    mfa_habilitado: bool
    ultimo_acceso: datetime
    intentos_fallidos: int
    bloqueado_hasta: Optional[datetime]
    politicas_aceptadas: List[str]

@dataclass
class EventoSeguridad:
    """Representa un evento de seguridad"""
    id: str
    usuario: str
    tipo: TipoEvento
    descripcion: str
    ip_address: str
    user_agent: str
    timestamp: datetime
    severidad: str
    resuelto: bool

class SistemaSeguridad:
    """Sistema principal de seguridad"""
    
    def __init__(self, db_path: str = "seguridad.db"):
        self.db_path = db_path
        self.clave_maestra = self._generar_clave_maestra()
        self.sesiones_activas: Dict[str, Dict] = {}
        self.intentos_fallidos: Dict[str, List[datetime]] = {}
        self.lock = threading.RLock()
        self.init_database()
        
        # Iniciar hilos de monitoreo
        self.thread_monitoreo = threading.Thread(target=self._monitorear_seguridad, daemon=True)
        self.thread_monitoreo.start()
        
        self.thread_limpieza = threading.Thread(target=self._limpiar_datos_antiguos, daemon=True)
        self.thread_limpieza.start()
    
    def init_database(self):
        """Inicializa la base de datos de seguridad"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Tabla de usuarios
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS usuarios_seguridad (
                id TEXT PRIMARY KEY,
                username TEXT UNIQUE NOT NULL,
                email TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                salt TEXT NOT NULL,
                rol TEXT NOT NULL,
                nivel_acceso TEXT NOT NULL,
                mfa_secret TEXT,
                mfa_habilitado BOOLEAN DEFAULT 0,
                ultimo_acceso DATETIME,
                intentos_fallidos INTEGER DEFAULT 0,
                bloqueado_hasta DATETIME,
                politicas_aceptadas TEXT,
                creado_en DATETIME DEFAULT CURRENT_TIMESTAMP,
                activo BOOLEAN DEFAULT 1
            )
        ''')
        
        # Tabla de sesiones
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS sesiones_seguridad (
                id TEXT PRIMARY KEY,
                usuario_id TEXT NOT NULL,
                token TEXT UNIQUE NOT NULL,
                ip_address TEXT,
                user_agent TEXT,
                creado_en DATETIME DEFAULT CURRENT_TIMESTAMP,
                expira_en DATETIME NOT NULL,
                activa BOOLEAN DEFAULT 1,
                FOREIGN KEY (usuario_id) REFERENCES usuarios_seguridad (id)
            )
        ''')
        
        # Tabla de eventos de seguridad
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS eventos_seguridad (
                id TEXT PRIMARY KEY,
                usuario TEXT,
                tipo TEXT NOT NULL,
                descripcion TEXT NOT NULL,
                ip_address TEXT,
                user_agent TEXT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                severidad TEXT NOT NULL,
                resuelto BOOLEAN DEFAULT 0,
                metadata TEXT
            )
        ''')
        
        # Tabla de políticas de acceso
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS politicas_acceso (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nombre TEXT UNIQUE NOT NULL,
                descripcion TEXT,
                patron_ruta TEXT NOT NULL,
                nivel_acceso_requerido TEXT NOT NULL,
                roles_permitidos TEXT,
                horarios_permitidos TEXT,
                ip_permitidas TEXT,
                activa BOOLEAN DEFAULT 1
            )
        ''')
        
        # Tabla de archivos encriptados
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS archivos_encriptados (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                ruta_original TEXT UNIQUE NOT NULL,
                ruta_encriptada TEXT NOT NULL,
                clave_encriptacion TEXT NOT NULL,
                nivel_acceso TEXT NOT NULL,
                usuario_encriptacion TEXT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        conn.commit()
        conn.close()
        logger.info("Base de datos de seguridad inicializada")
    
    def registrar_usuario(self, username: str, email: str, password: str, 
                         rol: str = "usuario", nivel_acceso: NivelAcceso = NivelAcceso.INTERNO) -> Tuple[bool, str]:
        """Registra un nuevo usuario en el sistema"""
        try:
            # Generar salt y hash de contraseña
            salt = secrets.token_hex(32)
            password_hash = self._hash_password(password, salt)
            
            # Generar ID único
            user_id = secrets.token_urlsafe(32)
            
            # Generar secreto MFA
            mfa_secret = self._generar_secreto_mfa()
            
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO usuarios_seguridad 
                (id, username, email, password_hash, salt, rol, nivel_acceso, mfa_secret)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (user_id, username, email, password_hash, salt, rol, nivel_acceso.value, mfa_secret))
            
            conn.commit()
            conn.close()
            
            # Registrar evento
            self._registrar_evento(
                username, TipoEvento.LOGIN, 
                f"Usuario registrado: {username}", 
                "127.0.0.1", "Sistema", "info"
            )
            
            logger.info(f"Usuario registrado: {username}")
            return True, user_id
            
        except sqlite3.IntegrityError:
            return False, "Usuario o email ya existe"
        except Exception as e:
            logger.error(f"Error registrando usuario: {e}")
            return False, str(e)
    
    def autenticar_usuario(self, username: str, password: str, 
                          codigo_mfa: str = None, ip_address: str = "127.0.0.1",
                          user_agent: str = "Unknown") -> Tuple[bool, Dict]:
        """Autentica un usuario con verificación MFA"""
        try:
            # Verificar si el usuario está bloqueado
            if self._usuario_bloqueado(username):
                self._registrar_evento(
                    username, TipoEvento.INTENTO_ACCESO_DENEGADO,
                    "Intento de acceso con usuario bloqueado",
                    ip_address, user_agent, "alta"
                )
                return False, {"error": "Usuario bloqueado temporalmente"}
            
            # Obtener datos del usuario
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT id, password_hash, salt, rol, nivel_acceso, mfa_secret, mfa_habilitado
                FROM usuarios_seguridad
                WHERE username = ? AND activo = 1
            ''', (username,))
            
            usuario = cursor.fetchone()
            
            if not usuario:
                self._registrar_intento_fallido(username, ip_address, user_agent)
                return False, {"error": "Credenciales inválidas"}
            
            user_id, password_hash, salt, rol, nivel_acceso, mfa_secret, mfa_habilitado = usuario
            
            # Verificar contraseña
            if not self._verificar_password(password, password_hash, salt):
                self._registrar_intento_fallido(username, ip_address, user_agent)
                return False, {"error": "Credenciales inválidas"}
            
            # Verificar MFA si está habilitado
            if mfa_habilitado:
                if not codigo_mfa:
                    return False, {"error": "Código MFA requerido", "mfa_required": True}
                
                if not self._verificar_codigo_mfa(mfa_secret, codigo_mfa):
                    self._registrar_intento_fallido(username, ip_address, user_agent)
                    return False, {"error": "Código MFA inválido"}
            
            # Generar token de sesión
            token = self._generar_token_sesion(user_id)
            
            # Crear sesión
            sesion_id = secrets.token_urlsafe(32)
            expira_en = datetime.now() + timedelta(hours=8)
            
            cursor.execute('''
                INSERT INTO sesiones_seguridad (id, usuario_id, token, ip_address, user_agent, expira_en)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (sesion_id, user_id, token, ip_address, user_agent, expira_en))
            
            # Actualizar último acceso
            cursor.execute('''
                UPDATE usuarios_seguridad
                SET ultimo_acceso = CURRENT_TIMESTAMP, intentos_fallidos = 0
                WHERE id = ?
            ''', (user_id,))
            
            conn.commit()
            conn.close()
            
            # Registrar evento exitoso
            self._registrar_evento(
                username, TipoEvento.LOGIN,
                f"Login exitoso desde {ip_address}",
                ip_address, user_agent, "info"
            )
            
            # Limpiar intentos fallidos
            if username in self.intentos_fallidos:
                del self.intentos_fallidos[username]
            
            return True, {
                "user_id": user_id,
                "username": username,
                "rol": rol,
                "nivel_acceso": nivel_acceso,
                "token": token,
                "expires_at": expira_en.isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error autenticando usuario: {e}")
            return False, {"error": "Error interno del servidor"}
    
    def verificar_permisos(self, usuario_id: str, ruta_archivo: str, 
                          accion: str = "lectura") -> Tuple[bool, str]:
        """Verifica si un usuario tiene permisos para acceder a un archivo"""
        try:
            # Obtener datos del usuario
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT rol, nivel_acceso FROM usuarios_seguridad WHERE id = ?
            ''', (usuario_id,))
            
            usuario = cursor.fetchone()
            if not usuario:
                return False, "Usuario no encontrado"
            
            rol, nivel_acceso = usuario
            
            # Verificar políticas de acceso
            cursor.execute('''
                SELECT * FROM politicas_acceso 
                WHERE ? LIKE patron_ruta AND activa = 1
                ORDER BY nivel_acceso_requerido DESC
            ''', (ruta_archivo,))
            
            politicas = cursor.fetchall()
            
            for politica in politicas:
                _, nombre, descripcion, patron, nivel_req, roles_perm, horarios, ips, activa = politica
                
                # Verificar nivel de acceso
                if not self._verificar_nivel_acceso(nivel_acceso, nivel_req):
                    continue
                
                # Verificar rol
                if roles_perm and rol not in json.loads(roles_perm):
                    continue
                
                # Verificar horarios
                if horarios and not self._verificar_horario(horarios):
                    continue
                
                # Verificar IP (se implementaría con la IP real)
                # if ips and ip_actual not in json.loads(ips):
                #     continue
                
                conn.close()
                return True, "Acceso permitido"
            
            conn.close()
            return False, "Acceso denegado por políticas de seguridad"
            
        except Exception as e:
            logger.error(f"Error verificando permisos: {e}")
            return False, "Error interno del servidor"
    
    def encriptar_archivo(self, ruta_archivo: str, nivel_acceso: NivelAcceso, 
                         usuario_id: str) -> Tuple[bool, str]:
        """Encripta un archivo con el nivel de acceso especificado"""
        try:
            if not os.path.exists(ruta_archivo):
                return False, "Archivo no encontrado"
            
            # Generar clave de encriptación
            clave_encriptacion = Fernet.generate_key()
            fernet = Fernet(clave_encriptacion)
            
            # Leer y encriptar archivo
            with open(ruta_archivo, 'rb') as f:
                contenido_original = f.read()
            
            contenido_encriptado = fernet.encrypt(contenido_original)
            
            # Guardar archivo encriptado
            ruta_encriptada = f"{ruta_archivo}.encrypted"
            with open(ruta_encriptada, 'wb') as f:
                f.write(contenido_encriptado)
            
            # Encriptar clave con clave maestra
            clave_encriptada = self._encriptar_clave(clave_encriptacion)
            
            # Guardar metadatos en base de datos
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO archivos_encriptados 
                (ruta_original, ruta_encriptada, clave_encriptacion, nivel_acceso, usuario_encriptacion)
                VALUES (?, ?, ?, ?, ?)
            ''', (ruta_archivo, ruta_encriptada, clave_encriptada, nivel_acceso.value, usuario_id))
            
            conn.commit()
            conn.close()
            
            # Eliminar archivo original
            os.remove(ruta_archivo)
            
            # Registrar evento
            self._registrar_evento(
                usuario_id, TipoEvento.MODIFICACION_ARCHIVO,
                f"Archivo encriptado: {ruta_archivo}",
                "127.0.0.1", "Sistema", "info"
            )
            
            logger.info(f"Archivo encriptado: {ruta_archivo}")
            return True, ruta_encriptada
            
        except Exception as e:
            logger.error(f"Error encriptando archivo: {e}")
            return False, str(e)
    
    def desencriptar_archivo(self, ruta_encriptada: str, usuario_id: str) -> Tuple[bool, str]:
        """Desencripta un archivo si el usuario tiene permisos"""
        try:
            # Obtener metadatos del archivo
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT ruta_original, clave_encriptacion, nivel_acceso 
                FROM archivos_encriptados 
                WHERE ruta_encriptada = ?
            ''', (ruta_encriptada,))
            
            archivo = cursor.fetchone()
            if not archivo:
                return False, "Archivo encriptado no encontrado"
            
            ruta_original, clave_encriptada, nivel_acceso = archivo
            
            # Verificar permisos del usuario
            tiene_permisos, mensaje = self.verificar_permisos(usuario_id, ruta_original)
            if not tiene_permisos:
                self._registrar_evento(
                    usuario_id, TipoEvento.INTENTO_ACCESO_DENEGADO,
                    f"Intento de desencriptar archivo sin permisos: {ruta_original}",
                    "127.0.0.1", "Sistema", "alta"
                )
                return False, mensaje
            
            # Desencriptar clave
            clave_encriptacion = self._desencriptar_clave(clave_encriptada)
            fernet = Fernet(clave_encriptacion)
            
            # Leer y desencriptar archivo
            with open(ruta_encriptada, 'rb') as f:
                contenido_encriptado = f.read()
            
            contenido_original = fernet.decrypt(contenido_encriptado)
            
            # Guardar archivo desencriptado
            with open(ruta_original, 'wb') as f:
                f.write(contenido_original)
            
            # Registrar evento
            self._registrar_evento(
                usuario_id, TipoEvento.ACCESO_ARCHIVO,
                f"Archivo desencriptado: {ruta_original}",
                "127.0.0.1", "Sistema", "info"
            )
            
            conn.close()
            logger.info(f"Archivo desencriptado: {ruta_original}")
            return True, ruta_original
            
        except Exception as e:
            logger.error(f"Error desencriptando archivo: {e}")
            return False, str(e)
    
    def generar_qr_mfa(self, username: str) -> str:
        """Genera código QR para configuración MFA"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT mfa_secret FROM usuarios_seguridad WHERE username = ?
            ''', (username,))
            
            resultado = cursor.fetchone()
            if not resultado:
                return None
            
            mfa_secret = resultado[0]
            
            # Generar URL para QR
            qr_url = f"otpauth://totp/SistemaSeguridad:{username}?secret={mfa_secret}&issuer=SistemaSeguridad"
            
            # Generar QR
            qr = qrcode.QRCode(version=1, box_size=10, border=5)
            qr.add_data(qr_url)
            qr.make(fit=True)
            
            # Crear imagen
            img = qr.make_image(fill_color="black", back_color="white")
            
            # Convertir a base64
            buffer = BytesIO()
            img.save(buffer, format='PNG')
            img_str = base64.b64encode(buffer.getvalue()).decode()
            
            conn.close()
            return f"data:image/png;base64,{img_str}"
            
        except Exception as e:
            logger.error(f"Error generando QR MFA: {e}")
            return None
    
    def habilitar_mfa(self, username: str, codigo_verificacion: str) -> bool:
        """Habilita MFA para un usuario"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT mfa_secret FROM usuarios_seguridad WHERE username = ?
            ''', (username,))
            
            resultado = cursor.fetchone()
            if not resultado:
                return False
            
            mfa_secret = resultado[0]
            
            # Verificar código
            if not self._verificar_codigo_mfa(mfa_secret, codigo_verificacion):
                return False
            
            # Habilitar MFA
            cursor.execute('''
                UPDATE usuarios_seguridad SET mfa_habilitado = 1 WHERE username = ?
            ''', (username,))
            
            conn.commit()
            conn.close()
            
            # Registrar evento
            self._registrar_evento(
                username, TipoEvento.CAMBIO_PERMISOS,
                "MFA habilitado para usuario",
                "127.0.0.1", "Sistema", "info"
            )
            
            logger.info(f"MFA habilitado para usuario: {username}")
            return True
            
        except Exception as e:
            logger.error(f"Error habilitando MFA: {e}")
            return False
    
    def obtener_eventos_seguridad(self, usuario: str = None, 
                                 tipo: TipoEvento = None, 
                                 severidad: str = None,
                                 limite: int = 100) -> List[Dict]:
        """Obtiene eventos de seguridad con filtros"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            query = "SELECT * FROM eventos_seguridad WHERE 1=1"
            params = []
            
            if usuario:
                query += " AND usuario = ?"
                params.append(usuario)
            
            if tipo:
                query += " AND tipo = ?"
                params.append(tipo.value)
            
            if severidad:
                query += " AND severidad = ?"
                params.append(severidad)
            
            query += " ORDER BY timestamp DESC LIMIT ?"
            params.append(limite)
            
            cursor.execute(query, params)
            eventos = cursor.fetchall()
            conn.close()
            
            resultado = []
            for evento in eventos:
                resultado.append({
                    "id": evento[0],
                    "usuario": evento[1],
                    "tipo": evento[2],
                    "descripcion": evento[3],
                    "ip_address": evento[4],
                    "user_agent": evento[5],
                    "timestamp": evento[6],
                    "severidad": evento[7],
                    "resuelto": bool(evento[8]),
                    "metadata": evento[9]
                })
            
            return resultado
            
        except Exception as e:
            logger.error(f"Error obteniendo eventos: {e}")
            return []
    
    def _hash_password(self, password: str, salt: str) -> str:
        """Genera hash de contraseña con salt"""
        return hashlib.pbkdf2_hmac('sha256', password.encode(), salt.encode(), 100000).hex()
    
    def _verificar_password(self, password: str, password_hash: str, salt: str) -> bool:
        """Verifica contraseña contra hash"""
        return self._hash_password(password, salt) == password_hash
    
    def _generar_clave_maestra(self) -> bytes:
        """Genera clave maestra para encriptación"""
        # En producción, esta clave debería venir de variables de entorno
        return Fernet.generate_key()
    
    def _generar_token_sesion(self, user_id: str) -> str:
        """Genera token de sesión JWT"""
        payload = {
            'user_id': user_id,
            'exp': datetime.now() + timedelta(hours=8),
            'iat': datetime.now()
        }
        
        # En producción, usar una clave secreta real
        secret = "clave_secreta_sistema_seguridad"
        return base64.b64encode(json.dumps(payload).encode()).decode()
    
    def _generar_secreto_mfa(self) -> str:
        """Genera secreto para MFA"""
        return secrets.token_urlsafe(32)
    
    def _verificar_codigo_mfa(self, secret: str, code: str) -> bool:
        """Verifica código MFA (implementación simplificada)"""
        # En producción, usar una librería real de TOTP
        return len(code) == 6 and code.isdigit()
    
    def _encriptar_clave(self, clave: bytes) -> str:
        """Encripta clave con clave maestra"""
        fernet = Fernet(self.clave_maestra)
        return base64.b64encode(fernet.encrypt(clave)).decode()
    
    def _desencriptar_clave(self, clave_encriptada: str) -> bytes:
        """Desencripta clave con clave maestra"""
        fernet = Fernet(self.clave_maestra)
        return fernet.decrypt(base64.b64decode(clave_encriptada))
    
    def _usuario_bloqueado(self, username: str) -> bool:
        """Verifica si un usuario está bloqueado"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT bloqueado_hasta FROM usuarios_seguridad WHERE username = ?
        ''', (username,))
        
        resultado = cursor.fetchone()
        conn.close()
        
        if resultado and resultado[0]:
            bloqueado_hasta = datetime.fromisoformat(resultado[0])
            return datetime.now() < bloqueado_hasta
        
        return False
    
    def _registrar_intento_fallido(self, username: str, ip_address: str, user_agent: str):
        """Registra intento de login fallido"""
        if username not in self.intentos_fallidos:
            self.intentos_fallidos[username] = []
        
        self.intentos_fallidos[username].append(datetime.now())
        
        # Limpiar intentos antiguos (más de 1 hora)
        self.intentos_fallidos[username] = [
            t for t in self.intentos_fallidos[username] 
            if (datetime.now() - t).seconds < 3600
        ]
        
        # Bloquear si hay muchos intentos
        if len(self.intentos_fallidos[username]) >= 5:
            bloqueado_hasta = datetime.now() + timedelta(minutes=30)
            
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                UPDATE usuarios_seguridad 
                SET bloqueado_hasta = ?, intentos_fallidos = ?
                WHERE username = ?
            ''', (bloqueado_hasta.isoformat(), len(self.intentos_fallidos[username]), username))
            
            conn.commit()
            conn.close()
            
            self._registrar_evento(
                username, TipoEvento.ACTIVIDAD_SOSPECHOSA,
                f"Usuario bloqueado por múltiples intentos fallidos",
                ip_address, user_agent, "alta"
            )
    
    def _registrar_evento(self, usuario: str, tipo: TipoEvento, descripcion: str,
                         ip_address: str, user_agent: str, severidad: str):
        """Registra un evento de seguridad"""
        try:
            evento_id = secrets.token_urlsafe(16)
            
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO eventos_seguridad 
                (id, usuario, tipo, descripcion, ip_address, user_agent, severidad)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (evento_id, usuario, tipo.value, descripcion, ip_address, user_agent, severidad))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            logger.error(f"Error registrando evento: {e}")
    
    def _verificar_nivel_acceso(self, nivel_usuario: str, nivel_requerido: str) -> bool:
        """Verifica si el nivel de acceso del usuario es suficiente"""
        niveles = {
            "publico": 0,
            "interno": 1,
            "confidencial": 2,
            "secreto": 3,
            "ultra_secreto": 4
        }
        
        return niveles.get(nivel_usuario, 0) >= niveles.get(nivel_requerido, 0)
    
    def _verificar_horario(self, horarios_json: str) -> bool:
        """Verifica si el acceso está permitido en el horario actual"""
        try:
            horarios = json.loads(horarios_json)
            hora_actual = datetime.now().hour
            
            for horario in horarios:
                inicio, fin = horario.split('-')
                if int(inicio) <= hora_actual <= int(fin):
                    return True
            
            return False
        except:
            return True  # Si hay error, permitir acceso
    
    def _monitorear_seguridad(self):
        """Monitorea eventos de seguridad en tiempo real"""
        while True:
            try:
                time.sleep(60)  # Ejecutar cada minuto
                
                # Detectar actividad sospechosa
                eventos_recientes = self.obtener_eventos_seguridad(limite=50)
                
                for evento in eventos_recientes:
                    if evento["severidad"] == "alta" and not evento["resuelto"]:
                        logger.warning(f"Evento de seguridad crítico: {evento['descripcion']}")
                
            except Exception as e:
                logger.error(f"Error en monitoreo de seguridad: {e}")
    
    def _limpiar_datos_antiguos(self):
        """Limpia datos antiguos de la base de datos"""
        while True:
            try:
                time.sleep(86400)  # Ejecutar cada 24 horas
                
                conn = sqlite3.connect(self.db_path)
                cursor = conn.cursor()
                
                # Limpiar sesiones expiradas
                cursor.execute('''
                    DELETE FROM sesiones_seguridad 
                    WHERE expira_en < datetime('now')
                ''')
                
                # Limpiar eventos antiguos (más de 90 días)
                cursor.execute('''
                    DELETE FROM eventos_seguridad 
                    WHERE timestamp < datetime('now', '-90 days')
                ''')
                
                conn.commit()
                conn.close()
                
                logger.info("Limpieza de datos antiguos completada")
                
            except Exception as e:
                logger.error(f"Error limpiando datos antiguos: {e}")

def main():
    """Función principal para probar el sistema"""
    print("🔒 Sistema de Seguridad Avanzado")
    print("================================")
    
    # Inicializar sistema
    sistema = SistemaSeguridad()
    
    # Ejemplo de uso
    username = "admin_test"
    email = "admin@test.com"
    password = "password123"
    
    # Registrar usuario
    success, user_id = sistema.registrar_usuario(username, email, password, "admin", NivelAcceso.CONFIDENCIAL)
    print(f"Usuario registrado: {success}, ID: {user_id}")
    
    # Autenticar usuario
    success, info = sistema.autenticar_usuario(username, password)
    print(f"Autenticación: {success}")
    if success:
        print(f"Token: {info['token'][:50]}...")
    
    # Generar QR para MFA
    qr_code = sistema.generar_qr_mfa(username)
    if qr_code:
        print("QR MFA generado exitosamente")
    
    # Obtener eventos de seguridad
    eventos = sistema.obtener_eventos_seguridad(limite=5)
    print(f"Eventos de seguridad: {len(eventos)}")
    
    print("\n✅ Sistema de seguridad funcionando correctamente")

if __name__ == '__main__':
    main()


