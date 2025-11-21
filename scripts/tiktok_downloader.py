#!/usr/bin/env python3
"""
Script para descargar videos de TikTok sin marca de agua
Usa yt-dlp para extraer y descargar videos de TikTok
"""

import os
import sys
import json
import argparse
import tempfile
import logging
import hashlib
from pathlib import Path
from typing import Optional, Dict, Any
from datetime import datetime

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

try:
    import yt_dlp
except ImportError:
    logger.error("yt-dlp no está instalado. Instálalo con: pip install yt-dlp")
    sys.exit(1)


class TikTokDownloader:
    """Clase para descargar videos de TikTok sin marca de agua"""
    
    def __init__(self, output_dir: Optional[str] = None, cache_dir: Optional[str] = None):
        """
        Inicializa el descargador de TikTok
        
        Args:
            output_dir: Directorio donde guardar los videos. Si es None, usa un directorio temporal
            cache_dir: Directorio para cache de videos descargados (opcional)
        """
        self.output_dir = output_dir or tempfile.mkdtemp(prefix="tiktok_downloads_")
        self.cache_dir = cache_dir or os.path.join(tempfile.gettempdir(), "tiktok_cache")
        Path(self.output_dir).mkdir(parents=True, exist_ok=True)
        Path(self.cache_dir).mkdir(parents=True, exist_ok=True)
        logger.info(f"TikTokDownloader inicializado. Output: {self.output_dir}, Cache: {self.cache_dir}")
        
    def get_cache_key(self, url: str) -> str:
        """
        Genera una clave de cache basada en la URL
        
        Args:
            url: URL del video de TikTok
            
        Returns:
            Clave de cache (hash MD5 de la URL)
        """
        return hashlib.md5(url.encode('utf-8')).hexdigest()
    
    def check_cache(self, url: str) -> Optional[Dict[str, Any]]:
        """
        Verifica si el video está en cache
        
        Args:
            url: URL del video de TikTok
            
        Returns:
            Información del video en cache o None
        """
        cache_key = self.get_cache_key(url)
        cache_file = os.path.join(self.cache_dir, f"{cache_key}.json")
        
        if os.path.exists(cache_file):
            try:
                with open(cache_file, 'r', encoding='utf-8') as f:
                    cache_data = json.load(f)
                
                # Verificar que el archivo de video aún existe
                if os.path.exists(cache_data.get('file_path')):
                    logger.info(f"Video encontrado en cache: {cache_key}")
                    return cache_data
                else:
                    # Archivo eliminado, limpiar cache
                    os.remove(cache_file)
            except Exception as e:
                logger.warning(f"Error leyendo cache: {e}")
        
        return None
    
    def save_to_cache(self, url: str, video_info: Dict[str, Any]) -> None:
        """
        Guarda información del video en cache
        
        Args:
            url: URL del video de TikTok
            video_info: Información del video descargado
        """
        try:
            cache_key = self.get_cache_key(url)
            cache_file = os.path.join(self.cache_dir, f"{cache_key}.json")
            
            cache_data = {
                **video_info,
                'cached_at': datetime.now().isoformat(),
                'original_url': url
            }
            
            with open(cache_file, 'w', encoding='utf-8') as f:
                json.dump(cache_data, f, indent=2, ensure_ascii=False)
            
            logger.info(f"Video guardado en cache: {cache_key}")
        except Exception as e:
            logger.warning(f"Error guardando en cache: {e}")
    
    def extract_video_id(self, url: str) -> Optional[str]:
        """
        Extrae el ID del video de la URL de TikTok
        
        Args:
            url: URL del video de TikTok
            
        Returns:
            ID del video o None si no se puede extraer
        """
        try:
            # Diferentes formatos de URL de TikTok
            if "vm.tiktok.com" in url or "vt.tiktok.com" in url:
                # URL corta, necesitamos seguir el redirect
                return None
            
            # URL completa: https://www.tiktok.com/@user/video/1234567890
            if "/video/" in url:
                parts = url.split("/video/")
                if len(parts) > 1:
                    video_id = parts[1].split("?")[0].split("#")[0]
                    return video_id
            
            return None
        except Exception as e:
            logger.error(f"Error extrayendo video ID: {e}")
            return None
    
    def download_video(self, url: str, filename: Optional[str] = None, use_cache: bool = True) -> Dict[str, Any]:
        """
        Descarga un video de TikTok sin marca de agua
        
        Args:
            url: URL del video de TikTok
            filename: Nombre del archivo de salida (opcional)
            use_cache: Si True, verifica cache antes de descargar
            
        Returns:
            Diccionario con información del video descargado
        """
        # Validar URL
        if not url or not isinstance(url, str):
            return {
                'success': False,
                'error': 'URL inválida',
                'message': 'La URL proporcionada no es válida'
            }
        
        url = url.strip()
        if not url.startswith('http://') and not url.startswith('https://'):
            url = 'https://' + url
        
        # Verificar cache
        if use_cache:
            cached = self.check_cache(url)
            if cached:
                cached['from_cache'] = True
                return cached
        
        logger.info(f"Iniciando descarga de TikTok: {url}")
        
        try:
            # Configuración de yt-dlp para TikTok sin marca de agua
            ydl_opts = {
                'format': 'best[ext=mp4]/best',  # Mejor calidad disponible
                'outtmpl': os.path.join(
                    self.output_dir,
                    filename or '%(title)s_%(id)s.%(ext)s'
                ),
                'quiet': False,
                'no_warnings': False,
                'extract_flat': False,
                'writesubtitles': False,
                'writeautomaticsub': False,
                'ignoreerrors': False,
                'no_check_certificate': False,
                'prefer_insecure': False,
                'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            }
            
            # Información del video
            video_info = {}
            
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                # Primero extraer información sin descargar
                info = ydl.extract_info(url, download=False)
                
                video_info = {
                    'id': info.get('id'),
                    'title': info.get('title', 'Sin título'),
                    'duration': info.get('duration', 0),
                    'uploader': info.get('uploader', 'Desconocido'),
                    'uploader_id': info.get('uploader_id', ''),
                    'view_count': info.get('view_count', 0),
                    'like_count': info.get('like_count', 0),
                    'description': info.get('description', ''),
                    'thumbnail': info.get('thumbnail', ''),
                    'url': info.get('url'),
                    'width': info.get('width', 0),
                    'height': info.get('height', 0),
                    'fps': info.get('fps', 0),
                    'format': info.get('format', ''),
                    'ext': info.get('ext', 'mp4'),
                }
                
                # Ahora descargar el video
                ydl.download([url])
                
                # Obtener el nombre del archivo descargado
                safe_title = ydl.prepare_filename(info)
                if os.path.exists(safe_title):
                    video_info['file_path'] = safe_title
                    video_info['file_size'] = os.path.getsize(safe_title)
                else:
                    # Buscar el archivo más reciente en el directorio
                    files = sorted(
                        Path(self.output_dir).glob('*'),
                        key=os.path.getmtime,
                        reverse=True
                    )
                    if files:
                        video_info['file_path'] = str(files[0])
                        video_info['file_size'] = os.path.getsize(files[0])
                    else:
                        raise Exception("No se pudo encontrar el archivo descargado")
                
                video_info['success'] = True
                video_info['message'] = 'Video descargado exitosamente'
                video_info['from_cache'] = False
                
                # Guardar en cache
                if use_cache:
                    self.save_to_cache(url, video_info)
                
                logger.info(f"Video descargado exitosamente: {video_info.get('file_path')}")
                
        except yt_dlp.utils.DownloadError as e:
            logger.error(f"Error de yt-dlp: {e}")
            video_info = {
                'success': False,
                'error': str(e),
                'message': 'Error al descargar el video. Verifica que la URL sea válida y el video esté disponible.'
            }
        except Exception as e:
            logger.error(f"Error inesperado: {e}", exc_info=True)
            video_info = {
                'success': False,
                'error': str(e),
                'message': f'Error inesperado: {e}'
            }
        
        return video_info


def main():
    """Función principal para ejecutar desde línea de comandos"""
    parser = argparse.ArgumentParser(
        description='Descarga videos de TikTok sin marca de agua'
    )
    parser.add_argument(
        'url',
        type=str,
        help='URL del video de TikTok'
    )
    parser.add_argument(
        '-o', '--output',
        type=str,
        default=None,
        help='Directorio de salida (opcional)'
    )
    parser.add_argument(
        '-f', '--filename',
        type=str,
        default=None,
        help='Nombre del archivo de salida (opcional)'
    )
    parser.add_argument(
        '-j', '--json',
        action='store_true',
        help='Mostrar resultado en formato JSON'
    )
    
    args = parser.parse_args()
    
    downloader = TikTokDownloader(output_dir=args.output)
    result = downloader.download_video(args.url, args.filename)
    
    if args.json:
        print(json.dumps(result, indent=2, ensure_ascii=False))
    else:
        if result.get('success'):
            print(f"✅ Video descargado exitosamente")
            print(f"📁 Archivo: {result.get('file_path')}")
            print(f"📊 Tamaño: {result.get('file_size', 0) / 1024 / 1024:.2f} MB")
            print(f"⏱️  Duración: {result.get('duration', 0)} segundos")
            print(f"👤 Autor: {result.get('uploader', 'Desconocido')}")
        else:
            print(f"❌ Error: {result.get('message')}")
            if result.get('error'):
                print(f"   Detalles: {result.get('error')}")
            sys.exit(1)
    
    return result


if __name__ == '__main__':
    main()

