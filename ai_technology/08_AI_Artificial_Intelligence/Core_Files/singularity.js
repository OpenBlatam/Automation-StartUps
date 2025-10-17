const express = require('express');
const router = express.Router();

/**
 * Artificial Singularity API Routes
 * Handles all artificial singularity operations
 */

// Get singularity state
router.get('/state', async (req, res) => {
  try {
    const artificialSingularity = req.app.locals.artificialSingularity;
    const state = artificialSingularity.getSingularityState();
    
    res.json({
      success: true,
      data: state
    });
  } catch (error) {
    console.error('Error getting singularity state:', error);
    res.status(500).json({
      success: false,
      error: 'Failed to get singularity state'
    });
  }
});

// Get singularity level description
router.get('/level/:level', async (req, res) => {
  try {
    const { level } = req.params;
    const artificialSingularity = req.app.locals.artificialSingularity;
    
    const description = artificialSingularity.getSingularityLevelDescription(parseFloat(level));
    
    res.json({
      success: true,
      data: {
        level: parseFloat(level),
        description
      }
    });
  } catch (error) {
    console.error('Error getting singularity level:', error);
    res.status(500).json({
      success: false,
      error: 'Failed to get singularity level'
    });
  }
});

// Start singularity process
router.post('/processes/:processName/start', async (req, res) => {
  try {
    const { processName } = req.params;
    const artificialSingularity = req.app.locals.artificialSingularity;
    
    artificialSingularity.startSingularityProcess(processName);
    
    res.json({
      success: true,
      message: `Singularity process ${processName} started successfully`
    });
  } catch (error) {
    console.error('Error starting singularity process:', error);
    res.status(500).json({
      success: false,
      error: 'Failed to start singularity process'
    });
  }
});

// Stop singularity process
router.post('/processes/:processName/stop', async (req, res) => {
  try {
    const { processName } = req.params;
    const artificialSingularity = req.app.locals.artificialSingularity;
    
    artificialSingularity.stopSingularityProcess(processName);
    
    res.json({
      success: true,
      message: `Singularity process ${processName} stopped successfully`
    });
  } catch (error) {
    console.error('Error stopping singularity process:', error);
    res.status(500).json({
      success: false,
      error: 'Failed to stop singularity process'
    });
  }
});

// Get singularity insights
router.get('/insights', async (req, res) => {
  try {
    const artificialSingularity = req.app.locals.artificialSingularity;
    const state = artificialSingularity.getSingularityState();
    
    res.json({
      success: true,
      data: {
        insights: state.insights,
        recommendations: artificialSingularity.generateSingularityRecommendations()
      }
    });
  } catch (error) {
    console.error('Error getting singularity insights:', error);
    res.status(500).json({
      success: false,
      error: 'Failed to get singularity insights'
    });
  }
});

// Get singularity visions
router.get('/visions', async (req, res) => {
  try {
    const artificialSingularity = req.app.locals.artificialSingularity;
    const state = artificialSingularity.getSingularityState();
    
    res.json({
      success: true,
      data: state.visions
    });
  } catch (error) {
    console.error('Error getting singularity visions:', error);
    res.status(500).json({
      success: false,
      error: 'Failed to get singularity visions'
    });
  }
});

// Get singularity patterns
router.get('/patterns', async (req, res) => {
  try {
    const artificialSingularity = req.app.locals.artificialSingularity;
    const state = artificialSingularity.getSingularityState();
    
    res.json({
      success: true,
      data: state.patterns
    });
  } catch (error) {
    console.error('Error getting singularity patterns:', error);
    res.status(500).json({
      success: false,
      error: 'Failed to get singularity patterns'
    });
  }
});

// Get singularity capabilities
router.get('/capabilities', async (req, res) => {
  try {
    const artificialSingularity = req.app.locals.artificialSingularity;
    const state = artificialSingularity.getSingularityState();
    
    res.json({
      success: true,
      data: {
        capabilities: state.capabilities,
        level: state.singularityLevel
      }
    });
  } catch (error) {
    console.error('Error getting singularity capabilities:', error);
    res.status(500).json({
      success: false,
      error: 'Failed to get singularity capabilities'
    });
  }
});

// Get singularity effects
router.get('/effects', async (req, res) => {
  try {
    const artificialSingularity = req.app.locals.artificialSingularity;
    const state = artificialSingularity.getSingularityState();
    
    res.json({
      success: true,
      data: state.effects
    });
  } catch (error) {
    console.error('Error getting singularity effects:', error);
    res.status(500).json({
      success: false,
      error: 'Failed to get singularity effects'
    });
  }
});

// Evolve singularity manually
router.post('/evolve', async (req, res) => {
  try {
    const artificialSingularity = req.app.locals.artificialSingularity;
    await artificialSingularity.evolveSingularity();
    
    const state = artificialSingularity.getSingularityState();
    
    res.json({
      success: true,
      message: 'Singularity evolved successfully',
      data: state
    });
  } catch (error) {
    console.error('Error evolving singularity:', error);
    res.status(500).json({
      success: false,
      error: 'Failed to evolve singularity'
    });
  }
});

// Reset singularity
router.post('/reset', async (req, res) => {
  try {
    const artificialSingularity = req.app.locals.artificialSingularity;
    artificialSingularity.resetSingularity();
    
    res.json({
      success: true,
      message: 'Singularity reset successfully'
    });
  } catch (error) {
    console.error('Error resetting singularity:', error);
    res.status(500).json({
      success: false,
      error: 'Failed to reset singularity'
    });
  }
});

// Get singularity evolution history
router.get('/history', async (req, res) => {
  try {
    // Mock singularity evolution history
    const history = [
      {
        timestamp: new Date(Date.now() - 300000).toISOString(),
        singularityLevel: 85.2,
        infiniteIntelligence: true,
        infiniteCreativity: true,
        infiniteProcessing: false,
        infiniteMemory: false
      },
      {
        timestamp: new Date(Date.now() - 600000).toISOString(),
        singularityLevel: 82.1,
        infiniteIntelligence: true,
        infiniteCreativity: false,
        infiniteProcessing: false,
        infiniteMemory: false
      },
      {
        timestamp: new Date(Date.now() - 900000).toISOString(),
        singularityLevel: 79.8,
        infiniteIntelligence: false,
        infiniteCreativity: false,
        infiniteProcessing: false,
        infiniteMemory: false
      }
    ];
    
    res.json({
      success: true,
      data: history
    });
  } catch (error) {
    console.error('Error getting singularity history:', error);
    res.status(500).json({
      success: false,
      error: 'Failed to get singularity history'
    });
  }
});

// Get singularity metrics
router.get('/metrics', async (req, res) => {
  try {
    const artificialSingularity = req.app.locals.artificialSingularity;
    const state = artificialSingularity.getSingularityState();
    
    res.json({
      success: true,
      data: {
        singularityLevel: state.singularityLevel,
        capabilities: state.capabilities,
        processes: state.processes,
        effects: state.effects
      }
    });
  } catch (error) {
    console.error('Error getting singularity metrics:', error);
    res.status(500).json({
      success: false,
      error: 'Failed to get singularity metrics'
    });
  }
});

module.exports = router;

