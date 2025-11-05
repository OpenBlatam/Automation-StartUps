const express = require('express');
const router = express.Router();
const auth = require('../middleware/auth');
const automationService = require('../services/automationService');
const { body, validationResult } = require('express-validator');

// Initialize automation service
automationService.initialize();

/**
 * @route   POST /api/automation/schedule
 * @desc    Schedule content generation
 * @access  Private
 */
router.post('/schedule', auth, [
  body('templateId').isMongoId().withMessage('Valid template ID is required'),
  body('frequency').isIn(['daily', 'weekly', 'monthly', 'hourly']).withMessage('Valid frequency is required'),
  body('time').notEmpty().withMessage('Time is required'),
  body('variables').isObject().withMessage('Variables must be an object')
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

    const schedule = {
      ...req.body,
      userId: req.user.id
    };

    const jobId = await automationService.scheduleContentGeneration(req.user.id, schedule);

    res.status(201).json({
      success: true,
      message: 'Content generation scheduled successfully',
      data: { jobId }
    });
  } catch (error) {
    console.error('Schedule content generation error:', error);
    res.status(500).json({
      success: false,
      message: error.message || 'Failed to schedule content generation'
    });
  }
});

/**
 * @route   POST /api/automation/workflow
 * @desc    Create automation workflow
 * @access  Private
 */
router.post('/workflow', auth, [
  body('name').notEmpty().withMessage('Workflow name is required'),
  body('triggers').isArray().withMessage('Triggers must be an array'),
  body('actions').isArray().withMessage('Actions must be an array')
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

    const workflow = {
      ...req.body,
      userId: req.user.id
    };

    const workflowId = await automationService.createWorkflow(req.user.id, workflow);

    res.status(201).json({
      success: true,
      message: 'Workflow created successfully',
      data: { workflowId }
    });
  } catch (error) {
    console.error('Create workflow error:', error);
    res.status(500).json({
      success: false,
      message: error.message || 'Failed to create workflow'
    });
  }
});

/**
 * @route   GET /api/automation
 * @desc    Get user automations
 * @access  Private
 */
router.get('/', auth, async (req, res) => {
  try {
    const automations = await automationService.getUserAutomations(req.user.id);

    res.json({
      success: true,
      data: automations
    });
  } catch (error) {
    console.error('Get automations error:', error);
    res.status(500).json({
      success: false,
      message: error.message || 'Failed to get automations'
    });
  }
});

/**
 * @route   DELETE /api/automation/:id
 * @desc    Delete automation
 * @access  Private
 */
router.delete('/:id', auth, async (req, res) => {
  try {
    const { id } = req.params;
    const deleted = await automationService.deleteAutomation(id, req.user.id);

    if (!deleted) {
      return res.status(404).json({
        success: false,
        message: 'Automation not found'
      });
    }

    res.json({
      success: true,
      message: 'Automation deleted successfully'
    });
  } catch (error) {
    console.error('Delete automation error:', error);
    res.status(500).json({
      success: false,
      message: error.message || 'Failed to delete automation'
    });
  }
});

/**
 * @route   PUT /api/automation/:id/toggle
 * @desc    Toggle automation
 * @access  Private
 */
router.put('/:id/toggle', auth, [
  body('enabled').isBoolean().withMessage('Enabled must be a boolean')
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

    const { id } = req.params;
    const { enabled } = req.body;

    const toggled = await automationService.toggleAutomation(id, req.user.id, enabled);

    if (!toggled) {
      return res.status(404).json({
        success: false,
        message: 'Automation not found'
      });
    }

    res.json({
      success: true,
      message: `Automation ${enabled ? 'enabled' : 'disabled'} successfully`
    });
  } catch (error) {
    console.error('Toggle automation error:', error);
    res.status(500).json({
      success: false,
      message: error.message || 'Failed to toggle automation'
    });
  }
});

module.exports = router;






