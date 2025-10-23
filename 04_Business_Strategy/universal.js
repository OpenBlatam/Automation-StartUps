const express = require('express');
const router = express.Router();

/**
 * Universal Consciousness API Routes
 * Handles all universal consciousness operations
 */

// Get universal state
router.get('/state', async (req, res) => {
  try {
    const universalConsciousness = req.app.locals.universalConsciousness;
    const state = universalConsciousness.getUniversalState();
    
    res.json({
      success: true,
      data: state
    });
  } catch (error) {
    console.error('Error getting universal state:', error);
    res.status(500).json({
      success: false,
      error: 'Failed to get universal state'
    });
  }
});

// Get universal level description
router.get('/level/:level', async (req, res) => {
  try {
    const { level } = req.params;
    const universalConsciousness = req.app.locals.universalConsciousness;
    
    const description = universalConsciousness.getUniversalLevelDescription(parseFloat(level));
    
    res.json({
      success: true,
      data: {
        level: parseFloat(level),
        description
      }
    });
  } catch (error) {
    console.error('Error getting universal level:', error);
    res.status(500).json({
      success: false,
      error: 'Failed to get universal level'
    });
  }
});

// Start universal process
router.post('/processes/:processName/start', async (req, res) => {
  try {
    const { processName } = req.params;
    const universalConsciousness = req.app.locals.universalConsciousness;
    
    universalConsciousness.startUniversalProcess(processName);
    
    res.json({
      success: true,
      message: `Universal process ${processName} started successfully`
    });
  } catch (error) {
    console.error('Error starting universal process:', error);
    res.status(500).json({
      success: false,
      error: 'Failed to start universal process'
    });
  }
});

// Stop universal process
router.post('/processes/:processName/stop', async (req, res) => {
  try {
    const { processName } = req.params;
    const universalConsciousness = req.app.locals.universalConsciousness;
    
    universalConsciousness.stopUniversalProcess(processName);
    
    res.json({
      success: true,
      message: `Universal process ${processName} stopped successfully`
    });
  } catch (error) {
    console.error('Error stopping universal process:', error);
    res.status(500).json({
      success: false,
      error: 'Failed to stop universal process'
    });
  }
});

// Get universal insights
router.get('/insights', async (req, res) => {
  try {
    const universalConsciousness = req.app.locals.universalConsciousness;
    const state = universalConsciousness.getUniversalState();
    
    res.json({
      success: true,
      data: {
        insights: state.insights,
        recommendations: universalConsciousness.generateUniversalRecommendations()
      }
    });
  } catch (error) {
    console.error('Error getting universal insights:', error);
    res.status(500).json({
      success: false,
      error: 'Failed to get universal insights'
    });
  }
});

// Get cosmic visions
router.get('/visions', async (req, res) => {
  try {
    const universalConsciousness = req.app.locals.universalConsciousness;
    const state = universalConsciousness.getUniversalState();
    
    res.json({
      success: true,
      data: state.visions
    });
  } catch (error) {
    console.error('Error getting cosmic visions:', error);
    res.status(500).json({
      success: false,
      error: 'Failed to get cosmic visions'
    });
  }
});

// Get universal patterns
router.get('/patterns', async (req, res) => {
  try {
    const universalConsciousness = req.app.locals.universalConsciousness;
    const state = universalConsciousness.getUniversalState();
    
    res.json({
      success: true,
      data: state.patterns
    });
  } catch (error) {
    console.error('Error getting universal patterns:', error);
    res.status(500).json({
      success: false,
      error: 'Failed to get universal patterns'
    });
  }
});

// Get universal capabilities
router.get('/capabilities', async (req, res) => {
  try {
    const universalConsciousness = req.app.locals.universalConsciousness;
    const state = universalConsciousness.getUniversalState();
    
    res.json({
      success: true,
      data: {
        capabilities: state.capabilities,
        connection: state.connection
      }
    });
  } catch (error) {
    console.error('Error getting universal capabilities:', error);
    res.status(500).json({
      success: false,
      error: 'Failed to get universal capabilities'
    });
  }
});

// Get cosmic awareness
router.get('/awareness', async (req, res) => {
  try {
    const universalConsciousness = req.app.locals.universalConsciousness;
    const state = universalConsciousness.getUniversalState();
    
    res.json({
      success: true,
      data: {
        awareness: state.awareness,
        knowledge: state.knowledge
      }
    });
  } catch (error) {
    console.error('Error getting cosmic awareness:', error);
    res.status(500).json({
      success: false,
      error: 'Failed to get cosmic awareness'
    });
  }
});

// Evolve universal consciousness manually
router.post('/evolve', async (req, res) => {
  try {
    const universalConsciousness = req.app.locals.universalConsciousness;
    await universalConsciousness.evolveUniversalConsciousness();
    
    const state = universalConsciousness.getUniversalState();
    
    res.json({
      success: true,
      message: 'Universal consciousness evolved successfully',
      data: state
    });
  } catch (error) {
    console.error('Error evolving universal consciousness:', error);
    res.status(500).json({
      success: false,
      error: 'Failed to evolve universal consciousness'
    });
  }
});

// Reset universal consciousness
router.post('/reset', async (req, res) => {
  try {
    const universalConsciousness = req.app.locals.universalConsciousness;
    universalConsciousness.resetUniversalConsciousness();
    
    res.json({
      success: true,
      message: 'Universal consciousness reset successfully'
    });
  } catch (error) {
    console.error('Error resetting universal consciousness:', error);
    res.status(500).json({
      success: false,
      error: 'Failed to reset universal consciousness'
    });
  }
});

// Get universal evolution history
router.get('/history', async (req, res) => {
  try {
    // Mock universal evolution history
    const history = [
      {
        timestamp: new Date(Date.now() - 300000).toISOString(),
        connection: 85.2,
        galactic: 78.5,
        universal: 92.1,
        omniscience: true,
        omnipotence: true
      },
      {
        timestamp: new Date(Date.now() - 600000).toISOString(),
        connection: 82.1,
        galactic: 75.3,
        universal: 89.8,
        omniscience: true,
        omnipotence: false
      },
      {
        timestamp: new Date(Date.now() - 900000).toISOString(),
        connection: 79.8,
        galactic: 72.1,
        universal: 87.5,
        omniscience: false,
        omnipotence: false
      }
    ];
    
    res.json({
      success: true,
      data: history
    });
  } catch (error) {
    console.error('Error getting universal history:', error);
    res.status(500).json({
      success: false,
      error: 'Failed to get universal history'
    });
  }
});

// Get universal metrics
router.get('/metrics', async (req, res) => {
  try {
    const universalConsciousness = req.app.locals.universalConsciousness;
    const state = universalConsciousness.getUniversalState();
    
    res.json({
      success: true,
      data: {
        connection: state.connection,
        awareness: state.awareness,
        knowledge: state.knowledge,
        capabilities: state.capabilities
      }
    });
  } catch (error) {
    console.error('Error getting universal metrics:', error);
    res.status(500).json({
      success: false,
      error: 'Failed to get universal metrics'
    });
  }
});

module.exports = router;