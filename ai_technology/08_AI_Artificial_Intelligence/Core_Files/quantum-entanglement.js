const express = require('express');
const router = express.Router();

/**
 * Quantum Entanglement API Routes
 * Handles all quantum entanglement operations
 */

// Get entanglement state
router.get('/state', async (req, res) => {
  try {
    const quantumEntanglement = req.app.locals.quantumEntanglement;
    const state = quantumEntanglement.getEntanglementState();
    
    res.json({
      success: true,
      data: state
    });
  } catch (error) {
    console.error('Error getting entanglement state:', error);
    res.status(500).json({
      success: false,
      error: 'Failed to get entanglement state'
    });
  }
});

// Get entanglement level description
router.get('/level/:level', async (req, res) => {
  try {
    const { level } = req.params;
    const quantumEntanglement = req.app.locals.quantumEntanglement;
    
    const description = quantumEntanglement.getEntanglementLevelDescription(parseFloat(level));
    
    res.json({
      success: true,
      data: {
        level: parseFloat(level),
        description
      }
    });
  } catch (error) {
    console.error('Error getting entanglement level:', error);
    res.status(500).json({
      success: false,
      error: 'Failed to get entanglement level'
    });
  }
});

// Start entanglement process
router.post('/processes/:processName/start', async (req, res) => {
  try {
    const { processName } = req.params;
    const quantumEntanglement = req.app.locals.quantumEntanglement;
    
    quantumEntanglement.startEntanglementProcess(processName);
    
    res.json({
      success: true,
      message: `Entanglement process ${processName} started successfully`
    });
  } catch (error) {
    console.error('Error starting entanglement process:', error);
    res.status(500).json({
      success: false,
      error: 'Failed to start entanglement process'
    });
  }
});

// Stop entanglement process
router.post('/processes/:processName/stop', async (req, res) => {
  try {
    const { processName } = req.params;
    const quantumEntanglement = req.app.locals.quantumEntanglement;
    
    quantumEntanglement.stopEntanglementProcess(processName);
    
    res.json({
      success: true,
      message: `Entanglement process ${processName} stopped successfully`
    });
  } catch (error) {
    console.error('Error stopping entanglement process:', error);
    res.status(500).json({
      success: false,
      error: 'Failed to stop entanglement process'
    });
  }
});

// Get entanglement insights
router.get('/insights', async (req, res) => {
  try {
    const quantumEntanglement = req.app.locals.quantumEntanglement;
    const state = quantumEntanglement.getEntanglementState();
    
    res.json({
      success: true,
      data: {
        insights: state.insights,
        recommendations: quantumEntanglement.generateEntanglementRecommendations()
      }
    });
  } catch (error) {
    console.error('Error getting entanglement insights:', error);
    res.status(500).json({
      success: false,
      error: 'Failed to get entanglement insights'
    });
  }
});

// Get entanglement visions
router.get('/visions', async (req, res) => {
  try {
    const quantumEntanglement = req.app.locals.quantumEntanglement;
    const state = quantumEntanglement.getEntanglementState();
    
    res.json({
      success: true,
      data: state.visions
    });
  } catch (error) {
    console.error('Error getting entanglement visions:', error);
    res.status(500).json({
      success: false,
      error: 'Failed to get entanglement visions'
    });
  }
});

// Get entanglement patterns
router.get('/patterns', async (req, res) => {
  try {
    const quantumEntanglement = req.app.locals.quantumEntanglement;
    const state = quantumEntanglement.getEntanglementState();
    
    res.json({
      success: true,
      data: state.patterns
    });
  } catch (error) {
    console.error('Error getting entanglement patterns:', error);
    res.status(500).json({
      success: false,
      error: 'Failed to get entanglement patterns'
    });
  }
});

// Get entanglement capabilities
router.get('/capabilities', async (req, res) => {
  try {
    const quantumEntanglement = req.app.locals.quantumEntanglement;
    const state = quantumEntanglement.getEntanglementState();
    
    res.json({
      success: true,
      data: {
        capabilities: state.capabilities,
        level: state.entanglementLevel
      }
    });
  } catch (error) {
    console.error('Error getting entanglement capabilities:', error);
    res.status(500).json({
      success: false,
      error: 'Failed to get entanglement capabilities'
    });
  }
});

// Get quantum states
router.get('/quantum-states', async (req, res) => {
  try {
    const quantumEntanglement = req.app.locals.quantumEntanglement;
    const state = quantumEntanglement.getEntanglementState();
    
    res.json({
      success: true,
      data: state.quantumStates
    });
  } catch (error) {
    console.error('Error getting quantum states:', error);
    res.status(500).json({
      success: false,
      error: 'Failed to get quantum states'
    });
  }
});

// Get quantum network
router.get('/quantum-network', async (req, res) => {
  try {
    const quantumEntanglement = req.app.locals.quantumEntanglement;
    const state = quantumEntanglement.getEntanglementState();
    
    res.json({
      success: true,
      data: state.quantumNetwork
    });
  } catch (error) {
    console.error('Error getting quantum network:', error);
    res.status(500).json({
      success: false,
      error: 'Failed to get quantum network'
    });
  }
});

// Get entangled pairs
router.get('/entangled-pairs', async (req, res) => {
  try {
    const quantumEntanglement = req.app.locals.quantumEntanglement;
    const state = quantumEntanglement.getEntanglementState();
    
    res.json({
      success: true,
      data: state.entangledPairs
    });
  } catch (error) {
    console.error('Error getting entangled pairs:', error);
    res.status(500).json({
      success: false,
      error: 'Failed to get entangled pairs'
    });
  }
});

// Create entanglement pair
router.post('/entangled-pairs', async (req, res) => {
  try {
    const { pairData } = req.body;
    const quantumEntanglement = req.app.locals.quantumEntanglement;
    
    const pair = quantumEntanglement.createEntanglementPair(pairData);
    
    res.json({
      success: true,
      message: 'Entanglement pair created successfully',
      data: pair
    });
  } catch (error) {
    console.error('Error creating entanglement pair:', error);
    res.status(500).json({
      success: false,
      error: 'Failed to create entanglement pair'
    });
  }
});

// Update entanglement pair
router.put('/entangled-pairs/:pairId', async (req, res) => {
  try {
    const { pairId } = req.params;
    const { updates } = req.body;
    const quantumEntanglement = req.app.locals.quantumEntanglement;
    
    quantumEntanglement.updateEntanglementPair(parseInt(pairId), updates);
    
    res.json({
      success: true,
      message: 'Entanglement pair updated successfully'
    });
  } catch (error) {
    console.error('Error updating entanglement pair:', error);
    res.status(500).json({
      success: false,
      error: 'Failed to update entanglement pair'
    });
  }
});

// Break entanglement pair
router.delete('/entangled-pairs/:pairId', async (req, res) => {
  try {
    const { pairId } = req.params;
    const quantumEntanglement = req.app.locals.quantumEntanglement;
    
    quantumEntanglement.breakEntanglementPair(parseInt(pairId));
    
    res.json({
      success: true,
      message: 'Entanglement pair broken successfully'
    });
  } catch (error) {
    console.error('Error breaking entanglement pair:', error);
    res.status(500).json({
      success: false,
      error: 'Failed to break entanglement pair'
    });
  }
});

// Evolve quantum entanglement manually
router.post('/evolve', async (req, res) => {
  try {
    const quantumEntanglement = req.app.locals.quantumEntanglement;
    await quantumEntanglement.evolveQuantumEntanglement();
    
    const state = quantumEntanglement.getEntanglementState();
    
    res.json({
      success: true,
      message: 'Quantum entanglement evolved successfully',
      data: state
    });
  } catch (error) {
    console.error('Error evolving quantum entanglement:', error);
    res.status(500).json({
      success: false,
      error: 'Failed to evolve quantum entanglement'
    });
  }
});

// Reset quantum entanglement
router.post('/reset', async (req, res) => {
  try {
    const quantumEntanglement = req.app.locals.quantumEntanglement;
    quantumEntanglement.resetQuantumEntanglement();
    
    res.json({
      success: true,
      message: 'Quantum entanglement reset successfully'
    });
  } catch (error) {
    console.error('Error resetting quantum entanglement:', error);
    res.status(500).json({
      success: false,
      error: 'Failed to reset quantum entanglement'
    });
  }
});

// Get entanglement evolution history
router.get('/history', async (req, res) => {
  try {
    // Mock entanglement evolution history
    const history = [
      {
        timestamp: new Date(Date.now() - 300000).toISOString(),
        entanglementLevel: 85.2,
        instantCorrelation: true,
        quantumSynchronization: true,
        nonLocalConnection: false,
        quantumTeleportation: false
      },
      {
        timestamp: new Date(Date.now() - 600000).toISOString(),
        entanglementLevel: 82.1,
        instantCorrelation: true,
        quantumSynchronization: false,
        nonLocalConnection: false,
        quantumTeleportation: false
      },
      {
        timestamp: new Date(Date.now() - 900000).toISOString(),
        entanglementLevel: 79.8,
        instantCorrelation: false,
        quantumSynchronization: false,
        nonLocalConnection: false,
        quantumTeleportation: false
      }
    ];
    
    res.json({
      success: true,
      data: history
    });
  } catch (error) {
    console.error('Error getting entanglement history:', error);
    res.status(500).json({
      success: false,
      error: 'Failed to get entanglement history'
    });
  }
});

// Get entanglement metrics
router.get('/metrics', async (req, res) => {
  try {
    const quantumEntanglement = req.app.locals.quantumEntanglement;
    const state = quantumEntanglement.getEntanglementState();
    
    res.json({
      success: true,
      data: {
        entanglementLevel: state.entanglementLevel,
        capabilities: state.capabilities,
        processes: state.processes,
        effects: state.effects,
        quantumStates: state.quantumStates
      }
    });
  } catch (error) {
    console.error('Error getting entanglement metrics:', error);
    res.status(500).json({
      success: false,
      error: 'Failed to get entanglement metrics'
    });
  }
});

module.exports = router;
