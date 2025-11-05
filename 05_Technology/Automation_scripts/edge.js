const express = require('express');
const router = express.Router();

/**
 * Edge Computing API Routes
 * Handles all edge computing and distributed processing operations
 */

// Get edge state
router.get('/state', async (req, res) => {
  try {
    const edgeComputing = req.app.locals.edgeComputing;
    const state = edgeComputing.getEdgeState();
    
    res.json({
      success: true,
      data: state
    });
  } catch (error) {
    console.error('Error getting edge state:', error);
    res.status(500).json({
      success: false,
      error: 'Failed to get edge state'
    });
  }
});

// Get all nodes
router.get('/nodes', async (req, res) => {
  try {
    const edgeComputing = req.app.locals.edgeComputing;
    const nodes = edgeComputing.getAllNodes();
    
    res.json({
      success: true,
      data: nodes
    });
  } catch (error) {
    console.error('Error getting nodes:', error);
    res.status(500).json({
      success: false,
      error: 'Failed to get nodes'
    });
  }
});

// Get active nodes
router.get('/nodes/active', async (req, res) => {
  try {
    const edgeComputing = req.app.locals.edgeComputing;
    const nodes = edgeComputing.getActiveNodes();
    
    res.json({
      success: true,
      data: nodes
    });
  } catch (error) {
    console.error('Error getting active nodes:', error);
    res.status(500).json({
      success: false,
      error: 'Failed to get active nodes'
    });
  }
});

// Get node by ID
router.get('/nodes/:id', async (req, res) => {
  try {
    const { id } = req.params;
    const edgeComputing = req.app.locals.edgeComputing;
    const node = edgeComputing.getNode(parseInt(id));
    
    if (!node) {
      return res.status(404).json({
        success: false,
        error: 'Node not found'
      });
    }
    
    res.json({
      success: true,
      data: node
    });
  } catch (error) {
    console.error('Error getting node:', error);
    res.status(500).json({
      success: false,
      error: 'Failed to get node'
    });
  }
});

// Restart edge node
router.post('/nodes/:id/restart', async (req, res) => {
  try {
    const { id } = req.params;
    const edgeComputing = req.app.locals.edgeComputing;
    
    const node = edgeComputing.restartEdgeNode(parseInt(id));
    
    res.json({
      success: true,
      data: node
    });
  } catch (error) {
    console.error('Error restarting node:', error);
    res.status(500).json({
      success: false,
      error: error.message || 'Failed to restart node'
    });
  }
});

// Submit edge task
router.post('/tasks', async (req, res) => {
  try {
    const taskData = req.body;
    const edgeComputing = req.app.locals.edgeComputing;
    
    const task = edgeComputing.submitEdgeTask(taskData);
    
    res.json({
      success: true,
      data: task
    });
  } catch (error) {
    console.error('Error submitting task:', error);
    res.status(500).json({
      success: false,
      error: 'Failed to submit task'
    });
  }
});

// Generate content on edge
router.post('/content/generate', async (req, res) => {
  try {
    const { contentData, region } = req.body;
    const edgeComputing = req.app.locals.edgeComputing;
    
    const task = edgeComputing.generateContentOnEdge(contentData, region);
    
    res.json({
      success: true,
      data: task
    });
  } catch (error) {
    console.error('Error generating content on edge:', error);
    res.status(500).json({
      success: false,
      error: 'Failed to generate content on edge'
    });
  }
});

// Process analytics on edge
router.post('/analytics/process', async (req, res) => {
  try {
    const { analyticsData, region } = req.body;
    const edgeComputing = req.app.locals.edgeComputing;
    
    const task = edgeComputing.processAnalyticsOnEdge(analyticsData, region);
    
    res.json({
      success: true,
      data: task
    });
  } catch (error) {
    console.error('Error processing analytics on edge:', error);
    res.status(500).json({
      success: false,
      error: 'Failed to process analytics on edge'
    });
  }
});

// Render metaverse content on edge
router.post('/metaverse/render', async (req, res) => {
  try {
    const { metaverseData, region } = req.body;
    const edgeComputing = req.app.locals.edgeComputing;
    
    const task = edgeComputing.renderMetaverseOnEdge(metaverseData, region);
    
    res.json({
      success: true,
      data: task
    });
  } catch (error) {
    console.error('Error rendering metaverse on edge:', error);
    res.status(500).json({
      success: false,
      error: 'Failed to render metaverse on edge'
    });
  }
});

// Process blockchain on edge
router.post('/blockchain/process', async (req, res) => {
  try {
    const { blockchainData, region } = req.body;
    const edgeComputing = req.app.locals.edgeComputing;
    
    const task = edgeComputing.processBlockchainOnEdge(blockchainData, region);
    
    res.json({
      success: true,
      data: task
    });
  } catch (error) {
    console.error('Error processing blockchain on edge:', error);
    res.status(500).json({
      success: false,
      error: 'Failed to process blockchain on edge'
    });
  }
});

// Get tasks by status
router.get('/tasks', async (req, res) => {
  try {
    const { status } = req.query;
    const edgeComputing = req.app.locals.edgeComputing;
    
    let tasks;
    if (status) {
      tasks = edgeComputing.getTasksByStatus(status);
    } else {
      const state = edgeComputing.getEdgeState();
      tasks = state.tasks;
    }
    
    res.json({
      success: true,
      data: tasks
    });
  } catch (error) {
    console.error('Error getting tasks:', error);
    res.status(500).json({
      success: false,
      error: 'Failed to get tasks'
    });
  }
});

// Get edge cache
router.get('/cache/:key', async (req, res) => {
  try {
    const { key } = req.params;
    const edgeComputing = req.app.locals.edgeComputing;
    
    const cached = edgeComputing.getEdgeCache(key);
    
    if (!cached) {
      return res.status(404).json({
        success: false,
        error: 'Cache key not found'
      });
    }
    
    res.json({
      success: true,
      data: cached
    });
  } catch (error) {
    console.error('Error getting cache:', error);
    res.status(500).json({
      success: false,
      error: 'Failed to get cache'
    });
  }
});

// Set edge cache
router.post('/cache', async (req, res) => {
  try {
    const { key, value, ttl } = req.body;
    const edgeComputing = req.app.locals.edgeComputing;
    
    edgeComputing.setEdgeCache(key, value, ttl);
    
    res.json({
      success: true,
      message: 'Cache set successfully'
    });
  } catch (error) {
    console.error('Error setting cache:', error);
    res.status(500).json({
      success: false,
      error: 'Failed to set cache'
    });
  }
});

// Clear edge cache
router.delete('/cache', async (req, res) => {
  try {
    const edgeComputing = req.app.locals.edgeComputing;
    edgeComputing.clearEdgeCache();
    
    res.json({
      success: true,
      message: 'Cache cleared successfully'
    });
  } catch (error) {
    console.error('Error clearing cache:', error);
    res.status(500).json({
      success: false,
      error: 'Failed to clear cache'
    });
  }
});

// Get edge analytics
router.get('/analytics', async (req, res) => {
  try {
    const edgeComputing = req.app.locals.edgeComputing;
    const analytics = edgeComputing.getEdgeAnalytics();
    
    res.json({
      success: true,
      data: analytics
    });
  } catch (error) {
    console.error('Error getting edge analytics:', error);
    res.status(500).json({
      success: false,
      error: 'Failed to get edge analytics'
    });
  }
});

// Get edge metrics
router.get('/metrics', async (req, res) => {
  try {
    const edgeComputing = req.app.locals.edgeComputing;
    const state = edgeComputing.getEdgeState();
    
    res.json({
      success: true,
      data: {
        metrics: state.metrics,
        nodes: state.nodes.length,
        tasks: state.tasks.length,
        queue: state.queue.length,
        cacheSize: state.cacheSize
      }
    });
  } catch (error) {
    console.error('Error getting edge metrics:', error);
    res.status(500).json({
      success: false,
      error: 'Failed to get edge metrics'
    });
  }
});

// Get edge performance trends
router.get('/trends', async (req, res) => {
  try {
    const { period = '1h' } = req.query;
    
    // Mock edge performance trends data
    const trends = [
      {
        timestamp: new Date(Date.now() - 300000).toISOString(),
        latency: 15,
        throughput: 1000,
        cpuUsage: 75,
        memoryUsage: 60,
        tasksCompleted: 150
      },
      {
        timestamp: new Date(Date.now() - 600000).toISOString(),
        latency: 18,
        throughput: 950,
        cpuUsage: 80,
        memoryUsage: 65,
        tasksCompleted: 140
      },
      {
        timestamp: new Date(Date.now() - 900000).toISOString(),
        latency: 20,
        throughput: 900,
        cpuUsage: 85,
        memoryUsage: 70,
        tasksCompleted: 130
      }
    ];
    
    res.json({
      success: true,
      data: trends
    });
  } catch (error) {
    console.error('Error getting edge trends:', error);
    res.status(500).json({
      success: false,
      error: 'Failed to get edge trends'
    });
  }
});

module.exports = router;

