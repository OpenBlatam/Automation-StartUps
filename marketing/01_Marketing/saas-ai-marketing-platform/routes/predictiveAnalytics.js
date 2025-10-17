const express = require('express');
const router = express.Router();
const AIPredictiveAnalyticsService = require('../services/aiPredictiveAnalyticsService');
const auth = require('../middleware/auth');

const predictiveAnalyticsService = new AIPredictiveAnalyticsService();

// Predicción de tendencias de mercado
router.post('/market-trends', auth, async (req, res) => {
  try {
    const { industry, timeframe } = req.body;
    
    if (!industry) {
      return res.status(400).json({ error: 'Industry is required' });
    }

    const predictions = await predictiveAnalyticsService.predictMarketTrends(industry, timeframe);
    
    res.json({
      success: true,
      data: predictions
    });
  } catch (error) {
    console.error('Error predicting market trends:', error);
    res.status(500).json({ error: 'Failed to predict market trends' });
  }
});

// Predicción de rendimiento de contenido
router.post('/content-performance', auth, async (req, res) => {
  try {
    const { content, targetAudience, platform } = req.body;
    
    if (!content || !targetAudience || !platform) {
      return res.status(400).json({ error: 'Content, targetAudience, and platform are required' });
    }

    const predictions = await predictiveAnalyticsService.predictContentPerformance(content, targetAudience, platform);
    
    res.json({
      success: true,
      data: predictions
    });
  } catch (error) {
    console.error('Error predicting content performance:', error);
    res.status(500).json({ error: 'Failed to predict content performance' });
  }
});

// Predicción de comportamiento del usuario
router.post('/user-behavior', auth, async (req, res) => {
  try {
    const { userId, userData, context } = req.body;
    
    if (!userId || !userData) {
      return res.status(400).json({ error: 'UserId and userData are required' });
    }

    const predictions = await predictiveAnalyticsService.predictUserBehavior(userId, userData, context);
    
    res.json({
      success: true,
      data: predictions
    });
  } catch (error) {
    console.error('Error predicting user behavior:', error);
    res.status(500).json({ error: 'Failed to predict user behavior' });
  }
});

// Predicción de ROI de campañas
router.post('/campaign-roi', auth, async (req, res) => {
  try {
    const { campaignData, budget, targetAudience } = req.body;
    
    if (!campaignData || !budget || !targetAudience) {
      return res.status(400).json({ error: 'CampaignData, budget, and targetAudience are required' });
    }

    const predictions = await predictiveAnalyticsService.predictCampaignROI(campaignData, budget, targetAudience);
    
    res.json({
      success: true,
      data: predictions
    });
  } catch (error) {
    console.error('Error predicting campaign ROI:', error);
    res.status(500).json({ error: 'Failed to predict campaign ROI' });
  }
});

// Predicción de tendencias de contenido
router.post('/content-trends', auth, async (req, res) => {
  try {
    const { platform, category, timeframe } = req.body;
    
    if (!platform || !category) {
      return res.status(400).json({ error: 'Platform and category are required' });
    }

    const predictions = await predictiveAnalyticsService.predictContentTrends(platform, category, timeframe);
    
    res.json({
      success: true,
      data: predictions
    });
  } catch (error) {
    console.error('Error predicting content trends:', error);
    res.status(500).json({ error: 'Failed to predict content trends' });
  }
});

// Predicción de competencia
router.post('/competitive-landscape', auth, async (req, res) => {
  try {
    const { industry, competitors } = req.body;
    
    if (!industry || !competitors) {
      return res.status(400).json({ error: 'Industry and competitors are required' });
    }

    const predictions = await predictiveAnalyticsService.predictCompetitiveLandscape(industry, competitors);
    
    res.json({
      success: true,
      data: predictions
    });
  } catch (error) {
    console.error('Error predicting competitive landscape:', error);
    res.status(500).json({ error: 'Failed to predict competitive landscape' });
  }
});

// Predicción de crisis y gestión de reputación
router.post('/crisis-risks', auth, async (req, res) => {
  try {
    const { brandData, industryContext } = req.body;
    
    if (!brandData) {
      return res.status(400).json({ error: 'BrandData is required' });
    }

    const predictions = await predictiveAnalyticsService.predictCrisisRisks(brandData, industryContext);
    
    res.json({
      success: true,
      data: predictions
    });
  } catch (error) {
    console.error('Error predicting crisis risks:', error);
    res.status(500).json({ error: 'Failed to predict crisis risks' });
  }
});

// Predicción de crecimiento de audiencia
router.post('/audience-growth', auth, async (req, res) => {
  try {
    const { currentAudience, growthStrategy, timeframe } = req.body;
    
    if (!currentAudience || !growthStrategy) {
      return res.status(400).json({ error: 'CurrentAudience and growthStrategy are required' });
    }

    const predictions = await predictiveAnalyticsService.predictAudienceGrowth(currentAudience, growthStrategy, timeframe);
    
    res.json({
      success: true,
      data: predictions
    });
  } catch (error) {
    console.error('Error predicting audience growth:', error);
    res.status(500).json({ error: 'Failed to predict audience growth' });
  }
});

// Obtener estadísticas del servicio
router.get('/stats', auth, async (req, res) => {
  try {
    const stats = predictiveAnalyticsService.getServiceStats();
    
    res.json({
      success: true,
      data: stats
    });
  } catch (error) {
    console.error('Error getting service stats:', error);
    res.status(500).json({ error: 'Failed to get service stats' });
  }
});

// Limpiar cache
router.post('/clear-cache', auth, async (req, res) => {
  try {
    predictiveAnalyticsService.clearCache();
    
    res.json({
      success: true,
      message: 'Cache cleared successfully'
    });
  } catch (error) {
    console.error('Error clearing cache:', error);
    res.status(500).json({ error: 'Failed to clear cache' });
  }
});

module.exports = router;

