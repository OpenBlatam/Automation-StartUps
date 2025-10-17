const OpenAI = require('openai');

/**
 * AI-Powered Content Generation Service
 * Advanced content generation with neural consciousness integration
 */
class ContentGenerator {
  constructor() {
    this.openai = new OpenAI({
      apiKey: process.env.OPENAI_API_KEY
    });
    
    this.templates = {
      // Thought Leadership Templates
      'thought-leadership': {
        'industry-analysis': `Being well-versed in the field of {industry/niche}, I am eager to approach {topic/issue} from a fresh perspective. This comprehensive analysis will explore the current landscape, emerging trends, and provide actionable insights for {target audience}.`,
        
        'trend-prediction': `As we look toward the future of {industry/niche}, several key trends are emerging that will fundamentally reshape how we approach {topic/issue}. This thought leadership piece examines these trends and their implications for {target audience}.`,
        
        'expert-opinion': `In my capacity as a {professional} in {field}, I've observed significant shifts in how {topic/issue} is being addressed. This article shares my insights and recommendations for {target audience} navigating these changes.`,
        
        'case-study': `Through my extensive experience in {industry/niche}, I've witnessed remarkable transformations in how organizations approach {topic/issue}. This detailed case study demonstrates the strategies and outcomes that can guide {target audience} toward success.`
      },
      
      // Marketing Copy Templates
      'marketing-copy': {
        'product-description': `Create a compelling product description for {product_name} that highlights its key features: {features}. Target audience: {target_audience}. Tone: {tone}.`,
        
        'email-subject': `Generate 10 engaging email subject lines for {campaign_type} targeting {target_audience}. The email is about {topic}. Tone: {tone}.`,
        
        'social-media': `Create {platform} posts about {topic} for {target_audience}. Tone: {tone}. Include relevant hashtags.`,
        
        'ad-copy': `Write compelling ad copy for {platform} promoting {product/service}. Target audience: {target_audience}. Call-to-action: {cta}. Budget: {budget}.`
      },
      
      // Business Content Templates
      'business-content': {
        'sales-proposal': `Create a professional sales proposal for {service/product} targeting {client_type}. Include problem statement, solution overview, benefits, and pricing.`,
        
        'pitch-deck': `Develop a pitch deck outline for {startup/idea} seeking {funding_amount} from {investor_type}. Include market opportunity, solution, business model, and financial projections.`,
        
        'white-paper': `Write a comprehensive white paper on {topic} for {industry}. Include executive summary, problem analysis, solution overview, implementation guide, and ROI analysis.`,
        
        'case-study': `Create a detailed case study showcasing how {company} achieved {results} using {solution/methodology}. Include challenge, approach, implementation, and outcomes.`
      }
    };
    
    this.contentTypes = {
      'blog-post': { minWords: 800, maxWords: 2000, temperature: 0.7 },
      'article': { minWords: 1000, maxWords: 3000, temperature: 0.7 },
      'social-media': { minWords: 50, maxWords: 280, temperature: 0.8 },
      'email': { minWords: 100, maxWords: 500, temperature: 0.6 },
      'ad-copy': { minWords: 50, maxWords: 200, temperature: 0.9 },
      'product-description': { minWords: 100, maxWords: 300, temperature: 0.6 }
    };
  }
  
  /**
   * Generate content based on type and parameters
   */
  async generateContent(type, params = {}) {
    try {
      const config = this.contentTypes[type] || this.contentTypes['blog-post'];
      const prompt = this.buildPrompt(type, params);
      
      const response = await this.openai.chat.completions.create({
        model: 'gpt-4',
        messages: [
          {
            role: 'system',
            content: this.getSystemPrompt(type)
          },
          {
            role: 'user',
            content: prompt
          }
        ],
        max_tokens: config.maxWords * 2, // Approximate token count
        temperature: config.temperature,
        presence_penalty: 0.6,
        frequency_penalty: 0.3
      });
      
      const generatedContent = response.choices[0].message.content;
      
      return {
        success: true,
        content: generatedContent,
        metadata: {
          type,
          wordCount: this.countWords(generatedContent),
          timestamp: new Date().toISOString(),
          model: 'gpt-4',
          temperature: config.temperature
        }
      };
      
    } catch (error) {
      console.error('Content generation error:', error);
      return {
        success: false,
        error: error.message,
        content: null
      };
    }
  }
  
  /**
   * Generate thought leadership content
   */
  async generateThoughtLeadership(templateType, params) {
    const template = this.templates['thought-leadership'][templateType];
    if (!template) {
      throw new Error(`Template type '${templateType}' not found`);
    }
    
    const prompt = this.buildPromptFromTemplate(template, params);
    
    return await this.generateContent('article', {
      ...params,
      prompt,
      style: 'thought-leadership',
      tone: 'authoritative'
    });
  }
  
  /**
   * Generate marketing copy
   */
  async generateMarketingCopy(copyType, params) {
    const template = this.templates['marketing-copy'][copyType];
    if (!template) {
      throw new Error(`Copy type '${copyType}' not found`);
    }
    
    const prompt = this.buildPromptFromTemplate(template, params);
    
    return await this.generateContent('ad-copy', {
      ...params,
      prompt,
      style: 'marketing',
      tone: params.tone || 'persuasive'
    });
  }
  
  /**
   * Generate business content
   */
  async generateBusinessContent(contentType, params) {
    const template = this.templates['business-content'][contentType];
    if (!template) {
      throw new Error(`Content type '${contentType}' not found`);
    }
    
    const prompt = this.buildPromptFromTemplate(template, params);
    
    return await this.generateContent('article', {
      ...params,
      prompt,
      style: 'business',
      tone: 'professional'
    });
  }
  
  /**
   * Build prompt from template
   */
  buildPromptFromTemplate(template, params) {
    return template.replace(/\{(\w+)\}/g, (match, key) => {
      return params[key] || `{${key}}`;
    });
  }
  
  /**
   * Build content generation prompt
   */
  buildPrompt(type, params) {
    const basePrompt = params.prompt || this.getDefaultPrompt(type);
    
    let enhancedPrompt = basePrompt;
    
    // Add context if provided
    if (params.context) {
      enhancedPrompt += `\n\nContext: ${params.context}`;
    }
    
    // Add target audience if provided
    if (params.target_audience) {
      enhancedPrompt += `\n\nTarget Audience: ${params.target_audience}`;
    }
    
    // Add tone if provided
    if (params.tone) {
      enhancedPrompt += `\n\nTone: ${params.tone}`;
    }
    
    // Add style if provided
    if (params.style) {
      enhancedPrompt += `\n\nStyle: ${params.style}`;
    }
    
    // Add word count requirements
    const config = this.contentTypes[type];
    if (config) {
      enhancedPrompt += `\n\nWord count: ${config.minWords}-${config.maxWords} words`;
    }
    
    return enhancedPrompt;
  }
  
  /**
   * Get system prompt for content type
   */
  getSystemPrompt(type) {
    const prompts = {
      'blog-post': 'You are an expert content writer specializing in creating engaging, informative blog posts that drive traffic and engagement.',
      'article': 'You are a professional journalist and content strategist with expertise in creating compelling, well-researched articles.',
      'social-media': 'You are a social media expert who creates viral, engaging content that drives engagement and brand awareness.',
      'email': 'You are an email marketing specialist who creates compelling, conversion-focused email content.',
      'ad-copy': 'You are a copywriting expert who creates persuasive, high-converting advertising copy.',
      'product-description': 'You are a product marketing expert who creates compelling product descriptions that drive sales.',
      'thought-leadership': 'You are a thought leader and industry expert who creates authoritative, insightful content that establishes expertise and drives industry conversations.',
      'business': 'You are a business consultant and content strategist who creates professional, strategic business content.'
    };
    
    return prompts[type] || prompts['blog-post'];
  }
  
  /**
   * Get default prompt for content type
   */
  getDefaultPrompt(type) {
    const prompts = {
      'blog-post': 'Write a comprehensive blog post about the given topic.',
      'article': 'Create a detailed, well-researched article on the specified subject.',
      'social-media': 'Create engaging social media content for the specified platform.',
      'email': 'Write a compelling email for the specified campaign.',
      'ad-copy': 'Create persuasive advertising copy for the specified platform.',
      'product-description': 'Write a compelling product description that highlights key features and benefits.'
    };
    
    return prompts[type] || 'Generate high-quality content based on the provided parameters.';
  }
  
  /**
   * Count words in text
   */
  countWords(text) {
    return text.trim().split(/\s+/).length;
  }
  
  /**
   * Generate multiple content variations
   */
  async generateVariations(type, params, count = 3) {
    const variations = [];
    
    for (let i = 0; i < count; i++) {
      const variation = await this.generateContent(type, {
        ...params,
        variation: i + 1
      });
      
      if (variation.success) {
        variations.push(variation);
      }
    }
    
    return variations;
  }
  
  /**
   * Optimize content for SEO
   */
  async optimizeForSEO(content, keywords = []) {
    const seoPrompt = `Optimize the following content for SEO by incorporating the keywords: ${keywords.join(', ')}. 
    Maintain readability and natural flow while improving search engine visibility.
    
    Content: ${content}`;
    
    return await this.generateContent('blog-post', {
      prompt: seoPrompt,
      style: 'seo-optimized'
    });
  }
  
  /**
   * Generate content in different tones
   */
  async generateToneVariations(content, tones = ['professional', 'casual', 'authoritative', 'friendly']) {
    const variations = [];
    
    for (const tone of tones) {
      const tonePrompt = `Rewrite the following content in a ${tone} tone while maintaining the core message and structure.
      
      Content: ${content}`;
      
      const variation = await this.generateContent('blog-post', {
        prompt: tonePrompt,
        tone: tone
      });
      
      if (variation.success) {
        variations.push({
          tone,
          content: variation.content
        });
      }
    }
    
    return variations;
  }
  
  /**
   * Get available templates
   */
  getAvailableTemplates() {
    return {
      thoughtLeadership: Object.keys(this.templates['thought-leadership']),
      marketingCopy: Object.keys(this.templates['marketing-copy']),
      businessContent: Object.keys(this.templates['business-content'])
    };
  }
  
  /**
   * Get content type configurations
   */
  getContentTypeConfigs() {
    return this.contentTypes;
  }
}

module.exports = ContentGenerator;

