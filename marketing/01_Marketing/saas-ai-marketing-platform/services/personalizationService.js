const natural = require('natural');
const User = require('../models/User');
const GeneratedContent = require('../models/GeneratedContent');
const ContentTemplate = require('../models/ContentTemplate');
const aiService = require('./advancedAIService');
const analyticsService = require('./analyticsService');
const abTestingService = require('./abTestingService');

class PersonalizationService {
  constructor() {
    this.userProfiles = new Map();
    this.contentPreferences = new Map();
    this.behaviorPatterns = new Map();
    this.personalizationRules = new Map();
    this.isInitialized = false;
  }

  /**
   * Initialize personalization service
   */
  async initialize() {
    if (this.isInitialized) return;

    try {
      await this.loadPersonalizationRules();
      await this.loadUserProfiles();
      this.isInitialized = true;
      console.log('Personalization Service initialized successfully');
    } catch (error) {
      console.error('Failed to initialize Personalization Service:', error);
      throw error;
    }
  }

  /**
   * Personalize content for user
   */
  async personalizeContent(userId, content, options = {}) {
    await this.initialize();

    try {
      const userProfile = await this.getUserProfile(userId);
      const personalizationRules = this.getPersonalizationRules(userProfile);
      
      let personalizedContent = content;
      const appliedRules = [];

      // Apply personalization rules
      for (const rule of personalizationRules) {
        const result = await this.applyPersonalizationRule(personalizedContent, rule, userProfile);
        if (result.modified) {
          personalizedContent = result.content;
          appliedRules.push(rule);
        }
      }

      // Apply AI-powered personalization
      const aiPersonalization = await this.applyAIPersonalization(personalizedContent, userProfile, options);
      if (aiPersonalization.modified) {
        personalizedContent = aiPersonalization.content;
        appliedRules.push({ type: 'ai_personalization', description: 'AI-powered content adaptation' });
      }

      // Generate content variations
      const variations = await this.generatePersonalizedVariations(personalizedContent, userProfile, options);

      return {
        originalContent: content,
        personalizedContent,
        variations,
        appliedRules,
        personalizationScore: this.calculatePersonalizationScore(appliedRules, userProfile),
        recommendations: this.generatePersonalizationRecommendations(userProfile, appliedRules)
      };
    } catch (error) {
      console.error('Content personalization error:', error);
      throw error;
    }
  }

  /**
   * Get user profile
   */
  async getUserProfile(userId) {
    if (this.userProfiles.has(userId)) {
      return this.userProfiles.get(userId);
    }

    const user = await User.findById(userId);
    if (!user) {
      throw new Error('User not found');
    }

    // Get user analytics
    const analytics = await analyticsService.getUserAnalytics(userId, '30d');
    
    // Get content preferences
    const preferences = await this.getContentPreferences(userId);
    
    // Get behavior patterns
    const behaviorPatterns = await this.getBehaviorPatterns(userId);

    const profile = {
      userId,
      demographics: {
        age: this.calculateAge(user.birthDate),
        gender: user.gender,
        location: user.location,
        industry: user.industry,
        jobTitle: user.jobTitle,
        company: user.company
      },
      preferences: preferences,
      behavior: behaviorPatterns,
      analytics: analytics,
      engagement: {
        averageEngagement: analytics.overview.averageRating || 0,
        preferredContentTypes: this.extractPreferredContentTypes(analytics),
        optimalPostingTimes: this.extractOptimalPostingTimes(analytics),
        preferredLength: this.extractPreferredLength(analytics)
      },
      interests: this.extractInterests(user, analytics),
      personality: this.analyzePersonality(user, analytics),
      lastUpdated: new Date()
    };

    this.userProfiles.set(userId, profile);
    return profile;
  }

  /**
   * Get content preferences
   */
  async getContentPreferences(userId) {
    if (this.contentPreferences.has(userId)) {
      return this.contentPreferences.get(userId);
    }

    // Analyze user's content history
    const contentHistory = await GeneratedContent.find({ userId })
      .sort({ createdAt: -1 })
      .limit(100);

    const preferences = {
      tone: this.analyzeTonePreferences(contentHistory),
      style: this.analyzeStylePreferences(contentHistory),
      length: this.analyzeLengthPreferences(contentHistory),
      topics: this.analyzeTopicPreferences(contentHistory),
      formats: this.analyzeFormatPreferences(contentHistory),
      complexity: this.analyzeComplexityPreferences(contentHistory)
    };

    this.contentPreferences.set(userId, preferences);
    return preferences;
  }

  /**
   * Get behavior patterns
   */
  async getBehaviorPatterns(userId) {
    if (this.behaviorPatterns.has(userId)) {
      return this.behaviorPatterns.get(userId);
    }

    const analytics = await analyticsService.getUserAnalytics(userId, '90d');
    
    const patterns = {
      usagePatterns: this.analyzeUsagePatterns(analytics),
      engagementPatterns: this.analyzeEngagementPatterns(analytics),
      contentPatterns: this.analyzeContentPatterns(analytics),
      timePatterns: this.analyzeTimePatterns(analytics),
      devicePatterns: this.analyzeDevicePatterns(analytics)
    };

    this.behaviorPatterns.set(userId, patterns);
    return patterns;
  }

  /**
   * Get personalization rules
   */
  getPersonalizationRules(userProfile) {
    const rules = [];

    // Demographics-based rules
    if (userProfile.demographics.age < 25) {
      rules.push({
        type: 'tone',
        condition: 'age_young',
        action: 'casual',
        description: 'Use casual tone for younger audience'
      });
    } else if (userProfile.demographics.age > 50) {
      rules.push({
        type: 'tone',
        condition: 'age_mature',
        action: 'professional',
        description: 'Use professional tone for mature audience'
      });
    }

    // Industry-based rules
    if (userProfile.demographics.industry === 'technology') {
      rules.push({
        type: 'complexity',
        condition: 'industry_tech',
        action: 'technical',
        description: 'Use technical language for tech industry'
      });
    } else if (userProfile.demographics.industry === 'healthcare') {
      rules.push({
        type: 'tone',
        condition: 'industry_healthcare',
        action: 'authoritative',
        description: 'Use authoritative tone for healthcare'
      });
    }

    // Engagement-based rules
    if (userProfile.engagement.averageEngagement < 3) {
      rules.push({
        type: 'engagement',
        condition: 'low_engagement',
        action: 'increase_interaction',
        description: 'Add more interactive elements'
      });
    }

    // Preference-based rules
    if (userProfile.preferences.tone === 'casual') {
      rules.push({
        type: 'tone',
        condition: 'preference_casual',
        action: 'casual',
        description: 'Use casual tone based on user preference'
      });
    }

    return rules;
  }

  /**
   * Apply personalization rule
   */
  async applyPersonalizationRule(content, rule, userProfile) {
    let modified = false;
    let newContent = content;

    switch (rule.type) {
      case 'tone':
        newContent = await this.adjustTone(content, rule.action);
        modified = newContent !== content;
        break;
      case 'complexity':
        newContent = await this.adjustComplexity(content, rule.action);
        modified = newContent !== content;
        break;
      case 'engagement':
        newContent = await this.increaseEngagement(content, rule.action);
        modified = newContent !== content;
        break;
      case 'length':
        newContent = await this.adjustLength(content, rule.action, userProfile);
        modified = newContent !== content;
        break;
    }

    return {
      modified,
      content: newContent,
      rule: rule
    };
  }

  /**
   * Apply AI-powered personalization
   */
  async applyAIPersonalization(content, userProfile, options) {
    try {
      const personalizationPrompt = this.buildPersonalizationPrompt(content, userProfile, options);
      
      const result = await aiService.generateAdvancedContent({
        prompt: personalizationPrompt,
        model: 'gpt-4-turbo',
        temperature: 0.7,
        maxTokens: 1000
      });

      return {
        modified: true,
        content: result.content,
        confidence: result.metadata?.confidence || 0.8
      };
    } catch (error) {
      console.error('AI personalization error:', error);
      return {
        modified: false,
        content: content,
        confidence: 0
      };
    }
  }

  /**
   * Build personalization prompt
   */
  buildPersonalizationPrompt(content, userProfile, options) {
    const prompt = `
    Personalize this content for the following user profile:
    
    Demographics:
    - Age: ${userProfile.demographics.age}
    - Industry: ${userProfile.demographics.industry}
    - Job Title: ${userProfile.demographics.jobTitle}
    
    Preferences:
    - Tone: ${userProfile.preferences.tone}
    - Style: ${userProfile.preferences.style}
    - Length: ${userProfile.preferences.length}
    
    Behavior:
    - Average Engagement: ${userProfile.engagement.averageEngagement}
    - Preferred Content Types: ${userProfile.engagement.preferredContentTypes.join(', ')}
    - Optimal Posting Times: ${userProfile.engagement.optimalPostingTimes.join(', ')}
    
    Interests: ${userProfile.interests.join(', ')}
    Personality: ${userProfile.personality}
    
    Original Content:
    ${content}
    
    Personalize this content to match the user's profile while maintaining the core message. 
    Adjust tone, style, complexity, and engagement elements as appropriate.
    `;

    return prompt;
  }

  /**
   * Generate personalized variations
   */
  async generatePersonalizedVariations(content, userProfile, options) {
    const variations = [];
    const variationCount = options.variationCount || 3;

    for (let i = 0; i < variationCount; i++) {
      try {
        const variationPrompt = `
        Create a variation of this personalized content for the same user profile:
        
        User Profile: ${JSON.stringify(userProfile.demographics)}
        Preferences: ${JSON.stringify(userProfile.preferences)}
        
        Content: ${content}
        
        Create variation ${i + 1} that maintains personalization but uses different:
        - Wording and phrasing
        - Structure and flow
        - Examples and references
        - Call-to-action
        
        Make it distinct but equally personalized and effective.
        `;

        const result = await aiService.generateAdvancedContent({
          prompt: variationPrompt,
          model: 'gpt-3.5-turbo',
          temperature: 0.8,
          maxTokens: 800
        });

        variations.push({
          id: `variation_${i + 1}`,
          content: result.content,
          personalizationScore: this.calculatePersonalizationScore([], userProfile),
          differences: this.identifyContentDifferences(content, result.content)
        });
      } catch (error) {
        console.error(`Failed to generate variation ${i + 1}:`, error);
      }
    }

    return variations;
  }

  /**
   * Calculate personalization score
   */
  calculatePersonalizationScore(appliedRules, userProfile) {
    let score = 0;
    const maxScore = 100;

    // Base score from applied rules
    score += appliedRules.length * 10;

    // Bonus for demographic alignment
    if (appliedRules.some(rule => rule.type === 'tone' && rule.condition.includes('age'))) {
      score += 15;
    }

    // Bonus for industry alignment
    if (appliedRules.some(rule => rule.type === 'complexity' && rule.condition.includes('industry'))) {
      score += 15;
    }

    // Bonus for preference alignment
    if (appliedRules.some(rule => rule.type === 'tone' && rule.condition.includes('preference'))) {
      score += 20;
    }

    // Bonus for engagement optimization
    if (appliedRules.some(rule => rule.type === 'engagement')) {
      score += 15;
    }

    // Bonus for AI personalization
    if (appliedRules.some(rule => rule.type === 'ai_personalization')) {
      score += 25;
    }

    return Math.min(maxScore, score);
  }

  /**
   * Generate personalization recommendations
   */
  generatePersonalizationRecommendations(userProfile, appliedRules) {
    const recommendations = [];

    // Check for missing personalization opportunities
    if (!appliedRules.some(rule => rule.type === 'tone')) {
      recommendations.push({
        type: 'tone',
        priority: 'medium',
        message: 'Consider personalizing tone based on user demographics',
        action: 'Adjust tone to match user age and industry'
      });
    }

    if (!appliedRules.some(rule => rule.type === 'engagement')) {
      recommendations.push({
        type: 'engagement',
        priority: 'high',
        message: 'Add engagement elements to increase interaction',
        action: 'Include questions, CTAs, or interactive elements'
      });
    }

    if (!appliedRules.some(rule => rule.type === 'ai_personalization')) {
      recommendations.push({
        type: 'ai_personalization',
        priority: 'high',
        message: 'Use AI to create highly personalized content',
        action: 'Apply AI-powered personalization for better results'
      });
    }

    // Check for optimization opportunities
    if (userProfile.engagement.averageEngagement < 4) {
      recommendations.push({
        type: 'optimization',
        priority: 'high',
        message: 'User has low engagement history - optimize for interaction',
        action: 'Focus on engagement-boosting elements'
      });
    }

    return recommendations;
  }

  /**
   * Helper methods for analysis
   */
  calculateAge(birthDate) {
    if (!birthDate) return null;
    const today = new Date();
    const birth = new Date(birthDate);
    let age = today.getFullYear() - birth.getFullYear();
    const monthDiff = today.getMonth() - birth.getMonth();
    if (monthDiff < 0 || (monthDiff === 0 && today.getDate() < birth.getDate())) {
      age--;
    }
    return age;
  }

  extractPreferredContentTypes(analytics) {
    // This would analyze content performance to determine preferred types
    return ['social_media', 'email', 'blog'];
  }

  extractOptimalPostingTimes(analytics) {
    // This would analyze engagement patterns to determine optimal times
    return ['9:00 AM', '2:00 PM', '7:00 PM'];
  }

  extractPreferredLength(analytics) {
    // This would analyze content performance to determine preferred length
    return 'medium';
  }

  extractInterests(user, analytics) {
    // This would analyze user behavior and content to extract interests
    return ['technology', 'marketing', 'business'];
  }

  analyzePersonality(user, analytics) {
    // This would analyze user behavior to determine personality traits
    return 'analytical';
  }

  analyzeTonePreferences(contentHistory) {
    // Analyze content history to determine tone preferences
    return 'professional';
  }

  analyzeStylePreferences(contentHistory) {
    // Analyze content history to determine style preferences
    return 'conversational';
  }

  analyzeLengthPreferences(contentHistory) {
    // Analyze content history to determine length preferences
    return 'medium';
  }

  analyzeTopicPreferences(contentHistory) {
    // Analyze content history to determine topic preferences
    return ['technology', 'business', 'marketing'];
  }

  analyzeFormatPreferences(contentHistory) {
    // Analyze content history to determine format preferences
    return ['article', 'social_media', 'email'];
  }

  analyzeComplexityPreferences(contentHistory) {
    // Analyze content history to determine complexity preferences
    return 'intermediate';
  }

  analyzeUsagePatterns(analytics) {
    // Analyze usage patterns from analytics
    return {
      frequency: 'daily',
      peakHours: ['9:00 AM', '2:00 PM'],
      preferredDays: ['Monday', 'Wednesday', 'Friday']
    };
  }

  analyzeEngagementPatterns(analytics) {
    // Analyze engagement patterns from analytics
    return {
      averageEngagement: analytics.overview.averageRating || 0,
      engagementTrend: 'increasing',
      preferredContentTypes: ['social_media', 'email']
    };
  }

  analyzeContentPatterns(analytics) {
    // Analyze content patterns from analytics
    return {
      preferredLength: 'medium',
      preferredTone: 'professional',
      preferredStyle: 'conversational'
    };
  }

  analyzeTimePatterns(analytics) {
    // Analyze time patterns from analytics
    return {
      activeHours: ['9:00 AM - 11:00 AM', '2:00 PM - 4:00 PM'],
      activeDays: ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday']
    };
  }

  analyzeDevicePatterns(analytics) {
    // Analyze device patterns from analytics
    return {
      primaryDevice: 'desktop',
      mobileUsage: 0.3,
      tabletUsage: 0.1
    };
  }

  async adjustTone(content, tone) {
    const toneAdjustments = {
      casual: 'Make this content more casual and conversational',
      professional: 'Make this content more professional and formal',
      friendly: 'Make this content more friendly and approachable',
      authoritative: 'Make this content more authoritative and expert'
    };

    const prompt = `${toneAdjustments[tone]}: ${content}`;
    
    try {
      const result = await aiService.generateAdvancedContent({
        prompt,
        model: 'gpt-3.5-turbo',
        temperature: 0.7,
        maxTokens: 500
      });
      return result.content;
    } catch (error) {
      return content;
    }
  }

  async adjustComplexity(content, complexity) {
    const complexityAdjustments = {
      simple: 'Simplify this content for a general audience',
      technical: 'Make this content more technical and detailed',
      intermediate: 'Make this content moderately complex'
    };

    const prompt = `${complexityAdjustments[complexity]}: ${content}`;
    
    try {
      const result = await aiService.generateAdvancedContent({
        prompt,
        model: 'gpt-3.5-turbo',
        temperature: 0.7,
        maxTokens: 500
      });
      return result.content;
    } catch (error) {
      return content;
    }
  }

  async increaseEngagement(content, action) {
    const engagementActions = {
      increase_interaction: 'Add interactive elements like questions, polls, or calls-to-action to increase engagement',
      add_emotional_hooks: 'Add emotional hooks and compelling elements to increase engagement',
      add_urgency: 'Add urgency elements to increase engagement and conversion'
    };

    const prompt = `${engagementActions[action]}: ${content}`;
    
    try {
      const result = await aiService.generateAdvancedContent({
        prompt,
        model: 'gpt-3.5-turbo',
        temperature: 0.7,
        maxTokens: 500
      });
      return result.content;
    } catch (error) {
      return content;
    }
  }

  async adjustLength(content, length, userProfile) {
    const targetLengths = {
      short: 100,
      medium: 300,
      long: 500
    };

    const targetWords = targetLengths[length] || 300;
    const currentWords = content.split(' ').length;

    if (currentWords < targetWords) {
      const prompt = `Expand this content to approximately ${targetWords} words: ${content}`;
      try {
        const result = await aiService.generateAdvancedContent({
          prompt,
          model: 'gpt-3.5-turbo',
          temperature: 0.7,
          maxTokens: 600
        });
        return result.content;
      } catch (error) {
        return content;
      }
    } else if (currentWords > targetWords) {
      const prompt = `Condense this content to approximately ${targetWords} words: ${content}`;
      try {
        const result = await aiService.generateAdvancedContent({
          prompt,
          model: 'gpt-3.5-turbo',
          temperature: 0.7,
          maxTokens: 400
        });
        return result.content;
      } catch (error) {
        return content;
      }
    }

    return content;
  }

  identifyContentDifferences(original, variation) {
    const differences = [];
    
    if (original.length !== variation.length) {
      differences.push('Length changed');
    }
    
    const originalWords = original.split(' ');
    const variationWords = variation.split(' ');
    
    if (originalWords.length !== variationWords.length) {
      differences.push('Word count changed');
    }
    
    return differences;
  }

  async loadPersonalizationRules() {
    // Load personalization rules from database
    console.log('Loading personalization rules...');
  }

  async loadUserProfiles() {
    // Load user profiles from database
    console.log('Loading user profiles...');
  }
}

module.exports = new PersonalizationService();





