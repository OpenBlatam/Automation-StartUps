const express = require('express');
const router = express.Router();
const auth = require('../middleware/auth');
const contentAnalysisService = require('../services/contentAnalysisService');
const { body, validationResult } = require('express-validator');

// Initialize content analysis service
contentAnalysisService.initialize();

/**
 * @route   POST /api/content-analysis/analyze
 * @desc    Analyze content for quality, engagement, and optimization
 * @access  Private
 */
router.post('/analyze', auth, [
  body('content').isString().withMessage('Content must be a string'),
  body('analysisType').optional().isIn(['comprehensive', 'quick', 'detailed', 'seo', 'engagement']).withMessage('Invalid analysis type'),
  body('includeSentiment').optional().isBoolean().withMessage('Include sentiment must be a boolean'),
  body('includeReadability').optional().isBoolean().withMessage('Include readability must be a boolean'),
  body('includeSEO').optional().isBoolean().withMessage('Include SEO must be a boolean'),
  body('includeEngagement').optional().isBoolean().withMessage('Include engagement must be a boolean')
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

    const { content, ...options } = req.body;
    const userId = req.user.id;
    
    const analysis = await contentAnalysisService.analyzeContent(content, {
      ...options,
      userId,
      contentId: `content_${Date.now()}`
    });

    res.json({
      success: true,
      message: 'Content analysis completed successfully',
      data: analysis
    });
  } catch (error) {
    console.error('Content analysis error:', error);
    res.status(500).json({
      success: false,
      message: error.message || 'Failed to analyze content'
    });
  }
});

/**
 * @route   POST /api/content-analysis/compare
 * @desc    Compare two pieces of content
 * @access  Private
 */
router.post('/compare', auth, [
  body('content1').isString().withMessage('Content 1 must be a string'),
  body('content2').isString().withMessage('Content 2 must be a string'),
  body('comparisonType').optional().isIn(['quality', 'engagement', 'seo', 'comprehensive']).withMessage('Invalid comparison type')
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

    const { content1, content2, ...options } = req.body;
    const userId = req.user.id;
    
    const comparison = await contentAnalysisService.compareContent(content1, content2, {
      ...options,
      userId
    });

    res.json({
      success: true,
      message: 'Content comparison completed successfully',
      data: comparison
    });
  } catch (error) {
    console.error('Content comparison error:', error);
    res.status(500).json({
      success: false,
      message: error.message || 'Failed to compare content'
    });
  }
});

/**
 * @route   POST /api/content-analysis/insights
 * @desc    Generate content insights and recommendations
 * @access  Private
 */
router.post('/insights', auth, [
  body('content').isString().withMessage('Content must be a string'),
  body('insightType').optional().isIn(['performance', 'optimization', 'strategy', 'comprehensive']).withMessage('Invalid insight type'),
  body('includeRecommendations').optional().isBoolean().withMessage('Include recommendations must be a boolean'),
  body('includeABTesting').optional().isBoolean().withMessage('Include A/B testing must be a boolean')
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

    const { content, ...options } = req.body;
    const userId = req.user.id;
    
    const insights = await contentAnalysisService.generateContentInsights(content, {
      ...options,
      userId,
      contentId: `content_${Date.now()}`
    });

    res.json({
      success: true,
      message: 'Content insights generated successfully',
      data: insights
    });
  } catch (error) {
    console.error('Content insights error:', error);
    res.status(500).json({
      success: false,
      message: error.message || 'Failed to generate content insights'
    });
  }
});

/**
 * @route   GET /api/content-analysis/templates
 * @desc    Get content analysis templates
 * @access  Private
 */
router.get('/templates', auth, async (req, res) => {
  try {
    const templates = [
      {
        id: 'comprehensive_analysis',
        name: 'Comprehensive Analysis',
        description: 'Complete content analysis including all metrics',
        analysisType: 'comprehensive',
        includeSentiment: true,
        includeReadability: true,
        includeSEO: true,
        includeEngagement: true
      },
      {
        id: 'quick_analysis',
        name: 'Quick Analysis',
        description: 'Fast content analysis for basic insights',
        analysisType: 'quick',
        includeSentiment: true,
        includeReadability: false,
        includeSEO: false,
        includeEngagement: true
      },
      {
        id: 'seo_analysis',
        name: 'SEO Analysis',
        description: 'Content analysis focused on SEO optimization',
        analysisType: 'seo',
        includeSentiment: false,
        includeReadability: true,
        includeSEO: true,
        includeEngagement: false
      },
      {
        id: 'engagement_analysis',
        name: 'Engagement Analysis',
        description: 'Content analysis focused on audience engagement',
        analysisType: 'engagement',
        includeSentiment: true,
        includeReadability: true,
        includeSEO: false,
        includeEngagement: true
      }
    ];

    res.json({
      success: true,
      data: templates
    });
  } catch (error) {
    console.error('Get content analysis templates error:', error);
    res.status(500).json({
      success: false,
      message: error.message || 'Failed to get content analysis templates'
    });
  }
});

/**
 * @route   GET /api/content-analysis/benchmarks
 * @desc    Get content analysis benchmarks
 * @access  Private
 */
router.get('/benchmarks', auth, async (req, res) => {
  try {
    const { industry = 'general', contentType = 'blog' } = req.query;
    
    const benchmarks = {
      industry: industry,
      contentType: contentType,
      benchmarks: {
        readability: {
          averageScore: industry === 'technology' ? 8.2 : 7.8,
          targetScore: 8.0,
          description: 'Flesch Reading Ease Score'
        },
        sentiment: {
          averageScore: industry === 'technology' ? 7.5 : 7.2,
          targetScore: 7.0,
          description: 'Sentiment Analysis Score (1-10)'
        },
        seo: {
          averageScore: industry === 'technology' ? 8.0 : 7.5,
          targetScore: 8.0,
          description: 'SEO Optimization Score (1-10)'
        },
        engagement: {
          averageScore: industry === 'technology' ? 7.8 : 7.3,
          targetScore: 7.5,
          description: 'Engagement Potential Score (1-10)'
        }
      },
      recommendations: [
        'Aim for readability scores above 8.0',
        'Maintain positive sentiment scores above 7.0',
        'Optimize for SEO with scores above 8.0',
        'Focus on engagement scores above 7.5',
        'Test different content formats and styles'
      ]
    };

    res.json({
      success: true,
      data: benchmarks
    });
  } catch (error) {
    console.error('Get content analysis benchmarks error:', error);
    res.status(500).json({
      success: false,
      message: error.message || 'Failed to get content analysis benchmarks'
    });
  }
});

module.exports = router;



