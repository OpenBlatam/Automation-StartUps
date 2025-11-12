#!/usr/bin/env python3
"""
API REST para procesamiento de videos de TikTok
Permite integración con otros sistemas vía HTTP
"""

import os
import sys
import json
import logging
import asyncio
from datetime import datetime
from typing import Dict, Any, Optional
from pathlib import Path

from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
import threading

from tiktok_downloader import TikTokDownloader
from video_script_generator import VideoScriptGenerator
from video_editor import VideoEditor
from tiktok_analytics import TikTokAnalytics

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)

# Inicializar componentes
downloader = TikTokDownloader()
script_generator = VideoScriptGenerator()
editor = VideoEditor()
analytics = TikTokAnalytics()

# Directorio para archivos temporales
TEMP_DIR = Path("/tmp/tiktok_api")
TEMP_DIR.mkdir(parents=True, exist_ok=True)


@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'version': '3.0'
    })


@app.route('/api/v1/download', methods=['POST'])
def download_video():
    """Descarga un video de TikTok"""
    try:
        data = request.json
        url = data.get('url')
        
        if not url:
            return jsonify({'error': 'URL requerida'}), 400
        
        logger.info(f"Descargando video: {url}")
        result = downloader.download_video(url)
        
        # Registrar en analytics
        analytics.record_processing({
            'url': url,
            'status': 'completed' if result.get('success') else 'error',
            'started_at': datetime.now().isoformat(),
            'completed_at': datetime.now().isoformat(),
            'file_size': result.get('file_size'),
            'duration': result.get('duration'),
            'from_cache': result.get('from_cache', False),
            'error_message': result.get('error')
        })
        
        return jsonify(result)
    
    except Exception as e:
        logger.error(f"Error en download: {e}", exc_info=True)
        return jsonify({'error': str(e)}), 500


@app.route('/api/v1/generate-script', methods=['POST'])
def generate_script():
    """Genera script de edición para un video"""
    try:
        data = request.json
        video_path = data.get('video_path')
        num_frames = data.get('num_frames', 10)
        
        if not video_path or not os.path.exists(video_path):
            return jsonify({'error': 'Video path inválido'}), 400
        
        logger.info(f"Generando script para: {video_path}")
        script = script_generator.generate_script(video_path, num_frames)
        
        return jsonify(script)
    
    except Exception as e:
        logger.error(f"Error generando script: {e}", exc_info=True)
        return jsonify({'error': str(e)}), 500


@app.route('/api/v1/edit', methods=['POST'])
def edit_video():
    """Edita un video aplicando un script"""
    try:
        data = request.json
        video_path = data.get('video_path')
        script_data = data.get('script')
        output_filename = data.get('output_filename')
        
        if not video_path or not os.path.exists(video_path):
            return jsonify({'error': 'Video path inválido'}), 400
        
        if not script_data:
            return jsonify({'error': 'Script requerido'}), 400
        
        # Guardar script temporalmente
        script_path = TEMP_DIR / f"script_{datetime.now().timestamp()}.json"
        with open(script_path, 'w', encoding='utf-8') as f:
            json.dump(script_data, f, ensure_ascii=False)
        
        logger.info(f"Editando video: {video_path}")
        result = editor.edit_video_from_dict(video_path, script_data, output_filename)
        
        # Limpiar script temporal
        if script_path.exists():
            script_path.unlink()
        
        return jsonify(result)
    
    except Exception as e:
        logger.error(f"Error editando video: {e}", exc_info=True)
        return jsonify({'error': str(e)}), 500


@app.route('/api/v1/process', methods=['POST'])
def process_complete():
    """Procesa un video completo (download + script + edit)"""
    try:
        data = request.json
        url = data.get('url')
        num_frames = data.get('num_frames', 10)
        
        if not url:
            return jsonify({'error': 'URL requerida'}), 400
        
        start_time = datetime.now()
        logger.info(f"Procesando video completo: {url}")
        
        # 1. Descargar
        download_result = downloader.download_video(url)
        if not download_result.get('success'):
            return jsonify(download_result), 500
        
        video_path = download_result['file_path']
        
        # 2. Generar script
        script = script_generator.generate_script(video_path, num_frames)
        
        # 3. Editar
        edit_result = editor.edit_video_from_dict(video_path, script)
        if not edit_result.get('success'):
            return jsonify(edit_result), 500
        
        processing_time = (datetime.now() - start_time).total_seconds()
        
        # Registrar en analytics
        analytics.record_processing({
            'url': url,
            'status': 'completed',
            'started_at': start_time.isoformat(),
            'completed_at': datetime.now().isoformat(),
            'processing_time': processing_time,
            'file_size': edit_result.get('file_size'),
            'duration': edit_result.get('duration'),
            'from_cache': download_result.get('from_cache', False)
        })
        
        return jsonify({
            'success': True,
            'download': download_result,
            'script': script,
            'edit': edit_result,
            'processing_time': processing_time
        })
    
    except Exception as e:
        logger.error(f"Error procesando video: {e}", exc_info=True)
        return jsonify({'error': str(e)}), 500


@app.route('/api/v1/analytics/stats', methods=['GET'])
def get_stats():
    """Obtiene estadísticas de analytics"""
    try:
        days = int(request.args.get('days', 7))
        stats = analytics.get_stats(days)
        return jsonify(stats)
    
    except Exception as e:
        logger.error(f"Error obteniendo stats: {e}", exc_info=True)
        return jsonify({'error': str(e)}), 500


@app.route('/api/v1/analytics/top', methods=['GET'])
def get_top_urls():
    """Obtiene top URLs procesadas"""
    try:
        limit = int(request.args.get('limit', 10))
        top = analytics.get_top_urls(limit)
        return jsonify(top)
    
    except Exception as e:
        logger.error(f"Error obteniendo top URLs: {e}", exc_info=True)
        return jsonify({'error': str(e)}), 500


@app.route('/api/v1/video/<path:filename>', methods=['GET'])
def get_video(filename):
    """Sirve archivos de video procesados"""
    try:
        video_path = TEMP_DIR / filename
        if not video_path.exists():
            return jsonify({'error': 'Video no encontrado'}), 404
        
        return send_file(str(video_path), mimetype='video/mp4')
    
    except Exception as e:
        logger.error(f"Error sirviendo video: {e}", exc_info=True)
        return jsonify({'error': str(e)}), 500


@app.route('/api/v1/compress', methods=['POST'])
def compress_video():
    """Comprime un video"""
    try:
        from video_compressor import compress_video
        
        data = request.json
        input_path = data.get('input_path')
        target_size = data.get('target_size_mb', 50)
        quality = data.get('quality', 'medium')
        
        if not input_path or not os.path.exists(input_path):
            return jsonify({'error': 'Input path inválido'}), 400
        
        output_path = TEMP_DIR / f"compressed_{datetime.now().timestamp()}.mp4"
        result = compress_video(input_path, str(output_path), target_size, quality)
        
        if result.get('success'):
            result['download_url'] = f"/api/v1/video/{output_path.name}"
        
        return jsonify(result)
    
    except Exception as e:
        logger.error(f"Error comprimiendo: {e}", exc_info=True)
        return jsonify({'error': str(e)}), 500


if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(description='API REST para TikTok Auto Edit')
    parser.add_argument('-p', '--port', type=int, default=5000, help='Puerto (default: 5000)')
    parser.add_argument('-h', '--host', default='0.0.0.0', help='Host (default: 0.0.0.0)')
    parser.add_argument('--debug', action='store_true', help='Modo debug')
    
    args = parser.parse_args()
    
    logger.info(f"Iniciando servidor API en {args.host}:{args.port}")
    app.run(host=args.host, port=args.port, debug=args.debug)


