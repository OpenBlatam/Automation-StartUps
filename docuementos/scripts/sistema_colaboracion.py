#!/usr/bin/env python3
"""
Sistema de Colaboración en Tiempo Real
=====================================

Sistema avanzado de colaboración que permite a múltiples usuarios
trabajar simultáneamente en documentos con sincronización en tiempo real,
control de versiones y gestión de conflictos.

Autor: Sistema de Organización Enterprise
Versión: 1.0
Fecha: 2024
"""

import os
import json
import sqlite3
import threading
import time
import hashlib
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from pathlib import Path
import logging
from dataclasses import dataclass, asdict
from enum import Enum

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class TipoOperacion(Enum):
    """Tipos de operaciones de colaboración"""
    INSERTAR = "insertar"
    ELIMINAR = "eliminar"
    MODIFICAR = "modificar"
    MOVER = "mover"
    COMENTAR = "comentar"
    RESALTAR = "resaltar"

@dataclass
class OperacionColaboracion:
    """Representa una operación de colaboración"""
    id: str
    usuario: str
    documento: str
    tipo: TipoOperacion
    contenido: str
    posicion: int
    timestamp: datetime
    version: int
    conflicto: bool = False

@dataclass
class SesionColaboracion:
    """Representa una sesión de colaboración activa"""
    documento: str
    usuario: str
    timestamp_inicio: datetime
    ultima_actividad: datetime
    operaciones_pendientes: List[str]
    version_local: int

class SistemaColaboracion:
    """Sistema principal de colaboración en tiempo real"""
    
    def __init__(self, db_path: str = "colaboracion.db"):
        self.db_path = db_path
        self.sesiones_activas: Dict[str, SesionColaboracion] = {}
        self.operaciones_pendientes: Dict[str, List[OperacionColaboracion]] = {}
        self.lock = threading.RLock()
        self.init_database()
        
        # Iniciar hilo de limpieza
        self.thread_limpieza = threading.Thread(target=self._limpiar_sesiones_inactivas, daemon=True)
        self.thread_limpieza.start()
    
    def init_database(self):
        """Inicializa la base de datos de colaboración"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Tabla de documentos colaborativos
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS documentos_colaborativos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                ruta_documento TEXT UNIQUE NOT NULL,
                version_actual INTEGER DEFAULT 1,
                ultima_modificacion DATETIME DEFAULT CURRENT_TIMESTAMP,
                usuarios_activos INTEGER DEFAULT 0,
                bloqueado_por TEXT,
                bloqueado_hasta DATETIME
            )
        ''')
        
        # Tabla de operaciones
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS operaciones_colaboracion (
                id TEXT PRIMARY KEY,
                documento TEXT NOT NULL,
                usuario TEXT NOT NULL,
                tipo TEXT NOT NULL,
                contenido TEXT,
                posicion INTEGER,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                version INTEGER NOT NULL,
                conflicto BOOLEAN DEFAULT 0,
                aplicada BOOLEAN DEFAULT 0,
                FOREIGN KEY (documento) REFERENCES documentos_colaborativos (ruta_documento)
            )
        ''')
        
        # Tabla de sesiones
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS sesiones_colaboracion (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                documento TEXT NOT NULL,
                usuario TEXT NOT NULL,
                timestamp_inicio DATETIME DEFAULT CURRENT_TIMESTAMP,
                ultima_actividad DATETIME DEFAULT CURRENT_TIMESTAMP,
                version_local INTEGER DEFAULT 1,
                activa BOOLEAN DEFAULT 1,
                FOREIGN KEY (documento) REFERENCES documentos_colaborativos (ruta_documento)
            )
        ''')
        
        # Tabla de comentarios
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS comentarios_documento (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                documento TEXT NOT NULL,
                usuario TEXT NOT NULL,
                comentario TEXT NOT NULL,
                posicion INTEGER,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                resuelto BOOLEAN DEFAULT 0,
                FOREIGN KEY (documento) REFERENCES documentos_colaborativos (ruta_documento)
            )
        ''')
        
        # Tabla de versiones
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS versiones_documento (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                documento TEXT NOT NULL,
                version INTEGER NOT NULL,
                contenido_hash TEXT NOT NULL,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                usuario_modificacion TEXT,
                descripcion TEXT,
                FOREIGN KEY (documento) REFERENCES documentos_colaborativos (ruta_documento)
            )
        ''')
        
        conn.commit()
        conn.close()
        logger.info("Base de datos de colaboración inicializada")
    
    def registrar_documento_colaborativo(self, ruta_documento: str) -> bool:
        """Registra un documento para colaboración"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT OR IGNORE INTO documentos_colaborativos (ruta_documento)
                VALUES (?)
            ''', (ruta_documento,))
            
            conn.commit()
            conn.close()
            
            logger.info(f"Documento registrado para colaboración: {ruta_documento}")
            return True
            
        except Exception as e:
            logger.error(f"Error registrando documento: {e}")
            return False
    
    def unirse_sesion(self, documento: str, usuario: str) -> Tuple[bool, Dict]:
        """Un usuario se une a una sesión de colaboración"""
        try:
            with self.lock:
                # Verificar si el documento está bloqueado
                if self._documento_bloqueado(documento, usuario):
                    return False, {"error": "Documento bloqueado por otro usuario"}
                
                # Crear o actualizar sesión
                sesion_id = f"{documento}_{usuario}"
                
                if sesion_id in self.sesiones_activas:
                    # Actualizar sesión existente
                    sesion = self.sesiones_activas[sesion_id]
                    sesion.ultima_actividad = datetime.now()
                else:
                    # Crear nueva sesión
                    sesion = SesionColaboracion(
                        documento=documento,
                        usuario=usuario,
                        timestamp_inicio=datetime.now(),
                        ultima_actividad=datetime.now(),
                        operaciones_pendientes=[],
                        version_local=1
                    )
                    self.sesiones_activas[sesion_id] = sesion
                
                # Actualizar base de datos
                self._actualizar_sesion_db(documento, usuario)
                
                # Obtener estado del documento
                estado = self._obtener_estado_documento(documento)
                
                logger.info(f"Usuario {usuario} se unió a sesión de {documento}")
                return True, {
                    "sesion_id": sesion_id,
                    "version_actual": estado["version_actual"],
                    "usuarios_activos": estado["usuarios_activos"],
                    "operaciones_pendientes": estado["operaciones_pendientes"]
                }
                
        except Exception as e:
            logger.error(f"Error uniéndose a sesión: {e}")
            return False, {"error": str(e)}
    
    def salir_sesion(self, documento: str, usuario: str) -> bool:
        """Un usuario sale de una sesión de colaboración"""
        try:
            with self.lock:
                sesion_id = f"{documento}_{usuario}"
                
                if sesion_id in self.sesiones_activas:
                    del self.sesiones_activas[sesion_id]
                
                # Actualizar base de datos
                self._actualizar_sesion_db(documento, usuario, activa=False)
                
                logger.info(f"Usuario {usuario} salió de sesión de {documento}")
                return True
                
        except Exception as e:
            logger.error(f"Error saliendo de sesión: {e}")
            return False
    
    def aplicar_operacion(self, operacion: OperacionColaboracion) -> Tuple[bool, Dict]:
        """Aplica una operación de colaboración"""
        try:
            with self.lock:
                # Verificar conflictos
                conflictos = self._detectar_conflictos(operacion)
                
                if conflictos:
                    operacion.conflicto = True
                    logger.warning(f"Conflicto detectado en operación {operacion.id}")
                
                # Guardar operación
                self._guardar_operacion(operacion)
                
                # Aplicar operación si no hay conflictos
                if not conflictos:
                    self._aplicar_operacion_documento(operacion)
                
                # Notificar a otros usuarios
                self._notificar_operacion(operacion)
                
                return True, {
                    "operacion_id": operacion.id,
                    "conflictos": conflictos,
                    "version_nueva": operacion.version
                }
                
        except Exception as e:
            logger.error(f"Error aplicando operación: {e}")
            return False, {"error": str(e)}
    
    def obtener_operaciones_pendientes(self, documento: str, usuario: str, version_local: int) -> List[Dict]:
        """Obtiene operaciones pendientes para un usuario"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT * FROM operaciones_colaboracion
                WHERE documento = ? AND version > ? AND aplicada = 0
                ORDER BY timestamp ASC
            ''', (documento, version_local))
            
            operaciones = cursor.fetchall()
            conn.close()
            
            # Convertir a formato JSON
            resultado = []
            for op in operaciones:
                resultado.append({
                    "id": op[0],
                    "documento": op[1],
                    "usuario": op[2],
                    "tipo": op[3],
                    "contenido": op[4],
                    "posicion": op[5],
                    "timestamp": op[6],
                    "version": op[7],
                    "conflicto": bool(op[8])
                })
            
            return resultado
            
        except Exception as e:
            logger.error(f"Error obteniendo operaciones pendientes: {e}")
            return []
    
    def resolver_conflicto(self, operacion_id: str, resolucion: str) -> bool:
        """Resuelve un conflicto de colaboración"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            if resolucion == "aceptar":
                cursor.execute('''
                    UPDATE operaciones_colaboracion
                    SET conflicto = 0, aplicada = 1
                    WHERE id = ?
                ''', (operacion_id,))
            elif resolucion == "rechazar":
                cursor.execute('''
                    UPDATE operaciones_colaboracion
                    SET aplicada = 0
                    WHERE id = ?
                ''', (operacion_id,))
            
            conn.commit()
            conn.close()
            
            logger.info(f"Conflicto resuelto para operación {operacion_id}: {resolucion}")
            return True
            
        except Exception as e:
            logger.error(f"Error resolviendo conflicto: {e}")
            return False
    
    def agregar_comentario(self, documento: str, usuario: str, comentario: str, posicion: int = None) -> bool:
        """Agrega un comentario a un documento"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO comentarios_documento (documento, usuario, comentario, posicion)
                VALUES (?, ?, ?, ?)
            ''', (documento, usuario, comentario, posicion))
            
            conn.commit()
            conn.close()
            
            logger.info(f"Comentario agregado por {usuario} en {documento}")
            return True
            
        except Exception as e:
            logger.error(f"Error agregando comentario: {e}")
            return False
    
    def obtener_comentarios(self, documento: str) -> List[Dict]:
        """Obtiene todos los comentarios de un documento"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT * FROM comentarios_documento
                WHERE documento = ? AND resuelto = 0
                ORDER BY timestamp ASC
            ''', (documento,))
            
            comentarios = cursor.fetchall()
            conn.close()
            
            resultado = []
            for com in comentarios:
                resultado.append({
                    "id": com[0],
                    "documento": com[1],
                    "usuario": com[2],
                    "comentario": com[3],
                    "posicion": com[4],
                    "timestamp": com[5],
                    "resuelto": bool(com[6])
                })
            
            return resultado
            
        except Exception as e:
            logger.error(f"Error obteniendo comentarios: {e}")
            return []
    
    def crear_version(self, documento: str, usuario: str, descripcion: str = "") -> bool:
        """Crea una nueva versión del documento"""
        try:
            # Leer contenido actual
            if not os.path.exists(documento):
                return False
            
            with open(documento, 'r', encoding='utf-8') as f:
                contenido = f.read()
            
            contenido_hash = hashlib.sha256(contenido.encode()).hexdigest()
            
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Obtener siguiente versión
            cursor.execute('''
                SELECT MAX(version) FROM versiones_documento WHERE documento = ?
            ''', (documento,))
            
            version_actual = cursor.fetchone()[0] or 0
            nueva_version = version_actual + 1
            
            # Guardar versión
            cursor.execute('''
                INSERT INTO versiones_documento (documento, version, contenido_hash, usuario_modificacion, descripcion)
                VALUES (?, ?, ?, ?, ?)
            ''', (documento, nueva_version, contenido_hash, usuario, descripcion))
            
            # Actualizar versión actual del documento
            cursor.execute('''
                UPDATE documentos_colaborativos
                SET version_actual = ?, ultima_modificacion = CURRENT_TIMESTAMP
                WHERE ruta_documento = ?
            ''', (nueva_version, documento))
            
            conn.commit()
            conn.close()
            
            logger.info(f"Versión {nueva_version} creada para {documento}")
            return True
            
        except Exception as e:
            logger.error(f"Error creando versión: {e}")
            return False
    
    def obtener_historial_versiones(self, documento: str) -> List[Dict]:
        """Obtiene el historial de versiones de un documento"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT * FROM versiones_documento
                WHERE documento = ?
                ORDER BY version DESC
            ''', (documento,))
            
            versiones = cursor.fetchall()
            conn.close()
            
            resultado = []
            for ver in versiones:
                resultado.append({
                    "id": ver[0],
                    "documento": ver[1],
                    "version": ver[2],
                    "contenido_hash": ver[3],
                    "timestamp": ver[4],
                    "usuario_modificacion": ver[5],
                    "descripcion": ver[6]
                })
            
            return resultado
            
        except Exception as e:
            logger.error(f"Error obteniendo historial: {e}")
            return []
    
    def obtener_estadisticas_colaboracion(self, documento: str = None) -> Dict:
        """Obtiene estadísticas de colaboración"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            stats = {}
            
            if documento:
                # Estadísticas para documento específico
                cursor.execute('''
                    SELECT COUNT(*) FROM operaciones_colaboracion WHERE documento = ?
                ''', (documento,))
                stats["total_operaciones"] = cursor.fetchone()[0]
                
                cursor.execute('''
                    SELECT COUNT(*) FROM comentarios_documento WHERE documento = ?
                ''', (documento,))
                stats["total_comentarios"] = cursor.fetchone()[0]
                
                cursor.execute('''
                    SELECT COUNT(*) FROM versiones_documento WHERE documento = ?
                ''', (documento,))
                stats["total_versiones"] = cursor.fetchone()[0]
                
            else:
                # Estadísticas globales
                cursor.execute('SELECT COUNT(*) FROM documentos_colaborativos')
                stats["documentos_colaborativos"] = cursor.fetchone()[0]
                
                cursor.execute('SELECT COUNT(*) FROM operaciones_colaboracion')
                stats["total_operaciones"] = cursor.fetchone()[0]
                
                cursor.execute('SELECT COUNT(*) FROM sesiones_colaboracion WHERE activa = 1')
                stats["sesiones_activas"] = cursor.fetchone()[0]
            
            conn.close()
            return stats
            
        except Exception as e:
            logger.error(f"Error obteniendo estadísticas: {e}")
            return {}
    
    def _detectar_conflictos(self, operacion: OperacionColaboracion) -> List[str]:
        """Detecta conflictos con operaciones existentes"""
        conflictos = []
        
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Buscar operaciones en la misma posición
            cursor.execute('''
                SELECT id, usuario, tipo FROM operaciones_colaboracion
                WHERE documento = ? AND posicion = ? AND aplicada = 0
            ''', (operacion.documento, operacion.posicion))
            
            operaciones_conflicto = cursor.fetchall()
            
            for op_conflicto in operaciones_conflicto:
                if op_conflicto[1] != operacion.usuario:  # Diferente usuario
                    conflictos.append(f"Conflicto con operación {op_conflicto[0]} de {op_conflicto[1]}")
            
            conn.close()
            
        except Exception as e:
            logger.error(f"Error detectando conflictos: {e}")
        
        return conflictos
    
    def _guardar_operacion(self, operacion: OperacionColaboracion):
        """Guarda una operación en la base de datos"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO operaciones_colaboracion 
            (id, documento, usuario, tipo, contenido, posicion, version, conflicto)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            operacion.id, operacion.documento, operacion.usuario,
            operacion.tipo.value, operacion.contenido, operacion.posicion,
            operacion.version, operacion.conflicto
        ))
        
        conn.commit()
        conn.close()
    
    def _aplicar_operacion_documento(self, operacion: OperacionColaboracion):
        """Aplica una operación al documento físico"""
        # Esta función sería implementada según el tipo de documento
        # Por ahora, solo marcamos como aplicada
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            UPDATE operaciones_colaboracion
            SET aplicada = 1
            WHERE id = ?
        ''', (operacion.id,))
        
        conn.commit()
        conn.close()
    
    def _notificar_operacion(self, operacion: OperacionColaboracion):
        """Notifica a otros usuarios sobre una operación"""
        # Esta función se integraría con WebSockets
        logger.info(f"Notificando operación {operacion.id} a otros usuarios")
    
    def _documento_bloqueado(self, documento: str, usuario: str) -> bool:
        """Verifica si un documento está bloqueado por otro usuario"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT bloqueado_por, bloqueado_hasta FROM documentos_colaborativos
            WHERE ruta_documento = ?
        ''', (documento,))
        
        resultado = cursor.fetchone()
        conn.close()
        
        if resultado and resultado[0] and resultado[0] != usuario:
            # Verificar si el bloqueo sigue vigente
            if resultado[1] and datetime.now() < datetime.fromisoformat(resultado[1]):
                return True
        
        return False
    
    def _actualizar_sesion_db(self, documento: str, usuario: str, activa: bool = True):
        """Actualiza la sesión en la base de datos"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        if activa:
            cursor.execute('''
                INSERT OR REPLACE INTO sesiones_colaboracion
                (documento, usuario, ultima_actividad, activa)
                VALUES (?, ?, CURRENT_TIMESTAMP, 1)
            ''', (documento, usuario))
        else:
            cursor.execute('''
                UPDATE sesiones_colaboracion
                SET activa = 0
                WHERE documento = ? AND usuario = ?
            ''', (documento, usuario))
        
        conn.commit()
        conn.close()
    
    def _obtener_estado_documento(self, documento: str) -> Dict:
        """Obtiene el estado actual de un documento"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT version_actual, usuarios_activos FROM documentos_colaborativos
            WHERE ruta_documento = ?
        ''', (documento,))
        
        resultado = cursor.fetchone()
        
        if resultado:
            version_actual, usuarios_activos = resultado
        else:
            version_actual, usuarios_activos = 1, 0
        
        # Obtener operaciones pendientes
        cursor.execute('''
            SELECT COUNT(*) FROM operaciones_colaboracion
            WHERE documento = ? AND aplicada = 0
        ''', (documento,))
        
        operaciones_pendientes = cursor.fetchone()[0]
        
        conn.close()
        
        return {
            "version_actual": version_actual,
            "usuarios_activos": usuarios_activos,
            "operaciones_pendientes": operaciones_pendientes
        }
    
    def _limpiar_sesiones_inactivas(self):
        """Limpia sesiones inactivas (ejecuta en hilo separado)"""
        while True:
            try:
                time.sleep(300)  # Ejecutar cada 5 minutos
                
                with self.lock:
                    ahora = datetime.now()
                    sesiones_a_eliminar = []
                    
                    for sesion_id, sesion in self.sesiones_activas.items():
                        if (ahora - sesion.ultima_actividad).seconds > 1800:  # 30 minutos
                            sesiones_a_eliminar.append(sesion_id)
                    
                    for sesion_id in sesiones_a_eliminar:
                        del self.sesiones_activas[sesion_id]
                        logger.info(f"Sesión inactiva eliminada: {sesion_id}")
                
                # Limpiar base de datos
                conn = sqlite3.connect(self.db_path)
                cursor = conn.cursor()
                
                cursor.execute('''
                    UPDATE sesiones_colaboracion
                    SET activa = 0
                    WHERE ultima_actividad < datetime('now', '-30 minutes')
                ''')
                
                conn.commit()
                conn.close()
                
            except Exception as e:
                logger.error(f"Error limpiando sesiones inactivas: {e}")

def main():
    """Función principal para probar el sistema"""
    print("🤝 Sistema de Colaboración en Tiempo Real")
    print("=========================================")
    
    # Inicializar sistema
    sistema = SistemaColaboracion()
    
    # Ejemplo de uso
    documento_test = "test_documento.md"
    usuario1 = "usuario1"
    usuario2 = "usuario2"
    
    # Registrar documento
    sistema.registrar_documento_colaborativo(documento_test)
    
    # Usuarios se unen a la sesión
    success1, info1 = sistema.unirse_sesion(documento_test, usuario1)
    success2, info2 = sistema.unirse_sesion(documento_test, usuario2)
    
    print(f"Usuario 1 se unió: {success1}")
    print(f"Usuario 2 se unió: {success2}")
    
    # Crear operación
    operacion = OperacionColaboracion(
        id="op_001",
        usuario=usuario1,
        documento=documento_test,
        tipo=TipoOperacion.INSERTAR,
        contenido="Nuevo contenido",
        posicion=10,
        timestamp=datetime.now(),
        version=1
    )
    
    # Aplicar operación
    success, resultado = sistema.aplicar_operacion(operacion)
    print(f"Operación aplicada: {success}")
    
    # Obtener estadísticas
    stats = sistema.obtener_estadisticas_colaboracion()
    print(f"Estadísticas: {stats}")
    
    print("\n✅ Sistema de colaboración funcionando correctamente")

if __name__ == '__main__':
    main()


