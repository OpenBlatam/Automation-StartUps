const express = require('express');
const router = express.Router();

/**
 * Metaverse Marketing API Routes
 * Handles all metaverse and virtual reality operations
 */

// Get metaverse state
router.get('/state', async (req, res) => {
  try {
    const metaverseMarketing = req.app.locals.metaverseMarketing;
    const state = metaverseMarketing.getMetaverseState();
    
    res.json({
      success: true,
      data: state
    });
  } catch (error) {
    console.error('Error getting metaverse state:', error);
    res.status(500).json({
      success: false,
      error: 'Failed to get metaverse state'
    });
  }
});

// Get all worlds
router.get('/worlds', async (req, res) => {
  try {
    const metaverseMarketing = req.app.locals.metaverseMarketing;
    const worlds = metaverseMarketing.getAllWorlds();
    
    res.json({
      success: true,
      data: worlds
    });
  } catch (error) {
    console.error('Error getting worlds:', error);
    res.status(500).json({
      success: false,
      error: 'Failed to get worlds'
    });
  }
});

// Get world by ID
router.get('/worlds/:id', async (req, res) => {
  try {
    const { id } = req.params;
    const metaverseMarketing = req.app.locals.metaverseMarketing;
    const world = metaverseMarketing.getWorld(parseInt(id));
    
    if (!world) {
      return res.status(404).json({
        success: false,
        error: 'World not found'
      });
    }
    
    res.json({
      success: true,
      data: world
    });
  } catch (error) {
    console.error('Error getting world:', error);
    res.status(500).json({
      success: false,
      error: 'Failed to get world'
    });
  }
});

// Join world
router.post('/worlds/:id/join', async (req, res) => {
  try {
    const { id } = req.params;
    const { user } = req.body;
    const metaverseMarketing = req.app.locals.metaverseMarketing;
    
    const result = metaverseMarketing.joinWorld(parseInt(id), user);
    
    res.json({
      success: true,
      data: result
    });
  } catch (error) {
    console.error('Error joining world:', error);
    res.status(500).json({
      success: false,
      error: error.message || 'Failed to join world'
    });
  }
});

// Leave world
router.post('/worlds/:id/leave', async (req, res) => {
  try {
    const { id } = req.params;
    const { user } = req.body;
    const metaverseMarketing = req.app.locals.metaverseMarketing;
    
    const result = metaverseMarketing.leaveWorld(parseInt(id), user);
    
    res.json({
      success: true,
      data: result
    });
  } catch (error) {
    console.error('Error leaving world:', error);
    res.status(500).json({
      success: false,
      error: error.message || 'Failed to leave world'
    });
  }
});

// Get available NFTs
router.get('/nfts', async (req, res) => {
  try {
    const metaverseMarketing = req.app.locals.metaverseMarketing;
    const nfts = metaverseMarketing.getAvailableNFTs();
    
    res.json({
      success: true,
      data: nfts
    });
  } catch (error) {
    console.error('Error getting NFTs:', error);
    res.status(500).json({
      success: false,
      error: 'Failed to get NFTs'
    });
  }
});

// Purchase NFT
router.post('/nfts/:id/purchase', async (req, res) => {
  try {
    const { id } = req.params;
    const { buyer } = req.body;
    const metaverseMarketing = req.app.locals.metaverseMarketing;
    
    const result = metaverseMarketing.purchaseNFT(id, buyer);
    
    res.json({
      success: true,
      data: result
    });
  } catch (error) {
    console.error('Error purchasing NFT:', error);
    res.status(500).json({
      success: false,
      error: error.message || 'Failed to purchase NFT'
    });
  }
});

// Get available virtual real estate
router.get('/real-estate', async (req, res) => {
  try {
    const metaverseMarketing = req.app.locals.metaverseMarketing;
    const properties = metaverseMarketing.getAvailableVirtualRealEstate();
    
    res.json({
      success: true,
      data: properties
    });
  } catch (error) {
    console.error('Error getting virtual real estate:', error);
    res.status(500).json({
      success: false,
      error: 'Failed to get virtual real estate'
    });
  }
});

// Purchase virtual real estate
router.post('/real-estate/:id/purchase', async (req, res) => {
  try {
    const { id } = req.params;
    const { buyer } = req.body;
    const metaverseMarketing = req.app.locals.metaverseMarketing;
    
    const result = metaverseMarketing.purchaseVirtualRealEstate(id, buyer);
    
    res.json({
      success: true,
      data: result
    });
  } catch (error) {
    console.error('Error purchasing virtual real estate:', error);
    res.status(500).json({
      success: false,
      error: error.message || 'Failed to purchase virtual real estate'
    });
  }
});

// Get active holographic ads
router.get('/ads', async (req, res) => {
  try {
    const metaverseMarketing = req.app.locals.metaverseMarketing;
    const ads = metaverseMarketing.getActiveHolographicAds();
    
    res.json({
      success: true,
      data: ads
    });
  } catch (error) {
    console.error('Error getting holographic ads:', error);
    res.status(500).json({
      success: false,
      error: 'Failed to get holographic ads'
    });
  }
});

// Get upcoming virtual events
router.get('/events', async (req, res) => {
  try {
    const metaverseMarketing = req.app.locals.metaverseMarketing;
    const events = metaverseMarketing.getUpcomingVirtualEvents();
    
    res.json({
      success: true,
      data: events
    });
  } catch (error) {
    console.error('Error getting virtual events:', error);
    res.status(500).json({
      success: false,
      error: 'Failed to get virtual events'
    });
  }
});

// Create virtual event
router.post('/events', async (req, res) => {
  try {
    const eventData = req.body;
    const metaverseMarketing = req.app.locals.metaverseMarketing;
    
    const event = metaverseMarketing.createVirtualEvent(eventData);
    
    res.json({
      success: true,
      data: event
    });
  } catch (error) {
    console.error('Error creating virtual event:', error);
    res.status(500).json({
      success: false,
      error: 'Failed to create virtual event'
    });
  }
});

// Get metaverse analytics
router.get('/analytics', async (req, res) => {
  try {
    const metaverseMarketing = req.app.locals.metaverseMarketing;
    const analytics = metaverseMarketing.getMetaverseAnalytics();
    
    res.json({
      success: true,
      data: analytics
    });
  } catch (error) {
    console.error('Error getting metaverse analytics:', error);
    res.status(500).json({
      success: false,
      error: 'Failed to get metaverse analytics'
    });
  }
});

// Get metaverse metrics
router.get('/metrics', async (req, res) => {
  try {
    const metaverseMarketing = req.app.locals.metaverseMarketing;
    const state = metaverseMarketing.getMetaverseState();
    
    res.json({
      success: true,
      data: {
        metrics: state.metrics,
        worlds: state.worlds.length,
        totalAssets: Object.values(state.assets).reduce((sum, arr) => sum + arr.length, 0)
      }
    });
  } catch (error) {
    console.error('Error getting metaverse metrics:', error);
    res.status(500).json({
      success: false,
      error: 'Failed to get metaverse metrics'
    });
  }
});

// Get metaverse trends
router.get('/trends', async (req, res) => {
  try {
    const { period = '24h' } = req.query;
    
    // Mock metaverse trends data
    const trends = [
      {
        timestamp: new Date(Date.now() - 3600000).toISOString(),
        users: 1250,
        transactions: 45,
        nftVolume: 12500,
        events: 3
      },
      {
        timestamp: new Date(Date.now() - 7200000).toISOString(),
        users: 1180,
        transactions: 38,
        nftVolume: 11200,
        events: 2
      },
      {
        timestamp: new Date(Date.now() - 10800000).toISOString(),
        users: 1100,
        transactions: 42,
        nftVolume: 10800,
        events: 4
      }
    ];
    
    res.json({
      success: true,
      data: trends
    });
  } catch (error) {
    console.error('Error getting metaverse trends:', error);
    res.status(500).json({
      success: false,
      error: 'Failed to get metaverse trends'
    });
  }
});

module.exports = router;

