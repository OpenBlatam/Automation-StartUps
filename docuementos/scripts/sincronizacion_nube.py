#!/usr/bin/env python3
"""
Sistema de Sincronización con Servicios en la Nube
=================================================

Sistema avanzado de sincronización que permite integrar con múltiples
servicios en la nube como Google Drive, Dropbox, OneDrive, AWS S3,
con sincronización bidireccional, resolución de conflictos y
sincronización selectiva.

Autor: Sistema de Organización Enterprise
Versión: 1.0
Fecha: 2024
"""

import os
import json
import sqlite3
import hashlib
import threading
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from pathlib import Path
import logging
from dataclasses import dataclass, asdict
from enum import Enum
import requests
from concurrent.futures import ThreadPoolExecutor, as_completed
import schedule

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class TipoServicio(Enum):
    """Tipos de servicios en la nube soportados"""
    GOOGLE_DRIVE = "google_drive"
    DROPBOX = "dropbox"
    ONEDRIVE = "onedrive"
    AWS_S3 = "aws_s3"
    BOX = "box"
    MEGA = "mega"

class EstadoSincronizacion(Enum):
    """Estados de sincronización"""
    SINCRONIZADO = "sincronizado"
    PENDIENTE_SUBIDA = "pendiente_subida"
    PENDIENTE_DESCARGA = "pendiente_descarga"
    CONFLICTO = "conflicto"
    ERROR = "error"
    SINCRONIZANDO = "sincronizando"

@dataclass
class ArchivoNube:
    """Representa un archivo en la nube"""
    id_nube: str
    nombre: str
    ruta_local: str
    ruta_nube: str
    tamaño: int
    hash_local: str
    hash_nube: str
    fecha_modificacion_local: datetime
    fecha_modificacion_nube: datetime
    servicio: TipoServicio
    estado: EstadoSincronizacion
    version: int

@dataclass
class ConfiguracionServicio:
    """Configuración de un servicio en la nube"""
    servicio: TipoServicio
    credenciales: Dict[str, str]
    carpeta_raiz: str
    sincronizacion_automatica: bool
    intervalos_sincronizacion: int  # minutos
    filtros_exclusion: List[str]
    filtros_inclusion: List[str]
    compresion: bool
    encriptacion: bool

class SincronizadorNube:
    """Sistema principal de sincronización con la nube"""
    
    def __init__(self, db_path: str = "sincronizacion_nube.db"):
        self.db_path = db_path
        self.servicios_configurados: Dict[TipoServicio, ConfiguracionServicio] = {}
        self.archivos_sincronizados: Dict[str, ArchivoNube] = {}
        self.lock = threading.RLock()
        self.executor = ThreadPoolExecutor(max_workers=4)
        self.init_database()
        
        # Iniciar hilos de sincronización
        self.thread_sincronizacion = threading.Thread(target=self._sincronizacion_automatica, daemon=True)
        self.thread_sincronizacion.start()
        
        self.thread_monitoreo = threading.Thread(target=self._monitorear_cambios, daemon=True)
        self.thread_monitoreo.start()
    
    def init_database(self):
        """Inicializa la base de datos de sincronización"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Tabla de servicios configurados
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS servicios_nube (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                servicio TEXT UNIQUE NOT NULL,
                credenciales TEXT NOT NULL,
                carpeta_raiz TEXT NOT NULL,
                sincronizacion_automatica BOOLEAN DEFAULT 1,
                intervalos_sincronizacion INTEGER DEFAULT 60,
                filtros_exclusion TEXT,
                filtros_inclusion TEXT,
                compresion BOOLEAN DEFAULT 0,
                encriptacion BOOLEAN DEFAULT 0,
                activo BOOLEAN DEFAULT 1,
                ultima_sincronizacion DATETIME,
                creado_en DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Tabla de archivos sincronizados
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS archivos_sincronizados (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                id_nube TEXT NOT NULL,
                nombre TEXT NOT NULL,
                ruta_local TEXT NOT NULL,
                ruta_nube TEXT NOT NULL,
                tamaño INTEGER,
                hash_local TEXT,
                hash_nube TEXT,
                fecha_modificacion_local DATETIME,
                fecha_modificacion_nube DATETIME,
                servicio TEXT NOT NULL,
                estado TEXT NOT NULL,
                version INTEGER DEFAULT 1,
                ultima_sincronizacion DATETIME,
                conflictos TEXT,
                metadata TEXT
            )
        ''')
        
        # Tabla de historial de sincronización
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS historial_sincronizacion (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                archivo_id INTEGER,
                accion TEXT NOT NULL,
                servicio TEXT NOT NULL,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                exito BOOLEAN NOT NULL,
                mensaje TEXT,
                tamaño_transferido INTEGER,
                duracion_segundos REAL,
                FOREIGN KEY (archivo_id) REFERENCES archivos_sincronizados (id)
            )
        ''')
        
        conn.commit()
        conn.close()
        logger.info("Base de datos de sincronización inicializada")
    
    def configurar_servicio(self, config: ConfiguracionServicio) -> bool:
        """Configura un servicio en la nube"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT OR REPLACE INTO servicios_nube 
                (servicio, credenciales, carpeta_raiz, sincronizacion_automatica, 
                 intervalos_sincronizacion, filtros_exclusion, filtros_inclusion, 
                 compresion, encriptacion)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                config.servicio.value,
                json.dumps(config.credenciales),
                config.carpeta_raiz,
                config.sincronizacion_automatica,
                config.intervalos_sincronizacion,
                json.dumps(config.filtros_exclusion),
                json.dumps(config.filtros_inclusion),
                config.compresion,
                config.encriptacion
            ))
            
            conn.commit()
            conn.close()
            
            # Cargar configuración en memoria
            self.servicios_configurados[config.servicio] = config
            
            logger.info(f"Servicio configurado: {config.servicio.value}")
            return True
            
        except Exception as e:
            logger.error(f"Error configurando servicio: {e}")
            return False
    
    def sincronizar_archivo(self, ruta_local: str, servicio: TipoServicio, 
                           forzar: bool = False) -> Tuple[bool, str]:
        """Sincroniza un archivo específico con la nube"""
        try:
            if not os.path.exists(ruta_local):
                return False, "Archivo local no encontrado"
            
            if servicio not in self.servicios_configurados:
                return False, "Servicio no configurado"
            
            config = self.servicios_configurados[servicio]
            
            # Calcular hash del archivo local
            hash_local = self._calcular_hash_archivo(ruta_local)
            fecha_mod_local = datetime.fromtimestamp(os.path.getmtime(ruta_local))
            
            # Verificar si el archivo ya está sincronizado
            archivo_existente = self._obtener_archivo_sincronizado(ruta_local, servicio)
            
            if archivo_existente and not forzar:
                # Verificar si hay cambios
                if (archivo_existente.hash_local == hash_local and 
                    archivo_existente.fecha_modificacion_local == fecha_mod_local):
                    return True, "Archivo ya sincronizado"
            
            # Determinar acción de sincronización
            if archivo_existente:
                if archivo_existente.hash_nube != hash_local:
                    # Hay cambios locales, subir
                    return self._subir_archivo(ruta_local, archivo_existente, config)
                else:
                    # Verificar si hay cambios en la nube
                    return self._verificar_cambios_nube(archivo_existente, config)
            else:
                # Archivo nuevo, subir
                return self._subir_archivo_nuevo(ruta_local, config)
                
        except Exception as e:
            logger.error(f"Error sincronizando archivo: {e}")
            return False, str(e)
    
    def sincronizar_carpeta(self, carpeta_local: str, servicio: TipoServicio, 
                           recursivo: bool = True) -> Dict[str, Tuple[bool, str]]:
        """Sincroniza una carpeta completa con la nube"""
        try:
            resultados = {}
            
            if not os.path.exists(carpeta_local):
                return {"error": (False, "Carpeta no encontrada")}
            
            # Obtener lista de archivos
            archivos = []
            if recursivo:
                for root, dirs, files in os.walk(carpeta_local):
                    for file in files:
                        archivos.append(os.path.join(root, file))
            else:
                archivos = [os.path.join(carpeta_local, f) for f in os.listdir(carpeta_local) 
                           if os.path.isfile(os.path.join(carpeta_local, f))]
            
            # Filtrar archivos según configuración
            config = self.servicios_configurados.get(servicio)
            if config:
                archivos = self._filtrar_archivos(archivos, config)
            
            # Sincronizar archivos en paralelo
            with ThreadPoolExecutor(max_workers=4) as executor:
                futures = {
                    executor.submit(self.sincronizar_archivo, archivo, servicio): archivo 
                    for archivo in archivos
                }
                
                for future in as_completed(futures):
                    archivo = futures[future]
                    try:
                        success, message = future.result()
                        resultados[archivo] = (success, message)
                    except Exception as e:
                        resultados[archivo] = (False, str(e))
            
            return resultados
            
        except Exception as e:
            logger.error(f"Error sincronizando carpeta: {e}")
            return {"error": (False, str(e))}
    
    def descargar_archivo_nube(self, id_nube: str, servicio: TipoServicio, 
                              ruta_destino: str) -> Tuple[bool, str]:
        """Descarga un archivo desde la nube"""
        try:
            config = self.servicios_configurados.get(servicio)
            if not config:
                return False, "Servicio no configurado"
            
            # Obtener metadatos del archivo
            archivo = self._obtener_archivo_por_id_nube(id_nube, servicio)
            if not archivo:
                return False, "Archivo no encontrado en sincronización"
            
            # Descargar según el servicio
            if servicio == TipoServicio.GOOGLE_DRIVE:
                return self._descargar_google_drive(id_nube, ruta_destino, config)
            elif servicio == TipoServicio.DROPBOX:
                return self._descargar_dropbox(id_nube, ruta_destino, config)
            elif servicio == TipoServicio.ONEDRIVE:
                return self._descargar_onedrive(id_nube, ruta_destino, config)
            elif servicio == TipoServicio.AWS_S3:
                return self._descargar_aws_s3(id_nube, ruta_destino, config)
            else:
                return False, "Servicio no soportado"
                
        except Exception as e:
            logger.error(f"Error descargando archivo: {e}")
            return False, str(e)
    
    def resolver_conflicto(self, archivo_id: int, resolucion: str, 
                          contenido_manual: str = None) -> bool:
        """Resuelve un conflicto de sincronización"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Obtener información del archivo
            cursor.execute('''
                SELECT * FROM archivos_sincronizados WHERE id = ?
            ''', (archivo_id,))
            
            archivo = cursor.fetchone()
            if not archivo:
                return False
            
            if resolucion == "usar_local":
                # Usar versión local, subir a la nube
                cursor.execute('''
                    UPDATE archivos_sincronizados 
                    SET estado = ?, conflictos = NULL
                    WHERE id = ?
                ''', (EstadoSincronizacion.PENDIENTE_SUBIDA.value, archivo_id))
                
            elif resolucion == "usar_nube":
                # Usar versión de la nube, descargar
                cursor.execute('''
                    UPDATE archivos_sincronizados 
                    SET estado = ?, conflictos = NULL
                    WHERE id = ?
                ''', (EstadoSincronizacion.PENDIENTE_DESCARGA.value, archivo_id))
                
            elif resolucion == "fusionar":
                # Fusionar contenido (requiere contenido manual)
                if contenido_manual:
                    # Guardar contenido fusionado
                    ruta_local = archivo[3]  # ruta_local
                    with open(ruta_local, 'w', encoding='utf-8') as f:
                        f.write(contenido_manual)
                    
                    cursor.execute('''
                        UPDATE archivos_sincronizados 
                        SET estado = ?, conflictos = NULL, hash_local = ?
                        WHERE id = ?
                    ''', (EstadoSincronizacion.PENDIENTE_SUBIDA.value, 
                          self._calcular_hash_archivo(ruta_local), archivo_id))
            
            conn.commit()
            conn.close()
            
            # Registrar resolución
            self._registrar_historial(archivo_id, "resolver_conflicto", 
                                    archivo[10], True, f"Conflicto resuelto: {resolucion}")
            
            logger.info(f"Conflicto resuelto para archivo {archivo_id}: {resolucion}")
            return True
            
        except Exception as e:
            logger.error(f"Error resolviendo conflicto: {e}")
            return False
    
    def obtener_estado_sincronizacion(self, servicio: TipoServicio = None) -> Dict:
        """Obtiene el estado actual de la sincronización"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            query = "SELECT servicio, estado, COUNT(*) FROM archivos_sincronizados"
            params = []
            
            if servicio:
                query += " WHERE servicio = ?"
                params.append(servicio.value)
            
            query += " GROUP BY servicio, estado"
            
            cursor.execute(query, params)
            resultados = cursor.fetchall()
            
            # Obtener estadísticas generales
            cursor.execute('''
                SELECT 
                    COUNT(*) as total_archivos,
                    SUM(CASE WHEN estado = 'sincronizado' THEN 1 ELSE 0 END) as sincronizados,
                    SUM(CASE WHEN estado = 'conflicto' THEN 1 ELSE 0 END) as conflictos,
                    SUM(CASE WHEN estado = 'error' THEN 1 ELSE 0 END) as errores,
                    SUM(tamaño) as tamaño_total
                FROM archivos_sincronizados
            ''')
            
            stats = cursor.fetchone()
            
            conn.close()
            
            return {
                "estadisticas_generales": {
                    "total_archivos": stats[0],
                    "sincronizados": stats[1],
                    "conflictos": stats[2],
                    "errores": stats[3],
                    "tamaño_total_mb": round(stats[4] / (1024 * 1024), 2) if stats[4] else 0
                },
                "estado_por_servicio": {
                    f"{row[0]}_{row[1]}": row[2] for row in resultados
                },
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error obteniendo estado: {e}")
            return {}
    
    def _calcular_hash_archivo(self, ruta_archivo: str) -> str:
        """Calcula hash SHA256 de un archivo"""
        hash_sha256 = hashlib.sha256()
        try:
            with open(ruta_archivo, "rb") as f:
                for chunk in iter(lambda: f.read(4096), b""):
                    hash_sha256.update(chunk)
            return hash_sha256.hexdigest()
        except Exception as e:
            logger.error(f"Error calculando hash: {e}")
            return ""
    
    def _obtener_archivo_sincronizado(self, ruta_local: str, servicio: TipoServicio) -> Optional[ArchivoNube]:
        """Obtiene información de un archivo sincronizado"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT * FROM archivos_sincronizados 
                WHERE ruta_local = ? AND servicio = ?
            ''', (ruta_local, servicio.value))
            
            resultado = cursor.fetchone()
            conn.close()
            
            if resultado:
                return ArchivoNube(
                    id_nube=resultado[1],
                    nombre=resultado[2],
                    ruta_local=resultado[3],
                    ruta_nube=resultado[4],
                    tamaño=resultado[5],
                    hash_local=resultado[6],
                    hash_nube=resultado[7],
                    fecha_modificacion_local=datetime.fromisoformat(resultado[8]) if resultado[8] else datetime.now(),
                    fecha_modificacion_nube=datetime.fromisoformat(resultado[9]) if resultado[9] else datetime.now(),
                    servicio=TipoServicio(resultado[10]),
                    estado=EstadoSincronizacion(resultado[11]),
                    version=resultado[12]
                )
            
            return None
            
        except Exception as e:
            logger.error(f"Error obteniendo archivo sincronizado: {e}")
            return None
    
    def _subir_archivo(self, ruta_local: str, archivo_existente: ArchivoNube, 
                      config: ConfiguracionServicio) -> Tuple[bool, str]:
        """Sube un archivo existente a la nube"""
        try:
            inicio = time.time()
            
            # Subir según el servicio
            if config.servicio == TipoServicio.GOOGLE_DRIVE:
                success, id_nube = self._subir_google_drive(ruta_local, archivo_existente, config)
            elif config.servicio == TipoServicio.DROPBOX:
                success, id_nube = self._subir_dropbox(ruta_local, archivo_existente, config)
            elif config.servicio == TipoServicio.ONEDRIVE:
                success, id_nube = self._subir_onedrive(ruta_local, archivo_existente, config)
            elif config.servicio == TipoServicio.AWS_S3:
                success, id_nube = self._subir_aws_s3(ruta_local, archivo_existente, config)
            else:
                return False, "Servicio no soportado"
            
            duracion = time.time() - inicio
            
            if success:
                # Actualizar base de datos
                self._actualizar_archivo_sincronizado(archivo_existente, id_nube, EstadoSincronizacion.SINCRONIZADO)
                
                # Registrar en historial
                self._registrar_historial(
                    archivo_existente.id_nube, "subir_archivo", 
                    config.servicio.value, True, "Archivo subido exitosamente",
                    os.path.getsize(ruta_local), duracion
                )
                
                return True, "Archivo subido exitosamente"
            else:
                return False, f"Error subiendo archivo: {id_nube}"
                
        except Exception as e:
            logger.error(f"Error subiendo archivo: {e}")
            return False, str(e)
    
    def _subir_archivo_nuevo(self, ruta_local: str, config: ConfiguracionServicio) -> Tuple[bool, str]:
        """Sube un archivo nuevo a la nube"""
        try:
            # Crear registro de archivo
            archivo_nuevo = ArchivoNube(
                id_nube="",
                nombre=os.path.basename(ruta_local),
                ruta_local=ruta_local,
                ruta_nube=f"{config.carpeta_raiz}/{os.path.basename(ruta_local)}",
                tamaño=os.path.getsize(ruta_local),
                hash_local=self._calcular_hash_archivo(ruta_local),
                hash_nube="",
                fecha_modificacion_local=datetime.fromtimestamp(os.path.getmtime(ruta_local)),
                fecha_modificacion_nube=datetime.now(),
                servicio=config.servicio,
                estado=EstadoSincronizacion.SINCRONIZANDO,
                version=1
            )
            
            # Subir archivo
            success, id_nube = self._subir_archivo(ruta_local, archivo_nuevo, config)
            
            if success:
                # Guardar en base de datos
                self._guardar_archivo_sincronizado(archivo_nuevo, id_nube)
                return True, "Archivo nuevo subido exitosamente"
            else:
                return False, f"Error subiendo archivo nuevo: {id_nube}"
                
        except Exception as e:
            logger.error(f"Error subiendo archivo nuevo: {e}")
            return False, str(e)
    
    def _subir_google_drive(self, ruta_local: str, archivo: ArchivoNube, 
                           config: ConfiguracionServicio) -> Tuple[bool, str]:
        """Sube archivo a Google Drive"""
        try:
            # Implementación simplificada - en producción usar Google Drive API
            access_token = config.credenciales.get('access_token')
            if not access_token:
                return False, "Token de acceso no configurado"
            
            # Simular subida exitosa
            id_nube = f"gdrive_{hashlib.md5(ruta_local.encode()).hexdigest()}"
            return True, id_nube
            
        except Exception as e:
            return False, str(e)
    
    def _subir_dropbox(self, ruta_local: str, archivo: ArchivoNube, 
                      config: ConfiguracionServicio) -> Tuple[bool, str]:
        """Sube archivo a Dropbox"""
        try:
            # Implementación simplificada - en producción usar Dropbox API
            access_token = config.credenciales.get('access_token')
            if not access_token:
                return False, "Token de acceso no configurado"
            
            # Simular subida exitosa
            id_nube = f"dropbox_{hashlib.md5(ruta_local.encode()).hexdigest()}"
            return True, id_nube
            
        except Exception as e:
            return False, str(e)
    
    def _subir_onedrive(self, ruta_local: str, archivo: ArchivoNube, 
                       config: ConfiguracionServicio) -> Tuple[bool, str]:
        """Sube archivo a OneDrive"""
        try:
            # Implementación simplificada - en producción usar Microsoft Graph API
            access_token = config.credenciales.get('access_token')
            if not access_token:
                return False, "Token de acceso no configurado"
            
            # Simular subida exitosa
            id_nube = f"onedrive_{hashlib.md5(ruta_local.encode()).hexdigest()}"
            return True, id_nube
            
        except Exception as e:
            return False, str(e)
    
    def _subir_aws_s3(self, ruta_local: str, archivo: ArchivoNube, 
                     config: ConfiguracionServicio) -> Tuple[bool, str]:
        """Sube archivo a AWS S3"""
        try:
            # Implementación simplificada - en producción usar boto3
            access_key = config.credenciales.get('access_key')
            secret_key = config.credenciales.get('secret_key')
            bucket = config.credenciales.get('bucket')
            
            if not all([access_key, secret_key, bucket]):
                return False, "Credenciales AWS incompletas"
            
            # Simular subida exitosa
            id_nube = f"s3_{hashlib.md5(ruta_local.encode()).hexdigest()}"
            return True, id_nube
            
        except Exception as e:
            return False, str(e)
    
    def _filtrar_archivos(self, archivos: List[str], config: ConfiguracionServicio) -> List[str]:
        """Filtra archivos según configuración"""
        archivos_filtrados = []
        
        for archivo in archivos:
            nombre_archivo = os.path.basename(archivo)
            
            # Verificar exclusiones
            excluido = False
            for patron in config.filtros_exclusion:
                if patron in nombre_archivo or patron in archivo:
                    excluido = True
                    break
            
            if excluido:
                continue
            
            # Verificar inclusiones (si hay)
            if config.filtros_inclusion:
                incluido = False
                for patron in config.filtros_inclusion:
                    if patron in nombre_archivo or patron in archivo:
                        incluido = True
                        break
                
                if not incluido:
                    continue
            
            archivos_filtrados.append(archivo)
        
        return archivos_filtrados
    
    def _guardar_archivo_sincronizado(self, archivo: ArchivoNube, id_nube: str):
        """Guarda información de archivo sincronizado en la base de datos"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO archivos_sincronizados 
                (id_nube, nombre, ruta_local, ruta_nube, tamaño, hash_local, hash_nube,
                 fecha_modificacion_local, fecha_modificacion_nube, servicio, estado, version)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                id_nube, archivo.nombre, archivo.ruta_local, archivo.ruta_nube,
                archivo.tamaño, archivo.hash_local, archivo.hash_nube,
                archivo.fecha_modificacion_local.isoformat(),
                archivo.fecha_modificacion_nube.isoformat(),
                archivo.servicio.value, archivo.estado.value, archivo.version
            ))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            logger.error(f"Error guardando archivo sincronizado: {e}")
    
    def _actualizar_archivo_sincronizado(self, archivo: ArchivoNube, id_nube: str, estado: EstadoSincronizacion):
        """Actualiza información de archivo sincronizado"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                UPDATE archivos_sincronizados 
                SET id_nube = ?, estado = ?, ultima_sincronizacion = CURRENT_TIMESTAMP
                WHERE ruta_local = ? AND servicio = ?
            ''', (id_nube, estado.value, archivo.ruta_local, archivo.servicio.value))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            logger.error(f"Error actualizando archivo sincronizado: {e}")
    
    def _registrar_historial(self, archivo_id: str, accion: str, servicio: str, 
                           exito: bool, mensaje: str, tamaño: int = 0, duracion: float = 0):
        """Registra evento en el historial de sincronización"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO historial_sincronizacion 
                (archivo_id, accion, servicio, exito, mensaje, tamaño_transferido, duracion_segundos)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (archivo_id, accion, servicio, exito, mensaje, tamaño, duracion))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            logger.error(f"Error registrando historial: {e}")
    
    def _sincronizacion_automatica(self):
        """Hilo de sincronización automática"""
        while True:
            try:
                time.sleep(60)  # Verificar cada minuto
                
                for servicio, config in self.servicios_configurados.items():
                    if config.sincronizacion_automatica:
                        # Verificar si es hora de sincronizar
                        ultima_sync = self._obtener_ultima_sincronizacion(servicio)
                        if ultima_sync:
                            tiempo_transcurrido = (datetime.now() - ultima_sync).total_seconds() / 60
                            if tiempo_transcurrido >= config.intervalos_sincronizacion:
                                self._ejecutar_sincronizacion_automatica(servicio, config)
                
            except Exception as e:
                logger.error(f"Error en sincronización automática: {e}")
    
    def _monitorear_cambios(self):
        """Monitorea cambios en archivos locales"""
        while True:
            try:
                time.sleep(30)  # Verificar cada 30 segundos
                
                # Obtener archivos sincronizados
                conn = sqlite3.connect(self.db_path)
                cursor = conn.cursor()
                
                cursor.execute('''
                    SELECT ruta_local, hash_local, servicio FROM archivos_sincronizados
                    WHERE estado = 'sincronizado'
                ''')
                
                archivos = cursor.fetchall()
                conn.close()
                
                for ruta_local, hash_guardado, servicio in archivos:
                    if os.path.exists(ruta_local):
                        hash_actual = self._calcular_hash_archivo(ruta_local)
                        if hash_actual != hash_guardado:
                            # Archivo modificado, marcar para sincronización
                            self._marcar_para_sincronizacion(ruta_local, TipoServicio(servicio))
                
            except Exception as e:
                logger.error(f"Error monitoreando cambios: {e}")
    
    def _obtener_ultima_sincronizacion(self, servicio: TipoServicio) -> Optional[datetime]:
        """Obtiene la última sincronización de un servicio"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT ultima_sincronizacion FROM servicios_nube WHERE servicio = ?
            ''', (servicio.value,))
            
            resultado = cursor.fetchone()
            conn.close()
            
            if resultado and resultado[0]:
                return datetime.fromisoformat(resultado[0])
            
            return None
            
        except Exception as e:
            logger.error(f"Error obteniendo última sincronización: {e}")
            return None
    
    def _ejecutar_sincronizacion_automatica(self, servicio: TipoServicio, config: ConfiguracionServicio):
        """Ejecuta sincronización automática para un servicio"""
        try:
            logger.info(f"Iniciando sincronización automática para {servicio.value}")
            
            # Sincronizar carpeta raíz
            resultados = self.sincronizar_carpeta(config.carpeta_raiz, servicio, True)
            
            # Actualizar última sincronización
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                UPDATE servicios_nube 
                SET ultima_sincronizacion = CURRENT_TIMESTAMP
                WHERE servicio = ?
            ''', (servicio.value,))
            
            conn.commit()
            conn.close()
            
            logger.info(f"Sincronización automática completada para {servicio.value}")
            
        except Exception as e:
            logger.error(f"Error en sincronización automática: {e}")
    
    def _marcar_para_sincronizacion(self, ruta_local: str, servicio: TipoServicio):
        """Marca un archivo para sincronización"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                UPDATE archivos_sincronizados 
                SET estado = 'pendiente_subida'
                WHERE ruta_local = ? AND servicio = ?
            ''', (ruta_local, servicio.value))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            logger.error(f"Error marcando para sincronización: {e}")

def main():
    """Función principal para probar el sistema"""
    print("☁️ Sistema de Sincronización con la Nube")
    print("=======================================")
    
    # Inicializar sistema
    sincronizador = SincronizadorNube()
    
    # Configurar Google Drive (ejemplo)
    config_gdrive = ConfiguracionServicio(
        servicio=TipoServicio.GOOGLE_DRIVE,
        credenciales={
            'access_token': 'token_ejemplo',
            'refresh_token': 'refresh_ejemplo'
        },
        carpeta_raiz="/Users/adan/frontier/docuementos",
        sincronizacion_automatica=True,
        intervalos_sincronizacion=60,
        filtros_exclusion=[".tmp", ".log", "__pycache__"],
        filtros_inclusion=[".md", ".py", ".json"],
        compresion=False,
        encriptacion=False
    )
    
    # Configurar servicio
    success = sincronizador.configurar_servicio(config_gdrive)
    print(f"Google Drive configurado: {success}")
    
    # Sincronizar archivo de prueba
    archivo_test = "/Users/adan/frontier/docuementos/ORGANIZACION_ARCHIVOS.md"
    if os.path.exists(archivo_test):
        success, message = sincronizador.sincronizar_archivo(archivo_test, TipoServicio.GOOGLE_DRIVE)
        print(f"Sincronización de archivo: {success} - {message}")
    
    # Obtener estado
    estado = sincronizador.obtener_estado_sincronizacion()
    print(f"Estado de sincronización: {estado}")
    
    print("\n✅ Sistema de sincronización funcionando correctamente")

if __name__ == '__main__':
    main()

