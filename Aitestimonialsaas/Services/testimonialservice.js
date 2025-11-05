const OpenAI = require('openai');
const Anthropic = require('@anthropic-ai/sdk');
const { GoogleGenerativeAI } = require('@google/generative-ai');
const Testimonial = require('../models/Testimonial');
const User = require('../models/User');
const Template = require('../models/Template');
const Analytics = require('../models/Analytics');
const { v4: uuidv4 } = require('uuid');
const moment = require('moment');

class TestimonialService {
  constructor() {
    this.openai = new OpenAI({
      apiKey: process.env.OPENAI_API_KEY
    });
    
    this.anthropic = new Anthropic({
      apiKey: process.env.ANTHROPIC_API_KEY
    });
    
    this.googleAI = new GoogleGenerativeAI(process.env.GOOGLE_AI_API_KEY);
    
    // Predefined testimonial prompts based on user requirements
    this.testimonialPrompts = {
      distinctiveQualities: {
        prompt: "Could you kindly produce a testimonial regarding the distinctive qualities that set {product/service} apart as an unparalleled solution within the realm of the commerce industry?",
        category: "Product Differentiation",
        useCase: "Highlighting unique value propositions",
        variables: ['product/service', 'industry', 'target_audience']
      },
      recommendation: {
        prompt: "Can you please provide a testimonial explaining your reasons for recommending {product/service} to others?",
        category: "Social Proof",
        useCase: "Building trust and credibility",
        variables: ['product/service', 'benefits', 'target_audience']
      },
      specificSituation: {
        prompt: "Can you provide me with a testimonial that highlights a particular situation in which {product/service} proved to be extremely useful?",
        category: "Use Case Stories",
        useCase: "Demonstrating practical benefits",
        variables: ['product/service', 'situation', 'outcome']
      },
      investmentWorth: {
        prompt: "Are you able to provide me with a testimonial expressing your belief on whether {product/service} warrants the investment?",
        category: "ROI Focus",
        useCase: "Justifying purchase decisions",
        variables: ['product/service', 'investment', 'roi']
      },
      efficiencyImprovement: {
        prompt: "Can you provide me with a testimonial that highlights how {product/service} has made your day-to-day tasks more efficient?",
        category: "Productivity",
        useCase: "Showing operational benefits",
        variables: ['product/service', 'tasks', 'efficiency_gains']
      }
    };
  }

  async generateTestimonial(userId, testimonialData) {
    try {
      const {
        templateType,
        productName,
        productCategory,
        targetAudience,
        keyBenefits,
        useCase,
        industry,
        tone = 'professional',
        length = 'medium',
        model = 'gpt-4',
        customPrompt,
        additionalContext
      } = testimonialData;

      // Get user's brand profile for personalization
      const user = await User.findById(userId);
      const brandProfile = user.brandProfile || {};

      // Select the appropriate prompt template
      const promptTemplate = customPrompt || this.testimonialPrompts[templateType];
      if (!promptTemplate) {
        throw new Error('Invalid template type');
      }

      // Build the context for AI generation
      const context = this.buildGenerationContext({
        promptTemplate,
        productName,
        productCategory,
        targetAudience,
        keyBenefits,
        useCase,
        industry,
        tone,
        length,
        brandProfile,
        additionalContext
      });

      // Generate testimonial using selected AI model
      const generatedContent = await this.generateWithAI(model, context);

      // Create testimonial record
      const testimonial = new Testimonial({
        id: uuidv4(),
        userId,
        templateType,
        productName,
        productCategory,
        targetAudience,
        keyBenefits,
        useCase,
        industry,
        tone,
        length,
        model,
        content: generatedContent.primary,
        alternatives: generatedContent.alternatives,
        metadata: {
          prompt: context.finalPrompt,
          tokensUsed: generatedContent.tokensUsed,
          generationTime: generatedContent.generationTime,
          qualityScore: generatedContent.qualityScore
        },
        status: 'generated',
        createdAt: new Date()
      });

      await testimonial.save();

      // Update user's usage statistics
      await this.updateUserUsage(userId, testimonial);

      // Track analytics
      await this.trackGeneration(userId, testimonial);

      return testimonial;
    } catch (error) {
      console.error('Error generating testimonial:', error);
      throw new Error(`Failed to generate testimonial: ${error.message}`);
    }
  }

  async generateBatchTestimonials(userId, requests, options = {}) {
    const results = [];
    const errors = [];

    for (let i = 0; i < requests.length; i++) {
      try {
        const testimonial = await this.generateTestimonial(userId, requests[i]);
        results.push(testimonial);
        
        // Add delay between requests to avoid rate limiting
        if (i < requests.length - 1) {
          await new Promise(resolve => setTimeout(resolve, 1000));
        }
      } catch (error) {
        errors.push({
          index: i,
          request: requests[i],
          error: error.message
        });
      }
    }

    return {
      testimonials: results,
      errors,
      summary: {
        total: requests.length,
        successful: results.length,
        failed: errors.length
      }
    };
  }

  buildGenerationContext(data) {
    const {
      promptTemplate,
      productName,
      productCategory,
      targetAudience,
      keyBenefits,
      useCase,
      industry,
      tone,
      length,
      brandProfile,
      additionalContext
    } = data;

    // Replace variables in the prompt template
    let finalPrompt = promptTemplate.prompt;
    finalPrompt = finalPrompt.replace(/{product\/service}/g, productName);
    finalPrompt = finalPrompt.replace(/{industry}/g, industry || 'business');
    finalPrompt = finalPrompt.replace(/{target_audience}/g, targetAudience || 'customers');

    // Add context and instructions
    const instructions = this.buildInstructions(tone, length, brandProfile, additionalContext);
    finalPrompt = `${finalPrompt}\n\n${instructions}`;

    return {
      finalPrompt,
      context: {
        productName,
        productCategory,
        targetAudience,
        keyBenefits,
        useCase,
        industry,
        tone,
        length,
        brandProfile
      }
    };
  }

  buildInstructions(tone, length, brandProfile, additionalContext) {
    const toneInstructions = {
      professional: "Write in a professional, business-appropriate tone.",
      casual: "Write in a friendly, conversational tone.",
      technical: "Write in a technical, detailed tone with specific terminology.",
      emotional: "Write in an emotional, personal tone that connects with readers."
    };

    const lengthInstructions = {
      short: "Keep the testimonial concise, around 50-75 words.",
      medium: "Write a detailed testimonial, around 150-200 words.",
      long: "Write a comprehensive testimonial, around 300+ words with specific details."
    };

    let instructions = [
      toneInstructions[tone] || toneInstructions.professional,
      lengthInstructions[length] || lengthInstructions.medium
    ];

    if (brandProfile.voice) {
      instructions.push(`Match this brand voice: ${brandProfile.voice}`);
    }

    if (brandProfile.keywords && brandProfile.keywords.length > 0) {
      instructions.push(`Include these keywords naturally: ${brandProfile.keywords.join(', ')}`);
    }

    if (additionalContext) {
      instructions.push(`Additional context: ${additionalContext}`);
    }

    return instructions.join(' ');
  }

  async generateWithAI(model, context) {
    const startTime = Date.now();
    let result;

    try {
      switch (model) {
        case 'gpt-4':
          result = await this.generateWithOpenAI(context);
          break;
        case 'claude-3':
          result = await this.generateWithClaude(context);
          break;
        case 'gemini-pro':
          result = await this.generateWithGemini(context);
          break;
        default:
          throw new Error(`Unsupported model: ${model}`);
      }

      const generationTime = Date.now() - startTime;
      
      return {
        ...result,
        generationTime,
        qualityScore: this.calculateQualityScore(result.primary, context)
      };
    } catch (error) {
      console.error(`Error generating with ${model}:`, error);
      throw new Error(`AI generation failed: ${error.message}`);
    }
  }

  async generateWithOpenAI(context) {
    try {
      const response = await this.openai.chat.completions.create({
        model: "gpt-4",
        messages: [
          {
            role: "system",
            content: "You are an expert copywriter specializing in creating compelling, authentic testimonials. Generate testimonials that feel genuine and persuasive."
          },
          {
            role: "user",
            content: context.finalPrompt
          }
        ],
        max_tokens: 500,
        temperature: 0.7,
        n: 3 // Generate 3 variations
      });

      const alternatives = response.choices.slice(1).map(choice => choice.message.content);
      
      return {
        primary: response.choices[0].message.content,
        alternatives,
        tokensUsed: response.usage.total_tokens
      };
    } catch (error) {
      throw new Error(`OpenAI generation failed: ${error.message}`);
    }
  }

  async generateWithClaude(context) {
    try {
      const response = await this.anthropic.messages.create({
        model: "claude-3-sonnet-20240229",
        max_tokens: 500,
        temperature: 0.7,
        messages: [
          {
            role: "user",
            content: `You are an expert copywriter specializing in creating compelling, authentic testimonials. Generate testimonials that feel genuine and persuasive.\n\n${context.finalPrompt}`
          }
        ]
      });

      return {
        primary: response.content[0].text,
        alternatives: [], // Claude doesn't support multiple completions in one request
        tokensUsed: response.usage.input_tokens + response.usage.output_tokens
      };
    } catch (error) {
      throw new Error(`Claude generation failed: ${error.message}`);
    }
  }

  async generateWithGemini(context) {
    try {
      const model = this.googleAI.getGenerativeModel({ model: "gemini-pro" });
      
      const result = await model.generateContent({
        contents: [{
          parts: [{
            text: `You are an expert copywriter specializing in creating compelling, authentic testimonials. Generate testimonials that feel genuine and persuasive.\n\n${context.finalPrompt}`
          }]
        }]
      });

      const response = await result.response;
      const text = response.text();

      return {
        primary: text,
        alternatives: [],
        tokensUsed: 0 // Gemini doesn't provide token count in the same way
      };
    } catch (error) {
      throw new Error(`Gemini generation failed: ${error.message}`);
    }
  }

  calculateQualityScore(content, context) {
    // Simple quality scoring based on content characteristics
    let score = 0;
    
    // Length appropriateness
    const wordCount = content.split(' ').length;
    if (context.context.length === 'short' && wordCount >= 40 && wordCount <= 80) score += 25;
    else if (context.context.length === 'medium' && wordCount >= 120 && wordCount <= 250) score += 25;
    else if (context.context.length === 'long' && wordCount >= 250) score += 25;
    
    // Emotional indicators
    const emotionalWords = ['amazing', 'incredible', 'fantastic', 'outstanding', 'excellent', 'love', 'impressed'];
    const hasEmotionalWords = emotionalWords.some(word => content.toLowerCase().includes(word));
    if (hasEmotionalWords) score += 20;
    
    // Specificity
    const hasNumbers = /\d+/.test(content);
    const hasSpecificDetails = content.includes(context.context.productName);
    if (hasNumbers || hasSpecificDetails) score += 20;
    
    // Readability
    const sentences = content.split(/[.!?]+/).filter(s => s.trim().length > 0);
    const avgSentenceLength = content.split(' ').length / sentences.length;
    if (avgSentenceLength >= 10 && avgSentenceLength <= 20) score += 15;
    
    // Call to action or recommendation
    const hasRecommendation = /recommend|suggest|would.*use|definitely|absolutely/.test(content.toLowerCase());
    if (hasRecommendation) score += 20;
    
    return Math.min(score, 100);
  }

  async getUserTestimonials(userId, options = {}) {
    const { page = 1, limit = 10, category, status } = options;
    const skip = (page - 1) * limit;
    
    const query = { userId };
    if (category) query.templateType = category;
    if (status) query.status = status;
    
    const testimonials = await Testimonial.find(query)
      .sort({ createdAt: -1 })
      .skip(skip)
      .limit(limit)
      .lean();
    
    const total = await Testimonial.countDocuments(query);
    
    return {
      testimonials,
      total,
      page,
      limit,
      totalPages: Math.ceil(total / limit)
    };
  }

  async getTestimonialById(id, userId) {
    return await Testimonial.findOne({ id, userId }).lean();
  }

  async updateTestimonial(id, userId, updates) {
    return await Testimonial.findOneAndUpdate(
      { id, userId },
      { ...updates, updatedAt: new Date() },
      { new: true }
    );
  }

  async deleteTestimonial(id, userId) {
    const result = await Testimonial.findOneAndDelete({ id, userId });
    return !!result;
  }

  async regenerateTestimonial(id, userId, model, options = {}) {
    const existingTestimonial = await Testimonial.findOne({ id, userId });
    if (!existingTestimonial) {
      throw new Error('Testimonial not found');
    }

    // Use existing data but with new model
    const testimonialData = {
      ...existingTestimonial.toObject(),
      model,
      ...options
    };

    // Generate new content
    const newTestimonial = await this.generateTestimonial(userId, testimonialData);
    
    // Update the existing record
    return await this.updateTestimonial(id, userId, {
      content: newTestimonial.content,
      alternatives: newTestimonial.alternatives,
      model: newTestimonial.model,
      metadata: newTestimonial.metadata
    });
  }

  async checkUserLimits(userId) {
    const user = await User.findById(userId);
    const plan = user.subscription?.plan || 'starter';
    
    const limits = {
      starter: { monthly: 100, daily: 10 },
      professional: { monthly: 500, daily: 50 },
      enterprise: { monthly: -1, daily: -1 } // Unlimited
    };
    
    const userLimits = limits[plan];
    if (!userLimits) {
      throw new Error('Invalid subscription plan');
    }
    
    // Check monthly limits
    const startOfMonth = moment().startOf('month').toDate();
    const monthlyUsage = await Testimonial.countDocuments({
      userId,
      createdAt: { $gte: startOfMonth }
    });
    
    if (userLimits.monthly !== -1 && monthlyUsage >= userLimits.monthly) {
      return {
        allowed: false,
        message: 'Monthly limit exceeded. Please upgrade your plan.',
        remaining: 0,
        resetDate: moment().add(1, 'month').startOf('month').toDate()
      };
    }
    
    // Check daily limits
    const startOfDay = moment().startOf('day').toDate();
    const dailyUsage = await Testimonial.countDocuments({
      userId,
      createdAt: { $gte: startOfDay }
    });
    
    if (userLimits.daily !== -1 && dailyUsage >= userLimits.daily) {
      return {
        allowed: false,
        message: 'Daily limit exceeded. Please try again tomorrow.',
        remaining: 0,
        resetDate: moment().add(1, 'day').startOf('day').toDate()
      };
    }
    
    return {
      allowed: true,
      remaining: userLimits.monthly === -1 ? -1 : userLimits.monthly - monthlyUsage,
      resetDate: moment().add(1, 'month').startOf('month').toDate()
    };
  }

  async checkBatchLimits(userId, batchSize) {
    const userLimits = await this.checkUserLimits(userId);
    
    if (!userLimits.allowed) {
      return userLimits;
    }
    
    if (userLimits.remaining !== -1 && userLimits.remaining < batchSize) {
      return {
        allowed: false,
        message: `Insufficient remaining quota for batch size of ${batchSize}`,
        remaining: userLimits.remaining,
        resetDate: userLimits.resetDate
      };
    }
    
    return userLimits;
  }

  async updateUserUsage(userId, testimonial) {
    await User.findByIdAndUpdate(userId, {
      $inc: {
        'usage.testimonialsGenerated': 1,
        'usage.tokensUsed': testimonial.metadata.tokensUsed || 0
      },
      $set: {
        'usage.lastGenerated': new Date()
      }
    });
  }

  async trackGeneration(userId, testimonial) {
    const analytics = new Analytics({
      userId,
      event: 'testimonial_generated',
      data: {
        templateType: testimonial.templateType,
        model: testimonial.model,
        qualityScore: testimonial.metadata.qualityScore,
        tokensUsed: testimonial.metadata.tokensUsed,
        generationTime: testimonial.metadata.generationTime
      },
      timestamp: new Date()
    });
    
    await analytics.save();
  }

  async getTestimonialAnalytics(userId, period = '30d') {
    const startDate = moment().subtract(parseInt(period), 'days').toDate();
    
    const analytics = await Analytics.aggregate([
      {
        $match: {
          userId,
          event: 'testimonial_generated',
          timestamp: { $gte: startDate }
        }
      },
      {
        $group: {
          _id: null,
          totalGenerated: { $sum: 1 },
          avgQualityScore: { $avg: '$data.qualityScore' },
          totalTokensUsed: { $sum: '$data.tokensUsed' },
          avgGenerationTime: { $avg: '$data.generationTime' },
          byTemplate: {
            $push: {
              template: '$data.templateType',
              quality: '$data.qualityScore'
            }
          },
          byModel: {
            $push: {
              model: '$data.model',
              tokens: '$data.tokensUsed'
            }
          }
        }
      }
    ]);
    
    return analytics[0] || {
      totalGenerated: 0,
      avgQualityScore: 0,
      totalTokensUsed: 0,
      avgGenerationTime: 0,
      byTemplate: [],
      byModel: []
    };
  }

  async exportTestimonials(userId, format = 'json', filters = {}) {
    const query = { userId, ...filters };
    const testimonials = await Testimonial.find(query).lean();
    
    if (format === 'csv') {
      return this.convertToCSV(testimonials);
    }
    
    return JSON.stringify(testimonials, null, 2);
  }

  convertToCSV(testimonials) {
    if (testimonials.length === 0) return '';
    
    const headers = [
      'ID', 'Template Type', 'Product Name', 'Content', 'Tone', 'Length',
      'Model', 'Quality Score', 'Created At', 'Status'
    ];
    
    const rows = testimonials.map(t => [
      t.id,
      t.templateType,
      t.productName,
      `"${t.content.replace(/"/g, '""')}"`, // Escape quotes
      t.tone,
      t.length,
      t.model,
      t.metadata?.qualityScore || 0,
      t.createdAt,
      t.status
    ]);
    
    return [headers, ...rows].map(row => row.join(',')).join('\n');
  }
}

module.exports = TestimonialService;



