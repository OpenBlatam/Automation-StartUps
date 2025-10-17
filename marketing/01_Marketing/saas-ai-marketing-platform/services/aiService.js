const OpenAI = require('openai');
const axios = require('axios');

class AIService {
  constructor() {
    this.openai = new OpenAI({
      apiKey: process.env.OPENAI_API_KEY
    });
    
    this.models = {
      'gpt-3.5-turbo': { cost: 0.002, maxTokens: 4096 },
      'gpt-4': { cost: 0.03, maxTokens: 8192 },
      'gpt-4-turbo': { cost: 0.01, maxTokens: 128000 },
      'claude-3-sonnet': { cost: 0.015, maxTokens: 200000 },
      'claude-3-opus': { cost: 0.075, maxTokens: 200000 }
    };
  }

  /**
   * Generate content using OpenAI API
   * @param {Object} options - Generation options
   * @param {string} options.prompt - The input prompt
   * @param {string} options.systemPrompt - System prompt for context
   * @param {string} options.model - AI model to use
   * @param {number} options.temperature - Creativity level (0-2)
   * @param {number} options.maxTokens - Maximum tokens to generate
   * @param {Object} options.variables - Template variables
   * @returns {Promise<Object>} Generated content and metadata
   */
  async generateContent(options = {}) {
    const {
      prompt,
      systemPrompt = 'You are a professional marketing copywriter. Create engaging, persuasive, and high-quality content that drives results.',
      model = 'gpt-3.5-turbo',
      temperature = 0.7,
      maxTokens = 500,
      variables = {}
    } = options;

    try {
      // Validate model
      if (!this.models[model]) {
        throw new Error(`Unsupported model: ${model}`);
      }

      // Process prompt with variables
      const processedPrompt = this.processPrompt(prompt, variables);

      // Prepare messages
      const messages = [];
      if (systemPrompt) {
        messages.push({ role: 'system', content: systemPrompt });
      }
      messages.push({ role: 'user', content: processedPrompt });

      // Generate content
      const response = await this.openai.chat.completions.create({
        model,
        messages,
        temperature,
        max_tokens: Math.min(maxTokens, this.models[model].maxTokens),
        top_p: 1,
        frequency_penalty: 0,
        presence_penalty: 0
      });

      const content = response.choices[0].message.content;
      const usage = response.usage;

      // Calculate cost
      const cost = this.calculateCost(model, usage.total_tokens);

      return {
        content,
        usage: {
          promptTokens: usage.prompt_tokens,
          completionTokens: usage.completion_tokens,
          totalTokens: usage.total_tokens
        },
        cost,
        model,
        timestamp: new Date().toISOString()
      };

    } catch (error) {
      console.error('AI generation error:', error);
      throw new Error(`Content generation failed: ${error.message}`);
    }
  }

  /**
   * Generate multiple content variations
   * @param {Object} options - Generation options
   * @param {number} options.count - Number of variations to generate
   * @returns {Promise<Array>} Array of generated content variations
   */
  async generateVariations(options = {}) {
    const { count = 3, ...generationOptions } = options;
    const variations = [];

    for (let i = 0; i < count; i++) {
      try {
        // Vary temperature for different styles
        const temperature = 0.5 + (i * 0.3);
        const variation = await this.generateContent({
          ...generationOptions,
          temperature: Math.min(temperature, 1.5)
        });
        
        variations.push({
          ...variation,
          variation: i + 1
        });
      } catch (error) {
        console.error(`Variation ${i + 1} generation failed:`, error);
      }
    }

    return variations;
  }

  /**
   * Optimize content for specific goals
   * @param {string} content - Original content
   * @param {string} goal - Optimization goal (seo, conversion, engagement, etc.)
   * @param {Object} options - Additional options
   * @returns {Promise<Object>} Optimized content
   */
  async optimizeContent(content, goal, options = {}) {
    const optimizationPrompts = {
      seo: 'Optimize this content for SEO by improving keyword density, adding relevant keywords, and enhancing readability while maintaining the original message.',
      conversion: 'Optimize this content to increase conversions by making it more persuasive, adding compelling calls-to-action, and addressing customer objections.',
      engagement: 'Optimize this content to increase engagement by making it more interactive, adding emotional triggers, and creating a stronger connection with the audience.',
      clarity: 'Optimize this content for clarity by simplifying complex sentences, improving flow, and making the message more direct and understandable.',
      creativity: 'Optimize this content to be more creative and unique while maintaining the core message and professional tone.'
    };

    const prompt = optimizationPrompts[goal] || optimizationPrompts.clarity;
    
    const fullPrompt = `${prompt}\n\nOriginal content:\n${content}`;

    return this.generateContent({
      prompt: fullPrompt,
      systemPrompt: 'You are an expert content optimizer. Improve the given content according to the specified goal while maintaining quality and brand voice.',
      ...options
    });
  }

  /**
   * Analyze content performance
   * @param {string} content - Content to analyze
   * @param {string} type - Content type (email, social, blog, etc.)
   * @returns {Promise<Object>} Analysis results
   */
  async analyzeContent(content, type = 'general') {
    const analysisPrompts = {
      email: 'Analyze this email content for effectiveness. Provide scores for: subject line appeal (1-10), opening hook (1-10), value proposition clarity (1-10), call-to-action strength (1-10), and overall persuasiveness (1-10). Also suggest improvements.',
      social: 'Analyze this social media content for engagement potential. Provide scores for: attention-grabbing (1-10), shareability (1-10), brand alignment (1-10), call-to-action effectiveness (1-10), and viral potential (1-10). Also suggest improvements.',
      blog: 'Analyze this blog content for quality and SEO. Provide scores for: readability (1-10), SEO optimization (1-10), value to reader (1-10), structure and flow (1-10), and engagement potential (1-10). Also suggest improvements.',
      ad: 'Analyze this ad copy for conversion potential. Provide scores for: headline impact (1-10), benefit clarity (1-10), urgency creation (1-10), trust building (1-10), and call-to-action strength (1-10). Also suggest improvements.',
      general: 'Analyze this content for overall quality and effectiveness. Provide scores for: clarity (1-10), persuasiveness (1-10), engagement (1-10), professionalism (1-10), and impact (1-10). Also suggest improvements.'
    };

    const prompt = analysisPrompts[type] || analysisPrompts.general;
    const fullPrompt = `${prompt}\n\nContent to analyze:\n${content}`;

    return this.generateContent({
      prompt: fullPrompt,
      systemPrompt: 'You are an expert content analyst. Provide detailed, constructive feedback with specific scores and actionable improvement suggestions.',
      maxTokens: 800
    });
  }

  /**
   * Generate content ideas
   * @param {string} topic - Main topic
   * @param {string} type - Content type
   * @param {number} count - Number of ideas to generate
   * @returns {Promise<Array>} Array of content ideas
   */
  async generateContentIdeas(topic, type = 'general', count = 10) {
    const typePrompts = {
      email: 'Generate engaging email marketing ideas for',
      social: 'Generate viral social media content ideas for',
      blog: 'Generate compelling blog post ideas for',
      ad: 'Generate high-converting ad copy ideas for',
      general: 'Generate creative content ideas for'
    };

    const prompt = `${typePrompts[type] || typePrompts.general} "${topic}". Provide ${count} unique, actionable ideas with brief descriptions.`;

    const response = await this.generateContent({
      prompt,
      systemPrompt: 'You are a creative content strategist. Generate innovative, engaging content ideas that drive results.',
      maxTokens: 1000
    });

    // Parse ideas from response
    const ideas = this.parseContentIdeas(response.content, count);
    return ideas;
  }

  /**
   * Translate content to different languages
   * @param {string} content - Content to translate
   * @param {string} targetLanguage - Target language code
   * @param {string} sourceLanguage - Source language code (optional)
   * @returns {Promise<Object>} Translated content
   */
  async translateContent(content, targetLanguage, sourceLanguage = 'auto') {
    const prompt = `Translate the following content to ${targetLanguage}${sourceLanguage !== 'auto' ? ` from ${sourceLanguage}` : ''}. Maintain the original tone, style, and marketing effectiveness:\n\n${content}`;

    return this.generateContent({
      prompt,
      systemPrompt: 'You are a professional translator specializing in marketing content. Preserve the original meaning, tone, and persuasive elements while ensuring natural language flow.',
      maxTokens: 1000
    });
  }

  /**
   * Process prompt with variables
   * @param {string} prompt - Original prompt
   * @param {Object} variables - Variables to replace
   * @returns {string} Processed prompt
   */
  processPrompt(prompt, variables) {
    let processedPrompt = prompt;
    
    for (const [key, value] of Object.entries(variables)) {
      const placeholder = new RegExp(`{${key}}`, 'g');
      processedPrompt = processedPrompt.replace(placeholder, value || '');
    }
    
    return processedPrompt;
  }

  /**
   * Calculate cost based on model and tokens
   * @param {string} model - AI model used
   * @param {number} tokens - Number of tokens
   * @returns {number} Cost in USD
   */
  calculateCost(model, tokens) {
    const modelInfo = this.models[model];
    if (!modelInfo) return 0;
    
    return (tokens / 1000) * modelInfo.cost;
  }

  /**
   * Parse content ideas from AI response
   * @param {string} response - AI response
   * @param {number} expectedCount - Expected number of ideas
   * @returns {Array} Parsed ideas
   */
  parseContentIdeas(response, expectedCount) {
    const ideas = [];
    const lines = response.split('\n').filter(line => line.trim());
    
    for (const line of lines) {
      if (ideas.length >= expectedCount) break;
      
      // Extract idea from numbered or bulleted lines
      const match = line.match(/^\d+\.\s*(.+)|^[-*]\s*(.+)|^(.+)/);
      if (match) {
        const idea = match[1] || match[2] || match[3];
        if (idea && idea.trim()) {
          ideas.push({
            title: idea.trim(),
            description: '',
            category: 'general'
          });
        }
      }
    }
    
    return ideas;
  }

  /**
   * Get available models and their capabilities
   * @returns {Object} Model information
   */
  getAvailableModels() {
    return this.models;
  }

  /**
   * Validate content generation request
   * @param {Object} options - Request options
   * @returns {Object} Validation result
   */
  validateRequest(options) {
    const errors = [];
    
    if (!options.prompt || options.prompt.trim().length === 0) {
      errors.push('Prompt is required');
    }
    
    if (options.prompt && options.prompt.length > 10000) {
      errors.push('Prompt is too long (max 10,000 characters)');
    }
    
    if (options.model && !this.models[options.model]) {
      errors.push(`Invalid model: ${options.model}`);
    }
    
    if (options.temperature && (options.temperature < 0 || options.temperature > 2)) {
      errors.push('Temperature must be between 0 and 2');
    }
    
    if (options.maxTokens && (options.maxTokens < 1 || options.maxTokens > 4000)) {
      errors.push('Max tokens must be between 1 and 4000');
    }
    
    return {
      isValid: errors.length === 0,
      errors
    };
  }
}

module.exports = new AIService();









