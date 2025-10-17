const OpenAI = require('openai');
const { v4: uuidv4 } = require('uuid');

class MultimediaContentService {
  constructor() {
    this.openai = new OpenAI({
      apiKey: process.env.OPENAI_API_KEY
    });
    this.content = new Map();
  }

  async initialize() {
    console.log('Multimedia Content Service initialized');
  }

  async generateVideoScript(content, options = {}) {
    try {
      const {
        videoType = 'educational',
        duration = '2-3 minutes',
        targetAudience = 'general',
        tone = 'professional',
        includeCallToAction = true
      } = options;

      const prompt = this.buildVideoScriptPrompt(content, {
        videoType,
        duration,
        targetAudience,
        tone,
        includeCallToAction
      });

      const completion = await this.openai.chat.completions.create({
        model: "gpt-4",
        messages: [
          {
            role: "system",
            content: "You are an expert video script writer with 10+ years of experience in creating engaging, conversion-focused video content for marketing and education."
          },
          {
            role: "user",
            content: prompt
          }
        ],
        max_tokens: 2000,
        temperature: 0.7
      });

      const script = {
        scriptId: uuidv4(),
        content: content,
        script: completion.choices[0].message.content,
        options: options,
        createdAt: new Date().toISOString(),
        status: 'active'
      };

      this.content.set(script.scriptId, script);
      return script;

    } catch (error) {
      console.error('Error generating video script:', error);
      throw new Error('Failed to generate video script');
    }
  }

  buildVideoScriptPrompt(content, options) {
    const {
      videoType,
      duration,
      targetAudience,
      tone,
      includeCallToAction
    } = options;

    return `
Create a professional video script based on the following content:

Content: "${content}"

Video Specifications:
- Video Type: ${videoType}
- Duration: ${duration}
- Target Audience: ${targetAudience}
- Tone: ${tone}
- Include Call to Action: ${includeCallToAction}

Please provide a detailed video script that includes:

1. HOOK (0-10 seconds)
   - Attention-grabbing opening
   - Problem statement or question
   - Value proposition preview

2. INTRODUCTION (10-30 seconds)
   - Brief introduction
   - Credibility establishment
   - What viewers will learn

3. MAIN CONTENT (30 seconds - 2 minutes)
   - Key points and information
   - Examples and case studies
   - Visual cues and transitions

4. CONCLUSION (2-3 minutes)
   - Summary of key points
   - Key takeaways
   - Next steps

${includeCallToAction ? '5. CALL TO ACTION\n   - Clear action step\n   - Contact information\n   - Follow-up instructions' : ''}

Additional Elements:
- Visual cues and transitions
- Timing suggestions
- Engagement techniques
- Brand voice guidelines

Format as a structured script with clear timing, dialogue, and visual cues.
    `;
  }

  async generatePodcastScript(content, options = {}) {
    try {
      const {
        podcastType = 'interview',
        duration = '20-30 minutes',
        hostStyle = 'conversational',
        includeIntro = true,
        includeOutro = true
      } = options;

      const prompt = this.buildPodcastScriptPrompt(content, {
        podcastType,
        duration,
        hostStyle,
        includeIntro,
        includeOutro
      });

      const completion = await this.openai.chat.completions.create({
        model: "gpt-4",
        messages: [
          {
            role: "system",
            content: "You are an expert podcast script writer with extensive experience in creating engaging, conversational podcast content that drives audience engagement and business results."
          },
          {
            role: "user",
            content: prompt
          }
        ],
        max_tokens: 2500,
        temperature: 0.6
      });

      const script = {
        scriptId: uuidv4(),
        content: content,
        script: completion.choices[0].message.content,
        options: options,
        createdAt: new Date().toISOString(),
        status: 'active'
      };

      this.content.set(script.scriptId, script);
      return script;

    } catch (error) {
      console.error('Error generating podcast script:', error);
      throw new Error('Failed to generate podcast script');
    }
  }

  buildPodcastScriptPrompt(content, options) {
    const {
      podcastType,
      duration,
      hostStyle,
      includeIntro,
      includeOutro
    } = options;

    return `
Create a professional podcast script based on the following content:

Content: "${content}"

Podcast Specifications:
- Podcast Type: ${podcastType}
- Duration: ${duration}
- Host Style: ${hostStyle}
- Include Intro: ${includeIntro}
- Include Outro: ${includeOutro}

Please provide a detailed podcast script that includes:

${includeIntro ? '1. INTRODUCTION\n   - Podcast intro and branding\n   - Host introduction\n   - Episode overview\n   - What listeners will learn' : ''}

2. MAIN CONTENT
   - Key discussion points
   - Questions and answers
   - Examples and case studies
   - Audience engagement techniques

3. TRANSITIONS
   - Smooth topic transitions
   - Segue techniques
   - Engagement hooks

${includeOutro ? '4. CONCLUSION\n   - Key takeaways summary\n   - Call to action\n   - Next episode preview\n   - Contact information' : ''}

Additional Elements:
- Timing suggestions
- Engagement techniques
- Brand voice guidelines
- Audience interaction prompts

Format as a conversational script with clear dialogue, timing, and engagement elements.
    `;
  }

  async generateInfographicContent(content, options = {}) {
    try {
      const {
        infographicType = 'educational',
        targetAudience = 'general',
        includeStatistics = true,
        includeVisualElements = true,
        colorScheme = 'professional'
      } = options;

      const prompt = this.buildInfographicPrompt(content, {
        infographicType,
        targetAudience,
        includeStatistics,
        includeVisualElements,
        colorScheme
      });

      const completion = await this.openai.chat.completions.create({
        model: "gpt-4",
        messages: [
          {
            role: "system",
            content: "You are an expert infographic designer with deep knowledge of visual communication, data visualization, and design principles that drive engagement and understanding."
          },
          {
            role: "user",
            content: prompt
          }
        ],
        max_tokens: 2000,
        temperature: 0.5
      });

      const infographic = {
        infographicId: uuidv4(),
        content: content,
        design: completion.choices[0].message.content,
        options: options,
        createdAt: new Date().toISOString(),
        status: 'active'
      };

      this.content.set(infographic.infographicId, infographic);
      return infographic;

    } catch (error) {
      console.error('Error generating infographic content:', error);
      throw new Error('Failed to generate infographic content');
    }
  }

  buildInfographicPrompt(content, options) {
    const {
      infographicType,
      targetAudience,
      includeStatistics,
      includeVisualElements,
      colorScheme
    } = options;

    return `
Create a comprehensive infographic design based on the following content:

Content: "${content}"

Infographic Specifications:
- Type: ${infographicType}
- Target Audience: ${targetAudience}
- Include Statistics: ${includeStatistics}
- Include Visual Elements: ${includeVisualElements}
- Color Scheme: ${colorScheme}

Please provide a detailed infographic design that includes:

1. LAYOUT STRUCTURE
   - Header and title design
   - Section organization
   - Visual hierarchy
   - Flow and navigation

2. CONTENT ELEMENTS
   - Key information points
   - Data visualization
   - Text and typography
   - Visual storytelling

3. DESIGN ELEMENTS
   - Color palette
   - Typography choices
   - Icon and graphic suggestions
   - Visual style guidelines

4. DATA VISUALIZATION
   - Chart and graph suggestions
   - Statistics presentation
   - Comparison elements
   - Trend indicators

5. ENGAGEMENT FEATURES
   - Interactive elements
   - Call-to-action placement
   - Social sharing optimization
   - Brand integration

Format as a structured design brief with specific recommendations for layout, content, and visual elements.
    `;
  }

  async generateSocialMediaContent(content, options = {}) {
    try {
      const {
        platform = 'facebook',
        contentType = 'post',
        targetAudience = 'general',
        includeHashtags = true,
        includeCallToAction = true
      } = options;

      const prompt = this.buildSocialMediaPrompt(content, {
        platform,
        contentType,
        targetAudience,
        includeHashtags,
        includeCallToAction
      });

      const completion = await this.openai.chat.completions.create({
        model: "gpt-4",
        messages: [
          {
            role: "system",
            content: "You are an expert social media content creator with deep knowledge of platform-specific best practices, audience engagement, and viral content strategies."
          },
          {
            role: "user",
            content: prompt
          }
        ],
        max_tokens: 1500,
        temperature: 0.7
      });

      const socialContent = {
        contentId: uuidv4(),
        content: content,
        socialContent: completion.choices[0].message.content,
        options: options,
        createdAt: new Date().toISOString(),
        status: 'active'
      };

      this.content.set(socialContent.contentId, socialContent);
      return socialContent;

    } catch (error) {
      console.error('Error generating social media content:', error);
      throw new Error('Failed to generate social media content');
    }
  }

  buildSocialMediaPrompt(content, options) {
    const {
      platform,
      contentType,
      targetAudience,
      includeHashtags,
      includeCallToAction
    } = options;

    return `
Create engaging social media content based on the following content:

Content: "${content}"

Social Media Specifications:
- Platform: ${platform}
- Content Type: ${contentType}
- Target Audience: ${targetAudience}
- Include Hashtags: ${includeHashtags}
- Include Call to Action: ${includeCallToAction}

Please provide platform-optimized content that includes:

1. CONTENT CREATION
   - Engaging headline/title
   - Compelling copy
   - Visual suggestions
   - Engagement hooks

2. PLATFORM OPTIMIZATION
   - Character count optimization
   - Format-specific formatting
   - Visual element suggestions
   - Timing recommendations

${includeHashtags ? '3. HASHTAG STRATEGY\n   - Relevant hashtags\n   - Trending tags\n   - Brand hashtags\n   - Hashtag research' : ''}

${includeCallToAction ? '4. CALL TO ACTION\n   - Clear action step\n   - Engagement prompts\n   - Link placement\n   - Follow-up strategy' : ''}

5. ENGAGEMENT STRATEGY
   - Audience interaction
   - Comment prompts
   - Share optimization
   - Community building

Format as platform-specific content with clear copy, visual suggestions, and engagement strategies.
    `;
  }

  getContent(contentId) {
    return this.content.get(contentId);
  }

  getUserContent(userId) {
    return Array.from(this.content.values())
      .filter(content => content.userId === userId);
  }

  updateContent(contentId, updates) {
    const content = this.content.get(contentId);
    if (content) {
      const updatedContent = { ...content, ...updates, updatedAt: new Date().toISOString() };
      this.content.set(contentId, updatedContent);
      return updatedContent;
    }
    return null;
  }

  deleteContent(contentId) {
    return this.content.delete(contentId);
  }
}

module.exports = new MultimediaContentService();