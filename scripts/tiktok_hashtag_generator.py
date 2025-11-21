#!/usr/bin/env python3
"""
Generador Avanzado de Hashtags para TikTok
Genera hashtags actualizados y relevantes basados en industria y público objetivo
Incluye análisis de tendencias, scoring inteligente y recomendaciones personalizadas
"""

import json
import random
import os
import csv
from pathlib import Path
from typing import List, Dict, Optional, Tuple
from datetime import datetime, timedelta
from collections import Counter, defaultdict
from dataclasses import dataclass, asdict


@dataclass
class HashtagScore:
    """Score de un hashtag individual"""
    hashtag: str
    relevance_score: float  # 0-1
    trend_score: float  # 0-1
    competition_score: float  # 0-1 (menor = menos competencia)
    engagement_potential: float  # 0-1
    total_score: float  # Score combinado
    
    def __str__(self):
        return f"{self.hashtag} (Score: {self.total_score:.2f})"


class TikTokHashtagGenerator:
    """Generador inteligente avanzado de hashtags para TikTok"""
    
    # Hashtags trending 2024-2025
    TRENDING_2024_2025 = [
        "#FYP", "#ForYouPage", "#Viral", "#Trending", "#TrendingNow",
        "#POV", "#CapCut", "#AI", "#AIGenerated", "#AITok",
        "#Relatable", "#Fypシ", "#ViralVideos", "#ExplorePage",
        "#TrendAlert", "#TrendingTok", "#MustWatch", "#WatchThis"
    ]
    
    # Base de datos expandida de hashtags por industria
    INDUSTRY_HASHTAGS = {
        "tech": {
            "trending": ["#TechTok", "#TechTips", "#TechReview", "#AITok", "#TechLife"],
            "niche": ["#CodeTok", "#DevLife", "#TechHacks", "#GadgetReview", "#TechNews"],
            "community": ["#TechCommunity", "#TechCreators", "#TechLovers", "#Techies", "#TechTalk"]
        },
        "ecommerce": {
            "trending": ["#ShopTok", "#Shopping", "#Ecommerce", "#OnlineShopping", "#ShopSmall"],
            "niche": ["#ProductReview", "#Unboxing", "#ShoppingHaul", "#Deals", "#Retail"],
            "community": ["#Shopaholics", "#ShoppingAddict", "#RetailTherapy", "#ShopLocal", "#ShoppingTips"]
        },
        "marketing": {
            "trending": ["#MarketingTok", "#DigitalMarketing", "#MarketingTips", "#ContentCreator", "#SocialMedia"],
            "niche": ["#MarketingStrategy", "#BrandBuilding", "#MarketingHacks", "#GrowthHacking", "#Marketing101"],
            "community": ["#MarketingCommunity", "#Marketers", "#MarketingLife", "#MarketingPro", "#MarketingTips"]
        },
        "fitness": {
            "trending": ["#FitnessTok", "#Workout", "#Fitness", "#GymTok", "#FitTok"],
            "niche": ["#HomeWorkout", "#FitnessMotivation", "#GymMotivation", "#FitnessTips", "#WorkoutRoutine"],
            "community": ["#FitnessCommunity", "#FitFam", "#GymLife", "#FitnessJourney", "#FitLife"]
        },
        "food": {
            "trending": ["#FoodTok", "#Foodie", "#Cooking", "#Recipe", "#Food"],
            "niche": ["#EasyRecipe", "#CookingTips", "#FoodHacks", "#QuickMeals", "#FoodReview"],
            "community": ["#FoodLovers", "#FoodCommunity", "#CookingAtHome", "#FoodShare", "#FoodieLife"]
        },
        "education": {
            "trending": ["#EduTok", "#LearnOnTikTok", "#Education", "#StudyTok", "#Learning"],
            "niche": ["#StudyTips", "#LearnWithMe", "#EducationTips", "#StudyHacks", "#Knowledge"],
            "community": ["#StudyCommunity", "#Students", "#Learners", "#EducationMatters", "#StudyLife"]
        },
        "beauty": {
            "trending": ["#BeautyTok", "#Makeup", "#Beauty", "#Skincare", "#BeautyTips"],
            "niche": ["#MakeupTutorial", "#SkincareRoutine", "#BeautyHacks", "#MakeupLook", "#BeautyReview"],
            "community": ["#BeautyCommunity", "#MakeupLovers", "#BeautyLovers", "#MakeupAddict", "#BeautyLife"]
        },
        "finance": {
            "trending": ["#FinanceTok", "#MoneyTok", "#Finance", "#Investing", "#MoneyTips"],
            "niche": ["#InvestingTips", "#FinancialLiteracy", "#MoneyHacks", "#BudgetTips", "#WealthBuilding"],
            "community": ["#FinanceCommunity", "#Investors", "#MoneyMindset", "#FinancialFreedom", "#MoneyTalk"]
        },
        "automation": {
            "trending": ["#AutomationTok", "#TechAutomation", "#Workflow", "#Productivity", "#TechTips"],
            "niche": ["#WorkflowAutomation", "#ProductivityHacks", "#TechHacks", "#AutomationTips", "#Efficiency"],
            "community": ["#AutomationCommunity", "#ProductivityPro", "#TechCreators", "#WorkflowTips", "#TechLife"]
        },
        "ai": {
            "trending": ["#AITok", "#AI", "#ArtificialIntelligence", "#MachineLearning", "#ChatGPT"],
            "niche": ["#AIGenerated", "#AITools", "#AITips", "#MLTok", "#DeepLearning"],
            "community": ["#AICommunity", "#AILovers", "#TechAI", "#AICreators", "#AIFuture"]
        },
        "gaming": {
            "trending": ["#GamingTok", "#Gaming", "#Gamer", "#GameTok", "#GamingCommunity"],
            "niche": ["#GameReview", "#GamingSetup", "#GamingTips", "#GamingLife", "#Gameplay"],
            "community": ["#GamingCommunity", "#Gamers", "#GamingLife", "#GamingFam", "#GamingContent"]
        },
        "travel": {
            "trending": ["#TravelTok", "#Travel", "#Wanderlust", "#TravelTips", "#TravelGuide"],
            "niche": ["#TravelHacks", "#BudgetTravel", "#TravelVlog", "#SoloTravel", "#TravelDiaries"],
            "community": ["#TravelCommunity", "#Travelers", "#TravelLife", "#TravelAddict", "#TravelShare"]
        },
        "business": {
            "trending": ["#BusinessTok", "#Business", "#Entrepreneur", "#Startup", "#BusinessTips"],
            "niche": ["#BusinessStrategy", "#BusinessGrowth", "#BusinessHacks", "#StartupLife", "#BusinessMindset"],
            "community": ["#BusinessCommunity", "#Entrepreneurs", "#BusinessOwners", "#StartupFounders", "#BusinessLife"]
        }
    }
    
    # Hashtags por edad/interés (expandido)
    DEMOGRAPHIC_HASHTAGS = {
        "gen_z": ["#GenZ", "#Zoomer", "#GenZLife", "#GenZProblems", "#GenZHumor", "#GenZContent", "#GenZTok"],
        "millennial": ["#Millennial", "#MillennialLife", "#Adulting", "#MillennialProblems", "#MillennialHumor", "#MillennialTok"],
        "tech_savvy": ["#TechSavvy", "#EarlyAdopter", "#TechEarly", "#Innovation", "#TechTrends", "#TechTok"],
        "entrepreneurs": ["#Entrepreneur", "#StartupLife", "#BusinessOwner", "#Entrepreneurship", "#Startup", "#BusinessTok"],
        "creators": ["#ContentCreator", "#Creator", "#CreatorLife", "#ContentCreation", "#CreatorEconomy", "#CreatorTok"],
        "professionals": ["#Professional", "#CareerTips", "#WorkLife", "#ProfessionalDevelopment", "#CareerGrowth", "#WorkTok"],
        "students": ["#StudentLife", "#StudyTok", "#Student", "#CollegeLife", "#StudyTips", "#StudentTok"],
        "parents": ["#ParentTok", "#Parenting", "#MomTok", "#DadTok", "#ParentingTips", "#FamilyLife"]
    }
    
    # Combinaciones únicas expandidas (no genéricas)
    UNIQUE_COMBINATIONS = [
        ["#BehindTheScenes", "#Process", "#HowItsMade"],
        ["#DayInTheLife", "#Routine", "#DailyLife"],
        ["#BeforeAndAfter", "#Transformation", "#Results"],
        ["#ProTip", "#Hack", "#LifeHack"],
        ["#TrendingNow", "#Viral", "#Trending"],
        ["#QuickTips", "#ShortTips", "#QuickHacks"],
        ["#RealTalk", "#HonestReview", "#NoFilter"],
        ["#Tutorial", "#HowTo", "#StepByStep"],
        ["#Comparison", "#Vs", "#WhichIsBetter"],
        ["#MythBusting", "#Debunked", "#Truth"],
        ["#TryThis", "#YouNeedThis", "#MustTry"],
        ["#Satisfying", "#OddlySatisfying", "#SatisfyingVideo"],
        ["#POV", "#POVTok", "#PointOfView"],
        ["#CapCut", "#CapCutEdit", "#CapCutTutorial"],
        ["#StoryTime", "#Story", "#TellMeAStory"],
        ["#Challenge", "#ChallengeAccepted", "#TrendingChallenge"],
        ["#Duet", "#DuetThis", "#DuetMe"],
        ["#Stitch", "#StitchThis", "#StitchMe"],
        ["#Transitions", "#TransitionTok", "#SmoothTransition"],
        ["#Editing", "#EditTok", "#EditingTips"]
    ]
    
    # Scores estimados de competencia (basado en uso promedio)
    COMPETITION_LEVELS = {
        "high": ["#FYP", "#ForYouPage", "#Viral", "#Trending", "#POV"],
        "medium": ["#TechTok", "#FoodTok", "#FitnessTok", "#BeautyTok"],
        "low": ["#WorkflowAutomation", "#ProductivityHacks", "#TechHacks", "#AutomationTips"]
    }
    
    def __init__(
        self, 
        industry: str, 
        demographic: str, 
        custom_keywords: List[str] = None,
        content_type: Optional[str] = None,
        video_length: Optional[str] = None
    ):
        """
        Inicializa el generador de hashtags
        
        Args:
            industry: Industria objetivo (tech, ecommerce, marketing, etc.)
            demographic: Demografía objetivo (gen_z, millennial, tech_savvy, etc.)
            custom_keywords: Palabras clave personalizadas adicionales
            content_type: Tipo de contenido (tutorial, review, behind_scenes, etc.)
            video_length: Duración del video (short, medium, long)
        """
        self.industry = industry.lower()
        self.demographic = demographic.lower()
        self.custom_keywords = custom_keywords or []
        self.content_type = content_type.lower() if content_type else None
        self.video_length = video_length.lower() if video_length else None
        self.hashtag_history = []  # Para tracking de uso
        self.history_file = Path.home() / ".tiktok_hashtag_history.json"
        self._load_history()
        
    def _calculate_hashtag_score(self, hashtag: str) -> HashtagScore:
        """
        Calcula el score de un hashtag individual
        
        Args:
            hashtag: Hashtag a evaluar
            
        Returns:
            HashtagScore con todos los scores calculados
        """
        # Relevance score (0-1)
        relevance = 0.5  # Base
        
        # Verificar si está en industria
        if self.industry in self.INDUSTRY_HASHTAGS:
            industry_tags = (
                self.INDUSTRY_HASHTAGS[self.industry]["trending"] +
                self.INDUSTRY_HASHTAGS[self.industry]["niche"] +
                self.INDUSTRY_HASHTAGS[self.industry]["community"]
            )
            if hashtag in industry_tags:
                relevance += 0.3
        
        # Verificar si está en demografía
        if self.demographic in self.DEMOGRAPHIC_HASHTAGS:
            if hashtag in self.DEMOGRAPHIC_HASHTAGS[self.demographic]:
                relevance += 0.2
        
        relevance = min(1.0, relevance)
        
        # Trend score (0-1) - basado en trending 2024-2025
        trend_score = 0.3  # Base
        if hashtag in self.TRENDING_2024_2025:
            trend_score = 0.9
        elif any(trend in hashtag for trend in ["Tok", "Trending", "Viral"]):
            trend_score = 0.7
        
        # Competition score (0-1) - menor = menos competencia
        competition = 0.5  # Base
        if hashtag in self.COMPETITION_LEVELS["high"]:
            competition = 0.9  # Alta competencia
        elif hashtag in self.COMPETITION_LEVELS["medium"]:
            competition = 0.6
        elif hashtag in self.COMPETITION_LEVELS["low"]:
            competition = 0.3  # Baja competencia
        
        # Engagement potential (0-1)
        engagement = 0.5  # Base
        if hashtag in self.TRENDING_2024_2025[:5]:  # Top trending
            engagement = 0.9
        elif any(word in hashtag.lower() for word in ["tip", "hack", "tutorial", "review"]):
            engagement = 0.7
        
        # Total score (weighted average)
        total_score = (
            relevance * 0.3 +
            trend_score * 0.25 +
            (1 - competition) * 0.25 +  # Invertir competencia
            engagement * 0.2
        )
        
        return HashtagScore(
            hashtag=hashtag,
            relevance_score=relevance,
            trend_score=trend_score,
            competition_score=competition,
            engagement_potential=engagement,
            total_score=total_score
        )
    
    def generate_hashtags(
        self, 
        count: int = 10, 
        include_unique: bool = True,
        use_scoring: bool = True,
        min_score: float = 0.4
    ) -> List[str]:
        """
        Genera una lista de hashtags personalizados con scoring inteligente
        
        Args:
            count: Número de hashtags a generar (default: 10)
            include_unique: Incluir combinaciones únicas (default: True)
            use_scoring: Usar sistema de scoring para optimizar selección (default: True)
            min_score: Score mínimo para incluir hashtag (default: 0.4)
            
        Returns:
            Lista de hashtags ordenados por score
        """
        candidate_hashtags = []
        
        # 1. Hashtags de industria (trending + niche + community)
        if self.industry in self.INDUSTRY_HASHTAGS:
            industry_data = self.INDUSTRY_HASHTAGS[self.industry]
            candidate_hashtags.extend(industry_data["trending"][:3])
            candidate_hashtags.extend(industry_data["niche"][:3])
            candidate_hashtags.extend(industry_data["community"][:2])
        
        # 2. Hashtags demográficos
        if self.demographic in self.DEMOGRAPHIC_HASHTAGS:
            candidate_hashtags.extend(self.DEMOGRAPHIC_HASHTAGS[self.demographic][:3])
        
        # 3. Combinaciones únicas (al menos 3)
        if include_unique:
            unique_count = min(3, len(self.UNIQUE_COMBINATIONS))
            for combo in self.UNIQUE_COMBINATIONS[:unique_count]:
                candidate_hashtags.extend(combo[:2])  # Tomar primeros 2 de cada combinación
        
        # 4. Keywords personalizadas
        if self.custom_keywords:
            candidate_hashtags.extend([
                f"#{kw.replace(' ', '').replace('#', '')}" 
                for kw in self.custom_keywords[:3]
            ])
        
        # 5. Hashtags trending universales
        candidate_hashtags.extend(self.TRENDING_2024_2025[:3])
        
        # Eliminar duplicados manteniendo orden
        seen = set()
        unique_candidates = []
        for tag in candidate_hashtags:
            tag_clean = tag.replace('#', '').lower()
            if tag_clean not in seen:
                seen.add(tag_clean)
                unique_candidates.append(tag)
        
        # Aplicar scoring si está habilitado
        if use_scoring:
            scored_hashtags = [
                self._calculate_hashtag_score(tag) 
                for tag in unique_candidates
            ]
            # Filtrar por score mínimo y ordenar
            scored_hashtags = [
                s for s in scored_hashtags 
                if s.total_score >= min_score
            ]
            scored_hashtags.sort(key=lambda x: x.total_score, reverse=True)
            
            # Seleccionar los mejores
            selected = [s.hashtag for s in scored_hashtags[:count]]
            
            # Asegurar que tenemos suficientes
            if len(selected) < count:
                remaining = [tag for tag in unique_candidates if tag not in selected]
                selected.extend(remaining[:count - len(selected)])
            
            return selected[:count]
        else:
            # Sin scoring, selección aleatoria balanceada
            return unique_candidates[:count]
    
    def generate_unique_combinations(self, count: int = 3) -> List[List[str]]:
        """
        Genera combinaciones únicas de hashtags
        
        Args:
            count: Número de combinaciones a generar
            
        Returns:
            Lista de combinaciones (cada una es una lista de hashtags)
        """
        return self.UNIQUE_COMBINATIONS[:count]
    
    def get_full_recommendation(self, include_scores: bool = False) -> Dict:
        """
        Genera una recomendación completa con hashtags y combinaciones únicas
        
        Args:
            include_scores: Incluir scores detallados de cada hashtag
            
        Returns:
            Diccionario con hashtags principales y combinaciones únicas
        """
        main_hashtags = self.generate_hashtags(count=10, include_unique=False, use_scoring=True)
        unique_combos = self.generate_unique_combinations(count=3)
        
        result = {
            "industry": self.industry,
            "demographic": self.demographic,
            "main_hashtags": main_hashtags,
            "unique_combinations": unique_combos,
            "all_hashtags": main_hashtags + [h for combo in unique_combos for h in combo],
            "formatted_string": " ".join(main_hashtags),
            "hashtag_count": len(main_hashtags),
            "unique_combinations_count": len(unique_combos),
            "generated_at": datetime.now().isoformat()
        }
        
        if include_scores:
            result["hashtag_scores"] = [
                {
                    "hashtag": score.hashtag,
                    "relevance": round(score.relevance_score, 2),
                    "trend": round(score.trend_score, 2),
                    "competition": round(score.competition_score, 2),
                    "engagement": round(score.engagement_potential, 2),
                    "total_score": round(score.total_score, 2)
                }
                for score in [
                    self._calculate_hashtag_score(tag) 
                    for tag in main_hashtags
                ]
            ]
        
        return result
    
    def analyze_hashtag_performance(self, hashtags: List[str]) -> Dict:
        """
        Analiza el rendimiento potencial de una lista de hashtags
        
        Args:
            hashtags: Lista de hashtags a analizar
            
        Returns:
            Diccionario con análisis de rendimiento
        """
        scores = [self._calculate_hashtag_score(tag) for tag in hashtags]
        
        avg_relevance = sum(s.relevance_score for s in scores) / len(scores) if scores else 0
        avg_trend = sum(s.trend_score for s in scores) / len(scores) if scores else 0
        avg_competition = sum(s.competition_score for s in scores) / len(scores) if scores else 0
        avg_engagement = sum(s.engagement_potential for s in scores) / len(scores) if scores else 0
        avg_total = sum(s.total_score for s in scores) / len(scores) if scores else 0
        
        # Categorizar hashtags
        high_performing = [s.hashtag for s in scores if s.total_score >= 0.7]
        medium_performing = [s.hashtag for s in scores if 0.5 <= s.total_score < 0.7]
        low_performing = [s.hashtag for s in scores if s.total_score < 0.5]
        
        return {
            "total_hashtags": len(hashtags),
            "average_scores": {
                "relevance": round(avg_relevance, 2),
                "trend": round(avg_trend, 2),
                "competition": round(avg_competition, 2),
                "engagement": round(avg_engagement, 2),
                "total": round(avg_total, 2)
            },
            "performance_breakdown": {
                "high_performing": high_performing,
                "medium_performing": medium_performing,
                "low_performing": low_performing
            },
            "recommendations": self._generate_recommendations(scores)
        }
    
    def _generate_recommendations(self, scores: List[HashtagScore]) -> List[str]:
        """Genera recomendaciones basadas en los scores"""
        recommendations = []
        
        avg_score = sum(s.total_score for s in scores) / len(scores) if scores else 0
        
        if avg_score < 0.5:
            recommendations.append("Considera agregar más hashtags trending para aumentar visibilidad")
        
        high_competition = [s for s in scores if s.competition_score > 0.7]
        if len(high_competition) > 3:
            recommendations.append("Tienes muchos hashtags de alta competencia, considera agregar más nicho")
        
        low_trend = [s for s in scores if s.trend_score < 0.4]
        if len(low_trend) > 5:
            recommendations.append("Agrega más hashtags trending para aprovechar tendencias actuales")
        
        return recommendations
    
    def _load_history(self):
        """Carga el historial de hashtags desde archivo"""
        if self.history_file.exists():
            try:
                with open(self.history_file, 'r', encoding='utf-8') as f:
                    self.hashtag_history = json.load(f)
            except:
                self.hashtag_history = []
        else:
            self.hashtag_history = []
    
    def _save_history(self):
        """Guarda el historial de hashtags a archivo"""
        try:
            with open(self.history_file, 'w', encoding='utf-8') as f:
                json.dump(self.hashtag_history, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"Warning: Could not save history: {e}")
    
    def save_to_history(self, hashtags: List[str], metadata: Optional[Dict] = None):
        """Guarda un set de hashtags al historial"""
        entry = {
            "hashtags": hashtags,
            "industry": self.industry,
            "demographic": self.demographic,
            "timestamp": datetime.now().isoformat(),
            "metadata": metadata or {}
        }
        self.hashtag_history.append(entry)
        # Mantener solo últimos 1000 registros
        if len(self.hashtag_history) > 1000:
            self.hashtag_history = self.hashtag_history[-1000:]
        self._save_history()
    
    def get_most_used_hashtags(self, limit: int = 20) -> List[Tuple[str, int]]:
        """Obtiene los hashtags más usados del historial"""
        counter = Counter()
        for entry in self.hashtag_history:
            for tag in entry.get("hashtags", []):
                counter[tag] += 1
        return counter.most_common(limit)
    
    def compare_hashtag_sets(self, set1: List[str], set2: List[str]) -> Dict:
        """Compara dos sets de hashtags"""
        set1_clean = {tag.replace('#', '').lower() for tag in set1}
        set2_clean = {tag.replace('#', '').lower() for tag in set2}
        
        common = set1_clean & set2_clean
        only_set1 = set1_clean - set2_clean
        only_set2 = set2_clean - set1_clean
        
        # Calcular scores promedio
        scores1 = [self._calculate_hashtag_score(f"#{tag}") for tag in set1_clean]
        scores2 = [self._calculate_hashtag_score(f"#{tag}") for tag in set2_clean]
        
        avg_score1 = sum(s.total_score for s in scores1) / len(scores1) if scores1 else 0
        avg_score2 = sum(s.total_score for s in scores2) / len(scores2) if scores2 else 0
        
        return {
            "set1_count": len(set1),
            "set2_count": len(set2),
            "common_count": len(common),
            "common_hashtags": [f"#{tag}" for tag in common],
            "only_in_set1": [f"#{tag}" for tag in only_set1],
            "only_in_set2": [f"#{tag}" for tag in only_set2],
            "similarity": len(common) / max(len(set1_clean), len(set2_clean)) if max(len(set1_clean), len(set2_clean)) > 0 else 0,
            "avg_score_set1": round(avg_score1, 2),
            "avg_score_set2": round(avg_score2, 2),
            "better_set": "set1" if avg_score1 > avg_score2 else "set2" if avg_score2 > avg_score1 else "equal"
        }
    
    def generate_variations(self, hashtags: List[str], count: int = 3) -> List[List[str]]:
        """Genera variaciones de un set de hashtags"""
        variations = []
        
        for _ in range(count):
            variation = hashtags.copy()
            
            # Reemplazar algunos hashtags trending con alternativas
            trending_replacements = {
                "#FYP": ["#ForYouPage", "#Fypシ", "#ExplorePage"],
                "#Viral": ["#Trending", "#TrendingNow", "#MustWatch"],
                "#POV": ["#POVTok", "#PointOfView", "#StoryTime"]
            }
            
            for i, tag in enumerate(variation):
                if tag in trending_replacements:
                    if random.random() < 0.3:  # 30% chance de reemplazar
                        variation[i] = random.choice(trending_replacements[tag])
            
            # Agregar hashtags adicionales de combinaciones únicas
            if random.random() < 0.5:
                combo = random.choice(self.UNIQUE_COMBINATIONS)
                variation.extend(combo[:2])
            
            # Eliminar duplicados y limitar
            seen = set()
            unique_variation = []
            for tag in variation:
                tag_clean = tag.replace('#', '').lower()
                if tag_clean not in seen:
                    seen.add(tag_clean)
                    unique_variation.append(tag)
            
            variations.append(unique_variation[:15])  # Max 15 hashtags
        
        return variations
    
    def export_to_file(self, hashtags: List[str], filename: str, format: str = "txt"):
        """Exporta hashtags a archivo en diferentes formatos"""
        path = Path(filename)
        
        if format.lower() == "txt":
            with open(path, 'w', encoding='utf-8') as f:
                f.write(" ".join(hashtags))
        
        elif format.lower() == "json":
            data = {
                "hashtags": hashtags,
                "industry": self.industry,
                "demographic": self.demographic,
                "generated_at": datetime.now().isoformat(),
                "count": len(hashtags)
            }
            with open(path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
        
        elif format.lower() == "csv":
            with open(path, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow(["Hashtag", "Score", "Relevance", "Trend", "Competition", "Engagement"])
                for tag in hashtags:
                    score = self._calculate_hashtag_score(tag)
                    writer.writerow([
                        tag,
                        round(score.total_score, 2),
                        round(score.relevance_score, 2),
                        round(score.trend_score, 2),
                        round(score.competition_score, 2),
                        round(score.engagement_potential, 2)
                    ])
        
        return str(path)
    
    def get_templates(self) -> Dict[str, Dict]:
        """Obtiene templates predefinidos por tipo de contenido"""
        templates = {
            "tutorial": {
                "name": "Tutorial",
                "suggested_combinations": [
                    ["#Tutorial", "#HowTo", "#StepByStep"],
                    ["#LearnWithMe", "#Tips", "#ProTip"]
                ],
                "recommended_count": 8
            },
            "review": {
                "name": "Review",
                "suggested_combinations": [
                    ["#Review", "#HonestReview", "#RealTalk"],
                    ["#ProductReview", "#Unboxing", "#FirstImpressions"]
                ],
                "recommended_count": 10
            },
            "behind_scenes": {
                "name": "Behind the Scenes",
                "suggested_combinations": [
                    ["#BehindTheScenes", "#Process", "#HowItsMade"],
                    ["#DayInTheLife", "#Routine", "#DailyLife"]
                ],
                "recommended_count": 8
            },
            "comparison": {
                "name": "Comparison",
                "suggested_combinations": [
                    ["#Comparison", "#Vs", "#WhichIsBetter"],
                    ["#Review", "#Comparison", "#Test"]
                ],
                "recommended_count": 10
            },
            "challenge": {
                "name": "Challenge",
                "suggested_combinations": [
                    ["#Challenge", "#ChallengeAccepted", "#TrendingChallenge"],
                    ["#TryThis", "#YouNeedThis", "#MustTry"]
                ],
                "recommended_count": 12
            },
            "transformation": {
                "name": "Transformation",
                "suggested_combinations": [
                    ["#BeforeAndAfter", "#Transformation", "#Results"],
                    ["#GlowUp", "#Transformation", "#Progress"]
                ],
                "recommended_count": 10
            }
        }
        return templates
    
    def apply_template(self, template_name: str) -> List[str]:
        """Aplica un template predefinido"""
        templates = self.get_templates()
        if template_name.lower() not in templates:
            return []
        
        template = templates[template_name.lower()]
        hashtags = []
        
        # Agregar combinaciones del template
        for combo in template["suggested_combinations"]:
            hashtags.extend(combo)
        
        # Agregar hashtags de industria y demografía
        base_hashtags = self.generate_hashtags(
            count=template["recommended_count"] - len(hashtags),
            include_unique=False
        )
        hashtags.extend(base_hashtags)
        
        # Eliminar duplicados
        seen = set()
        unique_hashtags = []
        for tag in hashtags:
            tag_clean = tag.replace('#', '').lower()
            if tag_clean not in seen:
                seen.add(tag_clean)
                unique_hashtags.append(tag)
        
        return unique_hashtags[:template["recommended_count"]]
    
    def batch_generate(self, configs: List[Dict]) -> List[Dict]:
        """Genera hashtags para múltiples configuraciones"""
        results = []
        
        for config in configs:
            industry = config.get("industry", self.industry)
            demographic = config.get("demographic", self.demographic)
            keywords = config.get("keywords", [])
            count = config.get("count", 10)
            
            generator = TikTokHashtagGenerator(
                industry=industry,
                demographic=demographic,
                custom_keywords=keywords,
                content_type=config.get("content_type"),
                video_length=config.get("video_length")
            )
            
            hashtags = generator.generate_hashtags(count=count)
            recommendation = generator.get_full_recommendation()
            
            results.append({
                "config": config,
                "hashtags": hashtags,
                "recommendation": recommendation
            })
        
        return results
    
    def get_statistics(self) -> Dict:
        """Obtiene estadísticas del historial"""
        if not self.hashtag_history:
            return {"message": "No history available"}
        
        total_entries = len(self.hashtag_history)
        all_hashtags = []
        industry_counter = Counter()
        demographic_counter = Counter()
        
        for entry in self.hashtag_history:
            all_hashtags.extend(entry.get("hashtags", []))
            industry_counter[entry.get("industry", "unknown")] += 1
            demographic_counter[entry.get("demographic", "unknown")] += 1
        
        hashtag_counter = Counter(all_hashtags)
        
        # Calcular fechas
        dates = [datetime.fromisoformat(e.get("timestamp", "")) for e in self.hashtag_history if e.get("timestamp")]
        if dates:
            first_date = min(dates)
            last_date = max(dates)
        else:
            first_date = last_date = None
        
        return {
            "total_entries": total_entries,
            "total_unique_hashtags": len(hashtag_counter),
            "most_used_hashtags": hashtag_counter.most_common(10),
            "most_used_industries": industry_counter.most_common(5),
            "most_used_demographics": demographic_counter.most_common(5),
            "first_entry": first_date.isoformat() if first_date else None,
            "last_entry": last_date.isoformat() if last_date else None,
            "date_range_days": (last_date - first_date).days if first_date and last_date else 0
        }


def main():
    """Función principal para uso desde CLI"""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Genera hashtags personalizados para TikTok"
    )
    parser.add_argument(
        "--industry",
        type=str,
        required=False,
        help="Industria: tech, ecommerce, marketing, fitness, food, education, beauty, finance, automation"
    )
    parser.add_argument(
        "--demographic",
        type=str,
        required=False,
        help="Demografía: gen_z, millennial, tech_savvy, entrepreneurs, creators, professionals"
    )
    parser.add_argument(
        "--keywords",
        type=str,
        nargs="+",
        help="Palabras clave personalizadas adicionales"
    )
    parser.add_argument(
        "--count",
        type=int,
        default=10,
        help="Número de hashtags a generar (default: 10)"
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Salida en formato JSON"
    )
    parser.add_argument(
        "--scores",
        action="store_true",
        help="Incluir scores detallados de cada hashtag"
    )
    parser.add_argument(
        "--analyze",
        action="store_true",
        help="Analizar rendimiento potencial de los hashtags generados"
    )
    parser.add_argument(
        "--content-type",
        type=str,
        help="Tipo de contenido: tutorial, review, behind_scenes, comparison, etc."
    )
    parser.add_argument(
        "--video-length",
        type=str,
        choices=["short", "medium", "long"],
        help="Duración del video"
    )
    parser.add_argument(
        "--export",
        type=str,
        help="Exportar a archivo (especificar ruta del archivo)"
    )
    parser.add_argument(
        "--export-format",
        type=str,
        choices=["txt", "json", "csv"],
        default="txt",
        help="Formato de exportación (default: txt)"
    )
    parser.add_argument(
        "--template",
        type=str,
        help="Aplicar template predefinido: tutorial, review, behind_scenes, comparison, challenge, transformation"
    )
    parser.add_argument(
        "--variations",
        type=int,
        help="Generar N variaciones del set de hashtags"
    )
    parser.add_argument(
        "--save-history",
        action="store_true",
        help="Guardar hashtags generados al historial"
    )
    parser.add_argument(
        "--stats",
        action="store_true",
        help="Mostrar estadísticas del historial"
    )
    parser.add_argument(
        "--most-used",
        type=int,
        help="Mostrar N hashtags más usados del historial"
    )
    parser.add_argument(
        "--compare",
        type=str,
        nargs="+",
        help="Comparar con otro set de hashtags (proporcionar como lista)"
    )
    parser.add_argument(
        "--batch",
        type=str,
        help="Procesar múltiples configuraciones desde archivo JSON"
    )
    parser.add_argument(
        "--list-templates",
        action="store_true",
        help="Listar todos los templates disponibles"
    )
    
    args = parser.parse_args()
    
    # Listar templates
    if args.list_templates:
        generator_temp = TikTokHashtagGenerator("tech", "gen_z")
        templates = generator_temp.get_templates()
        print("\n📋 TEMPLATES DISPONIBLES:")
        print("="*70)
        for key, template in templates.items():
            print(f"\n{key.upper()}:")
            print(f"  Nombre: {template['name']}")
            print(f"  Hashtags recomendados: {template['recommended_count']}")
            print(f"  Combinaciones sugeridas:")
            for combo in template['suggested_combinations']:
                print(f"    - {' '.join(combo)}")
        print("\n" + "="*70)
        return
    
    # Validar argumentos requeridos
    if not args.industry or not args.demographic:
        parser.error("--industry y --demographic son requeridos (excepto con --list-templates)")
    
    generator = TikTokHashtagGenerator(
        industry=args.industry,
        demographic=args.demographic,
        custom_keywords=args.keywords,
        content_type=args.content_type,
        video_length=args.video_length
    )
    
    # Aplicar template si se especifica
    if args.template:
        hashtags = generator.apply_template(args.template)
        recommendation = {
            "industry": generator.industry,
            "demographic": generator.demographic,
            "main_hashtags": hashtags,
            "unique_combinations": [],
            "formatted_string": " ".join(hashtags),
            "hashtag_count": len(hashtags),
            "template_used": args.template,
            "generated_at": datetime.now().isoformat()
        }
    else:
        recommendation = generator.get_full_recommendation(include_scores=args.scores)
    
    # Generar variaciones si se solicita
    if args.variations:
        variations = generator.generate_variations(recommendation['main_hashtags'], count=args.variations)
        recommendation['variations'] = variations
    
    # Comparar con otro set si se proporciona
    if args.compare:
        comparison = generator.compare_hashtag_sets(recommendation['main_hashtags'], args.compare)
        recommendation['comparison'] = comparison
    
    # Guardar al historial si se solicita
    if args.save_history:
        generator.save_to_history(
            recommendation['main_hashtags'],
            metadata={
                "content_type": args.content_type,
                "video_length": args.video_length,
                "template": args.template
            }
        )
    
    # Mostrar estadísticas
    if args.stats:
        stats = generator.get_statistics()
        recommendation['statistics'] = stats
    
    # Mostrar más usados
    if args.most_used:
        most_used = generator.get_most_used_hashtags(limit=args.most_used)
        recommendation['most_used_hashtags'] = [
            {"hashtag": tag, "count": count} 
            for tag, count in most_used
        ]
    
    # Análisis de rendimiento si se solicita
    if args.analyze:
        analysis = generator.analyze_hashtag_performance(recommendation['main_hashtags'])
        recommendation['performance_analysis'] = analysis
    
    # Exportar a archivo si se solicita
    if args.export:
        exported_path = generator.export_to_file(
            recommendation['main_hashtags'],
            args.export,
            format=args.export_format
        )
        recommendation['exported_to'] = exported_path
    
    if args.json:
        print(json.dumps(recommendation, indent=2, ensure_ascii=False))
    else:
        print("\n" + "="*70)
        print("🎯 GENERADOR AVANZADO DE HASHTAGS PARA TIKTOK")
        print("="*70)
        print(f"\n📊 Industria: {args.industry.upper()}")
        print(f"👥 Público: {args.demographic.upper()}")
        if args.content_type:
            print(f"🎬 Tipo de Contenido: {args.content_type.upper()}")
        if args.video_length:
            print(f"⏱️  Duración: {args.video_length.upper()}")
        
        print(f"\n✨ Hashtags Principales ({len(recommendation['main_hashtags'])}):")
        print("   " + " ".join(recommendation['main_hashtags']))
        
        if args.scores and 'hashtag_scores' in recommendation:
            print(f"\n📈 Scores Detallados:")
            for score_data in recommendation['hashtag_scores'][:5]:  # Mostrar top 5
                print(f"   {score_data['hashtag']}: {score_data['total_score']:.2f} "
                      f"(Relevancia: {score_data['relevance']:.2f}, "
                      f"Trend: {score_data['trend']:.2f}, "
                      f"Engagement: {score_data['engagement']:.2f})")
        
        print(f"\n🔗 Combinaciones Únicas ({len(recommendation['unique_combinations'])}):")
        for i, combo in enumerate(recommendation['unique_combinations'], 1):
            print(f"   {i}. {' '.join(combo)}")
        
        if args.analyze and 'performance_analysis' in recommendation:
            analysis = recommendation['performance_analysis']
            print(f"\n📊 Análisis de Rendimiento:")
            print(f"   Score Promedio: {analysis['average_scores']['total']:.2f}")
            print(f"   Alto Rendimiento: {len(analysis['performance_breakdown']['high_performing'])} hashtags")
            print(f"   Medio Rendimiento: {len(analysis['performance_breakdown']['medium_performing'])} hashtags")
            if analysis['recommendations']:
                print(f"\n💡 Recomendaciones:")
                for rec in analysis['recommendations']:
                    print(f"   • {rec}")
        
        if args.template:
            print(f"\n📋 Template Aplicado: {args.template.upper()}")
        
        if args.variations and 'variations' in recommendation:
            print(f"\n🔄 Variaciones Generadas ({len(recommendation['variations'])}):")
            for i, variation in enumerate(recommendation['variations'], 1):
                print(f"   Variación {i}: {' '.join(variation[:10])}...")
        
        if args.compare and 'comparison' in recommendation:
            comp = recommendation['comparison']
            print(f"\n⚖️  Comparación:")
            print(f"   Similitud: {comp['similarity']:.2%}")
            print(f"   Hashtags comunes: {comp['common_count']}")
            print(f"   Score promedio Set 1: {comp['avg_score_set1']:.2f}")
            print(f"   Score promedio Set 2: {comp['avg_score_set2']:.2f}")
            print(f"   Mejor set: {comp['better_set']}")
        
        if args.stats and 'statistics' in recommendation:
            stats = recommendation['statistics']
            if 'message' not in stats:
                print(f"\n📊 Estadísticas del Historial:")
                print(f"   Total de entradas: {stats['total_entries']}")
                print(f"   Hashtags únicos: {stats['total_unique_hashtags']}")
                print(f"   Rango de fechas: {stats['date_range_days']} días")
                if stats['most_used_hashtags']:
                    print(f"\n   Top Hashtags Más Usados:")
                    for tag, count in stats['most_used_hashtags'][:5]:
                        print(f"     {tag}: {count} veces")
        
        if args.most_used and 'most_used_hashtags' in recommendation:
            print(f"\n🏆 Hashtags Más Usados:")
            for item in recommendation['most_used_hashtags']:
                print(f"   {item['hashtag']}: {item['count']} veces")
        
        if args.export and 'exported_to' in recommendation:
            print(f"\n💾 Exportado a: {recommendation['exported_to']}")
        
        print(f"\n📝 Cadena Completa de Hashtags:")
        print("   " + recommendation['formatted_string'])
        print("\n" + "="*70)


if __name__ == "__main__":
    main()

