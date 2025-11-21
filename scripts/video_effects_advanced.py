#!/usr/bin/env python3
"""
Efectos avanzados para videos
Incluye transiciones profesionales, filtros y efectos visuales
"""

import logging
from typing import Any, Optional, Dict
from moviepy.editor import VideoFileClip, CompositeVideoClip
from moviepy.video.fx import fadein, fadeout, resize, speedx
import numpy as np

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class AdvancedVideoEffects:
    """Efectos avanzados para edición de video"""
    
    @staticmethod
    def zoom_pan_effect(clip, start_zoom: float = 1.0, end_zoom: float = 1.5, 
                       pan_x: float = 0.0, pan_y: float = 0.0):
        """
        Efecto de zoom con pan (movimiento de cámara)
        
        Args:
            clip: Clip de video
            start_zoom: Zoom inicial
            end_zoom: Zoom final
            pan_x: Movimiento horizontal (-1 a 1)
            pan_y: Movimiento vertical (-1 a 1)
        """
        w, h = clip.size
        
        def zoom_pan(t):
            progress = t / clip.duration
            current_zoom = start_zoom + (end_zoom - start_zoom) * progress
            
            # Calcular offset para pan
            max_offset_x = w * (current_zoom - 1) / 2
            max_offset_y = h * (current_zoom - 1) / 2
            offset_x = int(max_offset_x * pan_x * progress)
            offset_y = int(max_offset_y * pan_y * progress)
            
            # Aplicar zoom y pan
            zoomed = clip.resize(current_zoom)
            frame = zoomed.get_frame(t)
            
            # Recortar según pan
            new_w, new_h = int(w * current_zoom), int(h * current_zoom)
            start_x = max(0, min(new_w - w, (new_w - w) // 2 + offset_x))
            start_y = max(0, min(new_h - h, (new_h - h) // 2 + offset_y))
            
            return frame[start_y:start_y+h, start_x:start_x+w]
        
        return clip.fl(lambda gf, t: zoom_pan(t))
    
    @staticmethod
    def color_grade(clip, brightness: float = 1.0, contrast: float = 1.0, 
                   saturation: float = 1.0, temperature: float = 0.0):
        """
        Corrección de color avanzada
        
        Args:
            clip: Clip de video
            brightness: Brillo (0.0 a 2.0)
            contrast: Contraste (0.0 a 2.0)
            saturation: Saturación (0.0 a 2.0)
            temperature: Temperatura de color (-100 a 100)
        """
        def adjust_color(image):
            # Ajustar brillo
            img = image.astype(np.float32) * brightness
            
            # Ajustar contraste
            img = (img - 128) * contrast + 128
            
            # Ajustar saturación
            if saturation != 1.0:
                gray = np.dot(img[...,:3], [0.299, 0.587, 0.114])
                gray = np.stack([gray, gray, gray], axis=2)
                img = gray + (img - gray) * saturation
            
            # Ajustar temperatura
            if temperature > 0:  # Cálido
                img[:, :, 0] = np.clip(img[:, :, 0] + temperature * 0.5, 0, 255)
                img[:, :, 2] = np.clip(img[:, :, 2] - temperature * 0.3, 0, 255)
            elif temperature < 0:  # Frío
                img[:, :, 2] = np.clip(img[:, :, 2] - temperature * 0.5, 0, 255)
                img[:, :, 0] = np.clip(img[:, :, 0] + temperature * 0.3, 0, 255)
            
            return np.clip(img, 0, 255).astype(np.uint8)
        
        return clip.fl_image(adjust_color)


def apply_ken_burns(clip, zoom: float = 1.3, pan_direction: str = 'center'):
    """Aplica efecto Ken Burns (zoom + pan)"""
    effects = AdvancedVideoEffects()
    pan_map = {
        'center': (0, 0),
        'left': (-0.3, 0),
        'right': (0.3, 0),
        'up': (0, -0.3),
        'down': (0, 0.3)
    }
    pan_x, pan_y = pan_map.get(pan_direction, (0, 0))
    return effects.zoom_pan_effect(clip, start_zoom=1.0, end_zoom=zoom, pan_x=pan_x, pan_y=pan_y)


def apply_cinematic_look(clip):
    """Aplica look cinematográfico (color grading)"""
    effects = AdvancedVideoEffects()
    return effects.color_grade(
        clip,
        brightness=0.95,
        contrast=1.1,
        saturation=0.9,
        temperature=10
    )
