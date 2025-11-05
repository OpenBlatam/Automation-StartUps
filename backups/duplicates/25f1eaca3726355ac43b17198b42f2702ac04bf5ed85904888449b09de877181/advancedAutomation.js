const express = require('express');
const router = express.Router();
const auth = require('../middleware/auth');
const advancedAutomationService = require('../services/advancedAutomationService');
const { body, validationResult } = require('express-validator');

// Initialize advanced automation service
advancedAutomationService.initialize();

/**
 * @route   POST /api/automation/workflows
 * @desc    Create a new automation workflow
 * @access  Private
 */
router.post('/workflows', auth, [
  body('name').isString().withMessage('Name must be a string'),
  body('description').optional().isString().withMessage('Description must be a string'),
  body('triggers').optional().isArray().withMessage('Triggers must be an array'),
  body('actions').isArray().withMessage('Actions must be an array'),
  body('conditions').optional().isArray().withMessage('Conditions must be an array'),
  body('schedule').optional().isString().withMessage('Schedule must be a string'),
  body('isActive').optional().isBoolean().withMessage('Is active must be a boolean')
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

    const workflowData = req.body;
    const userId = req.user.id;
    
    const workflow = await advancedAutomationService.createWorkflow(userId, workflowData);

    res.json({
      success: true,
      message: 'Workflow created successfully',
      data: workflow
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
 * @route   GET /api/automation/workflows
 * @desc    Get user workflows
 * @access  Private
 */
router.get('/workflows', auth, async (req, res) => {
  try {
    const userId = req.user.id;
    const workflows = await advancedAutomationService.getUserWorkflows(userId);

    res.json({
      success: true,
      data: workflows
    });
  } catch (error) {
    console.error('Get workflows error:', error);
    res.status(500).json({
      success: false,
      message: error.message || 'Failed to get workflows'
    });
  }
});

/**
 * @route   GET /api/automation/workflows/:id
 * @desc    Get specific workflow
 * @access  Private
 */
router.get('/workflows/:id', auth, async (req, res) => {
  try {
    const { id } = req.params;
    const workflow = await advancedAutomationService.getWorkflow(id);
    
    if (!workflow) {
      return res.status(404).json({
        success: false,
        message: 'Workflow not found'
      });
    }

    res.json({
      success: true,
      data: workflow
    });
  } catch (error) {
    console.error('Get workflow error:', error);
    res.status(500).json({
      success: false,
      message: error.message || 'Failed to get workflow'
    });
  }
});

/**
 * @route   PUT /api/automation/workflows/:id
 * @desc    Update workflow
 * @access  Private
 */
router.put('/workflows/:id', auth, [
  body('updates').isObject().withMessage('Updates must be an object')
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
    const { updates } = req.body;
    
    const updatedWorkflow = await advancedAutomationService.updateWorkflow(id, updates);
    
    if (!updatedWorkflow) {
      return res.status(404).json({
        success: false,
        message: 'Workflow not found'
      });
    }

    res.json({
      success: true,
      message: 'Workflow updated successfully',
      data: updatedWorkflow
    });
  } catch (error) {
    console.error('Update workflow error:', error);
    res.status(500).json({
      success: false,
      message: error.message || 'Failed to update workflow'
    });
  }
});

/**
 * @route   DELETE /api/automation/workflows/:id
 * @desc    Delete workflow
 * @access  Private
 */
router.delete('/workflows/:id', auth, async (req, res) => {
  try {
    const { id } = req.params;
    const deleted = await advancedAutomationService.deleteWorkflow(id);
    
    if (!deleted) {
      return res.status(404).json({
        success: false,
        message: 'Workflow not found'
      });
    }

    res.json({
      success: true,
      message: 'Workflow deleted successfully'
    });
  } catch (error) {
    console.error('Delete workflow error:', error);
    res.status(500).json({
      success: false,
      message: error.message || 'Failed to delete workflow'
    });
  }
});

/**
 * @route   POST /api/automation/rules
 * @desc    Create automation rule
 * @access  Private
 */
router.post('/rules', auth, [
  body('name').isString().withMessage('Name must be a string'),
  body('description').optional().isString().withMessage('Description must be a string'),
  body('trigger').isObject().withMessage('Trigger must be an object'),
  body('conditions').optional().isArray().withMessage('Conditions must be an array'),
  body('actions').isArray().withMessage('Actions must be an array'),
  body('isActive').optional().isBoolean().withMessage('Is active must be a boolean')
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

    const ruleData = req.body;
    const userId = req.user.id;
    
    const rule = await advancedAutomationService.createAutomationRule(userId, ruleData);

    res.json({
      success: true,
      message: 'Automation rule created successfully',
      data: rule
    });
  } catch (error) {
    console.error('Create automation rule error:', error);
    res.status(500).json({
      success: false,
      message: error.message || 'Failed to create automation rule'
    });
  }
});

/**
 * @route   GET /api/automation/rules
 * @desc    Get user automation rules
 * @access  Private
 */
router.get('/rules', auth, async (req, res) => {
  try {
    const userId = req.user.id;
    const rules = await advancedAutomationService.getUserAutomationRules(userId);

    res.json({
      success: true,
      data: rules
    });
  } catch (error) {
    console.error('Get automation rules error:', error);
    res.status(500).json({
      success: false,
      message: error.message || 'Failed to get automation rules'
    });
  }
});

/**
 * @route   GET /api/automation/rules/:id
 * @desc    Get specific automation rule
 * @access  Private
 */
router.get('/rules/:id', auth, async (req, res) => {
  try {
    const { id } = req.params;
    const rule = await advancedAutomationService.getAutomationRule(id);
    
    if (!rule) {
      return res.status(404).json({
        success: false,
        message: 'Automation rule not found'
      });
    }

    res.json({
      success: true,
      data: rule
    });
  } catch (error) {
    console.error('Get automation rule error:', error);
    res.status(500).json({
      success: false,
      message: error.message || 'Failed to get automation rule'
    });
  }
});

/**
 * @route   PUT /api/automation/rules/:id
 * @desc    Update automation rule
 * @access  Private
 */
router.put('/rules/:id', auth, [
  body('updates').isObject().withMessage('Updates must be an object')
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
    const { updates } = req.body;
    
    const updatedRule = await advancedAutomationService.updateAutomationRule(id, updates);
    
    if (!updatedRule) {
      return res.status(404).json({
        success: false,
        message: 'Automation rule not found'
      });
    }

    res.json({
      success: true,
      message: 'Automation rule updated successfully',
      data: updatedRule
    });
  } catch (error) {
    console.error('Update automation rule error:', error);
    res.status(500).json({
      success: false,
      message: error.message || 'Failed to update automation rule'
    });
  }
});

/**
 * @route   DELETE /api/automation/rules/:id
 * @desc    Delete automation rule
 * @access  Private
 */
router.delete('/rules/:id', auth, async (req, res) => {
  try {
    const { id } = req.params;
    const deleted = await advancedAutomationService.deleteAutomationRule(id);
    
    if (!deleted) {
      return res.status(404).json({
        success: false,
        message: 'Automation rule not found'
      });
    }

    res.json({
      success: true,
      message: 'Automation rule deleted successfully'
    });
  } catch (error) {
    console.error('Delete automation rule error:', error);
    res.status(500).json({
      success: false,
      message: error.message || 'Failed to delete automation rule'
    });
  }
});

/**
 * @route   POST /api/automation/triggers
 * @desc    Create trigger
 * @access  Private
 */
router.post('/triggers', auth, [
  body('name').isString().withMessage('Name must be a string'),
  body('type').isString().withMessage('Type must be a string'),
  body('parameters').optional().isObject().withMessage('Parameters must be an object'),
  body('isActive').optional().isBoolean().withMessage('Is active must be a boolean')
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

    const triggerData = req.body;
    const userId = req.user.id;
    
    const trigger = await advancedAutomationService.createTrigger(userId, triggerData);

    res.json({
      success: true,
      message: 'Trigger created successfully',
      data: trigger
    });
  } catch (error) {
    console.error('Create trigger error:', error);
    res.status(500).json({
      success: false,
      message: error.message || 'Failed to create trigger'
    });
  }
});

/**
 * @route   GET /api/automation/triggers
 * @desc    Get user triggers
 * @access  Private
 */
router.get('/triggers', auth, async (req, res) => {
  try {
    const userId = req.user.id;
    const triggers = await advancedAutomationService.getUserTriggers(userId);

    res.json({
      success: true,
      data: triggers
    });
  } catch (error) {
    console.error('Get triggers error:', error);
    res.status(500).json({
      success: false,
      message: error.message || 'Failed to get triggers'
    });
  }
});

/**
 * @route   GET /api/automation/triggers/:id
 * @desc    Get specific trigger
 * @access  Private
 */
router.get('/triggers/:id', auth, async (req, res) => {
  try {
    const { id } = req.params;
    const trigger = await advancedAutomationService.getTrigger(id);
    
    if (!trigger) {
      return res.status(404).json({
        success: false,
        message: 'Trigger not found'
      });
    }

    res.json({
      success: true,
      data: trigger
    });
  } catch (error) {
    console.error('Get trigger error:', error);
    res.status(500).json({
      success: false,
      message: error.message || 'Failed to get trigger'
    });
  }
});

/**
 * @route   PUT /api/automation/triggers/:id
 * @desc    Update trigger
 * @access  Private
 */
router.put('/triggers/:id', auth, [
  body('updates').isObject().withMessage('Updates must be an object')
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
    const { updates } = req.body;
    
    const updatedTrigger = await advancedAutomationService.updateTrigger(id, updates);
    
    if (!updatedTrigger) {
      return res.status(404).json({
        success: false,
        message: 'Trigger not found'
      });
    }

    res.json({
      success: true,
      message: 'Trigger updated successfully',
      data: updatedTrigger
    });
  } catch (error) {
    console.error('Update trigger error:', error);
    res.status(500).json({
      success: false,
      message: error.message || 'Failed to update trigger'
    });
  }
});

/**
 * @route   DELETE /api/automation/triggers/:id
 * @desc    Delete trigger
 * @access  Private
 */
router.delete('/triggers/:id', auth, async (req, res) => {
  try {
    const { id } = req.params;
    const deleted = await advancedAutomationService.deleteTrigger(id);
    
    if (!deleted) {
      return res.status(404).json({
        success: false,
        message: 'Trigger not found'
      });
    }

    res.json({
      success: true,
      message: 'Trigger deleted successfully'
    });
  } catch (error) {
    console.error('Delete trigger error:', error);
    res.status(500).json({
      success: false,
      message: error.message || 'Failed to delete trigger'
    });
  }
});

/**
 * @route   GET /api/automation/templates
 * @desc    Get automation templates
 * @access  Private
 */
router.get('/templates', auth, async (req, res) => {
  try {
    const templates = [
      {
        id: 'content_publishing',
        name: 'Content Publishing Workflow',
        description: 'Automated content publishing workflow',
        triggers: [
          { type: 'schedule', parameters: { cron: '0 9 * * *' } }
        ],
        actions: [
          { type: 'create_content', parameters: { template: 'daily_post' } },
          { type: 'publish_content', parameters: { platforms: ['facebook', 'twitter'] } }
        ],
        conditions: [
          { type: 'time', operator: 'between', value: { start: '09:00', end: '17:00' } }
        ]
      },
      {
        id: 'email_campaign',
        name: 'Email Campaign Automation',
        description: 'Automated email campaign workflow',
        triggers: [
          { type: 'user_action', parameters: { action: 'signup' } }
        ],
        actions: [
          { type: 'send_email', parameters: { template: 'welcome_email' } },
          { type: 'update_analytics', parameters: { event: 'email_sent' } }
        ],
        conditions: [
          { type: 'user_activity', operator: 'equals', value: 'new_user' }
        ]
      },
      {
        id: 'social_media',
        name: 'Social Media Automation',
        description: 'Automated social media posting',
        triggers: [
          { type: 'schedule', parameters: { cron: '0 */4 * * *' } }
        ],
        actions: [
          { type: 'create_content', parameters: { type: 'social_post' } },
          { type: 'publish_content', parameters: { platforms: ['instagram', 'linkedin'] } }
        ],
        conditions: [
          { type: 'time', operator: 'between', value: { start: '08:00', end: '20:00' } }
        ]
      }
    ];

    res.json({
      success: true,
      data: templates
    });
  } catch (error) {
    console.error('Get automation templates error:', error);
    res.status(500).json({
      success: false,
      message: error.message || 'Failed to get automation templates'
    });
  }
});

module.exports = router;



