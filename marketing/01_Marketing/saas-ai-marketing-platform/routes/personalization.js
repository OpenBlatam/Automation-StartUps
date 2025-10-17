const express = require('express');
const router = express.Router();
const auth = require('../middleware/auth');
const personalizationService = require('../services/personalizationService');
const { body, validationResult } = require('express-validator');

// Initialize personalization service
personalizationService.initialize();

/**
 * @route   POST /api/personalization/personalize
 * @desc    Personalize content for user
 * @access  Private
 */
router.post('/personalize', auth, [
  body('content').notEmpty().withMessage('Content is required'),
  body('options').optional().isObject().withMessage('Options must be an object'),
  body('options.variationCount').optional().isInt({ min: 1, max: 5 }).withMessage('Variation count must be between 1 and 5')
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

    const { content, options = {} } = req.body;
    const userId = req.user.id;
    
    const result = await personalizationService.personalizeContent(userId, content, options);

    res.json({
      success: true,
      message: 'Content personalized successfully',
      data: result
    });
  } catch (error) {
    console.error('Content personalization error:', error);
    res.status(500).json({
      success: false,
      message: error.message || 'Failed to personalize content'
    });
  }
});

/**
 * @route   GET /api/personalization/profile
 * @desc    Get user personalization profile
 * @access  Private
 */
router.get('/profile', auth, async (req, res) => {
  try {
    const userId = req.user.id;
    
    const profile = await personalizationService.getUserProfile(userId);

    res.json({
      success: true,
      data: profile
    });
  } catch (error) {
    console.error('Get user profile error:', error);
    res.status(500).json({
      success: false,
      message: error.message || 'Failed to get user profile'
    });
  }
});

/**
 * @route   GET /api/personalization/preferences
 * @desc    Get user content preferences
 * @access  Private
 */
router.get('/preferences', auth, async (req, res) => {
  try {
    const userId = req.user.id;
    
    const preferences = await personalizationService.getContentPreferences(userId);

    res.json({
      success: true,
      data: preferences
    });
  } catch (error) {
    console.error('Get content preferences error:', error);
    res.status(500).json({
      success: false,
      message: error.message || 'Failed to get content preferences'
    });
  }
});

/**
 * @route   GET /api/personalization/behavior
 * @desc    Get user behavior patterns
 * @access  Private
 */
router.get('/behavior', auth, async (req, res) => {
  try {
    const userId = req.user.id;
    
    const behavior = await personalizationService.getBehaviorPatterns(userId);

    res.json({
      success: true,
      data: behavior
    });
  } catch (error) {
    console.error('Get behavior patterns error:', error);
    res.status(500).json({
      success: false,
      message: error.message || 'Failed to get behavior patterns'
    });
  }
});

/**
 * @route   PUT /api/personalization/preferences
 * @desc    Update user content preferences
 * @access  Private
 */
router.put('/preferences', auth, [
  body('tone').optional().isIn(['casual', 'professional', 'friendly', 'authoritative']).withMessage('Invalid tone'),
  body('style').optional().isIn(['conversational', 'formal', 'technical', 'creative']).withMessage('Invalid style'),
  body('length').optional().isIn(['short', 'medium', 'long']).withMessage('Invalid length'),
  body('topics').optional().isArray().withMessage('Topics must be an array'),
  body('formats').optional().isArray().withMessage('Formats must be an array'),
  body('complexity').optional().isIn(['simple', 'intermediate', 'advanced']).withMessage('Invalid complexity')
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

    const userId = req.user.id;
    const preferences = req.body;
    
    // This would update user preferences in the database
    // For now, return a placeholder response
    res.json({
      success: true,
      message: 'Content preferences updated successfully',
      data: preferences
    });
  } catch (error) {
    console.error('Update preferences error:', error);
    res.status(500).json({
      success: false,
      message: error.message || 'Failed to update preferences'
    });
  }
});

/**
 * @route   POST /api/personalization/analyze
 * @desc    Analyze content for personalization opportunities
 * @access  Private
 */
router.post('/analyze', auth, [
  body('content').notEmpty().withMessage('Content is required'),
  body('analysisType').optional().isIn(['tone', 'style', 'engagement', 'complexity', 'all']).withMessage('Invalid analysis type')
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

    const { content, analysisType = 'all' } = req.body;
    const userId = req.user.id;
    
    const profile = await personalizationService.getUserProfile(userId);
    const analysis = await personalizationService.analyzeContentForPersonalization(content, profile, analysisType);

    res.json({
      success: true,
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
 * @route   GET /api/personalization/recommendations
 * @desc    Get personalization recommendations
 * @access  Private
 */
router.get('/recommendations', auth, async (req, res) => {
  try {
    const userId = req.user.id;
    
    const profile = await personalizationService.getUserProfile(userId);
    const recommendations = personalizationService.generatePersonalizationRecommendations(profile, []);

    res.json({
      success: true,
      data: recommendations
    });
  } catch (error) {
    console.error('Get recommendations error:', error);
    res.status(500).json({
      success: false,
      message: error.message || 'Failed to get recommendations'
    });
  }
});

/**
 * @route   POST /api/personalization/batch
 * @desc    Personalize multiple pieces of content
 * @access  Private
 */
router.post('/batch', auth, [
  body('contents').isArray().withMessage('Contents must be an array'),
  body('contents.*').isObject().withMessage('Each content item must be an object'),
  body('contents.*.content').notEmpty().withMessage('Content is required'),
  body('options').optional().isObject().withMessage('Options must be an object')
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

    const { contents, options = {} } = req.body;
    const userId = req.user.id;
    
    const results = [];
    
    for (const contentItem of contents) {
      try {
        const result = await personalizationService.personalizeContent(
          userId, 
          contentItem.content, 
          { ...options, ...contentItem.options }
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
      message: 'Batch personalization completed',
      data: {
        total: contents.length,
        successful: results.filter(r => r.success).length,
        failed: results.filter(r => !r.success).length,
        results
      }
    });
  } catch (error) {
    console.error('Batch personalization error:', error);
    res.status(500).json({
      success: false,
      message: error.message || 'Failed to perform batch personalization'
    });
  }
});

/**
 * @route   GET /api/personalization/insights
 * @desc    Get personalization insights
 * @access  Private
 */
router.get('/insights', auth, async (req, res) => {
  try {
    const userId = req.user.id;
    
    const profile = await personalizationService.getUserProfile(userId);
    const insights = {
      personalizationScore: personalizationService.calculatePersonalizationScore([], profile),
      topPreferences: {
        tone: profile.preferences.tone,
        style: profile.preferences.style,
        length: profile.preferences.length
      },
      engagementInsights: {
        averageEngagement: profile.engagement.averageEngagement,
        preferredContentTypes: profile.engagement.preferredContentTypes,
        optimalPostingTimes: profile.engagement.optimalPostingTimes
      },
      behaviorInsights: {
        usagePatterns: profile.behavior.usagePatterns,
        engagementPatterns: profile.behavior.engagementPatterns,
        contentPatterns: profile.behavior.contentPatterns
      },
      recommendations: personalizationService.generatePersonalizationRecommendations(profile, [])
    };

    res.json({
      success: true,
      data: insights
    });
  } catch (error) {
    console.error('Get insights error:', error);
    res.status(500).json({
      success: false,
      message: error.message || 'Failed to get insights'
    });
  }
});

/**
 * @route   POST /api/personalization/feedback
 * @desc    Submit personalization feedback
 * @access  Private
 */
router.post('/feedback', auth, [
  body('contentId').notEmpty().withMessage('Content ID is required'),
  body('rating').isInt({ min: 1, max: 5 }).withMessage('Rating must be between 1 and 5'),
  body('feedback').optional().isString().withMessage('Feedback must be a string'),
  body('personalizationScore').optional().isInt({ min: 1, max: 10 }).withMessage('Personalization score must be between 1 and 10')
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

    const { contentId, rating, feedback, personalizationScore } = req.body;
    const userId = req.user.id;
    
    // This would store feedback in the database
    // For now, return a placeholder response
    res.json({
      success: true,
      message: 'Feedback submitted successfully',
      data: { contentId, rating, feedback, personalizationScore }
    });
  } catch (error) {
    console.error('Submit feedback error:', error);
    res.status(500).json({
      success: false,
      message: error.message || 'Failed to submit feedback'
    });
  }
});

/**
 * @route   GET /api/personalization/history
 * @desc    Get personalization history
 * @access  Private
 */
router.get('/history', auth, async (req, res) => {
  try {
    const userId = req.user.id;
    const { limit = 50, offset = 0 } = req.query;
    
    // This would get personalization history from the database
    // For now, return a placeholder response
    const history = {
      total: 0,
      items: [],
      pagination: {
        limit: parseInt(limit),
        offset: parseInt(offset),
        hasMore: false
      }
    };

    res.json({
      success: true,
      data: history
    });
  } catch (error) {
    console.error('Get personalization history error:', error);
    res.status(500).json({
      success: false,
      message: error.message || 'Failed to get personalization history'
    });
  }
});

/**
 * @route   DELETE /api/personalization/profile
 * @desc    Reset user personalization profile
 * @access  Private
 */
router.delete('/profile', auth, async (req, res) => {
  try {
    const userId = req.user.id;
    
    // This would reset the user profile in the database
    // For now, return a placeholder response
    res.json({
      success: true,
      message: 'Personalization profile reset successfully'
    });
  } catch (error) {
    console.error('Reset profile error:', error);
    res.status(500).json({
      success: false,
      message: error.message || 'Failed to reset profile'
    });
  }
});

module.exports = router;





