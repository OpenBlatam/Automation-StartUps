const express = require('express');
const router = express.Router();

/**
 * Holographic Reality API Routes
 * Handles all holographic reality operations
 */

// Get holographic state
router.get('/state', async (req, res) => {
  try {
    const holographicReality = req.app.locals.holographicReality;
    const state = holographicReality.getHolographicState();
    
    res.json({
      success: true,
      data: state
    });
  } catch (error) {
    console.error('Error getting holographic state:', error);
    res.status(500).json({
      success: false,
      error: 'Failed to get holographic state'
    });
  }
});

// Get holographic level description
router.get('/level/:level', async (req, res) => {
  try {
    const { level } = req.params;
    const holographicReality = req.app.locals.holographicReality;
    
    const description = holographicReality.getHolographicLevelDescription(parseFloat(level));
    
    res.json({
      success: true,
      data: {
        level: parseFloat(level),
        description
      }
    });
  } catch (error) {
    console.error('Error getting holographic level:', error);
    res.status(500).json({
      success: false,
      error: 'Failed to get holographic level'
    });
  }
});

// Start holographic process
router.post('/processes/:processName/start', async (req, res) => {
  try {
    const { processName } = req.params;
    const holographicReality = req.app.locals.holographicReality;
    
    holographicReality.startHolographicProcess(processName);
    
    res.json({
      success: true,
      message: `Holographic process ${processName} started successfully`
    });
  } catch (error) {
    console.error('Error starting holographic process:', error);
    res.status(500).json({
      success: false,
      error: 'Failed to start holographic process'
    });
  }
});

// Stop holographic process
router.post('/processes/:processName/stop', async (req, res) => {
  try {
    const { processName } = req.params;
    const holographicReality = req.app.locals.holographicReality;
    
    holographicReality.stopHolographicProcess(processName);
    
    res.json({
      success: true,
      message: `Holographic process ${processName} stopped successfully`
    });
  } catch (error) {
    console.error('Error stopping holographic process:', error);
    res.status(500).json({
      success: false,
      error: 'Failed to stop holographic process'
    });
  }
});

// Get holographic insights
router.get('/insights', async (req, res) => {
  try {
    const holographicReality = req.app.locals.holographicReality;
    const state = holographicReality.getHolographicState();
    
    res.json({
      success: true,
      data: {
        insights: state.insights,
        recommendations: holographicReality.generateHolographicRecommendations()
      }
    });
  } catch (error) {
    console.error('Error getting holographic insights:', error);
    res.status(500).json({
      success: false,
      error: 'Failed to get holographic insights'
    });
  }
});

// Get holographic visions
router.get('/visions', async (req, res) => {
  try {
    const holographicReality = req.app.locals.holographicReality;
    const state = holographicReality.getHolographicState();
    
    res.json({
      success: true,
      data: state.visions
    });
  } catch (error) {
    console.error('Error getting holographic visions:', error);
    res.status(500).json({
      success: false,
      error: 'Failed to get holographic visions'
    });
  }
});

// Get holographic patterns
router.get('/patterns', async (req, res) => {
  try {
    const holographicReality = req.app.locals.holographicReality;
    const state = holographicReality.getHolographicState();
    
    res.json({
      success: true,
      data: state.patterns
    });
  } catch (error) {
    console.error('Error getting holographic patterns:', error);
    res.status(500).json({
      success: false,
      error: 'Failed to get holographic patterns'
    });
  }
});

// Get holographic capabilities
router.get('/capabilities', async (req, res) => {
  try {
    const holographicReality = req.app.locals.holographicReality;
    const state = holographicReality.getHolographicState();
    
    res.json({
      success: true,
      data: {
        capabilities: state.capabilities,
        level: state.holographicLevel
      }
    });
  } catch (error) {
    console.error('Error getting holographic capabilities:', error);
    res.status(500).json({
      success: false,
      error: 'Failed to get holographic capabilities'
    });
  }
});

// Get spatial dimensions
router.get('/spatial-dimensions', async (req, res) => {
  try {
    const holographicReality = req.app.locals.holographicReality;
    const state = holographicReality.getHolographicState();
    
    res.json({
      success: true,
      data: state.spatialDimensions
    });
  } catch (error) {
    console.error('Error getting spatial dimensions:', error);
    res.status(500).json({
      success: false,
      error: 'Failed to get spatial dimensions'
    });
  }
});

// Get holographic projections
router.get('/projections', async (req, res) => {
  try {
    const holographicReality = req.app.locals.holographicReality;
    const state = holographicReality.getHolographicState();
    
    res.json({
      success: true,
      data: state.projections
    });
  } catch (error) {
    console.error('Error getting holographic projections:', error);
    res.status(500).json({
      success: false,
      error: 'Failed to get holographic projections'
    });
  }
});

// Create holographic projection
router.post('/projections', async (req, res) => {
  try {
    const { projectionData } = req.body;
    const holographicReality = req.app.locals.holographicReality;
    
    const projection = holographicReality.createHolographicProjection(projectionData);
    
    res.json({
      success: true,
      message: 'Holographic projection created successfully',
      data: projection
    });
  } catch (error) {
    console.error('Error creating holographic projection:', error);
    res.status(500).json({
      success: false,
      error: 'Failed to create holographic projection'
    });
  }
});

// Update holographic projection
router.put('/projections/:projectionId', async (req, res) => {
  try {
    const { projectionId } = req.params;
    const { updates } = req.body;
    const holographicReality = req.app.locals.holographicReality;
    
    holographicReality.updateHolographicProjection(parseInt(projectionId), updates);
    
    res.json({
      success: true,
      message: 'Holographic projection updated successfully'
    });
  } catch (error) {
    console.error('Error updating holographic projection:', error);
    res.status(500).json({
      success: false,
      error: 'Failed to update holographic projection'
    });
  }
});

// Delete holographic projection
router.delete('/projections/:projectionId', async (req, res) => {
  try {
    const { projectionId } = req.params;
    const holographicReality = req.app.locals.holographicReality;
    
    holographicReality.deleteHolographicProjection(parseInt(projectionId));
    
    res.json({
      success: true,
      message: 'Holographic projection deleted successfully'
    });
  } catch (error) {
    console.error('Error deleting holographic projection:', error);
    res.status(500).json({
      success: false,
      error: 'Failed to delete holographic projection'
    });
  }
});

// Evolve holographic reality manually
router.post('/evolve', async (req, res) => {
  try {
    const holographicReality = req.app.locals.holographicReality;
    await holographicReality.evolveHolographicReality();
    
    const state = holographicReality.getHolographicState();
    
    res.json({
      success: true,
      message: 'Holographic reality evolved successfully',
      data: state
    });
  } catch (error) {
    console.error('Error evolving holographic reality:', error);
    res.status(500).json({
      success: false,
      error: 'Failed to evolve holographic reality'
    });
  }
});

// Reset holographic reality
router.post('/reset', async (req, res) => {
  try {
    const holographicReality = req.app.locals.holographicReality;
    holographicReality.resetHolographicReality();
    
    res.json({
      success: true,
      message: 'Holographic reality reset successfully'
    });
  } catch (error) {
    console.error('Error resetting holographic reality:', error);
    res.status(500).json({
      success: false,
      error: 'Failed to reset holographic reality'
    });
  }
});

// Get holographic evolution history
router.get('/history', async (req, res) => {
  try {
    // Mock holographic evolution history
    const history = [
      {
        timestamp: new Date(Date.now() - 300000).toISOString(),
        holographicLevel: 85.2,
        threeDimensionalProjection: true,
        holographicInterfaces: true,
        virtualRealityIntegration: false,
        augmentedRealityOverlay: false
      },
      {
        timestamp: new Date(Date.now() - 600000).toISOString(),
        holographicLevel: 82.1,
        threeDimensionalProjection: true,
        holographicInterfaces: false,
        virtualRealityIntegration: false,
        augmentedRealityOverlay: false
      },
      {
        timestamp: new Date(Date.now() - 900000).toISOString(),
        holographicLevel: 79.8,
        threeDimensionalProjection: false,
        holographicInterfaces: false,
        virtualRealityIntegration: false,
        augmentedRealityOverlay: false
      }
    ];
    
    res.json({
      success: true,
      data: history
    });
  } catch (error) {
    console.error('Error getting holographic history:', error);
    res.status(500).json({
      success: false,
      error: 'Failed to get holographic history'
    });
  }
});

// Get holographic metrics
router.get('/metrics', async (req, res) => {
  try {
    const holographicReality = req.app.locals.holographicReality;
    const state = holographicReality.getHolographicState();
    
    res.json({
      success: true,
      data: {
        holographicLevel: state.holographicLevel,
        capabilities: state.capabilities,
        processes: state.processes,
        effects: state.effects,
        spatialDimensions: state.spatialDimensions
      }
    });
  } catch (error) {
    console.error('Error getting holographic metrics:', error);
    res.status(500).json({
      success: false,
      error: 'Failed to get holographic metrics'
    });
  }
});

module.exports = router;

