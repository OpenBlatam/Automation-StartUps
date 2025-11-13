#!/usr/bin/env python3
"""
Pipeline completo para descubrir videos de IA, extraer transcripciones y generar PDFs
Orquesta todo el proceso de principio a fin
"""

import os
import sys
import json
import argparse
import logging
from pathlib import Path
from typing import List, Dict, Any, Optional
from datetime import datetime

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Importar módulos locales
try:
    from ai_video_discoverer import AIVideoDiscoverer
    from video_transcript_extractor import VideoTranscriptExtractor
    from pdf_replication_guide_generator import PDFReplicationGuideGenerator
except ImportError as e:
    logger.error(f"Error importando módulos: {e}")
    logger.error("Asegúrate de que los scripts estén en el mismo directorio")
    sys.exit(1)


class AIVideoPipeline:
    """Pipeline completo para procesar videos de IA"""
    
    def __init__(
        self,
        youtube_api_key: Optional[str] = None,
        openai_api_key: Optional[str] = None,
        transcript_provider: str = "openai",
        output_dir: str = "./ai_video_outputs"
    ):
        """
        Inicializa el pipeline
        
        Args:
            youtube_api_key: API key de YouTube
            openai_api_key: API key de OpenAI
            transcript_provider: Proveedor de transcripción ('openai', 'assemblyai', 'whisper-local')
            output_dir: Directorio de salida
        """
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # Inicializar componentes
        self.discoverer = AIVideoDiscoverer(youtube_api_key=youtube_api_key)
        self.transcript_extractor = VideoTranscriptExtractor(
            provider=transcript_provider,
            api_key=openai_api_key
        )
        self.pdf_generator = PDFReplicationGuideGenerator(openai_api_key=openai_api_key)
        
        logger.info(f"Pipeline inicializado. Output dir: {self.output_dir}")
    
    def run(
        self,
        max_videos: int = 10,
        days_back: int = 7,
        languages: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Ejecuta el pipeline completo
        
        Args:
            max_videos: Número máximo de videos a procesar
            days_back: Días hacia atrás para buscar videos
            languages: Idiomas a buscar (None = todos excepto español)
            
        Returns:
            Diccionario con resultados del procesamiento
        """
        results = {
            'started_at': datetime.now().isoformat(),
            'videos_discovered': 0,
            'videos_processed': 0,
            'pdfs_generated': 0,
            'errors': [],
            'outputs': []
        }
        
        try:
            # Paso 1: Descubrir videos
            logger.info("=" * 60)
            logger.info("PASO 1: Descubriendo videos populares de IA...")
            logger.info("=" * 60)
            
            videos = self.discoverer.discover_popular_ai_videos(
                max_results=max_videos,
                days_back=days_back,
                languages=languages
            )
            
            results['videos_discovered'] = len(videos)
            logger.info(f"Encontrados {len(videos)} videos")
            
            # Guardar lista de videos descubiertos
            videos_file = self.output_dir / "discovered_videos.json"
            with open(videos_file, 'w', encoding='utf-8') as f:
                json.dump({
                    'discovered_at': datetime.now().isoformat(),
                    'videos': videos
                }, f, indent=2, ensure_ascii=False)
            logger.info(f"Lista de videos guardada en: {videos_file}")
            
            # Paso 2: Procesar cada video
            logger.info("=" * 60)
            logger.info("PASO 2: Procesando videos...")
            logger.info("=" * 60)
            
            for i, video in enumerate(videos, 1):
                logger.info(f"\n[{i}/{len(videos)}] Procesando: {video.get('title', 'Sin título')}")
                logger.info(f"URL: {video.get('url', 'N/A')}")
                
                try:
                    # Extraer transcripción
                    logger.info("Extrayendo transcripción...")
                    transcript = self.transcript_extractor.extract_transcript(
                        video_url=video['url'],
                        language=video.get('language')
                    )
                    
                    # Guardar transcripción
                    transcript_file = self.output_dir / f"transcript_{video.get('id', i)}.json"
                    with open(transcript_file, 'w', encoding='utf-8') as f:
                        json.dump(transcript, f, indent=2, ensure_ascii=False)
                    logger.info(f"Transcripción guardada en: {transcript_file}")
                    
                    # Guardar información del video
                    video_info_file = self.output_dir / f"video_info_{video.get('id', i)}.json"
                    with open(video_info_file, 'w', encoding='utf-8') as f:
                        json.dump(video, f, indent=2, ensure_ascii=False)
                    
                    # Generar PDF
                    logger.info("Generando PDF de replicación...")
                    pdf_file = self.output_dir / f"replication_guide_{video.get('id', i)}.pdf"
                    
                    pdf_path = self.pdf_generator.generate_replication_guide(
                        transcript=transcript.get('text', ''),
                        video_info=video,
                        output_path=str(pdf_file),
                        translate=True
                    )
                    
                    logger.info(f"PDF generado: {pdf_path}")
                    
                    results['videos_processed'] += 1
                    results['pdfs_generated'] += 1
                    results['outputs'].append({
                        'video_id': video.get('id', ''),
                        'title': video.get('title', ''),
                        'transcript_file': str(transcript_file),
                        'video_info_file': str(video_info_file),
                        'pdf_file': str(pdf_path)
                    })
                    
                except Exception as e:
                    error_msg = f"Error procesando video {video.get('url', 'N/A')}: {str(e)}"
                    logger.error(error_msg)
                    results['errors'].append({
                        'video_url': video.get('url', 'N/A'),
                        'error': str(e)
                    })
                    continue
            
            results['completed_at'] = datetime.now().isoformat()
            
            # Guardar resumen
            summary_file = self.output_dir / "pipeline_summary.json"
            with open(summary_file, 'w', encoding='utf-8') as f:
                json.dump(results, f, indent=2, ensure_ascii=False)
            
            logger.info("=" * 60)
            logger.info("RESUMEN DEL PROCESAMIENTO")
            logger.info("=" * 60)
            logger.info(f"Videos descubiertos: {results['videos_discovered']}")
            logger.info(f"Videos procesados: {results['videos_processed']}")
            logger.info(f"PDFs generados: {results['pdfs_generated']}")
            logger.info(f"Errores: {len(results['errors'])}")
            logger.info(f"Resumen guardado en: {summary_file}")
            
            return results
            
        except Exception as e:
            logger.error(f"Error en el pipeline: {e}")
            results['errors'].append({'pipeline_error': str(e)})
            return results


def main():
    parser = argparse.ArgumentParser(
        description='Pipeline completo para descubrir videos de IA y generar PDFs de replicación'
    )
    parser.add_argument('--max-videos', type=int, default=10, help='Número máximo de videos a procesar')
    parser.add_argument('--days-back', type=int, default=7, help='Días hacia atrás para buscar')
    parser.add_argument('--languages', nargs='+', help='Idiomas a buscar (ej: en pt fr)')
    parser.add_argument('--output-dir', '-o', default='./ai_video_outputs', help='Directorio de salida')
    parser.add_argument('--youtube-api-key', help='API key de YouTube (o usar YOUTUBE_API_KEY env var)')
    parser.add_argument('--openai-api-key', help='API key de OpenAI (o usar OPENAI_API_KEY env var)')
    parser.add_argument('--transcript-provider', choices=['openai', 'assemblyai', 'whisper-local'],
                       default='openai', help='Proveedor de transcripción')
    
    args = parser.parse_args()
    
    # Obtener API keys de variables de entorno si no se proporcionan
    youtube_api_key = args.youtube_api_key or os.getenv('YOUTUBE_API_KEY')
    openai_api_key = args.openai_api_key or os.getenv('OPENAI_API_KEY')
    
    # Crear pipeline
    pipeline = AIVideoPipeline(
        youtube_api_key=youtube_api_key,
        openai_api_key=openai_api_key,
        transcript_provider=args.transcript_provider,
        output_dir=args.output_dir
    )
    
    # Ejecutar pipeline
    results = pipeline.run(
        max_videos=args.max_videos,
        days_back=args.days_back,
        languages=args.languages
    )
    
    # Retornar código de salida según resultados
    if results['errors']:
        return 1
    return 0


if __name__ == '__main__':
    sys.exit(main())


