#!/usr/bin/env python3
"""
AI-Powered Personalization Engine for Affiliate Marketing
=========================================================

This module provides advanced personalization capabilities for affiliate marketing,
including behavioral analysis, dynamic content adaptation, and predictive personalization.

Author: AI Marketing System
Version: 2.0
"""

import pandas as pd
import numpy as np
import json
from typing import Dict, List, Optional, Tuple, Any
from datetime import datetime, timedelta
import asyncio
import aiohttp
from dataclasses import dataclass, asdict
from enum import Enum
import logging
from sklearn.cluster import KMeans, DBSCAN
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.ensemble import RandomForestClassifier
from sklearn.neural_network import MLPClassifier
from sklearn.metrics import silhouette_score, adjusted_rand_score
import openai
import torch
from transformers import pipeline, AutoTokenizer, AutoModel
import warnings
warnings.filterwarnings('ignore')

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class PersonalizationType(Enum):
    """Types of personalization"""
    CONTENT = "content"
    OFFER = "offer"
    TIMING = "timing"
    CHANNEL = "channel"
    FREQUENCY = "frequency"
    PRICING = "pricing"

class UserSegment(Enum):
    """User segmentation types"""
    BEHAVIORAL = "behavioral"
    DEMOGRAPHIC = "demographic"
    PSYCHOGRAPHIC = "psychographic"
    VALUE_BASED = "value_based"
    ENGAGEMENT = "engagement"

@dataclass
class UserProfile:
    """User profile data structure"""
    user_id: str
    demographics: Dict[str, Any]
    behavior_patterns: Dict[str, Any]
    preferences: Dict[str, Any]
    engagement_history: List[Dict]
    conversion_history: List[Dict]
    segment: str
    personalization_scores: Dict[str, float]
    last_updated: datetime

@dataclass
class PersonalizationRule:
    """Personalization rule data structure"""
    rule_id: str
    name: str
    description: str
    conditions: Dict[str, Any]
    actions: Dict[str, Any]
    priority: int
    is_active: bool
    created_at: datetime

@dataclass
class PersonalizedContent:
    """Personalized content data structure"""
    content_id: str
    user_id: str
    content_type: str
    personalized_content: Dict[str, Any]
    personalization_factors: List[str]
    confidence_score: float
    created_at: datetime

class AIPersonalizationEngine:
    """
    AI-Powered Personalization Engine for Affiliate Marketing
    """
    
    def __init__(self, openai_api_key: str):
        self.openai_api_key = openai_api_key
        openai.api_key = openai_api_key
        
        # Initialize user profiles and rules
        self.user_profiles = {}
        self.personalization_rules = []
        self.content_templates = {}
        self.segmentation_models = {}
        self.prediction_models = {}
        
        # Initialize AI models
        self._initialize_ai_models()
        
        # Initialize personalization parameters
        self.personalization_params = {
            'min_confidence_threshold': 0.7,
            'max_personalization_factors': 5,
            'segmentation_update_frequency': 24,  # hours
            'profile_update_frequency': 1  # hours
        }
    
    def _initialize_ai_models(self):
        """
        Initialize AI models for personalization
        """
        try:
            # Initialize sentiment analysis
            self.sentiment_analyzer = pipeline(
                "sentiment-analysis",
                model="cardiffnlp/twitter-roberta-base-sentiment-latest"
            )
            
            # Initialize text embedding model
            self.embedding_model = pipeline(
                "feature-extraction",
                model="sentence-transformers/all-MiniLM-L6-v2"
            )
            
            logger.info("AI models initialized successfully")
            
        except Exception as e:
            logger.warning(f"Could not initialize AI models: {str(e)}")
            self.sentiment_analyzer = None
            self.embedding_model = None
    
    def create_user_profile(self, user_id: str, demographics: Dict, 
                          behavior_patterns: Dict, preferences: Dict) -> UserProfile:
        """
        Create or update user profile
        """
        # Calculate personalization scores
        personalization_scores = self._calculate_personalization_scores(
            demographics, behavior_patterns, preferences
        )
        
        # Determine user segment
        segment = self._determine_user_segment(demographics, behavior_patterns, preferences)
        
        # Create user profile
        profile = UserProfile(
            user_id=user_id,
            demographics=demographics,
            behavior_patterns=behavior_patterns,
            preferences=preferences,
            engagement_history=[],
            conversion_history=[],
            segment=segment,
            personalization_scores=personalization_scores,
            last_updated=datetime.now()
        )
        
        self.user_profiles[user_id] = profile
        logger.info(f"Created user profile for {user_id}")
        
        return profile
    
    def _calculate_personalization_scores(self, demographics: Dict, 
                                        behavior_patterns: Dict, 
                                        preferences: Dict) -> Dict[str, float]:
        """
        Calculate personalization scores for different factors
        """
        scores = {}
        
        # Content personalization score
        scores['content'] = self._calculate_content_score(demographics, preferences)
        
        # Timing personalization score
        scores['timing'] = self._calculate_timing_score(behavior_patterns)
        
        # Channel personalization score
        scores['channel'] = self._calculate_channel_score(behavior_patterns, preferences)
        
        # Offer personalization score
        scores['offer'] = self._calculate_offer_score(demographics, preferences)
        
        # Frequency personalization score
        scores['frequency'] = self._calculate_frequency_score(behavior_patterns)
        
        return scores
    
    def _calculate_content_score(self, demographics: Dict, preferences: Dict) -> float:
        """
        Calculate content personalization score
        """
        score = 0.0
        
        # Age-based scoring
        if 'age' in demographics:
            age = demographics['age']
            if 18 <= age <= 25:
                score += 0.3
            elif 26 <= age <= 35:
                score += 0.4
            elif 36 <= age <= 45:
                score += 0.5
            elif 46 <= age <= 55:
                score += 0.4
            else:
                score += 0.3
        
        # Interest-based scoring
        if 'interests' in preferences:
            interests = preferences['interests']
            score += min(0.5, len(interests) * 0.1)
        
        # Content preference scoring
        if 'content_preferences' in preferences:
            content_prefs = preferences['content_preferences']
            score += min(0.2, len(content_prefs) * 0.05)
        
        return min(1.0, score)
    
    def _calculate_timing_score(self, behavior_patterns: Dict) -> float:
        """
        Calculate timing personalization score
        """
        score = 0.0
        
        # Activity pattern scoring
        if 'activity_patterns' in behavior_patterns:
            patterns = behavior_patterns['activity_patterns']
            if 'peak_hours' in patterns:
                score += 0.4
            if 'timezone' in patterns:
                score += 0.3
            if 'day_preferences' in patterns:
                score += 0.3
        
        return min(1.0, score)
    
    def _calculate_channel_score(self, behavior_patterns: Dict, preferences: Dict) -> float:
        """
        Calculate channel personalization score
        """
        score = 0.0
        
        # Channel usage patterns
        if 'channel_usage' in behavior_patterns:
            channel_usage = behavior_patterns['channel_usage']
            active_channels = sum(1 for usage in channel_usage.values() if usage > 0)
            score += min(0.5, active_channels * 0.1)
        
        # Channel preferences
        if 'preferred_channels' in preferences:
            preferred_channels = preferences['preferred_channels']
            score += min(0.5, len(preferred_channels) * 0.1)
        
        return min(1.0, score)
    
    def _calculate_offer_score(self, demographics: Dict, preferences: Dict) -> float:
        """
        Calculate offer personalization score
        """
        score = 0.0
        
        # Income-based scoring
        if 'income' in demographics:
            income = demographics['income']
            if income > 100000:
                score += 0.4
            elif income > 50000:
                score += 0.3
            else:
                score += 0.2
        
        # Purchase history scoring
        if 'purchase_history' in preferences:
            purchase_history = preferences['purchase_history']
            if len(purchase_history) > 0:
                score += min(0.4, len(purchase_history) * 0.05)
        
        # Price sensitivity scoring
        if 'price_sensitivity' in preferences:
            price_sensitivity = preferences['price_sensitivity']
            if price_sensitivity == 'low':
                score += 0.2
            elif price_sensitivity == 'medium':
                score += 0.1
        
        return min(1.0, score)
    
    def _calculate_frequency_score(self, behavior_patterns: Dict) -> float:
        """
        Calculate frequency personalization score
        """
        score = 0.0
        
        # Engagement frequency
        if 'engagement_frequency' in behavior_patterns:
            freq = behavior_patterns['engagement_frequency']
            if freq == 'high':
                score += 0.5
            elif freq == 'medium':
                score += 0.3
            elif freq == 'low':
                score += 0.1
        
        # Response patterns
        if 'response_patterns' in behavior_patterns:
            response_patterns = behavior_patterns['response_patterns']
            if 'quick_responder' in response_patterns:
                score += 0.3
            if 'consistent_responder' in response_patterns:
                score += 0.2
        
        return min(1.0, score)
    
    def _determine_user_segment(self, demographics: Dict, 
                               behavior_patterns: Dict, 
                               preferences: Dict) -> str:
        """
        Determine user segment
        """
        # Simple segmentation logic
        # In practice, use more sophisticated clustering algorithms
        
        if 'age' in demographics:
            age = demographics['age']
            if age < 30:
                return 'young_professionals'
            elif age < 50:
                return 'middle_aged_professionals'
            else:
                return 'senior_professionals'
        
        return 'general_audience'
    
    def update_user_profile(self, user_id: str, new_data: Dict) -> UserProfile:
        """
        Update user profile with new data
        """
        if user_id not in self.user_profiles:
            logger.error(f"User profile {user_id} not found")
            return None
        
        profile = self.user_profiles[user_id]
        
        # Update demographics
        if 'demographics' in new_data:
            profile.demographics.update(new_data['demographics'])
        
        # Update behavior patterns
        if 'behavior_patterns' in new_data:
            profile.behavior_patterns.update(new_data['behavior_patterns'])
        
        # Update preferences
        if 'preferences' in new_data:
            profile.preferences.update(new_data['preferences'])
        
        # Recalculate personalization scores
        profile.personalization_scores = self._calculate_personalization_scores(
            profile.demographics, profile.behavior_patterns, profile.preferences
        )
        
        # Update segment
        profile.segment = self._determine_user_segment(
            profile.demographics, profile.behavior_patterns, profile.preferences
        )
        
        # Update timestamp
        profile.last_updated = datetime.now()
        
        logger.info(f"Updated user profile for {user_id}")
        return profile
    
    def add_engagement_data(self, user_id: str, engagement_data: Dict):
        """
        Add engagement data to user profile
        """
        if user_id not in self.user_profiles:
            logger.error(f"User profile {user_id} not found")
            return
        
        profile = self.user_profiles[user_id]
        profile.engagement_history.append({
            **engagement_data,
            'timestamp': datetime.now()
        })
        
        # Update behavior patterns based on engagement
        self._update_behavior_patterns(profile, engagement_data)
    
    def add_conversion_data(self, user_id: str, conversion_data: Dict):
        """
        Add conversion data to user profile
        """
        if user_id not in self.user_profiles:
            logger.error(f"User profile {user_id} not found")
            return
        
        profile = self.user_profiles[user_id]
        profile.conversion_history.append({
            **conversion_data,
            'timestamp': datetime.now()
        })
        
        # Update preferences based on conversion
        self._update_preferences_from_conversion(profile, conversion_data)
    
    def _update_behavior_patterns(self, profile: UserProfile, engagement_data: Dict):
        """
        Update behavior patterns based on engagement data
        """
        # Update activity patterns
        if 'activity_patterns' not in profile.behavior_patterns:
            profile.behavior_patterns['activity_patterns'] = {}
        
        # Update peak hours
        if 'timestamp' in engagement_data:
            hour = engagement_data['timestamp'].hour
            if 'peak_hours' not in profile.behavior_patterns['activity_patterns']:
                profile.behavior_patterns['activity_patterns']['peak_hours'] = []
            
            peak_hours = profile.behavior_patterns['activity_patterns']['peak_hours']
            if hour not in peak_hours:
                peak_hours.append(hour)
        
        # Update channel usage
        if 'channel' in engagement_data:
            channel = engagement_data['channel']
            if 'channel_usage' not in profile.behavior_patterns:
                profile.behavior_patterns['channel_usage'] = {}
            
            if channel not in profile.behavior_patterns['channel_usage']:
                profile.behavior_patterns['channel_usage'][channel] = 0
            
            profile.behavior_patterns['channel_usage'][channel] += 1
    
    def _update_preferences_from_conversion(self, profile: UserProfile, conversion_data: Dict):
        """
        Update preferences based on conversion data
        """
        # Update purchase history
        if 'purchase_history' not in profile.preferences:
            profile.preferences['purchase_history'] = []
        
        profile.preferences['purchase_history'].append({
            'product': conversion_data.get('product', ''),
            'amount': conversion_data.get('amount', 0),
            'timestamp': conversion_data.get('timestamp', datetime.now())
        })
        
        # Update price sensitivity
        if 'amount' in conversion_data:
            amount = conversion_data['amount']
            if 'price_sensitivity' not in profile.preferences:
                profile.preferences['price_sensitivity'] = 'medium'
            
            if amount > 1000:
                profile.preferences['price_sensitivity'] = 'low'
            elif amount < 100:
                profile.preferences['price_sensitivity'] = 'high'
    
    def create_personalization_rule(self, name: str, description: str, 
                                  conditions: Dict, actions: Dict, 
                                  priority: int = 1) -> PersonalizationRule:
        """
        Create personalization rule
        """
        rule = PersonalizationRule(
            rule_id=f"rule_{len(self.personalization_rules)}",
            name=name,
            description=description,
            conditions=conditions,
            actions=actions,
            priority=priority,
            is_active=True,
            created_at=datetime.now()
        )
        
        self.personalization_rules.append(rule)
        logger.info(f"Created personalization rule: {name}")
        
        return rule
    
    def personalize_content(self, user_id: str, content_type: str, 
                          base_content: Dict) -> PersonalizedContent:
        """
        Personalize content for user
        """
        if user_id not in self.user_profiles:
            logger.error(f"User profile {user_id} not found")
            return None
        
        profile = self.user_profiles[user_id]
        
        # Apply personalization rules
        personalized_content = base_content.copy()
        personalization_factors = []
        
        for rule in sorted(self.personalization_rules, key=lambda r: r.priority):
            if rule.is_active and self._evaluate_rule_conditions(rule, profile):
                personalized_content = self._apply_rule_actions(rule, personalized_content)
                personalization_factors.append(rule.name)
        
        # Apply AI-powered personalization
        ai_personalized_content = self._apply_ai_personalization(
            profile, content_type, personalized_content
        )
        
        # Calculate confidence score
        confidence_score = self._calculate_personalization_confidence(
            profile, personalization_factors
        )
        
        # Create personalized content object
        personalized_content_obj = PersonalizedContent(
            content_id=f"content_{len(self.user_profiles)}",
            user_id=user_id,
            content_type=content_type,
            personalized_content=ai_personalized_content,
            personalization_factors=personalization_factors,
            confidence_score=confidence_score,
            created_at=datetime.now()
        )
        
        return personalized_content_obj
    
    def _evaluate_rule_conditions(self, rule: PersonalizationRule, 
                                 profile: UserProfile) -> bool:
        """
        Evaluate rule conditions
        """
        conditions = rule.conditions
        
        # Check demographic conditions
        if 'demographics' in conditions:
            demo_conditions = conditions['demographics']
            for key, value in demo_conditions.items():
                if key not in profile.demographics:
                    return False
                if profile.demographics[key] != value:
                    return False
        
        # Check behavior conditions
        if 'behavior_patterns' in conditions:
            behavior_conditions = conditions['behavior_patterns']
            for key, value in behavior_conditions.items():
                if key not in profile.behavior_patterns:
                    return False
                if profile.behavior_patterns[key] != value:
                    return False
        
        # Check preference conditions
        if 'preferences' in conditions:
            preference_conditions = conditions['preferences']
            for key, value in preference_conditions.items():
                if key not in profile.preferences:
                    return False
                if profile.preferences[key] != value:
                    return False
        
        return True
    
    def _apply_rule_actions(self, rule: PersonalizationRule, 
                           content: Dict) -> Dict:
        """
        Apply rule actions to content
        """
        actions = rule.actions
        updated_content = content.copy()
        
        # Apply content modifications
        if 'content_modifications' in actions:
            modifications = actions['content_modifications']
            for key, value in modifications.items():
                updated_content[key] = value
        
        # Apply personalization tags
        if 'personalization_tags' in actions:
            tags = actions['personalization_tags']
            if 'tags' not in updated_content:
                updated_content['tags'] = []
            updated_content['tags'].extend(tags)
        
        return updated_content
    
    def _apply_ai_personalization(self, profile: UserProfile, 
                                 content_type: str, content: Dict) -> Dict:
        """
        Apply AI-powered personalization
        """
        personalized_content = content.copy()
        
        # Personalize based on user segment
        if profile.segment == 'young_professionals':
            personalized_content = self._personalize_for_young_professionals(
                personalized_content, profile
            )
        elif profile.segment == 'middle_aged_professionals':
            personalized_content = self._personalize_for_middle_aged_professionals(
                personalized_content, profile
            )
        elif profile.segment == 'senior_professionals':
            personalized_content = self._personalize_for_senior_professionals(
                personalized_content, profile
            )
        
        # Personalize based on personalization scores
        if profile.personalization_scores['content'] > 0.7:
            personalized_content = self._enhance_content_personalization(
                personalized_content, profile
            )
        
        if profile.personalization_scores['timing'] > 0.7:
            personalized_content = self._enhance_timing_personalization(
                personalized_content, profile
            )
        
        return personalized_content
    
    def _personalize_for_young_professionals(self, content: Dict, 
                                           profile: UserProfile) -> Dict:
        """
        Personalize content for young professionals
        """
        personalized_content = content.copy()
        
        # Add youthful language
        if 'title' in personalized_content:
            personalized_content['title'] = f"🚀 {personalized_content['title']}"
        
        # Add urgency
        if 'call_to_action' in personalized_content:
            personalized_content['call_to_action'] = f"Get Started Now! {personalized_content['call_to_action']}"
        
        return personalized_content
    
    def _personalize_for_middle_aged_professionals(self, content: Dict, 
                                                 profile: UserProfile) -> Dict:
        """
        Personalize content for middle-aged professionals
        """
        personalized_content = content.copy()
        
        # Add professional language
        if 'title' in personalized_content:
            personalized_content['title'] = f"Professional: {personalized_content['title']}"
        
        # Add value proposition
        if 'description' in personalized_content:
            personalized_content['description'] = f"Proven Results: {personalized_content['description']}"
        
        return personalized_content
    
    def _personalize_for_senior_professionals(self, content: Dict, 
                                            profile: UserProfile) -> Dict:
        """
        Personalize content for senior professionals
        """
        personalized_content = content.copy()
        
        # Add authoritative language
        if 'title' in personalized_content:
            personalized_content['title'] = f"Expert: {personalized_content['title']}"
        
        # Add trust indicators
        if 'description' in personalized_content:
            personalized_content['description'] = f"Trusted Solution: {personalized_content['description']}"
        
        return personalized_content
    
    def _enhance_content_personalization(self, content: Dict, 
                                       profile: UserProfile) -> Dict:
        """
        Enhance content personalization
        """
        personalized_content = content.copy()
        
        # Add personalized recommendations
        if 'recommendations' not in personalized_content:
            personalized_content['recommendations'] = []
        
        # Add interest-based recommendations
        if 'interests' in profile.preferences:
            interests = profile.preferences['interests']
            personalized_content['recommendations'].extend(interests[:3])
        
        return personalized_content
    
    def _enhance_timing_personalization(self, content: Dict, 
                                      profile: UserProfile) -> Dict:
        """
        Enhance timing personalization
        """
        personalized_content = content.copy()
        
        # Add timing information
        if 'activity_patterns' in profile.behavior_patterns:
            patterns = profile.behavior_patterns['activity_patterns']
            if 'peak_hours' in patterns:
                peak_hours = patterns['peak_hours']
                personalized_content['optimal_timing'] = f"Best time: {peak_hours[0]}:00"
        
        return personalized_content
    
    def _calculate_personalization_confidence(self, profile: UserProfile, 
                                            personalization_factors: List[str]) -> float:
        """
        Calculate personalization confidence score
        """
        # Base confidence on personalization scores
        base_confidence = np.mean(list(profile.personalization_scores.values()))
        
        # Boost confidence based on number of factors applied
        factor_boost = min(0.3, len(personalization_factors) * 0.05)
        
        # Boost confidence based on profile completeness
        completeness_boost = self._calculate_profile_completeness(profile) * 0.2
        
        total_confidence = base_confidence + factor_boost + completeness_boost
        
        return min(1.0, total_confidence)
    
    def _calculate_profile_completeness(self, profile: UserProfile) -> float:
        """
        Calculate profile completeness score
        """
        completeness = 0.0
        
        # Demographics completeness
        demo_fields = ['age', 'gender', 'location', 'income']
        demo_completeness = sum(1 for field in demo_fields if field in profile.demographics) / len(demo_fields)
        completeness += demo_completeness * 0.3
        
        # Behavior patterns completeness
        behavior_fields = ['activity_patterns', 'channel_usage', 'engagement_frequency']
        behavior_completeness = sum(1 for field in behavior_fields if field in profile.behavior_patterns) / len(behavior_fields)
        completeness += behavior_completeness * 0.4
        
        # Preferences completeness
        preference_fields = ['interests', 'content_preferences', 'preferred_channels']
        preference_completeness = sum(1 for field in preference_fields if field in profile.preferences) / len(preference_fields)
        completeness += preference_completeness * 0.3
        
        return completeness
    
    def segment_users(self, segmentation_type: UserSegment = UserSegment.BEHAVIORAL) -> Dict:
        """
        Segment users using AI clustering
        """
        if not self.user_profiles:
            return {}
        
        # Prepare data for clustering
        user_data = []
        user_ids = []
        
        for user_id, profile in self.user_profiles.items():
            user_vector = self._create_user_vector(profile, segmentation_type)
            user_data.append(user_vector)
            user_ids.append(user_id)
        
        user_data = np.array(user_data)
        
        # Perform clustering
        if segmentation_type == UserSegment.BEHAVIORAL:
            n_clusters = min(5, len(user_data) // 2)
            if n_clusters < 2:
                n_clusters = 2
            
            kmeans = KMeans(n_clusters=n_clusters, random_state=42)
            cluster_labels = kmeans.fit_predict(user_data)
            
            # Calculate silhouette score
            silhouette_avg = silhouette_score(user_data, cluster_labels)
            
        else:
            # Use DBSCAN for other segmentation types
            dbscan = DBSCAN(eps=0.5, min_samples=2)
            cluster_labels = dbscan.fit_predict(user_data)
            
            # Calculate silhouette score
            if len(set(cluster_labels)) > 1:
                silhouette_avg = silhouette_score(user_data, cluster_labels)
            else:
                silhouette_avg = 0.0
        
        # Create segment mapping
        segments = {}
        for user_id, label in zip(user_ids, cluster_labels):
            segment_name = f"segment_{label}"
            if segment_name not in segments:
                segments[segment_name] = []
            segments[segment_name].append(user_id)
        
        # Update user profiles with segments
        for user_id, label in zip(user_ids, cluster_labels):
            if user_id in self.user_profiles:
                self.user_profiles[user_id].segment = f"segment_{label}"
        
        return {
            'segments': segments,
            'silhouette_score': silhouette_avg,
            'segmentation_type': segmentation_type.value,
            'num_segments': len(set(cluster_labels))
        }
    
    def _create_user_vector(self, profile: UserProfile, 
                           segmentation_type: UserSegment) -> List[float]:
        """
        Create user vector for clustering
        """
        vector = []
        
        if segmentation_type == UserSegment.BEHAVIORAL:
            # Behavioral features
            vector.extend([
                profile.personalization_scores.get('content', 0),
                profile.personalization_scores.get('timing', 0),
                profile.personalization_scores.get('channel', 0),
                profile.personalization_scores.get('offer', 0),
                profile.personalization_scores.get('frequency', 0)
            ])
            
            # Engagement features
            vector.append(len(profile.engagement_history))
            vector.append(len(profile.conversion_history))
            
        elif segmentation_type == UserSegment.DEMOGRAPHIC:
            # Demographic features
            vector.extend([
                profile.demographics.get('age', 0) / 100.0,  # Normalize age
                profile.demographics.get('income', 0) / 100000.0,  # Normalize income
                1 if profile.demographics.get('gender') == 'male' else 0,
                1 if profile.demographics.get('gender') == 'female' else 0
            ])
            
        elif segmentation_type == UserSegment.VALUE_BASED:
            # Value-based features
            total_value = sum(conv.get('amount', 0) for conv in profile.conversion_history)
            vector.extend([
                total_value / 10000.0,  # Normalize total value
                len(profile.conversion_history),
                profile.personalization_scores.get('offer', 0)
            ])
        
        return vector
    
    def get_personalization_insights(self) -> Dict:
        """
        Get personalization insights and recommendations
        """
        if not self.user_profiles:
            return {}
        
        # Calculate overall personalization metrics
        total_users = len(self.user_profiles)
        avg_personalization_score = np.mean([
            np.mean(list(profile.personalization_scores.values()))
            for profile in self.user_profiles.values()
        ])
        
        # Calculate segment distribution
        segment_distribution = {}
        for profile in self.user_profiles.values():
            segment = profile.segment
            if segment not in segment_distribution:
                segment_distribution[segment] = 0
            segment_distribution[segment] += 1
        
        # Calculate personalization factor usage
        factor_usage = {}
        for profile in self.user_profiles.values():
            for factor, score in profile.personalization_scores.items():
                if factor not in factor_usage:
                    factor_usage[factor] = []
                factor_usage[factor].append(score)
        
        factor_avg_scores = {
            factor: np.mean(scores) for factor, scores in factor_usage.items()
        }
        
        # Generate recommendations
        recommendations = self._generate_personalization_recommendations(
            avg_personalization_score, segment_distribution, factor_avg_scores
        )
        
        return {
            'total_users': total_users,
            'avg_personalization_score': avg_personalization_score,
            'segment_distribution': segment_distribution,
            'factor_avg_scores': factor_avg_scores,
            'recommendations': recommendations,
            'timestamp': datetime.now().isoformat()
        }
    
    def _generate_personalization_recommendations(self, avg_score: float, 
                                                segment_dist: Dict, 
                                                factor_scores: Dict) -> List[str]:
        """
        Generate personalization recommendations
        """
        recommendations = []
        
        # Overall personalization score recommendations
        if avg_score < 0.5:
            recommendations.append("Overall personalization score is low. Consider improving user data collection.")
        elif avg_score > 0.8:
            recommendations.append("Personalization is performing well. Consider advanced personalization strategies.")
        
        # Segment distribution recommendations
        if len(segment_dist) < 3:
            recommendations.append("Consider creating more user segments for better targeting.")
        
        # Factor-specific recommendations
        for factor, score in factor_scores.items():
            if score < 0.4:
                recommendations.append(f"Improve {factor} personalization. Current score: {score:.2f}")
            elif score > 0.8:
                recommendations.append(f"{factor} personalization is excellent. Leverage this strength.")
        
        return recommendations
    
    def export_personalization_data(self, format: str = 'json') -> str:
        """
        Export personalization data
        """
        data = {
            'user_profiles': {uid: asdict(profile) for uid, profile in self.user_profiles.items()},
            'personalization_rules': [asdict(rule) for rule in self.personalization_rules],
            'insights': self.get_personalization_insights()
        }
        
        if format == 'json':
            return json.dumps(data, indent=2, default=str)
        elif format == 'csv':
            # Export user profiles as CSV
            if self.user_profiles:
                df = pd.DataFrame([asdict(profile) for profile in self.user_profiles.values()])
                return df.to_csv(index=False)
            else:
                return ""
        else:
            raise ValueError(f"Unsupported format: {format}")

# Example usage
async def main():
    """
    Example usage of AI Personalization Engine
    """
    # Initialize personalization engine
    engine = AIPersonalizationEngine(openai_api_key="your-openai-api-key")
    
    # Create user profiles
    user1 = engine.create_user_profile(
        user_id="user_1",
        demographics={"age": 28, "gender": "female", "income": 75000},
        behavior_patterns={"engagement_frequency": "high", "channel_usage": {"email": 5, "sms": 2}},
        preferences={"interests": ["technology", "fitness"], "content_preferences": ["video", "articles"]}
    )
    
    user2 = engine.create_user_profile(
        user_id="user_2",
        demographics={"age": 45, "gender": "male", "income": 120000},
        behavior_patterns={"engagement_frequency": "medium", "channel_usage": {"email": 3, "linkedin": 4}},
        preferences={"interests": ["business", "finance"], "content_preferences": ["reports", "webinars"]}
    )
    
    # Create personalization rules
    rule1 = engine.create_personalization_rule(
        name="High Engagement Users",
        description="Personalize for high engagement users",
        conditions={"behavior_patterns": {"engagement_frequency": "high"}},
        actions={"content_modifications": {"tone": "energetic"}},
        priority=1
    )
    
    # Personalize content
    base_content = {
        "title": "New Product Launch",
        "description": "Check out our latest product",
        "call_to_action": "Learn More"
    }
    
    personalized_content1 = engine.personalize_content("user_1", "email", base_content)
    personalized_content2 = engine.personalize_content("user_2", "email", base_content)
    
    print(f"User 1 personalized content: {personalized_content1.personalized_content}")
    print(f"User 2 personalized content: {personalized_content2.personalized_content}")
    
    # Segment users
    segments = engine.segment_users(UserSegment.BEHAVIORAL)
    print(f"User segments: {segments}")
    
    # Get insights
    insights = engine.get_personalization_insights()
    print(f"Personalization insights: {insights}")

if __name__ == "__main__":
    asyncio.run(main())


