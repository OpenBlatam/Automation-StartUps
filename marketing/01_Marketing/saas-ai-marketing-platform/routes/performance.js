const express = require('express');
const router = express.Router();
const auth = require('../middleware/auth');
const performanceService = require('../services/performanceService');

/**
 * @route   GET /api/performance/summary
 * @desc    Get performance summary
 * @access  Private
 */
router.get('/summary', auth, async (req, res) => {
  try {
    const summary = performanceService.getPerformanceSummary();

    res.json({
      success: true,
      data: summary
    });
  } catch (error) {
    console.error('Get performance summary error:', error);
    res.status(500).json({
      success: false,
      message: error.message || 'Failed to get performance summary'
    });
  }
});

/**
 * @route   GET /api/performance/metrics
 * @desc    Get detailed performance metrics
 * @access  Private
 */
router.get('/metrics', auth, async (req, res) => {
  try {
    const metrics = performanceService.getDetailedMetrics();

    res.json({
      success: true,
      data: metrics
    });
  } catch (error) {
    console.error('Get performance metrics error:', error);
    res.status(500).json({
      success: false,
      message: error.message || 'Failed to get performance metrics'
    });
  }
});

/**
 * @route   GET /api/performance/trends
 * @desc    Get performance trends
 * @access  Private
 */
router.get('/trends', auth, async (req, res) => {
  try {
    const { timeRange = '1h' } = req.query;
    const trends = performanceService.getPerformanceTrends(timeRange);

    res.json({
      success: true,
      data: trends
    });
  } catch (error) {
    console.error('Get performance trends error:', error);
    res.status(500).json({
      success: false,
      message: error.message || 'Failed to get performance trends'
    });
  }
});

/**
 * @route   GET /api/performance/alerts
 * @desc    Get active performance alerts
 * @access  Private
 */
router.get('/alerts', auth, async (req, res) => {
  try {
    const alerts = performanceService.getActiveAlerts();

    res.json({
      success: true,
      data: alerts
    });
  } catch (error) {
    console.error('Get performance alerts error:', error);
    res.status(500).json({
      success: false,
      message: error.message || 'Failed to get performance alerts'
    });
  }
});

/**
 * @route   DELETE /api/performance/alerts
 * @desc    Clear performance alerts
 * @access  Private
 */
router.delete('/alerts', auth, async (req, res) => {
  try {
    performanceService.clearAlerts();

    res.json({
      success: true,
      message: 'Performance alerts cleared successfully'
    });
  } catch (error) {
    console.error('Clear performance alerts error:', error);
    res.status(500).json({
      success: false,
      message: error.message || 'Failed to clear performance alerts'
    });
  }
});

/**
 * @route   GET /api/performance/thresholds
 * @desc    Get performance thresholds
 * @access  Private
 */
router.get('/thresholds', auth, async (req, res) => {
  try {
    const thresholds = performanceService.getThresholds();

    res.json({
      success: true,
      data: thresholds
    });
  } catch (error) {
    console.error('Get performance thresholds error:', error);
    res.status(500).json({
      success: false,
      message: error.message || 'Failed to get performance thresholds'
    });
  }
});

/**
 * @route   PUT /api/performance/thresholds
 * @desc    Update performance thresholds
 * @access  Private
 */
router.put('/thresholds', auth, [
  body('cpu').optional().isFloat({ min: 0, max: 100 }).withMessage('CPU threshold must be between 0 and 100'),
  body('memory').optional().isFloat({ min: 0, max: 100 }).withMessage('Memory threshold must be between 0 and 100'),
  body('disk').optional().isFloat({ min: 0, max: 100 }).withMessage('Disk threshold must be between 0 and 100'),
  body('responseTime').optional().isInt({ min: 0 }).withMessage('Response time threshold must be a positive integer'),
  body('errorRate').optional().isFloat({ min: 0, max: 100 }).withMessage('Error rate threshold must be between 0 and 100'),
  body('throughput').optional().isInt({ min: 0 }).withMessage('Throughput threshold must be a positive integer')
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

    const thresholds = req.body;
    performanceService.setThresholds(thresholds);

    res.json({
      success: true,
      message: 'Performance thresholds updated successfully',
      data: performanceService.getThresholds()
    });
  } catch (error) {
    console.error('Update performance thresholds error:', error);
    res.status(500).json({
      success: false,
      message: error.message || 'Failed to update performance thresholds'
    });
  }
});

/**
 * @route   GET /api/performance/optimizations
 * @desc    Get performance optimization suggestions
 * @access  Private
 */
router.get('/optimizations', auth, async (req, res) => {
  try {
    const optimizations = await performanceService.optimizePerformance();

    res.json({
      success: true,
      data: optimizations
    });
  } catch (error) {
    console.error('Get performance optimizations error:', error);
    res.status(500).json({
      success: false,
      message: error.message || 'Failed to get performance optimizations'
    });
  }
});

/**
 * @route   POST /api/performance/optimize
 * @desc    Execute performance optimization
 * @access  Private
 */
router.post('/optimize', auth, [
  body('type').isIn(['garbage_collection', 'cache_cleanup', 'log_rotation']).withMessage('Invalid optimization type')
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

    const { type } = req.body;
    const optimization = { type };
    
    await performanceService.executeOptimization(optimization);

    res.json({
      success: true,
      message: 'Performance optimization executed successfully'
    });
  } catch (error) {
    console.error('Execute performance optimization error:', error);
    res.status(500).json({
      success: false,
      message: error.message || 'Failed to execute performance optimization'
    });
  }
});

/**
 * @route   GET /api/performance/report
 * @desc    Generate performance report
 * @access  Private
 */
router.get('/report', auth, async (req, res) => {
  try {
    const report = performanceService.generatePerformanceReport();

    res.json({
      success: true,
      data: report
    });
  } catch (error) {
    console.error('Generate performance report error:', error);
    res.status(500).json({
      success: false,
      message: error.message || 'Failed to generate performance report'
    });
  }
});

/**
 * @route   GET /api/performance/export
 * @desc    Export performance data
 * @access  Private
 */
router.get('/export', auth, async (req, res) => {
  try {
    const { format = 'json' } = req.query;
    const data = performanceService.exportPerformanceData(format);

    res.setHeader('Content-Type', format === 'csv' ? 'text/csv' : 'application/json');
    res.setHeader('Content-Disposition', `attachment; filename="performance-data.${format}"`);
    
    res.send(data);
  } catch (error) {
    console.error('Export performance data error:', error);
    res.status(500).json({
      success: false,
      message: error.message || 'Failed to export performance data'
    });
  }
});

/**
 * @route   POST /api/performance/save
 * @desc    Save performance data to file
 * @access  Private
 */
router.post('/save', auth, [
  body('filename').notEmpty().withMessage('Filename is required'),
  body('format').optional().isIn(['json', 'csv']).withMessage('Format must be json or csv')
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

    const { filename, format = 'json' } = req.body;
    
    await performanceService.savePerformanceData(filename, format);

    res.json({
      success: true,
      message: 'Performance data saved successfully'
    });
  } catch (error) {
    console.error('Save performance data error:', error);
    res.status(500).json({
      success: false,
      message: error.message || 'Failed to save performance data'
    });
  }
});

/**
 * @route   GET /api/performance/load
 * @desc    Load performance data from file
 * @access  Private
 */
router.get('/load/:filename', auth, async (req, res) => {
  try {
    const { filename } = req.params;
    const data = await performanceService.loadPerformanceData(filename);

    if (!data) {
      return res.status(404).json({
        success: false,
        message: 'Performance data file not found'
      });
    }

    res.json({
      success: true,
      data
    });
  } catch (error) {
    console.error('Load performance data error:', error);
    res.status(500).json({
      success: false,
      message: error.message || 'Failed to load performance data'
    });
  }
});

/**
 * @route   POST /api/performance/compare
 * @desc    Compare performance data
 * @access  Private
 */
router.post('/compare', auth, [
  body('baselineFile').notEmpty().withMessage('Baseline file is required'),
  body('currentFile').notEmpty().withMessage('Current file is required')
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

    const { baselineFile, currentFile } = req.body;
    
    const baselineData = await performanceService.loadPerformanceData(baselineFile);
    const currentData = await performanceService.loadPerformanceData(currentFile);

    if (!baselineData || !currentData) {
      return res.status(404).json({
        success: false,
        message: 'One or both performance data files not found'
      });
    }

    const comparison = performanceService.comparePerformance(baselineData, currentData);

    res.json({
      success: true,
      data: comparison
    });
  } catch (error) {
    console.error('Compare performance data error:', error);
    res.status(500).json({
      success: false,
      message: error.message || 'Failed to compare performance data'
    });
  }
});

/**
 * @route   POST /api/performance/start-monitoring
 * @desc    Start performance monitoring
 * @access  Private
 */
router.post('/start-monitoring', auth, [
  body('interval').optional().isInt({ min: 10000, max: 300000 }).withMessage('Interval must be between 10 and 300 seconds')
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

    const { interval = 30000 } = req.body;
    
    performanceService.startMonitoring(interval);

    res.json({
      success: true,
      message: 'Performance monitoring started successfully'
    });
  } catch (error) {
    console.error('Start performance monitoring error:', error);
    res.status(500).json({
      success: false,
      message: error.message || 'Failed to start performance monitoring'
    });
  }
});

/**
 * @route   POST /api/performance/stop-monitoring
 * @desc    Stop performance monitoring
 * @access  Private
 */
router.post('/stop-monitoring', auth, async (req, res) => {
  try {
    performanceService.stopMonitoring();

    res.json({
      success: true,
      message: 'Performance monitoring stopped successfully'
    });
  } catch (error) {
    console.error('Stop performance monitoring error:', error);
    res.status(500).json({
      success: false,
      message: error.message || 'Failed to stop performance monitoring'
    });
  }
});

module.exports = router;





