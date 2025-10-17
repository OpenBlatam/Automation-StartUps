const OpenAI = require('openai');
const axios = require('axios');
const natural = require('natural');
const sentiment = require('sentiment');

class AdvancedAIService {
  constructor() {
    this.openai = new OpenAI({
      apiKey: process.env.OPENAI_API_KEY
    });
    
    this.models = {
      'gpt-3.5-turbo': { cost: 0.002, maxTokens: 4096, speed: 'fast' },
      'gpt-4': { cost: 0.03, maxTokens: 8192, speed: 'medium' },
      'gpt-4-turbo': { cost: 0.01, maxTokens: 128000, speed: 'fast' },
      'claude-3-sonnet': { cost: 0.015, maxTokens: 200000, speed: 'medium' },
      'claude-3-opus': { cost: 0.075, maxTokens: 200000, speed: 'slow' },
      'gpt-4-vision': { cost: 0.01, maxTokens: 4096, speed: 'medium', vision: true }
    };

    // Initialize NLP tools
    this.sentimentAnalyzer = new sentiment();
    this.tokenizer = new natural.WordTokenizer();
    this.stemmer = natural.PorterStemmer;
  }

  /**
   * Advanced content generation with multi-modal capabilities
   */
  async generateAdvancedContent(options = {}) {
    const {
      prompt,
      context = {},
      targetAudience = {},
      brandVoice = {},
      competitors = [],
      marketTrends = [],
      visualElements = [],
      systemPrompt = 'You are an expert marketing strategist and copywriter.',
      model = 'gpt-4-turbo',
      temperature = 0.7,
      maxTokens = 1000,
      includeAnalysis = true
    } = options;

    try {
      // Enhanced prompt with context
      const enhancedPrompt = await this.buildEnhancedPrompt({
        prompt,
        context,
        targetAudience,
        brandVoice,
        competitors,
        marketTrends
      });

      // Generate content
      const response = await this.openai.chat.completions.create({
        model,
        messages: [
          { role: 'system', content: systemPrompt },
          { role: 'user', content: enhancedPrompt }
        ],
        temperature,
        max_tokens: maxTokens,
        top_p: 1,
        frequency_penalty: 0,
        presence_penalty: 0
      });

      const content = response.choices[0].message.content;
      const usage = response.usage;

      // Advanced analysis
      let analysis = null;
      if (includeAnalysis) {
        analysis = await this.analyzeContentAdvanced(content, {
          targetAudience,
          brandVoice,
          competitors
        });
      }

      // Generate variations if requested
      const variations = options.generateVariations ? 
        await this.generateContentVariations(content, options) : [];

      return {
        content,
        variations,
        analysis,
        metadata: {
          model,
          usage,
          cost: this.calculateCost(model, usage.total_tokens),
          timestamp: new Date().toISOString(),
          context: {
            targetAudience,
            brandVoice,
            competitors: competitors.length,
            marketTrends: marketTrends.length
          }
        }
      };

    } catch (error) {
      console.error('Advanced content generation error:', error);
      throw new Error(`Advanced content generation failed: ${error.message}`);
    }
  }

  /**
   * Build enhanced prompt with context and market intelligence
   */
  async buildEnhancedPrompt({ prompt, context, targetAudience, brandVoice, competitors, marketTrends }) {
    let enhancedPrompt = prompt;

    // Add target audience context
    if (targetAudience && Object.keys(targetAudience).length > 0) {
      enhancedPrompt += `\n\nTarget Audience:\n`;
      Object.entries(targetAudience).forEach(([key, value]) => {
        enhancedPrompt += `- ${key}: ${value}\n`;
      });
    }

    // Add brand voice context
    if (brandVoice && Object.keys(brandVoice).length > 0) {
      enhancedPrompt += `\n\nBrand Voice:\n`;
      Object.entries(brandVoice).forEach(([key, value]) => {
        enhancedPrompt += `- ${key}: ${value}\n`;
      });
    }

    // Add competitor analysis
    if (competitors && competitors.length > 0) {
      enhancedPrompt += `\n\nCompetitor Analysis:\n`;
      competitors.forEach((competitor, index) => {
        enhancedPrompt += `${index + 1}. ${competitor.name}: ${competitor.analysis}\n`;
      });
    }

    // Add market trends
    if (marketTrends && marketTrends.length > 0) {
      enhancedPrompt += `\n\nCurrent Market Trends:\n`;
      marketTrends.forEach((trend, index) => {
        enhancedPrompt += `${index + 1}. ${trend}\n`;
      });
    }

    // Add context
    if (context && Object.keys(context).length > 0) {
      enhancedPrompt += `\n\nAdditional Context:\n`;
      Object.entries(context).forEach(([key, value]) => {
        enhancedPrompt += `- ${key}: ${value}\n`;
      });
    }

    return enhancedPrompt;
  }

  /**
   * Advanced content analysis with NLP
   */
  async analyzeContentAdvanced(content, options = {}) {
    const {
      targetAudience = {},
      brandVoice = {},
      competitors = []
    } = options;

    // Sentiment analysis
    const sentimentResult = this.sentimentAnalyzer.analyze(content);
    
    // Readability analysis
    const readability = this.analyzeReadability(content);
    
    // Keyword analysis
    const keywords = this.extractKeywords(content);
    
    // Brand voice alignment
    const brandAlignment = this.analyzeBrandVoiceAlignment(content, brandVoice);
    
    // Competitor differentiation
    const differentiation = this.analyzeCompetitorDifferentiation(content, competitors);
    
    // Engagement prediction
    const engagementScore = this.predictEngagement(content, targetAudience);

    return {
      sentiment: {
        score: sentimentResult.score,
        comparative: sentimentResult.comparative,
        positive: sentimentResult.positive,
        negative: sentimentResult.negative
      },
      readability: {
        score: readability.score,
        level: readability.level,
        wordCount: readability.wordCount,
        sentenceCount: readability.sentenceCount,
        avgWordsPerSentence: readability.avgWordsPerSentence
      },
      keywords: {
        primary: keywords.primary,
        secondary: keywords.secondary,
        density: keywords.density
      },
      brandAlignment: {
        score: brandAlignment.score,
        factors: brandAlignment.factors
      },
      differentiation: {
        score: differentiation.score,
        uniqueElements: differentiation.uniqueElements
      },
      engagement: {
        predictedScore: engagementScore.score,
        factors: engagementScore.factors
      },
      recommendations: this.generateRecommendations({
        sentiment: sentimentResult,
        readability,
        brandAlignment,
        differentiation,
        engagement: engagementScore
      })
    };
  }

  /**
   * Analyze content readability
   */
  analyzeReadability(content) {
    const sentences = content.split(/[.!?]+/).filter(s => s.trim().length > 0);
    const words = this.tokenizer.tokenize(content);
    const syllables = words.reduce((total, word) => total + this.countSyllables(word), 0);
    
    const avgWordsPerSentence = words.length / sentences.length;
    const avgSyllablesPerWord = syllables / words.length;
    
    // Flesch Reading Ease Score
    const fleschScore = 206.835 - (1.015 * avgWordsPerSentence) - (84.6 * avgSyllablesPerWord);
    
    let level;
    if (fleschScore >= 90) level = 'Very Easy';
    else if (fleschScore >= 80) level = 'Easy';
    else if (fleschScore >= 70) level = 'Fairly Easy';
    else if (fleschScore >= 60) level = 'Standard';
    else if (fleschScore >= 50) level = 'Fairly Difficult';
    else if (fleschScore >= 30) level = 'Difficult';
    else level = 'Very Difficult';

    return {
      score: Math.round(fleschScore),
      level,
      wordCount: words.length,
      sentenceCount: sentences.length,
      avgWordsPerSentence: Math.round(avgWordsPerSentence * 10) / 10
    };
  }

  /**
   * Extract keywords from content
   */
  extractKeywords(content) {
    const words = this.tokenizer.tokenize(content.toLowerCase());
    const stopWords = new Set(['the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by']);
    
    const filteredWords = words.filter(word => 
      word.length > 3 && 
      !stopWords.has(word) && 
      /^[a-zA-Z]+$/.test(word)
    );
    
    const wordFreq = {};
    filteredWords.forEach(word => {
      wordFreq[word] = (wordFreq[word] || 0) + 1;
    });
    
    const sortedWords = Object.entries(wordFreq)
      .sort(([,a], [,b]) => b - a)
      .slice(0, 10);
    
    return {
      primary: sortedWords.slice(0, 5).map(([word]) => word),
      secondary: sortedWords.slice(5).map(([word]) => word),
      density: sortedWords.reduce((total, [, freq]) => total + freq, 0) / words.length
    };
  }

  /**
   * Analyze brand voice alignment
   */
  analyzeBrandVoiceAlignment(content, brandVoice) {
    if (!brandVoice || Object.keys(brandVoice).length === 0) {
      return { score: 0, factors: [] };
    }

    const factors = [];
    let score = 0;

    // Tone analysis
    if (brandVoice.tone) {
      const toneMatch = this.analyzeToneMatch(content, brandVoice.tone);
      factors.push({ factor: 'Tone', score: toneMatch.score, details: toneMatch.details });
      score += toneMatch.score * 0.3;
    }

    // Style analysis
    if (brandVoice.style) {
      const styleMatch = this.analyzeStyleMatch(content, brandVoice.style);
      factors.push({ factor: 'Style', score: styleMatch.score, details: styleMatch.details });
      score += styleMatch.score * 0.3;
    }

    // Language complexity
    if (brandVoice.complexity) {
      const complexityMatch = this.analyzeComplexityMatch(content, brandVoice.complexity);
      factors.push({ factor: 'Complexity', score: complexityMatch.score, details: complexityMatch.details });
      score += complexityMatch.score * 0.2;
    }

    // Emotional tone
    if (brandVoice.emotionalTone) {
      const emotionalMatch = this.analyzeEmotionalTone(content, brandVoice.emotionalTone);
      factors.push({ factor: 'Emotional Tone', score: emotionalMatch.score, details: emotionalMatch.details });
      score += emotionalMatch.score * 0.2;
    }

    return {
      score: Math.round(score * 100),
      factors
    };
  }

  /**
   * Analyze competitor differentiation
   */
  analyzeCompetitorDifferentiation(content, competitors) {
    if (!competitors || competitors.length === 0) {
      return { score: 100, uniqueElements: [] };
    }

    const contentWords = new Set(this.tokenizer.tokenize(content.toLowerCase()));
    const competitorWords = new Set();
    
    competitors.forEach(competitor => {
      if (competitor.content) {
        this.tokenizer.tokenize(competitor.content.toLowerCase()).forEach(word => {
          competitorWords.add(word);
        });
      }
    });

    const uniqueWords = [...contentWords].filter(word => !competitorWords.has(word));
    const uniqueElements = uniqueWords.slice(0, 10);

    const differentiationScore = Math.min(100, (uniqueWords.length / contentWords.size) * 100);

    return {
      score: Math.round(differentiationScore),
      uniqueElements
    };
  }

  /**
   * Predict engagement based on content and audience
   */
  predictEngagement(content, targetAudience) {
    const factors = [];
    let score = 50; // Base score

    // Content length optimization
    const wordCount = this.tokenizer.tokenize(content).length;
    if (wordCount >= 100 && wordCount <= 300) {
      score += 15;
      factors.push({ factor: 'Optimal Length', impact: '+15' });
    } else if (wordCount < 50) {
      score -= 10;
      factors.push({ factor: 'Too Short', impact: '-10' });
    } else if (wordCount > 500) {
      score -= 5;
      factors.push({ factor: 'Too Long', impact: '-5' });
    }

    // Question usage
    const questionCount = (content.match(/\?/g) || []).length;
    if (questionCount > 0) {
      score += Math.min(10, questionCount * 3);
      factors.push({ factor: 'Questions Used', impact: `+${Math.min(10, questionCount * 3)}` });
    }

    // Call-to-action presence
    const ctaWords = ['buy', 'click', 'learn', 'discover', 'try', 'get', 'start', 'join'];
    const hasCTA = ctaWords.some(word => content.toLowerCase().includes(word));
    if (hasCTA) {
      score += 10;
      factors.push({ factor: 'Call-to-Action', impact: '+10' });
    }

    // Emotional words
    const emotionalWords = ['amazing', 'incredible', 'fantastic', 'exclusive', 'limited', 'free', 'new', 'best'];
    const emotionalCount = emotionalWords.filter(word => content.toLowerCase().includes(word)).length;
    if (emotionalCount > 0) {
      score += Math.min(15, emotionalCount * 5);
      factors.push({ factor: 'Emotional Words', impact: `+${Math.min(15, emotionalCount * 5)}` });
    }

    // Audience-specific optimization
    if (targetAudience && targetAudience.age) {
      if (targetAudience.age < 30 && content.includes('trending') || content.includes('viral')) {
        score += 5;
        factors.push({ factor: 'Youth Appeal', impact: '+5' });
      }
    }

    return {
      score: Math.min(100, Math.max(0, score)),
      factors
    };
  }

  /**
   * Generate content variations
   */
  async generateContentVariations(originalContent, options = {}) {
    const variations = [];
    const { count = 3, styles = ['casual', 'formal', 'persuasive'] } = options;

    for (let i = 0; i < count; i++) {
      const style = styles[i % styles.length];
      const variationPrompt = `Rewrite the following content in a ${style} style while maintaining the core message:\n\n${originalContent}`;
      
      try {
        const response = await this.openai.chat.completions.create({
          model: options.model || 'gpt-3.5-turbo',
          messages: [
            { role: 'system', content: `You are an expert copywriter specializing in ${style} writing style.` },
            { role: 'user', content: variationPrompt }
          ],
          temperature: 0.8,
          max_tokens: 500
        });

        variations.push({
          style,
          content: response.choices[0].message.content,
          variation: i + 1
        });
      } catch (error) {
        console.error(`Variation ${i + 1} generation failed:`, error);
      }
    }

    return variations;
  }

  /**
   * Generate recommendations based on analysis
   */
  generateRecommendations(analysis) {
    const recommendations = [];

    // Sentiment recommendations
    if (analysis.sentiment.score < -2) {
      recommendations.push({
        type: 'sentiment',
        priority: 'high',
        message: 'Content has negative sentiment. Consider adding positive elements or reframing the message.',
        action: 'Add positive words and phrases to improve sentiment'
      });
    }

    // Readability recommendations
    if (analysis.readability.score < 60) {
      recommendations.push({
        type: 'readability',
        priority: 'medium',
        message: 'Content may be difficult to read. Consider simplifying sentence structure.',
        action: 'Break down complex sentences and use simpler words'
      });
    }

    // Brand alignment recommendations
    if (analysis.brandAlignment.score < 70) {
      recommendations.push({
        type: 'brand',
        priority: 'high',
        message: 'Content doesn\'t align well with brand voice. Adjust tone and style.',
        action: 'Review brand guidelines and adjust content accordingly'
      });
    }

    // Engagement recommendations
    if (analysis.engagement.predictedScore < 60) {
      recommendations.push({
        type: 'engagement',
        priority: 'medium',
        message: 'Content may have low engagement potential. Add interactive elements.',
        action: 'Include questions, calls-to-action, or emotional triggers'
      });
    }

    return recommendations;
  }

  /**
   * Count syllables in a word
   */
  countSyllables(word) {
    word = word.toLowerCase();
    if (word.length <= 3) return 1;
    word = word.replace(/(?:[^laeiouy]es|ed|[^laeiouy]e)$/, '');
    word = word.replace(/^y/, '');
    const matches = word.match(/[aeiouy]{1,2}/g);
    return matches ? matches.length : 1;
  }

  /**
   * Analyze tone match
   */
  analyzeToneMatch(content, targetTone) {
    const toneIndicators = {
      professional: ['ensure', 'implement', 'strategic', 'comprehensive', 'analysis'],
      casual: ['hey', 'awesome', 'cool', 'grab', 'check out'],
      friendly: ['welcome', 'happy', 'excited', 'pleased', 'delighted'],
      authoritative: ['proven', 'expert', 'leading', 'premier', 'superior']
    };

    const contentLower = content.toLowerCase();
    const targetIndicators = toneIndicators[targetTone] || [];
    const matches = targetIndicators.filter(indicator => contentLower.includes(indicator)).length;
    
    return {
      score: Math.min(100, (matches / targetIndicators.length) * 100),
      details: `${matches}/${targetIndicators.length} tone indicators found`
    };
  }

  /**
   * Analyze style match
   */
  analyzeStyleMatch(content, targetStyle) {
    const styleIndicators = {
      formal: ['therefore', 'furthermore', 'consequently', 'nevertheless'],
      informal: ['so', 'well', 'actually', 'basically', 'literally'],
      conversational: ['you', 'your', 'we', 'us', 'let\'s'],
      technical: ['algorithm', 'methodology', 'implementation', 'optimization']
    };

    const contentLower = content.toLowerCase();
    const targetIndicators = styleIndicators[targetStyle] || [];
    const matches = targetIndicators.filter(indicator => contentLower.includes(indicator)).length;
    
    return {
      score: Math.min(100, (matches / targetIndicators.length) * 100),
      details: `${matches}/${targetIndicators.length} style indicators found`
    };
  }

  /**
   * Analyze complexity match
   */
  analyzeComplexityMatch(content, targetComplexity) {
    const avgWordsPerSentence = this.tokenizer.tokenize(content).length / content.split(/[.!?]+/).length;
    const avgSyllablesPerWord = this.tokenizer.tokenize(content).reduce((total, word) => total + this.countSyllables(word), 0) / this.tokenizer.tokenize(content).length;
    
    const complexityScore = (avgWordsPerSentence * 0.5) + (avgSyllablesPerWord * 10);
    
    let targetRange;
    switch (targetComplexity) {
      case 'simple': targetRange = [0, 15]; break;
      case 'moderate': targetRange = [15, 25]; break;
      case 'complex': targetRange = [25, 35]; break;
      default: targetRange = [15, 25];
    }
    
    const score = complexityScore >= targetRange[0] && complexityScore <= targetRange[1] ? 100 : 
                  Math.max(0, 100 - Math.abs(complexityScore - (targetRange[0] + targetRange[1]) / 2) * 5);
    
    return {
      score: Math.round(score),
      details: `Complexity score: ${complexityScore.toFixed(1)} (target: ${targetRange[0]}-${targetRange[1]})`
    };
  }

  /**
   * Analyze emotional tone
   */
  analyzeEmotionalTone(content, targetEmotion) {
    const emotionWords = {
      excitement: ['amazing', 'incredible', 'fantastic', 'excited', 'thrilled'],
      trust: ['reliable', 'trusted', 'proven', 'secure', 'guaranteed'],
      urgency: ['limited', 'exclusive', 'now', 'hurry', 'deadline'],
      calm: ['peaceful', 'relaxed', 'serene', 'gentle', 'soothing']
    };

    const contentLower = content.toLowerCase();
    const targetWords = emotionWords[targetEmotion] || [];
    const matches = targetWords.filter(word => contentLower.includes(word)).length;
    
    return {
      score: Math.min(100, (matches / targetWords.length) * 100),
      details: `${matches}/${targetWords.length} emotional indicators found`
    };
  }

  /**
   * Calculate cost based on model and tokens
   */
  calculateCost(model, tokens) {
    const modelInfo = this.models[model];
    if (!modelInfo) return 0;
    return (tokens / 1000) * modelInfo.cost;
  }

  /**
   * Get available models with capabilities
   */
  getAvailableModels() {
    return this.models;
  }
}

module.exports = new AdvancedAIService();






