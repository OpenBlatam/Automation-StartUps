#!/usr/bin/env python3
"""
Script para editar videos aplicando transiciones y efectos según un script generado por IA
Usa moviepy para aplicar transiciones, efectos y cortes
"""

import os
import sys
import json
import argparse
import tempfile
import logging
from pathlib import Path
from typing import Dict, List, Any, Optional

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

try:
    from moviepy.editor import VideoFileClip, CompositeVideoClip, concatenate_videoclips
    from moviepy.video.fx import fadein, fadeout, resize, speedx
    from moviepy.video.tools.drawing import color_gradient
except ImportError:
    logger.error("moviepy no está instalado. Instálalo con: pip install moviepy")
    sys.exit(1)

# Importar efectos avanzados si están disponibles
try:
    from video_effects_advanced import AdvancedVideoEffects, apply_ken_burns, apply_cinematic_look
    ADVANCED_EFFECTS_AVAILABLE = True
except ImportError:
    ADVANCED_EFFECTS_AVAILABLE = False
    logger.warning("Efectos avanzados no disponibles")


class VideoEditor:
    """Clase para editar videos aplicando transiciones y efectos"""
    
    def __init__(self, output_dir: Optional[str] = None):
        """
        Inicializa el editor de video
        
        Args:
            output_dir: Directorio donde guardar los videos editados
        """
        self.output_dir = output_dir or os.path.dirname(os.path.abspath(__file__))
        Path(self.output_dir).mkdir(parents=True, exist_ok=True)
    
    def apply_transition(self, clip, transition_type: str, duration: float = 1.0) -> Any:
        """
        Aplica una transición a un clip
        
        Args:
            clip: Clip de video
            transition_type: Tipo de transición (fade_in, fade_out, zoom, etc.)
            duration: Duración de la transición en segundos
            
        Returns:
            Clip con transición aplicada
        """
        if transition_type == "fade_in":
            return fadein(clip, duration)
        elif transition_type == "fade_out":
            return fadeout(clip, duration)
        elif transition_type == "zoom_in":
            # Zoom in effect
            def zoom(t):
                return 1 + 0.2 * (t / duration) if t < duration else 1.2
            return clip.resize(lambda t: zoom(t))
        elif transition_type == "zoom_out":
            # Zoom out effect
            def zoom(t):
                return 1.2 - 0.2 * (t / duration) if t < duration else 1.0
            return clip.resize(lambda t: zoom(t))
        else:
            return clip
    
    def apply_effect(self, clip, effect_type: str, start_time: float, end_time: float, **kwargs) -> Any:
        """
        Aplica un efecto a una sección del clip
        
        Args:
            clip: Clip de video
            effect_type: Tipo de efecto (zoom, brightness, etc.)
            start_time: Tiempo de inicio del efecto
            end_time: Tiempo de fin del efecto
            **kwargs: Parámetros adicionales del efecto
            
        Returns:
            Clip con efecto aplicado
        """
        if effect_type == "zoom":
            intensity = kwargs.get('intensity', 1.2)
            # Aplicar zoom en la sección específica
            def zoom_effect(t):
                if start_time <= t <= end_time:
                    progress = (t - start_time) / (end_time - start_time)
                    # Zoom in y out suave
                    zoom_factor = 1 + (intensity - 1) * (1 - abs(progress - 0.5) * 2)
                    return zoom_factor
                return 1.0
            
            return clip.resize(lambda t: zoom_effect(t))
        
        elif effect_type == "brightness":
            factor = kwargs.get('factor', 1.2)
            # Aplicar cambio de brillo
            def brighten(image):
                return image * factor
            
            return clip.fl_image(brighten)
        
        else:
            return clip
    
    def apply_speed_change(self, clip, start_time: float, end_time: float, speed: float) -> Any:
        """
        Cambia la velocidad de reproducción de una sección
        
        Args:
            clip: Clip de video
            start_time: Tiempo de inicio
            end_time: Tiempo de fin
            speed: Factor de velocidad (1.0 = normal, 0.5 = lento, 2.0 = rápido)
            
        Returns:
            Clip con cambio de velocidad
        """
        # Extraer la sección
        section = clip.subclip(start_time, end_time)
        
        # Aplicar cambio de velocidad
        section_speed = section.fx(speedx, speed)
        
        # Reemplazar la sección en el clip original
        before = clip.subclip(0, start_time) if start_time > 0 else None
        after = clip.subclip(end_time) if end_time < clip.duration else None
        
        clips_to_concat = []
        if before:
            clips_to_concat.append(before)
        clips_to_concat.append(section_speed)
        if after:
            clips_to_concat.append(after)
        
        return concatenate_videoclips(clips_to_concat)
    
    def edit_video(self, video_path: str, script_path: str, output_filename: Optional[str] = None) -> Dict[str, Any]:
        """
        Edita un video aplicando el script de edición
        
        Args:
            video_path: Ruta al archivo de video original
            script_path: Ruta al archivo JSON con el script de edición
            output_filename: Nombre del archivo de salida (opcional)
            
        Returns:
            Información del video editado
        """
        try:
            # Cargar script
            with open(script_path, 'r', encoding='utf-8') as f:
                script = json.load(f)
            
            editing_script = script.get('editing_script', {})
            
            # Cargar video
            print(f"📹 Cargando video: {video_path}")
            clip = VideoFileClip(video_path)
            
            # Aplicar transiciones iniciales
            transitions = editing_script.get('transitions', [])
            for transition in transitions:
                if transition.get('type') == 'fade_in' and transition.get('start_time', 0) == 0:
                    duration = transition.get('end_time', 1.0) - transition.get('start_time', 0)
                    clip = self.apply_transition(clip, 'fade_in', duration)
                    print(f"  ✨ Aplicando fade in ({duration}s)")
            
            # Aplicar efectos
            effects = editing_script.get('effects', [])
            for effect in effects:
                effect_type = effect.get('type')
                start_time = effect.get('start_time', 0)
                end_time = effect.get('end_time', clip.duration)
                
                if effect_type == 'zoom':
                    intensity = effect.get('intensity', 1.2)
                    clip = self.apply_effect(clip, 'zoom', start_time, end_time, intensity=intensity)
                    logger.info(f"Aplicando zoom ({start_time}s - {end_time}s)")
                
                elif effect_type == 'ken_burns' and ADVANCED_EFFECTS_AVAILABLE:
                    # Efecto Ken Burns (zoom + pan)
                    zoom = effect.get('zoom', 1.3)
                    pan_direction = effect.get('pan_direction', 'center')
                    section = clip.subclip(start_time, end_time)
                    section = apply_ken_burns(section, zoom=zoom, pan_direction=pan_direction)
                    # Reemplazar sección
                    before = clip.subclip(0, start_time) if start_time > 0 else None
                    after = clip.subclip(end_time) if end_time < clip.duration else None
                    clips_to_concat = []
                    if before:
                        clips_to_concat.append(before)
                    clips_to_concat.append(section)
                    if after:
                        clips_to_concat.append(after)
                    clip = concatenate_videoclips(clips_to_concat)
                    logger.info(f"Aplicando Ken Burns ({start_time}s - {end_time}s)")
                
                elif effect_type == 'cinematic' and ADVANCED_EFFECTS_AVAILABLE:
                    # Look cinematográfico
                    section = clip.subclip(start_time, end_time)
                    section = apply_cinematic_look(section)
                    # Reemplazar sección
                    before = clip.subclip(0, start_time) if start_time > 0 else None
                    after = clip.subclip(end_time) if end_time < clip.duration else None
                    clips_to_concat = []
                    if before:
                        clips_to_concat.append(before)
                    clips_to_concat.append(section)
                    if after:
                        clips_to_concat.append(after)
                    clip = concatenate_videoclips(clips_to_concat)
                    logger.info(f"Aplicando look cinematográfico ({start_time}s - {end_time}s)")
            
            # Aplicar cambios de velocidad
            speed_changes = editing_script.get('speed_changes', [])
            for speed_change in speed_changes:
                start_time = speed_change.get('start_time', 0)
                end_time = speed_change.get('end_time', clip.duration)
                speed = speed_change.get('speed', 1.0)
                
                if speed != 1.0:
                    clip = self.apply_speed_change(clip, start_time, end_time, speed)
                    print(f"  ⚡ Cambiando velocidad a {speed}x ({start_time}s - {end_time}s)")
            
            # Aplicar transiciones finales
            for transition in transitions:
                if transition.get('type') == 'fade_out':
                    start_time = transition.get('start_time', clip.duration - 1.0)
                    end_time = transition.get('end_time', clip.duration)
                    duration = end_time - start_time
                    
                    # Aplicar fade out solo en la parte final
                    before = clip.subclip(0, start_time) if start_time > 0 else None
                    fade_section = clip.subclip(start_time, end_time)
                    fade_section = self.apply_transition(fade_section, 'fade_out', duration)
                    
                    if before:
                        clip = concatenate_videoclips([before, fade_section])
                    else:
                        clip = fade_section
                    
                    print(f"  ✨ Aplicando fade out ({duration}s)")
            
            # Generar nombre de archivo de salida
            if not output_filename:
                video_name = Path(video_path).stem
                output_filename = f"{video_name}_edited.mp4"
            
            output_path = os.path.join(self.output_dir, output_filename)
            
            # Calcular tamaño estimado y ajustar calidad si es necesario
            max_size_mb = 50  # Límite de Telegram
            estimated_size_mb = (clip.duration * clip.w * clip.h * 0.1) / (1024 * 1024)  # Estimación aproximada
            
            # Ajustar bitrate si el video es muy grande
            bitrate = '5000k'
            if estimated_size_mb > max_size_mb:
                # Reducir bitrate para comprimir
                bitrate = f"{int(5000 * (max_size_mb / estimated_size_mb))}k"
                logger.info(f"Video grande detectado ({estimated_size_mb:.1f}MB estimado). Comprimiendo con bitrate {bitrate}")
            
            # Exportar video editado
            logger.info(f"Exportando video editado: {output_path}")
            clip.write_videofile(
                output_path,
                codec='libx264',
                audio_codec='aac',
                bitrate=bitrate,
                temp_audiofile='temp-audio.m4a',
                remove_temp=True,
                fps=clip.fps,
                preset='medium',  # Balance entre velocidad y calidad
                threads=4  # Usar múltiples threads para acelerar
            )
            
            # Verificar tamaño final y comprimir más si es necesario
            final_size_mb = os.path.getsize(output_path) / (1024 * 1024)
            if final_size_mb > max_size_mb:
                logger.warning(f"Video aún muy grande ({final_size_mb:.1f}MB). Aplicando compresión adicional...")
                # Re-comprimir con menor calidad
                compressed_path = output_path.replace('.mp4', '_compressed.mp4')
                clip_compressed = VideoFileClip(output_path)
                clip_compressed.write_videofile(
                    compressed_path,
                    codec='libx264',
                    audio_codec='aac',
                    bitrate='2000k',  # Bitrate más bajo
                    preset='fast',
                    threads=4
                )
                clip_compressed.close()
                
                # Reemplazar archivo original
                os.replace(compressed_path, output_path)
                final_size_mb = os.path.getsize(output_path) / (1024 * 1024)
                logger.info(f"Video comprimido a {final_size_mb:.1f}MB")
            
            # Limpiar
            clip.close()
            
            result = {
                'success': True,
                'output_path': output_path,
                'file_size': os.path.getsize(output_path),
                'duration': clip.duration,
                'message': 'Video editado exitosamente'
            }
            
            return result
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'message': f'Error al editar el video: {e}'
            }
    
    def edit_video_from_dict(self, video_path: str, script_dict: Dict[str, Any], output_filename: Optional[str] = None) -> Dict[str, Any]:
        """
        Edita un video usando un diccionario de script directamente
        
        Args:
            video_path: Ruta al archivo de video original
            script_dict: Diccionario con el script de edición
            output_filename: Nombre del archivo de salida (opcional)
            
        Returns:
            Información del video editado
        """
        # Guardar script temporalmente
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(script_dict, f, indent=2, ensure_ascii=False)
            temp_script_path = f.name
        
        try:
            result = self.edit_video(video_path, temp_script_path, output_filename)
        finally:
            # Limpiar archivo temporal
            if os.path.exists(temp_script_path):
                os.unlink(temp_script_path)
        
        return result


def main():
    """Función principal para ejecutar desde línea de comandos"""
    parser = argparse.ArgumentParser(
        description='Edita videos aplicando transiciones y efectos'
    )
    parser.add_argument(
        'video_path',
        type=str,
        help='Ruta al archivo de video'
    )
    parser.add_argument(
        'script_path',
        type=str,
        help='Ruta al archivo JSON con el script de edición'
    )
    parser.add_argument(
        '-o', '--output',
        type=str,
        default=None,
        help='Nombre del archivo de salida (opcional)'
    )
    parser.add_argument(
        '-d', '--output-dir',
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
    
    if not os.path.exists(args.video_path):
        print(f"Error: El archivo {args.video_path} no existe")
        sys.exit(1)
    
    if not os.path.exists(args.script_path):
        print(f"Error: El archivo {args.script_path} no existe")
        sys.exit(1)
    
    editor = VideoEditor(output_dir=args.output_dir)
    result = editor.edit_video(args.video_path, args.script_path, args.output)
    
    if args.json:
        print(json.dumps(result, indent=2, ensure_ascii=False))
    else:
        if result.get('success'):
            print(f"✅ Video editado exitosamente")
            print(f"📁 Archivo: {result.get('output_path')}")
            print(f"📊 Tamaño: {result.get('file_size', 0) / 1024 / 1024:.2f} MB")
            print(f"⏱️  Duración: {result.get('duration', 0):.2f} segundos")
        else:
            print(f"❌ Error: {result.get('message')}")
            if result.get('error'):
                print(f"   Detalles: {result.get('error')}")
            sys.exit(1)
    
    return result


if __name__ == '__main__':
    main()

