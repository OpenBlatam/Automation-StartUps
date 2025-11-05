const express = require('express');
const { body, validationResult } = require('express-validator');
const ContentTemplate = require('../models/ContentTemplate');
const GeneratedContent = require('../models/GeneratedContent');
const aiService = require('../services/aiService');
const router = express.Router();

// Validation middleware
const validateContentGeneration = [
  body('templateId').optional().isMongoId().withMessage('Invalid template ID'),
  body('prompt').notEmpty().withMessage('Prompt is required'),
  body('variables').optional().isObject().withMessage('Variables must be an object'),
  body('model').optional().isIn(['gpt-3.5-turbo', 'gpt-4', 'gpt-4-turbo', 'claude-3-sonnet', 'claude-3-opus']),
  body('temperature').optional().isFloat({ min: 0, max: 2 }),
  body('maxTokens').optional().isInt({ min: 1, max: 4000 })
];

/**
 * @route   POST /api/content/generate
 * @desc    Generate content using AI
 * @access  Private
 */
router.post('/generate', validateContentGeneration, async (req, res) => {
  try {
    // Check validation errors
    const errors = validationResult(req);
    if (!errors.isEmpty()) {
      return res.status(400).json({
        success: false,
        message: 'Validation failed',
        errors: errors.array()
      });
    }

    const { templateId, prompt, variables = {}, model, temperature, maxTokens } = req.body;
    const userId = req.user.id;

    // Check user usage limits
    const user = req.user;
    if (!user.checkUsageLimit()) {
      return res.status(429).json({
        success: false,
        message: 'Monthly usage limit exceeded',
        limit: user.usage.monthlyLimit,
        used: user.usage.contentGenerations
      });
    }

    let template = null;
    let finalPrompt = prompt;

    // If templateId is provided, load template
    if (templateId) {
      template = await ContentTemplate.findById(templateId);
      if (!template) {
        return res.status(404).json({
          success: false,
          message: 'Template not found'
        });
      }

      // Check if user has access to this template
      const userPlan = user.subscription.plan;
      const templatePlan = template.requiredPlan;
      const planHierarchy = { free: 0, basic: 1, professional: 2, enterprise: 3 };
      
      if (planHierarchy[userPlan] < planHierarchy[templatePlan]) {
        return res.status(403).json({
          success: false,
          message: 'Upgrade required to use this template'
        });
      }

      // Use template prompt and settings
      finalPrompt = template.prompt;
      const templateVariables = { ...variables };
      
      // Validate required variables
      for (const variable of template.variables) {
        if (variable.required && !templateVariables[variable.name]) {
          return res.status(400).json({
            success: false,
            message: `Required variable missing: ${variable.name}`
          });
        }
      }
    }

    // Validate AI request
    const validation = aiService.validateRequest({
      prompt: finalPrompt,
      model: model || (template ? template.aiSettings.model : 'gpt-3.5-turbo'),
      temperature: temperature || (template ? template.aiSettings.temperature : 0.7),
      maxTokens: maxTokens || (template ? template.aiSettings.maxTokens : 500)
    });

    if (!validation.isValid) {
      return res.status(400).json({
        success: false,
        message: 'Invalid request parameters',
        errors: validation.errors
      });
    }

    // Generate content
    const result = await aiService.generateContent({
      prompt: finalPrompt,
      systemPrompt: template ? template.aiSettings.systemPrompt : undefined,
      model: model || (template ? template.aiSettings.model : 'gpt-3.5-turbo'),
      temperature: temperature || (template ? template.aiSettings.temperature : 0.7),
      maxTokens: maxTokens || (template ? template.aiSettings.maxTokens : 500),
      variables
    });

    // Save generated content
    const generatedContent = new GeneratedContent({
      userId,
      templateId: template ? template._id : null,
      prompt: finalPrompt,
      variables,
      content: result.content,
      metadata: {
        model: result.model,
        usage: result.usage,
        cost: result.cost,
        timestamp: result.timestamp
      },
      status: 'completed'
    });

    await generatedContent.save();

    // Update user usage
    await user.incrementUsage();

    // Update template usage if applicable
    if (template) {
      await template.incrementUsage(true);
    }

    res.json({
      success: true,
      data: {
        id: generatedContent._id,
        content: result.content,
        metadata: result,
        template: template ? {
          id: template._id,
          name: template.name,
          category: template.category
        } : null
      }
    });

  } catch (error) {
    console.error('Content generation error:', error);
    res.status(500).json({
      success: false,
      message: 'Content generation failed',
      error: process.env.NODE_ENV === 'development' ? error.message : 'Internal server error'
    });
  }
});

/**
 * @route   POST /api/content/generate-variations
 * @desc    Generate multiple content variations
 * @access  Private
 */
router.post('/generate-variations', [
  body('templateId').optional().isMongoId(),
  body('prompt').notEmpty().withMessage('Prompt is required'),
  body('count').optional().isInt({ min: 1, max: 5 }).withMessage('Count must be between 1 and 5'),
  body('variables').optional().isObject()
], async (req, res) => {
  try {
    const errors = validationResult(req);
    if (!errors.isEmpty()) {
      return res.status(400).json({
        success: false,
        message: 'Validation failed',
        errors: errors.array()
      });
    }

    const { templateId, prompt, count = 3, variables = {} } = req.body;
    const userId = req.user.id;

    // Check usage limits (multiply by count)
    const user = req.user;
    const requiredUsage = count;
    if (user.usage.contentGenerations + requiredUsage > user.usage.monthlyLimit) {
      return res.status(429).json({
        success: false,
        message: 'Insufficient usage quota',
        required: requiredUsage,
        available: user.usage.monthlyLimit - user.usage.contentGenerations
      });
    }

    let template = null;
    let finalPrompt = prompt;

    if (templateId) {
      template = await ContentTemplate.findById(templateId);
      if (!template) {
        return res.status(404).json({
          success: false,
          message: 'Template not found'
        });
      }
      finalPrompt = template.prompt;
    }

    // Generate variations
    const variations = await aiService.generateVariations({
      prompt: finalPrompt,
      systemPrompt: template ? template.aiSettings.systemPrompt : undefined,
      model: template ? template.aiSettings.model : 'gpt-3.5-turbo',
      temperature: template ? template.aiSettings.temperature : 0.7,
      maxTokens: template ? template.aiSettings.maxTokens : 500,
      variables,
      count
    });

    // Save all variations
    const savedVariations = [];
    for (const variation of variations) {
      const generatedContent = new GeneratedContent({
        userId,
        templateId: template ? template._id : null,
        prompt: finalPrompt,
        variables,
        content: variation.content,
        metadata: {
          model: variation.model,
          usage: variation.usage,
          cost: variation.cost,
          timestamp: variation.timestamp,
          variation: variation.variation
        },
        status: 'completed'
      });

      await generatedContent.save();
      savedVariations.push(generatedContent);
    }

    // Update user usage
    user.usage.contentGenerations += count;
    await user.save();

    // Update template usage if applicable
    if (template) {
      template.usage.totalUses += count;
      template.usage.successfulGenerations += variations.length;
      await template.save();
    }

    res.json({
      success: true,
      data: {
        variations: savedVariations.map(v => ({
          id: v._id,
          content: v.content,
          metadata: v.metadata
        })),
        count: variations.length
      }
    });

  } catch (error) {
    console.error('Variations generation error:', error);
    res.status(500).json({
      success: false,
      message: 'Variations generation failed',
      error: process.env.NODE_ENV === 'development' ? error.message : 'Internal server error'
    });
  }
});

/**
 * @route   POST /api/content/optimize
 * @desc    Optimize existing content
 * @access  Private
 */
router.post('/optimize', [
  body('content').notEmpty().withMessage('Content is required'),
  body('goal').isIn(['seo', 'conversion', 'engagement', 'clarity', 'creativity']).withMessage('Invalid optimization goal'),
  body('model').optional().isIn(['gpt-3.5-turbo', 'gpt-4', 'gpt-4-turbo'])
], async (req, res) => {
  try {
    const errors = validationResult(req);
    if (!errors.isEmpty()) {
      return res.status(400).json({
        success: false,
        message: 'Validation failed',
        errors: errors.array()
      });
    }

    const { content, goal, model = 'gpt-3.5-turbo' } = req.body;
    const userId = req.user.id;

    // Check usage limits
    const user = req.user;
    if (!user.checkUsageLimit()) {
      return res.status(429).json({
        success: false,
        message: 'Monthly usage limit exceeded'
      });
    }

    // Optimize content
    const result = await aiService.optimizeContent(content, goal, { model });

    // Save optimized content
    const generatedContent = new GeneratedContent({
      userId,
      prompt: `Optimize for ${goal}`,
      content: result.content,
      metadata: {
        model: result.model,
        usage: result.usage,
        cost: result.cost,
        timestamp: result.timestamp,
        optimizationGoal: goal,
        originalContent: content
      },
      status: 'completed'
    });

    await generatedContent.save();
    await user.incrementUsage();

    res.json({
      success: true,
      data: {
        id: generatedContent._id,
        originalContent: content,
        optimizedContent: result.content,
        goal,
        metadata: result
      }
    });

  } catch (error) {
    console.error('Content optimization error:', error);
    res.status(500).json({
      success: false,
      message: 'Content optimization failed',
      error: process.env.NODE_ENV === 'development' ? error.message : 'Internal server error'
    });
  }
});

/**
 * @route   POST /api/content/analyze
 * @desc    Analyze content performance
 * @access  Private
 */
router.post('/analyze', [
  body('content').notEmpty().withMessage('Content is required'),
  body('type').optional().isIn(['email', 'social', 'blog', 'ad', 'general'])
], async (req, res) => {
  try {
    const errors = validationResult(req);
    if (!errors.isEmpty()) {
      return res.status(400).json({
        success: false,
        message: 'Validation failed',
        errors: errors.array()
      });
    }

    const { content, type = 'general' } = req.body;

    // Analyze content
    const result = await aiService.analyzeContent(content, type);

    res.json({
      success: true,
      data: {
        analysis: result.content,
        type,
        metadata: result
      }
    });

  } catch (error) {
    console.error('Content analysis error:', error);
    res.status(500).json({
      success: false,
      message: 'Content analysis failed',
      error: process.env.NODE_ENV === 'development' ? error.message : 'Internal server error'
    });
  }
});

/**
 * @route   POST /api/content/ideas
 * @desc    Generate content ideas
 * @access  Private
 */
router.post('/ideas', [
  body('topic').notEmpty().withMessage('Topic is required'),
  body('type').optional().isIn(['email', 'social', 'blog', 'ad', 'general']),
  body('count').optional().isInt({ min: 1, max: 20 })
], async (req, res) => {
  try {
    const errors = validationResult(req);
    if (!errors.isEmpty()) {
      return res.status(400).json({
        success: false,
        message: 'Validation failed',
        errors: errors.array()
      });
    }

    const { topic, type = 'general', count = 10 } = req.body;

    // Generate ideas
    const ideas = await aiService.generateContentIdeas(topic, type, count);

    res.json({
      success: true,
      data: {
        ideas,
        topic,
        type,
        count: ideas.length
      }
    });

  } catch (error) {
    console.error('Content ideas generation error:', error);
    res.status(500).json({
      success: false,
      message: 'Content ideas generation failed',
      error: process.env.NODE_ENV === 'development' ? error.message : 'Internal server error'
    });
  }
});

/**
 * @route   GET /api/content/history
 * @desc    Get user's content generation history
 * @access  Private
 */
router.get('/history', async (req, res) => {
  try {
    const { page = 1, limit = 20, category, templateId } = req.query;
    const userId = req.user.id;

    const query = { userId, status: 'completed' };
    
    if (category) {
      query['template.category'] = category;
    }
    
    if (templateId) {
      query.templateId = templateId;
    }

    const skip = (page - 1) * limit;
    
    const content = await GeneratedContent.find(query)
      .populate('templateId', 'name category')
      .sort({ createdAt: -1 })
      .skip(skip)
      .limit(parseInt(limit));

    const total = await GeneratedContent.countDocuments(query);

    res.json({
      success: true,
      data: {
        content,
        pagination: {
          page: parseInt(page),
          limit: parseInt(limit),
          total,
          pages: Math.ceil(total / limit)
        }
      }
    });

  } catch (error) {
    console.error('Content history error:', error);
    res.status(500).json({
      success: false,
      message: 'Failed to fetch content history',
      error: process.env.NODE_ENV === 'development' ? error.message : 'Internal server error'
    });
  }
});

/**
 * @route   GET /api/content/:id
 * @desc    Get specific generated content
 * @access  Private
 */
router.get('/:id', async (req, res) => {
  try {
    const { id } = req.params;
    const userId = req.user.id;

    const content = await GeneratedContent.findOne({ _id: id, userId })
      .populate('templateId', 'name category description');

    if (!content) {
      return res.status(404).json({
        success: false,
        message: 'Content not found'
      });
    }

    res.json({
      success: true,
      data: content
    });

  } catch (error) {
    console.error('Get content error:', error);
    res.status(500).json({
      success: false,
      message: 'Failed to fetch content',
      error: process.env.NODE_ENV === 'development' ? error.message : 'Internal server error'
    });
  }
});

/**
 * @route   DELETE /api/content/:id
 * @desc    Delete generated content
 * @access  Private
 */
router.delete('/:id', async (req, res) => {
  try {
    const { id } = req.params;
    const userId = req.user.id;

    const content = await GeneratedContent.findOneAndDelete({ _id: id, userId });

    if (!content) {
      return res.status(404).json({
        success: false,
        message: 'Content not found'
      });
    }

    res.json({
      success: true,
      message: 'Content deleted successfully'
    });

  } catch (error) {
    console.error('Delete content error:', error);
    res.status(500).json({
      success: false,
      message: 'Failed to delete content',
      error: process.env.NODE_ENV === 'development' ? error.message : 'Internal server error'
    });
  }
});

module.exports = router;









