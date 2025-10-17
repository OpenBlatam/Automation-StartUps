#!/usr/bin/env python3
"""
Sistema de Inteligencia Artificial Avanzada con Procesamiento de Lenguaje Natural
"""

import os
import json
import sqlite3
import re
import random
from datetime import datetime
from collections import Counter
import math

class AdvancedAISystem:
    def __init__(self, base_path="/Users/adan/frontier"):
        self.base_path = base_path
        self.ai_db = os.path.join(base_path, "advanced_ai.db")
        self.business_areas = [
            '01_Marketing', '02_Finance', '03_Human_Resources', '04_Operations',
            '05_Technology', '06_Strategy', '07_Risk_Management', '08_AI_Artificial_Intelligence',
            '09_Sales', '10_Customer_Service', '11_Research_Development', '12_Quality_Assurance',
            '13_Legal_Compliance', '14_Procurement', '15_Logistics', '16_Data_Analytics',
            '17_Innovation', '18_Sustainability', '19_International_Business', '20_Project_Management'
        ]
        self.init_ai_database()
        self.load_knowledge_base()
    
    def init_ai_database(self):
        """Inicializar base de datos de IA"""
        conn = sqlite3.connect(self.ai_db)
        cursor = conn.cursor()
        
        # Tabla de conocimiento
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS ai_knowledge (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                concept TEXT,
                definition TEXT,
                category TEXT,
                confidence REAL,
                created_at TEXT,
                updated_at TEXT
            )
        ''')
        
        # Tabla de patrones de lenguaje
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS language_patterns (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                pattern TEXT,
                intent TEXT,
                response_template TEXT,
                confidence REAL,
                usage_count INTEGER DEFAULT 0
            )
        ''')
        
        # Tabla de análisis semántico
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS semantic_analysis (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                text_content TEXT,
                sentiment_score REAL,
                entities TEXT,
                topics TEXT,
                keywords TEXT,
                analysis_date TEXT
            )
        ''')
        
        # Tabla de recomendaciones
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS ai_recommendations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id TEXT,
                recommendation_type TEXT,
                content TEXT,
                confidence REAL,
                created_at TEXT,
                is_accepted BOOLEAN DEFAULT NULL
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def load_knowledge_base(self):
        """Cargar base de conocimiento"""
        conn = sqlite3.connect(self.ai_db)
        cursor = conn.cursor()
        
        # Conocimiento empresarial básico
        knowledge_items = [
            ('marketing', 'Estrategias para promocionar productos y servicios', 'business', 0.9),
            ('finanzas', 'Gestión de recursos financieros y presupuestos', 'business', 0.9),
            ('recursos_humanos', 'Gestión de personal y talento humano', 'business', 0.9),
            ('operaciones', 'Procesos operativos y eficiencia', 'business', 0.9),
            ('tecnologia', 'Innovación tecnológica y digitalización', 'business', 0.9),
            ('estrategia', 'Planificación estratégica y visión empresarial', 'business', 0.9),
            ('riesgo', 'Gestión de riesgos y compliance', 'business', 0.9),
            ('ventas', 'Procesos de venta y relación con clientes', 'business', 0.9),
            ('atencion_cliente', 'Servicio al cliente y satisfacción', 'business', 0.9),
            ('investigacion', 'I+D y desarrollo de productos', 'business', 0.9)
        ]
        
        for concept, definition, category, confidence in knowledge_items:
            cursor.execute('''
                INSERT OR IGNORE INTO ai_knowledge 
                (concept, definition, category, confidence, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (concept, definition, category, confidence, 
                  datetime.now().isoformat(), datetime.now().isoformat()))
        
        # Patrones de lenguaje
        language_patterns = [
            ('buscar.*documento', 'search', 'Te ayudo a buscar documentos relacionados con: {query}', 0.8),
            ('organizar.*archivo', 'organize', 'Procedo a organizar los archivos según las mejores prácticas', 0.9),
            ('analizar.*contenido', 'analyze', 'Analizando el contenido para extraer insights clave', 0.8),
            ('recomendar.*acción', 'recommend', 'Basándome en el análisis, te recomiendo: {recommendation}', 0.7),
            ('crear.*reporte', 'report', 'Generando reporte personalizado con métricas relevantes', 0.9),
            ('optimizar.*proceso', 'optimize', 'Identificando oportunidades de optimización en el proceso', 0.8),
            ('predecir.*tendencia', 'predict', 'Utilizando modelos predictivos para analizar tendencias', 0.7),
            ('clasificar.*información', 'classify', 'Clasificando información según categorías empresariales', 0.9)
        ]
        
        for pattern, intent, response, confidence in language_patterns:
            cursor.execute('''
                INSERT OR IGNORE INTO language_patterns 
                (pattern, intent, response_template, confidence)
                VALUES (?, ?, ?, ?)
            ''', (pattern, intent, response, confidence))
        
        conn.commit()
        conn.close()
    
    def analyze_sentiment(self, text):
        """Análisis de sentimiento del texto"""
        positive_words = ['bueno', 'excelente', 'genial', 'fantástico', 'increíble', 'perfecto', 'óptimo', 'mejor', 'superior', 'destacado']
        negative_words = ['malo', 'terrible', 'horrible', 'pésimo', 'deficiente', 'problema', 'error', 'fallo', 'crítico', 'urgente']
        
        words = re.findall(r'\b\w+\b', text.lower())
        positive_count = sum(1 for word in words if word in positive_words)
        negative_count = sum(1 for word in words if word in negative_words)
        
        total_words = len(words)
        if total_words == 0:
            return 0.0
        
        sentiment_score = (positive_count - negative_count) / total_words
        return max(-1.0, min(1.0, sentiment_score))
    
    def extract_entities(self, text):
        """Extraer entidades del texto"""
        entities = []
        
        # Patrones para entidades empresariales
        patterns = {
            'personas': r'\b[A-Z][a-z]+ [A-Z][a-z]+\b',
            'empresas': r'\b[A-Z][a-z]+ (?:Inc|Corp|LLC|Ltd|S\.A\.|S\.L\.)\b',
            'fechas': r'\b\d{1,2}[/-]\d{1,2}[/-]\d{2,4}\b',
            'montos': r'\$\d+(?:,\d{3})*(?:\.\d{2})?',
            'porcentajes': r'\d+(?:\.\d+)?%',
            'emails': r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',
            'telefonos': r'\b\d{3}[-.]?\d{3}[-.]?\d{4}\b'
        }
        
        for entity_type, pattern in patterns.items():
            matches = re.findall(pattern, text)
            entities.extend([(match, entity_type) for match in matches])
        
        return entities
    
    def extract_keywords(self, text, top_n=10):
        """Extraer palabras clave del texto"""
        # Palabras de parada en español
        stop_words = {'el', 'la', 'de', 'que', 'y', 'a', 'en', 'un', 'es', 'se', 'no', 'te', 'lo', 'le', 'da', 'su', 'por', 'son', 'con', 'para', 'al', 'del', 'los', 'las', 'una', 'como', 'más', 'pero', 'sus', 'le', 'ha', 'me', 'si', 'sin', 'sobre', 'este', 'ya', 'entre', 'cuando', 'todo', 'esta', 'ser', 'son', 'dos', 'también', 'fue', 'había', 'era', 'muy', 'años', 'hasta', 'desde', 'está', 'mi', 'porque', 'qué', 'sólo', 'han', 'yo', 'hay', 'vez', 'puede', 'todos', 'así', 'nos', 'ni', 'parte', 'tiene', 'él', 'uno', 'donde', 'bien', 'tiempo', 'mismo', 'ese', 'ahora', 'cada', 'e', 'vida', 'otro', 'después', 'te', 'otros', 'aunque', 'esa', 'esos', 'otra', 'esas', 'poco', 'él', 'todas', 'menos', 'año', 'antes', 'estos', 'estas', 'cual', 'mientras', 'además', 'primer', 'lugar', 'general', 'mejor', 'nuevo', 'siguiente', 'cerca', 'tanto', 'nunca', 'siempre', 'tampoco', 'nada', 'algo', 'todo', 'todos', 'todas', 'cualquier', 'cualquiera', 'algunos', 'algunas', 'varios', 'varias', 'muchos', 'muchas', 'pocos', 'pocas', 'todos', 'todas', 'ninguno', 'ninguna', 'nadie', 'nada', 'algo', 'todo', 'todos', 'todas'}
        
        words = re.findall(r'\b\w+\b', text.lower())
        filtered_words = [word for word in words if word not in stop_words and len(word) > 2]
        
        word_freq = Counter(filtered_words)
        return word_freq.most_common(top_n)
    
    def classify_intent(self, text):
        """Clasificar intención del usuario"""
        conn = sqlite3.connect(self.ai_db)
        cursor = conn.cursor()
        
        cursor.execute('SELECT pattern, intent, response_template, confidence FROM language_patterns')
        patterns = cursor.fetchall()
        
        best_match = None
        best_confidence = 0
        
        for pattern, intent, response_template, confidence in patterns:
            if re.search(pattern, text.lower()):
                if confidence > best_confidence:
                    best_confidence = confidence
                    best_match = (intent, response_template, confidence)
        
        conn.close()
        
        if best_match:
            return {
                'intent': best_match[0],
                'response_template': best_match[1],
                'confidence': best_match[2]
            }
        
        return {
            'intent': 'unknown',
            'response_template': 'No estoy seguro de cómo ayudarte con eso. ¿Podrías ser más específico?',
            'confidence': 0.0
        }
    
    def generate_recommendations(self, user_id, context_data):
        """Generar recomendaciones personalizadas"""
        recommendations = []
        
        # Análisis de contexto
        if 'search_queries' in context_data:
            queries = context_data['search_queries']
            if len(queries) > 5:
                recommendations.append({
                    'type': 'organization',
                    'content': 'Considera organizar mejor tus búsquedas usando filtros específicos',
                    'confidence': 0.8
                })
        
        if 'document_count' in context_data:
            doc_count = context_data['document_count']
            if doc_count > 100:
                recommendations.append({
                    'type': 'backup',
                    'content': 'Te recomiendo hacer backup de tus documentos importantes',
                    'confidence': 0.9
                })
        
        if 'areas_activity' in context_data:
            active_areas = context_data['areas_activity']
            if len(active_areas) < 3:
                recommendations.append({
                    'type': 'exploration',
                    'content': 'Explora otras áreas de negocio para diversificar tu conocimiento',
                    'confidence': 0.7
                })
        
        # Guardar recomendaciones
        conn = sqlite3.connect(self.ai_db)
        cursor = conn.cursor()
        
        for rec in recommendations:
            cursor.execute('''
                INSERT INTO ai_recommendations 
                (user_id, recommendation_type, content, confidence, created_at)
                VALUES (?, ?, ?, ?, ?)
            ''', (user_id, rec['type'], rec['content'], rec['confidence'], datetime.now().isoformat()))
        
        conn.commit()
        conn.close()
        
        return recommendations
    
    def process_natural_language(self, user_input):
        """Procesar lenguaje natural del usuario"""
        # Análisis semántico
        sentiment = self.analyze_sentiment(user_input)
        entities = self.extract_entities(user_input)
        keywords = self.extract_keywords(user_input)
        
        # Clasificar intención
        intent_analysis = self.classify_intent(user_input)
        
        # Guardar análisis
        conn = sqlite3.connect(self.ai_db)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO semantic_analysis 
            (text_content, sentiment_score, entities, topics, keywords, analysis_date)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (user_input, sentiment, json.dumps(entities), 
              json.dumps(keywords[:5]), json.dumps(keywords), datetime.now().isoformat()))
        
        conn.commit()
        conn.close()
        
        return {
            'sentiment': sentiment,
            'entities': entities,
            'keywords': keywords,
            'intent': intent_analysis['intent'],
            'response_template': intent_analysis['response_template'],
            'confidence': intent_analysis['confidence']
        }
    
    def generate_intelligent_response(self, user_input, context=None):
        """Generar respuesta inteligente"""
        analysis = self.process_natural_language(user_input)
        
        # Generar respuesta basada en análisis
        if analysis['intent'] == 'search':
            response = f"🔍 {analysis['response_template'].format(query=user_input)}"
        elif analysis['intent'] == 'organize':
            response = f"📁 {analysis['response_template']}"
        elif analysis['intent'] == 'analyze':
            response = f"📊 {analysis['response_template']}"
        elif analysis['intent'] == 'recommend':
            response = f"💡 {analysis['response_template'].format(recommendation='Revisar documentación actualizada')}"
        else:
            response = f"🤖 {analysis['response_template']}"
        
        # Agregar información contextual
        if analysis['sentiment'] > 0.3:
            response += " 😊"
        elif analysis['sentiment'] < -0.3:
            response += " 😟"
        
        if analysis['entities']:
            response += f"\n📋 Entidades detectadas: {', '.join([e[0] for e in analysis['entities'][:3]])}"
        
        return response
    
    def get_ai_insights(self):
        """Obtener insights de IA"""
        conn = sqlite3.connect(self.ai_db)
        cursor = conn.cursor()
        
        # Estadísticas de análisis semántico
        cursor.execute('SELECT COUNT(*) FROM semantic_analysis')
        total_analyses = cursor.fetchone()[0]
        
        cursor.execute('SELECT AVG(sentiment_score) FROM semantic_analysis')
        avg_sentiment = cursor.fetchone()[0] or 0
        
        cursor.execute('SELECT COUNT(*) FROM ai_recommendations')
        total_recommendations = cursor.fetchone()[0]
        
        cursor.execute('SELECT COUNT(*) FROM ai_recommendations WHERE is_accepted = 1')
        accepted_recommendations = cursor.fetchone()[0]
        
        # Patrones más utilizados
        cursor.execute('''
            SELECT intent, COUNT(*) as usage_count
            FROM language_patterns lp
            JOIN semantic_analysis sa ON sa.text_content LIKE '%' || lp.pattern || '%'
            GROUP BY intent
            ORDER BY usage_count DESC
        ''')
        popular_intents = cursor.fetchall()
        
        conn.close()
        
        return {
            'total_analyses': total_analyses,
            'avg_sentiment': avg_sentiment,
            'total_recommendations': total_recommendations,
            'accepted_recommendations': accepted_recommendations,
            'acceptance_rate': accepted_recommendations / max(total_recommendations, 1) * 100,
            'popular_intents': popular_intents
        }

def main():
    ai_system = AdvancedAISystem()
    
    print("🤖 Sistema de Inteligencia Artificial Avanzada")
    print("=" * 50)
    print("1. Procesar lenguaje natural")
    print("2. Generar recomendaciones")
    print("3. Análisis semántico")
    print("4. Chat inteligente")
    print("5. Ver insights de IA")
    print("6. Salir")
    
    while True:
        choice = input("\nSeleccione una opción (1-6): ").strip()
        
        if choice == '1':
            text = input("Ingrese texto para análisis: ").strip()
            if text:
                analysis = ai_system.process_natural_language(text)
                print(f"\n📊 Análisis del texto:")
                print(f"  😊 Sentimiento: {analysis['sentiment']:.2f}")
                print(f"  🎯 Intención: {analysis['intent']}")
                print(f"  📈 Confianza: {analysis['confidence']:.2f}")
                print(f"  🔑 Palabras clave: {', '.join([kw[0] for kw in analysis['keywords'][:5]])}")
                if analysis['entities']:
                    print(f"  📋 Entidades: {', '.join([e[0] for e in analysis['entities'][:3]])}")
        
        elif choice == '2':
            user_id = input("ID de usuario: ").strip()
            context = {
                'search_queries': ['marketing', 'ventas', 'finanzas', 'tecnología', 'recursos humanos'],
                'document_count': 150,
                'areas_activity': ['01_Marketing', '02_Finance']
            }
            
            recommendations = ai_system.generate_recommendations(user_id, context)
            print(f"\n💡 Recomendaciones generadas:")
            for i, rec in enumerate(recommendations, 1):
                print(f"  {i}. [{rec['type']}] {rec['content']} (Confianza: {rec['confidence']:.1f})")
        
        elif choice == '3':
            text = input("Texto para análisis semántico: ").strip()
            if text:
                analysis = ai_system.process_natural_language(text)
                print(f"\n🧠 Análisis Semántico:")
                print(f"  Sentimiento: {analysis['sentiment']:.3f}")
                print(f"  Entidades encontradas: {len(analysis['entities'])}")
                print(f"  Palabras clave: {len(analysis['keywords'])}")
                print(f"  Intención detectada: {analysis['intent']}")
        
        elif choice == '4':
            print("\n🤖 Chat Inteligente (escriba 'salir' para terminar)")
            while True:
                user_input = input("\n👤 Usted: ").strip()
                if user_input.lower() in ['salir', 'exit', 'quit']:
                    break
                
                response = ai_system.generate_intelligent_response(user_input)
                print(f"🤖 IA: {response}")
        
        elif choice == '5':
            insights = ai_system.get_ai_insights()
            print(f"\n📊 Insights de IA:")
            print(f"  🔍 Análisis realizados: {insights['total_analyses']}")
            print(f"  😊 Sentimiento promedio: {insights['avg_sentiment']:.2f}")
            print(f"  💡 Recomendaciones generadas: {insights['total_recommendations']}")
            print(f"  ✅ Tasa de aceptación: {insights['acceptance_rate']:.1f}%")
            
            if insights['popular_intents']:
                print(f"\n🔥 Intenciones más populares:")
                for intent, count in insights['popular_intents']:
                    print(f"  • {intent}: {count} veces")
        
        elif choice == '6':
            print("👋 ¡Hasta luego!")
            break
        
        else:
            print("❌ Opción no válida")

if __name__ == "__main__":
    main()



