const express = require('express');
const router = express.Router();

/**
 * Marketing Automation API Routes
 * Handles all marketing automation operations
 */

// Get all workflows
router.get('/workflows', async (req, res) => {
  try {
    const marketingAutomation = req.app.locals.marketingAutomation;
    const workflows = marketingAutomation.getWorkflows();
    
    res.json({
      success: true,
      data: workflows
    });
  } catch (error) {
    console.error('Error getting workflows:', error);
    res.status(500).json({
      success: false,
      error: 'Failed to get workflows'
    });
  }
});

// Get workflow by ID
router.get('/workflows/:id', async (req, res) => {
  try {
    const { id } = req.params;
    const marketingAutomation = req.app.locals.marketingAutomation;
    const workflow = marketingAutomation.getWorkflow(id);
    
    if (!workflow) {
      return res.status(404).json({
        success: false,
        error: 'Workflow not found'
      });
    }
    
    res.json({
      success: true,
      data: workflow
    });
  } catch (error) {
    console.error('Error getting workflow:', error);
    res.status(500).json({
      success: false,
      error: 'Failed to get workflow'
    });
  }
});

// Create new workflow
router.post('/workflows', async (req, res) => {
  try {
    const workflowData = req.body;
    const marketingAutomation = req.app.locals.marketingAutomation;
    const workflow = await marketingAutomation.createWorkflow(workflowData);
    
    res.json({
      success: true,
      data: workflow
    });
  } catch (error) {
    console.error('Error creating workflow:', error);
    res.status(500).json({
      success: false,
      error: 'Failed to create workflow'
    });
  }
});

// Update workflow
router.put('/workflows/:id', async (req, res) => {
  try {
    const { id } = req.params;
    const updates = req.body;
    const marketingAutomation = req.app.locals.marketingAutomation;
    const workflow = await marketingAutomation.updateWorkflow(id, updates);
    
    res.json({
      success: true,
      data: workflow
    });
  } catch (error) {
    console.error('Error updating workflow:', error);
    res.status(500).json({
      success: false,
      error: 'Failed to update workflow'
    });
  }
});

// Delete workflow
router.delete('/workflows/:id', async (req, res) => {
  try {
    const { id } = req.params;
    const marketingAutomation = req.app.locals.marketingAutomation;
    const result = await marketingAutomation.deleteWorkflow(id);
    
    res.json({
      success: true,
      data: result
    });
  } catch (error) {
    console.error('Error deleting workflow:', error);
    res.status(500).json({
      success: false,
      error: 'Failed to delete workflow'
    });
  }
});

// Toggle workflow status
router.post('/workflows/:id/toggle', async (req, res) => {
  try {
    const { id } = req.params;
    const marketingAutomation = req.app.locals.marketingAutomation;
    const workflow = await marketingAutomation.toggleWorkflow(id);
    
    res.json({
      success: true,
      data: workflow
    });
  } catch (error) {
    console.error('Error toggling workflow:', error);
    res.status(500).json({
      success: false,
      error: 'Failed to toggle workflow'
    });
  }
});

// Get all campaigns
router.get('/campaigns', async (req, res) => {
  try {
    const marketingAutomation = req.app.locals.marketingAutomation;
    const campaigns = marketingAutomation.getCampaigns();
    
    res.json({
      success: true,
      data: campaigns
    });
  } catch (error) {
    console.error('Error getting campaigns:', error);
    res.status(500).json({
      success: false,
      error: 'Failed to get campaigns'
    });
  }
});

// Get campaign by ID
router.get('/campaigns/:id', async (req, res) => {
  try {
    const { id } = req.params;
    const marketingAutomation = req.app.locals.marketingAutomation;
    const campaign = marketingAutomation.getCampaign(id);
    
    if (!campaign) {
      return res.status(404).json({
        success: false,
        error: 'Campaign not found'
      });
    }
    
    res.json({
      success: true,
      data: campaign
    });
  } catch (error) {
    console.error('Error getting campaign:', error);
    res.status(500).json({
      success: false,
      error: 'Failed to get campaign'
    });
  }
});

// Create new campaign
router.post('/campaigns', async (req, res) => {
  try {
    const campaignData = req.body;
    const marketingAutomation = req.app.locals.marketingAutomation;
    const campaign = await marketingAutomation.createCampaign(campaignData);
    
    res.json({
      success: true,
      data: campaign
    });
  } catch (error) {
    console.error('Error creating campaign:', error);
    res.status(500).json({
      success: false,
      error: 'Failed to create campaign'
    });
  }
});

// Schedule campaign
router.post('/campaigns/:id/schedule', async (req, res) => {
  try {
    const { id } = req.params;
    const { scheduledDate } = req.body;
    const marketingAutomation = req.app.locals.marketingAutomation;
    const campaign = await marketingAutomation.scheduleCampaign(id, scheduledDate);
    
    res.json({
      success: true,
      data: campaign
    });
  } catch (error) {
    console.error('Error scheduling campaign:', error);
    res.status(500).json({
      success: false,
      error: 'Failed to schedule campaign'
    });
  }
});

// Get all templates
router.get('/templates', async (req, res) => {
  try {
    const marketingAutomation = req.app.locals.marketingAutomation;
    const templates = marketingAutomation.getTemplates();
    
    res.json({
      success: true,
      data: templates
    });
  } catch (error) {
    console.error('Error getting templates:', error);
    res.status(500).json({
      success: false,
      error: 'Failed to get templates'
    });
  }
});

// Get template by ID
router.get('/templates/:id', async (req, res) => {
  try {
    const { id } = req.params;
    const marketingAutomation = req.app.locals.marketingAutomation;
    const template = marketingAutomation.getTemplate(id);
    
    if (!template) {
      return res.status(404).json({
        success: false,
        error: 'Template not found'
      });
    }
    
    res.json({
      success: true,
      data: template
    });
  } catch (error) {
    console.error('Error getting template:', error);
    res.status(500).json({
      success: false,
      error: 'Failed to get template'
    });
  }
});

// Create new template
router.post('/templates', async (req, res) => {
  try {
    const templateData = req.body;
    const marketingAutomation = req.app.locals.marketingAutomation;
    const template = await marketingAutomation.createTemplate(templateData);
    
    res.json({
      success: true,
      data: template
    });
  } catch (error) {
    console.error('Error creating template:', error);
    res.status(500).json({
      success: false,
      error: 'Failed to create template'
    });
  }
});

// Get automation stats
router.get('/stats', async (req, res) => {
  try {
    const marketingAutomation = req.app.locals.marketingAutomation;
    const stats = marketingAutomation.getStats();
    
    res.json({
      success: true,
      data: stats
    });
  } catch (error) {
    console.error('Error getting automation stats:', error);
    res.status(500).json({
      success: false,
      error: 'Failed to get automation stats'
    });
  }
});

// Get automation rules
router.get('/rules', async (req, res) => {
  try {
    const marketingAutomation = req.app.locals.marketingAutomation;
    const rules = marketingAutomation.getAutomationRules();
    
    res.json({
      success: true,
      data: rules
    });
  } catch (error) {
    console.error('Error getting automation rules:', error);
    res.status(500).json({
      success: false,
      error: 'Failed to get automation rules'
    });
  }
});

// Add automation rule
router.post('/rules', async (req, res) => {
  try {
    const { category, ruleName, rule } = req.body;
    const marketingAutomation = req.app.locals.marketingAutomation;
    
    marketingAutomation.addAutomationRule(category, ruleName, rule);
    
    res.json({
      success: true,
      message: 'Automation rule added successfully'
    });
  } catch (error) {
    console.error('Error adding automation rule:', error);
    res.status(500).json({
      success: false,
      error: 'Failed to add automation rule'
    });
  }
});

// Remove automation rule
router.delete('/rules/:category/:ruleName', async (req, res) => {
  try {
    const { category, ruleName } = req.params;
    const marketingAutomation = req.app.locals.marketingAutomation;
    
    marketingAutomation.removeAutomationRule(category, ruleName);
    
    res.json({
      success: true,
      message: 'Automation rule removed successfully'
    });
  } catch (error) {
    console.error('Error removing automation rule:', error);
    res.status(500).json({
      success: false,
      error: 'Failed to remove automation rule'
    });
  }
});

// Execute workflow manually
router.post('/workflows/:id/execute', async (req, res) => {
  try {
    const { id } = req.params;
    const marketingAutomation = req.app.locals.marketingAutomation;
    const workflow = marketingAutomation.getWorkflow(id);
    
    if (!workflow) {
      return res.status(404).json({
        success: false,
        error: 'Workflow not found'
      });
    }
    
    // Simulate workflow execution
    workflow.lastRun = new Date();
    marketingAutomation.updateWorkflow(id, workflow);
    
    res.json({
      success: true,
      message: 'Workflow executed successfully',
      data: workflow
    });
  } catch (error) {
    console.error('Error executing workflow:', error);
    res.status(500).json({
      success: false,
      error: 'Failed to execute workflow'
    });
  }
});

// Execute campaign manually
router.post('/campaigns/:id/execute', async (req, res) => {
  try {
    const { id } = req.params;
    const marketingAutomation = req.app.locals.marketingAutomation;
    const campaign = marketingAutomation.getCampaign(id);
    
    if (!campaign) {
      return res.status(404).json({
        success: false,
        error: 'Campaign not found'
      });
    }
    
    // Execute campaign
    await marketingAutomation.executeCampaign(id);
    
    res.json({
      success: true,
      message: 'Campaign executed successfully',
      data: campaign
    });
  } catch (error) {
    console.error('Error executing campaign:', error);
    res.status(500).json({
      success: false,
      error: 'Failed to execute campaign'
    });
  }
});

// Get automation performance
router.get('/performance', async (req, res) => {
  try {
    const { period = '7d' } = req.query;
    
    // Mock performance data
    const performance = {
      workflows: {
        total: 12,
        active: 8,
        paused: 4,
        executed: 156
      },
      campaigns: {
        total: 25,
        scheduled: 5,
        sent: 18,
        draft: 2
      },
      emails: {
        sent: 45230,
        delivered: 44120,
        opened: 13236,
        clicked: 3961
      },
      automation: {
        rate: 78.5,
        efficiency: 92.3,
        roi: 340
      }
    };
    
    res.json({
      success: true,
      data: performance
    });
  } catch (error) {
    console.error('Error getting automation performance:', error);
    res.status(500).json({
      success: false,
      error: 'Failed to get automation performance'
    });
  }
});

module.exports = router;

