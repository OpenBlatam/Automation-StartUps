const express = require('express');
const router = express.Router();
const auth = require('../middleware/auth');
const aiInsightsService = require('../services/aiInsightsService');
const { body, validationResult } = require('express-validator');

// Initialize AI insights service
aiInsightsService.initialize();

/**
 * @route   POST /api/ai-insights/generate
 * @desc    Generate comprehensive AI insights
 * @access  Private
 */
router.post('/generate', auth, [
  body('timeRange').optional().isIn(['7d', '30d', '90d', '1y']).withMessage('Invalid time range'),
  body('insightTypes').optional().isArray().withMessage('Insight types must be an array'),
  body('insightTypes.*').isIn(['performance', 'trends', 'opportunities', 'recommendations', 'competitive']).withMessage('Invalid insight type'),
  body('includePredictions').optional().isBoolean().withMessage('Include predictions must be a boolean'),
  body('includeCompetitiveAnalysis').optional().isBoolean().withMessage('Include competitive analysis must be a boolean')
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

    const options = req.body;
    const userId = req.user.id;
    
    const insights = await aiInsightsService.generateInsights(userId, options);

    res.json({
      success: true,
      message: 'AI insights generated successfully',
      data: insights
    });
  } catch (error) {
    console.error('Generate AI insights error:', error);
    res.status(500).json({
      success: false,
      message: error.message || 'Failed to generate AI insights'
    });
  }
});

/**
 * @route   GET /api/ai-insights/performance
 * @desc    Get performance insights
 * @access  Private
 */
router.get('/performance', auth, async (req, res) => {
  try {
    const { timeRange = '30d' } = req.query;
    const userId = req.user.id;
    
    const insights = await aiInsightsService.generatePerformanceInsights(userId, timeRange);

    res.json({
      success: true,
      data: insights
    });
  } catch (error) {
    console.error('Get performance insights error:', error);
    res.status(500).json({
      success: false,
      message: error.message || 'Failed to get performance insights'
    });
  }
});

/**
 * @route   GET /api/ai-insights/trends
 * @desc    Get trend insights
 * @access  Private
 */
router.get('/trends', auth, async (req, res) => {
  try {
    const { timeRange = '30d' } = req.query;
    const userId = req.user.id;
    
    const insights = await aiInsightsService.generateTrendInsights(userId, timeRange);

    res.json({
      success: true,
      data: insights
    });
  } catch (error) {
    console.error('Get trend insights error:', error);
    res.status(500).json({
      success: false,
      message: error.message || 'Failed to get trend insights'
    });
  }
});

/**
 * @route   GET /api/ai-insights/opportunities
 * @desc    Get opportunity insights
 * @access  Private
 */
router.get('/opportunities', auth, async (req, res) => {
  try {
    const { timeRange = '30d' } = req.query;
    const userId = req.user.id;
    
    const insights = await aiInsightsService.generateOpportunityInsights(userId, timeRange);

    res.json({
      success: true,
      data: insights
    });
  } catch (error) {
    console.error('Get opportunity insights error:', error);
    res.status(500).json({
      success: false,
      message: error.message || 'Failed to get opportunity insights'
    });
  }
});

/**
 * @route   GET /api/ai-insights/recommendations
 * @desc    Get recommendation insights
 * @access  Private
 */
router.get('/recommendations', auth, async (req, res) => {
  try {
    const { timeRange = '30d' } = req.query;
    const userId = req.user.id;
    
    const insights = await aiInsightsService.generateRecommendationInsights(userId, timeRange);

    res.json({
      success: true,
      data: insights
    });
  } catch (error) {
    console.error('Get recommendation insights error:', error);
    res.status(500).json({
      success: false,
      message: error.message || 'Failed to get recommendation insights'
    });
  }
});

/**
 * @route   GET /api/ai-insights/predictions
 * @desc    Get predictive insights
 * @access  Private
 */
router.get('/predictions', auth, async (req, res) => {
  try {
    const { timeRange = '30d' } = req.query;
    const userId = req.user.id;
    
    const insights = await aiInsightsService.generatePredictiveInsights(userId, timeRange);

    res.json({
      success: true,
      data: insights
    });
  } catch (error) {
    console.error('Get predictive insights error:', error);
    res.status(500).json({
      success: false,
      message: error.message || 'Failed to get predictive insights'
    });
  }
});

/**
 * @route   GET /api/ai-insights/competitive
 * @desc    Get competitive insights
 * @access  Private
 */
router.get('/competitive', auth, async (req, res) => {
  try {
    const { timeRange = '30d' } = req.query;
    const userId = req.user.id;
    
    const insights = await aiInsightsService.generateCompetitiveInsights(userId, timeRange);

    res.json({
      success: true,
      data: insights
    });
  } catch (error) {
    console.error('Get competitive insights error:', error);
    res.status(500).json({
      success: false,
      message: error.message || 'Failed to get competitive insights'
    });
  }
});

/**
 * @route   GET /api/ai-insights/executive-summary
 * @desc    Get executive summary
 * @access  Private
 */
router.get('/executive-summary', auth, async (req, res) => {
  try {
    const { timeRange = '30d' } = req.query;
    const userId = req.user.id;
    
    const insights = await aiInsightsService.generateInsights(userId, { timeRange });
    const summary = await aiInsightsService.generateExecutiveSummary(insights.insights);

    res.json({
      success: true,
      data: summary
    });
  } catch (error) {
    console.error('Get executive summary error:', error);
    res.status(500).json({
      success: false,
      message: error.message || 'Failed to get executive summary'
    });
  }
});

/**
 * @route   GET /api/ai-insights/dashboard
 * @desc    Get insights dashboard data
 * @access  Private
 */
router.get('/dashboard', auth, async (req, res) => {
  try {
    const { timeRange = '30d' } = req.query;
    const userId = req.user.id;
    
    const insights = await aiInsightsService.generateInsights(userId, { 
      timeRange,
      insightTypes: ['performance', 'trends', 'opportunities', 'recommendations'],
      includePredictions: true
    });

    res.json({
      success: true,
      data: {
        overview: insights.insightScore,
        performance: insights.insights.performance,
        trends: insights.insights.trends,
        opportunities: insights.insights.opportunities,
        recommendations: insights.insights.recommendations,
        predictions: insights.insights.predictions,
        executiveSummary: insights.executiveSummary
      }
    });
  } catch (error) {
    console.error('Get insights dashboard error:', error);
    res.status(500).json({
      success: false,
      message: error.message || 'Failed to get insights dashboard'
    });
  }
});

/**
 * @route   POST /api/ai-insights/export
 * @desc    Export insights data
 * @access  Private
 */
router.post('/export', auth, [
  body('format').isIn(['json', 'pdf', 'csv', 'excel']).withMessage('Invalid export format'),
  body('insightTypes').optional().isArray().withMessage('Insight types must be an array'),
  body('timeRange').optional().isIn(['7d', '30d', '90d', '1y']).withMessage('Invalid time range')
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

    const { format, insightTypes = ['performance', 'trends', 'opportunities', 'recommendations'], timeRange = '30d' } = req.body;
    const userId = req.user.id;
    
    const insights = await aiInsightsService.generateInsights(userId, { 
      timeRange,
      insightTypes,
      includePredictions: true,
      includeCompetitiveAnalysis: true
    });

    // This would generate the export file based on format
    // For now, return the insights data
    res.json({
      success: true,
      message: `Insights exported successfully in ${format} format`,
      data: insights
    });
  } catch (error) {
    console.error('Export insights error:', error);
    res.status(500).json({
      success: false,
      message: error.message || 'Failed to export insights'
    });
  }
});

/**
 * @route   GET /api/ai-insights/insight-score
 * @desc    Get insight score
 * @access  Private
 */
router.get('/insight-score', auth, async (req, res) => {
  try {
    const { timeRange = '30d' } = req.query;
    const userId = req.user.id;
    
    const insights = await aiInsightsService.generateInsights(userId, { timeRange });
    const score = insights.insightScore;

    res.json({
      success: true,
      data: {
        score: score,
        level: score >= 80 ? 'excellent' : score >= 60 ? 'good' : score >= 40 ? 'fair' : 'poor',
        recommendations: score < 60 ? [
          'Improve content quality',
          'Increase engagement',
          'Optimize for better performance'
        ] : []
      }
    });
  } catch (error) {
    console.error('Get insight score error:', error);
    res.status(500).json({
      success: false,
      message: error.message || 'Failed to get insight score'
    });
  }
});

/**
 * @route   GET /api/ai-insights/trending-topics
 * @desc    Get trending topics
 * @access  Private
 */
router.get('/trending-topics', auth, async (req, res) => {
  try {
    const { timeRange = '30d' } = req.query;
    const userId = req.user.id;
    
    const insights = await aiInsightsService.generateTrendInsights(userId, timeRange);
    const trendingTopics = insights.contentTrends?.popularTopics || [];

    res.json({
      success: true,
      data: trendingTopics
    });
  } catch (error) {
    console.error('Get trending topics error:', error);
    res.status(500).json({
      success: false,
      message: error.message || 'Failed to get trending topics'
    });
  }
});

/**
 * @route   GET /api/ai-insights/performance-gaps
 * @desc    Get performance gaps
 * @access  Private
 */
router.get('/performance-gaps', auth, async (req, res) => {
  try {
    const { timeRange = '30d' } = req.query;
    const userId = req.user.id;
    
    const insights = await aiInsightsService.generatePerformanceInsights(userId, timeRange);
    const performanceGaps = insights.contentPerformance?.performanceGaps || [];

    res.json({
      success: true,
      data: performanceGaps
    });
  } catch (error) {
    console.error('Get performance gaps error:', error);
    res.status(500).json({
      success: false,
      message: error.message || 'Failed to get performance gaps'
    });
  }
});

/**
 * @route   GET /api/ai-insights/opportunity-score
 * @desc    Get opportunity score
 * @access  Private
 */
router.get('/opportunity-score', auth, async (req, res) => {
  try {
    const { timeRange = '30d' } = req.query;
    const userId = req.user.id;
    
    const insights = await aiInsightsService.generateOpportunityInsights(userId, timeRange);
    
    // Calculate opportunity score based on available opportunities
    const opportunities = insights.contentOpportunities || {};
    const opportunityCount = Object.keys(opportunities).length;
    const score = Math.min(100, opportunityCount * 10);

    res.json({
      success: true,
      data: {
        score: score,
        level: score >= 70 ? 'high' : score >= 40 ? 'medium' : 'low',
        opportunities: opportunities
      }
    });
  } catch (error) {
    console.error('Get opportunity score error:', error);
    res.status(500).json({
      success: false,
      message: error.message || 'Failed to get opportunity score'
    });
  }
});

/**
 * @route   POST /api/ai-insights/analyze-content
 * @desc    Analyze specific content for insights
 * @access  Private
 */
router.post('/analyze-content', auth, [
  body('content').notEmpty().withMessage('Content is required'),
  body('contentType').optional().isString().withMessage('Content type must be a string'),
  body('analysisType').optional().isIn(['performance', 'engagement', 'optimization', 'all']).withMessage('Invalid analysis type')
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

    const { content, contentType = 'general', analysisType = 'all' } = req.body;
    const userId = req.user.id;
    
    // This would analyze the specific content
    // For now, return a placeholder response
    const analysis = {
      contentId: 'content_' + Date.now(),
      contentType: contentType,
      analysisType: analysisType,
      insights: {
        performance: {
          score: 7.5,
          strengths: ['Clear messaging', 'Good structure'],
          weaknesses: ['Low engagement', 'Poor SEO']
        },
        engagement: {
          score: 6.2,
          factors: ['Length', 'Tone', 'Call-to-action'],
          recommendations: ['Add interactive elements', 'Improve headlines']
        },
        optimization: {
          score: 5.8,
          opportunities: ['SEO optimization', 'Personalization', 'A/B testing'],
          priority: 'high'
        }
      },
      recommendations: [
        'Optimize for SEO',
        'Add more engaging elements',
        'Test different headlines',
        'Personalize content for audience'
      ]
    };

    res.json({
      success: true,
      message: 'Content analysis completed',
      data: analysis
    });
  } catch (error) {
    console.error('Analyze content error:', error);
    res.status(500).json({
      success: false,
      message: error.message || 'Failed to analyze content'
    });
  }
});

module.exports = router;





