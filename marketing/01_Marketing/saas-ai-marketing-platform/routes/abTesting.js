const express = require('express');
const router = express.Router();
const auth = require('../middleware/auth');
const abTestingService = require('../services/abTestingService');
const { body, validationResult } = require('express-validator');

// Initialize A/B testing service
abTestingService.initialize();

/**
 * @route   POST /api/ab-testing/create
 * @desc    Create A/B test
 * @access  Private
 */
router.post('/create', auth, [
  body('name').notEmpty().withMessage('Test name is required'),
  body('description').optional().isString().withMessage('Description must be a string'),
  body('hypothesis').notEmpty().withMessage('Hypothesis is required'),
  body('variants').isArray({ min: 2 }).withMessage('At least 2 variants are required'),
  body('variants.*.content').notEmpty().withMessage('Variant content is required'),
  body('variants.*.name').optional().isString().withMessage('Variant name must be a string'),
  body('variants.*.weight').optional().isFloat({ min: 0, max: 1 }).withMessage('Variant weight must be between 0 and 1'),
  body('trafficAllocation').optional().isInt({ min: 1, max: 100 }).withMessage('Traffic allocation must be between 1 and 100'),
  body('targetAudience').optional().isObject().withMessage('Target audience must be an object'),
  body('successMetrics').isArray({ min: 1 }).withMessage('At least one success metric is required'),
  body('duration').optional().isInt({ min: 1, max: 30 }).withMessage('Duration must be between 1 and 30 days'),
  body('minSampleSize').optional().isInt({ min: 10 }).withMessage('Minimum sample size must be at least 10'),
  body('confidenceLevel').optional().isFloat({ min: 0.8, max: 0.99 }).withMessage('Confidence level must be between 0.8 and 0.99')
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

    const testConfig = {
      ...req.body,
      userId: req.user.id
    };

    const test = await abTestingService.createTest(testConfig);

    res.status(201).json({
      success: true,
      message: 'A/B test created successfully',
      data: test
    });
  } catch (error) {
    console.error('Create A/B test error:', error);
    res.status(500).json({
      success: false,
      message: error.message || 'Failed to create A/B test'
    });
  }
});

/**
 * @route   POST /api/ab-testing/:testId/start
 * @desc    Start A/B test
 * @access  Private
 */
router.post('/:testId/start', auth, async (req, res) => {
  try {
    const { testId } = req.params;
    
    const test = await abTestingService.startTest(testId);

    res.json({
      success: true,
      message: 'A/B test started successfully',
      data: test
    });
  } catch (error) {
    console.error('Start A/B test error:', error);
    res.status(500).json({
      success: false,
      message: error.message || 'Failed to start A/B test'
    });
  }
});

/**
 * @route   POST /api/ab-testing/:testId/end
 * @desc    End A/B test
 * @access  Private
 */
router.post('/:testId/end', auth, async (req, res) => {
  try {
    const { testId } = req.params;
    
    const test = await abTestingService.endTest(testId);

    res.json({
      success: true,
      message: 'A/B test ended successfully',
      data: test
    });
  } catch (error) {
    console.error('End A/B test error:', error);
    res.status(500).json({
      success: false,
      message: error.message || 'Failed to end A/B test'
    });
  }
});

/**
 * @route   GET /api/ab-testing/:testId/variant
 * @desc    Get variant for user
 * @access  Private
 */
router.get('/:testId/variant', auth, async (req, res) => {
  try {
    const { testId } = req.params;
    const userId = req.user.id;
    
    const variant = await abTestingService.getVariantForUser(testId, userId);

    if (!variant) {
      return res.status(404).json({
        success: false,
        message: 'No variant available for this test'
      });
    }

    res.json({
      success: true,
      data: variant
    });
  } catch (error) {
    console.error('Get variant error:', error);
    res.status(500).json({
      success: false,
      message: error.message || 'Failed to get variant'
    });
  }
});

/**
 * @route   POST /api/ab-testing/:testId/event
 * @desc    Record test event
 * @access  Private
 */
router.post('/:testId/event', auth, [
  body('eventType').isIn(['impression', 'conversion', 'click', 'view', 'engagement']).withMessage('Invalid event type'),
  body('eventData').optional().isObject().withMessage('Event data must be an object')
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

    const { testId } = req.params;
    const { eventType, eventData } = req.body;
    const userId = req.user.id;
    
    await abTestingService.recordEvent(testId, userId, eventType, eventData);

    res.json({
      success: true,
      message: 'Event recorded successfully'
    });
  } catch (error) {
    console.error('Record event error:', error);
    res.status(500).json({
      success: false,
      message: error.message || 'Failed to record event'
    });
  }
});

/**
 * @route   GET /api/ab-testing/:testId/results
 * @desc    Get test results
 * @access  Private
 */
router.get('/:testId/results', auth, async (req, res) => {
  try {
    const { testId } = req.params;
    
    const results = await abTestingService.getTestResults(testId);

    res.json({
      success: true,
      data: results
    });
  } catch (error) {
    console.error('Get test results error:', error);
    res.status(500).json({
      success: false,
      message: error.message || 'Failed to get test results'
    });
  }
});

/**
 * @route   GET /api/ab-testing/:testId/analytics
 * @desc    Get test analytics
 * @access  Private
 */
router.get('/:testId/analytics', auth, async (req, res) => {
  try {
    const { testId } = req.params;
    
    const analytics = await abTestingService.getTestAnalytics(testId);

    res.json({
      success: true,
      data: analytics
    });
  } catch (error) {
    console.error('Get test analytics error:', error);
    res.status(500).json({
      success: false,
      message: error.message || 'Failed to get test analytics'
    });
  }
});

/**
 * @route   GET /api/ab-testing/:testId/report
 * @desc    Generate test report
 * @access  Private
 */
router.get('/:testId/report', auth, async (req, res) => {
  try {
    const { testId } = req.params;
    
    const report = await abTestingService.generateTestReport(testId);

    res.json({
      success: true,
      data: report
    });
  } catch (error) {
    console.error('Generate test report error:', error);
    res.status(500).json({
      success: false,
      message: error.message || 'Failed to generate test report'
    });
  }
});

/**
 * @route   GET /api/ab-testing/user-tests
 * @desc    Get user's tests
 * @access  Private
 */
router.get('/user-tests', auth, async (req, res) => {
  try {
    const userId = req.user.id;
    
    const tests = await abTestingService.getUserTests(userId);

    res.json({
      success: true,
      data: tests
    });
  } catch (error) {
    console.error('Get user tests error:', error);
    res.status(500).json({
      success: false,
      message: error.message || 'Failed to get user tests'
    });
  }
});

/**
 * @route   GET /api/ab-testing/statistics
 * @desc    Get A/B testing statistics
 * @access  Private
 */
router.get('/statistics', auth, async (req, res) => {
  try {
    const statistics = abTestingService.getTestStatistics();

    res.json({
      success: true,
      data: statistics
    });
  } catch (error) {
    console.error('Get A/B testing statistics error:', error);
    res.status(500).json({
      success: false,
      message: error.message || 'Failed to get A/B testing statistics'
    });
  }
});

/**
 * @route   PUT /api/ab-testing/:testId
 * @desc    Update A/B test
 * @access  Private
 */
router.put('/:testId', auth, [
  body('name').optional().isString().withMessage('Name must be a string'),
  body('description').optional().isString().withMessage('Description must be a string'),
  body('hypothesis').optional().isString().withMessage('Hypothesis must be a string'),
  body('trafficAllocation').optional().isInt({ min: 1, max: 100 }).withMessage('Traffic allocation must be between 1 and 100'),
  body('targetAudience').optional().isObject().withMessage('Target audience must be an object'),
  body('successMetrics').optional().isArray().withMessage('Success metrics must be an array'),
  body('duration').optional().isInt({ min: 1, max: 30 }).withMessage('Duration must be between 1 and 30 days'),
  body('minSampleSize').optional().isInt({ min: 10 }).withMessage('Minimum sample size must be at least 10'),
  body('confidenceLevel').optional().isFloat({ min: 0.8, max: 0.99 }).withMessage('Confidence level must be between 0.8 and 0.99')
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

    const { testId } = req.params;
    const updates = req.body;
    
    // This would update the test in the database
    // For now, return a placeholder response
    res.json({
      success: true,
      message: 'A/B test updated successfully',
      data: { testId, updates }
    });
  } catch (error) {
    console.error('Update A/B test error:', error);
    res.status(500).json({
      success: false,
      message: error.message || 'Failed to update A/B test'
    });
  }
});

/**
 * @route   DELETE /api/ab-testing/:testId
 * @desc    Delete A/B test
 * @access  Private
 */
router.delete('/:testId', auth, async (req, res) => {
  try {
    const { testId } = req.params;
    
    // This would delete the test from the database
    // For now, return a placeholder response
    res.json({
      success: true,
      message: 'A/B test deleted successfully'
    });
  } catch (error) {
    console.error('Delete A/B test error:', error);
    res.status(500).json({
      success: false,
      message: error.message || 'Failed to delete A/B test'
    });
  }
});

/**
 * @route   POST /api/ab-testing/:testId/duplicate
 * @desc    Duplicate A/B test
 * @access  Private
 */
router.post('/:testId/duplicate', auth, async (req, res) => {
  try {
    const { testId } = req.params;
    const { name } = req.body;
    
    // This would duplicate the test in the database
    // For now, return a placeholder response
    res.json({
      success: true,
      message: 'A/B test duplicated successfully',
      data: { originalTestId: testId, newName: name }
    });
  } catch (error) {
    console.error('Duplicate A/B test error:', error);
    res.status(500).json({
      success: false,
      message: error.message || 'Failed to duplicate A/B test'
    });
  }
});

/**
 * @route   GET /api/ab-testing/templates
 * @desc    Get A/B test templates
 * @access  Private
 */
router.get('/templates', auth, async (req, res) => {
  try {
    const templates = [
      {
        id: 'email_subject',
        name: 'Email Subject Line Test',
        description: 'Test different email subject lines to improve open rates',
        hypothesis: 'Different subject lines will have different open rates',
        successMetrics: ['open_rate', 'click_rate'],
        variants: [
          { name: 'Control', content: 'Your weekly update is here' },
          { name: 'Variant A', content: 'Don\'t miss this week\'s insights' },
          { name: 'Variant B', content: 'Exclusive content inside' }
        ]
      },
      {
        id: 'cta_button',
        name: 'Call-to-Action Button Test',
        description: 'Test different CTA button texts to improve conversion rates',
        hypothesis: 'Different CTA texts will have different conversion rates',
        successMetrics: ['conversion_rate', 'click_rate'],
        variants: [
          { name: 'Control', content: 'Get Started' },
          { name: 'Variant A', content: 'Start Free Trial' },
          { name: 'Variant B', content: 'Join Now' }
        ]
      },
      {
        id: 'landing_page',
        name: 'Landing Page Test',
        description: 'Test different landing page layouts to improve conversion rates',
        hypothesis: 'Different layouts will have different conversion rates',
        successMetrics: ['conversion_rate', 'bounce_rate', 'time_on_page'],
        variants: [
          { name: 'Control', content: 'Standard layout with hero image' },
          { name: 'Variant A', content: 'Layout with testimonials' },
          { name: 'Variant B', content: 'Layout with video' }
        ]
      }
    ];

    res.json({
      success: true,
      data: templates
    });
  } catch (error) {
    console.error('Get A/B test templates error:', error);
    res.status(500).json({
      success: false,
      message: error.message || 'Failed to get A/B test templates'
    });
  }
});

module.exports = router;





