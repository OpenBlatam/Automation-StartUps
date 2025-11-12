#!/usr/bin/env python3
"""
Script para descubrir videos populares de IA de esta semana
Busca en YouTube, TikTok y otras plataformas videos sobre IA ordenados por popularidad
"""

import os
import sys
import json
import argparse
import logging
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
from pathlib import Path

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

try:
    import yt_dlp
    YT_DLP_AVAILABLE = True
except ImportError:
    YT_DLP_AVAILABLE = False
    logger.warning("yt-dlp no está instalado. Algunas funciones pueden no estar disponibles.")

try:
    from googleapiclient.discovery import build
    from googleapiclient.errors import HttpError
    YOUTUBE_API_AVAILABLE = True
except ImportError:
    YOUTUBE_API_AVAILABLE = False
    logger.warning("google-api-python-client no está instalado. YouTube API no disponible.")


class AIVideoDiscoverer:
    """Descubridor de videos populares de IA"""
    
    def __init__(self, youtube_api_key: Optional[str] = None):
        """
        Inicializa el descubridor de videos
        
        Args:
            youtube_api_key: API key de YouTube Data API v3 (opcional)
        """
        self.youtube_api_key = youtube_api_key or os.getenv('YOUTUBE_API_KEY')
        self.youtube_service = None
        
        if self.youtube_api_key and YOUTUBE_API_AVAILABLE:
            try:
                self.youtube_service = build('youtube', 'v3', developerKey=self.youtube_api_key)
                logger.info("YouTube API inicializada correctamente")
            except Exception as e:
                logger.warning(f"No se pudo inicializar YouTube API: {e}")
    
    def search_youtube_videos(
        self,
        query: str = "artificial intelligence AI",
        max_results: int = 10,
        days_back: int = 7,
        language: Optional[str] = None,
        exclude_language: str = "es"
    ) -> List[Dict[str, Any]]:
        """
        Busca videos populares de IA en YouTube
        
        Args:
            query: Términos de búsqueda
            max_results: Número máximo de resultados
            days_back: Días hacia atrás para buscar (por defecto 7 = esta semana)
            language: Idioma específico a buscar (None = todos excepto exclude_language)
            exclude_language: Idioma a excluir (por defecto español)
            
        Returns:
            Lista de videos encontrados con metadatos
        """
        if not self.youtube_service:
            logger.warning("YouTube API no disponible, usando yt-dlp para búsqueda básica")
            return self._search_with_ytdlp(query, max_results, days_back, language, exclude_language)
        
        videos = []
        try:
            # Calcular fecha de inicio (hace X días)
            published_after = (datetime.now() - timedelta(days=days_back)).isoformat() + 'Z'
            
            # Construir query de búsqueda
            search_query = query
            if language:
                search_query += f" lang:{language}"
            
            # Realizar búsqueda
            request = self.youtube_service.search().list(
                part='id,snippet',
                q=search_query,
                type='video',
                order='viewCount',  # Ordenar por número de vistas
                maxResults=max_results,
                publishedAfter=published_after,
                relevanceLanguage=language if language else None,
                videoDuration='short',  # Videos cortos (menos de 4 minutos)
                videoCategoryId='28',  # Ciencia y tecnología
            )
            
            response = request.execute()
            
            # Obtener detalles adicionales de cada video
            video_ids = [item['id']['videoId'] for item in response.get('items', [])]
            
            if video_ids:
                videos_request = self.youtube_service.videos().list(
                    part='statistics,contentDetails,snippet',
                    id=','.join(video_ids)
                )
                videos_response = videos_request.execute()
                
                for item in videos_response.get('items', []):
                    snippet = item['snippet']
                    stats = item.get('statistics', {})
                    details = item.get('contentDetails', {})
                    
                    # Filtrar por idioma si es necesario
                    video_lang = snippet.get('defaultAudioLanguage') or snippet.get('defaultLanguage', '')
                    if exclude_language and video_lang.startswith(exclude_language):
                        continue
                    
                    video_info = {
                        'id': item['id'],
                        'title': snippet.get('title', ''),
                        'description': snippet.get('description', ''),
                        'channel': snippet.get('channelTitle', ''),
                        'channel_id': snippet.get('channelId', ''),
                        'published_at': snippet.get('publishedAt', ''),
                        'url': f"https://www.youtube.com/watch?v={item['id']}",
                        'thumbnail': snippet.get('thumbnails', {}).get('high', {}).get('url', ''),
                        'view_count': int(stats.get('viewCount', 0)),
                        'like_count': int(stats.get('likeCount', 0)),
                        'duration': details.get('duration', ''),
                        'language': video_lang,
                        'tags': snippet.get('tags', []),
                        'platform': 'youtube'
                    }
                    
                    videos.append(video_info)
            
            # Ordenar por número de likes
            videos.sort(key=lambda x: x['like_count'], reverse=True)
            
            logger.info(f"Encontrados {len(videos)} videos de YouTube")
            
        except HttpError as e:
            logger.error(f"Error en YouTube API: {e}")
        except Exception as e:
            logger.error(f"Error buscando videos: {e}")
        
        return videos
    
    def _search_with_ytdlp(
        self,
        query: str,
        max_results: int,
        days_back: int,
        language: Optional[str],
        exclude_language: str
    ) -> List[Dict[str, Any]]:
        """Búsqueda básica usando yt-dlp cuando YouTube API no está disponible"""
        videos = []
        
        if not YT_DLP_AVAILABLE:
            logger.error("yt-dlp no disponible para búsqueda")
            return videos
        
        try:
            ydl_opts = {
                'quiet': True,
                'no_warnings': True,
                'extract_flat': True,
                'default_search': f'ytsearch{max_results}:{query}',
            }
            
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                results = ydl.extract_info(query, download=False)
                
                if 'entries' in results:
                    for entry in results['entries'][:max_results]:
                        if not entry:
                            continue
                        
                        # Filtrar por fecha (aproximado)
                        upload_date = entry.get('upload_date', '')
                        if upload_date:
                            try:
                                upload_dt = datetime.strptime(upload_date, '%Y%m%d')
                                if (datetime.now() - upload_dt).days > days_back:
                                    continue
                            except:
                                pass
                        
                        video_info = {
                            'id': entry.get('id', ''),
                            'title': entry.get('title', ''),
                            'description': entry.get('description', ''),
                            'channel': entry.get('uploader', ''),
                            'url': entry.get('url', f"https://www.youtube.com/watch?v={entry.get('id', '')}"),
                            'thumbnail': entry.get('thumbnail', ''),
                            'view_count': entry.get('view_count', 0),
                            'like_count': entry.get('like_count', 0),
                            'duration': entry.get('duration', 0),
                            'platform': 'youtube'
                        }
                        
                        videos.append(video_info)
            
            logger.info(f"Encontrados {len(videos)} videos con yt-dlp")
            
        except Exception as e:
            logger.error(f"Error en búsqueda yt-dlp: {e}")
        
        return videos
    
    def discover_popular_ai_videos(
        self,
        max_results: int = 20,
        days_back: int = 7,
        languages: Optional[List[str]] = None
    ) -> List[Dict[str, Any]]:
        """
        Descubre videos populares de IA de esta semana en múltiples idiomas
        
        Args:
            max_results: Número máximo de videos por idioma
            days_back: Días hacia atrás (por defecto 7 = esta semana)
            languages: Lista de idiomas a buscar (None = todos excepto español)
            
        Returns:
            Lista de videos encontrados ordenados por popularidad
        """
        all_videos = []
        
        # Términos de búsqueda relacionados con IA
        search_queries = [
            "artificial intelligence",
            "AI tutorial",
            "machine learning",
            "deep learning",
            "AI tools",
            "ChatGPT tutorial",
            "AI automation",
            "AI tips"
        ]
        
        # Idiomas a buscar (códigos ISO 639-1)
        if languages is None:
            languages = ['en', 'pt', 'fr', 'de', 'it', 'ja', 'ko', 'zh']  # Excluye español
        
        for lang in languages:
            logger.info(f"Buscando videos en idioma: {lang}")
            
            for query in search_queries[:3]:  # Limitar queries por idioma
                videos = self.search_youtube_videos(
                    query=query,
                    max_results=max_results // len(languages) // len(search_queries[:3]),
                    days_back=days_back,
                    language=lang,
                    exclude_language='es'
                )
                all_videos.extend(videos)
        
        # Eliminar duplicados por URL
        seen_urls = set()
        unique_videos = []
        for video in all_videos:
            if video['url'] not in seen_urls:
                seen_urls.add(video['url'])
                unique_videos.append(video)
        
        # Ordenar por número de likes
        unique_videos.sort(key=lambda x: x.get('like_count', 0), reverse=True)
        
        # Tomar los más populares
        top_videos = unique_videos[:max_results]
        
        logger.info(f"Total de videos únicos encontrados: {len(unique_videos)}")
        logger.info(f"Top {len(top_videos)} videos seleccionados")
        
        return top_videos


def main():
    parser = argparse.ArgumentParser(description='Descubre videos populares de IA de esta semana')
    parser.add_argument('--max-results', type=int, default=20, help='Número máximo de videos')
    parser.add_argument('--days-back', type=int, default=7, help='Días hacia atrás para buscar')
    parser.add_argument('--languages', nargs='+', help='Idiomas a buscar (ej: en pt fr)')
    parser.add_argument('--output', '-o', help='Archivo JSON de salida')
    parser.add_argument('--youtube-api-key', help='API key de YouTube (o usar YOUTUBE_API_KEY env var)')
    
    args = parser.parse_args()
    
    discoverer = AIVideoDiscoverer(youtube_api_key=args.youtube_api_key)
    
    videos = discoverer.discover_popular_ai_videos(
        max_results=args.max_results,
        days_back=args.days_back,
        languages=args.languages
    )
    
    # Guardar resultados
    output_data = {
        'discovered_at': datetime.now().isoformat(),
        'total_videos': len(videos),
        'videos': videos
    }
    
    if args.output:
        with open(args.output, 'w', encoding='utf-8') as f:
            json.dump(output_data, f, indent=2, ensure_ascii=False)
        logger.info(f"Resultados guardados en: {args.output}")
    else:
        print(json.dumps(output_data, indent=2, ensure_ascii=False))
    
    return 0


if __name__ == '__main__':
    sys.exit(main())

