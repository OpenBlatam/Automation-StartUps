const express = require('express');
const router = express.Router();
const auth = require('../middleware/auth');
const aiOptimizationService = require('../services/aiOptimizationService');
const { body, validationResult } = require('express-validator');

// Initialize AI optimization service
aiOptimizationService.initialize();

/**
 * @route   POST /api/optimization/optimize
 * @desc    Optimize content for specific goals
 * @access  Private
 */
router.post('/optimize', auth, [
  body('content').notEmpty().withMessage('Content is required'),
  body('goals').isArray().withMessage('Goals must be an array'),
  body('goals.*').isIn(['engagement', 'conversion', 'seo', 'readability', 'brand_voice', 'viral_potential']).withMessage('Invalid goal'),
  body('context').optional().isObject().withMessage('Context must be an object')
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

    const { content, goals, context = {} } = req.body;
    
    const result = await aiOptimizationService.optimizeContent(content, goals, context);

    res.json({
      success: true,
      message: 'Content optimized successfully',
      data: result
    });
  } catch (error) {
    console.error('Content optimization error:', error);
    res.status(500).json({
      success: false,
      message: error.message || 'Failed to optimize content'
    });
  }
});

/**
 * @route   POST /api/optimization/engagement
 * @desc    Optimize content for engagement
 * @access  Private
 */
router.post('/engagement', auth, [
  body('content').notEmpty().withMessage('Content is required'),
  body('context').optional().isObject().withMessage('Context must be an object')
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

    const { content, context = {} } = req.body;
    
    const result = await aiOptimizationService.optimizeForEngagement(content, context);

    res.json({
      success: true,
      message: 'Content optimized for engagement',
      data: result
    });
  } catch (error) {
    console.error('Engagement optimization error:', error);
    res.status(500).json({
      success: false,
      message: error.message || 'Failed to optimize for engagement'
    });
  }
});

/**
 * @route   POST /api/optimization/conversion
 * @desc    Optimize content for conversion
 * @access  Private
 */
router.post('/conversion', auth, [
  body('content').notEmpty().withMessage('Content is required'),
  body('context').optional().isObject().withMessage('Context must be an object')
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

    const { content, context = {} } = req.body;
    
    const result = await aiOptimizationService.optimizeForConversion(content, context);

    res.json({
      success: true,
      message: 'Content optimized for conversion',
      data: result
    });
  } catch (error) {
    console.error('Conversion optimization error:', error);
    res.status(500).json({
      success: false,
      message: error.message || 'Failed to optimize for conversion'
    });
  }
});

/**
 * @route   POST /api/optimization/seo
 * @desc    Optimize content for SEO
 * @access  Private
 */
router.post('/seo', auth, [
  body('content').notEmpty().withMessage('Content is required'),
  body('context').optional().isObject().withMessage('Context must be an object')
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

    const { content, context = {} } = req.body;
    
    const result = await aiOptimizationService.optimizeForSEO(content, context);

    res.json({
      success: true,
      message: 'Content optimized for SEO',
      data: result
    });
  } catch (error) {
    console.error('SEO optimization error:', error);
    res.status(500).json({
      success: false,
      message: error.message || 'Failed to optimize for SEO'
    });
  }
});

/**
 * @route   POST /api/optimization/readability
 * @desc    Optimize content for readability
 * @access  Private
 */
router.post('/readability', auth, [
  body('content').notEmpty().withMessage('Content is required'),
  body('context').optional().isObject().withMessage('Context must be an object')
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

    const { content, context = {} } = req.body;
    
    const result = await aiOptimizationService.optimizeForReadability(content, context);

    res.json({
      success: true,
      message: 'Content optimized for readability',
      data: result
    });
  } catch (error) {
    console.error('Readability optimization error:', error);
    res.status(500).json({
      success: false,
      message: error.message || 'Failed to optimize for readability'
    });
  }
});

/**
 * @route   POST /api/optimization/brand-voice
 * @desc    Optimize content for brand voice
 * @access  Private
 */
router.post('/brand-voice', auth, [
  body('content').notEmpty().withMessage('Content is required'),
  body('context').optional().isObject().withMessage('Context must be an object')
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

    const { content, context = {} } = req.body;
    
    const result = await aiOptimizationService.optimizeForBrandVoice(content, context);

    res.json({
      success: true,
      message: 'Content optimized for brand voice',
      data: result
    });
  } catch (error) {
    console.error('Brand voice optimization error:', error);
    res.status(500).json({
      success: false,
      message: error.message || 'Failed to optimize for brand voice'
    });
  }
});

/**
 * @route   POST /api/optimization/viral
 * @desc    Optimize content for viral potential
 * @access  Private
 */
router.post('/viral', auth, [
  body('content').notEmpty().withMessage('Content is required'),
  body('context').optional().isObject().withMessage('Context must be an object')
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

    const { content, context = {} } = req.body;
    
    const result = await aiOptimizationService.optimizeForViralPotential(content, context);

    res.json({
      success: true,
      message: 'Content optimized for viral potential',
      data: result
    });
  } catch (error) {
    console.error('Viral optimization error:', error);
    res.status(500).json({
      success: false,
      message: error.message || 'Failed to optimize for viral potential'
    });
  }
});

/**
 * @route   POST /api/optimization/ab-test
 * @desc    Generate A/B test variants
 * @access  Private
 */
router.post('/ab-test', auth, [
  body('content').notEmpty().withMessage('Content is required'),
  body('goals').isArray().withMessage('Goals must be an array'),
  body('variants').optional().isInt({ min: 2, max: 5 }).withMessage('Variants must be between 2 and 5')
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

    const { content, goals, variants = 3 } = req.body;
    
    const result = await aiOptimizationService.generateABTestVariants(content, goals);

    res.json({
      success: true,
      message: 'A/B test variants generated successfully',
      data: {
        original: content,
        variants: result.slice(0, variants)
      }
    });
  } catch (error) {
    console.error('A/B test generation error:', error);
    res.status(500).json({
      success: false,
      message: error.message || 'Failed to generate A/B test variants'
    });
  }
});

/**
 * @route   POST /api/optimization/predict
 * @desc    Predict content performance
 * @access  Private
 */
router.post('/predict', auth, [
  body('content').notEmpty().withMessage('Content is required'),
  body('context').optional().isObject().withMessage('Context must be an object')
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

    const { content, context = {} } = req.body;
    
    const result = await aiOptimizationService.predictPerformance(content, context);

    res.json({
      success: true,
      message: 'Performance prediction generated',
      data: result
    });
  } catch (error) {
    console.error('Performance prediction error:', error);
    res.status(500).json({
      success: false,
      message: error.message || 'Failed to predict performance'
    });
  }
});

/**
 * @route   GET /api/optimization/strategies
 * @desc    Get available optimization strategies
 * @access  Private
 */
router.get('/strategies', auth, async (req, res) => {
  try {
    const strategies = {
      engagement: {
        name: 'Engagement Optimization',
        description: 'Optimize content to increase user engagement and interaction',
        features: ['Emotional triggers', 'Interactive questions', 'Call-to-actions', 'Optimal length']
      },
      conversion: {
        name: 'Conversion Optimization',
        description: 'Optimize content to increase conversion rates',
        features: ['Urgency elements', 'Social proof', 'Value propositions', 'Strong CTAs']
      },
      seo: {
        name: 'SEO Optimization',
        description: 'Optimize content for search engine visibility',
        features: ['Keyword optimization', 'Title optimization', 'Meta descriptions', 'Internal linking']
      },
      readability: {
        name: 'Readability Optimization',
        description: 'Optimize content for better readability and comprehension',
        features: ['Sentence structure', 'Subheadings', 'Simple language', 'Bullet points']
      },
      brand_voice: {
        name: 'Brand Voice Optimization',
        description: 'Optimize content to match brand voice and personality',
        features: ['Tone adjustment', 'Style consistency', 'Personality elements', 'Brand guidelines']
      },
      viral_potential: {
        name: 'Viral Potential Optimization',
        description: 'Optimize content for viral sharing and reach',
        features: ['Trending elements', 'Shareable content', 'Controversy hooks', 'Emotional triggers']
      }
    };

    res.json({
      success: true,
      data: strategies
    });
  } catch (error) {
    console.error('Get strategies error:', error);
    res.status(500).json({
      success: false,
      message: error.message || 'Failed to get optimization strategies'
    });
  }
});

/**
 * @route   GET /api/optimization/metrics
 * @desc    Get optimization metrics
 * @access  Private
 */
router.get('/metrics', auth, async (req, res) => {
  try {
    const { timeRange = '30d' } = req.query;
    
    // This would return optimization metrics from database
    const metrics = {
      totalOptimizations: 0,
      successfulOptimizations: 0,
      averageImprovement: 0,
      topPerformingGoals: [],
      userOptimizations: 0,
      timeRange
    };

    res.json({
      success: true,
      data: metrics
    });
  } catch (error) {
    console.error('Get optimization metrics error:', error);
    res.status(500).json({
      success: false,
      message: error.message || 'Failed to get optimization metrics'
    });
  }
});

/**
 * @route   POST /api/optimization/batch
 * @desc    Optimize multiple pieces of content
 * @access  Private
 */
router.post('/batch', auth, [
  body('contents').isArray().withMessage('Contents must be an array'),
  body('contents.*').isObject().withMessage('Each content item must be an object'),
  body('goals').isArray().withMessage('Goals must be an array'),
  body('context').optional().isObject().withMessage('Context must be an object')
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

    const { contents, goals, context = {} } = req.body;
    
    const results = [];
    
    for (const contentItem of contents) {
      try {
        const result = await aiOptimizationService.optimizeContent(
          contentItem.content, 
          goals, 
          { ...context, ...contentItem.context }
        );
        results.push({
          id: contentItem.id,
          success: true,
          data: result
        });
      } catch (error) {
        results.push({
          id: contentItem.id,
          success: false,
          error: error.message
        });
      }
    }

    res.json({
      success: true,
      message: 'Batch optimization completed',
      data: {
        total: contents.length,
        successful: results.filter(r => r.success).length,
        failed: results.filter(r => !r.success).length,
        results
      }
    });
  } catch (error) {
    console.error('Batch optimization error:', error);
    res.status(500).json({
      success: false,
      message: error.message || 'Failed to perform batch optimization'
    });
  }
});

module.exports = router;





