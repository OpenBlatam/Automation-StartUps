#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
External Data Integration System for ClickUp Brain
=================================================
Integrates multiple external data sources to provide real-time market insights,
trend analysis, and competitive intelligence for budget-friendly engagement tactics.
"""

import requests
import json
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
import logging
from dataclasses import dataclass
import asyncio
import aiohttp
from concurrent.futures import ThreadPoolExecutor
import time

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class DataSource:
    """Data source configuration"""
    name: str
    api_endpoint: str
    api_key: str
    rate_limit: int  # requests per minute
    data_type: str
    priority: int  # 1 = highest priority

class ExternalDataIntegration:
    """
    Advanced external data integration system that combines multiple data sources
    to provide comprehensive market insights for engagement tactics.
    """
    
    def __init__(self):
        """Initialize external data integration system"""
        self.data_sources = self._initialize_data_sources()
        self.cache = {}
        self.cache_duration = 3600  # 1 hour cache
        self.session = requests.Session()
        
    def _initialize_data_sources(self) -> Dict[str, DataSource]:
        """Initialize external data sources configuration"""
        return {
            "social_media_insights": DataSource(
                name="Social Media Analytics API",
                api_endpoint="https://api.socialinsights.com/v1/trends",
                api_key="your_social_media_api_key",
                rate_limit=100,
                data_type="social_media_trends",
                priority=1
            ),
            "market_research": DataSource(
                name="Market Research Database",
                api_endpoint="https://api.marketresearch.com/v2/insights",
                api_key="your_market_research_api_key",
                rate_limit=50,
                data_type="market_insights",
                priority=2
            ),
            "competitor_analysis": DataSource(
                name="Competitor Intelligence API",
                api_endpoint="https://api.competitorintel.com/v1/analysis",
                api_key="your_competitor_api_key",
                rate_limit=30,
                data_type="competitor_data",
                priority=3
            ),
            "trend_analysis": DataSource(
                name="Trend Analysis Platform",
                api_endpoint="https://api.trends.com/v1/analysis",
                api_key="your_trends_api_key",
                rate_limit=60,
                data_type="trend_data",
                priority=2
            ),
            "influencer_insights": DataSource(
                name="Influencer Marketing Platform",
                api_endpoint="https://api.influencer.com/v2/insights",
                api_key="your_influencer_api_key",
                rate_limit=40,
                data_type="influencer_data",
                priority=1
            ),
            "content_performance": DataSource(
                name="Content Performance Analytics",
                api_endpoint="https://api.contentanalytics.com/v1/performance",
                api_key="your_content_api_key",
                rate_limit=80,
                data_type="content_metrics",
                priority=2
            )
        }
    
    def get_social_media_trends(self, platform: str = None, timeframe: str = "30d") -> Dict:
        """
        Get social media trends and insights
        
        Args:
            platform: Specific platform (tiktok, instagram, facebook, etc.)
            timeframe: Time period for analysis (7d, 30d, 90d)
        
        Returns:
            Dictionary with social media trends and insights
        """
        cache_key = f"social_trends_{platform}_{timeframe}"
        
        if self._is_cache_valid(cache_key):
            return self.cache[cache_key]
        
        # Simulated API call - in real implementation, this would call actual APIs
        trends_data = self._simulate_social_media_api_call(platform, timeframe)
        
        self.cache[cache_key] = {
            "timestamp": datetime.now().isoformat(),
            "platform": platform or "all",
            "timeframe": timeframe,
            "trending_hashtags": trends_data["trending_hashtags"],
            "engagement_rates": trends_data["engagement_rates"],
            "content_types": trends_data["content_types"],
            "optimal_posting_times": trends_data["optimal_posting_times"],
            "audience_insights": trends_data["audience_insights"],
            "competitor_analysis": trends_data["competitor_analysis"]
        }
        
        return self.cache[cache_key]
    
    def _simulate_social_media_api_call(self, platform: str, timeframe: str) -> Dict:
        """Simulate social media API call with realistic data"""
        base_trends = {
            "trending_hashtags": {
                "tiktok": ["#SmallBusiness", "#Entrepreneur", "#MarketingTips", "#BusinessGrowth", "#StartupLife"],
                "instagram": ["#BusinessOwner", "#MarketingStrategy", "#DigitalMarketing", "#ContentCreation", "#SocialMediaMarketing"],
                "facebook": ["#BusinessTips", "#Marketing", "#Entrepreneurship", "#SmallBusiness", "#BusinessGrowth"],
                "linkedin": ["#BusinessStrategy", "#Marketing", "#Entrepreneurship", "#Leadership", "#Innovation"]
            },
            "engagement_rates": {
                "tiktok": {"avg": 9.38, "video": 12.5, "image": 3.2},
                "instagram": {"avg": 1.22, "reels": 2.8, "posts": 0.8, "stories": 1.5},
                "facebook": {"avg": 0.18, "video": 0.35, "image": 0.12, "text": 0.08},
                "linkedin": {"avg": 2.45, "video": 4.2, "image": 1.8, "text": 2.1}
            },
            "content_types": {
                "tiktok": {"video": 95, "image": 5},
                "instagram": {"reels": 45, "posts": 35, "stories": 20},
                "facebook": {"video": 40, "image": 35, "text": 25},
                "linkedin": {"text": 50, "image": 30, "video": 20}
            },
            "optimal_posting_times": {
                "tiktok": ["6-10 AM", "7-9 PM"],
                "instagram": ["11 AM-1 PM", "5-7 PM"],
                "facebook": ["9 AM-12 PM", "3-4 PM"],
                "linkedin": ["8-10 AM", "12-2 PM"]
            },
            "audience_insights": {
                "tiktok": {"age_18_24": 45, "age_25_34": 35, "age_35_44": 15, "age_45_plus": 5},
                "instagram": {"age_18_24": 30, "age_25_34": 40, "age_35_44": 20, "age_45_plus": 10},
                "facebook": {"age_25_34": 25, "age_35_44": 30, "age_45_54": 25, "age_55_plus": 20},
                "linkedin": {"age_25_34": 35, "age_35_44": 40, "age_45_54": 20, "age_55_plus": 5}
            },
            "competitor_analysis": {
                "avg_engagement_rate": 2.8,
                "top_performing_content": ["Educational posts", "Behind-the-scenes", "User testimonials"],
                "content_frequency": {"daily": 45, "weekly": 35, "monthly": 20},
                "hashtag_usage": {"branded": 30, "trending": 40, "niche": 30}
            }
        }
        
        if platform and platform.lower() in base_trends["trending_hashtags"]:
            return {
                "trending_hashtags": base_trends["trending_hashtags"][platform.lower()],
                "engagement_rates": base_trends["engagement_rates"][platform.lower()],
                "content_types": base_trends["content_types"][platform.lower()],
                "optimal_posting_times": base_trends["optimal_posting_times"][platform.lower()],
                "audience_insights": base_trends["audience_insights"][platform.lower()],
                "competitor_analysis": base_trends["competitor_analysis"]
            }
        
        return base_trends
    
    def get_market_insights(self, industry: str, region: str = "global") -> Dict:
        """
        Get comprehensive market insights for specific industry
        
        Args:
            industry: Target industry
            region: Geographic region
        
        Returns:
            Dictionary with market insights and trends
        """
        cache_key = f"market_insights_{industry}_{region}"
        
        if self._is_cache_valid(cache_key):
            return self.cache[cache_key]
        
        # Simulated market research API call
        market_data = self._simulate_market_research_api_call(industry, region)
        
        self.cache[cache_key] = {
            "timestamp": datetime.now().isoformat(),
            "industry": industry,
            "region": region,
            "market_size": market_data["market_size"],
            "growth_rate": market_data["growth_rate"],
            "key_trends": market_data["key_trends"],
            "consumer_behavior": market_data["consumer_behavior"],
            "competitive_landscape": market_data["competitive_landscape"],
            "budget_benchmarks": market_data["budget_benchmarks"],
            "opportunities": market_data["opportunities"]
        }
        
        return self.cache[cache_key]
    
    def _simulate_market_research_api_call(self, industry: str, region: str) -> Dict:
        """Simulate market research API call with industry-specific data"""
        industry_data = {
            "technology": {
                "market_size": "$4.8T",
                "growth_rate": "12.5%",
                "key_trends": ["AI integration", "Remote work solutions", "Cybersecurity", "Cloud computing"],
                "consumer_behavior": {
                    "prefers_digital_channels": 78,
                    "values_innovation": 85,
                    "price_sensitive": 45,
                    "brand_loyal": 62
                },
                "competitive_landscape": {
                    "market_leaders": ["Microsoft", "Google", "Amazon", "Apple"],
                    "emerging_players": 15,
                    "market_concentration": "High"
                },
                "budget_benchmarks": {
                    "marketing_budget_percentage": 8.5,
                    "digital_marketing_percentage": 65,
                    "social_media_budget": 25,
                    "content_marketing_budget": 20
                },
                "opportunities": [
                    "AI-powered customer service",
                    "Personalized user experiences",
                    "Community-driven product development",
                    "Sustainability-focused messaging"
                ]
            },
            "fashion": {
                "market_size": "$1.5T",
                "growth_rate": "8.2%",
                "key_trends": ["Sustainable fashion", "Digital try-on", "Influencer marketing", "Fast fashion alternatives"],
                "consumer_behavior": {
                    "prefers_digital_channels": 65,
                    "values_innovation": 70,
                    "price_sensitive": 80,
                    "brand_loyal": 45
                },
                "competitive_landscape": {
                    "market_leaders": ["Nike", "Zara", "H&M", "Adidas"],
                    "emerging_players": 25,
                    "market_concentration": "Medium"
                },
                "budget_benchmarks": {
                    "marketing_budget_percentage": 12.0,
                    "digital_marketing_percentage": 55,
                    "social_media_budget": 35,
                    "content_marketing_budget": 25
                },
                "opportunities": [
                    "User-generated content campaigns",
                    "Micro-influencer partnerships",
                    "Sustainable fashion messaging",
                    "Virtual fashion experiences"
                ]
            },
            "finance": {
                "market_size": "$12.4T",
                "growth_rate": "6.8%",
                "key_trends": ["Fintech innovation", "Digital banking", "Cryptocurrency", "Financial literacy"],
                "consumer_behavior": {
                    "prefers_digital_channels": 72,
                    "values_innovation": 68,
                    "price_sensitive": 90,
                    "brand_loyal": 78
                },
                "competitive_landscape": {
                    "market_leaders": ["JPMorgan", "Bank of America", "Wells Fargo", "Goldman Sachs"],
                    "emerging_players": 12,
                    "market_concentration": "High"
                },
                "budget_benchmarks": {
                    "marketing_budget_percentage": 6.5,
                    "digital_marketing_percentage": 45,
                    "social_media_budget": 15,
                    "content_marketing_budget": 30
                },
                "opportunities": [
                    "Educational content marketing",
                    "Trust-building campaigns",
                    "Financial literacy programs",
                    "Community-driven financial advice"
                ]
            }
        }
        
        return industry_data.get(industry.lower(), industry_data["technology"])
    
    def get_competitor_analysis(self, competitors: List[str], industry: str) -> Dict:
        """
        Get competitor analysis and benchmarking data
        
        Args:
            competitors: List of competitor names
            industry: Industry context
        
        Returns:
            Dictionary with competitor analysis
        """
        cache_key = f"competitor_analysis_{'_'.join(competitors)}_{industry}"
        
        if self._is_cache_valid(cache_key):
            return self.cache[cache_key]
        
        # Simulated competitor analysis API call
        competitor_data = self._simulate_competitor_analysis_api_call(competitors, industry)
        
        self.cache[cache_key] = {
            "timestamp": datetime.now().isoformat(),
            "competitors": competitors,
            "industry": industry,
            "social_media_performance": competitor_data["social_media_performance"],
            "content_strategy": competitor_data["content_strategy"],
            "engagement_rates": competitor_data["engagement_rates"],
            "budget_estimates": competitor_data["budget_estimates"],
            "strengths_weaknesses": competitor_data["strengths_weaknesses"],
            "opportunities": competitor_data["opportunities"]
        }
        
        return self.cache[cache_key]
    
    def _simulate_competitor_analysis_api_call(self, competitors: List[str], industry: str) -> Dict:
        """Simulate competitor analysis API call"""
        return {
            "social_media_performance": {
                comp: {
                    "followers": f"{i * 100000 + 50000:,}",
                    "engagement_rate": round(1.5 + (i * 0.3), 2),
                    "posting_frequency": f"{2 + i} posts/day",
                    "top_platforms": ["Instagram", "LinkedIn", "TikTok"][:2+i]
                }
                for i, comp in enumerate(competitors)
            },
            "content_strategy": {
                comp: {
                    "content_types": ["Educational", "Behind-the-scenes", "User testimonials"],
                    "hashtag_strategy": "Mix of branded and trending",
                    "posting_schedule": "Consistent daily posting",
                    "content_themes": ["Innovation", "Customer success", "Industry insights"]
                }
                for comp in competitors
            },
            "engagement_rates": {
                comp: {
                    "avg_engagement": round(2.1 + (i * 0.4), 2),
                    "best_performing_content": "Video content",
                    "engagement_trend": "Increasing"
                }
                for i, comp in enumerate(competitors)
            },
            "budget_estimates": {
                comp: {
                    "estimated_monthly_budget": f"${(i + 1) * 50000:,}",
                    "social_media_percentage": 30 + (i * 5),
                    "content_creation_percentage": 25 + (i * 3)
                }
                for i, comp in enumerate(competitors)
            },
            "strengths_weaknesses": {
                comp: {
                    "strengths": ["Strong brand presence", "Consistent content", "High engagement"],
                    "weaknesses": ["Limited video content", "Inconsistent posting", "Low community interaction"]
                }
                for comp in competitors
            },
            "opportunities": [
                "Gap in video content creation",
                "Opportunity for community building",
                "Potential for influencer partnerships",
                "Room for user-generated content campaigns"
            ]
        }
    
    def get_influencer_insights(self, platform: str, niche: str = None) -> Dict:
        """
        Get influencer marketing insights and recommendations
        
        Args:
            platform: Social media platform
            niche: Specific niche or industry
        
        Returns:
            Dictionary with influencer insights
        """
        cache_key = f"influencer_insights_{platform}_{niche}"
        
        if self._is_cache_valid(cache_key):
            return self.cache[cache_key]
        
        # Simulated influencer insights API call
        influencer_data = self._simulate_influencer_insights_api_call(platform, niche)
        
        self.cache[cache_key] = {
            "timestamp": datetime.now().isoformat(),
            "platform": platform,
            "niche": niche,
            "influencer_tiers": influencer_data["influencer_tiers"],
            "engagement_rates": influencer_data["engagement_rates"],
            "cost_benchmarks": influencer_data["cost_benchmarks"],
            "best_practices": influencer_data["best_practices"],
            "trending_niches": influencer_data["trending_niches"],
            "success_metrics": influencer_data["success_metrics"]
        }
        
        return self.cache[cache_key]
    
    def _simulate_influencer_insights_api_call(self, platform: str, niche: str) -> Dict:
        """Simulate influencer insights API call"""
        return {
            "influencer_tiers": {
                "nano_influencers": {
                    "followers": "1K-10K",
                    "engagement_rate": "8.5%",
                    "cost_per_post": "$50-200",
                    "authenticity": "Very High",
                    "recommended_for": "Local businesses, niche products"
                },
                "micro_influencers": {
                    "followers": "10K-100K",
                    "engagement_rate": "6.2%",
                    "cost_per_post": "$200-1000",
                    "authenticity": "High",
                    "recommended_for": "Brand awareness, product launches"
                },
                "macro_influencers": {
                    "followers": "100K-1M",
                    "engagement_rate": "3.8%",
                    "cost_per_post": "$1000-10000",
                    "authenticity": "Medium",
                    "recommended_for": "Mass market campaigns"
                },
                "mega_influencers": {
                    "followers": "1M+",
                    "engagement_rate": "2.1%",
                    "cost_per_post": "$10000+",
                    "authenticity": "Low",
                    "recommended_for": "Brand partnerships, major campaigns"
                }
            },
            "engagement_rates": {
                "tiktok": {"avg": 9.38, "nano": 12.5, "micro": 8.2, "macro": 4.1, "mega": 2.3},
                "instagram": {"avg": 1.22, "nano": 3.8, "micro": 2.1, "macro": 1.2, "mega": 0.8},
                "youtube": {"avg": 2.45, "nano": 4.2, "micro": 3.1, "macro": 2.0, "mega": 1.5}
            },
            "cost_benchmarks": {
                "cost_per_1000_followers": {
                    "nano": "$5-15",
                    "micro": "$10-25",
                    "macro": "$20-50",
                    "mega": "$50-200"
                },
                "cost_per_engagement": {
                    "nano": "$0.50-2.00",
                    "micro": "$1.00-3.00",
                    "macro": "$2.00-8.00",
                    "mega": "$5.00-25.00"
                }
            },
            "best_practices": [
                "Focus on nano and micro-influencers for better ROI",
                "Prioritize engagement rate over follower count",
                "Look for authentic content creators in your niche",
                "Establish long-term partnerships over one-off campaigns",
                "Provide creative freedom while maintaining brand guidelines"
            ],
            "trending_niches": [
                "Sustainable living",
                "Mental health awareness",
                "Financial literacy",
                "Remote work tips",
                "Home improvement",
                "Fitness and wellness",
                "Technology reviews",
                "Food and cooking"
            ],
            "success_metrics": [
                "Engagement rate",
                "Cost per engagement",
                "Brand mention sentiment",
                "Website traffic from influencer content",
                "Sales attributed to influencer campaigns",
                "Follower growth from influencer partnerships"
            ]
        }
    
    def get_content_performance_insights(self, content_type: str, platform: str) -> Dict:
        """
        Get content performance insights and optimization recommendations
        
        Args:
            content_type: Type of content (video, image, text, etc.)
            platform: Social media platform
        
        Returns:
            Dictionary with content performance insights
        """
        cache_key = f"content_performance_{content_type}_{platform}"
        
        if self._is_cache_valid(cache_key):
            return self.cache[cache_key]
        
        # Simulated content performance API call
        content_data = self._simulate_content_performance_api_call(content_type, platform)
        
        self.cache[cache_key] = {
            "timestamp": datetime.now().isoformat(),
            "content_type": content_type,
            "platform": platform,
            "performance_metrics": content_data["performance_metrics"],
            "optimization_tips": content_data["optimization_tips"],
            "best_practices": content_data["best_practices"],
            "trending_formats": content_data["trending_formats"],
            "audience_preferences": content_data["audience_preferences"]
        }
        
        return self.cache[cache_key]
    
    def _simulate_content_performance_api_call(self, content_type: str, platform: str) -> Dict:
        """Simulate content performance API call"""
        performance_data = {
            "video": {
                "tiktok": {"avg_engagement": 12.5, "completion_rate": 78, "share_rate": 8.2},
                "instagram": {"avg_engagement": 4.2, "completion_rate": 65, "share_rate": 3.1},
                "youtube": {"avg_engagement": 2.8, "completion_rate": 45, "share_rate": 1.8}
            },
            "image": {
                "instagram": {"avg_engagement": 1.8, "save_rate": 12, "share_rate": 2.1},
                "facebook": {"avg_engagement": 0.8, "save_rate": 5, "share_rate": 1.2},
                "linkedin": {"avg_engagement": 2.1, "save_rate": 8, "share_rate": 1.5}
            },
            "text": {
                "linkedin": {"avg_engagement": 3.2, "comment_rate": 15, "share_rate": 4.1},
                "facebook": {"avg_engagement": 0.6, "comment_rate": 8, "share_rate": 1.8},
                "twitter": {"avg_engagement": 1.2, "comment_rate": 5, "share_rate": 2.8}
            }
        }
        
        return {
            "performance_metrics": performance_data.get(content_type, {}).get(platform, {
                "avg_engagement": 2.1,
                "completion_rate": 60,
                "share_rate": 3.5
            }),
            "optimization_tips": [
                "Use captions and subtitles for video content",
                "Post at optimal times for your audience",
                "Include clear call-to-actions",
                "Use trending hashtags relevant to your niche",
                "Engage with comments within first hour"
            ],
            "best_practices": [
                "Maintain consistent visual branding",
                "Tell a story with your content",
                "Use high-quality visuals and audio",
                "Test different content formats",
                "Monitor and respond to engagement"
            ],
            "trending_formats": [
                "Short-form video content",
                "Behind-the-scenes content",
                "User-generated content",
                "Educational tutorials",
                "Interactive polls and questions"
            ],
            "audience_preferences": {
                "preferred_length": "15-30 seconds" if content_type == "video" else "N/A",
                "best_posting_times": ["6-9 AM", "12-2 PM", "7-9 PM"],
                "most_engaging_elements": ["Authentic storytelling", "Visual appeal", "Relevant hashtags"]
            }
        }
    
    def get_comprehensive_insights(self, industry: str, platforms: List[str], 
                                 competitors: List[str] = None) -> Dict:
        """
        Get comprehensive insights combining all data sources
        
        Args:
            industry: Target industry
            platforms: List of social media platforms
            competitors: List of competitors to analyze
        
        Returns:
            Comprehensive insights dictionary
        """
        logger.info(f"Generating comprehensive insights for {industry} industry")
        
        insights = {
            "timestamp": datetime.now().isoformat(),
            "industry": industry,
            "platforms": platforms,
            "data_sources": {}
        }
        
        # Get market insights
        insights["data_sources"]["market_insights"] = self.get_market_insights(industry)
        
        # Get social media trends for each platform
        insights["data_sources"]["social_media_trends"] = {}
        for platform in platforms:
            insights["data_sources"]["social_media_trends"][platform] = self.get_social_media_trends(platform)
        
        # Get competitor analysis if competitors provided
        if competitors:
            insights["data_sources"]["competitor_analysis"] = self.get_competitor_analysis(competitors, industry)
        
        # Get influencer insights
        insights["data_sources"]["influencer_insights"] = {}
        for platform in platforms:
            insights["data_sources"]["influencer_insights"][platform] = self.get_influencer_insights(platform, industry)
        
        # Get content performance insights
        insights["data_sources"]["content_performance"] = {}
        content_types = ["video", "image", "text"]
        for content_type in content_types:
            for platform in platforms:
                key = f"{content_type}_{platform}"
                insights["data_sources"]["content_performance"][key] = self.get_content_performance_insights(content_type, platform)
        
        # Generate summary insights
        insights["summary"] = self._generate_insights_summary(insights["data_sources"])
        
        return insights
    
    def _generate_insights_summary(self, data_sources: Dict) -> Dict:
        """Generate summary insights from all data sources"""
        summary = {
            "key_opportunities": [],
            "budget_recommendations": {},
            "platform_priorities": {},
            "content_strategy": {},
            "influencer_strategy": {},
            "competitive_advantages": []
        }
        
        # Extract key opportunities from market insights
        if "market_insights" in data_sources:
            market_data = data_sources["market_insights"]
            summary["key_opportunities"].extend(market_data.get("opportunities", []))
            summary["budget_recommendations"] = market_data.get("budget_benchmarks", {})
        
        # Analyze platform performance
        if "social_media_trends" in data_sources:
            for platform, trends in data_sources["social_media_trends"].items():
                summary["platform_priorities"][platform] = {
                    "engagement_rate": trends.get("engagement_rates", {}).get("avg", 0),
                    "trending_hashtags": trends.get("trending_hashtags", [])[:3],
                    "optimal_posting_times": trends.get("optimal_posting_times", [])
                }
        
        # Content strategy recommendations
        if "content_performance" in data_sources:
            best_performing = {}
            for key, performance in data_sources["content_performance"].items():
                content_type, platform = key.split("_", 1)
                if platform not in best_performing:
                    best_performing[platform] = {"type": content_type, "engagement": 0}
                
                current_engagement = performance.get("performance_metrics", {}).get("avg_engagement", 0)
                if current_engagement > best_performing[platform]["engagement"]:
                    best_performing[platform] = {"type": content_type, "engagement": current_engagement}
            
            summary["content_strategy"] = best_performing
        
        # Influencer strategy recommendations
        if "influencer_insights" in data_sources:
            for platform, insights in data_sources["influencer_insights"].items():
                summary["influencer_strategy"][platform] = {
                    "recommended_tier": "micro_influencers",
                    "expected_engagement": insights.get("engagement_rates", {}).get("micro", 0),
                    "cost_range": insights.get("cost_benchmarks", {}).get("cost_per_post", {}).get("micro", "N/A")
                }
        
        return summary
    
    def _is_cache_valid(self, cache_key: str) -> bool:
        """Check if cached data is still valid"""
        if cache_key not in self.cache:
            return False
        
        cached_time = datetime.fromisoformat(self.cache[cache_key]["timestamp"])
        return (datetime.now() - cached_time).seconds < self.cache_duration
    
    def export_insights(self, insights: Dict, filename: str = None) -> str:
        """Export insights to JSON file"""
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"external_data_insights_{timestamp}.json"
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(insights, f, ensure_ascii=False, indent=2, default=str)
        
        logger.info(f"External data insights exported to: {filename}")
        return filename

def main():
    """Demonstration of External Data Integration System"""
    print("🌐 External Data Integration System for ClickUp Brain")
    print("=" * 60)
    
    # Initialize system
    data_integration = ExternalDataIntegration()
    
    # Example usage scenarios
    scenarios = [
        {
            "name": "Technology Startup",
            "industry": "technology",
            "platforms": ["tiktok", "instagram", "linkedin"],
            "competitors": ["TechCorp", "InnovateLabs", "StartupXYZ"]
        },
        {
            "name": "Fashion Brand",
            "industry": "fashion",
            "platforms": ["instagram", "tiktok", "facebook"],
            "competitors": ["FashionForward", "StyleHub", "TrendyBrand"]
        }
    ]
    
    for scenario in scenarios:
        print(f"\n📊 {scenario['name']} Analysis")
        print("-" * 40)
        
        # Get comprehensive insights
        insights = data_integration.get_comprehensive_insights(
            industry=scenario["industry"],
            platforms=scenario["platforms"],
            competitors=scenario["competitors"]
        )
        
        # Display key insights
        summary = insights["summary"]
        print(f"🎯 Key Opportunities: {len(summary['key_opportunities'])} identified")
        print(f"📱 Platform Priorities: {list(summary['platform_priorities'].keys())}")
        print(f"🎨 Content Strategy: {summary['content_strategy']}")
        print(f"👥 Influencer Strategy: {list(summary['influencer_strategy'].keys())}")
        
        # Export insights
        filename = data_integration.export_insights(insights, f"insights_{scenario['name'].lower().replace(' ', '_')}.json")
        print(f"📄 Insights saved: {filename}")
    
    print(f"\n✨ External data integration analysis complete!")
    print("💡 Use the generated insights to inform your engagement strategy.")

if __name__ == "__main__":
    main()


