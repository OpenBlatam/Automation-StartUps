#!/usr/bin/env python3
"""
Integración con Base de Datos para Testimonios
Guarda y recupera testimonios, publicaciones y métricas desde BD
"""

import logging
from typing import Dict, List, Any, Optional
from datetime import datetime
from pathlib import Path
import json

logger = logging.getLogger(__name__)


class DatabaseIntegration:
    """Integración con bases de datos para persistencia"""
    
    def __init__(self, db_type: str = "sqlite", connection_string: Optional[str] = None):
        """
        Inicializa la integración con BD
        
        Args:
            db_type: Tipo de BD ('sqlite', 'postgresql', 'mysql')
            connection_string: String de conexión (opcional)
        """
        self.db_type = db_type
        self.connection_string = connection_string
        self.connection = None
        self._initialize_database()
    
    def _initialize_database(self):
        """Inicializa la conexión a la base de datos"""
        if self.db_type == "sqlite":
            try:
                import sqlite3
                db_path = self.connection_string or "data/testimonials.db"
                Path(db_path).parent.mkdir(parents=True, exist_ok=True)
                self.connection = sqlite3.connect(db_path)
                self._create_tables()
                logger.info(f"Base de datos SQLite inicializada: {db_path}")
            except ImportError:
                logger.warning("sqlite3 no disponible")
        elif self.db_type == "postgresql":
            try:
                import psycopg2
                if self.connection_string:
                    self.connection = psycopg2.connect(self.connection_string)
                    self._create_tables()
                    logger.info("Base de datos PostgreSQL conectada")
            except ImportError:
                logger.warning("psycopg2 no está instalado. Instala con: pip install psycopg2-binary")
            except Exception as e:
                logger.error(f"Error al conectar a PostgreSQL: {e}")
    
    def _create_tables(self):
        """Crea tablas necesarias si no existen"""
        if not self.connection:
            return
        
        cursor = self.connection.cursor()
        
        # Tabla de testimonios
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS testimonials (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                testimonial_text TEXT NOT NULL,
                target_audience TEXT,
                platform TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                metadata TEXT
            )
        """)
        
        # Tabla de publicaciones generadas
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS posts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                testimonial_id INTEGER,
                post_content TEXT NOT NULL,
                platform TEXT,
                hashtags TEXT,
                engagement_score REAL,
                engagement_rate REAL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                post_data TEXT,
                FOREIGN KEY (testimonial_id) REFERENCES testimonials(id)
            )
        """)
        
        # Tabla de métricas de tracking
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS post_metrics (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                post_id INTEGER,
                likes INTEGER DEFAULT 0,
                comments INTEGER DEFAULT 0,
                shares INTEGER DEFAULT 0,
                impressions INTEGER DEFAULT 0,
                reach INTEGER DEFAULT 0,
                engagement_rate REAL,
                tracked_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (post_id) REFERENCES posts(id)
            )
        """)
        
        # Tabla de versiones
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS post_versions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                post_id INTEGER,
                version_id TEXT UNIQUE,
                post_data TEXT,
                changes_summary TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (post_id) REFERENCES posts(id)
            )
        """)
        
        self.connection.commit()
        logger.debug("Tablas de base de datos creadas/verificadas")
    
    def save_testimonial(
        self,
        testimonial_text: str,
        target_audience: Optional[str] = None,
        platform: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> int:
        """
        Guarda un testimonio en la BD
        
        Returns:
            ID del testimonio guardado
        """
        if not self.connection:
            logger.warning("No hay conexión a BD disponible")
            return -1
        
        cursor = self.connection.cursor()
        cursor.execute("""
            INSERT INTO testimonials (testimonial_text, target_audience, platform, metadata)
            VALUES (?, ?, ?, ?)
        """, (
            testimonial_text,
            target_audience,
            platform,
            json.dumps(metadata) if metadata else None
        ))
        
        self.connection.commit()
        testimonial_id = cursor.lastrowid
        logger.info(f"Testimonio guardado con ID: {testimonial_id}")
        return testimonial_id
    
    def save_post(
        self,
        post_data: Dict[str, Any],
        testimonial_id: Optional[int] = None
    ) -> int:
        """
        Guarda una publicación generada en la BD
        
        Returns:
            ID del post guardado
        """
        if not self.connection:
            logger.warning("No hay conexión a BD disponible")
            return -1
        
        cursor = self.connection.cursor()
        cursor.execute("""
            INSERT INTO posts (
                testimonial_id, post_content, platform, hashtags,
                engagement_score, engagement_rate, post_data
            )
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            testimonial_id,
            post_data.get('post_content', ''),
            post_data.get('platform', ''),
            json.dumps(post_data.get('hashtags', [])),
            post_data.get('engagement_prediction', {}).get('predicted_score', 0),
            post_data.get('engagement_prediction', {}).get('predicted_engagement_rate', 0),
            json.dumps(post_data)
        ))
        
        self.connection.commit()
        post_id = cursor.lastrowid
        logger.info(f"Post guardado con ID: {post_id}")
        return post_id
    
    def save_post_metrics(
        self,
        post_id: int,
        likes: int,
        comments: int,
        shares: int,
        impressions: int,
        reach: int
    ):
        """Guarda métricas reales de un post"""
        if not self.connection:
            return
        
        engagement_rate = ((likes + comments + shares) / impressions * 100) if impressions > 0 else 0
        
        cursor = self.connection.cursor()
        cursor.execute("""
            INSERT INTO post_metrics (
                post_id, likes, comments, shares, impressions, reach, engagement_rate
            )
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (post_id, likes, comments, shares, impressions, reach, engagement_rate))
        
        self.connection.commit()
        logger.info(f"Métricas guardadas para post {post_id}")
    
    def get_post_history(self, testimonial_id: Optional[int] = None) -> List[Dict[str, Any]]:
        """Obtiene historial de posts"""
        if not self.connection:
            return []
        
        cursor = self.connection.cursor()
        
        if testimonial_id:
            cursor.execute("""
                SELECT id, post_content, platform, engagement_score, engagement_rate, created_at
                FROM posts
                WHERE testimonial_id = ?
                ORDER BY created_at DESC
            """, (testimonial_id,))
        else:
            cursor.execute("""
                SELECT id, post_content, platform, engagement_score, engagement_rate, created_at
                FROM posts
                ORDER BY created_at DESC
                LIMIT 100
            """)
        
        rows = cursor.fetchall()
        return [
            {
                'id': row[0],
                'post_content': row[1],
                'platform': row[2],
                'engagement_score': row[3],
                'engagement_rate': row[4],
                'created_at': row[5]
            }
            for row in rows
        ]
    
    def get_post_with_metrics(self, post_id: int) -> Optional[Dict[str, Any]]:
        """Obtiene un post con sus métricas"""
        if not self.connection:
            return None
        
        cursor = self.connection.cursor()
        cursor.execute("""
            SELECT p.*, 
                   COALESCE(AVG(pm.engagement_rate), 0) as avg_engagement_rate,
                   COUNT(pm.id) as metrics_count
            FROM posts p
            LEFT JOIN post_metrics pm ON p.id = pm.post_id
            WHERE p.id = ?
            GROUP BY p.id
        """, (post_id,))
        
        row = cursor.fetchone()
        if not row:
            return None
        
        return {
            'id': row[0],
            'testimonial_id': row[1],
            'post_content': row[2],
            'platform': row[3],
            'hashtags': json.loads(row[4]) if row[4] else [],
            'engagement_score': row[5],
            'engagement_rate': row[6],
            'created_at': row[7],
            'post_data': json.loads(row[8]) if row[8] else {},
            'avg_engagement_rate': row[9],
            'metrics_count': row[10]
        }
    
    def close(self):
        """Cierra la conexión a la BD"""
        if self.connection:
            self.connection.close()
            logger.info("Conexión a BD cerrada")



