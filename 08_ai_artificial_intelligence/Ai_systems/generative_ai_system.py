"""
Generative AI System for Ultimate Launch Planning System
Provides AI-powered content generation, natural language processing, and creative automation
"""

import json
import time
import asyncio
import threading
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Union, Callable
from dataclasses import dataclass, asdict
from collections import defaultdict, deque
import logging
from enum import Enum
import uuid
import re
import random
from transformers import pipeline, AutoTokenizer, AutoModelForCausalLM
import torch
import numpy as np

logger = logging.getLogger(__name__)

class ContentType(Enum):
    LAUNCH_PLAN = "launch_plan"
    MARKETING_COPY = "marketing_copy"
    TECHNICAL_SPEC = "technical_spec"
    RISK_ASSESSMENT = "risk_assessment"
    BUDGET_PROPOSAL = "budget_proposal"
    TIMELINE_ESTIMATE = "timeline_estimate"
    STAKEHOLDER_REPORT = "stakeholder_report"
    PRESENTATION_SLIDES = "presentation_slides"

class ContentQuality(Enum):
    DRAFT = "draft"
    REVIEW = "review"
    FINAL = "final"
    PREMIUM = "premium"

@dataclass
class GeneratedContent:
    id: str
    content_type: ContentType
    title: str
    content: str
    quality: ContentQuality
    confidence_score: float
    generation_time: float
    tokens_used: int
    metadata: Dict[str, Any]
    created_at: datetime
    updated_at: datetime
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "content_type": self.content_type.value,
            "title": self.title,
            "content": self.content,
            "quality": self.quality.value,
            "confidence_score": self.confidence_score,
            "generation_time": self.generation_time,
            "tokens_used": self.tokens_used,
            "metadata": self.metadata,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat()
        }

@dataclass
class ContentTemplate:
    id: str
    name: str
    description: str
    content_type: ContentType
    template: str
    variables: List[str]
    quality_level: ContentQuality
    created_at: datetime
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "content_type": self.content_type.value,
            "template": self.template,
            "variables": self.variables,
            "quality_level": self.quality_level.value,
            "created_at": self.created_at.isoformat()
        }

class GenerativeAIEngine:
    """Advanced Generative AI engine for content creation"""
    
    def __init__(self):
        self.models = {}
        self.templates: Dict[str, ContentTemplate] = {}
        self.generated_content: Dict[str, GeneratedContent] = {}
        self.content_history: deque = deque(maxlen=10000)
        self.lock = threading.RLock()
        
        # Initialize AI models
        self._initialize_models()
        
        # Load default templates
        self._load_default_templates()
        
        logger.info("Generative AI Engine initialized")
    
    def _initialize_models(self):
        """Initialize AI models for different content types"""
        try:
            # Text generation model
            self.models['text_generator'] = pipeline(
                "text-generation",
                model="gpt2",
                device=0 if torch.cuda.is_available() else -1
            )
            
            # Sentiment analysis model
            self.models['sentiment_analyzer'] = pipeline(
                "sentiment-analysis",
                model="cardiffnlp/twitter-roberta-base-sentiment-latest"
            )
            
            # Text summarization model
            self.models['summarizer'] = pipeline(
                "summarization",
                model="facebook/bart-large-cnn"
            )
            
            logger.info("AI models loaded successfully")
            
        except Exception as e:
            logger.warning(f"Could not load AI models: {e}. Using fallback methods.")
            self.models = {}
    
    def _load_default_templates(self):
        """Load default content templates"""
        templates = [
            ContentTemplate(
                id="launch_plan_template",
                name="Launch Plan Template",
                description="Comprehensive launch planning template",
                content_type=ContentType.LAUNCH_PLAN,
                template="""
# {product_name} Launch Plan

## Executive Summary
{executive_summary}

## Market Analysis
- Target Market: {target_market}
- Market Size: {market_size}
- Competition: {competition_level}

## Launch Strategy
- Launch Date: {launch_date}
- Budget: ${budget}
- Team Size: {team_size}

## Key Milestones
{key_milestones}

## Risk Assessment
{risk_factors}

## Success Metrics
{success_metrics}
                """,
                variables=["product_name", "executive_summary", "target_market", "market_size", 
                          "competition_level", "launch_date", "budget", "team_size", 
                          "key_milestones", "risk_factors", "success_metrics"],
                quality_level=ContentQuality.FINAL,
                created_at=datetime.now()
            ),
            
            ContentTemplate(
                id="marketing_copy_template",
                name="Marketing Copy Template",
                description="AI-generated marketing content",
                content_type=ContentType.MARKETING_COPY,
                template="""
# {product_name} - {tagline}

## Product Description
{product_description}

## Key Benefits
{key_benefits}

## Target Audience
{target_audience}

## Call to Action
{call_to_action}

## Social Media Posts
{social_media_posts}
                """,
                variables=["product_name", "tagline", "product_description", "key_benefits",
                          "target_audience", "call_to_action", "social_media_posts"],
                quality_level=ContentQuality.REVIEW,
                created_at=datetime.now()
            ),
            
            ContentTemplate(
                id="risk_assessment_template",
                name="Risk Assessment Template",
                description="Comprehensive risk analysis template",
                content_type=ContentType.RISK_ASSESSMENT,
                template="""
# Risk Assessment Report

## Executive Summary
{executive_summary}

## Risk Categories

### Technical Risks
{technical_risks}

### Market Risks
{market_risks}

### Financial Risks
{financial_risks}

### Operational Risks
{operational_risks}

## Risk Mitigation Strategies
{mitigation_strategies}

## Risk Monitoring Plan
{monitoring_plan}
                """,
                variables=["executive_summary", "technical_risks", "market_risks", 
                          "financial_risks", "operational_risks", "mitigation_strategies", "monitoring_plan"],
                quality_level=ContentQuality.FINAL,
                created_at=datetime.now()
            )
        ]
        
        for template in templates:
            self.templates[template.id] = template
        
        logger.info(f"Loaded {len(templates)} default templates")
    
    def generate_content(self, content_type: ContentType, prompt: str, 
                        context: Dict[str, Any] = None, quality: ContentQuality = ContentQuality.DRAFT) -> GeneratedContent:
        """Generate content using AI"""
        start_time = time.time()
        
        try:
            if content_type in [ContentType.LAUNCH_PLAN, ContentType.MARKETING_COPY, ContentType.RISK_ASSESSMENT]:
                content = self._generate_structured_content(content_type, prompt, context, quality)
            else:
                content = self._generate_freeform_content(content_type, prompt, context, quality)
            
            generation_time = time.time() - start_time
            
            # Create content object
            generated_content = GeneratedContent(
                id=str(uuid.uuid4()),
                content_type=content_type,
                title=self._extract_title(content),
                content=content,
                quality=quality,
                confidence_score=self._calculate_confidence(content, quality),
                generation_time=generation_time,
                tokens_used=self._estimate_tokens(content),
                metadata=context or {},
                created_at=datetime.now(),
                updated_at=datetime.now()
            )
            
            with self.lock:
                self.generated_content[generated_content.id] = generated_content
                self.content_history.append(generated_content)
            
            logger.info(f"Generated {content_type.value} content in {generation_time:.2f}s")
            return generated_content
            
        except Exception as e:
            logger.error(f"Error generating content: {e}")
            # Return fallback content
            return self._generate_fallback_content(content_type, prompt, quality)
    
    def _generate_structured_content(self, content_type: ContentType, prompt: str, 
                                   context: Dict[str, Any], quality: ContentQuality) -> str:
        """Generate structured content using templates"""
        template_id = f"{content_type.value}_template"
        
        if template_id in self.templates:
            template = self.templates[template_id]
            content = template.template
            
            # Fill in variables
            for variable in template.variables:
                value = context.get(variable, self._generate_variable_content(variable, context))
                content = content.replace(f"{{{variable}}}", str(value))
            
            # Enhance with AI if available
            if self.models.get('text_generator') and quality in [ContentQuality.REVIEW, ContentQuality.FINAL, ContentQuality.PREMIUM]:
                content = self._enhance_content_with_ai(content, quality)
            
            return content
        else:
            return self._generate_freeform_content(content_type, prompt, context, quality)
    
    def _generate_freeform_content(self, content_type: ContentType, prompt: str, 
                                 context: Dict[str, Any], quality: ContentQuality) -> str:
        """Generate freeform content using AI models"""
        if self.models.get('text_generator'):
            try:
                # Prepare prompt
                enhanced_prompt = self._prepare_prompt(content_type, prompt, context)
                
                # Generate content
                result = self.models['text_generator'](
                    enhanced_prompt,
                    max_length=500 if quality == ContentQuality.DRAFT else 1000,
                    num_return_sequences=1,
                    temperature=0.7 if quality == ContentQuality.DRAFT else 0.5,
                    do_sample=True,
                    pad_token_id=50256
                )
                
                generated_text = result[0]['generated_text']
                # Remove the original prompt from the generated text
                content = generated_text[len(enhanced_prompt):].strip()
                
                return content
                
            except Exception as e:
                logger.error(f"Error in AI generation: {e}")
                return self._generate_fallback_content(content_type, prompt, quality)
        else:
            return self._generate_fallback_content(content_type, prompt, quality)
    
    def _enhance_content_with_ai(self, content: str, quality: ContentQuality) -> str:
        """Enhance content using AI models"""
        try:
            if quality == ContentQuality.PREMIUM and self.models.get('text_generator'):
                # Premium enhancement
                enhanced_prompt = f"Enhance the following content to be more professional and engaging:\n\n{content}\n\nEnhanced version:"
                
                result = self.models['text_generator'](
                    enhanced_prompt,
                    max_length=len(content) + 200,
                    temperature=0.3,
                    do_sample=True
                )
                
                enhanced_content = result[0]['generated_text']
                return enhanced_content[len(enhanced_prompt):].strip()
            
            return content
            
        except Exception as e:
            logger.error(f"Error enhancing content: {e}")
            return content
    
    def _generate_variable_content(self, variable: str, context: Dict[str, Any]) -> str:
        """Generate content for template variables"""
        variable_generators = {
            "executive_summary": lambda: self._generate_executive_summary(context),
            "key_milestones": lambda: self._generate_milestones(context),
            "risk_factors": lambda: self._generate_risk_factors(context),
            "success_metrics": lambda: self._generate_success_metrics(context),
            "product_description": lambda: self._generate_product_description(context),
            "key_benefits": lambda: self._generate_key_benefits(context),
            "target_audience": lambda: self._generate_target_audience(context),
            "call_to_action": lambda: self._generate_call_to_action(context),
            "social_media_posts": lambda: self._generate_social_media_posts(context),
            "technical_risks": lambda: self._generate_technical_risks(context),
            "market_risks": lambda: self._generate_market_risks(context),
            "financial_risks": lambda: self._generate_financial_risks(context),
            "operational_risks": lambda: self._generate_operational_risks(context),
            "mitigation_strategies": lambda: self._generate_mitigation_strategies(context),
            "monitoring_plan": lambda: self._generate_monitoring_plan(context)
        }
        
        generator = variable_generators.get(variable)
        if generator:
            return generator()
        else:
            return f"[{variable.replace('_', ' ').title()}]"
    
    def _generate_executive_summary(self, context: Dict[str, Any]) -> str:
        """Generate executive summary"""
        product_name = context.get('product_name', 'the product')
        budget = context.get('budget', 'TBD')
        timeline = context.get('timeline_days', 'TBD')
        
        return f"""
This launch plan outlines the strategy for {product_name}, with a budget of ${budget} and a timeline of {timeline} days. 
The plan focuses on market penetration, risk mitigation, and achieving key success metrics through 
strategic execution and continuous monitoring.
        """.strip()
    
    def _generate_milestones(self, context: Dict[str, Any]) -> str:
        """Generate key milestones"""
        milestones = [
            "Phase 1: Pre-launch preparation and market research",
            "Phase 2: Product development and testing",
            "Phase 3: Marketing campaign launch",
            "Phase 4: Product launch and initial rollout",
            "Phase 5: Post-launch monitoring and optimization"
        ]
        
        return "\n".join([f"- {milestone}" for milestone in milestones])
    
    def _generate_risk_factors(self, context: Dict[str, Any]) -> str:
        """Generate risk factors"""
        risks = [
            "Market competition and saturation",
            "Technical challenges and development delays",
            "Budget overruns and resource constraints",
            "Regulatory compliance and legal issues",
            "Team capacity and skill gaps"
        ]
        
        return "\n".join([f"- {risk}" for risk in risks])
    
    def _generate_success_metrics(self, context: Dict[str, Any]) -> str:
        """Generate success metrics"""
        metrics = [
            "User acquisition and engagement rates",
            "Revenue targets and growth metrics",
            "Market share and competitive positioning",
            "Customer satisfaction and retention",
            "Operational efficiency and cost optimization"
        ]
        
        return "\n".join([f"- {metric}" for metric in metrics])
    
    def _generate_product_description(self, context: Dict[str, Any]) -> str:
        """Generate product description"""
        product_name = context.get('product_name', 'our innovative product')
        return f"{product_name} is a cutting-edge solution designed to address key market needs and deliver exceptional value to our target customers."
    
    def _generate_key_benefits(self, context: Dict[str, Any]) -> str:
        """Generate key benefits"""
        benefits = [
            "Improved efficiency and productivity",
            "Cost reduction and ROI optimization",
            "Enhanced user experience and satisfaction",
            "Scalable and flexible architecture",
            "Comprehensive support and maintenance"
        ]
        
        return "\n".join([f"- {benefit}" for benefit in benefits])
    
    def _generate_target_audience(self, context: Dict[str, Any]) -> str:
        """Generate target audience description"""
        return "Our target audience includes forward-thinking businesses and professionals seeking innovative solutions to enhance their operations and achieve sustainable growth."
    
    def _generate_call_to_action(self, context: Dict[str, Any]) -> str:
        """Generate call to action"""
        return "Ready to transform your business? Contact us today to learn more about how our solution can drive your success."
    
    def _generate_social_media_posts(self, context: Dict[str, Any]) -> str:
        """Generate social media posts"""
        posts = [
            "🚀 Exciting news! We're launching something amazing that will revolutionize the industry. Stay tuned!",
            "💡 Innovation meets excellence. Our new solution is designed to deliver exceptional results.",
            "🎯 Ready to take your business to the next level? Our launch is just around the corner!"
        ]
        
        return "\n\n".join(posts)
    
    def _generate_technical_risks(self, context: Dict[str, Any]) -> str:
        """Generate technical risks"""
        risks = [
            "System scalability and performance limitations",
            "Integration challenges with existing systems",
            "Data security and privacy concerns",
            "Technology stack compatibility issues",
            "Development timeline and resource constraints"
        ]
        
        return "\n".join([f"- {risk}" for risk in risks])
    
    def _generate_market_risks(self, context: Dict[str, Any]) -> str:
        """Generate market risks"""
        risks = [
            "Market saturation and competitive pressure",
            "Economic downturn and reduced spending",
            "Changing customer preferences and demands",
            "Regulatory changes and compliance requirements",
            "Supply chain disruptions and vendor dependencies"
        ]
        
        return "\n".join([f"- {risk}" for risk in risks])
    
    def _generate_financial_risks(self, context: Dict[str, Any]) -> str:
        """Generate financial risks"""
        risks = [
            "Budget overruns and cost escalation",
            "Revenue projections and market adoption",
            "Currency fluctuations and exchange rates",
            "Funding availability and investor confidence",
            "Cash flow management and liquidity"
        ]
        
        return "\n".join([f"- {risk}" for risk in risks])
    
    def _generate_operational_risks(self, context: Dict[str, Any]) -> str:
        """Generate operational risks"""
        risks = [
            "Team capacity and skill availability",
            "Process inefficiencies and bottlenecks",
            "Quality control and delivery standards",
            "Vendor management and dependencies",
            "Change management and adoption challenges"
        ]
        
        return "\n".join([f"- {risk}" for risk in risks])
    
    def _generate_mitigation_strategies(self, context: Dict[str, Any]) -> str:
        """Generate mitigation strategies"""
        strategies = [
            "Implement comprehensive risk monitoring and early warning systems",
            "Develop contingency plans and alternative approaches",
            "Establish strong vendor relationships and backup options",
            "Invest in team training and skill development",
            "Create robust quality assurance and testing processes"
        ]
        
        return "\n".join([f"- {strategy}" for strategy in strategies])
    
    def _generate_monitoring_plan(self, context: Dict[str, Any]) -> str:
        """Generate monitoring plan"""
        plan = [
            "Weekly risk assessment and status reviews",
            "Monthly performance metrics and KPI tracking",
            "Quarterly strategic reviews and adjustments",
            "Continuous stakeholder communication and feedback",
            "Regular team meetings and progress updates"
        ]
        
        return "\n".join([f"- {item}" for item in plan])
    
    def _prepare_prompt(self, content_type: ContentType, prompt: str, context: Dict[str, Any]) -> str:
        """Prepare prompt for AI generation"""
        base_prompts = {
            ContentType.LAUNCH_PLAN: "Create a comprehensive launch plan for",
            ContentType.MARKETING_COPY: "Write compelling marketing copy for",
            ContentType.TECHNICAL_SPEC: "Develop technical specifications for",
            ContentType.RISK_ASSESSMENT: "Conduct a risk assessment for",
            ContentType.BUDGET_PROPOSAL: "Create a budget proposal for",
            ContentType.TIMELINE_ESTIMATE: "Estimate timeline for",
            ContentType.STAKEHOLDER_REPORT: "Write a stakeholder report for",
            ContentType.PRESENTATION_SLIDES: "Create presentation slides for"
        }
        
        base_prompt = base_prompts.get(content_type, "Generate content for")
        context_info = f" Context: {json.dumps(context)}" if context else ""
        
        return f"{base_prompt} {prompt}.{context_info}"
    
    def _extract_title(self, content: str) -> str:
        """Extract title from content"""
        lines = content.split('\n')
        for line in lines:
            line = line.strip()
            if line.startswith('#') and len(line) > 1:
                return line[1:].strip()
            elif line and not line.startswith('#'):
                return line[:50] + "..." if len(line) > 50 else line
        
        return "Generated Content"
    
    def _calculate_confidence(self, content: str, quality: ContentQuality) -> float:
        """Calculate confidence score for generated content"""
        base_confidence = {
            ContentQuality.DRAFT: 0.6,
            ContentQuality.REVIEW: 0.75,
            ContentQuality.FINAL: 0.85,
            ContentQuality.PREMIUM: 0.95
        }
        
        confidence = base_confidence.get(quality, 0.7)
        
        # Adjust based on content length and structure
        if len(content) > 500:
            confidence += 0.05
        if content.count('\n') > 5:
            confidence += 0.05
        if any(keyword in content.lower() for keyword in ['strategy', 'analysis', 'recommendation']):
            confidence += 0.05
        
        return min(1.0, confidence)
    
    def _estimate_tokens(self, content: str) -> int:
        """Estimate token count for content"""
        # Rough estimation: 1 token ≈ 4 characters
        return len(content) // 4
    
    def _generate_fallback_content(self, content_type: ContentType, prompt: str, quality: ContentQuality) -> GeneratedContent:
        """Generate fallback content when AI models are not available"""
        fallback_content = f"""
# {content_type.value.replace('_', ' ').title()}

## Overview
This is a generated {content_type.value} for: {prompt}

## Key Points
- Generated using fallback method
- Quality level: {quality.value}
- Generated at: {datetime.now().isoformat()}

## Content
This content has been generated as a fallback when AI models are not available. 
Please review and enhance as needed for your specific requirements.

## Next Steps
1. Review the generated content
2. Customize based on your specific needs
3. Enhance with additional details
4. Validate with stakeholders
        """.strip()
        
        return GeneratedContent(
            id=str(uuid.uuid4()),
            content_type=content_type,
            title=f"{content_type.value.replace('_', ' ').title()} - {prompt[:30]}",
            content=fallback_content,
            quality=quality,
            confidence_score=0.5,
            generation_time=0.1,
            tokens_used=self._estimate_tokens(fallback_content),
            metadata={"fallback": True, "prompt": prompt},
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
    
    def analyze_sentiment(self, text: str) -> Dict[str, Any]:
        """Analyze sentiment of text"""
        if self.models.get('sentiment_analyzer'):
            try:
                result = self.models['sentiment_analyzer'](text)
                return {
                    "sentiment": result[0]['label'],
                    "confidence": result[0]['score'],
                    "analysis_time": time.time()
                }
            except Exception as e:
                logger.error(f"Error in sentiment analysis: {e}")
        
        # Fallback sentiment analysis
        positive_words = ['good', 'great', 'excellent', 'amazing', 'fantastic', 'success', 'win']
        negative_words = ['bad', 'terrible', 'awful', 'failure', 'problem', 'issue', 'risk']
        
        text_lower = text.lower()
        positive_count = sum(1 for word in positive_words if word in text_lower)
        negative_count = sum(1 for word in negative_words if word in text_lower)
        
        if positive_count > negative_count:
            sentiment = "POSITIVE"
            confidence = 0.6 + (positive_count - negative_count) * 0.1
        elif negative_count > positive_count:
            sentiment = "NEGATIVE"
            confidence = 0.6 + (negative_count - positive_count) * 0.1
        else:
            sentiment = "NEUTRAL"
            confidence = 0.5
        
        return {
            "sentiment": sentiment,
            "confidence": min(1.0, confidence),
            "analysis_time": time.time()
        }
    
    def summarize_content(self, content: str, max_length: int = 150) -> str:
        """Summarize content using AI"""
        if self.models.get('summarizer') and len(content) > 100:
            try:
                result = self.models['summarizer'](
                    content,
                    max_length=max_length,
                    min_length=50,
                    do_sample=False
                )
                return result[0]['summary_text']
            except Exception as e:
                logger.error(f"Error in summarization: {e}")
        
        # Fallback summarization
        sentences = content.split('.')
        if len(sentences) <= 3:
            return content
        
        # Take first few sentences as summary
        summary_sentences = sentences[:2]
        return '. '.join(summary_sentences) + '.'
    
    def get_content_by_type(self, content_type: ContentType, limit: int = 10) -> List[GeneratedContent]:
        """Get generated content by type"""
        with self.lock:
            content_list = [content for content in self.generated_content.values() 
                          if content.content_type == content_type]
            return sorted(content_list, key=lambda x: x.created_at, reverse=True)[:limit]
    
    def get_content_statistics(self) -> Dict[str, Any]:
        """Get content generation statistics"""
        with self.lock:
            total_content = len(self.generated_content)
            content_by_type = defaultdict(int)
            content_by_quality = defaultdict(int)
            
            for content in self.generated_content.values():
                content_by_type[content.content_type.value] += 1
                content_by_quality[content.quality.value] += 1
            
            avg_confidence = sum(content.confidence_score for content in self.generated_content.values()) / total_content if total_content > 0 else 0
            avg_generation_time = sum(content.generation_time for content in self.generated_content.values()) / total_content if total_content > 0 else 0
            
            return {
                "total_content": total_content,
                "content_by_type": dict(content_by_type),
                "content_by_quality": dict(content_by_quality),
                "average_confidence": avg_confidence,
                "average_generation_time": avg_generation_time,
                "models_available": len(self.models),
                "templates_available": len(self.templates)
            }

# Global generative AI instance
_generative_ai = None

def get_generative_ai() -> GenerativeAIEngine:
    """Get global generative AI instance"""
    global _generative_ai
    if _generative_ai is None:
        _generative_ai = GenerativeAIEngine()
    return _generative_ai

# Example usage
if __name__ == "__main__":
    # Initialize generative AI
    gen_ai = get_generative_ai()
    
    # Generate launch plan
    context = {
        "product_name": "AI-Powered Analytics Platform",
        "budget": 500000,
        "team_size": 15,
        "timeline_days": 120,
        "target_market": "Enterprise Analytics",
        "market_size": 10000000,
        "competition_level": "High"
    }
    
    launch_plan = gen_ai.generate_content(
        ContentType.LAUNCH_PLAN,
        "AI-Powered Analytics Platform",
        context,
        ContentQuality.FINAL
    )
    
    print("Generated Launch Plan:")
    print(f"Title: {launch_plan.title}")
    print(f"Quality: {launch_plan.quality.value}")
    print(f"Confidence: {launch_plan.confidence_score:.2f}")
    print(f"Generation Time: {launch_plan.generation_time:.2f}s")
    print("\nContent Preview:")
    print(launch_plan.content[:500] + "...")
    
    # Generate marketing copy
    marketing_copy = gen_ai.generate_content(
        ContentType.MARKETING_COPY,
        "AI-Powered Analytics Platform",
        context,
        ContentQuality.REVIEW
    )
    
    print(f"\nGenerated Marketing Copy:")
    print(f"Title: {marketing_copy.title}")
    print(f"Confidence: {marketing_copy.confidence_score:.2f}")
    
    # Analyze sentiment
    sentiment = gen_ai.analyze_sentiment("This is an amazing product that will revolutionize the industry!")
    print(f"\nSentiment Analysis: {sentiment['sentiment']} (confidence: {sentiment['confidence']:.2f})")
    
    # Get statistics
    stats = gen_ai.get_content_statistics()
    print(f"\nContent Statistics:")
    print(f"Total Content: {stats['total_content']}")
    print(f"Models Available: {stats['models_available']}")
    print(f"Templates Available: {stats['templates_available']}")








