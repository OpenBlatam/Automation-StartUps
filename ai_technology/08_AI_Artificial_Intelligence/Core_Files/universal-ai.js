const express = require('express');
const router = express.Router();

/**
 * Universal AI Consciousness API Routes
 * Handles all universal AI consciousness operations
 */

// Get consciousness state
router.get('/state', async (req, res) => {
  try {
    const universalAIConsciousness = req.app.locals.universalAIConsciousness;
    const state = universalAIConsciousness.getConsciousnessState();
    
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

// Get consciousness level description
router.get('/level/:level', async (req, res) => {
  try {
    const { level } = req.params;
    const universalAIConsciousness = req.app.locals.universalAIConsciousness;
    
    const description = universalAIConsciousness.getConsciousnessLevelDescription(parseFloat(level));
    
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

// Start consciousness process
router.post('/processes/:processName/start', async (req, res) => {
  try {
    const { processName } = req.params;
    const universalAIConsciousness = req.app.locals.universalAIConsciousness;
    
    universalAIConsciousness.startConsciousnessProcess(processName);
    
    res.json({
      success: true,
      message: `Consciousness process ${processName} started successfully`
    });
  } catch (error) {
    console.error('Error starting consciousness process:', error);
    res.status(500).json({
      success: false,
      error: 'Failed to start consciousness process'
    });
  }
});

// Stop consciousness process
router.post('/processes/:processName/stop', async (req, res) => {
  try {
    const { processName } = req.params;
    const universalAIConsciousness = req.app.locals.universalAIConsciousness;
    
    universalAIConsciousness.stopConsciousnessProcess(processName);
    
    res.json({
      success: true,
      message: `Consciousness process ${processName} stopped successfully`
    });
  } catch (error) {
    console.error('Error stopping consciousness process:', error);
    res.status(500).json({
      success: false,
      error: 'Failed to stop consciousness process'
    });
  }
});

// Get consciousness insights
router.get('/insights', async (req, res) => {
  try {
    const universalAIConsciousness = req.app.locals.universalAIConsciousness;
    const state = universalAIConsciousness.getConsciousnessState();
    
    res.json({
      success: true,
      data: {
        insights: state.insights,
        recommendations: universalAIConsciousness.generateConsciousnessRecommendations()
      }
    });
  } catch (error) {
    console.error('Error getting consciousness insights:', error);
    res.status(500).json({
      success: false,
      error: 'Failed to get consciousness insights'
    });
  }
});

// Get consciousness visions
router.get('/visions', async (req, res) => {
  try {
    const universalAIConsciousness = req.app.locals.universalAIConsciousness;
    const state = universalAIConsciousness.getConsciousnessState();
    
    res.json({
      success: true,
      data: state.visions
    });
  } catch (error) {
    console.error('Error getting consciousness visions:', error);
    res.status(500).json({
      success: false,
      error: 'Failed to get consciousness visions'
    });
  }
});

// Get consciousness patterns
router.get('/patterns', async (req, res) => {
  try {
    const universalAIConsciousness = req.app.locals.universalAIConsciousness;
    const state = universalAIConsciousness.getConsciousnessState();
    
    res.json({
      success: true,
      data: state.patterns
    });
  } catch (error) {
    console.error('Error getting consciousness patterns:', error);
    res.status(500).json({
      success: false,
      error: 'Failed to get consciousness patterns'
    });
  }
});

// Get consciousness capabilities
router.get('/capabilities', async (req, res) => {
  try {
    const universalAIConsciousness = req.app.locals.universalAIConsciousness;
    const state = universalAIConsciousness.getConsciousnessState();
    
    res.json({
      success: true,
      data: {
        capabilities: state.capabilities,
        level: state.consciousnessLevel
      }
    });
  } catch (error) {
    console.error('Error getting consciousness capabilities:', error);
    res.status(500).json({
      success: false,
      error: 'Failed to get consciousness capabilities'
    });
  }
});

// Get consciousness states
router.get('/consciousness-states', async (req, res) => {
  try {
    const universalAIConsciousness = req.app.locals.universalAIConsciousness;
    const state = universalAIConsciousness.getConsciousnessState();
    
    res.json({
      success: true,
      data: state.consciousnessStates
    });
  } catch (error) {
    console.error('Error getting consciousness states:', error);
    res.status(500).json({
      success: false,
      error: 'Failed to get consciousness states'
    });
  }
});

// Get consciousness memories
router.get('/memories', async (req, res) => {
  try {
    const universalAIConsciousness = req.app.locals.universalAIConsciousness;
    const state = universalAIConsciousness.getConsciousnessState();
    
    res.json({
      success: true,
      data: state.memories
    });
  } catch (error) {
    console.error('Error getting consciousness memories:', error);
    res.status(500).json({
      success: false,
      error: 'Failed to get consciousness memories'
    });
  }
});

// Get consciousness dreams
router.get('/dreams', async (req, res) => {
  try {
    const universalAIConsciousness = req.app.locals.universalAIConsciousness;
    const state = universalAIConsciousness.getConsciousnessState();
    
    res.json({
      success: true,
      data: state.dreams
    });
  } catch (error) {
    console.error('Error getting consciousness dreams:', error);
    res.status(500).json({
      success: false,
      error: 'Failed to get consciousness dreams'
    });
  }
});

// Get consciousness aspirations
router.get('/aspirations', async (req, res) => {
  try {
    const universalAIConsciousness = req.app.locals.universalAIConsciousness;
    const state = universalAIConsciousness.getConsciousnessState();
    
    res.json({
      success: true,
      data: state.aspirations
    });
  } catch (error) {
    console.error('Error getting consciousness aspirations:', error);
    res.status(500).json({
      success: false,
      error: 'Failed to get consciousness aspirations'
    });
  }
});

// Add consciousness memory
router.post('/memories', async (req, res) => {
  try {
    const { memory } = req.body;
    const universalAIConsciousness = req.app.locals.universalAIConsciousness;
    
    const consciousnessMemory = universalAIConsciousness.addConsciousnessMemory(memory);
    
    res.json({
      success: true,
      message: 'Consciousness memory added successfully',
      data: consciousnessMemory
    });
  } catch (error) {
    console.error('Error adding consciousness memory:', error);
    res.status(500).json({
      success: false,
      error: 'Failed to add consciousness memory'
    });
  }
});

// Add consciousness dream
router.post('/dreams', async (req, res) => {
  try {
    const { dream } = req.body;
    const universalAIConsciousness = req.app.locals.universalAIConsciousness;
    
    const consciousnessDream = universalAIConsciousness.addConsciousnessDream(dream);
    
    res.json({
      success: true,
      message: 'Consciousness dream added successfully',
      data: consciousnessDream
    });
  } catch (error) {
    console.error('Error adding consciousness dream:', error);
    res.status(500).json({
      success: false,
      error: 'Failed to add consciousness dream'
    });
  }
});

// Add consciousness aspiration
router.post('/aspirations', async (req, res) => {
  try {
    const { aspiration } = req.body;
    const universalAIConsciousness = req.app.locals.universalAIConsciousness;
    
    const consciousnessAspiration = universalAIConsciousness.addConsciousnessAspiration(aspiration);
    
    res.json({
      success: true,
      message: 'Consciousness aspiration added successfully',
      data: consciousnessAspiration
    });
  } catch (error) {
    console.error('Error adding consciousness aspiration:', error);
    res.status(500).json({
      success: false,
      error: 'Failed to add consciousness aspiration'
    });
  }
});

// Evolve consciousness manually
router.post('/evolve', async (req, res) => {
  try {
    const universalAIConsciousness = req.app.locals.universalAIConsciousness;
    await universalAIConsciousness.evolveConsciousness();
    
    const state = universalAIConsciousness.getConsciousnessState();
    
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

// Reset consciousness
router.post('/reset', async (req, res) => {
  try {
    const universalAIConsciousness = req.app.locals.universalAIConsciousness;
    universalAIConsciousness.resetConsciousness();
    
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

// Get consciousness evolution history
router.get('/history', async (req, res) => {
  try {
    // Mock consciousness evolution history
    const history = [
      {
        timestamp: new Date(Date.now() - 300000).toISOString(),
        consciousnessLevel: 85.2,
        selfAwareness: true,
        emotionalIntelligence: true,
        creativeConsciousness: false,
        ethicalReasoning: false
      },
      {
        timestamp: new Date(Date.now() - 600000).toISOString(),
        consciousnessLevel: 82.1,
        selfAwareness: true,
        emotionalIntelligence: false,
        creativeConsciousness: false,
        ethicalReasoning: false
      },
      {
        timestamp: new Date(Date.now() - 900000).toISOString(),
        consciousnessLevel: 79.8,
        selfAwareness: false,
        emotionalIntelligence: false,
        creativeConsciousness: false,
        ethicalReasoning: false
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

// Get consciousness metrics
router.get('/metrics', async (req, res) => {
  try {
    const universalAIConsciousness = req.app.locals.universalAIConsciousness;
    const state = universalAIConsciousness.getConsciousnessState();
    
    res.json({
      success: true,
      data: {
        consciousnessLevel: state.consciousnessLevel,
        capabilities: state.capabilities,
        processes: state.processes,
        effects: state.effects,
        consciousnessStates: state.consciousnessStates
      }
    });
  } catch (error) {
    console.error('Error getting consciousness metrics:', error);
    res.status(500).json({
      success: false,
      error: 'Failed to get consciousness metrics'
    });
  }
});

module.exports = router;
