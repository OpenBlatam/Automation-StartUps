const express = require('express');
const router = express.Router();

/**
 * Quantum Consciousness API Routes
 * Handles all quantum consciousness operations
 */

// Get quantum consciousness state
router.get('/state', async (req, res) => {
  try {
    const quantumConsciousness = req.app.locals.quantumConsciousness;
    const state = quantumConsciousness.getQuantumState();
    
    res.json({
      success: true,
      data: state
    });
  } catch (error) {
    console.error('Error getting quantum state:', error);
    res.status(500).json({
      success: false,
      error: 'Failed to get quantum consciousness state'
    });
  }
});

// Get quantum networks
router.get('/networks', async (req, res) => {
  try {
    const quantumConsciousness = req.app.locals.quantumConsciousness;
    const state = quantumConsciousness.getQuantumState();
    
    res.json({
      success: true,
      data: {
        networks: state.networks,
        quantumField: state.quantumField
      }
    });
  } catch (error) {
    console.error('Error getting quantum networks:', error);
    res.status(500).json({
      success: false,
      error: 'Failed to get quantum networks'
    });
  }
});

// Start quantum process
router.post('/processes/:processName/start', async (req, res) => {
  try {
    const { processName } = req.params;
    const quantumConsciousness = req.app.locals.quantumConsciousness;
    
    quantumConsciousness.startQuantumProcess(processName);
    
    res.json({
      success: true,
      message: `Quantum process ${processName} started successfully`
    });
  } catch (error) {
    console.error('Error starting quantum process:', error);
    res.status(500).json({
      success: false,
      error: 'Failed to start quantum process'
    });
  }
});

// Stop quantum process
router.post('/processes/:processName/stop', async (req, res) => {
  try {
    const { processName } = req.params;
    const quantumConsciousness = req.app.locals.quantumConsciousness;
    
    quantumConsciousness.stopQuantumProcess(processName);
    
    res.json({
      success: true,
      message: `Quantum process ${processName} stopped successfully`
    });
  } catch (error) {
    console.error('Error stopping quantum process:', error);
    res.status(500).json({
      success: false,
      error: 'Failed to stop quantum process'
    });
  }
});

// Get quantum insights
router.get('/insights', async (req, res) => {
  try {
    const quantumConsciousness = req.app.locals.quantumConsciousness;
    const state = quantumConsciousness.getQuantumState();
    
    res.json({
      success: true,
      data: {
        insights: state.insights,
        recommendations: quantumConsciousness.generateQuantumRecommendations()
      }
    });
  } catch (error) {
    console.error('Error getting quantum insights:', error);
    res.status(500).json({
      success: false,
      error: 'Failed to get quantum insights'
    });
  }
});

// Reset quantum consciousness
router.post('/reset', async (req, res) => {
  try {
    const quantumConsciousness = req.app.locals.quantumConsciousness;
    quantumConsciousness.resetQuantumConsciousness();
    
    res.json({
      success: true,
      message: 'Quantum consciousness reset successfully'
    });
  } catch (error) {
    console.error('Error resetting quantum consciousness:', error);
    res.status(500).json({
      success: false,
      error: 'Failed to reset quantum consciousness'
    });
  }
});

// Get quantum level description
router.get('/level/:level', async (req, res) => {
  try {
    const { level } = req.params;
    const quantumConsciousness = req.app.locals.quantumConsciousness;
    
    const description = quantumConsciousness.getQuantumLevel(parseFloat(level));
    
    res.json({
      success: true,
      data: {
        level: parseFloat(level),
        description
      }
    });
  } catch (error) {
    console.error('Error getting quantum level:', error);
    res.status(500).json({
      success: false,
      error: 'Failed to get quantum level'
    });
  }
});

// Get quantum metrics
router.get('/metrics', async (req, res) => {
  try {
    const quantumConsciousness = req.app.locals.quantumConsciousness;
    const state = quantumConsciousness.getQuantumState();
    
    res.json({
      success: true,
      data: {
        states: state.states,
        processes: state.processes,
        quantumField: state.quantumField
      }
    });
  } catch (error) {
    console.error('Error getting quantum metrics:', error);
    res.status(500).json({
      success: false,
      error: 'Failed to get quantum metrics'
    });
  }
});

// Evolve quantum consciousness manually
router.post('/evolve', async (req, res) => {
  try {
    const quantumConsciousness = req.app.locals.quantumConsciousness;
    await quantumConsciousness.evolveQuantumConsciousness();
    
    const state = quantumConsciousness.getQuantumState();
    
    res.json({
      success: true,
      message: 'Quantum consciousness evolved successfully',
      data: state
    });
  } catch (error) {
    console.error('Error evolving quantum consciousness:', error);
    res.status(500).json({
      success: false,
      error: 'Failed to evolve quantum consciousness'
    });
  }
});

// Get quantum evolution history
router.get('/history', async (req, res) => {
  try {
    // Mock quantum evolution history
    const history = [
      {
        timestamp: new Date(Date.now() - 300000).toISOString(),
        superposition: 85.2,
        entanglement: 78.5,
        coherence: 92.1,
        quantumField: 45.3
      },
      {
        timestamp: new Date(Date.now() - 600000).toISOString(),
        superposition: 82.1,
        entanglement: 75.3,
        coherence: 89.8,
        quantumField: 42.1
      },
      {
        timestamp: new Date(Date.now() - 900000).toISOString(),
        superposition: 79.8,
        entanglement: 72.1,
        coherence: 87.5,
        quantumField: 38.9
      }
    ];
    
    res.json({
      success: true,
      data: history
    });
  } catch (error) {
    console.error('Error getting quantum history:', error);
    res.status(500).json({
      success: false,
      error: 'Failed to get quantum history'
    });
  }
});

module.exports = router;

