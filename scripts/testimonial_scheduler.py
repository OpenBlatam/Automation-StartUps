#!/usr/bin/env python3
"""
Sistema de Programación Automática de Publicaciones
Programa publicaciones para publicación automática en redes sociales
"""

import json
import logging
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
from pathlib import Path

logger = logging.getLogger(__name__)


@dataclass
class ScheduledPost:
    """Publicación programada"""
    post_id: str
    platform: str
    content: str
    scheduled_time: datetime
    status: str  # "pending", "published", "failed", "cancelled"
    post_data: Dict[str, Any]
    created_at: datetime = None
    
    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now()


class PostScheduler:
    """Sistema de programación de publicaciones"""
    
    def __init__(self, schedule_file: Optional[str] = None):
        """
        Inicializa el programador
        
        Args:
            schedule_file: Archivo para almacenar programaciones
        """
        self.schedule_file = schedule_file or "data/scheduled_posts.json"
        self.scheduled_posts: List[ScheduledPost] = []
        self._load_schedule()
    
    def _load_schedule(self):
        """Carga programaciones desde archivo"""
        schedule_path = Path(self.schedule_file)
        if schedule_path.exists():
            try:
                with open(schedule_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.scheduled_posts = [
                        ScheduledPost(
                            post_id=item['post_id'],
                            platform=item['platform'],
                            content=item['content'],
                            scheduled_time=datetime.fromisoformat(item['scheduled_time']),
                            status=item['status'],
                            post_data=item['post_data'],
                            created_at=datetime.fromisoformat(item.get('created_at', datetime.now().isoformat()))
                        )
                        for item in data
                    ]
                logger.info(f"Programaciones cargadas: {len(self.scheduled_posts)} posts")
            except Exception as e:
                logger.warning(f"Error al cargar programaciones: {e}")
    
    def _save_schedule(self):
        """Guarda programaciones en archivo"""
        try:
            schedule_path = Path(self.schedule_file)
            schedule_path.parent.mkdir(parents=True, exist_ok=True)
            
            data = [
                {
                    'post_id': post.post_id,
                    'platform': post.platform,
                    'content': post.content,
                    'scheduled_time': post.scheduled_time.isoformat(),
                    'status': post.status,
                    'post_data': post.post_data,
                    'created_at': post.created_at.isoformat()
                }
                for post in self.scheduled_posts
            ]
            
            with open(schedule_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
        except Exception as e:
            logger.warning(f"Error al guardar programaciones: {e}")
    
    def schedule_post(
        self,
        post_data: Dict[str, Any],
        scheduled_time: datetime,
        platform: Optional[str] = None
    ) -> ScheduledPost:
        """
        Programa una publicación
        
        Args:
            post_data: Datos completos del post
            scheduled_time: Fecha y hora programada
            platform: Plataforma (opcional, se toma de post_data)
        
        Returns:
            ScheduledPost creado
        """
        post_id = post_data.get('metadata', {}).get('post_id', f"post_{datetime.now().timestamp()}")
        platform = platform or post_data.get('platform', 'linkedin')
        content = post_data.get('full_post', post_data.get('post_content', ''))
        
        scheduled_post = ScheduledPost(
            post_id=post_id,
            platform=platform,
            content=content,
            scheduled_time=scheduled_time,
            status="pending",
            post_data=post_data
        )
        
        self.scheduled_posts.append(scheduled_post)
        self._save_schedule()
        
        logger.info(f"Post programado: {post_id} para {scheduled_time}")
        return scheduled_post
    
    def get_pending_posts(self, before_time: Optional[datetime] = None) -> List[ScheduledPost]:
        """
        Obtiene posts pendientes listos para publicar
        
        Args:
            before_time: Obtener posts programados antes de esta hora
        
        Returns:
            Lista de posts pendientes
        """
        now = before_time or datetime.now()
        
        pending = [
            post for post in self.scheduled_posts
            if post.status == "pending" and post.scheduled_time <= now
        ]
        
        return sorted(pending, key=lambda x: x.scheduled_time)
    
    def get_upcoming_posts(self, days: int = 7) -> List[ScheduledPost]:
        """Obtiene posts programados para los próximos días"""
        end_date = datetime.now() + timedelta(days=days)
        
        upcoming = [
            post for post in self.scheduled_posts
            if post.status == "pending" and post.scheduled_time <= end_date
        ]
        
        return sorted(upcoming, key=lambda x: x.scheduled_time)
    
    def mark_as_published(self, post_id: str):
        """Marca un post como publicado"""
        for post in self.scheduled_posts:
            if post.post_id == post_id:
                post.status = "published"
                self._save_schedule()
                logger.info(f"Post {post_id} marcado como publicado")
                return
    
    def cancel_post(self, post_id: str):
        """Cancela una publicación programada"""
        for post in self.scheduled_posts:
            if post.post_id == post_id:
                post.status = "cancelled"
                self._save_schedule()
                logger.info(f"Post {post_id} cancelado")
                return
    
    def get_schedule_summary(self) -> Dict[str, Any]:
        """Obtiene resumen de programaciones"""
        status_counts = {}
        platform_counts = {}
        
        for post in self.scheduled_posts:
            status_counts[post.status] = status_counts.get(post.status, 0) + 1
            platform_counts[post.platform] = platform_counts.get(post.platform, 0) + 1
        
        pending = [p for p in self.scheduled_posts if p.status == "pending"]
        next_posts = sorted(pending, key=lambda x: x.scheduled_time)[:5] if pending else []
        
        return {
            "total_scheduled": len(self.scheduled_posts),
            "by_status": status_counts,
            "by_platform": platform_counts,
            "pending_count": len(pending),
            "next_posts": [
                {
                    "post_id": p.post_id,
                    "platform": p.platform,
                    "scheduled_time": p.scheduled_time.isoformat(),
                    "content_preview": p.content[:100] + "..." if len(p.content) > 100 else p.content
                }
                for p in next_posts
            ]
        }
    
    def export_schedule_ical(self, output_file: str) -> str:
        """Exporta programaciones a formato iCal"""
        output_path = Path(output_file)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        ical_content = ["BEGIN:VCALENDAR", "VERSION:2.0", "PRODID:-//Post Scheduler//EN"]
        
        for post in self.scheduled_posts:
            if post.status == "pending":
                end_time = post.scheduled_time + timedelta(hours=1)
                
                ical_content.extend([
                    "BEGIN:VEVENT",
                    f"DTSTART:{post.scheduled_time.strftime('%Y%m%dT%H%M%S')}",
                    f"DTEND:{end_time.strftime('%Y%m%dT%H%M%S')}",
                    f"SUMMARY:Publicar en {post.platform.upper()}",
                    f"DESCRIPTION:{post.content[:200]}",
                    f"LOCATION:{post.platform}",
                    f"UID:{post.post_id}",
                    "END:VEVENT"
                ])
        
        ical_content.append("END:VCALENDAR")
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write("\n".join(ical_content))
        
        logger.info(f"Calendario iCal exportado: {output_file}")
        return str(output_path)


