#!/usr/bin/env python3
"""
Utilidades compartidas para los chatbots
Incluye funciones de exportación, análisis y mejoras adicionales
"""

import json
import csv
from typing import Dict, List, Optional
from datetime import datetime
from pathlib import Path
from collections import Counter
import re


def export_metrics_to_json(metrics: Dict, output_file: str = "chatbot_metrics.json"):
    """
    Exporta métricas del chatbot a un archivo JSON.
    
    Args:
        metrics: Diccionario con las métricas
        output_file: Nombre del archivo de salida
    """
    export_data = {
        "exported_at": datetime.now().isoformat(),
        "metrics": metrics
    }
    
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(export_data, f, ensure_ascii=False, indent=2)
    
    return output_file


def export_metrics_to_csv(metrics: Dict, output_file: str = "chatbot_metrics.csv"):
    """
    Exporta métricas del chatbot a un archivo CSV.
    
    Args:
        metrics: Diccionario con las métricas
        output_file: Nombre del archivo de salida
    """
    with open(output_file, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        
        # Escribir encabezados
        writer.writerow(['Métrica', 'Valor'])
        writer.writerow(['Fecha de exportación', datetime.now().isoformat()])
        writer.writerow(['Total mensajes', metrics.get('total_messages', 0)])
        writer.writerow(['Total escalaciones', metrics.get('total_escalations', 0)])
        writer.writerow(['Tasa de escalación', f"{metrics.get('escalation_rate', 0):.2%}"])
        writer.writerow(['Confianza promedio', f"{metrics.get('average_confidence', 0):.2f}"])
        writer.writerow(['Tiempo promedio (s)', f"{metrics.get('average_processing_time', 0):.3f}"])
        writer.writerow(['Tasa de match FAQ', f"{metrics.get('faq_match_rate', 0):.2%}"])
        
        # Distribución de intenciones
        writer.writerow([])
        writer.writerow(['Distribución de Intenciones'])
        for intent, count in metrics.get('intent_distribution', {}).items():
            writer.writerow([intent, count])
    
    return output_file


def analyze_sentiment_basic(message: str) -> Dict[str, float]:
    """
    Análisis básico de sentimiento usando palabras clave.
    Retorna scores de positivo, negativo y neutro.
    
    Args:
        message: Mensaje a analizar
    
    Returns:
        Dict con scores de sentimiento
    """
    message_lower = message.lower()
    
    # Palabras positivas
    positive_words = [
        'gracias', 'excelente', 'bueno', 'genial', 'perfecto', 'sí', 'ok',
        'bien', 'me gusta', 'útil', 'ayuda', 'satisfecho', 'contento',
        'feliz', 'agradecido', 'maravilloso', 'fantástico', 'increíble'
    ]
    
    # Palabras negativas
    negative_words = [
        'no', 'mal', 'malo', 'terrible', 'horrible', 'problema', 'error',
        'no funciona', 'no sirve', 'frustrado', 'molesto', 'enojado',
        'decepcionado', 'confundido', 'difícil', 'complejo', 'no entiendo'
    ]
    
    positive_count = sum(1 for word in positive_words if word in message_lower)
    negative_count = sum(1 for word in negative_words if word in message_lower)
    
    total_words = len(re.findall(r'\b\w+\b', message_lower))
    
    if total_words == 0:
        return {"positive": 0.0, "negative": 0.0, "neutral": 1.0}
    
    positive_score = min(positive_count / max(total_words, 1), 1.0)
    negative_score = min(negative_count / max(total_words, 1), 1.0)
    neutral_score = 1.0 - positive_score - negative_score
    
    # Normalizar
    total = positive_score + negative_score + neutral_score
    if total > 0:
        positive_score /= total
        negative_score /= total
        neutral_score /= total
    
    return {
        "positive": round(positive_score, 3),
        "negative": round(negative_score, 3),
        "neutral": round(neutral_score, 3)
    }


def extract_keywords(text: str, min_length: int = 3, max_keywords: int = 10) -> List[str]:
    """
    Extrae palabras clave de un texto.
    
    Args:
        text: Texto del que extraer keywords
        min_length: Longitud mínima de las palabras
        max_keywords: Número máximo de keywords a retornar
    
    Returns:
        Lista de keywords ordenadas por frecuencia
    """
    # Palabras comunes a excluir
    stop_words = {
        'el', 'la', 'los', 'las', 'un', 'una', 'unos', 'unas',
        'de', 'del', 'en', 'a', 'al', 'con', 'por', 'para',
        'que', 'qué', 'cómo', 'cuándo', 'dónde', 'quién',
        'es', 'son', 'está', 'están', 'ser', 'estar',
        'y', 'o', 'pero', 'si', 'no', 'también', 'más'
    }
    
    # Extraer palabras
    words = re.findall(r'\b\w+\b', text.lower())
    
    # Filtrar stop words y por longitud
    filtered_words = [
        w for w in words 
        if len(w) >= min_length and w not in stop_words
    ]
    
    # Contar frecuencia
    word_counts = Counter(filtered_words)
    
    # Retornar las más frecuentes
    return [word for word, count in word_counts.most_common(max_keywords)]


def calculate_text_similarity(text1: str, text2: str) -> float:
    """
    Calcula similitud entre dos textos usando Jaccard similarity.
    
    Args:
        text1: Primer texto
        text2: Segundo texto
    
    Returns:
        Score de similitud entre 0 y 1
    """
    words1 = set(re.findall(r'\b\w+\b', text1.lower()))
    words2 = set(re.findall(r'\b\w+\b', text2.lower()))
    
    if not words1 and not words2:
        return 1.0
    
    if not words1 or not words2:
        return 0.0
    
    intersection = len(words1.intersection(words2))
    union = len(words1.union(words2))
    
    return intersection / union if union > 0 else 0.0


def format_response_time(seconds: float) -> str:
    """
    Formatea el tiempo de respuesta en formato legible.
    
    Args:
        seconds: Tiempo en segundos
    
    Returns:
        String formateado
    """
    if seconds < 0.001:
        return f"{seconds * 1000000:.0f}μs"
    elif seconds < 1:
        return f"{seconds * 1000:.1f}ms"
    else:
        return f"{seconds:.2f}s"


def generate_conversation_summary(conversation_history: List[Dict]) -> Dict:
    """
    Genera un resumen de una conversación.
    
    Args:
        conversation_history: Historial de conversación
    
    Returns:
        Dict con resumen de la conversación
    """
    if not conversation_history:
        return {
            "total_messages": 0,
            "user_messages": 0,
            "bot_messages": 0,
            "topics": [],
            "sentiment": {"positive": 0.0, "negative": 0.0, "neutral": 1.0}
        }
    
    user_messages = [msg for msg in conversation_history if msg.get('role') == 'user']
    bot_messages = [msg for msg in conversation_history if msg.get('role') == 'assistant']
    
    # Extraer keywords de todos los mensajes del usuario
    all_user_text = " ".join([msg.get('content', '') for msg in user_messages])
    topics = extract_keywords(all_user_text, max_keywords=5)
    
    # Análisis de sentimiento promedio
    sentiments = [analyze_sentiment_basic(msg.get('content', '')) for msg in user_messages]
    avg_sentiment = {
        "positive": sum(s['positive'] for s in sentiments) / len(sentiments) if sentiments else 0.0,
        "negative": sum(s['negative'] for s in sentiments) / len(sentiments) if sentiments else 0.0,
        "neutral": sum(s['neutral'] for s in sentiments) / len(sentiments) if sentiments else 1.0
    }
    
    return {
        "total_messages": len(conversation_history),
        "user_messages": len(user_messages),
        "bot_messages": len(bot_messages),
        "topics": topics,
        "sentiment": avg_sentiment,
        "duration_estimate": len(conversation_history) * 30  # Estimación: 30s por mensaje
    }


def validate_email(email: str) -> bool:
    """
    Valida formato de email básico.
    
    Args:
        email: Email a validar
    
    Returns:
        True si el formato es válido
    """
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email))


def sanitize_input(text: str, max_length: int = 2000) -> str:
    """
    Sanitiza entrada del usuario.
    
    Args:
        text: Texto a sanitizar
        max_length: Longitud máxima
    
    Returns:
        Texto sanitizado
    """
    # Remover caracteres de control excepto newlines y tabs
    text = re.sub(r'[\x00-\x08\x0b-\x0c\x0e-\x1f]', '', text)
    
    # Limitar longitud
    if len(text) > max_length:
        text = text[:max_length] + "..."
    
    return text.strip()


def create_metrics_dashboard_data(metrics: Dict) -> Dict:
    """
    Crea datos formateados para un dashboard de métricas.
    
    Args:
        metrics: Métricas del chatbot
    
    Returns:
        Dict con datos formateados para dashboard
    """
    return {
        "summary": {
            "total_messages": metrics.get('total_messages', 0),
            "total_escalations": metrics.get('total_escalations', 0),
            "escalation_rate": f"{metrics.get('escalation_rate', 0):.1%}",
            "average_confidence": f"{metrics.get('average_confidence', 0):.2f}",
            "average_response_time": format_response_time(metrics.get('average_processing_time', 0)),
            "faq_match_rate": f"{metrics.get('faq_match_rate', 0):.1%}"
        },
        "intent_distribution": metrics.get('intent_distribution', {}),
        "performance": {
            "messages_per_minute": 60 / metrics.get('average_processing_time', 1) if metrics.get('average_processing_time', 0) > 0 else 0,
            "success_rate": 1 - metrics.get('escalation_rate', 0)
        },
        "exported_at": datetime.now().isoformat()
    }






