const express = require('express');
const router = express.Router();

/**
 * Universal Reality Infinite Routes
 * API endpoints for universal reality infinite functionality
 */

// Get universal reality infinite state
router.get('/state', (req, res) => {
  try {
    const universalRealityInfinite = req.app.locals.universalRealityInfinite;
    const state = universalRealityInfinite.getUniversalRealityInfiniteState();
    res.json({
      success: true,
      data: state,
      message: 'Universal reality infinite state retrieved successfully'
    });
  } catch (error) {
    res.status(500).json({
      success: false,
      error: error.message,
      message: 'Failed to retrieve universal reality infinite state'
    });
  }
});

// Get universal reality level description
router.get('/level/:level', (req, res) => {
  try {
    const universalRealityInfinite = req.app.locals.universalRealityInfinite;
    const level = parseFloat(req.params.level);
    const description = universalRealityInfinite.getUniversalRealityLevelDescription(level);
    res.json({
      success: true,
      data: { level, description },
      message: 'Universal reality level description retrieved successfully'
    });
  } catch (error) {
    res.status(500).json({
      success: false,
      error: error.message,
      message: 'Failed to retrieve universal reality level description'
    });
  }
});

// Start universal reality process
router.post('/process/start', (req, res) => {
  try {
    const universalRealityInfinite = req.app.locals.universalRealityInfinite;
    const { processName } = req.body;
    
    if (!processName) {
      return res.status(400).json({
        success: false,
        error: 'Process name is required',
        message: 'Please provide a process name'
      });
    }

    universalRealityInfinite.startUniversalRealityProcess(processName);
    res.json({
      success: true,
      data: { processName },
      message: `Universal reality process ${processName} started successfully`
    });
  } catch (error) {
    res.status(500).json({
      success: false,
      error: error.message,
      message: 'Failed to start universal reality process'
    });
  }
});

// Stop universal reality process
router.post('/process/stop', (req, res) => {
  try {
    const universalRealityInfinite = req.app.locals.universalRealityInfinite;
    const { processName } = req.body;
    
    if (!processName) {
      return res.status(400).json({
        success: false,
        error: 'Process name is required',
        message: 'Please provide a process name'
      });
    }

    universalRealityInfinite.stopUniversalRealityProcess(processName);
    res.json({
      success: true,
      data: { processName },
      message: `Universal reality process ${processName} stopped successfully`
    });
  } catch (error) {
    res.status(500).json({
      success: false,
      error: error.message,
      message: 'Failed to stop universal reality process'
    });
  }
});

// Create universal reality
router.post('/reality/create', (req, res) => {
  try {
    const universalRealityInfinite = req.app.locals.universalRealityInfinite;
    const realityData = req.body;
    
    if (!realityData.name) {
      return res.status(400).json({
        success: false,
        error: 'Reality name is required',
        message: 'Please provide a reality name'
      });
    }

    const reality = universalRealityInfinite.createUniversalReality(realityData);
    res.json({
      success: true,
      data: reality,
      message: 'Universal reality created successfully'
    });
  } catch (error) {
    res.status(500).json({
      success: false,
      error: error.message,
      message: 'Failed to create universal reality'
    });
  }
});

// Create infinite reality
router.post('/infinite/create', (req, res) => {
  try {
    const universalRealityInfinite = req.app.locals.universalRealityInfinite;
    const realityData = req.body;
    
    if (!realityData.name) {
      return res.status(400).json({
        success: false,
        error: 'Reality name is required',
        message: 'Please provide a reality name'
      });
    }

    const reality = universalRealityInfinite.createInfiniteReality(realityData);
    res.json({
      success: true,
      data: reality,
      message: 'Infinite reality created successfully'
    });
  } catch (error) {
    res.status(500).json({
      success: false,
      error: error.message,
      message: 'Failed to create infinite reality'
    });
  }
});

// Create cosmic reality
router.post('/cosmic/create', (req, res) => {
  try {
    const universalRealityInfinite = req.app.locals.universalRealityInfinite;
    const realityData = req.body;
    
    if (!realityData.name) {
      return res.status(400).json({
        success: false,
        error: 'Reality name is required',
        message: 'Please provide a reality name'
      });
    }

    const reality = universalRealityInfinite.createCosmicReality(realityData);
    res.json({
      success: true,
      data: reality,
      message: 'Cosmic reality created successfully'
    });
  } catch (error) {
    res.status(500).json({
      success: false,
      error: error.message,
      message: 'Failed to create cosmic reality'
    });
  }
});

// Create divine reality
router.post('/divine/create', (req, res) => {
  try {
    const universalRealityInfinite = req.app.locals.universalRealityInfinite;
    const realityData = req.body;
    
    if (!realityData.name) {
      return res.status(400).json({
        success: false,
        error: 'Reality name is required',
        message: 'Please provide a reality name'
      });
    }

    const reality = universalRealityInfinite.createDivineReality(realityData);
    res.json({
      success: true,
      data: reality,
      message: 'Divine reality created successfully'
    });
  } catch (error) {
    res.status(500).json({
      success: false,
      error: error.message,
      message: 'Failed to create divine reality'
    });
  }
});

// Reset universal reality infinite
router.post('/reset', (req, res) => {
  try {
    const universalRealityInfinite = req.app.locals.universalRealityInfinite;
    universalRealityInfinite.resetUniversalRealityInfinite();
    res.json({
      success: true,
      message: 'Universal reality infinite reset successfully'
    });
  } catch (error) {
    res.status(500).json({
      success: false,
      error: error.message,
      message: 'Failed to reset universal reality infinite'
    });
  }
});

module.exports = router;
