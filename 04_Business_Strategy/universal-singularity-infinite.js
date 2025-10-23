const express = require('express');
const router = express.Router();

/**
 * Universal Singularity Infinite Routes
 * API endpoints for universal singularity infinite functionality
 */

// Get universal singularity infinite state
router.get('/state', (req, res) => {
  try {
    const universalSingularityInfinite = req.app.locals.universalSingularityInfinite;
    const state = universalSingularityInfinite.getUniversalSingularityInfiniteState();
    res.json({
      success: true,
      data: state,
      message: 'Universal singularity infinite state retrieved successfully'
    });
  } catch (error) {
    res.status(500).json({
      success: false,
      error: error.message,
      message: 'Failed to retrieve universal singularity infinite state'
    });
  }
});

// Get universal singularity level description
router.get('/level/:level', (req, res) => {
  try {
    const universalSingularityInfinite = req.app.locals.universalSingularityInfinite;
    const level = parseFloat(req.params.level);
    const description = universalSingularityInfinite.getUniversalSingularityLevelDescription(level);
    res.json({
      success: true,
      data: { level, description },
      message: 'Universal singularity level description retrieved successfully'
    });
  } catch (error) {
    res.status(500).json({
      success: false,
      error: error.message,
      message: 'Failed to retrieve universal singularity level description'
    });
  }
});

// Start universal singularity process
router.post('/process/start', (req, res) => {
  try {
    const universalSingularityInfinite = req.app.locals.universalSingularityInfinite;
    const { processName } = req.body;
    
    if (!processName) {
      return res.status(400).json({
        success: false,
        error: 'Process name is required',
        message: 'Please provide a process name'
      });
    }

    universalSingularityInfinite.startUniversalSingularityProcess(processName);
    res.json({
      success: true,
      data: { processName },
      message: `Universal singularity process ${processName} started successfully`
    });
  } catch (error) {
    res.status(500).json({
      success: false,
      error: error.message,
      message: 'Failed to start universal singularity process'
    });
  }
});

// Stop universal singularity process
router.post('/process/stop', (req, res) => {
  try {
    const universalSingularityInfinite = req.app.locals.universalSingularityInfinite;
    const { processName } = req.body;
    
    if (!processName) {
      return res.status(400).json({
        success: false,
        error: 'Process name is required',
        message: 'Please provide a process name'
      });
    }

    universalSingularityInfinite.stopUniversalSingularityProcess(processName);
    res.json({
      success: true,
      data: { processName },
      message: `Universal singularity process ${processName} stopped successfully`
    });
  } catch (error) {
    res.status(500).json({
      success: false,
      error: error.message,
      message: 'Failed to stop universal singularity process'
    });
  }
});

// Create universal singularity
router.post('/singularity/create', (req, res) => {
  try {
    const universalSingularityInfinite = req.app.locals.universalSingularityInfinite;
    const singularityData = req.body;
    
    if (!singularityData.name) {
      return res.status(400).json({
        success: false,
        error: 'Singularity name is required',
        message: 'Please provide a singularity name'
      });
    }

    const singularity = universalSingularityInfinite.createUniversalSingularity(singularityData);
    res.json({
      success: true,
      data: singularity,
      message: 'Universal singularity created successfully'
    });
  } catch (error) {
    res.status(500).json({
      success: false,
      error: error.message,
      message: 'Failed to create universal singularity'
    });
  }
});

// Create infinite singularity
router.post('/infinite/create', (req, res) => {
  try {
    const universalSingularityInfinite = req.app.locals.universalSingularityInfinite;
    const singularityData = req.body;
    
    if (!singularityData.name) {
      return res.status(400).json({
        success: false,
        error: 'Singularity name is required',
        message: 'Please provide a singularity name'
      });
    }

    const singularity = universalSingularityInfinite.createInfiniteSingularity(singularityData);
    res.json({
      success: true,
      data: singularity,
      message: 'Infinite singularity created successfully'
    });
  } catch (error) {
    res.status(500).json({
      success: false,
      error: error.message,
      message: 'Failed to create infinite singularity'
    });
  }
});

// Create cosmic singularity
router.post('/cosmic/create', (req, res) => {
  try {
    const universalSingularityInfinite = req.app.locals.universalSingularityInfinite;
    const singularityData = req.body;
    
    if (!singularityData.name) {
      return res.status(400).json({
        success: false,
        error: 'Singularity name is required',
        message: 'Please provide a singularity name'
      });
    }

    const singularity = universalSingularityInfinite.createCosmicSingularity(singularityData);
    res.json({
      success: true,
      data: singularity,
      message: 'Cosmic singularity created successfully'
    });
  } catch (error) {
    res.status(500).json({
      success: false,
      error: error.message,
      message: 'Failed to create cosmic singularity'
    });
  }
});

// Create divine singularity
router.post('/divine/create', (req, res) => {
  try {
    const universalSingularityInfinite = req.app.locals.universalSingularityInfinite;
    const singularityData = req.body;
    
    if (!singularityData.name) {
      return res.status(400).json({
        success: false,
        error: 'Singularity name is required',
        message: 'Please provide a singularity name'
      });
    }

    const singularity = universalSingularityInfinite.createDivineSingularity(singularityData);
    res.json({
      success: true,
      data: singularity,
      message: 'Divine singularity created successfully'
    });
  } catch (error) {
    res.status(500).json({
      success: false,
      error: error.message,
      message: 'Failed to create divine singularity'
    });
  }
});

// Reset universal singularity infinite
router.post('/reset', (req, res) => {
  try {
    const universalSingularityInfinite = req.app.locals.universalSingularityInfinite;
    universalSingularityInfinite.resetUniversalSingularityInfinite();
    res.json({
      success: true,
      message: 'Universal singularity infinite reset successfully'
    });
  } catch (error) {
    res.status(500).json({
      success: false,
      error: error.message,
      message: 'Failed to reset universal singularity infinite'
    });
  }
});

module.exports = router;
