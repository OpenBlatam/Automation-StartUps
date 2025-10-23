const express = require('express');
const router = express.Router();

/**
 * Reality Bending API Routes
 * Handles all reality bending operations
 */

// Get reality state
router.get('/state', async (req, res) => {
  try {
    const realityBending = req.app.locals.realityBending;
    const state = realityBending.getRealityState();
    
    res.json({
      success: true,
      data: state
    });
  } catch (error) {
    console.error('Error getting reality state:', error);
    res.status(500).json({
      success: false,
      error: 'Failed to get reality state'
    });
  }
});

// Get reality level description
router.get('/level/:level', async (req, res) => {
  try {
    const { level } = req.params;
    const realityBending = req.app.locals.realityBending;
    
    const description = realityBending.getRealityLevelDescription(parseFloat(level));
    
    res.json({
      success: true,
      data: {
        level: parseFloat(level),
        description
      }
    });
  } catch (error) {
    console.error('Error getting reality level:', error);
    res.status(500).json({
      success: false,
      error: 'Failed to get reality level'
    });
  }
});

// Start reality process
router.post('/processes/:processName/start', async (req, res) => {
  try {
    const { processName } = req.params;
    const realityBending = req.app.locals.realityBending;
    
    realityBending.startRealityProcess(processName);
    
    res.json({
      success: true,
      message: `Reality process ${processName} started successfully`
    });
  } catch (error) {
    console.error('Error starting reality process:', error);
    res.status(500).json({
      success: false,
      error: 'Failed to start reality process'
    });
  }
});

// Stop reality process
router.post('/processes/:processName/stop', async (req, res) => {
  try {
    const { processName } = req.params;
    const realityBending = req.app.locals.realityBending;
    
    realityBending.stopRealityProcess(processName);
    
    res.json({
      success: true,
      message: `Reality process ${processName} stopped successfully`
    });
  } catch (error) {
    console.error('Error stopping reality process:', error);
    res.status(500).json({
      success: false,
      error: 'Failed to stop reality process'
    });
  }
});

// Get reality distortions
router.get('/distortions', async (req, res) => {
  try {
    const realityBending = req.app.locals.realityBending;
    const state = realityBending.getRealityState();
    
    res.json({
      success: true,
      data: state.distortions
    });
  } catch (error) {
    console.error('Error getting reality distortions:', error);
    res.status(500).json({
      success: false,
      error: 'Failed to get reality distortions'
    });
  }
});

// Get reality visions
router.get('/visions', async (req, res) => {
  try {
    const realityBending = req.app.locals.realityBending;
    const state = realityBending.getRealityState();
    
    res.json({
      success: true,
      data: state.visions
    });
  } catch (error) {
    console.error('Error getting reality visions:', error);
    res.status(500).json({
      success: false,
      error: 'Failed to get reality visions'
    });
  }
});

// Get reality patterns
router.get('/patterns', async (req, res) => {
  try {
    const realityBending = req.app.locals.realityBending;
    const state = realityBending.getRealityState();
    
    res.json({
      success: true,
      data: state.patterns
    });
  } catch (error) {
    console.error('Error getting reality patterns:', error);
    res.status(500).json({
      success: false,
      error: 'Failed to get reality patterns'
    });
  }
});

// Get reality capabilities
router.get('/capabilities', async (req, res) => {
  try {
    const realityBending = req.app.locals.realityBending;
    const state = realityBending.getRealityState();
    
    res.json({
      success: true,
      data: {
        capabilities: state.capabilities,
        level: state.level
      }
    });
  } catch (error) {
    console.error('Error getting reality capabilities:', error);
    res.status(500).json({
      success: false,
      error: 'Failed to get reality capabilities'
    });
  }
});

// Get reality matrix
router.get('/matrix', async (req, res) => {
  try {
    const realityBending = req.app.locals.realityBending;
    const state = realityBending.getRealityState();
    
    res.json({
      success: true,
      data: {
        matrix: state.matrix,
        level: state.level
      }
    });
  } catch (error) {
    console.error('Error getting reality matrix:', error);
    res.status(500).json({
      success: false,
      error: 'Failed to get reality matrix'
    });
  }
});

// Bend reality manually
router.post('/bend', async (req, res) => {
  try {
    const realityBending = req.app.locals.realityBending;
    await realityBending.bendReality();
    
    const state = realityBending.getRealityState();
    
    res.json({
      success: true,
      message: 'Reality bent successfully',
      data: state
    });
  } catch (error) {
    console.error('Error bending reality:', error);
    res.status(500).json({
      success: false,
      error: 'Failed to bend reality'
    });
  }
});

// Reset reality bending
router.post('/reset', async (req, res) => {
  try {
    const realityBending = req.app.locals.realityBending;
    realityBending.resetRealityBending();
    
    res.json({
      success: true,
      message: 'Reality bending reset successfully'
    });
  } catch (error) {
    console.error('Error resetting reality bending:', error);
    res.status(500).json({
      success: false,
      error: 'Failed to reset reality bending'
    });
  }
});

// Get reality evolution history
router.get('/history', async (req, res) => {
  try {
    // Mock reality evolution history
    const history = [
      {
        timestamp: new Date(Date.now() - 300000).toISOString(),
        level: 85.2,
        space: 78.5,
        time: 92.1,
        matter: 75.3,
        spaceManipulation: true,
        timeManipulation: true
      },
      {
        timestamp: new Date(Date.now() - 600000).toISOString(),
        level: 82.1,
        space: 75.3,
        time: 89.8,
        matter: 72.1,
        spaceManipulation: true,
        timeManipulation: false
      },
      {
        timestamp: new Date(Date.now() - 900000).toISOString(),
        level: 79.8,
        space: 72.1,
        time: 87.5,
        matter: 69.8,
        spaceManipulation: false,
        timeManipulation: false
      }
    ];
    
    res.json({
      success: true,
      data: history
    });
  } catch (error) {
    console.error('Error getting reality history:', error);
    res.status(500).json({
      success: false,
      error: 'Failed to get reality history'
    });
  }
});

// Get reality metrics
router.get('/metrics', async (req, res) => {
  try {
    const realityBending = req.app.locals.realityBending;
    const state = realityBending.getRealityState();
    
    res.json({
      success: true,
      data: {
        level: state.level,
        matrix: state.matrix,
        capabilities: state.capabilities,
        processes: state.processes
      }
    });
  } catch (error) {
    console.error('Error getting reality metrics:', error);
    res.status(500).json({
      success: false,
      error: 'Failed to get reality metrics'
    });
  }
});

// Get reality recommendations
router.get('/recommendations', async (req, res) => {
  try {
    const realityBending = req.app.locals.realityBending;
    const recommendations = realityBending.generateRealityRecommendations();
    
    res.json({
      success: true,
      data: recommendations
    });
  } catch (error) {
    console.error('Error getting reality recommendations:', error);
    res.status(500).json({
      success: false,
      error: 'Failed to get reality recommendations'
    });
  }
});

module.exports = router;

