#!/usr/bin/env python3
"""
Script para analizar videos y generar scripts de edición usando IA
Analiza frames del video y genera un script de edición con transiciones
"""

import os
import sys
import json
import argparse
import base64
from pathlib import Path
from typing import Dict, List, Any, Optional
import tempfile

try:
    import cv2
    import numpy as np
except ImportError:
    print("Error: opencv-python no está instalado. Instálalo con: pip install opencv-python")
    sys.exit(1)

try:
    from openai import OpenAI
except ImportError:
    print("Error: openai no está instalado. Instálalo con: pip install openai")
    sys.exit(1)


class VideoScriptGenerator:
    """Clase para generar scripts de edición basados en análisis de video con IA"""
    
    def __init__(self, openai_api_key: Optional[str] = None):
        """
        Inicializa el generador de scripts
        
        Args:
            openai_api_key: Clave API de OpenAI. Si es None, intenta obtenerla de OPENAI_API_KEY
        """
        self.api_key = openai_api_key or os.getenv('OPENAI_API_KEY')
        if not self.api_key:
            raise ValueError("OPENAI_API_KEY no está configurada")
        
        self.client = OpenAI(api_key=self.api_key)
    
    def extract_frames(self, video_path: str, num_frames: int = 10) -> List[Dict[str, Any]]:
        """
        Extrae frames representativos del video
        
        Args:
            video_path: Ruta al archivo de video
            num_frames: Número de frames a extraer
            
        Returns:
            Lista de diccionarios con información de cada frame
        """
        frames = []
        cap = cv2.VideoCapture(video_path)
        
        if not cap.isOpened():
            raise ValueError(f"No se pudo abrir el video: {video_path}")
        
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        fps = cap.get(cv2.CAP_PROP_FPS)
        duration = total_frames / fps if fps > 0 else 0
        
        # Extraer frames distribuidos uniformemente
        frame_indices = np.linspace(0, total_frames - 1, num_frames, dtype=int)
        
        for idx, frame_num in enumerate(frame_indices):
            cap.set(cv2.CAP_PROP_POS_FRAMES, frame_num)
            ret, frame = cap.read()
            
            if ret:
                # Convertir a RGB para OpenAI Vision
                frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                
                # Guardar frame temporalmente como base64
                _, buffer = cv2.imencode('.jpg', frame)
                frame_base64 = base64.b64encode(buffer).decode('utf-8')
                
                timestamp = frame_num / fps if fps > 0 else 0
                
                frames.append({
                    'frame_number': int(frame_num),
                    'timestamp': timestamp,
                    'image_base64': frame_base64,
                    'width': frame.shape[1],
                    'height': frame.shape[0]
                })
        
        cap.release()
        
        return {
            'frames': frames,
            'total_frames': total_frames,
            'fps': fps,
            'duration': duration,
            'width': int(cap.get(cv2.CAP_PROP_FRAME_WIDTH)),
            'height': int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        }
    
    def analyze_video_with_ai(self, frames_data: Dict[str, Any], video_info: Optional[Dict] = None) -> Dict[str, Any]:
        """
        Analiza el video usando OpenAI Vision API y genera un script de edición
        
        Args:
            frames_data: Datos de los frames extraídos
            video_info: Información adicional del video (opcional)
            
        Returns:
            Script de edición generado por IA
        """
        # Preparar imágenes para OpenAI Vision
        image_contents = []
        for frame in frames_data['frames'][:6]:  # OpenAI permite hasta 6 imágenes
            image_contents.append({
                "type": "image_url",
                "image_url": {
                    "url": f"data:image/jpeg;base64,{frame['image_base64']}"
                }
            })
        
        # Construir prompt para análisis
        prompt = f"""Analiza este video de TikTok y genera un script de edición profesional con transiciones.

Información del video:
- Duración: {frames_data.get('duration', 0):.2f} segundos
- Resolución: {frames_data.get('width')}x{frames_data.get('height')}
- FPS: {frames_data.get('fps', 0):.2f}
- Total de frames analizados: {len(frames_data['frames'])}

Instrucciones:
1. Analiza el contenido visual de cada frame
2. Identifica cambios de escena, movimientos, y momentos clave
3. Genera un script de edición con:
   - Puntos de corte sugeridos (timestamps)
   - Tipos de transiciones recomendadas (fade, zoom, slide, etc.)
   - Efectos visuales apropiados
   - Velocidad de reproducción (normal, slow motion, fast forward)
   - Música y ritmo sugerido

Formato de respuesta JSON:
{{
  "analysis": {{
    "content_type": "tipo de contenido (dance, comedy, tutorial, etc.)",
    "mood": "estado de ánimo del video",
    "key_moments": ["momento1", "momento2", ...],
    "scene_changes": [{{"timestamp": 0.0, "type": "cut_type"}}, ...]
  }},
  "editing_script": {{
    "transitions": [
      {{
        "start_time": 0.0,
        "end_time": 2.0,
        "type": "fade_in",
        "description": "Fade in desde negro"
      }},
      ...
    ],
    "cuts": [
      {{
        "timestamp": 5.0,
        "type": "hard_cut",
        "reason": "cambio de escena"
      }},
      ...
    ],
    "effects": [
      {{
        "start_time": 10.0,
        "end_time": 12.0,
        "type": "zoom",
        "intensity": 1.2,
        "description": "Zoom in en el momento clave"
      }},
      ...
    ],
    "speed_changes": [
      {{
        "start_time": 15.0,
        "end_time": 18.0,
        "speed": 0.5,
        "description": "Slow motion para efecto dramático"
      }},
      ...
    ],
    "recommended_music": {{
      "tempo": "fast/medium/slow",
      "genre": "sugerencia de género",
      "mood": "energético/relajado/etc"
    }}
  }},
  "summary": "Resumen del análisis y recomendaciones"
}}"""
        
        try:
            response = self.client.chat.completions.create(
                model="gpt-4o",  # o "gpt-4-vision-preview" si está disponible
                messages=[
                    {
                        "role": "system",
                        "content": "Eres un editor de video profesional especializado en contenido de TikTok. Analizas videos y generas scripts de edición detallados con transiciones, efectos y cortes."
                    },
                    {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": prompt}
                        ] + image_contents
                    }
                ],
                max_tokens=2000,
                temperature=0.7
            )
            
            # Parsear respuesta JSON
            content = response.choices[0].message.content
            
            # Intentar extraer JSON de la respuesta
            try:
                # Buscar JSON en la respuesta
                json_start = content.find('{')
                json_end = content.rfind('}') + 1
                if json_start >= 0 and json_end > json_start:
                    json_str = content[json_start:json_end]
                    script = json.loads(json_str)
                else:
                    # Si no hay JSON, crear estructura básica
                    script = {
                        "analysis": {"content_type": "unknown", "mood": "neutral"},
                        "editing_script": {
                            "transitions": [],
                            "cuts": [],
                            "effects": [],
                            "speed_changes": []
                        },
                        "summary": content
                    }
            except json.JSONDecodeError:
                # Si falla el parseo, crear estructura básica con el texto
                script = {
                    "analysis": {"content_type": "unknown", "mood": "neutral"},
                    "editing_script": {
                        "transitions": [
                            {
                                "start_time": 0.0,
                                "end_time": 1.0,
                                "type": "fade_in",
                                "description": "Fade in inicial"
                            },
                            {
                                "start_time": frames_data.get('duration', 10) - 1.0,
                                "end_time": frames_data.get('duration', 10),
                                "type": "fade_out",
                                "description": "Fade out final"
                            }
                        ],
                        "cuts": [],
                        "effects": [],
                        "speed_changes": []
                    },
                    "summary": content
                }
            
            return script
            
        except Exception as e:
            print(f"Error en análisis con IA: {e}")
            # Retornar script básico por defecto
            return self._default_script(frames_data)
    
    def _default_script(self, frames_data: Dict[str, Any]) -> Dict[str, Any]:
        """Genera un script básico por defecto si falla el análisis con IA"""
        duration = frames_data.get('duration', 10)
        
        return {
            "analysis": {
                "content_type": "general",
                "mood": "neutral",
                "key_moments": [],
                "scene_changes": []
            },
            "editing_script": {
                "transitions": [
                    {
                        "start_time": 0.0,
                        "end_time": 1.0,
                        "type": "fade_in",
                        "description": "Fade in inicial"
                    },
                    {
                        "start_time": duration - 1.0,
                        "end_time": duration,
                        "type": "fade_out",
                        "description": "Fade out final"
                    }
                ],
                "cuts": [],
                "effects": [],
                "speed_changes": []
            },
            "summary": "Script básico generado automáticamente"
        }
    
    def generate_script(self, video_path: str, num_frames: int = 10) -> Dict[str, Any]:
        """
        Proceso completo: extrae frames y genera script
        
        Args:
            video_path: Ruta al archivo de video
            num_frames: Número de frames a analizar
            
        Returns:
            Script completo de edición
        """
        print(f"📹 Extrayendo frames del video...")
        frames_data = self.extract_frames(video_path, num_frames)
        
        print(f"🤖 Analizando video con IA...")
        script = self.analyze_video_with_ai(frames_data)
        
        # Agregar metadata del video
        script['video_metadata'] = {
            'duration': frames_data.get('duration'),
            'fps': frames_data.get('fps'),
            'resolution': f"{frames_data.get('width')}x{frames_data.get('height')}",
            'total_frames': frames_data.get('total_frames')
        }
        
        return script


def main():
    """Función principal para ejecutar desde línea de comandos"""
    parser = argparse.ArgumentParser(
        description='Genera script de edición para video usando IA'
    )
    parser.add_argument(
        'video_path',
        type=str,
        help='Ruta al archivo de video'
    )
    parser.add_argument(
        '-n', '--num-frames',
        type=int,
        default=10,
        help='Número de frames a analizar (default: 10)'
    )
    parser.add_argument(
        '-o', '--output',
        type=str,
        default=None,
        help='Archivo JSON de salida (opcional)'
    )
    
    args = parser.parse_args()
    
    if not os.path.exists(args.video_path):
        print(f"Error: El archivo {args.video_path} no existe")
        sys.exit(1)
    
    try:
        generator = VideoScriptGenerator()
        script = generator.generate_script(args.video_path, args.num_frames)
        
        # Guardar script
        if args.output:
            with open(args.output, 'w', encoding='utf-8') as f:
                json.dump(script, f, indent=2, ensure_ascii=False)
            print(f"✅ Script guardado en: {args.output}")
        else:
            print(json.dumps(script, indent=2, ensure_ascii=False))
        
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()



