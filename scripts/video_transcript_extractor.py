#!/usr/bin/env python3
"""
Script para extraer transcripciones de videos
Soporta múltiples proveedores: OpenAI Whisper, AssemblyAI, Google Speech-to-Text
"""

import os
import sys
import json
import argparse
import logging
import tempfile
from pathlib import Path
from typing import Dict, Any, Optional

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
    logger.error("yt-dlp no está instalado. Instálalo con: pip install yt-dlp")


class VideoTranscriptExtractor:
    """Extractor de transcripciones de videos"""
    
    def __init__(self, provider: str = "openai", api_key: Optional[str] = None):
        """
        Inicializa el extractor de transcripciones
        
        Args:
            provider: Proveedor a usar ('openai', 'assemblyai', 'google', 'whisper-local')
            api_key: API key del proveedor
        """
        self.provider = provider
        self.api_key = api_key
        
        if provider == "openai":
            self.api_key = api_key or os.getenv('OPENAI_API_KEY')
        elif provider == "assemblyai":
            self.api_key = api_key or os.getenv('ASSEMBLYAI_API_KEY')
        elif provider == "google":
            self.api_key = api_key or os.getenv('GOOGLE_CLOUD_API_KEY')
        
        logger.info(f"TranscriptExtractor inicializado con proveedor: {provider}")
    
    def download_video_audio(self, video_url: str, output_path: Optional[str] = None) -> str:
        """
        Descarga el audio de un video
        
        Args:
            video_url: URL del video
            output_path: Ruta de salida (opcional)
            
        Returns:
            Ruta del archivo de audio descargado
        """
        if not YT_DLP_AVAILABLE:
            raise ImportError("yt-dlp es requerido para descargar audio")
        
        if output_path is None:
            output_path = tempfile.mktemp(suffix='.mp3')
        
        ydl_opts = {
            'format': 'bestaudio/best',
            'outtmpl': output_path.replace('.mp3', ''),
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }],
            'quiet': False,
        }
        
        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([video_url])
                # yt-dlp añade la extensión automáticamente
                if not output_path.endswith('.mp3'):
                    output_path = output_path + '.mp3'
                if not os.path.exists(output_path):
                    # Buscar archivo generado
                    base_path = output_path.replace('.mp3', '')
                    for ext in ['.mp3', '.m4a', '.webm']:
                        if os.path.exists(base_path + ext):
                            return base_path + ext
                return output_path
        except Exception as e:
            logger.error(f"Error descargando audio: {e}")
            raise
    
    def extract_transcript_openai(self, audio_path: str, language: Optional[str] = None) -> Dict[str, Any]:
        """Extrae transcripción usando OpenAI Whisper API"""
        try:
            import openai
        except ImportError:
            raise ImportError("openai no está instalado. Instálalo con: pip install openai")
        
        if not self.api_key:
            raise ValueError("OPENAI_API_KEY no configurada")
        
        openai.api_key = self.api_key
        
        try:
            with open(audio_path, 'rb') as audio_file:
                transcript = openai.Audio.transcribe(
                    model="whisper-1",
                    file=audio_file,
                    language=language
                )
            
            return {
                'text': transcript.text,
                'language': language or 'auto',
                'provider': 'openai',
                'segments': []  # OpenAI no devuelve segmentos por defecto
            }
        except Exception as e:
            logger.error(f"Error en transcripción OpenAI: {e}")
            raise
    
    def extract_transcript_assemblyai(self, audio_path: str, language: Optional[str] = None) -> Dict[str, Any]:
        """Extrae transcripción usando AssemblyAI"""
        try:
            import requests
        except ImportError:
            raise ImportError("requests no está instalado")
        
        if not self.api_key:
            raise ValueError("ASSEMBLYAI_API_KEY no configurada")
        
        # Subir archivo
        upload_url = "https://api.assemblyai.com/v2/upload"
        headers = {"authorization": self.api_key}
        
        try:
            with open(audio_path, 'rb') as f:
                upload_response = requests.post(upload_url, headers=headers, files={'file': f})
                upload_response.raise_for_status()
                audio_url = upload_response.json()['upload_url']
            
            # Crear transcripción
            transcript_url = "https://api.assemblyai.com/v2/transcript"
            transcript_request = {
                "audio_url": audio_url,
            }
            if language:
                transcript_request["language_code"] = language
            
            transcript_response = requests.post(
                transcript_url,
                json=transcript_request,
                headers=headers
            )
            transcript_response.raise_for_status()
            transcript_id = transcript_response.json()['id']
            
            # Esperar a que termine
            import time
            while True:
                status_response = requests.get(
                    f"{transcript_url}/{transcript_id}",
                    headers=headers
                )
                status_data = status_response.json()
                
                if status_data['status'] == 'completed':
                    return {
                        'text': status_data.get('text', ''),
                        'language': status_data.get('language_code', language or 'auto'),
                        'provider': 'assemblyai',
                        'segments': status_data.get('words', [])
                    }
                elif status_data['status'] == 'error':
                    raise Exception(f"Error en transcripción: {status_data.get('error', 'Unknown')}")
                
                time.sleep(2)
                
        except Exception as e:
            logger.error(f"Error en transcripción AssemblyAI: {e}")
            raise
    
    def extract_transcript_whisper_local(self, audio_path: str, language: Optional[str] = None) -> Dict[str, Any]:
        """Extrae transcripción usando Whisper local"""
        try:
            import whisper
        except ImportError:
            raise ImportError("whisper no está instalado. Instálalo con: pip install openai-whisper")
        
        try:
            model = whisper.load_model("base")  # Puedes usar 'tiny', 'base', 'small', 'medium', 'large'
            result = model.transcribe(audio_path, language=language)
            
            return {
                'text': result['text'],
                'language': result['language'],
                'provider': 'whisper-local',
                'segments': result.get('segments', [])
            }
        except Exception as e:
            logger.error(f"Error en transcripción Whisper local: {e}")
            raise
    
    def extract_transcript(self, video_url: str, language: Optional[str] = None) -> Dict[str, Any]:
        """
        Extrae transcripción de un video
        
        Args:
            video_url: URL del video
            language: Idioma del video (opcional, se detecta automáticamente)
            
        Returns:
            Diccionario con la transcripción y metadatos
        """
        logger.info(f"Extrayendo transcripción de: {video_url}")
        
        # Descargar audio
        audio_path = None
        try:
            audio_path = self.download_video_audio(video_url)
            logger.info(f"Audio descargado: {audio_path}")
            
            # Extraer transcripción según el proveedor
            if self.provider == "openai":
                transcript = self.extract_transcript_openai(audio_path, language)
            elif self.provider == "assemblyai":
                transcript = self.extract_transcript_assemblyai(audio_path, language)
            elif self.provider == "whisper-local":
                transcript = self.extract_transcript_whisper_local(audio_path, language)
            else:
                raise ValueError(f"Proveedor no soportado: {self.provider}")
            
            transcript['video_url'] = video_url
            transcript['audio_path'] = audio_path
            
            return transcript
            
        finally:
            # Limpiar archivo temporal si existe
            if audio_path and os.path.exists(audio_path) and tempfile.gettempdir() in audio_path:
                try:
                    os.unlink(audio_path)
                except:
                    pass


def main():
    parser = argparse.ArgumentParser(description='Extrae transcripción de un video')
    parser.add_argument('video_url', help='URL del video')
    parser.add_argument('--provider', choices=['openai', 'assemblyai', 'whisper-local'], 
                       default='openai', help='Proveedor de transcripción')
    parser.add_argument('--language', help='Idioma del video (opcional)')
    parser.add_argument('--api-key', help='API key del proveedor')
    parser.add_argument('--output', '-o', help='Archivo JSON de salida')
    
    args = parser.parse_args()
    
    extractor = VideoTranscriptExtractor(provider=args.provider, api_key=args.api_key)
    
    try:
        transcript = extractor.extract_transcript(args.video_url, language=args.language)
        
        if args.output:
            with open(args.output, 'w', encoding='utf-8') as f:
                json.dump(transcript, f, indent=2, ensure_ascii=False)
            logger.info(f"Transcripción guardada en: {args.output}")
        else:
            print(json.dumps(transcript, indent=2, ensure_ascii=False))
        
        return 0
        
    except Exception as e:
        logger.error(f"Error: {e}")
        return 1


if __name__ == '__main__':
    sys.exit(main())


