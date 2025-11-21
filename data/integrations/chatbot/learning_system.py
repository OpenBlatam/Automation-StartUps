"""
Sistema de Aprendizaje y Mejora Continua del Chatbot
Versión: 2.0.0
"""

import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from pathlib import Path
from collections import defaultdict
import re

logger = logging.getLogger(__name__)


class LearningSystem:
    """
    Sistema que aprende de las interacciones para mejorar respuestas
    """
    
    def __init__(self, chatbot_engine, data_path: str = "learning_data"):
        self.chatbot = chatbot_engine
        self.data_path = Path(data_path)
        self.data_path.mkdir(exist_ok=True)
        
        # Datos de aprendizaje
        self.unresolved_questions = []  # Preguntas sin respuesta
        self.feedback_data = []  # Feedback de usuarios
        self.pattern_analysis = defaultdict(int)  # Patrones comunes
        self.improvement_suggestions = []
        
    def analyze_conversation(self, session_id: str, conversation_data: Dict):
        """
        Analiza una conversación para identificar oportunidades de mejora
        """
        if session_id not in self.chatbot.conversations:
            return
        
        conversation = self.chatbot.conversations[session_id]
        
        # Identificar preguntas no resueltas
        if len(conversation.messages) >= 3:
            # Si hay múltiples mensajes y baja satisfacción
            if any(s in [self.chatbot.Sentiment.NEGATIVE, self.chatbot.Sentiment.FRUSTRATED] 
                   for s in conversation.sentiment_history):
                # Buscar preguntas que no fueron respondidas
                for msg_data in conversation.messages:
                    if msg_data.get("intent") == "question":
                        # Verificar si se escaló (no se resolvió)
                        if conversation.intents_history and \
                           len([i for i in conversation.intents_history if i.value == "question"]) > 1:
                            self.unresolved_questions.append({
                                "question": msg_data.get("message", ""),
                                "session_id": session_id,
                                "timestamp": datetime.now().isoformat(),
                                "sentiment": msg_data.get("sentiment", "unknown")
                            })
        
        # Analizar patrones
        self._analyze_patterns(conversation)
        
        # Guardar datos
        self._save_learning_data()
    
    def _analyze_patterns(self, conversation):
        """Analiza patrones en las conversaciones"""
        # Patrones de palabras clave que llevan a escalamiento
        if any(s in [self.chatbot.Sentiment.NEGATIVE, self.chatbot.Sentiment.FRUSTRATED] 
               for s in conversation.sentiment_history):
            for msg_data in conversation.messages:
                message = msg_data.get("message", "").lower()
                # Extraer palabras clave
                words = re.findall(r'\b\w+\b', message)
                for word in words:
                    if len(word) > 4:  # Solo palabras significativas
                        self.pattern_analysis[word] += 1
    
    def record_feedback(self, session_id: str, question: str, 
                       was_helpful: bool, suggested_improvement: str = ""):
        """
        Registra feedback del usuario sobre una respuesta
        """
        feedback = {
            "session_id": session_id,
            "question": question,
            "was_helpful": was_helpful,
            "suggested_improvement": suggested_improvement,
            "timestamp": datetime.now().isoformat()
        }
        
        self.feedback_data.append(feedback)
        self._save_learning_data()
        
        # Si no fue útil, generar sugerencia de mejora
        if not was_helpful:
            self._generate_improvement_suggestion(feedback)
    
    def _generate_improvement_suggestion(self, feedback: Dict):
        """Genera sugerencias de mejora basadas en feedback negativo"""
        suggestion = {
            "type": "faq_improvement",
            "question": feedback["question"],
            "current_status": "unresolved_or_unsatisfactory",
            "suggested_action": "Add or improve FAQ",
            "priority": "high" if "error" in feedback["question"].lower() else "medium",
            "timestamp": datetime.now().isoformat(),
            "user_feedback": feedback.get("suggested_improvement", "")
        }
        
        self.improvement_suggestions.append(suggestion)
        logger.info(f"Sugerencia de mejora generada: {suggestion['question']}")
    
    def get_unresolved_questions(self, limit: int = 20) -> List[Dict]:
        """Obtiene preguntas no resueltas más frecuentes"""
        # Agrupar por pregunta similar
        question_groups = defaultdict(int)
        for q in self.unresolved_questions:
            # Normalizar pregunta
            normalized = q["question"].lower().strip()
            question_groups[normalized] += 1
        
        # Ordenar por frecuencia
        sorted_questions = sorted(
            question_groups.items(),
            key=lambda x: x[1],
            reverse=True
        )
        
        return [
            {
                "question": q,
                "frequency": count,
                "priority": "high" if count >= 5 else "medium"
            }
            for q, count in sorted_questions[:limit]
        ]
    
    def get_improvement_suggestions(self) -> List[Dict]:
        """Obtiene sugerencias de mejora"""
        return sorted(
            self.improvement_suggestions,
            key=lambda x: (x["priority"] == "high", x["timestamp"]),
            reverse=True
        )
    
    def generate_faq_suggestions(self) -> List[Dict]:
        """
        Genera sugerencias de nuevas FAQs basadas en preguntas no resueltas
        """
        unresolved = self.get_unresolved_questions(limit=10)
        suggestions = []
        
        for item in unresolved:
            if item["frequency"] >= 3:  # Pregunta frecuente
                suggestion = {
                    "question": item["question"],
                    "suggested_keywords": self._extract_keywords(item["question"]),
                    "frequency": item["frequency"],
                    "priority": item["priority"],
                    "recommended_action": "Add to FAQs"
                }
                suggestions.append(suggestion)
        
        return suggestions
    
    def _extract_keywords(self, text: str) -> List[str]:
        """Extrae palabras clave de un texto"""
        # Palabras comunes a ignorar
        stop_words = {
            "es", "el", "la", "de", "que", "y", "a", "en", "un", "ser", "se",
            "no", "haber", "por", "con", "su", "para", "como", "estar", "tener",
            "le", "lo", "todo", "pero", "más", "hacer", "o", "poder", "decir",
            "este", "ir", "otro", "ese", "la", "si", "me", "ya", "ver", "porque",
            "dar", "cuando", "él", "muy", "sin", "vez", "mucho", "saber", "qué",
            "sobre", "mi", "alguno", "mismo", "yo", "también", "hasta", "año",
            "dos", "querer", "entre", "así", "primero", "desde", "grande",
            "eso", "ni", "nos", "llegar", "pasar", "tiempo", "ella", "sí",
            "uno", "bien", "poco", "deber", "entonces", "poner", "cosa", "tanto",
            "hombre", "parecer", "nuestro", "tan", "donde", "ahora", "parte",
            "después", "vida", "quedar", "siempre", "creer", "hablar", "llevar",
            "dejar", "nada", "cada", "seguir", "menos", "nuevo", "encontrar",
            "venir", "pensar", "saber", "tomar", "mismo", "cual", "casi",
            "tener", "hacer", "ver", "dar", "decir", "poder", "ir", "ser",
            "estar", "haber", "querer", "llegar", "pasar", "deber", "poner",
            "parecer", "quedar", "hablar", "llevar", "dejar", "seguir",
            "encontrar", "venir", "pensar", "tomar", "tratar", "mirar",
            "contar", "empezar", "esperar", "buscar", "existir", "entrar",
            "trabajar", "escribir", "perder", "producir", "ocurrir", "entender",
            "pedir", "recibir", "recordar", "terminar", "permitir", "aparecer",
            "conseguir", "comenzar", "servir", "sacar", "necesitar", "mantener",
            "resultar", "leer", "caer", "cambiar", "presentar", "crear",
            "abrir", "considerar", "oír", "acabar", "convertir", "ganar",
            "formar", "traer", "partir", "morir", "aceptar", "realizar",
            "suponer", "comprender", "lograr", "explicar", "preguntar",
            "tocar", "reconocer", "estudiar", "alcanzar", "nacer", "dirigir",
            "correr", "utilizar", "pagar", "ayudar", "gustar", "jugar",
            "escuchar", "cumplir", "ofrecer", "descubrir", "levantar",
            "intentar", "usar", "obtener", "indicar", "formar", "reducir",
            "establecer", "desarrollar", "observar", "iniciar", "conseguir",
            "aplicar", "obtener", "conseguir", "lograr", "alcanzar",
            "conseguir", "obtener", "lograr", "alcanzar", "conseguir"
        }
        
        words = re.findall(r'\b\w+\b', text.lower())
        keywords = [w for w in words if len(w) > 3 and w not in stop_words]
        
        # Retornar las 5 palabras más relevantes
        return list(set(keywords))[:5]
    
    def analyze_weekly_performance(self) -> Dict:
        """
        Analiza el rendimiento semanal y genera recomendaciones
        """
        week_ago = datetime.now() - timedelta(days=7)
        
        # Analizar métricas
        metrics = self.chatbot.get_metrics()
        
        # Identificar tendencias
        analysis = {
            "period": "last_7_days",
            "metrics": metrics,
            "recommendations": [],
            "top_unresolved": self.get_unresolved_questions(limit=5),
            "improvement_suggestions": self.get_improvement_suggestions()[:5]
        }
        
        # Generar recomendaciones
        if metrics["resolution_rate"] < 80:
            analysis["recommendations"].append({
                "type": "low_resolution_rate",
                "message": f"La tasa de resolución ({metrics['resolution_rate']}%) está por debajo del objetivo (80%). Considera agregar más FAQs.",
                "priority": "high"
            })
        
        if metrics["avg_satisfaction"] < 4.5:
            analysis["recommendations"].append({
                "type": "low_satisfaction",
                "message": f"La satisfacción ({metrics['avg_satisfaction']}/5) está por debajo del objetivo (4.5/5). Revisa las respuestas más frecuentes.",
                "priority": "high"
            })
        
        if metrics["escalation_rate"] > 20:
            analysis["recommendations"].append({
                "type": "high_escalation",
                "message": f"La tasa de escalamiento ({metrics['escalation_rate']}%) es alta. Mejora la detección de intención y FAQs.",
                "priority": "medium"
            })
        
        return analysis
    
    def _save_learning_data(self):
        """Guarda los datos de aprendizaje"""
        try:
            # Guardar preguntas no resueltas
            unresolved_file = self.data_path / "unresolved_questions.json"
            with open(unresolved_file, 'w', encoding='utf-8') as f:
                json.dump(self.unresolved_questions[-100:], f, indent=2, ensure_ascii=False)
            
            # Guardar feedback
            feedback_file = self.data_path / "feedback.json"
            with open(feedback_file, 'w', encoding='utf-8') as f:
                json.dump(self.feedback_data[-100:], f, indent=2, ensure_ascii=False)
            
            # Guardar sugerencias
            suggestions_file = self.data_path / "improvement_suggestions.json"
            with open(suggestions_file, 'w', encoding='utf-8') as f:
                json.dump(self.improvement_suggestions, f, indent=2, ensure_ascii=False)
            
        except Exception as e:
            logger.error(f"Error guardando datos de aprendizaje: {e}")
    
    def load_learning_data(self):
        """Carga datos de aprendizaje guardados"""
        try:
            # Cargar preguntas no resueltas
            unresolved_file = self.data_path / "unresolved_questions.json"
            if unresolved_file.exists():
                with open(unresolved_file, 'r', encoding='utf-8') as f:
                    self.unresolved_questions = json.load(f)
            
            # Cargar feedback
            feedback_file = self.data_path / "feedback.json"
            if feedback_file.exists():
                with open(feedback_file, 'r', encoding='utf-8') as f:
                    self.feedback_data = json.load(f)
            
            # Cargar sugerencias
            suggestions_file = self.data_path / "improvement_suggestions.json"
            if suggestions_file.exists():
                with open(suggestions_file, 'r', encoding='utf-8') as f:
                    self.improvement_suggestions = json.load(f)
            
            logger.info("Datos de aprendizaje cargados")
        except Exception as e:
            logger.warning(f"No se pudieron cargar datos de aprendizaje: {e}")






