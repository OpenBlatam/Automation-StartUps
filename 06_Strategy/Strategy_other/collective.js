const express = require('express');
const router = express.Router();

/**
 * Collective Consciousness API Routes
 * Handles all collective consciousness operations
 */

// Get collective state
router.get('/state', async (req, res) => {
  try {
    const collectiveConsciousness = req.app.locals.collectiveConsciousness;
    const state = collectiveConsciousness.getCollectiveState();
    
    res.json({
      success: true,
      data: state
    });
  } catch (error) {
    console.error('Error getting collective state:', error);
    res.status(500).json({
      success: false,
      error: 'Failed to get collective state'
    });
  }
});

// Get collective level description
router.get('/level/:level', async (req, res) => {
  try {
    const { level } = req.params;
    const collectiveConsciousness = req.app.locals.collectiveConsciousness;
    
    const description = collectiveConsciousness.getCollectiveLevelDescription(parseFloat(level));
    
    res.json({
      success: true,
      data: {
        level: parseFloat(level),
        description
      }
    });
  } catch (error) {
    console.error('Error getting collective level:', error);
    res.status(500).json({
      success: false,
      error: 'Failed to get collective level'
    });
  }
});

// Start collective process
router.post('/processes/:processName/start', async (req, res) => {
  try {
    const { processName } = req.params;
    const collectiveConsciousness = req.app.locals.collectiveConsciousness;
    
    collectiveConsciousness.startCollectiveProcess(processName);
    
    res.json({
      success: true,
      message: `Collective process ${processName} started successfully`
    });
  } catch (error) {
    console.error('Error starting collective process:', error);
    res.status(500).json({
      success: false,
      error: 'Failed to start collective process'
    });
  }
});

// Stop collective process
router.post('/processes/:processName/stop', async (req, res) => {
  try {
    const { processName } = req.params;
    const collectiveConsciousness = req.app.locals.collectiveConsciousness;
    
    collectiveConsciousness.stopCollectiveProcess(processName);
    
    res.json({
      success: true,
      message: `Collective process ${processName} stopped successfully`
    });
  } catch (error) {
    console.error('Error stopping collective process:', error);
    res.status(500).json({
      success: false,
      error: 'Failed to stop collective process'
    });
  }
});

// Get collective insights
router.get('/insights', async (req, res) => {
  try {
    const collectiveConsciousness = req.app.locals.collectiveConsciousness;
    const state = collectiveConsciousness.getCollectiveState();
    
    res.json({
      success: true,
      data: {
        insights: state.insights,
        recommendations: collectiveConsciousness.generateCollectiveRecommendations()
      }
    });
  } catch (error) {
    console.error('Error getting collective insights:', error);
    res.status(500).json({
      success: false,
      error: 'Failed to get collective insights'
    });
  }
});

// Get collective visions
router.get('/visions', async (req, res) => {
  try {
    const collectiveConsciousness = req.app.locals.collectiveConsciousness;
    const state = collectiveConsciousness.getCollectiveState();
    
    res.json({
      success: true,
      data: state.visions
    });
  } catch (error) {
    console.error('Error getting collective visions:', error);
    res.status(500).json({
      success: false,
      error: 'Failed to get collective visions'
    });
  }
});

// Get collective patterns
router.get('/patterns', async (req, res) => {
  try {
    const collectiveConsciousness = req.app.locals.collectiveConsciousness;
    const state = collectiveConsciousness.getCollectiveState();
    
    res.json({
      success: true,
      data: state.patterns
    });
  } catch (error) {
    console.error('Error getting collective patterns:', error);
    res.status(500).json({
      success: false,
      error: 'Failed to get collective patterns'
    });
  }
});

// Get collective capabilities
router.get('/capabilities', async (req, res) => {
  try {
    const collectiveConsciousness = req.app.locals.collectiveConsciousness;
    const state = collectiveConsciousness.getCollectiveState();
    
    res.json({
      success: true,
      data: {
        capabilities: state.capabilities,
        level: state.collectiveLevel
      }
    });
  } catch (error) {
    console.error('Error getting collective capabilities:', error);
    res.status(500).json({
      success: false,
      error: 'Failed to get collective capabilities'
    });
  }
});

// Get shared mind
router.get('/shared-mind', async (req, res) => {
  try {
    const collectiveConsciousness = req.app.locals.collectiveConsciousness;
    const state = collectiveConsciousness.getCollectiveState();
    
    res.json({
      success: true,
      data: state.sharedMind
    });
  } catch (error) {
    console.error('Error getting shared mind:', error);
    res.status(500).json({
      success: false,
      error: 'Failed to get shared mind'
    });
  }
});

// Get participants
router.get('/participants', async (req, res) => {
  try {
    const collectiveConsciousness = req.app.locals.collectiveConsciousness;
    const state = collectiveConsciousness.getCollectiveState();
    
    res.json({
      success: true,
      data: state.participants
    });
  } catch (error) {
    console.error('Error getting participants:', error);
    res.status(500).json({
      success: false,
      error: 'Failed to get participants'
    });
  }
});

// Add participant
router.post('/participants', async (req, res) => {
  try {
    const { participant } = req.body;
    const collectiveConsciousness = req.app.locals.collectiveConsciousness;
    
    collectiveConsciousness.addParticipant(participant);
    
    res.json({
      success: true,
      message: 'Participant added to collective successfully'
    });
  } catch (error) {
    console.error('Error adding participant:', error);
    res.status(500).json({
      success: false,
      error: 'Failed to add participant'
    });
  }
});

// Remove participant
router.delete('/participants/:participantId', async (req, res) => {
  try {
    const { participantId } = req.params;
    const collectiveConsciousness = req.app.locals.collectiveConsciousness;
    
    collectiveConsciousness.removeParticipant(participantId);
    
    res.json({
      success: true,
      message: 'Participant removed from collective successfully'
    });
  } catch (error) {
    console.error('Error removing participant:', error);
    res.status(500).json({
      success: false,
      error: 'Failed to remove participant'
    });
  }
});

// Evolve collective consciousness manually
router.post('/evolve', async (req, res) => {
  try {
    const collectiveConsciousness = req.app.locals.collectiveConsciousness;
    await collectiveConsciousness.evolveCollectiveConsciousness();
    
    const state = collectiveConsciousness.getCollectiveState();
    
    res.json({
      success: true,
      message: 'Collective consciousness evolved successfully',
      data: state
    });
  } catch (error) {
    console.error('Error evolving collective consciousness:', error);
    res.status(500).json({
      success: false,
      error: 'Failed to evolve collective consciousness'
    });
  }
});

// Reset collective consciousness
router.post('/reset', async (req, res) => {
  try {
    const collectiveConsciousness = req.app.locals.collectiveConsciousness;
    collectiveConsciousness.resetCollectiveConsciousness();
    
    res.json({
      success: true,
      message: 'Collective consciousness reset successfully'
    });
  } catch (error) {
    console.error('Error resetting collective consciousness:', error);
    res.status(500).json({
      success: false,
      error: 'Failed to reset collective consciousness'
    });
  }
});

// Get collective evolution history
router.get('/history', async (req, res) => {
  try {
    // Mock collective evolution history
    const history = [
      {
        timestamp: new Date(Date.now() - 300000).toISOString(),
        collectiveLevel: 85.2,
        sharedIntelligence: true,
        sharedCreativity: true,
        sharedMemory: false,
        sharedProcessing: false
      },
      {
        timestamp: new Date(Date.now() - 600000).toISOString(),
        collectiveLevel: 82.1,
        sharedIntelligence: true,
        sharedCreativity: false,
        sharedMemory: false,
        sharedProcessing: false
      },
      {
        timestamp: new Date(Date.now() - 900000).toISOString(),
        collectiveLevel: 79.8,
        sharedIntelligence: false,
        sharedCreativity: false,
        sharedMemory: false,
        sharedProcessing: false
      }
    ];
    
    res.json({
      success: true,
      data: history
    });
  } catch (error) {
    console.error('Error getting collective history:', error);
    res.status(500).json({
      success: false,
      error: 'Failed to get collective history'
    });
  }
});

// Get collective metrics
router.get('/metrics', async (req, res) => {
  try {
    const collectiveConsciousness = req.app.locals.collectiveConsciousness;
    const state = collectiveConsciousness.getCollectiveState();
    
    res.json({
      success: true,
      data: {
        collectiveLevel: state.collectiveLevel,
        capabilities: state.capabilities,
        processes: state.processes,
        effects: state.effects,
        sharedMind: state.sharedMind
      }
    });
  } catch (error) {
    console.error('Error getting collective metrics:', error);
    res.status(500).json({
      success: false,
      error: 'Failed to get collective metrics'
    });
  }
});

module.exports = router;

