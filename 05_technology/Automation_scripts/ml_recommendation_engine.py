#!/usr/bin/env python3
"""
Motor de Machine Learning y Recomendaciones Inteligentes para Neural Marketing Consciousness Platform
"""

import json
import time
import sqlite3
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
import random
from collections import defaultdict
import math

class MLRecommendationEngine:
    def __init__(self, db_path="ml_recommendations.db"):
        self.db_path = db_path
        self.models = {}
        self.user_profiles = {}
        self.content_features = {}
        self.interaction_matrix = None
        self.init_ml_database()
        self.load_ml_configurations()
    
    def init_ml_database(self):
        """Inicializar base de datos de ML"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Tabla de perfiles de usuarios
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS user_profiles (
                user_id TEXT PRIMARY KEY,
                consciousness_level REAL,
                preferences TEXT,
                behavior_patterns TEXT,
                content_interests TEXT,
                engagement_history TEXT,
                last_updated TEXT,
                created_at TEXT
            )
        ''')
        
        # Tabla de características de contenido
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS content_features (
                content_id TEXT PRIMARY KEY,
                content_type TEXT,
                features TEXT,
                quality_score REAL,
                engagement_score REAL,
                ai_generated BOOLEAN,
                created_at TEXT
            )
        ''')
        
        # Tabla de interacciones
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS user_interactions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id TEXT,
                content_id TEXT,
                interaction_type TEXT,
                rating REAL,
                duration_seconds INTEGER,
                timestamp TEXT,
                context TEXT
            )
        ''')
        
        # Tabla de modelos ML
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS ml_models (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                model_name TEXT UNIQUE NOT NULL,
                model_type TEXT NOT NULL,
                model_data TEXT,
                accuracy REAL,
                last_trained TEXT,
                status TEXT DEFAULT 'active',
                created_at TEXT
            )
        ''')
        
        # Tabla de recomendaciones
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS recommendations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id TEXT,
                content_id TEXT,
                recommendation_type TEXT,
                score REAL,
                reason TEXT,
                generated_at TEXT,
                clicked BOOLEAN DEFAULT FALSE,
                converted BOOLEAN DEFAULT FALSE
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def load_ml_configurations(self):
        """Cargar configuraciones de ML"""
        self.ml_configs = {
            'collaborative_filtering': {
                'name': 'Collaborative Filtering',
                'description': 'Recomendaciones basadas en usuarios similares',
                'algorithm': 'matrix_factorization',
                'min_interactions': 5,
                'similarity_threshold': 0.3
            },
            'content_based': {
                'name': 'Content-Based Filtering',
                'description': 'Recomendaciones basadas en características del contenido',
                'algorithm': 'tf_idf',
                'min_features': 3,
                'similarity_threshold': 0.4
            },
            'hybrid': {
                'name': 'Hybrid Recommendation',
                'description': 'Combinación de filtrado colaborativo y basado en contenido',
                'algorithm': 'weighted_combination',
                'collaborative_weight': 0.6,
                'content_weight': 0.4
            },
            'consciousness_based': {
                'name': 'Consciousness-Based',
                'description': 'Recomendaciones basadas en nivel de conciencia',
                'algorithm': 'consciousness_matching',
                'level_tolerance': 10.0,
                'growth_factor': 1.2
            },
            'ai_optimized': {
                'name': 'AI-Optimized',
                'description': 'Recomendaciones optimizadas por IA',
                'algorithm': 'neural_network',
                'hidden_layers': [64, 32, 16],
                'learning_rate': 0.001
            }
        }
    
    def create_user_profile(self, user_id: str, consciousness_level: float = 0.0, 
                          preferences: Dict = None) -> Dict:
        """Crear perfil de usuario"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            profile_data = {
                'consciousness_level': consciousness_level,
                'preferences': preferences or {},
                'behavior_patterns': {},
                'content_interests': {},
                'engagement_history': [],
                'last_updated': datetime.now().isoformat(),
                'created_at': datetime.now().isoformat()
            }
            
            cursor.execute('''
                INSERT OR REPLACE INTO user_profiles 
                (user_id, consciousness_level, preferences, behavior_patterns, 
                 content_interests, engagement_history, last_updated, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (user_id, consciousness_level, json.dumps(profile_data['preferences']),
                  json.dumps(profile_data['behavior_patterns']),
                  json.dumps(profile_data['content_interests']),
                  json.dumps(profile_data['engagement_history']),
                  profile_data['last_updated'], profile_data['created_at']))
            
            conn.commit()
            conn.close()
            
            self.user_profiles[user_id] = profile_data
            
            return {'success': True, 'message': f'User profile created for {user_id}'}
            
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def add_content_features(self, content_id: str, content_type: str, 
                           features: Dict, quality_score: float = 0.0) -> Dict:
        """Agregar características de contenido"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT OR REPLACE INTO content_features 
                (content_id, content_type, features, quality_score, engagement_score, 
                 ai_generated, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (content_id, content_type, json.dumps(features), quality_score, 0.0, 
                  features.get('ai_generated', False), datetime.now().isoformat()))
            
            conn.commit()
            conn.close()
            
            self.content_features[content_id] = {
                'content_type': content_type,
                'features': features,
                'quality_score': quality_score,
                'engagement_score': 0.0
            }
            
            return {'success': True, 'message': f'Content features added for {content_id}'}
            
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def record_interaction(self, user_id: str, content_id: str, 
                         interaction_type: str, rating: float = None, 
                         duration_seconds: int = 0, context: Dict = None) -> Dict:
        """Registrar interacción de usuario"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO user_interactions 
                (user_id, content_id, interaction_type, rating, duration_seconds, 
                 timestamp, context)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (user_id, content_id, interaction_type, rating, duration_seconds,
                  datetime.now().isoformat(), json.dumps(context or {})))
            
            conn.commit()
            conn.close()
            
            # Actualizar perfil de usuario
            self.update_user_profile(user_id, interaction_type, content_id, rating)
            
            return {'success': True, 'message': 'Interaction recorded successfully'}
            
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def update_user_profile(self, user_id: str, interaction_type: str, 
                          content_id: str, rating: float = None):
        """Actualizar perfil de usuario basado en interacciones"""
        if user_id not in self.user_profiles:
            self.create_user_profile(user_id)
        
        profile = self.user_profiles[user_id]
        
        # Actualizar historial de engagement
        engagement_entry = {
            'interaction_type': interaction_type,
            'content_id': content_id,
            'rating': rating,
            'timestamp': datetime.now().isoformat()
        }
        profile['engagement_history'].append(engagement_entry)
        
        # Actualizar patrones de comportamiento
        if interaction_type not in profile['behavior_patterns']:
            profile['behavior_patterns'][interaction_type] = 0
        profile['behavior_patterns'][interaction_type] += 1
        
        # Actualizar intereses de contenido
        if content_id in self.content_features:
            content_type = self.content_features[content_id]['content_type']
            if content_type not in profile['content_interests']:
                profile['content_interests'][content_type] = 0
            profile['content_interests'][content_type] += 1
        
        # Actualizar nivel de conciencia basado en interacciones
        consciousness_increase = self.calculate_consciousness_increase(
            interaction_type, rating, profile['consciousness_level']
        )
        profile['consciousness_level'] = min(100.0, 
            profile['consciousness_level'] + consciousness_increase)
        
        profile['last_updated'] = datetime.now().isoformat()
        
        # Guardar en base de datos
        self.save_user_profile(user_id, profile)
    
    def calculate_consciousness_increase(self, interaction_type: str, 
                                       rating: float, current_level: float) -> float:
        """Calcular aumento de conciencia basado en interacción"""
        base_increase = {
            'view': 0.1,
            'like': 0.2,
            'share': 0.5,
            'comment': 0.3,
            'create': 1.0,
            'ai_interaction': 0.4,
            'collaboration': 0.6
        }
        
        increase = base_increase.get(interaction_type, 0.1)
        
        # Ajustar por rating
        if rating:
            increase *= (rating / 5.0)
        
        # Ajustar por nivel actual (más difícil subir niveles altos)
        if current_level > 80:
            increase *= 0.5
        elif current_level > 60:
            increase *= 0.7
        elif current_level > 40:
            increase *= 0.9
        
        return increase
    
    def save_user_profile(self, user_id: str, profile: Dict):
        """Guardar perfil de usuario en base de datos"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                UPDATE user_profiles 
                SET consciousness_level = ?, preferences = ?, behavior_patterns = ?,
                    content_interests = ?, engagement_history = ?, last_updated = ?
                WHERE user_id = ?
            ''', (profile['consciousness_level'], json.dumps(profile['preferences']),
                  json.dumps(profile['behavior_patterns']),
                  json.dumps(profile['content_interests']),
                  json.dumps(profile['engagement_history']),
                  profile['last_updated'], user_id))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            print(f"Error saving user profile: {e}")
    
    def train_collaborative_filtering_model(self) -> Dict:
        """Entrenar modelo de filtrado colaborativo"""
        try:
            # Obtener datos de interacciones
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT user_id, content_id, rating, interaction_type
                FROM user_interactions
                WHERE rating IS NOT NULL
            ''')
            
            interactions = cursor.fetchall()
            conn.close()
            
            if len(interactions) < 10:
                return {'success': False, 'error': 'Insufficient data for training'}
            
            # Crear matriz de usuario-contenido
            user_content_matrix = defaultdict(dict)
            for user_id, content_id, rating, interaction_type in interactions:
                user_content_matrix[user_id][content_id] = rating
            
            # Convertir a matriz numpy
            users = list(user_content_matrix.keys())
            contents = list(set([content_id for interactions in user_content_matrix.values() 
                               for content_id in interactions.keys()]))
            
            matrix = np.zeros((len(users), len(contents)))
            for i, user in enumerate(users):
                for j, content in enumerate(contents):
                    matrix[i][j] = user_content_matrix[user].get(content, 0)
            
            # Aplicar factorización de matrices (SVD simplificado)
            U, s, Vt = np.linalg.svd(matrix, full_matrices=False)
            
            # Reducir dimensionalidad
            k = min(50, len(s))
            U_k = U[:, :k]
            s_k = s[:k]
            Vt_k = Vt[:k, :]
            
            # Guardar modelo
            model_data = {
                'users': users,
                'contents': contents,
                'U': U_k.tolist(),
                's': s_k.tolist(),
                'Vt': Vt_k.tolist(),
                'trained_at': datetime.now().isoformat()
            }
            
            # Guardar en base de datos
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT OR REPLACE INTO ml_models 
                (model_name, model_type, model_data, accuracy, last_trained, status, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', ('collaborative_filtering', 'collaborative', json.dumps(model_data),
                  0.0, datetime.now().isoformat(), 'active', datetime.now().isoformat()))
            
            conn.commit()
            conn.close()
            
            self.models['collaborative_filtering'] = model_data
            
            return {
                'success': True, 
                'message': 'Collaborative filtering model trained successfully',
                'users_count': len(users),
                'contents_count': len(contents),
                'accuracy': 0.0  # Se calcularía con validación cruzada
            }
            
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def train_content_based_model(self) -> Dict:
        """Entrenar modelo basado en contenido"""
        try:
            # Obtener características de contenido
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT content_id, content_type, features, quality_score
                FROM content_features
            ''')
            
            contents = cursor.fetchall()
            conn.close()
            
            if len(contents) < 5:
                return {'success': False, 'error': 'Insufficient content data for training'}
            
            # Procesar características
            content_features = {}
            for content_id, content_type, features_json, quality_score in contents:
                features = json.loads(features_json)
                content_features[content_id] = {
                    'content_type': content_type,
                    'features': features,
                    'quality_score': quality_score
                }
            
            # Crear matriz de características
            all_features = set()
            for features in content_features.values():
                all_features.update(features['features'].keys())
            
            feature_matrix = {}
            for content_id, data in content_features.items():
                feature_vector = []
                for feature in sorted(all_features):
                    feature_vector.append(data['features'].get(feature, 0))
                feature_matrix[content_id] = feature_vector
            
            # Guardar modelo
            model_data = {
                'content_features': content_features,
                'feature_matrix': feature_matrix,
                'all_features': list(all_features),
                'trained_at': datetime.now().isoformat()
            }
            
            # Guardar en base de datos
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT OR REPLACE INTO ml_models 
                (model_name, model_type, model_data, accuracy, last_trained, status, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', ('content_based', 'content', json.dumps(model_data),
                  0.0, datetime.now().isoformat(), 'active', datetime.now().isoformat()))
            
            conn.commit()
            conn.close()
            
            self.models['content_based'] = model_data
            
            return {
                'success': True,
                'message': 'Content-based model trained successfully',
                'contents_count': len(contents),
                'features_count': len(all_features)
            }
            
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def generate_recommendations(self, user_id: str, recommendation_type: str = 'hybrid', 
                               limit: int = 10) -> Dict:
        """Generar recomendaciones para usuario"""
        try:
            if user_id not in self.user_profiles:
                return {'success': False, 'error': 'User profile not found'}
            
            user_profile = self.user_profiles[user_id]
            recommendations = []
            
            if recommendation_type == 'collaborative':
                recommendations = self.get_collaborative_recommendations(user_id, limit)
            elif recommendation_type == 'content_based':
                recommendations = self.get_content_based_recommendations(user_id, limit)
            elif recommendation_type == 'consciousness_based':
                recommendations = self.get_consciousness_based_recommendations(user_id, limit)
            elif recommendation_type == 'hybrid':
                recommendations = self.get_hybrid_recommendations(user_id, limit)
            else:
                return {'success': False, 'error': 'Unknown recommendation type'}
            
            # Guardar recomendaciones
            self.save_recommendations(user_id, recommendations, recommendation_type)
            
            return {
                'success': True,
                'recommendations': recommendations,
                'user_id': user_id,
                'recommendation_type': recommendation_type,
                'count': len(recommendations)
            }
            
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def get_collaborative_recommendations(self, user_id: str, limit: int) -> List[Dict]:
        """Obtener recomendaciones colaborativas"""
        if 'collaborative_filtering' not in self.models:
            return []
        
        model = self.models['collaborative_filtering']
        users = model['users']
        
        if user_id not in users:
            return []
        
        user_index = users.index(user_id)
        U = np.array(model['U'])
        s = np.array(model['s'])
        Vt = np.array(model['Vt'])
        
        # Calcular puntuaciones de recomendación
        user_vector = U[user_index] @ np.diag(s) @ Vt
        
        recommendations = []
        for i, content_id in enumerate(model['contents']):
            score = user_vector[i]
            if score > 0:
                recommendations.append({
                    'content_id': content_id,
                    'score': float(score),
                    'reason': 'Similar users liked this content'
                })
        
        return sorted(recommendations, key=lambda x: x['score'], reverse=True)[:limit]
    
    def get_content_based_recommendations(self, user_id: str, limit: int) -> List[Dict]:
        """Obtener recomendaciones basadas en contenido"""
        if 'content_based' not in self.models:
            return []
        
        user_profile = self.user_profiles[user_id]
        model = self.models['content_based']
        
        # Obtener intereses del usuario
        user_interests = user_profile['content_interests']
        if not user_interests:
            return []
        
        # Calcular similitud con contenido
        recommendations = []
        for content_id, data in model['content_features'].items():
            content_type = data['content_type']
            if content_type in user_interests:
                # Calcular score basado en intereses y calidad
                interest_score = user_interests[content_type]
                quality_score = data['quality_score']
                combined_score = (interest_score * 0.7) + (quality_score * 0.3)
                
                recommendations.append({
                    'content_id': content_id,
                    'score': combined_score,
                    'reason': f'Matches your interest in {content_type}'
                })
        
        return sorted(recommendations, key=lambda x: x['score'], reverse=True)[:limit]
    
    def get_consciousness_based_recommendations(self, user_id: str, limit: int) -> List[Dict]:
        """Obtener recomendaciones basadas en conciencia"""
        user_profile = self.user_profiles[user_id]
        consciousness_level = user_profile['consciousness_level']
        
        # Obtener contenido apropiado para el nivel de conciencia
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT content_id, content_type, quality_score, features
            FROM content_features
            WHERE quality_score > ?
        ''', (consciousness_level * 0.8,))
        
        contents = cursor.fetchall()
        conn.close()
        
        recommendations = []
        for content_id, content_type, quality_score, features_json in contents:
            features = json.loads(features_json)
            complexity = features.get('complexity', 5.0)
            
            # Calcular score basado en compatibilidad con nivel de conciencia
            consciousness_diff = abs(consciousness_level - complexity)
            compatibility_score = max(0, 1 - (consciousness_diff / 50))
            
            if compatibility_score > 0.3:
                recommendations.append({
                    'content_id': content_id,
                    'score': compatibility_score * quality_score,
                    'reason': f'Appropriate for your consciousness level ({consciousness_level:.1f}%)'
                })
        
        return sorted(recommendations, key=lambda x: x['score'], reverse=True)[:limit]
    
    def get_hybrid_recommendations(self, user_id: str, limit: int) -> List[Dict]:
        """Obtener recomendaciones híbridas"""
        collaborative_recs = self.get_collaborative_recommendations(user_id, limit * 2)
        content_recs = self.get_content_based_recommendations(user_id, limit * 2)
        consciousness_recs = self.get_consciousness_based_recommendations(user_id, limit * 2)
        
        # Combinar recomendaciones con pesos
        combined_scores = defaultdict(float)
        
        for rec in collaborative_recs:
            combined_scores[rec['content_id']] += rec['score'] * 0.4
        
        for rec in content_recs:
            combined_scores[rec['content_id']] += rec['score'] * 0.3
        
        for rec in consciousness_recs:
            combined_scores[rec['content_id']] += rec['score'] * 0.3
        
        # Crear recomendaciones finales
        recommendations = []
        for content_id, score in combined_scores.items():
            recommendations.append({
                'content_id': content_id,
                'score': score,
                'reason': 'Combined recommendation from multiple algorithms'
            })
        
        return sorted(recommendations, key=lambda x: x['score'], reverse=True)[:limit]
    
    def save_recommendations(self, user_id: str, recommendations: List[Dict], 
                           recommendation_type: str):
        """Guardar recomendaciones en base de datos"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            for rec in recommendations:
                cursor.execute('''
                    INSERT INTO recommendations 
                    (user_id, content_id, recommendation_type, score, reason, generated_at)
                    VALUES (?, ?, ?, ?, ?, ?)
                ''', (user_id, rec['content_id'], recommendation_type, 
                      rec['score'], rec['reason'], datetime.now().isoformat()))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            print(f"Error saving recommendations: {e}")
    
    def evaluate_recommendation_performance(self) -> Dict:
        """Evaluar rendimiento de las recomendaciones"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Obtener estadísticas de recomendaciones
            cursor.execute('''
                SELECT 
                    recommendation_type,
                    COUNT(*) as total_recommendations,
                    SUM(CASE WHEN clicked = 1 THEN 1 ELSE 0 END) as clicks,
                    SUM(CASE WHEN converted = 1 THEN 1 ELSE 0 END) as conversions,
                    AVG(score) as avg_score
                FROM recommendations
                GROUP BY recommendation_type
            ''')
            
            stats = cursor.fetchall()
            
            performance = {}
            for row in stats:
                rec_type, total, clicks, conversions, avg_score = row
                click_rate = (clicks / total) * 100 if total > 0 else 0
                conversion_rate = (conversions / total) * 100 if total > 0 else 0
                
                performance[rec_type] = {
                    'total_recommendations': total,
                    'clicks': clicks,
                    'conversions': conversions,
                    'click_rate': click_rate,
                    'conversion_rate': conversion_rate,
                    'avg_score': avg_score
                }
            
            conn.close()
            
            return {
                'success': True,
                'performance': performance,
                'evaluated_at': datetime.now().isoformat()
            }
            
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def get_user_insights(self, user_id: str) -> Dict:
        """Obtener insights del usuario"""
        if user_id not in self.user_profiles:
            return {'success': False, 'error': 'User profile not found'}
        
        user_profile = self.user_profiles[user_id]
        
        # Analizar patrones de comportamiento
        behavior_patterns = user_profile['behavior_patterns']
        most_common_interaction = max(behavior_patterns.items(), key=lambda x: x[1]) if behavior_patterns else ('none', 0)
        
        # Analizar intereses de contenido
        content_interests = user_profile['content_interests']
        top_content_type = max(content_interests.items(), key=lambda x: x[1]) if content_interests else ('none', 0)
        
        # Calcular engagement score
        total_interactions = sum(behavior_patterns.values())
        engagement_score = min(100, total_interactions * 2)
        
        # Generar insights
        insights = {
            'consciousness_level': user_profile['consciousness_level'],
            'engagement_score': engagement_score,
            'most_common_interaction': most_common_interaction[0],
            'top_content_type': top_content_type[0],
            'total_interactions': total_interactions,
            'behavior_patterns': behavior_patterns,
            'content_interests': content_interests,
            'growth_potential': self.calculate_growth_potential(user_profile),
            'recommendations': self.generate_insight_recommendations(user_profile)
        }
        
        return {
            'success': True,
            'insights': insights,
            'generated_at': datetime.now().isoformat()
        }
    
    def calculate_growth_potential(self, user_profile: Dict) -> Dict:
        """Calcular potencial de crecimiento del usuario"""
        consciousness_level = user_profile['consciousness_level']
        total_interactions = sum(user_profile['behavior_patterns'].values())
        
        # Calcular potencial basado en nivel actual y actividad
        if consciousness_level < 30:
            potential = 'high'
            next_milestone = 50
        elif consciousness_level < 60:
            potential = 'medium'
            next_milestone = 80
        elif consciousness_level < 90:
            potential = 'low'
            next_milestone = 100
        else:
            potential = 'expert'
            next_milestone = 100
        
        return {
            'potential': potential,
            'next_milestone': next_milestone,
            'estimated_time_to_milestone': self.estimate_time_to_milestone(consciousness_level, total_interactions),
            'recommended_actions': self.get_recommended_actions(consciousness_level)
        }
    
    def estimate_time_to_milestone(self, current_level: float, total_interactions: int) -> str:
        """Estimar tiempo para alcanzar el siguiente hito"""
        if total_interactions == 0:
            return 'Unknown'
        
        avg_increase_per_interaction = current_level / max(total_interactions, 1)
        interactions_needed = (50 - current_level) / max(avg_increase_per_interaction, 0.1)
        
        if interactions_needed < 10:
            return '1-2 weeks'
        elif interactions_needed < 50:
            return '1-2 months'
        else:
            return '3+ months'
    
    def get_recommended_actions(self, consciousness_level: float) -> List[str]:
        """Obtener acciones recomendadas basadas en nivel de conciencia"""
        if consciousness_level < 30:
            return [
                'Complete basic AI training modules',
                'Engage with simple content generation',
                'Participate in community discussions'
            ]
        elif consciousness_level < 60:
            return [
                'Try advanced AI models',
                'Create multi-modal content',
                'Collaborate with other users'
            ]
        elif consciousness_level < 90:
            return [
                'Lead content creation projects',
                'Mentor other users',
                'Experiment with cutting-edge AI'
            ]
        else:
            return [
                'Contribute to platform development',
                'Share expertise through content',
                'Explore experimental AI features'
            ]
    
    def generate_insight_recommendations(self, user_profile: Dict) -> List[str]:
        """Generar recomendaciones de insights"""
        recommendations = []
        
        # Recomendaciones basadas en patrones de comportamiento
        behavior_patterns = user_profile['behavior_patterns']
        if 'create' not in behavior_patterns:
            recommendations.append('Try creating content to increase your consciousness level')
        
        if 'ai_interaction' not in behavior_patterns:
            recommendations.append('Engage more with AI features to unlock advanced capabilities')
        
        # Recomendaciones basadas en intereses
        content_interests = user_profile['content_interests']
        if len(content_interests) < 3:
            recommendations.append('Explore different types of content to diversify your interests')
        
        # Recomendaciones basadas en nivel de conciencia
        consciousness_level = user_profile['consciousness_level']
        if consciousness_level < 50:
            recommendations.append('Focus on completing foundational learning modules')
        elif consciousness_level > 80:
            recommendations.append('Consider mentoring other users to further develop your skills')
        
        return recommendations

def main():
    ml_engine = MLRecommendationEngine()
    
    print("🤖 Motor de Machine Learning y Recomendaciones")
    print("=" * 60)
    print("1. Crear perfil de usuario")
    print("2. Agregar características de contenido")
    print("3. Registrar interacción")
    print("4. Entrenar modelo colaborativo")
    print("5. Entrenar modelo basado en contenido")
    print("6. Generar recomendaciones")
    print("7. Evaluar rendimiento")
    print("8. Obtener insights de usuario")
    print("9. Simular datos de ejemplo")
    print("10. Salir")
    
    while True:
        choice = input("\nSeleccione una opción (1-10): ").strip()
        
        if choice == '1':
            user_id = input("ID de usuario: ").strip()
            consciousness_level = float(input("Nivel de conciencia (0-100): ").strip() or "0")
            preferences = input("Preferencias (JSON, opcional): ").strip()
            preferences = json.loads(preferences) if preferences else {}
            
            result = ml_engine.create_user_profile(user_id, consciousness_level, preferences)
            print(f"✅ {result['message']}" if result['success'] else f"❌ {result['error']}")
        
        elif choice == '2':
            content_id = input("ID de contenido: ").strip()
            content_type = input("Tipo de contenido: ").strip()
            features = input("Características (JSON): ").strip()
            features = json.loads(features) if features else {}
            quality_score = float(input("Puntuación de calidad (0-100): ").strip() or "50")
            
            result = ml_engine.add_content_features(content_id, content_type, features, quality_score)
            print(f"✅ {result['message']}" if result['success'] else f"❌ {result['error']}")
        
        elif choice == '3':
            user_id = input("ID de usuario: ").strip()
            content_id = input("ID de contenido: ").strip()
            interaction_type = input("Tipo de interacción: ").strip()
            rating = input("Rating (1-5, opcional): ").strip()
            rating = float(rating) if rating else None
            duration = int(input("Duración en segundos: ").strip() or "0")
            
            result = ml_engine.record_interaction(user_id, content_id, interaction_type, rating, duration)
            print(f"✅ {result['message']}" if result['success'] else f"❌ {result['error']}")
        
        elif choice == '4':
            result = ml_engine.train_collaborative_filtering_model()
            if result['success']:
                print(f"✅ {result['message']}")
                print(f"   Usuarios: {result['users_count']}")
                print(f"   Contenidos: {result['contents_count']}")
            else:
                print(f"❌ {result['error']}")
        
        elif choice == '5':
            result = ml_engine.train_content_based_model()
            if result['success']:
                print(f"✅ {result['message']}")
                print(f"   Contenidos: {result['contents_count']}")
                print(f"   Características: {result['features_count']}")
            else:
                print(f"❌ {result['error']}")
        
        elif choice == '6':
            user_id = input("ID de usuario: ").strip()
            rec_type = input("Tipo de recomendación (collaborative/content_based/consciousness_based/hybrid): ").strip() or "hybrid"
            limit = int(input("Límite de recomendaciones: ").strip() or "10")
            
            result = ml_engine.generate_recommendations(user_id, rec_type, limit)
            if result['success']:
                print(f"✅ {result['count']} recomendaciones generadas:")
                for i, rec in enumerate(result['recommendations'], 1):
                    print(f"   {i}. {rec['content_id']} (Score: {rec['score']:.2f}) - {rec['reason']}")
            else:
                print(f"❌ {result['error']}")
        
        elif choice == '7':
            result = ml_engine.evaluate_recommendation_performance()
            if result['success']:
                print(f"📊 Rendimiento de Recomendaciones:")
                for rec_type, stats in result['performance'].items():
                    print(f"   {rec_type}:")
                    print(f"     Total: {stats['total_recommendations']}")
                    print(f"     Click Rate: {stats['click_rate']:.1f}%")
                    print(f"     Conversion Rate: {stats['conversion_rate']:.1f}%")
                    print(f"     Score Promedio: {stats['avg_score']:.2f}")
            else:
                print(f"❌ {result['error']}")
        
        elif choice == '8':
            user_id = input("ID de usuario: ").strip()
            result = ml_engine.get_user_insights(user_id)
            if result['success']:
                insights = result['insights']
                print(f"🧠 Insights de Usuario {user_id}:")
                print(f"   Nivel de Conciencia: {insights['consciousness_level']:.1f}%")
                print(f"   Engagement Score: {insights['engagement_score']:.1f}")
                print(f"   Interacción Más Común: {insights['most_common_interaction']}")
                print(f"   Tipo de Contenido Favorito: {insights['top_content_type']}")
                print(f"   Potencial de Crecimiento: {insights['growth_potential']['potential']}")
                print(f"   Próximo Hito: {insights['growth_potential']['next_milestone']}%")
                print(f"   Tiempo Estimado: {insights['growth_potential']['estimated_time_to_milestone']}")
            else:
                print(f"❌ {result['error']}")
        
        elif choice == '9':
            print("🔄 Simulando datos de ejemplo...")
            
            # Crear usuarios de ejemplo
            users = ['user1', 'user2', 'user3', 'user4', 'user5']
            for user in users:
                consciousness = random.uniform(20, 90)
                ml_engine.create_user_profile(user, consciousness)
            
            # Crear contenido de ejemplo
            content_types = ['blog_post', 'video', 'infographic', 'podcast', 'social_media']
            for i in range(20):
                content_id = f'content_{i+1}'
                content_type = random.choice(content_types)
                features = {
                    'complexity': random.uniform(1, 10),
                    'ai_generated': random.choice([True, False]),
                    'topic': random.choice(['marketing', 'ai', 'business', 'technology']),
                    'length': random.uniform(100, 2000)
                }
                quality_score = random.uniform(30, 95)
                ml_engine.add_content_features(content_id, content_type, features, quality_score)
            
            # Simular interacciones
            interaction_types = ['view', 'like', 'share', 'comment', 'create', 'ai_interaction']
            for _ in range(100):
                user_id = random.choice(users)
                content_id = f'content_{random.randint(1, 20)}'
                interaction_type = random.choice(interaction_types)
                rating = random.uniform(1, 5) if random.random() > 0.3 else None
                duration = random.randint(10, 300)
                ml_engine.record_interaction(user_id, content_id, interaction_type, rating, duration)
            
            print("✅ Datos de ejemplo simulados generados")
        
        elif choice == '10':
            print("👋 ¡Hasta luego!")
            break
        
        else:
            print("❌ Opción no válida")

if __name__ == "__main__":
    main()


