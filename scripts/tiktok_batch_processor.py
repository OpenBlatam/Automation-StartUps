#!/usr/bin/env python3
"""
Procesador en batch para múltiples videos de TikTok
Permite procesar varios links a la vez de forma eficiente
"""

import os
import sys
import json
import argparse
import logging
import tempfile
from pathlib import Path
from typing import List, Dict, Any, Optional
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed

from tiktok_downloader import TikTokDownloader
from video_script_generator import VideoScriptGenerator
from video_editor import VideoEditor

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class TikTokBatchProcessor:
    """Procesa múltiples videos de TikTok en batch"""
    
    def __init__(self, max_workers: int = 3, output_dir: Optional[str] = None):
        """
        Inicializa el procesador en batch
        
        Args:
            max_workers: Número máximo de videos a procesar en paralelo
            output_dir: Directorio de salida para videos procesados
        """
        self.max_workers = max_workers
        self.output_dir = output_dir or os.path.join(tempfile.gettempdir(), "tiktok_batch_output")
        Path(self.output_dir).mkdir(parents=True, exist_ok=True)
        
        self.downloader = TikTokDownloader(output_dir=os.path.join(self.output_dir, "downloads"))
        self.script_generator = VideoScriptGenerator()
        self.editor = VideoEditor(output_dir=os.path.join(self.output_dir, "edited"))
        
        self.results = []
        self.errors = []
    
    def process_single_video(self, url: str, index: int, total: int) -> Dict[str, Any]:
        """
        Procesa un solo video de TikTok
        
        Args:
            url: URL del video de TikTok
            index: Índice del video en el batch
            total: Total de videos en el batch
            
        Returns:
            Resultado del procesamiento
        """
        logger.info(f"[{index+1}/{total}] Procesando: {url}")
        result = {
            'url': url,
            'index': index,
            'status': 'processing',
            'started_at': datetime.now().isoformat(),
            'success': False
        }
        
        try:
            # 1. Descargar
            logger.info(f"[{index+1}/{total}] Descargando video...")
            download_result = self.downloader.download_video(url)
            
            if not download_result.get('success'):
                raise Exception(f"Error al descargar: {download_result.get('message')}")
            
            result['download'] = download_result
            video_path = download_result['file_path']
            
            # 2. Generar script
            logger.info(f"[{index+1}/{total}] Generando script de edición...")
            script = self.script_generator.generate_script(video_path, num_frames=10)
            result['script'] = script
            
            # Guardar script temporalmente
            script_path = os.path.join(self.output_dir, f"script_{index}.json")
            with open(script_path, 'w', encoding='utf-8') as f:
                json.dump(script, f, indent=2, ensure_ascii=False)
            
            # 3. Editar video
            logger.info(f"[{index+1}/{total}] Editando video...")
            edit_result = self.editor.edit_video(
                video_path,
                script_path,
                output_filename=f"video_{index}_edited.mp4"
            )
            
            if not edit_result.get('success'):
                raise Exception(f"Error al editar: {edit_result.get('message')}")
            
            result['edit'] = edit_result
            result['success'] = True
            result['status'] = 'completed'
            result['completed_at'] = datetime.now().isoformat()
            
            # Calcular tiempo total
            start = datetime.fromisoformat(result['started_at'])
            end = datetime.fromisoformat(result['completed_at'])
            result['processing_time'] = (end - start).total_seconds()
            
            logger.info(f"[{index+1}/{total}] ✅ Completado en {result['processing_time']:.1f}s")
            
        except Exception as e:
            logger.error(f"[{index+1}/{total}] ❌ Error: {e}", exc_info=True)
            result['status'] = 'error'
            result['error'] = str(e)
            result['completed_at'] = datetime.now().isoformat()
            self.errors.append(result)
        
        return result
    
    def process_batch(self, urls: List[str]) -> Dict[str, Any]:
        """
        Procesa múltiples videos en batch
        
        Args:
            urls: Lista de URLs de TikTok
            
        Returns:
            Resumen del procesamiento
        """
        logger.info(f"Iniciando procesamiento en batch de {len(urls)} videos")
        logger.info(f"Workers paralelos: {self.max_workers}")
        
        start_time = datetime.now()
        
        # Procesar en paralelo con ThreadPoolExecutor
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            futures = {
                executor.submit(self.process_single_video, url, i, len(urls)): (url, i)
                for i, url in enumerate(urls)
            }
            
            for future in as_completed(futures):
                try:
                    result = future.result()
                    self.results.append(result)
                except Exception as e:
                    url, index = futures[future]
                    logger.error(f"Error procesando {url}: {e}")
                    self.errors.append({
                        'url': url,
                        'index': index,
                        'error': str(e)
                    })
        
        end_time = datetime.now()
        total_time = (end_time - start_time).total_seconds()
        
        # Generar resumen
        successful = [r for r in self.results if r.get('success')]
        failed = [r for r in self.results if not r.get('success')]
        
        summary = {
            'total': len(urls),
            'successful': len(successful),
            'failed': len(failed),
            'total_time_seconds': total_time,
            'average_time_per_video': total_time / len(urls) if urls else 0,
            'results': self.results,
            'errors': self.errors,
            'started_at': start_time.isoformat(),
            'completed_at': end_time.isoformat()
        }
        
        logger.info(f"\n{'='*60}")
        logger.info(f"Resumen del procesamiento:")
        logger.info(f"  Total: {summary['total']}")
        logger.info(f"  Exitosos: {summary['successful']}")
        logger.info(f"  Fallidos: {summary['failed']}")
        logger.info(f"  Tiempo total: {total_time:.1f}s")
        logger.info(f"  Tiempo promedio: {summary['average_time_per_video']:.1f}s por video")
        logger.info(f"{'='*60}")
        
        return summary


def main():
    parser = argparse.ArgumentParser(
        description='Procesa múltiples videos de TikTok en batch'
    )
    parser.add_argument(
        'urls_file',
        type=str,
        help='Archivo JSON o texto con URLs (una por línea)'
    )
    parser.add_argument(
        '-w', '--workers',
        type=int,
        default=3,
        help='Número de workers paralelos (default: 3)'
    )
    parser.add_argument(
        '-o', '--output',
        type=str,
        default=None,
        help='Directorio de salida (opcional)'
    )
    parser.add_argument(
        '-j', '--json',
        action='store_true',
        help='Mostrar resultado en formato JSON'
    )
    
    args = parser.parse_args()
    
    # Leer URLs
    urls = []
    if args.urls_file.endswith('.json'):
        with open(args.urls_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
            if isinstance(data, list):
                urls = data
            elif isinstance(data, dict) and 'urls' in data:
                urls = data['urls']
    else:
        with open(args.urls_file, 'r', encoding='utf-8') as f:
            urls = [line.strip() for line in f if line.strip() and not line.startswith('#')]
    
    if not urls:
        logger.error("No se encontraron URLs para procesar")
        sys.exit(1)
    
    # Procesar
    processor = TikTokBatchProcessor(max_workers=args.workers, output_dir=args.output)
    summary = processor.process_batch(urls)
    
    # Guardar resumen
    summary_file = os.path.join(processor.output_dir, 'batch_summary.json')
    with open(summary_file, 'w', encoding='utf-8') as f:
        json.dump(summary, f, indent=2, ensure_ascii=False)
    
    if args.json:
        print(json.dumps(summary, indent=2, ensure_ascii=False))
    else:
        print(f"\n✅ Procesamiento completado")
        print(f"📁 Resumen guardado en: {summary_file}")
    
    # Exit code basado en resultados
    sys.exit(0 if summary['failed'] == 0 else 1)


if __name__ == '__main__':
    main()


