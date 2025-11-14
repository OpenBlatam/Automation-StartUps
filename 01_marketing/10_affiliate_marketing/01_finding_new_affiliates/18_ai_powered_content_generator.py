#!/usr/bin/env python3
"""
AI-Powered Content Generator for Affiliate Marketing
===================================================

This module provides intelligent content generation capabilities for affiliate marketing,
including personalized content creation, A/B testing, and performance optimization.

Author: AI Marketing System
Version: 2.0
"""

import openai
import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Tuple
import json
import re
from datetime import datetime, timedelta
import asyncio
import aiohttp
from dataclasses import dataclass, asdict
from enum import Enum
import logging
from PIL import Image, ImageDraw, ImageFont
import requests
from io import BytesIO
import textstat
from transformers import pipeline, AutoTokenizer, AutoModelForSequenceGeneration
import torch

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ContentType(Enum):
    """Types of content"""
    EMAIL = "email"
    SOCIAL_MEDIA = "social_media"
    BLOG_POST = "blog_post"
    AD_COPY = "ad_copy"
    LANDING_PAGE = "landing_page"
    VIDEO_SCRIPT = "video_script"
    PODCAST_SCRIPT = "podcast_script"

class ContentTone(Enum):
    """Content tone options"""
    PROFESSIONAL = "professional"
    CASUAL = "casual"
    FRIENDLY = "friendly"
    URGENT = "urgent"
    INSPIRATIONAL = "inspirational"
    EDUCATIONAL = "educational"

@dataclass
class ContentRequest:
    """Content generation request"""
    content_type: ContentType
    target_audience: str
    product_info: Dict
    tone: ContentTone
    length: str  # short, medium, long
    keywords: List[str]
    call_to_action: str
    affiliate_id: str
    campaign_id: str

@dataclass
class GeneratedContent:
    """Generated content structure"""
    content_id: str
    content_type: ContentType
    title: str
    body: str
    call_to_action: str
    metadata: Dict
    performance_score: float
    created_at: datetime
    affiliate_id: str
    campaign_id: str

class AIContentGenerator:
    """
    AI-Powered Content Generator for Affiliate Marketing
    """
    
    def __init__(self, openai_api_key: str):
        self.openai_api_key = openai_api_key
        openai.api_key = openai_api_key
        
        # Initialize content templates
        self.templates = self._load_templates()
        
        # Initialize performance tracking
        self.content_performance = {}
        self.optimization_rules = []
        
        # Initialize AI models
        self._initialize_ai_models()
    
    def _initialize_ai_models(self):
        """
        Initialize AI models for content generation
        """
        try:
            # Initialize text generation pipeline
            self.text_generator = pipeline(
                "text-generation",
                model="gpt2",
                tokenizer="gpt2",
                device=0 if torch.cuda.is_available() else -1
            )
            
            # Initialize sentiment analysis
            self.sentiment_analyzer = pipeline(
                "sentiment-analysis",
                model="cardiffnlp/twitter-roberta-base-sentiment-latest"
            )
            
            logger.info("AI models initialized successfully")
            
        except Exception as e:
            logger.warning(f"Could not initialize AI models: {str(e)}")
            self.text_generator = None
            self.sentiment_analyzer = None
    
    def _load_templates(self) -> Dict:
        """
        Load content templates
        """
        templates = {
            ContentType.EMAIL: {
                'subject_templates': [
                    "🚀 Exclusive {product_name} Offer Just for You!",
                    "Don't Miss Out: {product_name} Special Deal",
                    "Limited Time: {product_name} Discount Inside"
                ],
                'body_templates': [
                    "Hi {name},\n\nI wanted to share something special with you...",
                    "Hey {name},\n\nI've been using {product_name} and the results are amazing...",
                    "Hi {name},\n\nI know you're interested in {niche}, so I thought you'd love this..."
                ]
            },
            ContentType.SOCIAL_MEDIA: {
                'post_templates': [
                    "🔥 Just discovered {product_name} and it's a game-changer! {benefit}",
                    "Can't believe the results I'm getting with {product_name}! {testimonial}",
                    "If you're into {niche}, you need to check out {product_name}. {cta}"
                ],
                'hashtag_templates': [
                    "#{niche} #{product_name} #affiliate #recommendation",
                    "#{niche} #review #honest #affiliate",
                    "#{product_name} #testimonial #results #affiliate"
                ]
            },
            ContentType.BLOG_POST: {
                'title_templates': [
                    "Why {product_name} is the Best {niche} Solution in 2024",
                    "My Honest Review of {product_name}: {benefit}",
                    "How {product_name} Changed My {niche} Game Forever"
                ],
                'introduction_templates': [
                    "If you're looking for the best {niche} solution, you've come to the right place...",
                    "After months of testing {product_name}, I can confidently say...",
                    "I've been using {product_name} for {timeframe} and here's what I've learned..."
                ]
            }
        }
        
        return templates
    
    async def generate_content(self, request: ContentRequest) -> GeneratedContent:
        """
        Generate AI-powered content
        """
        logger.info(f"Generating {request.content_type.value} content for {request.affiliate_id}")
        
        # Generate content based on type
        if request.content_type == ContentType.EMAIL:
            content = await self._generate_email_content(request)
        elif request.content_type == ContentType.SOCIAL_MEDIA:
            content = await self._generate_social_media_content(request)
        elif request.content_type == ContentType.BLOG_POST:
            content = await self._generate_blog_post_content(request)
        elif request.content_type == ContentType.AD_COPY:
            content = await self._generate_ad_copy_content(request)
        elif request.content_type == ContentType.LANDING_PAGE:
            content = await self._generate_landing_page_content(request)
        elif request.content_type == ContentType.VIDEO_SCRIPT:
            content = await self._generate_video_script_content(request)
        elif request.content_type == ContentType.PODCAST_SCRIPT:
            content = await self._generate_podcast_script_content(request)
        else:
            content = await self._generate_generic_content(request)
        
        # Optimize content
        optimized_content = await self._optimize_content(content, request)
        
        # Calculate performance score
        performance_score = self._calculate_performance_score(optimized_content, request)
        
        # Create generated content object
        generated_content = GeneratedContent(
            content_id=f"content_{len(self.content_performance)}",
            content_type=request.content_type,
            title=optimized_content.get('title', ''),
            body=optimized_content.get('body', ''),
            call_to_action=optimized_content.get('call_to_action', request.call_to_action),
            metadata=optimized_content.get('metadata', {}),
            performance_score=performance_score,
            created_at=datetime.now(),
            affiliate_id=request.affiliate_id,
            campaign_id=request.campaign_id
        )
        
        # Store performance data
        self.content_performance[generated_content.content_id] = {
            'content': generated_content,
            'request': request,
            'performance_score': performance_score
        }
        
        return generated_content
    
    async def _generate_email_content(self, request: ContentRequest) -> Dict:
        """
        Generate email content
        """
        # Get templates
        templates = self.templates[ContentType.EMAIL]
        
        # Select random template
        subject_template = np.random.choice(templates['subject_templates'])
        body_template = np.random.choice(templates['body_templates'])
        
        # Format templates
        subject = subject_template.format(
            product_name=request.product_info.get('name', 'Product'),
            **request.product_info
        )
        
        body = body_template.format(
            name=request.target_audience,
            product_name=request.product_info.get('name', 'Product'),
            niche=request.product_info.get('niche', 'niche'),
            **request.product_info
        )
        
        # Add AI-generated content
        ai_enhancement = await self._generate_ai_enhancement(request, ContentType.EMAIL)
        
        return {
            'title': subject,
            'body': body + "\n\n" + ai_enhancement,
            'call_to_action': request.call_to_action,
            'metadata': {
                'tone': request.tone.value,
                'length': request.length,
                'keywords': request.keywords
            }
        }
    
    async def _generate_social_media_content(self, request: ContentRequest) -> Dict:
        """
        Generate social media content
        """
        # Get templates
        templates = self.templates[ContentType.SOCIAL_MEDIA]
        
        # Select random template
        post_template = np.random.choice(templates['post_templates'])
        hashtag_template = np.random.choice(templates['hashtag_templates'])
        
        # Format templates
        post = post_template.format(
            product_name=request.product_info.get('name', 'Product'),
            benefit=request.product_info.get('benefit', 'amazing results'),
            testimonial=request.product_info.get('testimonial', 'incredible results'),
            niche=request.product_info.get('niche', 'niche'),
            cta=request.call_to_action,
            **request.product_info
        )
        
        hashtags = hashtag_template.format(
            niche=request.product_info.get('niche', 'niche'),
            product_name=request.product_info.get('name', 'Product'),
            **request.product_info
        )
        
        # Add AI-generated content
        ai_enhancement = await self._generate_ai_enhancement(request, ContentType.SOCIAL_MEDIA)
        
        return {
            'title': post,
            'body': post + "\n\n" + ai_enhancement + "\n\n" + hashtags,
            'call_to_action': request.call_to_action,
            'metadata': {
                'tone': request.tone.value,
                'length': request.length,
                'keywords': request.keywords,
                'hashtags': hashtags.split()
            }
        }
    
    async def _generate_blog_post_content(self, request: ContentRequest) -> Dict:
        """
        Generate blog post content
        """
        # Get templates
        templates = self.templates[ContentType.BLOG_POST]
        
        # Select random template
        title_template = np.random.choice(templates['title_templates'])
        intro_template = np.random.choice(templates['introduction_templates'])
        
        # Format templates
        title = title_template.format(
            product_name=request.product_info.get('name', 'Product'),
            niche=request.product_info.get('niche', 'niche'),
            benefit=request.product_info.get('benefit', 'amazing results'),
            **request.product_info
        )
        
        intro = intro_template.format(
            niche=request.product_info.get('niche', 'niche'),
            product_name=request.product_info.get('name', 'Product'),
            timeframe=request.product_info.get('timeframe', 'several months'),
            **request.product_info
        )
        
        # Generate blog post structure
        blog_structure = await self._generate_blog_structure(request)
        
        # Add AI-generated content
        ai_enhancement = await self._generate_ai_enhancement(request, ContentType.BLOG_POST)
        
        return {
            'title': title,
            'body': intro + "\n\n" + blog_structure + "\n\n" + ai_enhancement,
            'call_to_action': request.call_to_action,
            'metadata': {
                'tone': request.tone.value,
                'length': request.length,
                'keywords': request.keywords,
                'structure': blog_structure
            }
        }
    
    async def _generate_ad_copy_content(self, request: ContentRequest) -> Dict:
        """
        Generate ad copy content
        """
        # Generate headline
        headline = await self._generate_headline(request)
        
        # Generate body copy
        body_copy = await self._generate_body_copy(request)
        
        # Generate call-to-action
        cta = await self._generate_cta(request)
        
        return {
            'title': headline,
            'body': body_copy,
            'call_to_action': cta,
            'metadata': {
                'tone': request.tone.value,
                'length': request.length,
                'keywords': request.keywords
            }
        }
    
    async def _generate_landing_page_content(self, request: ContentRequest) -> Dict:
        """
        Generate landing page content
        """
        # Generate headline
        headline = await self._generate_headline(request)
        
        # Generate subheadline
        subheadline = await self._generate_subheadline(request)
        
        # Generate body content
        body_content = await self._generate_body_copy(request)
        
        # Generate features list
        features = await self._generate_features_list(request)
        
        # Generate testimonials
        testimonials = await self._generate_testimonials(request)
        
        return {
            'title': headline,
            'body': f"{subheadline}\n\n{body_content}\n\n{features}\n\n{testimonials}",
            'call_to_action': request.call_to_action,
            'metadata': {
                'tone': request.tone.value,
                'length': request.length,
                'keywords': request.keywords,
                'features': features,
                'testimonials': testimonials
            }
        }
    
    async def _generate_video_script_content(self, request: ContentRequest) -> Dict:
        """
        Generate video script content
        """
        # Generate script structure
        script_structure = await self._generate_video_script_structure(request)
        
        # Generate dialogue
        dialogue = await self._generate_dialogue(request)
        
        # Generate visual cues
        visual_cues = await self._generate_visual_cues(request)
        
        return {
            'title': f"Video Script: {request.product_info.get('name', 'Product')}",
            'body': f"{script_structure}\n\n{dialogue}\n\n{visual_cues}",
            'call_to_action': request.call_to_action,
            'metadata': {
                'tone': request.tone.value,
                'length': request.length,
                'keywords': request.keywords,
                'script_structure': script_structure,
                'dialogue': dialogue,
                'visual_cues': visual_cues
            }
        }
    
    async def _generate_podcast_script_content(self, request: ContentRequest) -> Dict:
        """
        Generate podcast script content
        """
        # Generate script structure
        script_structure = await self._generate_podcast_script_structure(request)
        
        # Generate dialogue
        dialogue = await self._generate_dialogue(request)
        
        # Generate talking points
        talking_points = await self._generate_talking_points(request)
        
        return {
            'title': f"Podcast Script: {request.product_info.get('name', 'Product')}",
            'body': f"{script_structure}\n\n{dialogue}\n\n{talking_points}",
            'call_to_action': request.call_to_action,
            'metadata': {
                'tone': request.tone.value,
                'length': request.length,
                'keywords': request.keywords,
                'script_structure': script_structure,
                'dialogue': dialogue,
                'talking_points': talking_points
            }
        }
    
    async def _generate_generic_content(self, request: ContentRequest) -> Dict:
        """
        Generate generic content
        """
        # Generate basic content structure
        title = await self._generate_headline(request)
        body = await self._generate_body_copy(request)
        
        return {
            'title': title,
            'body': body,
            'call_to_action': request.call_to_action,
            'metadata': {
                'tone': request.tone.value,
                'length': request.length,
                'keywords': request.keywords
            }
        }
    
    async def _generate_ai_enhancement(self, request: ContentRequest, content_type: ContentType) -> str:
        """
        Generate AI-enhanced content
        """
        try:
            prompt = f"""
            Generate compelling {content_type.value} content for affiliate marketing:
            
            Product: {request.product_info.get('name', 'Product')}
            Target Audience: {request.target_audience}
            Tone: {request.tone.value}
            Keywords: {', '.join(request.keywords)}
            
            Make it engaging, persuasive, and optimized for conversions.
            """
            
            response = await openai.ChatCompletion.acreate(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=500
            )
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            logger.error(f"Error generating AI enhancement: {str(e)}")
            return ""
    
    async def _generate_headline(self, request: ContentRequest) -> str:
        """
        Generate compelling headline
        """
        headlines = [
            f"Transform Your {request.product_info.get('niche', 'Business')} with {request.product_info.get('name', 'Product')}",
            f"The {request.product_info.get('name', 'Product')} Secret That's Changing Everything",
            f"Why {request.product_info.get('name', 'Product')} is the #1 Choice for {request.target_audience}",
            f"Get {request.product_info.get('benefit', 'Amazing Results')} with {request.product_info.get('name', 'Product')}",
            f"The Ultimate {request.product_info.get('name', 'Product')} Guide for {request.target_audience}"
        ]
        
        return np.random.choice(headlines)
    
    async def _generate_subheadline(self, request: ContentRequest) -> str:
        """
        Generate compelling subheadline
        """
        subheadlines = [
            f"Discover how {request.product_info.get('name', 'Product')} can revolutionize your {request.product_info.get('niche', 'business')}",
            f"Join thousands of satisfied customers who've transformed their {request.product_info.get('niche', 'business')}",
            f"Get instant access to the {request.product_info.get('name', 'Product')} system that's generating {request.product_info.get('benefit', 'amazing results')}",
            f"Learn the proven strategies that are helping {request.target_audience} achieve {request.product_info.get('benefit', 'incredible results')}",
            f"Unlock the power of {request.product_info.get('name', 'Product')} and start seeing results today"
        ]
        
        return np.random.choice(subheadlines)
    
    async def _generate_body_copy(self, request: ContentRequest) -> str:
        """
        Generate compelling body copy
        """
        body_templates = [
            f"Are you tired of struggling with {request.product_info.get('niche', 'your business')}? {request.product_info.get('name', 'Product')} is the solution you've been looking for. With {request.product_info.get('benefit', 'amazing results')}, you'll see the difference immediately.",
            f"Imagine having {request.product_info.get('benefit', 'incredible results')} in your {request.product_info.get('niche', 'business')}. That's exactly what {request.product_info.get('name', 'Product')} delivers. Join thousands of satisfied customers who've already transformed their {request.product_info.get('niche', 'business')}.",
            f"Don't let another day pass without experiencing the power of {request.product_info.get('name', 'Product')}. This revolutionary solution has helped {request.target_audience} achieve {request.product_info.get('benefit', 'amazing results')} and you can too."
        ]
        
        return np.random.choice(body_templates)
    
    async def _generate_cta(self, request: ContentRequest) -> str:
        """
        Generate compelling call-to-action
        """
        cta_templates = [
            f"Get {request.product_info.get('name', 'Product')} Now and Start Seeing Results Today!",
            f"Don't Wait - Transform Your {request.product_info.get('niche', 'Business')} Now!",
            f"Join the {request.product_info.get('name', 'Product')} Revolution Today!",
            f"Get Instant Access to {request.product_info.get('name', 'Product')} Now!",
            f"Start Your {request.product_info.get('name', 'Product')} Journey Today!"
        ]
        
        return np.random.choice(cta_templates)
    
    async def _generate_blog_structure(self, request: ContentRequest) -> str:
        """
        Generate blog post structure
        """
        structure = f"""
## Why {request.product_info.get('name', 'Product')} is Perfect for {request.target_audience}

### Key Benefits:
- {request.product_info.get('benefit', 'Amazing results')}
- Easy to use and implement
- Proven track record of success
- Perfect for {request.product_info.get('niche', 'your business')}

### How It Works:
1. Simple setup process
2. Immediate results
3. Ongoing support and updates
4. Continuous improvement

### Real Results:
- Increased efficiency by 300%
- Reduced costs by 50%
- Improved customer satisfaction
- Higher conversion rates
        """
        
        return structure
    
    async def _generate_video_script_structure(self, request: ContentRequest) -> str:
        """
        Generate video script structure
        """
        structure = f"""
## Video Script Structure

### Opening (0-10 seconds):
- Hook: "Are you struggling with {request.product_info.get('niche', 'your business')}?"
- Problem: "I know exactly how you feel..."
- Solution: "That's why I want to share {request.product_info.get('name', 'Product')} with you"

### Main Content (10-60 seconds):
- Introduce {request.product_info.get('name', 'Product')}
- Show key benefits
- Demonstrate value
- Build trust and credibility

### Closing (60-90 seconds):
- Call to action
- Urgency and scarcity
- Next steps
        """
        
        return structure
    
    async def _generate_podcast_script_structure(self, request: ContentRequest) -> str:
        """
        Generate podcast script structure
        """
        structure = f"""
## Podcast Script Structure

### Introduction (0-30 seconds):
- Welcome and introduction
- Today's topic: {request.product_info.get('name', 'Product')}
- Why this matters to listeners

### Main Discussion (30-15 minutes):
- Deep dive into {request.product_info.get('name', 'Product')}
- Share personal experience
- Discuss benefits and features
- Address common objections

### Conclusion (15-20 minutes):
- Recap key points
- Call to action
- Thank listeners
        """
        
        return structure
    
    async def _generate_dialogue(self, request: ContentRequest) -> str:
        """
        Generate dialogue content
        """
        dialogue = f"""
## Sample Dialogue

**Host**: "Today I want to talk about something that's completely changed my {request.product_info.get('niche', 'business')} - {request.product_info.get('name', 'Product')}."

**Host**: "I was skeptical at first, but after using it for just a few weeks, I saw {request.product_info.get('benefit', 'amazing results')}."

**Host**: "What I love most about {request.product_info.get('name', 'Product')} is how easy it is to use. You don't need to be a tech expert to get started."

**Host**: "If you're looking for a solution to your {request.product_info.get('niche', 'business')} challenges, {request.product_info.get('name', 'Product')} is definitely worth checking out."
        """
        
        return dialogue
    
    async def _generate_visual_cues(self, request: ContentRequest) -> str:
        """
        Generate visual cues for video
        """
        visual_cues = f"""
## Visual Cues

### Opening Scene:
- Show {request.product_info.get('name', 'Product')} interface
- Display key features
- Show before/after results

### Main Content:
- Screen recordings of {request.product_info.get('name', 'Product')} in action
- Charts and graphs showing results
- Customer testimonials
- Product demonstrations

### Closing Scene:
- Call-to-action button
- Contact information
- Social media links
        """
        
        return visual_cues
    
    async def _generate_talking_points(self, request: ContentRequest) -> str:
        """
        Generate talking points
        """
        talking_points = f"""
## Key Talking Points

1. **Problem**: "Many {request.target_audience} struggle with {request.product_info.get('niche', 'business')} challenges"
2. **Solution**: "{request.product_info.get('name', 'Product')} solves these problems effectively"
3. **Benefits**: "You'll get {request.product_info.get('benefit', 'amazing results')} quickly"
4. **Proof**: "Thousands of satisfied customers can't be wrong"
5. **Action**: "Don't wait - get started with {request.product_info.get('name', 'Product')} today"
        """
        
        return talking_points
    
    async def _generate_features_list(self, request: ContentRequest) -> str:
        """
        Generate features list
        """
        features = f"""
## Key Features of {request.product_info.get('name', 'Product')}

✅ **Easy to Use**: Simple interface that anyone can master
✅ **Proven Results**: {request.product_info.get('benefit', 'Amazing results')} guaranteed
✅ **24/7 Support**: Help when you need it
✅ **Regular Updates**: Always improving and evolving
✅ **Money-Back Guarantee**: Risk-free trial
✅ **Perfect for {request.product_info.get('niche', 'Your Business')}**: Designed specifically for your needs
        """
        
        return features
    
    async def _generate_testimonials(self, request: ContentRequest) -> str:
        """
        Generate testimonials
        """
        testimonials = f"""
## What Our Customers Say

**Sarah M.**: "I've been using {request.product_info.get('name', 'Product')} for 6 months and the results are incredible. My {request.product_info.get('niche', 'business')} has never been better!"

**Mike R.**: "This is exactly what I needed for my {request.product_info.get('niche', 'business')}. The {request.product_info.get('benefit', 'results')} speak for themselves."

**Lisa K.**: "I wish I had found {request.product_info.get('name', 'Product')} sooner. It's completely transformed my {request.product_info.get('niche', 'business')}."
        """
        
        return testimonials
    
    async def _optimize_content(self, content: Dict, request: ContentRequest) -> Dict:
        """
        Optimize content for better performance
        """
        # Analyze readability
        readability_score = self._analyze_readability(content['body'])
        
        # Analyze sentiment
        sentiment_score = self._analyze_sentiment(content['body'])
        
        # Optimize for keywords
        optimized_body = self._optimize_keywords(content['body'], request.keywords)
        
        # Add performance metadata
        content['metadata']['readability_score'] = readability_score
        content['metadata']['sentiment_score'] = sentiment_score
        content['metadata']['optimization_applied'] = True
        
        content['body'] = optimized_body
        
        return content
    
    def _analyze_readability(self, text: str) -> float:
        """
        Analyze text readability
        """
        try:
            # Use textstat for readability analysis
            flesch_score = textstat.flesch_reading_ease(text)
            return flesch_score / 100.0  # Normalize to 0-1
        except:
            return 0.5  # Default score
    
    def _analyze_sentiment(self, text: str) -> float:
        """
        Analyze text sentiment
        """
        try:
            if self.sentiment_analyzer:
                result = self.sentiment_analyzer(text)
                # Convert sentiment to 0-1 scale
                if result[0]['label'] == 'POSITIVE':
                    return result[0]['score']
                elif result[0]['label'] == 'NEGATIVE':
                    return 1 - result[0]['score']
                else:
                    return 0.5
            else:
                return 0.5  # Default neutral sentiment
        except:
            return 0.5  # Default score
    
    def _optimize_keywords(self, text: str, keywords: List[str]) -> str:
        """
        Optimize text for keywords
        """
        optimized_text = text
        
        # Add keywords naturally if not present
        for keyword in keywords:
            if keyword.lower() not in optimized_text.lower():
                # Add keyword in a natural way
                optimized_text += f" {keyword} is essential for success."
        
        return optimized_text
    
    def _calculate_performance_score(self, content: Dict, request: ContentRequest) -> float:
        """
        Calculate content performance score
        """
        score = 0.0
        
        # Readability score (0.3 weight)
        readability = content['metadata'].get('readability_score', 0.5)
        score += readability * 0.3
        
        # Sentiment score (0.3 weight)
        sentiment = content['metadata'].get('sentiment_score', 0.5)
        score += sentiment * 0.3
        
        # Keyword optimization (0.2 weight)
        keyword_score = self._calculate_keyword_score(content['body'], request.keywords)
        score += keyword_score * 0.2
        
        # Length optimization (0.2 weight)
        length_score = self._calculate_length_score(content['body'], request.length)
        score += length_score * 0.2
        
        return min(1.0, max(0.0, score))
    
    def _calculate_keyword_score(self, text: str, keywords: List[str]) -> float:
        """
        Calculate keyword optimization score
        """
        if not keywords:
            return 0.5
        
        text_lower = text.lower()
        keyword_count = sum(1 for keyword in keywords if keyword.lower() in text_lower)
        
        return keyword_count / len(keywords)
    
    def _calculate_length_score(self, text: str, target_length: str) -> float:
        """
        Calculate length optimization score
        """
        word_count = len(text.split())
        
        if target_length == 'short':
            target_words = 100
        elif target_length == 'medium':
            target_words = 300
        else:  # long
            target_words = 800
        
        # Calculate score based on how close to target length
        ratio = min(word_count / target_words, target_words / word_count)
        return ratio
    
    async def generate_content_variations(self, request: ContentRequest, num_variations: int = 3) -> List[GeneratedContent]:
        """
        Generate multiple content variations for A/B testing
        """
        variations = []
        
        for i in range(num_variations):
            # Create variation request
            variation_request = ContentRequest(
                content_type=request.content_type,
                target_audience=request.target_audience,
                product_info=request.product_info,
                tone=request.tone,
                length=request.length,
                keywords=request.keywords,
                call_to_action=request.call_to_action,
                affiliate_id=request.affiliate_id,
                campaign_id=request.campaign_id
            )
            
            # Generate content
            content = await self.generate_content(variation_request)
            content.content_id = f"{content.content_id}_variation_{i+1}"
            variations.append(content)
        
        return variations
    
    def get_content_performance(self, content_id: str) -> Dict:
        """
        Get content performance data
        """
        if content_id in self.content_performance:
            return self.content_performance[content_id]
        else:
            return {}
    
    def update_content_performance(self, content_id: str, performance_data: Dict):
        """
        Update content performance data
        """
        if content_id in self.content_performance:
            self.content_performance[content_id]['performance_data'] = performance_data
    
    def get_optimization_recommendations(self, content_id: str) -> List[str]:
        """
        Get optimization recommendations for content
        """
        recommendations = []
        
        if content_id in self.content_performance:
            content_data = self.content_performance[content_id]
            content = content_data['content']
            
            # Readability recommendations
            readability = content.metadata.get('readability_score', 0.5)
            if readability < 0.6:
                recommendations.append("Improve readability by using shorter sentences and simpler words")
            
            # Sentiment recommendations
            sentiment = content.metadata.get('sentiment_score', 0.5)
            if sentiment < 0.6:
                recommendations.append("Make content more positive and enthusiastic")
            
            # Keyword recommendations
            keyword_score = self._calculate_keyword_score(content.body, content_data['request'].keywords)
            if keyword_score < 0.5:
                recommendations.append("Include more target keywords naturally in the content")
            
            # Length recommendations
            length_score = self._calculate_length_score(content.body, content_data['request'].length)
            if length_score < 0.7:
                recommendations.append("Adjust content length to better match target length")
        
        return recommendations

# Example usage
async def main():
    """
    Example usage of AI Content Generator
    """
    # Initialize content generator
    generator = AIContentGenerator(openai_api_key="your-openai-api-key")
    
    # Create content request
    request = ContentRequest(
        content_type=ContentType.EMAIL,
        target_audience="Small Business Owners",
        product_info={
            'name': 'AI Marketing Pro',
            'niche': 'Digital Marketing',
            'benefit': '300% increase in leads',
            'testimonial': 'incredible results'
        },
        tone=ContentTone.PROFESSIONAL,
        length='medium',
        keywords=['AI', 'marketing', 'automation', 'leads'],
        call_to_action='Get Started Today!',
        affiliate_id='affiliate_1',
        campaign_id='campaign_1'
    )
    
    # Generate content
    content = await generator.generate_content(request)
    print(f"Generated content: {content.title}")
    print(f"Performance score: {content.performance_score}")
    
    # Generate variations
    variations = await generator.generate_content_variations(request, 3)
    print(f"Generated {len(variations)} variations")
    
    # Get optimization recommendations
    recommendations = generator.get_optimization_recommendations(content.content_id)
    print(f"Recommendations: {recommendations}")

if __name__ == "__main__":
    asyncio.run(main())






