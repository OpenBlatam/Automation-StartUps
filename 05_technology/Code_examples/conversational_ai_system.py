#!/usr/bin/env python3
"""
Sistema de Inteligencia Artificial Conversacional Avanzada
"""

import os
import json
import sqlite3
import random
from datetime import datetime
import re

class ConversationalAISystem:
    def __init__(self, base_path="/Users/adan/frontier"):
        self.base_path = base_path
        self.conversational_db = os.path.join(base_path, "conversational_ai.db")
        self.conversation_context = {}
        self.user_profiles = {}
        self.init_conversational_database()
        self.load_conversation_templates()
    
    def init_conversational_database(self):
        """Inicializar base de datos conversacional"""
        conn = sqlite3.connect(self.conversational_db)
        cursor = conn.cursor()
        
        # Tabla de conversaciones
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS conversations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id TEXT,
                session_id TEXT,
                message TEXT,
                response TEXT,
                intent TEXT,
                entities TEXT,
                sentiment TEXT,
                confidence REAL,
                timestamp TEXT
            )
        ''')
        
        # Tabla de intenciones
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS intents (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                intent_name TEXT,
                patterns TEXT,
                responses TEXT,
                context_required TEXT,
                confidence_threshold REAL,
                created_at TEXT
            )
        ''')
        
        # Tabla de entidades
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS entities (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                entity_name TEXT,
                entity_type TEXT,
                values TEXT,
                synonyms TEXT,
                created_at TEXT
            )
        ''')
        
        # Tabla de perfiles de usuario
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS user_profiles (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id TEXT,
                preferences TEXT,
                conversation_history TEXT,
                personality_traits TEXT,
                created_at TEXT,
                updated_at TEXT
            )
        ''')
        
        # Tabla de conocimiento
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS knowledge_base (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                topic TEXT,
                question TEXT,
                answer TEXT,
                confidence REAL,
                source TEXT,
                created_at TEXT
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def load_conversation_templates(self):
        """Cargar plantillas de conversación"""
        # Intenciones predefinidas
        self.intents = {
            'greeting': {
                'patterns': ['hola', 'buenos días', 'buenas tardes', 'buenas noches', 'saludos'],
                'responses': [
                    '¡Hola! ¿En qué puedo ayudarte hoy?',
                    '¡Buenos días! Estoy aquí para asistirte.',
                    '¡Hola! ¿Cómo puedo ayudarte con tu trabajo?'
                ],
                'context_required': False
            },
            'help': {
                'patterns': ['ayuda', 'help', 'asistencia', 'soporte', 'cómo'],
                'responses': [
                    'Por supuesto, estoy aquí para ayudarte. ¿Qué necesitas?',
                    'Te puedo ayudar con búsquedas, organización, análisis y más.',
                    '¿En qué área específica necesitas asistencia?'
                ],
                'context_required': False
            },
            'search': {
                'patterns': ['buscar', 'encontrar', 'localizar', 'search', 'dónde está'],
                'responses': [
                    'Te ayudo a buscar información. ¿Qué estás buscando?',
                    'Puedo buscar documentos, datos o información específica.',
                    '¿Qué término o tema quieres que busque?'
                ],
                'context_required': False
            },
            'organize': {
                'patterns': ['organizar', 'clasificar', 'ordenar', 'estructurar'],
                'responses': [
                    'Te ayudo a organizar tus archivos y documentos.',
                    'Puedo clasificar automáticamente tu información.',
                    '¿Qué tipo de organización necesitas?'
                ],
                'context_required': False
            },
            'analyze': {
                'patterns': ['analizar', 'examinar', 'evaluar', 'revisar', 'estudiar'],
                'responses': [
                    'Te ayudo a analizar datos e información.',
                    'Puedo examinar documentos y generar insights.',
                    '¿Qué información quieres que analice?'
                ],
                'context_required': False
            },
            'report': {
                'patterns': ['reporte', 'informe', 'resumen', 'estadísticas'],
                'responses': [
                    'Te genero un reporte personalizado.',
                    'Puedo crear informes detallados de tu información.',
                    '¿Qué tipo de reporte necesitas?'
                ],
                'context_required': False
            },
            'goodbye': {
                'patterns': ['adiós', 'hasta luego', 'nos vemos', 'chao', 'bye'],
                'responses': [
                    '¡Hasta luego! Fue un placer ayudarte.',
                    '¡Adiós! Vuelve cuando necesites asistencia.',
                    '¡Nos vemos pronto! Que tengas un buen día.'
                ],
                'context_required': False
            }
        }
        
        # Entidades predefinidas
        self.entities = {
            'document_type': ['documento', 'archivo', 'presentación', 'hoja de cálculo', 'imagen'],
            'business_area': ['marketing', 'finanzas', 'recursos humanos', 'operaciones', 'tecnología'],
            'time_period': ['hoy', 'ayer', 'esta semana', 'este mes', 'este año'],
            'priority': ['urgente', 'importante', 'normal', 'baja prioridad']
        }
    
    def process_user_message(self, user_id, message, session_id=None):
        """Procesar mensaje del usuario"""
        if not session_id:
            session_id = f"session_{user_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        # Análisis del mensaje
        intent = self._classify_intent(message)
        entities = self._extract_entities(message)
        sentiment = self._analyze_sentiment(message)
        
        # Generar respuesta
        response = self._generate_response(intent, entities, sentiment, user_id, message)
        
        # Guardar conversación
        self._save_conversation(user_id, session_id, message, response, intent, entities, sentiment)
        
        # Actualizar contexto
        self._update_conversation_context(user_id, session_id, intent, entities)
        
        return {
            'response': response,
            'intent': intent,
            'entities': entities,
            'sentiment': sentiment,
            'session_id': session_id
        }
    
    def _classify_intent(self, message):
        """Clasificar intención del mensaje"""
        message_lower = message.lower()
        best_intent = 'unknown'
        best_confidence = 0
        
        for intent_name, intent_data in self.intents.items():
            for pattern in intent_data['patterns']:
                if pattern in message_lower:
                    confidence = len(pattern) / len(message)
                    if confidence > best_confidence:
                        best_confidence = confidence
                        best_intent = intent_name
        
        return {
            'intent': best_intent,
            'confidence': best_confidence
        }
    
    def _extract_entities(self, message):
        """Extraer entidades del mensaje"""
        entities = []
        message_lower = message.lower()
        
        for entity_type, values in self.entities.items():
            for value in values:
                if value in message_lower:
                    entities.append({
                        'type': entity_type,
                        'value': value,
                        'confidence': 0.8
                    })
        
        return entities
    
    def _analyze_sentiment(self, message):
        """Analizar sentimiento del mensaje"""
        positive_words = ['bueno', 'excelente', 'genial', 'perfecto', 'gracias', 'ayuda']
        negative_words = ['malo', 'problema', 'error', 'difícil', 'confuso']
        
        positive_count = sum(1 for word in positive_words if word in message.lower())
        negative_count = sum(1 for word in negative_words if word in message.lower())
        
        if positive_count > negative_count:
            return 'positive'
        elif negative_count > positive_count:
            return 'negative'
        else:
            return 'neutral'
    
    def _generate_response(self, intent, entities, sentiment, user_id, original_message):
        """Generar respuesta contextual"""
        intent_name = intent['intent']
        confidence = intent['confidence']
        
        # Respuesta basada en intención
        if intent_name in self.intents and confidence > 0.3:
            responses = self.intents[intent_name]['responses']
            base_response = random.choice(responses)
        else:
            base_response = "Entiendo. ¿Podrías ser más específico sobre lo que necesitas?"
        
        # Personalizar respuesta
        personalized_response = self._personalize_response(base_response, user_id, entities, sentiment)
        
        # Agregar contexto si es necesario
        contextual_response = self._add_context(personalized_response, user_id, intent_name)
        
        return contextual_response
    
    def _personalize_response(self, response, user_id, entities, sentiment):
        """Personalizar respuesta basada en perfil del usuario"""
        # Obtener perfil del usuario
        user_profile = self._get_user_profile(user_id)
        
        # Ajustar tono basado en sentimiento
        if sentiment == 'positive':
            response = f"¡Excelente! {response}"
        elif sentiment == 'negative':
            response = f"Entiendo tu preocupación. {response}"
        
        # Agregar información específica basada en entidades
        if entities:
            entity_info = []
            for entity in entities:
                if entity['type'] == 'business_area':
                    entity_info.append(f"en el área de {entity['value']}")
                elif entity['type'] == 'document_type':
                    entity_info.append(f"para {entity['value']}s")
            
            if entity_info:
                response += f" Específicamente {', '.join(entity_info)}."
        
        return response
    
    def _add_context(self, response, user_id, intent_name):
        """Agregar contexto a la respuesta"""
        # Obtener contexto de conversación
        context = self.conversation_context.get(user_id, {})
        
        # Agregar sugerencias basadas en contexto
        if intent_name == 'search' and 'previous_searches' in context:
            response += " Basándome en tus búsquedas anteriores, te sugiero revisar los documentos de marketing."
        elif intent_name == 'organize' and 'recent_activity' in context:
            response += " He notado que tienes muchos documentos nuevos. ¿Te ayudo a organizarlos?"
        
        return response
    
    def _get_user_profile(self, user_id):
        """Obtener perfil del usuario"""
        if user_id not in self.user_profiles:
            self.user_profiles[user_id] = {
                'preferences': {},
                'conversation_history': [],
                'personality_traits': {}
            }
        
        return self.user_profiles[user_id]
    
    def _update_conversation_context(self, user_id, session_id, intent, entities):
        """Actualizar contexto de conversación"""
        if user_id not in self.conversation_context:
            self.conversation_context[user_id] = {}
        
        context = self.conversation_context[user_id]
        
        # Actualizar intención actual
        context['current_intent'] = intent['intent']
        
        # Actualizar entidades encontradas
        if 'entities' not in context:
            context['entities'] = []
        context['entities'].extend(entities)
        
        # Mantener historial de intenciones
        if 'intent_history' not in context:
            context['intent_history'] = []
        context['intent_history'].append(intent['intent'])
        
        # Limitar historial
        if len(context['intent_history']) > 10:
            context['intent_history'] = context['intent_history'][-10:]
    
    def _save_conversation(self, user_id, session_id, message, response, intent, entities, sentiment):
        """Guardar conversación en base de datos"""
        conn = sqlite3.connect(self.conversational_db)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO conversations 
            (user_id, session_id, message, response, intent, entities, 
             sentiment, confidence, timestamp)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (user_id, session_id, message, response, intent['intent'], 
              json.dumps(entities), sentiment, intent['confidence'], 
              datetime.now().isoformat()))
        
        conn.commit()
        conn.close()
    
    def add_knowledge(self, topic, question, answer, source="user"):
        """Agregar conocimiento a la base"""
        conn = sqlite3.connect(self.conversational_db)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO knowledge_base 
            (topic, question, answer, confidence, source, created_at)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (topic, question, answer, 0.8, source, datetime.now().isoformat()))
        
        conn.commit()
        conn.close()
    
    def search_knowledge(self, query):
        """Buscar en base de conocimiento"""
        conn = sqlite3.connect(self.conversational_db)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT topic, question, answer, confidence FROM knowledge_base
            WHERE question LIKE ? OR answer LIKE ? OR topic LIKE ?
            ORDER BY confidence DESC
        ''', (f'%{query}%', f'%{query}%', f'%{query}%'))
        
        results = cursor.fetchall()
        conn.close()
        
        return [{
            'topic': row[0],
            'question': row[1],
            'answer': row[2],
            'confidence': row[3]
        } for row in results]
    
    def get_conversation_analytics(self, user_id=None):
        """Obtener analytics de conversación"""
        conn = sqlite3.connect(self.conversational_db)
        cursor = conn.cursor()
        
        # Consulta base
        base_query = 'SELECT intent, sentiment, confidence, timestamp FROM conversations'
        params = []
        
        if user_id:
            base_query += ' WHERE user_id = ?'
            params.append(user_id)
        
        cursor.execute(base_query, params)
        conversations = cursor.fetchall()
        
        # Análisis de intenciones
        intent_counts = {}
        sentiment_counts = {}
        confidence_scores = []
        
        for intent, sentiment, confidence, timestamp in conversations:
            intent_counts[intent] = intent_counts.get(intent, 0) + 1
            sentiment_counts[sentiment] = sentiment_counts.get(sentiment, 0) + 1
            confidence_scores.append(confidence)
        
        # Calcular estadísticas
        avg_confidence = sum(confidence_scores) / len(confidence_scores) if confidence_scores else 0
        
        conn.close()
        
        return {
            'total_conversations': len(conversations),
            'intent_distribution': intent_counts,
            'sentiment_distribution': sentiment_counts,
            'average_confidence': avg_confidence,
            'most_common_intent': max(intent_counts.items(), key=lambda x: x[1])[0] if intent_counts else None,
            'most_common_sentiment': max(sentiment_counts.items(), key=lambda x: x[1])[0] if sentiment_counts else None
        }

def main():
    conversational_ai = ConversationalAISystem()
    
    print("🤖 Sistema de IA Conversacional Avanzada")
    print("=" * 50)
    print("1. Chat con IA")
    print("2. Agregar conocimiento")
    print("3. Buscar en base de conocimiento")
    print("4. Ver analytics de conversación")
    print("5. Salir")
    
    while True:
        choice = input("\nSeleccione una opción (1-5): ").strip()
        
        if choice == '1':
            user_id = input("ID de usuario: ").strip()
            if not user_id:
                user_id = "user_001"
            
            print(f"\n🤖 Chat con IA (escriba 'salir' para terminar)")
            session_id = None
            
            while True:
                message = input(f"\n👤 {user_id}: ").strip()
                if message.lower() in ['salir', 'exit', 'quit', 'adiós']:
                    print("🤖 IA: ¡Hasta luego! Fue un placer conversar contigo.")
                    break
                
                if message:
                    result = conversational_ai.process_user_message(user_id, message, session_id)
                    session_id = result['session_id']
                    
                    print(f"🤖 IA: {result['response']}")
                    print(f"   [Intención: {result['intent']['intent']} ({result['intent']['confidence']:.2f})]")
                    if result['entities']:
                        print(f"   [Entidades: {', '.join([e['value'] for e in result['entities']])}]")
        
        elif choice == '2':
            topic = input("Tema: ").strip()
            question = input("Pregunta: ").strip()
            answer = input("Respuesta: ").strip()
            source = input("Fuente (default: user): ").strip() or "user"
            
            if topic and question and answer:
                conversational_ai.add_knowledge(topic, question, answer, source)
                print("✅ Conocimiento agregado a la base")
            else:
                print("❌ Tema, pregunta y respuesta requeridos")
        
        elif choice == '3':
            query = input("Consulta de búsqueda: ").strip()
            if query:
                results = conversational_ai.search_knowledge(query)
                if results:
                    print(f"🔍 Resultados encontrados: {len(results)}")
                    for i, result in enumerate(results[:3], 1):  # Mostrar solo los primeros 3
                        print(f"  {i}. {result['question']}")
                        print(f"     Respuesta: {result['answer']}")
                        print(f"     Confianza: {result['confidence']:.2f}")
                else:
                    print("❌ No se encontraron resultados")
            else:
                print("❌ Consulta requerida")
        
        elif choice == '4':
            user_id = input("ID de usuario (opcional): ").strip() or None
            analytics = conversational_ai.get_conversation_analytics(user_id)
            
            print(f"\n📊 Analytics de Conversación:")
            print(f"  💬 Total conversaciones: {analytics['total_conversations']}")
            print(f"  📊 Confianza promedio: {analytics['average_confidence']:.2f}")
            
            if analytics['intent_distribution']:
                print(f"\n🎯 Distribución de intenciones:")
                for intent, count in analytics['intent_distribution'].items():
                    print(f"  • {intent}: {count}")
            
            if analytics['sentiment_distribution']:
                print(f"\n😊 Distribución de sentimientos:")
                for sentiment, count in analytics['sentiment_distribution'].items():
                    print(f"  • {sentiment}: {count}")
            
            if analytics['most_common_intent']:
                print(f"\n🔥 Intención más común: {analytics['most_common_intent']}")
            
            if analytics['most_common_sentiment']:
                print(f"😊 Sentimiento más común: {analytics['most_common_sentiment']}")
        
        elif choice == '5':
            print("👋 ¡Hasta luego!")
            break
        
        else:
            print("❌ Opción no válida")

if __name__ == "__main__":
    main()


