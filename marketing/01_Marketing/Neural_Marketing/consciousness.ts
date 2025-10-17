import { Router } from 'express';
import { z } from 'zod';
import { ConsciousnessService } from '../services/consciousnessService';
import { authMiddleware } from '../middleware/auth';
import { logger } from '../utils/logger';

const router = Router();

// Validation schemas
const consciousnessContentSchema = z.object({
  contentType: z.string().min(1, 'Content type is required'),
  prompt: z.string().min(1, 'Prompt is required'),
});

// Assess consciousness level
router.post('/assess', authMiddleware, async (req, res) => {
  try {
    const userId = req.user?.id;
    if (!userId) {
      return res.status(401).json({ error: 'Unauthorized' });
    }

    const assessment = await ConsciousnessService.assessConsciousnessLevel(userId);
    
    logger.info(`Consciousness assessment completed for user ${userId}: Level ${assessment.level}`);

    res.json({
      success: true,
      assessment,
      message: `Your Neural Marketing Consciousness level is ${assessment.level} (${assessment.category})`,
    });
  } catch (error) {
    logger.error('Error assessing consciousness level:', error);
    res.status(500).json({ error: 'Failed to assess consciousness level' });
  }
});

// Generate neural marketing profile
router.post('/profile', authMiddleware, async (req, res) => {
  try {
    const userId = req.user?.id;
    if (!userId) {
      return res.status(401).json({ error: 'Unauthorized' });
    }

    const profile = await ConsciousnessService.generateNeuralMarketingProfile(userId);
    
    logger.info(`Neural marketing profile generated for user ${userId}`);

    res.json({
      success: true,
      profile,
      message: 'Neural marketing profile generated successfully',
    });
  } catch (error) {
    logger.error('Error generating neural marketing profile:', error);
    res.status(500).json({ error: 'Failed to generate neural marketing profile' });
  }
});

// Generate consciousness-based content
router.post('/generate-content', authMiddleware, async (req, res) => {
  try {
    const userId = req.user?.id;
    if (!userId) {
      return res.status(401).json({ error: 'Unauthorized' });
    }

    const validatedData = consciousnessContentSchema.parse(req.body);
    const { contentType, prompt } = validatedData;

    const content = await ConsciousnessService.generateConsciousnessBasedContent(
      userId,
      contentType,
      prompt
    );
    
    logger.info(`Consciousness-based content generated for user ${userId}`);

    res.json({
      success: true,
      content,
      contentType,
      message: 'Consciousness-based content generated successfully',
    });
  } catch (error) {
    logger.error('Error generating consciousness-based content:', error);
    if (error instanceof z.ZodError) {
      return res.status(400).json({ error: 'Validation error', details: error.errors });
    }
    res.status(500).json({ error: 'Failed to generate consciousness-based content' });
  }
});

// Get consciousness insights
router.get('/insights', authMiddleware, async (req, res) => {
  try {
    const userId = req.user?.id;
    if (!userId) {
      return res.status(401).json({ error: 'Unauthorized' });
    }

    const insights = await ConsciousnessService.getConsciousnessInsights(userId);
    
    res.json({
      success: true,
      insights,
    });
  } catch (error) {
    logger.error('Error getting consciousness insights:', error);
    res.status(500).json({ error: 'Failed to get consciousness insights' });
  }
});

// Get consciousness level
router.get('/level', authMiddleware, async (req, res) => {
  try {
    const userId = req.user?.id;
    if (!userId) {
      return res.status(401).json({ error: 'Unauthorized' });
    }

    const insights = await ConsciousnessService.getConsciousnessInsights(userId);
    
    res.json({
      success: true,
      level: insights.currentLevel,
      category: insights.category,
      levelLabel: insights.levelLabel,
      progress: insights.progress,
    });
  } catch (error) {
    logger.error('Error getting consciousness level:', error);
    res.status(500).json({ error: 'Failed to get consciousness level' });
  }
});

// Get consciousness recommendations
router.get('/recommendations', authMiddleware, async (req, res) => {
  try {
    const userId = req.user?.id;
    if (!userId) {
      return res.status(401).json({ error: 'Unauthorized' });
    }

    const insights = await ConsciousnessService.getConsciousnessInsights(userId);
    
    res.json({
      success: true,
      recommendations: insights.recommendations,
      nextSteps: insights.nextSteps,
      insights: insights.insights,
    });
  } catch (error) {
    logger.error('Error getting consciousness recommendations:', error);
    res.status(500).json({ error: 'Failed to get consciousness recommendations' });
  }
});

// Get consciousness progress
router.get('/progress', authMiddleware, async (req, res) => {
  try {
    const userId = req.user?.id;
    if (!userId) {
      return res.status(401).json({ error: 'Unauthorized' });
    }

    const insights = await ConsciousnessService.getConsciousnessInsights(userId);
    
    res.json({
      success: true,
      progress: insights.progress,
      currentLevel: insights.currentLevel,
      levelLabel: insights.levelLabel,
    });
  } catch (error) {
    logger.error('Error getting consciousness progress:', error);
    res.status(500).json({ error: 'Failed to get consciousness progress' });
  }
});

export { router as consciousnessRoutes };

