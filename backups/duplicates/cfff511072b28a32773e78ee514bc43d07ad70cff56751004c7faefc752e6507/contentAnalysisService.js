const OpenAI = require('openai');

class ContentAnalysisService {
  constructor() {
    this.openai = new OpenAI({
      apiKey: process.env.OPENAI_API_KEY
    });
  }

  async initialize() {
    console.log('Content Analysis Service initialized');
  }

  async analyzeContent(content, options = {}) {
    try {
      const {
        analysisType = 'comprehensive',
        includeSentiment = true,
        includeReadability = true,
        includeSEO = true,
        includeEngagement = true
      } = options;

      const prompt = this.buildAnalysisPrompt(content, {
        analysisType,
        includeSentiment,
        includeReadability,
        includeSEO,
        includeEngagement
      });

      const completion = await this.openai.chat.completions.create({
        model: "gpt-4",
        messages: [
          {
            role: "system",
            content: "You are an expert content analyst with deep knowledge of content marketing, SEO, and audience engagement."
          },
          {
            role: "user",
            content: prompt
          }
        ],
        max_tokens: 2000,
        temperature: 0.3
      });

      const analysis = {
        contentId: options.contentId || Date.now(),
        content: content,
        analysis: completion.choices[0].message.content,
        options: options,
        createdAt: new Date().toISOString()
      };

      return analysis;

    } catch (error) {
      console.error('Error analyzing content:', error);
      throw new Error('Failed to analyze content');
    }
  }

  buildAnalysisPrompt(content, options) {
    const {
      analysisType,
      includeSentiment,
      includeReadability,
      includeSEO,
      includeEngagement
    } = options;

    return `
Analyze the following content with the specified analysis type: ${analysisType}

Content: "${content}"

Please provide a comprehensive analysis including:

${includeSentiment ? '- Sentiment Analysis: Overall tone, emotional impact, brand voice alignment' : ''}
${includeReadability ? '- Readability Analysis: Reading level, clarity, structure, flow' : ''}
${includeSEO ? '- SEO Analysis: Keywords, meta information, search optimization' : ''}
${includeEngagement ? '- Engagement Analysis: Call-to-action effectiveness, audience appeal, shareability' : ''}

Additional analysis:
- Content Quality Score (1-10)
- Strengths and Weaknesses
- Improvement Recommendations
- Target Audience Suitability
- Platform Optimization Suggestions

Format as structured JSON with clear metrics and actionable insights.
    `;
  }

  async compareContent(content1, content2, options = {}) {
    try {
      const prompt = `
Compare the following two pieces of content:

Content 1: "${content1}"
Content 2: "${content2}"

Provide a detailed comparison including:
- Quality comparison
- Engagement potential
- SEO effectiveness
- Brand voice consistency
- Target audience appeal
- Strengths and weaknesses of each
- Recommendations for improvement
- Overall winner and reasoning

Format as structured JSON with clear metrics and actionable insights.
      `;

      const completion = await this.openai.chat.completions.create({
        model: "gpt-4",
        messages: [
          {
            role: "system",
            content: "You are an expert content analyst specializing in content comparison and optimization."
          },
          {
            role: "user",
            content: prompt
          }
        ],
        max_tokens: 2000,
        temperature: 0.3
      });

      const comparison = {
        content1: content1,
        content2: content2,
        comparison: completion.choices[0].message.content,
        options: options,
        createdAt: new Date().toISOString()
      };

      return comparison;

    } catch (error) {
      console.error('Error comparing content:', error);
      throw new Error('Failed to compare content');
    }
  }

  async generateContentInsights(content, options = {}) {
    try {
      const prompt = `
Analyze the following content and generate actionable insights:

Content: "${content}"

Provide insights on:
- Content performance potential
- Audience engagement strategies
- Optimization opportunities
- Content distribution recommendations
- A/B testing suggestions
- Content series potential
- Brand alignment opportunities
- Competitive advantages

Format as structured JSON with clear, actionable insights and recommendations.
      `;

      const completion = await this.openai.chat.completions.create({
        model: "gpt-4",
        messages: [
          {
            role: "system",
            content: "You are a content strategy expert with deep knowledge of content performance and optimization."
          },
          {
            role: "user",
            content: prompt
          }
        ],
        max_tokens: 2000,
        temperature: 0.4
      });

      const insights = {
        contentId: options.contentId || Date.now(),
        content: content,
        insights: completion.choices[0].message.content,
        options: options,
        createdAt: new Date().toISOString()
      };

      return insights;

    } catch (error) {
      console.error('Error generating content insights:', error);
      throw new Error('Failed to generate content insights');
    }
  }
}

module.exports = new ContentAnalysisService();



