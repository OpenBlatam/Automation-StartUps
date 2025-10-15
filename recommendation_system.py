"""
Advanced Recommendation System for Ultimate Launch Planning System
Provides personalized recommendations using collaborative filtering, content-based filtering, and hybrid approaches
"""

import numpy as np
import pandas as pd
import json
import time
import threading
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple, Union
from dataclasses import dataclass, asdict
from collections import defaultdict, deque
import logging
from enum import Enum
import uuid
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.decomposition import NMF, TruncatedSVD
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler, LabelEncoder
import warnings
warnings.filterwarnings('ignore')

logger = logging.getLogger(__name__)

class RecommendationType(Enum):
    LAUNCH_STRATEGY = "launch_strategy"
    BUDGET_ALLOCATION = "budget_allocation"
    TEAM_COMPOSITION = "team_composition"
    TIMELINE_OPTIMIZATION = "timeline_optimization"
    RISK_MITIGATION = "risk_mitigation"
    MARKET_APPROACH = "market_approach"
    TECHNOLOGY_STACK = "technology_stack"
    PARTNERSHIP_OPPORTUNITIES = "partnership_opportunities"

class RecommendationAlgorithm(Enum):
    COLLABORATIVE_FILTERING = "collaborative_filtering"
    CONTENT_BASED = "content_based"
    HYBRID = "hybrid"
    MATRIX_FACTORIZATION = "matrix_factorization"
    DEEP_LEARNING = "deep_learning"
    ASSOCIATION_RULES = "association_rules"

class RecommendationConfidence(Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    VERY_HIGH = "very_high"

@dataclass
class Recommendation:
    id: str
    recommendation_type: RecommendationType
    title: str
    description: str
    confidence: RecommendationConfidence
    confidence_score: float
    algorithm: RecommendationAlgorithm
    reasoning: str
    expected_impact: str
    implementation_effort: str
    cost_estimate: float
    timeline_estimate: int
    success_probability: float
    metadata: Dict[str, Any]
    created_at: datetime
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "recommendation_type": self.recommendation_type.value,
            "title": self.title,
            "description": self.description,
            "confidence": self.confidence.value,
            "confidence_score": self.confidence_score,
            "algorithm": self.algorithm.value,
            "reasoning": self.reasoning,
            "expected_impact": self.expected_impact,
            "implementation_effort": self.implementation_effort,
            "cost_estimate": self.cost_estimate,
            "timeline_estimate": self.timeline_estimate,
            "success_probability": self.success_probability,
            "metadata": self.metadata,
            "created_at": self.created_at.isoformat()
        }

@dataclass
class UserProfile:
    user_id: str
    preferences: Dict[str, Any]
    historical_launches: List[Dict[str, Any]]
    success_patterns: Dict[str, float]
    skill_set: List[str]
    industry_experience: str
    company_size: str
    risk_tolerance: float
    budget_range: Tuple[float, float]
    timeline_preference: str
    last_updated: datetime
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "user_id": self.user_id,
            "preferences": self.preferences,
            "historical_launches": self.historical_launches,
            "success_patterns": self.success_patterns,
            "skill_set": self.skill_set,
            "industry_experience": self.industry_experience,
            "company_size": self.company_size,
            "risk_tolerance": self.risk_tolerance,
            "budget_range": self.budget_range,
            "timeline_preference": self.timeline_preference,
            "last_updated": self.last_updated.isoformat()
        }

class RecommendationEngine:
    """Advanced recommendation system for launch planning"""
    
    def __init__(self):
        self.user_profiles: Dict[str, UserProfile] = {}
        self.recommendations: Dict[str, Recommendation] = {}
        self.recommendation_history: deque = deque(maxlen=10000)
        self.launch_data: List[Dict[str, Any]] = []
        self.lock = threading.RLock()
        
        # ML models
        self.tfidf_vectorizer = TfidfVectorizer(max_features=1000, stop_words='english')
        self.nmf_model = None
        self.svd_model = None
        self.kmeans_model = None
        self.scaler = StandardScaler()
        
        # Recommendation matrices
        self.user_item_matrix = None
        self.item_similarity_matrix = None
        self.user_similarity_matrix = None
        
        # Load sample data
        self._load_sample_data()
        
        logger.info("Recommendation Engine initialized")
    
    def _load_sample_data(self):
        """Load sample launch data for training"""
        sample_launches = [
            {
                "launch_id": "launch_001",
                "product_type": "SaaS Platform",
                "industry": "Technology",
                "budget": 500000,
                "team_size": 15,
                "timeline_days": 120,
                "success_rate": 0.85,
                "strategies_used": ["agile_development", "beta_testing", "influencer_marketing"],
                "technologies": ["python", "react", "aws", "docker"],
                "market_approach": "direct_sales",
                "risk_mitigation": ["phased_rollout", "backup_planning", "stakeholder_communication"]
            },
            {
                "launch_id": "launch_002",
                "product_type": "Mobile App",
                "industry": "Healthcare",
                "budget": 300000,
                "team_size": 10,
                "timeline_days": 90,
                "success_rate": 0.92,
                "strategies_used": ["user_research", "mvp_approach", "social_media_marketing"],
                "technologies": ["react_native", "nodejs", "mongodb", "firebase"],
                "market_approach": "app_store_optimization",
                "risk_mitigation": ["regulatory_compliance", "data_privacy", "user_testing"]
            },
            {
                "launch_id": "launch_003",
                "product_type": "E-commerce Platform",
                "industry": "Retail",
                "budget": 750000,
                "team_size": 20,
                "timeline_days": 150,
                "success_rate": 0.78,
                "strategies_used": ["market_research", "competitive_analysis", "seo_optimization"],
                "technologies": ["shopify", "react", "python", "postgresql"],
                "market_approach": "content_marketing",
                "risk_mitigation": ["inventory_management", "payment_security", "customer_support"]
            }
        ]
        
        self.launch_data.extend(sample_launches)
        self._train_models()
    
    def _train_models(self):
        """Train recommendation models"""
        if not self.launch_data:
            return
        
        try:
            # Prepare features for content-based filtering
            features = []
            for launch in self.launch_data:
                feature_text = f"{launch['product_type']} {launch['industry']} {' '.join(launch['strategies_used'])} {' '.join(launch['technologies'])}"
                features.append(feature_text)
            
            # TF-IDF vectorization
            tfidf_matrix = self.tfidf_vectorizer.fit_transform(features)
            
            # Matrix factorization
            self.nmf_model = NMF(n_components=10, random_state=42)
            self.nmf_model.fit(tfidf_matrix)
            
            self.svd_model = TruncatedSVD(n_components=10, random_state=42)
            self.svd_model.fit(tfidf_matrix)
            
            # Clustering
            feature_matrix = np.array([
                [launch['budget'], launch['team_size'], launch['timeline_days'], launch['success_rate']]
                for launch in self.launch_data
            ])
            
            self.kmeans_model = KMeans(n_clusters=3, random_state=42)
            self.kmeans_model.fit(feature_matrix)
            
            # Calculate similarity matrices
            self.item_similarity_matrix = cosine_similarity(tfidf_matrix)
            
            logger.info("Recommendation models trained successfully")
            
        except Exception as e:
            logger.error(f"Error training models: {e}")
    
    def create_user_profile(self, user_id: str, preferences: Dict[str, Any]) -> UserProfile:
        """Create or update user profile"""
        profile = UserProfile(
            user_id=user_id,
            preferences=preferences,
            historical_launches=preferences.get("historical_launches", []),
            success_patterns=preferences.get("success_patterns", {}),
            skill_set=preferences.get("skill_set", []),
            industry_experience=preferences.get("industry_experience", "Technology"),
            company_size=preferences.get("company_size", "Medium"),
            risk_tolerance=preferences.get("risk_tolerance", 0.5),
            budget_range=preferences.get("budget_range", (100000, 1000000)),
            timeline_preference=preferences.get("timeline_preference", "Medium"),
            last_updated=datetime.now()
        )
        
        with self.lock:
            self.user_profiles[user_id] = profile
        
        logger.info(f"Created user profile for {user_id}")
        return profile
    
    def get_recommendations(self, user_id: str, launch_context: Dict[str, Any], 
                          recommendation_types: List[RecommendationType] = None,
                          num_recommendations: int = 5) -> List[Recommendation]:
        """Get personalized recommendations for a user"""
        if user_id not in self.user_profiles:
            # Create default profile
            self.create_user_profile(user_id, {})
        
        user_profile = self.user_profiles[user_id]
        
        if recommendation_types is None:
            recommendation_types = list(RecommendationType)
        
        recommendations = []
        
        for rec_type in recommendation_types:
            recs = self._generate_recommendations_for_type(
                user_profile, launch_context, rec_type, num_recommendations
            )
            recommendations.extend(recs)
        
        # Sort by confidence score
        recommendations.sort(key=lambda x: x.confidence_score, reverse=True)
        
        # Store recommendations
        with self.lock:
            for rec in recommendations:
                self.recommendations[rec.id] = rec
                self.recommendation_history.append(rec)
        
        return recommendations[:num_recommendations]
    
    def _generate_recommendations_for_type(self, user_profile: UserProfile, 
                                         launch_context: Dict[str, Any],
                                         rec_type: RecommendationType,
                                         num_recommendations: int) -> List[Recommendation]:
        """Generate recommendations for a specific type"""
        recommendations = []
        
        if rec_type == RecommendationType.LAUNCH_STRATEGY:
            recommendations = self._recommend_launch_strategies(user_profile, launch_context)
        elif rec_type == RecommendationType.BUDGET_ALLOCATION:
            recommendations = self._recommend_budget_allocation(user_profile, launch_context)
        elif rec_type == RecommendationType.TEAM_COMPOSITION:
            recommendations = self._recommend_team_composition(user_profile, launch_context)
        elif rec_type == RecommendationType.TIMELINE_OPTIMIZATION:
            recommendations = self._recommend_timeline_optimization(user_profile, launch_context)
        elif rec_type == RecommendationType.RISK_MITIGATION:
            recommendations = self._recommend_risk_mitigation(user_profile, launch_context)
        elif rec_type == RecommendationType.MARKET_APPROACH:
            recommendations = self._recommend_market_approach(user_profile, launch_context)
        elif rec_type == RecommendationType.TECHNOLOGY_STACK:
            recommendations = self._recommend_technology_stack(user_profile, launch_context)
        elif rec_type == RecommendationType.PARTNERSHIP_OPPORTUNITIES:
            recommendations = self._recommend_partnership_opportunities(user_profile, launch_context)
        
        return recommendations[:num_recommendations]
    
    def _recommend_launch_strategies(self, user_profile: UserProfile, 
                                   launch_context: Dict[str, Any]) -> List[Recommendation]:
        """Recommend launch strategies"""
        recommendations = []
        
        # Analyze similar successful launches
        similar_launches = self._find_similar_launches(launch_context)
        
        # Extract successful strategies
        successful_strategies = defaultdict(int)
        for launch in similar_launches:
            if launch['success_rate'] > 0.8:
                for strategy in launch['strategies_used']:
                    successful_strategies[strategy] += 1
        
        # Generate recommendations
        for strategy, count in successful_strategies.items():
            confidence_score = min(1.0, count / len(similar_launches))
            
            recommendation = Recommendation(
                id=str(uuid.uuid4()),
                recommendation_type=RecommendationType.LAUNCH_STRATEGY,
                title=f"Implement {strategy.replace('_', ' ').title()} Strategy",
                description=f"Based on {count} successful launches, {strategy.replace('_', ' ')} has shown high success rates.",
                confidence=self._get_confidence_level(confidence_score),
                confidence_score=confidence_score,
                algorithm=RecommendationAlgorithm.COLLABORATIVE_FILTERING,
                reasoning=f"Found in {count} successful launches with average success rate of {np.mean([l['success_rate'] for l in similar_launches if strategy in l['strategies_used']]):.2f}",
                expected_impact="High - Proven strategy with strong success track record",
                implementation_effort="Medium - Requires planning and execution",
                cost_estimate=self._estimate_strategy_cost(strategy, launch_context),
                timeline_estimate=self._estimate_strategy_timeline(strategy),
                success_probability=confidence_score * 0.9,
                metadata={"strategy": strategy, "similar_launches": len(similar_launches)},
                created_at=datetime.now()
            )
            
            recommendations.append(recommendation)
        
        return recommendations
    
    def _recommend_budget_allocation(self, user_profile: UserProfile, 
                                   launch_context: Dict[str, Any]) -> List[Recommendation]:
        """Recommend budget allocation strategies"""
        recommendations = []
        
        total_budget = launch_context.get('budget', 500000)
        industry = launch_context.get('industry', 'Technology')
        
        # Industry-specific budget recommendations
        industry_allocations = {
            'Technology': {'development': 0.4, 'marketing': 0.3, 'operations': 0.2, 'contingency': 0.1},
            'Healthcare': {'development': 0.5, 'compliance': 0.2, 'marketing': 0.15, 'operations': 0.1, 'contingency': 0.05},
            'Retail': {'marketing': 0.4, 'operations': 0.3, 'development': 0.2, 'contingency': 0.1},
            'Finance': {'development': 0.4, 'compliance': 0.25, 'security': 0.15, 'marketing': 0.1, 'contingency': 0.1}
        }
        
        recommended_allocation = industry_allocations.get(industry, industry_allocations['Technology'])
        
        for category, percentage in recommended_allocation.items():
            amount = total_budget * percentage
            
            recommendation = Recommendation(
                id=str(uuid.uuid4()),
                recommendation_type=RecommendationType.BUDGET_ALLOCATION,
                title=f"Allocate {percentage*100:.1f}% to {category.title()}",
                description=f"Recommended budget allocation of ${amount:,.0f} for {category} based on industry best practices.",
                confidence=RecommendationConfidence.HIGH,
                confidence_score=0.85,
                algorithm=RecommendationAlgorithm.CONTENT_BASED,
                reasoning=f"Industry analysis shows {category} typically requires {percentage*100:.1f}% of total budget for {industry} launches",
                expected_impact="High - Proper budget allocation is critical for launch success",
                implementation_effort="Low - Budget planning and allocation",
                cost_estimate=amount,
                timeline_estimate=1,  # Immediate
                success_probability=0.8,
                metadata={"category": category, "percentage": percentage, "amount": amount},
                created_at=datetime.now()
            )
            
            recommendations.append(recommendation)
        
        return recommendations
    
    def _recommend_team_composition(self, user_profile: UserProfile, 
                                  launch_context: Dict[str, Any]) -> List[Recommendation]:
        """Recommend team composition"""
        recommendations = []
        
        team_size = launch_context.get('team_size', 10)
        product_type = launch_context.get('product_type', 'Software')
        
        # Role recommendations based on product type
        role_recommendations = {
            'Software': ['Product Manager', 'Software Engineers', 'UX/UI Designer', 'QA Engineer', 'DevOps Engineer'],
            'Mobile App': ['Product Manager', 'Mobile Developers', 'UX/UI Designer', 'QA Engineer', 'Marketing Specialist'],
            'E-commerce': ['Product Manager', 'Frontend Developers', 'Backend Developers', 'Marketing Specialist', 'Customer Support'],
            'SaaS Platform': ['Product Manager', 'Full-stack Engineers', 'DevOps Engineer', 'Sales Engineer', 'Customer Success Manager']
        }
        
        recommended_roles = role_recommendations.get(product_type, role_recommendations['Software'])
        
        for role in recommended_roles:
            recommendation = Recommendation(
                id=str(uuid.uuid4()),
                recommendation_type=RecommendationType.TEAM_COMPOSITION,
                title=f"Hire {role}",
                description=f"Add a {role} to your team for optimal launch success.",
                confidence=RecommendationConfidence.HIGH,
                confidence_score=0.9,
                algorithm=RecommendationAlgorithm.CONTENT_BASED,
                reasoning=f"{role} is essential for {product_type} launches based on industry standards",
                expected_impact="High - Right team composition is crucial for success",
                implementation_effort="High - Recruitment and onboarding",
                cost_estimate=self._estimate_role_cost(role),
                timeline_estimate=self._estimate_hiring_timeline(role),
                success_probability=0.85,
                metadata={"role": role, "product_type": product_type},
                created_at=datetime.now()
            )
            
            recommendations.append(recommendation)
        
        return recommendations
    
    def _recommend_timeline_optimization(self, user_profile: UserProfile, 
                                       launch_context: Dict[str, Any]) -> List[Recommendation]:
        """Recommend timeline optimization strategies"""
        recommendations = []
        
        current_timeline = launch_context.get('timeline_days', 120)
        team_size = launch_context.get('team_size', 10)
        
        # Timeline optimization recommendations
        if current_timeline > 150:
            recommendation = Recommendation(
                id=str(uuid.uuid4()),
                recommendation_type=RecommendationType.TIMELINE_OPTIMIZATION,
                title="Consider Phased Launch Approach",
                description="Break down the launch into smaller phases to reduce timeline and risk.",
                confidence=RecommendationConfidence.HIGH,
                confidence_score=0.8,
                algorithm=RecommendationAlgorithm.HYBRID,
                reasoning=f"Current timeline of {current_timeline} days is long. Phased approach can reduce risk and time to market.",
                expected_impact="High - Faster time to market and reduced risk",
                implementation_effort="Medium - Requires planning and coordination",
                cost_estimate=0,  # No additional cost
                timeline_estimate=7,  # Planning time
                success_probability=0.75,
                metadata={"current_timeline": current_timeline, "approach": "phased_launch"},
                created_at=datetime.now()
            )
            recommendations.append(recommendation)
        
        if team_size < 8:
            recommendation = Recommendation(
                id=str(uuid.uuid4()),
                recommendation_type=RecommendationType.TIMELINE_OPTIMIZATION,
                title="Consider Team Expansion",
                description="Increase team size to accelerate development timeline.",
                confidence=RecommendationConfidence.MEDIUM,
                confidence_score=0.7,
                algorithm=RecommendationAlgorithm.CONTENT_BASED,
                reasoning=f"Team size of {team_size} may be limiting development speed. Consider adding 2-3 more team members.",
                expected_impact="Medium - Faster development but higher costs",
                implementation_effort="High - Recruitment and onboarding",
                cost_estimate=200000,  # Additional team members
                timeline_estimate=30,  # Hiring time
                success_probability=0.7,
                metadata={"current_team_size": team_size, "recommended_increase": 3},
                created_at=datetime.now()
            )
            recommendations.append(recommendation)
        
        return recommendations
    
    def _recommend_risk_mitigation(self, user_profile: UserProfile, 
                                 launch_context: Dict[str, Any]) -> List[Recommendation]:
        """Recommend risk mitigation strategies"""
        recommendations = []
        
        industry = launch_context.get('industry', 'Technology')
        budget = launch_context.get('budget', 500000)
        
        # Industry-specific risk recommendations
        risk_recommendations = {
            'Technology': ['Technical debt management', 'Scalability planning', 'Security audit'],
            'Healthcare': ['Regulatory compliance', 'Data privacy protection', 'Clinical validation'],
            'Finance': ['Security audit', 'Compliance review', 'Penetration testing'],
            'Retail': ['Inventory management', 'Payment security', 'Customer support scaling']
        }
        
        recommended_risks = risk_recommendations.get(industry, risk_recommendations['Technology'])
        
        for risk_strategy in recommended_risks:
            recommendation = Recommendation(
                id=str(uuid.uuid4()),
                recommendation_type=RecommendationType.RISK_MITIGATION,
                title=f"Implement {risk_strategy}",
                description=f"Address {risk_strategy.lower()} to reduce launch risks.",
                confidence=RecommendationConfidence.HIGH,
                confidence_score=0.85,
                algorithm=RecommendationAlgorithm.CONTENT_BASED,
                reasoning=f"{risk_strategy} is critical for {industry} launches to ensure compliance and security",
                expected_impact="High - Risk mitigation is essential for launch success",
                implementation_effort="Medium - Requires planning and execution",
                cost_estimate=self._estimate_risk_mitigation_cost(risk_strategy, budget),
                timeline_estimate=self._estimate_risk_mitigation_timeline(risk_strategy),
                success_probability=0.9,
                metadata={"risk_strategy": risk_strategy, "industry": industry},
                created_at=datetime.now()
            )
            
            recommendations.append(recommendation)
        
        return recommendations
    
    def _recommend_market_approach(self, user_profile: UserProfile, 
                                 launch_context: Dict[str, Any]) -> List[Recommendation]:
        """Recommend market approach strategies"""
        recommendations = []
        
        product_type = launch_context.get('product_type', 'Software')
        budget = launch_context.get('budget', 500000)
        
        # Market approach recommendations
        market_approaches = {
            'Software': ['Direct sales', 'Content marketing', 'Partner channel'],
            'Mobile App': ['App store optimization', 'Social media marketing', 'Influencer partnerships'],
            'E-commerce': ['SEO optimization', 'Paid advertising', 'Social commerce'],
            'SaaS Platform': ['Inbound marketing', 'Free trial strategy', 'Customer success focus']
        }
        
        recommended_approaches = market_approaches.get(product_type, market_approaches['Software'])
        
        for approach in recommended_approaches:
            recommendation = Recommendation(
                id=str(uuid.uuid4()),
                recommendation_type=RecommendationType.MARKET_APPROACH,
                title=f"Adopt {approach} Strategy",
                description=f"Use {approach.lower()} as your primary market approach.",
                confidence=RecommendationConfidence.HIGH,
                confidence_score=0.8,
                algorithm=RecommendationAlgorithm.CONTENT_BASED,
                reasoning=f"{approach} is highly effective for {product_type} launches based on industry data",
                expected_impact="High - Market approach directly impacts customer acquisition",
                implementation_effort="Medium - Requires strategy development and execution",
                cost_estimate=self._estimate_marketing_cost(approach, budget),
                timeline_estimate=self._estimate_marketing_timeline(approach),
                success_probability=0.75,
                metadata={"approach": approach, "product_type": product_type},
                created_at=datetime.now()
            )
            
            recommendations.append(recommendation)
        
        return recommendations
    
    def _recommend_technology_stack(self, user_profile: UserProfile, 
                                  launch_context: Dict[str, Any]) -> List[Recommendation]:
        """Recommend technology stack"""
        recommendations = []
        
        product_type = launch_context.get('product_type', 'Software')
        team_skills = user_profile.skill_set
        
        # Technology recommendations
        tech_recommendations = {
            'Software': ['Python', 'React', 'PostgreSQL', 'AWS', 'Docker'],
            'Mobile App': ['React Native', 'Node.js', 'MongoDB', 'Firebase'],
            'E-commerce': ['Shopify', 'React', 'Python', 'PostgreSQL'],
            'SaaS Platform': ['Python', 'React', 'PostgreSQL', 'AWS', 'Kubernetes']
        }
        
        recommended_tech = tech_recommendations.get(product_type, tech_recommendations['Software'])
        
        for tech in recommended_tech:
            if tech.lower() not in [skill.lower() for skill in team_skills]:
                recommendation = Recommendation(
                    id=str(uuid.uuid4()),
                    recommendation_type=RecommendationType.TECHNOLOGY_STACK,
                    title=f"Consider {tech} Technology",
                    description=f"Add {tech} to your technology stack for optimal performance.",
                    confidence=RecommendationConfidence.MEDIUM,
                    confidence_score=0.7,
                    algorithm=RecommendationAlgorithm.CONTENT_BASED,
                    reasoning=f"{tech} is widely used and proven for {product_type} development",
                    expected_impact="Medium - Technology choice affects development speed and scalability",
                    implementation_effort="High - Learning curve and integration",
                    cost_estimate=self._estimate_tech_cost(tech),
                    timeline_estimate=self._estimate_tech_timeline(tech),
                    success_probability=0.7,
                    metadata={"technology": tech, "product_type": product_type},
                    created_at=datetime.now()
                )
                
                recommendations.append(recommendation)
        
        return recommendations
    
    def _recommend_partnership_opportunities(self, user_profile: UserProfile, 
                                          launch_context: Dict[str, Any]) -> List[Recommendation]:
        """Recommend partnership opportunities"""
        recommendations = []
        
        industry = launch_context.get('industry', 'Technology')
        product_type = launch_context.get('product_type', 'Software')
        
        # Partnership recommendations
        partnership_types = {
            'Technology': ['Cloud providers', 'API partners', 'Integration partners'],
            'Healthcare': ['Healthcare providers', 'Regulatory consultants', 'Data partners'],
            'Finance': ['Payment processors', 'Banking partners', 'Compliance consultants'],
            'Retail': ['Supplier partners', 'Logistics partners', 'Marketing agencies']
        }
        
        recommended_partnerships = partnership_types.get(industry, partnership_types['Technology'])
        
        for partnership in recommended_partnerships:
            recommendation = Recommendation(
                id=str(uuid.uuid4()),
                recommendation_type=RecommendationType.PARTNERSHIP_OPPORTUNITIES,
                title=f"Explore {partnership} Partnerships",
                description=f"Consider strategic partnerships with {partnership.lower()} to accelerate growth.",
                confidence=RecommendationConfidence.MEDIUM,
                confidence_score=0.6,
                algorithm=RecommendationAlgorithm.CONTENT_BASED,
                reasoning=f"Partnerships with {partnership.lower()} can provide access to resources and customers",
                expected_impact="Medium - Partnerships can accelerate growth but require management",
                implementation_effort="High - Partnership development and management",
                cost_estimate=50000,  # Partnership development costs
                timeline_estimate=60,  # Partnership development time
                success_probability=0.6,
                metadata={"partnership_type": partnership, "industry": industry},
                created_at=datetime.now()
            )
            
            recommendations.append(recommendation)
        
        return recommendations
    
    def _find_similar_launches(self, launch_context: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Find similar launches using content-based filtering"""
        if not self.launch_data:
            return []
        
        # Simple similarity based on key attributes
        similar_launches = []
        
        for launch in self.launch_data:
            similarity_score = 0
            
            # Product type similarity
            if launch.get('product_type') == launch_context.get('product_type'):
                similarity_score += 0.3
            
            # Industry similarity
            if launch.get('industry') == launch_context.get('industry'):
                similarity_score += 0.3
            
            # Budget similarity (within 50% range)
            launch_budget = launch.get('budget', 0)
            context_budget = launch_context.get('budget', 0)
            if context_budget > 0 and abs(launch_budget - context_budget) / context_budget < 0.5:
                similarity_score += 0.2
            
            # Team size similarity
            launch_team = launch.get('team_size', 0)
            context_team = launch_context.get('team_size', 0)
            if context_team > 0 and abs(launch_team - context_team) / context_team < 0.5:
                similarity_score += 0.2
            
            if similarity_score > 0.3:
                similar_launches.append(launch)
        
        return similar_launches
    
    def _get_confidence_level(self, confidence_score: float) -> RecommendationConfidence:
        """Convert confidence score to confidence level"""
        if confidence_score >= 0.8:
            return RecommendationConfidence.VERY_HIGH
        elif confidence_score >= 0.6:
            return RecommendationConfidence.HIGH
        elif confidence_score >= 0.4:
            return RecommendationConfidence.MEDIUM
        else:
            return RecommendationConfidence.LOW
    
    def _estimate_strategy_cost(self, strategy: str, launch_context: Dict[str, Any]) -> float:
        """Estimate cost for implementing a strategy"""
        base_budget = launch_context.get('budget', 500000)
        
        cost_estimates = {
            'agile_development': base_budget * 0.1,
            'beta_testing': base_budget * 0.05,
            'influencer_marketing': base_budget * 0.15,
            'user_research': base_budget * 0.08,
            'mvp_approach': base_budget * 0.05,
            'social_media_marketing': base_budget * 0.12,
            'market_research': base_budget * 0.06,
            'competitive_analysis': base_budget * 0.04,
            'seo_optimization': base_budget * 0.08
        }
        
        return cost_estimates.get(strategy, base_budget * 0.1)
    
    def _estimate_strategy_timeline(self, strategy: str) -> int:
        """Estimate timeline for implementing a strategy"""
        timeline_estimates = {
            'agile_development': 30,
            'beta_testing': 14,
            'influencer_marketing': 21,
            'user_research': 14,
            'mvp_approach': 7,
            'social_media_marketing': 14,
            'market_research': 21,
            'competitive_analysis': 7,
            'seo_optimization': 30
        }
        
        return timeline_estimates.get(strategy, 14)
    
    def _estimate_role_cost(self, role: str) -> float:
        """Estimate cost for hiring a role"""
        role_costs = {
            'Product Manager': 120000,
            'Software Engineers': 100000,
            'UX/UI Designer': 90000,
            'QA Engineer': 85000,
            'DevOps Engineer': 110000,
            'Mobile Developers': 95000,
            'Marketing Specialist': 80000,
            'Frontend Developers': 90000,
            'Backend Developers': 95000,
            'Customer Support': 60000,
            'Full-stack Engineers': 105000,
            'Sales Engineer': 100000,
            'Customer Success Manager': 85000
        }
        
        return role_costs.get(role, 90000)
    
    def _estimate_hiring_timeline(self, role: str) -> int:
        """Estimate timeline for hiring a role"""
        return 30  # Average hiring time in days
    
    def _estimate_risk_mitigation_cost(self, risk_strategy: str, budget: float) -> float:
        """Estimate cost for risk mitigation strategy"""
        return budget * 0.05  # 5% of budget for risk mitigation
    
    def _estimate_risk_mitigation_timeline(self, risk_strategy: str) -> int:
        """Estimate timeline for risk mitigation strategy"""
        return 14  # Average risk mitigation timeline
    
    def _estimate_marketing_cost(self, approach: str, budget: float) -> float:
        """Estimate cost for marketing approach"""
        return budget * 0.3  # 30% of budget for marketing
    
    def _estimate_marketing_timeline(self, approach: str) -> int:
        """Estimate timeline for marketing approach"""
        return 21  # Average marketing setup timeline
    
    def _estimate_tech_cost(self, tech: str) -> float:
        """Estimate cost for technology adoption"""
        return 25000  # Average technology adoption cost
    
    def _estimate_tech_timeline(self, tech: str) -> int:
        """Estimate timeline for technology adoption"""
        return 30  # Average technology learning timeline
    
    def get_recommendation_statistics(self) -> Dict[str, Any]:
        """Get recommendation system statistics"""
        with self.lock:
            total_recommendations = len(self.recommendations)
            
            if total_recommendations == 0:
                return {"total_recommendations": 0}
            
            # Statistics by recommendation type
            type_stats = defaultdict(int)
            algorithm_stats = defaultdict(int)
            confidence_stats = defaultdict(int)
            
            for rec in self.recommendations.values():
                type_stats[rec.recommendation_type.value] += 1
                algorithm_stats[rec.algorithm.value] += 1
                confidence_stats[rec.confidence.value] += 1
            
            # Average metrics
            avg_confidence = sum(rec.confidence_score for rec in self.recommendations.values()) / total_recommendations
            avg_cost = sum(rec.cost_estimate for rec in self.recommendations.values()) / total_recommendations
            avg_timeline = sum(rec.timeline_estimate for rec in self.recommendations.values()) / total_recommendations
            avg_success_prob = sum(rec.success_probability for rec in self.recommendations.values()) / total_recommendations
            
            return {
                "total_recommendations": total_recommendations,
                "total_users": len(self.user_profiles),
                "recommendation_types": dict(type_stats),
                "algorithms_used": dict(algorithm_stats),
                "confidence_distribution": dict(confidence_stats),
                "average_confidence_score": avg_confidence,
                "average_cost_estimate": avg_cost,
                "average_timeline_estimate": avg_timeline,
                "average_success_probability": avg_success_prob,
                "models_trained": {
                    "tfidf_vectorizer": self.tfidf_vectorizer is not None,
                    "nmf_model": self.nmf_model is not None,
                    "svd_model": self.svd_model is not None,
                    "kmeans_model": self.kmeans_model is not None
                }
            }

# Global recommendation engine instance
_recommendation_engine = None

def get_recommendation_engine() -> RecommendationEngine:
    """Get global recommendation engine instance"""
    global _recommendation_engine
    if _recommendation_engine is None:
        _recommendation_engine = RecommendationEngine()
    return _recommendation_engine

# Example usage
if __name__ == "__main__":
    # Initialize recommendation engine
    rec_engine = get_recommendation_engine()
    
    # Create user profile
    user_preferences = {
        "industry_experience": "Technology",
        "company_size": "Medium",
        "risk_tolerance": 0.6,
        "budget_range": (200000, 800000),
        "timeline_preference": "Medium",
        "skill_set": ["python", "react", "aws"]
    }
    
    user_profile = rec_engine.create_user_profile("user_001", user_preferences)
    
    # Launch context
    launch_context = {
        "product_type": "SaaS Platform",
        "industry": "Technology",
        "budget": 500000,
        "team_size": 12,
        "timeline_days": 120
    }
    
    # Get recommendations
    recommendations = rec_engine.get_recommendations(
        "user_001", 
        launch_context, 
        num_recommendations=5
    )
    
    print("Personalized Recommendations:")
    for i, rec in enumerate(recommendations, 1):
        print(f"\n{i}. {rec.title}")
        print(f"   Type: {rec.recommendation_type.value}")
        print(f"   Confidence: {rec.confidence.value} ({rec.confidence_score:.2f})")
        print(f"   Expected Impact: {rec.expected_impact}")
        print(f"   Cost Estimate: ${rec.cost_estimate:,.0f}")
        print(f"   Timeline: {rec.timeline_estimate} days")
        print(f"   Success Probability: {rec.success_probability:.2f}")
        print(f"   Reasoning: {rec.reasoning}")
    
    # Get statistics
    stats = rec_engine.get_recommendation_statistics()
    print(f"\nRecommendation Statistics:")
    print(f"Total Recommendations: {stats['total_recommendations']}")
    print(f"Average Confidence: {stats['average_confidence_score']:.2f}")
    print(f"Average Cost: ${stats['average_cost_estimate']:,.0f}")
    print(f"Average Success Probability: {stats['average_success_probability']:.2f}")







