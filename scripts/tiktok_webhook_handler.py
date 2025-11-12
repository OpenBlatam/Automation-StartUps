#!/usr/bin/env python3
"""
Manejador de webhooks para integración con servicios externos
Recibe notificaciones y procesa videos automáticamente
"""

import os
import sys
import json
import logging
import hmac
import hashlib
from datetime import datetime
from typing import Dict, Any, Optional
from flask import Flask, request, jsonify
from flask_cors import CORS

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

# Secret para validar webhooks (configurar en env)
WEBHOOK_SECRET = os.getenv('WEBHOOK_SECRET', '')


def verify_webhook_signature(payload: bytes, signature: str, secret: str) -> bool:
    """
    Verifica la firma de un webhook
    
    Args:
        payload: Cuerpo del request en bytes
        signature: Firma recibida
        secret: Secret compartido
        
    Returns:
        True si la firma es válida
    """
    if not secret:
        logger.warning("Webhook secret no configurado, saltando verificación")
        return True
    
    expected_signature = hmac.new(
        secret.encode('utf-8'),
        payload,
        hashlib.sha256
    ).hexdigest()
    
    return hmac.compare_digest(expected_signature, signature)


@app.route('/webhook/tiktok', methods=['POST'])
def handle_tiktok_webhook():
    """Maneja webhooks de TikTok"""
    try:
        # Verificar firma si está configurada
        signature = request.headers.get('X-Signature', '')
        if WEBHOOK_SECRET and not verify_webhook_signature(
            request.data,
            signature,
            WEBHOOK_SECRET
        ):
            return jsonify({'error': 'Firma inválida'}), 401
        
        data = request.json
        url = data.get('url') or data.get('tiktok_url')
        
        if not url:
            return jsonify({'error': 'URL no proporcionada'}), 400
        
        logger.info(f"Webhook recibido para URL: {url}")
        
        # Procesar video
        start_time = datetime.now()
        download_result = downloader.download_video(url)
        
        if not download_result.get('success'):
            return jsonify({
                'status': 'error',
                'message': download_result.get('message'),
                'error': download_result.get('error')
            }), 500
        
        video_path = download_result['file_path']
        script = script_generator.generate_script(video_path)
        edit_result = editor.edit_video_from_dict(video_path, script)
        
        processing_time = (datetime.now() - start_time).total_seconds()
        
        # Registrar en analytics
        analytics.record_processing({
            'url': url,
            'status': 'completed' if edit_result.get('success') else 'error',
            'started_at': start_time.isoformat(),
            'completed_at': datetime.now().isoformat(),
            'processing_time': processing_time,
            'file_size': edit_result.get('file_size'),
            'duration': edit_result.get('duration'),
            'from_cache': download_result.get('from_cache', False)
        })
        
        return jsonify({
            'status': 'success',
            'url': url,
            'processing_time': processing_time,
            'video_path': edit_result.get('output_path'),
            'file_size': edit_result.get('file_size'),
            'duration': edit_result.get('duration')
        })
    
    except Exception as e:
        logger.error(f"Error procesando webhook: {e}", exc_info=True)
        return jsonify({'error': str(e)}), 500


@app.route('/webhook/telegram', methods=['POST'])
def handle_telegram_webhook():
    """Maneja webhooks de Telegram"""
    try:
        data = request.json
        message = data.get('message', {})
        text = message.get('text', '')
        chat_id = message.get('chat', {}).get('id')
        
        # Extraer URL de TikTok del mensaje
        import re
        tiktok_pattern = r'(https?://(?:www\.)?(?:vm\.|vt\.)?tiktok\.com/[^\s]+)'
        match = re.search(tiktok_pattern, text)
        
        if not match:
            return jsonify({
                'status': 'ignored',
                'message': 'No se encontró URL de TikTok'
            })
        
        url = match.group(1)
        logger.info(f"Webhook Telegram: procesando {url}")
        
        # Procesar (similar a handle_tiktok_webhook)
        # ... (código similar)
        
        return jsonify({'status': 'processing', 'url': url})
    
    except Exception as e:
        logger.error(f"Error procesando webhook Telegram: {e}", exc_info=True)
        return jsonify({'error': str(e)}), 500


@app.route('/webhook/whatsapp', methods=['POST'])
def handle_whatsapp_webhook():
    """Maneja webhooks de WhatsApp"""
    try:
        data = request.json
        
        # Extraer mensaje según formato (Twilio, WhatsApp Business API, etc.)
        message_text = (
            data.get('Body') or
            data.get('text') or
            data.get('message') or
            (data.get('entry', [{}])[0]
             .get('changes', [{}])[0]
             .get('value', {})
             .get('messages', [{}])[0]
             .get('text', {})
             .get('body', ''))
        )
        
        # Extraer URL
        import re
        tiktok_pattern = r'(https?://(?:www\.)?(?:vm\.|vt\.)?tiktok\.com/[^\s]+)'
        match = re.search(tiktok_pattern, message_text)
        
        if not match:
            return jsonify({
                'status': 'ignored',
                'message': 'No se encontró URL de TikTok'
            })
        
        url = match.group(1)
        logger.info(f"Webhook WhatsApp: procesando {url}")
        
        # Procesar (similar a handle_tiktok_webhook)
        # ... (código similar)
        
        return jsonify({'status': 'processing', 'url': url})
    
    except Exception as e:
        logger.error(f"Error procesando webhook WhatsApp: {e}", exc_info=True)
        return jsonify({'error': str(e)}), 500


@app.route('/webhook/health', methods=['GET'])
def webhook_health():
    """Health check para webhooks"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'webhook_secret_configured': bool(WEBHOOK_SECRET)
    })


if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(description='Webhook Handler para TikTok Auto Edit')
    parser.add_argument('-p', '--port', type=int, default=5001, help='Puerto (default: 5001)')
    parser.add_argument('-h', '--host', default='0.0.0.0', help='Host (default: 0.0.0.0)')
    parser.add_argument('--debug', action='store_true', help='Modo debug')
    
    args = parser.parse_args()
    
    logger.info(f"Iniciando webhook handler en {args.host}:{args.port}")
    app.run(host=args.host, port=args.port, debug=args.debug)


