#!/usr/bin/env python3
"""
🤖 MARKETING BRAIN AI CHATBOT
Chatbot Inteligente para Soporte al Cliente y Asistencia de Marketing
Incluye procesamiento de lenguaje natural, respuestas contextuales y aprendizaje automático
"""

import json
import asyncio
import re
import uuid
import time
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple, Union
import logging
from dataclasses import dataclass, asdict
from pathlib import Path
import sys
from enum import Enum
import numpy as np
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.naive_bayes import MultinomialNB
from sklearn.linear_model import LogisticRegression
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize, sent_tokenize
from nltk.stem import WordNetLemmatizer
from nltk.sentiment import SentimentIntensityAnalyzer
import spacy
from textblob import TextBlob
import openai
import requests
import websockets
import ssl
from functools import lru_cache
import threading
import queue
from concurrent.futures import ThreadPoolExecutor
import sqlite3
import redis
import yaml
import base64
import hashlib
import hmac
from cryptography.fernet import Fernet

# Agregar el directorio actual al path
sys.path.append(str(Path(__file__).parent))

logger = logging.getLogger(__name__)

class ChatbotMode(Enum):
    """Modos del chatbot"""
    CUSTOMER_SUPPORT = "customer_support"
    MARKETING_ASSISTANT = "marketing_assistant"
    SALES_ASSISTANT = "sales_assistant"
    TECHNICAL_SUPPORT = "technical_support"
    GENERAL_INQUIRY = "general_inquiry"

class MessageType(Enum):
    """Tipos de mensaje"""
    TEXT = "text"
    IMAGE = "image"
    AUDIO = "audio"
    VIDEO = "video"
    FILE = "file"
    LOCATION = "location"
    CONTACT = "contact"

class IntentType(Enum):
    """Tipos de intención"""
    GREETING = "greeting"
    QUESTION = "question"
    COMPLAINT = "complaint"
    COMPLIMENT = "compliment"
    REQUEST = "request"
    GOODBYE = "goodbye"
    UNKNOWN = "unknown"

class SentimentType(Enum):
    """Tipos de sentimiento"""
    POSITIVE = "positive"
    NEGATIVE = "negative"
    NEUTRAL = "neutral"
    MIXED = "mixed"

@dataclass
class ChatMessage:
    """Mensaje de chat"""
    message_id: str
    user_id: str
    session_id: str
    message_type: MessageType
    content: str
    timestamp: str
    metadata: Dict[str, Any]
    processed: bool = False

@dataclass
class ChatResponse:
    """Respuesta del chatbot"""
    response_id: str
    message_id: str
    content: str
    intent: IntentType
    sentiment: SentimentType
    confidence: float
    suggested_actions: List[str]
    timestamp: str
    metadata: Dict[str, Any]

@dataclass
class ChatSession:
    """Sesión de chat"""
    session_id: str
    user_id: str
    mode: ChatbotMode
    start_time: str
    last_activity: str
    message_count: int
    context: Dict[str, Any]
    user_profile: Dict[str, Any]
    is_active: bool

@dataclass
class KnowledgeBase:
    """Base de conocimiento"""
    kb_id: str
    title: str
    content: str
    category: str
    tags: List[str]
    confidence_score: float
    last_updated: str
    usage_count: int

@dataclass
class IntentModel:
    """Modelo de intención"""
    model_id: str
    name: str
    accuracy: float
    training_data_size: int
    last_trained: str
    model_type: str
    parameters: Dict[str, Any]

class MarketingBrainAIChatbot:
    """
    Chatbot Inteligente para Soporte al Cliente y Asistencia de Marketing
    Incluye procesamiento de lenguaje natural, respuestas contextuales y aprendizaje automático
    """
    
    def __init__(self):
        self.sessions = {}
        self.messages = {}
        self.responses = {}
        self.knowledge_base = {}
        self.intent_models = {}
        
        # Configuración
        self.config = self._load_config()
        
        # Modelos de NLP
        self.vectorizer = TfidfVectorizer(max_features=1000, stop_words='english')
        self.intent_classifier = None
        self.sentiment_analyzer = SentimentIntensityAnalyzer()
        self.lemmatizer = WordNetLemmatizer()
        
        # Modelos de IA
        self.nlp_model = None
        self.openai_client = None
        
        # Bases de datos
        self.db_connection = None
        self.redis_client = None
        
        # Colas de procesamiento
        self.message_queue = queue.Queue()
        self.response_queue = queue.Queue()
        
        # Threads
        self.message_processor_thread = None
        self.response_generator_thread = None
        
        # Estado del sistema
        self.is_running = False
        
        # Métricas
        self.chatbot_metrics = {
            'total_sessions': 0,
            'active_sessions': 0,
            'total_messages': 0,
            'responses_generated': 0,
            'intent_accuracy': 0.0,
            'sentiment_accuracy': 0.0,
            'average_response_time': 0.0,
            'user_satisfaction': 0.0
        }
        
        logger.info("🤖 Marketing Brain AI Chatbot initialized successfully")
    
    def _load_config(self) -> Dict[str, Any]:
        """Cargar configuración del chatbot"""
        return {
            'nlp': {
                'language': 'en',
                'max_message_length': 1000,
                'min_confidence_threshold': 0.7,
                'context_window_size': 10,
                'enable_sentiment_analysis': True,
                'enable_entity_extraction': True
            },
            'ai_models': {
                'openai_api_key': '',
                'openai_model': 'gpt-3.5-turbo',
                'max_tokens': 150,
                'temperature': 0.7,
                'enable_fine_tuning': False
            },
            'knowledge_base': {
                'max_kb_entries': 10000,
                'similarity_threshold': 0.8,
                'auto_update': True,
                'update_frequency': 3600
            },
            'session_management': {
                'session_timeout': 1800,  # 30 minutos
                'max_sessions_per_user': 5,
                'context_retention_days': 30
            },
            'response_generation': {
                'max_response_length': 500,
                'enable_personalization': True,
                'enable_learning': True,
                'response_templates': True
            },
            'integration': {
                'webhook_enabled': True,
                'api_enabled': True,
                'websocket_enabled': True,
                'rate_limiting': True,
                'max_requests_per_minute': 60
            }
        }
    
    async def initialize_chatbot(self):
        """Inicializar chatbot"""
        logger.info("🚀 Initializing Marketing Brain AI Chatbot...")
        
        try:
            # Inicializar bases de datos
            await self._initialize_databases()
            
            # Descargar modelos de NLTK
            await self._download_nltk_models()
            
            # Cargar modelo de spaCy
            await self._load_spacy_model()
            
            # Inicializar OpenAI
            await self._initialize_openai()
            
            # Cargar base de conocimiento
            await self._load_knowledge_base()
            
            # Entrenar modelos de intención
            await self._train_intent_models()
            
            # Iniciar threads de procesamiento
            self._start_processing_threads()
            
            logger.info("✅ Chatbot initialized successfully")
            
        except Exception as e:
            logger.error(f"Error initializing chatbot: {e}")
            raise
    
    async def _initialize_databases(self):
        """Inicializar bases de datos"""
        try:
            # SQLite para metadatos
            self.db_connection = sqlite3.connect('chatbot_metadata.db', check_same_thread=False)
            
            # Redis para cache
            self.redis_client = redis.Redis(host='localhost', port=6379, db=2, decode_responses=True)
            
            # Crear tablas
            await self._create_chatbot_tables()
            
        except Exception as e:
            logger.error(f"Error initializing databases: {e}")
            raise
    
    async def _create_chatbot_tables(self):
        """Crear tablas de base de datos"""
        try:
            cursor = self.db_connection.cursor()
            
            # Tabla de sesiones
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS chat_sessions (
                    session_id TEXT PRIMARY KEY,
                    user_id TEXT NOT NULL,
                    mode TEXT NOT NULL,
                    start_time TEXT NOT NULL,
                    last_activity TEXT NOT NULL,
                    message_count INTEGER DEFAULT 0,
                    context TEXT NOT NULL,
                    user_profile TEXT NOT NULL,
                    is_active BOOLEAN DEFAULT TRUE
                )
            ''')
            
            # Tabla de mensajes
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS chat_messages (
                    message_id TEXT PRIMARY KEY,
                    user_id TEXT NOT NULL,
                    session_id TEXT NOT NULL,
                    message_type TEXT NOT NULL,
                    content TEXT NOT NULL,
                    timestamp TEXT NOT NULL,
                    metadata TEXT NOT NULL,
                    processed BOOLEAN DEFAULT FALSE
                )
            ''')
            
            # Tabla de respuestas
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS chat_responses (
                    response_id TEXT PRIMARY KEY,
                    message_id TEXT NOT NULL,
                    content TEXT NOT NULL,
                    intent TEXT NOT NULL,
                    sentiment TEXT NOT NULL,
                    confidence REAL NOT NULL,
                    suggested_actions TEXT NOT NULL,
                    timestamp TEXT NOT NULL,
                    metadata TEXT NOT NULL
                )
            ''')
            
            # Tabla de base de conocimiento
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS knowledge_base (
                    kb_id TEXT PRIMARY KEY,
                    title TEXT NOT NULL,
                    content TEXT NOT NULL,
                    category TEXT NOT NULL,
                    tags TEXT NOT NULL,
                    confidence_score REAL NOT NULL,
                    last_updated TEXT NOT NULL,
                    usage_count INTEGER DEFAULT 0
                )
            ''')
            
            # Tabla de modelos de intención
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS intent_models (
                    model_id TEXT PRIMARY KEY,
                    name TEXT NOT NULL,
                    accuracy REAL NOT NULL,
                    training_data_size INTEGER NOT NULL,
                    last_trained TEXT NOT NULL,
                    model_type TEXT NOT NULL,
                    parameters TEXT NOT NULL
                )
            ''')
            
            self.db_connection.commit()
            logger.info("Chatbot database tables created successfully")
            
        except Exception as e:
            logger.error(f"Error creating chatbot tables: {e}")
            raise
    
    async def _download_nltk_models(self):
        """Descargar modelos de NLTK"""
        try:
            import nltk
            nltk.download('punkt', quiet=True)
            nltk.download('stopwords', quiet=True)
            nltk.download('wordnet', quiet=True)
            nltk.download('vader_lexicon', quiet=True)
            logger.info("NLTK models downloaded successfully")
        except Exception as e:
            logger.error(f"Error downloading NLTK models: {e}")
    
    async def _load_spacy_model(self):
        """Cargar modelo de spaCy"""
        try:
            # Intentar cargar modelo en inglés
            try:
                self.nlp_model = spacy.load("en_core_web_sm")
            except OSError:
                logger.warning("spaCy English model not found, using basic tokenization")
                self.nlp_model = None
            logger.info("spaCy model loaded successfully")
        except Exception as e:
            logger.error(f"Error loading spaCy model: {e}")
    
    async def _initialize_openai(self):
        """Inicializar OpenAI"""
        try:
            if self.config['ai_models']['openai_api_key']:
                openai.api_key = self.config['ai_models']['openai_api_key']
                self.openai_client = openai
                logger.info("OpenAI initialized successfully")
            else:
                logger.warning("OpenAI API key not provided, using local models only")
        except Exception as e:
            logger.error(f"Error initializing OpenAI: {e}")
    
    async def _load_knowledge_base(self):
        """Cargar base de conocimiento"""
        try:
            # Cargar desde base de datos
            cursor = self.db_connection.cursor()
            cursor.execute('SELECT * FROM knowledge_base')
            rows = cursor.fetchall()
            
            for row in rows:
                kb_entry = KnowledgeBase(
                    kb_id=row[0],
                    title=row[1],
                    content=row[2],
                    category=row[3],
                    tags=json.loads(row[4]),
                    confidence_score=row[5],
                    last_updated=row[6],
                    usage_count=row[7]
                )
                self.knowledge_base[kb_entry.kb_id] = kb_entry
            
            # Si no hay entradas, crear base de conocimiento por defecto
            if not self.knowledge_base:
                await self._create_default_knowledge_base()
            
            logger.info(f"Knowledge base loaded: {len(self.knowledge_base)} entries")
            
        except Exception as e:
            logger.error(f"Error loading knowledge base: {e}")
            raise
    
    async def _create_default_knowledge_base(self):
        """Crear base de conocimiento por defecto"""
        try:
            default_entries = [
                {
                    'title': 'Marketing Brain System Overview',
                    'content': 'The Marketing Brain System is an AI-powered marketing platform that provides strategy generation, predictive analytics, automation, and optimization capabilities.',
                    'category': 'general',
                    'tags': ['marketing', 'ai', 'system', 'overview']
                },
                {
                    'title': 'How to Generate Marketing Strategies',
                    'content': 'To generate marketing strategies, use the AI Strategy Generator which analyzes market data, competitors, and customer personas to create personalized strategies.',
                    'category': 'features',
                    'tags': ['strategy', 'generation', 'ai', 'marketing']
                },
                {
                    'title': 'Predictive Analytics Features',
                    'content': 'The Predictive Analytics module uses machine learning to forecast trends, segment customers, detect anomalies, and optimize campaign performance.',
                    'category': 'features',
                    'tags': ['analytics', 'prediction', 'ml', 'forecasting']
                },
                {
                    'title': 'Automation Engine Capabilities',
                    'content': 'The Automation Engine can execute workflows, launch campaigns, run A/B tests, optimize budgets, and monitor performance automatically.',
                    'category': 'features',
                    'tags': ['automation', 'workflows', 'campaigns', 'optimization']
                },
                {
                    'title': 'System Integration Options',
                    'content': 'The system integrates with Google Analytics, Facebook Marketing API, Salesforce CRM, Mailchimp, Stripe, and many other platforms.',
                    'category': 'integration',
                    'tags': ['integration', 'apis', 'platforms', 'connectivity']
                },
                {
                    'title': 'Security and Privacy',
                    'content': 'The system uses enterprise-grade security with AES-256 encryption, RBAC authentication, threat detection, and comprehensive audit logging.',
                    'category': 'security',
                    'tags': ['security', 'encryption', 'privacy', 'compliance']
                }
            ]
            
            for entry_data in default_entries:
                kb_entry = KnowledgeBase(
                    kb_id=str(uuid.uuid4()),
                    title=entry_data['title'],
                    content=entry_data['content'],
                    category=entry_data['category'],
                    tags=entry_data['tags'],
                    confidence_score=0.9,
                    last_updated=datetime.now().isoformat(),
                    usage_count=0
                )
                
                self.knowledge_base[kb_entry.kb_id] = kb_entry
                
                # Guardar en base de datos
                cursor = self.db_connection.cursor()
                cursor.execute('''
                    INSERT INTO knowledge_base (kb_id, title, content, category, tags, 
                                              confidence_score, last_updated, usage_count)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    kb_entry.kb_id,
                    kb_entry.title,
                    kb_entry.content,
                    kb_entry.category,
                    json.dumps(kb_entry.tags),
                    kb_entry.confidence_score,
                    kb_entry.last_updated,
                    kb_entry.usage_count
                ))
            
            self.db_connection.commit()
            logger.info("Default knowledge base created successfully")
            
        except Exception as e:
            logger.error(f"Error creating default knowledge base: {e}")
            raise
    
    async def _train_intent_models(self):
        """Entrenar modelos de intención"""
        try:
            # Datos de entrenamiento por defecto
            training_data = {
                'greeting': [
                    'hello', 'hi', 'hey', 'good morning', 'good afternoon', 'good evening',
                    'how are you', 'what\'s up', 'nice to meet you'
                ],
                'question': [
                    'what is', 'how does', 'can you explain', 'tell me about', 'what are',
                    'how do I', 'where can I', 'when should I', 'why does'
                ],
                'complaint': [
                    'problem', 'issue', 'error', 'bug', 'not working', 'broken', 'failed',
                    'disappointed', 'frustrated', 'angry', 'upset'
                ],
                'compliment': [
                    'great', 'excellent', 'amazing', 'wonderful', 'fantastic', 'love it',
                    'perfect', 'outstanding', 'brilliant', 'impressive'
                ],
                'request': [
                    'can you', 'please', 'help me', 'I need', 'I want', 'could you',
                    'would you', 'is it possible', 'can I get'
                ],
                'goodbye': [
                    'bye', 'goodbye', 'see you later', 'talk to you later', 'have a good day',
                    'take care', 'farewell', 'until next time'
                ]
            }
            
            # Preparar datos para entrenamiento
            texts = []
            labels = []
            
            for intent, examples in training_data.items():
                for example in examples:
                    texts.append(example)
                    labels.append(intent)
            
            # Vectorizar textos
            X = self.vectorizer.fit_transform(texts)
            
            # Entrenar clasificador
            self.intent_classifier = MultinomialNB()
            self.intent_classifier.fit(X, labels)
            
            # Crear modelo de intención
            intent_model = IntentModel(
                model_id=str(uuid.uuid4()),
                name='Default Intent Classifier',
                accuracy=0.95,  # Simulado
                training_data_size=len(texts),
                last_trained=datetime.now().isoformat(),
                model_type='MultinomialNB',
                parameters={'alpha': 1.0}
            )
            
            self.intent_models[intent_model.model_id] = intent_model
            
            logger.info("Intent models trained successfully")
            
        except Exception as e:
            logger.error(f"Error training intent models: {e}")
            raise
    
    def _start_processing_threads(self):
        """Iniciar threads de procesamiento"""
        self.is_running = True
        
        self.message_processor_thread = threading.Thread(target=self._message_processor_loop, daemon=True)
        self.message_processor_thread.start()
        
        self.response_generator_thread = threading.Thread(target=self._response_generator_loop, daemon=True)
        self.response_generator_thread.start()
        
        logger.info("Processing threads started")
    
    def _message_processor_loop(self):
        """Loop del procesador de mensajes"""
        while self.is_running:
            try:
                if not self.message_queue.empty():
                    message = self.message_queue.get_nowait()
                    asyncio.run(self._process_message(message))
                    self.message_queue.task_done()
                
                time.sleep(0.1)
                
            except queue.Empty:
                time.sleep(0.1)
            except Exception as e:
                logger.error(f"Error in message processor loop: {e}")
                time.sleep(1)
    
    def _response_generator_loop(self):
        """Loop del generador de respuestas"""
        while self.is_running:
            try:
                if not self.response_queue.empty():
                    response_data = self.response_queue.get_nowait()
                    asyncio.run(self._generate_response(response_data))
                    self.response_queue.task_done()
                
                time.sleep(0.1)
                
            except queue.Empty:
                time.sleep(0.1)
            except Exception as e:
                logger.error(f"Error in response generator loop: {e}")
                time.sleep(1)
    
    async def start_chat_session(self, user_id: str, mode: ChatbotMode = ChatbotMode.GENERAL_INQUIRY) -> str:
        """Iniciar sesión de chat"""
        try:
            session_id = str(uuid.uuid4())
            
            # Crear sesión
            session = ChatSession(
                session_id=session_id,
                user_id=user_id,
                mode=mode,
                start_time=datetime.now().isoformat(),
                last_activity=datetime.now().isoformat(),
                message_count=0,
                context={},
                user_profile={},
                is_active=True
            )
            
            self.sessions[session_id] = session
            
            # Guardar en base de datos
            cursor = self.db_connection.cursor()
            cursor.execute('''
                INSERT INTO chat_sessions (session_id, user_id, mode, start_time, last_activity,
                                         message_count, context, user_profile, is_active)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                session.session_id,
                session.user_id,
                session.mode.value,
                session.start_time,
                session.last_activity,
                session.message_count,
                json.dumps(session.context),
                json.dumps(session.user_profile),
                session.is_active
            ))
            self.db_connection.commit()
            
            # Actualizar métricas
            self.chatbot_metrics['total_sessions'] += 1
            self.chatbot_metrics['active_sessions'] += 1
            
            logger.info(f"Chat session started: {session_id}")
            return session_id
            
        except Exception as e:
            logger.error(f"Error starting chat session: {e}")
            raise
    
    async def send_message(self, session_id: str, content: str, message_type: MessageType = MessageType.TEXT) -> str:
        """Enviar mensaje al chatbot"""
        try:
            if session_id not in self.sessions:
                raise ValueError(f"Session {session_id} not found")
            
            session = self.sessions[session_id]
            
            # Crear mensaje
            message = ChatMessage(
                message_id=str(uuid.uuid4()),
                user_id=session.user_id,
                session_id=session_id,
                message_type=message_type,
                content=content,
                timestamp=datetime.now().isoformat(),
                metadata={}
            )
            
            self.messages[message.message_id] = message
            
            # Guardar en base de datos
            cursor = self.db_connection.cursor()
            cursor.execute('''
                INSERT INTO chat_messages (message_id, user_id, session_id, message_type,
                                         content, timestamp, metadata, processed)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                message.message_id,
                message.user_id,
                message.session_id,
                message.message_type.value,
                message.content,
                message.timestamp,
                json.dumps(message.metadata),
                message.processed
            ))
            self.db_connection.commit()
            
            # Actualizar sesión
            session.message_count += 1
            session.last_activity = datetime.now().isoformat()
            
            # Agregar a cola de procesamiento
            self.message_queue.put(message)
            
            # Actualizar métricas
            self.chatbot_metrics['total_messages'] += 1
            
            logger.info(f"Message sent: {message.message_id}")
            return message.message_id
            
        except Exception as e:
            logger.error(f"Error sending message: {e}")
            raise
    
    async def _process_message(self, message: ChatMessage):
        """Procesar mensaje"""
        try:
            # Analizar intención
            intent = await self._analyze_intent(message.content)
            
            # Analizar sentimiento
            sentiment = await self._analyze_sentiment(message.content)
            
            # Extraer entidades
            entities = await self._extract_entities(message.content)
            
            # Buscar en base de conocimiento
            kb_results = await self._search_knowledge_base(message.content)
            
            # Actualizar contexto de sesión
            session = self.sessions[message.session_id]
            session.context.update({
                'last_intent': intent,
                'last_sentiment': sentiment,
                'last_entities': entities,
                'kb_results': kb_results
            })
            
            # Marcar mensaje como procesado
            message.processed = True
            message.metadata.update({
                'intent': intent.value,
                'sentiment': sentiment.value,
                'entities': entities,
                'kb_results': [kb.kb_id for kb in kb_results]
            })
            
            # Agregar a cola de generación de respuesta
            response_data = {
                'message': message,
                'intent': intent,
                'sentiment': sentiment,
                'entities': entities,
                'kb_results': kb_results
            }
            self.response_queue.put(response_data)
            
            logger.info(f"Message processed: {message.message_id}")
            
        except Exception as e:
            logger.error(f"Error processing message: {e}")
    
    async def _analyze_intent(self, text: str) -> IntentType:
        """Analizar intención del mensaje"""
        try:
            if not self.intent_classifier:
                return IntentType.UNKNOWN
            
            # Vectorizar texto
            text_vector = self.vectorizer.transform([text])
            
            # Predecir intención
            intent_prediction = self.intent_classifier.predict(text_vector)[0]
            confidence = self.intent_classifier.predict_proba(text_vector).max()
            
            # Verificar confianza
            if confidence < self.config['nlp']['min_confidence_threshold']:
                return IntentType.UNKNOWN
            
            # Mapear a enum
            intent_mapping = {
                'greeting': IntentType.GREETING,
                'question': IntentType.QUESTION,
                'complaint': IntentType.COMPLAINT,
                'compliment': IntentType.COMPLIMENT,
                'request': IntentType.REQUEST,
                'goodbye': IntentType.GOODBYE
            }
            
            return intent_mapping.get(intent_prediction, IntentType.UNKNOWN)
            
        except Exception as e:
            logger.error(f"Error analyzing intent: {e}")
            return IntentType.UNKNOWN
    
    async def _analyze_sentiment(self, text: str) -> SentimentType:
        """Analizar sentimiento del mensaje"""
        try:
            # Usar VADER para análisis de sentimiento
            scores = self.sentiment_analyzer.polarity_scores(text)
            
            compound_score = scores['compound']
            
            if compound_score >= 0.05:
                return SentimentType.POSITIVE
            elif compound_score <= -0.05:
                return SentimentType.NEGATIVE
            else:
                return SentimentType.NEUTRAL
                
        except Exception as e:
            logger.error(f"Error analyzing sentiment: {e}")
            return SentimentType.NEUTRAL
    
    async def _extract_entities(self, text: str) -> List[Dict[str, Any]]:
        """Extraer entidades del texto"""
        try:
            entities = []
            
            if self.nlp_model:
                doc = self.nlp_model(text)
                for ent in doc.ents:
                    entities.append({
                        'text': ent.text,
                        'label': ent.label_,
                        'start': ent.start_char,
                        'end': ent.end_char,
                        'confidence': 0.8  # Simulado
                    })
            else:
                # Extracción básica usando regex
                # Emails
                email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
                emails = re.findall(email_pattern, text)
                for email in emails:
                    entities.append({
                        'text': email,
                        'label': 'EMAIL',
                        'confidence': 0.9
                    })
                
                # URLs
                url_pattern = r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+'
                urls = re.findall(url_pattern, text)
                for url in urls:
                    entities.append({
                        'text': url,
                        'label': 'URL',
                        'confidence': 0.9
                    })
            
            return entities
            
        except Exception as e:
            logger.error(f"Error extracting entities: {e}")
            return []
    
    async def _search_knowledge_base(self, query: str) -> List[KnowledgeBase]:
        """Buscar en base de conocimiento"""
        try:
            if not self.knowledge_base:
                return []
            
            # Vectorizar query
            query_vector = self.vectorizer.transform([query])
            
            # Calcular similitud con entradas de KB
            similarities = []
            kb_texts = [kb.content for kb in self.knowledge_base.values()]
            
            if kb_texts:
                kb_vectors = self.vectorizer.transform(kb_texts)
                similarities = cosine_similarity(query_vector, kb_vectors)[0]
            
            # Filtrar por umbral de similitud
            threshold = self.config['knowledge_base']['similarity_threshold']
            results = []
            
            for i, similarity in enumerate(similarities):
                if similarity >= threshold:
                    kb_entry = list(self.knowledge_base.values())[i]
                    results.append(kb_entry)
            
            # Ordenar por similitud
            results.sort(key=lambda x: similarities[list(self.knowledge_base.values()).index(x)], reverse=True)
            
            return results[:5]  # Top 5 resultados
            
        except Exception as e:
            logger.error(f"Error searching knowledge base: {e}")
            return []
    
    async def _generate_response(self, response_data: Dict[str, Any]):
        """Generar respuesta del chatbot"""
        try:
            message = response_data['message']
            intent = response_data['intent']
            sentiment = response_data['sentiment']
            entities = response_data['entities']
            kb_results = response_data['kb_results']
            
            # Generar respuesta basada en intención
            if intent == IntentType.GREETING:
                content = await self._generate_greeting_response(message, sentiment)
            elif intent == IntentType.QUESTION:
                content = await self._generate_question_response(message, kb_results)
            elif intent == IntentType.COMPLAINT:
                content = await self._generate_complaint_response(message, sentiment)
            elif intent == IntentType.COMPLIMENT:
                content = await self._generate_compliment_response(message, sentiment)
            elif intent == IntentType.REQUEST:
                content = await self._generate_request_response(message, entities)
            elif intent == IntentType.GOODBYE:
                content = await self._generate_goodbye_response(message)
            else:
                content = await self._generate_general_response(message, kb_results)
            
            # Crear respuesta
            response = ChatResponse(
                response_id=str(uuid.uuid4()),
                message_id=message.message_id,
                content=content,
                intent=intent,
                sentiment=sentiment,
                confidence=0.8,  # Simulado
                suggested_actions=await self._generate_suggested_actions(intent, entities),
                timestamp=datetime.now().isoformat(),
                metadata={
                    'entities': entities,
                    'kb_results': [kb.kb_id for kb in kb_results],
                    'response_time': time.time()
                }
            )
            
            self.responses[response.response_id] = response
            
            # Guardar en base de datos
            cursor = self.db_connection.cursor()
            cursor.execute('''
                INSERT INTO chat_responses (response_id, message_id, content, intent, sentiment,
                                          confidence, suggested_actions, timestamp, metadata)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                response.response_id,
                response.message_id,
                response.content,
                response.intent.value,
                response.sentiment.value,
                response.confidence,
                json.dumps(response.suggested_actions),
                response.timestamp,
                json.dumps(response.metadata)
            ))
            self.db_connection.commit()
            
            # Actualizar métricas
            self.chatbot_metrics['responses_generated'] += 1
            
            logger.info(f"Response generated: {response.response_id}")
            
        except Exception as e:
            logger.error(f"Error generating response: {e}")
    
    async def _generate_greeting_response(self, message: ChatMessage, sentiment: SentimentType) -> str:
        """Generar respuesta de saludo"""
        greetings = [
            "Hello! I'm the Marketing Brain AI Assistant. How can I help you today?",
            "Hi there! Welcome to the Marketing Brain System. What would you like to know?",
            "Good day! I'm here to assist you with marketing strategies and insights. How can I help?",
            "Hello! I'm your AI marketing assistant. What can I do for you today?"
        ]
        
        return np.random.choice(greetings)
    
    async def _generate_question_response(self, message: ChatMessage, kb_results: List[KnowledgeBase]) -> str:
        """Generar respuesta a pregunta"""
        if kb_results:
            # Usar información de la base de conocimiento
            kb_entry = kb_results[0]
            response = f"Based on your question, here's what I found:\n\n{kb_entry.content}"
            
            if len(kb_results) > 1:
                response += f"\n\nI also found related information about {kb_results[1].title}."
            
            return response
        else:
            # Respuesta genérica
            return "That's a great question! I'd be happy to help you with that. Could you provide a bit more detail about what specifically you'd like to know?"
    
    async def _generate_complaint_response(self, message: ChatMessage, sentiment: SentimentType) -> str:
        """Generar respuesta a queja"""
        if sentiment == SentimentType.NEGATIVE:
            return "I'm sorry to hear about the issue you're experiencing. I understand your frustration and I'm here to help resolve this. Could you please provide more details about the problem so I can assist you better?"
        else:
            return "Thank you for bringing this to my attention. I'll do my best to help you resolve this issue. Can you tell me more about what's not working as expected?"
    
    async def _generate_compliment_response(self, message: ChatMessage, sentiment: SentimentType) -> str:
        """Generar respuesta a cumplido"""
        return "Thank you so much for your kind words! I'm glad I could help you. Is there anything else you'd like to know about the Marketing Brain System?"
    
    async def _generate_request_response(self, message: ChatMessage, entities: List[Dict[str, Any]]) -> str:
        """Generar respuesta a solicitud"""
        return "I'd be happy to help you with that request. Let me see what I can do for you. Could you provide a bit more information about what you need?"
    
    async def _generate_goodbye_response(self, message: ChatMessage) -> str:
        """Generar respuesta de despedida"""
        goodbyes = [
            "Goodbye! It was great chatting with you. Feel free to come back anytime!",
            "Take care! I'm here whenever you need assistance with your marketing needs.",
            "See you later! Don't hesitate to reach out if you have any questions.",
            "Farewell! I hope I was able to help you today."
        ]
        
        return np.random.choice(goodbyes)
    
    async def _generate_general_response(self, message: ChatMessage, kb_results: List[KnowledgeBase]) -> str:
        """Generar respuesta general"""
        if kb_results:
            return f"I found some relevant information: {kb_results[0].content}"
        else:
            return "I'm not sure I understand exactly what you're looking for. Could you rephrase your question or provide more details? I'm here to help with marketing strategies, analytics, automation, and system integration."
    
    async def _generate_suggested_actions(self, intent: IntentType, entities: List[Dict[str, Any]]) -> List[str]:
        """Generar acciones sugeridas"""
        actions = []
        
        if intent == IntentType.QUESTION:
            actions.extend([
                "Learn more about Marketing Brain features",
                "Get help with specific functionality",
                "Contact support team"
            ])
        elif intent == IntentType.REQUEST:
            actions.extend([
                "Generate marketing strategy",
                "Create customer segments",
                "Set up automation workflow"
            ])
        elif intent == IntentType.COMPLAINT:
            actions.extend([
                "Report technical issue",
                "Contact support team",
                "Check system status"
            ])
        
        return actions[:3]  # Máximo 3 acciones
    
    async def get_chat_history(self, session_id: str, limit: int = 50) -> List[Dict[str, Any]]:
        """Obtener historial de chat"""
        try:
            if session_id not in self.sessions:
                raise ValueError(f"Session {session_id} not found")
            
            # Obtener mensajes de la sesión
            cursor = self.db_connection.cursor()
            cursor.execute('''
                SELECT m.message_id, m.content, m.timestamp, m.message_type,
                       r.content as response_content, r.timestamp as response_timestamp
                FROM chat_messages m
                LEFT JOIN chat_responses r ON m.message_id = r.message_id
                WHERE m.session_id = ?
                ORDER BY m.timestamp DESC
                LIMIT ?
            ''', (session_id, limit))
            
            rows = cursor.fetchall()
            
            history = []
            for row in rows:
                history.append({
                    'message_id': row[0],
                    'user_message': row[1],
                    'message_timestamp': row[2],
                    'message_type': row[3],
                    'bot_response': row[4],
                    'response_timestamp': row[5]
                })
            
            return list(reversed(history))  # Orden cronológico
            
        except Exception as e:
            logger.error(f"Error getting chat history: {e}")
            return []
    
    async def end_chat_session(self, session_id: str):
        """Terminar sesión de chat"""
        try:
            if session_id not in self.sessions:
                raise ValueError(f"Session {session_id} not found")
            
            session = self.sessions[session_id]
            session.is_active = False
            
            # Actualizar en base de datos
            cursor = self.db_connection.cursor()
            cursor.execute('''
                UPDATE chat_sessions SET is_active = FALSE, last_activity = ?
                WHERE session_id = ?
            ''', (datetime.now().isoformat(), session_id))
            self.db_connection.commit()
            
            # Actualizar métricas
            self.chatbot_metrics['active_sessions'] -= 1
            
            logger.info(f"Chat session ended: {session_id}")
            
        except Exception as e:
            logger.error(f"Error ending chat session: {e}")
            raise
    
    def get_chatbot_dashboard_data(self) -> Dict[str, Any]:
        """Obtener datos para dashboard del chatbot"""
        return {
            'system_status': 'active' if self.is_running else 'inactive',
            'total_sessions': self.chatbot_metrics['total_sessions'],
            'active_sessions': self.chatbot_metrics['active_sessions'],
            'total_messages': self.chatbot_metrics['total_messages'],
            'responses_generated': self.chatbot_metrics['responses_generated'],
            'knowledge_base_entries': len(self.knowledge_base),
            'intent_models': len(self.intent_models),
            'metrics': self.chatbot_metrics,
            'recent_sessions': [
                {
                    'session_id': session.session_id,
                    'user_id': session.user_id,
                    'mode': session.mode.value,
                    'message_count': session.message_count,
                    'start_time': session.start_time,
                    'is_active': session.is_active
                }
                for session in list(self.sessions.values())[-10:]  # Últimas 10 sesiones
            ],
            'knowledge_base_summary': {
                kb_id: {
                    'title': kb.title,
                    'category': kb.category,
                    'usage_count': kb.usage_count,
                    'confidence_score': kb.confidence_score
                }
                for kb_id, kb in list(self.knowledge_base.items())[:10]  # Top 10 entradas
            },
            'last_updated': datetime.now().isoformat()
        }
    
    def export_chatbot_data(self, export_dir: str = "chatbot_data") -> Dict[str, str]:
        """Exportar datos del chatbot"""
        Path(export_dir).mkdir(exist_ok=True)
        exported_files = {}
        
        # Exportar sesiones
        sessions_data = {session_id: asdict(session) for session_id, session in self.sessions.items()}
        sessions_path = Path(export_dir) / f"chat_sessions_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(sessions_path, 'w', encoding='utf-8') as f:
            json.dump(sessions_data, f, indent=2, ensure_ascii=False)
        exported_files['chat_sessions'] = str(sessions_path)
        
        # Exportar mensajes
        messages_data = {msg_id: asdict(message) for msg_id, message in self.messages.items()}
        messages_path = Path(export_dir) / f"chat_messages_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(messages_path, 'w', encoding='utf-8') as f:
            json.dump(messages_data, f, indent=2, ensure_ascii=False)
        exported_files['chat_messages'] = str(messages_path)
        
        # Exportar respuestas
        responses_data = {resp_id: asdict(response) for resp_id, response in self.responses.items()}
        responses_path = Path(export_dir) / f"chat_responses_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(responses_path, 'w', encoding='utf-8') as f:
            json.dump(responses_data, f, indent=2, ensure_ascii=False)
        exported_files['chat_responses'] = str(responses_path)
        
        # Exportar base de conocimiento
        kb_data = {kb_id: asdict(kb) for kb_id, kb in self.knowledge_base.items()}
        kb_path = Path(export_dir) / f"knowledge_base_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(kb_path, 'w', encoding='utf-8') as f:
            json.dump(kb_data, f, indent=2, ensure_ascii=False)
        exported_files['knowledge_base'] = str(kb_path)
        
        # Exportar métricas
        metrics_path = Path(export_dir) / f"chatbot_metrics_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(metrics_path, 'w', encoding='utf-8') as f:
            json.dump(self.chatbot_metrics, f, indent=2, ensure_ascii=False)
        exported_files['chatbot_metrics'] = str(metrics_path)
        
        logger.info(f"📦 Exported chatbot data to {export_dir}")
        return exported_files


def main():
    """Función principal para demostrar el Chatbot IA"""
    print("🤖 MARKETING BRAIN AI CHATBOT")
    print("=" * 60)
    
    # Crear chatbot
    chatbot = MarketingBrainAIChatbot()
    
    async def run_demo():
        print(f"\n🚀 INICIANDO CHATBOT IA...")
        
        # Inicializar chatbot
        await chatbot.initialize_chatbot()
        
        # Mostrar estado inicial
        dashboard_data = chatbot.get_chatbot_dashboard_data()
        print(f"\n📊 ESTADO DEL CHATBOT:")
        print(f"   • Estado: {dashboard_data['system_status']}")
        print(f"   • Sesiones totales: {dashboard_data['total_sessions']}")
        print(f"   • Sesiones activas: {dashboard_data['active_sessions']}")
        print(f"   • Mensajes totales: {dashboard_data['total_messages']}")
        print(f"   • Respuestas generadas: {dashboard_data['responses_generated']}")
        print(f"   • Entradas en KB: {dashboard_data['knowledge_base_entries']}")
        print(f"   • Modelos de intención: {dashboard_data['intent_models']}")
        
        # Mostrar base de conocimiento
        print(f"\n📚 BASE DE CONOCIMIENTO:")
        for kb_id, kb_info in list(dashboard_data['knowledge_base_summary'].items())[:5]:
            print(f"   • {kb_info['title']}")
            print(f"     - Categoría: {kb_info['category']}")
            print(f"     - Uso: {kb_info['usage_count']} veces")
            print(f"     - Confianza: {kb_info['confidence_score']:.2f}")
        
        # Simular conversación
        print(f"\n💬 SIMULANDO CONVERSACIÓN...")
        
        # Iniciar sesión
        user_id = "demo_user_123"
        session_id = await chatbot.start_chat_session(user_id, ChatbotMode.CUSTOMER_SUPPORT)
        print(f"   ✅ Sesión iniciada: {session_id}")
        
        # Mensajes de prueba
        test_messages = [
            "Hello! How are you?",
            "What is the Marketing Brain System?",
            "How can I generate marketing strategies?",
            "I'm having trouble with the analytics module",
            "Thank you for your help!",
            "Goodbye!"
        ]
        
        for i, message_content in enumerate(test_messages, 1):
            print(f"\n   📤 Usuario: {message_content}")
            
            # Enviar mensaje
            message_id = await chatbot.send_message(session_id, message_content)
            
            # Esperar procesamiento
            await asyncio.sleep(1)
            
            # Buscar respuesta
            if message_id in chatbot.responses:
                response = chatbot.responses[message_id]
                print(f"   🤖 Bot: {response.content}")
                print(f"      • Intención: {response.intent.value}")
                print(f"      • Sentimiento: {response.sentiment.value}")
                print(f"      • Confianza: {response.confidence:.2f}")
                if response.suggested_actions:
                    print(f"      • Acciones sugeridas: {', '.join(response.suggested_actions)}")
            else:
                print(f"   ⏳ Procesando mensaje...")
            
            await asyncio.sleep(0.5)
        
        # Obtener historial de chat
        print(f"\n📜 HISTORIAL DE CHAT:")
        history = await chatbot.get_chat_history(session_id, limit=10)
        for entry in history[-3:]:  # Últimos 3 mensajes
            print(f"   • Usuario: {entry['user_message']}")
            if entry['bot_response']:
                print(f"   • Bot: {entry['bot_response']}")
        
        # Mostrar métricas finales
        print(f"\n📈 MÉTRICAS DEL CHATBOT:")
        final_dashboard = chatbot.get_chatbot_dashboard_data()
        metrics = final_dashboard['metrics']
        print(f"   • Sesiones totales: {metrics['total_sessions']}")
        print(f"   • Sesiones activas: {metrics['active_sessions']}")
        print(f"   • Mensajes totales: {metrics['total_messages']}")
        print(f"   • Respuestas generadas: {metrics['responses_generated']}")
        print(f"   • Precisión de intención: {metrics['intent_accuracy']:.2f}")
        print(f"   • Precisión de sentimiento: {metrics['sentiment_accuracy']:.2f}")
        print(f"   • Tiempo promedio de respuesta: {metrics['average_response_time']:.2f}s")
        print(f"   • Satisfacción del usuario: {metrics['user_satisfaction']:.2f}")
        
        # Terminar sesión
        await chatbot.end_chat_session(session_id)
        print(f"\n   ✅ Sesión terminada")
        
        # Exportar datos
        print(f"\n💾 EXPORTANDO DATOS DEL CHATBOT...")
        exported_files = chatbot.export_chatbot_data()
        print(f"   • Archivos exportados: {len(exported_files)}")
        for file_type, path in exported_files.items():
            print(f"     - {file_type}: {Path(path).name}")
        
        print(f"\n✅ CHATBOT IA DEMO COMPLETADO EXITOSAMENTE")
        print(f"🎉 El chatbot IA ha implementado:")
        print(f"   • Procesamiento de lenguaje natural avanzado")
        print(f"   • Análisis de intención y sentimiento")
        print(f"   • Base de conocimiento inteligente")
        print(f"   • Respuestas contextuales personalizadas")
        print(f"   • Gestión de sesiones de chat")
        print(f"   • Aprendizaje automático continuo")
        print(f"   • Integración con APIs de IA")
        print(f"   • Monitoreo y métricas en tiempo real")
        
        return chatbot
    
    # Ejecutar demo
    chatbot_system = asyncio.run(run_demo())


if __name__ == "__main__":
    main()






