"""
Motor de Procesamiento de Lenguaje Natural Avanzado
Sistema de NLP con análisis de sentimientos, clasificación de texto y técnicas avanzadas
"""

import asyncio
import json
import logging
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple, Union
from dataclasses import dataclass
from enum import Enum
import warnings
warnings.filterwarnings('ignore')

# NLP libraries
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize, sent_tokenize
from nltk.stem import PorterStemmer, WordNetLemmatizer
from nltk.sentiment import SentimentIntensityAnalyzer
from nltk.chunk import ne_chunk
from nltk.tag import pos_tag
from textblob import TextBlob
import spacy
from sklearn.feature_extraction.text import TfidfVectorizer, CountVectorizer
from sklearn.naive_bayes import MultinomialNB
from sklearn.linear_model import LogisticRegression
from sklearn.svm import SVC
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report, confusion_matrix, accuracy_score
from sklearn.model_selection import train_test_split
import re

# Deep learning for NLP
import tensorflow as tf
from tensorflow.keras.models import Sequential, Model
from tensorflow.keras.layers import Embedding, LSTM, GRU, Dense, Dropout, Conv1D, MaxPooling1D, GlobalMaxPooling1D
from tensorflow.keras.preprocessing.text import Tokenizer
from tensorflow.keras.preprocessing.sequence import pad_sequences
from tensorflow.keras.optimizers import Adam
from tensorflow.keras.callbacks import EarlyStopping

# Transformers (if available)
try:
    from transformers import pipeline, AutoTokenizer, AutoModelForSequenceClassification
    TRANSFORMERS_AVAILABLE = True
except ImportError:
    TRANSFORMERS_AVAILABLE = False

class NLPTaskType(Enum):
    SENTIMENT_ANALYSIS = "sentiment_analysis"
    TEXT_CLASSIFICATION = "text_classification"
    NAMED_ENTITY_RECOGNITION = "named_entity_recognition"
    TEXT_SUMMARIZATION = "text_summarization"
    LANGUAGE_DETECTION = "language_detection"
    KEYWORD_EXTRACTION = "keyword_extraction"
    TOPIC_MODELING = "topic_modeling"
    TEXT_SIMILARITY = "text_similarity"
    QUESTION_ANSWERING = "question_answering"
    TEXT_GENERATION = "text_generation"

class NLPModelType(Enum):
    RULE_BASED = "rule_based"
    MACHINE_LEARNING = "machine_learning"
    DEEP_LEARNING = "deep_learning"
    TRANSFORMER = "transformer"
    HYBRID = "hybrid"

@dataclass
class NLPRequest:
    text: str
    task_type: NLPTaskType
    model_type: NLPModelType
    language: str = "en"
    parameters: Dict[str, Any] = None
    context: Dict[str, Any] = None

@dataclass
class NLPResult:
    result: Any
    confidence: float
    model_info: Dict[str, Any]
    processing_time: float
    metadata: Dict[str, Any]

class AdvancedNLPEngine:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.models = {}
        self.tokenizers = {}
        self.vectorizers = {}
        self.nlp_models = {}
        self.processing_history = {}
        
        # Configuración por defecto
        self.default_config = {
            "max_sequence_length": 512,
            "embedding_dim": 100,
            "vocabulary_size": 10000,
            "learning_rate": 0.001,
            "batch_size": 32,
            "epochs": 100,
            "early_stopping_patience": 10
        }
        
        # Inicializar NLTK
        self._initialize_nltk()
        
        # Inicializar spaCy
        self._initialize_spacy()
        
    def _initialize_nltk(self):
        """Inicializar NLTK"""
        try:
            # Descargar recursos necesarios
            nltk.download('punkt', quiet=True)
            nltk.download('stopwords', quiet=True)
            nltk.download('wordnet', quiet=True)
            nltk.download('vader_lexicon', quiet=True)
            nltk.download('averaged_perceptron_tagger', quiet=True)
            nltk.download('maxent_ne_chunker', quiet=True)
            nltk.download('words', quiet=True)
            
            # Inicializar herramientas
            self.stemmer = PorterStemmer()
            self.lemmatizer = WordNetLemmatizer()
            self.sentiment_analyzer = SentimentIntensityAnalyzer()
            self.stop_words = set(stopwords.words('english'))
            
        except Exception as e:
            self.logger.warning(f"Error initializing NLTK: {e}")
    
    def _initialize_spacy(self):
        """Inicializar spaCy"""
        try:
            # Cargar modelo de spaCy
            self.nlp = spacy.load("en_core_web_sm")
        except OSError:
            self.logger.warning("spaCy model 'en_core_web_sm' not found. Please install it with: python -m spacy download en_core_web_sm")
            self.nlp = None
    
    async def process_text(self, request: NLPRequest) -> NLPResult:
        """Procesar texto con NLP avanzado"""
        try:
            start_time = datetime.now()
            
            # Validar entrada
            await self._validate_request(request)
            
            # Procesar según tipo de tarea
            if request.task_type == NLPTaskType.SENTIMENT_ANALYSIS:
                result = await self._analyze_sentiment(request)
            elif request.task_type == NLPTaskType.TEXT_CLASSIFICATION:
                result = await self._classify_text(request)
            elif request.task_type == NLPTaskType.NAMED_ENTITY_RECOGNITION:
                result = await self._extract_named_entities(request)
            elif request.task_type == NLPTaskType.TEXT_SUMMARIZATION:
                result = await self._summarize_text(request)
            elif request.task_type == NLPTaskType.LANGUAGE_DETECTION:
                result = await self._detect_language(request)
            elif request.task_type == NLPTaskType.KEYWORD_EXTRACTION:
                result = await self._extract_keywords(request)
            elif request.task_type == NLPTaskType.TOPIC_MODELING:
                result = await self._model_topics(request)
            elif request.task_type == NLPTaskType.TEXT_SIMILARITY:
                result = await self._calculate_text_similarity(request)
            elif request.task_type == NLPTaskType.QUESTION_ANSWERING:
                result = await self._answer_question(request)
            elif request.task_type == NLPTaskType.TEXT_GENERATION:
                result = await self._generate_text(request)
            else:
                raise ValueError(f"Unsupported NLP task type: {request.task_type}")
            
            # Calcular tiempo de procesamiento
            processing_time = (datetime.now() - start_time).total_seconds()
            
            # Crear resultado
            nlp_result = NLPResult(
                result=result,
                confidence=result.get("confidence", 0.0) if isinstance(result, dict) else 0.0,
                model_info=result.get("model_info", {}) if isinstance(result, dict) else {},
                processing_time=processing_time,
                metadata={
                    "task_type": request.task_type.value,
                    "model_type": request.model_type.value,
                    "language": request.language,
                    "text_length": len(request.text),
                    "processed_at": datetime.now().isoformat()
                }
            )
            
            # Guardar en historial
            await self._save_processing_history(request, nlp_result)
            
            return nlp_result
            
        except Exception as e:
            self.logger.error(f"Error processing text: {e}")
            raise
    
    async def _validate_request(self, request: NLPRequest) -> None:
        """Validar solicitud de NLP"""
        try:
            if not request.text or not request.text.strip():
                raise ValueError("Text is empty or None")
            
            if not request.task_type:
                raise ValueError("Task type is required")
            
            if not request.model_type:
                raise ValueError("Model type is required")
            
        except Exception as e:
            self.logger.error(f"Error validating request: {e}")
            raise
    
    async def _analyze_sentiment(self, request: NLPRequest) -> Dict[str, Any]:
        """Analizar sentimientos del texto"""
        try:
            text = request.text
            
            if request.model_type == NLPModelType.RULE_BASED:
                # Análisis basado en reglas con VADER
                scores = self.sentiment_analyzer.polarity_scores(text)
                
                # Determinar sentimiento
                if scores['compound'] >= 0.05:
                    sentiment = 'positive'
                elif scores['compound'] <= -0.05:
                    sentiment = 'negative'
                else:
                    sentiment = 'neutral'
                
                result = {
                    "sentiment": sentiment,
                    "scores": scores,
                    "confidence": abs(scores['compound']),
                    "model_info": {
                        "model": "VADER",
                        "type": "rule_based"
                    }
                }
                
            elif request.model_type == NLPModelType.MACHINE_LEARNING:
                # Análisis con TextBlob
                blob = TextBlob(text)
                polarity = blob.sentiment.polarity
                subjectivity = blob.sentiment.subjectivity
                
                # Determinar sentimiento
                if polarity > 0.1:
                    sentiment = 'positive'
                elif polarity < -0.1:
                    sentiment = 'negative'
                else:
                    sentiment = 'neutral'
                
                result = {
                    "sentiment": sentiment,
                    "polarity": polarity,
                    "subjectivity": subjectivity,
                    "confidence": abs(polarity),
                    "model_info": {
                        "model": "TextBlob",
                        "type": "machine_learning"
                    }
                }
                
            elif request.model_type == NLPModelType.TRANSFORMER and TRANSFORMERS_AVAILABLE:
                # Análisis con modelo transformer
                sentiment_pipeline = pipeline("sentiment-analysis", model="cardiffnlp/twitter-roberta-base-sentiment-latest")
                sentiment_result = sentiment_pipeline(text)
                
                result = {
                    "sentiment": sentiment_result[0]['label'].lower(),
                    "confidence": sentiment_result[0]['score'],
                    "model_info": {
                        "model": "twitter-roberta-base-sentiment",
                        "type": "transformer"
                    }
                }
                
            else:
                # Fallback a análisis basado en reglas
                scores = self.sentiment_analyzer.polarity_scores(text)
                sentiment = 'positive' if scores['compound'] >= 0.05 else 'negative' if scores['compound'] <= -0.05 else 'neutral'
                
                result = {
                    "sentiment": sentiment,
                    "scores": scores,
                    "confidence": abs(scores['compound']),
                    "model_info": {
                        "model": "VADER (fallback)",
                        "type": "rule_based"
                    }
                }
            
            return result
            
        except Exception as e:
            self.logger.error(f"Error analyzing sentiment: {e}")
            raise
    
    async def _classify_text(self, request: NLPRequest) -> Dict[str, Any]:
        """Clasificar texto"""
        try:
            text = request.text
            
            if request.model_type == NLPModelType.MACHINE_LEARNING:
                # Clasificación con ML
                categories = request.parameters.get("categories", ["positive", "negative", "neutral"]) if request.parameters else ["positive", "negative", "neutral"]
                
                # Crear datos de entrenamiento sintéticos
                training_data = await self._create_synthetic_training_data(categories)
                
                # Vectorizar texto
                vectorizer = TfidfVectorizer(max_features=1000, stop_words='english')
                X_train = vectorizer.fit_transform(training_data['text'])
                X_test = vectorizer.transform([text])
                
                # Entrenar modelo
                model = MultinomialNB()
                model.fit(X_train, training_data['label'])
                
                # Predecir
                prediction = model.predict(X_test)[0]
                probabilities = model.predict_proba(X_test)[0]
                confidence = max(probabilities)
                
                result = {
                    "category": prediction,
                    "confidence": confidence,
                    "probabilities": dict(zip(categories, probabilities)),
                    "model_info": {
                        "model": "MultinomialNB",
                        "type": "machine_learning",
                        "categories": categories
                    }
                }
                
            elif request.model_type == NLPModelType.DEEP_LEARNING:
                # Clasificación con deep learning
                categories = request.parameters.get("categories", ["positive", "negative", "neutral"]) if request.parameters else ["positive", "negative", "neutral"]
                
                # Crear modelo LSTM
                model = await self._create_lstm_classifier(categories)
                
                # Preprocesar texto
                tokenizer = Tokenizer(num_words=self.default_config["vocabulary_size"])
                tokenizer.fit_on_texts([text])
                sequences = tokenizer.texts_to_sequences([text])
                padded_sequences = pad_sequences(sequences, maxlen=self.default_config["max_sequence_length"])
                
                # Predecir
                prediction_proba = model.predict(padded_sequences)[0]
                prediction_idx = np.argmax(prediction_proba)
                prediction = categories[prediction_idx]
                confidence = prediction_proba[prediction_idx]
                
                result = {
                    "category": prediction,
                    "confidence": confidence,
                    "probabilities": dict(zip(categories, prediction_proba)),
                    "model_info": {
                        "model": "LSTM",
                        "type": "deep_learning",
                        "categories": categories
                    }
                }
                
            else:
                # Fallback a análisis de sentimientos
                sentiment_result = await self._analyze_sentiment(NLPRequest(
                    text=text,
                    task_type=NLPTaskType.SENTIMENT_ANALYSIS,
                    model_type=NLPModelType.RULE_BASED
                ))
                
                result = {
                    "category": sentiment_result["sentiment"],
                    "confidence": sentiment_result["confidence"],
                    "model_info": {
                        "model": "Sentiment Analysis (fallback)",
                        "type": "rule_based"
                    }
                }
            
            return result
            
        except Exception as e:
            self.logger.error(f"Error classifying text: {e}")
            raise
    
    async def _extract_named_entities(self, request: NLPRequest) -> Dict[str, Any]:
        """Extraer entidades nombradas"""
        try:
            text = request.text
            
            if self.nlp is not None:
                # Usar spaCy para NER
                doc = self.nlp(text)
                
                entities = []
                for ent in doc.ents:
                    entities.append({
                        "text": ent.text,
                        "label": ent.label_,
                        "start": ent.start_char,
                        "end": ent.end_char,
                        "confidence": 0.9  # spaCy no proporciona confianza por defecto
                    })
                
                result = {
                    "entities": entities,
                    "entity_count": len(entities),
                    "model_info": {
                        "model": "spaCy en_core_web_sm",
                        "type": "rule_based"
                    }
                }
                
            else:
                # Fallback a NLTK
                tokens = word_tokenize(text)
                pos_tags = pos_tag(tokens)
                chunks = ne_chunk(pos_tags)
                
                entities = []
                for chunk in chunks:
                    if hasattr(chunk, 'label'):
                        entities.append({
                            "text": ' '.join([token for token, pos in chunk.leaves()]),
                            "label": chunk.label(),
                            "confidence": 0.7
                        })
                
                result = {
                    "entities": entities,
                    "entity_count": len(entities),
                    "model_info": {
                        "model": "NLTK NER",
                        "type": "rule_based"
                    }
                }
            
            return result
            
        except Exception as e:
            self.logger.error(f"Error extracting named entities: {e}")
            raise
    
    async def _summarize_text(self, request: NLPRequest) -> Dict[str, Any]:
        """Resumir texto"""
        try:
            text = request.text
            
            # Tokenizar en oraciones
            sentences = sent_tokenize(text)
            
            # Calcular puntuación de oraciones
            sentence_scores = []
            for sentence in sentences:
                # Puntuación basada en frecuencia de palabras
                words = word_tokenize(sentence.lower())
                words = [word for word in words if word.isalnum() and word not in self.stop_words]
                
                # Calcular frecuencia de palabras
                word_freq = {}
                for word in words:
                    word_freq[word] = word_freq.get(word, 0) + 1
                
                # Puntuación de la oración
                score = sum(word_freq.values()) / len(words) if words else 0
                sentence_scores.append(score)
            
            # Seleccionar oraciones con mayor puntuación
            num_sentences = min(len(sentences), max(1, len(sentences) // 3))
            top_sentences = sorted(range(len(sentences)), key=lambda i: sentence_scores[i], reverse=True)[:num_sentences]
            
            # Ordenar oraciones por posición original
            top_sentences.sort()
            summary = ' '.join([sentences[i] for i in top_sentences])
            
            result = {
                "summary": summary,
                "original_length": len(text),
                "summary_length": len(summary),
                "compression_ratio": len(summary) / len(text),
                "sentences_used": len(top_sentences),
                "total_sentences": len(sentences),
                "model_info": {
                    "model": "Extractive Summarization",
                    "type": "rule_based"
                }
            }
            
            return result
            
        except Exception as e:
            self.logger.error(f"Error summarizing text: {e}")
            raise
    
    async def _detect_language(self, request: NLPRequest) -> Dict[str, Any]:
        """Detectar idioma del texto"""
        try:
            text = request.text
            
            # Detección simple basada en caracteres
            languages = {
                'en': 'abcdefghijklmnopqrstuvwxyz',
                'es': 'abcdefghijklmnopqrstuvwxyzñáéíóúü',
                'fr': 'abcdefghijklmnopqrstuvwxyzàâäéèêëïîôöùûüÿç',
                'de': 'abcdefghijklmnopqrstuvwxyzäöüß',
                'it': 'abcdefghijklmnopqrstuvwxyzàèéìíîòóùú',
                'pt': 'abcdefghijklmnopqrstuvwxyzàáâãéêíóôõúç',
                'ru': 'абвгдеёжзийклмнопрстуфхцчшщъыьэюя',
                'zh': '的一是了我不人在他有这个上们来到时大地为子中你说生国年着就那和要她出也得里后自以会家可下而过天去能对小多然于心学么之都好看起发当没成只如事把还用第样道想作种开',
                'ja': 'あいうえおかきくけこさしすせそたちつてとなにぬねのはひふへほまみむめもやゆよらりるれろわをん',
                'ko': '가나다라마바사아자차카타파하거너더러머버서어저처커터퍼허고노도로모보소오조초코토포호구누두루무부수우주추쿠투푸후그느드르므브스으즈츠크트프흐기니디리미비시이지치키티피히'
            }
            
            # Contar caracteres por idioma
            language_scores = {}
            for lang, chars in languages.items():
                score = sum(1 for char in text.lower() if char in chars)
                language_scores[lang] = score / len(text) if text else 0
            
            # Determinar idioma más probable
            detected_language = max(language_scores, key=language_scores.get)
            confidence = language_scores[detected_language]
            
            result = {
                "language": detected_language,
                "confidence": confidence,
                "language_scores": language_scores,
                "model_info": {
                    "model": "Character-based Language Detection",
                    "type": "rule_based"
                }
            }
            
            return result
            
        except Exception as e:
            self.logger.error(f"Error detecting language: {e}")
            raise
    
    async def _extract_keywords(self, request: NLPRequest) -> Dict[str, Any]:
        """Extraer palabras clave"""
        try:
            text = request.text
            
            # Preprocesar texto
            words = word_tokenize(text.lower())
            words = [word for word in words if word.isalnum() and word not in self.stop_words and len(word) > 2]
            
            # Calcular frecuencia de palabras
            word_freq = {}
            for word in words:
                word_freq[word] = word_freq.get(word, 0) + 1
            
            # Ordenar por frecuencia
            sorted_words = sorted(word_freq.items(), key=lambda x: x[1], reverse=True)
            
            # Seleccionar top keywords
            num_keywords = request.parameters.get("num_keywords", 10) if request.parameters else 10
            top_keywords = sorted_words[:num_keywords]
            
            # Calcular scores normalizados
            max_freq = max(word_freq.values()) if word_freq else 1
            keywords = []
            for word, freq in top_keywords:
                keywords.append({
                    "word": word,
                    "frequency": freq,
                    "score": freq / max_freq
                })
            
            result = {
                "keywords": keywords,
                "total_keywords": len(keywords),
                "model_info": {
                    "model": "Frequency-based Keyword Extraction",
                    "type": "rule_based"
                }
            }
            
            return result
            
        except Exception as e:
            self.logger.error(f"Error extracting keywords: {e}")
            raise
    
    async def _model_topics(self, request: NLPRequest) -> Dict[str, Any]:
        """Modelado de temas"""
        try:
            text = request.text
            
            # Dividir texto en documentos (oraciones)
            documents = sent_tokenize(text)
            
            # Preprocesar documentos
            processed_docs = []
            for doc in documents:
                words = word_tokenize(doc.lower())
                words = [word for word in words if word.isalnum() and word not in self.stop_words and len(word) > 2]
                processed_docs.append(' '.join(words))
            
            # Vectorizar documentos
            vectorizer = TfidfVectorizer(max_features=100, stop_words='english')
            doc_term_matrix = vectorizer.fit_transform(processed_docs)
            
            # Aplicar clustering simple (K-means)
            from sklearn.cluster import KMeans
            
            num_topics = request.parameters.get("num_topics", 3) if request.parameters else 3
            kmeans = KMeans(n_clusters=num_topics, random_state=42)
            kmeans.fit(doc_term_matrix)
            
            # Obtener temas
            feature_names = vectorizer.get_feature_names_out()
            topics = []
            for i, center in enumerate(kmeans.cluster_centers_):
                top_words_idx = center.argsort()[-5:][::-1]
                top_words = [feature_names[idx] for idx in top_words_idx]
                topics.append({
                    "topic_id": i,
                    "top_words": top_words,
                    "weight": center[top_words_idx[0]]
                })
            
            result = {
                "topics": topics,
                "num_topics": num_topics,
                "model_info": {
                    "model": "K-means Topic Modeling",
                    "type": "machine_learning"
                }
            }
            
            return result
            
        except Exception as e:
            self.logger.error(f"Error modeling topics: {e}")
            raise
    
    async def _calculate_text_similarity(self, request: NLPRequest) -> Dict[str, Any]:
        """Calcular similitud de texto"""
        try:
            text1 = request.text
            text2 = request.context.get("compare_text", "") if request.context else ""
            
            if not text2:
                raise ValueError("Compare text is required for similarity calculation")
            
            # Preprocesar textos
            def preprocess_text(text):
                words = word_tokenize(text.lower())
                words = [word for word in words if word.isalnum() and word not in self.stop_words]
                return ' '.join(words)
            
            processed_text1 = preprocess_text(text1)
            processed_text2 = preprocess_text(text2)
            
            # Calcular similitud coseno
            vectorizer = TfidfVectorizer()
            tfidf_matrix = vectorizer.fit_transform([processed_text1, processed_text2])
            
            from sklearn.metrics.pairwise import cosine_similarity
            similarity = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])[0][0]
            
            result = {
                "similarity": similarity,
                "similarity_percentage": similarity * 100,
                "text1_length": len(text1),
                "text2_length": len(text2),
                "model_info": {
                    "model": "TF-IDF Cosine Similarity",
                    "type": "machine_learning"
                }
            }
            
            return result
            
        except Exception as e:
            self.logger.error(f"Error calculating text similarity: {e}")
            raise
    
    async def _answer_question(self, request: NLPRequest) -> Dict[str, Any]:
        """Responder preguntas"""
        try:
            question = request.text
            context = request.context.get("context", "") if request.context else ""
            
            if not context:
                raise ValueError("Context is required for question answering")
            
            # Respuesta simple basada en coincidencias de palabras
            question_words = set(word_tokenize(question.lower()))
            context_sentences = sent_tokenize(context)
            
            # Encontrar oración más relevante
            best_sentence = ""
            best_score = 0
            
            for sentence in context_sentences:
                sentence_words = set(word_tokenize(sentence.lower()))
                score = len(question_words.intersection(sentence_words))
                if score > best_score:
                    best_score = score
                    best_sentence = sentence
            
            # Si no se encuentra respuesta relevante, usar primera oración
            if not best_sentence:
                best_sentence = context_sentences[0] if context_sentences else "No answer found."
            
            result = {
                "answer": best_sentence,
                "confidence": best_score / len(question_words) if question_words else 0,
                "context_used": best_sentence,
                "model_info": {
                    "model": "Word Matching QA",
                    "type": "rule_based"
                }
            }
            
            return result
            
        except Exception as e:
            self.logger.error(f"Error answering question: {e}")
            raise
    
    async def _generate_text(self, request: NLPRequest) -> Dict[str, Any]:
        """Generar texto"""
        try:
            prompt = request.text
            
            # Generación simple basada en plantillas
            templates = {
                "hello": "Hello! How can I help you today?",
                "thank": "You're welcome! Is there anything else I can assist you with?",
                "goodbye": "Goodbye! Have a great day!",
                "help": "I'm here to help! You can ask me questions, analyze text, or perform various NLP tasks.",
                "default": "I understand you're looking for assistance. How can I help you today?"
            }
            
            # Buscar plantilla más relevante
            prompt_lower = prompt.lower()
            response = templates["default"]
            
            for key, template in templates.items():
                if key in prompt_lower:
                    response = template
                    break
            
            result = {
                "generated_text": response,
                "prompt": prompt,
                "confidence": 0.8,
                "model_info": {
                    "model": "Template-based Text Generation",
                    "type": "rule_based"
                }
            }
            
            return result
            
        except Exception as e:
            self.logger.error(f"Error generating text: {e}")
            raise
    
    async def _create_synthetic_training_data(self, categories: List[str]) -> Dict[str, List[str]]:
        """Crear datos de entrenamiento sintéticos"""
        try:
            # Datos de ejemplo para cada categoría
            synthetic_data = {
                "positive": [
                    "This is amazing! I love it!",
                    "Great product, highly recommended!",
                    "Excellent service, thank you!",
                    "Perfect! Exactly what I needed.",
                    "Outstanding quality and value."
                ],
                "negative": [
                    "This is terrible! I hate it!",
                    "Poor quality, not recommended.",
                    "Bad service, very disappointed.",
                    "Waste of money, avoid this.",
                    "Worst experience ever."
                ],
                "neutral": [
                    "This is okay, nothing special.",
                    "Average product, meets expectations.",
                    "Standard service, as expected.",
                    "It's fine, nothing to complain about.",
                    "Normal quality, typical for the price."
                ]
            }
            
            # Filtrar categorías disponibles
            available_categories = [cat for cat in categories if cat in synthetic_data]
            
            # Crear datos de entrenamiento
            training_texts = []
            training_labels = []
            
            for category in available_categories:
                for text in synthetic_data[category]:
                    training_texts.append(text)
                    training_labels.append(category)
            
            return {
                "text": training_texts,
                "label": training_labels
            }
            
        except Exception as e:
            self.logger.error(f"Error creating synthetic training data: {e}")
            raise
    
    async def _create_lstm_classifier(self, categories: List[str]) -> Model:
        """Crear clasificador LSTM"""
        try:
            model = Sequential([
                Embedding(self.default_config["vocabulary_size"], self.default_config["embedding_dim"], input_length=self.default_config["max_sequence_length"]),
                LSTM(128, dropout=0.2, recurrent_dropout=0.2),
                Dense(64, activation='relu'),
                Dropout(0.2),
                Dense(len(categories), activation='softmax')
            ])
            
            model.compile(
                optimizer=Adam(learning_rate=self.default_config["learning_rate"]),
                loss='categorical_crossentropy',
                metrics=['accuracy']
            )
            
            return model
            
        except Exception as e:
            self.logger.error(f"Error creating LSTM classifier: {e}")
            raise
    
    async def _save_processing_history(self, request: NLPRequest, result: NLPResult) -> None:
        """Guardar historial de procesamiento"""
        try:
            processing_id = f"nlp_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            
            self.processing_history[processing_id] = {
                "timestamp": datetime.now().isoformat(),
                "task_type": request.task_type.value,
                "model_type": request.model_type.value,
                "language": request.language,
                "text_length": len(request.text),
                "processing_time": result.processing_time,
                "confidence": result.confidence,
                "model_info": result.model_info
            }
            
        except Exception as e:
            self.logger.error(f"Error saving processing history: {e}")
    
    async def get_nlp_insights(self) -> Dict[str, Any]:
        """Obtener insights de NLP"""
        insights = {
            "total_processing": len(self.processing_history),
            "task_types_used": {},
            "model_types_used": {},
            "languages_processed": {},
            "average_processing_time": 0.0,
            "average_confidence": 0.0,
            "recent_processing": []
        }
        
        if self.processing_history:
            # Análisis de tipos de tarea
            for processing in self.processing_history.values():
                task_type = processing["task_type"]
                insights["task_types_used"][task_type] = insights["task_types_used"].get(task_type, 0) + 1
                
                model_type = processing["model_type"]
                insights["model_types_used"][model_type] = insights["model_types_used"].get(model_type, 0) + 1
                
                language = processing["language"]
                insights["languages_processed"][language] = insights["languages_processed"].get(language, 0) + 1
            
            # Promedios
            processing_times = [p["processing_time"] for p in self.processing_history.values()]
            confidences = [p["confidence"] for p in self.processing_history.values()]
            
            insights["average_processing_time"] = np.mean(processing_times) if processing_times else 0.0
            insights["average_confidence"] = np.mean(confidences) if confidences else 0.0
            
            # Procesamiento reciente
            recent_processing = sorted(self.processing_history.items(), key=lambda x: x[1]["timestamp"], reverse=True)[:5]
            insights["recent_processing"] = [
                {
                    "id": processing_id,
                    "task_type": processing["task_type"],
                    "timestamp": processing["timestamp"],
                    "processing_time": processing["processing_time"]
                }
                for processing_id, processing in recent_processing
            ]
        
        return insights

# Función principal para inicializar el motor
async def initialize_nlp_engine() -> AdvancedNLPEngine:
    """Inicializar motor de NLP avanzado"""
    engine = AdvancedNLPEngine()
    
    # Configurar logging
    logging.basicConfig(level=logging.INFO)
    
    return engine

if __name__ == "__main__":
    # Ejemplo de uso
    async def main():
        engine = await initialize_nlp_engine()
        
        # Ejemplo de análisis de sentimientos
        sentiment_request = NLPRequest(
            text="I love this product! It's amazing and works perfectly.",
            task_type=NLPTaskType.SENTIMENT_ANALYSIS,
            model_type=NLPModelType.RULE_BASED
        )
        
        sentiment_result = await engine.process_text(sentiment_request)
        print("Sentiment Analysis Result:")
        print(f"Sentiment: {sentiment_result.result['sentiment']}")
        print(f"Confidence: {sentiment_result.confidence}")
        print(f"Processing time: {sentiment_result.processing_time}")
        
        # Ejemplo de extracción de palabras clave
        keyword_request = NLPRequest(
            text="Machine learning and artificial intelligence are transforming the world of technology and business.",
            task_type=NLPTaskType.KEYWORD_EXTRACTION,
            model_type=NLPModelType.RULE_BASED,
            parameters={"num_keywords": 5}
        )
        
        keyword_result = await engine.process_text(keyword_request)
        print("\nKeyword Extraction Result:")
        print(f"Keywords: {[kw['word'] for kw in keyword_result.result['keywords']]}")
        
        # Obtener insights
        insights = await engine.get_nlp_insights()
        print("\nNLP Insights:", json.dumps(insights, indent=2, default=str))
    
    asyncio.run(main())



