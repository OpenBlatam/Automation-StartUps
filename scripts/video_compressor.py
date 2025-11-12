#!/usr/bin/env python3
"""
Script auxiliar para comprimir videos grandes antes de enviarlos
Útil cuando el video editado excede los límites de Telegram (50MB)
"""

import os
import sys
import argparse
import logging
from pathlib import Path

try:
    from moviepy.editor import VideoFileClip
except ImportError:
    print("Error: moviepy no está instalado. Instálalo con: pip install moviepy")
    sys.exit(1)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def compress_video(input_path: str, output_path: str, target_size_mb: float = 50, max_quality: str = 'medium') -> dict:
    """
    Comprime un video para que no exceda un tamaño máximo
    
    Args:
        input_path: Ruta al video original
        output_path: Ruta donde guardar el video comprimido
        target_size_mb: Tamaño objetivo en MB (default: 50MB para Telegram)
        max_quality: Calidad máxima ('high', 'medium', 'low')
        
    Returns:
        Diccionario con información del video comprimido
    """
    if not os.path.exists(input_path):
        return {
            'success': False,
            'error': f'Archivo no encontrado: {input_path}'
        }
    
    try:
        # Cargar video
        logger.info(f"Cargando video: {input_path}")
        clip = VideoFileClip(input_path)
        
        # Calcular tamaño actual
        current_size_mb = os.path.getsize(input_path) / (1024 * 1024)
        logger.info(f"Tamaño actual: {current_size_mb:.2f}MB")
        
        if current_size_mb <= target_size_mb:
            logger.info("Video ya está dentro del límite. No se necesita compresión.")
            return {
                'success': True,
                'compressed': False,
                'original_size_mb': current_size_mb,
                'final_size_mb': current_size_mb,
                'output_path': input_path
            }
        
        # Calcular bitrate necesario
        duration = clip.duration
        target_size_bits = target_size_mb * 8 * 1024 * 1024  # Convertir a bits
        target_bitrate = int((target_size_bits / duration) / 1000)  # kbps
        
        # Ajustar según calidad máxima
        quality_limits = {
            'high': 8000,
            'medium': 5000,
            'low': 2000
        }
        max_bitrate = quality_limits.get(max_quality, 5000)
        target_bitrate = min(target_bitrate, max_bitrate)
        
        logger.info(f"Comprimiendo a bitrate: {target_bitrate}k")
        
        # Comprimir
        clip.write_videofile(
            output_path,
            codec='libx264',
            audio_codec='aac',
            bitrate=f'{target_bitrate}k',
            preset='medium',
            threads=4
        )
        
        clip.close()
        
        # Verificar tamaño final
        final_size_mb = os.path.getsize(output_path) / (1024 * 1024)
        compression_ratio = (1 - final_size_mb / current_size_mb) * 100
        
        logger.info(f"Compresión completada: {current_size_mb:.2f}MB → {final_size_mb:.2f}MB ({compression_ratio:.1f}% reducción)")
        
        return {
            'success': True,
            'compressed': True,
            'original_size_mb': current_size_mb,
            'final_size_mb': final_size_mb,
            'compression_ratio': compression_ratio,
            'output_path': output_path,
            'bitrate_used': f'{target_bitrate}k'
        }
        
    except Exception as e:
        logger.error(f"Error comprimiendo video: {e}", exc_info=True)
        return {
            'success': False,
            'error': str(e)
        }


def main():
    parser = argparse.ArgumentParser(description='Comprime videos para cumplir límites de tamaño')
    parser.add_argument('input', help='Archivo de video a comprimir')
    parser.add_argument('-o', '--output', help='Archivo de salida (default: input_compressed.mp4)')
    parser.add_argument('-s', '--target-size', type=float, default=50, help='Tamaño objetivo en MB (default: 50)')
    parser.add_argument('-q', '--quality', choices=['high', 'medium', 'low'], default='medium', help='Calidad máxima')
    parser.add_argument('-j', '--json', action='store_true', help='Mostrar resultado en JSON')
    
    args = parser.parse_args()
    
    if not args.output:
        input_path = Path(args.input)
        args.output = str(input_path.parent / f"{input_path.stem}_compressed{input_path.suffix}")
    
    result = compress_video(args.input, args.output, args.target_size, args.quality)
    
    if args.json:
        import json
        print(json.dumps(result, indent=2, ensure_ascii=False))
    else:
        if result.get('success'):
            if result.get('compressed'):
                print(f"✅ Video comprimido exitosamente")
                print(f"📊 {result['original_size_mb']:.2f}MB → {result['final_size_mb']:.2f}MB")
                print(f"📁 Archivo: {result['output_path']}")
            else:
                print(f"ℹ️  Video ya está dentro del límite ({result['final_size_mb']:.2f}MB)")
        else:
            print(f"❌ Error: {result.get('error')}")
            sys.exit(1)
    
    return result


if __name__ == '__main__':
    main()



