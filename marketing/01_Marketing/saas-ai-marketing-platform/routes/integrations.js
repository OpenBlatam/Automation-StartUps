const express = require('express');
const router = express.Router();
const auth = require('../middleware/auth');
const integrationService = require('../services/integrationService');
const { body, validationResult } = require('express-validator');

// Initialize integration service
integrationService.initialize();

/**
 * @route   GET /api/integrations/available
 * @desc    Get available integrations
 * @access  Private
 */
router.get('/available', auth, async (req, res) => {
  try {
    const integrations = integrationService.getAvailableIntegrations();

    res.json({
      success: true,
      data: integrations
    });
  } catch (error) {
    console.error('Get available integrations error:', error);
    res.status(500).json({
      success: false,
      message: error.message || 'Failed to get available integrations'
    });
  }
});

/**
 * @route   POST /api/integrations/connect
 * @desc    Connect integration
 * @access  Private
 */
router.post('/connect', auth, [
  body('type').isIn(['social-media', 'email-marketing', 'crm', 'analytics', 'content-management']).withMessage('Invalid integration type'),
  body('platform').notEmpty().withMessage('Platform is required'),
  body('credentials').isObject().withMessage('Credentials must be an object')
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

    const { type, platform, credentials } = req.body;
    const integration = await integrationService.connectIntegration(
      req.user.id,
      type,
      platform,
      credentials
    );

    res.status(201).json({
      success: true,
      message: 'Integration connected successfully',
      data: integration
    });
  } catch (error) {
    console.error('Connect integration error:', error);
    res.status(500).json({
      success: false,
      message: error.message || 'Failed to connect integration'
    });
  }
});

/**
 * @route   GET /api/integrations
 * @desc    Get user integrations
 * @access  Private
 */
router.get('/', auth, async (req, res) => {
  try {
    const integrations = await integrationService.getUserIntegrations(req.user.id);

    res.json({
      success: true,
      data: integrations
    });
  } catch (error) {
    console.error('Get user integrations error:', error);
    res.status(500).json({
      success: false,
      message: error.message || 'Failed to get user integrations'
    });
  }
});

/**
 * @route   POST /api/integrations/:id/test
 * @desc    Test integration connection
 * @access  Private
 */
router.post('/:id/test', auth, async (req, res) => {
  try {
    const { id } = req.params;
    const integration = integrationService.integrations.get(id);
    
    if (!integration || integration.userId !== req.user.id) {
      return res.status(404).json({
        success: false,
        message: 'Integration not found'
      });
    }

    const testResult = await integrationService.testConnection(
      integration.type,
      integration.platform,
      integrationService.decryptCredentials(integration.credentials)
    );

    res.json({
      success: true,
      data: testResult
    });
  } catch (error) {
    console.error('Test integration error:', error);
    res.status(500).json({
      success: false,
      message: error.message || 'Failed to test integration'
    });
  }
});

/**
 * @route   POST /api/integrations/:id/publish
 * @desc    Publish content to integration
 * @access  Private
 */
router.post('/:id/publish', auth, [
  body('contentId').isMongoId().withMessage('Valid content ID is required'),
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

    const { id } = req.params;
    const { contentId, options = {} } = req.body;

    const result = await integrationService.publishContent(id, contentId, options);

    res.json({
      success: true,
      message: 'Content published successfully',
      data: result
    });
  } catch (error) {
    console.error('Publish content error:', error);
    res.status(500).json({
      success: false,
      message: error.message || 'Failed to publish content'
    });
  }
});

/**
 * @route   DELETE /api/integrations/:id
 * @desc    Disconnect integration
 * @access  Private
 */
router.delete('/:id', auth, async (req, res) => {
  try {
    const { id } = req.params;
    const disconnected = await integrationService.disconnectIntegration(id, req.user.id);

    if (!disconnected) {
      return res.status(404).json({
        success: false,
        message: 'Integration not found'
      });
    }

    res.json({
      success: true,
      message: 'Integration disconnected successfully'
    });
  } catch (error) {
    console.error('Disconnect integration error:', error);
    res.status(500).json({
      success: false,
      message: error.message || 'Failed to disconnect integration'
    });
  }
});

/**
 * @route   GET /api/integrations/:id/webhooks
 * @desc    Get integration webhooks
 * @access  Private
 */
router.get('/:id/webhooks', auth, async (req, res) => {
  try {
    const { id } = req.params;
    const integration = integrationService.integrations.get(id);
    
    if (!integration || integration.userId !== req.user.id) {
      return res.status(404).json({
        success: false,
        message: 'Integration not found'
      });
    }

    const webhooks = Array.from(integrationService.webhooks.values())
      .filter(webhook => webhook.integrationId === id);

    res.json({
      success: true,
      data: webhooks
    });
  } catch (error) {
    console.error('Get integration webhooks error:', error);
    res.status(500).json({
      success: false,
      message: error.message || 'Failed to get integration webhooks'
    });
  }
});

/**
 * @route   POST /api/integrations/:id/webhooks
 * @desc    Create integration webhook
 * @access  Private
 */
router.post('/:id/webhooks', auth, [
  body('events').isArray().withMessage('Events must be an array')
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
    const integration = integrationService.integrations.get(id);
    
    if (!integration || integration.userId !== req.user.id) {
      return res.status(404).json({
        success: false,
        message: 'Integration not found'
      });
    }

    const webhook = await integrationService.setupWebhook(
      id,
      integration.type,
      integration.platform
    );

    res.status(201).json({
      success: true,
      message: 'Webhook created successfully',
      data: webhook
    });
  } catch (error) {
    console.error('Create webhook error:', error);
    res.status(500).json({
      success: false,
      message: error.message || 'Failed to create webhook'
    });
  }
});

/**
 * @route   GET /api/integrations/:id/stats
 * @desc    Get integration statistics
 * @access  Private
 */
router.get('/:id/stats', auth, async (req, res) => {
  try {
    const { id } = req.params;
    const integration = integrationService.integrations.get(id);
    
    if (!integration || integration.userId !== req.user.id) {
      return res.status(404).json({
        success: false,
        message: 'Integration not found'
      });
    }

    res.json({
      success: true,
      data: integration.stats
    });
  } catch (error) {
    console.error('Get integration stats error:', error);
    res.status(500).json({
      success: false,
      message: error.message || 'Failed to get integration statistics'
    });
  }
});

/**
 * @route   PUT /api/integrations/:id/settings
 * @desc    Update integration settings
 * @access  Private
 */
router.put('/:id/settings', auth, [
  body('autoSync').optional().isBoolean().withMessage('AutoSync must be a boolean'),
  body('syncInterval').optional().isIn(['hourly', 'daily', 'weekly']).withMessage('Invalid sync interval'),
  body('webhookEnabled').optional().isBoolean().withMessage('WebhookEnabled must be a boolean')
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
    const integration = integrationService.integrations.get(id);
    
    if (!integration || integration.userId !== req.user.id) {
      return res.status(404).json({
        success: false,
        message: 'Integration not found'
      });
    }

    // Update settings
    Object.assign(integration.settings, req.body);
    integrationService.integrations.set(id, integration);

    res.json({
      success: true,
      message: 'Integration settings updated successfully',
      data: integration.settings
    });
  } catch (error) {
    console.error('Update integration settings error:', error);
    res.status(500).json({
      success: false,
      message: error.message || 'Failed to update integration settings'
    });
  }
});

/**
 * @route   POST /api/integrations/:id/sync
 * @desc    Manually sync integration
 * @access  Private
 */
router.post('/:id/sync', auth, async (req, res) => {
  try {
    const { id } = req.params;
    const integration = integrationService.integrations.get(id);
    
    if (!integration || integration.userId !== req.user.id) {
      return res.status(404).json({
        success: false,
        message: 'Integration not found'
      });
    }

    // This would trigger a manual sync
    // For now, we'll just update the last sync time
    integration.lastSync = new Date();
    integrationService.integrations.set(id, integration);

    res.json({
      success: true,
      message: 'Integration sync initiated successfully',
      data: {
        lastSync: integration.lastSync
      }
    });
  } catch (error) {
    console.error('Sync integration error:', error);
    res.status(500).json({
      success: false,
      message: error.message || 'Failed to sync integration'
    });
  }
});

/**
 * @route   GET /api/integrations/:type/platforms
 * @desc    Get platforms for integration type
 * @access  Private
 */
router.get('/:type/platforms', auth, async (req, res) => {
  try {
    const { type } = req.params;
    const availableIntegrations = integrationService.getAvailableIntegrations();
    
    if (!availableIntegrations[type]) {
      return res.status(404).json({
        success: false,
        message: 'Integration type not found'
      });
    }

    res.json({
      success: true,
      data: availableIntegrations[type].platforms
    });
  } catch (error) {
    console.error('Get platforms error:', error);
    res.status(500).json({
      success: false,
      message: error.message || 'Failed to get platforms'
    });
  }
});

module.exports = router;






