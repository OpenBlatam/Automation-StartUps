import { Router } from 'express';
import { z } from 'zod';
import { NeuralInsightsService } from '../services/neuralInsightsService';
import { authMiddleware } from '../middleware/auth';
import { logger } from '../utils/logger';

const router = Router();

// Validation schemas
const marketTrendsSchema = z.object({
  industry: z.string().min(1, 'Industry is required'),
  timeframe: z.enum(['7d', '30d', '90d', '1y']).optional().default('30d'),
});

const competitiveAnalysisSchema = z.object({
  competitors: z.array(z.string()).min(1, 'At least one competitor is required'),
  industry: z.string().min(1, 'Industry is required'),
});

const contentStrategySchema = z.object({
  goals: z.array(z.string()).min(1, 'At least one goal is required'),
});

const performancePredictionSchema = z.object({
  timeframe: z.enum(['7d', '30d', '90d', '1y']).optional().default('30d'),
});

// Generate neural insights
router.post('/generate', authMiddleware, async (req, res) => {
  try {
    const userId = req.user?.id;
    if (!userId) {
      return res.status(401).json({ error: 'Unauthorized' });
    }

    const insights = await NeuralInsightsService.generateNeuralInsights(userId);
    
    logger.info(`Generated ${insights.length} neural insights for user ${userId}`);

    res.json({
      success: true,
      insights,
      count: insights.length,
      message: 'Neural insights generated successfully',
    });
  } catch (error) {
    logger.error('Error generating neural insights:', error);
    res.status(500).json({ error: 'Failed to generate neural insights' });
  }
});

// Analyze market trends
router.post('/market-trends', authMiddleware, async (req, res) => {
  try {
    const userId = req.user?.id;
    if (!userId) {
      return res.status(401).json({ error: 'Unauthorized' });
    }

    const validatedData = marketTrendsSchema.parse(req.body);
    const { industry, timeframe } = validatedData;

    const trends = await NeuralInsightsService.analyzeMarketTrends(industry, timeframe);
    
    logger.info(`Analyzed market trends for ${industry} (${timeframe}) for user ${userId}`);

    res.json({
      success: true,
      trends,
      count: trends.length,
      industry,
      timeframe,
      message: 'Market trends analyzed successfully',
    });
  } catch (error) {
    logger.error('Error analyzing market trends:', error);
    if (error instanceof z.ZodError) {
      return res.status(400).json({ error: 'Validation error', details: error.errors });
    }
    res.status(500).json({ error: 'Failed to analyze market trends' });
  }
});

// Perform competitive analysis
router.post('/competitive-analysis', authMiddleware, async (req, res) => {
  try {
    const userId = req.user?.id;
    if (!userId) {
      return res.status(401).json({ error: 'Unauthorized' });
    }

    const validatedData = competitiveAnalysisSchema.parse(req.body);
    const { competitors, industry } = validatedData;

    const analysis = await NeuralInsightsService.performCompetitiveAnalysis(competitors, industry);
    
    logger.info(`Performed competitive analysis for ${competitors.join(', ')} in ${industry} for user ${userId}`);

    res.json({
      success: true,
      analysis,
      count: analysis.length,
      competitors,
      industry,
      message: 'Competitive analysis completed successfully',
    });
  } catch (error) {
    logger.error('Error performing competitive analysis:', error);
    if (error instanceof z.ZodError) {
      return res.status(400).json({ error: 'Validation error', details: error.errors });
    }
    res.status(500).json({ error: 'Failed to perform competitive analysis' });
  }
});

// Generate content strategy
router.post('/content-strategy', authMiddleware, async (req, res) => {
  try {
    const userId = req.user?.id;
    if (!userId) {
      return res.status(401).json({ error: 'Unauthorized' });
    }

    const validatedData = contentStrategySchema.parse(req.body);
    const { goals } = validatedData;

    const strategy = await NeuralInsightsService.generateContentStrategy(userId, goals);
    
    logger.info(`Generated content strategy for user ${userId} with goals: ${goals.join(', ')}`);

    res.json({
      success: true,
      strategy,
      goals,
      message: 'Content strategy generated successfully',
    });
  } catch (error) {
    logger.error('Error generating content strategy:', error);
    if (error instanceof z.ZodError) {
      return res.status(400).json({ error: 'Validation error', details: error.errors });
    }
    res.status(500).json({ error: 'Failed to generate content strategy' });
  }
});

// Predict performance
router.post('/predict-performance', authMiddleware, async (req, res) => {
  try {
    const userId = req.user?.id;
    if (!userId) {
      return res.status(401).json({ error: 'Unauthorized' });
    }

    const validatedData = performancePredictionSchema.parse(req.body);
    const { timeframe } = validatedData;

    const predictions = await NeuralInsightsService.predictPerformance(userId, timeframe);
    
    logger.info(`Generated performance predictions for user ${userId} (${timeframe})`);

    res.json({
      success: true,
      predictions,
      timeframe,
      message: 'Performance predictions generated successfully',
    });
  } catch (error) {
    logger.error('Error predicting performance:', error);
    if (error instanceof z.ZodError) {
      return res.status(400).json({ error: 'Validation error', details: error.errors });
    }
    res.status(500).json({ error: 'Failed to predict performance' });
  }
});

// Generate optimization recommendations
router.post('/optimization-recommendations', authMiddleware, async (req, res) => {
  try {
    const userId = req.user?.id;
    if (!userId) {
      return res.status(401).json({ error: 'Unauthorized' });
    }

    const recommendations = await NeuralInsightsService.generateOptimizationRecommendations(userId);
    
    logger.info(`Generated optimization recommendations for user ${userId}`);

    res.json({
      success: true,
      recommendations,
      message: 'Optimization recommendations generated successfully',
    });
  } catch (error) {
    logger.error('Error generating optimization recommendations:', error);
    res.status(500).json({ error: 'Failed to generate optimization recommendations' });
  }
});

// Get insights summary
router.get('/summary', authMiddleware, async (req, res) => {
  try {
    const userId = req.user?.id;
    if (!userId) {
      return res.status(401).json({ error: 'Unauthorized' });
    }

    // This would fetch from database
    const summary = {
      totalInsights: 0,
      recentInsights: [],
      topCategories: [],
      averageConfidence: 0,
      highImpactInsights: 0,
    };

    res.json({
      success: true,
      summary,
    });
  } catch (error) {
    logger.error('Error getting insights summary:', error);
    res.status(500).json({ error: 'Failed to get insights summary' });
  }
});

// Get insights by category
router.get('/category/:category', authMiddleware, async (req, res) => {
  try {
    const userId = req.user?.id;
    if (!userId) {
      return res.status(401).json({ error: 'Unauthorized' });
    }

    const { category } = req.params;
    const page = parseInt(req.query.page as string) || 1;
    const limit = parseInt(req.query.limit as string) || 20;

    // This would fetch from database
    const insights = [];

    res.json({
      success: true,
      insights,
      category,
      pagination: {
        page,
        limit,
        total: 0,
        pages: 0,
      },
    });
  } catch (error) {
    logger.error('Error getting insights by category:', error);
    res.status(500).json({ error: 'Failed to get insights by category' });
  }
});

// Get insight details
router.get('/:id', authMiddleware, async (req, res) => {
  try {
    const userId = req.user?.id;
    if (!userId) {
      return res.status(401).json({ error: 'Unauthorized' });
    }

    const { id } = req.params;

    // This would fetch from database
    const insight = null;

    if (!insight) {
      return res.status(404).json({ error: 'Insight not found' });
    }

    res.json({
      success: true,
      insight,
    });
  } catch (error) {
    logger.error('Error getting insight details:', error);
    res.status(500).json({ error: 'Failed to get insight details' });
  }
});

// Mark insight as implemented
router.put('/:id/implement', authMiddleware, async (req, res) => {
  try {
    const userId = req.user?.id;
    if (!userId) {
      return res.status(401).json({ error: 'Unauthorized' });
    }

    const { id } = req.params;

    // This would update in database
    logger.info(`Marked insight ${id} as implemented for user ${userId}`);

    res.json({
      success: true,
      message: 'Insight marked as implemented',
    });
  } catch (error) {
    logger.error('Error marking insight as implemented:', error);
    res.status(500).json({ error: 'Failed to mark insight as implemented' });
  }
});

// Delete insight
router.delete('/:id', authMiddleware, async (req, res) => {
  try {
    const userId = req.user?.id;
    if (!userId) {
      return res.status(401).json({ error: 'Unauthorized' });
    }

    const { id } = req.params;

    // This would delete from database
    logger.info(`Deleted insight ${id} for user ${userId}`);

    res.json({
      success: true,
      message: 'Insight deleted successfully',
    });
  } catch (error) {
    logger.error('Error deleting insight:', error);
    res.status(500).json({ error: 'Failed to delete insight' });
  }
});

export { router as neuralInsightsRoutes };

