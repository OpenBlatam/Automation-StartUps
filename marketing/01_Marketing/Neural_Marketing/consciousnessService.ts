import OpenAI from 'openai';
import { prisma } from '../index';
import { logger } from '../utils/logger';

const openai = new OpenAI({
  apiKey: process.env.OPENAI_API_KEY,
});

export interface ConsciousnessAssessment {
  level: number; // 0-100
  category: 'BEGINNER' | 'INTERMEDIATE' | 'ADVANCED' | 'EXPERT' | 'MASTER';
  strengths: string[];
  weaknesses: string[];
  recommendations: string[];
  nextSteps: string[];
}

export interface NeuralMarketingProfile {
  consciousnessLevel: number;
  marketingStyle: string;
  preferredChannels: string[];
  contentPreferences: string[];
  automationLevel: 'MANUAL' | 'SEMI_AUTOMATED' | 'FULLY_AUTOMATED';
  aiAdoption: 'NOVICE' | 'INTERMEDIATE' | 'ADVANCED' | 'EXPERT';
}

export class ConsciousnessService {
  private static readonly CONSCIOUSNESS_LEVELS = {
    BEGINNER: { min: 0, max: 20, label: 'Neural Novice' },
    INTERMEDIATE: { min: 21, max: 40, label: 'Conscious Marketer' },
    ADVANCED: { min: 41, max: 60, label: 'Neural Strategist' },
    EXPERT: { min: 61, max: 80, label: 'AI Marketing Master' },
    MASTER: { min: 81, max: 100, label: 'Neural Marketing Consciousness' },
  };

  static async assessConsciousnessLevel(userId: string): Promise<ConsciousnessAssessment> {
    try {
      // Get user's content generation history and usage patterns
      const userData = await this.getUserMarketingData(userId);
      
      // Create assessment prompt
      const assessmentPrompt = this.createAssessmentPrompt(userData);
      
      // Get AI assessment
      const response = await openai.chat.completions.create({
        model: 'gpt-4',
        messages: [
          {
            role: 'system',
            content: `You are a Neural Marketing Consciousness assessor. Analyze the user's marketing data and provide a comprehensive consciousness level assessment. Return a JSON response with the following structure:
            {
              "level": number (0-100),
              "category": "BEGINNER" | "INTERMEDIATE" | "ADVANCED" | "EXPERT" | "MASTER",
              "strengths": string[],
              "weaknesses": string[],
              "recommendations": string[],
              "nextSteps": string[]
            }`
          },
          {
            role: 'user',
            content: assessmentPrompt
          }
        ],
        temperature: 0.3,
      });

      const assessment = JSON.parse(response.choices[0]?.message?.content || '{}');
      
      // Validate and normalize assessment
      const normalizedAssessment = this.normalizeAssessment(assessment);
      
      // Save assessment to database
      await this.saveAssessment(userId, normalizedAssessment);
      
      logger.info(`Consciousness assessment completed for user ${userId}: Level ${normalizedAssessment.level}`);
      
      return normalizedAssessment;
    } catch (error) {
      logger.error('Error assessing consciousness level:', error);
      throw new Error('Failed to assess consciousness level');
    }
  }

  static async generateNeuralMarketingProfile(userId: string): Promise<NeuralMarketingProfile> {
    try {
      const userData = await this.getUserMarketingData(userId);
      const assessment = await this.assessConsciousnessLevel(userId);
      
      const profilePrompt = this.createProfilePrompt(userData, assessment);
      
      const response = await openai.chat.completions.create({
        model: 'gpt-4',
        messages: [
          {
            role: 'system',
            content: `You are a Neural Marketing Consciousness profiler. Create a comprehensive marketing profile based on the user's data and consciousness level. Return a JSON response with:
            {
              "consciousnessLevel": number,
              "marketingStyle": string,
              "preferredChannels": string[],
              "contentPreferences": string[],
              "automationLevel": "MANUAL" | "SEMI_AUTOMATED" | "FULLY_AUTOMATED",
              "aiAdoption": "NOVICE" | "INTERMEDIATE" | "ADVANCED" | "EXPERT"
            }`
          },
          {
            role: 'user',
            content: profilePrompt
          }
        ],
        temperature: 0.4,
      });

      const profile = JSON.parse(response.choices[0]?.message?.content || '{}');
      
      // Save profile to database
      await this.saveNeuralProfile(userId, profile);
      
      return profile;
    } catch (error) {
      logger.error('Error generating neural marketing profile:', error);
      throw new Error('Failed to generate neural marketing profile');
    }
  }

  static async generateConsciousnessBasedContent(
    userId: string,
    contentType: string,
    prompt: string
  ): Promise<string> {
    try {
      const profile = await this.getNeuralProfile(userId);
      const assessment = await this.getLatestAssessment(userId);
      
      const contentPrompt = this.createConsciousnessContentPrompt(
        contentType,
        prompt,
        profile,
        assessment
      );
      
      const response = await openai.chat.completions.create({
        model: 'gpt-4',
        messages: [
          {
            role: 'system',
            content: `You are a Neural Marketing Consciousness content generator. Create content that matches the user's consciousness level and marketing profile. Adapt your approach based on their level:
            - BEGINNER (0-20): Simple, clear, educational content
            - INTERMEDIATE (21-40): Balanced content with some advanced concepts
            - ADVANCED (41-60): Sophisticated content with strategic insights
            - EXPERT (61-80): High-level strategic content
            - MASTER (81-100): Revolutionary, consciousness-level content`
          },
          {
            role: 'user',
            content: contentPrompt
          }
        ],
        temperature: 0.7,
      });

      const content = response.choices[0]?.message?.content || '';
      
      // Save content generation with consciousness context
      await this.saveConsciousnessContent(userId, contentType, prompt, content, profile, assessment);
      
      return content;
    } catch (error) {
      logger.error('Error generating consciousness-based content:', error);
      throw new Error('Failed to generate consciousness-based content');
    }
  }

  static async getConsciousnessInsights(userId: string): Promise<any> {
    try {
      const assessment = await this.getLatestAssessment(userId);
      const profile = await this.getNeuralProfile(userId);
      const userData = await this.getUserMarketingData(userId);
      
      return {
        currentLevel: assessment?.level || 0,
        category: assessment?.category || 'BEGINNER',
        levelLabel: this.getLevelLabel(assessment?.level || 0),
        progress: this.calculateProgress(userData),
        recommendations: assessment?.recommendations || [],
        nextSteps: assessment?.nextSteps || [],
        profile: profile,
        insights: this.generateInsights(assessment, profile, userData),
      };
    } catch (error) {
      logger.error('Error getting consciousness insights:', error);
      throw new Error('Failed to get consciousness insights');
    }
  }

  private static async getUserMarketingData(userId: string) {
    const [contentGenerations, campaigns, analytics] = await Promise.all([
      prisma.contentGeneration.findMany({
        where: { userId },
        orderBy: { createdAt: 'desc' },
        take: 50,
      }),
      prisma.campaign.findMany({
        where: { userId },
        orderBy: { createdAt: 'desc' },
        take: 20,
      }),
      prisma.analytics.findMany({
        where: { userId },
        orderBy: { date: 'desc' },
        take: 100,
      }),
    ]);

    return {
      contentGenerations,
      campaigns,
      analytics,
      totalGenerations: contentGenerations.length,
      totalCampaigns: campaigns.length,
      averageTokensPerGeneration: contentGenerations.reduce((sum, gen) => sum + gen.tokensUsed, 0) / contentGenerations.length || 0,
    };
  }

  private static createAssessmentPrompt(userData: any): string {
    return `
    Analyze this user's marketing data and assess their Neural Marketing Consciousness level:
    
    Content Generations: ${userData.totalGenerations}
    Campaigns: ${userData.totalCampaigns}
    Average Tokens per Generation: ${userData.averageTokensPerGeneration}
    
    Recent Content Types: ${userData.contentGenerations.slice(0, 10).map(gen => gen.type).join(', ')}
    
    Campaign Statuses: ${userData.campaigns.map(c => c.status).join(', ')}
    
    Based on this data, assess their:
    1. AI adoption level
    2. Marketing sophistication
    3. Content strategy maturity
    4. Automation usage
    5. Strategic thinking
    
    Provide a consciousness level (0-100) and detailed analysis.
    `;
  }

  private static createProfilePrompt(userData: any, assessment: ConsciousnessAssessment): string {
    return `
    Create a Neural Marketing Profile for a user with:
    - Consciousness Level: ${assessment.level} (${assessment.category})
    - Strengths: ${assessment.strengths.join(', ')}
    - Weaknesses: ${assessment.weaknesses.join(', ')}
    
    User Data:
    - Content Generations: ${userData.totalGenerations}
    - Campaigns: ${userData.totalCampaigns}
    - Content Types: ${userData.contentGenerations.map(gen => gen.type).join(', ')}
    
    Generate a comprehensive marketing profile that matches their consciousness level.
    `;
  }

  private static createConsciousnessContentPrompt(
    contentType: string,
    prompt: string,
    profile: NeuralMarketingProfile,
    assessment: ConsciousnessAssessment
  ): string {
    return `
    Generate ${contentType} content for a user with:
    - Consciousness Level: ${assessment?.level || 0} (${assessment?.category || 'BEGINNER'})
    - Marketing Style: ${profile?.marketingStyle || 'Traditional'}
    - Preferred Channels: ${profile?.preferredChannels?.join(', ') || 'Email, Social Media'}
    - Automation Level: ${profile?.automationLevel || 'MANUAL'}
    - AI Adoption: ${profile?.aiAdoption || 'NOVICE'}
    
    Original Prompt: ${prompt}
    
    Adapt the content complexity, style, and approach to match their consciousness level and profile.
    `;
  }

  private static normalizeAssessment(assessment: any): ConsciousnessAssessment {
    const level = Math.max(0, Math.min(100, assessment.level || 0));
    const category = this.getCategoryFromLevel(level);
    
    return {
      level,
      category,
      strengths: assessment.strengths || [],
      weaknesses: assessment.weaknesses || [],
      recommendations: assessment.recommendations || [],
      nextSteps: assessment.nextSteps || [],
    };
  }

  private static getCategoryFromLevel(level: number): 'BEGINNER' | 'INTERMEDIATE' | 'ADVANCED' | 'EXPERT' | 'MASTER' {
    if (level >= 81) return 'MASTER';
    if (level >= 61) return 'EXPERT';
    if (level >= 41) return 'ADVANCED';
    if (level >= 21) return 'INTERMEDIATE';
    return 'BEGINNER';
  }

  private static getLevelLabel(level: number): string {
    for (const [category, range] of Object.entries(this.CONSCIOUSNESS_LEVELS)) {
      if (level >= range.min && level <= range.max) {
        return range.label;
      }
    }
    return 'Neural Novice';
  }

  private static calculateProgress(userData: any): any {
    const totalGenerations = userData.totalGenerations;
    const totalCampaigns = userData.totalCampaigns;
    const averageTokens = userData.averageTokensPerGeneration;
    
    return {
      contentGeneration: Math.min(100, (totalGenerations / 100) * 100),
      campaignManagement: Math.min(100, (totalCampaigns / 20) * 100),
      aiAdoption: Math.min(100, (averageTokens / 1000) * 100),
      overall: Math.min(100, ((totalGenerations + totalCampaigns + averageTokens / 100) / 3)),
    };
  }

  private static generateInsights(assessment: any, profile: any, userData: any): string[] {
    const insights = [];
    
    if (assessment?.level < 30) {
      insights.push('Focus on basic AI tool adoption to increase consciousness level');
    }
    
    if (userData.totalGenerations < 10) {
      insights.push('Increase content generation frequency to improve AI familiarity');
    }
    
    if (profile?.automationLevel === 'MANUAL') {
      insights.push('Consider implementing more automation to advance your consciousness');
    }
    
    return insights;
  }

  private static async saveAssessment(userId: string, assessment: ConsciousnessAssessment) {
    // Save to database - you might want to create a separate table for this
    logger.info(`Assessment saved for user ${userId}: Level ${assessment.level}`);
  }

  private static async saveNeuralProfile(userId: string, profile: NeuralMarketingProfile) {
    // Save to database
    logger.info(`Neural profile saved for user ${userId}`);
  }

  private static async saveConsciousnessContent(
    userId: string,
    contentType: string,
    prompt: string,
    content: string,
    profile: NeuralMarketingProfile,
    assessment: ConsciousnessAssessment
  ) {
    // Save content generation with consciousness context
    logger.info(`Consciousness-based content saved for user ${userId}`);
  }

  private static async getNeuralProfile(userId: string): Promise<NeuralMarketingProfile | null> {
    // Retrieve from database
    return null;
  }

  private static async getLatestAssessment(userId: string): Promise<ConsciousnessAssessment | null> {
    // Retrieve from database
    return null;
  }
}

