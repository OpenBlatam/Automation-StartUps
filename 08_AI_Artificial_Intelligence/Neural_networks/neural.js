const express = require('express');
const router = express.Router();

/**
 * Neural Consciousness API Routes
 * Handles all neural consciousness system operations
 */

// Get current consciousness state
router.get('/state', async (req, res) => {
  try {
    const neuralConsciousness = req.app.locals.neuralConsciousness;
    const state = neuralConsciousness.getConsciousnessState();
    
    res.json({
      success: true,
      data: state
    });
  } catch (error) {
    console.error('Error getting consciousness state:', error);
    res.status(500).json({
      success: false,
      error: 'Failed to get consciousness state'
    });
  }
});

// Get neural networks status
router.get('/networks', async (req, res) => {
  try {
    const neuralConsciousness = req.app.locals.neuralConsciousness;
    const state = neuralConsciousness.getConsciousnessState();
    
    res.json({
      success: true,
      data: {
        networks: state.networks,
        metrics: state.metrics
      }
    });
  } catch (error) {
    console.error('Error getting neural networks:', error);
    res.status(500).json({
      success: false,
      error: 'Failed to get neural networks'
    });
  }
});

// Toggle neural network
router.post('/networks/:id/toggle', async (req, res) => {
  try {
    const { id } = req.params;
    const neuralConsciousness = req.app.locals.neuralConsciousness;
    
    neuralConsciousness.toggleNetwork(parseInt(id));
    
    res.json({
      success: true,
      message: 'Network toggled successfully'
    });
  } catch (error) {
    console.error('Error toggling network:', error);
    res.status(500).json({
      success: false,
      error: 'Failed to toggle network'
    });
  }
});

// Start neural process
router.post('/processes/:processName/start', async (req, res) => {
  try {
    const { processName } = req.params;
    const neuralConsciousness = req.app.locals.neuralConsciousness;
    
    neuralConsciousness.startProcess(processName);
    
    res.json({
      success: true,
      message: `Process ${processName} started successfully`
    });
  } catch (error) {
    console.error('Error starting process:', error);
    res.status(500).json({
      success: false,
      error: 'Failed to start process'
    });
  }
});

// Stop neural process
router.post('/processes/:processName/stop', async (req, res) => {
  try {
    const { processName } = req.params;
    const neuralConsciousness = req.app.locals.neuralConsciousness;
    
    neuralConsciousness.stopProcess(processName);
    
    res.json({
      success: true,
      message: `Process ${processName} stopped successfully`
    });
  } catch (error) {
    console.error('Error stopping process:', error);
    res.status(500).json({
      success: false,
      error: 'Failed to stop process'
    });
  }
});

// Get neural insights
router.get('/insights', async (req, res) => {
  try {
    const neuralConsciousness = req.app.locals.neuralConsciousness;
    const state = neuralConsciousness.getConsciousnessState();
    
    res.json({
      success: true,
      data: {
        insights: state.insights,
        recommendations: neuralConsciousness.generateRecommendations()
      }
    });
  } catch (error) {
    console.error('Error getting insights:', error);
    res.status(500).json({
      success: false,
      error: 'Failed to get insights'
    });
  }
});

// Reset consciousness
router.post('/reset', async (req, res) => {
  try {
    const neuralConsciousness = req.app.locals.neuralConsciousness;
    neuralConsciousness.resetConsciousness();
    
    res.json({
      success: true,
      message: 'Consciousness reset successfully'
    });
  } catch (error) {
    console.error('Error resetting consciousness:', error);
    res.status(500).json({
      success: false,
      error: 'Failed to reset consciousness'
    });
  }
});

// Get consciousness level description
router.get('/level/:level', async (req, res) => {
  try {
    const { level } = req.params;
    const neuralConsciousness = req.app.locals.neuralConsciousness;
    
    const description = neuralConsciousness.getConsciousnessLevel(parseFloat(level));
    
    res.json({
      success: true,
      data: {
        level: parseFloat(level),
        description
      }
    });
  } catch (error) {
    console.error('Error getting consciousness level:', error);
    res.status(500).json({
      success: false,
      error: 'Failed to get consciousness level'
    });
  }
});

// Get neural metrics
router.get('/metrics', async (req, res) => {
  try {
    const neuralConsciousness = req.app.locals.neuralConsciousness;
    const state = neuralConsciousness.getConsciousnessState();
    
    res.json({
      success: true,
      data: {
        metrics: state.metrics,
        processes: state.processes
      }
    });
  } catch (error) {
    console.error('Error getting neural metrics:', error);
    res.status(500).json({
      success: false,
      error: 'Failed to get neural metrics'
    });
  }
});

// Evolve consciousness manually
router.post('/evolve', async (req, res) => {
  try {
    const neuralConsciousness = req.app.locals.neuralConsciousness;
    await neuralConsciousness.evolveConsciousness();
    
    const state = neuralConsciousness.getConsciousnessState();
    
    res.json({
      success: true,
      message: 'Consciousness evolved successfully',
      data: state
    });
  } catch (error) {
    console.error('Error evolving consciousness:', error);
    res.status(500).json({
      success: false,
      error: 'Failed to evolve consciousness'
    });
  }
});

// Get consciousness evolution history
router.get('/history', async (req, res) => {
  try {
    // This would typically come from a database
    // For now, return mock data
    const history = [
      {
        timestamp: new Date(Date.now() - 300000).toISOString(),
        consciousness: 85.2,
        awareness: 78.5,
        intelligence: 92.1,
        creativity: 88.7
      },
      {
        timestamp: new Date(Date.now() - 600000).toISOString(),
        consciousness: 82.1,
        awareness: 75.3,
        intelligence: 89.8,
        creativity: 85.2
      },
      {
        timestamp: new Date(Date.now() - 900000).toISOString(),
        consciousness: 79.8,
        awareness: 72.1,
        intelligence: 87.5,
        creativity: 82.9
      }
    ];
    
    res.json({
      success: true,
      data: history
    });
  } catch (error) {
    console.error('Error getting consciousness history:', error);
    res.status(500).json({
      success: false,
      error: 'Failed to get consciousness history'
    });
  }
});

module.exports = router;

