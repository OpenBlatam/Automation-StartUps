const express = require('express');
const router = express.Router();

/**
 * Omniscient Intelligence API Routes
 * Handles all omniscient intelligence operations
 */

// Get omniscience state
router.get('/state', async (req, res) => {
  try {
    const omniscientIntelligence = req.app.locals.omniscientIntelligence;
    const state = omniscientIntelligence.getOmniscienceState();
    
    res.json({
      success: true,
      data: state
    });
  } catch (error) {
    console.error('Error getting omniscience state:', error);
    res.status(500).json({
      success: false,
      error: 'Failed to get omniscience state'
    });
  }
});

// Get omniscience level description
router.get('/level/:level', async (req, res) => {
  try {
    const { level } = req.params;
    const omniscientIntelligence = req.app.locals.omniscientIntelligence;
    
    const description = omniscientIntelligence.getOmniscienceLevelDescription(parseFloat(level));
    
    res.json({
      success: true,
      data: {
        level: parseFloat(level),
        description
      }
    });
  } catch (error) {
    console.error('Error getting omniscience level:', error);
    res.status(500).json({
      success: false,
      error: 'Failed to get omniscience level'
    });
  }
});

// Start omniscience process
router.post('/processes/:processName/start', async (req, res) => {
  try {
    const { processName } = req.params;
    const omniscientIntelligence = req.app.locals.omniscientIntelligence;
    
    omniscientIntelligence.startOmniscienceProcess(processName);
    
    res.json({
      success: true,
      message: `Omniscience process ${processName} started successfully`
    });
  } catch (error) {
    console.error('Error starting omniscience process:', error);
    res.status(500).json({
      success: false,
      error: 'Failed to start omniscience process'
    });
  }
});

// Stop omniscience process
router.post('/processes/:processName/stop', async (req, res) => {
  try {
    const { processName } = req.params;
    const omniscientIntelligence = req.app.locals.omniscientIntelligence;
    
    omniscientIntelligence.stopOmniscienceProcess(processName);
    
    res.json({
      success: true,
      message: `Omniscience process ${processName} stopped successfully`
    });
  } catch (error) {
    console.error('Error stopping omniscience process:', error);
    res.status(500).json({
      success: false,
      error: 'Failed to stop omniscience process'
    });
  }
});

// Get omniscience insights
router.get('/insights', async (req, res) => {
  try {
    const omniscientIntelligence = req.app.locals.omniscientIntelligence;
    const state = omniscientIntelligence.getOmniscienceState();
    
    res.json({
      success: true,
      data: {
        insights: state.insights,
        recommendations: omniscientIntelligence.generateOmniscienceRecommendations()
      }
    });
  } catch (error) {
    console.error('Error getting omniscience insights:', error);
    res.status(500).json({
      success: false,
      error: 'Failed to get omniscience insights'
    });
  }
});

// Get omniscience visions
router.get('/visions', async (req, res) => {
  try {
    const omniscientIntelligence = req.app.locals.omniscientIntelligence;
    const state = omniscientIntelligence.getOmniscienceState();
    
    res.json({
      success: true,
      data: state.visions
    });
  } catch (error) {
    console.error('Error getting omniscience visions:', error);
    res.status(500).json({
      success: false,
      error: 'Failed to get omniscience visions'
    });
  }
});

// Get omniscience patterns
router.get('/patterns', async (req, res) => {
  try {
    const omniscientIntelligence = req.app.locals.omniscientIntelligence;
    const state = omniscientIntelligence.getOmniscienceState();
    
    res.json({
      success: true,
      data: state.patterns
    });
  } catch (error) {
    console.error('Error getting omniscience patterns:', error);
    res.status(500).json({
      success: false,
      error: 'Failed to get omniscience patterns'
    });
  }
});

// Get omniscience capabilities
router.get('/capabilities', async (req, res) => {
  try {
    const omniscientIntelligence = req.app.locals.omniscientIntelligence;
    const state = omniscientIntelligence.getOmniscienceState();
    
    res.json({
      success: true,
      data: {
        capabilities: state.capabilities,
        level: state.omniscienceLevel
      }
    });
  } catch (error) {
    console.error('Error getting omniscience capabilities:', error);
    res.status(500).json({
      success: false,
      error: 'Failed to get omniscience capabilities'
    });
  }
});

// Get knowledge base
router.get('/knowledge-base', async (req, res) => {
  try {
    const omniscientIntelligence = req.app.locals.omniscientIntelligence;
    const state = omniscientIntelligence.getOmniscienceState();
    
    res.json({
      success: true,
      data: state.knowledgeBase
    });
  } catch (error) {
    console.error('Error getting knowledge base:', error);
    res.status(500).json({
      success: false,
      error: 'Failed to get knowledge base'
    });
  }
});

// Get wisdom levels
router.get('/wisdom-levels', async (req, res) => {
  try {
    const omniscientIntelligence = req.app.locals.omniscientIntelligence;
    const state = omniscientIntelligence.getOmniscienceState();
    
    res.json({
      success: true,
      data: state.wisdomLevels
    });
  } catch (error) {
    console.error('Error getting wisdom levels:', error);
    res.status(500).json({
      success: false,
      error: 'Failed to get wisdom levels'
    });
  }
});

// Add knowledge to base
router.post('/knowledge-base', async (req, res) => {
  try {
    const { category, knowledge } = req.body;
    const omniscientIntelligence = req.app.locals.omniscientIntelligence;
    
    omniscientIntelligence.addKnowledge(category, knowledge);
    
    res.json({
      success: true,
      message: 'Knowledge added to base successfully'
    });
  } catch (error) {
    console.error('Error adding knowledge:', error);
    res.status(500).json({
      success: false,
      error: 'Failed to add knowledge'
    });
  }
});

// Search knowledge base
router.get('/knowledge-base/search', async (req, res) => {
  try {
    const { query, category } = req.query;
    const omniscientIntelligence = req.app.locals.omniscientIntelligence;
    
    const results = omniscientIntelligence.searchKnowledge(query, category);
    
    res.json({
      success: true,
      data: results
    });
  } catch (error) {
    console.error('Error searching knowledge base:', error);
    res.status(500).json({
      success: false,
      error: 'Failed to search knowledge base'
    });
  }
});

// Evolve omniscience manually
router.post('/evolve', async (req, res) => {
  try {
    const omniscientIntelligence = req.app.locals.omniscientIntelligence;
    await omniscientIntelligence.evolveOmniscience();
    
    const state = omniscientIntelligence.getOmniscienceState();
    
    res.json({
      success: true,
      message: 'Omniscience evolved successfully',
      data: state
    });
  } catch (error) {
    console.error('Error evolving omniscience:', error);
    res.status(500).json({
      success: false,
      error: 'Failed to evolve omniscience'
    });
  }
});

// Reset omniscience
router.post('/reset', async (req, res) => {
  try {
    const omniscientIntelligence = req.app.locals.omniscientIntelligence;
    omniscientIntelligence.resetOmniscience();
    
    res.json({
      success: true,
      message: 'Omniscience reset successfully'
    });
  } catch (error) {
    console.error('Error resetting omniscience:', error);
    res.status(500).json({
      success: false,
      error: 'Failed to reset omniscience'
    });
  }
});

// Get omniscience evolution history
router.get('/history', async (req, res) => {
  try {
    // Mock omniscience evolution history
    const history = [
      {
        timestamp: new Date(Date.now() - 300000).toISOString(),
        omniscienceLevel: 85.2,
        absoluteKnowledge: true,
        infiniteWisdom: true,
        perfectUnderstanding: false,
        omniscientInsights: false
      },
      {
        timestamp: new Date(Date.now() - 600000).toISOString(),
        omniscienceLevel: 82.1,
        absoluteKnowledge: true,
        infiniteWisdom: false,
        perfectUnderstanding: false,
        omniscientInsights: false
      },
      {
        timestamp: new Date(Date.now() - 900000).toISOString(),
        omniscienceLevel: 79.8,
        absoluteKnowledge: false,
        infiniteWisdom: false,
        perfectUnderstanding: false,
        omniscientInsights: false
      }
    ];
    
    res.json({
      success: true,
      data: history
    });
  } catch (error) {
    console.error('Error getting omniscience history:', error);
    res.status(500).json({
      success: false,
      error: 'Failed to get omniscience history'
    });
  }
});

// Get omniscience metrics
router.get('/metrics', async (req, res) => {
  try {
    const omniscientIntelligence = req.app.locals.omniscientIntelligence;
    const state = omniscientIntelligence.getOmniscienceState();
    
    res.json({
      success: true,
      data: {
        omniscienceLevel: state.omniscienceLevel,
        capabilities: state.capabilities,
        processes: state.processes,
        effects: state.effects,
        wisdomLevels: state.wisdomLevels
      }
    });
  } catch (error) {
    console.error('Error getting omniscience metrics:', error);
    res.status(500).json({
      success: false,
      error: 'Failed to get omniscience metrics'
    });
  }
});

module.exports = router;