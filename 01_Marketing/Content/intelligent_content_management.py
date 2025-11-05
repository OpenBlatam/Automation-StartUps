#!/usr/bin/env python3
"""
Sistema de Gestión de Contenido Inteligente para Neural Marketing Consciousness Platform
"""

import json
import time
import sqlite3
import hashlib
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
import random
import re
from collections import defaultdict

class IntelligentContentManagement:
    def __init__(self, db_path="content_management.db"):
        self.db_path = db_path
        self.content_templates = {}
        self.ai_models = {}
        self.content_pipeline = {}
        self.init_content_database()
        self.load_content_templates()
        self.load_ai_models()
    
    def init_content_database(self):
        """Inicializar base de datos de gestión de contenido"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Tabla de contenido
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS content (
                id TEXT PRIMARY KEY,
                title TEXT NOT NULL,
                content_type TEXT NOT NULL,
                content_data TEXT NOT NULL,
                status TEXT DEFAULT 'draft',
                author_id TEXT,
                ai_generated BOOLEAN DEFAULT FALSE,
                ai_model_used TEXT,
                quality_score REAL DEFAULT 0.0,
                engagement_score REAL DEFAULT 0.0,
                seo_score REAL DEFAULT 0.0,
                tags TEXT,
                metadata TEXT,
                created_at TEXT,
                updated_at TEXT,
                published_at TEXT
            )
        ''')
        
        # Tabla de versiones de contenido
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS content_versions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                content_id TEXT,
                version_number INTEGER,
                content_data TEXT,
                changes_summary TEXT,
                created_at TEXT,
                created_by TEXT,
                FOREIGN KEY (content_id) REFERENCES content (id)
            )
        ''')
        
        # Tabla de plantillas de contenido
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS content_templates (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT UNIQUE NOT NULL,
                content_type TEXT NOT NULL,
                template_data TEXT NOT NULL,
                variables TEXT,
                ai_instructions TEXT,
                quality_criteria TEXT,
                created_at TEXT,
                updated_at TEXT
            )
        ''')
        
        # Tabla de flujos de trabajo de contenido
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS content_workflows (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT UNIQUE NOT NULL,
                workflow_steps TEXT NOT NULL,
                approval_required BOOLEAN DEFAULT FALSE,
                ai_review BOOLEAN DEFAULT FALSE,
                status TEXT DEFAULT 'active',
                created_at TEXT
            )
        ''')
        
        # Tabla de análisis de contenido
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS content_analytics (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                content_id TEXT,
                metric_name TEXT,
                metric_value REAL,
                metric_type TEXT,
                timestamp TEXT,
                FOREIGN KEY (content_id) REFERENCES content (id)
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def load_content_templates(self):
        """Cargar plantillas de contenido"""
        self.content_templates = {
            'blog_post': {
                'name': 'Blog Post Template',
                'structure': {
                    'title': 'string',
                    'introduction': 'text',
                    'main_content': 'text',
                    'conclusion': 'text',
                    'call_to_action': 'text',
                    'tags': 'array',
                    'meta_description': 'text'
                },
                'ai_instructions': 'Create an engaging blog post with clear structure, compelling introduction, valuable main content, strong conclusion, and effective call-to-action.',
                'quality_criteria': {
                    'readability_score': 80,
                    'seo_score': 75,
                    'engagement_potential': 70,
                    'word_count': {'min': 800, 'max': 2000}
                }
            },
            'social_media_post': {
                'name': 'Social Media Post Template',
                'structure': {
                    'platform': 'string',
                    'content': 'text',
                    'hashtags': 'array',
                    'image_prompt': 'text',
                    'call_to_action': 'text'
                },
                'ai_instructions': 'Create engaging social media content optimized for the specific platform with relevant hashtags and compelling visuals.',
                'quality_criteria': {
                    'character_count': {'max': 280},
                    'hashtag_count': {'min': 3, 'max': 10},
                    'engagement_potential': 80
                }
            },
            'email_campaign': {
                'name': 'Email Campaign Template',
                'structure': {
                    'subject_line': 'text',
                    'preheader': 'text',
                    'header': 'text',
                    'body': 'text',
                    'footer': 'text',
                    'call_to_action': 'text'
                },
                'ai_instructions': 'Create a compelling email campaign with attention-grabbing subject line, clear value proposition, and strong call-to-action.',
                'quality_criteria': {
                    'subject_line_length': {'max': 50},
                    'open_rate_potential': 75,
                    'click_rate_potential': 70
                }
            },
            'video_script': {
                'name': 'Video Script Template',
                'structure': {
                    'title': 'text',
                    'hook': 'text',
                    'main_points': 'array',
                    'transitions': 'array',
                    'conclusion': 'text',
                    'call_to_action': 'text'
                },
                'ai_instructions': 'Create an engaging video script with strong hook, clear main points, smooth transitions, and compelling call-to-action.',
                'quality_criteria': {
                    'duration': {'min': 60, 'max': 300},
                    'engagement_potential': 85,
                    'clarity_score': 80
                }
            },
            'infographic': {
                'name': 'Infographic Template',
                'structure': {
                    'title': 'text',
                    'main_statistics': 'array',
                    'key_points': 'array',
                    'visual_elements': 'array',
                    'data_sources': 'array'
                },
                'ai_instructions': 'Create an informative infographic with compelling statistics, clear key points, and visually appealing elements.',
                'quality_criteria': {
                    'statistic_count': {'min': 5, 'max': 15},
                    'visual_appeal': 80,
                    'information_density': 75
                }
            }
        }
    
    def load_ai_models(self):
        """Cargar modelos de IA disponibles"""
        self.ai_models = {
            'text_generation': {
                'gpt-4': {
                    'name': 'GPT-4',
                    'strengths': ['creative_writing', 'long_form_content', 'complex_analysis'],
                    'best_for': ['blog_posts', 'articles', 'detailed_content'],
                    'quality_score': 95
                },
                'claude-3': {
                    'name': 'Claude-3',
                    'strengths': ['reasoning', 'safety', 'factual_accuracy'],
                    'best_for': ['technical_content', 'educational_material', 'factual_posts'],
                    'quality_score': 92
                },
                'gemini-pro': {
                    'name': 'Gemini Pro',
                    'strengths': ['multilingual', 'code_generation', 'data_analysis'],
                    'best_for': ['international_content', 'technical_docs', 'data_driven_content'],
                    'quality_score': 88
                }
            },
            'image_generation': {
                'dall-e-3': {
                    'name': 'DALL-E 3',
                    'strengths': ['photorealistic', 'artistic', 'detailed'],
                    'best_for': ['social_media_images', 'blog_headers', 'marketing_graphics'],
                    'quality_score': 95
                },
                'midjourney': {
                    'name': 'Midjourney',
                    'strengths': ['artistic', 'creative', 'stylized'],
                    'best_for': ['creative_graphics', 'artistic_content', 'brand_visuals'],
                    'quality_score': 90
                },
                'stable-diffusion': {
                    'name': 'Stable Diffusion',
                    'strengths': ['customizable', 'fast', 'open_source'],
                    'best_for': ['bulk_generation', 'custom_styles', 'experimental_content'],
                    'quality_score': 85
                }
            },
            'video_generation': {
                'runway': {
                    'name': 'Runway',
                    'strengths': ['video_editing', 'effects', 'professional'],
                    'best_for': ['marketing_videos', 'tutorials', 'promotional_content'],
                    'quality_score': 88
                },
                'pika': {
                    'name': 'Pika',
                    'strengths': ['text_to_video', 'creative', 'experimental'],
                    'best_for': ['social_media_videos', 'creative_content', 'experimental_videos'],
                    'quality_score': 82
                }
            }
        }
    
    def create_content(self, title: str, content_type: str, content_data: Dict, 
                      author_id: str = None, ai_generated: bool = False, 
                      ai_model_used: str = None) -> Dict:
        """Crear nuevo contenido"""
        try:
            content_id = self.generate_content_id(title, content_type)
            
            # Validar estructura según plantilla
            template = self.content_templates.get(content_type)
            if template:
                validation_result = self.validate_content_structure(content_data, template)
                if not validation_result['valid']:
                    return {'success': False, 'error': f"Content structure invalid: {validation_result['errors']}"}
            
            # Calcular scores iniciales
            quality_score = self.calculate_quality_score(content_data, content_type)
            seo_score = self.calculate_seo_score(content_data, content_type)
            
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO content 
                (id, title, content_type, content_data, author_id, ai_generated, 
                 ai_model_used, quality_score, seo_score, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (content_id, title, content_type, json.dumps(content_data), author_id,
                  ai_generated, ai_model_used, quality_score, seo_score,
                  datetime.now().isoformat(), datetime.now().isoformat()))
            
            conn.commit()
            conn.close()
            
            return {
                'success': True,
                'content_id': content_id,
                'message': 'Content created successfully',
                'quality_score': quality_score,
                'seo_score': seo_score
            }
            
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def generate_content_id(self, title: str, content_type: str) -> str:
        """Generar ID único para contenido"""
        timestamp = str(int(time.time()))
        title_hash = hashlib.md5(title.encode()).hexdigest()[:8]
        return f"{content_type}_{title_hash}_{timestamp}"
    
    def validate_content_structure(self, content_data: Dict, template: Dict) -> Dict:
        """Validar estructura de contenido según plantilla"""
        errors = []
        structure = template['structure']
        
        for field, field_type in structure.items():
            if field not in content_data:
                errors.append(f"Missing required field: {field}")
                continue
            
            value = content_data[field]
            
            if field_type == 'string' and not isinstance(value, str):
                errors.append(f"Field {field} must be a string")
            elif field_type == 'text' and not isinstance(value, str):
                errors.append(f"Field {field} must be text")
            elif field_type == 'array' and not isinstance(value, list):
                errors.append(f"Field {field} must be an array")
            elif field_type == 'number' and not isinstance(value, (int, float)):
                errors.append(f"Field {field} must be a number")
        
        return {
            'valid': len(errors) == 0,
            'errors': errors
        }
    
    def calculate_quality_score(self, content_data: Dict, content_type: str) -> float:
        """Calcular puntuación de calidad del contenido"""
        score = 0.0
        max_score = 100.0
        
        # Puntuación por completitud
        template = self.content_templates.get(content_type, {})
        structure = template.get('structure', {})
        completeness_score = (len(content_data) / len(structure)) * 30
        score += min(completeness_score, 30)
        
        # Puntuación por longitud de contenido
        total_text = self.extract_text_content(content_data)
        word_count = len(total_text.split())
        
        if content_type == 'blog_post':
            if 800 <= word_count <= 2000:
                score += 25
            elif 500 <= word_count < 800 or 2000 < word_count <= 3000:
                score += 15
            else:
                score += 5
        elif content_type == 'social_media_post':
            if 50 <= len(total_text) <= 280:
                score += 25
            else:
                score += 10
        
        # Puntuación por elementos de engagement
        engagement_elements = 0
        if 'call_to_action' in content_data and content_data['call_to_action']:
            engagement_elements += 1
        if 'hashtags' in content_data and content_data['hashtags']:
            engagement_elements += 1
        if 'tags' in content_data and content_data['tags']:
            engagement_elements += 1
        
        score += min(engagement_elements * 10, 20)
        
        # Puntuación por calidad del texto (simplificado)
        readability_score = self.calculate_readability_score(total_text)
        score += readability_score * 0.25
        
        return min(score, max_score)
    
    def extract_text_content(self, content_data: Dict) -> str:
        """Extraer todo el texto del contenido"""
        text_parts = []
        for key, value in content_data.items():
            if isinstance(value, str):
                text_parts.append(value)
            elif isinstance(value, list):
                text_parts.extend([str(item) for item in value if isinstance(item, str)])
        return ' '.join(text_parts)
    
    def calculate_readability_score(self, text: str) -> float:
        """Calcular puntuación de legibilidad (simplificado)"""
        if not text:
            return 0.0
        
        sentences = len(re.split(r'[.!?]+', text))
        words = len(text.split())
        syllables = sum(self.count_syllables(word) for word in text.split())
        
        if sentences == 0 or words == 0:
            return 0.0
        
        # Flesch Reading Ease simplificado
        avg_sentence_length = words / sentences
        avg_syllables_per_word = syllables / words
        
        score = 206.835 - (1.015 * avg_sentence_length) - (84.6 * avg_syllables_per_word)
        return max(0, min(100, score))
    
    def count_syllables(self, word: str) -> int:
        """Contar sílabas en una palabra (aproximado)"""
        word = word.lower()
        vowels = 'aeiouy'
        syllable_count = 0
        prev_was_vowel = False
        
        for char in word:
            is_vowel = char in vowels
            if is_vowel and not prev_was_vowel:
                syllable_count += 1
            prev_was_vowel = is_vowel
        
        if word.endswith('e'):
            syllable_count -= 1
        
        return max(1, syllable_count)
    
    def calculate_seo_score(self, content_data: Dict, content_type: str) -> float:
        """Calcular puntuación SEO del contenido"""
        score = 0.0
        max_score = 100.0
        
        # Puntuación por título
        title = content_data.get('title', '')
        if title:
            if 30 <= len(title) <= 60:
                score += 20
            elif 20 <= len(title) < 30 or 60 < len(title) <= 70:
                score += 15
            else:
                score += 5
        
        # Puntuación por meta descripción
        meta_description = content_data.get('meta_description', '')
        if meta_description:
            if 120 <= len(meta_description) <= 160:
                score += 20
            elif 100 <= len(meta_description) < 120 or 160 < len(meta_description) <= 180:
                score += 15
            else:
                score += 5
        
        # Puntuación por tags/hashtags
        tags = content_data.get('tags', []) or content_data.get('hashtags', [])
        if tags and len(tags) >= 3:
            score += 15
        elif tags and len(tags) >= 1:
            score += 10
        
        # Puntuación por estructura
        if content_type == 'blog_post':
            if 'introduction' in content_data and 'conclusion' in content_data:
                score += 20
            if 'main_content' in content_data and len(content_data['main_content']) > 500:
                score += 15
        
        # Puntuación por densidad de palabras clave (simplificado)
        text_content = self.extract_text_content(content_data)
        if text_content and title:
            title_words = title.lower().split()
            text_words = text_content.lower().split()
            if text_words:
                keyword_density = sum(1 for word in text_words if word in title_words) / len(text_words)
                score += min(keyword_density * 100, 25)
        
        return min(score, max_score)
    
    def generate_content_with_ai(self, content_type: str, requirements: Dict, 
                                ai_model: str = None) -> Dict:
        """Generar contenido usando IA"""
        try:
            template = self.content_templates.get(content_type)
            if not template:
                return {'success': False, 'error': f'Content type {content_type} not supported'}
            
            # Seleccionar mejor modelo de IA
            if not ai_model:
                ai_model = self.select_best_ai_model(content_type, requirements)
            
            # Generar contenido usando IA (simulado)
            generated_content = self.simulate_ai_content_generation(
                content_type, requirements, template, ai_model
            )
            
            # Crear contenido
            title = generated_content.get('title', f'Generated {content_type}')
            result = self.create_content(
                title, content_type, generated_content, 
                ai_generated=True, ai_model_used=ai_model
            )
            
            if result['success']:
                result['generated_content'] = generated_content
                result['ai_model_used'] = ai_model
            
            return result
            
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def select_best_ai_model(self, content_type: str, requirements: Dict) -> str:
        """Seleccionar el mejor modelo de IA para el tipo de contenido"""
        if content_type in ['blog_post', 'article', 'email_campaign']:
            models = self.ai_models['text_generation']
        elif content_type in ['social_media_post', 'infographic']:
            models = self.ai_models['image_generation']
        elif content_type in ['video_script', 'video']:
            models = self.ai_models['video_generation']
        else:
            models = self.ai_models['text_generation']
        
        # Seleccionar modelo con mayor puntuación de calidad
        best_model = max(models.items(), key=lambda x: x[1]['quality_score'])
        return best_model[0]
    
    def simulate_ai_content_generation(self, content_type: str, requirements: Dict, 
                                     template: Dict, ai_model: str) -> Dict:
        """Simular generación de contenido con IA"""
        structure = template['structure']
        generated_content = {}
        
        for field, field_type in structure.items():
            if field == 'title':
                generated_content[field] = f"AI-Generated {content_type.title()} - {requirements.get('topic', 'Marketing Content')}"
            elif field == 'content' or field == 'main_content':
                generated_content[field] = f"This is AI-generated {content_type} content about {requirements.get('topic', 'marketing')}. The content is optimized for engagement and provides valuable insights to the target audience."
            elif field == 'introduction':
                generated_content[field] = f"Welcome to this comprehensive guide about {requirements.get('topic', 'marketing strategies')}. In this article, we'll explore key concepts and provide actionable insights."
            elif field == 'conclusion':
                generated_content[field] = f"In conclusion, {requirements.get('topic', 'effective marketing')} requires careful planning and execution. Apply these strategies to achieve your goals."
            elif field == 'call_to_action':
                generated_content[field] = "Ready to get started? Contact us today for a personalized consultation."
            elif field == 'hashtags':
                generated_content[field] = ['#marketing', '#ai', '#content', '#strategy']
            elif field == 'tags':
                generated_content[field] = ['marketing', 'ai', 'content', 'strategy']
            elif field == 'meta_description':
                generated_content[field] = f"Learn about {requirements.get('topic', 'marketing strategies')} with our comprehensive AI-generated guide. Get actionable insights and tips."
            elif field == 'platform':
                generated_content[field] = requirements.get('platform', 'twitter')
            elif field == 'image_prompt':
                generated_content[field] = f"Professional {content_type} image about {requirements.get('topic', 'marketing')}"
            elif field == 'main_points':
                generated_content[field] = [
                    f"Key point 1 about {requirements.get('topic', 'marketing')}",
                    f"Important insight 2 regarding {requirements.get('topic', 'strategy')}",
                    f"Actionable tip 3 for {requirements.get('topic', 'success')}"
                ]
            elif field == 'key_points':
                generated_content[field] = [
                    f"Essential concept 1: {requirements.get('topic', 'marketing fundamentals')}",
                    f"Critical insight 2: {requirements.get('topic', 'strategy development')}",
                    f"Practical application 3: {requirements.get('topic', 'implementation')}"
                ]
            elif field == 'main_statistics':
                generated_content[field] = [
                    "85% of marketers see improved results with AI",
                    "Content marketing generates 3x more leads",
                    "Personalized content increases engagement by 42%"
                ]
            else:
                generated_content[field] = f"AI-generated {field} for {content_type}"
        
        return generated_content
    
    def update_content(self, content_id: str, updates: Dict, author_id: str = None) -> Dict:
        """Actualizar contenido existente"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Obtener contenido actual
            cursor.execute('SELECT * FROM content WHERE id = ?', (content_id,))
            content = cursor.fetchone()
            
            if not content:
                return {'success': False, 'error': 'Content not found'}
            
            # Crear versión anterior
            self.create_content_version(content_id, content[3], f"Updated by {author_id or 'system'}")
            
            # Actualizar contenido
            current_data = json.loads(content[3])
            current_data.update(updates)
            
            # Recalcular scores
            quality_score = self.calculate_quality_score(current_data, content[2])
            seo_score = self.calculate_seo_score(current_data, content[2])
            
            cursor.execute('''
                UPDATE content 
                SET content_data = ?, quality_score = ?, seo_score = ?, 
                    updated_at = ?, status = 'updated'
                WHERE id = ?
            ''', (json.dumps(current_data), quality_score, seo_score, 
                  datetime.now().isoformat(), content_id))
            
            conn.commit()
            conn.close()
            
            return {
                'success': True,
                'message': 'Content updated successfully',
                'quality_score': quality_score,
                'seo_score': seo_score
            }
            
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def create_content_version(self, content_id: str, content_data: str, changes_summary: str):
        """Crear versión del contenido"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Obtener número de versión actual
            cursor.execute('''
                SELECT MAX(version_number) FROM content_versions WHERE content_id = ?
            ''', (content_id,))
            result = cursor.fetchone()
            version_number = (result[0] or 0) + 1
            
            cursor.execute('''
                INSERT INTO content_versions 
                (content_id, version_number, content_data, changes_summary, created_at)
                VALUES (?, ?, ?, ?, ?)
            ''', (content_id, version_number, content_data, changes_summary, 
                  datetime.now().isoformat()))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            print(f"Error creating content version: {e}")
    
    def publish_content(self, content_id: str, publish_date: str = None) -> Dict:
        """Publicar contenido"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            publish_timestamp = publish_date or datetime.now().isoformat()
            
            cursor.execute('''
                UPDATE content 
                SET status = 'published', published_at = ?, updated_at = ?
                WHERE id = ?
            ''', (publish_timestamp, datetime.now().isoformat(), content_id))
            
            conn.commit()
            conn.close()
            
            return {
                'success': True,
                'message': 'Content published successfully',
                'published_at': publish_timestamp
            }
            
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def get_content_analytics(self, content_id: str) -> Dict:
        """Obtener analytics de contenido"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Obtener métricas de contenido
            cursor.execute('''
                SELECT metric_name, metric_value, metric_type, timestamp
                FROM content_analytics
                WHERE content_id = ?
                ORDER BY timestamp DESC
            ''', (content_id,))
            
            metrics = cursor.fetchall()
            
            # Obtener información del contenido
            cursor.execute('''
                SELECT title, content_type, quality_score, seo_score, 
                       engagement_score, created_at, published_at
                FROM content WHERE id = ?
            ''', (content_id,))
            
            content_info = cursor.fetchone()
            conn.close()
            
            if not content_info:
                return {'success': False, 'error': 'Content not found'}
            
            # Procesar métricas
            analytics = {
                'content_id': content_id,
                'title': content_info[0],
                'content_type': content_info[1],
                'quality_score': content_info[2],
                'seo_score': content_info[3],
                'engagement_score': content_info[4],
                'created_at': content_info[5],
                'published_at': content_info[6],
                'metrics': {}
            }
            
            for metric_name, metric_value, metric_type, timestamp in metrics:
                if metric_name not in analytics['metrics']:
                    analytics['metrics'][metric_name] = []
                analytics['metrics'][metric_name].append({
                    'value': metric_value,
                    'type': metric_type,
                    'timestamp': timestamp
                })
            
            return {
                'success': True,
                'analytics': analytics
            }
            
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def search_content(self, query: str, content_type: str = None, 
                      filters: Dict = None) -> Dict:
        """Buscar contenido"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Construir consulta SQL
            sql = '''
                SELECT id, title, content_type, quality_score, seo_score, 
                       engagement_score, created_at, status
                FROM content
                WHERE (title LIKE ? OR content_data LIKE ?)
            '''
            params = [f'%{query}%', f'%{query}%']
            
            if content_type:
                sql += ' AND content_type = ?'
                params.append(content_type)
            
            if filters:
                if 'min_quality_score' in filters:
                    sql += ' AND quality_score >= ?'
                    params.append(filters['min_quality_score'])
                
                if 'status' in filters:
                    sql += ' AND status = ?'
                    params.append(filters['status'])
            
            sql += ' ORDER BY quality_score DESC, created_at DESC'
            
            cursor.execute(sql, params)
            results = cursor.fetchall()
            conn.close()
            
            content_list = []
            for row in results:
                content_list.append({
                    'id': row[0],
                    'title': row[1],
                    'content_type': row[2],
                    'quality_score': row[3],
                    'seo_score': row[4],
                    'engagement_score': row[5],
                    'created_at': row[6],
                    'status': row[7]
                })
            
            return {
                'success': True,
                'results': content_list,
                'count': len(content_list),
                'query': query
            }
            
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def get_content_recommendations(self, user_id: str, limit: int = 10) -> Dict:
        """Obtener recomendaciones de contenido para usuario"""
        try:
            # Simular recomendaciones basadas en contenido popular y de alta calidad
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT id, title, content_type, quality_score, seo_score, 
                       engagement_score, created_at
                FROM content
                WHERE status = 'published'
                ORDER BY (quality_score + seo_score + engagement_score) DESC
                LIMIT ?
            ''', (limit * 2,))
            
            all_content = cursor.fetchall()
            conn.close()
            
            # Simular personalización basada en usuario
            recommendations = []
            for i, row in enumerate(all_content[:limit]):
                recommendations.append({
                    'id': row[0],
                    'title': row[1],
                    'content_type': row[2],
                    'quality_score': row[3],
                    'seo_score': row[4],
                    'engagement_score': row[5],
                    'created_at': row[6],
                    'recommendation_score': row[3] + row[4] + row[5] + random.uniform(0, 10),
                    'reason': f'High-quality {row[2]} content with excellent scores'
                })
            
            return {
                'success': True,
                'recommendations': recommendations,
                'user_id': user_id,
                'count': len(recommendations)
            }
            
        except Exception as e:
            return {'success': False, 'error': str(e)}

def main():
    content_mgmt = IntelligentContentManagement()
    
    print("📝 Sistema de Gestión de Contenido Inteligente")
    print("=" * 60)
    print("1. Crear contenido")
    print("2. Generar contenido con IA")
    print("3. Actualizar contenido")
    print("4. Publicar contenido")
    print("5. Obtener analytics de contenido")
    print("6. Buscar contenido")
    print("7. Obtener recomendaciones")
    print("8. Simular datos de ejemplo")
    print("9. Salir")
    
    while True:
        choice = input("\nSeleccione una opción (1-9): ").strip()
        
        if choice == '1':
            title = input("Título del contenido: ").strip()
            print("Tipos disponibles: blog_post, social_media_post, email_campaign, video_script, infographic")
            content_type = input("Tipo de contenido: ").strip()
            
            # Simular datos de contenido
            content_data = {
                'introduction': 'This is an introduction to the content.',
                'main_content': 'This is the main content with valuable information.',
                'conclusion': 'This is the conclusion of the content.',
                'call_to_action': 'Contact us for more information.',
                'tags': ['marketing', 'content', 'strategy'],
                'meta_description': 'A comprehensive guide to content marketing strategies.'
            }
            
            result = content_mgmt.create_content(title, content_type, content_data)
            if result['success']:
                print(f"✅ {result['message']}")
                print(f"   ID: {result['content_id']}")
                print(f"   Quality Score: {result['quality_score']:.1f}")
                print(f"   SEO Score: {result['seo_score']:.1f}")
            else:
                print(f"❌ {result['error']}")
        
        elif choice == '2':
            print("Tipos disponibles: blog_post, social_media_post, email_campaign, video_script, infographic")
            content_type = input("Tipo de contenido: ").strip()
            topic = input("Tema del contenido: ").strip()
            platform = input("Plataforma (opcional): ").strip()
            
            requirements = {
                'topic': topic,
                'platform': platform
            }
            
            result = content_mgmt.generate_content_with_ai(content_type, requirements)
            if result['success']:
                print(f"✅ Contenido generado con IA")
                print(f"   ID: {result['content_id']}")
                print(f"   Modelo: {result['ai_model_used']}")
                print(f"   Quality Score: {result['quality_score']:.1f}")
                print(f"   Título: {result['generated_content']['title']}")
            else:
                print(f"❌ {result['error']}")
        
        elif choice == '3':
            content_id = input("ID del contenido: ").strip()
            updates = input("Actualizaciones (JSON): ").strip()
            updates = json.loads(updates) if updates else {}
            
            result = content_mgmt.update_content(content_id, updates)
            if result['success']:
                print(f"✅ {result['message']}")
                print(f"   Quality Score: {result['quality_score']:.1f}")
                print(f"   SEO Score: {result['seo_score']:.1f}")
            else:
                print(f"❌ {result['error']}")
        
        elif choice == '4':
            content_id = input("ID del contenido: ").strip()
            
            result = content_mgmt.publish_content(content_id)
            if result['success']:
                print(f"✅ {result['message']}")
                print(f"   Publicado: {result['published_at']}")
            else:
                print(f"❌ {result['error']}")
        
        elif choice == '5':
            content_id = input("ID del contenido: ").strip()
            
            result = content_mgmt.get_content_analytics(content_id)
            if result['success']:
                analytics = result['analytics']
                print(f"📊 Analytics de {analytics['title']}:")
                print(f"   Tipo: {analytics['content_type']}")
                print(f"   Quality Score: {analytics['quality_score']:.1f}")
                print(f"   SEO Score: {analytics['seo_score']:.1f}")
                print(f"   Engagement Score: {analytics['engagement_score']:.1f}")
                print(f"   Creado: {analytics['created_at']}")
                print(f"   Publicado: {analytics['published_at'] or 'No publicado'}")
            else:
                print(f"❌ {result['error']}")
        
        elif choice == '6':
            query = input("Consulta de búsqueda: ").strip()
            content_type = input("Tipo de contenido (opcional): ").strip() or None
            
            result = content_mgmt.search_content(query, content_type)
            if result['success']:
                print(f"🔍 {result['count']} resultados encontrados:")
                for i, content in enumerate(result['results'][:5], 1):
                    print(f"   {i}. {content['title']} ({content['content_type']}) - Quality: {content['quality_score']:.1f}")
            else:
                print(f"❌ {result['error']}")
        
        elif choice == '7':
            user_id = input("ID de usuario: ").strip()
            limit = int(input("Límite de recomendaciones: ").strip() or "10")
            
            result = content_mgmt.get_content_recommendations(user_id, limit)
            if result['success']:
                print(f"💡 {result['count']} recomendaciones para {user_id}:")
                for i, rec in enumerate(result['recommendations'], 1):
                    print(f"   {i}. {rec['title']} ({rec['content_type']}) - Score: {rec['recommendation_score']:.1f}")
            else:
                print(f"❌ {result['error']}")
        
        elif choice == '8':
            print("🔄 Simulando datos de ejemplo...")
            
            # Crear contenido de ejemplo
            content_examples = [
                ('AI Marketing Strategies', 'blog_post'),
                ('Social Media Best Practices', 'social_media_post'),
                ('Email Campaign Template', 'email_campaign'),
                ('Video Marketing Script', 'video_script'),
                ('Data Visualization Guide', 'infographic')
            ]
            
            for title, content_type in content_examples:
                content_data = {
                    'introduction': f'Introduction to {title.lower()}',
                    'main_content': f'Comprehensive guide about {title.lower()} with actionable insights.',
                    'conclusion': f'Conclusion and next steps for {title.lower()}.',
                    'call_to_action': 'Learn more about our services.',
                    'tags': ['marketing', 'ai', 'strategy'],
                    'meta_description': f'Learn about {title.lower()} with our comprehensive guide.'
                }
                
                result = content_mgmt.create_content(title, content_type, content_data)
                if result['success']:
                    print(f"   ✅ {title} creado")
            
            print("✅ Datos de ejemplo simulados generados")
        
        elif choice == '9':
            print("👋 ¡Hasta luego!")
            break
        
        else:
            print("❌ Opción no válida")

if __name__ == "__main__":
    main()


