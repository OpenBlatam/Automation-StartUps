import OpenAI from 'openai';
import { ContentType } from '@prisma/client';
import { logger } from '../utils/logger';

const openai = new OpenAI({
  apiKey: process.env.OPENAI_API_KEY,
});

export interface ContentGenerationRequest {
  type: ContentType;
  prompt: string;
  tone?: string;
  length?: string;
  targetAudience?: string;
  brandVoice?: string;
  keywords?: string[];
}

export interface ContentGenerationResponse {
  content: string;
  tokensUsed: number;
  cost: number;
}

export class ContentService {
  private static readonly PRICING_PER_1K_TOKENS = 0.002; // GPT-4 pricing

  private static getSystemPrompt(type: ContentType, options: Partial<ContentGenerationRequest>): string {
    const basePrompts = {
      [ContentType.BLOG_POST]: `You are an expert content writer specializing in blog posts. Create engaging, SEO-optimized blog content that provides value to readers.`,
      [ContentType.EMAIL]: `You are an expert email marketer. Create compelling email content that drives engagement and conversions.`,
      [ContentType.SOCIAL_MEDIA]: `You are a social media expert. Create engaging social media content that resonates with your audience and drives engagement.`,
      [ContentType.AD_COPY]: `You are a professional copywriter specializing in advertising. Create persuasive ad copy that converts.`,
      [ContentType.PRODUCT_DESCRIPTION]: `You are a product marketing expert. Create compelling product descriptions that highlight benefits and drive sales.`,
      [ContentType.LANDING_PAGE]: `You are a conversion optimization expert. Create high-converting landing page copy.`,
      [ContentType.SALES_PAGE]: `You are a sales copywriting expert. Create persuasive sales page content that converts visitors into customers.`,
      [ContentType.EMAIL_SEQUENCE]: `You are an email marketing automation expert. Create effective email sequences that nurture leads and drive conversions.`,
      [ContentType.WEBSITE_COPY]: `You are a web copywriting expert. Create clear, compelling website copy that communicates your value proposition effectively.`,
      [ContentType.OTHER]: `You are a professional content writer. Create high-quality content based on the user's requirements.`,
    };

    let systemPrompt = basePrompts[type] || basePrompts[ContentType.OTHER];

    if (options.tone) {
      systemPrompt += ` Use a ${options.tone} tone.`;
    }

    if (options.targetAudience) {
      systemPrompt += ` Target audience: ${options.targetAudience}.`;
    }

    if (options.brandVoice) {
      systemPrompt += ` Brand voice: ${options.brandVoice}.`;
    }

    if (options.keywords && options.keywords.length > 0) {
      systemPrompt += ` Include these keywords naturally: ${options.keywords.join(', ')}.`;
    }

    return systemPrompt;
  }

  private static getLengthInstruction(length?: string): string {
    const lengthMap = {
      'short': 'Keep it concise (50-100 words)',
      'medium': 'Write a medium-length piece (200-400 words)',
      'long': 'Write a comprehensive piece (500+ words)',
    };

    return lengthMap[length as keyof typeof lengthMap] || 'Write an appropriate length piece.';
  }

  static async generateContent(request: ContentGenerationRequest): Promise<ContentGenerationResponse> {
    try {
      const systemPrompt = this.getSystemPrompt(request.type, request);
      const lengthInstruction = this.getLengthInstruction(request.length);

      const messages = [
        {
          role: 'system' as const,
          content: systemPrompt,
        },
        {
          role: 'user' as const,
          content: `${request.prompt}\n\n${lengthInstruction}`,
        },
      ];

      const completion = await openai.chat.completions.create({
        model: 'gpt-4',
        messages,
        max_tokens: 2000,
        temperature: 0.7,
      });

      const content = completion.choices[0]?.message?.content || '';
      const tokensUsed = completion.usage?.total_tokens || 0;
      const cost = (tokensUsed / 1000) * this.PRICING_PER_1K_TOKENS;

      logger.info(`Content generated successfully. Tokens used: ${tokensUsed}, Cost: $${cost.toFixed(4)}`);

      return {
        content,
        tokensUsed,
        cost,
      };
    } catch (error) {
      logger.error('Error generating content:', error);
      throw new Error('Failed to generate content');
    }
  }

  static async generateMultipleVariations(
    request: ContentGenerationRequest,
    count: number = 3
  ): Promise<ContentGenerationResponse[]> {
    const variations: ContentGenerationResponse[] = [];

    for (let i = 0; i < count; i++) {
      try {
        const variation = await this.generateContent({
          ...request,
          prompt: `${request.prompt}\n\nGenerate variation ${i + 1} with a different approach.`,
        });
        variations.push(variation);
      } catch (error) {
        logger.error(`Error generating variation ${i + 1}:`, error);
      }
    }

    return variations;
  }

  static async improveContent(
    content: string,
    improvements: string[]
  ): Promise<ContentGenerationResponse> {
    try {
      const systemPrompt = `You are an expert content editor. Improve the provided content based on the specific feedback and requirements.`;

      const messages = [
        {
          role: 'system' as const,
          content: systemPrompt,
        },
        {
          role: 'user' as const,
          content: `Please improve this content:\n\n"${content}"\n\nImprovements needed:\n${improvements.join('\n')}`,
        },
      ];

      const completion = await openai.chat.completions.create({
        model: 'gpt-4',
        messages,
        max_tokens: 2000,
        temperature: 0.7,
      });

      const improvedContent = completion.choices[0]?.message?.content || '';
      const tokensUsed = completion.usage?.total_tokens || 0;
      const cost = (tokensUsed / 1000) * this.PRICING_PER_1K_TOKENS;

      return {
        content: improvedContent,
        tokensUsed,
        cost,
      };
    } catch (error) {
      logger.error('Error improving content:', error);
      throw new Error('Failed to improve content');
    }
  }
}

