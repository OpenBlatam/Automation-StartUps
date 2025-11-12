#!/usr/bin/env python3
"""
Generador Avanzado de Hashtags para TikTok
Genera hashtags actualizados y relevantes basados en industria y público objetivo
Incluye análisis de tendencias, scoring inteligente y recomendaciones personalizadas
"""

import json
import random
from typing import List, Dict, Optional, Tuple
from datetime import datetime, timedelta
from collections import Counter
from dataclasses import dataclass


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


def main():
    """Función principal para uso desde CLI"""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Genera hashtags personalizados para TikTok"
    )
    parser.add_argument(
        "--industry",
        type=str,
        required=True,
        help="Industria: tech, ecommerce, marketing, fitness, food, education, beauty, finance, automation"
    )
    parser.add_argument(
        "--demographic",
        type=str,
        required=True,
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
    
    args = parser.parse_args()
    
    generator = TikTokHashtagGenerator(
        industry=args.industry,
        demographic=args.demographic,
        custom_keywords=args.keywords,
        content_type=args.content_type,
        video_length=args.video_length
    )
    
    recommendation = generator.get_full_recommendation(include_scores=args.scores)
    
    # Análisis de rendimiento si se solicita
    if args.analyze:
        analysis = generator.analyze_hashtag_performance(recommendation['main_hashtags'])
        recommendation['performance_analysis'] = analysis
    
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
        
        print(f"\n📝 Cadena Completa de Hashtags:")
        print("   " + recommendation['formatted_string'])
        print("\n" + "="*70)


if __name__ == "__main__":
    main()

