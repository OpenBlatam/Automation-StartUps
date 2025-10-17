import { Router } from 'express';
import { z } from 'zod';
import { ContentService } from '../services/contentService';
import { authMiddleware } from '../middleware/auth';
import { prisma } from '../index';
import { logger } from '../utils/logger';

const router = Router();

// Validation schemas
const generateContentSchema = z.object({
  type: z.enum([
    'BLOG_POST',
    'EMAIL',
    'SOCIAL_MEDIA',
    'AD_COPY',
    'PRODUCT_DESCRIPTION',
    'LANDING_PAGE',
    'SALES_PAGE',
    'EMAIL_SEQUENCE',
    'WEBSITE_COPY',
    'OTHER'
  ]),
  prompt: z.string().min(1).max(2000),
  tone: z.string().optional(),
  length: z.enum(['short', 'medium', 'long']).optional(),
  targetAudience: z.string().optional(),
  brandVoice: z.string().optional(),
  keywords: z.array(z.string()).optional(),
});

const improveContentSchema = z.object({
  content: z.string().min(1),
  improvements: z.array(z.string()).min(1),
});

// Generate content
router.post('/generate', authMiddleware, async (req, res) => {
  try {
    const userId = req.user?.id;
    if (!userId) {
      return res.status(401).json({ error: 'Unauthorized' });
    }

    const validatedData = generateContentSchema.parse(req.body);
    
    const result = await ContentService.generateContent({
      ...validatedData,
      type: validatedData.type as any,
    });

    // Save generation to database
    const contentGeneration = await prisma.contentGeneration.create({
      data: {
        userId,
        type: validatedData.type as any,
        prompt: validatedData.prompt,
        result: result.content,
        tokensUsed: result.tokensUsed,
        cost: result.cost,
      },
    });

    logger.info(`Content generated for user ${userId}. Generation ID: ${contentGeneration.id}`);

    res.json({
      id: contentGeneration.id,
      content: result.content,
      tokensUsed: result.tokensUsed,
      cost: result.cost,
      createdAt: contentGeneration.createdAt,
    });
  } catch (error) {
    logger.error('Error generating content:', error);
    if (error instanceof z.ZodError) {
      return res.status(400).json({ error: 'Invalid input', details: error.errors });
    }
    res.status(500).json({ error: 'Failed to generate content' });
  }
});

// Generate multiple variations
router.post('/generate-variations', authMiddleware, async (req, res) => {
  try {
    const userId = req.user?.id;
    if (!userId) {
      return res.status(401).json({ error: 'Unauthorized' });
    }

    const { count = 3, ...contentData } = generateContentSchema.parse(req.body);
    
    const variations = await ContentService.generateMultipleVariations({
      ...contentData,
      type: contentData.type as any,
    }, count);

    // Save all variations to database
    const savedGenerations = await Promise.all(
      variations.map(variation =>
        prisma.contentGeneration.create({
          data: {
            userId,
            type: contentData.type as any,
            prompt: contentData.prompt,
            result: variation.content,
            tokensUsed: variation.tokensUsed,
            cost: variation.cost,
          },
        })
      )
    );

    res.json({
      variations: savedGenerations.map((gen, index) => ({
        id: gen.id,
        content: gen.result,
        tokensUsed: gen.tokensUsed,
        cost: gen.cost,
        variation: index + 1,
      })),
      totalTokensUsed: variations.reduce((sum, v) => sum + v.tokensUsed, 0),
      totalCost: variations.reduce((sum, v) => sum + v.cost, 0),
    });
  } catch (error) {
    logger.error('Error generating variations:', error);
    if (error instanceof z.ZodError) {
      return res.status(400).json({ error: 'Invalid input', details: error.errors });
    }
    res.status(500).json({ error: 'Failed to generate variations' });
  }
});

// Improve existing content
router.post('/improve', authMiddleware, async (req, res) => {
  try {
    const userId = req.user?.id;
    if (!userId) {
      return res.status(401).json({ error: 'Unauthorized' });
    }

    const { content, improvements } = improveContentSchema.parse(req.body);
    
    const result = await ContentService.improveContent(content, improvements);

    // Save improvement to database
    const contentGeneration = await prisma.contentGeneration.create({
      data: {
        userId,
        type: 'OTHER',
        prompt: `Improve content: ${improvements.join(', ')}`,
        result: result.content,
        tokensUsed: result.tokensUsed,
        cost: result.cost,
      },
    });

    res.json({
      id: contentGeneration.id,
      content: result.content,
      tokensUsed: result.tokensUsed,
      cost: result.cost,
      createdAt: contentGeneration.createdAt,
    });
  } catch (error) {
    logger.error('Error improving content:', error);
    if (error instanceof z.ZodError) {
      return res.status(400).json({ error: 'Invalid input', details: error.errors });
    }
    res.status(500).json({ error: 'Failed to improve content' });
  }
});

// Get user's content generations
router.get('/history', authMiddleware, async (req, res) => {
  try {
    const userId = req.user?.id;
    if (!userId) {
      return res.status(401).json({ error: 'Unauthorized' });
    }

    const page = parseInt(req.query.page as string) || 1;
    const limit = parseInt(req.query.limit as string) || 20;
    const skip = (page - 1) * limit;

    const [generations, total] = await Promise.all([
      prisma.contentGeneration.findMany({
        where: { userId },
        orderBy: { createdAt: 'desc' },
        skip,
        take: limit,
        select: {
          id: true,
          type: true,
          prompt: true,
          result: true,
          tokensUsed: true,
          cost: true,
          createdAt: true,
        },
      }),
      prisma.contentGeneration.count({
        where: { userId },
      }),
    ]);

    res.json({
      generations,
      pagination: {
        page,
        limit,
        total,
        pages: Math.ceil(total / limit),
      },
    });
  } catch (error) {
    logger.error('Error fetching content history:', error);
    res.status(500).json({ error: 'Failed to fetch content history' });
  }
});

// Get specific content generation
router.get('/:id', authMiddleware, async (req, res) => {
  try {
    const userId = req.user?.id;
    if (!userId) {
      return res.status(401).json({ error: 'Unauthorized' });
    }

    const { id } = req.params;

    const generation = await prisma.contentGeneration.findFirst({
      where: {
        id,
        userId,
      },
    });

    if (!generation) {
      return res.status(404).json({ error: 'Content generation not found' });
    }

    res.json(generation);
  } catch (error) {
    logger.error('Error fetching content generation:', error);
    res.status(500).json({ error: 'Failed to fetch content generation' });
  }
});

// Delete content generation
router.delete('/:id', authMiddleware, async (req, res) => {
  try {
    const userId = req.user?.id;
    if (!userId) {
      return res.status(401).json({ error: 'Unauthorized' });
    }

    const { id } = req.params;

    const generation = await prisma.contentGeneration.findFirst({
      where: {
        id,
        userId,
      },
    });

    if (!generation) {
      return res.status(404).json({ error: 'Content generation not found' });
    }

    await prisma.contentGeneration.delete({
      where: { id },
    });

    res.json({ message: 'Content generation deleted successfully' });
  } catch (error) {
    logger.error('Error deleting content generation:', error);
    res.status(500).json({ error: 'Failed to delete content generation' });
  }
});

export { router as contentRoutes };

