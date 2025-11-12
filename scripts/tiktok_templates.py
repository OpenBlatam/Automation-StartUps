#!/usr/bin/env python3
"""
Sistema de templates para edición de videos
Permite aplicar estilos predefinidos de edición
"""

import json
import logging
from typing import Dict, Any, Optional
from pathlib import Path

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class VideoTemplate:
    """Template de edición de video"""
    
    def __init__(self, name: str, description: str, script: Dict[str, Any]):
        """
        Inicializa un template
        
        Args:
            name: Nombre del template
            description: Descripción del template
            script: Script de edición
        """
        self.name = name
        self.description = description
        self.script = script
    
    def apply_to_video(self, video_duration: float) -> Dict[str, Any]:
        """
        Aplica el template a un video ajustando tiempos
        
        Args:
            video_duration: Duración del video en segundos
            
        Returns:
            Script ajustado para el video
        """
        script = json.loads(json.dumps(self.script))  # Deep copy
        
        # Ajustar tiempos relativos a duración absoluta
        for transition in script.get('editing_script', {}).get('transitions', []):
            if 'start_time' in transition:
                transition['start_time'] = min(transition['start_time'], video_duration - 0.5)
            if 'end_time' in transition:
                transition['end_time'] = min(transition['end_time'], video_duration)
        
        for effect in script.get('editing_script', {}).get('effects', []):
            if 'start_time' in effect:
                effect['start_time'] = min(effect['start_time'], video_duration - 0.5)
            if 'end_time' in effect:
                effect['end_time'] = min(effect['end_time'], video_duration)
        
        for speed_change in script.get('editing_script', {}).get('speed_changes', []):
            if 'start_time' in speed_change:
                speed_change['start_time'] = min(speed_change['start_time'], video_duration - 0.5)
            if 'end_time' in speed_change:
                speed_change['end_time'] = min(speed_change['end_time'], video_duration)
        
        return script


class TemplateManager:
    """Gestor de templates de edición"""
    
    def __init__(self, templates_dir: Optional[str] = None):
        """
        Inicializa el gestor de templates
        
        Args:
            templates_dir: Directorio donde están los templates
        """
        self.templates_dir = Path(templates_dir or "~/.tiktok_templates").expanduser()
        self.templates_dir.mkdir(parents=True, exist_ok=True)
        self.templates = {}
        self._load_templates()
    
    def _load_templates(self):
        """Carga templates desde archivos"""
        for template_file in self.templates_dir.glob("*.json"):
            try:
                with open(template_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    template = VideoTemplate(
                        data['name'],
                        data.get('description', ''),
                        data['script']
                    )
                    self.templates[data['name']] = template
                    logger.info(f"Template cargado: {data['name']}")
            except Exception as e:
                logger.error(f"Error cargando template {template_file}: {e}")
    
    def get_template(self, name: str) -> Optional[VideoTemplate]:
        """Obtiene un template por nombre"""
        return self.templates.get(name)
    
    def list_templates(self) -> list:
        """Lista todos los templates disponibles"""
        return [
            {
                'name': t.name,
                'description': t.description
            }
            for t in self.templates.values()
        ]
    
    def save_template(self, name: str, description: str, script: Dict[str, Any]):
        """Guarda un nuevo template"""
        template = VideoTemplate(name, description, script)
        self.templates[name] = template
        
        template_file = self.templates_dir / f"{name}.json"
        with open(template_file, 'w', encoding='utf-8') as f:
            json.dump({
                'name': name,
                'description': description,
                'script': script
            }, f, indent=2, ensure_ascii=False)
        
        logger.info(f"Template guardado: {name}")


# Templates predefinidos
PREDEFINED_TEMPLATES = {
    'cinematic': {
        'name': 'Cinematic',
        'description': 'Look cinematográfico con transiciones suaves',
        'script': {
            'editing_script': {
                'transitions': [
                    {'start_time': 0, 'end_time': 1, 'type': 'fade_in'},
                    {'start_time': -1, 'end_time': 0, 'type': 'fade_out'}
                ],
                'effects': [
                    {'type': 'cinematic', 'start_time': 0, 'end_time': -1}
                ],
                'cuts': [],
                'speed_changes': []
            }
        }
    },
    'energetic': {
        'name': 'Energetic',
        'description': 'Edición rápida y dinámica con zoom y cambios de velocidad',
        'script': {
            'editing_script': {
                'transitions': [
                    {'start_time': 0, 'end_time': 0.5, 'type': 'fade_in'}
                ],
                'effects': [
                    {'type': 'ken_burns', 'start_time': 0, 'end_time': -1, 'zoom': 1.3, 'pan_direction': 'center'}
                ],
                'cuts': [],
                'speed_changes': [
                    {'start_time': 0, 'end_time': -1, 'speed': 1.1, 'description': 'Slightly faster'}
                ]
            }
        }
    },
    'dramatic': {
        'name': 'Dramatic',
        'description': 'Efectos dramáticos con slow motion y zoom',
        'script': {
            'editing_script': {
                'transitions': [
                    {'start_time': 0, 'end_time': 2, 'type': 'fade_in'},
                    {'start_time': -2, 'end_time': 0, 'type': 'fade_out'}
                ],
                'effects': [
                    {'type': 'zoom', 'start_time': 0, 'end_time': -1, 'intensity': 1.2}
                ],
                'cuts': [],
                'speed_changes': [
                    {'start_time': 0, 'end_time': -1, 'speed': 0.8, 'description': 'Slow motion'}
                ]
            }
        }
    },
    'minimal': {
        'name': 'Minimal',
        'description': 'Edición mínima con solo fade in/out',
        'script': {
            'editing_script': {
                'transitions': [
                    {'start_time': 0, 'end_time': 1, 'type': 'fade_in'},
                    {'start_time': -1, 'end_time': 0, 'type': 'fade_out'}
                ],
                'effects': [],
                'cuts': [],
                'speed_changes': []
            }
        }
    }
}


def create_default_templates(templates_dir: Optional[str] = None):
    """Crea templates predefinidos"""
    manager = TemplateManager(templates_dir)
    
    for template_data in PREDEFINED_TEMPLATES.values():
        manager.save_template(
            template_data['name'],
            template_data['description'],
            template_data['script']
        )
    
    logger.info(f"Templates predefinidos creados en {manager.templates_dir}")


def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='Gestor de templates de edición')
    parser.add_argument('command', choices=['list', 'create', 'init'], help='Comando')
    parser.add_argument('-n', '--name', help='Nombre del template')
    parser.add_argument('-d', '--description', help='Descripción')
    parser.add_argument('-f', '--file', help='Archivo JSON con script')
    
    args = parser.parse_args()
    
    manager = TemplateManager()
    
    if args.command == 'init':
        create_default_templates()
        print("✅ Templates predefinidos creados")
    
    elif args.command == 'list':
        templates = manager.list_templates()
        if templates:
            print("\n📋 Templates disponibles:\n")
            for t in templates:
                print(f"  • {t['name']}: {t['description']}")
        else:
            print("No hay templates disponibles. Ejecuta 'init' para crear templates predefinidos.")
    
    elif args.command == 'create':
        if not all([args.name, args.file]):
            print("Error: Se requiere --name y --file")
            return
        
        with open(args.file, 'r', encoding='utf-8') as f:
            script = json.load(f)
        
        description = args.description or "Template personalizado"
        manager.save_template(args.name, description, script)
        print(f"✅ Template '{args.name}' creado")


if __name__ == '__main__':
    main()


