"""
Integración con Sistemas de Voice (Call Center).

Soporta transcripción de llamadas, análisis de sentimiento en voz,
y creación automática de tickets desde llamadas.
"""
import logging
import os
from typing import Dict, Any, List, Optional
from dataclasses import dataclass
from datetime import datetime

try:
    import requests
    REQUESTS_AVAILABLE = True
except ImportError:
    REQUESTS_AVAILABLE = False

logger = logging.getLogger(__name__)


@dataclass
class CallRecording:
    """Grabación de llamada."""
    call_id: str
    customer_phone: str
    agent_phone: Optional[str] = None
    duration_seconds: int = 0
    recording_url: Optional[str] = None
    transcript: Optional[str] = None
    started_at: Optional[datetime] = None
    ended_at: Optional[datetime] = None
    metadata: Dict[str, Any] = None


@dataclass
class VoiceAnalysis:
    """Análisis de voz."""
    sentiment: str  # positive, neutral, negative
    sentiment_score: float  # -1.0 a 1.0
    urgency_indicators: List[str]
    keywords: List[str]
    topics: List[str]
    customer_satisfaction: Optional[float] = None
    frustration_level: Optional[float] = None


class VoiceTranscriptionProvider:
    """Proveedor de transcripción de voz."""
    
    def __init__(self, provider: str = "openai", api_key: Optional[str] = None):
        """
        Inicializa proveedor de transcripción.
        
        Args:
            provider: 'openai', 'google', 'aws', 'assemblyai'
            api_key: API key del proveedor
        """
        self.provider = provider
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
    
    def transcribe(self, audio_url: str, language: str = "es") -> str:
        """
        Transcribe audio a texto.
        
        Args:
            audio_url: URL del audio
            language: Idioma (es, en, etc.)
            
        Returns:
            Texto transcrito
        """
        if self.provider == "openai":
            return self._transcribe_openai(audio_url, language)
        elif self.provider == "assemblyai":
            return self._transcribe_assemblyai(audio_url, language)
        elif self.provider == "google":
            return self._transcribe_google(audio_url, language)
        else:
            raise ValueError(f"Provider {self.provider} not supported")
    
    def _transcribe_openai(self, audio_url: str, language: str) -> str:
        """Transcribe usando OpenAI Whisper."""
        if not REQUESTS_AVAILABLE or not self.api_key:
            logger.warning("OpenAI API key not available")
            return ""
        
        try:
            # Descargar audio
            response = requests.get(audio_url, timeout=30)
            response.raise_for_status()
            
            # Usar OpenAI API
            import openai
            openai.api_key = self.api_key
            
            # Crear archivo temporal y transcribir
            import tempfile
            with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as tmp:
                tmp.write(response.content)
                tmp_path = tmp.name
            
            try:
                with open(tmp_path, "rb") as audio_file:
                    transcript = openai.Audio.transcribe(
                        model="whisper-1",
                        file=audio_file,
                        language=language
                    )
                return transcript.text
            finally:
                os.unlink(tmp_path)
                
        except Exception as e:
            logger.error(f"Error transcribing with OpenAI: {e}")
            return ""
    
    def _transcribe_assemblyai(self, audio_url: str, language: str) -> str:
        """Transcribe usando AssemblyAI."""
        if not REQUESTS_AVAILABLE:
            return ""
        
        api_key = os.getenv("ASSEMBLYAI_API_KEY") or self.api_key
        if not api_key:
            return ""
        
        try:
            # Subir audio
            headers = {"authorization": api_key}
            response = requests.post(
                "https://api.assemblyai.com/v2/transcript",
                json={"audio_url": audio_url},
                headers=headers,
                timeout=10
            )
            response.raise_for_status()
            transcript_id = response.json()["id"]
            
            # Esperar transcripción
            import time
            while True:
                response = requests.get(
                    f"https://api.assemblyai.com/v2/transcript/{transcript_id}",
                    headers=headers,
                    timeout=10
                )
                status = response.json()["status"]
                if status == "completed":
                    return response.json().get("text", "")
                elif status == "error":
                    raise Exception("Transcription failed")
                time.sleep(1)
                
        except Exception as e:
            logger.error(f"Error transcribing with AssemblyAI: {e}")
            return ""
    
    def _transcribe_google(self, audio_url: str, language: str) -> str:
        """Transcribe usando Google Cloud Speech-to-Text."""
        # Implementar según necesidad
        logger.warning("Google transcription not yet implemented")
        return ""


class VoiceAnalyzer:
    """Analizador de voz y transcripciones."""
    
    def __init__(self):
        """Inicializa analizador."""
        pass
    
    def analyze_transcript(self, transcript: str) -> VoiceAnalysis:
        """
        Analiza transcripción de llamada.
        
        Args:
            transcript: Texto transcrito
            
        Returns:
            Análisis de voz
        """
        # Análisis básico de sentimiento
        sentiment, sentiment_score = self._analyze_sentiment(transcript)
        
        # Detectar urgencia
        urgency_indicators = self._detect_urgency(transcript)
        
        # Extraer keywords
        keywords = self._extract_keywords(transcript)
        
        # Detectar topics
        topics = self._detect_topics(transcript)
        
        # Nivel de frustración
        frustration_level = self._calculate_frustration(transcript)
        
        # Satisfacción estimada
        customer_satisfaction = self._estimate_satisfaction(transcript, sentiment_score)
        
        return VoiceAnalysis(
            sentiment=sentiment,
            sentiment_score=sentiment_score,
            urgency_indicators=urgency_indicators,
            keywords=keywords,
            topics=topics,
            customer_satisfaction=customer_satisfaction,
            frustration_level=frustration_level
        )
    
    def _analyze_sentiment(self, text: str) -> tuple[str, float]:
        """Analiza sentimiento básico."""
        text_lower = text.lower()
        
        positive_words = ["gracias", "perfecto", "excelente", "bueno", "bien", "satisfecho"]
        negative_words = ["mal", "terrible", "horrible", "problema", "error", "no funciona"]
        
        positive_count = sum(1 for word in positive_words if word in text_lower)
        negative_count = sum(1 for word in negative_words if word in text_lower)
        
        if positive_count > negative_count:
            return "positive", 0.5 + (positive_count * 0.1)
        elif negative_count > positive_count:
            return "negative", -0.5 - (negative_count * 0.1)
        else:
            return "neutral", 0.0
    
    def _detect_urgency(self, text: str) -> List[str]:
        """Detecta indicadores de urgencia."""
        urgency_keywords = [
            "urgente", "inmediato", "ahora", "crítico", "importante",
            "no puedo esperar", "necesito ya", "asap"
        ]
        
        text_lower = text.lower()
        found = [kw for kw in urgency_keywords if kw in text_lower]
        return found
    
    def _extract_keywords(self, text: str, limit: int = 10) -> List[str]:
        """Extrae keywords importantes."""
        # Implementación simple - usar técnicas avanzadas como TF-IDF
        words = text.lower().split()
        # Filtrar stop words
        stop_words = {"el", "la", "de", "que", "y", "a", "en", "un", "es", "se", "no", "te", "lo", "le", "da", "su", "por", "son", "con", "las"}
        keywords = [w for w in words if w not in stop_words and len(w) > 3]
        # Contar frecuencia
        from collections import Counter
        counter = Counter(keywords)
        return [word for word, _ in counter.most_common(limit)]
    
    def _detect_topics(self, text: str) -> List[str]:
        """Detecta topics principales."""
        topics = []
        text_lower = text.lower()
        
        topic_keywords = {
            "facturación": ["factura", "pago", "cobro", "tarjeta", "precio"],
            "técnico": ["error", "bug", "no funciona", "problema técnico", "código"],
            "cuenta": ["cuenta", "login", "contraseña", "usuario", "acceso"],
            "producto": ["producto", "característica", "funcionalidad", "feature"],
            "soporte": ["ayuda", "soporte", "asistencia", "consultar"]
        }
        
        for topic, keywords in topic_keywords.items():
            if any(kw in text_lower for kw in keywords):
                topics.append(topic)
        
        return topics
    
    def _calculate_frustration(self, text: str) -> float:
        """Calcula nivel de frustración (0.0 a 1.0)."""
        frustration_words = [
            "molesto", "enojado", "frustrado", "cansado", "harto",
            "no aguanto", "terrible", "pésimo"
        ]
        
        text_lower = text.lower()
        count = sum(1 for word in frustration_words if word in text_lower)
        
        # Normalizar
        return min(count * 0.2, 1.0)
    
    def _estimate_satisfaction(self, text: str, sentiment_score: float) -> float:
        """Estima satisfacción del cliente (0.0 a 1.0)."""
        # Basado en sentimiento y palabras clave
        base_score = (sentiment_score + 1.0) / 2.0  # Normalizar -1 a 1 -> 0 a 1
        
        satisfaction_words = ["satisfecho", "contento", "feliz", "perfecto"]
        dissatisfaction_words = ["insatisfecho", "descontento", "molesto"]
        
        text_lower = text.lower()
        if any(word in text_lower for word in satisfaction_words):
            base_score = min(base_score + 0.2, 1.0)
        if any(word in text_lower for word in dissatisfaction_words):
            base_score = max(base_score - 0.3, 0.0)
        
        return base_score


class VoiceCallHandler:
    """Manejador de llamadas de voz."""
    
    def __init__(
        self,
        transcription_provider: VoiceTranscriptionProvider,
        voice_analyzer: VoiceAnalyzer
    ):
        """
        Inicializa manejador.
        
        Args:
            transcription_provider: Proveedor de transcripción
            voice_analyzer: Analizador de voz
        """
        self.transcription_provider = transcription_provider
        self.voice_analyzer = voice_analyzer
    
    def process_call(
        self,
        call_recording: CallRecording,
        auto_create_ticket: bool = True
    ) -> Dict[str, Any]:
        """
        Procesa una llamada: transcribe, analiza y opcionalmente crea ticket.
        
        Args:
            call_recording: Grabación de llamada
            auto_create_ticket: Crear ticket automáticamente
            
        Returns:
            Resultado del procesamiento
        """
        result = {
            "call_id": call_recording.call_id,
            "transcribed": False,
            "analyzed": False,
            "ticket_created": False
        }
        
        # Transcribir
        if call_recording.recording_url:
            transcript = self.transcription_provider.transcribe(
                call_recording.recording_url
            )
            if transcript:
                call_recording.transcript = transcript
                result["transcribed"] = True
                result["transcript"] = transcript
        
        # Analizar
        if call_recording.transcript:
            analysis = self.voice_analyzer.analyze_transcript(call_recording.transcript)
            result["analyzed"] = True
            result["analysis"] = {
                "sentiment": analysis.sentiment,
                "sentiment_score": analysis.sentiment_score,
                "urgency_indicators": analysis.urgency_indicators,
                "keywords": analysis.keywords,
                "topics": analysis.topics,
                "customer_satisfaction": analysis.customer_satisfaction,
                "frustration_level": analysis.frustration_level
            }
            
            # Crear ticket si está habilitado
            if auto_create_ticket and analysis.urgency_indicators:
                ticket_data = self._create_ticket_from_call(call_recording, analysis)
                result["ticket_data"] = ticket_data
                result["ticket_created"] = True
        
        return result
    
    def _create_ticket_from_call(
        self,
        call_recording: CallRecording,
        analysis: VoiceAnalysis
    ) -> Dict[str, Any]:
        """Crea datos de ticket desde llamada."""
        # Determinar prioridad basada en análisis
        priority = "normal"
        if analysis.frustration_level and analysis.frustration_level > 0.7:
            priority = "urgent"
        elif analysis.urgency_indicators:
            priority = "high"
        
        # Generar subject
        topics_str = ", ".join(analysis.topics[:2]) if analysis.topics else "Consulta"
        subject = f"Llamada: {topics_str}"
        
        # Descripción con transcript y análisis
        description = f"Llamada recibida de {call_recording.customer_phone}\n\n"
        description += f"Transcripción:\n{call_recording.transcript}\n\n"
        description += f"Análisis:\n"
        description += f"- Sentimiento: {analysis.sentiment} (score: {analysis.sentiment_score:.2f})\n"
        description += f"- Indicadores de urgencia: {', '.join(analysis.urgency_indicators)}\n"
        description += f"- Topics: {', '.join(analysis.topics)}\n"
        description += f"- Frustración: {analysis.frustration_level:.2f}\n"
        
        return {
            "subject": subject,
            "description": description,
            "customer_phone": call_recording.customer_phone,
            "priority": priority,
            "category": analysis.topics[0] if analysis.topics else "general",
            "tags": ["voice_call", "transcribed"] + analysis.topics,
            "metadata": {
                "call_id": call_recording.call_id,
                "duration_seconds": call_recording.duration_seconds,
                "analysis": {
                    "sentiment": analysis.sentiment,
                    "sentiment_score": analysis.sentiment_score,
                    "customer_satisfaction": analysis.customer_satisfaction
                }
            }
        }

