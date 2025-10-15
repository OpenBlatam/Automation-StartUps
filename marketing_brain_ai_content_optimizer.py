"""
Marketing Brain AI Content Optimizer
Motor avanzado de optimización de contenido con IA
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import json
import re
from textblob import TextBlob
from sklearn.feature_extraction.text import TfidfVectorizer, CountVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.cluster import KMeans
from sklearn.decomposition import LatentDirichletAllocation
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import warnings
warnings.filterwarnings('ignore')

class AIContentOptimizer:
    def __init__(self):
        self.content_database = {}
        self.optimization_models = {}
        self.performance_metrics = {}
        self.content_templates = {}
        self.seo_analysis = {}
        self.readability_scores = {}
        self.engagement_predictions = {}
        
    def analyze_content_quality(self, content, content_type='blog_post'):
        """Analizar calidad del contenido"""
        if not content or not isinstance(content, str):
            return None
        
        # Análisis básico del contenido
        word_count = len(content.split())
        char_count = len(content)
        sentence_count = len(re.split(r'[.!?]+', content))
        paragraph_count = len(content.split('\n\n'))
        
        # Análisis de legibilidad
        readability_score = self._calculate_readability(content)
        
        # Análisis de SEO
        seo_score = self._calculate_seo_score(content, content_type)
        
        # Análisis de engagement
        engagement_score = self._calculate_engagement_score(content)
        
        # Análisis de sentimiento
        sentiment_score = self._analyze_content_sentiment(content)
        
        # Análisis de keywords
        keyword_analysis = self._analyze_keywords(content)
        
        # Análisis de estructura
        structure_score = self._analyze_content_structure(content)
        
        quality_analysis = {
            'content': content,
            'content_type': content_type,
            'timestamp': datetime.now().isoformat(),
            'basic_metrics': {
                'word_count': word_count,
                'char_count': char_count,
                'sentence_count': sentence_count,
                'paragraph_count': paragraph_count,
                'avg_words_per_sentence': word_count / sentence_count if sentence_count > 0 else 0
            },
            'readability_score': readability_score,
            'seo_score': seo_score,
            'engagement_score': engagement_score,
            'sentiment_score': sentiment_score,
            'keyword_analysis': keyword_analysis,
            'structure_score': structure_score,
            'overall_quality_score': self._calculate_overall_quality_score(
                readability_score, seo_score, engagement_score, structure_score
            )
        }
        
        return quality_analysis
    
    def _calculate_readability(self, content):
        """Calcular score de legibilidad"""
        # Fórmula simplificada de Flesch Reading Ease
        sentences = re.split(r'[.!?]+', content)
        words = content.split()
        syllables = sum(self._count_syllables(word) for word in words)
        
        if len(sentences) == 0 or len(words) == 0:
            return 0
        
        avg_sentence_length = len(words) / len(sentences)
        avg_syllables_per_word = syllables / len(words)
        
        # Fórmula de Flesch Reading Ease
        readability_score = 206.835 - (1.015 * avg_sentence_length) - (84.6 * avg_syllables_per_word)
        
        # Normalizar a 0-100
        return max(0, min(100, readability_score))
    
    def _count_syllables(self, word):
        """Contar sílabas en una palabra"""
        word = word.lower()
        vowels = 'aeiouy'
        syllable_count = 0
        prev_was_vowel = False
        
        for char in word:
            if char in vowels:
                if not prev_was_vowel:
                    syllable_count += 1
                prev_was_vowel = True
            else:
                prev_was_vowel = False
        
        # Ajustar para palabras que terminan en 'e'
        if word.endswith('e') and syllable_count > 1:
            syllable_count -= 1
        
        return max(1, syllable_count)
    
    def _calculate_seo_score(self, content, content_type):
        """Calcular score de SEO"""
        seo_score = 0
        
        # Análisis de densidad de keywords
        words = content.lower().split()
        word_freq = {}
        for word in words:
            word_freq[word] = word_freq.get(word, 0) + 1
        
        # Keywords más frecuentes
        top_keywords = sorted(word_freq.items(), key=lambda x: x[1], reverse=True)[:10]
        
        # Score por densidad de keywords (1-3% es óptimo)
        for keyword, freq in top_keywords:
            density = freq / len(words) * 100
            if 1 <= density <= 3:
                seo_score += 10
            elif density > 3:
                seo_score += 5  # Penalizar por sobre-optimización
        
        # Análisis de estructura
        if content_type == 'blog_post':
            # Verificar presencia de headings
            if re.search(r'#+\s+', content):  # Markdown headings
                seo_score += 15
            elif re.search(r'<h[1-6]>', content):  # HTML headings
                seo_score += 15
            
            # Verificar presencia de listas
            if re.search(r'[-*+]\s+', content) or re.search(r'\d+\.\s+', content):
                seo_score += 10
            
            # Verificar longitud del contenido (300+ palabras para SEO)
            if len(words) >= 300:
                seo_score += 20
            elif len(words) >= 150:
                seo_score += 10
        
        # Análisis de enlaces internos/externos
        internal_links = len(re.findall(r'\[.*?\]\(.*?\)', content))
        external_links = len(re.findall(r'https?://', content))
        
        if internal_links > 0:
            seo_score += min(15, internal_links * 5)
        if external_links > 0:
            seo_score += min(10, external_links * 3)
        
        return min(100, seo_score)
    
    def _calculate_engagement_score(self, content):
        """Calcular score de engagement"""
        engagement_score = 0
        
        # Análisis de palabras de poder
        power_words = [
            'amazing', 'incredible', 'fantastic', 'outstanding', 'excellent',
            'proven', 'guaranteed', 'exclusive', 'limited', 'secret',
            'free', 'new', 'best', 'top', 'ultimate', 'complete'
        ]
        
        content_lower = content.lower()
        power_word_count = sum(1 for word in power_words if word in content_lower)
        engagement_score += min(30, power_word_count * 5)
        
        # Análisis de preguntas
        question_count = len(re.findall(r'\?', content))
        engagement_score += min(20, question_count * 5)
        
        # Análisis de llamadas a la acción
        cta_words = ['click', 'download', 'subscribe', 'buy', 'get', 'learn', 'discover']
        cta_count = sum(1 for word in cta_words if word in content_lower)
        engagement_score += min(25, cta_count * 5)
        
        # Análisis de números específicos
        numbers = re.findall(r'\b\d+\b', content)
        if numbers:
            engagement_score += 10
        
        # Análisis de listas
        if re.search(r'[-*+]\s+', content) or re.search(r'\d+\.\s+', content):
            engagement_score += 15
        
        return min(100, engagement_score)
    
    def _analyze_content_sentiment(self, content):
        """Analizar sentimiento del contenido"""
        blob = TextBlob(content)
        polarity = blob.sentiment.polarity
        subjectivity = blob.sentiment.subjectivity
        
        # Score de sentimiento (0-100)
        sentiment_score = (polarity + 1) * 50  # Convertir de -1,1 a 0,100
        
        return {
            'polarity': polarity,
            'subjectivity': subjectivity,
            'sentiment_score': sentiment_score,
            'sentiment': 'positive' if polarity > 0.1 else 'negative' if polarity < -0.1 else 'neutral'
        }
    
    def _analyze_keywords(self, content):
        """Analizar keywords del contenido"""
        words = content.lower().split()
        
        # Remover palabras comunes
        stop_words = {
            'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for',
            'of', 'with', 'by', 'is', 'are', 'was', 'were', 'be', 'been', 'have',
            'has', 'had', 'do', 'does', 'did', 'will', 'would', 'could', 'should'
        }
        
        filtered_words = [word for word in words if word not in stop_words and len(word) > 2]
        
        # Frecuencia de palabras
        word_freq = {}
        for word in filtered_words:
            word_freq[word] = word_freq.get(word, 0) + 1
        
        # Top keywords
        top_keywords = sorted(word_freq.items(), key=lambda x: x[1], reverse=True)[:20]
        
        # Análisis de densidad
        keyword_density = {}
        total_words = len(filtered_words)
        for word, freq in top_keywords:
            density = freq / total_words * 100
            keyword_density[word] = {
                'frequency': freq,
                'density': density,
                'is_optimal': 1 <= density <= 3
            }
        
        return {
            'top_keywords': top_keywords,
            'keyword_density': keyword_density,
            'total_unique_words': len(word_freq),
            'total_filtered_words': total_words
        }
    
    def _analyze_content_structure(self, content):
        """Analizar estructura del contenido"""
        structure_score = 0
        
        # Análisis de párrafos
        paragraphs = content.split('\n\n')
        if len(paragraphs) > 1:
            structure_score += 20
        
        # Análisis de headings
        headings = re.findall(r'#+\s+', content)
        if headings:
            structure_score += 25
        
        # Análisis de listas
        lists = re.findall(r'[-*+]\s+', content)
        if lists:
            structure_score += 15
        
        # Análisis de longitud de párrafos
        avg_paragraph_length = len(content.split()) / len(paragraphs) if paragraphs else 0
        if 50 <= avg_paragraph_length <= 150:
            structure_score += 20
        elif 30 <= avg_paragraph_length <= 200:
            structure_score += 10
        
        # Análisis de transiciones
        transition_words = [
            'however', 'therefore', 'furthermore', 'moreover', 'additionally',
            'consequently', 'meanwhile', 'nevertheless', 'similarly', 'likewise'
        ]
        
        transition_count = sum(1 for word in transition_words if word in content.lower())
        structure_score += min(20, transition_count * 5)
        
        return min(100, structure_score)
    
    def _calculate_overall_quality_score(self, readability, seo, engagement, structure):
        """Calcular score general de calidad"""
        # Pesos para diferentes aspectos
        weights = {
            'readability': 0.25,
            'seo': 0.30,
            'engagement': 0.25,
            'structure': 0.20
        }
        
        overall_score = (
            readability * weights['readability'] +
            seo * weights['seo'] +
            engagement * weights['engagement'] +
            structure * weights['structure']
        )
        
        return round(overall_score, 2)
    
    def optimize_content(self, content, target_metrics=None):
        """Optimizar contenido basado en métricas objetivo"""
        if target_metrics is None:
            target_metrics = {
                'readability_target': 70,
                'seo_target': 80,
                'engagement_target': 75,
                'structure_target': 80
            }
        
        # Analizar contenido actual
        current_analysis = self.analyze_content_quality(content)
        
        if not current_analysis:
            return None
        
        # Generar recomendaciones de optimización
        recommendations = []
        
        # Recomendaciones de legibilidad
        current_readability = current_analysis['readability_score']
        if current_readability < target_metrics['readability_target']:
            recommendations.append({
                'aspect': 'readability',
                'current_score': current_readability,
                'target_score': target_metrics['readability_target'],
                'recommendation': 'Reduce sentence length and use simpler words',
                'priority': 'high'
            })
        
        # Recomendaciones de SEO
        current_seo = current_analysis['seo_score']
        if current_seo < target_metrics['seo_target']:
            recommendations.append({
                'aspect': 'seo',
                'current_score': current_seo,
                'target_score': target_metrics['seo_target'],
                'recommendation': 'Add more headings, internal links, and optimize keyword density',
                'priority': 'high'
            })
        
        # Recomendaciones de engagement
        current_engagement = current_analysis['engagement_score']
        if current_engagement < target_metrics['engagement_target']:
            recommendations.append({
                'aspect': 'engagement',
                'current_score': current_engagement,
                'target_score': target_metrics['engagement_target'],
                'recommendation': 'Add power words, questions, and calls-to-action',
                'priority': 'medium'
            })
        
        # Recomendaciones de estructura
        current_structure = current_analysis['structure_score']
        if current_structure < target_metrics['structure_target']:
            recommendations.append({
                'aspect': 'structure',
                'current_score': current_structure,
                'target_score': target_metrics['structure_target'],
                'recommendation': 'Improve paragraph structure and add transition words',
                'priority': 'medium'
            })
        
        # Generar contenido optimizado
        optimized_content = self._generate_optimized_content(content, recommendations)
        
        optimization_result = {
            'original_content': content,
            'current_analysis': current_analysis,
            'target_metrics': target_metrics,
            'recommendations': recommendations,
            'optimized_content': optimized_content,
            'optimization_timestamp': datetime.now().isoformat()
        }
        
        return optimization_result
    
    def _generate_optimized_content(self, content, recommendations):
        """Generar contenido optimizado basado en recomendaciones"""
        optimized_content = content
        
        for rec in recommendations:
            if rec['aspect'] == 'readability':
                # Simplificar oraciones largas
                sentences = re.split(r'[.!?]+', optimized_content)
                simplified_sentences = []
                
                for sentence in sentences:
                    if len(sentence.split()) > 20:
                        # Dividir oraciones largas
                        words = sentence.split()
                        mid_point = len(words) // 2
                        simplified_sentences.append(' '.join(words[:mid_point]) + '.')
                        simplified_sentences.append(' '.join(words[mid_point:]))
                    else:
                        simplified_sentences.append(sentence)
                
                optimized_content = '. '.join(simplified_sentences)
            
            elif rec['aspect'] == 'seo':
                # Agregar headings si no existen
                if not re.search(r'#+\s+', optimized_content):
                    optimized_content = f"# {optimized_content[:50]}...\n\n{optimized_content}"
                
                # Agregar lista si no existe
                if not re.search(r'[-*+]\s+', optimized_content):
                    optimized_content += "\n\n## Key Points:\n- Point 1\n- Point 2\n- Point 3"
            
            elif rec['aspect'] == 'engagement':
                # Agregar pregunta al final
                if not re.search(r'\?', optimized_content):
                    optimized_content += "\n\nWhat do you think about this? Let us know in the comments!"
            
            elif rec['aspect'] == 'structure':
                # Mejorar estructura de párrafos
                paragraphs = optimized_content.split('\n\n')
                if len(paragraphs) > 1:
                    structured_content = []
                    for i, paragraph in enumerate(paragraphs):
                        if i > 0:
                            structured_content.append(f"Furthermore, {paragraph.lower()}")
                        else:
                            structured_content.append(paragraph)
                    optimized_content = '\n\n'.join(structured_content)
        
        return optimized_content
    
    def create_content_dashboard(self):
        """Crear dashboard de optimización de contenido"""
        if not self.content_database:
            return None
        
        # Crear subplots
        fig = make_subplots(
            rows=2, cols=2,
            subplot_titles=('Scores de Calidad', 'Análisis de Keywords',
                          'Métricas de Legibilidad', 'Distribución de Sentimientos'),
            specs=[[{"type": "bar"}, {"type": "bar"}],
                   [{"type": "scatter"}, {"type": "pie"}]]
        )
        
        # Gráfico de scores de calidad
        if self.content_database:
            content_ids = list(self.content_database.keys())
            quality_scores = [self.content_database[cid]['overall_quality_score'] for cid in content_ids]
            
            fig.add_trace(
                go.Bar(x=content_ids, y=quality_scores, name='Quality Scores'),
                row=1, col=1
            )
        
        # Gráfico de análisis de keywords
        if self.content_database:
            # Agregar datos de keywords (simplificado)
            keywords = ['marketing', 'content', 'seo', 'engagement', 'optimization']
            keyword_counts = [np.random.randint(5, 20) for _ in keywords]
            
            fig.add_trace(
                go.Bar(x=keywords, y=keyword_counts, name='Keyword Frequency'),
                row=1, col=2
            )
        
        # Gráfico de métricas de legibilidad
        if self.content_database:
            readability_scores = [self.content_database[cid]['readability_score'] for cid in content_ids]
            seo_scores = [self.content_database[cid]['seo_score'] for cid in content_ids]
            
            fig.add_trace(
                go.Scatter(x=readability_scores, y=seo_scores, mode='markers', name='Readability vs SEO'),
                row=2, col=1
            )
        
        # Gráfico de distribución de sentimientos
        if self.content_database:
            sentiments = []
            for cid in content_ids:
                sentiment = self.content_database[cid]['sentiment_score']['sentiment']
                sentiments.append(sentiment)
            
            sentiment_counts = pd.Series(sentiments).value_counts()
            
            fig.add_trace(
                go.Pie(labels=sentiment_counts.index, values=sentiment_counts.values, name='Sentiment Distribution'),
                row=2, col=2
            )
        
        fig.update_layout(
            title="Dashboard de Optimización de Contenido con IA",
            showlegend=False,
            height=800
        )
        
        return fig
    
    def export_content_analysis(self, filename='ai_content_optimization_analysis.json'):
        """Exportar análisis de contenido"""
        export_data = {
            'timestamp': datetime.now().isoformat(),
            'content_database': self.content_database,
            'optimization_models': self.optimization_models,
            'performance_metrics': self.performance_metrics,
            'summary': {
                'total_content_analyzed': len(self.content_database),
                'analysis_date': datetime.now().isoformat()
            }
        }
        
        with open(filename, 'w') as f:
            json.dump(export_data, f, indent=2, default=str)
        
        print(f"✅ Análisis de contenido exportado a {filename}")
        return export_data

# Ejemplo de uso
if __name__ == "__main__":
    # Crear instancia del optimizador de contenido
    content_optimizer = AIContentOptimizer()
    
    # Contenido de ejemplo
    sample_content = """
    # The Ultimate Guide to Digital Marketing
    
    Digital marketing is a comprehensive approach to reaching customers through various online channels. 
    It encompasses a wide range of strategies and tactics that businesses use to promote their products and services.
    
    ## Key Components of Digital Marketing
    
    Digital marketing includes several key components that work together to create a cohesive strategy:
    
    - Search Engine Optimization (SEO)
    - Content Marketing
    - Social Media Marketing
    - Email Marketing
    - Pay-Per-Click Advertising
    
    ## Benefits of Digital Marketing
    
    The benefits of digital marketing are numerous and significant. Businesses can reach a global audience, 
    track their results in real-time, and adjust their strategies based on data and analytics.
    
    ## Conclusion
    
    Digital marketing is essential for modern businesses. It provides cost-effective ways to reach customers 
    and build brand awareness in the digital age.
    """
    
    # Analizar calidad del contenido
    print("📝 Analizando calidad del contenido...")
    quality_analysis = content_optimizer.analyze_content_quality(sample_content, 'blog_post')
    
    # Optimizar contenido
    print("🎯 Optimizando contenido...")
    optimization_result = content_optimizer.optimize_content(sample_content)
    
    # Crear dashboard
    print("📊 Creando dashboard de optimización de contenido...")
    dashboard = content_optimizer.create_content_dashboard()
    
    # Exportar análisis
    print("💾 Exportando análisis de contenido...")
    export_data = content_optimizer.export_content_analysis()
    
    print("✅ Sistema de optimización de contenido con IA completado!")




