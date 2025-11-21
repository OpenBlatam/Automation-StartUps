#!/usr/bin/env python3
"""
Sistema de cola para procesamiento de videos
Permite procesar videos de forma asíncrona y escalable
"""

import os
import json
import logging
import sqlite3
import threading
import time
from datetime import datetime
from typing import Dict, List, Any, Optional
from enum import Enum
from pathlib import Path

from tiktok_downloader import TikTokDownloader
from video_script_generator import VideoScriptGenerator
from video_editor import VideoEditor
from tiktok_analytics import TikTokAnalytics

# Importar notificaciones si están disponibles
try:
    from tiktok_notifications import NotificationManager
    NOTIFICATIONS_AVAILABLE = True
except ImportError:
    NOTIFICATIONS_AVAILABLE = False
    logger.warning("Sistema de notificaciones no disponible")

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class JobStatus(Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class TikTokQueueManager:
    """Gestor de cola para procesamiento de videos"""
    
    def __init__(self, db_path: Optional[str] = None, max_workers: int = 3):
        """
        Inicializa el gestor de cola
        
        Args:
            db_path: Ruta a la base de datos de cola
            max_workers: Número máximo de workers simultáneos
        """
        self.db_path = db_path or os.path.join(
            os.path.expanduser("~"), ".tiktok_queue.db"
        )
        self.max_workers = max_workers
        self.workers = []
        self.running = False
        self._init_database()
        
        # Componentes
        self.downloader = TikTokDownloader()
        self.script_generator = VideoScriptGenerator()
        self.editor = VideoEditor()
        self.analytics = TikTokAnalytics()
        
        # Notificaciones
        if NOTIFICATIONS_AVAILABLE:
            self.notifications = NotificationManager()
        else:
            self.notifications = None
    
    def _init_database(self):
        """Inicializa la base de datos de cola"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS jobs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                url TEXT NOT NULL,
                status TEXT NOT NULL DEFAULT 'pending',
                priority INTEGER DEFAULT 5,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                started_at TIMESTAMP,
                completed_at TIMESTAMP,
                processing_time REAL,
                result TEXT,
                error_message TEXT,
                retry_count INTEGER DEFAULT 0,
                max_retries INTEGER DEFAULT 3
            )
        """)
        
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_status ON jobs(status)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_priority ON jobs(priority DESC)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_created_at ON jobs(created_at)")
        
        conn.commit()
        conn.close()
    
    def add_job(self, url: str, priority: int = 5, max_retries: int = 3) -> int:
        """
        Agrega un trabajo a la cola
        
        Args:
            url: URL del video de TikTok
            priority: Prioridad (1-10, mayor = más prioritario)
            max_retries: Intentos máximos en caso de error
            
        Returns:
            ID del trabajo creado
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO jobs (url, status, priority, max_retries)
            VALUES (?, ?, ?, ?)
        """, (url, JobStatus.PENDING.value, priority, max_retries))
        
        job_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        logger.info(f"Trabajo agregado a la cola: ID={job_id}, URL={url}, Priority={priority}")
        return job_id
    
    def get_next_job(self) -> Optional[Dict[str, Any]]:
        """Obtiene el siguiente trabajo pendiente"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT id, url, priority, retry_count, max_retries
            FROM jobs
            WHERE status = ?
            ORDER BY priority DESC, created_at ASC
            LIMIT 1
        """, (JobStatus.PENDING.value,))
        
        row = cursor.fetchone()
        if not row:
            conn.close()
            return None
        
        job = {
            'id': row[0],
            'url': row[1],
            'priority': row[2],
            'retry_count': row[3],
            'max_retries': row[4]
        }
        
        # Marcar como procesando
        cursor.execute("""
            UPDATE jobs
            SET status = ?, started_at = ?
            WHERE id = ?
        """, (JobStatus.PROCESSING.value, datetime.now().isoformat(), job['id']))
        
        conn.commit()
        conn.close()
        
        return job
    
    def process_job(self, job: Dict[str, Any]) -> Dict[str, Any]:
        """
        Procesa un trabajo
        
        Args:
            job: Diccionario con información del trabajo
            
        Returns:
            Resultado del procesamiento
        """
        job_id = job['id']
        url = job['url']
        start_time = datetime.now()
        
        logger.info(f"Procesando trabajo {job_id}: {url}")
        
        # Notificar inicio
        if self.notifications:
            self.notifications.notify_processing_started(url, job_id)
        
        try:
            # 1. Descargar
            download_result = self.downloader.download_video(url)
            if not download_result.get('success'):
                raise Exception(f"Error al descargar: {download_result.get('message')}")
            
            video_path = download_result['file_path']
            
            # 2. Generar script
            script = self.script_generator.generate_script(video_path)
            
            # 3. Editar
            edit_result = self.editor.edit_video_from_dict(video_path, script)
            if not edit_result.get('success'):
                raise Exception(f"Error al editar: {edit_result.get('message')}")
            
            processing_time = (datetime.now() - start_time).total_seconds()
            
            result = {
                'success': True,
                'video_path': edit_result.get('output_path'),
                'file_size': edit_result.get('file_size'),
                'duration': edit_result.get('duration'),
                'processing_time': processing_time
            }
            
            # Actualizar trabajo como completado
            self._update_job_status(
                job_id,
                JobStatus.COMPLETED,
                result,
                processing_time
            )
            
            # Registrar en analytics
            self.analytics.record_processing({
                'url': url,
                'status': 'completed',
                'started_at': start_time.isoformat(),
                'completed_at': datetime.now().isoformat(),
                'processing_time': processing_time,
                'file_size': edit_result.get('file_size'),
                'duration': edit_result.get('duration'),
                'from_cache': download_result.get('from_cache', False)
            })
            
            logger.info(f"Trabajo {job_id} completado exitosamente")
            
            # Notificar completación
            if self.notifications:
                self.notifications.notify_processing_completed(url, result, job_id)
            
            return result
        
        except Exception as e:
            logger.error(f"Error procesando trabajo {job_id}: {e}", exc_info=True)
            
            # Intentar retry si es posible
            retry_count = job.get('retry_count', 0) + 1
            max_retries = job.get('max_retries', 3)
            
            if retry_count < max_retries:
                # Reintentar
                self._update_job_status(
                    job_id,
                    JobStatus.PENDING,
                    None,
                    None,
                    retry_count
                )
                logger.info(f"Trabajo {job_id} será reintentado ({retry_count}/{max_retries})")
            else:
                # Marcar como fallido
                self._update_job_status(
                    job_id,
                    JobStatus.FAILED,
                    None,
                    None,
                    retry_count,
                    str(e)
                )
                logger.error(f"Trabajo {job_id} falló después de {retry_count} intentos")
                
                # Notificar fallo final
                if self.notifications:
                    self.notifications.notify_processing_failed(url, str(e), job_id, retry_count)
            
            return {'success': False, 'error': str(e)}
    
    def _update_job_status(self, job_id: int, status: JobStatus, result: Optional[Dict],
                           processing_time: Optional[float], retry_count: Optional[int] = None,
                           error_message: Optional[str] = None):
        """Actualiza el estado de un trabajo"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        update_fields = ['status = ?']
        values = [status.value]
        
        if status == JobStatus.COMPLETED:
            update_fields.append('completed_at = ?')
            values.append(datetime.now().isoformat())
            if result:
                update_fields.append('result = ?')
                values.append(json.dumps(result))
        
        if processing_time is not None:
            update_fields.append('processing_time = ?')
            values.append(processing_time)
        
        if retry_count is not None:
            update_fields.append('retry_count = ?')
            values.append(retry_count)
        
        if error_message:
            update_fields.append('error_message = ?')
            values.append(error_message)
        
        values.append(job_id)
        
        cursor.execute(f"""
            UPDATE jobs
            SET {', '.join(update_fields)}
            WHERE id = ?
        """, values)
        
        conn.commit()
        conn.close()
    
    def worker_thread(self):
        """Thread worker que procesa trabajos"""
        logger.info("Worker iniciado")
        
        while self.running:
            job = self.get_next_job()
            
            if not job:
                time.sleep(1)  # Esperar antes de revisar nuevamente
                continue
            
            self.process_job(job)
    
    def start(self):
        """Inicia los workers"""
        if self.running:
            logger.warning("Workers ya están corriendo")
            return
        
        self.running = True
        self.workers = []
        
        for i in range(self.max_workers):
            worker = threading.Thread(target=self.worker_thread, daemon=True)
            worker.start()
            self.workers.append(worker)
            logger.info(f"Worker {i+1} iniciado")
    
    def stop(self):
        """Detiene los workers"""
        logger.info("Deteniendo workers...")
        self.running = False
        
        for worker in self.workers:
            worker.join(timeout=5)
        
        logger.info("Workers detenidos")
    
    def get_queue_stats(self) -> Dict[str, Any]:
        """Obtiene estadísticas de la cola"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT 
                status,
                COUNT(*) as count
            FROM jobs
            GROUP BY status
        """)
        
        stats = {row[0]: row[1] for row in cursor.fetchall()}
        
        cursor.execute("SELECT COUNT(*) FROM jobs WHERE status = 'pending'")
        pending = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM jobs WHERE status = 'processing'")
        processing = cursor.fetchone()[0]
        
        conn.close()
        
        return {
            'pending': stats.get('pending', 0),
            'processing': stats.get('processing', 0),
            'completed': stats.get('completed', 0),
            'failed': stats.get('failed', 0),
            'total': sum(stats.values())
        }


def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='Gestor de cola para TikTok Auto Edit')
    parser.add_argument('command', choices=['start', 'add', 'stats', 'list'], help='Comando')
    parser.add_argument('-u', '--url', help='URL de TikTok (para add)')
    parser.add_argument('-p', '--priority', type=int, default=5, help='Prioridad (1-10)')
    parser.add_argument('-w', '--workers', type=int, default=3, help='Número de workers')
    
    args = parser.parse_args()
    
    manager = TikTokQueueManager(max_workers=args.workers)
    
    if args.command == 'start':
        logger.info("Iniciando gestor de cola...")
        manager.start()
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            manager.stop()
    
    elif args.command == 'add':
        if not args.url:
            print("Error: URL requerida")
            sys.exit(1)
        job_id = manager.add_job(args.url, args.priority)
        print(f"✅ Trabajo agregado: ID={job_id}")
    
    elif args.command == 'stats':
        stats = manager.get_queue_stats()
        print(json.dumps(stats, indent=2))
    
    elif args.command == 'list':
        # Listar trabajos pendientes
        conn = sqlite3.connect(manager.db_path)
        cursor = conn.cursor()
        cursor.execute("""
            SELECT id, url, status, priority, created_at
            FROM jobs
            WHERE status IN ('pending', 'processing')
            ORDER BY priority DESC, created_at ASC
        """)
        jobs = cursor.fetchall()
        conn.close()
        
        if not jobs:
            print("No hay trabajos pendientes")
        else:
            print(f"\n{'ID':<5} {'Status':<12} {'Priority':<8} {'URL':<50}")
            print("-" * 80)
            for job in jobs:
                print(f"{job[0]:<5} {job[2]:<12} {job[3]:<8} {job[1][:47]}")


if __name__ == '__main__':
    import sys
    import time
    main()

