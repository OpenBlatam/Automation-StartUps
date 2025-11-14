#!/usr/bin/env python3
"""
ClickUp Brain - Sistema de IA Conversacional Avanzada
===================================================

Sistema de inteligencia artificial conversacional que permite interacción
en lenguaje natural con el ClickUp Brain System.
"""

import os
import sys
import json
import re
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
import logging
from dataclasses import dataclass
from enum import Enum
import random

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ConversationState(Enum):
    """Estados de la conversación."""
    GREETING = "greeting"
    LISTENING = "listening"
    PROCESSING = "processing"
    RESPONDING = "responding"
    LEARNING = "learning"
    ERROR = "error"

class IntentType(Enum):
    """Tipos de intenciones del usuario."""
    GREETING = "greeting"
    QUESTION = "question"
    COMMAND = "command"
    COMPLAINT = "complaint"
    COMPLIMENT = "compliment"
    REQUEST_HELP = "request_help"
    REQUEST_ANALYSIS = "request_analysis"
    REQUEST_REPORT = "request_report"
    REQUEST_OPTIMIZATION = "request_optimization"
    UNKNOWN = "unknown"

@dataclass
class ConversationContext:
    """Contexto de la conversación."""
    user_id: str
    session_id: str
    conversation_history: List[Dict]
    current_intent: IntentType
    entities: Dict[str, Any]
    sentiment: str
    confidence: float
    timestamp: datetime

class NaturalLanguageProcessor:
    """Procesador de lenguaje natural para entender intenciones."""
    
    def __init__(self):
        self.intent_patterns = {
            IntentType.GREETING: [
                r'\b(hola|hi|hello|buenos días|good morning|hey)\b',
                r'\b(¿cómo estás?|how are you|what\'s up)\b'
            ],
            IntentType.QUESTION: [
                r'\b(¿qué|what|how|why|when|where|who)\b',
                r'\b(¿puedes|can you|could you)\b',
                r'\b(¿me puedes|can you help me)\b'
            ],
            IntentType.COMMAND: [
                r'\b(analiza|analyze|muestra|show|genera|generate)\b',
                r'\b(crea|create|haz|make|ejecuta|execute)\b',
                r'\b(optimiza|optimize|mejora|improve)\b'
            ],
            IntentType.REQUEST_ANALYSIS: [
                r'\b(análisis|analysis|analizar|analyze)\b',
                r'\b(eficiencia|efficiency|productividad|productivity)\b',
                r'\b(equipo|team|rendimiento|performance)\b'
            ],
            IntentType.REQUEST_REPORT: [
                r'\b(reporte|report|informe|summary)\b',
                r'\b(resumen|summary|estadísticas|statistics)\b',
                r'\b(métricas|metrics|datos|data)\b'
            ],
            IntentType.REQUEST_OPTIMIZATION: [
                r'\b(optimizar|optimize|mejorar|improve)\b',
                r'\b(eficiencia|efficiency|productividad|productivity)\b',
                r'\b(proceso|process|flujo|workflow)\b'
            ],
            IntentType.REQUEST_HELP: [
                r'\b(ayuda|help|soporte|support)\b',
                r'\b(¿cómo|how to|tutorial|guía|guide)\b',
                r'\b(no entiendo|don\'t understand|confused)\b'
            ],
            IntentType.COMPLAINT: [
                r'\b(problema|problem|error|bug|issue)\b',
                r'\b(no funciona|doesn\'t work|broken)\b',
                r'\b(lento|slow|demasiado|too much)\b'
            ],
            IntentType.COMPLIMENT: [
                r'\b(genial|great|excelente|excellent|fantástico|fantastic)\b',
                r'\b(gracias|thank you|thanks|perfecto|perfect)\b',
                r'\b(me gusta|like|love|amazing|increíble)\b'
            ]
        }
        
        self.entity_patterns = {
            'team_size': r'\b(\d+)\s*(personas|people|miembros|members)\b',
            'time_period': r'\b(última semana|last week|este mes|this month|último mes|last month)\b',
            'tool_name': r'\b(clickup|jira|asana|trello|slack|teams)\b',
            'metric_name': r'\b(eficiencia|efficiency|productividad|productivity|satisfacción|satisfaction)\b'
        }
    
    def process_input(self, user_input: str) -> Dict:
        """Procesar entrada del usuario y extraer intención y entidades."""
        try:
            user_input_lower = user_input.lower()
            
            # Detectar intención
            intent = self._detect_intent(user_input_lower)
            
            # Extraer entidades
            entities = self._extract_entities(user_input_lower)
            
            # Analizar sentimiento
            sentiment = self._analyze_sentiment(user_input)
            
            # Calcular confianza
            confidence = self._calculate_confidence(intent, entities, sentiment)
            
            return {
                'intent': intent,
                'entities': entities,
                'sentiment': sentiment,
                'confidence': confidence,
                'processed_input': user_input_lower
            }
            
        except Exception as e:
            logger.error(f"Error procesando entrada: {str(e)}")
            return {
                'intent': IntentType.UNKNOWN,
                'entities': {},
                'sentiment': 'neutral',
                'confidence': 0.0,
                'error': str(e)
            }
    
    def _detect_intent(self, text: str) -> IntentType:
        """Detectar intención del usuario."""
        intent_scores = {}
        
        for intent_type, patterns in self.intent_patterns.items():
            score = 0
            for pattern in patterns:
                matches = re.findall(pattern, text, re.IGNORECASE)
                score += len(matches)
            intent_scores[intent_type] = score
        
        # Retornar intención con mayor score
        if intent_scores:
            best_intent = max(intent_scores, key=intent_scores.get)
            if intent_scores[best_intent] > 0:
                return best_intent
        
        return IntentType.UNKNOWN
    
    def _extract_entities(self, text: str) -> Dict[str, Any]:
        """Extraer entidades del texto."""
        entities = {}
        
        for entity_type, pattern in self.entity_patterns.items():
            matches = re.findall(pattern, text, re.IGNORECASE)
            if matches:
                entities[entity_type] = matches[0] if isinstance(matches[0], str) else matches[0][0]
        
        return entities
    
    def _analyze_sentiment(self, text: str) -> str:
        """Análisis básico de sentimiento."""
        positive_words = ['bueno', 'good', 'excelente', 'excellent', 'genial', 'great', 'perfecto', 'perfect']
        negative_words = ['malo', 'bad', 'terrible', 'horrible', 'problema', 'problem', 'error']
        
        text_lower = text.lower()
        positive_count = sum(1 for word in positive_words if word in text_lower)
        negative_count = sum(1 for word in negative_words if word in text_lower)
        
        if positive_count > negative_count:
            return 'positive'
        elif negative_count > positive_count:
            return 'negative'
        else:
            return 'neutral'
    
    def _calculate_confidence(self, intent: IntentType, entities: Dict, sentiment: str) -> float:
        """Calcular confianza en el procesamiento."""
        confidence = 0.5  # Base confidence
        
        # Aumentar confianza si se detectó intención
        if intent != IntentType.UNKNOWN:
            confidence += 0.3
        
        # Aumentar confianza si se extrajeron entidades
        if entities:
            confidence += 0.2
        
        return min(confidence, 1.0)

class ResponseGenerator:
    """Generador de respuestas conversacionales."""
    
    def __init__(self):
        self.response_templates = {
            IntentType.GREETING: [
                "¡Hola! Soy ClickUp Brain AI, tu asistente inteligente. ¿En qué puedo ayudarte hoy?",
                "¡Buenos días! Estoy aquí para ayudarte con el análisis de tu equipo. ¿Qué te gustaría saber?",
                "¡Hola! Soy tu asistente de IA para optimización de equipos. ¿Cómo puedo asistirte?"
            ],
            IntentType.QUESTION: [
                "Excelente pregunta. Déjame analizar eso para ti...",
                "Te ayudo con esa consulta. Permíteme procesar la información...",
                "Buena pregunta. Voy a investigar eso en nuestros datos..."
            ],
            IntentType.REQUEST_ANALYSIS: [
                "Perfecto, voy a realizar un análisis completo de tu equipo...",
                "Excelente, iniciando análisis de eficiencia y productividad...",
                "Analizando datos del equipo para generar insights valiosos..."
            ],
            IntentType.REQUEST_REPORT: [
                "Generando reporte detallado con las métricas más importantes...",
                "Creando un informe completo con análisis y recomendaciones...",
                "Preparando reporte personalizado con insights clave..."
            ],
            IntentType.REQUEST_OPTIMIZATION: [
                "Iniciando proceso de optimización para mejorar la eficiencia...",
                "Analizando oportunidades de mejora en los procesos del equipo...",
                "Optimizando workflows para maximizar la productividad..."
            ],
            IntentType.REQUEST_HELP: [
                "¡Por supuesto! Te ayudo con eso. ¿Qué específicamente necesitas?",
                "Estoy aquí para ayudarte. ¿En qué área necesitas asistencia?",
                "Con gusto te ayudo. ¿Podrías ser más específico sobre lo que necesitas?"
            ],
            IntentType.COMPLAINT: [
                "Entiendo tu preocupación. Vamos a resolver este problema juntos.",
                "Lamento escuchar que hay un problema. Permíteme investigar...",
                "Gracias por reportar esto. Voy a analizar la situación..."
            ],
            IntentType.COMPLIMENT: [
                "¡Gracias! Me alegra saber que te está siendo útil.",
                "¡Excelente! Me complace poder ayudarte de manera efectiva.",
                "¡Muchas gracias! Es un placer trabajar contigo."
            ],
            IntentType.UNKNOWN: [
                "No estoy seguro de entender completamente. ¿Podrías reformular tu pregunta?",
                "Me gustaría ayudarte mejor. ¿Podrías ser más específico?",
                "No estoy seguro de lo que necesitas. ¿Te gustaría que te ayude con algo específico?"
            ]
        }
        
        self.follow_up_questions = {
            IntentType.REQUEST_ANALYSIS: [
                "¿Te gustaría que me enfoque en algún aspecto específico del análisis?",
                "¿Hay algún período de tiempo particular que te interese?",
                "¿Quieres que incluya recomendaciones de optimización?"
            ],
            IntentType.REQUEST_REPORT: [
                "¿Qué tipo de métricas te interesan más?",
                "¿Prefieres un reporte ejecutivo o uno más detallado?",
                "¿Hay algún formato específico que prefieras?"
            ],
            IntentType.REQUEST_OPTIMIZATION: [
                "¿En qué área específica te gustaría optimizar?",
                "¿Hay algún proceso particular que te preocupa?",
                "¿Quieres que me enfoque en eficiencia, colaboración o ambos?"
            ]
        }
    
    def generate_response(self, context: ConversationContext, analysis_result: Dict = None) -> str:
        """Generar respuesta conversacional."""
        try:
            # Respuesta base basada en intención
            base_responses = self.response_templates.get(context.current_intent, [])
            base_response = random.choice(base_responses) if base_responses else "Entiendo. ¿En qué más puedo ayudarte?"
            
            # Agregar información específica si hay análisis
            if analysis_result and 'error' not in analysis_result:
                specific_info = self._generate_specific_response(context, analysis_result)
                if specific_info:
                    base_response += f"\n\n{specific_info}"
            
            # Agregar pregunta de seguimiento
            follow_up = self._generate_follow_up(context)
            if follow_up:
                base_response += f"\n\n{follow_up}"
            
            return base_response
            
        except Exception as e:
            logger.error(f"Error generando respuesta: {str(e)}")
            return "Disculpa, hubo un problema procesando tu solicitud. ¿Podrías intentar de nuevo?"
    
    def _generate_specific_response(self, context: ConversationContext, analysis_result: Dict) -> str:
        """Generar respuesta específica basada en análisis."""
        if context.current_intent == IntentType.REQUEST_ANALYSIS:
            if 'efficiency_score' in analysis_result:
                score = analysis_result['efficiency_score']
                return f"El análisis muestra una eficiencia del equipo del {score:.1f}%. "
        
        elif context.current_intent == IntentType.REQUEST_REPORT:
            if 'total_insights' in analysis_result:
                insights = analysis_result['total_insights']
                return f"He generado {insights} insights clave en el reporte. "
        
        elif context.current_intent == IntentType.REQUEST_OPTIMIZATION:
            if 'optimization_opportunities' in analysis_result:
                opportunities = analysis_result['optimization_opportunities']
                return f"He identificado {opportunities} oportunidades de optimización. "
        
        return ""
    
    def _generate_follow_up(self, context: ConversationContext) -> str:
        """Generar pregunta de seguimiento."""
        follow_ups = self.follow_up_questions.get(context.current_intent, [])
        if follow_ups:
            return random.choice(follow_ups)
        return ""

class ConversationMemory:
    """Memoria conversacional para mantener contexto."""
    
    def __init__(self):
        self.conversation_history = {}
        self.user_preferences = {}
        self.learned_patterns = {}
    
    def store_conversation(self, user_id: str, context: ConversationContext, response: str):
        """Almacenar conversación en memoria."""
        if user_id not in self.conversation_history:
            self.conversation_history[user_id] = []
        
        conversation_entry = {
            'timestamp': context.timestamp.isoformat(),
            'user_input': context.conversation_history[-1] if context.conversation_history else "",
            'intent': context.current_intent.value,
            'entities': context.entities,
            'sentiment': context.sentiment,
            'confidence': context.confidence,
            'response': response
        }
        
        self.conversation_history[user_id].append(conversation_entry)
        
        # Mantener solo las últimas 50 conversaciones por usuario
        if len(self.conversation_history[user_id]) > 50:
            self.conversation_history[user_id] = self.conversation_history[user_id][-50:]
    
    def get_user_context(self, user_id: str) -> Dict:
        """Obtener contexto del usuario."""
        if user_id not in self.conversation_history:
            return {'conversation_count': 0, 'last_intent': None, 'preferences': {}}
        
        history = self.conversation_history[user_id]
        last_conversation = history[-1] if history else None
        
        return {
            'conversation_count': len(history),
            'last_intent': last_conversation['intent'] if last_conversation else None,
            'preferences': self.user_preferences.get(user_id, {}),
            'recent_topics': [conv['intent'] for conv in history[-5:]]
        }
    
    def learn_from_conversation(self, user_id: str, context: ConversationContext, response: str):
        """Aprender de la conversación para mejorar futuras interacciones."""
        # Aprender patrones de preferencias
        if context.current_intent in [IntentType.REQUEST_ANALYSIS, IntentType.REQUEST_REPORT]:
            if user_id not in self.user_preferences:
                self.user_preferences[user_id] = {}
            
            # Aprender preferencias de entidades
            for entity_type, entity_value in context.entities.items():
                if entity_type not in self.user_preferences[user_id]:
                    self.user_preferences[user_id][entity_type] = []
                
                if entity_value not in self.user_preferences[user_id][entity_type]:
                    self.user_preferences[user_id][entity_type].append(entity_value)

class ClickUpBrainConversationalAI:
    """Sistema principal de IA conversacional."""
    
    def __init__(self):
        self.nlp_processor = NaturalLanguageProcessor()
        self.response_generator = ResponseGenerator()
        self.conversation_memory = ConversationMemory()
        self.current_state = ConversationState.LISTENING
        self.active_sessions = {}
    
    def start_conversation(self, user_id: str, session_id: str = None) -> str:
        """Iniciar nueva conversación."""
        if not session_id:
            session_id = f"session_{int(time.time())}"
        
        # Crear contexto de conversación
        context = ConversationContext(
            user_id=user_id,
            session_id=session_id,
            conversation_history=[],
            current_intent=IntentType.GREETING,
            entities={},
            sentiment='neutral',
            confidence=1.0,
            timestamp=datetime.now()
        )
        
        # Almacenar sesión activa
        self.active_sessions[session_id] = context
        
        # Generar saludo
        greeting = self.response_generator.generate_response(context)
        
        # Cambiar estado
        self.current_state = ConversationState.LISTENING
        
        return greeting
    
    def process_user_input(self, user_input: str, user_id: str, session_id: str = None) -> str:
        """Procesar entrada del usuario y generar respuesta."""
        try:
            # Obtener contexto de sesión
            if session_id and session_id in self.active_sessions:
                context = self.active_sessions[session_id]
            else:
                # Crear nueva sesión si no existe
                session_id = f"session_{int(time.time())}"
                context = ConversationContext(
                    user_id=user_id,
                    session_id=session_id,
                    conversation_history=[],
                    current_intent=IntentType.UNKNOWN,
                    entities={},
                    sentiment='neutral',
                    confidence=0.0,
                    timestamp=datetime.now()
                )
                self.active_sessions[session_id] = context
            
            # Agregar entrada a historial
            context.conversation_history.append({
                'timestamp': datetime.now().isoformat(),
                'user_input': user_input,
                'type': 'user'
            })
            
            # Cambiar a estado de procesamiento
            self.current_state = ConversationState.PROCESSING
            
            # Procesar entrada con NLP
            nlp_result = self.nlp_processor.process_input(user_input)
            
            # Actualizar contexto
            context.current_intent = nlp_result['intent']
            context.entities = nlp_result['entities']
            context.sentiment = nlp_result['sentiment']
            context.confidence = nlp_result['confidence']
            context.timestamp = datetime.now()
            
            # Realizar análisis si es necesario
            analysis_result = None
            if context.current_intent in [IntentType.REQUEST_ANALYSIS, IntentType.REQUEST_REPORT, IntentType.REQUEST_OPTIMIZATION]:
                analysis_result = self._perform_requested_analysis(context)
            
            # Generar respuesta
            response = self.response_generator.generate_response(context, analysis_result)
            
            # Almacenar en memoria
            self.conversation_memory.store_conversation(user_id, context, response)
            self.conversation_memory.learn_from_conversation(user_id, context, response)
            
            # Agregar respuesta a historial
            context.conversation_history.append({
                'timestamp': datetime.now().isoformat(),
                'response': response,
                'type': 'assistant'
            })
            
            # Cambiar a estado de respuesta
            self.current_state = ConversationState.RESPONDING
            
            return response
            
        except Exception as e:
            logger.error(f"Error procesando entrada del usuario: {str(e)}")
            self.current_state = ConversationState.ERROR
            return "Disculpa, hubo un problema procesando tu solicitud. ¿Podrías intentar de nuevo?"
    
    def _perform_requested_analysis(self, context: ConversationContext) -> Dict:
        """Realizar análisis solicitado por el usuario."""
        try:
            # Simular análisis basado en la intención
            if context.current_intent == IntentType.REQUEST_ANALYSIS:
                return {
                    'efficiency_score': 78.5,
                    'productivity_trend': 'increasing',
                    'team_satisfaction': 0.82,
                    'collaboration_score': 0.75,
                    'recommendations': [
                        'Mejorar comunicación entre equipos',
                        'Optimizar procesos de revisión',
                        'Implementar herramientas de colaboración'
                    ]
                }
            
            elif context.current_intent == IntentType.REQUEST_REPORT:
                return {
                    'total_insights': 12,
                    'key_metrics': {
                        'efficiency': 78.5,
                        'productivity': 82.3,
                        'satisfaction': 0.82
                    },
                    'trends': ['positive', 'stable', 'improving'],
                    'recommendations_count': 5
                }
            
            elif context.current_intent == IntentType.REQUEST_OPTIMIZATION:
                return {
                    'optimization_opportunities': 7,
                    'potential_improvement': 15.2,
                    'priority_areas': [
                        'Comunicación',
                        'Procesos',
                        'Herramientas'
                    ],
                    'estimated_impact': 'high'
                }
            
            return {}
            
        except Exception as e:
            logger.error(f"Error realizando análisis: {str(e)}")
            return {'error': str(e)}
    
    def get_conversation_history(self, user_id: str, limit: int = 10) -> List[Dict]:
        """Obtener historial de conversación del usuario."""
        if user_id not in self.conversation_memory.conversation_history:
            return []
        
        history = self.conversation_memory.conversation_history[user_id]
        return history[-limit:] if limit else history
    
    def get_user_insights(self, user_id: str) -> Dict:
        """Obtener insights del usuario basados en conversaciones."""
        user_context = self.conversation_memory.get_user_context(user_id)
        
        return {
            'user_id': user_id,
            'conversation_count': user_context['conversation_count'],
            'preferred_intents': user_context['recent_topics'],
            'preferences': user_context['preferences'],
            'last_interaction': user_context['last_intent'],
            'engagement_level': self._calculate_engagement_level(user_context)
        }
    
    def _calculate_engagement_level(self, user_context: Dict) -> str:
        """Calcular nivel de engagement del usuario."""
        conversation_count = user_context['conversation_count']
        
        if conversation_count > 20:
            return 'high'
        elif conversation_count > 10:
            return 'medium'
        elif conversation_count > 0:
            return 'low'
        else:
            return 'new'
    
    def generate_conversation_report(self, user_id: str) -> str:
        """Generar reporte de conversaciones del usuario."""
        try:
            user_insights = self.get_user_insights(user_id)
            conversation_history = self.get_conversation_history(user_id, 20)
            
            report = f"""# 🤖 ClickUp Brain - Reporte de Conversaciones

## 📊 Resumen del Usuario

**Usuario:** {user_id}
**Total de Conversaciones:** {user_insights['conversation_count']}
**Nivel de Engagement:** {user_insights['engagement_level'].title()}
**Última Interacción:** {user_insights['last_interaction'] or 'N/A'}

## 🎯 Preferencias del Usuario

### Intenciones Más Frecuentes:
"""
            
            if user_insights['preferred_intents']:
                intent_counts = {}
                for intent in user_insights['preferred_intents']:
                    intent_counts[intent] = intent_counts.get(intent, 0) + 1
                
                for intent, count in sorted(intent_counts.items(), key=lambda x: x[1], reverse=True):
                    report += f"- **{intent}**: {count} veces\n"
            else:
                report += "- No hay datos suficientes\n"
            
            report += f"""
### Preferencias Identificadas:
"""
            
            if user_insights['preferences']:
                for pref_type, values in user_insights['preferences'].items():
                    report += f"- **{pref_type}**: {', '.join(values)}\n"
            else:
                report += "- No hay preferencias identificadas aún\n"
            
            report += f"""
## 💬 Historial de Conversaciones Recientes

"""
            
            for i, conv in enumerate(conversation_history[-10:], 1):
                report += f"""
### Conversación #{i}
**Fecha:** {conv['timestamp']}
**Intención:** {conv['intent']}
**Sentimiento:** {conv['sentiment']}
**Confianza:** {conv['confidence']:.2f}
**Entrada del Usuario:** "{conv['user_input']}"
**Respuesta:** "{conv['response'][:100]}..."
"""
            
            report += f"""
## 🎯 Recomendaciones

### Para Mejorar la Experiencia:
"""
            
            if user_insights['engagement_level'] == 'low':
                report += "- Proporcionar más ejemplos de uso\n"
                report += "- Ofrecer tutoriales interactivos\n"
                report += "- Enviar recordatorios de funcionalidades\n"
            elif user_insights['engagement_level'] == 'medium':
                report += "- Personalizar respuestas basadas en preferencias\n"
                report += "- Ofrecer análisis más profundos\n"
                report += "- Sugerir nuevas funcionalidades\n"
            else:
                report += "- Proporcionar análisis avanzados\n"
                report += "- Ofrecer integraciones personalizadas\n"
                report += "- Implementar automatizaciones específicas\n"
            
            report += f"""
---
*Reporte generado por ClickUp Brain Conversational AI*
*Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*
"""
            
            return report
            
        except Exception as e:
            logger.error(f"Error generando reporte de conversaciones: {str(e)}")
            return f"Error generando reporte: {str(e)}"

def main():
    """Función principal para demostrar el sistema conversacional."""
    print("🤖 ClickUp Brain - Sistema de IA Conversacional Avanzada")
    print("=" * 60)
    
    # Inicializar sistema conversacional
    conversational_ai = ClickUpBrainConversationalAI()
    
    # Simular conversación
    user_id = "demo_user_001"
    
    print("🤖 Iniciando conversación...")
    greeting = conversational_ai.start_conversation(user_id)
    print(f"AI: {greeting}")
    
    # Simular interacciones del usuario
    test_inputs = [
        "Hola, ¿cómo estás?",
        "¿Puedes analizar la eficiencia de mi equipo?",
        "Necesito un reporte de productividad",
        "¿Cómo puedo optimizar los procesos?",
        "Gracias, eso fue muy útil"
    ]
    
    print("\n💬 Simulando conversación...")
    for i, user_input in enumerate(test_inputs, 1):
        print(f"\nUsuario: {user_input}")
        
        response = conversational_ai.process_user_input(user_input, user_id)
        print(f"AI: {response}")
        
        time.sleep(1)  # Pausa para simular tiempo de procesamiento
    
    # Generar reporte de conversación
    print("\n📄 Generando reporte de conversación...")
    report = conversational_ai.generate_conversation_report(user_id)
    
    # Guardar reporte
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    report_filename = f"conversational_ai_report_{timestamp}.md"
    with open(report_filename, 'w', encoding='utf-8') as f:
        f.write(report)
    
    print(f"📄 Reporte de conversación guardado: {report_filename}")
    
    # Mostrar insights del usuario
    user_insights = conversational_ai.get_user_insights(user_id)
    print(f"\n📊 Insights del Usuario:")
    print(f"   • Total de conversaciones: {user_insights['conversation_count']}")
    print(f"   • Nivel de engagement: {user_insights['engagement_level']}")
    print(f"   • Última interacción: {user_insights['last_interaction']}")
    
    print("\n🎉 Sistema de IA Conversacional funcionando correctamente!")
    print("🤖 Listo para interacciones en lenguaje natural")
    
    return True

if __name__ == "__main__":
    main()










